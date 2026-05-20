# Robust OOF diagnostics

- Baseline: `multi_signal`
- Candidate count: 7
- Promotion rule: bootstrap p025 > 0, at least 4/5 folds improved, no target regression worse than 0.0030.

## Candidate summary

| name | avg_log_loss | robust_score | fold_std | worst_fold | improved_folds_vs_baseline | worst_target_delta_vs_baseline | improvement_p025 | improvement | improvement_p975 | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_q3q1_s4_q2_s1 | 0.580543 | 0.584043 | 0.010000 | 0.600462 | 2 | 0.000000 | -0.000005 | 0.001049 | 0.002155 | False |
| qranker_q3q1_s4_q2 | 0.580719 | 0.584197 | 0.009936 | 0.600462 | 2 | 0.000000 | -0.000131 | 0.000873 | 0.001927 | False |
| qranker_q3q1_s4 | 0.580759 | 0.584241 | 0.009950 | 0.600527 | 2 | 0.000000 | -0.000166 | 0.000834 | 0.001890 | False |
| qranker_q3tail | 0.581192 | 0.584815 | 0.010351 | 0.601426 | 1 | 0.000000 | -0.000259 | 0.000400 | 0.001166 | False |
| tail_q3_support_s4 | 0.581296 | 0.585070 | 0.010784 | 0.602583 | 2 | 0.000000 | 0.000024 | 0.000296 | 0.000579 | False |
| support_s4w100 | 0.581445 | 0.585326 | 0.011090 | 0.603370 | 2 | 0.000000 | -0.000069 | 0.000148 | 0.000374 | False |
| multi_signal | 0.581592 | 0.585501 | 0.011168 | 0.603544 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target deltas vs baseline

| name | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_q3q1_s4 | 0.002002 | 0.000000 | 0.002800 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |
| qranker_q3q1_s4_q2 | 0.002002 | 0.000274 | 0.002800 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |
| qranker_q3q1_s4_q2_s1 | 0.002002 | 0.000274 | 0.002800 | 0.001235 | 0.000000 | 0.000000 | 0.001034 |
| qranker_q3tail | 0.000000 | 0.000000 | 0.002800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w100 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |
| tail_q3_support_s4 | 0.000000 | 0.000000 | 0.001041 | 0.000000 | 0.000000 | 0.000000 | 0.001034 |

## Prediction shift

| name | mean_abs_shift | max_overconfident_frac |
| --- | --- | --- |
| multi_signal | 0.015133 | 0.080000 |
| qranker_q3q1_s4 | 0.014200 | 0.080000 |
| qranker_q3q1_s4_q2 | 0.014141 | 0.080000 |
| qranker_q3q1_s4_q2_s1 | 0.014307 | 0.080000 |
| qranker_q3tail | 0.015541 | 0.080000 |
| support_s4w100 | 0.014954 | 0.080000 |
| tail_q3_support_s4 | 0.015261 | 0.080000 |
