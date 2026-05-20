# Robust OOF diagnostics

- Baseline: `v35e`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v36a | 0.563651 | 0.564983 | 0.003807 | 0.567950 | 5 | 0.000000 | 0.002036 | 0.006663 | 0.011269 | True |
| v35e | 0.570315 | 0.571806 | 0.004262 | 0.577482 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v36a | 0.006377 | 0.027250 | 0.009239 | 0.000654 | 0.000000 | 0.000000 | 0.003124 |

## Prediction shift

_No submission files were provided for shift diagnostics._
