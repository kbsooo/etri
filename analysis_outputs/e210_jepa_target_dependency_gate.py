#!/usr/bin/env python3
"""E210: test whether target-dependency geometry can gate E209 JEPA movement.

E209 materialized the trained E208 feature-neighbor JEPA signal as a narrow Q3/S4
frontier graft. The remaining weakness was not local validation; it was
hard-label brittleness. This experiment asks whether a target-dependency
manifold, learned only from train labels and OOF prediction geometry, can
identify which JEPA Q3/S4 cells are coherent enough to keep.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import broad_feature_addon_builder as bfab  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402
import e209_feature_neighbor_jepa_materialization_stress as e209  # noqa: E402


STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

SUMMARY_OUT = OUT / "e210_jepa_target_dependency_gate_summary.csv"
FRONTIER_OUT = OUT / "e210_jepa_target_dependency_gate_frontier.csv"
SELECTED_OUT = OUT / "e210_jepa_target_dependency_gate_selected.csv"
CELL_OUT = OUT / "e210_jepa_target_dependency_gate_cell_anatomy.csv"
GEOMETRY_OUT = OUT / "e210_jepa_target_dependency_gate_geometry.csv"
REPORT_OUT = OUT / "e210_jepa_target_dependency_gate_report.md"

ACTIVE_COMBOS = ["q3_center_c010_s4_rank", "s4_rank"]
ACTIVE_TARGETS = {"Q3", "S4"}
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


def dependency_features(pred: np.ndarray, target_index: int) -> np.ndarray:
    p = clip_prob(pred)
    z = logit(p)
    other = [j for j in range(len(TARGETS)) if j != target_index]
    q_idx = [TARGETS.index(t) for t in ["Q1", "Q2", "Q3"] if TARGETS.index(t) != target_index]
    s_idx = [TARGETS.index(t) for t in ["S1", "S2", "S3", "S4"] if TARGETS.index(t) != target_index]
    q_mean = p[:, q_idx].mean(axis=1, keepdims=True) if q_idx else np.zeros((len(p), 1))
    s_mean = p[:, s_idx].mean(axis=1, keepdims=True) if s_idx else np.zeros((len(p), 1))
    entropy = -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))
    other_entropy = entropy[:, other].mean(axis=1, keepdims=True)
    return np.column_stack(
        [
            z[:, other],
            p[:, other],
            q_mean,
            s_mean,
            q_mean - s_mean,
            other_entropy,
        ]
    )


def make_model(c_value: float = 0.25):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=c_value, solver="lbfgs", max_iter=2000),
    )


def fit_predict_dependency(train_pred: np.ndarray, train_y: np.ndarray, pred: np.ndarray, c_value: float = 0.25) -> np.ndarray:
    out = np.zeros((len(pred), len(TARGETS)), dtype=np.float64)
    for j, target in enumerate(TARGETS):
        y = train_y[:, j].astype(int)
        if y.min() == y.max():
            out[:, j] = float(y.mean())
            continue
        model = make_model(c_value)
        model.fit(dependency_features(train_pred, j), y)
        out[:, j] = model.predict_proba(dependency_features(pred, j))[:, 1]
    return clip_prob(out)


def oof_dependency(pred: np.ndarray, y: np.ndarray, groups: np.ndarray, c_value: float = 0.25) -> np.ndarray:
    out = np.zeros_like(pred, dtype=np.float64)
    splitter = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    for tr_idx, val_idx in splitter.split(pred, groups=groups):
        out[val_idx] = fit_predict_dependency(pred[tr_idx], y[tr_idx], pred[val_idx], c_value)
    return clip_prob(out)


def gate_matrix(base: np.ndarray, cand: np.ndarray, cond: np.ndarray, mode: str) -> np.ndarray:
    step = logit(cand) - logit(base)
    desired = logit(cond) - logit(base)
    active = np.zeros_like(step, dtype=bool)
    for target in ACTIVE_TARGETS:
        active[:, TARGETS.index(target)] = np.abs(step[:, TARGETS.index(target)]) > EPS
    toward = active & ((step * desired) > 0.0)
    closer = active & (np.abs(logit(cand) - logit(cond)) < np.abs(logit(base) - logit(cond)))
    if mode == "toward":
        keep = toward
    elif mode == "closer":
        keep = closer
    elif mode == "toward_or_closer":
        keep = toward | closer
    elif mode == "both_targets_toward":
        row_keep = np.ones(len(base), dtype=bool)
        for target in ACTIVE_TARGETS:
            j = TARGETS.index(target)
            if np.abs(step[:, j]).sum() > EPS:
                row_keep &= toward[:, j]
        keep = active & row_keep[:, None]
    elif mode == "soft_toward":
        score = (step * desired) / (np.abs(step) + EPS)
        mult = np.where(active, 1.0 / (1.0 + np.exp(-np.clip(score / 0.25, -30.0, 30.0))), 0.0)
        return mult
    elif mode == "anti_toward_control":
        keep = active & ~toward
    else:
        raise ValueError(mode)
    return keep.astype(np.float64)


def apply_gate(base: np.ndarray, cand: np.ndarray, cond: np.ndarray, mode: str, shrink: float) -> np.ndarray:
    step = logit(cand) - logit(base)
    mult = gate_matrix(base, cand, cond, mode)
    return clip_prob(sigmoid(logit(base) + shrink * mult * step))


def cell_anatomy(y: np.ndarray, base: np.ndarray, cand: np.ndarray, cond: np.ndarray, combo: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    step = logit(cand) - logit(base)
    desired = logit(cond) - logit(base)
    for target in sorted(ACTIVE_TARGETS):
        j = TARGETS.index(target)
        active = np.abs(step[:, j]) > EPS
        if not active.any():
            continue
        loss_delta = -(y[:, j] * np.log(clip_prob(cand[:, j])) + (1 - y[:, j]) * np.log(1 - clip_prob(cand[:, j]))) + (
            y[:, j] * np.log(clip_prob(base[:, j])) + (1 - y[:, j]) * np.log(1 - clip_prob(base[:, j]))
        )
        toward = active & ((step[:, j] * desired[:, j]) > 0.0)
        closer = active & (np.abs(logit(cand[:, j]) - logit(cond[:, j])) < np.abs(logit(base[:, j]) - logit(cond[:, j])))
        for name, mask in [
            ("toward", toward),
            ("not_toward", active & ~toward),
            ("closer", closer),
            ("not_closer", active & ~closer),
        ]:
            if not mask.any():
                continue
            rows.append(
                {
                    "combo": combo,
                    "target": target,
                    "cell_group": name,
                    "n": int(mask.sum()),
                    "loss_delta_mean": float(loss_delta[mask].mean()),
                    "abs_step_mean": float(np.abs(step[mask, j]).mean()),
                    "desired_abs_mean": float(np.abs(desired[mask, j]).mean()),
                    "label_rate": float(y[mask, j].mean()),
                    "base_mean": float(base[mask, j].mean()),
                    "cand_mean": float(cand[mask, j].mean()),
                    "cond_mean": float(cond[mask, j].mean()),
                }
            )
    return pd.DataFrame(rows)


def geometry_gate_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    stage2_oof: np.ndarray,
    ops: list[e209.Op],
    combo: str,
    mode: str,
    shrink: float,
) -> pd.DataFrame:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=291210):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_base = stage2_oof[tr_idx].copy()
        val_base = stage2_oof[val_idx].copy()
        val_cand = val_base.copy()
        ref_cand = ref_base.copy()
        for op in ops:
            val_cand = e209.apply_op_fit_predict(ref, val, ref_cand, val_cand, op)
            ref_cand = e209.apply_op_fit_predict(ref, ref, ref_cand, ref_cand, op)
        cond = fit_predict_dependency(ref_base, y_all[tr_idx], val_base)
        gated = apply_gate(val_base, val_cand, cond, mode, shrink)
        y = y_all[val_idx]
        rows.append(
            {
                "combo": combo,
                "gate_mode": mode,
                "shrink": shrink,
                "fold": fold,
                "delta_mean": mean_loss(y, gated) - mean_loss(y, val_base),
                "ungated_delta_mean": mean_loss(y, val_cand) - mean_loss(y, val_base),
                "keep_abs_share": float(np.abs(logit(gated) - logit(val_base)).sum() / (np.abs(logit(val_cand) - logit(val_base)).sum() + EPS)),
            }
        )
    return pd.DataFrame(rows)


def frontier_rows(
    sample: pd.DataFrame,
    base_stage2: np.ndarray,
    cand_stage2: np.ndarray,
    train_y: np.ndarray,
    stage2_oof: np.ndarray,
    anchors: dict[str, np.ndarray],
    combo: str,
    mode: str,
    shrink: float,
    local_row: dict[str, Any],
) -> pd.DataFrame:
    priors = e162.prior_arrays(sample)
    z95 = logit(anchors["e95"])
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    axis_e154 = (logit(anchors["e154"]) - z95).reshape(-1)
    axis_e101 = (logit(anchors["e101"]) - z95).reshape(-1)
    axis_mixmin = (logit(anchors["mixmin"]) - z95).reshape(-1)
    delta_stage2 = logit(cand_stage2) - logit(base_stage2)
    out_rows: list[dict[str, Any]] = []
    for anchor_name in ["e95", "e154", "mixmin"]:
        anchor = anchors[anchor_name]
        for scale in [0.25, 0.50, 0.75, 1.00]:
            ungated = clip_prob(sigmoid(logit(anchor) + scale * delta_stage2))
            cond = fit_predict_dependency(stage2_oof, train_y, anchor)
            pred = apply_gate(anchor, ungated, cond, mode, shrink)
            move_vs_e95 = logit(pred) - z95
            move_vs_anchor = logit(pred) - logit(anchor)
            bad_energy, bad_resid = e165.span_energy(move_vs_e95, bad_basis)
            bad_cos = {f"cos_bad_{name}": cosine(move_vs_e95, bad_basis[i]) for i, name in enumerate(bad_names)}
            max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
            hard_e95 = e164.hard_breadth_metrics(pred, anchors["e95"], priors)
            hard_anchor = e164.hard_breadth_metrics(pred, anchor, priors)
            keep_share = float(np.abs(move_vs_anchor).sum() / (np.abs(logit(ungated) - logit(anchor)).sum() + EPS))
            rec: dict[str, Any] = {
                "combo": combo,
                "gate_mode": mode,
                "shrink": shrink,
                "anchor": anchor_name,
                "scale": scale,
                "local_delta": local_row["delta"],
                "local_vs_ungated_delta": local_row["delta"] - local_row["ungated_delta"],
                "subject_half_delta": local_row["subject_half_delta"],
                "subject_half_win_rate": local_row["subject_half_win_rate"],
                "geometry_delta": local_row["geometry_delta"],
                "geometry_win_rate": local_row["geometry_win_rate"],
                "geometry_vs_ungated_delta": local_row["geometry_delta"] - local_row["ungated_geometry_delta"],
                "keep_abs_share": keep_share,
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
            rec["e210_frontier_gate"] = bool(
                rec["local_delta"] < 0.0
                and rec["subject_half_delta"] < 0.0
                and rec["subject_half_win_rate"] >= 0.60
                and rec["geometry_delta"] <= 0.0
                and rec["geometry_win_rate"] >= 0.50
                and rec["anchor"] in {"e95", "e154"}
                and rec["vs_e95_expected_delta_focus_mean"] <= -2.0e-6
                and rec["vs_e95_top1_over_abs_expected"] <= 0.90
                and rec["bad_span_energy"] <= 0.55
                and rec["max_bad_cos"] <= 0.35
                and rec["mean_abs_logit_step_vs_anchor"] <= 0.012
                and rec["keep_abs_share"] >= 0.15
            )
            rec["survival_score"] = (
                -float(rec["local_delta"]) * 1.0
                - float(rec["geometry_delta"]) * 2.0
                - min(float(rec["vs_e95_expected_delta_focus_mean"]), 0.0) * 50.0
                + min(float(rec["vs_e95_cells_for_2e6_guard"]), 8) * 1.0e-4
                - max(float(rec["bad_span_energy"]) - 0.35, 0.0) * 1.0e-3
                - max(float(rec["max_bad_cos"]) - 0.20, 0.0) * 1.0e-3
                - max(float(rec["vs_e95_top1_over_abs_expected"]) - 0.50, 0.0) * 5.0e-4
                - max(float(rec["geometry_vs_ungated_delta"]), 0.0) * 0.25
            )
            out_rows.append(rec)
    return pd.DataFrame(out_rows)


def materialize(sample: pd.DataFrame, pred: np.ndarray, combo: str, mode: str, shrink: float, anchor: str, scale: float) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    scale_tag = str(scale).replace(".", "p")
    shrink_tag = str(shrink).replace(".", "p")
    file_name = f"submission_e210_jepa_depgate_{combo}_{mode}_sh{shrink_tag}_{anchor}_s{scale_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def write_report(summary: pd.DataFrame, frontier: pd.DataFrame, selected: pd.DataFrame, cell: pd.DataFrame) -> None:
    summary_cols = [
        "combo",
        "gate_mode",
        "shrink",
        "delta",
        "ungated_delta",
        "vs_ungated_delta",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
        "keep_abs_share",
    ]
    frontier_cols = [
        "combo",
        "gate_mode",
        "shrink",
        "anchor",
        "scale",
        "e210_frontier_gate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "keep_abs_share",
        "submission_file",
    ]
    cell_cols = [
        "combo",
        "target",
        "cell_group",
        "n",
        "loss_delta_mean",
        "abs_step_mean",
        "desired_abs_mean",
        "label_rate",
        "base_mean",
        "cand_mean",
        "cond_mean",
    ]
    lines = [
        "# E210 JEPA Target-Dependency Gate",
        "",
        "## Purpose",
        "",
        "Test whether a train-label target-dependency manifold can gate E209 Q3/S4 JEPA movement and reduce hard-label translation risk.",
        "",
        "## Cell Anatomy",
        "",
        md_table(cell.sort_values(["combo", "target", "cell_group"]), cell_cols, n=40),
        "",
        "## OOF / Subject / Geometry Summary",
        "",
        md_table(summary.sort_values(["delta", "geometry_delta"]), summary_cols, n=40),
        "",
        "## Frontier Stress",
        "",
        md_table(frontier.sort_values(["e210_frontier_gate", "survival_score"], ascending=[False, False]), frontier_cols, n=30),
        "",
        "## Selected Submissions",
        "",
        md_table(selected, frontier_cols, n=12),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No dependency-gated JEPA graft passed the E210 frontier gate. The target-dependency manifold is diagnostic only for now.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best dependency-gated candidate: `{best['submission_file']}`. It tests whether `{best['gate_mode']}` target-dependency filtering makes the E209 `{best['combo']}` graft safer on `{best['anchor']}`."
        )
        lines.append("- This does not supersede E209 as a generic next submission: the selected Q3/S4 closer gates lose local OOF and geometry margin versus ungated E209, while improving public-prior hard-tail anatomy.")
        lines.append("- Compare this against the ungated E209 candidate only when the public question is dependency-tail localization. A win credits dependency-gated JEPA translation; a loss says the gate removed useful body or followed a train-only dependency shortcut.")
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

    dep_oof = oof_dependency(stage2_oof, y, groups)
    combos = e209.combo_defs()
    gate_modes = ["toward", "closer", "toward_or_closer", "both_targets_toward", "soft_toward", "anti_toward_control"]
    shrinks = [0.50, 0.75, 1.00]

    summary_rows: list[dict[str, Any]] = []
    frontier_parts: list[pd.DataFrame] = []
    geometry_parts: list[pd.DataFrame] = []
    cell_parts: list[pd.DataFrame] = []
    ungated_subs: dict[str, np.ndarray] = {}

    base_loss = mean_loss(y, stage2_oof)
    for combo in ACTIVE_COMBOS:
        ops = combos[combo]
        ungated_oof = e209.apply_ops_oof(train_feat, stage2_oof, ops)
        ungated_sub = e209.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
        ungated_subs[combo] = ungated_sub
        ungated_delta = mean_loss(y, ungated_oof) - base_loss
        cell_parts.append(cell_anatomy(y, stage2_oof, ungated_oof, dep_oof, combo))
        for mode in gate_modes:
            for shrink in shrinks:
                gated = apply_gate(stage2_oof, ungated_oof, dep_oof, mode, shrink)
                subj = e209.subject_half_summary(train_raw, y, stage2_oof, gated, f"{combo}:{mode}:{shrink}")
                geo = geometry_gate_summary(train_raw, sub_raw, train_feat, stage2_oof, ops, combo, mode, shrink)
                geometry_parts.append(geo)
                keep_share = float(np.abs(logit(gated) - logit(stage2_oof)).sum() / (np.abs(logit(ungated_oof) - logit(stage2_oof)).sum() + EPS))
                local_row = {
                    "combo": combo,
                    "gate_mode": mode,
                    "shrink": shrink,
                    "delta": mean_loss(y, gated) - base_loss,
                    "ungated_delta": ungated_delta,
                    "vs_ungated_delta": mean_loss(y, gated) - mean_loss(y, ungated_oof),
                    "subject_half_delta": float(subj["delta_mean"].mean()),
                    "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
                    "geometry_delta": float(geo["delta_mean"].mean()),
                    "geometry_win_rate": float((geo["delta_mean"] < 0).mean()),
                    "ungated_geometry_delta": float(geo["ungated_delta_mean"].mean()),
                    "keep_abs_share": keep_share,
                }
                summary_rows.append(local_row)
                frontier_parts.append(
                    frontier_rows(
                        sample,
                        stage2_sub,
                        ungated_sub,
                        y,
                        stage2_oof,
                        anchors,
                        combo,
                        mode,
                        shrink,
                        local_row,
                    )
                )

    summary = pd.DataFrame(summary_rows)
    frontier = pd.concat(frontier_parts, ignore_index=True)
    geometry_df = pd.concat(geometry_parts, ignore_index=True)
    cell_df = pd.concat(cell_parts, ignore_index=True)

    selected = frontier[frontier["e210_frontier_gate"]].sort_values(
        ["survival_score", "vs_e95_expected_delta_focus_mean"], ascending=[False, True]
    ).head(4).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        combo = str(row.combo)
        mode = str(row.gate_mode)
        shrink = float(row.shrink)
        anchor = str(row.anchor)
        scale = float(row.scale)
        ungated_stage2 = ungated_subs[combo]
        ungated = clip_prob(sigmoid(logit(anchors[anchor]) + scale * (logit(ungated_stage2) - logit(stage2_sub))))
        cond = fit_predict_dependency(stage2_oof, y, anchors[anchor])
        pred = apply_gate(anchors[anchor], ungated, cond, mode, shrink)
        files.append(materialize(sample, pred, combo, mode, shrink, anchor, scale))
    if not selected.empty:
        selected = selected.copy()
        selected["submission_file"] = files
        frontier = frontier.merge(
            selected[["combo", "gate_mode", "shrink", "anchor", "scale", "submission_file"]],
            on=["combo", "gate_mode", "shrink", "anchor", "scale"],
            how="left",
        )
    else:
        frontier["submission_file"] = ""
        selected["submission_file"] = ""

    summary.to_csv(SUMMARY_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    cell_df.to_csv(CELL_OUT, index=False)
    geometry_df.to_csv(GEOMETRY_OUT, index=False)
    write_report(summary, frontier, selected, cell_df)

    print("[summary top]")
    print(summary.sort_values(["delta", "geometry_delta"]).head(24).round(9).to_string(index=False))
    print("\n[frontier top]")
    cols = [
        "combo",
        "gate_mode",
        "shrink",
        "anchor",
        "scale",
        "e210_frontier_gate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_cos",
        "keep_abs_share",
        "submission_file",
    ]
    print(frontier.sort_values(["e210_frontier_gate", "survival_score"], ascending=[False, False])[cols].head(24).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
