# Robust OOF diagnostics

- Baseline: `primary_w03`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_w065 | 0.581881 | 0.585756 | 0.011074 | 0.603685 | 4 | 0.000000 | 0.000455 | 0.001917 | 0.003388 | True |
| qcount_w05 | 0.582178 | 0.586063 | 0.011099 | 0.604077 | 4 | 0.000000 | 0.000488 | 0.001620 | 0.002758 | True |
| primary_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_w05 | 0.001296 | 0.008940 | 0.001102 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_w065 | 0.001536 | 0.010538 | 0.001347 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| primary_w03 | 0.014490 | 0.080000 |
| qcount_w05 | 0.014924 | 0.080000 |
| qcount_w065 | 0.015054 | 0.080000 |
