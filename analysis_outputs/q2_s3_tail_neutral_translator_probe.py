#!/usr/bin/env python3
"""E67 tail-neutral Q2/S3 translator probe.

E66 showed Q2/S3 are not simply wrong hidden targets. Q2/S3 add-back can
improve hidden-core and mean-anchor terms while worsening robust actual-anchor
through max-set tail expansion. This probe asks whether a small tail-aware
translator can preserve the E65 no-Q2/S3 pocket and add back only Q2/S3 cells
whose first-order anchor-scenario tail risk is neutral.

This is a diagnostic stress, not a submission generator. It deliberately uses
the known anchor scenario family as a microscope for tail-risk geometry, so any
candidate that clears local gates still needs an independent stress before a
public slot.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_lb_actual_anchor_ranker import COMBO_TABLES, combo_weights, load_submission  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, mask_matrix  # noqa: E402
import gradient_amplitude_translation_probe as e64  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import q2_s3_conflict_translator_probe as e66  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "q2_s3_tail_neutral_translator_probe_scan.csv"
SUMMARY_OUT = OUT / "q2_s3_tail_neutral_translator_probe_summary.csv"
PAIR_OUT = OUT / "q2_s3_tail_neutral_translator_probe_pair.csv"
REPORT_OUT = OUT / "q2_s3_tail_neutral_translator_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
EPS = 1e-6
ANCHOR_MARGIN = 1.0e-5

BANDS = ["all", "low_slack_half"]
BASE_CELL_GATES = ["all", "raw_agree", "support60"]
GRADIENT_GATES = ["grad_core_top50", "grad_all_4of6", "grad_all_abs50"]
ROW_GATES = ["all", "teacher_row_top50"]
CAPS = [0.080, 0.120]
SCALES = [0.070, 0.095, 0.130]
SHAPES = ["flat", "core_gain"]

Q2_IDX = TARGETS.index("Q2")
S3_IDX = TARGETS.index("S3")
QS_IDXS = [Q2_IDX, S3_IDX]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def build_anchor_gradient(sample: pd.DataFrame, mixmin: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return first-order logit-loss gradients over anchor scenarios.

    The derivative of BCE wrt logit is p - y. We include row-mask weight and
    target averaging because actual anchor score is built from masked row-wise
    mean target loss. Combo-set weights are normalized across the three anchor
    scenario tables.
    """

    masks = mask_matrix(sample)
    scenario_cache: dict[str, np.ndarray] = {}
    grads: list[np.ndarray] = []
    weights: list[float] = []
    set_count = float(len(COMBO_TABLES))
    for _combo_set, table_name in COMBO_TABLES.items():
        table = pd.read_csv(OUT / table_name).head(160).reset_index(drop=True)
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
    weights_arr = weights_arr / weights_arr.sum()
    return np.stack(grads, axis=0), weights_arr


def tail_gates_for_move(move_unit: np.ndarray, gradients: np.ndarray, weights: np.ndarray) -> dict[str, np.ndarray]:
    values = gradients * move_unit[None, :, :]
    mean = np.einsum("s,srt->rt", weights, values)
    centered = values - mean[None, :, :]
    std = np.sqrt(np.einsum("s,srt->rt", weights, centered * centered))
    p90 = np.quantile(values, 0.90, axis=0)
    maxv = values.max(axis=0)
    benefit = np.maximum(-mean, 0.0)
    soft_p90 = benefit / (benefit + np.maximum(p90, 0.0) + std + 1e-12)
    soft_max = benefit / (benefit + np.maximum(maxv, 0.0) + std + 1e-12)
    gates = {
        "meanneg": (mean < 0.0).astype(np.float64),
        "p90_nonpos": ((mean < 0.0) & (p90 <= 0.0)).astype(np.float64),
        "max_nonpos": ((mean < 0.0) & (maxv <= 0.0)).astype(np.float64),
        "soft_p90": np.where(mean < 0.0, soft_p90, 0.0),
        "soft_max": np.where(mean < 0.0, soft_max, 0.0),
    }
    for name in list(gates):
        gate = np.zeros_like(move_unit, dtype=np.float64)
        gate[:, QS_IDXS] = gates[name][:, QS_IDXS]
        gates[name] = gate
    return gates


def non_q2_s3_weight() -> np.ndarray:
    weight = np.ones((1, len(TARGETS)), dtype=np.float64)
    weight[:, QS_IDXS] = 0.0
    return weight


def variant_weights(tail_gates: dict[str, np.ndarray], shape: tuple[int, int]) -> list[tuple[str, np.ndarray]]:
    base = np.broadcast_to(non_q2_s3_weight(), shape).copy()
    variants: list[tuple[str, np.ndarray]] = [("no_q2_s3", base)]

    for q2_w, s3_w in [
        (0.05, 0.05),
        (0.10, 0.10),
        (0.20, 0.20),
        (0.35, 0.35),
        (0.00, 0.20),
        (0.20, 0.00),
        (1.00, 1.00),
    ]:
        w = base.copy()
        w[:, Q2_IDX] = q2_w
        w[:, S3_IDX] = s3_w
        variants.append((f"uniform_q2{q2_w:.2f}_s3{s3_w:.2f}", w))

    for gate_name, gate in tail_gates.items():
        for mult in [0.50, 1.00]:
            w = base.copy()
            w[:, QS_IDXS] = mult * gate[:, QS_IDXS]
            variants.append((f"tail_{gate_name}_m{mult:.2f}", w))
    return variants


def generate_candidates(
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
    gradients: np.ndarray,
    gradient_weights: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    for band in BANDS:
        component = components[band]
        teacher_delta = component["delta"]
        base_cell_gates = e58.make_cell_gates(component, raw_prior, mixmin)
        base_row_gates = e58.make_row_gates(component, raw_prior, mixmin)
        grad_cell_gates = e63.gradient_gates(teacher_delta, mixmin, views)
        shape_weights = e64.gradient_gain_shapes(teacher_delta, mixmin, views)
        for base_cell_name in BASE_CELL_GATES:
            base_cell = base_cell_gates[base_cell_name]
            for grad_gate_name in GRADIENT_GATES:
                cell_gate = base_cell * grad_cell_gates[grad_gate_name]
                if cell_gate.mean() <= 0.0:
                    continue
                for row_gate_name in ROW_GATES:
                    row_gate = (
                        np.ones((teacher_delta.shape[0], 1), dtype=np.float64)
                        if row_gate_name == "all"
                        else base_row_gates["teacher_row_top50"]
                    )
                    gate = cell_gate * row_gate
                    active = float(gate.mean())
                    if active <= 0.0:
                        continue
                    for shape_name in SHAPES:
                        shaped_gate = gate * shape_weights[shape_name]
                        for cap in CAPS:
                            move_unit = np.clip(teacher_delta, -cap, cap) * shaped_gate
                            if np.abs(move_unit).mean() <= 1e-10:
                                continue
                            tail_gates = tail_gates_for_move(move_unit, gradients, gradient_weights)
                            for variant_name, target_weight in variant_weights(tail_gates, move_unit.shape):
                                move = move_unit * target_weight
                                if np.abs(move).mean() <= 1e-10:
                                    continue
                                for scale in SCALES:
                                    pred = clip_prob(sigmoid(base_logit + scale * move))
                                    tag = stable_tag(pred)
                                    if tag in seen:
                                        continue
                                    seen.add(tag)
                                    q2_gate = target_weight[:, Q2_IDX]
                                    s3_gate = target_weight[:, S3_IDX]
                                    rows.append(
                                        {
                                            "candidate": (
                                                f"toward_teacher|{band}|{variant_name}|{base_cell_name}|"
                                                f"{grad_gate_name}|{row_gate_name}|{shape_name}|s{scale:.3f}|c{cap:.3f}"
                                            ),
                                            "pred_index": len(preds),
                                            "band": band,
                                            "translator": variant_name,
                                            "base_cell_gate": base_cell_name,
                                            "gradient_gate": grad_gate_name,
                                            "row_gate": row_gate_name,
                                            "shape": shape_name,
                                            "scale": scale,
                                            "cap": cap,
                                            "active_gate_mean": active,
                                            "q2_gate_mean": float(q2_gate.mean()),
                                            "s3_gate_mean": float(s3_gate.mean()),
                                            "q2_gate_nonzero": float((q2_gate > 0.0).mean()),
                                            "s3_gate_nonzero": float((s3_gate > 0.0).mean()),
                                            "hash": tag,
                                            "direction": "toward_teacher",
                                        }
                                    )
                                    preds.append(pred)
    return pd.DataFrame(rows), preds


def hidden_guard(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["hidden_core_mean_delta"].lt(0.0)
        & frame["hidden_core_improve_count"].ge(3)
        & frame["hidden_all_improve_count"].ge(5)
    )


def base_key_columns() -> list[str]:
    return ["band", "base_cell_gate", "gradient_gate", "row_gate", "shape", "scale", "cap"]


def pair_against_base(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    key_cols = base_key_columns()
    for key, group in scored.groupby(key_cols, dropna=False):
        by_name = {str(row.translator): row for row in group.itertuples(index=False)}
        if "no_q2_s3" not in by_name:
            continue
        base = by_name["no_q2_s3"]
        for name, row in by_name.items():
            if name == "no_q2_s3":
                continue
            rec: dict[str, Any] = dict(zip(key_cols, key, strict=True))
            rec.update(
                {
                    "translator": name,
                    "base_anchor_delta": float(base.anchor_delta_vs_mixmin),
                    "translator_anchor_delta": float(row.anchor_delta_vs_mixmin),
                    "anchor_minus_base": float(row.anchor_delta_vs_mixmin - base.anchor_delta_vs_mixmin),
                    "mean_anchor_minus_base": float(row.mean_actual_anchor - base.mean_actual_anchor),
                    "max_set_minus_base": float(row.max_set_score - base.max_set_score),
                    "min_set_minus_base": float(row.min_set_score - base.min_set_score),
                    "hidden_core_minus_base": float(row.hidden_core_mean_delta - base.hidden_core_mean_delta),
                    "hidden_all_minus_base": float(row.hidden_all_mean_delta - base.hidden_all_mean_delta),
                    "q2_hidden_minus_base": float(row.hidden_core_delta_Q2 - base.hidden_core_delta_Q2),
                    "s3_hidden_minus_base": float(row.hidden_core_delta_S3 - base.hidden_core_delta_S3),
                    "mean_move_minus_base": float(row.mean_abs_logit_move_vs_mixmin - base.mean_abs_logit_move_vs_mixmin),
                    "beats_base": bool(row.anchor_delta_vs_mixmin < base.anchor_delta_vs_mixmin),
                    "tail_neutral_vs_base": bool(row.max_set_score <= base.max_set_score),
                }
            )
            rows.append(rec)
    return pd.DataFrame(rows)


def translator_summary(scored: pd.DataFrame, pair: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, group in scored.groupby("translator", dropna=False):
        best = group.sort_values("anchor_delta_vs_mixmin").iloc[0]
        pair_group = pair[pair["translator"].eq(name)]
        rows.append(
            {
                "translator": name,
                "n": int(len(group)),
                "anchor_beats_mixmin": int((group["anchor_delta_vs_mixmin"] < 0.0).sum()),
                "anchor_margin": int((group["anchor_delta_vs_mixmin"] < -ANCHOR_MARGIN).sum()),
                "hidden_guard": int(group["hidden_guard"].sum()),
                "best_anchor_delta": float(best["anchor_delta_vs_mixmin"]),
                "median_anchor_delta": float(group["anchor_delta_vs_mixmin"].median()),
                "best_max_set_delta_vs_mixmin": float(best["max_set_score"] - scored["mixmin_max_set_score"].iloc[0]),
                "best_hidden_core_delta": float(best["hidden_core_mean_delta"]),
                "best_q2_gate_mean": float(best["q2_gate_mean"]),
                "best_s3_gate_mean": float(best["s3_gate_mean"]),
                "best_candidate": str(best["candidate"]),
                "beats_base": int(pair_group["beats_base"].sum()) if len(pair_group) else 0,
                "tail_neutral_beats_base": int((pair_group["beats_base"] & pair_group["tail_neutral_vs_base"]).sum()) if len(pair_group) else 0,
                "best_anchor_minus_base": float(pair_group["anchor_minus_base"].min()) if len(pair_group) else 0.0,
                "median_anchor_minus_base": float(pair_group["anchor_minus_base"].median()) if len(pair_group) else 0.0,
                "best_max_set_minus_base": float(pair_group["max_set_minus_base"].min()) if len(pair_group) else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["best_anchor_delta", "translator"]).reset_index(drop=True)


def write_report(scored: pd.DataFrame, summary: pd.DataFrame, pair: pd.DataFrame) -> None:
    best = scored.sort_values("anchor_delta_vs_mixmin").head(25)
    base = summary[summary["translator"].eq("no_q2_s3")].iloc[0]
    better_than_base = pair[pair["beats_base"]].copy()
    tail_neutral = better_than_base[better_than_base["tail_neutral_vs_base"]].copy()
    lines = [
        "# E67 Tail-Neutral Q2/S3 Translator Probe",
        "",
        "## Observe",
        "",
        "E66 split Q2/S3 into a hidden/mean-positive signal and a robust-anchor tail risk. A target mask alone cannot decide this conflict.",
        "",
        "## Wonder",
        "",
        "Can Q2/S3 be partially added back only where first-order public-anchor scenario tails are neutral, beating the `no_q2_s3` pocket without expanding the max-set tail?",
        "",
        "## Method",
        "",
        f"- Generated candidates: `{len(scored)}`.",
        "- Non-Q2/S3 targets keep the E65 move; Q2/S3 are added by uniform small weights or anchor-tail gates.",
        "- Tail gates use first-order BCE derivative `(mixmin - scenario) * teacher_delta` over the existing anchor scenario/mask family.",
        "- Scored actual-anchor, hidden-rate validation, and matched same-configuration deltas versus `no_q2_s3`.",
        "",
        "## Summary",
        "",
        e56.markdown_table(summary.head(30)),
        "",
        "## Matched Base Comparison",
        "",
        f"- `no_q2_s3` best anchor delta: `{base['best_anchor_delta']:.9g}`.",
        f"- translators beating matched `no_q2_s3`: `{len(better_than_base)}/{len(pair)}`.",
        f"- translators beating matched `no_q2_s3` with max-set tail neutral: `{len(tail_neutral)}/{len(pair)}`.",
    ]
    if len(tail_neutral):
        show_cols = [
            *base_key_columns(),
            "translator",
            "base_anchor_delta",
            "translator_anchor_delta",
            "anchor_minus_base",
            "max_set_minus_base",
            "hidden_core_minus_base",
            "q2_hidden_minus_base",
            "s3_hidden_minus_base",
        ]
        lines.extend(["", e56.markdown_table(tail_neutral.sort_values("anchor_minus_base")[show_cols].head(20))])
    lines.extend(
        [
            "",
            "## Top Candidates",
            "",
            e56.markdown_table(
                best[
                    [
                        "candidate",
                        "translator",
                        "anchor_delta_vs_mixmin",
                        "mean_actual_anchor",
                        "max_set_score",
                        "hidden_core_mean_delta",
                        "hidden_core_delta_Q2",
                        "hidden_core_delta_S3",
                        "q2_gate_mean",
                        "s3_gate_mean",
                        "mean_abs_logit_move_vs_mixmin",
                    ]
                ]
            ),
            "",
            "## Decision",
            "",
            "- E67 is a tail-risk translator audit, not a submission generator.",
            "- If tail-gated Q2/S3 beats matched `no_q2_s3` with max-set neutral, the next experiment should add independent non-anchor validation before considering a file.",
            "- If it cannot beat `no_q2_s3`, Q2/S3 tail risk is not solved by first-order anchor-tail gating; the next branch must use rowwise calibration or a structural target, not Q2/S3 add-back.",
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
    raw05 = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and hidden-rate state")

    views, _ = e63.hidden_row_views(state, sample, mixmin, a2c8)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    gradients, gradient_weights = build_anchor_gradient(sample, mixmin)
    rows, preds = generate_candidates(components, raw_prior, mixmin, views, gradients, gradient_weights)

    scored = e58.score_prefilter(rows, preds, labels, worlds, mixmin)
    hidden_rows = [e63.hidden_validation_scores(preds[int(row.pred_index)], mixmin, views) for row in scored.itertuples(index=False)]
    hidden_target_rows = [e66.hidden_target_contrib(preds[int(row.pred_index)], mixmin, views) for row in scored.itertuples(index=False)]
    scored = pd.concat(
        [scored.reset_index(drop=True), pd.DataFrame(hidden_rows), pd.DataFrame(hidden_target_rows)],
        axis=1,
    )
    scored["hidden_guard"] = hidden_guard(scored)

    anchor = actual_anchor_score([mixmin, a2c8, raw05] + [preds[int(i)] for i in scored["pred_index"]], sample)
    mixmin_anchor = float(anchor.iloc[0]["actual_anchor_score_final"])
    mixmin_max_set = float(anchor.iloc[0]["max_set_score"])
    cand_anchor = anchor.iloc[3:].reset_index(drop=True)
    scored["actual_anchor_score_final"] = cand_anchor["actual_anchor_score_final"].to_numpy(dtype=np.float64)
    scored["anchor_delta_vs_mixmin"] = scored["actual_anchor_score_final"] - mixmin_anchor
    scored["mean_actual_anchor"] = cand_anchor["mean_actual_anchor"].to_numpy(dtype=np.float64)
    scored["min_set_score"] = cand_anchor["min_set_score"].to_numpy(dtype=np.float64)
    scored["max_set_score"] = cand_anchor["max_set_score"].to_numpy(dtype=np.float64)
    scored["mixmin_max_set_score"] = mixmin_max_set
    scored["anchor_beats_mixmin"] = scored["anchor_delta_vs_mixmin"] < 0.0
    scored["anchor_margin_gate"] = scored["anchor_delta_vs_mixmin"] < -ANCHOR_MARGIN

    scored = scored.sort_values("anchor_delta_vs_mixmin").reset_index(drop=True)
    pair = pair_against_base(scored)
    summary = translator_summary(scored, pair)
    scored.to_csv(SCAN_OUT, index=False)
    pair.to_csv(PAIR_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scored, summary, pair)

    best = scored.iloc[0]
    base_best = summary[summary["translator"].eq("no_q2_s3")].iloc[0]
    print(
        f"generated={len(rows)} scored={len(scored)} "
        f"best={best['translator']} best_delta={best['anchor_delta_vs_mixmin']:.6g} "
        f"base_best={base_best['best_anchor_delta']:.6g} "
        f"tail_neutral_base_beats={int((pair['beats_base'] & pair['tail_neutral_vs_base']).sum())} "
        f"wrote={REPORT_OUT.relative_to(ROOT)}"
    )
    print(summary[["translator", "n", "best_anchor_delta", "beats_base", "tail_neutral_beats_base", "best_anchor_minus_base"]].head(20).to_string(index=False))


if __name__ == "__main__":
    main()
