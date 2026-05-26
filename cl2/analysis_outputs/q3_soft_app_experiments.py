from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import q23_presleep_app_experiments as app  # noqa: E402
import sensor_feature_variant_experiments as sfv  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
KEY = d.KEY
TARGET = "Q3"
TIDX = TARGETS.index(TARGET)

APP_NAMES = ["logreg_c0.03", "te_global_s2", "te_global_s6"]
APP_BY_NAME = {c.name: c for c in app.CANDIDATES if c.name in APP_NAMES}
R_GRID = [0.45, 0.50, 0.55, 0.60, 0.65]
SHRINK_GRID = [1.0, 2.0, 4.0, 8.0, 16.0]
APP_WEIGHT_GRID = [0.0, 0.05, 0.10, 0.15, 0.20]
SOFT_WEIGHT_GRID = [0.0, 0.05, 0.10, 0.15, 0.20]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def target_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(y, clip(pred), labels=[0, 1]))


def current_q3_from_base(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> np.ndarray:
    pred = base.copy()
    pred[:, TARGETS.index("Q2")] = 0.90 * base[:, TARGETS.index("Q2")] + 0.10 * phone[:, TARGETS.index("Q2")]
    pred[:, TARGETS.index("Q3")] = 0.80 * base[:, TARGETS.index("Q3")] + 0.20 * mobility[:, TARGETS.index("Q3")]
    pred[:, TARGETS.index("S4")] = 0.90 * base[:, TARGETS.index("S4")] + 0.10 * mobility[:, TARGETS.index("S4")]
    return clip(pred[:, TIDX])


def current_q3_predict(train_rows: pd.DataFrame, val_rows: pd.DataFrame) -> np.ndarray:
    base = cal.temporal_base(train_rows, val_rows)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        phone = sfv.fit_sensor_predict_variant(train_rows, val_rows, "phone", "missing")
        mobility = sfv.fit_sensor_predict_variant(train_rows, val_rows, "mobility", "missing")
    return current_q3_from_base(base, phone, mobility)


def current_q3_oof(rows: pd.DataFrame) -> np.ndarray:
    pred = np.zeros(len(rows), dtype=float)
    for tr_idx, val_idx in d.make_folds(rows, "subject_blocks"):
        tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = rows.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = current_q3_predict(tr, val)
    return clip(pred)


def app_target_oof(rows: pd.DataFrame, store: app.AppFeatureStore, cand: app.Candidate) -> np.ndarray:
    pred = np.zeros(len(rows), dtype=float)
    for tr_idx, val_idx in d.make_folds(rows, "subject_blocks"):
        tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = rows.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = app.fit_candidate(tr, val, store, TARGET, cand)
    return clip(pred)


def soft_rate_predict(
    ref: pd.DataFrame,
    rows: pd.DataFrame,
    r: float,
    shrink: float,
    target: str = TARGET,
) -> np.ndarray:
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


def soft_rate_oof(rows: pd.DataFrame, r: float, shrink: float) -> np.ndarray:
    pred = np.zeros(len(rows), dtype=float)
    for tr_idx, val_idx in d.make_folds(rows, "subject_blocks"):
        tr = rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = rows.iloc[val_idx].copy().reset_index(drop=True)
        pred[val_idx] = soft_rate_predict(tr, val, r, shrink)
    return clip(pred)


def blend(backbone: np.ndarray, app_pred: np.ndarray | None, soft_pred: np.ndarray | None, wa: float, ws: float) -> np.ndarray:
    out = (1.0 - wa - ws) * backbone
    if app_pred is not None and wa > 0:
        out = out + wa * app_pred
    if soft_pred is not None and ws > 0:
        out = out + ws * soft_pred
    return clip(out)


def choose_combo(y: np.ndarray, backbone: np.ndarray, app_preds: dict[str, np.ndarray], soft_preds: dict[tuple[float, float], np.ndarray]) -> dict[str, object]:
    best = {"loss": target_loss(y, backbone), "app": "none", "wa": 0.0, "r": 0.0, "shrink": 0.0, "ws": 0.0}
    for app_name in ["none", *APP_NAMES]:
        ap = None if app_name == "none" else app_preds[app_name]
        for soft_key in [None, *soft_preds.keys()]:
            sp = None if soft_key is None else soft_preds[soft_key]
            for wa in APP_WEIGHT_GRID:
                for ws in SOFT_WEIGHT_GRID:
                    if app_name == "none" and wa > 0:
                        continue
                    if soft_key is None and ws > 0:
                        continue
                    if wa + ws >= 0.80:
                        continue
                    pred = blend(backbone, ap, sp, wa, ws)
                    loss = target_loss(y, pred)
                    if loss < float(best["loss"]) - 1e-12:
                        if soft_key is None:
                            r, shrink = 0.0, 0.0
                        else:
                            r, shrink = soft_key
                        best = {"loss": loss, "app": app_name, "wa": wa, "r": r, "shrink": shrink, "ws": ws}
    return best


def predict_combo(train_rows: pd.DataFrame, val_rows: pd.DataFrame, store: app.AppFeatureStore, combo: dict[str, object]) -> np.ndarray:
    backbone = current_q3_predict(train_rows, val_rows)
    app_name = str(combo["app"])
    app_pred = None if app_name == "none" else app.fit_candidate(train_rows, val_rows, store, TARGET, APP_BY_NAME[app_name])
    r = float(combo["r"])
    shrink = float(combo["shrink"])
    soft_pred = None if float(combo["ws"]) <= 0 else soft_rate_predict(train_rows, val_rows, r, shrink)
    return blend(backbone, app_pred, soft_pred, float(combo["wa"]), float(combo["ws"]))


def nested_experiment(train: pd.DataFrame, store: app.AppFeatureStore) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    y = train[TARGET].to_numpy(dtype=int)
    current = np.zeros(len(train), dtype=float)
    nested = np.zeros(len(train), dtype=float)
    fixed = np.zeros(len(train), dtype=float)
    selected_rows = []
    fixed_combo = {"app": "logreg_c0.03", "wa": 0.10, "r": 0.50, "shrink": 1.0, "ws": 0.10}

    for outer_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_y = outer_train[TARGET].to_numpy(dtype=int)
        inner_current = current_q3_oof(outer_train)
        inner_app = {name: app_target_oof(outer_train, store, cand) for name, cand in APP_BY_NAME.items()}
        inner_soft = {(r, shrink): soft_rate_oof(outer_train, r, shrink) for r in R_GRID for shrink in SHRINK_GRID}
        combo = choose_combo(inner_y, inner_current, inner_app, inner_soft)

        current[val_idx] = current_q3_predict(outer_train, outer_val)
        nested[val_idx] = predict_combo(outer_train, outer_val, store, combo)
        fixed[val_idx] = predict_combo(outer_train, outer_val, store, fixed_combo)
        selected_rows.append({"outer_fold": outer_id, **combo, "train_rows": len(outer_train), "val_rows": len(outer_val)})
        print(f"[q3 soft/app] outer {outer_id} combo={combo}", flush=True)

    rows = []
    for name, pred in [("current_q3", current), ("nested_q3_soft_app", nested), ("fixed_q3_soft_app", fixed)]:
        rows.append({"model": name, TARGET: target_loss(y, pred)})
    return pd.DataFrame(rows).sort_values(TARGET), pd.DataFrame(selected_rows), {
        "current_q3": current,
        "nested_q3_soft_app": nested,
        "fixed_q3_soft_app": fixed,
    }


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, store: app.AppFeatureStore, model: str) -> pd.DataFrame:
    if (OUT / "submission_hybrid_0p599.csv").exists():
        out = pd.read_csv(OUT / "submission_hybrid_0p599.csv", parse_dates=["sleep_date", "lifelog_date"])
        out = out.sort_values(KEY).reset_index(drop=True)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"] + TARGETS].copy()
    if model == "current_q3":
        pred = current_q3_predict(train, sub)
    elif model == "fixed_q3_soft_app":
        combo = {"app": "logreg_c0.03", "wa": 0.10, "r": 0.50, "shrink": 1.0, "ws": 0.10}
        pred = predict_combo(train, sub, store, combo)
    else:
        train_y = train[TARGET].to_numpy(dtype=int)
        current = current_q3_oof(train)
        app_preds = {name: app_target_oof(train, store, cand) for name, cand in APP_BY_NAME.items()}
        soft_preds = {(r, shrink): soft_rate_oof(train, r, shrink) for r in R_GRID for shrink in SHRINK_GRID}
        combo = choose_combo(train_y, current, app_preds, soft_preds)
        pred = predict_combo(train, sub, store, combo)
    out[TARGET] = clip(pred)
    return out


def main() -> None:
    train, sub = mf.prepare(force_meta=False)
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    all_keys = pd.concat([train[KEY], sub[KEY]], ignore_index=True)
    store = app.build_app_feature_store(all_keys)

    results, selected, _ = nested_experiment(train, store)
    results.to_csv(OUT / "q3_soft_app_nested_results.csv", index=False)
    selected.to_csv(OUT / "q3_soft_app_nested_selected.csv", index=False)
    best_model = str(results.iloc[0]["model"])
    submission = make_submission(train, sub, store, best_model)
    submission.to_csv(OUT / "submission_q3_soft_app.csv", index=False)
    submission.to_csv(OUT / "submission_hybrid_0p598.csv", index=False)

    old_q3 = 0.6622200100969644
    old_mean = 0.5996807712266312
    new_q3 = float(results.iloc[0][TARGET])
    est_mean = old_mean - (old_q3 - new_q3) / 7.0
    delta_estimate = pd.DataFrame(
        [
            {"target": TARGET, "old_loss": old_q3, "new_loss": new_q3},
            {"target": "mean", "old_loss": old_mean, "new_loss": est_mean},
        ]
    )
    delta_estimate.to_csv(OUT / "q3_soft_app_hybrid_estimate.csv", index=False)

    current_0p599 = {
        "Q1": 0.625034,
        "Q2": 0.6635717635251487,
        "Q3": old_q3,
        "S1": 0.524188,
        "S2": 0.5597193509033811,
        "S3": 0.535248,
        "S4": 0.6277842740609245,
    }
    upgraded = current_0p599.copy()
    upgraded["Q3"] = new_q3
    full_rows = []
    for target in TARGETS:
        full_rows.append(
            {
                "target": target,
                "old_loss": current_0p599[target],
                "new_loss": upgraded[target],
                "delta": upgraded[target] - current_0p599[target],
            }
        )
    full_rows.append(
        {
            "target": "mean",
            "old_loss": float(np.mean([current_0p599[t] for t in TARGETS])),
            "new_loss": float(np.mean([upgraded[t] for t in TARGETS])),
            "delta": float(np.mean([upgraded[t] - current_0p599[t] for t in TARGETS])),
        }
    )
    pd.DataFrame(full_rows).to_csv(OUT / "hybrid_0p598_cv_estimate.csv", index=False)

    print("\nNested Q3 soft/app experiment")
    print(results.round(6).to_string(index=False))
    print("\nSelected")
    print(selected.round(6).to_string(index=False))
    print("\nHybrid estimate if Q3 replaced")
    print(pd.read_csv(OUT / "q3_soft_app_hybrid_estimate.csv").round(6).to_string(index=False))
    print("submission", OUT / "submission_q3_soft_app.csv")
    print("hybrid_submission", OUT / "submission_hybrid_0p598.csv")


if __name__ == "__main__":
    main()
