#!/usr/bin/env python3
"""H096: H057-positive / H088-toxic conflict inversion.

H095 found a sharper sensor than expected:

- many H057-positive cells overlap H088-toxic cells;
- most of those overlapping cells have opposite directions.

H096 tests the worldview that H088 failed because it reversed the H057-positive
field, not because those rows/targets are intrinsically unsafe.  The action is
therefore not to avoid the conflict cells, but to push selected conflict cells
further along the H057-positive direction and away from H088.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h096_positive_toxic_conflict_inversion_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H095_PATH = HITL / "h095_public_private_assignment_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h095mod", H095_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H095_PATH}")
h095mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h095mod
SPEC.loader.exec_module(h095mod)

h085mod = h095mod.h085mod
h087mod = h095mod.h087mod

TARGETS = h095mod.TARGETS
KEYS = h095mod.KEYS
BASE_FILE = h095mod.BASE_FILE
TOL = h095mod.TOL


@dataclass(frozen=True)
class H096Spec:
    name: str
    target_group: str
    k: int
    alpha: float
    cap: float
    min_conflict_score: float
    max_bad_same: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return h085mod.bce(np.asarray(prob, dtype=np.float64), np.asarray(q, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h096_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h096_conflict_inversion_*_uploadsafe.csv"):
        path.unlink()


def ensure_h095_cell_table(sample: pd.DataFrame, base_prob: np.ndarray) -> pd.DataFrame:
    path = HITL / "h095_public_private_assignment_solver_hsjepa" / "h095_cell_toxicity_table.csv"
    if path.exists():
        return pd.read_csv(path)
    _known, _configs, cell, _q_prob = h095mod.build_h095_cell_table(sample, base_prob)
    return cell


def target_mask(frame: pd.DataFrame, group: str) -> pd.Series:
    target = frame["target"].astype(str)
    if group == "all":
        return pd.Series(True, index=frame.index)
    if group == "nonq2":
        return target.ne("Q2")
    if group == "stage":
        return target.isin(["S1", "S2", "S3", "S4"])
    if group == "subjective":
        return target.isin(["Q1", "Q3"])
    if group == "objective_plus_q3":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"])
    raise ValueError(group)


def candidate_specs() -> list[H096Spec]:
    return [
        H096Spec(
            name="all_conflict_k105_a055",
            target_group="all",
            k=105,
            alpha=0.55,
            cap=0.70,
            min_conflict_score=0.08,
            max_bad_same=0.96,
            worldview="H088 failed by reversing H057-positive conflict cells; amplify all anti-H088 conflict cells",
        ),
        H096Spec(
            name="stage_conflict_k80_a060",
            target_group="stage",
            k=80,
            alpha=0.60,
            cap=0.72,
            min_conflict_score=0.08,
            max_bad_same=0.96,
            worldview="the conflict is mainly objective sleep-stage physiology; amplify stage conflict only",
        ),
        H096Spec(
            name="objective_q3_conflict_k95_a052",
            target_group="objective_plus_q3",
            k=95,
            alpha=0.52,
            cap=0.68,
            min_conflict_score=0.08,
            max_bad_same=0.96,
            worldview="Q3 and S-stage share a hidden objective route that H088 inverted",
        ),
        H096Spec(
            name="subjective_conflict_k45_a065",
            target_group="subjective",
            k=45,
            alpha=0.65,
            cap=0.78,
            min_conflict_score=0.08,
            max_bad_same=0.98,
            worldview="H088 reversed subjective satisfaction/quality state, not objective state",
        ),
        H096Spec(
            name="top_edge_conflict_k42_a085",
            target_group="all",
            k=42,
            alpha=0.85,
            cap=0.90,
            min_conflict_score=0.40,
            max_bad_same=0.98,
            worldview="only the strongest H057-positive/H088-toxic conflict edges matter",
        ),
        H096Spec(
            name="broad_lowcap_conflict_k145_a035",
            target_group="all",
            k=145,
            alpha=0.35,
            cap=0.45,
            min_conflict_score=0.03,
            max_bad_same=1.00,
            worldview="the conflict field is broad but should be moved softly to avoid calibration overshoot",
        ),
    ]


def select_cells(cell: pd.DataFrame, spec: H096Spec) -> pd.DataFrame:
    pos = cell["h057_positive_weight"].to_numpy(dtype=np.float64) > 0
    tox = cell["h088_toxicity"].to_numpy(dtype=np.float64) > 0
    anti = (
        np.sign(cell["h057_positive_logit_move"].to_numpy(dtype=np.float64))
        * np.sign(cell["h088_logit_move"].to_numpy(dtype=np.float64))
        < 0
    )
    pool = cell[pos & tox & anti & target_mask(cell, spec.target_group)].copy()
    pool["h096_conflict_score"] = (
        pool["h057_positive_weight"].to_numpy(dtype=np.float64)
        * pool["h088_toxicity"].to_numpy(dtype=np.float64)
        * (1.0 + 0.20 * rank01(pool["h085_q_gain"].to_numpy(dtype=np.float64), high=True))
        * (1.0 - 0.16 * pool["h080_bad_same_rank"].to_numpy(dtype=np.float64))
    )
    pool = pool[
        (pool["h096_conflict_score"] >= spec.min_conflict_score)
        & (pool["h080_bad_same_rank"] <= spec.max_bad_same)
    ].copy()
    return pool.sort_values("h096_conflict_score", ascending=False).head(spec.k).reset_index(drop=True)


def materialize_candidate(base_prob: np.ndarray, selected: pd.DataFrame, spec: H096Spec) -> np.ndarray:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        old = float(base_prob[row, tidx])
        move = float(np.clip(rec["h057_positive_logit_move"], -spec.cap, spec.cap) * spec.alpha)
        prob[row, tidx] = float(sigmoid(logit(np.array([old])) + np.array([move]))[0])
    return clip_prob(prob)


def cosine(delta_a: np.ndarray, delta_b: np.ndarray) -> float:
    a = np.asarray(delta_a, dtype=np.float64).reshape(-1)
    b = np.asarray(delta_b, dtype=np.float64).reshape(-1)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    base_prob: np.ndarray,
    selected: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    spec: H096Spec,
    path: Path,
) -> dict[str, object]:
    q096 = cell.sort_values("flat_index")["h085_q"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    qhard = cell.sort_values("flat_index")["q_hard"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    h088_prob = h095mod.load_optional_prob(h095mod.H088_FILE, sample)
    h042_prob = h095mod.load_optional_prob(h095mod.H042_FILE, sample)
    h050_prob = h095mod.load_optional_prob(h095mod.H050_FILE, sample)
    if h088_prob is None:
        raise FileNotFoundError(h095mod.H088_FILE)

    delta = prob - base_prob
    diff = np.abs(delta) > TOL
    selected_move = selected["h057_positive_logit_move"].to_numpy(dtype=np.float64)
    h088_move = selected["h088_logit_move"].to_numpy(dtype=np.float64)
    anti_rate = float((np.sign(selected_move) * np.sign(h088_move) < 0).mean()) if len(selected) else 0.0
    posterior_delta = float((bce(prob, q096) - bce(base_prob, q096)).mean())
    hard_delta = float((bce(prob, qhard) - bce(base_prob, qhard)).mean())
    validation = h085mod.validate_submission(path, sample, base_prob)
    bad_cos = h087mod.bad_anchor_cosines(delta, sample, base_prob)
    max_positive_bad = max([0.0] + [v for v in bad_cos.values() if v > 0])

    h042_cos = cosine(delta, base_prob - h042_prob) if h042_prob is not None else 0.0
    h050_cos = cosine(delta, base_prob - h050_prob) if h050_prob is not None else 0.0
    h088_cos = cosine(delta, h088_prob - base_prob)

    per_target = {
        f"{target}_changed_vs_h057": int(diff[:, i].sum())
        for i, target in enumerate(TARGETS)
    }
    scale = len(selected) / base_prob.size if base_prob.size else 0.0
    h096_score = (
        0.32 * float(selected["h096_conflict_score"].mean()) if len(selected) else 0.0
    )
    h096_score += (
        0.24 * anti_rate
        + 0.16 * max(h042_cos, 0.0)
        + 0.12 * max(h050_cos, 0.0)
        + 0.08 * min(scale / 0.08, 1.0)
        + 120.0 * (-posterior_delta)
        - 0.22 * max(h088_cos, 0.0)
        - 0.24 * max_positive_bad
        - 28.0 * max(hard_delta, 0.0)
    )

    out: dict[str, object] = {
        "candidate_id": candidate_id,
        "spec_name": spec.name,
        "target_group": spec.target_group,
        "worldview": spec.worldview,
        "k": spec.k,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_cells": int(len(selected)),
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "posterior_delta_vs_h057": posterior_delta,
        "hard_diag_delta_vs_h057": hard_delta,
        "mean_conflict_score": float(selected["h096_conflict_score"].mean()) if len(selected) else 0.0,
        "mean_h088_toxicity": float(selected["h088_toxicity"].mean()) if len(selected) else 0.0,
        "mean_h057_positive_weight": float(selected["h057_positive_weight"].mean()) if len(selected) else 0.0,
        "anti_h088_direction_rate": anti_rate,
        "cos_h057_vs_h042_direction": h042_cos,
        "cos_h057_vs_h050_direction": h050_cos,
        "cos_h088_direction": h088_cos,
        "max_positive_bad_cosine": float(max_positive_bad),
        "mean_bad_same_rank": float(selected["h080_bad_same_rank"].mean()) if len(selected) else 0.0,
        "mean_abs_prob_move_vs_h057": float(np.abs(delta).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(delta).max()),
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, sorted(selected["row"].astype(int).unique().tolist()))) if len(selected) else "",
        "h096_score": h096_score,
        "file": path.name,
        "resolved_path": str(path.resolve()),
    }
    out.update(per_target)
    out.update(bad_cos)
    out.update(validation)
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell = ensure_h095_cell_table(sample, base_prob)

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        selected = select_cells(cell, spec)
        if selected.empty:
            continue
        prob = materialize_candidate(base_prob, selected, spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h096_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(candidate_id, prob, base_prob, selected, cell, sample, spec, path)
        candidate_rows.append(metrics)
        selected = selected.copy()
        selected.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H096 candidates")
    candidates = candidates.sort_values(["h096_score", "mean_conflict_score"], ascending=[False, False]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h096_conflict_inversion_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h096_positive_toxic_conflict_inversion",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    candidates.to_csv(OUT / "h096_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h096_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h096_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "mean_conflict_score",
        "anti_h088_direction_rate",
        "cos_h057_vs_h042_direction",
        "cos_h057_vs_h050_direction",
        "cos_h088_direction",
        "max_positive_bad_cosine",
        "h096_score",
        "file",
    ]
    report = f"""# H096 Positive/Toxic Conflict Inversion HS-JEPA

Question: did H088 fail by reversing H057-positive cells rather than by touching
intrinsically unsafe cells?

Design:

- use H095's cell toxicity table;
- select cells where H057-positive weight and H088 toxicity overlap;
- require H057-positive direction to be opposite H088 direction;
- push selected cells further along H057-positive direction.

Candidates:

{md_table(candidates[cols], 20)}

Selected cells sample:

{md_table(pd.concat(selected_frames, ignore_index=True).head(80), 80)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H096 improves materially, H088's negative sensor means "do the opposite of
  this action on conflict cells", not "avoid these rows".
- If H096 loses, the H057/H088 conflict is not a reusable correction field; H088
  remains only a broad collapse diagnostic.
"""
    (OUT / "h096_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(8).to_string(index=False))


if __name__ == "__main__":
    run()
