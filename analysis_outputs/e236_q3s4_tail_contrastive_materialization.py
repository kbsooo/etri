#!/usr/bin/env python3
"""E236: materialize E234 Q3/S4 tail-contrastive policies on E224.

E234 showed that changing the JEPA target/loss to high-impact tail membership
can beat full Q3/S4 movement locally. E235 showed that the strongest S2 branch
does not transfer to public-safe submission geometry.

This script asks the next target-specific question:

Can E234's Q3/S4 tail policies improve the live E224 submission tensor under
the public-free E222/E230 support-tail stress?

No public LB is used. The script only materializes files if a learned tail mask
improves E224's expected/adverse/support geometry while preserving the E224
Q3/S4 body.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


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


Q3_IDX = TARGETS.index("Q3")
S4_IDX = TARGETS.index("S4")
E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

SCAN_OUT = OUT / "e236_q3s4_tail_contrastive_materialization_scan.csv"
TARGET_OUT = OUT / "e236_q3s4_tail_contrastive_materialization_targets.csv"
SELECTED_OUT = OUT / "e236_q3s4_tail_contrastive_materialization_selected.csv"
REPORT_OUT = OUT / "e236_q3s4_tail_contrastive_materialization_report.md"

EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def spec_tag(row: pd.Series) -> str:
    return (
        f"{row['target_kind']}_{row['policy']}_{row['model']}_{row['split']}_"
        f"{row['view']}_q{float(row['tail_q']):.2f}"
    ).replace(".", "p")


def target_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, list[str]]]:
    train_raw, train_long, sub_long, _ = e232.build_long_frames()
    train_long = e234.add_true_labels(train_long, train_raw)
    feats = e232.feature_sets(train_long)
    feats = {name: [c for c in cols if c != "true_label"] for name, cols in feats.items()}
    return train_long, sub_long, feats


def candidate_specs() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not e234.SELECTED_OUT.exists():
        e234.run()
    selected = pd.read_csv(e234.SELECTED_OUT)
    selected = selected[selected["stress_promote"].astype(bool)].copy()
    selected = selected[selected["policy"].astype(str).str.startswith("drop")].copy()
    selected["spec_tag"] = selected.apply(spec_tag, axis=1)
    selected = selected.drop_duplicates(["task", "spec_tag"]).sort_values(
        ["task", "loss_vs_full", "tail_auc"], ascending=[True, True, False]
    )
    q3 = selected[selected["task"].eq("q3_e224")].head(14).reset_index(drop=True)
    s4 = selected[selected["task"].eq("s4_e224")].head(14).reset_index(drop=True)
    return q3, s4


def fit_policy(row: pd.Series, train_long: pd.DataFrame, sub_long: pd.DataFrame, feats: dict[str, list[str]]) -> dict[str, Any]:
    task = str(row["task"])
    tr = train_long[train_long["task_name"].eq(task)].reset_index(drop=True)
    te = sub_long[sub_long["task_name"].eq(task)].reset_index(drop=True)
    cols = feats[str(row["view"])]
    model = e234.model_defs()[str(row["model"])]
    prob = e234.fit_full_tail_predict(model, tr, te, cols, str(row["target_kind"]), float(row["tail_q"]))
    amp = e234.amplitude_policies(str(row["target_kind"]), prob)[str(row["policy"])]
    dropped = np.asarray(amp, dtype=np.float64) < 0.05
    return {
        "tag": str(row["spec_tag"]),
        "task": task,
        "target": str(row["task"]).split("_", maxsplit=1)[0].upper(),
        "amp": np.asarray(amp, dtype=np.float64),
        "prob": prob,
        "dropped": dropped,
        "dropped_rows": int(np.sum(dropped)),
        "mean_amp": float(np.mean(amp)),
        "mean_prob": float(np.mean(prob)),
        "p10_prob": float(np.quantile(prob, 0.10)),
        "p50_prob": float(np.quantile(prob, 0.50)),
        "p90_prob": float(np.quantile(prob, 0.90)),
        "e234_loss_vs_full": float(row["loss_vs_full"]),
        "e234_target_delta": float(row["target_delta"]),
        "e234_tail_auc": float(row["tail_auc"]),
        "e234_subject_win_rate": float(row["subject_win_rate"]),
        "policy": str(row["policy"]),
        "view": str(row["view"]),
        "model": str(row["model"]),
        "split": str(row["split"]),
        "target_kind": str(row["target_kind"]),
        "tail_q": float(row["tail_q"]),
    }


def q3_overlap_metrics(dropped: np.ndarray) -> dict[str, Any]:
    dropped_set = set(np.where(dropped)[0].astype(int).tolist())
    prior_sets = e234.q3_prior_sets()
    out: dict[str, Any] = {}
    for name, prior in prior_sets.items():
        out[f"{name}_overlap"] = int(len(dropped_set & prior))
        out[f"{name}_jaccard"] = float(len(dropped_set & prior) / max(len(dropped_set | prior), 1))
    return out


def apply_policies(e154: np.ndarray, e224: np.ndarray, q3: dict[str, Any] | None, s4: dict[str, Any] | None) -> np.ndarray:
    out_logit = logit(e224).copy()
    anchor_logit = logit(e154)
    e224_logit = logit(e224)
    if q3 is not None:
        amp = np.asarray(q3["amp"], dtype=np.float64)
        out_logit[:, Q3_IDX] = anchor_logit[:, Q3_IDX] + amp * (e224_logit[:, Q3_IDX] - anchor_logit[:, Q3_IDX])
    if s4 is not None:
        amp = np.asarray(s4["amp"], dtype=np.float64)
        out_logit[:, S4_IDX] = anchor_logit[:, S4_IDX] + amp * (e224_logit[:, S4_IDX] - anchor_logit[:, S4_IDX])
    return clip_prob(sigmoid(out_logit))


def materialize(sample: pd.DataFrame, pred: np.ndarray, variant_id: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    file_name = f"submission_e236_e234tail_{variant_id[:80]}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def audit_candidate(
    variant_id: str,
    pred: np.ndarray,
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e95: np.ndarray,
    e154: np.ndarray,
    meta: dict[str, Any],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id=variant_id,
        file_name=variant_id,
        anchor_file=E154_FILE,
        family="e236_e234_q3s4_tail_materialization",
        status="generated",
        note="E234 tail-contrastive Q3/S4 mask applied to E224 and rolled back toward E154.",
    )
    rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for pair_kind, base_name, base in [
        ("graft_vs_e154", E154_FILE, e154),
        ("actual_vs_e95", E95_FILE, e95),
    ]:
        rec, tgt, _ = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
        rec.update(meta)
        rows.append(rec)
        if not tgt.empty:
            tgt = tgt.copy()
            for key, value in meta.items():
                if not isinstance(value, (list, dict, np.ndarray)):
                    tgt[key] = value
            target_parts.append(tgt)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    return rows, target_df


def target_metric(target_df: pd.DataFrame, target: str, source_col: str, prefix: str) -> pd.DataFrame:
    cols = [
        "candidate_id",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    part = target_df[target_df["pair_kind"].eq("graft_vs_e154") & target_df["target"].eq(target)][cols].copy()
    return part.rename(
        columns={
            "expected_focus": f"{prefix}_expected_focus",
            "adverse_delta": f"{prefix}_adverse_delta",
            "support_prob_focus_swing_weighted": f"{prefix}_support_prob",
            "top1_over_abs_expected": f"{prefix}_top1_over_abs_expected",
            source_col: source_col,
        }
    )


def add_comparison_metrics(summary: pd.DataFrame, target_df: pd.DataFrame, base_row: pd.Series, base_targets: pd.DataFrame) -> pd.DataFrame:
    out = e222.add_ranking(summary.copy())
    q3 = target_metric(target_df, "Q3", "candidate_id", "q3")
    s4 = target_metric(target_df, "S4", "candidate_id", "s4")
    out = out.merge(q3, on="candidate_id", how="left").merge(s4, on="candidate_id", how="left")

    base_q3 = base_targets[base_targets["target"].eq("Q3")].iloc[0]
    base_s4 = base_targets[base_targets["target"].eq("S4")].iloc[0]
    graft = out["pair_kind"].eq("graft_vs_e154")
    for col in [
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]:
        out[f"{col}_vs_e224"] = out[col] - float(base_row[col])
    out["adverse_reduction_vs_e224"] = float(base_row["adverse_delta"]) - out["adverse_delta"]
    out["expected_loss_vs_e224"] = out["expected_focus"] - float(base_row["expected_focus"])
    out["support_gain_vs_e224"] = out["support_prob_focus_swing_weighted"] - float(
        base_row["support_prob_focus_swing_weighted"]
    )
    out["q3_adverse_reduction_vs_e224"] = float(base_q3["adverse_delta"]) - out["q3_adverse_delta"].fillna(0.0)
    out["s4_adverse_reduction_vs_e224"] = float(base_s4["adverse_delta"]) - out["s4_adverse_delta"].fillna(0.0)
    out["q3_top1_delta_vs_e224"] = out["q3_top1_over_abs_expected"].fillna(9.0) - float(
        base_q3["top1_over_abs_expected"]
    )
    out["s4_top1_delta_vs_e224"] = out["s4_top1_over_abs_expected"].fillna(9.0) - float(
        base_s4["top1_over_abs_expected"]
    )

    out["e236_gate"] = False
    out.loc[graft, "e236_gate"] = (
        (out.loc[graft, "expected_focus"] <= float(base_row["expected_focus"]) + 0.000060)
        & (out.loc[graft, "adverse_reduction_vs_e224"] >= 0.000120)
        & (out.loc[graft, "support_gain_vs_e224"] >= 0.0020)
        & (out.loc[graft, "top1_over_abs_expected"] <= float(base_row["top1_over_abs_expected"]) + 0.010)
        & (out.loc[graft, "q3_top1_over_abs_expected"].fillna(float(base_q3["top1_over_abs_expected"])) <= 0.82)
        & (out.loc[graft, "q3_adverse_delta"].fillna(float(base_q3["adverse_delta"])) <= 0.00205)
        & (out.loc[graft, "q3_dropped_rows"].fillna(0).astype(float) <= 50)
        & (out.loc[graft, "s4_dropped_rows"].fillna(0).astype(float) <= 50)
    )
    out["e236_score"] = (
        -out["expected_loss_vs_e224"].fillna(0.0) * 2600.0
        + out["adverse_reduction_vs_e224"].fillna(0.0) * 1300.0
        + out["support_gain_vs_e224"].fillna(0.0) * 0.40
        - np.maximum(out["q3_top1_over_abs_expected"].fillna(9.0) - 0.78, 0.0) * 0.08
        - np.maximum(out["q3_dropped_rows"].fillna(0.0) - 25, 0.0) * 0.001
        - np.maximum(out["s4_dropped_rows"].fillna(0.0) - 25, 0.0) * 0.001
        - np.maximum(out["adverse_delta"].fillna(0.0) - float(base_row["adverse_delta"]), 0.0) * 700.0
    )
    return out


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_long, sub_long, feats = target_frames()
    q3_specs, s4_specs = candidate_specs()
    q3_policies = [fit_policy(row, train_long, sub_long, feats) for _, row in q3_specs.iterrows()]
    s4_policies = [fit_policy(row, train_long, sub_long, feats) for _, row in s4_specs.iterrows()]

    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    e95 = load_prob(E95_FILE, sample)
    e154 = load_prob(E154_FILE, sample)
    e224 = load_prob(E224_FILE, sample)

    base_spec = e222.Candidate(
        candidate_id="e224_original",
        file_name=E224_FILE,
        anchor_file=E154_FILE,
        family="e224_q3_scale_pareto",
        status="baseline",
        note="Current JEPA-first E224 candidate.",
    )
    base_rec, base_targets, _ = e222.pair_audit(base_spec, "graft_vs_e154", e224, e154, E154_FILE, priors, sample)
    base_row = pd.Series(base_rec)

    jobs: list[tuple[str, dict[str, Any] | None, dict[str, Any] | None]] = []
    for pol in q3_policies:
        jobs.append((f"q3_{pol['tag']}", pol, None))
    for pol in s4_policies:
        jobs.append((f"s4_{pol['tag']}", None, pol))
    for q3 in q3_policies[:8]:
        for s4 in s4_policies[:8]:
            jobs.append((f"q3_{q3['tag']}__s4_{s4['tag']}", q3, s4))

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    pred_cache: dict[str, np.ndarray] = {}
    for variant_id, q3, s4 in jobs:
        pred = apply_policies(e154, e224, q3, s4)
        pred_cache[variant_id] = pred
        q3_overlap = q3_overlap_metrics(q3["dropped"]) if q3 is not None else {}
        meta: dict[str, Any] = {
            "q3_tag": "" if q3 is None else q3["tag"],
            "s4_tag": "" if s4 is None else s4["tag"],
            "q3_policy": "" if q3 is None else q3["policy"],
            "s4_policy": "" if s4 is None else s4["policy"],
            "q3_dropped_rows": 0 if q3 is None else q3["dropped_rows"],
            "s4_dropped_rows": 0 if s4 is None else s4["dropped_rows"],
            "q3_e234_loss_vs_full": np.nan if q3 is None else q3["e234_loss_vs_full"],
            "s4_e234_loss_vs_full": np.nan if s4 is None else s4["e234_loss_vs_full"],
            "q3_e234_tail_auc": np.nan if q3 is None else q3["e234_tail_auc"],
            "s4_e234_tail_auc": np.nan if s4 is None else s4["e234_tail_auc"],
            "q3_subject_win_rate": np.nan if q3 is None else q3["e234_subject_win_rate"],
            "s4_subject_win_rate": np.nan if s4 is None else s4["e234_subject_win_rate"],
            **q3_overlap,
        }
        rows, targets = audit_candidate(variant_id, pred, sample, priors, e95, e154, meta)
        summary_rows.extend(rows)
        if not targets.empty:
            target_parts.append(targets)

    summary = pd.DataFrame(summary_rows)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    target_df = e222.add_ranking(target_df) if not target_df.empty else target_df
    summary = add_comparison_metrics(summary, target_df, base_row, base_targets) if not summary.empty else summary

    selected = summary[
        summary["pair_kind"].eq("graft_vs_e154") & summary["e236_gate"].fillna(False).astype(bool)
    ].sort_values(["e236_score", "expected_focus"], ascending=[False, True]).head(4).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        files.append(materialize(sample, pred_cache[str(row.candidate_id)], str(row.candidate_id)))
    if not selected.empty:
        selected["submission_file"] = files
        summary = summary.merge(selected[["candidate_id", "submission_file"]], on="candidate_id", how="left")
    else:
        summary["submission_file"] = ""
        selected["submission_file"] = ""

    summary = summary.sort_values(["pair_kind", "e236_gate", "e236_score"], ascending=[True, False, False])
    if not target_df.empty:
        target_df = target_df.sort_values(["pair_kind", "candidate_id", "target"])
    summary.to_csv(SCAN_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, target_df, selected, base_row, base_targets)
    return summary, target_df, selected


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, selected: pd.DataFrame, base_row: pd.Series, base_targets: pd.DataFrame) -> None:
    graft = summary[summary["pair_kind"].eq("graft_vs_e154")].sort_values(
        ["e236_gate", "e236_score"], ascending=[False, False]
    )
    actual = summary[summary["pair_kind"].eq("actual_vs_e95")].sort_values(
        ["e236_gate", "e236_score"], ascending=[False, False]
    )
    q3_only = graft[(graft["q3_dropped_rows"] > 0) & (graft["s4_dropped_rows"] == 0)]
    s4_only = graft[(graft["q3_dropped_rows"] == 0) & (graft["s4_dropped_rows"] > 0)]
    combo = graft[(graft["q3_dropped_rows"] > 0) & (graft["s4_dropped_rows"] > 0)]
    cols = [
        "candidate_id",
        "q3_dropped_rows",
        "s4_dropped_rows",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_delta",
        "adverse_reduction_vs_e224",
        "support_prob_focus_swing_weighted",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "s4_top1_over_abs_expected",
        "s4_adverse_delta",
        "q3_e230_q3_risk_top21_overlap",
        "q3_e230_q3_swing_top25_overlap",
        "e236_gate",
        "e236_score",
        "submission_file",
    ]
    # Preserve older column names from q3_overlap_metrics while rendering a compact table.
    rename_for_report = {
        "e230_q3_risk_top21_overlap": "q3_e230_q3_risk_top21_overlap",
        "e230_q3_swing_top25_overlap": "q3_e230_q3_swing_top25_overlap",
    }
    views = []
    for frame in [graft, actual, q3_only, s4_only, combo, selected]:
        views.append(frame.rename(columns=rename_for_report))
    graft_v, actual_v, q3_v, s4_v, combo_v, selected_v = views

    base_q3 = base_targets[base_targets["target"].eq("Q3")].iloc[0]
    base_s4 = base_targets[base_targets["target"].eq("S4")].iloc[0]
    lines = [
        "# E236 Q3/S4 Tail-Contrastive Materialization",
        "",
        "## Question",
        "",
        "Can E234's learned Q3/S4 high-impact tail masks improve the live E224 submission tensor under public-free tail stress?",
        "",
        "## Original E224 Baseline",
        "",
        f"- expected_focus: `{float(base_row['expected_focus']):.9f}`.",
        f"- adverse_delta: `{float(base_row['adverse_delta']):.9f}`.",
        f"- support_prob_focus_swing_weighted: `{float(base_row['support_prob_focus_swing_weighted']):.9f}`.",
        f"- Q3 adverse/top1: `{float(base_q3['adverse_delta']):.9f}` / `{float(base_q3['top1_over_abs_expected']):.9f}`.",
        f"- S4 adverse/top1: `{float(base_s4['adverse_delta']):.9f}` / `{float(base_s4['top1_over_abs_expected']):.9f}`.",
        "",
        "## Observed Read",
        "",
        f"- scanned candidate rows: `{len(summary)}` including actual-vs-E95 duplicates.",
        f"- graft-side gate passes: `{int(graft['e236_gate'].sum()) if not graft.empty else 0}`.",
        f"- materialized files: `{len(selected)}`.",
        "",
        "A pass must preserve E224 expected focus, reduce adverse capacity, improve support, and reduce Q3 top-cell concentration enough to be a learned alternative to E230's hand prune.",
        "",
        "## Selected",
        "",
        md_table(selected_v, cols, n=10),
        "",
        "## Graft vs E154 Top Rows",
        "",
        md_table(graft_v, cols, n=40),
        "",
        "## Actual vs E95 Top Rows",
        "",
        md_table(actual_v, cols, n=20),
        "",
        "## Q3-Only Learned Masks",
        "",
        md_table(q3_v, cols, n=20),
        "",
        "## S4-Only Learned Masks",
        "",
        md_table(s4_v, cols, n=20),
        "",
        "## Q3+S4 Combo Learned Masks",
        "",
        md_table(combo_v, cols, n=20),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.extend(
            [
                "- E234 Q3/S4 tail policies do not currently improve E224's public-free submission geometry enough to create a new public candidate.",
                "- This rejects the simplest learned replacement for E230's hand-pruned Q3 siblings.",
                "- Keep E224 as the clean JEPA public sensor and keep E230 as the conditional hand-prune after E224 feedback.",
            ]
        )
    else:
        best = selected.iloc[0]
        lines.extend(
            [
                f"- Best materialized file: `{best['submission_file']}`.",
                "- This is a learned E234 tail-mask alternative to E230's hand-pruned Q3 repair. It should still be treated as conditional unless the intended public question is specifically learned-tail materialization.",
                "- A public win would mean E234's high-impact target found a transferable Q3/S4 tail; a loss would demote learned tail masks and favor E224/E230 routebook discipline.",
            ]
        )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary, _, selected = run()
    print("[E236 selected]")
    cols = [
        "candidate_id",
        "q3_dropped_rows",
        "s4_dropped_rows",
        "expected_focus",
        "expected_loss_vs_e224",
        "adverse_delta",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "q3_adverse_delta",
        "e236_gate",
        "submission_file",
    ]
    print(selected[cols].to_string(index=False) if not selected.empty else "none")
    top = summary[summary["pair_kind"].eq("graft_vs_e154")].sort_values("e236_score", ascending=False).head(8)
    print("\n[E236 top graft rows]")
    print(top[cols[:-1]].round(9).to_string(index=False) if not top.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
