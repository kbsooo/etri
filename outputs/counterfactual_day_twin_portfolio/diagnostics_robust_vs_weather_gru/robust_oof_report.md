# Robust OOF diagnostics

- Baseline: `weather_gru_base`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dae_q1tail_w050 | 0.573732 | 0.574566 | 0.002383 | 0.577486 | 1 | 0.000000 | -0.000217 | 0.000143 | 0.000516 | False |
| dae_q1tail_w030 | 0.573773 | 0.574610 | 0.002393 | 0.577486 | 1 | 0.000000 | -0.000117 | 0.000102 | 0.000333 | False |
| weather_gru_base | 0.573874 | 0.574725 | 0.002432 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dae_q1tail_w030 | 0.000711 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dae_q1tail_w050 | 0.000998 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_gru_base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| dae_q1tail_w030 | 0.021121 | 0.100000 |
| dae_q1tail_w050 | 0.021835 | 0.100000 |
| weather_gru_base | 0.019975 | 0.100000 |
