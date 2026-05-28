#!/usr/bin/env python3
"""E62 transition-gated E56 posterior distillation probe.

E58 showed that simple E56 teacher slicing is below selector-scale margin.
E60 showed that transition residuals contain hidden mixmin sign, but direct
transition predictions collapse row calibration. This probe asks the narrower
question: can transition residuals act only as gates for small E56 teacher
movement, rather than as probability targets?
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import re
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import calendar_flank_block_count_state_probe as e53  # noqa: E402
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402
import transition_residual_block_state_probe as e60  # noqa: E402


SCAN_OUT = OUT / "transition_gated_posterior_distillation_probe_scan.csv"
SUMMARY_OUT = OUT / "transition_gated_posterior_distillation_probe_summary.csv"
TRANSITION_OUT = OUT / "transition_gated_posterior_distillation_probe_transition_views.csv"
REPORT_OUT = OUT / "transition_gated_posterior_distillation_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
ANCHOR_MARGIN = 1.0e-5
EPS = 1e-6

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "no_s3": ["Q1", "Q2", "Q3", "S1", "S2", "S4"],
    "q1_q3_s": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "s2_s3": ["S2", "S3"],
    "q2_s2_s3": ["Q2", "S2", "S3"],
}

WEIGHTS = [0.006, 0.010, 0.016, 0.024, 0.035, 0.050, 0.070]
CAPS = [0.010, 0.018, 0.030, 0.050, 0.080]


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)


def sign_agree(a: np.ndarray, b: np.ndarray, min_abs_b: float = 1e-8) -> np.ndarray:
    return ((np.sign(a) == np.sign(b)) & (np.abs(b) > min_abs_b)).astype(np.float64)


def quantile_gate(values: np.ndarray, q: float, high: bool = True) -> np.ndarray:
    gate = np.zeros_like(values, dtype=np.float64)
    for j in range(values.shape[1]):
        threshold = float(np.quantile(values[:, j], q))
        if high:
            gate[:, j] = values[:, j] >= threshold
        else:
            gate[:, j] = values[:, j] <= threshold
    return gate


def row_gate(values: np.ndarray, q: float, high: bool = True) -> np.ndarray:
    row_values = np.asarray(values, dtype=np.float64).mean(axis=1)
    threshold = float(np.quantile(row_values, q))
    if high:
        return (row_values >= threshold).astype(np.float64).reshape(-1, 1)
    return (row_values <= threshold).astype(np.float64).reshape(-1, 1)


def submission_frame(sample: pd.DataFrame, prob: np.ndarray) -> pd.DataFrame:
    out = sample.copy()
    out[TARGETS] = clip_prob(prob)
    return out


def block_rates_to_rows(state: e55.BaseState, block_rates: np.ndarray, sample: pd.DataFrame) -> np.ndarray:
    out = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    for i, block in enumerate(state.hidden_blocks):
        sub_idx = state.rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        out[sub_idx] = block_rates[i]
    if np.isnan(out).any():
        bad = np.where(np.isnan(out).any(axis=1))[0][:10].tolist()
        raise ValueError(f"missing transition row rates for sample rows: {bad}")
    return clip_prob(out)


def parse_transition_method(method: str) -> tuple[str, str, int, float, float]:
    match = re.fullmatch(r"transition_(.+)_base(.+)_k(\d+)_a([0-9.]+)_w([0-9.]+)", method)
    if not match:
        raise ValueError(f"not a transition method: {method}")
    context, base, k, alpha, strength = match.groups()
    return context, base, int(k), float(alpha), float(strength)


def hidden_rate_for_method(state: e55.BaseState, method: str) -> tuple[np.ndarray, pd.DataFrame]:
    if method == "subject_mean":
        return clip_prob(state.hidden_subject), pd.DataFrame()
    if method == "calendar_count_strict":
        return clip_prob(state.hidden_calendar), pd.DataFrame()
    if method == "raw_phone_base":
        return clip_prob(state.hidden_raw), pd.DataFrame()
    if method in {"edge_mid", "edge_shrink025", "edge_shrink050"}:
        return clip_prob(e60.base_matrix(state, method, True)), pd.DataFrame()

    context_name, base_name, k, alpha, strength = parse_transition_method(method)
    base_pseudo = e60.base_matrix(state, base_name, False)
    base_hidden = e60.base_matrix(state, base_name, True)
    donor_residual = e60.logit(state.rates) - e60.logit(base_pseudo)
    donor_context = e60.context_matrix(state, context_name, False, base_pseudo)
    hidden_context = e60.context_matrix(state, context_name, True, base_hidden)
    hidden_pred, hidden_meta = e60.residual_knn_predict(
        donor_context,
        hidden_context,
        donor_residual,
        base_hidden,
        state.pseudo_blocks,
        state.hidden_blocks,
        k,
        alpha,
        strength,
        hidden=True,
    )
    return clip_prob(hidden_pred), hidden_meta


def select_transition_methods() -> dict[str, list[str]]:
    summary = pd.read_csv(e60.SUMMARY_OUT)
    row_safe = (
        summary[
            summary["delta_weighted_row_logloss_vs_raw"].le(0.002)
            & summary["delta_transition_residual_mse_vs_raw"].le(0.0)
        ]
        .sort_values(["weighted_mixmin_delta_vs_a2c8", "delta_weighted_row_logloss_vs_raw"])
        .head(3)["method"]
        .astype(str)
        .tolist()
    )
    balanced = (
        summary[
            summary["weighted_mixmin_delta_vs_a2c8"].lt(0.0)
            & summary["delta_weighted_row_logloss_vs_raw"].lt(0.05)
            & summary["delta_transition_residual_mse_vs_raw"].le(0.0)
        ]
        .sort_values(["weighted_mixmin_delta_vs_a2c8", "delta_weighted_row_logloss_vs_raw"])
        .head(10)["method"]
        .astype(str)
        .tolist()
    )
    aggressive = (
        summary[summary["weighted_mixmin_delta_vs_a2c8"].lt(0.0)]
        .sort_values(["weighted_mixmin_delta_vs_a2c8", "delta_weighted_row_logloss_vs_raw"])
        .head(8)["method"]
        .astype(str)
        .tolist()
    )
    return {
        "row_safe": row_safe,
        "balanced_hidden_sign": balanced,
        "aggressive_hidden_sign": aggressive,
    }


def transition_views(
    state: e55.BaseState,
    sample: pd.DataFrame,
    mixmin: np.ndarray,
    a2c8: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], pd.DataFrame]:
    groups = select_transition_methods()
    method_rates: dict[str, np.ndarray] = {}
    rows = []
    for group, methods in groups.items():
        for method in methods:
            if method in method_rates:
                continue
            rates, meta = hidden_rate_for_method(state, method)
            method_rates[method] = rates
            hidden_rows, _ = e60.e54.hidden_alignment(method, sample, state.rows, state.hidden_blocks, rates, meta)
            rec = pd.DataFrame(hidden_rows)
            rows.append(
                {
                    "group": "method",
                    "view": method,
                    "methods": method,
                    "n_methods": 1,
                    "weighted_mixmin_delta_vs_a2c8": float(np.average(rec["expected_mixmin_delta_vs_a2c8"], weights=rec["n_rows"])),
                    "mixmin_better_block_rate": float((rec["expected_mixmin_delta_vs_a2c8"] < 0.0).mean()),
                }
            )

    row_views: dict[str, np.ndarray] = {}
    block_views: dict[str, np.ndarray] = {}
    mixmin_df = submission_frame(sample, mixmin)
    a2c8_df = submission_frame(sample, a2c8)
    for group, methods in groups.items():
        if not methods:
            continue
        logits = np.stack([logit(method_rates[m]) for m in methods], axis=0)
        block_rate = clip_prob(sigmoid(logits.mean(axis=0)))
        row_views[group] = block_rates_to_rows(state, block_rate, sample)
        block_views[group] = block_rate
        d_mix = e53.expected_block_delta(sample, state.rows, state.hidden_blocks, block_rate, mixmin_df, a2c8_df)
        weights = np.asarray([b.n for b in state.hidden_blocks], dtype=np.float64)
        rows.append(
            {
                "group": "aggregate",
                "view": group,
                "methods": ";".join(methods),
                "n_methods": len(methods),
                "weighted_mixmin_delta_vs_a2c8": float(np.average(d_mix.mean(axis=1), weights=weights)),
                "mixmin_better_block_rate": float((d_mix.mean(axis=1) < 0.0).mean()),
            }
        )
    return row_views, block_views, pd.DataFrame(rows)


def block_good_gate(
    state: e55.BaseState,
    sample: pd.DataFrame,
    block_rates: np.ndarray,
    mixmin: np.ndarray,
    a2c8: np.ndarray,
    targetwise: bool,
) -> np.ndarray:
    d_mix = e53.expected_block_delta(
        sample,
        state.rows,
        state.hidden_blocks,
        block_rates,
        submission_frame(sample, mixmin),
        submission_frame(sample, a2c8),
    )
    out = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    for i, block in enumerate(state.hidden_blocks):
        sub_idx = state.rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        good = d_mix[i] < 0.0 if targetwise else np.full(len(TARGETS), d_mix[i].mean() < 0.0)
        out[sub_idx] = good.astype(np.float64)
    return out


def make_transition_gates(
    teacher_delta: np.ndarray,
    raw_delta: np.ndarray,
    transition_delta: dict[str, np.ndarray],
    block_gates: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    balanced = transition_delta.get("balanced_hidden_sign", np.zeros_like(teacher_delta))
    aggressive = transition_delta.get("aggressive_hidden_sign", np.zeros_like(teacher_delta))
    row_safe = transition_delta.get("row_safe", np.zeros_like(teacher_delta))

    bal_agree = sign_agree(teacher_delta, balanced)
    agg_agree = sign_agree(teacher_delta, aggressive)
    raw_agree = sign_agree(teacher_delta, raw_delta)
    safe_opposed = (np.sign(teacher_delta) != np.sign(row_safe)) & (np.abs(row_safe) >= np.quantile(np.abs(row_safe), 0.75))
    safe_not_opposed = (~safe_opposed).astype(np.float64)
    bal_abs50 = quantile_gate(np.abs(balanced), 0.50, high=True)
    agg_abs50 = quantile_gate(np.abs(aggressive), 0.50, high=True)
    row_safe_low = row_gate(np.abs(row_safe), 0.50, high=False)

    return {
        "trans_bal_agree": bal_agree,
        "trans_bal_agree_abs50": bal_agree * bal_abs50,
        "trans_bal_raw_consensus": bal_agree * raw_agree,
        "trans_bal_agg_consensus": bal_agree * agg_agree,
        "trans_bal_agg_raw": bal_agree * agg_agree * raw_agree,
        "trans_safe_not_opposed": bal_agree * safe_not_opposed,
        "trans_row_safe_low": bal_agree * row_safe_low,
        "trans_block_good": block_gates["balanced_block_good"],
        "trans_block_target_good": block_gates["balanced_target_good"],
        "trans_good_bal_agree": block_gates["balanced_target_good"] * bal_agree,
        "trans_good_bal_raw": block_gates["balanced_target_good"] * bal_agree * raw_agree,
        "trans_good_consensus": block_gates["balanced_target_good"] * bal_agree * agg_agree * safe_not_opposed,
        "trans_aggressive_block_good": block_gates["aggressive_block_good"] * bal_agree * agg_agree,
    }


def generate_candidates(
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
    row_views: dict[str, np.ndarray],
    block_gates: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logit = logit(mixmin)
    raw_delta = logit(raw_prior) - logit(mixmin)
    transition_delta = {name: logit(prob) - logit(mixmin) for name, prob in row_views.items()}
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for band, component in components.items():
        teacher_delta = component["delta"]
        base_cell_gates = e58.make_cell_gates(component, raw_prior, mixmin)
        base_row_gates = e58.make_row_gates(component, raw_prior, mixmin)
        transition_cell_gates = make_transition_gates(teacher_delta, raw_delta, transition_delta, block_gates)
        for direction_name, direction in [("toward_teacher", 1.0), ("reverse_control", -1.0)]:
            for target_name in TARGET_MASKS:
                tgate = target_mask(target_name)
                for base_cell_name in ["all", "raw_agree", "support60", "agree_support60", "confident_abs_support"]:
                    base_cell = base_cell_gates[base_cell_name]
                    for trans_gate_name, trans_gate in transition_cell_gates.items():
                        combined_cell = base_cell * trans_gate
                        if combined_cell.mean() <= 0.0:
                            continue
                        for row_gate_name in ["all", "teacher_row_top50", "teacher_row_top70", "support_row_top50"]:
                            rgate = base_row_gates[row_gate_name]
                            gate = tgate * combined_cell * rgate
                            active = float(gate.mean())
                            if active <= 0.0:
                                continue
                            for cap in CAPS:
                                capped = np.clip(teacher_delta, -cap, cap) * gate
                                if np.abs(capped).mean() <= 1e-10:
                                    continue
                                for weight in WEIGHTS:
                                    pred = clip_prob(sigmoid(base_logit + direction * weight * capped))
                                    tag = stable_tag(pred)
                                    if tag in seen:
                                        continue
                                    seen.add(tag)
                                    rows.append(
                                        {
                                            "candidate": (
                                                f"{direction_name}|{band}|{target_name}|{base_cell_name}|"
                                                f"{trans_gate_name}|{row_gate_name}|w{weight:.3f}|c{cap:.3f}"
                                            ),
                                            "pred_index": len(preds),
                                            "direction": direction_name,
                                            "band": band,
                                            "target_mask": target_name,
                                            "base_cell_gate": base_cell_name,
                                            "transition_gate": trans_gate_name,
                                            "row_gate": row_gate_name,
                                            "weight": weight,
                                            "cap": cap,
                                            "active_gate_mean": active,
                                            "hash": tag,
                                        }
                                    )
                                    preds.append(pred)
    return pd.DataFrame(rows), preds


def save_submission(sample: pd.DataFrame, pred: np.ndarray, candidate: str) -> str:
    tag = stable_tag(pred, "transgate_")
    out_name = f"submission_transition_gated_distill_{tag}.csv"
    out = submission_frame(sample, pred)
    out.to_csv(OUT / out_name, index=False)
    return out_name


def write_report(
    scores: pd.DataFrame,
    transition: pd.DataFrame,
    total_candidates: int,
    prefilter_count: int,
    saved_submission: str | None,
) -> None:
    top_cols = [
        "candidate",
        "direction",
        "actual_anchor_score_final",
        "anchor_delta_vs_mixmin",
        "anchor_margin_gate",
        "raw_energy_quarter_median_delta",
        "raw_energy_quarter_p90_delta",
        "world_all_median_delta",
        "mean_abs_logit_move_vs_mixmin",
        "movement_guard",
        "world_guard",
        "eligible_submission_gate",
    ]
    transition_cols = ["group", "view", "n_methods", "weighted_mixmin_delta_vs_a2c8", "mixmin_better_block_rate"]
    top = scores[scores["direction"].ne("reference")].head(20)
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    best_toward = scores[scores["direction"].eq("toward_teacher")].head(1)
    best_reverse = scores[scores["direction"].eq("reverse_control")].head(1)
    lines = [
        "# E62 Transition-Gated Posterior Distillation Probe",
        "",
        "## Observe",
        "",
        "E56 posterior energy is coherent internally, E58 simple slicing is sub-margin, and E60 transition residuals sense hidden mixmin sign only when row calibration collapses.",
        "",
        "## Wonder",
        "",
        "Can transition residuals be used as a gate for E56 teacher cells without using them as probability targets?",
        "",
        "## Method",
        "",
        f"- Generated transition-gated E56 teacher candidates: `{total_candidates}`.",
        f"- Prefiltered by E56-world support and movement before actual-anchor scoring: `{prefilter_count}`.",
        "- Transition views: row-safe residual methods, balanced hidden-sign methods, and aggressive hidden-sign methods.",
        "- Candidate movement remains a small capped logit move from mixmin toward the E56 teacher; transition residuals only open or close gates.",
        f"- Submission eligibility requires actual-anchor improvement margin `< {-ANCHOR_MARGIN:g}` versus mixmin plus movement/world guards.",
        "",
        "## Transition Views",
        "",
        e56.markdown_table(transition[[c for c in transition_cols if c in transition.columns]].head(24)),
        "",
        "## Top Scored Candidates",
        "",
        e56.markdown_table(top[[c for c in top_cols if c in top.columns]].head(20)),
        "",
        "## Decision",
        "",
        f"- eligible toward-teacher submission gates: `{int(len(eligible))}`.",
        f"- diagnostic reverse-control gates: `{int(len(reverse))}`.",
    ]
    if len(best_toward):
        rec = best_toward.iloc[0]
        lines.append(f"- best toward-teacher anchor delta: `{rec['anchor_delta_vs_mixmin']:.6g}` from `{rec['candidate']}`.")
    if len(best_reverse):
        rec = best_reverse.iloc[0]
        lines.append(f"- best reverse-control anchor delta: `{rec['anchor_delta_vs_mixmin']:.6g}` from `{rec['candidate']}`.")
    if saved_submission:
        lines.append(f"- saved eligible submission: `{saved_submission}`.")
    else:
        lines.append("- No submission file is justified by E62.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "If no gate opens, the transition residual axis is a risk diagnostic rather than the missing E56 validator. If only reverse controls improve, transition gates are exposing an adverse E56 direction. If a toward gate opens with margin, it becomes a candidate because it survived two independent hidden-world stresses: E56 world support and E60 transition gating.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TRANSITION_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw05 = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)

    state = e55.build_base_state()
    if not state.sample[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("sample key mismatch between anchor sample and transition state")

    row_views, block_views, transition = transition_views(state, sample, mixmin, a2c8)
    transition.to_csv(TRANSITION_OUT, index=False)
    block_gates = {
        "balanced_block_good": block_good_gate(state, sample, block_views["balanced_hidden_sign"], mixmin, a2c8, targetwise=False),
        "balanced_target_good": block_good_gate(state, sample, block_views["balanced_hidden_sign"], mixmin, a2c8, targetwise=True),
        "aggressive_block_good": block_good_gate(state, sample, block_views["aggressive_hidden_sign"], mixmin, a2c8, targetwise=False),
    }

    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    rows, preds = generate_candidates(components, raw_prior, mixmin, row_views, block_gates)
    prefilter = e58.score_prefilter(rows, preds, labels, worlds, mixmin)
    toward_keep = prefilter[prefilter["prefilter_keep"] & prefilter["direction"].eq("toward_teacher")].head(1000)
    reverse_keep = (
        prefilter[prefilter["direction"].eq("reverse_control") & prefilter["mean_abs_logit_move_vs_mixmin"].le(0.08)]
        .sort_values(["mean_abs_logit_move_vs_mixmin", "world_support_score"])
        .head(300)
    )
    keep = pd.concat([toward_keep, reverse_keep], ignore_index=False)
    if len(keep) < min(250, len(prefilter)):
        keep = prefilter.head(min(250, len(prefilter))).copy()
    scores = e58.attach_anchor_scores(keep, preds, sample, mixmin, a2c8, raw05)
    scores.to_csv(SCAN_OUT, index=False)

    summary_rows = []
    for direction, part in scores[scores["direction"].ne("reference")].groupby("direction"):
        summary_rows.append(
            {
                "direction": direction,
                "candidates_scored": int(len(part)),
                "anchor_beats_mixmin": int(part["anchor_beats_mixmin"].sum()),
                "movement_guard": int(part["movement_guard"].sum()),
                "world_guard": int(part["world_guard"].sum()),
                "eligible_submission_gate": int(part["eligible_submission_gate"].sum()),
                "diagnostic_reverse_gate": int(part["diagnostic_reverse_gate"].sum()),
                "best_anchor_delta_vs_mixmin": float(part["anchor_delta_vs_mixmin"].min()),
                "best_anchor_candidate": str(part.sort_values("anchor_delta_vs_mixmin").iloc[0]["candidate"]),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)

    saved_submission = None
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    if len(eligible):
        best = eligible.sort_values(["anchor_delta_vs_mixmin", "world_support_score"]).iloc[0]
        pred = preds[int(best["pred_index"])]
        saved_submission = save_submission(sample, pred, str(best["candidate"]))

    write_report(scores, transition, len(rows), len(keep), saved_submission)

    best_toward = scores[scores["direction"].eq("toward_teacher")].head(1)
    best_reverse = scores[scores["direction"].eq("reverse_control")].head(1)
    best_toward_delta = float(best_toward.iloc[0]["anchor_delta_vs_mixmin"]) if len(best_toward) else float("nan")
    best_reverse_delta = float(best_reverse.iloc[0]["anchor_delta_vs_mixmin"]) if len(best_reverse) else float("nan")
    print(
        f"generated={len(rows)} scored={len(keep)} eligible={len(eligible)} "
        f"best_toward_anchor_delta={best_toward_delta:.6g} "
        f"best_reverse_anchor_delta={best_reverse_delta:.6g} saved={saved_submission}"
    )
    print(summary.to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
