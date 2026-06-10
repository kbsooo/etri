#!/usr/bin/env python3
"""Probe whether OG human-state can replace public-sensor assignment.

This is a boundary test for HS-JEPA:

1. Unsupervised OG human-state rank
   Uses only lifestyle/cohort/route-context geometry.  No public score ledger,
   no submission-source consensus, and no teacher labels.

2. Human-state teacher distillation
   Uses subject-held-out OOF probabilities already produced by the human-state
   distillation module.  Inputs are OG human-state features, but the target is a
   public-sensitive action teacher, so this is a capacity diagnostic rather than
   a portable deployment recipe.

3. Listener/source upper bound
   Uses the listener-responsibility artifact.  This is not OG-only; it tells us
   how much extra assignment information the competition adapter has beyond the
   reusable HS-JEPA core.
"""

from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

DISTILL_OUT = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_human_state_distillation"
LISTENER_OUT = ROOT / "paper_hsjepa_core" / "outputs" / "listener_responsibility_jepa"

TEACHERS = {
    "s2hub_jackpot": {
        "cell_frame": DISTILL_OUT / "s2hub_jackpot_cell_student_frame.csv",
        "row_frame": DISTILL_OUT / "s2hub_jackpot_row_student_frame.csv",
    },
    "stagebridge_jackpot": {
        "cell_frame": DISTILL_OUT / "stagebridge_jackpot_cell_student_frame.csv",
        "row_frame": DISTILL_OUT / "stagebridge_jackpot_row_student_frame.csv",
    },
}

LISTENER_RANKED = LISTENER_OUT / "listener_responsibility_ranked_cells.csv"
LISTENER_READOUT = LISTENER_OUT / "listener_responsibility_readout.json"

REPORT_JSON = OUT / "og_only_assignment_teacher_probe.json"
REPORT_MD = OUT / "og_only_assignment_teacher_probe_ko.md"
RANKED_CSV = OUT / "og_only_assignment_teacher_ranked_cells.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def finite_series(frame: pd.DataFrame, name: str, default: float = 0.0) -> pd.Series:
    if name not in frame:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    values = pd.to_numeric(frame[name], errors="coerce").replace([np.inf, -np.inf], np.nan)
    if values.notna().any():
        return values.fillna(float(values.median())).astype(np.float64)
    return pd.Series(default, index=frame.index, dtype=np.float64)


def rank01(values: pd.Series | np.ndarray, ascending: bool = True) -> pd.Series:
    s = pd.Series(values).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if s.notna().any():
        s = s.fillna(float(s.median()))
    else:
        s = s.fillna(0.0)
    return s.rank(method="average", pct=True, ascending=ascending).astype(np.float64)


def sign_nonzero(values: pd.Series | np.ndarray, fallback: pd.Series | np.ndarray | None = None) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    out = np.sign(arr)
    if fallback is not None:
        fb = np.sign(np.asarray(fallback, dtype=np.float64))
        out[out == 0] = fb[out == 0]
    out[out == 0] = 1.0
    return out.astype(int)


def load_teacher_frame(cell_path: Path, row_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(cell_path)
    row = pd.read_csv(row_path)[["row", "student_oof_row_prob", "teacher_row_has_action"]].copy()
    frame["row"] = frame["row"].astype(int)
    row["row"] = row["row"].astype(int)
    frame = frame.merge(row, on="row", how="left", suffixes=("", "_row"))
    frame["target_idx_int"] = frame["target_idx_int"].astype(int)
    frame["flat_idx"] = frame["row"].astype(int) * len(TARGETS) + frame["target_idx_int"].astype(int)
    frame["teacher_has_action"] = finite_series(frame, "teacher_has_action").gt(0.5)
    frame["teacher_action_sign"] = sign_nonzero(finite_series(frame, "teacher_action_sign"))
    return frame


def add_og_scores(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["og_unsupervised_score"] = (
        0.18 * rank01(finite_series(out, "base_uncertainty"))
        + 0.17 * rank01(finite_series(out, "cohort_outlier_score"))
        + 0.15 * rank01(finite_series(out, "atlas_action_health"))
        + 0.12 * rank01(finite_series(out, "axis_disagreement").abs())
        + 0.12 * rank01(finite_series(out, "target_peer_margin_abs"))
        + 0.10 * rank01(finite_series(out, "target_route_margin_q2q3s2").abs())
        + 0.08 * rank01(finite_series(out, "subject_outlier_rank"))
        + 0.08 * rank01(finite_series(out, "peer_outlier_rank"))
    )
    out["og_row_context_score"] = (
        0.52 * rank01(finite_series(out, "oof_prob_human_row_context_only"))
        + 0.20 * rank01(finite_series(out, "oof_move_human_row_context_only").abs())
        + 0.18 * rank01(finite_series(out, "student_oof_row_prob"))
        + 0.10 * rank01(finite_series(out, "target_peer_margin_abs"))
    )
    out["og_distilled_cell_score"] = (
        0.63 * rank01(finite_series(out, "oof_prob_human_target_context"))
        + 0.22 * rank01(finite_series(out, "oof_move_human_target_context").abs())
        + 0.15 * rank01(out["og_unsupervised_score"])
    )
    out["og_distilled_row_gated_score"] = (
        0.64 * rank01(out["og_distilled_cell_score"])
        + 0.26 * rank01(finite_series(out, "student_oof_row_prob"))
        + 0.10 * rank01(out["og_row_context_score"])
    )
    out["unsupervised_sign"] = sign_nonzero(
        0.6 * finite_series(out, "target_peer_margin")
        + 0.3 * finite_series(out, "target_route_margin_q2q3s2")
        + 0.1 * finite_series(out, "q_group_peer_margin"),
        fallback=finite_series(out, "target_peer_margin_sign"),
    )
    out["distilled_sign"] = sign_nonzero(
        finite_series(out, "oof_move_human_target_context"),
        fallback=out["unsupervised_sign"],
    )
    out["row_context_sign"] = sign_nonzero(
        finite_series(out, "oof_move_human_row_context_only"),
        fallback=out["unsupervised_sign"],
    )
    return out


def add_listener_scores(frame: pd.DataFrame) -> pd.DataFrame:
    if not LISTENER_RANKED.exists():
        frame["listener_selection_score"] = 0.0
        frame["listener_sign"] = 1
        return frame
    listener = pd.read_csv(LISTENER_RANKED)
    keep = ["flat_idx", "selection_score", "responsibility_score", "sign"]
    listener = listener[[c for c in keep if c in listener]].copy()
    merged = frame.merge(listener, on="flat_idx", how="left")
    merged["listener_selection_score"] = finite_series(merged, "selection_score", default=0.0)
    merged["listener_responsibility_score"] = finite_series(merged, "responsibility_score", default=0.0)
    merged["listener_sign"] = sign_nonzero(finite_series(merged, "sign", default=1.0))
    return merged


def select_top(frame: pd.DataFrame, score_col: str, k: int, max_cells_per_row: int | None = None) -> np.ndarray:
    selected = np.zeros(len(frame), dtype=bool)
    row_counts: dict[int, int] = {}
    order = frame.sort_values(score_col, ascending=False, kind="mergesort").index.to_numpy()
    for idx in order:
        row = int(frame.at[idx, "row"])
        if max_cells_per_row is not None and row_counts.get(row, 0) >= max_cells_per_row:
            continue
        selected[idx] = True
        row_counts[row] = row_counts.get(row, 0) + 1
        if selected.sum() >= k:
            break
    return selected


def selection_metrics(
    frame: pd.DataFrame,
    selected: np.ndarray,
    sign_col: str,
    score_col: str,
    teacher_count: int,
) -> dict[str, object]:
    teacher = frame["teacher_has_action"].to_numpy(dtype=bool)
    overlap = selected & teacher
    pred_sign = np.asarray(frame[sign_col], dtype=int)
    teacher_sign = frame["teacher_action_sign"].to_numpy(dtype=int)
    selected_rows = set(frame.loc[selected, "row"].astype(int))
    teacher_rows = set(frame.loc[teacher, "row"].astype(int))
    row_overlap = selected_rows & teacher_rows
    base_rate = float(teacher.mean()) if len(teacher) else 0.0
    selected_count = int(selected.sum())
    overlap_count = int(overlap.sum())
    row_precision = len(row_overlap) / len(selected_rows) if selected_rows else 0.0
    row_recall = len(row_overlap) / len(teacher_rows) if teacher_rows else 0.0
    sign_match = float((pred_sign[overlap] == teacher_sign[overlap]).mean()) if overlap_count else None
    top_decile_k = max(1, int(math.ceil(len(frame) * 0.10)))
    top_decile = select_top(frame, score_col, top_decile_k, max_cells_per_row=None)
    top_decile_rate = float(teacher[top_decile].mean()) if top_decile.any() else 0.0
    target_counts = frame.loc[selected, "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict()
    teacher_target_counts = frame.loc[teacher, "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict()
    return {
        "teacher_cells": int(teacher_count),
        "selected_cells": selected_count,
        "overlap_cells": overlap_count,
        "precision_vs_teacher": overlap_count / selected_count if selected_count else 0.0,
        "recall_vs_teacher": overlap_count / teacher_count if teacher_count else 0.0,
        "base_teacher_rate": base_rate,
        "precision_lift_vs_base": (overlap_count / selected_count) / base_rate if selected_count and base_rate > 0 else None,
        "sign_match_on_overlap": sign_match,
        "teacher_rows": len(teacher_rows),
        "selected_rows": len(selected_rows),
        "overlap_rows": len(row_overlap),
        "row_precision_vs_teacher": row_precision,
        "row_recall_vs_teacher": row_recall,
        "top_decile_teacher_rate": top_decile_rate,
        "top_decile_lift_vs_base": top_decile_rate / base_rate if base_rate > 0 else None,
        "target_counts": target_counts,
        "teacher_target_counts": teacher_target_counts,
    }


def evaluate_family(frame: pd.DataFrame, score_col: str, sign_col: str, family: str, k: int) -> list[dict[str, object]]:
    rows = []
    for cap_name, cap in [("uncapped", None), ("row_cap_2", 2), ("row_cap_1", 1)]:
        selected = select_top(frame, score_col, k, max_cells_per_row=cap)
        metrics = selection_metrics(frame, selected, sign_col, score_col, k)
        rows.append(
            {
                "family": family,
                "score_col": score_col,
                "sign_col": sign_col,
                "row_cap": cap_name,
                "uses_public_score_ledger": False,
                "uses_teacher_labels_for_training": family in {"og_teacher_distilled", "og_teacher_distilled_row_gated", "og_row_context_teacher"},
                "uses_submission_source_artifacts": family == "listener_source_upper_bound",
                **metrics,
            }
        )
    return rows


def probe_teacher(name: str, paths: dict[str, Path]) -> tuple[list[dict[str, object]], pd.DataFrame]:
    frame = load_teacher_frame(paths["cell_frame"], paths["row_frame"])
    frame = add_listener_scores(add_og_scores(frame))
    teacher_count = int(frame["teacher_has_action"].sum())
    if teacher_count <= 0:
        raise ValueError(f"{name} has no teacher actions")

    rows: list[dict[str, object]] = []
    families = [
        ("og_unsupervised", "og_unsupervised_score", "unsupervised_sign"),
        ("og_row_context_teacher", "og_row_context_score", "row_context_sign"),
        ("og_teacher_distilled", "og_distilled_cell_score", "distilled_sign"),
        ("og_teacher_distilled_row_gated", "og_distilled_row_gated_score", "distilled_sign"),
        ("listener_source_upper_bound", "listener_selection_score", "listener_sign"),
    ]
    for family, score_col, sign_col in families:
        for row in evaluate_family(frame, score_col, sign_col, family, teacher_count):
            row["teacher"] = name
            rows.append(row)

    frame["teacher"] = name
    return rows, frame


def verdict(rows: list[dict[str, object]]) -> dict[str, object]:
    pure = [
        row
        for row in rows
        if row["family"] == "og_unsupervised" and row["row_cap"] == "row_cap_2"
    ]
    distilled = [
        row
        for row in rows
        if row["family"] == "og_teacher_distilled_row_gated" and row["row_cap"] == "row_cap_2"
    ]
    upper = [
        row
        for row in rows
        if row["family"] == "listener_source_upper_bound" and row["row_cap"] == "row_cap_2"
    ]

    def mean_metric(records: list[dict[str, object]], key: str) -> float:
        values = [float(row[key]) for row in records if row.get(key) is not None]
        return float(np.mean(values)) if values else 0.0

    pure_recall = mean_metric(pure, "recall_vs_teacher")
    pure_lift = mean_metric(pure, "precision_lift_vs_base")
    distilled_recall = mean_metric(distilled, "recall_vs_teacher")
    distilled_precision = mean_metric(distilled, "precision_vs_teacher")
    upper_recall = mean_metric(upper, "recall_vs_teacher")

    if pure_recall >= 0.35 and pure_lift >= 1.50:
        status = "og_unsupervised_assignment_signal_alive"
    elif distilled_recall >= 0.35 and distilled_precision >= 0.25:
        status = "teacher_distillation_alive_but_not_portable"
    else:
        status = "og_only_assignment_replacement_not_ready"

    return {
        "status": status,
        "pure_og_row_cap2_mean_recall": pure_recall,
        "pure_og_row_cap2_mean_precision_lift": pure_lift,
        "distilled_row_cap2_mean_recall": distilled_recall,
        "distilled_row_cap2_mean_precision": distilled_precision,
        "listener_upper_bound_row_cap2_mean_recall": upper_recall,
        "interpretation": (
            "Pure OG human-state is sufficient to replace the public-sensor assignment teacher."
            if status == "og_unsupervised_assignment_signal_alive"
            else "Human-state explains action orientation, but the safe row-target assignment still needs adapter-side evidence."
        ),
    }


def build_markdown(report: dict[str, object]) -> str:
    summary = report["verdict"]
    rows = ["| Teacher | Family | Cap | Precision | Recall | Row recall | Sign match | Lift |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for item in report["metrics"]:
        if item["row_cap"] != "row_cap_2":
            continue
        rows.append(
            f"| `{item['teacher']}` | `{item['family']}` | `{item['row_cap']}` | "
            f"`{item['precision_vs_teacher']:.4f}` | `{item['recall_vs_teacher']:.4f}` | "
            f"`{item['row_recall_vs_teacher']:.4f}` | `{fmt_optional(item['sign_match_on_overlap'])}` | "
            f"`{fmt_optional(item['precision_lift_vs_base'])}` |"
        )

    return "\n".join(
        [
            "# OG-only Human-State Assignment Teacher Probe",
            "",
            "이 프로브는 HS-JEPA Core가 public LB sensor 없이 row-target action assignment를 얼마나 설명할 수 있는지 확인한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{summary['status']}`",
            f"- Pure OG row-cap2 mean recall: `{summary['pure_og_row_cap2_mean_recall']:.4f}`",
            f"- Pure OG row-cap2 mean precision lift: `{summary['pure_og_row_cap2_mean_precision_lift']:.4f}`",
            f"- Distilled row-cap2 mean recall: `{summary['distilled_row_cap2_mean_recall']:.4f}`",
            f"- Distilled row-cap2 mean precision: `{summary['distilled_row_cap2_mean_precision']:.4f}`",
            f"- Listener/source upper-bound row-cap2 mean recall: `{summary['listener_upper_bound_row_cap2_mean_recall']:.4f}`",
            "",
            "해석:",
            "",
            summary["interpretation"],
            "",
            "## Row-Capped Metrics",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- `og_unsupervised`: teacher label도 source artifact도 쓰지 않는 가장 강한 portability test.",
            "- `og_teacher_distilled*`: OG feature로 public-sensitive teacher를 subject-held-out으로 distill한 capacity diagnostic.",
            "- `listener_source_upper_bound`: source/listener artifact를 쓰는 adapter-side upper bound이며 pure HS-JEPA core 증거가 아니다.",
            "",
        ]
    )


def fmt_optional(value: object, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def run() -> dict[str, object]:
    all_rows: list[dict[str, object]] = []
    ranked_frames: list[pd.DataFrame] = []
    for teacher, paths in TEACHERS.items():
        rows, frame = probe_teacher(teacher, paths)
        all_rows.extend(rows)
        ranked_frames.append(frame)

    listener_readout = read_json(LISTENER_READOUT) if LISTENER_READOUT.exists() else {}
    report = {
        "package": "OG-only Human-State Assignment Teacher Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": False,
        "uses_proprietary_embedding_api": False,
        "teacher_frames": {k: {kk: str(vv.relative_to(ROOT)) for kk, vv in v.items()} for k, v in TEACHERS.items()},
        "listener_upper_bound_public_score_ledger_used": listener_readout.get("public_score_ledger_used"),
        "verdict": verdict(all_rows),
        "metrics": all_rows,
    }

    ranked = pd.concat(ranked_frames, ignore_index=True)
    ranked.to_csv(RANKED_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")

    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "ranked_csv": str(RANKED_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
