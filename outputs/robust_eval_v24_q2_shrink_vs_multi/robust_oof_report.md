# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q2w015 | 0.574155 | 0.574946 | 0.002258 | 0.577486 | 4 | 0.002689 | 0.004288 | 0.007437 | 0.010973 | True |
| q2w010 | 0.574178 | 0.574958 | 0.002228 | 0.577486 | 4 | 0.002689 | 0.004258 | 0.007414 | 0.010964 | True |
| v22 | 0.574235 | 0.574989 | 0.002154 | 0.577486 | 4 | 0.002689 | 0.004188 | 0.007358 | 0.010930 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q2w010 | 0.002689 | 0.008111 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |
| q2w015 | 0.002689 | 0.008267 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |
| v22 | 0.002689 | 0.007713 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| q2w010 | 0.021363 | 0.148000 |
| q2w015 | 0.021675 | 0.148000 |
| v22 | 0.020737 | 0.148000 |
