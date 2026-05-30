#!/usr/bin/env python3
"""E224: Q3 scale Pareto sweep for the E211/E223 JEPA lane.

E223 tested only the smallest manual correction after E222: Q3 scale 0.75
instead of 1.0. This experiment asks the next narrower question: is 0.75 a
real Pareto point, or does a lower Q3 scale keep enough local/geometry support
while cutting the hard-label tail further?

The script recomputes OOF, subject-half, geometry, and submission-side
support-tail metrics for a small Q3 scale grid. It creates only selected
Pareto submission files.
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


SUMMARY_OUT = OUT / "e224_e211_q3_scale_pareto_summary.csv"
TARGET_OUT = OUT / "e224_e211_q3_scale_pareto_targets.csv"
GEOMETRY_OUT = OUT / "e224_e211_q3_scale_pareto_geometry.csv"
SELECTED_OUT = OUT / "e224_e211_q3_scale_pareto_selected.csv"
REPORT_OUT = OUT / "e224_e211_q3_scale_pareto_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
STAGE2_FILE = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
STAGE2_OOF = "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
COMBO = "q3_center_c010_s4_rank"
Q3_IDX = TARGETS.index("Q3")
EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip_prob(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def scale_tag(x: float) -> str:
    return (f"{x:.3f}".rstrip("0").rstrip(".")).replace(".", "p")


def materialize(sample: pd.DataFrame, pred: np.ndarray, candidate_id: str) -> str:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    file_name = f"submission_e224_{candidate_id}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(OUT / file_name, index=False)
    return file_name


def target_rows(y: np.ndarray, base: np.ndarray, pred: np.ndarray, prefix: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for j, target in enumerate(TARGETS):
        rows.append(
            {
                **prefix,
                "target": target,
                "local_target_delta": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j]),
                "moved_abs_logit": float(np.abs(logit(pred[:, j]) - logit(base[:, j])).mean()),
            }
        )
    return rows


def local_summary(
    train_raw: pd.DataFrame,
    sub_raw: pd.DataFrame,
    train_feat: pd.DataFrame,
    stage2_oof: np.ndarray,
    ungated_oof: np.ndarray,
    dep_oof: np.ndarray,
    ops: list[e209.Op],
    q3_scale: float,
    s4_mode: str,
) -> tuple[dict[str, Any], pd.DataFrame, np.ndarray]:
    y = train_raw[TARGETS].to_numpy(dtype=int)
    pred_oof = e211.apply_policy(stage2_oof, ungated_oof, dep_oof, q3_scale, s4_mode, 1.0)
    subj = e209.subject_half_summary(train_raw, y, stage2_oof, pred_oof, f"e224:{q3_scale}:{s4_mode}")
    geo = e211.geometry_summary(train_raw, sub_raw, train_feat, stage2_oof, ops, q3_scale, s4_mode, 1.0)
    rec = {
        "q3_scale": q3_scale,
        "s4_mode": s4_mode,
        "local_delta": mean_loss(y, pred_oof) - mean_loss(y, stage2_oof),
        "q3_local_target_delta": loss_col(y[:, Q3_IDX], pred_oof[:, Q3_IDX]) - loss_col(y[:, Q3_IDX], stage2_oof[:, Q3_IDX]),
        "subject_half_delta": float(subj["delta_mean"].mean()),
        "subject_half_win_rate": float((subj["delta_mean"] < 0).mean()),
        "geometry_delta": float(geo["delta_mean"].mean()),
        "geometry_win_rate": float((geo["delta_mean"] < 0).mean()),
        "geometry_vs_ungated_delta": float(geo["delta_mean"].mean() - geo["ungated_delta_mean"].mean()),
        "keep_abs_share_oof": e211.keep_share(stage2_oof, ungated_oof, pred_oof),
    }
    return rec, geo, pred_oof


def make_sub_prediction(
    anchor: np.ndarray,
    stage2_sub: np.ndarray,
    ungated_sub: np.ndarray,
    stage2_oof: np.ndarray,
    y: np.ndarray,
    q3_scale: float,
    s4_mode: str,
    anchor_scale: float,
) -> np.ndarray:
    raw = clip_prob(sigmoid(logit(anchor) + anchor_scale * (logit(ungated_sub) - logit(stage2_sub))))
    cond = e210.fit_predict_dependency(stage2_oof, y, anchor)
    return e211.apply_policy(anchor, raw, cond, q3_scale, s4_mode, 1.0)


def audit_pred(
    sample: pd.DataFrame,
    priors: dict[str, np.ndarray],
    e95: np.ndarray,
    pred: np.ndarray,
    anchor: np.ndarray,
    anchor_file: str,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id=str(params["candidate_id"]),
        file_name=str(params["candidate_id"]),
        anchor_file=anchor_file,
        family="e224_q3_scale_pareto",
        status="generated",
        note="Q3 scale sweep with E211 S4 dependency-gated body.",
    )
    rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    for pair_kind, base_name, base in [
        ("graft_vs_anchor", anchor_file, anchor),
        ("actual_vs_e95", E95_FILE, e95),
    ]:
        rec, tgt, _top = e222.pair_audit(spec, pair_kind, pred, base, base_name, priors, sample)
        rec.update(params)
        rows.append(rec)
        if not tgt.empty:
            tgt = tgt.copy()
            for key, value in params.items():
                tgt[key] = value
            target_parts.append(tgt)
    return rows, pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()


def add_scores(summary: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
    out = e222.add_ranking(summary)
    q3 = target_df[(target_df["pair_kind"].eq("graft_vs_anchor")) & (target_df["target"].eq("Q3"))][
        ["candidate_id", "top1_over_abs_expected", "adverse_delta", "expected_focus"]
    ].rename(
        columns={
            "top1_over_abs_expected": "q3_top1_over_abs_expected",
            "adverse_delta": "q3_adverse_delta",
            "expected_focus": "q3_expected_focus",
        }
    )
    s4 = target_df[(target_df["pair_kind"].eq("graft_vs_anchor")) & (target_df["target"].eq("S4"))][
        ["candidate_id", "top1_over_abs_expected", "expected_focus", "adverse_delta"]
    ].rename(
        columns={
            "top1_over_abs_expected": "s4_top1_over_abs_expected",
            "expected_focus": "s4_expected_focus",
            "adverse_delta": "s4_adverse_delta",
        }
    )
    out = out.merge(q3, on="candidate_id", how="left").merge(s4, on="candidate_id", how="left")
    graft = out["pair_kind"].eq("graft_vs_anchor")
    out["e224_gate"] = False
    out.loc[graft, "e224_gate"] = (
        (out.loc[graft, "local_delta"] <= -0.00090)
        & (out.loc[graft, "subject_half_win_rate"] >= 0.90)
        & (out.loc[graft, "geometry_delta"] < 0.0)
        & (out.loc[graft, "expected_focus"] <= -0.00058)
        & (out.loc[graft, "adverse_delta"] <= 0.00425)
        & (out.loc[graft, "support_prob_focus_swing_weighted"] >= 0.464)
        & (out.loc[graft, "q3_top1_over_abs_expected"].fillna(9.0) <= 0.88)
    )
    out["e224_score"] = (
        -out["local_delta"].fillna(0.0) * 120.0
        -out["expected_focus"].fillna(0.0) * 850.0
        -np.maximum(out["adverse_delta"].fillna(0.0) - 0.0038, 0.0) * 40.0
        -np.maximum(out["q3_top1_over_abs_expected"].fillna(9.0) - 0.75, 0.0) * 0.04
        +np.maximum(out["support_prob_focus_swing_weighted"].fillna(0.0) - 0.46, 0.0) * 0.25
        -np.maximum(out["geometry_delta"].fillna(0.0), 0.0) * 60.0
    )
    return out


def pareto_front(frame: pd.DataFrame) -> pd.DataFrame:
    """Pareto front over lower-is-better adverse/q3 tail and higher-is-better edge."""
    cols = ["expected_focus", "adverse_delta", "q3_top1_over_abs_expected", "local_delta"]
    data = frame.dropna(subset=cols).copy()
    keep = []
    for idx, row in data.iterrows():
        dominated = False
        for other_idx, other in data.iterrows():
            if idx == other_idx:
                continue
            no_worse = (
                other["expected_focus"] <= row["expected_focus"]
                and other["adverse_delta"] <= row["adverse_delta"]
                and other["q3_top1_over_abs_expected"] <= row["q3_top1_over_abs_expected"]
                and other["local_delta"] <= row["local_delta"]
            )
            strictly_better = (
                other["expected_focus"] < row["expected_focus"]
                or other["adverse_delta"] < row["adverse_delta"]
                or other["q3_top1_over_abs_expected"] < row["q3_top1_over_abs_expected"]
                or other["local_delta"] < row["local_delta"]
            )
            if bool(no_worse and strictly_better):
                dominated = True
                break
        if not dominated:
            keep.append(idx)
    return data.loc[keep].copy()


def write_report(summary: pd.DataFrame, target_df: pd.DataFrame, selected: pd.DataFrame, pareto: pd.DataFrame) -> None:
    graft = summary[summary["pair_kind"].eq("graft_vs_anchor")].sort_values(
        ["e224_gate", "e224_score"], ascending=[False, False]
    )
    actual = summary[summary["pair_kind"].eq("actual_vs_e95")].sort_values(
        ["e224_gate", "e224_score"], ascending=[False, False]
    )
    target = target_df[target_df["pair_kind"].eq("graft_vs_anchor")].sort_values(["candidate_id", "target"])
    cols = [
        "candidate_id",
        "pair_kind",
        "q3_scale",
        "s4_mode",
        "anchor",
        "local_delta",
        "geometry_delta",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "q3_top1_over_abs_expected",
        "e224_gate",
        "e224_score",
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
        "# E224 E211 Q3 Scale Pareto",
        "",
        "## Question",
        "",
        "Is E223's Q3 scale 0.75 the right risk point, or does a lower Q3 scale improve the JEPA tail tradeoff?",
        "",
        "## Graft vs Anchor",
        "",
        md_table(graft, cols, n=30),
        "",
        "## Actual vs E95",
        "",
        md_table(actual, cols, n=30),
        "",
        "## Pareto Front",
        "",
        md_table(pareto.sort_values("q3_scale"), cols, n=30),
        "",
        "## Target Breakdown",
        "",
        md_table(target, target_cols, n=50),
        "",
        "## Selected",
        "",
        md_table(selected, cols, n=8),
        "",
        "## Decision",
        "",
    ]
    if selected.empty:
        lines.append("- No lower-Q3 candidate passed E224. Keep E223 as the current risk-rebalanced sensor.")
    else:
        best = selected.iloc[0]
        lines.append(
            f"- Best E224 candidate: `{best['submission_file']}`. It uses Q3 scale `{best['q3_scale']}` with S4 `{best['s4_mode']}` on `{best['anchor']}`."
        )
        lines.append(
            "- E224 chooses a lower-Q3 Pareto point only if it keeps local/geometry support while reducing adverse capacity and Q3 top-cell concentration."
        )
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train_raw, sub_raw, train_feat, sub_feat = e209.read_frames()
    y = train_raw[TARGETS].to_numpy(dtype=int)
    groups = train_raw["subject_id"].astype(str).to_numpy()
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    if not sub_feat[e209.SUB_KEY].astype(str).equals(sample[KEYS].astype(str)):
        raise RuntimeError("submission feature order differs from sample order")

    priors = e162.prior_arrays(sample)
    stage2_oof = clip_prob(np.load(OUT / STAGE2_OOF))
    stage2_sub = load_prob(STAGE2_FILE, sample)
    e95 = load_prob(E95_FILE, sample)
    anchors = {"e95": e95, "e154": load_prob(E154_FILE, sample)}
    ops = e209.combo_defs()[COMBO]
    ungated_oof = e209.apply_ops_oof(train_feat, stage2_oof, ops)
    ungated_sub = e209.apply_ops_fit_predict(train_feat, sub_feat, stage2_oof, stage2_sub, ops)
    dep_oof = e210.oof_dependency(stage2_oof, y, groups)

    q3_scales = [0.0, 0.25, 0.50, 0.625, 0.75, 0.875, 1.0]
    s4_modes = ["closer", "toward"]
    anchor_scale = 0.5

    local_rows: list[dict[str, Any]] = []
    local_target_rows: list[dict[str, Any]] = []
    geometry_parts: list[pd.DataFrame] = []
    pred_oof_cache: dict[tuple[float, str], np.ndarray] = {}
    for q3_scale in q3_scales:
        for s4_mode in s4_modes:
            rec, geo, pred_oof = local_summary(
                train_raw, sub_raw, train_feat, stage2_oof, ungated_oof, dep_oof, ops, q3_scale, s4_mode
            )
            local_rows.append(rec)
            geometry_parts.append(geo.assign(q3_scale=q3_scale, s4_mode=s4_mode))
            local_target_rows.extend(target_rows(y, stage2_oof, pred_oof, {"q3_scale": q3_scale, "s4_mode": s4_mode}))
            pred_oof_cache[(q3_scale, s4_mode)] = pred_oof

    local = pd.DataFrame(local_rows)
    summary_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    pred_cache: dict[str, np.ndarray] = {}
    for local_rec in local.to_dict("records"):
        q3_scale = float(local_rec["q3_scale"])
        s4_mode = str(local_rec["s4_mode"])
        for anchor_name, anchor in anchors.items():
            candidate_id = f"e224_q3s{scale_tag(q3_scale)}_s4{s4_mode}_{anchor_name}_a0p5"
            pred = make_sub_prediction(anchor, stage2_sub, ungated_sub, stage2_oof, y, q3_scale, s4_mode, anchor_scale)
            pred_cache[candidate_id] = pred
            params = {
                **local_rec,
                "candidate_id": candidate_id,
                "anchor": anchor_name,
                "anchor_scale": anchor_scale,
            }
            rows, target = audit_pred(
                sample,
                priors,
                e95,
                pred,
                anchor,
                E95_FILE if anchor_name == "e95" else E154_FILE,
                params,
            )
            summary_rows.extend(rows)
            if not target.empty:
                target_parts.append(target)

    summary = pd.DataFrame(summary_rows)
    target_df = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    target_df = e222.add_ranking(target_df)
    summary = add_scores(summary, target_df)
    graft = summary[summary["pair_kind"].eq("graft_vs_anchor")].copy()
    pareto = pareto_front(graft)
    selected = graft[graft["e224_gate"]].sort_values(["e224_score", "expected_focus"], ascending=[False, True]).head(4).copy()
    files: list[str] = []
    for row in selected.itertuples(index=False):
        files.append(materialize(sample, pred_cache[str(row.candidate_id)], str(row.candidate_id)))
    if not selected.empty:
        selected["submission_file"] = files
        summary = summary.merge(
            selected[["candidate_id", "submission_file"]],
            on="candidate_id",
            how="left",
        )
        pareto = pareto.merge(selected[["candidate_id", "submission_file"]], on="candidate_id", how="left")
    else:
        summary["submission_file"] = ""
        selected["submission_file"] = ""
        pareto["submission_file"] = ""

    geometry = pd.concat(geometry_parts, ignore_index=True)
    summary.to_csv(SUMMARY_OUT, index=False)
    target_df.to_csv(TARGET_OUT, index=False)
    geometry.to_csv(GEOMETRY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, target_df, selected, pareto)

    print("[E224 selected]")
    cols = [
        "candidate_id",
        "q3_scale",
        "s4_mode",
        "anchor",
        "local_delta",
        "geometry_delta",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "q3_top1_over_abs_expected",
        "e224_gate",
        "e224_score",
        "submission_file",
    ]
    print(selected[cols].round(9).to_string(index=False) if not selected.empty else "none")
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
