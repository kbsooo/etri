#!/usr/bin/env python3
"""E85 target-prune E84's inverse-top conflict.

E84 found candidates that pass margin, hidden/world/block stress, and two combo
worlds, but every row is rejected by the `inverse_top` combo set. This probe asks
whether that conflict is target-axis specific. It takes the best E84 loose
recombinations, keeps different target subsets of their mixmin-relative logit
movement, and re-scores them under the same stress.
"""

from __future__ import annotations

from itertools import combinations
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
from public_subset_sensitivity_audit import ce_matrix  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e84_structural_margin_q2s3_safety_recombination as e84  # noqa: E402
import public_lb_actual_anchor_ranker as ranker  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCAN_OUT = OUT / "e85_inverse_conflict_target_prune_scan.csv"
SUMMARY_OUT = OUT / "e85_inverse_conflict_target_prune_summary.csv"
TARGET_CONTRIB_OUT = OUT / "e85_inverse_conflict_target_prune_target_contrib.csv"
ROW_CONTRIB_OUT = OUT / "e85_inverse_conflict_target_prune_row_contrib.csv"
REPORT_OUT = OUT / "e85_inverse_conflict_target_prune_report.md"

SEED_LIMIT = 80
MAX_NONANCHOR_ROWS = 700


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), e83.EPS, 1.0 - e83.EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def target_masks() -> list[tuple[str, list[str]]]:
    masks: list[tuple[str, list[str]]] = []
    for n in range(1, len(TARGETS) + 1):
        for combo in combinations(TARGETS, n):
            masks.append(("+".join(combo), list(combo)))
    return masks


def reconstruct_e84_predictions() -> tuple[
    pd.DataFrame,
    np.ndarray,
    np.ndarray,
    pd.DataFrame,
    dict[str, np.ndarray],
    Any,
    pd.DataFrame,
    list[np.ndarray],
    pd.DataFrame,
]:
    sample, mixmin, labels, worlds, views, state, e83_rows, e83_preds = e84.reconstruct_e83_state()
    struct_pool, q_pool = e84.select_pools(pd.read_csv(e83.SCAN_OUT))
    rows, preds = e84.build_recombined_candidates(struct_pool, q_pool, e83_rows, e83_preds, mixmin)
    scan = pd.read_csv(e84.SCAN_OUT)
    return sample, mixmin, labels, worlds, views, state, rows, preds, scan


def selected_seed_rows(scan: pd.DataFrame) -> pd.DataFrame:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    seed = evaluated[
        evaluated["loose_gate"].fillna(False).astype(bool)
        & evaluated["all_margin_vs_mixmin"].fillna(False).astype(bool)
        & evaluated["hidden_q2s3_beats_base"].fillna(False).astype(bool)
        & evaluated["world_nonworse"].fillna(False).astype(bool)
        & evaluated["block_majority_beats"].fillna(False).astype(bool)
        & evaluated["block_tail_safe"].fillna(False).astype(bool)
    ].copy()
    seed = seed.sort_values(
        [
            "structural_raw_energy_nonworse",
            "all_delta_vs_mixmin",
            "set_inverse_top_delta_vs_mixmin",
        ],
        ascending=[False, True, True],
    ).head(SEED_LIMIT)
    return seed.reset_index(drop=True)


def build_pruned_candidates(
    seed: pd.DataFrame,
    e84_rows: pd.DataFrame,
    e84_preds: list[np.ndarray],
    mixmin: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    pred_by_tag = e84_rows.set_index("tag")["pred_index"].astype(int).to_dict()
    mix_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {e83.stable_tag(mixmin, "e85_mixmin_"): 0}
    target_to_idx = {t: i for i, t in enumerate(TARGETS)}

    for sidx, rec in enumerate(seed.to_dict("records")):
        source_tag = str(rec["tag"])
        source_pred = e84_preds[pred_by_tag[source_tag]]
        source_delta = logit(source_pred) - mix_logit
        for mask_name, keep_targets in target_masks():
            gate = np.zeros(len(TARGETS), dtype=np.float64)
            for target in keep_targets:
                gate[target_to_idx[target]] = 1.0
            if float(np.abs(source_delta * gate).mean()) <= 1.0e-14:
                continue
            pred = clip_prob(sigmoid(mix_logit + source_delta * gate))
            tag = e83.stable_tag(pred, f"e85_tprune_{sidx:02d}_")
            if tag in seen:
                pred_index = seen[tag]
            else:
                pred_index = len(preds)
                seen[tag] = pred_index
                preds.append(pred)
            kept = ",".join(keep_targets)
            removed = ",".join([t for t in TARGETS if t not in keep_targets])
            move = source_delta * gate
            rows.append(
                {
                    "pred_index": pred_index,
                    "base_index": 0,
                    "tag": tag,
                    "seed_rank": int(sidx),
                    "source_tag": source_tag,
                    "struct_source_file": str(rec["struct_source_file"]),
                    "struct_weight": float(rec["struct_weight"]),
                    "q_weight": float(rec["q_weight"]),
                    "q_target_scope": str(rec["q_target_scope"]),
                    "keep_targets": kept,
                    "removed_targets": removed,
                    "n_keep_targets": int(len(keep_targets)),
                    "source_all_delta_vs_mixmin": float(rec["all_delta_vs_mixmin"]),
                    "source_inverse_top_delta_vs_mixmin": float(rec["set_inverse_top_delta_vs_mixmin"]),
                    "source_raw05_delta_vs_mixmin": float(rec["set_raw05_compatible_delta_vs_mixmin"]),
                    "source_all_sign_delta_vs_mixmin": float(rec["set_all_sign_delta_vs_mixmin"]),
                    "source_raw_energy_q_p90_minus_base": float(rec["raw_energy_q_p90_minus_base"]),
                    "mean_abs_logit_move_raw": float(np.abs(move).mean()),
                    "active_cells": int((np.abs(move) > 1.0e-12).sum()),
                    "active_rows": int((np.abs(move) > 1.0e-12).any(axis=1).sum()),
                }
            )
    return pd.DataFrame(rows), preds


def combo_contributions(
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    pred: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    masks = ranker.mask_matrix(sample)
    target_rows: list[dict[str, Any]] = []
    row_frames: list[pd.DataFrame] = []
    for set_name, table in ranker.COMBO_TABLES.items():
        combo_df = pd.read_csv(OUT / table).head(160).copy().reset_index(drop=True)
        weights = ranker.combo_weights(combo_df)
        contrib = np.zeros_like(pred)
        for pair, weight in zip(combo_df.itertuples(index=False), weights):
            q = ranker.load_submission(str(pair.scenario_file), sample)
            mask_vec = masks[int(pair.mask_index)]
            contrib += float(weight) * mask_vec[:, None] * (ce_matrix(q, pred) - ce_matrix(q, mixmin)) / len(TARGETS)
        for target, value in zip(TARGETS, contrib.sum(axis=0)):
            target_rows.append({"combo_set": set_name, "target": target, "contribution_vs_mixmin": float(value)})
        frame = sample[KEYS].copy()
        frame["combo_set"] = set_name
        frame["row_index"] = np.arange(len(sample), dtype=int)
        frame["row_contribution_vs_mixmin"] = contrib.sum(axis=1)
        for j, target in enumerate(TARGETS):
            frame[f"target_contrib_{target}"] = contrib[:, j]
        row_frames.append(frame)
    return pd.DataFrame(target_rows), pd.concat(row_frames, ignore_index=True)


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keep_targets, group in scan.groupby("keep_targets", dropna=False):
        evaluated = group[group["nonanchor_evaluated"].fillna(False).astype(bool)]
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        best_eval = evaluated.sort_values("all_delta_vs_mixmin").head(1)
        rows.append(
            {
                "keep_targets": keep_targets,
                "rows": int(len(group)),
                "nonanchor_evaluated": int(len(evaluated)),
                "strict": int(evaluated["strict_gate"].sum()) if len(evaluated) else 0,
                "deployable": int(evaluated["deployable_gate"].sum()) if len(evaluated) else 0,
                "loose": int(evaluated["loose_gate"].sum()) if len(evaluated) else 0,
                "structural_strict": int(evaluated["structural_strict_gate"].sum()) if len(evaluated) else 0,
                "structural_loose": int(evaluated["structural_loose_gate"].sum()) if len(evaluated) else 0,
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_eval_all_delta_vs_mixmin": float(best_eval["all_delta_vs_mixmin"].iloc[0])
                if len(best_eval)
                else np.nan,
                "best_inverse_top_delta": float(evaluated["set_inverse_top_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_raw05_delta": float(evaluated["set_raw05_compatible_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_all_sign_delta": float(evaluated["set_all_sign_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min())
                if len(evaluated)
                else np.nan,
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
                "best_raw_energy": float(evaluated["raw_energy_q_p90_minus_base"].min()) if len(evaluated) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "structural_strict", "loose", "best_eval_all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    )


def write_submission(sample: pd.DataFrame, pred: np.ndarray, tag: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"submission_e85_inverse_conflict_pruned_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    seed: pd.DataFrame,
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    target_contrib: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    strict = evaluated[evaluated["strict_gate"].fillna(False).astype(bool)].sort_values("all_delta_vs_mixmin")
    top_cols = [
        "tag",
        "source_tag",
        "keep_targets",
        "removed_targets",
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
        "loose_gate",
    ]
    lines = [
        "# E85 Inverse-Top Conflict Target Prune",
        "",
        "## Observe",
        "",
        "E84 recombination is healthy under hidden/world/block stress but rejected by the `inverse_top` combo set.",
        "",
        "## Wonder",
        "",
        "Is the `inverse_top` rejection a row/block conflict, or a target-axis conflict that can be falsified by pruning target movements?",
        "",
        "## Method",
        "",
        f"- Seeds: top `{len(seed)}` E84 loose rows that pass margin, hidden/world/block, and block-tail guards.",
        "- For each seed, apply every non-empty subset of the seven target movements relative to mixmin.",
        "- Score with the same combo, hidden/world/block, raw-energy, and strict gates as E84.",
        "",
        "## E84 Sensor Target Contribution",
        "",
        e56.markdown_table(target_contrib.pivot(index="target", columns="combo_set", values="contribution_vs_mixmin").reset_index()),
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(40)),
        "",
        "## Strict Rows",
        "",
        e56.markdown_table(strict[top_cols].head(40)) if len(strict) else "None.",
        "",
        "## Best Evaluated Rows",
        "",
        e56.markdown_table(evaluated.sort_values("all_delta_vs_mixmin")[top_cols].head(40)),
        "",
        "## Decision",
        "",
    ]
    if submission_path is not None:
        best = strict.iloc[0]
        lines += [
            f"Materialized best strict target-pruned candidate: `{submission_path.name}`.",
            "",
            f"It keeps `{best['keep_targets']}` and removes `{best['removed_targets']}` from the E84 movement.",
            "",
            "This file bets that the E84 conflict is target-axis contamination, not a broad row/block rejection.",
        ]
    else:
        lines += [
            "No strict target-pruned candidate survived.",
            "",
            "The conflict is not solved by target-axis pruning alone; the next branch should be row/block-specific.",
        ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, mixmin, labels, worlds, views, state, e84_rows, e84_preds, e84_scan = reconstruct_e84_predictions()
    seed = selected_seed_rows(e84_scan)
    if seed.empty:
        raise RuntimeError("No E84 loose seed rows available")
    rows, preds = build_pruned_candidates(seed, e84_rows, e84_preds, mixmin)
    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)

    sensor = e84_scan[e84_scan["materialized_sensor"].fillna(False).astype(bool)].sort_values("all_delta_vs_mixmin")
    if len(sensor):
        sensor_tag = str(sensor.iloc[0]["tag"])
    else:
        sensor_tag = str(seed.iloc[0]["tag"])
    source_pred = e84_preds[int(e84_rows.set_index("tag").loc[sensor_tag, "pred_index"])]
    target_contrib, row_contrib = combo_contributions(sample, mixmin, source_pred)

    strict = scan[scan["strict_gate"].fillna(False).astype(bool)].sort_values(
        [
            "all_delta_vs_mixmin",
            "set_inverse_top_delta_vs_mixmin",
            "raw_energy_q_p90_minus_base",
        ],
        ascending=[True, True, True],
    )
    submission_path: Path | None = None
    scan["materialized_submission"] = False
    if len(strict):
        best = strict.iloc[0]
        submission_path = write_submission(sample, preds[int(best["pred_index"])], str(best["tag"]))
        scan["materialized_submission"] = scan["tag"].eq(str(best["tag"]))

    summary = summarize(scan)
    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_contrib.to_csv(TARGET_CONTRIB_OUT, index=False)
    row_contrib.to_csv(ROW_CONTRIB_OUT, index=False)
    write_report(seed, scan, summary, target_contrib, submission_path)
    print(
        {
            "rows": int(len(scan)),
            "nonanchor_evaluated": int(scan["nonanchor_evaluated"].sum()),
            "strict": int(scan["strict_gate"].sum()),
            "deployable": int(scan["deployable_gate"].sum()),
            "loose": int(scan["loose_gate"].sum()),
            "best_eval_all_delta": float(
                scan.loc[scan["nonanchor_evaluated"].fillna(False), "all_delta_vs_mixmin"].min()
            ),
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
