# Robust OOF diagnostics

- Baseline: `temporal_smoothing`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoothing_min3 | 0.588070 | 0.592045 | 0.011359 | 0.609775 | 3 | 0.000000 | -0.000699 | 0.000713 | 0.002188 | False |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| logit_smoothing | 0.588627 | 0.593139 | 0.012782 | 0.613100 | 3 | -0.000255 | -0.000459 | 0.000156 | 0.000768 | False |
| logit_noself | 0.590040 | 0.596173 | 0.013273 | 0.616008 | 2 | -0.009911 | -0.002966 | -0.001257 | 0.000437 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| logit_noself | 0.000000 | 0.000464 | 0.000000 | 0.000000 | 0.000260 | -0.009911 | 0.000385 |
| logit_smoothing | 0.000000 | 0.000506 | 0.000246 | 0.000000 | -0.000255 | 0.000261 | 0.000333 |
| smoothing_min3 | 0.002026 | 0.000000 | 0.000147 | 0.002819 | 0.000000 | 0.000000 | 0.000000 |
| temporal_smoothing | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| logit_noself | 0.010006 | 0.076000 |
| logit_smoothing | 0.009890 | 0.088000 |
| smoothing_min3 | 0.009965 | 0.080000 |
| temporal_smoothing | 0.010079 | 0.080000 |
