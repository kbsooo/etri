#!/usr/bin/env python3
"""E53 calendar-flank block count-state probe.

Post-mixmin experiments moved the question from "which existing submission wins"
to "what hidden state did mixmin approximate?". This probe treats the natural
JEPA target as a hidden block count/rate vector. The context is only the labeled
calendar flanks around a pseudo-hidden block plus its block length/topology.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import lgamma, log
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402


TARGETS = hbr.TARGETS
KEY = hbr.KEY
EPS = 1e-5

MIXMIN = OUT / "submission_mixmin_0c916bb4.csv"
A2C8 = OUT / "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
RAW05 = JEPA / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"

SUMMARY_OUT = OUT / "calendar_flank_block_count_state_summary.csv"
TARGET_OUT = OUT / "calendar_flank_block_count_state_target_detail.csv"
BLOCK_OUT = OUT / "calendar_flank_block_count_state_block_detail.csv"
HIDDEN_OUT = OUT / "calendar_flank_block_count_state_hidden_alignment.csv"
HIDDEN_TARGET_OUT = OUT / "calendar_flank_block_count_state_hidden_target_alignment.csv"
REPORT_OUT = OUT / "calendar_flank_block_count_state_report.md"


@dataclass(frozen=True)
class ProbeFeatures:
    subject_id: str
    n: int
    len_bin: str
    has_left: bool
    has_right: bool
    context_type: str
    ctx: np.ndarray
    subject_mean: np.ndarray
    global_mean: np.ndarray
    prev: np.ndarray
    next: np.ndarray


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def binom_nll_per_row(k: int, n: int, p: float) -> float:
    p = float(np.clip(p, EPS, 1.0 - EPS))
    log_choose = lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    return float(-(log_choose + k * log(p) + (n - k) * log(1.0 - p)) / max(n, 1))


def row_logloss_for_block(labels: np.ndarray, pred_rate: np.ndarray) -> float:
    p = clip(pred_rate)
    loss = -(labels * np.log(p) + (1.0 - labels) * np.log(1.0 - p))
    return float(loss.mean())


def count_nll_for_block(counts: np.ndarray, n: int, pred_rate: np.ndarray) -> float:
    return float(np.mean([binom_nll_per_row(int(counts[j]), n, float(pred_rate[j])) for j in range(len(TARGETS))]))


def len_bin_exact(n: int) -> str:
    if n <= 2:
        return "1-2"
    if n <= 5:
        return "3-5"
    if n <= 10:
        return "6-10"
    return "11-16"


def block_context_type(rows: pd.DataFrame, positions: np.ndarray, known_mask: np.ndarray) -> tuple[str, bool, bool]:
    sid = str(rows.iloc[int(positions[0])]["subject_id"])
    subject_mask = rows["subject_id"].astype(str).eq(sid).to_numpy()
    known_subject = np.where(subject_mask & known_mask)[0]
    left = known_subject[known_subject < positions.min()]
    right = known_subject[known_subject > positions.max()]
    has_left = len(left) > 0
    has_right = len(right) > 0
    if has_left and has_right:
        return "between_train_runs", True, True
    if has_left:
        return "after_train_run", True, False
    if has_right:
        return "before_train_run", False, True
    return "isolated", False, False


def make_probe_features(
    rows: pd.DataFrame,
    y: np.ndarray,
    positions: np.ndarray,
    known_mask: np.ndarray,
) -> ProbeFeatures:
    ctx, info = hbr.context_info(rows, y, positions, known_mask)
    context_type, has_left, has_right = block_context_type(rows, positions, known_mask)
    return ProbeFeatures(
        subject_id=str(info["subject_id"]),
        n=int(len(positions)),
        len_bin=len_bin_exact(int(len(positions))),
        has_left=has_left,
        has_right=has_right,
        context_type=context_type,
        ctx=ctx.astype(np.float64),
        subject_mean=clip(np.asarray(info["subject_mean"], dtype=np.float64)),
        global_mean=clip(np.asarray(info["global_mean"], dtype=np.float64)),
        prev=np.asarray(info["prev"], dtype=np.float64),
        next=np.asarray(info["next"], dtype=np.float64),
    )


def finite_endpoint(value: float) -> int | None:
    if not np.isfinite(value):
        return None
    return int(value)


def donor_mask(blocks: list[hbr.Block], features: list[ProbeFeatures], i: int, mode: str) -> np.ndarray:
    target = blocks[i]
    target_set = set(int(p) for p in target.positions)
    keep = []
    for k, block in enumerate(blocks):
        if k == i:
            keep.append(False)
            continue
        if mode == "strict_subject" and features[k].subject_id == features[i].subject_id:
            keep.append(False)
            continue
        elif target_set.intersection(int(p) for p in block.positions):
            keep.append(False)
            continue
        else:
            keep.append(True)
    return np.asarray(keep, dtype=bool)


def relax_donors(
    i: int,
    j: int,
    blocks: list[hbr.Block],
    features: list[ProbeFeatures],
    base_donors: np.ndarray,
    min_donors: int = 5,
) -> tuple[np.ndarray, str]:
    target = features[i]
    prev = finite_endpoint(target.prev[j])
    nxt = finite_endpoint(target.next[j])
    stages: list[tuple[str, Any]] = [
        (
            "exact_len_both_edges",
            lambda f, b: b.n == target.n
            and finite_endpoint(f.prev[j]) == prev
            and finite_endpoint(f.next[j]) == nxt,
        ),
        (
            "lenbin_both_edges",
            lambda f, b: f.len_bin == target.len_bin
            and finite_endpoint(f.prev[j]) == prev
            and finite_endpoint(f.next[j]) == nxt,
        ),
        (
            "exact_len_left_edge",
            lambda f, b: b.n == target.n and prev is not None and finite_endpoint(f.prev[j]) == prev,
        ),
        (
            "exact_len_right_edge",
            lambda f, b: b.n == target.n and nxt is not None and finite_endpoint(f.next[j]) == nxt,
        ),
        ("exact_len", lambda f, b: b.n == target.n),
        ("lenbin", lambda f, b: f.len_bin == target.len_bin),
        ("all_donors", lambda f, b: True),
    ]
    for stage, predicate in stages:
        mask = base_donors.copy()
        for k, block in enumerate(blocks):
            if mask[k] and not predicate(features[k], block):
                mask[k] = False
        if int(mask.sum()) >= min_donors or stage == "all_donors":
            return mask, stage
    return base_donors, "all_donors"


def empirical_rate_predict(
    i: int,
    blocks: list[hbr.Block],
    features: list[ProbeFeatures],
    rates: np.ndarray,
    mode: str,
    alpha: float = 24.0,
) -> tuple[np.ndarray, dict[str, float | str]]:
    base = donor_mask(blocks, features, i, mode)
    pred = features[i].subject_mean.copy()
    supports = []
    stages = []
    for j in range(len(TARGETS)):
        mask, stage = relax_donors(i, j, blocks, features, base)
        idx = np.where(mask)[0]
        supports.append(float(len(idx)))
        stages.append(stage)
        if len(idx):
            local = float(np.mean(rates[idx, j]))
            pred[j] = (len(idx) * local + alpha * pred[j]) / (len(idx) + alpha)
    return clip(pred), {
        "support_min": float(np.min(supports)),
        "support_mean": float(np.mean(supports)),
        "dominant_stage": max(set(stages), key=stages.count),
    }


def edge_shrink_predict(feature: ProbeFeatures, weight: float) -> np.ndarray:
    out = feature.subject_mean.copy()
    for j in range(len(TARGETS)):
        vals = []
        if np.isfinite(feature.prev[j]):
            vals.append(float(feature.prev[j]))
        if np.isfinite(feature.next[j]):
            vals.append(float(feature.next[j]))
        if vals:
            out[j] = (1.0 - weight) * out[j] + weight * float(np.mean(vals))
    return clip(out)


def summarize_method(
    name: str,
    pred: np.ndarray,
    y: np.ndarray,
    blocks: list[hbr.Block],
    counts: np.ndarray,
    rates: np.ndarray,
) -> tuple[dict[str, float | str], list[dict[str, float | str]]]:
    weights = np.asarray([b.n for b in blocks], dtype=np.float64)
    row_losses = []
    count_losses = []
    for i, block in enumerate(blocks):
        labels = y[block.positions]
        row_losses.append(row_logloss_for_block(labels, pred[i]))
        count_losses.append(count_nll_for_block(counts[i], block.n, pred[i]))
    err = pred - rates
    subject_like = name == "subject_mean"
    row = {
        "method": name,
        "blocks": len(blocks),
        "weighted_row_logloss": float(np.average(row_losses, weights=weights)),
        "weighted_count_nll_per_row": float(np.average(count_losses, weights=weights)),
        "rate_mae_weighted": float(np.average(np.abs(err), weights=weights, axis=0).mean()),
        "count_mae_mean": float(np.mean(np.abs(err * weights[:, None]))),
        "is_subject_mean": float(subject_like),
    }
    target_rows = []
    for j, target in enumerate(TARGETS):
        target_row_loss = []
        target_count_nll = []
        for i, block in enumerate(blocks):
            labels = y[block.positions, j]
            p = float(pred[i, j])
            target_row_loss.append(float((-(labels * np.log(p) + (1.0 - labels) * np.log(1.0 - p))).mean()))
            target_count_nll.append(binom_nll_per_row(int(counts[i, j]), block.n, p))
        target_rows.append(
            {
                "method": name,
                "target": target,
                "target_row_logloss": float(np.average(target_row_loss, weights=weights)),
                "target_count_nll_per_row": float(np.average(target_count_nll, weights=weights)),
                "target_rate_mae": float(np.average(np.abs(err[:, j]), weights=weights)),
                "target_count_mae": float(np.mean(np.abs(err[:, j] * weights))),
            }
        )
    return row, target_rows


def make_predictions(
    blocks: list[hbr.Block],
    features: list[ProbeFeatures],
    rates: np.ndarray,
    mode: str,
) -> tuple[np.ndarray, pd.DataFrame]:
    pred = np.zeros((len(blocks), len(TARGETS)), dtype=np.float64)
    meta_rows = []
    for i in range(len(blocks)):
        p, meta = empirical_rate_predict(i, blocks, features, rates, mode)
        pred[i] = p
        meta_rows.append({"block_idx": i, "mode": mode, **meta})
    return pred, pd.DataFrame(meta_rows)


def predict_hidden(
    pseudo_blocks: list[hbr.Block],
    pseudo_features: list[ProbeFeatures],
    rates: np.ndarray,
    hidden_blocks: list[hbr.Block],
    hidden_features: list[ProbeFeatures],
    mode: str,
) -> tuple[np.ndarray, pd.DataFrame]:
    all_blocks = pseudo_blocks + hidden_blocks
    all_features = pseudo_features + hidden_features
    pred = np.zeros((len(hidden_blocks), len(TARGETS)), dtype=np.float64)
    meta_rows = []
    for h, _ in enumerate(hidden_blocks):
        i = len(pseudo_blocks) + h
        base = np.ones(len(all_blocks), dtype=bool)
        base[len(pseudo_blocks) :] = False
        if mode == "strict_subject":
            base[: len(pseudo_blocks)] &= np.asarray(
                [f.subject_id != hidden_features[h].subject_id for f in pseudo_features],
                dtype=bool,
            )
        out = hidden_features[h].subject_mean.copy()
        supports = []
        stages = []
        for j in range(len(TARGETS)):
            mask, stage = relax_donors(i, j, all_blocks, all_features, base)
            idx = np.where(mask[: len(pseudo_blocks)])[0]
            supports.append(float(len(idx)))
            stages.append(stage)
            if len(idx):
                local = float(np.mean(rates[idx, j]))
                out[j] = (len(idx) * local + 24.0 * out[j]) / (len(idx) + 24.0)
        pred[h] = clip(out)
        meta_rows.append(
            {
                "hidden_idx": h,
                "mode": mode,
                "support_min": float(np.min(supports)),
                "support_mean": float(np.mean(supports)),
                "dominant_stage": max(set(stages), key=stages.count),
            }
        )
    return pred, pd.DataFrame(meta_rows)


def read_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    return df


def expected_block_delta(
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    hidden_blocks: list[hbr.Block],
    hidden_rate: np.ndarray,
    candidate: pd.DataFrame,
    baseline: pd.DataFrame,
) -> np.ndarray:
    cand = candidate[TARGETS].to_numpy(dtype=np.float64)
    base = baseline[TARGETS].to_numpy(dtype=np.float64)
    out = np.zeros((len(hidden_blocks), len(TARGETS)), dtype=np.float64)
    if not candidate[KEY].equals(sample[KEY]) or not baseline[KEY].equals(sample[KEY]):
        raise ValueError("submission key mismatch")
    for i, block in enumerate(hidden_blocks):
        sub_idx = rows.iloc[block.positions]["sub_idx"].to_numpy(dtype=int)
        for j in range(len(TARGETS)):
            y = float(hidden_rate[i, j])
            cp = clip(cand[sub_idx, j])
            bp = clip(base[sub_idx, j])
            cand_ce = -(y * np.log(cp) + (1.0 - y) * np.log(1.0 - cp)).mean()
            base_ce = -(y * np.log(bp) + (1.0 - y) * np.log(1.0 - bp)).mean()
            out[i, j] = cand_ce - base_ce
    return out


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    y = hbr.train_label_matrix(rows, train)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    known = hbr.base_known_mask(rows)

    pseudo_features = []
    for block in pseudo_blocks:
        mask = known.copy()
        mask[block.positions] = False
        pseudo_features.append(make_probe_features(rows, y, block.positions, mask))
    hidden_features = [make_probe_features(rows, y, block.positions, known) for block in hidden_blocks]

    rates = hbr.true_rates(y, pseudo_blocks)
    counts = np.vstack([np.nansum(y[b.positions], axis=0) for b in pseudo_blocks]).astype(np.float64)

    pred_subject = np.vstack([f.subject_mean for f in pseudo_features])
    pred_edge025 = np.vstack([edge_shrink_predict(f, 0.25) for f in pseudo_features])
    pred_edge050 = np.vstack([edge_shrink_predict(f, 0.50) for f in pseudo_features])
    pred_strict, meta_strict = make_predictions(pseudo_blocks, pseudo_features, rates, "strict_subject")
    pred_local, meta_local = make_predictions(pseudo_blocks, pseudo_features, rates, "local_nonoverlap")

    methods = {
        "subject_mean": pred_subject,
        "edge_shrink025": pred_edge025,
        "edge_shrink050": pred_edge050,
        "calendar_count_strict": pred_strict,
        "calendar_count_local": pred_local,
    }

    summary_rows = []
    target_rows = []
    for name, pred in methods.items():
        row, detail = summarize_method(name, pred, y, pseudo_blocks, counts, rates)
        summary_rows.append(row)
        target_rows.extend(detail)
    summary = pd.DataFrame(summary_rows)
    subj_loss = float(summary.loc[summary["method"].eq("subject_mean"), "weighted_row_logloss"].iloc[0])
    subj_count = float(summary.loc[summary["method"].eq("subject_mean"), "weighted_count_nll_per_row"].iloc[0])
    for col, base in [
        ("weighted_row_logloss", subj_loss),
        ("weighted_count_nll_per_row", subj_count),
    ]:
        summary[f"delta_{col}_vs_subject"] = summary[col] - base
    summary = summary.sort_values(["weighted_row_logloss", "weighted_count_nll_per_row"]).reset_index(drop=True)

    target_detail = pd.DataFrame(target_rows)
    target_base = target_detail[target_detail["method"].eq("subject_mean")].set_index("target")
    target_detail["delta_row_vs_subject"] = target_detail.apply(
        lambda r: r["target_row_logloss"] - float(target_base.loc[r["target"], "target_row_logloss"]),
        axis=1,
    )
    target_detail["delta_count_vs_subject"] = target_detail.apply(
        lambda r: r["target_count_nll_per_row"] - float(target_base.loc[r["target"], "target_count_nll_per_row"]),
        axis=1,
    )
    target_detail = target_detail.sort_values(["target", "target_row_logloss"]).reset_index(drop=True)

    block_rows = []
    meta_join = {
        ("calendar_count_strict", int(r.block_idx)): r
        for r in meta_strict.itertuples(index=False)
    }
    meta_join.update(
        {
            ("calendar_count_local", int(r.block_idx)): r
            for r in meta_local.itertuples(index=False)
        }
    )
    for i, block in enumerate(pseudo_blocks):
        base_rec = {
            "block_idx": i,
            "block_id": block.block_id,
            "subject_id": pseudo_features[i].subject_id,
            "n_rows": block.n,
            "len_bin": pseudo_features[i].len_bin,
            "context_type": pseudo_features[i].context_type,
            "start": block.start.date().isoformat(),
            "end": block.end.date().isoformat(),
        }
        for method, pred in methods.items():
            meta = meta_join.get((method, i))
            block_rows.append(
                {
                    **base_rec,
                    "method": method,
                    "row_logloss": row_logloss_for_block(y[block.positions], pred[i]),
                    "count_nll_per_row": count_nll_for_block(counts[i], block.n, pred[i]),
                    "rate_mae": float(np.abs(pred[i] - rates[i]).mean()),
                    "count_mae": float(np.abs((pred[i] - rates[i]) * block.n).mean()),
                    "support_min": float(getattr(meta, "support_min", np.nan)) if meta is not None else np.nan,
                    "support_mean": float(getattr(meta, "support_mean", np.nan)) if meta is not None else np.nan,
                    "dominant_stage": str(getattr(meta, "dominant_stage", "")) if meta is not None else "",
                }
            )
    block_detail = pd.DataFrame(block_rows)

    mixmin = read_submission(MIXMIN)
    a2c8 = read_submission(A2C8)
    raw05 = read_submission(RAW05)
    hidden_strict, hidden_meta_strict = predict_hidden(
        pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, "strict_subject"
    )
    hidden_local, hidden_meta_local = predict_hidden(
        pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, "local_nonoverlap"
    )

    hidden_rows = []
    for mode, hidden_rate, meta in [
        ("strict_subject", hidden_strict, hidden_meta_strict),
        ("local_nonoverlap", hidden_local, hidden_meta_local),
    ]:
        d_mix_a2c8 = expected_block_delta(sample, rows, hidden_blocks, hidden_rate, mixmin, a2c8)
        d_raw_a2c8 = expected_block_delta(sample, rows, hidden_blocks, hidden_rate, raw05, a2c8)
        d_mix_raw = expected_block_delta(sample, rows, hidden_blocks, hidden_rate, mixmin, raw05)
        for i, block in enumerate(hidden_blocks):
            rec = {
                "mode": mode,
                "hidden_block_id": block.block_id,
                "subject_id": block.subject_id,
                "n_rows": block.n,
                "len_bin": len_bin_exact(block.n),
                "context_type": hidden_features[i].context_type,
                "start": block.start.date().isoformat(),
                "end": block.end.date().isoformat(),
                "expected_mixmin_delta_vs_a2c8": float(d_mix_a2c8[i].mean()),
                "expected_raw05_delta_vs_a2c8": float(d_raw_a2c8[i].mean()),
                "expected_mixmin_delta_vs_raw05": float(d_mix_raw[i].mean()),
                "support_min": float(meta.loc[i, "support_min"]),
                "support_mean": float(meta.loc[i, "support_mean"]),
                "dominant_stage": str(meta.loc[i, "dominant_stage"]),
            }
            for j, target in enumerate(TARGETS):
                rec[f"rate_{target}"] = float(hidden_rate[i, j])
                rec[f"mixmin_delta_vs_a2c8_{target}"] = float(d_mix_a2c8[i, j])
            hidden_rows.append(rec)
    hidden_alignment = pd.DataFrame(hidden_rows)

    SUMMARY_OUT.write_text(summary.to_csv(index=False), encoding="utf-8")
    TARGET_OUT.write_text(target_detail.to_csv(index=False), encoding="utf-8")
    BLOCK_OUT.write_text(block_detail.to_csv(index=False), encoding="utf-8")
    HIDDEN_OUT.write_text(hidden_alignment.to_csv(index=False), encoding="utf-8")

    best = summary.iloc[0]
    best_non_base = summary[~summary["method"].eq("subject_mean")].iloc[0]
    hidden_by_mode = (
        hidden_alignment.groupby("mode")
        .agg(
            hidden_blocks=("hidden_block_id", "size"),
            mean_mixmin_delta_vs_a2c8=("expected_mixmin_delta_vs_a2c8", "mean"),
            weighted_mixmin_delta_vs_a2c8=("expected_mixmin_delta_vs_a2c8", lambda x: np.average(x, weights=hidden_alignment.loc[x.index, "n_rows"])),
            mean_raw05_delta_vs_a2c8=("expected_raw05_delta_vs_a2c8", "mean"),
            mixmin_better_block_rate=("expected_mixmin_delta_vs_a2c8", lambda x: float(np.mean(x < 0))),
            median_support_min=("support_min", "median"),
        )
        .reset_index()
        .sort_values("weighted_mixmin_delta_vs_a2c8")
    )
    hidden_target_rows = []
    for mode, g in hidden_alignment.groupby("mode", sort=False):
        for target in TARGETS:
            col = f"mixmin_delta_vs_a2c8_{target}"
            hidden_target_rows.append(
                {
                    "mode": mode,
                    "target": target,
                    "mean_mixmin_delta_vs_a2c8": float(g[col].mean()),
                    "weighted_mixmin_delta_vs_a2c8": float(np.average(g[col], weights=g["n_rows"])),
                    "mixmin_better_block_rate": float(np.mean(g[col] < 0)),
                    "mean_predicted_rate": float(g[f"rate_{target}"].mean()),
                }
            )
    hidden_target_alignment = pd.DataFrame(hidden_target_rows).sort_values(
        ["mode", "weighted_mixmin_delta_vs_a2c8"]
    )
    HIDDEN_TARGET_OUT.write_text(hidden_target_alignment.to_csv(index=False), encoding="utf-8")
    strict_targets = target_detail[target_detail["method"].eq("calendar_count_strict")].copy()
    strict_target_good = int((strict_targets["delta_row_vs_subject"] < 0).sum())
    local_targets = target_detail[target_detail["method"].eq("calendar_count_local")].copy()
    local_target_good = int((local_targets["delta_row_vs_subject"] < 0).sum())

    report = [
        "# E53 Calendar-Flank Block Count-State Probe",
        "",
        "## Observe",
        "",
        "E48 made `submission_mixmin_0c916bb4.csv` the public frontier. E50-E52 then falsified three selector translations: calendar kNN, anchor-calendar kNN, and existing-candidate binary-world replacement.",
        "",
        "## Wonder",
        "",
        "Does the subject-calendar flank context actually predict a hidden block count/rate state, and does that predicted state prefer mixmin over a2c8 on the real hidden blocks?",
        "",
        "## Hypothesis",
        "",
        "H53: mixmin approximates a hidden block count-state. If true, a fold-safe calendar-flank posterior should beat subject mean on pseudo-hidden blocks and its real hidden-block rates should give negative expected LogLoss delta for mixmin versus a2c8.",
        "",
        "## Method",
        "",
        f"- Pseudo-hidden blocks: `{len(pseudo_blocks)}`, generated from train rows with actual submission block lengths.",
        f"- Real hidden submission blocks: `{len(hidden_blocks)}`.",
        "- Context: subject mean, global mean, previous/next labeled flank values, block length bin, and donor block count/rate signatures.",
        "- Predictors: subject mean, two edge-shrink baselines, strict-subject calendar count posterior, and local non-overlap calendar count posterior.",
        "- Stress: strict-subject excludes same subject donors; local non-overlap allows same subject but excludes overlapping pseudo blocks.",
        "",
        "## Pseudo-Hidden Block Results",
        "",
        markdown_table(
            summary,
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_subject",
                "weighted_count_nll_per_row",
                "delta_weighted_count_nll_per_row_vs_subject",
                "rate_mae_weighted",
                "count_mae_mean",
            ],
        ),
        "",
        "## Target Detail",
        "",
        markdown_table(
            target_detail[target_detail["method"].isin(["subject_mean", "calendar_count_strict", "calendar_count_local"])],
            [
                "method",
                "target",
                "target_row_logloss",
                "delta_row_vs_subject",
                "target_count_nll_per_row",
                "delta_count_vs_subject",
                "target_count_mae",
            ],
            max_rows=24,
        ),
        "",
        "## Hidden-Block Mixmin Alignment",
        "",
        markdown_table(
            hidden_by_mode,
            [
                "mode",
                "hidden_blocks",
                "weighted_mixmin_delta_vs_a2c8",
                "mean_mixmin_delta_vs_a2c8",
                "mean_raw05_delta_vs_a2c8",
                "mixmin_better_block_rate",
                "median_support_min",
            ],
        ),
        "",
        "## Hidden-Block Target Alignment",
        "",
        markdown_table(
            hidden_target_alignment,
            [
                "mode",
                "target",
                "weighted_mixmin_delta_vs_a2c8",
                "mean_mixmin_delta_vs_a2c8",
                "mixmin_better_block_rate",
                "mean_predicted_rate",
            ],
            max_rows=20,
        ),
        "",
        "## Decision",
        "",
    ]
    strict_row_delta = float(
        summary.loc[summary["method"].eq("calendar_count_strict"), "delta_weighted_row_logloss_vs_subject"].iloc[0]
    )
    local_row_delta = float(
        summary.loc[summary["method"].eq("calendar_count_local"), "delta_weighted_row_logloss_vs_subject"].iloc[0]
    )
    strict_mix_delta = float(
        hidden_by_mode.loc[hidden_by_mode["mode"].eq("strict_subject"), "weighted_mixmin_delta_vs_a2c8"].iloc[0]
    )
    local_mix_delta = float(
        hidden_by_mode.loc[hidden_by_mode["mode"].eq("local_nonoverlap"), "weighted_mixmin_delta_vs_a2c8"].iloc[0]
    )
    if strict_row_delta < -0.002 and strict_mix_delta < -0.0002:
        report.extend(
            [
                "The strict calendar-flank count posterior passes the first useful gate: it improves pseudo-hidden block prediction and independently prefers mixmin over a2c8 on actual hidden blocks.",
                "",
                "This is not yet a submission; it should next be converted into a low-amplitude mixmin-relative block gate and tested against E52 binary worlds.",
            ]
        )
    elif local_row_delta < -0.002 and strict_row_delta >= -0.002:
        report.extend(
            [
                "The only meaningful pseudo-hidden improvement is local/same-subject. That is a weak representation signal but not a private-safe mixmin explanation.",
                "",
                f"Strict-subject target count recovery improved `{strict_target_good}` targets, while local recovery improved `{local_target_good}` targets. This keeps calendar-flank state as an energy feature, not a candidate generator.",
            ]
        )
    else:
        report.extend(
            [
                "Calendar-flank count-state is not recovered strongly enough by this posterior family.",
                "",
                f"Strict-subject row delta vs subject mean is `{strict_row_delta:+.6f}` and local delta is `{local_row_delta:+.6f}`. The strict predicted hidden state gives mixmin expected delta `{strict_mix_delta:+.6f}` versus a2c8; local gives `{local_mix_delta:+.6f}`.",
                "",
                "This weakens the simple calendar-flank target hypothesis. The live branch shifts toward richer raw overnight context, target-dependency count manifolds, or hard mixmin-constrained world generation.",
            ]
        )
    report.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TARGET_OUT.relative_to(ROOT)}`",
            f"- `{BLOCK_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_TARGET_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(
        "pseudo_blocks=",
        len(pseudo_blocks),
        "hidden_blocks=",
        len(hidden_blocks),
        "best=",
        best["method"],
        f"{float(best['weighted_row_logloss']):.6f}",
        "best_non_base=",
        best_non_base["method"],
        f"{float(best_non_base['delta_weighted_row_logloss_vs_subject']):+.6f}",
        "strict_mix_delta=",
        f"{strict_mix_delta:+.6f}",
        "local_mix_delta=",
        f"{local_mix_delta:+.6f}",
    )
    print(summary.round(6).to_string(index=False))
    print(hidden_by_mode.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
