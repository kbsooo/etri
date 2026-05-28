#!/usr/bin/env python3
"""E68 independent validation for E67 tail-gated Q2/S3 cells.

E67 showed first-order tail gates can add back Q2/S3 better than broad target
masks, but the same known-anchor scenario family defined and scored the gates.
This probe keeps the E67 matched configurations, rebuilds only the most
promising tail-gated cells, and asks a sharper question:

If one combo-set family is held out from gate construction, does the tail-gated
Q2/S3 cell still beat its matched `no_q2_s3` base on the held-out family and on
non-anchor hidden/world/block stresses?

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
from public_lb_actual_anchor_ranker import COMBO_TABLES, STAGE2_LB, combo_weights, load_submission  # noqa: E402
from public_subset_sensitivity_audit import ce_matrix  # noqa: E402
from raw05_anchor_jepa_micro_injection import mask_matrix  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_conflict_translator_probe as e66  # noqa: E402
import q2_s3_tail_neutral_translator_probe as e67  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


PAIR_IN = OUT / "q2_s3_tail_neutral_translator_probe_pair.csv"
SCAN_OUT = OUT / "q2_s3_tail_gate_independence_probe_scan.csv"
PAIR_OUT = OUT / "q2_s3_tail_gate_independence_probe_pair.csv"
SUMMARY_OUT = OUT / "q2_s3_tail_gate_independence_probe_summary.csv"
REPORT_OUT = OUT / "q2_s3_tail_gate_independence_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
EPS = 1e-6
MAX_BASE_CONFIGS = 180

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]
CORE_VIEW_NAMES = ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign", "core_median"]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def bce(prob: np.ndarray, target: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = clip_prob(target)
    return -(y * np.log(p) + (1.0 - y) * np.log1p(-p))


def candidate_key_cols() -> list[str]:
    return ["band", "base_cell_gate", "gradient_gate", "row_gate", "shape", "scale", "cap"]


def select_e67_configs() -> pd.DataFrame:
    pair = pd.read_csv(PAIR_IN)
    pair = pair[pair["translator"].astype(str).str.startswith("tail_")].copy()
    pair["hidden_q2s3_minus_base"] = 0.5 * (pair["q2_hidden_minus_base"] + pair["s3_hidden_minus_base"])
    pair["selection_score"] = (
        pair["anchor_minus_base"]
        + 35.0 * np.maximum(pair["hidden_q2s3_minus_base"], 0.0)
        + 10.0 * np.maximum(pair["max_set_minus_base"], 0.0)
        + 4.0 * np.maximum(pair["hidden_core_minus_base"], 0.0)
    )
    preferred = pair[
        pair["beats_base"]
        & pair["tail_neutral_vs_base"]
        & pair["hidden_q2s3_minus_base"].lt(0.0)
    ].copy()
    pieces: list[pd.DataFrame] = []
    if len(preferred):
        pieces.append(preferred.sort_values("selection_score").head(120))
        for name, part in preferred.groupby("translator", dropna=False):
            pieces.append(part.sort_values("selection_score").head(25))
    pieces.append(pair.sort_values("selection_score").head(80))
    selected = pd.concat(pieces, ignore_index=False).drop_duplicates(candidate_key_cols() + ["translator"])
    return selected.sort_values("selection_score").head(MAX_BASE_CONFIGS).reset_index(drop=True)


def anchor_gradient_for_sets(
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    combo_sets: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    masks = mask_matrix(sample)
    scenario_cache: dict[str, np.ndarray] = {}
    grads: list[np.ndarray] = []
    weights: list[float] = []
    set_count = float(len(combo_sets))
    for combo_set in combo_sets:
        table = pd.read_csv(OUT / COMBO_TABLES[combo_set]).head(160).reset_index(drop=True)
        table_weights = combo_weights(table) / set_count
        for i, row in table.iterrows():
            scenario = str(row["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = load_submission(scenario, sample)
            q = scenario_cache[scenario]
            mask_vec = masks[int(row["mask_index"])].reshape(-1, 1)
            grads.append(mask_vec * (mixmin - q) / float(len(TARGETS)))
            weights.append(float(table_weights[i]))
    weights_arr = np.asarray(weights, dtype=np.float64)
    weights_arr /= weights_arr.sum()
    return np.stack(grads, axis=0), weights_arr


def pred_from_config(
    rec: pd.Series,
    translator: str,
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
    gradients: np.ndarray,
    gradient_weights: np.ndarray,
) -> np.ndarray:
    component = components[str(rec["band"])]
    teacher_delta = component["delta"]
    base_cell = e58.make_cell_gates(component, raw_prior, mixmin)[str(rec["base_cell_gate"])]
    row_gate = (
        np.ones((teacher_delta.shape[0], 1), dtype=np.float64)
        if str(rec["row_gate"]) == "all"
        else e58.make_row_gates(component, raw_prior, mixmin)["teacher_row_top50"]
    )
    grad_gate = e63.gradient_gates(teacher_delta, mixmin, views)[str(rec["gradient_gate"])]
    shape_weight = e67.e64.gradient_gain_shapes(teacher_delta, mixmin, views)[str(rec["shape"])]
    move_unit = np.clip(teacher_delta, -float(rec["cap"]), float(rec["cap"])) * base_cell * row_gate * grad_gate * shape_weight
    tail_gates = e67.tail_gates_for_move(move_unit, gradients, gradient_weights)
    weights = dict(e67.variant_weights(tail_gates, move_unit.shape))
    if translator not in weights:
        raise KeyError(translator)
    move = move_unit * weights[translator]
    return clip_prob(sigmoid(logit(mixmin) + float(rec["scale"]) * move))


def combo_set_score(preds: list[np.ndarray], sample: pd.DataFrame, combo_sets: list[str]) -> pd.DataFrame:
    pred_stack = np.stack(preds, axis=0)
    masks = mask_matrix(sample)
    stage2 = load_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", sample)
    scenario_cache: dict[str, np.ndarray] = {}
    frames = []
    for combo_set in combo_sets:
        table = pd.read_csv(OUT / COMBO_TABLES[combo_set]).head(160).reset_index(drop=True)
        weights = combo_weights(table)
        values = np.zeros((len(preds), len(table)), dtype=np.float64)
        for i, row in table.iterrows():
            scenario = str(row["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = load_submission(scenario, sample)
            q = scenario_cache[scenario]
            mask_vec = masks[int(row["mask_index"])]
            stage_loss = float(mask_vec @ ce_matrix(q, stage2).mean(axis=1))
            cand_loss = bce(pred_stack, q[None, :, :]).mean(axis=2) @ mask_vec
            values[:, i] = STAGE2_LB + cand_loss - stage_loss
        mean = values @ weights
        std = np.sqrt(((values - mean[:, None]) ** 2) @ weights)
        p90 = np.quantile(values, 0.90, axis=1)
        worst = values.max(axis=1)
        score = mean + 0.35 * std + 0.20 * np.maximum(p90 - mean, 0.0) + 0.10 * np.maximum(worst - mean, 0.0)
        frames.append(
            pd.DataFrame(
                {
                    "candidate_index": np.arange(len(preds)),
                    f"score__{combo_set}": score,
                    f"mean__{combo_set}": mean,
                    f"worst__{combo_set}": worst,
                }
            )
        )
    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="candidate_index", how="inner")
    score_cols = [c for c in merged.columns if c.startswith("score__")]
    mean_cols = [c for c in merged.columns if c.startswith("mean__")]
    worst_cols = [c for c in merged.columns if c.startswith("worst__")]
    merged["score"] = merged[score_cols].mean(axis=1)
    merged["mean"] = merged[mean_cols].mean(axis=1)
    merged["worst"] = merged[worst_cols].max(axis=1)
    return merged[["candidate_index", "score", "mean", "worst"]]


def world_support(prob: np.ndarray, mixmin: np.ndarray, labels: np.ndarray, worlds: pd.DataFrame) -> dict[str, float]:
    mix_loss = e58.binary_logloss_by_world(mixmin, labels)
    delta = e58.binary_logloss_by_world(prob, labels) - mix_loss
    masks = {
        "world_all": np.ones(len(labels), dtype=bool),
        "raw_energy_quarter": worlds["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
    }
    out: dict[str, float] = {}
    for name, mask in masks.items():
        out.update(e58.band_stats(delta, mask, name))
    out["world_support_score"] = (
        out["raw_energy_quarter_median_delta"]
        + 0.25 * out["raw_energy_quarter_p90_delta"]
        + 0.10 * out["world_all_median_delta"]
    )
    return out


def hidden_block_q2s3_delta(
    prob: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> np.ndarray:
    deltas = []
    for view_name in CORE_VIEW_NAMES:
        rate = views[view_name]
        row_delta = bce(prob[:, QS_IDXS], rate[:, QS_IDXS]).mean(axis=1) - bce(
            mixmin[:, QS_IDXS], rate[:, QS_IDXS]
        ).mean(axis=1)
        block_vals = []
        for block in state.hidden_blocks:
            sample_idx = state.rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
            block_vals.append(float(row_delta[sample_idx].mean()))
        deltas.append(np.asarray(block_vals, dtype=np.float64))
    return np.mean(np.stack(deltas, axis=0), axis=0)


def score_prediction(
    tag: str,
    prob: np.ndarray,
    mixmin: np.ndarray,
    labels: np.ndarray,
    worlds: pd.DataFrame,
    views: dict[str, np.ndarray],
    state: e55.BaseState,
) -> dict[str, Any]:
    hidden = e63.hidden_validation_scores(prob, mixmin, views)
    target_hidden = e66.hidden_target_contrib(prob, mixmin, views)
    world = world_support(prob, mixmin, labels, worlds)
    block = hidden_block_q2s3_delta(prob, mixmin, views, state)
    return {
        "tag": tag,
        **hidden,
        **target_hidden,
        **world,
        "block_q2s3_core_mean_delta": float(block.mean()),
        "block_q2s3_core_max_delta": float(block.max()),
        "block_q2s3_core_improve_rate": float((block < 0.0).mean()),
        "_block_vector": block,
    }


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw05 = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")
    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)

    selected = select_e67_configs()
    rows: list[dict[str, Any]] = []
    pred_cache: dict[str, np.ndarray] = {"mixmin": mixmin, "a2c8": a2c8, "raw05": raw05}
    pred_meta: dict[str, dict[str, Any]] = {}
    for heldout_set in COMBO_TABLES:
        train_sets = [name for name in COMBO_TABLES if name != heldout_set]
        gradients, gradient_weights = anchor_gradient_for_sets(sample, mixmin, train_sets)
        for rec in selected.to_dict("records"):
            spec = pd.Series(rec)
            for translator in ["no_q2_s3", str(rec["translator"])]:
                pred = pred_from_config(spec, translator, components, raw_prior, mixmin, views, gradients, gradient_weights)
                tag = e67.stable_tag(pred, prefix=f"{heldout_set}_{translator}_")
                if tag not in pred_cache:
                    pred_cache[tag] = pred
                    pred_meta[tag] = {"translator": translator, **{c: rec[c] for c in candidate_key_cols()}}
            base_tag = e67.stable_tag(
                pred_from_config(spec, "no_q2_s3", components, raw_prior, mixmin, views, gradients, gradient_weights),
                prefix=f"{heldout_set}_no_q2_s3_",
            )
            cand_tag = e67.stable_tag(
                pred_from_config(spec, str(rec["translator"]), components, raw_prior, mixmin, views, gradients, gradient_weights),
                prefix=f"{heldout_set}_{rec['translator']}_",
            )
            rows.append(
                {
                    "heldout_set": heldout_set,
                    "gate_train_sets": ",".join(train_sets),
                    "translator": rec["translator"],
                    "base_tag": base_tag,
                    "candidate_tag": cand_tag,
                    **{c: rec[c] for c in candidate_key_cols()},
                    "e67_anchor_minus_base": rec["anchor_minus_base"],
                    "e67_max_set_minus_base": rec["max_set_minus_base"],
                    "e67_hidden_q2s3_minus_base": rec["hidden_q2s3_minus_base"],
                }
            )
        print(f"rebuilt heldout={heldout_set} configs={len(selected)} unique_preds={len(pred_cache)}")

    tags = list(pred_cache)
    preds = [pred_cache[tag] for tag in tags]
    tag_to_idx = {tag: i for i, tag in enumerate(tags)}
    score_frames = {}
    for heldout_set in COMBO_TABLES:
        train_sets = [name for name in COMBO_TABLES if name != heldout_set]
        score_frames[(heldout_set, "heldout")] = combo_set_score(preds, sample, [heldout_set])
        score_frames[(heldout_set, "train")] = combo_set_score(preds, sample, train_sets)
        print(f"scored heldout={heldout_set}")

    pred_scores: dict[str, dict[str, Any]] = {}
    for tag, pred in pred_cache.items():
        if tag in {"mixmin", "a2c8", "raw05"}:
            continue
        pred_scores[tag] = score_prediction(tag, pred, mixmin, labels, worlds, views, state)

    pair_rows: list[dict[str, Any]] = []
    scan_rows: list[dict[str, Any]] = []
    for row in rows:
        heldout_set = str(row["heldout_set"])
        base_tag = str(row["base_tag"])
        cand_tag = str(row["candidate_tag"])
        base_idx = tag_to_idx[base_tag]
        cand_idx = tag_to_idx[cand_tag]
        mix_idx = tag_to_idx["mixmin"]
        rec = dict(row)
        for split in ["heldout", "train"]:
            frame = score_frames[(heldout_set, split)].set_index("candidate_index")
            base_score = float(frame.loc[base_idx, "score"] - frame.loc[mix_idx, "score"])
            cand_score = float(frame.loc[cand_idx, "score"] - frame.loc[mix_idx, "score"])
            base_worst = float(frame.loc[base_idx, "worst"] - frame.loc[mix_idx, "worst"])
            cand_worst = float(frame.loc[cand_idx, "worst"] - frame.loc[mix_idx, "worst"])
            rec[f"{split}_base_delta_vs_mixmin"] = base_score
            rec[f"{split}_candidate_delta_vs_mixmin"] = cand_score
            rec[f"{split}_minus_base"] = cand_score - base_score
            rec[f"{split}_worst_minus_base"] = cand_worst - base_worst
        base_stats = pred_scores[base_tag]
        cand_stats = pred_scores[cand_tag]
        base_block = base_stats["_block_vector"]
        cand_block = cand_stats["_block_vector"]
        block_minus = cand_block - base_block
        rec.update(
            {
                "world_support_minus_base": float(cand_stats["world_support_score"] - base_stats["world_support_score"]),
                "raw_energy_q_p90_minus_base": float(
                    cand_stats["raw_energy_quarter_p90_delta"] - base_stats["raw_energy_quarter_p90_delta"]
                ),
                "hidden_core_minus_base": float(cand_stats["hidden_core_mean_delta"] - base_stats["hidden_core_mean_delta"]),
                "hidden_q2_minus_base": float(cand_stats["hidden_core_delta_Q2"] - base_stats["hidden_core_delta_Q2"]),
                "hidden_s3_minus_base": float(cand_stats["hidden_core_delta_S3"] - base_stats["hidden_core_delta_S3"]),
                "hidden_q2s3_mean_minus_base": float(
                    0.5
                    * (
                        cand_stats["hidden_core_delta_Q2"]
                        - base_stats["hidden_core_delta_Q2"]
                        + cand_stats["hidden_core_delta_S3"]
                        - base_stats["hidden_core_delta_S3"]
                    )
                ),
                "block_q2s3_mean_minus_base": float(block_minus.mean()),
                "block_q2s3_max_minus_base": float(block_minus.max()),
                "block_q2s3_beats_base_rate": float((block_minus < 0.0).mean()),
                "block_q2s3_tail_safe_rate": float((block_minus <= 1.0e-8).mean()),
                "heldout_beats_base": rec["heldout_minus_base"] < 0.0,
                "heldout_tail_neutral": rec["heldout_worst_minus_base"] <= 0.0,
                "train_beats_base": rec["train_minus_base"] < 0.0,
                "hidden_q2s3_beats_base": False,
                "world_nonworse": False,
            }
        )
        rec["hidden_q2s3_beats_base"] = rec["hidden_q2s3_mean_minus_base"] < 0.0
        rec["world_nonworse"] = rec["world_support_minus_base"] <= 0.0
        rec["independent_gate"] = bool(
            rec["heldout_beats_base"]
            and rec["heldout_tail_neutral"]
            and rec["hidden_q2s3_beats_base"]
            and rec["world_nonworse"]
            and rec["block_q2s3_beats_base_rate"] >= 0.55
        )
        rec["strict_independent_gate"] = bool(
            rec["independent_gate"]
            and rec["train_beats_base"]
            and rec["raw_energy_q_p90_minus_base"] <= 0.0
            and rec["block_q2s3_tail_safe_rate"] >= 0.75
        )
        pair_rows.append(rec)
        for tag, kind in [(base_tag, "base"), (cand_tag, "candidate")]:
            stats = pred_scores[tag]
            scan_rows.append(
                {
                    "heldout_set": heldout_set,
                    "kind": kind,
                    "tag": tag,
                    "translator": "no_q2_s3" if kind == "base" else row["translator"],
                    **{c: row[c] for c in candidate_key_cols()},
                    "hidden_core_mean_delta": stats["hidden_core_mean_delta"],
                    "hidden_core_delta_Q2": stats["hidden_core_delta_Q2"],
                    "hidden_core_delta_S3": stats["hidden_core_delta_S3"],
                    "world_support_score": stats["world_support_score"],
                    "block_q2s3_core_mean_delta": stats["block_q2s3_core_mean_delta"],
                    "block_q2s3_core_improve_rate": stats["block_q2s3_core_improve_rate"],
                }
            )

    pair = pd.DataFrame(pair_rows).sort_values(
        ["strict_independent_gate", "independent_gate", "heldout_minus_base"],
        ascending=[False, False, True],
    )
    scan = pd.DataFrame(scan_rows).drop_duplicates(["heldout_set", "tag"])
    summary_rows = []
    for translator, group in pair.groupby("translator", dropna=False):
        best = group.sort_values("heldout_minus_base").iloc[0]
        summary_rows.append(
            {
                "translator": translator,
                "pairs": int(len(group)),
                "heldout_beats_base": int(group["heldout_beats_base"].sum()),
                "heldout_tail_neutral_beats": int((group["heldout_beats_base"] & group["heldout_tail_neutral"]).sum()),
                "train_beats_base": int(group["train_beats_base"].sum()),
                "hidden_q2s3_beats_base": int(group["hidden_q2s3_beats_base"].sum()),
                "world_nonworse": int(group["world_nonworse"].sum()),
                "block_majority_beats": int((group["block_q2s3_beats_base_rate"] >= 0.55).sum()),
                "independent_gate": int(group["independent_gate"].sum()),
                "strict_independent_gate": int(group["strict_independent_gate"].sum()),
                "best_heldout_minus_base": float(best["heldout_minus_base"]),
                "median_heldout_minus_base": float(group["heldout_minus_base"].median()),
                "best_heldout_set": str(best["heldout_set"]),
                "best_block_win_rate": float(group["block_q2s3_beats_base_rate"].max()),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(
        ["strict_independent_gate", "independent_gate", "best_heldout_minus_base"],
        ascending=[False, False, True],
    )

    scan.to_csv(SCAN_OUT, index=False)
    pair.to_csv(PAIR_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(selected, scan, pair, summary)
    print(
        f"selected={len(selected)} unique_preds={len(pred_cache)} pair={len(pair)} "
        f"independent={int(pair['independent_gate'].sum())} "
        f"strict={int(pair['strict_independent_gate'].sum())} wrote={REPORT_OUT.relative_to(ROOT)}"
    )
    print(summary.to_string(index=False))


def write_report(selected: pd.DataFrame, scan: pd.DataFrame, pair: pd.DataFrame, summary: pd.DataFrame) -> None:
    lines = [
        "# E68 Q2/S3 Tail-Gate Independence Probe",
        "",
        "## Observe",
        "",
        "E67 found a better Q2/S3 add-back rule, but that rule was still known-anchor-tail-derived and below margin.",
        "",
        "## Wonder",
        "",
        "If each combo set is held out from tail-gate construction, do the selected E67 Q2/S3 cells still beat matched `no_q2_s3` and survive non-anchor hidden/world/block stress?",
        "",
        "## Method",
        "",
        f"- Selected E67 matched configs: `{len(selected)}`.",
        f"- Rebuilt unique predictions: `{scan['tag'].nunique() if len(scan) else 0}` scored non-anchor, plus references.",
        f"- Matched held-out comparisons: `{len(pair)}`.",
        "- For each held-out combo set, gates were rebuilt from the other combo sets only.",
        "- Independent gate requires held-out beat, held-out worst-tail neutrality, hidden Q2/S3 improvement, non-worse world support, and hidden-block Q2/S3 majority beat.",
        "- Strict gate additionally requires train-set beat, non-worse raw-energy p90, and hidden-block tail-safe rate at least `0.75`.",
        "",
        "## Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Best Comparisons",
        "",
        e56.markdown_table(
            pair[
                [
                    "heldout_set",
                    "translator",
                    "heldout_minus_base",
                    "heldout_worst_minus_base",
                    "train_minus_base",
                    "world_support_minus_base",
                    "hidden_q2s3_mean_minus_base",
                    "block_q2s3_beats_base_rate",
                    "independent_gate",
                    "strict_independent_gate",
                ]
            ].head(25)
        ),
        "",
        "## Decision",
        "",
    ]
    strict_n = int(pair["strict_independent_gate"].sum()) if len(pair) else 0
    loose_n = int(pair["independent_gate"].sum()) if len(pair) else 0
    if strict_n:
        lines.append(f"- Strict independent gates exist: `{strict_n}`. Tail-gated Q2/S3 cells are no longer just an E67 anchor-tail artifact, but they still need selector-scale public margin before submission.")
    elif loose_n:
        lines.append(f"- Loose independent gates exist: `{loose_n}`, but strict raw/train/block-tail conditions fail. Keep this as partial validation, not a submission.")
    else:
        lines.append("- Independent gates are `0`; E67 tail gates do not survive the held-out/non-anchor audit.")
    lines.extend(
        [
            "- No submission file is produced.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{PAIR_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
