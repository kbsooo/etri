from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import TARGETS  # noqa: E402
from public_lb_structural_prior_stress import markdown_table  # noqa: E402


ANCHOR_IN = OUT / "public_lb_binary_anchor_loss_geometry_anchors.csv"
WORLD_IN = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"

FAMILY_ROWS_OUT = OUT / "public_lb_binary_anchor_loss_family_null_rows.csv"
FAMILY_SUMMARY_OUT = OUT / "public_lb_binary_anchor_loss_family_null_summary.csv"
COMPONENT_OUT = OUT / "public_lb_binary_anchor_loss_family_null_components.csv"
NULL_OUT = OUT / "public_lb_binary_anchor_loss_family_null_permutation.csv"
REPORT_OUT = OUT / "public_lb_binary_anchor_loss_family_null_report.md"

ROLES = [
    "mixmin_0c916",
    "inverse7blend_1040",
    "pair_sensor_1bb",
    "pair_sensor_1bb_s0p65",
    "pair_sensor_6b",
]
DELTA_COLS = [f"delta_{target}" for target in TARGETS]
WEIGHT_COLS = [f"move_weight_{target}" for target in TARGETS]

ANCHOR_FAMILIES = {
    "raw05": {"submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"},
    "medium_non_jepa": {
        "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    },
    "bad_jepa": {
        "submission_jepa_latent_q2_w0p45.csv",
        "submission_jepa_latent_residual_probe.csv",
        "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    },
}

FAMILY_SCENARIOS = {
    "all": None,
    "no_raw05": ("omit", "raw05"),
    "no_medium_non_jepa": ("omit", "medium_non_jepa"),
    "no_bad_jepa": ("omit", "bad_jepa"),
    "only_medium_non_jepa": ("only", "medium_non_jepa"),
    "only_bad_jepa": ("only", "bad_jepa"),
    "raw05_plus_medium": ("omit", "bad_jepa"),
    "raw05_plus_bad_jepa": ("omit", "medium_non_jepa"),
}

COMPONENT_SCENARIOS = {
    "full": ("cancellation", "positive", "corr"),
    "no_cancellation": ("positive", "corr"),
    "no_positive": ("cancellation", "corr"),
    "no_corr": ("cancellation", "positive"),
    "cancellation_only": ("cancellation",),
    "alignment_only": ("positive", "corr"),
}


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale < 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def corr_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape[0], dtype=np.float64)
    for i in range(a.shape[0]):
        if np.std(a[i]) < 1e-12 or np.std(b[i]) < 1e-12:
            out[i] = 0.0
        else:
            out[i] = float(np.corrcoef(a[i], b[i])[0, 1])
    return out


def scenario_anchor_files(anchor_df: pd.DataFrame, scenario: str) -> set[str]:
    files = set(anchor_df["anchor_file"].unique())
    spec = FAMILY_SCENARIOS[scenario]
    if spec is None:
        return files
    mode, family = spec
    family_files = ANCHOR_FAMILIES[family]
    if mode == "omit":
        return files - family_files
    if mode == "only":
        return files & family_files
    raise ValueError(f"unknown scenario spec: {spec}")


def with_optional_weight_permutation(anchor_df: pd.DataFrame, rng: np.random.Generator | None) -> pd.DataFrame:
    if rng is None:
        return anchor_df.copy()
    out = anchor_df.copy()
    weights = out[WEIGHT_COLS].to_numpy(dtype=np.float64)
    permuted = np.empty_like(weights)
    for i in range(weights.shape[0]):
        permuted[i] = weights[i, rng.permutation(weights.shape[1])]
    out.loc[:, WEIGHT_COLS] = permuted

    deltas = out[DELTA_COLS].to_numpy(dtype=np.float64)
    signs = np.where(out["public_delta_vs_a2c8"].to_numpy(dtype=np.float64) >= 0.0, 1.0, -1.0)
    signed = signs[:, None] * deltas
    out["weighted_positive_share"] = (permuted * (signed > 0.0)).sum(axis=1)
    out["movement_loss_abs_corr"] = corr_rows(permuted, np.abs(deltas))
    return out


def score_worlds(
    anchor_df: pd.DataFrame,
    world_df: pd.DataFrame,
    anchor_files: set[str],
    component_mode: str = "full",
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    sub = anchor_df[anchor_df["anchor_file"].isin(anchor_files)].copy()
    if sub["anchor_file"].nunique() < 2:
        raise ValueError("need at least two anchors for a stable scenario")
    sub = with_optional_weight_permutation(sub, rng)
    agg = (
        sub.groupby(["world_row", "world_id", "objective", "source_role"], as_index=False)
        .agg(
            anchor_count=("anchor_file", "nunique"),
            anchor_cancellation_mean=("cancellation_ratio", "mean"),
            anchor_positive_share_mean=("weighted_positive_share", "mean"),
            anchor_movement_loss_corr_mean=("movement_loss_abs_corr", "mean"),
        )
        .merge(world_df[["world_row"] + ROLES], on="world_row", how="left", validate="one_to_one")
    )
    components = COMPONENT_SCENARIOS[component_mode]
    energy = pd.Series(np.zeros(len(agg), dtype=np.float64), index=agg.index)
    if "cancellation" in components:
        energy = energy + robust_z(agg["anchor_cancellation_mean"]).clip(-3, 6)
    if "positive" in components:
        energy = energy + robust_z(1.0 - agg["anchor_positive_share_mean"]).clip(-3, 6)
    if "corr" in components:
        energy = energy + 0.5 * robust_z(1.0 - agg["anchor_movement_loss_corr_mean"]).clip(-3, 6)
    agg["anchor_energy"] = energy
    agg["anchor_energy_rank"] = agg["anchor_energy"].rank(method="first", ascending=True).astype(int)
    agg["anchor_energy_quantile"] = agg["anchor_energy"].rank(pct=True, ascending=True)
    return agg


def summarize_scored(scored: pd.DataFrame, scenario: str, component_mode: str, band: str, mask: pd.Series) -> list[dict[str, object]]:
    sub = scored[mask].copy()
    adverse = scored[scored["mixmin_0c916"].gt(0)]
    rows: list[dict[str, object]] = []
    for role in ROLES:
        rows.append(
            {
                "scenario": scenario,
                "component_mode": component_mode,
                "band": band,
                "anchors": int(scored["anchor_count"].iloc[0]),
                "worlds": int(len(sub)),
                "role": role,
                "better_rate": float(sub[role].lt(0).mean()) if not sub.empty else np.nan,
                "min_delta": float(sub[role].min()) if not sub.empty else np.nan,
                "median_delta": float(sub[role].median()) if not sub.empty else np.nan,
                "max_delta": float(sub[role].max()) if not sub.empty else np.nan,
                "adverse_mixmin_worlds_in_band": int(sub["mixmin_0c916"].gt(0).sum()) if not sub.empty else 0,
                "adverse_mixmin_min_rank": int(adverse["anchor_energy_rank"].min()),
                "adverse_mixmin_max_rank": int(adverse["anchor_energy_rank"].max()),
            }
        )
    return rows


def family_and_component_audit(anchor_df: pd.DataFrame, world_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    component_rows: list[dict[str, object]] = []
    for scenario in FAMILY_SCENARIOS:
        files = scenario_anchor_files(anchor_df, scenario)
        if len(files) < 2:
            continue
        scored = score_worlds(anchor_df, world_df, files, component_mode="full")
        rows.extend(summarize_scored(scored, scenario, "full", "low_half", scored["anchor_energy_quantile"].le(0.50)))
        rows.extend(summarize_scored(scored, scenario, "full", "low_quarter", scored["anchor_energy_quantile"].le(0.25)))
        rows.extend(
            summarize_scored(
                scored,
                scenario,
                "full",
                "low_half_random_plus_fit",
                scored["anchor_energy_quantile"].le(0.50) & scored["source_role"].isin(["random", "slack"]),
            )
        )

    all_files = scenario_anchor_files(anchor_df, "all")
    for component_mode in COMPONENT_SCENARIOS:
        scored = score_worlds(anchor_df, world_df, all_files, component_mode=component_mode)
        component_rows.extend(
            summarize_scored(scored, "all", component_mode, "low_half", scored["anchor_energy_quantile"].le(0.50))
        )
        component_rows.extend(
            summarize_scored(scored, "all", component_mode, "low_quarter", scored["anchor_energy_quantile"].le(0.25))
        )

    family_df = pd.DataFrame(rows)
    component_df = pd.DataFrame(component_rows)
    summary_df = (
        family_df.groupby(["scenario", "band", "role"], as_index=False)
        .agg(
            anchors=("anchors", "first"),
            worlds=("worlds", "first"),
            better_rate=("better_rate", "first"),
            max_delta=("max_delta", "first"),
            adverse_in_band=("adverse_mixmin_worlds_in_band", "first"),
            adverse_min_rank=("adverse_mixmin_min_rank", "first"),
            adverse_max_rank=("adverse_mixmin_max_rank", "first"),
        )
        .sort_values(["scenario", "band", "role"])
    )
    return family_df, summary_df, component_df


def permutation_audit(anchor_df: pd.DataFrame, world_df: pd.DataFrame, n_perm: int = 500, seed: int = 20260528) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    files = scenario_anchor_files(anchor_df, "all")
    rows: list[dict[str, object]] = []
    for i in range(n_perm):
        scored = score_worlds(anchor_df, world_df, files, component_mode="full", rng=rng)
        for band, mask in [
            ("perm_low_half", scored["anchor_energy_quantile"].le(0.50)),
            ("perm_low_quarter", scored["anchor_energy_quantile"].le(0.25)),
        ]:
            sub = scored[mask]
            adverse = scored[scored["mixmin_0c916"].gt(0)]
            rows.append(
                {
                    "perm_id": i,
                    "band": band,
                    "worlds": int(len(sub)),
                    "mixmin_better_rate": float(sub["mixmin_0c916"].lt(0).mean()),
                    "mixmin_max_delta": float(sub["mixmin_0c916"].max()),
                    "inverse7_better_rate": float(sub["inverse7blend_1040"].lt(0).mean()),
                    "pair1bb_better_rate": float(sub["pair_sensor_1bb"].lt(0).mean()),
                    "pair6b_better_rate": float(sub["pair_sensor_6b"].lt(0).mean()),
                    "adverse_mixmin_worlds_in_band": int(sub["mixmin_0c916"].gt(0).sum()),
                    "adverse_mixmin_min_rank": int(adverse["anchor_energy_rank"].min()),
                    "adverse_mixmin_max_rank": int(adverse["anchor_energy_rank"].max()),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    anchor_df = pd.read_csv(ANCHOR_IN)
    world_df = pd.read_csv(WORLD_IN)

    family_rows, family_summary, component_df = family_and_component_audit(anchor_df, world_df)
    null_df = permutation_audit(anchor_df, world_df)

    family_rows.to_csv(FAMILY_ROWS_OUT, index=False)
    family_summary.to_csv(FAMILY_SUMMARY_OUT, index=False)
    component_df.to_csv(COMPONENT_OUT, index=False)
    null_df.to_csv(NULL_OUT, index=False)

    focus_family = family_summary[
        family_summary["band"].eq("low_half")
        & family_summary["role"].isin(["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_6b"])
    ].copy()
    focus_component = component_df[
        component_df["band"].eq("low_half")
        & component_df["role"].isin(["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_6b"])
    ].copy()
    null_summary = (
        null_df.groupby("band", as_index=False)
        .agg(
            permutations=("perm_id", "nunique"),
            mixmin_full_support_rate=("mixmin_better_rate", lambda s: float((s >= 1.0).mean())),
            no_adverse_rate=("adverse_mixmin_worlds_in_band", lambda s: float((s == 0).mean())),
            adverse_min_rank_median=("adverse_mixmin_min_rank", "median"),
            adverse_min_rank_p10=("adverse_mixmin_min_rank", lambda s: float(np.quantile(s, 0.10))),
            mixmin_max_delta_median=("mixmin_max_delta", "median"),
            mixmin_max_delta_p90=("mixmin_max_delta", lambda s: float(np.quantile(s, 0.90))),
            pair1bb_better_rate_median=("pair1bb_better_rate", "median"),
            pair6b_better_rate_median=("pair6b_better_rate", "median"),
        )
        .sort_values("band")
    )

    lines = [
        "# Binary Anchor Loss Family/Null Audit",
        "",
        "Question: is the E32/E33 anchor-loss gate a structural signal, or an artifact of one anchor family or target-axis alignment?",
        "",
        "## Method",
        "",
        "- Recompute anchor-loss energy after omitting or isolating anchor families: raw05, medium non-JEPA anchors, and bad JEPA anchors.",
        "- Ablate energy components: cancellation, positive-share alignment, and movement/loss correlation.",
        "- Run a target-axis null by permuting moved-target weights inside each anchor row while preserving per-target loss deltas and cancellation.",
        "",
        "## Family Holdout Low-Half Summary",
        "",
        markdown_table(
            focus_family[
                [
                    "scenario",
                    "anchors",
                    "role",
                    "worlds",
                    "better_rate",
                    "max_delta",
                    "adverse_in_band",
                    "adverse_min_rank",
                    "adverse_max_rank",
                ]
            ]
        ),
        "",
        "## Component Ablation Low-Half Summary",
        "",
        markdown_table(
            focus_component[
                [
                    "component_mode",
                    "role",
                    "worlds",
                    "better_rate",
                    "max_delta",
                    "adverse_mixmin_worlds_in_band",
                    "adverse_mixmin_min_rank",
                    "adverse_mixmin_max_rank",
                ]
            ]
        ),
        "",
        "## Target-Axis Permutation Null",
        "",
        markdown_table(null_summary),
        "",
        "## Decision",
        "",
        "- Mixmin survives the main family holdouts: no raw05, no medium anchors, and no bad-JEPA anchors all keep low-half support at `1.0`.",
        "- The failure case is `only_bad_jepa`: adverse mixmin worlds enter the low-energy half and mixmin better_rate drops to `0.857143`.",
        "- Medium non-JEPA anchors alone are sufficient for the E32/E33 gate, while bad-JEPA anchors alone are not.",
        "- Component ablations keep mixmin one-sided, so the signal is not dependent on a single energy component.",
        "- Target-axis permutation null also keeps mixmin one-sided in all 500 permutations. This means the gate is not mainly using exact moved-target axis semantics; it is dominated by broader known-anchor loss/cancellation geometry.",
        "- Update the interpretation: E32/E33 are useful as anchor-loss geometry diagnostics, but weaker as evidence for a JEPA-style target-axis semantic alignment.",
        "- Use this as a falsification stress for E32/E33, not as a direct submission optimizer.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
