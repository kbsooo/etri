#!/usr/bin/env python3
"""E119 E101 flank-gate replacement stress.

E118 found train-flank evidence that is directionally compatible with E101, but
not strong enough to certify it locally. This script asks the smallest next
question before spending another public submission:

Can visible flank support select a smaller E101-direction move that dominates
full E101 under the same broad mean, p95, and beat-rate stress used by E104?

No public labels are fitted. Candidates start from E95 and move selected E118
active cells along the E95->E101 direction.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e104_e101_amplitude_pareto_cliff as e104  # noqa: E402


CELLS_IN = OUT / "e118_e101_flank_label_support_cells.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
SCAN_OUT = OUT / "e119_e101_flank_gate_variant_stress_scan.csv"
SUMMARY_OUT = OUT / "e119_e101_flank_gate_variant_stress_summary.csv"
REPORT_OUT = OUT / "e119_e101_flank_gate_variant_stress_report.md"
SUBMISSION_PREFIX = "submission_e119_flankgate"

EPS = 1.0e-6
SCALES = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00]
SUPPORT_QS = [0.50, 0.60, 0.70, 0.80, 0.90]
TOP_KS = [8, 10, 12, 15, 20, 23, 25, 30, 35, 40, 45, 50]


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


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


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
    tag = e83.stable_tag(pred, f"e119_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": tag, **rec})


def cells_to_mask(cells: pd.DataFrame, selector: pd.Series | np.ndarray, n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    selected = cells[np.asarray(selector, dtype=bool)].copy()
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}
    for rec in selected.to_dict("records"):
        mask[int(rec["sub_idx"]), target_to_idx[str(rec["target"])]] = True
    return mask


def selector_specs(active: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    specs: list[tuple[str, np.ndarray]] = []
    edge_support = active["support_probability_edge_endpoint_beta"].astype(float)
    subj_support = active["support_probability_subject"].astype(float)
    edge_expected = active["expected_delta_edge_endpoint_beta"].astype(float)
    subj_expected = active["expected_delta_subject"].astype(float)
    flip_support = active["flip_benefit"].astype(float) * edge_support

    specs.append(("active_all", np.ones(len(active), dtype=bool)))
    specs.append(("active_s3_all", active["target"].eq("S3").to_numpy()))
    specs.append(("active_q2_all", active["target"].eq("Q2").to_numpy()))
    specs.append(("edge_or_near", active["edge_distance"].astype(float).le(1.0).to_numpy()))
    specs.append(("interior", active["edge_distance"].astype(float).gt(1.0).to_numpy()))
    specs.append(("both_flanks", active["both_flanks"].astype(bool).to_numpy()))
    specs.append(("flank_agree", active["flank_agree"].astype(bool).to_numpy()))
    specs.append(("flank_conflict", active["flank_conflict"].astype(bool).to_numpy()))
    specs.append(("edge_expected_negative", edge_expected.lt(0.0).to_numpy()))
    specs.append(("subject_expected_negative", subj_expected.lt(0.0).to_numpy()))
    specs.append(("edge_support_ge_0p50", edge_support.ge(0.50).to_numpy()))
    specs.append(("edge_support_beats_subject", edge_support.gt(subj_support).to_numpy()))
    specs.append(("edge_support_high_and_near_edge", (edge_support.ge(0.50) & active["edge_distance"].astype(float).le(1.0)).to_numpy()))
    specs.append(("conflict_flat_prior_help", active["expected_delta_conflict_flat"].astype(float).lt(0.0).to_numpy()))

    for q in SUPPORT_QS:
        cut = float(edge_support.quantile(q))
        specs.append((f"edge_support_q{q:.2f}", edge_support.ge(cut).to_numpy()))
        s3 = active["target"].eq("S3")
        if s3.any():
            s3_cut = float(edge_support[s3].quantile(q))
            specs.append((f"s3_edge_support_q{q:.2f}", (s3 & edge_support.ge(s3_cut)).to_numpy()))
        q2 = active["target"].eq("Q2")
        if q2.any():
            q2_cut = float(edge_support[q2].quantile(q))
            specs.append((f"q2_edge_support_q{q:.2f}", (q2 & edge_support.ge(q2_cut)).to_numpy()))

    rank_fields = {
        "edge_expected_best": edge_expected.to_numpy(dtype=np.float64),
        "subject_expected_best": subj_expected.to_numpy(dtype=np.float64),
        "edge_support_best": -edge_support.to_numpy(dtype=np.float64),
        "flip_x_edge_support_best": -flip_support.to_numpy(dtype=np.float64),
        "flip_benefit_best": -active["flip_benefit"].to_numpy(dtype=np.float64),
        "near_edge_first": active["edge_distance"].astype(float).to_numpy(dtype=np.float64),
    }
    for name, values in rank_fields.items():
        order = np.argsort(values)
        for k in TOP_KS:
            if k > len(active):
                continue
            selected = np.zeros(len(active), dtype=bool)
            selected[order[:k]] = True
            specs.append((f"{name}_top{k}", selected))

    unique: list[tuple[str, np.ndarray]] = []
    seen: set[bytes] = set()
    for name, mask in specs:
        mask = np.asarray(mask, dtype=bool)
        if mask.sum() == 0:
            continue
        key = mask.tobytes()
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, mask))
    return unique


def build_refs(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    refs = e101.build_refs(sample)
    refs["e101"] = load_pred(E101_FILE, sample)
    return refs


def build_candidates(
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], pd.DataFrame]:
    refs = build_refs(sample)
    tail_state = e101.e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    cells = pd.read_csv(CELLS_IN)
    active = cells[cells["active"].astype(bool)].copy().reset_index(drop=True)

    e95_logit = logit(refs["e95"])
    e101_logit = logit(refs["e101"])
    direction = e101_logit - e95_logit

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for name in ["mixmin", "e95", "e101", "e89", "e85", "e86", "e90"]:
        add_pred(rows, preds, seen, refs[name], {"strategy": "control", "source": name})

    for selector_name, selector_mask in selector_specs(active):
        full_mask = cells_to_mask(active, selector_mask, len(sample))
        effective_mask = full_mask & (np.abs(direction) > 1.0e-12)
        move_cells = int(effective_mask.sum())
        if move_cells == 0:
            continue
        selected = active[selector_mask].copy()
        target_scope = "+".join(TARGETS[j] for j in np.where(effective_mask.any(axis=0))[0])
        edge_cells = int((selected["edge_distance"].astype(float) <= 1.0).sum())
        for scale in SCALES:
            pred = clip_prob(sigmoid(e95_logit + float(scale) * direction * full_mask))
            add_pred(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "e95_q2s3_tail_graft",
                    "source": "e95",
                    "fallback": "e101",
                    "selector": selector_name,
                    "target_scope": target_scope,
                    "graft_alpha": float(scale),
                    "selected_cells": int(full_mask.sum()),
                    "selected_rows": int(np.any(full_mask, axis=1).sum()),
                    "move_cells": move_cells,
                    "move_rows": int(np.any(effective_mask, axis=1).sum()),
                    "move_edge_cells": edge_cells,
                    "move_edge_rate": edge_cells / max(move_cells, 1),
                    "selected_s3_cells": int(selected["target"].eq("S3").sum()),
                    "selected_q2_cells": int(selected["target"].eq("Q2").sum()),
                    "edge_support_mean": float(selected["support_probability_edge_endpoint_beta"].mean()),
                    "subject_support_mean": float(selected["support_probability_subject"].mean()),
                    "edge_expected_delta_e101_basis": float(
                        selected["expected_delta_edge_endpoint_beta"].sum() / (250 * len(TARGETS))
                    ),
                    "subject_expected_delta_e101_basis": float(
                        selected["expected_delta_subject"].sum() / (250 * len(TARGETS))
                    ),
                    "flip_benefit_share": float(
                        selected["flip_benefit"].sum() / max(active["flip_benefit"].sum(), EPS)
                    ),
                },
            )

    return pd.DataFrame(rows), preds, refs, tail_state, active


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("e95_q2s3_tail_graft")].copy()
    rows: list[dict[str, Any]] = []
    for selector, group in variants.groupby("selector"):
        scale_1 = group.iloc[(group["graft_alpha"].astype(float) - 1.0).abs().argsort()].iloc[0]
        pass_rows = group[group["e101_pass"].fillna(False).astype(bool)]
        dom_rows = group[group["dominates_e101"].fillna(False).astype(bool)]
        mean_better = group[group["mean_gain_vs_e101"] < 0.0]
        mean_p95_better = group[group["beats_mean_p95_loses_beat"].fillna(False).astype(bool)]
        best_mean = group.sort_values("mean_vs_e95_broad_plausible").iloc[0]
        best_pass = pass_rows.sort_values("mean_vs_e95_broad_plausible").iloc[0] if not pass_rows.empty else None
        rows.append(
            {
                "selector": selector,
                "rows": len(group),
                "selected_cells": int(group["selected_cells"].max()),
                "selected_s3_cells": int(group["selected_s3_cells"].max()),
                "selected_q2_cells": int(group["selected_q2_cells"].max()),
                "pass_rows": int(len(pass_rows)),
                "dominates_e101": int(len(dom_rows)),
                "mean_better_rows": int(len(mean_better)),
                "mean_p95_better_but_beat_worse_rows": int(len(mean_p95_better)),
                "scale1_mean_vs_e95": float(scale_1["mean_vs_e95_broad_plausible"]),
                "scale1_p95_vs_e95": float(scale_1["p95_vs_e95_broad_plausible"]),
                "scale1_beat": float(scale_1["beat_e95_rate_broad_plausible"]),
                "best_mean_scale": float(best_mean["graft_alpha"]),
                "best_mean_vs_e95": float(best_mean["mean_vs_e95_broad_plausible"]),
                "best_mean_p95_vs_e95": float(best_mean["p95_vs_e95_broad_plausible"]),
                "best_mean_beat": float(best_mean["beat_e95_rate_broad_plausible"]),
                "best_pass_scale": float(best_pass["graft_alpha"]) if best_pass is not None else np.nan,
                "best_pass_mean_vs_e95": float(best_pass["mean_vs_e95_broad_plausible"]) if best_pass is not None else np.nan,
                "best_pass_p95_vs_e95": float(best_pass["p95_vs_e95_broad_plausible"]) if best_pass is not None else np.nan,
                "best_pass_beat": float(best_pass["beat_e95_rate_broad_plausible"]) if best_pass is not None else np.nan,
                "edge_support_mean": float(group["edge_support_mean"].max()),
                "edge_expected_delta_basis": float(group["edge_expected_delta_e101_basis"].min()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["dominates_e101", "best_pass_mean_vs_e95", "best_mean_vs_e95"],
        ascending=[False, True, True],
    )


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["dominates_e101"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["p95_vs_e95_broad_plausible", "mean_vs_e95_broad_plausible", "active_cells_vs_e95"],
        ascending=[True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, selected_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("e95_q2s3_tail_graft")].copy()
    controls = scan[scan["strategy"].eq("control")].copy()
    pass_rows = variants[variants["e101_pass"].fillna(False).astype(bool)].sort_values(
        ["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]
    )
    dominated = variants[variants["dominates_e101"].fillna(False).astype(bool)]
    best_mean = variants.sort_values(["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]).head(15)
    best_pass = pass_rows.head(15)

    control_cols = [
        "source",
        "all_delta_vs_mixmin",
        "e72_adverse_positive_exposure_all",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
    ]
    row_cols = [
        "tag",
        "selector",
        "graft_alpha",
        "selected_cells",
        "selected_s3_cells",
        "selected_q2_cells",
        "edge_support_mean",
        "strict_gate",
        "e101_pass",
        "dominates_e101",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "mean_gain_vs_e101",
        "p95_gain_vs_e101",
        "beat_gap_vs_e101",
    ]

    n_dom = int(dominated.shape[0])
    n_pass = int(pass_rows.shape[0])
    if n_dom == 0:
        interpretation = (
            "Visible flank support is real enough to explain why E101 is not arbitrary, "
            "but it does not produce a safer pre-feedback replacement. The live signal "
            "appears distributed across the full Q2/S3 E101 active set; hard-gating by "
            "local train flanks mostly removes scenario support faster than it removes "
            "risk. Keep E101 as the next public sensor unless the public result says "
            "the full active set is wrong."
        )
    else:
        interpretation = (
            "At least one flank-gated row dominates E101 on broad mean, p95, and beat "
            "rate. Treat the materialized file as a stronger pre-feedback candidate "
            "than full E101, but still read the selected-cell pattern before submitting."
        )

    report = f"""# E119 E101 Flank-Gate Variant Stress

## Question

E118 made visible flank support plausible but not decisive. This audit asks
whether that support can replace full E101 before public feedback by selecting
only the E101 active cells that train-neighborhood priors favor.

## Result

- variant rows: `{len(variants)}`
- E101-pass rows: `{n_pass}`
- E101-dominating rows: `{n_dom}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`

## Controls

{md_table(controls[control_cols].sort_values('all_delta_vs_mixmin'), '.9f')}

## Selector Summary

{md_table(summary.head(35), '.9f')}

## Best Mean Rows

{md_table(best_mean[row_cols], '.9f')}

## Best E101-Pass Rows

{md_table(best_pass[row_cols], '.9f')}

## Dominating Rows

{md_table(dominated[row_cols], '.9f')}

## Interpretation

{interpretation}
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, tail_state, _active = build_candidates(sample)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e101.merge_transfer(scan, transfer)
    scan = e104.attach_flags(scan)
    summary = summarize(scan)
    selected_path = materialize(scan, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, selected_path)

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
