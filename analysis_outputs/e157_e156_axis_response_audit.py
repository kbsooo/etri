#!/usr/bin/env python3
"""E157: audit whether E156's low-body axis choice is signal or selector artifact.

E156 selected the minimum-body all-four row, but the stronger question is whether
target-axis decomposition says anything stable. This audit uses the completed
E156 lattice, computes finite-difference axis responses, and materializes only a
candidate that Pareto-dominates E155 inside the low-body region.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e156_e154_target_axis_lattice as e156  # noqa: E402


SCAN_IN = OUT / "e156_e154_target_axis_lattice_scan.csv"
FINITE_DIFF_OUT = OUT / "e157_e156_axis_response_finite_diffs.csv"
PARETO_OUT = OUT / "e157_e156_axis_response_pareto.csv"
REPORT_OUT = OUT / "e157_e156_axis_response_audit_report.md"
SUBMISSION_PREFIX = "submission_e157_lowbodypareto"

AXES = ["Q1", "Q3", "S2", "S3", "S4"]
METRICS = [
    "all_minus_base",
    "post101_p95_vs_e95_e101_sensor",
    "e72_plausible_gap_vs_e95",
    "body_norm_ratio",
    "transfer_shrinkage_risk_index",
]
STEP = 0.25


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    data = frame.copy()
    if cols is not None:
        data = data[[col for col in cols if col in data.columns]]
    data = data.head(n)
    out = ["| " + " | ".join(data.columns) + " |"]
    out.append("| " + " | ".join(["---"] * len(data.columns)) + " |")
    for _, row in data.iterrows():
        vals: list[str] = []
        for val in row:
            if isinstance(val, float):
                vals.append(f"{val:.12f}")
            else:
                vals.append(str(val))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def finite_differences(variants: pd.DataFrame) -> pd.DataFrame:
    keys = [f"alpha_{axis}" for axis in AXES]
    indexed = variants.reset_index(drop=True).copy()
    pos = {tuple(row[key] for key in keys): i for i, row in indexed.iterrows()}
    rows: list[dict[str, Any]] = []
    for axis in AXES:
        key = f"alpha_{axis}"
        axis_pos = AXES.index(axis)
        for metric in METRICS:
            diffs: list[float] = []
            low_diffs: list[float] = []
            for _, row in indexed.iterrows():
                if float(row[key]) > 1.0 - STEP:
                    continue
                target = [row[col] for col in keys]
                target[axis_pos] = float(target[axis_pos]) + STEP
                nxt = pos.get(tuple(target))
                if nxt is None:
                    continue
                delta = float(indexed.loc[nxt, metric] - row[metric])
                diffs.append(delta)
                if float(row["body_norm_ratio"]) < 0.25:
                    low_diffs.append(delta)
            arr = np.asarray(diffs, dtype=np.float64)
            low = np.asarray(low_diffs, dtype=np.float64)
            rows.append(
                {
                    "axis": axis,
                    "metric": metric,
                    "mean_delta": float(arr.mean()),
                    "median_delta": float(np.median(arr)),
                    "p_favorable": float((arr < 0).mean()),
                    "lowbody_mean_delta": float(low.mean()) if len(low) else np.nan,
                    "lowbody_p_favorable": float((low < 0).mean()) if len(low) else np.nan,
                    "n": int(len(arr)),
                    "lowbody_n": int(len(low)),
                }
            )
    return pd.DataFrame(rows)


def select_pareto(variants: pd.DataFrame, e155: pd.Series) -> pd.DataFrame:
    eligible = variants[
        variants["e156_strict_candidate"].fillna(False).astype(bool)
        & variants["uses_less_body_than_e155"].fillna(False).astype(bool)
        & variants["beats_e155_local"].fillna(False).astype(bool)
        & variants["post101_p95_vs_e95_e101_sensor"].le(float(e155["post101_p95_vs_e95_e101_sensor"]) + 1.0e-12)
        & variants["e72_plausible_gap_vs_e95"].le(float(e155["e72_plausible_gap_vs_e95"]) + 1.0e-12)
    ].copy()
    if eligible.empty:
        return eligible
    eligible["delta_all_vs_e155"] = eligible["all_minus_base"] - float(e155["all_minus_base"])
    eligible["delta_body_vs_e155"] = eligible["body_norm_ratio"] - float(e155["body_norm_ratio"])
    eligible["delta_post101_p95_vs_e155"] = (
        eligible["post101_p95_vs_e95_e101_sensor"] - float(e155["post101_p95_vs_e95_e101_sensor"])
    )
    eligible["delta_e72_gap_vs_e155"] = eligible["e72_plausible_gap_vs_e95"] - float(e155["e72_plausible_gap_vs_e95"])
    return eligible.sort_values(
        ["all_minus_base", "post101_p95_vs_e95_e101_sensor", "body_norm_ratio"],
        ascending=[True, True, True],
    )


def build_axis_prediction(row: pd.Series) -> tuple[pd.DataFrame, Path]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    refs["e144"] = e156.load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample)
    refs["e154"] = e156.load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample)
    e144_logit = logit(refs["e144"])
    body = logit(refs["e154"]) - e144_logit
    scaled = np.zeros_like(body)
    for idx, target in enumerate(TARGETS):
        scaled[:, idx] = float(row.get(f"alpha_{target}", 0.0)) * body[:, idx]
    pred = e156.clip_prob(e156.sigmoid(e144_logit + scaled))
    suffix = str(row["tag"]).split("_")[-1]
    out_path = OUT / f"{SUBMISSION_PREFIX}_{suffix}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = pred
    sub.to_csv(out_path, index=False)
    return sub, out_path


def write_report(scan: pd.DataFrame, diffs: pd.DataFrame, pareto: pd.DataFrame, submission_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("target_axis_lattice")].copy()
    controls = scan[scan["strategy"].astype(str).str.startswith("control_")].copy()
    e155 = controls[controls["strategy"].eq("control_e155")].iloc[0]
    e156_min = variants[variants["materialized_submission"].fillna(False).astype(bool)].iloc[0]
    selected = pareto.iloc[0] if len(pareto) else None

    all_span = float(variants["all_minus_base"].max() - variants["all_minus_base"].min())
    all_four = int(variants["all_four_health"].fillna(False).astype(bool).sum())
    strict = int(variants["e156_strict_candidate"].fillna(False).astype(bool).sum())

    lines = [
        "# E157 E156 Axis Response Audit",
        "",
        "## Question",
        "",
        "Did E156's Q1/S2/S4 minimum-body row reveal a target law, or did the all-four gate saturate so that body-minimization selected a low-information point?",
        "",
        "## Strange Point",
        "",
        f"- E156 lattice variants: `{len(variants)}`.",
        f"- all-four variants: `{all_four}`.",
        f"- strict candidates: `{strict}`.",
        f"- all-minus-E95 span across the whole lattice: `{all_span:.12f}`.",
        f"- E156 min-body file: `submission_e156_targetaxis_757546d2.csv`, axes `{e156_min['target_axes']}`, body `{float(e156_min['body_norm_ratio']):.12f}`.",
        "",
        "## Finite-Difference Axis Response",
        "",
        md_table(
            diffs[diffs["metric"].eq("all_minus_base")].sort_values("mean_delta"),
            ["axis", "metric", "mean_delta", "p_favorable", "lowbody_mean_delta", "lowbody_p_favorable"],
        ),
        "",
        md_table(
            diffs[diffs["metric"].eq("post101_p95_vs_e95_e101_sensor")].sort_values("mean_delta"),
            ["axis", "metric", "mean_delta", "p_favorable", "lowbody_mean_delta", "lowbody_p_favorable"],
        ),
        "",
        md_table(
            diffs[diffs["metric"].eq("e72_plausible_gap_vs_e95")].sort_values("mean_delta"),
            ["axis", "metric", "mean_delta", "p_favorable", "lowbody_mean_delta", "lowbody_p_favorable"],
        ),
        "",
        "## E155-Dominating Low-Body Rows",
        "",
        md_table(
            pareto,
            [
                "tag",
                "target_axes",
                "body_norm_ratio",
                "all_minus_base",
                "delta_all_vs_e155",
                "post101_p95_vs_e95_e101_sensor",
                "delta_post101_p95_vs_e155",
                "e72_plausible_gap_vs_e95",
                "delta_e72_gap_vs_e155",
                "alpha_Q1",
                "alpha_Q3",
                "alpha_S2",
                "alpha_S3",
                "alpha_S4",
            ],
            12,
        ),
        "",
        "## Decision",
        "",
    ]
    if selected is None or submission_path is None:
        lines.append("No E157 submission: no low-body target-axis row dominated E155 across local, post-E101, and E72 stress.")
    else:
        lines.extend(
            [
                f"Materialized `{submission_path.name}` because it uses less body than E155 while improving local all-minus, post-E101 p95, and E72 gap.",
                "",
                f"Selected axes: `{selected['target_axes']}`.",
                f"Selected all-minus-E95: `{float(selected['all_minus_base']):.12f}` vs E155 `{float(e155['all_minus_base']):.12f}`.",
                f"Selected body ratio: `{float(selected['body_norm_ratio']):.12f}` vs E155 `{float(e155['body_norm_ratio']):.12f}`.",
                "",
                "This is not a new first sensor. The E155-dominating edge is far below public-resolution scale, and the finite-difference audit shows Q3 is locally favorable rather than rejected. E157 is a tuned low-body Pareto control; E154 remains the first public sensor and E155 remains the cleaner amplitude-control interpretation.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan = pd.read_csv(SCAN_IN)
    variants = scan[scan["strategy"].eq("target_axis_lattice")].copy()
    controls = scan[scan["strategy"].astype(str).str.startswith("control_")].copy()
    e155 = controls[controls["strategy"].eq("control_e155")].iloc[0]

    diffs = finite_differences(variants)
    pareto = select_pareto(variants, e155)
    submission_path: Path | None = None
    if len(pareto):
        _sub, submission_path = build_axis_prediction(pareto.iloc[0])

    diffs.to_csv(FINITE_DIFF_OUT, index=False)
    pareto.to_csv(PARETO_OUT, index=False)
    write_report(scan, diffs, pareto, submission_path)

    print(
        {
            "variants": int(len(variants)),
            "all_four": int(variants["all_four_health"].fillna(False).astype(bool).sum()),
            "strict": int(variants["e156_strict_candidate"].fillna(False).astype(bool).sum()),
            "e155_dominating_lowbody": int(len(pareto)),
            "submission": str(submission_path) if submission_path else None,
        }
    )
    if len(pareto):
        print(
            pareto[
                [
                    "tag",
                    "target_axes",
                    "body_norm_ratio",
                    "all_minus_base",
                    "post101_p95_vs_e95_e101_sensor",
                    "e72_plausible_gap_vs_e95",
                    "alpha_Q1",
                    "alpha_Q3",
                    "alpha_S2",
                    "alpha_S3",
                    "alpha_S4",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
