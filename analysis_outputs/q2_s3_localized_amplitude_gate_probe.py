#!/usr/bin/env python3
"""E78 row/cell-localized Q2/S3 amplitude gate probe.

E77 rejected generic posterior averaging over E76 source-subset predictions.
This probe asks the sharper follow-up: can E76's deployable/non-deployable
source-subset distribution be used only as a row/target reliability gate, while
retaining the E75 sparse-gate amplitude family?

No submission is written by default.
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
import q2_s3_target_amplitude_stability_probe as e76  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_localized_amplitude_gate_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_localized_amplitude_gate_probe_summary.csv"
MASK_OUT = OUT / "q2_s3_localized_amplitude_gate_probe_mask_summary.csv"
REPORT_OUT = OUT / "q2_s3_localized_amplitude_gate_probe_report.md"

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = e70.QS_IDXS

Q2_ALPHAS = [0.0, 4.0, 8.0, 12.0, 16.0, 20.0]
S3_ALPHAS = [16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0]
LOCALIZATIONS = ["both", "q2_local_s3_full", "s3_local_q2_full"]
EPS = 1e-12

E75_LOCAL_DELTA = -1.2367636337495824e-5
E74_LOCAL_DELTA = -1.0726078925937799e-5
E73_LOCAL_DELTA = -1.0545787970772658e-5


def stable_tag(pred: np.ndarray, prefix: str) -> str:
    return e76.e72.e68_tag(pred, prefix)


def source_stack(scan: pd.DataFrame, preds: list[np.ndarray], source: pd.DataFrame) -> np.ndarray:
    rows = source.drop_duplicates("pred_index").copy()
    deltas = []
    for rec in rows.to_dict("records"):
        pred = preds[int(rec["pred_index"])]
        base = preds[int(rec["base_index"])]
        deltas.append(logit(pred) - logit(base))
    if not deltas:
        raise ValueError("empty source for reliability stack")
    return np.stack(deltas, axis=0)


def base_qs_mask(full_unit: np.ndarray) -> np.ndarray:
    mask = np.zeros_like(full_unit, dtype=bool)
    mask[:, QS_IDXS] = np.abs(full_unit[:, QS_IDXS]) > EPS
    return mask


def _zero_non_qs(x: np.ndarray) -> np.ndarray:
    out = np.zeros_like(x, dtype=np.float64)
    out[:, QS_IDXS] = x[:, QS_IDXS]
    return out


def reliability_maps_from_stack(
    source_name: str,
    stack: np.ndarray,
    full_unit: np.ndarray,
) -> list[dict[str, Any]]:
    full_sign = np.sign(full_unit)
    valid = base_qs_mask(full_unit)
    signs = np.sign(stack)
    mean = stack.mean(axis=0)
    mean_abs = np.abs(stack).mean(axis=0)
    consensus = np.abs(mean) / (mean_abs + EPS)
    sign_agree = ((signs == full_sign[None, :, :]) & valid[None, :, :]).mean(axis=0)
    sign_match = (np.sign(mean) == full_sign) & valid

    maps: list[dict[str, Any]] = []
    soft = np.where(sign_match, consensus, 0.0)
    maps.append(
        {
            "source_name": source_name,
            "mask_mode": "soft_consensus",
            "mask": _zero_non_qs(soft),
            "threshold": np.nan,
        }
    )
    for thr in [0.55, 0.70, 0.85]:
        maps.append(
            {
                "source_name": source_name,
                "mask_mode": f"hard_consensus_{thr:.2f}",
                "mask": _zero_non_qs(((consensus >= thr) & sign_match).astype(np.float64)),
                "threshold": thr,
            }
        )
    for thr in [0.60, 0.75, 0.90]:
        maps.append(
            {
                "source_name": source_name,
                "mask_mode": f"hard_sign_{thr:.2f}",
                "mask": _zero_non_qs(((sign_agree >= thr) & sign_match).astype(np.float64)),
                "threshold": thr,
            }
        )
    return maps


def excess_maps(
    good: np.ndarray,
    bad: np.ndarray,
    full_unit: np.ndarray,
) -> list[dict[str, Any]]:
    full_sign = np.sign(full_unit)
    valid = base_qs_mask(full_unit)
    good_mean = good.mean(axis=0)
    good_abs = np.abs(good).mean(axis=0)
    bad_abs = np.abs(bad).mean(axis=0)
    sign_match = (np.sign(good_mean) == full_sign) & valid
    excess = np.where(sign_match, (good_abs - bad_abs) / (good_abs + bad_abs + EPS), 0.0)
    soft = np.clip(excess, 0.0, 1.0)
    maps = [
        {
            "source_name": "exact_deployable_vs_failed",
            "mask_mode": "soft_excess",
            "mask": _zero_non_qs(soft),
            "threshold": np.nan,
        }
    ]
    for q in [0.50, 0.70, 0.85]:
        vals = soft[valid & (soft > 0.0)]
        if len(vals) == 0:
            continue
        thr = float(np.quantile(vals, q))
        maps.append(
            {
                "source_name": "exact_deployable_vs_failed",
                "mask_mode": f"hard_excess_q{int(q * 100)}",
                "mask": _zero_non_qs(((soft >= thr) & valid).astype(np.float64)),
                "threshold": thr,
            }
        )
    ratio = bad_abs / (good_abs + EPS)
    for thr in [0.75, 1.00, 1.25]:
        maps.append(
            {
                "source_name": "exact_deployable_vs_failed",
                "mask_mode": f"bad_veto_le{thr:.2f}",
                "mask": _zero_non_qs(((ratio <= thr) & sign_match).astype(np.float64)),
                "threshold": thr,
            }
        )
    return maps


def summarize_mask(mask: np.ndarray, full_unit: np.ndarray) -> dict[str, float]:
    valid = base_qs_mask(full_unit)
    q2_valid = valid[:, Q2_IDX]
    s3_valid = valid[:, S3_IDX]
    return {
        "mask_mean_q2": float(mask[:, Q2_IDX][q2_valid].mean()) if q2_valid.any() else 0.0,
        "mask_mean_s3": float(mask[:, S3_IDX][s3_valid].mean()) if s3_valid.any() else 0.0,
        "mask_active_q2": float((mask[:, Q2_IDX][q2_valid] > 0.0).mean()) if q2_valid.any() else 0.0,
        "mask_active_s3": float((mask[:, S3_IDX][s3_valid] > 0.0).mean()) if s3_valid.any() else 0.0,
    }


def build_reliability_maps(
    e76_scan: pd.DataFrame,
    e76_preds: list[np.ndarray],
    full_unit: np.ndarray,
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    exact = e76_scan[e76_scan["pair_name"].eq("asym8_28_e75")].copy()
    exact_dep = exact[exact["deployable_gate"]].copy()
    exact_fail = exact[~exact["deployable_gate"]].copy()
    s3_dep = e76_scan[e76_scan["deployable_gate"] & e76_scan["dominant_axis"].eq("s3_higher")].copy()
    all_dep = e76_scan[e76_scan["deployable_gate"]].copy()

    source_frames = {
        "exact_all": exact,
        "exact_deployable": exact_dep,
        "s3_deployable": s3_dep,
        "all_deployable": all_dep,
    }
    maps: list[dict[str, Any]] = [
        {
            "source_name": "control",
            "mask_mode": "identity",
            "mask": _zero_non_qs(base_qs_mask(full_unit).astype(np.float64)),
            "threshold": np.nan,
        }
    ]
    source_stacks: dict[str, np.ndarray] = {}
    for name, frame in source_frames.items():
        if frame.empty:
            continue
        stack = source_stack(e76_scan, e76_preds, frame)
        source_stacks[name] = stack
        maps.extend(reliability_maps_from_stack(name, stack, full_unit))
    if len(exact_dep) and len(exact_fail):
        maps.extend(excess_maps(source_stacks["exact_deployable"], source_stack(e76_scan, e76_preds, exact_fail), full_unit))

    rows = []
    for item in maps:
        stats = summarize_mask(item["mask"], full_unit)
        rows.append(
            {
                "source_name": item["source_name"],
                "mask_mode": item["mask_mode"],
                "threshold": item["threshold"],
                **stats,
            }
        )
    return maps, pd.DataFrame(rows)


def localized_unit(full_unit: np.ndarray, mask: np.ndarray, localization: str) -> np.ndarray:
    out = np.zeros_like(full_unit)
    if localization == "both":
        out[:, QS_IDXS] = full_unit[:, QS_IDXS] * mask[:, QS_IDXS]
        return out
    if localization == "q2_local_s3_full":
        out[:, Q2_IDX] = full_unit[:, Q2_IDX] * mask[:, Q2_IDX]
        out[:, S3_IDX] = full_unit[:, S3_IDX]
        return out
    if localization == "s3_local_q2_full":
        out[:, Q2_IDX] = full_unit[:, Q2_IDX]
        out[:, S3_IDX] = full_unit[:, S3_IDX] * mask[:, S3_IDX]
        return out
    raise KeyError(localization)


def dominant_axis(alpha_q2: float, alpha_s3: float) -> str:
    if alpha_q2 <= 0.0 and alpha_s3 > 0.0:
        return "s3_only"
    if alpha_s3 <= 0.0 and alpha_q2 > 0.0:
        return "q2_only"
    if alpha_q2 == alpha_s3:
        return "equal"
    return "s3_higher" if alpha_s3 > alpha_q2 else "q2_higher"


def add_pred(preds: list[np.ndarray], seen: dict[str, int], pred: np.ndarray, prefix: str) -> tuple[int, str]:
    tag = stable_tag(pred, prefix)
    if tag in seen:
        return seen[tag], tag
    idx = len(preds)
    seen[tag] = idx
    preds.append(pred)
    return idx, tag


def build_candidates(
    base_pred: np.ndarray,
    base_logit: np.ndarray,
    full_unit: np.ndarray,
    masks: list[dict[str, Any]],
    mask_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    bidx, base_tag = add_pred(preds, seen, base_pred, "e78_base_full_pool_")
    summary_lookup = {
        (str(row.source_name), str(row.mask_mode)): row
        for row in mask_summary.itertuples(index=False)
    }

    rows: list[dict[str, Any]] = []
    for item in masks:
        source_name = str(item["source_name"])
        mask_mode = str(item["mask_mode"])
        localizations = ["both"] if mask_mode == "identity" else LOCALIZATIONS
        summary = summary_lookup[(source_name, mask_mode)]
        for localization in localizations:
            unit = localized_unit(full_unit, item["mask"], localization)
            if np.abs(unit[:, QS_IDXS]).mean() <= EPS:
                continue
            for alpha_q2 in Q2_ALPHAS:
                for alpha_s3 in S3_ALPHAS:
                    if alpha_q2 == 0.0 and alpha_s3 == 0.0:
                        continue
                    move = np.zeros_like(unit)
                    move[:, Q2_IDX] = float(alpha_q2) * unit[:, Q2_IDX]
                    move[:, S3_IDX] = float(alpha_s3) * unit[:, S3_IDX]
                    if np.abs(move[:, QS_IDXS]).mean() <= EPS:
                        continue
                    pred = e70.clip_prob(e70.sigmoid(base_logit + move))
                    prefix = f"e78_{source_name}_{mask_mode}_{localization}_q2{alpha_q2:.1f}_s3{alpha_s3:.1f}_"
                    pred_index, tag = add_pred(preds, seen, pred, prefix)
                    rows.append(
                        {
                            "pred_index": pred_index,
                            "base_index": bidx,
                            "tag": tag,
                            "base_tag": base_tag,
                            "source_name": source_name,
                            "mask_mode": mask_mode,
                            "localization": localization,
                            "threshold": float(item["threshold"]) if pd.notna(item["threshold"]) else np.nan,
                            "alpha_q2": float(alpha_q2),
                            "alpha_s3": float(alpha_s3),
                            "alpha_sum": float(alpha_q2 + alpha_s3),
                            "alpha_max": float(max(alpha_q2, alpha_s3)),
                            "alpha_gap": float(abs(alpha_q2 - alpha_s3)),
                            "dominant_axis": dominant_axis(float(alpha_q2), float(alpha_s3)),
                            "mask_mean_q2": float(summary.mask_mean_q2),
                            "mask_mean_s3": float(summary.mask_mean_s3),
                            "mask_active_q2": float(summary.mask_active_q2),
                            "mask_active_s3": float(summary.mask_active_s3),
                            "unit_abs_q2": float(np.abs(unit[:, Q2_IDX]).mean()),
                            "unit_abs_s3": float(np.abs(unit[:, S3_IDX]).mean()),
                            "move_abs_q2": float(np.abs(move[:, Q2_IDX]).mean()),
                            "move_abs_s3": float(np.abs(move[:, S3_IDX]).mean()),
                            "move_abs_q2s3": float(np.abs(move[:, QS_IDXS]).mean()),
                        }
                    )
    return pd.DataFrame(rows), preds


def score_candidates(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    scan = e76.score_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    scan["beats_e75_local_all"] = scan["all_delta_vs_mixmin"] < E75_LOCAL_DELTA
    scan["beats_e74_local_all"] = scan["all_delta_vs_mixmin"] < E74_LOCAL_DELTA
    scan["beats_e73_local_all"] = scan["all_delta_vs_mixmin"] < E73_LOCAL_DELTA
    return scan


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["source_name", "mask_mode", "localization"]
    for key, group in scan.groupby(group_cols, sort=False):
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        deploy = group[group["deployable_gate"]]
        strict = group[group["strict_gate"]]
        rows.append(
            {
                "source_name": key[0],
                "mask_mode": key[1],
                "localization": key[2],
                "rows": int(len(group)),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "beats_e75_local_all": int(group["beats_e75_local_all"].sum()),
                "deployable_beats_e75": int((group["deployable_gate"] & group["beats_e75_local_all"]).sum()),
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_worst_set_delta": float(group["worst_set_delta_vs_mixmin"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
                "best_alpha_q2": float(best["alpha_q2"]),
                "best_alpha_s3": float(best["alpha_s3"]),
                "best_deployable_delta": float(deploy["all_delta_vs_mixmin"].min()) if len(deploy) else np.nan,
                "best_strict_delta": float(strict["all_delta_vs_mixmin"].min()) if len(strict) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable_beats_e75", "deployable", "strict", "loose", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, mask_summary: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    by_axis = (
        scan.groupby(["dominant_axis", "localization"])
        .agg(
            rows=("tag", "size"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            beats_e75=("beats_e75_local_all", "sum"),
            deployable_beats_e75=("deployable_gate", lambda x: int((x & scan.loc[x.index, "beats_e75_local_all"]).sum())),
            best_all=("all_delta_vs_mixmin", "min"),
            best_hidden=("hidden_q2s3_mean_minus_base", "min"),
            best_world=("world_support_minus_base", "min"),
            best_block=("block_q2s3_beats_base_rate", "max"),
        )
        .reset_index()
        .sort_values(["deployable_beats_e75", "deployable", "strict", "loose", "best_all"], ascending=[False, False, False, False, True])
    )
    lines = [
        "# E78 Q2/S3 Localized Amplitude Gate Probe",
        "",
        "## Observe",
        "",
        "E76 says S3-heavy/Q2-low direction is subset-stable but exact E75 amplitude is only partly deployable. E77 says averaging those subset predictions is not enough: safe Q2/S3 posterior movement is sub-margin, while full posterior margin is tail/set unsafe.",
        "",
        "## Wonder",
        "",
        "Is the missing object a row/target reliability gate over E75's sparse amplitude movement, especially a gate that shrinks Q2 or unstable cells while leaving S3-heavy signal intact?",
        "",
        "## Method",
        "",
        f"- Base movement: E75 full-pool `{e74.POOL_NAME}` / `{e74.GATE}` unit delta.",
        f"- Q2 alpha grid: `{Q2_ALPHAS}`.",
        f"- S3 alpha grid: `{S3_ALPHAS}`.",
        "- Reliability maps are derived from E76 source-subset exact-asym, deployable, S3-heavy, and deployable-vs-failed stacks.",
        "- Localizations: both Q2/S3 localized, Q2 localized with full S3, and S3 localized with full Q2.",
        "- Candidates are scored by the same combo, hidden, world, block, and raw-energy gates used by E76/E77.",
        "",
        "## Mask Summary",
        "",
        e56.markdown_table(mask_summary),
        "",
        "## Stress Summary",
        "",
        e56.markdown_table(summary.head(60)),
        "",
        "## By Axis",
        "",
        e56.markdown_table(by_axis),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "source_name",
                    "mask_mode",
                    "localization",
                    "alpha_q2",
                    "alpha_s3",
                    "dominant_axis",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "raw_energy_q_p90_minus_base",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                    "beats_e75_local_all",
                ]
            ]
        ),
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deployable[
                [
                    "source_name",
                    "mask_mode",
                    "localization",
                    "alpha_q2",
                    "alpha_s3",
                    "dominant_axis",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "raw_energy_q_p90_minus_base",
                    "beats_e75_local_all",
                ]
            ]
        )
        if len(deployable)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    deploy_beats = int((scan["deployable_gate"] & scan["beats_e75_local_all"]).sum())
    if deploy_beats:
        lines.append(f"- Localized amplitude is live: `{deploy_beats}` deployable rows beat E75 local all-combo.")
    elif int(scan["deployable_gate"].sum()):
        lines.append("- Localized amplitude creates deployable rows, but none beat E75 local all-combo.")
    else:
        lines.append("- Localized amplitude does not create deployable rows under the current stress gate.")
    lines.extend(
        [
            "- This probe writes no submission by default. Materialize only if the best deployable row has a clearer stress profile than E73/E75/E74.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{MASK_OUT.relative_to(ROOT)}`",
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
    e75_rows, e75_preds, meta = e75.build_target_alpha_candidates(cells, bases, deltas)
    full_unit = meta["gated_delta"]
    base_pred = e75_preds[0]
    base_logit = logit(base_pred)
    print(f"loaded E75 unit rows={len(e75_rows)} cells={len(meta['pool_idxs'])}", flush=True)

    e76_rows, e76_preds, variants = e76.build_target_stability_candidates(cells, bases, deltas)
    e76_scan = pd.read_csv(e76.SCAN_OUT)
    missing_tags = set(e76_scan["tag"]) - set(e76_rows["tag"])
    if len(e76_rows) != len(e76_scan) or missing_tags or int(e76_scan["pred_index"].max()) >= len(e76_preds):
        raise RuntimeError("E76 rebuilt rows do not match persisted E76 scan; rerun E76 before E78")
    print(f"loaded E76 scan rows={len(e76_scan)} variants={len(variants)} preds={len(e76_preds)}", flush=True)

    masks, mask_summary = build_reliability_maps(e76_scan, e76_preds, full_unit)
    rows, preds = build_candidates(base_pred, base_logit, full_unit, masks, mask_summary)
    print(f"built localized rows={len(rows)} masks={len(masks)} unique_preds={len(preds)}", flush=True)

    scan = score_candidates(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    mask_summary.to_csv(MASK_OUT, index=False)
    write_report(scan, summary, mask_summary)
    print(
        f"rows={len(scan)} strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"deployable_beats_e75={int((scan['deployable_gate'] & scan['beats_e75_local_all']).sum())} "
        f"best_all={float(scan['all_delta_vs_mixmin'].min()):.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )


if __name__ == "__main__":
    main()
