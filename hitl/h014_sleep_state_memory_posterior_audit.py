#!/usr/bin/env python3
"""H014: subject-time memory stress for the H012 public-equation posterior.

H012 proved that public LB observations can be inverted into a powerful hidden
public-state posterior.  H014 asks the next private-risk question: do the
high-impact H012 cells also agree with same-subject sleep-state/sensor-quality
memory, or did H012 mostly learn a public-subset equation artifact?
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H012 = HITL / "h012_public_equation_jepa_jackpot"
H013 = HITL / "h013_raw_human_state_jepa_gate"
H014 = HITL / "h014_sleep_state_memory_posterior_audit"
H014.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


EPS = 1.0e-6
CURRENT = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
H012_SUB = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"

FEATURES_IN = H013 / "h013_human_state_features.csv"
POSTERIOR_IN = H012 / "h012_cell_posterior.csv"

CELL_OUT = H014 / "h014_memory_cells.csv"
ROW_OUT = H014 / "h014_memory_rows.csv"
TARGET_OUT = H014 / "h014_target_summary.csv"
BUCKET_OUT = H014 / "h014_bucket_summary.csv"
CANDIDATE_OUT = H014 / "h014_candidates.csv"
REPORT_OUT = H014 / "h014_report.md"


@dataclass(frozen=True)
class CandidateSpec:
    candidate_id: str
    min_mem_q: float
    min_rel_q: float
    max_cells: int
    mode: str


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def quantile01(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if len(x) <= 1:
        return np.zeros_like(x)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    ranks[order] = np.arange(len(x), dtype=np.float64)
    return ranks / (len(x) - 1.0)


def bce(prob: np.ndarray, y_prob: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    y = clip_prob(y_prob)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def load_base_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(KEYS).reset_index(drop=True)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = load_sub(CURRENT, sample)
    h012 = load_sub(H012_SUB, sample)
    features = pd.read_csv(FEATURES_IN, parse_dates=["sleep_date", "lifelog_date", "date"])
    features = features.sort_values(KEYS).reset_index(drop=True)
    return train, sample, base, h012, features


def feature_groups(features: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
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
        "hr_",
        "usage_late",
        "usage_prebed",
        "usage_early",
        "m_activity_active_late",
        "m_activity_active_early",
    )
    quality_tokens = (
        "count",
        "obs",
        "rows",
        "events",
        "points",
        "list_len",
        "wifi_",
        "ble_",
        "ambience_",
    )
    sleep_cols = [c for c in numeric if any(tok in c for tok in sleep_tokens)]
    quality_cols = [c for c in numeric if any(tok in c for tok in quality_tokens)]
    state_cols = sorted(set(sleep_cols + quality_cols + [c for c in numeric if c.startswith("usage_cat_")]))
    return sleep_cols, quality_cols, state_cols


def standardized_matrix(
    features: pd.DataFrame,
    cols: list[str],
    train_mask: np.ndarray,
) -> np.ndarray:
    if not cols:
        return np.zeros((len(features), 1), dtype=np.float64)
    x = features[cols].to_numpy(dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    mu = x[train_mask].mean(axis=0)
    sigma = x[train_mask].std(axis=0)
    sigma = np.where(sigma < 1.0e-9, 1.0, sigma)
    return (x - mu) / sigma


def weighted_prob(y: np.ndarray, weights: np.ndarray, fallback: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    weights = np.asarray(weights, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    total = float(weights.sum())
    if total <= 1.0e-12:
        return fallback.copy(), 0.0, 0.0, 0.0
    prob = (weights[:, None] * y).sum(axis=0)
    prob = (prob + 0.5) / (total + 1.0)
    ess = float(total * total / (np.sum(weights * weights) + 1.0e-12))
    max_w = float(weights.max() / total)
    entropy = float(-(weights / total * np.log(weights / total + 1.0e-12)).sum())
    return np.clip(prob, EPS, 1.0 - EPS), total, ess, max_w + 0.01 * entropy


def memory_for_test_rows(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    features: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    split = features["split"].astype(str).to_numpy()
    train_mask = split == "train"
    test_mask = split == "test"
    sleep_cols, quality_cols, _ = feature_groups(features)
    z_sleep = standardized_matrix(features, sleep_cols, train_mask)
    z_quality = standardized_matrix(features, quality_cols, train_mask)
    z_state = np.concatenate([z_sleep, z_quality], axis=1)
    z_state = np.nan_to_num(z_state, nan=0.0, posinf=0.0, neginf=0.0)

    feat_train = features.loc[train_mask].reset_index(drop=True)
    feat_test = features.loc[test_mask].reset_index(drop=True)
    if not feat_test[KEYS].equals(sample[KEYS]):
        raise ValueError("H013 feature test rows do not align with submission sample")
    if not feat_train[KEYS].equals(train[KEYS]):
        raise ValueError("H013 feature train rows do not align with train labels")

    y_train = train[TARGETS].to_numpy(dtype=np.float64)
    global_prior = np.clip((y_train.sum(axis=0) + 0.5) / (len(y_train) + 1.0), EPS, 1.0 - EPS)
    z_sleep_tr = z_sleep[train_mask]
    z_sleep_te = z_sleep[test_mask]
    z_quality_tr = z_quality[train_mask]
    z_quality_te = z_quality[test_mask]
    z_state_tr = z_state[train_mask]
    z_state_te = z_state[test_mask]

    mem_full = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    mem_date = np.zeros_like(mem_full)
    mem_state = np.zeros_like(mem_full)
    row_rows: list[dict[str, Any]] = []
    for i, rec in sample.iterrows():
        sid = str(rec["subject_id"])
        same = train["subject_id"].astype(str).eq(sid).to_numpy()
        past = train["lifelog_date"].to_numpy(dtype="datetime64[ns]") < np.datetime64(rec["lifelog_date"])
        idx = np.flatnonzero(same & past)
        if len(idx) == 0:
            idx = np.flatnonzero(same)
        if len(idx) == 0:
            fallback = global_prior
            mem_full[i] = fallback
            mem_date[i] = fallback
            mem_state[i] = fallback
            row_rows.append(
                {
                    **{k: rec[k] for k in KEYS},
                    "neighbor_count": 0,
                    "min_day_gap": np.nan,
                    "full_weight_sum": 0.0,
                    "full_ess": 0.0,
                    "full_reliability": 0.0,
                    "sleep_dist_min": np.nan,
                    "quality_dist_min": np.nan,
                }
            )
            continue

        gaps = (
            np.datetime64(rec["lifelog_date"]) - train.loc[idx, "lifelog_date"].to_numpy(dtype="datetime64[ns]")
        ).astype("timedelta64[D]").astype(float)
        gaps = np.maximum(gaps, 0.0)
        date_w = np.exp(-gaps / 7.0)

        ds = ((z_sleep_tr[idx] - z_sleep_te[i]) ** 2).mean(axis=1)
        dq = ((z_quality_tr[idx] - z_quality_te[i]) ** 2).mean(axis=1)
        dst = ((z_state_tr[idx] - z_state_te[i]) ** 2).mean(axis=1)
        s_scale = max(float(np.median(ds)), 1.0e-6)
        q_scale = max(float(np.median(dq)), 1.0e-6)
        st_scale = max(float(np.median(dst)), 1.0e-6)
        w_date = date_w
        w_state = date_w * np.exp(-dst / st_scale)
        w_full = date_w * np.exp(-ds / s_scale) * np.exp(-dq / q_scale)

        subj_fallback = np.clip((y_train[idx].sum(axis=0) + 0.5) / (len(idx) + 1.0), EPS, 1.0 - EPS)
        mem_date[i], date_sum, date_ess, date_rel = weighted_prob(y_train[idx], w_date, subj_fallback)
        mem_state[i], state_sum, state_ess, state_rel = weighted_prob(y_train[idx], w_state, mem_date[i])
        mem_full[i], full_sum, full_ess, full_rel = weighted_prob(y_train[idx], w_full, mem_state[i])
        row_rows.append(
            {
                **{k: rec[k] for k in KEYS},
                "neighbor_count": int(len(idx)),
                "min_day_gap": float(np.min(gaps)),
                "date_weight_sum": date_sum,
                "date_ess": date_ess,
                "date_reliability": date_rel,
                "state_weight_sum": state_sum,
                "state_ess": state_ess,
                "state_reliability": state_rel,
                "full_weight_sum": full_sum,
                "full_ess": full_ess,
                "full_reliability": full_rel,
                "sleep_dist_min": float(np.min(ds)),
                "quality_dist_min": float(np.min(dq)),
            }
        )

    rows = pd.DataFrame(row_rows)
    rows["full_reliability_q"] = quantile01(rows["full_reliability"].to_numpy(dtype=np.float64))
    rows["full_ess_q"] = quantile01(rows["full_ess"].to_numpy(dtype=np.float64))
    rows.to_csv(ROW_OUT, index=False)
    return rows, mem_full, mem_date, mem_state, z_state_te


def posterior_matrix(sample: pd.DataFrame, base_prob: np.ndarray) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    posterior = pd.read_csv(POSTERIOR_IN)
    q = base_prob.copy()
    score = np.zeros_like(base_prob)
    consistency = np.zeros_like(base_prob)
    target_to_i = {t: i for i, t in enumerate(TARGETS)}
    for rec in posterior.to_dict("records"):
        r = int(rec["row"])
        t = target_to_i[str(rec["target"])]
        q[r, t] = float(rec["posterior_prob"])
        score[r, t] = float(rec["cell_score"])
        consistency[r, t] = float(rec["direction_consistency"])
    return np.clip(q, EPS, 1.0 - EPS), score, posterior


def build_cell_table(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h012_prob: np.ndarray,
    q: np.ndarray,
    cell_score: np.ndarray,
    rows: pd.DataFrame,
    mem_full: np.ndarray,
    mem_date: np.ndarray,
    mem_state: np.ndarray,
) -> pd.DataFrame:
    base_logit = logit(base_prob)
    h012_logit = logit(h012_prob)
    mem_logit = logit(mem_full)
    h012_move = h012_logit - base_logit
    posterior_move = logit(q) - base_logit
    mem_move = mem_logit - base_logit
    changed = np.abs(h012_move) > 1.0e-12
    cell_delta = bce(h012_prob, q) - bce(base_prob, q)

    records: list[dict[str, Any]] = []
    for i in range(len(sample)):
        for ti, target in enumerate(TARGETS):
            records.append(
                {
                    "row": i,
                    "target": target,
                    "subject_id": sample.loc[i, "subject_id"],
                    "sleep_date": sample.loc[i, "sleep_date"],
                    "lifelog_date": sample.loc[i, "lifelog_date"],
                    "base_prob": base_prob[i, ti],
                    "h012_prob": h012_prob[i, ti],
                    "posterior_prob": q[i, ti],
                    "memory_prob_full": mem_full[i, ti],
                    "memory_prob_date": mem_date[i, ti],
                    "memory_prob_state": mem_state[i, ti],
                    "h012_changed": bool(changed[i, ti]),
                    "h012_logit_delta": h012_move[i, ti],
                    "posterior_logit_delta": posterior_move[i, ti],
                    "memory_logit_delta": mem_move[i, ti],
                    "memory_alignment": mem_move[i, ti] * h012_move[i, ti],
                    "memory_agrees_h012": bool(np.sign(mem_move[i, ti]) == np.sign(h012_move[i, ti]) and changed[i, ti]),
                    "memory_disagrees_h012": bool(np.sign(mem_move[i, ti]) == -np.sign(h012_move[i, ti]) and changed[i, ti]),
                    "posterior_cell_delta": cell_delta[i, ti],
                    "posterior_gain": -cell_delta[i, ti],
                    "cell_score": cell_score[i, ti],
                    "row_full_reliability": rows.loc[i, "full_reliability"],
                    "row_full_reliability_q": rows.loc[i, "full_reliability_q"],
                    "row_full_ess": rows.loc[i, "full_ess"],
                    "neighbor_count": rows.loc[i, "neighbor_count"],
                    "min_day_gap": rows.loc[i, "min_day_gap"],
                }
            )
    cells = pd.DataFrame(records)
    changed_cells = cells["h012_changed"].to_numpy()
    cells["memory_alignment_q"] = 0.0
    cells.loc[changed_cells, "memory_alignment_q"] = quantile01(cells.loc[changed_cells, "memory_alignment"].to_numpy())
    cells["private_safe_score"] = (
        cells["memory_alignment_q"]
        + 0.50 * cells["row_full_reliability_q"]
        + 0.20 * quantile01(cells["cell_score"].to_numpy(dtype=np.float64))
    )
    cells.to_csv(CELL_OUT, index=False)
    return cells


def summarize(cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    changed = cells[cells["h012_changed"]].copy()
    total_gain = float(changed["posterior_gain"].sum())
    target_rows: list[dict[str, Any]] = []
    for target, part in changed.groupby("target", sort=False):
        gain = float(part["posterior_gain"].sum())
        agree = part["memory_agrees_h012"].to_numpy(dtype=bool)
        disagree = part["memory_disagrees_h012"].to_numpy(dtype=bool)
        target_rows.append(
            {
                "target": target,
                "changed_cells": int(len(part)),
                "posterior_gain_sum": gain,
                "posterior_gain_share": gain / max(total_gain, 1.0e-12),
                "memory_agree_rate": float(agree.mean()) if len(part) else 0.0,
                "memory_disagree_rate": float(disagree.mean()) if len(part) else 0.0,
                "memory_agree_gain_share_within_target": float(part.loc[agree, "posterior_gain"].sum() / max(gain, 1.0e-12)),
                "memory_disagree_gain_share_within_target": float(part.loc[disagree, "posterior_gain"].sum() / max(gain, 1.0e-12)),
                "mean_alignment": float(part["memory_alignment"].mean()),
                "mean_reliability_q": float(part["row_full_reliability_q"].mean()),
            }
        )
    target_summary = pd.DataFrame(target_rows).sort_values("posterior_gain_sum", ascending=False)
    target_summary.to_csv(TARGET_OUT, index=False)

    buckets: list[dict[str, Any]] = []
    for name, mask in {
        "agree": changed["memory_agrees_h012"],
        "disagree": changed["memory_disagrees_h012"],
        "high_align_q75": changed["memory_alignment_q"] >= 0.75,
        "high_align_q60": changed["memory_alignment_q"] >= 0.60,
        "high_rel_q60": changed["row_full_reliability_q"] >= 0.60,
        "high_align_and_rel": (changed["memory_alignment_q"] >= 0.60) & (changed["row_full_reliability_q"] >= 0.60),
        "low_align_or_low_rel": (changed["memory_alignment_q"] < 0.35) | (changed["row_full_reliability_q"] < 0.35),
    }.items():
        part = changed[mask].copy()
        buckets.append(
            {
                "bucket": name,
                "cells": int(len(part)),
                "cell_share": float(len(part) / max(len(changed), 1)),
                "posterior_gain_sum": float(part["posterior_gain"].sum()),
                "posterior_gain_share": float(part["posterior_gain"].sum() / max(total_gain, 1.0e-12)),
                "mean_gain": float(part["posterior_gain"].mean()) if len(part) else 0.0,
                "mean_alignment": float(part["memory_alignment"].mean()) if len(part) else 0.0,
                "targets": ",".join(sorted(part["target"].unique())) if len(part) else "",
            }
        )
    bucket_summary = pd.DataFrame(buckets)
    bucket_summary.to_csv(BUCKET_OUT, index=False)
    return target_summary, bucket_summary


def candidate_specs() -> list[CandidateSpec]:
    return [
        CandidateSpec("memory_compat_q60_rel40_k900", 0.60, 0.40, 900, "keep_h012"),
        CandidateSpec("memory_compat_q65_rel50_k750", 0.65, 0.50, 750, "keep_h012"),
        CandidateSpec("memory_compat_q70_rel55_k600", 0.70, 0.55, 600, "keep_h012"),
        CandidateSpec("memory_compat_q75_rel60_k450", 0.75, 0.60, 450, "keep_h012"),
        CandidateSpec("memory_conflict_revert_q35_k300", 0.35, 0.00, 300, "revert_conflict"),
    ]


def write_candidate(sample: pd.DataFrame, base: pd.DataFrame, h012: pd.DataFrame, cells: pd.DataFrame, spec: CandidateSpec) -> tuple[Path, dict[str, Any]]:
    out = base.copy()
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    mask = np.zeros_like(base_prob, dtype=bool)
    changed = cells[cells["h012_changed"]].copy()
    if spec.mode == "keep_h012":
        pool = changed[
            (changed["memory_alignment_q"] >= spec.min_mem_q)
            & (changed["row_full_reliability_q"] >= spec.min_rel_q)
            & (changed["memory_agrees_h012"])
        ].copy()
        pool = pool.sort_values(["posterior_gain", "private_safe_score"], ascending=False).head(spec.max_cells)
        for rec in pool.to_dict("records"):
            mask[int(rec["row"]), TARGETS.index(str(rec["target"]))] = True
        out[TARGETS] = base_prob
        out_arr = out[TARGETS].to_numpy(dtype=np.float64)
        out_arr[mask] = h012_prob[mask]
        out[TARGETS] = out_arr
    elif spec.mode == "revert_conflict":
        out[TARGETS] = h012_prob
        pool = changed[
            (changed["memory_alignment_q"] <= spec.min_mem_q)
            | (changed["memory_disagrees_h012"])
        ].copy()
        pool = pool.sort_values(["posterior_gain", "cell_score"], ascending=False).head(spec.max_cells)
        revert = np.zeros_like(base_prob, dtype=bool)
        for rec in pool.to_dict("records"):
            revert[int(rec["row"]), TARGETS.index(str(rec["target"]))] = True
        out_arr = out[TARGETS].to_numpy(dtype=np.float64)
        out_arr[revert] = base_prob[revert]
        out[TARGETS] = out_arr
        mask = np.abs(out_arr - base_prob) > 1.0e-12
    else:
        raise ValueError(spec.mode)

    path = H014 / f"submission_h014_{spec.candidate_id}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    root_path = ROOT / f"submission_h014_{spec.candidate_id}_{short_hash(out)}_uploadsafe.csv"
    shutil.copyfile(path, root_path)

    q = cells.pivot(index="row", columns="target", values="posterior_prob").reindex(range(len(sample)))[TARGETS].to_numpy()
    prob = out[TARGETS].to_numpy(dtype=np.float64)
    h012_delta = float(np.mean(bce(h012_prob, q) - bce(base_prob, q)))
    cand_delta = float(np.mean(bce(prob, q) - bce(base_prob, q)))
    changed_cells = int(mask.sum())
    kept_gain = float(-cand_delta / max(-h012_delta, 1.0e-12))
    return root_path, {
        "candidate_id": spec.candidate_id,
        "mode": spec.mode,
        "file": rel(root_path),
        "changed_cells": changed_cells,
        "changed_rows": int(mask.any(axis=1).sum()),
        "posterior_delta_vs_e247": cand_delta,
        "h012_posterior_delta_vs_e247": h012_delta,
        "kept_h012_posterior_gain_rate": kept_gain,
        "mean_abs_prob_delta_vs_h012": float(np.mean(np.abs(prob - h012_prob))),
        "max_abs_prob_delta_vs_h012": float(np.max(np.abs(prob - h012_prob))),
    }


def generate_candidates(sample: pd.DataFrame, base: pd.DataFrame, h012: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for spec in candidate_specs():
        path, row = write_candidate(sample, base, h012, cells, spec)
        df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEYS).reset_index(drop=True)
        if not df[KEYS].equals(sample[KEYS]):
            raise ValueError(f"key mismatch: {path}")
        arr = df[TARGETS].to_numpy(dtype=np.float64)
        if not np.isfinite(arr).all() or arr.min() < 0.0 or arr.max() > 1.0:
            raise ValueError(f"invalid probabilities: {path}")
        rows.append(row)
    candidates = pd.DataFrame(rows).sort_values("posterior_delta_vs_e247").reset_index(drop=True)
    candidates["h014_decision"] = np.where(
        (candidates["kept_h012_posterior_gain_rate"] >= 0.60) & (candidates["changed_cells"] <= 900),
        "memory_regularized_big_bet",
        "diagnostic_only",
    )
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates


def df_to_markdown(df: pd.DataFrame) -> str:
    """Render a small markdown table without pandas' optional tabulate dependency."""
    if df.empty:
        return "_empty_"
    table = df.copy()
    for col in table.columns:
        if pd.api.types.is_float_dtype(table[col]):
            table[col] = table[col].map(lambda x: f"{x:.6f}" if pd.notna(x) else "")
        else:
            table[col] = table[col].map(lambda x: "" if pd.isna(x) else str(x))
    cols = [str(c) for c in table.columns]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in table.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in table.columns) + " |")
    return "\n".join(lines)


def write_report(
    cells: pd.DataFrame,
    target_summary: pd.DataFrame,
    bucket_summary: pd.DataFrame,
    candidates: pd.DataFrame,
) -> None:
    changed = cells[cells["h012_changed"]].copy()
    total_gain = float(changed["posterior_gain"].sum())
    agree_rate = float(changed["memory_agrees_h012"].mean())
    disagree_rate = float(changed["memory_disagrees_h012"].mean())
    agree_gain_share = float(changed.loc[changed["memory_agrees_h012"], "posterior_gain"].sum() / max(total_gain, 1.0e-12))
    high_rel_align = bucket_summary.loc[bucket_summary["bucket"].eq("high_align_and_rel")].iloc[0]
    best = candidates.iloc[0]
    lines = [
        "# H014 Sleep-State Memory Posterior Audit",
        "",
        "## Question",
        "",
        "Do H012's high-impact public-equation cells agree with same-subject sleep-state and sensor-quality memory?",
        "",
        "## Main Findings",
        "",
        f"- H012 changed cells audited: `{len(changed)}`.",
        f"- Memory agrees with H012 direction on `{agree_rate:.6f}` of changed cells.",
        f"- Memory disagrees on `{disagree_rate:.6f}` of changed cells.",
        f"- Memory-agree cells carry `{agree_gain_share:.6f}` of H012 posterior gain.",
        f"- High alignment + high reliability cells: `{int(high_rel_align['cells'])}` cells, `{float(high_rel_align['posterior_gain_share']):.6f}` posterior-gain share.",
        "",
        "## Target Summary",
        "",
        df_to_markdown(target_summary),
        "",
        "## Bucket Summary",
        "",
        df_to_markdown(bucket_summary),
        "",
        "## Candidate Summary",
        "",
        df_to_markdown(candidates),
        "",
        "## Interpretation",
        "",
        "- If memory-compatible cells keep most of H012's posterior gain, H012 is not only public-equation fitting; it overlaps with within-subject human-state continuity.",
        "- If memory-compatible cells are low-gain or target-skewed, H012 remains the best public file but should not be blindly amplified for private risk.",
        f"- Best generated H014 candidate is `{best['file']}` with kept posterior-gain rate `{float(best['kept_h012_posterior_gain_rate']):.6f}`.",
        "",
        "## Decision",
        "",
    ]
    if str(best["h014_decision"]) == "memory_regularized_big_bet":
        lines.append("- A memory-regularized H012 candidate exists as a high-information submission sensor.")
        lines.append("- Submit only if the next public question is whether subject-time continuity can reduce H012 private/public overfit risk.")
    else:
        lines.append("- No H014 candidate is promoted above H012.")
        lines.append("- Keep H012 as the current frontier and use memory compatibility as diagnostics/paper evidence.")
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    train, sample, base, h012, features = load_base_frames()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    h012_prob = h012[TARGETS].to_numpy(dtype=np.float64)
    row_memory, mem_full, mem_date, mem_state, _ = memory_for_test_rows(train, sample, features)
    q, cell_score, _ = posterior_matrix(sample, base_prob)
    cells = build_cell_table(sample, base_prob, h012_prob, q, cell_score, row_memory, mem_full, mem_date, mem_state)
    target_summary, bucket_summary = summarize(cells)
    candidates = generate_candidates(sample, base, h012, cells)
    write_report(cells, target_summary, bucket_summary, candidates)
    print(f"wrote {rel(REPORT_OUT)}")
    print(candidates.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
