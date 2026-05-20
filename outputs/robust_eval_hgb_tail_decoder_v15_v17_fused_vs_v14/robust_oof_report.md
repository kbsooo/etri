# Robust OOF diagnostics

- Baseline: `v14`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v17_s4s3q2 | 0.574969 | 0.575750 | 0.002230 | 0.577486 | 1 | 0.000000 | 0.000197 | 0.001255 | 0.002464 | False |
| v15_s4 | 0.575529 | 0.576583 | 0.003014 | 0.580234 | 1 | 0.000000 | 0.000092 | 0.000696 | 0.001393 | False |
| v14 | 0.576224 | 0.577714 | 0.004256 | 0.583918 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v14 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v15_s4 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.004871 |
| v17_s4s3q2 | 0.000000 | 0.001749 | 0.000000 | 0.000000 | 0.000000 | 0.002166 | 0.004871 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| v14 | 0.018342 | 0.104000 |
| v15_s4 | 0.019319 | 0.104000 |
| v17_s4s3q2 | 0.022164 | 0.132000 |
