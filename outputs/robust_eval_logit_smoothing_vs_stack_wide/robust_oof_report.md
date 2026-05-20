# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.000000 | 0.001647 | 0.004140 | 0.006687 | True |
| logit_smoothing | 0.588627 | 0.593101 | 0.012782 | 0.613100 | 5 | 0.000000 | 0.001570 | 0.004296 | 0.007160 | True |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| logit_smoothing | 0.000000 | 0.006800 | 0.000246 | 0.000000 | 0.010668 | 0.010172 | 0.002186 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_smoothing | 0.000000 | 0.006294 | 0.000000 | 0.000000 | 0.010922 | 0.009911 | 0.001853 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| logit_smoothing | 0.009890 | 0.088000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| temporal_smoothing | 0.010079 | 0.080000 |
