#!/usr/bin/env python3
"""E181: current-anchor binary-world counterprior audit.

E180 showed that visible priors are not reliable decisive-cell selectors at the
frontier. This audit asks a different JEPA-style question:

    If we treat existing binary hidden-label worlds as candidate target
    representations and re-score them against all current public anchors, which
    live submissions do those worlds support?

The goal is not to optimize public LB or create a submission. The goal is to
test whether E176's visible-prior support survives a binary-world
counter-prior, and whether another live branch is more aligned with the current
anchor-fit worlds.
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

from public_anchor_bottleneck_decomposition import A2C8, TARGETS, known_public_table, load_sub, locate  # noqa: E402
from public_lb_inverse_feasibility import load_prob  # noqa: E402
from public_lb_binary_anchor_loss_geometry import target_logloss  # noqa: E402
from public_lb_structural_prior_stress import markdown_table  # noqa: E402


WORLD_CSV = OUT / "public_lb_binary_anchor_loss_geometry_worlds.csv"
LABEL_NPZ = OUT / "public_lb_binary_frontier_box_pool_labels.npz"
E180_CELLS = OUT / "e180_known_anchor_decisive_cell_visibility_cells.csv"

WORLD_OUT = OUT / "e181_e176_binary_world_counterprior_worlds.csv"
ANCHOR_OUT = OUT / "e181_e176_binary_world_counterprior_anchor_residuals.csv"
CANDIDATE_OUT = OUT / "e181_e176_binary_world_counterprior_candidate_worlds.csv"
BAND_OUT = OUT / "e181_e176_binary_world_counterprior_candidate_bands.csv"
CELL_OUT = OUT / "e181_e176_binary_world_counterprior_e176_cells.csv"
CELL_SUMMARY_OUT = OUT / "e181_e176_binary_world_counterprior_e176_cell_summary.csv"
REPORT_OUT = OUT / "e181_e176_binary_world_counterprior_report.md"


BASE_FILE = "submission_e95_hardtail_541e3973.csv"
LIVE_CANDIDATES = [
    ("e176", "risk_adjusted_broad_q2_underopen", "submission_e176_abl_q2_to0p75_91e49725.csv"),
    ("e174", "max_edge_broad_reopen", "submission_e174_ro_fc_top75_to1p0_95638e73.csv"),
    ("e172", "visible_tail_repair", "submission_e172_vis_pos_all_keep0p25_d90f4407.csv"),
    ("e169", "context_veto_broad_body", "submission_e169_ctx_veto_c5e806e3.csv"),
    ("e166", "raw_broad_survivor", "submission_e166_broadsurv_s0p01_d8bfa94b.csv"),
    ("e154", "repaired_all_four_branch", "submission_e154_s3repair_9f2e2e73.csv"),
    ("e144", "active_boundary_branch", "submission_e144_activeboundary_d7b4b331.csv"),
    ("mixmin", "previous_public_anchor", "submission_mixmin_0c916bb4.csv"),
    ("e101", "resolved_negative_q2s3_tail", "submission_e101_q2s3tail_177569bc.csv"),
]

BANDS = [
    ("best3_current_anchor_residual", 3),
    ("best5_current_anchor_residual", 5),
    ("best10_current_anchor_residual", 10),
    ("best15_current_anchor_residual", 15),
    ("all_binary_worlds", None),
]


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 60) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return markdown_table(view.head(n))


def load_worlds_and_labels(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    worlds = pd.read_csv(WORLD_CSV)
    labels = np.load(LABEL_NPZ, allow_pickle=True)["labels"].astype(np.float64)
    labels = labels.reshape(labels.shape[0], len(sample), len(TARGETS))
    if len(worlds) != len(labels):
        if "world_row" in worlds.columns:
            worlds = worlds.sort_values("world_row").reset_index(drop=True)
    if len(worlds) != len(labels):
        raise RuntimeError(f"world/label mismatch: {len(worlds)} vs {len(labels)}")
    worlds = worlds.copy().reset_index(drop=True)
    worlds["label_world_idx"] = np.arange(len(worlds), dtype=int)
    return worlds, labels


def score_current_anchors(
    labels: np.ndarray,
    known: pd.DataFrame,
    known_probs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    world_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    for world_idx, y in enumerate(labels):
        residuals = []
        for rec in known.to_dict("records"):
            file_name = str(rec["file"])
            public_lb = float(rec["public_lb"])
            fitted = float(target_logloss(known_probs[file_name], y).mean())
            residual = fitted - public_lb
            residuals.append(residual)
            residual_rows.append(
                {
                    "label_world_idx": world_idx,
                    "file": file_name,
                    "public_lb": public_lb,
                    "fitted_lb": fitted,
                    "residual": residual,
                    "abs_residual": abs(residual),
                }
            )
        residuals_arr = np.asarray(residuals, dtype=np.float64)
        world_rows.append(
            {
                "label_world_idx": world_idx,
                "current_anchor_sum_abs_residual": float(np.abs(residuals_arr).sum()),
                "current_anchor_mean_abs_residual": float(np.abs(residuals_arr).mean()),
                "current_anchor_max_abs_residual": float(np.abs(residuals_arr).max()),
                "current_anchor_rmse": float(np.sqrt(np.mean(residuals_arr * residuals_arr))),
            }
        )
    return pd.DataFrame(world_rows), pd.DataFrame(residual_rows)


def candidate_world_deltas(
    labels: np.ndarray,
    sample: pd.DataFrame,
    world_scores: pd.DataFrame,
) -> pd.DataFrame:
    base_prob = load_prob(BASE_FILE, sample)
    rows: list[dict[str, Any]] = []
    for name, role, file_name in LIVE_CANDIDATES:
        if locate(file_name) is None:
            continue
        prob = load_prob(file_name, sample)
        for world_idx, y in enumerate(labels):
            delta = float(target_logloss(prob, y).mean() - target_logloss(base_prob, y).mean())
            rows.append(
                {
                    "candidate": name,
                    "role": role,
                    "file": file_name,
                    "base_file": BASE_FILE,
                    "label_world_idx": world_idx,
                    "delta_vs_e95": delta,
                    "candidate_better_than_e95": bool(delta < 0.0),
                }
            )
    out = pd.DataFrame(rows)
    out = out.merge(
        world_scores[
            [
                "label_world_idx",
                "current_anchor_sum_abs_residual",
                "current_anchor_max_abs_residual",
                "current_anchor_residual_rank",
            ]
        ],
        on="label_world_idx",
        how="left",
        validate="many_to_one",
    )
    return out


def summarize_candidate_bands(candidate_worlds: pd.DataFrame, world_order: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for band_name, n_worlds in BANDS:
        if n_worlds is None:
            band_worlds = set(world_order["label_world_idx"].tolist())
        else:
            band_worlds = set(world_order.head(n_worlds)["label_world_idx"].tolist())
        part = candidate_worlds[candidate_worlds["label_world_idx"].isin(band_worlds)].copy()
        for (candidate, role, file_name), grp in part.groupby(["candidate", "role", "file"], sort=False):
            deltas = grp["delta_vs_e95"].to_numpy(dtype=np.float64)
            rows.append(
                {
                    "band": band_name,
                    "n_worlds": int(len(deltas)),
                    "candidate": candidate,
                    "role": role,
                    "file": file_name,
                    "delta_mean_vs_e95": float(deltas.mean()),
                    "delta_min_vs_e95": float(deltas.min()),
                    "delta_p25_vs_e95": float(np.quantile(deltas, 0.25)),
                    "delta_median_vs_e95": float(np.median(deltas)),
                    "delta_p75_vs_e95": float(np.quantile(deltas, 0.75)),
                    "delta_max_vs_e95": float(deltas.max()),
                    "negative_rate": float(np.mean(deltas < 0.0)),
                    "current_anchor_sum_abs_residual_max": float(grp["current_anchor_sum_abs_residual"].max()),
                    "current_anchor_max_abs_residual_max": float(grp["current_anchor_max_abs_residual"].max()),
                }
            )
    out = pd.DataFrame(rows)
    out = out.sort_values(["band", "delta_mean_vs_e95", "candidate"]).reset_index(drop=True)
    return out


def e176_cell_support(labels: np.ndarray, world_order: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not E180_CELLS.exists():
        return pd.DataFrame(), pd.DataFrame()
    cells = pd.read_csv(E180_CELLS)
    cells = cells[cells["pair"].eq("e176_vs_e95_pending")].copy()
    cells = cells.sort_values("swing_rank").head(16).reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    for band_name, n_worlds in BANDS:
        if n_worlds is None:
            band = world_order
        else:
            band = world_order.head(n_worlds)
        world_idx = band["label_world_idx"].to_numpy(dtype=int)
        y_band = labels[world_idx]
        for rec in cells.to_dict("records"):
            sub_idx = int(rec["sub_idx"])
            target_idx = int(rec["target_idx"])
            p_y1_world = float(y_band[:, sub_idx, target_idx].mean())
            support_label = int(rec["support_label"])
            world_support = p_y1_world if support_label == 1 else 1.0 - p_y1_world
            rows.append(
                {
                    "band": band_name,
                    "n_worlds": int(len(world_idx)),
                    "swing_rank": int(rec["swing_rank"]),
                    "sub_idx": sub_idx,
                    "target_idx": target_idx,
                    "target": rec["target"],
                    "hidden_block_id": rec.get("hidden_block_id"),
                    "subject_id": rec.get("subject_id"),
                    "support_label": support_label,
                    "swing": float(rec["swing"]),
                    "p_y1_visible_mean": float(rec["p_y1_visible_mean"]),
                    "visible_support": float(rec["support_probability_visible_mean"]),
                    "world_p_y1": p_y1_world,
                    "world_support": float(world_support),
                    "between_train_runs": bool(rec["between_train_runs"]),
                    "e72_active": bool(rec["e72_active"]),
                    "e101_active": bool(rec["e101_active"]),
                    "pos_bin": rec.get("pos_bin"),
                    "context_type": rec.get("context_type"),
                }
            )
        detail = pd.DataFrame([r for r in rows if r["band"] == band_name])
        for top_n in [4, 8, 16]:
            top = detail[detail["swing_rank"].le(top_n)].copy()
            weights = top["swing"].to_numpy(dtype=np.float64)
            summary_rows.append(
                {
                    "band": band_name,
                    "n_worlds": int(len(world_idx)),
                    "top_n": top_n,
                    "world_support_swing": float(np.average(top["world_support"], weights=weights)),
                    "visible_support_swing": float(np.average(top["visible_support"], weights=weights)),
                    "world_support_mean": float(top["world_support"].mean()),
                    "visible_support_mean": float(top["visible_support"].mean()),
                    "hard_world_support_rate": float((top["world_support"] >= 0.5).mean()),
                    "hard_visible_support_rate": float((top["visible_support"] >= 0.5).mean()),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def main() -> None:
    sample = load_sub(A2C8)
    known = known_public_table().copy().reset_index(drop=True)
    known = known[known["file"].map(lambda f: locate(str(f)) is not None)].reset_index(drop=True)
    known_probs = {str(file_name): load_prob(str(file_name), sample) for file_name in known["file"]}

    worlds, labels = load_worlds_and_labels(sample)
    world_fit, anchor_residuals = score_current_anchors(labels, known, known_probs)
    world_scores = worlds.merge(world_fit, on="label_world_idx", how="left", validate="one_to_one")
    world_scores = world_scores.sort_values(
        ["current_anchor_sum_abs_residual", "current_anchor_max_abs_residual", "label_world_idx"]
    ).reset_index(drop=True)
    world_scores["current_anchor_residual_rank"] = np.arange(1, len(world_scores) + 1, dtype=int)

    candidate_worlds = candidate_world_deltas(labels, sample, world_scores)
    candidate_bands = summarize_candidate_bands(candidate_worlds, world_scores)
    cell_detail, cell_summary = e176_cell_support(labels, world_scores)

    world_scores.to_csv(WORLD_OUT, index=False)
    anchor_residuals.to_csv(ANCHOR_OUT, index=False)
    candidate_worlds.to_csv(CANDIDATE_OUT, index=False)
    candidate_bands.to_csv(BAND_OUT, index=False)
    cell_detail.to_csv(CELL_OUT, index=False)
    cell_summary.to_csv(CELL_SUMMARY_OUT, index=False)

    top_world_cols = [
        "current_anchor_residual_rank",
        "label_world_idx",
        "objective",
        "source_role",
        "current_anchor_sum_abs_residual",
        "current_anchor_max_abs_residual",
        "anchor_energy_quantile",
        "mixmin_0c916",
    ]
    band_cols = [
        "band",
        "candidate",
        "delta_mean_vs_e95",
        "delta_min_vs_e95",
        "delta_max_vs_e95",
        "negative_rate",
        "current_anchor_sum_abs_residual_max",
    ]
    e176_band = candidate_bands[candidate_bands["candidate"].eq("e176")].copy()
    branch_band = candidate_bands[
        candidate_bands["candidate"].isin(["e176", "e174", "e172", "e154", "e144"])
        & candidate_bands["band"].isin(["best3_current_anchor_residual", "best5_current_anchor_residual", "best10_current_anchor_residual"])
    ].copy()
    cell_summary_view = cell_summary[
        cell_summary["band"].isin(["best3_current_anchor_residual", "best5_current_anchor_residual", "best10_current_anchor_residual", "all_binary_worlds"])
    ].copy()
    cell_top_view = cell_detail[
        cell_detail["band"].eq("best5_current_anchor_residual") & cell_detail["swing_rank"].le(8)
    ].copy()

    best5_e176 = e176_band[e176_band["band"].eq("best5_current_anchor_residual")].iloc[0]
    best10_e176 = e176_band[e176_band["band"].eq("best10_current_anchor_residual")].iloc[0]
    best5_e154 = candidate_bands[
        candidate_bands["candidate"].eq("e154") & candidate_bands["band"].eq("best5_current_anchor_residual")
    ].iloc[0]
    best5_e144 = candidate_bands[
        candidate_bands["candidate"].eq("e144") & candidate_bands["band"].eq("best5_current_anchor_residual")
    ].iloc[0]

    report = f"""# E181 E176 Binary-World Counterprior Audit

## Question

E180 says visible priors cannot certify frontier decisive cells. If the existing
binary hidden-label worlds are rescored against all current known public anchors,
do they support E176, or do they point to a different live branch?

No submission is created.

## Result In One Sentence

The current-anchor best binary worlds are a counterprior against E176: in the
best-5 residual worlds E176 averages `{float(best5_e176['delta_mean_vs_e95']):.9f}`
versus E95 with negative rate `{float(best5_e176['negative_rate']):.3f}`, while
E154 and E144 are negative in all best-5 worlds
(`{float(best5_e154['delta_mean_vs_e95']):.9f}` and
`{float(best5_e144['delta_mean_vs_e95']):.9f}`). This is not enough to demote
E176 by itself, but it cleanly splits the live world models.

## Current-Anchor Best Worlds

{md(world_scores, top_world_cols, n=10)}

## Candidate Bands Versus E95

{md(branch_band, band_cols, n=40)}

## E176 Band Summary

{md(e176_band, band_cols, n=10)}

## E176 Decisive-Cell Support Under Binary Worlds

{md(cell_summary_view, ['band', 'top_n', 'world_support_swing', 'visible_support_swing', 'hard_world_support_rate', 'hard_visible_support_rate'], n=20)}

## Best-5 E176 Top Cells

{md(cell_top_view, ['swing_rank', 'sub_idx', 'target', 'support_label', 'visible_support', 'world_p_y1', 'world_support', 'hidden_block_id', 'context_type', 'e72_active', 'e101_active'], n=12)}

## Interpretation

- E176 survives E180 because weak visible top-cell support is common among
  known winners. E181 adds the opposite stress: binary worlds that best fit the
  current public anchors do not like the E176/E174/E169 broad reopening family.
- This does not prove E176 will lose. The world pool is inherited from the
  older frontier-box construction and its current-anchor residuals are still
  larger than the E95 public edge. It is a counterprior, not a selector.
- The split is informative: visible/flank/body evidence points to E176 as the
  next broad hidden-tail sensor, while current-anchor binary worlds point toward
  the repaired E154/E144 branch.
- The next decisive local experiment should regenerate or stress a current-anchor
  binary-world pool with explicit objectives for E176, E154, and E144. If that
  fresh pool keeps E154/E144 one-sided while E176 remains mixed/adverse, the
  next submission priority should be reconsidered.

## Decision

No new submission. Keep E176 as an available public sensor only if the next slot
is meant to test the visible-body/Q2-underopen world. Do not call it the most
supported world across representations. The strongest unresolved conflict is now
E176 broad-body support versus E154/E144 binary-world counterprior.
"""
    REPORT_OUT.write_text(report)

    for path in [WORLD_OUT, ANCHOR_OUT, CANDIDATE_OUT, BAND_OUT, CELL_OUT, CELL_SUMMARY_OUT, REPORT_OUT]:
        print(path)


if __name__ == "__main__":
    main()
