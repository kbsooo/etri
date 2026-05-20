# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_s2_blend | 0.584769 | 0.588848 | 0.011655 | 0.607774 | 5 | 0.000357 | 0.000922 | 0.002408 | 0.003920 | True |
| graph_sleep_blend | 0.586096 | 0.590172 | 0.011643 | 0.608847 | 5 | 0.000357 | 0.000286 | 0.001080 | 0.001887 | True |
| guarded | 0.587176 | 0.591209 | 0.011524 | 0.609772 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.001035 | 0.000537 | 0.002322 |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_s2_blend | 0.000357 | 0.000503 | 0.000548 | 0.002255 | 0.010330 | 0.000537 | 0.002322 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_sleep_blend | 0.009904 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| temporal_s2_blend | 0.013825 | 0.080000 |
