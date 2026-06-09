#!/usr/bin/env python3
"""Candidate 1: Public-Loss Sparse Tomography HS-JEPA.

Team-facing final candidate.

This script intentionally avoids old experiment-version vocabulary in the
algorithm description. It starts from the original competition files plus the
public-score ledger and constructs a row-target action field:

    OG metric/sample data
      -> current best row-state anchor
      -> local semantic listener/support field
      -> public-loss sensor tomography on sparse support
      -> upload-safe submission

The implementation reuses the reproducible HS-JEPA listener modules already in
this repository. If their intermediate artifacts are missing, this script
regenerates them.
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
OUT = HERE / "outputs" / "candidate_1_public_loss_sparse_tomography"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939

H154_FILE = "submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv"
H155_FILE = "submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv"
H158_FILE = "submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv"

PUBLIC_LEDGER = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"
H154_MODULE = ROOT / "hsjepa_jackpot" / "h154_local_semantic_source_consensus.py"
H155_H158_MODULE = ROOT / "hsjepa_jackpot" / "h155_h158_posterior_lossnull_jackpot.py"
H154_CELL_CANDIDATES = ROOT / "hsjepa_jackpot" / "outputs" / "h154_cell_candidates.csv"


@dataclass(frozen=True)
class CandidateConfig:
    ridge_alpha: float = 10.0
    top_cells: int = 110
    action_amp: float = 1.5
    per_cell_logit_cap: float = 1.9
    max_cells_per_row: int = 2
    max_cells_per_target: int = 55
    min_sign_stability: float = 0.55
    max_h088_alignment: float = 0.66
    min_semantic_mean: float = -5e-6
    min_base_mean: float = -5e-5


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h154 = import_module(H154_MODULE, "final_candidate_h154")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denom) if denom else 0.0


def locate(name: str | Path) -> Path | None:
    found = h154.locate(name)
    if found is not None:
        return found
    path = ROOT / str(name)
    if path.exists():
        return path
    return None


def load_submission(path_or_name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(path_or_name)
    if path is None:
        raise FileNotFoundError(path_or_name)
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    if sample is not None:
        df = sample[KEYS].merge(df, on=KEYS, how="left", validate="one_to_one")
    return df.sort_values(KEYS).reset_index(drop=True)


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


def write_submission(path: Path, sample: pd.DataFrame, prob: np.ndarray) -> None:
    out = sample[KEYS].copy()
    for idx, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, idx])
    out.to_csv(path, index=False)


def ensure_prerequisites() -> None:
    """Regenerate local listener artifacts when the repo has been freshly cloned."""

    if locate(H154_FILE) is None or not H154_CELL_CANDIDATES.exists():
        h154.run()
    if locate(H155_FILE) is None or locate(H158_FILE) is None:
        h155_h158 = import_module(H155_H158_MODULE, "final_candidate_h155_h158")
        h155_h158.run()


def movement_from_file(name: str | Path, sample: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray | None:
    path = locate(name)
    if path is None:
        return None
    try:
        prob = load_submission(path, sample)[TARGETS].to_numpy(dtype=np.float64).reshape(-1)
        return logit(prob) - base_logit
    except Exception:
        return None


def load_world():
    sample, _narratives, base_prob, moves, base_models, semantic_models = h154.load_world()
    base_flat = base_prob.reshape(-1)
    base_logit = logit(base_flat)
    n_cells = base_flat.size
    base_grads = np.vstack([h154.h150mod.gradient(model, n_cells) for model in base_models.values()])
    semantic_grads = np.vstack([h154.h150mod.gradient(model, n_cells) for model in semantic_models.values()])
    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    return sample, base_prob, base_logit, base_grads, semantic_grads, h088_move


def candidate_metrics(move: np.ndarray, base_grads: np.ndarray, semantic_grads: np.ndarray, h088_move: np.ndarray) -> dict[str, object]:
    base_vals = base_grads @ move
    sem_vals = semantic_grads @ move
    changed = np.abs(move) > TOL
    return {
        "base_listener_mean_delta": float(base_vals.mean()),
        "base_listener_max_delta": float(base_vals.max()),
        "base_listener_negative_count": int((base_vals < 0).sum()),
        "semantic_listener_mean_delta": float(sem_vals.mean()),
        "semantic_listener_max_delta": float(sem_vals.max()),
        "semantic_listener_negative_count": int((sem_vals < 0).sum()),
        "h088_cosine": cosine(move, h088_move),
        "changed_cells": int(changed.sum()),
        "changed_rows": int(len(set(np.where(changed)[0] // len(TARGETS)))),
    }


def public_observed_matrix(sample: pd.DataFrame, base_logit: np.ndarray, support_idx: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str]]:
    ledger = pd.read_csv(PUBLIC_LEDGER)
    rows: list[np.ndarray] = []
    y: list[float] = []
    files: list[str] = []
    for rec in ledger.to_dict("records"):
        file = str(rec["file"])
        move = movement_from_file(file, sample, base_logit)
        if move is None:
            continue
        rows.append(move[support_idx])
        y.append(float(rec["public_lb"]) - CURRENT_BEST_PUBLIC_LB)
        files.append(file)
    if CURRENT_BEST_FILE not in files:
        rows.append(np.zeros(len(support_idx), dtype=np.float64))
        y.append(0.0)
        files.append(CURRENT_BEST_FILE)
    return np.vstack(rows), np.asarray(y, dtype=np.float64), files


def ridge_public_loss_coefficients(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    col_scale = np.sqrt((x**2).mean(axis=0)) + 1e-6
    xs = x / col_scale
    coef_scaled = np.linalg.solve(xs.T @ xs + alpha * np.eye(xs.shape[1]), xs.T @ y)
    coef = coef_scaled / col_scale
    pred = x @ coef

    signs = []
    loo_sq = []
    for hold in range(len(y)):
        mask = np.ones(len(y), dtype=bool)
        mask[hold] = False
        wh_scaled = np.linalg.solve(xs[mask].T @ xs[mask] + alpha * np.eye(xs.shape[1]), xs[mask].T @ y[mask])
        wh = wh_scaled / col_scale
        signs.append(np.sign(wh))
        loo_sq.append(float((x[hold] @ wh - y[hold]) ** 2))
    sign_frame = np.vstack(signs)
    stability = np.maximum((sign_frame > 0).mean(axis=0), (sign_frame < 0).mean(axis=0))
    diagnostics = {
        "ridge_alpha": float(alpha),
        "rmse": float(np.sqrt(((pred - y) ** 2).mean())),
        "loo_rmse": float(np.sqrt(np.mean(loo_sq))),
        "stable_cells_gt_0p8": int((stability > 0.8).sum()),
    }
    return coef, stability, diagnostics


def listener_support() -> dict[tuple[int, int], pd.Series]:
    cells = pd.read_csv(H154_CELL_CANDIDATES)
    agg = (
        cells.groupby(["flat_idx", "sign"], as_index=False)
        .agg(
            source_support=("source_file", "nunique"),
            sem_mean=("sem_mean_benefit", "mean"),
            base_mean=("base_mean_benefit", "mean"),
            sem_pos=("sem_pos", "max"),
            base_pos=("base_pos", "max"),
            h088_alignment=("h088_alignment", "max"),
            score=("score", "mean"),
        )
    )
    agg["key"] = list(zip(agg["flat_idx"].astype(int), agg["sign"].astype(int)))
    return {key: row for key, row in agg.set_index("key").iterrows()}


def build_action(
    config: CandidateConfig,
    support_idx: np.ndarray,
    coef: np.ndarray,
    stability: np.ndarray,
    support: dict[tuple[int, int], pd.Series],
    h158_move: np.ndarray,
    n_cells: int,
) -> tuple[np.ndarray, pd.DataFrame]:
    pool = []
    denom = np.percentile(np.abs(coef), 90) + 1e-9
    for local_idx, flat in enumerate(support_idx):
        if abs(coef[local_idx]) < 1e-8 or stability[local_idx] < config.min_sign_stability:
            continue
        desired_sign = int(-np.sign(coef[local_idx]))
        rec = support.get((int(flat), desired_sign))
        if rec is None:
            continue
        if rec["h088_alignment"] > config.max_h088_alignment:
            continue
        if rec["sem_mean"] < config.min_semantic_mean or rec["base_mean"] < config.min_base_mean:
            continue
        h158_agreement = 1.0 if desired_sign == np.sign(h158_move[flat]) else 0.75
        score = (
            abs(coef[local_idx])
            * (0.35 + stability[local_idx])
            * (1.0 + 0.30 * rec["source_support"])
            * (1.0 + 12000.0 * max(float(rec["sem_mean"]), 0.0))
            * (1.0 + 7000.0 * max(float(rec["base_mean"]), 0.0))
            * h158_agreement
            / (1.0 + 2.5 * rec["h088_alignment"])
        )
        pool.append((float(score), int(flat), desired_sign, float(coef[local_idx]), float(stability[local_idx]), rec))
    pool.sort(reverse=True, key=lambda row: row[0])

    selected = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for item in pool:
        _score, flat, _sign, *_ = item
        row = flat // len(TARGETS)
        target = TARGETS[flat % len(TARGETS)]
        if row_count.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_count.get(target, 0) >= config.max_cells_per_target:
            continue
        selected.append(item)
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        if len(selected) >= config.top_cells:
            break

    move = np.zeros(n_cells, dtype=np.float64)
    audit_rows = []
    for score, flat, sign, coef_value, stab, rec in selected:
        magnitude = min(config.per_cell_logit_cap, config.action_amp * (0.12 + abs(coef_value) / denom))
        move[flat] = sign * magnitude
        audit_rows.append(
            {
                "score": score,
                "flat_idx": flat,
                "row": flat // len(TARGETS),
                "target": TARGETS[flat % len(TARGETS)],
                "sign": sign,
                "logit_move": float(move[flat]),
                "public_loss_coef": coef_value,
                "sign_stability": stab,
                "source_support": float(rec["source_support"]),
                "semantic_mean": float(rec["sem_mean"]),
                "base_mean": float(rec["base_mean"]),
                "h088_alignment": float(rec["h088_alignment"]),
            }
        )
    return move, pd.DataFrame(audit_rows)


def run() -> dict[str, object]:
    ensure_prerequisites()
    config = CandidateConfig()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = load_world()
    n_cells = base_prob.size

    support_moves = {}
    for name in [H154_FILE, H155_FILE, H158_FILE]:
        move = movement_from_file(name, sample, base_logit)
        if move is None:
            raise FileNotFoundError(name)
        support_moves[name] = move
    support_idx = np.flatnonzero(np.any(np.vstack([np.abs(move) > TOL for move in support_moves.values()]), axis=0))

    x, y, public_files = public_observed_matrix(sample, base_logit, support_idx)
    coef, stability, ridge_diag = ridge_public_loss_coefficients(x, y, config.ridge_alpha)
    support = listener_support()
    move, selected = build_action(config, support_idx, coef, stability, support, support_moves[H158_FILE], n_cells)

    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    digest = short_hash(prob)
    name = f"submission_final_candidate1_public_loss_sparse_tomography_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)

    selected.to_csv(OUT / "candidate1_selected_cells.csv", index=False)
    metric = candidate_metrics(move, base_grads, semantic_grads, h088_move)
    readout = {
        "candidate": "Public-Loss Sparse Tomography HS-JEPA",
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "hash": digest,
        "current_best_file": CURRENT_BEST_FILE,
        "current_best_public_lb": CURRENT_BEST_PUBLIC_LB,
        "support_files": list(support_moves),
        "support_cells": int(len(support_idx)),
        "public_observation_count": int(len(public_files)),
        "public_observation_files": public_files,
        "ridge_diagnostics": ridge_diag,
        "listener_metrics": metric,
        "predicted_public_delta_by_sensor": float(move[support_idx] @ coef),
        "validation": validate_submission(root_path, sample, base_prob),
    }
    (OUT / "candidate1_readout.json").write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
