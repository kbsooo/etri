# Robust OOF diagnostics

- Baseline: `prediction_stack_qcal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_stack | 0.595953 | 0.600160 | 0.012020 | 0.618617 | 3 | 0.000000 | -0.000696 | 0.000439 | 0.001583 | False |
| prediction_stack_qcal | 0.596392 | 0.600278 | 0.011102 | 0.617705 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| graph_variant | 0.602485 | 0.608482 | 0.009273 | 0.617895 | 0 | -0.018344 | -0.010421 | -0.006093 | -0.001776 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_variant | 0.000000 | -0.016184 | -0.018344 | 0.000000 | 0.000000 | -0.006956 | -0.001166 |
| prediction_stack_qcal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| targetwise_stack | 0.000000 | 0.000000 | 0.001439 | 0.000000 | 0.000000 | 0.001217 | 0.000415 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_variant | 0.010225 | 0.028000 |
| prediction_stack_qcal | 0.009884 | 0.028000 |
| targetwise_stack | 0.009661 | 0.028000 |
