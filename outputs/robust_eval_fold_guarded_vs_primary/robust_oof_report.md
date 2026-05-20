# Robust OOF diagnostics

- Baseline: `primary`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 4 | 0.000000 | -0.000424 | 0.001607 | 0.003647 | False |
| guarded_delta001 | 0.587211 | 0.591255 | 0.011552 | 0.609854 | 4 | 0.000000 | -0.000446 | 0.001572 | 0.003616 | False |
| primary | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| logit | 0.588627 | 0.593139 | 0.012782 | 0.613100 | 3 | -0.000255 | -0.000459 | 0.000156 | 0.000768 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guarded | 0.000000 | 0.002934 | 0.000246 | 0.003025 | 0.000000 | 0.000000 | 0.005043 |
| guarded_delta001 | 0.000000 | 0.002934 | 0.000000 | 0.003025 | 0.000000 | 0.000000 | 0.005043 |
| logit | 0.000000 | 0.000506 | 0.000246 | 0.000000 | -0.000255 | 0.000261 | 0.000333 |
| primary | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| guarded | 0.010319 | 0.080000 |
| guarded_delta001 | 0.010379 | 0.080000 |
| logit | 0.009890 | 0.088000 |
| primary | 0.010079 | 0.080000 |
