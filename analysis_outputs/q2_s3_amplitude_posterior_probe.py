#!/usr/bin/env python3
"""E77 posterior aggregation probe for Q2/S3 target-asymmetric amplitude.

E76 says the S3-heavy/Q2-low direction is stable across source-subset variants,
but exact E75 q2=8/s3=28 deployability is only partial. This probe asks a
JEPA-style follow-up question: can the distribution of E76 subset predictions be
used as a latent posterior over amplitude, rather than trusting one universal
alpha pair?

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
import q2_s3_strict_cell_amplitude_probe as e69  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import q2_s3_target_amplitude_stability_probe as e76  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_amplitude_posterior_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_amplitude_posterior_probe_summary.csv"
SELECTOR_OUT = OUT / "q2_s3_amplitude_posterior_probe_selector_summary.csv"
REPORT_OUT = OUT / "q2_s3_amplitude_posterior_probe_report.md"

E73_FILE = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E74_FILE = OUT / "submission_e74_fullpool_a20_q2s3_gate_55455b60.csv"
E75_FILE = OUT / "submission_e75_q2a8_s3a28_sparse_amp_f07219b4.csv"

QS_IDXS = e70.QS_IDXS
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")

AGG_MODES = ["mean", "median", "signed_p60", "signed_p75", "signed_p90"]
BASE_REFS = ["mixmin", "e73", "e74"]
TARGET_SCOPES = ["q2s3", "s3_only", "full"]
SHRINKS = [0.50, 0.75, 1.00, 1.25, 1.50, 1.75, 2.00, 2.50]
MAX_DYNAMIC_PAIRS = 8


def aggregate_delta(stack: np.ndarray, mode: str) -> np.ndarray:
    if mode == "mean":
        return stack.mean(axis=0)
    if mode == "median":
        return np.median(stack, axis=0)
    if mode.startswith("signed_p"):
        q = float(mode.replace("signed_p", "")) / 100.0
        mean = stack.mean(axis=0)
        mag = np.quantile(np.abs(stack), q, axis=0)
        return np.sign(mean) * mag
    raise KeyError(mode)


def apply_scope(delta: np.ndarray, scope: str) -> np.ndarray:
    out = np.zeros_like(delta)
    if scope == "q2s3":
        out[:, QS_IDXS] = delta[:, QS_IDXS]
        return out
    if scope == "s3_only":
        out[:, S3_IDX] = delta[:, S3_IDX]
        return out
    if scope == "q2_only":
        out[:, Q2_IDX] = delta[:, Q2_IDX]
        return out
    if scope == "full":
        return delta.copy()
    raise KeyError(scope)


def dominant_axis_from_delta(delta: np.ndarray) -> str:
    q2 = float(np.abs(delta[:, Q2_IDX]).mean())
    s3 = float(np.abs(delta[:, S3_IDX]).mean())
    if q2 <= 1e-12 and s3 > 1e-12:
        return "s3_only"
    if s3 <= 1e-12 and q2 > 1e-12:
        return "q2_only"
    if q2 <= 1e-12 and s3 <= 1e-12:
        return "none"
    ratio = s3 / max(q2, 1e-12)
    if 0.90 <= ratio <= 1.10:
        return "balanced"
    return "s3_higher" if ratio > 1.10 else "q2_higher"


def stable_tag(pred: np.ndarray, prefix: str) -> str:
    return e76.e72.e68_tag(pred, prefix)


def selector_frames(scan: pd.DataFrame) -> list[tuple[str, str, pd.DataFrame]]:
    selectors: list[tuple[str, str, pd.DataFrame]] = []

    deploy = scan[scan["deployable_gate"]].copy()
    s3_deploy = deploy[deploy["dominant_axis"].eq("s3_higher")].copy()
    exact = scan[scan["pair_name"].eq("asym8_28_e75")].copy()

    if len(exact):
        selectors.append(("exact_asym_all", "all exact E75 asym8/28 rows", exact))
        exact_dep = exact[exact["deployable_gate"]].copy()
        if len(exact_dep):
            selectors.append(("exact_asym_deployable", "deployable exact E75 asym8/28 rows", exact_dep))

    if len(deploy):
        best_deploy = deploy.sort_values("all_delta_vs_mixmin").groupby("variant_name", as_index=False).head(1)
        selectors.append(("best_deployable_per_variant", "best deployable row in each source variant", best_deploy))

    if len(s3_deploy):
        best_s3 = s3_deploy.sort_values("all_delta_vs_mixmin").groupby("variant_name", as_index=False).head(1)
        selectors.append(("best_s3_deployable_per_variant", "best S3-heavy deployable row in each source variant", best_s3))
        selectors.append(("all_s3_deployable", "all S3-heavy deployable rows", s3_deploy))

    pair_summary = (
        scan.groupby(["pair_name", "dominant_axis"])
        .agg(
            rows=("tag", "size"),
            deployable=("deployable_gate", "sum"),
            strict=("strict_gate", "sum"),
            loose=("loose_gate", "sum"),
            median_all=("all_delta_vs_mixmin", "median"),
            best_all=("all_delta_vs_mixmin", "min"),
        )
        .reset_index()
    )
    pair_summary = pair_summary[
        pair_summary["dominant_axis"].isin(["s3_higher", "equal"])
        & pair_summary["deployable"].ge(70)
    ].sort_values(["deployable", "median_all"], ascending=[False, True])

    for rec in pair_summary.head(MAX_DYNAMIC_PAIRS).to_dict("records"):
        pair = str(rec["pair_name"])
        frame = scan[scan["pair_name"].eq(pair)].copy()
        selectors.append((f"pair_all_{pair}", f"all rows for stable pair {pair}", frame))
        dep = frame[frame["deployable_gate"]].copy()
        if len(dep):
            selectors.append((f"pair_deployable_{pair}", f"deployable rows for stable pair {pair}", dep))

    # Keep this negative-control axis explicit if it exists in future scans.
    q2_only = scan[scan["dominant_axis"].eq("q2_only") & scan["deployable_gate"]].copy()
    if len(q2_only):
        selectors.append(("q2_only_deployable_control", "Q2-only deployable control rows", q2_only))

    dedup: list[tuple[str, str, pd.DataFrame]] = []
    seen: set[str] = set()
    for name, desc, frame in selectors:
        if name in seen or frame.empty:
            continue
        seen.add(name)
        dedup.append((name, desc, frame))
    return dedup


def add_pred(preds: list[np.ndarray], seen: dict[str, int], pred: np.ndarray, prefix: str) -> tuple[int, str]:
    tag = stable_tag(pred, prefix)
    if tag in seen:
        return seen[tag], tag
    idx = len(preds)
    seen[tag] = idx
    preds.append(pred)
    return idx, tag


def build_posterior_candidates(
    e76_scan: pd.DataFrame,
    e76_preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame]:
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    base_indexes: dict[str, int] = {}
    base_tags: dict[str, str] = {}
    for name in ["mixmin", "e73", "e74", "e75"]:
        idx, tag = add_pred(preds, seen, refs[name], f"e77_base_{name}_")
        base_indexes[name] = idx
        base_tags[name] = tag

    selector_summaries: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    source_logits = {i: logit(pred) for i, pred in enumerate(e76_preds)}
    ref_logits = {name: logit(pred) for name, pred in refs.items()}

    for selector_name, selector_desc, source in selector_frames(e76_scan):
        source = source.drop_duplicates("pred_index").copy()
        source_pred_indexes = source["pred_index"].astype(int).to_numpy()
        selector_summaries.append(
            {
                "selector_name": selector_name,
                "description": selector_desc,
                "source_rows": int(len(source)),
                "source_variants": int(source["variant_name"].nunique()),
                "source_pairs": int(source["pair_name"].nunique()),
                "deployable_rate": float(source["deployable_gate"].mean()),
                "strict_rate": float(source["strict_gate"].mean()),
                "loose_rate": float(source["loose_gate"].mean()),
                "best_source_all_delta": float(source["all_delta_vs_mixmin"].min()),
                "median_source_all_delta": float(source["all_delta_vs_mixmin"].median()),
                "best_source_hidden_q2s3": float(source["hidden_q2s3_mean_minus_base"].min()),
                "best_source_world": float(source["world_support_minus_base"].min()),
            }
        )
        if len(source_pred_indexes) == 0:
            continue
        src_stack_by_base = {
            base_name: np.stack([source_logits[int(i)] - ref_logits[base_name] for i in source_pred_indexes], axis=0)
            for base_name in BASE_REFS
        }
        for base_name in BASE_REFS:
            base_logit = ref_logits[base_name]
            for agg_mode in AGG_MODES:
                raw_delta = aggregate_delta(src_stack_by_base[base_name], agg_mode)
                for scope in TARGET_SCOPES:
                    scoped_delta = apply_scope(raw_delta, scope)
                    if np.abs(scoped_delta).mean() <= 1e-12:
                        continue
                    for shrink in SHRINKS:
                        move = float(shrink) * scoped_delta
                        pred = e70.clip_prob(e70.sigmoid(base_logit + move))
                        prefix = f"e77_{selector_name}_{base_name}_{agg_mode}_{scope}_{shrink:.2f}_"
                        pred_index, tag = add_pred(preds, seen, pred, prefix)
                        q2_move = float(np.abs(move[:, Q2_IDX]).mean())
                        s3_move = float(np.abs(move[:, S3_IDX]).mean())
                        full_move = float(np.abs(move).mean())
                        rows.append(
                            {
                                "pred_index": pred_index,
                                "base_index": base_indexes[base_name],
                                "tag": tag,
                                "base_tag": base_tags[base_name],
                                "selector_name": selector_name,
                                "selector_desc": selector_desc,
                                "base_ref": base_name,
                                "agg_mode": agg_mode,
                                "target_scope": scope,
                                "shrink": float(shrink),
                                "dominant_axis": dominant_axis_from_delta(move),
                                "source_rows": int(len(source)),
                                "source_variants": int(source["variant_name"].nunique()),
                                "source_pairs": int(source["pair_name"].nunique()),
                                "source_deployable_rate": float(source["deployable_gate"].mean()),
                                "source_strict_rate": float(source["strict_gate"].mean()),
                                "source_loose_rate": float(source["loose_gate"].mean()),
                                "source_best_all_delta": float(source["all_delta_vs_mixmin"].min()),
                                "source_median_all_delta": float(source["all_delta_vs_mixmin"].median()),
                                "source_best_hidden_q2s3": float(source["hidden_q2s3_mean_minus_base"].min()),
                                "source_best_world": float(source["world_support_minus_base"].min()),
                                "mean_abs_q2_move_unit": q2_move / max(float(shrink), 1e-12),
                                "mean_abs_s3_move_unit": s3_move / max(float(shrink), 1e-12),
                                "mean_abs_q2_move": q2_move,
                                "mean_abs_s3_move": s3_move,
                                "mean_abs_full_move": full_move,
                                "s3_to_q2_move_ratio": float(s3_move / max(q2_move, 1e-12)),
                            }
                        )
    return pd.DataFrame(rows), preds, pd.DataFrame(selector_summaries)


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
    scan["beats_e75_local_all"] = scan["all_delta_vs_mixmin"] < -1.2367636337495824e-5
    scan["beats_e74_local_all"] = scan["all_delta_vs_mixmin"] < -1.0726078925937799e-5
    scan["beats_e73_local_all"] = scan["all_delta_vs_mixmin"] < -1.0545787970772658e-5
    return scan


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (base_ref, target_scope), group in scan.groupby(["base_ref", "target_scope"], sort=False):
        deploy = group[group["deployable_gate"]]
        strict = group[group["strict_gate"]]
        rows.append(
            {
                "base_ref": base_ref,
                "target_scope": target_scope,
                "rows": int(len(group)),
                "strict": int(group["strict_gate"].sum()),
                "deployable": int(group["deployable_gate"].sum()),
                "loose": int(group["loose_gate"].sum()),
                "beats_e75_local_all": int(group["beats_e75_local_all"].sum()),
                "best_all_delta_vs_mixmin": float(group["all_delta_vs_mixmin"].min()),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "best_worst_set_delta": float(group["worst_set_delta_vs_mixmin"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
                "best_deployable_delta": float(deploy["all_delta_vs_mixmin"].min()) if len(deploy) else np.nan,
                "best_strict_delta": float(strict["all_delta_vs_mixmin"].min()) if len(strict) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "loose", "best_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, selector_summary: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(30)
    deployable = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    strict = scan[scan["strict_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    by_selector = (
        scan.groupby("selector_name")
        .agg(
            rows=("tag", "size"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            beats_e75=("beats_e75_local_all", "sum"),
            best_all=("all_delta_vs_mixmin", "min"),
            best_minus_base=("all_minus_base", "min"),
            best_hidden=("hidden_q2s3_mean_minus_base", "min"),
            best_world=("world_support_minus_base", "min"),
            best_block=("block_q2s3_beats_base_rate", "max"),
        )
        .reset_index()
        .sort_values(["deployable", "strict", "loose", "best_all"], ascending=[False, False, False, True])
    )
    lines = [
        "# E77 Q2/S3 Amplitude Posterior Probe",
        "",
        "## Observe",
        "",
        "E76 separates direction from exact amplitude: S3-heavy beats symmetric controls in every source-subset variant, but exact asym8/28 is deployable in only 49/94 variants.",
        "",
        "## Wonder",
        "",
        "Can the E76 source-subset prediction distribution be used as a latent posterior over amplitude, reducing exact-alpha fragility without losing local margin, hidden support, world support, or block stress?",
        "",
        "## Method",
        "",
        f"- Source scan: `{e76.SCAN_OUT.relative_to(ROOT)}`.",
        f"- Selectors: `{len(selector_summary)}` groups from exact asym rows, best deployable rows per variant, all S3-heavy deployable rows, and dynamically stable alpha pairs.",
        f"- Base references: `{BASE_REFS}`.",
        f"- Aggregators: `{AGG_MODES}`.",
        f"- Target scopes: `{TARGET_SCOPES}`.",
        f"- Shrinks: `{SHRINKS}`.",
        "- Candidates are built as logit-space posterior movements from mixmin/E73/E74, then scored by the same combo, hidden, world, block, raw-energy gates used by E76.",
        "",
        "## Selector Summary",
        "",
        e56.markdown_table(selector_summary),
        "",
        "## Stress Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## By Selector",
        "",
        e56.markdown_table(by_selector.head(40)),
        "",
        "## Best Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "selector_name",
                    "base_ref",
                    "agg_mode",
                    "target_scope",
                    "shrink",
                    "dominant_axis",
                    "source_rows",
                    "source_variants",
                    "source_pairs",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                    "beats_e75_local_all",
                ]
            ]
        ),
        "",
        "## Best Strict Rows",
        "",
        e56.markdown_table(
            strict[
                [
                    "selector_name",
                    "base_ref",
                    "agg_mode",
                    "target_scope",
                    "shrink",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "mean_abs_q2_move",
                    "mean_abs_s3_move",
                    "mean_abs_full_move",
                ]
            ]
        )
        if len(strict)
        else "_None._",
        "",
        "## Best Deployable Rows",
        "",
        e56.markdown_table(
            deployable[
                [
                    "selector_name",
                    "base_ref",
                    "agg_mode",
                    "target_scope",
                    "shrink",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "mean_abs_q2_move",
                    "mean_abs_s3_move",
                    "mean_abs_full_move",
                ]
            ]
        )
        if len(deployable)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    strict_n = int(scan["strict_gate"].sum())
    deployable_n = int(scan["deployable_gate"].sum())
    beats_e75_n = int((scan["deployable_gate"] & scan["beats_e75_local_all"]).sum())
    if deployable_n and beats_e75_n:
        lines.append("- Posterior amplitude aggregation is live: at least one deployable row beats the E75 local all-combo delta.")
    elif deployable_n:
        lines.append("- Posterior amplitude aggregation is deployable but does not beat E75's local all-combo edge.")
    elif strict_n:
        lines.append("- Strict rows exist but no deployable row survives the E76-style gate.")
    else:
        lines.append("- Posterior aggregation does not solve the exact-amplitude instability under the current stress gate.")
    lines.extend(
        [
            "- This probe writes no submission. If a row is later materialized, it should be treated as an amplitude-posterior hypothesis, not as a generic ensemble.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{SELECTOR_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e73 = load_sub(E73_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e74 = load_sub(E74_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e75 = load_sub(E75_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    refs = {"mixmin": mixmin, "e73": e73, "e74": e74, "e75": e75}

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
    e76_rows, e76_preds, variants = e76.build_target_stability_candidates(cells, bases, deltas)
    e76_scan = pd.read_csv(e76.SCAN_OUT)
    missing_tags = set(e76_scan["tag"]) - set(e76_rows["tag"])
    if len(e76_rows) != len(e76_scan) or missing_tags or int(e76_scan["pred_index"].max()) >= len(e76_preds):
        raise RuntimeError("E76 rebuilt rows do not match persisted E76 scan; rerun E76 before E77")
    print(f"loaded E76 scan rows={len(e76_scan)} variants={len(variants)} preds={len(e76_preds)}", flush=True)

    rows, preds, selector_summary = build_posterior_candidates(e76_scan, e76_preds, refs)
    print(
        f"built posterior rows={len(rows)} selectors={len(selector_summary)} unique_preds={len(preds)}",
        flush=True,
    )
    scan = score_candidates(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    selector_summary.to_csv(SELECTOR_OUT, index=False)
    write_report(scan, summary, selector_summary)
    print(
        f"rows={len(scan)} strict={int(scan['strict_gate'].sum())} "
        f"deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} "
        f"beats_e75_deployable={int((scan['deployable_gate'] & scan['beats_e75_local_all']).sum())} "
        f"best_all={scan['all_delta_vs_mixmin'].min():.6g} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}",
        flush=True,
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
