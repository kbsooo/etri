# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_tail_full | 0.580692 | 0.584202 | 0.010028 | 0.600462 | 3 | 0.000000 | 0.000136 | 0.000900 | 0.001755 | False |
| qranker_tail_w065 | 0.580839 | 0.584455 | 0.010331 | 0.601243 | 3 | 0.000000 | 0.000178 | 0.000753 | 0.001373 | False |
| tail_q3_support_s4 | 0.581296 | 0.585070 | 0.010784 | 0.602583 | 2 | 0.000000 | 0.000024 | 0.000296 | 0.000579 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_full | 0.000959 | 0.000274 | 0.002800 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| qranker_tail_w065 | 0.000650 | 0.000274 | 0.002077 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| tail_q3_support_s4 | 0.000000 | 0.000000 | 0.001041 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| qranker_tail_full | 0.014087 | 0.080000 |
| qranker_tail_w065 | 0.014488 | 0.080000 |
| tail_q3_support_s4 | 0.015261 | 0.080000 |
