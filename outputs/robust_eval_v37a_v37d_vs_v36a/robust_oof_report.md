# Robust OOF diagnostics

- Baseline: `v36a`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v37d | 0.550990 | 0.552577 | 0.004537 | 0.556666 | 5 | 0.005593 | 0.006833 | 0.012662 | 0.018242 | True |
| v37a | 0.563275 | 0.564684 | 0.004024 | 0.567950 | 2 | 0.000000 | 0.000102 | 0.000376 | 0.000662 | False |
| v36a | 0.563651 | 0.564983 | 0.003807 | 0.567950 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v36a | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v37a | 0.001259 | 0.000000 | 0.000333 | 0.000640 | 0.000179 | 0.000222 | 0.000000 |
| v37d | 0.016309 | 0.017819 | 0.011728 | 0.005593 | 0.010341 | 0.013951 | 0.012890 |

## Prediction shift

_No submission files were provided for shift diagnostics._
