#!/usr/bin/env python3
"""Action-episode listener responsibility transport for HS-JEPA.

Subject-level cohort transport failed because averaged subject fingerprints are
too coarse for row-target action responsibility.  This experiment moves the
transport unit to the action episode:

    similar target + action route + world-model residual geometry
    -> peer action gain
    -> keep/veto the current row-target action.

The solver is public-free:
    - no public LB ledger
    - no prior submission probabilities
    - no proprietary embedding API

It tests whether HS-JEPA core residual geometry becomes useful when combined
with route/action context rather than subject averages.
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
    reconstruct_release_oof_actions,
    release_spec,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "action_episode_listener_transport"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ACTION_EPISODE_LISTENER_TRANSPORT_KO.md"
NEIGHBORS = [1, 3, 5, 7, 11]
THRESHOLDS = [-0.10, -0.05, 0.0, 0.05, 0.10]
GROUP_MODES = ["target_expert", "target_family", "target"]
WEIGHT_MODES = ["uniform", "distance"]


def ensure_inputs() -> None:
    if not WORLD_MODEL_STATE.exists():
        subprocess.run(["python3", str(WORLD_MODEL_SCRIPT)], cwd=ROOT, check=True)


def normalize_action_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "expert_family" in out.columns:
        out["action_family"] = out["expert_family"].astype(str)
    elif "candidate_family" in out.columns:
        out["action_family"] = out["candidate_family"].astype(str)
    else:
        out["action_family"] = "unknown"
    out["action_expert"] = out.get("selected_expert", pd.Series("unknown", index=out.index)).astype(str)
    out["action_delta"] = pd.to_numeric(out["selected_pred"], errors="coerce") - pd.to_numeric(out["raw_pred"], errors="coerce")
    out["abs_action_delta"] = out["action_delta"].abs()
    out["action_direction"] = np.sign(out["action_delta"].to_numpy(dtype=float))
    return out


def feature_columns(frame: pd.DataFrame) -> list[str]:
    cols = [
        "selection_score",
        "raw_pred",
        "selected_pred",
        "action_delta",
        "abs_action_delta",
    ]
    cols.extend([col for col in frame.columns if col.startswith("wm_energy_")])
    return [col for col in cols if col in frame.columns and pd.api.types.is_numeric_dtype(frame[col])]


def standardizer(reference: pd.DataFrame, cols: list[str]) -> tuple[pd.Series, pd.Series]:
    mean = reference[cols].mean()
    std = reference[cols].std(ddof=0).replace(0, 1.0).fillna(1.0)
    return mean, std


def standardized_matrix(frame: pd.DataFrame, cols: list[str], mean: pd.Series, std: pd.Series) -> np.ndarray:
    z = (frame[cols] - mean) / std
    return z.replace([np.inf, -np.inf], 0.0).fillna(0.0).to_numpy(dtype=float)


def group_pool(reference: pd.DataFrame, query: pd.Series, group_mode: str) -> pd.DataFrame:
    pool = reference[reference["target"].astype(str).eq(str(query["target"]))].copy()
    if group_mode == "target_expert":
        strict = pool[
            pool["action_family"].astype(str).eq(str(query["action_family"]))
            & pool["action_expert"].astype(str).eq(str(query["action_expert"]))
        ]
        if len(strict):
            return strict
        family = pool[pool["action_family"].astype(str).eq(str(query["action_family"]))]
        return family if len(family) else pool
    if group_mode == "target_family":
        family = pool[pool["action_family"].astype(str).eq(str(query["action_family"]))]
        return family if len(family) else pool
    if group_mode == "target":
        return pool
    raise ValueError(f"unknown group_mode: {group_mode}")


def predict_gain_for_row(
    reference: pd.DataFrame,
    query: pd.Series,
    cols: list[str],
    mean: pd.Series,
    std: pd.Series,
    group_mode: str,
    neighbors: int,
    weights: str,
    exclude_subject: str | None = None,
) -> dict[str, Any]:
    pool = group_pool(reference, query, group_mode)
    if exclude_subject is not None:
        pool = pool[~pool["subject_id"].astype(str).eq(str(exclude_subject))]
    if pool.empty:
        return {
            "predicted_gain": 0.0,
            "neighbor_positive_rate": 0.0,
            "neighbor_count": 0,
            "neighbor_subjects": "",
            "mean_distance": np.nan,
        }
    q = standardized_matrix(pd.DataFrame([query]), cols, mean, std)[0]
    matrix = standardized_matrix(pool, cols, mean, std)
    distances = np.sqrt(((matrix - q) ** 2).sum(axis=1))
    order = np.argsort(distances, kind="mergesort")[: min(neighbors, len(pool))]
    near = pool.iloc[order].copy()
    near_dist = distances[order]
    gains = pd.to_numeric(near["true_gain"], errors="coerce").to_numpy(dtype=float)
    if weights == "distance":
        w = 1.0 / (near_dist + 1e-6)
        predicted_gain = float(np.sum(w * gains) / np.sum(w))
    elif weights == "uniform":
        predicted_gain = float(np.mean(gains))
    else:
        raise ValueError(f"unknown weights: {weights}")
    return {
        "predicted_gain": predicted_gain,
        "neighbor_positive_rate": float((gains > 0).mean()) if len(gains) else 0.0,
        "neighbor_count": int(len(near)),
        "neighbor_subjects": ",".join(sorted(near["subject_id"].astype(str).unique())),
        "mean_distance": float(np.mean(near_dist)) if len(near_dist) else np.nan,
    }


def score_oof_policy(
    oof: pd.DataFrame,
    cols: list[str],
    group_mode: str,
    neighbors: int,
    weights: str,
    threshold: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    mean, std = standardizer(oof, cols)
    rows: list[dict[str, Any]] = []
    keep_values: list[bool] = []
    for idx, row in oof.iterrows():
        pred = predict_gain_for_row(
            oof,
            row,
            cols,
            mean,
            std,
            group_mode,
            neighbors,
            weights,
            exclude_subject=str(row["subject_id"]),
        )
        keep = bool(pred["predicted_gain"] > threshold)
        keep_values.append(keep)
        rows.append(
            {
                "cell_key": row["cell_key"],
                "row_index": int(idx),
                "subject_id": row["subject_id"],
                "target": row["target"],
                "action_family": row["action_family"],
                "action_expert": row["action_expert"],
                "true_gain": float(row["true_gain"]),
                "keep": keep,
                "group_mode": group_mode,
                "neighbors": neighbors,
                "weights": weights,
                "threshold": threshold,
                **pred,
            }
        )
    keep = pd.Series(keep_values, index=oof.index, dtype=bool)
    kept = oof.loc[keep]
    removed = oof.loc[~keep]
    subject_summary = subject_summary_from_keep(oof, keep)
    metrics = {
        "group_mode": group_mode,
        "neighbors": neighbors,
        "weights": weights,
        "threshold": threshold,
        "oof_original_cells": int(len(oof)),
        "oof_original_gain_sum": float(oof["true_gain"].sum()),
        "oof_original_positive_gain_rate": float((oof["true_gain"] > 0).mean()),
        "oof_kept_cells": int(len(kept)),
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "oof_gain_delta": float((kept["true_gain"].sum() if len(kept) else 0.0) - oof["true_gain"].sum()),
        "active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
        "positive_subjects": int((subject_summary["improvement_sum"] > 0).sum()) if len(subject_summary) else 0,
        "negative_subjects": int((subject_summary["improvement_sum"] < 0).sum()) if len(subject_summary) else 0,
        "min_subject_improvement": float(subject_summary["improvement_sum"].min()) if len(subject_summary) else 0.0,
        "mean_predicted_gain": float(pd.DataFrame(rows)["predicted_gain"].mean()) if rows else 0.0,
    }
    return metrics, pd.DataFrame(rows)


def subject_summary_from_keep(oof: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
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


def target_summary_from_keep(oof: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
    tmp = oof.copy()
    tmp["keep"] = keep.to_numpy(dtype=bool)
    rows: list[dict[str, Any]] = []
    for target, part in tmp.groupby("target", observed=True):
        kept = part[part["keep"]]
        rows.append(
            {
                "target": target,
                "all_cells": int(len(part)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(part["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "improvement_sum": float((kept["true_gain"].sum() if len(kept) else 0.0) - part["true_gain"].sum()),
            }
        )
    return pd.DataFrame(rows)


def policy_board(oof: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    metrics: list[dict[str, Any]] = []
    audits: dict[str, pd.DataFrame] = {}
    for group_mode in GROUP_MODES:
        for neighbors in NEIGHBORS:
            for weights in WEIGHT_MODES:
                for threshold in THRESHOLDS:
                    rec, audit = score_oof_policy(oof, cols, group_mode, neighbors, weights, threshold)
                    key = policy_key(rec)
                    metrics.append(rec | {"policy_key": key})
                    audits[key] = audit
    board = pd.DataFrame(metrics)
    board = board.sort_values(
        ["oof_gain_delta", "positive_subjects", "negative_subjects", "oof_kept_positive_gain_rate"],
        ascending=[False, False, True, False],
        kind="mergesort",
    ).reset_index(drop=True)
    return board, audits


def policy_key(policy: dict[str, Any] | pd.Series) -> str:
    return (
        f"{policy['group_mode']}__knn{int(policy['neighbors'])}__"
        f"{policy['weights']}__thr{float(policy['threshold']):.2f}"
    )


def choose_policy(board: pd.DataFrame) -> pd.Series:
    positive = board[
        board["oof_gain_delta"].gt(0)
        & board["active_subjects"].ge(3)
        & board["positive_subjects"].ge(board["negative_subjects"])
    ]
    if len(positive):
        return positive.iloc[0]
    weak = board[board["oof_gain_delta"].gt(0)]
    if len(weak):
        return weak.iloc[0]
    return board.iloc[0]


def apply_policy_to_test(test: pd.DataFrame, reference: pd.DataFrame, cols: list[str], policy: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    mean, std = standardizer(reference, cols)
    keep = pd.Series(True, index=test.index)
    rows: list[dict[str, Any]] = []
    switched = test[test["switched"].astype(bool)].copy()
    for idx, row in switched.iterrows():
        pred = predict_gain_for_row(
            reference,
            row,
            cols,
            mean,
            std,
            str(policy["group_mode"]),
            int(policy["neighbors"]),
            str(policy["weights"]),
            exclude_subject=None,
        )
        decision = bool(pred["predicted_gain"] > float(policy["threshold"]))
        keep.loc[idx] = decision
        rows.append(
            {
                "cell_key": row["cell_key"],
                "row_index": int(idx),
                "subject_id": row["subject_id"],
                "target": row["target"],
                "action_family": row["action_family"],
                "action_expert": row["action_expert"],
                "keep": decision,
                **pred,
            }
        )
    return keep.astype(bool), pd.DataFrame(rows)


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
    oof_audit: pd.DataFrame,
    subject_summary: pd.DataFrame,
    target_summary: pd.DataFrame,
    counts: pd.DataFrame,
) -> str:
    return f"""# Action-Episode Listener Transport

## 한 줄 요약

Subject 평균 fingerprint가 아니라, 비슷한 row-target action episode에서 listener responsibility를 전이했다.

```text
target + action route + HS-JEPA world-model residual geometry
  -> peer action gain
  -> keep/veto current row-target action
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 action responsibility로 번역하는 adapter다.
직전 cohort 실험이 subject 평균 fingerprint에서 실패했기 때문에, responsibility의 단위를
subject에서 action episode로 낮췄다.

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Policy Leaderboard

{markdown_table(board, ["policy_key", "oof_gain_delta", "oof_kept_gain_sum", "oof_removed_gain_sum", "active_subjects", "positive_subjects", "negative_subjects", "min_subject_improvement"], max_rows=20)}

## Release Policy

- policy: `{readout["release_policy_key"]}`
- verdict: `{readout["verdict"]}`
- original OOF gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- kept OOF gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- OOF gain delta: `{readout["oof_gain_delta"]:.6f}`
- positive subjects: `{readout["positive_subjects"]}`
- negative subjects: `{readout["negative_subjects"]}`

## OOF Action-Episode Audit

{markdown_table(oof_audit, ["cell_key", "subject_id", "target", "action_family", "true_gain", "predicted_gain", "neighbor_positive_rate", "keep"], max_rows=24)}

Subject summary:

{markdown_table(subject_summary, ["subject_id", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

Target summary:

{markdown_table(target_summary, ["target", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "improvement_sum"], max_rows=20)}

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
row-target action episode geometry가 peer action gain을 예측해 toxic actions를 제거한다.
```

실패 조건:

```text
route/action/residual geometry를 넣어도 peer action gain이 전이되지 않는다.
```

이 실험은 HS-JEPA의 adapter claim을 더 정확히 찌른다.
core residual 자체보다 중요한 것은, 그 residual이 어떤 action route에서 어떤 책임을 가져야 하는지다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inputs()
    spec = release_spec()
    actions, source_metric = reconstruct_release_oof_actions(spec)
    world_state = pd.read_csv(WORLD_MODEL_STATE)
    score_cols = energy_columns(world_state)
    oof = normalize_action_frame(attach_world_model_state(actions, world_state, "train"))
    cols = feature_columns(oof)
    board, audits = policy_board(oof, cols)
    policy = choose_policy(board)
    selected_key = str(policy["policy_key"])
    oof_audit = audits[selected_key].copy()
    keep = pd.Series(oof_audit["keep"].to_numpy(dtype=bool), index=oof.index)
    subject_summary = subject_summary_from_keep(oof, keep)
    target_summary = target_summary_from_keep(oof, keep)

    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test = normalize_action_frame(attach_world_model_state(test_actions, world_state, "test"))
    test_keep, test_neighbor_audit = apply_policy_to_test(test, oof, cols, policy)
    candidate, test_audit = build_candidate(test, test_keep)
    validation = validate_submission(candidate, read_sample())
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_action_episode_listener_transport_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)
    counts = test_counts(test_audit)

    selected = policy.to_dict()
    if float(selected["oof_gain_delta"]) > 0 and int(selected["positive_subjects"]) >= int(selected["negative_subjects"]):
        verdict = "action_episode_transport_positive"
    elif float(selected["oof_gain_delta"]) > 0:
        verdict = "action_episode_transport_oof_positive_subject_mixed"
    else:
        verdict = "action_episode_transport_negative_or_inconclusive"

    readout = {
        "package": "action_episode_listener_transport",
        "status": "adapter_diagnostic_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "source_metric": source_metric.iloc[0].to_dict() if len(source_metric) else {},
        "release_policy_key": selected_key,
        "group_mode": str(selected["group_mode"]),
        "neighbors": int(selected["neighbors"]),
        "weights": str(selected["weights"]),
        "threshold": float(selected["threshold"]),
        "oof_original_cells": int(selected["oof_original_cells"]),
        "oof_original_gain_sum": float(selected["oof_original_gain_sum"]),
        "oof_kept_cells": int(selected["oof_kept_cells"]),
        "oof_kept_gain_sum": float(selected["oof_kept_gain_sum"]),
        "oof_removed_cells": int(selected["oof_removed_cells"]),
        "oof_removed_gain_sum": float(selected["oof_removed_gain_sum"]),
        "oof_gain_delta": float(selected["oof_gain_delta"]),
        "active_subjects": int(selected["active_subjects"]),
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
            "HS-JEPA residual geometry should transport action responsibility at the "
            "row-target action-episode level, not at the averaged subject level."
        ),
    }

    board.to_csv(OUT_DIR / "action_episode_policy_board.csv", index=False)
    oof_audit.to_csv(OUT_DIR / "action_episode_oof_neighbor_audit.csv", index=False)
    subject_summary.to_csv(OUT_DIR / "action_episode_subject_summary.csv", index=False)
    target_summary.to_csv(OUT_DIR / "action_episode_target_summary.csv", index=False)
    test_neighbor_audit.to_csv(OUT_DIR / "action_episode_test_neighbor_audit.csv", index=False)
    test_audit.to_csv(OUT_DIR / "action_episode_test_action_audit.csv", index=False)
    counts.to_csv(OUT_DIR / "action_episode_test_summary.csv", index=False)
    (OUT_DIR / "action_episode_listener_transport_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, board, oof_audit, subject_summary, target_summary, counts)
    (OUT_DIR / "ACTION_EPISODE_LISTENER_TRANSPORT_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
