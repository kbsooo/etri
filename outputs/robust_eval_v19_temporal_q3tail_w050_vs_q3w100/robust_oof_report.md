# Robust OOF diagnostics

- Baseline: `q3w100`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v19_temporal_q3tail_w050 | 0.575317 | 0.576051 | 0.002098 | 0.578006 | 1 | 0.000000 | -0.000157 | 0.000365 | 0.000910 | False |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v19_temporal_q3tail_w050 | 0.000000 | 0.000000 | 0.002556 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| q3w100 | 0.021103 | 0.132000 |
| v19_temporal_q3tail_w050 | 0.021320 | 0.132000 |
