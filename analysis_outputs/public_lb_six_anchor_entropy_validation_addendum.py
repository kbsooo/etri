from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

SCAN = OUT / "public_lb_six_anchor_entropy_projection_scan.csv"
LOCAL = OUT / "local_lb_proxy_validation_candidate_predictions.csv"
LEJEPA = OUT / "lejepa_sigreg_candidate_audit.csv"
OUT_CSV = OUT / "public_lb_six_anchor_entropy_validation_addendum.csv"
OUT_MD = OUT / "public_lb_six_anchor_entropy_validation_addendum.md"

RAW05_PUBLIC = 0.5775263072


def read(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def table(frame: pd.DataFrame, cols: list[str], n: int = 12) -> str:
    keep = [c for c in cols if c in frame.columns]
    return frame.loc[:, keep].head(n).to_csv(index=False)


def main() -> None:
    scan = read(SCAN)
    local = read(LOCAL)
    lejepa = read(LEJEPA)

    scan["file"] = scan["file"].astype(str)
    local["file"] = local["file"].astype(str)
    lejepa["file"] = lejepa["file"].astype(str)

    local_cols = [
        "file",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "axis_only_raw05_relative_lb_proxy_mean",
        "axis_only_raw05_relative_delta_vs_raw05_public",
        "axis_only_raw05_relative_lb_proxy_model_spread",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_raw05_relative_model_spread",
        "available_proxy_model_family",
        "independent_lb_proxy_mean",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
    ]
    lejepa_cols = [
        "file",
        "family",
        "lejepa_residual_health",
        "health_rank",
        "actual_rank",
        "bad_rank",
        "lejepa_combined_rank",
        "public_axis_sigreg_global",
        "target_q3s4_sigreg_global",
    ]
    merged = (
        scan.merge(local[[c for c in local_cols if c in local.columns]], on="file", how="left", suffixes=("", "_local"))
        .merge(lejepa[[c for c in lejepa_cols if c in lejepa.columns]], on="file", how="left")
    )
    merged["abs_bad_residual_axis_ratio"] = merged["bad_residual_axis_ratio_local"].abs()
    merged["local_evaluated"] = merged["available_raw05_relative_delta_vs_raw05_public"].notna()
    merged["local_reject"] = merged["local_evaluated"] & (merged["available_raw05_relative_delta_vs_raw05_public"] > 0.0)
    merged["large_bad_axis"] = merged["abs_bad_residual_axis_ratio"] > 0.02
    merged["validation_role"] = "hold_public6_inverse"
    merged.loc[
        (~merged["local_reject"]) & (~merged["large_bad_axis"]),
        "validation_role",
    ] = "possible_probe"
    merged.to_csv(OUT_CSV, index=False)

    public6 = merged[merged["file"].str.contains("public6entropy", na=False)].copy()
    local_top = public6.sort_values("available_raw05_relative_lb_proxy_mean")
    lejepa_top = public6.sort_values("lejepa_combined_rank", na_position="last")
    low_bad = public6.sort_values("abs_bad_residual_axis_ratio")

    best_local = local_top.iloc[0]
    best_lejepa = lejepa_top.iloc[0]
    local_evaluated = int(public6["local_evaluated"].sum())
    rejected_count = int(public6["local_reject"].sum())
    large_bad_count = int(public6["large_bad_axis"].sum())

    cols = [
        "file",
        "prior",
        "target_mask",
        "gamma",
        "available_raw05_relative_lb_proxy_mean",
        "available_raw05_relative_delta_vs_raw05_public",
        "available_proxy_model_family",
        "axis_only_raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_mean",
        "raw05_relative_delta_vs_raw05_public",
        "raw05_relative_lb_proxy_model_spread",
        "posterior_expected_public_vs_anchor",
        "bad_residual_axis_ratio_local",
        "mean_abs_move_vs_raw05_local",
        "lejepa_residual_health",
        "lejepa_combined_rank",
        "validation_role",
    ]

    md = f"""# Public6 Entropy Validation Addendum

This merges the six-anchor entropy-projection candidates with local public-LB proxy predictions and deterministic LeJEPA/SIGReg audit.

## Summary

- public6 generated candidates: `{len(public6)}`
- public6 candidates evaluated by local LB proxy: `{local_evaluated}`
- local raw05-relative rejects among evaluated candidates: `{rejected_count}` / `{local_evaluated}`
- large bad-axis candidates (`abs(bad_residual_axis_ratio) > 0.02`): `{large_bad_count}` / `{len(public6)}`
- raw05 public control: `{RAW05_PUBLIC:.10f}`
- best local public6 candidate: `{best_local['file']}` at `{best_local['available_raw05_relative_lb_proxy_mean']:.10f}`; delta `{best_local['available_raw05_relative_delta_vs_raw05_public']:.10f}` using `{best_local['available_proxy_model_family']}`
- best LeJEPA public6 candidate: `{best_lejepa['file']}` with combined rank `{best_lejepa['lejepa_combined_rank']:.2f}`, local available delta `{best_lejepa['available_raw05_relative_delta_vs_raw05_public']:.10f}`

## Best By Local Raw05-Relative Proxy

```csv
{table(local_top, cols, 16)}
```

## Best By LeJEPA/SIGReg Combined Rank

```csv
{table(lejepa_top, cols, 16)}
```

## Lowest Bad-Axis Public6 Candidates

```csv
{table(low_bad, cols, 16)}
```

## Decision

Six-anchor entropy projection is useful as a diagnostic and only a very small probe generator. It exactly fits known public scores, but leave-one-anchor-out reliability is around `0.001`. Direct large-move public6 candidates remain unsafe because many have large bad-axis movement. After the missing-anchor-feature correction, a few raw05-based small-move candidates are axis-only competitive, but their margin is far below the local proxy's LOOCV error, so they are probes rather than confirmed improvements.
"""
    OUT_MD.write_text(md, encoding="utf-8")
    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print(f"public6={len(public6)} rejected={rejected_count} large_bad={large_bad_count}")


if __name__ == "__main__":
    main()
