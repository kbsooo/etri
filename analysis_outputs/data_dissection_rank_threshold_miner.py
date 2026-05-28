from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"

sys.path.append(str(OUT))
import geometry_mask_cv_experiments as geom  # noqa: E402


def clip(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=float), 1e-5, 1.0 - 1e-5)


def target_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(log_loss(y.astype(int), clip(p), labels=[0, 1]))


def read_core() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = clip(np.load(BASE_OOF))
    return train, sub, base


def feature_candidates(limit_per_type: int = 80) -> pd.DataFrame:
    sig = pd.read_csv(OUT / "data_dissection_feature_signal_all.csv")
    parts = []
    for signal_type in ["residual", "label"]:
        part = sig[sig["signal_type"].eq(signal_type)].sort_values("abs_corr", ascending=False).head(limit_per_type)
        parts.append(part)
    shift = sig.drop_duplicates(["feature_file", "feature"]).assign(abs_shift=lambda d: d["sub_train_z_shift"].abs()).sort_values("abs_shift", ascending=False).head(40)
    parts.append(shift)
    cols = ["feature_file", "feature"]
    return pd.concat(parts, ignore_index=True)[cols].drop_duplicates().reset_index(drop=True)


def load_feature_matrix(train: pd.DataFrame, sub: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    frame = train[SUB_KEY].copy()
    for feature_file, group in candidates.groupby("feature_file", sort=False):
        path = OUT / str(feature_file)
        if not path.exists():
            continue
        df0 = pd.read_parquet(path)
        for col in ["lifelog_date", "sleep_date"]:
            if col in df0.columns:
                df0[col] = pd.to_datetime(df0[col])
        key = SUB_KEY if "sleep_date" in df0.columns else KEY
        feats = [c for c in group["feature"].astype(str).tolist() if c in df0.columns]
        if not feats:
            continue
        df = df0[key + feats].copy()
        rename = {c: f"{Path(str(feature_file)).stem}__{c}" for c in feats}
        df = df.rename(columns=rename)
        left_keys = SUB_KEY if key == SUB_KEY else KEY
        frame = frame.merge(df, left_on=left_keys, right_on=key, how="left")
        extra_keys = [c for c in key if c not in left_keys]
        if extra_keys:
            frame = frame.drop(columns=extra_keys)
    return frame


def transforms(frame: pd.DataFrame, col: str) -> dict[str, np.ndarray]:
    x = pd.to_numeric(frame[col], errors="coerce").astype(float)
    x = x.replace([np.inf, -np.inf], np.nan)
    med = float(x.median()) if np.isfinite(x.median()) else 0.0
    raw = x.fillna(med).to_numpy(dtype=float)
    out = {"raw": raw}
    subj = frame["subject_id"].astype(str).to_numpy()
    center = raw.copy()
    z = raw.copy()
    rank = np.zeros_like(raw, dtype=float)
    for sid in np.unique(subj):
        idx = np.where(subj == sid)[0]
        vals = raw[idx]
        mu = float(vals.mean())
        sd = float(vals.std())
        center[idx] = vals - mu
        z[idx] = (vals - mu) / max(sd, 1e-6)
        order = pd.Series(vals).rank(method="average", pct=True).to_numpy(dtype=float)
        rank[idx] = order
    out["subject_center"] = center
    out["subject_z"] = z
    out["subject_rank"] = rank
    return out


def fit_stump(x: np.ndarray, y: np.ndarray, train_idx: np.ndarray) -> tuple[str, float, float, float]:
    xt = x[train_idx]
    yt = y[train_idx].astype(float)
    qs = np.unique(np.quantile(xt, np.linspace(0.10, 0.90, 9)))
    best = ("high", float(qs[0]), 0.5, 0.5, 99.0)
    prior = float((yt.sum() + 1.0) / (len(yt) + 2.0))
    for thr in qs:
        for direction in ["high", "low"]:
            mask = xt >= thr if direction == "high" else xt <= thr
            if mask.sum() < 3 or (~mask).sum() < 3:
                continue
            p_pos = float((yt[mask].sum() + 1.0) / (mask.sum() + 2.0))
            p_neg = float((yt[~mask].sum() + 1.0) / ((~mask).sum() + 2.0))
            pred = np.where(mask, p_pos, p_neg)
            loss = target_loss(yt, pred)
            if loss < best[-1]:
                best = (direction, float(thr), p_pos, p_neg, loss)
    if best[-1] == 99.0:
        return "high", float(np.median(xt)), prior, prior
    return best[0], best[1], best[2], best[3]


def apply_stump(x: np.ndarray, direction: str, thr: float, p_pos: float, p_neg: float) -> np.ndarray:
    mask = x >= thr if direction == "high" else x <= thr
    return clip(np.where(mask, p_pos, p_neg))


def scan_thresholds(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train[TARGETS].to_numpy(int)
    feature_cols = [c for c in frame.columns if c not in set(SUB_KEY)]
    folds = geom.geometry_folds(train, sub, n_repeats=4, seed=314159)
    summary_rows = []
    fold_rows = []
    for col_i, col in enumerate(feature_cols):
        if col_i % 25 == 0:
            print(f"rank-threshold feature {col_i}/{len(feature_cols)}", flush=True)
        for mode, x in transforms(frame, col).items():
            if np.nanstd(x) < 1e-9:
                continue
            for target_j, target in enumerate(TARGETS):
                oof = np.full(len(train), np.nan, dtype=float)
                fold_losses = []
                base_losses = []
                dirs = []
                for tr_idx, val_idx, fold in folds:
                    direction, thr, p_pos, p_neg = fit_stump(x, y[:, target_j], tr_idx)
                    pred = apply_stump(x[val_idx], direction, thr, p_pos, p_neg)
                    oof[val_idx] = pred
                    loss = target_loss(y[val_idx, target_j], pred)
                    base_loss = target_loss(y[val_idx, target_j], base[val_idx, target_j])
                    fold_losses.append(loss)
                    base_losses.append(base_loss)
                    dirs.append(direction)
                    fold_rows.append(
                        {
                            "feature": col,
                            "mode": mode,
                            "target": target,
                            "fold": fold,
                            "direction": direction,
                            "threshold": thr,
                            "p_pos": p_pos,
                            "p_neg": p_neg,
                            "loss": loss,
                            "base_loss": base_loss,
                            "delta": loss - base_loss,
                        }
                    )
                covered = np.isfinite(oof)
                full_loss = target_loss(y[covered, target_j], oof[covered])
                full_base = target_loss(y[covered, target_j], base[covered, target_j])
                summary_rows.append(
                    {
                        "feature": col,
                        "mode": mode,
                        "target": target,
                        "full_loss": full_loss,
                        "full_base_loss": full_base,
                        "full_delta_vs_stage2": full_loss - full_base,
                        "mean_fold_loss": float(np.mean(fold_losses)),
                        "mean_fold_delta": float(np.mean(np.asarray(fold_losses) - np.asarray(base_losses))),
                        "win_rate": float(np.mean((np.asarray(fold_losses) - np.asarray(base_losses)) < 0)),
                        "dominant_direction": max(set(dirs), key=dirs.count),
                    }
                )
    summary = pd.DataFrame(summary_rows).sort_values(["full_delta_vs_stage2", "full_loss"])
    folds_df = pd.DataFrame(fold_rows)
    return summary, folds_df


def write_report(summary: pd.DataFrame) -> None:
    lines = [
        "# Rank/Threshold Miner",
        "",
        "This scans top residual/label/shift features as possible subject-relative threshold rules. Each candidate is a one-level stump selected inside geometry folds.",
        "",
        "## Best Overall",
        "",
        "```",
        summary.head(30).to_string(index=False),
        "```",
        "",
        "## Best By Target",
        "",
        "```",
        summary.sort_values(['target', 'full_delta_vs_stage2']).groupby('target').head(8).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "If these stumps beat stage2, the label likely has a recoverable threshold/rank component. If they lose but still show stable direction, use them as weak count priors rather than direct probability replacements.",
    ]
    (OUT / "data_dissection_rank_threshold_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    train, sub, base = read_core()
    candidates = feature_candidates()
    candidates.to_csv(OUT / "data_dissection_rank_threshold_feature_candidates.csv", index=False)
    frame = load_feature_matrix(train, sub, candidates)
    summary, folds = scan_thresholds(train, sub, base, frame)
    summary.to_csv(OUT / "data_dissection_rank_threshold_scan.csv", index=False)
    folds.to_csv(OUT / "data_dissection_rank_threshold_folds.csv", index=False)
    write_report(summary)
    print("wrote", OUT / "data_dissection_rank_threshold_report.md")
    print(summary.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
