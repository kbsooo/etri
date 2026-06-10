#!/usr/bin/env python3
"""Probe whether hard-world toxicity is a separate HS-JEPA action mode.

The private-safe toxicity probe found a specific failure: broad bad-anchor
toxicity generalizes across most failed submissions but fails on the H088
hard-world anchor.  This probe asks a narrower question:

    Is H088 just a hard example of the same toxicity field, or a separate
    toxicity mode that must be factorized into its own head?

It does not create a submission.  It decides whether the sleep competition
adapter should treat action-health as a mixture of broad-public toxicity and
hard-world toxicity instead of a single scalar score.
"""

from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd

from sklearn.metrics import average_precision_score, roc_auc_score

import private_safe_toxicity_probe as pst


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

TOX_OUT = ROOT / "paper_hsjepa_core" / "outputs" / "public_private_toxicity_head"
TOX_CANDIDATES = TOX_OUT / "toxicity_candidate_cell_table.csv"
TOX_ACTIONS = TOX_OUT / "toxicity_action_audit.csv"

REPORT_JSON = OUT / "hardworld_toxicity_factorization_probe.json"
REPORT_MD = OUT / "hardworld_toxicity_factorization_probe_ko.md"
SECTOR_CSV = OUT / "hardworld_toxicity_factorization_sectors.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
HARDWORLD_TOKEN = "h088"
TOL = 1e-12


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


def metric_safe(y: np.ndarray, score: np.ndarray) -> dict[str, object]:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    if len(y) == 0 or len(np.unique(y)) < 2:
        return {
            "auc": None,
            "ap": float(y.mean()) if len(y) else None,
            "positive_rate": float(y.mean()) if len(y) else 0.0,
        }
    return {
        "auc": float(roc_auc_score(y, score)),
        "ap": float(average_precision_score(y, score)),
        "positive_rate": float(y.mean()),
    }


def rank01(values: pd.Series | np.ndarray, ascending: bool = True) -> pd.Series:
    return pst.rank01(values, ascending=ascending)


def z_and_p(actual: float, null_values: list[float], higher_is_better: bool = True) -> dict[str, float]:
    arr = np.asarray(null_values, dtype=np.float64)
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = float((actual - float(arr.mean())) / (std + 1e-12))
    if higher_is_better:
        p = float((arr >= actual).mean())
    else:
        p = float((arr <= actual).mean())
    return {"z": z, "p": p, "null_mean": float(arr.mean()), "null_std": std}


def matched_null(candidates: pd.DataFrame, iterations: int = 5000, seed: int = 20260610) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    selected = candidates[candidates["selected_by_existing_decoder"]].copy()
    if selected.empty:
        raise RuntimeError("No selected cells found for hard-world null stress")

    group_cols = ["target", "teacher_has_action", "lrj_has_cell"]
    group_counts = selected.groupby(group_cols, dropna=False).size().to_dict()
    null_hard_safe: list[float] = []
    null_joint_safe: list[float] = []
    null_hard_top: list[float] = []
    null_conflict: list[float] = []
    null_listener: list[float] = []

    for _ in range(iterations):
        parts = []
        for group_key, count in group_counts.items():
            mask = np.ones(len(candidates), dtype=bool)
            for col, value in zip(group_cols, group_key):
                mask &= candidates[col].to_numpy() == value
            pool = candidates[mask]
            if len(pool) < count:
                pool = candidates[candidates["target"] == group_key[0]]
            parts.append(
                pool.sample(
                    n=count,
                    replace=len(pool) < count,
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
        null = pd.concat(parts, ignore_index=True)
        null_hard_safe.append(float(null["hardworld_safe_rank"].mean()))
        null_joint_safe.append(float(null["joint_safety_min_rank"].mean()))
        null_hard_top.append(float(null["hardworld_top_toxic"].mean()))
        null_conflict.append(float(null["broad_safe_hardworld_toxic"].mean()))
        null_listener.append(float(null["selection_score"].mean()))

    actual_hard_safe = float(selected["hardworld_safe_rank"].mean())
    actual_joint_safe = float(selected["joint_safety_min_rank"].mean())
    actual_hard_top = float(selected["hardworld_top_toxic"].mean())
    actual_conflict = float(selected["broad_safe_hardworld_toxic"].mean())
    actual_listener = float(selected["selection_score"].mean())

    hard_safe = z_and_p(actual_hard_safe, null_hard_safe, higher_is_better=True)
    joint_safe = z_and_p(actual_joint_safe, null_joint_safe, higher_is_better=True)
    hard_top = z_and_p(actual_hard_top, null_hard_top, higher_is_better=False)
    conflict = z_and_p(actual_conflict, null_conflict, higher_is_better=False)
    listener = z_and_p(actual_listener, null_listener, higher_is_better=True)
    return {
        "iterations": iterations,
        "selected_cells": int(len(selected)),
        "candidate_cells": int(len(candidates)),
        "selected_hardworld_safe_mean": actual_hard_safe,
        "null_hardworld_safe_mean": hard_safe["null_mean"],
        "hardworld_safe_z": hard_safe["z"],
        "p_null_hardworld_safe_ge_selected": hard_safe["p"],
        "selected_joint_safety_mean": actual_joint_safe,
        "null_joint_safety_mean": joint_safe["null_mean"],
        "joint_safety_z": joint_safe["z"],
        "p_null_joint_safety_ge_selected": joint_safe["p"],
        "selected_hardworld_top_toxic_rate": actual_hard_top,
        "null_hardworld_top_toxic_rate": hard_top["null_mean"],
        "hardworld_top_toxic_z": hard_top["z"],
        "p_null_hardworld_top_toxic_le_selected": hard_top["p"],
        "selected_broad_safe_hardworld_toxic_rate": actual_conflict,
        "null_broad_safe_hardworld_toxic_rate": conflict["null_mean"],
        "broad_safe_hardworld_toxic_z": conflict["z"],
        "p_null_conflict_le_selected": conflict["p"],
        "selected_listener_score_mean": actual_listener,
        "null_listener_score_mean": listener["null_mean"],
        "listener_score_z": listener["z"],
        "target_counts": selected["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
    }


def build_scored_cells(candidates: pd.DataFrame, anchor_rows: pd.DataFrame, anchor_moves: np.ndarray) -> tuple[pd.DataFrame, dict[str, object]]:
    hard_idx = [
        idx
        for idx, file in enumerate(anchor_rows["file"].astype(str).str.lower().tolist())
        if HARDWORLD_TOKEN in file
    ]
    if len(hard_idx) != 1:
        raise RuntimeError(f"Expected exactly one hard-world anchor containing {HARDWORLD_TOKEN}, got {hard_idx}")
    hard_idx_int = int(hard_idx[0])

    flat_sign = candidates["candidate_sign"].astype(int).to_numpy()
    same = (np.abs(anchor_moves) > TOL) & (np.sign(anchor_moves).astype(int) == flat_sign[None, :])
    same_weight = np.abs(anchor_moves) * same
    hardworld_weight = same_weight[hard_idx_int]
    broad_weight = np.delete(same_weight, hard_idx_int, axis=0).sum(axis=0)

    scored = candidates.copy()
    scored["hardworld_same_weight"] = hardworld_weight
    scored["hardworld_active"] = hardworld_weight > TOL
    scored["hardworld_toxic_rank"] = rank01(hardworld_weight)
    scored["hardworld_safe_rank"] = 1.0 - scored["hardworld_toxic_rank"]
    scored["broad_same_weight_ex_hardworld"] = broad_weight
    scored["broad_toxic_rank_ex_hardworld"] = rank01(broad_weight)
    scored["broad_safe_rank_ex_hardworld"] = 1.0 - scored["broad_toxic_rank_ex_hardworld"]
    scored["joint_safety_min_rank"] = np.minimum(
        scored["toxic_safety_rank"].astype(float),
        scored["hardworld_safe_rank"].astype(float),
    )
    scored["broad_safe_hardworld_toxic"] = (
        (scored["broad_toxic_rank_ex_hardworld"] <= 0.40)
        & (scored["hardworld_toxic_rank"] >= 0.60)
    )
    scored["broad_toxic_hardworld_safe"] = (
        (scored["broad_toxic_rank_ex_hardworld"] >= 0.60)
        & (scored["hardworld_toxic_rank"] <= 0.40)
    )
    scored["hardworld_top_toxic"] = scored["hardworld_toxic_rank"] >= 0.75
    scored["broad_top_toxic"] = scored["broad_toxic_rank_ex_hardworld"] >= 0.75

    selected_keys = set()
    actions = pd.read_csv(TOX_ACTIONS)
    if not actions.empty:
        selected_keys = set(zip(actions["flat_idx"].astype(int), actions["candidate_sign"].astype(int)))
    scored["key"] = list(zip(scored["flat_idx"].astype(int), scored["candidate_sign"].astype(int)))
    scored["selected_by_existing_decoder"] = scored["key"].isin(selected_keys)
    scored = scored.drop(columns=["key"])

    hardworld_active = scored["hardworld_active"].to_numpy(dtype=bool)
    broad_score = scored["broad_same_weight_ex_hardworld"].to_numpy(dtype=np.float64)
    hard_score = scored["hardworld_same_weight"].to_numpy(dtype=np.float64)
    mode_metrics = {
        "hardworld_anchor_file": str(anchor_rows.iloc[hard_idx_int]["file"]),
        "hardworld_public_lb": float(anchor_rows.iloc[hard_idx_int]["public_lb"]),
        "hardworld_positive_cells": int(hardworld_active.sum()),
        "hardworld_positive_rate": float(hardworld_active.mean()),
        "broad_predicts_hardworld_auc": metric_safe(hardworld_active.astype(int), broad_score)["auc"],
        "broad_predicts_hardworld_ap": metric_safe(hardworld_active.astype(int), broad_score)["ap"],
        "broad_hardworld_spearman": float(pd.Series(broad_score).corr(pd.Series(hard_score), method="spearman")),
        "broad_hardworld_pearson": float(np.corrcoef(broad_score, hard_score)[0, 1]),
        "hardworld_active_rate_broad_top_quartile": float(scored.loc[scored["broad_top_toxic"], "hardworld_active"].mean()),
        "hardworld_active_rate_broad_bottom_quartile": float(scored.loc[scored["broad_toxic_rank_ex_hardworld"] <= 0.25, "hardworld_active"].mean()),
        "broad_safe_hardworld_toxic_cells": int(scored["broad_safe_hardworld_toxic"].sum()),
        "broad_toxic_hardworld_safe_cells": int(scored["broad_toxic_hardworld_safe"].sum()),
        "selected_hardworld_active_rate": float(scored.loc[scored["selected_by_existing_decoder"], "hardworld_active"].mean()),
        "all_hardworld_active_rate": float(scored["hardworld_active"].mean()),
        "selected_hardworld_top_toxic_rate": float(scored.loc[scored["selected_by_existing_decoder"], "hardworld_top_toxic"].mean()),
        "all_hardworld_top_toxic_rate": float(scored["hardworld_top_toxic"].mean()),
        "selected_broad_safe_hardworld_toxic_cells": int(
            (scored["selected_by_existing_decoder"] & scored["broad_safe_hardworld_toxic"]).sum()
        ),
    }
    return scored, mode_metrics


def aggregate_verdict(mode: dict[str, object], null_metrics: dict[str, object]) -> dict[str, object]:
    broad_auc = float(mode["broad_predicts_hardworld_auc"])
    rho = float(mode["broad_hardworld_spearman"])
    conflict_cells = int(mode["broad_safe_hardworld_toxic_cells"])
    joint_z = float(null_metrics["joint_safety_z"])
    hard_top_selected = float(null_metrics["selected_hardworld_top_toxic_rate"])
    hard_top_null = float(null_metrics["null_hardworld_top_toxic_rate"])

    if broad_auc < 0.45 and rho < -0.25 and conflict_cells >= 100 and joint_z >= 2.0 and hard_top_selected < hard_top_null:
        status = "hardworld_mixture_factorization_required"
        interpretation = (
            "H088 is not a harder sample of broad toxicity; it is an anti-correlated hard-world mode. "
            "The adapter should keep separate broad-public and hard-world toxicity heads."
        )
    elif broad_auc < 0.55 and conflict_cells >= 50:
        status = "hardworld_mode_alive_but_decoder_not_validated"
        interpretation = (
            "H088 carries a distinct toxicity pattern, but current selected actions do not yet prove a safe mixture decoder."
        )
    else:
        status = "hardworld_factorization_not_supported"
        interpretation = "H088 does not separate strongly enough from broad toxicity to justify a new decoder head."

    return {
        "status": status,
        "broad_predicts_hardworld_auc": broad_auc,
        "broad_hardworld_spearman": rho,
        "broad_safe_hardworld_toxic_cells": conflict_cells,
        "selected_joint_safety_z": joint_z,
        "selected_hardworld_top_toxic_rate": hard_top_selected,
        "null_hardworld_top_toxic_rate": hard_top_null,
        "interpretation": interpretation,
    }


def sector_summary(scored: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    sector_defs = {
        "broad_safe_hardworld_toxic": scored["broad_safe_hardworld_toxic"],
        "broad_toxic_hardworld_safe": scored["broad_toxic_hardworld_safe"],
        "dual_safe": (scored["broad_toxic_rank_ex_hardworld"] <= 0.40) & (scored["hardworld_toxic_rank"] <= 0.40),
        "dual_toxic": (scored["broad_toxic_rank_ex_hardworld"] >= 0.60) & (scored["hardworld_toxic_rank"] >= 0.60),
    }
    for name, mask in sector_defs.items():
        part = scored[mask].copy()
        rows.append(
            {
                "sector": name,
                "cells": int(len(part)),
                "selected_cells": int(part["selected_by_existing_decoder"].sum()) if len(part) else 0,
                "mean_selection_score": float(part["selection_score"].mean()) if len(part) else 0.0,
                "mean_broad_toxic_rank": float(part["broad_toxic_rank_ex_hardworld"].mean()) if len(part) else 0.0,
                "mean_hardworld_toxic_rank": float(part["hardworld_toxic_rank"].mean()) if len(part) else 0.0,
                "target_counts": part["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict() if len(part) else {},
            }
        )
    return rows


def build_markdown(report: dict[str, object]) -> str:
    verdict = report["verdict"]
    mode = report["mode_separation"]
    null = report["matched_null_selection"]
    sectors = report["sector_summary"]
    sector_rows = ["| Sector | Cells | Selected | Mean broad toxic | Mean hard toxic |", "| --- | ---: | ---: | ---: | ---: |"]
    for rec in sectors:
        sector_rows.append(
            f"| `{rec['sector']}` | `{rec['cells']}` | `{rec['selected_cells']}` | "
            f"`{fmt(rec['mean_broad_toxic_rank'])}` | `{fmt(rec['mean_hardworld_toxic_rank'])}` |"
        )
    return "\n".join(
        [
            "# Hard-World Toxicity Factorization Probe",
            "",
            "이 프로브는 H088 hard-world 실패가 broad bad-anchor toxicity의 한 사례인지, 아니면 별도 action-health mode인지 검증한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Broad toxicity -> H088 AUC: `{fmt(verdict['broad_predicts_hardworld_auc'])}`",
            f"- Broad/H088 Spearman: `{fmt(verdict['broad_hardworld_spearman'])}`",
            f"- Broad-safe but H088-toxic cells: `{verdict['broad_safe_hardworld_toxic_cells']}`",
            f"- Selected joint safety z: `{fmt(verdict['selected_joint_safety_z'])}`",
            f"- Selected H088 top-toxic rate: `{fmt(verdict['selected_hardworld_top_toxic_rate'])}` vs null `{fmt(verdict['null_hardworld_top_toxic_rate'])}`",
            "",
            verdict["interpretation"],
            "",
            "## Mode Separation",
            "",
            f"- Hard-world anchor: `{mode['hardworld_anchor_file']}`",
            f"- H088 active cells: `{mode['hardworld_positive_cells']}` / `{fmt(mode['hardworld_positive_rate'])}`",
            f"- H088 active rate in broad top quartile: `{fmt(mode['hardworld_active_rate_broad_top_quartile'])}`",
            f"- H088 active rate in broad bottom quartile: `{fmt(mode['hardworld_active_rate_broad_bottom_quartile'])}`",
            f"- Existing decoder selected H088 top-toxic rate: `{fmt(mode['selected_hardworld_top_toxic_rate'])}`",
            f"- All candidates H088 top-toxic rate: `{fmt(mode['all_hardworld_top_toxic_rate'])}`",
            "",
            "## Matched-Null Stress",
            "",
            f"- Selected cells: `{null['selected_cells']}` / candidates `{null['candidate_cells']}`",
            f"- Selected hard-world safety mean: `{fmt(null['selected_hardworld_safe_mean'])}` vs null `{fmt(null['null_hardworld_safe_mean'])}`",
            f"- Hard-world safety z: `{fmt(null['hardworld_safe_z'])}`",
            f"- Selected joint safety mean: `{fmt(null['selected_joint_safety_mean'])}` vs null `{fmt(null['null_joint_safety_mean'])}`",
            f"- Joint safety z: `{fmt(null['joint_safety_z'])}`",
            f"- Selected broad-safe/H088-toxic rate: `{fmt(null['selected_broad_safe_hardworld_toxic_rate'])}` vs null `{fmt(null['null_broad_safe_hardworld_toxic_rate'])}`",
            "",
            "## Sectors",
            "",
            *sector_rows,
            "",
            "## Decoder Implication",
            "",
            "Scalar toxicity is not enough.  HS-JEPA action-health should be represented as at least two listener-conditioned heads:",
            "",
            "```text",
            "broad public-bad toxicity head",
            "  + hard-world / H088 toxicity head",
            "  -> joint safety or mixture-gated action decoder",
            "```",
            "",
            "이 probe는 새 submission을 만들지 않는다. 다음 big-bet은 이 factorized toxicity를 실제 row-target assignment solver에 넣는 것이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidates = pd.read_csv(TOX_CANDIDATES)
    anchor_rows, anchor_moves = pst.load_bad_anchor_moves(candidates)
    scored, mode = build_scored_cells(candidates, anchor_rows, anchor_moves)
    null_metrics = matched_null(scored)
    report = {
        "package": "Hard-World Toxicity Factorization Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": True,
        "uses_private_labels": False,
        "verdict": aggregate_verdict(mode, null_metrics),
        "mode_separation": mode,
        "matched_null_selection": null_metrics,
        "sector_summary": sector_summary(scored),
    }
    scored.to_csv(SECTOR_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "sector_csv": str(SECTOR_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
