# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 5
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| with_forward_relaxed | 0.574825 | 0.575366 | 0.001546 | 0.576822 | 4 | 0.001424 | 0.003722 | 0.006767 | 0.010013 | True |
| with_forward_safe | 0.575454 | 0.576156 | 0.002007 | 0.577666 | 4 | 0.001424 | 0.003485 | 0.006139 | 0.009028 | True |
| portfolio_v17_robust | 0.575829 | 0.576574 | 0.002131 | 0.578006 | 4 | 0.001424 | 0.002968 | 0.005764 | 0.008892 | True |
| v17 | 0.574969 | 0.575750 | 0.002230 | 0.577486 | 3 | 0.001424 | 0.003445 | 0.006623 | 0.010082 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| portfolio_v17_robust | 0.002689 | 0.007713 | 0.012511 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| v17 | 0.002689 | 0.007442 | 0.018796 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| with_forward_relaxed | 0.009711 | 0.007713 | 0.012511 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| with_forward_safe | 0.007278 | 0.007226 | 0.011033 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| portfolio_v17_robust | 0.020556 | 0.132000 |
| v17 | 0.022164 | 0.132000 |
| with_forward_relaxed | 0.021931 | 0.132000 |
| with_forward_safe | 0.020495 | 0.132000 |
