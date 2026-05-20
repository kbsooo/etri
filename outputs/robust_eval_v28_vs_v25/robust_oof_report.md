# Robust OOF diagnostics

- Baseline: `v25`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28 | 0.572758 | 0.573636 | 0.002510 | 0.577486 | 3 | 0.000000 | -0.000086 | 0.000947 | 0.001962 | False |
| v27w100 | 0.572806 | 0.573674 | 0.002479 | 0.577486 | 2 | 0.000000 | -0.000124 | 0.000898 | 0.001907 | False |
| v27w050 | 0.573139 | 0.573951 | 0.002320 | 0.577486 | 2 | 0.000000 | 0.000046 | 0.000566 | 0.001084 | False |
| v25 | 0.573704 | 0.574478 | 0.002210 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v25 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v27w050 | 0.000000 | 0.000000 | 0.003960 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v27w100 | 0.000000 | 0.000000 | 0.006286 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v28 | 0.000000 | 0.000341 | 0.006286 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v25 | 0.021236 | 0.148000 |
| v27w050 | 0.021591 | 0.148000 |
| v27w100 | 0.021898 | 0.148000 |
| v28 | 0.022648 | 0.148000 |
