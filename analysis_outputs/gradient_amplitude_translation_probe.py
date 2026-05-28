#!/usr/bin/env python3
"""E64 amplitude translation probe for E56 gradient-consensus cells.

E63 showed that E56 teacher deltas agree with independent hidden-rate
gradients, but only at sub-margin anchor amplitude. This probe asks whether
the issue is merely scale: keep the E63 direction/gates fixed, then test
larger capped logit amplitudes and gain-shaped moves under the same world,
hidden-rate, movement, and actual-anchor stresses.
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
import gradient_consensus_posterior_probe as e63  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402


SCAN_OUT = OUT / "gradient_amplitude_translation_probe_scan.csv"
SUMMARY_OUT = OUT / "gradient_amplitude_translation_probe_summary.csv"
REPORT_OUT = OUT / "gradient_amplitude_translation_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
EPS = 1e-6

BANDS = ["all", "low_slack_half"]
TARGET_MASKS = ["all", "no_q2_s3", "no_s3", "no_q2"]
BASE_CELL_GATES = ["all", "raw_agree", "support60"]
GRADIENT_GATES = ["grad_core_top50", "grad_all_4of6", "grad_all_abs50"]
ROW_GATES = ["all", "teacher_row_top50"]
CAPS = [0.080, 0.120, 0.180]
SCALES = [0.10, 0.24, 0.50, 0.90, 1.40, 2.00, 2.80]
SHAPES = ["flat", "core_gain"]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def normalize_gain(gain: np.ndarray) -> np.ndarray:
    pos = np.maximum(np.asarray(gain, dtype=np.float64), 0.0)
    out = np.zeros_like(pos, dtype=np.float64)
    for j in range(pos.shape[1]):
        scale = float(np.quantile(pos[:, j], 0.95))
        if scale > 1e-12:
            out[:, j] = np.clip(pos[:, j] / scale, 0.0, 1.0)
    return out


def gradient_gain_shapes(teacher_delta: np.ndarray, mixmin: np.ndarray, views: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    core_names = ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign"]
    all_names = [
        "subject_mean",
        "calendar_count_strict",
        "raw_phone_base",
        "transition_row_safe",
        "transition_balanced_hidden_sign",
        "transition_aggressive_hidden_sign",
    ]
    gains = {}
    for name in all_names:
        grad = mixmin - views[name]
        gains[name] = -(teacher_delta * grad)
    core_gain = np.median(np.stack([gains[name] for name in core_names], axis=0), axis=0)
    all_gain = np.median(np.stack([gains[name] for name in all_names], axis=0), axis=0)
    core_norm = normalize_gain(core_gain)
    all_norm = normalize_gain(all_gain)
    return {
        "flat": np.ones_like(teacher_delta, dtype=np.float64),
        "core_gain": 0.25 + 0.75 * core_norm,
        "all_gain": 0.25 + 0.75 * all_norm,
        "sqrt_core": np.sqrt(np.clip(core_norm, 0.0, 1.0)),
    }


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
            "grad_core_row_top50": e63.row_gate(grad_cell_gates["grad_core_2of3"], 0.50, high=True),
            "teacher_row_top50": base_row_gates["teacher_row_top50"],
            "support_row_top50": base_row_gates["support_row_top50"],
        }
        shape_weights = gradient_gain_shapes(teacher_delta, mixmin, views)
        for direction_name, direction in [("toward_teacher", 1.0), ("reverse_control", -1.0)]:
            for target_name in TARGET_MASKS:
                tgate = e63.target_mask(target_name)
                for base_cell_name in BASE_CELL_GATES:
                    base_cell = base_cell_gates[base_cell_name]
                    for grad_gate_name in GRADIENT_GATES:
                        grad_gate = grad_cell_gates[grad_gate_name]
                        cell_gate = base_cell * grad_gate
                        if cell_gate.mean() <= 0.0:
                            continue
                        for row_gate_name in ROW_GATES:
                            gate = tgate * cell_gate * grad_row_gates[row_gate_name]
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
                                                    f"{grad_gate_name}|{row_gate_name}|{shape_name}|s{scale:.2f}|c{cap:.3f}"
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
        + 60.0 * np.maximum(scored["hidden_core_mean_delta"], 0.0)
        + 20.0 * np.maximum(scored["hidden_all_mean_delta"], 0.0)
        + 0.005 * np.maximum(scored["mean_abs_logit_move_vs_mixmin"] - 0.08, 0.0)
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
        & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)
    ].copy()
    if toward.empty:
        toward = scored[
            scored["direction"].eq("toward_teacher")
            & scored["prefilter_keep"]
            & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)
        ].copy()
    pieces = []
    if len(toward):
        pieces.append(toward.sort_values("world_support_score").head(800))
        pieces.append(toward.sort_values("hidden_core_mean_delta").head(600))
        pieces.append(toward.sort_values("mean_abs_logit_move_vs_mixmin", ascending=False).head(500))
        for lo, hi in [(0.0, 0.01), (0.01, 0.025), (0.025, 0.05), (0.05, 0.08)]:
            part = toward[toward["mean_abs_logit_move_vs_mixmin"].between(lo, hi, inclusive="left")]
            pieces.append(part.sort_values("world_support_score").head(250))
    reverse = scored[
        scored["direction"].eq("reverse_control")
        & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)
    ].copy()
    if len(reverse):
        pieces.append(reverse.sort_values(["hidden_core_mean_delta", "world_support_score"]).head(450))
    selected = pd.concat(pieces, ignore_index=False).drop_duplicates("pred_index")
    return selected.head(2500).reset_index(drop=True)


def write_report(scores: pd.DataFrame, total_candidates: int, selected_count: int, saved_submission: str | None) -> None:
    top_cols = [
        "candidate",
        "direction",
        "actual_anchor_score_final",
        "anchor_delta_vs_mixmin",
        "anchor_margin_gate",
        "hidden_core_mean_delta",
        "hidden_all_mean_delta",
        "raw_energy_quarter_median_delta",
        "raw_energy_quarter_p90_delta",
        "world_all_median_delta",
        "mean_abs_logit_move_vs_mixmin",
        "movement_guard",
        "world_guard",
        "hidden_guard",
        "eligible_submission_gate",
    ]
    top = scores[scores["direction"].ne("reference")].head(30)
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    summary = scores[scores["direction"].ne("reference")].groupby(["direction"], dropna=False).agg(
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
        "# E64 Gradient-Amplitude Translation Probe",
        "",
        "## Observe",
        "",
        "E63 validates E56 teacher direction under independent hidden-rate gradients but fails selector-scale anchor margin.",
        "",
        "## Wonder",
        "",
        "Is E63 only under-amplified, or does public-anchor geometry saturate before the validated direction becomes useful?",
        "",
        "## Method",
        "",
        f"- Generated amplitude-expanded candidates: `{total_candidates}`.",
        f"- Selected for actual-anchor scoring after world, hidden, and movement prefilters: `{selected_count}`.",
        "- Candidate probabilities are larger capped logit moves from mixmin toward E56 teacher on E63 gradient-consensus cells.",
        "- Tested flat and gradient-gain-shaped amplitudes, broader caps, and larger scales, plus reverse controls.",
        "- Submission eligibility still requires toward direction, actual-anchor margin `< -1e-5`, world guard, hidden guard, and movement guard.",
        "",
        "## Direction Summary",
        "",
        e56.markdown_table(summary),
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
        lines.append("- No submission file is justified by E64.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "If larger amplitudes clear margin while reverse controls do not, E63 was under-scaled. If not, the missing variable is not scalar amplitude but a different calibration/targetwise translator.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_submission(sample: pd.DataFrame, pred: np.ndarray) -> str:
    out_name = f"submission_gradamp_translate_{stable_tag(pred)}.csv"
    out = sample.copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / out_name, index=False)
    return out_name


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

    saved_submission = None
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    if len(eligible) and not len(reverse):
        best = eligible.sort_values(["anchor_delta_vs_mixmin", "mean_abs_logit_move_vs_mixmin"]).iloc[0]
        saved_submission = save_submission(sample, preds[int(best["pred_index"])])

    write_report(scores, len(rows), len(selected), saved_submission)
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
