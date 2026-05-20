# Robust OOF diagnostics

- Baseline: `q3w100`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v21_q3w050_s3w030_s1mid | 0.574597 | 0.575230 | 0.001807 | 0.577486 | 3 | 0.000000 | 0.000065 | 0.001084 | 0.002110 | False |
| v21_q3w030_s3w030_s1mid | 0.574658 | 0.575280 | 0.001775 | 0.577486 | 3 | 0.000000 | 0.000095 | 0.001024 | 0.001952 | False |
| v20_q3w050_s3w030 | 0.575164 | 0.575932 | 0.002194 | 0.578006 | 1 | 0.000000 | -0.000158 | 0.000517 | 0.001247 | False |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v20_q3w050_s3w030 | 0.000000 | 0.000000 | 0.002556 | 0.000000 | 0.000000 | 0.001066 | 0.000000 |
| v21_q3w030_s3w030_s1mid | 0.000000 | 0.000000 | 0.002131 | 0.003968 | 0.000000 | 0.001066 | 0.000000 |
| v21_q3w050_s3w030_s1mid | 0.000000 | 0.000000 | 0.002556 | 0.003968 | 0.000000 | 0.001066 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| q3w100 | 0.021103 | 0.132000 |
| v20_q3w050_s3w030 | 0.021456 | 0.148000 |
| v21_q3w030_s3w030_s1mid | 0.020432 | 0.148000 |
| v21_q3w050_s3w030_s1mid | 0.020355 | 0.148000 |
