# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v19_temporal_q3tail_w050 | 0.575317 | 0.576051 | 0.002098 | 0.578006 | 4 | 0.001424 | 0.003276 | 0.006276 | 0.009684 | True |
| q3w100 | 0.575682 | 0.576404 | 0.002064 | 0.578006 | 4 | 0.001424 | 0.003081 | 0.005911 | 0.009133 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | 0.002689 | 0.007713 | 0.013539 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |
| v19_temporal_q3tail_w050 | 0.002689 | 0.007713 | 0.016095 | 0.001424 | 0.004672 | 0.003721 | 0.007617 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| q3w100 | 0.021103 | 0.132000 |
| v19_temporal_q3tail_w050 | 0.021320 | 0.132000 |
