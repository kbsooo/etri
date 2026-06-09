#!/usr/bin/env python3
"""Objective-stage bridge conservation solver for HS-JEPA.

The previous row-bundle solver showed that large Q2/S2 bundles do not survive,
but objective-stage pairs such as S1/S2 and S3/S4 do.  This script tests a
different mechanism:

    public-utility driver action + route-energy bridge action

The bridge action is allowed even when it has weak public utility, if it keeps
the S-stage target vector on the learned route manifold.
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
OUT = HERE / "outputs" / "stage_bridge_conservation_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
STAGE_TARGETS = ["S1", "S2", "S3", "S4"]
TOL = 1e-12

ENERGY_UTILITY_MODULE = HERE / "energy_utility_assignment_solver.py"


@dataclass(frozen=True)
class BridgeConfig:
    name: str
    max_bundles: int
    max_cells: int
    max_cells_per_target: int
    min_driver_stability: float
    max_driver_h088: float
    min_public_utility: float
    max_route_energy_delta: float
    driver_amp: float
    driver_max_step: float
    bridge_max_step: float
    bridge_grid_points: int
    energy_bonus: float
    energy_penalty: float
    bridge_bad_public_penalty: float
    same_direction_bonus: float
    require_bridge: bool


CONFIGS = [
    BridgeConfig(
        name="stagebridge",
        max_bundles=30,
        max_cells=60,
        max_cells_per_target=24,
        min_driver_stability=0.54,
        max_driver_h088=0.68,
        min_public_utility=8e-6,
        max_route_energy_delta=0.0048,
        driver_amp=1.12,
        driver_max_step=1.20,
        bridge_max_step=0.42,
        bridge_grid_points=7,
        energy_bonus=0.030,
        energy_penalty=0.060,
        bridge_bad_public_penalty=0.65,
        same_direction_bonus=1.08,
        require_bridge=False,
    ),
    BridgeConfig(
        name="stagebridge_jackpot",
        max_bundles=42,
        max_cells=84,
        max_cells_per_target=32,
        min_driver_stability=0.48,
        max_driver_h088=0.76,
        min_public_utility=3e-6,
        max_route_energy_delta=0.0072,
        driver_amp=1.30,
        driver_max_step=1.45,
        bridge_max_step=0.62,
        bridge_grid_points=9,
        energy_bonus=0.034,
        energy_penalty=0.044,
        bridge_bad_public_penalty=0.48,
        same_direction_bonus=1.12,
        require_bridge=False,
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


energy_utility = import_module(ENERGY_UTILITY_MODULE, "stage_bridge_energy_utility")
candidate1 = energy_utility.candidate1
route_energy = energy_utility.route_energy


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


def stage_target_index(target: str) -> int:
    return TARGETS.index(target)


def driver_step(rec: dict[str, object], config: BridgeConfig) -> float:
    target = str(rec["target"])
    scale = 1.08 if target == "S2" else 0.88 if target in {"S1", "S3", "S4"} else 1.0
    step = int(rec["sign"]) * config.driver_amp * float(rec["magnitude_base"]) * scale
    return float(np.clip(step, -config.driver_max_step, config.driver_max_step))


def prepare_world() -> tuple[pd.DataFrame, dict[str, object]]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    public_support = energy_utility.build_public_support(sample, base_logit)
    pool = energy_utility.proposal_pool(public_support)
    support_idx = public_support["support_idx"]
    coef = public_support["coef"]
    stability = public_support["stability"]
    coef_by_flat = {int(flat): float(coef[i]) for i, flat in enumerate(support_idx)}
    stability_by_flat = {int(flat): float(stability[i]) for i, flat in enumerate(support_idx)}
    return pool, {
        "sample": sample,
        "base_prob": clip_prob(base_prob),
        "base_logit": base_logit,
        "base_grads": base_grads,
        "semantic_grads": semantic_grads,
        "h088_move": h088_move,
        "public_support": public_support,
        "coef_by_flat": coef_by_flat,
        "stability_by_flat": stability_by_flat,
    }


def bridge_grid(max_step: float, n: int) -> list[float]:
    raw = np.linspace(-max_step, max_step, n)
    return [float(x) for x in raw if abs(float(x)) > 1e-9]


def evaluate_driver_bridge(
    driver: dict[str, object],
    bridge_target: str | None,
    bridge_step: float,
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    coef_by_flat: dict[int, float],
    config: BridgeConfig,
) -> dict[str, object] | None:
    row = int(driver["row"])
    driver_target = str(driver["target"])
    driver_flat = int(driver["flat_idx"])
    dstep = driver_step(driver, config)
    old_vec = current_prob[row : row + 1].copy()
    trial_vec = old_vec.copy()
    trial_vec[0, stage_target_index(driver_target)] = float(sigmoid(current_logit[driver_flat] + dstep))
    public_delta = float(driver["coef"]) * dstep
    actions = [(driver_flat, driver_target, dstep, "driver")]
    bridge_flat = -1
    bridge_public_delta = 0.0
    same_direction = False
    if bridge_target is not None:
        bridge_flat = row * len(TARGETS) + stage_target_index(bridge_target)
        trial_vec[0, stage_target_index(bridge_target)] = float(sigmoid(current_logit[bridge_flat] + bridge_step))
        bridge_public_delta = coef_by_flat.get(bridge_flat, 0.0) * bridge_step
        public_delta += bridge_public_delta
        actions.append((bridge_flat, bridge_target, bridge_step, "bridge"))
        same_direction = np.sign(dstep) == np.sign(bridge_step)
    old_energy = float(model.row_energy(old_vec)[0])
    new_energy = float(model.row_energy(trial_vec)[0])
    energy_delta = new_energy - old_energy
    public_utility = -public_delta
    if public_utility < config.min_public_utility:
        return None
    if energy_delta > config.max_route_energy_delta:
        return None
    bridge_bad_public = max(bridge_public_delta, 0.0)
    score = public_utility
    score += config.energy_bonus * max(-energy_delta, 0.0)
    score -= config.energy_penalty * max(energy_delta, 0.0)
    score -= config.bridge_bad_public_penalty * bridge_bad_public
    if bridge_target is not None:
        score *= 1.0 + 0.04
        if same_direction:
            score *= config.same_direction_bonus
        if "S2" in {driver_target, bridge_target}:
            score *= 1.07
    elif config.require_bridge:
        return None
    if score <= 0:
        return None
    return {
        "row": row,
        "driver_target": driver_target,
        "driver_flat": driver_flat,
        "driver_step": dstep,
        "bridge_target": bridge_target or "",
        "bridge_flat": bridge_flat,
        "bridge_step": bridge_step if bridge_target is not None else 0.0,
        "actions": actions,
        "action_count": len(actions),
        "public_delta_estimate": public_delta,
        "driver_public_delta": float(driver["coef"]) * dstep,
        "bridge_public_delta": bridge_public_delta,
        "public_utility": public_utility,
        "old_route_energy": old_energy,
        "new_route_energy": new_energy,
        "route_energy_delta": energy_delta,
        "same_direction": bool(same_direction),
        "driver_h088_alignment": float(driver["h088_alignment"]),
        "driver_stability": float(driver["stability"]),
        "source_support": int(driver["source_support"]),
        "solver_score": score,
    }


def generate_candidates(
    pool: pd.DataFrame,
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    coef_by_flat: dict[int, float],
    config: BridgeConfig,
) -> pd.DataFrame:
    candidates = []
    drivers = pool[
        pool["target"].isin(STAGE_TARGETS)
        & (pool["stability"] >= config.min_driver_stability)
        & (pool["h088_alignment"] <= config.max_driver_h088)
    ].copy()
    drivers = drivers.sort_values("rank_seed_score", ascending=False)
    for driver in drivers.to_dict("records"):
        row = int(driver["row"])
        driver_target = str(driver["target"])
        no_bridge = evaluate_driver_bridge(
            driver, None, 0.0, current_logit, current_prob, model, coef_by_flat, config
        )
        if no_bridge is not None:
            candidates.append(no_bridge)
        for bridge_target in STAGE_TARGETS:
            if bridge_target == driver_target:
                continue
            bridge_flat = row * len(TARGETS) + stage_target_index(bridge_target)
            # Avoid adding a bridge that would duplicate a non-stage source action.
            if bridge_flat == int(driver["flat_idx"]):
                continue
            for step in bridge_grid(config.bridge_max_step, config.bridge_grid_points):
                cand = evaluate_driver_bridge(
                    driver, bridge_target, step, current_logit, current_prob, model, coef_by_flat, config
                )
                if cand is not None:
                    candidates.append(cand)
    frame = pd.DataFrame(candidates)
    if len(frame):
        frame = frame.sort_values("solver_score", ascending=False).reset_index(drop=True)
    return frame


def solve_variant(
    config: BridgeConfig,
    pool: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
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
        config,
    )
    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        targets = [str(rec["driver_target"])]
        if str(rec["bridge_target"]):
            targets.append(str(rec["bridge_target"]))
        if any(target_counts.get(target, 0) >= config.max_cells_per_target for target in targets):
            continue
        if sum(int(sel["action_count"]) for sel in selected) + int(rec["action_count"]) > config.max_cells:
            continue
        # Re-evaluate after prior selected rows. Rows are unique, but keep this
        # explicit so the audit records the actual final energy.
        driver = pool[pool["flat_idx"].astype(int).eq(int(rec["driver_flat"]))].iloc[0].to_dict()
        bridge_target = str(rec["bridge_target"]) or None
        refreshed = evaluate_driver_bridge(
            driver,
            bridge_target,
            float(rec["bridge_step"]),
            current_logit,
            current_prob,
            model,
            world["coef_by_flat"],
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
        "candidate_actions": int(len(candidates)),
        "selected_bundles": int(len(audit)),
        "selected_cells": int(audit["action_count"].sum()) if len(audit) else 0,
        "selected_bridge_bundles": int((audit["bridge_target"].astype(str) != "").sum()) if len(audit) else 0,
        "changed_rows": int(audit["row"].nunique()) if len(audit) else 0,
        "target_counts": target_counts,
        "driver_counts": audit["driver_target"].value_counts().sort_index().to_dict() if len(audit) else {},
        "bridge_counts": audit[audit["bridge_target"].astype(str) != ""]["bridge_target"].value_counts().sort_index().to_dict()
        if len(audit)
        else {},
        "estimated_public_delta": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "mean_selected_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "negative_energy_bundles": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
        "same_direction_bridges": int(audit["same_direction"].sum()) if len(audit) else 0,
    }
    return prob, audit, candidates, diagnostics


def run() -> dict[str, object]:
    pool, world = prepare_world()
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = route_energy.RouteEnergyModel()
    model.fit(train_labels)

    stage_pool = pool[pool["target"].isin(STAGE_TARGETS)].copy()
    stage_pool.to_csv(OUT / "stage_bridge_driver_pool.csv", index=False)

    outputs = {}
    for config in CONFIGS:
        prob, audit, candidates, diagnostics = solve_variant(config, stage_pool, world, model)
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_stage_bridge_conservation_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, world["sample"], prob)
        write_submission(root_path, world["sample"], prob)
        move = logit(prob).reshape(-1) - world["base_logit"]
        audit.to_csv(OUT / f"stage_bridge_{config.name}_selected.csv", index=False)
        candidates.to_csv(OUT / f"stage_bridge_{config.name}_candidates.csv", index=False)
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
        "experiment": "Objective-Stage Bridge Conservation Solver HS-JEPA",
        "public_score_used": True,
        "route_energy_public_free": True,
        "stage_driver_pool_cells": int(len(stage_pool)),
        "outputs": outputs,
    }
    (OUT / "stage_bridge_conservation_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
