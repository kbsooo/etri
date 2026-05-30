#!/usr/bin/env python3
"""E237: cell-level decisive JEPA target for Q3/S4.

E234 showed that high-impact tail targets can improve OOF movement. E236 showed
that row-level Q3/S4 tail masks do not become a public-safe E224 translator.

This experiment asks the sharper follow-up:

Can the useful object be a row-target *cell* representation rather than a row
mask? We train small fold-safe bad-cell predictors from OOF benefit labels over
Q3/S4 cells, optionally with S2 as a negative/control source, then materialize
only candidates that survive the E222/E230 public-free tail stress.

No public LB is used. The script writes submission files only when a candidate
preserves E224 expected focus, reduces adverse capacity, improves support, and
does not worsen Q3 top-cell concentration.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import warnings
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e232_cross_target_support_invariance as e232  # noqa: E402
import e234_tail_contrastive_jepa_target as e234  # noqa: E402


RNG = 20260530 + 237
EPS = 1.0e-12

Q3_IDX = TARGETS.index("Q3")
S4_IDX = TARGETS.index("S4")
ACTIVE_TASKS = ["q3_e224", "s4_e224"]
CONTROL_TASKS = ["s2_e216", "q3_e224", "s4_e224"]

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

OOF_OUT = OUT / "e237_cell_decisive_jepa_target_oof_scan.csv"
MATERIALIZATION_OUT = OUT / "e237_cell_decisive_jepa_target_materialization_scan.csv"
SELECTED_OUT = OUT / "e237_cell_decisive_jepa_target_selected.csv"
TARGET_OUT = OUT / "e237_cell_decisive_jepa_target_targets.csv"
REPORT_OUT = OUT / "e237_cell_decisive_jepa_target_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_vec(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    yy = np.asarray(y, dtype=np.float64)
    pp = clip_prob(p)
    return -(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp))


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    yy = np.asarray(y)
    mask = ~pd.isna(yy)
    yy = yy[mask].astype(int)
    pp = clip_prob(np.asarray(p, dtype=np.float64)[mask])
    if len(yy) == 0 or len(np.unique(yy)) < 2:
        return float("nan")
    return float(roc_auc_score(yy, pp))


def safe_logloss(y: np.ndarray, p: np.ndarray) -> float:
    yy = np.asarray(y)
    mask = ~pd.isna(yy)
    yy = yy[mask].astype(int)
    pp = clip_prob(np.asarray(p, dtype=np.float64)[mask])
    if len(yy) == 0:
        return float("nan")
    return float(log_loss(yy, pp, labels=[0, 1]))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    mask = np.isfinite(aa) & np.isfinite(bb)
    aa = aa[mask]
    bb = bb[mask]
    if len(aa) == 0 or float(np.std(aa)) <= EPS or float(np.std(bb)) <= EPS:
        return 0.0
    return float(np.corrcoef(aa, bb)[0, 1])


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def model_defs() -> dict[str, Any]:
    return {
        "lr_l2_c0p10": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.10,
                        solver="lbfgs",
                        class_weight="balanced",
                        max_iter=3000,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
        "hgb_shallow": Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                (
                    "clf",
                    HistGradientBoostingClassifier(
                        max_iter=70,
                        learning_rate=0.035,
                        max_leaf_nodes=7,
                        min_samples_leaf=18,
                        l2_regularization=0.8,
                        random_state=RNG,
                    ),
                ),
            ]
        ),
    }


def fit_predict(model: Any, x_train: pd.DataFrame, y_train: np.ndarray, x_pred: pd.DataFrame) -> np.ndarray:
    yy = np.asarray(y_train, dtype=int)
    if len(yy) == 0:
        return np.full(len(x_pred), 0.5, dtype=np.float64)
    if len(np.unique(yy)) < 2:
        return np.full(len(x_pred), float(np.mean(yy)), dtype=np.float64)
    fitted = clone(model)
    fitted.fit(x_train, yy)
    return clip_prob(fitted.predict_proba(x_pred)[:, 1])


def build_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_raw, train_long, sub_long, _ = e232.build_long_frames()
    train_long = e234.add_true_labels(train_long, train_raw)
    feats = e232.feature_sets(train_long)
    feats = {name: [c for c in cols if c != "true_label"] for name, cols in feats.items()}
    return train_raw, train_long, sub_long, feats


def source_mask(df: pd.DataFrame, source_scope: str) -> np.ndarray:
    if source_scope == "q3s4":
        return df["task_name"].isin(ACTIVE_TASKS).to_numpy()
    if source_scope == "all3":
        return df["task_name"].isin(CONTROL_TASKS).to_numpy()
    raise ValueError(source_scope)


def active_mask(df: pd.DataFrame) -> np.ndarray:
    return df["task_name"].isin(ACTIVE_TASKS).to_numpy()


def thresholds_by_task(df: pd.DataFrame, q: float) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for task, part in df.groupby("task_name"):
        benefit = part["benefit"].to_numpy(dtype=np.float64)
        out[str(task)] = (float(np.quantile(benefit, q)), float(np.quantile(benefit, 1.0 - q)))
    return out


def label_with_thresholds(
    df: pd.DataFrame, thresholds: dict[str, tuple[float, float]], kind: str
) -> tuple[np.ndarray, np.ndarray]:
    benefit = df["benefit"].to_numpy(dtype=np.float64)
    task = df["task_name"].astype(str).to_numpy()
    label = np.zeros(len(df), dtype=int)
    eval_mask = np.zeros(len(df), dtype=bool)
    for name, (low, high) in thresholds.items():
        idx = task == name
        if not np.any(idx):
            continue
        if kind == "risk":
            label[idx] = (benefit[idx] <= low).astype(int)
            eval_mask[idx] = True
        elif kind == "contrast":
            tail = idx & ((benefit <= low) | (benefit >= high))
            label[tail] = (benefit[tail] <= low).astype(int)
            eval_mask[tail] = True
        else:
            raise ValueError(kind)
    return label, eval_mask


def fold_indices(df: pd.DataFrame, split: str, y_hint: np.ndarray) -> Any:
    del y_hint
    if split == "subject5":
        groups = df["subject_id"].astype(str).to_numpy()
    elif split == "row5":
        groups = df["row_idx"].astype(str).to_numpy()
    else:
        raise ValueError(split)
    return GroupKFold(n_splits=min(5, len(np.unique(groups)))).split(df, groups=groups)


def oof_bad_predict(
    model: Any,
    df: pd.DataFrame,
    cols: list[str],
    source_scope: str,
    split: str,
    kind: str,
    q: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pred = np.full(len(df), np.nan, dtype=np.float64)
    eval_label = np.full(len(df), np.nan, dtype=np.float64)
    eval_mask = np.zeros(len(df), dtype=bool)
    src_all = source_mask(df, source_scope)
    active_all = active_mask(df)
    # The fold labels are recomputed inside each fold from train-only tail cutoffs.
    for tr_idx, va_idx in fold_indices(df, split, np.zeros(len(df), dtype=int)):
        tr_df = df.iloc[tr_idx].reset_index(drop=True)
        va_df = df.iloc[va_idx].reset_index(drop=True)
        thresholds = thresholds_by_task(tr_df.loc[source_mask(tr_df, source_scope)], q)
        tr_label, tr_eval = label_with_thresholds(tr_df, thresholds, kind)
        va_label, va_eval = label_with_thresholds(va_df, thresholds, kind)
        tr_source = source_mask(tr_df, source_scope) & tr_eval
        if kind == "risk":
            tr_source = source_mask(tr_df, source_scope)
        x_fit = tr_df.loc[tr_source, cols]
        y_fit = tr_label[tr_source]
        pred[va_idx] = fit_predict(model, x_fit, y_fit, va_df[cols])
        va_active = active_mask(va_df) & va_eval
        eval_label[np.asarray(va_idx)[va_active]] = va_label[va_active].astype(float)
        eval_mask[np.asarray(va_idx)[va_active]] = True
    if np.isnan(pred[active_all]).any():
        raise RuntimeError(f"NaN OOF predictions for {source_scope} {split} {kind} q={q}")
    # Non-active/control rows may be NaN if not evaluated downstream; keep them filled.
    pred = np.where(np.isnan(pred), 0.5, pred)
    return clip_prob(pred), eval_label, eval_mask


def fit_full_bad_predict(
    model: Any,
    train_df: pd.DataFrame,
    sub_df: pd.DataFrame,
    cols: list[str],
    source_scope: str,
    kind: str,
    q: float,
) -> np.ndarray:
    src = source_mask(train_df, source_scope)
    thresholds = thresholds_by_task(train_df.loc[src], q)
    labels, eval_mask = label_with_thresholds(train_df, thresholds, kind)
    if kind == "risk":
        fit_mask = src
    else:
        fit_mask = src & eval_mask
    return fit_predict(model, train_df.loc[fit_mask, cols], labels[fit_mask], sub_df[cols])


def policy_amplitudes(df: pd.DataFrame, bad_prob: np.ndarray) -> dict[str, np.ndarray]:
    p = clip_prob(bad_prob)
    task = df["task_name"].astype(str).to_numpy()
    active = np.isin(task, ACTIVE_TASKS)
    n = len(df)
    policies: dict[str, np.ndarray] = {
        "soft_inverse_bad": np.where(active, 1.0 - p, 1.0),
        "soft_inverse_bad_pow2": np.where(active, np.square(1.0 - p), 1.0),
    }
    active_idx = np.where(active)[0]
    order = active_idx[np.argsort(-p[active_idx], kind="mergesort")]
    for k in [10, 13, 21, 25, 40, 50, 75, 100]:
        kk = min(k, len(order))
        amp = np.ones(n, dtype=np.float64)
        amp[order[:kk]] = 0.0
        policies[f"drop_global_top{kk}"] = amp
    for frac in [0.05, 0.10, 0.15, 0.20]:
        kk = max(1, int(round(len(order) * frac)))
        amp = np.ones(n, dtype=np.float64)
        amp[order[:kk]] = 0.0
        policies[f"drop_global_p{int(frac * 100):02d}"] = amp
    for target_task, short in [("q3_e224", "q3"), ("s4_e224", "s4")]:
        idx = np.where(task == target_task)[0]
        target_order = idx[np.argsort(-p[idx], kind="mergesort")]
        for k in [10, 13, 21, 25, 40, 50]:
            kk = min(k, len(target_order))
            amp = np.ones(n, dtype=np.float64)
            amp[target_order[:kk]] = 0.0
            policies[f"drop_{short}_top{kk}"] = amp
        for frac in [0.05, 0.10, 0.15, 0.20]:
            kk = max(1, int(round(len(target_order) * frac)))
            amp = np.ones(n, dtype=np.float64)
            amp[target_order[:kk]] = 0.0
            policies[f"drop_{short}_p{int(frac * 100):02d}"] = amp
    for k in [5, 10, 13, 21, 25]:
        amp = np.ones(n, dtype=np.float64)
        for target_task in ACTIVE_TASKS:
            idx = np.where(task == target_task)[0]
            target_order = idx[np.argsort(-p[idx], kind="mergesort")]
            amp[target_order[: min(k, len(target_order))]] = 0.0
        policies[f"drop_each_top{min(k, len(active_idx))}"] = amp
    return policies


def predict_from_amp(df: pd.DataFrame, amp: np.ndarray) -> np.ndarray:
    base = df["base_prob"].to_numpy(dtype=np.float64)
    full = df["full_prob"].to_numpy(dtype=np.float64)
    return clip_prob(sigmoid(logit(base) + np.asarray(amp, dtype=np.float64) * (logit(full) - logit(base))))


def subject_stats(df: pd.DataFrame, pred: np.ndarray) -> tuple[float, float]:
    active_df = df.loc[active_mask(df)].reset_index(drop=True)
    vals: list[float] = []
    for _, idx in active_df.groupby("subject_id").groups.items():
        arr = np.asarray(list(idx), dtype=int)
        y = active_df.loc[arr, "true_label"].to_numpy(dtype=int)
        base = active_df.loc[arr, "base_prob"].to_numpy(dtype=np.float64)
        vals.append(float(loss_vec(y, pred[active_mask(df)][arr]).mean() - loss_vec(y, base).mean()))
    vv = np.asarray(vals, dtype=np.float64)
    return float(vv.mean()), float(np.mean(vv < 0.0))


def evaluate_oof_policy(
    df: pd.DataFrame,
    spec: dict[str, Any],
    bad_prob: np.ndarray,
    eval_label: np.ndarray,
    amp: np.ndarray,
    policy: str,
) -> dict[str, Any]:
    active = active_mask(df)
    pred = predict_from_amp(df, amp)
    true_y = df["true_label"].to_numpy(dtype=int)
    base = df["base_prob"].to_numpy(dtype=np.float64)
    full = df["full_prob"].to_numpy(dtype=np.float64)
    base_loss = loss_vec(true_y, base)
    full_loss = loss_vec(true_y, full)
    pred_loss = loss_vec(true_y, pred)

    active_full_delta = float(full_loss[active].mean() - base_loss[active].mean())
    active_policy_delta = float(pred_loss[active].mean() - base_loss[active].mean())
    q3_mask = df["task_name"].eq("q3_e224").to_numpy()
    s4_mask = df["task_name"].eq("s4_e224").to_numpy()
    dropped = (np.asarray(amp) < 0.05) & active
    subject_delta, subject_win = subject_stats(df, pred)
    return {
        **spec,
        "policy": policy,
        "tail_auc": safe_auc(eval_label[active], bad_prob[active]),
        "tail_logloss": safe_logloss(eval_label[active], bad_prob[active]),
        "tail_brier": float(
            brier_score_loss(eval_label[active][~pd.isna(eval_label[active])].astype(int), bad_prob[active][~pd.isna(eval_label[active])])
        )
        if (~pd.isna(eval_label[active])).any()
        else np.nan,
        "corr_benefit": corr(bad_prob[active], -df.loc[active, "benefit"].to_numpy(dtype=np.float64)),
        "active_full_delta": active_full_delta,
        "active_policy_delta": active_policy_delta,
        "loss_vs_full": active_policy_delta - active_full_delta,
        "q3_policy_delta": float(pred_loss[q3_mask].mean() - base_loss[q3_mask].mean()),
        "q3_full_delta": float(full_loss[q3_mask].mean() - base_loss[q3_mask].mean()),
        "s4_policy_delta": float(pred_loss[s4_mask].mean() - base_loss[s4_mask].mean()),
        "s4_full_delta": float(full_loss[s4_mask].mean() - base_loss[s4_mask].mean()),
        "subject_delta": subject_delta,
        "subject_win_rate": subject_win,
        "dropped_cells": int(np.sum(dropped)),
        "dropped_q3": int(np.sum(dropped & q3_mask)),
        "dropped_s4": int(np.sum(dropped & s4_mask)),
        "dropped_mean_benefit": float(df.loc[dropped, "benefit"].mean()) if dropped.any() else np.nan,
        "dropped_bad_prob_mean": float(np.mean(bad_prob[dropped])) if dropped.any() else np.nan,
        "mean_amp_active": float(np.mean(np.asarray(amp)[active])),
        "stress_promote": bool(
            active_policy_delta < active_full_delta - 1.0e-5
            and subject_win >= 0.58
            and (not dropped.any() or float(df.loc[dropped, "benefit"].mean()) < 0.0)
        ),
    }


def e224_baseline(
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e95: np.ndarray,
    e154: np.ndarray,
    e224: np.ndarray,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any], pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=E224_FILE,
        anchor_file=E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current E224 capped-Q3/S4 JEPA sensor.",
    )
    graft_rec, graft_targets, _ = e222.pair_audit(spec, "graft_vs_e154", e224, e154, E154_FILE, priors, sample)
    actual_rec, actual_targets, _ = e222.pair_audit(spec, "actual_vs_e95", e224, e95, E95_FILE, priors, sample)
    return graft_rec, graft_targets, actual_rec, actual_targets


def apply_to_submission(e154: np.ndarray, e224: np.ndarray, sub_df: pd.DataFrame, amp: np.ndarray) -> np.ndarray:
    out_logit = logit(e224).copy()
    anchor_logit = logit(e154)
    e224_logit = logit(e224)
    task = sub_df["task_name"].astype(str).to_numpy()
    for target_task, target_idx in [("q3_e224", Q3_IDX), ("s4_e224", S4_IDX)]:
        idx = np.where(task == target_task)[0]
        if len(idx) != e224.shape[0]:
            raise RuntimeError(f"unexpected test row count for {target_task}: {len(idx)}")
        out_logit[:, target_idx] = anchor_logit[:, target_idx] + amp[idx] * (
            e224_logit[:, target_idx] - anchor_logit[:, target_idx]
        )
    return clip_prob(sigmoid(out_logit))


def materialize(sample: pd.DataFrame, pred: np.ndarray, variant_id: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in variant_id)[:80]
    file_name = f"submission_e237_cell_decisive_{safe_id}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def q3_overlap_metrics(sub_df: pd.DataFrame, amp: np.ndarray) -> dict[str, Any]:
    q3_idx = np.where(sub_df["task_name"].eq("q3_e224").to_numpy())[0]
    q3_dropped = set(np.where(amp[q3_idx] < 0.05)[0].astype(int).tolist())
    priors = e234.q3_prior_sets()
    out: dict[str, Any] = {}
    for name, prior in priors.items():
        out[f"{name}_overlap"] = int(len(q3_dropped & prior))
        out[f"{name}_jaccard"] = float(len(q3_dropped & prior) / max(len(q3_dropped | prior), 1))
    return out


def target_metric(targets: pd.DataFrame, candidate_id: str, target: str, col: str, default: float = np.nan) -> float:
    part = targets[
        targets["candidate_id"].eq(candidate_id)
        & targets["pair_kind"].eq("graft_vs_e154")
        & targets["target"].eq(target)
    ]
    if part.empty or col not in part.columns:
        return default
    return float(part[col].iloc[0])


def scan_materializations(
    oof_scan: pd.DataFrame,
    train_df: pd.DataFrame,
    sub_df: pd.DataFrame,
    feats: dict[str, list[str]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = e230.load_prob(E95_FILE, sample)
    e154 = e230.load_prob(E154_FILE, sample)
    e224 = e230.load_prob(E224_FILE, sample)
    base_rec, base_targets, base_actual_rec, _ = e224_baseline(sample, priors, e95, e154, e224)
    base_q3_top = target_metric(base_targets, "e224_original", "Q3", "top1_over_abs_expected", 9.0)
    base_q3_adverse = target_metric(base_targets, "e224_original", "Q3", "adverse_delta", 9.0)
    base_s4_expected = target_metric(base_targets, "e224_original", "S4", "expected_focus", 0.0)

    # Keep a deliberately broad but bounded set: OOF-improving policies plus best
    # bad-cell predictors that may improve test stress even if OOF loss is flat.
    pool = pd.concat(
        [
            oof_scan[oof_scan["stress_promote"].astype(bool)],
            oof_scan.sort_values("loss_vs_full").head(80),
            oof_scan.sort_values("tail_auc", ascending=False).head(40),
        ],
        ignore_index=True,
    ).drop_duplicates(["source_scope", "view", "model", "split", "target_kind", "tail_q", "policy"])
    pool = pool.sort_values(["stress_promote", "loss_vs_full", "tail_auc"], ascending=[False, True, False]).head(120)

    models = model_defs()
    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for _, row in pool.iterrows():
        spec_key = {
            "source_scope": str(row["source_scope"]),
            "view": str(row["view"]),
            "model": str(row["model"]),
            "split": str(row["split"]),
            "target_kind": str(row["target_kind"]),
            "tail_q": float(row["tail_q"]),
        }
        cols = feats[spec_key["view"]]
        bad_prob = fit_full_bad_predict(
            models[spec_key["model"]],
            train_df,
            sub_df,
            cols,
            spec_key["source_scope"],
            spec_key["target_kind"],
            spec_key["tail_q"],
        )
        amp = policy_amplitudes(sub_df, bad_prob)[str(row["policy"])]
        pred = apply_to_submission(e154, e224, sub_df, amp)
        variant_id = (
            f"{spec_key['source_scope']}_{spec_key['view']}_{spec_key['model']}_{spec_key['split']}_"
            f"{spec_key['target_kind']}_q{spec_key['tail_q']:.2f}_{row['policy']}"
        ).replace(".", "p")
        q3_dropped = int(np.sum((amp < 0.05) & sub_df["task_name"].eq("q3_e224").to_numpy()))
        s4_dropped = int(np.sum((amp < 0.05) & sub_df["task_name"].eq("s4_e224").to_numpy()))
        meta = {
            **spec_key,
            "policy": str(row["policy"]),
            "q3_dropped_cells": q3_dropped,
            "s4_dropped_cells": s4_dropped,
            "oof_loss_vs_full": float(row["loss_vs_full"]),
            "oof_active_policy_delta": float(row["active_policy_delta"]),
            "oof_tail_auc": float(row["tail_auc"]),
            "oof_subject_win_rate": float(row["subject_win_rate"]),
            **q3_overlap_metrics(sub_df, amp),
        }
        spec = e222.Candidate(
            candidate_id=variant_id,
            file_name=variant_id,
            anchor_file=E154_FILE,
            family="e237_cell_decisive_q3s4",
            status="generated",
            note="Cell-level bad-tail predictor rolls selected E224 Q3/S4 cells back toward E154.",
        )
        for pair_kind, base_name, base in [
            ("graft_vs_e154", E154_FILE, e154),
            ("actual_vs_e95", E95_FILE, e95),
        ]:
            rec, targets, _ = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
            rec.update(meta)
            rec["baseline_expected_focus"] = float(base_rec["expected_focus"])
            rec["baseline_adverse_delta"] = float(base_rec["adverse_delta"])
            rec["baseline_support_prob_focus_swing_weighted"] = float(base_rec["support_prob_focus_swing_weighted"])
            rec["expected_loss_vs_e224"] = float(rec["expected_focus"] - base_rec["expected_focus"])
            rec["adverse_reduction_vs_e224"] = float(base_rec["adverse_delta"] - rec["adverse_delta"])
            rec["support_gain_vs_e224"] = float(
                rec["support_prob_focus_swing_weighted"] - base_rec["support_prob_focus_swing_weighted"]
            )
            if pair_kind == "actual_vs_e95":
                rec["actual_expected_delta_vs_e224"] = float(rec["expected_focus"] - base_actual_rec["expected_focus"])
                rec["actual_adverse_reduction_vs_e224"] = float(base_actual_rec["adverse_delta"] - rec["adverse_delta"])
                rec["actual_support_gain_vs_e224"] = float(
                    rec["support_prob_focus_swing_weighted"]
                    - base_actual_rec["support_prob_focus_swing_weighted"]
                )
            summary_rows.append(rec)
            if not targets.empty:
                targets = targets.copy()
                for key, val in meta.items():
                    if not isinstance(val, (list, dict, np.ndarray)):
                        targets[key] = val
                target_parts.append(targets)

    summary = pd.DataFrame(summary_rows)
    targets = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    if summary.empty:
        return summary, targets, pd.DataFrame()

    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].copy()
    actual_summary = summary[summary["pair_kind"].eq("actual_vs_e95")][
        [
            "candidate_id",
            "expected_focus",
            "adverse_delta",
            "support_prob_focus_swing_weighted",
            "actual_expected_delta_vs_e224",
            "actual_adverse_reduction_vs_e224",
            "actual_support_gain_vs_e224",
        ]
    ].rename(
        columns={
            "expected_focus": "actual_expected_focus",
            "adverse_delta": "actual_adverse_delta",
            "support_prob_focus_swing_weighted": "actual_support_prob_focus_swing_weighted",
        }
    )
    q3_metrics = targets[
        targets["pair_kind"].eq("graft_vs_e154") & targets["target"].eq("Q3")
    ][["candidate_id", "top1_over_abs_expected", "adverse_delta", "expected_focus"]].rename(
        columns={
            "top1_over_abs_expected": "q3_top1_over_abs_expected",
            "adverse_delta": "q3_adverse_delta",
            "expected_focus": "q3_expected_focus",
        }
    )
    s4_metrics = targets[
        targets["pair_kind"].eq("graft_vs_e154") & targets["target"].eq("S4")
    ][["candidate_id", "top1_over_abs_expected", "adverse_delta", "expected_focus"]].rename(
        columns={
            "top1_over_abs_expected": "s4_top1_over_abs_expected",
            "adverse_delta": "s4_adverse_delta",
            "expected_focus": "s4_expected_focus",
        }
    )
    actual_cols = [
        "actual_expected_focus",
        "actual_adverse_delta",
        "actual_support_prob_focus_swing_weighted",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
    ]
    graft = graft.drop(columns=[c for c in actual_cols if c in graft.columns], errors="ignore")
    graft = graft.merge(q3_metrics, on="candidate_id", how="left").merge(s4_metrics, on="candidate_id", how="left")
    graft = graft.merge(actual_summary, on="candidate_id", how="left")
    summary_merge_cols = [
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "q3_expected_focus",
        "s4_top1_over_abs_expected",
        "s4_adverse_delta",
        "s4_expected_focus",
        "actual_expected_focus",
        "actual_adverse_delta",
        "actual_support_prob_focus_swing_weighted",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
    ]
    summary = summary.drop(columns=[c for c in summary_merge_cols if c in summary.columns], errors="ignore").merge(
        graft[["candidate_id", *summary_merge_cols]],
        on="candidate_id",
        how="left",
    )
    summary["e237_gate"] = (
        summary["pair_kind"].eq("graft_vs_e154")
        & (summary["expected_loss_vs_e224"] <= 0.000080)
        & (summary["adverse_reduction_vs_e224"] >= 0.000150)
        & (summary["support_gain_vs_e224"] > 0.0)
        & (summary["q3_top1_over_abs_expected"] <= min(base_q3_top, 0.875120489))
        & (summary["q3_adverse_delta"] <= base_q3_adverse)
        & (summary["s4_expected_focus"] <= base_s4_expected + 0.000080)
        & (summary["actual_expected_delta_vs_e224"] <= 0.000020)
        & (summary["actual_adverse_reduction_vs_e224"] >= 0.000150)
        & (summary["actual_support_gain_vs_e224"] > 0.0)
    )
    summary["e237_score"] = (
        -summary["expected_loss_vs_e224"].fillna(9.0) * 140.0
        + summary["adverse_reduction_vs_e224"].fillna(0.0) * 100.0
        + summary["support_gain_vs_e224"].fillna(0.0) * 0.08
        - np.maximum(summary["q3_top1_over_abs_expected"].fillna(9.0) - base_q3_top, 0.0) * 0.04
        - np.maximum(summary["oof_loss_vs_full"].fillna(0.0), 0.0) * 30.0
    )
    selected = summary[summary["e237_gate"].astype(bool)].sort_values("e237_score", ascending=False).copy()
    selected["submission_file"] = ""
    for idx, rec in selected.iterrows():
        row = pool[
            (pool["source_scope"].astype(str).eq(str(rec["source_scope"])))
            & (pool["view"].astype(str).eq(str(rec["view"])))
            & (pool["model"].astype(str).eq(str(rec["model"])))
            & (pool["split"].astype(str).eq(str(rec["split"])))
            & (pool["target_kind"].astype(str).eq(str(rec["target_kind"])))
            & (np.isclose(pool["tail_q"].astype(float), float(rec["tail_q"])))
            & (pool["policy"].astype(str).eq(str(rec["policy"])))
        ].iloc[0]
        spec_key = {
            "source_scope": str(row["source_scope"]),
            "view": str(row["view"]),
            "model": str(row["model"]),
            "split": str(row["split"]),
            "target_kind": str(row["target_kind"]),
            "tail_q": float(row["tail_q"]),
        }
        bad_prob = fit_full_bad_predict(
            models[spec_key["model"]],
            train_df,
            sub_df,
            feats[spec_key["view"]],
            spec_key["source_scope"],
            spec_key["target_kind"],
            spec_key["tail_q"],
        )
        amp = policy_amplitudes(sub_df, bad_prob)[str(row["policy"])]
        pred = apply_to_submission(e154, e224, sub_df, amp)
        selected.loc[idx, "submission_file"] = materialize(sample, pred, str(rec["candidate_id"]))

    summary = summary.sort_values(["pair_kind", "e237_gate", "e237_score"], ascending=[True, False, False])
    return summary, targets, selected


def oof_scan(train_df: pd.DataFrame, feats: dict[str, list[str]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    models = model_defs()
    train_df = train_df[train_df["task_name"].isin(CONTROL_TASKS)].reset_index(drop=True)
    for source_scope in ["q3s4", "all3"]:
        for view in ["movement", "latent_no_targetid", "latent_with_targetid"]:
            cols = feats[view]
            for model_name, model in models.items():
                for split in ["row5", "subject5"]:
                    for kind in ["risk", "contrast"]:
                        for q in [0.10, 0.20]:
                            spec = {
                                "source_scope": source_scope,
                                "view": view,
                                "model": model_name,
                                "split": split,
                                "target_kind": kind,
                                "tail_q": q,
                            }
                            bad_prob, eval_label, _ = oof_bad_predict(model, train_df, cols, source_scope, split, kind, q)
                            for policy, amp in policy_amplitudes(train_df, bad_prob).items():
                                rows.append(evaluate_oof_policy(train_df, spec, bad_prob, eval_label, amp, policy))
    return pd.DataFrame(rows).sort_values(["stress_promote", "loss_vs_full"], ascending=[False, True])


def write_report(oof: pd.DataFrame, material: pd.DataFrame, targets: pd.DataFrame, selected: pd.DataFrame) -> None:
    promoted = oof[oof["stress_promote"].astype(bool)].sort_values("loss_vs_full")
    best_oof = oof.sort_values("loss_vs_full").head(30)
    graft = material[material["pair_kind"].eq("graft_vs_e154")].sort_values("e237_score", ascending=False)
    selected_view = selected.sort_values("e237_score", ascending=False) if not selected.empty else pd.DataFrame()
    q3_only = graft[(graft["q3_dropped_cells"] > 0) & (graft["s4_dropped_cells"] == 0)]
    s4_only = graft[(graft["s4_dropped_cells"] > 0) & (graft["q3_dropped_cells"] == 0)]
    both = graft[(graft["s4_dropped_cells"] > 0) & (graft["q3_dropped_cells"] > 0)]
    target_cols = [
        "candidate_id",
        "target",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    mat_cols = [
        "candidate_id",
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_loss_vs_full",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_delta",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "e230_q3_risk_top21_overlap",
        "e237_gate",
        "e237_score",
        "submission_file",
    ]
    oof_cols = [
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "tail_auc",
        "corr_benefit",
        "active_policy_delta",
        "loss_vs_full",
        "q3_policy_delta",
        "s4_policy_delta",
        "subject_win_rate",
        "dropped_cells",
        "dropped_q3",
        "dropped_s4",
        "stress_promote",
    ]
    lines = [
        "# E237 Cell-Level Decisive JEPA Target",
        "",
        "## Question",
        "",
        "Can Q3/S4 public-safe tail translation be learned at row-target cell level after row-level E234/E236 masks failed?",
        "",
        "## Observed Read",
        "",
        f"- OOF policy rows: `{len(oof)}`.",
        f"- OOF stress-promoted rows: `{int(oof['stress_promote'].sum())}`.",
        f"- materialized scan rows: `{len(material)}` including actual-vs-E95 duplicates.",
        f"- graft-side gate passes: `{int(material['e237_gate'].sum()) if 'e237_gate' in material else 0}`.",
        f"- selected rows/files: `{len(selected)}` / `{selected['submission_file'].nunique() if 'submission_file' in selected else 0}`.",
        "",
        "A pass must beat or preserve E224's local cell-level signal and then improve both graft-vs-E154 and actual-vs-E95 public-free stress: expected body, adverse capacity, support probability, and Q3 top-cell concentration.",
        "",
        "## Selected",
        "",
        md_table(selected_view, mat_cols, n=30),
        "",
        "## Best Graft Rows",
        "",
        md_table(graft, mat_cols, n=30),
        "",
        "## Q3-Only Rows",
        "",
        md_table(q3_only, mat_cols, n=20),
        "",
        "## S4-Only Rows",
        "",
        md_table(s4_only, mat_cols, n=20),
        "",
        "## Q3+S4 Rows",
        "",
        md_table(both, mat_cols, n=20),
        "",
        "## Best OOF Policies",
        "",
        md_table(best_oof, oof_cols, n=40),
        "",
        "## OOF-Promoted Policies",
        "",
        md_table(promoted, oof_cols, n=40),
        "",
        "## Target Breakdown",
        "",
        md_table(targets.sort_values(["candidate_id", "target"]).head(80), target_cols, n=80),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.extend(
            [
                "- No E237 submission is selected.",
                "- Cell-level decisive labels produce useful local rankings, but they do not yet recover a submission-safe Q3/S4 tail law on E224.",
                "- This keeps E224/E230 policy unchanged and pushes the next JEPA target away from row/cell tail classification toward block/world-state or decisive-label objectives with stronger public-free geometry.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one E237 file passed the public-free gate.",
                "- Submit only the top selected file first, because its public result tests whether cell-level decisive labels finally replace E230's external Q3 intervention.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    _, train_long, sub_long, feats = build_frames()
    train_df = train_long[train_long["task_name"].isin(CONTROL_TASKS)].reset_index(drop=True)
    sub_df = sub_long[sub_long["task_name"].isin(ACTIVE_TASKS)].reset_index(drop=True)
    oof = oof_scan(train_df, feats)
    material, targets, selected = scan_materializations(oof, train_df, sub_df, feats)
    oof.to_csv(OOF_OUT, index=False)
    material.to_csv(MATERIALIZATION_OUT, index=False)
    targets.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(oof, material, targets, selected)
    return oof, material, targets, selected


def main() -> None:
    oof, material, _, selected = run()
    print("[E237 selected]")
    if selected.empty:
        print("none")
    else:
        print(
            selected[
                [
                    "candidate_id",
                    "expected_loss_vs_e224",
                    "adverse_reduction_vs_e224",
                    "support_gain_vs_e224",
                    "actual_expected_delta_vs_e224",
                    "actual_adverse_reduction_vs_e224",
                    "actual_support_gain_vs_e224",
                    "q3_top1_over_abs_expected",
                    "submission_file",
                ]
            ].to_string(index=False)
        )
    print("\n[E237 best graft rows]")
    graft = material[material["pair_kind"].eq("graft_vs_e154")].sort_values("e237_score", ascending=False)
    cols = [
        "candidate_id",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "oof_loss_vs_full",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "e237_gate",
    ]
    print(graft[cols].head(10).to_string(index=False))
    print("\n[E237 best OOF policies]")
    cols2 = [
        "source_scope",
        "view",
        "model",
        "split",
        "target_kind",
        "tail_q",
        "policy",
        "tail_auc",
        "loss_vs_full",
        "subject_win_rate",
        "stress_promote",
    ]
    print(oof.sort_values("loss_vs_full")[cols2].head(10).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
