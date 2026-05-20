# Robust OOF diagnostics

- Baseline: `v13b`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v14 | 0.576224 | 0.577714 | 0.004256 | 0.583918 | 3 | 0.000000 | 0.000003 | 0.000151 | 0.000301 | False |
| v13b | 0.576376 | 0.577924 | 0.004424 | 0.584461 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v13b | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v14 | 0.000000 | 0.000000 | 0.000000 | 0.000188 | 0.000360 | 0.000298 | 0.000213 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v13b | 0.017886 | 0.096000 |
| v14 | 0.018342 | 0.104000 |
