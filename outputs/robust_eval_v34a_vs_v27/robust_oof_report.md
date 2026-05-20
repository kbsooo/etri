# Robust OOF diagnostics

- Baseline: `v27`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v34a | 0.570913 | 0.572207 | 0.003697 | 0.577482 | 5 | 0.000107 | 0.000796 | 0.002102 | 0.003397 | True |
| v33a | 0.571019 | 0.572287 | 0.003623 | 0.577482 | 5 | 0.000107 | 0.000687 | 0.001997 | 0.003303 | True |
| v27 | 0.573015 | 0.573845 | 0.002372 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v27 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | 0.003481 | 0.001504 | 0.005719 | 0.002187 | 0.000442 | 0.000107 | 0.000535 |
| v34a | 0.003481 | 0.001504 | 0.006460 | 0.002187 | 0.000442 | 0.000107 | 0.000535 |

## Prediction shift

_No submission files were provided for shift diagnostics._
