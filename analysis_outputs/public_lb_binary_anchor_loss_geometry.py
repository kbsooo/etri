from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, known_public_table, load_sub, logit  # noqa: E402
from public_lb_inverse_feasibility import load_prob  # noqa: E402
from public_lb_structural_prior_stress import markdown_table  # noqa: E402


WORLD_CSV = OUT / "public_lb_binary_frontier_box_pool_worlds.csv"
DELTA_CSV = OUT / "public_lb_binary_frontier_box_pool_candidate_deltas.csv"
NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"

WORLD_OUT = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"
ANCHOR_OUT = OUT / "public_lb_binary_anchor_loss_geometry_anchors.csv"
BAND_OUT = OUT / "public_lb_binary_anchor_loss_geometry_bands.csv"
REPORT_OUT = OUT / "public_lb_binary_anchor_loss_geometry_report.md"


EPS = 1e-6


def clip_prob(prob: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(prob, dtype=np.float64), EPS, 1.0 - EPS)


def target_logloss(prob: np.ndarray, y: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean(axis=0)


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale < 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def entropy(values: np.ndarray) -> float:
    v = np.asarray(values, dtype=np.float64)
    v = np.abs(v)
    total = float(v.sum())
    if total <= 1e-15:
        return 0.0
    q = v / total
    return float(-(q * np.log(q + 1e-15)).sum() / np.log(len(q)))


def corr_safe(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def main() -> None:
    sample = load_sub(A2C8)
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    known = known_public_table().copy().reset_index(drop=True)
    known = known[known["file"].map(lambda f: load_sub(str(f), sample) is not None)].reset_index(drop=True)
    base_public = float(known.loc[known["file"].eq(A2C8), "public_lb"].iloc[0])

    worlds = pd.read_csv(WORLD_CSV)
    deltas = pd.read_csv(DELTA_CSV)
    npz = np.load(NPZ, allow_pickle=True)
    labels = npz["labels"].astype(np.float64).reshape(-1, len(sample), len(TARGETS))
    if len(worlds) != labels.shape[0]:
        worlds = worlds[worlds["has_incumbent"].astype(bool)].reset_index(drop=True)
    if len(worlds) != labels.shape[0]:
        raise ValueError("world/label count mismatch")

    base_prob = load_prob(A2C8, sample)
    base_logit = logit(base_prob)
    known_probs: dict[str, np.ndarray] = {file: load_prob(file, sample) for file in known["file"]}
    move_weights = {
        file: np.mean(np.abs(logit(prob) - base_logit), axis=0)
        for file, prob in known_probs.items()
    }

    anchor_rows = []
    world_rows = []
    for world_idx, y in enumerate(labels):
        meta = worlds.iloc[world_idx].to_dict()
        base_loss_t = target_logloss(base_prob, y)
        metrics = []
        for rec in known.to_dict("records"):
            file = str(rec["file"])
            if file == A2C8:
                continue
            public_delta = float(rec["public_lb"]) - base_public
            prob = known_probs[file]
            loss_t = target_logloss(prob, y)
            delta_t = loss_t - base_loss_t
            total_delta = float(delta_t.mean())
            target_sum_delta = float(delta_t.sum())
            abs_sum = float(np.abs(delta_t).sum())
            cancellation_ratio = float(abs_sum / (abs(target_sum_delta) + 1e-12))
            weights = move_weights[file]
            if weights.sum() <= 1e-12:
                weights = np.ones(len(TARGETS), dtype=np.float64)
            weights = weights / weights.sum()
            sign = 1.0 if public_delta >= 0 else -1.0
            weighted_positive_share = float(weights[(sign * delta_t) > 0].sum())
            weighted_signed_margin = float(np.sum(weights * sign * delta_t))
            movement_loss_abs_corr = corr_safe(weights, np.abs(delta_t))
            metrics.append(
                {
                    "public_delta_vs_a2c8": public_delta,
                    "fitted_delta_vs_a2c8": total_delta,
                    "abs_residual_to_public_delta": abs(total_delta - public_delta),
                    "cancellation_ratio": cancellation_ratio,
                    "weighted_positive_share": weighted_positive_share,
                    "weighted_signed_margin": weighted_signed_margin,
                    "movement_loss_abs_corr": movement_loss_abs_corr,
                    "target_delta_entropy": entropy(delta_t),
                }
            )
            row = {
                "world_row": world_idx,
                "world_id": meta.get("world_id"),
                "objective": meta.get("objective"),
                "source_role": meta.get("source_role"),
                "anchor_file": file,
                "public_delta_vs_a2c8": public_delta,
                "fitted_delta_vs_a2c8": total_delta,
                "abs_residual_to_public_delta": abs(total_delta - public_delta),
                "cancellation_ratio": cancellation_ratio,
                "weighted_positive_share": weighted_positive_share,
                "weighted_signed_margin": weighted_signed_margin,
                "movement_loss_abs_corr": movement_loss_abs_corr,
                "target_delta_entropy": entropy(delta_t),
            }
            for target_i, target in enumerate(TARGETS):
                row[f"delta_{target}"] = float(delta_t[target_i])
                row[f"move_weight_{target}"] = float(weights[target_i])
            anchor_rows.append(row)

        mdf = pd.DataFrame(metrics)
        world_rows.append(
            {
                "world_row": world_idx,
                "world_id": meta.get("world_id"),
                "objective": meta.get("objective"),
                "source_role": meta.get("source_role"),
                "duplicate_world": bool(meta.get("duplicate_world")),
                "max_abs_residual": float(meta.get("max_abs_residual")),
                "sum_abs_residual": float(meta.get("sum_abs_residual")),
                "anchor_abs_residual_mean": float(mdf["abs_residual_to_public_delta"].mean()),
                "anchor_cancellation_mean": float(mdf["cancellation_ratio"].mean()),
                "anchor_cancellation_max": float(mdf["cancellation_ratio"].max()),
                "anchor_positive_share_mean": float(mdf["weighted_positive_share"].mean()),
                "anchor_positive_share_min": float(mdf["weighted_positive_share"].min()),
                "anchor_signed_margin_mean": float(mdf["weighted_signed_margin"].mean()),
                "anchor_movement_loss_corr_mean": float(mdf["movement_loss_abs_corr"].mean()),
                "anchor_target_entropy_mean": float(mdf["target_delta_entropy"].mean()),
            }
        )

    anchor_df = pd.DataFrame(anchor_rows)
    world_df = pd.DataFrame(world_rows)
    delta_pivot = deltas.pivot_table(
        index=["world_id", "objective", "source_role"],
        columns="role",
        values="candidate_delta_vs_a2c8",
        aggfunc="first",
    ).reset_index()
    world_df = world_df.merge(delta_pivot, on=["world_id", "objective", "source_role"], how="left")

    # Lower energy = less cancellation, higher sign agreement, stronger movement/loss alignment.
    world_df["anchor_cancellation_rz"] = robust_z(world_df["anchor_cancellation_mean"]).clip(-3, 6)
    world_df["anchor_positive_gap_rz"] = robust_z(1.0 - world_df["anchor_positive_share_mean"]).clip(-3, 6)
    world_df["anchor_corr_gap_rz"] = robust_z(1.0 - world_df["anchor_movement_loss_corr_mean"]).clip(-3, 6)
    world_df["anchor_energy"] = (
        world_df["anchor_cancellation_rz"]
        + world_df["anchor_positive_gap_rz"]
        + 0.5 * world_df["anchor_corr_gap_rz"]
    )
    world_df["anchor_energy_rank"] = world_df["anchor_energy"].rank(method="first", ascending=True).astype(int)
    world_df["anchor_energy_quantile"] = world_df["anchor_energy"].rank(pct=True, ascending=True)
    for role in ["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_1bb_s0p65", "pair_sensor_6b"]:
        if role in world_df.columns:
            world_df[f"{role}_better"] = world_df[role] < 0.0

    world_df.to_csv(WORLD_OUT, index=False)
    anchor_df.to_csv(ANCHOR_OUT, index=False)

    bands = []
    band_specs = [
        ("all", np.ones(len(world_df), dtype=bool)),
        ("random_plus_fit", world_df["source_role"].isin(["random", "slack"]).to_numpy()),
        ("low_anchor_energy_half", (world_df["anchor_energy_quantile"] <= 0.50).to_numpy()),
        ("low_anchor_energy_quarter", (world_df["anchor_energy_quantile"] <= 0.25).to_numpy()),
        (
            "low_anchor_energy_random_plus_fit",
            ((world_df["anchor_energy_quantile"] <= 0.50) & world_df["source_role"].isin(["random", "slack"])).to_numpy(),
        ),
    ]
    roles = ["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_1bb_s0p65", "pair_sensor_6b"]
    for band_name, mask in band_specs:
        sub = world_df[mask].copy()
        if sub.empty:
            continue
        for role in roles:
            if role not in sub.columns:
                continue
            bands.append(
                {
                    "band": band_name,
                    "role": role,
                    "worlds": int(len(sub)),
                    "better_rate": float((sub[role] < 0.0).mean()),
                    "min_delta": float(sub[role].min()),
                    "median_delta": float(sub[role].median()),
                    "max_delta": float(sub[role].max()),
                    "median_anchor_energy": float(sub["anchor_energy"].median()),
                }
            )
    band_df = pd.DataFrame(bands)
    band_df.to_csv(BAND_OUT, index=False)

    adverse_mix = world_df[world_df.get("mixmin_0c916_better", False) == False].copy()
    top_anchor = world_df.sort_values("anchor_energy").head(10)
    least_anchor = world_df.sort_values("anchor_energy", ascending=False).head(10)

    lines = [
        "# Binary Anchor Loss Geometry Audit",
        "",
        "Question: do known-public anchor loss decompositions reject the E30 adverse mixmin/inverse7 worlds?",
        "",
        "## Method",
        "",
        "- For each E30 binary world, compute per-target log-loss deltas of every known public anchor versus A2C8.",
        "- Score whether each known public-worse anchor's loss delta is aligned with its moved target axes, and whether total public delta requires large target-level cancellation.",
        "- Lower `anchor_energy` means less cancellation and better sign/movement alignment with known public anchors.",
        "",
        "## Candidate Support By Anchor Geometry Band",
        "",
        markdown_table(band_df),
        "",
        "## Lowest Anchor-Energy Worlds",
        "",
        markdown_table(
            top_anchor[
                [
                    "objective",
                    "source_role",
                    "world_id",
                    "anchor_energy",
                    "anchor_energy_rank",
                    "anchor_cancellation_mean",
                    "anchor_positive_share_mean",
                    "anchor_movement_loss_corr_mean",
                    "mixmin_0c916",
                    "inverse7blend_1040",
                    "pair_sensor_1bb",
                ]
            ]
        ),
        "",
        "## Highest Anchor-Energy Worlds",
        "",
        markdown_table(
            least_anchor[
                [
                    "objective",
                    "source_role",
                    "world_id",
                    "anchor_energy",
                    "anchor_energy_rank",
                    "anchor_cancellation_mean",
                    "anchor_positive_share_mean",
                    "anchor_movement_loss_corr_mean",
                    "mixmin_0c916",
                    "inverse7blend_1040",
                    "pair_sensor_1bb",
                ]
            ]
        ),
        "",
        "## Adverse Mixmin Worlds",
        "",
        f"- mixmin adverse worlds: `{len(adverse_mix)}`.",
    ]
    if not adverse_mix.empty:
        lines.append(
            markdown_table(
                adverse_mix[
                    [
                        "objective",
                        "source_role",
                        "world_id",
                        "anchor_energy",
                        "anchor_energy_rank",
                        "anchor_cancellation_mean",
                        "anchor_positive_share_mean",
                        "anchor_movement_loss_corr_mean",
                        "mixmin_0c916",
                        "inverse7blend_1040",
                    ]
                ].sort_values("mixmin_0c916", ascending=False)
            )
        )

    low_band = band_df[(band_df["band"] == "low_anchor_energy_half") & (band_df["role"] == "mixmin_0c916")]
    low_rate = float(low_band["better_rate"].iloc[0]) if not low_band.empty else float("nan")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- worlds scored: `{len(world_df)}`.",
            f"- low-anchor-energy-half mixmin better_rate: `{low_rate:.6f}`.",
        ]
    )
    if len(adverse_mix) and adverse_mix["anchor_energy_rank"].min() <= max(3, int(len(world_df) * 0.25)):
        lines.append("- Known-anchor loss geometry cannot reject the adverse mixmin worlds.")
    elif len(adverse_mix):
        lines.append("- Adverse mixmin worlds have worse anchor geometry; this strengthens mixmin but remains a diagnostic gate.")
    else:
        lines.append("- No adverse mixmin world remains under the audited worlds.")
    lines.append("- This is not a public-LB optimizer; it is a stress test for hidden-world plausibility.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "worlds": len(world_df),
            "mixmin_adverse": len(adverse_mix),
            "low_anchor_half_mixmin_rate": low_rate,
        }
    )
    print(band_df.to_string(index=False))


if __name__ == "__main__":
    main()
