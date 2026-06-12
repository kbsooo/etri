#!/usr/bin/env python3
"""Score-free HS-JEPA action-health separation probe.

The health score in this file is computed without public LB values. Public
outcomes are read only after scoring, as a retrospective diagnostic.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "action_health_separation_probe"
LEDGER_PATH = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"
FEATURE_PATH = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_human_state_features.csv"
LABEL_PATH = ROOT / "data" / "ch2026_metrics_train.csv"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
BASE_STAGE_FILE = ROOT / "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
CURRENT_FRONTIER_FILE = ROOT / "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv"
BIGBET_FILE = ROOT / "submission_hsjepa_core_geometry_outlier_route_bigbet_ef001c23_uploadsafe.csv"
BIGBET_AUDIT = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "core_geometry_outlier_route_adapter"
    / "core_geometry_outlier_route_action_audit.csv"
)
CORE_SUPPORT = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "core_geometry_outlier_route_adapter"
    / "core_geometry_row_support.csv"
)
TARGET_LAWS = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "core_geometry_outlier_route_adapter"
    / "train_outlier_target_laws.csv"
)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
REFERENCE_STAGE_FILES = {
    "public_equation_jump": "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
    "frontier_active_silence": "submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv",
    "row_state_vector_frontier": "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
    "dual_head_toxicity_stress": "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
    "target_split_xor_stress": "submission_h144_targetxor_def80b88_uploadsafe.csv",
    "q3_repair_only_stress": "submission_h145_q3repair_2d818e46_uploadsafe.csv",
    "cross_listener_transport_stress": "submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv",
    "target_route_teacher_only": "submission_hsjepa_target_route_toxicity_teacher_only_66f1f5b4_uploadsafe.csv",
    "target_route_q2_extra": "submission_hsjepa_target_route_toxicity_q2_extra_90b62d2d_uploadsafe.csv",
    "public_private_toxicity": "submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv",
    "core_geometry_outlier_route_bigbet": "submission_hsjepa_core_geometry_outlier_route_bigbet_ef001c23_uploadsafe.csv",
}


def logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), 1e-6, 1 - 1e-6)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-values))


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    series = pd.Series(values, dtype="float64")
    if series.notna().sum() <= 1:
        return np.full(len(series), 0.5, dtype=float)
    return series.rank(method="average", pct=True).fillna(0.5).to_numpy(dtype=float)


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def find_file(filename: str) -> Path | None:
    direct = ROOT / filename
    if direct.exists():
        return direct
    matches = list(ROOT.glob(f"**/{filename}"))
    return matches[0] if matches else None


def load_submission(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = [col for col in TARGETS if col not in frame.columns]
    if missing:
        raise ValueError(f"{path} is missing target columns: {missing}")
    return frame


def route_energy_model(train_labels: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    y = train_labels[TARGETS].astype(float).to_numpy()
    mean = y.mean(axis=0)
    cov = np.cov(y, rowvar=False)
    cov += np.eye(cov.shape[0]) * 0.02
    inv_cov = np.linalg.pinv(cov)
    return mean, inv_cov


def route_energy(prob: np.ndarray, mean: np.ndarray, inv_cov: np.ndarray) -> np.ndarray:
    centered = prob - mean.reshape(1, -1)
    energy = np.einsum("ij,jk,ik->i", centered, inv_cov, centered)
    return np.sqrt(np.maximum(energy, 0.0))


def load_core_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = pd.read_csv(FEATURE_PATH)
    test = features[features["split"].eq("test")].copy().reset_index(drop=True)
    support = pd.read_csv(CORE_SUPPORT)
    laws = pd.read_csv(TARGET_LAWS)
    labels = pd.read_csv(LABEL_PATH)
    return test, support, laws, labels


def cell_alignment(delta_logit: np.ndarray, test: pd.DataFrame, support: pd.DataFrame, laws: pd.DataFrame) -> pd.DataFrame:
    rows = []
    law_map = laws.set_index("target").to_dict("index")
    support_rank = support["core_support_rank"].to_numpy(dtype=float)
    for row_idx in range(delta_logit.shape[0]):
        for target_idx, target in enumerate(TARGETS):
            delta = float(delta_logit[row_idx, target_idx])
            if abs(delta) <= 1e-6:
                continue
            law = law_map[target]
            score_col = str(law["score"])
            score_rank = float(rank01(test[score_col])[row_idx])
            law_direction = 1 if float(law["shift"]) >= 0 else -1
            sign = 1 if delta >= 0 else -1
            rows.append(
                {
                    "row": row_idx,
                    "target": target,
                    "target_idx": target_idx,
                    "delta_logit": delta,
                    "abs_delta_logit": abs(delta),
                    "core_support_rank": float(support_rank[row_idx]),
                    "outlier_score": score_col,
                    "row_outlier_rank": score_rank,
                    "target_law_shift": float(law["shift"]),
                    "target_law_abs_shift": float(law["abs_shift"]),
                    "law_alignment": float(sign * law_direction),
                    "weighted_law_alignment": float(sign * law_direction * score_rank * min(1.0, float(law["abs_shift"]) / 0.16)),
                }
            )
    return pd.DataFrame(rows)


def summarize_action_field(
    name: str,
    filename: str,
    base: pd.DataFrame,
    candidate: pd.DataFrame,
    test: pd.DataFrame,
    support: pd.DataFrame,
    laws: pd.DataFrame,
    route_mean: np.ndarray,
    route_inv_cov: np.ndarray,
) -> dict[str, Any]:
    base_prob = base[TARGETS].to_numpy(dtype=float)
    cand_prob = candidate[TARGETS].to_numpy(dtype=float)
    delta = logit(cand_prob) - logit(base_prob)
    cells = cell_alignment(delta, test, support, laws)
    base_energy = route_energy(base_prob, route_mean, route_inv_cov)
    cand_energy = route_energy(cand_prob, route_mean, route_inv_cov)
    if cells.empty:
        return {
            "semantic_name": name,
            "file": filename,
            "available": True,
            "changed_cells": 0,
            "changed_rows": 0,
            "mean_abs_logit_delta": 0.0,
            "p95_abs_logit_delta": 0.0,
            "max_abs_logit_delta": 0.0,
            "mean_core_support_rank": 0.0,
            "mean_weighted_law_alignment": 0.0,
            "positive_law_alignment_rate": 0.0,
            "route_energy_delta": float(cand_energy.mean() - base_energy.mean()),
            "p95_route_energy_delta": float(np.quantile(cand_energy - base_energy, 0.95)),
        }
    rows_changed = cells["row"].nunique()
    return {
        "semantic_name": name,
        "file": filename,
        "available": True,
        "changed_cells": int(len(cells)),
        "changed_rows": int(rows_changed),
        "mean_abs_logit_delta": float(cells["abs_delta_logit"].mean()),
        "p95_abs_logit_delta": float(cells["abs_delta_logit"].quantile(0.95)),
        "max_abs_logit_delta": float(cells["abs_delta_logit"].max()),
        "mean_core_support_rank": float(cells["core_support_rank"].mean()),
        "mean_weighted_law_alignment": float(cells["weighted_law_alignment"].mean()),
        "positive_law_alignment_rate": float((cells["law_alignment"] > 0).mean()),
        "route_energy_delta": float(cand_energy.mean() - base_energy.mean()),
        "p95_route_energy_delta": float(np.quantile(cand_energy - base_energy, 0.95)),
        "Q_changed_cells": int(cells[cells["target"].str.startswith("Q")].shape[0]),
        "S_changed_cells": int(cells[cells["target"].str.startswith("S")].shape[0]),
    }


def add_health_score(summary: pd.DataFrame) -> pd.DataFrame:
    out = summary.copy()
    out["support_score"] = out["mean_core_support_rank"].fillna(0.0)
    out["law_score"] = (out["mean_weighted_law_alignment"].fillna(0.0) + 1.0) / 2.0
    out["route_safety_score"] = rank01(-out["route_energy_delta"].fillna(0.0))
    out["spread_safety_score"] = rank01(-out["changed_cells"].fillna(0.0))
    out["amplitude_safety_score"] = rank01(-out["p95_abs_logit_delta"].fillna(0.0))
    out["hsjepa_action_health_score"] = (
        0.30 * out["support_score"]
        + 0.30 * out["law_score"]
        + 0.20 * out["route_safety_score"]
        + 0.10 * out["spread_safety_score"]
        + 0.10 * out["amplitude_safety_score"]
    )
    return out.sort_values("hsjepa_action_health_score", ascending=False).reset_index(drop=True)


def attach_public_outcomes(summary: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    ledger = pd.read_csv(LEDGER_PATH)
    public_map = ledger.set_index("file")["public_lb"].to_dict()
    stage_map = ledger.set_index("file")["semantic_stage"].to_dict()
    out = summary.copy()
    out["public_lb"] = out["file"].map(public_map)
    out["semantic_stage"] = out["file"].map(stage_map)
    scored = out[out["public_lb"].notna()].copy()
    eval_report: dict[str, Any] = {
        "uses_public_score_for_health_features": False,
        "uses_public_score_for_retrospective_evaluation": True,
        "scored_candidate_count": int(len(scored)),
    }
    if len(scored) >= 3:
        corr = spearmanr(scored["hsjepa_action_health_score"], -scored["public_lb"])
        eval_report["spearman_health_vs_negative_public_lb"] = float(corr.correlation)
        eval_report["spearman_pvalue"] = float(corr.pvalue) if not math.isnan(corr.pvalue) else None
        nonzero = scored[scored["changed_cells"] > 0].copy()
        eval_report["nonzero_action_scored_candidate_count"] = int(len(nonzero))
        if len(nonzero) >= 3:
            nonzero_corr = spearmanr(nonzero["hsjepa_action_health_score"], -nonzero["public_lb"])
            eval_report["nonzero_spearman_health_vs_negative_public_lb"] = float(nonzero_corr.correlation)
            eval_report["nonzero_spearman_pvalue"] = (
                float(nonzero_corr.pvalue) if not math.isnan(nonzero_corr.pvalue) else None
            )
        scored["public_success_binary"] = scored["public_lb"] <= 0.56795
        pos = scored[scored["public_success_binary"]]
        neg = scored[~scored["public_success_binary"]]
        eval_report["mean_health_public_success"] = float(pos["hsjepa_action_health_score"].mean()) if len(pos) else None
        eval_report["mean_health_public_failure"] = float(neg["hsjepa_action_health_score"].mean()) if len(neg) else None
        eval_report["success_threshold_public_lb"] = 0.56795
    return out, eval_report


def build_health_gated_candidate(test: pd.DataFrame, support: pd.DataFrame, laws: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    frontier = load_submission(CURRENT_FRONTIER_FILE)
    bigbet = load_submission(BIGBET_FILE)
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    delta = logit(bigbet[TARGETS].to_numpy(dtype=float)) - logit(frontier[TARGETS].to_numpy(dtype=float))
    cells = cell_alignment(delta, test, support, laws)
    if cells.empty:
        raise ValueError("bigbet action field has no changed cells")
    cells["cell_action_health"] = (
        0.42 * cells["core_support_rank"]
        + 0.30 * ((cells["weighted_law_alignment"] + 1.0) / 2.0)
        + 0.18 * cells["row_outlier_rank"]
        + 0.10 * rank01(-cells["abs_delta_logit"])
    )
    # Keep a broad release, but remove the bottom tail that lacks core/law support.
    keep_threshold = float(cells["cell_action_health"].quantile(0.42))
    cells["released"] = cells["cell_action_health"] >= keep_threshold
    logits = logit(frontier[TARGETS].to_numpy(dtype=float))
    for _, row in cells[cells["released"]].iterrows():
        logits[int(row["row"]), int(row["target_idx"])] += float(row["delta_logit"])
    out = sample.copy()
    out[TARGETS] = np.clip(sigmoid(logits), 1e-5, 1 - 1e-5)
    file_hash = short_hash(out)
    filename = f"submission_hsjepa_action_health_separation_core_route_release_{file_hash}_uploadsafe.csv"
    return out, cells, filename


def markdown_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    if frame.empty:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.loc[:, columns].head(max_rows).iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_markdown(summary: pd.DataFrame, eval_report: dict[str, Any], candidate_filename: str, cell_audit: pd.DataFrame) -> str:
    return f"""# Action-Health Separation Probe

## 목적

이 실험은 HS-JEPA core representation이 action decoder의 독성을 public score 없이 줄일 수 있는지 본다.

Health score 계산에는 public LB를 쓰지 않는다. Public LB는 마지막 retrospective evaluation에만 쓴다.

## Health Score 구성

- core support: core-state geometry가 해당 row를 action-support row로 보는가
- outlier-law alignment: action 방향이 train에서 관측된 personal/cohort outlier target law와 맞는가
- route safety: train target manifold에서 멀어지는가
- spread/amplitude safety: 너무 넓고 큰 action field인가

## Retrospective 결과

- public score used for health features: `{eval_report["uses_public_score_for_health_features"]}`
- public score used for retrospective evaluation: `{eval_report["uses_public_score_for_retrospective_evaluation"]}`
- scored candidate count: `{eval_report["scored_candidate_count"]}`
- Spearman health vs -public_lb: `{eval_report.get("spearman_health_vs_negative_public_lb")}`
- nonzero-action scored candidate count: `{eval_report.get("nonzero_action_scored_candidate_count")}`
- nonzero-action Spearman health vs -public_lb: `{eval_report.get("nonzero_spearman_health_vs_negative_public_lb")}`
- success mean health: `{eval_report.get("mean_health_public_success")}`
- failure mean health: `{eval_report.get("mean_health_public_failure")}`

## Action Field Ranking

{markdown_table(summary, ["semantic_name", "public_lb", "hsjepa_action_health_score", "changed_cells", "changed_rows", "mean_core_support_rank", "mean_weighted_law_alignment", "route_energy_delta"], max_rows=20)}

## 생성된 후보

- `{candidate_filename}`

이 후보는 `core_geometry_outlier_route_bigbet`의 broad action field를 그대로 믿지 않고, cell-level action-health 하위 tail을 제거한 release다.

핵심 수치:

- input bigbet cells: `{len(cell_audit)}`
- released cells: `{int(cell_audit["released"].sum())}`
- released rows: `{int(cell_audit[cell_audit["released"]]["row"].nunique())}`
- release threshold: `{float(cell_audit["cell_action_health"].quantile(0.42)):.6f}`

## 해석

좋아지면 HS-JEPA core representation이 실제로 action decoder 독성을 줄인다는 강한 증거다.

나빠지면 현재 core-state geometry는 row support를 찾는 데는 강하지만, cell-level release health를 단독으로 결정하기에는 아직 부족하다는 뜻이다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    test, support, laws, labels = load_core_context()
    route_mean, route_inv_cov = route_energy_model(labels)
    base = load_submission(BASE_STAGE_FILE)

    rows = []
    for semantic_name, filename in REFERENCE_STAGE_FILES.items():
        path = find_file(filename)
        if path is None:
            rows.append({"semantic_name": semantic_name, "file": filename, "available": False})
            continue
        candidate = load_submission(path)
        rows.append(
            summarize_action_field(
                semantic_name,
                filename,
                base,
                candidate,
                test,
                support,
                laws,
                route_mean,
                route_inv_cov,
            )
        )
    summary = add_health_score(pd.DataFrame(rows))
    summary, eval_report = attach_public_outcomes(summary)

    candidate, cell_audit, candidate_filename = build_health_gated_candidate(test, support, laws)
    candidate.to_csv(OUT_DIR / candidate_filename, index=False)
    candidate.to_csv(ROOT / candidate_filename, index=False)
    cell_audit.to_csv(OUT_DIR / "cell_action_health_audit.csv", index=False)
    summary.to_csv(OUT_DIR / "action_field_health_ranking.csv", index=False)

    readout = {
        "package": "action_health_separation_probe",
        "status": "probe_ready",
        "uses_public_score_for_health_features": False,
        "uses_public_score_for_retrospective_evaluation": True,
        "base_stage_file": str(BASE_STAGE_FILE.relative_to(ROOT)),
        "candidate_file": candidate_filename,
        "root_candidate_file": candidate_filename,
        "eval": eval_report,
        "candidate": {
            "input_bigbet_cells": int(len(cell_audit)),
            "released_cells": int(cell_audit["released"].sum()),
            "released_rows": int(cell_audit[cell_audit["released"]]["row"].nunique()),
            "mean_released_cell_health": float(cell_audit[cell_audit["released"]]["cell_action_health"].mean()),
            "mean_dropped_cell_health": float(cell_audit[~cell_audit["released"]]["cell_action_health"].mean()),
        },
        "interpretation": (
            "A score-free HS-JEPA action-health score is useful only if it ranks known "
            "safe/stress action fields coherently and the gated core-route release improves."
        ),
    }
    (OUT_DIR / "action_health_separation_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False)
    )
    (OUT_DIR / "ACTION_HEALTH_SEPARATION_PROBE_KO.md").write_text(
        build_markdown(summary, eval_report, candidate_filename, cell_audit)
    )
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
