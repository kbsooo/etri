# Robust OOF diagnostics

- Baseline: `v35e`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v38a | 0.549791 | 0.551602 | 0.005176 | 0.555440 | 5 | 0.006464 | 0.013942 | 0.020524 | 0.027011 | True |
| v35e | 0.570315 | 0.571806 | 0.004262 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v38a | 0.024062 | 0.045598 | 0.024043 | 0.006464 | 0.011580 | 0.015691 | 0.016229 |

## Prediction shift

_No submission files were provided for shift diagnostics._
