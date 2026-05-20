# Robust OOF diagnostics

- Baseline: `block_aware_qcount`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_qcount | 0.581652 | 0.585419 | 0.010762 | 0.602752 | 4 | 0.000000 | -0.000492 | 0.000199 | 0.000866 | False |
| block_aware_qcount | 0.581851 | 0.585713 | 0.011035 | 0.603548 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_qcount | 0.000000 | 0.000000 | 0.000000 | 0.000551 | 0.000569 | 0.000066 | 0.000206 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| block_aware_qcount | 0.015083 | 0.080000 |
| prior_qcount | 0.015168 | 0.084000 |
