#!/usr/bin/env python3
"""Subject-invariant listener solver for HS-JEPA world-model residuals.

The previous world-model residual action decoder showed a useful but fragile
pattern:

    full OOF action toxicity improved, but subject-heldout stress collapsed.

This script changes the selection objective.  It treats the HS-JEPA world-model
residual as a target-specific listener, then accepts a listener rule only when
its gain is not explained by one subject tail.

The experiment is public-free:
    - no public LB ledger
    - no prior submission probabilities
    - no proprietary embedding API

Question:
    Can a subject-invariant objective preserve the toxicity separation of the
    HS-JEPA core residual while avoiding subject-specific action shortcuts?
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.surprise_responsibility_toxicity_veto import (  # noqa: E402
    TARGETS,
    markdown_table,
    read_sample,
    short_hash,
    validate_submission,
)
from sleep_competition_adapter.world_model_residual_action_decoder import (  # noqa: E402
    CROSS_TEST_ACTIONS,
    WORLD_MODEL_SCRIPT,
    WORLD_MODEL_STATE,
    attach_world_model_state,
    build_candidate,
    energy_columns,
    keep_for_rule,
    reconstruct_release_oof_actions,
    release_spec,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "subject_invariant_world_model_listener_solver"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_INVARIANT_WORLD_MODEL_LISTENER_SOLVER_KO.md"
MIN_ROBUST_SCORE = 0.0
QUANTILES = [0.25, 0.5, 0.75]


OBJECTIVES: dict[str, dict[str, float]] = {
    "full_oof_improvement": {
        "negative_subject_penalty": 0.0,
        "min_subject_penalty": 0.0,
        "coverage_penalty": 0.0,
        "positive_subject_bonus": 0.0,
    },
    "subject_balanced_listener": {
        "negative_subject_penalty": 0.18,
        "min_subject_penalty": 0.65,
        "coverage_penalty": 0.04,
        "positive_subject_bonus": 0.035,
    },
    "minimax_listener": {
        "negative_subject_penalty": 0.25,
        "min_subject_penalty": 1.05,
        "coverage_penalty": 0.06,
        "positive_subject_bonus": 0.02,
    },
}


def ensure_inputs() -> None:
    if not WORLD_MODEL_STATE.exists():
        subprocess.run(["python3", str(WORLD_MODEL_SCRIPT)], cwd=ROOT, check=True)


def candidate_mask(frame: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    if rule["mode"] == "all":
        return pd.Series(True, index=frame.index)
    return keep_for_rule(frame, rule)


def subject_improvement(part: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    all_by_subject = (
        part.groupby("subject_id", observed=True)
        .agg(
            all_cells=("cell_key", "size"),
            all_gain_sum=("true_gain", "sum"),
        )
        .reset_index()
    )
    if selected.empty:
        kept_by_subject = all_by_subject[["subject_id"]].copy()
        kept_by_subject["kept_cells"] = 0
        kept_by_subject["kept_gain_sum"] = 0.0
    else:
        kept_by_subject = (
            selected.groupby("subject_id", observed=True)
            .agg(
                kept_cells=("cell_key", "size"),
                kept_gain_sum=("true_gain", "sum"),
            )
            .reset_index()
        )
    out = all_by_subject.merge(kept_by_subject, on="subject_id", how="left")
    out["kept_cells"] = out["kept_cells"].fillna(0).astype(int)
    out["kept_gain_sum"] = out["kept_gain_sum"].fillna(0.0)
    out["improvement_sum"] = out["kept_gain_sum"] - out["all_gain_sum"]
    return out


def evaluate_candidate(part: pd.DataFrame, rule: dict[str, Any]) -> dict[str, Any]:
    mask = candidate_mask(part, rule)
    selected = part.loc[mask]
    subject_table = subject_improvement(part, selected)
    improvement = float(selected["true_gain"].sum() - part["true_gain"].sum()) if len(part) else 0.0
    negative_subjects = int((subject_table["improvement_sum"] < -1e-12).sum())
    positive_subjects = int((subject_table["improvement_sum"] > 1e-12).sum())
    no_action_subjects = int((subject_table["kept_cells"] == 0).sum())
    min_improvement = float(subject_table["improvement_sum"].min()) if len(subject_table) else 0.0
    return {
        "target": str(part["target"].iloc[0]) if len(part) else "",
        "score_col": str(rule["score_col"]),
        "mode": str(rule["mode"]),
        "threshold": float(rule["threshold"]),
        "all_cells": int(len(part)),
        "selected_cells": int(len(selected)),
        "all_gain_sum": float(part["true_gain"].sum()) if len(part) else 0.0,
        "selected_gain_sum": float(selected["true_gain"].sum()) if len(selected) else 0.0,
        "improvement_sum": improvement,
        "all_positive_gain_rate": float((part["true_gain"] > 0).mean()) if len(part) else 0.0,
        "selected_positive_gain_rate": float((selected["true_gain"] > 0).mean()) if len(selected) else 0.0,
        "active_subjects": int(subject_table.loc[subject_table["kept_cells"].gt(0), "subject_id"].nunique()),
        "subject_count": int(subject_table["subject_id"].nunique()),
        "positive_improvement_subjects": positive_subjects,
        "negative_improvement_subjects": negative_subjects,
        "no_action_subjects": no_action_subjects,
        "min_subject_improvement": min_improvement,
        "mean_subject_improvement": float(subject_table["improvement_sum"].mean()) if len(subject_table) else 0.0,
    }


def score_candidate(row: pd.Series, objective: str) -> float:
    cfg = OBJECTIVES[objective]
    score = float(row["improvement_sum"])
    score -= float(cfg["negative_subject_penalty"]) * float(row["negative_improvement_subjects"])
    score -= float(cfg["min_subject_penalty"]) * max(0.0, -float(row["min_subject_improvement"]))
    score -= float(cfg["coverage_penalty"]) * float(row["no_action_subjects"]) / max(1.0, float(row["subject_count"]))
    score += float(cfg["positive_subject_bonus"]) * float(row["positive_improvement_subjects"])
    return score


def candidate_grid(part: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if part.empty:
        return pd.DataFrame()
    rows.append(evaluate_candidate(part, {"score_col": score_cols[0], "mode": "all", "threshold": 0.0}))
    for score_col in score_cols:
        values = pd.to_numeric(part[score_col], errors="coerce")
        if values.notna().sum() < 3 or values.nunique(dropna=True) < 2:
            continue
        for threshold in sorted(set(float(values.quantile(q)) for q in QUANTILES)):
            rows.append(
                evaluate_candidate(
                    part,
                    {"score_col": score_col, "mode": "low_energy_listener", "threshold": threshold},
                )
            )
            rows.append(
                evaluate_candidate(
                    part,
                    {"score_col": score_col, "mode": "high_energy_listener", "threshold": threshold},
                )
            )
    frame = pd.DataFrame(rows)
    for objective in OBJECTIVES:
        frame[f"score__{objective}"] = frame.apply(lambda row: score_candidate(row, objective), axis=1)
    return frame


def learn_rules(oof: pd.DataFrame, score_cols: list[str], objective: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rules: list[dict[str, Any]] = []
    detail: list[pd.DataFrame] = []
    for target, part in oof.groupby("target", observed=True):
        grid = candidate_grid(part, score_cols)
        if grid.empty:
            rules.append(
                {
                    "target": target,
                    "score_col": score_cols[0],
                    "mode": "all",
                    "threshold": 0.0,
                    "objective": objective,
                    "objective_score": 0.0,
                    "selected_cells": int(len(part)),
                    "improvement_sum": 0.0,
                }
            )
            continue
        grid["objective"] = objective
        detail.append(grid)
        score_col = f"score__{objective}"
        best = grid.sort_values(
            [score_col, "improvement_sum", "selected_positive_gain_rate", "selected_gain_sum"],
            ascending=False,
            kind="mergesort",
        ).iloc[0]
        if str(best["mode"]) != "all" and float(best[score_col]) <= MIN_ROBUST_SCORE:
            best = grid[grid["mode"].eq("all")].iloc[0]
        rules.append(
            {
                "target": target,
                "score_col": str(best["score_col"]),
                "mode": str(best["mode"]),
                "threshold": float(best["threshold"]),
                "objective": objective,
                "objective_score": float(best[score_col]),
                "all_cells": int(best["all_cells"]),
                "selected_cells": int(best["selected_cells"]),
                "all_gain_sum": float(best["all_gain_sum"]),
                "selected_gain_sum": float(best["selected_gain_sum"]),
                "improvement_sum": float(best["improvement_sum"]),
                "active_subjects": int(best["active_subjects"]),
                "positive_improvement_subjects": int(best["positive_improvement_subjects"]),
                "negative_improvement_subjects": int(best["negative_improvement_subjects"]),
                "min_subject_improvement": float(best["min_subject_improvement"]),
                "selected_positive_gain_rate": float(best["selected_positive_gain_rate"]),
            }
        )
    detail_frame = pd.concat(detail, ignore_index=True) if detail else pd.DataFrame()
    return pd.DataFrame(rules), detail_frame


def apply_rules(frame: pd.DataFrame, rules: pd.DataFrame) -> pd.Series:
    keep = pd.Series(True, index=frame.index)
    rule_map = {row["target"]: row.to_dict() for _, row in rules.iterrows()}
    for target, idx in frame.groupby("target", observed=True).groups.items():
        rule = rule_map.get(target)
        if rule is None:
            keep.loc[idx] = True
        else:
            keep.loc[idx] = candidate_mask(frame.loc[idx], rule).to_numpy(dtype=bool)
    return keep.astype(bool)


def evaluate_rules(oof: pd.DataFrame, rules: pd.DataFrame, keep: pd.Series) -> dict[str, Any]:
    kept = oof.loc[keep]
    removed = oof.loc[~keep]
    return {
        "oof_original_cells": int(len(oof)),
        "oof_original_active_subjects": int(oof["subject_id"].nunique()),
        "oof_original_gain_sum": float(oof["true_gain"].sum()),
        "oof_original_positive_gain_rate": float((oof["true_gain"] > 0).mean()) if len(oof) else 0.0,
        "oof_kept_cells": int(len(kept)),
        "oof_kept_active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "oof_gain_delta": float((kept["true_gain"].sum() if len(kept) else 0.0) - oof["true_gain"].sum()),
        "rule_non_all_targets": int(rules["mode"].ne("all").sum()) if len(rules) else 0,
    }


def subject_loo_stress(oof: pd.DataFrame, score_cols: list[str], objective: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for subject, idx in oof.groupby("subject_id", observed=True).groups.items():
        train = oof.drop(index=idx)
        holdout = oof.loc[idx].copy()
        rules, _ = learn_rules(train, score_cols, objective)
        keep = apply_rules(holdout, rules)
        kept = holdout.loc[keep]
        rows.append(
            {
                "objective": objective,
                "heldout_subject": subject,
                "all_cells": int(len(holdout)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(holdout["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "improvement_sum": float((kept["true_gain"].sum() if len(kept) else 0.0) - holdout["true_gain"].sum()),
                "all_positive_gain_rate": float((holdout["true_gain"] > 0).mean()) if len(holdout) else 0.0,
                "kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
                "learned_non_all_targets": int(rules["mode"].ne("all").sum()) if len(rules) else 0,
            }
        )
    return pd.DataFrame(rows)


def target_summary(oof: pd.DataFrame, rules: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
    tmp = oof.copy()
    tmp["keep"] = keep.to_numpy(dtype=bool)
    rows: list[dict[str, Any]] = []
    for target, part in tmp.groupby("target", observed=True):
        kept = part[part["keep"]]
        rule = rules[rules["target"].eq(target)].head(1)
        rows.append(
            {
                "target": target,
                "rule": "all" if rule.empty else f"{rule['mode'].iloc[0]}::{rule['score_col'].iloc[0]}",
                "threshold": 0.0 if rule.empty else float(rule["threshold"].iloc[0]),
                "all_cells": int(len(part)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(part["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "improvement_sum": float((kept["true_gain"].sum() if len(kept) else 0.0) - part["true_gain"].sum()),
            }
        )
    return pd.DataFrame(rows)


def test_summary(test_audit: pd.DataFrame) -> pd.DataFrame:
    switched = test_audit[test_audit["switched"].astype(bool)].copy()
    return (
        switched.groupby("target", observed=True)
        .agg(
            switched=("switched", "size"),
            kept=("world_model_keep", "sum"),
            vetoed=("vetoed", "sum"),
        )
        .reset_index()
    )


def objective_leaderboard(oof: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for objective in OBJECTIVES:
        rules, _ = learn_rules(oof, score_cols, objective)
        keep = apply_rules(oof, rules)
        metrics = evaluate_rules(oof, rules, keep)
        stress = subject_loo_stress(oof, score_cols, objective)
        rows.append(
            {
                "objective": objective,
                **metrics,
                "subject_loo_original_gain_sum": float(stress["all_gain_sum"].sum()) if len(stress) else 0.0,
                "subject_loo_kept_gain_sum": float(stress["kept_gain_sum"].sum()) if len(stress) else 0.0,
                "subject_loo_improvement_sum": float(stress["improvement_sum"].sum()) if len(stress) else 0.0,
                "subject_loo_positive_subjects": int((stress["improvement_sum"] > 0).sum()) if len(stress) else 0,
                "subject_loo_negative_subjects": int((stress["improvement_sum"] < 0).sum()) if len(stress) else 0,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["subject_loo_improvement_sum", "oof_gain_delta", "oof_kept_gain_sum"],
        ascending=False,
        kind="mergesort",
    )


def pick_release_objective(board: pd.DataFrame) -> str:
    positive = board[
        board["subject_loo_improvement_sum"].gt(0)
        & board["oof_gain_delta"].ge(0)
        & board["rule_non_all_targets"].gt(0)
    ]
    if len(positive):
        return str(positive.iloc[0]["objective"])
    nontrivial = board[board["rule_non_all_targets"].gt(0)]
    if len(nontrivial):
        return str(nontrivial.iloc[0]["objective"])
    return str(board.iloc[0]["objective"])


def build_markdown(
    readout: dict[str, Any],
    board: pd.DataFrame,
    rules: pd.DataFrame,
    summary: pd.DataFrame,
    stress: pd.DataFrame,
    test_counts: pd.DataFrame,
) -> str:
    return f"""# Subject-Invariant World-Model Listener Solver

## 한 줄 요약

HS-JEPA masked-context world model residual을 action-health listener로 쓰되,
full OOF gain이 아니라 subject-invariant objective로 listener rule을 고른 실험이다.

```text
HS-JEPA core residual energy
  -> target-specific listener candidates
  -> subject-balanced rule selector
  -> cross-subject prototype action veto
  -> subject-LOO stress
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니다.
정확한 위치는 core representation을 action decoder로 안전하게 번역할 수 있는지 검증하는
adapter + LeJEPA-style diagnostic이다.

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## 왜 필요한가

직전 `World-Model Residual Action Decoder`는 full OOF에서 toxic action을 잘 제거했다.
하지만 subject-heldout stress에서는 gain이 크게 줄어 `oof_positive_subjectheldout_fragile` 판정을 받았다.

이번 실험은 그 실패를 정면으로 찌른다.

```text
좋은 listener는 한 subject의 lucky tail이 아니라,
subject가 바뀌어도 같은 방향의 action-health를 보여야 한다.
```

## Objective Leaderboard

{markdown_table(board, ["objective", "oof_gain_delta", "oof_kept_gain_sum", "rule_non_all_targets", "subject_loo_improvement_sum", "subject_loo_positive_subjects", "subject_loo_negative_subjects"], max_rows=20)}

## Release Objective

- selected objective: `{readout["release_objective"]}`
- verdict: `{readout["verdict"]}`
- original OOF cells: `{readout["oof_original_cells"]}`
- kept OOF cells: `{readout["oof_kept_cells"]}`
- OOF gain delta: `{readout["oof_gain_delta"]:.6f}`
- subject-LOO improvement sum: `{readout["subject_loo_improvement_sum"]:.6f}`

## Learned Rules

{markdown_table(rules, ["target", "mode", "score_col", "threshold", "objective_score", "all_cells", "selected_cells", "improvement_sum", "negative_improvement_subjects", "min_subject_improvement"], max_rows=20)}

Target summary:

{markdown_table(summary, ["target", "rule", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

## Subject-LOO Stress

{markdown_table(stress, ["heldout_subject", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum", "learned_non_all_targets"], max_rows=20)}

## Test Candidate

- candidate: `{readout["candidate_file"]}`
- original switched cells: `{readout["test_original_switched_cells"]}`
- kept switched cells: `{readout["test_kept_switched_cells"]}`
- vetoed switched cells: `{readout["test_vetoed_switched_cells"]}`
- validation: `{readout["validation"]}`

Target별 test kept/vetoed:

{markdown_table(test_counts, ["target", "switched", "kept", "vetoed"], max_rows=20)}

## 해석

성공 조건:

```text
subject-balanced selector가 full OOF toxicity separation을 유지하면서
subject-LOO에서도 positive improvement를 만든다.
```

실패 조건:

```text
selector가 all-action으로 후퇴하거나,
subject-LOO improvement가 음수가 되어 core residual listener가 subject-tail shortcut임을 보인다.
```

현재 결과는 위 verdict를 따른다. 이 문서는 좋은 점수용 tuning이 아니라,
HS-JEPA core residual을 action decoder로 번역할 때 필요한 subject-invariance 조건을
검증하는 논문용 stress experiment다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inputs()
    spec = release_spec()
    actions, source_metric = reconstruct_release_oof_actions(spec)
    world_state = pd.read_csv(WORLD_MODEL_STATE)
    score_cols = energy_columns(world_state)
    oof = attach_world_model_state(actions, world_state, "train")
    board = objective_leaderboard(oof, score_cols)
    release_objective = pick_release_objective(board)
    rules, detail = learn_rules(oof, score_cols, release_objective)
    keep = apply_rules(oof, rules)
    oof["subject_invariant_keep"] = keep.to_numpy(dtype=bool)
    summary = target_summary(oof, rules, keep)
    stress = subject_loo_stress(oof, score_cols, release_objective)

    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test_audit = attach_world_model_state(test_actions, world_state, "test")
    test_keep = apply_rules(test_audit, rules)
    candidate, test_audit = build_candidate(test_audit, test_keep)
    validation = validate_submission(candidate, read_sample())
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_subject_invariant_world_model_listener_solver_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    counts = test_summary(test_audit)

    selected_metrics = evaluate_rules(oof, rules, keep)
    subject_loo_improvement = float(stress["improvement_sum"].sum()) if len(stress) else 0.0
    if selected_metrics["oof_gain_delta"] > 0 and subject_loo_improvement > 0:
        verdict = "subject_invariant_positive"
    elif selected_metrics["oof_gain_delta"] > 0 and subject_loo_improvement <= 0:
        verdict = "oof_positive_subject_invariant_negative"
    elif int(rules["mode"].ne("all").sum()) == 0:
        verdict = "selector_collapsed_to_all_action"
    else:
        verdict = "negative_or_inconclusive"

    readout = {
        "package": "subject_invariant_world_model_listener_solver",
        "status": "adapter_diagnostic_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "release_objective": release_objective,
        "source_metric": source_metric.iloc[0].to_dict() if len(source_metric) else {},
        **selected_metrics,
        "subject_loo_original_gain_sum": float(stress["all_gain_sum"].sum()) if len(stress) else 0.0,
        "subject_loo_kept_gain_sum": float(stress["kept_gain_sum"].sum()) if len(stress) else 0.0,
        "subject_loo_improvement_sum": subject_loo_improvement,
        "subject_loo_positive_subjects": int((stress["improvement_sum"] > 0).sum()) if len(stress) else 0,
        "subject_loo_negative_subjects": int((stress["improvement_sum"] < 0).sum()) if len(stress) else 0,
        "test_original_switched_cells": int(test_audit["switched"].astype(bool).sum()),
        "test_kept_switched_cells": int((test_audit["switched"].astype(bool) & test_audit["world_model_keep"]).sum()),
        "test_vetoed_switched_cells": int(test_audit["vetoed"].sum()),
        "candidate_file": candidate_file,
        "validation": validation,
        "verdict": verdict,
        "worldview": (
            "HS-JEPA core residual energy should become a release-grade listener only if "
            "its toxicity separation survives subject-invariant rule selection."
        ),
    }

    board.to_csv(OUT_DIR / "subject_invariant_world_model_objective_board.csv", index=False)
    rules.to_csv(OUT_DIR / "subject_invariant_world_model_listener_rules.csv", index=False)
    detail.to_csv(OUT_DIR / "subject_invariant_world_model_rule_detail.csv", index=False)
    oof.to_csv(OUT_DIR / "subject_invariant_world_model_oof_action_audit.csv", index=False)
    summary.to_csv(OUT_DIR / "subject_invariant_world_model_target_summary.csv", index=False)
    stress.to_csv(OUT_DIR / "subject_invariant_world_model_subject_loo_stress.csv", index=False)
    test_audit.to_csv(OUT_DIR / "subject_invariant_world_model_test_action_audit.csv", index=False)
    counts.to_csv(OUT_DIR / "subject_invariant_world_model_test_summary.csv", index=False)
    (OUT_DIR / "subject_invariant_world_model_listener_solver_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, board, rules, summary, stress, counts)
    (OUT_DIR / "SUBJECT_INVARIANT_WORLD_MODEL_LISTENER_SOLVER_KO.md").write_text(
        md.rstrip() + "\n",
        encoding="utf-8",
    )
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
