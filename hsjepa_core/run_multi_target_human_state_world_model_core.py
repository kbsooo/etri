#!/usr/bin/env python3
"""HS-JEPA multi-target human-state world-model core experiment.

This runner turns the accumulated HS-JEPA core modules into one architecture:

    visible human-life context
      -> predicted routine-break state
      -> predicted sleep-pressure state
      -> predicted personal-vs-peer cohort state
      -> unified hidden human-state bundle
      -> frozen low-trust Q/S probe

The pretext targets are label-free.  Q/S labels are used only after the
representation is frozen, through simple linear probes.
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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.human_state_world_model import finite_frame, rank01  # noqa: E402
from hsjepa_core.run_cohort_relative_world_model_core import (  # noqa: E402
    build_cohort_relative_world_state,
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
from hsjepa_core.run_routine_break_world_model_core import (  # noqa: E402
    build_routine_break_world_state,
)
from hsjepa_core.run_sleep_pressure_world_model_core import (  # noqa: E402
    build_sleep_pressure_world_state,
    json_safe,
)


OUT_DIR = ROOT / "hsjepa_core" / "outputs" / "multi_target_human_state_world_model_core"
PAPER_DOC = ROOT / "paper_hsjepa_core" / "MULTI_TARGET_HUMAN_STATE_WORLD_MODEL_CORE_KO.md"
RANDOM_SEED = 20260613


def short_hash(frame: pd.DataFrame) -> str:
    arr = frame[TARGETS].to_numpy(dtype=np.float64)
    return hashlib.sha256(np.round(arr, 10).tobytes()).hexdigest()[:8]


def prefixed(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return frame.rename(columns={col: f"{prefix}__{col}" for col in frame.columns})


def prefixed_cols(prefix: str, cols: list[str]) -> list[str]:
    return [f"{prefix}__{col}" for col in cols]


def fit_core_latent(frame: pd.DataFrame, cols: list[str], prefix: str, dims: int = 18) -> tuple[pd.DataFrame, list[str]]:
    n_components = max(1, min(dims, len(cols), len(frame) - 1))
    latent = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        PCA(n_components=n_components, random_state=RANDOM_SEED),
    ).fit_transform(finite_frame(frame, cols))
    out = pd.DataFrame(
        latent,
        index=frame.index,
        columns=[f"{prefix}_c{idx + 1}" for idx in range(n_components)],
    )
    return out, list(out.columns)


def block_norms(frame: pd.DataFrame, blocks: dict[str, list[str]]) -> pd.DataFrame:
    out = pd.DataFrame(index=frame.index)
    for name, cols in blocks.items():
        if not cols:
            continue
        values = SimpleImputer(strategy="median").fit_transform(finite_frame(frame, cols))
        values = StandardScaler().fit_transform(values)
        out[f"mthswm_norm_{name}"] = np.sqrt(np.mean(np.square(values), axis=1))
        out[f"mthswm_absmean_{name}"] = np.mean(np.abs(values), axis=1)
        out[f"mthswm_std_{name}"] = np.std(values, axis=1)
    norm_cols = [col for col in out.columns if col.startswith("mthswm_norm_")]
    if norm_cols:
        out["mthswm_cross_target_norm_mean"] = out[norm_cols].mean(axis=1)
        out["mthswm_cross_target_norm_std"] = out[norm_cols].std(axis=1).fillna(0.0)
        out["mthswm_cross_target_norm_max"] = out[norm_cols].max(axis=1)
        out["mthswm_cross_target_norm_rank"] = rank01(out["mthswm_cross_target_norm_mean"].to_numpy(dtype=np.float64))
    return out


def build_multi_target_world_state(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    routine_state, routine_metrics, routine_colsets = build_routine_break_world_state(frame)
    sleep_state, sleep_metrics, sleep_colsets = build_sleep_pressure_world_state(frame)
    cohort_state, cohort_metrics, _subject_fingerprint, cohort_colsets = build_cohort_relative_world_state(frame)

    routine_state = prefixed(routine_state, "routine")
    sleep_state = prefixed(sleep_state, "sleep")
    cohort_state = prefixed(cohort_state, "cohort")

    routine_pred = prefixed_cols("routine", routine_colsets["routine_break_predicted"])
    routine_energy = prefixed_cols("routine", routine_colsets["routine_break_energy"])
    sleep_pred = prefixed_cols("sleep", sleep_colsets["sleep_pressure_predicted"])
    sleep_energy = prefixed_cols("sleep", sleep_colsets["sleep_pressure_energy"])
    cohort_pred = prefixed_cols("cohort", cohort_colsets["cohort_relative_predicted"])
    cohort_energy = prefixed_cols("cohort", cohort_colsets["cohort_relative_energy"])
    cohort_observed = prefixed_cols("cohort", cohort_colsets["cohort_relative_observed"])
    cohort_full = prefixed_cols("cohort", cohort_colsets["cohort_relative_full"])

    state = pd.concat([routine_state, sleep_state, cohort_state], axis=1)
    predicted_blocks = {
        "routine_break": routine_pred,
        "sleep_pressure": sleep_pred,
        "cohort_relative": cohort_pred,
    }
    energy_blocks = {
        "routine_break_energy": routine_energy,
        "sleep_pressure_energy": sleep_energy,
        "cohort_relative_energy": cohort_energy,
    }
    diagnostics = block_norms(state, predicted_blocks | energy_blocks)
    state = pd.concat([state, diagnostics], axis=1)

    predicted_cols = sorted(set(routine_pred + sleep_pred + cohort_pred))
    energy_cols = sorted(set(routine_energy + sleep_energy + cohort_energy + list(diagnostics.columns)))
    predicted_energy_cols = sorted(set(predicted_cols + energy_cols))
    core_latent, core_latent_cols = fit_core_latent(state, predicted_energy_cols, "mthswm_core_latent", dims=18)
    predicted_latent, predicted_latent_cols = fit_core_latent(state, predicted_cols, "mthswm_predicted_latent", dims=16)
    state = pd.concat([state, core_latent, predicted_latent], axis=1)

    routine_metrics = routine_metrics.copy()
    routine_metrics.insert(0, "module", "routine_break")
    sleep_metrics = sleep_metrics.copy()
    sleep_metrics.insert(0, "module", "sleep_pressure")
    cohort_metrics = cohort_metrics.copy()
    cohort_metrics.insert(0, "module", "cohort_relative")
    pretext_metrics = pd.concat([routine_metrics, sleep_metrics, cohort_metrics], ignore_index=True, sort=False)
    for column in ("context", "target", "task"):
        if column not in pretext_metrics.columns:
            pretext_metrics[column] = "NA"
    pretext_metrics["context"] = pretext_metrics["context"].fillna("NA")

    colsets = {
        "routine_break_predicted": routine_pred,
        "sleep_pressure_predicted": sleep_pred,
        "cohort_relative_predicted": cohort_pred,
        "multi_target_predicted": predicted_cols,
        "multi_target_energy": energy_cols,
        "multi_target_predicted_energy": predicted_energy_cols,
        "multi_target_core_latent": core_latent_cols,
        "multi_target_predicted_latent": predicted_latent_cols,
        "multi_target_safe_core": sorted(set(core_latent_cols + predicted_latent_cols + energy_cols)),
        "cohort_relative_observed": cohort_observed,
        "cohort_relative_full": cohort_full,
    }
    return state, pretext_metrics, colsets


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
    core = subject_all[subject_all["feature_set"].eq("multi_target_core_latent_calibrated10")]
    predicted = subject_all[subject_all["feature_set"].eq("multi_target_predicted_calibrated10")]
    safe_core = subject_all[subject_all["feature_set"].eq("multi_target_safe_core_calibrated10")]
    single_names = [
        "routine_break_predicted_calibrated10",
        "sleep_pressure_predicted_calibrated10",
        "cohort_relative_predicted_calibrated10",
    ]
    singles = subject_all[subject_all["feature_set"].isin(single_names)].sort_values("logloss")
    best_single = None if singles.empty else singles.iloc[0].to_dict()
    best_subject = subject_all.sort_values("logloss").head(1)
    pretext = pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False)
    nn_all = nn_metrics[nn_metrics["target"].eq("all")].sort_values("lift", ascending=False)

    prior_value = None if prior.empty else float(prior["logloss"].iloc[0])
    core_value = None if core.empty else float(core["logloss"].iloc[0])
    predicted_value = None if predicted.empty else float(predicted["logloss"].iloc[0])
    safe_core_value = None if safe_core.empty else float(safe_core["logloss"].iloc[0])
    best_single_value = None if best_single is None else float(best_single["logloss"])
    return {
        "package": "multi_target_human_state_world_model_core",
        "status": "multi_target_human_state_world_model_core_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_proprietary_embedding_api": False,
        "uses_label_as_pretext_target": False,
        "primary_probe_feature_set": "multi_target_predicted_calibrated10",
        "negative_ablation": "multi_target_core_latent_calibrated10 compresses route axes and underperforms",
        "hidden_targets": [
            "subject_relative_routine_break",
            "label_free_sleep_pressure",
            "personal_vs_peer_cohort_relative_state",
        ],
        "best_pretext": None if pretext.empty else pretext.iloc[0].to_dict(),
        "subject_prior_logloss": prior_value,
        "multi_target_core_latent_calibrated_logloss": core_value,
        "multi_target_predicted_calibrated_logloss": predicted_value,
        "multi_target_safe_core_calibrated_logloss": safe_core_value,
        "multi_target_core_delta_vs_prior": None if prior_value is None or core_value is None else core_value - prior_value,
        "multi_target_predicted_delta_vs_prior": None
        if prior_value is None or predicted_value is None
        else predicted_value - prior_value,
        "multi_target_predicted_delta_vs_best_single": None
        if best_single_value is None or predicted_value is None
        else predicted_value - best_single_value,
        "multi_target_safe_core_delta_vs_prior": None
        if prior_value is None or safe_core_value is None
        else safe_core_value - prior_value,
        "best_single_predicted_probe": best_single,
        "multi_target_core_delta_vs_best_single": None
        if best_single_value is None or core_value is None
        else core_value - best_single_value,
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
    best_pretext = summary.get("best_pretext") or {}
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
    core_delta = summary.get("multi_target_core_delta_vs_prior")
    predicted_delta = summary.get("multi_target_predicted_delta_vs_prior")
    predicted_single_delta = summary.get("multi_target_predicted_delta_vs_best_single")
    single_delta = summary.get("multi_target_core_delta_vs_best_single")
    verdict = "core_positive_with_route_preservation" if predicted_delta is not None and predicted_delta < 0 else "core_mixed_or_negative"
    return f"""# Multi-Target Human-State World Model Core

## 한 줄 요약

HS-JEPA를 단일 hidden target 실험에서 통합 world model로 올린 실험이다.

```text
visible human-life context
  -> predicted routine-break state
  -> predicted sleep-pressure state
  -> predicted personal-vs-peer cohort state
  -> unified hidden human-state bundle
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `{verdict}`
- public LB ledger 사용: `{summary["uses_public_score_ledger"]}`
- prior submission probability 사용: `{summary["uses_prior_submission_probabilities"]}`
- proprietary embedding API 사용: `{summary["uses_proprietary_embedding_api"]}`
- label을 pretext target으로 사용: `{summary["uses_label_as_pretext_target"]}`
- primary probe: `{summary["primary_probe_feature_set"]}`
- route-preserving predicted bundle delta vs prior: `{format_float(predicted_delta, 6)}`
- route-preserving predicted bundle delta vs best single predicted target: `{format_float(predicted_single_delta, 6)}`
- compressed core-latent delta vs prior: `{format_float(core_delta, 6)}`
- compressed core-latent delta vs best single predicted target: `{format_float(single_delta, 6)}`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label을 pretext target으로 쓰지 않는다.
대신 보이는 생활 context가 세 종류의 보이지 않는 human-state representation을 동시에 예측해야 한다.

1. routine-break: 개인 루틴이 얼마나 깨졌는가
2. sleep-pressure: 수면 압력/각성/회복부하가 어떤 상태인가
3. cohort-relative: 개인 기준과 peer 기준에서 오늘은 어디에 놓이는가

따라서 architecture claim은 다음이다.

```text
HS-JEPA는 하나의 label을 맞히는 모델이 아니라,
여러 human-state target representation을 예측해
사람의 생활 상태를 더 선형적인 latent bundle로 만든다.
```

## Pretext 결과

- best module: `{best_pretext.get("module", "NA")}`
- best task: `{best_pretext.get("task", "NA")}`
- best target: `{best_pretext.get("target", "NA")}`
- best component-corr lift vs null: `{format_float(best_pretext.get("component_corr_lift_vs_null"), 6)}`
- best R2 lift vs null: `{format_float(best_pretext.get("r2_lift_vs_null"), 6)}`

{markdown_table(
    pretext_metrics.sort_values("component_corr_lift_vs_null", ascending=False).head(18),
    ["module", "task", "target", "context", "component_corr_lift_vs_null", "r2_lift_vs_null"],
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

이 파일은 core 증거 자체가 아니라, frozen multi-target representation을 competition label로 번역한 probe candidate다.

## 해석

positive이면:

```text
여러 hidden target을 함께 예측하는 HS-JEPA bundle이 subject-heldout label manifold를 더 잘 정렬한다.
단, route 축을 보존해야 하며 PCA식 단일 latent 압축은 오히려 신호를 죽일 수 있다.
```

negative이면:

```text
각 hidden target은 따로는 의미가 있지만, 단순 결합만으로는 더 일반적인 HS-JEPA core가 되지 않는다.
다음 breakthrough는 bundle 결합이 아니라 target별 listener responsibility 또는 adapter-free route selection이어야 한다.
```
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame, _labels = load_frames()
    views = make_views(frame)
    raw_cols = sorted({col for view in views for col in view.columns})

    state, pretext_metrics, colsets = build_multi_target_world_state(frame)
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
        "routine_break_predicted": colsets["routine_break_predicted"],
        "sleep_pressure_predicted": colsets["sleep_pressure_predicted"],
        "cohort_relative_predicted": colsets["cohort_relative_predicted"],
        "multi_target_predicted": colsets["multi_target_predicted"],
        "multi_target_energy": colsets["multi_target_energy"],
        "multi_target_predicted_energy": colsets["multi_target_predicted_energy"],
        "multi_target_predicted_latent": colsets["multi_target_predicted_latent"],
        "multi_target_core_latent": colsets["multi_target_core_latent"],
        "multi_target_safe_core": colsets["multi_target_safe_core"],
        "cohort_relative_observed": colsets["cohort_relative_observed"],
        "cohort_relative_full": colsets["cohort_relative_full"],
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
            if key
            not in {
                "prior_only",
                "cohort_relative_full",
                "cohort_relative_observed",
            }
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
        colsets["multi_target_predicted"],
    )
    candidate_name = f"submission_hsjepa_multi_target_human_state_world_model_probe_{short_hash(submission)}_uploadsafe.csv"
    candidate_path = ROOT / candidate_name
    submission.to_csv(candidate_path, index=False)
    submission.to_csv(OUT_DIR / candidate_name, index=False)

    summary = summarize(pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    state.to_csv(OUT_DIR / "multi_target_human_state_world_model_state.csv", index=False)
    pretext_metrics.to_csv(OUT_DIR / "multi_target_human_state_world_model_pretext_metrics.csv", index=False)
    probe_metrics.to_csv(OUT_DIR / "multi_target_human_state_world_model_probe_metrics.csv", index=False)
    probe_predictions.to_csv(OUT_DIR / "multi_target_human_state_world_model_probe_predictions.csv", index=False)
    nn_metrics.to_csv(OUT_DIR / "multi_target_human_state_world_model_neighbor_consistency.csv", index=False)
    leakage.to_csv(OUT_DIR / "multi_target_human_state_world_model_subject_leakage.csv", index=False)
    with (OUT_DIR / "multi_target_human_state_world_model_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(json_safe(summary), handle, indent=2, ensure_ascii=False)
    markdown = build_markdown(summary, pretext_metrics, probe_metrics, nn_metrics, leakage, candidate_name)
    (OUT_DIR / "MULTI_TARGET_HUMAN_STATE_WORLD_MODEL_CORE_KO.md").write_text(markdown, encoding="utf-8")
    PAPER_DOC.write_text(markdown, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": summary["status"],
                "candidate_file": candidate_name,
                "multi_target_core_delta_vs_prior": summary["multi_target_core_delta_vs_prior"],
                "multi_target_predicted_delta_vs_prior": summary["multi_target_predicted_delta_vs_prior"],
                "multi_target_core_delta_vs_best_single": summary["multi_target_core_delta_vs_best_single"],
                "multi_target_predicted_delta_vs_best_single": summary["multi_target_predicted_delta_vs_best_single"],
                "best_pretext_lift": None
                if summary["best_pretext"] is None
                else summary["best_pretext"]["component_corr_lift_vs_null"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
