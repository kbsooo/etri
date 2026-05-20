# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_on_stack_wide | 0.591979 | 0.596081 | 0.011722 | 0.615092 | 3 | 0.000203 | -0.000519 | 0.000944 | 0.002395 | False |
| graph_on_stack_wide_min4 | 0.592512 | 0.596680 | 0.011908 | 0.615930 | 4 | 0.000000 | -0.000605 | 0.000411 | 0.001411 | False |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_on_stack_wide | 0.000653 | 0.000203 | 0.001129 | 0.000291 | 0.001456 | 0.002106 | 0.000774 |
| graph_on_stack_wide_min4 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.002106 | 0.000774 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_on_stack_wide | 0.009710 | 0.080000 |
| graph_on_stack_wide_min4 | 0.010549 | 0.080000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
