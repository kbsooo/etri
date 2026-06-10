#!/usr/bin/env python3
"""Probe whether the toxicity field is action-health or public memorization.

The current competition adapter has a public/private toxicity head.  This probe
tests whether that field is strong enough to justify a "private-safe" big bet:

1. Leave-one-anchor-out bad-action recovery.
   If a bad public anchor is held out, do the other bad anchors still rank the
   held-out bad cells as toxic?

2. Matched-null selection stress.
   Are toxicity-head selected cells safer than random cells matched by target
   and teacher/source status?

If the answer is no, the toxicity field remains a public-sensor diagnostic,
not an action-grade private-safe decoder.
"""

from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import math
import sys

import numpy as np
import pandas as pd

from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

TOX_OUT = ROOT / "paper_hsjepa_core" / "outputs" / "public_private_toxicity_head"
TOX_CANDIDATES = TOX_OUT / "toxicity_candidate_cell_table.csv"
TOX_ACTIONS = TOX_OUT / "toxicity_action_audit.csv"
TOX_LEDGER = TOX_OUT / "toxicity_anchor_ledger.csv"
CANDIDATE1_MODULE = ROOT / "final_hsjepa_candidates" / "candidate_1_public_loss_sparse_tomography.py"

REPORT_JSON = OUT / "private_safe_toxicity_probe.json"
REPORT_MD = OUT / "private_safe_toxicity_probe_ko.md"
SCORED_CSV = OUT / "private_safe_toxicity_scored_cells.csv"
LOO_CSV = OUT / "private_safe_toxicity_loo_anchor_metrics.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "private_safe_toxicity_candidate1")


def fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def rank01(values: pd.Series | np.ndarray, ascending: bool = True) -> pd.Series:
    s = pd.Series(values).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if s.notna().any():
        s = s.fillna(float(s.median()))
    else:
        s = s.fillna(0.0)
    return s.rank(method="average", pct=True, ascending=ascending).astype(np.float64)


def metric_safe(y: np.ndarray, score: np.ndarray) -> dict[str, object]:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return {"auc": None, "ap": float(y.mean()) if len(y) else None, "positive_rate": float(y.mean()) if len(y) else 0.0}
    return {
        "auc": float(roc_auc_score(y, score)),
        "ap": float(average_precision_score(y, score)),
        "positive_rate": float(y.mean()),
    }


def load_bad_anchor_moves(candidates: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    sample, _base_prob, base_logit, _base_grads, _semantic_grads, _h088_move = candidate1.load_world()
    ledger = pd.read_csv(TOX_LEDGER)
    rows = []
    moves = []
    flat = candidates["flat_idx"].astype(int).to_numpy()
    sign = candidates["candidate_sign"].astype(int).to_numpy()
    for rec in ledger.to_dict("records"):
        file = str(rec["file"])
        move = candidate1.movement_from_file(file, sample, base_logit)
        if move is None:
            continue
        signed_active = (np.abs(move[flat]) > TOL) & (np.sign(move[flat]).astype(int) == sign)
        opposite_active = (np.abs(move[flat]) > TOL) & (np.sign(move[flat]).astype(int) == -sign)
        rows.append(
            {
                "file": file,
                "public_lb": float(rec["public_lb"]),
                "candidate_same_active_cells": int(signed_active.sum()),
                "candidate_opposite_active_cells": int(opposite_active.sum()),
                "available": True,
            }
        )
        moves.append(move[flat])
    if not rows:
        raise RuntimeError("No toxicity anchor movements could be loaded")
    return pd.DataFrame(rows), np.vstack(moves)


def leave_one_anchor_metrics(candidates: pd.DataFrame, anchor_moves: np.ndarray, anchor_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    flat_sign = candidates["candidate_sign"].astype(int).to_numpy()
    same = (np.abs(anchor_moves) > TOL) & (np.sign(anchor_moves).astype(int) == flat_sign[None, :])
    abs_same = np.abs(anchor_moves) * same
    total_same = abs_same.sum(axis=0)
    total_count = same.sum(axis=0)
    loo_rows = []
    per_cell = candidates[["flat_idx", "row", "target", "candidate_sign"]].copy()
    per_cell["bad_anchor_same_count"] = total_count
    per_cell["bad_anchor_same_weight"] = total_same
    per_cell["bad_anchor_same_count_rank"] = rank01(per_cell["bad_anchor_same_count"])
    per_cell["bad_anchor_same_weight_rank"] = rank01(per_cell["bad_anchor_same_weight"])
    for idx, rec in anchor_rows.iterrows():
        y = same[idx].astype(int)
        loo_score = total_same - abs_same[idx]
        metrics = metric_safe(y, loo_score)
        loo_rows.append(
            {
                "file": rec["file"],
                "public_lb": float(rec["public_lb"]),
                "positive_cells": int(y.sum()),
                "positive_rate": metrics["positive_rate"],
                "loo_auc": metrics["auc"],
                "loo_ap": metrics["ap"],
                "loo_mean_score_positive": float(loo_score[y.astype(bool)].mean()) if y.any() else 0.0,
                "loo_mean_score_negative": float(loo_score[~y.astype(bool)].mean()) if (~y.astype(bool)).any() else 0.0,
            }
        )
    return pd.DataFrame(loo_rows), per_cell


def matched_null_selection(candidates: pd.DataFrame, actions: pd.DataFrame, seed: int = 20260610, iterations: int = 5000) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    cand = candidates.copy()
    cand["key"] = list(zip(cand["flat_idx"].astype(int), cand["candidate_sign"].astype(int)))
    selected_keys = set(zip(actions["flat_idx"].astype(int), actions["candidate_sign"].astype(int)))
    cand["selected_by_toxicity_head"] = cand["key"].isin(selected_keys)
    selected = cand[cand["selected_by_toxicity_head"]].copy()
    if selected.empty:
        raise RuntimeError("No selected toxicity actions")

    group_cols = ["target", "teacher_has_action", "lrj_has_cell"]
    target_counts = selected.groupby(group_cols, dropna=False).size().to_dict()
    null_safety = []
    null_toxic = []
    null_listener = []
    for _ in range(iterations):
        sampled_parts = []
        for group_key, count in target_counts.items():
            mask = np.ones(len(cand), dtype=bool)
            for col, value in zip(group_cols, group_key):
                mask &= cand[col].to_numpy() == value
            pool = cand[mask]
            if len(pool) < count:
                pool = cand[cand["target"] == group_key[0]]
            replace = len(pool) < count
            sampled_parts.append(pool.sample(n=count, replace=replace, random_state=int(rng.integers(0, 2**31 - 1))))
        null = pd.concat(sampled_parts, ignore_index=True)
        null_safety.append(float(null["toxic_safety_rank"].mean()))
        null_toxic.append(float(null["toxic_same_rank"].mean()))
        null_listener.append(float(null["selection_score"].mean()))

    null_safety_arr = np.asarray(null_safety, dtype=np.float64)
    null_toxic_arr = np.asarray(null_toxic, dtype=np.float64)
    null_listener_arr = np.asarray(null_listener, dtype=np.float64)
    actual_safety = float(selected["toxic_safety_rank"].mean())
    actual_toxic = float(selected["toxic_same_rank"].mean())
    actual_listener = float(selected["selection_score"].mean())
    return {
        "iterations": iterations,
        "selected_cells": int(len(selected)),
        "candidate_cells": int(len(cand)),
        "selected_toxic_safety_rank_mean": actual_safety,
        "null_toxic_safety_rank_mean": float(null_safety_arr.mean()),
        "null_toxic_safety_rank_std": float(null_safety_arr.std(ddof=1)),
        "selected_safety_z": float((actual_safety - null_safety_arr.mean()) / (null_safety_arr.std(ddof=1) + 1e-12)),
        "p_null_safety_ge_selected": float((null_safety_arr >= actual_safety).mean()),
        "selected_toxic_same_rank_mean": actual_toxic,
        "null_toxic_same_rank_mean": float(null_toxic_arr.mean()),
        "p_null_toxic_le_selected": float((null_toxic_arr <= actual_toxic).mean()),
        "selected_listener_score_mean": actual_listener,
        "null_listener_score_mean": float(null_listener_arr.mean()),
        "p_null_listener_ge_selected": float((null_listener_arr >= actual_listener).mean()),
        "target_counts": selected["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "action_source_counts": actions["action_source"].value_counts().astype(int).to_dict() if "action_source" in actions else {},
    }


def aggregate_verdict(loo: pd.DataFrame, null_metrics: dict[str, object]) -> dict[str, object]:
    auc_values = [float(v) for v in loo["loo_auc"].dropna()]
    mean_loo_auc = float(np.mean(auc_values)) if auc_values else 0.0
    median_loo_auc = float(np.median(auc_values)) if auc_values else 0.0
    mean_loo_ap = float(loo["loo_ap"].dropna().mean()) if loo["loo_ap"].notna().any() else 0.0
    worst_loo_auc = float(np.min(auc_values)) if auc_values else 0.0
    anchors_below_0p6 = int((loo["loo_auc"].fillna(0.0) < 0.60).sum())
    selected_safety_z = float(null_metrics["selected_safety_z"])
    p_safety = float(null_metrics["p_null_safety_ge_selected"])

    if (
        mean_loo_auc >= 0.70
        and worst_loo_auc >= 0.55
        and anchors_below_0p6 <= 1
        and selected_safety_z >= 2.0
        and p_safety <= 0.05
    ):
        status = "private_safe_toxicity_field_promising"
    elif mean_loo_auc >= 0.70 and selected_safety_z >= 2.0 and p_safety <= 0.05:
        status = "toxicity_field_promising_with_hardworld_gap"
    elif mean_loo_auc >= 0.62 or selected_safety_z >= 1.0:
        status = "toxicity_field_alive_but_public_sensor_bound"
    else:
        status = "private_safe_toxicity_field_not_ready"

    return {
        "status": status,
        "mean_loo_bad_anchor_auc": mean_loo_auc,
        "median_loo_bad_anchor_auc": median_loo_auc,
        "mean_loo_bad_anchor_ap": mean_loo_ap,
        "worst_loo_bad_anchor_auc": worst_loo_auc,
        "anchors_below_0p6_auc": anchors_below_0p6,
        "selected_safety_z_vs_matched_null": selected_safety_z,
        "p_null_safety_ge_selected": p_safety,
        "interpretation": (
            "The toxicity field generalizes across bad anchors and selects cells safer than matched nulls."
            if status == "private_safe_toxicity_field_promising"
            else (
                "The toxicity field is strong on most bad anchors, but a hard-world toxicity mode is still not captured."
                if status == "toxicity_field_promising_with_hardworld_gap"
                else "The toxicity field is useful as a public-sensor diagnostic, but not yet strong enough to claim private-safe decoding."
            )
        ),
    }


def build_markdown(report: dict[str, object]) -> str:
    verdict = report["verdict"]
    null = report["matched_null_selection"]
    return "\n".join(
        [
            "# Private-Safe Toxicity Probe",
            "",
            "이 프로브는 public/private toxicity head가 단순히 나쁜 제출을 기억하는 장치인지, 아니면 action-health field로 볼 수 있는지 확인한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Mean leave-one-bad-anchor AUC: `{fmt(verdict['mean_loo_bad_anchor_auc'])}`",
            f"- Median leave-one-bad-anchor AUC: `{fmt(verdict['median_loo_bad_anchor_auc'])}`",
            f"- Mean leave-one-bad-anchor AP: `{fmt(verdict['mean_loo_bad_anchor_ap'])}`",
            f"- Worst leave-one-bad-anchor AUC: `{fmt(verdict['worst_loo_bad_anchor_auc'])}`",
            f"- Anchors below 0.60 AUC: `{verdict['anchors_below_0p6_auc']}`",
            f"- Selected safety z vs matched null: `{fmt(verdict['selected_safety_z_vs_matched_null'])}`",
            f"- P(null safety >= selected): `{fmt(verdict['p_null_safety_ge_selected'])}`",
            "",
            verdict["interpretation"],
            "",
            "## Matched-Null Selection Stress",
            "",
            f"- Selected cells: `{null['selected_cells']}` / candidate cells `{null['candidate_cells']}`",
            f"- Selected toxicity safety mean: `{fmt(null['selected_toxic_safety_rank_mean'])}`",
            f"- Null toxicity safety mean: `{fmt(null['null_toxic_safety_rank_mean'])}`",
            f"- Selected toxicity rank mean: `{fmt(null['selected_toxic_same_rank_mean'])}`",
            f"- Null toxicity rank mean: `{fmt(null['null_toxic_same_rank_mean'])}`",
            f"- Selected listener score mean: `{fmt(null['selected_listener_score_mean'])}`",
            f"- Null listener score mean: `{fmt(null['null_listener_score_mean'])}`",
            "",
            "## Boundary",
            "",
            "- `leave-one-anchor`가 높아도 이는 bad public anchors 사이의 일반화일 뿐 private LB 증거는 아니다.",
            "- matched null 대비 safety가 높지 않으면 toxicity head는 action decoder가 아니라 diagnostic으로만 써야 한다.",
            "- 이 probe는 새 submission을 만들지 않는다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidates = pd.read_csv(TOX_CANDIDATES)
    actions = pd.read_csv(TOX_ACTIONS)
    anchor_rows, anchor_moves = load_bad_anchor_moves(candidates)
    loo, per_cell = leave_one_anchor_metrics(candidates, anchor_moves, anchor_rows)
    null_metrics = matched_null_selection(candidates, actions)
    report = {
        "package": "Private-Safe Toxicity Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": True,
        "uses_private_labels": False,
        "bad_anchor_count": int(len(anchor_rows)),
        "verdict": aggregate_verdict(loo, null_metrics),
        "matched_null_selection": null_metrics,
        "anchor_summary": {
            "available_bad_anchors": int(len(anchor_rows)),
            "mean_same_active_cells": float(anchor_rows["candidate_same_active_cells"].mean()),
            "mean_opposite_active_cells": float(anchor_rows["candidate_opposite_active_cells"].mean()),
        },
    }
    scored = candidates.merge(per_cell, on=["flat_idx", "row", "target", "candidate_sign"], how="left")
    loo.to_csv(LOO_CSV, index=False)
    scored.to_csv(SCORED_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "scored_csv": str(SCORED_CSV.resolve()),
        "loo_csv": str(LOO_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
