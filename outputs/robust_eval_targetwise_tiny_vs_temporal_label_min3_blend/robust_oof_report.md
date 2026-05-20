# Robust OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_tiny_blend | 0.584410 | 0.588455 | 0.011558 | 0.607269 | 4 | -0.000000 | 0.000001 | 0.000053 | 0.000106 | True |
| targetwise_raw | 0.583819 | 0.588247 | 0.012653 | 0.608759 | 4 | 0.000000 | -0.000395 | 0.000644 | 0.001673 | False |
| temporal_label_min3_blend | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_raw | 0.000000 | 0.000000 | 0.000000 | 0.002306 | 0.001084 | 0.000000 | 0.001121 |
| targetwise_tiny_blend | -0.000000 | 0.000000 | 0.000000 | 0.000203 | 0.000066 | 0.000000 | 0.000105 |
| temporal_label_min3_blend | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| targetwise_raw | 0.015950 | 0.080000 |
| targetwise_tiny_blend | 0.014510 | 0.080000 |
| temporal_label_min3_blend | 0.014434 | 0.080000 |
