# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_resid_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 5 | 0.000503 | 0.001503 | 0.003378 | 0.005251 | True |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 5 | 0.000357 | 0.000286 | 0.001080 | 0.001887 | True |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.001035 | 0.000537 | 0.002322 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_resid_w03 | 0.001366 | 0.000503 | 0.003621 | 0.003507 | 0.010330 | 0.001549 | 0.002771 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| master_resid_w03 | 0.014490 | 0.080000 |
