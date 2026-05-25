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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs, logloss

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}

SELECTED = [
    ("prior_sleep_proxy_features_v1.parquet", "S1"),
    ("prior_sleep_window_features_v1.parquet", "S1"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S1"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "Q1"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S2"),
    ("goal4_sleep_boundary_rest_features_v1.parquet", "S4"),
    ("goal4_hour_transition_features_v1.parquet", "Q3"),
    ("goal4_hour_transition_features_v1.parquet", "S2"),
]


def norm_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in KEYS:
        if c in out.columns and "date" in c:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
        elif c in out.columns:
            out[c] = out[c].astype(str)
    return out


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = norm_dates(pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv"))
    test = norm_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv"))
    return (
        train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
        test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True),
    )


def fold_indices(train: pd.DataFrame, fold: dict) -> tuple[np.ndarray, np.ndarray]:
    idx = {(str(r.subject_id), str(r.lifelog_date)): i for i, r in train.reset_index(drop=True).iterrows()}
    tr = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["train_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    va = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["valid_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    return np.array(tr, dtype=int), np.array(va, dtype=int)


def clip(x, lo=0.03, hi=0.97):
    return np.clip(np.asarray(x, dtype=float), lo, hi)


def logit(p):
    p = clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def blend(a, b, mode: str, w: float, temp: float = 1.0):
    if mode == "prob":
        return clip(a * (1 - w) + b * w)
    return clip(sigmoid(((1 - w) * logit(a) + w * logit(b)) / temp))


def ll(y, p):
    return float(logloss(np.asarray(y, dtype=int), clip(p)))


def subject_prior(train: pd.DataFrame, rows: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    rate = (pos + alpha * g) / (cnt + alpha)
    return rows["subject_id"].map(rate).fillna(g).to_numpy(float)


def sleep_state_pred(row_pred: pd.DataFrame) -> pd.Series:
    weights = {"Q1": 0.03, "Q2": 0.08, "Q3": 0.45, "S1": 0.48, "S2": 0.42, "S3": 0.08, "S4": 0.16}
    out = []
    for r in row_pred.itertuples(index=False):
        w = weights.get(r.target, 0.0)
        out.append(float(blend(np.array([r.anchor]), np.array([r.model]), "logit", w, 1.08)[0]))
    return pd.Series(out, index=row_pred.index)


def load_feature_file(name: str, train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    path = FEATURE_DIR / name
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
    df = norm_dates(df)
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).reset_index(drop=True)
    out = keys.merge(df, on=KEYS, how="left")
    num = [c for c in out.columns if c not in KEYS and pd.api.types.is_numeric_dtype(out[c])]
    return out[KEYS + num]


def select_cols(X: pd.DataFrame, y: np.ndarray, k: int = 100) -> list[str]:
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


def fit_model(Xtr: pd.DataFrame, ytr: np.ndarray) -> HistGradientBoostingClassifier:
    model = HistGradientBoostingClassifier(
        max_iter=110,
        learning_rate=0.04,
        max_leaf_nodes=15,
        min_samples_leaf=10,
        l2_regularization=0.08,
        random_state=2026,
    )
    model.fit(Xtr.replace([np.inf, -np.inf], np.nan), ytr)
    return model


def collect_selected_oof(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    row_pred = pd.read_csv(EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv")
    row_pred["sleep_state"] = sleep_state_pred(row_pred)
    frames = {name: load_feature_file(name, train, test) for name, _ in SELECTED}
    records = []
    for feat_name, target in SELECTED:
        feat = frames[feat_name].iloc[: len(train)].reset_index(drop=True)
        num = [c for c in feat.columns if c not in KEYS]
        for fold_family, path in FOLD_FILES.items():
            folds = json.loads(path.read_text())["folds"]
            for fold in folds:
                tr_idx, va_idx = fold_indices(train, fold)
                tr0 = train.iloc[tr_idx].reset_index(drop=True)
                va0 = train.iloc[va_idx].reset_index(drop=True)
                ytr = tr0[target].astype(int).to_numpy()
                cols = select_cols(feat.iloc[tr_idx][num], ytr)
                if not cols:
                    continue
                anchor_tr = subject_prior(tr0, tr0, target)
                Xtr = feat.iloc[tr_idx][cols].copy()
                Xtr["anchor_logit"] = logit(anchor_tr)
                model = fit_model(Xtr, ytr)
                anchor_va = subject_prior(tr0, va0, target)
                Xva = feat.iloc[va_idx][cols].copy()
                Xva["anchor_logit"] = logit(anchor_va)
                p = clip(model.predict_proba(Xva.replace([np.inf, -np.inf], np.nan))[:, 1])
                rp = row_pred[
                    row_pred["family"].eq(fold_family)
                    & row_pred["fold"].eq(fold["name"])
                    & row_pred["target"].eq(target)
                ].copy()
                by_row = dict(zip(rp["row_index"].astype(int), rp["sleep_state"].astype(float)))
                for j, row_i in enumerate(va_idx):
                    records.append(
                        {
                            "feature_file": feat_name,
                            "feature_family": Path(feat_name).stem,
                            "fold_family": fold_family,
                            "fold": fold["name"],
                            "row_index": int(row_i),
                            "target": target,
                            "y": int(train.iloc[row_i][target]),
                            "anchor": float(anchor_va[j]),
                            "sleep_state": float(by_row.get(int(row_i), anchor_va[j])),
                            "feature_pred": float(p[j]),
                            "n_features": int(len(cols)),
                        }
                    )
    out = pd.DataFrame(records)
    out.to_csv(EXPERIMENT_DIR / "cl_clue_family_oof_predictions.csv", index=False)
    return out


def search_over_sleep(oof: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for (feature_file, target), g_all in oof.groupby(["feature_file", "target"]):
        for mode in ["prob", "logit"]:
            for w in [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.55, 0.70]:
                for temp in ([1.0] if mode == "prob" else [1.0, 1.08, 1.16, 1.25]):
                    fam_scores = {}
                    moves = []
                    for fam, g in g_all.groupby("fold_family"):
                        p = blend(g["sleep_state"].to_numpy(float), g["feature_pred"].to_numpy(float), mode, w, temp)
                        fam_scores[fam] = ll(g["y"], p)
                        base = ll(g["y"], g["sleep_state"])
                        moves.append(float(np.abs(p - g["sleep_state"]).mean()))
                    rows.append(
                        {
                            "feature_file": feature_file,
                            "feature_family": Path(feature_file).stem,
                            "target": target,
                            "mode": mode,
                            "weight": w,
                            "temp": temp,
                            "chrono": fam_scores.get("chrono_tail", np.nan),
                            "hole": fam_scores.get("hole_v1", np.nan),
                            "mirror": fam_scores.get("mirror_v1", np.nan),
                            "mirror_hole": np.nanmean([fam_scores.get("hole_v1", np.nan), fam_scores.get("mirror_v1", np.nan)]),
                            "worst": np.nanmax(list(fam_scores.values())),
                            "mean_move_vs_sleep": float(np.mean(moves)),
                        }
                    )
    grid = pd.DataFrame(rows)
    base_rows = []
    for (feature_file, target), g_all in oof.groupby(["feature_file", "target"]):
        fam = {}
        for ff, g in g_all.groupby("fold_family"):
            fam[ff] = ll(g["y"], g["sleep_state"])
        base_rows.append(
            {
                "feature_file": feature_file,
                "target": target,
                "base_chrono": fam.get("chrono_tail", np.nan),
                "base_hole": fam.get("hole_v1", np.nan),
                "base_mirror": fam.get("mirror_v1", np.nan),
                "base_mirror_hole": np.nanmean([fam.get("hole_v1", np.nan), fam.get("mirror_v1", np.nan)]),
            }
        )
    base = pd.DataFrame(base_rows)
    merged = grid.merge(base, on=["feature_file", "target"], how="left")
    merged["delta_mirror_hole_vs_sleep"] = merged["mirror_hole"] - merged["base_mirror_hole"]
    merged["delta_chrono_vs_sleep"] = merged["chrono"] - merged["base_chrono"]
    merged["selection_score"] = (
        merged["delta_mirror_hole_vs_sleep"]
        + np.maximum(0.0, merged["delta_chrono_vs_sleep"] - 0.002)
        + np.maximum(0.0, merged["mean_move_vs_sleep"] - 0.05) * 0.20
    )
    merged.to_csv(EXPERIMENT_DIR / "cl_clue_family_over_sleep_grid.csv", index=False)
    best = merged.sort_values(["feature_file", "target", "selection_score"]).groupby(["feature_file", "target"], as_index=False).first()
    best.to_csv(EXPERIMENT_DIR / "cl_clue_family_over_sleep_best.csv", index=False)
    return merged, best.sort_values("selection_score")


def train_full_preds(train: pd.DataFrame, test: pd.DataFrame, best: pd.DataFrame) -> dict[tuple[str, str], np.ndarray]:
    preds = {}
    frames = {name: load_feature_file(name, train, test) for name in best["feature_file"].unique()}
    for r in best.itertuples(index=False):
        feat = frames[r.feature_file].reset_index(drop=True)
        train_feat = feat.iloc[: len(train)].reset_index(drop=True)
        test_feat = feat.iloc[len(train) :].reset_index(drop=True)
        num = [c for c in train_feat.columns if c not in KEYS]
        y = train[r.target].astype(int).to_numpy()
        cols = select_cols(train_feat[num], y)
        anchor_tr = subject_prior(train, train, r.target)
        anchor_te = subject_prior(train, test, r.target)
        Xtr = train_feat[cols].copy()
        Xte = test_feat[cols].copy()
        Xtr["anchor_logit"] = logit(anchor_tr)
        Xte["anchor_logit"] = logit(anchor_te)
        model = fit_model(Xtr, y)
        preds[(r.feature_file, r.target)] = clip(model.predict_proba(Xte.replace([np.inf, -np.inf], np.nan))[:, 1])
    return preds


def build_candidates(train: pd.DataFrame, test: pd.DataFrame, best: pd.DataFrame) -> pd.DataFrame:
    sleep = norm_dates(pd.read_csv(OUT_DIR / "submission_cl_catboost_state_proto_sleep_state_prob.csv")).sort_values(KEYS).reset_index(drop=True)
    sample = norm_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv")).sort_values(KEYS).reset_index(drop=True)
    preds = train_full_preds(train, test, best)
    chosen = best[
        (best["delta_mirror_hole_vs_sleep"] < -0.001)
        & (best["delta_chrono_vs_sleep"] < 0.006)
        & (best["weight"] > 0)
    ].copy()
    chosen = chosen.sort_values("selection_score").groupby("target", as_index=False).first()
    rows = []

    def write_one(name: str, targets: list[str], cap_s2: bool = False) -> None:
        out = sleep.copy()
        for r in chosen.itertuples(index=False):
            if r.target not in targets:
                continue
            pred = preds[(r.feature_file, r.target)]
            base = sleep[r.target].to_numpy(float)
            w = min(float(r.weight), 0.25 if (cap_s2 and r.target == "S2") else float(r.weight))
            out[r.target] = blend(base, pred, r.mode, w, float(r.temp))
        out = out[sample.columns]
        path = OUT_DIR / name
        out.to_csv(path, index=False)
        for y in LABELS:
            rows.append(
                {
                    "file": name,
                    "target": y,
                    "keys_ok": bool(out[KEYS].equals(sample[KEYS])),
                    "no_na": bool(out[LABELS].notna().all().all()),
                    "mean_abs_vs_sleep": float(np.abs(out[y] - sleep[y]).mean()),
                    "mean": float(out[y].mean()),
                    "min": float(out[y].min()),
                    "max": float(out[y].max()),
                }
            )

    write_one("submission_cl_clue_s1_only_sleep_family_prob.csv", ["S1"])
    write_one("submission_cl_clue_q1_s1_sleep_boundary_prob.csv", ["Q1", "S1"])
    write_one("submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv", ["Q1", "Q3", "S1", "S2", "S4"], cap_s2=True)
    summary = pd.DataFrame(rows)
    summary.to_csv(EXPERIMENT_DIR / "cl_clue_family_candidate_summary.csv", index=False)
    chosen.to_csv(EXPERIMENT_DIR / "cl_clue_family_chosen_targets.csv", index=False)
    return summary


def md_table(df: pd.DataFrame, n: int = 20) -> str:
    if df.empty:
        return "_empty_"
    d = df.head(n).copy()
    cols = list(d.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        vals = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                vals.append(f"{float(v):.6f}")
            else:
                vals.append(str(v))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def main() -> None:
    ensure_dirs()
    train, test = load_data()
    oof = collect_selected_oof(train, test)
    _, best = search_over_sleep(oof)
    summary = build_candidates(train, test, best)
    report = "\n".join(
        [
            "# CL Clue Family Candidates",
            "",
            "## Best Feature-Family Blends Over Sleep-State",
            "",
            md_table(best[["feature_file", "target", "mode", "weight", "temp", "delta_mirror_hole_vs_sleep", "delta_chrono_vs_sleep", "mean_move_vs_sleep", "selection_score"]], 30),
            "",
            "## Candidate Files",
            "",
            md_table(summary, 40),
            "",
            "## Interpretation",
            "",
            "- These candidates are not broad CatBoost extrapolations. They only apply feature families that improved over the current sleep-state baseline in fold-local OOF.",
            "- The strictest candidate is S1-only because S1 has the largest stable signal and today's public feedback says overmoving S2/Q3 is dangerous.",
        ]
    )
    (EXPERIMENT_DIR / "cl_clue_family_candidates_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
