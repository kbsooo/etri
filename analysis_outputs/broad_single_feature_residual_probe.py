from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

import quiet_feature_logit_postprocess_probe as qlp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
GRID = np.array([0.0, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.45])
MODES = ["global_z", "subject_center", "subject_z", "subject_rank", "missing"]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def prefixed_frame(path: Path, prefix: str, key: list[str] = KEY) -> pd.DataFrame:
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, parse_dates=["lifelog_date"])
    keep = [c for c in df.columns if c in key]
    drop = set(TARGETS + ["sleep_date", "split"])
    cols = [c for c in df.columns if c not in set(key) | drop]
    out = df[keep + cols].copy()
    out = out.rename(columns={c: f"{prefix}__{c}" for c in cols})
    return out


def build_frame() -> pd.DataFrame:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    blocks = [
        prefixed_frame(OUT / "train_deep_features.parquet", "deep"),
        prefixed_frame(OUT / "sleep_interval_proxy_features.parquet", "proxy"),
        prefixed_frame(OUT / "pre_sleep_relative_features.parquet", "presleep"),
        prefixed_frame(OUT / "presleep_temporal_context_features.parquet", "prectx"),
        prefixed_frame(OUT / "quiet_window_residual_features.parquet", "quiet"),
        prefixed_frame(OUT / "wifi_identity_daily_features.csv", "wifi"),
        prefixed_frame(OUT / "ble_identity_daily_features.csv", "ble"),
    ]
    out = train.copy()
    for block in blocks:
        out = out.merge(block, on=KEY, how="left")
    return out.sort_values(KEY).reset_index(drop=True)


def finite_numeric_cols(df: pd.DataFrame) -> list[str]:
    excluded = set(TARGETS + KEY + ["sleep_date"])
    cols = []
    for col in df.columns:
        if col in excluded:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
            cols.append(col)
    return cols


def standardize(ref_vals: np.ndarray, vals: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ok = np.isfinite(ref_vals)
    if ok.sum() == 0:
        return np.zeros_like(ref_vals, dtype=float), np.zeros_like(vals, dtype=float)
    fill = float(np.nanmedian(ref_vals))
    ref = np.where(np.isfinite(ref_vals), ref_vals, fill)
    out = np.where(np.isfinite(vals), vals, fill)
    mean = float(np.mean(ref))
    std = float(np.std(ref, ddof=1)) if len(ref) > 1 else 0.0
    if not np.isfinite(std) or std <= 1e-12:
        return ref * 0.0, out * 0.0
    return (ref - mean) / std, (out - mean) / std


def transform_pair(ref: pd.DataFrame, rows: pd.DataFrame, col: str, mode: str) -> tuple[np.ndarray, np.ndarray]:
    ref_raw = pd.to_numeric(ref[col], errors="coerce").to_numpy(dtype=float)
    row_raw = pd.to_numeric(rows[col], errors="coerce").to_numpy(dtype=float)
    if mode == "missing":
        return ref_raw * 0.0 + pd.isna(ref[col]).to_numpy(dtype=float), row_raw * 0.0 + pd.isna(rows[col]).to_numpy(dtype=float)
    if mode == "global_z":
        return standardize(ref_raw, row_raw)

    ref_out = np.full(len(ref), np.nan, dtype=float)
    row_out = np.full(len(rows), np.nan, dtype=float)
    ref_sids = ref["subject_id"].astype(str).to_numpy()
    row_sids = rows["subject_id"].astype(str).to_numpy()
    for sid in sorted(set(ref_sids) | set(row_sids)):
        ref_idx = np.where(ref_sids == sid)[0]
        row_idx = np.where(row_sids == sid)[0]
        vals = ref_raw[ref_idx]
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        mean = float(np.mean(vals))
        std = float(np.std(vals, ddof=1)) if vals.size > 1 else np.nan
        if mode == "subject_center":
            ref_out[ref_idx] = ref_raw[ref_idx] - mean
            row_out[row_idx] = row_raw[row_idx] - mean
        elif mode == "subject_z":
            denom = std if np.isfinite(std) and std > 1e-12 else 1.0
            ref_out[ref_idx] = (ref_raw[ref_idx] - mean) / denom
            row_out[row_idx] = (row_raw[row_idx] - mean) / denom
        elif mode == "subject_rank":
            sorted_vals = np.sort(vals)
            n = len(sorted_vals)
            ref_out[ref_idx] = (np.searchsorted(sorted_vals, ref_raw[ref_idx], side="right") / max(n, 1)) - 0.5
            row_out[row_idx] = (np.searchsorted(sorted_vals, row_raw[row_idx], side="right") / max(n, 1)) - 0.5
        else:
            raise ValueError(mode)
    return standardize(ref_out, row_out)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 80:
        return np.nan
    aa = a[ok]
    bb = b[ok]
    if np.std(aa) <= 1e-12 or np.std(bb) <= 1e-12:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def prefilter(df: pd.DataFrame, base: np.ndarray, cols: list[str], targets: list[str], top_n: int) -> pd.DataFrame:
    rows = []
    y = df[TARGETS].to_numpy(dtype=int)
    for target in targets:
        j = TARGETS.index(target)
        residual = y[:, j].astype(float) - base[:, j]
        for col in cols:
            for mode in MODES:
                try:
                    x_ref, _ = transform_pair(df, df, col, mode)
                except Exception:
                    continue
                r = corr(x_ref, residual)
                if np.isfinite(r):
                    rows.append({"target": target, "feature": col, "mode": mode, "corr": r, "abs_corr": abs(r)})
    pre = pd.DataFrame(rows).sort_values(["target", "abs_corr"], ascending=[True, False])
    return pre.groupby("target", group_keys=False).head(top_n).reset_index(drop=True)


def fit_corrected(
    train_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    target: str,
    feature: str,
    mode: str,
    c_value: float,
) -> np.ndarray:
    j = TARGETS.index(target)
    z_tr, z_pr = transform_pair(train_rows, pred_rows, feature, mode)
    x_tr = np.column_stack([logit(train_base[:, j]), z_tr])
    x_pr = np.column_stack([logit(pred_base[:, j]), z_pr])
    y = train_rows[target].to_numpy(dtype=int)
    if y.min() == y.max():
        return np.full(len(pred_rows), float(y.mean()))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=500)
    clf.fit(x_tr, y)
    return clip(clf.predict_proba(x_pr)[:, 1])


def oof_corrected(df: pd.DataFrame, base: np.ndarray, target: str, feature: str, mode: str, c_value: float) -> np.ndarray:
    pred = np.zeros(len(df), dtype=float)
    for tr_idx, val_idx in qlp.make_subject_blocks(df):
        pred[val_idx] = fit_corrected(
            df.iloc[tr_idx].copy(),
            df.iloc[val_idx].copy(),
            base[tr_idx],
            base[val_idx],
            target,
            feature,
            mode,
            c_value,
        )
    return clip(pred)


def repeated_subject_guardrail(df: pd.DataFrame, y: np.ndarray, base: np.ndarray, corrected: np.ndarray, target_idx: int) -> dict[str, float]:
    subjects = np.array(sorted(df["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(260991 + target_idx)
    deltas = []
    weights = []
    for _ in range(260):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        sel = df["subject_id"].astype(str).isin(picked).to_numpy()
        hold = ~sel
        best = None
        for w in GRID:
            p = (1.0 - w) * base[:, target_idx] + w * corrected
            sel_loss = loss_col(y[sel, target_idx], p[sel])
            if best is None or sel_loss < best[0]:
                best = (sel_loss, float(w), p)
        assert best is not None
        deltas.append(loss_col(y[hold, target_idx], best[2][hold]) - loss_col(y[hold, target_idx], base[hold, target_idx]))
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
    parser.add_argument("--base-oof", type=Path, default=OUT / "final_hybrid_0p575_foldsafe_quiet_s3_subject_q3_s4_s1_logit_s1_oof.npy")
    parser.add_argument("--prefix", default="current_0p575_broad_single_feature")
    parser.add_argument("--targets", default="Q1,Q2")
    parser.add_argument("--top-n", type=int, default=40)
    args = parser.parse_args()

    df = build_frame()
    base = clip(np.load(args.base_oof))
    y = df[TARGETS].to_numpy(dtype=int)
    targets = [t for t in args.targets.split(",") if t]
    cols = finite_numeric_cols(df)
    pre = prefilter(df, base, cols, targets, args.top_n)
    pre.to_csv(OUT / f"{args.prefix}_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20, 0.50]:
            corrected = oof_corrected(df, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": c_value,
                "base_loss": base_loss,
                "corrected_loss": loss_col(y[:, j], corrected),
                "best_weight": float(GRID[best_i]),
                "best_blend_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(repeated_subject_guardrail(df, y, base, corrected, j))
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
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.58)
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.0004 and row["mean_delta"] <= -0.00015 and row["win_rate"] >= 0.65)
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / f"{args.prefix}_results.csv", index=False)
    result.groupby("target", group_keys=False).head(15).to_csv(OUT / f"{args.prefix}_top.csv", index=False)
    result[result["passes_loose"]].to_csv(OUT / f"{args.prefix}_selected.csv", index=False)
    print(result.head(40).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
