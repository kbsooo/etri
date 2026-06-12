#!/usr/bin/env python3
"""Use HS-JEPA world-model residual energy as an action decoder listener.

This adapter consumes the OG-only core world model from
``hsjepa_core/run_masked_context_world_model.py`` and tests whether its
residual energy can reduce toxic row-target actions in the cross-subject
prototype transport field.

It is intentionally public-free:
    - no public LB ledger
    - no prior submission probabilities
    - no proprietary embedding API

The experiment asks a narrow falsifiable question:

    Does the HS-JEPA core world-model residual behave like a target-specific
    action-health listener under subject-heldout stress?
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

from sleep_competition_adapter.cross_subject_episode_prototype_transport import OUT as CROSS_OUT  # noqa: E402
from sleep_competition_adapter.cross_subject_surprise_responsibility_veto import (  # noqa: E402
    CROSS_TEST_ACTIONS,
    reconstruct_release_oof_actions,
    release_spec,
)
from sleep_competition_adapter.surprise_responsibility_toxicity_veto import (  # noqa: E402
    TARGETS,
    markdown_table,
    read_sample,
    short_hash,
    validate_submission,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "world_model_residual_action_decoder"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "WORLD_MODEL_RESIDUAL_ACTION_DECODER_KO.md"
WORLD_MODEL_SCRIPT = ROOT / "hsjepa_core" / "run_masked_context_world_model.py"
WORLD_MODEL_OUT = ROOT / "hsjepa_core" / "outputs" / "masked_context_world_model"
WORLD_MODEL_STATE = WORLD_MODEL_OUT / "masked_context_world_model_state.csv"
WORLD_MODEL_SUMMARY = WORLD_MODEL_OUT / "masked_context_world_model_summary.json"
CROSS_SCRIPT = ROOT / "sleep_competition_adapter" / "cross_subject_episode_prototype_transport.py"
MIN_GAIN_IMPROVEMENT = 0.05


def ensure_inputs() -> None:
    if not WORLD_MODEL_STATE.exists() or not WORLD_MODEL_SUMMARY.exists():
        subprocess.run(["python3", str(WORLD_MODEL_SCRIPT)], cwd=ROOT, check=True)
    if not CROSS_TEST_ACTIONS.exists() or not (CROSS_OUT / "cross_subject_episode_prototype_transport_readout.json").exists():
        subprocess.run(["python3", str(CROSS_SCRIPT)], cwd=ROOT, check=True)


def energy_columns(state: pd.DataFrame) -> list[str]:
    return [
        col
        for col in state.columns
        if col.startswith("wm_energy_")
        and pd.api.types.is_numeric_dtype(state[col])
    ]


def attach_world_model_state(actions: pd.DataFrame, state: pd.DataFrame, split: str) -> pd.DataFrame:
    metric = state[state["split"].eq(split)].copy()
    metric["row"] = metric["metric_row"].astype(int)
    keep_cols = ["row", "subject_id"] + energy_columns(metric)
    merged = actions.merge(metric[keep_cols], on=["row", "subject_id"], how="left", validate="many_to_one")
    missing = int(merged[energy_columns(metric)].isna().all(axis=1).sum())
    if missing:
        raise ValueError(f"failed to attach world-model state for {missing} action rows")
    return merged


def keep_for_rule(frame: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    if rule["mode"] == "all":
        return pd.Series(True, index=frame.index)
    values = pd.to_numeric(frame[rule["score_col"]], errors="coerce")
    if rule["mode"] == "low_energy_listener":
        return values <= float(rule["threshold"])
    if rule["mode"] == "high_energy_listener":
        return values > float(rule["threshold"])
    raise ValueError(f"unknown rule mode: {rule['mode']}")


def evaluate_rule(part: pd.DataFrame, score_col: str, mode: str, threshold: float) -> dict[str, Any]:
    if mode == "all":
        selected = part
    else:
        selected = part.loc[keep_for_rule(part, {"score_col": score_col, "mode": mode, "threshold": threshold})]
    all_gain = float(part["true_gain"].sum())
    selected_gain = float(selected["true_gain"].sum()) if len(selected) else 0.0
    return {
        "score_col": score_col,
        "mode": mode,
        "threshold": threshold,
        "cells": int(len(selected)),
        "gain_sum": selected_gain,
        "mean_gain": float(selected["true_gain"].mean()) if len(selected) else 0.0,
        "positive_gain_rate": float((selected["true_gain"] > 0).mean()) if len(selected) else 0.0,
        "all_cells": int(len(part)),
        "all_gain_sum": all_gain,
        "all_mean_gain": float(part["true_gain"].mean()) if len(part) else 0.0,
        "all_positive_gain_rate": float((part["true_gain"] > 0).mean()) if len(part) else 0.0,
        "removed_gain_sum": float(all_gain - selected_gain),
    }


def rule_candidates(part: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for score_col in score_cols:
        values = pd.to_numeric(part[score_col], errors="coerce")
        if values.notna().sum() < 2 or values.nunique(dropna=True) < 2:
            continue
        threshold = float(values.median())
        for mode in ["low_energy_listener", "high_energy_listener", "all"]:
            rows.append(evaluate_rule(part, score_col, mode, threshold))
    return pd.DataFrame(rows)


def learn_rules(oof: pd.DataFrame, score_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    rules: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for target, part in oof.groupby("target", observed=True):
        detail = rule_candidates(part, score_cols)
        if detail.empty:
            rules.append({"target": target, "score_col": score_cols[0], "mode": "all", "threshold": 0.0})
            continue
        detail["target"] = target
        detail_rows.extend(detail.to_dict(orient="records"))
        all_best = detail[detail["mode"].eq("all")].sort_values("all_gain_sum", ascending=False).iloc[0]
        non_all = detail[detail["mode"].ne("all")].copy()
        non_all["gain_improvement"] = non_all["gain_sum"] - float(all_best["all_gain_sum"])
        best = non_all.sort_values(
            ["gain_improvement", "positive_gain_rate", "gain_sum"],
            ascending=False,
        ).iloc[0]
        if float(best["gain_improvement"]) >= MIN_GAIN_IMPROVEMENT:
            selected = best
        else:
            selected = all_best.copy()
            selected["mode"] = "all"
            selected["threshold"] = float(all_best["threshold"])
            selected["gain_improvement"] = 0.0
        rules.append(
            {
                "target": target,
                "score_col": str(selected["score_col"]),
                "mode": str(selected["mode"]),
                "threshold": float(selected["threshold"]),
                "selected_cells": int(selected["cells"]),
                "selected_gain_sum": float(selected["gain_sum"]),
                "all_gain_sum": float(selected["all_gain_sum"]),
                "removed_gain_sum": float(selected["removed_gain_sum"]),
                "gain_improvement": float(selected.get("gain_improvement", 0.0)),
                "selected_positive_gain_rate": float(selected["positive_gain_rate"]),
                "all_positive_gain_rate": float(selected["all_positive_gain_rate"]),
            }
        )
    return pd.DataFrame(rules), pd.DataFrame(detail_rows)


def apply_rules(frame: pd.DataFrame, rules: pd.DataFrame) -> pd.Series:
    keep = pd.Series(True, index=frame.index)
    rule_map = {row["target"]: row.to_dict() for _, row in rules.iterrows()}
    for target, idx in frame.groupby("target", observed=True).groups.items():
        rule = rule_map.get(target)
        if rule is None:
            keep.loc[idx] = True
            continue
        keep.loc[idx] = keep_for_rule(frame.loc[idx], rule).to_numpy(dtype=bool)
    return keep.astype(bool)


def subject_heldout_stress(oof: pd.DataFrame, score_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for subject, heldout_idx in oof.groupby("subject_id", observed=True).groups.items():
        train = oof.drop(index=heldout_idx)
        heldout = oof.loc[heldout_idx].copy()
        rules, _ = learn_rules(train, score_cols)
        keep = apply_rules(heldout, rules)
        kept = heldout.loc[keep]
        rows.append(
            {
                "heldout_subject": subject,
                "all_cells": int(len(heldout)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(heldout["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "removed_gain_sum": float(heldout["true_gain"].sum() - (kept["true_gain"].sum() if len(kept) else 0.0)),
                "all_mean_gain": float(heldout["true_gain"].mean()) if len(heldout) else 0.0,
                "kept_mean_gain": float(kept["true_gain"].mean()) if len(kept) else 0.0,
                "all_positive_gain_rate": float((heldout["true_gain"] > 0).mean()) if len(heldout) else 0.0,
                "kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def per_target_summary(oof: pd.DataFrame, rules: pd.DataFrame, keep: pd.Series) -> pd.DataFrame:
    tmp = oof.copy()
    tmp["world_model_keep"] = keep.to_numpy(dtype=bool)
    rows = []
    for target, part in tmp.groupby("target", observed=True):
        kept = part[part["world_model_keep"]]
        rule = rules[rules["target"].eq(target)].head(1)
        rows.append(
            {
                "target": target,
                "rule": "all" if rule.empty else f"{rule['mode'].iloc[0]}::{rule['score_col'].iloc[0]}",
                "all_cells": int(len(part)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(part["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "removed_gain_sum": float(part["true_gain"].sum() - (kept["true_gain"].sum() if len(kept) else 0.0)),
                "all_positive_gain_rate": float((part["true_gain"] > 0).mean()),
                "kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_candidate(test_actions: pd.DataFrame, keep: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = read_sample()
    actions = test_actions.copy()
    actions["world_model_keep"] = keep.to_numpy(dtype=bool)
    actions["vetoed"] = actions["switched"].astype(bool) & ~actions["world_model_keep"]
    actions["final_pred"] = np.where(actions["vetoed"], actions["raw_pred"], actions["selected_pred"])
    candidate = sample.copy()
    for target in TARGETS:
        part = actions[actions["target"].eq(target)].sort_values("row")
        if len(part) != len(candidate):
            raise ValueError(f"test action rows for {target} do not match sample rows")
        candidate[target] = np.clip(part["final_pred"].to_numpy(dtype=float), 1e-5, 1 - 1e-5)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    return candidate, actions


def build_markdown(
    readout: dict[str, Any],
    rules: pd.DataFrame,
    target_summary: pd.DataFrame,
    stress: pd.DataFrame,
    test_summary: pd.DataFrame,
) -> str:
    return f"""# World-Model Residual Action Decoder

## 한 줄 요약

HS-JEPA core의 masked-context world model이 만든 residual energy를 cross-subject row-target action decoder의 listener로 사용했다.

```text
HS-JEPA core world-model residual
  -> target-specific action-health listener
  -> cross-subject prototype action veto
  -> subject-heldout stress
```

## 위치

이 실험은 HS-JEPA core 자체가 아니라, core representation을 사용하는 adapter/diagnostic이다.

- Core input: `hsjepa_core/run_masked_context_world_model.py`
- Adapter input: `cross_subject_episode_prototype_transport.py`
- Diagnostic: target-specific residual-energy listener와 subject-heldout stress

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Source Field

- source release law: `{readout["source_release_law"]}`
- source policy: `{readout["source_release_policy"]}` `{readout["source_release_param"]}`
- original OOF cells: `{readout["oof_original_cells"]}`
- original active subjects: `{readout["oof_original_active_subjects"]}`
- original gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- original positive gain rate: `{readout["oof_original_positive_gain_rate"]:.6f}`
- verdict: `{readout["verdict"]}`

## Learned Listener Rules

{markdown_table(rules, ["target", "mode", "score_col", "selected_cells", "selected_gain_sum", "all_gain_sum", "removed_gain_sum", "gain_improvement", "selected_positive_gain_rate", "all_positive_gain_rate"], max_rows=20)}

## OOF 결과

- kept cells: `{readout["oof_kept_cells"]}`
- kept active subjects: `{readout["oof_kept_active_subjects"]}`
- kept gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- removed cells: `{readout["oof_removed_cells"]}`
- removed gain sum: `{readout["oof_removed_gain_sum"]:.6f}`
- kept positive gain rate: `{readout["oof_kept_positive_gain_rate"]:.6f}`

Target summary:

{markdown_table(target_summary, ["target", "rule", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "removed_gain_sum", "all_positive_gain_rate", "kept_positive_gain_rate"], max_rows=20)}

## Subject-Heldout Stress

{markdown_table(stress, ["heldout_subject", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "removed_gain_sum", "all_mean_gain", "kept_mean_gain"], max_rows=20)}

Stress summary:

- subject-heldout original gain sum: `{readout["subject_heldout_original_gain_sum"]:.6f}`
- subject-heldout kept gain sum: `{readout["subject_heldout_kept_gain_sum"]:.6f}`
- subject-heldout delta: `{readout["subject_heldout_delta"]:.6f}`

## Test Candidate

- candidate: `{readout["candidate_file"]}`
- original switched cells: `{readout["test_original_switched_cells"]}`
- kept switched cells: `{readout["test_kept_switched_cells"]}`
- vetoed switched cells: `{readout["test_vetoed_switched_cells"]}`
- validation: `{readout["validation"]}`

Target별 test kept/vetoed:

{markdown_table(test_summary, ["target", "switched", "kept", "vetoed"], max_rows=20)}

## 해석

성공 조건:

```text
core world-model residual energy가 cross-subject action field에서 negative-gain action을 제거한다.
```

실패 조건:

```text
world-model residual은 representation evidence로는 의미가 있지만,
row-target action decoder에서는 subject-heldout stress를 통과하지 못한다.
```

이 실험은 LB 최적화가 아니라 HS-JEPA core representation이 adapter 독성을 줄일 수 있는지 확인하는 stress test다.

현재 판정은 full OOF positive / subject-heldout fragile이다. 즉 core residual energy가 toxic pocket을 찾는 신호는 있지만,
그 신호를 그대로 public/private-safe release rule로 주장하기에는 아직 이르다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_inputs()
    spec = release_spec()
    world_state = pd.read_csv(WORLD_MODEL_STATE)
    score_cols = energy_columns(world_state)
    if not score_cols:
        raise ValueError("world-model state has no energy columns")
    actions, source_metric = reconstruct_release_oof_actions(spec)
    oof = attach_world_model_state(actions, world_state, "train")
    rules, detail = learn_rules(oof, score_cols)
    keep = apply_rules(oof, rules)
    oof["world_model_keep"] = keep.to_numpy(dtype=bool)
    target_summary = per_target_summary(oof, rules, keep)
    stress = subject_heldout_stress(oof, score_cols)

    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test_audit = attach_world_model_state(test_actions, world_state, "test")
    test_keep = apply_rules(test_audit, rules)
    candidate, test_audit = build_candidate(test_audit, test_keep)
    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_world_model_residual_action_decoder_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)

    kept = oof[oof["world_model_keep"]]
    removed = oof[~oof["world_model_keep"]]
    switched = test_audit[test_audit["switched"].astype(bool)].copy()
    test_summary = (
        switched.groupby("target", observed=True)
        .agg(
            switched=("switched", "size"),
            kept=("world_model_keep", "sum"),
            vetoed=("vetoed", "sum"),
        )
        .reset_index()
    )
    validation = validate_submission(candidate, read_sample())
    heldout_original = float(stress["all_gain_sum"].sum()) if len(stress) else 0.0
    heldout_kept = float(stress["kept_gain_sum"].sum()) if len(stress) else 0.0
    verdict = (
        "oof_positive_subjectheldout_fragile"
        if float(kept["true_gain"].sum()) > float(oof["true_gain"].sum()) and heldout_kept < heldout_original
        else "subjectheldout_positive"
        if heldout_kept >= heldout_original and float(kept["true_gain"].sum()) > float(oof["true_gain"].sum())
        else "negative_or_inconclusive"
    )
    readout = {
        "package": "world_model_residual_action_decoder",
        "status": "adapter_diagnostic_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "oof_original_cells": int(len(oof)),
        "oof_original_active_subjects": int(oof["subject_id"].nunique()),
        "oof_original_gain_sum": float(oof["true_gain"].sum()),
        "oof_original_mean_gain": float(oof["true_gain"].mean()),
        "oof_original_positive_gain_rate": float((oof["true_gain"] > 0).mean()),
        "oof_kept_cells": int(len(kept)),
        "oof_kept_active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_mean_gain": float(kept["true_gain"].mean()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "subject_heldout_original_gain_sum": heldout_original,
        "subject_heldout_kept_gain_sum": heldout_kept,
        "subject_heldout_delta": float(heldout_kept - heldout_original),
        "test_original_switched_cells": int(test_audit["switched"].astype(bool).sum()),
        "test_kept_switched_cells": int((test_audit["switched"].astype(bool) & test_audit["world_model_keep"]).sum()),
        "test_vetoed_switched_cells": int(test_audit["vetoed"].sum()),
        "candidate_file": candidate_file,
        "validation": validation,
        "verdict": verdict,
        "source_metric": source_metric.iloc[0].to_dict() if len(source_metric) else {},
        "worldview": (
            "HS-JEPA core world-model residual energy can act as a target-specific listener "
            "that reduces action toxicity in a cross-subject prototype transport decoder."
        ),
    }

    rules.to_csv(OUT_DIR / "world_model_residual_listener_rules.csv", index=False)
    detail.to_csv(OUT_DIR / "world_model_residual_rule_detail.csv", index=False)
    oof.to_csv(OUT_DIR / "world_model_residual_oof_action_audit.csv", index=False)
    target_summary.to_csv(OUT_DIR / "world_model_residual_target_summary.csv", index=False)
    stress.to_csv(OUT_DIR / "world_model_residual_subject_heldout_stress.csv", index=False)
    test_audit.to_csv(OUT_DIR / "world_model_residual_test_action_audit.csv", index=False)
    test_summary.to_csv(OUT_DIR / "world_model_residual_test_summary.csv", index=False)
    (OUT_DIR / "world_model_residual_action_decoder_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, rules, target_summary, stress, test_summary)
    (OUT_DIR / "WORLD_MODEL_RESIDUAL_ACTION_DECODER_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
