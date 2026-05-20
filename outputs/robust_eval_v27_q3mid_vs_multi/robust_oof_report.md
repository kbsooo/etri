# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v27_q3mid_w100 | 0.572806 | 0.573674 | 0.002479 | 0.577486 | 4 | 0.002689 | 0.005428 | 0.008786 | 0.012435 | True |
| v27_q3mid_w050 | 0.573139 | 0.573951 | 0.002320 | 0.577486 | 4 | 0.002689 | 0.005194 | 0.008454 | 0.012044 | True |
| v25 | 0.573704 | 0.574478 | 0.002210 | 0.577486 | 4 | 0.002689 | 0.004684 | 0.007888 | 0.011455 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v25 | 0.002689 | 0.008111 | 0.018634 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |
| v27_q3mid_w050 | 0.002689 | 0.008111 | 0.022594 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |
| v27_q3mid_w100 | 0.002689 | 0.008111 | 0.024920 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| v25 | 0.021236 | 0.148000 |
| v27_q3mid_w050 | 0.021591 | 0.148000 |
| v27_q3mid_w100 | 0.021898 | 0.148000 |
