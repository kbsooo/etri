# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v21_q3w050_s3w030_s1mid | 0.574597 | 0.575230 | 0.001807 | 0.577486 | 4 | 0.002689 | 0.003725 | 0.006995 | 0.010639 | True |
| v21_q3w030_s3w030_s1mid | 0.574658 | 0.575280 | 0.001775 | 0.577486 | 4 | 0.002689 | 0.003725 | 0.006934 | 0.010571 | True |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 4 | 0.001424 | 0.003081 | 0.005911 | 0.009133 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | 0.002689 | 0.007713 | 0.013539 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| v21_q3w030_s3w030_s1mid | 0.002689 | 0.007713 | 0.015670 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |
| v21_q3w050_s3w030_s1mid | 0.002689 | 0.007713 | 0.016095 | 0.005392 | 0.004672 | 0.004786 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| q3w100 | 0.021103 | 0.132000 |
| v21_q3w030_s3w030_s1mid | 0.020432 | 0.148000 |
| v21_q3w050_s3w030_s1mid | 0.020355 | 0.148000 |
