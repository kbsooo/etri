#!/usr/bin/env python3
"""Subject-invariant episode controller for HS-JEPA.

The episode action-space restriction decoder found a strong full-OOF signal, but
the stress audit showed that selecting the best policy by full OOF can collapse
onto a few subjects.  This experiment changes the selector, not the encoder:

    choose an episode action-space policy only if its gains survive a
    subject-invariant objective.

This keeps the experiment anchored in the HS-JEPA architecture claim.  The row
episode state is still a controller over row-target actions, but the release
policy must pass a representation-health constraint: it cannot be explained only
by one subject's lucky action tail.
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

from sleep_competition_adapter.core_oof_action_health_benchmark import (  # noqa: E402
    TARGETS,
    load_world,
    raw_feature_cols,
    short_hash,
    validate_submission,
)
from sleep_competition_adapter.contextual_listener_route_selector import build_temporal_oof_frames  # noqa: E402
from sleep_competition_adapter.episode_action_space_restriction_decoder import (  # noqa: E402
    SCORE_SPECS,
    action_space_policies,
    attach_episode_features,
    build_oof_episode_state,
    episode_thresholds,
    train_final_submission,
)
from sleep_competition_adapter.episode_controller_stress_audit import (  # noqa: E402
    build_cell_baseline,
    load_inputs,
    policy_id_cols,
    policy_subject_table,
)
from sleep_competition_adapter.failure_boundary_law_distillation import (  # noqa: E402
    add_law_features,
    feature_views as law_feature_views,
)
from sleep_competition_adapter.raw_knn_failure_detector import prepare_gain_pairs  # noqa: E402


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "subject_invariant_episode_controller"
OUT.mkdir(parents=True, exist_ok=True)

OBJECTIVES = {
    "full_oof_gain": {
        "std_penalty": 0.0,
        "negative_active_penalty": 0.0,
        "sparsity_penalty": 0.0,
        "coverage_bonus": 0.0,
        "require_active_subjects": 1,
        "require_no_negative_active": False,
    },
    "active_subject_balanced": {
        "std_penalty": 0.22,
        "negative_active_penalty": 0.0012,
        "sparsity_penalty": 0.0010,
        "coverage_bonus": 0.0015,
        "require_active_subjects": 2,
        "require_no_negative_active": False,
    },
    "negative_veto_balanced": {
        "std_penalty": 0.12,
        "negative_active_penalty": 0.0035,
        "sparsity_penalty": 0.0006,
        "coverage_bonus": 0.0008,
        "require_active_subjects": 1,
        "require_no_negative_active": True,
    },
    "coverage_first_controller": {
        "std_penalty": 0.10,
        "negative_active_penalty": 0.0014,
        "sparsity_penalty": 0.0004,
        "coverage_bonus": 0.0030,
        "require_active_subjects": 3,
        "require_no_negative_active": False,
    },
    "minimax_active_gain": {
        "std_penalty": 0.06,
        "negative_active_penalty": 0.0020,
        "sparsity_penalty": 0.0004,
        "coverage_bonus": 0.0010,
        "require_active_subjects": 2,
        "require_no_negative_active": False,
        "minimax_weight": 0.45,
    },
}


def aggregate_with_health(table: pd.DataFrame) -> pd.DataFrame:
    """Aggregate policy-by-subject rows into controller-health metrics."""
    id_cols = policy_id_cols() + ["policy_key"]
    rows = []
    for key, group in table.groupby(id_cols, sort=False):
        rec = dict(zip(id_cols, key))
        active = group[group["selected_cells"].gt(0)].copy()
        raw_loss_sum = float(group[["subject_id", "raw_loss_sum"]].drop_duplicates()["raw_loss_sum"].sum())
        cells = int(group[["subject_id", "cells"]].drop_duplicates()["cells"].sum())
        gain_sum = float(group["gain_sum"].sum())
        active_subjects = int(active["subject_id"].nunique())
        negative_active_subjects = int((active["gain_sum"] < 0).sum())
        positive_active_subjects = int((active["gain_sum"] > 0).sum())
        no_action_subjects = int(group["subject_id"].nunique() - active_subjects)
        active_gain_per_cell = active["gain_per_cell"] if active_subjects else pd.Series(dtype=float)
        rec.update({
            "cells": cells,
            "raw_loss_sum": raw_loss_sum,
            "gain_sum": gain_sum,
            "selected_cells": int(group["selected_cells"].sum()),
            "logloss": (raw_loss_sum - gain_sum) / cells,
            "gain_per_cell": gain_sum / cells,
            "subject_count": int(group["subject_id"].nunique()),
            "active_subjects": active_subjects,
            "positive_active_subjects": positive_active_subjects,
            "negative_active_subjects": negative_active_subjects,
            "no_action_subjects": no_action_subjects,
            "active_subject_rate": active_subjects / max(1, int(group["subject_id"].nunique())),
            "no_action_subject_rate": no_action_subjects / max(1, int(group["subject_id"].nunique())),
            "positive_active_subject_rate": positive_active_subjects / max(1, active_subjects),
            "negative_active_subject_rate": negative_active_subjects / max(1, active_subjects),
            "mean_subject_gain_per_cell": float(group["gain_per_cell"].mean()),
            "std_subject_gain_per_cell": float(group["gain_per_cell"].std(ddof=0)),
            "min_subject_gain_per_cell": float(group["gain_per_cell"].min()),
            "mean_active_gain_per_cell": float(active_gain_per_cell.mean()) if active_subjects else 0.0,
            "min_active_gain_per_cell": float(active_gain_per_cell.min()) if active_subjects else 0.0,
        })
        rows.append(rec)
    return pd.DataFrame(rows)


def score_objective(agg: pd.DataFrame, objective_name: str) -> pd.Series:
    cfg = OBJECTIVES[objective_name]
    score = (
        agg["gain_per_cell"].astype(float)
        - float(cfg["std_penalty"]) * agg["std_subject_gain_per_cell"].astype(float)
        - float(cfg["negative_active_penalty"]) * agg["negative_active_subjects"].astype(float)
        - float(cfg["sparsity_penalty"]) * agg["no_action_subject_rate"].astype(float)
        + float(cfg["coverage_bonus"]) * agg["active_subject_rate"].astype(float)
    )
    if "minimax_weight" in cfg:
        score = score + float(cfg["minimax_weight"]) * agg["min_active_gain_per_cell"].astype(float)
    valid = agg["active_subjects"].ge(int(cfg["require_active_subjects"]))
    if bool(cfg.get("require_no_negative_active", False)):
        valid &= agg["negative_active_subjects"].eq(0)
    return score.where(valid, -np.inf)


def objective_table(table: pd.DataFrame) -> pd.DataFrame:
    agg = aggregate_with_health(table)
    frames = []
    for objective_name in OBJECTIVES:
        scored = agg.copy()
        scored["objective_name"] = objective_name
        scored["objective_score"] = score_objective(scored, objective_name)
        scored = scored.sort_values(["objective_score", "gain_per_cell"], ascending=[False, False], kind="mergesort")
        scored["objective_rank"] = np.arange(1, len(scored) + 1)
        frames.append(scored)
    return pd.concat(frames, ignore_index=True)


def select_policy(train_table: pd.DataFrame, objective_name: str) -> pd.Series:
    scored = objective_table(train_table)
    best = scored[scored["objective_name"].eq(objective_name)].iloc[0]
    if not np.isfinite(float(best["objective_score"])):
        fallback = scored[scored["objective_name"].eq("full_oof_gain")].iloc[0]
        return fallback
    return best


def subject_loo_by_objective(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    subject_cells = table[["subject_id", "cells", "raw_loss_sum"]].drop_duplicates()
    total_cells = int(subject_cells["cells"].sum())
    raw_logloss = float(subject_cells["raw_loss_sum"].sum() / total_cells)
    decisions = []
    summaries = []
    for objective_name in OBJECTIVES:
        selected_total_loss = 0.0
        selected_total_cells = 0
        objective_decisions = []
        for subject in sorted(table["subject_id"].unique()):
            train = table[~table["subject_id"].eq(subject)]
            valid = table[table["subject_id"].eq(subject)]
            chosen = select_policy(train, objective_name)
            held = valid[valid["policy_key"].eq(chosen["policy_key"])].iloc[0]
            subj_cells = int(held["cells"])
            selected_total_loss += float(held["logloss"]) * subj_cells
            selected_total_cells += subj_cells
            rec = {
                "objective_name": objective_name,
                "heldout_subject": subject,
                "selected_policy_key": str(chosen["policy_key"]),
                "selected_law_name": str(chosen["law_name"]),
                "selected_action_space_policy": str(chosen["action_space_policy"]),
                "selected_selection_policy": str(chosen["selection_policy"]),
                "selected_selection_param": float(chosen["selection_param"]),
                "train_objective_score": float(chosen["objective_score"]),
                "train_gain_per_cell": float(chosen["gain_per_cell"]),
                "train_active_subjects": int(chosen["active_subjects"]),
                "train_negative_active_subjects": int(chosen["negative_active_subjects"]),
                "heldout_logloss": float(held["logloss"]),
                "heldout_raw_logloss": float(held["raw_loss_sum"] / held["cells"]),
                "heldout_gain_per_cell": float(held["gain_per_cell"]),
                "heldout_selected_cells": int(held["selected_cells"]),
                "heldout_active": bool(held["selected_cells"] > 0),
                "heldout_positive": bool(held["gain_sum"] > 0),
                "heldout_negative": bool(held["gain_sum"] < 0),
            }
            decisions.append(rec)
            objective_decisions.append(rec)
        loo_logloss = selected_total_loss / selected_total_cells
        frame = pd.DataFrame(objective_decisions)
        summaries.append({
            "objective_name": objective_name,
            "subject_loo_logloss": loo_logloss,
            "raw_logloss": raw_logloss,
            "delta_vs_raw": loo_logloss - raw_logloss,
            "heldout_active_rate": float(frame["heldout_active"].mean()),
            "heldout_positive_rate_all": float(frame["heldout_positive"].mean()),
            "heldout_negative_rate_all": float(frame["heldout_negative"].mean()),
            "heldout_positive_rate_active": float(frame.loc[frame["heldout_active"], "heldout_positive"].mean()) if frame["heldout_active"].any() else 0.0,
            "mean_heldout_gain_per_cell": float(frame["heldout_gain_per_cell"].mean()),
            "selected_policy_entropy": int(frame["selected_policy_key"].nunique()),
            "most_selected_policy_key": str(frame["selected_policy_key"].value_counts().index[0]),
        })
    summary = pd.DataFrame(summaries).sort_values("subject_loo_logloss", kind="mergesort").reset_index(drop=True)
    return pd.DataFrame(decisions), summary


def rebuild_release_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, float]]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    episode, row_pair_frame, row_meta = build_oof_episode_state(cell_frame)
    raw_pred = cell_frame[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame).merge(raw_pred, on="cell_key", how="left", suffixes=("", "_dup"))
    if "raw_pred_dup" in gain_pairs.columns:
        gain_pairs = gain_pairs.drop(columns=["raw_pred_dup"])
    gain_pairs = add_law_features(gain_pairs)
    gain_pairs = attach_episode_features(gain_pairs, episode)
    return features_frame, labels, sample, raw_cols, gain_pairs, row_pair_frame, row_meta, episode_thresholds(episode)


def release_from_policy(policy: pd.Series, features: list[str], thresholds: dict[str, float]) -> dict[str, Any]:
    spec_map = {str(spec["model_name"]): spec for spec in SCORE_SPECS}
    law_name = str(policy["law_name"])
    if law_name not in spec_map:
        raise KeyError(f"unknown law_name for release: {law_name}")
    policy_map = {str(item["name"]): item for item in action_space_policies(thresholds)}
    action_policy_name = str(policy["action_space_policy"])
    if action_policy_name not in policy_map:
        raise KeyError(f"unknown action-space policy: {action_policy_name}")
    metric = {
        "law_name": law_name,
        "model_name": law_name,
        "action_space_policy": action_policy_name,
        "selection_policy": str(policy["selection_policy"]),
        "selection_param": float(policy["selection_param"]),
    }
    return {
        "metric": metric,
        "space_policy": policy_map[action_policy_name],
        "spec": spec_map[law_name],
        "features": features,
    }


def make_release_candidate(policy: pd.Series) -> tuple[str, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    features_frame, labels, sample, raw_cols, gain_pairs, row_pair_frame, row_meta, thresholds = rebuild_release_context()
    features = law_feature_views(gain_pairs)["route_disagreement_law"]
    leak_cols = [col for col in features if "loss" in col or "gain" in col or col in {"y", "raw_loss"}]
    if leak_cols:
        raise RuntimeError(f"leaky release feature columns detected: {leak_cols}")
    release = release_from_policy(policy, features, thresholds)
    submission, test_actions, description = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        gain_pairs,
        row_pair_frame,
        row_meta,
        release,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_subject_invariant_episode_controller_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)
    return candidate_file, submission, test_actions, description


def markdown_table(frame: pd.DataFrame, max_rows: int = 16) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        vals = []
        for col in cols:
            val = rec[col]
            vals.append(f"{val:.6f}" if isinstance(val, float) else str(val))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], objectives: pd.DataFrame, loo_summary: pd.DataFrame, decisions: pd.DataFrame, test_actions: pd.DataFrame) -> str:
    top_obj_cols = [
        "objective_name",
        "law_name",
        "action_space_policy",
        "selection_policy",
        "selection_param",
        "objective_score",
        "logloss",
        "gain_per_cell",
        "selected_cells",
        "active_subjects",
        "negative_active_subjects",
        "no_action_subject_rate",
    ]
    loo_cols = [
        "objective_name",
        "subject_loo_logloss",
        "delta_vs_raw",
        "heldout_active_rate",
        "heldout_positive_rate_all",
        "heldout_negative_rate_all",
        "selected_policy_entropy",
    ]
    release_cols = [
        "target",
        "count",
    ]
    if len(test_actions):
        release_counts = test_actions[test_actions["switched"]]["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).rename_axis("target").reset_index(name="count")
    else:
        release_counts = pd.DataFrame({"target": TARGETS, "count": [0] * len(TARGETS)})
    lines = [
        "# Subject-Invariant Episode Controller",
        "",
        "## 한 줄 요약",
        "",
        "episode row-state controller를 full OOF 최저점으로 고르지 않고, subject가 바뀌어도 살아남는 목적함수로 고르는 실험이다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py",
        "python3 sleep_competition_adapter/subject_invariant_episode_controller.py",
        "```",
        "",
        "public LB, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.",
        "",
        "## 왜 이것이 HS-JEPA/LeJEPA 진단인가",
        "",
        "이 실험은 새 predictor를 만드는 실험이 아니라, HS-JEPA representation이 만든 action을 믿어도 되는지 검사하는 health check다.",
        "",
        "| JEPA 구성요소 | 이 실험에서의 의미 |",
        "| --- | --- |",
        "| context | row episode state와 target/route context |",
        "| target representation | full OOF에서 성공한 것처럼 보이는 action-space policy |",
        "| predictor | subject를 하나 가린 상태에서 어떤 controller가 target representation을 안정적으로 재현하는지 선택 |",
        "| energy / decoder | 선택된 controller가 held-out subject에서 raw보다 낮은 action energy를 만드는지 검사 |",
        "| LeJEPA-style health check | subject-LOO, active subject rate, negative heldout action으로 shortcut/collapse를 판정 |",
        "",
        "따라서 이 문서는 positive release 모델이라기보다, HS-JEPA decoder가 subject shortcut에 빠졌는지 확인하는 anti-collapse audit다.",
        "",
        "## Architecture Contract",
        "",
        "```text",
        "row episode representation",
        "  -> candidate action-space controller",
        "  -> subject-heldout policy selection",
        "  -> heldout action-health stress",
        "  -> accept only if representation survives subject shift",
        "```",
        "",
        "## 핵심 결과",
        "",
        f"- raw OOF logloss: `{readout['raw_oof_logloss_from_cells']:.6f}`",
        f"- full OOF best restricted logloss: `{readout['full_oof_best_restricted_logloss']:.6f}`",
        f"- best subject-invariant objective: `{readout['best_subject_loo_objective']}`",
        f"- best subject-LOO logloss: `{readout['best_subject_loo_logloss']:.6f}`",
        f"- best subject-LOO delta vs raw: `{readout['best_subject_loo_delta_vs_raw']:.6f}`",
        f"- release objective: `{readout['release_objective_name']}`",
        f"- release policy: `{readout['release_policy_key']}`",
        f"- release full OOF logloss: `{readout['release_full_oof_logloss']:.6f}`",
        f"- release candidate: `{readout['candidate_file']}`",
        f"- verdict: `{readout['verdict']}`",
        "",
        "## Objective leaderboard",
        "",
        markdown_table(loo_summary[loo_cols], max_rows=12),
        "",
        "## Release objective top policies",
        "",
        markdown_table(objectives[objectives["objective_name"].eq(readout["release_objective_name"])][top_obj_cols], max_rows=16),
        "",
        "## Release test switched target counts",
        "",
        markdown_table(release_counts[release_cols], max_rows=10),
        "",
        "## Subject-LOO decisions for release objective",
        "",
        markdown_table(decisions[decisions["objective_name"].eq(readout["release_objective_name"])][[
            "heldout_subject",
            "selected_action_space_policy",
            "heldout_logloss",
            "heldout_raw_logloss",
            "heldout_gain_per_cell",
            "heldout_selected_cells",
            "heldout_positive",
            "heldout_negative",
        ]], max_rows=20),
        "",
        "## 논문용 해석",
        "",
        "이 실험은 HS-JEPA representation을 더 크게 만드는 실험이 아니라, representation이 만든 action을 어떤 기준으로 믿을지 정의한다.",
        "LeJEPA식으로 보면 full OOF loss만 낮은 controller는 shortcut/collapse일 수 있다.",
        "따라서 subject-invariant objective는 human-state representation의 건강성 검사이자 row-target assignment decoder의 안전장치다.",
        "",
        "좋은 결과는 subject-LOO에서도 raw보다 낮은 logloss를 유지하는 것이다.",
        "나쁜 결과는 episode state가 action-space를 제한할 수는 있지만, 아직 subject-general law로는 번역되지 않았다는 뜻이다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    selected, gain_pairs, _metrics, source_readout = load_inputs()
    cells = build_cell_baseline(gain_pairs)
    table = policy_subject_table(selected, cells)
    objectives = objective_table(table)
    decisions, loo_summary = subject_loo_by_objective(table)
    objectives.to_csv(OUT / "subject_invariant_objective_table.csv", index=False)
    decisions.to_csv(OUT / "subject_invariant_subject_loo_decisions.csv", index=False)
    loo_summary.to_csv(OUT / "subject_invariant_subject_loo_summary.csv", index=False)

    best_loo = loo_summary.iloc[0].to_dict()
    release_objective = str(best_loo["objective_name"])
    release_policy = objectives[
        objectives["objective_name"].eq(release_objective)
        & objectives["objective_rank"].eq(1)
    ].iloc[0]
    candidate_file, _submission, test_actions, description = make_release_candidate(release_policy)
    test_actions.to_csv(OUT / "subject_invariant_test_actions.csv", index=False)
    (OUT / "subject_invariant_release_model_description.json").write_text(
        json.dumps(description, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    eps = 1e-9
    if float(best_loo["delta_vs_raw"]) < -0.001:
        verdict = "subject_invariant_controller_positive"
    elif float(best_loo["delta_vs_raw"]) < -eps:
        verdict = "weak_subject_invariant_controller_positive"
    elif abs(float(best_loo["delta_vs_raw"])) <= eps:
        verdict = "subject_invariant_selector_is_safe_but_inactive"
    else:
        verdict = "subject_invariant_selector_does_not_yet_generalize"

    readout = {
        "package": "subject_invariant_episode_controller",
        "status": "subject_invariant_controller_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "source_candidate_file": source_readout.get("candidate_file", ""),
        "raw_oof_logloss_from_cells": float(best_loo["raw_logloss"]),
        "full_oof_best_restricted_logloss": float(source_readout["source_best_restricted_oof_logloss"] if "source_best_restricted_oof_logloss" in source_readout else source_readout["best_restricted_oof_logloss"]),
        "best_subject_loo_objective": str(best_loo["objective_name"]),
        "best_subject_loo_logloss": float(best_loo["subject_loo_logloss"]),
        "best_subject_loo_delta_vs_raw": float(best_loo["delta_vs_raw"]),
        "release_objective_name": release_objective,
        "release_policy_key": str(release_policy["policy_key"]),
        "release_law_name": str(release_policy["law_name"]),
        "release_action_space_policy": str(release_policy["action_space_policy"]),
        "release_selection_policy": str(release_policy["selection_policy"]),
        "release_selection_param": float(release_policy["selection_param"]),
        "release_full_oof_logloss": float(release_policy["logloss"]),
        "release_gain_per_cell": float(release_policy["gain_per_cell"]),
        "release_active_subjects": int(release_policy["active_subjects"]),
        "release_negative_active_subjects": int(release_policy["negative_active_subjects"]),
        "release_test_switched_cells": int(test_actions["switched"].sum()) if len(test_actions) else 0,
        "candidate_file": candidate_file,
        "verdict": verdict,
    }
    (OUT / "subject_invariant_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, objectives, loo_summary, decisions, test_actions)
    (OUT / "SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md").write_text(md + "\n", encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md").write_text(md + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
