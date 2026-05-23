#!/usr/bin/env python3
"""Deeper no-submit data-science diagnostics.

Adds three deeper analyses beyond label grammar:
1) latent-state transition event study over engineered feature families,
2) raw-modality daily aggregation and state/target separability with and without
   subject normalization,
3) gap/direction-aware Q2/Q3 interpolation grammar.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "ch2025_data_items"
EXP = ROOT / "experiments"
FEAT = ROOT / "features"
SCRIPTS = ROOT / "scripts"
EXP.mkdir(exist_ok=True)
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]

spec = importlib.util.spec_from_file_location("big67", SCRIPTS / "67_big_swing_all_experiments.py")
big67 = importlib.util.module_from_spec(spec)
sys.modules["big67"] = big67
spec.loader.exec_module(big67)


def family_of_col(c: str) -> str:
    c = c.lower()
    rules = [
        ("ssl", ["ssl", "dino", "ae_", "cluster", "proto"]),
        ("sleep_episode", ["sleep", "psw", "s4x", "q1qual", "q2lr", "crossnight", "cn_"]),
        ("screen_phone", ["screen", "usage", "app_"]),
        ("activity_steps", ["step", "pedo", "activity", "distance", "speed", "calor"]),
        ("heart_light", ["hr_", "heart", "light"]),
        ("location_context", ["gps", "wifi", "ble", "amb", "place", "rssi", "lat", "lon"]),
        ("routine_axes", ["routine", "axis_", "human_"]),
        ("hourly_shape", ["h00", "h01", "h02", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10", "h11", "h12", "h13", "h14", "h15", "h16", "h17", "h18", "h19", "h20", "h21", "h22", "h23", "_h"]),
    ]
    for name, toks in rules:
        if any(t in c for t in toks):
            return name
    return "other_numeric"


def safe_logloss(y, p):
    return log_loss(np.asarray(y, int), np.clip(np.asarray(p, float), 0.02, 0.98), labels=[0, 1])


def feature_cols(df, max_cols=1400):
    return big67.numeric_cols(
        df,
        contains=("sleep", "quiet", "screen", "steps", "activity", "hr_", "heart", "gps_", "app_", "wifi_", "ble_", "amb_", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "ssl", "dino", "ae_", "cluster", "routine", "light", "pedo"),
        max_cols=max_cols,
    )


def make_masks(train, sample, seeds=range(4)):
    masks = [(n, m, f, "testpattern") for n, m, f in big67.make_testpattern_masks(train, sample, seeds=seeds)]
    # interleaved-rank masks copied intentionally from prior diagnostics
    n = len(train)
    for seed in seeds:
        rng = np.random.default_rng(1900 + seed)
        mask = np.zeros(n, bool)
        for sid, sub in train.groupby("subject_id"):
            sub = sub.sort_values("sleep_date")
            tst = sample[sample.subject_id == sid].sort_values("sleep_date")
            all_dates = pd.concat([sub[["sleep_date"]].assign(kind="train"), tst[["sleep_date"]].assign(kind="test")]).sort_values("sleep_date").reset_index(drop=True)
            test_fracs = all_dates.index[all_dates.kind.eq("test")].to_numpy() / max(1, len(all_dates) - 1)
            ranks = np.linspace(0, 1, len(sub))
            prob = np.ones(len(sub)) * 0.05
            for frac in test_fracs:
                prob += np.exp(-0.5 * ((ranks - frac) / 0.10) ** 2)
            prob = prob / prob.sum()
            size = min(len(sub) - 2, max(3, len(tst)))
            chosen = rng.choice(sub.index.to_numpy(), size=size, replace=False, p=prob)
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f"deep_interleaved_rank{seed}", mask, True, "interleaved_rank"))
    return masks


def standardize_within_subject(df, cols):
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    g = out.groupby("subject_id")[cols]
    mu = g.transform("mean")
    sd = g.transform("std").replace(0, np.nan)
    out[cols] = (out[cols] - mu) / sd
    return out


def event_study_engineered(train, cols, top_per_family=50):
    # Use within-column z scores to compare transition-day feature changes.
    use = []
    byfam = defaultdict(list)
    for c in cols:
        byfam[family_of_col(c)].append(c)
    for fam, cs in byfam.items():
        use += cs[:top_per_family]
    use = list(dict.fromkeys(use))
    X = train[use].apply(pd.to_numeric, errors="coerce")
    X = pd.DataFrame(SimpleImputer(strategy="median").fit_transform(X), columns=use)
    Xz = pd.DataFrame(StandardScaler().fit_transform(X), columns=use)
    tmp = train[IDS + ["latent_state"]].reset_index(drop=True).copy()
    rows = []
    for sid, sub in tmp.sort_values(["subject_id", "sleep_date"]).groupby("subject_id"):
        idx = sub.index.to_numpy()
        st = sub.latent_state.to_numpy(int)
        for pos in range(1, len(idx)):
            if st[pos] == st[pos - 1]:
                continue
            before_i, after_i = idx[pos - 1], idx[pos]
            delta = Xz.loc[after_i, use].to_numpy(float) - Xz.loc[before_i, use].to_numpy(float)
            trans = f"{st[pos-1]}->{st[pos]}"
            for c, d in zip(use, delta):
                rows.append({"subject_id": sid, "transition": trans, "from_state": int(st[pos-1]), "to_state": int(st[pos]), "feature": c, "family": family_of_col(c), "delta_z": float(d)})
    raw = pd.DataFrame(rows)
    raw.to_csv(EXP / "deep_state_transition_feature_deltas_raw.csv", index=False)
    if len(raw) == 0:
        return raw, pd.DataFrame(), pd.DataFrame()
    fam = raw.groupby(["transition", "family"]).agg(
        n_events=("subject_id", "nunique"),
        n_feature_deltas=("delta_z", "count"),
        mean_delta_z=("delta_z", "mean"),
        mean_abs_delta_z=("delta_z", lambda s: float(np.mean(np.abs(s)))),
    ).reset_index().sort_values(["transition", "mean_abs_delta_z"], ascending=[True, False])
    feat = raw.groupby(["transition", "feature", "family"]).agg(
        mean_delta_z=("delta_z", "mean"),
        mean_abs_delta_z=("delta_z", lambda s: float(np.mean(np.abs(s)))),
        count=("delta_z", "count"),
    ).reset_index().sort_values(["transition", "mean_abs_delta_z"], ascending=[True, False])
    fam.to_csv(EXP / "deep_state_transition_family_event_study.csv", index=False)
    feat.groupby("transition").head(30).to_csv(EXP / "deep_state_transition_top_features.csv", index=False)
    return raw, fam, feat


def daily_agg_numeric(path, value_cols, prefix):
    p = RAW / path
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_parquet(p)
    df["lifelog_date"] = pd.to_datetime(df["timestamp"]).dt.normalize()
    out = df.groupby(["subject_id", "lifelog_date"]).size().rename(f"{prefix}_n").reset_index()
    for c in value_cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        tmp = df.assign(_v=s).groupby(["subject_id", "lifelog_date"])["_v"].agg(["mean", "std", "min", "max", "sum"]).reset_index()
        tmp = tmp.rename(columns={k: f"{prefix}_{c}_{k}" for k in ["mean", "std", "min", "max", "sum"]})
        out = out.merge(tmp, on=["subject_id", "lifelog_date"], how="outer")
    return out


def daily_agg_raw_modalities():
    parts = []
    specs = [
        ("ch2025_mACStatus.parquet", ["m_charging"], "raw_ac"),
        ("ch2025_mScreenStatus.parquet", ["m_screen_use"], "raw_screen"),
        ("ch2025_mActivity.parquet", ["m_activity"], "raw_act"),
        ("ch2025_wPedo.parquet", ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"], "raw_pedo"),
        ("ch2025_mLight.parquet", ["m_light"], "raw_mlight"),
        ("ch2025_wLight.parquet", ["w_light"], "raw_wlight"),
    ]
    for spec in specs:
        part = daily_agg_numeric(*spec)
        if len(part):
            parts.append(part)

    # Heart-rate list column.
    p = RAW / "ch2025_wHr.parquet"
    if p.exists():
        df = pd.read_parquet(p)
        df["lifelog_date"] = pd.to_datetime(df["timestamp"]).dt.normalize()
        def arr_mean(x):
            try:
                return float(np.mean(x)) if len(x) else np.nan
            except Exception:
                return np.nan
        df["hr_row_mean"] = df["heart_rate"].map(arr_mean)
        part = df.groupby(["subject_id", "lifelog_date"])["hr_row_mean"].agg(["count", "mean", "std", "min", "max"]).reset_index()
        part = part.rename(columns={"count": "raw_hr_n", "mean": "raw_hr_mean", "std": "raw_hr_std", "min": "raw_hr_min", "max": "raw_hr_max"})
        parts.append(part)

    # Nested/location/context modalities: summarize counts and RSSI/speed when easy.
    nested_specs = [
        ("ch2025_mWifi.parquet", "m_wifi", "raw_wifi"),
        ("ch2025_mBle.parquet", "m_ble", "raw_ble"),
        ("ch2025_mUsageStats.parquet", "m_usage_stats", "raw_usage"),
        ("ch2025_mGps.parquet", "m_gps", "raw_gps"),
        ("ch2025_mAmbience.parquet", "m_ambience", "raw_amb"),
    ]
    for fname, col, pref in nested_specs:
        p = RAW / fname
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        df["lifelog_date"] = pd.to_datetime(df["timestamp"]).dt.normalize()
        def count_obj(x):
            try: return len(x) if x is not None else 0
            except Exception: return 0
        df[f"{pref}_items"] = df[col].map(count_obj)
        # Extract simple scalar means from nested dict/list objects.
        if pref in ["raw_wifi", "raw_ble"]:
            def mean_rssi(x):
                try:
                    vals = [float(d.get("rssi", np.nan)) for d in x]
                    vals = [v for v in vals if np.isfinite(v)]
                    return float(np.mean(vals)) if vals else np.nan
                except Exception:
                    return np.nan
            df[f"{pref}_rssi_mean_row"] = df[col].map(mean_rssi)
            part = df.groupby(["subject_id", "lifelog_date"]).agg(**{
                f"{pref}_n": (f"{pref}_items", "sum"),
                f"{pref}_rows": (f"{pref}_items", "count"),
                f"{pref}_rssi_mean": (f"{pref}_rssi_mean_row", "mean"),
                f"{pref}_rssi_std": (f"{pref}_rssi_mean_row", "std"),
            }).reset_index()
        elif pref == "raw_usage":
            def total_time(x):
                try: return float(sum(float(d.get("total_time", 0)) for d in x))
                except Exception: return np.nan
            def n_apps(x):
                try: return len(set(str(d.get("app_name", "")) for d in x))
                except Exception: return 0
            df[f"{pref}_time_row"] = df[col].map(total_time)
            df[f"{pref}_apps_row"] = df[col].map(n_apps)
            part = df.groupby(["subject_id", "lifelog_date"]).agg(**{
                f"{pref}_rows": (f"{pref}_items", "count"),
                f"{pref}_total_time": (f"{pref}_time_row", "sum"),
                f"{pref}_apps_mean": (f"{pref}_apps_row", "mean"),
                f"{pref}_apps_max": (f"{pref}_apps_row", "max"),
            }).reset_index()
        elif pref == "raw_gps":
            def gps_mean(x, key):
                try:
                    vals = [float(d.get(key, np.nan)) for d in x]
                    vals = [v for v in vals if np.isfinite(v)]
                    return float(np.mean(vals)) if vals else np.nan
                except Exception:
                    return np.nan
            for key in ["speed", "altitude", "latitude", "longitude"]:
                df[f"{pref}_{key}_row"] = df[col].map(lambda x, key=key: gps_mean(x, key))
            part = df.groupby(["subject_id", "lifelog_date"]).agg(**{
                f"{pref}_n": (f"{pref}_items", "sum"),
                f"{pref}_rows": (f"{pref}_items", "count"),
                f"{pref}_speed_mean": (f"{pref}_speed_row", "mean"),
                f"{pref}_altitude_mean": (f"{pref}_altitude_row", "mean"),
                f"{pref}_lat_std": (f"{pref}_latitude_row", "std"),
                f"{pref}_lon_std": (f"{pref}_longitude_row", "std"),
            }).reset_index()
        else:
            part = df.groupby(["subject_id", "lifelog_date"]).agg(**{
                f"{pref}_n": (f"{pref}_items", "sum"),
                f"{pref}_rows": (f"{pref}_items", "count"),
            }).reset_index()
        parts.append(part)

    if not parts:
        return pd.DataFrame()
    out = parts[0]
    for p in parts[1:]:
        out = out.merge(p, on=["subject_id", "lifelog_date"], how="outer")
    out["subject_id"] = out["subject_id"].astype(str)
    out.to_parquet(FEAT / "deep_raw_modality_daily_features.parquet", index=False)
    return out


def eval_binary_family(table, cols, target, masks, normalized=False):
    rows = []
    work = standardize_within_subject(table, cols) if normalized else table
    for name, mask, future, scheme in masks:
        trm, vam = ~mask, mask
        ytr = table.loc[trm, target].astype(int).to_numpy()
        yva = table.loc[vam, target].astype(int).to_numpy()
        if len(np.unique(ytr)) < 2:
            continue
        pipe = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sel", SelectKBest(f_classif, k=min(40, len(cols)))),
            ("scale", RobustScaler()),
            ("clf", LogisticRegression(C=0.05, solver="liblinear", max_iter=1000, random_state=42)),
        ])
        try:
            pipe.fit(work.loc[trm, cols], ytr)
            p = pipe.predict_proba(work.loc[vam, cols])[:, 1]
            auc = roc_auc_score(yva, p) if len(np.unique(yva)) == 2 else np.nan
            rows.append({"mask": name, "scheme": scheme, "target": target, "normalized": normalized, "n_cols": len(cols), "logloss": safe_logloss(yva, p), "auc": auc})
        except Exception:
            pass
    return rows


def eval_state_family(table, cols, masks, normalized=False):
    rows = []
    work = standardize_within_subject(table, cols) if normalized else table
    for name, mask, future, scheme in masks:
        trm, vam = ~mask, mask
        ytr = table.loc[trm, "latent_state"].astype(int).to_numpy()
        yva = table.loc[vam, "latent_state"].astype(int).to_numpy()
        if len(np.unique(ytr)) < 2:
            continue
        pipe = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sel", SelectKBest(f_classif, k=min(50, len(cols)))),
            ("scale", RobustScaler()),
            ("clf", LogisticRegression(C=0.08, solver="lbfgs", max_iter=1500, random_state=42)),
        ])
        try:
            pipe.fit(work.loc[trm, cols], ytr)
            pred = pipe.predict(work.loc[vam, cols])
            proba = pipe.predict_proba(work.loc[vam, cols])
            classes = pipe.named_steps["clf"].classes_
            K = int(table.latent_state.max() + 1)
            aligned = np.ones((len(yva), K)) * 1e-6
            for j, cls in enumerate(classes):
                aligned[:, int(cls)] = proba[:, j]
            aligned /= aligned.sum(axis=1, keepdims=True)
            rows.append({
                "mask": name, "scheme": scheme, "normalized": normalized, "n_cols": len(cols),
                "accuracy": accuracy_score(yva, pred),
                "balanced_accuracy": balanced_accuracy_score(yva, pred),
                "state_logloss": log_loss(yva, aligned, labels=list(range(K))),
                "majority_acc": pd.Series(ytr).value_counts(normalize=True).iloc[0],
            })
        except Exception:
            pass
    return rows


def raw_modality_separability(train, sample):
    raw = daily_agg_raw_modalities()
    raw["lifelog_date"] = pd.to_datetime(raw["lifelog_date"])
    table = train.merge(raw, on=["subject_id", "lifelog_date"], how="left")
    raw_cols = [c for c in table.columns if c.startswith("raw_") and pd.api.types.is_numeric_dtype(table[c])]
    families = defaultdict(list)
    for c in raw_cols:
        parts = c.split("_")
        fam = "_".join(parts[:2]) if len(parts) >= 2 else "raw_other"
        families[fam].append(c)
    masks = make_masks(train, sample, seeds=range(3))
    state_rows, target_rows = [], []
    for fam, cols in families.items():
        if len(cols) < 2:
            continue
        for norm in [False, True]:
            for r in eval_state_family(table, cols, masks, normalized=norm):
                r["modality"] = fam
                state_rows.append(r)
            for y in LABELS:
                for r in eval_binary_family(table, cols, y, masks, normalized=norm):
                    r["modality"] = fam
                    target_rows.append(r)
    state_df = pd.DataFrame(state_rows)
    target_df = pd.DataFrame(target_rows)
    if len(state_df):
        state_sum = state_df.groupby(["scheme", "modality", "normalized"]).agg(
            masks=("mask", "count"), acc=("accuracy", "mean"), bal_acc=("balanced_accuracy", "mean"),
            state_logloss=("state_logloss", "mean"), majority_acc=("majority_acc", "mean")
        ).reset_index().sort_values(["scheme", "bal_acc"], ascending=[True, False])
    else:
        state_sum = pd.DataFrame()
    if len(target_df):
        # compare to target prior in same mask.
        target_sum = target_df.groupby(["scheme", "target", "modality", "normalized"]).agg(
            masks=("mask", "count"), mean_logloss=("logloss", "mean"), mean_auc=("auc", "mean")
        ).reset_index().sort_values(["scheme", "target", "mean_auc"], ascending=[True, True, False])
    else:
        target_sum = pd.DataFrame()
    state_df.to_csv(EXP / "deep_raw_modality_state_separability_raw.csv", index=False)
    state_sum.to_csv(EXP / "deep_raw_modality_state_separability_summary.csv", index=False)
    target_df.to_csv(EXP / "deep_raw_modality_target_signal_raw.csv", index=False)
    target_sum.to_csv(EXP / "deep_raw_modality_target_signal_summary.csv", index=False)
    return raw, state_sum, target_sum


def q2q3_grammar(train):
    rows = []
    for y in ["Q2", "Q3"]:
        other = "Q3" if y == "Q2" else "Q2"
        for sid, sub in train.sort_values(["subject_id", "sleep_date"]).groupby("subject_id"):
            sub = sub.reset_index(drop=True)
            dates = sub.sleep_date.values.astype("datetime64[D]").astype(int)
            arr = sub[y].astype(int).to_numpy()
            oth = sub[other].astype(int).to_numpy()
            for i in range(1, len(sub) - 1):
                pg = int(dates[i] - dates[i-1]); ng = int(dates[i+1] - dates[i])
                code = f"{arr[i-1]}{arr[i+1]}"
                direction = "agree_00" if code == "00" else "agree_11" if code == "11" else "rising_01" if code == "01" else "falling_10"
                rows.append({
                    "target": y, "other": other, "subject_id": sid, "sleep_date": sub.loc[i, "sleep_date"],
                    "y": int(arr[i]), "prev_y": int(arr[i-1]), "next_y": int(arr[i+1]), "direction": direction,
                    "prev_gap_d": pg, "next_gap_d": ng, "gap_asym_next_minus_prev": ng - pg,
                    "other_t": int(oth[i]), "other_prev": int(oth[i-1]), "other_next": int(oth[i+1]),
                    "latent_state": int(sub.loc[i, "latent_state"]),
                })
    dyn = pd.DataFrame(rows)
    dyn.to_csv(EXP / "deep_q2q3_gap_direction_rows.csv", index=False)
    summary = dyn.groupby(["target", "direction"]).agg(
        n=("y", "count"), p_y1=("y", "mean"), p_other_t1=("other_t", "mean"),
        mean_prev_gap=("prev_gap_d", "mean"), mean_next_gap=("next_gap_d", "mean"),
    ).reset_index()
    # Stratify conflict by gap asymmetry and other target.
    dyn["gap_bucket"] = pd.cut(dyn["gap_asym_next_minus_prev"], bins=[-999, -4, -1, 1, 4, 999], labels=["next_much_closer", "next_closer", "balanced", "prev_closer", "prev_much_closer"])
    conflict = dyn[dyn.direction.isin(["rising_01", "falling_10"])].groupby(["target", "direction", "gap_bucket", "other_t"]).agg(
        n=("y", "count"), p_y1=("y", "mean"), mean_prev_gap=("prev_gap_d", "mean"), mean_next_gap=("next_gap_d", "mean")
    ).reset_index().sort_values(["target", "direction", "gap_bucket", "other_t"])
    summary.to_csv(EXP / "deep_q2q3_direction_summary.csv", index=False)
    conflict.to_csv(EXP / "deep_q2q3_conflict_gap_other_summary.csv", index=False)
    return summary, conflict


def main():
    train_base = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    states = pd.read_csv(EXP / "advanced_ds_row_latent_states.csv", parse_dates=["sleep_date", "lifelog_date"])
    train_state = train_base.merge(states[IDS + ["latent_state", "state_confidence"]], on=IDS, how="left")

    df = big67.load_base_table().sort_values(["is_train", "subject_id", "sleep_date"], ascending=[False, True, True]).reset_index(drop=True)
    train_full = df[df.is_train.eq(1)].copy().reset_index(drop=True)
    train_full = train_full.merge(states[IDS + ["latent_state", "state_confidence"]], on=IDS, how="left")
    sample_full = df[df.is_train.eq(0)].copy().reset_index(drop=True)
    cols = feature_cols(train_full)

    raw_delta, event_fam, event_feat = event_study_engineered(train_full, cols)
    raw_daily, raw_state_sum, raw_target_sum = raw_modality_separability(train_state, sample)
    q23_sum, q23_conflict = q2q3_grammar(train_state)

    # concise report
    lines = []
    lines += ["# Deeper State/Event/Modality/Grammar Diagnostics", ""]
    lines += ["## 1. State transition event-study", "", "For each latent-state transition day, engineered features were z-scored and compared as `after - before`. This asks: when label grammar changes, what behavioral feature families move?", ""]
    if len(event_fam):
        lines += [event_fam.groupby("transition").head(8).to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 2. Raw modality state separability", "", "Daily raw modality aggregates were built directly from the original parquet files, then tested under masked splits. `normalized=True` means within-subject z-scoring, i.e. asking whether deviations from a person's own baseline matter more than raw level.", ""]
    if len(raw_state_sum):
        lines += [raw_state_sum.groupby("scheme").head(20).to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 3. Raw modality target signal", "", "AUC is easier to read here than tiny logloss differences. Values near 0.5 mean no useful rank signal.", ""]
    if len(raw_target_sum):
        lines += [raw_target_sum.groupby(["scheme", "target"]).head(3).to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 4. Q2/Q3 direction/gap grammar", "", q23_sum.to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["### Conflict cases by gap bucket and other target", "", q23_conflict.head(80).to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 5. Output files", ""]
    for name in [
        "deep_state_transition_feature_deltas_raw.csv",
        "deep_state_transition_family_event_study.csv",
        "deep_state_transition_top_features.csv",
        "deep_raw_modality_daily_features.parquet",
        "deep_raw_modality_state_separability_summary.csv",
        "deep_raw_modality_target_signal_summary.csv",
        "deep_q2q3_direction_summary.csv",
        "deep_q2q3_conflict_gap_other_summary.csv",
    ]:
        lines.append(f"- `experiments/{name}`" if not name.endswith('.parquet') else f"- `features/{name}`")
    report = "\n".join(lines) + "\n"
    (EXP / "deep_state_event_modality_grammar_report.md").write_text(report, encoding="utf-8")
    print(report[:7000])
    print("\n[written]", EXP / "deep_state_event_modality_grammar_report.md")


if __name__ == "__main__":
    main()
