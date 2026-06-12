#!/usr/bin/env python3
"""Subject-balanced target-route conservation decoder for HS-JEPA.

The first target-route conservation decoder produced a large public-free OOF
gain, but it selected policies by aggregate OOF objective.  This script asks the
next, stricter question:

    Does the listener-conditioned HS-JEPA route law survive subject-tail stress?

It keeps the same public-free ingredients:

    masked world-state residual/energy
      -> target listener interaction support
      -> route-specific release / inverse / hold policy

but selects target routes by subject-balanced health: positive gain, target
shuffle lift, active subject coverage, and small negative-subject exposure.

This is a competition adapter/diagnostic, not HS-JEPA core itself.
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

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    LISTENER_GLOBAL_GAIN_REFERENCE,
    PAPER_DOC as ROUTE_CONSERVATION_DOC,
    SAMPLE_SUBMISSION,
    apply_conserved_routes_to_oof,
    apply_conserved_routes_to_test,
    build_listener_cells,
    route_policy_grid,
    select_indices,
    short_hash,
    target_summary,
)


OUT_DIR = ROOT / "sleep_competition_adapter" / "outputs" / "subject_balanced_route_conservation_decoder"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_BALANCED_ROUTE_CONSERVATION_DECODER_KO.md"
ROUTE_CONSERVATION_GAIN_REFERENCE = 15.595885092582881


def policy_subject_audit(cells: pd.DataFrame, grid: pd.DataFrame, score_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    subjects = sorted(cells["subject_id"].astype(str).unique())
    audit_rows: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []
    for _, route in grid.iterrows():
        target = str(route["target"])
        policy = str(route["policy"])
        fraction = float(route["fraction"])
        decoder = str(route["decoder_action"])
        part = cells[cells["target"].eq(target)]
        selected = select_indices(part, score_col, policy, fraction)
        gain_col = "inverse_realized_gain" if decoder == "inverse_toxic_memory" else "realized_gain"
        selected_cells = cells.loc[selected] if len(selected) else cells.iloc[0:0]

        subject_gains: dict[str, float] = {subject: 0.0 for subject in subjects}
        subject_counts: dict[str, int] = {subject: 0 for subject in subjects}
        if len(selected_cells):
            grouped = selected_cells.groupby("subject_id", observed=True)
            for subject, group in grouped:
                subject = str(subject)
                subject_gains[subject] = float(group[gain_col].sum())
                subject_counts[subject] = int(len(group))

        gains = np.array([subject_gains[subject] for subject in subjects], dtype=np.float64)
        counts = np.array([subject_counts[subject] for subject in subjects], dtype=np.int64)
        selected_gain = selected_cells[gain_col].to_numpy(dtype=np.float64) if len(selected_cells) else np.array([], dtype=np.float64)
        positive_subjects = int((gains > 0).sum())
        negative_subjects = int((gains < 0).sum())
        active_subjects = int((counts > 0).sum())
        no_action_subjects = int((counts == 0).sum())
        gain_sum = float(gains.sum())
        min_subject_gain = float(gains.min()) if len(gains) else 0.0
        lower_quartile_gain = float(np.quantile(gains, 0.25)) if len(gains) else 0.0
        positive_gain_rate = float((selected_gain > 0).mean()) if len(selected_gain) else np.nan
        balance_score = (
            gain_sum
            + 0.35 * float(route.get("gain_lift_vs_null", 0.0))
            + 0.45 * positive_subjects
            - 0.85 * negative_subjects
            - 0.12 * no_action_subjects
            + 0.60 * min_subject_gain
            + 0.30 * lower_quartile_gain
        )
        aggregate_rows.append(
            {
                **route.to_dict(),
                "subject_gain_sum": gain_sum,
                "subject_positive_count": positive_subjects,
                "subject_negative_count": negative_subjects,
                "subject_active_count": active_subjects,
                "subject_no_action_count": no_action_subjects,
                "subject_min_gain": min_subject_gain,
                "subject_lower_quartile_gain": lower_quartile_gain,
                "subject_selected_positive_gain_rate": positive_gain_rate,
                "subject_balance_score": balance_score,
            }
        )
        for subject in subjects:
            audit_rows.append(
                {
                    "target": target,
                    "policy": policy,
                    "decoder_action": decoder,
                    "fraction": fraction,
                    "subject_id": subject,
                    "selected_cells": subject_counts[subject],
                    "gain_sum": subject_gains[subject],
                }
            )
    return pd.DataFrame(aggregate_rows), pd.DataFrame(audit_rows)


def choose_subject_balanced_routes(subject_grid: pd.DataFrame) -> pd.DataFrame:
    chosen = []
    for target, part in subject_grid.groupby("target", observed=True):
        hold = part[part["policy"].eq("hold")].iloc[0].to_dict()
        non_hold = part[~part["policy"].eq("hold")].copy()
        viable = non_hold[
            (non_hold["selected_gain_sum"] > 0.0)
            & (non_hold["gain_lift_vs_null"] > 0.0)
            & (non_hold["subject_selected_positive_gain_rate"].fillna(0.0) >= 0.60)
            & (non_hold["subject_negative_count"] <= 2)
            & (non_hold["subject_active_count"] >= 3)
            & (non_hold["subject_min_gain"] >= -1.25)
        ].copy()
        if viable.empty:
            hold["accepted"] = False
            hold["accept_reason"] = "no_policy_passed_subject_balance_gate"
            chosen.append(hold)
            continue
        row = viable.sort_values(
            ["subject_balance_score", "subject_gain_sum", "gain_lift_vs_null"],
            ascending=False,
        ).iloc[0].to_dict()
        row["accepted"] = True
        row["accept_reason"] = "positive_gain_subject_balance_target_shuffle_lift"
        chosen.append(row)
    return pd.DataFrame(chosen).sort_values("target")


def build_markdown(
    summary: dict[str, Any],
    chosen: pd.DataFrame,
    target_table: pd.DataFrame,
    subject_grid_top: pd.DataFrame,
    subject_audit_summary: pd.DataFrame,
) -> str:
    return f"""# HS-JEPA Diagnostic Adapter: Subject-Balanced Route Conservation Decoder

## 한 줄 요약

`Target-Route Conservation Decoder`가 OOF에서는 강했지만 subject-tail shortcut일 수 있다.
이번 실험은 같은 HS-JEPA listener-conditioned route law를 subject-balanced objective로 다시 고른다.

```text
masked world-state residual/energy
  -> target listener interaction support
  -> subject-balanced route conservation
  -> anchor-free correction sensor
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden world-state representation

이 문서의 역할
  = hidden world-state route law가 subject-tail shortcut인지 stress한다.
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
- route conservation gain reference: `{format_float(summary["route_conservation_gain_reference"], 6)}`
- gain over listener global reference: `{format_float(summary["gain_over_listener_global_reference"], 6)}`
- gain retained vs route conservation reference: `{format_float(summary["gain_retained_vs_route_conservation_reference"], 6)}`
- accepted targets: `{summary["accepted_targets"]}`
- held targets: `{summary["held_targets"]}`
- released test cells: `{summary["released_test_cells"]}`

## Selected Subject-Balanced Routes

{markdown_table(chosen, ["target", "accepted", "policy", "decoder_action", "fraction", "selected_cells", "selected_gain_sum", "subject_selected_positive_gain_rate", "subject_positive_count", "subject_negative_count", "subject_active_count", "subject_min_gain", "gain_lift_vs_null", "subject_balance_score", "accept_reason"], max_rows=20)}

## OOF Target Contribution

{markdown_table(target_table, ["target", "selected_cells", "selected_gain_sum", "selected_mean_gain", "selected_positive_gain_rate", "active_subjects"], max_rows=20)}

## Subject Stress Summary

{markdown_table(subject_audit_summary, ["subject_id", "selected_cells", "gain_sum", "positive_targets", "negative_targets"], max_rows=20)}

## Top Subject-Balanced Policy Candidates

{markdown_table(subject_grid_top, ["target", "policy", "decoder_action", "fraction", "selected_cells", "selected_gain_sum", "subject_selected_positive_gain_rate", "subject_positive_count", "subject_negative_count", "subject_min_gain", "gain_lift_vs_null", "subject_balance_score"], max_rows=40)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

## 해석

좋은 결과:

```text
subject-balanced route selection이 listener-global reference를 넘고,
route-conservation gain의 의미 있는 부분을 보존하면,
HS-JEPA route law가 단순 subject-tail shortcut만은 아니라는 증거가 된다.
```

나쁜 결과:

```text
subject balance를 걸자 gain이 대부분 사라지면,
target-route conservation은 OOF adapter로는 유효하지만 subject-general law는 아니다.
그 경우 다음 논문 주장은 core representation + diagnostic necessity로 낮춰야 한다.
```

현재 결론:

```text
HS-JEPA core residual/energy는 target listener route action을 설명한다.
하지만 release-grade architecture가 되려면 subject-balanced route responsibility가 필요하다.
```
"""


def subject_audit_summary(oof_audit: pd.DataFrame) -> pd.DataFrame:
    selected = oof_audit[oof_audit["released"]].copy()
    if selected.empty:
        return pd.DataFrame(columns=["subject_id", "selected_cells", "gain_sum", "positive_targets", "negative_targets"])
    cell_summary = (
        selected.groupby("subject_id", observed=True)
        .agg(
            selected_cells=("effective_gain", "size"),
            gain_sum=("effective_gain", "sum"),
        )
        .reset_index()
    )
    by_subject_target = (
        selected.groupby(["subject_id", "target"], observed=True)["effective_gain"]
        .sum()
        .reset_index()
    )
    target_summary_frame = (
        by_subject_target.groupby("subject_id", observed=True)
        .agg(
            positive_targets=("effective_gain", lambda x: int((x > 0).sum())),
            negative_targets=("effective_gain", lambda x: int((x < 0).sum())),
        )
        .reset_index()
    )
    return cell_summary.merge(target_summary_frame, on="subject_id", how="left").sort_values("subject_id")


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    score_col = "support_score_target_interaction_world_residual_energy"
    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    grid = route_policy_grid(train_cells, score_col)
    subject_grid, subject_policy_audit = policy_subject_audit(train_cells, grid, score_col)
    chosen = choose_subject_balanced_routes(subject_grid)
    oof_audit = apply_conserved_routes_to_oof(train_cells, chosen, score_col)
    target_table = target_summary(oof_audit)
    subject_summary = subject_audit_summary(oof_audit)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = apply_conserved_routes_to_test(sample, test_cells, chosen, score_col, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_balanced_route_conservation_anchor_free_{short_hash(candidate)}_uploadsafe.csv"
    selected = oof_audit[oof_audit["released"]].copy()
    selected_gain = float(selected["effective_gain"].sum()) if len(selected) else 0.0
    accepted_targets = chosen.loc[chosen["accepted"].eq(True), "target"].tolist()
    held_targets = chosen.loc[chosen["accepted"].eq(False), "target"].tolist()
    summary = {
        "package": "subject_balanced_route_conservation_decoder",
        "status": "subject_balanced_route_conservation_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "source_route_conservation_doc": str(ROUTE_CONSERVATION_DOC.relative_to(ROOT)),
        "verdict": "subject_balanced_route_conservation_positive" if selected_gain > LISTENER_GLOBAL_GAIN_REFERENCE else "subject_balanced_route_conservation_below_listener_reference",
        "oof_selected_cells": int(len(selected)),
        "oof_selected_gain_sum": selected_gain,
        "oof_selected_positive_gain_rate": float((selected["effective_gain"] > 0).mean()) if len(selected) else np.nan,
        "listener_global_gain_reference": LISTENER_GLOBAL_GAIN_REFERENCE,
        "route_conservation_gain_reference": ROUTE_CONSERVATION_GAIN_REFERENCE,
        "gain_over_listener_global_reference": selected_gain - LISTENER_GLOBAL_GAIN_REFERENCE,
        "gain_retained_vs_route_conservation_reference": selected_gain / ROUTE_CONSERVATION_GAIN_REFERENCE if ROUTE_CONSERVATION_GAIN_REFERENCE else np.nan,
        "accepted_targets": accepted_targets,
        "held_targets": held_targets,
        "released_test_cells": int(test_audit["released"].sum()),
        "candidate_file": candidate_name,
        "validation": validation,
    }

    top = subject_grid.sort_values(["subject_balance_score", "selected_gain_sum"], ascending=False).head(40)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_DIR / "aggregate_route_policy_grid.csv", index=False)
    subject_grid.to_csv(OUT_DIR / "subject_balanced_route_policy_grid.csv", index=False)
    subject_policy_audit.to_csv(OUT_DIR / "subject_route_policy_audit.csv", index=False)
    chosen.to_csv(OUT_DIR / "subject_balanced_selected_routes.csv", index=False)
    oof_audit.to_csv(OUT_DIR / "subject_balanced_oof_audit.csv", index=False)
    target_table.to_csv(OUT_DIR / "subject_balanced_target_summary.csv", index=False)
    subject_summary.to_csv(OUT_DIR / "subject_balanced_subject_summary.csv", index=False)
    test_audit.to_csv(OUT_DIR / "subject_balanced_test_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_balanced_route_conservation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, chosen, target_table, top, subject_summary)
    (OUT_DIR / "SUBJECT_BALANCED_ROUTE_CONSERVATION_DECODER_KO.md").write_text(md.rstrip() + "\n", encoding="utf-8")
    PAPER_DOC.write_text(md.rstrip() + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
