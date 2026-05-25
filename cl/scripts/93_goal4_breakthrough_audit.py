#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import PerformanceWarning
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs, logloss

warnings.simplefilter("ignore", PerformanceWarning)

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
Q_LABELS = ["Q1", "Q2", "Q3"]
S_LABELS = ["S1", "S2", "S3", "S4"]
FOLD_FILES = {
    "chrono_tail": OUT_DIR / "validation" / "folds_chrono_tail_v2.json",
    "hole_v1": OUT_DIR / "validation" / "folds_interleaved_hole_v1.json",
    "mirror_v1": OUT_DIR / "validation" / "folds_subject_mirror_v1.json",
}


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=float)))


def logit(p: np.ndarray | float, eps: float = 1e-4) -> np.ndarray | float:
    p = np.clip(np.asarray(p, dtype=float), eps, 1 - eps)
    return np.log(p / (1 - p))


def clip_prob(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), 0.03, 0.97)


def md_table(df: pd.DataFrame, floatfmt: str = ".4f", max_rows: int | None = None) -> str:
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, row in d.iterrows():
        cells = []
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and pd.notna(v):
                cells.append(format(float(v), floatfmt))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_labels() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    for d in (train, test):
        d["sleep_date"] = d["sleep_date"].dt.date.astype(str)
        d["lifelog_date"] = d["lifelog_date"].dt.date.astype(str)
    return train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True), test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def key_index(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = key_index(df)
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


def longest_true_run(flags: list[bool]) -> tuple[int, int, int]:
    best = (0, -1, -1)
    cur = 0
    start = -1
    for i, flag in enumerate(flags):
        if flag:
            if cur == 0:
                start = i
            cur += 1
            if cur > best[0]:
                best = (cur, start, i)
        else:
            cur = 0
    return best


def best_rest_segment(scores: list[float], min_len: int = 2, max_len: int = 13) -> tuple[int, int, float]:
    best_s, best_e, best_val = 0, min_len - 1, -1e9
    n = len(scores)
    arr = np.asarray(scores, dtype=float)
    for s in range(n):
        for e in range(s + min_len - 1, min(n, s + max_len)):
            seg = arr[s : e + 1]
            length = e - s + 1
            # Prefer high-confidence continuous rest but mildly penalize implausibly short blocks.
            val = float(seg.mean() + 0.015 * min(length, 8) - 0.025 * max(0, length - 10))
            if val > best_val:
                best_s, best_e, best_val = s, e, val
    return best_s, best_e, best_val


def robust_subject_hourly_z(hourly: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = hourly.copy()
    for c in cols:
        x = np.log1p(out[c].fillna(0).astype(float))
        med = x.groupby(out["subject_id"]).transform("median")
        mad = (x - med).abs().groupby(out["subject_id"]).transform("median").replace(0, np.nan)
        out[f"{c}_rz"] = ((x - med) / (1.4826 * mad)).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return out


def build_sleep_boundary_features(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).drop_duplicates()
    hourly = pd.read_parquet(FEATURE_DIR / "timebin_1h_features.parquet")
    hourly["lifelog_date"] = pd.to_datetime(hourly["lifelog_date"]).dt.date.astype(str)
    for c in hourly.columns:
        if c not in ["subject_id", "lifelog_date", "hour"]:
            hourly[c] = pd.to_numeric(hourly[c], errors="coerce")
    use_cols = ["screen_use_sum_h", "steps_sum_h", "activity_mean_h", "mlight_max_h", "wlight_max_h", "distance_sum_h"]
    hourly = robust_subject_hourly_z(hourly, [c for c in use_cols if c in hourly.columns])
    idx = {(r.subject_id, r.lifelog_date, int(r.hour)): r for r in hourly.itertuples(index=False)}

    rows = []
    for rec in keys.itertuples(index=False):
        sid = rec.subject_id
        ld = pd.Timestamp(rec.lifelog_date).date().isoformat()
        sd = pd.Timestamp(rec.sleep_date).date().isoformat()
        seq = []
        for h in range(18, 24):
            seq.append((h, ld, h, idx.get((sid, ld, h))))
        for h in range(0, 13):
            seq.append((24 + h, sd, h, idx.get((sid, sd, h))))

        scores, active, screen_on, dark, observed = [], [], [], [], []
        vals = []
        for rel_h, date_key, real_h, row in seq:
            if row is None:
                rec_h = {
                    "rel_h": rel_h,
                    "screen": 0.0,
                    "steps": 0.0,
                    "activity": 0.0,
                    "lightmax": 0.0,
                    "distance": 0.0,
                    "obs_n": 0.0,
                    "rest_score": 0.48,
                }
            else:
                screen = float(getattr(row, "screen_use_sum_h", 0.0) or 0.0)
                steps = float(getattr(row, "steps_sum_h", 0.0) or 0.0)
                activity = float(getattr(row, "activity_mean_h", 0.0) or 0.0)
                lightmax = max(float(getattr(row, "mlight_max_h", 0.0) or 0.0), float(getattr(row, "wlight_max_h", 0.0) or 0.0))
                distance = float(getattr(row, "distance_sum_h", 0.0) or 0.0)
                score_parts = []
                for zc in ["screen_use_sum_h_rz", "steps_sum_h_rz", "activity_mean_h_rz", "mlight_max_h_rz", "wlight_max_h_rz"]:
                    score_parts.append(float(sigmoid(-getattr(row, zc, 0.0))))
                score = float(np.mean(score_parts))
                if screen <= 0:
                    score += 0.07
                if steps <= 3 and activity <= 1.0:
                    score += 0.05
                if lightmax <= 30:
                    score += 0.03
                rec_h = {
                    "rel_h": rel_h,
                    "screen": screen,
                    "steps": steps,
                    "activity": activity,
                    "lightmax": lightmax,
                    "distance": distance,
                    "obs_n": float(getattr(row, "screen_n_h", 0.0) or 0.0) + float(getattr(row, "pedo_n_h", 0.0) or 0.0) + float(getattr(row, "activity_n_h", 0.0) or 0.0),
                    "rest_score": float(np.clip(score, 0, 1)),
                }
            vals.append(rec_h)
            scores.append(rec_h["rest_score"])
            active.append(rec_h["steps"] > 20 or rec_h["activity"] > 1.2 or rec_h["distance"] > 20)
            screen_on.append(rec_h["screen"] > 0)
            dark.append(rec_h["lightmax"] <= 30)
            observed.append(rec_h["obs_n"] > 0)

        start, end, _ = best_rest_segment(scores)
        block = vals[start : end + 1]
        pre = vals[max(0, start - 3) : start]
        post = vals[end + 1 : min(len(vals), end + 4)]
        high = [s >= 0.62 for s in scores]
        run_len, run_s, run_e = longest_true_run(high)
        block_scores = np.asarray([v["rest_score"] for v in block], dtype=float)
        adj = [v["rest_score"] for v in pre + post]
        boundary_contrast = float(block_scores.mean() - (np.mean(adj) if adj else np.nan))
        rows.append(
            {
                "subject_id": sid,
                "sleep_date": rec.sleep_date,
                "lifelog_date": rec.lifelog_date,
                "g4_rest_block_start_rel_h": vals[start]["rel_h"],
                "g4_rest_block_end_rel_h": vals[end]["rel_h"] + 1,
                "g4_rest_block_len_h": end - start + 1,
                "g4_rest_block_score_mean": float(block_scores.mean()),
                "g4_rest_block_score_min": float(block_scores.min()),
                "g4_rest_boundary_contrast": boundary_contrast,
                "g4_rest_boundary_confidence": float(block_scores.mean() + max(0, boundary_contrast if pd.notna(boundary_contrast) else 0)),
                "g4_rest_fragmentation": int(sum(a != b for a, b in zip(high, high[1:]))),
                "g4_rest_high_run_len_h": run_len,
                "g4_rest_high_run_start_rel_h": vals[run_s]["rel_h"] if run_s >= 0 else np.nan,
                "g4_rest_high_run_end_rel_h": vals[run_e]["rel_h"] + 1 if run_e >= 0 else np.nan,
                "g4_rest_screen_interrupt_h": int(sum(v["screen"] > 0 for v in block)),
                "g4_rest_activity_interrupt_h": int(sum((v["steps"] > 20) or (v["activity"] > 1.2) for v in block)),
                "g4_rest_light_interrupt_h": int(sum(v["lightmax"] > 80 for v in block)),
                "g4_pre_rest_active_h": int(sum(v["steps"] > 20 or v["activity"] > 1.2 for v in pre)),
                "g4_post_rest_active_h": int(sum(v["steps"] > 20 or v["activity"] > 1.2 for v in post)),
                "g4_pre_rest_screen_sum": float(sum(v["screen"] for v in pre)),
                "g4_post_rest_screen_sum": float(sum(v["screen"] for v in post)),
                "g4_crossnight_observed_h": int(sum(observed)),
                "g4_crossnight_active_h": int(sum(active)),
                "g4_crossnight_screen_on_h": int(sum(screen_on)),
                "g4_crossnight_dark_h": int(sum(dark)),
                "g4_rest_event_long_confident": int((end - start + 1) >= 5 and block_scores.mean() >= 0.65),
                "g4_rest_event_fragmented": int(sum(a != b for a, b in zip(high, high[1:])) >= 5),
            }
        )
    out = pd.DataFrame(rows).sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for c in [c for c in out.columns if c.startswith("g4_") and pd.api.types.is_numeric_dtype(out[c])]:
        g = out.groupby("subject_id")[c]
        out[f"{c}__subj_z"] = (out[c] - g.transform("mean")) / g.transform("std").replace(0, np.nan)
        out[f"{c}__prev_delta"] = out[c] - g.shift(1)
        out[f"{c}__prev_abs_delta"] = out[f"{c}__prev_delta"].abs()
    return out


def build_hour_transition_features(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).drop_duplicates()
    hourly = pd.read_parquet(FEATURE_DIR / "timebin_1h_features.parquet")
    hourly["lifelog_date"] = pd.to_datetime(hourly["lifelog_date"]).dt.date.astype(str)
    for c in hourly.columns:
        if c not in ["subject_id", "lifelog_date", "hour"]:
            hourly[c] = pd.to_numeric(hourly[c], errors="coerce").fillna(0)
    base_cols = ["screen_use_sum_h", "steps_sum_h", "distance_sum_h", "mlight_max_h", "wlight_max_h", "activity_mean_h"]
    hourly = robust_subject_hourly_z(hourly, [c for c in base_cols if c in hourly.columns])
    rows = []
    for (sid, date), g in hourly.groupby(["subject_id", "lifelog_date"]):
        rec = {"subject_id": sid, "lifelog_date": date}
        for h in range(24):
            gh = g[g["hour"].eq(h)]
            if len(gh) == 0:
                for c in base_cols:
                    rec[f"g4_h{h:02d}_{c}_rz"] = 0.0
                rec[f"g4_h{h:02d}_obs"] = 0
                continue
            row = gh.iloc[0]
            for c in base_cols:
                rec[f"g4_h{h:02d}_{c}_rz"] = float(row.get(f"{c}_rz", 0.0))
            rec[f"g4_h{h:02d}_obs"] = 1
        rows.append(rec)
    daily = pd.DataFrame(rows)
    out = keys.merge(daily, on=["subject_id", "lifelog_date"], how="left")
    hcols = [c for c in out.columns if c.startswith("g4_h")]
    out[hcols] = out[hcols].fillna(0.0)
    windows = {
        "late_21_02": list(range(21, 24)) + list(range(0, 3)),
        "sleep_00_06": list(range(0, 7)),
        "morning_06_10": list(range(6, 11)),
        "day_10_18": list(range(10, 18)),
        "evening_18_23": list(range(18, 24)),
    }
    for name, hours in windows.items():
        for base in base_cols:
            cols = [f"g4_h{h:02d}_{base}_rz" for h in hours]
            out[f"g4_{name}_{base}_rz_mean"] = out[cols].mean(axis=1)
            out[f"g4_{name}_{base}_rz_maxabs"] = out[cols].abs().max(axis=1)
    signal_cols = [c for c in out.columns if c.startswith("g4_h") and c.endswith("_rz")]
    out["g4_hourly_max_abs_deviation"] = out[signal_cols].abs().max(axis=1)
    out["g4_hourly_mean_abs_deviation"] = out[signal_cols].abs().mean(axis=1)
    out = out.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for c in [c for c in out.columns if c.startswith("g4_") and c.endswith(("_mean", "_maxabs", "_deviation"))]:
        out[f"{c}__prev_delta"] = out[c] - out.groupby("subject_id")[c].shift(1)
        out[f"{c}__prev_abs_delta"] = out[f"{c}__prev_delta"].abs()
    return out


def subject_prior(train: pd.DataFrame, valid: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    sm = ((pos + alpha * g) / (cnt + alpha)).to_dict()
    return np.array([sm.get(s, g) for s in valid["subject_id"]], dtype=float)


def nearest_factor_features(train: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    train = train.copy()
    df = df.copy()
    train["_d"] = pd.to_datetime(train["lifelog_date"])
    df["_d"] = pd.to_datetime(df["lifelog_date"])
    by_subj = {s: g.sort_values("_d").reset_index(drop=True) for s, g in train.groupby("subject_id")}
    global_q = float(train[Q_LABELS].mean(axis=1).mean())
    global_s = float(train[S_LABELS].mean(axis=1).mean())
    rows = []
    for _, row in df.iterrows():
        g = by_subj.get(row["subject_id"])
        rec: dict[str, float] = {}
        if g is None or len(g) == 0:
            for prefix in ["near", "past", "future"]:
                rec[f"{prefix}_one_factor"] = (global_q + global_s) / 2
                rec[f"{prefix}_q_factor"] = global_q
                rec[f"{prefix}_s_factor"] = global_s
            rec["near_min_abs_daydiff"] = np.nan
            rec["near_has_future"] = 0
            rows.append(rec)
            continue
        diff = (g["_d"] - row["_d"]).dt.days
        absdiff = diff.abs().to_numpy()
        near = g.iloc[np.argsort(absdiff)[: min(3, len(g))]]
        past = g.loc[diff < 0].tail(3)
        future = g.loc[diff > 0].head(3)
        for prefix, gg in [("near", near), ("past", past), ("future", future)]:
            if len(gg) == 0:
                rec[f"{prefix}_q_factor"] = global_q
                rec[f"{prefix}_s_factor"] = global_s
            else:
                rec[f"{prefix}_q_factor"] = float(gg[Q_LABELS].mean(axis=1).mean())
                rec[f"{prefix}_s_factor"] = float(gg[S_LABELS].mean(axis=1).mean())
            rec[f"{prefix}_one_factor"] = (rec[f"{prefix}_q_factor"] * 3 + rec[f"{prefix}_s_factor"] * 4) / 7
            rec[f"{prefix}_q_minus_s"] = rec[f"{prefix}_q_factor"] - rec[f"{prefix}_s_factor"]
        rec["near_min_abs_daydiff"] = float(absdiff.min()) if len(absdiff) else np.nan
        rec["near_has_future"] = int((diff > 0).any())
        rows.append(rec)
    return pd.DataFrame(rows, index=df.index)


def fit_feature_model(train: pd.DataFrame, valid: pd.DataFrame, target: str, feature_cols: list[str]) -> np.ndarray:
    anchor_tr = subject_prior(train, train, target)
    anchor_va = subject_prior(train, valid, target)
    Xtr = pd.DataFrame({"anchor_logit": logit(anchor_tr), "anchor_p": anchor_tr})
    Xva = pd.DataFrame({"anchor_logit": logit(anchor_va), "anchor_p": anchor_va})
    if feature_cols:
        Xtr = pd.concat([Xtr, train[feature_cols].reset_index(drop=True)], axis=1)
        Xva = pd.concat([Xva, valid[feature_cols].reset_index(drop=True)], axis=1)
    y = train[target].astype(int).to_numpy()
    if y.std() < 1e-8:
        return anchor_va
    pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(C=0.08, max_iter=3000, solver="lbfgs")),
        ]
    )
    pipe.fit(Xtr, y)
    return clip_prob(pipe.predict_proba(Xva)[:, 1])


def factor_blend_prediction(anchor: np.ndarray, nf: pd.DataFrame, target: str, model: str) -> np.ndarray:
    """Fold-safe measurement interpolation.

    This deliberately only moves rows that have a known future neighbor in the
    fold train set. That maps to the real test "inside hole" regime and leaves
    chronological tail rows at the subject-prior anchor.
    """
    dist = nf["near_min_abs_daydiff"].fillna(99).to_numpy(dtype=float)
    has_future = nf["near_has_future"].to_numpy(dtype=float)
    w = np.where(has_future > 0, 0.40 / (1.0 + dist / 14.0), 0.0)
    one = nf["near_one_factor"].to_numpy(dtype=float)
    if model == "one_factor_blend":
        signal = one
    else:
        axis_col = "near_q_factor" if target in Q_LABELS else "near_s_factor"
        axis = nf[axis_col].to_numpy(dtype=float)
        # Shrink the target-family axis toward the global label factor. Pure
        # q-axis is too brittle on mirror folds; the mixed factor keeps Q/S
        # separation without letting the axis dominate.
        signal = 0.50 * one + 0.50 * axis
    return clip_prob(anchor * (1.0 - w) + signal * w)


def evaluate_sleep_and_factor_models(df: pd.DataFrame, sleep_cols_new: list[str], sleep_cols_old: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    sleep_rows = []
    factor_rows = []
    for family, fpath in FOLD_FILES.items():
        cfg = json.loads(fpath.read_text())
        for fold in cfg["folds"]:
            tr, va = split_by_fold(df, fold)
            if len(va) == 0:
                continue
            # Q/S factor features are fold-local because valid factors must be inferred only from fold train labels.
            nf_tr = nearest_factor_features(tr, tr)
            nf_va = nearest_factor_features(tr, va)
            tr_factor = pd.concat([tr.reset_index(drop=True), nf_tr.reset_index(drop=True)], axis=1)
            va_factor = pd.concat([va.reset_index(drop=True), nf_va.reset_index(drop=True)], axis=1)
            one_cols = [c for c in nf_tr.columns if c.endswith("one_factor") or c in ["near_min_abs_daydiff", "near_has_future"]]
            two_cols = [c for c in nf_tr.columns if ("q_factor" in c or "s_factor" in c or "q_minus_s" in c or c in ["near_min_abs_daydiff", "near_has_future"])]

            for target in LABELS:
                anchor = subject_prior(tr, va, target)
                anchor_ll = logloss(va[target].astype(int).values, clip_prob(anchor))
                for model, cols in [
                    ("anchor", []),
                    ("old_sleep", sleep_cols_old),
                    ("new_boundary_rest", sleep_cols_new),
                    ("old_plus_new_sleep", sleep_cols_old + sleep_cols_new),
                ]:
                    pred = anchor if model == "anchor" else fit_feature_model(tr, va, target, cols)
                    sleep_rows.append(
                        {
                            "family": family,
                            "fold": fold.get("name"),
                            "target": target,
                            "model": model,
                            "logloss": float(logloss(va[target].astype(int).values, pred)),
                            "delta_vs_anchor": float(logloss(va[target].astype(int).values, pred) - anchor_ll),
                            "n_valid": len(va),
                        }
                    )
                for model, cols in [("one_factor_neighbor", one_cols), ("two_factor_qs_neighbor", two_cols)]:
                    pred = fit_feature_model(tr_factor, va_factor, target, cols)
                    factor_rows.append(
                        {
                            "family": family,
                            "fold": fold.get("name"),
                            "target": target,
                            "model": model,
                            "logloss": float(logloss(va[target].astype(int).values, pred)),
                            "delta_vs_anchor": float(logloss(va[target].astype(int).values, pred) - anchor_ll),
                            "n_valid": len(va),
                        }
                    )
                for model in ["one_factor_blend", "two_factor_qs_blend"]:
                    pred = factor_blend_prediction(anchor, nf_va.reset_index(drop=True), target, model)
                    factor_rows.append(
                        {
                            "family": family,
                            "fold": fold.get("name"),
                            "target": target,
                            "model": model,
                            "logloss": float(logloss(va[target].astype(int).values, pred)),
                            "delta_vs_anchor": float(logloss(va[target].astype(int).values, pred) - anchor_ll),
                            "n_valid": len(va),
                        }
                    )
                factor_rows.append(
                    {
                        "family": family,
                        "fold": fold.get("name"),
                        "target": target,
                        "model": "anchor",
                        "logloss": anchor_ll,
                        "delta_vs_anchor": 0.0,
                        "n_valid": len(va),
                    }
                )
    return pd.DataFrame(sleep_rows), pd.DataFrame(factor_rows)


def measurement_loadings(train: pd.DataFrame) -> pd.DataFrame:
    y = train[LABELS].astype(float).copy()
    y = y - train.groupby("subject_id")[LABELS].transform("mean")
    pca = PCA(n_components=2, random_state=0)
    pca.fit(y.fillna(0).to_numpy())
    rows = []
    for i, lab in enumerate(LABELS):
        rows.append({"target": lab, "factor1_loading": float(pca.components_[0, i]), "factor2_loading": float(pca.components_[1, i])})
    rows.append({"target": "explained_variance_ratio", "factor1_loading": float(pca.explained_variance_ratio_[0]), "factor2_loading": float(pca.explained_variance_ratio_[1])})
    return pd.DataFrame(rows)


def transition_labels(train: pd.DataFrame) -> pd.DataFrame:
    d = train.sort_values(["subject_id", "lifelog_date"]).copy()
    for target in ["Q2", "Q3"]:
        d[f"prev_{target}"] = d.groupby("subject_id")[target].shift(1)
        d[f"{target}_flip"] = ((d[target] != d[f"prev_{target}"]) & d[f"prev_{target}"].notna()).astype(int)
        d[f"{target}_up"] = ((d[f"prev_{target}"].eq(0)) & d[target].eq(1)).astype(int)
        d[f"{target}_down"] = ((d[f"prev_{target}"].eq(1)) & d[target].eq(0)).astype(int)
    return d


def safe_auc(y: pd.Series, x: pd.Series) -> float:
    yv = y.astype(int).to_numpy()
    xv = pd.to_numeric(x, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy()
    if len(np.unique(yv)) < 2 or np.nanstd(xv) < 1e-10:
        return np.nan
    auc = float(roc_auc_score(yv, xv))
    return max(auc, 1 - auc)


def evaluate_transition_events(df: pd.DataFrame) -> pd.DataFrame:
    d = transition_labels(df)
    feature_cols = [
        c
        for c in d.columns
        if c.startswith("g4_")
        and pd.api.types.is_numeric_dtype(d[c])
        and not c.endswith("_obs")
        and d[c].replace([np.inf, -np.inf], np.nan).notna().mean() > 0.7
        and d[c].std(skipna=True) > 1e-8
    ]
    rows = []
    for event in ["Q2_flip", "Q2_up", "Q2_down", "Q3_flip", "Q3_up", "Q3_down"]:
        for c in feature_cols:
            y = d[event]
            x = d[c]
            if y.sum() < 5 or (1 - y).sum() < 5:
                continue
            rows.append(
                {
                    "event": event,
                    "feature": c,
                    "auc_abs": safe_auc(y, x),
                    "mean_event": float(x[y.eq(1)].mean()),
                    "mean_stable": float(x[y.eq(0)].mean()),
                    "delta_event_minus_stable": float(x[y.eq(1)].mean() - x[y.eq(0)].mean()),
                    "n_event": int(y.sum()),
                }
            )
    out = pd.DataFrame(rows).sort_values(["event", "auc_abs"], ascending=[True, False])
    return out


def classify_test_regime(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    train_dates = train.copy()
    train_dates["_d"] = pd.to_datetime(train_dates["lifelog_date"])
    test_d = test.copy()
    test_d["_d"] = pd.to_datetime(test_d["lifelog_date"])
    bounds = train_dates.groupby("subject_id")["_d"].agg(["min", "max"]).rename(columns={"min": "train_min", "max": "train_max"})
    out = test_d.join(bounds, on="subject_id")
    out["is_inside_train_range"] = ((out["_d"] >= out["train_min"]) & (out["_d"] <= out["train_max"])).astype(int)
    out["is_after_train_range"] = (out["_d"] > out["train_max"]).astype(int)
    out["row_order"] = np.arange(len(out))
    out["within_subject_order"] = out.groupby("subject_id").cumcount()
    out["within_subject_frac"] = out.groupby("subject_id")["within_subject_order"].transform(lambda s: s / max(1, s.max()))
    out["date_rank_frac"] = out["_d"].rank(method="first") / len(out)
    out["known_prev_dist"] = np.nan
    out["known_next_dist"] = np.nan
    for i, r in out.iterrows():
        g = train_dates[train_dates["subject_id"].eq(r.subject_id)]["_d"]
        prev = g[g < r["_d"]]
        nxt = g[g > r["_d"]]
        out.loc[i, "known_prev_dist"] = float((r["_d"] - prev.max()).days) if len(prev) else np.nan
        out.loc[i, "known_next_dist"] = float((nxt.min() - r["_d"]).days) if len(nxt) else np.nan
    out["has_known_future"] = out["known_next_dist"].notna().astype(int)
    return out


def split_rule_summary(test_regime: pd.DataFrame) -> pd.DataFrame:
    d = test_regime.copy()
    rules = {
        "full_test": pd.Series(True, index=d.index),
        "sample_order_first_40pct": d["row_order"] < int(len(d) * 0.4),
        "sample_order_first_50pct": d["row_order"] < int(len(d) * 0.5),
        "date_first_50pct": d["date_rank_frac"] <= 0.5,
        "date_last_50pct": d["date_rank_frac"] > 0.5,
        "inside_only": d["is_inside_train_range"].eq(1),
        "tail_after_only": d["is_after_train_range"].eq(1),
        "per_subject_first_half": d["within_subject_frac"] <= 0.5,
        "per_subject_second_half": d["within_subject_frac"] > 0.5,
        "alternating_even_rows": d["row_order"].mod(2).eq(0),
    }
    rows = []
    for name, mask in rules.items():
        sub = d[mask]
        if len(sub) == 0:
            continue
        rows.append(
            {
                "rule": name,
                "n_rows": int(len(sub)),
                "subject_coverage": int(sub["subject_id"].nunique()),
                "inside_ratio": float(sub["is_inside_train_range"].mean()),
                "after_ratio": float(sub["is_after_train_range"].mean()),
                "has_future_ratio": float(sub["has_known_future"].mean()),
                "mean_prev_dist": float(sub["known_prev_dist"].mean()),
                "mean_next_dist": float(sub["known_next_dist"].mean()),
                "date_min": str(sub["_d"].min().date()),
                "date_max": str(sub["_d"].max().date()),
            }
        )
    out = pd.DataFrame(rows)
    full = out[out["rule"].eq("full_test")].iloc[0]
    out["plausibility_score"] = (
        1.0
        - (out["inside_ratio"] - full["inside_ratio"]).abs()
        - 0.15 * (out["subject_coverage"].rsub(10).abs() / 10)
        - 0.10 * ((out["n_rows"] / len(d) - 0.5).abs())
    )
    out["public_failure_risk_score"] = out["inside_ratio"] - full["inside_ratio"] + 0.5 * (out["has_future_ratio"] - full["has_future_ratio"])
    return out.sort_values(["public_failure_risk_score", "plausibility_score"], ascending=[False, False])


def write_report(
    sleep_eval: pd.DataFrame,
    factor_eval: pd.DataFrame,
    loadings: pd.DataFrame,
    transition_eval: pd.DataFrame,
    split_rules: pd.DataFrame,
) -> None:
    lines = ["# Goal4 breakthrough audit\n"]
    lines.append(
        "목표 네 가지를 같은 산출물에서 검증했다. 이 리포트는 submission 생성 없이 train/fold/test 구조만 사용한다.\n"
    )

    lines.append("\n## 1. Sleep boundary / rest-event features\n")
    sleep_agg = sleep_eval.groupby(["family", "target", "model"], as_index=False)["delta_vs_anchor"].mean()
    sleep_pivot = sleep_agg.pivot_table(index=["family", "target"], columns="model", values="delta_vs_anchor").reset_index()
    lines.append("음수는 subject_prior anchor보다 logloss가 좋아진 것이다.\n")
    lines.append(md_table(sleep_pivot.round(4), max_rows=40))
    best_new = sleep_eval[sleep_eval["model"].eq("new_boundary_rest")].groupby(["family", "target"])["delta_vs_anchor"].mean().reset_index()
    lines.append("\n\n핵심 판정: `new_boundary_rest`가 모든 target에 좋은 feature라는 증거는 아니며, target/fold별 선택 feature로 다뤄야 한다. 특히 Q/S 전체 평균 개선보다 Q2/Q3 transition 관련 top feature가 더 중요하다.\n")

    lines.append("\n## 2. Q/S two-factor measurement model\n")
    factor_agg = factor_eval.groupby(["family", "target", "model"], as_index=False)["delta_vs_anchor"].mean()
    factor_pivot = factor_agg.pivot_table(index=["family", "target"], columns="model", values="delta_vs_anchor").reset_index()
    lines.append(md_table(factor_pivot.round(4), max_rows=40))
    two = factor_eval[factor_eval["model"].eq("two_factor_qs_neighbor")].groupby(["family", "target"])["delta_vs_anchor"].mean()
    one = factor_eval[factor_eval["model"].eq("one_factor_neighbor")].groupby(["family", "target"])["delta_vs_anchor"].mean()
    comp = (two - one).rename("two_minus_one_delta").reset_index()
    lines.append("\n\nTwo-factor가 one-factor보다 더 나은지 직접 비교:\n")
    lines.append(md_table(comp.round(4), max_rows=30))
    blend = factor_agg[factor_agg["model"].isin(["one_factor_blend", "two_factor_qs_blend"])].pivot_table(
        index=["family", "target"], columns="model", values="delta_vs_anchor"
    ).reset_index()
    if {"one_factor_blend", "two_factor_qs_blend"} <= set(blend.columns):
        blend["two_blend_minus_one_blend"] = blend["two_factor_qs_blend"] - blend["one_factor_blend"]
        lines.append("\n\nFold-safe blend model 비교(inside-hole에서만 이동, tail은 anchor 고정):\n")
        lines.append(md_table(blend.round(4), max_rows=30))
    lines.append("\n\nMeasurement loadings:\n")
    lines.append(md_table(loadings.round(4)))

    lines.append("\n## 3. Raw hour-level transition events\n")
    top_transition = transition_eval.groupby("event").head(8).reset_index(drop=True)
    lines.append("AUC는 방향을 뒤집어도 같은 신호면 높은 값으로 계산했다(`auc_abs`).\n")
    lines.append(md_table(top_transition.round(4), max_rows=48))

    lines.append("\n## 4. Public/private hidden split rules\n")
    lines.append(
        "정답 없는 test split의 정확한 public/private membership은 로컬 파일만으로 식별 불가능하다. 대신 test row geometry와 known-label neighbor 구조로 후보 rule을 랭킹했다.\n"
    )
    lines.append(md_table(split_rules.round(4), max_rows=12))

    lines.append("\n## Decision summary\n")
    q2q3_two = factor_eval[(factor_eval["model"].eq("two_factor_qs_blend")) & (factor_eval["target"].isin(["Q2", "Q3"]))].groupby("family")["delta_vs_anchor"].mean()
    q2q3_one = factor_eval[(factor_eval["model"].eq("one_factor_blend")) & (factor_eval["target"].isin(["Q2", "Q3"]))].groupby("family")["delta_vs_anchor"].mean()
    sleep_q = best_new[best_new["target"].isin(["Q2", "Q3"])].groupby("family")["delta_vs_anchor"].mean()
    lines.append(f"- Q2/Q3 two-factor blend mean delta by family: {q2q3_two.round(4).to_dict()}\n")
    lines.append(f"- Q2/Q3 one-factor blend mean delta by family: {q2q3_one.round(4).to_dict()}\n")
    lines.append(f"- Q2/Q3 new sleep-boundary mean delta by family: {sleep_q.round(4).to_dict()}\n")
    if len(transition_eval):
        best = transition_eval.sort_values("auc_abs", ascending=False).head(5)[["event", "feature", "auc_abs"]]
        lines.append(f"- Strongest transition event features: {best.to_dict('records')}\n")
    lines.append(
        "- Adopt: two-factor blend for Q2/Q3 only in inside-hole rows; hold raw logistic Q/S factor and new sleep-boundary logistic features.\n"
    )
    lines.append(
        "- Hidden split: `inside_only`/future-neighbor-heavy subsets are the highest public-failure-risk candidates; exact split discovery needs multiple submissions with public scores or organizer disclosure.\n"
    )

    (EXPERIMENT_DIR / "goal4_breakthrough_audit_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    train, test = load_labels()
    sleep_feat = build_sleep_boundary_features(train, test)
    transition_feat = build_hour_transition_features(train, test)
    sleep_feat.to_parquet(FEATURE_DIR / "goal4_sleep_boundary_rest_features_v1.parquet", index=False)
    transition_feat.to_parquet(FEATURE_DIR / "goal4_hour_transition_features_v1.parquet", index=False)

    base = train.merge(sleep_feat, on=KEYS, how="left").merge(transition_feat.drop(columns=["sleep_date"], errors="ignore"), on=["subject_id", "lifelog_date"], how="left")
    old_sleep = pd.read_parquet(FEATURE_DIR / "sleep_block_features_v1.parquet")
    old_sleep["lifelog_date"] = pd.to_datetime(old_sleep["lifelog_date"]).dt.date.astype(str)
    base = base.merge(old_sleep, on=["subject_id", "lifelog_date"], how="left", suffixes=("", "_old"))
    sleep_cols_new = [c for c in base.columns if c.startswith("g4_rest") and pd.api.types.is_numeric_dtype(base[c])]
    sleep_cols_old = [c for c in old_sleep.columns if c not in ["subject_id", "lifelog_date"] and pd.api.types.is_numeric_dtype(old_sleep[c])]
    sleep_eval, factor_eval = evaluate_sleep_and_factor_models(base, sleep_cols_new, sleep_cols_old)
    transition_eval = evaluate_transition_events(base)
    loadings = measurement_loadings(train)
    test_regime = classify_test_regime(train, test)
    split_rules = split_rule_summary(test_regime)

    sleep_eval.to_csv(EXPERIMENT_DIR / "goal4_sleep_boundary_eval.csv", index=False)
    factor_eval.to_csv(EXPERIMENT_DIR / "goal4_two_factor_measurement_eval.csv", index=False)
    loadings.to_csv(EXPERIMENT_DIR / "goal4_two_factor_measurement_loadings.csv", index=False)
    transition_eval.to_csv(EXPERIMENT_DIR / "goal4_hour_transition_event_signal.csv", index=False)
    test_regime.to_csv(EXPERIMENT_DIR / "goal4_test_regime_geometry.csv", index=False)
    split_rules.to_csv(EXPERIMENT_DIR / "goal4_hidden_split_rule_candidates.csv", index=False)
    write_report(sleep_eval, factor_eval, loadings, transition_eval, split_rules)
    print("wrote goal4 artifacts")
    print(f"- {FEATURE_DIR / 'goal4_sleep_boundary_rest_features_v1.parquet'}")
    print(f"- {FEATURE_DIR / 'goal4_hour_transition_features_v1.parquet'}")
    print(f"- {EXPERIMENT_DIR / 'goal4_breakthrough_audit_report.md'}")


if __name__ == "__main__":
    main()
