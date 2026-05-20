# Robust OOF diagnostics

- Baseline: `temporal_smoothing`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoothing_min3 | 0.588070 | 0.592045 | 0.011359 | 0.609775 | 3 | 0.000000 | -0.000699 | 0.000713 | 0.002188 | False |
| targetwise_smoothed | 0.588598 | 0.592934 | 0.012390 | 0.612092 | 4 | 0.000000 | -0.000075 | 0.000185 | 0.000440 | False |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| smoothing_min3 | 0.002026 | 0.000000 | 0.000147 | 0.002819 | 0.000000 | 0.000000 | 0.000000 |
| targetwise_smoothed | 0.000000 | 0.000078 | 0.001090 | 0.000000 | 0.000000 | 0.000000 | 0.000126 |
| temporal_smoothing | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| smoothing_min3 | 0.009965 | 0.080000 |
| targetwise_smoothed | 0.009963 | 0.080000 |
| temporal_smoothing | 0.010079 | 0.080000 |
