# Robust OOF diagnostics

- Baseline: `trp_base`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weather_s4tail_plus_gru_s3tail | 0.573874 | 0.574725 | 0.002432 | 0.577486 | 1 | 0.000000 | -0.000139 | 0.000354 | 0.000888 | False |
| weather_s4tail_w050 | 0.573964 | 0.574833 | 0.002481 | 0.577486 | 1 | 0.000000 | -0.000212 | 0.000264 | 0.000761 | False |
| trp_base | 0.574228 | 0.575172 | 0.002699 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000630 | 0.001845 |
| weather_s4tail_w050 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001845 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| trp_base | 0.021772 | 0.112000 |
| weather_s4tail_plus_gru_s3tail | 0.019975 | 0.100000 |
| weather_s4tail_w050 | 0.020771 | 0.112000 |
