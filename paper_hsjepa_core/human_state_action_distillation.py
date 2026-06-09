#!/usr/bin/env python3
"""Human-State Action Distillation HS-JEPA.

This experiment separates the paper architecture from the competition decoder.

Question:
    The public-loss sparse tomography candidate is strong, but is it only a
    leaderboard-sensor trick? Or can its row-target action field be explained
    by OG human-state context?

Method:
    1. Build the OG raw-lifelog cohort atlas.
    2. Treat Candidate 1's sparse logit corrections as an action teacher.
    3. Build one row-target sample per test row/target.
    4. Train row-group OOF students that predict:
       - whether a cell receives a teacher action;
       - the signed teacher action magnitude.
    5. Decode a big-bet candidate by expanding teacher-consistent actions to
       high-student-support cells.

This is intentionally a research experiment. Candidate 1 remains the stronger
direct submission candidate; this script tests whether HS-JEPA can become a
generalizable architecture instead of an implicit experiment ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

import numpy as np
import pandas as pd

from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, roc_auc_score, mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
CURRENT_BEST_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
CURRENT_BEST_PUBLIC_LB = 0.5677475939
TEACHER_FILE = "submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv"

FINAL_CANDIDATE_DIR = ROOT / "final_hsjepa_candidates"
CANDIDATE1_MODULE = FINAL_CANDIDATE_DIR / "candidate_1_public_loss_sparse_tomography.py"
CANDIDATE2_MODULE = FINAL_CANDIDATE_DIR / "candidate_2_cohort_relative_atlas.py"


@dataclass(frozen=True)
class DecodeConfig:
    top_student_cells: int = 220
    teacher_keep_amp: float = 1.00
    expansion_amp: float = 0.62
    max_logit_step: float = 1.55
    min_student_prob: float = 0.20
    max_cells_per_row: int = 3
    max_cells_per_target: int = 52


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


candidate1 = import_module(CANDIDATE1_MODULE, "paper_core_candidate1")
candidate2 = import_module(CANDIDATE2_MODULE, "paper_core_candidate2")


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def clip_prob(values: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=np.float64), 1e-6, 1.0 - 1e-6)


def logit(values: np.ndarray) -> np.ndarray:
    p = clip_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(values, dtype=np.float64)))


def rank01(values: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique(dropna=True) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


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


def target_static_features(target: str) -> dict[str, float]:
    idx = TARGETS.index(target)
    return {
        "target_idx": float(idx),
        "is_q_target": float(target.startswith("Q")),
        "is_s_target": float(target.startswith("S")),
        "is_q2_q3_s2": float(target in {"Q2", "Q3", "S2"}),
        "is_objective_tail": float(target in {"S1", "S2", "S3", "S4"}),
        "target_prior_rank": float((idx + 1) / len(TARGETS)),
        **{f"target_onehot_{t}": float(t == target) for t in TARGETS},
    }


def build_cell_frame(sample: pd.DataFrame, base_prob: np.ndarray, teacher_prob: np.ndarray) -> tuple[pd.DataFrame, list[str]]:
    atlas, meta = candidate2.build_cohort_atlas()
    test_atlas = atlas[atlas["split"].eq("test")].copy().sort_values(KEYS).reset_index(drop=True)
    if not test_atlas[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise ValueError("cohort atlas test keys do not match sample keys")

    row_feature_cols = [
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
    ]
    row_feature_cols += [c for c in test_atlas.columns if c.startswith("human_state_latent_")]
    row_feature_cols += [f"peer_margin_{target}" for target in TARGETS]
    row_feature_cols = [c for c in row_feature_cols if c in test_atlas.columns]

    base_z = logit(base_prob)
    teacher_z = logit(teacher_prob)
    teacher_move = teacher_z - base_z

    rows = []
    for row_idx in range(len(sample)):
        base_row = {c: float(test_atlas.loc[row_idx, c]) for c in row_feature_cols}
        base_row["row"] = float(row_idx)
        base_row["row_frac"] = float(row_idx / max(len(sample) - 1, 1))
        base_row["subject_code"] = float(pd.factorize(sample["subject_id"])[0][row_idx])
        for target_idx, target in enumerate(TARGETS):
            rec = dict(base_row)
            rec.update(target_static_features(target))
            rec["target"] = target
            rec["target_idx_int"] = target_idx
            rec["base_prob"] = float(base_prob[row_idx, target_idx])
            rec["base_logit"] = float(base_z[row_idx, target_idx])
            rec["base_uncertainty"] = float(1.0 - abs(base_prob[row_idx, target_idx] - 0.5) * 2.0)
            rec["target_peer_margin"] = float(test_atlas.loc[row_idx, f"peer_margin_{target}"])
            rec["target_peer_margin_abs"] = abs(rec["target_peer_margin"])
            rec["target_peer_margin_sign"] = float(np.sign(rec["target_peer_margin"]))
            rec["teacher_logit_move"] = float(teacher_move[row_idx, target_idx])
            rec["teacher_has_action"] = float(abs(teacher_move[row_idx, target_idx]) > 1e-12)
            rec["teacher_action_sign"] = float(np.sign(teacher_move[row_idx, target_idx]))
            rows.append(rec)

    frame = pd.DataFrame(rows)
    feature_cols = [
        c for c in frame.columns
        if c not in {"target", "target_idx_int", "teacher_logit_move", "teacher_has_action", "teacher_action_sign"}
        and pd.api.types.is_numeric_dtype(frame[c])
    ]
    frame.attrs["cohort_meta"] = meta
    return frame, feature_cols


def make_classifier(seed: int):
    if seed % 2 == 0:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=4000, C=0.35, class_weight="balanced", solver="lbfgs")),
            ]
        )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "clf",
                ExtraTreesClassifier(
                    n_estimators=480,
                    min_samples_leaf=5,
                    max_features=0.65,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def make_sign_classifier(seed: int):
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_iter=160,
                    learning_rate=0.035,
                    max_leaf_nodes=15,
                    l2_regularization=0.15,
                    random_state=seed,
                ),
            ),
        ]
    )


def make_regressor(seed: int):
    if seed % 2 == 0:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("reg", Ridge(alpha=24.0)),
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


def oof_student(frame: pd.DataFrame, feature_cols: list[str]) -> tuple[pd.DataFrame, dict[str, object]]:
    x = frame[feature_cols]
    y_action = frame["teacher_has_action"].to_numpy(dtype=int)
    y_move = frame["teacher_logit_move"].to_numpy(dtype=np.float64)
    groups = frame["row"].astype(int).to_numpy()
    splits = list(GroupKFold(n_splits=5).split(x, y_action, groups=groups))

    action_prob = np.zeros(len(frame), dtype=np.float64)
    sign_prob = np.zeros(len(frame), dtype=np.float64)
    move_pred = np.zeros(len(frame), dtype=np.float64)
    signed_rows = np.abs(y_move) > 1e-12
    signed_y = (np.sign(y_move[signed_rows]) > 0).astype(int)

    for fold, (tr, val) in enumerate(splits):
        clf_preds = []
        sign_preds = []
        reg_preds = []
        for seed in [100 + fold, 200 + fold]:
            clf = make_classifier(seed)
            clf.fit(x.iloc[tr], y_action[tr])
            clf_preds.append(clf.predict_proba(x.iloc[val])[:, 1])

            reg = make_regressor(seed)
            reg.fit(x.iloc[tr], y_move[tr])
            reg_preds.append(reg.predict(x.iloc[val]))

            tr_signed = np.intersect1d(tr, np.flatnonzero(signed_rows))
            if len(np.unique((np.sign(y_move[tr_signed]) > 0).astype(int))) == 2:
                sign_clf = make_sign_classifier(seed)
                sign_clf.fit(x.iloc[tr_signed], (np.sign(y_move[tr_signed]) > 0).astype(int))
                sign_preds.append(sign_clf.predict_proba(x.iloc[val])[:, 1])
        action_prob[val] = np.mean(clf_preds, axis=0)
        move_pred[val] = np.mean(reg_preds, axis=0)
        sign_prob[val] = np.mean(sign_preds, axis=0) if sign_preds else 0.5

    frame = frame.copy()
    frame["student_oof_action_prob"] = action_prob
    frame["student_oof_sign_prob"] = sign_prob
    frame["student_oof_move"] = move_pred
    frame["student_oof_signed_move"] = action_prob * np.sign(sign_prob - 0.5) * np.minimum(1.55, np.abs(move_pred))

    rmse_all = float(np.sqrt(mean_squared_error(y_move, move_pred)))
    rmse_action = float(np.sqrt(mean_squared_error(y_move[signed_rows], move_pred[signed_rows])))
    diagnostics = {
        "oof_action_auc": float(roc_auc_score(y_action, action_prob)),
        "oof_action_average_precision": float(average_precision_score(y_action, action_prob)),
        "teacher_action_rate": float(y_action.mean()),
        "oof_move_rmse_all": rmse_all,
        "oof_move_rmse_action_cells": rmse_action,
        "oof_sign_auc_on_action_cells": float(roc_auc_score(signed_y, sign_prob[signed_rows])) if len(np.unique(signed_y)) == 2 else None,
        "feature_count": int(len(feature_cols)),
        "rows": int(frame["row"].nunique()),
        "cells": int(len(frame)),
        "teacher_action_cells": int(y_action.sum()),
    }
    return frame, diagnostics


def fit_full_student(frame: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    x = frame[feature_cols]
    y_action = frame["teacher_has_action"].to_numpy(dtype=int)
    y_move = frame["teacher_logit_move"].to_numpy(dtype=np.float64)
    signed_rows = np.abs(y_move) > 1e-12

    action_preds = []
    sign_preds = []
    move_preds = []
    for seed in [701, 702, 703, 704]:
        clf = make_classifier(seed)
        clf.fit(x, y_action)
        action_preds.append(clf.predict_proba(x)[:, 1])

        reg = make_regressor(seed)
        reg.fit(x, y_move)
        move_preds.append(reg.predict(x))

        if len(np.unique((np.sign(y_move[signed_rows]) > 0).astype(int))) == 2:
            sign_clf = make_sign_classifier(seed)
            sign_clf.fit(x.loc[signed_rows], (np.sign(y_move[signed_rows]) > 0).astype(int))
            sign_preds.append(sign_clf.predict_proba(x)[:, 1])

    out = frame.copy()
    out["student_full_action_prob"] = np.mean(action_preds, axis=0)
    out["student_full_sign_prob"] = np.mean(sign_preds, axis=0) if sign_preds else 0.5
    out["student_full_move"] = np.mean(move_preds, axis=0)
    out["student_full_signed_move"] = (
        out["student_full_action_prob"].to_numpy()
        * np.sign(out["student_full_sign_prob"].to_numpy() - 0.5)
        * np.minimum(1.55, np.abs(out["student_full_move"].to_numpy()))
    )
    return out


def decode_candidate(
    frame: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    teacher_prob: np.ndarray,
    config: DecodeConfig,
) -> tuple[np.ndarray, pd.DataFrame]:
    base_z = logit(base_prob).reshape(-1)
    teacher_move = logit(teacher_prob).reshape(-1) - base_z
    decoded_move = teacher_move.copy() * config.teacher_keep_amp

    frame = frame.copy()
    frame["flat_idx"] = frame["row"].astype(int) * len(TARGETS) + frame["target_idx_int"].astype(int)
    frame["already_teacher"] = np.abs(teacher_move[frame["flat_idx"].to_numpy(dtype=int)]) > 1e-12
    frame["student_score"] = (
        frame["student_full_action_prob"]
        * (0.35 + frame["atlas_action_health"])
        * (0.50 + frame["base_uncertainty"])
        * (1.0 + 0.25 * frame["target_peer_margin_abs"])
    )
    pool = frame[
        (~frame["already_teacher"])
        & (frame["student_full_action_prob"] >= config.min_student_prob)
        & (np.abs(frame["student_full_signed_move"]) > 1e-5)
    ].sort_values("student_score", ascending=False)

    selected = []
    row_count: dict[int, int] = {}
    target_count: dict[str, int] = {}
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if row_count.get(row, 0) >= config.max_cells_per_row:
            continue
        if target_count.get(target, 0) >= config.max_cells_per_target:
            continue
        flat = int(rec["flat_idx"])
        move = float(np.clip(config.expansion_amp * rec["student_full_signed_move"], -config.max_logit_step, config.max_logit_step))
        if abs(move) <= 1e-8:
            continue
        decoded_move[flat] = move
        selected.append({**rec, "decoded_logit_move": move, "source": "student_expansion"})
        row_count[row] = row_count.get(row, 0) + 1
        target_count[target] = target_count.get(target, 0) + 1
        if len(selected) >= config.top_student_cells:
            break

    teacher_rows = frame[frame["already_teacher"]].copy()
    teacher_rows["decoded_logit_move"] = teacher_move[teacher_rows["flat_idx"].to_numpy(dtype=int)] * config.teacher_keep_amp
    teacher_rows["source"] = "teacher_keep"
    audit = pd.concat([teacher_rows, pd.DataFrame(selected)], ignore_index=True, sort=False)

    decoded_prob = clip_prob(sigmoid(base_z + decoded_move).reshape(base_prob.shape))
    return decoded_prob, audit


def run() -> dict[str, object]:
    c1_readout = candidate1.run()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    teacher_prob = load_submission(c1_readout["root_path"])[TARGETS].to_numpy(dtype=np.float64)

    frame, feature_cols = build_cell_frame(sample, base_prob, teacher_prob)
    oof_frame, oof_diag = oof_student(frame, feature_cols)
    full_frame = fit_full_student(oof_frame, feature_cols)

    decoded_prob, audit = decode_candidate(full_frame, sample, base_prob, teacher_prob, DecodeConfig())
    digest = short_hash(decoded_prob)
    name = f"submission_hsjepa_paper_student_action_distill_{digest}_uploadsafe.csv"
    local_path = OUT / name
    root_path = ROOT / name
    write_submission(local_path, sample, decoded_prob)
    write_submission(root_path, sample, decoded_prob)

    move = logit(decoded_prob).reshape(-1) - base_logit
    listener_metrics = candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move)
    audit_cols = [
        "row",
        "target",
        "source",
        "teacher_logit_move",
        "decoded_logit_move",
        "student_full_action_prob",
        "student_full_sign_prob",
        "student_full_signed_move",
        "student_score",
        "atlas_action_health",
        "cohort_outlier_score",
        "peer_only_toxicity",
        "base_prob",
        "base_uncertainty",
        "target_peer_margin",
        "target_peer_margin_abs",
    ]
    audit[[c for c in audit_cols if c in audit.columns]].to_csv(OUT / "student_action_decode_audit.csv", index=False)
    full_frame.to_csv(OUT / "student_action_cell_frame.csv", index=False)

    readout = {
        "experiment": "Human-State Action Distillation HS-JEPA",
        "submission_file": name,
        "local_path": str(local_path.resolve()),
        "root_path": str(root_path.resolve()),
        "current_best_file": CURRENT_BEST_FILE,
        "current_best_public_lb": CURRENT_BEST_PUBLIC_LB,
        "teacher_file": c1_readout["submission_file"],
        "teacher_changed_cells": c1_readout["validation"]["changed_cells_vs_current_best"],
        "student_decoded_changed_cells": int((np.abs(decoded_prob - base_prob) > 1e-12).sum()),
        "student_expansion_cells": int((audit["source"] == "student_expansion").sum()),
        "oof_diagnostics": oof_diag,
        "listener_metrics": listener_metrics,
        "validation": validate_submission(root_path, sample, base_prob),
    }
    (OUT / "student_action_distillation_readout.json").write_text(
        json.dumps(readout, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    run()
