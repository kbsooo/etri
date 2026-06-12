#!/usr/bin/env python3
"""Subject-invariant masked-tail jury core for HS-JEPA.

The strongest current HS-JEPA core evidence is masked-view consensus: multiple
context masks can agree on an episode-conditioned hidden tail field.  The
remaining failure mode is subject shortcut.  A full OOF policy can look useful
because it learned one subject's tail, then fail when a different subject is
held out.

This experiment makes subject-invariance part of the release mechanism:

    visible masked human-state views
      -> predict hidden episode-conditioned tail representation
      -> leave one subject out when choosing tail policies
      -> each subject-excluded world votes on row-target-action release
      -> release only actions that a subject jury repeatedly accepts

No public LB ledger, prior submission probabilities, or proprietary embedding
APIs are used.  The target representation and action-health labels are built
from OG train labels only.
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

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_episode_conditioned_relative_tail_core import (  # noqa: E402
    add_episode_conditioned_targets,
    add_episode_context,
    episode_feature_summary,
)
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from hsjepa_core.run_masked_view_consensus_tail_core import (  # noqa: E402
    apply_policies,
    build_view_feature_sets,
    choose_policies,
    fit_masked_view_consensus,
    policy_grid,
    summarize_nested_targets,
    view_disagreement_summary,
)
from hsjepa_core.run_tail_safe_expected_utility_core import (  # noqa: E402
    add_subject_contrastive_scores,
    build_mode_tables,
    utility_feature_columns,
)
from sleep_competition_adapter.target_route_conservation_decoder import (  # noqa: E402
    SAMPLE_SUBMISSION,
    build_listener_cells,
    short_hash,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_invariant_masked_tail_jury_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_INVARIANT_MASKED_TAIL_JURY_CORE_KO.md"
PARENT_OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "masked_view_consensus_tail_core"
NULL_REPEATS = 0


JURY_COLUMNS = [
    "row",
    "metric_row",
    "subject_id",
    "target",
    "cell_id",
    "decoder_action",
    "decoder_raw",
    "decoder_inverse",
    "action_prob",
    "prior_prob",
    "candidate_prob",
    "inverse_prob",
    "decisive_action",
    "effective_gain",
    "masked_view_gain_mean",
    "masked_view_consensus_utility",
    "masked_view_consensus_pessimistic_utility",
    "masked_view_consensus_health_score",
    "masked_view_disagreement",
]


def compact_for_jury(frame: pd.DataFrame) -> pd.DataFrame:
    cols = [col for col in JURY_COLUMNS if col in frame.columns]
    return frame[cols].copy()


def build_subject_jury(
    train_scored: pd.DataFrame,
    test_scored: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run subject-excluded policy selection and collect train/test jury votes."""
    train_modes = compact_for_jury(train_scored)
    test_modes = compact_for_jury(test_scored)
    subjects = sorted(train_scored["subject_id"].astype(str).unique())
    train_vote_count = pd.Series(0, index=train_modes.index, dtype=np.int64)
    test_vote_count = pd.Series(0, index=test_modes.index, dtype=np.int64)
    heldout_audits: list[pd.DataFrame] = []
    subject_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []

    for excluded_subject in subjects:
        selector = train_modes[~train_modes["subject_id"].astype(str).eq(excluded_subject)].copy()
        heldout = train_modes[train_modes["subject_id"].astype(str).eq(excluded_subject)].copy()
        chosen = choose_policies(policy_grid(selector, null_repeats=NULL_REPEATS))

        train_audit = apply_policies(train_modes, chosen)
        train_vote_count.loc[train_audit.index] += train_audit["released"].astype(int)

        test_audit = apply_policies(test_modes, chosen)
        test_vote_count.loc[test_audit.index] += test_audit["released"].astype(int)

        heldout_audit = apply_policies(heldout, chosen)
        heldout_audit["heldout_subject"] = excluded_subject
        heldout_audit["strict_jury_released"] = heldout_audit["released"].astype(bool)
        heldout_audits.append(heldout_audit)

        selected = heldout_audit[heldout_audit["released"]].copy()
        gains = selected["effective_gain"].to_numpy(dtype=np.float64) if len(selected) else np.array([], dtype=np.float64)
        subject_rows.append(
            {
                "heldout_subject": excluded_subject,
                "selected_cells": int(len(selected)),
                "gain_sum": float(gains.sum()) if len(gains) else 0.0,
                "mean_gain": float(gains.mean()) if len(gains) else 0.0,
                "positive_gain_rate": float((gains > 0).mean()) if len(gains) else np.nan,
                "accepted_targets": ",".join(chosen.loc[chosen["accepted"].eq(True), "target"].astype(str).tolist()),
            }
        )

        for _, route in chosen.iterrows():
            target_selected = selected[selected["target"].eq(route["target"])]
            route_rows.append(
                {
                    "heldout_subject": excluded_subject,
                    "target": str(route["target"]),
                    "accepted": bool(route["accepted"]),
                    "score_col": str(route["score_col"]),
                    "policy": str(route["policy"]),
                    "fraction": float(route["fraction"]),
                    "heldout_selected_cells": int(len(target_selected)),
                    "heldout_gain_sum": float(target_selected["effective_gain"].sum()) if len(target_selected) else 0.0,
                    "heldout_positive_gain_rate": float((target_selected["effective_gain"] > 0).mean())
                    if len(target_selected)
                    else np.nan,
                    "raw_action_count": int(target_selected["decoder_raw"].sum()) if len(target_selected) else 0,
                    "inverse_action_count": int(target_selected["decoder_inverse"].sum()) if len(target_selected) else 0,
                }
            )

    train_jury = train_modes.copy()
    test_jury = test_modes.copy()
    train_jury["subject_jury_vote_count"] = train_vote_count.to_numpy(dtype=np.int64)
    test_jury["subject_jury_vote_count"] = test_vote_count.to_numpy(dtype=np.int64)
    train_jury["subject_jury_vote_fraction"] = train_jury["subject_jury_vote_count"].astype(float) / max(len(subjects), 1)
    test_jury["subject_jury_vote_fraction"] = test_jury["subject_jury_vote_count"].astype(float) / max(len(subjects), 1)

    for frame in [train_jury, test_jury]:
        frame["subject_jury_release_score"] = (
            frame["subject_jury_vote_fraction"]
            + 0.16 * frame["masked_view_consensus_health_score"].rank(pct=True)
            + 0.10 * frame["masked_view_consensus_utility"].rank(pct=True)
            - 0.14 * frame["masked_view_disagreement"].rank(pct=True)
        )

    return (
        train_jury,
        test_jury,
        pd.DataFrame(subject_rows),
        pd.DataFrame(route_rows),
        pd.concat(heldout_audits, ignore_index=True),
    )


def choose_jury_release_laws(
    nested_target_summary: pd.DataFrame,
    route_rows: pd.DataFrame,
    train_rows: int,
    test_rows: int,
    subject_count: int,
) -> pd.DataFrame:
    """Translate strict subject-heldout evidence into target-level release budgets."""
    accept_rate = route_rows.groupby("target", observed=True)["accepted"].mean().to_dict()
    rows: list[dict[str, Any]] = []
    scale = test_rows / max(train_rows, 1)
    if nested_target_summary.empty:
        nested_target_summary = pd.DataFrame({"target": TARGETS})

    stats = nested_target_summary.set_index("target").to_dict(orient="index")
    for target in TARGETS:
        target_stats = stats.get(target, {})
        gain_sum = float(target_stats.get("gain_sum", 0.0))
        selected_cells = int(target_stats.get("selected_cells", 0))
        positive_rate = float(target_stats.get("positive_gain_rate", 0.0)) if pd.notna(target_stats.get("positive_gain_rate", np.nan)) else 0.0
        positive_subjects = int(target_stats.get("positive_subjects", 0))
        negative_subjects = int(target_stats.get("negative_subjects", 0))
        target_accept_rate = float(accept_rate.get(target, 0.0))
        accepted = (
            gain_sum > 0.0
            and selected_cells > 0
            and positive_subjects >= negative_subjects
            and positive_rate >= 0.52
            and target_accept_rate >= 0.40
        )
        vote_threshold = max(2, int(np.ceil(0.40 * subject_count)))
        if positive_subjects >= negative_subjects + 3 and gain_sum > 0.5:
            vote_threshold = max(2, int(np.ceil(0.30 * subject_count)))
        budget = int(np.clip(round(selected_cells * scale), 0, 120))
        if accepted:
            budget = max(1, budget)
        else:
            budget = 0
        rows.append(
            {
                "target": target,
                "accepted": bool(accepted),
                "vote_threshold": int(vote_threshold),
                "test_budget": int(budget),
                "heldout_accept_rate": target_accept_rate,
                "heldout_gain_sum": gain_sum,
                "heldout_selected_cells": selected_cells,
                "heldout_positive_gain_rate": positive_rate,
                "heldout_positive_subjects": positive_subjects,
                "heldout_negative_subjects": negative_subjects,
                "accept_reason": "subject_invariant_masked_tail_jury_release"
                if accepted
                else "failed_subject_invariant_jury_stress",
            }
        )
    return pd.DataFrame(rows)


def load_or_build_parent_masked_view_state() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float], pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    """Load the parent masked-view hidden-tail state, rebuilding only if absent."""
    parent_train = PARENT_OUT_DIR / "masked_view_consensus_full_oof_action_audit.csv"
    parent_test = PARENT_OUT_DIR / "masked_view_consensus_test_release_audit.csv"
    parent_view_metrics = PARENT_OUT_DIR / "masked_view_consensus_view_metrics.csv"
    parent_disagreement = PARENT_OUT_DIR / "masked_view_consensus_disagreement_by_target.csv"
    parent_episode_features = PARENT_OUT_DIR / "masked_view_consensus_episode_feature_summary.csv"
    if parent_train.exists() and parent_test.exists():
        train_scored = pd.read_csv(parent_train)
        test_scored = pd.read_csv(parent_test)
        view_metrics = pd.read_csv(parent_view_metrics) if parent_view_metrics.exists() else pd.DataFrame()
        disagreement = pd.read_csv(parent_disagreement) if parent_disagreement.exists() else view_disagreement_summary(train_scored)
        episode_features = pd.read_csv(parent_episode_features) if parent_episode_features.exists() else pd.DataFrame()
        prior_col = "target_prior" if "target_prior" in train_scored.columns else "prior_prob"
        train_priors = train_scored.groupby("target", observed=True)[prior_col].first().astype(float).to_dict()
        return train_scored, test_scored, train_priors, view_metrics, disagreement, episode_features, "parent_masked_view_state_cache"

    train_cells, test_cells, train_priors, _view_metrics = build_listener_cells()
    train_cells, test_cells, _contrastive_metrics, _contrastive_summary = add_subject_contrastive_scores(train_cells, test_cells)
    train_modes, test_modes = build_mode_tables(train_cells, test_cells)
    train_modes, test_modes, episode_cols = add_episode_context(train_modes, test_modes)
    train_modes = add_episode_conditioned_targets(train_modes)
    feature_cols = utility_feature_columns(train_modes, test_modes) + [
        col for col in episode_cols if col in train_modes.columns and col in test_modes.columns
    ]
    feature_cols = list(dict.fromkeys(feature_cols))
    view_feature_sets = build_view_feature_sets(feature_cols)
    train_scored, test_scored, view_metrics = fit_masked_view_consensus(train_modes, test_modes, view_feature_sets)
    disagreement = view_disagreement_summary(train_scored)
    episode_features = episode_feature_summary(train_scored, test_scored, episode_cols)
    return train_scored, test_scored, train_priors, view_metrics, disagreement, episode_features, "rebuilt_from_og_parent_state"


def apply_jury_release_to_test(
    sample: pd.DataFrame,
    test_jury: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])

    released = pd.Series(False, index=test_jury.index)
    for _, law in release_laws.iterrows():
        if not bool(law["accepted"]):
            continue
        target = str(law["target"])
        part = test_jury[
            test_jury["target"].eq(target)
            & (test_jury["subject_jury_vote_count"] >= int(law["vote_threshold"]))
        ].copy()
        if part.empty:
            part = test_jury[test_jury["target"].eq(target)].copy()
        part = part.sort_values(
            ["subject_jury_release_score", "subject_jury_vote_count", "masked_view_consensus_utility"],
            ascending=False,
        )
        part = part.drop_duplicates("cell_id", keep="first").head(int(law["test_budget"]))
        released.loc[part.index] = True

    audit = test_jury.copy()
    audit["released"] = released.to_numpy(dtype=bool)
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def summarize_jury_votes(train_jury: pd.DataFrame, test_jury: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for target in TARGETS:
        tr = train_jury[train_jury["target"].eq(target)]
        te = test_jury[test_jury["target"].eq(target)]
        rows.append(
            {
                "target": target,
                "train_mean_vote_fraction": float(tr["subject_jury_vote_fraction"].mean()),
                "train_p90_vote_fraction": float(tr["subject_jury_vote_fraction"].quantile(0.90)),
                "test_mean_vote_fraction": float(te["subject_jury_vote_fraction"].mean()),
                "test_p90_vote_fraction": float(te["subject_jury_vote_fraction"].quantile(0.90)),
                "test_high_vote_cells": int((te["subject_jury_vote_fraction"] >= 0.40).sum()),
            }
        )
    return pd.DataFrame(rows)


def build_markdown(
    summary: dict[str, Any],
    view_metrics: pd.DataFrame,
    disagreement: pd.DataFrame,
    episode_features: pd.DataFrame,
    jury_subject_summary: pd.DataFrame,
    jury_route_rows: pd.DataFrame,
    nested_target_summary: pd.DataFrame,
    release_laws: pd.DataFrame,
    vote_summary: pd.DataFrame,
) -> str:
    return f"""# Subject-Invariant Masked-Tail Jury Core

## 한 줄 요약

HS-JEPA hidden tail representation이 진짜 human-state 구조라면,
특정 subject를 빼고 policy를 골라도 비슷한 row-target-action이 살아남아야 한다.
이 실험은 subject-excluded worlds를 jury로 사용해 subject shortcut을 release 조건 안에 넣었다.

```text
masked visible context views
  -> hidden episode-conditioned tail representation
  -> subject-excluded policy selection
  -> jury vote over row-target-action release
  -> sparse anchor-free correction
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 단, classifier가 아니라 **HS-JEPA core-decoder boundary**다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 masked human context만으로 보이지 않는 episode-conditioned action-tail representation을
subject가 바뀌어도 예측할 수 있는가?
```

LeJEPA성은 다음 질문에서 나온다.

```text
좋아 보이는 tail action이 subject shortcut/collapse인지,
subject-excluded jury vote로 걸러낼 수 있는가?
```

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- parent hidden-tail state source: `{summary["parent_state_source"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- strict subject-heldout gain: `{format_float(summary["strict_subjectheldout_gain_sum"], 6)}`
- strict subject-heldout selected cells: `{summary["strict_subjectheldout_selected_cells"]}`
- release targets: `{summary["release_targets"]}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## View Metrics

{markdown_table(view_metrics, ["view", "feature_count", "gain_mae", "tail_mae", "positive_auc", "positive_ap", "toxic_auc", "toxic_ap"], max_rows=16)}

## View Disagreement By Target

{markdown_table(disagreement, ["target", "mean_disagreement", "median_disagreement", "mean_abs_gain", "toxic_tail_rate"], max_rows=16)}

## Episode Feature Summary

{markdown_table(episode_features, ["feature", "train_mean", "train_std", "test_mean", "test_std"], max_rows=20)}

## Jury Subject Summary

{markdown_table(jury_subject_summary, ["heldout_subject", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "accepted_targets"], max_rows=20)}

## Jury Route Rows

{markdown_table(jury_route_rows, ["heldout_subject", "target", "accepted", "score_col", "policy", "fraction", "heldout_selected_cells", "heldout_gain_sum", "heldout_positive_gain_rate", "raw_action_count", "inverse_action_count"], max_rows=70)}

## Nested Target Summary

{markdown_table(nested_target_summary, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate", "raw_action_count", "inverse_action_count", "positive_subjects", "negative_subjects"], max_rows=20)}

## Subject-Jury Release Laws

{markdown_table(release_laws, ["target", "accepted", "vote_threshold", "test_budget", "heldout_accept_rate", "heldout_gain_sum", "heldout_selected_cells", "heldout_positive_gain_rate", "heldout_positive_subjects", "heldout_negative_subjects", "accept_reason"], max_rows=20)}

## Jury Vote Distribution

{markdown_table(vote_summary, ["target", "train_mean_vote_fraction", "train_p90_vote_fraction", "test_mean_vote_fraction", "test_p90_vote_fraction", "test_high_vote_cells"], max_rows=20)}

## 해석

좋은 결과:

```text
subject-excluded jury가 positive heldout gain을 유지하면,
HS-JEPA hidden tail representation은 단일 subject의 tail memory가 아니라
subject-invariant action-health field에 가깝다.
```

나쁜 결과:

```text
full masked-view consensus가 좋고 jury가 나쁘면,
현재 positive signal은 view-invariant일 수는 있어도 subject-invariant하지 않다.
그 경우 HS-JEPA core는 아직 public/private-safe release law가 아니라
adapter가 의심해야 할 teacher signal로 다뤄야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_scored, test_scored, train_priors, view_metrics, disagreement, efs, parent_state_source = load_or_build_parent_masked_view_state()

    train_jury, test_jury, jury_subject_summary, jury_route_rows, strict_audit = build_subject_jury(train_scored, test_scored)
    strict_selected = strict_audit[strict_audit["released"]].copy()
    nested_target_summary = summarize_nested_targets(strict_audit)
    release_laws = choose_jury_release_laws(
        nested_target_summary,
        jury_route_rows,
        train_rows=int(train_scored["row"].nunique()),
        test_rows=len(pd.read_csv(SAMPLE_SUBMISSION)),
        subject_count=int(train_scored["subject_id"].astype(str).nunique()),
    )
    vote_summary = summarize_jury_votes(train_jury, test_jury)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_release_audit = apply_jury_release_to_test(sample, test_jury, release_laws, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_invariant_masked_tail_jury_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    strict_gain = float(strict_selected["effective_gain"].sum()) if len(strict_selected) else 0.0
    release_targets = release_laws.loc[release_laws["accepted"].eq(True), "target"].astype(str).tolist()
    verdict = (
        "subject_invariant_masked_tail_jury_positive"
        if strict_gain > 0 and len(release_targets) > 0
        else "subject_invariant_masked_tail_jury_inactive"
        if strict_gain >= 0
        else "subject_invariant_masked_tail_jury_negative"
    )
    summary = {
        "package": "subject_invariant_masked_tail_jury_core",
        "status": "subject_invariant_masked_tail_jury_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "parent_state_source": parent_state_source,
        "view_names": [
            name.replace("mv_", "").replace("_gain", "")
            for name in train_scored.columns
            if name.startswith("mv_") and name.endswith("_gain")
        ],
        "verdict": verdict,
        "strict_subjectheldout_gain_sum": strict_gain,
        "strict_subjectheldout_selected_cells": int(len(strict_selected)),
        "release_targets": release_targets,
        "released_test_cells": int(test_release_audit["released"].sum()),
        "candidate_file": candidate_name,
        "validation": validation,
    }

    view_metrics.to_csv(OUT_DIR / "subject_invariant_jury_view_metrics.csv", index=False)
    disagreement.to_csv(OUT_DIR / "subject_invariant_jury_disagreement_by_target.csv", index=False)
    efs.to_csv(OUT_DIR / "subject_invariant_jury_episode_feature_summary.csv", index=False)
    jury_subject_summary.to_csv(OUT_DIR / "subject_invariant_jury_subject_summary.csv", index=False)
    jury_route_rows.to_csv(OUT_DIR / "subject_invariant_jury_route_rows.csv", index=False)
    nested_target_summary.to_csv(OUT_DIR / "subject_invariant_jury_nested_target_summary.csv", index=False)
    release_laws.to_csv(OUT_DIR / "subject_invariant_jury_release_laws.csv", index=False)
    vote_summary.to_csv(OUT_DIR / "subject_invariant_jury_vote_summary.csv", index=False)
    strict_audit.to_csv(OUT_DIR / "subject_invariant_jury_strict_subjectheldout_audit.csv", index=False)
    test_release_audit.to_csv(OUT_DIR / "subject_invariant_jury_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_invariant_masked_tail_jury_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(
        summary,
        view_metrics,
        disagreement,
        efs,
        jury_subject_summary,
        jury_route_rows,
        nested_target_summary,
        release_laws,
        vote_summary,
    )
    (OUT_DIR / "SUBJECT_INVARIANT_MASKED_TAIL_JURY_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
