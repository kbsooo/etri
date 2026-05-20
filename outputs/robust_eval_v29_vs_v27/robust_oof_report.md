# Robust OOF diagnostics

- Baseline: `v27`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v29 | 0.572520 | 0.573492 | 0.002778 | 0.577482 | 4 | 0.000000 | -0.000367 | 0.000495 | 0.001323 | False |
| v28 | 0.572758 | 0.573636 | 0.002510 | 0.577486 | 3 | 0.000000 | -0.000129 | 0.000257 | 0.000630 | False |
| prior_proj | 0.572758 | 0.573709 | 0.002717 | 0.577482 | 3 | 0.000000 | -0.000651 | 0.000257 | 0.001130 | False |
| v27 | 0.573015 | 0.573845 | 0.002372 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prior_proj | 0.000000 | 0.000194 | 0.000000 | 0.000520 | 0.000442 | 0.000107 | 0.000535 |
| v27 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v28 | 0.000000 | 0.000341 | 0.001461 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v29 | 0.000000 | 0.000194 | 0.000000 | 0.002187 | 0.000442 | 0.000107 | 0.000535 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| prior_proj | 0.022059 | 0.156000 |
| v27 | 0.021688 | 0.148000 |
| v28 | 0.022648 | 0.148000 |
| v29 | 0.021347 | 0.156000 |
