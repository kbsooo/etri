#!/usr/bin/env python3
"""E37 inverse7/mixmin raw-anchor bridge scale scan.

E36 found raw observed structure supports inverse7, not mixmin. E32/E33 favor
mixmin under anchor-loss binary-world geometry. This scan asks whether a
scaled or blended direction can keep both signals while reducing selector veto.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
BRIDGE_DIR = OUT / "bridge_scan_candidates"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from direction_probe_selector_reconciliation import add_flags  # noqa: E402
from hidden_subset_selector_stress import candidate_stress_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    KEYS,
    TARGETS,
    feature_row,
    load_sub,
    logit,
)
from public_pairwise_order_selector import evaluate_pairwise_models, score_candidates  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
from raw_structure_pseudolabel_candidate_stress import (  # noqa: E402
    aligned_labels,
    candidate_scores,
    cluster_pseudo,
    knn_pseudo,
    load_frame,
    make_xy,
    soft_logloss,
    subject_mean_pseudo,
    subject_temporal_pseudo,
    summarize as summarize_raw,
)


MIXMIN = "analysis_outputs/submission_mixmin_0c916bb4.csv"
INV7 = "analysis_outputs/submission_inverse7blend_1040423d.csv"

LABEL_NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"
WORLD_CSV = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"

DETAIL_OUT = OUT / "inverse7_raw_anchor_bridge_scale_scan_scores.csv"
RAW_OUT = OUT / "inverse7_raw_anchor_bridge_scale_scan_raw_scores.csv"
ANCHOR_OUT = OUT / "inverse7_raw_anchor_bridge_scale_scan_anchor_bands.csv"
SELECTOR_OUT = OUT / "inverse7_raw_anchor_bridge_scale_scan_selector_scores.csv"
REPORT_OUT = OUT / "inverse7_raw_anchor_bridge_scale_scan_report.md"

EPS = 1e-6


def expit(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def prob_from_file(path: str | Path, sample: pd.DataFrame) -> np.ndarray:
    return load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)


def write_submission(path: Path, sample: pd.DataFrame, prob: np.ndarray) -> None:
    df = sample[KEYS].copy()
    for target_i, target in enumerate(TARGETS):
        df[target] = clip_prob(prob[:, target_i])
    df.to_csv(path, index=False)


def variant_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for scale in [0.25, 0.50, 0.75, 1.00, 1.25, 1.50]:
        specs.append({"role": f"inv7_s{scale:.2f}".replace(".", "p"), "family": "pure_inv7", "scale": scale, "mix_weight": 0.0})
    for scale in [0.25, 0.50, 0.75, 1.00]:
        specs.append({"role": f"mixmin_s{scale:.2f}".replace(".", "p"), "family": "pure_mixmin", "scale": scale, "mix_weight": 1.0})
    for mix_weight in [0.25, 0.50, 0.75]:
        for scale in [0.50, 0.75, 1.00, 1.25]:
            specs.append(
                {
                    "role": f"blend_m{mix_weight:.2f}_s{scale:.2f}".replace(".", "p"),
                    "family": "inv7_mixmin_blend",
                    "scale": scale,
                    "mix_weight": mix_weight,
                }
            )
    return specs


def generate_variants() -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    base = prob_from_file(A2C8, sample)
    inv7 = prob_from_file(INV7, sample)
    mixmin = prob_from_file(MIXMIN, sample)
    z_base = logit(base)
    d_inv7 = logit(inv7) - z_base
    d_mix = logit(mixmin) - z_base

    rows: list[dict[str, Any]] = []
    preds: dict[str, np.ndarray] = {"a2c8": base}
    for spec in variant_specs():
        role = str(spec["role"])
        mix_weight = float(spec["mix_weight"])
        scale = float(spec["scale"])
        direction = (1.0 - mix_weight) * d_inv7 + mix_weight * d_mix
        prob = clip_prob(expit(z_base + scale * direction))
        file_name = f"submission_bridge_{role}.csv"
        path = BRIDGE_DIR / file_name
        write_submission(path, sample, prob)
        preds[role] = prob
        rows.append(
            {
                "role": role,
                "family": spec["family"],
                "scale": scale,
                "mix_weight": mix_weight,
                "file": str(path.relative_to(ROOT)),
                "basename": file_name,
                "mean_abs_prob_move_vs_a2c8": float(np.mean(np.abs(prob - base))),
                "mean_abs_logit_move_vs_a2c8": float(np.mean(np.abs(logit(prob) - z_base))),
                "mean_abs_logit_move_vs_inv7": float(np.mean(np.abs(logit(prob) - logit(inv7)))),
                "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(logit(prob) - logit(mixmin)))),
            }
        )
    return pd.DataFrame(rows), preds


def build_raw_sources() -> tuple[list[Any], pd.DataFrame]:
    features, train, test = load_frame()
    train_feat, test_feat = aligned_labels(features, train, test)
    y_train = train_feat[TARGETS].to_numpy(float)
    numeric_cols = list(features.select_dtypes(include="number").columns)
    meta_cols = {"dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"}
    sensor_cols = [c for c in numeric_cols if c not in meta_cols and c not in TARGETS]
    count_cols = [c for c in sensor_cols if c.endswith("_count")]
    stat_cols = [c for c in sensor_cols if not c.endswith("_count")]
    sources = [
        subject_mean_pseudo(train_feat, test_feat, y_train),
        subject_temporal_pseudo(train_feat, test_feat, y_train, k=3),
        subject_temporal_pseudo(train_feat, test_feat, y_train, k=7),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=5, name="sensor_all_knn_k5", tier="raw_feature_knn_prior"),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=15, name="sensor_all_knn_k15", tier="raw_feature_knn_prior"),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=15, name="sensor_all_cross_subject_knn_k15", tier="raw_feature_cross_subject_prior", exclude_same_subject=True),
        knn_pseudo(train_feat, test_feat, count_cols, y_train, k=10, name="sensor_count_knn_k10", tier="missingness_coverage_prior"),
        knn_pseudo(train_feat, test_feat, stat_cols, y_train, k=10, name="sensor_stat_knn_k10", tier="sensor_behavior_prior"),
        cluster_pseudo(train_feat, test_feat, sensor_cols, y_train, n_clusters=12),
        cluster_pseudo(train_feat, test_feat, sensor_cols, y_train, n_clusters=24),
    ]
    return sources, test_feat


def score_raw(preds: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    sources, _ = build_raw_sources()
    scores = candidate_scores(sources, preds)
    summary = summarize_raw(scores, pd.DataFrame())
    summary["raw_support_gate"] = (
        (summary["support_rate"] >= 0.80)
        & (summary["mean_delta"] < 0.0)
        & (summary["worst_delta"] <= 0.0)
    )
    return scores, summary


def binary_logloss(prob: np.ndarray, y: np.ndarray) -> float:
    p = clip_prob(prob)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def score_anchor_bands(variant_meta: pd.DataFrame, preds: dict[str, np.ndarray]) -> pd.DataFrame:
    worlds = pd.read_csv(WORLD_CSV)
    labels = np.load(LABEL_NPZ, allow_pickle=True)["labels"].astype(np.float64)
    labels = labels.reshape(-1, len(preds["a2c8"]), len(TARGETS))
    if len(worlds) != labels.shape[0]:
        worlds = worlds[worlds["has_incumbent"].astype(bool)].reset_index(drop=True)
    if len(worlds) != labels.shape[0]:
        raise RuntimeError("world/label count mismatch")

    base = preds["a2c8"]
    base_loss = np.asarray([binary_logloss(base, y) for y in labels], dtype=np.float64)
    band_specs = {
        "all": np.ones(len(worlds), dtype=bool),
        "random_plus_fit": worlds["source_role"].isin(["random", "slack"]).to_numpy(),
        "low_anchor_energy_half": (worlds["anchor_energy_quantile"] <= 0.50).to_numpy(),
        "low_anchor_energy_quarter": (worlds["anchor_energy_quantile"] <= 0.25).to_numpy(),
        "low_anchor_energy_random_plus_fit": (
            (worlds["anchor_energy_quantile"] <= 0.50)
            & worlds["source_role"].isin(["random", "slack"])
        ).to_numpy(),
    }

    rows: list[dict[str, Any]] = []
    roles = variant_meta["role"].astype(str).tolist()
    for role in roles:
        cand = preds[role]
        delta = np.asarray([binary_logloss(cand, y) for y in labels], dtype=np.float64) - base_loss
        for band, mask in band_specs.items():
            sub = delta[mask]
            if len(sub) == 0:
                continue
            rows.append(
                {
                    "role": role,
                    "band": band,
                    "worlds": int(len(sub)),
                    "better_rate": float(np.mean(sub < 0.0)),
                    "min_delta": float(np.min(sub)),
                    "median_delta": float(np.median(sub)),
                    "max_delta": float(np.max(sub)),
                }
            )
    return pd.DataFrame(rows)


def score_selectors(variant_meta: pd.DataFrame) -> pd.DataFrame:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    rows: list[dict[str, Any]] = []
    for rec in variant_meta.to_dict("records"):
        path = ROOT / str(rec["file"])
        row = feature_row(path, sample, refs, ref_vecs)
        row.update(
            {
                "file": str(path.relative_to(ROOT)),
                "source_path": str(path.relative_to(ROOT)),
                "basename": path.name,
                "probe_family": str(rec["family"]),
                "probe_role": str(rec["role"]),
                "role": str(rec["role"]),
            }
        )
        rows.append(row)
    features = pd.DataFrame(rows)
    old_scored = candidate_stress_scores(known, features)
    old_cols = [
        "file",
        "selector_delta_vs_a2c8_public",
        "selector_p90_delta_vs_a2c8_public",
        "selector_stress_spread",
        "beats_a2c8_scenario_rate",
        "resolved_better_than_a2c8_gate",
        "candidate_selector_risk",
    ]
    merged = features.merge(old_scored[[col for col in old_cols if col in old_scored.columns]], on="file", how="left")
    model_df, _ = evaluate_pairwise_models(known)
    pair_scored = score_candidates(known, merged, model_df)
    return add_flags(pair_scored)


def pivot_anchor(anchor: pd.DataFrame) -> pd.DataFrame:
    cols = []
    for metric in ["better_rate", "median_delta", "max_delta"]:
        pivot = anchor.pivot(index="role", columns="band", values=metric)
        pivot.columns = [f"anchor_{band}_{metric}" for band in pivot.columns]
        cols.append(pivot)
    return pd.concat(cols, axis=1).reset_index()


def final_scores(
    variant_meta: pd.DataFrame,
    raw_summary: pd.DataFrame,
    anchor_bands: pd.DataFrame,
    selector_scores: pd.DataFrame,
) -> pd.DataFrame:
    raw_cols = [
        "role",
        "support_count",
        "support_rate",
        "mean_delta",
        "worst_delta",
        "best_delta",
        "mean_toward_rate",
        "mean_abs_move",
        "raw_support_gate",
    ]
    raw = raw_summary[raw_cols].rename(
        columns={
            "mean_delta": "raw_mean_delta",
            "worst_delta": "raw_worst_delta",
            "best_delta": "raw_best_delta",
            "mean_abs_move": "raw_mean_abs_move",
        }
    )
    sel_cols = [
        "role",
        "file",
        "source_path",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "q3s4_move_share",
        "stage_move_share",
        "old_majority",
        "pair_majority",
        "two_selector_majority",
        "submit_shape",
        "reconciliation_rank",
    ]
    sel = selector_scores[[col for col in sel_cols if col in selector_scores.columns]].copy()
    anchors = pivot_anchor(anchor_bands)
    out = variant_meta.merge(raw, on="role", how="left").merge(anchors, on="role", how="left")
    out = out.merge(sel, on="role", how="left", suffixes=("", "_selector"))
    out["anchor_low_half_gate"] = (
        (out["anchor_low_anchor_energy_half_better_rate"] >= 1.0)
        & (out["anchor_low_anchor_energy_half_max_delta"] < 0.0)
    )
    out["anchor_low_quarter_gate"] = (
        (out["anchor_low_anchor_energy_quarter_better_rate"] >= 1.0)
        & (out["anchor_low_anchor_energy_quarter_max_delta"] < 0.0)
    )
    out["selector_hard_veto"] = (
        ~out["two_selector_majority"].fillna(False).astype(bool)
        & (
            (out["pair_delta_vs_a2c8_p90"].fillna(1.0) > 0.0)
            | (out["selector_p90_delta_vs_a2c8_public"].fillna(1.0) > 0.0)
        )
    )
    out["bridge_gate"] = (
        out["raw_support_gate"].fillna(False).astype(bool)
        & out["anchor_low_half_gate"].fillna(False).astype(bool)
        & out["anchor_low_quarter_gate"].fillna(False).astype(bool)
        & ~out["selector_hard_veto"].fillna(True).astype(bool)
    )
    out["bridge_rank_score"] = (
        out["pair_delta_vs_a2c8_p90"].fillna(0.002)
        + 0.35 * out["selector_p90_delta_vs_a2c8_public"].fillna(0.002)
        + 0.00025 * out["bad_axis_abs_load"].fillna(0.0)
        - 0.00040 * out["support_rate"].fillna(0.0)
        - 0.00025 * out["anchor_low_anchor_energy_half_better_rate"].fillna(0.0)
        - 0.00010 * out["anchor_low_anchor_energy_quarter_better_rate"].fillna(0.0)
    )
    return out.sort_values(
        ["bridge_gate", "raw_support_gate", "anchor_low_half_gate", "bridge_rank_score"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._"
    view = df.copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def write_report(scores: pd.DataFrame) -> None:
    top_cols = [
        "role",
        "family",
        "scale",
        "mix_weight",
        "support_rate",
        "raw_mean_delta",
        "raw_worst_delta",
        "anchor_low_anchor_energy_half_better_rate",
        "anchor_low_anchor_energy_half_max_delta",
        "anchor_low_anchor_energy_quarter_better_rate",
        "pair_delta_vs_a2c8_p90",
        "pair_beats_a2c8_rate",
        "selector_p90_delta_vs_a2c8_public",
        "beats_a2c8_scenario_rate",
        "bad_axis_abs_load",
        "two_selector_majority",
        "selector_hard_veto",
        "bridge_gate",
        "bridge_rank_score",
        "file",
    ]
    top = scores[[col for col in top_cols if col in scores.columns]].head(18)
    gates = scores[scores["bridge_gate"].fillna(False).astype(bool)]
    raw_gate = int(scores["raw_support_gate"].fillna(False).sum())
    anchor_gate = int((scores["anchor_low_half_gate"].fillna(False) & scores["anchor_low_quarter_gate"].fillna(False)).sum())
    two_sel = int(scores["two_selector_majority"].fillna(False).sum())

    lines = [
        "# E37 Inverse7 Raw-Anchor Bridge Scale Scan",
        "",
        "## Observe",
        "",
        "E36 split the probe family: mixmin is stronger under anchor-loss/binary-world geometry, while inverse7 is stronger under train-derived raw observed structure.",
        "",
        "## Wonder",
        "",
        "Can a scaled inverse7 or inverse7/mixmin blend preserve raw-structure support and anchor-loss support while reducing the pairwise/old selector veto?",
        "",
        "## Hypothesis",
        "",
        "H36: inverse7 is a bridge direction between raw observed structure and anchor-loss worlds. If true, some scale/blend variant should keep raw pseudo-label support, keep low-anchor-energy binary-world support, and have weaker selector veto than the original inverse7/mixmin files. If false, raw support and anchor-loss support remain separated by selector conflict.",
        "",
        "## Method",
        "",
        "- Generated logit-space variants from A2C8 toward inverse7, mixmin, and inverse7/mixmin blended directions.",
        "- Scored all variants against the same 10 raw-structure pseudo-label sources from E36.",
        "- Scored all variants against E32 binary anchor-loss worlds and low-energy bands.",
        "- Scored all variants with the old hidden-subset selector and the pairwise public-order selector.",
        "",
        "## Result",
        "",
        f"- variants scanned: `{len(scores)}`.",
        f"- raw support gates: `{raw_gate}`.",
        f"- anchor low-half+quarter gates: `{anchor_gate}`.",
        f"- two-selector majority variants: `{two_sel}`.",
        f"- strict bridge gates: `{len(gates)}`.",
        "",
        "## Top Variants",
        "",
        markdown_table(top),
        "",
        "## Decision",
        "",
    ]
    if len(gates):
        best = gates.sort_values("bridge_rank_score").iloc[0]
        lines.append(
            f"A local bridge candidate exists: `{best['file']}`. It still needs a final independent audit before any public claim, but E37 makes it the first scale/blend direction that crosses the raw+anchor+selector gate."
        )
    else:
        best = scores.iloc[0]
        lines.append(
            f"No variant resolves the full bridge gate. Best-ranked diagnostic is `{best['file']}`, but it remains a sensor, not a certified improvement. This means E36's inverse7 support and E32/E33's mixmin anchor support are still not reconciled locally."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{DETAIL_OUT.relative_to(ROOT)}`",
        f"- `{RAW_OUT.relative_to(ROOT)}`",
        f"- `{ANCHOR_OUT.relative_to(ROOT)}`",
        f"- `{SELECTOR_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    variant_meta, preds = generate_variants()
    raw_scores, raw_summary = score_raw(preds)
    anchor_bands = score_anchor_bands(variant_meta, preds)
    selector_scores = score_selectors(variant_meta)
    scores = final_scores(variant_meta, raw_summary, anchor_bands, selector_scores)

    raw_scores.to_csv(RAW_OUT, index=False)
    anchor_bands.to_csv(ANCHOR_OUT, index=False)
    selector_scores.to_csv(SELECTOR_OUT, index=False)
    scores.to_csv(DETAIL_OUT, index=False)
    write_report(scores)

    print(f"variants={len(scores)}")
    print(f"bridge_gates={int(scores['bridge_gate'].fillna(False).sum())}")
    print(f"raw_gates={int(scores['raw_support_gate'].fillna(False).sum())}")
    print(f"two_selector_majority={int(scores['two_selector_majority'].fillna(False).sum())}")
    print(
        scores[
            [
                "role",
                "support_rate",
                "anchor_low_anchor_energy_half_better_rate",
                "pair_delta_vs_a2c8_p90",
                "selector_p90_delta_vs_a2c8_public",
                "bridge_gate",
                "bridge_rank_score",
                "file",
            ]
        ]
        .head(12)
        .to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
