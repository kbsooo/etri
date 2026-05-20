# Robust OOF diagnostics

- Baseline: `trp_base`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trp_plus_gru28_s3tail_w100 | 0.574138 | 0.575052 | 0.002613 | 0.577486 | 1 | 0.000000 | -0.000042 | 0.000090 | 0.000264 | False |
| trp_base | 0.574228 | 0.575172 | 0.002699 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000630 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| trp_base | 0.021772 | 0.112000 |
| trp_plus_gru28_s3tail_w100 | 0.020976 | 0.100000 |
