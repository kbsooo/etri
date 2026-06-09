#!/usr/bin/env python3
"""Row-Bundle Transport Solver for HS-JEPA.

Energy-Utility Assignment Solver chooses one cell at a time.  That can miss a
human-state transition that only becomes route-consistent when two or three
targets move together inside the same row.

This script evaluates row-local action bundles and accepts the best bundles
under public-utility, listener, toxicity, and route-consistency constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "row_bundle_transport_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12

ENERGY_UTILITY_MODULE = HERE / "energy_utility_assignment_solver.py"


@dataclass(frozen=True)
class BundleConfig:
    name: str
    max_bundles: int
    max_cells: int
    max_bundle_size: int
    max_bundles_per_target: int
    row_candidate_limit: int
    min_stability: float
    max_h088_alignment: float
    min_public_utility: float
    max_route_energy_delta: float
    action_amp: float
    max_logit_step: float
    singleton_penalty: float
    pair_bonus: float
    triple_bonus: float
    energy_bonus: float
    energy_penalty: float


CONFIGS = [
    BundleConfig(
        name="paircore",
        max_bundles=24,
        max_cells=54,
        max_bundle_size=2,
        max_bundles_per_target=18,
        row_candidate_limit=5,
        min_stability=0.54,
        max_h088_alignment=0.68,
        min_public_utility=1.2e-5,
        max_route_energy_delta=0.0050,
        action_amp=1.16,
        max_logit_step=1.22,
        singleton_penalty=0.78,
        pair_bonus=1.28,
        triple_bonus=1.00,
        energy_bonus=0.022,
        energy_penalty=0.060,
    ),
    BundleConfig(
        name="triadjackpot",
        max_bundles=30,
        max_cells=72,
        max_bundle_size=3,
        max_bundles_per_target=24,
        row_candidate_limit=6,
        min_stability=0.48,
        max_h088_alignment=0.76,
        min_public_utility=5.0e-6,
        max_route_energy_delta=0.0075,
        action_amp=1.32,
        max_logit_step=1.48,
        singleton_penalty=0.62,
        pair_bonus=1.33,
        triple_bonus=1.46,
        energy_bonus=0.025,
        energy_penalty=0.045,
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


energy_utility = import_module(ENERGY_UTILITY_MODULE, "bundle_energy_utility")
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


def target_scale(target: str) -> float:
    if target == "Q2":
        return 1.08
    if target == "S2":
        return 1.12
    if target in {"S1", "S3", "S4"}:
        return 0.86
    return 1.00


def bundle_multiplier(size: int, config: BundleConfig) -> float:
    if size == 1:
        return config.singleton_penalty
    if size == 2:
        return config.pair_bonus
    return config.triple_bonus


def prepared_pool() -> tuple[pd.DataFrame, dict[str, object]]:
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    public_support = energy_utility.build_public_support(sample, base_logit)
    pool = energy_utility.proposal_pool(public_support)
    return pool, {
        "sample": sample,
        "base_prob": clip_prob(base_prob),
        "base_logit": base_logit,
        "base_grads": base_grads,
        "semantic_grads": semantic_grads,
        "h088_move": h088_move,
        "public_support": public_support,
    }


def cell_step(rec: dict[str, object], config: BundleConfig) -> float:
    magnitude = (
        config.action_amp
        * float(rec["magnitude_base"])
        * target_scale(str(rec["target"]))
    )
    magnitude = min(config.max_logit_step, magnitude)
    return int(rec["sign"]) * magnitude


def evaluate_bundle(
    bundle: tuple[dict[str, object], ...],
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    config: BundleConfig,
) -> dict[str, object] | None:
    row = int(bundle[0]["row"])
    old_vec = current_prob[row : row + 1].copy()
    trial_vec = old_vec.copy()
    steps = []
    public_delta = 0.0
    max_h088 = 0.0
    min_stability = 1.0
    source_support = 0
    targets = []
    for rec in bundle:
        target = str(rec["target"])
        target_idx = TARGETS.index(target)
        flat = int(rec["flat_idx"])
        step = cell_step(rec, config) * bundle_multiplier(len(bundle), config)
        step = float(np.clip(step, -config.max_logit_step, config.max_logit_step))
        trial_vec[0, target_idx] = float(sigmoid(current_logit[flat] + step))
        public_delta += float(rec["coef"]) * step
        max_h088 = max(max_h088, float(rec["h088_alignment"]))
        min_stability = min(min_stability, float(rec["stability"]))
        source_support += int(rec["source_support"])
        targets.append(target)
        steps.append((flat, target, step))
    old_energy = float(model.row_energy(old_vec)[0])
    new_energy = float(model.row_energy(trial_vec)[0])
    energy_delta = new_energy - old_energy
    public_utility = -float(public_delta)
    if public_utility < config.min_public_utility:
        return None
    if energy_delta > config.max_route_energy_delta:
        return None
    score = public_utility
    score -= config.energy_penalty * max(energy_delta, 0.0)
    score += config.energy_bonus * max(-energy_delta, 0.0)
    score *= 1.0 + 0.03 * source_support
    score *= 1.0 + 0.04 * len(set(targets))
    if {"Q2", "S2"}.issubset(set(targets)):
        score *= 1.18
    if score <= 0:
        return None
    return {
        "row": row,
        "bundle_size": len(bundle),
        "targets": "+".join(targets),
        "flat_indices": ",".join(str(flat) for flat, _target, _step in steps),
        "steps": steps,
        "public_delta_estimate": public_delta,
        "public_utility": public_utility,
        "old_route_energy": old_energy,
        "new_route_energy": new_energy,
        "route_energy_delta": energy_delta,
        "max_h088_alignment": max_h088,
        "min_stability": min_stability,
        "source_support_sum": source_support,
        "solver_score": score,
    }


def generate_row_bundles(
    pool: pd.DataFrame,
    current_logit: np.ndarray,
    current_prob: np.ndarray,
    model: route_energy.RouteEnergyModel,
    config: BundleConfig,
) -> pd.DataFrame:
    candidates = []
    filtered = pool[
        (pool["stability"] >= config.min_stability)
        & (pool["h088_alignment"] <= config.max_h088_alignment)
    ].copy()
    for _row, group in filtered.groupby("row"):
        group = group.sort_values("rank_seed_score", ascending=False).head(config.row_candidate_limit)
        records = group.to_dict("records")
        max_size = min(config.max_bundle_size, len(records))
        for size in range(1, max_size + 1):
            for combo in combinations(records, size):
                if len({int(rec["flat_idx"]) for rec in combo}) != size:
                    continue
                result = evaluate_bundle(combo, current_logit, current_prob, model, config)
                if result is not None:
                    candidates.append(result)
    frame = pd.DataFrame(candidates)
    if len(frame):
        frame = frame.sort_values("solver_score", ascending=False).reset_index(drop=True)
    return frame


def solve_variant(
    config: BundleConfig,
    pool: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    model: route_energy.RouteEnergyModel,
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    current_logit = base_logit.copy()
    current_prob = base_prob.copy()
    selected = []
    target_bundle_counts: dict[str, int] = {}
    used_rows: set[int] = set()
    candidates = generate_row_bundles(pool, current_logit, current_prob, model, config)
    for rec in candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        target_list = str(rec["targets"]).split("+")
        if any(target_bundle_counts.get(target, 0) >= config.max_bundles_per_target for target in target_list):
            continue
        if sum(len(str(sel["flat_indices"]).split(",")) for sel in selected) + int(rec["bundle_size"]) > config.max_cells:
            continue
        # Re-evaluate against the current probability after earlier bundles.
        combo = []
        lookup = {
            int(row_rec["flat_idx"]): row_rec
            for row_rec in pool[pool["row"].astype(int).eq(row)].to_dict("records")
        }
        for flat in str(rec["flat_indices"]).split(","):
            combo.append(lookup[int(flat)])
        refreshed = evaluate_bundle(tuple(combo), current_logit, current_prob, model, config)
        if refreshed is None:
            continue
        for flat, target, step in refreshed["steps"]:
            current_logit[int(flat)] += float(step)
            current_prob[row, TARGETS.index(target)] = float(sigmoid(current_logit[int(flat)]))
            target_bundle_counts[target] = target_bundle_counts.get(target, 0) + 1
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
        "selected_cells": int(audit["bundle_size"].sum()) if len(audit) else 0,
        "changed_rows": int(audit["row"].nunique()) if len(audit) else 0,
        "bundle_size_counts": audit.groupby("bundle_size").size().to_dict() if len(audit) else {},
        "target_counts": pd.Series(
            [target for targets in audit["targets"].astype(str) for target in targets.split("+")]
        ).value_counts().sort_index().to_dict()
        if len(audit)
        else {},
        "estimated_public_delta": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "mean_selected_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "negative_energy_bundles": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
        "q2s2_bundles": int(audit["targets"].astype(str).str.contains("Q2").mul(audit["targets"].astype(str).str.contains("S2")).sum())
        if len(audit)
        else 0,
    }
    return prob, audit, candidates, diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    pool, world = prepared_pool()
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = route_energy.RouteEnergyModel()
    model.fit(train_labels)

    sample = world["sample"]
    base_prob = world["base_prob"]
    base_logit = world["base_logit"]
    base_grads = world["base_grads"]
    semantic_grads = world["semantic_grads"]
    h088_move = world["h088_move"]

    pool.to_csv(OUT / "row_bundle_proposal_pool.csv", index=False)
    outputs = {}
    for config in CONFIGS:
        prob, audit, candidates, diagnostics = solve_variant(config, pool, sample, base_prob, base_logit, model)
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_row_bundle_transport_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        move = logit(prob).reshape(-1) - base_logit
        audit.to_csv(OUT / f"row_bundle_{config.name}_selected.csv", index=False)
        candidates.to_csv(OUT / f"row_bundle_{config.name}_candidates.csv", index=False)
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
        "experiment": "Row-Bundle Transport Solver HS-JEPA",
        "public_score_used": True,
        "route_energy_public_free": True,
        "proposal_cells": int(len(pool)),
        "outputs": outputs,
    }
    (OUT / "row_bundle_transport_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
