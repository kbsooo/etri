#!/usr/bin/env python3
"""E76 subset-stability stress for E75 target-specific Q2/S3 amplitude.

E75 found that the E73/E74 sparse gate is locally better with Q2 shrunk and
S3 amplified. This probe asks whether that target-asymmetric ridge survives the
same cell-subset stresses that upgraded E73 in E74.

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
import q2_s3_target_amplitude_ridge_probe as e75  # noqa: E402
import q2_s3_unified_gate_geometry_probe as e72  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_target_amplitude_stability_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_target_amplitude_stability_probe_summary.csv"
PAIR_OUT = OUT / "q2_s3_target_amplitude_stability_probe_pair_comparison.csv"
REPORT_OUT = OUT / "q2_s3_target_amplitude_stability_probe_report.md"

POOL_NAME = e74.POOL_NAME
BASE_AGG = e74.BASE_AGG
DELTA_AGG = e74.DELTA_AGG
GATE = e74.GATE
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = e70.QS_IDXS

E73_FILE = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E74_FILE = OUT / "submission_e74_fullpool_a20_q2s3_gate_55455b60.csv"
E75_FILE = OUT / "submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv"

TARGET_ALPHA_PAIRS = [
    (16.0, 16.0),
    (20.0, 20.0),
    (24.0, 24.0),
    (8.0, 20.0),
    (8.0, 22.0),
    (8.0, 24.0),
    (8.0, 26.0),
    (8.0, 28.0),
    (8.0, 32.0),
    (12.0, 22.0),
    (12.0, 24.0),
    (12.0, 26.0),
    (12.0, 28.0),
    (12.0, 32.0),
    (16.0, 24.0),
    (16.0, 26.0),
    (16.0, 28.0),
    (0.0, 22.0),
    (0.0, 24.0),
    (0.0, 26.0),
    (0.0, 28.0),
]

PAIR_NAMES = {
    (16.0, 16.0): "sym16_e73",
    (20.0, 20.0): "sym20_e74",
    (24.0, 24.0): "sym24_failref",
    (8.0, 28.0): "asym8_28_e75",
}


def pair_name(alpha_q2: float, alpha_s3: float) -> str:
    return PAIR_NAMES.get((float(alpha_q2), float(alpha_s3)), f"q2a{alpha_q2:.0f}_s3a{alpha_s3:.0f}")


def dominant_axis(alpha_q2: float, alpha_s3: float) -> str:
    if alpha_q2 == 0.0:
        return "s3_only"
    if alpha_s3 == 0.0:
        return "q2_only"
    if alpha_q2 == alpha_s3:
        return "equal"
    if alpha_q2 > alpha_s3:
        return "q2_higher"
    return "s3_higher"


def add_reference_distance(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    refs = {
        "e73": load_sub(E73_FILE, sample)[TARGETS].to_numpy(dtype=np.float64),
        "e74": load_sub(E74_FILE, sample)[TARGETS].to_numpy(dtype=np.float64),
        "e75": load_sub(E75_FILE, sample)[TARGETS].to_numpy(dtype=np.float64),
    }
    ref_logits = {name: logit(pred) for name, pred in refs.items()}
    rows = []
    for i, pred in enumerate(preds):
        cur = logit(pred)
        row: dict[str, Any] = {"pred_index": i}
        for name, ref in ref_logits.items():
            row[f"mean_abs_logit_delta_vs_{name}"] = float(np.abs(cur - ref).mean())
            row[f"mean_abs_q2s3_logit_delta_vs_{name}"] = float(np.abs(cur[:, QS_IDXS] - ref[:, QS_IDXS]).mean())
        rows.append(row)
    return scan.merge(pd.DataFrame(rows), on="pred_index", how="left")


def build_target_stability_candidates(
    cells: pd.DataFrame,
    bases: list[np.ndarray],
    deltas: list[np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], list[dict[str, Any]]]:
    base_logits_all = np.stack([logit(x) for x in bases], axis=0)
    delta_all = np.stack(deltas, axis=0)
    pool_idxs = e71.make_unified_pools(cells)[POOL_NAME]
    variants = e74.make_variants(cells, pool_idxs)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    for variant_id, variant in enumerate(variants):
        idxs = variant["idxs"]
        pool = cells.loc[idxs].copy()
        base_logit = e70.aggregate_base(base_logits_all[idxs], BASE_AGG)
        base_pred = e70.clip_prob(e70.sigmoid(base_logit))
        base_tag = e72.e68_tag(base_pred, f"e76_base_{variant['variant_name']}_")
        if base_tag in seen:
            base_index = seen[base_tag]
        else:
            base_index = len(preds)
            seen[base_tag] = base_index
            preds.append(base_pred)

        delta, weights = e74.weighted_delta(cells, idxs, delta_all)
        gate = e72.adaptive_gate(delta_all[idxs], delta, GATE)
        gated_delta = delta * gate
        gate_active_q2 = float((np.abs(gate[:, Q2_IDX]) > 0.0).mean())
        gate_active_s3 = float((np.abs(gate[:, S3_IDX]) > 0.0).mean())
        if np.abs(gated_delta[:, QS_IDXS]).mean() <= 1e-12:
            continue

        for alpha_q2, alpha_s3 in TARGET_ALPHA_PAIRS:
            move = np.zeros_like(gated_delta)
            move[:, Q2_IDX] = float(alpha_q2) * gated_delta[:, Q2_IDX]
            move[:, S3_IDX] = float(alpha_s3) * gated_delta[:, S3_IDX]
            if np.abs(move[:, QS_IDXS]).mean() <= 1e-12:
                continue
            pred = e70.clip_prob(e70.sigmoid(base_logit + move))
            p_name = pair_name(alpha_q2, alpha_s3)
            tag = e72.e68_tag(pred, f"e76_{variant['variant_name']}_{p_name}_")
            if tag in seen:
                pred_index = seen[tag]
            else:
                pred_index = len(preds)
                seen[tag] = pred_index
                preds.append(pred)
            rows.append(
                {
                    "pred_index": pred_index,
                    "base_index": base_index,
                    "tag": tag,
                    "base_tag": base_tag,
                    "variant_id": variant_id,
                    "variant_kind": variant["variant_kind"],
                    "variant_name": variant["variant_name"],
                    "reason": variant["reason"],
                    "subset_key": variant["subset_key"],
                    "pool": POOL_NAME,
                    "pool_size": int(len(idxs)),
                    "pool_support_mean": float(pool["support_count"].mean()),
                    "pool_support2_count": int(pool["support_count"].ge(2).sum()),
                    "base_agg": BASE_AGG,
                    "delta_agg": DELTA_AGG,
                    "gate": GATE,
                    "pair_name": p_name,
                    "alpha_q2": float(alpha_q2),
                    "alpha_s3": float(alpha_s3),
                    "alpha_sum": float(alpha_q2 + alpha_s3),
                    "alpha_max": float(max(alpha_q2, alpha_s3)),
                    "alpha_gap": float(abs(alpha_q2 - alpha_s3)),
                    "dominant_axis": dominant_axis(alpha_q2, alpha_s3),
                    "gate_active_q2": gate_active_q2,
                    "gate_active_s3": gate_active_s3,
                    "mean_abs_q2_delta_unit": float(np.abs(gated_delta[:, Q2_IDX]).mean()),
                    "mean_abs_s3_delta_unit": float(np.abs(gated_delta[:, S3_IDX]).mean()),
                    "mean_abs_q2s3_delta_unit": float(np.abs(gated_delta[:, QS_IDXS]).mean()),
                    "weight_max": float(weights.max()),
                    "weight_entropy": float(-(weights * np.log(weights + 1e-12)).sum()),
                    "cell_heldout_mean": float(pool["heldout_minus_base"].mean()),
                    "cell_world_mean": float(pool["world_support_minus_base"].mean()),
                    "cell_hidden_q2s3_mean": float(pool["hidden_q2s3_mean_minus_base"].mean()),
                    "cell_block_win_mean": float(pool["block_q2s3_beats_base_rate"].mean()),
                }
            )
    return pd.DataFrame(rows), preds, variants


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


def pair_comparison(scan: pd.DataFrame) -> pd.DataFrame:
    keep = ["sym16_e73", "sym20_e74", "asym8_28_e75"]
    rows = []
    for (kind, name), group in scan.groupby(["variant_kind", "variant_name"], sort=False):
        pivot = group[group["pair_name"].isin(keep)].set_index("pair_name")
        if not all(k in pivot.index for k in keep):
            continue
        asym = pivot.loc["asym8_28_e75"]
        sym16 = pivot.loc["sym16_e73"]
        sym20 = pivot.loc["sym20_e74"]
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        deploy = group[group["deployable_gate"]].sort_values("all_delta_vs_mixmin")
        best_deploy = deploy.iloc[0] if len(deploy) else None
        rows.append(
            {
                "variant_kind": kind,
                "variant_name": name,
                "pool_size": int(asym["pool_size"]),
                "asym_all_delta": float(asym["all_delta_vs_mixmin"]),
                "sym16_all_delta": float(sym16["all_delta_vs_mixmin"]),
                "sym20_all_delta": float(sym20["all_delta_vs_mixmin"]),
                "asym_minus_sym16": float(asym["all_delta_vs_mixmin"] - sym16["all_delta_vs_mixmin"]),
                "asym_minus_sym20": float(asym["all_delta_vs_mixmin"] - sym20["all_delta_vs_mixmin"]),
                "asym_strict": bool(asym["strict_gate"]),
                "asym_deployable": bool(asym["deployable_gate"]),
                "sym16_deployable": bool(sym16["deployable_gate"]),
                "sym20_deployable": bool(sym20["deployable_gate"]),
                "asym_beats_sym16": bool(asym["all_delta_vs_mixmin"] < sym16["all_delta_vs_mixmin"]),
                "asym_beats_sym20": bool(asym["all_delta_vs_mixmin"] < sym20["all_delta_vs_mixmin"]),
                "asym_hidden_q2s3": float(asym["hidden_q2s3_mean_minus_base"]),
                "asym_world": float(asym["world_support_minus_base"]),
                "asym_block_win": float(asym["block_q2s3_beats_base_rate"]),
                "best_pair_name": str(best["pair_name"]),
                "best_dominant_axis": str(best["dominant_axis"]),
                "best_all_delta": float(best["all_delta_vs_mixmin"]),
                "best_deployable_pair_name": str(best_deploy["pair_name"]) if best_deploy is not None else "",
                "best_deployable_axis": str(best_deploy["dominant_axis"]) if best_deploy is not None else "",
                "best_deployable_all_delta": float(best_deploy["all_delta_vs_mixmin"]) if best_deploy is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)


def summarize(scan: pd.DataFrame, pair_cmp: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for kind, group in scan.groupby("variant_kind", sort=False):
        cmp = pair_cmp[pair_cmp["variant_kind"].eq(kind)]
        e75_pair = group[group["pair_name"].eq("asym8_28_e75")]
        deploy = group[group["deployable_gate"]]
        rows.append(
            {
                "variant_kind": kind,
                "rows": int(len(group)),
                "variants": int(group["variant_name"].nunique()),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "asym8_28_deployable": int(e75_pair["deployable_gate"].sum()),
                "asym8_28_strict": int(e75_pair["strict_gate"].sum()),
                "asym8_28_loose": int(e75_pair["loose_gate"].sum()),
                "asym8_28_beats_sym16": int(cmp["asym_beats_sym16"].sum()) if len(cmp) else 0,
                "asym8_28_beats_sym20": int(cmp["asym_beats_sym20"].sum()) if len(cmp) else 0,
                "asym8_28_deployable_and_beats_sym20": int(
                    (cmp["asym_deployable"] & cmp["asym_beats_sym20"]).sum()
                )
                if len(cmp)
                else 0,
                "best_deployable_s3_higher_variants": int(cmp["best_deployable_axis"].eq("s3_higher").sum())
                if len(cmp)
                else 0,
                "best_deployable_equal_variants": int(cmp["best_deployable_axis"].eq("equal").sum()) if len(cmp) else 0,
                "best_deployable_s3_only_variants": int(cmp["best_deployable_axis"].eq("s3_only").sum())
                if len(cmp)
                else 0,
                "best_all_delta_vs_mixmin": float(group["all_delta_vs_mixmin"].min()),
                "median_asym8_28_all_delta": float(e75_pair["all_delta_vs_mixmin"].median()) if len(e75_pair) else np.nan,
                "worst_asym8_28_all_delta": float(e75_pair["all_delta_vs_mixmin"].max()) if len(e75_pair) else np.nan,
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["asym8_28_deployable", "deployable", "asym8_28_beats_sym20", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    pair_cmp: pd.DataFrame,
    cells: pd.DataFrame,
    variants: list[dict[str, Any]],
) -> None:
    ref = scan[scan["variant_kind"].eq("reference") & scan["variant_name"].eq("full_pool")].copy()
    ref = ref[ref["pair_name"].isin(["sym16_e73", "sym20_e74", "asym8_28_e75"])]
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    cmp_summary = (
        pair_cmp.groupby("variant_kind")
        .agg(
            variants=("variant_name", "nunique"),
            asym_deployable=("asym_deployable", "sum"),
            asym_beats_sym16=("asym_beats_sym16", "sum"),
            asym_beats_sym20=("asym_beats_sym20", "sum"),
            asym_deployable_and_beats_sym20=(
                "asym_deployable",
                lambda s: int((s & pair_cmp.loc[s.index, "asym_beats_sym20"]).sum()),
            ),
            median_asym_minus_sym20=("asym_minus_sym20", "median"),
            best_deployable_s3_higher=("best_deployable_axis", lambda s: int(s.eq("s3_higher").sum())),
        )
        .reset_index()
    )
    by_pair = (
        scan.groupby(["variant_kind", "pair_name"])
        .agg(
            rows=("tag", "size"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            best_all=("all_delta_vs_mixmin", "min"),
            median_all=("all_delta_vs_mixmin", "median"),
            best_hidden=("hidden_q2s3_mean_minus_base", "min"),
            best_world=("world_support_minus_base", "min"),
        )
        .reset_index()
    )
    lines = [
        "# E76 Q2/S3 Target-Amplitude Stability Probe",
        "",
        "## Observe",
        "",
        "E75's best full-pool ridge is target-asymmetric: Q2 alpha `8`, S3 alpha `28`.",
        "",
        "## Wonder",
        "",
        "Does that target-asymmetric ridge survive cell-subset stress, or is it a full-pool/local-combo artifact?",
        "",
        "## Method",
        "",
        f"- Source pool: `{POOL_NAME}` with `{len(e71.make_unified_pools(cells)[POOL_NAME])}` cells.",
        f"- Variants: `{len(variants)}` across reference, jackknife, group-keep, rank-keep, and deterministic bootstrap8 subsets.",
        f"- Target alpha pairs: `{TARGET_ALPHA_PAIRS}`.",
        f"- Gate/base/delta: `{GATE}` / `{BASE_AGG}` / `{DELTA_AGG}`.",
        "- Every row is combo-scored and hidden/world/block stressed.",
        "",
        "## Full-Pool Reference",
        "",
        e56.markdown_table(
            ref[
                [
                    "pair_name",
                    "alpha_q2",
                    "alpha_s3",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_gate",
                    "deployable_gate",
                ]
            ].sort_values("pair_name")
        ),
        "",
        "## Stability Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Pair Comparison Summary",
        "",
        e56.markdown_table(cmp_summary),
        "",
        "## Pair Grid By Variant Kind",
        "",
        e56.markdown_table(by_pair),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "variant_kind",
                    "variant_name",
                    "pair_name",
                    "dominant_axis",
                    "pool_size",
                    "alpha_q2",
                    "alpha_s3",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deployable[
                [
                    "variant_kind",
                    "variant_name",
                    "pair_name",
                    "dominant_axis",
                    "pool_size",
                    "alpha_q2",
                    "alpha_s3",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "mean_abs_q2s3_logit_delta_vs_e75",
                ]
            ]
        )
        if len(deployable)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    jack = pair_cmp[pair_cmp["variant_kind"].eq("jackknife")]
    boot = pair_cmp[pair_cmp["variant_kind"].eq("bootstrap8")]
    jack_asym_deploy = int(jack["asym_deployable"].sum()) if len(jack) else 0
    boot_asym_deploy = int(boot["asym_deployable"].sum()) if len(boot) else 0
    jack_asym_beats = int((jack["asym_deployable"] & jack["asym_beats_sym20"]).sum()) if len(jack) else 0
    boot_asym_beats = int((boot["asym_deployable"] & boot["asym_beats_sym20"]).sum()) if len(boot) else 0
    if jack_asym_deploy >= 10 and boot_asym_deploy >= 40:
        lines.append("- E75 target asymmetry is broad under subset stress: asym8/28 remains deployable across most jackknife and bootstrap variants.")
    elif jack_asym_deploy > 0 and boot_asym_deploy > 0:
        lines.append("- E75 target asymmetry has partial subset stability, but it is not as broad as the E73 alpha16 sparse-gate sign.")
    else:
        lines.append("- E75 target asymmetry is fragile under this subset stress and should stay behind E74 as a second sensor.")
    lines.extend(
        [
            f"- Asym8/28 deployable and better than sym20: jackknife `{jack_asym_beats}/{len(jack)}`, bootstrap8 `{boot_asym_beats}/{len(boot)}`.",
            "- This probe writes no submission. It decides whether E75 deserves priority over E74 as the second sparse-gate sensor.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{PAIR_OUT.relative_to(ROOT)}`",
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
    rows, preds, variants = build_target_stability_candidates(cells, bases, deltas)
    print(f"built rows={len(rows)} variants={len(variants)} unique_preds={len(preds)}", flush=True)
    scan = score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    pair_cmp = pair_comparison(scan)
    summary = summarize(scan, pair_cmp)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    pair_cmp.to_csv(PAIR_OUT, index=False)
    write_report(scan, summary, pair_cmp, cells, variants)
    print(
        f"rows={len(scan)} variants={scan['variant_name'].nunique()} "
        f"strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"asym8_28_deployable={int(scan[scan['pair_name'].eq('asym8_28_e75')]['deployable_gate'].sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
