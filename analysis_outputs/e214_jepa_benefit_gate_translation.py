#!/usr/bin/env python3
"""E214: learn a public-free benefit gate for the E208/E211 JEPA step.

E213 says the live Q3/S4 JEPA axes are unlikely to be random coordinates.
The next failure mode is translation: a real latent direction may still be
harmful when moved uniformly into probability space.

This experiment uses the OOF cell-wise loss improvement of the raw E209 JEPA
step as a training signal for a small subject-CV benefit gate. The gate is then
stress-tested under subject halves, geometry folds, and frontier graft audits.
It is deliberately narrow: only the already-certified Q3/S4 JEPA step is gated.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import e209_feature_neighbor_jepa_materialization_stress as e209  # noqa: E402
import e210_jepa_target_dependency_gate as e210  # noqa: E402
import e211_target_specific_jepa_gate as e211  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"

COMBO = "q3_center_c010_s4_rank"
ACTIVE_TARGETS = ["Q3", "S4"]
EPS = 1.0e-12
SEED = 291214

SUMMARY_OUT = OUT / "e214_jepa_benefit_gate_translation_summary.csv"
TARGET_OUT = OUT / "e214_jepa_benefit_gate_translation_target_summary.csv"
GATE_AUDIT_OUT = OUT / "e214_jepa_benefit_gate_translation_gate_audit.csv"
GEOMETRY_OUT = OUT / "e214_jepa_benefit_gate_translation_geometry_summary.csv"
FRONTIER_OUT = OUT / "e214_jepa_benefit_gate_translation_frontier_summary.csv"
SELECTED_OUT = OUT / "e214_jepa_benefit_gate_translation_selected_summary.csv"
REPORT_OUT = OUT / "e214_jepa_benefit_gate_translation_report.md"


@dataclass(frozen=True)
class Policy:
    policy_id: str
    q3_mode: str
    s4_mode: str
    q3_scale: float = 1.0
    s4_scale: float = 1.0


POLICIES = [
    Policy("baseline_raw_raw", "raw", "raw"),
    Policy("baseline_q3raw_s4toward", "raw", "toward_binary"),
    Policy("baseline_q3raw_s4closer", "raw", "closer_binary"),
    Policy("q3raw_s4benefit_prob", "raw", "prob"),
    Policy("q3raw_s4benefit_rank", "raw", "rank"),
    Policy("q3raw_s4benefit_margin", "raw", "margin"),
    Policy("q3raw_s4benefit_toward", "raw", "toward_prob"),
    Policy("q3raw_s4benefit_toward_rank", "raw", "toward_rank"),
    Policy("q3raw_s4benefit_closer", "raw", "closer_prob"),
    Policy("q3raw_s4benefit_closer_rank", "raw", "closer_rank"),
    Policy("q3benefit_prob_s4benefit_prob", "prob", "prob"),
    Policy("q3benefit_rank_s4benefit_rank", "rank", "rank"),
    Policy("q3benefit_margin_s4benefit_margin", "margin", "margin"),
    Policy("q3benefit_prob_s4benefit_toward", "prob", "toward_prob"),
    Policy("q3benefit_rank_s4benefit_toward_rank", "rank", "toward_rank"),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip_prob(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def cell_loss(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = y.astype(float)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


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


def entropy(p: np.ndarray) -> np.ndarray:
    pp = clip_prob(p)
    return -(pp * np.log(pp) + (1.0 - pp) * np.log(1.0 - pp))


def rank01(values: np.ndarray) -> np.ndarray:
    vals = np.asarray(values, dtype=np.float64)
    if len(vals) <= 1:
        return np.ones_like(vals)
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(len(vals), dtype=np.float64)
    ranks[order] = np.arange(len(vals), dtype=np.float64)
    return ranks / max(len(vals) - 1, 1)


def target_group_share(move: np.ndarray, names: set[str]) -> float:
    mask = np.array([target in names for target in TARGETS], dtype=bool)
    den = float(np.abs(move).sum())
    if den <= 1.0e-15:
        return 0.0
    return float(np.abs(move[:, mask]).sum() / den)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in frame.columns if c in cols]]
    return e138.md_table(view.head(n), floatfmt)


def axis_spec(target: str) -> tuple[str, str]:
    if target == "Q3":
        return "e208_resid_self_pc10", "subject_center"
    if target == "S4":
        return "e208_pred_pc14", "subject_rank"
    raise ValueError(target)


def make_gate_model(c_value: float = 0.20):
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=c_value, solver="lbfgs", max_iter=2000, class_weight="balanced"),
    )


def benefit_label(y: np.ndarray, base: np.ndarray, cand: np.ndarray) -> np.ndarray:
    return (cell_loss(y, cand) < cell_loss(y, base)).astype(int)


def gate_feature_matrix(
    ref_rows: pd.DataFrame,
    rows: pd.DataFrame,
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    target: str,
) -> np.ndarray:
    j = TARGETS.index(target)
    axis_feature, axis_mode = axis_spec(target)
    _, axis_z = broad.transform_pair(ref_rows, rows, axis_feature, axis_mode)
    base_p = clip_prob(base[:, j])
    cand_p = clip_prob(cand[:, j])
    cond_p = clip_prob(cond[:, j])
    base_z = logit(base_p)
    cand_z = logit(cand_p)
    cond_z = logit(cond_p)
    step = cand_z - base_z
    desired = cond_z - base_z
    toward = (step * desired > 0.0).astype(float)
    closer = (np.abs(cand_z - cond_z) < np.abs(base_z - cond_z)).astype(float)
    return np.column_stack(
        [
            base_z,
            cand_z,
            cond_z,
            step,
            np.abs(step),
            desired,
            np.abs(desired),
            step * desired,
            toward,
            closer,
            base_p,
            cand_p,
            cond_p,
            entropy(base_p),
            entropy(cand_p),
            np.abs(base_p - 0.5),
            axis_z,
            np.abs(axis_z),
            axis_z * np.sign(step),
        ]
    )


def fit_predict_gate(
    ref_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    ref_base: np.ndarray,
    pred_base: np.ndarray,
    ref_cand: np.ndarray,
    pred_cand: np.ndarray,
    ref_cond: np.ndarray,
    pred_cond: np.ndarray,
    ref_y: np.ndarray,
    target: str,
) -> np.ndarray:
    j = TARGETS.index(target)
    labels = benefit_label(ref_y[:, j], ref_base[:, j], ref_cand[:, j])
    if labels.min() == labels.max():
        return np.full(len(pred_rows), float(labels.mean()), dtype=np.float64)
    x_ref = gate_feature_matrix(ref_rows, ref_rows, ref_base, ref_cand, ref_cond, target)
    x_pred = gate_feature_matrix(ref_rows, pred_rows, pred_base, pred_cand, pred_cond, target)
    model = make_gate_model()
    model.fit(x_ref, labels)
    return clip_prob(model.predict_proba(x_pred)[:, 1])


def oof_gate_probs(
    rows: pd.DataFrame,
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> dict[str, np.ndarray]:
    out = {target: np.zeros(len(rows), dtype=np.float64) for target in ACTIVE_TARGETS}
    splitter = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    for tr_idx, val_idx in splitter.split(rows, groups=groups):
        ref_rows = rows.iloc[tr_idx].reset_index(drop=True)
        val_rows = rows.iloc[val_idx].reset_index(drop=True)
        for target in ACTIVE_TARGETS:
            out[target][val_idx] = fit_predict_gate(
                ref_rows,
                val_rows,
                base[tr_idx],
                base[val_idx],
                cand[tr_idx],
                cand[val_idx],
                cond[tr_idx],
                cond[val_idx],
                y[tr_idx],
                target,
            )
    return out


def gate_audit(
    rows: pd.DataFrame,
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    y: np.ndarray,
    gate_probs: dict[str, np.ndarray],
) -> pd.DataFrame:
    parts: list[dict[str, Any]] = []
    for target in ACTIVE_TARGETS:
        j = TARGETS.index(target)
        labels = benefit_label(y[:, j], base[:, j], cand[:, j])
        probs = gate_probs[target]
        auc = np.nan
        if labels.min() != labels.max():
            auc = float(roc_auc_score(labels, probs))
        step = logit(cand[:, j]) - logit(base[:, j])
        desired = logit(cond[:, j]) - logit(base[:, j])
        parts.append(
            {
                "target": target,
                "benefit_rate": float(labels.mean()),
                "gate_auc": auc,
                "gate_prob_mean": float(probs.mean()),
                "gate_prob_benefit_mean": float(probs[labels == 1].mean()) if (labels == 1).any() else np.nan,
                "gate_prob_harm_mean": float(probs[labels == 0].mean()) if (labels == 0).any() else np.nan,
                "margin_keep_rate": float((probs > 0.5).mean()),
                "hard60_keep_rate": float((probs >= 0.6).mean()),
                "toward_benefit_rate": float(labels[(step * desired) > 0.0].mean()) if ((step * desired) > 0.0).any() else np.nan,
                "closer_benefit_rate": float(labels[np.abs(logit(cand[:, j]) - logit(cond[:, j])) < np.abs(logit(base[:, j]) - logit(cond[:, j]))].mean()),
                "rows": int(len(rows)),
            }
        )
    return pd.DataFrame(parts)


def multiplier_for_mode(
    mode: str,
    target: str,
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    gate_prob: np.ndarray,
) -> np.ndarray:
    j = TARGETS.index(target)
    step = logit(cand[:, j]) - logit(base[:, j])
    desired = logit(cond[:, j]) - logit(base[:, j])
    active = np.abs(step) > EPS
    toward = active & ((step * desired) > 0.0)
    closer = active & (np.abs(logit(cand[:, j]) - logit(cond[:, j])) < np.abs(logit(base[:, j]) - logit(cond[:, j])))
    if mode == "raw":
        return active.astype(np.float64)
    if mode == "zero":
        return np.zeros(len(base), dtype=np.float64)
    if mode == "toward_binary":
        return toward.astype(np.float64)
    if mode == "closer_binary":
        return closer.astype(np.float64)
    if mode == "prob":
        return np.where(active, gate_prob, 0.0)
    if mode == "rank":
        return np.where(active, rank01(gate_prob), 0.0)
    if mode == "margin":
        return np.where(active, np.clip((gate_prob - 0.5) / 0.25, 0.0, 1.0), 0.0)
    if mode == "toward_prob":
        return np.where(toward, gate_prob, 0.0)
    if mode == "closer_prob":
        return np.where(closer, gate_prob, 0.0)
    if mode == "toward_rank":
        return np.where(toward, rank01(gate_prob), 0.0)
    if mode == "closer_rank":
        return np.where(closer, rank01(gate_prob), 0.0)
    raise ValueError(mode)


def apply_policy(
    base: np.ndarray,
    cand: np.ndarray,
    cond: np.ndarray,
    gate_probs: dict[str, np.ndarray],
    policy: Policy,
) -> np.ndarray:
    out = base.copy()
    step = logit(cand) - logit(base)
    modes = {"Q3": policy.q3_mode, "S4": policy.s4_mode}
    scales = {"Q3": policy.q3_scale, "S4": policy.s4_scale}
    mult = np.zeros_like(step)
    for target in ACTIVE_TARGETS:
        j = TARGETS.index(target)
        mult[:, j] = scales[target] * multiplier_for_mode(modes[target], target, base, cand, cond, gate_probs[target])
    out = clip_prob(sigmoid(logit(base) + mult * step))
    return out


def keep_share(base: np.ndarray, cand: np.ndarray, out: np.ndarray) -> float:
    return float(np.abs(logit(out) - logit(base)).sum() / (np.abs(logit(cand) - logit(base)).sum() + EPS))


def target_rows(y: np.ndarray, base: np.ndarray, pred: np.ndarray, policy: Policy) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for j, target in enumerate(TARGETS):
        rows.append(
            {
                "policy_id": policy.policy_id,
                "q3_mode": policy.q3_mode,
                "s4_mode": policy.s4_mode,
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
    policies: list[Policy],
) -> pd.DataFrame:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, Any]] = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=SEED):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_base = stage2_oof[tr_idx].copy()
        val_base = stage2_oof[val_idx].copy()
        ref_cand = ref_base.copy()
        val_cand = val_base.copy()
        for op in ops:
            val_cand = e209.apply_op_fit_predict(ref, val, ref_cand, val_cand, op)
            ref_cand = e209.apply_op_fit_predict(ref, ref, ref_cand, ref_cand, op)
        ref_cond = e210.fit_predict_dependency(ref_base, y_all[tr_idx], ref_base)
        val_cond = e210.fit_predict_dependency(ref_base, y_all[tr_idx], val_base)
        gate_probs = {
            target: fit_predict_gate(ref, val, ref_base, val_base, ref_cand, val_cand, ref_cond, val_cond, y_all[tr_idx], target)
            for target in ACTIVE_TARGETS
        }
        y = y_all[val_idx]
        for policy in policies:
            pred = apply_policy(val_base, val_cand, val_cond, gate_probs, policy)
            rows.append(
                {
                    "policy_id": policy.policy_id,
                    "q3_mode": policy.q3_mode,
                    "s4_mode": policy.s4_mode,
                    "fold": fold,
                    "delta_mean": mean_loss(y, pred) - mean_loss(y, val_base),
                    "ungated_delta_mean": mean_loss(y, val_cand) - mean_loss(y, val_base),
                    "keep_abs_share": keep_share(val_base, val_cand, pred),
                }
            )
    return pd.DataFrame(rows)


def fit_full_gate_for_rows(
    train_feat: pd.DataFrame,
    rows: pd.DataFrame,
    train_base: np.ndarray,
    row_base: np.ndarray,
    train_cand: np.ndarray,
    row_cand: np.ndarray,
    train_cond: np.ndarray,
    row_cond: np.ndarray,
    y: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        target: fit_predict_gate(train_feat, rows, train_base, row_base, train_cand, row_cand, train_cond, row_cond, y, target)
        for target in ACTIVE_TARGETS
    }


def frontier_rows(
    sample: pd.DataFrame,
    stage2_sub: np.ndarray,
    ungated_sub: np.ndarray,
    stage2_oof: np.ndarray,
    ungated_oof: np.ndarray,
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    y: np.ndarray,
    anchors: dict[str, np.ndarray],
    local_rows: pd.DataFrame,
) -> pd.DataFrame:
    priors = e162.prior_arrays(sample)
    z95 = logit(anchors["e95"])
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    axis_e154 = (logit(anchors["e154"]) - z95).reshape(-1)
    axis_e101 = (logit(anchors["e101"]) - z95).reshape(-1)
    axis_mixmin = (logit(anchors["mixmin"]) - z95).reshape(-1)
    delta_stage2 = logit(ungated_sub) - logit(stage2_sub)
    dep_oof = e210.oof_dependency(stage2_oof, y, train_feat["subject_id"].astype(str).to_numpy())
    rows: list[dict[str, Any]] = []
    local_by_policy = {str(r.policy_id): r._asdict() for r in local_rows.itertuples(index=False)}
    for policy in POLICIES:
        local_row = local_by_policy[policy.policy_id]
        for anchor_name in ["e95", "e154"]:
            anchor = anchors[anchor_name]
            cond = e210.fit_predict_dependency(stage2_oof, y, anchor)
            gate_anchor_cache: dict[float, dict[str, np.ndarray]] = {}
            for anchor_scale in [0.25, 0.50, 0.75, 1.00]:
                raw = clip_prob(sigmoid(logit(anchor) + anchor_scale * delta_stage2))
                if anchor_scale not in gate_anchor_cache:
                    gate_anchor_cache[anchor_scale] = fit_full_gate_for_rows(
                        train_feat,
                        sub_feat,
                        stage2_oof,
                        anchor,
                        ungated_oof,
                        raw,
                        dep_oof,
                        cond,
                        y,
                    )
                pred = apply_policy(anchor, raw, cond, gate_anchor_cache[anchor_scale], policy)
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
                rec["is_benefit_policy"] = not policy.policy_id.startswith("baseline")
                rec["e214_frontier_gate"] = bool(
                    rec["is_benefit_policy"]
                    and rec["delta"] <= -0.00095
                    and rec["subject_half_delta"] < 0.0
                    and rec["subject_half_win_rate"] >= 0.88
                    and rec["geometry_delta"] <= -0.00045
                    and rec["geometry_win_rate"] >= 0.75
                    and rec["anchor"] in {"e95", "e154"}
                    and rec["vs_e95_expected_delta_focus_mean"] <= -2.0e-6
                    and rec["vs_e95_top1_over_abs_expected"] <= 0.90
                    and rec["bad_span_energy"] <= 0.58
                    and rec["max_bad_cos"] <= 0.38
                    and rec["mean_abs_logit_step_vs_anchor"] <= 0.012
                    and rec["frontier_keep_abs_share"] >= 0.10
                )
                rec["survival_score"] = (
                    -float(rec["delta"]) * 1.0
                    - float(rec["geometry_delta"]) * 2.0
                    - min(float(rec["vs_e95_expected_delta_focus_mean"]), 0.0) * 45.0
                    + min(float(rec["vs_e95_cells_for_2e6_guard"]), 8) * 1.0e-4
                    - max(float(rec["bad_span_energy"]) - 0.35, 0.0) * 1.0e-3
                    - max(float(rec["max_bad_cos"]) - 0.20, 0.0) * 1.0e-3
                    - max(float(rec["vs_e95_top1_over_abs_expected"]) - 0.50, 0.0) * 5.0e-4
                    - max(0.00060 - abs(float(rec["frontier_keep_abs_share"])) * 1.0e-3, 0.0)
                )
                rows.append(rec)
    return pd.DataFrame(rows)


def materialize(
    sample: pd.DataFrame,
    pred: np.ndarray,
    policy: Policy,
    anchor: str,
    anchor_scale: float,
) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    anchor_tag = str(anchor_scale).replace(".", "p")
    name = f"submission_e214_jepa_benefitgate_{policy.policy_id}_{anchor}_a{anchor_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / name, index=False)
    return name


def write_report(
    gate_audit_df: pd.DataFrame,
    summary: pd.DataFrame,
    target_df: pd.DataFrame,
    geometry_agg: pd.DataFrame,
    frontier: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:
    summary_cols = [
        "policy_id",
        "q3_mode",
        "s4_mode",
        "delta",
        "delta_vs_raw",
        "delta_vs_e211_toward",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
        "geometry_vs_raw",
        "keep_abs_share",
    ]
    frontier_cols = [
        "policy_id",
        "anchor",
        "anchor_scale",
        "e214_frontier_gate",
        "survival_score",
        "delta",
        "geometry_delta",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_cos",
        "frontier_keep_abs_share",
        "submission_file",
    ]
    lines = [
        "# E214 JEPA Benefit Gate Translation",
        "",
        "## Purpose",
        "",
        "Test whether the real Q3/S4 JEPA axes need a learned sample-level benefit gate before being translated into public probability movement.",
        "",
        "## Gate Audit",
        "",
        md_table(gate_audit_df, n=20),
        "",
        "## OOF / Subject / Geometry Summary",
        "",
        md_table(summary.sort_values(["delta", "geometry_delta"]), summary_cols, n=30),
        "",
        "## Target Deltas",
        "",
        md_table(target_df.sort_values(["policy_id", "target"]), ["policy_id", "target", "delta", "moved_abs_logit"], n=80),
        "",
        "## Geometry Fold Aggregate",
        "",
        md_table(geometry_agg.sort_values(["delta_mean", "geometry_win_rate"], ascending=[True, False]), n=30),
        "",
        "## Frontier Stress",
        "",
        md_table(frontier.sort_values(["e214_frontier_gate", "survival_score"], ascending=[False, False]), frontier_cols, n=40),
        "",
        "## Selected Submissions",
        "",
        md_table(selected, frontier_cols, n=12),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No benefit-gated JEPA translation beat the E214 gate. This weakens the idea that a simple supervised benefit classifier fixes the E211 public-tail translation problem.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best E214 benefit-gated candidate: `{best['submission_file']}`. It tests `{best['policy_id']}` on `{best['anchor']}` anchor scale `{best['anchor_scale']}`."
        )
        lines.append("- If this wins publicly, JEPA's bottleneck is sample-level translation. If it loses while E211 wins, the benefit gate overfit train labels.")
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    gate_probs = oof_gate_probs(train_feat, stage2_oof, ungated_oof, dep_oof, y, groups)
    gate_audit_df = gate_audit(train_feat, stage2_oof, ungated_oof, dep_oof, y, gate_probs)

    base_loss = mean_loss(y, stage2_oof)
    raw_delta = mean_loss(y, ungated_oof) - base_loss
    e211_toward = e211.apply_policy(stage2_oof, ungated_oof, dep_oof, 1.0, "toward", 1.0)
    e211_toward_delta = mean_loss(y, e211_toward) - base_loss

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[dict[str, Any]] = []
    pred_by_policy: dict[str, np.ndarray] = {}
    for policy in POLICIES:
        pred = apply_policy(stage2_oof, ungated_oof, dep_oof, gate_probs, policy)
        pred_by_policy[policy.policy_id] = pred
        subj = e209.subject_half_summary(train_raw, y, stage2_oof, pred, f"e214:{policy.policy_id}")
        row = {
            "policy_id": policy.policy_id,
            "q3_mode": policy.q3_mode,
            "s4_mode": policy.s4_mode,
            "q3_scale": policy.q3_scale,
            "s4_scale": policy.s4_scale,
            "delta": mean_loss(y, pred) - base_loss,
            "raw_delta": raw_delta,
            "delta_vs_raw": mean_loss(y, pred) - mean_loss(y, ungated_oof),
            "e211_toward_delta": e211_toward_delta,
            "delta_vs_e211_toward": mean_loss(y, pred) - mean_loss(y, e211_toward),
            "subject_half_delta": float(subj["delta_mean"].mean()),
            "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
            "keep_abs_share": keep_share(stage2_oof, ungated_oof, pred),
        }
        summary_rows.append(row)
        target_parts.extend(target_rows(y, stage2_oof, pred, policy))

    geometry_df = geometry_summary(train_raw, sub_raw, train_feat, stage2_oof, ops, POLICIES)
    geometry_agg = (
        geometry_df.groupby(["policy_id", "q3_mode", "s4_mode"], as_index=False)
        .agg(
            delta_mean=("delta_mean", "mean"),
            geometry_win_rate=("delta_mean", lambda x: float((x < 0.0).mean())),
            ungated_delta_mean=("ungated_delta_mean", "mean"),
            keep_abs_share=("keep_abs_share", "mean"),
        )
    )
    geometry_agg["geometry_vs_raw"] = geometry_agg["delta_mean"] - geometry_agg["ungated_delta_mean"]
    summary = pd.DataFrame(summary_rows).merge(
        geometry_agg.rename(
            columns={
                "delta_mean": "geometry_delta",
                "ungated_delta_mean": "ungated_geometry_delta",
                "keep_abs_share": "geometry_keep_abs_share",
            }
        ),
        on=["policy_id", "q3_mode", "s4_mode"],
        how="left",
    )
    target_df = pd.DataFrame(target_parts)
    frontier = frontier_rows(sample, stage2_sub, ungated_sub, stage2_oof, ungated_oof, train_feat, sub_feat, y, anchors, summary)

    selected = frontier[frontier["e214_frontier_gate"]].sort_values(
        ["survival_score", "delta", "geometry_delta"], ascending=[False, True, True]
    )
    selected = selected.groupby("anchor", group_keys=False).head(2).head(4).copy()
    files: list[str] = []
    if not selected.empty:
        dep_oof_full = e210.oof_dependency(stage2_oof, y, groups)
        delta_stage2 = logit(ungated_sub) - logit(stage2_sub)
        policy_map = {p.policy_id: p for p in POLICIES}
        for row in selected.itertuples(index=False):
            policy = policy_map[str(row.policy_id)]
            anchor = anchors[str(row.anchor)]
            raw = clip_prob(sigmoid(logit(anchor) + float(row.anchor_scale) * delta_stage2))
            cond = e210.fit_predict_dependency(stage2_oof, y, anchor)
            gate_anchor = fit_full_gate_for_rows(train_feat, sub_feat, stage2_oof, anchor, ungated_oof, raw, dep_oof_full, cond, y)
            pred = apply_policy(anchor, raw, cond, gate_anchor, policy)
            files.append(materialize(sample, pred, policy, str(row.anchor), float(row.anchor_scale)))
        selected = selected.copy()
        selected["submission_file"] = files
        frontier = frontier.merge(
            selected[["policy_id", "anchor", "anchor_scale", "submission_file"]],
            on=["policy_id", "anchor", "anchor_scale"],
            how="left",
        )
    else:
        frontier["submission_file"] = ""
        selected["submission_file"] = ""

    gate_audit_df.to_csv(GATE_AUDIT_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    geometry_agg.to_csv(GEOMETRY_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(gate_audit_df, summary, target_df, geometry_agg, frontier, selected)

    print("[gate audit]")
    print(gate_audit_df.round(9).to_string(index=False))
    print("\n[summary top]")
    cols = [
        "policy_id",
        "delta",
        "delta_vs_raw",
        "delta_vs_e211_toward",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
        "geometry_vs_raw",
        "keep_abs_share",
    ]
    print(summary.sort_values(["delta", "geometry_delta"])[cols].round(9).to_string(index=False))
    print("\n[frontier top]")
    fcols = [
        "policy_id",
        "anchor",
        "anchor_scale",
        "e214_frontier_gate",
        "survival_score",
        "delta",
        "geometry_delta",
        "vs_e95_expected_delta_focus_mean",
        "bad_span_energy",
        "max_bad_cos",
        "frontier_keep_abs_share",
        "submission_file",
    ]
    print(frontier.sort_values(["e214_frontier_gate", "survival_score"], ascending=[False, False])[fcols].head(32).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
