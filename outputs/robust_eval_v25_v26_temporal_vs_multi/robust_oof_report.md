# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v25_s1s2_mid | 0.573704 | 0.574478 | 0.002210 | 0.577486 | 4 | 0.002689 | 0.004670 | 0.007888 | 0.011454 | True |
| v26_targetwise | 0.573829 | 0.574525 | 0.001988 | 0.577273 | 4 | 0.002689 | 0.004549 | 0.007763 | 0.011351 | True |
| v24 | 0.574178 | 0.574958 | 0.002228 | 0.577486 | 4 | 0.002689 | 0.004258 | 0.007414 | 0.010964 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v24 | 0.002689 | 0.008111 | 0.018634 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |
| v25_s1s2_mid | 0.002689 | 0.008111 | 0.018634 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |
| v26_targetwise | 0.002689 | 0.008111 | 0.018634 | 0.005528 | 0.006975 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| v24 | 0.021363 | 0.148000 |
| v25_s1s2_mid | 0.021236 | 0.148000 |
| v26_targetwise | 0.021492 | 0.148000 |
