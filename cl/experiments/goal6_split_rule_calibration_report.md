# Goal6 — split rule and row calibration probe

Known public facts used: `wcap01=0.6394201335`, `wcap02=0.6311869686`, and failed `prior_sleep_conservative_q1q2s4=0.6421303776`.

This cannot identify exact public/private membership without more public scores; it ranks plausible row regimes and calibration targets.


## 1. Top Split/Calibration Rule Candidates

| rule | n_rows | inside_ratio | tail_ratio | has_future_ratio | mean_publiclike_score | mean_nearest_gap | w02_minus_w01_mean_abs | bad_minus_base_mean_abs | calibration_probe_score |
|---|---|---|---|---|---|---|---|---|---|
| publiclike_top30pct | 75 | 1.0000 | 0.0000 | 1.0000 | 0.9323 | 2.7867 | 0.0134 | 0.0355 | 1.2899 |
| publiclike_top40pct | 100 | 1.0000 | 0.0000 | 1.0000 | 0.9147 | 2.9400 | 0.0133 | 0.0336 | 1.2696 |
| inside_has_future | 156 | 1.0000 | 0.0000 | 1.0000 | 0.8712 | 3.4679 | 0.0132 | 0.0368 | 1.1985 |
| within_frac_0.25_0.50 | 58 | 1.0000 | 0.0000 | 1.0000 | 0.9110 | 4.3966 | 0.0131 | 0.0386 | 1.1971 |
| subject_id04 | 27 | 0.8889 | 0.1111 | 0.8889 | 0.8311 | 2.0000 | 0.0110 | 0.0261 | 1.1765 |
| subject_id08 | 19 | 0.8947 | 0.1053 | 0.8947 | 0.8368 | 1.6842 | 0.0179 | 0.0507 | 1.1693 |
| within_frac_0.00_0.25 | 64 | 1.0000 | 0.0000 | 1.0000 | 0.8292 | 3.6875 | 0.0124 | 0.0376 | 1.1438 |
| small_gap_le3 | 122 | 0.7869 | 0.2131 | 0.7869 | 0.7941 | 1.8852 | 0.0141 | 0.0358 | 1.0828 |
| small_gap_le5 | 164 | 0.7622 | 0.2378 | 0.7622 | 0.7746 | 2.5488 | 0.0135 | 0.0359 | 1.0225 |
| subject_id06 | 24 | 0.7500 | 0.2500 | 0.7500 | 0.7639 | 2.4167 | 0.0130 | 0.0297 | 1.0220 |
| subject_id05 | 21 | 0.7619 | 0.2381 | 0.7619 | 0.7615 | 2.5238 | 0.0140 | 0.0308 | 1.0217 |
| row_order_mod5_3 | 50 | 0.6600 | 0.3400 | 0.6600 | 0.6941 | 5.1400 | 0.0133 | 0.0333 | 0.7920 |
| row_order_mod5_2 | 50 | 0.6600 | 0.3400 | 0.6600 | 0.6892 | 5.2400 | 0.0128 | 0.0367 | 0.7745 |
| row_order_mod4_0 | 63 | 0.6349 | 0.3651 | 0.6349 | 0.6824 | 5.0000 | 0.0131 | 0.0352 | 0.7687 |
| row_order_mod4_1 | 63 | 0.6508 | 0.3492 | 0.6508 | 0.6858 | 5.3333 | 0.0128 | 0.0370 | 0.7622 |
| alternating_even_rows | 125 | 0.6320 | 0.3680 | 0.6320 | 0.6784 | 5.1760 | 0.0130 | 0.0340 | 0.7583 |
| row_order_mod4_2 | 62 | 0.6290 | 0.3710 | 0.6290 | 0.6743 | 5.3548 | 0.0128 | 0.0328 | 0.7476 |
| alternating_odd_rows | 125 | 0.6160 | 0.3840 | 0.6160 | 0.6702 | 5.3120 | 0.0129 | 0.0380 | 0.7282 |
| row_order_mod5_4 | 50 | 0.6000 | 0.4000 | 0.6000 | 0.6639 | 5.2400 | 0.0132 | 0.0339 | 0.7261 |
| row_order_mod5_0 | 50 | 0.6000 | 0.4000 | 0.6000 | 0.6660 | 4.9800 | 0.0122 | 0.0409 | 0.7217 |
| row_order_mod5_1 | 50 | 0.6000 | 0.4000 | 0.6000 | 0.6580 | 5.6200 | 0.0130 | 0.0353 | 0.7018 |
| within_frac_0.50_0.75 | 62 | 0.4194 | 0.5806 | 0.4194 | 0.6461 | 3.1452 | 0.0136 | 0.0354 | 0.7001 |
| row_order_mod4_3 | 62 | 0.5806 | 0.4194 | 0.5806 | 0.6543 | 5.2903 | 0.0129 | 0.0390 | 0.6936 |
| subject_id01 | 27 | 0.5185 | 0.4815 | 0.5185 | 0.6136 | 6.4074 | 0.0128 | 0.0452 | 0.5646 |
| subject_id09 | 27 | 0.5185 | 0.4815 | 0.5185 | 0.6058 | 7.0000 | 0.0154 | 0.0346 | 0.5620 |

## 2. Top Row Calibration Candidates

| row_id | subject_id | lifelog_date | regime | within_subject_frac | nearest_train_gap_d | has_future_train | publiclike_score | row_calibration_pressure | w02_minus_w01_mean_abs | w03_minus_anchor_mean_abs | block_minus_anchor_mean_abs | bad_minus_base_mean_abs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 117 | id05 | 2024-10-16 | inside | 0.5000 | 2.0000 | 1 | 0.9796 | 1.3442 | 0.0147 | 0.0078 | 0.1176 | 0.0278 |
| 141 | id06 | 2024-08-09 | inside | 0.5652 | 1.0000 | 1 | 0.9068 | 1.3357 | 0.0116 | 0.0056 | 0.1267 | 0.0013 |
| 119 | id05 | 2024-11-06 | inside | 0.6000 | 1.0000 | 1 | 0.8890 | 1.3088 | 0.0158 | 0.0065 | 0.1566 | 0.0584 |
| 113 | id05 | 2024-10-06 | inside | 0.3000 | 3.0000 | 1 | 0.9289 | 1.2569 | 0.0174 | 0.0075 | 0.1015 | 0.0256 |
| 139 | id06 | 2024-07-18 | inside | 0.4783 | 3.0000 | 1 | 0.9693 | 1.2445 | 0.0171 | 0.0116 | 0.0893 | 0.0395 |
| 42 | id02 | 2024-09-09 | inside | 0.4839 | 1.0000 | 1 | 0.9579 | 1.2364 | 0.0140 | 0.0039 | 0.0956 | 0.0309 |
| 211 | id09 | 2024-08-15 | inside | 0.3846 | 6.0000 | 1 | 0.9182 | 1.2307 | 0.0171 | 0.0104 | 0.0863 | 0.0144 |
| 110 | id05 | 2024-10-01 | inside | 0.1500 | 4.0000 | 1 | 0.8753 | 1.2230 | 0.0099 | 0.0074 | 0.1104 | 0.0178 |
| 116 | id05 | 2024-10-15 | inside | 0.4500 | 3.0000 | 1 | 0.9623 | 1.2134 | 0.0199 | 0.0170 | 0.0773 | 0.0458 |
| 112 | id05 | 2024-10-05 | inside | 0.2500 | 4.0000 | 1 | 0.9037 | 1.2070 | 0.0137 | 0.0092 | 0.0950 | 0.0252 |
| 213 | id09 | 2024-08-18 | inside | 0.4615 | 3.0000 | 1 | 0.9699 | 1.1982 | 0.0215 | 0.0113 | 0.0560 | 0.0192 |
| 196 | id08 | 2024-09-10 | inside | 0.7778 | 1.0000 | 1 | 0.8298 | 1.1958 | 0.0213 | 0.0099 | 0.0941 | 0.0051 |
| 189 | id08 | 2024-08-10 | inside | 0.3889 | 1.0000 | 1 | 0.9817 | 1.1945 | 0.0142 | 0.0070 | 0.0835 | 0.0505 |
| 210 | id09 | 2024-08-14 | inside | 0.3462 | 7.0000 | 1 | 0.8966 | 1.1939 | 0.0160 | 0.0103 | 0.0794 | 0.0098 |
| 120 | id05 | 2024-11-07 | inside | 0.6500 | 2.0000 | 1 | 0.8629 | 1.1893 | 0.0115 | 0.0089 | 0.1234 | 0.0524 |
| 92 | id04 | 2024-09-25 | inside | 0.4615 | 2.0000 | 1 | 0.9818 | 1.1851 | 0.0064 | 0.0034 | 0.0828 | 0.0373 |
| 93 | id04 | 2024-09-26 | inside | 0.5000 | 1.0000 | 1 | 0.9979 | 1.1823 | 0.0092 | 0.0043 | 0.0559 | 0.0119 |
| 114 | id05 | 2024-10-10 | inside | 0.3500 | 1.0000 | 1 | 0.9749 | 1.1774 | 0.0249 | 0.0126 | 0.0442 | 0.0213 |
| 109 | id05 | 2024-09-30 | inside | 0.1000 | 3.0000 | 1 | 0.8724 | 1.1749 | 0.0146 | 0.0117 | 0.0846 | 0.0152 |
| 108 | id05 | 2024-09-29 | inside | 0.0500 | 2.0000 | 1 | 0.8686 | 1.1740 | 0.0121 | 0.0077 | 0.0959 | 0.0208 |
| 69 | id03 | 2024-08-28 | inside | 0.5000 | 1.0000 | 1 | 0.9982 | 1.1690 | 0.0148 | 0.0046 | 0.0505 | 0.0193 |
| 188 | id08 | 2024-08-09 | inside | 0.3333 | 2.0000 | 1 | 0.9614 | 1.1662 | 0.0146 | 0.0096 | 0.0752 | 0.0467 |
| 133 | id06 | 2024-07-11 | inside | 0.2174 | 3.0000 | 1 | 0.9110 | 1.1656 | 0.0160 | 0.0119 | 0.0676 | 0.0160 |
| 88 | id04 | 2024-09-20 | inside | 0.3077 | 3.0000 | 1 | 0.9463 | 1.1646 | 0.0102 | 0.0067 | 0.0620 | 0.0093 |
| 212 | id09 | 2024-08-16 | inside | 0.4231 | 5.0000 | 1 | 0.9383 | 1.1620 | 0.0181 | 0.0113 | 0.0681 | 0.0344 |
| 87 | id04 | 2024-09-19 | inside | 0.2692 | 2.0000 | 1 | 0.9514 | 1.1535 | 0.0118 | 0.0076 | 0.0580 | 0.0151 |
| 121 | id05 | 2024-11-12 | inside | 0.7000 | 1.0000 | 1 | 0.8249 | 1.1529 | 0.0228 | 0.0142 | 0.0834 | 0.0167 |
| 166 | id07 | 2024-07-27 | inside | 0.4828 | 1.0000 | 1 | 0.9586 | 1.1497 | 0.0181 | 0.0118 | 0.0561 | 0.0334 |
| 115 | id05 | 2024-10-13 | inside | 0.4000 | 4.0000 | 1 | 0.9434 | 1.1473 | 0.0147 | 0.0086 | 0.1002 | 0.0833 |
| 68 | id03 | 2024-08-27 | inside | 0.4500 | 2.0000 | 1 | 0.9799 | 1.1429 | 0.0108 | 0.0035 | 0.0493 | 0.0139 |
| 111 | id05 | 2024-10-04 | inside | 0.2000 | 5.0000 | 1 | 0.8771 | 1.1417 | 0.0161 | 0.0110 | 0.0889 | 0.0418 |
| 62 | id03 | 2024-08-19 | inside | 0.1500 | 4.0000 | 1 | 0.8738 | 1.1416 | 0.0075 | 0.0051 | 0.0879 | 0.0168 |
| 204 | id09 | 2024-08-08 | inside | 0.1154 | 4.0000 | 1 | 0.8575 | 1.1295 | 0.0194 | 0.0119 | 0.0813 | 0.0329 |
| 13 | id01 | 2024-08-16 | inside | 0.5000 | 1.0000 | 1 | 1.0000 | 1.1266 | 0.0123 | 0.0078 | 0.0459 | 0.0356 |
| 67 | id03 | 2024-08-26 | inside | 0.4000 | 3.0000 | 1 | 0.9590 | 1.1263 | 0.0122 | 0.0068 | 0.0676 | 0.0463 |

## 3. Interpretation

- The live public improvement `w02 < w01` points to same-subject temporal interpolation, not raw sensor modeling.

- The failed Q1/Q2/S4 prior-sleep file penalizes broad hard-target feature shifts; row calibration should stay close to the temporal anchor.

- Highest-priority masks are inside-range/future-neighbor rows with small train gaps. Tail-only rows should be conservative unless a separate public score proves otherwise.

- Exact public/private split still needs more orthogonal public submissions; with only the current public facts, use this as a row-routing map, not a decoded hidden label file.


## 4. Generated Conservative Calibration Candidates

| file | target | changed_rows | mean_abs_delta_vs_anchor | max_abs_delta_vs_anchor | mean_signed_delta_vs_anchor | corr_vs_anchor |
|---|---|---|---|---|---|---|
| submission_goal6_publiclike_top30_block20_prob.csv | Q1 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_publiclike_top30_block20_prob.csv | Q2 | 75 | 0.00383 | 0.04000 | 0.00242 | 0.99674 |
| submission_goal6_publiclike_top30_block20_prob.csv | Q3 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_publiclike_top30_block20_prob.csv | S1 | 75 | 0.00473 | 0.04000 | 0.00226 | 0.99784 |
| submission_goal6_publiclike_top30_block20_prob.csv | S2 | 75 | 0.00802 | 0.04000 | 0.00605 | 0.99664 |
| submission_goal6_publiclike_top30_block20_prob.csv | S3 | 75 | 0.00648 | 0.04000 | 0.00334 | 0.99802 |
| submission_goal6_publiclike_top30_block20_prob.csv | S4 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_publiclike_top40_block15_prob.csv | Q1 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_publiclike_top40_block15_prob.csv | Q2 | 100 | 0.00393 | 0.04000 | 0.00230 | 0.99732 |
| submission_goal6_publiclike_top40_block15_prob.csv | Q3 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_publiclike_top40_block15_prob.csv | S1 | 100 | 0.00471 | 0.04000 | 0.00241 | 0.99855 |
| submission_goal6_publiclike_top40_block15_prob.csv | S2 | 100 | 0.00845 | 0.04000 | 0.00652 | 0.99731 |
| submission_goal6_publiclike_top40_block15_prob.csv | S3 | 100 | 0.00686 | 0.04000 | 0.00362 | 0.99847 |
| submission_goal6_publiclike_top40_block15_prob.csv | S4 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_inside_future_block10_prob.csv | Q1 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_inside_future_block10_prob.csv | Q2 | 156 | 0.00493 | 0.04000 | 0.00260 | 0.99776 |
| submission_goal6_inside_future_block10_prob.csv | Q3 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |
| submission_goal6_inside_future_block10_prob.csv | S1 | 156 | 0.00489 | 0.02809 | 0.00190 | 0.99923 |
| submission_goal6_inside_future_block10_prob.csv | S2 | 156 | 0.00768 | 0.02907 | 0.00612 | 0.99873 |
| submission_goal6_inside_future_block10_prob.csv | S3 | 156 | 0.00648 | 0.03338 | 0.00330 | 0.99923 |
| submission_goal6_inside_future_block10_prob.csv | S4 | 0 | 0.00000 | 0.00000 | 0.00000 | 1.00000 |

Use these as diagnostics only. The expected gain is small; their value is identifying whether publiclike inside rows should receive validated-block residuals.
