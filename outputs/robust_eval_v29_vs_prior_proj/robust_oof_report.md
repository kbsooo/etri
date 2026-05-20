# Robust OOF diagnostics

- Baseline: `prior_proj`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v29 | 0.572520 | 0.573492 | 0.002778 | 0.577482 | 2 | 0.000000 | 0.000017 | 0.000238 | 0.000472 | False |
| prior_proj | 0.572758 | 0.573709 | 0.002717 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| v28 | 0.572758 | 0.573717 | 0.002510 | 0.577486 | 2 | -0.000535 | -0.000940 | 0.000000 | 0.000977 | False |
| v27 | 0.573015 | 0.573925 | 0.002372 | 0.577486 | 2 | -0.000535 | -0.001130 | -0.000257 | 0.000651 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prior_proj | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v27 | 0.000000 | -0.000194 | 0.000000 | -0.000520 | -0.000442 | -0.000107 | -0.000535 |
| v28 | 0.000000 | 0.000147 | 0.001461 | -0.000520 | -0.000442 | -0.000107 | -0.000535 |
| v29 | 0.000000 | 0.000000 | 0.000000 | 0.001667 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| prior_proj | 0.022059 | 0.156000 |
| v27 | 0.021688 | 0.148000 |
| v28 | 0.022648 | 0.148000 |
| v29 | 0.021347 | 0.156000 |
