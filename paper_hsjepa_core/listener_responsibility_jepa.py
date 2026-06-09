#!/usr/bin/env python3
"""Listener Responsibility JEPA.

This experiment attacks the support-assignment bottleneck found by
human_state_action_distillation.py.

The previous result showed:
    OG human-state alone cannot locate the row-target cells that should move.

This script tests a stronger paper-oriented solver:
    source/listener responsibility context + OG human-state context
        -> sparse row-target support and sign

Important:
    The solver does not read the public score ledger. Candidate 1 is used only
    as a teacher/evaluation target after the public-free responsibility field is
    built.
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
OUT = HERE / "outputs" / "listener_responsibility_jepa"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
TEACHER_FILE = "submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv"
CELL_CANDIDATES = ROOT / "hsjepa_jackpot" / "outputs" / "h154_cell_candidates.csv"

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"
ACTION_DISTILL_MODULE = HERE / "human_state_action_distillation.py"


@dataclass(frozen=True)
class ResponsibilityConfig:
    top_cells: int = 118
    max_cells_per_row: int = 2
    max_cells_per_target: int = 48
    max_logit_step: float = 1.75
    min_responsibility_score: float = 0.10
    source_weight: float = 0.48
    listener_weight: float = 0.32
    human_state_weight: float = 0.20


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "listener_resp_candidate1")
distill = import_module(ACTION_DISTILL_MODULE, "listener_resp_distill")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


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


def aggregate_listener_candidates() -> pd.DataFrame:
    cells = pd.read_csv(CELL_CANDIDATES, parse_dates=["sleep_date", "lifelog_date"])
    agg = (
        cells.groupby(["flat_idx", "row", "target", "target_idx", "sign"], as_index=False)
        .agg(
            source_support=("source_file", "nunique"),
            source_move_abs_mean=("source_move", lambda x: float(np.mean(np.abs(x)))),
            source_move_abs_max=("source_move", lambda x: float(np.max(np.abs(x)))),
            source_move_std=("source_move", "std"),
            sem_mean=("sem_mean_benefit", "mean"),
            base_mean=("base_mean_benefit", "mean"),
            sem_min=("sem_min_benefit", "mean"),
            base_min=("base_min_benefit", "mean"),
            sem_pos=("sem_pos", "max"),
            base_pos=("base_pos", "max"),
            h088_alignment=("h088_alignment", "max"),
            source_score=("score", "mean"),
            source_score_max=("score", "max"),
        )
    )
    agg["source_move_std"] = agg["source_move_std"].fillna(0.0)
    for col in [
        "source_support",
        "source_move_abs_mean",
        "source_move_abs_max",
        "source_move_std",
        "sem_mean",
        "base_mean",
        "sem_min",
        "base_min",
        "sem_pos",
        "base_pos",
        "source_score",
        "source_score_max",
    ]:
        agg[f"{col}_rank"] = rank01(agg[col])
    agg["h088_safe_rank"] = 1.0 - rank01(agg["h088_alignment"])
    agg["listener_benefit_rank"] = (
        0.30 * agg["sem_mean_rank"]
        + 0.23 * agg["base_mean_rank"]
        + 0.17 * agg["sem_min_rank"]
        + 0.15 * agg["base_min_rank"]
        + 0.08 * rank01(agg["sem_pos"])
        + 0.07 * rank01(agg["base_pos"])
    )
    agg["source_consensus_rank"] = (
        0.42 * agg["source_score_rank"]
        + 0.25 * agg["source_support_rank"]
        + 0.18 * agg["source_move_abs_mean_rank"]
        + 0.15 * agg["source_move_abs_max_rank"]
    )
    return agg


def build_responsibility_frame(sample: pd.DataFrame, base_prob: np.ndarray, teacher_prob: np.ndarray) -> pd.DataFrame:
    cell_frame, _feature_cols = distill.build_cell_frame(sample, base_prob, teacher_prob)
    keep_cols = [
        "row",
        "target",
        "target_idx_int",
        "base_prob",
        "base_uncertainty",
        "target_peer_margin",
        "target_peer_margin_abs",
        "atlas_action_health",
        "cohort_outlier_score",
        "personal_axis",
        "cohort_axis",
        "axis_disagreement",
        "peer_only_toxicity",
        "q_group_peer_margin",
        "s_group_peer_margin",
        "target_route_margin_q2q3s2",
        "teacher_logit_move",
        "teacher_has_action",
        "teacher_action_sign",
    ]
    base_cells = cell_frame[keep_cols].copy()
    base_cells["row"] = base_cells["row"].astype(int)
    base_cells["target_idx_int"] = base_cells["target_idx_int"].astype(int)
    base_cells["flat_idx"] = base_cells["row"] * len(TARGETS) + base_cells["target_idx_int"]

    listener = aggregate_listener_candidates()
    merged = base_cells.merge(listener, on=["flat_idx", "row", "target"], how="left")
    numeric_listener_cols = [c for c in listener.columns if c not in {"target"}]
    for col in numeric_listener_cols:
        if col in merged:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
    merged["sign"] = merged["sign"].fillna(0).astype(int)
    fill_zero = [c for c in merged.columns if c.endswith("_rank") or c in {
        "source_support",
        "source_move_abs_mean",
        "source_move_abs_max",
        "source_move_std",
        "sem_mean",
        "base_mean",
        "sem_min",
        "base_min",
        "sem_pos",
        "base_pos",
        "h088_alignment",
        "source_score",
        "source_score_max",
        "listener_benefit_rank",
        "source_consensus_rank",
    }]
    for col in fill_zero:
        merged[col] = merged[col].fillna(0.0)
    return merged


def score_responsibility(frame: pd.DataFrame, config: ResponsibilityConfig) -> pd.DataFrame:
    out = frame.copy()
    human_state_score = (
        0.26 * rank01(out["atlas_action_health"])
        + 0.20 * rank01(out["cohort_outlier_score"])
        + 0.18 * rank01(out["base_uncertainty"])
        + 0.14 * rank01(out["target_peer_margin_abs"])
        + 0.12 * (1.0 - rank01(out["peer_only_toxicity"]))
        + 0.10 * rank01(out["target_route_margin_q2q3s2"])
    )
    out["human_state_responsibility"] = human_state_score
    out["responsibility_score"] = (
        config.source_weight * out["source_consensus_rank"]
        + config.listener_weight * out["listener_benefit_rank"]
        + config.human_state_weight * out["human_state_responsibility"]
    ) * (0.68 + 0.32 * out["h088_safe_rank"])
    out["signed_responsibility"] = out["sign"] * out["responsibility_score"]
    return out


def collapse_signs(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for flat, group in scored.groupby("flat_idx", sort=False):
        valid = group[group["sign"].isin([-1, 1])].copy()
        if valid.empty:
            continue
        best = valid.sort_values("responsibility_score", ascending=False).iloc[0].copy()
        opp = valid[valid["sign"].eq(-int(best["sign"]))]
        opp_score = float(opp["responsibility_score"].max()) if len(opp) else 0.0
        best["opposite_sign_score"] = opp_score
        best["sign_margin"] = float(best["responsibility_score"] - opp_score)
        best["sign_margin_rank"] = 0.0
        rows.append(best)
    collapsed = pd.DataFrame(rows)
    if collapsed.empty:
        return collapsed
    collapsed["sign_margin_rank"] = rank01(collapsed["sign_margin"])
    collapsed["selection_score"] = (
        0.72 * rank01(collapsed["responsibility_score"])
        + 0.18 * collapsed["sign_margin_rank"]
        + 0.10 * rank01(collapsed["source_move_abs_mean"])
    )
    return collapsed.sort_values("selection_score", ascending=False).reset_index(drop=True)


def decode_public_free_action(
    collapsed: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    teacher_prob: np.ndarray,
    base_logit: np.ndarray,
    config: ResponsibilityConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    teacher_move = logit(teacher_prob).reshape(-1) - base_logit
    teacher_support = set(np.flatnonzero(np.abs(teacher_move) > 1e-12).tolist())
    selected = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for rec in collapsed.to_dict("records"):
        if rec["selection_score"] < config.min_responsibility_score:
            continue
        row = int(rec["row"])
        target = str(rec["target"])
        if row_count.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_count.get(target, 0) >= config.max_cells_per_target:
            continue
        selected.append(rec)
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        if len(selected) >= config.top_cells:
            break

    move = np.zeros(base_prob.size, dtype=np.float64)
    audit_rows = []
    for rec in selected:
        flat = int(rec["flat_idx"])
        sign = int(rec["sign"])
        magnitude = (
            0.18
            + 1.35 * float(rec["responsibility_score"])
            + 0.38 * float(rec["source_move_abs_mean_rank"])
            + 0.22 * float(rec["sign_margin_rank"])
        )
        magnitude = min(config.max_logit_step, magnitude)
        move[flat] = sign * magnitude
        audit_rows.append(
            {
                "flat_idx": flat,
                "row": int(rec["row"]),
                "target": rec["target"],
                "sign": sign,
                "decoded_logit_move": float(move[flat]),
                "responsibility_score": float(rec["responsibility_score"]),
                "selection_score": float(rec["selection_score"]),
                "source_consensus_rank": float(rec["source_consensus_rank"]),
                "listener_benefit_rank": float(rec["listener_benefit_rank"]),
                "human_state_responsibility": float(rec["human_state_responsibility"]),
                "h088_safe_rank": float(rec["h088_safe_rank"]),
                "source_support": float(rec["source_support"]),
                "source_move_abs_mean": float(rec["source_move_abs_mean"]),
                "sign_margin": float(rec["sign_margin"]),
                "teacher_has_action": bool(flat in teacher_support),
                "teacher_sign_match": bool(flat in teacher_support and np.sign(teacher_move[flat]) == sign),
                "teacher_logit_move": float(teacher_move[flat]),
            }
        )
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    audit = pd.DataFrame(audit_rows)
    selected_support = set(audit["flat_idx"].astype(int).tolist()) if len(audit) else set()
    overlap = len(selected_support & teacher_support)
    sign_match = int(audit["teacher_sign_match"].sum()) if len(audit) else 0
    diagnostics = {
        "selected_cells": int(len(selected_support)),
        "teacher_cells": int(len(teacher_support)),
        "teacher_overlap": int(overlap),
        "precision_vs_teacher": float(overlap / max(len(selected_support), 1)),
        "recall_vs_teacher": float(overlap / max(len(teacher_support), 1)),
        "sign_match_on_overlap": float(sign_match / max(overlap, 1)),
        "teacher_overlap_by_target": audit[audit["teacher_has_action"]].groupby("target").size().to_dict() if len(audit) else {},
        "selected_by_target": audit.groupby("target").size().to_dict() if len(audit) else {},
    }
    return prob, audit, diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    teacher_prob = load_submission(TEACHER_FILE)[TARGETS].to_numpy(dtype=np.float64)
    base_prob = clip_prob(base_prob)

    config = ResponsibilityConfig()
    frame = build_responsibility_frame(sample, base_prob, teacher_prob)
    scored = score_responsibility(frame, config)
    collapsed = collapse_signs(scored)
    prob, audit, support_diag = decode_public_free_action(collapsed, sample, base_prob, teacher_prob, base_logit, config)

    digest = short_hash(prob)
    name = f"submission_hsjepa_listener_responsibility_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)

    move = logit(prob).reshape(-1) - base_logit
    listener_metrics = candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move)
    collapsed.to_csv(OUT / "listener_responsibility_ranked_cells.csv", index=False)
    scored.to_csv(OUT / "listener_responsibility_sign_frame.csv", index=False)
    audit.to_csv(OUT / "listener_responsibility_action_audit.csv", index=False)

    readout = {
        "experiment": "Listener Responsibility JEPA",
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "public_score_ledger_used": False,
        "teacher_file_for_diagnostics_only": TEACHER_FILE,
        "config": config.__dict__,
        "support_diagnostics_vs_teacher": support_diag,
        "listener_metrics": listener_metrics,
        "validation": validate_submission(root_path, sample, base_prob),
    }
    (OUT / "listener_responsibility_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
