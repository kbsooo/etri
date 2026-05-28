#!/usr/bin/env python3
"""E69 amplitude stress for independently validated Q2/S3 tail-gated cells.

E68 showed that many E67 Q2/S3 tail-gated cells survive held-out combo
construction plus hidden/world/block stress. The remaining question is whether
those independently validated cells can be amplified into selector-scale
probability movement, or whether they behave like E64 and break as soon as the
move leaves the tiny local neighborhood.

This script only scales the Q2/S3 logit delta between each E68 strict candidate
and its matched `no_q2_s3` base. Non-Q2/S3 targets are held fixed at the base.
No submission is written.
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
from public_lb_actual_anchor_ranker import COMBO_TABLES  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_tail_gate_independence_probe as e68  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


PAIR_IN = OUT / "q2_s3_tail_gate_independence_probe_pair.csv"
SCAN_OUT = OUT / "q2_s3_strict_cell_amplitude_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_strict_cell_amplitude_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_strict_cell_amplitude_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
EPS = 1e-6
ANCHOR_MARGIN = 1.0e-5
ALPHAS = [0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 24.0]

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def strict_rows() -> pd.DataFrame:
    pair = pd.read_csv(PAIR_IN)
    strict = pair[pair["strict_independent_gate"]].copy()
    if strict.empty:
        raise RuntimeError("E68 strict rows are empty; run E68 first")
    strict = strict.sort_values(["heldout_minus_base", "hidden_q2s3_mean_minus_base"]).reset_index(drop=True)
    strict["strict_pair_id"] = np.arange(len(strict), dtype=int)
    return strict


def amplified_predictions(
    strict: pd.DataFrame,
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}
    for heldout_set, group in strict.groupby("heldout_set", sort=False):
        train_sets = [name for name in COMBO_TABLES if name != heldout_set]
        gradients, gradient_weights = e68.anchor_gradient_for_sets(
            e68.load_sub(A2C8).sort_values(KEYS).reset_index(drop=True),
            mixmin,
            train_sets,
        )
        for rec in group.to_dict("records"):
            spec = pd.Series(rec)
            base = e68.pred_from_config(spec, "no_q2_s3", components, raw_prior, mixmin, views, gradients, gradient_weights)
            cand = e68.pred_from_config(
                spec, str(rec["translator"]), components, raw_prior, mixmin, views, gradients, gradient_weights
            )
            base_logit = logit(base)
            q_delta = np.zeros_like(base_logit)
            q_delta[:, QS_IDXS] = logit(cand)[:, QS_IDXS] - base_logit[:, QS_IDXS]
            for alpha in ALPHAS:
                pred = clip_prob(sigmoid(base_logit + float(alpha) * q_delta))
                tag = e68.e67.stable_tag(pred, prefix=f"e69_a{alpha:.2f}_")
                if tag in seen:
                    pred_index = seen[tag]
                else:
                    pred_index = len(preds)
                    seen[tag] = pred_index
                    preds.append(pred)
                rows.append(
                    {
                        "pred_index": pred_index,
                        "tag": tag,
                        "strict_pair_id": int(rec["strict_pair_id"]),
                        "heldout_set": heldout_set,
                        "translator": rec["translator"],
                        "alpha": float(alpha),
                        **{c: rec[c] for c in e68.candidate_key_cols()},
                        "e68_heldout_minus_base": rec["heldout_minus_base"],
                        "e68_train_minus_base": rec["train_minus_base"],
                        "e68_world_support_minus_base": rec["world_support_minus_base"],
                        "e68_hidden_q2s3_mean_minus_base": rec["hidden_q2s3_mean_minus_base"],
                        "e68_block_q2s3_beats_base_rate": rec["block_q2s3_beats_base_rate"],
                    }
                )
    return pd.DataFrame(rows), preds


def add_combo_scores(rows: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    all_frame = e68.combo_set_score(preds, sample, list(COMBO_TABLES)).set_index("candidate_index")
    heldout_frames = {
        name: e68.combo_set_score(preds, sample, [name]).set_index("candidate_index") for name in COMBO_TABLES
    }
    train_frames = {
        name: e68.combo_set_score(preds, sample, [other for other in COMBO_TABLES if other != name]).set_index(
            "candidate_index"
        )
        for name in COMBO_TABLES
    }
    grouped = out[out["alpha"].eq(0.0)][["strict_pair_id", "pred_index"]].rename(columns={"pred_index": "base_index"})
    grouped = grouped.merge(
        out[out["alpha"].eq(1.0)][["strict_pair_id", "pred_index"]].rename(columns={"pred_index": "alpha1_index"}),
        on="strict_pair_id",
        how="left",
    )
    base_lookup = grouped.set_index("strict_pair_id")[["base_index", "alpha1_index"]].to_dict("index")

    metric_rows: list[dict[str, Any]] = []
    mix_ref = 0
    # The caller prepends mixmin to preds before scoring.
    for rec in out.to_dict("records"):
        idx = int(rec["pred_index"]) + 1
        base_idx = int(base_lookup[int(rec["strict_pair_id"])]["base_index"]) + 1
        alpha1_idx = int(base_lookup[int(rec["strict_pair_id"])]["alpha1_index"]) + 1
        heldout_set = str(rec["heldout_set"])
        metrics: dict[str, Any] = {}
        for split, frame in [
            ("heldout", heldout_frames[heldout_set]),
            ("train", train_frames[heldout_set]),
            ("all", all_frame),
        ]:
            cand_score = float(frame.loc[idx, "score"] - frame.loc[mix_ref, "score"])
            base_score = float(frame.loc[base_idx, "score"] - frame.loc[mix_ref, "score"])
            alpha1_score = float(frame.loc[alpha1_idx, "score"] - frame.loc[mix_ref, "score"])
            cand_worst = float(frame.loc[idx, "worst"] - frame.loc[mix_ref, "worst"])
            base_worst = float(frame.loc[base_idx, "worst"] - frame.loc[mix_ref, "worst"])
            metrics[f"{split}_delta_vs_mixmin"] = cand_score
            metrics[f"{split}_minus_base"] = cand_score - base_score
            metrics[f"{split}_minus_alpha1"] = cand_score - alpha1_score
            metrics[f"{split}_worst_minus_base"] = cand_worst - base_worst
        metric_rows.append(metrics)
    return pd.concat([out.reset_index(drop=True), pd.DataFrame(metric_rows)], axis=1)


def add_nonanchor_scores(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> pd.DataFrame:
    stats = [e68.score_prediction(str(i), pred, mixmin, labels, worlds, views, state) for i, pred in enumerate(preds)]
    out = rows.copy()
    base_rows = out[out["alpha"].eq(0.0)][["strict_pair_id", "pred_index"]].rename(columns={"pred_index": "base_index"})
    alpha1_rows = out[out["alpha"].eq(1.0)][["strict_pair_id", "pred_index"]].rename(
        columns={"pred_index": "alpha1_index"}
    )
    lookup = base_rows.merge(alpha1_rows, on="strict_pair_id", how="left").set_index("strict_pair_id").to_dict("index")
    metric_rows: list[dict[str, Any]] = []
    for rec in out.to_dict("records"):
        idx = int(rec["pred_index"])
        base_idx = int(lookup[int(rec["strict_pair_id"])]["base_index"])
        alpha1_idx = int(lookup[int(rec["strict_pair_id"])]["alpha1_index"])
        cur = stats[idx]
        base = stats[base_idx]
        alpha1 = stats[alpha1_idx]
        block_minus_base = cur["_block_vector"] - base["_block_vector"]
        block_minus_alpha1 = cur["_block_vector"] - alpha1["_block_vector"]
        metric_rows.append(
            {
                "world_support_minus_base": float(cur["world_support_score"] - base["world_support_score"]),
                "world_support_minus_alpha1": float(cur["world_support_score"] - alpha1["world_support_score"]),
                "raw_energy_q_p90_minus_base": float(
                    cur["raw_energy_quarter_p90_delta"] - base["raw_energy_quarter_p90_delta"]
                ),
                "hidden_core_minus_base": float(cur["hidden_core_mean_delta"] - base["hidden_core_mean_delta"]),
                "hidden_q2_minus_base": float(cur["hidden_core_delta_Q2"] - base["hidden_core_delta_Q2"]),
                "hidden_s3_minus_base": float(cur["hidden_core_delta_S3"] - base["hidden_core_delta_S3"]),
                "hidden_q2s3_mean_minus_base": float(
                    0.5
                    * (
                        cur["hidden_core_delta_Q2"]
                        - base["hidden_core_delta_Q2"]
                        + cur["hidden_core_delta_S3"]
                        - base["hidden_core_delta_S3"]
                    )
                ),
                "hidden_q2s3_mean_minus_alpha1": float(
                    0.5
                    * (
                        cur["hidden_core_delta_Q2"]
                        - alpha1["hidden_core_delta_Q2"]
                        + cur["hidden_core_delta_S3"]
                        - alpha1["hidden_core_delta_S3"]
                    )
                ),
                "block_q2s3_mean_minus_base": float(block_minus_base.mean()),
                "block_q2s3_max_minus_base": float(block_minus_base.max()),
                "block_q2s3_beats_base_rate": float((block_minus_base < 0.0).mean()),
                "block_q2s3_tail_safe_rate": float((block_minus_base <= 1.0e-8).mean()),
                "block_q2s3_mean_minus_alpha1": float(block_minus_alpha1.mean()),
                "block_q2s3_max_minus_alpha1": float(block_minus_alpha1.max()),
                "block_q2s3_beats_alpha1_rate": float((block_minus_alpha1 < 0.0).mean()),
            }
        )
    return pd.concat([out.reset_index(drop=True), pd.DataFrame(metric_rows)], axis=1)


def add_gates(rows: pd.DataFrame, preds: list[np.ndarray], mixmin: np.ndarray) -> pd.DataFrame:
    out = rows.copy()
    mean_abs_moves = []
    q2s3_moves = []
    mix_logit = logit(mixmin)
    for pred in preds:
        delta = logit(pred) - mix_logit
        mean_abs_moves.append(float(np.abs(delta).mean()))
        q2s3_moves.append(float(np.abs(delta[:, QS_IDXS]).mean()))
    move_frame = pd.DataFrame(
        {
            "pred_index": np.arange(len(preds), dtype=int),
            "mean_abs_logit_move_vs_mixmin": mean_abs_moves,
            "mean_abs_q2s3_logit_move_vs_mixmin": q2s3_moves,
        }
    )
    out = out.merge(move_frame, on="pred_index", how="left")
    out["heldout_beats_base"] = out["heldout_minus_base"] < 0.0
    out["heldout_tail_neutral"] = out["heldout_worst_minus_base"] <= 0.0
    out["train_beats_base"] = out["train_minus_base"] < 0.0
    out["all_beats_base"] = out["all_minus_base"] < 0.0
    out["all_margin_vs_mixmin"] = out["all_delta_vs_mixmin"] < -ANCHOR_MARGIN
    out["hidden_q2s3_beats_base"] = out["hidden_q2s3_mean_minus_base"] < 0.0
    out["world_nonworse"] = out["world_support_minus_base"] <= 0.0
    out["block_majority_beats"] = out["block_q2s3_beats_base_rate"] >= 0.55
    out["block_tail_safe"] = out["block_q2s3_tail_safe_rate"] >= 0.75
    out["strict_amplitude_gate"] = (
        out["heldout_beats_base"]
        & out["heldout_tail_neutral"]
        & out["train_beats_base"]
        & out["all_beats_base"]
        & out["all_margin_vs_mixmin"]
        & out["hidden_q2s3_beats_base"]
        & out["world_nonworse"]
        & out["block_majority_beats"]
        & out["block_tail_safe"]
        & out["raw_energy_q_p90_minus_base"].le(0.0)
    )
    out["beats_alpha1_on_all"] = out["all_minus_alpha1"] < 0.0
    out["beats_alpha1_on_heldout"] = out["heldout_minus_alpha1"] < 0.0
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for alpha, group in scan.groupby("alpha", dropna=False):
        best = group.sort_values("all_delta_vs_mixmin").iloc[0]
        rows.append(
            {
                "alpha": float(alpha),
                "n": int(len(group)),
                "heldout_beats_base": int(group["heldout_beats_base"].sum()),
                "heldout_tail_neutral": int((group["heldout_beats_base"] & group["heldout_tail_neutral"]).sum()),
                "train_beats_base": int(group["train_beats_base"].sum()),
                "all_beats_base": int(group["all_beats_base"].sum()),
                "all_margin_vs_mixmin": int(group["all_margin_vs_mixmin"].sum()),
                "strict_amplitude_gate": int(group["strict_amplitude_gate"].sum()),
                "beats_alpha1_on_all": int(group["beats_alpha1_on_all"].sum()),
                "best_all_delta_vs_mixmin": float(best["all_delta_vs_mixmin"]),
                "best_all_minus_base": float(group["all_minus_base"].min()),
                "median_all_minus_base": float(group["all_minus_base"].median()),
                "best_heldout_minus_base": float(group["heldout_minus_base"].min()),
                "median_heldout_minus_base": float(group["heldout_minus_base"].median()),
                "best_world_support_minus_base": float(group["world_support_minus_base"].min()),
                "best_hidden_q2s3_minus_base": float(group["hidden_q2s3_mean_minus_base"].min()),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
            }
        )
    return pd.DataFrame(rows).sort_values("alpha").reset_index(drop=True)


def write_report(scan: pd.DataFrame, summary: pd.DataFrame) -> None:
    best = scan.sort_values("all_delta_vs_mixmin").head(20)
    strict_count = int(scan["strict_amplitude_gate"].sum())
    lines = [
        "# E69 Q2/S3 Strict-Cell Amplitude Probe",
        "",
        "## Observe",
        "",
        "E68 validates many Q2/S3 tail-gated cells outside same-anchor construction, but their held-out edge is only `1e-6` scale.",
        "",
        "## Wonder",
        "",
        "Can the independently validated Q2/S3 cells be amplified while preserving held-out, train, hidden, world, and block stress?",
        "",
        "## Method",
        "",
        f"- E68 strict pairs used: `{scan['strict_pair_id'].nunique()}`.",
        f"- Alpha grid over Q2/S3 logit delta: `{ALPHAS}`.",
        f"- Unique predictions scored: `{scan['pred_index'].nunique()}`.",
        "- Non-Q2/S3 targets stay fixed at the matched `no_q2_s3` base.",
        "- Strict amplitude gate requires heldout/train/all beats, heldout tail neutrality, full-combo margin vs mixmin, hidden/world/block support, and raw-energy non-worsening.",
        "",
        "## Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Best Full-Combo Rows",
        "",
        e56.markdown_table(
            best[
                [
                    "heldout_set",
                    "translator",
                    "alpha",
                    "all_delta_vs_mixmin",
                    "all_minus_base",
                    "heldout_minus_base",
                    "train_minus_base",
                    "world_support_minus_base",
                    "hidden_q2s3_mean_minus_base",
                    "block_q2s3_beats_base_rate",
                    "strict_amplitude_gate",
                ]
            ]
        ),
        "",
        "## Decision",
        "",
    ]
    if strict_count:
        lines.append(f"- Strict amplitude gates exist: `{strict_count}`. This branch can become a candidate generator after converting heldout-specific gates into one unified prediction rule.")
    else:
        lines.append("- Strict amplitude gates are `0`. E68 validates Q2/S3 cell direction, but simple alpha amplification still fails to create selector-scale probability movement.")
    lines.extend(
        [
            "- No submission file is produced.",
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

    strict = strict_rows()
    rows, preds = amplified_predictions(strict, components, raw_prior, mixmin, views)
    combo_scored = add_combo_scores(rows, [mixmin] + preds, sample)
    # add_combo_scores prepends mixmin for scoring, so pred_index values in rows still
    # refer to `preds`; non-anchor scoring should not include the reference.
    scored = add_nonanchor_scores(combo_scored, preds, mixmin, labels, worlds, views, state)
    scored = add_gates(scored, preds, mixmin).sort_values(["strict_amplitude_gate", "all_delta_vs_mixmin"], ascending=[False, True])
    summary = summarize(scored)

    scored.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scored, summary)
    print(
        f"strict_pairs={strict['strict_pair_id'].nunique()} rows={len(rows)} "
        f"unique_preds={len(preds)} strict_amp={int(scored['strict_amplitude_gate'].sum())} "
        f"best_all={scored['all_delta_vs_mixmin'].min():.6g} wrote={REPORT_OUT.relative_to(ROOT)}"
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
