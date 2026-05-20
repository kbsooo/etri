# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aggressive_w065 | 0.580839 | 0.584455 | 0.010331 | 0.601243 | 3 | 0.000000 | 0.000178 | 0.000753 | 0.001373 | False |
| q3old_q1fast | 0.580805 | 0.584622 | 0.010907 | 0.602494 | 3 | 0.000000 | 0.000235 | 0.000788 | 0.001377 | False |
| old_balanced_w030 | 0.581031 | 0.584785 | 0.010726 | 0.602258 | 3 | 0.000000 | 0.000160 | 0.000561 | 0.000971 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| aggressive_w065 | 0.000650 | 0.000274 | 0.002077 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| old_balanced_w030 | 0.000312 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| q3old_q1fast | 0.001897 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| aggressive_w065 | 0.014488 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
| old_balanced_w030 | 0.014821 | 0.080000 |
| q3old_q1fast | 0.015359 | 0.080000 |
