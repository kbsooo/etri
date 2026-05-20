# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.584545 | 0.010814 | 0.602258 | 3 | 0.000000 | 0.000281 | 0.000832 | 0.001419 | False |
| old_balanced_w030 | 0.581031 | 0.584785 | 0.010726 | 0.602258 | 3 | 0.000000 | 0.000160 | 0.000561 | 0.000971 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| old_balanced_w030 | 0.000312 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| oldbalanced_plus_q1fastmid | 0.002209 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| old_balanced_w030 | 0.014821 | 0.080000 |
| oldbalanced_plus_q1fastmid | 0.014942 | 0.080000 |
