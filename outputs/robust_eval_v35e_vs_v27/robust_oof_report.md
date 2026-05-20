# Robust OOF diagnostics

- Baseline: `v27`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | 0.570315 | 0.571806 | 0.004262 | 0.577482 | 5 | 0.000107 | 0.001329 | 0.002700 | 0.004060 | True |
| v35a | 0.570663 | 0.572034 | 0.003917 | 0.577482 | 5 | 0.000107 | 0.001006 | 0.002352 | 0.003696 | True |
| v27 | 0.573015 | 0.573845 | 0.002372 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v27 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | 0.003481 | 0.001504 | 0.006460 | 0.003934 | 0.000442 | 0.000107 | 0.000535 |
| v35e | 0.003481 | 0.002638 | 0.007766 | 0.003934 | 0.000442 | 0.000107 | 0.000535 |

## Prediction shift

_No submission files were provided for shift diagnostics._
