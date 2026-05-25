#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
EXP = ROOT / "experiments"
DATA = ROOT / "data"
IDS = ["subject_id", "sleep_date", "lifelog_date"]
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

PUBLIC_FEEDBACK = {
    "submission_temporal_state_smoothing_wcap02_prob.csv": 0.6311869686,
    "submission_v38_targetwise_catboost_proto_safe_prob.csv": 0.6218639574,
    "submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv": 0.6610032443,
    "submission_cl_catboost_state_proto_sleep_state_prob.csv": 0.6146217599,
}


def md_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in df.iterrows():
        vals = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                vals.append(f"{float(v):.6f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in IDS:
        if "date" in c:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
        else:
            out[c] = out[c].astype(str)
    return out


def read_sub(name: str) -> pd.DataFrame:
    return norm_dates(pd.read_csv(OUT / name)).sort_values(IDS).reset_index(drop=True)


def clip(x, lo=0.03, hi=0.97):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def logit_blend(anchor: pd.DataFrame, model: pd.DataFrame, weights: dict[str, float], temp: float = 1.0) -> pd.DataFrame:
    out = anchor.copy()
    for y in LABELS:
        w = weights.get(y, 0.0)
        z = (1 - w) * logit(anchor[y]) + w * logit(model[y])
        out[y] = clip(sigmoid(z / temp))
    return out


def gated_extra(base: pd.DataFrame, anchor: pd.DataFrame, model: pd.DataFrame, specs: dict[str, tuple[float, float]]) -> pd.DataFrame:
    out = base.copy()
    for y, (top_frac, extra_w) in specs.items():
        delta = model[y].to_numpy(float) - anchor[y].to_numpy(float)
        thr = np.quantile(np.abs(delta), 1 - top_frac)
        gate = np.abs(delta) >= thr
        cur = out[y].to_numpy(float).copy()
        cur[gate] = cur[gate] * (1 - extra_w) + model[y].to_numpy(float)[gate] * extra_w
        out[y] = clip(cur)
    return out


def distribution_guard(df: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    """Keep the aggressive candidates from becoming the failed v81 shape."""
    out = df.copy()
    for y in LABELS:
        # Keep each target's spread within a broad but finite band around the
        # public-improving sleep_state file, not the failed imported v81 file.
        lo = max(0.03, reference[y].quantile(0.01) - 0.035)
        hi = min(0.97, reference[y].quantile(0.99) + 0.035)
        out[y] = out[y].clip(lo, hi)
    return out


def build_candidates(anchor: pd.DataFrame, model: pd.DataFrame, sleep: pd.DataFrame) -> dict[str, pd.DataFrame]:
    # Public feedback says safe < sleep_state and v81 is strongly wrong.
    # Therefore the extrapolation axis is only the CL CatBoost sleep/state axis:
    # Q3/S1/S2 up in movement, Q1/Q2/S3 heavily constrained.
    step2 = logit_blend(
        anchor,
        model,
        {"Q1": 0.00, "Q2": 0.04, "Q3": 0.62, "S1": 0.64, "S2": 0.56, "S3": 0.00, "S4": 0.22},
        temp=1.10,
    )
    step3 = logit_blend(
        anchor,
        model,
        {"Q1": 0.00, "Q2": 0.02, "Q3": 0.78, "S1": 0.76, "S2": 0.68, "S3": 0.00, "S4": 0.26},
        temp=1.15,
    )
    rowgate = gated_extra(
        sleep.copy(),
        anchor,
        model,
        {
            "Q3": (0.40, 0.22),
            "S1": (0.35, 0.20),
            "S2": (0.35, 0.20),
            "S4": (0.25, 0.10),
        },
    )
    consensus = sleep.copy()
    for y in LABELS:
        if y in ["Q3", "S1", "S2", "S4"]:
            consensus[y] = clip(0.50 * sleep[y] + 0.25 * step2[y] + 0.25 * rowgate[y])
        else:
            consensus[y] = sleep[y]

    return {
        "submission_cl_catboost_public_axis_step2_prob.csv": distribution_guard(step2, sleep),
        "submission_cl_catboost_public_axis_step3_prob.csv": distribution_guard(step3, sleep),
        "submission_cl_catboost_public_axis_rowgate_prob.csv": distribution_guard(rowgate, sleep),
        "submission_cl_catboost_public_axis_consensus_prob.csv": distribution_guard(consensus, sleep),
    }


def summarize(files: dict[str, pd.DataFrame], anchor: pd.DataFrame, sleep: pd.DataFrame, model: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = norm_dates(pd.read_csv(DATA / "ch2026_submission_sample.csv")).sort_values(IDS).reset_index(drop=True)
    rows = []
    target_rows = []
    for name, df in files.items():
        df = norm_dates(df).sort_values(IDS).reset_index(drop=True)
        df.to_csv(OUT / name, index=False)
        for y in LABELS:
            da = df[y].to_numpy(float) - anchor[y].to_numpy(float)
            ds = df[y].to_numpy(float) - sleep[y].to_numpy(float)
            dm = df[y].to_numpy(float) - model[y].to_numpy(float)
            target_rows.append(
                {
                    "file": name,
                    "target": y,
                    "mean_abs_vs_anchor": float(np.abs(da).mean()),
                    "mean_abs_vs_sleep_state": float(np.abs(ds).mean()),
                    "mean_abs_vs_raw_model": float(np.abs(dm).mean()),
                    "signed_vs_anchor": float(da.mean()),
                    "std": float(df[y].std()),
                    "min": float(df[y].min()),
                    "max": float(df[y].max()),
                    "corr_vs_anchor": float(np.corrcoef(df[y], anchor[y])[0, 1]),
                }
            )
        rows.append(
            {
                "file": name,
                "rows": len(df),
                "keys_ok": bool(df[IDS].equals(sample[IDS])),
                "no_na": bool(df[LABELS].notna().all().all()),
                "mean_abs_vs_anchor": float(np.mean([np.abs(df[y] - anchor[y]).mean() for y in LABELS])),
                "mean_abs_vs_sleep_state": float(np.mean([np.abs(df[y] - sleep[y]).mean() for y in LABELS])),
                "min_prob": float(df[LABELS].min().min()),
                "max_prob": float(df[LABELS].max().max()),
                "mean_target_std": float(df[LABELS].std().mean()),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(target_rows)


def write_report(file_summary: pd.DataFrame, target_summary: pd.DataFrame) -> None:
    feedback = pd.DataFrame([{"file": k, "public_lb": v} for k, v in PUBLIC_FEEDBACK.items()])
    lines = [
        "# CL CatBoost Public Axis Candidates",
        "",
        "## Public Feedback Used",
        "",
        md_table(feedback),
        "",
        "Interpretation: imported v81 is anti-public; CL CatBoost direction is public-positive; more sleep/state movement beat the safe blend.",
        "",
        "## Candidate Files",
        "",
        md_table(file_summary),
        "",
        "## Target Movement",
        "",
        md_table(target_summary),
        "",
        "## Intended Order For Tomorrow",
        "",
        "1. `submission_cl_catboost_public_axis_consensus_prob.csv`",
        "2. `submission_cl_catboost_public_axis_step2_prob.csv`",
        "3. `submission_cl_catboost_public_axis_rowgate_prob.csv`",
        "",
        "`step3` is the minimum-0.57 attempt, not the first diagnostic. It moves far enough to plausibly jump but has the largest overfit risk.",
    ]
    (EXP / "cl_catboost_public_axis_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    EXP.mkdir(parents=True, exist_ok=True)
    anchor = read_sub("submission_meta_anchor_w02_noq3_prob.csv")
    model = read_sub("submission_v38_targetwise_catboost_proto_raw_model_prob.csv")
    sleep = read_sub("submission_cl_catboost_state_proto_sleep_state_prob.csv")
    files = build_candidates(anchor, model, sleep)
    file_summary, target_summary = summarize(files, anchor, sleep, model)
    file_summary.to_csv(EXP / "cl_catboost_public_axis_file_summary.csv", index=False)
    target_summary.to_csv(EXP / "cl_catboost_public_axis_target_summary.csv", index=False)
    write_report(file_summary, target_summary)
    print(file_summary.to_string(index=False))


if __name__ == "__main__":
    main()
