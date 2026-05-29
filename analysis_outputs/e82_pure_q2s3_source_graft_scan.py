#!/usr/bin/env python3
"""E82 pure mixmin-anchored Q2/S3 source-graft scan.

E81 showed that the submitted E73 file was broad all-target movement and that
the isolated final-file Q2/S3 values are locally real but sub-margin. This
probe asks the next sharper question:

Can the larger E72/E75/E76 Q2/S3 source universe produce a margin-scale
candidate if every non-Q2/S3 base movement is removed and only Q2/S3 structure
is grafted onto mixmin?

Two grafts are separated:
- value graft: copy source final Q2/S3 probabilities onto mixmin.
- delta graft: add source candidate-vs-source-base Q2/S3 logit movement to
  mixmin.

No submission is written unless a pure mixmin-anchored graft survives the
existing strict/deployable combo, hidden, world, and block stress.
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
import q2_s3_target_amplitude_ridge_probe as e75  # noqa: E402
import q2_s3_target_amplitude_stability_probe as e76  # noqa: E402
import q2_s3_unified_gate_geometry_probe as e72  # noqa: E402
import q2_s3_unified_strict_cell_consensus_probe as e71  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "e82_pure_q2s3_source_graft_scan.csv"
SUMMARY_OUT = OUT / "e82_pure_q2s3_source_graft_summary.csv"
SOURCE_SUMMARY_OUT = OUT / "e82_pure_q2s3_source_graft_source_summary.csv"
REPORT_OUT = OUT / "e82_pure_q2s3_source_graft_report.md"

EPS = 1.0e-6
MAX_E72_TOP = 500
Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]
TARGET_SCOPES = {
    "q2s3": QS_IDXS,
    "q2_only": [Q2_IDX],
    "s3_only": [S3_IDX],
}


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def stable_tag(pred: np.ndarray, prefix: str) -> str:
    return e72.e68_tag(pred, prefix)


def bool_col(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame:
        return pd.Series(False, index=frame.index)
    return frame[col].fillna(False).astype(bool)


def select_e72_rows(rows: pd.DataFrame) -> pd.DataFrame:
    scan = pd.read_csv(e72.SCAN_OUT)
    keep_cols = [
        "tag",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "worst_set_delta_vs_mixmin",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "strict_gate",
        "deployable_gate",
        "loose_gate",
    ]
    merged = rows.merge(scan[keep_cols], on="tag", how="left", suffixes=("", "_source"))
    selected_parts = [
        merged[bool_col(merged, "deployable_gate")],
        merged[bool_col(merged, "loose_gate")],
        merged.nsmallest(MAX_E72_TOP, "all_delta_vs_mixmin"),
        merged.nsmallest(MAX_E72_TOP, "hidden_q2s3_mean_minus_base"),
        merged.nsmallest(MAX_E72_TOP, "world_support_minus_base"),
    ]
    selected = pd.concat(selected_parts, ignore_index=False).drop_duplicates("tag")
    return selected.reset_index(drop=True)


def select_e75_rows(rows: pd.DataFrame) -> pd.DataFrame:
    scan = pd.read_csv(e75.SCAN_OUT)
    keep_cols = [
        "tag",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "worst_set_delta_vs_mixmin",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "strict_gate",
        "deployable_gate",
        "loose_gate",
        "dominant_axis",
    ]
    return rows.merge(scan[keep_cols], on="tag", how="left", suffixes=("", "_source")).reset_index(drop=True)


def select_e76_rows(rows: pd.DataFrame) -> pd.DataFrame:
    scan = pd.read_csv(e76.SCAN_OUT)
    keep_cols = [
        "tag",
        "all_delta_vs_mixmin",
        "all_minus_base",
        "worst_set_delta_vs_mixmin",
        "sets_beating_base",
        "sets_tail_neutral",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "strict_gate",
        "deployable_gate",
        "loose_gate",
        "pair_name",
        "dominant_axis",
        "variant_kind",
        "variant_name",
    ]
    merged = rows.merge(scan[keep_cols], on="tag", how="left", suffixes=("", "_source"))
    keep = (
        bool_col(merged, "deployable_gate")
        | bool_col(merged, "loose_gate")
        | merged["pair_name"].isin(["sym16_e73", "sym20_e74", "asym8_28_e75"])
    )
    return merged[keep].drop_duplicates("tag").reset_index(drop=True)


def graft_value(mixmin: np.ndarray, source_pred: np.ndarray, scope: list[int]) -> np.ndarray:
    out = mixmin.copy()
    out[:, scope] = source_pred[:, scope]
    return clip_prob(out)


def graft_delta(
    mixmin: np.ndarray,
    source_base: np.ndarray,
    source_pred: np.ndarray,
    scope: list[int],
) -> np.ndarray:
    out_logit = logit(mixmin)
    move = logit(source_pred) - logit(source_base)
    out_logit[:, scope] = out_logit[:, scope] + move[:, scope]
    return clip_prob(sigmoid(out_logit))


def movement_summary(pred: np.ndarray, mixmin: np.ndarray, scope: list[int]) -> dict[str, Any]:
    delta = logit(pred) - logit(mixmin)
    moved = np.abs(delta) > 1.0e-12
    return {
        "active_cells": int(moved.sum()),
        "active_rows": int(moved.any(axis=1).sum()),
        "q2_cells": int(moved[:, Q2_IDX].sum()),
        "s3_cells": int(moved[:, S3_IDX].sum()),
        "active_scope_cells": int(moved[:, scope].sum()),
        "mean_abs_q2s3_logit_move_raw": float(np.abs(delta[:, QS_IDXS]).mean()),
        "max_abs_q2s3_logit_move_raw": float(np.abs(delta[:, QS_IDXS]).max()),
    }


def add_graft_rows(
    out_rows: list[dict[str, Any]],
    out_preds: list[np.ndarray],
    seen: dict[str, int],
    source_name: str,
    source_rows: pd.DataFrame,
    source_preds: list[np.ndarray],
    mixmin: np.ndarray,
) -> None:
    for rec in source_rows.to_dict("records"):
        pred_index = int(rec["pred_index"])
        base_index = int(rec["base_index"])
        source_pred = source_preds[pred_index]
        source_base = source_preds[base_index]
        for graft_mode in ["delta_graft", "value_graft"]:
            for target_scope, scope in TARGET_SCOPES.items():
                if graft_mode == "delta_graft":
                    pred = graft_delta(mixmin, source_base, source_pred, scope)
                else:
                    pred = graft_value(mixmin, source_pred, scope)
                if np.abs(logit(pred) - logit(mixmin)).mean() <= 1.0e-12:
                    continue
                tag = stable_tag(pred, f"e82_{source_name}_{graft_mode}_{target_scope}_")
                if tag in seen:
                    continue
                candidate_index = len(out_preds)
                seen[tag] = candidate_index
                out_preds.append(pred)
                move = movement_summary(pred, mixmin, scope)
                out_rows.append(
                    {
                        "pred_index": candidate_index,
                        "base_index": 0,
                        "tag": tag,
                        "source": source_name,
                        "source_tag": str(rec["tag"]),
                        "source_pred_index": pred_index,
                        "source_base_index": base_index,
                        "graft_mode": graft_mode,
                        "target_scope": target_scope,
                        "pool": str(rec.get("pool", "")),
                        "gate": str(rec.get("gate", "")),
                        "alpha": float(rec.get("alpha", np.nan)),
                        "alpha_q2": float(rec.get("alpha_q2", np.nan)),
                        "alpha_s3": float(rec.get("alpha_s3", np.nan)),
                        "pair_name": str(rec.get("pair_name", "")),
                        "dominant_axis": str(rec.get("dominant_axis", "")),
                        "variant_kind": str(rec.get("variant_kind", "")),
                        "variant_name": str(rec.get("variant_name", "")),
                        "source_all_delta": float(rec.get("all_delta_vs_mixmin", np.nan)),
                        "source_all_minus_base": float(rec.get("all_minus_base", np.nan)),
                        "source_worst_set_delta": float(rec.get("worst_set_delta_vs_mixmin", np.nan)),
                        "source_sets_beating_base": float(rec.get("sets_beating_base", np.nan)),
                        "source_sets_tail_neutral": float(rec.get("sets_tail_neutral", np.nan)),
                        "source_hidden_q2s3": float(rec.get("hidden_q2s3_mean_minus_base", np.nan)),
                        "source_world": float(rec.get("world_support_minus_base", np.nan)),
                        "source_block_win": float(rec.get("block_q2s3_beats_base_rate", np.nan)),
                        "source_strict": bool(rec.get("strict_gate", False)),
                        "source_deployable": bool(rec.get("deployable_gate", False)),
                        "source_loose": bool(rec.get("loose_gate", False)),
                        **move,
                    }
                )


def build_source_universe(
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    raw_prior: np.ndarray,
    views: dict[str, np.ndarray],
    components: dict[str, dict[str, np.ndarray]],
) -> tuple[pd.DataFrame, list[np.ndarray], pd.DataFrame]:
    strict = e69.strict_rows()
    cells = e71.unique_strict_cells(strict)
    bases, _cands, deltas = e71.reconstruct_unified_arrays(cells, sample, mixmin, raw_prior, views, components)

    e72_rows, e72_preds = e72.build_adaptive_candidates(cells, bases, deltas)
    e72_rows = select_e72_rows(e72_rows)

    e75_rows, e75_preds, _meta = e75.build_target_alpha_candidates(cells, bases, deltas)
    e75_rows = select_e75_rows(e75_rows)

    e76_rows, e76_preds, _variants = e76.build_target_stability_candidates(cells, bases, deltas)
    e76_rows = select_e76_rows(e76_rows)

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen: dict[str, int] = {stable_tag(mixmin, "e82_mixmin_"): 0}
    add_graft_rows(rows, preds, seen, "e72", e72_rows, e72_preds, mixmin)
    add_graft_rows(rows, preds, seen, "e75", e75_rows, e75_preds, mixmin)
    add_graft_rows(rows, preds, seen, "e76", e76_rows, e76_preds, mixmin)
    source_summary = pd.DataFrame(
        [
            {"source": "e72", "source_rows": len(e72_rows), "source_preds": len(e72_preds)},
            {"source": "e75", "source_rows": len(e75_rows), "source_preds": len(e75_preds)},
            {"source": "e76", "source_rows": len(e76_rows), "source_preds": len(e76_preds)},
        ]
    )
    return pd.DataFrame(rows), preds, source_summary


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
    return scan.sort_values(
        ["deployable_gate", "strict_gate", "loose_gate", "all_delta_vs_mixmin"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def summarize(scan: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for keys, group in scan.groupby(["source", "graft_mode", "target_scope"], dropna=False):
        source, graft_mode, target_scope = keys
        evaluated = group[group["nonanchor_evaluated"]]
        deploy = evaluated[evaluated["deployable_gate"]]
        loose = evaluated[evaluated["loose_gate"]]
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        best_eval = evaluated.sort_values("all_delta_vs_mixmin").head(1)
        rows.append(
            {
                "source": source,
                "graft_mode": graft_mode,
                "target_scope": target_scope,
                "rows": int(len(group)),
                "nonanchor_evaluated": int(len(evaluated)),
                "strict": int(evaluated["strict_gate"].sum()) if len(evaluated) else 0,
                "deployable": int(evaluated["deployable_gate"].sum()) if len(evaluated) else 0,
                "loose": int(evaluated["loose_gate"].sum()) if len(evaluated) else 0,
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_eval_all_delta_vs_mixmin": float(best_eval["all_delta_vs_mixmin"].iloc[0])
                if len(best_eval)
                else np.nan,
                "best_deployable_all_delta": float(deploy["all_delta_vs_mixmin"].min()) if len(deploy) else np.nan,
                "best_loose_all_delta": float(loose["all_delta_vs_mixmin"].min()) if len(loose) else np.nan,
                "best_hidden_q2s3": float(evaluated["hidden_q2s3_mean_minus_base"].min()) if len(evaluated) else np.nan,
                "best_world": float(evaluated["world_support_minus_base"].min()) if len(evaluated) else np.nan,
                "best_block_win": float(evaluated["block_q2s3_beats_base_rate"].max()) if len(evaluated) else np.nan,
            }
        )
    summary = pd.DataFrame(rows).sort_values(
        ["deployable", "loose", "best_eval_all_delta_vs_mixmin"],
        ascending=[False, False, True],
    )
    source = (
        scan.groupby("source")
        .agg(
            rows=("tag", "size"),
            nonanchor_evaluated=("nonanchor_evaluated", "sum"),
            strict=("strict_gate", "sum"),
            deployable=("deployable_gate", "sum"),
            loose=("loose_gate", "sum"),
            best_all=("all_delta_vs_mixmin", "min"),
            best_eval_all=("all_delta_vs_mixmin", lambda s: float(scan.loc[s.index][scan.loc[s.index, "nonanchor_evaluated"]]["all_delta_vs_mixmin"].min())),
        )
        .reset_index()
    )
    return summary, source


def write_submission(sample: pd.DataFrame, pred: np.ndarray, tag: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"submission_e82_pure_q2s3_graft_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def write_report(
    scan: pd.DataFrame,
    summary: pd.DataFrame,
    source_summary: pd.DataFrame,
    submission_path: Path | None,
) -> None:
    evaluated = scan[scan["nonanchor_evaluated"]].copy()
    best = evaluated.sort_values("all_delta_vs_mixmin").head(40)
    deploy = evaluated[evaluated["deployable_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    loose = evaluated[evaluated["loose_gate"]].sort_values("all_delta_vs_mixmin").head(30)
    lines = [
        "# E82 Pure Q2/S3 Source-Graft Scan",
        "",
        "## Observe",
        "",
        "E81 rejected direct E73/E74/E75 follow-up because the submitted E73 file moved all seven targets, while isolated final-file Q2/S3 was only sub-margin.",
        "",
        "## Wonder",
        "",
        "Does the broader E72/E75/E76 source universe contain a pure mixmin-anchored Q2/S3 movement that survives combo-tail stress once non-Q2/S3 base movement is removed?",
        "",
        "## Method",
        "",
        "- Reconstruct E72 adaptive gate rows, E75 target-ridge rows, and E76 subset-stability rows.",
        "- For each source row, build both value graft and delta graft variants over Q2/S3, Q2-only, and S3-only.",
        "- Score all rows on combo sets first, then run non-anchor hidden/world/block stress only on the combo-promising subset.",
        "",
        "## Source Universe",
        "",
        e56.markdown_table(source_summary),
        "",
        "## Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Best Evaluated Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "source",
                    "graft_mode",
                    "target_scope",
                    "pool",
                    "gate",
                    "pair_name",
                    "variant_kind",
                    "variant_name",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "worst_set_delta_vs_mixmin",
                    "sets_beating_base",
                    "sets_tail_neutral",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_gate",
                    "deployable_gate",
                    "loose_gate",
                    "tag",
                ]
            ]
        ),
        "",
        "## Deployable Rows",
        "",
        e56.markdown_table(
            deploy[
                [
                    "source",
                    "graft_mode",
                    "target_scope",
                    "pair_name",
                    "variant_kind",
                    "variant_name",
                    "all_delta_vs_mixmin",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "tag",
                ]
            ]
        )
        if len(deploy)
        else "_None._",
        "",
        "## Loose Rows",
        "",
        e56.markdown_table(
            loose[
                [
                    "source",
                    "graft_mode",
                    "target_scope",
                    "pair_name",
                    "variant_kind",
                    "variant_name",
                    "all_delta_vs_mixmin",
                    "worst_set_delta_vs_mixmin",
                    "hidden_q2s3_mean_minus_base",
                    "world_support_minus_base",
                    "block_q2s3_beats_base_rate",
                    "tag",
                ]
            ]
        )
        if len(loose)
        else "_None._",
        "",
        "## Decision",
        "",
    ]
    if submission_path is not None:
        lines.append(f"- A strict/deployable pure graft survived; materialized `{submission_path.relative_to(ROOT)}` as the next diagnostic candidate.")
    else:
        lines.append("- No pure source graft survived strict/deployable stress. The Q2/S3 latent remains useful energy but not a submission source.")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{SOURCE_SUMMARY_OUT.relative_to(ROOT)}`",
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

    rows, preds, source_summary = build_source_universe(sample, mixmin, raw_prior, views, components)
    print(f"built pure graft rows={len(rows)} unique_preds={len(preds)}", flush=True)
    scan = score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    summary, source_rollup = summarize(scan)
    source_summary = source_summary.merge(source_rollup, on="source", how="left")

    submission_path: Path | None = None
    deploy = scan[scan["deployable_gate"]].sort_values("all_delta_vs_mixmin")
    if len(deploy):
        best = deploy.iloc[0]
        submission_path = write_submission(sample, preds[int(best["pred_index"])], str(best["tag"]))

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    source_summary.to_csv(SOURCE_SUMMARY_OUT, index=False)
    write_report(scan, summary, source_summary, submission_path)

    print(
        f"rows={len(scan)} evaluated={int(scan['nonanchor_evaluated'].sum())} "
        f"strict={int(scan['strict_gate'].sum())} deployable={int(scan['deployable_gate'].sum())} "
        f"loose={int(scan['loose_gate'].sum())} best_eval={scan[scan['nonanchor_evaluated']]['all_delta_vs_mixmin'].min():.6g} "
        f"submission={submission_path.relative_to(ROOT) if submission_path is not None else 'none'}",
        flush=True,
    )
    print(summary.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
