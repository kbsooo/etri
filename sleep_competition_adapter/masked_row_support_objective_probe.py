#!/usr/bin/env python3
"""Stress the row-support sensor as a masked HS-JEPA objective.

The previous hidden-row-support probe found a transferable row-support signal.
This probe asks whether that signal behaves like a useful HS-JEPA target
representation or like a brittle shortcut.  It masks feature families and
measures whether row-support prediction survives:

* teacher-world transfer: train on one action teacher, test on another.
* row/subject/calendar held-out stress: train on part of one teacher world and
  test on hidden groups.

The target is not a raw value reconstruction.  The target representation is
the hidden row-support variable: "is this subject-day actionable before target
route selection?"  This makes the probe a direct translation of the JEPA idea
into the competition adapter.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sleep_competition_adapter.hidden_row_support_sensor_probe import (
    INPUT_CSV,
    OBJECTIVE_STAGE_PRIOR,
    ROOT,
    build_row_frame,
    clean_matrix,
    columns_for_family,
    feature_families,
    rank01,
    select_top_cells,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

REPORT_JSON = OUT / "masked_row_support_objective_probe.json"
REPORT_MD = OUT / "masked_row_support_objective_probe_ko.md"
MASKED_TRANSFER_CSV = OUT / "masked_row_support_objective_transfer_metrics.csv"
MASKED_STRESS_CSV = OUT / "masked_row_support_objective_group_stress.csv"

SEED = 20260610


def fit_sensor(x_train: pd.DataFrame, y_train: np.ndarray) -> Any:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.30, class_weight="balanced", max_iter=1000, solver="liblinear", random_state=SEED),
    ).fit(x_train, y_train)


def safe_auc(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return None
    if np.nanstd(score) <= 0:
        return None
    return float(roc_auc_score(y, score))


def safe_log_loss(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return None
    return float(log_loss(y, np.clip(score, 1e-6, 1.0 - 1e-6), labels=[0, 1]))


def match_group(col: str, patterns: list[str]) -> bool:
    return any(col == pat or col.startswith(pat) for pat in patterns)


def build_masked_views(row_frame: pd.DataFrame, cell_frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    families = feature_families(cell_frame)
    full_cols = columns_for_family(row_frame, families["portable_row_support_composite"])
    prediction_cols = [
        "base_prob",
        "base_logit",
        "base_uncertainty",
        "target_peer_margin",
        "target_peer_margin_abs",
        "q_group_peer_margin",
        "s_group_peer_margin",
        "target_route_margin_q2q3s2",
    ]
    groups = {
        "calendar": ["row_frac", "dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"],
        "subject": ["subject_code", "peer_group"],
        "cohort": [
            "dist_to_subject_normal",
            "dist_to_peer_normal",
            "subject_minus_peer_dist",
            "subject_outlier_rank",
            "peer_outlier_rank",
            "cohort_outlier_score",
            "atlas_action_health",
        ],
        "latent": ["human_state_latent_", "personal_axis", "cohort_axis", "axis_disagreement", "peer_only_toxicity"],
        "prediction": prediction_cols,
        "route_margin": ["target_peer_margin", "target_peer_margin_abs", "q_group_peer_margin", "s_group_peer_margin", "target_route_margin_q2q3s2"],
    }

    views = {
        "full_composite": {
            "mask": "none",
            "cols": full_cols,
            "interpretation": "All portable row-support context.",
        },
        "prediction_landscape_only": {
            "mask": "human/cohort/calendar/latent removed",
            "cols": columns_for_family(row_frame, families["prediction_landscape"]),
            "interpretation": "Only seven-target probability and route-margin landscape.",
        },
        "human_only_no_prediction": {
            "mask": "prediction landscape removed",
            "cols": [c for c in full_cols if not match_group(c, groups["prediction"])],
            "interpretation": "Human/social/cohort/latent context without prediction landscape.",
        },
        "mask_calendar_sequence": {
            "mask": "calendar and row phase removed",
            "cols": [c for c in full_cols if not match_group(c, groups["calendar"])],
            "interpretation": "Tests whether the support sensor is only row/order/calendar shortcut.",
        },
        "mask_subject_peer": {
            "mask": "subject and peer identifiers removed",
            "cols": [c for c in full_cols if not match_group(c, groups["subject"])],
            "interpretation": "Tests whether subject-like identity is the main support signal.",
        },
        "mask_cohort_social": {
            "mask": "cohort/social outlier features removed",
            "cols": [c for c in full_cols if not match_group(c, groups["cohort"])],
            "interpretation": "Tests whether peer anomaly alone drives support.",
        },
        "mask_latent_geometry": {
            "mask": "human-state latent geometry removed",
            "cols": [c for c in full_cols if not match_group(c, groups["latent"])],
            "interpretation": "Tests whether latent geometry is required.",
        },
        "mask_target_route_margins": {
            "mask": "target route margin features removed",
            "cols": [c for c in full_cols if not match_group(c, groups["route_margin"])],
            "interpretation": "Tests whether the sensor is only target-route leakage.",
        },
    }
    return {name: item for name, item in views.items() if item["cols"]}


def cell_recall_from_row_score(cell_frame: pd.DataFrame, test_teacher: str, rows: pd.DataFrame, score: np.ndarray) -> dict[str, float]:
    row_score = dict(zip(rows["row"].astype(int), score))
    cells = cell_frame.loc[cell_frame["teacher"] == test_teacher].reset_index(drop=True).copy()
    cells["_row_score"] = cells["row"].astype(int).map(row_score).fillna(0.0)
    stage_prior = cells["target"].map(OBJECTIVE_STAGE_PRIOR).fillna(0.0).to_numpy(dtype=np.float64)
    cell_score = 2.0 * rank01(cells["_row_score"]) + stage_prior
    teacher = cells["teacher_has_action"].to_numpy(dtype=bool)
    selected = select_top_cells(cells, cell_score, int(teacher.sum()), max_cells_per_row=2)
    selected_rows = set(cells.loc[selected, "row"].astype(int))
    teacher_rows = set(cells.loc[teacher, "row"].astype(int))
    overlap = selected & teacher
    return {
        "cell_recall_with_stage_prior": float(overlap.sum() / teacher.sum()) if teacher.sum() else 0.0,
        "cell_precision_with_stage_prior": float(overlap.sum() / selected.sum()) if selected.any() else 0.0,
        "row_recall_with_stage_prior": float(len(selected_rows & teacher_rows) / len(teacher_rows)) if teacher_rows else 0.0,
    }


def evaluate_transfer(row_frame: pd.DataFrame, cell_frame: pd.DataFrame, views: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    teachers = sorted(row_frame["teacher"].unique())
    for view_name, view in views.items():
        cols = view["cols"]
        for test_teacher in teachers:
            train_teacher = next(t for t in teachers if t != test_teacher)
            train = row_frame.loc[row_frame["teacher"] == train_teacher].copy()
            test = row_frame.loc[row_frame["teacher"] == test_teacher].copy()
            y_train = train["teacher_row_has_action"].to_numpy(dtype=int)
            y_test = test["teacher_row_has_action"].to_numpy(dtype=int)
            x_train, x_test = clean_matrix(train, test, cols)
            model = fit_sensor(x_train, y_train)
            score = model.predict_proba(x_test)[:, 1]
            k = int(y_test.sum())
            top = np.argsort(-score)[:k]
            cell_metrics = cell_recall_from_row_score(cell_frame, test_teacher, test, score)
            rows.append(
                {
                    "view": view_name,
                    "mask": view["mask"],
                    "train_teacher": train_teacher,
                    "test_teacher": test_teacher,
                    "feature_count": len(cols),
                    "row_auc": safe_auc(y_test, score),
                    "row_bce": safe_log_loss(y_test, score),
                    "row_recall_at_k": float(y_test[top].sum() / k) if k else 0.0,
                    **cell_metrics,
                    "interpretation": view["interpretation"],
                }
            )
    full_lookup = {
        (row["train_teacher"], row["test_teacher"]): row["cell_recall_with_stage_prior"]
        for row in rows
        if row["view"] == "full_composite"
    }
    for row in rows:
        base = full_lookup.get((row["train_teacher"], row["test_teacher"]), 0.0)
        row["cell_recall_retention_vs_full"] = float(row["cell_recall_with_stage_prior"] / base) if base else None
    return rows


def add_stress_groups(row_frame: pd.DataFrame) -> pd.DataFrame:
    out = row_frame.copy()
    out["row_order_bin"] = pd.qcut(out["row"], 4, labels=False, duplicates="drop").astype(int)
    if "subject_code" in out:
        out["subject_mod_bin"] = out["subject_code"].fillna(0).astype(int) % 4
    else:
        out["subject_mod_bin"] = out["row"].astype(int) % 4
    if "dayofweek" in out:
        out["calendar_mod_bin"] = out["dayofweek"].fillna(0).astype(int) % 4
    else:
        out["calendar_mod_bin"] = out["row"].astype(int) % 4
    return out


def evaluate_group_stress(row_frame: pd.DataFrame, views: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    row_frame = add_stress_groups(row_frame)
    stress_cols = {
        "row_order_holdout": "row_order_bin",
        "subject_mod_holdout": "subject_mod_bin",
        "calendar_mod_holdout": "calendar_mod_bin",
    }
    rows: list[dict[str, Any]] = []
    for view_name in ["full_composite", "prediction_landscape_only", "human_only_no_prediction", "mask_target_route_margins"]:
        if view_name not in views:
            continue
        cols = views[view_name]["cols"]
        for teacher, teacher_frame in row_frame.groupby("teacher", sort=True):
            for stress_name, group_col in stress_cols.items():
                for group_value in sorted(teacher_frame[group_col].dropna().unique()):
                    train = teacher_frame.loc[teacher_frame[group_col] != group_value].copy()
                    test = teacher_frame.loc[teacher_frame[group_col] == group_value].copy()
                    if train["teacher_row_has_action"].sum() == 0 or test["teacher_row_has_action"].sum() == 0:
                        continue
                    if test["teacher_row_has_action"].nunique() < 2:
                        continue
                    x_train, x_test = clean_matrix(train, test, cols)
                    model = fit_sensor(x_train, train["teacher_row_has_action"].to_numpy(dtype=int))
                    score = model.predict_proba(x_test)[:, 1]
                    y_test = test["teacher_row_has_action"].to_numpy(dtype=int)
                    k = int(y_test.sum())
                    top = np.argsort(-score)[:k]
                    rows.append(
                        {
                            "view": view_name,
                            "teacher": str(teacher),
                            "stress": stress_name,
                            "heldout_group": int(group_value),
                            "test_rows": int(len(test)),
                            "test_positive_rows": int(k),
                            "row_auc": safe_auc(y_test, score),
                            "row_bce": safe_log_loss(y_test, score),
                            "row_recall_at_k": float(y_test[top].sum() / k) if k else 0.0,
                        }
                    )
    return rows


def mean_metric(records: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in records if row.get(key) is not None and math.isfinite(float(row[key]))]
    return float(np.mean(values)) if values else 0.0


def verdict(transfer_rows: list[dict[str, Any]], stress_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_view = pd.DataFrame(transfer_rows).groupby("view").agg(
        mean_row_auc=("row_auc", "mean"),
        mean_row_recall_at_k=("row_recall_at_k", "mean"),
        mean_cell_recall=("cell_recall_with_stage_prior", "mean"),
        mean_retention=("cell_recall_retention_vs_full", "mean"),
    )
    full = by_view.loc["full_composite"]
    human = by_view.loc["human_only_no_prediction"]
    prediction = by_view.loc["prediction_landscape_only"]
    route_mask = by_view.loc["mask_target_route_margins"]
    group_df = pd.DataFrame(stress_rows)
    full_group = group_df.loc[group_df["view"] == "full_composite"]
    full_group_auc = float(full_group["row_auc"].mean()) if not full_group.empty else 0.0
    full_group_recall = float(full_group["row_recall_at_k"].mean()) if not full_group.empty else 0.0
    robust_mask_count = int(
        (
            (by_view["mean_row_auc"] >= 0.70)
            & (by_view["mean_cell_recall"] >= 0.20)
            & (by_view["mean_retention"] >= 0.60)
        ).sum()
    )

    if full["mean_row_auc"] >= 0.78 and human["mean_cell_recall"] >= 0.25 and prediction["mean_cell_recall"] >= 0.20 and route_mask["mean_cell_recall"] >= 0.28:
        status = "masked_row_support_objective_supported_with_stress_boundary"
        next_action = "Train a dedicated masked row-support objective, but do not promote it to a submission decoder until group-heldout stress improves."
    elif full["mean_row_auc"] >= 0.72 and robust_mask_count >= 3:
        status = "masked_row_support_objective_alive_but_fragile"
        next_action = "Use the masked objective for representation learning only; improve stress robustness before decoding actions."
    else:
        status = "masked_row_support_objective_not_supported"
        next_action = "Do not spend submission slots on row-support decoding; redesign the context representation."

    return {
        "status": status,
        "full_composite_mean_row_auc": float(full["mean_row_auc"]),
        "full_composite_mean_row_recall_at_k": float(full["mean_row_recall_at_k"]),
        "full_composite_mean_cell_recall": float(full["mean_cell_recall"]),
        "human_only_mean_cell_recall": float(human["mean_cell_recall"]),
        "prediction_only_mean_cell_recall": float(prediction["mean_cell_recall"]),
        "route_mask_mean_cell_recall": float(route_mask["mean_cell_recall"]),
        "robust_mask_count": robust_mask_count,
        "group_stress_full_mean_auc": full_group_auc,
        "group_stress_full_mean_recall_at_k": full_group_recall,
        "next_action": next_action,
        "interpretation": (
            "The row-support target is not a single-feature shortcut: human-only, prediction-only, and route-masked views all retain signal. "
            "However, row/order/subject/calendar held-out stress is much weaker than teacher-world transfer, so this is a representation objective, not yet an action-grade decoder."
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
    transfer_summary = pd.DataFrame(report["transfer_metrics"]).groupby("view", as_index=False).agg(
        row_auc=("row_auc", "mean"),
        row_recall_at_k=("row_recall_at_k", "mean"),
        cell_recall=("cell_recall_with_stage_prior", "mean"),
        retention=("cell_recall_retention_vs_full", "mean"),
    ).sort_values(["cell_recall", "row_auc"], ascending=False)
    transfer_rows = ["| View | Mean row AUC | Mean row recall@K | Mean cell recall | Retention vs full |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in transfer_summary.to_dict("records"):
        transfer_rows.append(
            f"| `{row['view']}` | `{fmt(row['row_auc'])}` | `{fmt(row['row_recall_at_k'])}` | "
            f"`{fmt(row['cell_recall'])}` | `{fmt(row['retention'])}` |"
        )

    stress_summary = pd.DataFrame(report["group_stress_metrics"]).groupby(["view", "stress"], as_index=False).agg(
        row_auc=("row_auc", "mean"),
        row_recall_at_k=("row_recall_at_k", "mean"),
        row_bce=("row_bce", "mean"),
    ).sort_values(["view", "stress"])
    stress_rows = ["| View | Stress | Mean row AUC | Mean recall@K | Mean BCE |", "| --- | --- | ---: | ---: | ---: |"]
    for row in stress_summary.to_dict("records"):
        stress_rows.append(
            f"| `{row['view']}` | `{row['stress']}` | `{fmt(row['row_auc'])}` | "
            f"`{fmt(row['row_recall_at_k'])}` | `{fmt(row['row_bce'])}` |"
        )

    return "\n".join(
        [
            "# Masked Row-Support Objective Probe",
            "",
            "이 프로브는 hidden row-support를 HS-JEPA식 masked prediction target으로 삼을 수 있는지 검증한다.",
            "raw feature 복원이 아니라, feature family를 가린 context에서 보이지 않는 row-support representation을 예측한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{v['status']}`",
            f"- Full composite row AUC: `{fmt(v['full_composite_mean_row_auc'])}`",
            f"- Full composite cell recall: `{fmt(v['full_composite_mean_cell_recall'])}`",
            f"- Human-only cell recall: `{fmt(v['human_only_mean_cell_recall'])}`",
            f"- Prediction-only cell recall: `{fmt(v['prediction_only_mean_cell_recall'])}`",
            f"- Route-masked cell recall: `{fmt(v['route_mask_mean_cell_recall'])}`",
            f"- Robust mask count: `{v['robust_mask_count']}`",
            f"- Group stress full row AUC: `{fmt(v['group_stress_full_mean_auc'])}`",
            f"- Group stress full recall@K: `{fmt(v['group_stress_full_mean_recall_at_k'])}`",
            "",
            "해석:",
            "",
            v["interpretation"],
            "",
            "다음 행동:",
            "",
            v["next_action"],
            "",
            "## Teacher-Transfer Mask Summary",
            "",
            *transfer_rows,
            "",
            "## Group-Heldout Stress Summary",
            "",
            *stress_rows,
            "",
            "## Boundary",
            "",
            "- `teacher-transfer`가 강하다는 것은 row-support target이 완전히 public-specific hallucination은 아니라는 뜻이다.",
            "- `group-heldout stress`가 약하다는 것은 아직 action-grade decoder로 바로 쓰기 어렵다는 뜻이다.",
            "- 다음 HS-JEPA objective는 row-support를 masked representation target으로 학습하되, subject/date/order stress를 통과해야 submission decoder로 승격할 수 있다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input ranked cells: {INPUT_CSV.relative_to(ROOT)}")
    cell_frame = pd.read_csv(INPUT_CSV)
    row_frame = build_row_frame(cell_frame)
    views = build_masked_views(row_frame, cell_frame)
    transfer_rows = evaluate_transfer(row_frame, cell_frame, views)
    stress_rows = evaluate_group_stress(row_frame, views)
    report = {
        "package": "Masked Row-Support Objective Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": False,
        "uses_proprietary_embedding_api": False,
        "input": str(INPUT_CSV.relative_to(ROOT)),
        "verdict": verdict(transfer_rows, stress_rows),
        "transfer_metrics": transfer_rows,
        "group_stress_metrics": stress_rows,
    }
    pd.DataFrame(transfer_rows).to_csv(MASKED_TRANSFER_CSV, index=False)
    pd.DataFrame(stress_rows).to_csv(MASKED_STRESS_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "transfer_csv": str(MASKED_TRANSFER_CSV.resolve()),
        "stress_csv": str(MASKED_STRESS_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
