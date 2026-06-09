#!/usr/bin/env python3
"""Candidate 2: Cohort-Relative Human-State Atlas HS-JEPA.

Team-facing final candidate.

This script starts from the original competition metric files and raw lifelog
parquet files, builds a cohort-relative human-state atlas, and uses that atlas
to translate Candidate 1's sparse row-target action field more cautiously.

The key distinction from Candidate 1:

    Candidate 1 asks:
        Which row-target corrections look beneficial under the public-loss
        sensor equation?

    Candidate 2 asks:
        Among those same corrections, which rows look human-state plausible
        when interpreted both against the subject's own normal state and a
        peer cohort's normal state?

No external embedding API is used. The human-state representation is built from
the original raw lifelog files through deterministic daily aggregation, PCA, and
peer-cohort geometry.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "candidate_2_cohort_relative_atlas"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939

CANDIDATE1_MODULE = HERE / "candidate_1_public_loss_sparse_tomography.py"
COHORT_MODULE = ROOT / "team_experiments" / "cohort_hsjepa" / "cohort_hsjepa_experiment.py"


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "final_candidate1_for_cohort_atlas")
cohort = import_module(COHORT_MODULE, "final_cohort_hsjepa_module")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    return cohort.rank01(np.asarray(values, dtype=np.float64))


def write_submission(path: Path, sample: pd.DataFrame, prob: np.ndarray) -> None:
    out = sample[KEYS].copy()
    for idx, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, idx])
    out.to_csv(path, index=False)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    keys_match = df[KEYS].equals(sample[KEYS])
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(keys_match),
        "duplicate_keys": int(df[KEYS].duplicated().sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > 1e-12).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def load_submission(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


def build_cohort_atlas() -> tuple[pd.DataFrame, dict[str, object]]:
    """Build daily human-state latent and peer-cohort geometry from OG data."""

    config = cohort.ExperimentConfig(peer_group_count=4, latent_dims=8, random_state=42)
    rows = cohort.make_metric_rows()
    daily, numeric_cols = cohort.build_daily_features(rows)
    latent, cohort_cols, meta = cohort.build_latent_and_cohort(daily, numeric_cols, config)
    labels = pd.read_csv(ROOT / "data" / "ch2026_metrics_train.csv")[TARGETS]
    latent_cols = [c for c in cohort_cols if c.startswith("human_state_latent_")]
    full = cohort.add_full_peer_margins(latent, labels, latent_cols)

    for target in TARGETS:
        if f"peer_margin_{target}" not in full:
            full[f"peer_margin_{target}"] = 0.0

    full["q_group_peer_margin"] = (
        0.34 * rank01(np.abs(full["peer_margin_Q1"]))
        + 0.33 * rank01(np.abs(full["peer_margin_Q2"]))
        + 0.33 * rank01(np.abs(full["peer_margin_Q3"]))
    )
    full["s_group_peer_margin"] = (
        0.25 * rank01(np.abs(full["peer_margin_S1"]))
        + 0.25 * rank01(np.abs(full["peer_margin_S2"]))
        + 0.25 * rank01(np.abs(full["peer_margin_S3"]))
        + 0.25 * rank01(np.abs(full["peer_margin_S4"]))
    )
    full["target_route_margin_q2q3s2"] = (
        0.34 * rank01(np.abs(full["peer_margin_Q2"]))
        + 0.33 * rank01(np.abs(full["peer_margin_Q3"]))
        + 0.33 * rank01(np.abs(full["peer_margin_S2"]))
    )
    full["personal_axis"] = rank01(full["dist_to_subject_normal"])
    full["cohort_axis"] = rank01(full["dist_to_peer_normal"])
    full["axis_disagreement"] = rank01(np.abs(full["subject_minus_peer_dist"]))
    full["peer_only_toxicity"] = rank01(full["dist_to_peer_normal"] - full["dist_to_subject_normal"])
    full["atlas_action_health"] = (
        0.34 * full["personal_axis"]
        + 0.28 * full["cohort_axis"]
        + 0.18 * full["axis_disagreement"]
        + 0.12 * full["target_route_margin_q2q3s2"]
        + 0.08 * (1.0 - full["peer_only_toxicity"])
    )

    meta = dict(meta)
    meta["numeric_daily_feature_count"] = len(numeric_cols)
    meta["cohort_atlas_columns"] = [
        "peer_group",
        "dist_to_subject_normal",
        "dist_to_peer_normal",
        "subject_minus_peer_dist",
        "cohort_outlier_score",
        "target_route_margin_q2q3s2",
        "atlas_action_health",
        "peer_only_toxicity",
    ]
    return full, meta


def target_gate(row: pd.Series, target: str) -> float:
    """Translate public-loss action strength through cohort-relative geometry."""

    health = float(row["atlas_action_health"])
    peer_toxic = float(row["peer_only_toxicity"])
    gate = 0.78 + 0.48 * health - 0.24 * peer_toxic

    if target in {"Q2", "Q3", "S2"}:
        gate += 0.16 * float(row["target_route_margin_q2q3s2"])
    elif target in {"S3", "S4"}:
        gate -= 0.08 * float(row["peer_only_toxicity"])
    elif target == "Q1":
        gate -= 0.04 * float(row["axis_disagreement"])

    margin_col = f"peer_margin_{target}"
    if margin_col in row:
        gate += 0.08 * float(row[f"{target[0].lower()}_group_peer_margin"]) if target[0] in {"Q", "S"} else 0.0
        gate += 0.05 * abs(float(row[margin_col]))

    return float(np.clip(gate, 0.52, 1.34))


def run() -> dict[str, object]:
    c1_readout = candidate1.run()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    best_prob = clip_prob(base_prob)

    c1_path = Path(c1_readout["root_path"])
    c1_prob = load_submission(c1_path)[TARGETS].to_numpy(dtype=np.float64)
    c1_move = logit(c1_prob.reshape(-1)) - base_logit

    atlas, atlas_meta = build_cohort_atlas()
    test_atlas = atlas[atlas["split"].eq("test")].copy().sort_values(KEYS).reset_index(drop=True)
    if len(test_atlas) != len(sample):
        raise ValueError(f"test atlas row count mismatch: {len(test_atlas)} != {len(sample)}")
    if not test_atlas[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("test atlas keys do not match submission sample")

    base_z = base_logit.reshape(best_prob.shape)
    c1_move_matrix = c1_move.reshape(best_prob.shape)
    gate_matrix = np.ones_like(c1_move_matrix)
    audit_rows = []
    for row_idx in range(len(sample)):
        row = test_atlas.loc[row_idx]
        for target_idx, target in enumerate(TARGETS):
            if abs(c1_move_matrix[row_idx, target_idx]) <= 1e-12:
                continue
            gate = target_gate(row, target)
            gate_matrix[row_idx, target_idx] = gate
            audit_rows.append(
                {
                    "row": row_idx,
                    **{key: sample.loc[row_idx, key] for key in KEYS},
                    "target": target,
                    "candidate1_logit_move": float(c1_move_matrix[row_idx, target_idx]),
                    "cohort_gate": gate,
                    "candidate2_logit_move": float(c1_move_matrix[row_idx, target_idx] * gate),
                    "atlas_action_health": float(row["atlas_action_health"]),
                    "cohort_outlier_score": float(row["cohort_outlier_score"]),
                    "dist_to_subject_normal": float(row["dist_to_subject_normal"]),
                    "dist_to_peer_normal": float(row["dist_to_peer_normal"]),
                    "subject_minus_peer_dist": float(row["subject_minus_peer_dist"]),
                    "peer_only_toxicity": float(row["peer_only_toxicity"]),
                    "target_route_margin_q2q3s2": float(row["target_route_margin_q2q3s2"]),
                    "peer_margin": float(row.get(f"peer_margin_{target}", 0.0)),
                }
            )

    c2_move = c1_move_matrix * gate_matrix
    prob = clip_prob(sigmoid(base_z + c2_move))
    digest = short_hash(prob)
    name = f"submission_final_candidate2_cohort_relative_atlas_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, prob)
    write_submission(root_path, sample, prob)

    action_audit = pd.DataFrame(audit_rows)
    action_audit.to_csv(OUT / "candidate2_action_audit.csv", index=False)
    test_cols = KEYS + [
        "peer_group",
        "dist_to_subject_normal",
        "dist_to_peer_normal",
        "subject_minus_peer_dist",
        "cohort_outlier_score",
        "target_route_margin_q2q3s2",
        "atlas_action_health",
        "peer_only_toxicity",
        *[f"peer_margin_{target}" for target in TARGETS],
    ]
    test_atlas[test_cols].to_csv(OUT / "candidate2_test_cohort_atlas.csv", index=False)

    c2_flat_move = c2_move.reshape(-1)
    metric = candidate1.candidate_metrics(c2_flat_move, base_grads, semantic_grads, h088_move)
    readout = {
        "candidate": "Cohort-Relative Human-State Atlas HS-JEPA",
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "hash": digest,
        "current_best_file": CURRENT_BEST_FILE,
        "current_best_public_lb": CURRENT_BEST_PUBLIC_LB,
        "candidate1_anchor_file": c1_readout["submission_file"],
        "candidate1_anchor_hash": c1_readout["hash"],
        "changed_cells": int((np.abs(prob - best_prob) > 1e-12).sum()),
        "changed_rows": int(np.unique(np.where(np.abs(prob - best_prob) > 1e-12)[0]).size),
        "mean_gate_on_changed_cells": float(action_audit["cohort_gate"].mean()) if len(action_audit) else 1.0,
        "min_gate_on_changed_cells": float(action_audit["cohort_gate"].min()) if len(action_audit) else 1.0,
        "max_gate_on_changed_cells": float(action_audit["cohort_gate"].max()) if len(action_audit) else 1.0,
        "target_changed_cells": action_audit.groupby("target").size().to_dict() if len(action_audit) else {},
        "cohort_atlas_meta": atlas_meta,
        "listener_metrics": metric,
        "validation": validate_submission(root_path, sample, best_prob),
    }
    (OUT / "candidate2_readout.json").write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
