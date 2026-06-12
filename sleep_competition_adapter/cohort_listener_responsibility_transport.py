#!/usr/bin/env python3
"""Cohort-level listener responsibility transport for HS-JEPA.

Cell-level world-model residual thresholds found toxic action pockets, but they
failed subject-heldout stress.  This experiment moves the decision up one
level:

    choose a listener rule for a subject-target from similar peer subjects,
    then transport that responsibility rule to the held-out subject.

The goal is not another local veto.  The goal is to test whether HS-JEPA core
residual geometry supports a subject/cohort-level responsibility law.

Public-free inputs:
    - OG-derived HS-JEPA world-model residual state
    - cross-subject prototype action field
    - OOF action gains only for local stress
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

from sleep_competition_adapter.subject_invariant_world_model_listener_solver import (  # noqa: E402
    OBJECTIVES,
    candidate_grid,
    candidate_mask,
    evaluate_rules,
)
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
    reconstruct_release_oof_actions,
    release_spec,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "cohort_listener_responsibility_transport"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "COHORT_LISTENER_RESPONSIBILITY_TRANSPORT_KO.md"
NEIGHBOR_COUNTS = [1, 2, 3, 4, 5, 6]
RELEASE_OBJECTIVE = "subject_balanced_listener"
FINGERPRINT_STATS = ["mean", "std", "q25", "q75"]


def ensure_inputs() -> None:
    if not WORLD_MODEL_STATE.exists():
        subprocess.run(["python3", str(WORLD_MODEL_SCRIPT)], cwd=ROOT, check=True)


def make_subject_fingerprint(state: pd.DataFrame, score_cols: list[str], split: str) -> pd.DataFrame:
    part = state[state["split"].eq(split)].copy()
    rows: list[dict[str, Any]] = []
    for subject, group in part.groupby("subject_id", observed=True):
        rec: dict[str, Any] = {"subject_id": subject, "rows": int(len(group))}
        for col in score_cols:
            values = pd.to_numeric(group[col], errors="coerce")
            rec[f"{col}__mean"] = float(values.mean())
            rec[f"{col}__std"] = float(values.std(ddof=0))
            rec[f"{col}__q25"] = float(values.quantile(0.25))
            rec[f"{col}__q75"] = float(values.quantile(0.75))
        rows.append(rec)
    return pd.DataFrame(rows).sort_values("subject_id").reset_index(drop=True)


def standardize_fingerprints(train_fp: pd.DataFrame, query_fp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    feature_cols = [col for col in train_fp.columns if col not in {"subject_id", "rows"}]
    mean = train_fp[feature_cols].mean()
    std = train_fp[feature_cols].std(ddof=0).replace(0, 1.0).fillna(1.0)
    train_z = train_fp.copy()
    query_z = query_fp.copy()
    train_z[feature_cols] = (train_z[feature_cols] - mean) / std
    query_z[feature_cols] = (query_z[feature_cols] - mean) / std
    train_z[feature_cols] = train_z[feature_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    query_z[feature_cols] = query_z[feature_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return train_z, query_z, feature_cols


def nearest_peers(
    subject: str,
    query_fp: pd.DataFrame,
    pool_fp: pd.DataFrame,
    feature_cols: list[str],
    pool_subjects: list[str],
    k: int,
    exclude_subject: str | None = None,
) -> list[str]:
    query = query_fp[query_fp["subject_id"].astype(str).eq(str(subject))]
    if query.empty:
        return pool_subjects[:k]
    pool = pool_fp[pool_fp["subject_id"].astype(str).isin([str(item) for item in pool_subjects])].copy()
    if exclude_subject is not None:
        pool = pool[~pool["subject_id"].astype(str).eq(str(exclude_subject))]
    if pool.empty:
        return []
    q = query[feature_cols].iloc[0].to_numpy(dtype=float)
    matrix = pool[feature_cols].to_numpy(dtype=float)
    pool["distance"] = np.sqrt(((matrix - q) ** 2).sum(axis=1))
    return pool.sort_values(["distance", "subject_id"], kind="mergesort")["subject_id"].astype(str).head(k).tolist()


def choose_rule(peer_cells: pd.DataFrame, score_cols: list[str], objective: str) -> dict[str, Any]:
    if peer_cells.empty:
        return {
            "score_col": score_cols[0],
            "mode": "all",
            "threshold": 0.0,
            "objective_score": 0.0,
            "peer_cells": 0,
            "peer_gain_sum": 0.0,
            "peer_improvement_sum": 0.0,
        }
    grid = candidate_grid(peer_cells, score_cols)
    if grid.empty:
        return {
            "score_col": score_cols[0],
            "mode": "all",
            "threshold": 0.0,
            "objective_score": 0.0,
            "peer_cells": int(len(peer_cells)),
            "peer_gain_sum": float(peer_cells["true_gain"].sum()),
            "peer_improvement_sum": 0.0,
        }
    score_col = f"score__{objective}"
    if score_col not in grid.columns:
        raise ValueError(f"unknown objective score column: {score_col}")
    best = grid.sort_values(
        [score_col, "improvement_sum", "selected_positive_gain_rate", "selected_gain_sum"],
        ascending=False,
        kind="mergesort",
    ).iloc[0]
    if str(best["mode"]) != "all" and float(best[score_col]) <= 0.0:
        best = grid[grid["mode"].eq("all")].iloc[0]
    return {
        "score_col": str(best["score_col"]),
        "mode": str(best["mode"]),
        "threshold": float(best["threshold"]),
        "objective_score": float(best[score_col]),
        "peer_cells": int(best["all_cells"]),
        "peer_selected_cells": int(best["selected_cells"]),
        "peer_gain_sum": float(best["all_gain_sum"]),
        "peer_selected_gain_sum": float(best["selected_gain_sum"]),
        "peer_improvement_sum": float(best["improvement_sum"]),
        "peer_negative_improvement_subjects": int(best["negative_improvement_subjects"]),
        "peer_min_subject_improvement": float(best["min_subject_improvement"]),
    }


def transport_oof(
    oof: pd.DataFrame,
    train_fp_z: pd.DataFrame,
    feature_cols: list[str],
    score_cols: list[str],
    k: int,
    objective: str,
) -> tuple[pd.Series, pd.DataFrame]:
    keep = pd.Series(True, index=oof.index)
    assignments: list[dict[str, Any]] = []
    action_subjects = sorted(oof["subject_id"].astype(str).unique())
    for subject in action_subjects:
        peers = nearest_peers(subject, train_fp_z, train_fp_z, feature_cols, action_subjects, k, exclude_subject=subject)
        for target in TARGETS:
            idx = oof[oof["subject_id"].astype(str).eq(subject) & oof["target"].eq(target)].index
            if len(idx) == 0:
                continue
            peer_cells = oof[oof["subject_id"].astype(str).isin(peers) & oof["target"].eq(target)].copy()
            rule = choose_rule(peer_cells, score_cols, objective)
            selected = candidate_mask(oof.loc[idx], rule)
            keep.loc[idx] = selected.to_numpy(dtype=bool)
            assignments.append(
                {
                    "split": "oof",
                    "subject_id": subject,
                    "target": target,
                    "k": k,
                    "objective": objective,
                    "peers": ",".join(peers),
                    "heldout_cells": int(len(idx)),
                    "kept_cells": int(selected.sum()),
                    **rule,
                }
            )
    return keep.astype(bool), pd.DataFrame(assignments)


def subject_transport_summary(oof: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
    tmp = oof.copy()
    tmp["keep"] = keep.to_numpy(dtype=bool)
    rows: list[dict[str, Any]] = []
    for subject, part in tmp.groupby("subject_id", observed=True):
        kept = part[part["keep"]]
        rows.append(
            {
                "subject_id": subject,
                "all_cells": int(len(part)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(part["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "improvement_sum": float((kept["true_gain"].sum() if len(kept) else 0.0) - part["true_gain"].sum()),
                "all_positive_gain_rate": float((part["true_gain"] > 0).mean()) if len(part) else 0.0,
                "kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def transport_target_summary(oof: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
    tmp = oof.copy()
    tmp["keep"] = keep.to_numpy(dtype=bool)
    rows: list[dict[str, Any]] = []
    for target, part in tmp.groupby("target", observed=True):
        kept = part[part["keep"]]
        rows.append(
            {
                "target": target,
                "rule": "cohort_peer_transport",
                "all_cells": int(len(part)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(part["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "improvement_sum": float((kept["true_gain"].sum() if len(kept) else 0.0) - part["true_gain"].sum()),
            }
        )
    return pd.DataFrame(rows)


def objective_board_for_k(
    oof: pd.DataFrame,
    train_fp_z: pd.DataFrame,
    feature_cols: list[str],
    score_cols: list[str],
    objective: str,
) -> tuple[pd.DataFrame, dict[int, tuple[pd.Series, pd.DataFrame, pd.DataFrame]]]:
    rows: list[dict[str, Any]] = []
    cache: dict[int, tuple[pd.Series, pd.DataFrame, pd.DataFrame]] = {}
    for k in NEIGHBOR_COUNTS:
        keep, assignments = transport_oof(oof, train_fp_z, feature_cols, score_cols, k, objective)
        metrics = evaluate_rules(oof, pd.DataFrame(), keep)
        subject_summary = subject_transport_summary(oof, keep)
        non_all = int(assignments["mode"].ne("all").sum()) if len(assignments) else 0
        rows.append(
            {
                "objective": objective,
                "neighbors": k,
                **metrics,
                "non_all_assignments": non_all,
                "positive_subjects": int((subject_summary["improvement_sum"] > 0).sum()) if len(subject_summary) else 0,
                "negative_subjects": int((subject_summary["improvement_sum"] < 0).sum()) if len(subject_summary) else 0,
                "min_subject_improvement": float(subject_summary["improvement_sum"].min()) if len(subject_summary) else 0.0,
                "mean_subject_improvement": float(subject_summary["improvement_sum"].mean()) if len(subject_summary) else 0.0,
            }
        )
        cache[k] = (keep, assignments, subject_summary)
    board = pd.DataFrame(rows).sort_values(
        ["oof_gain_delta", "positive_subjects", "negative_subjects", "non_all_assignments"],
        ascending=[False, False, True, False],
        kind="mergesort",
    )
    return board, cache


def pick_k(board: pd.DataFrame) -> int:
    positive = board[
        board["oof_gain_delta"].gt(0)
        & board["non_all_assignments"].gt(0)
        & board["positive_subjects"].ge(board["negative_subjects"])
    ]
    if len(positive):
        return int(positive.iloc[0]["neighbors"])
    nontrivial = board[board["non_all_assignments"].gt(0)]
    if len(nontrivial):
        return int(nontrivial.iloc[0]["neighbors"])
    return int(board.iloc[0]["neighbors"])


def transport_test(
    test_audit: pd.DataFrame,
    oof: pd.DataFrame,
    train_fp_z: pd.DataFrame,
    test_fp_z: pd.DataFrame,
    feature_cols: list[str],
    score_cols: list[str],
    k: int,
    objective: str,
) -> tuple[pd.Series, pd.DataFrame]:
    keep = pd.Series(True, index=test_audit.index)
    assignments: list[dict[str, Any]] = []
    action_subjects = sorted(oof["subject_id"].astype(str).unique())
    for subject in sorted(test_audit["subject_id"].astype(str).unique()):
        peers = nearest_peers(subject, test_fp_z, train_fp_z, feature_cols, action_subjects, k)
        for target in TARGETS:
            idx = test_audit[test_audit["subject_id"].astype(str).eq(subject) & test_audit["target"].eq(target)].index
            if len(idx) == 0:
                continue
            peer_cells = oof[oof["subject_id"].astype(str).isin(peers) & oof["target"].eq(target)].copy()
            rule = choose_rule(peer_cells, score_cols, objective)
            selected = candidate_mask(test_audit.loc[idx], rule)
            keep.loc[idx] = selected.to_numpy(dtype=bool)
            assignments.append(
                {
                    "split": "test",
                    "subject_id": subject,
                    "target": target,
                    "k": k,
                    "objective": objective,
                    "peers": ",".join(peers),
                    "rows": int(len(idx)),
                    "kept_rows": int(selected.sum()),
                    **rule,
                }
            )
    return keep.astype(bool), pd.DataFrame(assignments)


def test_counts(test_audit: pd.DataFrame) -> pd.DataFrame:
    switched = test_audit[test_audit["switched"].astype(bool)].copy()
    return (
        switched.groupby("target", observed=True)
        .agg(switched=("switched", "size"), kept=("world_model_keep", "sum"), vetoed=("vetoed", "sum"))
        .reset_index()
    )


def build_markdown(
    readout: dict[str, Any],
    board: pd.DataFrame,
    assignments: pd.DataFrame,
    subject_summary: pd.DataFrame,
    per_target: pd.DataFrame,
    counts: pd.DataFrame,
) -> str:
    return f"""# Cohort Listener Responsibility Transport

## 한 줄 요약

Cell-level threshold 대신, HS-JEPA world-model subject fingerprint가 비슷한 peer subject에서
target별 listener responsibility rule을 빌려와 held-out subject/test subject에 전이했다.

```text
HS-JEPA world-model subject fingerprint
  -> nearest peer subjects
  -> peer target-listener responsibility rule
  -> held-out subject row-target action veto
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 subject/cohort-level
action responsibility로 번역하는 adapter 실험이다.

이전 실패는 cell-level residual threshold가 subject-LOO에서 무너진다는 것이었다.
이번 실험은 decision level을 cell에서 subject/cohort로 올린다.

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Objective Board

{markdown_table(board, ["objective", "neighbors", "oof_gain_delta", "oof_kept_gain_sum", "non_all_assignments", "positive_subjects", "negative_subjects", "min_subject_improvement"], max_rows=20)}

## Release Setting

- release objective: `{readout["release_objective"]}`
- peer neighbors: `{readout["release_neighbors"]}`
- verdict: `{readout["verdict"]}`
- original OOF gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- transported kept gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- transported gain delta: `{readout["oof_gain_delta"]:.6f}`
- positive subjects: `{readout["positive_subjects"]}`
- negative subjects: `{readout["negative_subjects"]}`

## OOF Subject Transport Summary

{markdown_table(subject_summary, ["subject_id", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

Target summary:

{markdown_table(per_target, ["target", "rule", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

Assignment examples:

{markdown_table(assignments, ["split", "subject_id", "target", "peers", "mode", "score_col", "threshold", "peer_improvement_sum"], max_rows=24)}

## Test Candidate

- candidate: `{readout["candidate_file"]}`
- original switched cells: `{readout["test_original_switched_cells"]}`
- kept switched cells: `{readout["test_kept_switched_cells"]}`
- vetoed switched cells: `{readout["test_vetoed_switched_cells"]}`
- validation: `{readout["validation"]}`

Target별 test kept/vetoed:

{markdown_table(counts, ["target", "switched", "kept", "vetoed"], max_rows=20)}

## 해석

성공 조건:

```text
peer subject에서 학습한 listener responsibility가 held-out subject에서도 toxic action을 제거한다.
```

실패 조건:

```text
nearest-peer responsibility가 subject-LOO에서 개선되지 않거나,
대부분 all-action으로 후퇴한다.
```

이 실험의 의미는 단순 veto가 아니다. HS-JEPA core representation을 subject/cohort
좌표계로 해석했을 때, action responsibility가 개인을 넘어 전이 가능한지 검증한다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inputs()
    spec = release_spec()
    actions, source_metric = reconstruct_release_oof_actions(spec)
    world_state = pd.read_csv(WORLD_MODEL_STATE)
    score_cols = energy_columns(world_state)
    oof = attach_world_model_state(actions, world_state, "train")
    train_fp = make_subject_fingerprint(world_state, score_cols, "train")
    test_fp = make_subject_fingerprint(world_state, score_cols, "test")
    train_fp_z, test_fp_z, feature_cols = standardize_fingerprints(train_fp, test_fp)

    board, cache = objective_board_for_k(oof, train_fp_z, feature_cols, score_cols, RELEASE_OBJECTIVE)
    release_k = pick_k(board)
    keep, assignments, subject_summary = cache[release_k]
    oof["cohort_transport_keep"] = keep.to_numpy(dtype=bool)
    per_target = transport_target_summary(oof, keep)

    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test_audit = attach_world_model_state(test_actions, world_state, "test")
    test_keep, test_assignments = transport_test(
        test_audit,
        oof,
        train_fp_z,
        test_fp_z,
        feature_cols,
        score_cols,
        release_k,
        RELEASE_OBJECTIVE,
    )
    candidate, test_audit = build_candidate(test_audit, test_keep)
    validation = validate_submission(candidate, read_sample())
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")

    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_cohort_listener_responsibility_transport_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    counts = test_counts(test_audit)

    selected = board[board["neighbors"].eq(release_k)].iloc[0].to_dict()
    if float(selected["oof_gain_delta"]) > 0 and int(selected["positive_subjects"]) >= int(selected["negative_subjects"]):
        verdict = "cohort_transport_positive"
    elif float(selected["oof_gain_delta"]) > 0:
        verdict = "cohort_transport_oof_positive_subject_mixed"
    else:
        verdict = "cohort_transport_negative_or_inconclusive"

    readout = {
        "package": "cohort_listener_responsibility_transport",
        "status": "adapter_diagnostic_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "release_objective": RELEASE_OBJECTIVE,
        "release_neighbors": release_k,
        "source_metric": source_metric.iloc[0].to_dict() if len(source_metric) else {},
        "oof_original_cells": int(selected["oof_original_cells"]),
        "oof_original_gain_sum": float(selected["oof_original_gain_sum"]),
        "oof_kept_cells": int(selected["oof_kept_cells"]),
        "oof_kept_gain_sum": float(selected["oof_kept_gain_sum"]),
        "oof_removed_cells": int(selected["oof_removed_cells"]),
        "oof_removed_gain_sum": float(selected["oof_removed_gain_sum"]),
        "oof_gain_delta": float(selected["oof_gain_delta"]),
        "non_all_assignments": int(selected["non_all_assignments"]),
        "positive_subjects": int(selected["positive_subjects"]),
        "negative_subjects": int(selected["negative_subjects"]),
        "min_subject_improvement": float(selected["min_subject_improvement"]),
        "test_original_switched_cells": int(test_audit["switched"].astype(bool).sum()),
        "test_kept_switched_cells": int((test_audit["switched"].astype(bool) & test_audit["world_model_keep"]).sum()),
        "test_vetoed_switched_cells": int(test_audit["vetoed"].sum()),
        "candidate_file": candidate_file,
        "validation": validation,
        "verdict": verdict,
        "worldview": (
            "HS-JEPA world-model residuals should be more useful when listener responsibility "
            "is transported at the subject/cohort level rather than thresholded per cell."
        ),
    }

    all_assignments = pd.concat([assignments, test_assignments], ignore_index=True)
    board.to_csv(OUT_DIR / "cohort_listener_objective_board.csv", index=False)
    all_assignments.to_csv(OUT_DIR / "cohort_listener_assignments.csv", index=False)
    oof.to_csv(OUT_DIR / "cohort_listener_oof_action_audit.csv", index=False)
    subject_summary.to_csv(OUT_DIR / "cohort_listener_subject_summary.csv", index=False)
    per_target.to_csv(OUT_DIR / "cohort_listener_target_summary.csv", index=False)
    train_fp.to_csv(OUT_DIR / "cohort_listener_train_subject_fingerprint.csv", index=False)
    test_fp.to_csv(OUT_DIR / "cohort_listener_test_subject_fingerprint.csv", index=False)
    test_audit.to_csv(OUT_DIR / "cohort_listener_test_action_audit.csv", index=False)
    counts.to_csv(OUT_DIR / "cohort_listener_test_summary.csv", index=False)
    (OUT_DIR / "cohort_listener_responsibility_transport_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, board, assignments, subject_summary, per_target, counts)
    (OUT_DIR / "COHORT_LISTENER_RESPONSIBILITY_TRANSPORT_KO.md").write_text(
        md.rstrip() + "\n",
        encoding="utf-8",
    )
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
