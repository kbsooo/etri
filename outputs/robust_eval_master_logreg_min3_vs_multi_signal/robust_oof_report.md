# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_logreg_min3 | 0.580974 | 0.585110 | 0.011815 | 0.603985 | 3 | 0.000000 | -0.000647 | 0.000618 | 0.001878 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| master_logreg_min3 | 0.001783 | 0.000000 | 0.001434 | 0.000874 | 0.000000 | 0.000000 | 0.000234 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| master_logreg_min3 | 0.015757 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
