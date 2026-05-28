#!/usr/bin/env python3
"""E45 structured public-subset feasibility audit.

This experiment treats known public LBs as a sensor for whether the public
subset can be explained by simple row/subject/date/raw-domain masks.  It does
not rank new submissions.  A mask is useful only if it predicts held-out known
anchors with selector-scale error and narrow feasible ranges under train-prior
constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import linprog as scipy_linprog
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, known_public_table, load_sub  # noqa: E402


POINT_OUT = OUT / "structured_public_subset_feasibility_loocv.csv"
MASK_OUT = OUT / "structured_public_subset_feasibility_masks.csv"
RANGE_OUT = OUT / "structured_public_subset_feasibility_ranges.csv"
SUMMARY_OUT = OUT / "structured_public_subset_feasibility_summary.csv"
REPORT_OUT = OUT / "structured_public_subset_feasibility_report.md"

EPS = 1e-6
RAW05_GAP = 0.5775263072 - 0.5774393210
BEST_SELECTOR_ERROR = 0.000218288


@dataclass(frozen=True)
class Mask:
    kind: str
    name: str
    mask: np.ndarray


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def losses(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip_prob(prob)
    return -np.log(p), -np.log1p(-p)


def solve_lp(
    c: np.ndarray,
    a_ub: np.ndarray | None,
    b_ub: np.ndarray | None,
    bounds: list[tuple[float | None, float | None]],
) -> tuple[bool, float, np.ndarray, str]:
    res = scipy_linprog(c, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not res.success:
        return False, float("nan"), np.full(len(c), np.nan), str(res.message)
    return True, float(res.fun), np.asarray(res.x, dtype=np.float64), str(res.message)


def markdown_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "_None._"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else str(x))
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]).replace("\n", " ") for col in view.columns) + " |")
    return "\n".join(lines)


def load_known(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    known = known_public_table().copy()
    known = known.reset_index(drop=True)
    pos_rows: list[np.ndarray] = []
    neg_rows: list[np.ndarray] = []
    for file_name in known["file"]:
        pred = load_sub(str(file_name), sample)[TARGETS].to_numpy(dtype=np.float64)
        pos, neg = losses(pred)
        pos_rows.append(pos)
        neg_rows.append(neg)
    return known, np.stack(pos_rows, axis=0), np.stack(neg_rows, axis=0)


def mask_record(kind: str, name: str, idx: np.ndarray, n: int) -> Mask:
    mask = np.zeros(n, dtype=bool)
    mask[np.asarray(idx, dtype=int)] = True
    return Mask(kind, name, mask)


def add_mask(rows: list[Mask], kind: str, name: str, mask: np.ndarray, min_rows: int = 15) -> None:
    if int(mask.sum()) >= min_rows:
        rows.append(Mask(kind, name, np.asarray(mask, dtype=bool)))


def quantile_mask(values: np.ndarray, q: float, high: bool) -> np.ndarray:
    cut = float(np.nanquantile(values, q))
    return values >= cut if high else values <= cut


def numeric_feature_cols(frame: pd.DataFrame) -> list[str]:
    skip = set(KEYS + TARGETS + ["split", "dow", "month"])
    cols = []
    for col in frame.columns:
        if col in skip:
            continue
        if pd.api.types.is_numeric_dtype(frame[col]):
            vals = pd.to_numeric(frame[col], errors="coerce")
            if int(vals.notna().sum()) >= 60 and float(vals.nunique(dropna=True)) > 1:
                cols.append(col)
    return cols


def raw_domain_masks(sample: pd.DataFrame) -> list[Mask]:
    features_path = OUT / "all_keys_deep_features.parquet"
    if not features_path.exists():
        return []
    features = pd.read_parquet(features_path)
    for df in (features, sample):
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    train_feat = features[features["split"].eq("train")].copy().reset_index(drop=True)
    test_feat = features[features["split"].eq("submission")].copy()
    test_feat = sample[KEYS].merge(test_feat, on=KEYS, how="left", validate="one_to_one")
    all_feat = pd.concat([train_feat, test_feat], axis=0, ignore_index=True)
    cols = numeric_feature_cols(all_feat)
    if not cols:
        return []

    x_all = all_feat[cols].replace([np.inf, -np.inf], np.nan)
    y_domain = np.r_[np.zeros(len(train_feat), dtype=int), np.ones(len(test_feat), dtype=int)]
    domain_pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced", solver="lbfgs"),
    )
    domain_pipe.fit(x_all, y_domain)
    domain_prob = domain_pipe.predict_proba(x_all)[:, 1][-len(test_feat) :]
    domain_auc = float(roc_auc_score(y_domain, domain_pipe.predict_proba(x_all)[:, 1]))

    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    x_train = prep.fit_transform(train_feat[cols].replace([np.inf, -np.inf], np.nan))
    x_test = prep.transform(test_feat[cols].replace([np.inf, -np.inf], np.nan))
    nn = NearestNeighbors(n_neighbors=min(8, len(train_feat)), metric="euclidean")
    nn.fit(x_train)
    dist, _ = nn.kneighbors(x_test)
    density_radius = dist[:, -1]
    missing_frac = test_feat[cols].replace([np.inf, -np.inf], np.nan).isna().mean(axis=1).to_numpy()
    km = KMeans(n_clusters=8, n_init=20, random_state=20260528)
    cluster = km.fit_predict(np.vstack([x_train, x_test]))[-len(test_feat) :]

    rows: list[Mask] = []
    n = len(test_feat)
    for name, values in (
        ("domain", domain_prob),
        ("density_radius", density_radius),
        ("missing", missing_frac),
    ):
        for q in (0.30, 0.40):
            add_mask(rows, "raw_domain", f"{name}_low{int(q * 100)}", quantile_mask(values, q, high=False), 20)
            add_mask(rows, "raw_domain", f"{name}_high{int(q * 100)}", quantile_mask(values, 1.0 - q, high=True), 20)
    for c in sorted(set(cluster.tolist())):
        add_mask(rows, "raw_cluster", f"cluster_{c}_domain_auc_{domain_auc:.3f}", cluster == c, 18)
    rows.append(Mask("raw_domain_meta", f"domain_auc_{domain_auc:.3f}", np.ones(n, dtype=bool)))
    return rows


def build_masks(sample: pd.DataFrame) -> list[Mask]:
    sample = sample.copy().reset_index(drop=True)
    n = len(sample)
    sample["_row"] = np.arange(n)
    masks: list[Mask] = [Mask("all", "all_rows", np.ones(n, dtype=bool))]

    for subject, group in sample.groupby("subject_id", sort=True):
        idx = group["_row"].to_numpy(dtype=int)
        masks.append(mask_record("single_subject", f"subject_{subject}", idx, n))
        comp = np.ones(n, dtype=bool)
        comp[idx] = False
        masks.append(Mask("subject_complement", f"not_subject_{subject}", comp))

    subject_order = sorted(sample["subject_id"].unique())
    for split_name, ids in (
        ("id01_to_id05", subject_order[:5]),
        ("id06_to_id10", subject_order[5:]),
        ("odd_subjects", subject_order[::2]),
        ("even_subjects", subject_order[1::2]),
    ):
        add_mask(masks, "subject_group", split_name, sample["subject_id"].isin(ids).to_numpy(), 20)

    order = np.arange(n)
    for frac in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80):
        k = max(1, int(round(n * frac)))
        add_mask(masks, "global_key_order", f"prefix_frac{frac:.2f}", order < k, 20)
        add_mask(masks, "global_key_order", f"suffix_frac{frac:.2f}", order >= n - k, 20)
    for window in (50, 75, 100, 125, 175):
        starts = sorted(set([0, max(0, (n - window) // 2), max(0, n - window)]))
        for start in starts:
            mask = np.zeros(n, dtype=bool)
            mask[start : start + window] = True
            add_mask(masks, "global_key_window", f"start{start:03d}_len{window:03d}", mask, 20)
    for mod in (2, 3, 4, 5, 7):
        for rem in range(mod):
            add_mask(masks, "global_key_mod", f"mod{mod}_rem{rem}", order % mod == rem, 20)

    for frac in (0.30, 0.50, 0.70):
        head = np.zeros(n, dtype=bool)
        tail = np.zeros(n, dtype=bool)
        middle = np.zeros(n, dtype=bool)
        for _subject, group in sample.groupby("subject_id", sort=True):
            idx = group["_row"].to_numpy(dtype=int)
            k = max(1, int(round(len(idx) * frac)))
            head[idx[:k]] = True
            tail[idx[-k:]] = True
            start = max(0, (len(idx) - k) // 2)
            middle[idx[start : start + k]] = True
        add_mask(masks, "subject_order", f"per_subject_head_frac{frac:.2f}", head, 20)
        add_mask(masks, "subject_order", f"per_subject_tail_frac{frac:.2f}", tail, 20)
        add_mask(masks, "subject_order", f"per_subject_mid_frac{frac:.2f}", middle, 20)

    by_date = sample.sort_values(["sleep_date", "subject_id", "lifelog_date"]).reset_index()
    date_rank = np.empty(n, dtype=int)
    date_rank[by_date["index"].to_numpy(dtype=int)] = np.arange(n)
    for frac in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80):
        k = max(1, int(round(n * frac)))
        add_mask(masks, "calendar_order", f"date_prefix_frac{frac:.2f}", date_rank < k, 20)
        add_mask(masks, "calendar_order", f"date_suffix_frac{frac:.2f}", date_rank >= n - k, 20)

    sleep_dt = pd.to_datetime(sample["sleep_date"])
    dow = sleep_dt.dt.day_name()
    for name, mask in (
        ("weekend", sleep_dt.dt.dayofweek.ge(5).to_numpy()),
        ("weekday", sleep_dt.dt.dayofweek.lt(5).to_numpy()),
    ):
        add_mask(masks, "calendar", name, mask, 20)
    for day_name in sorted(dow.unique()):
        add_mask(masks, "dow", day_name, dow.eq(day_name).to_numpy(), 20)
    for month, idx in sample.groupby(sleep_dt.dt.month, sort=True).groups.items():
        mask = np.zeros(n, dtype=bool)
        mask[list(idx)] = True
        add_mask(masks, "month", f"month_{month}", mask, 20)

    masks.extend(raw_domain_masks(sample.copy()))

    rng = np.random.default_rng(20260528)
    for frac in (0.30, 0.50, 0.70):
        k = max(1, int(round(n * frac)))
        for rep in range(8):
            idx = rng.choice(n, size=k, replace=False)
            mask = np.zeros(n, dtype=bool)
            mask[idx] = True
            masks.append(Mask("random_control", f"frac{frac:.2f}_rep{rep:02d}", mask))

    deduped: list[Mask] = []
    seen: set[bytes] = set()
    for mask in masks:
        key = np.packbits(mask.mask).tobytes()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mask)
    return deduped


def build_prior_center(sample: pd.DataFrame, train: pd.DataFrame, selected_rows: np.ndarray) -> np.ndarray:
    global_prior = train[TARGETS].mean()
    subject_prior = train.groupby("subject_id")[TARGETS].mean()
    centers = []
    for row_idx in selected_rows:
        subject = sample.iloc[int(row_idx)]["subject_id"]
        if subject in subject_prior.index:
            center = 0.70 * subject_prior.loc[subject, TARGETS] + 0.30 * global_prior
        else:
            center = global_prior
        centers.append(center.to_numpy(dtype=np.float64))
    return np.vstack(centers).reshape(-1)


def target_ids_for_rows(n_rows: int) -> np.ndarray:
    return np.tile(np.arange(len(TARGETS), dtype=int), n_rows)


def subject_ids_for_cells(sample: pd.DataFrame, selected_rows: np.ndarray) -> np.ndarray:
    row_subjects = sample.iloc[selected_rows]["subject_id"].to_numpy()
    return np.repeat(row_subjects, len(TARGETS))


def prior_constraint_rows(
    sample: pd.DataFrame,
    train: pd.DataFrame,
    selected_rows: np.ndarray,
    m: int,
    n_slack: int,
    n_dev: int,
    global_band: float,
    subject_band: float,
) -> tuple[list[np.ndarray], list[float]]:
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    n_row = len(selected_rows)
    target_ids = target_ids_for_rows(n_row)
    train_global = train[TARGETS].mean().to_dict()
    zeros_tail = np.zeros(n_slack + n_dev, dtype=np.float64)

    for ti, target in enumerate(TARGETS):
        coeff = (target_ids == ti).astype(np.float64) / float(n_row)
        lo = max(0.0, float(train_global[target]) - global_band)
        hi = min(1.0, float(train_global[target]) + global_band)
        rows.append(np.r_[coeff, zeros_tail])
        rhs.append(hi)
        rows.append(np.r_[-coeff, zeros_tail])
        rhs.append(-lo)

    subject_prior = train.groupby("subject_id")[TARGETS].mean()
    cell_subject = subject_ids_for_cells(sample, selected_rows)
    row_subject = sample.iloc[selected_rows]["subject_id"].to_numpy()
    for subject in sorted(set(row_subject.tolist())):
        if subject not in subject_prior.index:
            continue
        subject_rows = int((row_subject == subject).sum())
        if subject_rows < 4:
            continue
        for ti, target in enumerate(TARGETS):
            coeff = ((cell_subject == subject) & (target_ids == ti)).astype(np.float64) / float(subject_rows)
            center = float(subject_prior.loc[subject, target])
            lo = max(0.0, center - subject_band)
            hi = min(1.0, center + subject_band)
            rows.append(np.r_[coeff, zeros_tail])
            rhs.append(hi)
            rows.append(np.r_[-coeff, zeros_tail])
            rhs.append(-lo)
    return rows, rhs


def fit_min_deviation_point(
    known_y: np.ndarray,
    const: np.ndarray,
    b: np.ndarray,
    holdout: int,
    y0: np.ndarray,
    sample: pd.DataFrame,
    train: pd.DataFrame,
    selected_rows: np.ndarray,
    global_band: float = 0.10,
    subject_band: float = 0.20,
    slack_tol: float = 1e-9,
) -> dict[str, object]:
    fit_idx = np.array([i for i in range(len(known_y)) if i != holdout], dtype=int)
    n_fit = len(fit_idx)
    m = len(y0)
    n_vars = m + n_fit + 2 * m
    q_slice = slice(0, m)
    s_slice = slice(m, m + n_fit)
    dp_slice = slice(m + n_fit, m + n_fit + m)
    dn_slice = slice(m + n_fit + m, n_vars)

    lhs = known_y[fit_idx] - const[fit_idx]
    rows = []
    rhs = []
    left = np.zeros((n_fit, n_vars), dtype=np.float64)
    left[:, q_slice] = b[fit_idx]
    left[:, s_slice] = -np.eye(n_fit)
    rows.append(left)
    rhs.extend(lhs.tolist())
    right = np.zeros((n_fit, n_vars), dtype=np.float64)
    right[:, q_slice] = -b[fit_idx]
    right[:, s_slice] = -np.eye(n_fit)
    rows.append(right)
    rhs.extend((-lhs).tolist())

    prior_rows, prior_rhs = prior_constraint_rows(
        sample, train, selected_rows, m, n_fit, 2 * m, global_band, subject_band
    )
    rows.extend(prior_rows)
    rhs.extend(prior_rhs)

    bounds = [(0.0, 1.0)] * m + [(0.0, None)] * n_fit + [(0.0, None)] * (2 * m)

    c1 = np.zeros(n_vars, dtype=np.float64)
    c1[s_slice] = 1.0
    a_ub1 = np.vstack(rows)
    b_ub1 = np.asarray(rhs, dtype=np.float64)
    ok1, min_slack, x1, msg1 = solve_lp(c1, a_ub1, b_ub1, bounds)
    if not ok1:
        return {
            "fit_ok": False,
            "stage": "min_slack",
            "message": msg1,
            "fit_sum_slack": np.nan,
            "heldout_pred": np.nan,
            "heldout_abs_error": np.nan,
            "mean_abs_fit_resid": np.nan,
            "max_abs_fit_resid": np.nan,
            "mean_abs_dev": np.nan,
            "q": np.full(m, np.nan),
        }

    dev_pos = np.zeros((m, n_vars), dtype=np.float64)
    dev_pos[:, q_slice] = np.eye(m)
    dev_pos[:, dp_slice] = -np.eye(m)
    rows.append(dev_pos)
    rhs.extend(y0.tolist())
    dev_neg = np.zeros((m, n_vars), dtype=np.float64)
    dev_neg[:, q_slice] = -np.eye(m)
    dev_neg[:, dn_slice] = -np.eye(m)
    rows.append(dev_neg)
    rhs.extend((-y0).tolist())
    slack_budget = np.zeros((1, n_vars), dtype=np.float64)
    slack_budget[:, s_slice] = 1.0
    rows.append(slack_budget)
    rhs.append(float(min_slack + slack_tol))

    c2 = np.zeros(n_vars, dtype=np.float64)
    c2[dp_slice] = 1.0 / float(m)
    c2[dn_slice] = 1.0 / float(m)
    ok2, dev_obj, x2, msg2 = solve_lp(c2, np.vstack(rows), np.asarray(rhs, dtype=np.float64), bounds)
    if not ok2:
        return {
            "fit_ok": False,
            "stage": "min_dev",
            "message": msg2,
            "fit_sum_slack": min_slack,
            "heldout_pred": np.nan,
            "heldout_abs_error": np.nan,
            "mean_abs_fit_resid": np.nan,
            "max_abs_fit_resid": np.nan,
            "mean_abs_dev": np.nan,
            "q": np.full(m, np.nan),
        }
    q = x2[q_slice]
    pred_fit = const[fit_idx] + b[fit_idx] @ q
    fit_resid = pred_fit - known_y[fit_idx]
    heldout_pred = float(const[holdout] + b[holdout] @ q)
    return {
        "fit_ok": True,
        "stage": "ok",
        "message": msg2,
        "fit_sum_slack": float(min_slack),
        "heldout_pred": heldout_pred,
        "heldout_abs_error": float(abs(heldout_pred - known_y[holdout])),
        "mean_abs_fit_resid": float(np.mean(np.abs(fit_resid))),
        "max_abs_fit_resid": float(np.max(np.abs(fit_resid))),
        "mean_abs_dev": float(dev_obj),
        "q": q,
    }


def range_for_holdout(
    known_y: np.ndarray,
    const: np.ndarray,
    b: np.ndarray,
    holdout: int,
    fit_sum_slack: float,
    sample: pd.DataFrame,
    train: pd.DataFrame,
    selected_rows: np.ndarray,
    global_band: float = 0.10,
    subject_band: float = 0.20,
    slack_tol: float = 1e-8,
) -> tuple[bool, float, float]:
    fit_idx = np.array([i for i in range(len(known_y)) if i != holdout], dtype=int)
    n_fit = len(fit_idx)
    m = b.shape[1]
    n_vars = m + n_fit
    q_slice = slice(0, m)
    s_slice = slice(m, m + n_fit)
    lhs = known_y[fit_idx] - const[fit_idx]
    rows = []
    rhs = []
    left = np.zeros((n_fit, n_vars), dtype=np.float64)
    left[:, q_slice] = b[fit_idx]
    left[:, s_slice] = -np.eye(n_fit)
    rows.append(left)
    rhs.extend(lhs.tolist())
    right = np.zeros((n_fit, n_vars), dtype=np.float64)
    right[:, q_slice] = -b[fit_idx]
    right[:, s_slice] = -np.eye(n_fit)
    rows.append(right)
    rhs.extend((-lhs).tolist())
    prior_rows, prior_rhs = prior_constraint_rows(sample, train, selected_rows, m, n_fit, 0, global_band, subject_band)
    rows.extend(prior_rows)
    rhs.extend(prior_rhs)
    slack_budget = np.zeros((1, n_vars), dtype=np.float64)
    slack_budget[:, s_slice] = 1.0
    rows.append(slack_budget)
    rhs.append(float(fit_sum_slack + slack_tol))
    a_ub = np.vstack(rows)
    b_ub = np.asarray(rhs, dtype=np.float64)
    bounds = [(0.0, 1.0)] * m + [(0.0, None)] * n_fit

    c = np.zeros(n_vars, dtype=np.float64)
    c[q_slice] = b[holdout]
    ok_min, lo_raw, _, _ = solve_lp(c, a_ub, b_ub, bounds)
    ok_max, hi_raw_neg, _, _ = solve_lp(-c, a_ub, b_ub, bounds)
    if not ok_min or not ok_max:
        return False, float("nan"), float("nan")
    return True, float(const[holdout] + lo_raw), float(const[holdout] - hi_raw_neg)


def pairwise_rank_accuracy(frame: pd.DataFrame) -> float:
    y = frame["actual_public_lb"].to_numpy(dtype=np.float64)
    p = frame["heldout_pred"].to_numpy(dtype=np.float64)
    ok = total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = p[i] - p[j]
            if abs(dy) < 1e-15 or abs(dp) < 1e-15:
                continue
            total += 1
            ok += int(dy * dp > 0)
    return float(ok / total) if total else float("nan")


def main() -> None:
    start_time = time.time()
    sample = load_sub(A2C8)
    sample_key = sample[KEYS].copy()
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    for df in (sample_key, train):
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    known, pos_all, neg_all = load_known(sample)
    y_public = known["public_lb"].to_numpy(dtype=np.float64)
    masks = build_masks(sample_key)

    mask_meta = pd.DataFrame(
        [
            {
                "mask_kind": mask.kind,
                "mask_name": mask.name,
                "rows": int(mask.mask.sum()),
                "row_frac": float(mask.mask.mean()),
            }
            for mask in masks
        ]
    )
    mask_meta.to_csv(MASK_OUT, index=False)

    point_rows: list[dict[str, object]] = []
    fit_slack_cache: dict[tuple[str, str, int], float] = {}
    for mi, mask in enumerate(masks, start=1):
        selected_rows = np.flatnonzero(mask.mask)
        y0 = build_prior_center(sample_key, train, selected_rows)
        pos = pos_all[:, selected_rows, :].reshape(len(known), -1)
        neg = neg_all[:, selected_rows, :].reshape(len(known), -1)
        const = neg.mean(axis=1)
        b = (pos - neg) / float(pos.shape[1])
        for holdout in range(len(known)):
            fit = fit_min_deviation_point(
                y_public,
                const,
                b,
                holdout,
                y0,
                sample_key,
                train,
                selected_rows,
            )
            key = (mask.kind, mask.name, holdout)
            fit.pop("q")
            fit_slack_cache[key] = float(fit["fit_sum_slack"]) if pd.notna(fit["fit_sum_slack"]) else float("nan")
            point_rows.append(
                {
                    "mask_kind": mask.kind,
                    "mask_name": mask.name,
                    "rows": int(mask.mask.sum()),
                    "holdout_name": str(known.loc[holdout, "file"]),
                    "actual_public_lb": float(y_public[holdout]),
                    **fit,
                }
            )
        if mi % 25 == 0:
            print(f"processed {mi}/{len(masks)} masks in {time.time() - start_time:.1f}s", flush=True)

    point = pd.DataFrame(point_rows)
    point.to_csv(POINT_OUT, index=False)

    summary_rows: list[dict[str, object]] = []
    for (kind, name), group in point[point["fit_ok"].eq(True)].groupby(["mask_kind", "mask_name"], sort=False):
        summary_rows.append(
            {
                "mask_kind": kind,
                "mask_name": name,
                "rows": int(group["rows"].iloc[0]),
                "loocv_mae": float(group["heldout_abs_error"].mean()),
                "loocv_median_abs": float(group["heldout_abs_error"].median()),
                "loocv_max_abs": float(group["heldout_abs_error"].max()),
                "fit_slack_mean": float(group["fit_sum_slack"].mean()),
                "fit_slack_max": float(group["fit_sum_slack"].max()),
                "mean_abs_dev": float(group["mean_abs_dev"].mean()),
                "rank_accuracy": pairwise_rank_accuracy(group),
                "a2c8_predicted_best": bool(
                    group.loc[group["holdout_name"].str.contains(A2C8), "heldout_pred"].iloc[0]
                    <= group["heldout_pred"].min() + 1e-12
                    if group["holdout_name"].str.contains(A2C8).any()
                    else False
                ),
                "raw05_direction_correct": bool(
                    group.loc[group["holdout_name"].str.contains(A2C8), "heldout_pred"].iloc[0]
                    < group.loc[
                        group["holdout_name"].str.contains("submission_raw_timeline_jepa_rescue_strict_scale0p5"),
                        "heldout_pred",
                    ].iloc[0]
                    if group["holdout_name"].str.contains(A2C8).any()
                    and group["holdout_name"].str.contains("submission_raw_timeline_jepa_rescue_strict_scale0p5").any()
                    else False
                ),
            }
        )
    summary = pd.DataFrame(summary_rows)
    if not summary.empty:
        summary["mae_over_raw05_gap"] = summary["loocv_mae"] / RAW05_GAP
        summary["mae_over_selector_error"] = summary["loocv_mae"] / BEST_SELECTOR_ERROR
        summary["max_abs_over_selector_error"] = summary["loocv_max_abs"] / BEST_SELECTOR_ERROR
        summary["selector_scale_gate"] = (
            summary["loocv_mae"].le(BEST_SELECTOR_ERROR)
            & summary["loocv_max_abs"].le(2.0 * BEST_SELECTOR_ERROR)
            & summary["a2c8_predicted_best"]
            & summary["raw05_direction_correct"]
        )
        summary["strict_subgap_gate"] = (
            summary["loocv_mae"].le(RAW05_GAP)
            & summary["loocv_max_abs"].le(BEST_SELECTOR_ERROR)
            & summary["a2c8_predicted_best"]
            & summary["raw05_direction_correct"]
        )
        summary = summary.sort_values(
            [
                "strict_subgap_gate",
                "selector_scale_gate",
                "loocv_mae",
                "loocv_max_abs",
                "rank_accuracy",
            ],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    summary.to_csv(SUMMARY_OUT, index=False)

    selected_for_range = []
    if not summary.empty:
        selected_for_range.extend(summary.head(8)[["mask_kind", "mask_name"]].itertuples(index=False, name=None))
        for kind in sorted(summary["mask_kind"].unique()):
            row = summary[summary["mask_kind"].eq(kind)].head(1)
            if not row.empty:
                selected_for_range.append((str(row["mask_kind"].iloc[0]), str(row["mask_name"].iloc[0])))
        selected_for_range.append(("all", "all_rows"))
    selected_for_range = list(dict.fromkeys(selected_for_range))

    range_rows: list[dict[str, object]] = []
    mask_lookup = {(m.kind, m.name): m for m in masks}
    for kind, name in selected_for_range:
        mask = mask_lookup.get((kind, name))
        if mask is None:
            continue
        selected_rows = np.flatnonzero(mask.mask)
        pos = pos_all[:, selected_rows, :].reshape(len(known), -1)
        neg = neg_all[:, selected_rows, :].reshape(len(known), -1)
        const = neg.mean(axis=1)
        b = (pos - neg) / float(pos.shape[1])
        for holdout in range(len(known)):
            fit_sum = fit_slack_cache.get((kind, name, holdout), np.nan)
            ok, lo, hi = range_for_holdout(
                y_public,
                const,
                b,
                holdout,
                fit_sum,
                sample_key,
                train,
                selected_rows,
            )
            actual = float(y_public[holdout])
            range_rows.append(
                {
                    "mask_kind": kind,
                    "mask_name": name,
                    "rows": int(mask.mask.sum()),
                    "holdout_name": str(known.loc[holdout, "file"]),
                    "range_ok": ok,
                    "actual_public_lb": actual,
                    "pred_min": lo,
                    "pred_max": hi,
                    "range_width": float(hi - lo) if ok else np.nan,
                    "actual_inside_range": bool(ok and lo - 1e-12 <= actual <= hi + 1e-12),
                    "nearest_abs_error": float(0.0 if ok and lo <= actual <= hi else min(abs(actual - lo), abs(actual - hi)))
                    if ok
                    else np.nan,
                }
            )
    ranges = pd.DataFrame(range_rows)
    ranges.to_csv(RANGE_OUT, index=False)

    family = (
        summary.groupby("mask_kind")
        .agg(
            masks=("mask_name", "count"),
            best_mae=("loocv_mae", "min"),
            median_mae=("loocv_mae", "median"),
            best_max_abs=("loocv_max_abs", "min"),
            best_rank_accuracy=("rank_accuracy", "max"),
            selector_scale_gates=("selector_scale_gate", "sum"),
            strict_subgap_gates=("strict_subgap_gate", "sum"),
            a2c8_best_rate=("a2c8_predicted_best", "mean"),
            raw05_direction_rate=("raw05_direction_correct", "mean"),
        )
        .reset_index()
        .sort_values(["strict_subgap_gates", "selector_scale_gates", "best_mae"], ascending=[False, False, True])
        if not summary.empty
        else pd.DataFrame()
    )

    range_summary = (
        ranges[ranges["range_ok"].eq(True)]
        .groupby(["mask_kind", "mask_name"])
        .agg(
            range_mean_width=("range_width", "mean"),
            range_max_width=("range_width", "max"),
            range_coverage=("actual_inside_range", "mean"),
            range_nearest_mae=("nearest_abs_error", "mean"),
        )
        .reset_index()
        .sort_values(["range_mean_width", "range_max_width"])
        if not ranges.empty
        else pd.DataFrame()
    )

    best = summary.head(15) if not summary.empty else pd.DataFrame()
    gates = summary[summary["selector_scale_gate"].eq(True)] if not summary.empty else pd.DataFrame()
    strict = summary[summary["strict_subgap_gate"].eq(True)] if not summary.empty else pd.DataFrame()
    report = [
        "# E45 Structured Public-Subset Feasibility",
        "",
        "## Observe",
        "",
        "E43-E44 showed that current candidate edges are smaller than selector error and the existing scored universe has no hidden large safe movement. The next cheap falsification is whether the public subset itself is a simple structured mask that can be used as an independent selector target.",
        "",
        "## Wonder",
        "",
        "Can subject/date/order/raw-domain masks plus train-derived priors predict held-out known public anchors at selector-scale error, or are public-subset inverse worlds still too underdetermined?",
        "",
        "## Hypothesis",
        "",
        "H44: if public LB is dominated by a simple structured subset, then at least one predeclared mask family should produce leave-one-anchor-out public-LB predictions with MAE below the current selector error and feasible ranges narrow enough to beat the raw05-A2C8 gap.",
        "",
        "## Method",
        "",
        f"- known anchors: `{len(known)}`.",
        f"- masks tested: `{len(masks)}`.",
        f"- raw05-A2C8 public gap: `{RAW05_GAP:.10f}`.",
        f"- best audited selector error: `{BEST_SELECTOR_ERROR:.9f}`.",
        "- For each mask and held-out anchor, fit soft hidden labels on the remaining anchors under train global +/-0.10 and subject-target +/-0.20 prior constraints, then choose the minimum-deviation solution from shrunk subject train priors.",
        "- Stress tests: anchor-LOO, structured-vs-random mask comparison, train-prior plausibility, raw05/A2C8 known-direction check, and feasible interval width on the best masks.",
        "",
        "## Result",
        "",
        f"- selector-scale gates: `{int(summary['selector_scale_gate'].sum()) if not summary.empty else 0}`.",
        f"- strict sub-gap gates: `{int(summary['strict_subgap_gate'].sum()) if not summary.empty else 0}`.",
        f"- best LOO MAE: `{float(summary['loocv_mae'].min()) if not summary.empty else np.nan:.9f}`.",
        f"- best LOO MAE / raw05 gap: `{float(summary['mae_over_raw05_gap'].min()) if not summary.empty else np.nan:.3f}`.",
        f"- best LOO MAE / selector error: `{float(summary['mae_over_selector_error'].min()) if not summary.empty else np.nan:.3f}`.",
        "",
        "### Family Summary",
        "",
        markdown_table(family),
        "",
        "### Best Masks",
        "",
        markdown_table(
            best[
                [
                    "mask_kind",
                    "mask_name",
                    "rows",
                    "loocv_mae",
                    "loocv_max_abs",
                    "rank_accuracy",
                    "a2c8_predicted_best",
                    "raw05_direction_correct",
                    "selector_scale_gate",
                    "strict_subgap_gate",
                ]
            ]
            if not best.empty
            else best
        ),
        "",
        "### Feasible Range Check",
        "",
        markdown_table(range_summary.head(20)),
        "",
        "## Decision",
        "",
    ]
    if len(strict) > 0:
        report.extend(
            [
                "At least one structured mask achieved strict sub-gap LOO behavior. This would make H44 a candidate selector target and should be tested against candidate movement before any submission ranking.",
            ]
        )
    elif len(gates) > 0:
        report.extend(
            [
                "Some masks reached selector-scale point error but not strict raw05-gap resolution. H44 is partially alive as a diagnostic sensor, not yet as a submission selector.",
            ]
        )
    else:
        report.extend(
            [
                "No structured mask produced selector-scale held-out-anchor predictions. Simple public-subset structure is not the missing selector target under these priors.",
                "This strengthens the bottleneck diagnosis: the plateau is not explained by an obvious subject/order/date/raw-domain public split that we can locally recover.",
            ]
        )
    report.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{POINT_OUT.relative_to(ROOT)}`",
            f"- `{MASK_OUT.relative_to(ROOT)}`",
            f"- `{RANGE_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
