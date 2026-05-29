#!/usr/bin/env python3
"""E98 E95-updated selector audit.

E95 is now a public-positive hard-tail localization anchor. This audit asks a
small falsifiable question: does adding E95 make the known-public movement
proxy usable at the next frontier scale, or does it still fail exactly where
the next E90/E86/E85 decision lives?
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import public_anchor_bottleneck_decomposition as pab  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


KNOWN_OUT = OUT / "e98_e95_updated_selector_known_loo.csv"
MODEL_OUT = OUT / "e98_e95_updated_selector_model_scores.csv"
CANDIDATE_OUT = OUT / "e98_e95_updated_selector_candidates.csv"
REPORT_OUT = OUT / "e98_e95_updated_selector_report.md"

E95_FILE = "submission_e95_hardtail_541e3973.csv"
MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"

POST_E95_CANDIDATES = [
    ("current_frontier", E95_FILE),
    ("previous_frontier", MIXMIN_FILE),
    ("failed_public_anchor", E72_FILE),
    ("conservative_floor", "submission_e85_inverse_conflict_pruned_58b23ed1.csv"),
    ("max_upside_consensus", "submission_e86_e85_consensus_a3f7c96f.csv"),
    ("no_q2_contrast", "submission_e87_noq2_source_consensus_a85c4e39.csv"),
    ("no_overstep_contrast", "submission_e87_q2_nooverstep_consensus_acd7add0.csv"),
    ("inverse_top_contrast", "submission_e87_inverse_top_prior_consensus_5445ec28.csv"),
    ("min_contamination_decontam", "submission_e89_e72decontam_00d7807f.csv"),
    ("pareto_row_decontam", "submission_e90_e72pareto_28925de5.csv"),
]


def ref_features(sample: pd.DataFrame) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    ref_files = {
        "stage2": pab.STAGE2,
        "raw05": pab.RAW05,
        "a2c8": pab.A2C8,
        "final9": pab.FINAL9,
        "ordinal": pab.ORDINAL,
        "q2_bad": pab.Q2_BAD,
        "resid_bad": pab.RESID_BAD,
        "lejepa_bad": pab.LEJEPA_BAD,
    }
    refs = {name: pab.prob_matrix(file_name, sample) for name, file_name in ref_files.items()}
    ref_vecs = {name: pab.vec(prob) for name, prob in refs.items()}
    return refs, ref_vecs


def known_feature_table(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    ref_vecs: dict[str, np.ndarray],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for rec in pab.known_public_table().to_dict("records"):
        row = pab.feature_row(str(rec["file"]), sample, refs, ref_vecs)
        row.update(rec)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)


def loo_detail(known: pd.DataFrame, models: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    y = known["public_lb"].to_numpy(dtype=np.float64)
    for _, model in models.iterrows():
        name = str(model["model"])
        if str(model["kind"]) == "baseline":
            pred = np.full(len(known), np.median(y), dtype=np.float64)
        else:
            features = [x for x in str(model["features"]).split(",") if x]
            pred = pab.loocv_pred(known, features, float(model["alpha"]))
        for i, rec in known.iterrows():
            rows.append(
                {
                    "model": name,
                    "file": rec["file"],
                    "public_lb": float(rec["public_lb"]),
                    "loo_pred": float(pred[i]),
                    "loo_error": float(pred[i] - rec["public_lb"]),
                    "abs_error": float(abs(pred[i] - rec["public_lb"])),
                    "rank_actual": int(known["public_lb"].rank(method="first").iloc[i]),
                }
            )
    return pd.DataFrame(rows)


def candidate_feature_table(
    sample: pd.DataFrame,
    refs: dict[str, np.ndarray],
    ref_vecs: dict[str, np.ndarray],
    known: pd.DataFrame,
    models: pd.DataFrame,
) -> pd.DataFrame:
    known_files = set(known["file"].astype(str))
    rows: list[dict[str, Any]] = []
    for role, file_name in POST_E95_CANDIDATES:
        row = pab.feature_row(file_name, sample, refs, ref_vecs)
        row["role"] = role
        row["is_known_public"] = file_name in known_files
        row["known_public_lb"] = (
            float(known.loc[known["file"].eq(file_name), "public_lb"].iloc[0]) if file_name in known_files else np.nan
        )
        rows.append(row)
    candidates = pd.DataFrame(rows)
    scored = pab.fit_all_predict(known, candidates, models)
    best_public = float(known["public_lb"].min())
    best_model_mae = float(models[models["kind"].eq("fixed_loocv")]["mae"].min())
    scored["proxy_delta_vs_e95_public"] = scored["proxy_pred_mean"] - best_public
    scored["edge_to_proxy_mae_e95"] = -scored["proxy_delta_vs_e95_public"] / best_model_mae
    return scored.sort_values(["candidate_risk_score", "role"]).reset_index(drop=True)


def critical_pair(
    best_loo: pd.DataFrame,
    newer_file: str,
    older_file: str,
    label: str,
) -> dict[str, Any]:
    newer = best_loo[best_loo["file"].eq(newer_file)].iloc[0]
    older = best_loo[best_loo["file"].eq(older_file)].iloc[0]
    actual = float(older["public_lb"] - newer["public_lb"])
    pred = float(older["loo_pred"] - newer["loo_pred"])
    return {
        "pair": label,
        "newer_file": newer_file,
        "older_file": older_file,
        "actual_older_minus_newer": actual,
        "pred_older_minus_newer": pred,
        "correct_sign": bool(actual * pred > 0),
        "abs_error": abs(pred - actual),
        "newer_loo_error": float(newer["loo_error"]),
        "older_loo_error": float(older["loo_error"]),
    }


def write_report(known: pd.DataFrame, models: pd.DataFrame, loo: pd.DataFrame, candidates: pd.DataFrame) -> None:
    fixed = models[models["kind"].eq("fixed_loocv")].copy()
    best_model = fixed.sort_values(["mae", "rmse"]).iloc[0]
    best_name = str(best_model["model"])
    best_loo = loo[loo["model"].eq(best_name)].copy()
    e95 = best_loo[best_loo["file"].eq(E95_FILE)].iloc[0]
    mixmin = best_loo[best_loo["file"].eq(MIXMIN_FILE)].iloc[0]
    e72 = best_loo[best_loo["file"].eq(E72_FILE)].iloc[0]
    best_mae = float(best_model["mae"])
    best_p90 = float(best_model["p90_abs_error"])
    e95_edge = float(mixmin["public_lb"] - e95["public_lb"])
    e72_miss = float(e72["public_lb"] - mixmin["public_lb"])
    pairs = pd.DataFrame(
        [
            critical_pair(best_loo, E95_FILE, MIXMIN_FILE, "mixmin_minus_e95"),
            critical_pair(best_loo, MIXMIN_FILE, E72_FILE, "e72_minus_mixmin"),
            critical_pair(best_loo, E95_FILE, E72_FILE, "e72_minus_e95"),
        ]
    )

    candidate_view = candidates[
        [
            "role",
            "file",
            "known_public_lb",
            "proxy_pred_mean",
            "proxy_delta_vs_e95_public",
            "edge_to_proxy_mae_e95",
            "proxy_pred_spread",
            "below_proxy_resolution",
            "mean_abs_move_vs_a2c8",
            "mean_abs_move_vs_raw05",
            "bad_axis_abs_load",
            "good_span_residual_ratio",
            "candidate_risk_score",
        ]
    ].sort_values(["candidate_risk_score", "role"])

    future = candidate_view[candidate_view["known_public_lb"].isna()].copy()
    best_future = future.sort_values("candidate_risk_score").iloc[0]
    future_spread = float(future["proxy_delta_vs_e95_public"].max() - future["proxy_delta_vs_e95_public"].min())

    verdict = (
        "rejected"
        if best_p90 > 5.0 * max(abs(e95_edge), 1.0e-12) or not bool(pairs["correct_sign"].all())
        else "weakly_supported"
    )

    lines = [
        "# E98 E95-Updated Selector Audit",
        "",
        "## Observe",
        "",
        "E95 is the first public-positive post-mixmin movement. This gives the known-LB proxy one more near-frontier anchor: mixmin, failed E72, and successful E95 now bracket the hard-tail branch.",
        "",
        "## Wonder",
        "",
        "Does adding E95 make movement-fingerprint public regression sharp enough to choose E90/E86/E85, or does it still fail at the exact scale of the new frontier?",
        "",
        "## Hypothesis",
        "",
        "H92: E95 as a known public anchor makes the current movement proxy useful for E95-relative candidate ranking.",
        "",
        "## Method",
        "",
        "- Add `submission_e95_hardtail_541e3973.csv` public `0.5762913298` to `public_probe_observations.csv`.",
        "- Reuse fixed LOOCV ridge proxy families from `public_anchor_bottleneck_decomposition.py`.",
        "- Audit critical holdout deltas among E95, mixmin, and E72.",
        "- Score the unresolved post-E95 queue: E90, E86, E85, E89, and E87 contrasts.",
        "",
        "## Known Public Anchors",
        "",
        e56.markdown_table(
            known[
                [
                    "file",
                    "public_lb",
                    "mean_abs_move_vs_a2c8",
                    "mean_abs_move_vs_raw05",
                    "bad_axis_abs_load",
                    "good_span_residual_ratio",
                ]
            ].sort_values("public_lb")
        ),
        "",
        "## LOOCV Proxy Models",
        "",
        e56.markdown_table(
            models[
                [
                    "model",
                    "mae",
                    "rmse",
                    "max_abs_error",
                    "pairwise_rank_accuracy",
                    "p90_abs_error",
                ]
            ]
        ),
        "",
        "## Critical Near-Frontier Holdouts",
        "",
        e56.markdown_table(pairs),
        "",
        "## Candidate Proxy Scores",
        "",
        e56.markdown_table(candidate_view),
        "",
        "## Falsification",
        "",
        f"- Best fixed proxy: `{best_name}`, MAE `{best_mae:.9f}`, p90 abs error `{best_p90:.9f}`.",
        f"- New E95 edge over mixmin: `{e95_edge:.10f}`. The best proxy p90 error is `{best_p90 / max(abs(e95_edge), 1.0e-12):.2f}x` this edge.",
        f"- E72 miss over mixmin: `{e72_miss:.10f}`. The best proxy p90 error is `{best_p90 / abs(e72_miss):.2f}x` this miss.",
        f"- Best future candidate by this proxy is `{best_future['role']}` / `{best_future['file']}` with proxy delta vs E95 `{float(best_future['proxy_delta_vs_e95_public']):+.9f}`.",
        f"- Future proxy spread is `{future_spread:.9f}`, still not interpretable unless the proxy can hold out the near-frontier anchors.",
        "",
        f"Verdict: `{verdict}` for H92.",
        "",
        "## Decision",
        "",
        "Do not use E98 proxy scores as the next submission order. E95 adds a valuable public anchor, but the current known-LB regression remains too coarse at the `1e-5` to `1e-4` frontier scale. The next public file should remain a hypothesis sensor:",
        "",
        "1. `E90` if the question is whether preserving more row-coherent E86 structure beats E95's cell-local hard-tail cleanup.",
        "2. `E86` if the question is maximum source-consensus structural upside despite higher hard-tail exposure.",
        "3. `E85` if the question is whether the conservative p95 tail floor beats retained E86 structure.",
        "",
        "## Files",
        "",
        f"- `{KNOWN_OUT.name}`",
        f"- `{MODEL_OUT.name}`",
        f"- `{CANDIDATE_OUT.name}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(pab.KEYS).reset_index(drop=True)
    refs, ref_vecs = ref_features(sample)
    known = known_feature_table(sample, refs, ref_vecs)
    models = pab.evaluate_models(known)
    loo = loo_detail(known, models)
    candidates = candidate_feature_table(sample, refs, ref_vecs, known, models)

    loo.to_csv(KNOWN_OUT, index=False)
    models.to_csv(MODEL_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    write_report(known, models, loo, candidates)

    fixed = models[models["kind"].eq("fixed_loocv")].copy()
    best_model = fixed.sort_values(["mae", "rmse"]).iloc[0]
    best_loo = loo[loo["model"].eq(best_model["model"])].copy()
    e95 = best_loo[best_loo["file"].eq(E95_FILE)].iloc[0]
    mixmin = best_loo[best_loo["file"].eq(MIXMIN_FILE)].iloc[0]
    e72 = best_loo[best_loo["file"].eq(E72_FILE)].iloc[0]
    print(
        {
            "known_anchors": int(len(known)),
            "best_model": str(best_model["model"]),
            "best_mae": float(best_model["mae"]),
            "best_p90_abs_error": float(best_model["p90_abs_error"]),
            "e95_loo_error": float(e95["loo_error"]),
            "mixmin_loo_error": float(mixmin["loo_error"]),
            "e72_loo_error": float(e72["loo_error"]),
            "e95_edge_vs_mixmin": float(mixmin["public_lb"] - e95["public_lb"]),
            "e72_miss_vs_mixmin": float(e72["public_lb"] - mixmin["public_lb"]),
            "post_e95_candidates": int(len(candidates)),
            "report": str(REPORT_OUT),
        }
    )


if __name__ == "__main__":
    main()
