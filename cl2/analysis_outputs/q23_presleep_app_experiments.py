from __future__ import annotations

import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import normalize

sys.path.append(str(Path(__file__).resolve().parent))
import calibration_experiments as cal  # noqa: E402
import deep_dive_analysis as d  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
OUT = ROOT / "analysis_outputs"
TARGETS = d.TARGETS
Q_TARGETS = ["Q2", "Q3"]
KEY = d.KEY

WINDOWS = {
    "aft_12_18": (12, 18),
    "eve_18_21": (18, 21),
    "pre_21_24": (21, 24),
    "mid_24_26": (24, 26),
    "late_18_26": (18, 26),
    "sleep_22_26": (22, 26),
    "awake_06_12": (6, 12),
}

CATEGORY_PATTERNS = {
    "chat": ["카카오톡", "메시지", "messenger", "line", "whatsapp", "telegram", "threads"],
    "call": ["전화", "통화", "t전화"],
    "search": ["naver", "chrome", "google", "삼성 인터넷", "safari", "네이트"],
    "video": ["youtube", "netflix", "tiktok", "동영상", "웹툰", "reels"],
    "music": ["music", "멜론", "spotify", "flo", "youtube music"],
    "finance": ["토스", "kb", "카카오뱅크", "뱅크", "증권", "pay"],
    "shopping": ["쿠팡", "당근", "11번가", "g마켓", "auction", "배달"],
    "game": ["game", "게임", "royal", "클래시", "number match"],
    "health": ["health", "fit", "캐시워크", "타임스프레드", "만보기"],
    "home": ["one ui 홈", "launcher", "시스템 ui"],
}


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1 - 1e-5)


def q_loss(y: np.ndarray, pred: np.ndarray, target: str) -> float:
    j = Q_TARGETS.index(target)
    return float(log_loss(y[:, j], clip(pred[:, j]), labels=[0, 1]))


def mean_q_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([q_loss(y, pred, target) for target in Q_TARGETS]))


def clean_app_name(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).strip().lower()
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text or "unknown"


def app_categories(app: str) -> list[str]:
    return [name for name, pats in CATEGORY_PATTERNS.items() if any(pat.lower() in app for pat in pats)]


def read_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEY).reset_index(drop=True)
    sub = sub.sort_values(KEY).reset_index(drop=True)
    return train, sub


def row_key(row: pd.Series) -> tuple[str, pd.Timestamp]:
    return str(row["subject_id"]), pd.Timestamp(row["lifelog_date"]).normalize()


def usage_record_night_hour(ts: pd.Timestamp) -> tuple[pd.Timestamp, int]:
    hour = int(ts.hour)
    base = ts.normalize()
    if hour < 6:
        return base - pd.Timedelta(days=1), hour + 24
    return base, hour


@dataclass
class AppFeatureStore:
    dicts: dict[tuple[str, pd.Timestamp], dict[str, float]]
    app_sets: dict[tuple[str, pd.Timestamp], set[str]]
    window_app_sets: dict[tuple[str, pd.Timestamp], dict[str, set[str]]]
    summaries: pd.DataFrame
    top_apps: pd.DataFrame


def build_app_feature_store(all_keys: pd.DataFrame) -> AppFeatureStore:
    keys = {(str(r.subject_id), pd.Timestamp(r.lifelog_date).normalize()) for r in all_keys.itertuples(index=False)}
    feature_dicts: dict[tuple[str, pd.Timestamp], dict[str, float]] = {key: {} for key in keys}
    window_app_sets: dict[tuple[str, pd.Timestamp], dict[str, set[str]]] = {
        key: {win: set() for win in WINDOWS} for key in keys
    }
    raw_times: dict[tuple[str, pd.Timestamp], dict[str, list[float]]] = {
        key: {win: [] for win in WINDOWS} for key in keys
    }
    top_counter: Counter[str] = Counter()
    top_time: Counter[str] = Counter()

    df = pd.read_parquet(ITEMS / "ch2025_mUsageStats.parquet")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for rec in df.itertuples(index=False):
        day, night_hour = usage_record_night_hour(pd.Timestamp(rec.timestamp))
        key = (str(rec.subject_id), day)
        if key not in feature_dicts:
            continue
        wins = [name for name, (lo, hi) in WINDOWS.items() if lo <= night_hour < hi]
        if not wins:
            continue
        stats = rec.m_usage_stats
        if not hasattr(stats, "__iter__"):
            continue
        for item in stats:
            if not isinstance(item, dict):
                continue
            app = clean_app_name(item.get("app_name"))
            try:
                total = float(item.get("total_time") or 0.0)
            except Exception:
                total = 0.0
            if not math.isfinite(total) or total < 0:
                total = 0.0
            value = math.log1p(min(total, 24 * 60 * 60 * 1000))
            top_counter[app] += 1
            top_time[app] += total
            cats = app_categories(app)
            for win in wins:
                fd = feature_dicts[key]
                fd[f"app_time:{win}:{app}"] = fd.get(f"app_time:{win}:{app}", 0.0) + value
                fd[f"app_seen:{win}:{app}"] = fd.get(f"app_seen:{win}:{app}", 0.0) + 1.0
                fd[f"window_total:{win}"] = fd.get(f"window_total:{win}", 0.0) + value
                fd[f"window_items:{win}"] = fd.get(f"window_items:{win}", 0.0) + 1.0
                fd[f"window_peak:{win}"] = max(fd.get(f"window_peak:{win}", 0.0), value)
                for cat in cats:
                    fd[f"cat_time:{win}:{cat}"] = fd.get(f"cat_time:{win}:{cat}", 0.0) + value
                    fd[f"cat_seen:{win}:{cat}"] = fd.get(f"cat_seen:{win}:{cat}", 0.0) + 1.0
                window_app_sets[key][win].add(app)
                raw_times[key][win].append(value)

    rows = []
    for key, win_sets in window_app_sets.items():
        sid, day = key
        fd = feature_dicts[key]
        fd[f"sid:{sid}"] = 1.0
        fd[f"dow:{day.dayofweek}"] = 1.0
        fd[f"month:{day.month}"] = 1.0
        all_apps = set()
        row = {"subject_id": sid, "lifelog_date": day}
        for win, apps in win_sets.items():
            all_apps.update(apps)
            vals = np.array(raw_times[key][win], dtype=float)
            row[f"{win}_unique_apps"] = float(len(apps))
            row[f"{win}_events"] = float(len(vals))
            row[f"{win}_log_time_sum"] = float(vals.sum()) if len(vals) else 0.0
            row[f"{win}_log_time_max"] = float(vals.max()) if len(vals) else 0.0
            if len(vals) and vals.sum() > 0:
                p = vals / vals.sum()
                row[f"{win}_entropy"] = float(-(p * np.log(p + 1e-12)).sum())
                row[f"{win}_top_share"] = float(vals.max() / vals.sum())
            else:
                row[f"{win}_entropy"] = 0.0
                row[f"{win}_top_share"] = 0.0
            for col in [
                f"{win}_unique_apps",
                f"{win}_events",
                f"{win}_log_time_sum",
                f"{win}_log_time_max",
                f"{win}_entropy",
                f"{win}_top_share",
            ]:
                fd[f"summary:{col}"] = row[col]
        row["all_unique_apps"] = float(len(all_apps))
        rows.append(row)

    top_apps = (
        pd.DataFrame(
            [{"app": app, "count": top_counter[app], "total_time": float(top_time[app])} for app in top_counter]
        )
        .sort_values(["total_time", "count"], ascending=False)
        .reset_index(drop=True)
    )
    summaries = pd.DataFrame(rows)
    return AppFeatureStore(
        dicts=feature_dicts,
        app_sets={key: set().union(*wins.values()) for key, wins in window_app_sets.items()},
        window_app_sets=window_app_sets,
        summaries=summaries,
        top_apps=top_apps,
    )


def dicts_for_rows(rows: pd.DataFrame, store: AppFeatureStore) -> list[dict[str, float]]:
    out = []
    min_day = rows.groupby("subject_id")["lifelog_date"].transform("min")
    for i, row in rows.reset_index(drop=True).iterrows():
        key = row_key(row)
        fd = dict(store.dicts.get(key, {}))
        fd[f"split_sid:{row['subject_id']}"] = 1.0
        fd[f"split_dow:{int(row['lifelog_date'].dayofweek)}"] = 1.0
        fd["subject_day_index"] = float((row["lifelog_date"] - min_day.iloc[i]).days)
        out.append(fd)
    return out


def app_tokens_for_rows(rows: pd.DataFrame, store: AppFeatureStore, scoped: bool) -> list[dict[str, float]]:
    dicts = []
    for _, row in rows.reset_index(drop=True).iterrows():
        key = row_key(row)
        sid = str(row["subject_id"])
        toks: dict[str, float] = {}
        for win in ["pre_21_24", "late_18_26", "sleep_22_26", "mid_24_26"]:
            for app in store.window_app_sets.get(key, {}).get(win, set()):
                if scoped:
                    toks[f"{sid}|{win}|{app}"] = 1.0
                else:
                    toks[f"{win}|{app}"] = 1.0
        dicts.append(toks)
    return dicts


def fit_logreg_predict(
    train_rows: pd.DataFrame,
    val_rows: pd.DataFrame,
    store: AppFeatureStore,
    target: str,
    c_value: float,
) -> np.ndarray:
    vec = DictVectorizer(sparse=True)
    x_train = vec.fit_transform(dicts_for_rows(train_rows, store))
    x_val = vec.transform(dicts_for_rows(val_rows, store))
    y = train_rows[target].to_numpy(dtype=int)
    if len(np.unique(y)) < 2:
        return np.full(len(val_rows), float(y.mean()) if len(y) else 0.5)
    clf = LogisticRegression(
        C=c_value,
        solver="liblinear",
        max_iter=2000,
        class_weight="balanced",
        random_state=17,
    )
    clf.fit(x_train, y)
    return clip(clf.predict_proba(x_val)[:, 1])


def fit_app_te_predict(
    train_rows: pd.DataFrame,
    val_rows: pd.DataFrame,
    store: AppFeatureStore,
    target: str,
    shrink: float,
    scoped: bool,
) -> np.ndarray:
    train_tokens = app_tokens_for_rows(train_rows, store, scoped=scoped)
    val_tokens = app_tokens_for_rows(val_rows, store, scoped=scoped)
    y = train_rows[target].to_numpy(dtype=float)
    prior = float(np.mean(y)) if len(y) else 0.5
    sums: defaultdict[str, float] = defaultdict(float)
    counts: defaultdict[str, float] = defaultdict(float)
    for toks, label in zip(train_tokens, y, strict=False):
        for token, weight in toks.items():
            sums[token] += weight * label
            counts[token] += weight
    out = []
    for toks in val_tokens:
        numer = shrink * prior
        denom = shrink
        for token, weight in toks.items():
            if counts[token] <= 0:
                continue
            token_rate = (sums[token] + shrink * prior) / (counts[token] + shrink)
            numer += weight * token_rate
            denom += weight
        out.append(numer / denom if denom else prior)
    return clip(np.asarray(out, dtype=float))


def fit_knn_predict(
    train_rows: pd.DataFrame,
    val_rows: pd.DataFrame,
    store: AppFeatureStore,
    target: str,
    k: int,
    scoped: bool,
) -> np.ndarray:
    train_dicts = app_tokens_for_rows(train_rows, store, scoped=scoped)
    val_dicts = app_tokens_for_rows(val_rows, store, scoped=scoped)
    vec = DictVectorizer(sparse=True)
    x_train = normalize(vec.fit_transform(train_dicts), norm="l2")
    x_val = normalize(vec.transform(val_dicts), norm="l2")
    y = train_rows[target].to_numpy(dtype=float)
    prior = float(np.mean(y)) if len(y) else 0.5
    if x_train.shape[0] == 0:
        return np.full(len(val_rows), prior)
    sim = x_val @ x_train.T
    if sparse.issparse(sim):
        sim = sim.toarray()
    out = []
    for i in range(sim.shape[0]):
        row = sim[i]
        if scoped:
            same = train_rows["subject_id"].to_numpy() == val_rows.iloc[i]["subject_id"]
            candidate_idx = np.where(same)[0]
        else:
            candidate_idx = np.arange(len(train_rows))
        if len(candidate_idx) == 0 or float(row[candidate_idx].max(initial=0.0)) <= 0:
            out.append(prior)
            continue
        cand_scores = row[candidate_idx]
        order = np.argsort(cand_scores)[::-1][:k]
        idx = candidate_idx[order]
        weights = row[idx]
        if float(weights.sum()) <= 0:
            out.append(prior)
        else:
            out.append((float(np.dot(weights, y[idx])) + 1.5 * prior) / (float(weights.sum()) + 1.5))
    return clip(np.asarray(out, dtype=float))


@dataclass(frozen=True)
class Candidate:
    name: str
    method: str
    param: float
    scoped: bool = False


CANDIDATES = [
    Candidate("logreg_c0.03", "logreg", 0.03),
    Candidate("logreg_c0.08", "logreg", 0.08),
    Candidate("logreg_c0.20", "logreg", 0.20),
    Candidate("te_global_s2", "te", 2.0),
    Candidate("te_global_s6", "te", 6.0),
    Candidate("te_subject_s2", "te", 2.0, scoped=True),
    Candidate("te_subject_s6", "te", 6.0, scoped=True),
    Candidate("knn_global_k5", "knn", 5.0),
    Candidate("knn_global_k9", "knn", 9.0),
    Candidate("knn_subject_k3", "knn", 3.0, scoped=True),
    Candidate("knn_subject_k5", "knn", 5.0, scoped=True),
]

BLEND_GRID = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60, 0.80, 1.0]


def fit_candidate(
    train_rows: pd.DataFrame,
    val_rows: pd.DataFrame,
    store: AppFeatureStore,
    target: str,
    cand: Candidate,
) -> np.ndarray:
    if cand.method == "logreg":
        return fit_logreg_predict(train_rows, val_rows, store, target, cand.param)
    if cand.method == "te":
        return fit_app_te_predict(train_rows, val_rows, store, target, cand.param, scoped=cand.scoped)
    if cand.method == "knn":
        return fit_knn_predict(train_rows, val_rows, store, target, int(cand.param), scoped=cand.scoped)
    raise ValueError(cand.method)


def candidate_oof(
    train_rows: pd.DataFrame,
    folds: list[tuple[np.ndarray, np.ndarray]],
    store: AppFeatureStore,
    cand: Candidate,
) -> np.ndarray:
    pred = np.zeros((len(train_rows), len(Q_TARGETS)), dtype=float)
    for tr_idx, val_idx in folds:
        tr = train_rows.iloc[tr_idx].copy().reset_index(drop=True)
        val = train_rows.iloc[val_idx].copy().reset_index(drop=True)
        for j, target in enumerate(Q_TARGETS):
            pred[val_idx, j] = fit_candidate(tr, val, store, target, cand)
    return clip(pred)


def choose_candidate(
    train_rows: pd.DataFrame,
    base_pred: np.ndarray,
    app_preds: dict[str, np.ndarray],
) -> dict[str, tuple[str, float, float]]:
    y = train_rows[Q_TARGETS].to_numpy(dtype=int)
    choices: dict[str, tuple[str, float, float]] = {}
    for j, target in enumerate(Q_TARGETS):
        best = ("base", 0.0, log_loss(y[:, j], clip(base_pred[:, j]), labels=[0, 1]))
        for name, pred in app_preds.items():
            for weight in BLEND_GRID:
                blended = (1 - weight) * base_pred[:, j] + weight * pred[:, j]
                loss = log_loss(y[:, j], clip(blended), labels=[0, 1])
                if loss < best[2] - 1e-12:
                    best = (name, weight, float(loss))
        choices[target] = best
    return choices


def apply_choices(
    train_rows: pd.DataFrame,
    val_rows: pd.DataFrame,
    store: AppFeatureStore,
    base_val: np.ndarray,
    choices: dict[str, tuple[str, float, float]],
) -> np.ndarray:
    out = base_val.copy()
    cand_cache: dict[tuple[str, str], np.ndarray] = {}
    cand_by_name = {c.name: c for c in CANDIDATES}
    for j, target in enumerate(Q_TARGETS):
        cand_name, weight, _ = choices[target]
        if cand_name == "base" or weight <= 0:
            continue
        key = (cand_name, target)
        if key not in cand_cache:
            cand_cache[key] = fit_candidate(train_rows, val_rows, store, target, cand_by_name[cand_name])
        out[:, j] = (1 - weight) * base_val[:, j] + weight * cand_cache[key]
    return clip(out)


def nested_experiment(train: pd.DataFrame, store: AppFeatureStore) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    y = train[Q_TARGETS].to_numpy(dtype=int)
    outer_folds = d.make_folds(train, "subject_blocks")
    base_outer = np.zeros((len(train), len(Q_TARGETS)), dtype=float)
    nested_pred = np.zeros_like(base_outer)
    selected_rows = []

    for outer_id, (tr_idx, val_idx) in enumerate(outer_folds):
        outer_train = train.iloc[tr_idx].copy().reset_index(drop=True)
        outer_val = train.iloc[val_idx].copy().reset_index(drop=True)
        inner_folds = d.make_folds(outer_train, "subject_blocks")
        inner_base_all = cal.base_oof(outer_train, inner_folds)
        inner_base = inner_base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
        app_preds = {}
        for cand in CANDIDATES:
            app_preds[cand.name] = candidate_oof(outer_train, inner_folds, store, cand)
        choices = choose_candidate(outer_train, inner_base, app_preds)

        outer_base_all = cal.temporal_base(outer_train, outer_val)
        outer_base = outer_base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
        base_outer[val_idx] = outer_base
        nested_pred[val_idx] = apply_choices(outer_train, outer_val, store, outer_base, choices)
        for target, (cand_name, weight, inner_loss) in choices.items():
            selected_rows.append(
                {
                    "outer_fold": outer_id,
                    "target": target,
                    "candidate": cand_name,
                    "weight": weight,
                    "inner_loss": inner_loss,
                }
            )
        print(f"[q23 app] outer {outer_id} choices={choices}", flush=True)

    rows = []
    for name, pred in [("temporal_base", base_outer), ("nested_q23_app", nested_pred)]:
        row = {"model": name, "mean_q23": mean_q_loss(y, pred)}
        for target in Q_TARGETS:
            row[target] = q_loss(y, pred, target)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mean_q23"), pd.DataFrame(selected_rows), nested_pred


def full_train_choices(train: pd.DataFrame, store: AppFeatureStore) -> tuple[pd.DataFrame, dict[str, tuple[str, float, float]]]:
    folds = d.make_folds(train, "subject_blocks")
    base_all = cal.base_oof(train, folds)
    base = base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
    app_preds = {}
    rows = []
    y = train[Q_TARGETS].to_numpy(dtype=int)
    for cand in CANDIDATES:
        pred = candidate_oof(train, folds, store, cand)
        app_preds[cand.name] = pred
        row = {"candidate": cand.name, "mean_q23": mean_q_loss(y, pred)}
        for target in Q_TARGETS:
            row[target] = q_loss(y, pred, target)
        rows.append(row)
    rows.append({"candidate": "temporal_base", "mean_q23": mean_q_loss(y, base), "Q2": q_loss(y, base, "Q2"), "Q3": q_loss(y, base, "Q3")})
    choices = choose_candidate(train, base, app_preds)
    return pd.DataFrame(rows).sort_values("mean_q23"), choices


def make_submission(train: pd.DataFrame, sub: pd.DataFrame, store: AppFeatureStore, choices: dict[str, tuple[str, float, float]]) -> pd.DataFrame:
    if (OUT / "submission_hybrid_overnight_context.csv").exists():
        out = pd.read_csv(OUT / "submission_hybrid_overnight_context.csv", parse_dates=["sleep_date", "lifelog_date"])
        out = out.sort_values(KEY).reset_index(drop=True)
    else:
        out = sub[["subject_id", "sleep_date", "lifelog_date"] + TARGETS].copy()
    base_all = cal.temporal_base(train, sub)
    base = base_all[:, [TARGETS.index(t) for t in Q_TARGETS]]
    q_pred = apply_choices(train, sub, store, base, choices)
    for j, target in enumerate(Q_TARGETS):
        out[target] = q_pred[:, j]
    return out


def main() -> None:
    train, sub = read_rows()
    all_keys = pd.concat([train[KEY], sub[KEY]], ignore_index=True)
    store = build_app_feature_store(all_keys)
    store.top_apps.to_csv(OUT / "q23_presleep_app_top_apps.csv", index=False)
    store.summaries.to_csv(OUT / "q23_presleep_app_summaries.csv", index=False)

    nested, selected, nested_pred = nested_experiment(train, store)
    nested.to_csv(OUT / "q23_presleep_app_nested_results.csv", index=False)
    selected.to_csv(OUT / "q23_presleep_app_nested_selected.csv", index=False)

    candidate_results, choices = full_train_choices(train, store)
    candidate_results.to_csv(OUT / "q23_presleep_app_candidate_results.csv", index=False)
    pd.DataFrame(
        [
            {"target": target, "candidate": cand, "weight": weight, "inner_loss": loss}
            for target, (cand, weight, loss) in choices.items()
        ]
    ).to_csv(OUT / "q23_presleep_app_full_choices.csv", index=False)

    submission = make_submission(train, sub, store, choices)
    submission.to_csv(OUT / "submission_q23_presleep_app.csv", index=False)

    old_q2 = 0.6927101523541841
    old_q3 = 0.6622200100969644
    old_mean = 0.6049114285714285
    nested_row = nested[nested["model"] == "nested_q23_app"].iloc[0]
    est_mean = old_mean - ((old_q2 + old_q3) - (float(nested_row["Q2"]) + float(nested_row["Q3"]))) / 7.0
    pd.DataFrame(
        [
            {"target": "Q2", "old_loss": old_q2, "new_loss": float(nested_row["Q2"])},
            {"target": "Q3", "old_loss": old_q3, "new_loss": float(nested_row["Q3"])},
            {"target": "mean", "old_loss": old_mean, "new_loss": float(est_mean)},
        ]
    ).to_csv(OUT / "q23_presleep_app_hybrid_estimate.csv", index=False)

    print("\nNested Q2/Q3 app experiment")
    print(nested.round(6).to_string(index=False))
    print("\nFull-train candidate OOF")
    print(candidate_results.head(20).round(6).to_string(index=False))
    print("\nFull-train choices")
    print(choices)
    print("\nHybrid context estimate if Q2/Q3 replaced")
    print(pd.read_csv(OUT / "q23_presleep_app_hybrid_estimate.csv").round(6).to_string(index=False))


if __name__ == "__main__":
    main()
