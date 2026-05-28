from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from local_lb_proxy_validation import (  # noqa: E402
    RAW05_FILE,
    RAW05_PUBLIC,
    add_derived_features,
    fit_ridge_predict,
    load_known_and_candidates,
)


OUT_PRED = OUT / "local_lb_anchor_robustness_predictions.csv"
OUT_SHORT = OUT / "local_lb_anchor_robustness_shortlist.csv"
OUT_MODEL = OUT / "local_lb_anchor_robustness_model_errors.csv"
OUT_REPORT = OUT / "local_lb_anchor_robustness_report.md"


MODEL_DEFS = [
    (
        "abs_axes",
        ["abs_delta_vs_raw05_rawaxis", "abs_bad_residual_axis_ratio", "mean_abs_move_vs_raw05"],
        1.0,
    ),
    (
        "anchor_abs_axes",
        [
            "actual_anchor_score_final",
            "abs_delta_vs_raw05_rawaxis",
            "abs_bad_residual_axis_ratio",
            "mean_abs_move_vs_raw05",
        ],
        1.0,
    ),
    (
        "signed_axes",
        ["delta_vs_raw05_rawaxis", "bad_residual_axis_ratio", "ordinal_axis_ratio", "mean_abs_move_vs_raw05"],
        1.0,
    ),
    (
        "public_shape",
        [
            "actual_anchor_score_final",
            "abs_delta_vs_raw05_rawaxis",
            "abs_bad_residual_axis_ratio",
            "abs_ordinal_axis_ratio",
            "prob_span",
        ],
        1.0,
    ),
]


def ensure_raw05(candidates: pd.DataFrame, ranker: pd.DataFrame) -> pd.DataFrame:
    if candidates["file"].astype(str).eq(RAW05_FILE).any():
        return candidates
    raw = ranker[ranker["file"].astype(str).eq(RAW05_FILE)].copy()
    if raw.empty:
        raise ValueError(f"raw05 row not found: {RAW05_FILE}")
    return pd.concat([candidates, raw], ignore_index=True, sort=False)


def eval_model_leave_one(known: pd.DataFrame, features: list[str], alpha: float) -> dict[str, float]:
    rows = []
    for holdout_idx in range(len(known)):
        train = known.drop(known.index[holdout_idx])
        holdout = known.iloc[[holdout_idx]]
        pred = fit_ridge_predict(
            train,
            train["known_public"].to_numpy(dtype=np.float64),
            holdout,
            features,
            alpha,
        )[0]
        rows.append(
            {
                "heldout_file": str(holdout["file"].iloc[0]),
                "known_public": float(holdout["known_public"].iloc[0]),
                "pred": float(pred),
                "error": float(pred - holdout["known_public"].iloc[0]),
            }
        )
    err = np.asarray([row["error"] for row in rows], dtype=np.float64)
    return {
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err**2))),
        "max_abs": float(np.max(np.abs(err))),
        "bias": float(np.mean(err)),
    }


def scenario_predictions(known: pd.DataFrame, candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw05 = candidates[candidates["file"].astype(str).eq(RAW05_FILE)]
    if len(raw05) != 1:
        raise ValueError("expected one raw05 row in candidates")
    raw05 = raw05.iloc[[0]]

    model_error_rows = []
    scenario_cols = []
    out = candidates.copy()

    for model_name, features, alpha in MODEL_DEFS:
        err = eval_model_leave_one(known, features, alpha)
        model_error_rows.append({"model": model_name, "features": ",".join(features), "alpha": alpha, **err})
        for heldout_idx in range(len(known)):
            heldout_file = str(known.iloc[heldout_idx]["file"])
            train = known.drop(known.index[heldout_idx])
            pred = fit_ridge_predict(
                train,
                train["known_public"].to_numpy(dtype=np.float64),
                candidates,
                features,
                alpha,
            )
            pred_raw = float(
                fit_ridge_predict(
                    train,
                    train["known_public"].to_numpy(dtype=np.float64),
                    raw05,
                    features,
                    alpha,
                )[0]
            )
            short = heldout_file.replace("submission_", "").replace(".csv", "")
            col = f"loao_{model_name}__drop_{short}"
            out[col] = RAW05_PUBLIC + (pred - pred_raw)
            scenario_cols.append(col)

    mat = out[scenario_cols].to_numpy(dtype=np.float64)
    out["anchor_robust_mean"] = np.nanmean(mat, axis=1)
    out["anchor_robust_median"] = np.nanmedian(mat, axis=1)
    out["anchor_robust_std"] = np.nanstd(mat, axis=1)
    out["anchor_robust_min"] = np.nanmin(mat, axis=1)
    out["anchor_robust_p10"] = np.nanpercentile(mat, 10, axis=1)
    out["anchor_robust_p90"] = np.nanpercentile(mat, 90, axis=1)
    out["anchor_robust_max"] = np.nanmax(mat, axis=1)
    out["anchor_robust_spread"] = out["anchor_robust_max"] - out["anchor_robust_min"]
    out["anchor_robust_delta_mean"] = out["anchor_robust_mean"] - RAW05_PUBLIC
    out["anchor_robust_delta_p90"] = out["anchor_robust_p90"] - RAW05_PUBLIC
    out["anchor_robust_delta_max"] = out["anchor_robust_max"] - RAW05_PUBLIC
    out["anchor_robust_beat_raw05_rate"] = np.mean(mat < RAW05_PUBLIC, axis=1)

    # A conservative scalar for sorting: lower expected delta is good, but only if
    # the leave-one-anchor distribution is not too wide.
    out["anchor_robust_selection_score"] = (
        out["anchor_robust_delta_p90"]
        + 0.15 * out["anchor_robust_std"]
        + 0.03 * out["anchor_robust_spread"]
    )
    return out, pd.DataFrame(model_error_rows).sort_values("mae").reset_index(drop=True)


def build_shortlist(pred: pd.DataFrame) -> pd.DataFrame:
    frame = pred.copy()
    for col in [
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lejepa_residual_health",
    ]:
        if col not in frame.columns:
            frame[col] = np.nan
    frame["abs_bad"] = frame["bad_residual_axis_ratio"].abs()
    frame["abs_raw"] = frame["delta_vs_raw05_rawaxis"].abs()
    frame["constraint_family"] = np.select(
        [
            frame["file"].astype(str).str.contains("structrefine|axistrade|axisrepair|axisbridge", regex=True, na=False),
            frame["file"].astype(str).str.contains("efmicro|siganchor|siggate|efback|energyfront", regex=True, na=False),
            frame["file"].astype(str).str.contains("public6entropy", regex=True, na=False),
        ],
        ["motif_structural", "lowbad_anchor", "public6entropy"],
        default="other",
    )
    frame["structural_guard"] = (
        frame["q3s4_motif_cos"].fillna(0.0).ge(0.9999)
        & frame["q3s4_motif_orth_ratio"].fillna(99.0).le(0.010)
    )
    frame["public_axis_guard"] = (
        frame["posterior_expected_public_vs_anchor"].fillna(9.0).le(0.576910)
        & frame["delta_vs_raw05_rawaxis"].fillna(9.0).le(1.0e-7)
        & frame["abs_bad"].fillna(9.0).le(0.00065)
    )
    frame["strict_public_axis_guard"] = (
        frame["posterior_expected_public_vs_anchor"].fillna(9.0).le(0.576905)
        & frame["delta_vs_raw05_rawaxis"].fillna(9.0).le(1.0e-7)
        & frame["abs_bad"].fillna(9.0).le(0.00012)
    )

    parts = [
        frame[frame["strict_public_axis_guard"] & frame["structural_guard"]]
        .sort_values(["anchor_robust_selection_score", "anchor_robust_delta_p90"])
        .head(50)
        .assign(shortlist_bucket="strict_structural_robust"),
        frame[frame["strict_public_axis_guard"]]
        .sort_values(["anchor_robust_selection_score", "anchor_robust_delta_p90"])
        .head(50)
        .assign(shortlist_bucket="strict_axis_robust"),
        frame[frame["public_axis_guard"]]
        .sort_values(["anchor_robust_selection_score", "anchor_robust_delta_p90"])
        .head(50)
        .assign(shortlist_bucket="public_axis_robust"),
        frame.sort_values(["anchor_robust_selection_score", "anchor_robust_delta_p90"])
        .head(80)
        .assign(shortlist_bucket="raw_robust_top"),
    ]
    short = pd.concat(parts, ignore_index=True, sort=False)
    short = short.drop_duplicates(["file", "shortlist_bucket"]).sort_values(
        ["shortlist_bucket", "anchor_robust_selection_score", "anchor_robust_delta_p90"]
    )
    return short.reset_index(drop=True)


def write_report(pred: pd.DataFrame, short: pd.DataFrame, model_errors: pd.DataFrame) -> None:
    cols = [
        "file",
        "rank",
        "tier",
        "constraint_family",
        "shortlist_bucket",
        "anchor_robust_mean",
        "anchor_robust_delta_mean",
        "anchor_robust_delta_p90",
        "anchor_robust_delta_max",
        "anchor_robust_std",
        "anchor_robust_spread",
        "anchor_robust_beat_raw05_rate",
        "anchor_robust_selection_score",
        "available_raw05_relative_delta_vs_raw05_public",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
        "lejepa_residual_health",
    ]
    top_raw = pred[~pred["file"].astype(str).eq(RAW05_FILE)].sort_values(
        ["anchor_robust_selection_score", "anchor_robust_delta_p90"]
    ).head(18)
    top_strict = short[short["shortlist_bucket"].eq("strict_structural_robust")].head(18)
    lines = [
        "# Local LB Anchor Robustness Probe",
        "",
        "This probe retrains the local public-LB proxy after dropping each known public anchor in turn, then evaluates each candidate relative to raw05 under every leave-one-anchor scenario.",
        "",
        "## Leave-One-Anchor Model Errors",
        "",
        "```csv",
        model_errors.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Main Read",
        "",
        f"- Scenarios per candidate: `{len(MODEL_DEFS)} models x 6 held-out anchors = {len(MODEL_DEFS) * 6}`.",
        "- `anchor_robust_delta_p90` and `anchor_robust_delta_max` are pessimistic raw05-relative diagnostics; lower is better.",
        "- This still cannot prove a public gain, but it separates candidates that only win under one anchor fit from candidates whose local edge survives anchor removal.",
        "",
        "## Raw Robust Top",
        "",
        "```csv",
        top_raw[[col for col in cols if col in top_raw.columns]].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Strict Structural Robust Top",
        "",
        "```csv",
        top_strict[[col for col in cols if col in top_strict.columns]].round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    known, candidates, ranker = load_known_and_candidates()
    candidates = ensure_raw05(add_derived_features(candidates), add_derived_features(ranker))
    candidates = candidates[candidates["file"].notna()].drop_duplicates("file").reset_index(drop=True)
    pred, model_errors = scenario_predictions(known, candidates)
    short = build_shortlist(pred)

    pred.to_csv(OUT_PRED, index=False)
    short.to_csv(OUT_SHORT, index=False)
    model_errors.to_csv(OUT_MODEL, index=False)
    write_report(pred, short, model_errors)

    keep = [
        "file",
        "rank",
        "tier",
        "shortlist_bucket",
        "anchor_robust_delta_mean",
        "anchor_robust_delta_p90",
        "anchor_robust_delta_max",
        "anchor_robust_std",
        "anchor_robust_beat_raw05_rate",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "q3s4_motif_cos",
        "q3s4_motif_orth_ratio",
    ]
    print("[model_errors]")
    print(model_errors.round(10).to_string(index=False))
    print("\n[strict_structural_robust_top]")
    sub = short[short["shortlist_bucket"].eq("strict_structural_robust")]
    print(sub[[col for col in keep if col in sub.columns]].head(20).round(10).to_string(index=False))
    print("\n[raw_robust_top]")
    raw = pred[~pred["file"].astype(str).eq(RAW05_FILE)].sort_values(
        ["anchor_robust_selection_score", "anchor_robust_delta_p90"]
    )
    print(raw[[col for col in keep if col in raw.columns]].head(20).round(10).to_string(index=False))
    print(f"\nwrote: {OUT_PRED}")
    print(f"wrote: {OUT_SHORT}")
    print(f"wrote: {OUT_MODEL}")
    print(f"wrote: {OUT_REPORT}")


if __name__ == "__main__":
    main()
