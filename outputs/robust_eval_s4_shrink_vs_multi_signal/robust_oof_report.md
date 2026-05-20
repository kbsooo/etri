# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s4w100 | 0.581519 | 0.585400 | 0.011087 | 0.603462 | 3 | 0.000000 | -0.000375 | 0.000073 | 0.000535 | False |
| s4w080 | 0.581519 | 0.585404 | 0.011100 | 0.603463 | 3 | 0.000000 | -0.000285 | 0.000074 | 0.000442 | False |
| s4w065 | 0.581523 | 0.585412 | 0.011111 | 0.603469 | 3 | 0.000000 | -0.000222 | 0.000069 | 0.000368 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| s4w065 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000485 |
| s4w080 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000516 |
| s4w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000511 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| s4w065 | 0.015085 | 0.080000 |
| s4w080 | 0.015075 | 0.080000 |
| s4w100 | 0.015061 | 0.080000 |
