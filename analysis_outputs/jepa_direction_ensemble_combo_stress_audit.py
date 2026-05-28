from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import public_lb_actual_anchor_ranker as ranker  # noqa: E402
from public_subset_sensitivity_audit import ce_matrix  # noqa: E402


DETAIL_OUT = OUT / "jepa_direction_ensemble_combo_stress_detail.csv"
SUMMARY_OUT = OUT / "jepa_direction_ensemble_combo_stress_summary.csv"
PAIRWISE_OUT = OUT / "jepa_direction_ensemble_combo_stress_pairwise.csv"
REPORT_OUT = OUT / "jepa_direction_ensemble_combo_stress_report.md"


CANDIDATES = {
    "a2c8": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "raw05": "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
    "b01_ladder": "submission_sparseladder_b01acaa1.csv",
    "898_ladder": "submission_sparseladder_89817541.csv",
    "f1ee_noq2": "submission_sparseladder_f1ee16b0.csv",
    "blockorth_3a28": "submission_blockorth_3a28f87f.csv",
    "target_q3stage": "submission_targetabl_b19056bb.csv",
    "direns_2a96": "submission_direns_2a96ae73.csv",
    "direns_1e0f": "submission_direns_1e0f159d.csv",
    "direns_81cc": "submission_direns_81cca594.csv",
    "direns_c0fd": "submission_direns_c0fdb76b.csv",
    "direns_24a9": "submission_direns_24a92ca1.csv",
    "direns_c4af": "submission_direns_c4af1fd8.csv",
    "direns_652c": "submission_direns_652cd2ca.csv",
    "direns_b096_orth": "submission_direns_b0962ff8.csv",
}

BASELINES = {
    "a2c8": "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "b01_ladder": "submission_sparseladder_b01acaa1.csv",
    "898_ladder": "submission_sparseladder_89817541.csv",
    "blockorth_3a28": "submission_blockorth_3a28f87f.csv",
}


def load_sample() -> pd.DataFrame:
    return pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=ranker.KEY[1:]).sort_values(ranker.KEY).reset_index(drop=True)


def candidate_frame() -> pd.DataFrame:
    rows = []
    for name, file_name in CANDIDATES.items():
        if ranker.exists(file_name):
            rows.append({"candidate": name, "file": file_name})
    return pd.DataFrame(rows)


def score_candidates(sample: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    masks = ranker.mask_matrix(sample)
    stage2 = ranker.load_submission("submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", sample)
    pred_cache = {
        str(row.candidate): ranker.load_submission(str(row.file), sample)
        for row in candidates.itertuples(index=False)
    }
    scenario_cache: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []

    for combo_set, table_name in ranker.COMBO_TABLES.items():
        table_path = OUT / table_name
        if not table_path.exists():
            continue
        table = pd.read_csv(table_path).head(160).reset_index(drop=True)
        weights = ranker.combo_weights(table)
        for i, combo in table.iterrows():
            scenario = str(combo["scenario_file"])
            if scenario not in scenario_cache:
                scenario_cache[scenario] = ranker.load_submission(scenario, sample)
            q = scenario_cache[scenario]
            mask_vec = masks[int(combo["mask_index"])]
            stage_loss = float(mask_vec @ ce_matrix(q, stage2).mean(axis=1))
            for candidate, pred in pred_cache.items():
                loss = float(mask_vec @ ce_matrix(q, pred).mean(axis=1))
                rows.append(
                    {
                        "candidate": candidate,
                        "file": candidates.loc[candidates["candidate"].eq(candidate), "file"].iloc[0],
                        "combo_set": combo_set,
                        "combo_rank": i + 1,
                        "combo_weight": float(weights[i]),
                        "scenario_file": scenario,
                        "mask_index": int(combo["mask_index"]),
                        "mask_kind": str(combo.get("mask_kind", "")),
                        "mask_name": str(combo.get("mask_name", "")),
                        "rows": int(combo.get("rows", 0)),
                        "anchored_score": float(ranker.STAGE2_LB + loss - stage_loss),
                    }
                )
    detail = pd.DataFrame(rows)

    for base_name in BASELINES:
        base = detail[detail["candidate"].eq(base_name)][
            ["combo_set", "combo_rank", "anchored_score"]
        ].rename(columns={"anchored_score": f"score_{base_name}"})
        detail = detail.merge(base, on=["combo_set", "combo_rank"], how="left")
        detail[f"delta_vs_{base_name}"] = detail["anchored_score"] - detail[f"score_{base_name}"]
        detail[f"win_vs_{base_name}"] = detail[f"delta_vs_{base_name}"] < 0.0
    return detail


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    order = np.argsort(values)
    values = values[order]
    weights = weights[order]
    cdf = np.cumsum(weights) / np.sum(weights)
    return float(np.interp(q, cdf, values))


def summarize(detail: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for candidate, group in detail.groupby("candidate", sort=False):
        weights = group["combo_weight"].to_numpy(dtype=float)
        weights = weights / weights.sum()
        score = group["anchored_score"].to_numpy(dtype=float)
        rec: dict[str, object] = {
            "candidate": candidate,
            "file": str(group["file"].iloc[0]),
            "weighted_mean_score": float(weights @ score),
            "mean_score": float(np.mean(score)),
            "p10_score": weighted_quantile(score, weights, 0.10),
            "p50_score": weighted_quantile(score, weights, 0.50),
            "p90_score": weighted_quantile(score, weights, 0.90),
            "worst_score": float(np.max(score)),
        }
        for base_name in BASELINES:
            delta = group[f"delta_vs_{base_name}"].to_numpy(dtype=float)
            rec[f"weighted_delta_vs_{base_name}"] = float(weights @ delta)
            rec[f"win_rate_vs_{base_name}"] = float(np.mean(delta < 0.0))
            rec[f"weighted_win_rate_vs_{base_name}"] = float(weights @ (delta < 0.0).astype(float))
            rec[f"p10_delta_vs_{base_name}"] = weighted_quantile(delta, weights, 0.10)
            rec[f"p50_delta_vs_{base_name}"] = weighted_quantile(delta, weights, 0.50)
            rec[f"p90_delta_vs_{base_name}"] = weighted_quantile(delta, weights, 0.90)
            rec[f"worst_delta_vs_{base_name}"] = float(np.max(delta))
        rows.append(rec)
    summary = pd.DataFrame(rows)
    return summary.sort_values(["weighted_delta_vs_b01_ladder", "weighted_mean_score"]).reset_index(drop=True)


def pairwise_by_set(detail: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (candidate, combo_set), group in detail.groupby(["candidate", "combo_set"], sort=False):
        weights = group["combo_weight"].to_numpy(dtype=float)
        weights = weights / weights.sum()
        rec: dict[str, object] = {
            "candidate": candidate,
            "file": str(group["file"].iloc[0]),
            "combo_set": combo_set,
            "weighted_mean_score": float(weights @ group["anchored_score"].to_numpy(dtype=float)),
        }
        for base_name in BASELINES:
            delta = group[f"delta_vs_{base_name}"].to_numpy(dtype=float)
            rec[f"weighted_delta_vs_{base_name}"] = float(weights @ delta)
            rec[f"weighted_win_rate_vs_{base_name}"] = float(weights @ (delta < 0.0).astype(float))
            rec[f"worst_delta_vs_{base_name}"] = float(np.max(delta))
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["candidate", "combo_set"]).reset_index(drop=True)


def write_report(summary: pd.DataFrame, pairwise: pd.DataFrame) -> None:
    cols = [
        "candidate",
        "file",
        "weighted_mean_score",
        "weighted_delta_vs_b01_ladder",
        "weighted_win_rate_vs_b01_ladder",
        "p50_delta_vs_b01_ladder",
        "p90_delta_vs_b01_ladder",
        "worst_delta_vs_b01_ladder",
        "weighted_delta_vs_898_ladder",
        "weighted_win_rate_vs_898_ladder",
        "weighted_delta_vs_a2c8",
    ]
    set_cols = [
        "candidate",
        "combo_set",
        "weighted_delta_vs_b01_ladder",
        "weighted_win_rate_vs_b01_ladder",
        "worst_delta_vs_b01_ladder",
        "weighted_delta_vs_898_ladder",
    ]
    lines = [
        "# JEPA Direction Ensemble Combo Stress Audit",
        "",
        "This scores the new direction-ensemble candidates on every inverse public scenario/mask combo instead of trusting only the averaged actual-anchor score.",
        "",
        "## Overall Pairwise Summary",
        "",
        "```",
        summary[[c for c in cols if c in summary.columns]].round(10).to_string(index=False),
        "```",
        "",
        "## Per-Combo-Set Pairwise Summary",
        "",
        "```",
        pairwise[pairwise["candidate"].isin(summary["candidate"].head(10))][[c for c in set_cols if c in pairwise.columns]].round(10).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- A robust replacement for `b01_ladder` should have negative weighted delta, high weighted win rate, and non-positive or small p90/worst deltas versus `b01_ladder`.",
        "- If a candidate improves only the weighted mean but loses many combo rows, it is likely another inverse-scenario averaging artifact.",
        "- `898_ladder` remains the scale-stress reference; candidates that beat `b01_ladder` but lose badly to `898_ladder` are safer but lower-upside probes.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    candidates = candidate_frame()
    detail = score_candidates(sample, candidates)
    summary = summarize(detail, candidates)
    pairwise = pairwise_by_set(detail)
    detail.to_csv(DETAIL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    pairwise.to_csv(PAIRWISE_OUT, index=False)
    write_report(summary, pairwise)

    print(REPORT_OUT)
    print("[summary]")
    cols = [
        "candidate",
        "file",
        "weighted_delta_vs_b01_ladder",
        "weighted_win_rate_vs_b01_ladder",
        "p50_delta_vs_b01_ladder",
        "p90_delta_vs_b01_ladder",
        "worst_delta_vs_b01_ladder",
        "weighted_delta_vs_898_ladder",
        "weighted_delta_vs_a2c8",
    ]
    print(summary[cols].round(10).to_string(index=False))


if __name__ == "__main__":
    main()
