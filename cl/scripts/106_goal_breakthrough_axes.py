#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_selection import f_classif
from sklearn.impute import SimpleImputer

CL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = CL_ROOT.parent
sys.path.insert(0, str(CL_ROOT))

from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs, logloss

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5
V83_PATH = REPO_ROOT / "outputs/v83_repaired_v80/submission_v83_gq015_gs010.csv"

FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}

FEATURE_SPECS = [
    # Axis 1: BCG proxy state decoder for S1/S3.
    ("prior_sleep_window_features_v1.parquet", "S1", "bcg_s1_prior_window"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S1", "bcg_s1_boundary"),
    ("mechanism_sleep_load_features_v2.parquet", "S1", "bcg_s1_mechanism"),
    ("tiny_ae_residual_features_v1.parquet", "S1", "bcg_s1_tiny_ae"),
    ("prior_sleep_window_features_v1.parquet", "S3", "bcg_s3_prior_window"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S3", "bcg_s3_boundary"),
    ("mechanism_sleep_load_features_v2.parquet", "S3", "bcg_s3_mechanism"),
    ("tiny_ae_residual_features_v1.parquet", "S3", "bcg_s3_tiny_ae"),
    # Axis 2: separate subjective-Q and sensor-S measurement factors.
    ("stress_arousal_q_features_v1.parquet", "Q1", "qfac_q1_stress"),
    ("routine_deviation_features_v1.parquet", "Q1", "qfac_q1_routine"),
    ("stress_arousal_q_features_v1.parquet", "Q2", "qfac_q2_stress"),
    ("routine_deviation_features_v1.parquet", "Q2", "qfac_q2_routine"),
    ("stress_arousal_q_features_v1.parquet", "Q3", "qfac_q3_stress"),
    ("routine_deviation_features_v1.parquet", "Q3", "qfac_q3_routine"),
]

S1_BCG = [("bcg_s1_prior_window", 0.35), ("bcg_s1_boundary", 0.30), ("bcg_s1_mechanism", 0.25), ("bcg_s1_tiny_ae", 0.10)]
S3_BCG = [("bcg_s3_prior_window", 0.30), ("bcg_s3_boundary", 0.25), ("bcg_s3_mechanism", 0.30), ("bcg_s3_tiny_ae", 0.15)]
QFAC = {
    "Q1": [("qfac_q1_stress", 0.55), ("qfac_q1_routine", 0.45)],
    "Q2": [("qfac_q2_stress", 0.55), ("qfac_q2_routine", 0.45)],
    "Q3": [("qfac_q3_stress", 0.55), ("qfac_q3_routine", 0.45)],
}
LAG_CORE = {t: [(f"lag_{t}", 1.0)] for t in ["Q1", "Q2", "Q3", "S1", "S3"]}
LAG_ALL = {t: [(f"lag_{t}", 1.0)] for t in LABELS}

CANDIDATES = {
    "axis1_bcg_s1s3_g030": (0.030, {"S1": S1_BCG, "S3": S3_BCG}),
    "axis1_bcg_s1s3_g050": (0.050, {"S1": S1_BCG, "S3": S3_BCG}),
    "axis1_bcg_s1s3_g100_stress": (0.100, {"S1": S1_BCG, "S3": S3_BCG}),
    "axis2_twofactor_qonly_g030": (0.030, QFAC),
    "axis2_twofactor_qs_g030": (0.030, {**QFAC, "S1": S1_BCG, "S3": S3_BCG}),
    "axis2_twofactor_qs_g050": (0.050, {**QFAC, "S1": S1_BCG, "S3": S3_BCG}),
    "axis3_lag_core_g030": (0.030, LAG_CORE),
    "axis3_lag_core_g050": (0.050, LAG_CORE),
    "axis3_lag_core_g100_stress": (0.100, LAG_CORE),
    "axis3_lag_all_g030": (0.030, LAG_ALL),
    "combo_bcg_lag_core_g030": (
        0.030,
        {
            "Q1": [("lag_Q1", 0.75)],
            "Q2": [("lag_Q2", 0.75)],
            "Q3": [("lag_Q3", 0.75)],
            "S1": S1_BCG + [("lag_S1", 0.50)],
            "S3": S3_BCG + [("lag_S3", 0.50)],
        },
    ),
    "combo_twofactor_bcg_lag_g030": (
        0.030,
        {
            "Q1": QFAC["Q1"] + [("lag_Q1", 0.50)],
            "Q2": QFAC["Q2"] + [("lag_Q2", 0.50)],
            "Q3": QFAC["Q3"] + [("lag_Q3", 0.50)],
            "S1": S1_BCG + [("lag_S1", 0.50)],
            "S3": S3_BCG + [("lag_S3", 0.50)],
        },
    ),
}


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEYS:
        if col in out.columns and "date" in col:
            out[col] = pd.to_datetime(out[col]).dt.date.astype(str)
        elif col in out.columns:
            out[col] = out[col].astype(str)
    return out


def clip_prob(x, lo: float = EPS, hi: float = 1 - EPS):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip_prob(p)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -50, 50)))


def ll(y, p) -> float:
    return float(logloss(np.asarray(y, dtype=int), clip_prob(p, 1e-6, 1 - 1e-6)))


def load_train_test() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = norm_dates(pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv"))
    test = norm_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv"))
    return (
        train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
        test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
    )


def load_feature_file(name: str, train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    path = FEATURE_DIR / name
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    df = norm_dates(df)
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).reset_index(drop=True)
    merge_keys = [c for c in KEYS if c in df.columns]
    if "subject_id" not in merge_keys or not ({"sleep_date", "lifelog_date"} & set(merge_keys)):
        raise ValueError(f"{name} lacks a usable subject/date key: {df.columns[:8].tolist()}")
    merged = keys.merge(df, on=merge_keys, how="left")
    num = [c for c in merged.columns if c not in KEYS and pd.api.types.is_numeric_dtype(merged[c])]
    return merged[KEYS + num]


def fold_indices(train: pd.DataFrame, fold: dict) -> tuple[np.ndarray, np.ndarray]:
    idx = {(str(r.subject_id), str(r.lifelog_date)): i for i, r in train.reset_index(drop=True).iterrows()}
    tr = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["train_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    va = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["valid_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    return np.array(tr, dtype=int), np.array(va, dtype=int)


def subject_prior(train_part: pd.DataFrame, rows: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    global_rate = float(train_part[target].mean())
    pos = train_part.groupby("subject_id")[target].sum()
    cnt = train_part.groupby("subject_id")[target].count()
    rate = (pos + alpha * global_rate) / (cnt + alpha)
    return rows["subject_id"].map(rate).fillna(global_rate).to_numpy(float)


def select_cols(X: pd.DataFrame, y: np.ndarray, k: int = 120) -> list[str]:
    cols = [c for c in X.columns if X[c].notna().mean() >= 0.35 and X[c].nunique(dropna=True) > 2]
    if len(cols) <= k:
        return cols
    arr = SimpleImputer(strategy="median").fit_transform(X[cols].replace([np.inf, -np.inf], np.nan))
    try:
        scores, _ = f_classif(arr, y)
        order = np.argsort(np.nan_to_num(scores, nan=-np.inf))[::-1][:k]
        return [cols[i] for i in order]
    except Exception:
        return cols[:k]


def fit_model(X: pd.DataFrame, y: np.ndarray) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        max_iter=120,
        learning_rate=0.035,
        max_leaf_nodes=15,
        min_samples_leaf=10,
        l2_regularization=0.12,
        random_state=2026,
    )
    model.fit(X.replace([np.inf, -np.inf], np.nan), y)
    return model


def rank_center(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x, dtype=float)
    finite = np.isfinite(x)
    if finite.sum() <= 1:
        return out
    r = pd.Series(x[finite]).rank(method="average").to_numpy(float)
    r = (r - 0.5) / len(r)
    r = (r - r.mean()) / max(r.std(), 1e-9)
    out[finite] = np.clip(r, -2.5, 2.5)
    out -= out.mean()
    return out


def sleep_state_pred(row_pred: pd.DataFrame) -> pd.Series:
    weights = {"Q1": 0.03, "Q2": 0.08, "Q3": 0.45, "S1": 0.48, "S2": 0.42, "S3": 0.08, "S4": 0.16}
    vals = []
    for r in row_pred.itertuples(index=False):
        w = weights.get(r.target, 0.0)
        vals.append(float(sigmoid((1 - w) * logit(r.anchor) + w * logit(r.model))))
    return pd.Series(vals, index=row_pred.index)


def lag_predict(query_subject: str, query_date: pd.Timestamp, pool: pd.DataFrame, target: str, prior: float, window: int = 7, halflife: float = 3.0, alpha: float = 3.0) -> float:
    g = pool[pool["subject_id"].eq(query_subject)]
    if g.empty:
        return prior
    diff = (pd.to_datetime(g["lifelog_date"]) - query_date).dt.days.abs()
    mask = diff <= window
    if not mask.any():
        return prior
    w = np.power(0.5, diff[mask].to_numpy(float) / halflife)
    y = g.loc[mask, target].to_numpy(float)
    return float((np.dot(w, y) + alpha * prior) / (w.sum() + alpha))


def collect_feature_signals(train: pd.DataFrame, test: pd.DataFrame, feature_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    base_rows = pd.read_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv")
    base_rows["base"] = sleep_state_pred(base_rows)
    records = []
    for feat_name, target, signal_name in FEATURE_SPECS:
        feat = feature_tables[feat_name].iloc[: len(train)].reset_index(drop=True)
        num = [c for c in feat.columns if c not in KEYS]
        for fold_family, fold_path in FOLD_FILES.items():
            for fold in json.loads(fold_path.read_text())["folds"]:
                tr_idx, va_idx = fold_indices(train, fold)
                tr_rows = train.iloc[tr_idx].reset_index(drop=True)
                va_rows = train.iloc[va_idx].reset_index(drop=True)
                ytr = tr_rows[target].astype(int).to_numpy()
                cols = select_cols(feat.iloc[tr_idx][num], ytr)
                if not cols:
                    continue
                anchor_tr = subject_prior(tr_rows, tr_rows, target)
                Xtr = feat.iloc[tr_idx][cols].copy()
                Xtr["anchor_logit"] = logit(anchor_tr)
                model = fit_model(Xtr, ytr)
                anchor_va = subject_prior(tr_rows, va_rows, target)
                Xva = feat.iloc[va_idx][cols].copy()
                Xva["anchor_logit"] = logit(anchor_va)
                p = clip_prob(model.predict_proba(Xva.replace([np.inf, -np.inf], np.nan))[:, 1], 0.03, 0.97)
                base = base_rows[
                    base_rows["family"].eq(fold_family)
                    & base_rows["fold"].eq(fold["name"])
                    & base_rows["target"].eq(target)
                ]
                base_by_row = dict(zip(base["row_index"].astype(int), base["base"].astype(float)))
                for j, row_i in enumerate(va_idx):
                    records.append(
                        {
                            "axis": "bcg" if signal_name.startswith("bcg_") else "twofactor",
                            "signal": signal_name,
                            "fold_family": fold_family,
                            "fold": fold["name"],
                            "row_index": int(row_i),
                            "target": target,
                            "y": int(train.iloc[row_i][target]),
                            "anchor": float(anchor_va[j]),
                            "base": float(base_by_row.get(int(row_i), anchor_va[j])),
                            "raw_resid": float(logit(p[j]) - logit(anchor_va[j])),
                            "n_features": int(len(cols)),
                        }
                    )
    return pd.DataFrame(records)


def collect_lag_signals(train: pd.DataFrame) -> pd.DataFrame:
    base_rows = pd.read_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv")
    base_rows["base"] = sleep_state_pred(base_rows)
    records = []
    train_dt = train.copy()
    train_dt["lifelog_date_dt"] = pd.to_datetime(train_dt["lifelog_date"])
    for fold_family, fold_path in FOLD_FILES.items():
        for fold in json.loads(fold_path.read_text())["folds"]:
            tr_idx, va_idx = fold_indices(train, fold)
            tr_rows = train_dt.iloc[tr_idx].reset_index(drop=True)
            va_rows = train_dt.iloc[va_idx].reset_index(drop=True)
            for target in LABELS:
                base = base_rows[
                    base_rows["family"].eq(fold_family)
                    & base_rows["fold"].eq(fold["name"])
                    & base_rows["target"].eq(target)
                ]
                base_by_row = dict(zip(base["row_index"].astype(int), base["base"].astype(float)))
                for j, row_i in enumerate(va_idx):
                    row = va_rows.iloc[j]
                    prior = subject_prior(tr_rows, pd.DataFrame([row]), target)[0]
                    p = lag_predict(str(row.subject_id), pd.to_datetime(row.lifelog_date), tr_rows, target, prior)
                    records.append(
                        {
                            "axis": "lag",
                            "signal": f"lag_{target}",
                            "fold_family": fold_family,
                            "fold": fold["name"],
                            "row_index": int(row_i),
                            "target": target,
                            "y": int(train.iloc[row_i][target]),
                            "anchor": float(prior),
                            "base": float(base_by_row.get(int(row_i), prior)),
                            "raw_resid": float(logit(p) - logit(prior)),
                            "n_features": 0,
                        }
                    )
    return pd.DataFrame(records)


def train_test_feature_signals(train: pd.DataFrame, test: pd.DataFrame, feature_tables: dict[str, pd.DataFrame]) -> dict[str, np.ndarray]:
    signals: dict[str, np.ndarray] = {}
    for feat_name, target, signal_name in FEATURE_SPECS:
        feat = feature_tables[feat_name].reset_index(drop=True)
        num = [c for c in feat.columns if c not in KEYS]
        X_all = feat.iloc[: len(train)][num]
        y = train[target].astype(int).to_numpy()
        cols = select_cols(X_all, y)
        anchor_train = subject_prior(train, train, target)
        anchor_test = subject_prior(train, test, target)
        Xtr = X_all[cols].copy()
        Xtr["anchor_logit"] = logit(anchor_train)
        Xte = feat.iloc[len(train) : len(train) + len(test)][cols].copy()
        Xte["anchor_logit"] = logit(anchor_test)
        model = fit_model(Xtr, y)
        p = clip_prob(model.predict_proba(Xte.replace([np.inf, -np.inf], np.nan))[:, 1], 0.03, 0.97)
        signals[signal_name] = rank_center(logit(p) - logit(anchor_test))
    return signals


def train_test_lag_signals(train: pd.DataFrame, test: pd.DataFrame) -> dict[str, np.ndarray]:
    train_dt = train.copy()
    train_dt["lifelog_date"] = pd.to_datetime(train_dt["lifelog_date"])
    out = {}
    for target in LABELS:
        vals = []
        for row in test.itertuples(index=False):
            prior = subject_prior(train_dt, pd.DataFrame([{"subject_id": row.subject_id}]), target)[0]
            vals.append(lag_predict(str(row.subject_id), pd.to_datetime(row.lifelog_date), train_dt, target, prior))
        anchor = subject_prior(train_dt, test, target)
        out[f"lag_{target}"] = rank_center(logit(np.asarray(vals)) - logit(anchor))
    return out


def evaluate_candidates(oof: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    agg_rows = []
    target_rows = []
    for cand_name, (gamma, target_map) in CANDIDATES.items():
        for fold_family, fam in oof.groupby("fold_family"):
            base_losses = []
            new_losses = []
            moves = []
            for target, parts in target_map.items():
                gt = fam[fam["target"].eq(target)]
                combo = None
                y = None
                base = None
                for signal, weight in parts:
                    g = gt[gt["signal"].eq(signal)]
                    if g.empty:
                        continue
                    r = rank_center(g["raw_resid"].to_numpy(float)) * weight
                    if combo is None:
                        combo = r
                        y = g["y"].to_numpy(int)
                        base = g["base"].to_numpy(float)
                    else:
                        combo = combo + r
                if combo is None or y is None or base is None:
                    continue
                combo = rank_center(combo)
                pred = clip_prob(sigmoid(logit(base) + gamma * combo), 0.03, 0.97)
                bll = ll(y, base)
                nll = ll(y, pred)
                base_losses.append(bll)
                new_losses.append(nll)
                moves.append(float(np.mean(np.abs(pred - base))))
                target_rows.append(
                    {
                        "candidate": cand_name,
                        "fold_family": fold_family,
                        "target": target,
                        "base_logloss": bll,
                        "new_logloss": nll,
                        "delta": nll - bll,
                        "move": float(np.mean(np.abs(pred - base))),
                    }
                )
            if base_losses:
                agg_rows.append(
                    {
                        "candidate": cand_name,
                        "fold_family": fold_family,
                        "gamma": gamma,
                        "base_logloss": float(np.mean(base_losses)),
                        "new_logloss": float(np.mean(new_losses)),
                        "delta": float(np.mean(new_losses) - np.mean(base_losses)),
                        "move": float(np.mean(moves)),
                    }
                )
    agg = pd.DataFrame(agg_rows)
    target = pd.DataFrame(target_rows)
    agg.to_csv(EXPERIMENT_DIR / "goal_breakthrough_axes_oof_scores.csv", index=False)
    target.to_csv(EXPERIMENT_DIR / "goal_breakthrough_axes_target_scores.csv", index=False)
    return agg, target


def load_v83(test: pd.DataFrame) -> pd.DataFrame:
    v83 = norm_dates(pd.read_csv(V83_PATH))
    if not v83[KEYS].astype(str).equals(test[KEYS].astype(str)):
        v83 = test[KEYS].merge(v83, on=KEYS, how="left")
    if v83[LABELS].isna().any().any():
        raise ValueError("v83 base does not align with test sample")
    return v83


def write_candidates(test: pd.DataFrame, v83: pd.DataFrame, signals: dict[str, np.ndarray]) -> pd.DataFrame:
    base = v83[LABELS].to_numpy(float)
    rows = []
    for cand_name, (gamma, target_map) in CANDIDATES.items():
        cand = base.copy()
        for target, parts in target_map.items():
            idx = LABELS.index(target)
            combo = np.zeros(len(test), dtype=float)
            active = 0.0
            for signal, weight in parts:
                if signal not in signals:
                    continue
                combo += weight * signals[signal]
                active += abs(weight)
            if active <= 0:
                continue
            combo = rank_center(combo)
            cand[:, idx] = clip_prob(sigmoid(logit(base[:, idx]) + gamma * combo), 0.03, 0.97)
        out = test[KEYS].copy()
        for i, target in enumerate(LABELS):
            out[target] = cand[:, i]
        path = OUT_DIR / f"submission_goal_breakthrough_{cand_name}_prob.csv"
        out.to_csv(path, index=False)
        move = np.abs(cand - base)
        rows.append(
            {
                "candidate": cand_name,
                "file": str(path),
                "gamma": gamma,
                "mean_abs_move_v83": float(move.mean()),
                "max_abs_move_v83": float(move.max()),
                **{f"dmean_{t}": float(cand[:, i].mean() - base[:, i].mean()) for i, t in enumerate(LABELS)},
            }
        )
    manifest = pd.DataFrame(rows).sort_values(["mean_abs_move_v83", "candidate"])
    manifest.to_csv(EXPERIMENT_DIR / "goal_breakthrough_axes_candidate_files.csv", index=False)
    return manifest


def bce_soft(q: np.ndarray, p: np.ndarray) -> float:
    p = clip_prob(p, 1e-6, 1 - 1e-6)
    return float(np.mean(-(q * np.log(p) + (1 - q) * np.log(1 - p))))


def score_public_posteriors(manifest: pd.DataFrame, v83: pd.DataFrame) -> pd.DataFrame:
    posterior_paths = {
        "refit_public_anchor": EXPERIMENT_DIR / "cl_public_anchor_clue_refit_posterior_values.csv",
        "old_public_anchor": REPO_ROOT / "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv",
    }
    base = v83[LABELS].to_numpy(float)
    rows = []
    for posterior_name, path in posterior_paths.items():
        if not path.exists():
            continue
        q = pd.read_csv(path)[LABELS].to_numpy(float)
        base_score = bce_soft(q, base)
        rows.append({"posterior": posterior_name, "candidate": "v83_base", "posterior_bce": base_score, "vs_v83": 0.0})
        for row in manifest.itertuples(index=False):
            vals = pd.read_csv(row.file)[LABELS].to_numpy(float)
            score = bce_soft(q, vals)
            rows.append({"posterior": posterior_name, "candidate": row.candidate, "posterior_bce": score, "vs_v83": score - base_score})
    out = pd.DataFrame(rows)
    out.to_csv(EXPERIMENT_DIR / "goal_breakthrough_axes_posterior_scores.csv", index=False)
    return out


def to_md(df: pd.DataFrame) -> str:
    if df.empty:
        return "(empty)"
    text = df.copy()
    for col in text.columns:
        if pd.api.types.is_float_dtype(text[col]):
            text[col] = text[col].map(lambda x: f"{x:.6f}")
        else:
            text[col] = text[col].astype(str)
    cols = list(text.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in text.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def write_report(agg: pd.DataFrame, target: pd.DataFrame, manifest: pd.DataFrame, posterior: pd.DataFrame) -> None:
    summary = (
        agg.groupby("candidate", as_index=False)
        .agg(delta_mean=("delta", "mean"), delta_worst=("delta", "max"), move_mean=("move", "mean"))
        .sort_values(["delta_worst", "delta_mean"])
    )
    lines = [
        "# Goal breakthrough axes",
        "",
        "All three requested axes are evaluated as v83-anchored centered residual-rank signals, not direct probability submissions.",
        "",
        "Axes:",
        "- Axis 1: S1/S3 BCG proxy state decoder from sleep-window, boundary/rest, mechanism, and tiny-AE residual features.",
        "- Axis 2: Q/S two-factor measurement model using subjective Q factors separately from sensor-S/BCG factors.",
        "- Axis 3: same-subject lag/nearest-label transition rule.",
        "",
        "Formula: `candidate_t = sigmoid(logit(v83_t) + gamma * rank_center(axis_signal_t))`.",
        "",
        "## OOF stress summary",
        "",
        to_md(summary),
        "",
        "## Target-level OOF details",
        "",
        to_md(target.sort_values(["candidate", "fold_family", "target"])),
        "",
        "## Candidate files",
        "",
        to_md(manifest),
        "",
        "## Public-posterior diagnostics",
        "",
        to_md(posterior.sort_values(["posterior", "posterior_bce"])),
        "",
        "Decision rule: carry forward candidates that improve every fold-family, stay close to v83, and avoid broad target mean drift.",
    ]
    (EXPERIMENT_DIR / "goal_breakthrough_axes_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    train, test = load_train_test()
    feature_names = sorted({name for name, _, _ in FEATURE_SPECS})
    feature_tables = {name: load_feature_file(name, train, test) for name in feature_names}
    feature_oof = collect_feature_signals(train, test, feature_tables)
    lag_oof = collect_lag_signals(train)
    oof = pd.concat([feature_oof, lag_oof], ignore_index=True)
    oof.to_csv(EXPERIMENT_DIR / "goal_breakthrough_axes_oof_signals.csv", index=False)
    agg, target = evaluate_candidates(oof)
    signals = train_test_feature_signals(train, test, feature_tables)
    signals.update(train_test_lag_signals(train, test))
    v83 = load_v83(test)
    manifest = write_candidates(test, v83, signals)
    posterior = score_public_posteriors(manifest, v83)
    write_report(agg, target, manifest, posterior)
    print((EXPERIMENT_DIR / "goal_breakthrough_axes_report.md").read_text())


if __name__ == "__main__":
    main()
