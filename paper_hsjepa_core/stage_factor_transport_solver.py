#!/usr/bin/env python3
"""Objective-stage factor transport solver for HS-JEPA.

The stage-bridge solver found that S-stage actions often become safe only when
a public-sensitive driver is paired with an objective-stage bridge.  This script
tests a larger law:

    Are S1/S2/S3/S4 actions transported along a shared objective sleep-state
    factor, rather than by arbitrary pairwise bridges?

The factor is learned only from train labels.  Public-loss coefficients are
used as an action utility/toxicity sensor after the factor proposal is formed.
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
OUT = HERE / "outputs" / "stage_factor_transport_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
STAGE_TARGETS = ["S1", "S2", "S3", "S4"]
TOL = 1e-12

STAGE_BRIDGE_MODULE = HERE / "stage_bridge_conservation_solver.py"


@dataclass(frozen=True)
class FactorConfig:
    name: str
    max_bundles: int
    max_cells: int
    max_cells_per_target: int
    min_driver_stability: float
    max_driver_h088: float
    min_public_utility: float
    max_route_energy_delta: float
    min_energy_gain_without_public: float
    driver_amp: float
    driver_max_step: float
    bridge_max_step: float
    min_bridge_step: float
    min_targets_per_bundle: int
    max_targets_per_bundle: int
    route_bonus: float
    route_penalty: float
    public_bonus: float
    factor_residual_penalty: float
    h088_penalty: float


CONFIGS = [
    FactorConfig(
        name="factor_paircore",
        max_bundles=34,
        max_cells=68,
        max_cells_per_target=28,
        min_driver_stability=0.54,
        max_driver_h088=0.68,
        min_public_utility=5.0e-6,
        max_route_energy_delta=0.0048,
        min_energy_gain_without_public=0.0006,
        driver_amp=1.10,
        driver_max_step=1.16,
        bridge_max_step=0.48,
        min_bridge_step=0.055,
        min_targets_per_bundle=2,
        max_targets_per_bundle=2,
        route_bonus=0.034,
        route_penalty=0.060,
        public_bonus=1.00,
        factor_residual_penalty=0.012,
        h088_penalty=0.50,
    ),
    FactorConfig(
        name="factor_axis_jackpot",
        max_bundles=38,
        max_cells=128,
        max_cells_per_target=38,
        min_driver_stability=0.48,
        max_driver_h088=0.76,
        min_public_utility=1.5e-6,
        max_route_energy_delta=0.0084,
        min_energy_gain_without_public=0.0002,
        driver_amp=1.25,
        driver_max_step=1.36,
        bridge_max_step=0.64,
        min_bridge_step=0.040,
        min_targets_per_bundle=3,
        max_targets_per_bundle=4,
        route_bonus=0.040,
        route_penalty=0.046,
        public_bonus=1.00,
        factor_residual_penalty=0.009,
        h088_penalty=0.38,
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


stage_bridge = import_module(STAGE_BRIDGE_MODULE, "stage_factor_stage_bridge")
candidate1 = stage_bridge.candidate1
route_energy = stage_bridge.route_energy


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


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


def learn_stage_factor(labels: pd.DataFrame) -> dict[str, object]:
    y = labels[STAGE_TARGETS].to_numpy(dtype=np.float64)
    centered = y - y.mean(axis=0, keepdims=True)
    cov = np.cov(centered, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]
    pc1 = evecs[:, 0].astype(float)
    if pc1.sum() < 0:
        pc1 = -pc1
    pc1 = pc1 / (np.linalg.norm(pc1) + 1e-12)
    explained = evals / (evals.sum() + 1e-12)
    corr = labels[STAGE_TARGETS].corr().to_dict()
    return {
        "targets": STAGE_TARGETS,
        "weights": {target: float(pc1[i]) for i, target in enumerate(STAGE_TARGETS)},
        "explained_variance_ratio": {f"pc{i + 1}": float(value) for i, value in enumerate(explained)},
        "covariance": cov.tolist(),
        "correlation": corr,
    }


def stage_target_index(target: str) -> int:
    return TARGETS.index(target)


def driver_step(rec: dict[str, object], config: FactorConfig) -> float:
    target = str(rec["target"])
    scale = 1.05 if target == "S2" else 0.92
    step = int(rec["sign"]) * config.driver_amp * float(rec["magnitude_base"]) * scale
    return float(np.clip(step, -config.driver_max_step, config.driver_max_step))


def factor_bundle_steps(
    driver: dict[str, object],
    config: FactorConfig,
    factor_weights: dict[str, float],
) -> list[tuple[str, float, str]]:
    driver_target = str(driver["target"])
    dstep = driver_step(driver, config)
    w_driver = factor_weights[driver_target]
    if abs(w_driver) < 1e-9:
        return []
    alpha = dstep / w_driver
    raw_steps = {target: float(alpha * factor_weights[target]) for target in STAGE_TARGETS}
    raw_steps[driver_target] = dstep
    bridge_targets = [
        target
        for target in STAGE_TARGETS
        if target != driver_target and abs(raw_steps[target]) >= config.min_bridge_step
    ]
    bridge_targets = sorted(bridge_targets, key=lambda target: abs(raw_steps[target]), reverse=True)
    take = max(0, config.max_targets_per_bundle - 1)
    bridge_targets = bridge_targets[:take]
    actions = [(driver_target, dstep, "driver")]
    for target in bridge_targets:
        step = float(np.clip(raw_steps[target], -config.bridge_max_step, config.bridge_max_step))
        if abs(step) >= config.min_bridge_step:
            actions.append((target, step, "factor_bridge"))
    if len(actions) < config.min_targets_per_bundle:
        return []
    return actions


def factor_residual(actions: list[tuple[str, float, str]], factor_weights: dict[str, float]) -> float:
    vec = np.zeros(len(STAGE_TARGETS), dtype=np.float64)
    axis = np.asarray([factor_weights[target] for target in STAGE_TARGETS], dtype=np.float64)
    axis = axis / (np.linalg.norm(axis) + 1e-12)
    for target, step, _role in actions:
        vec[STAGE_TARGETS.index(target)] = step
    if np.linalg.norm(vec) < 1e-12:
        return 1.0
    proj = axis * float(vec @ axis)
    return float(np.linalg.norm(vec - proj) / (np.linalg.norm(vec) + 1e-12))


def evaluate_factor_bundle(
    driver: dict[str, object],
    actions: list[tuple[str, float, str]],
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    coef_by_flat: dict[int, float],
    h088_move: np.ndarray,
    factor_weights: dict[str, float],
    config: FactorConfig,
) -> dict[str, object] | None:
    row = int(driver["row"])
    old_vec = current_prob[row : row + 1].copy()
    trial_vec = old_vec.copy()
    public_delta = 0.0
    h088_same = 0.0
    flat_actions = []
    for target, step, role in actions:
        flat = row * len(TARGETS) + stage_target_index(target)
        trial_vec[0, stage_target_index(target)] = float(sigmoid(current_logit[flat] + step))
        public_delta += coef_by_flat.get(flat, 0.0) * step
        h088_same += max(0.0, float(h088_move[flat]) * np.sign(step)) * abs(step)
        flat_actions.append((flat, target, step, role))
    old_energy = float(model.row_energy(old_vec)[0])
    new_energy = float(model.row_energy(trial_vec)[0])
    energy_delta = new_energy - old_energy
    public_utility = -public_delta
    if public_utility < config.min_public_utility and energy_delta > -config.min_energy_gain_without_public:
        return None
    if energy_delta > config.max_route_energy_delta:
        return None
    residual = factor_residual(actions, factor_weights)
    score = 0.0
    score += config.public_bonus * public_utility
    score += config.route_bonus * max(-energy_delta, 0.0)
    score -= config.route_penalty * max(energy_delta, 0.0)
    score -= config.factor_residual_penalty * residual
    score -= config.h088_penalty * h088_same
    score += 0.0000015 * float(driver["source_support"])
    if "S2" in {target for target, _step, _role in actions}:
        score *= 1.05
    if score <= 0:
        return None
    return {
        "row": row,
        "driver_target": str(driver["target"]),
        "driver_flat": int(driver["flat_idx"]),
        "action_count": len(flat_actions),
        "action_targets": ",".join(target for _flat, target, _step, _role in flat_actions),
        "action_steps": ",".join(f"{step:.8f}" for _flat, _target, step, _role in flat_actions),
        "action_roles": ",".join(role for _flat, _target, _step, role in flat_actions),
        "actions": flat_actions,
        "public_delta_estimate": float(public_delta),
        "public_utility": float(public_utility),
        "old_route_energy": old_energy,
        "new_route_energy": new_energy,
        "route_energy_delta": float(energy_delta),
        "factor_residual": residual,
        "h088_same_direction_mass": float(h088_same),
        "driver_h088_alignment": float(driver["h088_alignment"]),
        "driver_stability": float(driver["stability"]),
        "source_support": int(driver["source_support"]),
        "solver_score": float(score),
    }


def generate_candidates(
    pool: pd.DataFrame,
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    coef_by_flat: dict[int, float],
    h088_move: np.ndarray,
    factor_weights: dict[str, float],
    config: FactorConfig,
) -> pd.DataFrame:
    rows = []
    drivers = pool[
        pool["target"].isin(STAGE_TARGETS)
        & (pool["stability"] >= config.min_driver_stability)
        & (pool["h088_alignment"] <= config.max_driver_h088)
    ].sort_values("rank_seed_score", ascending=False)
    for driver in drivers.to_dict("records"):
        actions = factor_bundle_steps(driver, config, factor_weights)
        if not actions:
            continue
        rec = evaluate_factor_bundle(
            driver,
            actions,
            current_logit,
            current_prob,
            model,
            coef_by_flat,
            h088_move,
            factor_weights,
            config,
        )
        if rec is not None:
            rows.append(rec)
    frame = pd.DataFrame(rows)
    if len(frame):
        frame = frame.sort_values("solver_score", ascending=False).reset_index(drop=True)
    return frame


def solve_variant(
    config: FactorConfig,
    pool: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
    factor_weights: dict[str, float],
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    current_logit = world["base_logit"].copy()
    base_prob = world["base_prob"]
    current_prob = base_prob.copy()
    selected = []
    used_rows: set[int] = set()
    target_counts: dict[str, int] = {}
    candidates = generate_candidates(
        pool,
        current_logit,
        current_prob,
        model,
        world["coef_by_flat"],
        world["h088_move"],
        factor_weights,
        config,
    )
    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        if sum(int(sel["action_count"]) for sel in selected) + int(rec["action_count"]) > config.max_cells:
            continue
        actions = list(rec["actions"])
        targets = [target for _flat, target, _step, _role in actions]
        if any(target_counts.get(target, 0) >= config.max_cells_per_target for target in targets):
            continue
        driver = pool[pool["flat_idx"].astype(int).eq(int(rec["driver_flat"]))].iloc[0].to_dict()
        refreshed = evaluate_factor_bundle(
            driver,
            [(target, step, role) for _flat, target, step, role in actions],
            current_logit,
            current_prob,
            model,
            world["coef_by_flat"],
            world["h088_move"],
            factor_weights,
            config,
        )
        if refreshed is None:
            continue
        for flat, target, step, _role in refreshed["actions"]:
            current_logit[int(flat)] += float(step)
            current_prob[row, stage_target_index(target)] = float(sigmoid(current_logit[int(flat)]))
            target_counts[target] = target_counts.get(target, 0) + 1
        used_rows.add(row)
        selected.append(refreshed)
        if len(selected) >= config.max_bundles:
            break
    audit = pd.DataFrame(selected)
    prob = clip_prob(sigmoid(current_logit).reshape(base_prob.shape))
    diagnostics = {
        "variant": config.name,
        "candidate_bundles": int(len(candidates)),
        "selected_bundles": int(len(audit)),
        "selected_cells": int(audit["action_count"].sum()) if len(audit) else 0,
        "changed_rows": int(audit["row"].nunique()) if len(audit) else 0,
        "target_counts": target_counts,
        "driver_counts": audit["driver_target"].value_counts().sort_index().to_dict() if len(audit) else {},
        "bundle_size_counts": audit["action_count"].value_counts().sort_index().to_dict() if len(audit) else {},
        "estimated_public_delta": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "mean_selected_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "negative_energy_bundles": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
        "mean_factor_residual": float(audit["factor_residual"].mean()) if len(audit) else 0.0,
    }
    return prob, audit, candidates, diagnostics


def factor_null_stress(
    config: FactorConfig,
    pool: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
    factor_weights: dict[str, float],
    actual_candidates: pd.DataFrame,
    repeats: int = 96,
) -> dict[str, float]:
    rng = np.random.default_rng(20260609)
    weights = np.asarray([factor_weights[target] for target in STAGE_TARGETS], dtype=np.float64)

    def top_score(frame: pd.DataFrame) -> float:
        if not len(frame):
            return 0.0
        return float(frame.head(config.max_bundles)["solver_score"].sum())

    def top_energy_gain(frame: pd.DataFrame) -> float:
        if not len(frame):
            return 0.0
        return float((-frame.head(config.max_bundles)["route_energy_delta"]).clip(lower=0.0).sum())

    actual_top_score = top_score(actual_candidates)
    actual_energy_gain = top_energy_gain(actual_candidates)
    null_scores = []
    null_energy = []
    null_counts = []
    for _ in range(repeats):
        perm = rng.permutation(weights)
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=len(STAGE_TARGETS))
        vec = perm * signs
        if vec.sum() < 0:
            vec = -vec
        vec = vec / (np.linalg.norm(vec) + 1e-12)
        null_weights = {target: float(vec[i]) for i, target in enumerate(STAGE_TARGETS)}
        frame = generate_candidates(
            pool,
            world["base_logit"],
            world["base_prob"],
            model,
            world["coef_by_flat"],
            world["h088_move"],
            null_weights,
            config,
        )
        null_scores.append(top_score(frame))
        null_energy.append(top_energy_gain(frame))
        null_counts.append(float(len(frame)))
    score_arr = np.asarray(null_scores, dtype=np.float64)
    energy_arr = np.asarray(null_energy, dtype=np.float64)
    count_arr = np.asarray(null_counts, dtype=np.float64)
    return {
        "repeats": float(repeats),
        "actual_candidate_count": float(len(actual_candidates)),
        "null_candidate_count_mean": float(count_arr.mean()),
        "actual_top_score_sum": float(actual_top_score),
        "null_top_score_sum_mean": float(score_arr.mean()),
        "null_top_score_sum_std": float(score_arr.std(ddof=1) + 1e-12),
        "actual_top_score_z": float((actual_top_score - score_arr.mean()) / (score_arr.std(ddof=1) + 1e-12)),
        "actual_top_score_p_ge": float((score_arr >= actual_top_score).mean()),
        "actual_top_energy_gain": float(actual_energy_gain),
        "null_top_energy_gain_mean": float(energy_arr.mean()),
        "null_top_energy_gain_std": float(energy_arr.std(ddof=1) + 1e-12),
        "actual_top_energy_gain_z": float((actual_energy_gain - energy_arr.mean()) / (energy_arr.std(ddof=1) + 1e-12)),
        "actual_top_energy_gain_p_ge": float((energy_arr >= actual_energy_gain).mean()),
    }


def run() -> dict[str, object]:
    pool, world = stage_bridge.prepare_world()
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = route_energy.RouteEnergyModel()
    model.fit(labels)
    factor = learn_stage_factor(labels)
    factor_weights = factor["weights"]
    stage_pool = pool[pool["target"].isin(STAGE_TARGETS)].copy()
    stage_pool.to_csv(OUT / "stage_factor_driver_pool.csv", index=False)

    outputs = {}
    for config in CONFIGS:
        prob, audit, candidates, diagnostics = solve_variant(config, stage_pool, world, model, factor_weights)
        diagnostics["factor_null_stress"] = factor_null_stress(
            config,
            stage_pool,
            world,
            model,
            factor_weights,
            candidates,
        )
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_stage_factor_transport_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, world["sample"], prob)
        write_submission(root_path, world["sample"], prob)
        move = logit(prob).reshape(-1) - world["base_logit"]
        audit_to_write = audit.drop(columns=["actions"], errors="ignore")
        candidates_to_write = candidates.drop(columns=["actions"], errors="ignore")
        audit_to_write.to_csv(OUT / f"stage_factor_{config.name}_selected.csv", index=False)
        candidates_to_write.to_csv(OUT / f"stage_factor_{config.name}_candidates.csv", index=False)
        outputs[config.name] = {
            "submission_file": out_name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "config": config.__dict__,
            "diagnostics": diagnostics,
            "listener_metrics": candidate1.candidate_metrics(
                move, world["base_grads"], world["semantic_grads"], world["h088_move"]
            ),
            "validation": validate_submission(root_path, world["sample"], world["base_prob"]),
        }
    readout = {
        "experiment": "Objective-Stage Factor Transport Solver HS-JEPA",
        "hypothesis": "S-stage actions are transported along a shared train-label objective factor.",
        "public_score_used": True,
        "stage_factor_public_free": True,
        "stage_factor": factor,
        "outputs": outputs,
    }
    (OUT / "stage_factor_transport_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
