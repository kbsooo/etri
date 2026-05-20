# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_guarded | 0.586921 | 0.590855 | 0.011240 | 0.608883 | 4 | 0.000000 | -0.000438 | 0.000255 | 0.000934 | False |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| smoothing_min3 | 0.588070 | 0.592802 | 0.011359 | 0.609775 | 1 | -0.005043 | -0.002642 | -0.000894 | 0.000819 | False |
| primary | 0.588783 | 0.593823 | 0.012240 | 0.612043 | 1 | -0.005043 | -0.003647 | -0.001607 | 0.000424 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_guarded | 0.000000 | 0.000924 | 0.000000 | 0.000000 | 0.000000 | 0.000861 | 0.000000 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary | 0.000000 | -0.002934 | -0.000246 | -0.003025 | 0.000000 | 0.000000 | -0.005043 |
| smoothing_min3 | 0.002026 | -0.002934 | -0.000099 | -0.000206 | 0.000000 | 0.000000 | -0.005043 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_guarded | 0.010061 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| primary | 0.010079 | 0.080000 |
| smoothing_min3 | 0.009965 | 0.080000 |
