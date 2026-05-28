#!/usr/bin/env python3
"""E52 post-mixmin binary-world sign stress.

E48 proved that mixmin is a real public anchor, while E50/E51 showed that
known-submission kNN selectors do not explain it. This audit keeps the E30/E32
binary worlds but conditions them on the observed mixmin public delta, then asks
whether any candidate has a stable one-sided sign versus mixmin.
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

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    A2C8,
    RAW05,
    STAGE2,
    FINAL9,
    ORDINAL,
    Q2_BAD,
    RESID_BAD,
    LEJEPA_BAD,
    KEYS,
    TARGETS,
    load_sub,
    locate,
    logit,
)
from public_lb_inverse_feasibility import CANDIDATES, load_prob  # noqa: E402
from public_lb_structural_prior_stress import markdown_table  # noqa: E402


WORLD_CSV = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"
LABEL_NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"
POST_MIXMIN_CANDIDATES = OUT / "post_mixmin_anchor_calendar_selector_candidates.csv"

WORLD_OUT = OUT / "post_mixmin_binary_world_sign_stress_worlds.csv"
BAND_OUT = OUT / "post_mixmin_binary_world_sign_stress_bands.csv"
SCORE_OUT = OUT / "post_mixmin_binary_world_sign_stress_scores.csv"
SUMMARY_OUT = OUT / "post_mixmin_binary_world_sign_stress_summary.csv"
REPORT_OUT = OUT / "post_mixmin_binary_world_sign_stress_report.md"


MIXMIN_FILE = "analysis_outputs/submission_mixmin_0c916bb4.csv"
MIXMIN_PUBLIC = 0.5763066405
A2C8_PUBLIC = 0.5774393210
RAW05_PUBLIC = 0.5775263072
ACTUAL_MIXMIN_DELTA_VS_A2C8 = MIXMIN_PUBLIC - A2C8_PUBLIC
RAW05_A2C8_GAP = RAW05_PUBLIC - A2C8_PUBLIC
EPS = 1e-6


def clip_prob(prob: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(prob, dtype=np.float64), EPS, 1.0 - EPS)


def target_logloss(prob: np.ndarray, y: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean(axis=0)


def binary_logloss(prob: np.ndarray, y: np.ndarray) -> float:
    return float(target_logloss(prob, y).mean())


def robust_z(values: pd.Series) -> pd.Series:
    med = float(values.median())
    mad = float((values - med).abs().median())
    scale = 1.4826 * mad
    if scale < 1e-12:
        std = float(values.std(ddof=0))
        scale = std if std > 1e-12 else 1.0
    return (values - med) / scale


def resolve_file(file_name: str | Path) -> Path | None:
    path = Path(file_name)
    if path.is_absolute() and path.exists():
        return path
    if path.exists():
        return path.resolve()
    root_path = ROOT / path
    if root_path.exists():
        return root_path
    located = locate(file_name)
    if located is not None:
        return located.resolve()
    return None


def add_candidate(rows: list[dict[str, Any]], name: str, role: str, source: str, file_name: str | Path) -> None:
    path = resolve_file(file_name)
    if path is None:
        return
    rows.append(
        {
            "name": name,
            "role": role,
            "source": source,
            "file": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
        }
    )


def selected_candidates_from_csv(
    rows: list[dict[str, Any]],
    csv_path: Path,
    source: str,
    role: str,
    n: int,
    sort_col: str | None = None,
    ascending: bool = True,
) -> None:
    if not csv_path.exists():
        return
    df = pd.read_csv(csv_path)
    if sort_col and sort_col in df.columns:
        df = df.sort_values(sort_col, ascending=ascending)
    for rec in df.head(n).to_dict("records"):
        file_name = rec.get("file") or rec.get("source_path") or rec.get("file_local")
        if not isinstance(file_name, str) or not file_name:
            continue
        name = Path(file_name).stem.replace("submission_", "")
        add_candidate(rows, name=name, role=role, source=source, file_name=file_name)


def candidate_table() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    add_candidate(rows, "mixmin", "active_frontier", "manual_anchor", MIXMIN_FILE)
    add_candidate(rows, "a2c8", "previous_frontier", "manual_anchor", A2C8)
    add_candidate(rows, "raw05", "known_public_anchor", "manual_anchor", RAW05)
    add_candidate(rows, "stage2", "known_public_anchor", "manual_anchor", STAGE2)
    add_candidate(rows, "ordinal", "known_public_anchor", "manual_anchor", ORDINAL)
    add_candidate(rows, "final9", "known_public_anchor", "manual_anchor", FINAL9)
    add_candidate(rows, "q2_jepa_bad", "known_bad_anchor", "manual_anchor", Q2_BAD)
    add_candidate(rows, "resid_bad", "known_bad_anchor", "manual_anchor", RESID_BAD)
    add_candidate(rows, "lejepa_bad", "known_bad_anchor", "manual_anchor", LEJEPA_BAD)

    for role, file_name in CANDIDATES:
        add_candidate(rows, role, "inverse_feasibility_candidate", "E26_candidate_list", file_name)

    if POST_MIXMIN_CANDIDATES.exists():
        post = pd.read_csv(POST_MIXMIN_CANDIDATES)
        for rec in post[["name", "role", "file"]].drop_duplicates().to_dict("records"):
            add_candidate(rows, str(rec["name"]), str(rec["role"]), "E51_candidate_table", str(rec["file"]))

    for path in sorted((OUT / "bridge_scan_candidates").glob("*.csv")):
        add_candidate(
            rows,
            path.stem.replace("submission_bridge_", "bridge_"),
            "raw_structure_bridge_variant",
            "E37_bridge_grid",
            path,
        )

    selected_candidates_from_csv(
        rows,
        OUT / "worldview_sensor_discriminability_audit.csv",
        source="E38_worldview_sensor",
        role="worldview_sensor",
        n=20,
        sort_col="sensor_information_score",
        ascending=False,
    )
    selected_candidates_from_csv(
        rows,
        OUT / "hidden_public_local_bridge_selected.csv",
        source="hidden_public_local_bridge_selected",
        role="hiddenloc_bridge",
        n=30,
        sort_col="bridge_rank_score",
        ascending=True,
    )
    selected_candidates_from_csv(
        rows,
        OUT / "jepa_public_minimax_rawsafe_bridge_selected.csv",
        source="jepa_public_minimax_rawsafe_bridge_selected",
        role="jepa_public_minimax_bridge",
        n=30,
        sort_col="bridge_score",
        ascending=True,
    )
    selected_candidates_from_csv(
        rows,
        OUT / "jepa_bridge_ensemble_selected.csv",
        source="jepa_bridge_ensemble_selected",
        role="jepa_bridge_ensemble",
        n=30,
        sort_col="bridge_score",
        ascending=True,
    )
    selected_candidates_from_csv(
        rows,
        OUT / "jepa_micro_bridge_ensemble_selected.csv",
        source="jepa_micro_bridge_ensemble_selected",
        role="jepa_micro_bridge_ensemble",
        n=30,
        sort_col="bridge_score",
        ascending=True,
    )

    out = pd.DataFrame(rows)
    out = out.drop_duplicates("file", keep="first").reset_index(drop=True)
    return out


def load_worlds_and_labels(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    worlds = pd.read_csv(WORLD_CSV)
    labels = np.load(LABEL_NPZ, allow_pickle=True)["labels"].astype(np.float64)
    if labels.ndim == 2:
        labels = labels.reshape(labels.shape[0], labels.shape[1] // len(TARGETS), len(TARGETS))
    if len(worlds) != labels.shape[0] and "has_incumbent" in worlds.columns:
        worlds = worlds[worlds["has_incumbent"].astype(bool)].reset_index(drop=True)
    if len(worlds) != labels.shape[0]:
        raise RuntimeError(f"world/label mismatch: {len(worlds)} vs {labels.shape[0]}")
    if labels.shape[1] != len(sample):
        raise RuntimeError(f"sample/label mismatch: {len(sample)} vs {labels.shape[1]}")

    worlds = worlds.copy()
    worlds["mixmin_actual_delta_vs_a2c8"] = ACTUAL_MIXMIN_DELTA_VS_A2C8
    worlds["mixmin_abs_error"] = (worlds["mixmin_0c916"] - ACTUAL_MIXMIN_DELTA_VS_A2C8).abs()
    worlds["mixmin_error_over_raw05_gap"] = worlds["mixmin_abs_error"] / RAW05_A2C8_GAP
    worlds["mixmin_fit_gap"] = worlds["mixmin_abs_error"] <= RAW05_A2C8_GAP
    worlds["mixmin_fit_2gap"] = worlds["mixmin_abs_error"] <= 2.0 * RAW05_A2C8_GAP
    worlds["mixmin_fit_5gap"] = worlds["mixmin_abs_error"] <= 5.0 * RAW05_A2C8_GAP
    worlds["mixmin_abs_error_rz"] = robust_z(worlds["mixmin_abs_error"]).clip(-3.0, 6.0)
    worlds["anchor_energy_rz"] = robust_z(worlds["anchor_energy"]).clip(-3.0, 6.0)
    worlds["postmix_world_energy"] = worlds["anchor_energy_rz"] + worlds["mixmin_abs_error_rz"]
    worlds["postmix_world_energy_rank"] = worlds["postmix_world_energy"].rank(method="first", ascending=True).astype(int)
    worlds["postmix_world_energy_quantile"] = worlds["postmix_world_energy"].rank(pct=True, ascending=True)
    return worlds, labels


def band_masks(worlds: pd.DataFrame) -> dict[str, np.ndarray]:
    random_fit = worlds["source_role"].isin(["random", "slack"]).to_numpy()
    low_half = (worlds["anchor_energy_quantile"] <= 0.50).to_numpy()
    low_quarter = (worlds["anchor_energy_quantile"] <= 0.25).to_numpy()
    mix_gap = worlds["mixmin_fit_gap"].to_numpy()
    mix_2gap = worlds["mixmin_fit_2gap"].to_numpy()
    mix_5gap = worlds["mixmin_fit_5gap"].to_numpy()
    post_half = (worlds["postmix_world_energy_quantile"] <= 0.50).to_numpy()
    post_quarter = (worlds["postmix_world_energy_quantile"] <= 0.25).to_numpy()
    return {
        "all": np.ones(len(worlds), dtype=bool),
        "old_low_anchor_half": low_half,
        "old_low_anchor_quarter": low_quarter,
        "mixmin_fit_gap": mix_gap,
        "mixmin_fit_2gap": mix_2gap,
        "mixmin_fit_5gap": mix_5gap,
        "mixmin_fit_gap_low_anchor_half": mix_gap & low_half,
        "mixmin_fit_2gap_low_anchor_half": mix_2gap & low_half,
        "mixmin_fit_2gap_low_anchor_quarter": mix_2gap & low_quarter,
        "mixmin_fit_gap_random_fit": mix_gap & random_fit,
        "postmix_energy_half": post_half,
        "postmix_energy_quarter": post_quarter,
        "postmix_energy_half_random_fit": post_half & random_fit,
    }


def movement_features(prob: np.ndarray, base_a2c8: np.ndarray, base_mixmin: np.ndarray) -> dict[str, float]:
    z = logit(prob)
    z_a2c8 = logit(base_a2c8)
    z_mix = logit(base_mixmin)
    return {
        "mean_abs_prob_move_vs_a2c8": float(np.mean(np.abs(prob - base_a2c8))),
        "mean_abs_prob_move_vs_mixmin": float(np.mean(np.abs(prob - base_mixmin))),
        "mean_abs_logit_move_vs_a2c8": float(np.mean(np.abs(z - z_a2c8))),
        "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(z - z_mix))),
        "max_abs_logit_move_vs_mixmin": float(np.max(np.abs(z - z_mix))),
    }


def score_candidates(candidates: pd.DataFrame, worlds: pd.DataFrame, labels: np.ndarray, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    masks = band_masks(worlds)
    mixmin_prob = load_prob(MIXMIN_FILE, sample)
    a2c8_prob = load_prob(A2C8, sample)
    mixmin_loss = np.asarray([binary_logloss(mixmin_prob, y) for y in labels], dtype=np.float64)
    mixmin_loss_t = np.asarray([target_logloss(mixmin_prob, y) for y in labels], dtype=np.float64)

    score_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        file_name = str(rec["file"])
        try:
            prob = load_prob(file_name, sample)
        except Exception:
            continue
        cand_loss = np.asarray([binary_logloss(prob, y) for y in labels], dtype=np.float64)
        delta = cand_loss - mixmin_loss
        cand_loss_t = np.asarray([target_logloss(prob, y) for y in labels], dtype=np.float64)
        target_delta = cand_loss_t - mixmin_loss_t
        movement = movement_features(prob, a2c8_prob, mixmin_prob)

        row: dict[str, Any] = {
            "name": rec["name"],
            "role": rec["role"],
            "source": rec["source"],
            "file": file_name,
            **movement,
        }
        for band_name, mask in masks.items():
            if not mask.any():
                continue
            sub = delta[mask]
            tsub = target_delta[mask]
            score_rows.append(
                {
                    "name": rec["name"],
                    "role": rec["role"],
                    "source": rec["source"],
                    "file": file_name,
                    "band": band_name,
                    "worlds": int(mask.sum()),
                    "better_rate_vs_mixmin": float((sub < 0.0).mean()),
                    "median_delta_vs_mixmin": float(np.median(sub)),
                    "mean_delta_vs_mixmin": float(np.mean(sub)),
                    "p10_delta_vs_mixmin": float(np.quantile(sub, 0.10)),
                    "p90_delta_vs_mixmin": float(np.quantile(sub, 0.90)),
                    "min_delta_vs_mixmin": float(np.min(sub)),
                    "max_delta_vs_mixmin": float(np.max(sub)),
                    "median_public_lb_proxy": float(MIXMIN_PUBLIC + np.median(sub)),
                    "max_public_lb_proxy": float(MIXMIN_PUBLIC + np.max(sub)),
                    **{f"target_mean_delta_{target}": float(tsub[:, target_i].mean()) for target_i, target in enumerate(TARGETS)},
                }
            )
            prefix = band_name
            row[f"{prefix}__worlds"] = int(mask.sum())
            row[f"{prefix}__better_rate"] = float((sub < 0.0).mean())
            row[f"{prefix}__median_delta"] = float(np.median(sub))
            row[f"{prefix}__mean_delta"] = float(np.mean(sub))
            row[f"{prefix}__max_delta"] = float(np.max(sub))
            row[f"{prefix}__min_delta"] = float(np.min(sub))
        summary_rows.append(row)

    summary = pd.DataFrame(summary_rows)
    if summary.empty:
        return pd.DataFrame(score_rows), summary

    def col(name: str) -> pd.Series:
        return summary[name] if name in summary.columns else pd.Series(np.nan, index=summary.index)

    is_mixmin = summary["file"].eq(str(Path(MIXMIN_FILE)))
    is_mixmin_equivalent = summary["mean_abs_logit_move_vs_mixmin"].fillna(np.inf) <= 1e-12
    core_one_sided = (
        (col("mixmin_fit_gap__better_rate").fillna(0.0) >= 1.0)
        & (col("mixmin_fit_gap__max_delta").fillna(1.0) < 0.0)
        & (col("postmix_energy_quarter__better_rate").fillna(0.0) >= 1.0)
        & (col("postmix_energy_quarter__max_delta").fillna(1.0) < 0.0)
    )
    loose_sign = (
        (col("mixmin_fit_2gap__better_rate").fillna(0.0) >= 0.75)
        & (col("mixmin_fit_2gap__median_delta").fillna(1.0) < 0.0)
        & (col("postmix_energy_half__better_rate").fillna(0.0) >= 0.75)
        & (col("postmix_energy_half__median_delta").fillna(1.0) < 0.0)
        & (col("mixmin_fit_2gap__max_delta").fillna(1.0) <= RAW05_A2C8_GAP)
    )
    near_tie = (
        (col("mixmin_fit_gap__median_delta").abs().fillna(1.0) <= RAW05_A2C8_GAP)
        & (col("postmix_energy_quarter__median_delta").abs().fillna(1.0) <= RAW05_A2C8_GAP)
        & (col("mixmin_fit_gap__max_delta").fillna(1.0) <= RAW05_A2C8_GAP)
    )
    summary["mixmin_equivalent_prediction"] = is_mixmin_equivalent
    summary["strict_better_than_mixmin_gate"] = core_one_sided & ~is_mixmin_equivalent
    summary["loose_better_than_mixmin_gate"] = loose_sign & ~is_mixmin_equivalent
    summary["near_tie_with_mixmin_gate"] = near_tie & ~is_mixmin_equivalent
    summary["postmix_sign_rank_score"] = (
        col("mixmin_fit_gap__median_delta").fillna(0.003)
        + 0.50 * col("postmix_energy_quarter__median_delta").fillna(0.003)
        + 0.25 * col("mixmin_fit_2gap__max_delta").fillna(0.003)
        - 0.00025 * col("mixmin_fit_gap__better_rate").fillna(0.0)
        - 0.00015 * col("postmix_energy_quarter__better_rate").fillna(0.0)
    )
    summary = summary.sort_values(
        [
            "strict_better_than_mixmin_gate",
            "loose_better_than_mixmin_gate",
            "near_tie_with_mixmin_gate",
            "postmix_sign_rank_score",
        ],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    return pd.DataFrame(score_rows), summary


def summarize_bands(worlds: pd.DataFrame, masks: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, mask in masks.items():
        if not mask.any():
            continue
        sub = worlds[mask]
        rows.append(
            {
                "band": name,
                "worlds": int(len(sub)),
                "random_fit_worlds": int(sub["source_role"].isin(["random", "slack"]).sum()),
                "median_anchor_energy": float(sub["anchor_energy"].median()),
                "median_postmix_world_energy": float(sub["postmix_world_energy"].median()),
                "median_mixmin_error_over_gap": float(sub["mixmin_error_over_raw05_gap"].median()),
                "min_mixmin_delta_vs_a2c8": float(sub["mixmin_0c916"].min()),
                "median_mixmin_delta_vs_a2c8": float(sub["mixmin_0c916"].median()),
                "max_mixmin_delta_vs_a2c8": float(sub["mixmin_0c916"].max()),
            }
        )
    return pd.DataFrame(rows)


def write_report(worlds: pd.DataFrame, bands: pd.DataFrame, scores: pd.DataFrame, summary: pd.DataFrame) -> None:
    strict = summary[summary["strict_better_than_mixmin_gate"].fillna(False)] if not summary.empty else summary
    loose = summary[summary["loose_better_than_mixmin_gate"].fillna(False)] if not summary.empty else summary
    near = summary[summary["near_tie_with_mixmin_gate"].fillna(False)] if not summary.empty else summary
    top_cols = [
        "name",
        "role",
        "source",
        "mixmin_fit_gap__worlds",
        "mixmin_fit_gap__better_rate",
        "mixmin_fit_gap__median_delta",
        "mixmin_fit_gap__max_delta",
        "mixmin_fit_2gap__better_rate",
        "postmix_energy_quarter__better_rate",
        "postmix_energy_quarter__median_delta",
        "postmix_energy_quarter__max_delta",
        "mean_abs_logit_move_vs_mixmin",
        "mixmin_equivalent_prediction",
        "strict_better_than_mixmin_gate",
        "loose_better_than_mixmin_gate",
        "near_tie_with_mixmin_gate",
        "postmix_sign_rank_score",
        "file",
    ]
    top = summary[[c for c in top_cols if c in summary.columns]].head(20) if not summary.empty else pd.DataFrame()
    band_view = bands.copy()

    lines = [
        "# E52 Post-Mixmin Binary-World Sign Stress",
        "",
        "## Observe",
        "",
        "Mixmin is now a real public anchor. E50/E51 failed to translate calendar or anchor-calendar fingerprints into a known-submission selector.",
        "",
        "## Wonder",
        "",
        "If we condition the E30/E32 binary worlds on the observed mixmin public delta, does any existing candidate have a stable one-sided sign versus mixmin?",
        "",
        "## Hypothesis",
        "",
        "H52: mixmin is not just the best known public file; it may be a local sign frontier inside the current binary-world family. If true, post-mixmin feasible worlds should not certify another candidate as one-sided better than mixmin. If false, at least one candidate should beat mixmin across mixmin-compatible and low-energy world bands.",
        "",
        "## Method",
        "",
        f"- Actual mixmin delta versus a2c8: `{ACTUAL_MIXMIN_DELTA_VS_A2C8:.10f}`.",
        f"- Raw05-a2c8 gap used as one resolution unit: `{RAW05_A2C8_GAP:.10f}`.",
        "- Reused the E30 frontier-box binary worlds and E32 anchor-energy scores.",
        "- Defined post-mixmin feasible bands by whether each world reproduces mixmin's observed delta within 1x, 2x, or 5x the raw05-a2c8 gap, plus LeJEPA-style postmix energy combining old anchor energy and mixmin residual.",
        "- Scored curated candidates from E51, E37 bridge variants, E38 worldview sensors, and top selected bridge families by LogLoss delta versus mixmin on every binary world.",
        "",
        "## World Bands",
        "",
        markdown_table(band_view),
        "",
        "## Top Candidate Signs",
        "",
        markdown_table(top),
        "",
        "## Decision",
        "",
        f"- candidates scored: `{len(summary)}`.",
        f"- strict better-than-mixmin gates: `{len(strict)}`.",
        f"- loose better-than-mixmin gates: `{len(loose)}`.",
        f"- near-tie-with-mixmin gates: `{len(near)}`.",
    ]
    if len(strict):
        best = strict.iloc[0]
        lines.append(
            f"- Strict sign candidate exists: `{best['file']}`. It should not be submitted until raw/selector/private-risk stress explains why it beats mixmin rather than overfitting the conditioned worlds."
        )
    elif len(loose):
        best = loose.iloc[0]
        lines.append(
            f"- Only loose sign support exists, led by `{best['file']}`. Treat this as a diagnostic near-frontier direction, not a submission."
        )
    elif len(near):
        best = near.iloc[0]
        lines.append(
            f"- No candidate is one-sided better. Best surviving pattern is a near-tie, led by `{best['file']}`. This supports mixmin as a local frontier under the current binary-world family."
        )
    else:
        lines.append("- No candidate even reaches the near-tie gate. The current binary-world family strongly says not to submit a mixmin-relative replacement.")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{WORLD_OUT.relative_to(ROOT)}`",
            f"- `{BAND_OUT.relative_to(ROOT)}`",
            f"- `{SCORE_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    worlds, labels = load_worlds_and_labels(sample)
    masks = band_masks(worlds)
    bands = summarize_bands(worlds, masks)
    candidates = candidate_table()
    scores, summary = score_candidates(candidates, worlds, labels, sample)

    worlds.to_csv(WORLD_OUT, index=False)
    bands.to_csv(BAND_OUT, index=False)
    scores.to_csv(SCORE_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(worlds, bands, scores, summary)

    print(
        f"worlds={len(worlds)} candidates={len(summary)} "
        f"strict={int(summary['strict_better_than_mixmin_gate'].sum()) if not summary.empty else 0} "
        f"loose={int(summary['loose_better_than_mixmin_gate'].sum()) if not summary.empty else 0} "
        f"near_tie={int(summary['near_tie_with_mixmin_gate'].sum()) if not summary.empty else 0}"
    )
    if not summary.empty:
        cols = [
            "name",
            "role",
            "mixmin_fit_gap__better_rate",
            "mixmin_fit_gap__median_delta",
            "mixmin_fit_gap__max_delta",
            "postmix_energy_quarter__better_rate",
            "postmix_energy_quarter__median_delta",
            "strict_better_than_mixmin_gate",
            "loose_better_than_mixmin_gate",
            "near_tie_with_mixmin_gate",
            "file",
        ]
        print(summary[[c for c in cols if c in summary.columns]].head(15).to_string(index=False))
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
