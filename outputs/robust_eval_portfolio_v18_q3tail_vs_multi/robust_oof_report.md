# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| portfolio_q3tail | 0.575700 | 0.576425 | 0.002070 | 0.578006 | 4 | 0.001424 | 0.003080 | 0.005892 | 0.009102 | True |
| robust_portfolio | 0.575829 | 0.576574 | 0.002131 | 0.578006 | 4 | 0.001424 | 0.002993 | 0.005764 | 0.008898 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| portfolio_q3tail | 0.002689 | 0.007713 | 0.013407 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| robust_portfolio | 0.002689 | 0.007713 | 0.012511 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| portfolio_q3tail | 0.021016 | 0.132000 |
| robust_portfolio | 0.020556 | 0.132000 |
