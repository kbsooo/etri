# Robust OOF diagnostics

- Baseline: `qcount`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 4 | 0.000020 | 0.000009 | 0.000259 | 0.000502 | True |
| minimax_positive_tail | 0.581830 | 0.585694 | 0.011043 | 0.603543 | 5 | 0.000005 | 0.000005 | 0.000022 | 0.000039 | True |
| qcount | 0.581851 | 0.585713 | 0.011035 | 0.603548 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| minimax_positive_tail | 0.000042 | 0.000040 | 0.000015 | 0.000022 | 0.000011 | 0.000005 | 0.000017 |
| multi_signal | 0.000375 | 0.000224 | 0.000086 | 0.000405 | 0.000200 | 0.000020 | 0.000501 |
| qcount | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| minimax_positive_tail | 0.015085 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
| qcount | 0.015083 | 0.080000 |
