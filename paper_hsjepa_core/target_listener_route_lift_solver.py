#!/usr/bin/env python3
"""Target-listener route lift solver for HS-JEPA.

Previous OG distillation showed an asymmetric result:

* target/cell action support is visible from OG human-state context;
* row-level action assignment is weak when the row is predicted directly.

This experiment tests a sharper architecture claim:

    Do not predict row assignment directly.  Predict target-listener support
    first, then lift it back to row actions through route-energy constraints.

The output is a diagnostic big-bet submission family.  It is not a local alpha
retune: it changes the assignment rule from row-first to target-listener-first.
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
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "target_listener_route_lift_solver"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12

S2_DISTILL_MODULE = HERE / "s2hub_human_state_distillation.py"
STAGE_BRIDGE_MODULE = HERE / "stage_bridge_conservation_solver.py"

S2HUB_TEACHER_FILE = "submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv"
STAGEBRIDGE_TEACHER_FILE = "submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv"


@dataclass(frozen=True)
class LiftConfig:
    name: str
    teacher_name: str
    teacher_file: str
    teacher_amp: float
    extra_cells: int
    extra_amp: float
    max_logit_step: float
    min_full_prob_quantile: float
    max_cells_per_row: int
    max_cells_per_target: int
    max_route_energy_increase: float
    allowed_targets: tuple[str, ...]
    s2_bonus: float
    stage_bonus: float


CONFIGS = [
    LiftConfig(
        name="s2hub_listener_lift_core",
        teacher_name="s2hub_jackpot",
        teacher_file=S2HUB_TEACHER_FILE,
        teacher_amp=0.98,
        extra_cells=24,
        extra_amp=0.42,
        max_logit_step=0.58,
        min_full_prob_quantile=0.975,
        max_cells_per_row=1,
        max_cells_per_target=16,
        max_route_energy_increase=0.0014,
        allowed_targets=("S1", "S2", "S3", "S4"),
        s2_bonus=1.35,
        stage_bonus=1.12,
    ),
    LiftConfig(
        name="s2hub_listener_lift_jackpot",
        teacher_name="s2hub_jackpot",
        teacher_file=S2HUB_TEACHER_FILE,
        teacher_amp=1.03,
        extra_cells=54,
        extra_amp=0.56,
        max_logit_step=0.82,
        min_full_prob_quantile=0.955,
        max_cells_per_row=2,
        max_cells_per_target=28,
        max_route_energy_increase=0.0032,
        allowed_targets=("Q2", "Q3", "S1", "S2", "S3", "S4"),
        s2_bonus=1.42,
        stage_bonus=1.08,
    ),
    LiftConfig(
        name="stagebridge_listener_lift_jackpot",
        teacher_name="stagebridge_jackpot",
        teacher_file=STAGEBRIDGE_TEACHER_FILE,
        teacher_amp=1.00,
        extra_cells=46,
        extra_amp=0.50,
        max_logit_step=0.74,
        min_full_prob_quantile=0.962,
        max_cells_per_row=2,
        max_cells_per_target=24,
        max_route_energy_increase=0.0026,
        allowed_targets=("S1", "S2", "S3", "S4"),
        s2_bonus=1.28,
        stage_bonus=1.10,
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


s2_distill = import_module(S2_DISTILL_MODULE, "target_listener_s2_distill")
stage_bridge = import_module(STAGE_BRIDGE_MODULE, "target_listener_stage_bridge")
candidate1 = s2_distill.candidate1
route_energy = stage_bridge.route_energy


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


def load_submission(path_or_name: str | Path) -> pd.DataFrame:
    path = Path(path_or_name)
    if not path.is_absolute():
        path = ROOT / path
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


def metric_safe(y: np.ndarray, score: np.ndarray) -> dict[str, float | None]:
    if len(np.unique(y)) < 2:
        return {"auc": None, "ap": float(y.mean())}
    return {
        "auc": float(roc_auc_score(y, score)),
        "ap": float(average_precision_score(y, score)),
    }


def row_lift_metrics(frame: pd.DataFrame, score_col: str) -> dict[str, dict[str, float | None]]:
    row = frame.groupby("row").agg(
        y=("teacher_has_action", "max"),
        max_score=(score_col, "max"),
        mean_score=(score_col, "mean"),
        top2_score=(score_col, lambda s: s.nlargest(2).mean()),
        s2_score=(score_col, lambda s: float(s.iloc[1]) if len(s) > 1 else float(s.max())),
    )
    return {
        name: metric_safe(row["y"].to_numpy(dtype=int), row[name].to_numpy(dtype=np.float64))
        for name in ["max_score", "mean_score", "top2_score", "s2_score"]
    }


def prepare_teacher_frame(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    config: LiftConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, list[str], dict[str, object]]:
    teacher_prob = load_submission(config.teacher_file)[TARGETS].to_numpy(dtype=np.float64)
    base_frame, feature_cols = s2_distill.human_distill.build_cell_frame(sample, base_prob, teacher_prob)
    frame, _ = s2_distill.add_teacher(base_frame, sample, base_prob, config.teacher_file)
    cols = s2_distill.feature_sets(feature_cols)["human_target_context"]
    oof_prob, oof_move, oof_diag = s2_distill.oof_cell_student(frame, cols, sample)
    full_prob, full_move = s2_distill.full_cell_student(frame, cols)
    frame = frame.copy()
    frame["oof_listener_prob"] = oof_prob
    frame["oof_listener_move"] = oof_move
    frame["full_listener_prob"] = full_prob
    frame["full_listener_move"] = full_move
    frame["flat_idx"] = frame["row"].astype(int) * len(TARGETS) + frame["target_idx_int"].astype(int)
    row_metrics = row_lift_metrics(frame, "oof_listener_prob")
    diagnostics = {
        "cell_oof": oof_diag,
        "row_lift_from_oof_cell": row_metrics,
    }
    return frame, load_submission(config.teacher_file), teacher_prob, cols, diagnostics


def listener_score(frame: pd.DataFrame, config: LiftConfig) -> pd.Series:
    target = frame["target"].astype(str)
    target_bonus = np.ones(len(frame), dtype=np.float64)
    target_bonus *= np.where(target.eq("S2"), config.s2_bonus, 1.0)
    target_bonus *= np.where(target.str.startswith("S"), config.stage_bonus, 1.0)
    health = frame.get("atlas_action_health", pd.Series(0.5, index=frame.index)).to_numpy(dtype=np.float64)
    uncertainty = frame.get("base_uncertainty", pd.Series(0.5, index=frame.index)).to_numpy(dtype=np.float64)
    peer_margin = frame.get("target_peer_margin_abs", pd.Series(0.0, index=frame.index)).to_numpy(dtype=np.float64)
    move_mag = np.minimum(np.abs(frame["full_listener_move"].to_numpy(dtype=np.float64)), config.max_logit_step)
    score = (
        frame["full_listener_prob"].to_numpy(dtype=np.float64)
        * (0.62 + 0.70 * health)
        * (0.70 + 0.45 * uncertainty)
        * (1.0 + 0.18 * peer_margin)
        * (0.50 + move_mag)
        * target_bonus
    )
    return pd.Series(score, index=frame.index)


def solve_variant(
    config: LiftConfig,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    base_grads: np.ndarray,
    semantic_grads: np.ndarray,
    h088_move: np.ndarray,
    energy_model: route_energy.RouteEnergyModel,
    prepared: tuple[pd.DataFrame, pd.DataFrame, np.ndarray, list[str], dict[str, object]] | None = None,
) -> dict[str, object]:
    if prepared is None:
        prepared = prepare_teacher_frame(sample, base_prob, config)
    frame, _teacher_df, teacher_prob, _cols, student_diag = prepared
    base_z = logit(base_prob).reshape(-1)
    teacher_move = logit(teacher_prob).reshape(-1) - base_z
    decoded_move = np.zeros_like(teacher_move)
    teacher_mask = np.abs(teacher_move) > TOL
    decoded_move[teacher_mask] = teacher_move[teacher_mask] * config.teacher_amp

    frame = frame.copy()
    frame["teacher_action"] = teacher_mask[frame["flat_idx"].to_numpy(dtype=int)]
    frame["listener_score"] = listener_score(frame, config)
    thresh = float(frame["full_listener_prob"].quantile(config.min_full_prob_quantile))
    pool = frame[
        (~frame["teacher_action"])
        & frame["target"].isin(config.allowed_targets)
        & (frame["full_listener_prob"] >= thresh)
        & (np.abs(frame["full_listener_move"]) > 1e-5)
    ].sort_values("listener_score", ascending=False)

    current_prob = clip_prob(sigmoid(base_z + decoded_move).reshape(base_prob.shape))
    selected: list[dict[str, object]] = []
    row_counts: dict[int, int] = {}
    target_counts: dict[str, int] = {}

    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if row_counts.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_counts.get(target, 0) >= config.max_cells_per_target:
            continue
        flat = int(rec["flat_idx"])
        move = float(np.clip(config.extra_amp * rec["full_listener_move"], -config.max_logit_step, config.max_logit_step))
        if abs(move) <= 1e-8:
            continue
        trial = current_prob[row : row + 1].copy()
        old_energy = float(energy_model.row_energy(trial)[0])
        trial[0, TARGETS.index(target)] = float(sigmoid(base_z[flat] + decoded_move[flat] + move))
        new_energy = float(energy_model.row_energy(trial)[0])
        energy_delta = new_energy - old_energy
        if energy_delta > config.max_route_energy_increase:
            continue
        decoded_move[flat] += move
        current_prob[row, TARGETS.index(target)] = trial[0, TARGETS.index(target)]
        row_counts[row] = row_counts.get(row, 0) + 1
        target_counts[target] = target_counts.get(target, 0) + 1
        selected.append(
            {
                **rec,
                "decoded_logit_move": move,
                "route_energy_delta": energy_delta,
                "old_row_energy": old_energy,
                "new_row_energy": new_energy,
                "source": "listener_lift_extra",
            }
        )
        if len(selected) >= config.extra_cells:
            break

    decoded_prob = clip_prob(sigmoid(base_z + decoded_move).reshape(base_prob.shape))
    digest = short_hash(decoded_prob)
    out_name = f"submission_hsjepa_target_listener_route_lift_{config.name}_{digest}_uploadsafe.csv"
    local_path = OUT / out_name
    root_path = ROOT / out_name
    write_submission(local_path, sample, decoded_prob)
    write_submission(root_path, sample, decoded_prob)

    teacher_audit = frame[frame["teacher_action"]].copy()
    teacher_audit["source"] = "teacher_scaled"
    teacher_audit["decoded_logit_move"] = teacher_move[teacher_audit["flat_idx"].to_numpy(dtype=int)] * config.teacher_amp
    teacher_audit["route_energy_delta"] = np.nan
    audit = pd.concat([teacher_audit, pd.DataFrame(selected)], ignore_index=True, sort=False)
    audit_path = OUT / f"{config.name}_action_audit.csv"
    pool_path = OUT / f"{config.name}_candidate_pool.csv"
    audit.to_csv(audit_path, index=False)
    pool.to_csv(pool_path, index=False)

    move = logit(decoded_prob).reshape(-1) - base_logit
    diagnostics = {
        "variant": config.name,
        "teacher_name": config.teacher_name,
        "teacher_file": config.teacher_file,
        "config": config.__dict__,
        "student_diagnostics": student_diag,
        "teacher_cells": int(teacher_mask.sum()),
        "teacher_rows": int(len(set(np.where(teacher_mask.reshape(base_prob.shape))[0]))),
        "extra_pool_cells": int(len(pool)),
        "extra_selected_cells": int(len(selected)),
        "extra_selected_rows": int(len({int(x["row"]) for x in selected})),
        "target_counts_extra": target_counts,
        "mean_extra_route_energy_delta": float(np.mean([x["route_energy_delta"] for x in selected])) if selected else 0.0,
        "mean_route_energy": float(energy_model.row_energy(decoded_prob).mean()),
        "base_mean_route_energy": float(energy_model.row_energy(base_prob).mean()),
        "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
        "validation": validate_submission(root_path, sample, base_prob),
        "submission_file": out_name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "audit_path": str(audit_path.resolve()),
        "pool_path": str(pool_path.resolve()),
    }
    return diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    energy_model = route_energy.RouteEnergyModel()
    energy_model.fit(train_labels)

    outputs = {}
    prepared_by_teacher: dict[str, tuple[pd.DataFrame, pd.DataFrame, np.ndarray, list[str], dict[str, object]]] = {}
    for config in CONFIGS:
        if config.teacher_file not in prepared_by_teacher:
            prepared_by_teacher[config.teacher_file] = prepare_teacher_frame(sample, base_prob, config)
        outputs[config.name] = solve_variant(
            config,
            sample,
            base_prob,
            base_logit,
            base_grads,
            semantic_grads,
            h088_move,
            energy_model,
            prepared_by_teacher[config.teacher_file],
        )

    readout = {
        "experiment": "Target-Listener Route Lift Solver HS-JEPA",
        "question": "Can OG target-listener posterior be lifted into row-target actions through route energy?",
        "public_score_used_for_teacher": True,
        "student_context_public_free": True,
        "route_energy_public_free": True,
        "interpretation_rule": (
            "If cell OOF is high but row-lift AUC remains weak, HS-JEPA needs a separate "
            "listener/assignment solver. If listener-lift submissions improve, target-listener "
            "posterior is action-grade despite weak direct row prediction."
        ),
        "outputs": outputs,
    }
    (OUT / "target_listener_route_lift_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
