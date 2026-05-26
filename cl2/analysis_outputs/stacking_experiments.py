from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402
import meta_feature_experiments as mf  # noqa: E402
import sensor_feature_variant_experiments as sfv  # noqa: E402


OUT = Path(__file__).resolve().parent
TARGETS = d.TARGETS
STACK_TARGETS = ["Q2", "Q3", "S4"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1 - p))


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j in range(y.shape[1])]))


def per_target_loss(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {target: log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]) for j, target in enumerate(TARGETS)}


def fixed_blend(base: np.ndarray, phone: np.ndarray, mobility: np.ndarray) -> np.ndarray:
    pred = base.copy()
    for target, source, weight in [("Q2", "phone", 0.10), ("Q3", "mobility", 0.20), ("S4", "mobility", 0.10)]:
        j = TARGETS.index(target)
        sensor = phone if source == "phone" else mobility
        pred[:, j] = (1 - weight) * base[:, j] + weight * sensor[:, j]
    return clip(pred)


def predict_bundle(train_rows: pd.DataFrame, val_rows: pd.DataFrame) -> dict[str, np.ndarray]:
    base = cal.temporal_base(train_rows, val_rows)
    cur_phone = sfv.fit_sensor_predict_variant(train_rows, val_rows, "phone", "missing")
    cur_mob = sfv.fit_sensor_predict_variant(train_rows, val_rows, "mobility", "missing")
    meta_phone = mf.fit_predict(train_rows, val_rows, "meta_phone")
    meta_mob = mf.fit_predict(train_rows, val_rows, "meta_mobility")
    meta_all = mf.fit_predict(train_rows, val_rows, "meta_all")
    return {
        "base": base,
        "cur_phone": cur_phone,
        "cur_mobility": cur_mob,
        "meta_phone": meta_phone,
        "meta_mobility": meta_mob,
        "meta_all": meta_all,
        "current_fixed": fixed_blend(base, cur_phone, cur_mob),
        "meta_fixed": fixed_blend(base, meta_phone, meta_mob),
        "meta_all_fixed": fixed_blend(base, meta_all, meta_all),
    }


def oof_bundle(train: pd.DataFrame, folds: list[tuple[np.ndarray, np.ndarray]]) -> dict[str, np.ndarray]:
    y_shape = (len(train), len(TARGETS))
    out = {}
    for fold_id, (tr_idx, val_idx) in enumerate(folds):
        tr = train.iloc[tr_idx].copy().reset_index(drop=True)
        val = train.iloc[val_idx].copy().reset_index(drop=True)
        bundle = predict_bundle(tr, val)
        for name, pred in bundle.items():
            out.setdefault(name, np.zeros(y_shape, dtype=float))[val_idx] = pred
        print(f"[inner bundle] fold {fold_id}", flush=True)
    return out


def stack_features(bundle: dict[str, np.ndarray], target_idx: int, mode: str) -> np.ndarray:
    own_sources = ["base", "current_fixed", "meta_fixed", "meta_all_fixed", "cur_phone", "cur_mobility", "meta_phone", "meta_mobility", "meta_all"]
    blocks = [logit(bundle[name][:, [target_idx]]) for name in own_sources]
    if mode == "own":
        return np.hstack(blocks)
    if mode == "own_plus_base_all":
        return np.hstack(blocks + [logit(bundle["base"])])
    if mode == "own_plus_fixed_all":
        return np.hstack(blocks + [logit(bundle["current_fixed"]), logit(bundle["meta_fixed"]), logit(bundle["meta_all_fixed"])])
    raise ValueError(mode)


def fit_stackers(
    train_rows: pd.DataFrame,
    inner_bundle: dict[str, np.ndarray],
    mode: str,
    c_value: float,
) -> dict[str, Pipeline]:
    y = train_rows[TARGETS].to_numpy()
    stackers = {}
    for target in STACK_TARGETS:
        j = TARGETS.index(target)
        X = stack_features(inner_bundle, j, mode)
        pipe = Pipeline(
            [
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(C=c_value, solver="liblinear", max_iter=1000)),
            ]
        )
        pipe.fit(X, y[:, j])
        stackers[target] = pipe
    return stackers


def apply_stackers(base_pred: np.ndarray, outer_bundle: dict[str, np.ndarray], stackers: dict[str, Pipeline], mode: str) -> np.ndarray:
    pred = base_pred.copy()
    for target, pipe in stackers.items():
        j = TARGETS.index(target)
        X = stack_features(outer_bundle, j, mode)
        pred[:, j] = pipe.predict_proba(X)[:, 1]
    return clip(pred)


def inner_select(train_rows: pd.DataFrame, inner_bundle: dict[str, np.ndarray]) -> tuple[str, float, float]:
    y = train_rows[TARGETS].to_numpy()
    best = ("own", 0.05, np.inf)
    for mode in ["own", "own_plus_base_all", "own_plus_fixed_all"]:
        for c_value in [0.03, 0.05, 0.1, 0.2, 0.4]:
            stackers = fit_stackers(train_rows, inner_bundle, mode, c_value)
            pred = inner_bundle["current_fixed"].copy()
            pred = apply_stackers(pred, inner_bundle, stackers, mode)
            loss = mean_loss(y, pred)
            if loss < best[2]:
                best = (mode, c_value, loss)
    return best


def nested_stacking(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy()
    pred_base = np.zeros_like(y, dtype=float)
    pred_current = np.zeros_like(y, dtype=float)
    pred_stack = np.zeros_like(y, dtype=float)
    selected = []
    for outer_id, (tr_idx, val_idx) in enumerate(d.make_folds(train, "subject_blocks")):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_bundle = oof_bundle(outer_train, inner_folds)
        mode, c_value, inner_loss = inner_select(outer_train, inner_bundle)
        stackers = fit_stackers(outer_train, inner_bundle, mode, c_value)
        outer_bundle = predict_bundle(outer_train, outer_val)
        base_val = outer_bundle["base"]
        current_val = outer_bundle["current_fixed"]
        stack_val = apply_stackers(current_val, outer_bundle, stackers, mode)
        pred_base[val_idx] = base_val
        pred_current[val_idx] = current_val
        pred_stack[val_idx] = stack_val
        selected.append({"outer_fold": outer_id, "mode": mode, "C": c_value, "inner_loss": inner_loss})
        print(f"[nested stack] outer={outer_id} mode={mode} C={c_value} inner={inner_loss:.5f}", flush=True)

    rows = []
    for name, pred in [("temporal_base", pred_base), ("current_missing", pred_current), ("nested_stacker", pred_stack)]:
        row = {"model": name, "mean": mean_loss(y, pred)}
        row.update(per_target_loss(y, pred))
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean"), pd.DataFrame(selected)


def full_train_choice(train: pd.DataFrame) -> tuple[str, float, dict[str, Pipeline]]:
    folds = d.make_folds(train, "subject_blocks")
    bundle = oof_bundle(train, folds)
    mode, c_value, _ = inner_select(train, bundle)
    return mode, c_value, fit_stackers(train, bundle, mode, c_value)


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, mode: str, stackers: dict[str, Pipeline]) -> pd.DataFrame:
    bundle = predict_bundle(train, sub)
    pred = apply_stackers(bundle["current_fixed"], bundle, stackers, mode)
    out = sub[["subject_id", "sleep_date", "lifelog_date"]].copy()
    for j, target in enumerate(TARGETS):
        out[target] = pred[:, j]
    return out


def main() -> None:
    train, sub = mf.prepare(force_meta=False)
    results, selected = nested_stacking(train)
    results.to_csv(OUT / "stacking_nested_results.csv", index=False)
    selected.to_csv(OUT / "stacking_nested_selected.csv", index=False)
    mode, c_value, stackers = full_train_choice(train)
    submission = make_submission(train, sub, mode, stackers)
    submission.to_csv(OUT / "submission_stacked.csv", index=False)
    if float(results.iloc[0]["mean"]) < 0.6228411063084949 and str(results.iloc[0]["model"]) == "nested_stacker":
        submission.to_csv(OUT / "submission_best.csv", index=False)
    pd.DataFrame([{"mode": mode, "C": c_value}]).to_csv(OUT / "stacking_full_choice.csv", index=False)
    print("\nNested stacking")
    print(results.round(5).to_string(index=False))
    print("\nSelected")
    print(selected.to_string(index=False))
    print(f"\nFull train choice: mode={mode}, C={c_value}")


if __name__ == "__main__":
    main()
