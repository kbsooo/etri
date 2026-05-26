from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import q23_presleep_app_experiments as app  # noqa: E402
import sensor_feature_variant_experiments as sfv  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
Q2_IDX = TARGETS.index("Q2")
KEY = d.KEY

APP_CANDIDATE = next(c for c in app.CANDIDATES if c.name == "logreg_c0.03")
STACK_C_GRID = [0.03, 0.1, 0.3, 1.0, 3.0]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def q2_loss(y: pd.Series | np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(np.asarray(y), clip(pred), labels=[0, 1]))


def soft_rate_predict(ref: pd.DataFrame, rows: pd.DataFrame, target: str = "Q2", r: float = 0.45, shrink: float = 2.0) -> np.ndarray:
    global_rate = float(ref[target].mean())
    pred = np.zeros(len(rows), dtype=float)
    tmp = rows.reset_index(drop=True)
    for sid, g in tmp.groupby("subject_id", sort=False):
        known = ref[ref["subject_id"] == sid]
        n_known = len(known)
        n_hidden = len(g)
        known_pos = float(known[target].sum())
        raw = (r * (n_known + n_hidden) - known_pos + shrink * global_rate) / (n_hidden + shrink)
        pred[g.index.to_numpy()] = float(np.clip(raw, 0.03, 0.97))
    return clip(pred)


def q2_current_from_base_phone(base_q2: np.ndarray, phone_pred: np.ndarray) -> np.ndarray:
    return clip(0.90 * base_q2 + 0.10 * phone_pred[:, Q2_IDX])


def first_level_oof(rows: pd.DataFrame, store: app.AppFeatureStore) -> pd.DataFrame:
    folds = d.make_folds(rows, "subject_blocks")
    base_all = cal.base_oof(rows, folds)
    base_q2 = base_all[:, Q2_IDX]
    phone_q2 = np.zeros(len(rows), dtype=float)
    soft_q2 = np.zeros(len(rows), dtype=float)
    for tr_idx, val_idx in folds:
        tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = rows.iloc[val_idx].copy().reset_index(drop=True)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            phone = sfv.fit_sensor_predict_variant(tr, val, "phone", "missing")
        phone_q2[val_idx] = phone[:, Q2_IDX]
        soft_q2[val_idx] = soft_rate_predict(tr, val)
    current_q2 = q2_current_from_base_phone(base_q2, np.column_stack([phone_q2] * len(TARGETS)))
    app_q2 = app.candidate_oof(rows, folds, store, APP_CANDIDATE)[:, 0]
    combo_q2 = clip(0.60 * base_q2 + 0.20 * app_q2 + 0.20 * soft_q2)
    return pd.DataFrame(
        {
            "subject_id": rows["subject_id"].astype(str).to_numpy(),
            "dow": rows["lifelog_date"].dt.dayofweek.astype(str).to_numpy(),
            "base_q2": base_q2,
            "phone_q2": phone_q2,
            "current_q2": current_q2,
            "app_q2": app_q2,
            "soft_q2": soft_q2,
            "combo_q2": combo_q2,
        }
    )


def first_level_predict(train_rows: pd.DataFrame, val_rows: pd.DataFrame, store: app.AppFeatureStore) -> pd.DataFrame:
    base_all = cal.temporal_base(train_rows, val_rows)
    base_q2 = base_all[:, Q2_IDX]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        phone = sfv.fit_sensor_predict_variant(train_rows, val_rows, "phone", "missing")
    phone_q2 = phone[:, Q2_IDX]
    current_q2 = clip(0.90 * base_q2 + 0.10 * phone_q2)
    app_q2 = app.fit_candidate(train_rows, val_rows, store, "Q2", APP_CANDIDATE)
    soft_q2 = soft_rate_predict(train_rows, val_rows)
    combo_q2 = clip(0.60 * base_q2 + 0.20 * app_q2 + 0.20 * soft_q2)
    return pd.DataFrame(
        {
            "subject_id": val_rows["subject_id"].astype(str).to_numpy(),
            "dow": val_rows["lifelog_date"].dt.dayofweek.astype(str).to_numpy(),
            "base_q2": base_q2,
            "phone_q2": phone_q2,
            "current_q2": current_q2,
            "app_q2": app_q2,
            "soft_q2": soft_q2,
            "combo_q2": combo_q2,
        }
    )


def make_stack_pipeline(c_value: float, use_subject: bool) -> tuple[Pipeline, list[str]]:
    num_cols = ["current_q2", "combo_q2", "base_q2", "app_q2", "soft_q2"]
    cols = num_cols.copy()
    transformers = [
        (
            "num",
            Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]),
            [f"logit_{c}" for c in num_cols],
        )
    ]
    if use_subject:
        cols.extend(["subject_id", "dow"])
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), ["subject_id", "dow"]))
    pre = ColumnTransformer(transformers)
    clf = LogisticRegression(C=c_value, solver="liblinear", max_iter=1000)
    return Pipeline([("pre", pre), ("clf", clf)]), cols


def stack_frame(features: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()
    for col in ["current_q2", "combo_q2", "base_q2", "app_q2", "soft_q2"]:
        out[f"logit_{col}"] = logit(out[col].to_numpy(dtype=float))
    return out


def nested_stack(train: pd.DataFrame, store: app.AppFeatureStore) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    folds = d.make_folds(train, "subject_blocks")
    preds: dict[str, np.ndarray] = {}
    for c_value in STACK_C_GRID:
        for use_subject in [False, True]:
            preds[f"stack_C{c_value:g}_subj{int(use_subject)}"] = np.zeros(len(train), dtype=float)
    baselines = {name: np.zeros(len(train), dtype=float) for name in ["base_q2", "current_q2", "combo_q2", "soft_q2", "app_q2"]}
    selected_rows = []

    for outer_id, (tr_idx, val_idx) in enumerate(folds):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        train_feat = first_level_oof(outer_train, store)
        val_feat = first_level_predict(outer_train, outer_val, store)
        train_x = stack_frame(train_feat)
        val_x = stack_frame(val_feat)
        for name in baselines:
            baselines[name][val_idx] = val_feat[name].to_numpy(dtype=float)
        y_train = outer_train["Q2"].to_numpy(dtype=int)
        for c_value in STACK_C_GRID:
            for use_subject in [False, True]:
                key = f"stack_C{c_value:g}_subj{int(use_subject)}"
                pipe, cols = make_stack_pipeline(c_value, use_subject)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    pipe.fit(train_x, y_train)
                preds[key][val_idx] = pipe.predict_proba(val_x)[:, 1]
        selected_rows.append({"outer_fold": outer_id, "train_rows": len(outer_train), "val_rows": len(outer_val)})
        print(f"[q2 stack] outer {outer_id} done", flush=True)

    y = train["Q2"].to_numpy(dtype=int)
    rows = []
    for name, pred in {**baselines, **preds}.items():
        rows.append({"model": name, "Q2": q2_loss(y, pred)})
    return pd.DataFrame(rows).sort_values("Q2"), pd.DataFrame(selected_rows), {**baselines, **preds}


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, store: app.AppFeatureStore, model_name: str) -> pd.DataFrame:
    sub_feat = first_level_predict(train, sub, store)
    if model_name in {"base_q2", "current_q2", "combo_q2", "soft_q2", "app_q2"}:
        q2_pred = sub_feat[model_name].to_numpy(dtype=float)
    else:
        train_feat = first_level_oof(train, store)
        train_x = stack_frame(train_feat)
        sub_x = stack_frame(sub_feat)
        _, c_part, subj_part = model_name.split("_")
        c_value = float(c_part.replace("C", ""))
        use_subject = bool(int(subj_part.replace("subj", "")))
        pipe, cols = make_stack_pipeline(c_value, use_subject)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pipe.fit(train_x, train["Q2"].to_numpy(dtype=int))
        q2_pred = pipe.predict_proba(sub_x)[:, 1]

    if (OUT / "submission_hybrid_overnight_context.csv").exists():
        out = pd.read_csv(OUT / "submission_hybrid_overnight_context.csv", parse_dates=["sleep_date", "lifelog_date"])
        out = out.sort_values(KEY).reset_index(drop=True)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"] + TARGETS].copy()
    out["Q2"] = clip(q2_pred)
    return out


def main() -> None:
    train, sub = mf.prepare(force_meta=False)
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    all_keys = pd.concat([train[KEY], sub[KEY]], ignore_index=True)
    store = app.build_app_feature_store(all_keys)

    results, selected, _ = nested_stack(train, store)
    results.to_csv(OUT / "q2_soft_app_stack_nested_results.csv", index=False)
    selected.to_csv(OUT / "q2_soft_app_stack_nested_selected.csv", index=False)
    best_model = str(results.iloc[0]["model"])
    submission = make_submission(train, sub, store, best_model)
    submission.to_csv(OUT / "submission_q2_soft_app_stack.csv", index=False)

    old_q2 = 0.6927101523541841
    old_mean = 0.6049114285714285
    new_q2 = float(results.iloc[0]["Q2"])
    est_mean = old_mean - (old_q2 - new_q2) / 7.0
    pd.DataFrame(
        [
            {"target": "Q2", "old_loss": old_q2, "new_loss": new_q2},
            {"target": "mean", "old_loss": old_mean, "new_loss": est_mean},
        ]
    ).to_csv(OUT / "q2_soft_app_stack_hybrid_estimate.csv", index=False)

    print("\nNested Q2 soft/app stack")
    print(results.round(6).to_string(index=False))
    print("\nBest model", best_model)
    print(pd.read_csv(OUT / "q2_soft_app_stack_hybrid_estimate.csv").round(6).to_string(index=False))
    print("submission", OUT / "submission_q2_soft_app_stack.csv")


if __name__ == "__main__":
    main()
