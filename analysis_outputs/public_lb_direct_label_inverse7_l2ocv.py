from __future__ import annotations

from itertools import combinations
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
DETAIL_OUT = OUT / "public_lb_direct_label_inverse7_l2ocv_detail.csv"
SOURCE_OUT = OUT / "public_lb_direct_label_inverse7_l2ocv_source_summary.csv"
POLICY_OUT = OUT / "public_lb_direct_label_inverse7_l2ocv_policy.csv"
REPORT_OUT = OUT / "public_lb_direct_label_inverse7_l2ocv_report.md"


def heldout_pred_delta(fit: inv.FitResult, preds: dict[str, np.ndarray], anchor_key: str) -> float:
    base = preds["stage2"]
    pred = preds[anchor_key]
    intercept, coef = inv.diff_terms(pred, base)
    n_cells = len(fit.flat_rows)
    return float(intercept[fit.flat_rows, fit.flat_targets].mean() + (coef[fit.flat_rows, fit.flat_targets] / n_cells) @ fit.y)


def aggregate_sources(detail: pd.DataFrame) -> pd.DataFrame:
    source = (
        detail.groupby(["mask_index", "mask_kind", "mask_name", "rows", "prior_name"], as_index=False)
        .agg(
            l2o_mae=("heldout_abs_error", "mean"),
            l2o_median=("heldout_abs_error", "median"),
            l2o_p80=("heldout_abs_error", lambda s: float(s.quantile(0.80))),
            l2o_p90=("heldout_abs_error", lambda s: float(s.quantile(0.90))),
            l2o_max=("heldout_abs_error", "max"),
            l2o_signed_mean=("heldout_signed_error", "mean"),
            l2o_signed_abs_mean=("heldout_signed_error", lambda s: float(np.mean(np.abs(s)))),
            train_solution_score_mean=("train_solution_score", "mean"),
            train_weighted_std_rmse_mean=("train_weighted_std_rmse", "mean"),
            train_shift_mean=("train_mean_abs_shift_vs_prior", "mean"),
            n_pairs=("heldout_pair", "nunique"),
            n_anchor_errors=("heldout_key", "count"),
        )
        .reset_index(drop=True)
    )
    pair = (
        detail.groupby(["mask_index", "prior_name", "heldout_pair"], as_index=False)
        .agg(pair_mae=("heldout_abs_error", "mean"), pair_max=("heldout_abs_error", "max"))
    )
    pair_agg = (
        pair.groupby(["mask_index", "prior_name"], as_index=False)
        .agg(
            l2o_pair_mae=("pair_mae", "mean"),
            l2o_pair_p90=("pair_mae", lambda s: float(s.quantile(0.90))),
            l2o_pair_max=("pair_max", "max"),
        )
    )
    source = source.merge(pair_agg, on=["mask_index", "prior_name"], how="left")
    source["l2o_source_score"] = (
        0.60 * source["l2o_mae"]
        + 0.25 * source["l2o_p90"]
        + 0.20 * source["l2o_max"]
        + 0.35 * source["l2o_pair_mae"]
        + 0.25 * source["l2o_pair_p90"]
        + 0.30 * np.abs(source["l2o_signed_mean"])
        + 0.08 * source["train_solution_score_mean"]
        + 0.01 * source["train_shift_mean"]
    )
    return source.sort_values(["l2o_source_score", "l2o_mae", "l2o_p90"]).reset_index(drop=True)


def summarize_policy(detail: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    ranked = source.sort_values(["l2o_source_score", "l2o_mae"]).copy()
    keys = ["mask_index", "prior_name"]
    rows = []
    policies = {
        "l2o_best1": ranked.head(1)[keys],
        "l2o_best5_mean": ranked.head(5)[keys],
        "l2o_best12_mean": ranked.head(12)[keys],
        "structured_best1": ranked[ranked["mask_kind"] != "random_rows"].head(1)[keys],
        "subject_best3_mean": ranked[ranked["mask_kind"].isin(["single_subject", "subject_order", "subject_contiguous"])].head(3)[keys],
        "oracle_pair_best1": None,
    }
    for pair_name, group in detail.groupby("heldout_pair", sort=False):
        pair_source = (
            group.groupby(["mask_index", "prior_name"], as_index=False)
            .agg(pair_mae=("heldout_abs_error", "mean"), pair_signed=("heldout_signed_error", "mean"))
            .sort_values("pair_mae")
        )
        for policy, key_frame in policies.items():
            if policy == "oracle_pair_best1":
                chosen_keys = pair_source.head(1)[keys]
            else:
                chosen_keys = key_frame
            if chosen_keys is None or chosen_keys.empty:
                continue
            chosen = group.merge(chosen_keys, on=keys, how="inner")
            if chosen.empty:
                continue
            pred_by_anchor = chosen.groupby("heldout_key")["heldout_pred_delta"].mean()
            obs_by_anchor = chosen.groupby("heldout_key")["heldout_obs_delta"].first()
            errors = pred_by_anchor - obs_by_anchor
            first_key = tuple(chosen_keys.iloc[0][keys])
            first_meta = source[(source["mask_index"] == first_key[0]) & (source["prior_name"] == first_key[1])].head(1)
            rows.append(
                {
                    "heldout_pair": pair_name,
                    "policy": policy,
                    "n_sources": int(len(chosen_keys)),
                    "pair_abs_error_mean": float(errors.abs().mean()),
                    "pair_abs_error_max": float(errors.abs().max()),
                    "pair_signed_error_mean": float(errors.mean()),
                    "top_mask_kind": str(first_meta["mask_kind"].iloc[0]) if not first_meta.empty else "",
                    "top_mask_name": str(first_meta["mask_name"].iloc[0]) if not first_meta.empty else "",
                    "top_prior_name": str(first_meta["prior_name"].iloc[0]) if not first_meta.empty else "",
                    "top_l2o_source_score": float(first_meta["l2o_source_score"].iloc[0]) if not first_meta.empty else np.nan,
                }
            )
    policy_df = pd.DataFrame(rows)
    overall = (
        policy_df.groupby("policy", as_index=False)
        .agg(
            pair_abs_error_mean=("pair_abs_error_mean", "mean"),
            pair_abs_error_max=("pair_abs_error_max", "mean"),
            pair_signed_error_mean=("pair_signed_error_mean", "mean"),
            top_l2o_source_score=("top_l2o_source_score", "mean"),
        )
        .assign(heldout_pair="__overall__", n_sources=np.nan, top_mask_kind="", top_mask_name="", top_prior_name="")
    )
    return pd.concat([policy_df, overall[policy_df.columns]], ignore_index=True, sort=False)


def write_report(detail: pd.DataFrame, source: pd.DataFrame, policy: pd.DataFrame) -> None:
    source_cols = [
        "mask_kind",
        "mask_name",
        "rows",
        "prior_name",
        "l2o_source_score",
        "l2o_mae",
        "l2o_p90",
        "l2o_max",
        "l2o_pair_mae",
        "l2o_pair_p90",
        "l2o_signed_mean",
        "train_solution_score_mean",
        "train_shift_mean",
    ]
    overall = policy[policy["heldout_pair"] == "__overall__"].sort_values("pair_abs_error_mean")
    per_pair = policy[policy["heldout_pair"] != "__overall__"].sort_values(["heldout_pair", "policy"])
    report = [
        "# Direct Label Inverse7 Leave-Two-Anchor CV",
        "",
        "This trains direct-label inverse solutions on four known public anchors and predicts the two held-out anchors.",
        "",
        "## Overall Policy Error",
        "",
        "```",
        overall[
            [
                "policy",
                "pair_abs_error_mean",
                "pair_abs_error_max",
                "pair_signed_error_mean",
                "top_l2o_source_score",
            ]
        ]
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Best Source Masks",
        "",
        "```",
        source[source_cols].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Per-Pair Policy Error",
        "",
        "```",
        per_pair[
            [
                "heldout_pair",
                "policy",
                "pair_abs_error_mean",
                "pair_abs_error_max",
                "pair_signed_error_mean",
                "top_mask_kind",
                "top_mask_name",
                "top_prior_name",
            ]
        ]
        .round(9)
        .to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- L2O is intentionally harsher than LOO. A source that stays near the top here is less likely to be merely fitting one anchor's idiosyncrasy.",
        "- If L2O-best masks differ from LOO-best masks, candidate generation should shrink or ensemble across both rankings instead of trusting a single mask.",
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

    rows = []
    try:
        for heldout in combinations(ALL_ANCHORS, 2):
            heldout_keys = {heldout[0][0], heldout[1][0]}
            pair_name = "+".join(sorted(heldout_keys))
            inv.ANCHORS = [anchor for anchor in ALL_ANCHORS if anchor[0] not in heldout_keys]
            for mask_row in selected_masks.itertuples(index=False):
                rec = records[int(mask_row.mask_index)]
                row_mask = rec["mask"]
                assert isinstance(row_mask, np.ndarray)
                row_series = pd.Series(mask_row._asdict())
                for prior_name, prior in priors.items():
                    fit = inv.solve_for_prior(row_series, row_mask, preds, prior_name, prior)
                    for key, file_name, public_lb, weight in heldout:
                        obs_delta = public_lb - inv.STAGE2_PUBLIC
                        pred_delta = heldout_pred_delta(fit, preds, key)
                        err = pred_delta - obs_delta
                        rows.append(
                            {
                                "heldout_pair": pair_name,
                                "heldout_key": key,
                                "heldout_file": file_name,
                                "heldout_public": public_lb,
                                "heldout_weight": weight,
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

    detail = pd.DataFrame(rows)
    detail.to_csv(DETAIL_OUT, index=False)
    source = aggregate_sources(detail)
    source.to_csv(SOURCE_OUT, index=False)
    policy = summarize_policy(detail, source)
    policy.to_csv(POLICY_OUT, index=False)
    write_report(detail, source, policy)

    print(REPORT_OUT)
    print("[overall]")
    print(
        policy[policy["heldout_pair"] == "__overall__"][
            [
                "policy",
                "pair_abs_error_mean",
                "pair_abs_error_max",
                "pair_signed_error_mean",
                "top_l2o_source_score",
            ]
        ]
        .sort_values("pair_abs_error_mean")
        .round(9)
        .to_string(index=False)
    )
    print("[sources]")
    print(source[["mask_kind", "mask_name", "rows", "prior_name", "l2o_source_score", "l2o_mae", "l2o_p90", "l2o_pair_mae"]].head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
