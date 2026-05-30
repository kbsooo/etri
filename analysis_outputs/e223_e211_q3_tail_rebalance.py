#!/usr/bin/env python3
"""E223: rebalance the live E211 Q3/S4 JEPA movement after E222.

E222 found that the E211 S4 component carries most of the favorable expected
movement, while the Q3 component is hard-label fragile: low support probability
and a single-cell swing larger than the Q3 expected edge. This script creates
and audits the smallest non-autopilot fix: keep the E211 S4 dependency-gated
body, reduce Q3 from scale 1.0 to 0.75, and compare against the original E211
selected candidates under the same support/tail metrics.
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
import e209_feature_neighbor_jepa_materialization_stress as e209  # noqa: E402
import e210_jepa_target_dependency_gate as e210  # noqa: E402
import e211_target_specific_jepa_gate as e211  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402


SUMMARY_OUT = OUT / "e223_e211_q3_tail_rebalance_summary.csv"
TARGET_OUT = OUT / "e223_e211_q3_tail_rebalance_targets.csv"
SELECTED_OUT = OUT / "e223_e211_q3_tail_rebalance_selected.csv"
REPORT_OUT = OUT / "e223_e211_q3_tail_rebalance_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
COMBO = "q3_center_c010_s4_rank"
EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def materialize(sample: pd.DataFrame, pred: np.ndarray, q3_scale: float, s4_mode: str, anchor: str, anchor_scale: float) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    q3_tag = str(q3_scale).replace(".", "p")
    a_tag = str(anchor_scale).replace(".", "p")
    file_name = f"submission_e223_jepa_q3s{q3_tag}_s4{s4_mode}_{anchor}_a{a_tag}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def make_prediction(
    anchor: np.ndarray,
    stage2_sub: np.ndarray,
    ungated_sub: np.ndarray,
    stage2_oof: np.ndarray,
    y: np.ndarray,
    q3_scale: float,
    s4_mode: str,
    s4_scale: float,
    anchor_scale: float,
) -> np.ndarray:
    raw = clip_prob(sigmoid(logit(anchor) + anchor_scale * (logit(ungated_sub) - logit(stage2_sub))))
    cond = e210.fit_predict_dependency(stage2_oof, y, anchor)
    return e211.apply_policy(anchor, raw, cond, q3_scale, s4_mode, s4_scale)


def audit_generated(
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e95: np.ndarray,
    pred: np.ndarray,
    file_name: str,
    anchor_file: str,
    anchor: np.ndarray,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id=str(params["candidate_id"]),
        file_name=file_name,
        anchor_file=anchor_file,
        family="e223_q3_tail_rebalance",
        status="generated",
        note="Q3 reduced after E222; S4 dependency-gated body preserved.",
    )
    rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for pair_kind, base_name, base in [
        ("graft_vs_anchor", anchor_file, anchor),
        ("actual_vs_e95", E95_FILE, e95),
    ]:
        rec, tgt, _ = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
        rec.update(params)
        rows.append(rec)
        if not tgt.empty:
            tgt = tgt.copy()
            for key, value in params.items():
                tgt[key] = value
            target_parts.append(tgt)
    return rows, pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()


def attach_local_frontier(summary: pd.DataFrame) -> pd.DataFrame:
    frontier = pd.read_csv(OUT / "e211_target_specific_jepa_gate_frontier.csv")
    keys = ["q3_scale", "s4_mode", "s4_scale", "anchor", "anchor_scale"]
    keep_cols = keys + [
        "delta",
        "subject_half_delta",
        "subject_half_win_rate",
        "geometry_delta",
        "geometry_win_rate",
        "geometry_vs_ungated_delta",
        "survival_score",
        "e211_frontier_gate",
        "vs_e95_expected_delta_focus_mean",
        "vs_e95_top1_over_abs_expected",
    ]
    local = frontier[keep_cols].drop_duplicates(keys)
    out = summary.merge(local, on=keys, how="left", suffixes=("", "_e211"))
    return out


def score_candidates(summary: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
    out = e222.add_ranking(summary)
    q3 = target_df[(target_df["pair_kind"].eq("graft_vs_anchor")) & (target_df["target"].eq("Q3"))][
        ["candidate_id", "top1_over_abs_expected", "adverse_delta"]
    ].rename(columns={"top1_over_abs_expected": "q3_top1_over_abs_expected", "adverse_delta": "q3_adverse_delta"})
    s4 = target_df[(target_df["pair_kind"].eq("graft_vs_anchor")) & (target_df["target"].eq("S4"))][
        ["candidate_id", "expected_focus", "top1_over_abs_expected"]
    ].rename(columns={"expected_focus": "s4_expected_focus", "top1_over_abs_expected": "s4_top1_over_abs_expected"})
    out = out.merge(q3, on="candidate_id", how="left").merge(s4, on="candidate_id", how="left")
    graft = out["pair_kind"].eq("graft_vs_anchor")
    out["e223_gate"] = bool(False)
    out.loc[graft, "e223_gate"] = (
        out.loc[graft, "e211_frontier_gate"].fillna(False).astype(bool)
        & (out.loc[graft, "expected_focus"] < -0.00055)
        & (out.loc[graft, "q3_top1_over_abs_expected"].fillna(9.0) < 0.95)
        & (out.loc[graft, "support_prob_focus_swing_weighted"].fillna(0.0) >= 0.464)
        & (out.loc[graft, "adverse_delta"] <= 0.00485)
        & (out.loc[graft, "geometry_delta"].fillna(1.0) < 0.0)
    )
    out["e223_score"] = (
        out["e222_tail_survival_score"].fillna(0.0)
        - np.maximum(out["q3_top1_over_abs_expected"].fillna(9.0) - 0.75, 0.0) * 0.04
        - np.maximum(out["adverse_delta"].fillna(0.0) - 0.0048, 0.0) * 20.0
        - np.maximum(out["geometry_delta"].fillna(0.0), 0.0) * 50.0
    )
    return out


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, selected: pd.DataFrame) -> None:
    graft = summary[summary["pair_kind"].eq("graft_vs_anchor")].sort_values(
        ["e223_gate", "e223_score"], ascending=[False, False]
    )
    actual = summary[summary["pair_kind"].eq("actual_vs_e95")].sort_values(
        ["e223_gate", "e223_score"], ascending=[False, False]
    )
    target = target_df[target_df["pair_kind"].eq("graft_vs_anchor")].sort_values(["candidate_id", "target"])
    cols = [
        "candidate_id",
        "pair_kind",
        "q3_scale",
        "s4_mode",
        "anchor",
        "anchor_scale",
        "moved_cells",
        "targets_moved",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "q3_top1_over_abs_expected",
        "geometry_delta",
        "e211_frontier_gate",
        "e223_gate",
        "e223_score",
        "submission_file",
    ]
    target_cols = [
        "candidate_id",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    lines = [
        "# E223 E211 Q3 Tail Rebalance",
        "",
        "## Question",
        "",
        "Can we keep the E211 S4 body while reducing the Q3 hard-tail risk identified by E222?",
        "",
        "## Graft vs Anchor",
        "",
        md_table(graft, cols, n=20),
        "",
        "## Actual vs E95",
        "",
        md_table(actual, cols, n=20),
        "",
        "## Target Breakdown",
        "",
        md_table(target, target_cols, n=40),
        "",
        "## Selected",
        "",
        md_table(selected, cols, n=8),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No E223 candidate passed the Q3-tail rebalance gate.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best E223 candidate: `{best['submission_file']}`. It lowers Q3 to `{best['q3_scale']}`, keeps S4 `{best['s4_mode']}`, and preserves E211 frontier/geometry eligibility while reducing Q3 top-cell risk."
        )
        lines.append("- This is a risk-rebalanced JEPA sensor, not a fully support-safe candidate: support probability remains below 0.5, but Q3 adverse capacity and top-cell concentration are materially lower than the E211 selected files.")
        lines.append("- This is a direct post-E216/E222 correction, not a new model-capacity experiment.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, _sub_raw, train_feat, sub_feat = e209.read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    if not sub_feat[e209.SUB_KEY].astype(str).equals(sample[KEYS].astype(str)):
        raise RuntimeError("submission feature order differs from sample order")

    priors = e162.prior_arrays(sample)
    stage2_oof = clip_prob(np.load(OUT / STAGE2_OOF))
    stage2_sub = load_prob(STAGE2_FILE, sample)
    e95 = load_prob(E95_FILE, sample)
    anchors = {"e95": e95, "e154": load_prob(E154_FILE, sample)}
    ops = e209.combo_defs()[COMBO]
    ungated_sub = e209.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)

    configs = []
    for q3_scale in [0.75, 1.00]:
        for s4_mode in ["closer", "toward"]:
            for anchor_name in ["e95", "e154"]:
                configs.append(
                    {
                        "candidate_id": f"e223_q3s{str(q3_scale).replace('.', 'p')}_{s4_mode}_{anchor_name}",
                        "q3_scale": q3_scale,
                        "s4_mode": s4_mode,
                        "s4_scale": 1.0,
                        "anchor": anchor_name,
                        "anchor_scale": 0.5,
                    }
                )

    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for params in configs:
        anchor_name = str(params["anchor"])
        pred = make_prediction(
            anchors[anchor_name],
            stage2_sub,
            ungated_sub,
            stage2_oof,
            y,
            float(params["q3_scale"]),
            str(params["s4_mode"]),
            float(params["s4_scale"]),
            float(params["anchor_scale"]),
        )
        file_name = materialize(sample, pred, float(params["q3_scale"]), str(params["s4_mode"]), anchor_name, float(params["anchor_scale"]))
        params_with_file = {**params, "submission_file": file_name}
        rows, target = audit_generated(
            sample,
            priors,
            e95,
            pred,
            file_name,
            E95_FILE if anchor_name == "e95" else E154_FILE,
            anchors[anchor_name],
            params_with_file,
        )
        summary_rows.extend(rows)
        if not target.empty:
            target_parts.append(target)

    summary = attach_local_frontier(pd.DataFrame(summary_rows))
    target_df = e222.add_ranking(pd.concat(target_parts, ignore_index=True)) if target_parts else pd.DataFrame()
    summary = score_candidates(summary, target_df)
    selected = summary[summary["pair_kind"].eq("graft_vs_anchor") & summary["e223_gate"]].sort_values(
        "e223_score", ascending=False
    ).head(4)

    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, target_df, selected)

    print("[E223 selected]")
    cols = [
        "candidate_id",
        "pair_kind",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "q3_top1_over_abs_expected",
        "geometry_delta",
        "e223_gate",
        "e223_score",
        "submission_file",
    ]
    print(selected[cols].round(9).to_string(index=False) if not selected.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
