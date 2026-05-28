#!/usr/bin/env python3
"""E57 safety stress for E56 mixmin-hard raw posterior candidates.

E56 produced strong world-internal leave-one-world gains, but those worlds are
generated from the same mixmin-hard/raw-prior constraints. This stress asks the
opposite LeJEPA question: do the posterior candidates still look healthy under
the independent actual-anchor/public-shape proxy that previously caught many
overfit latent moves?
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
from raw05_anchor_jepa_micro_injection import actual_anchor_score  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCORE_OUT = OUT / "mixmin_hard_raw_posterior_safety_stress_scores.csv"
REPORT_OUT = OUT / "mixmin_hard_raw_posterior_safety_stress_report.md"


def binary_logloss(prob: np.ndarray, labels: np.ndarray) -> float:
    p = e56.clip_prob(prob)
    y = np.asarray(labels, dtype=np.float64)
    return float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean())


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


def build_variants(
    labels: np.ndarray,
    worlds: pd.DataFrame,
    raw_prior: np.ndarray,
    mixmin: np.ndarray,
) -> list[tuple[str, str, float, np.ndarray]]:
    masks = {
        "all": np.ones(len(labels), dtype=bool),
        "raw_energy_half": worlds["raw_ce_energy_rank_pct"].le(0.50).to_numpy(),
        "raw_energy_quarter": worlds["raw_ce_energy_rank_pct"].le(0.25).to_numpy(),
    }
    variants: list[tuple[str, str, float, np.ndarray]] = []
    for band, mask in masks.items():
        if int(mask.sum()) < 3:
            continue
        posterior = e56.posterior_prob_from_labels(labels[mask], raw_prior)
        for weight in [0.05, 0.10, 0.18, 0.28]:
            name = f"posterior_{band}_w{weight:.2f}"
            variants.append((name, band, weight, e56.logit_blend(mixmin, posterior, weight)))
    return variants


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    raw_prior, _ = e56.raw_prior_from_e54(sample)
    labels = np.load(e56.LABEL_NPZ_OUT, allow_pickle=True)["labels"].astype(np.float64)
    worlds = pd.read_csv(e56.WORLD_OUT)
    posterior_summary = pd.read_csv(e56.POSTERIOR_SUMMARY_OUT)

    mixmin = load_sub(e56.MIXMIN_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    a2c8 = load_sub(A2C8, sample)[TARGETS].to_numpy(dtype=np.float64)
    raw05 = load_sub("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", sample)[TARGETS].to_numpy(dtype=np.float64)

    refs: list[tuple[str, str, float, np.ndarray]] = [
        ("mixmin", "reference", 0.0, mixmin),
        ("a2c8", "reference", 0.0, a2c8),
        ("raw05", "reference", 0.0, raw05),
    ]
    variants = build_variants(labels, worlds, raw_prior, mixmin)
    names = refs + variants
    anchor = actual_anchor_score([prob for _, _, _, prob in names], sample)

    mixmin_anchor = float(anchor.iloc[0]["actual_anchor_score_final"])
    mixmin_loss = np.asarray([binary_logloss(mixmin, y) for y in labels], dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for i, (name, band, weight, prob) in enumerate(names):
        delta = np.asarray([binary_logloss(prob, y) for y in labels], dtype=np.float64) - mixmin_loss
        rec = {
            "candidate": name,
            "band": band,
            "weight": weight,
            "actual_anchor_score_final": float(anchor.iloc[i]["actual_anchor_score_final"]),
            "mean_actual_anchor": float(anchor.iloc[i]["mean_actual_anchor"]),
            "min_set_score": float(anchor.iloc[i]["min_set_score"]),
            "max_set_score": float(anchor.iloc[i]["max_set_score"]),
            "anchor_delta_vs_mixmin": float(anchor.iloc[i]["actual_anchor_score_final"] - mixmin_anchor),
            "world_all_better_rate": float((delta < 0.0).mean()),
            "world_all_median_delta": float(np.median(delta)),
            "world_all_p90_delta": float(np.quantile(delta, 0.90)),
            "world_all_max_delta": float(np.max(delta)),
            **movement(prob, mixmin),
            **target_movements(prob, mixmin),
        }
        if name.startswith("posterior_"):
            ps = posterior_summary[posterior_summary["candidate"].eq(name)]
            if len(ps):
                rec["world_loo_strict_gate"] = bool(ps.iloc[0]["strict_gate"])
                rec["world_loo_better_rate"] = float(ps.iloc[0]["better_rate"])
                rec["world_loo_median_delta"] = float(ps.iloc[0]["median_delta"])
                rec["world_loo_p90_delta"] = float(ps.iloc[0]["p90_delta"])
            else:
                rec["world_loo_strict_gate"] = False
        else:
            rec["world_loo_strict_gate"] = False
        rec["anchor_beats_mixmin"] = bool(rec["anchor_delta_vs_mixmin"] < 0.0)
        rec["movement_guard"] = bool(rec["mean_abs_logit_move_vs_mixmin"] <= 0.08)
        rec["joint_candidate_gate"] = bool(rec["world_loo_strict_gate"] and rec["anchor_beats_mixmin"] and rec["movement_guard"])
        rows.append(rec)

    scores = pd.DataFrame(rows).sort_values(
        ["joint_candidate_gate", "actual_anchor_score_final", "world_all_median_delta"],
        ascending=[False, True, True],
    )
    scores.to_csv(SCORE_OUT, index=False)

    display_cols = [
        "candidate",
        "actual_anchor_score_final",
        "anchor_delta_vs_mixmin",
        "world_loo_strict_gate",
        "world_loo_median_delta",
        "mean_abs_logit_move_vs_mixmin",
        "movement_guard",
        "joint_candidate_gate",
    ]
    lines = [
        "# E57 Mixmin-Hard Raw Posterior Safety Stress",
        "",
        "## Observe",
        "",
        "E56 generated a posterior candidate because mixmin-hard/raw-prior worlds agree internally. The selected file was `analysis_outputs/submission_mixhard_rawposterior_af1502f9.csv`.",
        "",
        "## Wonder",
        "",
        "Is the E56 posterior a real public-subset hypothesis, or did the generated world family create an overconfident self-consistent label prior?",
        "",
        "## Method",
        "",
        "- Reconstructed all E56 posterior variants from the saved mixmin-hard labels.",
        "- Scored each variant with the independent actual-anchor/public-shape proxy used by previous raw05/JEPa frontier searches.",
        "- Required three gates for a public candidate: E56 world-LOO strict pass, actual-anchor score better than mixmin, and mean abs logit movement vs mixmin <= 0.08.",
        "",
        "## Safety Scores",
        "",
        e56.markdown_table(scores[[c for c in display_cols if c in scores.columns]].head(20)),
        "",
        "## Decision",
        "",
        f"- joint candidate gates: `{int(scores['joint_candidate_gate'].sum())}`.",
        f"- best actual-anchor posterior: `{scores[scores['candidate'].str.startswith('posterior_')].iloc[0]['candidate']}` with anchor delta `{scores[scores['candidate'].str.startswith('posterior_')].iloc[0]['anchor_delta_vs_mixmin']:.6f}` versus mixmin.",
        "- Do not submit the E56 posterior files. The world-internal signal is strong but independent anchor geometry says the movement is public-risk adverse.",
        "",
        "## Interpretation",
        "",
        "E56 is still useful: mixmin-hard raw worlds are coherent enough to expose a hidden binary-world direction. E57 says that direction is not yet calibrated to public anchors. The next version should use the E56 posterior as an energy axis or teacher, then constrain it by public-anchor geometry before producing a submission.",
        "",
        "## Outputs",
        "",
        f"- `{SCORE_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"variants={len(scores)} joint={int(scores['joint_candidate_gate'].sum())} "
        f"best_posterior_anchor_delta={scores[scores['candidate'].str.startswith('posterior_')].iloc[0]['anchor_delta_vs_mixmin']:.6f}"
    )
    print(scores[[c for c in display_cols if c in scores.columns]].head(15).to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
