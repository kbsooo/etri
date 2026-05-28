#!/usr/bin/env python3
"""E65 near-zero amplitude response probe.

E63 showed a tiny favorable actual-anchor edge for gradient-consensus E56
movement. E64 showed larger scalar amplification is uniformly adverse. This
probe tests the only remaining scalar-ish possibility: perhaps the useful
region is a very small targetwise/rowwise amplitude pocket around mixmin.

The output is meant as a response-surface diagnostic. A submission is saved
only if a candidate clears the same world, hidden, movement, and anchor margin
guards used by the prior probes.
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
import gradient_amplitude_translation_probe as e64  # noqa: E402
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "near_zero_amplitude_response_probe_scan.csv"
SUMMARY_OUT = OUT / "near_zero_amplitude_response_probe_summary.csv"
TARGET_OUT = OUT / "near_zero_amplitude_response_probe_target_response.csv"
SCALE_OUT = OUT / "near_zero_amplitude_response_probe_scale_response.csv"
REPORT_OUT = OUT / "near_zero_amplitude_response_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
ANCHOR_MARGIN = 1.0e-5
EPS = 1e-6

BANDS = ["all", "low_slack_half"]
TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "no_s3": ["Q1", "Q2", "Q3", "S1", "S2", "S4"],
    "no_q2_s3": ["Q1", "Q3", "S1", "S2", "S4"],
    "q1": ["Q1"],
    "q3": ["Q3"],
    "s2": ["S2"],
    "s4": ["S4"],
}
BASE_CELL_GATES = ["all", "raw_agree", "support60"]
GRADIENT_GATES = ["grad_core_top50", "grad_all_4of6", "grad_all_abs50"]
ROW_GATES = ["all", "teacher_row_top50"]
CAPS = [0.030, 0.080, 0.120]
SCALES = [0.006, 0.010, 0.016, 0.024, 0.035, 0.050, 0.070, 0.095, 0.130]
SHAPES = ["flat", "core_gain"]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)


def generate_candidates(
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    for band in BANDS:
        if band not in components:
            continue
        component = components[band]
        teacher_delta = component["delta"]
        base_cell_gates = e58.make_cell_gates(component, raw_prior, mixmin)
        base_row_gates = e58.make_row_gates(component, raw_prior, mixmin)
        grad_cell_gates = e63.gradient_gates(teacher_delta, mixmin, views)
        grad_row_gates = {
            "all": np.ones((teacher_delta.shape[0], 1), dtype=np.float64),
            "teacher_row_top50": base_row_gates["teacher_row_top50"],
            "support_row_top50": base_row_gates["support_row_top50"],
        }
        shape_weights = e64.gradient_gain_shapes(teacher_delta, mixmin, views)
        for direction_name, direction in [("toward_teacher", 1.0), ("reverse_control", -1.0)]:
            for target_name in TARGET_MASKS:
                tgate = target_mask(target_name)
                for base_cell_name in BASE_CELL_GATES:
                    base_cell = base_cell_gates[base_cell_name]
                    for grad_gate_name in GRADIENT_GATES:
                        grad_gate = grad_cell_gates[grad_gate_name]
                        cell_gate = base_cell * grad_gate
                        if cell_gate.mean() <= 0.0:
                            continue
                        for row_gate_name in ROW_GATES:
                            row_gate = grad_row_gates[row_gate_name]
                            gate = tgate * cell_gate * row_gate
                            active = float(gate.mean())
                            if active <= 0.0:
                                continue
                            for shape_name in SHAPES:
                                shaped_gate = gate * shape_weights[shape_name]
                                if shaped_gate.mean() <= 0.0:
                                    continue
                                for cap in CAPS:
                                    capped = np.clip(teacher_delta, -cap, cap) * shaped_gate
                                    if np.abs(capped).mean() <= 1e-10:
                                        continue
                                    for scale in SCALES:
                                        pred = clip_prob(sigmoid(base_logit + direction * scale * capped))
                                        tag = stable_tag(pred)
                                        if tag in seen:
                                            continue
                                        seen.add(tag)
                                        rows.append(
                                            {
                                                "candidate": (
                                                    f"{direction_name}|{band}|{target_name}|{base_cell_name}|"
                                                    f"{grad_gate_name}|{row_gate_name}|{shape_name}|s{scale:.3f}|c{cap:.3f}"
                                                ),
                                                "pred_index": len(preds),
                                                "direction": direction_name,
                                                "band": band,
                                                "target_mask": target_name,
                                                "base_cell_gate": base_cell_name,
                                                "gradient_gate": grad_gate_name,
                                                "row_gate": row_gate_name,
                                                "shape": shape_name,
                                                "scale": scale,
                                                "cap": cap,
                                                "active_gate_mean": active,
                                                "hash": tag,
                                            }
                                        )
                                        preds.append(pred)
    return pd.DataFrame(rows), preds


def score_candidates(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    labels: np.ndarray,
    worlds: pd.DataFrame,
    mixmin: np.ndarray,
    views: dict[str, np.ndarray],
) -> pd.DataFrame:
    scored = e58.score_prefilter(rows, preds, labels, worlds, mixmin)
    hidden_rows = []
    for rec in scored.to_dict("records"):
        hidden_rows.append(e63.hidden_validation_scores(preds[int(rec["pred_index"])], mixmin, views))
    scored = pd.concat([scored.reset_index(drop=True), pd.DataFrame(hidden_rows)], axis=1)
    scored["hidden_guard"] = (
        scored["hidden_core_mean_delta"].lt(0.0)
        & scored["hidden_core_improve_count"].ge(3)
        & scored["hidden_all_improve_count"].ge(5)
    )
    scored["validation_support_score"] = (
        scored["world_support_score"]
        + 80.0 * np.maximum(scored["hidden_core_mean_delta"], 0.0)
        + 30.0 * np.maximum(scored["hidden_all_mean_delta"], 0.0)
        + 0.002 * scored["mean_abs_logit_move_vs_mixmin"]
    )
    return scored.sort_values(
        ["prefilter_keep", "hidden_guard", "validation_support_score"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def select_for_anchor(scored: pd.DataFrame) -> pd.DataFrame:
    toward = scored[
        scored["direction"].eq("toward_teacher")
        & scored["prefilter_keep"]
        & scored["hidden_guard"]
        & scored["mean_abs_logit_move_vs_mixmin"].le(0.035)
    ].copy()
    pieces = []
    if len(toward):
        pieces.append(toward.sort_values("world_support_score").head(900))
        pieces.append(toward.sort_values("hidden_core_mean_delta").head(600))
        pieces.append(toward.sort_values("mean_abs_logit_move_vs_mixmin").head(400))
        for target_name, part in toward.groupby("target_mask", dropna=False):
            pieces.append(part.sort_values("world_support_score").head(80))
        for scale, part in toward.groupby("scale", dropna=False):
            pieces.append(part.sort_values("world_support_score").head(120))
    reverse = scored[
        scored["direction"].eq("reverse_control")
        & scored["mean_abs_logit_move_vs_mixmin"].le(0.035)
    ].copy()
    if len(reverse):
        pieces.append(reverse.sort_values(["hidden_core_mean_delta", "world_support_score"]).head(450))
    if not pieces:
        return scored.head(min(800, len(scored))).reset_index(drop=True)
    return pd.concat(pieces, ignore_index=False).drop_duplicates("pred_index").head(2400).reset_index(drop=True)


def response_table(scores: pd.DataFrame, group_col: str) -> pd.DataFrame:
    part = scores[scores["direction"].eq("toward_teacher")].copy()
    rows = []
    for name, group in part.groupby(group_col, dropna=False):
        best = group.sort_values("anchor_delta_vs_mixmin").iloc[0]
        rows.append(
            {
                group_col: name,
                "n": int(len(group)),
                "anchor_beats": int(group["anchor_beats_mixmin"].sum()),
                "anchor_margin": int(group["anchor_margin_gate"].sum()),
                "best_delta": float(best["anchor_delta_vs_mixmin"]),
                "median_delta": float(group["anchor_delta_vs_mixmin"].median()),
                "best_move": float(best["mean_abs_logit_move_vs_mixmin"]),
                "best_candidate": str(best["candidate"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["best_delta", group_col]).reset_index(drop=True)


def save_submission(sample: pd.DataFrame, pred: np.ndarray) -> str:
    out_name = f"submission_nearzero_amp_{stable_tag(pred)}.csv"
    out = sample.copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / out_name, index=False)
    return out_name


def write_report(
    scores: pd.DataFrame,
    target_response: pd.DataFrame,
    scale_response: pd.DataFrame,
    total_candidates: int,
    selected_count: int,
    saved_submission: str | None,
) -> None:
    top_cols = [
        "candidate",
        "direction",
        "actual_anchor_score_final",
        "anchor_delta_vs_mixmin",
        "anchor_margin_gate",
        "hidden_core_mean_delta",
        "raw_energy_quarter_median_delta",
        "raw_energy_quarter_p90_delta",
        "mean_abs_logit_move_vs_mixmin",
        "movement_guard",
        "world_guard",
        "hidden_guard",
        "eligible_submission_gate",
    ]
    top = scores[scores["direction"].ne("reference")].head(30)
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    summary = scores[scores["direction"].ne("reference")].groupby("direction", dropna=False).agg(
        scored=("candidate", "size"),
        anchor_beats=("anchor_beats_mixmin", "sum"),
        anchor_margin=("anchor_margin_gate", "sum"),
        hidden_guard=("hidden_guard", "sum"),
        world_guard=("world_guard", "sum"),
        movement_guard=("movement_guard", "sum"),
        best_anchor_delta=("anchor_delta_vs_mixmin", "min"),
        median_anchor_delta=("anchor_delta_vs_mixmin", "median"),
        max_move=("mean_abs_logit_move_vs_mixmin", "max"),
    ).reset_index()
    lines = [
        "# E65 Near-Zero Amplitude Response Probe",
        "",
        "## Observe",
        "",
        "E63 has a tiny favorable edge; E64 shows scalar amplification is adverse.",
        "",
        "## Wonder",
        "",
        "Is there a targetwise near-zero amplitude pocket that clears selector margin, or is the local edge bounded below submission scale?",
        "",
        "## Method",
        "",
        f"- Generated near-zero targetwise candidates: `{total_candidates}`.",
        f"- Selected for actual-anchor scoring: `{selected_count}`.",
        "- Tested small scales, target masks, gradient gates, row gates, caps, and flat/core-gain shapes around mixmin.",
        "- Submission eligibility requires toward direction, actual-anchor margin `< -1e-5`, hidden guard, world guard, and movement guard.",
        "",
        "## Direction Summary",
        "",
        e56.markdown_table(summary),
        "",
        "## Target Response",
        "",
        e56.markdown_table(target_response.head(20)),
        "",
        "## Scale Response",
        "",
        e56.markdown_table(scale_response.head(20)),
        "",
        "## Top Scored Candidates",
        "",
        e56.markdown_table(top[[c for c in top_cols if c in top.columns]]),
        "",
        "## Decision",
        "",
        f"- eligible toward-teacher gates: `{int(len(eligible))}`.",
        f"- diagnostic reverse-control gates: `{int(len(reverse))}`.",
    ]
    if len(top):
        rec = top.iloc[0]
        lines.append(f"- best anchor delta: `{rec['anchor_delta_vs_mixmin']:.6g}` from `{rec['candidate']}`.")
    if saved_submission:
        lines.append(f"- saved candidate submission: `{saved_submission}`.")
    else:
        lines.append("- No submission file is justified by E65.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A margin-clearing tiny targetwise pocket would support an amplitude translator. If the best local edge remains sub-margin, E56 gradient energy is a diagnostic rather than the next candidate generator.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TARGET_OUT.relative_to(ROOT)}`",
            f"- `{SCALE_OUT.relative_to(ROOT)}`",
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
    rows, preds = generate_candidates(components, raw_prior, mixmin, views)
    scored = score_candidates(rows, preds, labels, worlds, mixmin, views)
    selected = select_for_anchor(scored)
    scores = e58.attach_anchor_scores(selected, preds, sample, mixmin, a2c8, raw05)
    scores["hidden_guard"] = (
        scores["hidden_core_mean_delta"].lt(0.0)
        & scores["hidden_core_improve_count"].ge(3)
        & scores["hidden_all_improve_count"].ge(5)
    )
    scores["eligible_submission_gate"] = scores["eligible_submission_gate"] & scores["hidden_guard"].fillna(False)
    scores.to_csv(SCAN_OUT, index=False)

    summary_rows = []
    for direction, part in scores[scores["direction"].ne("reference")].groupby("direction"):
        best = part.sort_values("anchor_delta_vs_mixmin").iloc[0]
        summary_rows.append(
            {
                "direction": direction,
                "candidates_scored": int(len(part)),
                "anchor_beats_mixmin": int(part["anchor_beats_mixmin"].sum()),
                "anchor_margin_gate": int(part["anchor_margin_gate"].sum()),
                "movement_guard": int(part["movement_guard"].sum()),
                "world_guard": int(part["world_guard"].sum()),
                "hidden_guard": int(part["hidden_guard"].sum()),
                "eligible_submission_gate": int(part["eligible_submission_gate"].sum()),
                "diagnostic_reverse_gate": int(part["diagnostic_reverse_gate"].sum()),
                "best_anchor_delta_vs_mixmin": float(best["anchor_delta_vs_mixmin"]),
                "best_anchor_candidate": str(best["candidate"]),
                "best_move": float(best["mean_abs_logit_move_vs_mixmin"]),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_response = response_table(scores, "target_mask")
    scale_response = response_table(scores, "scale")
    target_response.to_csv(TARGET_OUT, index=False)
    scale_response.to_csv(SCALE_OUT, index=False)

    saved_submission = None
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    if len(eligible) and not len(reverse):
        best = eligible.sort_values(["anchor_delta_vs_mixmin", "mean_abs_logit_move_vs_mixmin"]).iloc[0]
        saved_submission = save_submission(sample, preds[int(best["pred_index"])])

    write_report(scores, target_response, scale_response, len(rows), len(selected), saved_submission)
    best_toward = summary[summary["direction"].eq("toward_teacher")]
    best_reverse = summary[summary["direction"].eq("reverse_control")]
    toward_delta = float(best_toward.iloc[0]["best_anchor_delta_vs_mixmin"]) if len(best_toward) else float("nan")
    reverse_delta = float(best_reverse.iloc[0]["best_anchor_delta_vs_mixmin"]) if len(best_reverse) else float("nan")
    print(
        f"generated={len(rows)} scored={len(selected)} eligible={len(eligible)} reverse_diag={len(reverse)} "
        f"best_toward_anchor_delta={toward_delta:.6g} "
        f"best_reverse_anchor_delta={reverse_delta:.6g} saved={saved_submission}"
    )
    print(summary.to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
