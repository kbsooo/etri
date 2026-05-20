# Robust OOF diagnostics

- Baseline: `multi`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| portfolio | 0.575829 | 0.576574 | 0.002131 | 0.578006 | 4 | 0.001424 | 0.002968 | 0.005764 | 0.008892 | True |
| v17 | 0.574969 | 0.575750 | 0.002230 | 0.577486 | 3 | 0.001424 | 0.003445 | 0.006623 | 0.010082 | False |
| v15 | 0.575529 | 0.576583 | 0.003014 | 0.580234 | 3 | 0.001424 | 0.003111 | 0.006064 | 0.009260 | False |
| multi | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| portfolio | 0.002689 | 0.007713 | 0.012511 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| v15 | 0.002689 | 0.005693 | 0.018796 | 0.001424 | 0.004672 | 0.001555 | 0.007617 |
| v17 | 0.002689 | 0.007442 | 0.018796 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi | 0.015133 | 0.080000 |
| portfolio | 0.020556 | 0.132000 |
| v15 | 0.019319 | 0.104000 |
| v17 | 0.022164 | 0.132000 |
