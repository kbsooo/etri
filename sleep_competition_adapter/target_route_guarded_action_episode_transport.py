#!/usr/bin/env python3
"""Target-route guarded action-episode transport for HS-JEPA.

The global action-episode listener transport found a positive route, but it
mixed two different regimes:

    S3 action episodes improved strongly.
    S4 action episodes were harmed.

This script makes that architectural separation explicit.  Each target can
choose its own responsibility policy:

    - keep all source actions
    - veto all source actions for that target
    - use action-episode transport

The experiment remains public-free and anchor-free.  It asks whether
HS-JEPA's adapter should be a target-route responsibility system rather than a
single global action listener.
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

from sleep_competition_adapter.action_episode_listener_transport import (  # noqa: E402
    GROUP_MODES,
    NEIGHBORS,
    OUT_DIR as ACTION_EPISODE_OUT,
    THRESHOLDS,
    WEIGHT_MODES,
    apply_policy_to_test,
    feature_columns,
    normalize_action_frame,
    policy_key,
    score_oof_policy,
    subject_summary_from_keep,
    target_summary_from_keep,
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


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "target_route_guarded_action_episode_transport"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "TARGET_ROUTE_GUARDED_ACTION_EPISODE_TRANSPORT_KO.md"


def ensure_inputs() -> None:
    if not WORLD_MODEL_STATE.exists():
        subprocess.run(["python3", str(WORLD_MODEL_SCRIPT)], cwd=ROOT, check=True)


def static_policy_metrics(part: pd.DataFrame, mode: str) -> tuple[dict[str, Any], pd.DataFrame]:
    if mode == "keep_all":
        keep = pd.Series(True, index=part.index)
    elif mode == "veto_all":
        keep = pd.Series(False, index=part.index)
    else:
        raise ValueError(f"unknown static policy mode: {mode}")
    kept = part.loc[keep]
    removed = part.loc[~keep]
    subject_summary = subject_summary_from_keep(part, keep)
    rec = {
        "group_mode": mode,
        "neighbors": 0,
        "weights": "none",
        "threshold": 0.0,
        "oof_original_cells": int(len(part)),
        "oof_original_gain_sum": float(part["true_gain"].sum()),
        "oof_original_positive_gain_rate": float((part["true_gain"] > 0).mean()) if len(part) else 0.0,
        "oof_kept_cells": int(len(kept)),
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "oof_gain_delta": float((kept["true_gain"].sum() if len(kept) else 0.0) - part["true_gain"].sum()),
        "active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
        "positive_subjects": int((subject_summary["improvement_sum"] > 0).sum()) if len(subject_summary) else 0,
        "negative_subjects": int((subject_summary["improvement_sum"] < 0).sum()) if len(subject_summary) else 0,
        "min_subject_improvement": float(subject_summary["improvement_sum"].min()) if len(subject_summary) else 0.0,
        "mean_predicted_gain": 0.0,
        "policy_key": mode,
    }
    audit = part[["cell_key", "subject_id", "target", "action_family", "action_expert", "true_gain"]].copy()
    audit["predicted_gain"] = 0.0
    audit["neighbor_positive_rate"] = 0.0
    audit["neighbor_count"] = 0
    audit["neighbor_subjects"] = ""
    audit["mean_distance"] = np.nan
    audit["keep"] = keep.to_numpy(dtype=bool)
    audit["policy_key"] = mode
    return rec, audit


def guarded_score(row: pd.Series) -> float:
    return (
        float(row["oof_gain_delta"])
        - 0.30 * max(0.0, -float(row["min_subject_improvement"]))
        - 0.08 * float(row["negative_subjects"])
        + 0.03 * float(row["positive_subjects"])
    )


def target_policy_board(part: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    metrics: list[dict[str, Any]] = []
    audits: dict[str, pd.DataFrame] = {}
    for mode in ["keep_all", "veto_all"]:
        rec, audit = static_policy_metrics(part, mode)
        metrics.append(rec)
        audits[mode] = audit
    for group_mode in GROUP_MODES:
        for neighbors in NEIGHBORS:
            for weights in WEIGHT_MODES:
                for threshold in THRESHOLDS:
                    rec, audit = score_oof_policy(part, cols, group_mode, neighbors, weights, threshold)
                    key = policy_key(rec)
                    rec["policy_key"] = key
                    metrics.append(rec)
                    audits[key] = audit
    board = pd.DataFrame(metrics)
    board["guarded_score"] = board.apply(guarded_score, axis=1)
    return board.sort_values(
        ["guarded_score", "oof_gain_delta", "positive_subjects", "negative_subjects"],
        ascending=[False, False, False, True],
        kind="mergesort",
    ).reset_index(drop=True), audits


def choose_target_policy(board: pd.DataFrame) -> pd.Series:
    best = board.iloc[0]
    if str(best["policy_key"]) != "keep_all" and float(best["guarded_score"]) > 0 and float(best["oof_gain_delta"]) > 0:
        return best
    return board[board["policy_key"].eq("keep_all")].iloc[0]


def learn_target_guards(oof: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rules: list[dict[str, Any]] = []
    detail: list[pd.DataFrame] = []
    audits: list[pd.DataFrame] = []
    for target in TARGETS:
        part = oof[oof["target"].eq(target)].copy()
        if part.empty:
            continue
        board, audit_map = target_policy_board(part, cols)
        board["target"] = target
        detail.append(board)
        selected = choose_target_policy(board)
        key = str(selected["policy_key"])
        audit = audit_map[key].copy()
        audit["target_policy_key"] = key
        audits.append(audit)
        rules.append(
            {
                "target": target,
                "policy_key": key,
                "group_mode": str(selected["group_mode"]),
                "neighbors": int(selected["neighbors"]),
                "weights": str(selected["weights"]),
                "threshold": float(selected["threshold"]),
                "guarded_score": float(selected["guarded_score"]),
                "oof_gain_delta": float(selected["oof_gain_delta"]),
                "oof_kept_gain_sum": float(selected["oof_kept_gain_sum"]),
                "oof_removed_gain_sum": float(selected["oof_removed_gain_sum"]),
                "positive_subjects": int(selected["positive_subjects"]),
                "negative_subjects": int(selected["negative_subjects"]),
                "min_subject_improvement": float(selected["min_subject_improvement"]),
            }
        )
    return pd.DataFrame(rules), pd.concat(detail, ignore_index=True), pd.concat(audits, ignore_index=True)


def apply_target_guards_to_oof(oof: pd.DataFrame, audit: pd.DataFrame) -> pd.Series:
    keep = pd.Series(True, index=oof.index)
    keyed = audit.set_index("cell_key")
    for idx, row in oof.iterrows():
        rec = keyed.loc[row["cell_key"]]
        keep.loc[idx] = bool(rec["keep"])
    return keep.astype(bool)


def apply_target_guards_to_test(test: pd.DataFrame, oof: pd.DataFrame, cols: list[str], rules: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    keep = pd.Series(True, index=test.index)
    audit_rows: list[pd.DataFrame] = []
    for _, rule in rules.iterrows():
        target = str(rule["target"])
        idx = test[test["target"].eq(target)].index
        if len(idx) == 0:
            continue
        policy = rule.to_dict()
        policy["policy_key"] = str(rule["policy_key"])
        if str(rule["policy_key"]) == "keep_all":
            keep.loc[idx] = True
            continue
        if str(rule["policy_key"]) == "veto_all":
            keep.loc[idx] = False
            tmp = test.loc[idx, ["cell_key", "subject_id", "target", "action_family", "action_expert"]].copy()
            tmp["keep"] = False
            tmp["predicted_gain"] = 0.0
            tmp["neighbor_positive_rate"] = 0.0
            tmp["neighbor_count"] = 0
            tmp["neighbor_subjects"] = ""
            tmp["policy_key"] = "veto_all"
            audit_rows.append(tmp)
            continue
        part_test = test.loc[idx].copy()
        part_oof = oof[oof["target"].eq(target)].copy()
        part_keep, neighbor_audit = apply_policy_to_test(part_test, part_oof, cols, pd.Series(policy))
        keep.loc[idx] = part_keep.to_numpy(dtype=bool)
        neighbor_audit["policy_key"] = str(rule["policy_key"])
        audit_rows.append(neighbor_audit)
    audit = pd.concat(audit_rows, ignore_index=True) if audit_rows else pd.DataFrame()
    return keep.astype(bool), audit


def summarize_keep(frame: pd.DataFrame, keep: pd.Series) -> dict[str, Any]:
    kept = frame.loc[keep]
    removed = frame.loc[~keep]
    subject = subject_summary_from_keep(frame, keep)
    return {
        "oof_original_cells": int(len(frame)),
        "oof_original_gain_sum": float(frame["true_gain"].sum()),
        "oof_original_positive_gain_rate": float((frame["true_gain"] > 0).mean()) if len(frame) else 0.0,
        "oof_kept_cells": int(len(kept)),
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "oof_gain_delta": float((kept["true_gain"].sum() if len(kept) else 0.0) - frame["true_gain"].sum()),
        "active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
        "positive_subjects": int((subject["improvement_sum"] > 0).sum()) if len(subject) else 0,
        "negative_subjects": int((subject["improvement_sum"] < 0).sum()) if len(subject) else 0,
        "min_subject_improvement": float(subject["improvement_sum"].min()) if len(subject) else 0.0,
    }


def test_counts(test_audit: pd.DataFrame) -> pd.DataFrame:
    switched = test_audit[test_audit["switched"].astype(bool)].copy()
    return (
        switched.groupby("target", observed=True)
        .agg(switched=("switched", "size"), kept=("world_model_keep", "sum"), vetoed=("vetoed", "sum"))
        .reset_index()
    )


def build_markdown(
    readout: dict[str, Any],
    rules: pd.DataFrame,
    detail: pd.DataFrame,
    subject_summary: pd.DataFrame,
    target_summary: pd.DataFrame,
    counts: pd.DataFrame,
) -> str:
    return f"""# Target-Route Guarded Action-Episode Transport

## 한 줄 요약

전역 action-episode transport를 target별 route guard로 분해했다.
S3처럼 transport가 살아나는 route는 믿고, S4처럼 손실이 나는 route는 별도 veto/guard를 허용한다.

```text
target-specific route guard
  -> keep all / veto all / action-episode transport
  -> row-target action responsibility
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 target-route action decoder로 번역하는 adapter다.
전역 action listener가 서로 다른 target noise/action regime을 섞는 문제를 해결하기 위해,
listener responsibility를 target별로 분해한다.

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Learned Target Guards

{markdown_table(rules, ["target", "policy_key", "guarded_score", "oof_gain_delta", "oof_removed_gain_sum", "positive_subjects", "negative_subjects", "min_subject_improvement"], max_rows=20)}

## OOF Result

- verdict: `{readout["verdict"]}`
- original gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- kept gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- OOF gain delta: `{readout["oof_gain_delta"]:.6f}`
- removed action gain sum: `{readout["oof_removed_gain_sum"]:.6f}`
- positive subjects: `{readout["positive_subjects"]}`
- negative subjects: `{readout["negative_subjects"]}`

Subject summary:

{markdown_table(subject_summary, ["subject_id", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

Target summary:

{markdown_table(target_summary, ["target", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

Top target policy alternatives:

{markdown_table(detail, ["target", "policy_key", "guarded_score", "oof_gain_delta", "oof_kept_gain_sum", "oof_removed_gain_sum"], max_rows=30)}

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
전역 action-episode transport의 S3 positive signal을 유지하면서 S4 손실을 제거한다.
```

실패 조건:

```text
target별 guard가 OOF gain을 늘리지 못하거나, 지나치게 veto_all로 collapse한다.
```

이 실험은 HS-JEPA adapter를 더 일반화한다.
core representation 자체보다 중요한 것은 target별 listener responsibility의 위치를 찾는 것이다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inputs()
    spec = release_spec()
    actions, source_metric = reconstruct_release_oof_actions(spec)
    world_state = pd.read_csv(WORLD_MODEL_STATE)
    _ = energy_columns(world_state)
    oof = normalize_action_frame(attach_world_model_state(actions, world_state, "train"))
    cols = feature_columns(oof)
    rules, detail, audit = learn_target_guards(oof, cols)
    keep = apply_target_guards_to_oof(oof, audit)
    oof["target_route_guard_keep"] = keep.to_numpy(dtype=bool)
    subject_summary = subject_summary_from_keep(oof, keep)
    target_summary = target_summary_from_keep(oof, keep)

    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test = normalize_action_frame(attach_world_model_state(test_actions, world_state, "test"))
    test_keep, test_neighbor_audit = apply_target_guards_to_test(test, oof, cols, rules)
    candidate, test_audit = build_candidate(test, test_keep)
    validation = validate_submission(candidate, read_sample())
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_target_route_guarded_action_episode_transport_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    counts = test_counts(test_audit)

    metrics = summarize_keep(oof, keep)
    if float(metrics["oof_gain_delta"]) > 0 and int(metrics["positive_subjects"]) >= int(metrics["negative_subjects"]):
        verdict = "target_route_guard_positive"
    elif float(metrics["oof_gain_delta"]) > 0:
        verdict = "target_route_guard_oof_positive_subject_mixed"
    else:
        verdict = "target_route_guard_negative_or_inconclusive"
    readout = {
        "package": "target_route_guarded_action_episode_transport",
        "status": "adapter_diagnostic_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "source_metric": source_metric.iloc[0].to_dict() if len(source_metric) else {},
        **metrics,
        "test_original_switched_cells": int(test_audit["switched"].astype(bool).sum()),
        "test_kept_switched_cells": int((test_audit["switched"].astype(bool) & test_audit["world_model_keep"]).sum()),
        "test_vetoed_switched_cells": int(test_audit["vetoed"].sum()),
        "candidate_file": candidate_file,
        "validation": validation,
        "verdict": verdict,
        "worldview": (
            "HS-JEPA action responsibility should be target-route specific: S3-like "
            "action episodes can use transport while S4-like routes need a guard."
        ),
    }

    rules.to_csv(OUT_DIR / "target_route_guard_rules.csv", index=False)
    detail.to_csv(OUT_DIR / "target_route_guard_policy_detail.csv", index=False)
    audit.to_csv(OUT_DIR / "target_route_guard_oof_neighbor_audit.csv", index=False)
    oof.to_csv(OUT_DIR / "target_route_guard_oof_action_audit.csv", index=False)
    subject_summary.to_csv(OUT_DIR / "target_route_guard_subject_summary.csv", index=False)
    target_summary.to_csv(OUT_DIR / "target_route_guard_target_summary.csv", index=False)
    test_neighbor_audit.to_csv(OUT_DIR / "target_route_guard_test_neighbor_audit.csv", index=False)
    test_audit.to_csv(OUT_DIR / "target_route_guard_test_action_audit.csv", index=False)
    counts.to_csv(OUT_DIR / "target_route_guard_test_summary.csv", index=False)
    (OUT_DIR / "target_route_guarded_action_episode_transport_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, rules, detail, subject_summary, target_summary, counts)
    (OUT_DIR / "TARGET_ROUTE_GUARDED_ACTION_EPISODE_TRANSPORT_KO.md").write_text(
        md.rstrip() + "\n",
        encoding="utf-8",
    )
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
