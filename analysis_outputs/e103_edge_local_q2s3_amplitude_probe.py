#!/usr/bin/env python3
"""E103 edge-local Q2/S3 amplitude probe.

E102 rejected the strong hypothesis that E101's 50 active Q2/S3 cells are a
hidden subject/block-local selector. The remaining signal is weaker and more
specific: those cells are unusually close to hidden-block edges.

This probe asks whether that edge-local geometry is strong enough to improve on
E101 locally, or whether it should remain only a post-E101 diagnostic.

No public labels are fitted. The stress frame is inherited from E101:
local combo/world/block checks plus E99's E95-conditioned tail-transfer worlds.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402


CELLS_IN = OUT / "e102_e101_active_cell_structure_audit_cells.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
SCAN_OUT = OUT / "e103_edge_local_q2s3_amplitude_probe_scan.csv"
SUMMARY_OUT = OUT / "e103_edge_local_q2s3_amplitude_probe_summary.csv"
TRANSFER_OUT = OUT / "e103_edge_local_q2s3_amplitude_probe_transfer.csv"
REPORT_OUT = OUT / "e103_edge_local_q2s3_amplitude_probe_report.md"
SUBMISSION_PREFIX = "submission_e103_edgeq2s3"

EPS = 1.0e-6
Q2S3_NAMES = ["Q2", "S3"]
ALPHAS = [0.125, 0.25, 0.375, 0.50, 0.75, 1.00]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
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


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e103_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": tag, **rec})


def cells_to_mask(cells: pd.DataFrame, use: pd.Series, n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    for rec in cells[use].to_dict("records"):
        mask[int(rec["sub_idx"]), TARGETS.index(str(rec["target"]))] = True
    return mask


def top_gap_mask(cells: pd.DataFrame, base: pd.Series, n_rows: int, k: int, name: str) -> tuple[str, np.ndarray]:
    ranked = cells[base].sort_values("abs_logit_gap_e95_minus_mixmin", ascending=False)
    use = cells.index.isin(ranked.head(k).index)
    return name, cells_to_mask(cells, pd.Series(use, index=cells.index), n_rows)


def build_selectors(cells: pd.DataFrame, n_rows: int) -> list[tuple[str, np.ndarray]]:
    target = cells["target"].isin(Q2S3_NAMES)
    active = target & cells["active_e95_vs_mixmin"].astype(bool)
    edge = target & (cells["edge_distance"].astype(float) <= 1.0)
    interior = target & (cells["edge_distance"].astype(float) > 1.0)
    s3 = cells["target"].eq("S3")
    q2 = cells["target"].eq("Q2")

    specs: list[tuple[str, pd.Series]] = [
        ("active_all", active),
        ("active_edge", active & edge),
        ("active_interior", active & interior),
        ("active_s3_all", active & s3),
        ("active_s3_edge", active & s3 & edge),
        ("active_s3_interior", active & s3 & interior),
        ("active_q2_all", active & q2),
        ("active_q2_edge", active & q2 & edge),
        ("edge_all", edge),
        ("edge_s3_all", edge & s3),
        ("edge_q2_all", edge & q2),
        ("interior_all", interior),
        ("interior_s3_all", interior & s3),
        ("edge_or_active", edge | active),
    ]

    selectors = [(name, cells_to_mask(cells, use, n_rows)) for name, use in specs]
    for k in [10, 20, 30, 40, 50, 75, 100]:
        selectors.append(top_gap_mask(cells, edge, n_rows, k, f"edge_topgap{k}"))
        selectors.append(top_gap_mask(cells, edge & s3, n_rows, k, f"edge_s3_topgap{k}"))
        selectors.append(top_gap_mask(cells, active, n_rows, k, f"active_topgap{k}"))

    dedup: dict[bytes, tuple[str, np.ndarray]] = {}
    for name, mask in selectors:
        if not mask.any():
            continue
        dedup.setdefault(mask.tobytes(), (name, mask))
    return list(dedup.values())


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    refs = e101.build_refs(sample)
    refs["e101"] = e101.load_pred(E101_FILE, sample)
    tail_state = e101.e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    cells = pd.read_csv(CELLS_IN)
    selectors = build_selectors(cells, len(sample))

    e95_logit = logit(refs["e95"])
    mixmin_logit = logit(refs["mixmin"])
    rollback = mixmin_logit - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for name in ["mixmin", "e95", "e101", "e89", "e85", "e86", "e90"]:
        add_pred(rows, preds, seen, refs[name], {"strategy": "control", "source": name})

    for selector_name, selector_mask in selectors:
        effective_mask = selector_mask & (np.abs(rollback) > 1.0e-12)
        move_cells = int(effective_mask.sum())
        if move_cells == 0:
            continue
        targets = [TARGETS[j] for j in np.where(effective_mask.any(axis=0))[0]]
        selected_rows = int(np.any(effective_mask, axis=1).sum())
        edge_cells = int(
            cells_to_mask(cells, cells["edge_distance"].astype(float).le(1.0), len(sample))[effective_mask].sum()
        )
        s3_cells = int(effective_mask[:, TARGETS.index("S3")].sum())
        q2_cells = int(effective_mask[:, TARGETS.index("Q2")].sum())
        for alpha in ALPHAS:
            pred = clip_prob(sigmoid(e95_logit + alpha * rollback * selector_mask))
            add_pred(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "edge_q2s3_amplitude",
                    "source": "e95",
                    "fallback": "mixmin",
                    "selector": selector_name,
                    "target_scope": "+".join(targets),
                    "graft_alpha": alpha,
                    "selected_cells": int(selector_mask.sum()),
                    "selected_rows": int(np.any(selector_mask, axis=1).sum()),
                    "move_cells": move_cells,
                    "move_rows": selected_rows,
                    "move_q2_cells": q2_cells,
                    "move_s3_cells": s3_cells,
                    "move_edge_cells": edge_cells,
                    "move_edge_rate": edge_cells / max(move_cells, 1),
                },
            )

    return pd.DataFrame(rows), preds, refs, tail_state


def attach_e103_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    e95_tail = float(
        out.loc[
            out["strategy"].eq("control") & out["source"].eq("e95"),
            "e72_adverse_positive_exposure_all",
        ].min()
    )
    e101_ref = (
        out[out["strategy"].eq("control") & out["source"].eq("e101")]
        .sort_values("mean_vs_e95_broad_plausible")
        .iloc[0]
    )
    e101_mean = float(e101_ref["mean_vs_e95_broad_plausible"])
    e101_p95 = float(e101_ref["p95_vs_e95_broad_plausible"])
    e101_beat = float(e101_ref["beat_e95_rate_broad_plausible"])

    is_variant = out["strategy"].eq("edge_q2s3_amplitude")
    out["e103_strict_like"] = (
        is_variant
        & out["nonanchor_evaluated"].fillna(False).astype(bool)
        & out["strict_gate"].fillna(False).astype(bool)
        & (out["all_delta_vs_mixmin"] < -2.0e-5)
        & (out["hidden_q2s3_mean_minus_base"] < 0.0)
        & (out["world_support_minus_base"] < 0.0)
        & (out["block_q2s3_beats_base_rate"] >= 0.50)
        & (out["e72_adverse_positive_exposure_all"] <= e95_tail + 5.0e-7)
    )
    out["e103_pass"] = (
        out["e103_strict_like"].fillna(False).astype(bool)
        & (out["mean_vs_e95_broad_plausible"] < 0.0)
        & (out["p95_vs_e95_broad_plausible"] <= 0.0)
        & (out["beat_e95_rate_broad_plausible"] > 0.75)
        & (out["mean_vs_e95_broad_q2s3"] < 0.0)
    )
    out["dominates_e101"] = (
        out["e103_pass"].fillna(False).astype(bool)
        & (out["mean_vs_e95_broad_plausible"] <= e101_mean - 1.0e-8)
        & (out["p95_vs_e95_broad_plausible"] <= e101_p95 + 1.0e-10)
        & (out["beat_e95_rate_broad_plausible"] >= e101_beat - 1.0e-12)
    )
    out["e101_ref_mean_vs_e95"] = e101_mean
    out["e101_ref_p95_vs_e95"] = e101_p95
    out["e101_ref_beat_rate"] = e101_beat
    out["survival_score"] = (
        -out["mean_vs_e95_broad_plausible"].fillna(0.0)
        - 0.25 * out["p95_vs_e95_broad_plausible"].fillna(0.0)
        + 1.0e-5 * out["beat_e95_rate_broad_plausible"].fillna(0.0)
        - 1.0e-4 * out["move_l1_vs_e95"].fillna(0.0)
    )
    return out


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["dominates_e101"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        [
            "p95_vs_e95_broad_plausible",
            "mean_vs_e95_broad_plausible",
            "active_cells_vs_e95",
            "survival_score",
        ],
        ascending=[True, True, True, False],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, transfer: pd.DataFrame, selected_path: Path | None) -> None:
    controls = scan[scan["strategy"].eq("control")].copy()
    variants = scan[scan["strategy"].eq("edge_q2s3_amplitude")].copy()
    best_pass = variants[variants["e103_pass"].fillna(False).astype(bool)].sort_values(
        ["dominates_e101", "p95_vs_e95_broad_plausible", "mean_vs_e95_broad_plausible"],
        ascending=[False, True, True],
    ).head(12)
    best_transfer = variants.sort_values(
        ["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]
    ).head(12)
    best_edge = variants[variants["move_edge_rate"].fillna(0.0).ge(0.99)].sort_values(
        ["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]
    ).head(12)
    best_interior = variants[variants["move_edge_rate"].fillna(0.0).le(0.01)].sort_values(
        ["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]
    ).head(12)

    control_cols = [
        "source",
        "all_delta_vs_mixmin",
        "e72_adverse_positive_exposure_all",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
    ]
    variant_cols = [
        "tag",
        "selector",
        "graft_alpha",
        "move_cells",
        "move_rows",
        "move_edge_rate",
        "move_q2_cells",
        "move_s3_cells",
        "strict_gate",
        "e103_pass",
        "dominates_e101",
        "all_delta_vs_mixmin",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
    ]

    e101_ref = controls[controls["source"].eq("e101")].iloc[0]
    n_pass = int(variants["e103_pass"].fillna(False).sum())
    n_dom = int(variants["dominates_e101"].fillna(False).sum())
    if n_dom > 0:
        interpretation = (
            "At least one edge/amplitude variant dominates E101 locally under the inherited "
            "E101 stress frame. This would justify an E103 submission only after checking "
            "that it still tests the same public question."
        )
    elif n_pass > 0:
        interpretation = (
            "Edge/amplitude variants can survive the same broad stress, but none dominate "
            "E101 on mean, p95, and beat-rate together. E101 remains the cleaner public sensor; "
            "edge energy is useful mainly for post-E101 branching."
        )
    else:
        interpretation = (
            "The edge-local clue does not survive as a stronger amplitude candidate. Treat "
            "E102 edge proximity as diagnostic geometry only, not a submission selector."
        )

    report = f"""# E103 Edge-Local Q2/S3 Amplitude Probe

## Question

E102 found E101's active cells are weakly hidden-block-edge-local but not
subject/block-local. This probe asks whether edge-local Q2/S3 rollback is a
better E95-relative candidate than E101, or only a diagnostic branch after E101.

## Result

- variant rows: `{len(variants)}`
- E103 pass rows: `{n_pass}`
- E101-dominating rows: `{n_dom}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`
- E101 broad mean/p95/beat: `{float(e101_ref['mean_vs_e95_broad_plausible']):.9f}` / `{float(e101_ref['p95_vs_e95_broad_plausible']):.9f}` / `{float(e101_ref['beat_e95_rate_broad_plausible']):.6f}`

## Controls

{md_table(controls[control_cols].sort_values('all_delta_vs_mixmin'), '.9f')}

## Best Passing Variants

{md_table(best_pass[variant_cols], '.9f')}

## Best Broad-Mean Variants

{md_table(best_transfer[variant_cols], '.9f')}

## Best Edge-Only Variants

{md_table(best_edge[variant_cols], '.9f')}

## Best Interior-Only Variants

{md_table(best_interior[variant_cols], '.9f')}

## Interpretation

{interpretation}
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, tail_state = build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    scan = attach_e103_flags(scan)
    selected_path = materialize(scan, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    summary = (
        scan.groupby(["strategy", "selector", "graft_alpha"], dropna=False)
        .agg(
            rows=("pred_index", "count"),
            e103_pass=("e103_pass", "sum"),
            dominates_e101=("dominates_e101", "sum"),
            best_broad_mean_vs_e95=("mean_vs_e95_broad_plausible", "min"),
            best_broad_p95_vs_e95=("p95_vs_e95_broad_plausible", "min"),
            best_beat_e95=("beat_e95_rate_broad_plausible", "max"),
            min_active_cells_vs_e95=("active_cells_vs_e95", "min"),
            max_move_edge_rate=("move_edge_rate", "max"),
        )
        .reset_index()
        .sort_values(["dominates_e101", "e103_pass", "best_broad_mean_vs_e95"], ascending=[False, False, True])
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, transfer, selected_path)

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {TRANSFER_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
