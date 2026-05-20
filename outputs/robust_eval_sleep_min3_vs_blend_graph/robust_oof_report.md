# Robust OOF diagnostics

- Baseline: `blend_graph_w04`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sleep_min3 | 0.585653 | 0.590105 | 0.012721 | 0.610462 | 4 | 0.000000 | -0.000562 | 0.000790 | 0.002159 | False |
| sleep_conservative | 0.585883 | 0.590208 | 0.012359 | 0.609980 | 4 | 0.000000 | -0.000598 | 0.000560 | 0.001686 | False |
| blend_graph_w04 | 0.586443 | 0.590394 | 0.011288 | 0.608518 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| blend_graph_w04 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| sleep_conservative | 0.000000 | 0.000000 | 0.000000 | 0.003921 | 0.000000 | 0.000000 | 0.000000 |
| sleep_min3 | 0.000000 | 0.000000 | 0.000000 | 0.003921 | 0.000352 | 0.000000 | 0.001256 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| blend_graph_w04 | 0.009715 | 0.080000 |
| sleep_conservative | 0.011977 | 0.080000 |
| sleep_min3 | 0.010471 | 0.080000 |
