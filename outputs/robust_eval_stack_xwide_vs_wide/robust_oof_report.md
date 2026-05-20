# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prediction_stack_xwide | 0.592416 | 0.596931 | 0.012902 | 0.617238 | 3 | 0.000000 | -0.002115 | 0.000507 | 0.003022 | False |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| prediction_stack_qcal | 0.596392 | 0.601780 | 0.011102 | 0.617705 | 0 | -0.010016 | -0.006196 | -0.003469 | -0.000557 | False |
| graph_variant | 0.602485 | 0.609885 | 0.009273 | 0.617895 | 0 | -0.027697 | -0.014256 | -0.009562 | -0.004846 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_variant | 0.000000 | -0.020461 | -0.027697 | 0.000000 | 0.000000 | -0.016973 | -0.001801 |
| prediction_stack_qcal | 0.000000 | -0.004277 | -0.009353 | 0.000000 | 0.000000 | -0.010016 | -0.000635 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prediction_stack_xwide | 0.000000 | 0.000418 | 0.001090 | 0.000000 | 0.000000 | 0.001975 | 0.000069 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_variant | 0.010225 | 0.028000 |
| prediction_stack_qcal | 0.009884 | 0.028000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| prediction_stack_xwide | 0.010534 | 0.068000 |
