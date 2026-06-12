#!/usr/bin/env python3
"""Signed listener-responsibility direction core probe for HS-JEPA.

The listener-responsibility field experiment showed a clean core signal:
HS-JEPA can identify which row-target cells deserve listener intervention.
The remaining failure was translation toxicity: the existing action decoder
still picked unsafe raw/inverse directions for some responsible cells.

This script makes that bottleneck the hidden target:

    visible human-state context
      + target listener
      + action-direction listener (raw vs inverse)
      -> hidden signed action-health field

The release adapter is deliberately narrow. It first uses the previously
recomputed responsibility field to select row-target cells, then chooses the
raw/inverse action whose signed direction score is higher.

No public LB ledger, prior submission probabilities, proprietary embedding API,
masked-tail teacher score as feature, or label-informed peer margins are used.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import TARGETS, validate_submission  # noqa: E402
from hsjepa_core.run_lifelog_core_state_evidence import format_float, markdown_table  # noqa: E402
from hsjepa_core.run_masked_human_state_pretext_listener_core import (  # noqa: E402
    build_masked_pretext_state,
)
from hsjepa_core.run_subject_invariant_listener_responsibility_field_core import (  # noqa: E402
    FEATURE_PATH,
    JURY_OUT_DIR,
    attach_core_features,
    build_cell_frame,
    build_test_cell_frame,
    evaluate as evaluate_responsibility,
    feature_families as responsibility_feature_families,
    human_numeric_columns,
    load_action_frames,
)
from sleep_competition_adapter.target_route_conservation_decoder import SAMPLE_SUBMISSION, short_hash  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "signed_listener_responsibility_direction_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SIGNED_LISTENER_RESPONSIBILITY_DIRECTION_CORE_KO.md"
RANDOM_SEED = 20260613

warnings.simplefilter("ignore", PerformanceWarning)

ACTION_GEOMETRY_COLS = [
    "prior_prob",
    "candidate_prob",
    "inverse_prob",
    "action_prob",
    "action_move",
    "abs_action_move",
    "decisive_action",
    "action_move_rank",
    "decoder_raw",
    "decoder_inverse",
]


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, score))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    if len(np.unique(y)) < 2:
        return None
    return float(average_precision_score(y, score))


def classifier_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.035,
            max_leaf_nodes=12,
            min_samples_leaf=16,
            l2_regularization=0.35,
            random_state=seed,
        ),
    )


def target_listener_columns(frame: pd.DataFrame) -> list[str]:
    base = [
        "target_prior",
        "target_prior_rank",
        "target_uncertainty",
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
    ]
    return [col for col in base if col in frame.columns] + [
        col for col in frame.columns if col.startswith("target_onehot_")
    ]


def add_signed_columns(frame: pd.DataFrame, cols: list[str], prefix: str) -> list[str]:
    sign = frame["direction_sign"].astype(float).to_numpy()
    made: list[str] = []
    signed_data: dict[str, np.ndarray] = {}
    for col in cols:
        if col not in frame.columns or not pd.api.types.is_numeric_dtype(frame[col]):
            continue
        out_col = f"{prefix}signed__{col}"
        signed_data[out_col] = frame[col].astype(float).to_numpy() * sign
        made.append(out_col)
    if signed_data:
        frame[made] = pd.DataFrame(signed_data, index=frame.index)
    return made


def prepare_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray], str]:
    features = pd.read_csv(FEATURE_PATH)
    pretext_state, _pretext_metrics, pretext_cols, _ = build_masked_pretext_state(features)
    action_train, action_test, _strict = load_action_frames()
    release_laws = pd.read_csv(JURY_OUT_DIR / "subject_invariant_jury_release_laws.csv")

    cell_train = build_cell_frame(action_train)
    cell_test = build_test_cell_frame(action_test)
    cell_train, cell_test, pretext_cols = attach_core_features(cell_train, cell_test, features, pretext_state)
    resp_families = responsibility_feature_families(cell_train, cell_test, pretext_cols)
    resp_metrics, _target_metrics, _fold_metrics, resp_test_scores, resp_oof_scores = evaluate_responsibility(
        cell_train,
        cell_test,
        resp_families,
    )

    primary = resp_metrics[resp_metrics["label_task"].eq("listener_responsible")].copy()
    core_family_names = [
        "human_listener_responsibility",
        "masked_pretext_listener_responsibility",
        "human_plus_masked_pretext_responsibility",
    ]
    release_family = str(
        primary[primary["feature_family"].isin(core_family_names)]
        .sort_values("ap_lift_vs_rate", ascending=False)
        .iloc[0]["feature_family"]
    )
    resp_col = f"score__{release_family}__listener_responsible"
    cell_train = cell_train.copy()
    cell_test = cell_test.copy()
    cell_train["responsibility_score"] = resp_oof_scores[resp_col]
    cell_test["responsibility_score"] = resp_test_scores[resp_col]

    merge_cols = [
        "cell_id",
        "listener_responsible",
        "positive_listener_responsible",
        "responsibility_score",
    ]
    human_cols = human_numeric_columns(cell_train, cell_test)
    clean_pretext_cols = [col for col in pretext_cols if col in cell_train.columns and col in cell_test.columns]
    core_cols = list(dict.fromkeys(human_cols + clean_pretext_cols))
    action_train = action_train.merge(
        cell_train[merge_cols + core_cols],
        on="cell_id",
        how="left",
        validate="many_to_one",
    )
    action_test = action_test.merge(
        cell_test[["cell_id", "responsibility_score"] + [col for col in core_cols if col in cell_test.columns]],
        on="cell_id",
        how="left",
        validate="many_to_one",
    )

    for frame in [action_train, action_test]:
        frame["direction_sign"] = np.where(frame["decoder_raw"].astype(float).gt(0.5), 1.0, -1.0)
        frame["direction_raw_listener"] = frame["decoder_raw"].astype(float)
        frame["direction_inverse_listener"] = frame["decoder_inverse"].astype(float)
        frame["signed_responsibility_score"] = frame["responsibility_score"].astype(float) * frame["direction_sign"]

    action_train["positive_action"] = action_train["effective_gain"].astype(float).gt(0.0).astype(int)
    return action_train, action_test, cell_train, release_laws, resp_oof_scores, resp_test_scores, release_family


def direction_feature_families(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, list[str]]:
    listener = [col for col in target_listener_columns(train) if col in test.columns]
    direction_listener = [
        "direction_raw_listener",
        "direction_inverse_listener",
        "direction_sign",
    ]
    action_geometry = [col for col in ACTION_GEOMETRY_COLS if col in train.columns and col in test.columns]
    human = human_numeric_columns(train, test)
    pretext_pred_energy = [
        col
        for col in train.columns
        if col in test.columns
        and (col.startswith("pretext_pred_") or col.startswith("pretext_energy_"))
    ]
    signed_human = add_signed_columns(train, human, "human_")
    add_signed_columns(test, human, "human_")
    signed_pretext = add_signed_columns(train, pretext_pred_energy, "pretext_")
    add_signed_columns(test, pretext_pred_energy, "pretext_")
    responsibility_cols = ["responsibility_score", "signed_responsibility_score"]
    responsibility_cols = [col for col in responsibility_cols if col in train.columns and col in test.columns]

    return {
        "direction_listener_only": list(dict.fromkeys(listener + direction_listener)),
        "action_geometry_direction": list(dict.fromkeys(listener + action_geometry)),
        "human_signed_direction": list(dict.fromkeys(listener + direction_listener + human + signed_human)),
        "masked_pretext_signed_direction": list(
            dict.fromkeys(listener + direction_listener + pretext_pred_energy + signed_pretext)
        ),
        "responsibility_weighted_pretext_direction": list(
            dict.fromkeys(listener + direction_listener + responsibility_cols + pretext_pred_energy + signed_pretext)
        ),
        "human_plus_pretext_signed_direction": list(
            dict.fromkeys(listener + direction_listener + responsibility_cols + human + pretext_pred_energy + signed_human + signed_pretext)
        ),
    }


def fit_oof_scores(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    groups = train["subject_id"].astype(str).to_numpy()
    y = train["positive_action"].astype(int).to_numpy()
    splitter = GroupKFold(n_splits=max(2, min(5, len(np.unique(groups)))))
    oof = np.zeros(len(train), dtype=np.float64)
    fold_rows: list[dict[str, Any]] = []
    for fold, (tr, va) in enumerate(splitter.split(train, y, groups=groups)):
        y_tr = y[tr]
        if len(np.unique(y_tr)) < 2 or not features:
            pred = np.full(len(va), float(y_tr.mean()) if len(y_tr) else 0.5)
        else:
            model = classifier_factory(RANDOM_SEED + fold)
            model.fit(train.iloc[tr][features], y_tr)
            pred = model.predict_proba(train.iloc[va][features])[:, 1]
        oof[va] = np.clip(pred, 1e-5, 1.0 - 1e-5)
        fold_rows.append(
            {
                "fold": fold,
                "heldout_subjects": ",".join(sorted(train.iloc[va]["subject_id"].astype(str).unique())),
                "positive_rate": float(y[va].mean()),
                "auc": safe_auc(y[va], oof[va]),
                "ap": safe_ap(y[va], oof[va]),
            }
        )
    if len(np.unique(y)) < 2 or not features:
        test_score = np.full(len(test), float(y.mean()) if len(y) else 0.5)
    else:
        model = classifier_factory(RANDOM_SEED + 101)
        model.fit(train[features], y)
        test_score = model.predict_proba(test[features])[:, 1]
    return np.clip(oof, 1e-5, 1.0 - 1e-5), np.clip(test_score, 1e-5, 1.0 - 1e-5), fold_rows


def select_cells_by_release_laws(
    cells: pd.DataFrame,
    release_laws: pd.DataFrame,
    budget_col: str,
) -> set[int]:
    selected: set[int] = set()
    laws = release_laws[release_laws["accepted"].astype(bool)]
    for _, law in laws.iterrows():
        target = str(law["target"])
        budget = max(1, int(law[budget_col]))
        part = cells[cells["target"].eq(target)].sort_values("responsibility_score", ascending=False).head(budget)
        selected.update(part["cell_id"].astype(int).tolist())
    return selected


def pairwise_action_metrics(
    actions: pd.DataFrame,
    score: np.ndarray,
    selected_cell_ids: set[int] | None = None,
) -> dict[str, Any]:
    frame = actions.copy()
    frame["direction_score"] = score
    if selected_cell_ids is not None:
        frame = frame[frame["cell_id"].isin(selected_cell_ids)]
    if frame.empty:
        return {
            "selected_cells": 0,
            "gain_sum": 0.0,
            "mean_gain": 0.0,
            "positive_rate": 0.0,
            "negative_rate": 0.0,
        }
    selected = frame.sort_values(
        ["cell_id", "direction_score", "masked_view_consensus_health_score"],
        ascending=[True, False, False],
    ).drop_duplicates("cell_id", keep="first")
    gains = selected["effective_gain"].astype(float)
    return {
        "selected_cells": int(len(selected)),
        "gain_sum": float(gains.sum()),
        "mean_gain": float(gains.mean()) if len(gains) else 0.0,
        "positive_rate": float(gains.gt(0).mean()) if len(gains) else 0.0,
        "negative_rate": float(gains.lt(0).mean()) if len(gains) else 0.0,
    }


def evaluate_direction(
    train: pd.DataFrame,
    test: pd.DataFrame,
    cell_train: pd.DataFrame,
    release_laws: pd.DataFrame,
    families: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray]]:
    y = train["positive_action"].astype(int).to_numpy()
    responsibility_cells = select_cells_by_release_laws(cell_train, release_laws, "heldout_selected_cells")
    oracle_responsibility_cells = set(
        cell_train[cell_train["listener_responsible"].astype(int).eq(1)]["cell_id"].astype(int).tolist()
    )
    metric_rows: list[dict[str, Any]] = []
    target_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    test_scores: dict[str, np.ndarray] = {}
    oof_scores: dict[str, np.ndarray] = {}
    for family_name, features in families.items():
        oof, test_score, folds = fit_oof_scores(train, test, features)
        oof_scores[family_name] = oof
        test_scores[family_name] = test_score
        ap = safe_ap(y, oof)
        all_pair = pairwise_action_metrics(train, oof, None)
        resp_pair = pairwise_action_metrics(train, oof, responsibility_cells)
        oracle_pair = pairwise_action_metrics(train, oof, oracle_responsibility_cells)
        metric_rows.append(
            {
                "feature_family": family_name,
                "feature_count": len(features),
                "positive_rate": float(y.mean()),
                "auc": safe_auc(y, oof),
                "ap": ap,
                "ap_lift_vs_rate": float(ap - y.mean()) if ap is not None else None,
                "pairwise_all_cells": all_pair["selected_cells"],
                "pairwise_all_gain_sum": all_pair["gain_sum"],
                "pairwise_all_positive_rate": all_pair["positive_rate"],
                "responsibility_cells": resp_pair["selected_cells"],
                "responsibility_gain_sum": resp_pair["gain_sum"],
                "responsibility_positive_rate": resp_pair["positive_rate"],
                "oracle_responsibility_cells": oracle_pair["selected_cells"],
                "oracle_responsibility_gain_sum": oracle_pair["gain_sum"],
                "oracle_responsibility_positive_rate": oracle_pair["positive_rate"],
            }
        )
        for fold in folds:
            fold["feature_family"] = family_name
            fold_rows.append(fold)
        for target in TARGETS:
            part = train[train["target"].eq(target)]
            idx = part.index.to_numpy()
            yt = part["positive_action"].astype(int).to_numpy()
            target_pair = pairwise_action_metrics(part, oof[idx], None)
            target_rows.append(
                {
                    "feature_family": family_name,
                    "target": target,
                    "positive_rate": float(yt.mean()),
                    "auc": safe_auc(yt, oof[idx]),
                    "ap": safe_ap(yt, oof[idx]),
                    "pairwise_gain_sum": target_pair["gain_sum"],
                    "pairwise_positive_rate": target_pair["positive_rate"],
                }
            )
    return pd.DataFrame(metric_rows), pd.DataFrame(target_rows), pd.DataFrame(fold_rows), test_scores, oof_scores


def release_candidate(
    sample: pd.DataFrame,
    action_test: pd.DataFrame,
    cell_test: pd.DataFrame,
    release_laws: pd.DataFrame,
    train_priors: dict[str, float],
    test_score: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    selected_cell_ids = select_cells_by_release_laws(cell_test, release_laws, "test_budget")
    audit = action_test.copy()
    audit["direction_score"] = test_score
    audit["released"] = audit["cell_id"].isin(selected_cell_ids)
    selected = audit[audit["released"]].sort_values(
        ["cell_id", "direction_score", "masked_view_consensus_health_score"],
        ascending=[True, False, False],
    ).drop_duplicates("cell_id", keep="first")
    for _, row in selected.iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row["action_prob"])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    audit["selected_action"] = audit.index.isin(selected.index)
    return out, audit


def build_markdown(
    summary: dict[str, Any],
    metrics: pd.DataFrame,
    target_metrics: pd.DataFrame,
    fold_metrics: pd.DataFrame,
    release_counts: pd.DataFrame,
) -> str:
    ranked = metrics.sort_values("responsibility_gain_sum", ascending=False)
    target_ranked = target_metrics.sort_values(["feature_family", "pairwise_gain_sum"], ascending=[True, False])
    return f"""# Signed Listener Responsibility Direction Core

## 한 줄 요약

row-target responsibility를 찾은 뒤, 그 cell에서 raw 방향으로 움직일지 inverse 방향으로 움직일지를
HS-JEPA core representation으로 다시 예측했다.

```text
visible human-state context
  + target listener
  + raw/inverse direction listener
  -> hidden signed action-health field
  -> responsibility-high cell에서 안전한 방향만 release
```

## 왜 필요한 실험인가

직전 responsibility field core는 `어디를 봐야 하는가`를 listener-only보다 잘 복원했다.
하지만 기존 action decoder로 번역하면 OOF gain이 음수였다. 따라서 이번 hidden target은
cell 위치가 아니라 signed action direction이다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`
- masked-tail teacher score as feature: `{summary["uses_masked_tail_teacher_score"]}`
- label-informed peer margin as feature: `{summary["uses_label_informed_peer_margin"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- responsibility source: `{summary["responsibility_source_family"]}`
- best direction family: `{summary["best_direction_family"]}`
- best direction AP lift: `{format_float(summary["best_direction_ap_lift"], 6)}`
- best responsibility-gated OOF gain: `{format_float(summary["best_responsibility_gain_sum"], 6)}`
- action-geometry responsibility-gated OOF gain: `{format_float(summary["action_geometry_responsibility_gain_sum"], 6)}`
- previous responsibility decoder OOF gain: `{format_float(summary["previous_responsibility_decoder_gain_sum"], 6)}`
- released test cells: `{summary["released_test_cells"]}`
- candidate: `{summary["candidate_file"]}`

## Direction Family Leaderboard

{markdown_table(ranked, ["feature_family", "feature_count", "positive_rate", "auc", "ap", "ap_lift_vs_rate", "pairwise_all_gain_sum", "responsibility_gain_sum", "responsibility_positive_rate", "oracle_responsibility_gain_sum"], max_rows=20)}

## Target-Level Direction Metrics

{markdown_table(target_ranked, ["feature_family", "target", "positive_rate", "auc", "ap", "pairwise_gain_sum", "pairwise_positive_rate"], max_rows=90)}

## Fold Stability

{markdown_table(fold_metrics, ["feature_family", "fold", "heldout_subjects", "positive_rate", "auc", "ap"], max_rows=90)}

## Release Counts

{markdown_table(release_counts, ["target", "count"], max_rows=20)}

## 해석

좋은 결과:

```text
responsibility-high cell 안에서 signed direction gain이 양수로 바뀌면,
HS-JEPA core가 "어디를 볼지"뿐 아니라 "어느 방향이 안전한지"도 복원한다는 뜻이다.
```

나쁜 결과:

```text
direction AP가 좋아도 responsibility-gated OOF gain이 음수면,
방향 classifier는 action-health ranking을 읽지만 Log Loss utility로 번역되지 않은 것이다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    action_train, action_test, cell_train, release_laws, _resp_oof, _resp_test, responsibility_family = prepare_frames()
    families = direction_feature_families(action_train, action_test)
    metrics, target_metrics, fold_metrics, test_scores, oof_scores = evaluate_direction(
        action_train,
        action_test,
        cell_train,
        release_laws,
        families,
    )

    best = metrics.sort_values(["responsibility_gain_sum", "ap_lift_vs_rate"], ascending=[False, False]).iloc[0]
    best_family = str(best["feature_family"])
    action_geometry_gain = float(
        metrics.loc[metrics["feature_family"].eq("action_geometry_direction"), "responsibility_gain_sum"].iloc[0]
    )
    previous_summary = json.loads(
        (ROOT / "hsjepa_core" / "outputs" / "subject_invariant_listener_responsibility_field_core" / "subject_invariant_listener_responsibility_field_core_summary.json").read_text(
            encoding="utf-8"
        )
    )
    previous_gain = float(previous_summary["release_family_oof_gain_sum"])
    train_priors = action_train.groupby("target", observed=True)["target_prior"].first().astype(float).to_dict()
    sample = pd.read_csv(SAMPLE_SUBMISSION)
    # Rebuild test cell frame from action_test after scores have been generated.
    cell_test = (
        action_test.groupby(["row", "metric_row", "subject_id", "sleep_date", "lifelog_date", "target", "cell_id"], observed=True)
        .agg(responsibility_score=("responsibility_score", "first"))
        .reset_index()
    )
    candidate, release_audit = release_candidate(
        sample,
        action_test,
        cell_test,
        release_laws,
        train_priors,
        test_scores[best_family],
    )
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_signed_listener_responsibility_direction_{short_hash(candidate)}_uploadsafe.csv"
    release_counts = (
        release_audit[release_audit["selected_action"]].groupby("target", observed=True).size().reset_index(name="count")
    )

    best_gain = float(best["responsibility_gain_sum"])
    if best_gain > 0.0 and best_gain > previous_gain:
        verdict = "signed_direction_core_positive_action_translation_repaired"
    elif best_gain > previous_gain:
        verdict = "signed_direction_core_reduces_translation_toxicity"
    elif float(best["ap_lift_vs_rate"]) > 0.03:
        verdict = "signed_direction_signal_positive_but_utility_fragile"
    else:
        verdict = "signed_direction_core_negative"
    summary = {
        "package": "signed_listener_responsibility_direction_core",
        "status": "signed_listener_responsibility_direction_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_masked_tail_teacher_score": False,
        "uses_label_informed_peer_margin": False,
        "verdict": verdict,
        "responsibility_source_family": responsibility_family,
        "best_direction_family": best_family,
        "best_direction_ap_lift": float(best["ap_lift_vs_rate"]),
        "best_responsibility_gain_sum": best_gain,
        "action_geometry_responsibility_gain_sum": action_geometry_gain,
        "previous_responsibility_decoder_gain_sum": previous_gain,
        "released_test_cells": int(release_audit["selected_action"].sum()),
        "release_targets": release_counts["target"].astype(str).tolist() if not release_counts.empty else [],
        "candidate_file": candidate_name,
        "validation": validation,
    }

    metrics.to_csv(OUT_DIR / "signed_direction_family_metrics.csv", index=False)
    target_metrics.to_csv(OUT_DIR / "signed_direction_target_metrics.csv", index=False)
    fold_metrics.to_csv(OUT_DIR / "signed_direction_fold_metrics.csv", index=False)
    release_audit.to_csv(OUT_DIR / "signed_direction_release_audit.csv", index=False)
    release_counts.to_csv(OUT_DIR / "signed_direction_release_counts.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "signed_listener_responsibility_direction_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, metrics, target_metrics, fold_metrics, release_counts)
    (OUT_DIR / "SIGNED_LISTENER_RESPONSIBILITY_DIRECTION_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
