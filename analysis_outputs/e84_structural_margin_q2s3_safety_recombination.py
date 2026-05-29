#!/usr/bin/env python3
"""E84 recombine structural margin with Q2/S3 safety movement.

E83 split the remaining signal into two incompatible-looking parts:
- broad/non-Q2S3 structural movements can create local combo margin, but they
  damage Q2/S3 hidden/world guards;
- E72-derived Q2/S3 movements pass Q2/S3 guards, but remain sub-margin.

This probe asks whether the two parts are actually complementary: keep the
structural movement outside Q2/S3, then add only the Q2/S3 component from the
E72-safe branch.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "e84_structural_margin_q2s3_safety_recombination_scan.csv"
SUMMARY_OUT = OUT / "e84_structural_margin_q2s3_safety_recombination_summary.csv"
REPORT_OUT = OUT / "e84_structural_margin_q2s3_safety_recombination_report.md"

STRUCT_LIMIT = 18
Q_LIMIT = 12
STRUCT_WEIGHTS = [0.50, 0.75, 1.00]
Q_WEIGHTS = [0.75, 1.00, 1.25, 1.50]
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), e83.EPS, 1.0 - e83.EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def pred_hash(tag: str) -> str:
    return str(tag).split("_")[-1]


def select_pools(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    evaluated = scan[scan["nonanchor_evaluated"].fillna(False).astype(bool)].copy()
    evaluated["pred_hash"] = evaluated["tag"].map(pred_hash)

    struct_pool = evaluated[
        evaluated["structural_loose_gate"].fillna(False).astype(bool)
        & evaluated["target_scope"].eq("non_q2s3")
        & evaluated["all_delta_vs_mixmin"].lt(-1.0e-5)
        & evaluated["hidden_core_minus_base"].lt(0.0)
        & evaluated["world_support_minus_base"].le(0.0)
        & evaluated["raw_energy_q_p90_minus_base"].le(0.0)
    ].copy()
    struct_pool = (
        struct_pool.sort_values(
            ["sets_beating_base", "sets_tail_neutral", "all_delta_vs_mixmin"],
            ascending=[False, False, True],
        )
        .drop_duplicates("pred_hash")
        .head(STRUCT_LIMIT)
        .reset_index(drop=True)
    )

    q_pool = evaluated[
        evaluated["loose_gate"].fillna(False).astype(bool)
        & evaluated["source_file"].eq("submission_e72_topabs50_q2s3_gate_4e48cba2.csv")
        & evaluated["target_scope"].isin(["q2s3", "all", "s_all", "q3_s2_s3_s4"])
        & evaluated["hidden_q2s3_mean_minus_base"].lt(0.0)
        & evaluated["world_support_minus_base"].le(0.0)
    ].copy()
    q_pool = (
        q_pool.sort_values(["sets_beating_base", "sets_tail_neutral", "all_delta_vs_mixmin"], ascending=[False, False, True])
        .drop_duplicates("pred_hash")
        .head(Q_LIMIT)
        .reset_index(drop=True)
    )
    return struct_pool, q_pool


def reconstruct_e83_state() -> tuple[
    pd.DataFrame,
    np.ndarray,
    np.ndarray,
    pd.DataFrame,
    dict[str, np.ndarray],
    e55.BaseState,
    pd.DataFrame,
    list[np.ndarray],
]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    energy, _energy_summary = e83.build_e82_energy(sample, mixmin, raw_prior, views, components)
    source_files = e83.sorted_existing_candidate_files()
    e83_rows, e83_preds = e83.build_structural_candidates(source_files, sample, mixmin, energy)
    return sample, mixmin, labels, worlds, views, state, e83_rows, e83_preds


def build_recombined_candidates(
    struct_pool: pd.DataFrame,
    q_pool: pd.DataFrame,
    e83_rows: pd.DataFrame,
    e83_preds: list[np.ndarray],
    mixmin: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    row_by_tag = e83_rows.set_index("tag")["pred_index"].astype(int).to_dict()
    mix_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {e83.stable_tag(mixmin, "e84_mixmin_"): 0}

    for srec in struct_pool.to_dict("records"):
        spred = e83_preds[row_by_tag[str(srec["tag"])]]
        sdelta = logit(spred) - mix_logit
        for qrec in q_pool.to_dict("records"):
            qpred = e83_preds[row_by_tag[str(qrec["tag"])]]
            qdelta = np.zeros_like(sdelta)
            qdelta[:, QS_IDXS] = (logit(qpred) - mix_logit)[:, QS_IDXS]
            for sw in STRUCT_WEIGHTS:
                for qw in Q_WEIGHTS:
                    pred = clip_prob(sigmoid(mix_logit + float(sw) * sdelta + float(qw) * qdelta))
                    tag = e83.stable_tag(pred, f"e84_sw{sw:.2f}_qw{qw:.2f}_")
                    if tag in seen:
                        continue
                    pred_index = len(preds)
                    seen[tag] = pred_index
                    preds.append(pred)
                    delta = logit(pred) - mix_logit
                    rows.append(
                        {
                            "pred_index": pred_index,
                            "base_index": 0,
                            "tag": tag,
                            "struct_tag": str(srec["tag"]),
                            "struct_source_file": str(srec["source_file"]),
                            "struct_row_gate": str(srec["row_gate"]),
                            "struct_scale": float(srec["scale"]),
                            "struct_all_delta": float(srec["all_delta_vs_mixmin"]),
                            "struct_sets_beating_base": int(srec["sets_beating_base"]),
                            "struct_sets_tail_neutral": int(srec["sets_tail_neutral"]),
                            "q_tag": str(qrec["tag"]),
                            "q_row_gate": str(qrec["row_gate"]),
                            "q_target_scope": str(qrec["target_scope"]),
                            "q_scale": float(qrec["scale"]),
                            "q_all_delta": float(qrec["all_delta_vs_mixmin"]),
                            "struct_weight": float(sw),
                            "q_weight": float(qw),
                            "mean_abs_logit_move_raw": float(np.abs(delta).mean()),
                            "mean_abs_q2s3_logit_move_raw": float(np.abs(delta[:, QS_IDXS]).mean()),
                            "active_cells": int((np.abs(delta) > 1.0e-12).sum()),
                            "active_rows": int((np.abs(delta) > 1.0e-12).any(axis=1).sum()),
                        }
                    )
    return pd.DataFrame(rows), preds


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in scan.groupby(["struct_weight", "q_weight", "q_target_scope"], dropna=False):
        sw, qw, q_scope = keys
        evaluated = group[group["nonanchor_evaluated"]]
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        best_eval = evaluated.sort_values("all_delta_vs_mixmin").head(1)
        rows.append(
            {
                "struct_weight": float(sw),
                "q_weight": float(qw),
                "q_target_scope": q_scope,
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
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min()) if len(evaluated) else np.nan,
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["deployable", "strict", "structural_strict", "loose", "best_eval_all_delta_vs_mixmin"],
        ascending=[False, False, False, False, True],
    )


def write_submission(sample: pd.DataFrame, pred: np.ndarray, tag: str, prefix: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"{prefix}_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    struct_pool: pd.DataFrame,
    q_pool: pd.DataFrame,
    submission_path: Path | None,
    sensor_path: Path | None,
) -> None:
    evaluated = scan[scan["nonanchor_evaluated"]].copy()
    cols = [
        "struct_source_file",
        "struct_weight",
        "q_weight",
        "q_target_scope",
        "all_delta_vs_mixmin",
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
        "structural_strict_gate",
        "structural_loose_gate",
        "tag",
    ]
    lines = [
        "# E84 Structural Margin + Q2/S3 Safety Recombination",
        "",
        "## Observe",
        "",
        "E83 produced margin in non-Q2S3 structural movements and Q2/S3 safety in E72-derived movements, but no single row carried both.",
        "",
        "## Wonder",
        "",
        "Can the two movements be combined without reintroducing the E73 all-target public failure?",
        "",
        "## Method",
        "",
        "- Select E83 structural-loose `non_q2s3` rows with margin-scale combo deltas and nonworse world/raw-energy stress.",
        "- Select E83 E72-derived loose Q2/S3-safe rows.",
        "- Add structural deltas outside Q2/S3 and only Q2/S3 deltas from the safety rows.",
        "- Sweep conservative structural and Q2/S3 weights, then run the same combo and nonanchor stress.",
        "",
        "## Selected Structural Pool",
        "",
        e56.markdown_table(
            struct_pool[
                [
                    "source_file",
                    "row_gate",
                    "scale",
                    "all_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_core_minus_base",
                    "world_support_minus_base",
                    "tag",
                ]
            ]
        ),
        "",
        "## Selected Q2/S3 Safety Pool",
        "",
        e56.markdown_table(
            q_pool[
                [
                    "row_gate",
                    "target_scope",
                    "scale",
                    "all_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "tag",
                ]
            ]
        ),
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(50)),
        "",
        "## Strict Rows",
        "",
        e56.markdown_table(evaluated[evaluated["strict_gate"]].sort_values("all_delta_vs_mixmin")[cols].head(30))
        if evaluated["strict_gate"].any()
        else "None.",
        "",
        "## Loose Rows",
        "",
        e56.markdown_table(evaluated[evaluated["loose_gate"]].sort_values("all_delta_vs_mixmin")[cols].head(30))
        if evaluated["loose_gate"].any()
        else "None.",
        "",
        "## Best Evaluated Rows",
        "",
        e56.markdown_table(evaluated.sort_values("all_delta_vs_mixmin")[cols].head(40)),
        "",
        "## Decision",
        "",
    ]
    if submission_path is not None:
        lines += [
            f"Materialized best strict candidate: `{submission_path.name}`.",
            "",
            "This file bets that the remaining plateau is an additive target-block conflict: structural margin outside Q2/S3 plus a separate Q2/S3 safety correction.",
        ]
    else:
        lines += [
            "No strict/deployable recombination survived.",
            "",
            "The additive decomposition is therefore not enough for a safe candidate; the conflict is likely row/block-specific rather than separable by target group.",
        ]
        if sensor_path is not None:
            lines += [
                "",
                f"Materialized a diagnostic inverse-top sensor only: `{sensor_path.name}`.",
                "",
                "This is not a deployable-safe recommendation. It tests whether the public subset behaves like the inverse-top combo set that rejects every otherwise-healthy E84 candidate.",
            ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not e83.SCAN_OUT.exists():
        raise FileNotFoundError(e83.SCAN_OUT)
    e83_scan = pd.read_csv(e83.SCAN_OUT)
    struct_pool, q_pool = select_pools(e83_scan)
    if struct_pool.empty or q_pool.empty:
        raise RuntimeError(f"empty pools: struct={len(struct_pool)} q={len(q_pool)}")

    sample, mixmin, labels, worlds, views, state, e83_rows, e83_preds = reconstruct_e83_state()
    rows, preds = build_recombined_candidates(struct_pool, q_pool, e83_rows, e83_preds, mixmin)
    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary = summarize(scan)

    submission_path: Path | None = None
    sensor_path: Path | None = None
    strict = scan[scan["strict_gate"]].sort_values("all_delta_vs_mixmin")
    if len(strict):
        best = strict.iloc[0]
        submission_path = write_submission(
            sample,
            preds[int(best["pred_index"])],
            str(best["tag"]),
            "submission_e84_struct_q2s3_recombo",
        )
        scan["materialized_submission"] = scan["tag"].eq(str(best["tag"]))
    else:
        scan["materialized_submission"] = False
        sensor = scan[
            scan["nonanchor_evaluated"].fillna(False).astype(bool)
            & scan["all_margin_vs_mixmin"].fillna(False).astype(bool)
            & scan["hidden_q2s3_beats_base"].fillna(False).astype(bool)
            & scan["world_nonworse"].fillna(False).astype(bool)
            & scan["block_majority_beats"].fillna(False).astype(bool)
            & scan["block_tail_safe"].fillna(False).astype(bool)
            & scan["structural_raw_energy_nonworse"].fillna(False).astype(bool)
            & scan["sets_beating_base"].eq(2)
            & scan["sets_tail_neutral"].eq(2)
        ].sort_values("all_delta_vs_mixmin")
        if len(sensor):
            best_sensor = sensor.iloc[0]
            sensor_path = write_submission(
                sample,
                preds[int(best_sensor["pred_index"])],
                str(best_sensor["tag"]),
                "submission_e84_inverse_sensor",
            )
            scan["materialized_sensor"] = scan["tag"].eq(str(best_sensor["tag"]))
        else:
            scan["materialized_sensor"] = False

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, struct_pool, q_pool, submission_path, sensor_path)
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
            "sensor_submission": str(sensor_path) if sensor_path is not None else None,
        }
    )


if __name__ == "__main__":
    main()
