# Robust OOF diagnostics

- Baseline: `primary_w03`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | 0.581851 | 0.585713 | 0.011035 | 0.603548 | 4 | 0.000000 | 0.000451 | 0.001947 | 0.003449 | True |
| qcount_w065 | 0.581881 | 0.585756 | 0.011074 | 0.603685 | 4 | 0.000000 | 0.000455 | 0.001917 | 0.003388 | True |
| primary_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | 0.001536 | 0.010538 | 0.001553 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_w065 | 0.001536 | 0.010538 | 0.001347 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| block_aware_qcount | 0.015083 | 0.080000 |
| primary_w03 | 0.014490 | 0.080000 |
| qcount_w065 | 0.015054 | 0.080000 |
