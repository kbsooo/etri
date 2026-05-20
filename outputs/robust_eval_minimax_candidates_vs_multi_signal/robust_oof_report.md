# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| minimax_current_pool | 0.581327 | 0.585379 | 0.011579 | 0.604115 | 4 | 0.000028 | -0.000111 | 0.000266 | 0.000640 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| minimax_positive_tail | 0.581830 | 0.585767 | 0.011043 | 0.603543 | 2 | -0.000485 | -0.000475 | -0.000237 | 0.000009 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| minimax_current_pool | 0.000075 | 0.000078 | 0.000053 | 0.000696 | 0.000884 | 0.000046 | 0.000028 |
| minimax_positive_tail | -0.000334 | -0.000184 | -0.000071 | -0.000383 | -0.000189 | -0.000014 | -0.000485 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| minimax_current_pool | 0.016091 | 0.084000 |
| minimax_positive_tail | 0.015085 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
