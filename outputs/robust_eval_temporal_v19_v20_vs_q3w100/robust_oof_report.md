# Robust OOF diagnostics

- Baseline: `q3w100`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v20_q3w050_s3w030 | 0.575164 | 0.575932 | 0.002194 | 0.578006 | 1 | 0.000000 | -0.000158 | 0.000517 | 0.001247 | False |
| v20_q3w030_s3w030 | 0.575225 | 0.575978 | 0.002150 | 0.578006 | 1 | 0.000000 | -0.000069 | 0.000457 | 0.001031 | False |
| v19_q3w030 | 0.575377 | 0.576103 | 0.002072 | 0.578006 | 1 | 0.000000 | -0.000023 | 0.000304 | 0.000663 | False |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v19_q3w030 | 0.000000 | 0.000000 | 0.002131 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v20_q3w030_s3w030 | 0.000000 | 0.000000 | 0.002131 | 0.000000 | 0.000000 | 0.001066 | 0.000000 |
| v20_q3w050_s3w030 | 0.000000 | 0.000000 | 0.002556 | 0.000000 | 0.000000 | 0.001066 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| q3w100 | 0.021103 | 0.132000 |
| v19_q3w030 | 0.021397 | 0.132000 |
| v20_q3w030_s3w030 | 0.021532 | 0.148000 |
| v20_q3w050_s3w030 | 0.021456 | 0.148000 |
