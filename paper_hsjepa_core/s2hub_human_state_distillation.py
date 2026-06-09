#!/usr/bin/env python3
"""OG human-state distillation of the S2-hub HS-JEPA decoder.

The current strongest competition-side decoder is objective-stage bridge logic:

    S-stage factor encoder -> S2 listener/hub -> row-local driver/bridge action

This script tests whether that decoder is only a public-loss artifact, or
whether its selected rows/cells are visible from OG raw-lifelog human-state
context.  It treats S2-hub bridge actions as a teacher and trains subject-held
out students from the cohort-relative human-state atlas.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "s2hub_human_state_distillation"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
TOL = 1e-12

HUMAN_DISTILL_MODULE = HERE / "human_state_action_distillation.py"
S2HUB_TEACHER_FILE = "submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv"
STAGEBRIDGE_TEACHER_FILE = "submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv"


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


human_distill = import_module(HUMAN_DISTILL_MODULE, "s2hub_human_distill_core")
candidate1 = human_distill.candidate1


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def load_submission(path_or_name: str | Path) -> pd.DataFrame:
    path = Path(path_or_name)
    if not path.is_absolute():
        path = ROOT / path
    return pd.read_csv(path, parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)


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
        "changed_cells_vs_current_best": int((np.abs(prob - base_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and keys_match
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def metric_safe(y: np.ndarray, pred: np.ndarray) -> dict[str, float | None]:
    if len(np.unique(y)) < 2:
        return {"auc": None, "ap": float(y.mean())}
    return {
        "auc": float(roc_auc_score(y, pred)),
        "ap": float(average_precision_score(y, pred)),
    }


def classifier(seed: int):
    if seed % 2 == 0:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=5000, C=0.45, class_weight="balanced")),
            ]
        )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "clf",
                ExtraTreesClassifier(
                    n_estimators=520,
                    min_samples_leaf=4,
                    max_features=0.70,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def regressor(seed: int):
    if seed % 2 == 0:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("reg", Ridge(alpha=18.0)),
            ]
        )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "reg",
                ExtraTreesRegressor(
                    n_estimators=520,
                    min_samples_leaf=4,
                    max_features=0.70,
                    random_state=seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def feature_sets(feature_cols: list[str]) -> dict[str, list[str]]:
    forbidden_order = {"row", "row_frac", "subject_code"}
    no_order = [c for c in feature_cols if c not in forbidden_order]
    human_cols = [
        c
        for c in no_order
        if (
            c.startswith("human_state_latent_")
            or c
            in {
                "dayofweek",
                "is_weekend",
                "dayofmonth",
                "month_start_proximity",
                "month_end",
                "peer_group",
                "dist_to_subject_normal",
                "dist_to_peer_normal",
                "subject_minus_peer_dist",
                "subject_outlier_rank",
                "peer_outlier_rank",
                "cohort_outlier_score",
                "q_group_peer_margin",
                "s_group_peer_margin",
                "target_route_margin_q2q3s2",
                "personal_axis",
                "cohort_axis",
                "axis_disagreement",
                "peer_only_toxicity",
                "atlas_action_health",
                "target_peer_margin",
                "target_peer_margin_abs",
                "target_peer_margin_sign",
            }
            or c.startswith("peer_margin_")
            or c.startswith("target_onehot_")
            or c
            in {
                "target_idx",
                "is_q_target",
                "is_s_target",
                "is_q2_q3_s2",
                "is_objective_tail",
                "target_prior_rank",
            }
        )
    ]
    human_no_target = [
        c
        for c in human_cols
        if not (
            c.startswith("target_onehot_")
            or c
            in {
                "target_idx",
                "is_q_target",
                "is_s_target",
                "is_q2_q3_s2",
                "is_objective_tail",
                "target_prior_rank",
                "target_peer_margin",
                "target_peer_margin_abs",
                "target_peer_margin_sign",
            }
        )
    ]
    return {
        "all_no_order": no_order,
        "human_target_context": human_cols,
        "human_row_context_only": human_no_target,
    }


def subject_groups(frame: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    row_to_subject = sample["subject_id"].astype(str).to_dict()
    return frame["row"].astype(int).map(row_to_subject).to_numpy()


def oof_cell_student(frame: pd.DataFrame, cols: list[str], sample: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    x = frame[cols]
    y = frame["teacher_has_action"].to_numpy(dtype=int)
    y_move = frame["teacher_logit_move"].to_numpy(dtype=np.float64)
    groups = subject_groups(frame, sample)
    splits = list(GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(x, y, groups=groups))
    pred = np.zeros(len(frame), dtype=np.float64)
    move_pred = np.zeros(len(frame), dtype=np.float64)
    for fold, (tr, val) in enumerate(splits):
        preds = []
        moves = []
        for seed in [1200 + fold, 2200 + fold]:
            clf = classifier(seed)
            clf.fit(x.iloc[tr], y[tr])
            preds.append(clf.predict_proba(x.iloc[val])[:, 1])
            reg = regressor(seed)
            reg.fit(x.iloc[tr], y_move[tr])
            moves.append(reg.predict(x.iloc[val]))
        pred[val] = np.mean(preds, axis=0)
        move_pred[val] = np.mean(moves, axis=0)
    signed = np.abs(y_move) > TOL
    m = metric_safe(y, pred)
    diagnostics = {
        "feature_count": int(len(cols)),
        "cells": int(len(frame)),
        "positive_cells": int(y.sum()),
        "positive_rate": float(y.mean()),
        "subject_group_oof_auc": m["auc"],
        "subject_group_oof_ap": m["ap"],
        "move_rmse_all": float(np.sqrt(mean_squared_error(y_move, move_pred))),
        "move_rmse_action_cells": float(np.sqrt(mean_squared_error(y_move[signed], move_pred[signed]))) if signed.any() else None,
    }
    return pred, move_pred, diagnostics


def full_cell_student(frame: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x = frame[cols]
    y = frame["teacher_has_action"].to_numpy(dtype=int)
    y_move = frame["teacher_logit_move"].to_numpy(dtype=np.float64)
    preds = []
    moves = []
    for seed in [3101, 3102, 3103, 3104]:
        clf = classifier(seed)
        clf.fit(x, y)
        preds.append(clf.predict_proba(x)[:, 1])
        reg = regressor(seed)
        reg.fit(x, y_move)
        moves.append(reg.predict(x))
    return np.mean(preds, axis=0), np.mean(moves, axis=0)


def row_feature_columns(cell_feature_cols: list[str]) -> list[str]:
    remove_prefix = ("target_onehot_", "peer_margin_")
    remove_names = {
        "row",
        "row_frac",
        "subject_code",
        "target_idx",
        "is_q_target",
        "is_s_target",
        "is_q2_q3_s2",
        "is_objective_tail",
        "target_prior_rank",
        "base_prob",
        "base_logit",
        "base_uncertainty",
        "target_peer_margin",
        "target_peer_margin_abs",
        "target_peer_margin_sign",
    }
    cols = [
        c
        for c in cell_feature_cols
        if c not in remove_names and not any(c.startswith(prefix) for prefix in remove_prefix)
    ]
    return cols


def oof_row_student(frame: pd.DataFrame, row_cols: list[str], sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    row_frame = frame.sort_values(["row", "target_idx_int"]).groupby("row", as_index=False).first()
    row_frame["teacher_row_has_action"] = (
        frame.groupby("row")["teacher_has_action"].max().reindex(row_frame["row"]).to_numpy(dtype=float)
    )
    x = row_frame[row_cols]
    y = row_frame["teacher_row_has_action"].to_numpy(dtype=int)
    groups = sample.loc[row_frame["row"].astype(int), "subject_id"].astype(str).to_numpy()
    splits = list(GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(x, y, groups=groups))
    pred = np.zeros(len(row_frame), dtype=np.float64)
    for fold, (tr, val) in enumerate(splits):
        fold_preds = []
        for seed in [4100 + fold, 5100 + fold]:
            clf = classifier(seed)
            clf.fit(x.iloc[tr], y[tr])
            fold_preds.append(clf.predict_proba(x.iloc[val])[:, 1])
        pred[val] = np.mean(fold_preds, axis=0)
    row_frame["student_oof_row_prob"] = pred
    m = metric_safe(y, pred)
    diagnostics = {
        "feature_count": int(len(row_cols)),
        "rows": int(len(row_frame)),
        "positive_rows": int(y.sum()),
        "positive_rate": float(y.mean()),
        "subject_group_oof_auc": m["auc"],
        "subject_group_oof_ap": m["ap"],
    }
    return row_frame, diagnostics


def add_teacher(frame: pd.DataFrame, sample: pd.DataFrame, base_prob: np.ndarray, teacher_file: str) -> tuple[pd.DataFrame, np.ndarray]:
    teacher_prob = load_submission(teacher_file)[TARGETS].to_numpy(dtype=np.float64)
    if teacher_prob.shape != base_prob.shape:
        raise ValueError(teacher_file)
    base_z = logit(base_prob)
    teacher_move = logit(teacher_prob) - base_z
    out = frame.copy()
    moves = []
    has = []
    signs = []
    for rec in out[["row", "target_idx_int"]].to_dict("records"):
        move = float(teacher_move[int(rec["row"]), int(rec["target_idx_int"])])
        moves.append(move)
        has.append(float(abs(move) > TOL))
        signs.append(float(np.sign(move)))
    out["teacher_logit_move"] = moves
    out["teacher_has_action"] = has
    out["teacher_action_sign"] = signs
    return out, teacher_prob


def decode_og_gated_candidate(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    teacher_prob: np.ndarray,
    full_prob: np.ndarray,
    full_move: np.ndarray,
    teacher_name: str,
) -> tuple[np.ndarray, pd.DataFrame]:
    base_z = logit(base_prob).reshape(-1)
    teacher_move = logit(teacher_prob).reshape(-1) - base_z
    out_move = np.zeros_like(teacher_move)
    frame = frame.copy()
    frame["flat_idx"] = frame["row"].astype(int) * len(TARGETS) + frame["target_idx_int"].astype(int)
    frame["student_full_action_prob"] = full_prob
    frame["student_full_move"] = full_move
    teacher_mask = np.abs(teacher_move[frame["flat_idx"].to_numpy(dtype=int)]) > TOL
    teacher_rows = frame[teacher_mask].copy()
    if len(teacher_rows) == 0:
        return base_prob.copy(), teacher_rows
    support = teacher_rows["student_full_action_prob"].to_numpy(dtype=np.float64)
    lo = float(np.quantile(support, 0.15))
    hi = float(np.quantile(support, 0.90))
    denom = max(hi - lo, 1e-9)
    gate = np.clip((support - lo) / denom, 0.0, 1.0)
    # Keep every teacher cell, but let OG human-state support decide amplitude.
    amp = 0.52 + 0.66 * gate
    # If the regressor agrees in sign, allow a small extra boost.
    pred_move = teacher_rows["student_full_move"].to_numpy(dtype=np.float64)
    teacher_local_move = teacher_move[teacher_rows["flat_idx"].to_numpy(dtype=int)]
    sign_agree = np.sign(pred_move) == np.sign(teacher_local_move)
    amp += 0.10 * sign_agree.astype(float)
    amp = np.clip(amp, 0.45, 1.28)
    out_move[teacher_rows["flat_idx"].to_numpy(dtype=int)] = teacher_local_move * amp
    decoded = clip_prob(sigmoid(base_z + out_move).reshape(base_prob.shape))
    audit = teacher_rows.copy()
    audit["teacher_name"] = teacher_name
    audit["teacher_logit_move"] = teacher_local_move
    audit["og_student_amp"] = amp
    audit["decoded_logit_move"] = teacher_local_move * amp
    audit["student_teacher_sign_agree"] = sign_agree.astype(float)
    return decoded, audit


def evaluate_teacher(
    teacher_name: str,
    teacher_file: str,
    base_frame: pd.DataFrame,
    feature_cols: list[str],
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    base_grads: np.ndarray,
    semantic_grads: np.ndarray,
    h088_move: np.ndarray,
) -> dict[str, object]:
    frame, teacher_prob = add_teacher(base_frame, sample, base_prob, teacher_file)
    sets = feature_sets(feature_cols)
    cell_outputs = {}
    best_set = "human_target_context"
    for set_name, cols in sets.items():
        pred, move_pred, diag = oof_cell_student(frame, cols, sample)
        cell_outputs[set_name] = diag
        frame[f"oof_prob_{set_name}"] = pred
        frame[f"oof_move_{set_name}"] = move_pred
    full_prob, full_move = full_cell_student(frame, sets[best_set])
    row_cols = [c for c in row_feature_columns(feature_cols) if c in frame.columns]
    row_frame, row_diag = oof_row_student(frame, row_cols, sample)
    decoded_prob, audit = decode_og_gated_candidate(
        frame, sample, base_prob, teacher_prob, full_prob, full_move, teacher_name
    )
    digest = short_hash(decoded_prob)
    out_name = f"submission_hsjepa_ogdistilled_{teacher_name}_{digest}_uploadsafe.csv"
    local_path = OUT / out_name
    root_path = ROOT / out_name
    write_submission(local_path, sample, decoded_prob)
    write_submission(root_path, sample, decoded_prob)
    move = logit(decoded_prob).reshape(-1) - base_logit
    audit.to_csv(OUT / f"{teacher_name}_og_gated_action_audit.csv", index=False)
    frame.to_csv(OUT / f"{teacher_name}_cell_student_frame.csv", index=False)
    row_frame.to_csv(OUT / f"{teacher_name}_row_student_frame.csv", index=False)
    return {
        "teacher_name": teacher_name,
        "teacher_file": teacher_file,
        "submission_file": out_name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "teacher_changed_cells": int((np.abs(teacher_prob - base_prob) > TOL).sum()),
        "teacher_changed_rows": int(np.where(np.abs(teacher_prob - base_prob) > TOL)[0].size)
        if (np.abs(teacher_prob - base_prob) > TOL).ndim == 1
        else int(len(set(np.where(np.abs(teacher_prob - base_prob) > TOL)[0]))),
        "cell_oof": cell_outputs,
        "row_oof": row_diag,
        "og_gated_changed_cells": int((np.abs(decoded_prob - base_prob) > TOL).sum()),
        "og_gated_action_cells": int(len(audit)),
        "og_gated_mean_amp": float(audit["og_student_amp"].mean()) if len(audit) else 0.0,
        "og_gated_sign_agree_rate": float(audit["student_teacher_sign_agree"].mean()) if len(audit) else 0.0,
        "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
        "validation": validate_submission(root_path, sample, base_prob),
    }


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    # Build a temporary frame using S2-hub as the teacher; the function also
    # gives us the OG cohort-atlas feature columns.
    s2hub_prob = load_submission(S2HUB_TEACHER_FILE)[TARGETS].to_numpy(dtype=np.float64)
    base_frame, feature_cols = human_distill.build_cell_frame(sample, base_prob, s2hub_prob)
    outputs = {
        "s2hub_jackpot": evaluate_teacher(
            "s2hub_jackpot",
            S2HUB_TEACHER_FILE,
            base_frame,
            feature_cols,
            sample,
            base_prob,
            base_logit,
            base_grads,
            semantic_grads,
            h088_move,
        ),
        "stagebridge_jackpot": evaluate_teacher(
            "stagebridge_jackpot",
            STAGEBRIDGE_TEACHER_FILE,
            base_frame,
            feature_cols,
            sample,
            base_prob,
            base_logit,
            base_grads,
            semantic_grads,
            h088_move,
        ),
    }
    readout = {
        "experiment": "OG Human-State Distillation of S2-Hub HS-JEPA",
        "question": "Can OG cohort-relative human-state context explain S2-hub/stagebridge action support?",
        "public_score_used_for_teacher": True,
        "student_context_public_free": True,
        "outputs": outputs,
    }
    (OUT / "s2hub_human_state_distillation_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
