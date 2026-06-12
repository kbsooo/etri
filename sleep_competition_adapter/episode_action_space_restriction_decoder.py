#!/usr/bin/env python3
"""Episode-conditioned action-space restriction decoder for HS-JEPA.

The previous selective-assignment ablation showed an important failure mode:
adding row episode scores as ordinary features did not change the release law.
The decoder collapsed back to a route-disagreement prior-reset rule.

This experiment changes the interface.  The row episode state is not a feature
fed into the gain model.  It constrains the action space before release:

    If HS-JEPA says this row is a hidden reset episode, which listener routes
    are allowed to compete for each row-target cell?

This is a stronger architectural test than feature injection.  If it works, the
HS-JEPA row-state encoder acts as a responsibility allocator that limits toxic
actions.  If it fails, row episodes are useful diagnostics but not yet a
release-grade action-space controller.
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

from sleep_competition_adapter.contextual_listener_route_selector import (  # noqa: E402
    build_cell_and_pair_frames,
    build_temporal_oof_frames,
)
from sleep_competition_adapter.core_oof_action_health_benchmark import (  # noqa: E402
    TARGETS,
    load_world,
    logloss,
    prediction_catalog,
    raw_feature_cols,
    short_hash,
    validate_submission,
)
from sleep_competition_adapter.episode_selective_assignment_decoder import (  # noqa: E402
    attach_episode_features,
    build_oof_episode_state,
    fit_row_episode_for_test,
)
from sleep_competition_adapter.failure_boundary_law_distillation import (  # noqa: E402
    add_law_features,
    feature_views as law_feature_views,
    make_model,
    model_description,
)
from sleep_competition_adapter.raw_knn_failure_detector import prepare_gain_pairs  # noqa: E402
from sleep_competition_adapter.raw_knn_override_safety_jury import (  # noqa: E402
    expert_family,
    target_family_stratified_null,
    target_stratified_null,
)


OUT = ROOT / "sleep_competition_adapter" / "outputs" / "episode_action_space_restriction_decoder"
OUT.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 20260612
TOP_FRACS = [0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.15]
THRESHOLDS = [-0.02, -0.01, 0.0, 0.005, 0.01, 0.02, 0.04, 0.08]
NULL_REPEATS = 1600

SCORE_SPECS = [
    {
        "model_name": "route_tree_depth2_leaf28",
        "family": "shallow_tree",
        "depth": 2,
        "leaf": 28,
    },
    {
        "model_name": "route_tree_depth3_leaf24",
        "family": "shallow_tree",
        "depth": 3,
        "leaf": 24,
    },
]


def score_oof_pairs(frame: pd.DataFrame, features: list[str], spec: dict[str, Any]) -> np.ndarray:
    pred = np.full(len(frame), np.nan, dtype=float)
    for subject in sorted(frame["subject_id"].unique()):
        train = frame[~frame["subject_id"].eq(subject)]
        valid = frame[frame["subject_id"].eq(subject)]
        model = make_model(spec)
        model.fit(train[features], train["gain"].to_numpy(dtype=float))
        pred[valid.index.to_numpy()] = model.predict(valid[features])
    if np.isnan(pred).any():
        raise RuntimeError("OOF action-space score contains NaN")
    return pred


def episode_thresholds(episode: pd.DataFrame) -> dict[str, float]:
    rows = episode[["row", "subject_id", "row_episode_score"]].drop_duplicates()
    scores = rows["row_episode_score"].to_numpy(dtype=float)
    return {
        "q70": float(np.quantile(scores, 0.70)),
        "q80": float(np.quantile(scores, 0.80)),
        "q90": float(np.quantile(scores, 0.90)),
    }


def action_space_policies(thresholds: dict[str, float]) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = [
        {"name": "unrestricted_route_law", "kind": "unrestricted", "episode_threshold": -np.inf},
    ]
    for label, threshold in thresholds.items():
        policies.extend([
            {
                "name": f"episode_rows_only_any_route_{label}",
                "kind": "episode_rows_only_any_route",
                "episode_threshold": threshold,
            },
            {
                "name": f"episode_family_space_{label}",
                "kind": "episode_family_space",
                "episode_threshold": threshold,
            },
            {
                "name": f"episode_exact_route_space_{label}",
                "kind": "episode_exact_route_space",
                "episode_threshold": threshold,
            },
            {
                "name": f"episode_veto_family_mismatch_{label}",
                "kind": "episode_veto_family_mismatch",
                "episode_threshold": threshold,
            },
        ])
    for beta, gamma in [(0.08, 0.04), (0.14, 0.08), (0.22, 0.12)]:
        policies.append({
            "name": f"episode_responsibility_score_beta{beta:g}_gamma{gamma:g}",
            "kind": "episode_responsibility_score",
            "episode_threshold": thresholds["q70"],
            "beta": beta,
            "gamma": gamma,
        })
    return policies


def apply_action_space(frame: pd.DataFrame, score_col: str, policy: dict[str, Any]) -> pd.DataFrame:
    out = frame.copy()
    out["selection_score"] = out[score_col].astype(float)
    out["expert_family"] = out["expert"].astype(str).map(expert_family)
    out["episode_high"] = out["row_episode_score"].astype(float).ge(float(policy["episode_threshold"]))
    kind = str(policy["kind"])
    if kind == "unrestricted":
        out["action_allowed"] = True
    elif kind == "episode_rows_only_any_route":
        out["action_allowed"] = out["episode_high"]
    elif kind == "episode_family_space":
        out["action_allowed"] = out["episode_high"] & out["family_matches_row_episode"].astype(bool)
    elif kind == "episode_exact_route_space":
        out["action_allowed"] = out["episode_high"] & out["expert_matches_row_episode_route"].astype(bool)
    elif kind == "episode_veto_family_mismatch":
        out["action_allowed"] = (~out["episode_high"]) | out["family_matches_row_episode"].astype(bool)
    elif kind == "episode_responsibility_score":
        beta = float(policy.get("beta", 0.0))
        gamma = float(policy.get("gamma", 0.0))
        family_match = out["family_matches_row_episode"].astype(float)
        episode_pressure = out["row_episode_score"].astype(float).clip(lower=0.0)
        out["selection_score"] = (
            out["selection_score"]
            + beta * episode_pressure * family_match
            - gamma * episode_pressure * (1.0 - family_match)
        )
        out["action_allowed"] = True
    else:
        raise KeyError(kind)
    return out[out["action_allowed"]].copy()


def best_candidate_for_policy(scored_pairs: pd.DataFrame, score_col: str, policy: dict[str, Any], law_name: str) -> pd.DataFrame:
    allowed = apply_action_space(scored_pairs, score_col, policy)
    rows = []
    if allowed.empty:
        return pd.DataFrame(columns=[
            "cell_key", "row", "subject_id", "target", "expert", "expert_family", "expert_pred",
            "selection_score", "true_gain", "row_episode_score", "row_episode_route",
            "expert_matches_row_episode_route", "family_matches_row_episode", "action_space_policy",
            "law_name",
        ])
    for cell_key, group in allowed.groupby("cell_key", sort=False):
        best = group.sort_values("selection_score", ascending=False, kind="mergesort").iloc[0]
        rows.append({
            "cell_key": cell_key,
            "row": int(best["row"]),
            "subject_id": best["subject_id"],
            "target": best["target"],
            "expert": str(best["expert"]),
            "expert_family": str(best["expert_family"]),
            "expert_pred": float(best["expert_pred"]),
            "selection_score": float(best["selection_score"]),
            "true_gain": float(best["gain"]) if "gain" in best.index else np.nan,
            "row_episode_score": float(best.get("row_episode_score", 0.0)),
            "row_episode_route": str(best.get("row_episode_route", "")),
            "expert_matches_row_episode_route": float(best.get("expert_matches_row_episode_route", 0.0)),
            "family_matches_row_episode": float(best.get("family_matches_row_episode", 0.0)),
            "action_space_policy": str(policy["name"]),
            "law_name": law_name,
        })
    return pd.DataFrame(rows)


def selected_by_policy(candidates: pd.DataFrame, selection_policy: str, param: float, total_cells: int) -> set[str]:
    if candidates.empty:
        return set()
    if selection_policy == "topfrac":
        k = max(1, int(round(total_cells * param)))
        return set(candidates.sort_values("selection_score", ascending=False, kind="mergesort").head(k)["cell_key"])
    if selection_policy == "threshold":
        return set(candidates[candidates["selection_score"].gt(param)]["cell_key"])
    raise KeyError(selection_policy)


def evaluate_release_policy(
    cell_frame: pd.DataFrame,
    candidates: pd.DataFrame,
    selection_policy: str,
    param: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    selected = selected_by_policy(candidates, selection_policy, param, len(cell_frame))
    candidate_map = candidates.set_index("cell_key") if not candidates.empty else pd.DataFrame()
    pred = []
    gains = []
    actions = []
    for rec in cell_frame.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred.append(float(cand["expert_pred"]))
            gain = float(cand["true_gain"])
            gains.append(gain)
            actions.append({
                "cell_key": cell_key,
                "row": int(rec["row"]),
                "subject_id": rec["subject_id"],
                "target": rec["target"],
                "selected_expert": str(cand["expert"]),
                "expert_family": str(cand["expert_family"]),
                "selection_score": float(cand["selection_score"]),
                "true_gain": gain,
                "row_episode_score": float(cand["row_episode_score"]),
                "row_episode_route": str(cand["row_episode_route"]),
                "expert_matches_row_episode_route": float(cand["expert_matches_row_episode_route"]),
                "family_matches_row_episode": float(cand["family_matches_row_episode"]),
                "raw_pred": float(rec["pred__raw_knn_blend"]),
                "selected_pred": float(cand["expert_pred"]),
                "switched": True,
            })
        else:
            pred.append(float(rec["pred__raw_knn_blend"]))
            gains.append(0.0)
    actions_df = pd.DataFrame(actions)
    metric = {
        "selection_policy": selection_policy,
        "selection_param": float(param),
        "logloss": logloss(cell_frame["y"].to_numpy(dtype=float), np.asarray(pred, dtype=float)),
        "switched_cells": int(len(selected)),
        "available_candidate_cells": int(candidates["cell_key"].nunique()) if not candidates.empty else 0,
        "mean_realized_gain_all_cells": float(np.sum(gains) / len(cell_frame)),
        "mean_realized_gain_switched": float(actions_df["true_gain"].mean()) if len(actions_df) else 0.0,
        "positive_true_gain_rate": float((actions_df["true_gain"] > 0).mean()) if len(actions_df) else 0.0,
        "episode_route_match_rate": float(actions_df["expert_matches_row_episode_route"].mean()) if len(actions_df) else 0.0,
        "episode_family_match_rate": float(actions_df["family_matches_row_episode"].mean()) if len(actions_df) else 0.0,
        "mean_row_episode_score_switched": float(actions_df["row_episode_score"].mean()) if len(actions_df) else 0.0,
    }
    return metric, actions_df


def evaluate_action_spaces(cell_frame: pd.DataFrame, scored_pairs: pd.DataFrame, score_cols: dict[str, dict[str, Any]], thresholds: dict[str, float]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    raw = logloss(cell_frame["y"].to_numpy(dtype=float), cell_frame["pred__raw_knn_blend"].to_numpy(dtype=float))
    rng = np.random.default_rng(RANDOM_STATE)
    metrics = [{
        "law_name": "raw_knn_blend_baseline",
        "model_name": "raw_knn_blend",
        "action_space_policy": "baseline",
        "action_space_kind": "baseline",
        "selection_policy": "baseline",
        "selection_param": 0.0,
        "logloss": raw,
        "switched_cells": 0,
        "available_candidate_cells": 0,
        "mean_realized_gain_all_cells": 0.0,
        "mean_realized_gain_switched": 0.0,
        "positive_true_gain_rate": 0.0,
        "episode_route_match_rate": 0.0,
        "episode_family_match_rate": 0.0,
        "mean_row_episode_score_switched": 0.0,
        "target_null_p_ge_observed": 1.0,
        "target_family_null_p_ge_observed": 1.0,
        "target_null_z": 0.0,
        "target_family_null_z": 0.0,
    }]
    all_candidates = []
    all_actions = []
    best_overall: dict[str, Any] | None = None
    best_restricted: dict[str, Any] | None = None
    for law_name, meta in score_cols.items():
        score_col = str(meta["score_col"])
        spec = meta["spec"]
        for space_policy in action_space_policies(thresholds):
            candidates = best_candidate_for_policy(scored_pairs, score_col, space_policy, law_name)
            if candidates.empty:
                continue
            all_candidates.append(candidates)
            for frac in TOP_FRACS:
                metric, actions = evaluate_release_policy(cell_frame, candidates, "topfrac", frac)
                metric.update({
                    "law_name": law_name,
                    "model_name": str(spec["model_name"]),
                    "model_family": str(spec["family"]),
                    "action_space_policy": str(space_policy["name"]),
                    "action_space_kind": str(space_policy["kind"]),
                    "episode_threshold": float(space_policy.get("episode_threshold", np.nan)),
                })
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = law_name
                    actions["action_space_policy"] = str(space_policy["name"])
                    actions["selection_policy"] = "topfrac"
                    actions["selection_param"] = float(frac)
                    all_actions.append(actions)
                rec = {"metric": metric, "actions": actions, "candidates": candidates, "space_policy": space_policy, "spec": spec, "features": meta["features"], "score_col": score_col}
                if best_overall is None or metric["logloss"] < best_overall["metric"]["logloss"]:
                    best_overall = rec
                if space_policy["kind"] != "unrestricted" and (best_restricted is None or metric["logloss"] < best_restricted["metric"]["logloss"]):
                    best_restricted = rec
            for threshold in THRESHOLDS:
                metric, actions = evaluate_release_policy(cell_frame, candidates, "threshold", threshold)
                metric.update({
                    "law_name": law_name,
                    "model_name": str(spec["model_name"]),
                    "model_family": str(spec["family"]),
                    "action_space_policy": str(space_policy["name"]),
                    "action_space_kind": str(space_policy["kind"]),
                    "episode_threshold": float(space_policy.get("episode_threshold", np.nan)),
                })
                metric.update(target_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metric.update(target_family_stratified_null(candidates, actions, len(cell_frame), rng, repeats=NULL_REPEATS))
                metrics.append(metric)
                if len(actions):
                    actions["law_name"] = law_name
                    actions["action_space_policy"] = str(space_policy["name"])
                    actions["selection_policy"] = "threshold"
                    actions["selection_param"] = float(threshold)
                    all_actions.append(actions)
                rec = {"metric": metric, "actions": actions, "candidates": candidates, "space_policy": space_policy, "spec": spec, "features": meta["features"], "score_col": score_col}
                if best_overall is None or metric["logloss"] < best_overall["metric"]["logloss"]:
                    best_overall = rec
                if space_policy["kind"] != "unrestricted" and (best_restricted is None or metric["logloss"] < best_restricted["metric"]["logloss"]):
                    best_restricted = rec
    if best_overall is None or best_restricted is None:
        raise RuntimeError("no action-space policy evaluated")
    return (
        pd.DataFrame(metrics).sort_values("logloss", kind="mergesort").reset_index(drop=True),
        pd.concat(all_actions, ignore_index=True) if all_actions else pd.DataFrame(),
        pd.concat(all_candidates, ignore_index=True) if all_candidates else pd.DataFrame(),
        best_overall,
        best_restricted,
    )


def fit_and_score_test_pairs(
    train_pairs: pd.DataFrame,
    test_pairs: pd.DataFrame,
    features: list[str],
    spec: dict[str, Any],
) -> pd.Series:
    model = make_model(spec)
    model.fit(train_pairs[features], train_pairs["gain"].to_numpy(dtype=float))
    return pd.Series(model.predict(test_pairs[features]), index=test_pairs.index), model_description(model, features, spec)


def build_test_pairs(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    raw_cols: list[str],
    row_pair_frame: pd.DataFrame,
    row_meta: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = features_frame[features_frame["split"].eq("train")].copy().reset_index(drop=True)
    train[TARGETS] = labels[TARGETS].to_numpy(dtype=float)
    test = features_frame[features_frame["split"].eq("test")].copy().reset_index(drop=True)
    catalog, _audit = prediction_catalog(train, test, raw_cols)
    test_cells, test_pairs = build_cell_and_pair_frames(test, None, catalog, "test")
    test_episode = fit_row_episode_for_test(row_pair_frame, row_meta, test_cells)
    raw_pred = test_cells[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    test_gain_pairs = test_pairs[test_pairs["expert"].ne("raw_knn_blend")].copy().reset_index(drop=True)
    test_gain_pairs = test_gain_pairs.merge(raw_pred, on="cell_key", how="left")
    test_gain_pairs = add_law_features(test_gain_pairs)
    test_gain_pairs = attach_episode_features(test_gain_pairs, test_episode)
    return test_cells, test_gain_pairs, test_episode


def train_final_submission(
    features_frame: pd.DataFrame,
    labels: pd.DataFrame,
    sample: pd.DataFrame,
    raw_cols: list[str],
    gain_pairs: pd.DataFrame,
    row_pair_frame: pd.DataFrame,
    row_meta: dict[str, Any],
    release: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    test_cells, test_pairs, _test_episode = build_test_pairs(features_frame, labels, raw_cols, row_pair_frame, row_meta)
    test_scores, description = fit_and_score_test_pairs(gain_pairs, test_pairs, release["features"], release["spec"])
    score_col = "predicted_action_space_gain"
    test_pairs[score_col] = test_scores
    candidates = best_candidate_for_policy(test_pairs, score_col, release["space_policy"], str(release["metric"]["law_name"]))
    selected = selected_by_policy(
        candidates,
        str(release["metric"]["selection_policy"]),
        float(release["metric"]["selection_param"]),
        len(test_cells),
    )
    candidate_map = candidates.set_index("cell_key") if not candidates.empty else pd.DataFrame()
    pred_vec = []
    actions = []
    for rec in test_cells.to_dict("records"):
        cell_key = rec["cell_key"]
        if cell_key in selected:
            cand = candidate_map.loc[cell_key]
            pred = float(cand["expert_pred"])
            selected_expert = str(cand["expert"])
            switched = True
        else:
            pred = float(rec["pred__raw_knn_blend"])
            selected_expert = "raw_knn_blend"
            switched = False
            cand = {}
        pred_vec.append(pred)
        actions.append({
            "cell_key": cell_key,
            "row": int(rec["row"]),
            "subject_id": rec["subject_id"],
            "target": rec["target"],
            "selected_expert": selected_expert,
            "candidate_expert": str(cand.get("expert", "")) if switched else "",
            "candidate_family": str(cand.get("expert_family", "")) if switched else "",
            "selection_score": float(cand.get("selection_score", np.nan)) if switched else np.nan,
            "row_episode_score": float(cand.get("row_episode_score", 0.0)) if switched else 0.0,
            "row_episode_route": str(cand.get("row_episode_route", "")) if switched else "",
            "raw_pred": float(rec["pred__raw_knn_blend"]),
            "selected_pred": pred,
            "switched": switched,
        })
    pred = np.asarray(pred_vec, dtype=float).reshape((len(sample), len(TARGETS)))
    submission = sample.copy()
    submission[TARGETS] = np.clip(pred, 1e-5, 1 - 1e-5)
    return submission, pd.DataFrame(actions), description


def markdown_table(frame: pd.DataFrame, max_rows: int = 16) -> str:
    show = frame.head(max_rows).copy()
    cols = list(show.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for rec in show.to_dict("records"):
        vals = []
        for col in cols:
            val = rec[col]
            vals.append(f"{val:.6f}" if isinstance(val, float) else str(val))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def build_markdown(readout: dict[str, Any], metrics: pd.DataFrame, selected: pd.DataFrame, description: dict[str, Any]) -> str:
    top_cols = [
        "law_name",
        "action_space_policy",
        "selection_policy",
        "selection_param",
        "logloss",
        "switched_cells",
        "mean_realized_gain_all_cells",
        "episode_family_match_rate",
        "target_family_null_p_ge_observed",
    ]
    release_actions = selected[
        selected["law_name"].eq(readout["release_law_name"])
        & selected["action_space_policy"].eq(readout["release_action_space_policy"])
        & selected["selection_policy"].eq(readout["release_selection_policy"])
        & selected["selection_param"].eq(readout["release_selection_param"])
    ] if len(selected) else pd.DataFrame()
    target_counts = release_actions["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).rename_axis("target").reset_index(name="count")
    family_counts = release_actions["expert_family"].value_counts().rename_axis("expert_family").reset_index(name="count") if len(release_actions) else pd.DataFrame(columns=["expert_family", "count"])
    features = pd.DataFrame(description["top_features"])
    lines = [
        "# Episode Action-Space Restriction Decoder",
        "",
        "## 한 줄 요약",
        "",
        "row episode state를 gain model feature로 넣지 않고, action 후보 공간을 제한하는 controller로 사용했다.",
        "",
        "## 재현 명령",
        "",
        "```bash",
        "python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py",
        "```",
        "",
        "public LB score ledger, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.",
        "",
        "## 핵심 결과",
        "",
        f"- raw KNN OOF logloss: `{readout['raw_knn_oof_logloss']:.6f}`",
        f"- unrestricted best OOF: `{readout['best_unrestricted_oof_logloss']:.6f}`",
        f"- best restricted OOF: `{readout['best_restricted_oof_logloss']:.6f}`",
        f"- restricted delta vs raw: `{readout['best_restricted_delta_vs_raw_knn']:.6f}`",
        f"- restricted delta vs unrestricted: `{readout['best_restricted_delta_vs_unrestricted']:.6f}`",
        f"- release action-space policy: `{readout['release_action_space_policy']}`",
        f"- release switched OOF cells: `{readout['release_switched_cells']}`",
        f"- release target+family null p-value: `{readout['release_target_family_null_p_ge_observed']:.6f}`",
        f"- generated candidate: `{readout['candidate_file']}`",
        f"- same prediction as failure-boundary law: `{readout['candidate_matches_failure_boundary_law']}`",
        "",
        "## 판정",
        "",
        readout["architecture_verdict"],
        "",
        "## Release target counts",
        "",
        markdown_table(target_counts, max_rows=10),
        "",
        "## Release expert-family counts",
        "",
        markdown_table(family_counts, max_rows=10),
        "",
        "## Release scorer top features",
        "",
        markdown_table(features, max_rows=20),
        "",
        "## Top policies",
        "",
        markdown_table(metrics[top_cols], max_rows=16),
        "",
        "## 논문용 해석",
        "",
        "이 실험은 HS-JEPA의 row-state encoder를 decoder feature가 아니라 action-space controller로 사용했다.",
        "feature injection이 실패했기 때문에, 더 강한 구조적 결합을 검증한 것이다.",
        "",
        "restricted policy가 unrestricted policy보다 낮은 OOF를 만들면, row episode state가 action toxicity를 줄이는 controller라는 주장이 강화된다.",
        "반대로 restricted policy가 뒤처지면, 현재 row episode는 diagnostic으로는 유효하지만 action-space를 자를 만큼 충분한 causal/responsibility state는 아니라는 결론이다.",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    features_frame, labels, sample, raw_cols_from_module = load_world()
    raw_cols = raw_feature_cols(features_frame) if not raw_cols_from_module else raw_cols_from_module
    cell_frame, pair_frame = build_temporal_oof_frames(features_frame, labels, raw_cols)
    episode, row_pair_frame, row_meta = build_oof_episode_state(cell_frame)
    raw_pred = cell_frame[["cell_key", "pred__raw_knn_blend"]].rename(columns={"pred__raw_knn_blend": "raw_pred"})
    gain_pairs = prepare_gain_pairs(cell_frame, pair_frame).merge(raw_pred, on="cell_key", how="left", suffixes=("", "_dup"))
    if "raw_pred_dup" in gain_pairs.columns:
        gain_pairs = gain_pairs.drop(columns=["raw_pred_dup"])
    gain_pairs = add_law_features(gain_pairs)
    gain_pairs = attach_episode_features(gain_pairs, episode)
    features = law_feature_views(gain_pairs)["route_disagreement_law"]
    leak_cols = [col for col in features if "loss" in col or "gain" in col or col in {"y", "raw_loss"}]
    if leak_cols:
        raise RuntimeError(f"leaky action-space feature columns detected: {leak_cols}")
    score_cols = {}
    for spec in SCORE_SPECS:
        col = f"pred__{spec['model_name']}"
        gain_pairs[col] = score_oof_pairs(gain_pairs, features, spec)
        score_cols[spec["model_name"]] = {"score_col": col, "spec": spec, "features": features}
    thresholds = episode_thresholds(episode)
    metrics, selected, candidates, best_overall, best_restricted = evaluate_action_spaces(cell_frame, gain_pairs, score_cols, thresholds)
    raw = float(metrics[metrics["law_name"].eq("raw_knn_blend_baseline")]["logloss"].iloc[0])
    unrestricted = metrics[metrics["action_space_kind"].eq("unrestricted")].iloc[0].to_dict()
    release = best_restricted
    submission, test_actions, description = train_final_submission(
        features_frame,
        labels,
        sample,
        raw_cols,
        gain_pairs,
        row_pair_frame,
        row_meta,
        release,
    )
    validate_submission(submission, sample)
    suffix = short_hash(submission)
    candidate_file = f"submission_hsjepa_episode_action_space_restriction_decoder_{suffix}_uploadsafe.csv"
    submission.to_csv(ROOT / candidate_file, index=False)
    submission.to_csv(OUT / candidate_file, index=False)
    failure_file = ROOT / "submission_hsjepa_failure_boundary_law_distillation_65ce2d48_uploadsafe.csv"
    candidate_matches_failure_law = False
    if failure_file.exists():
        failure = pd.read_csv(failure_file)
        candidate_matches_failure_law = bool(np.allclose(submission[TARGETS].to_numpy(float), failure[TARGETS].to_numpy(float), atol=1e-12, rtol=0.0))
    release_metric = release["metric"]
    best_restricted_delta_vs_unrestricted = float(release_metric["logloss"] - float(unrestricted["logloss"]))
    if best_restricted_delta_vs_unrestricted < -1e-9:
        verdict = "restricted action-space가 unrestricted route law를 이겼다. row episode state가 action toxicity를 줄이는 controller로 작동했다는 positive evidence다."
    elif abs(best_restricted_delta_vs_unrestricted) <= 1e-9:
        verdict = "restricted action-space가 unrestricted route law와 동률이다. episode controller가 action-space를 바꾸지 못했거나 같은 prior-reset law로 수렴했다."
    else:
        verdict = "restricted action-space가 unrestricted route law보다 나쁘다. 현재 row episode state는 diagnostic으로는 살아 있지만 action-space controller로는 과하게 잘라낸다."
    readout = {
        "package": "episode_action_space_restriction_decoder",
        "status": "episode_action_space_restriction_ready",
        "uses_public_score_ledger": False,
        "uses_prior_submission_probabilities": False,
        "uses_action_teacher": False,
        "uses_frontier_file": False,
        "raw_knn_oof_logloss": raw,
        "best_overall_law_name": str(best_overall["metric"]["law_name"]),
        "best_overall_action_space_policy": str(best_overall["metric"]["action_space_policy"]),
        "best_overall_oof_logloss": float(best_overall["metric"]["logloss"]),
        "best_unrestricted_law_name": str(unrestricted["law_name"]),
        "best_unrestricted_oof_logloss": float(unrestricted["logloss"]),
        "best_restricted_law_name": str(release_metric["law_name"]),
        "best_restricted_action_space_policy": str(release_metric["action_space_policy"]),
        "best_restricted_oof_logloss": float(release_metric["logloss"]),
        "best_restricted_delta_vs_raw_knn": float(release_metric["logloss"] - raw),
        "best_restricted_delta_vs_unrestricted": best_restricted_delta_vs_unrestricted,
        "release_law_name": str(release_metric["law_name"]),
        "release_model_name": str(release_metric["model_name"]),
        "release_action_space_policy": str(release_metric["action_space_policy"]),
        "release_action_space_kind": str(release_metric["action_space_kind"]),
        "release_selection_policy": str(release_metric["selection_policy"]),
        "release_selection_param": float(release_metric["selection_param"]),
        "release_oof_logloss": float(release_metric["logloss"]),
        "release_switched_cells": int(release_metric["switched_cells"]),
        "release_available_candidate_cells": int(release_metric["available_candidate_cells"]),
        "release_positive_true_gain_rate": float(release_metric["positive_true_gain_rate"]),
        "release_episode_family_match_rate": float(release_metric["episode_family_match_rate"]),
        "release_target_null_p_ge_observed": float(release_metric["target_null_p_ge_observed"]),
        "release_target_family_null_p_ge_observed": float(release_metric["target_family_null_p_ge_observed"]),
        "release_top_features": description["top_features"],
        "release_nonzero_feature_count": int(description["nonzero_feature_count"]),
        "episode_thresholds": thresholds,
        "candidate_file": candidate_file,
        "root_candidate_file": candidate_file,
        "candidate_matches_failure_boundary_law": candidate_matches_failure_law,
        "test_switched_cells": int(test_actions["switched"].sum()),
        "test_switched_rows": int(test_actions.loc[test_actions["switched"], "row"].nunique()),
        "test_selected_expert_counts": test_actions.loc[test_actions["switched"], "selected_expert"].value_counts().to_dict(),
        "test_target_counts": test_actions.loc[test_actions["switched"], "target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict(),
        "architecture_verdict": verdict,
        "submission_priority": "high_information_sensor_episode_action_space_restriction",
    }
    metrics.to_csv(OUT / "episode_action_space_policy_table.csv", index=False)
    selected.to_csv(OUT / "episode_action_space_selected_oof_cells.csv", index=False)
    candidates.to_csv(OUT / "episode_action_space_oof_candidates.csv", index=False)
    gain_pairs.to_csv(OUT / "episode_action_space_oof_gain_pairs.csv", index=False)
    test_actions.to_csv(OUT / "episode_action_space_test_actions.csv", index=False)
    (OUT / "episode_action_space_readout.json").write_text(json.dumps(readout, ensure_ascii=False, indent=2), encoding="utf-8")
    md = build_markdown(readout, metrics, selected, description)
    (OUT / "EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md").write_text(md, encoding="utf-8")
    (ROOT / "paper_hsjepa_core" / "EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md").write_text(md, encoding="utf-8")
    return readout


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
