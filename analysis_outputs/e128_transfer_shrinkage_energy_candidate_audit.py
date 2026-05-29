#!/usr/bin/env python3
"""E128 candidate audit using transfer-shrinkage energy.

SAUNA question:
E127 found that E101-compatible budget is visible as tail-neutral / low-alpha
density, but not strong enough as a direct metadata gate. This script asks
whether that energy is at least useful for explaining known public anchors and
triaging live candidates.

No submission is generated.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e96_public_miss_budget_tail_scenarios as e96  # noqa: E402
from public_anchor_bottleneck_decomposition import TARGETS, load_sub, logit  # noqa: E402


CELL_IN = OUT / "e127_transfer_shrinkage_cell_summary.csv"
SCORES_OUT = OUT / "e128_transfer_shrinkage_energy_scores_summary.csv"
METRIC_OUT = OUT / "e128_transfer_shrinkage_metric_public_summary.csv"
REPORT_OUT = OUT / "e128_transfer_shrinkage_energy_candidate_audit_report.md"

FILES: dict[str, str] = {
    "e95": "submission_e95_hardtail_541e3973.csv",
    "e101": "submission_e101_q2s3tail_177569bc.csv",
    "mixmin": "submission_mixmin_0c916bb4.csv",
    "failed_e72": "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "a2c8": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "raw_timeline": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "stage2": "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "ordinal": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "final9": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "q2_bad": "submission_jepa_latent_q2_w0p45.csv",
    "lejepa_bad": "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "resid_bad": "submission_jepa_latent_residual_probe.csv",
    "e85": "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86": "submission_e86_e85_consensus_a3f7c96f.csv",
    "e89": "submission_e89_e72decontam_00d7807f.csv",
    "e90": "submission_e90_e72pareto_28925de5.csv",
    "noq2": "submission_e87_noq2_source_consensus_a85c4e39.csv",
}

PUBLIC_LB: dict[str, float] = {
    "e95": 0.5762913298,
    "e101": 0.5763003660,
    "mixmin": 0.5763066405,
    "failed_e72": 0.5764077772,
    "a2c8": 0.5774393210,
    "raw_timeline": 0.5775263072,
    "stage2": 0.5779449757,
    "ordinal": 0.5783033652,
    "final9": 0.5784273528,
    "q2_bad": 0.5798012862,
    "lejepa_bad": 0.5802468192,
    "resid_bad": 0.5812273278,
}

LIVE_NAMES = ["e85", "e86", "e89", "e90", "noq2"]
REFERENCE_NAMES = ["e95", "e101", "mixmin", "failed_e72", "a2c8", "raw_timeline", "stage2", "ordinal", "final9", "q2_bad", "lejepa_bad", "resid_bad"]


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.where(np.isfinite(arr), np.maximum(arr, 0.0), 0.0)
    total = float(arr.sum())
    if total <= 0:
        return np.ones_like(arr) / len(arr)
    return arr / total


def weighted_cosine(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    num = float(np.sum(ww * a * b))
    den = float(np.sqrt(np.sum(ww * a * a) * np.sum(ww * b * b)))
    if den <= 1.0e-15:
        return 0.0
    return num / den


def weighted_projection(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    den = float(np.sum(ww * b * b))
    if den <= 1.0e-15:
        return np.nan
    return float(np.sum(ww * a * b) / den)


def weighted_l1(a: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    return float(np.sum(ww * np.abs(a)))


def weighted_rmse(a: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    return float(np.sqrt(np.sum(ww * a * a)))


def weighted_resid_ratio(a: np.ndarray, b: np.ndarray, w: np.ndarray) -> float:
    ww = normalize(w)
    den = float(np.sqrt(np.sum(ww * b * b)))
    if den <= 1.0e-15:
        return np.nan
    return float(np.sqrt(np.sum(ww * (a - b) ** 2)) / den)


def safe_corr(a: pd.Series, b: pd.Series, method: str = "spearman") -> float:
    valid = a.notna() & b.notna()
    if int(valid.sum()) < 3:
        return np.nan
    return float(a[valid].corr(b[valid], method=method))


def load_available_predictions() -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    sample = load_sub(FILES["mixmin"])
    preds: dict[str, np.ndarray] = {}
    for name, file_name in FILES.items():
        try:
            preds[name] = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        except FileNotFoundError:
            continue
    return sample, preds


def candidate_scores() -> pd.DataFrame:
    cell = pd.read_csv(CELL_IN)
    _, preds = load_available_predictions()
    lm = {name: logit(prob).reshape(-1) for name, prob in preds.items()}

    law = lm["e95"] - lm["mixmin"]
    e101_delta = lm["e101"] - lm["e95"]
    failed_e72_delta = lm["failed_e72"] - lm["mixmin"]

    weights = {
        "tail_equal": cell["broad_tail_equal_share"].to_numpy(dtype=np.float64),
        "low_alpha": cell["broad_low_alpha_share"].to_numpy(dtype=np.float64),
        "e101_plausible": cell["e101_plausible_share"].to_numpy(dtype=np.float64),
        "broad": cell["broad_share"].to_numpy(dtype=np.float64),
        "q2s3": cell["target_is_q2s3"].astype(float).to_numpy(dtype=np.float64),
        "e101_active": cell["e101_active"].astype(float).to_numpy(dtype=np.float64),
        "e72_pos": cell["e72_pos"].to_numpy(dtype=np.float64),
    }

    wrong_is_zero = failed_e72_delta > 1.0e-9
    wrong_is_one = failed_e72_delta < -1.0e-9
    base = preds["mixmin"]

    rows: list[dict[str, Any]] = []
    for name in [n for n in FILES if n in lm]:
        move_mix = lm[name] - lm["mixmin"]
        move_e95 = lm[name] - lm["e95"]
        move_e101 = lm[name] - lm["e101"]
        adverse = e96.adverse_delta_for_e72_direction(preds[name], base, wrong_is_zero.reshape(base.shape), wrong_is_one.reshape(base.shape)).reshape(-1)
        pos_adverse = np.maximum(adverse, 0.0)

        row: dict[str, Any] = {
            "name": name,
            "file": FILES[name],
            "role": "known_public" if name in PUBLIC_LB else "live_candidate",
            "public_lb": PUBLIC_LB.get(name, np.nan),
            "public_delta_vs_e95": PUBLIC_LB.get(name, np.nan) - PUBLIC_LB["e95"] if name in PUBLIC_LB else np.nan,
            "mean_abs_logit_move_vs_mixmin": float(np.mean(np.abs(move_mix))),
            "mean_abs_logit_move_vs_e95": float(np.mean(np.abs(move_e95))),
            "changed_cells_vs_e95": int(np.sum(np.abs(move_e95) > 1.0e-9)),
            "changed_cells_vs_mixmin": int(np.sum(np.abs(move_mix) > 1.0e-9)),
            "e72_adverse_exposure_mean": float(np.mean(pos_adverse)),
            "e72_adverse_exposure_tail_equal": weighted_l1(pos_adverse, weights["tail_equal"]),
            "e72_adverse_exposure_e101_plausible": weighted_l1(pos_adverse, weights["e101_plausible"]),
        }
        for wname, w in weights.items():
            row[f"{wname}_law_cosine"] = weighted_cosine(move_mix, law, w)
            row[f"{wname}_law_projection"] = weighted_projection(move_mix, law, w)
            row[f"{wname}_law_resid_ratio"] = weighted_resid_ratio(move_mix, law, w)
            row[f"{wname}_delta95_l1"] = weighted_l1(move_e95, w)
            row[f"{wname}_delta101_l1"] = weighted_l1(move_e101, w)
            row[f"{wname}_move_mix_rmse"] = weighted_rmse(move_mix, w)
        row["active_rollback_per_tail_equal_l1"] = row["e101_active_delta95_l1"] / max(row["tail_equal_delta95_l1"], 1.0e-12)
        row["tail_equal_preservation_score"] = row["tail_equal_law_cosine"] - row["tail_equal_law_resid_ratio"]
        row["transfer_shrinkage_risk_index"] = (
            row["e101_active_delta95_l1"]
            + row["q2s3_delta95_l1"]
            + 0.5 * row["e72_adverse_exposure_e101_plausible"]
            - row["tail_equal_law_cosine"]
        )
        rows.append(row)
    return pd.DataFrame(rows)


def metric_public_summary(scores: pd.DataFrame) -> pd.DataFrame:
    known = scores[scores["public_delta_vs_e95"].notna()].copy()
    metric_cols = [
        c
        for c in scores.columns
        if c
        not in {
            "name",
            "file",
            "role",
            "public_lb",
            "public_delta_vs_e95",
        }
        and pd.api.types.is_numeric_dtype(scores[c])
    ]
    rows: list[dict[str, Any]] = []
    for col in metric_cols:
        rows.append(
            {
                "metric": col,
                "spearman_public_delta": safe_corr(known[col], known["public_delta_vs_e95"], "spearman"),
                "pearson_public_delta": safe_corr(known[col], known["public_delta_vs_e95"], "pearson"),
                "known_min": float(known[col].min()),
                "known_max": float(known[col].max()),
                "e95_value": float(scores.loc[scores["name"].eq("e95"), col].iloc[0]),
                "e101_value": float(scores.loc[scores["name"].eq("e101"), col].iloc[0]),
                "mixmin_value": float(scores.loc[scores["name"].eq("mixmin"), col].iloc[0]),
                "failed_e72_value": float(scores.loc[scores["name"].eq("failed_e72"), col].iloc[0]),
            }
        )
    out = pd.DataFrame(rows)
    out["abs_spearman"] = out["spearman_public_delta"].abs()
    return out.sort_values(["abs_spearman", "spearman_public_delta"], ascending=[False, True]).drop(columns=["abs_spearman"])


def write_report(scores: pd.DataFrame, metrics: pd.DataFrame) -> None:
    cols = [
        "name",
        "role",
        "public_delta_vs_e95",
        "tail_equal_law_cosine",
        "tail_equal_law_projection",
        "tail_equal_law_resid_ratio",
        "e101_active_delta95_l1",
        "q2s3_delta95_l1",
        "e72_adverse_exposure_e101_plausible",
        "transfer_shrinkage_risk_index",
    ]
    known_view = scores[scores["name"].isin(REFERENCE_NAMES)].copy()
    live_view = scores[scores["name"].isin(LIVE_NAMES)].copy().sort_values("transfer_shrinkage_risk_index")
    key_metrics = metrics[
        metrics["metric"].isin(
            [
                "tail_equal_law_cosine",
                "tail_equal_law_projection",
                "tail_equal_law_resid_ratio",
                "e101_active_delta95_l1",
                "q2s3_delta95_l1",
                "e72_adverse_exposure_e101_plausible",
                "transfer_shrinkage_risk_index",
            ]
        )
    ]
    e95 = scores[scores["name"].eq("e95")].iloc[0]
    e101 = scores[scores["name"].eq("e101")].iloc[0]
    mixmin = scores[scores["name"].eq("mixmin")].iloc[0]
    best_live = live_view.iloc[0] if not live_view.empty else None

    live_sentence = "No live candidates were available."
    if best_live is not None:
        live_sentence = (
            f"Lowest-risk live candidate by this index is `{best_live['name']}`, "
            f"but it remains a diagnostic ranking, not a submit gate."
        )

    report = f"""# E128 Transfer-shrinkage energy candidate audit

## Question

E127 showed that tail-neutral / low-alpha density predicts the E101-compatible
cell budget. E128 asks whether that energy explains known public anchors and
usefully triages live candidates.

## Known Public Anchors

{md_table(known_view[cols].sort_values('public_delta_vs_e95'), '.6f')}

## Live Candidate Triage

{md_table(live_view[cols], '.6f')}

## Public Correlation of Key Metrics

{md_table(key_metrics[[
    'metric',
    'spearman_public_delta',
    'pearson_public_delta',
    'e95_value',
    'e101_value',
    'mixmin_value',
    'failed_e72_value',
]], '.6f')}

## Interpretation

- E95 has tail-equal law cosine `{float(e95['tail_equal_law_cosine']):.6f}` by construction; mixmin is `{float(mixmin['tail_equal_law_cosine']):.6f}` because it has no E95 law movement.
- E101 preserves the E95 law on tail-neutral cells but pays active rollback: E101-active delta95 L1 `{float(e101['e101_active_delta95_l1']):.6f}`.
- The energy is useful as a veto/diagnostic: it separates E101's active rollback from E95 and keeps q2s3/active movement explicit.
- The energy is not sufficient as a public selector: known-public correlations are not enough to rank all bad anchors, and live candidates still require the E124/E126 public-world stress.

{live_sentence}

## Decision

No submission. Transfer-shrinkage energy is promoted to a candidate-risk
component, not a standalone ranker. A future candidate must satisfy this energy
plus E124/E126 stress and must show selector-scale expected movement.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    scores = candidate_scores()
    metrics = metric_public_summary(scores)
    scores.to_csv(SCORES_OUT, index=False)
    metrics.to_csv(METRIC_OUT, index=False)
    write_report(scores, metrics)

    print("Wrote:")
    for path in [SCORES_OUT, METRIC_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print("\nKnown anchors:")
    print(
        scores[scores["name"].isin(REFERENCE_NAMES)][
            [
                "name",
                "public_delta_vs_e95",
                "tail_equal_law_cosine",
                "e101_active_delta95_l1",
                "q2s3_delta95_l1",
                "transfer_shrinkage_risk_index",
            ]
        ].sort_values("public_delta_vs_e95").to_string(index=False)
    )
    print("\nLive:")
    print(
        scores[scores["name"].isin(LIVE_NAMES)][
            [
                "name",
                "tail_equal_law_cosine",
                "e101_active_delta95_l1",
                "q2s3_delta95_l1",
                "transfer_shrinkage_risk_index",
            ]
        ].sort_values("transfer_shrinkage_risk_index").to_string(index=False)
    )


if __name__ == "__main__":
    main()
