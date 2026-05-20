# Robust OOF diagnostics

- Baseline: `v35a`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v35b_q3w1 | 0.570477 | 0.571909 | 0.004092 | 0.577482 | 2 | 0.000000 | -0.000040 | 0.000187 | 0.000414 | False |
| v35d_q2w05 | 0.570501 | 0.571928 | 0.004077 | 0.577482 | 2 | 0.000000 | -0.000071 | 0.000162 | 0.000389 | False |
| v35c_q3w05 | 0.570564 | 0.571967 | 0.004008 | 0.577482 | 2 | 0.000000 | -0.000015 | 0.000099 | 0.000213 | False |
| v35a | 0.570663 | 0.572034 | 0.003917 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35a | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35b_q3w1 | 0.000000 | 0.000000 | 0.001306 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35c_q3w05 | 0.000000 | 0.000000 | 0.000690 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35d_q2w05 | 0.000000 | 0.001134 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

_No submission files were provided for shift diagnostics._
