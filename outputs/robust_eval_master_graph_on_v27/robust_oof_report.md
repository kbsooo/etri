# Robust OOF diagnostics

- Baseline: `v27`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_fast | 0.572535 | 0.573334 | 0.002285 | 0.576827 | 4 | 0.000000 | -0.000388 | 0.000480 | 0.001352 | False |
| v28 | 0.572758 | 0.573636 | 0.002510 | 0.577486 | 3 | 0.000000 | -0.000131 | 0.000257 | 0.000631 | False |
| graph_tc | 0.572881 | 0.573666 | 0.002245 | 0.576689 | 3 | 0.000000 | -0.000363 | 0.000134 | 0.000645 | False |
| v27 | 0.573015 | 0.573845 | 0.002372 | 0.577486 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_tc | 0.000308 | 0.000000 | 0.000000 | 0.000000 | 0.000632 | 0.000000 | 0.000000 |
| master_fast | 0.002965 | 0.000000 | 0.000397 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v27 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v28 | 0.000000 | 0.000341 | 0.001461 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| graph_tc | 0.021527 | 0.148000 |
| master_fast | 0.022198 | 0.148000 |
| v27 | 0.021688 | 0.148000 |
| v28 | 0.022648 | 0.148000 |
