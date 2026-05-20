# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 5
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 5 | 0.000357 | 0.000286 | 0.001080 | 0.001887 | True |
| graph_blend | 0.586443 | 0.590394 | 0.011288 | 0.608518 | 5 | 0.000357 | 0.000018 | 0.000733 | 0.001456 | True |
| sleep_min3 | 0.585653 | 0.590105 | 0.012721 | 0.610462 | 4 | 0.000357 | -0.000030 | 0.001523 | 0.003050 | False |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| primary | 0.588783 | 0.593823 | 0.012240 | 0.612043 | 1 | -0.005043 | -0.003647 | -0.001607 | 0.000424 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_blend | 0.000357 | 0.000503 | 0.000548 | 0.000574 | 0.000884 | 0.000537 | 0.001728 |
| graph_sleep_blend | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.001035 | 0.000537 | 0.002322 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary | 0.000000 | -0.002934 | -0.000246 | -0.003025 | 0.000000 | 0.000000 | -0.005043 |
| sleep_min3 | 0.000357 | 0.000503 | 0.000548 | 0.004495 | 0.001237 | 0.000537 | 0.002984 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_blend | 0.009715 | 0.080000 |
| graph_sleep_blend | 0.009904 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| primary | 0.010079 | 0.080000 |
| sleep_min3 | 0.010471 | 0.080000 |
