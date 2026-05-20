# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v6 | 0.578528 | 0.580813 | 0.006528 | 0.591103 | 3 | 0.001034 | 0.001152 | 0.003064 | 0.005158 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v6 | 0.002689 | 0.003755 | 0.010078 | 0.001235 | 0.001399 | 0.001257 | 0.001034 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| hgb_tail_decoder_v6 | 0.017245 | 0.076000 |
| multi_signal | 0.015133 | 0.080000 |
