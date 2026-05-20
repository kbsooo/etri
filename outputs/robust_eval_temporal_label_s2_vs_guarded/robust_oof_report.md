# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_s2 | 0.584614 | 0.588748 | 0.011811 | 0.607999 | 5 | 0.000357 | 0.000817 | 0.002563 | 0.004328 | True |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 5 | 0.000357 | 0.000286 | 0.001080 | 0.001887 | True |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| primary | 0.588783 | 0.593823 | 0.012240 | 0.612043 | 1 | -0.005043 | -0.003647 | -0.001607 | 0.000424 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.001035 | 0.000537 | 0.002322 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary | 0.000000 | -0.002934 | -0.000246 | -0.003025 | 0.000000 | 0.000000 | -0.005043 |
| temporal_label_s2 | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.011415 | 0.000537 | 0.002322 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| primary | 0.010079 | 0.080000 |
| temporal_label_s2 | 0.014806 | 0.080000 |
