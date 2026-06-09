#!/usr/bin/env python3
"""Target-Route Toxicity Head for HS-JEPA.

This is the safer follow-up to public_private_toxicity_head.py.

The previous toxicity head added 56 extra cells across all targets. That is a
large move. This script creates two target-route variants:

    1. teacher-only calibrated
       Keep Candidate 1's 94 support cells, but target-route toxicity calibrates
       their amplitude. No new support is introduced.

    2. Q2-extra calibrated
       Keep the calibrated teacher cells and add only Q2 Listener
       Responsibility cells that pass toxicity filters.

The paper idea:
    support assignment and competition decoder are separate. The decoder should
    be target-route aware, because Q2 support behaved differently from S-tail
    support in prior experiments.
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
OUT = HERE / "outputs" / "target_route_toxicity_head"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TEACHER_FILE = "submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv"

CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"
TOXICITY_MODULE = HERE / "public_private_toxicity_head.py"


@dataclass(frozen=True)
class TargetRouteConfig:
    min_teacher_amp: float = 0.78
    max_teacher_amp: float = 1.24
    s_tail_max_amp: float = 1.07
    q2_min_amp: float = 0.96
    q2_max_amp: float = 1.28
    q2_extra_top_cells: int = 18
    q2_extra_min_selection: float = 0.68
    q2_extra_max_toxicity: float = 0.56
    q2_extra_min_h088_safe: float = 0.24
    q2_extra_max_logit_step: float = 0.72


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "target_route_candidate1")
toxicity = import_module(TOXICITY_MODULE, "target_route_toxicity_base")


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


def load_submission(path_or_name: str | Path) -> pd.DataFrame:
    path = Path(path_or_name)
    if not path.is_absolute():
        path = ROOT / path
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def ensure_toxicity_table() -> pd.DataFrame:
    table_path = HERE / "outputs" / "public_private_toxicity_head" / "toxicity_candidate_cell_table.csv"
    if not table_path.exists():
        toxicity.run()
    table = pd.read_csv(table_path)
    for col in ["teacher_has_action", "lrj_has_cell", "lrj_teacher_sign_match"]:
        if col in table:
            table[col] = as_bool(table[col])
    return table


def teacher_route_amp(row: pd.Series, config: TargetRouteConfig) -> float:
    target = str(row["target"])
    amp = (
        0.90
        + 0.14 * float(row.get("lrj_teacher_sign_match", False))
        + 0.11 * float(row.get("toxic_safety_rank", 0.5))
        + 0.07 * float(row.get("h088_safe_rank", 0.5))
        - 0.10 * float(row.get("toxic_same_rank", 0.5))
    )
    if target == "Q2":
        amp += 0.08 + 0.05 * float(row.get("listener_benefit_rank", 0.0))
        return float(np.clip(amp, config.q2_min_amp, config.q2_max_amp))
    if target in {"S1", "S3", "S4"}:
        amp -= 0.08 + 0.06 * float(row.get("toxic_same_rank", 0.0))
        return float(np.clip(amp, config.min_teacher_amp, config.s_tail_max_amp))
    if target == "S2":
        amp += 0.02 * float(row.get("toxic_safety_rank", 0.5))
    return float(np.clip(amp, config.min_teacher_amp, config.max_teacher_amp))


def decode_variant(
    table: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    variant: str,
    config: TargetRouteConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    move = np.zeros(base_prob.size, dtype=np.float64)
    audit_rows = []
    teacher = table[table["teacher_has_action"]].copy()
    teacher["amp"] = teacher.apply(lambda row: teacher_route_amp(row, config), axis=1)
    for rec in teacher.to_dict("records"):
        flat = int(rec["flat_idx"])
        decoded = float(rec["teacher_logit_move"]) * float(rec["amp"])
        move[flat] = decoded
        audit_rows.append({**rec, "decoded_logit_move": decoded, "action_source": "teacher_target_route_calibrated"})

    if variant == "q2_extra":
        extra_pool = table[
            (~table["teacher_has_action"])
            & table["lrj_has_cell"]
            & table["target"].eq("Q2")
            & (table["selection_score"] >= config.q2_extra_min_selection)
            & (table["toxic_same_rank"] <= config.q2_extra_max_toxicity)
            & (table["h088_safe_rank"] >= config.q2_extra_min_h088_safe)
        ].copy()
        extra_pool["q2_extra_score"] = (
            0.34 * extra_pool["selection_score"]
            + 0.24 * extra_pool["listener_benefit_rank"]
            + 0.18 * extra_pool["toxic_safety_rank"]
            + 0.14 * extra_pool["h088_safe_rank"]
            + 0.10 * extra_pool["human_state_responsibility"]
        )
        extra_pool = extra_pool.sort_values("q2_extra_score", ascending=False).head(config.q2_extra_top_cells)
        for rec in extra_pool.to_dict("records"):
            flat = int(rec["flat_idx"])
            magnitude = min(
                config.q2_extra_max_logit_step,
                0.12
                + 0.42 * float(rec["responsibility_score"])
                + 0.16 * float(rec["listener_benefit_rank"])
                + 0.12 * float(rec["toxic_safety_rank"]),
            )
            decoded = int(rec["candidate_sign"]) * magnitude
            move[flat] = decoded
            audit_rows.append({**rec, "decoded_logit_move": decoded, "action_source": "q2_lrj_extra_target_route_safe"})

    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    audit = pd.DataFrame(audit_rows)
    diagnostics = {
        "variant": variant,
        "teacher_cells": int((audit["action_source"] == "teacher_target_route_calibrated").sum()) if len(audit) else 0,
        "q2_extra_cells": int((audit["action_source"] == "q2_lrj_extra_target_route_safe").sum()) if len(audit) else 0,
        "changed_cells": int(np.sum(np.abs(move) > 1e-12)),
        "changed_rows": int(len(set(np.where(np.abs(move) > 1e-12)[0] // len(TARGETS)))),
        "teacher_mean_amp": float(teacher["amp"].mean()) if len(teacher) else 0.0,
        "teacher_min_amp": float(teacher["amp"].min()) if len(teacher) else 0.0,
        "teacher_max_amp": float(teacher["amp"].max()) if len(teacher) else 0.0,
        "target_action_counts": audit.groupby(["target", "action_source"]).size().unstack(fill_value=0).to_dict() if len(audit) else {},
    }
    return prob, audit, diagnostics


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    table = ensure_toxicity_table()
    config = TargetRouteConfig()

    outputs = {}
    for variant in ["teacher_only", "q2_extra"]:
        prob, audit, diag = decode_variant(table, sample, base_prob, base_logit, variant, config)
        digest = short_hash(prob)
        name = f"submission_hsjepa_target_route_toxicity_{variant}_{digest}_uploadsafe.csv"
        local_path = OUT / name
        root_path = ROOT / name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        move = logit(prob).reshape(-1) - base_logit
        metrics = candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move)
        audit.to_csv(OUT / f"target_route_toxicity_{variant}_audit.csv", index=False)
        outputs[variant] = {
            "submission_file": name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "decode_diagnostics": diag,
            "listener_metrics": metrics,
            "validation": validate_submission(root_path, sample, base_prob),
        }

    readout = {
        "experiment": "Target-Route Toxicity Head HS-JEPA",
        "support_generator": "Listener Responsibility JEPA",
        "competition_decoder": "target-route toxicity calibrated decoder",
        "teacher_file": TEACHER_FILE,
        "config": config.__dict__,
        "variants": outputs,
    }
    (OUT / "target_route_toxicity_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
