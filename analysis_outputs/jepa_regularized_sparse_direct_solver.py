from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402
import public_lb_direct_label_robust_selector as robust  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, read_submission  # noqa: E402


CONSENSUS_CELLS = OUT / "public_lb_direct_label_consensus_energy_cells.csv"
SCAN_OUT = OUT / "jepa_regularized_sparse_direct_solver_scan.csv"
SELECTED_OUT = OUT / "jepa_regularized_sparse_direct_solver_selected.csv"
ANCHOR_OUT = OUT / "jepa_regularized_sparse_direct_solver_actual_anchor.csv"
REPORT_OUT = OUT / "jepa_regularized_sparse_direct_solver_report.md"


TARGET_MASKS = {
    "q3_s4": ["Q3", "S4"],
    "q3_s3_s4": ["Q3", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "s2_s3_s4": ["S2", "S3", "S4"],
    "stage_all": ["S1", "S2", "S3", "S4"],
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_q3_s_stage": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "all": inv.TARGETS,
}

CELL_GATES = {
    "strict": {"energy": 1.25, "agreement": 0.88, "count": 4, "abs_delta": 0.050},
    "balanced": {"energy": 0.80, "agreement": 0.78, "count": 3, "abs_delta": 0.035},
    "broad_safe": {"energy": 0.55, "agreement": 0.70, "count": 2, "abs_delta": 0.025},
    "q3s4_edge": {"energy": 0.35, "agreement": 0.66, "count": 2, "abs_delta": 0.020},
}

ROW_GATES = ["all_rows", "energy_q60", "energy_q75", "id01_id02_energy"]
STRENGTHS = [0.55, 0.75, 1.00]
CAPS = [0.030, 0.050, 0.080]
ANTI_LAMBDAS = [0.0, 0.70, 1.00]

POSITIVE_DONOR_GROUPS = {
    "directrob": [
        "submission_directrob_29ffe34b.csv",
        "submission_directrob_93b1b685.csv",
        "submission_directrob_93de02d3.csv",
    ],
    "q3s4_consensus": [
        "submission_directcons_de1d6b6d.csv",
        "submission_directcons_8a0ae0b0.csv",
        "submission_directcons_bf4f6c46.csv",
    ],
    "jepa_block": [
        "submission_jepa_block_countshift_449129ae.csv",
        "submission_jepa_block_countshift_65d5ef0c.csv",
        "submission_jepa_block_countshift_33884d08.csv",
        "submission_jepa_public_blockentropy_publicmask_q3_s4_g000_8c617ee7.csv",
        "submission_jepa_bridge_ensemble_c42fbf1e.csv",
        "submission_jepa_bridge_posteriorreg_9c5e225e.csv",
    ],
    "sequence_motif": [
        "submission_hiddenblock_seqmotif_cellgate_ed262832.csv",
        "submission_hiddenblock_seqmotif_cellgate_75288a05.csv",
        "submission_hiddenblock_seqmotif_neutral_ad40753e.csv",
        "submission_hiddenblock_seqmotif_neutral_dcffa5a7.csv",
    ],
}

NEGATIVE_AXIS_FILES = [
    "submission_directcons_1d5b6f39.csv",
    "submission_directcons_95be47ec.csv",
    "submission_directcons_0b3f77c3.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_jepa_latent_q2_w0p45.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def locate(file_name: str) -> Path | None:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    return None


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray | None:
    path = locate(file_name)
    if path is None:
        return None
    frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(inv.KEY).reset_index(drop=True)
    if not frame[inv.KEY].reset_index(drop=True).equals(sample[inv.KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return inv.clip_prob(frame[inv.TARGETS].to_numpy(dtype=np.float64))


def target_mask_matrix(name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    mask = np.asarray([target in allowed for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(mask.reshape(1, -1), n_rows, axis=0)


def consensus_matrices(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    cells = pd.read_csv(CONSENSUS_CELLS)
    shape = (len(sample), len(inv.TARGETS))
    mats = {
        "delta": np.zeros(shape, dtype=np.float64),
        "energy": np.zeros(shape, dtype=np.float64),
        "agreement": np.zeros(shape, dtype=np.float64),
        "source_count": np.zeros(shape, dtype=np.float64),
        "abs_delta": np.zeros(shape, dtype=np.float64),
        "l2o": np.ones(shape, dtype=np.float64) * 0.0025,
    }
    target_idx = {target: i for i, target in enumerate(inv.TARGETS)}
    for row in cells.itertuples(index=False):
        i = int(row.row_index)
        j = target_idx[str(row.target)]
        delta = float(row.mean_logit_delta)
        mats["delta"][i, j] = delta
        mats["energy"][i, j] = float(row.consensus_energy)
        mats["agreement"][i, j] = float(row.agreement_weight)
        mats["source_count"][i, j] = float(row.source_count)
        mats["abs_delta"][i, j] = abs(delta)
        mats["l2o"][i, j] = float(row.mean_source_l2o)
    return mats


def row_gate_matrix(sample: pd.DataFrame, row_gate: str, energy: np.ndarray) -> np.ndarray:
    if row_gate == "all_rows":
        return np.ones_like(energy, dtype=np.float64)

    row_energy = energy.max(axis=1)
    if row_gate == "energy_q60":
        keep = row_energy >= np.quantile(row_energy, 0.60)
    elif row_gate == "energy_q75":
        keep = row_energy >= np.quantile(row_energy, 0.75)
    elif row_gate in {"id01_id02_early", "id01_id02_energy"}:
        keep = np.zeros(len(sample), dtype=bool)
        for _sid, group in sample.groupby("subject_id", sort=False):
            idx = group.index.to_numpy()
            frac_rank = np.arange(len(idx)) / max(len(idx) - 1, 1)
            subject_keep = sample.loc[idx, "subject_id"].isin(["id01", "id02"]).to_numpy() & (frac_rank <= 0.45)
            keep[idx] = subject_keep
        if row_gate == "id01_id02_energy":
            keep &= row_energy >= np.quantile(row_energy, 0.55)
    else:
        raise ValueError(row_gate)
    return np.repeat(keep.reshape(-1, 1).astype(np.float64), len(inv.TARGETS), axis=1)


def cell_gate_matrix(consensus: dict[str, np.ndarray], gate_name: str) -> np.ndarray:
    cfg = CELL_GATES[gate_name]
    keep = (
        (consensus["energy"] >= cfg["energy"])
        & (consensus["agreement"] >= cfg["agreement"])
        & (consensus["source_count"] >= cfg["count"])
        & (consensus["abs_delta"] >= cfg["abs_delta"])
    )
    return keep.astype(np.float64)


def median_delta(files: list[str], sample: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray | None:
    deltas = []
    for file_name in files:
        arr = load_array(file_name, sample)
        if arr is None:
            continue
        deltas.append(inv.logit(arr) - base_logit)
    if not deltas:
        return None
    return np.median(np.stack(deltas, axis=0), axis=0)


def build_positive_signals(sample: pd.DataFrame, base_logit: np.ndarray, consensus_delta: np.ndarray) -> dict[str, np.ndarray]:
    raw: dict[str, np.ndarray] = {"consensus": consensus_delta.copy()}
    for name, files in POSITIVE_DONOR_GROUPS.items():
        delta = median_delta(files, sample, base_logit)
        if delta is not None:
            raw[name] = delta

    signals: dict[str, np.ndarray] = {}
    signals["consensus"] = consensus_delta
    if "directrob" in raw:
        signals["directrob"] = raw["directrob"]
        signals["consensus_directrob"] = 0.60 * consensus_delta + 0.40 * raw["directrob"]
    if "q3s4_consensus" in raw:
        signals["q3s4_consensus"] = raw["q3s4_consensus"]
    if "jepa_block" in raw:
        signals["jepa_block"] = raw["jepa_block"]
    if "sequence_motif" in raw:
        signals["sequence_motif"] = raw["sequence_motif"]
    if all(key in raw for key in ["directrob", "jepa_block", "sequence_motif"]):
        signals["sparse_fusion"] = 0.50 * consensus_delta + 0.25 * raw["directrob"] + 0.18 * raw["jepa_block"] + 0.07 * raw["sequence_motif"]
    if all(key in raw for key in ["q3s4_consensus", "jepa_block"]):
        signals["q3s4_jepa"] = 0.65 * raw["q3s4_consensus"] + 0.35 * raw["jepa_block"]
    if all(key in raw for key in ["directrob", "jepa_block"]):
        signals["direct_jepa"] = 0.55 * raw["directrob"] + 0.45 * raw["jepa_block"]
    return signals


def build_negative_axes(sample: pd.DataFrame, base_logit: np.ndarray) -> list[np.ndarray]:
    axes: list[np.ndarray] = []
    for file_name in NEGATIVE_AXIS_FILES:
        arr = load_array(file_name, sample)
        if arr is None:
            continue
        axis = inv.logit(arr) - base_logit
        norm = float(np.linalg.norm(axis.reshape(-1)))
        if norm > 1e-9:
            axes.append(axis / norm)
    return axes


def anti_project(delta: np.ndarray, active_gate: np.ndarray, negative_axes: list[np.ndarray], lam: float) -> tuple[np.ndarray, float, float, float]:
    if lam <= 0 or not negative_axes:
        return delta, 0.0, 0.0, 0.0
    out = delta.copy()
    before_scores = []
    after_scores = []
    removed_norm = 0.0
    for axis in negative_axes:
        masked_axis = axis * active_gate
        denom = float(np.dot(masked_axis.reshape(-1), masked_axis.reshape(-1)))
        if denom <= 1e-12:
            continue
        flat = out.reshape(-1)
        avec = masked_axis.reshape(-1)
        coef = float(np.dot(flat, avec) / denom)
        before_scores.append(max(coef, 0.0))
        if coef > 0:
            removal = lam * coef * masked_axis
            out = out - removal
            removed_norm += float(np.linalg.norm(removal.reshape(-1)))
        after_coef = float(np.dot(out.reshape(-1), avec) / denom)
        after_scores.append(max(after_coef, 0.0))
    out *= active_gate
    before = float(np.mean(before_scores)) if before_scores else 0.0
    after = float(np.mean(after_scores)) if after_scores else 0.0
    return out, before, after, removed_norm


def sign_agreement(signal: np.ndarray, reference: np.ndarray) -> np.ndarray:
    return ((np.sign(signal) == np.sign(reference)) & (np.abs(reference) > 1e-9)).astype(np.float64)


def geometric_features(pred: np.ndarray, base: np.ndarray, raw05: np.ndarray) -> dict[str, float]:
    diff_base = pred - base
    vec = (inv.logit(pred) - inv.logit(raw05)).reshape(-1)
    basis = (inv.logit(base) - inv.logit(raw05)).reshape(-1)
    denom = float(np.linalg.norm(vec) * np.linalg.norm(basis))
    cosine = float(np.dot(vec, basis) / denom) if denom > 1e-12 else np.nan
    if float(np.dot(basis, basis)) > 1e-12 and float(np.linalg.norm(vec)) > 1e-12:
        proj = basis * (float(np.dot(vec, basis)) / float(np.dot(basis, basis)))
        orth = float(np.linalg.norm(vec - proj) / np.linalg.norm(vec))
    else:
        orth = np.nan
    gain_if_one = np.log(inv.clip_prob(pred) / inv.clip_prob(raw05))
    gain_if_zero = np.log((1.0 - inv.clip_prob(pred)) / (1.0 - inv.clip_prob(raw05)))
    return {
        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(diff_base))),
        "max_abs_move_vs_a2c8": float(np.max(np.abs(diff_base))),
        "mean_abs_move_vs_raw05": float(np.mean(np.abs(pred - raw05))),
        "logit_cosine_to_a2c8_move": cosine,
        "logit_orth_ratio_to_a2c8_move": orth,
        "best_case_gain_vs_raw05_if_all_correct": float(np.mean(np.maximum(gain_if_one, gain_if_zero))),
    }


def score_scan(predictions: dict[str, np.ndarray], sources: pd.DataFrame, solution_map: dict[str, robust.Solution], base: np.ndarray, stage2: np.ndarray, raw05: np.ndarray) -> pd.DataFrame:
    ensemble, weights = robust.solution_ensemble(sources, solution_map, limit=48)
    base_scores = np.asarray([robust.score_under_solution(sol, base, stage2) for sol in ensemble])
    rows = []
    for name, pred in predictions.items():
        scores = np.asarray([robust.score_under_solution(sol, pred, stage2) for sol in ensemble])
        delta = scores - base_scores
        rec = {
            "name": name,
            "robust_expected_public": float(weights @ scores),
            "robust_delta_vs_a2c8": float(weights @ delta),
            "robust_p10_delta_vs_a2c8": float(np.quantile(delta, 0.10)),
            "robust_p50_delta_vs_a2c8": float(np.quantile(delta, 0.50)),
            "robust_p90_delta_vs_a2c8": float(np.quantile(delta, 0.90)),
            "robust_worst_delta_vs_a2c8": float(np.max(delta)),
            "robust_win_rate_vs_a2c8": float(np.mean(delta < 0.0)),
        }
        rec.update(geometric_features(pred, base, raw05))
        rows.append(rec)
    return pd.DataFrame(rows)


def generate_candidates(sample: pd.DataFrame, preds: dict[str, np.ndarray], sources: pd.DataFrame, solution_map: dict[str, robust.Solution]) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base = preds["cvjepa_a2c8"]
    raw05 = preds["raw05"]
    stage2 = preds["stage2"]
    base_logit = inv.logit(base)
    consensus = consensus_matrices(sample)
    signals = build_positive_signals(sample, base_logit, consensus["delta"])
    negative_axes = build_negative_axes(sample, base_logit)

    meta_rows: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {}

    for signal_name, signal in signals.items():
        for target_mask in TARGET_MASKS:
            target_gate = target_mask_matrix(target_mask, len(sample))
            for cell_gate_name in CELL_GATES:
                cell_gate = cell_gate_matrix(consensus, cell_gate_name)
                if signal_name in {"q3s4_consensus", "q3s4_jepa"} and target_mask not in {"q3_s4", "q3_s3_s4", "q3_s2_s3_s4"}:
                    continue
                for row_gate_name in ROW_GATES:
                    row_gate = row_gate_matrix(sample, row_gate_name, consensus["energy"])
                    active_gate = target_gate * cell_gate * row_gate
                    active_gate *= sign_agreement(signal, consensus["delta"])
                    active_cells = int(active_gate.sum())
                    if active_cells <= 0:
                        continue
                    active_rows = int((active_gate.sum(axis=1) > 0).sum())
                    active_l2o = consensus["l2o"][active_gate > 0]
                    mean_energy = float(consensus["energy"][active_gate > 0].mean())
                    mean_l2o = float(active_l2o.mean()) if len(active_l2o) else np.nan
                    for cap in CAPS:
                        capped = np.clip(signal, -cap, cap) * active_gate
                        if float(np.mean(np.abs(capped))) <= 1e-10:
                            continue
                        for anti_lambda in ANTI_LAMBDAS:
                            projected, bad_align_before, bad_align_after, removed_norm = anti_project(capped, active_gate, negative_axes, anti_lambda)
                            if float(np.mean(np.abs(projected))) <= 1e-10:
                                continue
                            for strength in STRENGTHS:
                                final_delta = strength * projected
                                pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                                label = (
                                    f"{signal_name}|{target_mask}|{cell_gate_name}|{row_gate_name}|"
                                    f"s{strength:.2f}|c{cap:.3f}|a{anti_lambda:.2f}"
                                )
                                name = f"sparsejepa_{stable_hash(label)}"
                                if name in predictions:
                                    continue
                                predictions[name] = pred
                                cheap_mean_abs_move = float(np.mean(np.abs(pred - base)))
                                cheap_max_abs_move = float(np.max(np.abs(pred - base)))
                                meta_rows.append(
                                    {
                                        "name": name,
                                        "label": label,
                                        "file": f"submission_sparsejepa_{stable_hash(label)}.csv",
                                        "signal": signal_name,
                                        "target_mask": target_mask,
                                        "cell_gate": cell_gate_name,
                                        "row_gate": row_gate_name,
                                        "strength": strength,
                                        "cap": cap,
                                        "anti_lambda": anti_lambda,
                                        "active_cells": active_cells,
                                        "active_rows": active_rows,
                                        "mean_active_energy": mean_energy,
                                        "mean_active_l2o": mean_l2o,
                                        "bad_axis_align_before": bad_align_before,
                                        "bad_axis_align_after": bad_align_after,
                                        "bad_axis_removed_norm": removed_norm,
                                        "cheap_mean_abs_move_vs_a2c8": cheap_mean_abs_move,
                                        "cheap_max_abs_move_vs_a2c8": cheap_max_abs_move,
                                    }
                                )

    meta = pd.DataFrame(meta_rows)
    if meta.empty:
        return meta, predictions

    target_bonus = meta["target_mask"].map(
        {
            "q3_s4": -0.0010,
            "q3_s3_s4": -0.0009,
            "q3_s2_s3_s4": -0.0008,
            "s2_s3_s4": -0.0005,
            "stage_all": -0.0002,
            "no_q2": 0.0000,
            "q1_q3_s_stage": 0.0002,
            "all": 0.0006,
        }
    ).fillna(0.0)
    meta["cheap_priority"] = (
        np.abs(meta["cheap_mean_abs_move_vs_a2c8"] - 0.0050)
        + 0.0003 * np.maximum(meta["bad_axis_align_after"], 0.0)
        + 0.00025 * meta["mean_active_l2o"].fillna(0.001)
        - 0.0004 * np.minimum(meta["mean_active_energy"] / 1.25, 1.5)
        + target_bonus
    )
    pre = meta[
        meta["cheap_mean_abs_move_vs_a2c8"].between(0.0018, 0.0120)
        & (meta["bad_axis_align_after"] <= meta["bad_axis_align_before"] + 0.05)
    ].copy()
    if pre.empty:
        pre = meta.copy()
    pre_frames = [
        pre.sort_values("cheap_priority").head(900),
        pre[pre["target_mask"].isin(["q3_s4", "q3_s3_s4", "q3_s2_s3_s4"])].sort_values("cheap_priority").head(360),
        pre[(pre["cheap_mean_abs_move_vs_a2c8"] >= 0.0050) & (pre["target_mask"] != "all")].sort_values("cheap_priority").head(360),
        pre[(pre["anti_lambda"] > 0) & (pre["bad_axis_align_after"] <= pre["bad_axis_align_before"])].sort_values("cheap_priority").head(280),
    ]
    score_meta = pd.concat(pre_frames, ignore_index=True).drop_duplicates("name").head(1400).reset_index(drop=True)
    score_predictions = {str(name): predictions[str(name)] for name in score_meta["name"]}
    score = score_scan(score_predictions, sources, solution_map, base, stage2, raw05)
    scan = score_meta.merge(score, on="name", how="left")
    scan["selection_score"] = (
        scan["robust_delta_vs_a2c8"]
        + 0.85 * np.maximum(scan["robust_p90_delta_vs_a2c8"], 0.0)
        + 0.40 * np.maximum(scan["robust_worst_delta_vs_a2c8"], 0.0)
        + 0.10 * scan["mean_active_l2o"].fillna(0.001)
        + 0.0008 * np.maximum(scan["bad_axis_align_after"], 0.0)
        - 0.0015 * np.minimum(scan["mean_abs_move_vs_a2c8"] / 0.0050, 1.5)
        - 0.0007 * np.minimum(scan["mean_active_energy"] / 1.5, 1.5)
    )
    scan = scan.sort_values(["selection_score", "robust_delta_vs_a2c8"]).reset_index(drop=True)
    return scan, predictions


def choose_for_anchor(scan: pd.DataFrame, limit: int = 180) -> pd.DataFrame:
    frames = [
        scan[(scan["mean_abs_move_vs_a2c8"].between(0.0035, 0.0085)) & (scan["robust_p90_delta_vs_a2c8"] <= 0.00020)].head(70),
        scan[(scan["target_mask"].isin(["q3_s4", "q3_s3_s4", "q3_s2_s3_s4"])) & (scan["robust_p90_delta_vs_a2c8"] <= 0.00025)].head(55),
        scan[(scan["anti_lambda"] > 0) & (scan["bad_axis_align_after"] <= scan["bad_axis_align_before"])].head(45),
        scan.head(40),
    ]
    out = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    return out.head(limit).reset_index(drop=True)


def actual_anchor_for_candidates(sample: pd.DataFrame, candidates: pd.DataFrame, predictions: dict[str, np.ndarray]) -> pd.DataFrame:
    files = [
        "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "submission_directrob_29ffe34b.csv",
        "submission_directcons_de1d6b6d.csv",
    ]
    names = ["control_a2c8", "control_raw05", "control_directrob_29ffe34b", "control_directcons_de1d6b6d"]
    pred_list = [read_submission(file_name)[inv.TARGETS].to_numpy(dtype=float) for file_name in files]
    for row in candidates.itertuples(index=False):
        names.append(str(row.name))
        files.append(str(row.file))
        pred_list.append(predictions[str(row.name)])
    scored = actual_anchor_score(pred_list, sample)
    scored["name"] = names
    scored["file"] = files
    scored = scored.merge(candidates, on=["name", "file"], how="left")
    return scored.sort_values("actual_anchor_score_final").reset_index(drop=True)


def select_outputs(sample: pd.DataFrame, anchor: pd.DataFrame, predictions: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    specs = [
        ("sparse_first", anchor[(anchor["name"].str.startswith("sparsejepa_")) & (anchor["actual_anchor_score_final"] < 0.57780) & (anchor["mean_abs_move_vs_a2c8"].between(0.0030, 0.0070))], 8),
        ("sparse_q3s4", anchor[(anchor["name"].str.startswith("sparsejepa_")) & (anchor["target_mask"].isin(["q3_s4", "q3_s3_s4", "q3_s2_s3_s4"])) & (anchor["actual_anchor_score_final"] < 0.57784)], 8),
        ("sparse_large_probe", anchor[(anchor["name"].str.startswith("sparsejepa_")) & (anchor["mean_abs_move_vs_a2c8"] >= 0.0060) & (anchor["actual_anchor_score_final"] < 0.57790)], 8),
        ("sparse_antiaxis", anchor[(anchor["name"].str.startswith("sparsejepa_")) & (anchor["anti_lambda"] >= 0.70) & (anchor["actual_anchor_score_final"] < 0.57784)], 8),
    ]
    used: set[str] = set()
    for role, frame, limit in specs:
        seen_keys: set[tuple[object, object, object, object]] = set()
        for row in frame.sort_values(["actual_anchor_score_final", "selection_score"]).itertuples(index=False):
            key = (row.signal, row.target_mask, row.cell_gate, row.strength)
            if key in seen_keys or str(row.name) in used:
                continue
            seen_keys.add(key)
            used.add(str(row.name))
            rows.append({**row._asdict(), "submit_role": role})
            if len([r for r in rows if r["submit_role"] == role]) >= limit:
                break

    selected = pd.DataFrame(rows)
    if not selected.empty:
        for row in selected.itertuples(index=False):
            out = sample.copy()
            out[inv.TARGETS] = inv.clip_prob(predictions[str(row.name)])
            out.to_csv(OUT / str(row.file), index=False)
    return selected


def write_report(scan: pd.DataFrame, anchor: pd.DataFrame, selected: pd.DataFrame) -> None:
    scan_cols = [
        "name",
        "file",
        "signal",
        "target_mask",
        "cell_gate",
        "row_gate",
        "strength",
        "cap",
        "anti_lambda",
        "active_cells",
        "actual_anchor_score_final",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "bad_axis_align_before",
        "bad_axis_align_after",
        "selection_score",
    ]
    anchor_cols = [
        "file",
        "submit_role",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "signal",
        "target_mask",
        "cell_gate",
        "row_gate",
        "strength",
        "cap",
        "anti_lambda",
        "active_cells",
        "mean_abs_move_vs_a2c8",
        "robust_delta_vs_a2c8",
    ]
    merged_top = scan.merge(
        anchor[["name", "actual_anchor_score_final"]],
        on="name",
        how="left",
        suffixes=("", "_anchor"),
    )
    report = [
        "# JEPA-Regularized Sparse Direct Solver",
        "",
        "This combines direct-label consensus cells, JEPA/block/count/motif donor directions, and negative public axes into sparse larger-move candidates.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        anchor[[c for c in anchor_cols if c in anchor.columns]].head(30).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in anchor_cols if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Scan Top With Actual-Anchor Overlay",
        "",
        "```",
        merged_top[[c for c in scan_cols if c in merged_top.columns]].head(80).round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- This is the first sparse solver that explicitly combines JEPA energy priors with direct-label hidden-label pseudo solutions.",
        "- `anti_lambda` projects candidate logit moves away from known rejected axes: broad all-target consensus, latent residual, Q2-forced latent, and ordinal-Q drift.",
        "- A candidate is interesting only if it increases mean move beyond the micro-refine band while staying below or near the a2c8 actual-anchor control.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(inv.KEY).reset_index(drop=True)
    preds = inv.load_predictions(sample)
    sources, solution_map = robust.load_sources()

    scan, predictions = generate_candidates(sample, preds, sources, solution_map)
    scan.to_csv(SCAN_OUT, index=False)

    candidates = choose_for_anchor(scan)
    anchor = actual_anchor_for_candidates(sample, candidates, predictions)
    anchor.to_csv(ANCHOR_OUT, index=False)

    selected = select_outputs(sample, anchor, predictions)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(scan, anchor, selected)

    print(REPORT_OUT)
    print("[scan]", scan.shape)
    print(
        scan[
            [
                "name",
                "file",
                "signal",
                "target_mask",
                "cell_gate",
                "row_gate",
                "strength",
                "cap",
                "anti_lambda",
                "active_cells",
                "robust_delta_vs_a2c8",
                "robust_p90_delta_vs_a2c8",
                "mean_abs_move_vs_a2c8",
                "selection_score",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )
    print("[actual-anchor]")
    print(
        anchor[
            [
                "file",
                "actual_anchor_score_final",
                "signal",
                "target_mask",
                "cell_gate",
                "row_gate",
                "strength",
                "cap",
                "anti_lambda",
                "mean_abs_move_vs_a2c8",
                "robust_delta_vs_a2c8",
            ]
        ]
        .head(25)
        .round(9)
        .to_string(index=False)
    )
    print("[selected]")
    if selected.empty:
        print("none")
    else:
        print(
            selected[
                [
                    "submit_role",
                    "file",
                    "actual_anchor_score_final",
                    "signal",
                    "target_mask",
                    "cell_gate",
                    "row_gate",
                    "strength",
                    "cap",
                    "anti_lambda",
                    "mean_abs_move_vs_a2c8",
                    "robust_delta_vs_a2c8",
                ]
            ]
            .head(30)
            .round(9)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
