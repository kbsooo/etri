# Robust OOF diagnostics

- Baseline: `trp_base`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weather_s4midtail_w030 | 0.573799 | 0.574702 | 0.002582 | 0.577486 | 3 | 0.000000 | -0.000357 | 0.000429 | 0.001194 | False |
| weather_s4tail_w050 | 0.573964 | 0.574833 | 0.002481 | 0.577486 | 1 | 0.000000 | -0.000212 | 0.000264 | 0.000761 | False |
| trp_base | 0.574228 | 0.575172 | 0.002699 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4midtail_w030 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.003003 |
| weather_s4tail_w050 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001845 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| trp_base | 0.021772 | 0.112000 |
| weather_s4midtail_w030 | 0.020760 | 0.112000 |
| weather_s4tail_w050 | 0.020771 | 0.112000 |
