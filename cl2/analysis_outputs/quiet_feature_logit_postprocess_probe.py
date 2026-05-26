from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45])


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def make_subject_blocks(train: pd.DataFrame, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    idx = np.arange(len(train))
    folds = [[] for _ in range(n_splits)]
    for _, g in train.sort_values(KEY).groupby("subject_id", sort=False):
        locs = g.index.to_numpy()
        for fold, part in enumerate(np.array_split(locs, n_splits)):
            folds[fold].extend(part.tolist())
    out = []
    for val_ids in folds:
        val = np.array(sorted(val_ids))
        tr = np.setdiff1d(idx, val)
        out.append((tr, val))
    return out


def add_ref_z(rows: pd.DataFrame, ref: pd.DataFrame, feature: str) -> np.ndarray:
    out = np.full(len(rows), np.nan, dtype=float)
    row_sids = rows["subject_id"].astype(str).to_numpy()
    for sid, ref_g in ref.groupby("subject_id", sort=False):
        idx = np.where(row_sids == str(sid))[0]
        if idx.size == 0:
            continue
        vals = ref_g[feature].to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1)) if vals.size > 1 else np.nan
        raw = rows.iloc[idx][feature].to_numpy(dtype=float)
        if np.isfinite(std) and std > 0:
            out[idx] = (raw - mean) / std
        else:
            out[idx] = raw - mean
    if not np.isfinite(out).any():
        return np.zeros(len(rows), dtype=float)
    fill = float(np.nanmedian(out))
    return np.where(np.isfinite(out), out, fill)


def fit_corrected(
    train_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    target: str,
    feature: str,
    c_value: float,
) -> np.ndarray:
    j = TARGETS.index(target)
    z_tr = add_ref_z(train_rows, train_rows, feature)
    z_pr = add_ref_z(pred_rows, train_rows, feature)
    x_tr = np.column_stack([logit(train_base[:, j]), z_tr])
    x_pr = np.column_stack([logit(pred_base[:, j]), z_pr])
    y = train_rows[target].to_numpy(dtype=int)
    if y.min() == y.max():
        return np.full(len(pred_rows), float(y.mean()))
    clf = LogisticRegression(C=c_value, solver="lbfgs", max_iter=500)
    clf.fit(x_tr, y)
    return clip(clf.predict_proba(x_pr)[:, 1])


def oof_corrected(train: pd.DataFrame, base: np.ndarray, target: str, feature: str, c_value: float) -> np.ndarray:
    pred = np.zeros(len(train), dtype=float)
    for tr_idx, val_idx in make_subject_blocks(train):
        pred[val_idx] = fit_corrected(
            train.iloc[tr_idx].copy(),
            train.iloc[val_idx].copy(),
            base[tr_idx],
            base[val_idx],
            target,
            feature,
            c_value,
        )
    return clip(pred)


def repeated_subject_guardrail(train: pd.DataFrame, y: np.ndarray, base: np.ndarray, corrected: np.ndarray, target_idx: int) -> dict[str, float]:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(260989 + target_idx)
    deltas = []
    weights = []
    for _ in range(260):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        sel = train["subject_id"].astype(str).isin(picked).to_numpy()
        hold = ~sel
        best = None
        for w in GRID:
            p = (1.0 - w) * base[:, target_idx] + w * corrected
            sel_loss = loss_col(y[sel, target_idx], p[sel])
            if best is None or sel_loss < best[0]:
                best = (sel_loss, float(w), p)
        assert best is not None
        hold_base = loss_col(y[hold, target_idx], base[hold, target_idx])
        hold_blend = loss_col(y[hold, target_idx], best[2][hold])
        deltas.append(float(hold_blend - hold_base))
        weights.append(best[1])
    arr = np.asarray(deltas)
    return {
        "mean_delta": float(arr.mean()),
        "median_delta": float(np.median(arr)),
        "p25_delta": float(np.quantile(arr, 0.25)),
        "p75_delta": float(np.quantile(arr, 0.75)),
        "win_rate": float((arr < 0).mean()),
        "mean_selected_weight": float(np.mean(weights)),
        "zero_weight_rate": float((np.asarray(weights) == 0.0).mean()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p578_logit_after_subject_final9_strict_oof.npy")
    parser.add_argument("--prefix", default="current_0p578_quiet_logit")
    parser.add_argument("--top-per-target", type=int, default=10)
    args = parser.parse_args()

    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    quiet = pd.read_parquet(OUT / "quiet_window_residual_features.parquet")
    train = train.merge(quiet, on=KEY, how="left")
    base = clip(np.load(args.base_oof))
    y = train[TARGETS].to_numpy(dtype=int)
    top = pd.read_csv(OUT / "quiet_window_residual_probe.csv")
    candidates = top.groupby("target", group_keys=False).head(args.top_per_target)
    rows = []
    pred_cache: dict[tuple[str, str, float], np.ndarray] = {}
    for cand in candidates.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        if feature not in train:
            continue
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20, 0.50]:
            corrected = oof_corrected(train, base, target, feature, c_value)
            pred_cache[(target, feature, c_value)] = corrected
            corr_loss = loss_col(y[:, j], corrected)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "c_value": c_value,
                "base_loss": base_loss,
                "corrected_loss": corr_loss,
                "best_weight": float(GRID[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(repeated_subject_guardrail(train, y, base, corrected, j))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            row["passes_loose"] = bool(
                row["delta_vs_base"] <= -0.0002 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.58
            )
            row["passes_strict"] = bool(
                row["delta_vs_base"] <= -0.0005 and row["mean_delta"] <= -0.0002 and row["win_rate"] >= 0.65
            )
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / f"{args.prefix}_results.csv", index=False)
    result.groupby("target", group_keys=False).head(10).to_csv(OUT / f"{args.prefix}_top.csv", index=False)
    result[result["passes_loose"]].to_csv(OUT / f"{args.prefix}_selected.csv", index=False)
    print(result.head(35).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
