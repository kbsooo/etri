#!/usr/bin/env python3
"""Target-route conservation decoder for HS-JEPA listener-conditioned support.

The listener-conditioned core showed strong action-support signal, but the
global top-k release still mixed good routes (Q2/S2/S3/S4) with toxic pockets
(notably S1).  This script tests the next architecture step:

    hidden world-state residual/energy
      -> target listener interaction
      -> target-route conservation gate
      -> anchor-free correction sensor

Everything is train-only / public-free.  The gate chooses target-specific
release, inverse-toxic, or no-action policies using OOF realized gain, subject
balance, and target-shuffle stress.  No public LB ledger or prior submission
probability is used.

This file intentionally lives in ``sleep_competition_adapter/`` rather than
``hsjepa_core/``.  The masked world-state representation is HS-JEPA core, but
Q1/Q2/Q3/S1/S2/S3/S4 route policy selection and upload-safe CSV materialization
are competition adapter responsibilities.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import (  # noqa: E402
    NEIGHBORS,
    RANDOM_SEED,
    TARGETS,
    append_row_features,
    fit_support_models,
    knn_probability_field,
    make_action_cell_table,
    make_test_action_table,
    target_context_columns,
    validate_submission,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    catalog_features,
    finite_matrix,
    format_float,
    load_frames,
    markdown_table,
)
from hsjepa_core.run_listener_conditioned_action_support_core import (  # noqa: E402
    add_listener_interactions,
    state_feature_columns,
)
from hsjepa_core.run_masked_context_world_model import build_world_model_state  # noqa: E402


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "target_route_conservation_decoder"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "TARGET_ROUTE_CONSERVATION_DECODER_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
NULL_REPEATS = 64
LISTENER_GLOBAL_GAIN_REFERENCE = 6.192500093739957


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def route_family(target: str) -> str:
    if target in {"Q2", "S2"}:
        return "intervention_stage_bridge"
    if target in {"S3", "S4"}:
        return "objective_tail_bridge"
    if target == "S1":
        return "objective_s1_toxic_watch"
    return "subjective_q_shadow"


def build_listener_cells() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float], pd.DataFrame]:
    frame, _ = load_frames()
    frame = frame.copy()
    state, view_metrics, _pred_cols, _energy_cols = build_world_model_state(frame)
    catalog = catalog_features(frame)
    raw_cols = [col for col in catalog.raw_numeric if col in frame.columns]

    train = frame[frame["split"].eq("train")].reset_index(drop=True)
    test = frame[frame["split"].eq("test")].reset_index(drop=True)
    state_train = state[state["split"].eq("train")].reset_index(drop=True)
    state_test = state[state["split"].eq("test")].reset_index(drop=True)
    groups = train["subject_id"].astype(str).to_numpy()

    raw_oof, raw_test_field = knn_probability_field(
        train,
        test,
        finite_matrix(train, raw_cols),
        finite_matrix(test, raw_cols),
        groups,
        NEIGHBORS,
    )
    raw_cells = make_action_cell_table(train, raw_oof, "raw_lifelog_memory")
    train_cells = raw_cells.copy()

    sfc = state_feature_columns(state)
    state_cols = sorted(set(sfc["resid_energy"]))
    train_cells = append_row_features(train_cells, state_train[["metric_row"] + state_cols], state_cols)

    train_priors = train[TARGETS].astype(float).mean().to_dict()
    test_cells = make_test_action_table(test, raw_test_field, train_priors, "raw_lifelog_memory")
    test_cells = append_row_features(test_cells, state_test[["metric_row"] + state_cols], state_cols)

    train_cells, test_cells, interaction_cols = add_listener_interactions(train_cells, test_cells, state_cols)
    action_cols = ["action_move", "abs_action_move", "action_move_rank"]
    target_cols = target_context_columns()
    feature_map = {
        "target_interaction_world_residual_energy": target_cols
        + action_cols
        + state_cols
        + interaction_cols["target_interaction"],
        "target_action_only": target_cols + action_cols,
    }
    _metrics, oof_predictions, test_predictions = fit_support_models(train_cells, test_cells, feature_map)
    score_col = "support_score_target_interaction_world_residual_energy"
    train_cells[score_col] = oof_predictions[score_col].to_numpy(dtype=np.float64)
    test_cells[score_col] = test_predictions[score_col].to_numpy(dtype=np.float64)
    train_cells["target_route_family"] = train_cells["target"].map(route_family)
    test_cells["target_route_family"] = test_cells["target"].map(route_family)
    return train_cells, test_cells, train_priors, view_metrics


def select_indices(part: pd.DataFrame, score_col: str, policy: str, fraction: float) -> np.ndarray:
    if policy == "hold":
        return np.array([], dtype=int)
    frame = part
    if "decisive" in policy:
        frame = frame[frame["decisive_action"].eq(1)]
    if frame.empty:
        return np.array([], dtype=int)
    k = max(1, int(round(len(frame) * fraction)))
    ascending = policy.startswith("inverse_low")
    return frame.sort_values(score_col, ascending=ascending, kind="mergesort").head(k).index.to_numpy()


def evaluate_route_policy(
    cells: pd.DataFrame,
    target: str,
    score_col: str,
    policy: str,
    fraction: float,
    null_repeats: int = NULL_REPEATS,
) -> dict[str, Any]:
    part = cells[cells["target"].eq(target)]
    selected = select_indices(part, score_col, policy, fraction)
    decoder = "none" if policy == "hold" else ("inverse_toxic_memory" if policy.startswith("inverse_low") else "raw_memory_release")
    gain_col = "inverse_realized_gain" if decoder == "inverse_toxic_memory" else "realized_gain"
    if len(selected) == 0:
        selected_gain = np.array([], dtype=np.float64)
        subject_gain = pd.Series(dtype=float)
    else:
        selected_gain = cells.loc[selected, gain_col].to_numpy(dtype=np.float64)
        subject_gain = cells.loc[selected].groupby("subject_id", observed=True)[gain_col].sum()

    rng = np.random.default_rng(RANDOM_SEED + int(hashlib.sha256(f"{target}:{policy}:{fraction}".encode()).hexdigest()[:8], 16) % 1009)
    null_sums = []
    if len(selected) > 0:
        scores = part[score_col].to_numpy(dtype=np.float64)
        for _ in range(null_repeats):
            shuffled = scores.copy()
            rng.shuffle(shuffled)
            shuffled_part = part.copy()
            shuffled_part[score_col] = shuffled
            shuffled_idx = select_indices(shuffled_part, score_col, policy, fraction)
            null_sums.append(float(cells.loc[shuffled_idx, gain_col].sum()) if len(shuffled_idx) else 0.0)
    null_mean = float(np.mean(null_sums)) if null_sums else 0.0
    null_std = float(np.std(null_sums, ddof=1)) if len(null_sums) > 1 else np.nan
    selected_gain_sum = float(selected_gain.sum()) if len(selected_gain) else 0.0
    positive_rate = float((selected_gain > 0).mean()) if len(selected_gain) else np.nan
    negative_subjects = int((subject_gain < 0).sum()) if len(subject_gain) else 0
    positive_subjects = int((subject_gain > 0).sum()) if len(subject_gain) else 0
    active_subjects = int(len(subject_gain))
    route_family_name = route_family(target)
    conservation_score = (
        selected_gain_sum
        + 0.30 * (selected_gain_sum - null_mean)
        + 0.20 * (0.0 if not np.isfinite(null_std) or null_std == 0 else (selected_gain_sum - null_mean) / null_std)
        + 0.50 * max(positive_rate if np.isfinite(positive_rate) else 0.0, 0.0)
        - 0.65 * negative_subjects
    )
    return {
        "target": target,
        "target_route_family": route_family_name,
        "policy": policy,
        "decoder_action": decoder,
        "fraction": fraction,
        "selected_cells": int(len(selected)),
        "selected_gain_sum": selected_gain_sum,
        "selected_mean_gain": float(selected_gain.mean()) if len(selected_gain) else 0.0,
        "selected_positive_gain_rate": positive_rate,
        "active_subjects": active_subjects,
        "positive_subjects": positive_subjects,
        "negative_subjects": negative_subjects,
        "min_subject_gain": float(subject_gain.min()) if len(subject_gain) else 0.0,
        "null_gain_mean": null_mean,
        "null_gain_std": null_std,
        "gain_lift_vs_null": selected_gain_sum - null_mean,
        "gain_z_vs_null": (selected_gain_sum - null_mean) / null_std if np.isfinite(null_std) and null_std else np.nan,
        "conservation_score": conservation_score,
    }


def route_policy_grid(cells: pd.DataFrame, score_col: str) -> pd.DataFrame:
    rows = []
    fractions = [0.02, 0.04, 0.06, 0.08, 0.10, 0.14, 0.18, 0.25]
    for target in TARGETS:
        rows.append(evaluate_route_policy(cells, target, score_col, "hold", 0.0))
        for fraction in fractions:
            rows.append(evaluate_route_policy(cells, target, score_col, "release_high_all", fraction))
            rows.append(evaluate_route_policy(cells, target, score_col, "release_high_decisive", fraction))
            rows.append(evaluate_route_policy(cells, target, score_col, "inverse_low_decisive", fraction))
    return pd.DataFrame(rows)


def choose_conserved_routes(grid: pd.DataFrame) -> pd.DataFrame:
    chosen = []
    for target, part in grid.groupby("target", observed=True):
        non_hold = part[~part["policy"].eq("hold")].copy()
        viable = non_hold[
            (non_hold["selected_gain_sum"] > 0.0)
            & (non_hold["gain_lift_vs_null"] > 0.0)
            & (non_hold["selected_positive_gain_rate"].fillna(0.0) >= 0.58)
            & (non_hold["negative_subjects"] <= 3)
        ].copy()
        if viable.empty:
            row = part[part["policy"].eq("hold")].iloc[0].to_dict()
            row["accepted"] = False
            row["accept_reason"] = "no_policy_passed_conservation_gate"
            chosen.append(row)
        else:
            row = viable.sort_values(["conservation_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()
            row["accepted"] = True
            row["accept_reason"] = "positive_gain_null_lift_subject_balance"
            chosen.append(row)
    return pd.DataFrame(chosen).sort_values("target")


def apply_conserved_routes_to_oof(cells: pd.DataFrame, chosen: pd.DataFrame, score_col: str) -> pd.DataFrame:
    selected_mask = pd.Series(False, index=cells.index)
    decoder = pd.Series("none", index=cells.index, dtype=object)
    for _, route in chosen.iterrows():
        if not bool(route["accepted"]):
            continue
        part = cells[cells["target"].eq(route["target"])]
        idx = select_indices(part, score_col, str(route["policy"]), float(route["fraction"]))
        selected_mask.loc[idx] = True
        decoder.loc[idx] = str(route["decoder_action"])
    audit = cells.copy()
    audit["released"] = selected_mask.to_numpy()
    audit["decoder_action"] = decoder.to_numpy()
    audit["effective_gain"] = np.where(
        audit["decoder_action"].eq("inverse_toxic_memory"),
        audit["inverse_realized_gain"],
        np.where(audit["decoder_action"].eq("raw_memory_release"), audit["realized_gain"], 0.0),
    )
    return audit


def apply_conserved_routes_to_test(
    sample: pd.DataFrame,
    test_cells: pd.DataFrame,
    chosen: pd.DataFrame,
    score_col: str,
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    selected_mask = pd.Series(False, index=test_cells.index)
    decoder = pd.Series("none", index=test_cells.index, dtype=object)
    for _, route in chosen.iterrows():
        if not bool(route["accepted"]):
            continue
        part = test_cells[test_cells["target"].eq(route["target"])]
        idx = select_indices(part, score_col, str(route["policy"]), float(route["fraction"]))
        selected_mask.loc[idx] = True
        decoder.loc[idx] = str(route["decoder_action"])
    audit = test_cells.copy()
    audit["released"] = selected_mask.to_numpy()
    audit["decoder_action"] = decoder.to_numpy()
    for _, row in audit[audit["released"]].iterrows():
        value_col = "inverse_prob" if row["decoder_action"] == "inverse_toxic_memory" else "candidate_prob"
        out.at[int(row["row"]), str(row["target"])] = float(row[value_col])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def target_summary(oof_audit: pd.DataFrame) -> pd.DataFrame:
    part = oof_audit[oof_audit["released"]].copy()
    if part.empty:
        return pd.DataFrame(columns=["target", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate"])
    return (
        part.groupby("target", observed=True)
        .agg(
            selected_cells=("effective_gain", "size"),
            selected_gain_sum=("effective_gain", "sum"),
            selected_mean_gain=("effective_gain", "mean"),
            selected_positive_gain_rate=("effective_gain", lambda x: float((x > 0).mean())),
            active_subjects=("subject_id", "nunique"),
        )
        .reset_index()
    )


def build_markdown(
    summary: dict[str, Any],
    chosen: pd.DataFrame,
    target_table: pd.DataFrame,
    top_grid: pd.DataFrame,
) -> str:
    return f"""# HS-JEPA Adapter: Target-Route Conservation Decoder

## 한 줄 요약

listener-conditioned HS-JEPA action-support는 강하지만 S1/Q1/Q3 toxic pocket을 섞었다.
이번 실험은 target route별로 release / inverse / hold 정책을 고르고,
OOF gain, subject balance, target-shuffle stress를 통과한 route만 보존했다.

```text
masked world-state residual/energy
  -> target listener interaction support score
  -> target-route conservation gate
  -> anchor-free correction sensor
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.** 정확한 위치는 **HS-JEPA competition adapter**다.

```text
HS-JEPA core
  = visible human-life context -> hidden human-state world representation

이 문서의 역할
  = hidden world representation + target listener -> route-specific action decoder
```

따라서 이 실험을 논문에서 설명할 때 핵심 주장은 `target별 top-k가 좋다`가 아니다.
핵심 주장은 HS-JEPA core가 만든 masked world-state residual/energy가
target listener와 결합될 때 row-target action의 건강성을 route별로 분해할 수 있다는 것이다.

## 왜 중요한 adapter 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> route-wise conservation policy
```

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- OOF selected cells: `{summary["oof_selected_cells"]}`
- OOF selected gain sum: `{format_float(summary["oof_selected_gain_sum"], 6)}`
- OOF selected positive gain rate: `{format_float(summary["oof_selected_positive_gain_rate"], 6)}`
- listener global gain reference: `{format_float(summary["listener_global_gain_reference"], 6)}`
- gain over listener global reference: `{format_float(summary["gain_over_listener_global_reference"], 6)}`
- accepted targets: `{summary["accepted_targets"]}`
- held targets: `{summary["held_targets"]}`
- released test cells: `{summary["released_test_cells"]}`

## Selected Target Routes

{markdown_table(chosen, ["target", "target_route_family", "accepted", "policy", "decoder_action", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "conservation_score", "accept_reason"], max_rows=20)}

## OOF Target Contribution

{markdown_table(target_table, ["target", "selected_cells", "selected_gain_sum", "selected_mean_gain", "selected_positive_gain_rate", "active_subjects"], max_rows=20)}

## Top Route Policy Candidates

{markdown_table(top_grid, ["target", "policy", "decoder_action", "fraction", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "negative_subjects", "gain_lift_vs_null", "gain_z_vs_null", "conservation_score"], max_rows=40)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

이 후보는 train prior에서 시작하고, accepted target route에 대해서만 raw-memory 또는 inverse action을 적용한다.

## 해석

성공 조건:

```text
listener-conditioned global release보다 독성 target route를 줄이고,
OOF selected gain과 positive gain rate가 올라가야 한다.
```

실패 조건:

```text
route conservation이 대부분 hold로 수렴하거나,
positive route만 train OOF에 과적합되고 subject balance가 무너지면 release-grade가 아니다.
```

현재 결론:

```text
HS-JEPA core만으로는 release law가 완성되지 않는다.
하지만 core residual/energy는 target listener와 결합될 때 action-health를 강하게 설명한다.
따라서 competition adapter는 target-route conservation decoder를 가져야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_cells, test_cells, train_priors, view_metrics = build_listener_cells()
    score_col = "support_score_target_interaction_world_residual_energy"
    grid = route_policy_grid(train_cells, score_col)
    chosen = choose_conserved_routes(grid)
    oof_audit = apply_conserved_routes_to_oof(train_cells, chosen, score_col)
    target_table = target_summary(oof_audit)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_conserved_routes_to_test(sample, test_cells, chosen, score_col, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_target_route_conservation_decoder_anchor_free_{short_hash(candidate)}_uploadsafe.csv"
    accepted_targets = chosen.loc[chosen["accepted"].eq(True), "target"].tolist()
    held_targets = chosen.loc[chosen["accepted"].eq(False), "target"].tolist()
    selected = oof_audit[oof_audit["released"]].copy()
    summary = {
        "package": "target_route_conservation_decoder",
        "status": "target_route_conservation_decoder_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "verdict": "route_conservation_decoder_positive_public_free" if selected["effective_gain"].sum() > LISTENER_GLOBAL_GAIN_REFERENCE else "route_conservation_decoder_not_above_listener_global",
        "oof_selected_cells": int(len(selected)),
        "oof_selected_gain_sum": float(selected["effective_gain"].sum()) if len(selected) else 0.0,
        "oof_selected_positive_gain_rate": float((selected["effective_gain"] > 0).mean()) if len(selected) else np.nan,
        "listener_global_gain_reference": LISTENER_GLOBAL_GAIN_REFERENCE,
        "gain_over_listener_global_reference": float(selected["effective_gain"].sum()) - LISTENER_GLOBAL_GAIN_REFERENCE if len(selected) else -LISTENER_GLOBAL_GAIN_REFERENCE,
        "accepted_targets": accepted_targets,
        "held_targets": held_targets,
        "released_test_cells": int(test_audit["released"].sum()),
        "candidate_file": candidate_name,
        "validation": validation,
        "best_masked_view_component_corr_lift": float(view_metrics["component_corr_lift_vs_null"].max()),
    }

    top_grid = grid.sort_values(["conservation_score", "selected_gain_sum"], ascending=False).head(40)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_DIR / "target_route_policy_grid.csv", index=False)
    chosen.to_csv(OUT_DIR / "target_route_conservation_selected_routes.csv", index=False)
    oof_audit.to_csv(OUT_DIR / "target_route_conservation_oof_audit.csv", index=False)
    target_table.to_csv(OUT_DIR / "target_route_conservation_target_summary.csv", index=False)
    test_audit.to_csv(OUT_DIR / "target_route_conservation_test_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "target_route_conservation_decoder_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, chosen, target_table, top_grid)
    (OUT_DIR / "TARGET_ROUTE_CONSERVATION_DECODER_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
