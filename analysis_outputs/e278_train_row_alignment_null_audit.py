#!/usr/bin/env python3
"""E278: train-label row-alignment null audit for q-sleep diary energy.

E277 blocked every q-sleep candidate because test-side matched shuffles looked
as good as the real row placement under the public-free selector.

This script asks the complementary supervised question on train:
when the same policy is applied to labeled train rows on top of an OOF
calendar/subject baseline, does the real row placement reduce Q-target logloss
more than row/subject/dateblock matched shuffles?

If not, the branch needs a new row-alignment objective before any more
probability tensors are generated.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e274_target_specific_diary_energy_audit import (  # noqa: E402
    FEATURE_PATH,
    TARGETS,
    base_matrix,
    clip_prob,
    fit_predict,
    robust_z,
    sigmoid,
)
from e276_q_sleep_story_ablation_placebo_audit import q_axes_top12  # noqa: E402
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


RNG_SEED = 20260531 + 278
Q_TARGETS = ["Q1", "Q2", "Q3"]
N_REPS = 200

SUMMARY_OUT = OUT / "e278_train_row_alignment_null_summary.csv"
TARGET_OUT = OUT / "e278_train_row_alignment_null_target_detail.csv"
NULL_OUT = OUT / "e278_train_row_alignment_null_distribution.csv"
REPORT_OUT = OUT / "e278_train_row_alignment_null_report.md"


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def variant_specs(axes: pd.DataFrame) -> list[dict[str, object]]:
    families = ["mobility_context", "bedtime_phone", "routine_calendar", "cognitive_money", "social_comm", "media_game", "diary_global"]
    specs: list[dict[str, object]] = [
        {"candidate_id": "full_qsleep", "variant_type": "primary", "axes": axes},
        {"candidate_id": "q3_only", "variant_type": "target_ablation", "axes": axes[axes["target"].eq("Q3")]},
        {"candidate_id": "q12_only", "variant_type": "target_ablation", "axes": axes[axes["target"].isin(["Q1", "Q2"])]},
        {"candidate_id": "jepa_only", "variant_type": "axis_kind", "axes": axes[axes["axis_kind"].str.startswith("jepa")]},
        {"candidate_id": "nonjepa_only", "variant_type": "axis_kind", "axes": axes[~axes["axis_kind"].str.startswith("jepa")]},
    ]
    for family in families:
        specs.append({"candidate_id": f"only_{family}", "variant_type": "family_only", "family": family, "axes": axes[axes["story_family"].eq(family)]})
        specs.append({"candidate_id": f"no_{family}", "variant_type": "leave_one_family", "family": family, "axes": axes[~axes["story_family"].eq(family)]})
    specs.append({"candidate_id": "inverse_full_qsleep_m080", "variant_type": "inverse_control", "axes": axes, "inverse_scale": 0.80})
    return specs


def oof_baseline(train: pd.DataFrame, group_col: str) -> np.ndarray:
    groups = train[group_col].astype(str).to_numpy()
    uniq = np.unique(groups)
    if len(uniq) < 2:
        raise RuntimeError(f"not enough groups for {group_col}")
    cv = GroupKFold(n_splits=min(5, len(uniq)))
    out = np.zeros((len(train), len(Q_TARGETS)), dtype=np.float64)
    for target_idx, target in enumerate(Q_TARGETS):
        y = train[target].to_numpy(dtype=int)
        for tr_idx, va_idx in cv.split(train, y, groups=groups):
            tr = train.iloc[tr_idx]
            va = train.iloc[va_idx]
            x_tr, cols = base_matrix(tr)
            x_va, _ = base_matrix(va, cols)
            out[va_idx, target_idx] = fit_predict(x_tr, tr[target].to_numpy(dtype=int), x_va)
    return clip_prob(out)


def q_mean_logloss(y: np.ndarray, prob: np.ndarray) -> float:
    losses = []
    for idx in range(prob.shape[1]):
        losses.append(log_loss(y[:, idx], clip_prob(prob[:, idx]), labels=[0, 1]))
    return float(np.mean(losses))


def target_logloss_delta(y: np.ndarray, base_prob: np.ndarray, cand_prob: np.ndarray) -> dict[str, float]:
    out = {}
    for idx, target in enumerate(Q_TARGETS):
        out[target] = float(
            log_loss(y[:, idx], clip_prob(cand_prob[:, idx]), labels=[0, 1])
            - log_loss(y[:, idx], clip_prob(base_prob[:, idx]), labels=[0, 1])
        )
    return out


def candidate_delta(train: pd.DataFrame, base_logits: np.ndarray, axes: pd.DataFrame, inverse_scale: float | None = None) -> tuple[np.ndarray, pd.DataFrame]:
    logits = base_logits.copy()
    original = base_logits.copy()
    cell_rows: list[dict[str, object]] = []
    amp = 0.045 * 1.60
    cap = 0.090
    top_each = 12

    for _, row in axes.sort_values("local_axis_score", ascending=False).iterrows():
        target = str(row["target"])
        if target not in Q_TARGETS:
            continue
        target_idx = Q_TARGETS.index(target)
        feature = str(row["feature"])
        direction = int(row["direction"])
        if direction == 0 or feature not in train.columns:
            continue
        z_train, _, _ = robust_z(train[feature], train[feature])
        effect = direction * z_train
        order_hi = np.argsort(effect)[::-1]
        order_lo = np.argsort(effect)
        chosen = np.zeros(len(train), dtype=bool)
        chosen[order_hi[:top_each]] = True
        chosen[order_lo[:top_each]] = True
        scale = np.clip(float(row["abs_label_lift"]) / 0.20, 0.45, 1.60)
        raw_delta = amp * scale * np.clip(effect / 2.5, -1.0, 1.0)
        delta = np.where(chosen, raw_delta, 0.0)
        before = logits[:, target_idx].copy()
        logits[:, target_idx] = np.clip(logits[:, target_idx] + delta, original[:, target_idx] - cap, original[:, target_idx] + cap)
        applied = logits[:, target_idx] - before
        for idx in np.where(np.abs(applied) > 1.0e-12)[0]:
            cell_rows.append(
                {
                    "row_idx": int(idx),
                    "subject_id": train.iloc[idx]["subject_id"],
                    "dateblock_group": train.iloc[idx]["dateblock_group"],
                    "target": target,
                    "feature": feature,
                    "story_family": row.get("story_family", ""),
                    "axis_kind": row.get("axis_kind", ""),
                    "feature_effect": float(effect[idx]),
                    "logit_delta": float(applied[idx]),
                    "label": int(train.iloc[idx][target]),
                }
            )
    delta = logits - original
    if inverse_scale is not None:
        delta = -float(inverse_scale) * delta
        for item in cell_rows:
            item["logit_delta"] = -float(inverse_scale) * float(item["logit_delta"])
    return delta, pd.DataFrame(cell_rows)


def shuffle_delta(delta: np.ndarray, groups: pd.Series | None, rng: np.random.Generator) -> np.ndarray:
    out = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
        values = delta[:, target_idx].copy()
        if groups is None:
            out[:, target_idx] = values[rng.permutation(len(values))]
        else:
            for _, idx in groups.groupby(groups).indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                out[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
    return out


def audit_variant(
    train: pd.DataFrame,
    y: np.ndarray,
    base_prob: np.ndarray,
    base_logits: np.ndarray,
    spec: dict[str, object],
    split_name: str,
    rng: np.random.Generator,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    axes = spec["axes"]
    assert isinstance(axes, pd.DataFrame)
    delta, cells = candidate_delta(train, base_logits, axes, spec.get("inverse_scale"))
    cand_prob = clip_prob(sigmoid(base_logits + delta))
    base_loss = q_mean_logloss(y, base_prob)
    cand_loss = q_mean_logloss(y, cand_prob)
    actual_delta = cand_loss - base_loss

    null_rows: list[dict[str, object]] = []
    null_losses: list[float] = []
    modes = {
        "row": None,
        "subject": train["subject_id"].astype(str),
        "dateblock": train["dateblock_group"].astype(str),
    }
    for mode, groups in modes.items():
        for rep in range(N_REPS):
            shuffled = shuffle_delta(delta, groups, rng)
            prob = clip_prob(sigmoid(base_logits + shuffled))
            loss_delta = q_mean_logloss(y, prob) - base_loss
            null_losses.append(loss_delta)
            null_rows.append(
                {
                    "candidate_id": spec["candidate_id"],
                    "split": split_name,
                    "mode": mode,
                    "rep": rep,
                    "null_delta": float(loss_delta),
                }
            )
    null_arr = np.asarray(null_losses, dtype=np.float64)
    mode_dom = {}
    for mode in modes:
        vals = np.asarray([r["null_delta"] for r in null_rows if r["mode"] == mode], dtype=np.float64)
        mode_dom[f"{mode}_dominance"] = float(np.mean(actual_delta < vals))
        mode_dom[f"{mode}_null_q20"] = float(np.quantile(vals, 0.20))
        mode_dom[f"{mode}_null_best"] = float(np.min(vals))

    dominance = float(np.mean(actual_delta < null_arr))
    null_q20 = float(np.quantile(null_arr, 0.20))
    null_median = float(np.median(null_arr))
    train_align_gate = bool(
        actual_delta < 0.0
        and dominance >= 0.80
        and min(mode_dom["row_dominance"], mode_dom["subject_dominance"], mode_dom["dateblock_dominance"]) >= 0.60
        and actual_delta <= null_q20 - 1.0e-5
        and spec["variant_type"] != "inverse_control"
    )
    target_deltas = target_logloss_delta(y, base_prob, cand_prob)
    summary = {
        "candidate_id": spec["candidate_id"],
        "variant_type": spec["variant_type"],
        "family": spec.get("family", ""),
        "split": split_name,
        "axis_count": int(len(axes)),
        "changed_cells": int(np.count_nonzero(np.abs(delta) > 1.0e-12)),
        "changed_rows": int(np.any(np.abs(delta) > 1.0e-12, axis=1).sum()),
        "base_loss": base_loss,
        "candidate_loss": cand_loss,
        "actual_delta": actual_delta,
        "null_q20": null_q20,
        "null_median": null_median,
        "null_best": float(np.min(null_arr)),
        "dominance": dominance,
        "placebo_adjusted_vs_median": actual_delta - null_median,
        "placebo_adjusted_vs_best": actual_delta - float(np.min(null_arr)),
        "train_align_gate": train_align_gate,
        **mode_dom,
        **{f"{target}_delta": value for target, value in target_deltas.items()},
    }
    target_rows = [
        {
            "candidate_id": spec["candidate_id"],
            "variant_type": spec["variant_type"],
            "split": split_name,
            "target": target,
            "target_delta": value,
        }
        for target, value in target_deltas.items()
    ]
    if not cells.empty:
        summary["selected_label_mean"] = float(cells["label"].mean())
        summary["selected_abs_logit_delta_mean"] = float(cells["logit_delta"].abs().mean())
    else:
        summary["selected_label_mean"] = np.nan
        summary["selected_abs_logit_delta_mean"] = 0.0
    return summary, target_rows, null_rows


def write_report(summary: pd.DataFrame, target_detail: pd.DataFrame, nulls: pd.DataFrame) -> None:
    gates = summary[summary["train_align_gate"].astype(bool)] if not summary.empty else pd.DataFrame()
    both_split = (
        summary.groupby("candidate_id")["train_align_gate"].sum().reset_index(name="split_gate_count")
        if not summary.empty
        else pd.DataFrame()
    )
    both_split = both_split[both_split["split_gate_count"] >= 2] if not both_split.empty else both_split
    cols = [
        "candidate_id",
        "variant_type",
        "family",
        "split",
        "axis_count",
        "changed_cells",
        "actual_delta",
        "null_q20",
        "null_median",
        "dominance",
        "row_dominance",
        "subject_dominance",
        "dateblock_dominance",
        "placebo_adjusted_vs_median",
        "placebo_adjusted_vs_best",
        "train_align_gate",
        "Q1_delta",
        "Q2_delta",
        "Q3_delta",
    ]
    mode_summary = (
        nulls.groupby(["candidate_id", "split", "mode"], dropna=False)
        .agg(n=("null_delta", "size"), best=("null_delta", "min"), q20=("null_delta", lambda x: float(np.quantile(x, 0.20))), median=("null_delta", "median"))
        .reset_index()
        .sort_values(["candidate_id", "split", "mode"])
        if not nulls.empty
        else pd.DataFrame()
    )
    lines = [
        "# E278 Train Row-Alignment Null Audit",
        "",
        "## Question",
        "",
        "Do q-sleep diary-energy policies pick labeled train rows better than matched row/subject/dateblock shuffle nulls when applied on top of OOF calendar/subject baselines?",
        "",
        "## Method",
        "",
        "- Baselines: OOF logistic calendar/subject models for Q1/Q2/Q3.",
        "- Splits: subject-group OOF and dateblock-group OOF.",
        "- Policies: same E275/E276 q-sleep semantic variants.",
        f"- Nulls: `{N_REPS}` per row/subject/dateblock mode per candidate/split.",
        "- Metric: mean Q1/Q2/Q3 logloss delta versus OOF baseline; lower is better.",
        "",
        "## Summary",
        "",
        f"- candidate/split rows: `{len(summary)}`",
        f"- train-align gate rows: `{len(gates)}`",
        f"- candidates passing both subject and dateblock gates: `{len(both_split)}`",
        "",
        "## Candidate Results",
        "",
        md_table(summary[cols].sort_values(["train_align_gate", "dominance", "actual_delta"], ascending=[False, False, True]), n=80),
        "",
        "## Target Detail",
        "",
        md_table(target_detail.sort_values(["candidate_id", "split", "target"]), n=80),
        "",
        "## Null Mode Summary",
        "",
        md_table(mode_summary.head(100), n=100),
        "",
        "## Decision",
        "",
    ]
    if len(both_split):
        lines.append("At least one policy beats train matched nulls on both split views. It should be cross-checked against E277 test matched-placebo failure before materialization.")
    else:
        lines.append("No policy beats train matched nulls on both subject and dateblock OOF views. This strengthens the diagnosis that q-sleep diary energy lacks a row-alignment objective.")
    lines.extend([
        "",
        "## Next Action",
        "",
        "Do not make another q-sleep submission. Train a target that directly predicts row-alignment or candidate-vs-shuffle benefit, especially for JEPA/mobility/Q3, then rerun E277.",
        "",
        "## Files",
        "",
        f"- `{SUMMARY_OUT.name}`",
        f"- `{TARGET_OUT.name}`",
        f"- `{NULL_OUT.name}`",
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    features = pd.read_parquet(FEATURE_PATH)
    train = features[features["split"].eq("train")].reset_index(drop=True)
    axes = q_axes_top12()
    specs = variant_specs(axes)
    y = train[Q_TARGETS].to_numpy(dtype=int)
    rows: list[dict[str, object]] = []
    target_rows: list[dict[str, object]] = []
    null_rows: list[dict[str, object]] = []
    rng = np.random.default_rng(RNG_SEED)

    for split_name, group_col in [("subject_oof", "subject_id"), ("dateblock_oof", "dateblock_group")]:
        base_prob = oof_baseline(train, group_col)
        base_logits = logit(base_prob)
        for spec in specs:
            summary, targets, nulls = audit_variant(train, y, base_prob, base_logits, spec, split_name, rng)
            rows.append(summary)
            target_rows.extend(targets)
            null_rows.extend(nulls)

    summary = pd.DataFrame(rows).sort_values(["train_align_gate", "dominance", "actual_delta"], ascending=[False, False, True])
    target_detail = pd.DataFrame(target_rows)
    nulls = pd.DataFrame(null_rows)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_detail.to_csv(TARGET_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(summary, target_detail, nulls)
    print(REPORT_OUT)
    print(
        summary[
            [
                "candidate_id",
                "split",
                "actual_delta",
                "null_median",
                "dominance",
                "row_dominance",
                "subject_dominance",
                "dateblock_dominance",
                "train_align_gate",
            ]
        ].head(40).round(9).to_string(index=False)
    )


if __name__ == "__main__":
    main()
