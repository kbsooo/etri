#!/usr/bin/env python3
"""Subject-contrastive action-support core evidence for HS-JEPA.

This is a public-free HS-JEPA core-side experiment.

Previous adapter diagnostics showed a recurring bottleneck:

    HS-JEPA world state weakly reads action toxicity,
    but absolute action-health scores do not translate safely across subjects.

This script tests a more core-level hypothesis:

    If subject identity and target prevalence are the nuisance factors,
    HS-JEPA should still rank two days from the same subject-target route by
    which raw-memory action is healthier.

The experiment trains pairwise preference models:

    same subject + same target action pair
      -> which row-target action has higher realized OOF gain?

Then it scores held-out subjects by comparing their cells against peer
reference cells from other subjects.  This removes direct subject-memory and
target-prior shortcuts from the supervision interface.

No public LB ledger, previous submission probabilities, or proprietary
embedding APIs are used.  The generated candidate is an anchor-free sensor,
not a leaderboard-tuned final blend.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.run_action_support_world_model_core import (  # noqa: E402
    NEIGHBORS,
    RANDOM_SEED,
    TARGETS,
    append_row_features,
    knn_probability_field,
    make_action_cell_table,
    make_test_action_table,
    score_support_predictions,
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
from hsjepa_core.run_masked_context_world_model import build_world_model_state  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "subject_contrastive_action_support_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md"
SAMPLE_SUBMISSION = ROOT / "data" / "ch2026_submission_sample.csv"
NULL_REPEATS = 24
MAX_PAIRS_PER_SUBJECT_TARGET = 180
MAX_REFERENCES_PER_TARGET = 40
MIN_PAIR_GAIN_MARGIN = 0.015


def short_hash(frame: pd.DataFrame) -> str:
    return hashlib.sha256(frame[TARGETS].to_numpy(dtype=np.float64).round(10).tobytes()).hexdigest()[:8]


def stable_seed(*parts: object) -> int:
    key = "::".join(map(str, parts)).encode("utf-8")
    return RANDOM_SEED + int(hashlib.sha256(key).hexdigest()[:8], 16) % 1009


def safe_auc(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(roc_auc_score(y[mask], score[mask]))


def safe_ap(y: np.ndarray, score: np.ndarray) -> float | None:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    mask = np.isfinite(score)
    if mask.sum() == 0 or len(np.unique(y[mask])) < 2:
        return None
    return float(average_precision_score(y[mask], score[mask]))


def model_factory(seed: int) -> Any:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        HistGradientBoostingClassifier(
            learning_rate=0.032,
            max_leaf_nodes=12,
            min_samples_leaf=22,
            l2_regularization=0.28,
            random_state=seed,
        ),
    )


def world_feature_columns(state: pd.DataFrame) -> dict[str, list[str]]:
    pred = [col for col in state.columns if col.startswith("wm_pred_")]
    resid = [col for col in state.columns if col.startswith("wm_resid_")]
    energy = [col for col in state.columns if col.startswith("wm_energy")]
    return {
        "pred": pred,
        "resid": resid,
        "energy": energy,
        "resid_energy": resid + energy,
        "full": pred + resid + energy,
    }


def make_feature_map(state: pd.DataFrame) -> dict[str, list[str]]:
    cols = world_feature_columns(state)
    action_cols = ["action_move", "abs_action_move", "action_move_rank"]
    target_cols = target_context_columns()
    return {
        "action_pair_only": action_cols,
        "target_action_pair_only": target_cols + action_cols,
        "world_residual_energy_pair": cols["resid_energy"],
        "world_residual_energy_action_pair": action_cols + cols["resid_energy"],
        "world_predicted_action_pair": action_cols + cols["pred"],
        "world_full_action_pair": action_cols + cols["full"],
    }


def pair_columns(cols: list[str]) -> list[str]:
    return [f"diff__{col}" for col in cols] + [f"absdiff__{col}" for col in cols]


def build_pairwise_dataset(
    cells: pd.DataFrame,
    cols: list[str],
    max_pairs_per_group: int,
    seed_key: str,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Build balanced pairwise examples inside subject-target groups."""
    rng = np.random.default_rng(stable_seed("pairwise", seed_key))
    x_parts: list[pd.DataFrame] = []
    y_parts: list[np.ndarray] = []
    weight_parts: list[np.ndarray] = []
    clean = cells.reset_index(drop=True)
    values = clean[cols].replace([np.inf, -np.inf], np.nan)
    gains = clean["realized_gain"].to_numpy(dtype=np.float64)

    for (subject, target), group in clean.groupby(["subject_id", "target"], observed=True).groups.items():
        idx = np.asarray(list(group), dtype=int)
        if len(idx) < 3:
            continue
        pairs: list[tuple[int, int]] = []
        for pos, i in enumerate(idx[:-1]):
            for j in idx[pos + 1 :]:
                if abs(gains[i] - gains[j]) >= MIN_PAIR_GAIN_MARGIN:
                    pairs.append((i, j))
        if not pairs:
            continue
        if len(pairs) > max_pairs_per_group:
            chosen = rng.choice(len(pairs), size=max_pairs_per_group, replace=False)
            pairs = [pairs[int(k)] for k in chosen]

        left = np.asarray([i for i, _j in pairs], dtype=int)
        right = np.asarray([j for _i, j in pairs], dtype=int)
        diff = values.iloc[left].reset_index(drop=True) - values.iloc[right].reset_index(drop=True)
        absdiff = diff.abs()
        diff.columns = [f"diff__{col}" for col in cols]
        absdiff.columns = [f"absdiff__{col}" for col in cols]
        y = (gains[left] > gains[right]).astype(int)
        gain_gap = np.abs(gains[left] - gains[right])
        weights = 1.0 + np.minimum(gain_gap / 0.05, 8.0)

        rev_diff = -diff
        rev_absdiff = absdiff.copy()
        rev_y = 1 - y
        rev_weights = weights.copy()
        x_parts.extend([pd.concat([diff, absdiff], axis=1), pd.concat([rev_diff, rev_absdiff], axis=1)])
        y_parts.extend([y, rev_y])
        weight_parts.extend([weights, rev_weights])

    if not x_parts:
        return pd.DataFrame(columns=pair_columns(cols)), np.array([], dtype=int), np.array([], dtype=np.float64)
    x = pd.concat(x_parts, ignore_index=True)
    y_all = np.concatenate(y_parts).astype(int)
    weights_all = np.concatenate(weight_parts).astype(np.float64)
    return x, y_all, weights_all


def reference_indices_by_target(cells: pd.DataFrame, max_refs: int, seed_key: str) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(stable_seed("refs", seed_key))
    out: dict[str, np.ndarray] = {}
    for target, part in cells.groupby("target", observed=True):
        idx = part.index.to_numpy(dtype=int)
        if len(idx) > max_refs:
            # Prefer decisive reference cells but keep deterministic coverage.
            decisive = part[part["decisive_action"].eq(1)].index.to_numpy(dtype=int)
            if len(decisive) >= max_refs // 2:
                keep_decisive = rng.choice(decisive, size=max_refs // 2, replace=False)
                remaining_pool = np.setdiff1d(idx, keep_decisive, assume_unique=False)
                keep_other = rng.choice(remaining_pool, size=max_refs - len(keep_decisive), replace=False)
                idx = np.concatenate([keep_decisive, keep_other])
            else:
                idx = rng.choice(idx, size=max_refs, replace=False)
        out[str(target)] = np.asarray(idx, dtype=int)
    return out


def score_cells_against_references(
    model: Any,
    apply_cells: pd.DataFrame,
    ref_cells: pd.DataFrame,
    cols: list[str],
    seed_key: str,
) -> np.ndarray:
    ref_map = reference_indices_by_target(ref_cells, MAX_REFERENCES_PER_TARGET, seed_key)
    apply_values = apply_cells[cols].replace([np.inf, -np.inf], np.nan).reset_index(drop=True)
    ref_values = ref_cells[cols].replace([np.inf, -np.inf], np.nan).reset_index(drop=True)
    scores = np.full(len(apply_cells), 0.5, dtype=np.float64)
    pair_col_names = pair_columns(cols)
    n_cols = len(cols)
    for target, apply_part in apply_cells.reset_index().groupby("target", observed=True):
        refs = ref_map.get(str(target))
        if refs is None or len(refs) == 0:
            continue
        apply_idx = apply_part["index"].to_numpy(dtype=int)
        left = apply_values.iloc[apply_idx].to_numpy(dtype=np.float64)
        right = ref_values.iloc[refs].to_numpy(dtype=np.float64)
        diff = left[:, None, :] - right[None, :, :]
        absdiff = np.abs(diff)
        pair_values = np.concatenate(
            [diff.reshape(-1, n_cols), absdiff.reshape(-1, n_cols)],
            axis=1,
        )
        x_pair = pd.DataFrame(pair_values, columns=pair_col_names)
        prob = model.predict_proba(x_pair)[:, 1].reshape(len(apply_idx), len(refs))
        scores[apply_idx] = prob.mean(axis=1)
    return scores


def fit_subject_contrastive_scores(
    train_cells: pd.DataFrame,
    test_cells: pd.DataFrame,
    feature_map: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    subjects = sorted(train_cells["subject_id"].astype(str).unique())
    y_support = train_cells["positive_gain"].astype(int).to_numpy()
    metric_rows: list[dict[str, Any]] = []
    score_summary_rows: list[dict[str, Any]] = []
    oof_predictions = train_cells[[
        "action_name",
        "row",
        "metric_row",
        "subject_id",
        "target",
        "target_idx",
        "realized_gain",
        "inverse_realized_gain",
        "positive_gain",
        "positive_inverse_gain",
        "decisive_action",
        "action_move",
    ]].copy()
    test_predictions = test_cells[[
        "action_name",
        "row",
        "metric_row",
        "subject_id",
        "target",
        "target_idx",
        "prior_prob",
        "candidate_prob",
        "inverse_prob",
        "action_move",
        "decisive_action",
    ]].copy()

    rng = np.random.default_rng(RANDOM_SEED + 818)
    for base_feature_name, cols in feature_map.items():
        cols = [col for col in cols if col in train_cells.columns and col in test_cells.columns]
        if not cols:
            continue
        for weight_mode in ["binary_preference", "tail_weighted_preference"]:
            feature_name = f"{weight_mode}__{base_feature_name}"
            oof_score = np.full(len(train_cells), 0.5, dtype=np.float64)
            fold_pair_counts: list[int] = []
            for subject in subjects:
                train_pool = train_cells[~train_cells["subject_id"].astype(str).eq(subject)].reset_index(drop=True)
                valid_pool = train_cells[train_cells["subject_id"].astype(str).eq(subject)].copy()
                valid_indices = valid_pool.index.to_numpy(dtype=int)
                x_pair, y_pair, pair_weight = build_pairwise_dataset(
                    train_pool,
                    cols,
                    max_pairs_per_group=MAX_PAIRS_PER_SUBJECT_TARGET,
                    seed_key=f"{feature_name}:{subject}",
                )
                fold_pair_counts.append(int(len(y_pair)))
                if len(y_pair) < 40 or len(np.unique(y_pair)) < 2:
                    oof_score[valid_indices] = 0.5
                    continue
                model = model_factory(stable_seed("subject-contrastive", feature_name, subject))
                if weight_mode == "tail_weighted_preference":
                    model.fit(x_pair, y_pair, histgradientboostingclassifier__sample_weight=pair_weight)
                else:
                    model.fit(x_pair, y_pair)
                scored = score_cells_against_references(
                    model,
                    valid_pool.reset_index(drop=True),
                    train_pool.reset_index(drop=True),
                    cols,
                    seed_key=f"{feature_name}:{subject}:oof",
                )
                oof_score[valid_indices] = scored

            full_pairs, full_y, full_weight = build_pairwise_dataset(
                train_cells.reset_index(drop=True),
                cols,
                max_pairs_per_group=MAX_PAIRS_PER_SUBJECT_TARGET,
                seed_key=f"{feature_name}:full",
            )
            if len(full_y) < 40 or len(np.unique(full_y)) < 2:
                test_score = np.full(len(test_cells), 0.5, dtype=np.float64)
            else:
                full_model = model_factory(stable_seed("subject-contrastive", feature_name, "full-test"))
                if weight_mode == "tail_weighted_preference":
                    full_model.fit(full_pairs, full_y, histgradientboostingclassifier__sample_weight=full_weight)
                else:
                    full_model.fit(full_pairs, full_y)
                test_score = score_cells_against_references(
                    full_model,
                    test_cells.reset_index(drop=True),
                    train_cells.reset_index(drop=True),
                    cols,
                    seed_key=f"{feature_name}:test",
                )

            oof_predictions[f"support_score_{feature_name}"] = oof_score
            test_predictions[f"support_score_{feature_name}"] = test_score

            metric_rows.extend(score_support_predictions(train_cells, oof_score, feature_name, "observed"))
            for repeat in range(NULL_REPEATS):
                shuffled = oof_score.copy()
                for target in TARGETS:
                    idx = np.where(train_cells["target"].eq(target).to_numpy())[0]
                    values = shuffled[idx].copy()
                    rng.shuffle(values)
                    shuffled[idx] = values
                metric_rows.extend(score_support_predictions(train_cells, shuffled, feature_name, f"target_shuffle_null_{repeat:02d}"))

            score_summary_rows.append(
                {
                    "feature_set": feature_name,
                    "pairwise_weight_mode": weight_mode,
                    "base_feature_set": base_feature_name,
                    "pairwise_training_examples_mean": float(np.mean(fold_pair_counts)) if fold_pair_counts else 0.0,
                    "pairwise_training_examples_min": int(np.min(fold_pair_counts)) if fold_pair_counts else 0,
                    "full_pairwise_training_examples": int(len(full_y)),
                    "support_auc": safe_auc(y_support, oof_score),
                    "support_ap": safe_ap(y_support, oof_score),
                    "score_mean": float(np.mean(oof_score)),
                    "score_std": float(np.std(oof_score)),
                }
            )

    metrics = pd.DataFrame(metric_rows)
    observed = metrics[metrics["null_family"].eq("observed")].copy()
    null = metrics[metrics["null_family"].ne("observed")].copy()
    if not null.empty:
        null_summary = (
            null.groupby(["feature_set", "selection_policy", "decoder_action"], observed=True)
            .agg(null_gain_mean=("selected_gain_sum", "mean"), null_gain_std=("selected_gain_sum", "std"))
            .reset_index()
        )
        observed = observed.merge(null_summary, on=["feature_set", "selection_policy", "decoder_action"], how="left")
        observed["gain_lift_vs_null"] = observed["selected_gain_sum"] - observed["null_gain_mean"]
        observed["gain_z_vs_null"] = (
            observed["selected_gain_sum"] - observed["null_gain_mean"]
        ) / observed["null_gain_std"].replace(0, np.nan)
    observed = add_robust_score(observed)
    score_summary = pd.DataFrame(score_summary_rows).sort_values(["support_auc", "support_ap"], ascending=False)
    return observed, oof_predictions, test_predictions, score_summary


def add_robust_score(metrics: pd.DataFrame) -> pd.DataFrame:
    out = metrics.copy()
    out["robust_score"] = (
        out["selected_gain_sum"].fillna(0.0)
        + 0.25 * out.get("gain_lift_vs_null", 0.0).fillna(0.0)
        + 0.08 * out.get("gain_z_vs_null", 0.0).fillna(0.0)
        + 0.25 * out["selected_positive_gain_rate"].fillna(0.0)
    )
    return out


def choose_release_policy(metrics: pd.DataFrame) -> dict[str, Any]:
    allowed = metrics[
        metrics["selection_policy"].isin(
            [
                "top05_all_cells",
                "top10_all_cells",
                "top18_decisive_only",
                "low05_inverse_decisive",
                "low08_inverse_decisive",
                "low10_inverse_decisive",
                "low18_inverse_decisive",
            ]
        )
    ].copy()
    if allowed.empty:
        allowed = metrics.copy()
    return allowed.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0].to_dict()


def select_policy_indices(cells: pd.DataFrame, score_col: str, policy: dict[str, Any]) -> np.ndarray:
    score = cells[score_col].to_numpy(dtype=np.float64)
    selection_policy = str(policy["selection_policy"])
    decisive_only = bool(policy["decisive_only"])
    fraction = float(policy["release_fraction"])
    descending = not selection_policy.startswith("low")
    idx = cells.index.to_numpy(dtype=int)
    if decisive_only:
        idx = idx[cells.loc[idx, "decisive_action"].eq(1).to_numpy()]
    if len(idx) == 0:
        return np.array([], dtype=int)
    k = max(1, int(round(len(idx) * fraction)))
    order_key = -score[idx] if descending else score[idx]
    return idx[np.argsort(order_key, kind="mergesort")[:k]]


def build_candidate(
    sample: pd.DataFrame,
    test_cells: pd.DataFrame,
    policy: dict[str, Any],
    train_priors: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = sample.copy()
    for target in TARGETS:
        out[target] = float(train_priors[target])
    score_col = f"support_score_{policy['feature_set']}"
    selected_idx = select_policy_indices(test_cells, score_col, policy)
    released = pd.Series(False, index=test_cells.index)
    released.loc[selected_idx] = True
    audit = test_cells.copy()
    audit["released"] = released.to_numpy()
    audit["decoder_action"] = str(policy["decoder_action"])
    value_col = "inverse_prob" if str(policy["decoder_action"]) == "inverse_toxic_memory" else "candidate_prob"
    for _, row in audit[audit["released"]].iterrows():
        out.at[int(row["row"]), str(row["target"])] = float(row[value_col])
    out[TARGETS] = out[TARGETS].clip(1e-5, 1.0 - 1e-5)
    return out, audit


def summarize_feature_families(metrics: pd.DataFrame, score_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    score_map = score_summary.set_index("feature_set").to_dict(orient="index") if not score_summary.empty else {}
    for feature_set, part in metrics.groupby("feature_set", observed=True):
        best = part.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0]
        base_name = feature_set.split("__", 1)[-1]
        weight_mode = feature_set.split("__", 1)[0] if "__" in feature_set else "unknown"
        if base_name in {"action_pair_only", "target_action_pair_only"}:
            family = "shortcut_baseline"
        elif "residual_energy" in base_name:
            family = "world_residual_energy"
        elif "predicted" in base_name:
            family = "world_predicted"
        else:
            family = "world_full"
        score_info = score_map.get(feature_set, {})
        rows.append(
            {
                "feature_set": feature_set,
                "base_feature_set": base_name,
                "pairwise_weight_mode": weight_mode,
                "family": family,
                "best_policy": best["selection_policy"],
                "best_decoder_action": best["decoder_action"],
                "support_auc": score_info.get("support_auc", best.get("support_auc")),
                "support_ap": score_info.get("support_ap", best.get("support_ap")),
                "selected_cells": int(best["selected_cells"]),
                "selected_gain_sum": float(best["selected_gain_sum"]),
                "selected_positive_gain_rate": float(best["selected_positive_gain_rate"]),
                "gain_lift_vs_null": float(best.get("gain_lift_vs_null", np.nan)),
                "gain_z_vs_null": float(best.get("gain_z_vs_null", np.nan)),
                "robust_score": float(best["robust_score"]),
                "full_pairwise_training_examples": int(score_info.get("full_pairwise_training_examples", 0)),
            }
        )
    return pd.DataFrame(rows).sort_values(["robust_score", "selected_gain_sum"], ascending=False)


def target_gain_table(oof_predictions: pd.DataFrame, policy: dict[str, Any]) -> pd.DataFrame:
    score_col = f"support_score_{policy['feature_set']}"
    selected = select_policy_indices(oof_predictions, score_col, policy)
    decoder = str(policy["decoder_action"])
    gain_col = "inverse_realized_gain" if decoder == "inverse_toxic_memory" else "realized_gain"
    frame = oof_predictions.loc[selected].copy()
    if frame.empty:
        return pd.DataFrame(columns=["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate"])
    return (
        frame.groupby("target", observed=True)
        .agg(
            selected_cells=(gain_col, "size"),
            gain_sum=(gain_col, "sum"),
            mean_gain=(gain_col, "mean"),
            positive_gain_rate=(gain_col, lambda x: float((x > 0).mean())),
        )
        .reset_index()
        .sort_values("target")
    )


def verdict(feature_summary: pd.DataFrame) -> str:
    baseline = feature_summary[feature_summary["base_feature_set"].eq("action_pair_only")]
    target_baseline = feature_summary[feature_summary["base_feature_set"].eq("target_action_pair_only")]
    world = feature_summary[feature_summary["family"].isin(["world_residual_energy", "world_full"])]
    if baseline.empty or target_baseline.empty or world.empty:
        return "missing_required_comparison"
    base_gain = max(float(baseline.iloc[0]["selected_gain_sum"]), float(target_baseline.iloc[0]["selected_gain_sum"]))
    best_world = world.sort_values(["robust_score", "selected_gain_sum"], ascending=False).iloc[0]
    world_gain = float(best_world["selected_gain_sum"])
    z = float(best_world.get("gain_z_vs_null", np.nan))
    auc = float(best_world.get("support_auc", np.nan))
    if world_gain > base_gain + 2.0 and z > 2.0 and auc > 0.55:
        return "subject_contrastive_world_state_positive"
    if world_gain > base_gain + 1.0 and world_gain > 0.0:
        return "subject_contrastive_world_state_weakly_positive"
    if world_gain > 0.0:
        return "subject_contrastive_signal_positive_but_not_above_shortcut"
    return "subject_contrastive_world_state_negative"


def build_markdown(
    summary: dict[str, Any],
    feature_summary: pd.DataFrame,
    score_summary: pd.DataFrame,
    metrics: pd.DataFrame,
    target_table: pd.DataFrame,
) -> str:
    top_metrics = metrics.sort_values(["robust_score", "selected_gain_sum"], ascending=False)
    return f"""# Subject-Contrastive Action-Support Core

## 한 줄 요약

HS-JEPA world state가 subject/target 평균을 외우는 shortcut이 아니라,
같은 subject-target 안에서 어떤 날의 row-target action이 더 건강한지를 맞힐 수 있는지 검증했다.

```text
same subject + same target action pair
  -> which day has healthier raw-memory action?
  -> held-out subject cells scored against peer references
  -> anchor-free action-support sensor
```

## 왜 HS-JEPA core 실험인가

이 실험의 target은 Q/S label probability가 아니다.
보이는 lifelog context에서 보이지 않는 `action-health ordering representation`을 예측한다.

일반 action-support classifier는 subject나 target prior를 외울 수 있다.
여기서는 pairwise supervision을 같은 subject/target 내부에만 만들기 때문에,
학습 신호가 다음 질문으로 바뀐다.

```text
이 사람의 이 target에서 A날과 B날 중 어느 날의 hidden human-state가
raw-memory action을 더 건강하게 만드는가?
```

그 다음 held-out subject의 row-target cell을 다른 subject의 peer reference와 비교해 score를 만든다.
즉 subject identity를 직접 쓰는 memory가 아니라, hidden episode/action-support geometry를 쓰는 실험이다.

## 사용하지 않은 정보

- public LB ledger: `{summary["uses_public_score_ledger"]}`
- prior submission probability: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API: `{summary["uses_proprietary_embedding_api"]}`

## Verdict

- verdict: `{summary["verdict"]}`
- selected feature set: `{summary["release_policy"]["feature_set"]}`
- selected policy: `{summary["release_policy"]["selection_policy"]}`
- selected decoder: `{summary["release_policy"]["decoder_action"]}`
- selected gain sum: `{format_float(summary["release_policy"]["selected_gain_sum"], 6)}`
- gain lift vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_lift_vs_null"), 6)}`
- gain z vs target-shuffle null: `{format_float(summary["release_policy"].get("gain_z_vs_null"), 6)}`
- released test cells: `{summary["released_test_cells"]}`

## Feature Family Summary

{markdown_table(feature_summary, ["feature_set", "base_feature_set", "pairwise_weight_mode", "family", "best_policy", "best_decoder_action", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score", "full_pairwise_training_examples"], max_rows=30)}

## Pairwise Score Summary

{markdown_table(score_summary, ["feature_set", "base_feature_set", "pairwise_weight_mode", "pairwise_training_examples_mean", "pairwise_training_examples_min", "full_pairwise_training_examples", "support_auc", "support_ap", "score_mean", "score_std"], max_rows=30)}

## Target Gain For Selected Policy

{markdown_table(target_table, ["target", "selected_cells", "gain_sum", "mean_gain", "positive_gain_rate"], max_rows=20)}

## Full Metric Leaderboard

{markdown_table(top_metrics, ["feature_set", "selection_policy", "decoder_action", "release_fraction", "support_auc", "support_ap", "selected_cells", "selected_gain_sum", "selected_positive_gain_rate", "gain_lift_vs_null", "gain_z_vs_null", "robust_score"], max_rows=36)}

## Anchor-Free Candidate

- candidate: `{summary["candidate_file"]}`
- validation: `{summary["validation"]}`

이 후보는 train prior에서 시작한다.
subject-contrastive support score가 release-worthy라고 본 row-target action만 sparse하게 release하거나,
low-support decisive action은 inverse-toxic 방향으로 움직인다.

## 해석

성공 조건:

```text
world-state pairwise feature가 action-only / target-action shortcut baseline보다 높은
selected gain과 target-shuffle null lift를 보여야 한다.
```

실패 조건:

```text
action-only baseline만 좋거나, world-state score가 null보다 낫지 않으면
현재 HS-JEPA core는 subject-contrastive episode ordering을 잡지 못한다.
```

현재 결론:

```text
HS-JEPA core의 일반성은 direct label prediction이 아니라
subject-contrastive action-health ordering으로 검증해야 한다.
```
"""


def run() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _labels = load_frames()
    frame = frame.copy()
    state, _view_metrics, _pred_cols, _energy_cols = build_world_model_state(frame)
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
    train_cells = make_action_cell_table(train, raw_oof, "raw_lifelog_memory")
    train_priors = train[TARGETS].astype(float).mean().to_dict()
    test_cells = make_test_action_table(test, raw_test_field, train_priors, "raw_lifelog_memory")

    sfc = world_feature_columns(state)
    state_cols = sorted(set(sfc["full"]))
    train_cells = append_row_features(train_cells, state_train[["metric_row"] + state_cols], state_cols)
    test_cells = append_row_features(test_cells, state_test[["metric_row"] + state_cols], state_cols)

    feature_map = make_feature_map(state)
    metrics, oof_predictions, test_predictions, score_summary = fit_subject_contrastive_scores(
        train_cells,
        test_cells,
        feature_map,
    )
    feature_summary = summarize_feature_families(metrics, score_summary)
    release_policy = choose_release_policy(metrics)
    target_table = target_gain_table(oof_predictions, release_policy)

    sample = pd.read_csv(SAMPLE_SUBMISSION)
    candidate, test_audit = build_candidate(sample, test_predictions, release_policy, train_priors)
    validation = validate_submission(candidate, sample)
    if not validation["valid"]:
        raise ValueError(f"candidate is not upload-safe: {validation['problems']}")
    candidate_name = f"submission_hsjepa_subject_contrastive_action_support_anchor_free_{short_hash(candidate)}_uploadsafe.csv"

    summary = {
        "package": "subject_contrastive_action_support_core",
        "status": "subject_contrastive_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "action_support_target": "same_subject_same_target_pairwise_realized_gain_ordering",
        "verdict": verdict(feature_summary),
        "release_policy": release_policy,
        "candidate_file": candidate_name,
        "validation": validation,
        "released_test_cells": int(test_audit["released"].sum()),
        "max_pairs_per_subject_target": MAX_PAIRS_PER_SUBJECT_TARGET,
        "max_references_per_target": MAX_REFERENCES_PER_TARGET,
        "min_pair_gain_margin": MIN_PAIR_GAIN_MARGIN,
    }

    metrics.to_csv(OUT_DIR / "subject_contrastive_policy_metrics.csv", index=False)
    feature_summary.to_csv(OUT_DIR / "subject_contrastive_feature_summary.csv", index=False)
    score_summary.to_csv(OUT_DIR / "subject_contrastive_score_summary.csv", index=False)
    target_table.to_csv(OUT_DIR / "subject_contrastive_selected_target_gain.csv", index=False)
    oof_predictions.to_csv(OUT_DIR / "subject_contrastive_oof_support_predictions.csv", index=False)
    test_predictions.to_csv(OUT_DIR / "subject_contrastive_test_support_predictions.csv", index=False)
    test_audit.to_csv(OUT_DIR / "subject_contrastive_test_release_audit.csv", index=False)
    candidate.to_csv(OUT_DIR / candidate_name, index=False)
    candidate.to_csv(ROOT / candidate_name, index=False)
    (OUT_DIR / "subject_contrastive_action_support_core_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = build_markdown(summary, feature_summary, score_summary, metrics, target_table)
    (OUT_DIR / "SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md").write_text(md, encoding="utf-8")
    PAPER_DOC.write_text(md, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    run()
