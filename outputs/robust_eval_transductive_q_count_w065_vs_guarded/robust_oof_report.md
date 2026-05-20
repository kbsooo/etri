# Robust OOF diagnostics

- Baseline: `guarded`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_w065 | 0.581881 | 0.585756 | 0.011074 | 0.603685 | 5 | 0.001012 | 0.002287 | 0.004562 | 0.006890 | True |
| guarded | 0.586443 | 0.590394 | 0.011288 | 0.608518 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guarded | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_w065 | 0.002545 | 0.010538 | 0.004419 | 0.002933 | 0.009446 | 0.001012 | 0.001043 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| guarded | 0.009715 | 0.080000 |
| qcount_w065 | 0.015054 | 0.080000 |
