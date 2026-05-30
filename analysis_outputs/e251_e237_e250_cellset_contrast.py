#!/usr/bin/env python3
"""E251: contrast E237 and E250 Q3 decisive-cell sets.

E250 survived as a feature-NN1-context decisive-cell sensor, but it may be only
an E237 sibling. This script asks a smaller question before any public feedback:
are E237 and E250 selecting the same Q3 tail, or does feature-NN1 context add a
different cell set that survives materialization stress?

No public LB is used and no new submission is created.
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
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e237_cell_decisive_jepa_target as e237  # noqa: E402


E237_FILE = (
    "submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_"
    "risk_q0p10_drop_q3_top25_426424f2.csv"
)
E250_FILE = (
    "submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_"
    "row5_risk_q0p10_drop_q3_top21_4e9a88af.csv"
)

SUMMARY_OUT = OUT / "e251_e237_e250_cellset_contrast_summary.csv"
TARGET_OUT = OUT / "e251_e237_e250_cellset_contrast_targets.csv"
OVERLAP_OUT = OUT / "e251_e237_e250_cellset_contrast_overlap.csv"
REPORT_OUT = OUT / "e251_e237_e250_cellset_contrast_report.md"

Q3_IDX = TARGETS.index("Q3")
EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in frame.columns if cols is None or c in cols]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def q3_drop_rows(pred: np.ndarray, e224: np.ndarray) -> set[int]:
    diff = np.abs(logit(pred)[:, Q3_IDX] - logit(e224)[:, Q3_IDX])
    return set(np.where(diff > 1.0e-9)[0].astype(int).tolist())


def build_pred_from_rows(e224: np.ndarray, e154: np.ndarray, rows: set[int]) -> np.ndarray:
    pred = e224.copy()
    if rows:
        idx = np.array(sorted(rows), dtype=int)
        pred[idx, Q3_IDX] = e154[idx, Q3_IDX]
    return clip_prob(pred)


def target_metric(targets: pd.DataFrame, candidate_id: str, pair_kind: str, target: str, col: str) -> float:
    part = targets[
        targets["candidate_id"].eq(candidate_id)
        & targets["pair_kind"].eq(pair_kind)
        & targets["target"].eq(target)
    ]
    if part.empty or col not in part.columns:
        return float("nan")
    return float(part[col].iloc[0])


def audit_candidate(
    candidate_id: str,
    rows: set[int],
    pred: np.ndarray,
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e154: np.ndarray,
    e95: np.ndarray,
    base_rec: dict[str, Any],
    base_targets: pd.DataFrame,
    base_actual_rec: dict[str, Any],
    base_q3_top: float,
    base_q3_adverse: float,
    base_s4_expected: float,
    row_meta: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[pd.DataFrame]]:
    spec = e222.Candidate(
        candidate_id=candidate_id,
        file_name=candidate_id,
        anchor_file=e237.E154_FILE,
        family="e251_e237_e250_cellset",
        status="generated",
        note="Q3 rollback cell-set contrast built from E237/E250 selected cells.",
    )
    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for pair_kind, base_name, base in [
        ("graft_vs_e154", e237.E154_FILE, e154),
        ("actual_vs_e95", e237.E95_FILE, e95),
    ]:
        rec, targets, _ = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
        rec.update(row_meta)
        rec["q3_dropped_cells"] = int(len(rows))
        rec["s4_dropped_cells"] = 0
        rec["baseline_expected_focus"] = float(base_rec["expected_focus"])
        rec["baseline_adverse_delta"] = float(base_rec["adverse_delta"])
        rec["baseline_support_prob_focus_swing_weighted"] = float(base_rec["support_prob_focus_swing_weighted"])
        rec["expected_loss_vs_e224"] = float(rec["expected_focus"] - base_rec["expected_focus"])
        rec["adverse_reduction_vs_e224"] = float(base_rec["adverse_delta"] - rec["adverse_delta"])
        rec["support_gain_vs_e224"] = float(
            rec["support_prob_focus_swing_weighted"] - base_rec["support_prob_focus_swing_weighted"]
        )
        if pair_kind == "actual_vs_e95":
            rec["actual_expected_delta_vs_e224"] = float(rec["expected_focus"] - base_actual_rec["expected_focus"])
            rec["actual_adverse_reduction_vs_e224"] = float(base_actual_rec["adverse_delta"] - rec["adverse_delta"])
            rec["actual_support_gain_vs_e224"] = float(
                rec["support_prob_focus_swing_weighted"]
                - base_actual_rec["support_prob_focus_swing_weighted"]
            )
        summary_rows.append(rec)
        if not targets.empty:
            targets = targets.copy()
            targets["q3_dropped_cells"] = int(len(rows))
            target_parts.append(targets)

    joined_targets = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    q3_top = target_metric(joined_targets, candidate_id, "graft_vs_e154", "Q3", "top1_over_abs_expected")
    q3_adverse = target_metric(joined_targets, candidate_id, "graft_vs_e154", "Q3", "adverse_delta")
    q3_expected = target_metric(joined_targets, candidate_id, "graft_vs_e154", "Q3", "expected_focus")
    s4_expected = target_metric(joined_targets, candidate_id, "graft_vs_e154", "S4", "expected_focus")
    actual = [r for r in summary_rows if r["pair_kind"] == "actual_vs_e95"][0]
    for rec in summary_rows:
        rec["q3_top1_over_abs_expected"] = q3_top
        rec["q3_adverse_delta"] = q3_adverse
        rec["q3_expected_focus"] = q3_expected
        rec["s4_expected_focus"] = s4_expected
        rec["actual_expected_delta_vs_e224"] = actual["actual_expected_delta_vs_e224"]
        rec["actual_adverse_reduction_vs_e224"] = actual["actual_adverse_reduction_vs_e224"]
        rec["actual_support_gain_vs_e224"] = actual["actual_support_gain_vs_e224"]
        rec["materialization_gate"] = bool(
            rec["pair_kind"] == "graft_vs_e154"
            and rec["expected_loss_vs_e224"] <= 0.000080
            and rec["adverse_reduction_vs_e224"] >= 0.000150
            and rec["support_gain_vs_e224"] > 0.0
            and q3_top <= min(base_q3_top, 0.875120489)
            and q3_adverse <= base_q3_adverse
            and s4_expected <= base_s4_expected + 0.000080
            and actual["actual_expected_delta_vs_e224"] <= 0.000020
            and actual["actual_adverse_reduction_vs_e224"] >= 0.000150
            and actual["actual_support_gain_vs_e224"] > 0.0
        )
        rec["e237_like_score_no_oof"] = (
            -float(rec["expected_loss_vs_e224"]) * 140.0
            + float(rec["adverse_reduction_vs_e224"]) * 100.0
            + float(rec["support_gain_vs_e224"]) * 0.08
            - max(float(q3_top) - base_q3_top, 0.0) * 0.04
        )
    return summary_rows, target_parts


def row_overlap(name: str, rows: set[int], e237_rows: set[int], e250_rows: set[int]) -> dict[str, Any]:
    inter_237 = rows & e237_rows
    inter_250 = rows & e250_rows
    return {
        "candidate_id": name,
        "q3_rows": len(rows),
        "overlap_e237": len(inter_237),
        "overlap_e250": len(inter_250),
        "jaccard_e237": len(inter_237) / max(len(rows | e237_rows), 1),
        "jaccard_e250": len(inter_250) / max(len(rows | e250_rows), 1),
        "e237_only_cells_in_candidate": len(rows & (e237_rows - e250_rows)),
        "e250_only_cells_in_candidate": len(rows & (e250_rows - e237_rows)),
        "shared_cells_in_candidate": len(rows & e237_rows & e250_rows),
    }


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = e230.load_prob(e237.E95_FILE, sample)
    e154 = e230.load_prob(e237.E154_FILE, sample)
    e224 = e230.load_prob(e237.E224_FILE, sample)
    e237_pred = load_prob(E237_FILE, sample)
    e250_pred = load_prob(E250_FILE, sample)

    e237_rows = q3_drop_rows(e237_pred, e224)
    e250_rows = q3_drop_rows(e250_pred, e224)
    shared = e237_rows & e250_rows
    e237_only = e237_rows - e250_rows
    e250_only = e250_rows - e237_rows
    union = e237_rows | e250_rows
    symdiff = e237_rows ^ e250_rows

    base_rec, base_targets, base_actual_rec, _ = e237.e224_baseline(sample, priors, e95, e154, e224)
    base_q3_top = target_metric(base_targets, "e224_original", "graft_vs_e154", "Q3", "top1_over_abs_expected")
    base_q3_adverse = target_metric(base_targets, "e224_original", "graft_vs_e154", "Q3", "adverse_delta")
    base_s4_expected = target_metric(base_targets, "e224_original", "graft_vs_e154", "S4", "expected_focus")

    candidates = [
        ("e237_top25", e237_rows, "known_e237"),
        ("e250_top21", e250_rows, "known_e250"),
        ("shared_intersection", shared, "overlap"),
        ("union_e237_e250", union, "union"),
        ("e237_only", e237_only, "difference"),
        ("e250_only", e250_only, "difference"),
        ("symmetric_difference", symdiff, "difference"),
    ]

    selected_map = {}
    for path in [
        OUT / "e237_cell_decisive_jepa_target_selected.csv",
        OUT / "e250_feature_nn1_decisive_materialization_selected_summary.csv",
    ]:
        if path.exists():
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                selected_map[str(row.get("submission_file", ""))] = row.to_dict()

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    overlap_rows: list[dict[str, Any]] = []
    for name, rows, source in candidates:
        pred = e237_pred if name == "e237_top25" else e250_pred if name == "e250_top21" else build_pred_from_rows(e224, e154, rows)
        source_file = E237_FILE if name == "e237_top25" else E250_FILE if name == "e250_top21" else ""
        selected = selected_map.get(source_file, {})
        row_meta = {
            "source_type": source,
            "source_file": source_file,
            "known_oof_loss_vs_full": selected.get("oof_loss_vs_full", np.nan),
            "known_oof_tail_auc": selected.get("oof_tail_auc", np.nan),
            **row_overlap(name, rows, e237_rows, e250_rows),
        }
        rows_out, targets_out = audit_candidate(
            name,
            rows,
            pred,
            sample,
            priors,
            e154,
            e95,
            base_rec,
            base_targets,
            base_actual_rec,
            base_q3_top,
            base_q3_adverse,
            base_s4_expected,
            row_meta,
        )
        summary_rows.extend(rows_out)
        target_parts.extend(targets_out)
        overlap_rows.append(row_overlap(name, rows, e237_rows, e250_rows))

    summary = pd.DataFrame(summary_rows).sort_values(
        ["pair_kind", "materialization_gate", "e237_like_score_no_oof"],
        ascending=[True, False, False],
    )
    targets = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    overlap = pd.DataFrame(overlap_rows).sort_values("q3_rows", ascending=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    overlap.to_csv(OVERLAP_OUT, index=False)

    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].copy()
    gate = graft[graft["materialization_gate"].astype(bool)].sort_values("e237_like_score_no_oof", ascending=False)
    cols = [
        "candidate_id",
        "source_type",
        "q3_rows",
        "overlap_e237",
        "overlap_e250",
        "shared_cells_in_candidate",
        "known_oof_loss_vs_full",
        "known_oof_tail_auc",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "materialization_gate",
        "e237_like_score_no_oof",
    ]
    lines = [
        "# E251 E237/E250 Cell-Set Contrast",
        "",
        "## Question",
        "",
        "Is E250 a feature-NN1-context variant that adds useful Q3 cells beyond E237, or mostly a sibling of the same learned Q3 tail?",
        "",
        "## Headline",
        "",
        f"- E237 Q3 cells: `{len(e237_rows)}`.",
        f"- E250 Q3 cells: `{len(e250_rows)}`.",
        f"- shared cells: `{len(shared)}`.",
        f"- E237-only cells: `{len(e237_only)}`.",
        f"- E250-only cells: `{len(e250_only)}`.",
        f"- union cells: `{len(union)}`.",
        f"- materialization gate passes: `{len(gate)}` of `{len(graft)}` graft rows.",
        "",
        "## Gate-Passing Cell Sets",
        "",
        md_table(gate, cols, n=20),
        "",
        "## All Graft Rows",
        "",
        md_table(graft.sort_values("e237_like_score_no_oof", ascending=False), cols, n=20),
        "",
        "## Overlap",
        "",
        md_table(overlap, None, n=20),
        "",
        "## Decision",
        "",
    ]
    if "union_e237_e250" in set(gate["candidate_id"]):
        lines.append("- The union survives materialization, so E237/E250 may be complementary. This is still not submission-ready without an OOF analogue for the union.")
    elif "e250_only" in set(gate["candidate_id"]):
        lines.append("- E250-only cells survive materialization, so feature-NN1 context adds a separable Q3 tail. Next step is an OOF analogue for those cells.")
    else:
        lines.append("- E250 does not yet prove an independently deployable cell set. Keep E250 as a public sensor, not a replacement or union candidate.")
    lines.append("- Public LB is not used and no new submission is created.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("[E251 cell overlap]")
    print(overlap.to_string(index=False))
    print("\n[E251 graft top]")
    print(graft.sort_values("e237_like_score_no_oof", ascending=False)[cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
