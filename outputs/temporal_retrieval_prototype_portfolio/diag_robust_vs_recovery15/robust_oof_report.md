# Robust OOF diagnostics

- Baseline: `recovery15`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trp_w100_q3w035 | 0.574169 | 0.575094 | 0.002642 | 0.577486 | 3 | 0.000000 | 0.000059 | 0.002048 | 0.004021 | False |
| trp_w080_q3w035 | 0.574228 | 0.575172 | 0.002699 | 0.577486 | 3 | 0.000000 | 0.000057 | 0.001989 | 0.003868 | False |
| trp_w100_q3w050 | 0.574432 | 0.575584 | 0.003292 | 0.578657 | 3 | 0.000000 | -0.000873 | 0.001785 | 0.004358 | False |
| recovery15 | 0.576217 | 0.577081 | 0.002471 | 0.578995 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| recovery15 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_w080_q3w035 | 0.000000 | 0.000000 | 0.008230 | 0.000000 | 0.005692 | 0.000000 | 0.000000 |
| trp_w100_q3w035 | 0.000000 | 0.000000 | 0.008230 | 0.000000 | 0.006104 | 0.000000 | 0.000000 |
| trp_w100_q3w050 | 0.000000 | 0.000000 | 0.006392 | 0.000000 | 0.006104 | 0.000000 | 0.000000 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| recovery15 | 0.020179 | 0.112000 |
| trp_w080_q3w035 | 0.021772 | 0.112000 |
| trp_w100_q3w035 | 0.021915 | 0.112000 |
| trp_w100_q3w050 | 0.022826 | 0.112000 |
