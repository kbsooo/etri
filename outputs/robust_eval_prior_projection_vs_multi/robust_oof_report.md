# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v28 | 0.572758 | 0.573636 | 0.002510 | 0.577486 | 4 | 0.002689 | 0.005496 | 0.008835 | 0.012471 | True |
| prior_proj | 0.572758 | 0.573709 | 0.002717 | 0.577482 | 5 | 0.002689 | 0.005339 | 0.008834 | 0.012657 | True |
| v27 | 0.573015 | 0.573845 | 0.002372 | 0.577486 | 4 | 0.002689 | 0.005292 | 0.008577 | 0.012193 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_proj | 0.002689 | 0.008305 | 0.023459 | 0.006924 | 0.007417 | 0.004894 | 0.008152 |
| v27 | 0.002689 | 0.008111 | 0.023459 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |
| v28 | 0.002689 | 0.008451 | 0.024920 | 0.006403 | 0.006975 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| prior_proj | 0.022059 | 0.156000 |
| v27 | 0.021688 | 0.148000 |
| v28 | 0.022648 | 0.148000 |
