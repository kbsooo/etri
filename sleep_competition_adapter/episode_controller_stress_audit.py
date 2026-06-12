#!/usr/bin/env python3
"""Subject-LOO stress audit for HS-JEPA episode action-space controller.

The action-space restriction decoder produced the first strong positive
architecture evidence: row episode state improved OOF logloss when used as an
action-space controller, not as a feature.

This audit asks whether that result survives policy-selection stress:

    If we choose the action-space policy without seeing one subject, does the
    chosen controller still improve that held-out subject?

The audit uses the OOF action logs produced by
episode_action_space_restriction_decoder.py.  It does not use public LB,
submission probabilities, action teachers, or frontier files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.core_oof_action_health_benchmark import TARGETS  # noqa: E402


SRC = ROOT / "sleep_competition_adapter" / "outputs" / "episode_action_space_restriction_decoder"
OUT = ROOT / "sleep_competition_adapter" / "outputs" / "episode_controller_stress_audit"
OUT.mkdir(parents=True, exist_ok=True)


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    selected_path = SRC / "episode_action_space_selected_oof_cells.csv"
    gain_path = SRC / "episode_action_space_oof_gain_pairs.csv"
    metrics_path = SRC / "episode_action_space_policy_table.csv"
    readout_path = SRC / "episode_action_space_readout.json"
    missing = [p for p in [selected_path, gain_path, metrics_path, readout_path] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Run episode_action_space_restriction_decoder.py first; missing: {missing}")
    selected = pd.read_csv(selected_path)
    gain_pairs = pd.read_csv(gain_path)
    metrics = pd.read_csv(metrics_path)
    readout = json.loads(readout_path.read_text(encoding="utf-8"))
    return selected, gain_pairs, metrics, readout


def policy_id_cols() -> list[str]:
    return ["law_name", "action_space_policy", "selection_policy", "selection_param"]


def build_cell_baseline(gain_pairs: pd.DataFrame) -> pd.DataFrame:
    cols = ["cell_key", "subject_id", "target", "row", "raw_loss"]
    cells = gain_pairs[cols].drop_duplicates("cell_key").copy()
    if cells["cell_key"].duplicated().any():
        raise RuntimeError("cell baseline has duplicate cell_key")
    return cells


def policy_subject_table(selected: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    total_by_subject = cells.groupby("subject_id").agg(
        cells=("cell_key", "nunique"),
        raw_loss_sum=("raw_loss", "sum"),
    ).reset_index()
    action = selected.copy()
    action["policy_key"] = action[policy_id_cols()].astype(str).agg("||".join, axis=1)
    gains = action.groupby(policy_id_cols() + ["policy_key", "subject_id"]).agg(
        selected_cells=("cell_key", "nunique"),
        gain_sum=("true_gain", "sum"),
        mean_gain=("true_gain", "mean"),
        positive_gain_rate=("true_gain", lambda s: float((s > 0).mean())),
        episode_family_match_rate=("family_matches_row_episode", "mean"),
    ).reset_index()
    keys = action[policy_id_cols() + ["policy_key"]].drop_duplicates().copy()
    subjects = total_by_subject[["subject_id"]].drop_duplicates().copy()
    grid = keys.merge(subjects, how="cross")
    table = grid.merge(total_by_subject, on="subject_id", how="left").merge(
        gains,
        on=policy_id_cols() + ["policy_key", "subject_id"],
        how="left",
    )
    fill_zero = ["selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "episode_family_match_rate"]
    table[fill_zero] = table[fill_zero].fillna(0.0)
    table["logloss"] = (table["raw_loss_sum"] - table["gain_sum"]) / table["cells"]
    table["gain_per_cell"] = table["gain_sum"] / table["cells"]
    return table


def aggregate_policy(table: pd.DataFrame) -> pd.DataFrame:
    grouped = table.groupby(policy_id_cols() + ["policy_key"]).agg(
        cells=("cells", "sum"),
        raw_loss_sum=("raw_loss_sum", "sum"),
        gain_sum=("gain_sum", "sum"),
        selected_cells=("selected_cells", "sum"),
        positive_subjects=("gain_sum", lambda s: int((s > 0).sum())),
        negative_subjects=("gain_sum", lambda s: int((s < 0).sum())),
        mean_subject_gain_per_cell=("gain_per_cell", "mean"),
        std_subject_gain_per_cell=("gain_per_cell", "std"),
        min_subject_gain_per_cell=("gain_per_cell", "min"),
    ).reset_index()
    grouped["logloss"] = (grouped["raw_loss_sum"] - grouped["gain_sum"]) / grouped["cells"]
    grouped["gain_per_cell"] = grouped["gain_sum"] / grouped["cells"]
    grouped["subject_positive_rate"] = grouped["positive_subjects"] / (grouped["positive_subjects"] + grouped["negative_subjects"]).clip(lower=1)
    return grouped.sort_values("logloss", kind="mergesort").reset_index(drop=True)


def subject_loo_policy_selection(table: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    subjects = sorted(table["subject_id"].unique())
    rows = []
    for subject in subjects:
        train = table[~table["subject_id"].eq(subject)]
        valid = table[table["subject_id"].eq(subject)]
        train_agg = aggregate_policy(train)
        selected_policy = train_agg.iloc[0]
        mask = valid["policy_key"].eq(selected_policy["policy_key"])
        held = valid[mask].iloc[0]
        rows.append({
            "heldout_subject": subject,
            "selected_policy_key": selected_policy["policy_key"],
            "selected_law_name": selected_policy["law_name"],
            "selected_action_space_policy": selected_policy["action_space_policy"],
            "selected_selection_policy": selected_policy["selection_policy"],
            "selected_selection_param": float(selected_policy["selection_param"]),
            "train_logloss": float(selected_policy["logloss"]),
            "heldout_logloss": float(held["logloss"]),
            "heldout_raw_logloss": float(held["raw_loss_sum"] / held["cells"]),
            "heldout_gain_per_cell": float(held["gain_per_cell"]),
            "heldout_selected_cells": int(held["selected_cells"]),
            "heldout_positive": bool(held["gain_sum"] > 0),
        })
    frame = pd.DataFrame(rows)
    cells = table[["subject_id", "cells", "raw_loss_sum"]].drop_duplicates()
    raw_total = float(cells["raw_loss_sum"].sum() / cells["cells"].sum())
    selected_total_loss = 0.0
    selected_total_cells = 0
    for rec in frame.to_dict("records"):
        subj_cells = cells[cells["subject_id"].eq(rec["heldout_subject"])]["cells"].iloc[0]
        selected_total_loss += float(rec["heldout_logloss"]) * float(subj_cells)
        selected_total_cells += int(subj_cells)
    meta = {
        "subject_loo_logloss": selected_total_loss / selected_total_cells,
        "raw_oof_logloss_from_cells": raw_total,
        "subject_loo_delta_vs_raw": selected_total_loss / selected_total_cells - raw_total,
        "subject_loo_positive_subject_rate": float(frame["heldout_positive"].mean()),
        "selected_policy_counts": frame["selected_policy_key"].value_counts().to_dict(),
    }
    return frame, meta


def markdown_table(frame: pd.DataFrame, max_rows: int = 16) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        values = []
        for col in cols:
            value = rec[col]
            values.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], policy_agg: pd.DataFrame, loo: pd.DataFrame) -> str:
    top_cols = [
        "law_name",
        "action_space_policy",
        "selection_policy",
        "selection_param",
        "logloss",
        "gain_per_cell",
        "selected_cells",
        "positive_subjects",
        "negative_subjects",
        "min_subject_gain_per_cell",
    ]
    loo_cols = [
        "heldout_subject",
        "selected_action_space_policy",
        "heldout_logloss",
        "heldout_raw_logloss",
        "heldout_gain_per_cell",
        "heldout_selected_cells",
        "heldout_positive",
    ]
    return "\n".join([
        "# Episode Controller Stress Audit",
        "",
        "## 한 줄 요약",
        "",
        "episode action-space controller가 전체 OOF policy selection artifact인지 subject-LOO로 검증했다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py",
        "python3 sleep_competition_adapter/episode_controller_stress_audit.py",
        "```",
        "",
        "public LB, prior submission probability, action teacher, frontier file은 사용하지 않는다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw OOF logloss from cells: `{readout['raw_oof_logloss_from_cells']:.6f}`",
        f"- full best policy logloss: `{readout['full_best_policy_logloss']:.6f}`",
        f"- subject-LOO selected-policy logloss: `{readout['subject_loo_logloss']:.6f}`",
        f"- subject-LOO delta vs raw: `{readout['subject_loo_delta_vs_raw']:.6f}`",
        f"- subject-LOO positive subject rate: `{readout['subject_loo_positive_subject_rate']:.6f}`",
        f"- most selected policy: `{readout['most_selected_policy']}`",
        f"- verdict: `{readout['verdict']}`",
        "",
        "## Top Full-OOF Policies",
        "",
        markdown_table(policy_agg[top_cols], max_rows=16),
        "",
        "## Subject-LOO Decisions",
        "",
        markdown_table(loo[loo_cols], max_rows=20),
        "",
        "## 논문용 해석",
        "",
        "이 audit는 controller 자체를 다시 학습하지 않는다. 이미 OOF로 저장된 action logs만 사용해, policy selection 단계가 held-out subject label에 의존했는지 본다.",
        "",
        "subject-LOO에서도 raw보다 낮은 logloss를 유지하면, episode controller는 단일 OOF grid artifact가 아니라 subject-general action-space restriction이라는 증거가 된다.",
        "반대로 subject-LOO에서 무너지면, 0.62977은 full OOF에서 정책을 고른 선택 편향일 가능성이 크다.",
    ])


def run() -> dict[str, Any]:
    selected, gain_pairs, metrics, source_readout = load_inputs()
    cells = build_cell_baseline(gain_pairs)
    table = policy_subject_table(selected, cells)
    policy_agg = aggregate_policy(table)
    loo, loo_meta = subject_loo_policy_selection(table)
    full_best = policy_agg.iloc[0].to_dict()
    most_selected_policy = max(loo_meta["selected_policy_counts"].items(), key=lambda kv: kv[1])[0]
    if loo_meta["subject_loo_delta_vs_raw"] < -0.003:
        verdict = "strong_subject_general_controller"
    elif loo_meta["subject_loo_delta_vs_raw"] < 0:
        verdict = "weak_but_positive_subject_general_controller"
    else:
        verdict = "policy_selection_artifact_risk"
    readout = {
        "package": "episode_controller_stress_audit",
        "status": "subject_loo_policy_stress_complete",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "source_candidate_file": source_readout.get("candidate_file", ""),
        "source_best_restricted_oof_logloss": float(source_readout["best_restricted_oof_logloss"]),
        "raw_oof_logloss_from_cells": float(loo_meta["raw_oof_logloss_from_cells"]),
        "full_best_policy_key": str(full_best["policy_key"]),
        "full_best_policy_logloss": float(full_best["logloss"]),
        "full_best_policy_gain_per_cell": float(full_best["gain_per_cell"]),
        "subject_loo_logloss": float(loo_meta["subject_loo_logloss"]),
        "subject_loo_delta_vs_raw": float(loo_meta["subject_loo_delta_vs_raw"]),
        "subject_loo_positive_subject_rate": float(loo_meta["subject_loo_positive_subject_rate"]),
        "selected_policy_counts": loo_meta["selected_policy_counts"],
        "most_selected_policy": most_selected_policy,
        "verdict": verdict,
    }
    table.to_csv(OUT / "episode_controller_subject_policy_table.csv", index=False)
    policy_agg.to_csv(OUT / "episode_controller_policy_aggregate.csv", index=False)
    loo.to_csv(OUT / "episode_controller_subject_loo_decisions.csv", index=False)
    (OUT / "episode_controller_stress_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, policy_agg, loo)
    (OUT / "EPISODE_CONTROLLER_STRESS_AUDIT_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "EPISODE_CONTROLLER_STRESS_AUDIT_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
