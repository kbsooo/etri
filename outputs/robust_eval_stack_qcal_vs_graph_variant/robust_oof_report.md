# Robust OOF diagnostics

- Baseline: `graph_variant`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prediction_stack_qcal | 0.596392 | 0.600278 | 0.011102 | 0.617705 | 5 | 0.000000 | 0.001776 | 0.006093 | 0.010421 | True |
| prediction_stack | 0.598173 | 0.602243 | 0.011631 | 0.619211 | 4 | 0.000000 | 0.001270 | 0.004312 | 0.007408 | True |
| q_calibrated | 0.601828 | 0.605259 | 0.008819 | 0.615602 | 4 | -0.002291 | -0.000736 | 0.000656 | 0.002020 | False |
| graph_variant | 0.602485 | 0.605730 | 0.009273 | 0.617895 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_variant | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prediction_stack | 0.000000 | 0.008242 | 0.012190 | 0.000000 | 0.000000 | 0.008173 | 0.001581 |
| prediction_stack_qcal | 0.000000 | 0.016184 | 0.018344 | 0.000000 | 0.000000 | 0.006956 | 0.001166 |
| q_calibrated | -0.002291 | 0.004268 | 0.002618 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_variant | 0.010225 | 0.028000 |
| prediction_stack | 0.009597 | 0.028000 |
| prediction_stack_qcal | 0.009884 | 0.028000 |
| q_calibrated | 0.009520 | 0.028000 |
