# Robust OOF diagnostics

- Baseline: `v35a`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | 0.570315 | 0.571806 | 0.004262 | 0.577482 | 2 | 0.000000 | 0.000012 | 0.000349 | 0.000684 | False |
| v35a | 0.570663 | 0.572034 | 0.003917 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35a | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | 0.000000 | 0.001134 | 0.001306 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

_No submission files were provided for shift diagnostics._
