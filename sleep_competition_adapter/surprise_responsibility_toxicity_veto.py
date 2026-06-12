#!/usr/bin/env python3
"""Target-conditional masked-surprise responsibility veto.

This experiment asks whether HS-JEPA masked-view residual energy can reduce
row-target action toxicity.  It does not use public LB.  It learns, from OOF
action gain only, whether each target listener should trust high-surprise or
low-surprise episodes, then applies that rule to the public-free episode
action-space test actions.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "surprise_responsibility_toxicity_veto"
MASKED_VIEW_SCRIPT = ROOT / "sleep_competition_adapter" / "masked_view_surprise_action_release.py"
MASKED_VIEW_OUT = ROOT / "sleep_competition_adapter" / "outputs" / "masked_view_surprise_action_release"
ENERGY_PATH = MASKED_VIEW_OUT / "masked_view_surprise_energy.csv"
LAW_PATH = MASKED_VIEW_OUT / "masked_view_target_surprise_laws.csv"
EPISODE_OOF_PATH = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "episode_action_space_restriction_decoder"
    / "episode_action_space_selected_oof_cells.csv"
)
EPISODE_TEST_PATH = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "episode_action_space_restriction_decoder"
    / "episode_action_space_test_actions.csv"
)
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SURPRISE_RESPONSIBILITY_TOXICITY_VETO_KO.md"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
RELEASE_LAW = "route_tree_depth3_leaf24"
RELEASE_ACTION_SPACE = "episode_family_space_q90"
RELEASE_POLICY = "topfrac"
RELEASE_PARAM = 0.06


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def ensure_masked_view_outputs() -> None:
    if ENERGY_PATH.exists() and LAW_PATH.exists():
        return
    subprocess.run(["python3", str(MASKED_VIEW_SCRIPT)], cwd=ROOT, check=True)


def read_sample() -> pd.DataFrame:
    return pd.read_csv(SAMPLE_SUBMISSION, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)


def select_release_oof(cells: pd.DataFrame) -> pd.DataFrame:
    mask = (
        cells["law_name"].eq(RELEASE_LAW)
        & cells["action_space_policy"].eq(RELEASE_ACTION_SPACE)
        & cells["selection_policy"].eq(RELEASE_POLICY)
        & (pd.to_numeric(cells["selection_param"], errors="coerce") - RELEASE_PARAM).abs().le(1e-12)
    )
    return cells.loc[mask].copy().reset_index(drop=True)


def add_surprise_features(cells: pd.DataFrame, energy: pd.DataFrame, laws: pd.DataFrame, split_key: str) -> pd.DataFrame:
    frame = cells.copy()
    split_energy = energy[energy["split_key"].eq(split_key)].drop(columns=["split_key"]).copy()
    frame = frame.merge(split_energy, left_on="row", right_on="metric_row", how="left")
    law_map = laws.set_index("target").to_dict("index")
    target_surprise = []
    target_shift = []
    for _, row in frame.iterrows():
        law = law_map[str(row["target"])]
        target_surprise.append(float(row[str(law["surprise_score"])]))
        target_shift.append(float(law["shift"]))
    frame["target_surprise_rank"] = target_surprise
    frame["target_surprise_shift"] = target_shift
    frame["target_surprise_direction"] = np.sign(frame["target_surprise_shift"].to_numpy(dtype=float))
    frame["action_move_sign"] = np.sign(
        pd.to_numeric(frame["selected_pred"], errors="coerce").to_numpy(dtype=float)
        - pd.to_numeric(frame["raw_pred"], errors="coerce").to_numpy(dtype=float)
    )
    frame["surprise_action_direction_agrees"] = (
        frame["action_move_sign"].eq(frame["target_surprise_direction"])
        | np.isclose(
            pd.to_numeric(frame["selected_pred"], errors="coerce").to_numpy(dtype=float),
            pd.to_numeric(frame["raw_pred"], errors="coerce").to_numpy(dtype=float),
        )
    )
    frame["surprise_responsibility_score"] = (
        0.55 * pd.to_numeric(frame["masked_surprise_energy_mean_rank"], errors="coerce").fillna(0.5)
        + 0.45 * pd.to_numeric(frame["target_surprise_rank"], errors="coerce").fillna(0.5)
    )
    return frame


def learn_target_listener_rules(oof: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for target, group in oof.groupby("target", observed=True):
        median = float(group["surprise_responsibility_score"].median())
        candidates = {
            "all": pd.Series(True, index=group.index),
            "high_surprise_listener": group["surprise_responsibility_score"] >= median,
            "low_surprise_listener": group["surprise_responsibility_score"] < median,
        }
        for mode, mask in candidates.items():
            sub = group.loc[mask].copy()
            detail_rows.append(
                {
                    "target": target,
                    "mode": mode,
                    "median_score": median,
                    "cells": int(len(sub)),
                    "gain_sum": float(sub["true_gain"].sum()) if len(sub) else 0.0,
                    "mean_gain": float(sub["true_gain"].mean()) if len(sub) else 0.0,
                    "positive_gain_rate": float((sub["true_gain"] > 0).mean()) if len(sub) else 0.0,
                }
            )
        best = max(
            detail_rows[-3:],
            key=lambda item: (item["gain_sum"], item["mean_gain"], item["positive_gain_rate"]),
        )
        rows.append(
            {
                "target": target,
                "selected_mode": best["mode"],
                "median_score": median,
                "selected_cells": best["cells"],
                "selected_gain_sum": best["gain_sum"],
                "selected_mean_gain": best["mean_gain"],
                "selected_positive_gain_rate": best["positive_gain_rate"],
                "all_gain_sum": float(group["true_gain"].sum()),
                "all_mean_gain": float(group["true_gain"].mean()),
                "all_positive_gain_rate": float((group["true_gain"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(detail_rows)


def apply_rules(frame: pd.DataFrame, rules: pd.DataFrame) -> pd.Series:
    rule_map = rules.set_index("target").to_dict("index")
    keep = []
    for _, row in frame.iterrows():
        rule = rule_map.get(str(row["target"]))
        if rule is None:
            keep.append(True)
            continue
        score = float(row["surprise_responsibility_score"])
        median = float(rule["median_score"])
        mode = str(rule["selected_mode"])
        if mode == "all":
            keep.append(True)
        elif mode == "high_surprise_listener":
            keep.append(score >= median)
        elif mode == "low_surprise_listener":
            keep.append(score < median)
        else:
            keep.append(False)
    return pd.Series(keep, index=frame.index, dtype=bool)


def subject_heldout_stress(oof: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for subject in sorted(oof["subject_id"].astype(str).unique()):
        train = oof[oof["subject_id"].astype(str).ne(subject)].copy()
        holdout = oof[oof["subject_id"].astype(str).eq(subject)].copy()
        if train.empty or holdout.empty:
            continue
        rules, _ = learn_target_listener_rules(train)
        keep = apply_rules(holdout, rules)
        kept = holdout.loc[keep]
        rows.append(
            {
                "heldout_subject": subject,
                "all_cells": int(len(holdout)),
                "kept_cells": int(len(kept)),
                "all_gain_sum": float(holdout["true_gain"].sum()),
                "kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
                "removed_gain_sum": float(holdout.loc[~keep, "true_gain"].sum()),
                "all_mean_gain": float(holdout["true_gain"].mean()) if len(holdout) else 0.0,
                "kept_mean_gain": float(kept["true_gain"].mean()) if len(kept) else 0.0,
                "all_positive_gain_rate": float((holdout["true_gain"] > 0).mean()) if len(holdout) else 0.0,
                "kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_candidate(test_actions: pd.DataFrame, keep: pd.Series, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    actions = test_actions.copy()
    actions["surprise_veto_keep"] = keep.to_numpy(dtype=bool)
    actions["vetoed"] = actions["switched"].astype(bool) & ~actions["surprise_veto_keep"]
    actions["final_pred"] = np.where(actions["vetoed"], actions["raw_pred"], actions["selected_pred"])
    out = sample.copy()
    for target in TARGETS:
        part = actions[actions["target"].eq(target)].sort_values("row")
        if len(part) != len(out):
            raise ValueError(f"test action rows for {target} do not match sample rows")
        out[target] = np.clip(part["final_pred"].to_numpy(dtype=float), 1e-5, 1 - 1e-5)
    return out, actions


def validate_submission(candidate: pd.DataFrame, sample: pd.DataFrame) -> dict[str, Any]:
    problems = []
    if list(candidate.columns) != list(sample.columns):
        problems.append("columns differ from sample submission")
    if len(candidate) != len(sample):
        problems.append("row count differs from sample submission")
    if candidate[KEYS].astype(str).to_numpy().tolist() != sample[KEYS].astype(str).to_numpy().tolist():
        problems.append("key rows differ from sample submission")
    values = candidate[TARGETS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        problems.append("non-finite probabilities")
    if values.min() < 0 or values.max() > 1:
        problems.append("probabilities outside [0, 1]")
    return {
        "valid": not problems,
        "problems": problems,
        "rows": int(len(candidate)),
        "probability_min": float(np.nanmin(values)),
        "probability_max": float(np.nanmax(values)),
    }


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


def build_markdown(
    readout: dict[str, Any],
    rules: pd.DataFrame,
    rule_detail: pd.DataFrame,
    stress: pd.DataFrame,
    oof_audit: pd.DataFrame,
    test_audit: pd.DataFrame,
) -> str:
    switched = test_audit[test_audit["switched"].astype(bool)].copy()
    target_test_summary = (
        switched.groupby("target", observed=True)
        .agg(
            switched=("switched", "size"),
            kept=("surprise_veto_keep", "sum"),
            vetoed=("vetoed", "sum"),
        )
        .reset_index()
    )
    return f"""# Surprise Responsibility Toxicity Veto

## 한 줄 요약

Masked-view surprise energy를 action release 자체가 아니라 target별 listener responsibility로 사용해, episode action-space decoder의 독성 cell을 public LB 없이 OOF gain 기준으로 veto하는 실험이다.

## 왜 필요한가

`Masked View Surprise Action Release`는 JEPA residual energy가 Q3/Q2/S3 target law와 연결된다는 증거를 만들었다. 하지만 그 energy를 그대로 action으로 release하면 action-grade decoder인지 아직 불분명하다.

이번 실험은 질문을 바꾼다.

```text
surprise energy가 action을 직접 만드는가?
```

가 아니라,

```text
surprise energy가 target listener별로 어떤 action을 믿고 버릴지 결정하는가?
```

## JEPA Mapping

| 구성 | 의미 |
| --- | --- |
| context | episode action-space decoder가 제안한 row-target action |
| hidden target representation | masked-view residual energy가 만든 hidden episode responsibility |
| predictor | target별로 high-surprise listener / low-surprise listener / all listener 중 어느 책임자가 건강한지 OOF gain으로 선택 |
| energy decoder | 선택된 listener responsibility와 맞지 않는 action을 veto |
| stress | subject-heldout으로 target listener rule이 특정 subject tail인지 검사 |

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Target Listener Rules

{markdown_table(rules, ["target", "selected_mode", "median_score", "selected_cells", "selected_gain_sum", "all_gain_sum", "selected_mean_gain", "all_mean_gain", "selected_positive_gain_rate", "all_positive_gain_rate"])}

상세 rule 비교:

{markdown_table(rule_detail, ["target", "mode", "cells", "gain_sum", "mean_gain", "positive_gain_rate"], max_rows=24)}

## OOF Veto 결과

- original episode release cells: `{readout["oof_original_cells"]}`
- original gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- veto-kept cells: `{readout["oof_kept_cells"]}`
- veto-kept gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- removed gain sum: `{readout["oof_removed_gain_sum"]:.6f}`
- original positive gain rate: `{readout["oof_original_positive_gain_rate"]:.6f}`
- kept positive gain rate: `{readout["oof_kept_positive_gain_rate"]:.6f}`

## Subject-Heldout Stress

{markdown_table(stress, ["heldout_subject", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "removed_gain_sum", "all_mean_gain", "kept_mean_gain"], max_rows=20)}

주의: 이 release policy의 OOF action은 `id02`, `id09` 두 subject에만 집중되어 있다. 따라서 subject-heldout stress는 강한 검증이 아니라 "현재 release가 subject-tail에 몰려 있어 target listener rule을 안정적으로 외삽하기 어렵다"는 약한 진단으로 읽어야 한다.

## Test Candidate

- candidate: `{readout["candidate_file"]}`
- original switched cells: `{readout["test_original_switched_cells"]}`
- kept switched cells: `{readout["test_kept_switched_cells"]}`
- vetoed switched cells: `{readout["test_vetoed_switched_cells"]}`
- validation: `{readout["validation"]}`

Target별 kept/vetoed:

{markdown_table(target_test_summary, ["target", "switched", "kept", "vetoed"])}

## 해석

이 실험은 masked surprise가 넓은 action을 직접 만드는 장치가 아니라, target별 listener responsibility로 더 잘 작동하는지 검증한다.

OOF에서 gain이 증가하면:

```text
HS-JEPA residual energy can reduce action toxicity by assigning target-specific listener responsibility.
```

OOF에서는 증가하지만 subject-heldout에서 약하면:

```text
surprise responsibility is real but still subject-tail sensitive.
```

OOF에서도 감소하면:

```text
masked surprise energy is a state diagnostic, not a release-grade toxicity veto.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_masked_view_outputs()
    energy = pd.read_csv(ENERGY_PATH)
    laws = pd.read_csv(LAW_PATH)
    oof_cells = select_release_oof(pd.read_csv(EPISODE_OOF_PATH))
    if oof_cells.empty:
        raise ValueError("release OOF cells are empty")
    oof_audit = add_surprise_features(oof_cells, energy, laws, "train")
    rules, rule_detail = learn_target_listener_rules(oof_audit)
    oof_keep = apply_rules(oof_audit, rules)
    oof_audit["surprise_veto_keep"] = oof_keep
    stress = subject_heldout_stress(oof_audit)

    sample = read_sample()
    test_actions = pd.read_csv(EPISODE_TEST_PATH)
    test_audit = add_surprise_features(test_actions, energy, laws, "test")
    test_keep = apply_rules(test_audit, rules)
    candidate, test_audit = build_candidate(test_audit, test_keep, sample)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")

    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_surprise_responsibility_toxicity_veto_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)

    kept = oof_audit.loc[oof_keep]
    removed = oof_audit.loc[~oof_keep]
    readout = {
        "package": "surprise_responsibility_toxicity_veto",
        "status": "bigbet_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_action_decoder": "episode_action_space_restriction_decoder",
        "source_release_law": RELEASE_LAW,
        "source_release_action_space": RELEASE_ACTION_SPACE,
        "source_release_policy": RELEASE_POLICY,
        "source_release_param": RELEASE_PARAM,
        "oof_original_cells": int(len(oof_audit)),
        "oof_original_gain_sum": float(oof_audit["true_gain"].sum()),
        "oof_original_mean_gain": float(oof_audit["true_gain"].mean()),
        "oof_original_positive_gain_rate": float((oof_audit["true_gain"] > 0).mean()),
        "oof_kept_cells": int(len(kept)),
        "oof_kept_gain_sum": float(kept["true_gain"].sum()) if len(kept) else 0.0,
        "oof_kept_mean_gain": float(kept["true_gain"].mean()) if len(kept) else 0.0,
        "oof_kept_positive_gain_rate": float((kept["true_gain"] > 0).mean()) if len(kept) else 0.0,
        "oof_removed_cells": int(len(removed)),
        "oof_removed_gain_sum": float(removed["true_gain"].sum()) if len(removed) else 0.0,
        "subject_heldout_original_gain_sum": float(stress["all_gain_sum"].sum()) if len(stress) else 0.0,
        "subject_heldout_kept_gain_sum": float(stress["kept_gain_sum"].sum()) if len(stress) else 0.0,
        "test_original_switched_cells": int(test_audit["switched"].astype(bool).sum()),
        "test_kept_switched_cells": int((test_audit["switched"].astype(bool) & test_audit["surprise_veto_keep"]).sum()),
        "test_vetoed_switched_cells": int(test_audit["vetoed"].sum()),
        "candidate_file": candidate_file,
        "validation": validation,
        "worldview": (
            "Masked-view surprise energy is a target-conditional listener responsibility signal; "
            "it should veto actions whose episode surprise responsibility is unhealthy for that target."
        ),
    }

    rules.to_csv(OUT_DIR / "surprise_responsibility_target_rules.csv", index=False)
    rule_detail.to_csv(OUT_DIR / "surprise_responsibility_rule_detail.csv", index=False)
    stress.to_csv(OUT_DIR / "surprise_responsibility_subject_heldout_stress.csv", index=False)
    oof_audit.to_csv(OUT_DIR / "surprise_responsibility_oof_action_audit.csv", index=False)
    test_audit.to_csv(OUT_DIR / "surprise_responsibility_test_action_audit.csv", index=False)
    (OUT_DIR / "surprise_responsibility_toxicity_veto_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, rules, rule_detail, stress, oof_audit, test_audit)
    (OUT_DIR / "SURPRISE_RESPONSIBILITY_TOXICITY_VETO_KO.md").write_text(md + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
