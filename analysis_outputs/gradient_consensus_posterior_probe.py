#!/usr/bin/env python3
"""E63 gradient-consensus posterior probe.

E58/E62 showed that E56 teacher movement is too small after simple gates, and
transition residuals do not rescue it as a mask. This probe changes the
question from "which handcrafted gate looks plausible?" to "does the E56
teacher point down the BCE gradient implied by independent hidden-rate views?"

The independent views are not public-LB optimized: subject/calendar/raw block
rates plus row-safe/balanced/aggressive transition views. Public-anchor scoring
is used only after candidate generation as a final stress.
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
import mixmin_hard_posterior_distillation_probe as e58  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402
import transition_gated_posterior_distillation_probe as e62  # noqa: E402


SCAN_OUT = OUT / "gradient_consensus_posterior_probe_scan.csv"
SUMMARY_OUT = OUT / "gradient_consensus_posterior_probe_summary.csv"
VIEW_OUT = OUT / "gradient_consensus_posterior_probe_view_summary.csv"
REPORT_OUT = OUT / "gradient_consensus_posterior_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
ANCHOR_MARGIN = 1.0e-5
EPS = 1e-6

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "no_s3": ["Q1", "Q2", "Q3", "S1", "S2", "S4"],
    "no_q2_s3": ["Q1", "Q3", "S1", "S2", "S4"],
    "q1_q3_s": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "q_targets": ["Q1", "Q2", "Q3"],
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


def rate_bce(prob: np.ndarray, rate: np.ndarray) -> float:
    p = clip_prob(prob)
    y = clip_prob(rate)
    return float((-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))).mean())


def hidden_row_views(state: e55.BaseState, sample: pd.DataFrame, mixmin: np.ndarray, a2c8: np.ndarray) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    views = {
        "subject_mean": e62.block_rates_to_rows(state, state.hidden_subject, sample),
        "calendar_count_strict": e62.block_rates_to_rows(state, state.hidden_calendar, sample),
        "raw_phone_base": e62.block_rates_to_rows(state, state.hidden_raw, sample),
    }
    transition_rows, transition_blocks, transition_summary = e62.transition_views(state, sample, mixmin, a2c8)
    for name in ["row_safe", "balanced_hidden_sign", "aggressive_hidden_sign"]:
        if name in transition_rows:
            views[f"transition_{name}"] = transition_rows[name]
    core = np.stack([logit(views[k]) for k in ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign"]], axis=0)
    views["core_median"] = clip_prob(sigmoid(np.median(core, axis=0)))

    rows = []
    for name, rate in views.items():
        rows.append(
            {
                "view": name,
                "bce_mixmin": rate_bce(mixmin, rate),
                "bce_a2c8": rate_bce(a2c8, rate),
                "mixmin_delta_vs_a2c8": rate_bce(mixmin, rate) - rate_bce(a2c8, rate),
                "mean_rate": float(rate.mean()),
            }
        )
    view_summary = pd.concat(
        [pd.DataFrame(rows), transition_summary.assign(view=lambda d: "transition_method:" + d["view"].astype(str))],
        ignore_index=True,
        sort=False,
    )
    return views, view_summary


def gradient_gates(teacher_delta: np.ndarray, mixmin: np.ndarray, views: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    core_names = ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign"]
    all_names = [
        "subject_mean",
        "calendar_count_strict",
        "raw_phone_base",
        "transition_row_safe",
        "transition_balanced_hidden_sign",
        "transition_aggressive_hidden_sign",
    ]
    improvements = {}
    first_order = {}
    for name in all_names + ["core_median"]:
        if name not in views:
            continue
        grad = mixmin - views[name]
        score = teacher_delta * grad
        improvements[name] = score < 0.0
        first_order[name] = -score

    core_count = sum(improvements[name].astype(np.float64) for name in core_names if name in improvements)
    all_count = sum(improvements[name].astype(np.float64) for name in all_names if name in improvements)
    core_gain = np.median(np.stack([first_order[name] for name in core_names if name in first_order], axis=0), axis=0)
    all_gain = np.median(np.stack([first_order[name] for name in all_names if name in first_order], axis=0), axis=0)
    core_abs = np.abs(core_gain)
    all_abs = np.abs(all_gain)
    raw_grad = mixmin - views["raw_phone_base"]
    cal_grad = mixmin - views["calendar_count_strict"]
    bal_grad = mixmin - views["transition_balanced_hidden_sign"]

    return {
        "grad_core_2of3": (core_count >= 2).astype(np.float64),
        "grad_core_3of3": (core_count >= 3).astype(np.float64),
        "grad_all_4of6": (all_count >= 4).astype(np.float64),
        "grad_all_5of6": (all_count >= 5).astype(np.float64),
        "grad_all_6of6": (all_count >= 6).astype(np.float64),
        "grad_core_top50": ((core_count >= 2) & (core_gain >= np.quantile(core_gain, 0.50))).astype(np.float64),
        "grad_core_top70": ((core_count >= 2) & (core_gain >= np.quantile(core_gain, 0.70))).astype(np.float64),
        "grad_all_top50": ((all_count >= 4) & (all_gain >= np.quantile(all_gain, 0.50))).astype(np.float64),
        "grad_all_top70": ((all_count >= 4) & (all_gain >= np.quantile(all_gain, 0.70))).astype(np.float64),
        "grad_raw_cal_bal": ((teacher_delta * raw_grad < 0.0) & (teacher_delta * cal_grad < 0.0) & (teacher_delta * bal_grad < 0.0)).astype(np.float64),
        "grad_core_abs50": (core_abs >= np.quantile(core_abs, 0.50)).astype(np.float64) * (core_count >= 2),
        "grad_all_abs50": (all_abs >= np.quantile(all_abs, 0.50)).astype(np.float64) * (all_count >= 4),
    }


def hidden_validation_scores(prob: np.ndarray, mixmin: np.ndarray, views: dict[str, np.ndarray]) -> dict[str, float | int]:
    deltas = {name: rate_bce(prob, rate) - rate_bce(mixmin, rate) for name, rate in views.items()}
    core_names = ["calendar_count_strict", "raw_phone_base", "transition_balanced_hidden_sign", "core_median"]
    all_names = [
        "subject_mean",
        "calendar_count_strict",
        "raw_phone_base",
        "transition_row_safe",
        "transition_balanced_hidden_sign",
        "transition_aggressive_hidden_sign",
        "core_median",
    ]
    out: dict[str, float | int] = {}
    for name, delta in deltas.items():
        out[f"hidden_delta_{name}"] = float(delta)
    core_vals = np.asarray([deltas[name] for name in core_names if name in deltas], dtype=np.float64)
    all_vals = np.asarray([deltas[name] for name in all_names if name in deltas], dtype=np.float64)
    out["hidden_core_mean_delta"] = float(core_vals.mean())
    out["hidden_core_max_delta"] = float(core_vals.max())
    out["hidden_core_improve_count"] = int((core_vals < 0.0).sum())
    out["hidden_all_mean_delta"] = float(all_vals.mean())
    out["hidden_all_max_delta"] = float(all_vals.max())
    out["hidden_all_improve_count"] = int((all_vals < 0.0).sum())
    return out


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
    for band, component in components.items():
        teacher_delta = component["delta"]
        base_cell_gates = e58.make_cell_gates(component, raw_prior, mixmin)
        base_row_gates = e58.make_row_gates(component, raw_prior, mixmin)
        grad_cell_gates = gradient_gates(teacher_delta, mixmin, views)
        grad_row_gates = {
            "all": np.ones((teacher_delta.shape[0], 1), dtype=np.float64),
            "grad_core_row_top50": row_gate(grad_cell_gates["grad_core_2of3"], 0.50, high=True),
            "grad_all_row_top50": row_gate(grad_cell_gates["grad_all_4of6"], 0.50, high=True),
            "teacher_row_top50": base_row_gates["teacher_row_top50"],
            "support_row_top50": base_row_gates["support_row_top50"],
        }
        for direction_name, direction in [("toward_teacher", 1.0), ("reverse_control", -1.0)]:
            for target_name in TARGET_MASKS:
                tgate = target_mask(target_name)
                for base_cell_name in ["all", "raw_agree", "support60", "agree_support60", "confident_abs_support"]:
                    base_cell = base_cell_gates[base_cell_name]
                    for grad_gate_name, grad_gate in grad_cell_gates.items():
                        cell_gate = base_cell * grad_gate
                        if cell_gate.mean() <= 0.0:
                            continue
                        for row_gate_name, rgate in grad_row_gates.items():
                            gate = tgate * cell_gate * rgate
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
                                                f"{grad_gate_name}|{row_gate_name}|w{weight:.3f}|c{cap:.3f}"
                                            ),
                                            "pred_index": len(preds),
                                            "direction": direction_name,
                                            "band": band,
                                            "target_mask": target_name,
                                            "base_cell_gate": base_cell_name,
                                            "gradient_gate": grad_gate_name,
                                            "row_gate": row_gate_name,
                                            "weight": weight,
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
        pred = preds[int(rec["pred_index"])]
        hidden_rows.append(hidden_validation_scores(pred, mixmin, views))
    hidden = pd.DataFrame(hidden_rows)
    scored = pd.concat([scored.reset_index(drop=True), hidden], axis=1)
    scored["hidden_guard"] = (
        scored["hidden_core_mean_delta"].lt(0.0)
        & scored["hidden_core_improve_count"].ge(3)
        & scored["hidden_all_improve_count"].ge(5)
    )
    scored["validation_support_score"] = (
        scored["world_support_score"]
        + 100.0 * np.maximum(scored["hidden_core_mean_delta"], 0.0)
        + 50.0 * np.maximum(scored["hidden_all_mean_delta"], 0.0)
    )
    return scored.sort_values(
        ["prefilter_keep", "hidden_guard", "validation_support_score"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def save_submission(sample: pd.DataFrame, pred: np.ndarray) -> str:
    out_name = f"submission_gradconsensus_distill_{stable_tag(pred)}.csv"
    out = sample.copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / out_name, index=False)
    return out_name


def write_report(scores: pd.DataFrame, views: pd.DataFrame, total_candidates: int, prefilter_count: int, saved_submission: str | None) -> None:
    top_cols = [
        "candidate",
        "direction",
        "actual_anchor_score_final",
        "anchor_delta_vs_mixmin",
        "anchor_margin_gate",
        "hidden_core_mean_delta",
        "hidden_core_max_delta",
        "hidden_core_improve_count",
        "hidden_all_improve_count",
        "raw_energy_quarter_median_delta",
        "raw_energy_quarter_p90_delta",
        "mean_abs_logit_move_vs_mixmin",
        "movement_guard",
        "world_guard",
        "hidden_guard",
        "eligible_submission_gate",
    ]
    view_cols = ["view", "bce_mixmin", "bce_a2c8", "mixmin_delta_vs_a2c8", "weighted_mixmin_delta_vs_a2c8", "mixmin_better_block_rate"]
    top = scores[scores["direction"].ne("reference")].head(24)
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    best_toward = scores[scores["direction"].eq("toward_teacher")].head(1)
    best_reverse = scores[scores["direction"].eq("reverse_control")].head(1)
    lines = [
        "# E63 Gradient-Consensus Posterior Probe",
        "",
        "## Observe",
        "",
        "E56 teacher energy is coherent but sub-margin under simple gates. E60 transition residuals are sign-informative but unsafe. The missing piece may be an independent gradient validator rather than another handcrafted gate.",
        "",
        "## Wonder",
        "",
        "Does E56 teacher movement point down the BCE gradient implied by independent hidden-rate views?",
        "",
        "## Method",
        "",
        f"- Generated gradient-consensus E56 candidates: `{total_candidates}`.",
        f"- Prefiltered by E56-world support, hidden-view support, and movement before actual-anchor scoring: `{prefilter_count}`.",
        "- Independent views: subject mean, calendar strict, raw phone, transition row-safe, transition balanced, transition aggressive, and core median.",
        "- Candidate probabilities are still capped logit moves from mixmin toward E56 teacher; hidden views only define gradient gates and validation deltas.",
        f"- Submission eligibility requires actual-anchor improvement margin `< {-ANCHOR_MARGIN:g}` plus world, movement, and hidden guards.",
        "",
        "## Hidden Views",
        "",
        e56.markdown_table(views[[c for c in view_cols if c in views.columns]].head(24)),
        "",
        "## Top Scored Candidates",
        "",
        e56.markdown_table(top[[c for c in top_cols if c in top.columns]].head(24)),
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
        lines.append("- No submission file is justified by E63.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "If gradient-consensus gates beat E58/E62 with selector-scale margin, E56 teacher has independent non-anchor support. If they remain sub-margin or require reverse movement, then the hidden-rate views do not validate E56 as a probability translator.",
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{VIEW_OUT.relative_to(ROOT)}`",
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

    views, view_summary = hidden_row_views(state, sample, mixmin, a2c8)
    view_summary.to_csv(VIEW_OUT, index=False)
    components = e58.posterior_components(labels, worlds, raw_prior, mixmin)
    rows, preds = generate_candidates(components, raw_prior, mixmin, views)
    scored = score_candidates(rows, preds, labels, worlds, mixmin, views)

    toward_keep = scored[
        scored["prefilter_keep"]
        & scored["hidden_guard"]
        & scored["direction"].eq("toward_teacher")
        & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)
    ].head(1000)
    if len(toward_keep) < 400:
        toward_keep = scored[
            scored["prefilter_keep"]
            & scored["direction"].eq("toward_teacher")
            & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)
        ].head(1000)
    reverse_keep = (
        scored[scored["direction"].eq("reverse_control") & scored["mean_abs_logit_move_vs_mixmin"].le(0.08)]
        .sort_values(["hidden_core_mean_delta", "world_support_score"])
        .head(300)
    )
    keep = pd.concat([toward_keep, reverse_keep], ignore_index=False)
    if len(keep) < min(250, len(scored)):
        keep = scored.head(min(250, len(scored))).copy()
    scores = e58.attach_anchor_scores(keep, preds, sample, mixmin, a2c8, raw05)
    scores["hidden_guard"] = (
        scores["hidden_core_mean_delta"].lt(0.0)
        & scores["hidden_core_improve_count"].ge(3)
        & scores["hidden_all_improve_count"].ge(5)
    )
    scores["eligible_submission_gate"] = scores["eligible_submission_gate"] & scores["hidden_guard"].fillna(False)
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
                "hidden_guard": int(part["hidden_guard"].sum()),
                "eligible_submission_gate": int(part["eligible_submission_gate"].sum()),
                "diagnostic_reverse_gate": int(part["diagnostic_reverse_gate"].sum()),
                "best_anchor_delta_vs_mixmin": float(part["anchor_delta_vs_mixmin"].min()),
                "best_anchor_candidate": str(part.sort_values("anchor_delta_vs_mixmin").iloc[0]["candidate"]),
                "best_hidden_core_mean_delta": float(part.sort_values("hidden_core_mean_delta").iloc[0]["hidden_core_mean_delta"]),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)

    saved_submission = None
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    if len(eligible):
        best = eligible.sort_values(["anchor_delta_vs_mixmin", "hidden_core_mean_delta"]).iloc[0]
        saved_submission = save_submission(sample, preds[int(best["pred_index"])])

    write_report(scores, view_summary, len(rows), len(keep), saved_submission)
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
