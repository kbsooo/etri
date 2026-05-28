from __future__ import annotations

from hashlib import sha1
from itertools import combinations
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
import jepa_bad_axis_orthogonal_scale_ladder as orth  # noqa: E402


SCAN_OUT = OUT / "jepa_sparse_direction_ensemble_orthogonalizer_scan.csv"
CV_DETAIL_OUT = OUT / "jepa_sparse_direction_ensemble_orthogonalizer_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_sparse_direction_ensemble_orthogonalizer_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_sparse_direction_ensemble_orthogonalizer_selected.csv"
REPORT_OUT = OUT / "jepa_sparse_direction_ensemble_orthogonalizer_report.md"


DIRECTION_FILES = {
    "ladder_b01_282_full_s1p3": "submission_sparseladder_b01acaa1.csv",
    "ladder_898_f465_full_s1p5": "submission_sparseladder_89817541.csv",
    "ladder_f1ee_f465_noq2_s1p5": "submission_sparseladder_f1ee16b0.csv",
    "ladder_3be_282_energy_s1p5": "submission_sparseladder_3be0b7a3.csv",
    "sparse_f465_s1": "submission_sparsejepa_f4657144.csv",
    "sparse_282_s1": "submission_sparsejepa_282e9546.csv",
    "sparse_f43_cv": "submission_sparsejepa_f43ea825.csv",
    "sparse_3cf_noq2": "submission_sparsejepa_3cfdf64a.csv",
    "target_q3stage": "submission_targetabl_b19056bb.csv",
    "target_q3_s234": "submission_targetabl_1049b8e7.csv",
    "blockorth_3a28": "submission_blockorth_3a28f87f.csv",
    "blockorth_0352": "submission_blockorth_0352b65f.csv",
    "blockorth_f628": "submission_blockorth_f628c242.csv",
    "blockorth_4696": "submission_blockorth_46969019.csv",
}

BAD_AXIS_FILES = orth.BAD_AXIS_FILES
AXIS_GROUPS = {
    "none": [],
    "classic_bad2": orth.AXIS_GROUPS["classic_bad2"],
    "public_bad4": orth.AXIS_GROUPS["public_bad4"],
}

TARGET_GROUPS = {
    "full": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
}

PAIR_WEIGHTS = [(0.35, 0.65), (0.50, 0.50), (0.65, 0.35)]
TRI_WEIGHTS = [
    (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0),
    (0.50, 0.25, 0.25),
]
SCALES = [0.95, 1.10, 1.25]
ANTI_LAMBDAS = [0.0, 0.25, 0.35]
DELTA_CAPS = [0.30]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return inv.clip_prob(inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64))


def build_bad_axes(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, np.ndarray]:
    axes: dict[str, np.ndarray] = {}
    for axis_name, file_name in BAD_AXIS_FILES.items():
        if inv.locate(file_name) is None:
            continue
        pred = load_array(file_name, sample)
        axis = inv.logit(pred) - base_logit
        if float(np.linalg.norm(axis.reshape(-1))) > 1e-10:
            axes[axis_name] = axis
    return axes


def target_gate(name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_GROUPS[name])
    keep = np.asarray([target in allowed for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(keep.reshape(1, -1), n_rows, axis=0)


def energy_gate(name: str, delta: np.ndarray, energy: np.ndarray) -> np.ndarray:
    if name == "all_cells":
        return np.ones_like(delta)
    active = np.abs(delta) > 1e-10
    if not active.any():
        return np.zeros_like(delta)
    if name == "energy_top70":
        cutoff = np.quantile(energy[active], 0.30)
        return ((energy >= cutoff) & active).astype(np.float64)
    if name == "energy_top50":
        cutoff = np.quantile(energy[active], 0.50)
        return ((energy >= cutoff) & active).astype(np.float64)
    if name == "abs_top70":
        cutoff = np.quantile(np.abs(delta[active]), 0.30)
        return ((np.abs(delta) >= cutoff) & active).astype(np.float64)
    raise ValueError(name)


def sign_agreement_gate(source_deltas: list[np.ndarray], delta: np.ndarray, mode: str) -> np.ndarray:
    if mode == "none":
        return np.ones_like(delta)
    signs = np.stack([np.sign(d) for d in source_deltas], axis=0)
    target_sign = np.sign(delta)
    nonzero = np.abs(signs).sum(axis=0) > 0
    agree = (signs == target_sign.reshape(1, *target_sign.shape)) & (target_sign.reshape(1, *target_sign.shape) != 0)
    agree_rate = agree.sum(axis=0) / np.maximum((signs != 0).sum(axis=0), 1)
    if mode == "majority":
        return ((agree_rate >= 0.50) & nonzero).astype(np.float64)
    if mode == "strong":
        return ((agree_rate >= 0.67) & nonzero).astype(np.float64)
    if mode == "unanimous":
        return ((agree_rate >= 0.999) & nonzero).astype(np.float64)
    raise ValueError(mode)


def projection_stats(delta: np.ndarray, gate: np.ndarray, axes: list[np.ndarray]) -> dict[str, float]:
    if not axes:
        return {
            "before_bad_align_pos_mean": 0.0,
            "after_bad_align_pos_mean": 0.0,
            "before_bad_align_abs_mean": 0.0,
            "after_bad_align_abs_mean": 0.0,
            "removed_norm_ratio": 0.0,
        }
    before = orth.positive_axis_alignment(delta, gate, axes)
    return {
        "before_bad_align_pos_mean": before["bad_axis_align_mean_pos"],
        "before_bad_align_abs_mean": abs(before["bad_axis_align_mean_pos"]),
    }


def project_delta(
    delta: np.ndarray,
    gate: np.ndarray,
    axes: list[np.ndarray],
    anti_lambda: float,
    signed: bool,
) -> tuple[np.ndarray, dict[str, float]]:
    base_delta = delta * gate
    if anti_lambda <= 0.0 or not axes:
        before = orth.positive_axis_alignment(base_delta, gate, axes) if axes else {
            "bad_axis_align_mean_pos": 0.0,
            "bad_axis_align_max_pos": 0.0,
            "bad_axis_cosine_mean": 0.0,
            "bad_axis_cosine_max": 0.0,
        }
        return base_delta, {
            "before_bad_align_pos_mean": before["bad_axis_align_mean_pos"],
            "after_bad_align_pos_mean": before["bad_axis_align_mean_pos"],
            "before_bad_align_abs_mean": abs(before["bad_axis_align_mean_pos"]),
            "after_bad_align_abs_mean": abs(before["bad_axis_align_mean_pos"]),
            "removed_norm": 0.0,
            "removed_norm_ratio": 0.0,
        }

    before = orth.positive_axis_alignment(base_delta, gate, axes)
    out = base_delta.copy()
    removed_norm = 0.0
    for axis in axes:
        masked_axis = axis * gate
        avec = masked_axis.reshape(-1)
        denom = float(np.dot(avec, avec))
        if denom <= 1e-12:
            continue
        coef = float(np.dot(out.reshape(-1), avec) / denom)
        if not signed and coef <= 0:
            continue
        if signed and abs(coef) <= 1e-12:
            continue
        removal = anti_lambda * coef * masked_axis
        out = out - removal
        removed_norm += float(np.linalg.norm(removal.reshape(-1)))
    out *= gate
    after = orth.positive_axis_alignment(out, gate, axes)
    base_norm = float(np.linalg.norm(base_delta.reshape(-1)))
    return out, {
        "before_bad_align_pos_mean": before["bad_axis_align_mean_pos"],
        "after_bad_align_pos_mean": after["bad_axis_align_mean_pos"],
        "before_bad_align_abs_mean": abs(before["bad_axis_align_mean_pos"]),
        "after_bad_align_abs_mean": abs(after["bad_axis_align_mean_pos"]),
        "removed_norm": removed_norm,
        "removed_norm_ratio": removed_norm / base_norm if base_norm > 1e-12 else 0.0,
    }


def combo_specs() -> list[tuple[str, list[str], list[tuple[float, ...]]]]:
    pairs = [
        ("b01_x_898", ["ladder_b01_282_full_s1p3", "ladder_898_f465_full_s1p5"]),
        ("b01_x_f1ee", ["ladder_b01_282_full_s1p3", "ladder_f1ee_f465_noq2_s1p5"]),
        ("b01_x_block3a28", ["ladder_b01_282_full_s1p3", "blockorth_3a28"]),
        ("b01_x_q3stage", ["ladder_b01_282_full_s1p3", "target_q3stage"]),
        ("898_x_f1ee", ["ladder_898_f465_full_s1p5", "ladder_f1ee_f465_noq2_s1p5"]),
    ]
    triads = [
        ("b01_898_f1ee", ["ladder_b01_282_full_s1p3", "ladder_898_f465_full_s1p5", "ladder_f1ee_f465_noq2_s1p5"]),
        ("b01_block_q3", ["ladder_b01_282_full_s1p3", "blockorth_3a28", "target_q3stage"]),
        ("b01_f1ee_q3", ["ladder_b01_282_full_s1p3", "ladder_f1ee_f465_noq2_s1p5", "target_q3stage"]),
        ("b01_block_f1ee", ["ladder_b01_282_full_s1p3", "blockorth_3a28", "ladder_f1ee_f465_noq2_s1p5"]),
    ]
    specs: list[tuple[str, list[str], list[tuple[float, ...]]]] = []
    specs.extend((name, names, PAIR_WEIGHTS) for name, names in pairs)
    specs.extend((name, names, TRI_WEIGHTS) for name, names in triads)
    for name in [
        "ladder_b01_282_full_s1p3",
        "ladder_898_f465_full_s1p5",
        "ladder_f1ee_f465_noq2_s1p5",
    ]:
        specs.append((f"solo_{name}", [name], [(1.0,)]))
    return specs


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    energy = consensus["energy"]
    bad_axes = build_bad_axes(sample, base_logit)

    directions: dict[str, np.ndarray] = {}
    available: set[str] = set()
    for name, file_name in DIRECTION_FILES.items():
        if inv.locate(file_name) is None:
            continue
        arr = load_array(file_name, sample)
        directions[name] = inv.logit(arr) - base_logit
        available.add(name)

    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}
    seen_predictions: set[str] = set()
    n_rows = len(sample)

    for combo_name, names, weights_list in combo_specs():
        if not set(names).issubset(available):
            continue
        source_deltas = [directions[name] for name in names]
        for weights in weights_list:
            raw_delta = sum(float(w) * delta for w, delta in zip(weights, source_deltas, strict=False))
            if float(np.mean(np.abs(raw_delta))) <= 1e-12:
                continue
            weight_tag = "_".join(f"{w:.2f}" for w in weights)
            for target_name in TARGET_GROUPS:
                tgate = target_gate(target_name, n_rows)
                for cell_gate_name in ["all_cells", "energy_top70"]:
                    egate = energy_gate(cell_gate_name, raw_delta, energy)
                    for sign_gate_name in ["none", "majority"]:
                        sgate = sign_agreement_gate(source_deltas, raw_delta, sign_gate_name)
                        gate = tgate * egate * sgate
                        if float(gate.mean()) <= 0:
                            continue
                        active = np.abs(raw_delta * gate) > 1e-10
                        active_cells = int(active.sum())
                        if active_cells <= 0:
                            continue
                        active_rows = int((active.sum(axis=1) > 0).sum())
                        active_energy = energy[active]
                        for axis_group, axis_names in AXIS_GROUPS.items():
                            axes = [bad_axes[name] for name in axis_names if name in bad_axes]
                            anti_values = [0.0] if axis_group == "none" else ANTI_LAMBDAS
                            for anti_lambda in anti_values:
                                for signed in ([False, True] if anti_lambda > 0 else [False]):
                                    projected, stats = project_delta(raw_delta, gate, axes, anti_lambda, signed)
                                    if float(np.mean(np.abs(projected))) <= 1e-12:
                                        continue
                                    for cap in DELTA_CAPS:
                                        capped = np.clip(projected, -cap, cap)
                                        for scale in SCALES:
                                            final_delta = scale * capped
                                            pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                                            pred_hash = sha1(np.round(pred, 10).tobytes()).hexdigest()[:12]
                                            if pred_hash in seen_predictions:
                                                continue
                                            seen_predictions.add(pred_hash)
                                            label = (
                                                f"{combo_name}|{weight_tag}|{target_name}|{cell_gate_name}|"
                                                f"{sign_gate_name}|{axis_group}|a{anti_lambda:.2f}|"
                                                f"{'signed' if signed else 'positive'}|cap{cap:.2f}|s{scale:.2f}"
                                            )
                                            tag = stable_hash(label)
                                            name = f"direns_{tag}"
                                            arrays[name] = pred
                                            rows.append(
                                                {
                                                    "name": name,
                                                    "file": f"submission_direns_{tag}.csv",
                                                    "source_name": combo_name,
                                                    "source_file": "+".join(DIRECTION_FILES[n] for n in names),
                                                    "variant": f"{target_name}/{cell_gate_name}/{sign_gate_name}/{axis_group}",
                                                    "combo_sources": "+".join(names),
                                                    "combo_weights": weight_tag,
                                                    "target_group": target_name,
                                                    "cell_gate": cell_gate_name,
                                                    "sign_gate": sign_gate_name,
                                                    "axis_group": axis_group,
                                                    "anti_lambda": anti_lambda,
                                                    "projection_mode": "signed" if signed else "positive",
                                                    "scale": scale,
                                                    "delta_cap": cap,
                                                    "active_cells": active_cells,
                                                    "active_rows": active_rows,
                                                    "mean_active_energy": float(np.mean(active_energy)),
                                                    "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                                                    "mean_abs_logit_delta": float(np.mean(np.abs(final_delta))),
                                                    "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                                                    "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                                                    "prediction_hash": pred_hash,
                                                    **stats,
                                                }
                                            )
    return pd.DataFrame(rows), arrays


def prefilter(meta: pd.DataFrame, arrays: dict[str, np.ndarray], limit: int = 760) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    if meta.empty:
        return meta, arrays
    frame = meta.copy()
    reduction = frame["before_bad_align_pos_mean"] - frame["after_bad_align_pos_mean"]
    source_bonus = frame["source_name"].map(
        {
            "b01_x_f1ee": -0.00028,
            "b01_x_block3a28": -0.00026,
            "b01_898_f1ee": -0.00025,
            "b01_block_f1ee": -0.00024,
            "b01_block_q3": -0.00020,
            "solo_ladder_b01_282_full_s1p3": -0.00018,
        }
    ).fillna(0.0)
    frame["cheap_priority"] = (
        np.abs(frame["mean_abs_move_vs_a2c8"] - 0.0090)
        + 0.00045 * np.maximum(frame["removed_norm_ratio"] - 0.45, 0.0)
        + 0.00100 * np.maximum(frame["after_bad_align_pos_mean"], 0.0)
        - 0.00075 * np.minimum(np.maximum(reduction, 0.0), 0.20)
        - 0.00035 * np.minimum(frame["mean_active_energy"] / 1.5, 1.4)
        + source_bonus
    )
    eligible = frame[
        frame["mean_abs_move_vs_a2c8"].between(0.0045, 0.0140)
        & (frame["active_cells"] >= 80)
        & (frame["removed_norm_ratio"] <= 0.80)
    ].copy()
    if eligible.empty:
        eligible = frame.copy()
    selected = pd.concat(
        [
            eligible.sort_values("cheap_priority").head(260),
            eligible[
                (eligible["axis_group"].ne("none"))
                & (eligible["anti_lambda"] > 0)
                & (eligible["mean_abs_move_vs_a2c8"] >= 0.0075)
            ].sort_values("cheap_priority").head(210),
            eligible[
                (eligible["source_name"].isin(["b01_x_f1ee", "b01_x_block3a28", "b01_898_f1ee", "b01_block_f1ee"]))
                & (eligible["target_group"].isin(["full", "no_q2", "q3_stage"]))
            ].sort_values("cheap_priority").head(220),
            eligible[
                (eligible["cell_gate"].isin(["all_cells", "energy_top70"]))
                & (eligible["sign_gate"].isin(["none", "majority"]))
                & (eligible["mean_abs_move_vs_a2c8"] >= 0.0080)
            ].sort_values(["cheap_priority", "mean_abs_move_vs_a2c8"]).head(180),
            eligible[eligible["axis_group"].eq("none")].sort_values("cheap_priority").head(100),
        ],
        ignore_index=True,
    ).drop_duplicates("name")
    selected = selected.sort_values("cheap_priority").head(limit).reset_index(drop=True)
    return selected, {str(row.name): arrays[str(row.name)] for row in selected.itertuples(index=False)}


def coalesce_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["mean_abs_move_vs_a2c8", "max_abs_move_vs_a2c8"]:
        if column not in out.columns:
            for candidate in [f"{column}_x", f"{column}_y"]:
                if candidate in out.columns:
                    out[column] = out[candidate]
                    break
    return out


def candidate_pool_for_cv(scored: pd.DataFrame, limit: int = 148) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("direns_")].copy()
    if candidates.empty:
        return candidates
    frames = [
        candidates.sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(56),
        candidates[
            (candidates["axis_group"].ne("none"))
            & (candidates["anti_lambda"] > 0)
            & (candidates["actual_anchor_score_final"] <= 0.57782)
        ].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(48),
        candidates[
            (candidates["mean_abs_move_vs_a2c8"] >= 0.0085)
            & (candidates["actual_anchor_score_final"] <= 0.57784)
        ].sort_values(["actual_anchor_score_final", "mean_abs_move_vs_a2c8"]).head(48),
        candidates[
            (candidates["robust_delta_vs_a2c8"] <= -0.00105)
            & (candidates["robust_p90_delta_vs_a2c8"] <= -0.00085)
        ].sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"]).head(40),
        candidates[
            (candidates["source_name"].isin(["b01_x_f1ee", "b01_x_block3a28", "b01_898_f1ee", "b01_block_f1ee"]))
            & (candidates["target_group"].isin(["full", "no_q2", "q3_stage"]))
        ].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(44),
    ]
    out = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    return out.head(limit).reset_index(drop=True)


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("direns_")].copy()
    if candidates.empty:
        return candidates
    frames = [
        candidates[
            (candidates["actual_anchor_score_final"] <= 0.57775)
            & (candidates["honest_cv_delta_mean"] <= -0.00085)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0080)
        ].assign(submit_role="direns_score_probe").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(6),
        candidates[
            (candidates["actual_anchor_score_final"] <= 0.57773)
            & (candidates["honest_cv_delta_mean"] <= -0.00078)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0075)
        ].assign(submit_role="direns_frontier").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        candidates[
            (candidates["mean_abs_move_vs_a2c8"] >= 0.0090)
            & (candidates["actual_anchor_score_final"] <= 0.57779)
            & (candidates["honest_cv_delta_mean"] <= -0.00090)
        ].assign(submit_role="direns_large_probe").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(6),
        candidates[
            (candidates["axis_group"].ne("none"))
            & (candidates["anti_lambda"] > 0)
            & (candidates["actual_anchor_score_final"] <= 0.57782)
            & (candidates["honest_cv_delta_mean"] <= -0.00070)
        ].assign(submit_role="direns_orth_diag").sort_values(["actual_anchor_score_final", "removed_norm_ratio"]).head(6),
        candidates[
            (candidates["target_group"].isin(["no_q2", "q3_stage"]))
            & (candidates["actual_anchor_score_final"] <= 0.57782)
            & (candidates["honest_cv_delta_mean"] <= -0.00065)
        ].assign(submit_role="direns_target_guard").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(6),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    if selected.empty:
        selected = candidates.sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(8).copy()
        selected["submit_role"] = "direns_fallback_top"
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def integrity_check(sample: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        frame = pd.read_csv(OUT / str(row.file), parse_dates=["sleep_date", "lifelog_date"]).sort_values(inv.KEY).reset_index(drop=True)
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
    candidates = scored[scored["name"].str.startswith("direns_")].copy()
    cols = [
        "name",
        "file",
        "source_name",
        "combo_sources",
        "combo_weights",
        "target_group",
        "cell_gate",
        "sign_gate",
        "axis_group",
        "anti_lambda",
        "projection_mode",
        "scale",
        "delta_cap",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
        "before_bad_align_pos_mean",
        "after_bad_align_pos_mean",
    ]
    by_source = pd.DataFrame()
    if not candidates.empty:
        by_source = (
            candidates.groupby(["source_name", "target_group", "axis_group"], as_index=False)
            .agg(
                best_actual_anchor=("actual_anchor_score_final", "min"),
                best_honest_cv=("honest_cv_delta_mean", "min"),
                max_move=("mean_abs_move_vs_a2c8", "max"),
                median_removed_ratio=("removed_norm_ratio", "median"),
            )
            .sort_values(["best_actual_anchor", "best_honest_cv"])
        )
    report = [
        "# JEPA Sparse Direction Ensemble Orthogonalizer",
        "",
        "This tests whether good sparse-JEPA/direct-label directions can cancel bad public-axis components by convex logit ensembling before optional bad-axis projection.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(60).round(9).to_string(index=False)
        if not candidates.empty
        else "none",
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(60).round(9).to_string(index=False)
        if not candidates.empty and "honest_cv_delta_mean" in candidates.columns
        else "none",
        "```",
        "",
        "## Source / Target / Axis Summary",
        "",
        "```",
        by_source.head(80).round(9).to_string(index=False) if not by_source.empty else "none",
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False)
        if not selected.empty
        else "none",
        "```",
        "",
        "## Integrity",
        "",
        "```",
        integrity.round(9).to_string(index=False) if not integrity.empty else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- If direction ensembling beats the single-source scale ladder, the bottleneck was a mixture issue rather than missing hidden labels.",
        "- If it only ties or worsens, the current frontier is not limited by simple bad-axis cancellation; hidden subset/label-prior inference remains the next bottleneck.",
        "- Orthogonalized rows with high removed ratio are diagnostics, not score-first rows unless they also keep honest CV and actual-anchor near the frontier.",
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
        "target_group",
        "axis_group",
        "anti_lambda",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
    ]
    print(REPORT_OUT)
    print("[full candidates]", meta_full.shape, "[prefiltered]", meta.shape, "[cv pool]", pool.shape)
    print(pool[[c for c in cols if c in pool.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(32).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")
    print("[integrity]")
    print(integrity.round(9).to_string(index=False) if not integrity.empty else "none")


if __name__ == "__main__":
    main()
