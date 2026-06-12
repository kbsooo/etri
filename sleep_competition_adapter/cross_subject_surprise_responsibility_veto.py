#!/usr/bin/env python3
"""Masked-surprise responsibility veto on cross-subject transport actions.

The previous surprise-responsibility veto improved OOF gain, but the source
episode release was concentrated in two subjects.  This experiment applies the
same HS-JEPA residual-energy listener idea to the broader cross-subject
prototype transport field.

Question:
    Does masked-view residual energy still reduce action toxicity when the
    action field is produced by cross-subject episode prototype transport?
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

from sleep_competition_adapter.cross_subject_episode_prototype_transport import (
    OUT as CROSS_OUT,
    build_oof_context,
    evaluate_policy,
    feature_views,
    predict_oof_transport,
)
from sleep_competition_adapter.failure_boundary_law_distillation import (
    best_candidate_per_cell,
)
from sleep_competition_adapter.surprise_responsibility_toxicity_veto import (
    ENERGY_PATH,
    KEYS,
    LAW_PATH,
    TARGETS,
    add_surprise_features,
    apply_rules,
    ensure_masked_view_outputs,
    learn_target_listener_rules,
    markdown_table,
    read_sample,
    short_hash,
    subject_heldout_stress,
    validate_submission,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "cross_subject_surprise_responsibility_veto"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md"
CROSS_READOUT = CROSS_OUT / "cross_subject_episode_prototype_transport_readout.json"
CROSS_TEST_ACTIONS = CROSS_OUT / "cross_subject_episode_prototype_transport_test_actions.csv"


def release_spec() -> dict[str, Any]:
    readout = json.loads(CROSS_READOUT.read_text(encoding="utf-8"))
    metrics = pd.read_csv(CROSS_OUT / "cross_subject_episode_prototype_transport_metrics.csv")
    row = metrics[
        metrics["law_name"].eq(readout["release_law_name"])
        & metrics["policy"].eq(readout["release_policy"])
        & (pd.to_numeric(metrics["param"], errors="coerce") - float(readout["release_param"])).abs().le(1e-12)
    ].head(1)
    if row.empty:
        raise ValueError("release law from cross-subject readout not found in metrics")
    rec = row.iloc[0].to_dict()
    return {
        "readout": readout,
        "law_name": str(rec["law_name"]),
        "feature_view": str(rec["feature_view"]),
        "group_mode": str(rec["group_mode"]),
        "neighbors": int(rec["neighbors"]),
        "weights": str(rec["weights"]),
        "policy": str(rec["policy"]),
        "param": float(rec["param"]),
    }


def reconstruct_release_oof_actions(spec: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    features_frame, labels, sample, gain_pairs, raw_cols, row_pair_frame, row_meta = build_oof_context()
    del features_frame, labels, sample, raw_cols, row_pair_frame, row_meta
    cell_frame = (
        gain_pairs[
            [
                "cell_key",
                "fold",
                "row",
                "subject_id",
                "target",
                "y",
                "raw_pred",
                "raw_loss",
            ]
        ]
        .drop_duplicates("cell_key")
        .rename(columns={"raw_pred": "pred__raw_knn_blend"})
        .copy()
    )
    views = feature_views(gain_pairs)
    cols = views[spec["feature_view"]]
    score_col = f"pred__{spec['law_name']}"
    scored = gain_pairs.copy()
    scored[score_col] = predict_oof_transport(
        scored,
        cols,
        int(spec["neighbors"]),
        str(spec["weights"]),
        str(spec["group_mode"]),
    )
    candidates = best_candidate_per_cell(scored, score_col, str(spec["law_name"]), str(spec["feature_view"]))
    metric, actions = evaluate_policy(cell_frame, candidates, str(spec["policy"]), float(spec["param"]))
    return actions, pd.DataFrame([metric])


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


def per_subject_summary(oof_audit: pd.DataFrame) -> pd.DataFrame:
    if oof_audit.empty:
        return pd.DataFrame()
    return (
        oof_audit.groupby("subject_id", observed=True)
        .agg(
            cells=("cell_key", "size"),
            kept_cells=("surprise_veto_keep", "sum"),
            all_gain_sum=("true_gain", "sum"),
            kept_gain_sum=("true_gain", lambda s: float(s[oof_audit.loc[s.index, "surprise_veto_keep"]].sum())),
            positive_gain_rate=("true_gain", lambda s: float((s > 0).mean())),
        )
        .reset_index()
    )


def build_markdown(
    readout: dict[str, Any],
    rules: pd.DataFrame,
    rule_detail: pd.DataFrame,
    stress: pd.DataFrame,
    subject_summary: pd.DataFrame,
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
    return f"""# Cross-Subject Surprise Responsibility Veto

## 한 줄 요약

Cross-subject episode prototype transport가 만든 더 넓은 row-target action field에 masked-view surprise responsibility veto를 적용했다.

## HS-JEPA 안에서의 위치

이 실험은 HS-JEPA core 자체가 아니다.

```text
Core signal  = masked context-to-hidden-view prediction residual
Adapter      = cross-subject episode-action prototype transport
Diagnostic   = target-specific surprise responsibility veto
```

따라서 논문에서의 정확한 위치는 다음과 같다.

```text
HS-JEPA core가 만든 surprise representation이
cross-subject adapter의 toxic row-target action을 줄일 수 있는지 검증하는
adapter + LeJEPA-style diagnostic 실험
```

## 왜 필요한가

이전 `Surprise Responsibility Toxicity Veto`는 OOF gain을 개선했지만, source release가 `id02`, `id09` 두 subject에 몰려 있었다. 따라서 masked surprise가 진짜 general action-health signal인지, 좁은 subject tail에만 맞은 rule인지 구분하기 어려웠다.

이번 실험은 source action field를 cross-subject prototype transport로 바꾼다.

```text
peer subject episode-action prototype
  -> held-out subject row-target action
  -> masked-view surprise responsibility
  -> toxicity veto
```

## 사용하지 않은 정보

- public LB ledger: `{readout["uses_public_score_ledger"]}`
- prior submission probability: `{readout["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{readout["uses_proprietary_embedding_api"]}`

## Source Cross-Subject Field

- release law: `{readout["source_release_law"]}`
- source policy: `{readout["source_release_policy"]}` `{readout["source_release_param"]}`
- original OOF cells: `{readout["oof_original_cells"]}`
- original active subjects: `{readout["oof_original_active_subjects"]}`
- original gain sum: `{readout["oof_original_gain_sum"]:.6f}`
- original positive gain rate: `{readout["oof_original_positive_gain_rate"]:.6f}`

## Target Listener Rules

{markdown_table(rules, ["target", "selected_mode", "median_score", "selected_cells", "selected_gain_sum", "all_gain_sum", "selected_mean_gain", "all_mean_gain", "selected_positive_gain_rate", "all_positive_gain_rate"])}

Rule detail:

{markdown_table(rule_detail, ["target", "mode", "cells", "gain_sum", "mean_gain", "positive_gain_rate"], max_rows=24)}

## OOF Veto 결과

- kept cells: `{readout["oof_kept_cells"]}`
- kept active subjects: `{readout["oof_kept_active_subjects"]}`
- kept gain sum: `{readout["oof_kept_gain_sum"]:.6f}`
- removed cells: `{readout["oof_removed_cells"]}`
- removed gain sum: `{readout["oof_removed_gain_sum"]:.6f}`
- kept positive gain rate: `{readout["oof_kept_positive_gain_rate"]:.6f}`

Subject summary:

{markdown_table(subject_summary, ["subject_id", "cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "positive_gain_rate"], max_rows=20)}

## Subject-Heldout Stress

{markdown_table(stress, ["heldout_subject", "all_cells", "kept_cells", "all_gain_sum", "kept_gain_sum", "removed_gain_sum", "all_mean_gain", "kept_mean_gain"], max_rows=20)}

## Test Candidate

- candidate: `{readout["candidate_file"]}`
- original switched cells: `{readout["test_original_switched_cells"]}`
- kept switched cells: `{readout["test_kept_switched_cells"]}`
- vetoed switched cells: `{readout["test_vetoed_switched_cells"]}`
- validation: `{readout["validation"]}`

Target별 test kept/vetoed:

{markdown_table(target_test_summary, ["target", "switched", "kept", "vetoed"])}

## 해석

이 실험은 HS-JEPA의 action-health story를 더 강하게 검증한다.

성공 조건:

```text
cross-subject action field에서도 masked-view residual energy가 negative-gain actions를 더 많이 제거한다.
```

실패 조건:

```text
surprise responsibility는 narrow episode release에는 맞지만 cross-subject transport field에는 일반화되지 않는다.
```

결과 해석은 OOF gain sum뿐 아니라 active subject coverage와 subject-heldout stress를 같이 봐야 한다.
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_masked_view_outputs()
    spec = release_spec()
    energy = pd.read_csv(ENERGY_PATH)
    laws = pd.read_csv(LAW_PATH)
    actions, source_metric = reconstruct_release_oof_actions(spec)
    oof_audit = add_surprise_features(actions, energy, laws, "train")
    rules, rule_detail = learn_target_listener_rules(oof_audit)
    oof_keep = apply_rules(oof_audit, rules)
    oof_audit["surprise_veto_keep"] = oof_keep
    stress = subject_heldout_stress(oof_audit)
    subject_summary = per_subject_summary(oof_audit)

    sample = read_sample()
    test_actions = pd.read_csv(CROSS_TEST_ACTIONS)
    test_audit = add_surprise_features(test_actions, energy, laws, "test")
    test_keep = apply_rules(test_audit, rules)
    candidate, test_audit = build_candidate(test_audit, test_keep, sample)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")

    file_hash = short_hash(candidate)
    candidate_file = f"submission_hsjepa_cross_subject_surprise_responsibility_veto_{file_hash}_uploadsafe.csv"
    candidate.to_csv(OUT_DIR / candidate_file, index=False)
    candidate.to_csv(ROOT / candidate_file, index=False)

    kept = oof_audit.loc[oof_keep]
    removed = oof_audit.loc[~oof_keep]
    readout = {
        "package": "cross_subject_surprise_responsibility_veto",
        "status": "bigbet_candidate_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_release_law": spec["law_name"],
        "source_release_policy": spec["policy"],
        "source_release_param": spec["param"],
        "oof_original_cells": int(len(oof_audit)),
        "oof_original_active_subjects": int(oof_audit["subject_id"].nunique()),
        "oof_original_gain_sum": float(oof_audit["true_gain"].sum()),
        "oof_original_mean_gain": float(oof_audit["true_gain"].mean()),
        "oof_original_positive_gain_rate": float((oof_audit["true_gain"] > 0).mean()),
        "oof_kept_cells": int(len(kept)),
        "oof_kept_active_subjects": int(kept["subject_id"].nunique()) if len(kept) else 0,
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
            "Masked-view surprise responsibility should reduce toxicity on cross-subject "
            "episode-action prototype transport, not only on a narrow local episode tail."
        ),
    }

    rules.to_csv(OUT_DIR / "cross_subject_surprise_target_rules.csv", index=False)
    rule_detail.to_csv(OUT_DIR / "cross_subject_surprise_rule_detail.csv", index=False)
    source_metric.to_csv(OUT_DIR / "cross_subject_surprise_source_metric.csv", index=False)
    oof_audit.to_csv(OUT_DIR / "cross_subject_surprise_oof_action_audit.csv", index=False)
    stress.to_csv(OUT_DIR / "cross_subject_surprise_subject_heldout_stress.csv", index=False)
    subject_summary.to_csv(OUT_DIR / "cross_subject_surprise_subject_summary.csv", index=False)
    test_audit.to_csv(OUT_DIR / "cross_subject_surprise_test_action_audit.csv", index=False)
    (OUT_DIR / "cross_subject_surprise_responsibility_veto_readout.json").write_text(
        json.dumps(readout, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(readout, rules, rule_detail, stress, subject_summary, test_audit)
    (OUT_DIR / "CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md").write_text(md + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md + "\n", encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
