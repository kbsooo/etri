# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label | 0.573944 | 0.574516 | 0.001636 | 0.576832 | 4 | 0.002689 | 0.004308 | 0.007649 | 0.011337 | True |
| v24 | 0.574178 | 0.574958 | 0.002228 | 0.577486 | 4 | 0.002689 | 0.004258 | 0.007414 | 0.010964 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label | 0.002689 | 0.008111 | 0.018634 | 0.005528 | 0.006175 | 0.004786 | 0.007617 |
| v24 | 0.002689 | 0.008111 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| temporal_label | 0.021368 | 0.148000 |
| v24 | 0.021363 | 0.148000 |
