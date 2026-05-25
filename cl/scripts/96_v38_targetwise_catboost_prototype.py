#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.decomposition import PCA
from sklearn.feature_selection import f_classif
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

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
ANCHOR_FILE = OUT_DIR / "submission_meta_anchor_w02_noq3_prob.csv"


@dataclass(frozen=True)
class FeatureSpec:
    name: str
    prefix: str
    max_cols: int


FEATURE_SPECS = [
    FeatureSpec("model_features_v0.parquet", "mf", 220),
    FeatureSpec("semantic_topk_features_v2.parquet", "sem", 140),
    FeatureSpec("observation_identity_token_features.parquet", "tok", 90),
    FeatureSpec("external_context_features_v1.parquet", "ext", 75),
    FeatureSpec("deep_raw_modality_daily_features.parquet", "raw", 90),
    FeatureSpec("ssl_hourly_dino_temporal_embeddings.parquet", "dino", 48),
    FeatureSpec("ssl_hourly_masked_ae_embeddings.parquet", "mae", 48),
    FeatureSpec("cola_denoising_latent_v1.parquet", "cola", 20),
    FeatureSpec("goal4_hour_transition_features_v1.parquet", "g4h", 190),
    FeatureSpec("goal4_sleep_boundary_rest_features_v1.parquet", "g4r", 90),
]


def clip(p: np.ndarray | pd.Series | float, lo: float = 0.03, hi: float = 0.97):
    return np.clip(np.asarray(p, dtype=float), lo, hi)


def safe_logit(p: np.ndarray) -> np.ndarray:
    p = clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def md_table(df: pd.DataFrame, max_rows: int | None = None, floatfmt: str = ".5f") -> str:
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


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["sleep_date", "lifelog_date", "date"]:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c]).dt.date.astype(str)
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = normalize_dates(pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv"))
    test = normalize_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv"))
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    test = test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    return train, test


def variance_pick(df: pd.DataFrame, cols: list[str], max_cols: int) -> list[str]:
    if len(cols) <= max_cols:
        return cols
    x = df[cols].replace([np.inf, -np.inf], np.nan)
    ok = x.notna().mean().loc[lambda s: s >= 0.35].index.tolist()
    if not ok:
        return cols[:max_cols]
    var = x[ok].fillna(0).var().sort_values(ascending=False)
    return var.head(max_cols).index.tolist()


def load_feature_frame(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    base = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).drop_duplicates().reset_index(drop=True)
    out = base.copy()
    loaded = []
    for spec in FEATURE_SPECS:
        path = FEATURE_DIR / spec.name
        if not path.exists():
            continue
        d = normalize_dates(pd.read_parquet(path))
        if "date" in d.columns and "lifelog_date" not in d.columns:
            d = d.rename(columns={"date": "lifelog_date"})
        join = ["subject_id", "lifelog_date"]
        if "sleep_date" in d.columns:
            join = ["subject_id", "sleep_date", "lifelog_date"]
        num = [c for c in d.columns if c not in join and pd.api.types.is_numeric_dtype(d[c])]
        num = [c for c in num if "__subj_mean" not in c and not c.endswith("_mean_y")]
        keep = variance_pick(d, num, spec.max_cols)
        renamed = {c: f"{spec.prefix}__{c}" for c in keep}
        out = out.merge(d[join + keep].rename(columns=renamed), on=join, how="left")
        loaded.append({"artifact": spec.name, "kept_cols": len(keep), "rows": len(d)})
    pd.DataFrame(loaded).to_csv(EXPERIMENT_DIR / "v38_loaded_feature_artifacts.csv", index=False)
    return out


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    dt = pd.to_datetime(out["lifelog_date"])
    out["v38_dow"] = dt.dt.dayofweek
    out["v38_month"] = dt.dt.month
    out["v38_dayofyear"] = dt.dt.dayofyear
    out["v38_dow_sin"] = np.sin(2 * np.pi * out["v38_dow"] / 7)
    out["v38_dow_cos"] = np.cos(2 * np.pi * out["v38_dow"] / 7)
    out["v38_subject_order"] = out.groupby("subject_id").cumcount()
    n = out.groupby("subject_id")["lifelog_date"].transform("count")
    out["v38_subject_order_frac"] = out["v38_subject_order"] / np.maximum(1, n - 1)
    return out


def build_state_embedding(frame: pd.DataFrame, train_n: int, max_state_cols: int = 260, n_components: int = 24) -> tuple[pd.DataFrame, list[str]]:
    out = frame.copy()
    candidates = [
        c
        for c in out.columns
        if c not in KEYS and pd.api.types.is_numeric_dtype(out[c]) and not c.startswith("v38_pca_")
    ]
    x_train = out.iloc[:train_n][candidates].replace([np.inf, -np.inf], np.nan)
    usable = x_train.notna().mean().loc[lambda s: s >= 0.45].index.tolist()
    usable = [c for c in usable if x_train[c].std(skipna=True) > 1e-8]
    usable = variance_pick(out.iloc[:train_n], usable, max_state_cols)
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    pca = PCA(n_components=min(n_components, len(usable)), random_state=20260525)
    X = out[usable].replace([np.inf, -np.inf], np.nan)
    Xi = imputer.fit_transform(X)
    Xs = scaler.fit_transform(Xi)
    Z = pca.fit_transform(Xs)
    for i in range(Z.shape[1]):
        out[f"v38_pca_{i:02d}"] = Z[:, i]
    out["v38_state_norm"] = np.sqrt((Z**2).sum(axis=1))
    pca_cols = [f"v38_pca_{i:02d}" for i in range(Z.shape[1])]
    return out, pca_cols


def add_trajectory_features(frame: pd.DataFrame, pca_cols: list[str]) -> pd.DataFrame:
    out = frame.copy()
    out["_dt"] = pd.to_datetime(out["lifelog_date"])
    out = out.sort_values(["subject_id", "_dt"]).reset_index(drop=True)
    Z = out[pca_cols].to_numpy(float)
    prev_dist = np.zeros(len(out))
    next_dist = np.zeros(len(out))
    speed3 = np.zeros(len(out))
    accel = np.zeros(len(out))
    for _, idx in out.groupby("subject_id").indices.items():
        idx = np.asarray(idx)
        z = Z[idx]
        if len(idx) > 1:
            dprev = np.sqrt(((z[1:] - z[:-1]) ** 2).sum(axis=1))
            prev_dist[idx[1:]] = dprev
            next_dist[idx[:-1]] = dprev
            roll = pd.Series(np.r_[0.0, dprev]).rolling(3, min_periods=1).mean().to_numpy()
            speed3[idx] = roll
            accel[idx] = np.r_[0.0, np.diff(roll)]
    out["v38_traj_prev_dist"] = prev_dist
    out["v38_traj_next_dist"] = next_dist
    out["v38_traj_speed3"] = speed3
    out["v38_traj_accel"] = accel
    out = out.drop(columns=["_dt"])
    return out.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def key_to_index(df: pd.DataFrame) -> dict[tuple[str, str], int]:
    return {(str(r.subject_id), str(r.lifelog_date)): i for i, r in df.reset_index(drop=True).iterrows()}


def fold_indices(train: pd.DataFrame, fold: dict) -> tuple[np.ndarray, np.ndarray]:
    idx = key_to_index(train)
    tr = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["train_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    va = [idx[(str(k["subject_id"]), str(k["lifelog_date"]))] for k in fold["valid_keys"] if (str(k["subject_id"]), str(k["lifelog_date"])) in idx]
    return np.asarray(tr, dtype=int), np.asarray(va, dtype=int)


def subject_prior(train: pd.DataFrame, rows: pd.DataFrame, target: str, alpha: float = 20.0) -> np.ndarray:
    g = float(train[target].mean())
    pos = train.groupby("subject_id")[target].sum()
    cnt = train.groupby("subject_id")[target].count()
    sm = ((pos + alpha * g) / (cnt + alpha)).to_dict()
    return np.array([sm.get(s, g) for s in rows["subject_id"]], dtype=float)


def cosine_to(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    an = np.sqrt((a * a).sum(axis=1))
    bn = float(np.sqrt((b * b).sum()))
    if bn < 1e-12:
        return np.zeros(len(a))
    return (a @ b) / np.maximum(1e-12, an * bn)


def proto_stats(Z: np.ndarray, proto: np.ndarray, prefix: str) -> dict[str, np.ndarray]:
    d = Z - proto
    return {
        f"{prefix}_dist": np.sqrt((d * d).sum(axis=1)),
        f"{prefix}_l1": np.abs(d).mean(axis=1),
        f"{prefix}_cos": cosine_to(Z, proto),
    }


def recent_subject_proto(meta: pd.DataFrame, Z: np.ndarray, windows: list[int]) -> dict[str, np.ndarray]:
    n = len(meta)
    rows: dict[str, np.ndarray] = {}
    order = meta.assign(_i=np.arange(n), _dt=pd.to_datetime(meta["lifelog_date"])).sort_values(["subject_id", "_dt"])
    for w in windows:
        dist = np.full(n, np.nan)
        cos = np.full(n, np.nan)
        for _, g in order.groupby("subject_id"):
            idx = g["_i"].to_numpy()
            for pos, i in enumerate(idx):
                hist = idx[max(0, pos - w) : pos]
                if len(hist) == 0:
                    continue
                proto = Z[hist].mean(axis=0)
                d = Z[i] - proto
                dist[i] = float(np.sqrt((d * d).sum()))
                cos[i] = float(cosine_to(Z[i : i + 1], proto)[0])
        rows[f"v38_recent{w}_dist"] = dist
        rows[f"v38_recent{w}_cos"] = cos
    return rows


def build_prototype_features(
    meta: pd.DataFrame,
    Z_all: np.ndarray,
    train_proto_idx: np.ndarray,
    target: str,
    labels: pd.DataFrame,
    model_idx: np.ndarray | None = None,
) -> pd.DataFrame:
    n = len(meta)
    Z = Z_all[meta["_full_index"].to_numpy()]
    train_meta = meta.iloc[train_proto_idx].reset_index(drop=True)
    Z_train = Z[train_proto_idx]
    y = labels.iloc[train_proto_idx][target].astype(int).to_numpy()
    global_proto = Z_train.mean(axis=0)
    rows: dict[str, np.ndarray] = {}
    rows.update(proto_stats(Z, global_proto, "v38_global"))

    high = Z_train[y == 1]
    low = Z_train[y == 0]
    high_proto = high.mean(axis=0) if len(high) else global_proto
    low_proto = low.mean(axis=0) if len(low) else global_proto
    hp = proto_stats(Z, high_proto, "v38_t_high")
    lp = proto_stats(Z, low_proto, "v38_t_low")
    rows.update(hp)
    rows.update(lp)
    rows["v38_t_margin_dist_low_minus_high"] = lp["v38_t_low_dist"] - hp["v38_t_high_dist"]
    rows["v38_t_margin_cos_high_minus_low"] = hp["v38_t_high_cos"] - lp["v38_t_low_cos"]
    rows["v38_target_base_rate"] = np.full(n, float(y.mean()))

    subj_mean: dict[str, np.ndarray] = {}
    subj_vol: dict[str, float] = {}
    subj_cnt: dict[str, int] = {}
    subj_rate: dict[str, float] = {}
    subj_high: dict[str, np.ndarray] = {}
    subj_low: dict[str, np.ndarray] = {}
    for s, g in train_meta.assign(_local_i=np.arange(len(train_meta))).groupby("subject_id"):
        ii = g["_local_i"].to_numpy()
        z = Z_train[ii]
        p = z.mean(axis=0)
        subj_mean[s] = p
        subj_cnt[s] = len(ii)
        subj_vol[s] = float(np.sqrt(((z - p) ** 2).sum(axis=1)).mean()) if len(ii) else 0.0
        yy = y[ii]
        subj_rate[s] = float(yy.mean()) if len(ii) else float(y.mean())
        if (yy == 1).sum() >= 2:
            subj_high[s] = z[yy == 1].mean(axis=0)
        if (yy == 0).sum() >= 2:
            subj_low[s] = z[yy == 0].mean(axis=0)

    sm_dist = np.zeros(n)
    sm_cos = np.zeros(n)
    sm_vol = np.zeros(n)
    sm_cnt = np.zeros(n)
    sm_rate = np.zeros(n)
    sh_dist = np.zeros(n)
    sl_dist = np.zeros(n)
    st_margin = np.zeros(n)
    for i, s in enumerate(meta["subject_id"].astype(str)):
        mp = subj_mean.get(s, global_proto)
        hp_s = subj_high.get(s, high_proto)
        lp_s = subj_low.get(s, low_proto)
        sm_dist[i] = float(np.sqrt(((Z[i] - mp) ** 2).sum()))
        sm_cos[i] = float(cosine_to(Z[i : i + 1], mp)[0])
        sm_vol[i] = subj_vol.get(s, 0.0)
        sm_cnt[i] = subj_cnt.get(s, 0)
        sm_rate[i] = subj_rate.get(s, float(y.mean()))
        sh_dist[i] = float(np.sqrt(((Z[i] - hp_s) ** 2).sum()))
        sl_dist[i] = float(np.sqrt(((Z[i] - lp_s) ** 2).sum()))
        st_margin[i] = sl_dist[i] - sh_dist[i]
    rows["v38_subject_mean_dist"] = sm_dist
    rows["v38_subject_mean_cos"] = sm_cos
    rows["v38_subject_volatility"] = sm_vol
    rows["v38_subject_count"] = sm_cnt
    rows["v38_subject_target_rate"] = sm_rate
    rows["v38_subject_high_dist"] = sh_dist
    rows["v38_subject_low_dist"] = sl_dist
    rows["v38_subject_margin_dist_low_minus_high"] = st_margin

    rows.update(recent_subject_proto(meta, Z, [3, 7, 14]))
    out = pd.DataFrame(rows)

    if model_idx is not None:
        local_to_row = {int(v): pos for pos, v in enumerate(train_proto_idx)}
        for row_i in model_idx:
            if int(row_i) not in local_to_row:
                continue
            j = local_to_row[int(row_i)]
            cls = int(labels.iloc[int(row_i)][target])
            cls_mask = y == cls
            if cls_mask.sum() <= 1:
                continue
            z_pool = Z_train[cls_mask]
            z_self = Z[int(row_i)]
            proto = (z_pool.sum(axis=0) - z_self) / max(1, len(z_pool) - 1)
            dist = float(np.sqrt(((Z[int(row_i)] - proto) ** 2).sum()))
            if cls == 1:
                out.loc[int(row_i), "v38_t_high_dist"] = dist
            else:
                out.loc[int(row_i), "v38_t_low_dist"] = dist
            out.loc[int(row_i), "v38_t_margin_dist_low_minus_high"] = out.loc[int(row_i), "v38_t_low_dist"] - out.loc[int(row_i), "v38_t_high_dist"]
    return out


def select_features(X: pd.DataFrame, y: np.ndarray, always: list[str], k: int = 300) -> list[str]:
    candidates = [c for c in X.columns if c not in always]
    candidates = [c for c in candidates if pd.api.types.is_numeric_dtype(X[c])]
    candidates = [c for c in candidates if X[c].replace([np.inf, -np.inf], np.nan).notna().mean() >= 0.45]
    candidates = [c for c in candidates if X[c].replace([np.inf, -np.inf], np.nan).std(skipna=True) > 1e-9]
    if len(candidates) <= k:
        return always + candidates
    imp = SimpleImputer(strategy="median")
    Xi = imp.fit_transform(X[candidates].replace([np.inf, -np.inf], np.nan))
    scores, _ = f_classif(Xi, y)
    scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
    top = np.argsort(scores)[::-1][:k]
    return always + [candidates[i] for i in top]


def fit_catboost(X: pd.DataFrame, y: np.ndarray) -> tuple[CatBoostClassifier, list[str]]:
    X = X.replace([np.inf, -np.inf], np.nan)
    model = CatBoostClassifier(
        iterations=260,
        depth=3,
        learning_rate=0.035,
        l2_leaf_reg=18.0,
        random_seed=20260525,
        loss_function="Logloss",
        eval_metric="Logloss",
        verbose=False,
        allow_writing_files=False,
        od_type="Iter",
        od_wait=40,
    )
    model.fit(X, y)
    return model, list(X.columns)


def build_test_meta(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ordered_test = test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    for global_i, r in ordered_test.iterrows():
        tr = train[train["subject_id"].eq(r.subject_id)].sort_values("lifelog_date")
        te = ordered_test[ordered_test["subject_id"].eq(r.subject_id)].sort_values("lifelog_date").reset_index(drop=True)
        q = pd.to_datetime(r.lifelog_date)
        tr_dates = pd.to_datetime(tr["lifelog_date"])
        before = tr_dates[tr_dates < q]
        after = tr_dates[tr_dates > q]
        all_dates = pd.concat(
            [tr[["lifelog_date"]].assign(kind="train"), te[["lifelog_date"]].assign(kind="test")],
            ignore_index=True,
        ).sort_values("lifelog_date").reset_index(drop=True)
        pos_all = int(all_dates.index[(all_dates["lifelog_date"].eq(r.lifelog_date)) & (all_dates["kind"].eq("test"))][0])
        within_order = int(te.index[te["lifelog_date"].eq(r.lifelog_date)][0])
        rows.append(
            {
                "subject_id": r.subject_id,
                "sleep_date": r.sleep_date,
                "lifelog_date": r.lifelog_date,
                "row_id": global_i,
                "within_subject_order": within_order,
                "within_subject_frac": within_order / max(1, len(te) - 1),
                "test_timeline_frac": pos_all / max(1, len(all_dates) - 1),
                "prev_train_gap_d": float((q - before.max()).days) if len(before) else np.nan,
                "next_train_gap_d": float((after.min() - q).days) if len(after) else np.nan,
                "nearest_train_gap_d": float(
                    np.nanmin(
                        [
                            (q - before.max()).days if len(before) else np.nan,
                            (after.min() - q).days if len(after) else np.nan,
                        ]
                    )
                ),
                "has_future_train": int(len(after) > 0),
                "inside_train_range": int((q >= tr_dates.min()) and (q <= tr_dates.max())),
            }
        )
    meta = pd.DataFrame(rows)
    center = meta.groupby("subject_id")["test_timeline_frac"].transform("median")
    raw = 0.30 + np.exp(-0.5 * ((meta["test_timeline_frac"] - center) / 0.25) ** 2) + 0.5 * meta["test_timeline_frac"]
    raw += 0.65 * meta["inside_train_range"] + 0.35 * meta["has_future_train"]
    raw -= 0.03 * meta["nearest_train_gap_d"].fillna(meta["nearest_train_gap_d"].median())
    meta["publiclike_score"] = (raw - raw.min()) / max(1e-9, raw.max() - raw.min())
    return meta


def validation_loop(train: pd.DataFrame, full_frame: pd.DataFrame, pca_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict]]:
    base_cols = [
        c
        for c in full_frame.columns
        if c not in KEYS and pd.api.types.is_numeric_dtype(full_frame[c]) and not c.startswith("_")
    ]
    always_proto = [
        "anchor",
        "anchor_logit",
        "v38_global_dist",
        "v38_t_margin_dist_low_minus_high",
        "v38_t_margin_cos_high_minus_low",
        "v38_subject_mean_dist",
        "v38_subject_margin_dist_low_minus_high",
        "v38_subject_volatility",
        "v38_recent3_dist",
        "v38_recent7_dist",
        "v38_traj_prev_dist",
        "v38_traj_next_dist",
        "v38_traj_speed3",
    ]
    Z_all = full_frame[pca_cols].to_numpy(float)
    rows = []
    oof = train[KEYS].copy()
    for target in LABELS:
        oof[f"{target}_anchor"] = np.nan
        oof[f"{target}_model"] = np.nan

    for family, path in FOLD_FILES.items():
        folds = json.loads(path.read_text())["folds"]
        for fold in folds:
            tr_idx, va_idx = fold_indices(train, fold)
            local_idx = np.r_[tr_idx, va_idx]
            meta = full_frame.iloc[local_idx].reset_index(drop=True).copy()
            meta["_full_index"] = local_idx
            model_local = np.arange(len(tr_idx))
            valid_local = np.arange(len(tr_idx), len(local_idx))
            for target in LABELS:
                ytr = train.iloc[tr_idx][target].astype(int).to_numpy()
                yva = train.iloc[va_idx][target].astype(int).to_numpy()
                proto = build_prototype_features(meta, Z_all, np.arange(len(tr_idx)), target, train.iloc[local_idx].reset_index(drop=True), model_idx=model_local)
                anchor_tr = subject_prior(train.iloc[tr_idx], train.iloc[tr_idx], target)
                anchor_va = subject_prior(train.iloc[tr_idx], train.iloc[va_idx], target)
                X = pd.concat([meta[base_cols].reset_index(drop=True), proto], axis=1)
                X["anchor"] = np.r_[anchor_tr, anchor_va]
                X["anchor_logit"] = safe_logit(X["anchor"].to_numpy())
                keep = select_features(X.iloc[model_local], ytr, [c for c in always_proto if c in X.columns], k=320)
                model, used = fit_catboost(X.iloc[model_local][keep], ytr)
                pva = clip(model.predict_proba(X.iloc[valid_local][used].replace([np.inf, -np.inf], np.nan))[:, 1])
                base_loss = float(logloss(yva, anchor_va))
                model_loss = float(logloss(yva, pva))
                best = {"weight": 1.0, "loss": model_loss}
                for w in [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.55, 0.70]:
                    pred = clip(anchor_va * (1 - w) + pva * w)
                    loss = float(logloss(yva, pred))
                    if loss < best["loss"]:
                        best = {"weight": w, "loss": loss}
                rows.append(
                    {
                        "family": family,
                        "fold": fold["name"],
                        "target": target,
                        "n_train": int(len(tr_idx)),
                        "n_valid": int(len(va_idx)),
                        "anchor_loss": base_loss,
                        "model_loss": model_loss,
                        "best_blend_weight": best["weight"],
                        "best_blend_loss": best["loss"],
                        "delta_model_vs_anchor": model_loss - base_loss,
                        "delta_best_vs_anchor": best["loss"] - base_loss,
                        "n_features": len(used),
                    }
                )
                oof.loc[va_idx, f"{target}_anchor"] = anchor_va
                oof.loc[va_idx, f"{target}_model"] = pva
    result = pd.DataFrame(rows)
    robust = {}
    for target, g in result.groupby("target"):
        agg = g.groupby("family").agg(
            anchor_loss=("anchor_loss", "mean"),
            model_loss=("model_loss", "mean"),
            best_blend_loss=("best_blend_loss", "mean"),
            delta_best_vs_anchor=("delta_best_vs_anchor", "mean"),
            best_blend_weight=("best_blend_weight", "median"),
        )
        mh = g[g["family"].isin(["hole_v1", "mirror_v1"])]
        chrono = g[g["family"].eq("chrono_tail")]
        w = float(np.clip(mh["best_blend_weight"].median() if len(mh) else 0.0, 0.0, 0.25))
        if len(mh) and mh["delta_best_vs_anchor"].mean() >= -0.001:
            w = min(w, 0.05)
        if len(chrono) and chrono["delta_best_vs_anchor"].mean() > 0.006:
            w = min(w, 0.05)
        robust[target] = {
            "safe_weight": w,
            "hole_mirror_delta": float(mh["delta_best_vs_anchor"].mean()) if len(mh) else np.nan,
            "chrono_delta": float(chrono["delta_best_vs_anchor"].mean()) if len(chrono) else np.nan,
            "family_table": agg.reset_index().to_dict("records"),
        }
    return result, oof, robust


def train_full_and_predict(
    train: pd.DataFrame,
    test: pd.DataFrame,
    full_frame: pd.DataFrame,
    pca_cols: list[str],
    robust: dict[str, dict],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_n = len(train)
    base_cols = [
        c
        for c in full_frame.columns
        if c not in KEYS and pd.api.types.is_numeric_dtype(full_frame[c]) and not c.startswith("_")
    ]
    Z_all = full_frame[pca_cols].to_numpy(float)
    meta = full_frame.copy()
    meta["_full_index"] = np.arange(len(meta))
    train_local = np.arange(train_n)
    test_local = np.arange(train_n, len(meta))
    model_pred = pd.concat([test[KEYS].reset_index(drop=True)], axis=1)
    fi_rows = []
    for target in LABELS:
        y = train[target].astype(int).to_numpy()
        proto = build_prototype_features(meta, Z_all, train_local, target, pd.concat([train, test], ignore_index=True), model_idx=train_local)
        anchor_tr = subject_prior(train, train, target)
        X = pd.concat([meta[base_cols].reset_index(drop=True), proto], axis=1)
        X["anchor"] = np.r_[anchor_tr, np.full(len(test), np.nan)]
        X.loc[test_local, "anchor"] = float(train[target].mean())
        X["anchor_logit"] = safe_logit(X["anchor"].to_numpy())
        always = [c for c in ["anchor", "anchor_logit", "v38_t_margin_dist_low_minus_high", "v38_subject_margin_dist_low_minus_high", "v38_recent3_dist"] if c in X.columns]
        keep = select_features(X.iloc[train_local], y, always, k=340)
        model, used = fit_catboost(X.iloc[train_local][keep], y)
        p = clip(model.predict_proba(X.iloc[test_local][used].replace([np.inf, -np.inf], np.nan))[:, 1])
        model_pred[target] = p
        try:
            imp = model.get_feature_importance(prettified=True).head(20)
            for _, r in imp.iterrows():
                fi_rows.append({"target": target, "feature": r["Feature Id"], "importance": float(r["Importances"])})
        except Exception:
            pass
    return model_pred, pd.DataFrame(fi_rows)


def write_submissions(train: pd.DataFrame, test: pd.DataFrame, model_pred: pd.DataFrame, robust: dict[str, dict]) -> pd.DataFrame:
    anchor = pd.read_csv(ANCHOR_FILE)
    anchor = normalize_dates(anchor).sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    model_pred = normalize_dates(model_pred).sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    test_meta = build_test_meta(train, test).sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    top30 = test_meta["publiclike_score"] >= test_meta["publiclike_score"].quantile(0.70)
    inside = test_meta["inside_train_range"].eq(1) & test_meta["has_future_train"].eq(1)

    safe = anchor.copy()
    routed = anchor.copy()
    rows = []
    for target in LABELS:
        w = float(robust[target]["safe_weight"])
        w = min(w, 0.25)
        safe[target] = clip(anchor[target].to_numpy() * (1 - w) + model_pred[target].to_numpy() * w)
        route_w = np.zeros(len(anchor)) + min(w, 0.05)
        route_w[inside.to_numpy()] = np.maximum(route_w[inside.to_numpy()], min(0.15, max(w, 0.10)))
        route_w[top30.to_numpy()] = np.maximum(route_w[top30.to_numpy()], min(0.25, max(w, 0.18)))
        routed[target] = clip(anchor[target].to_numpy() * (1 - route_w) + model_pred[target].to_numpy() * route_w)
        for name, df in [("safe", safe), ("publiclike_routed", routed)]:
            d = df[target].to_numpy(float) - anchor[target].to_numpy(float)
            rows.append(
                {
                    "submission": name,
                    "target": target,
                    "weight": w,
                    "changed_rows": int((np.abs(d) > 1e-12).sum()),
                    "mean_abs_delta": float(np.abs(d).mean()),
                    "max_abs_delta": float(np.abs(d).max()),
                }
            )

    safe_path = OUT_DIR / "submission_v38_targetwise_catboost_proto_safe_prob.csv"
    routed_path = OUT_DIR / "submission_v38_targetwise_catboost_proto_publiclike_routed_prob.csv"
    safe.to_csv(safe_path, index=False)
    routed.to_csv(routed_path, index=False)
    model_pred.to_csv(OUT_DIR / "submission_v38_targetwise_catboost_proto_raw_model_prob.csv", index=False)
    test_meta.to_csv(EXPERIMENT_DIR / "v38_test_publiclike_meta.csv", index=False)
    shift = pd.DataFrame(rows)
    shift.to_csv(EXPERIMENT_DIR / "v38_submission_shift_summary.csv", index=False)
    return shift


def validate_submission(path: Path, sample: pd.DataFrame) -> dict:
    sub = pd.read_csv(path)
    return {
        "file": path.name,
        "rows": int(len(sub)),
        "keys_ok": bool(sub[ID_COLS].astype(str).equals(sample[ID_COLS].astype(str))),
        "no_na": bool(sub[LABELS].notna().all().all()),
        "min_prob": float(sub[LABELS].min().min()),
        "max_prob": float(sub[LABELS].max().max()),
    }


def main() -> None:
    ensure_dirs()
    train, test = load_data()
    ordered_keys = pd.concat([train[KEYS], test[KEYS]], ignore_index=True).copy()
    ordered_keys["_row_order"] = np.arange(len(ordered_keys))
    features = load_feature_frame(train, test)
    features = add_calendar_features(features)
    full_frame, pca_cols = build_state_embedding(features, len(train))
    full_frame = add_trajectory_features(full_frame, pca_cols)
    full_frame = ordered_keys.merge(full_frame, on=KEYS, how="left")
    full_frame = full_frame.sort_values("_row_order").drop(columns=["_row_order"]).reset_index(drop=True)

    result, oof, robust = validation_loop(train, full_frame, pca_cols)
    result.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_validation_rows.csv", index=False)
    oof.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_oof_predictions.csv", index=False)

    summary = (
        result.groupby(["family", "target"])
        .agg(
            anchor_loss=("anchor_loss", "mean"),
            model_loss=("model_loss", "mean"),
            best_blend_loss=("best_blend_loss", "mean"),
            delta_best_vs_anchor=("delta_best_vs_anchor", "mean"),
            best_weight=("best_blend_weight", "median"),
            n_features=("n_features", "median"),
        )
        .reset_index()
    )
    family_avg = (
        result.groupby("family")
        .agg(
            anchor_loss=("anchor_loss", "mean"),
            model_loss=("model_loss", "mean"),
            best_blend_loss=("best_blend_loss", "mean"),
            delta_best_vs_anchor=("delta_best_vs_anchor", "mean"),
        )
        .reset_index()
    )
    target_avg = (
        result.groupby("target")
        .agg(
            anchor_loss=("anchor_loss", "mean"),
            model_loss=("model_loss", "mean"),
            best_blend_loss=("best_blend_loss", "mean"),
            delta_best_vs_anchor=("delta_best_vs_anchor", "mean"),
            best_weight=("best_blend_weight", "median"),
        )
        .reset_index()
    )
    robust_df = pd.DataFrame(
        [
            {
                "target": t,
                "safe_weight": v["safe_weight"],
                "hole_mirror_delta": v["hole_mirror_delta"],
                "chrono_delta": v["chrono_delta"],
            }
            for t, v in robust.items()
        ]
    )
    summary.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_summary.csv", index=False)
    family_avg.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_family_avg.csv", index=False)
    target_avg.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_target_avg.csv", index=False)
    robust_df.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_safe_weights.csv", index=False)
    (EXPERIMENT_DIR / "v38_targetwise_catboost_robust.json").write_text(json.dumps(robust, indent=2), encoding="utf-8")

    model_pred, fi = train_full_and_predict(train, test, full_frame, pca_cols, robust)
    if len(fi):
        fi.to_csv(EXPERIMENT_DIR / "v38_targetwise_catboost_feature_importance_top20.csv", index=False)
    shifts = write_submissions(train, test, model_pred, robust)
    sample = normalize_dates(pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv")).sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    validations = pd.DataFrame(
        [
            validate_submission(OUT_DIR / "submission_v38_targetwise_catboost_proto_safe_prob.csv", sample),
            validate_submission(OUT_DIR / "submission_v38_targetwise_catboost_proto_publiclike_routed_prob.csv", sample),
            validate_submission(OUT_DIR / "submission_v38_targetwise_catboost_proto_raw_model_prob.csv", sample),
        ]
    )
    validations.to_csv(EXPERIMENT_DIR / "v38_submission_validation.csv", index=False)

    report = f"""# V38 Target-wise CatBoost Prototype Report

## Validation Family Average

{md_table(family_avg)}

## Target Average

{md_table(target_avg)}

## Safe Blend Weights

{md_table(robust_df)}

## Submission Shift Summary

{md_table(shifts, max_rows=30)}

## Submission Validation

{md_table(validations)}

## Notes

- Feature base: accumulated CL feature artifacts plus goal4 transition/rest features.
- State model: unsupervised PCA day-state embedding, subject prototypes, recent prototypes, target high/low margins, subject-target margins, volatility, trajectory speed/acceleration.
- Supervised model: target-wise CatBoost with fold-local label prototypes for validation.
- Submission candidates are anchored to `submission_meta_anchor_w02_noq3_prob.csv`; raw model output is also written for diagnostics, but the anchored candidates are the practical ones.
"""
    (EXPERIMENT_DIR / "v38_targetwise_catboost_report.md").write_text(report, encoding="utf-8")

    print(report)


if __name__ == "__main__":
    main()
