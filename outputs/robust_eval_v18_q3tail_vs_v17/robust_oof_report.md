# Robust OOF diagnostics

- Baseline: `v17`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v18_q3tail | 0.574823 | 0.575553 | 0.002087 | 0.577486 | 1 | 0.000000 | -0.000100 | 0.000147 | 0.000393 | False |
| v17 | 0.574969 | 0.575750 | 0.002230 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v17 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v18_q3tail | 0.000000 | 0.000000 | 0.001028 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v17 | 0.022164 | 0.132000 |
| v18_q3tail | 0.022712 | 0.132000 |
