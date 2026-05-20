# Robust OOF diagnostics

- Baseline: `v34a`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stack | 0.567602 | 0.568901 | 0.003711 | 0.572749 | 4 | 0.000000 | 0.001788 | 0.003310 | 0.004797 | True |
| v34a | 0.570913 | 0.572207 | 0.003697 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| stack | 0.001765 | 0.015883 | 0.004601 | 0.000611 | 0.000000 | 0.000000 | 0.000311 |
| v34a | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

_No submission files were provided for shift diagnostics._
