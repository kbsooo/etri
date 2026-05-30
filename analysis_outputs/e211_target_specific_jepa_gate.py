#!/usr/bin/env python3
"""E211: split E209 JEPA translation by target.

E210 showed that target-dependency gating is useful for S4 but cuts away too
much of the locally validated Q3 JEPA body. This experiment keeps Q3 as a raw
E209 body axis while applying dependency gates only to S4.
"""

from __future__ import annotations

import hashlib
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
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import e209_feature_neighbor_jepa_materialization_stress as e209  # noqa: E402
import e210_jepa_target_dependency_gate as e210  # noqa: E402


STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

SUMMARY_OUT = OUT / "e211_target_specific_jepa_gate_summary.csv"
FRONTIER_OUT = OUT / "e211_target_specific_jepa_gate_frontier.csv"
GEOMETRY_OUT = OUT / "e211_target_specific_jepa_gate_geometry.csv"
TARGET_OUT = OUT / "e211_target_specific_jepa_gate_target_deltas.csv"
SELECTED_OUT = OUT / "e211_target_specific_jepa_gate_selected.csv"
REPORT_OUT = OUT / "e211_target_specific_jepa_gate_report.md"

COMBO = "q3_center_c010_s4_rank"
Q3 = TARGETS.index("Q3")
S4 = TARGETS.index("S4")
EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip_prob(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= 1.0e-15:
        return 0.0
    return float(np.dot(aa, bb) / den)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def target_group_share(move: np.ndarray, names: set[str]) -> float:
    mask = np.array([target in names for target in TARGETS], dtype=bool)
    den = float(np.abs(move).sum())
    if den <= 1.0e-15:
        return 0.0
    return float(np.abs(move[:, mask]).sum() / den)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def s4_multiplier(base: np.ndarray, cand: np.ndarray, cond: np.ndarray, mode: str) -> np.ndarray:
    step = logit(cand) - logit(base)
    active = np.abs(step[:, S4]) > EPS
    if mode == "raw":
        return active.astype(np.float64)
    if mode == "zero":
        return np.zeros(len(base), dtype=np.float64)
    return e210.gate_matrix(base, cand, cond, mode)[:, S4]


def apply_policy(
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    q3_scale: float,
    s4_mode: str,
    s4_scale: float,
) -> np.ndarray:
    step = logit(cand) - logit(base)
    mult = np.zeros_like(step)
    mult[:, Q3] = q3_scale * (np.abs(step[:, Q3]) > EPS)
    mult[:, S4] = s4_scale * s4_multiplier(base, cand, cond, s4_mode)
    return clip_prob(sigmoid(logit(base) + mult * step))


def keep_share(base: np.ndarray, cand: np.ndarray, out: np.ndarray) -> float:
    return float(np.abs(logit(out) - logit(base)).sum() / (np.abs(logit(cand) - logit(base)).sum() + EPS))


def target_rows(y: np.ndarray, base: np.ndarray, pred: np.ndarray, policy: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for j, target in enumerate(TARGETS):
        rows.append(
            {
                **policy,
                "target": target,
                "delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j]),
                "moved_abs_logit": float(np.abs(logit(pred[:, j]) - logit(base[:, j])).mean()),
            }
        )
    return rows


def geometry_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    stage2_oof: np.ndarray,
    ops: list[e209.Op],
    q3_scale: float,
    s4_mode: str,
    s4_scale: float,
) -> pd.DataFrame:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=291211):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_base = stage2_oof[tr_idx].copy()
        val_base = stage2_oof[val_idx].copy()
        ref_cand = ref_base.copy()
        val_cand = val_base.copy()
        for op in ops:
            val_cand = e209.apply_op_fit_predict(ref, val, ref_cand, val_cand, op)
            ref_cand = e209.apply_op_fit_predict(ref, ref, ref_cand, ref_cand, op)
        cond = e210.fit_predict_dependency(ref_base, y_all[tr_idx], val_base)
        gated = apply_policy(val_base, val_cand, cond, q3_scale, s4_mode, s4_scale)
        y = y_all[val_idx]
        rows.append(
            {
                "q3_scale": q3_scale,
                "s4_mode": s4_mode,
                "s4_scale": s4_scale,
                "fold": fold,
                "delta_mean": mean_loss(y, gated) - mean_loss(y, val_base),
                "ungated_delta_mean": mean_loss(y, val_cand) - mean_loss(y, val_base),
                "keep_abs_share": keep_share(val_base, val_cand, gated),
            }
        )
    return pd.DataFrame(rows)


def frontier_rows(
    sample: pd.DataFrame,
    stage2_sub: np.ndarray,
    ungated_sub: np.ndarray,
    stage2_oof: np.ndarray,
    y: np.ndarray,
    anchors: dict[str, np.ndarray],
    local_row: dict[str, Any],
) -> pd.DataFrame:
    priors = e162.prior_arrays(sample)
    z95 = logit(anchors["e95"])
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    axis_e154 = (logit(anchors["e154"]) - z95).reshape(-1)
    axis_e101 = (logit(anchors["e101"]) - z95).reshape(-1)
    axis_mixmin = (logit(anchors["mixmin"]) - z95).reshape(-1)
    delta_stage2 = logit(ungated_sub) - logit(stage2_sub)
    rows: list[dict[str, Any]] = []
    for anchor_name in ["e95", "e154", "mixmin"]:
        anchor = anchors[anchor_name]
        cond = e210.fit_predict_dependency(stage2_oof, y, anchor)
        for anchor_scale in [0.25, 0.50, 0.75, 1.00]:
            raw = clip_prob(sigmoid(logit(anchor) + anchor_scale * delta_stage2))
            pred = apply_policy(
                anchor,
                raw,
                cond,
                float(local_row["q3_scale"]),
                str(local_row["s4_mode"]),
                float(local_row["s4_scale"]),
            )
            move_vs_e95 = logit(pred) - z95
            move_vs_anchor = logit(pred) - logit(anchor)
            hard_e95 = e164.hard_breadth_metrics(pred, anchors["e95"], priors)
            hard_anchor = e164.hard_breadth_metrics(pred, anchor, priors)
            bad_energy, bad_resid = e165.span_energy(move_vs_e95, bad_basis)
            bad_cos = {f"cos_bad_{name}": cosine(move_vs_e95, bad_basis[i]) for i, name in enumerate(bad_names)}
            max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
            rec: dict[str, Any] = {
                **local_row,
                "anchor": anchor_name,
                "anchor_scale": anchor_scale,
                "frontier_keep_abs_share": keep_share(anchor, raw, pred),
                "mean_abs_logit_step_vs_anchor": float(np.abs(move_vs_anchor).mean()),
                "max_abs_logit_step_vs_anchor": float(np.abs(move_vs_anchor).max()),
                "q3s4_share_vs_e95": target_group_share(move_vs_e95, {"Q3", "S4"}),
                "q2s3_share_vs_e95": target_group_share(move_vs_e95, {"Q2", "S3"}),
                "bad_span_energy": bad_energy,
                "bad_span_residual": bad_resid,
                "max_bad_axis": max_bad_name,
                "max_bad_cos": bad_cos[f"cos_bad_{max_bad_name}"],
                "cos_e154_axis": cosine(move_vs_e95, axis_e154),
                "cos_e101_axis": cosine(move_vs_e95, axis_e101),
                "cos_mixmin_axis": cosine(move_vs_e95, axis_mixmin),
                **{f"vs_e95_{k}": v for k, v in hard_e95.items()},
                **{f"vs_anchor_{k}": v for k, v in hard_anchor.items()},
            }
            rec["e211_frontier_gate"] = bool(
                rec["delta"] < 0.0
                and rec["delta_vs_ungated"] <= 0.00055
                and rec["subject_half_delta"] < 0.0
                and rec["subject_half_win_rate"] >= 0.62
                and rec["geometry_delta"] <= 0.0
                and rec["geometry_win_rate"] >= 0.50
                and rec["geometry_vs_ungated_delta"] <= 0.00065
                and rec["anchor"] in {"e95", "e154"}
                and rec["vs_e95_expected_delta_focus_mean"] <= -2.0e-6
                and rec["vs_e95_top1_over_abs_expected"] <= 0.90
                and rec["bad_span_energy"] <= 0.55
                and rec["max_bad_cos"] <= 0.35
                and rec["mean_abs_logit_step_vs_anchor"] <= 0.012
                and rec["frontier_keep_abs_share"] >= 0.15
            )
            rec["survival_score"] = (
                -float(rec["delta"]) * 1.0
                - float(rec["geometry_delta"]) * 2.0
                - min(float(rec["vs_e95_expected_delta_focus_mean"]), 0.0) * 50.0
                + min(float(rec["vs_e95_cells_for_2e6_guard"]), 8) * 1.0e-4
                - max(float(rec["bad_span_energy"]) - 0.35, 0.0) * 1.0e-3
                - max(float(rec["max_bad_cos"]) - 0.20, 0.0) * 1.0e-3
                - max(float(rec["vs_e95_top1_over_abs_expected"]) - 0.50, 0.0) * 5.0e-4
                - max(float(rec["delta_vs_ungated"]) - 0.00035, 0.0) * 0.50
                - max(float(rec["geometry_vs_ungated_delta"]) - 0.00045, 0.0) * 0.50
            )
            rows.append(rec)
    return pd.DataFrame(rows)


def materialize(
    sample: pd.DataFrame,
    pred: np.ndarray,
    q3_scale: float,
    s4_mode: str,
    s4_scale: float,
    anchor: str,
    anchor_scale: float,
) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    q3_tag = str(q3_scale).replace(".", "p")
    s4_tag = str(s4_scale).replace(".", "p")
    anchor_tag = str(anchor_scale).replace(".", "p")
    name = f"submission_e211_jepa_q3raw{s4_mode}_q3s{q3_tag}_s4s{s4_tag}_{anchor}_a{anchor_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / name, index=False)
    return name


def write_report(summary: pd.DataFrame, frontier: pd.DataFrame, selected: pd.DataFrame, target_df: pd.DataFrame) -> None:
    summary_cols = [
        "q3_scale",
        "s4_mode",
        "s4_scale",
        "delta",
        "ungated_delta",
        "delta_vs_ungated",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
        "geometry_vs_ungated_delta",
        "keep_abs_share",
    ]
    frontier_cols = [
        "q3_scale",
        "s4_mode",
        "s4_scale",
        "anchor",
        "anchor_scale",
        "e211_frontier_gate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "frontier_keep_abs_share",
        "submission_file",
    ]
    target_cols = ["q3_scale", "s4_mode", "s4_scale", "target", "delta", "moved_abs_logit"]
    lines = [
        "# E211 Target-Specific JEPA Gate",
        "",
        "## Purpose",
        "",
        "Keep the E209 Q3 body while applying target-dependency gates only to S4.",
        "",
        "## Target Deltas",
        "",
        md_table(target_df.sort_values(["q3_scale", "s4_mode", "s4_scale", "target"]), target_cols, n=40),
        "",
        "## OOF / Subject / Geometry Summary",
        "",
        md_table(summary.sort_values(["delta", "geometry_delta"]), summary_cols, n=40),
        "",
        "## Frontier Stress",
        "",
        md_table(frontier.sort_values(["e211_frontier_gate", "survival_score"], ascending=[False, False]), frontier_cols, n=32),
        "",
        "## Selected Submissions",
        "",
        md_table(selected, frontier_cols, n=12),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No target-specific gate passed E211. E210's S4 signal is diagnostic only under this translation.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best target-specific candidate: `{best['submission_file']}`. It keeps Q3 scale `{best['q3_scale']}` and applies S4 `{best['s4_mode']}` at scale `{best['s4_scale']}` on `{best['anchor']}` anchor scale `{best['anchor_scale']}`."
        )
        lines.append("- E211 is the first attempt to preserve the E209 Q3 body while using dependency geometry only where E210 said it is locally coherent.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = e209.read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    groups = train_raw["subject_id"].astype(str).to_numpy()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    stage2_oof = clip_prob(np.load(OUT / STAGE2_OOF))
    stage2_sub = load_prob(STAGE2_FILE, sample)
    anchors = {
        "e95": load_prob(E95_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
    }
    ops = e209.combo_defs()[COMBO]
    ungated_oof = e209.apply_ops_oof(train_feat, stage2_oof, ops)
    ungated_sub = e209.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
    dep_oof = e210.oof_dependency(stage2_oof, y, groups)
    base_loss = mean_loss(y, stage2_oof)
    ungated_delta = mean_loss(y, ungated_oof) - base_loss

    q3_scales = [0.75, 1.00]
    s4_modes = ["raw", "toward", "closer", "soft_toward", "anti_toward_control", "zero"]
    s4_scales = [0.50, 0.75, 1.00]
    summary_rows: list[dict[str, Any]] = []
    target_parts: list[dict[str, Any]] = []
    geometry_parts: list[pd.DataFrame] = []
    frontier_parts: list[pd.DataFrame] = []

    for q3_scale in q3_scales:
        for s4_mode in s4_modes:
            for s4_scale in s4_scales:
                if s4_mode == "zero" and s4_scale != 1.00:
                    continue
                pred_oof = apply_policy(stage2_oof, ungated_oof, dep_oof, q3_scale, s4_mode, s4_scale)
                subj = e209.subject_half_summary(train_raw, y, stage2_oof, pred_oof, f"e211:{q3_scale}:{s4_mode}:{s4_scale}")
                geo = geometry_summary(train_raw, sub_raw, train_feat, stage2_oof, ops, q3_scale, s4_mode, s4_scale)
                geometry_parts.append(geo)
                policy = {"q3_scale": q3_scale, "s4_mode": s4_mode, "s4_scale": s4_scale}
                target_parts.extend(target_rows(y, stage2_oof, pred_oof, policy))
                local_row = {
                    **policy,
                    "delta": mean_loss(y, pred_oof) - base_loss,
                    "ungated_delta": ungated_delta,
                    "delta_vs_ungated": mean_loss(y, pred_oof) - mean_loss(y, ungated_oof),
                    "subject_half_delta": float(subj["delta_mean"].mean()),
                    "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
                    "geometry_delta": float(geo["delta_mean"].mean()),
                    "geometry_win_rate": float((geo["delta_mean"] < 0).mean()),
                    "ungated_geometry_delta": float(geo["ungated_delta_mean"].mean()),
                    "geometry_vs_ungated_delta": float(geo["delta_mean"].mean() - geo["ungated_delta_mean"].mean()),
                    "keep_abs_share": keep_share(stage2_oof, ungated_oof, pred_oof),
                }
                summary_rows.append(local_row)
                frontier_parts.append(frontier_rows(sample, stage2_sub, ungated_sub, stage2_oof, y, anchors, local_row))

    summary = pd.DataFrame(summary_rows)
    target_df = pd.DataFrame(target_parts)
    geometry_df = pd.concat(geometry_parts, ignore_index=True)
    frontier = pd.concat(frontier_parts, ignore_index=True)
    gated_frontier = frontier[frontier["e211_frontier_gate"]].sort_values(
        ["survival_score", "vs_e95_expected_delta_focus_mean"], ascending=[False, True]
    )
    # Keep the diagnostic pair: the best E154-confounded candidates and the
    # best clean E95 candidates. A pure top-4 ranking overselects E154 because
    # that anchor already carries the repaired-branch worldview.
    selected = gated_frontier.groupby("anchor", group_keys=False).head(2)
    selected = selected.sort_values(["survival_score", "vs_e95_expected_delta_focus_mean"], ascending=[False, True]).head(4).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        anchor = str(row.anchor)
        anchor_scale = float(row.anchor_scale)
        raw = clip_prob(sigmoid(logit(anchors[anchor]) + anchor_scale * (logit(ungated_sub) - logit(stage2_sub))))
        cond = e210.fit_predict_dependency(stage2_oof, y, anchors[anchor])
        pred = apply_policy(
            anchors[anchor],
            raw,
            cond,
            float(row.q3_scale),
            str(row.s4_mode),
            float(row.s4_scale),
        )
        files.append(materialize(sample, pred, float(row.q3_scale), str(row.s4_mode), float(row.s4_scale), anchor, anchor_scale))
    if not selected.empty:
        selected = selected.copy()
        selected["submission_file"] = files
        frontier = frontier.merge(
            selected[["q3_scale", "s4_mode", "s4_scale", "anchor", "anchor_scale", "submission_file"]],
            on=["q3_scale", "s4_mode", "s4_scale", "anchor", "anchor_scale"],
            how="left",
        )
    else:
        frontier["submission_file"] = ""
        selected["submission_file"] = ""

    summary.to_csv(SUMMARY_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)
    geometry_df.to_csv(GEOMETRY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, frontier, selected, target_df)

    print("[summary top]")
    print(summary.sort_values(["delta", "geometry_delta"]).head(24).round(9).to_string(index=False))
    print("\n[frontier top]")
    cols = [
        "q3_scale",
        "s4_mode",
        "s4_scale",
        "anchor",
        "anchor_scale",
        "e211_frontier_gate",
        "survival_score",
        "delta",
        "delta_vs_ungated",
        "geometry_delta",
        "geometry_vs_ungated_delta",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "frontier_keep_abs_share",
        "submission_file",
    ]
    print(frontier.sort_values(["e211_frontier_gate", "survival_score"], ascending=[False, False])[cols].head(24).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
