# Robust OOF diagnostics

- Baseline: `temporal_smoothing`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_smoothed | 0.588598 | 0.592934 | 0.012390 | 0.612092 | 4 | 0.000000 | -0.000075 | 0.000185 | 0.000440 | False |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| smooth_xwide | 0.588932 | 0.593880 | 0.013135 | 0.613693 | 2 | -0.002339 | -0.001965 | -0.000149 | 0.001598 | False |
| prediction_stack_wide | 0.592923 | 0.598877 | 0.012331 | 0.617225 | 0 | -0.010922 | -0.006687 | -0.004140 | -0.001647 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prediction_stack_wide | 0.000000 | -0.006294 | 0.000000 | 0.000000 | -0.010922 | -0.009911 | -0.001853 |
| smooth_xwide | 0.000000 | 0.000078 | 0.001090 | 0.000000 | 0.000000 | -0.002339 | 0.000126 |
| targetwise_smoothed | 0.000000 | 0.000078 | 0.001090 | 0.000000 | 0.000000 | 0.000000 | 0.000126 |
| temporal_smoothing | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| prediction_stack_wide | 0.010898 | 0.076000 |
| smooth_xwide | 0.009624 | 0.052000 |
| targetwise_smoothed | 0.009963 | 0.080000 |
| temporal_smoothing | 0.010079 | 0.080000 |
