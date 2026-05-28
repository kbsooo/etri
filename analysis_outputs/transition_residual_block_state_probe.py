#!/usr/bin/env python3
"""E60 transition-residual block-state probe.

E59 showed that within-block joint labels are learnable but do not translate
into row-calibrated, mixmin-aligned movement. This probe moves the target from
"what labels co-occur inside the block?" to "how does the hidden block depart
from its labeled calendar flanks?". The representation is a strict
subject-excluded residual in logit-rate space.
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

SUMMARY_OUT = OUT / "transition_residual_block_state_probe_summary.csv"
TARGET_OUT = OUT / "transition_residual_block_state_probe_target_detail.csv"
HIDDEN_OUT = OUT / "transition_residual_block_state_probe_hidden_alignment.csv"
HIDDEN_TARGET_OUT = OUT / "transition_residual_block_state_probe_hidden_target_alignment.csv"
REPORT_OUT = OUT / "transition_residual_block_state_probe_report.md"


def clip(x: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray | float) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def sigmoid(z: np.ndarray | float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(z, dtype=np.float64)))


def endpoint_mid(features: list[e53.ProbeFeatures]) -> np.ndarray:
    out = np.zeros((len(features), len(TARGETS)), dtype=np.float64)
    for i, feature in enumerate(features):
        row = feature.subject_mean.copy()
        for j in range(len(TARGETS)):
            vals = []
            if np.isfinite(feature.prev[j]):
                vals.append(float(feature.prev[j]))
            if np.isfinite(feature.next[j]):
                vals.append(float(feature.next[j]))
            if vals:
                row[j] = float(np.mean(vals))
        out[i] = clip(row)
    return out


def endpoint_shrink(features: list[e53.ProbeFeatures], weight: float) -> np.ndarray:
    return np.vstack([e53.edge_shrink_predict(f, weight) for f in features]).astype(np.float64)


def base_matrix(state: e55.BaseState, name: str, hidden: bool) -> np.ndarray:
    features = state.hidden_features if hidden else state.pseudo_features
    if name == "subject":
        return state.hidden_subject if hidden else state.pseudo_subject
    if name == "raw":
        return state.hidden_raw if hidden else state.pseudo_raw
    if name == "calendar":
        return state.hidden_calendar if hidden else state.pseudo_calendar
    if name == "edge_mid":
        return endpoint_mid(features)
    if name == "edge_shrink025":
        return endpoint_shrink(features, 0.25)
    if name == "edge_shrink050":
        return endpoint_shrink(features, 0.50)
    raise ValueError(name)


def topology_matrix(features: list[e53.ProbeFeatures]) -> np.ndarray:
    context_types = ["between_train_runs", "after_train_run", "before_train_run", "isolated"]
    len_bins = ["1-2", "3-5", "6-10", "11-16"]
    rows = []
    for f in features:
        rows.append(
            np.r_[
                f.ctx,
                float(f.n),
                float(f.has_left),
                float(f.has_right),
                [1.0 if f.context_type == c else 0.0 for c in context_types],
                [1.0 if f.len_bin == b else 0.0 for b in len_bins],
            ]
        )
    return np.vstack(rows).astype(np.float64)


def context_matrix(state: e55.BaseState, name: str, hidden: bool, base: np.ndarray) -> np.ndarray:
    raw = state.hidden_raw if hidden else state.pseudo_raw
    cal = state.hidden_calendar if hidden else state.pseudo_calendar
    sub = state.hidden_subject if hidden else state.pseudo_subject
    topo = topology_matrix(state.hidden_features if hidden else state.pseudo_features)
    if name == "topology":
        return topo
    if name == "raw_residual":
        return np.concatenate([logit(raw) - logit(base), logit(cal) - logit(base), logit(sub) - logit(base)], axis=1)
    if name == "raw_topology":
        return np.concatenate([topo, logit(raw), logit(base), logit(raw) - logit(base)], axis=1)
    if name == "full_transition":
        return np.concatenate(
            [topo, logit(raw), logit(cal), logit(sub), logit(base), logit(raw) - logit(base), logit(cal) - logit(base)],
            axis=1,
        )
    raise ValueError(name)


def donor_mask_for_pseudo(blocks: list[hbr.Block], i: int) -> np.ndarray:
    return e55.donor_mask_for_pseudo(blocks, i)


def donor_mask_for_hidden(pseudo_blocks: list[hbr.Block], hidden_block: hbr.Block) -> np.ndarray:
    return e55.donor_mask_for_hidden(pseudo_blocks, hidden_block)


def residual_knn_predict(
    donor_context: np.ndarray,
    query_context: np.ndarray,
    donor_residual: np.ndarray,
    base_query: np.ndarray,
    pseudo_blocks: list[hbr.Block],
    query_blocks: list[hbr.Block],
    k: int,
    alpha: float,
    strength: float,
    hidden: bool,
) -> tuple[np.ndarray, pd.DataFrame]:
    scaler = StandardScaler()
    x_all = scaler.fit_transform(np.nan_to_num(donor_context, nan=0.0, posinf=0.0, neginf=0.0))
    q_all = scaler.transform(np.nan_to_num(query_context, nan=0.0, posinf=0.0, neginf=0.0))
    out = np.zeros((len(query_blocks), len(TARGETS)), dtype=np.float64)
    meta_rows: list[dict[str, Any]] = []
    for i, block in enumerate(query_blocks):
        mask = donor_mask_for_hidden(pseudo_blocks, block) if hidden else donor_mask_for_pseudo(pseudo_blocks, i)
        idx = np.where(mask)[0]
        if len(idx) == 0:
            residual = np.zeros(len(TARGETS), dtype=np.float64)
            support = 0
            dist_median = np.nan
        else:
            dist = np.sqrt(np.maximum(((x_all[idx] - q_all[i]) ** 2).mean(axis=1), 0.0))
            order = np.argsort(dist)[: min(k, len(dist))]
            chosen_idx = idx[order]
            chosen_dist = dist[order]
            weights = 1.0 / np.maximum(chosen_dist, 1e-3)
            weights /= weights.sum()
            local = weights @ donor_residual[chosen_idx]
            support = len(chosen_idx)
            residual = (float(support) * local) / (float(support) + alpha)
            dist_median = float(np.median(chosen_dist))
        pred = sigmoid(logit(base_query[i]) + strength * residual)
        out[i] = clip(pred)
        meta_rows.append(
            {
                "block_idx": i,
                "support": float(support),
                "dist_median": dist_median,
                "residual_l2": float(np.sqrt(np.mean(residual**2))),
            }
        )
    return clip(out), pd.DataFrame(meta_rows)


def transition_residual_mse(pred: np.ndarray, base: np.ndarray, true_rates: np.ndarray, weights: np.ndarray) -> float:
    pred_res = logit(pred) - logit(base)
    true_res = logit(true_rates) - logit(base)
    return float(np.average(np.mean((pred_res - true_res) ** 2, axis=1), weights=weights))


def summarize(
    state: e55.BaseState,
    methods: dict[str, tuple[np.ndarray, np.ndarray, pd.DataFrame, np.ndarray]],
    meta: dict[str, dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    target_rows = []
    hidden_rows = []
    hidden_target_rows = []
    weights = np.asarray([b.n for b in state.pseudo_blocks], dtype=np.float64)
    for method, (pseudo_pred, hidden_pred, hidden_meta, pseudo_base) in methods.items():
        row, detail = e53.summarize_method(method, pseudo_pred, state.y, state.pseudo_blocks, state.counts, state.rates)
        row["transition_residual_mse"] = transition_residual_mse(pseudo_pred, pseudo_base, state.rates, weights)
        row.update(meta.get(method, {}))
        summary_rows.append(row)
        target_rows.extend(detail)
        block_rows, target_alignment = e54.hidden_alignment(method, state.sample, state.rows, state.hidden_blocks, hidden_pred, hidden_meta)
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
    raw_residual = float(summary.loc[summary["method"].eq("raw_phone_base"), "transition_residual_mse"].iloc[0])
    summary["delta_weighted_row_logloss_vs_subject"] = summary["weighted_row_logloss"] - subject_loss
    summary["delta_weighted_row_logloss_vs_raw"] = summary["weighted_row_logloss"] - raw_loss
    summary["delta_transition_residual_mse_vs_raw"] = summary["transition_residual_mse"] - raw_residual
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
    summary["row_beats_raw"] = summary["delta_weighted_row_logloss_vs_raw"].le(0)
    summary["transition_mse_beats_raw"] = summary["delta_transition_residual_mse_vs_raw"].le(0)
    summary["fixes_s3_vs_subject"] = summary["s3_delta_vs_subject"].le(0)
    summary["hidden_mixmin_negative"] = summary["weighted_mixmin_delta_vs_a2c8"].lt(0)
    summary["joint_gate"] = (
        summary["row_beats_raw"]
        & summary["transition_mse_beats_raw"]
        & summary["fixes_s3_vs_subject"]
        & summary["hidden_mixmin_negative"]
    )
    summary = summary.sort_values(
        ["joint_gate", "delta_weighted_row_logloss_vs_raw", "weighted_mixmin_delta_vs_a2c8"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    target = target.sort_values(["target", "target_row_logloss"]).reset_index(drop=True)
    hidden_by_method = hidden_by_method.sort_values(["weighted_mixmin_delta_vs_a2c8", "mean_mixmin_delta_vs_a2c8"]).reset_index(drop=True)
    hidden_target = hidden_target.sort_values(["target", "weighted_mixmin_delta_vs_a2c8"]).reset_index(drop=True)
    return summary, target, hidden_by_method, hidden_target


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 16) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in view.columns) + " |")
    return "\n".join(lines)


def write_report(summary: pd.DataFrame, target: pd.DataFrame, hidden: pd.DataFrame) -> None:
    gates = int(summary["joint_gate"].sum())
    best = summary.iloc[0]
    best_hidden = hidden.iloc[0]
    lines = [
        "# E60 Transition-Residual Block-State Probe",
        "",
        "Question: does the hidden block state live in the transition residual from labeled flanks to the hidden run, rather than in within-block marginal or joint labels?",
        "",
        "Decision gates:",
        "",
        "- row LogLoss improves over E54 raw phone base;",
        "- transition-residual MSE improves over raw phone base;",
        "- S3 does not regress versus subject mean;",
        "- real hidden-block expected mixmin delta versus a2c8 is negative.",
        "",
        f"Joint gates opened: `{gates}`.",
        "",
        "Best by row/raw stress:",
        "",
        markdown_table(
            summary,
            [
                "method",
                "weighted_row_logloss",
                "delta_weighted_row_logloss_vs_raw",
                "delta_transition_residual_mse_vs_raw",
                "s3_delta_vs_subject",
                "weighted_mixmin_delta_vs_a2c8",
                "joint_gate",
            ],
            14,
        ),
        "",
        "Best hidden mixmin alignment:",
        "",
        markdown_table(
            hidden,
            ["method", "weighted_mixmin_delta_vs_a2c8", "mean_mixmin_delta_vs_a2c8", "mixmin_better_block_rate"],
            12,
        ),
        "",
        "Target stress for the best row/raw method:",
        "",
        markdown_table(
            target[target["method"].eq(str(best["method"]))],
            ["target", "target_row_logloss", "delta_row_vs_subject", "delta_row_vs_raw"],
            7,
        ),
        "",
        "Interpretation:",
        "",
    ]
    if gates:
        lines.append(
            "At least one transition-residual method survived the full local and hidden-sign gate. It should be promoted to candidate-generation stress before any public submission."
        )
    else:
        lines.append(
            "No transition-residual method survived the full gate. If row/raw recovery improves without hidden mixmin sign, transition structure is real but not enough to explain the current frontier."
        )
    lines.extend(
        [
            "",
            "Most informative rows:",
            "",
            f"- best row/raw method: `{best['method']}`",
            f"- best hidden-sign method: `{best_hidden['method']}`",
            "",
            "Next action:",
            "",
            "If no gate opens, use transition-residual features as non-anchor diagnostics for E56 teacher reliability rather than as direct probability movement.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    state = e55.build_base_state()
    methods: dict[str, tuple[np.ndarray, np.ndarray, pd.DataFrame, np.ndarray]] = {}
    meta: dict[str, dict[str, Any]] = {}
    empty_hidden_meta = pd.DataFrame(
        {"support": np.full(len(state.hidden_blocks), np.nan), "dist_median": np.full(len(state.hidden_blocks), np.nan)}
    )
    for name, pseudo, hidden in [
        ("subject_mean", state.pseudo_subject, state.hidden_subject),
        ("calendar_count_strict", state.pseudo_calendar, state.hidden_calendar),
        ("raw_phone_base", state.pseudo_raw, state.hidden_raw),
        ("edge_mid", base_matrix(state, "edge_mid", False), base_matrix(state, "edge_mid", True)),
        ("edge_shrink025", base_matrix(state, "edge_shrink025", False), base_matrix(state, "edge_shrink025", True)),
        ("edge_shrink050", base_matrix(state, "edge_shrink050", False), base_matrix(state, "edge_shrink050", True)),
    ]:
        methods[name] = (clip(pseudo), clip(hidden), empty_hidden_meta, clip(pseudo))
        meta[name] = {"family": "baseline", "context": "", "base": name, "k": np.nan, "alpha": np.nan, "strength": np.nan}

    method_count = 0
    for base_name in ["edge_mid", "edge_shrink025", "subject", "raw"]:
        base_pseudo = base_matrix(state, base_name, False)
        base_hidden = base_matrix(state, base_name, True)
        donor_residual = logit(state.rates) - logit(base_pseudo)
        for context_name in ["topology", "raw_residual", "raw_topology", "full_transition"]:
            donor_context = context_matrix(state, context_name, False, base_pseudo)
            hidden_context = context_matrix(state, context_name, True, base_hidden)
            for k in [4, 8, 16]:
                for alpha in [4.0, 12.0, 24.0]:
                    for strength in [0.35, 0.65, 1.0]:
                        method = f"transition_{context_name}_base{base_name}_k{k}_a{alpha:g}_w{strength:.2f}"
                        pseudo_pred, pseudo_meta = residual_knn_predict(
                            donor_context,
                            donor_context,
                            donor_residual,
                            base_pseudo,
                            state.pseudo_blocks,
                            state.pseudo_blocks,
                            k,
                            alpha,
                            strength,
                            hidden=False,
                        )
                        hidden_pred, hidden_meta = residual_knn_predict(
                            donor_context,
                            hidden_context,
                            donor_residual,
                            base_hidden,
                            state.pseudo_blocks,
                            state.hidden_blocks,
                            k,
                            alpha,
                            strength,
                            hidden=True,
                        )
                        methods[method] = (pseudo_pred, hidden_pred, hidden_meta, base_pseudo)
                        meta[method] = {
                            "family": "transition_residual",
                            "context": context_name,
                            "base": base_name,
                            "k": float(k),
                            "alpha": float(alpha),
                            "strength": float(strength),
                            "pseudo_support_mean": float(pseudo_meta["support"].mean()),
                            "hidden_support_mean": float(hidden_meta["support"].mean()),
                            "pseudo_dist_median": float(pseudo_meta["dist_median"].median()),
                            "hidden_dist_median": float(hidden_meta["dist_median"].median()),
                            "pseudo_residual_l2_mean": float(pseudo_meta["residual_l2"].mean()),
                            "hidden_residual_l2_mean": float(hidden_meta["residual_l2"].mean()),
                        }
                        method_count += 1

    summary, target, hidden, hidden_target = summarize(state, methods, meta)
    summary.to_csv(SUMMARY_OUT, index=False)
    target.to_csv(TARGET_OUT, index=False)
    hidden.to_csv(HIDDEN_OUT, index=False)
    hidden_target.to_csv(HIDDEN_TARGET_OUT, index=False)
    write_report(summary, target, hidden)
    print(
        {
            "methods": len(summary),
            "transition_methods": method_count,
            "joint_gates": int(summary["joint_gate"].sum()),
            "row_beats_raw": int(summary["row_beats_raw"].sum()),
            "transition_mse_beats_raw": int(summary["transition_mse_beats_raw"].sum()),
            "hidden_mixmin_negative": int(summary["hidden_mixmin_negative"].sum()),
            "best_method": str(summary.iloc[0]["method"]),
            "best_row_delta_vs_raw": float(summary.iloc[0]["delta_weighted_row_logloss_vs_raw"]),
            "best_hidden_mixmin_delta": float(summary.iloc[0]["weighted_mixmin_delta_vs_a2c8"]),
            "best_hidden_method": str(hidden.iloc[0]["method"]),
            "best_hidden_mixmin_delta_any": float(hidden.iloc[0]["weighted_mixmin_delta_vs_a2c8"]),
        }
    )


if __name__ == "__main__":
    main()
