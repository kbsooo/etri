# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label | 0.592276 | 0.596286 | 0.011456 | 0.615061 | 3 | 0.000000 | -0.000790 | 0.000647 | 0.002141 | False |
| prediction_stack_xwide | 0.592416 | 0.596931 | 0.012902 | 0.617238 | 3 | 0.000000 | -0.002115 | 0.000507 | 0.003022 | False |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prediction_stack_xwide | 0.000000 | 0.000418 | 0.001090 | 0.000000 | 0.000000 | 0.001975 | 0.000069 |
| temporal_label | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.004288 | 0.000000 | 0.000242 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| prediction_stack_wide | 0.010898 | 0.076000 |
| prediction_stack_xwide | 0.010534 | 0.068000 |
| temporal_label | 0.013383 | 0.076000 |
