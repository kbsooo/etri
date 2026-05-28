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

from hidden_subset_selector_stress import MODEL_DEFS as OLD_MODEL_DEFS  # noqa: E402
from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, feature_row  # noqa: E402
from public_pairwise_order_selector import ALPHAS, FEATURE_SETS, fit_pairwise  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


PINNED = [
    "analysis_outputs/submission_label_flow_focused_1bbfb735.csv",
    "analysis_outputs/submission_label_flow_focused_6b9335b1.csv",
    "analysis_outputs/submission_label_flow_combo_3d536109.csv",
    "analysis_outputs/submission_label_flow_twampl_b8c66b64.csv",
    "analysis_outputs/submission_label_flow_gated_ff8df011.csv",
    "analysis_outputs/submission_label_flow_gated_f1046674.csv",
]

DETAIL_OUT = OUT / "selector_conflict_decomposition_detail.csv"
SUMMARY_OUT = OUT / "selector_conflict_decomposition_summary.csv"
REPORT_OUT = OUT / "selector_conflict_decomposition_report.md"


def standardize(train: np.ndarray, point_diff: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = np.nanmean(train, axis=0)
    sigma = np.nanstd(train, axis=0)
    sigma = np.where(sigma < 1e-12, 1.0, sigma)
    return np.nan_to_num(point_diff / sigma), mu, sigma


def old_selector_contribs(known: pd.DataFrame, candidates: pd.DataFrame, anchor: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, features, alpha in OLD_MODEL_DEFS:
        x = known[features].to_numpy(dtype=np.float64)
        y = known["public_lb"].to_numpy(dtype=np.float64)
        mu = np.nanmean(x, axis=0)
        sigma = np.nanstd(x, axis=0)
        sigma = np.where(sigma < 1e-12, 1.0, sigma)
        x_std = np.nan_to_num((x - mu) / sigma)
        x_aug = np.column_stack([np.ones(len(x_std)), x_std])
        penalty = np.eye(x_aug.shape[1], dtype=np.float64) * float(alpha)
        penalty[0, 0] = 0.0
        beta = np.linalg.pinv(x_aug.T @ x_aug + penalty) @ x_aug.T @ y

        anchor_x = anchor[features].to_numpy(dtype=np.float64)
        for rec in candidates.to_dict("records"):
            cand_x = np.asarray([float(rec[f]) for f in features], dtype=np.float64)
            raw_diff = cand_x - anchor_x
            z_diff = np.nan_to_num(raw_diff / sigma)
            contrib = z_diff * beta[1:]
            pred_delta = float(np.sum(contrib))
            for feature, raw, z, value in zip(features, raw_diff, z_diff, contrib, strict=True):
                rows.append(
                    {
                        "selector": "old_hidden_subset",
                        "candidate": str(rec["file"]),
                        "model": model,
                        "alpha": float(alpha),
                        "pred_delta_vs_a2c8": pred_delta,
                        "feature": feature,
                        "raw_diff_vs_a2c8": float(raw),
                        "z_diff_vs_a2c8": float(z),
                        "contribution": float(value),
                    }
                )
    return pd.DataFrame(rows)


def pairwise_selector_contribs(known: pd.DataFrame, candidates: pd.DataFrame, anchor: pd.Series) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, features in FEATURE_SETS:
        for alpha in ALPHAS:
            fit = fit_pairwise(known, model, features, alpha)
            if fit is None:
                continue
            anchor_x = anchor[list(fit.features)].to_numpy(dtype=np.float64)
            for rec in candidates.to_dict("records"):
                cand_x = np.asarray([float(rec[f]) for f in fit.features], dtype=np.float64)
                raw_diff = cand_x - anchor_x
                z_diff = np.nan_to_num((raw_diff - fit.mu) / fit.sigma)
                contrib = z_diff * fit.beta
                pred_delta = float(np.sum(contrib))
                for feature, raw, z, value in zip(fit.features, raw_diff, z_diff, contrib, strict=True):
                    rows.append(
                        {
                            "selector": "pairwise_order",
                            "candidate": str(rec["file"]),
                            "model": fit.model,
                            "alpha": float(fit.alpha),
                            "pred_delta_vs_a2c8": pred_delta,
                            "feature": feature,
                            "raw_diff_vs_a2c8": float(raw),
                            "z_diff_vs_a2c8": float(z),
                            "contribution": float(value),
                        }
                    )
    return pd.DataFrame(rows)


def summarize(detail: pd.DataFrame) -> pd.DataFrame:
    return (
        detail.groupby(["candidate", "selector", "feature"], as_index=False)
        .agg(
            mean_contribution=("contribution", "mean"),
            median_contribution=("contribution", "median"),
            abs_mean_contribution=("contribution", lambda x: float(np.mean(np.abs(x)))),
            mean_z_diff=("z_diff_vs_a2c8", "mean"),
            mean_raw_diff=("raw_diff_vs_a2c8", "mean"),
            mean_pred_delta=("pred_delta_vs_a2c8", "mean"),
        )
        .sort_values(["candidate", "selector", "abs_mean_contribution"], ascending=[True, True, False])
        .reset_index(drop=True)
    )


def write_report(summary: pd.DataFrame, detail: pd.DataFrame) -> None:
    lines = [
        "# Selector Conflict Decomposition",
        "",
        "Purpose: explain why E14 S4+Q3 label-flow candidates look good to the pairwise selector but fail independent hidden-subset survival.",
        "",
        "Sign convention: `pred_delta_vs_a2c8 < 0` means the selector predicts the candidate is better than a2c8; positive means worse.",
        "",
        "## Candidate-Level Predicted Deltas",
        "",
    ]
    pred = (
        detail.groupby(["candidate", "selector", "model", "alpha"], as_index=False)["pred_delta_vs_a2c8"].first()
        .groupby(["candidate", "selector"], as_index=False)
        .agg(
            mean_pred_delta=("pred_delta_vs_a2c8", "mean"),
            median_pred_delta=("pred_delta_vs_a2c8", "median"),
            p10_pred_delta=("pred_delta_vs_a2c8", lambda x: float(np.quantile(x, 0.10))),
            p90_pred_delta=("pred_delta_vs_a2c8", lambda x: float(np.quantile(x, 0.90))),
            better_rate=("pred_delta_vs_a2c8", lambda x: float(np.mean(np.asarray(x) < 0.0))),
        )
        .sort_values(["candidate", "selector"])
    )
    lines.append(pred.round(9).to_csv(index=False))
    lines.extend(["", "## Top Contributions By Candidate", ""])

    for candidate in PINNED:
        lines.extend([f"### {candidate}", ""])
        sub = summary[summary["candidate"].eq(candidate)].copy()
        for selector in ["pairwise_order", "old_hidden_subset"]:
            top = sub[sub["selector"].eq(selector)].sort_values("abs_mean_contribution", ascending=False).head(8)
            lines.extend([f"#### {selector}", "", top.round(9).to_csv(index=False), ""])

    lines.extend(
        [
            "## Interpretation",
            "",
            "- Pairwise models are internally mixed: S4 target-local movement and max-move terms often give favorable contributions, while residual-span/projection terms push the other way. E14 optimized the favorable pairwise scenario tail, not a unanimous pairwise model family.",
            "- Old hidden-subset models also mix signs, but they do not give a scenario-majority endorsement. They mostly treat the focused S4/Q3 movement as an underidentified move away from a2c8 because the known public anchor set has no positive example for this exact direction.",
            "- This is an underidentification problem: current anchors cannot tell whether the pairwise S4+Q3 direction is real public signal or a surrogate artifact. That is why E15 closed the submission gate.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    known, refs, ref_vecs = build_known_and_refs(sample)
    anchor = known[known["file"].eq(A2C8)].iloc[0]

    rows: list[dict[str, object]] = []
    for rel in PINNED:
        path = ROOT / rel
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel
        rows.append(row)
    candidates = pd.DataFrame(rows)

    detail = pd.concat(
        [
            pairwise_selector_contribs(known, candidates, anchor),
            old_selector_contribs(known, candidates, anchor),
        ],
        ignore_index=True,
        sort=False,
    )
    summary = summarize(detail)
    detail.to_csv(DETAIL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(summary, detail)

    print(REPORT_OUT)
    pred = (
        detail.groupby(["candidate", "selector", "model", "alpha"], as_index=False)["pred_delta_vs_a2c8"].first()
        .groupby(["candidate", "selector"], as_index=False)
        .agg(mean_pred_delta=("pred_delta_vs_a2c8", "mean"), better_rate=("pred_delta_vs_a2c8", lambda x: float(np.mean(np.asarray(x) < 0.0))))
    )
    print(pred.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
