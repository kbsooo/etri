# Robust OOF diagnostics

- Baseline: `v36a`
- Candidate count: 3
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v38a | 0.549791 | 0.551602 | 0.005176 | 0.555440 | 5 | 0.005811 | 0.008114 | 0.013861 | 0.019440 | True |
| v37e | 0.550513 | 0.552241 | 0.004937 | 0.556598 | 5 | 0.005811 | 0.007329 | 0.013138 | 0.018817 | True |
| v36a | 0.563651 | 0.564983 | 0.003807 | 0.567950 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v36a | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v37e | 0.017685 | 0.017819 | 0.012015 | 0.005811 | 0.011580 | 0.013951 | 0.013105 |
| v38a | 0.017685 | 0.018348 | 0.014804 | 0.005811 | 0.011580 | 0.015691 | 0.013105 |

## Prediction shift

_No submission files were provided for shift diagnostics._
