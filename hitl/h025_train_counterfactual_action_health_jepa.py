from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hitl" / "h025_train_counterfactual_action_health_jepa"
ANALYSIS = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
JEPA = ROOT / "jepa"
GPT_SUBS = ROOT / "gpt_pro_pack" / "q2s1_hidden_state_translation" / "submissions"

FEATURES_IN = HITL / "h013_raw_human_state_jepa_gate" / "h013_human_state_features.csv"
H024_POOL = HITL / "h024_action_health_decoder_jepa" / "h024_candidate_pool.csv"
H024_PUBLIC_PRED = HITL / "h024_action_health_decoder_jepa" / "h024_candidate_predictions.csv"

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6


@dataclass(frozen=True)
class ProposalSpec:
    name: str
    kind: str
    group: str = "all"
    k: int = 24
    subject_only: bool = False
    date_decay: float = 21.0


def locate(name: str | Path) -> Path | None:
    path = Path(str(name))
    probes: list[Path] = []
    if path.is_absolute():
        probes.append(path)
    else:
        probes.extend(
            [
                path,
                ROOT / path,
                ANALYSIS / path,
                JEPA / path,
                HITL / path,
                GPT_SUBS / path.name,
            ]
        )
    for probe in probes:
        if probe.exists():
            return probe.resolve()
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def binary_loss(prob: np.ndarray, y: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    yy = np.asarray(y, dtype=np.float64)
    return -(yy * np.log(p) + (1.0 - yy) * np.log(1.0 - p))


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def safe_id(text: str, limit: int = 92) -> str:
    keep = []
    for ch in str(text):
        if ch.isalnum() or ch in "._-":
            keep.append(ch)
        else:
            keep.append("_")
    return "".join(keep).strip("_")[:limit].strip("_")


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rank01(x: np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = rank01(a)
    rb = rank01(b)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def feature_groups(features: pd.DataFrame) -> dict[str, list[str]]:
    ignore = set(KEYS + ["split", "date"] + TARGETS)
    numeric = [c for c in features.columns if c not in ignore and pd.api.types.is_numeric_dtype(features[c])]
    sleep_tokens = (
        "late",
        "early",
        "prebed",
        "screen",
        "charge",
        "light",
        "w_hr",
        "usage_late",
        "usage_prebed",
        "usage_early",
        "m_activity_active_late",
        "m_activity_active_early",
    )
    quality_tokens = ("count", "obs", "rows", "events", "points", "list_len", "wifi_", "ble_", "ambience_")
    calendar_tokens = (
        "weekday",
        "weekend",
        "day_of_month",
        "month",
        "payday",
        "subject_day_idx",
        "pre_weekend",
        "post_weekend",
        "month_start",
        "month_end",
    )
    social_tokens = (
        "usage_cat_call",
        "usage_cat_chat",
        "usage_cat_religion",
        "usage_cat_work",
        "usage_cat_finance",
        "usage_cat_game",
        "usage_cat_media",
        "usage_cat_shopping_food",
        "usage_cat_search_news",
        "usage_day_",
        "usage_evening_",
        "usage_late_",
        "usage_prebed_",
    )
    body_tokens = ("pedo_", "m_activity", "w_hr", "gps_")
    sleep_cols = [c for c in numeric if any(tok in c for tok in sleep_tokens)]
    quality_cols = [c for c in numeric if any(tok in c for tok in quality_tokens)]
    calendar_cols = [c for c in numeric if any(tok in c for tok in calendar_tokens)]
    social_cols = [c for c in numeric if any(tok in c for tok in social_tokens)]
    body_cols = [c for c in numeric if any(tok in c for tok in body_tokens)]
    state_cols = sorted(set(sleep_cols + quality_cols + social_cols + body_cols))
    return {
        "all": numeric,
        "state": state_cols,
        "sleep": sleep_cols,
        "quality": quality_cols,
        "social_sleep": sorted(set(social_cols + sleep_cols + calendar_cols)),
        "body_calendar": sorted(set(body_cols + calendar_cols)),
    }


def standardized_matrix(features: pd.DataFrame, cols: list[str], train_mask: np.ndarray) -> np.ndarray:
    if not cols:
        return np.zeros((len(features), 1), dtype=np.float64)
    x = features[cols].to_numpy(dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    lo = np.nanpercentile(x[train_mask], 0.5, axis=0)
    hi = np.nanpercentile(x[train_mask], 99.5, axis=0)
    x = np.minimum(np.maximum(x, lo), hi)
    mu = x[train_mask].mean(axis=0)
    sd = x[train_mask].std(axis=0)
    sd = np.where(sd < 1.0e-9, 1.0, sd)
    return np.nan_to_num((x - mu) / sd, nan=0.0, posinf=0.0, neginf=0.0)


def make_subject_time_folds(train: pd.DataFrame, n_folds: int = 5) -> np.ndarray:
    folds = np.zeros(len(train), dtype=np.int64)
    for _, idx in train.sort_values(["subject_id", "sleep_date"]).groupby("subject_id").groups.items():
        idx_arr = np.asarray(list(idx), dtype=np.int64)
        for rank, row_idx in enumerate(idx_arr):
            folds[row_idx] = min(n_folds - 1, int(rank * n_folds / max(len(idx_arr), 1)))
    return folds


def fit_oof_base(z_all: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray, train_y: np.ndarray, folds: np.ndarray) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    x_train = z_all[train_idx]
    x_test = z_all[test_idx]
    base_oof = np.zeros((len(train_idx), len(TARGETS)), dtype=np.float64)
    base_test = np.zeros((len(test_idx), len(TARGETS)), dtype=np.float64)
    rows = []
    for t_i, target in enumerate(TARGETS):
        y = train_y[:, t_i]
        fold_losses = []
        for fold in sorted(np.unique(folds)):
            tr = folds != fold
            va = folds == fold
            if len(np.unique(y[tr])) < 2:
                pred = np.full(va.sum(), float(np.mean(y[tr])), dtype=np.float64)
            else:
                clf = ExtraTreesClassifier(
                    n_estimators=180,
                    min_samples_leaf=4,
                    max_features="sqrt",
                    random_state=2500 + 17 * t_i + int(fold),
                    n_jobs=-1,
                    class_weight="balanced_subsample",
                )
                clf.fit(x_train[tr], y[tr])
                pred = clf.predict_proba(x_train[va])[:, 1]
            pred = clip_prob(pred)
            base_oof[va, t_i] = pred
            fold_losses.append(binary_loss(pred, y[va]).mean())
        if len(np.unique(y)) < 2:
            test_pred = np.full(len(test_idx), float(np.mean(y)), dtype=np.float64)
        else:
            clf = ExtraTreesClassifier(
                n_estimators=260,
                min_samples_leaf=4,
                max_features="sqrt",
                random_state=3500 + 17 * t_i,
                n_jobs=-1,
                class_weight="balanced_subsample",
            )
            clf.fit(x_train, y)
            test_pred = clf.predict_proba(x_test)[:, 1]
        base_test[:, t_i] = clip_prob(test_pred)
        rows.append(
            {
                "target": target,
                "oof_logloss": float(binary_loss(base_oof[:, t_i], y).mean()),
                "target_rate": float(y.mean()),
                "fold_logloss_mean": float(np.mean(fold_losses)),
                "fold_logloss_max": float(np.max(fold_losses)),
            }
        )
    return base_oof, base_test, pd.DataFrame(rows)


def knn_mean(
    z_train: np.ndarray,
    z_query: np.ndarray,
    y_ref: np.ndarray,
    k: int,
    ref_subject: np.ndarray,
    query_subject: np.ndarray,
    subject_only: bool,
) -> np.ndarray:
    out = np.zeros((len(z_query), y_ref.shape[1]), dtype=np.float64)
    global_mean = y_ref.mean(axis=0)
    for i in range(len(z_query)):
        allowed = np.ones(len(z_train), dtype=bool)
        if subject_only:
            allowed = ref_subject == query_subject[i]
            if allowed.sum() < 3:
                allowed = np.ones(len(z_train), dtype=bool)
        cand_idx = np.flatnonzero(allowed)
        if len(cand_idx) == 0:
            out[i] = global_mean
            continue
        diff = z_train[cand_idx] - z_query[i]
        dist = np.einsum("ij,ij->i", diff, diff)
        take = cand_idx[np.argsort(dist)[: min(k, len(cand_idx))]]
        w = 1.0 / (np.sqrt(np.sort(dist)[: min(k, len(cand_idx))]) + 1.0e-3)
        if len(w) != len(take) or float(w.sum()) <= 1.0e-12:
            out[i] = y_ref[take].mean(axis=0)
        else:
            out[i] = (y_ref[take] * (w / w.sum()).reshape(-1, 1)).sum(axis=0)
    return clip_prob(out)


def time_memory_mean(
    train_meta: pd.DataFrame,
    ref_idx: np.ndarray,
    query_idx: np.ndarray,
    y_ref: np.ndarray,
    date_decay: float,
) -> np.ndarray:
    ref = train_meta.iloc[ref_idx].reset_index(drop=True)
    query = train_meta.iloc[query_idx].reset_index(drop=True)
    out = np.zeros((len(query), y_ref.shape[1]), dtype=np.float64)
    global_mean = y_ref.mean(axis=0)
    ref_dates = pd.to_datetime(ref["sleep_date"]).to_numpy(dtype="datetime64[D]")
    query_dates = pd.to_datetime(query["sleep_date"]).to_numpy(dtype="datetime64[D]")
    ref_subject = ref["subject_id"].to_numpy()
    for i in range(len(query)):
        same = ref_subject == query.loc[i, "subject_id"]
        if same.sum() < 2:
            out[i] = global_mean
            continue
        days = np.abs((ref_dates[same] - query_dates[i]).astype("timedelta64[D]").astype(float))
        weights = np.exp(-days / date_decay)
        weights = weights / max(float(weights.sum()), 1.0e-12)
        out[i] = (y_ref[same] * weights.reshape(-1, 1)).sum(axis=0)
    return clip_prob(out)


def build_proposals(
    features: pd.DataFrame,
    z_by_group: dict[str, np.ndarray],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    train_y: np.ndarray,
    folds: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], pd.DataFrame]:
    specs = [
        ProposalSpec("global_prior", "global"),
        ProposalSpec("subject_prior", "subject"),
        ProposalSpec("subject_time_decay14", "time", date_decay=14.0),
        ProposalSpec("subject_time_decay35", "time", date_decay=35.0),
        ProposalSpec("knn_all_k16", "knn", "all", 16),
        ProposalSpec("knn_all_k40", "knn", "all", 40),
        ProposalSpec("knn_sleep_k24", "knn", "sleep", 24),
        ProposalSpec("knn_social_sleep_k32", "knn", "social_sleep", 32),
        ProposalSpec("knn_quality_k24", "knn", "quality", 24),
        ProposalSpec("knn_body_calendar_k32", "knn", "body_calendar", 32),
        ProposalSpec("subject_knn_all_k10", "knn", "all", 10, subject_only=True),
        ProposalSpec("subject_knn_social_sleep_k12", "knn", "social_sleep", 12, subject_only=True),
    ]
    train_meta = features.iloc[train_idx].reset_index(drop=True)
    test_meta = features.iloc[test_idx].reset_index(drop=True)
    train_subject = train_meta["subject_id"].to_numpy()
    test_subject = test_meta["subject_id"].to_numpy()
    global_mean = train_y.mean(axis=0)
    proposals_train: dict[str, np.ndarray] = {}
    proposals_test: dict[str, np.ndarray] = {}
    rows = []
    for spec in specs:
        q_train = np.zeros_like(train_y, dtype=np.float64)
        for fold in sorted(np.unique(folds)):
            tr_local = np.flatnonzero(folds != fold)
            va_local = np.flatnonzero(folds == fold)
            if spec.kind == "global":
                q_train[va_local] = train_y[tr_local].mean(axis=0)
            elif spec.kind == "subject":
                for row in va_local:
                    same = train_subject[tr_local] == train_subject[row]
                    q_train[row] = train_y[tr_local][same].mean(axis=0) if same.sum() >= 2 else train_y[tr_local].mean(axis=0)
            elif spec.kind == "time":
                q_train[va_local] = time_memory_mean(train_meta, tr_local, va_local, train_y[tr_local], spec.date_decay)
            elif spec.kind == "knn":
                z = z_by_group[spec.group][train_idx]
                q_train[va_local] = knn_mean(
                    z[tr_local],
                    z[va_local],
                    train_y[tr_local],
                    spec.k,
                    train_subject[tr_local],
                    train_subject[va_local],
                    spec.subject_only,
                )
            else:
                raise ValueError(spec.kind)
        if spec.kind == "global":
            q_test = np.tile(global_mean, (len(test_idx), 1))
        elif spec.kind == "subject":
            q_test = np.zeros((len(test_idx), len(TARGETS)), dtype=np.float64)
            for i in range(len(test_idx)):
                same = train_subject == test_subject[i]
                q_test[i] = train_y[same].mean(axis=0) if same.sum() >= 2 else global_mean
        elif spec.kind == "time":
            q_test = np.zeros((len(test_idx), len(TARGETS)), dtype=np.float64)
            ref = train_meta.reset_index(drop=True)
            query = test_meta.reset_index(drop=True)
            ref_dates = pd.to_datetime(ref["sleep_date"]).to_numpy(dtype="datetime64[D]")
            query_dates = pd.to_datetime(query["sleep_date"]).to_numpy(dtype="datetime64[D]")
            for i in range(len(test_idx)):
                same = train_subject == test_subject[i]
                if same.sum() < 2:
                    q_test[i] = global_mean
                    continue
                days = np.abs((ref_dates[same] - query_dates[i]).astype("timedelta64[D]").astype(float))
                w = np.exp(-days / spec.date_decay)
                w = w / max(float(w.sum()), 1.0e-12)
                q_test[i] = (train_y[same] * w.reshape(-1, 1)).sum(axis=0)
        elif spec.kind == "knn":
            z = z_by_group[spec.group]
            q_test = knn_mean(
                z[train_idx],
                z[test_idx],
                train_y,
                spec.k,
                train_subject,
                test_subject,
                spec.subject_only,
            )
        q_train = clip_prob(0.98 * q_train + 0.02 * global_mean.reshape(1, -1))
        q_test = clip_prob(0.98 * q_test + 0.02 * global_mean.reshape(1, -1))
        proposals_train[spec.name] = q_train
        proposals_test[spec.name] = q_test
        rows.append(
            {
                "proposal": spec.name,
                "kind": spec.kind,
                "group": spec.group,
                "k": spec.k,
                "subject_only": spec.subject_only,
                "mean_train_prob": float(q_train.mean()),
                "mean_test_prob": float(q_test.mean()),
            }
        )
    return proposals_train, proposals_test, pd.DataFrame(rows)


def action_feature_frame(
    row_pcs: np.ndarray,
    base: np.ndarray,
    proposal: np.ndarray,
    alpha: float,
    row_ids: np.ndarray | None = None,
    family: str | None = None,
) -> pd.DataFrame:
    n_rows = base.shape[0]
    if row_ids is None:
        row_ids = np.arange(n_rows)
    z_base = logit(base)
    z_prop = logit(proposal)
    z_action = z_base + alpha * (z_prop - z_base)
    action = clip_prob(sigmoid(z_action))
    frames = []
    target_prior = proposal.mean(axis=0)
    for t_i, target in enumerate(TARGETS):
        dlog = z_action[:, t_i] - z_base[:, t_i]
        dprob = action[:, t_i] - base[:, t_i]
        part = pd.DataFrame(
            {
                "row_id": row_ids,
                "target": target,
                "target_i": t_i,
                "alpha": alpha,
                "base_p": base[:, t_i],
                "proposal_p": proposal[:, t_i],
                "action_p": action[:, t_i],
                "delta_logit": dlog,
                "abs_delta_logit": np.abs(dlog),
                "delta_prob": dprob,
                "abs_delta_prob": np.abs(dprob),
                "base_conf": np.abs(base[:, t_i] - 0.5),
                "proposal_conf": np.abs(proposal[:, t_i] - 0.5),
                "action_conf": np.abs(action[:, t_i] - 0.5),
                "base_entropy": -(clip_prob(base[:, t_i]) * np.log(clip_prob(base[:, t_i])) + (1.0 - clip_prob(base[:, t_i])) * np.log(clip_prob(1.0 - base[:, t_i]))),
                "action_entropy": -(clip_prob(action[:, t_i]) * np.log(clip_prob(action[:, t_i])) + (1.0 - clip_prob(action[:, t_i])) * np.log(clip_prob(1.0 - action[:, t_i]))),
                "target_prior": target_prior[t_i],
                "family": "candidate" if family is None else family,
            }
        )
        for j in range(row_pcs.shape[1]):
            part[f"pc{j:02d}"] = row_pcs[:, j]
        for j, name in enumerate(TARGETS):
            part[f"target_{name}"] = 1.0 if j == t_i else 0.0
        frames.append(part)
    return pd.concat(frames, ignore_index=True)


def build_action_training_set(
    train_pcs: np.ndarray,
    base_oof: np.ndarray,
    proposals_train: dict[str, np.ndarray],
    train_y: np.ndarray,
    folds: np.ndarray,
) -> pd.DataFrame:
    rows = []
    alphas = [0.25, 0.5, 0.75, 1.0]
    base_loss = binary_loss(base_oof, train_y)
    for family, q in proposals_train.items():
        for alpha in alphas:
            feat = action_feature_frame(train_pcs, base_oof, q, alpha, row_ids=np.arange(len(train_pcs)), family=family)
            action = feat.pivot(index="row_id", columns="target", values="action_p")[TARGETS].to_numpy(dtype=np.float64)
            gain = (base_loss - binary_loss(action, train_y)).reshape(-1)
            feat["actual_gain"] = gain
            feat["actual_good"] = (gain > 0).astype(float)
            feat["fold"] = np.repeat(folds, len(TARGETS))
            rows.append(feat)
    return pd.concat(rows, ignore_index=True)


def action_feature_cols(actions: pd.DataFrame) -> list[str]:
    blocked = {"row_id", "target", "target_i", "family", "actual_gain", "actual_good", "fold"}
    cols = []
    for col in actions.columns:
        if col in blocked:
            continue
        if pd.api.types.is_numeric_dtype(actions[col]) and float(np.nanstd(actions[col].to_numpy(dtype=np.float64))) > 1.0e-12:
            cols.append(col)
    return cols


def fit_action_model(x: pd.DataFrame, y: np.ndarray, seed: int = 5000) -> ExtraTreesRegressor:
    model = ExtraTreesRegressor(
        n_estimators=120,
        min_samples_leaf=45,
        max_features=0.75,
        random_state=seed,
        n_jobs=-1,
        bootstrap=True,
    )
    model.fit(x, y)
    return model


def evaluate_action_health(actions: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred = np.zeros(len(actions), dtype=np.float64)
    fold_rows = []
    for fold in sorted(actions["fold"].unique()):
        tr = actions["fold"] != fold
        va = actions["fold"] == fold
        model = fit_action_model(actions.loc[tr, cols], actions.loc[tr, "actual_gain"].to_numpy(dtype=np.float64), seed=6000 + int(fold))
        pred[va.to_numpy()] = model.predict(actions.loc[va, cols])
        yv = actions.loc[va, "actual_gain"].to_numpy(dtype=np.float64)
        pv = pred[va.to_numpy()]
        top = pv >= np.quantile(pv, 0.90)
        fold_rows.append(
            {
                "stress": "row_time_fold",
                "fold": int(fold),
                "n": int(va.sum()),
                "spearman": spearman(yv, pv),
                "top10_gain_mean": float(yv[top].mean()),
                "all_gain_mean": float(yv.mean()),
                "top10_lift": float(yv[top].mean() - yv.mean()),
                "top10_good_rate": float((yv[top] > 0).mean()),
                "all_good_rate": float((yv > 0).mean()),
            }
        )
    overall = pd.DataFrame(
        [
            {
                "stress": "row_time_fold_overall",
                "fold": -1,
                "n": len(actions),
                "spearman": spearman(actions["actual_gain"].to_numpy(dtype=np.float64), pred),
                "top10_gain_mean": float(actions.loc[pred >= np.quantile(pred, 0.90), "actual_gain"].mean()),
                "all_gain_mean": float(actions["actual_gain"].mean()),
                "top10_lift": float(actions.loc[pred >= np.quantile(pred, 0.90), "actual_gain"].mean() - actions["actual_gain"].mean()),
                "top10_good_rate": float((actions.loc[pred >= np.quantile(pred, 0.90), "actual_gain"] > 0).mean()),
                "all_good_rate": float((actions["actual_gain"] > 0).mean()),
            }
        ]
    )
    oof = actions[["row_id", "target", "family", "alpha", "actual_gain", "actual_good", "fold"]].copy()
    oof["pred_gain"] = pred

    fam_rows = []
    rng = np.random.default_rng(20260602)
    for family in sorted(actions["family"].unique()):
        tr = actions["family"] != family
        va = actions["family"] == family
        if tr.sum() < 100 or va.sum() < 100:
            continue
        train_pos = np.flatnonzero(tr.to_numpy())
        if len(train_pos) > 55000:
            train_pos = rng.choice(train_pos, size=55000, replace=False)
        model = fit_action_model(
            actions.iloc[train_pos][cols],
            actions.iloc[train_pos]["actual_gain"].to_numpy(dtype=np.float64),
            seed=7000 + len(fam_rows),
        )
        pv = model.predict(actions.loc[va, cols])
        yv = actions.loc[va, "actual_gain"].to_numpy(dtype=np.float64)
        top = pv >= np.quantile(pv, 0.90)
        fam_rows.append(
            {
                "stress": "leave_family_out",
                "family": family,
                "n": int(va.sum()),
                "spearman": spearman(yv, pv),
                "top10_gain_mean": float(yv[top].mean()),
                "all_gain_mean": float(yv.mean()),
                "top10_lift": float(yv[top].mean() - yv.mean()),
                "top10_good_rate": float((yv[top] > 0).mean()),
                "all_good_rate": float((yv > 0).mean()),
            }
        )
    stress = pd.concat([overall, pd.DataFrame(fold_rows), pd.DataFrame(fam_rows)], ignore_index=True)

    real_rho = float(overall.iloc[0]["spearman"])
    real_lift = float(overall.iloc[0]["top10_lift"])
    null_rows = []
    y_all = actions["actual_gain"].to_numpy(dtype=np.float64)
    for i in range(500):
        yp = rng.permutation(y_all)
        null_rows.append(
            {
                "perm": i,
                "spearman": spearman(yp, pred),
                "top10_lift": float(yp[pred >= np.quantile(pred, 0.90)].mean() - yp.mean()),
            }
        )
    null = pd.DataFrame(null_rows)
    stress.attrs["perm_spearman_p"] = float(np.mean(null["spearman"].to_numpy(dtype=np.float64) >= real_rho))
    stress.attrs["perm_lift_p"] = float(np.mean(null["top10_lift"].to_numpy(dtype=np.float64) >= real_lift))
    null.to_csv(OUT / "h025_action_health_permutation_null.csv", index=False)
    return stress, oof


def collect_candidate_pool() -> pd.DataFrame:
    if H024_POOL.exists():
        pool = pd.read_csv(H024_POOL)
    else:
        pool = pd.DataFrame(columns=["file", "resolved_path", "source"])
    extras = [
        H012,
        "submission_h015_self_feedback_top_all_k1600_a0.7_uploadsafe.csv",
        "submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv",
        "submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv",
    ]
    rows = pool.to_dict("records")
    for file_name in extras:
        path = locate(file_name)
        if path is not None:
            rows.append({"file": file_name, "resolved_path": str(path), "source": "h025_extra"})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["path_key"] = out.apply(lambda r: str(locate(r.get("resolved_path", r.get("file", ""))) or locate(r.get("file", "")) or r.get("resolved_path", "")), axis=1)
    out = out.drop_duplicates("path_key", keep="first")
    return out.drop(columns=["path_key"]).reset_index(drop=True)


def candidate_action_features(candidate_file: str | Path, h012_prob: np.ndarray, test_pcs: np.ndarray, sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    cand = load_sub(candidate_file, sample)
    q = cand[TARGETS].to_numpy(dtype=np.float64)
    feat = action_feature_frame(test_pcs, h012_prob, q, alpha=1.0, row_ids=np.arange(len(test_pcs)), family="candidate")
    return feat, q


def score_candidates(
    model: ExtraTreesRegressor,
    cols: list[str],
    pool: pd.DataFrame,
    h012_prob: np.ndarray,
    test_pcs: np.ndarray,
    sample: pd.DataFrame,
    train_actions: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    h024_pred = pd.read_csv(H024_PUBLIC_PRED) if H024_PUBLIC_PRED.exists() else pd.DataFrame()
    rows = []
    cell_parts = []
    train_abs_delta_p95 = float(np.quantile(train_actions["abs_delta_logit"].to_numpy(dtype=np.float64), 0.95))
    for rec in pool.to_dict("records"):
        file_name = str(rec.get("file", rec.get("resolved_path", "")))
        path = locate(rec.get("resolved_path", file_name)) or locate(file_name)
        if path is None:
            continue
        try:
            feat, q = candidate_action_features(path, h012_prob, test_pcs, sample)
        except Exception:
            continue
        pred = model.predict(feat[cols])
        feat_small = feat[["row_id", "target", "target_i", "delta_prob", "abs_delta_prob", "delta_logit", "abs_delta_logit"]].copy()
        feat_small["file"] = file_name
        feat_small["pred_gain"] = pred
        moved = feat_small["abs_delta_prob"].to_numpy(dtype=np.float64) > 1.0e-6
        if moved.sum() == 0:
            moved = np.ones(len(feat_small), dtype=bool)
        moved_idx = np.flatnonzero(moved)
        rank = moved_idx[np.argsort(-pred[moved_idx])]
        top_k = min(1200, int(moved.sum()))
        top_idx = rank[:top_k]
        pred_moved = pred[moved]
        row = {
            "file": file_name,
            "resolved_path": str(path),
            "source": rec.get("source", rec.get("pool_source", "")),
            "changed_cells": int(np.sum(feat_small["abs_delta_prob"].to_numpy(dtype=np.float64) > 1.0e-6)),
            "changed_rows": int(feat_small.loc[feat_small["abs_delta_prob"] > 1.0e-6].groupby("row_id").size().shape[0]),
            "pred_gain_sum_moved": float(np.sum(pred_moved)),
            "pred_gain_mean_moved": float(np.mean(pred_moved)),
            "pred_gain_top1200_sum": float(np.sum(pred[top_idx])),
            "pred_gain_top1200_mean": float(np.mean(pred[top_idx])),
            "pred_positive_rate_moved": float(np.mean(pred_moved > 0.0)),
            "mean_abs_delta_prob": float(feat_small["abs_delta_prob"].mean()),
            "max_abs_delta_prob": float(feat_small["abs_delta_prob"].max()),
            "ood_abs_delta_rate": float(np.mean(feat_small["abs_delta_logit"].to_numpy(dtype=np.float64) > train_abs_delta_p95)),
        }
        if not h024_pred.empty and "file" in h024_pred.columns:
            hp = h024_pred[h024_pred["file"] == file_name]
            if hp.empty:
                hp = h024_pred[h024_pred["resolved_path"].astype(str) == str(path)]
            if len(hp):
                for col in ["pred_public_median", "pred_public_p10", "pred_public_p90", "support_better_than_h012", "decoder_score", "bad_to_good_load_ratio"]:
                    if col in hp.columns:
                        row[f"h024_{col}"] = float(hp.iloc[0][col])
        rows.append(row)
        # Keep cells only for plausible top candidates to avoid very large files.
        if len(rows) <= 60:
            cell_parts.append(feat_small.sort_values("pred_gain", ascending=False).head(1400))
    scores = pd.DataFrame(rows)
    if scores.empty:
        return scores, pd.DataFrame()
    scores["h025_score"] = (
        -scores["pred_gain_top1200_sum"]
        + 0.025 * scores["ood_abs_delta_rate"]
        + 0.002 * scores.get("h024_bad_to_good_load_ratio", pd.Series(0.0, index=scores.index)).fillna(0.0)
    )
    scores = scores.sort_values(["h025_score", "pred_gain_top1200_sum"], ascending=[True, False]).reset_index(drop=True)
    cells = pd.concat(cell_parts, ignore_index=True) if cell_parts else pd.DataFrame()
    return scores, cells


def row_permutation_candidate_stress(
    model: ExtraTreesRegressor,
    cols: list[str],
    selected_file: str,
    h012_prob: np.ndarray,
    test_pcs: np.ndarray,
    sample: pd.DataFrame,
    n_perm: int = 300,
) -> pd.DataFrame:
    rng = np.random.default_rng(20260603)
    feat, _ = candidate_action_features(selected_file, h012_prob, test_pcs, sample)
    real_pred = model.predict(feat[cols])
    moved = feat["abs_delta_prob"].to_numpy(dtype=np.float64) > 1.0e-6
    moved_idx = np.flatnonzero(moved)
    if len(moved_idx) == 0:
        moved_idx = np.arange(len(feat))
    top_k = min(1200, len(moved_idx))
    real_top = np.sort(real_pred[moved_idx])[-top_k:].sum()
    pc_cols = [c for c in feat.columns if c.startswith("pc")]
    rows = []
    for i in range(n_perm):
        f = feat.copy()
        perm = rng.permutation(test_pcs.shape[0])
        for j, col in enumerate(pc_cols):
            vals = np.repeat(test_pcs[perm, j], len(TARGETS))
            f[col] = vals
        pred = model.predict(f[cols])
        perm_top = np.sort(pred[moved_idx])[-top_k:].sum()
        rows.append(
            {
                "perm": i,
                "real_top1200_sum": float(real_top),
                "perm_top1200_sum": float(perm_top),
                "real_minus_perm": float(real_top - perm_top),
            }
        )
    return pd.DataFrame(rows)


def materialize_candidate(
    selected: pd.Series,
    model: ExtraTreesRegressor,
    cols: list[str],
    h012: pd.DataFrame,
    h012_prob: np.ndarray,
    test_pcs: np.ndarray,
    sample: pd.DataFrame,
    top_k: int = 1200,
) -> Path:
    feat, q = candidate_action_features(str(selected["resolved_path"]), h012_prob, test_pcs, sample)
    pred = model.predict(feat[cols])
    out_prob = h012_prob.copy()
    moved = feat["abs_delta_prob"].to_numpy(dtype=np.float64) > 1.0e-6
    moved_idx = np.flatnonzero(moved)
    if len(moved_idx) == 0:
        moved_idx = np.arange(len(feat))
    cell_order = moved_idx[np.argsort(-pred[moved_idx])]
    chosen = cell_order[: min(top_k, len(cell_order))]
    for flat_idx in chosen:
        row = int(feat.iloc[flat_idx]["row_id"])
        target_i = int(feat.iloc[flat_idx]["target_i"])
        if pred[flat_idx] > 0:
            out_prob[row, target_i] = q[row, target_i]
    out = h012.copy()
    out[TARGETS] = clip_prob(out_prob)
    digest = short_hash(out)
    name = ROOT / f"submission_h025_train_actionhealth_top{top_k}_{digest}_uploadsafe.csv"
    out.to_csv(name, index=False)
    return name


def write_report(
    base_scores: pd.DataFrame,
    proposal_summary: pd.DataFrame,
    stress: pd.DataFrame,
    candidate_scores: pd.DataFrame,
    null_df: pd.DataFrame,
    decision: str,
    promoted_path: Path | None,
) -> None:
    lines = []
    lines.append("# H025 Train-Counterfactual Action-Health JEPA\n")
    lines.append("## Question\n")
    lines.append(
        "Can HS-JEPA learn action health from train labels by generating counterfactual probability moves, "
        "then use that independent supervision to select post-H012 test actions without regressing public LB?\n"
    )
    lines.append("## Base model\n")
    lines.append(md_table(base_scores, 12) + "\n")
    lines.append("## Proposal families\n")
    lines.append(md_table(proposal_summary, 16) + "\n")
    lines.append("## Action-health stress\n")
    lines.append(md_table(stress, 24) + "\n")
    if len(stress):
        overall = stress[stress["stress"] == "row_time_fold_overall"]
        if len(overall):
            lines.append(
                f"- row/time OOF Spearman: `{float(overall.iloc[0]['spearman']):.9f}`; "
                f"top10 lift: `{float(overall.iloc[0]['top10_lift']):.9f}`\n"
            )
    lines.append("## Candidate ranking\n")
    lines.append(md_table(candidate_scores.head(20), 20) + "\n")
    if not null_df.empty:
        p = float(np.mean(null_df["perm_top1200_sum"].to_numpy(dtype=np.float64) >= null_df["real_top1200_sum"].iloc[0]))
        lines.append(
            f"- selected row-permutation p(higher top1200 gain): `{p:.9f}`; "
            f"real top1200 sum `{float(null_df['real_top1200_sum'].iloc[0]):.9f}`\n"
        )
    lines.append("## Decision\n")
    lines.append(f"- decision: `{decision}`\n")
    lines.append(f"- promoted path: `{promoted_path if promoted_path is not None else 'none'}`\n")
    lines.append(
        "\nInterpretation: H025 is independent action-health supervision. "
        "It promotes a submission only if train-counterfactual action health transfers across row-time folds, across proposal families, and beats row-permuted test-state controls.\n"
    )
    (OUT / "h025_report.md").write_text("".join(lines))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    features = pd.read_csv(FEATURES_IN, parse_dates=["sleep_date", "lifelog_date"])
    features = features.sort_values(["split", "subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    train_mask = features["split"].eq("train").to_numpy()
    test_mask = features["split"].eq("test").to_numpy()
    train_idx = np.flatnonzero(train_mask)
    test_idx = np.flatnonzero(test_mask)
    train = features.iloc[train_idx].reset_index(drop=True)
    test = features.iloc[test_idx].reset_index(drop=True)
    train_y = train[TARGETS].to_numpy(dtype=np.float64)

    groups = feature_groups(features)
    z_by_group = {name: standardized_matrix(features, cols, train_mask) for name, cols in groups.items()}
    z_all = z_by_group["all"]
    pca = PCA(n_components=16, random_state=2525)
    pcs_all = pca.fit_transform(z_all[train_idx])
    pcs_test = pca.transform(z_all[test_idx])
    folds = make_subject_time_folds(train, n_folds=5)

    base_oof, base_test, base_scores = fit_oof_base(z_all, train_idx, test_idx, train_y, folds)
    base_scores.to_csv(OUT / "h025_base_oof_scores.csv", index=False)
    pd.DataFrame(base_oof, columns=TARGETS).to_csv(OUT / "h025_train_base_oof.csv", index=False)
    pd.DataFrame(base_test, columns=TARGETS).to_csv(OUT / "h025_test_base_model.csv", index=False)

    proposals_train, proposals_test, proposal_summary = build_proposals(features, z_by_group, train_idx, test_idx, train_y, folds)
    proposal_summary.to_csv(OUT / "h025_proposal_summary.csv", index=False)
    for name, arr in proposals_test.items():
        pd.DataFrame(arr, columns=TARGETS).to_csv(OUT / f"h025_test_proposal_{safe_id(name)}.csv", index=False)

    actions = build_action_training_set(pcs_all, base_oof, proposals_train, train_y, folds)
    actions.to_csv(OUT / "h025_train_counterfactual_actions.csv", index=False)
    cols = action_feature_cols(actions)
    pd.Series(cols, name="feature").to_csv(OUT / "h025_action_feature_columns.csv", index=False)

    stress, oof = evaluate_action_health(actions, cols)
    stress.to_csv(OUT / "h025_action_health_stress.csv", index=False)
    oof.to_csv(OUT / "h025_action_health_oof_predictions.csv", index=False)

    model = fit_action_model(actions[cols], actions["actual_gain"].to_numpy(dtype=np.float64), seed=9000)
    h012 = load_sub(H012)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    sample = h012[KEYS].copy()
    test_for_sample = test.sort_values(KEYS).reset_index(drop=True)
    # Reorder PCA rows to match submission sample order.
    test_pcs_df = test[KEYS].copy()
    for j in range(pcs_test.shape[1]):
        test_pcs_df[f"pc{j:02d}"] = pcs_test[:, j]
    test_pcs_df = sample.merge(test_pcs_df, on=KEYS, how="left")
    if test_pcs_df[[f"pc{j:02d}" for j in range(pcs_test.shape[1])]].isna().any().any():
        raise ValueError("test PCA rows do not align to H012 sample")
    test_pcs_ordered = test_pcs_df[[f"pc{j:02d}" for j in range(pcs_test.shape[1])]].to_numpy(dtype=np.float64)

    pool = collect_candidate_pool()
    pool.to_csv(OUT / "h025_candidate_pool.csv", index=False)
    candidate_scores, candidate_cells = score_candidates(model, cols, pool, h012_prob, test_pcs_ordered, sample, actions)
    candidate_scores.to_csv(OUT / "h025_candidate_scores.csv", index=False)
    candidate_cells.to_csv(OUT / "h025_top_candidate_cells.csv", index=False)

    known_public = set(pd.read_csv(ANALYSIS / "public_probe_observations.csv")["file"]) if (ANALYSIS / "public_probe_observations.csv").exists() else set()
    unknown = candidate_scores[~candidate_scores["file"].isin(known_public)].copy()
    selected = unknown.iloc[0] if len(unknown) else candidate_scores.iloc[0]
    null_df = row_permutation_candidate_stress(model, cols, str(selected["resolved_path"]), h012_prob, test_pcs_ordered, sample, n_perm=300)
    null_df.to_csv(OUT / "h025_selected_rowperm_stress.csv", index=False)

    overall = stress[stress["stress"] == "row_time_fold_overall"].iloc[0]
    fam = stress[stress["stress"] == "leave_family_out"].copy()
    rowperm_p = float(np.mean(null_df["perm_top1200_sum"].to_numpy(dtype=np.float64) >= null_df["real_top1200_sum"].iloc[0]))
    median_fam_spearman = float(fam["spearman"].median()) if len(fam) else -1.0
    median_fam_lift = float(fam["top10_lift"].median()) if len(fam) else -1.0
    gate_ok = (
        float(overall["spearman"]) > 0.08
        and float(overall["top10_lift"]) > 0.001
        and median_fam_spearman > 0.02
        and median_fam_lift > 0.0002
        and rowperm_p <= 0.05
        and float(selected["pred_gain_top1200_sum"]) > 0.0
        and float(selected["ood_abs_delta_rate"]) < 0.35
    )
    promoted_path = materialize_candidate(selected, model, cols, h012, h012_prob, test_pcs_ordered, sample, top_k=1200) if gate_ok else None
    decision = "primary_train_counterfactual_action" if gate_ok else "diagnostic_only_action_health_not_transfer_safe"
    decision_df = pd.DataFrame(
        [
            {
                "decision": decision,
                "selected_file": selected["file"],
                "selected_resolved_path": selected["resolved_path"],
                "promoted_path": None if promoted_path is None else str(promoted_path),
                "rowperm_p": rowperm_p,
                "overall_spearman": float(overall["spearman"]),
                "overall_top10_lift": float(overall["top10_lift"]),
                "median_leave_family_spearman": median_fam_spearman,
                "median_leave_family_top10_lift": median_fam_lift,
            }
        ]
    )
    decision_df.to_csv(OUT / "h025_decision.csv", index=False)
    write_report(base_scores, proposal_summary, stress, candidate_scores, null_df, decision, promoted_path)
    print(decision_df.to_string(index=False))
    print(candidate_scores.head(15)[["file", "pred_gain_top1200_sum", "pred_gain_top1200_mean", "pred_positive_rate_moved", "ood_abs_delta_rate", "h025_score"]].to_string(index=False))


if __name__ == "__main__":
    main()
