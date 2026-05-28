#!/usr/bin/env python3
"""E59 structural block target representation probe.

E54/E55 showed that strict raw overnight context recovers pseudo-hidden block
marginal target rates, but it breaks S3 and does not align with mixmin on real
hidden blocks. This probe asks a sharper JEPA-style question: is the useful
target representation a block-level joint label-pattern distribution rather
than seven independent marginal rates?
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import calendar_flank_block_count_state_probe as e53  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import raw_block_target_dependency_probe as e55  # noqa: E402
import raw_overnight_block_context_probe as e54  # noqa: E402


TARGETS = hbr.TARGETS
EPS = 1e-5
N_PATTERNS = 2 ** len(TARGETS)
PATTERN_BITS = ((np.arange(N_PATTERNS)[:, None] >> np.arange(len(TARGETS))[None, :]) & 1).astype(np.float64)
PAIR_INDEX = [(i, j) for i in range(len(TARGETS)) for j in range(i + 1, len(TARGETS))]
PAIR_BITS = np.stack([PATTERN_BITS[:, i] * PATTERN_BITS[:, j] for i, j in PAIR_INDEX], axis=1)

SUMMARY_OUT = OUT / "structural_block_target_probe_summary.csv"
TARGET_OUT = OUT / "structural_block_target_probe_target_detail.csv"
PATTERN_OUT = OUT / "structural_block_target_probe_pattern_detail.csv"
HIDDEN_OUT = OUT / "structural_block_target_probe_hidden_alignment.csv"
HIDDEN_TARGET_OUT = OUT / "structural_block_target_probe_hidden_target_alignment.csv"
REPORT_OUT = OUT / "structural_block_target_probe_report.md"


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray | float) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def pattern_ids(labels: np.ndarray) -> np.ndarray:
    powers = (1 << np.arange(len(TARGETS))).astype(np.int64)
    return (np.nan_to_num(labels, nan=0.0).astype(np.int64) * powers[None, :]).sum(axis=1)


def block_pattern_counts(y: np.ndarray, blocks: list[hbr.Block]) -> np.ndarray:
    counts = np.zeros((len(blocks), N_PATTERNS), dtype=np.float64)
    for i, block in enumerate(blocks):
        ids = pattern_ids(y[block.positions])
        counts[i] = np.bincount(ids, minlength=N_PATTERNS).astype(np.float64)
    return counts


def normalize_dist(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=np.float64), EPS)
    return x / x.sum(axis=-1, keepdims=True)


def independent_pattern_dist(rates: np.ndarray) -> np.ndarray:
    rates = clip(rates)
    logp = PATTERN_BITS[None, :, :] * np.log(rates)[:, None, :]
    logp += (1.0 - PATTERN_BITS[None, :, :]) * np.log(1.0 - rates)[:, None, :]
    logp = logp.sum(axis=2)
    logp -= logp.max(axis=1, keepdims=True)
    out = np.exp(logp)
    return normalize_dist(out)


def patterns_to_rates(dist: np.ndarray) -> np.ndarray:
    return clip(normalize_dist(dist) @ PATTERN_BITS)


def patterns_to_pairs(dist: np.ndarray) -> np.ndarray:
    return normalize_dist(dist) @ PAIR_BITS


def pattern_nll_per_row(counts: np.ndarray, dist: np.ndarray, block_sizes: np.ndarray) -> np.ndarray:
    return -np.sum(counts * np.log(normalize_dist(dist)), axis=1) / np.maximum(block_sizes, 1.0)


def pattern_entropy(dist: np.ndarray) -> np.ndarray:
    p = normalize_dist(dist)
    return -np.sum(p * np.log(p), axis=1)


def context_matrix(state: e55.BaseState, name: str, hidden: bool) -> np.ndarray:
    raw = state.hidden_raw if hidden else state.pseudo_raw
    cal = state.hidden_calendar if hidden else state.pseudo_calendar
    sub = state.hidden_subject if hidden else state.pseudo_subject
    if name == "raw":
        return logit(raw)
    if name == "raw_calendar":
        return np.concatenate([logit(raw), logit(cal), logit(raw) - logit(cal)], axis=1)
    if name == "raw_subject":
        return np.concatenate([logit(raw), logit(sub), logit(raw) - logit(sub)], axis=1)
    if name == "raw_calendar_subject":
        return np.concatenate([logit(raw), logit(cal), logit(sub), logit(raw) - logit(cal), logit(raw) - logit(sub)], axis=1)
    raise ValueError(name)


def fallback_rates(state: e55.BaseState, name: str, hidden: bool) -> np.ndarray:
    if name == "raw":
        return state.hidden_raw if hidden else state.pseudo_raw
    if name == "calendar":
        return state.hidden_calendar if hidden else state.pseudo_calendar
    if name == "subject":
        return state.hidden_subject if hidden else state.pseudo_subject
    raise ValueError(name)


def pseudo_donor_mask(blocks: list[hbr.Block], i: int) -> np.ndarray:
    return e55.donor_mask_for_pseudo(blocks, i)


def hidden_donor_mask(pseudo_blocks: list[hbr.Block], hidden_block: hbr.Block) -> np.ndarray:
    return e55.donor_mask_for_hidden(pseudo_blocks, hidden_block)


def structural_knn_predict(
    donor_context: np.ndarray,
    query_context: np.ndarray,
    donor_patterns: np.ndarray,
    fallback_dist: np.ndarray,
    pseudo_blocks: list[hbr.Block],
    query_blocks: list[hbr.Block],
    k: int,
    alpha: float,
    strength: float,
    hidden: bool,
) -> tuple[np.ndarray, pd.DataFrame]:
    scaler = StandardScaler()
    x_all = scaler.fit_transform(donor_context)
    q_all = scaler.transform(query_context)
    out = np.zeros((len(query_blocks), N_PATTERNS), dtype=np.float64)
    meta_rows: list[dict[str, Any]] = []
    donor_patterns = normalize_dist(donor_patterns)
    fallback_dist = normalize_dist(fallback_dist)

    for i, block in enumerate(query_blocks):
        mask = hidden_donor_mask(pseudo_blocks, block) if hidden else pseudo_donor_mask(pseudo_blocks, i)
        idx = np.where(mask)[0]
        if len(idx) == 0:
            local = fallback_dist[i]
            support = 0
            dist_median = np.nan
            local_entropy = np.nan
        else:
            dist = np.sqrt(np.maximum(((x_all[idx] - q_all[i]) ** 2).mean(axis=1), 0.0))
            order = np.argsort(dist)[: min(k, len(dist))]
            chosen_idx = idx[order]
            chosen_dist = dist[order]
            weights = 1.0 / np.maximum(chosen_dist, 1e-3)
            weights /= weights.sum()
            local = weights @ donor_patterns[chosen_idx]
            support = len(chosen_idx)
            dist_median = float(np.median(chosen_dist))
            local_entropy = float(pattern_entropy(local.reshape(1, -1))[0])
        shrunk = (float(support) * local + alpha * fallback_dist[i]) / (float(support) + alpha) if support else fallback_dist[i]
        pred = (1.0 - strength) * fallback_dist[i] + strength * normalize_dist(shrunk)
        out[i] = normalize_dist(pred)
        meta_rows.append(
            {
                "block_idx": i,
                "support": float(support),
                "dist_median": dist_median,
                "local_entropy": local_entropy,
                "pred_entropy": float(pattern_entropy(out[i].reshape(1, -1))[0]),
                "pred_top_mass": float(out[i].max()),
            }
        )
    return out, pd.DataFrame(meta_rows)


def pair_mse(true_patterns: np.ndarray, pred_patterns: np.ndarray) -> np.ndarray:
    true_pairs = patterns_to_pairs(true_patterns)
    pred_pairs = patterns_to_pairs(pred_patterns)
    return np.mean((true_pairs - pred_pairs) ** 2, axis=1)


def summarize(
    state: e55.BaseState,
    true_counts: np.ndarray,
    true_patterns: np.ndarray,
    methods: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]],
    method_meta: dict[str, dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    block_sizes = np.asarray([b.n for b in state.pseudo_blocks], dtype=np.float64)
    summary_rows = []
    target_rows = []
    pattern_rows = []
    hidden_rows = []
    hidden_target_rows = []

    for method, (pseudo_patterns, pseudo_rates, hidden_rates, hidden_meta) in methods.items():
        row, detail = e53.summarize_method(method, pseudo_rates, state.y, state.pseudo_blocks, state.counts, state.rates)
        pseudo_patterns = normalize_dist(pseudo_patterns)
        row_nll = pattern_nll_per_row(true_counts, pseudo_patterns, block_sizes)
        indep_same_margin = independent_pattern_dist(pseudo_rates)
        margin_only_nll = pattern_nll_per_row(true_counts, indep_same_margin, block_sizes)
        entropy = pattern_entropy(pseudo_patterns)
        top_mass = pseudo_patterns.max(axis=1)
        pair_err = pair_mse(true_patterns, pseudo_patterns)
        row.update(
            {
                "weighted_pattern_nll": float(np.average(row_nll, weights=block_sizes)),
                "mean_pattern_nll": float(np.mean(row_nll)),
                "weighted_margin_only_pattern_nll": float(np.average(margin_only_nll, weights=block_sizes)),
                "weighted_joint_gain_vs_own_margins": float(np.average(row_nll - margin_only_nll, weights=block_sizes)),
                "weighted_pair_mse": float(np.average(pair_err, weights=block_sizes)),
                "mean_pred_entropy": float(np.mean(entropy)),
                "mean_pred_top_mass": float(np.mean(top_mass)),
            }
        )
        row.update(method_meta.get(method, {}))
        summary_rows.append(row)
        target_rows.extend(detail)
        hidden_block_rows, hidden_target = e54.hidden_alignment(method, state.sample, state.rows, state.hidden_blocks, hidden_rates, hidden_meta)
        hidden_rows.extend(hidden_block_rows)
        hidden_target_rows.extend(hidden_target)
        top = np.argsort(row_nll - margin_only_nll)[:8]
        for i in top:
            pattern_rows.append(
                {
                    "method": method,
                    "block_idx": int(i),
                    "subject_id": state.pseudo_blocks[i].subject_id,
                    "n_rows": int(state.pseudo_blocks[i].n),
                    "pattern_nll": float(row_nll[i]),
                    "margin_only_pattern_nll": float(margin_only_nll[i]),
                    "joint_gain_vs_own_margins": float(row_nll[i] - margin_only_nll[i]),
                    "pair_mse": float(pair_err[i]),
                    "pred_entropy": float(entropy[i]),
                    "pred_top_mass": float(top_mass[i]),
                    "true_top_pattern": int(true_patterns[i].argmax()),
                    "pred_top_pattern": int(pseudo_patterns[i].argmax()),
                }
            )

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

    subject = summary[summary["method"].eq("subject_indep")].iloc[0]
    raw = summary[summary["method"].eq("raw_phone_indep")].iloc[0]
    summary["delta_weighted_row_logloss_vs_subject"] = summary["weighted_row_logloss"] - float(subject["weighted_row_logloss"])
    summary["delta_weighted_row_logloss_vs_raw"] = summary["weighted_row_logloss"] - float(raw["weighted_row_logloss"])
    summary["delta_pattern_nll_vs_subject"] = summary["weighted_pattern_nll"] - float(subject["weighted_pattern_nll"])
    summary["delta_pattern_nll_vs_raw"] = summary["weighted_pattern_nll"] - float(raw["weighted_pattern_nll"])
    summary["delta_pair_mse_vs_raw"] = summary["weighted_pair_mse"] - float(raw["weighted_pair_mse"])
    summary = summary.merge(hidden_by_method, on="method", how="left")

    target_base = target[target["method"].eq("subject_indep")].set_index("target")
    target_raw = target[target["method"].eq("raw_phone_indep")].set_index("target")
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
    summary["pattern_beats_raw"] = summary["delta_pattern_nll_vs_raw"].lt(0)
    summary["row_beats_raw"] = summary["delta_weighted_row_logloss_vs_raw"].lt(0)
    summary["joint_beats_margin"] = summary["weighted_joint_gain_vs_own_margins"].lt(-1e-5)
    summary["fixes_s3_vs_subject"] = summary["s3_delta_vs_subject"].le(0)
    summary["hidden_mixmin_negative"] = summary["weighted_mixmin_delta_vs_a2c8"].lt(0)
    summary["joint_gate"] = (
        summary["pattern_beats_raw"]
        & summary["row_beats_raw"]
        & summary["joint_beats_margin"]
        & summary["fixes_s3_vs_subject"]
        & summary["hidden_mixmin_negative"]
    )
    summary = summary.sort_values(
        ["joint_gate", "delta_pattern_nll_vs_raw", "delta_weighted_row_logloss_vs_raw"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    target = target.sort_values(["target", "target_row_logloss"]).reset_index(drop=True)
    hidden_by_method = hidden_by_method.sort_values(["weighted_mixmin_delta_vs_a2c8", "mean_mixmin_delta_vs_a2c8"]).reset_index(drop=True)
    hidden_target = hidden_target.sort_values(["target", "weighted_mixmin_delta_vs_a2c8"]).reset_index(drop=True)
    return summary, target, pd.DataFrame(pattern_rows), hidden_by_method, hidden_target


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 16) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def write_report(summary: pd.DataFrame, hidden: pd.DataFrame, target: pd.DataFrame) -> None:
    gates = int(summary["joint_gate"].sum())
    best_pattern = summary.iloc[0]
    best_hidden = hidden.iloc[0]
    lines = [
        "# E59 Structural Block Target Representation Probe",
        "",
        "Question: are hidden block targets better represented as a 128-state joint label-pattern distribution than as seven independent marginal rates?",
        "",
        "Decision gates:",
        "",
        "- pseudo-hidden pattern NLL improves over raw independent pattern baseline;",
        "- pseudo-hidden row LogLoss also improves over raw marginal baseline;",
        "- predicted joint pattern carries information beyond its own marginals;",
        "- S3 does not regress versus subject mean;",
        "- real hidden-block expected mixmin delta versus a2c8 is negative.",
        "",
        f"Joint gates opened: `{gates}`.",
        "",
        "Best by structural pattern stress:",
        "",
        markdown_table(
            summary,
            [
                "method",
                "weighted_pattern_nll",
                "delta_pattern_nll_vs_raw",
                "weighted_joint_gain_vs_own_margins",
                "delta_weighted_row_logloss_vs_raw",
                "s3_delta_vs_subject",
                "weighted_mixmin_delta_vs_a2c8",
                "joint_gate",
            ],
            12,
        ),
        "",
        "Best hidden mixmin alignment:",
        "",
        markdown_table(
            hidden,
            [
                "method",
                "weighted_mixmin_delta_vs_a2c8",
                "mean_mixmin_delta_vs_a2c8",
                "mixmin_better_block_rate",
            ],
            12,
        ),
        "",
        "Target stress for the best structural method:",
        "",
        markdown_table(
            target[target["method"].eq(str(best_pattern["method"]))],
            ["target", "target_row_logloss", "delta_row_vs_subject", "delta_row_vs_raw"],
            7,
        ),
        "",
        "Interpretation:",
        "",
    ]
    if gates:
        lines.append(
            "At least one structural target representation survived all local and hidden-sign gates. This should become a candidate-generation branch, not just a diagnostic."
        )
    else:
        lines.append(
            "No structural joint-pattern method survived the full gate. If pattern NLL improves without row/mixmin survival, the joint structure is learnable but not the current public frontier latent."
        )
    lines.extend(
        [
            "",
            "Most informative rows:",
            "",
            f"- best structural method: `{best_pattern['method']}`",
            f"- best hidden-sign method: `{best_hidden['method']}`",
            "",
            "Next action:",
            "",
            "Use this result to decide whether the next branch should translate joint-pattern structure into a submission, or abandon joint labels and seek an independent non-anchor validator for the E56 posterior.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    state = e55.build_base_state()
    true_counts = block_pattern_counts(state.y, state.pseudo_blocks)
    block_sizes = np.asarray([b.n for b in state.pseudo_blocks], dtype=np.float64)
    true_patterns = normalize_dist(true_counts + 1e-6)
    empirical_patterns = normalize_dist(true_counts + 1e-3 * independent_pattern_dist(state.rates))

    methods: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]] = {}
    method_meta: dict[str, dict[str, Any]] = {}
    for name, pseudo_rates, hidden_rates in [
        ("subject_indep", state.pseudo_subject, state.hidden_subject),
        ("calendar_count_indep", state.pseudo_calendar, state.hidden_calendar),
        ("raw_phone_indep", state.pseudo_raw, state.hidden_raw),
    ]:
        pseudo_patterns = independent_pattern_dist(pseudo_rates)
        hidden_meta = pd.DataFrame(
            {
                "support": np.full(len(state.hidden_blocks), np.nan),
                "dist_median": np.full(len(state.hidden_blocks), np.nan),
            }
        )
        methods[name] = (pseudo_patterns, patterns_to_rates(pseudo_patterns), hidden_rates, hidden_meta)
        method_meta[name] = {"family": "baseline", "context": "", "fallback": name.replace("_indep", ""), "k": np.nan, "alpha": np.nan, "strength": np.nan}

    method_count = 0
    for context_name in ["raw", "raw_calendar", "raw_subject", "raw_calendar_subject"]:
        donor_context = context_matrix(state, context_name, hidden=False)
        hidden_context = context_matrix(state, context_name, hidden=True)
        for fallback_name in ["raw", "subject"]:
            fallback_pseudo = independent_pattern_dist(fallback_rates(state, fallback_name, hidden=False))
            fallback_hidden = independent_pattern_dist(fallback_rates(state, fallback_name, hidden=True))
            for k in [4, 8, 16]:
                for alpha in [4.0, 12.0, 24.0]:
                    for strength in [0.35, 0.65, 1.0]:
                        method = f"struct_{context_name}_fb{fallback_name}_k{k}_a{alpha:g}_w{strength:.2f}"
                        pseudo_patterns, pseudo_meta = structural_knn_predict(
                            donor_context,
                            donor_context,
                            empirical_patterns,
                            fallback_pseudo,
                            state.pseudo_blocks,
                            state.pseudo_blocks,
                            k,
                            alpha,
                            strength,
                            hidden=False,
                        )
                        hidden_patterns, hidden_meta = structural_knn_predict(
                            donor_context,
                            hidden_context,
                            empirical_patterns,
                            fallback_hidden,
                            state.pseudo_blocks,
                            state.hidden_blocks,
                            k,
                            alpha,
                            strength,
                            hidden=True,
                        )
                        pseudo_rates = patterns_to_rates(pseudo_patterns)
                        hidden_rates = patterns_to_rates(hidden_patterns)
                        methods[method] = (pseudo_patterns, pseudo_rates, hidden_rates, hidden_meta)
                        method_meta[method] = {
                            "family": "structural_knn",
                            "context": context_name,
                            "fallback": fallback_name,
                            "k": float(k),
                            "alpha": float(alpha),
                            "strength": float(strength),
                            "pseudo_support_mean": float(pseudo_meta["support"].mean()),
                            "hidden_support_mean": float(hidden_meta["support"].mean()),
                            "pseudo_dist_median": float(pseudo_meta["dist_median"].median()),
                            "hidden_dist_median": float(hidden_meta["dist_median"].median()),
                            "true_pattern_entropy_weighted": float(np.average(pattern_entropy(true_patterns), weights=block_sizes)),
                        }
                        method_count += 1

    summary, target, pattern, hidden, hidden_target = summarize(state, true_counts, true_patterns, methods, method_meta)
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    pattern.to_csv(PATTERN_OUT, index=False)
    hidden.to_csv(HIDDEN_OUT, index=False)
    hidden_target.to_csv(HIDDEN_TARGET_OUT, index=False)
    write_report(summary, hidden, target)
    print(
        {
            "methods": len(summary),
            "structural_methods": method_count,
            "joint_gates": int(summary["joint_gate"].sum()),
            "best_method": str(summary.iloc[0]["method"]),
            "best_delta_pattern_vs_raw": float(summary.iloc[0]["delta_pattern_nll_vs_raw"]),
            "best_delta_row_vs_raw": float(summary.iloc[0]["delta_weighted_row_logloss_vs_raw"]),
            "best_hidden_mixmin_delta": float(summary.iloc[0]["weighted_mixmin_delta_vs_a2c8"]),
            "best_hidden_method": str(hidden.iloc[0]["method"]),
            "best_hidden_mixmin_delta_any": float(hidden.iloc[0]["weighted_mixmin_delta_vs_a2c8"]),
        }
    )


if __name__ == "__main__":
    main()
