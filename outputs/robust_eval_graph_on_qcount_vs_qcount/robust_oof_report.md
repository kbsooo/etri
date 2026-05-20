# Robust OOF diagnostics

- Baseline: `block_aware_qcount`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_on_qcount_min3 | 0.581834 | 0.585664 | 0.010944 | 0.603334 | 2 | 0.000000 | -0.000181 | 0.000018 | 0.000225 | False |
| block_aware_qcount | 0.581851 | 0.585713 | 0.011035 | 0.603548 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_on_qcount_min3 | 0.000000 | 0.000000 | 0.000000 | 0.000021 | 0.000000 | 0.000102 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| block_aware_qcount | 0.015083 | 0.080000 |
| graph_on_qcount_min3 | 0.015009 | 0.084000 |
