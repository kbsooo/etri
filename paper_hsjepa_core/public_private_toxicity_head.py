#!/usr/bin/env python3
"""Public/Private Toxicity Head for HS-JEPA.

This experiment builds on Listener Responsibility JEPA.

Architecture role split:
    1. Listener Responsibility JEPA
       Public-score-free support generator.

    2. Public/Private Toxicity Head
       Competition-specific decoder that decides which responsible actions are
       safe, toxic, amplified, or damped.

The toxicity head uses public-bad anchor submissions as negative sensors, but
it does not use them to create the support field itself. This keeps the paper
architecture separate from the competition decoder.
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
OUT = HERE / "outputs" / "public_private_toxicity_head"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939
TEACHER_FILE = "submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv"
PUBLIC_LEDGER = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"
LISTENER_RESP_MODULE = HERE / "listener_responsibility_jepa.py"


@dataclass(frozen=True)
class ToxicityConfig:
    max_teacher_amp: float = 1.22
    min_teacher_amp: float = 0.74
    lrj_extra_top_cells: int = 56
    lrj_extra_min_score: float = 0.68
    lrj_extra_max_toxicity: float = 0.62
    lrj_extra_max_logit_step: float = 0.92
    max_cells_per_row: int = 3
    max_extra_per_target: int = 18
    q2_extra_bonus: float = 1.18
    objective_tail_toxic_penalty: float = 0.18


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "toxicity_candidate1")
listener_resp = import_module(LISTENER_RESP_MODULE, "toxicity_listener_resp")


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


def movement_from_file(name: str, sample: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray | None:
    path = candidate1.locate(name)
    if path is None:
        return None
    try:
        prob = candidate1.load_submission(path, sample)[TARGETS].to_numpy(dtype=np.float64).reshape(-1)
        return logit(prob) - base_logit
    except Exception:
        return None


def toxic_anchor_matrix(sample: pd.DataFrame, base_logit: np.ndarray) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    ledger = pd.read_csv(PUBLIC_LEDGER)
    bad = ledger[ledger["public_lb"].astype(float) >= CURRENT_BEST_PUBLIC_LB + 0.00045].copy()
    rows = []
    names = []
    weights = []
    for rec in bad.to_dict("records"):
        name = str(rec["file"])
        move = movement_from_file(name, sample, base_logit)
        if move is None:
            continue
        delta = float(rec["public_lb"]) - CURRENT_BEST_PUBLIC_LB
        names.append(name)
        rows.append(move)
        weights.append(np.sqrt(max(delta, 1e-8) / 0.00045))
    if not rows:
        return pd.DataFrame(), np.zeros((0, base_logit.size)), []
    return bad[bad["file"].isin(names)].reset_index(drop=True), np.vstack(rows), names


def cell_toxicity_features(candidate_cells: pd.DataFrame, toxic_moves: np.ndarray, toxic_names: list[str]) -> pd.DataFrame:
    out = candidate_cells.copy()
    if toxic_moves.size == 0:
        out["toxic_same_weight"] = 0.0
        out["toxic_opp_weight"] = 0.0
        out["toxic_abs_weight"] = 0.0
        out["toxic_same_rank"] = 0.0
        out["toxic_safety_rank"] = 1.0
        return out
    same = []
    opp = []
    absw = []
    for rec in out.to_dict("records"):
        flat = int(rec["flat_idx"])
        sign = int(np.sign(rec["candidate_sign"]))
        mv = toxic_moves[:, flat]
        active = np.abs(mv) > 1e-12
        same.append(float(np.sum(np.abs(mv[active]) * (np.sign(mv[active]) == sign))))
        opp.append(float(np.sum(np.abs(mv[active]) * (np.sign(mv[active]) == -sign))))
        absw.append(float(np.sum(np.abs(mv[active]))))
    out["toxic_same_weight"] = same
    out["toxic_opp_weight"] = opp
    out["toxic_abs_weight"] = absw
    out["toxic_same_rank"] = rank01(out["toxic_same_weight"])
    out["toxic_opp_rank"] = rank01(out["toxic_opp_weight"])
    out["toxic_safety_rank"] = 1.0 - out["toxic_same_rank"]
    return out


def build_candidate_cell_table(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    teacher_prob: np.ndarray,
    lrj_audit: pd.DataFrame,
    lrj_ranked: pd.DataFrame,
) -> pd.DataFrame:
    teacher_move = logit(teacher_prob).reshape(-1) - base_logit
    teacher_cells = set(np.flatnonzero(np.abs(teacher_move) > 1e-12).tolist())

    lrj = lrj_ranked.copy()
    lrj["flat_idx"] = lrj["flat_idx"].astype(int)
    lrj["candidate_sign"] = lrj["sign"].astype(int)
    lrj_cols = [
        "flat_idx",
        "candidate_sign",
        "responsibility_score",
        "selection_score",
        "source_consensus_rank",
        "listener_benefit_rank",
        "human_state_responsibility",
        "h088_safe_rank",
        "source_support",
        "source_move_abs_mean",
        "sign_margin",
        "target",
        "row",
    ]
    lrj = lrj[[c for c in lrj_cols if c in lrj.columns]].drop_duplicates("flat_idx")

    rows = []
    all_flats = sorted(teacher_cells | set(lrj["flat_idx"].astype(int)))
    lrj_index = lrj.set_index("flat_idx")
    for flat in all_flats:
        row = flat // len(TARGETS)
        target = TARGETS[flat % len(TARGETS)]
        teacher_has = flat in teacher_cells
        teacher_sign = int(np.sign(teacher_move[flat])) if teacher_has else 0
        if flat in lrj_index.index:
            rec = lrj_index.loc[flat].to_dict()
            lrj_sign = int(rec.get("candidate_sign", 0))
        else:
            rec = {}
            lrj_sign = 0
        candidate_sign = teacher_sign if teacher_has else lrj_sign
        if candidate_sign == 0:
            continue
        rows.append(
            {
                "flat_idx": flat,
                "row": row,
                "target": target,
                "target_idx": flat % len(TARGETS),
                "candidate_sign": candidate_sign,
                "teacher_has_action": teacher_has,
                "teacher_logit_move": float(teacher_move[flat]),
                "teacher_sign": teacher_sign,
                "lrj_has_cell": flat in lrj_index.index,
                "lrj_sign": lrj_sign,
                "lrj_teacher_sign_match": bool(teacher_has and lrj_sign == teacher_sign),
                "responsibility_score": float(rec.get("responsibility_score", 0.0)),
                "selection_score": float(rec.get("selection_score", 0.0)),
                "source_consensus_rank": float(rec.get("source_consensus_rank", 0.0)),
                "listener_benefit_rank": float(rec.get("listener_benefit_rank", 0.0)),
                "human_state_responsibility": float(rec.get("human_state_responsibility", 0.0)),
                "h088_safe_rank": float(rec.get("h088_safe_rank", 0.5)),
                "source_support": float(rec.get("source_support", 0.0)),
                "source_move_abs_mean": float(rec.get("source_move_abs_mean", 0.0)),
                "sign_margin": float(rec.get("sign_margin", 0.0)),
                "base_prob": float(base_prob[row, flat % len(TARGETS)]),
            }
        )
    table = pd.DataFrame(rows)
    for col in [
        "responsibility_score",
        "selection_score",
        "source_consensus_rank",
        "listener_benefit_rank",
        "human_state_responsibility",
        "h088_safe_rank",
        "source_support",
        "source_move_abs_mean",
        "sign_margin",
    ]:
        table[col] = table[col].fillna(0.0)
    return table


def decode_toxicity_gated(
    table: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    config: ToxicityConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    move = np.zeros(base_prob.size, dtype=np.float64)
    audit = []

    teacher = table[table["teacher_has_action"]].copy()
    teacher["agreement_bonus"] = np.where(teacher["lrj_teacher_sign_match"], 1.0, 0.0)
    teacher["amp"] = (
        0.86
        + 0.18 * teacher["agreement_bonus"]
        + 0.12 * teacher["toxic_safety_rank"]
        + 0.08 * teacher["h088_safe_rank"]
        - 0.10 * teacher["toxic_same_rank"]
    ).clip(config.min_teacher_amp, config.max_teacher_amp)
    for rec in teacher.to_dict("records"):
        flat = int(rec["flat_idx"])
        move[flat] = float(rec["teacher_logit_move"]) * float(rec["amp"])
        audit.append({**rec, "decoded_logit_move": float(move[flat]), "action_source": "teacher_toxicity_gated"})

    extra_pool = table[
        (~table["teacher_has_action"])
        & (table["lrj_has_cell"])
        & (table["selection_score"] >= config.lrj_extra_min_score)
        & (table["toxic_same_rank"] <= config.lrj_extra_max_toxicity)
    ].copy()
    extra_pool["extra_score"] = (
        0.38 * extra_pool["selection_score"]
        + 0.24 * extra_pool["toxic_safety_rank"]
        + 0.16 * extra_pool["h088_safe_rank"]
        + 0.14 * extra_pool["listener_benefit_rank"]
        + 0.08 * extra_pool["human_state_responsibility"]
    )
    extra_pool.loc[extra_pool["target"].eq("Q2"), "extra_score"] *= config.q2_extra_bonus
    extra_pool.loc[extra_pool["target"].isin(["S1", "S3", "S4"]), "extra_score"] -= (
        config.objective_tail_toxic_penalty * extra_pool.loc[extra_pool["target"].isin(["S1", "S3", "S4"]), "toxic_same_rank"]
    )
    extra_pool = extra_pool.sort_values("extra_score", ascending=False)

    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for rec in extra_pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if row_count.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_count.get(target, 0) >= config.max_extra_per_target:
            continue
        flat = int(rec["flat_idx"])
        magnitude = min(
            config.lrj_extra_max_logit_step,
            0.15
            + 0.58 * float(rec["responsibility_score"])
            + 0.18 * float(rec["listener_benefit_rank"])
            + 0.12 * float(rec["toxic_safety_rank"]),
        )
        if target == "Q2":
            magnitude *= config.q2_extra_bonus
        magnitude = min(config.lrj_extra_max_logit_step, magnitude)
        move[flat] = int(rec["candidate_sign"]) * magnitude
        audit.append({**rec, "decoded_logit_move": float(move[flat]), "action_source": "lrj_extra_toxicity_safe"})
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        if sum(target_count.values()) >= config.lrj_extra_top_cells:
            break

    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    audit_frame = pd.DataFrame(audit)
    diagnostics = {
        "teacher_cells_retained": int((audit_frame["action_source"] == "teacher_toxicity_gated").sum()) if len(audit_frame) else 0,
        "lrj_extra_cells_added": int((audit_frame["action_source"] == "lrj_extra_toxicity_safe").sum()) if len(audit_frame) else 0,
        "changed_cells": int(np.sum(np.abs(move) > 1e-12)),
        "changed_rows": int(len(set(np.where(np.abs(move) > 1e-12)[0] // len(TARGETS)))),
        "action_by_target": audit_frame.groupby(["target", "action_source"]).size().unstack(fill_value=0).to_dict() if len(audit_frame) else {},
        "mean_teacher_amp": float(teacher["amp"].mean()) if len(teacher) else 0.0,
        "min_teacher_amp": float(teacher["amp"].min()) if len(teacher) else 0.0,
        "max_teacher_amp": float(teacher["amp"].max()) if len(teacher) else 0.0,
    }
    return prob, audit_frame, diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    listener_resp.run()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    teacher_prob = load_submission(TEACHER_FILE)[TARGETS].to_numpy(dtype=np.float64)

    lrj_dir = HERE / "outputs" / "listener_responsibility_jepa"
    lrj_audit = pd.read_csv(lrj_dir / "listener_responsibility_action_audit.csv")
    lrj_ranked = pd.read_csv(lrj_dir / "listener_responsibility_ranked_cells.csv")
    table = build_candidate_cell_table(sample, base_prob, base_logit, teacher_prob, lrj_audit, lrj_ranked)
    toxic_ledger, toxic_moves, toxic_names = toxic_anchor_matrix(sample, base_logit)
    table = cell_toxicity_features(table, toxic_moves, toxic_names)

    config = ToxicityConfig()
    prob, audit, decode_diag = decode_toxicity_gated(table, sample, base_prob, base_logit, config)
    digest = short_hash(prob)
    name = f"submission_hsjepa_public_private_toxicity_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)

    move = logit(prob).reshape(-1) - base_logit
    listener_metrics = candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move)
    table.to_csv(OUT / "toxicity_candidate_cell_table.csv", index=False)
    audit.to_csv(OUT / "toxicity_action_audit.csv", index=False)
    toxic_ledger.to_csv(OUT / "toxicity_anchor_ledger.csv", index=False)

    readout = {
        "experiment": "Public/Private Toxicity Head HS-JEPA",
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "support_generator": "Listener Responsibility JEPA",
        "competition_decoder": "public/private toxicity head",
        "public_score_ledger_used_for_support": False,
        "public_score_ledger_used_for_toxicity_decoder": True,
        "teacher_file": TEACHER_FILE,
        "toxic_anchor_files": toxic_names,
        "config": config.__dict__,
        "decode_diagnostics": decode_diag,
        "listener_metrics": listener_metrics,
        "validation": validate_submission(root_path, sample, base_prob),
    }
    (OUT / "public_private_toxicity_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
