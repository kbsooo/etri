# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v5 | 0.578640 | 0.580918 | 0.006510 | 0.591103 | 3 | 0.000620 | 0.001074 | 0.002953 | 0.005087 | False |
| hgb_tail_decoder_v4 | 0.578841 | 0.581227 | 0.006816 | 0.591957 | 3 | 0.000000 | 0.000962 | 0.002751 | 0.004739 | False |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.584545 | 0.010814 | 0.602258 | 3 | 0.000000 | 0.000277 | 0.000832 | 0.001417 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v4 | 0.001897 | 0.003755 | 0.010078 | 0.001235 | 0.000000 | 0.001257 | 0.001034 |
| hgb_tail_decoder_v5 | 0.002689 | 0.003755 | 0.010078 | 0.001235 | 0.000620 | 0.001257 | 0.001034 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| oldbalanced_plus_q1fastmid | 0.002209 | 0.000274 | 0.001073 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| hgb_tail_decoder_v4 | 0.019262 | 0.076000 |
| hgb_tail_decoder_v5 | 0.017284 | 0.076000 |
| multi_signal | 0.015133 | 0.080000 |
| oldbalanced_plus_q1fastmid | 0.014942 | 0.080000 |
