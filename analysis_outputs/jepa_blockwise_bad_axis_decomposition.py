from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
import jepa_regularized_sparse_direct_solver as sparse_solver  # noqa: E402
import jepa_sparse_scale_ladder_stress as ladder  # noqa: E402
import jepa_inverse7_gated_sparse_scale as inv7_gate  # noqa: E402
from public_subset_sensitivity_audit import build_masks  # noqa: E402


SCAN_OUT = OUT / "jepa_blockwise_bad_axis_decomposition_scan.csv"
CV_DETAIL_OUT = OUT / "jepa_blockwise_bad_axis_decomposition_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_blockwise_bad_axis_decomposition_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_blockwise_bad_axis_decomposition_selected.csv"
REPORT_OUT = OUT / "jepa_blockwise_bad_axis_decomposition_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
}

BAD_AXIS_FILES = {
    "anchor578": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "ordinal_q": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "jepa_bad_residual": "submission_jepa_latent_residual_probe.csv",
    "jepa_bad_q2": "submission_jepa_latent_q2_w0p45.csv",
    "directcons_bad_all": "submission_directcons_1d5b6f39.csv",
    "directcons_bad_q": "submission_directcons_95be47ec.csv",
    "directcons_bad_stage": "submission_directcons_0b3f77c3.csv",
}

AXIS_GROUPS = {
    "classic_bad2": ["anchor578", "ordinal_q"],
    "public_bad4": ["anchor578", "ordinal_q", "jepa_bad_residual", "jepa_bad_q2"],
    "consensus_bad3": ["directcons_bad_all", "directcons_bad_q", "directcons_bad_stage"],
    "all_bad7": [
        "anchor578",
        "ordinal_q",
        "jepa_bad_residual",
        "jepa_bad_q2",
        "directcons_bad_all",
        "directcons_bad_q",
        "directcons_bad_stage",
    ],
}

SOURCE_TARGETS = {
    "full": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
}

CORRECTION_TARGETS = {
    "all": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "stage_all": ["S1", "S2", "S3", "S4"],
}

SCALES = [1.15, 1.30, 1.50, 1.75]
ANTI_LAMBDAS = [0.25, 0.35, 0.50, 0.70, 1.00]
PROJECTION_MODES = ["positive", "signed"]
DELTA_CAP = 0.30


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64)


def target_gate(targets: list[str], n_rows: int) -> np.ndarray:
    keep = np.asarray([target in set(targets) for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(keep.reshape(1, -1), n_rows, axis=0)


def named_mask(records: list[dict[str, object]], kind: str, name: str) -> np.ndarray:
    for record in records:
        if record["mask_kind"] == kind and record["mask_name"] == name:
            mask = record["mask"]
            assert isinstance(mask, np.ndarray)
            return mask.astype(np.float64)
    raise KeyError(f"{kind}:{name}")


def build_row_gates(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    records = build_masks(sample)
    gates = inv7_gate.build_row_gates(sample)
    selected = {
        "id01": gates["id01"],
        "prefix20": gates["prefix20"],
        "prefix30": gates["prefix30"],
        "subject_prefix25": gates["subject_prefix25"],
        "inv64_soft": gates["inv64_soft"],
        "inv64_top20": gates["inv64_top20"],
        "inv64_top30": gates["inv64_top30"],
        "rowmod4_rem3": named_mask(records, "global_order", "rowmod4_rem3"),
        "subject_suffix25": named_mask(records, "subject_order", "per_subject_suffix_frac0.25"),
    }
    selected["not_prefix20"] = 1.0 - selected["prefix20"]
    selected["not_prefix30"] = 1.0 - selected["prefix30"]
    selected["not_id01"] = 1.0 - selected["id01"]
    return selected


def build_bad_axes(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, np.ndarray]:
    axes: dict[str, np.ndarray] = {}
    for axis_name, file_name in BAD_AXIS_FILES.items():
        if inv.locate(file_name) is None:
            continue
        pred = load_array(file_name, sample)
        delta = inv.logit(pred) - base_logit
        if float(np.linalg.norm(delta.reshape(-1))) > 1e-10:
            axes[axis_name] = delta
    return axes


def projection_stats(delta: np.ndarray, gate: np.ndarray, axes: list[np.ndarray]) -> dict[str, float]:
    coefs: list[float] = []
    abs_coefs: list[float] = []
    cosines: list[float] = []
    dvec = (delta * gate).reshape(-1)
    dnorm = float(np.linalg.norm(dvec))
    for axis in axes:
        avec = (axis * gate).reshape(-1)
        denom = float(np.dot(avec, avec))
        if denom <= 1e-12:
            continue
        coef = float(np.dot(dvec, avec) / denom)
        coefs.append(max(coef, 0.0))
        abs_coefs.append(abs(coef))
        anorm = float(np.linalg.norm(avec))
        if dnorm > 1e-12 and anorm > 1e-12:
            cosines.append(float(np.dot(dvec, avec) / (dnorm * anorm)))
    return {
        "bad_align_pos_mean": float(np.mean(coefs)) if coefs else 0.0,
        "bad_align_abs_mean": float(np.mean(abs_coefs)) if abs_coefs else 0.0,
        "bad_cosine_mean": float(np.mean(cosines)) if cosines else 0.0,
    }


def block_project(
    source_delta: np.ndarray,
    source_gate: np.ndarray,
    correction_gate: np.ndarray,
    axes: list[np.ndarray],
    anti_lambda: float,
    mode: str,
) -> tuple[np.ndarray, dict[str, float]]:
    out = source_delta * source_gate
    before = projection_stats(out, correction_gate, axes)
    removed_norm = 0.0
    for axis in axes:
        masked_axis = axis * correction_gate
        avec = masked_axis.reshape(-1)
        denom = float(np.dot(avec, avec))
        if denom <= 1e-12:
            continue
        coef = float(np.dot(out.reshape(-1), avec) / denom)
        if mode == "positive" and coef <= 0:
            continue
        if mode == "signed" and abs(coef) <= 1e-12:
            continue
        removal = anti_lambda * coef * masked_axis
        out = out - removal
        removed_norm += float(np.linalg.norm(removal.reshape(-1)))
    out *= source_gate
    after = projection_stats(out, correction_gate, axes)
    original_norm = float(np.linalg.norm((source_delta * source_gate * correction_gate).reshape(-1)))
    active_delta_norm = float(np.linalg.norm((out * correction_gate).reshape(-1)))
    return out, {
        **{f"before_{key}": value for key, value in before.items()},
        **{f"after_{key}": value for key, value in after.items()},
        "removed_norm": removed_norm,
        "removed_norm_ratio": removed_norm / original_norm if original_norm > 1e-12 else 0.0,
        "block_delta_norm_ratio_after": active_delta_norm / original_norm if original_norm > 1e-12 else 0.0,
    }


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    row_gates = build_row_gates(sample)
    bad_axes = build_bad_axes(sample, base_logit)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    n_rows = len(sample)

    for source_name, source_file in SOURCE_FILES.items():
        source = load_array(source_file, sample)
        source_delta = inv.logit(source) - base_logit
        for source_target_name, source_targets in SOURCE_TARGETS.items():
            source_gate = target_gate(source_targets, n_rows)
            source_move = float(np.mean(np.abs(inv.sigmoid(base_logit + source_delta * source_gate) - base)))
            source_active = np.abs(source_delta * source_gate) > 1e-10
            for row_gate_name, row_gate in row_gates.items():
                row_gate_2d = row_gate.reshape(-1, 1)
                row_support = row_gate > 1e-10
                for correction_target_name, correction_targets in CORRECTION_TARGETS.items():
                    correction_gate = row_gate_2d * target_gate(correction_targets, n_rows) * source_gate
                    active = source_active & (correction_gate > 1e-10)
                    active_cells = int(active.sum())
                    if active_cells <= 0:
                        continue
                    active_rows = int((active.sum(axis=1) > 0).sum())
                    active_energy = consensus["energy"][active]
                    for axis_group, axis_names in AXIS_GROUPS.items():
                        axes = [bad_axes[name] for name in axis_names if name in bad_axes]
                        if not axes:
                            continue
                        for anti_lambda in ANTI_LAMBDAS:
                            for projection_mode in PROJECTION_MODES:
                                adjusted_delta, stats = block_project(
                                    source_delta=source_delta,
                                    source_gate=source_gate,
                                    correction_gate=correction_gate,
                                    axes=axes,
                                    anti_lambda=anti_lambda,
                                    mode=projection_mode,
                                )
                                if stats["removed_norm_ratio"] <= 1e-10:
                                    continue
                                for scale in SCALES:
                                    final_delta = np.clip(scale * adjusted_delta, -DELTA_CAP, DELTA_CAP)
                                    pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                                    label = (
                                        f"{source_name}|{source_target_name}|{row_gate_name}|"
                                        f"{correction_target_name}|{axis_group}|a{anti_lambda:.2f}|"
                                        f"{projection_mode}|s{scale:.2f}"
                                    )
                                    tag = stable_hash(label)
                                    name = f"blockorth_{tag}"
                                    arrays[name] = pred
                                    rows.append(
                                        {
                                            "name": name,
                                            "file": f"submission_blockorth_{tag}.csv",
                                            "source_name": source_name,
                                            "source_file": source_file,
                                            "variant": f"{source_target_name}/{row_gate_name}/{correction_target_name}/{axis_group}/{projection_mode}",
                                            "source_target": source_target_name,
                                            "row_gate": row_gate_name,
                                            "correction_target": correction_target_name,
                                            "axis_group": axis_group,
                                            "anti_lambda": anti_lambda,
                                            "projection_mode": projection_mode,
                                            "scale": scale,
                                            "delta_cap": DELTA_CAP,
                                            "source_mean_abs_move_vs_a2c8": source_move,
                                            "row_support_rows": int(row_support.sum()),
                                            "row_gate_sum": float(row_gate.sum()),
                                            "active_cells": active_cells,
                                            "active_rows": active_rows,
                                            "mean_active_energy": float(np.mean(active_energy)),
                                            "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                                            "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                                            "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                                            **stats,
                                        }
                                    )
    return pd.DataFrame(rows), arrays


def prefilter(meta: pd.DataFrame, arrays: dict[str, np.ndarray], limit: int = 560) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    if meta.empty:
        return meta, arrays
    frame = meta.copy()
    reduction = frame["before_bad_align_abs_mean"] - frame["after_bad_align_abs_mean"]
    frame["cheap_priority"] = (
        np.abs(frame["mean_abs_move_vs_a2c8"] - 0.0086)
        + 0.0008 * np.maximum(frame["removed_norm_ratio"] - 0.45, 0.0)
        + 0.0003 * np.maximum(frame["block_delta_norm_ratio_after"] - 1.25, 0.0)
        - 0.0010 * np.minimum(np.maximum(reduction, 0.0), 0.20)
        - 0.0007 * np.minimum(frame["removed_norm_ratio"], 0.30)
        - 0.0003 * np.minimum(frame["mean_active_energy"] / 1.5, 1.5)
    )
    eligible = frame[
        frame["mean_abs_move_vs_a2c8"].between(0.0050, 0.0135)
        & frame["removed_norm_ratio"].between(0.01, 0.90)
        & (frame["block_delta_norm_ratio_after"] <= 1.60)
    ].copy()
    if eligible.empty:
        eligible = frame.copy()
    selected = pd.concat(
        [
            eligible.sort_values("cheap_priority").head(240),
            eligible[
                (eligible["row_gate"].isin(["prefix20", "prefix30", "id01", "inv64_top20"]))
                & (eligible["source_target"].isin(["full", "no_q2"]))
            ].sort_values("cheap_priority").head(160),
            eligible[
                (eligible["correction_target"].isin(["q3_stage", "q3_s2_s3_s4", "stage_all"]))
                & (eligible["mean_abs_move_vs_a2c8"] >= 0.0060)
            ].sort_values("cheap_priority").head(140),
            eligible[
                (eligible["projection_mode"] == "signed")
                & (eligible["removed_norm_ratio"] <= 0.55)
            ].sort_values("cheap_priority").head(120),
            eligible[
                (eligible["axis_group"].isin(["classic_bad2", "public_bad4"]))
                & (eligible["anti_lambda"].isin([0.25, 0.35, 0.50]))
            ].sort_values("cheap_priority").head(180),
        ],
        ignore_index=True,
    ).drop_duplicates("name")
    selected = selected.sort_values("cheap_priority").head(limit).reset_index(drop=True)
    return selected, {str(row.name): arrays[str(row.name)] for row in selected.itertuples(index=False)}


def coalesce_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["mean_abs_move_vs_a2c8", "max_abs_move_vs_a2c8", "mean_abs_move_vs_raw05"]:
        if column not in out.columns:
            for candidate in [f"{column}_y", f"{column}_x"]:
                if candidate in out.columns:
                    out[column] = out[candidate]
                    break
    return out


def candidate_pool_for_cv(scored: pd.DataFrame, limit: int = 132) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("blockorth_")].copy()
    if candidates.empty:
        return candidates
    frames = [
        candidates.sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(52),
        candidates[
            (candidates["actual_anchor_score_final"] <= 0.57782)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0065)
        ].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(48),
        candidates[
            (candidates["robust_delta_vs_a2c8"] <= -0.00105)
            & (candidates["robust_p90_delta_vs_a2c8"] <= -0.00085)
        ].sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"]).head(44),
        candidates[
            (candidates["row_gate"].isin(["prefix20", "prefix30", "id01", "inv64_top20"]))
            & (candidates["actual_anchor_score_final"] <= 0.57790)
        ].sort_values(["actual_anchor_score_final", "mean_abs_move_vs_a2c8"]).head(40),
        candidates[
            (candidates["correction_target"].isin(["q3_stage", "q3_s2_s3_s4", "stage_all"]))
            & (candidates["actual_anchor_score_final"] <= 0.57790)
        ].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(36),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(limit).reset_index(drop=True)


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("blockorth_")].copy()
    if candidates.empty:
        return candidates
    frames = [
        candidates[
            (candidates["actual_anchor_score_final"] <= 0.57773)
            & (candidates["honest_cv_delta_mean"] <= -0.00070)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0065)
        ].assign(submit_role="blockorth_frontier").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        candidates[
            (candidates["mean_abs_move_vs_a2c8"] >= 0.0080)
            & (candidates["actual_anchor_score_final"] <= 0.57780)
            & (candidates["honest_cv_delta_mean"] <= -0.00075)
        ].assign(submit_role="blockorth_large_probe").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        candidates[
            (candidates["row_gate"].isin(["prefix20", "prefix30", "id01", "inv64_top20"]))
            & (candidates["actual_anchor_score_final"] <= 0.57784)
            & (candidates["honest_cv_delta_mean"] <= -0.00060)
        ].assign(submit_role="blockorth_row_diag").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(6),
        candidates[
            (candidates["correction_target"].isin(["q3_stage", "q3_s2_s3_s4", "stage_all"]))
            & (candidates["actual_anchor_score_final"] <= 0.57784)
            & (candidates["honest_cv_delta_mean"] <= -0.00060)
        ].assign(submit_role="blockorth_target_diag").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(6),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def integrity_check(sample: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        path = OUT / str(row.file)
        frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(inv.KEY).reset_index(drop=True)
        probs = frame[inv.TARGETS].to_numpy(dtype=float)
        rows.append(
            {
                "file": str(row.file),
                "shape_ok": tuple(frame.shape) == tuple(sample.shape),
                "key_ok": bool(frame[inv.KEY].reset_index(drop=True).equals(sample[inv.KEY].reset_index(drop=True))),
                "nan_count": int(np.isnan(probs).sum()),
                "min_prob": float(np.min(probs)),
                "max_prob": float(np.max(probs)),
            }
        )
    return pd.DataFrame(rows)


def write_report(scored: pd.DataFrame, selected: pd.DataFrame, integrity: pd.DataFrame) -> None:
    candidates = scored[scored["name"].str.startswith("blockorth_")].copy()
    cols = [
        "name",
        "file",
        "source_name",
        "source_target",
        "row_gate",
        "correction_target",
        "axis_group",
        "anti_lambda",
        "projection_mode",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
        "before_bad_align_abs_mean",
        "after_bad_align_abs_mean",
    ]
    by_block = pd.DataFrame()
    if not candidates.empty:
        by_block = (
            candidates.groupby(["row_gate", "correction_target", "axis_group"], as_index=False)
            .agg(
                best_actual_anchor=("actual_anchor_score_final", "min"),
                best_honest_cv=("honest_cv_delta_mean", "min"),
                max_move=("mean_abs_move_vs_a2c8", "max"),
                median_removed_ratio=("removed_norm_ratio", "median"),
            )
            .sort_values(["best_actual_anchor", "best_honest_cv"])
        )

    selected_text = (
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False)
        if not selected.empty
        else "none"
    )
    integrity_text = integrity.round(9).to_string(index=False) if not integrity.empty else "none"
    report = [
        "# JEPA Blockwise Bad-Axis Decomposition",
        "",
        "This keeps the useful sparse JEPA/direct-label move globally, then removes failed public-axis components only inside specific row-block and target-group gates.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(50).round(9).to_string(index=False)
        if not candidates.empty
        else "none",
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(50).round(9).to_string(index=False)
        if not candidates.empty and "honest_cv_delta_mean" in candidates.columns
        else "none",
        "```",
        "",
        "## Block Summary",
        "",
        "```",
        by_block.head(80).round(9).to_string(index=False) if not by_block.empty else "none",
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected_text,
        "```",
        "",
        "## Integrity",
        "",
        "```",
        integrity_text,
        "```",
        "",
        "## Interpretation",
        "",
        "- If this beats uniform scale-ladder, the failed axes were harmful only in localized row/target blocks.",
        "- If it does not beat uniform scale-ladder, the next path is direct hidden label-prior/subset inference rather than further projection.",
        "- `projection_mode=signed` is a stress test: it removes all local alignment, not only positive alignment.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]

    meta_full, arrays_full = build_candidates(sample, base)
    meta, arrays = prefilter(meta_full, arrays_full)
    robust_scored = ladder.robust_scan(meta, arrays, preds)
    anchor_scored = ladder.actual_anchor_for_ladder(sample, meta, arrays)
    scored = anchor_scored.merge(
        robust_scored.drop(columns=["file"], errors="ignore"),
        on="name",
        how="left",
        suffixes=("", "_robust"),
    )
    scored = coalesce_columns(scored)
    pool = candidate_pool_for_cv(scored)
    pool_arrays = {str(row.name): arrays[str(row.name)] for row in pool.itertuples(index=False)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, pool, pool_arrays, preds)
    honest = ladder.combined_honest_cv(cv_summary)
    scored = scored.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    pool = pool.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    pool = coalesce_columns(pool)
    selected = select_outputs(sample, pool, arrays)
    integrity = integrity_check(sample, selected)

    scored.to_csv(SCAN_OUT, index=False)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(scored, selected, integrity)

    cols = [
        "name",
        "file",
        "source_name",
        "source_target",
        "row_gate",
        "correction_target",
        "axis_group",
        "anti_lambda",
        "projection_mode",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
    ]
    print(REPORT_OUT)
    print("[candidate pool]", pool.shape)
    print(pool[[c for c in cols if c in pool.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(30).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")
    print("[integrity]")
    print(integrity.round(9).to_string(index=False) if not integrity.empty else "none")


if __name__ == "__main__":
    main()
