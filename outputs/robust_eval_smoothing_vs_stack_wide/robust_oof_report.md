# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.000000 | 0.001647 | 0.004140 | 0.006687 | True |
| graph_on_stack_wide | 0.591979 | 0.596081 | 0.011722 | 0.615092 | 3 | 0.000203 | -0.000519 | 0.000944 | 0.002395 | False |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_on_stack_wide | 0.000653 | 0.000203 | 0.001129 | 0.000291 | 0.001456 | 0.002106 | 0.000774 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_smoothing | 0.000000 | 0.006294 | 0.000000 | 0.000000 | 0.010922 | 0.009911 | 0.001853 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_on_stack_wide | 0.009710 | 0.080000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| temporal_smoothing | 0.010079 | 0.080000 |
