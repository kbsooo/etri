# Robust OOF diagnostics

- Baseline: `graph_sleep_blend`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_min3 | 0.585999 | 0.590051 | 0.011579 | 0.608460 | 2 | 0.000000 | -0.000464 | 0.000098 | 0.000646 | False |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_min3 | 0.000000 | 0.000000 | 0.000000 | 0.000349 | 0.000237 | 0.000000 | 0.000099 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| prior_min3 | 0.010069 | 0.080000 |
