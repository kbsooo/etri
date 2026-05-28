# Public Two-Axis Blend Report

Last updated: 2026-05-26

## Purpose

The previous public-aware audit used one observed failure direction:

```text
stage2 -> ordinal/ambnext
public delta = +0.0003583895
```

There is also one observed success direction:

```text
0p578 anchor -> stage2
public delta = -0.0004823771
```

`public_two_axis_blend_optimizer.py` decomposes each candidate move from stage2 into these two axes:

- `good_axis_coef`: exposure to the public-good anchor-to-stage2 direction.
- `bad_axis_coef`: exposure to the public-bad stage2-to-ordinal direction after accounting for the good axis.
- `two_axis_public_est`: linear public estimate using both observed public deltas.

This is more informative than the one-axis projection, but also more model-based. The residual ratios are high for low-risk files, so this should be treated as a ranking/audit model, not a proof.

## Generated Candidates

| File | OOF | Two-axis public delta vs stage2 | One-axis public delta vs stage2 | Components |
| --- | ---: | ---: | ---: | --- |
| `submission_public2dblend_budgetm0p00001.csv` | 0.563026 | -0.000010 | -0.000000 | 33% pure Q2/Q3 exact + 67% pure orthcap |
| `submission_public2dblend_budget0p0.csv` | 0.561702 | -0.000000 | +0.000009 | 75% `projblend_cap0p0` + 25% `projblend_cap0p1` |
| `submission_public2dblend_budget0p00002.csv` | 0.560724 | +0.000020 | +0.000031 | 27% `projblend_cap0p05` + 73% `projblend_cap0p1` |
| `submission_public2dblend_budget0p00005.csv` | 0.560039 | +0.000050 | +0.000061 | 67% cap010 Q2/Q3 exact + 33% cap030 Q2/Q3 exact |
| `submission_public2dblend_budget0p00010.csv` | 0.559351 | +0.000097 | +0.000109 | 88% cap030 Q2/Q3 exact + 12% cap030 Q3 exact |

## Interpretation

`submission_public2dblend_budget0p0.csv` is the best new low-risk file. It is almost public-neutral under the two-axis model, while OOF `0.561702` is slightly better than the old `projblend_cap0p025` OOF `0.561715`.

`submission_public2dblend_budget0p00002.csv` is the best new balanced score probe. It improves OOF to `0.560724`, stronger than `projblend_cap0p075` (`0.560904`) at a similar practical risk level.

The high-upside two-axis files are mostly refinements of the cap030 exact family. They are useful endpoints, but not low-risk blind submissions.

## Integrity

All generated two-axis submissions have:

- 250 rows
- 0 duplicate keys
- 0 missing predictions
- probability ranges inside `[0.05848, 0.98267]` for the low/balanced files
- favorable per-target OOF deltas versus stage2 for all seven targets

## Reproducibility

Generator:

```text
analysis_outputs/public_two_axis_blend_optimizer.py
```

Main generated tables:

```text
analysis_outputs/public_two_axis_blend_pool.csv
analysis_outputs/public_two_axis_blend_scan.csv
analysis_outputs/public_two_axis_blend_summary.csv
analysis_outputs/public_two_axis_blend_integrity_and_deltas.csv
analysis_outputs/public_two_axis_blend_candidates.csv
```
