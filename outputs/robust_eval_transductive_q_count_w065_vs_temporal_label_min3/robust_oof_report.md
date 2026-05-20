# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_w065 | 0.581881 | 0.585756 | 0.011074 | 0.603685 | 4 | 0.000000 | 0.000960 | 0.002583 | 0.004231 | True |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_w065 | 0.002517 | 0.010538 | 0.003917 | 0.000895 | 0.000000 | 0.000000 | 0.000211 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| qcount_w065 | 0.015054 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
