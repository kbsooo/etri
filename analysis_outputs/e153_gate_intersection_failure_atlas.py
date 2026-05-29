#!/usr/bin/env python3
"""E153: why do E152 branch-orthogonal gates not intersect?

E152 showed that non-collinear decoder signal exists, but no projected row
passes relaxed structural, E72-budget, post-E101, and active-veto/actionability
gates together. This audit does not create predictions. It rebuilds the E152
projection predictions, attaches target/axis movement anatomy, and explains the
near-miss blocker classes.
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
import e152_branch_orthogonal_decoder_audit as e152  # noqa: E402


SCAN_IN = OUT / "e152_branch_orthogonal_projection_scan.csv"
SUMMARY_OUT = OUT / "e153_gate_intersection_failure_summary.csv"
CLASS_OUT = OUT / "e153_gate_intersection_failure_classes.csv"
TARGET_OUT = OUT / "e153_gate_intersection_target_contrasts.csv"
BLOCKER_OUT = OUT / "e153_gate_intersection_component_blockers.csv"
FRONTIER_OUT = OUT / "e153_gate_intersection_near_miss_frontier.csv"
REPORT_OUT = OUT / "e153_gate_intersection_failure_atlas_report.md"

BOOL_TRUE = {"true", "1", "yes"}
TARGET_IDXS = {target: idx for idx, target in enumerate(TARGETS)}
Q_TARGETS = [TARGET_IDXS[t] for t in ["Q1", "Q2", "Q3"]]
S_TARGETS = [TARGET_IDXS[t] for t in ["S1", "S2", "S3", "S4"]]
Q2S3 = [TARGET_IDXS["Q2"], TARGET_IDXS["S3"]]


def bool_col(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(False, index=frame.index)
    raw = frame[col]
    if raw.dtype == bool:
        return raw.fillna(False)
    return raw.astype(str).str.lower().isin(BOOL_TRUE)


def safe_num(frame: pd.DataFrame, col: str, default: float = np.nan) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[col], errors="coerce")


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    af = np.asarray(a, dtype=np.float64).reshape(-1)
    bf = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(af) * np.linalg.norm(bf))
    if denom <= 1.0e-15:
        return 0.0
    return float(np.dot(af, bf) / denom)


def rebuild_e152_predictions() -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray], list[np.ndarray]]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    e142_pred = e152.clip_prob(load_sub(e152.E142_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e143_pred = e152.clip_prob(load_sub(e152.E143_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    e144_pred = e152.clip_prob(load_sub(e152.E144_FILE, sample)[TARGETS].to_numpy(dtype=np.float64))
    refs["e142"] = e142_pred
    refs["e143"] = e143_pred
    refs["e144"] = e144_pred

    e95_logit = logit(refs["e95"])
    branch_axes = {
        "e142": logit(e142_pred) - e95_logit,
        "e143": logit(e143_pred) - e95_logit,
        "e144": logit(e144_pred) - e95_logit,
        "e101": logit(refs["e101"]) - e95_logit,
        "e72": logit(refs["failed_e72"]) - e95_logit,
        "mixmin": logit(refs["mixmin"]) - e95_logit,
    }

    state, density, tail_state = e152.setup_state(sample, refs)
    geo, pred_lookup = e152.source_geometry(sample, refs, state, density, tail_state, branch_axes)
    _rows, preds = e152.build_projected_candidates(geo, pred_lookup, refs, branch_axes, e144_pred)
    return sample, refs, branch_axes, preds


def target_movement_rows(scan: pd.DataFrame, refs: dict[str, np.ndarray], branch_axes: dict[str, np.ndarray], preds: list[np.ndarray]) -> pd.DataFrame:
    e95_logit = logit(refs["e95"])
    rows: list[dict[str, Any]] = []
    for pos, rec in enumerate(scan.to_dict("records")):
        pred_index = int(rec["pred_index"])
        if pred_index < 0 or pred_index >= len(preds):
            continue
        delta = logit(preds[pred_index]) - e95_logit
        abs_delta = np.abs(delta)
        total_l1 = float(abs_delta.sum())
        target_l1 = abs_delta.sum(axis=0)
        active = abs_delta > 1.0e-9
        row: dict[str, Any] = {
            "variant_pos": int(pos),
            "pred_index": pred_index,
            "delta_l1_total": total_l1,
            "changed_cells_rebuilt": int(active.sum()),
            "changed_rows_rebuilt": int(active.any(axis=1).sum()),
            "q_share": float(target_l1[Q_TARGETS].sum() / total_l1) if total_l1 > 0 else 0.0,
            "s_share": float(target_l1[S_TARGETS].sum() / total_l1) if total_l1 > 0 else 0.0,
            "q2s3_share": float(target_l1[Q2S3].sum() / total_l1) if total_l1 > 0 else 0.0,
            "max_target": TARGETS[int(np.argmax(target_l1))] if total_l1 > 0 else "",
            "cos_e144": cosine(delta, branch_axes["e144"]),
            "cos_e101": cosine(delta, branch_axes["e101"]),
            "cos_e72": cosine(delta, branch_axes["e72"]),
            "cos_mixmin": cosine(delta, branch_axes["mixmin"]),
        }
        for target, idx in TARGET_IDXS.items():
            row[f"share_{target}"] = float(target_l1[idx] / total_l1) if total_l1 > 0 else 0.0
            row[f"cells_{target}"] = int(active[:, idx].sum())
        rows.append(row)
    return pd.DataFrame(rows)


def add_gate_classes(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    out["gate_relaxed"] = bool_col(out, "relaxed_structural_tol1e12")
    out["gate_budget"] = bool_col(out, "budget_ok")
    out["gate_post101"] = bool_col(out, "post101_ok")
    out["gate_actionable"] = bool_col(out, "gate_strict_actionable")
    out["passed_gate_count"] = (
        out[["gate_relaxed", "gate_budget", "gate_post101", "gate_actionable"]].astype(int).sum(axis=1)
    )
    out["gate_class"] = "other"
    out.loc[out["gate_relaxed"] & out["gate_budget"] & out["gate_post101"] & out["gate_actionable"], "gate_class"] = "all_four"
    out.loc[out["gate_relaxed"] & out["gate_budget"] & out["gate_post101"] & ~out["gate_actionable"], "gate_class"] = "missing_actionable"
    out.loc[out["gate_budget"] & out["gate_post101"] & out["gate_actionable"] & ~out["gate_relaxed"], "gate_class"] = "missing_relaxed"
    out.loc[out["gate_relaxed"] & out["gate_post101"] & out["gate_actionable"] & ~out["gate_budget"], "gate_class"] = "missing_budget"
    out.loc[out["gate_relaxed"] & out["gate_budget"] & out["gate_actionable"] & ~out["gate_post101"], "gate_class"] = "missing_post101"

    out["fail_action_cos"] = ~bool_col(out, "gate_cos95_resid025")
    out["fail_action_active_q2s3"] = ~bool_col(out, "gate_active_q2s3_not_more_than_e101")
    out["fail_action_e72"] = ~bool_col(out, "gate_e72_not_more_than_e95")
    out["fail_action_material"] = ~bool_col(out, "gate_material_vs_e95")

    out["fail_relaxed_margin"] = ~bool_col(out, "all_margin_vs_mixmin")
    out["fail_relaxed_all_beats"] = ~bool_col(out, "all_beats_base")
    out["fail_relaxed_set_mean"] = ~bool_col(out, "all_sets_mean_beat")
    out["fail_relaxed_tail"] = ~bool_col(out, "tail_pass_tol1e12")
    out["fail_relaxed_hidden"] = safe_num(out, "hidden_core_minus_base").ge(0.0)
    out["fail_relaxed_world"] = safe_num(out, "world_support_minus_base").gt(0.0)
    out["fail_relaxed_raw"] = safe_num(out, "raw_energy_q_p90_minus_base").gt(0.0)
    return out


def class_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, g in df.groupby("gate_class", dropna=False):
        rows.append(
            {
                "gate_class": name,
                "rows": int(len(g)),
                "best_all_minus_base": float(g["all_minus_base"].min()),
                "best_post101_p95": float(safe_num(g, "post101_p95_vs_e95_e101_sensor").min()),
                "best_e72_gap": float(safe_num(g, "e72_plausible_gap_vs_e95").min()),
                "median_q_share": float(g["q_share"].median()),
                "median_s_share": float(g["s_share"].median()),
                "median_q2s3_share": float(g["q2s3_share"].median()),
                "median_share_Q3": float(g["share_Q3"].median()),
                "median_share_S3": float(g["share_S3"].median()),
                "median_cos_e144": float(g["cos_e144"].median()),
                "median_cos_e72": float(g["cos_e72"].median()),
                "median_tail_equal_cosine": float(safe_num(g, "tail_equal_law_cosine").median()),
                "median_tail_equal_resid": float(safe_num(g, "tail_equal_law_resid_ratio").median()),
            }
        )
    order = {"all_four": 0, "missing_actionable": 1, "missing_relaxed": 2, "missing_budget": 3, "missing_post101": 4}
    out = pd.DataFrame(rows)
    out["_order"] = out["gate_class"].map(order).fillna(99)
    return out.sort_values(["_order", "rows"], ascending=[True, False]).drop(columns="_order")


def component_blockers(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "fail_action_cos",
        "fail_action_active_q2s3",
        "fail_action_e72",
        "fail_action_material",
        "fail_relaxed_margin",
        "fail_relaxed_all_beats",
        "fail_relaxed_set_mean",
        "fail_relaxed_tail",
        "fail_relaxed_hidden",
        "fail_relaxed_world",
        "fail_relaxed_raw",
    ]
    rows: list[dict[str, Any]] = []
    for name, g in df.groupby("gate_class", dropna=False):
        if len(g) == 0:
            continue
        for col in cols:
            rows.append(
                {
                    "gate_class": name,
                    "component": col,
                    "fail_rate": float(g[col].mean()),
                    "fail_count": int(g[col].sum()),
                    "rows": int(len(g)),
                }
            )
    return pd.DataFrame(rows).sort_values(["gate_class", "fail_rate", "fail_count"], ascending=[True, False, False])


def target_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    share_cols = [f"share_{target}" for target in TARGETS]
    focus_classes = ["missing_actionable", "missing_relaxed", "other"]
    for gate_class in focus_classes:
        g = df[df["gate_class"].eq(gate_class)]
        if g.empty:
            continue
        rest = df[~df["gate_class"].eq(gate_class)]
        for target, col in zip(TARGETS, share_cols):
            rows.append(
                {
                    "gate_class": gate_class,
                    "target": target,
                    "rows": int(len(g)),
                    "mean_share": float(g[col].mean()),
                    "median_share": float(g[col].median()),
                    "rest_mean_share": float(rest[col].mean()) if len(rest) else np.nan,
                    "mean_lift_vs_rest": float(g[col].mean() - rest[col].mean()) if len(rest) else np.nan,
                    "top_target_rate": float((g["max_target"] == target).mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["gate_class", "mean_lift_vs_rest"], ascending=[True, False])


def family_mode_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    near = df[df["passed_gate_count"].ge(3)].copy()
    for keys, g in near.groupby(["gate_class", "source_family", "projection_mode"], dropna=False):
        gate_class, source_family, projection_mode = keys
        rows.append(
            {
                "gate_class": gate_class,
                "source_family": source_family,
                "projection_mode": projection_mode,
                "rows": int(len(g)),
                "best_all_minus_base": float(g["all_minus_base"].min()),
                "median_q2s3_share": float(g["q2s3_share"].median()),
                "median_share_Q3": float(g["share_Q3"].median()),
                "median_share_S3": float(g["share_S3"].median()),
                "median_tail_equal_resid": float(safe_num(g, "tail_equal_law_resid_ratio").median()),
                "fail_action_cos_rate": float(g["fail_action_cos"].mean()),
                "fail_relaxed_tail_rate": float(g["fail_relaxed_tail"].mean()),
                "fail_relaxed_raw_rate": float(g["fail_relaxed_raw"].mean()),
                "fail_relaxed_world_rate": float(g["fail_relaxed_world"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["gate_class", "rows", "best_all_minus_base"], ascending=[True, False, True])


def frontier(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "gate_class",
        "passed_gate_count",
        "projection_mode",
        "source_family",
        "source_tag",
        "alpha",
        "top_k",
        "all_minus_base",
        "post101_p95_vs_e95_e101_sensor",
        "e72_plausible_gap_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_resid_ratio",
        "q2s3_share",
        "share_Q3",
        "share_S3",
        "cos_e144",
        "cos_e72",
        "fail_action_cos",
        "fail_action_active_q2s3",
        "fail_relaxed_tail",
        "fail_relaxed_world",
        "fail_relaxed_raw",
        "tag",
    ]
    near = df[df["passed_gate_count"].ge(3)].copy()
    if near.empty:
        near = df.sort_values(["passed_gate_count", "all_minus_base"], ascending=[False, True]).head(80)
    return near.sort_values(["passed_gate_count", "all_minus_base"], ascending=[False, True])[[c for c in cols if c in near.columns]].head(120)


def md_table(frame: pd.DataFrame, cols: list[str], n: int = 20, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    return e152.e138.md_table(frame[[c for c in cols if c in frame.columns]].head(n), floatfmt)


def write_report(summary: pd.DataFrame, fam: pd.DataFrame, blockers: pd.DataFrame, targets: pd.DataFrame, front: pd.DataFrame) -> None:
    missing_action = summary[summary["gate_class"].eq("missing_actionable")]
    missing_relaxed = summary[summary["gate_class"].eq("missing_relaxed")]
    action_rows = int(missing_action["rows"].iloc[0]) if len(missing_action) else 0
    relaxed_rows = int(missing_relaxed["rows"].iloc[0]) if len(missing_relaxed) else 0
    lines = [
        "# E153 Gate-Intersection Failure Atlas",
        "",
        "## Question",
        "",
        "E152 found non-collinear decoder signal but zero all-four gate intersections. This audit asks which gate actually kills the near misses and whether the blockers look localized or structural.",
        "",
        "## Gate-Class Summary",
        "",
        md_table(
            summary,
            [
                "gate_class",
                "rows",
                "best_all_minus_base",
                "best_post101_p95",
                "best_e72_gap",
                "median_q_share",
                "median_s_share",
                "median_q2s3_share",
                "median_share_Q3",
                "median_share_S3",
                "median_tail_equal_cosine",
                "median_tail_equal_resid",
            ],
            20,
        ),
        "",
        "## Near-Miss Family/Mode Summary",
        "",
        md_table(
            fam,
            [
                "gate_class",
                "source_family",
                "projection_mode",
                "rows",
                "best_all_minus_base",
                "median_q2s3_share",
                "median_share_Q3",
                "median_share_S3",
                "median_tail_equal_resid",
                "fail_action_cos_rate",
                "fail_relaxed_tail_rate",
                "fail_relaxed_raw_rate",
                "fail_relaxed_world_rate",
            ],
            30,
        ),
        "",
        "## Component Blockers",
        "",
        md_table(
            blockers[blockers["gate_class"].isin(["missing_actionable", "missing_relaxed"])],
            ["gate_class", "component", "fail_rate", "fail_count", "rows"],
            40,
        ),
        "",
        "## Target Contrasts",
        "",
        md_table(
            targets[targets["gate_class"].isin(["missing_actionable", "missing_relaxed"])],
            ["gate_class", "target", "rows", "mean_share", "median_share", "mean_lift_vs_rest", "top_target_rate"],
            30,
        ),
        "",
        "## Frontier Near Misses",
        "",
        md_table(front, list(front.columns), 40),
        "",
        "## Decision",
        "",
        (
            f"No submission. The near misses split into `{action_rows}` missing-actionable rows and `{relaxed_rows}` "
            "missing-relaxed rows. This supports the E152 interpretation: the decoder failure is not a single scalar "
            "threshold that can be tuned; it is a mismatch between tail-equal/actionability geometry and relaxed "
            "structural health."
        ),
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan = pd.read_csv(SCAN_IN)
    variants = scan[scan["strategy"].eq("branch_orthogonal_projection")].copy().reset_index(drop=True)
    variants["variant_pos"] = np.arange(len(variants), dtype=int)
    _sample, refs, branch_axes, preds = rebuild_e152_predictions()
    anatomy = target_movement_rows(variants, refs, branch_axes, preds)
    merged = variants.merge(anatomy.drop(columns=["pred_index"]), on="variant_pos", how="left")
    merged = add_gate_classes(merged)

    summary = class_summary(merged)
    fam = family_mode_summary(merged)
    blockers = component_blockers(merged)
    targets = target_contrasts(merged)
    front = frontier(merged)

    summary.to_csv(SUMMARY_OUT, index=False)
    fam.to_csv(CLASS_OUT, index=False)
    blockers.to_csv(BLOCKER_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    front.to_csv(FRONTIER_OUT, index=False)
    write_report(summary, fam, blockers, targets, front)

    key = summary[summary["gate_class"].isin(["missing_actionable", "missing_relaxed"])][
        ["gate_class", "rows", "best_all_minus_base", "median_q2s3_share", "median_tail_equal_resid"]
    ]
    print(
        {
            "rows": int(len(merged)),
            "near_3of4": int((merged["passed_gate_count"] >= 3).sum()),
            "all_four": int((merged["gate_class"] == "all_four").sum()),
            "missing_actionable": int((merged["gate_class"] == "missing_actionable").sum()),
            "missing_relaxed": int((merged["gate_class"] == "missing_relaxed").sum()),
            "best_all_minus_base": float(merged["all_minus_base"].min()),
        }
    )
    print(key.to_string(index=False))


if __name__ == "__main__":
    main()
