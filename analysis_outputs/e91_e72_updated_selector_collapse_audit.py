#!/usr/bin/env python3
"""E91 E72-updated selector collapse audit.

The E72 public miss adds the first post-mixmin negative anchor. This audit asks
whether the existing movement-fingerprint public proxy becomes usable after
that anchor, or whether it collapses exactly where we need it: ranking
mixmin-relative E85/E86/E89/E90 successors.
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


KNOWN_OUT = OUT / "e91_e72_updated_selector_known_loo.csv"
CANDIDATE_OUT = OUT / "e91_e72_updated_selector_candidates.csv"
REPORT_OUT = OUT / "e91_e72_updated_selector_collapse_report.md"

POST_MIXMIN_CANDIDATES = [
    ("frontier", "submission_mixmin_0c916bb4.csv"),
    ("failed_public_anchor", "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"),
    ("conservative_target_prune", "submission_e85_inverse_conflict_pruned_58b23ed1.csv"),
    ("max_upside_consensus", "submission_e86_e85_consensus_a3f7c96f.csv"),
    ("no_q2_contrast", "submission_e87_noq2_source_consensus_a85c4e39.csv"),
    ("no_overstep_contrast", "submission_e87_q2_nooverstep_consensus_acd7add0.csv"),
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


def known_feature_table(sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
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
    for role, file_name in POST_MIXMIN_CANDIDATES:
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
    scored["proxy_delta_vs_mixmin_public"] = scored["proxy_pred_mean"] - best_public
    return scored.sort_values(["role"]).reset_index(drop=True)


def write_report(known: pd.DataFrame, models: pd.DataFrame, loo: pd.DataFrame, candidates: pd.DataFrame) -> None:
    fixed_models = models[models["kind"].eq("fixed_loocv")].copy()
    best_model = fixed_models.sort_values(["mae", "rmse"]).iloc[0]
    best_name = str(best_model["model"])
    best_loo = loo[loo["model"].eq(best_name)].copy()
    mixmin_loo = best_loo[best_loo["file"].eq("submission_mixmin_0c916bb4.csv")].iloc[0]
    e72_loo = best_loo[best_loo["file"].eq("submission_e72_topabs50_q2s3_gate_4e48cba2.csv")].iloc[0]
    frontier = float(known["public_lb"].min())
    e72_actual_delta = float(e72_loo["public_lb"] - frontier)
    e72_pred_delta = float(e72_loo["loo_pred"] - mixmin_loo["loo_pred"])

    candidate_view = candidates[
        [
            "role",
            "file",
            "known_public_lb",
            "proxy_pred_mean",
            "proxy_delta_vs_mixmin_public",
            "proxy_pred_spread",
            "below_proxy_resolution",
            "mean_abs_move_vs_a2c8",
            "mean_abs_move_vs_raw05",
            "bad_axis_abs_load",
            "good_span_residual_ratio",
            "candidate_risk_score",
        ]
    ].sort_values("candidate_risk_score")

    lines = [
        "# E91 E72-Updated Selector Collapse Audit",
        "",
        "## Observe",
        "",
        "E72 is the first public-negative anchor after mixmin. It is close to mixmin in public score but close in movement geometry as well, so it is a direct test of whether movement-fingerprint proxies can now rank post-mixmin candidates.",
        "",
        "## Wonder",
        "",
        "Does adding E72 make the public proxy usable for choosing among E86, E90, E89, and E85, or does the proxy fail on the exact frontier/E72 distinction?",
        "",
        "## Hypothesis",
        "",
        "H86: an E72-updated movement-fingerprint selector can rank the next mixmin-relative candidates.",
        "",
        "## Method",
        "",
        "- Reuse the public-anchor movement features from `public_anchor_bottleneck_decomposition.py`.",
        "- Include known public anchors from `public_probe_observations.csv`, now including mixmin and E72, plus manual A2C8.",
        "- Run fixed LOOCV ridge proxy families and inspect their holdout errors on mixmin and E72.",
        "- Score only the current post-mixmin decision set: E85, E86, E87 contrasts, E89, E90.",
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
        "## Critical Holdout Checks",
        "",
        f"- Best fixed proxy: `{best_name}` with MAE `{float(best_model['mae']):.9f}` and p90 abs error `{float(best_model['p90_abs_error']):.9f}`.",
        f"- Mixmin is the actual frontier at `{float(mixmin_loo['public_lb']):.10f}`, but best-proxy LOO predicts `{float(mixmin_loo['loo_pred']):.10f}`; error `{float(mixmin_loo['loo_error']):+.9f}`.",
        f"- E72 actual delta vs mixmin is `{e72_actual_delta:+.10f}`; best-proxy LOO predicted E72-minus-mixmin `{e72_pred_delta:+.10f}`.",
        f"- The proxy's p90 error is `{float(best_model['p90_abs_error']):.9f}`, about `{float(best_model['p90_abs_error']) / abs(e72_actual_delta):.2f}x` the entire E72 public miss.",
        "",
        "## Post-Mixmin Candidate Proxy Scores",
        "",
        e56.markdown_table(candidate_view),
        "",
        "## Falsification",
        "",
        "H86 is rejected as a submission selector. The updated proxy cannot explain the frontier distinction with enough resolution: it overprices/underprices mixmin-scale anchors by more than the E72 public signal itself.",
        "",
        "## Decision",
        "",
        "No E91 submission is materialized. The correct action is to keep E86/E90/E89 as predeclared public sensors, not to rank them by a regression proxy trained on the known public anchors. If one slot is used, the choice should be the hypothesis being tested: E86 for max-upside structural consensus, E90 for row-coherent E72 repair, E89 for minimum contamination.",
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
    candidates.to_csv(CANDIDATE_OUT, index=False)
    write_report(known, models, loo, candidates)

    best_model = models[models["kind"].eq("fixed_loocv")].sort_values(["mae", "rmse"]).iloc[0]
    best_loo = loo[loo["model"].eq(best_model["model"])].copy()
    mixmin = best_loo[best_loo["file"].eq("submission_mixmin_0c916bb4.csv")].iloc[0]
    e72 = best_loo[best_loo["file"].eq("submission_e72_topabs50_q2s3_gate_4e48cba2.csv")].iloc[0]
    print(
        {
            "known_anchors": int(len(known)),
            "best_model": str(best_model["model"]),
            "best_mae": float(best_model["mae"]),
            "best_p90_abs_error": float(best_model["p90_abs_error"]),
            "mixmin_loo_error": float(mixmin["loo_error"]),
            "e72_loo_error": float(e72["loo_error"]),
            "e72_actual_delta_vs_mixmin": float(e72["public_lb"] - mixmin["public_lb"]),
            "post_mixmin_candidates": int(len(candidates)),
            "report": str(REPORT_OUT),
        }
    )


if __name__ == "__main__":
    main()
