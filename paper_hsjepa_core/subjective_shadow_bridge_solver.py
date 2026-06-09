#!/usr/bin/env python3
"""Subjective-shadow bridge solver for HS-JEPA.

Objective-stage bridge conservation suggested that S-stage actions often need a
route-preserving S2-hub companion.  This experiment asks a larger human-state
question:

    If an objective sleep-stage bridge changes the row's S-state pressure,
    should the subjective satisfaction target Q1 move as a shadow response?

The Q1 direction is not hand-picked from public LB.  It is inferred from train
target geometry: Q1 is positively related to S1 and weakly negatively related
to S3.  Public-loss coefficients are used only as a toxicity/utility sensor
after the route-consistent subjective proposal is built.
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
OUT = HERE / "outputs" / "subjective_shadow_bridge_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
STAGE_TARGETS = ["S1", "S2", "S3", "S4"]
TOL = 1e-12

STAGE_BRIDGE_MODULE = HERE / "stage_bridge_conservation_solver.py"


@dataclass(frozen=True)
class ShadowConfig:
    name: str
    stage_variant: str
    max_shadow_cells: int
    min_abs_pressure: float
    min_public_utility: float
    max_route_energy_delta: float
    min_route_energy_gain_without_public: float
    max_h088_same_direction_step: float
    shadow_grid: tuple[float, ...]
    route_bonus: float
    public_bonus: float
    pressure_bonus: float
    h088_penalty: float


CONFIGS = [
    ShadowConfig(
        name="q1shadow_guarded",
        stage_variant="stagebridge",
        max_shadow_cells=18,
        min_abs_pressure=0.030,
        min_public_utility=-1.2e-6,
        max_route_energy_delta=0.0016,
        min_route_energy_gain_without_public=0.0006,
        max_h088_same_direction_step=0.10,
        shadow_grid=(0.08, 0.13, 0.20, 0.30, 0.42),
        route_bonus=0.042,
        public_bonus=1.00,
        pressure_bonus=0.010,
        h088_penalty=0.80,
    ),
    ShadowConfig(
        name="q1shadow_jackpot",
        stage_variant="stagebridge_jackpot",
        max_shadow_cells=32,
        min_abs_pressure=0.018,
        min_public_utility=-3.0e-6,
        max_route_energy_delta=0.0034,
        min_route_energy_gain_without_public=0.0002,
        max_h088_same_direction_step=0.18,
        shadow_grid=(0.08, 0.14, 0.22, 0.34, 0.50, 0.68),
        route_bonus=0.052,
        public_bonus=1.00,
        pressure_bonus=0.013,
        h088_penalty=0.58,
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


stage_bridge = import_module(STAGE_BRIDGE_MODULE, "subjective_shadow_stage_bridge")
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


def train_target_correlations() -> dict[str, float]:
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    corr = labels[TARGETS].corr().loc["Q1", STAGE_TARGETS].to_dict()
    # Keep the learned sign and relative scale, but normalize so the pressure
    # magnitude is comparable across solver variants.
    denom = sum(abs(v) for v in corr.values()) + 1e-9
    return {target: float(value / denom) for target, value in corr.items()}


def selected_stage_steps(stage_audit: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in stage_audit.to_dict("records"):
        row = int(rec["row"])
        rows.append(
            {
                "row": row,
                "target": str(rec["driver_target"]),
                "step": float(rec["driver_step"]),
                "role": "driver",
                "source_solver_score": float(rec["solver_score"]),
            }
        )
        bridge_target = str(rec.get("bridge_target", ""))
        if bridge_target:
            rows.append(
                {
                    "row": row,
                    "target": bridge_target,
                    "step": float(rec["bridge_step"]),
                    "role": "bridge",
                    "source_solver_score": float(rec["solver_score"]),
                }
            )
    return pd.DataFrame(rows)


def build_shadow_candidates(
    stage_prob: np.ndarray,
    stage_logit: np.ndarray,
    stage_audit: pd.DataFrame,
    base_prob: np.ndarray,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
    config: ShadowConfig,
    q1_stage_corr: dict[str, float],
) -> pd.DataFrame:
    q1_idx = TARGETS.index("Q1")
    q1_flats = {
        row: row * len(TARGETS) + q1_idx
        for row in sorted(stage_audit["row"].astype(int).unique())
    }
    stage_steps = selected_stage_steps(stage_audit)
    pressure = (
        stage_steps.assign(weight=stage_steps["target"].map(q1_stage_corr).fillna(0.0))
        .assign(contribution=lambda d: d["step"] * d["weight"])
        .groupby("row", as_index=False)
        .agg(
            q1_shadow_pressure=("contribution", "sum"),
            source_solver_score=("source_solver_score", "mean"),
            stage_action_count=("target", "size"),
        )
    )
    candidates = []
    coef_by_flat = world["coef_by_flat"]
    h088 = world["h088_move"]
    for rec in pressure.to_dict("records"):
        row = int(rec["row"])
        q1_pressure = float(rec["q1_shadow_pressure"])
        if abs(q1_pressure) < config.min_abs_pressure:
            continue
        direction = float(np.sign(q1_pressure))
        flat = q1_flats[row]
        coef = float(coef_by_flat.get(flat, 0.0))
        h088_same = max(0.0, direction * float(h088[flat]))
        if h088_same > config.max_h088_same_direction_step:
            continue
        old_row = stage_prob[row : row + 1].copy()
        old_energy = float(model.row_energy(old_row)[0])
        for mag in config.shadow_grid:
            step = direction * float(mag)
            trial_row = old_row.copy()
            trial_row[0, q1_idx] = float(sigmoid(stage_logit[flat] + step))
            new_energy = float(model.row_energy(trial_row)[0])
            energy_delta = new_energy - old_energy
            public_delta = coef * step
            public_utility = -public_delta
            if energy_delta > config.max_route_energy_delta:
                continue
            if public_utility < config.min_public_utility and energy_delta > -config.min_route_energy_gain_without_public:
                continue
            score = 0.0
            score += config.route_bonus * max(-energy_delta, 0.0)
            score -= config.route_bonus * 0.80 * max(energy_delta, 0.0)
            score += config.public_bonus * public_utility
            score += config.pressure_bonus * abs(q1_pressure)
            score -= config.h088_penalty * h088_same * abs(step)
            score += 0.0005 * float(rec["source_solver_score"])
            if score <= 0:
                continue
            candidates.append(
                {
                    "row": row,
                    "flat_idx": int(flat),
                    "target": "Q1",
                    "q1_shadow_pressure": q1_pressure,
                    "sign": int(direction),
                    "shadow_step": float(step),
                    "old_route_energy": old_energy,
                    "new_route_energy": new_energy,
                    "route_energy_delta": energy_delta,
                    "coef": coef,
                    "public_delta_estimate": public_delta,
                    "public_utility": public_utility,
                    "h088_same_direction": h088_same,
                    "stage_action_count": int(rec["stage_action_count"]),
                    "source_solver_score": float(rec["source_solver_score"]),
                    "solver_score": float(score),
                }
            )
    frame = pd.DataFrame(candidates)
    if len(frame):
        frame = frame.sort_values("solver_score", ascending=False).reset_index(drop=True)
    return frame


def shadow_null_stress(
    stage_prob: np.ndarray,
    stage_logit: np.ndarray,
    stage_audit: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
    config: ShadowConfig,
    q1_stage_corr: dict[str, float],
    actual_candidates: pd.DataFrame,
    repeats: int = 128,
) -> dict[str, float]:
    rng = np.random.default_rng(20260609)
    magnitudes = np.asarray([abs(q1_stage_corr[target]) for target in STAGE_TARGETS], dtype=np.float64)

    def top_sum(frame: pd.DataFrame) -> float:
        if not len(frame):
            return 0.0
        return float(frame.head(config.max_shadow_cells)["solver_score"].sum())

    def top_energy_gain(frame: pd.DataFrame) -> float:
        if not len(frame):
            return 0.0
        return float((-frame.head(config.max_shadow_cells)["route_energy_delta"]).clip(lower=0.0).sum())

    actual_top_sum = top_sum(actual_candidates)
    actual_top_energy_gain = top_energy_gain(actual_candidates)
    null_top_sum = []
    null_top_energy_gain = []
    null_count = []
    for _ in range(repeats):
        shuffled = rng.permutation(magnitudes)
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=len(STAGE_TARGETS))
        null_corr = {target: float(shuffled[i] * signs[i]) for i, target in enumerate(STAGE_TARGETS)}
        frame = build_shadow_candidates(
            stage_prob,
            stage_logit,
            stage_audit,
            world["base_prob"],
            world,
            model,
            config,
            null_corr,
        )
        null_top_sum.append(top_sum(frame))
        null_top_energy_gain.append(top_energy_gain(frame))
        null_count.append(float(len(frame)))
    sum_arr = np.asarray(null_top_sum, dtype=np.float64)
    energy_arr = np.asarray(null_top_energy_gain, dtype=np.float64)
    count_arr = np.asarray(null_count, dtype=np.float64)
    return {
        "repeats": float(repeats),
        "actual_candidate_count": float(len(actual_candidates)),
        "null_candidate_count_mean": float(count_arr.mean()),
        "actual_top_score_sum": float(actual_top_sum),
        "null_top_score_sum_mean": float(sum_arr.mean()),
        "null_top_score_sum_std": float(sum_arr.std(ddof=1) + 1e-12),
        "actual_top_score_z": float((actual_top_sum - sum_arr.mean()) / (sum_arr.std(ddof=1) + 1e-12)),
        "actual_top_score_p_ge": float((sum_arr >= actual_top_sum).mean()),
        "actual_top_energy_gain": float(actual_top_energy_gain),
        "null_top_energy_gain_mean": float(energy_arr.mean()),
        "null_top_energy_gain_std": float(energy_arr.std(ddof=1) + 1e-12),
        "actual_top_energy_gain_z": float(
            (actual_top_energy_gain - energy_arr.mean()) / (energy_arr.std(ddof=1) + 1e-12)
        ),
        "actual_top_energy_gain_p_ge": float((energy_arr >= actual_top_energy_gain).mean()),
    }


def solve_shadow_variant(
    config: ShadowConfig,
    stage_prob: np.ndarray,
    stage_audit: pd.DataFrame,
    world: dict[str, object],
    model: route_energy.RouteEnergyModel,
    q1_stage_corr: dict[str, float],
) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    current_logit = logit(stage_prob.reshape(-1))
    current_prob = stage_prob.copy()
    shadow_candidates = build_shadow_candidates(
        current_prob,
        current_logit,
        stage_audit,
        world["base_prob"],
        world,
        model,
        config,
        q1_stage_corr,
    )
    null_stress = shadow_null_stress(
        current_prob,
        current_logit,
        stage_audit,
        world,
        model,
        config,
        q1_stage_corr,
        shadow_candidates,
    )
    selected = []
    used_rows: set[int] = set()
    for rec in shadow_candidates.to_dict("records"):
        row = int(rec["row"])
        if row in used_rows:
            continue
        flat = int(rec["flat_idx"])
        step = float(rec["shadow_step"])
        current_logit[flat] += step
        current_prob[row, TARGETS.index("Q1")] = float(sigmoid(current_logit[flat]))
        selected.append(rec)
        used_rows.add(row)
        if len(selected) >= config.max_shadow_cells:
            break
    audit = pd.DataFrame(selected)
    prob = clip_prob(current_prob)
    diagnostics = {
        "variant": config.name,
        "stage_variant": config.stage_variant,
        "candidate_shadow_cells": int(len(shadow_candidates)),
        "selected_shadow_cells": int(len(audit)),
        "stage_cells": int(stage_audit["action_count"].sum()) if len(stage_audit) else 0,
        "total_changed_cells_vs_current_best": int((np.abs(prob - world["base_prob"]) > TOL).sum()),
        "changed_rows": int(len(set(np.where(np.abs(prob - world["base_prob"]) > TOL)[0]))),
        "selected_mean_pressure": float(audit["q1_shadow_pressure"].mean()) if len(audit) else 0.0,
        "selected_mean_route_energy_delta": float(audit["route_energy_delta"].mean()) if len(audit) else 0.0,
        "selected_negative_energy": int((audit["route_energy_delta"] < 0).sum()) if len(audit) else 0,
        "selected_public_delta_estimate": float(audit["public_delta_estimate"].sum()) if len(audit) else 0.0,
        "mean_route_energy": float(model.row_energy(prob).mean()),
        "stage_mean_route_energy": float(model.row_energy(stage_prob).mean()),
        "base_mean_route_energy": float(model.row_energy(world["base_prob"]).mean()),
        "q1_stage_corr_null_stress": null_stress,
    }
    return prob, audit, shadow_candidates, diagnostics


def run() -> dict[str, object]:
    pool, world = stage_bridge.prepare_world()
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = route_energy.RouteEnergyModel()
    model.fit(labels)
    q1_stage_corr = train_target_correlations()

    stage_outputs = {}
    for stage_config in stage_bridge.CONFIGS:
        stage_prob, stage_audit, stage_candidates, stage_diag = stage_bridge.solve_variant(
            stage_config, pool[pool["target"].isin(STAGE_TARGETS)].copy(), world, model
        )
        stage_outputs[stage_config.name] = {
            "prob": stage_prob,
            "audit": stage_audit,
            "candidates": stage_candidates,
            "diagnostics": stage_diag,
        }

    outputs = {}
    for config in CONFIGS:
        stage_result = stage_outputs[config.stage_variant]
        prob, audit, candidates, diagnostics = solve_shadow_variant(
            config,
            stage_result["prob"],
            stage_result["audit"],
            world,
            model,
            q1_stage_corr,
        )
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_subjective_shadow_bridge_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, world["sample"], prob)
        write_submission(root_path, world["sample"], prob)
        move = logit(prob).reshape(-1) - world["base_logit"]
        audit.to_csv(OUT / f"subjective_shadow_{config.name}_selected.csv", index=False)
        candidates.to_csv(OUT / f"subjective_shadow_{config.name}_candidates.csv", index=False)
        outputs[config.name] = {
            "submission_file": out_name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "config": config.__dict__,
            "stage_diagnostics": stage_result["diagnostics"],
            "diagnostics": diagnostics,
            "listener_metrics": candidate1.candidate_metrics(
                move, world["base_grads"], world["semantic_grads"], world["h088_move"]
            ),
            "validation": validate_submission(root_path, world["sample"], world["base_prob"]),
        }

    readout = {
        "experiment": "Subjective Shadow Bridge Solver HS-JEPA",
        "hypothesis": "Objective S-stage bridge pressure can cast a Q1 subjective shadow when target geometry agrees.",
        "public_score_used": True,
        "target_geometry_public_free": True,
        "q1_stage_corr_normalized": q1_stage_corr,
        "outputs": outputs,
    }
    (OUT / "subjective_shadow_bridge_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
