#!/usr/bin/env python3
"""Energy-Utility Assignment Solver for HS-JEPA.

This experiment turns route consistency from a post-hoc veto into an assignment
solver.  Candidate actions are proposed by the public-loss sparse tomography
support field, then accepted only when expected public utility and target-route
energy agree.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "energy_utility_assignment_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"
ROUTE_ENERGY_MODULE = HERE / "route_consistency_energy.py"
SUPPORT_FILES = [
    "submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv",
    "submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv",
    "submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv",
]


@dataclass(frozen=True)
class SolverConfig:
    name: str
    max_cells: int
    max_cells_per_row: int
    max_cells_per_target: int
    min_stability: float
    max_h088_alignment: float
    min_listener_support: int
    action_amp: float
    max_logit_step: float
    min_public_utility: float
    max_energy_delta: float
    energy_penalty: float
    route_bonus: float


CONFIGS = [
    SolverConfig(
        name="balanced",
        max_cells=84,
        max_cells_per_row=2,
        max_cells_per_target=32,
        min_stability=0.56,
        max_h088_alignment=0.66,
        min_listener_support=1,
        action_amp=1.15,
        max_logit_step=1.25,
        min_public_utility=1.0e-5,
        max_energy_delta=0.0042,
        energy_penalty=0.060,
        route_bonus=0.018,
    ),
    SolverConfig(
        name="jackpot",
        max_cells=126,
        max_cells_per_row=3,
        max_cells_per_target=46,
        min_stability=0.48,
        max_h088_alignment=0.74,
        min_listener_support=1,
        action_amp=1.35,
        max_logit_step=1.55,
        min_public_utility=4.0e-6,
        max_energy_delta=0.0064,
        energy_penalty=0.045,
        route_bonus=0.022,
    ),
]


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "energy_utility_candidate1")
route_energy = import_module(ROUTE_ENERGY_MODULE, "energy_utility_route_energy")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def write_submission(path: Path, sample: pd.DataFrame, prob: np.ndarray) -> None:
    out = sample[KEYS].copy()
    for idx, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, idx])
    out.to_csv(path, index=False)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    keys_match = df[KEYS].equals(sample[KEYS])
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(keys_match),
        "duplicate_keys": int(df[KEYS].duplicated().sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def target_energy_tolerance(target: str, config: SolverConfig) -> float:
    if target == "Q2":
        return config.max_energy_delta * 1.35
    if target == "S2":
        return config.max_energy_delta * 1.55
    if target in {"S1", "S3", "S4"}:
        return config.max_energy_delta * 0.80
    return config.max_energy_delta


def target_magnitude_scale(target: str) -> float:
    if target == "Q2":
        return 1.10
    if target == "S2":
        return 1.08
    if target in {"S1", "S3", "S4"}:
        return 0.84
    return 1.00


def build_public_support(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, object]:
    support_moves = {}
    for name in SUPPORT_FILES:
        move = candidate1.movement_from_file(name, sample, base_logit)
        if move is None:
            raise FileNotFoundError(name)
        support_moves[name] = move
    support_idx = np.flatnonzero(
        np.any(np.vstack([np.abs(move) > TOL for move in support_moves.values()]), axis=0)
    )
    x, y, public_files = candidate1.public_observed_matrix(sample, base_logit, support_idx)
    coef, stability, ridge_diag = candidate1.ridge_public_loss_coefficients(x, y, alpha=10.0)
    listener = candidate1.listener_support()
    return {
        "support_moves": support_moves,
        "support_idx": support_idx,
        "coef": coef,
        "stability": stability,
        "ridge_diag": ridge_diag,
        "public_files": public_files,
        "listener": listener,
    }


def proposal_pool(public_support: dict[str, object]) -> pd.DataFrame:
    support_idx = public_support["support_idx"]
    coef = public_support["coef"]
    stability = public_support["stability"]
    listener = public_support["listener"]
    denom = float(np.percentile(np.abs(coef), 90) + 1e-9)
    rows = []
    for local_idx, flat in enumerate(support_idx):
        coef_value = float(coef[local_idx])
        if abs(coef_value) < 1e-10:
            continue
        sign = int(-np.sign(coef_value))
        rec = listener.get((int(flat), sign))
        if rec is None:
            continue
        target = TARGETS[int(flat) % len(TARGETS)]
        magnitude_base = 0.11 + abs(coef_value) / denom
        public_utility = abs(coef_value) * magnitude_base
        rows.append(
            {
                "flat_idx": int(flat),
                "row": int(flat) // len(TARGETS),
                "target": target,
                "sign": sign,
                "coef": coef_value,
                "stability": float(stability[local_idx]),
                "source_support": int(rec["source_support"]),
                "semantic_mean": float(rec["sem_mean"]),
                "base_mean": float(rec["base_mean"]),
                "h088_alignment": float(rec["h088_alignment"]),
                "listener_score": float(rec["score"]),
                "public_utility_base": float(public_utility),
                "magnitude_base": float(magnitude_base),
            }
        )
    pool = pd.DataFrame(rows)
    if len(pool):
        pool["rank_seed_score"] = (
            pool["public_utility_base"]
            * (0.40 + pool["stability"])
            * (1.0 + 0.22 * pool["source_support"])
            * (1.0 + 9000.0 * np.maximum(pool["semantic_mean"], 0.0))
            * (1.0 + 4500.0 * np.maximum(pool["base_mean"], 0.0))
            / (1.0 + 2.0 * pool["h088_alignment"])
        )
        pool = pool.sort_values("rank_seed_score", ascending=False).reset_index(drop=True)
    return pool


def solve_variant(
    config: SolverConfig,
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    model: route_energy.RouteEnergyModel,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    current_logit = base_logit.copy()
    current_prob = base_prob.copy()
    move = np.zeros(base_prob.size, dtype=np.float64)
    selected = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        target_idx = TARGETS.index(target)
        if row_count.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_count.get(target, 0) >= config.max_cells_per_target:
            continue
        if int(rec["source_support"]) < config.min_listener_support:
            continue
        if float(rec["stability"]) < config.min_stability:
            continue
        if float(rec["h088_alignment"]) > config.max_h088_alignment:
            continue

        magnitude = min(
            config.max_logit_step,
            config.action_amp * float(rec["magnitude_base"]) * target_magnitude_scale(target),
        )
        step = int(rec["sign"]) * magnitude
        old_row = current_prob[row : row + 1].copy()
        new_logit_flat = current_logit[int(rec["flat_idx"])] + step
        new_prob_value = float(sigmoid(new_logit_flat))
        trial_row = old_row.copy()
        trial_row[0, target_idx] = new_prob_value
        old_energy = float(model.row_energy(old_row)[0])
        new_energy = float(model.row_energy(trial_row)[0])
        energy_delta = new_energy - old_energy
        public_delta = float(rec["coef"]) * step
        public_utility = -public_delta
        if public_utility < config.min_public_utility:
            continue
        if energy_delta > target_energy_tolerance(target, config):
            continue
        score = public_utility - config.energy_penalty * max(energy_delta, 0.0)
        score += config.route_bonus * max(-energy_delta, 0.0)
        score += 0.000002 * float(rec["source_support"])
        if score <= 0:
            continue

        flat = int(rec["flat_idx"])
        current_logit[flat] += step
        current_prob[row, target_idx] = new_prob_value
        move[flat] += step
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        selected.append(
            {
                **rec,
                "logit_step": float(step),
                "public_delta_estimate": public_delta,
                "public_utility": public_utility,
                "old_route_energy": old_energy,
                "new_route_energy": new_energy,
                "route_energy_delta": energy_delta,
                "solver_score": score,
            }
        )
        if len(selected) >= config.max_cells:
            break

    prob = clip_prob(sigmoid(current_logit).reshape(base_prob.shape))
    audit = pd.DataFrame(selected)
    diagnostics = {
        "variant": config.name,
        "selected_cells": int(len(audit)),
        "changed_rows": int(len(set(audit["row"].astype(int)))) if len(audit) else 0,
        "target_counts": audit.groupby("target").size().to_dict() if len(audit) else {},
        "estimated_public_delta": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "mean_selected_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "negative_energy_actions": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
    }
    return prob, audit, diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    energy_model = route_energy.RouteEnergyModel()
    energy_model.fit(train_labels)

    public_support = build_public_support(sample, base_logit)
    pool = proposal_pool(public_support)
    pool.to_csv(OUT / "energy_utility_proposal_pool.csv", index=False)

    outputs = {}
    for config in CONFIGS:
        prob, audit, diagnostics = solve_variant(config, pool, sample, base_prob, base_logit, energy_model)
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_energy_utility_solver_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        move = logit(prob).reshape(-1) - base_logit
        audit.to_csv(OUT / f"energy_utility_{config.name}_audit.csv", index=False)
        outputs[config.name] = {
            "submission_file": out_name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "config": config.__dict__,
            "diagnostics": diagnostics,
            "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
            "validation": validate_submission(root_path, sample, base_prob),
        }

    readout = {
        "experiment": "Energy-Utility Assignment Solver HS-JEPA",
        "public_score_used": True,
        "route_energy_public_free": True,
        "support_cells": int(len(public_support["support_idx"])),
        "proposal_cells": int(len(pool)),
        "ridge_diagnostics": public_support["ridge_diag"],
        "public_observation_count": int(len(public_support["public_files"])),
        "outputs": outputs,
    }
    (OUT / "energy_utility_assignment_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
