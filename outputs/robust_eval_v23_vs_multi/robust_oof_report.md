# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v23 | 0.574109 | 0.574922 | 0.002322 | 0.577486 | 4 | 0.002689 | 0.004357 | 0.007483 | 0.010977 | True |
| v22 | 0.574235 | 0.574989 | 0.002154 | 0.577486 | 4 | 0.002689 | 0.004200 | 0.007358 | 0.010895 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v22 | 0.002689 | 0.007713 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |
| v23 | 0.002689 | 0.008592 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| v22 | 0.020737 | 0.148000 |
| v23 | 0.022614 | 0.148000 |
