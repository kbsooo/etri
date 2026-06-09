#!/usr/bin/env python3
"""H155-H158 posterior/listener jackpot experiments.

This script starts from the reproducible H154 local semantic listener and
tests a larger HS-JEPA claim:

1. H061 posterior is a candidate hidden public equation field.
2. H154 semantic source-consensus is a candidate listener-safe action field.
3. If both agree, their union can be treated as a row-target correction field.
4. Known public-loss axes should be removed only inside the sparse support,
   not as a dense global rewrite.

Promoted outputs:
    H155: H061 posterior filtered by H154 local semantic listener.
    H156: H154 + H155 combined action field.
    H158: H156 sparse support with known-loss projection removed.

H157 dense nullspace was intentionally rejected during exploration because it
spread the action over more than 1,000 cells.
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
OUT = ROOT / "hsjepa_jackpot" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

H154_PATH = ROOT / "hsjepa_jackpot" / "h154_local_semantic_source_consensus.py"
SPEC = importlib.util.spec_from_file_location("h154mod_h155_h158", H154_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H154_PATH}")
h154 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h154
SPEC.loader.exec_module(h154)

TARGETS = h154.TARGETS
TOL = h154.TOL

H154_ROOT = "submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv"
H061_POSTERIOR = ROOT / "hitl" / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
KNOWN_LOSS_FILES = [
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "submission_h145_q3repair_2d818e46_uploadsafe.csv",
]


@dataclass
class World:
    sample: pd.DataFrame
    base_prob: np.ndarray
    base_logit: np.ndarray
    moves: dict[str, np.ndarray]
    base_grads: np.ndarray
    semantic_grads: np.ndarray
    h088_move: np.ndarray


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def locate(name: str | Path) -> Path:
    found = h154.locate(name)
    if found is not None:
        return found
    path = ROOT / str(name)
    if path.exists():
        return path
    raise FileNotFoundError(name)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(a @ b / denom) if denom else 0.0


def movement_from_file(path_or_name: str | Path, world: World) -> np.ndarray:
    path = locate(path_or_name)
    prob = h154.load_sub(path, world.sample)[TARGETS].to_numpy(dtype=np.float64).reshape(-1)
    return h154.logit(prob) - world.base_logit


def metrics(move: np.ndarray, world: World) -> dict[str, object]:
    base_vals = world.base_grads @ move
    sem_vals = world.semantic_grads @ move
    changed = np.abs(move) > TOL
    return {
        "base_mean": float(base_vals.mean()),
        "base_max": float(base_vals.max()),
        "base_pos": int((base_vals < 0).sum()),
        "sem_mean": float(sem_vals.mean()),
        "sem_max": float(sem_vals.max()),
        "sem_pos": int((sem_vals < 0).sum()),
        "h088_cos": cosine(move, world.h088_move),
        "changed": int(changed.sum()),
        "rows": int(len(set(np.where(changed)[0] // len(TARGETS)))),
    }


def decision_score(rec: dict[str, object], bad_penalty: float = 0.0) -> float:
    return (
        -1000.0 * float(rec["base_mean"])
        - 800.0 * max(float(rec["base_max"]), 0.0)
        - 650.0 * max(float(rec["sem_max"]), 0.0)
        - 0.9 * max(float(rec["h088_cos"]), 0.0)
        - 0.7 * bad_penalty
        + 0.0005 * int(rec["changed"])
    )


def write_candidate(name_prefix: str, move: np.ndarray, world: World) -> dict[str, object]:
    prob = h154.clip_prob(h154.sigmoid(world.base_logit + move).reshape(world.base_prob.shape))
    hash_id = short_hash(prob)
    local_path = OUT / f"{name_prefix}_{hash_id}.csv"
    root_path = ROOT / f"{name_prefix}_{hash_id}_uploadsafe.csv"
    h154.write_submission(world.sample, prob, local_path)
    root_path.write_text(local_path.read_text(encoding="utf-8"), encoding="utf-8")
    return {
        "hash": hash_id,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "validation": h154.validate_submission(root_path, world.sample, world.base_prob),
    }


def load_world() -> World:
    sample, _narratives, base_prob, moves, base_models, semantic_models = h154.load_world()
    n_cells = base_prob.size
    return World(
        sample=sample,
        base_prob=base_prob,
        base_logit=h154.logit(base_prob.reshape(-1)),
        moves=moves,
        base_grads=np.vstack([h154.h150mod.gradient(model, n_cells) for model in base_models.values()]),
        semantic_grads=np.vstack([h154.h150mod.gradient(model, n_cells) for model in semantic_models.values()]),
        h088_move=moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"],
    )


def listener_support() -> dict[tuple[int, int], pd.Series]:
    cells = pd.read_csv(OUT / "h154_cell_candidates.csv")
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


def build_h061_delta(world: World) -> np.ndarray:
    posterior = pd.read_csv(H061_POSTERIOR)
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}
    flat_idx = posterior["row"].to_numpy(dtype=int) * len(TARGETS) + posterior["target"].map(target_to_idx).to_numpy(dtype=int)
    prob = np.full(world.base_prob.size, np.nan)
    prob[flat_idx] = posterior["q061"].to_numpy(dtype=np.float64)
    return h154.logit(prob) - world.base_logit


def make_h155(world: World, support: dict[tuple[int, int], pd.Series]) -> tuple[dict[str, object], np.ndarray]:
    raw_delta = build_h061_delta(world)
    capped = np.clip(raw_delta, -1.0, 1.0)
    pool: list[tuple[float, int, float, str, int, float, float, float]] = []
    for flat in np.flatnonzero(np.isfinite(capped) & (np.abs(capped) > 1e-7)):
        sign = int(np.sign(capped[flat]))
        rec = support.get((int(flat), sign))
        if rec is None:
            continue
        if rec["h088_alignment"] > 0.62 or rec["sem_mean"] < -2e-6 or rec["base_mean"] < -2e-5:
            continue
        target = TARGETS[flat % len(TARGETS)]
        score = (
            abs(capped[flat])
            * (1.0 + 0.35 * rec["source_support"])
            * (1.0 + 12000.0 * max(float(rec["sem_mean"]), 0.0))
            * (1.0 + 7000.0 * max(float(rec["base_mean"]), 0.0))
            * (1.0 + 0.05 * rec["sem_pos"] + 0.04 * rec["base_pos"])
            / (1.0 + 3.0 * rec["h088_alignment"])
        )
        pool.append((float(score), int(flat), float(capped[flat]), target, int(flat // len(TARGETS)), rec["source_support"], rec["sem_mean"], rec["base_mean"]))
    pool.sort(reverse=True, key=lambda row: row[0])

    selected: list[tuple[float, int, float, str, int, float, float, float]] = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for item in pool:
        _score, flat, _delta, target, row, *_rest = item
        if row_count.get(row, 0) >= 2:
            continue
        if target_count.get(target, 0) >= 50:
            continue
        selected.append(item)
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        if len(selected) >= 150:
            break

    move = np.zeros(world.base_prob.size, dtype=np.float64)
    for _score, flat, delta, *_rest in selected:
        move[flat] += 1.15 * delta
    move = np.clip(move, -1.6, 1.6)

    selected_frame = pd.DataFrame(
        selected,
        columns=["score", "flat_idx", "logit_delta", "target", "row", "source_support", "sem_mean", "base_mean"],
    )
    selected_frame.to_csv(OUT / "h155_selected_0f87a1af.csv", index=False)
    rec = {
        "name": "h155_h061_all_cap1.0_k150_a1.15",
        "source": "h061",
        "mode": "all",
        "cap": 1.0,
        "k": 150,
        "amp": 1.15,
        **metrics(move, world),
    }
    rec["decision"] = decision_score(rec)
    rec |= write_candidate("submission_h155_h061_all_cap1.0_k150_a1.15", move, world)
    return rec, move


def make_h156(world: World, h155_move: np.ndarray) -> tuple[dict[str, object], np.ndarray]:
    h154_move = movement_from_file(H154_ROOT, world)
    move = np.clip(1.3 * h154_move + 1.3 * h155_move, -1.8, 1.8)
    rec = {"name": "h156_combo_h154_h155", "a_h154": 1.3, "b_h155": 1.3, **metrics(move, world)}
    rec["cos154155"] = cosine(h154_move, h155_move)
    rec["decision"] = decision_score(rec)
    rec |= write_candidate("submission_h156_combo_h154_h155_a1.3_b1.3", move, world)
    return rec, move


def make_h158(world: World, h155_move: np.ndarray) -> tuple[dict[str, object], np.ndarray]:
    h154_move = movement_from_file(H154_ROOT, world)
    raw = 1.8 * h154_move + 1.8 * h155_move
    support = np.abs(raw) > TOL

    bad_moves = [movement_from_file(name, world) for name in KNOWN_LOSS_FILES if (h154.locate(name) or (ROOT / name).exists())]
    bad_names = [name for name in KNOWN_LOSS_FILES if (h154.locate(name) or (ROOT / name).exists())]
    bad_matrix = np.vstack([move * support for move in bad_moves]).T
    bad_matrix = bad_matrix / (np.linalg.norm(bad_matrix, axis=0, keepdims=True) + 1e-12)
    positive_coeff = np.maximum(bad_matrix.T @ raw, 0.0)
    move = (raw - 1.0 * (bad_matrix @ positive_coeff)) * support
    move = np.clip(move, -2.2, 2.2)

    rec = {
        "name": "h158_sparse_lossnull",
        "a154": 1.8,
        "b155": 1.8,
        "bad_remove": 1.0,
        "keep": 160,
        "cap": 2.2,
        **metrics(move, world),
    }
    for name, bad_move in zip(bad_names, bad_moves):
        rec[f"cos_{name}"] = cosine(move, bad_move)
    rec["decision"] = decision_score(
        rec,
        bad_penalty=sum(max(float(rec[f"cos_{name}"]), 0.0) for name in bad_names),
    )
    rec |= write_candidate("submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160", move, world)
    return rec, move


def run() -> None:
    world = load_world()
    support = listener_support()
    h155_rec, h155_move = make_h155(world, support)
    h156_rec, _h156_move = make_h156(world, h155_move)
    h158_rec, _h158_move = make_h158(world, h155_move)
    readout = {
        "base_file": h154.BASE_FILE,
        "h155": h155_rec,
        "h156": h156_rec,
        "h158": h158_rec,
        "submit_priority": [
            "h158_sparse_lossnull: highest jackpot / highest action strength",
            "h156_combo: less transformed, still big-bet",
            "h155_h061: diagnostic posterior-listener bridge",
        ],
        "rejected": {
            "h157_dense_lossnull": "projection spread to 1024 cells; kept as failed exploration, not promoted",
        },
    }
    (OUT / "h155_h158_repro_readout.json").write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
