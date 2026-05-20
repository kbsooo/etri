# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 5
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| support_s4w100 | 0.581445 | 0.585326 | 0.011090 | 0.603370 | 2 | 0.000000 | -0.000069 | 0.000148 | 0.000374 | False |
| master_q3s4 | 0.581569 | 0.585410 | 0.010862 | 0.602834 | 1 | -0.000264 | -0.000394 | 0.000024 | 0.000446 | False |
| master_q1q3s1s4 | 0.581437 | 0.585424 | 0.011277 | 0.603708 | 2 | -0.000264 | -0.000469 | 0.000155 | 0.000789 | False |
| master_q1q3s4 | 0.581560 | 0.585489 | 0.011114 | 0.603424 | 2 | -0.000264 | -0.000518 | 0.000032 | 0.000587 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| master_q1q3s1s4 | 0.000060 | 0.000000 | 0.000430 | 0.000859 | 0.000000 | 0.000000 | -0.000264 |
| master_q1q3s4 | 0.000060 | 0.000000 | 0.000430 | 0.000000 | 0.000000 | 0.000000 | -0.000264 |
| master_q3s4 | 0.000000 | 0.000000 | 0.000430 | 0.000000 | 0.000000 | 0.000000 | -0.000264 |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| master_q1q3s1s4 | 0.015240 | 0.080000 |
| master_q1q3s4 | 0.014943 | 0.080000 |
| master_q3s4 | 0.015221 | 0.080000 |
| multi_signal | 0.015133 | 0.080000 |
| support_s4w100 | 0.014954 | 0.080000 |
