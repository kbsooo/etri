#!/usr/bin/env python3
"""E58 anchor-constrained distillation of E56 mixmin-hard posterior energy.

E56 found a coherent mixmin-hard/raw-prior posterior, but E57 showed direct
posterior averaging is public-anchor adverse. This probe asks a narrower
question: can the E56 posterior be used as a teacher only on cells where its
own world geometry is confident, while staying close to the active mixmin
frontier under independent actual-anchor stress?
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
from raw05_anchor_jepa_micro_injection import actual_anchor_score  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCAN_OUT = OUT / "mixmin_hard_posterior_distillation_probe_scan.csv"
SUMMARY_OUT = OUT / "mixmin_hard_posterior_distillation_probe_summary.csv"
REPORT_OUT = OUT / "mixmin_hard_posterior_distillation_probe_report.md"

RAW05_FILE = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"


TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_q3_s3": ["Q1", "Q3", "S3"],
    "q1_q3_s": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "s2_s3": ["S2", "S3"],
    "q2_s2_s3": ["Q2", "S2", "S3"],
}

WEIGHTS = [0.006, 0.010, 0.016, 0.024, 0.035, 0.050, 0.070, 0.095]
CAPS = [0.010, 0.018, 0.030, 0.050, 0.080, 0.120]
ANCHOR_MARGIN = 1.0e-5


def clip_prob(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), e56.EPS, 1.0 - e56.EPS)


def sigmoid(x: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def stable_tag(arr: np.ndarray, prefix: str = "") -> str:
    return prefix + hashlib.sha1(np.asarray(arr, dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def binary_logloss_by_world(prob: np.ndarray, labels: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)[None, :, :]
    y = np.asarray(labels, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean(axis=(1, 2))


def band_stats(delta: np.ndarray, mask: np.ndarray, prefix: str) -> dict[str, float | int]:
    if not mask.any():
        return {
            f"{prefix}_worlds": 0,
            f"{prefix}_better_rate": np.nan,
            f"{prefix}_median_delta": np.nan,
            f"{prefix}_p90_delta": np.nan,
            f"{prefix}_max_delta": np.nan,
        }
    sub = delta[mask]
    return {
        f"{prefix}_worlds": int(mask.sum()),
        f"{prefix}_better_rate": float((sub < 0.0).mean()),
        f"{prefix}_median_delta": float(np.median(sub)),
        f"{prefix}_p90_delta": float(np.quantile(sub, 0.90)),
        f"{prefix}_max_delta": float(np.max(sub)),
    }


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
    row_values = values.mean(axis=1)
    threshold = float(np.quantile(row_values, q))
    if high:
        return (row_values >= threshold).astype(np.float64).reshape(-1, 1)
    return (row_values <= threshold).astype(np.float64).reshape(-1, 1)


def posterior_components(
    labels: np.ndarray,
    worlds: pd.DataFrame,
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
) -> dict[str, dict[str, np.ndarray]]:
    masks = {
        "all": np.ones(len(labels), dtype=bool),
        "raw_energy_half": worlds["raw_ce_energy_rank_pct"].le(0.50).to_numpy(),
        "raw_energy_quarter": worlds["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
        "low_slack_half": worlds["sum_abs_residual"].rank(pct=True).le(0.50).to_numpy(),
    }
    out: dict[str, dict[str, np.ndarray]] = {}
    for name, mask in masks.items():
        if int(mask.sum()) < 3:
            continue
        subset = labels[mask]
        world_mean = subset.mean(axis=0)
        posterior = e56.posterior_prob_from_labels(subset, raw_prior)
        delta = logit(posterior) - logit(mixmin)
        support = np.where(delta >= 0.0, world_mean, 1.0 - world_mean)
        entropy = -(world_mean * np.log(clip_prob(world_mean)) + (1.0 - world_mean) * np.log(clip_prob(1.0 - world_mean)))
        out[name] = {
            "posterior": posterior,
            "delta": delta,
            "world_mean": world_mean,
            "support": support,
            "entropy": entropy,
            "mask": mask,
        }
    return out


def make_cell_gates(component: dict[str, np.ndarray], raw_prior: np.ndarray, mixmin: np.ndarray) -> dict[str, np.ndarray]:
    delta = component["delta"]
    abs_delta = np.abs(delta)
    support = component["support"]
    entropy = component["entropy"]
    raw_delta = logit(raw_prior) - logit(mixmin)
    raw_agree = ((np.sign(delta) == np.sign(raw_delta)) & (np.abs(raw_delta) > 1e-8)).astype(np.float64)
    high_abs60 = quantile_gate(abs_delta, 0.60, high=True)
    high_abs75 = quantile_gate(abs_delta, 0.75, high=True)
    high_support60 = quantile_gate(support, 0.60, high=True)
    low_entropy40 = quantile_gate(entropy, 0.40, high=False)
    return {
        "all": np.ones_like(delta, dtype=np.float64),
        "raw_agree": raw_agree,
        "high_abs60": high_abs60,
        "high_abs75": high_abs75,
        "support60": high_support60,
        "low_entropy40": low_entropy40,
        "agree_support60": raw_agree * high_support60,
        "confident_abs_support": high_abs60 * high_support60,
        "confident_low_entropy": high_abs60 * low_entropy40,
    }


def make_row_gates(component: dict[str, np.ndarray], raw_prior: np.ndarray, mixmin: np.ndarray) -> dict[str, np.ndarray]:
    abs_delta = np.abs(component["delta"])
    raw_abs = np.abs(logit(raw_prior) - logit(mixmin))
    support = component["support"]
    return {
        "all": np.ones((abs_delta.shape[0], 1), dtype=np.float64),
        "teacher_row_top50": row_gate(abs_delta, 0.50, high=True),
        "teacher_row_top70": row_gate(abs_delta, 0.70, high=True),
        "raw_row_top50": row_gate(raw_abs, 0.50, high=True),
        "support_row_top50": row_gate(support, 0.50, high=True),
    }


def movement(prob: np.ndarray, mixmin: np.ndarray) -> dict[str, float]:
    return {
        "mean_abs_prob_move_vs_mixmin": float(np.mean(np.abs(prob - mixmin))),
        "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(logit(prob) - logit(mixmin)))),
        "max_abs_logit_move_vs_mixmin": float(np.max(np.abs(logit(prob) - logit(mixmin)))),
    }


def target_movements(prob: np.ndarray, mixmin: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        out[f"mean_prob_delta_{target}"] = float((prob[:, j] - mixmin[:, j]).mean())
        out[f"mean_abs_prob_delta_{target}"] = float(np.abs(prob[:, j] - mixmin[:, j]).mean())
    return out


def generate_candidates(
    components: dict[str, dict[str, np.ndarray]],
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
) -> tuple[pd.DataFrame, list[np.ndarray]]:
    base_logit = logit(mixmin)
    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for band, component in components.items():
        cell_gates = make_cell_gates(component, raw_prior, mixmin)
        row_gates = make_row_gates(component, raw_prior, mixmin)
        teacher_delta = component["delta"]
        for direction_name, direction in [("toward_teacher", 1.0), ("reverse_control", -1.0)]:
            for target_name in TARGET_MASKS:
                tgate = target_mask(target_name)
                for cell_gate_name, cgate in cell_gates.items():
                    for row_gate_name, rgate in row_gates.items():
                        gate = tgate * cgate * rgate
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
                                        "candidate": f"{direction_name}|{band}|{target_name}|{cell_gate_name}|{row_gate_name}|w{weight:.3f}|c{cap:.3f}",
                                        "pred_index": len(preds),
                                        "direction": direction_name,
                                        "band": band,
                                        "target_mask": target_name,
                                        "cell_gate": cell_gate_name,
                                        "row_gate": row_gate_name,
                                        "weight": weight,
                                        "cap": cap,
                                        "active_gate_mean": active,
                                        "hash": tag,
                                    }
                                )
                                preds.append(pred)
    return pd.DataFrame(rows), preds


def score_prefilter(
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    labels: np.ndarray,
    worlds: pd.DataFrame,
    mixmin: np.ndarray,
) -> pd.DataFrame:
    mix_loss = binary_logloss_by_world(mixmin, labels)
    bands = {
        "world_all": np.ones(len(labels), dtype=bool),
        "raw_energy_half": worlds["raw_ce_energy_rank_pct"].le(0.50).to_numpy(),
        "raw_energy_quarter": worlds["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
        "low_slack_half": worlds["sum_abs_residual"].rank(pct=True).le(0.50).to_numpy(),
    }
    out_rows: list[dict[str, Any]] = []
    for rec, prob in zip(rows.to_dict("records"), preds, strict=True):
        delta = binary_logloss_by_world(prob, labels) - mix_loss
        scored = dict(rec)
        for band, mask in bands.items():
            scored.update(band_stats(delta, mask, band))
        scored.update(movement(prob, mixmin))
        scored.update(target_movements(prob, mixmin))
        scored["world_support_score"] = (
            scored["raw_energy_quarter_median_delta"]
            + 0.25 * scored["raw_energy_quarter_p90_delta"]
            + 0.10 * scored["world_all_median_delta"]
            + max(scored["mean_abs_logit_move_vs_mixmin"] - 0.08, 0.0)
        )
        out_rows.append(scored)
    scored_rows = pd.DataFrame(out_rows)
    scored_rows["prefilter_keep"] = (
        scored_rows["mean_abs_logit_move_vs_mixmin"].le(0.12)
        & (
            scored_rows["raw_energy_quarter_median_delta"].lt(0.0)
            | scored_rows["world_all_median_delta"].lt(0.0)
        )
    )
    return scored_rows.sort_values(["prefilter_keep", "world_support_score"], ascending=[False, True]).reset_index(drop=True)


def attach_anchor_scores(frame: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame, mixmin: np.ndarray, a2c8: np.ndarray, raw05: np.ndarray) -> pd.DataFrame:
    if "pred_index" in frame.columns:
        candidate_indices = frame["pred_index"].to_numpy(dtype=int)
    else:
        candidate_indices = frame.index.to_numpy()
    score_preds = [mixmin, a2c8, raw05] + [preds[int(i)] for i in candidate_indices]
    anchor = actual_anchor_score(score_preds, sample)
    mixmin_anchor = float(anchor.iloc[0]["actual_anchor_score_final"])
    ref = pd.DataFrame(
        [
            {
                "candidate": "mixmin",
                "direction": "reference",
                "actual_anchor_score_final": float(anchor.iloc[0]["actual_anchor_score_final"]),
                "anchor_delta_vs_mixmin": 0.0,
                "mean_actual_anchor": float(anchor.iloc[0]["mean_actual_anchor"]),
                "min_set_score": float(anchor.iloc[0]["min_set_score"]),
                "max_set_score": float(anchor.iloc[0]["max_set_score"]),
                **movement(mixmin, mixmin),
            },
            {
                "candidate": "a2c8",
                "direction": "reference",
                "actual_anchor_score_final": float(anchor.iloc[1]["actual_anchor_score_final"]),
                "anchor_delta_vs_mixmin": float(anchor.iloc[1]["actual_anchor_score_final"] - mixmin_anchor),
                "mean_actual_anchor": float(anchor.iloc[1]["mean_actual_anchor"]),
                "min_set_score": float(anchor.iloc[1]["min_set_score"]),
                "max_set_score": float(anchor.iloc[1]["max_set_score"]),
                **movement(a2c8, mixmin),
            },
            {
                "candidate": "raw05",
                "direction": "reference",
                "actual_anchor_score_final": float(anchor.iloc[2]["actual_anchor_score_final"]),
                "anchor_delta_vs_mixmin": float(anchor.iloc[2]["actual_anchor_score_final"] - mixmin_anchor),
                "mean_actual_anchor": float(anchor.iloc[2]["mean_actual_anchor"]),
                "min_set_score": float(anchor.iloc[2]["min_set_score"]),
                "max_set_score": float(anchor.iloc[2]["max_set_score"]),
                **movement(raw05, mixmin),
            },
        ]
    )
    scored = frame.copy()
    cand_anchor = anchor.iloc[3:].reset_index(drop=True)
    scored["actual_anchor_score_final"] = cand_anchor["actual_anchor_score_final"].to_numpy(dtype=np.float64)
    scored["mean_actual_anchor"] = cand_anchor["mean_actual_anchor"].to_numpy(dtype=np.float64)
    scored["min_set_score"] = cand_anchor["min_set_score"].to_numpy(dtype=np.float64)
    scored["max_set_score"] = cand_anchor["max_set_score"].to_numpy(dtype=np.float64)
    scored["anchor_delta_vs_mixmin"] = scored["actual_anchor_score_final"] - mixmin_anchor
    scored["anchor_beats_mixmin"] = scored["anchor_delta_vs_mixmin"] < 0.0
    scored["anchor_margin_gate"] = scored["anchor_delta_vs_mixmin"] < -ANCHOR_MARGIN
    scored["movement_guard"] = scored["mean_abs_logit_move_vs_mixmin"] <= 0.08
    scored["world_guard"] = (
        scored["raw_energy_quarter_median_delta"].lt(0.0)
        & scored["raw_energy_quarter_p90_delta"].le(0.0)
        & scored["world_all_median_delta"].lt(0.0)
    )
    scored["eligible_submission_gate"] = (
        scored["direction"].eq("toward_teacher")
        & scored["anchor_margin_gate"]
        & scored["movement_guard"]
        & scored["world_guard"]
    )
    scored["diagnostic_reverse_gate"] = (
        scored["direction"].eq("reverse_control")
        & scored["anchor_margin_gate"]
        & scored["movement_guard"]
    )
    scored["selection_score"] = (
        scored["anchor_delta_vs_mixmin"]
        + 0.02 * np.maximum(scored["mean_abs_logit_move_vs_mixmin"] - 0.05, 0.0)
        + 0.10 * np.maximum(scored["raw_energy_quarter_p90_delta"], 0.0)
    )
    scored = scored.sort_values(
        ["eligible_submission_gate", "anchor_delta_vs_mixmin", "world_support_score"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    return pd.concat([ref, scored], ignore_index=True, sort=False)


def write_report(scores: pd.DataFrame, total_candidates: int, prefilter_count: int) -> None:
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
    top = scores[scores["direction"].ne("reference")].head(20)
    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    reverse = scores[scores.get("diagnostic_reverse_gate", False).fillna(False)]
    best_toward = scores[scores["direction"].eq("toward_teacher")].head(1)
    best_reverse = scores[scores["direction"].eq("reverse_control")].head(1)
    lines = [
        "# E58 Mixmin-Hard Posterior Distillation Probe",
        "",
        "## Observe",
        "",
        "E56 posterior is internally coherent, while E57 rejects direct posterior averaging under actual-anchor safety.",
        "",
        "## Wonder",
        "",
        "Can E56 posterior energy be distilled only on confident cells and still stay public-anchor-compatible near mixmin?",
        "",
        "## Method",
        "",
        f"- Generated latent-gated candidates from E56 posterior components: `{total_candidates}`.",
        f"- Prefiltered by movement and world-support before actual-anchor scoring: `{prefilter_count}`.",
        "- Candidate generation used teacher band, target mask, raw-agreement/support/entropy cell gates, row gates, caps, and small weights.",
        "- Actual-anchor score was used only as a final safety stress, not to generate per-cell directions.",
        f"- Submission eligibility requires actual-anchor improvement margin `< {-ANCHOR_MARGIN:g}` versus mixmin.",
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
        lines.append(
            f"- best toward-teacher anchor delta: `{rec['anchor_delta_vs_mixmin']:.6g}` from `{rec['candidate']}`."
        )
    if len(best_reverse):
        rec = best_reverse.iloc[0]
        lines.append(
            f"- best reverse-control anchor delta: `{rec['anchor_delta_vs_mixmin']:.6g}` from `{rec['candidate']}`."
        )
    if len(eligible) == 0:
        lines.append("- No submission file is justified by E58.")
    else:
        lines.append("- A candidate passed local E58 gates and still needs final human/public-risk framing before submission.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "If toward-teacher gates are empty while reverse controls improve anchor stress, E56 posterior is useful mainly as an adverse energy axis. If neither direction improves anchor stress, the E56 posterior is a hidden-world diagnostic but not the next probability movement.",
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
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)

    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw05 = load_sub(RAW05_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)

    components = posterior_components(labels, worlds, raw_prior, mixmin)
    rows, preds = generate_candidates(components, raw_prior, mixmin)
    prefilter = score_prefilter(rows, preds, labels, worlds, mixmin)
    toward_keep = prefilter[prefilter["prefilter_keep"] & prefilter["direction"].eq("toward_teacher")].head(900)
    reverse_keep = (
        prefilter[prefilter["direction"].eq("reverse_control") & prefilter["mean_abs_logit_move_vs_mixmin"].le(0.08)]
        .sort_values(["mean_abs_logit_move_vs_mixmin", "world_support_score"])
        .head(300)
    )
    keep = pd.concat([toward_keep, reverse_keep], ignore_index=False)
    if len(keep) < min(250, len(prefilter)):
        keep = prefilter.head(min(250, len(prefilter))).copy()
    scores = attach_anchor_scores(keep, preds, sample, mixmin, a2c8, raw05)
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
    write_report(scores, len(rows), len(keep))

    eligible = scores[scores.get("eligible_submission_gate", False).fillna(False)]
    best_toward = scores[scores["direction"].eq("toward_teacher")].head(1)
    best_reverse = scores[scores["direction"].eq("reverse_control")].head(1)
    best_toward_delta = float(best_toward.iloc[0]["anchor_delta_vs_mixmin"]) if len(best_toward) else float("nan")
    best_reverse_delta = float(best_reverse.iloc[0]["anchor_delta_vs_mixmin"]) if len(best_reverse) else float("nan")
    print(
        f"generated={len(rows)} scored={len(keep)} eligible={len(eligible)} "
        f"best_toward_anchor_delta={best_toward_delta:.6g} "
        f"best_reverse_anchor_delta={best_reverse_delta:.6g}"
    )
    print(summary.to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
