from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402


ALL_ANCHORS = list(inv.ANCHORS)
DETAIL_OUT = OUT / "public_lb_direct_label_inverse7_loocv_detail.csv"
POLICY_OUT = OUT / "public_lb_direct_label_inverse7_loocv_policy.csv"
REPORT_OUT = OUT / "public_lb_direct_label_inverse7_loocv_report.md"


def heldout_pred_delta(fit: inv.FitResult, preds: dict[str, np.ndarray], anchor_key: str) -> float:
    base = preds["stage2"]
    pred = preds[anchor_key]
    intercept, coef = inv.diff_terms(pred, base)
    n_cells = len(fit.flat_rows)
    return float(intercept[fit.flat_rows, fit.flat_targets].mean() + (coef[fit.flat_rows, fit.flat_targets] / n_cells) @ fit.y)


def summarize_policy(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    policies = [
        ("train_best1", lambda df: df.sort_values(["train_solution_score", "train_weighted_std_rmse", "train_mean_abs_shift_vs_prior"]).head(1)),
        ("train_best5_mean", lambda df: df.sort_values(["train_solution_score", "train_weighted_std_rmse", "train_mean_abs_shift_vs_prior"]).head(5)),
        ("train_best12_mean", lambda df: df.sort_values(["train_solution_score", "train_weighted_std_rmse", "train_mean_abs_shift_vs_prior"]).head(12)),
        (
            "structured_best1",
            lambda df: df[df["mask_kind"].isin(["single_subject", "subject_order", "global_order", "subject_contiguous"])]
            .sort_values(["train_solution_score", "train_weighted_std_rmse", "train_mean_abs_shift_vs_prior"])
            .head(1),
        ),
        (
            "nonrandom_best5_mean",
            lambda df: df[df["mask_kind"] != "random_rows"]
            .sort_values(["train_solution_score", "train_weighted_std_rmse", "train_mean_abs_shift_vs_prior"])
            .head(5),
        ),
        ("oracle_best1", lambda df: df.sort_values("heldout_abs_error").head(1)),
    ]
    for heldout, group in detail.groupby("heldout_key", sort=False):
        for name, selector in policies:
            chosen = selector(group)
            if chosen.empty:
                continue
            pred = float(chosen["heldout_pred_delta"].mean())
            obs = float(chosen["heldout_obs_delta"].iloc[0])
            err = pred - obs
            rows.append(
                {
                    "heldout_key": heldout,
                    "policy": name,
                    "n_selected": int(len(chosen)),
                    "heldout_pred_delta": pred,
                    "heldout_obs_delta": obs,
                    "heldout_abs_error": abs(err),
                    "heldout_signed_error": err,
                    "heldout_public_pred": float(inv.STAGE2_PUBLIC + pred),
                    "heldout_public_actual": float(inv.STAGE2_PUBLIC + obs),
                    "top_mask_kind": str(chosen.iloc[0]["mask_kind"]),
                    "top_mask_name": str(chosen.iloc[0]["mask_name"]),
                    "top_prior_name": str(chosen.iloc[0]["prior_name"]),
                    "top_solution_score": float(chosen.iloc[0]["train_solution_score"]),
                }
            )
    policy = pd.DataFrame(rows)
    agg_rows = []
    for name, group in policy.groupby("policy", sort=False):
        agg_rows.append(
            {
                "heldout_key": "__overall__",
                "policy": name,
                "n_selected": int(group["n_selected"].sum()),
                "heldout_pred_delta": np.nan,
                "heldout_obs_delta": np.nan,
                "heldout_abs_error": float(group["heldout_abs_error"].mean()),
                "heldout_signed_error": float(group["heldout_signed_error"].mean()),
                "heldout_public_pred": np.nan,
                "heldout_public_actual": np.nan,
                "top_mask_kind": "",
                "top_mask_name": "",
                "top_prior_name": "",
                "top_solution_score": float(group["top_solution_score"].mean()),
            }
        )
    return pd.concat([policy, pd.DataFrame(agg_rows)], ignore_index=True, sort=False)


def write_report(policy: pd.DataFrame, detail: pd.DataFrame) -> None:
    per_anchor = policy[policy["heldout_key"] != "__overall__"].copy()
    overall = policy[policy["heldout_key"] == "__overall__"].copy()
    best_detail = (
        detail.sort_values(["heldout_key", "train_solution_score", "heldout_abs_error"])
        .groupby("heldout_key", as_index=False)
        .head(5)
    )
    report = [
        "# Direct Label Inverse7 Leave-One-Anchor CV",
        "",
        "This checks whether soft-label inverse solutions selected on five public anchors predict the sixth public anchor.",
        "",
        "## Overall Policy Error",
        "",
        "```",
        overall[
            [
                "policy",
                "heldout_abs_error",
                "heldout_signed_error",
                "top_solution_score",
            ]
        ]
        .sort_values("heldout_abs_error")
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Per-Anchor Policy Error",
        "",
        "```",
        per_anchor[
            [
                "heldout_key",
                "policy",
                "heldout_abs_error",
                "heldout_signed_error",
                "heldout_public_pred",
                "heldout_public_actual",
                "top_mask_kind",
                "top_mask_name",
                "top_prior_name",
            ]
        ]
        .sort_values(["heldout_key", "policy"])
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Train-Selected Top Fits By Heldout Anchor",
        "",
        "```",
        best_detail[
            [
                "heldout_key",
                "mask_kind",
                "mask_name",
                "rows",
                "prior_name",
                "train_solution_score",
                "train_weighted_std_rmse",
                "train_mean_abs_shift_vs_prior",
                "heldout_abs_error",
                "heldout_pred_delta",
                "heldout_obs_delta",
            ]
        ]
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- If `train_best*` is much worse than `oracle_best1`, the inverse problem is still underidentified: useful label assignments exist, but the current selector cannot reliably choose them.",
        "- A high error on `cvjepa_a2c8` means the direct-label solver can reproduce older anchors while missing the new best anchor, so direct-label probes should be treated as diagnostic larger moves.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(inv.KEY).reset_index(drop=True)
    records, mask_meta = inv.mask_records(sample)
    selected_masks = inv.selected_mask_indices().merge(mask_meta, on=["mask_index", "mask_kind", "mask_name", "rows"], how="left")

    inv.ANCHORS = ALL_ANCHORS
    preds = inv.load_predictions(sample)
    priors = {
        name: inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64)
        for name, file_name in inv.PRIOR_FILES.items()
        if inv.locate(file_name) is not None
    }

    detail_rows = []
    try:
        for heldout_key, heldout_file, heldout_public, heldout_weight in ALL_ANCHORS:
            inv.ANCHORS = [anchor for anchor in ALL_ANCHORS if anchor[0] != heldout_key]
            obs_delta = heldout_public - inv.STAGE2_PUBLIC
            for mask_row in selected_masks.itertuples(index=False):
                rec = records[int(mask_row.mask_index)]
                row_mask = rec["mask"]
                assert isinstance(row_mask, np.ndarray)
                row_series = pd.Series(mask_row._asdict())
                for prior_name, prior in priors.items():
                    fit = inv.solve_for_prior(row_series, row_mask, preds, prior_name, prior)
                    pred_delta = heldout_pred_delta(fit, preds, heldout_key)
                    err = pred_delta - obs_delta
                    detail_rows.append(
                        {
                            "heldout_key": heldout_key,
                            "heldout_file": heldout_file,
                            "heldout_public": heldout_public,
                            "heldout_weight": heldout_weight,
                            "heldout_obs_delta": obs_delta,
                            "heldout_pred_delta": pred_delta,
                            "heldout_abs_error": abs(err),
                            "heldout_signed_error": err,
                            "mask_index": fit.mask_index,
                            "mask_kind": fit.mask_kind,
                            "mask_name": fit.mask_name,
                            "rows": fit.rows,
                            "top_blocks": fit.top_blocks,
                            "prior_name": fit.prior_name,
                            "lambda": fit.lam,
                            "train_solution_score": float(fit.metrics["solution_score"]),
                            "train_weighted_std_rmse": float(fit.metrics["weighted_std_rmse"]),
                            "train_mean_abs_shift_vs_prior": float(fit.metrics["mean_abs_shift_vs_prior"]),
                            "train_near_binary_rate_05": float(fit.metrics["near_binary_rate_05"]),
                        }
                    )
    finally:
        inv.ANCHORS = ALL_ANCHORS

    detail = pd.DataFrame(detail_rows)
    detail.to_csv(DETAIL_OUT, index=False)
    policy = summarize_policy(detail)
    policy.to_csv(POLICY_OUT, index=False)
    write_report(policy, detail)

    print(REPORT_OUT)
    print("[overall]")
    print(
        policy[policy["heldout_key"] == "__overall__"][
            ["policy", "heldout_abs_error", "heldout_signed_error", "top_solution_score"]
        ]
        .sort_values("heldout_abs_error")
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
