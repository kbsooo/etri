# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 2
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| forward_prior_broadw | 0.573959 | 0.577737 | 0.010793 | 0.595520 | 5 | 0.000000 | 0.002961 | 0.007633 | 0.012279 | True |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| forward_prior_broadw | 0.010695 | 0.030513 | 0.012225 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| forward_prior_broadw | 0.018445 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
