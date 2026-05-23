#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs


def load_folds() -> list[dict]:
    return json.loads((OUT_DIR / "validation" / "folds_chrono.json").read_text(encoding="utf-8"))["folds"]


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv")
    feat = con.execute(f"SELECT * FROM read_parquet('{FEATURE_DIR / 'model_features_v0.parquet'}')").df()
    df = train.merge(feat, on=["subject_id", "lifelog_date"], how="left")
    feature_cols = [c for c in feat.columns if c not in {"subject_id", "lifelog_date"}]
    folds = load_folds()
    configs = []
    for k in [10, 20, 30, 50, 80, 120, 200]:
        for C in [0.003, 0.01, 0.03, 0.1, 0.3]:
            for scaler in ["standard", "robust"]:
                configs.append((k, C, scaler))
    rows = []
    for k, C, scaler_name in configs:
        for fold in folds:
            valid_set = {(x["subject_id"], x["lifelog_date"]) for x in fold["valid_keys"]}
            is_valid = df.apply(lambda r: (r["subject_id"], r["lifelog_date"]) in valid_set, axis=1).to_numpy()
            x_train = df.loc[~is_valid, feature_cols]
            x_valid = df.loc[is_valid, feature_cols]
            target_scores = {}
            for y in LABELS:
                y_train = df.loc[~is_valid, y].astype(int).to_numpy()
                y_valid = df.loc[is_valid, y].astype(int).to_numpy()
                scaler = RobustScaler() if scaler_name == "robust" else StandardScaler()
                pipe = Pipeline([
                    ("impute", SimpleImputer(strategy="median")),
                    ("select", SelectKBest(score_func=f_classif, k=min(k, len(feature_cols)))),
                    ("scale", scaler),
                    ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000)),
                ])
                try:
                    pipe.fit(x_train, y_train)
                    p = pipe.predict_proba(x_valid)[:, 1]
                except Exception:
                    p = np.full(len(y_valid), y_train.mean())
                p = np.clip(p, 0.05, 0.95)
                target_scores[y] = log_loss(y_valid, p, labels=[0, 1])
            rows.append({"model": "selectk_logistic_feature_only", "k": k, "C": C, "scaler": scaler_name, "fold_id": fold["fold_id"], "mean_logloss": float(np.mean(list(target_scores.values()))), **{f"logloss_{a}": b for a,b in target_scores.items()}})
    res = pd.DataFrame(rows).sort_values("mean_logloss")
    out = EXPERIMENT_DIR / "probe_selectk_logistic_results.csv"
    res.to_csv(out, index=False)
    best = res.iloc[0].to_dict()
    (EXPERIMENT_DIR / "probe_selectk_logistic_best.json").write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")
    print("best", best)
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
