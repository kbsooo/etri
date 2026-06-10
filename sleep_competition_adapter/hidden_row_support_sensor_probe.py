#!/usr/bin/env python3
"""Search for a transferable hidden row-support sensor.

The previous assignment-gap probe showed that row support, not target route, is
the large missing variable.  This probe asks the next question:

    If one public-sensitive teacher tells us which rows matter, can a row-level
    sensor learned from reusable context transfer to another teacher world?

This is not a submission builder.  It is a big-bet diagnostic for whether the
HS-JEPA core can grow from "human-state orientation" into a portable row-support
model.  Families that use only calendar/cohort/latent/base-landscape features
are treated as portable.  Families using listener artifacts are reported only as
adapter-side upper bounds.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import math
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

INPUT_CSV = OUT / "og_only_assignment_teacher_ranked_cells.csv"
REPORT_JSON = OUT / "hidden_row_support_sensor_probe.json"
REPORT_MD = OUT / "hidden_row_support_sensor_probe_ko.md"
TRANSFER_CSV = OUT / "hidden_row_support_sensor_transfer_metrics.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
OBJECTIVE_STAGE_PRIOR = {"S2": 1.0, "S4": 0.70, "S1": 0.50, "S3": 0.35, "Q1": 0.0, "Q2": 0.0, "Q3": 0.0}
SEED = 20260610
NULL_REPEATS = 128


def finite(frame: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col not in frame:
        return pd.Series(default, index=frame.index, dtype=np.float64)
    values = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    if values.notna().any():
        return values.fillna(float(values.median())).astype(np.float64)
    return pd.Series(default, index=frame.index, dtype=np.float64)


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    s = pd.Series(values).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if s.notna().any():
        s = s.fillna(float(s.median()))
    else:
        s = s.fillna(0.0)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def safe_auc(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return None
    x = np.asarray(score, dtype=np.float64)
    if np.nanstd(x) <= 0:
        return None
    return float(roc_auc_score(y, x))


def safe_ap(y_true: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y_true, dtype=int)
    if len(np.unique(y)) < 2:
        return None
    x = np.asarray(score, dtype=np.float64)
    if np.nanstd(x) <= 0:
        return None
    return float(average_precision_score(y, x))


def select_top_cells(frame: pd.DataFrame, score: np.ndarray, k: int, max_cells_per_row: int = 2) -> np.ndarray:
    work = frame[["row", "target_idx_int"]].copy()
    work["_score"] = np.asarray(score, dtype=np.float64)
    work["_score"] = work["_score"].replace([np.inf, -np.inf], np.nan)
    if work["_score"].notna().any():
        work["_score"] = work["_score"].fillna(float(work["_score"].median()))
    else:
        work["_score"] = 0.0
    work["_orig"] = np.arange(len(work))
    order = work.sort_values(
        ["_score", "row", "target_idx_int", "_orig"],
        ascending=[False, True, True, True],
        kind="mergesort",
    ).index
    selected = np.zeros(len(frame), dtype=bool)
    row_counts: dict[int, int] = {}
    for idx in order:
        row = int(frame.at[idx, "row"])
        if row_counts.get(row, 0) >= max_cells_per_row:
            continue
        selected[idx] = True
        row_counts[row] = row_counts.get(row, 0) + 1
        if int(selected.sum()) >= k:
            break
    return selected


def feature_families(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    latent_cols = [c for c in frame.columns if c.startswith("human_state_latent_")]
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
    return {
        "calendar_sequence_phase": {
            "type": "portable_human_context",
            "base_cols": ["row_frac", "dayofweek", "is_weekend", "dayofmonth", "month_start_proximity", "month_end"],
            "agg_cols": [],
            "interpretation": "Row/order/calendar rhythm as support sensor.",
        },
        "subject_peer_block": {
            "type": "portable_human_context",
            "base_cols": ["subject_code", "row_frac", "peer_group"],
            "agg_cols": [],
            "interpretation": "Subject-like block and peer membership as support sensor.",
        },
        "cohort_social_outlier": {
            "type": "portable_human_context",
            "base_cols": [
                "dist_to_subject_normal",
                "dist_to_peer_normal",
                "subject_minus_peer_dist",
                "subject_outlier_rank",
                "peer_outlier_rank",
                "cohort_outlier_score",
                "atlas_action_health",
                "peer_group",
                "dayofweek",
                "is_weekend",
                "month_end",
                "month_start_proximity",
            ],
            "agg_cols": [],
            "interpretation": "Personal/cohort anomaly and social-calendar state.",
        },
        "latent_geometry": {
            "type": "portable_human_context",
            "base_cols": latent_cols + ["personal_axis", "cohort_axis", "axis_disagreement", "peer_only_toxicity"],
            "agg_cols": [],
            "interpretation": "HS-JEPA human-state geometry without target labels.",
        },
        "prediction_landscape": {
            "type": "portable_prediction_context",
            "base_cols": [],
            "agg_cols": prediction_cols,
            "interpretation": "The row's seven-target probability/margin landscape, independent of public score labels.",
        },
        "portable_row_support_composite": {
            "type": "portable_composite_context",
            "base_cols": [
                "row_frac",
                "dayofweek",
                "is_weekend",
                "dayofmonth",
                "month_start_proximity",
                "month_end",
                "subject_code",
                "peer_group",
                "dist_to_subject_normal",
                "dist_to_peer_normal",
                "subject_minus_peer_dist",
                "subject_outlier_rank",
                "peer_outlier_rank",
                "cohort_outlier_score",
                "atlas_action_health",
                "personal_axis",
                "cohort_axis",
                "axis_disagreement",
                "peer_only_toxicity",
            ]
            + latent_cols,
            "agg_cols": prediction_cols,
            "interpretation": "All portable context currently available to the sleep adapter.",
        },
        "distilled_row_context_capacity": {
            "type": "teacher_distilled_capacity",
            "base_cols": [],
            "agg_cols": ["student_oof_row_prob", "oof_prob_human_row_context_only", "oof_move_human_row_context_only", "og_row_context_score"],
            "interpretation": "Teacher-distilled row context; capacity diagnostic, not deployment proof.",
        },
        "listener_adapter_upper_bound": {
            "type": "adapter_source_upper_bound",
            "base_cols": [],
            "agg_cols": ["listener_selection_score", "listener_responsibility_score", "selection_score", "responsibility_score"],
            "interpretation": "Adapter/listener artifacts; upper bound for row support.",
        },
    }


def add_phase_features(row_frame: pd.DataFrame) -> pd.DataFrame:
    out = row_frame.copy()
    for col, period in [("row_frac", 1.0), ("dayofweek", 7.0), ("dayofmonth", 31.0), ("subject_code", 32.0)]:
        if col not in out:
            continue
        vals = finite(out, col).to_numpy(dtype=np.float64)
        scale = 2.0 * math.pi * vals / period
        out[f"{col}_sin"] = np.sin(scale)
        out[f"{col}_cos"] = np.cos(scale)
    return out


def build_row_frame(cell_frame: pd.DataFrame) -> pd.DataFrame:
    families = feature_families(cell_frame)
    first_cols = sorted({col for fam in families.values() for col in fam["base_cols"] if col in cell_frame})
    agg_cols = sorted({col for fam in families.values() for col in fam["agg_cols"] if col in cell_frame})

    pieces: list[pd.DataFrame] = []
    for teacher, group in cell_frame.groupby("teacher", sort=True):
        y = group.groupby("row")["teacher_has_action"].max().astype(int)
        row_part = pd.DataFrame({"row": y.index.astype(int), "teacher_row_has_action": y.to_numpy(dtype=int)})
        for col in first_cols:
            row_part[col] = group.groupby("row")[col].first().reindex(y.index).to_numpy()
        agg_data: dict[str, np.ndarray] = {}
        for col in agg_cols:
            gb = group.groupby("row")[col]
            agg_data[f"{col}_mean"] = gb.mean().reindex(y.index).to_numpy()
            agg_data[f"{col}_max"] = gb.max().reindex(y.index).to_numpy()
            agg_data[f"{col}_min"] = gb.min().reindex(y.index).to_numpy()
            agg_data[f"{col}_std"] = gb.std().fillna(0.0).reindex(y.index).to_numpy()
            agg_data[f"{col}_range"] = (gb.max() - gb.min()).reindex(y.index).to_numpy()
        if agg_data:
            row_part = pd.concat([row_part, pd.DataFrame(agg_data)], axis=1)
        row_part["teacher"] = str(teacher)
        pieces.append(add_phase_features(row_part))
    return pd.concat(pieces, ignore_index=True)


def columns_for_family(row_frame: pd.DataFrame, family: dict[str, Any]) -> list[str]:
    cols: list[str] = []
    for col in family["base_cols"]:
        if col in row_frame:
            cols.append(col)
        for suffix in ["_sin", "_cos"]:
            phase_col = f"{col}{suffix}"
            if phase_col in row_frame:
                cols.append(phase_col)
    for col in family["agg_cols"]:
        for suffix in ["_mean", "_max", "_min", "_std", "_range"]:
            agg_col = f"{col}{suffix}"
            if agg_col in row_frame:
                cols.append(agg_col)
    return sorted(set(cols))


def clean_matrix(train: pd.DataFrame, test: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    x_train = train[cols].replace([np.inf, -np.inf], np.nan)
    med = x_train.median(numeric_only=True)
    x_train = x_train.fillna(med).fillna(0.0)
    x_test = test[cols].replace([np.inf, -np.inf], np.nan).fillna(med).fillna(0.0)
    return x_train, x_test


def fit_sensor(x_train: pd.DataFrame, y_train: np.ndarray) -> Any:
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.30, class_weight="balanced", max_iter=1000, solver="liblinear", random_state=SEED),
    )
    return model.fit(x_train, y_train)


def evaluate_transfer(
    row_frame: pd.DataFrame,
    cell_frame: pd.DataFrame,
    family_name: str,
    family: dict[str, Any],
    train_teacher: str,
    test_teacher: str,
) -> dict[str, Any] | None:
    cols = columns_for_family(row_frame, family)
    if not cols:
        return None
    train = row_frame.loc[row_frame["teacher"] == train_teacher].copy()
    test = row_frame.loc[row_frame["teacher"] == test_teacher].copy()
    y_train = train["teacher_row_has_action"].to_numpy(dtype=int)
    y_test = test["teacher_row_has_action"].to_numpy(dtype=int)
    if y_train.sum() == 0 or y_test.sum() == 0:
        return None
    x_train, x_test = clean_matrix(train, test, cols)
    model = fit_sensor(x_train, y_train)
    score = model.predict_proba(x_test)[:, 1]
    row_k = int(y_test.sum())
    top_idx = np.argsort(-score)[:row_k]
    row_overlap = int(y_test[top_idx].sum())

    row_score_map = dict(zip(test["row"].astype(int), score))
    test_cells = cell_frame.loc[cell_frame["teacher"] == test_teacher].reset_index(drop=True).copy()
    test_cells["_row_score"] = test_cells["row"].astype(int).map(row_score_map).fillna(0.0)
    stage_prior = test_cells["target"].map(OBJECTIVE_STAGE_PRIOR).fillna(0.0).to_numpy(dtype=np.float64)
    cell_score = 2.0 * rank01(test_cells["_row_score"]) + stage_prior
    teacher_cells = test_cells["teacher_has_action"].to_numpy(dtype=bool)
    selected = select_top_cells(test_cells, cell_score, int(teacher_cells.sum()), max_cells_per_row=2)
    cell_overlap = int((selected & teacher_cells).sum())
    selected_rows = set(test_cells.loc[selected, "row"].astype(int))
    true_rows = set(test_cells.loc[teacher_cells, "row"].astype(int))

    seed_key = f"{family_name}|{train_teacher}|{test_teacher}|{SEED}".encode("utf-8")
    seed = int.from_bytes(hashlib.sha1(seed_key).digest()[:4], "little", signed=False)
    null_rng = np.random.default_rng(seed)
    null_aucs: list[float] = []
    for _ in range(NULL_REPEATS):
        permuted = null_rng.permutation(y_train)
        null_model = fit_sensor(x_train, permuted)
        null_score = null_model.predict_proba(x_test)[:, 1]
        auc = safe_auc(y_test, null_score)
        if auc is not None:
            null_aucs.append(auc)
    null_mean = float(np.mean(null_aucs)) if null_aucs else None
    null_std = float(np.std(null_aucs, ddof=1)) if len(null_aucs) > 1 else None
    auc = safe_auc(y_test, score)
    auc_z = None
    if auc is not None and null_mean is not None and null_std is not None and null_std > 1e-12:
        auc_z = float((auc - null_mean) / null_std)

    return {
        "family": family_name,
        "family_type": family["type"],
        "train_teacher": train_teacher,
        "test_teacher": test_teacher,
        "feature_count": len(cols),
        "teacher_rows": row_k,
        "row_auc": auc,
        "row_average_precision": safe_ap(y_test, score),
        "row_recall_at_k": float(row_overlap / row_k) if row_k else 0.0,
        "row_precision_at_k": float(row_overlap / row_k) if row_k else 0.0,
        "cell_recall_with_stage_prior": float(cell_overlap / teacher_cells.sum()) if teacher_cells.sum() else 0.0,
        "cell_precision_with_stage_prior": float(cell_overlap / selected.sum()) if selected.any() else 0.0,
        "cell_row_recall_with_stage_prior": float(len(selected_rows & true_rows) / len(true_rows)) if true_rows else 0.0,
        "null_auc_mean": null_mean,
        "null_auc_std": null_std,
        "auc_z_vs_permuted_train": auc_z,
        "interpretation": family["interpretation"],
    }


def verdict(records: list[dict[str, Any]]) -> dict[str, Any]:
    portable = [
        row
        for row in records
        if row["family_type"] in {"portable_human_context", "portable_prediction_context", "portable_composite_context"}
    ]
    adapter = [row for row in records if row["family_type"] == "adapter_source_upper_bound"]
    best_portable = max(portable, key=lambda row: (row["cell_recall_with_stage_prior"], row["row_auc"] or 0.0))
    best_adapter = max(adapter, key=lambda row: (row["cell_recall_with_stage_prior"], row["row_auc"] or 0.0)) if adapter else None
    by_family = pd.DataFrame(portable).groupby("family").agg(
        row_auc=("row_auc", "mean"),
        row_recall_at_k=("row_recall_at_k", "mean"),
        cell_recall_with_stage_prior=("cell_recall_with_stage_prior", "mean"),
        auc_z_vs_permuted_train=("auc_z_vs_permuted_train", "mean"),
    )
    best_family_name = str(by_family["cell_recall_with_stage_prior"].idxmax())
    best_family = by_family.loc[best_family_name]
    adapter_gap = None
    if best_adapter is not None:
        adapter_gap = float(best_adapter["cell_recall_with_stage_prior"] - best_portable["cell_recall_with_stage_prior"])

    if float(best_family["row_auc"]) >= 0.70 and float(best_family["cell_recall_with_stage_prior"]) >= 0.22:
        status = "portable_row_support_sensor_alive_partial"
        next_action = "Promote prediction-landscape row support into a masked HS-JEPA row-support objective, then stress against subject/date splits."
    elif best_adapter is not None and adapter_gap is not None and adapter_gap >= 0.10:
        status = "adapter_row_support_upper_bound_only"
        next_action = "Look for a new non-public sensor; current portable context cannot match listener-side row support."
    else:
        status = "row_support_sensor_not_found"
        next_action = "Do not build a submission from current row sensors; redesign the human-state context."

    return {
        "status": status,
        "best_portable_family": best_family_name,
        "best_portable_mean_row_auc": float(best_family["row_auc"]),
        "best_portable_mean_row_recall_at_k": float(best_family["row_recall_at_k"]),
        "best_portable_mean_cell_recall_with_stage_prior": float(best_family["cell_recall_with_stage_prior"]),
        "best_portable_mean_auc_z_vs_permuted_train": float(best_family["auc_z_vs_permuted_train"]),
        "best_single_portable_family": best_portable["family"],
        "best_single_portable_test_teacher": best_portable["test_teacher"],
        "best_single_portable_cell_recall": best_portable["cell_recall_with_stage_prior"],
        "best_adapter_cell_recall": best_adapter["cell_recall_with_stage_prior"] if best_adapter is not None else None,
        "adapter_minus_portable_cell_recall_gap": adapter_gap,
        "next_action": next_action,
        "interpretation": (
            "A transferable row-support sensor exists, but it is partial: the seven-target prediction landscape transfers better than "
            "calendar/cohort-only state and turns the row-support bottleneck into a concrete HS-JEPA pretraining target."
            if status == "portable_row_support_sensor_alive_partial"
            else "Current reusable context does not yet recover row support strongly enough for a portable adapter."
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
    family_rows = [
        "| Family | Type | Mean row AUC | Mean row recall@K | Mean cell recall | Mean AUC z |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    family_df = pd.DataFrame(report["transfer_metrics"]).groupby(["family", "family_type"], as_index=False).agg(
        row_auc=("row_auc", "mean"),
        row_recall_at_k=("row_recall_at_k", "mean"),
        cell_recall_with_stage_prior=("cell_recall_with_stage_prior", "mean"),
        auc_z_vs_permuted_train=("auc_z_vs_permuted_train", "mean"),
    )
    family_df = family_df.sort_values(["cell_recall_with_stage_prior", "row_auc"], ascending=False)
    for item in family_df.to_dict("records"):
        family_rows.append(
            f"| `{item['family']}` | `{item['family_type']}` | `{fmt(item['row_auc'])}` | "
            f"`{fmt(item['row_recall_at_k'])}` | `{fmt(item['cell_recall_with_stage_prior'])}` | "
            f"`{fmt(item['auc_z_vs_permuted_train'])}` |"
        )

    transfer_rows = [
        "| Family | Train -> Test | Row AUC | Row recall@K | Cell recall | AUC z |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in sorted(report["transfer_metrics"], key=lambda row: (row["family"], row["test_teacher"])):
        transfer_rows.append(
            f"| `{item['family']}` | `{item['train_teacher']} -> {item['test_teacher']}` | "
            f"`{fmt(item['row_auc'])}` | `{fmt(item['row_recall_at_k'])}` | "
            f"`{fmt(item['cell_recall_with_stage_prior'])}` | `{fmt(item['auc_z_vs_permuted_train'])}` |"
        )

    return "\n".join(
        [
            "# Hidden Row-Support Sensor Probe",
            "",
            "이 프로브는 HS-JEPA의 다음 병목인 hidden row-support를 teacher-transfer 방식으로 찾는다.",
            "한 teacher 세계에서 row-support를 학습하고, 다른 teacher 세계에서 같은 row-support가 살아남는지 본다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{v['status']}`",
            f"- Best portable family: `{v['best_portable_family']}`",
            f"- Best portable mean row AUC: `{fmt(v['best_portable_mean_row_auc'])}`",
            f"- Best portable mean row recall@K: `{fmt(v['best_portable_mean_row_recall_at_k'])}`",
            f"- Best portable mean cell recall with stage prior: `{fmt(v['best_portable_mean_cell_recall_with_stage_prior'])}`",
            f"- Best portable mean AUC z vs permuted train: `{fmt(v['best_portable_mean_auc_z_vs_permuted_train'])}`",
            f"- Adapter minus portable cell-recall gap: `{fmt(v['adapter_minus_portable_cell_recall_gap'])}`",
            "",
            "해석:",
            "",
            v["interpretation"],
            "",
            "다음 행동:",
            "",
            v["next_action"],
            "",
            "## Family Summary",
            "",
            *family_rows,
            "",
            "## Teacher Transfer Metrics",
            "",
            *transfer_rows,
            "",
            "## Boundary",
            "",
            "- 이 프로브는 submission 후보가 아니라 row-support sensor가 이식 가능한지 보는 진단이다.",
            "- `prediction_landscape`는 public score ledger를 쓰지 않지만 기존 base prediction/margin 구조는 사용한다.",
            "- `listener_adapter_upper_bound`는 adapter-side source artifact를 쓰므로 HS-JEPA core portability 증거가 아니다.",
            "- 살아남은 신호는 target route가 아니라 row-level seven-target landscape이며, 다음 HS-JEPA objective는 이 row support를 masked prediction target으로 삼아야 한다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input ranked cells: {INPUT_CSV.relative_to(ROOT)}")
    cell_frame = pd.read_csv(INPUT_CSV)
    row_frame = build_row_frame(cell_frame)
    teachers = sorted(row_frame["teacher"].unique().tolist())
    families = feature_families(cell_frame)
    records: list[dict[str, Any]] = []
    for test_teacher in teachers:
        for train_teacher in teachers:
            if train_teacher == test_teacher:
                continue
            for family_name, family in families.items():
                rec = evaluate_transfer(row_frame, cell_frame, family_name, family, train_teacher, test_teacher)
                if rec is not None:
                    records.append(rec)

    report = {
        "package": "Hidden Row-Support Sensor Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": False,
        "uses_proprietary_embedding_api": False,
        "input": str(INPUT_CSV.relative_to(ROOT)),
        "null_repeats": NULL_REPEATS,
        "verdict": verdict(records),
        "transfer_metrics": records,
    }
    pd.DataFrame(records).to_csv(TRANSFER_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "transfer_csv": str(TRANSFER_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
