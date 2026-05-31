#!/usr/bin/env python3
"""E352: selector-sensitivity audit for the compact lifestyle-state plateau.

Question:
    Is the E351 plateau representative stable, or did it win because of one
    arbitrary selector weighting?

This is not a new model and it does not use public LB.  It repeatedly perturbs
the public-free selector thresholds and maximin weights over the E350 compact
lifestyle-state basin.  A useful hidden lifestyle-state candidate should remain
near the top under many plausible selector worlds.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from e328_ownlatent_lifestyle_state_experiment import md_table


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

RANKED_IN = OUT / "e351_robust_plateau_selector_ranked.csv"
PROFILES_IN = OUT / "e351_robust_plateau_selector_profiles.csv"
SCENARIOS_OUT = OUT / "e352_selector_sensitivity_scenarios.csv"
SUMMARY_OUT = OUT / "e352_selector_sensitivity_summary.csv"
REPORT_OUT = OUT / "e352_selector_sensitivity_report.md"

SEED = 20260531 + 352
N_RANDOM_SCENARIOS = 2500

COMPONENTS = [
    "p90_pct",
    "risk_pct",
    "bad_margin_pct",
    "q1_specificity_pct",
    "support_pct",
    "compat_e349_pct",
    "micro_scale_pct",
]

METRIC_COLS = [
    "pred_delta_vs_current_p90",
    "p90_gain_vs_e349",
    "public_analog_risk_score",
    "risk_delta_vs_e349",
    "incremental_bad_axis_vs_current",
    "bad_axis_margin",
    "q1_specificity_margin",
    "q1_margin_delta_vs_e349",
    "plateau_support_score",
    "prob_l1_delta_vs_e349",
    "prob_l1_delta_vs_e347",
    "direct_bad_poscos_sum",
    "scale_abs_delta",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def finite(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(default)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    ranked = pd.read_csv(RANKED_IN)
    profiles = pd.read_csv(PROFILES_IN)
    for col in COMPONENTS + METRIC_COLS:
        if col in ranked.columns:
            ranked[col] = finite(ranked[col])
    for col in ["e350_plateau_gate", "e351_compat_gate", "s3_tail_present"]:
        if col in ranked.columns:
            ranked[col] = ranked[col].fillna(False).astype(bool)
    return ranked, profiles


def profile_lookup(profiles: pd.DataFrame) -> dict[str, str]:
    out: dict[str, str] = {}
    for _, row in profiles.iterrows():
        variant = str(row.get("variant", ""))
        profile = str(row.get("profile", ""))
        if variant:
            out[variant] = profile
    return out


def apply_gate(frame: pd.DataFrame, cfg: dict[str, float]) -> pd.Series:
    return (
        (frame["p90_gain_vs_e349"] >= cfg["p90_min"])
        & (frame["risk_delta_vs_e349"] <= cfg["risk_cap"])
        & (frame["bad_axis_margin"] >= cfg["bad_min"])
        & (frame["q1_margin_delta_vs_e349"] >= cfg["q1_min"])
        & (frame["plateau_support_score"] >= cfg["support_min"])
        & (frame["prob_l1_delta_vs_e349"] >= cfg["l1_min"])
        & (frame["prob_l1_delta_vs_e349"] <= cfg["l1_max"])
        & (frame["scale_abs_delta"] <= cfg["scale_max"])
        & (frame["direct_bad_poscos_sum"] <= cfg["bad_poscos_max"])
    )


def score_pool(pool: pd.DataFrame, weights: np.ndarray, worst_lambda: float, s3_bonus: float) -> pd.Series:
    matrix = pool[COMPONENTS].to_numpy(dtype=np.float64)
    score = matrix @ weights
    score += worst_lambda * matrix.min(axis=1)
    score += s3_bonus * pool["s3_tail_present"].astype(float).to_numpy(dtype=np.float64)
    return pd.Series(score, index=pool.index)


def random_config(rng: np.random.Generator) -> tuple[dict[str, float], np.ndarray, float, float]:
    cfg = {
        "risk_cap": float(rng.uniform(2.0e-5, 6.0e-5)),
        "l1_min": float(rng.uniform(0.0010, 0.0040)),
        "l1_max": float(rng.uniform(0.0070, 0.0120)),
        "p90_min": float(rng.uniform(0.0, 2.2e-7)),
        "bad_min": float(rng.uniform(0.00020, 0.00033)),
        "support_min": float(rng.integers(28, 38)),
        "q1_min": float(rng.uniform(-0.035, 0.008)),
        "scale_max": float(rng.choice([0.0001, 0.0051, 0.0101], p=[0.20, 0.60, 0.20])),
        "bad_poscos_max": 1.0e-9,
    }
    weights = rng.dirichlet(np.ones(len(COMPONENTS)))
    worst_lambda = float(rng.uniform(0.50, 2.60))
    s3_bonus = float(rng.uniform(-0.05, 0.08))
    return cfg, weights, worst_lambda, s3_bonus


def deterministic_configs() -> list[tuple[str, dict[str, float], np.ndarray, float, float]]:
    def weights(**items: float) -> np.ndarray:
        vals = np.array([items.get(c, 1.0) for c in COMPONENTS], dtype=np.float64)
        return vals / vals.sum()

    base = {
        "risk_cap": 5.0e-5,
        "l1_min": 0.0010,
        "l1_max": 0.0090,
        "p90_min": 5.0e-8,
        "bad_min": 0.00020,
        "support_min": 30.0,
        "q1_min": -0.030,
        "scale_max": 0.0051,
        "bad_poscos_max": 1.0e-9,
    }
    configs: list[tuple[str, dict[str, float], np.ndarray, float, float]] = []
    configs.append(("balanced", dict(base), weights(), 1.50, 0.00))

    cfg = dict(base)
    cfg.update({"risk_cap": 4.0e-5, "bad_min": 0.00025, "l1_max": 0.0080})
    configs.append(
        (
            "public_skeptic",
            cfg,
            weights(risk_pct=3.0, bad_margin_pct=3.0, compat_e349_pct=2.5, micro_scale_pct=2.0),
            2.50,
            -0.02,
        )
    )

    cfg = dict(base)
    cfg.update({"risk_cap": 6.0e-5, "p90_min": 1.0e-7, "support_min": 32.0, "l1_max": 0.0120})
    configs.append(
        (
            "p90_hungry",
            cfg,
            weights(p90_pct=4.0, support_pct=2.5, q1_specificity_pct=1.5),
            0.80,
            0.05,
        )
    )

    cfg = dict(base)
    cfg.update({"q1_min": -0.005, "support_min": 34.0})
    configs.append(
        (
            "state_specific",
            cfg,
            weights(q1_specificity_pct=4.0, support_pct=3.0, bad_margin_pct=2.0),
            1.80,
            0.00,
        )
    )

    cfg = dict(base)
    cfg.update({"risk_cap": 3.5e-5, "l1_max": 0.0070, "bad_min": 0.00025, "p90_min": 0.0})
    configs.append(
        (
            "e349_conservative",
            cfg,
            weights(compat_e349_pct=4.0, micro_scale_pct=3.0, risk_pct=2.5, bad_margin_pct=2.0),
            2.20,
            -0.03,
        )
    )

    cfg = dict(base)
    cfg.update({"risk_cap": 5.5e-5, "l1_max": 0.0120, "p90_min": 1.0e-7})
    configs.append(
        (
            "s3_tail_tolerant",
            cfg,
            weights(p90_pct=3.0, support_pct=2.0, q1_specificity_pct=1.5, risk_pct=1.0),
            1.00,
            0.08,
        )
    )
    return configs


def select_one(
    plateau: pd.DataFrame,
    scenario: str,
    cfg: dict[str, float],
    weights: np.ndarray,
    worst_lambda: float,
    s3_bonus: float,
    scenario_id: int,
) -> dict[str, object] | None:
    gate = apply_gate(plateau, cfg)
    pool = plateau[gate].copy()
    if pool.empty:
        return None
    pool["scenario_score"] = score_pool(pool, weights, worst_lambda, s3_bonus)
    ordered = pool.sort_values(
        ["scenario_score", "e351_worst_axis_pct", "p90_gain_vs_e349"],
        ascending=[False, False, False],
    )
    top = ordered.iloc[0]
    top3 = ordered.head(3)
    rec: dict[str, object] = {
        "scenario_id": scenario_id,
        "scenario": scenario,
        "pool_size": len(pool),
        "top_variant": top["variant"],
        "top_basename": top["basename"],
        "top3_variants": "|".join(top3["variant"].astype(str).tolist()),
        "top_score": float(top["scenario_score"]),
        "worst_lambda": worst_lambda,
        "s3_bonus": s3_bonus,
    }
    for key, value in cfg.items():
        rec[key] = value
    for name, value in zip(COMPONENTS, weights):
        rec[f"w_{name}"] = float(value)
    return rec


def run_scenarios(plateau: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows: list[dict[str, object]] = []
    scenario_id = 0
    for _ in range(N_RANDOM_SCENARIOS):
        cfg, weights, worst_lambda, s3_bonus = random_config(rng)
        rec = select_one(plateau, "random", cfg, weights, worst_lambda, s3_bonus, scenario_id)
        scenario_id += 1
        if rec is not None:
            rows.append(rec)

    for name, cfg, weights, worst_lambda, s3_bonus in deterministic_configs():
        rec = select_one(plateau, name, cfg, weights, worst_lambda, s3_bonus, scenario_id)
        scenario_id += 1
        if rec is not None:
            rows.append(rec)
    return pd.DataFrame(rows)


def summarize(plateau: pd.DataFrame, scenarios: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    profile_by_variant = profile_lookup(profiles)
    valid = max(len(scenarios), 1)
    rows: list[dict[str, object]] = []
    top_counts = scenarios["top_variant"].value_counts().to_dict()
    top3_counts: dict[str, int] = {}
    for variants in scenarios["top3_variants"].astype(str):
        for variant in variants.split("|"):
            top3_counts[variant] = top3_counts.get(variant, 0) + 1

    top_variants = set(top_counts) | set(top3_counts) | set(profile_by_variant)
    for _, row in plateau.iterrows():
        variant = str(row["variant"])
        scenario_scores = scenarios.loc[scenarios["top_variant"].eq(variant), "top_score"]
        rec: dict[str, object] = {
            "variant": variant,
            "profile_role": profile_by_variant.get(variant, ""),
            "basename": row["basename"],
            "file": row["file"],
            "top1_count": int(top_counts.get(variant, 0)),
            "top3_count": int(top3_counts.get(variant, 0)),
            "top1_rate": float(top_counts.get(variant, 0) / valid),
            "top3_rate": float(top3_counts.get(variant, 0) / valid),
            "selected_in_any_scenario": variant in top_variants,
            "median_top_score_when_selected": float(scenario_scores.median()) if len(scenario_scores) else np.nan,
        }
        for col in COMPONENTS + METRIC_COLS + ["e351_robust_score", "e351_worst_axis_pct", "e351_compat_gate"]:
            if col in row.index:
                rec[col] = row[col]
        rows.append(rec)

    summary = pd.DataFrame(rows)
    summary = summary.sort_values(
        ["top1_count", "top3_count", "e351_worst_axis_pct", "p90_gain_vs_e349"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    summary["selection_rank"] = np.arange(1, len(summary) + 1)
    return summary


def profile_winners(scenarios: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, group in scenarios.groupby("scenario", sort=False):
        rows.append(
            {
                "scenario": name,
                "count": len(group),
                "winner": group["top_variant"].mode().iloc[0],
                "winner_count": int(group["top_variant"].value_counts().iloc[0]),
                "mean_pool_size": float(group["pool_size"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["scenario"], ascending=True)


def write_report(
    plateau: pd.DataFrame,
    scenarios: pd.DataFrame,
    summary: pd.DataFrame,
    profiles: pd.DataFrame,
) -> None:
    e351_variant = profiles.loc[profiles["profile"].eq("e351_robust"), "variant"].iloc[0]
    e350_variant = profiles.loc[profiles["profile"].eq("e350_rank_selected"), "variant"].iloc[0]
    leader = summary.iloc[0]
    e351 = summary[summary["variant"].eq(e351_variant)].iloc[0]
    e350 = summary[summary["variant"].eq(e350_variant)].iloc[0]
    winners = profile_winners(scenarios)

    top_cols = [
        "selection_rank",
        "variant",
        "profile_role",
        "top1_count",
        "top3_count",
        "top1_rate",
        "top3_rate",
        "p90_gain_vs_e349",
        "public_analog_risk_score",
        "risk_delta_vs_e349",
        "bad_axis_margin",
        "q1_specificity_margin",
        "plateau_support_score",
        "prob_l1_delta_vs_e349",
        "scale_abs_delta",
        "e351_compat_gate",
    ]
    top_cols = [c for c in top_cols if c in summary.columns]

    profile_cols = [
        "scenario",
        "count",
        "winner",
        "winner_count",
        "mean_pool_size",
    ]

    stability = "stable" if str(leader["variant"]) == str(e351_variant) else "unstable"
    lines = [
        "# E352 Selector Sensitivity Audit",
        "",
        "## Question",
        "",
        "Did E351 win because of one hand-picked maximin selector, or is it the stable representative of the E350 compact lifestyle-state basin?",
        "",
        "## Method",
        "",
        "- Input: E351-ranked E350 plateau only; no public LB tuning.",
        f"- Random selector worlds: `{N_RANDOM_SCENARIOS}` generated, `{len(scenarios)}` non-empty.",
        "- Perturbed gates: p90 gain, public-analog risk delta, bad-axis margin, Q1 specificity delta, support, distance from E349, micro-scale size, and hard public-bad positive cosine veto.",
        "- Perturbed scores: Dirichlet weights over p90/risk/bad-margin/Q1-specificity/support/E349-compatibility/micro-scale plus a random worst-axis penalty and tiny S3-tail preference.",
        "- Fixed stress profiles: balanced, public_skeptic, p90_hungry, state_specific, e349_conservative, and s3_tail_tolerant.",
        "",
        "## Decision",
        "",
        f"- stability verdict: `{stability}`",
        f"- selector-sensitivity winner: `{leader['variant']}`",
        f"- E351 robust top1/top3 rate: `{float(e351['top1_rate']):.6f}` / `{float(e351['top3_rate']):.6f}`",
        f"- E350 rank winner top1/top3 rate: `{float(e350['top1_rate']):.6f}` / `{float(e350['top3_rate']):.6f}`",
        "",
        "## Top Selector-Stable Candidates",
        "",
        md_table(summary[top_cols], n=25, floatfmt=".9f"),
        "",
        "## Scenario Profile Winners",
        "",
        md_table(winners[profile_cols], n=20, floatfmt=".6f"),
        "",
        "## Interpretation",
        "",
    ]
    if stability == "stable":
        lines.extend(
            [
                "E351 remains the most stable representative after selector perturbation.",
                "The useful hidden lifestyle-state basin is not centered on the original E350 rank winner; the robust center is the high-threshold, small-S3-tail candidate.",
                "This supports the current practical ordering: submit E351 before E350 if public slots are scarce. E350 remains the more aggressive sensor if we specifically want to test full S3-tail restoration.",
            ]
        )
    else:
        lines.extend(
            [
                "E351 did not remain the selector-sensitivity winner.",
                "The plateau is real, but the public-free candidate ordering should be updated toward the scenario-stable winner before spending a public slot.",
            ]
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(SCENARIOS_OUT)}`",
            f"- `{rel(SUMMARY_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    ranked, profiles = load_inputs()
    plateau = ranked[ranked["e350_plateau_gate"].astype(bool)].copy()
    if plateau.empty:
        raise RuntimeError("No E350 plateau candidates found.")
    scenarios = run_scenarios(plateau)
    if scenarios.empty:
        raise RuntimeError("All selector-sensitivity scenarios were empty.")
    summary = summarize(plateau, scenarios, profiles)

    scenarios.to_csv(SCENARIOS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(plateau, scenarios, summary, profiles)

    print(f"plateau candidates: {len(plateau)}")
    print(f"non-empty scenarios: {len(scenarios)}")
    print("top selector-stable variants:")
    print(summary[["selection_rank", "variant", "top1_count", "top3_count", "top1_rate", "top3_rate"]].head(12).to_string(index=False))
    print(f"wrote {rel(SCENARIOS_OUT)}")
    print(f"wrote {rel(SUMMARY_OUT)}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
