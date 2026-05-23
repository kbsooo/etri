#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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
    assert len(df) == len(train), (len(df), len(train))

    feature_cols = [c for c in feat.columns if c not in {"subject_id", "lifelog_date"}]
    # dominant_state is categorical-ish but numeric; keep as numeric for v0.
    folds = load_folds()
    Cs = [0.01, 0.03, 0.1, 0.3, 1.0]
    rows = []
    pred_dir = EXPERIMENT_DIR / "probe_predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)

    for C in Cs:
        for fold in folds:
            valid_set = {(k["subject_id"], k["lifelog_date"]) for k in fold["valid_keys"]}
            is_valid = df.apply(lambda r: (r["subject_id"], r["lifelog_date"]) in valid_set, axis=1).to_numpy()
            x_train = df.loc[~is_valid, feature_cols]
            x_valid = df.loc[is_valid, feature_cols]
            fold_preds = pd.DataFrame(df.loc[is_valid, ["subject_id", "sleep_date", "lifelog_date"]].reset_index(drop=True))
            target_scores = {}
            for y in LABELS:
                y_train = df.loc[~is_valid, y].astype(int).to_numpy()
                y_valid = df.loc[is_valid, y].astype(int).to_numpy()
                if len(np.unique(y_train)) < 2:
                    p = np.full(len(y_valid), y_train.mean())
                else:
                    pipe = Pipeline([
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                        ("clf", LogisticRegression(C=C, penalty="l2", solver="liblinear", max_iter=1000)),
                    ])
                    pipe.fit(x_train, y_train)
                    p = pipe.predict_proba(x_valid)[:, 1]
                p = np.clip(p, 0.03, 0.97)
                fold_preds[y] = p
                target_scores[y] = log_loss(y_valid, p, labels=[0, 1])
            mean_score = float(np.mean(list(target_scores.values())))
            rows.append({"model": "logistic_l2_features_v0", "C": C, "fold_id": fold["fold_id"], "mean_logloss": mean_score, **{f"logloss_{k}": v for k, v in target_scores.items()}})
            fold_preds.to_csv(pred_dir / f"logistic_l2_C{C}_{fold['fold_id']}.csv", index=False)

    res = pd.DataFrame(rows).sort_values("mean_logloss")
    out_csv = EXPERIMENT_DIR / "probe_logistic_l2_results.csv"
    res.to_csv(out_csv, index=False)
    best = res.iloc[0].to_dict()
    (EXPERIMENT_DIR / "probe_logistic_l2_best.json").write_text(json.dumps(best, ensure_ascii=False, indent=2), encoding="utf-8")
    print("best", best)
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
