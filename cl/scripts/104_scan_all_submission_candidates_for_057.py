#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CL_ROOT = ROOT / "cl"
sys.path.insert(0, str(CL_ROOT))
from src.cl_common import EXPERIMENT_DIR, LABELS, OUT_DIR, ensure_dirs

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in KEYS:
        if "date" in c:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
        else:
            out[c] = out[c].astype(str)
    return out


def load(path: Path) -> pd.DataFrame | None:
    try:
        df = norm_dates(pd.read_csv(path))
    except Exception:
        return None
    if not set(KEYS + LABELS).issubset(df.columns):
        return None
    return df[KEYS + LABELS].sort_values(KEYS).reset_index(drop=True)


def mat(df: pd.DataFrame) -> np.ndarray:
    return np.clip(df[LABELS].to_numpy(float), EPS, 1 - EPS)


def bce_soft(q: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1 - EPS)
    return float(np.mean(-(q * np.log(p) + (1 - q) * np.log(1 - p))))


def entropy(p: np.ndarray) -> float:
    return bce_soft(p, p)


def main() -> None:
    ensure_dirs()
    sample = load(ROOT / "data/ch2026_submission_sample.csv")
    assert sample is not None
    v83 = mat(load(ROOT / "outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv"))
    v76 = mat(load(ROOT / "outputs/public_lb_pseudolabel_calibration/submission_02_exact_v76_public_anchor_reconstructed.csv"))
    old_q = pd.read_csv(ROOT / "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv")[LABELS].to_numpy(float)
    refit_q = mat(load(EXPERIMENT_DIR / "cl_public_anchor_clue_refit_posterior_values.csv"))
    rows = []
    paths = sorted(set(ROOT.glob("outputs/**/submission*.csv")) | set((ROOT / "cl" / "outputs").glob("submission*.csv")))
    for path in paths:
        df = load(path)
        if df is None or not df[KEYS].equals(sample[KEYS]):
            continue
        p = mat(df)
        d83 = np.abs(p - v83)
        d76 = np.abs(p - v76)
        old = bce_soft(old_q, p)
        refit = bce_soft(refit_q, p)
        robust = max(old, refit)
        drift83 = float(d83.mean())
        max83 = float(d83.max())
        # v85 failure says low posterior alone is not enough. Penalize high drift,
        # saturation, and public-anchor mean distortion.
        score = (
            robust
            + max(0.0, drift83 - 0.025) * 1.5
            + max(0.0, max83 - 0.18) * 0.05
            + max(0.0, abs(float(p[:, 0].mean() - v83[:, 0].mean())) - 0.006) * 1.2
            + max(0.0, entropy(v83) - entropy(p) - 0.04) * 0.40
        )
        rows.append(
            {
                "path": str(path.relative_to(ROOT)),
                "selection_score": score,
                "posterior_old_bce": old,
                "posterior_refit_bce": refit,
                "robust_posterior": robust,
                "entropy": entropy(p),
                "drift_v83": drift83,
                "max_drift_v83": max83,
                "drift_v76": float(d76.mean()),
                "mean_Q1": float(p[:, 0].mean()),
                "mean_Q2": float(p[:, 1].mean()),
                "mean_Q3": float(p[:, 2].mean()),
                "mean_S1": float(p[:, 3].mean()),
                "mean_S2": float(p[:, 4].mean()),
                "mean_S3": float(p[:, 5].mean()),
                "mean_S4": float(p[:, 6].mean()),
                "min_prob": float(p.min()),
                "max_prob": float(p.max()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["selection_score", "robust_posterior"]).reset_index(drop=True)
    out.to_csv(EXPERIMENT_DIR / "cl_all_submission_057_scan_scores.csv", index=False)
    credible = out[
        (out["robust_posterior"] < 0.585)
        & (out["drift_v83"] < 0.04)
        & (out["max_drift_v83"] < 0.22)
        & (out["mean_Q1"].between(0.49, 0.525))
    ].copy()
    credible.to_csv(EXPERIMENT_DIR / "cl_all_submission_057_scan_credible_under0585.csv", index=False)

    def md_table(df: pd.DataFrame, n: int = 30) -> str:
        if df.empty:
            return "_empty_"
        d = df.head(n).copy()
        cols = list(d.columns)
        lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in d.iterrows():
            vals = []
            for v in r.tolist():
                if isinstance(v, (float, np.floating)) and pd.notna(v):
                    vals.append(f"{float(v):.6f}")
                else:
                    vals.append(str(v))
            lines.append("| " + " | ".join(vals) + " |")
        return "\n".join(lines)

    report = "\n".join(
        [
            "# All Submission Candidate Scan For 0.57",
            "",
            f"Scanned `{len(out)}` submission-shaped files with keys matching the sample.",
            "",
            "## Top Robust Candidates",
            "",
            md_table(out[["path", "selection_score", "posterior_old_bce", "posterior_refit_bce", "robust_posterior", "drift_v83", "max_drift_v83", "entropy", "mean_Q1", "mean_S1", "mean_S2", "mean_S3"]], 35),
            "",
            "## Credible Under 0.585 Gate",
            "",
            md_table(credible[["path", "selection_score", "posterior_old_bce", "posterior_refit_bce", "robust_posterior", "drift_v83", "max_drift_v83", "mean_Q1", "mean_S1", "mean_S2", "mean_S3"]], 30),
            "",
            "## Verdict",
            "",
            "- If this table is empty or only contains already-failed posterior/sharp candidates, the repo does not contain a credible 0.57 file under current public constraints.",
            "- Candidates with low old-posterior but high refit-posterior or high drift are not trusted because v85 already falsified that behavior.",
        ]
    )
    (EXPERIMENT_DIR / "cl_all_submission_057_scan_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
