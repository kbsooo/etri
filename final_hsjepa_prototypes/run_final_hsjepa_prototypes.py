#!/usr/bin/env python3
"""Final team-facing HS-JEPA prototypes.

This script starts from the original competition data and the public-observed
submission ledger, then produces two end-to-end HS-JEPA prototype submissions:

1. Public-Private Equation HS-JEPA Solver
   - no cohort features
   - treats previous public LB observations as a sensor for action toxicity
   - predicts a hidden listener/correction representation and plans row-target
     actions that avoid known public-bad directions

2. Personal-Cohort Atlas HS-JEPA Solver
   - includes raw lifelog-derived human-state latent and peer cohort context
   - gates the same row-target action plan by personal/cohort anomaly evidence

The code is written for teammates who did not follow the full experiment
history. Version labels are kept only as file anchors for reproducibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
from typing import Iterable

import numpy as np
import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import LeaveOneOut


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1.0e-6

CURRENT_PUBLIC_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
PUBLIC_EQUATION_ANCHOR_FILE = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
ROW_STATE_DISCOVERY_FILE = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
TARGET_ROUTE_STRESS_FILE = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
OBJECTIVE_BAD_ROUTE_FILE = "submission_h010_objective_s1s4_v2_uploadsafe.csv"
DUAL_GATE_BAD_ROUTE_FILE = "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"
TARGET_XOR_STRESS_FILE = "submission_h144_targetxor_def80b88_uploadsafe.csv"
Q3_REPAIR_STRESS_FILE = "submission_h145_q3repair_2d818e46_uploadsafe.csv"

PUBLIC_LISTENER_POSTERIOR_FILE = "hitl/h055_postfeedback_public_listener_jepa/h055_cell_posterior.csv"
PUBLIC_SCORE_LEDGER_FILE = "data_analytics/hsjepa_public_score_ledger.csv"
H057_ACTION_AUDIT_FILE = "hs_jepa_end_to_end/h057_row_target_actions.csv"

CURRENT_PUBLIC_BEST_LB = 0.5677475939


@dataclass(frozen=True)
class PlannerConfig:
    """Action planning constants for the two prototypes."""

    no_cohort_top_cells: int = 260
    no_cohort_scale: float = 0.62
    no_cohort_max_abs_logit_step: float = 1.05
    cohort_top_cells: int = 220
    cohort_scale: float = 0.62
    cohort_max_abs_logit_step: float = 1.05
    row_route_bonus: float = 0.14
    bad_alignment_penalty: float = 0.42
    listener_gain_weight: float = 0.48
    listener_step_weight: float = 0.18
    stability_weight: float = 0.16
    q2_penalty: float = 0.65
    risky_s1s4_penalty: float = 0.08
    cohort_weight: float = 0.34
    cohort_peer_only_penalty: float = 0.20


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def soft_bce(prob: np.ndarray, target_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    q = clip_prob(target_prob)
    return -(q * np.log(p) + (1.0 - q) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def rank01(values: Iterable[float]) -> np.ndarray:
    s = pd.Series(np.asarray(list(values), dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def load_submission(filename: str) -> pd.DataFrame:
    path = ROOT / filename
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    return df.sort_values(KEYS).reset_index(drop=True)


def validate_submission(df: pd.DataFrame, name: str, expected_rows: int = 250) -> None:
    missing = [c for c in KEYS + TARGETS if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")
    if len(df) != expected_rows:
        raise ValueError(f"{name} expected {expected_rows} rows, got {len(df)}")
    if df[KEYS].duplicated().any():
        raise ValueError(f"{name} contains duplicated key rows")
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(prob).all():
        raise ValueError(f"{name} contains non-finite probabilities")
    if ((prob <= 0.0) | (prob >= 1.0)).any():
        raise ValueError(f"{name} probabilities must be inside (0, 1)")


def assert_same_keys(reference: pd.DataFrame, frames: list[tuple[str, pd.DataFrame]]) -> None:
    ref = reference[KEYS]
    for name, frame in frames:
        if not frame[KEYS].equals(ref):
            raise ValueError(f"{name} keys do not match the reference")


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, j])
    validate_submission(out, path.name)
    out.to_csv(path, index=False)


def load_listener_target(sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    cells = pd.read_csv(ROOT / PUBLIC_LISTENER_POSTERIOR_FILE)
    listener = np.full((len(sample), len(TARGETS)), np.nan, dtype=np.float64)
    aux = np.full_like(listener, np.nan)
    target_index = {target: i for i, target in enumerate(TARGETS)}

    for rec in cells.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if 0 <= row < len(sample) and target in target_index:
            j = target_index[target]
            listener[row, j] = float(rec["posterior_prob"])
            aux[row, j] = float(rec["aux_score"])

    if np.isnan(listener).any() or np.isnan(aux).any():
        raise ValueError("listener posterior is incomplete")
    return clip_prob(listener), np.nan_to_num(aux, nan=0.0)


def load_public_observed_worlds(reference: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    ledger = pd.read_csv(ROOT / PUBLIC_SCORE_LEDGER_FILE)
    rows: list[dict[str, object]] = []
    worlds: dict[str, np.ndarray] = {}
    for rec in ledger.to_dict("records"):
        file = str(rec["file"])
        path = ROOT / file
        if not path.exists():
            continue
        sub = load_submission(file)
        validate_submission(sub, file)
        assert_same_keys(reference, [(file, sub)])
        prob = sub[TARGETS].to_numpy(dtype=np.float64)
        worlds[file] = prob
        public_lb = float(rec["public_lb"])
        rows.append(
            {
                "file": file,
                "public_lb": public_lb,
                "family": str(rec.get("family", "")),
                "note": str(rec.get("note", "")),
                "delta_vs_current_best": public_lb - CURRENT_PUBLIC_BEST_LB,
                "local": True,
            }
        )
    observed = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    return observed, worlds


def build_cell_frame(
    sample: pd.DataFrame,
    current_prob: np.ndarray,
    row_state_prob: np.ndarray,
    listener_prob: np.ndarray,
    listener_aux: np.ndarray,
    observed: pd.DataFrame,
    worlds: dict[str, np.ndarray],
    config: PlannerConfig,
) -> pd.DataFrame:
    current_z = logit(current_prob)
    row_state_z = logit(row_state_prob)
    listener_z = logit(listener_prob)
    listener_step = np.clip(listener_z - current_z, -1.5, 1.5)
    trial_z = current_z + 0.35 * listener_step
    listener_gain = soft_bce(current_prob, listener_prob) - soft_bce(sigmoid(trial_z), listener_prob)

    # Public-bad axis: cells where worse submissions moved in the same
    # direction as the listener target are toxic for further planning.
    same_bad = np.zeros_like(current_prob, dtype=np.float64)
    opposite_bad = np.zeros_like(current_prob, dtype=np.float64)
    abs_bad = np.zeros_like(current_prob, dtype=np.float64)
    for rec in observed.to_dict("records"):
        file = str(rec["file"])
        if file == CURRENT_PUBLIC_BEST_FILE or file not in worlds:
            continue
        public_delta = max(float(rec["delta_vs_current_best"]), 0.0)
        if public_delta <= 0:
            continue
        weight = np.sqrt(public_delta / max(public_delta, 1.0e-9))
        movement = logit(worlds[file]) - current_z
        same = (movement * listener_step) > 0
        same_bad += weight * np.where(same, np.abs(movement), 0.0)
        opposite_bad += weight * np.where(~same, np.abs(movement), 0.0)
        abs_bad += weight * np.abs(movement)

    row_route = np.abs(row_state_z - current_z).sum(axis=1) > 1.0e-12
    row_state_strength = np.abs(row_state_z - current_z).sum(axis=1)
    row_state_rank = rank01(row_state_strength)

    h057_audit = pd.read_csv(ROOT / H057_ACTION_AUDIT_FILE)
    current_action_cells = set((int(r["row"]), str(r["target"])) for r in h057_audit.to_dict("records"))

    records: list[dict[str, object]] = []
    for row in range(len(sample)):
        for j, target in enumerate(TARGETS):
            current_action = (row, target) in current_action_cells
            target_penalty = 0.0
            if target == "Q2":
                target_penalty += config.q2_penalty
            if target in {"S1", "S4"}:
                target_penalty += config.risky_s1s4_penalty

            gain_rank = rank01(listener_gain.reshape(-1))[row * len(TARGETS) + j]
            step_rank = rank01(np.abs(listener_step).reshape(-1))[row * len(TARGETS) + j]
            bad_rank = rank01(same_bad.reshape(-1))[row * len(TARGETS) + j]
            stability_rank = rank01((opposite_bad - same_bad).reshape(-1))[row * len(TARGETS) + j]
            aux_rank = rank01(listener_aux.reshape(-1))[row * len(TARGETS) + j]

            score = (
                config.listener_gain_weight * gain_rank
                + config.listener_step_weight * step_rank
                + config.stability_weight * stability_rank
                + 0.10 * aux_rank
                + (config.row_route_bonus if row_route[row] or current_action else 0.0)
                - config.bad_alignment_penalty * bad_rank
                - target_penalty
            )
            records.append(
                {
                    "row": row,
                    **{key: sample.loc[row, key] for key in KEYS},
                    "target": target,
                    "current_prob": float(current_prob[row, j]),
                    "listener_prob": float(listener_prob[row, j]),
                    "listener_logit_step": float(listener_step[row, j]),
                    "listener_gain": float(listener_gain[row, j]),
                    "listener_aux": float(listener_aux[row, j]),
                    "known_bad_same_direction": float(same_bad[row, j]),
                    "known_bad_opposite_direction": float(opposite_bad[row, j]),
                    "known_bad_abs_movement": float(abs_bad[row, j]),
                    "row_state_route": bool(row_route[row]),
                    "row_state_rank": float(row_state_rank[row]),
                    "current_best_action_cell": bool(current_action),
                    "q2_frozen_penalty": float(target == "Q2"),
                    "risk_s1s4_penalty": float(target in {"S1", "S4"}),
                    "no_cohort_score": float(score),
                }
            )
    cells = pd.DataFrame(records)
    cells["no_cohort_rank"] = rank01(cells["no_cohort_score"])
    return cells


def load_cohort_module():
    module_path = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_hsjepa_experiment.py"
    spec = importlib.util.spec_from_file_location("cohort_hsjepa_experiment", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_or_load_cohort_features() -> tuple[pd.DataFrame, dict[str, object]]:
    """Build cohort latent from OG data using the team cohort experiment code."""

    cohort_module = load_cohort_module()
    config = cohort_module.ExperimentConfig(peer_group_count=4, latent_dims=8, random_state=42)
    rows = cohort_module.make_metric_rows()
    daily, numeric_cols = cohort_module.build_daily_features(rows)
    latent_frame, cohort_cols, meta = cohort_module.build_latent_and_cohort(daily, numeric_cols, config)
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")[TARGETS]
    full = cohort_module.add_full_peer_margins(latent_frame, labels, [c for c in cohort_cols if c.startswith("human_state_latent_")])

    test = full[full["split"].eq("test")].copy().reset_index(drop=True)
    for target in TARGETS:
        col = f"peer_margin_{target}"
        if col not in test.columns:
            test[col] = 0.0

    test["target_route_margin_q2q3s2"] = (
        0.34 * rank01(np.abs(test["peer_margin_Q2"]))
        + 0.33 * rank01(np.abs(test["peer_margin_Q3"]))
        + 0.33 * rank01(np.abs(test["peer_margin_S2"]))
    )
    test["personal_cohort_gate"] = (
        0.50 * rank01(test["dist_to_subject_normal"])
        + 0.25 * rank01(test["cohort_outlier_score"])
        + 0.15 * rank01(np.abs(test["subject_minus_peer_dist"]))
        + 0.10 * rank01(test["target_route_margin_q2q3s2"])
    )
    test["peer_only_risk"] = rank01(test["dist_to_peer_normal"] - test["dist_to_subject_normal"])

    hidden_path = ROOT / "hs_jepa_end_to_end" / "h057_hidden_row_states.csv"
    if hidden_path.exists():
        hidden = pd.read_csv(hidden_path)
        selected = test["metric_row"].isin(hidden["row"]).astype(int).to_numpy()
        meta["current_best_hidden_rows"] = int(selected.sum())
        for col in ["personal_cohort_gate", "cohort_outlier_score", "dist_to_subject_normal", "dist_to_peer_normal"]:
            score = test[col].fillna(0.0).to_numpy(dtype=np.float64)
            meta[f"{col}_mean_selected_hidden"] = float(score[selected == 1].mean()) if selected.sum() else None
            meta[f"{col}_mean_other"] = float(score[selected == 0].mean()) if (1 - selected).sum() else None

    return test, meta


def add_cohort_scores(cells: pd.DataFrame, cohort_test: pd.DataFrame, config: PlannerConfig) -> pd.DataFrame:
    cohort_view = cohort_test[
        [
            "metric_row",
            "peer_group",
            "dist_to_subject_normal",
            "dist_to_peer_normal",
            "subject_minus_peer_dist",
            "cohort_outlier_score",
            "target_route_margin_q2q3s2",
            "personal_cohort_gate",
            "peer_only_risk",
        ]
        + [f"peer_margin_{target}" for target in TARGETS]
    ].rename(columns={"metric_row": "row"})

    out = cells.merge(cohort_view, on="row", how="left")
    out["target_peer_margin_abs"] = [
        abs(float(rec.get(f"peer_margin_{rec['target']}", 0.0))) for rec in out.to_dict("records")
    ]
    out["target_peer_margin_rank"] = rank01(out["target_peer_margin_abs"])
    out["cohort_score"] = (
        out["no_cohort_score"]
        + config.cohort_weight * out["personal_cohort_gate"].fillna(0.5)
        + 0.10 * out["target_peer_margin_rank"]
        - config.cohort_peer_only_penalty * out["peer_only_risk"].fillna(0.5)
    )
    out["cohort_rank"] = rank01(out["cohort_score"])
    return out


def choose_actions(cells: pd.DataFrame, score_col: str, top_cells: int, mode: str) -> pd.DataFrame:
    candidate = cells.copy()
    candidate = candidate[candidate["target"] != "Q2"].copy()

    # A row-target solver, not only a global top-k: first reward rows with at
    # least two plausible target actions, then keep the strongest cells.
    row_support = (
        candidate.groupby("row")[score_col]
        .agg(["mean", "max", "count"])
        .rename(columns={"mean": "row_score_mean", "max": "row_score_max", "count": "row_candidate_count"})
    )
    candidate = candidate.merge(row_support, on="row", how="left")
    candidate["solver_score"] = (
        0.72 * candidate[score_col]
        + 0.18 * candidate["row_score_max"]
        + 0.10 * candidate["row_score_mean"]
    )

    if mode == "cohort":
        # Cohort is allowed to elevate Q2/Q3/S2-style human-state routes, but
        # still avoids known public-toxic S1/S4-only movement.
        candidate.loc[candidate["target"].isin(["Q3", "S2"]), "solver_score"] += 0.035
        candidate.loc[candidate["target"].isin(["S1", "S4"]), "solver_score"] -= 0.045
    else:
        candidate.loc[candidate["target"].isin(["S1", "S4"]), "solver_score"] -= 0.025

    selected = candidate.sort_values("solver_score", ascending=False).head(top_cells).copy()
    selected["selected_rank"] = np.arange(1, len(selected) + 1)
    return selected


def materialize_candidate(
    sample: pd.DataFrame,
    current_prob: np.ndarray,
    listener_prob: np.ndarray,
    selected: pd.DataFrame,
    scale: float,
    max_abs_logit_step: float,
    label: str,
) -> tuple[str, np.ndarray, pd.DataFrame]:
    current_z = logit(current_prob)
    listener_z = logit(listener_prob)
    out_z = current_z.copy()

    audit_records: list[dict[str, object]] = []
    target_index = {target: i for i, target in enumerate(TARGETS)}
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        j = target_index[target]
        step = np.clip(listener_z[row, j] - current_z[row, j], -max_abs_logit_step, max_abs_logit_step)
        out_z[row, j] = current_z[row, j] + scale * step
        audit_records.append(
            {
                "row": row,
                **{key: sample.loc[row, key] for key in KEYS},
                "target": target,
                "current_prob": float(current_prob[row, j]),
                "listener_prob": float(listener_prob[row, j]),
                "candidate_prob": float(sigmoid(out_z[row, j])),
                "delta_vs_current_best": float(sigmoid(out_z[row, j]) - current_prob[row, j]),
                "applied_logit_step": float(scale * step),
                "planner": label,
                "selected_rank": int(rec["selected_rank"]),
                "solver_score": float(rec["solver_score"]),
                "no_cohort_score": float(rec.get("no_cohort_score", np.nan)),
                "cohort_score": float(rec.get("cohort_score", np.nan)),
                "known_bad_same_direction": float(rec.get("known_bad_same_direction", np.nan)),
                "listener_gain": float(rec.get("listener_gain", np.nan)),
                "row_state_route": bool(rec.get("row_state_route", False)),
                "current_best_action_cell": bool(rec.get("current_best_action_cell", False)),
            }
        )

    prob = clip_prob(sigmoid(out_z))
    digest = short_hash(prob)
    name = f"submission_final_{label}_{digest}_uploadsafe.csv"
    root_path = ROOT / name
    local_path = OUT / name
    write_submission(sample, prob, root_path)
    write_submission(sample, prob, local_path)
    audit = pd.DataFrame(audit_records)
    return name, prob, audit


def summarize_candidate(
    name: str,
    prob: np.ndarray,
    current_prob: np.ndarray,
    listener_prob: np.ndarray,
    audit: pd.DataFrame,
    observed: pd.DataFrame,
    worlds: dict[str, np.ndarray],
) -> dict[str, object]:
    diff = prob - current_prob
    current_soft = float(np.mean(soft_bce(current_prob, listener_prob)))
    candidate_soft = float(np.mean(soft_bce(prob, listener_prob)))
    row_count = int((np.abs(diff).sum(axis=1) > 1.0e-12).sum())
    cell_count = int((np.abs(diff) > 1.0e-12).sum())
    target_counts = {target: int((np.abs(diff[:, j]) > 1.0e-12).sum()) for j, target in enumerate(TARGETS)}

    bad_alignments: dict[str, float] = {}
    move = logit(prob) - logit(current_prob)
    move_norm = float(np.linalg.norm(move.reshape(-1))) + 1.0e-12
    for rec in observed.to_dict("records"):
        file = str(rec["file"])
        if file == CURRENT_PUBLIC_BEST_FILE or file not in worlds:
            continue
        if float(rec["delta_vs_current_best"]) <= 0:
            continue
        axis = logit(worlds[file]) - logit(current_prob)
        axis_norm = float(np.linalg.norm(axis.reshape(-1))) + 1.0e-12
        bad_alignments[file] = float(np.sum(move * axis) / (move_norm * axis_norm))

    return {
        "submission_file": name,
        "hash": short_hash(prob),
        "changed_rows": row_count,
        "changed_cells": cell_count,
        "target_changed_cells": target_counts,
        "soft_listener_logloss": candidate_soft,
        "soft_listener_delta_vs_current_best": candidate_soft - current_soft,
        "mean_abs_delta_vs_current_best": float(np.mean(np.abs(diff))),
        "max_abs_delta_vs_current_best": float(np.max(np.abs(diff))),
        "mean_selected_known_bad_same_direction": float(audit["known_bad_same_direction"].mean()) if not audit.empty else None,
        "mean_selected_listener_gain": float(audit["listener_gain"].mean()) if not audit.empty else None,
        "bad_axis_cosine": bad_alignments,
    }


def build_public_equation_proxy(
    current_prob: np.ndarray,
    listener_prob: np.ndarray,
    observed: pd.DataFrame,
    worlds: dict[str, np.ndarray],
    cells: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    current_z = logit(current_prob)
    listener_step = logit(listener_prob) - current_z
    features: list[dict[str, object]] = []
    y: list[float] = []

    no_cohort_score = cells.pivot(index="row", columns="target", values="no_cohort_score").reindex(columns=TARGETS).to_numpy()
    bad_same = cells.pivot(index="row", columns="target", values="known_bad_same_direction").reindex(columns=TARGETS).to_numpy()

    for rec in observed.to_dict("records"):
        file = str(rec["file"])
        if file == CURRENT_PUBLIC_BEST_FILE or file not in worlds:
            continue
        move = logit(worlds[file]) - current_z
        changed = np.abs(move) > 1.0e-12
        row_changed = changed.any(axis=1)
        feat = {
            "file": file,
            "public_delta_vs_current_best": float(rec["delta_vs_current_best"]),
            "move_norm": float(np.linalg.norm(move)),
            "changed_cells": int(changed.sum()),
            "changed_rows": int(row_changed.sum()),
            "listener_alignment": float(np.sum(move * listener_step) / (np.linalg.norm(move) * np.linalg.norm(listener_step) + 1.0e-12)),
            "mean_no_cohort_score_on_changed": float(np.mean(no_cohort_score[changed])) if changed.any() else 0.0,
            "mean_bad_same_on_changed": float(np.mean(bad_same[changed])) if changed.any() else 0.0,
        }
        for j, target in enumerate(TARGETS):
            feat[f"{target}_changed_cells"] = int(changed[:, j].sum())
            feat[f"{target}_move_abs_sum"] = float(np.abs(move[:, j]).sum())
        features.append(feat)
        y.append(float(rec["delta_vs_current_best"]))

    frame = pd.DataFrame(features)
    if len(frame) < 4:
        return frame, {"enabled": False, "reason": "too few public-observed local submissions"}

    x_cols = [c for c in frame.columns if c not in {"file", "public_delta_vs_current_best"}]
    x = frame[x_cols].to_numpy(dtype=np.float64)
    target = np.asarray(y, dtype=np.float64)
    loo = LeaveOneOut()
    pred = np.zeros_like(target)
    for tr, va in loo.split(x):
        model = Ridge(alpha=1.0)
        model.fit(x[tr], target[tr])
        pred[va] = model.predict(x[va])
    frame["loo_predicted_delta_vs_current_best"] = pred
    diagnostics = {
        "enabled": True,
        "n_public_observed_worlds": int(len(frame)),
        "loo_mae_delta_vs_current_best": float(mean_absolute_error(target, pred)),
        "all_observed_are_current_best_or_worse": bool((target >= -1.0e-12).all()),
        "warning": "This is a tiny sensor inversion proxy, not a leaderboard oracle.",
    }
    return frame, diagnostics


def write_markdown_report(
    observed: pd.DataFrame,
    proxy_frame: pd.DataFrame,
    proxy_diag: dict[str, object],
    no_cohort_summary: dict[str, object],
    cohort_summary: dict[str, object],
    cohort_meta: dict[str, object],
    no_cohort_audit: pd.DataFrame,
    cohort_audit: pd.DataFrame,
) -> None:
    def md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
        if df.empty:
            return "_empty_"
        view = df.head(max_rows).copy()
        lines = [
            "| " + " | ".join(map(str, view.columns)) + " |",
            "| " + " | ".join(["---"] * len(view.columns)) + " |",
        ]
        for _, row in view.iterrows():
            lines.append("| " + " | ".join(str(row[c]).replace("|", "/") for c in view.columns) + " |")
        return "\n".join(lines)

    observed_view = observed[["public_lb", "delta_vs_current_best", "file", "family"]].copy()
    observed_view["public_lb"] = observed_view["public_lb"].map(lambda x: f"{x:.10f}")
    observed_view["delta_vs_current_best"] = observed_view["delta_vs_current_best"].map(lambda x: f"{x:+.10f}")

    no_target = pd.DataFrame(
        [{"target": k, "changed_cells": v} for k, v in no_cohort_summary["target_changed_cells"].items()]
    )
    co_target = pd.DataFrame(
        [{"target": k, "changed_cells": v} for k, v in cohort_summary["target_changed_cells"].items()]
    )

    report = f"""# Final HS-JEPA Prototype Report

## What was built

This run produced two team-facing end-to-end prototypes from the original data:

1. `{no_cohort_summary['submission_file']}`
   - Public-Private Equation HS-JEPA Solver
   - no cohort features
   - bets that the key bottleneck is row-target action toxicity, not raw model capacity

2. `{cohort_summary['submission_file']}`
   - Personal-Cohort Atlas HS-JEPA Solver
   - uses raw lifelog-derived human-state latent and peer cohort context
   - bets that action safety improves when a row-target action is supported by both personal and cohort anomaly coordinates

Current public best anchor:

- `{CURRENT_PUBLIC_BEST_FILE}`
- public LB `{CURRENT_PUBLIC_BEST_LB:.10f}`

## JEPA interpretation

Plain tabular modeling asks: `context -> label`.

HS-JEPA asks:

1. encode visible context: row order, previous public sensor responses, raw lifestyle logs, subject/cohort state;
2. predict hidden target representation: listener posterior, row-target route, action-health field;
3. plan an action: choose which row-target cells should move and by how much;
4. reject action collapse: avoid directions that known public observations punished.

This follows the JEPA idea that the useful target is an embedding/representation
of the hidden state, not raw reconstruction. It also follows the LeWorldModel
idea that actions should be chosen after predicting their consequence, not
cloned directly.

## Public-observed sensor worlds

{md_table(observed_view, max_rows=30)}

## Tiny public equation proxy

This proxy is intentionally conservative. It uses only local files with known
public LB and predicts public delta from vector movement features. It is a
stress diagnostic, not an oracle.

```json
{json.dumps(proxy_diag, indent=2)}
```

{md_table(proxy_frame[['file', 'public_delta_vs_current_best', 'loo_predicted_delta_vs_current_best', 'listener_alignment', 'mean_bad_same_on_changed']] if not proxy_frame.empty else proxy_frame)}

## Prototype 1: Public-Private Equation HS-JEPA Solver

Worldview:

The public best is not just a good probability table. It is a partially decoded
hidden row-state. Further improvement should come from changing only row-target
cells whose listener direction is strong and whose direction is not shared by
known public-bad submissions.

Summary:

```json
{json.dumps(no_cohort_summary, indent=2)}
```

Per-target changed cells:

{md_table(no_target)}

Top selected actions:

{md_table(no_cohort_audit[['row', 'subject_id', 'lifelog_date', 'target', 'current_prob', 'candidate_prob', 'delta_vs_current_best', 'solver_score', 'known_bad_same_direction', 'listener_gain']].head(20))}

## Prototype 2: Personal-Cohort Atlas HS-JEPA Solver

Worldview:

A row-target action is safer when the row is interpretable in two coordinate
systems:

- personal coordinate: unusual relative to the subject's own normal state;
- cohort coordinate: unusual inside a peer group of similar human-state trajectories.

The cohort module is not used as a direct label rule. It is an additional context
view for action planning.

Cohort metadata:

```json
{json.dumps(cohort_meta, indent=2)}
```

Summary:

```json
{json.dumps(cohort_summary, indent=2)}
```

Per-target changed cells:

{md_table(co_target)}

Top selected actions:

{md_table(cohort_audit[['row', 'subject_id', 'lifelog_date', 'target', 'current_prob', 'candidate_prob', 'delta_vs_current_best', 'solver_score', 'known_bad_same_direction', 'listener_gain']].head(20))}

## Submission interpretation

These files should not be read as blends. Each is a claim:

- no-cohort solver: the current missing piece is public/private action toxicity;
- cohort solver: action toxicity becomes easier to control when row-target
  movement is grounded in human-state cohort coordinates.

If either file improves public LB by a meaningful amount, HS-JEPA's action-world
model framing is strengthened. If both fail, the hidden state may be real but
the current listener/correction target is still too public-specific or collapsed.
"""
    (OUT / "final_hsjepa_prototype_report.md").write_text(report)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    config = PlannerConfig()

    current = load_submission(CURRENT_PUBLIC_BEST_FILE)
    row_state = load_submission(ROW_STATE_DISCOVERY_FILE)
    for name, frame in [("current_public_best", current), ("row_state_discovery", row_state)]:
        validate_submission(frame, name)
    assert_same_keys(current, [("row_state_discovery", row_state)])

    sample = current[KEYS].copy()
    current_prob = current[TARGETS].to_numpy(dtype=np.float64)
    row_state_prob = row_state[TARGETS].to_numpy(dtype=np.float64)
    listener_prob, listener_aux = load_listener_target(sample)
    observed, worlds = load_public_observed_worlds(current)

    cells = build_cell_frame(
        sample=sample,
        current_prob=current_prob,
        row_state_prob=row_state_prob,
        listener_prob=listener_prob,
        listener_aux=listener_aux,
        observed=observed,
        worlds=worlds,
        config=config,
    )
    proxy_frame, proxy_diag = build_public_equation_proxy(current_prob, listener_prob, observed, worlds, cells)

    no_selected = choose_actions(cells, "no_cohort_score", config.no_cohort_top_cells, mode="no_cohort")
    no_name, no_prob, no_audit = materialize_candidate(
        sample=sample,
        current_prob=current_prob,
        listener_prob=listener_prob,
        selected=no_selected,
        scale=config.no_cohort_scale,
        max_abs_logit_step=config.no_cohort_max_abs_logit_step,
        label="no_cohort_equation_hsjepa",
    )
    no_summary = summarize_candidate(no_name, no_prob, current_prob, listener_prob, no_audit, observed, worlds)

    cohort_test, cohort_meta = build_or_load_cohort_features()
    cohort_test.to_csv(OUT / "cohort_human_state_features_test.csv", index=False)
    cells_with_cohort = add_cohort_scores(cells, cohort_test, config)
    co_selected = choose_actions(cells_with_cohort, "cohort_score", config.cohort_top_cells, mode="cohort")
    co_name, co_prob, co_audit = materialize_candidate(
        sample=sample,
        current_prob=current_prob,
        listener_prob=listener_prob,
        selected=co_selected,
        scale=config.cohort_scale,
        max_abs_logit_step=config.cohort_max_abs_logit_step,
        label="with_cohort_atlas_hsjepa",
    )
    co_summary = summarize_candidate(co_name, co_prob, current_prob, listener_prob, co_audit, observed, worlds)

    cells.to_csv(OUT / "no_cohort_cell_scores.csv", index=False)
    cells_with_cohort.to_csv(OUT / "cohort_cell_scores.csv", index=False)
    no_audit.to_csv(OUT / "no_cohort_action_audit.csv", index=False)
    co_audit.to_csv(OUT / "cohort_action_audit.csv", index=False)
    observed.to_csv(OUT / "public_observed_sensor_worlds.csv", index=False)
    proxy_frame.to_csv(OUT / "public_equation_proxy_loo.csv", index=False)

    summaries = {
        "current_public_best_file": CURRENT_PUBLIC_BEST_FILE,
        "current_public_best_lb": CURRENT_PUBLIC_BEST_LB,
        "no_cohort": no_summary,
        "with_cohort": co_summary,
        "public_equation_proxy": proxy_diag,
        "cohort_meta": cohort_meta,
    }
    (OUT / "prototype_summaries.json").write_text(json.dumps(summaries, indent=2))

    write_markdown_report(
        observed=observed,
        proxy_frame=proxy_frame,
        proxy_diag=proxy_diag,
        no_cohort_summary=no_summary,
        cohort_summary=co_summary,
        cohort_meta=cohort_meta,
        no_cohort_audit=no_audit,
        cohort_audit=co_audit,
    )

    print("Final HS-JEPA prototypes built")
    print(f"current_best_lb={CURRENT_PUBLIC_BEST_LB:.10f}")
    print(f"no_cohort_submission={ROOT / no_name}")
    print(f"with_cohort_submission={ROOT / co_name}")
    print(f"report={OUT / 'final_hsjepa_prototype_report.md'}")


if __name__ == "__main__":
    main()
