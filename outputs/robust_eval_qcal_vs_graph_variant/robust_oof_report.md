# Robust OOF diagnostics

- Baseline: `graph_variant`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q_calibrated | 0.601828 | 0.605259 | 0.008819 | 0.615602 | 4 | -0.002291 | -0.000736 | 0.000656 | 0.002020 | False |
| graph_variant | 0.602485 | 0.605730 | 0.009273 | 0.617895 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_variant | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q_calibrated | -0.002291 | 0.004268 | 0.002618 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_variant | 0.010225 | 0.028000 |
| q_calibrated | 0.009520 | 0.028000 |
