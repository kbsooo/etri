#!/usr/bin/env python3
from __future__ import annotations

import json
import math
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
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, ID_COLS, LABELS, OUT_DIR, ensure_dirs, logloss

warnings.filterwarnings("ignore")

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}

KNOWN_PUBLIC = {
    "submission_temporal_state_smoothing_wcap01_prob.csv": 0.6394201335,
    "submission_temporal_state_smoothing_wcap02_prob.csv": 0.6311869686,
    "submission_v38_targetwise_catboost_proto_safe_prob.csv": 0.6218639574,
    "submission_cl_catboost_state_proto_sleep_state_prob.csv": 0.6146217599,
    "submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv": 0.6610032443,
}


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
    return 1.0 / (1.0 + np.exp(-z))


def blend(anchor: np.ndarray, model: np.ndarray, mode: str, weight: float, temp: float = 1.0) -> np.ndarray:
    if mode == "prob":
        return clip(anchor * (1 - weight) + model * weight)
    return clip(sigmoid(((1 - weight) * logit(anchor) + weight * logit(model)) / temp))


def ll(y, p) -> float:
    return float(logloss(np.asarray(y, dtype=int), clip(p)))


def subject_prior(train: pd.DataFrame, rows: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    rate = (pos + alpha * g) / (cnt + alpha)
    return rows["subject_id"].map(rate).fillna(g).to_numpy(float)


def read_sub(path: Path) -> pd.DataFrame | None:
    try:
        df = norm_dates(pd.read_csv(path))
    except Exception:
        return None
    if not set(KEYS + LABELS).issubset(df.columns):
        return None
    return df.sort_values(KEYS).reset_index(drop=True)[KEYS + LABELS]


def test_meta(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in test.iterrows():
        g = train[train["subject_id"].eq(r.subject_id)].copy()
        d = pd.to_datetime(r.lifelog_date)
        gd = pd.to_datetime(g["lifelog_date"])
        before = gd[gd < d]
        after = gd[gd > d]
        nearest = np.nan
        if len(before) or len(after):
            nearest = float(
                np.nanmin(
                    [
                        (d - before.max()).days if len(before) else np.nan,
                        (after.min() - d).days if len(after) else np.nan,
                    ]
                )
            )
        rows.append(
            {
                **{k: r[k] for k in KEYS},
                "inside_train_range": int(len(gd) and d >= gd.min() and d <= gd.max()),
                "after_train_range": int(len(gd) and d > gd.max()),
                "has_future_train": int(len(after) > 0),
                "nearest_train_gap_d": nearest,
                "weekday": int(d.weekday()),
            }
        )
    return pd.DataFrame(rows)


def submission_axis_audit(train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = norm_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv")).sort_values(KEYS).reset_index(drop=True)
    anchor = read_sub(OUT_DIR / "submission_meta_anchor_w02_noq3_prob.csv")
    sleep = read_sub(OUT_DIR / "submission_cl_catboost_state_proto_sleep_state_prob.csv")
    raw = read_sub(OUT_DIR / "submission_v38_targetwise_catboost_proto_raw_model_prob.csv")
    bad = read_sub(OUT_DIR / "submission_v39_imported_v81_conditional_latent_routing_raw_prob.csv")
    if anchor is None:
        anchor = sample.copy()
        for y in LABELS:
            anchor[y] = subject_prior(train, test, y)
    tm = test_meta(train, test).sort_values(KEYS).reset_index(drop=True)
    masks = {
        "all": np.ones(len(sample), dtype=bool),
        "inside_future": tm["inside_train_range"].eq(1).to_numpy(),
        "tail_after": tm["after_train_range"].eq(1).to_numpy(),
        "small_gap_le3": tm["nearest_train_gap_d"].le(3).fillna(False).to_numpy(),
    }
    rows = []
    file_rows = []
    for path in sorted(OUT_DIR.glob("submission_*.csv")):
        df = read_sub(path)
        if df is None or not df[KEYS].equals(sample[KEYS]):
            continue
        file_rows.append({"file": path.name, "known_public_lb": KNOWN_PUBLIC.get(path.name, np.nan)})
        for target in LABELS:
            d_anchor = df[target].to_numpy(float) - anchor[target].to_numpy(float)
            d_sleep = df[target].to_numpy(float) - sleep[target].to_numpy(float) if sleep is not None else np.full(len(df), np.nan)
            d_raw = df[target].to_numpy(float) - raw[target].to_numpy(float) if raw is not None else np.full(len(df), np.nan)
            d_bad = df[target].to_numpy(float) - bad[target].to_numpy(float) if bad is not None else np.full(len(df), np.nan)
            good_axis = sleep[target].to_numpy(float) - anchor[target].to_numpy(float) if sleep is not None else np.zeros(len(df))
            bad_axis = bad[target].to_numpy(float) - anchor[target].to_numpy(float) if bad is not None else np.zeros(len(df))
            for mask_name, mask in masks.items():
                def corr(a, b):
                    if mask.sum() < 3 or np.nanstd(a[mask]) < 1e-9 or np.nanstd(b[mask]) < 1e-9:
                        return np.nan
                    return float(np.corrcoef(a[mask], b[mask])[0, 1])

                rows.append(
                    {
                        "file": path.name,
                        "target": target,
                        "mask": mask_name,
                        "known_public_lb": KNOWN_PUBLIC.get(path.name, np.nan),
                        "mean_abs_vs_anchor": float(np.abs(d_anchor[mask]).mean()),
                        "mean_delta_vs_anchor": float(d_anchor[mask].mean()),
                        "mean_abs_vs_sleep": float(np.abs(d_sleep[mask]).mean()),
                        "mean_abs_vs_raw": float(np.abs(d_raw[mask]).mean()),
                        "mean_abs_vs_bad_import": float(np.abs(d_bad[mask]).mean()),
                        "corr_with_good_sleep_axis": corr(d_anchor, good_axis),
                        "corr_with_bad_import_axis": corr(d_anchor, bad_axis),
                    }
                )
    detail = pd.DataFrame(rows)
    by_file = (
        detail[detail["mask"].eq("all")]
        .groupby("file", as_index=False)
        .agg(
            known_public_lb=("known_public_lb", "first"),
            move_vs_anchor=("mean_abs_vs_anchor", "mean"),
            dist_vs_sleep=("mean_abs_vs_sleep", "mean"),
            dist_vs_raw=("mean_abs_vs_raw", "mean"),
            dist_vs_bad_import=("mean_abs_vs_bad_import", "mean"),
            good_axis_corr=("corr_with_good_sleep_axis", "mean"),
            bad_axis_corr=("corr_with_bad_import_axis", "mean"),
        )
    )
    by_file["public_axis_score"] = (
        -by_file["dist_vs_sleep"]
        + 0.25 * by_file["dist_vs_bad_import"]
        + 0.02 * by_file["good_axis_corr"].fillna(0)
        - 0.02 * by_file["bad_axis_corr"].fillna(0)
        - np.maximum(0.0, by_file["move_vs_anchor"] - 0.07)
    )
    detail.to_csv(EXPERIMENT_DIR / "cl_exhaustive_submission_axis_detail.csv", index=False)
    by_file.sort_values("public_axis_score", ascending=False).to_csv(EXPERIMENT_DIR / "cl_exhaustive_submission_axis_summary.csv", index=False)
    return detail, by_file.sort_values("public_axis_score", ascending=False)


def load_feature_family(path: Path, keys: pd.DataFrame) -> pd.DataFrame | None:
    try:
        if path.suffix == ".parquet":
            df = pd.read_parquet(path)
        elif path.suffix == ".csv":
            df = pd.read_csv(path)
        else:
            return None
    except Exception:
        return None
    if not set(KEYS).issubset(df.columns):
        return None
    df = norm_dates(df)
    df = keys.merge(df, on=KEYS, how="left")
    num = [c for c in df.columns if c not in KEYS and pd.api.types.is_numeric_dtype(df[c])]
    if not num:
        return None
    return df[KEYS + num]


def select_cols(X: pd.DataFrame, y: np.ndarray, max_k: int = 80) -> list[str]:
    cols = [c for c in X.columns if X[c].notna().mean() >= 0.35 and X[c].nunique(dropna=True) > 2]
    if not cols:
        return []
    Xs = X[cols].replace([np.inf, -np.inf], np.nan)
    if len(cols) <= max_k:
        return cols
    imp = SimpleImputer(strategy="median")
    arr = imp.fit_transform(Xs)
    try:
        scores, _ = f_classif(arr, y)
        order = np.argsort(np.nan_to_num(scores, nan=-np.inf))[::-1][:max_k]
        return [cols[i] for i in order]
    except Exception:
        return cols[:max_k]


def fit_predict_family(Xtr: pd.DataFrame, ytr: np.ndarray, Xva: pd.DataFrame) -> np.ndarray:
    if len(np.unique(ytr)) < 2:
        return np.full(len(Xva), float(np.mean(ytr)))
    model = HistGradientBoostingClassifier(
        max_iter=80,
        learning_rate=0.045,
        max_leaf_nodes=15,
        min_samples_leaf=12,
        l2_regularization=0.08,
        random_state=2026,
    )
    model.fit(Xtr.replace([np.inf, -np.inf], np.nan), ytr)
    return clip(model.predict_proba(Xva.replace([np.inf, -np.inf], np.nan))[:, 1])


def feature_family_scout(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).reset_index(drop=True)
    feature_paths = sorted(list(FEATURE_DIR.glob("*.parquet")) + list(FEATURE_DIR.glob("*.csv")))
    rows = []
    for path in feature_paths:
        fam = path.stem
        feat = load_feature_family(path, keys)
        if feat is None:
            continue
        Xfull = feat.iloc[: len(train)].reset_index(drop=True)
        numeric_cols = [c for c in Xfull.columns if c not in KEYS]
        if not numeric_cols:
            continue
        for family, fold_path in FOLD_FILES.items():
            folds = json.loads(fold_path.read_text())["folds"]
            for fold in folds:
                tr_idx, va_idx = fold_indices(train, fold)
                tr0 = train.iloc[tr_idx].reset_index(drop=True)
                va0 = train.iloc[va_idx].reset_index(drop=True)
                for target in LABELS:
                    ytr = tr0[target].astype(int).to_numpy()
                    yva = va0[target].astype(int).to_numpy()
                    anchor_tr = subject_prior(tr0, tr0, target)
                    anchor_va = subject_prior(tr0, va0, target)
                    cols = select_cols(Xfull.iloc[tr_idx][numeric_cols], ytr, max_k=80)
                    if not cols:
                        continue
                    Xtr = Xfull.iloc[tr_idx][cols].copy()
                    Xva = Xfull.iloc[va_idx][cols].copy()
                    Xtr["anchor_logit"] = logit(anchor_tr)
                    Xva["anchor_logit"] = logit(anchor_va)
                    pred = fit_predict_family(Xtr, ytr, Xva)
                    base = ll(yva, anchor_va)
                    best = {"mode": "raw", "weight": 1.0, "temp": 1.0, "pred": pred, "loss": ll(yva, pred)}
                    for mode in ["prob", "logit"]:
                        for w in [0.05, 0.10, 0.20, 0.35, 0.50]:
                            for temp in ([1.0] if mode == "prob" else [1.0, 1.08, 1.16]):
                                p = blend(anchor_va, pred, mode, w, temp)
                                loss = ll(yva, p)
                                if loss < best["loss"]:
                                    best = {"mode": mode, "weight": w, "temp": temp, "pred": p, "loss": loss}
                    rows.append(
                        {
                            "feature_family": fam,
                            "feature_file": path.name,
                            "fold_family": family,
                            "fold": fold["name"],
                            "target": target,
                            "n_valid": int(len(va_idx)),
                            "n_features_used": int(len(cols) + 1),
                            "anchor_logloss": base,
                            "best_logloss": float(best["loss"]),
                            "delta_vs_anchor": float(best["loss"] - base),
                            "best_mode": best["mode"],
                            "best_weight": float(best["weight"]),
                            "best_temp": float(best["temp"]),
                            "mean_abs_move": float(np.abs(best["pred"] - anchor_va).mean()),
                            "selected_features": "|".join(cols[:20]),
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(EXPERIMENT_DIR / "cl_exhaustive_feature_family_scores_raw.csv", index=False)
    if out.empty:
        return out
    agg = (
        out.groupby(["feature_family", "feature_file", "target"], as_index=False)
        .agg(
            n=("n_valid", "sum"),
            mean_delta=("delta_vs_anchor", "mean"),
            chrono_delta=("delta_vs_anchor", lambda s: float(out.loc[s.index][out.loc[s.index, "fold_family"].eq("chrono_tail")]["delta_vs_anchor"].mean())),
            hole_delta=("delta_vs_anchor", lambda s: float(out.loc[s.index][out.loc[s.index, "fold_family"].eq("hole_v1")]["delta_vs_anchor"].mean())),
            mirror_delta=("delta_vs_anchor", lambda s: float(out.loc[s.index][out.loc[s.index, "fold_family"].eq("mirror_v1")]["delta_vs_anchor"].mean())),
            mean_abs_move=("mean_abs_move", "mean"),
            mean_features=("n_features_used", "mean"),
        )
    )
    agg["mirror_hole_delta"] = (agg["hole_delta"] + agg["mirror_delta"]) / 2
    agg["worst_delta"] = agg[["chrono_delta", "hole_delta", "mirror_delta"]].max(axis=1)
    agg["consistent_gain"] = (agg[["chrono_delta", "hole_delta", "mirror_delta"]] < -0.001).all(axis=1)
    agg["scout_score"] = agg["mirror_hole_delta"] + np.maximum(0.0, agg["worst_delta"] - 0.002) + np.maximum(0.0, agg["mean_abs_move"] - 0.06) * 0.25
    agg.sort_values(["scout_score", "mirror_hole_delta"]).to_csv(EXPERIMENT_DIR / "cl_exhaustive_feature_family_summary.csv", index=False)
    return agg.sort_values(["scout_score", "mirror_hole_delta"])


def row_prediction_oracle() -> tuple[pd.DataFrame, pd.DataFrame]:
    row_path = EXPERIMENT_DIR / "cl_public_calibrated_validation_row_predictions.csv"
    if not row_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    rp = pd.read_csv(row_path)
    rows = []
    for (family, target), g in rp.groupby(["family", "target"]):
        y = g["y"].to_numpy(int)
        a = g["anchor"].to_numpy(float)
        m = g["model"].to_numpy(float)
        for mask_name, mask in {
            "all": np.ones(len(g), dtype=bool),
            "inside": g["inside_fold_train"].eq(1).to_numpy(),
            "tail_after": g["after_fold_train"].eq(1).to_numpy(),
            "has_future": g["has_future_fold_train"].eq(1).to_numpy(),
            "gap_le3": g["nearest_fold_train_gap"].le(3).fillna(False).to_numpy(),
        }.items():
            if mask.sum() < 10:
                continue
            base = ll(y[mask], a[mask])
            raw = ll(y[mask], m[mask])
            best = {"mode": "raw", "weight": 1.0, "temp": 1.0, "loss": raw, "move": float(np.abs(m[mask] - a[mask]).mean())}
            for mode in ["prob", "logit"]:
                for w in np.linspace(0, 0.8, 17):
                    for temp in ([1.0] if mode == "prob" else [1.0, 1.08, 1.16, 1.25]):
                        p = blend(a[mask], m[mask], mode, float(w), float(temp))
                        loss = ll(y[mask], p)
                        if loss < best["loss"]:
                            best = {"mode": mode, "weight": float(w), "temp": float(temp), "loss": loss, "move": float(np.abs(p - a[mask]).mean())}
            rows.append(
                {
                    "fold_family": family,
                    "target": target,
                    "mask": mask_name,
                    "n": int(mask.sum()),
                    "anchor_logloss": base,
                    "raw_model_logloss": raw,
                    "best_logloss": float(best["loss"]),
                    "best_delta_vs_anchor": float(best["loss"] - base),
                    "best_mode": best["mode"],
                    "best_weight": best["weight"],
                    "best_temp": best["temp"],
                    "mean_abs_move": best["move"],
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(EXPERIMENT_DIR / "cl_exhaustive_row_oracle_detail.csv", index=False)
    summary = (
        detail.groupby(["target", "mask"], as_index=False)
        .agg(
            mean_delta=("best_delta_vs_anchor", "mean"),
            worst_delta=("best_delta_vs_anchor", "max"),
            mean_weight=("best_weight", "mean"),
            mean_move=("mean_abs_move", "mean"),
            families=("fold_family", "nunique"),
        )
        .sort_values(["mean_delta", "worst_delta"])
    )
    summary.to_csv(EXPERIMENT_DIR / "cl_exhaustive_row_oracle_summary.csv", index=False)
    return detail, summary


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
    sub_detail, sub_summary = submission_axis_audit(train, test)
    oracle_detail, oracle_summary = row_prediction_oracle()
    feature_summary = feature_family_scout(train, test)

    best_features = feature_summary[
        (feature_summary["consistent_gain"].eq(True))
        & (feature_summary["mirror_hole_delta"] < -0.003)
        & (feature_summary["worst_delta"] < 0.004)
    ].copy() if not feature_summary.empty else pd.DataFrame()

    known = sub_summary[sub_summary["known_public_lb"].notna()].sort_values("known_public_lb")
    top_unsubmitted_like = sub_summary[sub_summary["known_public_lb"].isna()].head(15)
    strongest_oracle = oracle_summary[(oracle_summary["mean_delta"] < -0.006) & (oracle_summary["worst_delta"] < 0.004)].head(20)

    lines = [
        "# CL Exhaustive Clue Hunt",
        "",
        "## Claim",
        "",
        "This run does not assume a new submission can be uploaded today. It exhaustively reuses current local evidence: submitted-file movement geometry, fold-local row predictions, and every numeric `cl/features` family.",
        "",
        "## Known Public Axis",
        "",
        md_table(known, 20),
        "",
        "Interpretation: the best known public move is still the CL sleep-state axis. The imported/raw axis is explicitly anti-public, so new clues must be either close to sleep-state or orthogonal to both sleep-state and imported raw.",
        "",
        "## Existing Files Closest To The Good Axis",
        "",
        md_table(top_unsubmitted_like[["file", "public_axis_score", "move_vs_anchor", "dist_vs_sleep", "dist_vs_bad_import", "good_axis_corr", "bad_axis_corr"]], 15),
        "",
        "## Row-Level Oracle From Fold-Local CatBoost",
        "",
        md_table(strongest_oracle, 20),
        "",
        "Interpretation: this is the upper-bound map for where the current CatBoost/prototype signal is real. Targets/masks absent here should not be pushed without a new feature family.",
        "",
        "## New Feature-Family Clues",
        "",
        md_table(best_features[["feature_family", "target", "mirror_hole_delta", "worst_delta", "mean_delta", "mean_abs_move", "mean_features"]], 25),
        "",
        "## Decision",
        "",
    ]
    if best_features.empty:
        lines.append("- No feature family passed the strict consistent-gain gate. That means the current 0.57 route is not another broad feature dump; it needs target/mask-isolated probing.")
    else:
        top = best_features.head(8)
        lines.append("- Feature families that passed strict gates are the only credible new-signal candidates. Use them target-wise, not as global model input.")
        for r in top.itertuples(index=False):
            lines.append(f"- `{r.feature_family}` on `{r.target}`: mirror/hole {r.mirror_hole_delta:.4f}, worst {r.worst_delta:.4f}, move {r.mean_abs_move:.4f}.")
    lines.extend(
        [
            "",
            "## Next Experiment Queue",
            "",
            "1. Build tomorrow's probes as target-isolated files: S1-only, Q3-only, S1+Q3, and S1+Q3 with S2 capped.",
            "2. If a feature family appears above, train only that family for the listed target and only on inside/future or small-gap rows.",
            "3. Do not extrapolate `public_axis_step2/step3`; validation already says it worsens S2/Q3 movement.",
        ]
    )
    report = "\n".join(lines)
    (EXPERIMENT_DIR / "cl_exhaustive_clue_hunt_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
