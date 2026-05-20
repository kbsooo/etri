# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 4
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tail_q3_support_s4 | 0.581296 | 0.585070 | 0.010784 | 0.602583 | 2 | 0.000000 | 0.000024 | 0.000296 | 0.000579 | False |
| tail_q3 | 0.581444 | 0.585246 | 0.010864 | 0.602756 | 1 | 0.000000 | -0.000013 | 0.000149 | 0.000325 | False |
| support_s4w100 | 0.581445 | 0.585326 | 0.011090 | 0.603370 | 2 | 0.000000 | -0.000069 | 0.000148 | 0.000374 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |
| tail_q3 | 0.000000 | 0.000000 | 0.001041 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3_support_s4 | 0.000000 | 0.000000 | 0.001041 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| support_s4w100 | 0.014954 | 0.080000 |
| tail_q3 | 0.015439 | 0.080000 |
| tail_q3_support_s4 | 0.015261 | 0.080000 |
