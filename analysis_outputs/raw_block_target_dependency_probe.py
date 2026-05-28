#!/usr/bin/env python3
"""E55 raw block target-dependency probe.

E54 proved that raw overnight context can recover a strict pseudo-hidden
block-state latent, but that latent regressed S3 and did not explain mixmin's
actual hidden-block edge. This probe asks whether a target-dependency/count
manifold can repair that split without using same-subject donors.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import calendar_flank_block_count_state_probe as e53  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import raw_overnight_block_context_probe as e54  # noqa: E402


TARGETS = hbr.TARGETS
EPS = 1e-5

SUMMARY_OUT = OUT / "raw_block_target_dependency_probe_summary.csv"
TARGET_OUT = OUT / "raw_block_target_dependency_probe_target_detail.csv"
HIDDEN_OUT = OUT / "raw_block_target_dependency_probe_hidden_alignment.csv"
HIDDEN_TARGET_OUT = OUT / "raw_block_target_dependency_probe_hidden_target_alignment.csv"
METHOD_OUT = OUT / "raw_block_target_dependency_probe_method_detail.csv"
REPORT_OUT = OUT / "raw_block_target_dependency_probe_report.md"


@dataclass(frozen=True)
class BaseState:
    train: pd.DataFrame
    sample: pd.DataFrame
    rows: pd.DataFrame
    y: np.ndarray
    pseudo_blocks: list[hbr.Block]
    hidden_blocks: list[hbr.Block]
    rates: np.ndarray
    counts: np.ndarray
    pseudo_features: list[e53.ProbeFeatures]
    hidden_features: list[e53.ProbeFeatures]
    pseudo_subject: np.ndarray
    hidden_subject: np.ndarray
    pseudo_calendar: np.ndarray
    hidden_calendar: np.ndarray
    pseudo_raw: np.ndarray
    hidden_raw: np.ndarray
    raw_meta: pd.DataFrame
    hidden_raw_meta: pd.DataFrame


PAIR_CONTEXT = {
    "Q1": ["S1", "Q2", "Q3"],
    "Q2": ["Q3", "Q1"],
    "Q3": ["Q2", "Q1"],
    "S1": ["Q1", "S2", "S4"],
    "S2": ["S4", "S3", "S1"],
    "S3": ["S2", "S1"],
    "S4": ["S2", "S1", "S3"],
}

MASKS = {
    "s3": ["S3"],
    "s2s3": ["S2", "S3"],
    "stage": ["S1", "S2", "S3", "S4"],
    "all": TARGETS,
}


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray | float) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(z, dtype=np.float64)))


def context_columns(target: str, mode: str) -> list[int]:
    if mode == "pair":
        names = PAIR_CONTEXT[target]
    elif mode == "allcross":
        names = [t for t in TARGETS if t != target]
    elif mode == "groupcross":
        group = ["S1", "S2", "S3", "S4"] if target.startswith("S") else ["Q1", "Q2", "Q3"]
        names = [t for t in group if t != target]
    else:
        raise ValueError(mode)
    if not names:
        names = [t for t in TARGETS if t != target]
    return [TARGETS.index(t) for t in names]


def donor_mask_for_pseudo(blocks: list[hbr.Block], i: int) -> np.ndarray:
    return e54.donor_mask(blocks, i, "strict_subject")


def donor_mask_for_hidden(pseudo_blocks: list[hbr.Block], hidden_block: hbr.Block) -> np.ndarray:
    return np.asarray([b.subject_id != hidden_block.subject_id for b in pseudo_blocks], dtype=bool)


def weighted_knn_rate(
    donor_context: np.ndarray,
    donor_target: np.ndarray,
    query_context: np.ndarray,
    fallback: float,
    k: int,
    alpha: float,
) -> tuple[float, float, float]:
    if len(donor_context) == 0:
        return float(clip(fallback)), 0.0, np.nan
    scaler = StandardScaler()
    x = scaler.fit_transform(logit(donor_context))
    q = scaler.transform(logit(query_context).reshape(1, -1))[0]
    dist = np.sqrt(np.maximum(((x - q) ** 2).mean(axis=1), 0.0))
    order = np.argsort(dist)[: min(k, len(dist))]
    chosen_dist = dist[order]
    weights = 1.0 / np.maximum(chosen_dist, 1e-3)
    weights /= weights.sum()
    local = float(weights @ donor_target[order])
    eff = float(len(order))
    pred = (eff * local + alpha * float(fallback)) / (eff + alpha)
    return float(clip(pred)), eff, float(np.median(chosen_dist))


def ridge_rate(
    donor_context: np.ndarray,
    donor_target: np.ndarray,
    query_context: np.ndarray,
    fallback: float,
    alpha: float,
) -> tuple[float, float, float]:
    if len(donor_context) < 12 or np.nanstd(donor_target) < 1e-6:
        return float(clip(fallback)), float(len(donor_context)), np.nan
    scaler = StandardScaler()
    x = scaler.fit_transform(logit(donor_context))
    q = scaler.transform(logit(query_context).reshape(1, -1))
    model = Ridge(alpha=alpha)
    model.fit(x, logit(donor_target))
    pred = float(sigmoid(model.predict(q)[0]))
    return float(clip(pred)), float(len(donor_context)), np.nan


def project_one(
    base_row: np.ndarray,
    fallback_row: np.ndarray,
    donor_rates: np.ndarray,
    donor_mask: np.ndarray,
    target: str,
    mode: str,
    estimator: str,
    k: int,
    alpha: float,
) -> tuple[float, float, float]:
    j = TARGETS.index(target)
    cols = context_columns(target, mode)
    idx = np.where(donor_mask)[0]
    if len(idx) == 0:
        return float(base_row[j]), 0.0, np.nan
    donor_context = clip(donor_rates[idx][:, cols])
    donor_target = clip(donor_rates[idx, j])
    query_context = clip(base_row[cols])
    fallback = float(fallback_row[j])
    if estimator == "knn":
        return weighted_knn_rate(donor_context, donor_target, query_context, fallback, k, alpha)
    if estimator == "ridge":
        return ridge_rate(donor_context, donor_target, query_context, fallback, alpha)
    raise ValueError(estimator)


def apply_dependency_projection_pseudo(
    base: np.ndarray,
    fallback: np.ndarray,
    blocks: list[hbr.Block],
    rates: np.ndarray,
    mode: str,
    estimator: str,
    k: int,
    alpha: float,
    strength: float,
    mask_targets: list[str],
) -> tuple[np.ndarray, pd.DataFrame]:
    out = base.copy()
    meta = []
    active = set(mask_targets)
    for i in range(len(blocks)):
        donors = donor_mask_for_pseudo(blocks, i)
        for target in active:
            j = TARGETS.index(target)
            q, support, dist = project_one(base[i], fallback[i], rates, donors, target, mode, estimator, k, alpha)
            out[i, j] = (1.0 - strength) * base[i, j] + strength * q
            meta.append(
                {
                    "block_idx": i,
                    "target": target,
                    "support": support,
                    "dist_median": dist,
                    "projected_rate": q,
                    "base_rate": float(base[i, j]),
                    "final_rate": float(out[i, j]),
                }
            )
    return clip(out), pd.DataFrame(meta)


def apply_dependency_projection_hidden(
    base_hidden: np.ndarray,
    fallback_hidden: np.ndarray,
    pseudo_rates: np.ndarray,
    pseudo_blocks: list[hbr.Block],
    hidden_blocks: list[hbr.Block],
    mode: str,
    estimator: str,
    k: int,
    alpha: float,
    strength: float,
    mask_targets: list[str],
) -> tuple[np.ndarray, pd.DataFrame]:
    out = base_hidden.copy()
    meta = []
    active = set(mask_targets)
    for i, block in enumerate(hidden_blocks):
        donors = donor_mask_for_hidden(pseudo_blocks, block)
        for target in active:
            j = TARGETS.index(target)
            q, support, dist = project_one(
                base_hidden[i], fallback_hidden[i], pseudo_rates, donors, target, mode, estimator, k, alpha
            )
            out[i, j] = (1.0 - strength) * base_hidden[i, j] + strength * q
            meta.append(
                {
                    "hidden_idx": i,
                    "target": target,
                    "support": support,
                    "dist_median": dist,
                    "projected_rate": q,
                    "base_rate": float(base_hidden[i, j]),
                    "final_rate": float(out[i, j]),
                }
            )
    return clip(out), pd.DataFrame(meta)


def build_base_state() -> BaseState:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    y = hbr.train_label_matrix(rows, train)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    known = hbr.base_known_mask(rows)
    rates = hbr.true_rates(y, pseudo_blocks)
    counts = np.vstack([np.nansum(y[b.positions], axis=0) for b in pseudo_blocks]).astype(np.float64)

    pseudo_features = []
    for block in pseudo_blocks:
        mask = known.copy()
        mask[block.positions] = False
        pseudo_features.append(e53.make_probe_features(rows, y, block.positions, mask))
    hidden_features = [e53.make_probe_features(rows, y, block.positions, known) for block in hidden_blocks]
    pseudo_ctx = np.vstack([f.ctx for f in pseudo_features])
    hidden_ctx = np.vstack([f.ctx for f in hidden_features])

    overnight = e54.load_overnight_rows(rows)
    pack = e54.make_view_pack("night_phone", rows, overnight, pseudo_blocks, hidden_blocks)
    spec = e54.MethodSpec(
        "night_phone_rawctx_strict_k8_a24",
        "night_phone",
        "strict_subject",
        True,
        8,
        24.0,
        np.concatenate([pack.pseudo_raw, pseudo_ctx], axis=1),
        np.concatenate([pack.hidden_raw, hidden_ctx], axis=1),
    )
    pseudo_raw, raw_meta = e54.make_method_predictions(spec, pseudo_blocks, pseudo_features, rates)
    hidden_raw, hidden_raw_meta = e54.hidden_method_prediction(
        spec, pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features
    )
    pseudo_calendar, _ = e53.make_predictions(pseudo_blocks, pseudo_features, rates, "strict_subject")
    hidden_calendar, _ = e53.predict_hidden(
        pseudo_blocks, pseudo_features, rates, hidden_blocks, hidden_features, "strict_subject"
    )
    pseudo_subject = np.vstack([f.subject_mean for f in pseudo_features])
    hidden_subject = np.vstack([f.subject_mean for f in hidden_features])
    return BaseState(
        train=train,
        sample=sample,
        rows=rows,
        y=y,
        pseudo_blocks=pseudo_blocks,
        hidden_blocks=hidden_blocks,
        rates=rates,
        counts=counts,
        pseudo_features=pseudo_features,
        hidden_features=hidden_features,
        pseudo_subject=pseudo_subject,
        hidden_subject=hidden_subject,
        pseudo_calendar=pseudo_calendar,
        hidden_calendar=hidden_calendar,
        pseudo_raw=pseudo_raw,
        hidden_raw=hidden_raw,
        raw_meta=raw_meta,
        hidden_raw_meta=hidden_raw_meta,
    )


def simple_replacements(state: BaseState) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    out: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    j = TARGETS.index("S3")
    for name, source_pseudo, source_hidden, weight in [
        ("s3_subject_w1p00", state.pseudo_subject, state.hidden_subject, 1.0),
        ("s3_calendar_w1p00", state.pseudo_calendar, state.hidden_calendar, 1.0),
        ("s3_subject_w0p50", state.pseudo_subject, state.hidden_subject, 0.5),
        ("s3_calendar_w0p50", state.pseudo_calendar, state.hidden_calendar, 0.5),
    ]:
        p = state.pseudo_raw.copy()
        h = state.hidden_raw.copy()
        p[:, j] = (1.0 - weight) * p[:, j] + weight * source_pseudo[:, j]
        h[:, j] = (1.0 - weight) * h[:, j] + weight * source_hidden[:, j]
        out[f"raw_phone_{name}"] = (clip(p), clip(h))
    for targets, label in [(["S2", "S3"], "s2s3_calendar_w0p50"), (["S1", "S2", "S3", "S4"], "stage_calendar_w0p50")]:
        p = state.pseudo_raw.copy()
        h = state.hidden_raw.copy()
        idx = [TARGETS.index(t) for t in targets]
        p[:, idx] = 0.5 * p[:, idx] + 0.5 * state.pseudo_calendar[:, idx]
        h[:, idx] = 0.5 * h[:, idx] + 0.5 * state.hidden_calendar[:, idx]
        out[f"raw_phone_{label}"] = (clip(p), clip(h))
    return out


def manifold_energy_model(rates: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mu = rates.mean(axis=0)
    cov = np.asarray(np.cov(rates, rowvar=False), dtype=np.float64)
    diag = np.diag(np.diag(cov))
    shrink = 0.45 * diag + 0.55 * cov
    shrink += np.eye(len(TARGETS)) * 0.02
    return mu, np.linalg.pinv(shrink)


def manifold_energy(pred: np.ndarray, mu: np.ndarray, inv: np.ndarray) -> np.ndarray:
    x = pred - mu[None, :]
    return np.sum((x @ inv) * x, axis=1)


def summarize_methods(
    state: BaseState,
    methods: dict[str, tuple[np.ndarray, np.ndarray]],
    method_meta: dict[str, dict[str, object]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    target_rows = []
    hidden_rows = []
    hidden_target_rows = []
    mu, inv = manifold_energy_model(state.rates)
    base_energy = manifold_energy(state.pseudo_raw, mu, inv)
    weights = np.asarray([b.n for b in state.pseudo_blocks], dtype=np.float64)
    for method, (pseudo_pred, hidden_pred) in methods.items():
        row, detail = e53.summarize_method(method, pseudo_pred, state.y, state.pseudo_blocks, state.counts, state.rates)
        energy = manifold_energy(pseudo_pred, mu, inv)
        row["mean_manifold_energy"] = float(np.mean(energy))
        row["weighted_manifold_energy"] = float(np.average(energy, weights=weights))
        row["energy_delta_vs_raw"] = float(np.mean(energy - base_energy))
        row.update(method_meta.get(method, {}))
        summary_rows.append(row)
        target_rows.extend(detail)
        block_rows, target_alignment = e54.hidden_alignment(
            method, state.sample, state.rows, state.hidden_blocks, hidden_pred, pd.DataFrame()
        )
        hidden_rows.extend(block_rows)
        hidden_target_rows.extend(target_alignment)
    summary = pd.DataFrame(summary_rows)
    target = pd.DataFrame(target_rows)
    hidden = pd.DataFrame(hidden_rows)
    hidden_by_method = (
        hidden.groupby("method")
        .apply(
            lambda g: pd.Series(
                {
                    "hidden_blocks": len(g),
                    "weighted_mixmin_delta_vs_a2c8": float(np.average(g["expected_mixmin_delta_vs_a2c8"], weights=g["n_rows"])),
                    "mean_mixmin_delta_vs_a2c8": float(g["expected_mixmin_delta_vs_a2c8"].mean()),
                    "mean_raw05_delta_vs_a2c8": float(g["expected_raw05_delta_vs_a2c8"].mean()),
                    "mixmin_better_block_rate": float((g["expected_mixmin_delta_vs_a2c8"] < 0).mean()),
                }
            )
        )
        .reset_index()
    )
    hidden_target = pd.DataFrame(hidden_target_rows)
    subject_loss = float(summary.loc[summary["method"].eq("subject_mean"), "weighted_row_logloss"].iloc[0])
    raw_loss = float(summary.loc[summary["method"].eq("raw_phone_base"), "weighted_row_logloss"].iloc[0])
    summary["delta_weighted_row_logloss_vs_subject"] = summary["weighted_row_logloss"] - subject_loss
    summary["delta_weighted_row_logloss_vs_raw"] = summary["weighted_row_logloss"] - raw_loss
    summary = summary.merge(hidden_by_method, on="method", how="left")
    target_base = target[target["method"].eq("subject_mean")].set_index("target")
    target_raw = target[target["method"].eq("raw_phone_base")].set_index("target")
    target["delta_row_vs_subject"] = target.apply(
        lambda r: r["target_row_logloss"] - float(target_base.loc[r["target"], "target_row_logloss"]),
        axis=1,
    )
    target["delta_row_vs_raw"] = target.apply(
        lambda r: r["target_row_logloss"] - float(target_raw.loc[r["target"], "target_row_logloss"]),
        axis=1,
    )
    s3 = target[target["target"].eq("S3")][["method", "delta_row_vs_subject", "delta_row_vs_raw"]].rename(
        columns={"delta_row_vs_subject": "s3_delta_vs_subject", "delta_row_vs_raw": "s3_delta_vs_raw"}
    )
    summary = summary.merge(s3, on="method", how="left")
    summary["fixes_s3_vs_subject"] = summary["s3_delta_vs_subject"].le(0)
    summary["improves_vs_raw"] = summary["delta_weighted_row_logloss_vs_raw"].le(0)
    summary["hidden_mixmin_negative"] = summary["weighted_mixmin_delta_vs_a2c8"].lt(0)
    summary["joint_gate"] = summary["fixes_s3_vs_subject"] & summary["improves_vs_raw"] & summary["hidden_mixmin_negative"]
    return (
        summary.sort_values(["joint_gate", "weighted_row_logloss"], ascending=[False, True]).reset_index(drop=True),
        target.sort_values(["target", "target_row_logloss"]).reset_index(drop=True),
        hidden_by_method.sort_values(["weighted_mixmin_delta_vs_a2c8", "mean_mixmin_delta_vs_a2c8"]).reset_index(drop=True),
        hidden_target.sort_values(["target", "weighted_mixmin_delta_vs_a2c8"]).reset_index(drop=True),
        hidden,
    )


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
    state = build_base_state()
    methods: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "subject_mean": (state.pseudo_subject, state.hidden_subject),
        "calendar_count_strict": (state.pseudo_calendar, state.hidden_calendar),
        "raw_phone_base": (state.pseudo_raw, state.hidden_raw),
    }
    method_meta: dict[str, dict[str, object]] = {
        "subject_mean": {"family": "baseline", "mask": "", "mode": "", "estimator": "", "strength": 0.0},
        "calendar_count_strict": {"family": "baseline", "mask": "", "mode": "", "estimator": "", "strength": 0.0},
        "raw_phone_base": {"family": "raw", "mask": "", "mode": "", "estimator": "", "strength": 0.0},
    }
    for name, pair in simple_replacements(state).items():
        methods[name] = pair
        method_meta[name] = {"family": "replacement", "mask": name.replace("raw_phone_", ""), "mode": "", "estimator": "", "strength": np.nan}

    method_detail_rows = []
    for mode in ["pair", "groupcross", "allcross"]:
        for estimator in ["knn", "ridge"]:
            for k in ([8, 16] if estimator == "knn" else [0]):
                for alpha in ([8.0, 24.0] if estimator == "knn" else [2.0, 8.0]):
                    for strength in [0.25, 0.50, 0.75]:
                        for mask_name, targets in MASKS.items():
                            method = f"raw_phone_td_{estimator}_{mode}_{mask_name}_k{k}_a{alpha:g}_w{strength:.2f}"
                            pseudo, meta_p = apply_dependency_projection_pseudo(
                                state.pseudo_raw,
                                state.pseudo_subject,
                                state.pseudo_blocks,
                                state.rates,
                                mode,
                                estimator,
                                k,
                                alpha,
                                strength,
                                targets,
                            )
                            hidden, meta_h = apply_dependency_projection_hidden(
                                state.hidden_raw,
                                state.hidden_subject,
                                state.rates,
                                state.pseudo_blocks,
                                state.hidden_blocks,
                                mode,
                                estimator,
                                k,
                                alpha,
                                strength,
                                targets,
                            )
                            methods[method] = (pseudo, hidden)
                            method_meta[method] = {
                                "family": "target_dependency",
                                "mask": mask_name,
                                "mode": mode,
                                "estimator": estimator,
                                "k": float(k),
                                "alpha": float(alpha),
                                "strength": float(strength),
                                "pseudo_support_mean": float(meta_p["support"].mean()) if len(meta_p) else np.nan,
                                "hidden_support_mean": float(meta_h["support"].mean()) if len(meta_h) else np.nan,
                                "pseudo_dist_median": float(meta_p["dist_median"].median()) if "dist_median" in meta_p else np.nan,
                            }
                            method_detail_rows.append(
                                {
                                    "method": method,
                                    "mode": mode,
                                    "estimator": estimator,
                                    "k": k,
                                    "alpha": alpha,
                                    "strength": strength,
                                    "mask": mask_name,
                                    "pseudo_adjusted_cells": len(meta_p),
                                    "hidden_adjusted_cells": len(meta_h),
                                }
                            )

    summary, target, hidden_by_method, hidden_target, hidden_blocks = summarize_methods(state, methods, method_meta)
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    hidden_by_method.to_csv(HIDDEN_OUT, index=False)
    hidden_target.to_csv(HIDDEN_TARGET_OUT, index=False)
    pd.DataFrame(method_detail_rows).to_csv(METHOD_OUT, index=False)

    base_raw = summary[summary["method"].eq("raw_phone_base")].iloc[0]
    gates = summary[summary["joint_gate"]].copy()
    best_pseudo = summary.sort_values(["weighted_row_logloss", "weighted_mixmin_delta_vs_a2c8"]).iloc[0]
    best_hidden = hidden_by_method.iloc[0]
    s3_fixed = summary[summary["fixes_s3_vs_subject"]].sort_values(["weighted_row_logloss"]).head(10)
    lines = [
        "# E55 Raw Block Target-Dependency Probe",
        "",
        "## Observe",
        "",
        "E54 showed a split world: raw overnight context is a real strict block-state representation, but its best strict method regresses S3 and produces an adverse actual hidden mixmin sign.",
        "",
        "## Wonder",
        "",
        "If S3 and mixmin sign are target-manifold failures rather than raw-context failures, can other predicted target rates project each block back onto a train block-rate dependency manifold and repair both?",
        "",
        "## Hypothesis",
        "",
        "H55: a strict target-dependency/count projection should keep the raw overnight block-state gain, fix the S3 pseudo-hidden regression, and make actual hidden-block rates prefer mixmin rather than a2c8.",
        "",
        "## Method",
        "",
        f"- Pseudo-hidden blocks: `{len(state.pseudo_blocks)}`; actual hidden blocks: `{len(state.hidden_blocks)}`.",
        "- Base: `night_phone_rawctx_strict_k8_a24` from E54.",
        "- Context for projection: other target rates only, using strict subject-excluded donor blocks. Donor contexts use true donor block rates; query contexts use raw predicted block rates.",
        "- Estimators: kNN target-rate manifold and Ridge logit-rate projection.",
        "- Masks: S3 only, S2/S3, S-stage group, and all targets.",
        "- Stress: pseudo-hidden row/count LogLoss, S3 target recovery, train-rate manifold energy, and actual hidden-block expected mixmin delta versus a2c8.",
        "",
        "## Baseline Raw State",
        "",
        markdown_table(
            summary[summary["method"].isin(["subject_mean", "calendar_count_strict", "raw_phone_base"])],
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_subject",
                "delta_weighted_row_logloss_vs_raw",
                "s3_delta_vs_subject",
                "weighted_mixmin_delta_vs_a2c8",
                "joint_gate",
            ],
            max_rows=5,
        ),
        "",
        "## Top Pseudo-Hidden Methods",
        "",
        markdown_table(
            summary.sort_values(["weighted_row_logloss", "weighted_mixmin_delta_vs_a2c8"]),
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_raw",
                "s3_delta_vs_subject",
                "s3_delta_vs_raw",
                "weighted_mixmin_delta_vs_a2c8",
                "energy_delta_vs_raw",
                "joint_gate",
            ],
            max_rows=16,
        ),
        "",
        "## S3-Fixed Methods",
        "",
        markdown_table(
            s3_fixed,
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_raw",
                "s3_delta_vs_subject",
                "weighted_mixmin_delta_vs_a2c8",
                "joint_gate",
            ],
            max_rows=10,
        ),
        "",
        "## Best Hidden Mixmin Alignment",
        "",
        markdown_table(
            summary.sort_values(["weighted_mixmin_delta_vs_a2c8", "weighted_row_logloss"]),
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_raw",
                "s3_delta_vs_subject",
                "weighted_mixmin_delta_vs_a2c8",
                "mixmin_better_block_rate",
                "joint_gate",
            ],
            max_rows=16,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(gates):
        best_gate = gates.sort_values(["weighted_row_logloss", "weighted_mixmin_delta_vs_a2c8"]).iloc[0]
        lines.extend(
            [
                f"`{best_gate['method']}` passes the local joint gate: it improves or ties raw pseudo-hidden loss, fixes S3 versus subject mean, and gives negative hidden mixmin delta `{float(best_gate['weighted_mixmin_delta_vs_a2c8']):+.6f}`.",
                "",
                "This is still not a submission by itself because it only moves hidden-rate beliefs, not test probabilities. But it reopens a candidate-generation branch: target-dependency projection can reconcile raw block state with mixmin sign under local stress.",
            ]
        )
    else:
        lines.extend(
            [
                "No target-dependency projection passed the joint gate. The projection can improve one axis at a time, but not all three requirements together: preserve raw pseudo-hidden recovery, fix S3, and make hidden mixmin sign negative.",
                "",
                f"Raw base pseudo-hidden delta vs subject is `{float(base_raw['delta_weighted_row_logloss_vs_subject']):+.6f}`, S3 delta is `{float(base_raw['s3_delta_vs_subject']):+.6f}`, and hidden mixmin delta is `{float(base_raw['weighted_mixmin_delta_vs_a2c8']):+.6f}`.",
                f"The best pseudo-hidden method is `{best_pseudo['method']}` with raw delta `{float(best_pseudo['delta_weighted_row_logloss_vs_raw']):+.6f}` and hidden mixmin delta `{float(best_pseudo['weighted_mixmin_delta_vs_a2c8']):+.6f}`.",
                f"The best hidden mixmin alignment is `{best_hidden['method']}` at `{float(best_hidden['weighted_mixmin_delta_vs_a2c8']):+.6f}`.",
                "",
                "This weakens the idea that a simple target-dependency count manifold can translate the raw overnight latent into the mixmin-public latent. The remaining branch is a hard mixmin-constrained world model or a more structural target representation, not a post-hoc target projection.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TARGET_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_OUT.relative_to(ROOT)}`",
            f"- `{HIDDEN_TARGET_OUT.relative_to(ROOT)}`",
            f"- `{METHOD_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "methods=",
        len(summary),
        "joint_gates=",
        int(summary["joint_gate"].sum()),
        "best_pseudo=",
        best_pseudo["method"],
        f"{float(best_pseudo['delta_weighted_row_logloss_vs_raw']):+.6f}",
        "best_hidden=",
        best_hidden["method"],
        f"{float(best_hidden['weighted_mixmin_delta_vs_a2c8']):+.6f}",
    )
    print(summary.head(12).round(6).to_string(index=False))
    print(summary.sort_values(["weighted_mixmin_delta_vs_a2c8", "weighted_row_logloss"]).head(12).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
