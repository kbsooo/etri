# Robust OOF diagnostics

- Baseline: `primary_w03`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0010.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_broadgrid | 0.581703 | 0.585594 | 0.011117 | 0.603700 | 3 | 0.000000 | -0.000357 | 0.002095 | 0.004546 | False |
| primary_w03 | 0.583798 | 0.587749 | 0.011289 | 0.606060 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_broadgrid | 0.000000 | 0.012656 | 0.002006 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| primary_w03 | 0.014490 | 0.080000 |
| qcount_broadgrid | 0.015803 | 0.080000 |
