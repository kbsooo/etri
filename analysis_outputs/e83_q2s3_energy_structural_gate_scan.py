#!/usr/bin/env python3
"""E83 Q2/S3-energy gated structural movement scan.

E82 closed the direct pure Q2/S3 graft branch: the signal is coherent but too
small to be a submission-scale movement. This probe treats that Q2/S3 structure
as a latent row-energy selector instead.

Question:
Can E82's Q2/S3 latent energy identify rows where older broad JEPA/block/raw
structural submissions have useful movement relative to mixmin?

The experiment is intentionally conservative:
- no new learner;
- no public LB fitting;
- every candidate is a gated logit movement from the current public frontier;
- broad movements must survive combo, world, hidden, and energy stress.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, locate, logit  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_strict_cell_consensus_probe as e70  # noqa: E402
import e82_pure_q2s3_source_graft_scan as e82  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "e83_q2s3_energy_structural_gate_scan.csv"
SUMMARY_OUT = OUT / "e83_q2s3_energy_structural_gate_summary.csv"
SOURCE_SUMMARY_OUT = OUT / "e83_q2s3_energy_structural_gate_source_summary.csv"
ENERGY_OUT = OUT / "e83_q2s3_energy_structural_gate_energy_summary.csv"
REPORT_OUT = OUT / "e83_q2s3_energy_structural_gate_report.md"

EPS = 1.0e-6
MAX_FILES_PER_TABLE = 6
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]

SELECTED_TABLES = [
    "jepa_block_consensus_gate_selected.csv",
    "jepa_block_consensus_rawcorrector_selected.csv",
    "jepa_block_consensus_rawcorrector_refine_selected.csv",
    "jepa_block_consensus_rawcorrector_microrefine_shortlist.csv",
]

MANUAL_FILES = [
    # Controls around the active frontier and known sparse-gate failure.
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    # Older broad structural/latent candidates that may contain useful movement
    # but were not trustworthy as direct submissions after mixmin.
    "submission_jepa_energy_ensemble_5a01b623.csv",
    "submission_hiddenblock_seqmotif_cellgate_b8c9ae2f.csv",
    "submission_jepa_block_consensus_rawcorr_refine_a2f628d8.csv",
    "submission_jepa_block_consensus_rawcorr_7cc6473a.csv",
    "submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv",
    "submission_jepa_block_consensus_gate_cf9e36f2.csv",
]

TARGET_SCOPES = {
    "all": list(range(len(TARGETS))),
    "q2s3": QS_IDXS,
    "s_all": [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"]],
    "q3_s2_s3_s4": [TARGETS.index(t) for t in ["Q3", "S2", "S3", "S4"]],
    "non_q2s3": [i for i in range(len(TARGETS)) if i not in QS_IDXS],
}

ROW_GATE_SPECS = [
    ("all_rows", None),
    ("e82_energy_top50", 50),
    ("e82_energy_top100", 100),
    ("e82_energy_top250", 250),
    ("e82_energy_top500", 500),
    ("e82_energy_not_top100", -100),
]

SCALES = [0.25, 0.50, 0.75, 1.00]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(pred: np.ndarray, prefix: str) -> str:
    return e82.stable_tag(pred, prefix)


def sorted_existing_candidate_files() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for table_name in SELECTED_TABLES:
        path = OUT / table_name
        if not path.exists():
            continue
        table = pd.read_csv(path)
        sort_cols = [
            c
            for c in ["compact_focused_score", "posterior_expected_public_vs_anchor", "bridge_score"]
            if c in table.columns
        ]
        if sort_cols:
            table = table.sort_values(sort_cols, ascending=True)
        for rank, rec in enumerate(table.head(MAX_FILES_PER_TABLE).to_dict("records"), start=1):
            file_name = str(rec["file"])
            if file_name in seen or locate(file_name) is None:
                continue
            seen.add(file_name)
            rows.append(
                {
                    "file": file_name,
                    "source_table": table_name,
                    "source_rank": rank,
                    "source": str(rec.get("source", "")),
                    "base_file": str(rec.get("base_file", "")),
                    "target_mask": str(rec.get("target_mask", "")),
                    "gate": str(rec.get("gate", "")),
                    "compact_focused_score": float(rec.get("compact_focused_score", np.nan)),
                    "posterior_expected_public_vs_anchor": float(
                        rec.get("posterior_expected_public_vs_anchor", np.nan)
                    ),
                    "bridge_score": float(rec.get("bridge_score", np.nan)),
                }
            )

    for file_name in MANUAL_FILES:
        if file_name in seen or locate(file_name) is None:
            continue
        seen.add(file_name)
        rows.append(
            {
                "file": file_name,
                "source_table": "manual_controls",
                "source_rank": 999,
                "source": "manual_control",
                "base_file": "",
                "target_mask": "",
                "gate": "",
                "compact_focused_score": np.nan,
                "posterior_expected_public_vs_anchor": np.nan,
                "bridge_score": np.nan,
            }
        )

    return pd.DataFrame(rows)


def build_e82_energy(
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    raw_prior: np.ndarray,
    views: dict[str, np.ndarray],
    components: dict[str, dict[str, np.ndarray]],
) -> tuple[np.ndarray, pd.DataFrame]:
    if not e82.SCAN_OUT.exists():
        raise FileNotFoundError(e82.SCAN_OUT)

    e82_rows, e82_preds, source_summary = e82.build_source_universe(sample, mixmin, raw_prior, views, components)
    scan = pd.read_csv(e82.SCAN_OUT)
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    if evaluated.empty:
        evaluated = scan.copy()
    best = evaluated.sort_values("all_delta_vs_mixmin").head(20)
    pred_indexes = [int(x) for x in best["pred_index"].drop_duplicates().tolist()]

    mix_logit = logit(mixmin)
    energy_parts = []
    for pred_index in pred_indexes:
        pred = e82_preds[pred_index]
        energy_parts.append(np.abs(logit(pred) - mix_logit)[:, QS_IDXS].mean(axis=1))
    energy_stack = np.vstack(energy_parts)
    energy = energy_stack.mean(axis=0)

    top = best.head(1).iloc[0]
    summary = pd.DataFrame(
        [
            {
                "source": "e82_top20_q2s3_energy",
                "source_rows": int(len(e82_rows)),
                "source_preds": int(len(e82_preds)),
                "used_top_predictions": int(len(pred_indexes)),
                "best_e82_tag": str(top["tag"]),
                "best_e82_all_delta": float(top["all_delta_vs_mixmin"]),
                "energy_mean": float(energy.mean()),
                "energy_p90": float(np.quantile(energy, 0.90)),
                "energy_p99": float(np.quantile(energy, 0.99)),
                "energy_max": float(energy.max()),
                "nonzero_rows": int((energy > 1.0e-12).sum()),
                "source_summary": source_summary.to_json(orient="records"),
            }
        ]
    )
    return energy, summary


def row_gate_masks(energy: np.ndarray) -> dict[str, np.ndarray]:
    order = np.argsort(-energy)
    masks: dict[str, np.ndarray] = {}
    for name, n in ROW_GATE_SPECS:
        mask = np.zeros(len(energy), dtype=np.float64)
        if n is None:
            mask[:] = 1.0
        elif n > 0:
            mask[order[: min(n, len(order))]] = 1.0
        else:
            k = min(abs(n), len(order))
            mask[:] = 1.0
            mask[order[:k]] = 0.0
        masks[name] = mask
    return masks


def target_mask(scope: list[int], n_rows: int) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=np.float64)
    mask[:, scope] = 1.0
    return mask


def movement_summary(
    pred: np.ndarray,
    mixmin: np.ndarray,
    row_mask: np.ndarray,
    tmask: np.ndarray,
) -> dict[str, Any]:
    delta = logit(pred) - logit(mixmin)
    moved = np.abs(delta) > 1.0e-12
    target_active = tmask.astype(bool)
    return {
        "active_rows": int(moved.any(axis=1).sum()),
        "active_cells": int(moved.sum()),
        "active_q2s3_cells": int(moved[:, QS_IDXS].sum()),
        "row_gate_rows": int(row_mask.sum()),
        "target_scope_cells": int(target_active.sum()),
        "mean_abs_logit_move_raw": float(np.abs(delta).mean()),
        "mean_abs_q2s3_logit_move_raw": float(np.abs(delta[:, QS_IDXS]).mean()),
        "max_abs_logit_move_raw": float(np.abs(delta).max()),
    }


def build_structural_candidates(
    source_files: pd.DataFrame,
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    energy: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    mix_logit = logit(mixmin)
    gates = row_gate_masks(energy)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {stable_tag(mixmin, "e83_mixmin_"): 0}

    for rec in source_files.to_dict("records"):
        file_name = str(rec["file"])
        source_pred = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        source_delta = logit(source_pred) - mix_logit
        source_abs_move = float(np.abs(source_delta).mean())
        source_q2s3_move = float(np.abs(source_delta[:, QS_IDXS]).mean())
        if source_abs_move <= 1.0e-12:
            continue

        for row_gate_name, row_mask in gates.items():
            row_mask_2d = row_mask[:, None]
            for target_scope, scope in TARGET_SCOPES.items():
                tmask = target_mask(scope, len(sample))
                unit_delta = source_delta * row_mask_2d * tmask
                if np.abs(unit_delta).mean() <= 1.0e-12:
                    continue
                for scale in SCALES:
                    pred = clip_prob(sigmoid(mix_logit + float(scale) * unit_delta))
                    tag = stable_tag(pred, f"e83_{row_gate_name}_{target_scope}_{scale:.2f}_")
                    if tag in seen:
                        continue
                    pred_index = len(preds)
                    seen[tag] = pred_index
                    preds.append(pred)
                    move = movement_summary(pred, mixmin, row_mask, tmask)
                    rows.append(
                        {
                            "pred_index": pred_index,
                            "base_index": 0,
                            "tag": tag,
                            "source_file": file_name,
                            "source_table": str(rec["source_table"]),
                            "source_rank": int(rec["source_rank"]),
                            "source": str(rec["source"]),
                            "source_base_file": str(rec.get("base_file", "")),
                            "source_target_mask": str(rec.get("target_mask", "")),
                            "source_gate": str(rec.get("gate", "")),
                            "compact_focused_score": float(rec.get("compact_focused_score", np.nan)),
                            "posterior_expected_public_vs_anchor": float(
                                rec.get("posterior_expected_public_vs_anchor", np.nan)
                            ),
                            "bridge_score": float(rec.get("bridge_score", np.nan)),
                            "row_gate": row_gate_name,
                            "target_scope": target_scope,
                            "scale": float(scale),
                            "source_mean_abs_logit_move": source_abs_move,
                            "source_mean_abs_q2s3_logit_move": source_q2s3_move,
                            **move,
                        }
                    )
    return pd.DataFrame(rows), preds


def score_candidate_rows(
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
    selected = e70.select_nonanchor_rows(combo)
    base_rows = selected[["row_id", "pred_index", "base_index"]].copy()
    nonanchor = e70.nonanchor_scores(base_rows, preds, mixmin, labels, worlds, views, state)
    metric_cols = [c for c in nonanchor.columns if c not in base_rows.columns and c != "row_id"]
    scan_input = combo.merge(nonanchor[["row_id", *metric_cols]], on="row_id", how="left")
    scan_input["nonanchor_evaluated"] = scan_input["row_id"].isin(set(selected["row_id"].astype(int)))

    scan = e70.add_gates(scan_input, preds, mixmin)
    scan = scan.rename(columns={"strict_consensus_gate": "strict_gate", "loose_consensus_gate": "loose_gate"})
    scan["deployable_gate"] = scan["strict_gate"]

    evaluated = scan["nonanchor_evaluated"].fillna(False).astype(bool)
    scan["structural_all_sets_tail_neutral"] = scan["sets_tail_neutral"].eq(len(e70.COMBO_TABLES))
    scan["structural_all_sets_beat_base"] = scan["sets_beating_base"].eq(len(e70.COMBO_TABLES))
    scan["structural_hidden_core_beats_base"] = scan["hidden_core_minus_base"].lt(0.0)
    scan["structural_world_nonworse"] = scan["world_support_minus_base"].le(0.0)
    scan["structural_raw_energy_nonworse"] = scan["raw_energy_q_p90_minus_base"].le(0.0)
    scan["structural_strict_gate"] = (
        evaluated
        & scan["all_margin_vs_mixmin"]
        & scan["all_beats_base"]
        & scan["structural_all_sets_beat_base"]
        & scan["structural_all_sets_tail_neutral"]
        & scan["structural_hidden_core_beats_base"]
        & scan["structural_world_nonworse"]
        & scan["structural_raw_energy_nonworse"]
    )
    scan["structural_loose_gate"] = (
        evaluated
        & scan["all_beats_base"]
        & scan["structural_hidden_core_beats_base"]
        & scan["structural_world_nonworse"]
    )

    return scan.sort_values(
        ["deployable_gate", "strict_gate", "structural_strict_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    ).reset_index(drop=True)


def summarize(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for keys, group in scan.groupby(["row_gate", "target_scope", "scale"], dropna=False):
        row_gate, target_scope, scale = keys
        evaluated = group[group["nonanchor_evaluated"]]
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        best_eval = evaluated.sort_values("all_delta_vs_mixmin").head(1)
        rows.append(
            {
                "row_gate": row_gate,
                "target_scope": target_scope,
                "scale": float(scale),
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
                "best_hidden_core": float(evaluated["hidden_core_minus_base"].min()) if len(evaluated) else np.nan,
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min()) if len(evaluated) else np.nan,
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "structural_strict", "loose", "best_eval_all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    )

    source_rows = []
    for file_name, group in scan.groupby("source_file", dropna=False):
        evaluated = group[group["nonanchor_evaluated"]]
        source_rows.append(
            {
                "source_file": file_name,
                "source_table": str(group["source_table"].iloc[0]),
                "rows": int(len(group)),
                "nonanchor_evaluated": int(len(evaluated)),
                "strict": int(evaluated["strict_gate"].sum()) if len(evaluated) else 0,
                "deployable": int(evaluated["deployable_gate"].sum()) if len(evaluated) else 0,
                "loose": int(evaluated["loose_gate"].sum()) if len(evaluated) else 0,
                "structural_strict": int(evaluated["structural_strict_gate"].sum()) if len(evaluated) else 0,
                "structural_loose": int(evaluated["structural_loose_gate"].sum()) if len(evaluated) else 0,
                "best_eval_all_delta_vs_mixmin": float(evaluated["all_delta_vs_mixmin"].min())
                if len(evaluated)
                else np.nan,
                "best_all_delta_vs_mixmin": float(group["all_delta_vs_mixmin"].min()),
            }
        )
    source_summary = pd.DataFrame(source_rows).sort_values(
        ["deployable", "strict", "structural_strict", "best_eval_all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    )
    return summary, source_summary


def write_submission(sample: pd.DataFrame, pred: np.ndarray, tag: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"submission_e83_q2s3_structgate_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    source_summary: pd.DataFrame,
    energy_summary: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    evaluated = scan[scan["nonanchor_evaluated"]].copy()
    strict = evaluated[evaluated["strict_gate"]].sort_values("all_delta_vs_mixmin").head(25)
    structural = evaluated[evaluated["structural_strict_gate"]].sort_values("all_delta_vs_mixmin").head(25)
    loose = evaluated[evaluated["loose_gate"]].sort_values("all_delta_vs_mixmin").head(25)
    structural_loose = evaluated[evaluated["structural_loose_gate"]].sort_values("all_delta_vs_mixmin").head(25)
    best = evaluated.sort_values("all_delta_vs_mixmin").head(40)

    cols = [
        "source_file",
        "row_gate",
        "target_scope",
        "scale",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_core_minus_base",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "raw_energy_q_p90_minus_base",
        "strict_gate",
        "structural_strict_gate",
        "loose_gate",
        "structural_loose_gate",
        "mean_abs_logit_move_vs_mixmin",
        "mean_abs_q2s3_logit_move_vs_mixmin",
        "tag",
    ]

    lines = [
        "# E83 Q2/S3-Energy Structural Gate Scan",
        "",
        "## Observe",
        "",
        "E82 showed that pure Q2/S3 movement is coherent across combo, hidden, world, and block stresses, but every evaluated row missed the margin gate.",
        "",
        "## Wonder",
        "",
        "Is Q2/S3 better used as a row-energy selector for broader structural movements than as the movement itself?",
        "",
        "## Hypothesis",
        "",
        "If Q2/S3 latent energy marks a real hidden sleep-state block, then older broad JEPA/block/raw movements should become safer when applied only on high-energy E82 rows. The inverse/not-top gate is a falsification control.",
        "",
        "## Method",
        "",
        "- Use `submission_mixmin_0c916bb4.csv` as the base.",
        "- Build E82 row energy from the top 20 evaluated pure Q2/S3 grafts.",
        "- Load compact-selected broad structural submissions from block consensus, rawcorrector, refine, microrefine, plus manual controls.",
        "- Apply logit movement from each source file to mixmin under row gates, target scopes, and scales.",
        "- Score combo first, then run hidden/world/block stress only on combo-promising rows.",
        "",
        "## Energy Summary",
        "",
        e56.markdown_table(energy_summary),
        "",
        "## Gate Summary",
        "",
        e56.markdown_table(summary.head(40)),
        "",
        "## Source Summary",
        "",
        e56.markdown_table(source_summary.head(40)),
        "",
        "## E70 Strict Rows",
        "",
        e56.markdown_table(strict[cols]) if len(strict) else "None.",
        "",
        "## Structural Strict Rows",
        "",
        e56.markdown_table(structural[cols]) if len(structural) else "None.",
        "",
        "## E70 Loose Rows",
        "",
        e56.markdown_table(loose[cols]) if len(loose) else "None.",
        "",
        "## Structural Loose Rows",
        "",
        e56.markdown_table(structural_loose[cols]) if len(structural_loose) else "None.",
        "",
        "## Best Evaluated Rows",
        "",
        e56.markdown_table(best[cols]),
        "",
        "## Decision",
        "",
    ]
    if submission_path is not None:
        lines += [
            f"Materialized the best strict candidate: `{submission_path.name}`.",
            "",
            "This candidate should still be treated as a world-model sensor: it bets that E82 Q2/S3 energy identifies rows where broad structural movement is public-safe.",
        ]
    else:
        lines += [
            "No strict/deployable E70 candidate was materialized.",
            "",
            "If structural strict rows exist without E70 strict rows, they are diagnostic only: the broader movement may repair hidden-core stress while failing the Q2/S3-specific block guard.",
        ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)

    energy, energy_summary = build_e82_energy(sample, mixmin, raw_prior, views, components)
    source_files = sorted_existing_candidate_files()
    rows, preds = build_structural_candidates(source_files, sample, mixmin, energy)
    if rows.empty:
        raise RuntimeError("no E83 candidates were generated")

    scan = score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary, source_summary = summarize(scan)

    submission_path: Path | None = None
    strict = scan[scan["strict_gate"]].sort_values("all_delta_vs_mixmin")
    if len(strict):
        best = strict.iloc[0]
        submission_path = write_submission(sample, preds[int(best["pred_index"])], str(best["tag"]))
        scan["materialized_submission"] = scan["tag"].eq(str(best["tag"]))
    else:
        scan["materialized_submission"] = False

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    source_summary.to_csv(SOURCE_SUMMARY_OUT, index=False)
    energy_summary.to_csv(ENERGY_OUT, index=False)
    write_report(scan, summary, source_summary, energy_summary, submission_path)

    print(
        {
            "rows": int(len(scan)),
            "nonanchor_evaluated": int(scan["nonanchor_evaluated"].sum()),
            "strict": int(scan["strict_gate"].sum()),
            "deployable": int(scan["deployable_gate"].sum()),
            "loose": int(scan["loose_gate"].sum()),
            "structural_strict": int(scan["structural_strict_gate"].sum()),
            "structural_loose": int(scan["structural_loose_gate"].sum()),
            "best_eval_all_delta": float(
                scan.loc[scan["nonanchor_evaluated"].fillna(False), "all_delta_vs_mixmin"].min()
            ),
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
