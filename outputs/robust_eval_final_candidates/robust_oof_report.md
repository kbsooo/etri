# Robust OOF diagnostics

- Baseline: `latent_temporal`
- Candidate count: 5
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoothing_min3 | 0.588070 | 0.592045 | 0.011359 | 0.609775 | 5 | 0.010716 | 0.018713 | 0.024543 | 0.030407 | True |
| temporal_smoothing | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.008675 | 0.018023 | 0.023830 | 0.029532 | True |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 5 | 0.007109 | 0.013329 | 0.019690 | 0.026295 | True |
| graph_variant | 0.602485 | 0.605730 | 0.009273 | 0.617895 | 5 | 0.004777 | 0.005357 | 0.010128 | 0.014898 | True |
| latent_temporal | 0.612613 | 0.616651 | 0.011538 | 0.631994 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_variant | 0.008690 | 0.006638 | 0.008318 | 0.008675 | 0.007109 | 0.004777 | 0.026693 |
| latent_temporal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prediction_stack_wide | 0.008690 | 0.027098 | 0.036015 | 0.008675 | 0.007109 | 0.021749 | 0.028495 |
| smoothing_min3 | 0.010716 | 0.033393 | 0.036162 | 0.011494 | 0.018031 | 0.031660 | 0.030347 |
| temporal_smoothing | 0.008690 | 0.033393 | 0.036015 | 0.008675 | 0.018031 | 0.031660 | 0.030347 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_variant | 0.010225 | 0.028000 |
| latent_temporal | 0.009483 | 0.000000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| smoothing_min3 | 0.009965 | 0.080000 |
| temporal_smoothing | 0.010079 | 0.080000 |
