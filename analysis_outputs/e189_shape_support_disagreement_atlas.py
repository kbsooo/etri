#!/usr/bin/env python3
"""E189: atlas of shape/support pair-decoder disagreements.

E187/E188 showed that support-heavy pair structure improves wider edge stress
but breaks the exact E95/E101 frontier boundary. This audit asks the smaller
question: what are the actual rows behind that tradeoff?

If support's gains are broad, a conditional selector may be worth building. If
the gains are just one anchor family while the harms are another anchor family,
then the support decoder is not a hidden-world selector; it is an anchor-specific
sensor.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e185_known_lb_pair_structural_decoder as e185  # noqa: E402


PRED_IN = OUT / "e187_e95_e101_boundary_miss_anatomy_predictions.csv"
Z_IN = OUT / "e186_antisymmetric_pair_decoder_zfeatures.csv"
SUMMARY_OUT = OUT / "e189_shape_support_disagreement_atlas_summary.csv"
ROW_AUDIT_OUT = OUT / "e189_shape_support_disagreement_atlas_row_audit.csv"
FEATURE_AUDIT_OUT = OUT / "e189_shape_support_disagreement_atlas_feature_audit.csv"
GATE_SUMMARY_OUT = OUT / "e189_shape_support_disagreement_atlas_gate_summary.csv"
REPORT_OUT = OUT / "e189_shape_support_disagreement_atlas_report.md"

EPS = 1.0e-12
SHAPE = "shape_only"
PRIMARY_SUPPORT = "shape_support"
SUPPORT_VARIANTS = (
    "shape_support",
    "shape_support_public_axis",
    "shape_support_drop_global",
    "shape_support_drop_subject",
    "shape_support_drop_nearest",
    "shape_support_drop_focus",
    "shape_support_drop_flank",
    "shape_support_drop_visible",
    "shape_support_drop_prior_split",
    "shape_support_drop_top1",
    "shape_support_drop_top16_33",
    "shape_support_drop_between",
    "shape_support_keep_mean_only",
    "shape_support_keep_hard_only",
    "shape_support_no_q2s3_targets",
)
E72 = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E95 = "submission_e95_hardtail_541e3973.csv"
E101 = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN = "submission_mixmin_0c916bb4.csv"


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered = view.copy()
    for col in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[col]):
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
        else:
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(rendered.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(rendered.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in rendered.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def file_tag(file_name: str) -> str:
    name = file_name.lower()
    if file_name == E95:
        return "e95"
    if file_name == E101:
        return "e101"
    if file_name == E72:
        return "e72"
    if file_name == MIXMIN:
        return "mixmin"
    if "frontier_cvjepa" in name:
        return "a2c8_frontier"
    if "raw_timeline" in name:
        return "raw_jepa"
    if "lejepa" in name:
        return "bad_lejepa"
    if "ordinal" in name:
        return "ordinal"
    if "hybrid_0p578" in name:
        return "hybrid_final9"
    if "hybrid_0p567" in name:
        return "hybrid_stage2"
    if "jepa_latent" in name:
        return "jepa_latent"
    return "other"


def pair_context(row: pd.Series) -> str:
    tags = sorted([file_tag(str(row["new_file"])), file_tag(str(row["base_file"]))])
    return "__".join(tags)


def add_pair_flags(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["new_tag"] = out["new_file"].map(file_tag)
    out["base_tag"] = out["base_file"].map(file_tag)
    out["pair_context"] = out.apply(pair_context, axis=1)
    out["pair_has_e72"] = out["new_file"].eq(E72) | out["base_file"].eq(E72)
    out["pair_has_e95"] = out["new_file"].eq(E95) | out["base_file"].eq(E95)
    out["pair_has_e101"] = out["new_file"].eq(E101) | out["base_file"].eq(E101)
    out["pair_has_mixmin"] = out["new_file"].eq(MIXMIN) | out["base_file"].eq(MIXMIN)
    out["pair_is_e95_e101"] = (
        (out["new_file"].eq(E95) & out["base_file"].eq(E101))
        | (out["new_file"].eq(E101) & out["base_file"].eq(E95))
    )
    out["pair_is_e72_frontier_neighbor"] = out["pair_has_e72"] & (
        out["pair_has_e95"] | out["pair_has_e101"] | out["pair_has_mixmin"]
    )
    return out


def z_family(col: str) -> str:
    if col.startswith("z__shape_"):
        return "shape"
    if col.startswith("z__target_"):
        return "target"
    if col.startswith("z__ctx_"):
        return "context"
    if col.startswith("z__axis_"):
        return "axis"
    if col.startswith("z__sup_"):
        return "support"
    return "other"


def z_aggregates() -> pd.DataFrame:
    z = pd.read_csv(Z_IN)
    keys = ["pair_id", "new_file", "base_file"]
    out = z[keys].copy()
    for family in ("shape", "target", "context", "axis", "support"):
        cols = [c for c in z.columns if z_family(c) == family]
        if not cols:
            continue
        out[f"{family}_signed_mean"] = z[cols].mean(axis=1)
        out[f"{family}_abs_sum"] = z[cols].abs().sum(axis=1)
    for token in ("e72_active", "e101_active", "all_veto_null", "safe_density", "broad_low_alpha"):
        cols = [c for c in z.columns if c.startswith("z__axis_") and token in c]
        if cols:
            out[f"axis_{token}_abs_sum"] = z[cols].abs().sum(axis=1)
            out[f"axis_{token}_signed_mean"] = z[cols].mean(axis=1)
    return out


def merged_predictions() -> pd.DataFrame:
    pred = pd.read_csv(PRED_IN)
    file_pred = pred[pred["group_col"].eq("file")].copy()
    keys = ["heldout", "pair_id", "new_file", "base_file"]
    keep_cols = keys + [
        "actual_delta",
        "abs_actual_delta",
        "actual_new_better",
        "frontier_pair",
        "micro_pair",
        "e95_edge_pair",
        "e95_e101_pair",
        "prob_new_better",
        "correct",
    ]
    shape = file_pred[file_pred["variant"].eq(SHAPE)][keep_cols].rename(
        columns={"prob_new_better": "p_shape", "correct": "shape_correct"}
    )
    scores = e185.load_known_scores().set_index("file")["public_lb"].to_dict()
    rows: list[pd.DataFrame] = []
    for support_variant in SUPPORT_VARIANTS:
        support = file_pred[file_pred["variant"].eq(support_variant)][keys + ["prob_new_better", "correct"]].rename(
            columns={"prob_new_better": "p_support", "correct": "support_correct"}
        )
        merged = shape.merge(support, on=keys)
        merged.insert(0, "support_variant", support_variant)
        merged["disagreement_class"] = "both_correct"
        merged.loc[~merged["shape_correct"] & ~merged["support_correct"], "disagreement_class"] = "both_wrong"
        merged.loc[merged["shape_correct"] & ~merged["support_correct"], "disagreement_class"] = "shape_only_win"
        merged.loc[~merged["shape_correct"] & merged["support_correct"], "disagreement_class"] = "support_rescue"
        merged["p_support_minus_shape"] = merged["p_support"] - merged["p_shape"]
        merged["new_public_lb"] = merged["new_file"].map(scores)
        merged["base_public_lb"] = merged["base_file"].map(scores)
        merged["heldout_public_lb"] = merged["heldout"].map(scores)
        merged["abs_public_delta"] = (merged["new_public_lb"] - merged["base_public_lb"]).abs()
        rows.append(add_pair_flags(merged))
    out = pd.concat(rows, ignore_index=True)
    zagg = z_aggregates()
    out = out.merge(zagg, on=["pair_id", "new_file", "base_file"], how="left")
    return out


def summarize(rows: pd.DataFrame) -> pd.DataFrame:
    summary_rows: list[dict[str, Any]] = []
    for (variant, flag_name), part in flagged_parts(rows):
        counts = part["disagreement_class"].value_counts()
        rec: dict[str, Any] = {
            "support_variant": variant,
            "slice": flag_name,
            "n_rows": int(len(part)),
            "shape_accuracy": float(part["shape_correct"].mean()) if len(part) else np.nan,
            "support_accuracy": float(part["support_correct"].mean()) if len(part) else np.nan,
            "both_correct": int(counts.get("both_correct", 0)),
            "support_rescue": int(counts.get("support_rescue", 0)),
            "shape_only_win": int(counts.get("shape_only_win", 0)),
            "both_wrong": int(counts.get("both_wrong", 0)),
            "support_rescue_rate": float((part["disagreement_class"].eq("support_rescue")).mean())
            if len(part)
            else np.nan,
            "shape_only_win_rate": float((part["disagreement_class"].eq("shape_only_win")).mean())
            if len(part)
            else np.nan,
            "e72_neighbor_share": float(part["pair_is_e72_frontier_neighbor"].mean()) if len(part) else np.nan,
            "exact_e95_e101_share": float(part["pair_is_e95_e101"].mean()) if len(part) else np.nan,
        }
        summary_rows.append(rec)
    return pd.DataFrame(summary_rows)


def flagged_parts(rows: pd.DataFrame):
    flags: list[tuple[str, pd.Series]] = [
        ("all", pd.Series(True, index=rows.index)),
        ("frontier", rows["frontier_pair"].astype(bool)),
        ("micro", rows["micro_pair"].astype(bool)),
        ("e95_edge", rows["e95_edge_pair"].astype(bool)),
        ("exact_e95_e101", rows["pair_is_e95_e101"].astype(bool)),
        ("e72_frontier_neighbor", rows["pair_is_e72_frontier_neighbor"].astype(bool)),
    ]
    for variant, vpart in rows.groupby("support_variant"):
        for name, mask in flags:
            part = vpart.loc[mask.loc[vpart.index]].copy()
            yield (variant, name), part


def metric_dict(part: pd.DataFrame, p: np.ndarray, name: str, support_variant: str, gate: str) -> dict[str, Any]:
    y = part["actual_new_better"].to_numpy(dtype=int)
    rec: dict[str, Any] = {
        "support_variant": support_variant,
        "gate": gate,
        "slice": name,
        "n_rows": int(len(part)),
        "accuracy": float(np.mean((p >= 0.5) == y)) if len(part) else np.nan,
        "auc": safe_auc(y, p) if len(part) else np.nan,
        "logloss": float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1])) if len(part) else np.nan,
        "support_use_rate": np.nan,
    }
    return rec


def gate_scores(rows: pd.DataFrame) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for variant, part in rows.groupby("support_variant"):
        gates = {
            "shape_only": part["p_shape"].to_numpy(dtype=np.float64),
            "support_only": part["p_support"].to_numpy(dtype=np.float64),
            "support_with_exact_e95e101_veto": np.where(
                part["pair_is_e95_e101"], part["p_shape"], part["p_support"]
            ),
            "support_only_on_e72_frontier_neighbors": np.where(
                part["pair_is_e72_frontier_neighbor"], part["p_support"], part["p_shape"]
            ),
            "support_on_e72_or_shape_exact": np.where(
                part["pair_is_e72_frontier_neighbor"], part["p_support"], part["p_shape"]
            ),
        }
        for gate, p_all in gates.items():
            for name, mask in [
                ("all", pd.Series(True, index=part.index)),
                ("frontier", part["frontier_pair"].astype(bool)),
                ("micro", part["micro_pair"].astype(bool)),
                ("e95_edge", part["e95_edge_pair"].astype(bool)),
                ("exact_e95_e101", part["pair_is_e95_e101"].astype(bool)),
                ("e72_frontier_neighbor", part["pair_is_e72_frontier_neighbor"].astype(bool)),
            ]:
                sub = part.loc[mask].copy()
                if sub.empty:
                    continue
                p = pd.Series(p_all, index=part.index).loc[sub.index].to_numpy(dtype=np.float64)
                rec = metric_dict(sub, p, name, variant, gate)
                if gate in ("support_only",):
                    rec["support_use_rate"] = 1.0
                elif gate == "shape_only":
                    rec["support_use_rate"] = 0.0
                elif gate == "support_with_exact_e95e101_veto":
                    rec["support_use_rate"] = float((~sub["pair_is_e95_e101"]).mean())
                else:
                    rec["support_use_rate"] = float(sub["pair_is_e72_frontier_neighbor"].mean())
                out.append(rec)
    return pd.DataFrame(out)


def feature_audit(rows: pd.DataFrame) -> pd.DataFrame:
    primary = rows[(rows["support_variant"].eq(PRIMARY_SUPPORT)) & rows["e95_edge_pair"]].copy()
    left = primary[primary["disagreement_class"].eq("support_rescue")]
    right = primary[primary["disagreement_class"].eq("shape_only_win")]
    z = pd.read_csv(Z_IN)
    z = z[["pair_id", "new_file", "base_file"] + [c for c in z.columns if c.startswith("z__")]]
    merged = primary[["pair_id", "new_file", "base_file", "actual_new_better", "disagreement_class"]].merge(
        z, on=["pair_id", "new_file", "base_file"], how="left"
    )
    zcols = [c for c in merged.columns if c.startswith("z__")]
    rows_out: list[dict[str, Any]] = []
    if left.empty or right.empty:
        return pd.DataFrame()
    for col in zcols:
        rescue_mask = merged["disagreement_class"].eq("support_rescue")
        shape_mask = merged["disagreement_class"].eq("shape_only_win")
        rescue = merged.loc[rescue_mask, col].astype(float)
        shape_win = merged.loc[shape_mask, col].astype(float)
        rescue_sign = np.where(merged.loc[rescue_mask, "actual_new_better"].astype(int).to_numpy() == 1, 1.0, -1.0)
        shape_sign = np.where(merged.loc[shape_mask, "actual_new_better"].astype(int).to_numpy() == 1, 1.0, -1.0)
        rescue_aligned = rescue.to_numpy(dtype=np.float64) * rescue_sign
        shape_aligned = shape_win.to_numpy(dtype=np.float64) * shape_sign
        rows_out.append(
            {
                "feature": col,
                "family": z_family(col),
                "support_rescue_abs_mean": float(rescue.abs().mean()),
                "shape_only_win_abs_mean": float(shape_win.abs().mean()),
                "abs_mean_diff_rescue_minus_shapewin": float(rescue.abs().mean() - shape_win.abs().mean()),
                "support_rescue_aligned_mean": float(np.mean(rescue_aligned)),
                "shape_only_win_aligned_mean": float(np.mean(shape_aligned)),
                "aligned_mean_diff_rescue_minus_shapewin": float(
                    np.mean(rescue_aligned) - np.mean(shape_aligned)
                ),
                "sort_abs_diff": float(
                    max(
                        abs(rescue.abs().mean() - shape_win.abs().mean()),
                        abs(np.mean(rescue_aligned) - np.mean(shape_aligned)),
                    )
                ),
            }
        )
    return pd.DataFrame(rows_out).sort_values("sort_abs_diff", ascending=False)


def write_report(rows: pd.DataFrame, summary: pd.DataFrame, gate: pd.DataFrame, features: pd.DataFrame) -> None:
    primary = rows[rows["support_variant"].eq(PRIMARY_SUPPORT)].copy()
    edge = primary[primary["e95_edge_pair"]].copy()
    edge_disagree = edge[edge["disagreement_class"].isin(["support_rescue", "shape_only_win"])].copy()
    support_rescue = edge_disagree[edge_disagree["disagreement_class"].eq("support_rescue")]
    shape_win = edge_disagree[edge_disagree["disagreement_class"].eq("shape_only_win")]
    gate_focus = gate[
        gate["support_variant"].eq(PRIMARY_SUPPORT)
        & gate["slice"].isin(["all", "frontier", "micro", "e95_edge", "exact_e95_e101", "e72_frontier_neighbor"])
    ].sort_values(["slice", "accuracy", "logloss"], ascending=[True, False, True])
    summary_focus = summary[
        summary["support_variant"].isin([PRIMARY_SUPPORT, "shape_support_drop_subject", "shape_support_keep_hard_only"])
    ].sort_values(["support_variant", "slice"])

    edge_rescue_e72_rate = float(support_rescue["pair_is_e72_frontier_neighbor"].mean()) if not support_rescue.empty else np.nan
    edge_shape_exact_rate = float(shape_win["pair_is_e95_e101"].mean()) if not shape_win.empty else np.nan
    one_liner = (
        f"In the primary file-LOO E95-edge slice, support rescues `{len(support_rescue)}` rows and "
        f"shape-only wins `{len(shape_win)}` rows; support rescues are E72-frontier-neighbor rows at rate "
        f"`{edge_rescue_e72_rate:.3f}`, while shape-only wins are exact E95/E101 rows at rate "
        f"`{edge_shape_exact_rate:.3f}`."
    )

    cols_summary = [
        "support_variant",
        "slice",
        "n_rows",
        "shape_accuracy",
        "support_accuracy",
        "both_correct",
        "support_rescue",
        "shape_only_win",
        "both_wrong",
        "e72_neighbor_share",
        "exact_e95_e101_share",
    ]
    cols_rows = [
        "disagreement_class",
        "heldout",
        "new_tag",
        "base_tag",
        "actual_delta",
        "p_shape",
        "p_support",
        "pair_context",
        "pair_is_e72_frontier_neighbor",
        "pair_is_e95_e101",
    ]
    cols_gate = [
        "support_variant",
        "gate",
        "slice",
        "n_rows",
        "accuracy",
        "auc",
        "logloss",
        "support_use_rate",
    ]
    cols_feature = [
        "feature",
        "family",
        "support_rescue_abs_mean",
        "shape_only_win_abs_mean",
        "abs_mean_diff_rescue_minus_shapewin",
        "support_rescue_aligned_mean",
        "shape_only_win_aligned_mean",
        "aligned_mean_diff_rescue_minus_shapewin",
    ]
    report = f"""# E189 Shape/Support Disagreement Atlas

## Question

E187/E188 showed that support-heavy known-LB pair geometry helps wider edge
stress but breaks the exact E95/E101 boundary. Are support's wins broad, or are
they just one anchor family?

## Result In One Sentence

{one_liner}

## Primary Edge-Band Disagreements

{md(edge_disagree.sort_values(["disagreement_class", "actual_delta"]), cols_rows, n=80)}

## Disagreement Summary

{md(summary_focus, cols_summary, n=80)}

## Gate Scores

{md(gate_focus, cols_gate, n=120)}

## Structural Feature Differences

{md(features.head(40), cols_feature, n=40)}

## Interpretation

- Support's primary E95-edge gain is an E72-neighbor correction, not a general
  frontier law.
- Shape-only's primary E95-edge advantage is the exact E95/E101 hardtail
  boundary.
- A file-identity gate can make known-pair E95-edge stress look perfect, but
  that is not deployable to live pressure branches because the live branch does
  not come with an E72/E95/E101 filename.
- The useful world model is now anchor-specific: E72-contamination and
  E95/E101 hardtail boundary are different hidden sensors.

## Decision

No submission is created. Support-heavy pair structure can be used only as an
E72-adjacency diagnostic or as auxiliary evidence. It should not rank E176,
E154, or E144 without a new structural target that separates E72-contamination
from tight hardtail frontier boundaries.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def run() -> None:
    rows = merged_predictions()
    summary = summarize(rows)
    gate = gate_scores(rows)
    features = feature_audit(rows)
    rows.to_csv(ROW_AUDIT_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    gate.to_csv(GATE_SUMMARY_OUT, index=False)
    features.to_csv(FEATURE_AUDIT_OUT, index=False)
    write_report(rows, summary, gate, features)
    print(ROW_AUDIT_OUT)
    print(SUMMARY_OUT)
    print(GATE_SUMMARY_OUT)
    print(FEATURE_AUDIT_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
