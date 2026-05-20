# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sleep_min3 | 0.583974 | 0.588350 | 0.012503 | 0.608535 | 3 | 0.000000 | -0.000484 | 0.000490 | 0.001469 | False |
| sleep_tiny_blend | 0.584378 | 0.588438 | 0.011603 | 0.607313 | 4 | -0.000000 | -0.000014 | 0.000086 | 0.000187 | False |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sleep_min3 | 0.000000 | 0.000000 | 0.000000 | 0.002306 | 0.000000 | 0.000000 | 0.001121 |
| sleep_tiny_blend | -0.000000 | 0.000000 | 0.000000 | 0.000396 | 0.000000 | 0.000000 | 0.000204 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| sleep_min3 | 0.014969 | 0.080000 |
| sleep_tiny_blend | 0.014488 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
