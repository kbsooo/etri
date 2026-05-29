#!/usr/bin/env python3
"""E86 robustness stress for E85 target-pruned structural movement.

E85 opened a deployable candidate by pruning E84 movement down to mostly
S1/S2/S3. This probe asks whether that is a single best-row artifact or a
stable target-axis law across E84 source rows and structural source families.

It rebuilds E85 predictions, forms source-diverse logit-delta consensus
variants from strict E85 rows, and scores those variants with the same combo and
non-anchor stress used by E83-E85.
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

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e85_inverse_conflict_target_prune as e85  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCAN_OUT = OUT / "e86_e85_target_prune_robustness_scan.csv"
SUMMARY_OUT = OUT / "e86_e85_target_prune_robustness_summary.csv"
SOURCE_STABILITY_OUT = OUT / "e86_e85_target_prune_source_stability.csv"
REPORT_OUT = OUT / "e86_e85_target_prune_robustness_report.md"

MAX_NONANCHOR_ROWS = 700
TARGET_MASKS = [
    "S1,S2,S3",
    "Q2,S1,S2,S3",
    "S1,S3",
    "Q2,S1,S3",
    "S1,S3,S4",
    "Q2,S1,S3,S4",
    "Q2,S2,S3",
]
SELECTION_MODES = ["top", "source_file", "seed_rank"]
TOP_NS = [3, 5, 10, 20, 40, 80]
AGGREGATORS = ["mean", "median", "trim20"]
SHRINKS = [0.75, 0.90, 1.00, 1.10, 1.25]


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), e83.EPS, 1.0 - e83.EPS)


def source_family(path: str) -> str:
    name = Path(str(path)).name
    if "rawcorr_micro" in name:
        return "rawcorr_micro"
    if "rawcorr_refine" in name:
        return "rawcorr_refine"
    if "rawcorr" in name:
        return "rawcorr"
    if "consensus_gate" in name:
        return "gate"
    if "hiddenblock" in name:
        return "hiddenblock"
    return "other"


def aggregate_delta(deltas: np.ndarray, mode: str) -> np.ndarray:
    if mode == "mean":
        return deltas.mean(axis=0)
    if mode == "median":
        return np.median(deltas, axis=0)
    if mode == "trim20":
        if deltas.shape[0] < 5:
            return deltas.mean(axis=0)
        ordered = np.sort(deltas, axis=0)
        k = max(1, int(np.floor(0.2 * deltas.shape[0])))
        if 2 * k >= deltas.shape[0]:
            return deltas.mean(axis=0)
        return ordered[k:-k].mean(axis=0)
    raise ValueError(f"unknown aggregate mode: {mode}")


def select_source_rows(group: pd.DataFrame, mode: str, n: int) -> pd.DataFrame:
    sorted_group = group.sort_values(
        ["all_delta_vs_mixmin", "set_inverse_top_delta_vs_mixmin", "raw_energy_q_p90_minus_base"],
        ascending=[True, True, True],
    )
    if mode == "top":
        return sorted_group.head(n)
    if mode == "source_file":
        return sorted_group.drop_duplicates("struct_source_file").head(n)
    if mode == "seed_rank":
        return sorted_group.drop_duplicates("seed_rank").head(n)
    raise ValueError(f"unknown selection mode: {mode}")


def source_stability_table(e85_scan: pd.DataFrame) -> pd.DataFrame:
    evaluated = e85_scan[e85_scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    evaluated["source_family"] = evaluated["struct_source_file"].map(source_family)
    rows: list[dict[str, Any]] = []
    for keep_targets, group in evaluated.groupby("keep_targets", dropna=False):
        strict = group[group["strict_gate"].fillna(False).astype(bool)]
        rows.append(
            {
                "keep_targets": keep_targets,
                "evaluated": int(len(group)),
                "strict": int(len(strict)),
                "deployable": int(strict["deployable_gate"].sum()) if len(strict) else 0,
                "unique_source_files": int(strict["struct_source_file"].nunique()) if len(strict) else 0,
                "unique_seed_ranks": int(strict["seed_rank"].nunique()) if len(strict) else 0,
                "source_families": ",".join(sorted(strict["source_family"].unique())) if len(strict) else "",
                "best_all_delta": float(strict["all_delta_vs_mixmin"].min()) if len(strict) else np.nan,
                "median_all_delta": float(strict["all_delta_vs_mixmin"].median()) if len(strict) else np.nan,
                "worst_strict_all_delta": float(strict["all_delta_vs_mixmin"].max()) if len(strict) else np.nan,
                "best_inverse_top_delta": float(strict["set_inverse_top_delta_vs_mixmin"].min())
                if len(strict)
                else np.nan,
                "worst_strict_inverse_top_delta": float(strict["set_inverse_top_delta_vs_mixmin"].max())
                if len(strict)
                else np.nan,
                "best_world": float(strict["world_support_minus_base"].min()) if len(strict) else np.nan,
                "best_raw_energy": float(strict["raw_energy_q_p90_minus_base"].min()) if len(strict) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["strict", "best_all_delta"], ascending=[False, True])


def rebuild_e85_predictions() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.DataFrame, dict[str, np.ndarray], Any, pd.DataFrame, list[np.ndarray], pd.DataFrame]:
    sample, mixmin, labels, worlds, views, state, e84_rows, e84_preds, e84_scan = e85.reconstruct_e84_predictions()
    seed = e85.selected_seed_rows(e84_scan)
    rows, preds = e85.build_pruned_candidates(seed, e84_rows, e84_preds, mixmin)
    return sample, mixmin, labels, worlds, views, state, rows, preds, pd.read_csv(e85.SCAN_OUT)


def build_consensus_candidates(
    e85_rows: pd.DataFrame,
    e85_preds: list[np.ndarray],
    e85_scan: pd.DataFrame,
    mixmin: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    pred_by_tag = e85_rows.set_index("tag")["pred_index"].astype(int).to_dict()
    strict = e85_scan[
        e85_scan["nonanchor_evaluated"].fillna(False).astype(bool)
        & e85_scan["strict_gate"].fillna(False).astype(bool)
        & e85_scan["keep_targets"].isin(TARGET_MASKS)
    ].copy()
    strict["source_family"] = strict["struct_source_file"].map(source_family)

    mix_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {e83.stable_tag(mixmin, "e86_mixmin_"): 0}

    for keep_targets, group in strict.groupby("keep_targets", dropna=False):
        for selection_mode in SELECTION_MODES:
            for n in TOP_NS:
                selected = select_source_rows(group, selection_mode, n)
                if len(selected) < min(n, len(group)) or len(selected) < 2:
                    continue
                deltas = []
                missing = False
                for tag in selected["tag"]:
                    pred_index = pred_by_tag.get(str(tag))
                    if pred_index is None:
                        missing = True
                        break
                    deltas.append(logit(e85_preds[pred_index]) - mix_logit)
                if missing:
                    continue
                delta_stack = np.stack(deltas, axis=0)
                for agg in AGGREGATORS:
                    base_delta = aggregate_delta(delta_stack, agg)
                    for shrink in SHRINKS:
                        pred = clip_prob(sigmoid(mix_logit + float(shrink) * base_delta))
                        tag = e83.stable_tag(pred, f"e86_{agg}_{selection_mode}_{n}_s{shrink:.2f}_")
                        if tag in seen:
                            pred_index = seen[tag]
                        else:
                            pred_index = len(preds)
                            seen[tag] = pred_index
                            preds.append(pred)
                        rows.append(
                            {
                                "pred_index": pred_index,
                                "base_index": 0,
                                "tag": tag,
                                "keep_targets": str(keep_targets),
                                "selection_mode": selection_mode,
                                "requested_n": int(n),
                                "selected_n": int(len(selected)),
                                "unique_source_files": int(selected["struct_source_file"].nunique()),
                                "unique_seed_ranks": int(selected["seed_rank"].nunique()),
                                "source_families": ",".join(sorted(selected["source_family"].unique())),
                                "aggregator": agg,
                                "shrink": float(shrink),
                                "source_best_all_delta": float(selected["all_delta_vs_mixmin"].min()),
                                "source_median_all_delta": float(selected["all_delta_vs_mixmin"].median()),
                                "source_worst_all_delta": float(selected["all_delta_vs_mixmin"].max()),
                                "source_best_inverse_top_delta": float(selected["set_inverse_top_delta_vs_mixmin"].min()),
                                "source_median_inverse_top_delta": float(selected["set_inverse_top_delta_vs_mixmin"].median()),
                                "mean_abs_logit_move_raw": float(np.abs(float(shrink) * base_delta).mean()),
                                "active_cells": int((np.abs(base_delta) > 1.0e-12).sum()),
                                "active_rows": int((np.abs(base_delta) > 1.0e-12).any(axis=1).sum()),
                            }
                        )
    return pd.DataFrame(rows).drop_duplicates("tag").reset_index(drop=True), preds


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, group in scan.groupby(["keep_targets", "selection_mode", "aggregator", "shrink"], dropna=False):
        keep_targets, selection_mode, agg, shrink = keys
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)]
        strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)]
        rows.append(
            {
                "keep_targets": keep_targets,
                "selection_mode": selection_mode,
                "aggregator": agg,
                "shrink": float(shrink),
                "rows": int(len(group)),
                "evaluated": int(len(evaluated)),
                "strict": int(len(strict)),
                "deployable": int(strict["deployable_gate"].sum()) if len(strict) else 0,
                "loose": int(evaluated["loose_gate"].sum()) if len(evaluated) else 0,
                "max_unique_source_files": int(group["unique_source_files"].max()),
                "best_all_delta": float(evaluated["all_delta_vs_mixmin"].min()) if len(evaluated) else np.nan,
                "best_inverse_top_delta": float(evaluated["set_inverse_top_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_raw05_delta": float(evaluated["set_raw05_compatible_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_all_sign_delta": float(evaluated["set_all_sign_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min()) if len(evaluated) else np.nan,
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
                "best_raw_energy": float(evaluated["raw_energy_q_p90_minus_base"].min()) if len(evaluated) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "best_all_delta", "max_unique_source_files"],
        ascending=[False, False, True, False],
    )


def survival_score(row: pd.Series) -> tuple:
    return (
        int(bool(row["strict_gate"])),
        int(bool(row["structural_strict_gate"])),
        int(row["unique_source_files"]),
        int(row["unique_seed_ranks"]),
        -float(row["all_delta_vs_mixmin"]),
        -float(row["set_inverse_top_delta_vs_mixmin"]),
        -float(row["raw_energy_q_p90_minus_base"]),
    )


def write_submission(sample: pd.DataFrame, pred: np.ndarray, tag: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"submission_e86_e85_consensus_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    source_stability: pd.DataFrame,
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].copy()
    top_cols = [
        "tag",
        "keep_targets",
        "selection_mode",
        "selected_n",
        "unique_source_files",
        "unique_seed_ranks",
        "source_families",
        "aggregator",
        "shrink",
        "all_delta_vs_mixmin",
        "set_inverse_top_delta_vs_mixmin",
        "set_raw05_compatible_delta_vs_mixmin",
        "set_all_sign_delta_vs_mixmin",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_core_minus_base",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "raw_energy_q_p90_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
        "strict_gate",
    ]
    lines = [
        "# E86 E85 Target-Prune Robustness",
        "",
        "## Observe",
        "",
        "E85 opened a strict/deployable target-pruned candidate, but the public risk is whether that file is a single-source artifact.",
        "",
        "## Wonder",
        "",
        "Does the S1/S2/S3 target-prune law survive source-diverse logit consensus and small shrink/overstep stress?",
        "",
        "## Method",
        "",
        "- Rebuild E85 target-pruned predictions from the same E84 seeds.",
        "- Use strict E85 rows only, grouped by target mask.",
        "- Build logit-delta consensus variants by top rows, distinct source files, and distinct seed ranks.",
        "- Aggregate with mean/median/trimmed mean and apply shrink values `0.75,0.90,1.00,1.10,1.25`.",
        "- Score with the same combo and non-anchor stress as E83-E85.",
        "",
        "## E85 Source Stability",
        "",
        e56.markdown_table(source_stability.head(30)),
        "",
        "## Consensus Summary",
        "",
        e56.markdown_table(summary.head(40)),
        "",
        "## Top Strict Consensus Rows",
        "",
        e56.markdown_table(strict.sort_values(["all_delta_vs_mixmin", "unique_source_files"], ascending=[True, False])[top_cols].head(40))
        if len(strict)
        else "None.",
        "",
        "## Decision",
        "",
    ]
    if submission_path is None:
        lines += [
            "No source-consensus row beat the E85 single-row candidate under the strict gate.",
            "",
            "Keep E85 as the public candidate and use E86 only as robustness evidence.",
        ]
    else:
        best = strict.sort_values(["unique_source_files", "all_delta_vs_mixmin"], ascending=[False, True]).iloc[0]
        lines += [
            f"Materialized source-consensus candidate: `{submission_path.name}`.",
            "",
            f"It keeps `{best['keep_targets']}`, uses `{best['selection_mode']}` selection over `{int(best['unique_source_files'])}` source files, `{best['aggregator']}` aggregation, and shrink `{best['shrink']}`.",
            "",
            "This file is a robustness-oriented companion to E85, not an automatic replacement unless public-risk preference favors source diversity over maximum local edge.",
        ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, mixmin, labels, worlds, views, state, e85_rows, e85_preds, e85_scan = rebuild_e85_predictions()
    source_stability = source_stability_table(e85_scan)
    rows, preds = build_consensus_candidates(e85_rows, e85_preds, e85_scan, mixmin)
    if rows.empty:
        raise RuntimeError("No E86 consensus rows were generated")

    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    source_stability.to_csv(SOURCE_STABILITY_OUT, index=False)

    strict = scan[scan["strict_gate"].fillna(False).astype(bool)].copy()
    submission_path: Path | None = None
    scan["materialized_submission"] = False
    if len(strict):
        strict = strict.assign(_score=strict.apply(survival_score, axis=1))
        # Prefer a genuinely source-diverse strict consensus if it keeps useful margin.
        robust = strict[
            strict["unique_source_files"].ge(10)
            & strict["all_delta_vs_mixmin"].lt(-1.0e-5)
            & strict["set_inverse_top_delta_vs_mixmin"].lt(0.0)
            & strict["set_raw05_compatible_delta_vs_mixmin"].lt(0.0)
            & strict["set_all_sign_delta_vs_mixmin"].lt(0.0)
        ].copy()
        if len(robust):
            best = robust.sort_values(
                ["unique_source_files", "all_delta_vs_mixmin", "raw_energy_q_p90_minus_base"],
                ascending=[False, True, True],
            ).iloc[0]
            submission_path = write_submission(sample, preds[int(best["pred_index"])], str(best["tag"]))
            scan["materialized_submission"] = scan["tag"].eq(str(best["tag"]))

    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(source_stability, scan, summary, submission_path)

    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)]
    print(
        {
            "rows": int(len(scan)),
            "evaluated": int(len(evaluated)),
            "strict": int(scan["strict_gate"].sum()),
            "deployable": int(scan["deployable_gate"].sum()),
            "loose": int(scan["loose_gate"].sum()),
            "best_eval_all_delta": float(evaluated["all_delta_vs_mixmin"].min()) if len(evaluated) else None,
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
