from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
from public_lb_structural_prior_stress import markdown_table  # noqa: E402


WORLD_CSV = OUT / "public_lb_binary_frontier_box_pool_worlds.csv"
DELTA_CSV = OUT / "public_lb_binary_frontier_box_pool_candidate_deltas.csv"
NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"

WORLD_FEATURE_OUT = OUT / "public_lb_binary_world_plausibility_features.csv"
BAND_OUT = OUT / "public_lb_binary_world_plausibility_bands.csv"
REPORT_OUT = OUT / "public_lb_binary_world_plausibility_report.md"


def load_world_labels(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    worlds = pd.read_csv(WORLD_CSV)
    npz = np.load(NPZ, allow_pickle=True)
    labels = npz["labels"].astype(np.float64)
    if labels.shape[1] != len(sample) * len(TARGETS):
        raise ValueError(f"label shape mismatch: {labels.shape}, sample={len(sample)}")
    if len(worlds) != labels.shape[0]:
        incumbent_worlds = worlds[worlds["has_incumbent"].astype(bool)].copy()
        if len(incumbent_worlds) != labels.shape[0]:
            raise ValueError(f"world/label row mismatch: worlds={len(worlds)} labels={labels.shape[0]}")
        worlds = incumbent_worlds.reset_index(drop=True)
    return worlds.reset_index(drop=True), labels.reshape(labels.shape[0], len(sample), len(TARGETS))


def pair_joint(mat: np.ndarray) -> np.ndarray:
    vals = []
    for i in range(mat.shape[1]):
        for j in range(i + 1, mat.shape[1]):
            vals.append(float(np.mean(mat[:, i] * mat[:, j])))
    return np.asarray(vals, dtype=np.float64)


def corr_vec(mat: np.ndarray) -> np.ndarray:
    corr = np.corrcoef(mat, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    vals = []
    for i in range(mat.shape[1]):
        for j in range(i + 1, mat.shape[1]):
            vals.append(float(corr[i, j]))
    return np.asarray(vals, dtype=np.float64)


def cardinality_hist(mat: np.ndarray) -> np.ndarray:
    counts = mat.sum(axis=1).astype(int)
    hist = np.bincount(counts, minlength=len(TARGETS) + 1).astype(np.float64)
    return hist / max(hist.sum(), 1.0)


def transition_rates(frame: pd.DataFrame, values: np.ndarray) -> np.ndarray:
    tmp = frame[KEYS].copy()
    rates = []
    for target_i in range(values.shape[1]):
        target_rates = []
        for _, idx in tmp.sort_values(KEYS).groupby("subject_id", sort=False).groups.items():
            loc = np.asarray(list(idx), dtype=int)
            if len(loc) < 2:
                continue
            v = values[loc, target_i]
            target_rates.append(float(np.mean(np.abs(np.diff(v)))))
        rates.append(float(np.mean(target_rates)) if target_rates else 0.0)
    return np.asarray(rates, dtype=np.float64)


def subject_transition_rates(frame: pd.DataFrame, values: np.ndarray) -> pd.DataFrame:
    rows = []
    tmp = frame[KEYS].copy()
    for subject_id, idx in tmp.sort_values(KEYS).groupby("subject_id", sort=False).groups.items():
        loc = np.asarray(list(idx), dtype=int)
        rec = {"subject_id": subject_id}
        for target_i, target in enumerate(TARGETS):
            if len(loc) < 2:
                rec[target] = np.nan
            else:
                rec[target] = float(np.mean(np.abs(np.diff(values[loc, target_i]))))
        rows.append(rec)
    return pd.DataFrame(rows).set_index("subject_id")


def mean_run_lengths(frame: pd.DataFrame, values: np.ndarray) -> np.ndarray:
    tmp = frame[KEYS].copy()
    out = []
    for target_i in range(values.shape[1]):
        runs = []
        for _, idx in tmp.sort_values(KEYS).groupby("subject_id", sort=False).groups.items():
            loc = np.asarray(list(idx), dtype=int)
            if len(loc) == 0:
                continue
            v = values[loc, target_i].astype(int)
            current = 1
            for a, b in zip(v[:-1], v[1:]):
                if a == b:
                    current += 1
                else:
                    runs.append(current)
                    current = 1
            runs.append(current)
        out.append(float(np.mean(runs)) if runs else 0.0)
    return np.asarray(out, dtype=np.float64)


def edge_flip_rate(train: pd.DataFrame, sample: pd.DataFrame, world: np.ndarray) -> float:
    vals = []
    train_sorted = train.sort_values(KEYS)
    sample_sorted = sample.sort_values(KEYS)
    for subject_id, g_test in sample_sorted.groupby("subject_id", sort=False):
        g_train = train_sorted[train_sorted["subject_id"].eq(subject_id)]
        if g_train.empty or g_test.empty:
            continue
        last_train = g_train.iloc[-1][TARGETS].to_numpy(dtype=np.float64)
        first_pos = int(g_test.index[0])
        first_test = world[first_pos]
        vals.extend(np.abs(first_test - last_train).tolist())
    return float(np.mean(vals)) if vals else float("nan")


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale < 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def main() -> None:
    sample = load_sub(A2C8)
    train = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEYS).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    worlds, label_cube = load_world_labels(sample)
    deltas = pd.read_csv(DELTA_CSV)

    train_y = train[TARGETS].to_numpy(dtype=np.float64)
    train_prior = train_y.mean(axis=0)
    train_pair = pair_joint(train_y)
    train_corr = corr_vec(train_y)
    train_card = cardinality_hist(train_y)
    train_flip = transition_rates(train, train_y)
    train_subject_flip = subject_transition_rates(train, train_y)
    train_run = mean_run_lengths(train, train_y)
    subject_prior = train.groupby("subject_id")[TARGETS].mean()

    rows = []
    for world_idx, world in enumerate(label_cube):
        meta = worlds.iloc[world_idx].to_dict()
        world_prior = world.mean(axis=0)
        world_pair = pair_joint(world)
        world_corr = corr_vec(world)
        world_card = cardinality_hist(world)
        world_flip = transition_rates(sample, world)
        world_subject_flip = subject_transition_rates(sample, world)
        world_run = mean_run_lengths(sample, world)

        subject_maes = []
        for subject_id, g in sample.groupby("subject_id", sort=False):
            if subject_id not in subject_prior.index:
                continue
            loc = g.index.to_numpy(dtype=int)
            subject_maes.append(np.abs(world[loc].mean(axis=0) - subject_prior.loc[subject_id].to_numpy(dtype=float)))
        subject_target_mae = float(np.mean(np.vstack(subject_maes))) if subject_maes else float("nan")

        flip_subject_maes = []
        for subject_id in sample["subject_id"].unique():
            if subject_id not in train_subject_flip.index or subject_id not in world_subject_flip.index:
                continue
            a = world_subject_flip.loc[subject_id, TARGETS].to_numpy(dtype=np.float64)
            b = train_subject_flip.loc[subject_id, TARGETS].to_numpy(dtype=np.float64)
            mask = np.isfinite(a) & np.isfinite(b)
            if mask.any():
                flip_subject_maes.append(np.abs(a[mask] - b[mask]))
        flip_subject_mae = float(np.mean(np.concatenate(flip_subject_maes))) if flip_subject_maes else float("nan")

        rows.append(
            {
                "world_row": world_idx,
                "world_id": meta.get("world_id"),
                "objective": meta.get("objective"),
                "source_role": meta.get("source_role"),
                "duplicate_world": bool(meta.get("duplicate_world")),
                "max_abs_residual": float(meta.get("max_abs_residual")),
                "sum_abs_residual": float(meta.get("sum_abs_residual")),
                "positive_cell_count": int(meta.get("positive_cell_count")),
                "target_prior_mae": float(np.mean(np.abs(world_prior - train_prior))),
                "subject_target_mae": subject_target_mae,
                "pair_joint_mae": float(np.mean(np.abs(world_pair - train_pair))),
                "corr_mae": float(np.mean(np.abs(world_corr - train_corr))),
                "cardinality_l1": float(np.sum(np.abs(world_card - train_card))),
                "flip_global_mae": float(np.mean(np.abs(world_flip - train_flip))),
                "flip_subject_mae": flip_subject_mae,
                "runlen_mae": float(np.mean(np.abs(world_run - train_run))),
                "edge_flip_rate": edge_flip_rate(train, sample, world),
            }
        )

    feat = pd.DataFrame(rows)
    metric_cols = [
        "target_prior_mae",
        "subject_target_mae",
        "pair_joint_mae",
        "corr_mae",
        "cardinality_l1",
        "flip_global_mae",
        "flip_subject_mae",
        "runlen_mae",
        "edge_flip_rate",
    ]
    for col in metric_cols:
        feat[f"{col}_rz"] = robust_z(feat[col]).clip(lower=-3.0, upper=6.0)
    feat["plausibility_energy"] = feat[[f"{col}_rz" for col in metric_cols]].sum(axis=1)
    feat["plausibility_rank"] = feat["plausibility_energy"].rank(method="first", ascending=True).astype(int)
    feat["plausibility_quantile"] = feat["plausibility_energy"].rank(pct=True, ascending=True)

    delta_pivot = deltas.pivot_table(
        index=["world_id", "objective", "source_role"],
        columns="role",
        values="candidate_delta_vs_a2c8",
        aggfunc="first",
    ).reset_index()
    feat = feat.merge(delta_pivot, on=["world_id", "objective", "source_role"], how="left")
    for role in ["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_1bb_s0p65", "pair_sensor_6b"]:
        if role in feat.columns:
            feat[f"{role}_better"] = feat[role] < 0.0

    feat.to_csv(WORLD_FEATURE_OUT, index=False)

    bands = []
    band_specs = [
        ("all", np.ones(len(feat), dtype=bool)),
        ("random_plus_fit", feat["source_role"].isin(["random", "slack"]).to_numpy()),
        ("low_energy_half", (feat["plausibility_quantile"] <= 0.50).to_numpy()),
        ("low_energy_quarter", (feat["plausibility_quantile"] <= 0.25).to_numpy()),
        (
            "low_energy_random_plus_fit",
            ((feat["plausibility_quantile"] <= 0.50) & feat["source_role"].isin(["random", "slack"])).to_numpy(),
        ),
        (
            "high_energy_half",
            (feat["plausibility_quantile"] > 0.50).to_numpy(),
        ),
    ]
    for band_name, mask in band_specs:
        sub = feat[mask].copy()
        if sub.empty:
            continue
        for role in ["mixmin_0c916", "inverse7blend_1040", "pair_sensor_1bb", "pair_sensor_1bb_s0p65", "pair_sensor_6b"]:
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
                    "median_energy": float(sub["plausibility_energy"].median()),
                }
            )
    band_df = pd.DataFrame(bands)
    band_df.to_csv(BAND_OUT, index=False)

    adverse_mix = feat[feat.get("mixmin_0c916_better", False) == False].copy()
    adverse_inv = feat[feat.get("inverse7blend_1040_better", False) == False].copy()
    top_plausible = feat.sort_values("plausibility_energy").head(10)
    least_plausible = feat.sort_values("plausibility_energy", ascending=False).head(10)

    lines = [
        "# Binary Frontier World Plausibility Audit",
        "",
        "Question: are E30's adverse mixmin/inverse7 frontier worlds structurally implausible under train label dynamics?",
        "",
        "## Method",
        "",
        "- No target labels from test are used.",
        "- Each E30 binary world is scored against train-only label geometry: target priors, subject-target priors, pairwise co-occurrence, target correlation, row-cardinality histogram, temporal flip rates, run lengths, and train/test edge continuity.",
        "- Lower `plausibility_energy` means closer to train label dynamics under these diagnostics.",
        "",
        "## Candidate Support By Plausibility Band",
        "",
        markdown_table(band_df),
        "",
        "## Most Plausible Worlds",
        "",
        markdown_table(
            top_plausible[
                [
                    "objective",
                    "source_role",
                    "world_id",
                    "plausibility_energy",
                    "plausibility_rank",
                    "mixmin_0c916",
                    "inverse7blend_1040",
                    "pair_sensor_1bb",
                    "pair_sensor_6b",
                ]
            ]
        ),
        "",
        "## Least Plausible Worlds",
        "",
        markdown_table(
            least_plausible[
                [
                    "objective",
                    "source_role",
                    "world_id",
                    "plausibility_energy",
                    "plausibility_rank",
                    "mixmin_0c916",
                    "inverse7blend_1040",
                    "pair_sensor_1bb",
                    "pair_sensor_6b",
                ]
            ]
        ),
        "",
        "## Adverse Worlds",
        "",
        f"- mixmin adverse worlds: `{len(adverse_mix)}`.",
        f"- inverse7 adverse worlds: `{len(adverse_inv)}`.",
    ]
    if not adverse_mix.empty:
        lines.extend(
            [
                "",
                "### Mixmin Adverse Worlds",
                "",
                markdown_table(
                    adverse_mix[
                        [
                            "objective",
                            "source_role",
                            "world_id",
                            "plausibility_energy",
                            "plausibility_rank",
                            "target_prior_mae",
                            "subject_target_mae",
                            "pair_joint_mae",
                            "flip_subject_mae",
                            "mixmin_0c916",
                            "inverse7blend_1040",
                        ]
                    ].sort_values("mixmin_0c916", ascending=False)
                ),
            ]
        )
    if not adverse_inv.empty:
        lines.extend(
            [
                "",
                "### Inverse7 Adverse Worlds",
                "",
                markdown_table(
                    adverse_inv[
                        [
                            "objective",
                            "source_role",
                            "world_id",
                            "plausibility_energy",
                            "plausibility_rank",
                            "target_prior_mae",
                            "subject_target_mae",
                            "pair_joint_mae",
                            "flip_subject_mae",
                            "mixmin_0c916",
                            "inverse7blend_1040",
                        ]
                    ].sort_values("inverse7blend_1040", ascending=False)
                ),
            ]
        )

    low_half = band_df[(band_df["band"] == "low_energy_half") & (band_df["role"] == "mixmin_0c916")]
    low_half_rate = float(low_half["better_rate"].iloc[0]) if not low_half.empty else float("nan")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- worlds scored: `{len(feat)}`.",
            f"- low-energy-half mixmin better_rate: `{low_half_rate:.6f}`.",
        ]
    )
    if len(adverse_mix) and adverse_mix["plausibility_rank"].min() <= max(3, int(len(feat) * 0.25)):
        lines.append("- At least one mixmin-adverse world is among the most plausible quartile; plausibility diagnostics cannot safely discard it.")
    elif len(adverse_mix):
        lines.append("- Mixmin-adverse worlds are not in the most plausible quartile; this strengthens mixmin as a probe, but still does not prove the public world excludes them.")
    else:
        lines.append("- No mixmin-adverse world remains under this pool; mixmin would be one-sided under the audited worlds.")
    lines.append("- This is a LeJEPA-style world-geometry gate: useful for probe ranking, not a leaderboard prior.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(REPORT_OUT)
    print(
        {
            "worlds": len(feat),
            "mixmin_adverse": len(adverse_mix),
            "inverse7_adverse": len(adverse_inv),
            "low_half_mixmin_rate": low_half_rate,
        }
    )
    if not band_df.empty:
        print(band_df.to_string(index=False))


if __name__ == "__main__":
    main()
