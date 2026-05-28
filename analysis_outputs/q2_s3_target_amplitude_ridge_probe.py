#!/usr/bin/env python3
"""E75 target-specific amplitude ridge for the E73/E74 sparse Q2/S3 gate.

E74 showed that the E73 sparse gate is not single-cell fragile, but full-pool
alpha20 improves locally while alpha24 fails strict consensus. This probe asks
whether that amplitude boundary is target-specific: Q2 and S3 may not share the
same safe scale even when the same sparse gate is used.

No submission is written by this script.
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
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_sparse_gate_stability_probe as e74  # noqa: E402
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_unified_gate_geometry_probe as e72  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_target_amplitude_ridge_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_target_amplitude_ridge_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_target_amplitude_ridge_probe_report.md"

POOL_NAME = e74.POOL_NAME
BASE_AGG = e74.BASE_AGG
DELTA_AGG = e74.DELTA_AGG
GATE = e74.GATE
TARGET_ALPHAS = [0.0, 8.0, 12.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 32.0]
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = e70.QS_IDXS
E73_FILE = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E74_FILE = OUT / "submission_e74_fullpool_a20_q2s3_gate_55455b60.csv"


def add_reference_distance(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    out = scan.copy()
    e73 = load_sub(E73_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e74_pred = load_sub(E74_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e73_logit = logit(e73)
    e74_logit = logit(e74_pred)
    rows = []
    for i, pred in enumerate(preds):
        cur = logit(pred)
        rows.append(
            {
                "pred_index": i,
                "mean_abs_logit_delta_vs_e73": float(np.abs(cur - e73_logit).mean()),
                "mean_abs_q2s3_logit_delta_vs_e73": float(np.abs(cur[:, QS_IDXS] - e73_logit[:, QS_IDXS]).mean()),
                "mean_abs_logit_delta_vs_e74": float(np.abs(cur - e74_logit).mean()),
                "mean_abs_q2s3_logit_delta_vs_e74": float(np.abs(cur[:, QS_IDXS] - e74_logit[:, QS_IDXS]).mean()),
            }
        )
    return out.merge(pd.DataFrame(rows), on="pred_index", how="left")


def build_target_alpha_candidates(
    cells: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, Any]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pool_idxs = e71.make_unified_pools(cells)[POOL_NAME]
    pool = cells.loc[pool_idxs].copy()

    base_logit = e70.aggregate_base(base_logits_all[pool_idxs], BASE_AGG)
    base_pred = e70.clip_prob(e70.sigmoid(base_logit))
    delta, weights = e74.weighted_delta(cells, pool_idxs, delta_all)
    gate = e72.adaptive_gate(delta_all[pool_idxs], delta, GATE)
    gated_delta = delta * gate

    preds: list[np.ndarray] = [base_pred]
    seen = {e72.e68_tag(base_pred, "e75_base_full_pool_"): 0}
    rows: list[dict[str, Any]] = []
    for alpha_q2 in TARGET_ALPHAS:
        for alpha_s3 in TARGET_ALPHAS:
            if alpha_q2 == 0.0 and alpha_s3 == 0.0:
                continue
            move = np.zeros_like(gated_delta)
            move[:, Q2_IDX] = float(alpha_q2) * gated_delta[:, Q2_IDX]
            move[:, S3_IDX] = float(alpha_s3) * gated_delta[:, S3_IDX]
            if np.abs(move[:, QS_IDXS]).mean() <= 1e-12:
                continue
            pred = e70.clip_prob(e70.sigmoid(base_logit + move))
            tag = e72.e68_tag(pred, f"e75_q2a{alpha_q2:.1f}_s3a{alpha_s3:.1f}_")
            if tag in seen:
                pred_index = seen[tag]
            else:
                pred_index = len(preds)
                seen[tag] = pred_index
                preds.append(pred)
            dominant_axis = "both"
            if alpha_q2 == 0.0:
                dominant_axis = "s3_only"
            elif alpha_s3 == 0.0:
                dominant_axis = "q2_only"
            elif alpha_q2 == alpha_s3:
                dominant_axis = "equal"
            elif alpha_q2 > alpha_s3:
                dominant_axis = "q2_higher"
            else:
                dominant_axis = "s3_higher"
            rows.append(
                {
                    "pred_index": pred_index,
                    "base_index": 0,
                    "tag": tag,
                    "pool": POOL_NAME,
                    "pool_size": int(len(pool_idxs)),
                    "pool_support_mean": float(pool["support_count"].mean()),
                    "pool_support2_count": int(pool["support_count"].ge(2).sum()),
                    "base_agg": BASE_AGG,
                    "delta_agg": DELTA_AGG,
                    "gate": GATE,
                    "alpha_q2": float(alpha_q2),
                    "alpha_s3": float(alpha_s3),
                    "alpha_sum": float(alpha_q2 + alpha_s3),
                    "alpha_max": float(max(alpha_q2, alpha_s3)),
                    "alpha_gap": float(abs(alpha_q2 - alpha_s3)),
                    "dominant_axis": dominant_axis,
                    "gate_active_q2": float((np.abs(gate[:, Q2_IDX]) > 0.0).mean()),
                    "gate_active_s3": float((np.abs(gate[:, S3_IDX]) > 0.0).mean()),
                    "mean_abs_q2_delta_unit": float(np.abs(gated_delta[:, Q2_IDX]).mean()),
                    "mean_abs_s3_delta_unit": float(np.abs(gated_delta[:, S3_IDX]).mean()),
                    "mean_abs_q2s3_delta_unit": float(np.abs(gated_delta[:, QS_IDXS]).mean()),
                    "weight_max": float(weights.max()),
                    "weight_entropy": float(-(weights * np.log(weights + 1e-12)).sum()),
                }
            )

    meta = {
        "pool": pool,
        "pool_idxs": pool_idxs,
        "weights": weights,
        "gate": gate,
        "gated_delta": gated_delta,
    }
    return pd.DataFrame(rows), preds, meta


def score_rows(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    combo = e70.combo_scores(rows, [mixmin] + preds, sample).reset_index(drop=True)
    combo["row_id"] = np.arange(len(combo), dtype=int)
    base_rows = combo[["row_id", "pred_index", "base_index"]].copy()
    nonanchor = e70.nonanchor_scores(base_rows, preds, mixmin, labels, worlds, views, state)
    metric_cols = [c for c in nonanchor.columns if c not in base_rows.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = True
    scan = e70.add_gates(scan_input, preds, mixmin)
    scan = scan.rename(columns={"strict_consensus_gate": "strict_gate", "loose_consensus_gate": "loose_gate"})
    scan["deployable_gate"] = scan["strict_gate"]
    scan = add_reference_distance(scan, preds, sample)
    return scan.sort_values(
        ["deployable_gate", "strict_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for axis, group in scan.groupby("dominant_axis", sort=False):
        strict = group[group["strict_gate"]]
        rows.append(
            {
                "dominant_axis": axis,
                "rows": int(len(group)),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "best_all_delta_vs_mixmin": float(group["all_delta_vs_mixmin"].min()),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_worst_set_delta": float(group["worst_set_delta_vs_mixmin"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
                "strict_alpha_q2_min": float(strict["alpha_q2"].min()) if len(strict) else np.nan,
                "strict_alpha_q2_max": float(strict["alpha_q2"].max()) if len(strict) else np.nan,
                "strict_alpha_s3_min": float(strict["alpha_s3"].min()) if len(strict) else np.nan,
                "strict_alpha_s3_max": float(strict["alpha_s3"].max()) if len(strict) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "best_all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, meta: dict[str, Any]) -> None:
    ref16 = scan[scan["alpha_q2"].eq(16.0) & scan["alpha_s3"].eq(16.0)].iloc[0]
    ref20 = scan[scan["alpha_q2"].eq(20.0) & scan["alpha_s3"].eq(20.0)].iloc[0]
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deploy = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    strict_grid = (
        scan.pivot_table(index="alpha_q2", columns="alpha_s3", values="strict_gate", aggfunc="max")
        .fillna(False)
        .astype(int)
        .reset_index()
    )
    strict_grid.columns = [str(c) for c in strict_grid.columns]
    delta_grid = (
        scan.pivot_table(index="alpha_q2", columns="alpha_s3", values="all_delta_vs_mixmin", aggfunc="min")
        .reset_index()
    )
    delta_grid.columns = [str(c) for c in delta_grid.columns]
    lines = [
        "# E75 Q2/S3 Target-Specific Amplitude Ridge Probe",
        "",
        "## Observe",
        "",
        "E74 shows full-pool alpha20 improves over E73 alpha16, but alpha24 fails strict consensus.",
        "",
        "## Wonder",
        "",
        "Is the safe amplitude ridge symmetric across Q2 and S3, or does one target need a different scale?",
        "",
        "## Method",
        "",
        f"- Source pool/gate: `{POOL_NAME}` / `{GATE}`.",
        f"- Base/delta aggregation: `{BASE_AGG}` / `{DELTA_AGG}`.",
        f"- Target-specific alpha grid: `{TARGET_ALPHAS}` for Q2 crossed with the same grid for S3.",
        f"- Source cells: `{len(meta['pool_idxs'])}`; support-2 cells: `{int(meta['pool']['support_count'].ge(2).sum())}`.",
        f"- Gate active rates: Q2 `{float((np.abs(meta['gate'][:, Q2_IDX]) > 0.0).mean()):.6g}`, S3 `{float((np.abs(meta['gate'][:, S3_IDX]) > 0.0).mean()):.6g}`.",
        "",
        "## Reference Rows",
        "",
        e56.markdown_table(
            pd.DataFrame(
                [
                    {
                        "name": "E73-equivalent alpha16/16",
                        "tag": ref16["tag"],
                        "all_delta_vs_mixmin": ref16["all_delta_vs_mixmin"],
                        "hidden_q2s3_mean_minus_base": ref16["hidden_q2s3_mean_minus_base"],
                        "world_support_minus_base": ref16["world_support_minus_base"],
                        "block_q2s3_beats_base_rate": ref16["block_q2s3_beats_base_rate"],
                        "strict_gate": ref16["strict_gate"],
                    },
                    {
                        "name": "E74-equivalent alpha20/20",
                        "tag": ref20["tag"],
                        "all_delta_vs_mixmin": ref20["all_delta_vs_mixmin"],
                        "hidden_q2s3_mean_minus_base": ref20["hidden_q2s3_mean_minus_base"],
                        "world_support_minus_base": ref20["world_support_minus_base"],
                        "block_q2s3_beats_base_rate": ref20["block_q2s3_beats_base_rate"],
                        "strict_gate": ref20["strict_gate"],
                    },
                ]
            )
        ),
        "",
        "## Axis Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Strict Gate Matrix",
        "",
        e56.markdown_table(strict_grid),
        "",
        "## All-Delta Matrix",
        "",
        e56.markdown_table(delta_grid),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "dominant_axis",
                    "alpha_q2",
                    "alpha_s3",
                    "tag",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "hidden_q2_minus_base",
                    "hidden_s3_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_gate",
                    "deployable_gate",
                    "mean_abs_q2s3_logit_delta_vs_e74",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deploy[
                [
                    "dominant_axis",
                    "alpha_q2",
                    "alpha_s3",
                    "tag",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "hidden_q2_minus_base",
                    "hidden_s3_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "mean_abs_q2s3_logit_delta_vs_e73",
                    "mean_abs_q2s3_logit_delta_vs_e74",
                ]
            ]
        )
        if len(deploy)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    best_deploy = deploy.iloc[0] if len(deploy) else None
    if best_deploy is not None and (
        float(best_deploy["alpha_q2"]) != 20.0 or float(best_deploy["alpha_s3"]) != 20.0
    ):
        lines.append(
            "- Target-specific amplitude is live: the best deployable row is not the symmetric alpha20/20 E74 row."
        )
    elif best_deploy is not None:
        lines.append(
            "- Symmetric alpha20/20 remains the best deployable row under this target-specific grid."
        )
    else:
        lines.append("- No deployable target-specific amplitude row survived; E73/E74 remain the only sparse-gate files.")
    lines.extend(
        [
            "- This probe does not write a submission. It decides whether an E75 materialized file is justified.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    print("loaded shared state", flush=True)

    strict = e69.strict_rows()
    cells = e71.unique_strict_cells(strict)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)
    rows, preds, meta = build_target_alpha_candidates(cells, bases, deltas)
    print(f"built rows={len(rows)} unique_preds={len(preds)}", flush=True)
    scan = score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, meta)
    print(
        f"rows={len(scan)} strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
