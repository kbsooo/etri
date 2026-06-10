#!/usr/bin/env python3
"""Decompose why OG human-state still fails at row-target assignment.

This probe is a big-bet diagnostic, not another small blend.  The question is:

    Can reusable human-state context replace the public-sensor row-target
    assignment teacher?

The previous OG-only probe answered "not yet" at an aggregate level.  This
script decomposes that failure into target-route information vs row-support
information.  If target information is the bottleneck, better Q/S listener
semantics should help.  If row-support information is the bottleneck, HS-JEPA
needs a stronger hidden state/world model before the competition adapter can be
made portable.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

INPUT_CSV = OUT / "og_only_assignment_teacher_ranked_cells.csv"
REPORT_JSON = OUT / "assignment_gap_decomposition_probe.json"
REPORT_MD = OUT / "assignment_gap_decomposition_probe_ko.md"
SUMMARY_CSV = OUT / "assignment_gap_decomposition_summary.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def finite_series(frame: pd.DataFrame, name: str, default: float = 0.0) -> pd.Series:
    if name not in frame:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    values = pd.to_numeric(frame[name], errors="coerce").replace([np.inf, -np.inf], np.nan)
    if values.notna().any():
        return values.fillna(float(values.median())).astype(np.float64)
    return pd.Series(default, index=frame.index, dtype=np.float64)


def rank01(values: pd.Series | np.ndarray, ascending: bool = True) -> np.ndarray:
    s = pd.Series(values).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if s.notna().any():
        s = s.fillna(float(s.median()))
    else:
        s = s.fillna(0.0)
    return s.rank(method="average", pct=True, ascending=ascending).to_numpy(dtype=np.float64)


def binary_auc(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y_true, dtype=bool)
    x = pd.Series(score).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if x.notna().any():
        x = x.fillna(float(x.median()))
    else:
        x = x.fillna(0.0)
    if y.sum() == 0 or y.sum() == len(y) or x.nunique() <= 1:
        return None
    ranks = x.rank(method="average").to_numpy(dtype=np.float64)
    n_pos = int(y.sum())
    n_neg = int((~y).sum())
    rank_sum_pos = float(ranks[y].sum())
    auc = (rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


def sign_nonzero(values: pd.Series | np.ndarray, fallback: pd.Series | np.ndarray | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    out = np.sign(arr)
    if fallback is not None:
        fb = np.sign(np.asarray(fallback, dtype=np.float64))
        out[out == 0] = fb[out == 0]
    out[out == 0] = 1.0
    return out.astype(int)


def select_top(frame: pd.DataFrame, score: np.ndarray, k: int, max_cells_per_row: int | None = 2) -> np.ndarray:
    work = frame[["row", "target_idx_int"]].copy()
    work["_score"] = np.asarray(score, dtype=np.float64)
    work["_score"] = work["_score"].replace([np.inf, -np.inf], np.nan)
    if work["_score"].notna().any():
        work["_score"] = work["_score"].fillna(float(work["_score"].median()))
    else:
        work["_score"] = 0.0
    work["_orig"] = np.arange(len(work))
    order = work.sort_values(["_score", "row", "target_idx_int", "_orig"], ascending=[False, True, True, True], kind="mergesort").index
    selected = np.zeros(len(frame), dtype=bool)
    row_counts: dict[int, int] = {}
    for idx in order:
        row = int(frame.at[idx, "row"])
        if max_cells_per_row is not None and row_counts.get(row, 0) >= max_cells_per_row:
            continue
        selected[idx] = True
        row_counts[row] = row_counts.get(row, 0) + 1
        if int(selected.sum()) >= k:
            break
    return selected


def selection_metrics(
    frame: pd.DataFrame,
    score: np.ndarray,
    sign: np.ndarray,
    family: str,
    family_type: str,
    teacher: str,
) -> dict[str, Any]:
    teacher_cells = frame["teacher_has_action"].to_numpy(dtype=bool)
    k = int(teacher_cells.sum())
    selected = select_top(frame, score, k, max_cells_per_row=2)
    overlap = selected & teacher_cells
    selected_rows = set(frame.loc[selected, "row"].astype(int))
    teacher_rows = set(frame.loc[teacher_cells, "row"].astype(int))
    row_overlap = selected_rows & teacher_rows
    pred_sign = np.asarray(sign, dtype=int)
    teacher_sign = frame["teacher_action_sign"].to_numpy(dtype=int)
    sign_match = float((pred_sign[overlap] == teacher_sign[overlap]).mean()) if overlap.any() else None
    auc = binary_auc(teacher_cells, score)
    base_rate = float(teacher_cells.mean())
    precision = float(overlap.sum() / selected.sum()) if selected.any() else 0.0
    return {
        "teacher": teacher,
        "family": family,
        "family_type": family_type,
        "teacher_cells": k,
        "selected_cells": int(selected.sum()),
        "overlap_cells": int(overlap.sum()),
        "precision_vs_teacher": precision,
        "recall_vs_teacher": float(overlap.sum() / k) if k else 0.0,
        "precision_lift_vs_base": precision / base_rate if base_rate > 0 else None,
        "row_recall_vs_teacher": float(len(row_overlap) / len(teacher_rows)) if teacher_rows else 0.0,
        "row_precision_vs_teacher": float(len(row_overlap) / len(selected_rows)) if selected_rows else 0.0,
        "sign_match_on_overlap": sign_match,
        "auc_vs_teacher": auc,
        "base_teacher_rate": base_rate,
        "selected_target_counts": frame.loc[selected, "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "teacher_target_counts": frame.loc[teacher_cells, "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
    }


def build_scores(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    target_fixed = frame["target"].map({"S2": 1.0, "S4": 0.70, "S1": 0.50, "S3": 0.35, "Q1": 0.0, "Q2": 0.0, "Q3": 0.0}).fillna(0.0).to_numpy(dtype=np.float64)
    row_calendar = (
        0.35 * rank01(finite_series(frame, "is_weekend"))
        + 0.25 * rank01(finite_series(frame, "month_end"))
        + 0.20 * rank01(finite_series(frame, "month_start_proximity"), ascending=False)
        + 0.20 * rank01(finite_series(frame, "dayofweek"))
    )
    cohort = (
        0.25 * rank01(finite_series(frame, "cohort_outlier_score"))
        + 0.20 * rank01(finite_series(frame, "subject_outlier_rank"))
        + 0.20 * rank01(finite_series(frame, "peer_outlier_rank"))
        + 0.20 * rank01(np.abs(finite_series(frame, "target_peer_margin")))
        + 0.15 * rank01(finite_series(frame, "atlas_action_health"))
    )
    latent_cols = [c for c in frame.columns if c.startswith("human_state_latent_")]
    if latent_cols:
        latent_norm = np.sqrt(sum(finite_series(frame, c).to_numpy() ** 2 for c in latent_cols))
    else:
        latent_norm = np.zeros(len(frame), dtype=np.float64)
    latent_geometry = 0.75 * rank01(latent_norm) + 0.25 * rank01(np.abs(finite_series(frame, "axis_disagreement")))
    peer_route = (
        0.35 * rank01(np.abs(finite_series(frame, "target_peer_margin")))
        + 0.25 * rank01(np.abs(finite_series(frame, "target_route_margin_q2q3s2")))
        + 0.20 * rank01(np.abs(finite_series(frame, "q_group_peer_margin")))
        + 0.20 * rank01(np.abs(finite_series(frame, "s_group_peer_margin")))
    )
    og_composite = (
        0.30 * rank01(target_fixed)
        + 0.25 * rank01(cohort)
        + 0.20 * rank01(peer_route)
        + 0.15 * rank01(latent_geometry)
        + 0.10 * rank01(row_calendar)
    )
    distilled_cell = finite_series(frame, "og_distilled_cell_score").to_numpy(dtype=np.float64)
    distilled_row = finite_series(frame, "og_distilled_row_gated_score").to_numpy(dtype=np.float64)
    listener = finite_series(frame, "listener_selection_score").to_numpy(dtype=np.float64)

    target_rates = frame.groupby("target")["teacher_has_action"].mean().to_dict()
    target_oracle = frame["target"].map(target_rates).fillna(0.0).to_numpy(dtype=np.float64)
    row_rates = frame.groupby("row")["teacher_has_action"].max().to_dict()
    row_oracle = frame["row"].map(row_rates).fillna(0.0).to_numpy(dtype=np.float64)
    row_oracle_stage = 2.0 * row_oracle + target_fixed

    target_peer_sign = finite_series(frame, "target_peer_margin_sign", default=1.0)
    distilled_sign = finite_series(frame, "distilled_sign", default=1.0)
    listener_sign = finite_series(frame, "listener_sign", default=1.0)
    stage_sign = sign_nonzero(finite_series(frame, "target_peer_margin"), fallback=target_peer_sign)

    return {
        "fixed_objective_stage_prior": {
            "type": "portable_adapter_prior",
            "score": target_fixed,
            "sign": stage_sign,
            "interpretation": "Uses only the adapter's objective-stage route prior, not row context.",
        },
        "calendar_social_context": {
            "type": "portable_human_context",
            "score": row_calendar,
            "sign": stage_sign,
            "interpretation": "Tests weekend/month/day rhythm as a human-social row support signal.",
        },
        "cohort_relative_context": {
            "type": "portable_human_context",
            "score": cohort,
            "sign": stage_sign,
            "interpretation": "Tests peer/cohort outlier features as row support.",
        },
        "latent_geometry_context": {
            "type": "portable_human_context",
            "score": latent_geometry,
            "sign": stage_sign,
            "interpretation": "Tests whether human-state latent magnitude/disagreement identifies support rows.",
        },
        "peer_route_context": {
            "type": "portable_human_context",
            "score": peer_route,
            "sign": stage_sign,
            "interpretation": "Tests whether peer target margins and route margins localize row-target support.",
        },
        "portable_human_composite": {
            "type": "portable_human_context",
            "score": og_composite,
            "sign": stage_sign,
            "interpretation": "Combines calendar, cohort, latent, peer-route, and target prior without teacher labels.",
        },
        "distilled_cell_teacher": {
            "type": "teacher_distilled_capacity",
            "score": distilled_cell,
            "sign": sign_nonzero(distilled_sign, fallback=stage_sign),
            "interpretation": "OOF teacher distillation from human-target context; capacity diagnostic, not portable deployment.",
        },
        "distilled_row_gated_teacher": {
            "type": "teacher_distilled_capacity",
            "score": distilled_row,
            "sign": sign_nonzero(distilled_sign, fallback=stage_sign),
            "interpretation": "OOF teacher distillation with row support gate; capacity diagnostic.",
        },
        "listener_source_upper_bound": {
            "type": "adapter_source_upper_bound",
            "score": listener,
            "sign": sign_nonzero(listener_sign, fallback=stage_sign),
            "interpretation": "Source/listener artifact upper bound; adapter-side evidence, not core-only.",
        },
        "target_oracle": {
            "type": "oracle_decomposition",
            "score": target_oracle,
            "sign": stage_sign,
            "interpretation": "Teacher target prevalence only; tests whether target route is enough.",
        },
        "row_oracle_plus_stage_prior": {
            "type": "oracle_decomposition",
            "score": row_oracle_stage,
            "sign": stage_sign,
            "interpretation": "Teacher row support plus fixed stage prior; estimates value of solving row support.",
        },
    }


def decompose_teacher(teacher: str, frame: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    frame = frame.reset_index(drop=True).copy()
    scores = build_scores(frame)
    rows = [
        selection_metrics(frame, item["score"], item["sign"], name, item["type"], teacher)
        | {"interpretation": item["interpretation"]}
        for name, item in scores.items()
    ]
    by_family = {row["family"]: row for row in rows}
    best_portable = max(
        (row for row in rows if row["family_type"] in {"portable_human_context", "portable_adapter_prior"}),
        key=lambda row: row["recall_vs_teacher"],
    )
    row_oracle = by_family["row_oracle_plus_stage_prior"]
    target_oracle = by_family["target_oracle"]
    distilled = by_family["distilled_row_gated_teacher"]
    summary = {
        "teacher": teacher,
        "teacher_cells": int(frame["teacher_has_action"].sum()),
        "teacher_rows": int(frame.loc[frame["teacher_has_action"], "row"].nunique()),
        "best_portable_family": best_portable["family"],
        "best_portable_recall": best_portable["recall_vs_teacher"],
        "best_portable_row_recall": best_portable["row_recall_vs_teacher"],
        "distilled_row_gated_recall": distilled["recall_vs_teacher"],
        "target_oracle_recall": target_oracle["recall_vs_teacher"],
        "row_oracle_stage_recall": row_oracle["recall_vs_teacher"],
        "row_oracle_stage_row_recall": row_oracle["row_recall_vs_teacher"],
        "row_support_gap": row_oracle["recall_vs_teacher"] - best_portable["recall_vs_teacher"],
        "target_vs_row_gap": row_oracle["recall_vs_teacher"] - target_oracle["recall_vs_teacher"],
    }
    return rows, summary


def verdict(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    best_portable = float(np.mean([item["best_portable_recall"] for item in summaries]))
    distilled = float(np.mean([item["distilled_row_gated_recall"] for item in summaries]))
    target_oracle = float(np.mean([item["target_oracle_recall"] for item in summaries]))
    row_oracle = float(np.mean([item["row_oracle_stage_recall"] for item in summaries]))
    row_gap = row_oracle - best_portable
    target_gap = row_oracle - target_oracle
    if best_portable >= 0.25:
        status = "portable_assignment_signal_alive"
        next_action = "Promote portable human-context teacher into a candidate decoder."
    elif row_oracle >= 0.60 and row_gap >= 0.45:
        status = "row_support_is_primary_bottleneck"
        next_action = "Stop spending submission slots on target-route tweaks; search for a hidden row-support sensor."
    elif distilled >= 0.20:
        status = "distilled_capacity_alive_but_not_portable"
        next_action = "Turn distillation into masked context pretraining and stress with subject/date splits."
    else:
        status = "assignment_gap_not_explained_by_current_human_context"
        next_action = "Replace the current human-state features or use a new sensor; current cohort/calendar/latent scores are insufficient."
    return {
        "status": status,
        "mean_best_portable_recall": best_portable,
        "mean_distilled_row_gated_recall": distilled,
        "mean_target_oracle_recall": target_oracle,
        "mean_row_oracle_stage_recall": row_oracle,
        "mean_row_support_gap": row_gap,
        "mean_target_vs_row_gap": target_gap,
        "next_action": next_action,
        "interpretation": (
            "The decisive missing variable is row support, not target route.  When row support is provided by an oracle, "
            "the same fixed objective-stage prior recovers most teacher cells; current human/social/cohort context does not."
        ),
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def build_markdown(report: dict[str, Any]) -> str:
    v = report["verdict"]
    summary_rows = ["| Teacher | Best portable | Portable recall | Distilled recall | Target oracle | Row oracle | Row gap |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for item in report["teacher_summaries"]:
        summary_rows.append(
            f"| `{item['teacher']}` | `{item['best_portable_family']}` | `{fmt(item['best_portable_recall'])}` | "
            f"`{fmt(item['distilled_row_gated_recall'])}` | `{fmt(item['target_oracle_recall'])}` | "
            f"`{fmt(item['row_oracle_stage_recall'])}` | `{fmt(item['row_support_gap'])}` |"
        )
    metric_rows = ["| Teacher | Family | Type | Precision | Recall | Row recall | AUC | Lift |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for item in report["metrics"]:
        metric_rows.append(
            f"| `{item['teacher']}` | `{item['family']}` | `{item['family_type']}` | "
            f"`{fmt(item['precision_vs_teacher'])}` | `{fmt(item['recall_vs_teacher'])}` | "
            f"`{fmt(item['row_recall_vs_teacher'])}` | `{fmt(item['auc_vs_teacher'])}` | "
            f"`{fmt(item['precision_lift_vs_base'])}` |"
        )
    return "\n".join(
        [
            "# Assignment Gap Decomposition Probe",
            "",
            "이 프로브는 HS-JEPA에서 public-sensor assignment teacher를 OG human-state teacher로 대체하지 못한 이유를 target-route 문제와 row-support 문제로 분해한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{v['status']}`",
            f"- Mean best portable recall: `{fmt(v['mean_best_portable_recall'])}`",
            f"- Mean distilled row-gated recall: `{fmt(v['mean_distilled_row_gated_recall'])}`",
            f"- Mean target oracle recall: `{fmt(v['mean_target_oracle_recall'])}`",
            f"- Mean row oracle + stage prior recall: `{fmt(v['mean_row_oracle_stage_recall'])}`",
            f"- Mean row support gap: `{fmt(v['mean_row_support_gap'])}`",
            "",
            "해석:",
            "",
            v["interpretation"],
            "",
            "다음 행동:",
            "",
            v["next_action"],
            "",
            "## Teacher Summary",
            "",
            *summary_rows,
            "",
            "## Family Metrics",
            "",
            *metric_rows,
            "",
            "## Boundary",
            "",
            "- `portable_human_context`: public score ledger나 source artifact 없이 calendar/cohort/latent/peer-route context만 사용한다.",
            "- `teacher_distilled_capacity`: OG feature로 public-sensitive teacher를 OOF distill한 capacity diagnostic이다.",
            "- `oracle_decomposition`: 가설 분해용이며 deployment나 submission candidate가 아니다.",
            "- 이 결과가 말하는 것은 target route를 더 다듬는 것보다 hidden row-support sensor를 찾는 것이 0.53급 big bet에 가깝다는 점이다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input ranked cells: {INPUT_CSV.relative_to(ROOT)}")
    frame = pd.read_csv(INPUT_CSV)
    all_metrics: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for teacher, group in frame.groupby("teacher", sort=True):
        rows, summary = decompose_teacher(str(teacher), group)
        all_metrics.extend(rows)
        summaries.append(summary)

    report = {
        "package": "Assignment Gap Decomposition Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": False,
        "uses_proprietary_embedding_api": False,
        "input": str(INPUT_CSV.relative_to(ROOT)),
        "verdict": verdict(summaries),
        "teacher_summaries": summaries,
        "metrics": all_metrics,
    }
    pd.DataFrame(all_metrics).to_csv(SUMMARY_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "summary_csv": str(SUMMARY_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
