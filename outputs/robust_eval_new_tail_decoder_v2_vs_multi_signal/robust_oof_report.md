# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| new_tail_decoder_v2 | 0.579118 | 0.581699 | 0.007373 | 0.593422 | 3 | 0.000000 | 0.000817 | 0.002474 | 0.004240 | False |
| new_q3tail_combo | 0.579709 | 0.582735 | 0.008646 | 0.596695 | 3 | 0.000000 | 0.000583 | 0.001883 | 0.003225 | False |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.584545 | 0.010814 | 0.602258 | 3 | 0.000000 | 0.000277 | 0.000832 | 0.001417 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| new_q3tail_combo | 0.001897 | 0.000274 | 0.008741 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| new_tail_decoder_v2 | 0.001897 | 0.003462 | 0.008741 | 0.001235 | 0.000000 | 0.000950 | 0.001034 |
| oldbalanced_plus_q1fastmid | 0.002209 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| new_q3tail_combo | 0.019905 | 0.080000 |
| new_tail_decoder_v2 | 0.021174 | 0.080000 |
| oldbalanced_plus_q1fastmid | 0.014942 | 0.080000 |
