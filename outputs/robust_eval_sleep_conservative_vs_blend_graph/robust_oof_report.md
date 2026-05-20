# Robust OOF diagnostics

- Baseline: `blend_graph_w04`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sleep_conservative | 0.585883 | 0.590208 | 0.012359 | 0.609980 | 4 | 0.000000 | -0.000598 | 0.000560 | 0.001686 | False |
| blend_graph_w04 | 0.586443 | 0.590394 | 0.011288 | 0.608518 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| guarded | 0.587176 | 0.591469 | 0.011524 | 0.609772 | 0 | -0.001728 | -0.001456 | -0.000733 | -0.000018 | False |
| primary | 0.588783 | 0.594083 | 0.012240 | 0.612043 | 0 | -0.006771 | -0.004212 | -0.002340 | -0.000467 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| blend_graph_w04 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guarded | -0.000357 | -0.000503 | -0.000548 | -0.000574 | -0.000884 | -0.000537 | -0.001728 |
| primary | -0.000357 | -0.003437 | -0.000795 | -0.003599 | -0.000884 | -0.000537 | -0.006771 |
| sleep_conservative | 0.000000 | 0.000000 | 0.000000 | 0.003921 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| blend_graph_w04 | 0.009715 | 0.080000 |
| guarded | 0.010319 | 0.080000 |
| primary | 0.010079 | 0.080000 |
| sleep_conservative | 0.011977 | 0.080000 |
