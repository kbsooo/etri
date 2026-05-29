#!/usr/bin/env python3
"""E149: anchor-geometry audit for E144.

E147/E148 say E144 is visible-prior supported but public-tail fragile. This
audit asks a different pre-public question:

Is E144 a genuinely new E95 successor direction, or mostly a pruned member of
the E142/E143 residual branch that stays close to the hardtail frontier while
trying not to re-enter E72/E101 public-negative axes?

No submission is generated. The output is a geometry/attribution guardrail for
interpreting E144 before public feedback.
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

from public_anchor_bottleneck_decomposition import TARGETS, load_sub, logit  # noqa: E402


FILES: dict[str, str] = {
    "mixmin": "submission_mixmin_0c916bb4.csv",
    "failed_e72": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "e85": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86": "submission_e86_e85_consensus_a3f7c96f.csv",
    "e89": "submission_e89_e72decontam_00d7807f.csv",
    "e90": "submission_e90_e72pareto_28925de5.csv",
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e101": "submission_e101_q2s3tail_177569bc.csv",
    "e142": "submission_e142_transferclip_09a92236.csv",
    "e143": "submission_e143_activeq2s3repair_68ca656f.csv",
    "e144": "submission_e144_activeboundary_d7b4b331.csv",
}

PUBLIC_LB: dict[str, float] = {
    "mixmin": 0.5763066405,
    "failed_e72": 0.5764077772,
    "e95": 0.5762913298,
    "e101": 0.5763003660,
}

SUMMARY_OUT = OUT / "e149_e144_anchor_geometry_summary.csv"
PAIR_OUT = OUT / "e149_e144_anchor_geometry_pairwise.csv"
TARGET_OUT = OUT / "e149_e144_anchor_geometry_target.csv"
REPORT_OUT = OUT / "e149_e144_anchor_geometry_report.md"

EPS = 1.0e-12


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def cosine(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
    av = np.asarray(a, dtype=np.float64)
    bv = np.asarray(b, dtype=np.float64)
    if mask is not None:
        av = av[mask]
        bv = bv[mask]
    av = av.reshape(-1)
    bv = bv.reshape(-1)
    den = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if den <= EPS:
        return np.nan
    return float(np.dot(av, bv) / den)


def projection(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
    av = np.asarray(a, dtype=np.float64)
    bv = np.asarray(b, dtype=np.float64)
    if mask is not None:
        av = av[mask]
        bv = bv[mask]
    av = av.reshape(-1)
    bv = bv.reshape(-1)
    den = float(np.dot(bv, bv))
    if den <= EPS:
        return np.nan
    return float(np.dot(av, bv) / den)


def resid_ratio(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
    scale = projection(a, b, mask)
    if not np.isfinite(scale):
        return np.nan
    av = np.asarray(a, dtype=np.float64)
    bv = np.asarray(b, dtype=np.float64)
    if mask is not None:
        av = av[mask]
        bv = bv[mask]
    num = float(np.linalg.norm((av - scale * bv).reshape(-1)))
    den = float(np.linalg.norm(av.reshape(-1)))
    if den <= EPS:
        return np.nan
    return num / den


def norm_l2(a: np.ndarray, mask: np.ndarray | None = None) -> float:
    av = np.asarray(a, dtype=np.float64)
    if mask is not None:
        av = av[mask]
    return float(np.linalg.norm(av.reshape(-1)))


def l1(a: np.ndarray, mask: np.ndarray | None = None) -> float:
    av = np.asarray(a, dtype=np.float64)
    if mask is not None:
        av = av[mask]
    return float(np.abs(av).sum())


def target_l1_shares(delta: np.ndarray) -> dict[str, float]:
    abs_delta = np.abs(delta)
    total = float(abs_delta.sum())
    out: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        out[f"share_{target}"] = float(abs_delta[:, j].sum() / total) if total > 0 else 0.0
    q_mask = np.array([t.startswith("Q") for t in TARGETS], dtype=bool)
    s_mask = ~q_mask
    q2s3 = np.array([t in {"Q2", "S3"} for t in TARGETS], dtype=bool)
    out["q_share"] = float(abs_delta[:, q_mask].sum() / total) if total > 0 else 0.0
    out["s_share"] = float(abs_delta[:, s_mask].sum() / total) if total > 0 else 0.0
    out["q2s3_share"] = float(abs_delta[:, q2s3].sum() / total) if total > 0 else 0.0
    return out


def load_predictions() -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    sample = load_sub(FILES["e95"])
    probs: dict[str, np.ndarray] = {}
    logits: dict[str, np.ndarray] = {}
    for name, file_name in FILES.items():
        frame = load_sub(file_name, sample)
        p = frame[TARGETS].to_numpy(dtype=np.float64)
        probs[name] = p
        logits[name] = logit(p)
    return sample, probs, logits


def build_summary(probs: dict[str, np.ndarray], logits: dict[str, np.ndarray]) -> pd.DataFrame:
    z = logits
    axes = {
        "hardtail_e95_minus_mixmin": z["e95"] - z["mixmin"],
        "e72_fail_minus_e95": z["failed_e72"] - z["e95"],
        "e101_loss_minus_e95": z["e101"] - z["e95"],
        "e142_branch_minus_e95": z["e142"] - z["e95"],
        "e143_branch_minus_e95": z["e143"] - z["e95"],
        "e144_branch_minus_e95": z["e144"] - z["e95"],
    }
    e101_active = np.abs(axes["e101_loss_minus_e95"]) > 1.0e-9
    e72_active = np.abs(axes["e72_fail_minus_e95"]) > 1.0e-9
    e144_active = np.abs(axes["e144_branch_minus_e95"]) > 1.0e-9

    rows: list[dict[str, Any]] = []
    for name in ["mixmin", "failed_e72", "e85", "e86", "e89", "e90", "e101", "e142", "e143", "e144"]:
        delta = z[name] - z["e95"]
        active = np.abs(delta) > 1.0e-9
        rec: dict[str, Any] = {
            "name": name,
            "file": FILES[name],
            "public_lb": PUBLIC_LB.get(name, np.nan),
            "public_delta_vs_e95": PUBLIC_LB.get(name, np.nan) - PUBLIC_LB["e95"] if name in PUBLIC_LB else np.nan,
            "changed_cells_vs_e95": int(active.sum()),
            "changed_rows_vs_e95": int(active.any(axis=1).sum()),
            "l1_logit_vs_e95": l1(delta),
            "l2_logit_vs_e95": norm_l2(delta),
            "mean_abs_prob_vs_e95": float(np.abs(probs[name] - probs["e95"]).mean()),
            "max_abs_prob_vs_e95": float(np.abs(probs[name] - probs["e95"]).max()),
            "active_overlap_with_e101_cells": int((active & e101_active).sum()),
            "active_overlap_with_e72_cells": int((active & e72_active).sum()),
            "active_overlap_with_e144_cells": int((active & e144_active).sum()),
            "overlap_e101_share_of_active": float((active & e101_active).sum() / max(int(active.sum()), 1)),
            "overlap_e72_share_of_active": float((active & e72_active).sum() / max(int(active.sum()), 1)),
            "overlap_e144_share_of_active": float((active & e144_active).sum() / max(int(active.sum()), 1)),
            "cos_hardtail_axis": cosine(delta, axes["hardtail_e95_minus_mixmin"]),
            "proj_on_hardtail_axis": projection(delta, axes["hardtail_e95_minus_mixmin"]),
            "cos_e101_loss_axis": cosine(delta, axes["e101_loss_minus_e95"]),
            "proj_on_e101_loss_axis": projection(delta, axes["e101_loss_minus_e95"]),
            "cos_e72_fail_axis": cosine(delta, axes["e72_fail_minus_e95"]),
            "proj_on_e72_fail_axis": projection(delta, axes["e72_fail_minus_e95"]),
            "cos_e142_branch_axis": cosine(delta, axes["e142_branch_minus_e95"]),
            "proj_on_e142_branch_axis": projection(delta, axes["e142_branch_minus_e95"]),
            "cos_e143_branch_axis": cosine(delta, axes["e143_branch_minus_e95"]),
            "proj_on_e143_branch_axis": projection(delta, axes["e143_branch_minus_e95"]),
            "resid_ratio_vs_e142_axis": resid_ratio(delta, axes["e142_branch_minus_e95"]),
            "resid_ratio_vs_e143_axis": resid_ratio(delta, axes["e143_branch_minus_e95"]),
        }
        rec.update(target_l1_shares(delta))
        rows.append(rec)
    return pd.DataFrame(rows)


def build_pairwise(logits: dict[str, np.ndarray]) -> pd.DataFrame:
    axes = {
        "hardtail_e95_minus_mixmin": logits["e95"] - logits["mixmin"],
        "e72_fail_minus_e95": logits["failed_e72"] - logits["e95"],
        "e101_loss_minus_e95": logits["e101"] - logits["e95"],
        "e142_branch_minus_e95": logits["e142"] - logits["e95"],
        "e143_branch_minus_e95": logits["e143"] - logits["e95"],
        "e144_branch_minus_e95": logits["e144"] - logits["e95"],
        "e144_minus_e143": logits["e144"] - logits["e143"],
        "e144_minus_e142": logits["e144"] - logits["e142"],
    }
    rows: list[dict[str, Any]] = []
    names = list(axes)
    masks = {
        "all": np.ones_like(next(iter(axes.values())), dtype=bool),
        "e144_active": np.abs(axes["e144_branch_minus_e95"]) > 1.0e-9,
        "e101_active": np.abs(axes["e101_loss_minus_e95"]) > 1.0e-9,
        "q2s3": np.broadcast_to(np.array([t in {"Q2", "S3"} for t in TARGETS]), axes["e144_branch_minus_e95"].shape),
    }
    for mask_name, mask in masks.items():
        for i, left in enumerate(names):
            for right in names[i + 1 :]:
                rows.append(
                    {
                        "mask": mask_name,
                        "left": left,
                        "right": right,
                        "cosine": cosine(axes[left], axes[right], mask),
                        "projection_left_on_right": projection(axes[left], axes[right], mask),
                        "projection_right_on_left": projection(axes[right], axes[left], mask),
                    }
                )
    return pd.DataFrame(rows)


def build_target(logits: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    base_axes = {
        "hardtail_e95_minus_mixmin": logits["e95"] - logits["mixmin"],
        "e101_loss_minus_e95": logits["e101"] - logits["e95"],
        "e72_fail_minus_e95": logits["failed_e72"] - logits["e95"],
    }
    for candidate in ["e101", "e142", "e143", "e144"]:
        delta = logits[candidate] - logits["e95"]
        for j, target in enumerate(TARGETS):
            mask = np.zeros_like(delta, dtype=bool)
            mask[:, j] = True
            rec = {
                "candidate": candidate,
                "target": target,
                "changed_cells": int((np.abs(delta[:, j]) > 1.0e-9).sum()),
                "l1_logit": float(np.abs(delta[:, j]).sum()),
                "mean_signed_logit": float(delta[:, j].mean()),
                "cos_hardtail_axis": cosine(delta, base_axes["hardtail_e95_minus_mixmin"], mask),
                "cos_e101_loss_axis": cosine(delta, base_axes["e101_loss_minus_e95"], mask),
                "cos_e72_fail_axis": cosine(delta, base_axes["e72_fail_minus_e95"], mask),
            }
            rows.append(rec)
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame, pairwise: pd.DataFrame, target: pd.DataFrame) -> None:
    live = summary[summary["name"].isin(["e85", "e86", "e89", "e90", "e101", "e142", "e143", "e144"])].copy()
    live = live.sort_values(["name"])
    e144 = summary[summary["name"].eq("e144")].iloc[0]
    e142 = summary[summary["name"].eq("e142")].iloc[0]
    e143 = summary[summary["name"].eq("e143")].iloc[0]
    anchors = summary[summary["name"].isin(["mixmin", "failed_e72", "e101", "e95", "e144"])].copy()
    selected_pairs = pairwise[
        pairwise["mask"].eq("all")
        & pairwise["left"].isin(["e144_branch_minus_e95", "e144_minus_e143", "e144_minus_e142"])
    ].sort_values(["left", "cosine"], ascending=[True, False])
    e144_target = target[target["candidate"].eq("e144")].sort_values("l1_logit", ascending=False)

    lines = [
        "# E149 E144 Anchor-Geometry Audit",
        "",
        "## Question",
        "",
        "Is E144 a new E95 successor law, or mostly a pruned E142/E143 residual branch that stays near the hardtail frontier while trying to avoid E72/E101 public-negative axes?",
        "",
        "## Anchor Geometry Summary",
        "",
        md_table(
            anchors[
                [
                    "name",
                    "public_delta_vs_e95",
                    "changed_cells_vs_e95",
                    "l1_logit_vs_e95",
                    "cos_hardtail_axis",
                    "cos_e101_loss_axis",
                    "cos_e72_fail_axis",
                    "q2s3_share",
                    "share_Q3",
                    "share_S3",
                ]
            ],
            ".9f",
        ),
        "",
        "## Live Candidate Geometry",
        "",
        md_table(
            live[
                [
                    "name",
                    "changed_cells_vs_e95",
                    "l1_logit_vs_e95",
                    "cos_e101_loss_axis",
                    "cos_e72_fail_axis",
                    "cos_e142_branch_axis",
                    "cos_e143_branch_axis",
                    "resid_ratio_vs_e142_axis",
                    "resid_ratio_vs_e143_axis",
                    "q2s3_share",
                    "share_Q3",
                    "share_S3",
                ]
            ],
            ".9f",
        ),
        "",
        "## E144 Pairwise Axis Relations",
        "",
        md_table(
            selected_pairs[
                [
                    "left",
                    "right",
                    "cosine",
                    "projection_left_on_right",
                    "projection_right_on_left",
                ]
            ].head(24),
            ".9f",
        ),
        "",
        "## E144 Target Anatomy",
        "",
        md_table(
            e144_target[
                [
                    "target",
                    "changed_cells",
                    "l1_logit",
                    "mean_signed_logit",
                    "cos_hardtail_axis",
                    "cos_e101_loss_axis",
                    "cos_e72_fail_axis",
                ]
            ],
            ".9f",
        ),
        "",
        "## Interpretation",
        "",
        f"- E144 changed cells versus E95: `{int(e144['changed_cells_vs_e95'])}`; E142 `{int(e142['changed_cells_vs_e95'])}`, E143 `{int(e143['changed_cells_vs_e95'])}`.",
        f"- E144 cosine with E142 branch axis: `{float(e144['cos_e142_branch_axis']):.9f}`; residual ratio vs E142: `{float(e144['resid_ratio_vs_e142_axis']):.9f}`.",
        f"- E144 cosine with E143 branch axis: `{float(e144['cos_e143_branch_axis']):.9f}`; residual ratio vs E143: `{float(e144['resid_ratio_vs_e143_axis']):.9f}`.",
        f"- E144 cosine with E101 public-negative axis: `{float(e144['cos_e101_loss_axis']):.9f}`; with E72 fail axis: `{float(e144['cos_e72_fail_axis']):.9f}`.",
        f"- E144 target L1 shares: Q3 `{float(e144['share_Q3']):.6f}`, S3 `{float(e144['share_S3']):.6f}`, S2 `{float(e144['share_S2']):.6f}`, Q1 `{float(e144['share_Q1']):.6f}`, S4 `{float(e144['share_S4']):.6f}`.",
        "",
        "Read: E144 should be interpreted as a branch-pruned residual sensor, not a new broad representation breakthrough. It is close to the E142/E143 branch geometry, while its public value depends on whether that small residual direction avoids the E101/E72 negative axes well enough on hidden public labels.",
        "",
        "## Decision",
        "",
        "No submission is created. E144 remains the next file. Public feedback should be read together with E145/E148 and this geometry audit: a win validates branch-pruned residual geometry; a loss requires checking whether the E142/E143 branch geometry itself failed or only the fine retained S3/Q3/S2 slices failed.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    _, probs, logits = load_predictions()
    summary = build_summary(probs, logits)
    pairwise = build_pairwise(logits)
    target = build_target(logits)
    summary.to_csv(SUMMARY_OUT, index=False)
    pairwise.to_csv(PAIR_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    write_report(summary, pairwise, target)
    print(
        {
            "summary": str(SUMMARY_OUT),
            "pairwise": str(PAIR_OUT),
            "target": str(TARGET_OUT),
            "report": str(REPORT_OUT),
        }
    )
    print(
        summary[
            summary["name"].isin(["e101", "e142", "e143", "e144"])
        ][
            [
                "name",
                "changed_cells_vs_e95",
                "cos_e101_loss_axis",
                "cos_e72_fail_axis",
                "cos_e142_branch_axis",
                "cos_e143_branch_axis",
                "resid_ratio_vs_e142_axis",
                "resid_ratio_vs_e143_axis",
                "q2s3_share",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
