#!/usr/bin/env python3
"""Route-Consistency Energy for HS-JEPA.

This experiment adds a JEPA-style energy diagnostic:

    Does a row-target action field keep the Q/S target vector on the train
    target-dependency manifold?

The energy model is trained only on train labels. It does not use public scores.
It is used as a diagnostic/veto head for competition candidates.
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

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_consistency_energy"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"


@dataclass(frozen=True)
class VetoConfig:
    energy_keep_tolerance: float = 0.0018
    teacher_energy_keep_tolerance: float = 0.0040
    q2_energy_keep_tolerance: float = 0.0048
    min_absolute_move: float = 1e-12


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "route_energy_candidate1")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def soft_bce(prob: np.ndarray, target_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(target_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def load_submission(path_or_name: str | Path) -> pd.DataFrame:
    path = Path(path_or_name)
    if not path.is_absolute():
        path = ROOT / path
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


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
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > 1e-12).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


class RouteEnergyModel:
    def __init__(self):
        self.models: dict[str, Pipeline] = {}
        self.target_indices = {target: i for i, target in enumerate(TARGETS)}

    def fit(self, labels: pd.DataFrame) -> None:
        y = labels[TARGETS].to_numpy(dtype=np.float64)
        for idx, target in enumerate(TARGETS):
            x = np.delete(y, idx, axis=1)
            model = Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    ("clf", LogisticRegression(max_iter=2000, C=0.85, solver="lbfgs")),
                ]
            )
            model.fit(x, y[:, idx].astype(int))
            self.models[target] = model

    def conditional_prob(self, prob: np.ndarray) -> np.ndarray:
        prob = clip_prob(prob)
        out = np.zeros_like(prob, dtype=np.float64)
        for idx, target in enumerate(TARGETS):
            x = np.delete(prob, idx, axis=1)
            out[:, idx] = self.models[target].predict_proba(x)[:, 1]
        return clip_prob(out)

    def row_energy(self, prob: np.ndarray) -> np.ndarray:
        cond = self.conditional_prob(prob)
        per_target = soft_bce(prob, cond)
        return per_target.mean(axis=1)

    def per_target_energy(self, prob: np.ndarray) -> dict[str, float]:
        cond = self.conditional_prob(prob)
        per_target = soft_bce(prob, cond)
        return {target: float(per_target[:, idx].mean()) for idx, target in enumerate(TARGETS)}

    def pair_moment_error(self, prob: np.ndarray, train_labels: pd.DataFrame) -> float:
        train = train_labels[TARGETS].to_numpy(dtype=np.float64)
        err = 0.0
        count = 0
        for i in range(len(TARGETS)):
            for j in range(i + 1, len(TARGETS)):
                train_pair = float((train[:, i] * train[:, j]).mean())
                cand_pair = float((prob[:, i] * prob[:, j]).mean())
                err += abs(cand_pair - train_pair)
                count += 1
        return float(err / max(count, 1))


def target_keep_tolerance(target: str, is_teacher: bool, config: VetoConfig) -> float:
    if target == "Q2":
        return config.q2_energy_keep_tolerance
    if is_teacher:
        return config.teacher_energy_keep_tolerance
    return config.energy_keep_tolerance


def route_veto_candidate(
    name: str,
    candidate_file: str,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    teacher_prob: np.ndarray,
    model: RouteEnergyModel,
    config: VetoConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    cand_prob = load_submission(candidate_file)[TARGETS].to_numpy(dtype=np.float64)
    out_prob = cand_prob.copy()
    teacher_move = np.abs(logit(teacher_prob).reshape(-1) - logit(base_prob).reshape(-1))
    changed = np.argwhere(np.abs(cand_prob - base_prob) > config.min_absolute_move)
    audit_rows = []
    for row, target_idx in changed:
        target = TARGETS[target_idx]
        full_vec = out_prob[row : row + 1].copy()
        revert_vec = full_vec.copy()
        revert_vec[0, target_idx] = base_prob[row, target_idx]
        full_energy = float(model.row_energy(full_vec)[0])
        revert_energy = float(model.row_energy(revert_vec)[0])
        flat = row * len(TARGETS) + target_idx
        is_teacher = bool(teacher_move[flat] > 1e-12)
        tolerance = target_keep_tolerance(target, is_teacher, config)
        keep = full_energy <= revert_energy + tolerance
        if not keep:
            out_prob[row, target_idx] = base_prob[row, target_idx]
        audit_rows.append(
            {
                "candidate": name,
                "row": int(row),
                "target": target,
                "flat_idx": int(flat),
                "is_teacher_cell": is_teacher,
                "candidate_prob": float(cand_prob[row, target_idx]),
                "base_prob": float(base_prob[row, target_idx]),
                "delta_prob": float(cand_prob[row, target_idx] - base_prob[row, target_idx]),
                "full_row_energy": full_energy,
                "revert_cell_energy": revert_energy,
                "energy_delta_if_keep": float(full_energy - revert_energy),
                "keep_tolerance": tolerance,
                "kept": bool(keep),
            }
        )
    audit = pd.DataFrame(audit_rows)
    diagnostics = {
        "candidate_file": candidate_file,
        "input_changed_cells": int(len(changed)),
        "kept_cells": int(audit["kept"].sum()) if len(audit) else 0,
        "vetoed_cells": int((~audit["kept"]).sum()) if len(audit) else 0,
        "input_mean_route_energy": float(model.row_energy(cand_prob).mean()),
        "output_mean_route_energy": float(model.row_energy(out_prob).mean()),
        "base_mean_route_energy": float(model.row_energy(base_prob).mean()),
        "kept_by_target": audit[audit["kept"]].groupby("target").size().to_dict() if len(audit) else {},
        "vetoed_by_target": audit[~audit["kept"]].groupby("target").size().to_dict() if len(audit) else {},
    }
    return clip_prob(out_prob), audit, diagnostics


def evaluate_candidates(
    files: dict[str, str],
    base_prob: np.ndarray,
    train_labels: pd.DataFrame,
    model: RouteEnergyModel,
) -> pd.DataFrame:
    rows = []
    base_energy = model.row_energy(base_prob)
    for name, file in files.items():
        prob = load_submission(file)[TARGETS].to_numpy(dtype=np.float64)
        energy = model.row_energy(prob)
        rows.append(
            {
                "candidate": name,
                "file": file,
                "mean_route_energy": float(energy.mean()),
                "delta_route_energy_vs_base": float(energy.mean() - base_energy.mean()),
                "p95_row_energy": float(np.quantile(energy, 0.95)),
                "pair_moment_error": model.pair_moment_error(prob, train_labels),
                "changed_cells_vs_base": int((np.abs(prob - base_prob) > 1e-12).sum()),
                **{f"{target}_energy": value for target, value in model.per_target_energy(prob).items()},
            }
        )
    return pd.DataFrame(rows).sort_values("mean_route_energy")


def run() -> dict[str, object]:
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    train_labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")
    model = RouteEnergyModel()
    model.fit(train_labels)

    files = {
        "current_best": CURRENT_BEST_FILE,
        "candidate1_public_loss_sparse": "submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv",
        "listener_responsibility": "submission_hsjepa_listener_responsibility_9990e658_uploadsafe.csv",
        "public_private_toxicity": "submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv",
        "target_route_teacher_only": "submission_hsjepa_target_route_toxicity_teacher_only_66f1f5b4_uploadsafe.csv",
        "target_route_q2_extra": "submission_hsjepa_target_route_toxicity_q2_extra_90b62d2d_uploadsafe.csv",
    }
    candidate_energy = evaluate_candidates(files, base_prob, train_labels, model)
    candidate_energy.to_csv(OUT / "route_consistency_candidate_energy.csv", index=False)

    teacher_prob = load_submission(files["candidate1_public_loss_sparse"])[TARGETS].to_numpy(dtype=np.float64)
    config = VetoConfig()
    veto_outputs = {}
    all_audits = []
    for name in ["public_private_toxicity", "target_route_q2_extra"]:
        prob, audit, diag = route_veto_candidate(name, files[name], sample, base_prob, teacher_prob, model, config)
        digest = short_hash(prob)
        out_name = f"submission_hsjepa_route_energy_veto_{name}_{digest}_uploadsafe.csv"
        local_path = OUT / out_name
        root_path = ROOT / out_name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        move = logit(prob).reshape(-1) - base_logit
        veto_outputs[name] = {
            "submission_file": out_name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "diagnostics": diag,
            "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
            "validation": validate_submission(root_path, sample, base_prob),
        }
        all_audits.append(audit)
    audit_frame = pd.concat(all_audits, ignore_index=True)
    audit_frame.to_csv(OUT / "route_energy_veto_audit.csv", index=False)

    readout = {
        "experiment": "Route-Consistency Energy HS-JEPA",
        "energy_model": "train-label conditional pseudo-likelihood over Q/S route vector",
        "public_score_used": False,
        "candidate_energy_table": str((OUT / "route_consistency_candidate_energy.csv").resolve()),
        "veto_config": config.__dict__,
        "veto_outputs": veto_outputs,
    }
    (OUT / "route_consistency_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
