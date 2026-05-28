from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

SHORTLIST = OUT / "raw05_jepa_compat_band_refine_shortlist.csv"
AUDIT = OUT / "lejepa_sigreg_candidate_audit.csv"
LOCAL_LB = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
MODEL_SCORES = OUT / "local_lb_proxy_validation_model_scores.csv"

OUT_CSV = OUT / "final_jepa_compat_band_refine_addendum_20260527.csv"
OUT_MD = OUT / "final_jepa_compat_band_refine_addendum_20260527.md"


FULLSIGREG_FINALISTS = {
    "submission_raw05_jepa_compatband_e065e98e.csv",
    "submission_raw05_jepa_compatband_abc94f31.csv",
    "submission_raw05_jepa_compatband_57c2f1e7.csv",
}

LOWBAD_STRESS_ONLY = {
    "submission_raw05_jepa_compatband_cbdfe8f4.csv",
    "submission_raw05_jepa_compatband_a5965ec3.csv",
    "submission_raw05_jepa_compatband_f61b4f40.csv",
    "submission_raw05_jepa_compatband_1d434b47.csv",
}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def add_rank(df: pd.DataFrame, col: str, out_col: str) -> None:
    if col in df.columns:
        df[out_col] = df[col].rank(method="min", ascending=True, na_option="bottom")


def role_for_file(file: str) -> str:
    if file in FULLSIGREG_FINALISTS:
        return "compatband_fullsigreg_probe"
    if file in LOWBAD_STRESS_ONLY:
        return "local_lowbad_stress_only"
    return "compatband_pool"


def fmt_table(df: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    keep = [c for c in cols if c in df.columns]
    if not keep:
        return ""
    return df.loc[:, keep].head(n).to_csv(index=False)


def main() -> None:
    shortlist = read_csv(SHORTLIST)
    audit = read_csv(AUDIT)
    local = read_csv(LOCAL_LB)
    scores = read_csv(MODEL_SCORES)

    shortlist["file"] = shortlist["file"].map(Path).map(lambda p: p.name)
    audit["file"] = audit["file"].map(Path).map(lambda p: p.name)
    local["file"] = local["file"].map(Path).map(lambda p: p.name)

    audit_cols = [
        "file",
        "family",
        "lejepa_residual_health",
        "health_rank",
        "actual_rank",
        "bad_rank",
        "lejepa_combined_rank",
    ]
    local_cols = [
        "file",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "independent_lb_proxy_mean",
        "independent_lb_proxy_model_spread",
    ]

    merged = (
        shortlist.merge(audit.loc[:, [c for c in audit_cols if c in audit.columns]], on="file", how="left")
        .merge(local.loc[:, [c for c in local_cols if c in local.columns]], on="file", how="left")
    )

    for src, dst in [
        ("lejepa_combined_rank", "compatband_rank_full_sigreg"),
        ("raw05_relative_lb_proxy_mean", "compatband_rank_local_raw05_relative"),
        ("bad_residual_axis_ratio", "compatband_rank_bad_axis"),
        ("actual_anchor_score_final", "compatband_rank_actual_anchor"),
        ("quick_lejepa_health", "compatband_rank_quick_health"),
    ]:
        add_rank(merged, src, dst)

    merged["selection_role"] = merged["file"].map(role_for_file)
    merged["full_audit_matched"] = merged["lejepa_combined_rank"].notna()
    merged["local_lb_resolution_note"] = "indistinguishable_top_band"

    priority_cols = [
        "file",
        "selection_role",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "bad_residual_axis_ratio",
        "compat_kl_mean_delta_vs_raw05",
        "quick_lejepa_health",
        "lejepa_residual_health",
        "lejepa_combined_rank",
        "compatband_rank_full_sigreg",
        "compatband_rank_local_raw05_relative",
        "compatband_rank_bad_axis",
        "compatband_rank_actual_anchor",
        "base_file",
        "donor_file",
        "blend_profile",
        "beta",
        "row_gate",
        "full_audit_matched",
    ]

    merged = merged.sort_values(
        [
            "selection_role",
            "compatband_rank_full_sigreg",
            "compatband_rank_local_raw05_relative",
            "compatband_rank_actual_anchor",
        ],
        na_position="last",
    )
    merged.loc[:, [c for c in priority_cols if c in merged.columns]].to_csv(OUT_CSV, index=False)

    best_model = scores.loc[scores["model"].eq("loocv_ridge_abs_axes_a1")].iloc[0]
    fullsigreg = merged[merged["full_audit_matched"]].sort_values("lejepa_combined_rank")
    local_top = merged.sort_values("raw05_relative_lb_proxy_mean")
    lowbad = merged.sort_values("bad_residual_axis_ratio")
    finalists = merged[merged["selection_role"].ne("compatband_pool")].sort_values(
        ["selection_role", "compatband_rank_full_sigreg", "compatband_rank_local_raw05_relative"],
        na_position="last",
    )

    cols = [
        "file",
        "selection_role",
        "actual_anchor_score_final",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "bad_residual_axis_ratio",
        "compat_kl_mean_delta_vs_raw05",
        "quick_lejepa_health",
        "lejepa_residual_health",
        "lejepa_combined_rank",
        "base_file",
        "donor_file",
        "blend_profile",
        "beta",
        "row_gate",
    ]

    md = f"""# Compatibility-Band Local LB Addendum

This addendum merges the raw05 JEPA compatibility-band refinement candidates with the local public-LB proxy and the deterministic LeJEPA/SIGReg audit.

## Local LB Proxy Resolution

- Best independent local proxy: `{best_model['model']}`
- LOOCV MAE: `{best_model['mae']:.10f}`
- LOOCV RMSE: `{best_model['rmse']:.10f}`
- Max held-out error: `{best_model['max_abs_error']:.10f}`
- Practical read: compat-band candidates with raw05-relative deltas around `-0.000003` are locally indistinguishable from raw05 because the validation error is about two orders of magnitude larger.

## Finalist Split

- `compatband_fullsigreg_probe`: best compromise under full LeJEPA/SIGReg audit plus compatibility band.
- `local_lowbad_stress_only`: best local raw05-relative/bad-axis probes, but not primary finalists because full residual health is weaker.
- Full audit coverage: `{int(merged['full_audit_matched'].sum())}` / `{len(merged)}`

## Recommended Compat-Band Probes

```csv
{fmt_table(finalists, cols, n=12)}
```

## Best By Full LeJEPA/SIGReg Combined Rank

```csv
{fmt_table(fullsigreg, cols, n=12)}
```

## Best By Local Raw05-Relative Proxy

```csv
{fmt_table(local_top, cols, n=12)}
```

## Best By Bad-Axis

```csv
{fmt_table(lowbad, cols, n=12)}
```

## Decision

The compatibility-band search produced useful probes but not a new primary frontier. `submission_raw05_jepa_compatband_e065e98e.csv` is the cleanest compat-band full-audit compromise, while `submission_raw05_jepa_compatband_cbdfe8f4.csv` and neighbors are stress-only low-bad probes. Local LB validation cannot prove any of these beats `submission_raw_timeline_jepa_rescue_strict_scale0p5.csv`; it can mainly reject candidates that move too far on public-failure axes.
"""
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"merged={len(merged)} full_audit_matched={int(merged['full_audit_matched'].sum())}")


if __name__ == "__main__":
    main()
