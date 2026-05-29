# E167 Broad Survivor Context Alignment

## Question

Does the E166 broad survivor move touch hidden row/block/context and safety-atlas structure, or does it look like target-count-matched random cells?

## Summary

- evaluated pairs: `5`.
- E166 focus cells from swing threshold: `74`.
- permutation nulls per E166 top set: `3000`.

## E166 Set Anatomy

| set_type | n_cells | n_rows | n_subjects | n_blocks | expected_delta | benefit_sum | risk_sum | swing_sum | q_share | s_share | q2s3_share | edge_like_rate | between_train_runs_rate | top_subject_share | top_block_share | all_veto_null_rate | all_low_adverse75_rate | all_co_vetonull_density_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_moved | 1750 | 250 | 10 | 36 | -0.000332077 | 0.000372683 | 0.000040607 | 0.002243986 | 0.428571429 | 0.571428571 | 0.285714286 | 0.472000000 | 0.624000000 | 0.128000000 | 0.064000000 | 0.671428571 | 0.749714286 | 0.000000000 |
| top_benefit_nfocus | 74 | 64 | 9 | 24 | -0.000115303 | 0.000115303 | 0.000000000 | 0.000310840 | 0.297297297 | 0.702702703 | 0.054054054 | 0.689189189 | 0.797297297 | 0.243243243 | 0.094594595 | 0.297297297 | 0.540540541 | 0.000000000 |
| top_swing_nfocus | 74 | 67 | 10 | 22 | -0.000101442 | 0.000101544 | 0.000000102 | 0.000332260 | 0.310810811 | 0.689189189 | 0.067567568 | 0.594594595 | 0.824324324 | 0.229729730 | 0.094594595 | 0.351351351 | 0.594594595 | 0.000000000 |

## E166 Target-Count Null Deviations

| set_name | metric | observed | null_mean | null_std | z | p_high | p_low |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e166_vs_e95:top_benefit_nfocus | edge_like_rate | 0.689189189 | 0.471567568 | 0.056290937 | 3.866015277 | 0.000666445 | 1.000000000 |
| e166_vs_e95:top_benefit_nfocus | e72_active_rate | 0.837837838 | 0.671752252 | 0.048889051 | 3.397193916 | 0.000666445 | 1.000000000 |
| e166_vs_e95:top_benefit_nfocus | between_train_runs_rate | 0.797297297 | 0.624121622 | 0.054687005 | 3.166669605 | 0.001332889 | 0.999666778 |
| e166_vs_e95:top_benefit_nfocus | top_subject_share | 0.243243243 | 0.164572072 | 0.022957703 | 3.426787611 | 0.007997334 | 0.997334222 |
| e166_vs_e95:top_benefit_nfocus | weekend_rate | 0.175675676 | 0.273243243 | 0.049013866 | -1.990611529 | 0.986337887 | 0.029323559 |
| e166_vs_e95:top_benefit_nfocus | all_low_adverse75_rate | 0.540540541 | 0.672522523 | 0.050949639 | -2.590439993 | 0.996667777 | 0.006331223 |
| e166_vs_e95:top_benefit_nfocus | all_co_vetonull_density_mean | 0.000000000 | 0.000000000 | 0.000000000 | -0.785269655 | 0.997001000 | 0.003332223 |
| e166_vs_e95:top_benefit_nfocus | e95_fallback_rate | 0.027027027 | 0.109243243 | 0.032776622 | -2.508379766 | 0.999000333 | 0.006997667 |
| e166_vs_e95:top_benefit_nfocus | long_block_rate | 0.337837838 | 0.596711712 | 0.054634670 | -4.738271017 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_benefit_nfocus | all_veto_null_rate | 0.297297297 | 0.576022523 | 0.054001434 | -5.161441166 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_benefit_nfocus | all_safe_density_mean | 0.117097166 | 0.244671535 | 0.024337018 | -5.241988451 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_benefit_nfocus | broad_low_alpha_mass_sum | 1.321365440 | 3.185393859 | 0.549913072 | -3.389678322 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_benefit_nfocus | e101_plausible_mass_sum | 0.238204293 | 0.529650974 | 0.095040197 | -3.066562241 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_benefit_nfocus | n_subjects | 9.000000000 | 9.995666667 | 0.065696227 | -15.155614175 | 1.000000000 | 0.004665112 |
| e166_vs_e95:top_swing_nfocus | between_train_runs_rate | 0.824324324 | 0.623824324 | 0.054111077 | 3.705341122 | 0.000333222 | 1.000000000 |
| e166_vs_e95:top_swing_nfocus | e72_active_rate | 0.783783784 | 0.657990991 | 0.049914596 | 2.520160498 | 0.005664778 | 0.997667444 |
| e166_vs_e95:top_swing_nfocus | top_subject_share | 0.229729730 | 0.165063063 | 0.022792881 | 2.837143147 | 0.015328224 | 0.992669110 |
| e166_vs_e95:top_swing_nfocus | edge_like_rate | 0.594594595 | 0.472355856 | 0.055534694 | 2.201123823 | 0.022992336 | 0.985671443 |
| e166_vs_e95:top_swing_nfocus | long_block_rate | 0.486486486 | 0.596815315 | 0.055481622 | -1.988565313 | 0.980339887 | 0.034988337 |
| e166_vs_e95:top_swing_nfocus | weekend_rate | 0.162162162 | 0.272590090 | 0.051247508 | -2.154796035 | 0.992002666 | 0.017994002 |
| e166_vs_e95:top_swing_nfocus | n_blocks | 22.000000000 | 26.637333333 | 1.948265417 | -2.380236950 | 0.997001000 | 0.016661113 |
| e166_vs_e95:top_swing_nfocus | e95_fallback_rate | 0.027027027 | 0.110427928 | 0.032608768 | -2.557621918 | 0.999333555 | 0.004331889 |
| e166_vs_e95:top_swing_nfocus | all_veto_null_rate | 0.351351351 | 0.587837838 | 0.054814723 | -4.314287727 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_swing_nfocus | all_safe_density_mean | 0.142310695 | 0.248456193 | 0.024909372 | -4.261267550 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_swing_nfocus | broad_low_alpha_mass_sum | 1.354317193 | 3.519096687 | 0.613625098 | -3.527853573 | 1.000000000 | 0.000333222 |
| e166_vs_e95:top_swing_nfocus | e101_plausible_mass_sum | 0.232534857 | 0.552448838 | 0.102859091 | -3.110215907 | 1.000000000 | 0.000333222 |

## Pair Comparison

| pair | n_cells | n_rows | n_subjects | n_blocks | expected_delta | benefit_sum | risk_sum | swing_sum | q2s3_share | edge_like_rate | between_train_runs_rate | top_subject_share | all_veto_null_rate | all_low_adverse75_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e166_vs_e95 | 74 | 64 | 9 | 24 | -0.000115303 | 0.000115303 | 0.000000000 | 0.000310840 | 0.054054054 | 0.689189189 | 0.797297297 | 0.243243243 | 0.297297297 | 0.540540541 |
| e154_vs_e95 | 3 | 3 | 2 | 2 | -0.000012543 | 0.000012543 | 0.000000000 | 0.000037490 | 0.000000000 | 0.666666667 | 0.000000000 | 0.666666667 | 1.000000000 | 1.000000000 |
| e101_vs_e95 | 5 | 5 | 3 | 4 | -0.000005888 | 0.000005888 | 0.000000000 | 0.000038175 | 1.000000000 | 0.600000000 | 0.600000000 | 0.600000000 | 0.400000000 | 0.400000000 |
| e95_vs_mixmin | 4 | 4 | 2 | 4 | -0.000066583 | 0.000066583 | 0.000000000 | 0.000164776 | 1.000000000 | 0.750000000 | 1.000000000 | 0.500000000 | 0.250000000 | 0.250000000 |
| mixmin_vs_a2c8 | 5 | 5 | 1 | 3 | -0.000133742 | 0.000133742 | 0.000000000 | 0.000234596 | 1.000000000 | 0.600000000 | 0.800000000 | 1.000000000 | 1.000000000 | 1.000000000 |

## E166 Top Blocks

| hidden_block_id | subject_id | context_type | block_len_bin | cells | rows | benefit_sum | risk_sum | expected_delta | swing_sum | targets | edge_like_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id10_b2 | id10 | between_train_runs | 11-16 | 10 | 5 | 0.000022645 | 0.000000000 | -0.000022645 | 0.000043995 | S1 | 0.400000000 |
| id01_b2 | id01 | between_train_runs | 11-16 | 13 | 6 | 0.000022161 | 0.000000000 | -0.000022161 | 0.000060043 | Q1,S1 | 0.230769231 |
| id06_b2 | id06 | between_train_runs | 6-10 | 13 | 7 | 0.000020623 | 0.000000000 | -0.000020623 | 0.000072729 | S1 | 0.615384615 |
| id08_b10 | id08 | between_train_runs | 3-5 | 10 | 4 | 0.000017336 | 0.000000000 | -0.000017336 | 0.000048222 | Q3,S1 | 1.000000000 |
| id05_b8 | id05 | between_train_runs | 1-2 | 7 | 2 | 0.000016537 | 0.000000000 | -0.000016537 | 0.000039173 | Q1,S2,S3 | 1.000000000 |
| id10_b4 | id10 | after_train_run | 11-16 | 6 | 3 | 0.000015874 | 0.000000000 | -0.000015874 | 0.000027280 | S1 | 0.333333333 |
| id03_b2 | id03 | between_train_runs | 11-16 | 11 | 5 | 0.000014197 | 0.000000000 | -0.000014197 | 0.000052082 | Q1,S1,S4 | 0.636363636 |
| id06_b6 | id06 | between_train_runs | 1-2 | 8 | 1 | 0.000010734 | 0.000000000 | -0.000010734 | 0.000034315 | Q1,S1,S3,S4 | 1.000000000 |
| id03_b4 | id03 | after_train_run | 6-10 | 8 | 6 | 0.000010108 | 0.000000000 | -0.000010108 | 0.000028571 | S4 | 0.500000000 |
| id06_b4 | id06 | between_train_runs | 3-5 | 8 | 4 | 0.000009218 | 0.000000000 | -0.000009218 | 0.000031874 | S1,S3 | 0.750000000 |
| id05_b4 | id05 | between_train_runs | 3-5 | 5 | 3 | 0.000007748 | 0.000000000 | -0.000007748 | 0.000017881 | S2 | 1.000000000 |
| id08_b6 | id08 | between_train_runs | 1-2 | 6 | 2 | 0.000007421 | 0.000000000 | -0.000007421 | 0.000027024 | Q2,Q3 | 1.000000000 |
| id09_b2 | id09 | between_train_runs | 11-16 | 7 | 7 | 0.000005749 | 0.000000000 | -0.000005749 | 0.000024925 | S1,S2 | 0.142857143 |
| id08_b2 | id08 | between_train_runs | 1-2 | 4 | 2 | 0.000005706 | 0.000000000 | -0.000005706 | 0.000016669 | Q3 | 1.000000000 |
| id04_b12 | id04 | between_train_runs | 3-5 | 5 | 3 | 0.000005361 | 0.000000000 | -0.000005361 | 0.000021723 | S1 | 1.000000000 |
| id07_b4 | id07 | after_train_run | 11-16 | 5 | 4 | 0.000004766 | 0.000000000 | -0.000004766 | 0.000020958 | Q1,S1 | 0.600000000 |
| id07_b2 | id07 | between_train_runs | 11-16 | 5 | 4 | 0.000004080 | 0.000000000 | -0.000004080 | 0.000018305 | Q1,S1,S2 | 0.200000000 |
| id06_b8 | id06 | between_train_runs | 3-5 | 3 | 2 | 0.000003738 | 0.000000000 | -0.000003738 | 0.000011367 | Q1,S1 | 1.000000000 |
| id06_b10 | id06 | after_train_run | 6-10 | 3 | 2 | 0.000003351 | 0.000000000 | -0.000003351 | 0.000011160 | S1,S4 | 1.000000000 |
| id08_b4 | id08 | between_train_runs | 6-10 | 2 | 1 | 0.000002185 | 0.000000000 | -0.000002185 | 0.000004866 | Q1,S1 | 0.000000000 |
| id05_b6 | id05 | between_train_runs | 1-2 | 1 | 1 | 0.000001495 | 0.000000000 | -0.000001495 | 0.000002721 | S1 | 1.000000000 |
| id08_b12 | id08 | between_train_runs | 1-2 | 1 | 1 | 0.000001471 | 0.000000000 | -0.000001471 | 0.000003127 | S1 | 1.000000000 |
| id05_b10 | id05 | after_train_run | 3-5 | 1 | 1 | 0.000001270 | 0.000000000 | -0.000001270 | 0.000002656 | S1 | 1.000000000 |
| id09_b4 | id09 | after_train_run | 11-16 | 2 | 2 | 0.000001145 | 0.000000000 | -0.000001145 | 0.000007286 | S2 | 0.000000000 |
| id08_b14 | id08 | after_train_run | 1-2 | 1 | 1 | 0.000001109 | 0.000000000 | -0.000001109 | 0.000002923 | Q3 | 1.000000000 |

## Decision

E167 is a context-alignment diagnostic, not a new submission generator. The E166 focus cells are not target-count-random: they are enriched for edge-like and between-train-runs context, and they concentrate by subject/block more than the permutation null expects. But they are also safety-atlas-divergent: all-veto-null, safe-density, broad-low-alpha, and E101-plausible mass are all lower than matched null sets while E72-active mass is higher. Therefore E166 is a real broad hidden-context sensor, not a safer expected-score file. It should be submitted only when the question is whether the current safety atlas is too conservative; do not scale it up before public feedback.
