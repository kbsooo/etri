#!/usr/bin/env python3
"""E209: materialize the E208 feature-neighbor JEPA signal under frontier stress.

E208 proved that the feature-neighbor JEPA task is learnable, but it deliberately
did not create a submission. This experiment asks the next smallest question:
can the E208 Q3/S4-only operations become a submission-grade movement when
compared with the current frontier tensors?

The script keeps three objects separate:

1. stage2 OOF validation, where the E208 corrections were discovered;
2. geometry-fold and subject-half stress, where local OOF shortcuts are rejected;
3. frontier graft stress, where the stage2-learned logit movement is placed on
   E95/E154/Mixmin and checked against hard-label priors and known bad axes.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import broad_feature_addon_builder as bfab  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e164_universe_broad_edge_screen as e164  # noqa: E402
import e165_broad_edge_bad_axis_geometry as e165  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E176_FILE = "submission_e176_abl_q2_to0p75_91e49725.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E101_FILE = "submission_e101_q2s3tail_177569bc.csv"

TRAIN_FEATURES = OUT / "e208_feature_neighbor_jepa_train_features.parquet"
SUB_FEATURES = OUT / "e208_feature_neighbor_jepa_submission_features.parquet"

SUMMARY_OUT = OUT / "e209_feature_neighbor_jepa_materialization_summary.csv"
TARGET_OUT = OUT / "e209_feature_neighbor_jepa_materialization_target_deltas.csv"
SUBJECT_OUT = OUT / "e209_feature_neighbor_jepa_materialization_subject_halves.csv"
GEOMETRY_OUT = OUT / "e209_feature_neighbor_jepa_materialization_geometry.csv"
FRONTIER_OUT = OUT / "e209_feature_neighbor_jepa_materialization_frontier_stress.csv"
SELECTED_OUT = OUT / "e209_feature_neighbor_jepa_materialization_selected.csv"
REPORT_OUT = OUT / "e209_feature_neighbor_jepa_materialization_report.md"

EPS = 1.0e-12
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]


@dataclass(frozen=True)
class Op:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float


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


def target_group_share(move: np.ndarray, names: set[str]) -> float:
    mask = np.array([target in names for target in TARGETS], dtype=bool)
    den = float(np.sum(np.abs(move)))
    if den <= 1.0e-15:
        return 0.0
    return float(np.sum(np.abs(move[:, mask])) / den)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def read_feature_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"{path} missing. Run e208_feature_neighbor_jepa_probe.py first.")
    frame = pd.read_parquet(path)
    for col in ["sleep_date", "lifelog_date"]:
        frame[col] = pd.to_datetime(frame[col])
    return frame


def read_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_raw, sub_raw, train_base, sub_base = bfab.build_frames()
    train_e208 = read_feature_frame(TRAIN_FEATURES)
    sub_e208 = read_feature_frame(SUB_FEATURES)
    keep_cols = [c for c in train_e208.columns if c.startswith("e208_")]
    train_feat = train_raw[SUB_KEY + TARGETS].merge(train_e208[SUB_KEY + keep_cols], on=SUB_KEY, how="left")
    sub_feat = sub_raw[SUB_KEY].merge(sub_e208[SUB_KEY + keep_cols], on=SUB_KEY, how="left")
    if len(train_feat) != len(train_raw) or len(sub_feat) != len(sub_raw):
        raise RuntimeError("E208 feature merge changed row counts")
    if train_feat[keep_cols].isna().any().any() or sub_feat[keep_cols].isna().any().any():
        raise RuntimeError("E208 feature merge introduced missing values")
    # Keep subject/date ordering identical to bfab/build_frames and geometry folds.
    assert train_base[SUB_KEY].equals(train_feat[SUB_KEY])
    assert sub_base[SUB_KEY].equals(sub_feat[SUB_KEY])
    return train_raw, sub_raw, train_feat, sub_feat


def combo_defs() -> dict[str, list[Op]]:
    q3_center = Op("Q3", "e208_resid_self_pc10", "subject_center", 0.20, 0.45)
    q3_z = Op("Q3", "e208_resid_self_pc10", "subject_z", 0.20, 0.45)
    q3_rank = Op("Q3", "e208_resid_self_pc10", "subject_rank", 0.20, 0.45)
    q3_center_c010 = Op("Q3", "e208_resid_self_pc10", "subject_center", 0.10, 0.45)
    s4_rank = Op("S4", "e208_pred_pc14", "subject_rank", 0.20, 0.45)
    return {
        "q3_center": [q3_center],
        "q3_z": [q3_z],
        "q3_rank": [q3_rank],
        "q3_center_c010": [q3_center_c010],
        "s4_rank": [s4_rank],
        "q3_center_s4_rank": [q3_center, s4_rank],
        "q3_z_s4_rank": [q3_z, s4_rank],
        "q3_rank_s4_rank": [q3_rank, s4_rank],
        "q3_center_c010_s4_rank": [q3_center_c010, s4_rank],
    }


def apply_op_oof(rows: pd.DataFrame, pred: np.ndarray, op: Op) -> np.ndarray:
    out = pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.oof_corrected(rows, out, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip_prob((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_op_fit_predict(ref: pd.DataFrame, rows: pd.DataFrame, ref_pred: np.ndarray, row_pred: np.ndarray, op: Op) -> np.ndarray:
    out = row_pred.copy()
    j = TARGETS.index(op.target)
    corrected = broad.fit_corrected(ref, rows, ref_pred, row_pred, op.target, op.feature, op.mode, op.c_value)
    out[:, j] = clip_prob((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_ops_oof(rows: pd.DataFrame, base: np.ndarray, ops: list[Op]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        out = apply_op_oof(rows, out, op)
    return clip_prob(out)


def apply_ops_fit_predict(
    train_feat: pd.DataFrame,
    pred_feat: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    ops: list[Op],
) -> np.ndarray:
    out = pred_base.copy()
    ref = train_base.copy()
    for op in ops:
        out = apply_op_fit_predict(train_feat, pred_feat, ref, out, op)
        ref = apply_op_fit_predict(train_feat, train_feat, ref, ref, op)
    return clip_prob(out)


def subject_half_summary(train: pd.DataFrame, y: np.ndarray, base: np.ndarray, pred: np.ndarray, combo: str) -> pd.DataFrame:
    subjects = np.array(sorted(train["subject_id"].astype(str).unique()))
    rng = np.random.default_rng(291209)
    rows: list[dict[str, float | str | int]] = []
    for repeat in range(260):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        hold = ~train["subject_id"].astype(str).isin(picked).to_numpy()
        rec: dict[str, float | str | int] = {
            "combo": combo,
            "repeat": repeat,
            "delta_mean": mean_loss(y[hold], pred[hold]) - mean_loss(y[hold], base[hold]),
        }
        for j, target in enumerate(TARGETS):
            rec[f"{target}_delta"] = loss_col(y[hold, j], pred[hold, j]) - loss_col(y[hold, j], base[hold, j])
        rows.append(rec)
    return pd.DataFrame(rows)


def geometry_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    base: np.ndarray,
    ops: list[Op],
    combo: str,
) -> pd.DataFrame:
    y_all = train_raw[TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, float | str | int]] = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=291209):
        ref = train_feat.iloc[tr_idx].reset_index(drop=True)
        val = train_feat.iloc[val_idx].reset_index(drop=True)
        ref_pred = base[tr_idx].copy()
        val_pred = base[val_idx].copy()
        for op in ops:
            val_pred = apply_op_fit_predict(ref, val, ref_pred, val_pred, op)
            ref_pred = apply_op_fit_predict(ref, ref, ref_pred, ref_pred, op)
        y = y_all[val_idx]
        rec: dict[str, float | str | int] = {
            "combo": combo,
            "fold": fold,
            "delta_mean": mean_loss(y, val_pred) - mean_loss(y, base[val_idx]),
        }
        for j, target in enumerate(TARGETS):
            rec[f"{target}_delta"] = loss_col(y[:, j], val_pred[:, j]) - loss_col(y[:, j], base[val_idx, j])
        rows.append(rec)
    return pd.DataFrame(rows)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def frontier_stress(
    combo: str,
    pred_stage2_sub: np.ndarray,
    stage2_sub: np.ndarray,
    anchors: dict[str, np.ndarray],
    sample: pd.DataFrame,
    oof_row: dict[str, Any],
) -> pd.DataFrame:
    priors = e162.prior_arrays(sample)
    e95 = anchors["e95"]
    z95 = logit(e95)
    e154 = anchors["e154"]
    e101 = anchors["e101"]
    mixmin = anchors["mixmin"]
    bad_names, bad_basis = e165.bad_axes(sample, z95)
    axis_e154 = (logit(e154) - z95).reshape(-1)
    axis_e101 = (logit(e101) - z95).reshape(-1)
    axis_mixmin = (logit(mixmin) - z95).reshape(-1)

    delta_from_stage2 = logit(pred_stage2_sub) - logit(stage2_sub)
    active_targets = np.abs(delta_from_stage2).sum(axis=0) > EPS
    rows: list[dict[str, Any]] = []
    for anchor_name in ["e95", "e154", "mixmin"]:
        anchor = anchors[anchor_name]
        z_anchor = logit(anchor)
        for scale in [0.25, 0.50, 0.75, 1.00]:
            pred = clip_prob(sigmoid(z_anchor + scale * delta_from_stage2))
            move_vs_e95 = logit(pred) - z95
            move_vs_anchor = logit(pred) - z_anchor
            hard_vs_e95 = e164.hard_breadth_metrics(pred, e95, priors)
            hard_vs_anchor = e164.hard_breadth_metrics(pred, anchor, priors)
            bad_energy, bad_resid = e165.span_energy(move_vs_e95, bad_basis)
            bad_cos = {f"cos_bad_{name}": cosine(move_vs_e95, bad_basis[i]) for i, name in enumerate(bad_names)}
            max_bad_name = max(bad_names, key=lambda name: bad_cos[f"cos_bad_{name}"])
            rec: dict[str, Any] = {
                "combo": combo,
                "anchor": anchor_name,
                "scale": scale,
                "active_targets": ",".join(TARGETS[j] for j, ok in enumerate(active_targets) if ok),
                "stage2_oof_delta": oof_row["delta"],
                "stage2_subject_half_delta": oof_row["subject_half_delta"],
                "stage2_subject_half_win_rate": oof_row["subject_half_win_rate"],
                "stage2_geometry_delta": oof_row["geometry_delta"],
                "stage2_geometry_win_rate": oof_row["geometry_win_rate"],
                "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move_vs_e95))),
                "max_abs_logit_move_vs_e95": float(np.max(np.abs(move_vs_e95))),
                "mean_abs_logit_step_vs_anchor": float(np.mean(np.abs(move_vs_anchor))),
                "max_abs_logit_step_vs_anchor": float(np.max(np.abs(move_vs_anchor))),
                "q3s4_share_vs_e95": target_group_share(move_vs_e95, {"Q3", "S4"}),
                "q2s3_share_vs_e95": target_group_share(move_vs_e95, {"Q2", "S3"}),
                "bad_span_energy": bad_energy,
                "bad_span_residual": bad_resid,
                "max_bad_axis": max_bad_name,
                "max_bad_cos": bad_cos[f"cos_bad_{max_bad_name}"],
                "cos_e154_axis": cosine(move_vs_e95, axis_e154),
                "cos_e101_axis": cosine(move_vs_e95, axis_e101),
                "cos_mixmin_axis": cosine(move_vs_e95, axis_mixmin),
                **{f"vs_e95_{k}": v for k, v in hard_vs_e95.items()},
                **{f"vs_anchor_{k}": v for k, v in hard_vs_anchor.items()},
            }
            rec["e209_frontier_gate"] = bool(
                rec["stage2_oof_delta"] < 0.0
                and rec["stage2_subject_half_delta"] < 0.0
                and rec["stage2_subject_half_win_rate"] >= 0.62
                and rec["stage2_geometry_delta"] <= 0.0
                and rec["stage2_geometry_win_rate"] >= 0.50
                and rec["anchor"] in {"e95", "e154"}
                and rec["vs_e95_expected_delta_focus_mean"] <= -2.0e-6
                and rec["vs_e95_cells_for_2e6_guard"] >= 1
                and rec["vs_e95_top1_over_abs_expected"] <= 0.90
                and rec["bad_span_energy"] <= 0.55
                and rec["max_bad_cos"] <= 0.35
                and rec["mean_abs_logit_step_vs_anchor"] <= 0.012
            )
            rec["survival_score"] = (
                -float(rec["stage2_oof_delta"]) * 1.0
                - float(rec["stage2_geometry_delta"]) * 2.0
                - min(float(rec["vs_e95_expected_delta_focus_mean"]), 0.0) * 50.0
                + min(float(rec["vs_e95_cells_for_2e6_guard"]), 8) * 1.0e-4
                - max(float(rec["bad_span_energy"]) - 0.35, 0.0) * 1.0e-3
                - max(float(rec["max_bad_cos"]) - 0.20, 0.0) * 1.0e-3
                - max(float(rec["vs_e95_top1_over_abs_expected"]) - 0.50, 0.0) * 5.0e-4
            )
            rows.append(rec)
    return pd.DataFrame(rows)


def materialize_submission(sample: pd.DataFrame, pred: np.ndarray, combo: str, anchor: str, scale: float) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    scale_tag = str(scale).replace(".", "p")
    file_name = f"submission_e209_jepa_{combo}_{anchor}_s{scale_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def write_report(summary: pd.DataFrame, frontier: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "combo",
        "n_ops",
        "targets",
        "delta",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
    ]
    frontier_cols = [
        "combo",
        "anchor",
        "scale",
        "e209_frontier_gate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_cells_for_2e6_guard",
        "vs_e95_top1_over_abs_expected",
        "bad_span_energy",
        "max_bad_axis",
        "max_bad_cos",
        "mean_abs_logit_step_vs_anchor",
        "submission_file",
    ]
    lines = [
        "# E209 Feature-Neighbor JEPA Materialization Stress",
        "",
        "## Purpose",
        "",
        "Materialize only the E208 Q3/S4 operations and test whether the learned JEPA movement remains sane when grafted onto frontier tensors.",
        "",
        "## Stage2 OOF/Subject/Geometry Summary",
        "",
        md_table(summary.sort_values(["delta", "geometry_delta"]), top_cols, n=20),
        "",
        "## Frontier Stress",
        "",
        md_table(frontier.sort_values(["e209_frontier_gate", "survival_score"], ascending=[False, False]), frontier_cols, n=24),
        "",
        "## Selected Submissions",
        "",
        md_table(selected, frontier_cols, n=12),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No E209 graft passed the frontier materialization gate. Keep E208 as diagnostic JEPA evidence and revise the probability translator.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best materialized candidate: `{best['submission_file']}`. It tests whether the E208 Q3/S4 JEPA residual can improve the `{best['anchor']}` frontier tensor at scale `{best['scale']}`."
        )
        lines.append("- This remains a hypothesis submission, not proof of a 0.54 path. Public feedback should be read as a Q3/S4 JEPA-translation sensor.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    if not sub_feat[SUB_KEY].astype(str).equals(sample[KEYS].astype(str)):
        raise RuntimeError("submission feature order differs from sample order")

    stage2_oof = clip_prob(np.load(OUT / STAGE2_OOF))
    stage2_sub = load_prob(STAGE2_FILE, sample)
    anchors = {
        "stage2": stage2_sub,
        "e95": load_prob(E95_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e176": load_prob(E176_FILE, sample),
        "mixmin": load_prob(MIXMIN_FILE, sample),
        "e101": load_prob(E101_FILE, sample),
    }

    summary_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    subject_parts: list[pd.DataFrame] = []
    geometry_parts: list[pd.DataFrame] = []
    frontier_parts: list[pd.DataFrame] = []
    preds_oof: dict[str, np.ndarray] = {}
    preds_sub: dict[str, np.ndarray] = {}
    combos = combo_defs()
    base_loss = mean_loss(y, stage2_oof)

    for combo, ops in combos.items():
        pred_oof = apply_ops_oof(train_feat, stage2_oof, ops)
        pred_sub = apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
        preds_oof[combo] = pred_oof
        preds_sub[combo] = pred_sub

        subj = subject_half_summary(train_raw, y, stage2_oof, pred_oof, combo)
        geo = geometry_summary(train_raw, sub_raw, train_feat, stage2_oof, ops, combo)
        subject_parts.append(subj)
        geometry_parts.append(geo)
        row: dict[str, Any] = {
            "combo": combo,
            "n_ops": len(ops),
            "targets": ",".join(op.target for op in ops),
            "base_loss": base_loss,
            "candidate_loss": mean_loss(y, pred_oof),
            "delta": mean_loss(y, pred_oof) - base_loss,
            "subject_half_delta": float(subj["delta_mean"].mean()),
            "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
            "geometry_delta": float(geo["delta_mean"].mean()),
            "geometry_win_rate": float((geo["delta_mean"] < 0).mean()),
        }
        summary_rows.append(row)
        for j, target in enumerate(TARGETS):
            target_rows.append(
                {
                    "combo": combo,
                    "target": target,
                    "base_loss": loss_col(y[:, j], stage2_oof[:, j]),
                    "candidate_loss": loss_col(y[:, j], pred_oof[:, j]),
                    "delta": loss_col(y[:, j], pred_oof[:, j]) - loss_col(y[:, j], stage2_oof[:, j]),
                }
            )
        frontier_parts.append(frontier_stress(combo, pred_sub, stage2_sub, anchors, sample, row))

    summary = pd.DataFrame(summary_rows).sort_values(["delta", "geometry_delta"]).reset_index(drop=True)
    target_df = pd.DataFrame(target_rows)
    subject_df = pd.concat(subject_parts, ignore_index=True)
    geometry_df = pd.concat(geometry_parts, ignore_index=True)
    frontier = pd.concat(frontier_parts, ignore_index=True)

    selected = frontier[frontier["e209_frontier_gate"]].sort_values(
        ["survival_score", "vs_e95_expected_delta_focus_mean"], ascending=[False, True]
    ).head(4).copy()
    submission_files: list[str] = []
    for row in selected.itertuples(index=False):
        combo = str(row.combo)
        anchor = str(row.anchor)
        scale = float(row.scale)
        pred = clip_prob(sigmoid(logit(anchors[anchor]) + scale * (logit(preds_sub[combo]) - logit(stage2_sub))))
        submission_files.append(materialize_submission(sample, pred, combo, anchor, scale))
    if not selected.empty:
        selected = selected.copy()
        selected["submission_file"] = submission_files
        frontier = frontier.merge(
            selected[["combo", "anchor", "scale", "submission_file"]],
            on=["combo", "anchor", "scale"],
            how="left",
        )
    else:
        frontier["submission_file"] = ""
        selected["submission_file"] = ""

    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    subject_df.to_csv(SUBJECT_OUT, index=False)
    geometry_df.to_csv(GEOMETRY_OUT, index=False)
    frontier.to_csv(FRONTIER_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, frontier, selected)

    print("[summary]")
    print(summary.round(9).to_string(index=False))
    print("\n[frontier top]")
    cols = [
        "combo",
        "anchor",
        "scale",
        "e209_frontier_gate",
        "survival_score",
        "vs_e95_expected_delta_focus_mean",
        "bad_span_energy",
        "max_bad_cos",
        "mean_abs_logit_step_vs_anchor",
        "submission_file",
    ]
    print(frontier.sort_values(["e209_frontier_gate", "survival_score"], ascending=[False, False])[cols].head(24).round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
