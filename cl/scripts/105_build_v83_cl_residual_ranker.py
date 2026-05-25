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

SELECTED = [
    ("prior_sleep_proxy_features_v1.parquet", "S1", "s1_prior_proxy"),
    ("prior_sleep_window_features_v1.parquet", "S1", "s1_prior_window"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S1", "s1_boundary_rest"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "Q1", "q1_boundary_rest"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S2", "s2_boundary_rest"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S4", "s4_boundary_rest"),
]

S1_MAP = {"S1": [("s1_prior_proxy", 0.50), ("s1_prior_window", 0.30), ("s1_boundary_rest", 0.20)]}
Q1_MAP = {"Q1": [("q1_boundary_rest", 1.00)]}
Q1S1_MAP = {
    "Q1": [("q1_boundary_rest", 1.00)],
    "S1": [("s1_prior_proxy", 0.50), ("s1_prior_window", 0.30), ("s1_boundary_rest", 0.20)],
}
SLEEP_FAMILY_MAP = {
    "Q1": [("q1_boundary_rest", 1.00)],
    "S1": [("s1_prior_proxy", 0.50), ("s1_prior_window", 0.30), ("s1_boundary_rest", 0.20)],
    "S2": [("s2_boundary_rest", 1.00)],
    "S4": [("s4_boundary_rest", 1.00)],
}

CANDIDATES = {
    "s1_rank_g005": S1_MAP,
    "s1_rank_g010": S1_MAP,
    "s1_rank_g030": S1_MAP,
    "s1_rank_g050": S1_MAP,
    "s1_rank_g100_stress": S1_MAP,
    "q1_rank_g005": Q1_MAP,
    "q1_rank_g030": Q1_MAP,
    "q1s1_rank_g005": Q1S1_MAP,
    "q1s1_rank_g010": Q1S1_MAP,
    "q1s1_rank_g030": Q1S1_MAP,
    "q1s1_rank_g050": Q1S1_MAP,
    "sleep_family_rank_g005": SLEEP_FAMILY_MAP,
    "sleep_family_rank_g030": SLEEP_FAMILY_MAP,
    "sleep_family_rank_g050": SLEEP_FAMILY_MAP,
}

GAMMAS = {
    "s1_rank_g005": 0.005,
    "s1_rank_g010": 0.010,
    "s1_rank_g030": 0.030,
    "s1_rank_g050": 0.050,
    "s1_rank_g100_stress": 0.100,
    "q1_rank_g005": 0.005,
    "q1_rank_g030": 0.030,
    "q1s1_rank_g005": 0.005,
    "q1s1_rank_g010": 0.010,
    "q1s1_rank_g030": 0.030,
    "q1s1_rank_g050": 0.050,
    "sleep_family_rank_g005": 0.005,
    "sleep_family_rank_g030": 0.030,
    "sleep_family_rank_g050": 0.050,
}


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEYS:
        if col in out.columns and "date" in col:
            out[col] = pd.to_datetime(out[col]).dt.date.astype(str)
        elif col in out.columns:
            out[col] = out[col].astype(str)
    return out


def clip_prob(x: np.ndarray | pd.Series | float, lo: float = EPS, hi: float = 1 - EPS):
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
    merged = keys.merge(df, on=KEYS, how="left")
    num = [c for c in merged.columns if c not in KEYS and pd.api.types.is_numeric_dtype(merged[c])]
    return merged[KEYS + num]


def subject_prior(train_part: pd.DataFrame, rows: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    global_rate = float(train_part[target].mean())
    pos = train_part.groupby("subject_id")[target].sum()
    cnt = train_part.groupby("subject_id")[target].count()
    rate = (pos + alpha * global_rate) / (cnt + alpha)
    return rows["subject_id"].map(rate).fillna(global_rate).to_numpy(float)


def fold_indices(train: pd.DataFrame, fold: dict) -> tuple[np.ndarray, np.ndarray]:
    idx = {(str(r.subject_id), str(r.lifelog_date)): i for i, r in train.reset_index(drop=True).iterrows()}
    tr = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["train_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    va = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["valid_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    return np.array(tr, dtype=int), np.array(va, dtype=int)


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
        max_iter=130,
        learning_rate=0.035,
        max_leaf_nodes=15,
        min_samples_leaf=10,
        l2_regularization=0.10,
        random_state=2026,
    )
    model.fit(X.replace([np.inf, -np.inf], np.nan), y)
    return model


def rank_center(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    finite = np.isfinite(x)
    out = np.zeros_like(x, dtype=float)
    if finite.sum() <= 1:
        return out
    s = pd.Series(x[finite]).rank(method="average").to_numpy(float)
    s = (s - 0.5) / len(s)
    s = (s - s.mean()) / max(s.std(), 1e-9)
    out[finite] = np.clip(s, -2.5, 2.5)
    out -= out.mean()
    return out


def sleep_state_pred(row_pred: pd.DataFrame) -> pd.Series:
    weights = {"Q1": 0.03, "Q2": 0.08, "Q3": 0.45, "S1": 0.48, "S2": 0.42, "S3": 0.08, "S4": 0.16}
    vals = []
    for r in row_pred.itertuples(index=False):
        w = weights.get(r.target, 0.0)
        vals.append(float(sigmoid((1 - w) * logit(r.anchor) + w * logit(r.model))))
    return pd.Series(vals, index=row_pred.index)


def collect_oof_signals(train: pd.DataFrame, feature_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    cached = EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv"
    base_rows = pd.read_csv(cached)
    base_rows["base"] = sleep_state_pred(base_rows)
    records = []
    for feat_name, target, signal_name in SELECTED:
        feat = feature_tables[feat_name].iloc[: len(train)].reset_index(drop=True)
        num = [c for c in feat.columns if c not in KEYS]
        for fold_family, fold_path in FOLD_FILES.items():
            folds = json.loads(fold_path.read_text())["folds"]
            for fold in folds:
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
                            "signal": signal_name,
                            "feature_file": feat_name,
                            "fold_family": fold_family,
                            "fold": fold["name"],
                            "row_index": int(row_i),
                            "target": target,
                            "y": int(train.iloc[row_i][target]),
                            "anchor": float(anchor_va[j]),
                            "base": float(base_by_row.get(int(row_i), anchor_va[j])),
                            "feature_pred": float(p[j]),
                            "raw_resid": float(logit(p[j]) - logit(anchor_va[j])),
                            "n_features": int(len(cols)),
                        }
                    )
    oof = pd.DataFrame(records)
    oof.to_csv(EXPERIMENT_DIR / "cl_v83_residual_ranker_oof_signals.csv", index=False)
    return oof


def evaluate_oof(oof: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cand_name, target_map in CANDIDATES.items():
        gamma = GAMMAS[cand_name]
        for fold_family, fam in oof.groupby("fold_family"):
            losses_base = []
            losses_new = []
            drifts = []
            target_rows = []
            for target, parts in target_map.items():
                g_target = fam[fam["target"].eq(target)]
                if g_target.empty:
                    continue
                pivot = None
                y = None
                base = None
                for signal, weight in parts:
                    g = g_target[g_target["signal"].eq(signal)].copy()
                    if g.empty:
                        continue
                    r = rank_center(g["raw_resid"].to_numpy(float)) * weight
                    if pivot is None:
                        pivot = r
                        y = g["y"].to_numpy(int)
                        base = g["base"].to_numpy(float)
                    else:
                        pivot = pivot + r
                if pivot is None or y is None or base is None:
                    continue
                pivot = rank_center(pivot)
                pred = clip_prob(sigmoid(logit(base) + gamma * pivot), 0.03, 0.97)
                losses_base.append(ll(y, base))
                losses_new.append(ll(y, pred))
                drifts.append(float(np.mean(np.abs(pred - base))))
                target_rows.append(
                    {
                        "candidate": cand_name,
                        "fold_family": fold_family,
                        "target": target,
                        "base_logloss": ll(y, base),
                        "new_logloss": ll(y, pred),
                        "delta": ll(y, pred) - ll(y, base),
                        "mean_abs_move_base": float(np.mean(np.abs(pred - base))),
                    }
                )
            if losses_base:
                rows.append(
                    {
                        "candidate": cand_name,
                        "fold_family": fold_family,
                        "gamma": gamma,
                        "base_logloss": float(np.mean(losses_base)),
                        "new_logloss": float(np.mean(losses_new)),
                        "delta": float(np.mean(losses_new) - np.mean(losses_base)),
                        "mean_abs_move_base": float(np.mean(drifts)),
                    }
                )
                rows.extend(target_rows)
    out = pd.DataFrame(rows)
    out.to_csv(EXPERIMENT_DIR / "cl_v83_residual_ranker_oof_scores.csv", index=False)
    return out


def train_test_signals(train: pd.DataFrame, test: pd.DataFrame, feature_tables: dict[str, pd.DataFrame]) -> dict[str, np.ndarray]:
    signals: dict[str, np.ndarray] = {}
    for feat_name, target, signal_name in SELECTED:
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
        pred = clip_prob(model.predict_proba(Xte.replace([np.inf, -np.inf], np.nan))[:, 1], 0.03, 0.97)
        signals[signal_name] = rank_center(logit(pred) - logit(anchor_test))
    return signals


def load_v83(test: pd.DataFrame) -> pd.DataFrame:
    v83 = norm_dates(pd.read_csv(V83_PATH))
    if not v83[KEYS].astype(str).equals(test[KEYS].astype(str)):
        v83 = test[KEYS].merge(v83, on=KEYS, how="left")
    if v83[LABELS].isna().any().any():
        raise ValueError("v83 base does not align with sample keys")
    return v83


def write_candidates(test: pd.DataFrame, v83: pd.DataFrame, signals: dict[str, np.ndarray]) -> pd.DataFrame:
    base = v83[LABELS].to_numpy(float)
    rows = []
    for cand_name, target_map in CANDIDATES.items():
        gamma = GAMMAS[cand_name]
        cand = base.copy()
        for target, parts in target_map.items():
            idx = LABELS.index(target)
            combo = np.zeros(len(test), dtype=float)
            active = 0.0
            for signal, weight in parts:
                if signal not in signals:
                    continue
                combo += weight * signals[signal]
                active += weight
            if active <= 0:
                continue
            combo = rank_center(combo)
            cand[:, idx] = clip_prob(sigmoid(logit(base[:, idx]) + gamma * combo), 0.03, 0.97)
        out = test[KEYS].copy()
        for i, target in enumerate(LABELS):
            out[target] = cand[:, i]
        path = OUT_DIR / f"submission_cl_v83_residual_ranker_{cand_name}_prob.csv"
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
    manifest.to_csv(EXPERIMENT_DIR / "cl_v83_residual_ranker_candidate_files.csv", index=False)
    return manifest


def bce_soft(q: np.ndarray, p: np.ndarray) -> float:
    p = clip_prob(p, 1e-6, 1 - 1e-6)
    return float(np.mean(-(q * np.log(p) + (1 - q) * np.log(1 - p))))


def score_public_posteriors(manifest: pd.DataFrame, v83: pd.DataFrame) -> pd.DataFrame:
    posterior_paths = {
        "refit_public_anchor": EXPERIMENT_DIR / "cl_public_anchor_clue_refit_posterior_values.csv",
        "old_public_anchor": REPO_ROOT / "outputs/public_lb_pseudolabel_calibration/posterior_values_only.csv",
    }
    rows = []
    base = v83[LABELS].to_numpy(float)
    for posterior_name, path in posterior_paths.items():
        if not path.exists():
            continue
        q = pd.read_csv(path)[LABELS].to_numpy(float)
        base_score = bce_soft(q, base)
        rows.append(
            {
                "posterior": posterior_name,
                "candidate": "v83_base",
                "posterior_bce": base_score,
                "vs_v83": 0.0,
            }
        )
        for row in manifest.itertuples(index=False):
            vals = pd.read_csv(row.file)[LABELS].to_numpy(float)
            score = bce_soft(q, vals)
            rows.append(
                {
                    "posterior": posterior_name,
                    "candidate": row.candidate,
                    "posterior_bce": score,
                    "vs_v83": score - base_score,
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(EXPERIMENT_DIR / "cl_v83_residual_ranker_posterior_scores.csv", index=False)
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


def write_report(oof_scores: pd.DataFrame, manifest: pd.DataFrame, posterior_scores: pd.DataFrame) -> None:
    cand_summary = (
        oof_scores[oof_scores.get("target", pd.Series(index=oof_scores.index)).isna()]
        .groupby("candidate", as_index=False)
        .agg(delta_mean=("delta", "mean"), delta_worst=("delta", "max"), move_mean=("mean_abs_move_base", "mean"))
        if "target" in oof_scores.columns
        else pd.DataFrame()
    )
    if cand_summary.empty:
        cand_summary = (
            oof_scores.groupby("candidate", as_index=False)
            .agg(delta_mean=("delta", "mean"), delta_worst=("delta", "max"), move_mean=("mean_abs_move_base", "mean"))
        )
    lines = [
        "# CL v83 residual ranker",
        "",
        "Purpose: keep the v83 public coordinate fixed and inject only centered CL residual rank signals.",
        "",
        "Formula:",
        "",
        "`candidate_t = sigmoid(logit(v83_t) + gamma * rank_center(CL_residual_signal_t))`",
        "",
        "The CL model is not used as direct probability. Each injected signal is target-wise mean-zero and rank-normalized.",
        "",
        "## OOF stress over CL validation anchors",
        "",
        to_md(cand_summary.sort_values(["delta_worst", "delta_mean"])),
        "",
        "## Candidate files",
        "",
        to_md(manifest),
        "",
        "## Public-posterior diagnostics",
        "",
        to_md(posterior_scores.sort_values(["posterior", "posterior_bce"])),
        "",
        "Read: negative OOF delta means the residual rank helped over the CL validation anchor. Upload trust still depends on staying close to v83; these files are diagnostic candidates, not a 0.57 claim.",
    ]
    (EXPERIMENT_DIR / "cl_v83_residual_ranker_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    train, test = load_train_test()
    feature_tables = {name: load_feature_file(name, train, test) for name, _, _ in SELECTED}
    oof = collect_oof_signals(train, feature_tables)
    oof_scores = evaluate_oof(oof)
    signals = train_test_signals(train, test, feature_tables)
    v83 = load_v83(test)
    manifest = write_candidates(test, v83, signals)
    posterior_scores = score_public_posteriors(manifest, v83)
    write_report(oof_scores, manifest, posterior_scores)
    print((EXPERIMENT_DIR / "cl_v83_residual_ranker_report.md").read_text())


if __name__ == "__main__":
    main()
