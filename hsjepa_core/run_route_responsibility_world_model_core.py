#!/usr/bin/env python3
"""HS-JEPA route-responsibility world-model core experiment.

Previous evidence showed that route-preserving multi-target predicted axes
work better than a compressed latent.  This runner asks the next question:

    can the core infer, without labels, which hidden route carries
    non-redundant human-state information for each row?

It builds a label-free cross-route responsibility field:

    other predicted routes -> held-out predicted route representation
    residual energy -> route responsibility / salience
    responsibility-weighted route axes -> frozen low-trust Q/S probe
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import (  # noqa: E402
    WorldModelConfig,
    component_correlation,
    encode_latent,
    finite_frame,
    rank01,
    ridge_predict_oof,
    weighted_r2,
)
from hsjepa_core.run_human_state_world_model_core import (  # noqa: E402
    build_downstream_probe_submission,
    calibrated_probe_metrics,
    chronological_folds,
    evaluate_split,
    make_views,
    subject_folds,
    subject_leakage_probe,
)
from hsjepa_core.run_lifelog_core_state_evidence import (  # noqa: E402
    TARGETS,
    catalog_features,
    format_float,
    load_frames,
    markdown_table,
)
from hsjepa_core.run_multi_target_human_state_world_model_core import (  # noqa: E402
    build_multi_target_world_state,
)
from hsjepa_core.run_sleep_pressure_world_model_core import json_safe  # noqa: E402


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "route_responsibility_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "ROUTE_RESPONSIBILITY_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260613
CONFIG = WorldModelConfig(
    latent_dims_per_view=6,
    future_state_dims=8,
    ridge_alpha=12.0,
    group_folds=5,
    cohort_count=4,
    random_state=RANDOM_SEED,
)


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def row_softmax(values: np.ndarray, temperature: float = 0.35) -> np.ndarray:
    scaled = values / max(temperature, 1e-6)
    scaled = scaled - np.nanmax(scaled, axis=1, keepdims=True)
    exp = np.exp(np.nan_to_num(scaled, nan=0.0, posinf=0.0, neginf=0.0))
    total = exp.sum(axis=1, keepdims=True)
    total[total <= 1e-12] = 1.0
    return exp / total


def build_route_responsibility_state(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    base_state, base_metrics, base_colsets = build_multi_target_world_state(frame)
    route_blocks = {
        "routine_break": base_colsets["routine_break_predicted"],
        "sleep_pressure": base_colsets["sleep_pressure_predicted"],
        "cohort_relative": base_colsets["cohort_relative_predicted"],
    }
    groups = frame["subject_id"].astype(str).to_numpy()
    responsibility_data: dict[str, np.ndarray] = {}
    metric_rows: list[dict[str, Any]] = []
    route_energy_cols: list[str] = []
    route_rank_cols: list[str] = []
    route_norm_cols: list[str] = []
    weighted_cols: list[str] = []
    residual_cols: list[str] = []

    for route, target_cols in route_blocks.items():
        context_cols = sorted(set(col for name, cols in route_blocks.items() if name != route for col in cols))
        target_latent, _ = encode_latent(base_state, target_cols, CONFIG.latent_dims_per_view, RANDOM_SEED)
        pred, null_pred = ridge_predict_oof(base_state, context_cols, target_latent, groups, CONFIG)
        residual = target_latent - pred
        energy = np.sqrt(np.mean(np.square(residual), axis=1))
        target_values = SimpleImputer(strategy="median").fit_transform(finite_frame(base_state, target_cols))
        target_values = StandardScaler().fit_transform(target_values)
        route_norm = np.sqrt(np.mean(np.square(target_values), axis=1))
        energy_col = f"rrwm_route_unique_energy_{route}"
        rank_col = f"rrwm_route_unique_rank_{route}"
        norm_col = f"rrwm_route_norm_{route}"
        responsibility_data[energy_col] = energy
        responsibility_data[rank_col] = rank01(energy)
        responsibility_data[norm_col] = route_norm
        route_energy_cols.append(energy_col)
        route_rank_cols.append(rank_col)
        route_norm_cols.append(norm_col)
        for comp in range(target_latent.shape[1]):
            responsibility_data[f"rrwm_crossroute_pred_{route}_c{comp + 1}"] = pred[:, comp]
            responsibility_data[f"rrwm_crossroute_resid_{route}_c{comp + 1}"] = residual[:, comp]
            residual_cols.append(f"rrwm_crossroute_resid_{route}_c{comp + 1}")
        metric_rows.append(
            {
                "task": "cross_route_to_hidden_route",
                "target_route": route,
                "components": int(target_latent.shape[1]),
                "context_feature_count": len(context_cols),
                "target_feature_count": len(target_cols),
                "component_corr": component_correlation(target_latent, pred),
                "null_component_corr": component_correlation(target_latent, null_pred),
                "component_corr_lift_vs_null": component_correlation(target_latent, pred)
                - component_correlation(target_latent, null_pred),
                "r2": weighted_r2(target_latent, pred),
                "null_r2": weighted_r2(target_latent, null_pred),
                "r2_lift_vs_null": weighted_r2(target_latent, pred) - weighted_r2(target_latent, null_pred),
            }
        )

    state = pd.DataFrame(responsibility_data, index=frame.index)
    salience_basis = np.column_stack(
        [
            rank01(state[f"rrwm_route_unique_energy_{route}"].to_numpy(dtype=np.float64))
            + 0.35 * rank01(state[f"rrwm_route_norm_{route}"].to_numpy(dtype=np.float64))
            for route in route_blocks
        ]
    )
    weights = row_softmax(salience_basis, temperature=0.42)
    extra_data: dict[str, np.ndarray] = {}
    for idx, route in enumerate(route_blocks):
        weight_col = f"rrwm_responsibility_{route}"
        extra_data[weight_col] = weights[:, idx]
        for col in route_blocks[route]:
            weighted_col = f"rrwm_weighted_{col}"
            extra_data[weighted_col] = base_state[col].to_numpy(dtype=np.float64) * weights[:, idx]
            weighted_cols.append(weighted_col)
    route_names = list(route_blocks)
    extra_data["rrwm_responsibility_entropy"] = -np.sum(weights * np.log(np.clip(weights, 1e-12, 1.0)), axis=1) / math.log(len(route_names))
    extra_data["rrwm_responsibility_max"] = weights.max(axis=1)
    sorted_weights = np.sort(weights, axis=1)
    extra_data["rrwm_responsibility_margin"] = sorted_weights[:, -1] - sorted_weights[:, -2]
    extra_data["rrwm_responsibility_argmax"] = np.argmax(weights, axis=1).astype(float)
    score_cols = [f"rrwm_responsibility_{route}" for route in route_blocks] + [
        "rrwm_responsibility_entropy",
        "rrwm_responsibility_max",
        "rrwm_responsibility_margin",
        "rrwm_responsibility_argmax",
    ]
    extra_data["rrwm_unique_energy_mean"] = state[route_energy_cols].mean(axis=1).to_numpy(dtype=np.float64)
    extra_data["rrwm_unique_energy_max"] = state[route_energy_cols].max(axis=1).to_numpy(dtype=np.float64)
    extra_data["rrwm_unique_rank_mean"] = state[route_rank_cols].mean(axis=1).to_numpy(dtype=np.float64)
    extra_data["rrwm_route_norm_mean"] = state[route_norm_cols].mean(axis=1).to_numpy(dtype=np.float64)
    score_cols.extend(
        [
            "rrwm_unique_energy_mean",
            "rrwm_unique_energy_max",
            "rrwm_unique_rank_mean",
            "rrwm_route_norm_mean",
        ]
    )
    state = pd.concat([state, pd.DataFrame(extra_data, index=frame.index)], axis=1).copy()
    route_metrics = pd.DataFrame(metric_rows)
    base_metrics = base_metrics.copy()
    base_metrics["task_family"] = "base_multi_target_pretext"
    route_metrics["task_family"] = "route_responsibility_pretext"
    metrics = pd.concat([base_metrics, route_metrics], ignore_index=True, sort=False)
    full_state = pd.concat([base_state.add_prefix("base__"), state], axis=1)
    colsets = {
        "base_multi_target_predicted": [f"base__{col}" for col in base_colsets["multi_target_predicted"]],
        "base_multi_target_energy": [f"base__{col}" for col in base_colsets["multi_target_energy"]],
        "route_responsibility_scores": score_cols,
        "route_weighted_predicted": weighted_cols,
        "route_cross_residual": residual_cols,
        "route_responsibility_full": sorted(set(score_cols + weighted_cols + residual_cols + route_energy_cols + route_rank_cols + route_norm_cols)),
        "route_weighted_plus_scores": sorted(set(score_cols + weighted_cols)),
        "route_weighted_plus_residual": sorted(set(weighted_cols + residual_cols)),
    }
    return full_state, metrics, colsets


def neighbor_consistency(
    train_frame: pd.DataFrame,
    features: pd.DataFrame,
    feature_sets: dict[str, list[str]],
) -> pd.DataFrame:
    labels = train_frame[TARGETS].astype(int).to_numpy()
    rng = np.random.default_rng(RANDOM_SEED)
    rows: list[dict[str, Any]] = []
    for feature_set, cols in feature_sets.items():
        if not cols:
            continue
        x = SimpleImputer(strategy="median").fit_transform(finite_frame(features, cols))
        x = StandardScaler().fit_transform(x)
        if x.shape[1] > 24:
            x = PCA(n_components=min(24, x.shape[0] - 1, x.shape[1]), random_state=RANDOM_SEED).fit_transform(x)
        nn = NearestNeighbors(n_neighbors=min(6, len(features)), metric="euclidean")
        nn.fit(x)
        _, idx = nn.kneighbors(x)
        idx = idx[:, 1:]
        near = []
        random = []
        for row in range(len(features)):
            near.append((labels[idx[row]] == labels[row]).mean(axis=0))
            pool = [item for item in range(len(features)) if item != row]
            rnd = rng.choice(pool, size=idx.shape[1], replace=False)
            random.append((labels[rnd] == labels[row]).mean(axis=0))
        near_arr = np.vstack(near)
        random_arr = np.vstack(random)
        for target_idx, target in enumerate(TARGETS):
            rows.append(
                {
                    "feature_set": feature_set,
                    "target": target,
                    "neighbor_match_rate": float(near_arr[:, target_idx].mean()),
                    "random_match_rate": float(random_arr[:, target_idx].mean()),
                    "lift": float(near_arr[:, target_idx].mean() - random_arr[:, target_idx].mean()),
                }
            )
        rows.append(
            {
                "feature_set": feature_set,
                "target": "all",
                "neighbor_match_rate": float(near_arr.mean()),
                "random_match_rate": float(random_arr.mean()),
                "lift": float(near_arr.mean() - random_arr.mean()),
            }
        )
    return pd.DataFrame(rows)


def summarize(
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> dict[str, Any]:
    subject_all = probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
    chrono_all = probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
    prior = subject_all[subject_all["feature_set"].eq("prior_only")]
    base = subject_all[subject_all["feature_set"].eq("base_multi_target_predicted_calibrated10")]
    weighted = subject_all[subject_all["feature_set"].eq("route_weighted_predicted_calibrated10")]
    full = subject_all[subject_all["feature_set"].eq("route_responsibility_full_calibrated10")]
    best_route = subject_all[
        subject_all["feature_set"].str.startswith("route_") | subject_all["feature_set"].str.startswith("route_responsibility")
    ].sort_values("logloss")
    best_subject = subject_all.sort_values("logloss").head(1)
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    route_pretext = pretext_metrics[pretext_metrics["task_family"].eq("route_responsibility_pretext")].sort_values(
        "component_corr_lift_vs_null",
        ascending=False,
    )
    nn_all = nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False)
    prior_value = None if prior.empty else float(prior["logloss"].iloc[0])
    base_value = None if base.empty else float(base["logloss"].iloc[0])
    weighted_value = None if weighted.empty else float(weighted["logloss"].iloc[0])
    full_value = None if full.empty else float(full["logloss"].iloc[0])
    best_route_row = None if best_route.empty else best_route.iloc[0].to_dict()
    return {
        "package": "route_responsibility_world_model_core",
        "status": "route_responsibility_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "hidden_target": "label_free_cross_route_responsibility",
        "best_pretext": None if pretext.empty else pretext.iloc[0].to_dict(),
        "best_route_pretext": None if route_pretext.empty else route_pretext.iloc[0].to_dict(),
        "subject_prior_logloss": prior_value,
        "base_multi_target_predicted_logloss": base_value,
        "primary_probe_feature_set": "route_weighted_predicted_calibrated10",
        "route_weighted_predicted_logloss": weighted_value,
        "route_responsibility_full_logloss": full_value,
        "route_weighted_delta_vs_prior": None if prior_value is None or weighted_value is None else weighted_value - prior_value,
        "route_weighted_delta_vs_base_multi_target": None
        if base_value is None or weighted_value is None
        else weighted_value - base_value,
        "route_full_delta_vs_prior": None if prior_value is None or full_value is None else full_value - prior_value,
        "best_route_probe": best_route_row,
        "subject_best_probe": None if best_subject.empty else best_subject.iloc[0].to_dict(),
        "chronological_best_probe": None if chrono_all.empty else chrono_all.sort_values("logloss").iloc[0].to_dict(),
        "best_neighbor_consistency": None if nn_all.empty else nn_all.iloc[0].to_dict(),
        "subject_leakage": leakage.to_dict(orient="records"),
        "candidate_file": candidate_file,
    }


def build_markdown(
    summary: dict[str, Any],
    pretext_metrics: pd.DataFrame,
    probe_metrics: pd.DataFrame,
    nn_metrics: pd.DataFrame,
    leakage: pd.DataFrame,
    candidate_file: str,
) -> str:
    weighted_delta = summary.get("route_weighted_delta_vs_prior")
    base_delta = summary.get("route_weighted_delta_vs_base_multi_target")
    if weighted_delta is not None and weighted_delta < 0 and base_delta is not None and base_delta < 0:
        verdict = "core_positive_and_base_improving"
    elif weighted_delta is not None and weighted_delta < 0:
        verdict = "core_positive_but_not_base_improving"
    else:
        verdict = "core_mixed_or_negative"
    subject_all = (
        probe_metrics[(probe_metrics["split"].eq("subject_heldout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    chrono_all = (
        probe_metrics[(probe_metrics["split"].eq("chronological_holdout")) & (probe_metrics["target"].eq("all"))]
        .sort_values("logloss")
        .loc[:, ["feature_set", "logloss", "auc"]]
    )
    route_pretext = pretext_metrics[pretext_metrics["task_family"].eq("route_responsibility_pretext")].sort_values(
        "component_corr_lift_vs_null",
        ascending=False,
    )
    return f"""# Route-Responsibility World Model Core

## 한 줄 요약

route-preserving multi-target HS-JEPA 위에서,
각 row가 어떤 hidden route에 책임을 둬야 하는지 label 없이 추정하는 실험이다.

```text
other predicted routes
  -> held-out route representation
  -> cross-route residual energy
  -> label-free route responsibility
  -> responsibility-weighted human-state axes
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- primary probe: `{summary["primary_probe_feature_set"]}`
- route-weighted delta vs prior: `{format_float(weighted_delta, 6)}`
- route-weighted delta vs base multi-target: `{format_float(base_delta, 6)}`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label을 route responsibility target으로 쓰지 않는다.
대신 route 간 예측 가능성만 본다.

예를 들어 routine-break와 sleep-pressure만으로 cohort-relative route를 잘 예측할 수 없다면,
그 row에서 cohort route는 non-redundant한 책임을 가진다.

즉 core 질문은 다음이다.

```text
HS-JEPA가 hidden route bundle 안에서
어느 route가 그 row의 독립적인 human-state 정보를 들고 있는지
label 없이 추정할 수 있는가?
```

## Route Pretext 결과

{markdown_table(
    route_pretext,
    ["task", "target_route", "component_corr", "null_component_corr", "component_corr_lift_vs_null", "r2_lift_vs_null"],
)}

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

{markdown_table(subject_all, ["feature_set", "logloss", "auc"])}

## Chronological Row-Heldout Probe

{markdown_table(chrono_all, ["feature_set", "logloss", "auc"])}

## Nearest-Neighbor State Consistency

{markdown_table(
    nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False),
    ["feature_set", "neighbor_match_rate", "random_match_rate", "lift"],
)}

## Subject Leakage Diagnostic

{markdown_table(
    leakage.sort_values("subject_id_accuracy", ascending=False),
    ["feature_set", "subject_id_accuracy", "chance_accuracy", "leakage_lift_vs_chance"],
)}

## Downstream Probe Candidate

- file: `{candidate_file}`

이 파일은 core evidence 자체가 아니라, route responsibility weighted axes를 competition label로 번역한 downstream probe candidate다.

## 해석

positive이면:

```text
HS-JEPA core는 route를 보존할 뿐 아니라,
어떤 route가 row의 non-redundant hidden state를 들고 있는지 label 없이 추정할 수 있다.
단, base multi-target을 이기지 못하면 route weighting은 core diagnostic이지 최종 representation replacement는 아니다.
```

negative이면:

```text
route responsibility는 label-free redundancy만으로는 부족하다.
다음에는 listener/target별 responsibility를 weak supervision 또는 action-health diagnostic과 분리해서 배워야 한다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _labels = load_frames()
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})
    state, pretext_metrics, colsets = build_route_responsibility_state(frame)
    state = pd.concat(
        [frame[["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"]].reset_index(drop=True), state.reset_index(drop=True)],
        axis=1,
    )
    catalog = catalog_features(frame)
    combined = pd.concat(
        [frame.reset_index(drop=True), state.drop(columns=["subject_id", "sleep_date", "lifelog_date", "split", "metric_row"])],
        axis=1,
    )
    feature_sets = {
        "prior_only": [],
        "raw_lifelog_pca": raw_cols,
        "existing_cohort_human_state": catalog.core_state,
        "base_multi_target_predicted": colsets["base_multi_target_predicted"],
        "base_multi_target_energy": colsets["base_multi_target_energy"],
        "route_responsibility_scores": colsets["route_responsibility_scores"],
        "route_weighted_predicted": colsets["route_weighted_predicted"],
        "route_weighted_plus_scores": colsets["route_weighted_plus_scores"],
        "route_weighted_plus_residual": colsets["route_weighted_plus_residual"],
        "route_responsibility_full": colsets["route_responsibility_full"],
    }

    train_mask = frame["split"].eq("train").to_numpy()
    train_frame = frame.loc[train_mask].reset_index(drop=True)
    train_features = combined.loc[train_mask].reset_index(drop=True)
    subject_metrics, subject_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "subject_heldout",
        subject_folds(train_frame),
    )
    chrono_metrics, chrono_predictions = evaluate_split(
        train_frame,
        train_features,
        feature_sets,
        "chronological_holdout",
        chronological_folds(train_frame),
    )
    probe_metrics = pd.concat([subject_metrics, chrono_metrics], ignore_index=True)
    probe_predictions = pd.concat([subject_predictions, chrono_predictions], ignore_index=True)
    probe_metrics = pd.concat([probe_metrics, calibrated_probe_metrics(probe_predictions)], ignore_index=True, sort=False)
    nn_metrics = neighbor_consistency(train_frame, train_features, feature_sets)
    leakage = subject_leakage_probe(
        train_frame,
        train_features,
        {
            key: value
            for key, value in feature_sets.items()
            if key not in {"prior_only", "route_responsibility_full"}
        },
    )

    test_mask = frame["split"].eq("test").to_numpy()
    test_frame = frame.loc[test_mask].reset_index(drop=True)
    test_features = combined.loc[test_mask].reset_index(drop=True)
    submission = build_downstream_probe_submission(
        train_frame,
        test_frame,
        train_features,
        test_features,
        colsets["route_weighted_predicted"],
    )
    candidate_name = f"submission_hsjepa_route_responsibility_world_model_probe_{short_hash(submission)}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_name, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = summarize(pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    state.to_csv(OUT_DIR / "route_responsibility_world_model_state.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "route_responsibility_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "route_responsibility_world_model_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "route_responsibility_world_model_probe_predictions.csv", index=False)
    nn_metrics.to_csv(OUT_DIR / "route_responsibility_world_model_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "route_responsibility_world_model_subject_leakage.csv", index=False)
    with (OUT_DIR / "route_responsibility_world_model_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(json_safe(summary), handle, indent=2, ensure_ascii=False)
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    (OUT_DIR / "ROUTE_RESPONSIBILITY_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "route_weighted_delta_vs_prior": summary["route_weighted_delta_vs_prior"],
                "route_weighted_delta_vs_base_multi_target": summary["route_weighted_delta_vs_base_multi_target"],
                "best_route_pretext_lift": None
                if summary["best_route_pretext"] is None
                else summary["best_route_pretext"]["component_corr_lift_vs_null"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
