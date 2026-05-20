# Robust OOF diagnostics

- Baseline: `v21`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v22 | 0.574235 | 0.574989 | 0.002154 | 0.577486 | 1 | 0.000000 | -0.000276 | 0.000363 | 0.001202 | False |
| v21 | 0.574597 | 0.575230 | 0.001807 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v21 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v22 | 0.000000 | 0.000000 | 0.002540 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v21 | 0.020355 | 0.148000 |
| v22 | 0.020737 | 0.148000 |
