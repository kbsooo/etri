# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_tiny_blend | 0.584410 | 0.588455 | 0.011558 | 0.607269 | 5 | 0.000385 | 0.000972 | 0.002766 | 0.004579 | True |
| graph_sleep_temporal_label_min3 | 0.584463 | 0.588489 | 0.011502 | 0.607213 | 5 | 0.000385 | 0.000932 | 0.002713 | 0.004505 | True |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_temporal_label_min3 | 0.000385 | 0.000503 | 0.001051 | 0.002612 | 0.010330 | 0.001549 | 0.002560 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| targetwise_tiny_blend | 0.000385 | 0.000503 | 0.001051 | 0.002815 | 0.010396 | 0.001549 | 0.002664 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_temporal_label_min3 | 0.014434 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| targetwise_tiny_blend | 0.014510 | 0.080000 |
