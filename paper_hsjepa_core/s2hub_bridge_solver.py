#!/usr/bin/env python3
"""S2-hub bridge solver for HS-JEPA.

Stage-bridge conservation found that S2 repeatedly appears as an objective-stage
hub.  Stage-factor transport showed that moving along the full S-stage factor
is too broad.  This script tests the narrower law:

    S2 is the local bridge/listener target that makes S-stage driver actions
    safe.

The solver reuses the stage-bridge candidate generator, then restricts selected
actions to S2-hub bundles.
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
OUT = HERE / "outputs" / "s2hub_bridge_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
STAGE_TARGETS = ["S1", "S2", "S3", "S4"]
TOL = 1e-12

STAGE_BRIDGE_MODULE = HERE / "stage_bridge_conservation_solver.py"


@dataclass(frozen=True)
class HubConfig:
    name: str
    base_stage_config: str
    max_bundles: int
    max_cells: int
    max_cells_per_target: int
    require_s2_bridge: bool
    require_s2_any: bool
    min_energy_gain: float
    min_public_utility: float
    s2_bridge_bonus: float
    s2_driver_bonus: float


CONFIGS = [
    HubConfig(
        name="s2bridge_core",
        base_stage_config="stagebridge",
        max_bundles=26,
        max_cells=52,
        max_cells_per_target=26,
        require_s2_bridge=True,
        require_s2_any=True,
        min_energy_gain=0.0020,
        min_public_utility=4.0e-6,
        s2_bridge_bonus=1.18,
        s2_driver_bonus=1.00,
    ),
    HubConfig(
        name="s2hub_jackpot",
        base_stage_config="stagebridge_jackpot",
        max_bundles=40,
        max_cells=80,
        max_cells_per_target=34,
        require_s2_bridge=False,
        require_s2_any=True,
        min_energy_gain=0.0004,
        min_public_utility=1.5e-6,
        s2_bridge_bonus=1.14,
        s2_driver_bonus=1.08,
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


stage_bridge = import_module(STAGE_BRIDGE_MODULE, "s2hub_stage_bridge")
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


def stage_config_by_name(name: str):
    for config in stage_bridge.CONFIGS:
        if config.name == name:
            return config
    raise KeyError(name)


def candidate_passes_hub(rec: dict[str, object], config: HubConfig) -> bool:
    driver = str(rec["driver_target"])
    bridge = str(rec["bridge_target"])
    if not bridge:
        return False
    if config.require_s2_bridge and bridge != "S2":
        return False
    if config.require_s2_any and "S2" not in {driver, bridge}:
        return False
    if -float(rec["route_energy_delta"]) < config.min_energy_gain:
        return False
    if float(rec["public_utility"]) < config.min_public_utility:
        return False
    return True


def hub_score(rec: dict[str, object], config: HubConfig) -> float:
    score = float(rec["solver_score"])
    if str(rec["bridge_target"]) == "S2":
        score *= config.s2_bridge_bonus
    if str(rec["driver_target"]) == "S2":
        score *= config.s2_driver_bonus
    score *= 1.0 + 0.10 * max(-float(rec["route_energy_delta"]), 0.0)
    return float(score)


def solve_hub_variant(
    config: HubConfig,
    pool: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    base_config = stage_config_by_name(config.base_stage_config)
    current_logit = world["base_logit"].copy()
    base_prob = world["base_prob"]
    current_prob = base_prob.copy()
    raw_candidates = stage_bridge.generate_candidates(
        pool,
        current_logit,
        current_prob,
        model,
        world["coef_by_flat"],
        base_config,
    )
    if len(raw_candidates):
        raw_candidates = raw_candidates.copy()
        raw_candidates["s2hub_score"] = raw_candidates.apply(lambda row: hub_score(row.to_dict(), config), axis=1)
        candidates = raw_candidates[
            raw_candidates.apply(lambda row: candidate_passes_hub(row.to_dict(), config), axis=1)
        ].sort_values("s2hub_score", ascending=False)
    else:
        candidates = raw_candidates

    selected = []
    used_rows: set[int] = set()
    target_counts: dict[str, int] = {}
    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        targets = [str(rec["driver_target"]), str(rec["bridge_target"])]
        if any(target_counts.get(target, 0) >= config.max_cells_per_target for target in targets):
            continue
        if sum(int(sel["action_count"]) for sel in selected) + int(rec["action_count"]) > config.max_cells:
            continue
        driver = pool[pool["flat_idx"].astype(int).eq(int(rec["driver_flat"]))].iloc[0].to_dict()
        refreshed = stage_bridge.evaluate_driver_bridge(
            driver,
            str(rec["bridge_target"]),
            float(rec["bridge_step"]),
            current_logit,
            current_prob,
            model,
            world["coef_by_flat"],
            base_config,
        )
        if refreshed is None or not candidate_passes_hub(refreshed, config):
            continue
        refreshed["s2hub_score"] = hub_score(refreshed, config)
        for flat, target, step, _role in refreshed["actions"]:
            current_logit[int(flat)] += float(step)
            current_prob[row, TARGETS.index(target)] = float(sigmoid(current_logit[int(flat)]))
            target_counts[target] = target_counts.get(target, 0) + 1
        selected.append(refreshed)
        used_rows.add(row)
        if len(selected) >= config.max_bundles:
            break
    audit = pd.DataFrame(selected)
    prob = clip_prob(sigmoid(current_logit).reshape(base_prob.shape))
    diagnostics = {
        "variant": config.name,
        "base_stage_config": config.base_stage_config,
        "raw_candidate_bundles": int(len(raw_candidates)),
        "hub_candidate_bundles": int(len(candidates)),
        "selected_bundles": int(len(audit)),
        "selected_cells": int(audit["action_count"].sum()) if len(audit) else 0,
        "changed_rows": int(audit["row"].nunique()) if len(audit) else 0,
        "target_counts": target_counts,
        "driver_counts": audit["driver_target"].value_counts().sort_index().to_dict() if len(audit) else {},
        "bridge_counts": audit["bridge_target"].value_counts().sort_index().to_dict() if len(audit) else {},
        "estimated_public_delta": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "mean_selected_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "negative_energy_bundles": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
        "s2_bridge_bundles": int((audit["bridge_target"] == "S2").sum()) if len(audit) else 0,
        "s2_driver_bundles": int((audit["driver_target"] == "S2").sum()) if len(audit) else 0,
    }
    return prob, audit, raw_candidates, diagnostics


def hub_contrast(raw_candidates: pd.DataFrame, max_bundles: int) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {}
    if not len(raw_candidates):
        return out
    frame = raw_candidates[raw_candidates["bridge_target"].astype(str) != ""].copy()
    for hub in STAGE_TARGETS:
        sub = frame[frame["bridge_target"].astype(str).eq(hub)].sort_values("solver_score", ascending=False)
        top = sub.head(max_bundles)
        out[hub] = {
            "candidate_count": float(len(sub)),
            "top_score_sum": float(top["solver_score"].sum()) if len(top) else 0.0,
            "top_energy_gain_sum": float((-top["route_energy_delta"]).clip(lower=0.0).sum()) if len(top) else 0.0,
            "top_public_utility_sum": float(top["public_utility"].sum()) if len(top) else 0.0,
        }
    return out


def run() -> dict[str, object]:
    pool, world = stage_bridge.prepare_world()
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = route_energy.RouteEnergyModel()
    model.fit(labels)
    stage_pool = pool[pool["target"].isin(STAGE_TARGETS)].copy()
    stage_pool.to_csv(OUT / "s2hub_driver_pool.csv", index=False)

    outputs = {}
    for config in CONFIGS:
        prob, audit, raw_candidates, diagnostics = solve_hub_variant(config, stage_pool, world, model)
        diagnostics["bridge_hub_contrast"] = hub_contrast(raw_candidates, config.max_bundles)
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_s2hub_bridge_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, world["sample"], prob)
        write_submission(root_path, world["sample"], prob)
        move = logit(prob).reshape(-1) - world["base_logit"]
        audit.drop(columns=["actions"], errors="ignore").to_csv(OUT / f"s2hub_{config.name}_selected.csv", index=False)
        raw_candidates.drop(columns=["actions"], errors="ignore").to_csv(
            OUT / f"s2hub_{config.name}_raw_candidates.csv", index=False
        )
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
        "experiment": "S2-Hub Bridge Solver HS-JEPA",
        "hypothesis": "S2 is the local objective-stage bridge/listener target for safe S-stage actions.",
        "public_score_used": True,
        "route_energy_public_free": True,
        "outputs": outputs,
    }
    (OUT / "s2hub_bridge_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
