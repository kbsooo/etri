# Robust OOF diagnostics

- Baseline: `prediction_stack_wide`
- Candidate count: 7
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 5 | 0.000000 | 0.002300 | 0.005747 | 0.009385 | True |
| guarded_delta001 | 0.587211 | 0.591255 | 0.011552 | 0.609854 | 5 | 0.000000 | 0.002339 | 0.005712 | 0.009307 | True |
| primary | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.000000 | 0.001647 | 0.004140 | 0.006687 | True |
| label_prior_primary | 0.588783 | 0.593067 | 0.012240 | 0.612043 | 5 | 0.000000 | 0.001647 | 0.004140 | 0.006687 | True |
| logit | 0.588627 | 0.593101 | 0.012782 | 0.613100 | 5 | 0.000000 | 0.001570 | 0.004296 | 0.007160 | True |
| prediction_stack_wide | 0.592923 | 0.597239 | 0.012331 | 0.617225 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| diverse_xgb_latent | 0.626053 | 0.640060 | 0.011553 | 0.639739 | 0 | -0.066424 | -0.041354 | -0.033130 | -0.024719 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| diverse_xgb_latent | -0.037464 | -0.066424 | -0.050548 | -0.007867 | -0.027730 | -0.023867 | -0.018008 |
| guarded | 0.000000 | 0.009228 | 0.000246 | 0.003025 | 0.010922 | 0.009911 | 0.006896 |
| guarded_delta001 | 0.000000 | 0.009228 | 0.000000 | 0.003025 | 0.010922 | 0.009911 | 0.006896 |
| label_prior_primary | 0.000000 | 0.006294 | 0.000000 | 0.000000 | 0.010922 | 0.009911 | 0.001853 |
| logit | 0.000000 | 0.006800 | 0.000246 | 0.000000 | 0.010668 | 0.010172 | 0.002186 |
| prediction_stack_wide | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary | 0.000000 | 0.006294 | 0.000000 | 0.000000 | 0.010922 | 0.009911 | 0.001853 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| diverse_xgb_latent | 0.009799 | 0.000000 |
| guarded | 0.010319 | 0.080000 |
| guarded_delta001 | 0.010379 | 0.080000 |
| label_prior_primary | 0.010079 | 0.080000 |
| logit | 0.009890 | 0.088000 |
| prediction_stack_wide | 0.010898 | 0.076000 |
| primary | 0.010079 | 0.080000 |
