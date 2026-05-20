# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_graph_w04 | 0.586443 | 0.590394 | 0.011288 | 0.608518 | 5 | 0.000357 | 0.003165 | 0.006480 | 0.009917 | True |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 5 | 0.000000 | 0.002300 | 0.005747 | 0.009385 | True |
| primary | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.000000 | 0.001647 | 0.004140 | 0.006687 | True |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| blend_graph_w04 | 0.000357 | 0.009732 | 0.000795 | 0.003599 | 0.011807 | 0.010448 | 0.008624 |
| guarded | 0.000000 | 0.009228 | 0.000246 | 0.003025 | 0.010922 | 0.009911 | 0.006896 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary | 0.000000 | 0.006294 | 0.000000 | 0.000000 | 0.010922 | 0.009911 | 0.001853 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| blend_graph_w04 | 0.009715 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| primary | 0.010079 | 0.080000 |
