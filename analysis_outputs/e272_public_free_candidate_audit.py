#!/usr/bin/env python3
"""E272: public-free candidate promotion audit.

The public LB cannot be used as an iteration loop. This script treats known
public scores only as old observations for stress calibration, then audits
new candidates against the current public anchor E247.

It does not claim a true LB forecast. It answers a narrower question:
"Is this candidate strong and distinct enough to deserve a scarce public
submission slot?"
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    feature_row,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
from public_pairwise_order_selector import (  # noqa: E402
    ALPHAS,
    FEATURE_SETS,
    eval_fit_on_pairs,
    fit_pairwise,
    predict_diff,
    sign_accuracy,
)


CURRENT = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
KNOWN_FAILS = [
    "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
    "submission_e267_humansocial_tail_balanced_2936100f.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_e176_abl_q2_to0p75_91e49725.csv",
    "submission_e101_q2s3tail_177569bc.csv",
    "submission_e95_hardtail_541e3973.csv",
    "submission_mixmin_0c916bb4.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
]

REPORT_OUT = OUT / "e272_public_free_candidate_audit_report.md"
MODEL_OUT = OUT / "e272_public_free_candidate_audit_models.csv"
SCORE_OUT = OUT / "e272_public_free_candidate_audit_scores.csv"
ANATOMY_OUT = OUT / "e272_public_free_candidate_audit_anatomy.csv"


def locate(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in [OUT, JEPA]:
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    return None


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def load_prob_vec(file_name: str | Path, sample: pd.DataFrame) -> np.ndarray:
    return logit(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)).reshape(-1)


def candidate_files() -> list[str]:
    files = [
        CURRENT,
        "submission_e269_combo_phonebed8_anti4_small_b27a2e23.csv",
        "submission_e269_anti_e256_tophalf_beta035_4e910856.csv",
        "submission_e269_e247only_all_amp006_control_2cef7c9d.csv",
        "submission_e271_cashflow_top8_anti4_tiny_ccd08be8.csv",
        "submission_e271_cashflow_top8_amp010_170ae6b0.csv",
        "submission_e271_cashflow_top6_amp014_ecc2b44c.csv",
        "submission_e271_cashflow_top6_anti_pay15_c12a8485.csv",
        "submission_e271_pay25_pre3_only_amp016_62659ed5.csv",
        "submission_e271_calendar_only_control_top8_36405aed.csv",
        "submission_e267_humansocial_tail_balanced_2936100f.csv",
        "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
        "submission_e95_hardtail_541e3973.csv",
        "submission_mixmin_0c916bb4.csv",
    ]
    out: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        path = locate(file_name)
        if path is None:
            continue
        key = rel(path)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def current_order_flags(fit, known: pd.DataFrame, features: list[str]) -> dict[str, object]:
    files = known["file"].astype(str).tolist()
    current_pos = files.index(CURRENT)
    x = known[features].to_numpy(dtype=np.float64)
    deltas = predict_diff(fit, x - x[current_pos])
    series = pd.Series(deltas, index=files)
    non_current = series.drop(CURRENT)
    top_file = str(series.sort_values().index[0])
    known_lb = known.set_index("file")["public_lb"]
    sign_ok = []
    for file_name, pred_delta in non_current.items():
        actual_delta = float(known_lb[file_name] - known_lb[CURRENT])
        if abs(actual_delta) < 1e-15 or abs(pred_delta) < 1e-15:
            continue
        sign_ok.append(float(pred_delta * actual_delta > 0.0))
    return {
        "top1_is_current": bool(top_file == CURRENT),
        "pred_top_file": top_file,
        "non_current_pred_worse_rate": float((non_current > 0.0).mean()),
        "current_pair_sign_acc": float(np.mean(sign_ok)) if sign_ok else np.nan,
        "min_non_current_delta": float(non_current.min()),
        "max_non_current_delta": float(non_current.max()),
    }


def evaluate_models(known: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    n = len(known)
    all_pairs = list(combinations(range(n), 2))
    for feature_name, features in FEATURE_SETS:
        if any(col not in known.columns for col in features):
            continue
        for alpha in ALPHAS:
            model_name = f"{feature_name}_a{alpha:g}"
            full_fit = fit_pairwise(known, model_name, features, alpha)
            if full_fit is None:
                continue
            ins_pred, ins_actual = eval_fit_on_pairs(full_fit, known, all_pairs)

            loo_pred: list[float] = []
            loo_actual: list[float] = []
            for heldout in range(n):
                fit = fit_pairwise(known, model_name, features, alpha, {heldout})
                if fit is None:
                    continue
                pairs = [(heldout, other) for other in range(n) if other != heldout]
                pred, actual = eval_fit_on_pairs(fit, known, pairs)
                loo_pred.extend(pred.tolist())
                loo_actual.extend(actual.tolist())

            l2o_pred: list[float] = []
            l2o_actual: list[float] = []
            for i, j in all_pairs:
                fit = fit_pairwise(known, model_name, features, alpha, {i, j})
                if fit is None:
                    continue
                pred, actual = eval_fit_on_pairs(fit, known, [(i, j)])
                l2o_pred.extend(pred.tolist())
                l2o_actual.extend(actual.tolist())

            loo_pred_arr = np.asarray(loo_pred, dtype=np.float64)
            loo_actual_arr = np.asarray(loo_actual, dtype=np.float64)
            l2o_pred_arr = np.asarray(l2o_pred, dtype=np.float64)
            l2o_actual_arr = np.asarray(l2o_actual, dtype=np.float64)
            flags = current_order_flags(full_fit, known, features)

            loo_err = loo_pred_arr - loo_actual_arr
            l2o_err = l2o_pred_arr - l2o_actual_arr
            ins_err = ins_pred - ins_actual
            current_order_pass = bool(
                flags["top1_is_current"]
                and flags["non_current_pred_worse_rate"] >= 0.75
                and flags["current_pair_sign_acc"] >= 0.75
            )
            reliability_score = (
                float(np.mean(np.abs(loo_err))) if len(loo_err) else 9.0
            ) + 0.75 * (float(np.mean(np.abs(l2o_err))) if len(l2o_err) else 9.0)
            reliability_score += 0.00025 * (1.0 - sign_accuracy(loo_pred_arr, loo_actual_arr))
            reliability_score += 0.00020 * (1.0 - sign_accuracy(l2o_pred_arr, l2o_actual_arr))
            if not current_order_pass:
                reliability_score += 0.002

            rows.append(
                {
                    "model": model_name,
                    "feature_set": feature_name,
                    "features": ",".join(features),
                    "alpha": alpha,
                    "n_features": len(features),
                    "insample_mae": float(np.mean(np.abs(ins_err))),
                    "insample_sign_acc": sign_accuracy(ins_pred, ins_actual),
                    "loo_mae": float(np.mean(np.abs(loo_err))) if len(loo_err) else np.nan,
                    "loo_p90_abs_error": float(np.quantile(np.abs(loo_err), 0.90)) if len(loo_err) else np.nan,
                    "loo_sign_acc": sign_accuracy(loo_pred_arr, loo_actual_arr),
                    "l2o_mae": float(np.mean(np.abs(l2o_err))) if len(l2o_err) else np.nan,
                    "l2o_p90_abs_error": float(np.quantile(np.abs(l2o_err), 0.90)) if len(l2o_err) else np.nan,
                    "l2o_sign_acc": sign_accuracy(l2o_pred_arr, l2o_actual_arr),
                    "current_order_pass": current_order_pass,
                    "model_score": float(reliability_score),
                    **flags,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["current_order_pass", "model_score"],
        ascending=[False, True],
    ).reset_index(drop=True)


def selected_models(model_df: pd.DataFrame) -> pd.DataFrame:
    strict = model_df[
        model_df["current_order_pass"].astype(bool)
        & (model_df["loo_sign_acc"] >= 0.65)
        & (model_df["l2o_sign_acc"] >= 0.55)
    ].copy()
    if len(strict):
        return strict.head(12).reset_index(drop=True)
    return model_df.head(12).reset_index(drop=True)


def build_features(files: list[str], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for file_name in files:
        path = locate(file_name)
        if path is None:
            continue
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["basename"] = path.name
        row["source_path"] = rel(path)
        rows.append(row)
    return pd.DataFrame(rows)


def score_candidates(known: pd.DataFrame, candidates: pd.DataFrame, model_df: pd.DataFrame) -> pd.DataFrame:
    current_pos = known["file"].astype(str).tolist().index(CURRENT)
    selected = selected_models(model_df)
    scenario_cols: list[np.ndarray] = []
    scenario_meta: list[str] = []

    for _, model_rec in selected.iterrows():
        features = str(model_rec["features"]).split(",")
        alpha = float(model_rec["alpha"])
        model_name = str(model_rec["model"])
        known_x = known[features].to_numpy(dtype=np.float64)
        cand_x = candidates[features].to_numpy(dtype=np.float64)
        scenarios: list[tuple[str, set[int]]] = [("all", set())]
        scenarios.extend((f"loo_{i}", {i}) for i in range(len(known)))
        scenarios.extend((f"l2o_current_{i}", {current_pos, i}) for i in range(len(known)) if i != current_pos)
        for scenario_name, exclude in scenarios:
            fit = fit_pairwise(known, model_name, features, alpha, exclude)
            if fit is None:
                continue
            pred = predict_diff(fit, cand_x - known_x[current_pos])
            scenario_cols.append(pred)
            scenario_meta.append(f"{model_name}:{scenario_name}")

    mat = np.column_stack(scenario_cols)
    out = candidates.copy()
    out["current_anchor"] = CURRENT
    out["scenario_count"] = mat.shape[1]
    out["pred_delta_vs_current_mean"] = np.nanmean(mat, axis=1)
    out["pred_delta_vs_current_median"] = np.nanmedian(mat, axis=1)
    out["pred_delta_vs_current_p10"] = np.nanpercentile(mat, 10, axis=1)
    out["pred_delta_vs_current_p90"] = np.nanpercentile(mat, 90, axis=1)
    out["pred_delta_vs_current_min"] = np.nanmin(mat, axis=1)
    out["pred_delta_vs_current_max"] = np.nanmax(mat, axis=1)
    out["pred_delta_vs_current_spread"] = out["pred_delta_vs_current_max"] - out["pred_delta_vs_current_min"]
    out["pred_beats_current_rate"] = np.mean(mat < 0.0, axis=1)
    current_bad = float(out.loc[out["basename"].eq(CURRENT), "bad_axis_abs_load"].iloc[0])
    out["incremental_bad_axis_vs_current"] = out["bad_axis_abs_load"] - current_bad
    out["strict_promote_gate"] = (
        (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["pred_beats_current_rate"] >= 0.75)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
    )
    out["info_sensor_gate"] = (
        ~out["strict_promote_gate"]
        & (out["pred_delta_vs_current_mean"] < 0.0)
        & (out["pred_beats_current_rate"] >= 0.55)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.025)
    )
    out["below_resolution_gate"] = (
        (out["pred_delta_vs_current_p10"] <= 0.00005)
        & (out["pred_delta_vs_current_p90"] >= -0.00005)
    )
    out["block_gate"] = (
        (out["pred_delta_vs_current_mean"] > 0.00005)
        | (out["incremental_bad_axis_vs_current"].abs() > 0.05)
    )
    out["promotion_decision"] = np.select(
        [
            out["strict_promote_gate"],
            out["info_sensor_gate"] & ~out["below_resolution_gate"],
            out["info_sensor_gate"] & out["below_resolution_gate"],
            out["below_resolution_gate"],
            out["block_gate"],
        ],
        [
            "promote_candidate",
            "information_sensor_only",
            "too_small_to_submit",
            "below_selector_resolution",
            "block_or_reject",
        ],
        default="hold_for_more_local_evidence",
    )
    out.attrs["selected_models"] = selected
    out.attrs["scenario_meta"] = scenario_meta
    return out.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def movement_anatomy(files: list[str], sample: pd.DataFrame) -> pd.DataFrame:
    current = load_prob_vec(CURRENT, sample)
    fail_vecs: dict[str, np.ndarray] = {}
    fail_lbs = known_public_table().set_index("file")["public_lb"].to_dict()
    for name in KNOWN_FAILS:
        path = locate(name)
        if path is not None:
            fail_vecs[name] = load_prob_vec(name, sample) - current

    rows: list[dict[str, object]] = []
    current_prob = load_sub(CURRENT, sample)[TARGETS].to_numpy(dtype=np.float64)
    for file_name in files:
        path = locate(file_name)
        if path is None:
            continue
        pred = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        z = logit(pred).reshape(-1)
        move = z - current
        prob_delta = np.abs(pred - current_prob)
        rec: dict[str, object] = {
            "file": rel(path),
            "basename": path.name,
            "changed_cells_vs_current": int((np.abs(move) > 1.0e-12).sum()),
            "changed_rows_vs_current": int((prob_delta.max(axis=1) > 1.0e-12).sum()),
            "mean_abs_logit_delta_vs_current": float(np.mean(np.abs(move))),
            "l1_logit_delta_vs_current": float(np.sum(np.abs(move))),
            "max_abs_logit_delta_vs_current": float(np.max(np.abs(move))),
            "max_abs_prob_delta_vs_current": float(np.max(prob_delta)),
        }
        for target_i, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(pred[:, target_i] - current_prob[:, target_i]) > 1.0e-12).sum())
        for fail_name, fail_move in fail_vecs.items():
            denom = float(np.linalg.norm(move) * np.linalg.norm(fail_move) + 1.0e-12)
            rec[f"cos_delta_with_{Path(fail_name).stem}"] = float(np.dot(move, fail_move) / denom) if denom else 0.0
            rec[f"l1_ratio_to_{Path(fail_name).stem}"] = float(np.sum(np.abs(move)) / (np.sum(np.abs(fail_move)) + 1.0e-12))
            if fail_name in fail_lbs:
                rec[f"known_public_lb_{Path(fail_name).stem}"] = float(fail_lbs[fail_name])
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["l1_logit_delta_vs_current", "basename"]).reset_index(drop=True)


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


def write_report(model_df: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> None:
    selected = selected_models(model_df)
    strict_count = int(scores["strict_promote_gate"].sum())
    info_count = int(scores["info_sensor_gate"].sum())
    best = scores.iloc[0]
    e271 = scores[scores["basename"].eq("submission_e271_cashflow_top8_anti4_tiny_ccd08be8.csv")]
    e269 = scores[scores["basename"].eq("submission_e269_combo_phonebed8_anti4_small_b27a2e23.csv")]
    lines = [
        "# E272 Public-Free Candidate Audit",
        "",
        "## Question",
        "",
        "Can any social/cash-flow follow-up be promoted without spending another public LB test?",
        "",
        "## Promotion Rule",
        "",
        "A scarce public submission requires `strict_promote_gate`: p90 predicted delta vs current E247 < `-0.00005`, candidate beats current in at least `75%` of pairwise stress scenarios, and incremental bad-axis change versus E247 <= `0.015`.",
        "",
        "If a candidate is only mean-negative but its p10/p90 interval overlaps zero, it is an information sensor but not a submission-grade candidate.",
        "",
        "## Model Reliability",
        "",
        f"- known public anchors: `{len(known_public_table())}`",
        f"- selected local selector models: `{len(selected)}`",
        f"- selected model current-order pass rate: `{float(selected['current_order_pass'].mean()):.3f}`",
        f"- selected model median LOO sign accuracy: `{float(selected['loo_sign_acc'].median()):.3f}`",
        f"- selected model median L2O sign accuracy: `{float(selected['l2o_sign_acc'].median()):.3f}`",
        "",
        "## Candidate Decisions",
        "",
        f"- strict promote count: `{strict_count}`",
        f"- information-sensor count: `{info_count}`",
        f"- best local candidate by gate/sort: `{best['basename']}` -> `{best['promotion_decision']}`",
        "",
    ]
    if not e271.empty:
        row = e271.iloc[0]
        lines.extend([
            "## E271 Cash-Flow Read",
            "",
            f"- decision: `{row['promotion_decision']}`",
            f"- pred mean delta vs E247: `{float(row['pred_delta_vs_current_mean']):.9f}`",
            f"- pred p10/p90 delta vs E247: `{float(row['pred_delta_vs_current_p10']):.9f}` / `{float(row['pred_delta_vs_current_p90']):.9f}`",
            f"- beats-current scenario rate: `{float(row['pred_beats_current_rate']):.3f}`",
            "- interpretation: cash-flow is a plausible story diagnostic, but this candidate does not clear the public-free promotion bar unless the row above says `promote_candidate`.",
            "",
        ])
    if not e269.empty:
        row = e269.iloc[0]
        lines.extend([
            "## E269 Social Boundary Read",
            "",
            f"- decision: `{row['promotion_decision']}`",
            f"- pred mean delta vs E247: `{float(row['pred_delta_vs_current_mean']):.9f}`",
            f"- pred p10/p90 delta vs E247: `{float(row['pred_delta_vs_current_p10']):.9f}` / `{float(row['pred_delta_vs_current_p90']):.9f}`",
            f"- beats-current scenario rate: `{float(row['pred_beats_current_rate']):.3f}`",
            "",
        ])

    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "changed_rows_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
    ]
    e256_cos = "cos_delta_with_submission_e256_featnn1_top50_amp_then_smooth25_a3827329"
    e267_cos = "cos_delta_with_submission_e267_humansocial_tail_balanced_2936100f"
    for col in [e256_cos, e267_cos]:
        if col in anatomy.columns:
            anatomy_cols.append(col)
    lines.extend([
        "## Score Table",
        "",
        md_table(scores[score_cols], n=40),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[anatomy_cols], n=40),
        "",
        "## Decision",
        "",
        "Do not spend a public LB slot on any candidate unless it clears `strict_promote_gate` or unless the explicit goal is information gain, not score improvement.",
        "",
        "For the current social/cash-flow probes, the local bar is intentionally higher than before. A tiny boundary move can stay in the hypothesis graph, but it should not be called a score candidate when selector uncertainty is larger than the expected edge.",
        "",
        "## Files",
        "",
        f"- `{MODEL_OUT.name}`",
        f"- `{SCORE_OUT.name}`",
        f"- `{ANATOMY_OUT.name}`",
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current_path = locate(CURRENT)
    if current_path is None:
        raise FileNotFoundError(CURRENT)
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    if CURRENT not in set(known["file"].astype(str)):
        raise RuntimeError(f"{CURRENT} missing from known public table")

    files = candidate_files()
    candidates = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    anatomy = movement_anatomy(files, sample)

    model_df.to_csv(MODEL_OUT, index=False)
    scores.to_csv(SCORE_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    write_report(model_df, scores, anatomy)

    print(REPORT_OUT)
    print(scores[[
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "bad_axis_abs_load",
        "incremental_bad_axis_vs_current",
    ]].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
