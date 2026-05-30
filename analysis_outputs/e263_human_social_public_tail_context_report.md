# E263 Human/Social Context Around Public-Tail Q3 Cells

## Question

E256 lost to E247 on public. Are the four E256-only high-amplitude Q3 cells just numeric smoothing artifacts, or do they sit on recognizable human lifestyle states?

This does not use hidden public labels. It joins E257/E260 Q3 cell groups to the E262 human-social day representation.

## Main Read

- The E256-only group is tiny (`4` rows), so this is a hypothesis generator, not proof.
- The useful object is a JEPA target candidate: predict public-tail cell risk from human diary context, rather than predicting raw app/sensor values.
- If these rows have coherent lifestyle signatures, the next JEPA experiment should mask lifestyle families and predict `Q3 tail-risk / smoothing-validity` as a latent target.

## Top E256-Separating Human/Social Features

| feature | common | e247_only | e256_only | e256_minus_e247only_z | e256_minus_common_z | e256_separation_score |
| --- | --- | --- | --- | --- | --- | --- |
| usage_late_search_browser_time | 8.845466 | 9.038433 | 4.494132 | -4.544301 | -4.351334 | 8.895635 |
| human_late_cognitive_load_subj_z | 0.991756 | 4.101469 | 5.376608 | 1.275140 | 4.384852 | 5.659992 |
| usage_late_social_msg_time | 2.719695 | 2.233827 | 0.473295 | -1.760532 | -2.246400 | 4.006932 |
| human_public_social_presence | 1.461399 | 1.209951 | -0.527964 | -1.737915 | -1.989363 | 3.727278 |
| human_late_cognitive_load | 4.416087 | 7.917794 | 5.643344 | -2.274451 | 1.227257 | 3.501707 |
| hr_heart_rate_mean_mean_day | -0.268962 | -0.713625 | 1.134660 | 1.848285 | 1.403622 | 3.251907 |
| usage_presleep_social_msg_time | 1.035496 | 1.095853 | -0.169299 | -1.265152 | -1.204796 | 2.469948 |
| human_public_social_presence_subj_z | 1.204854 | 1.149569 | -0.049379 | -1.198948 | -1.254233 | 2.453181 |
| human_sleep_onset_risk | 2.204606 | 0.469284 | 0.181332 | -0.287952 | -2.023274 | 2.311226 |
| human_sleep_onset_risk_subj_z | 2.479509 | 1.060163 | 0.668678 | -0.391486 | -1.810831 | 2.202317 |
| human_social_overstim_late | 1.420659 | 1.130788 | 0.185381 | -0.945407 | -1.235278 | 2.180684 |
| usage_presleep_search_browser_time | 0.378072 | 1.711189 | -0.036860 | -1.748049 | -0.414932 | 2.162981 |
| gps_speed_mean_evening | 1.108759 | 1.251712 | 0.270902 | -0.980810 | -0.837856 | 1.818666 |
| screen_m_screen_use_mean_late | 0.700941 | 0.408107 | -0.279641 | -0.687747 | -0.980582 | 1.668329 |
| screen_m_screen_use_mean_presleep | 0.541903 | 0.328256 | -0.361593 | -0.689850 | -0.903496 | 1.593346 |

## E256-Only Group: Largest Lifestyle Outliers

| feature | n | mean_value | mean_test_robust_z | mean_abs_test_robust_z | mean_subject_test_percentile | mean_global_test_percentile |
| --- | --- | --- | --- | --- | --- | --- |
| human_late_cognitive_load | 4 | 273892.380871 | 5.643344 | 6.317833 | 0.704496 | 0.491000 |
| human_late_cognitive_load_subj_z | 4 | 0.692604 | 5.376608 | 5.819132 | 0.704496 | 0.607000 |
| usage_late_search_browser_time | 4 | 171175.750000 | 4.494132 | 5.505868 | 0.833212 | 0.583000 |
| pedo_step_sum_presleep | 4 | 1059.500000 | 1.264785 | 1.871552 | 0.718324 | 0.596000 |
| usage_late_social_msg_time | 4 | 156078.000000 | 0.473295 | 1.460660 | 0.665266 | 0.406000 |
| gps_speed_mean_deepnight | 4 | 0.119913 | 0.125088 | 1.205274 | 0.682749 | 0.358000 |
| human_commute_mobility_subj_z | 4 | 0.559222 | 0.746196 | 1.193301 | 0.677083 | 0.644000 |
| human_social_overstim_late | 4 | 218289.420635 | 0.185381 | 1.184063 | 0.524062 | 0.345000 |
| human_sleep_onset_risk_subj_z | 4 | -0.077723 | 0.668678 | 1.166516 | 0.437439 | 0.490000 |
| hr_heart_rate_mean_mean_day | 4 | 97.105514 | 1.134660 | 1.134660 | 0.796174 | 0.808000 |
| human_physical_fatigue_subj_z | 4 | 0.361103 | 0.388517 | 0.961557 | 0.651925 | 0.636000 |
| usage_presleep_search_browser_time | 4 | 304971.250000 | -0.036860 | 0.903149 | 0.524245 | 0.375000 |
| human_routine_anchor_subj_z | 4 | -0.643165 | -0.491059 | 0.796790 | 0.465461 | 0.311000 |
| gps_speed_mean_evening | 4 | 0.529349 | 0.270902 | 0.723516 | 0.658869 | 0.491000 |
| human_social_overstim_late_subj_z | 4 | -0.166604 | 0.404826 | 0.648260 | 0.524062 | 0.503000 |

## Common E247/E256 Core: Lifestyle Contrast

| feature | n | mean_value | mean_test_robust_z | mean_abs_test_robust_z | mean_subject_test_percentile | mean_global_test_percentile |
| --- | --- | --- | --- | --- | --- | --- |
| usage_late_search_browser_time | 21 | 100048.761905 | 8.845466 | 9.359364 | 0.581773 | 0.595619 |
| human_late_cognitive_load | 21 | 271928.733357 | 4.416087 | 5.013563 | 0.489233 | 0.491429 |
| usage_late_social_msg_time | 21 | 497094.857143 | 2.719695 | 3.165448 | 0.544659 | 0.578476 |
| human_sleep_onset_risk_subj_z | 21 | 0.488261 | 2.479509 | 3.048355 | 0.617740 | 0.548381 |
| human_sleep_onset_risk | 21 | 375.698176 | 2.204606 | 2.621517 | 0.617740 | 0.592762 |
| pedo_step_sum_presleep | 21 | 1182.666667 | 1.490225 | 1.994186 | 0.584393 | 0.585524 |
| human_social_overstim_late | 21 | 531880.259219 | 1.420659 | 1.921823 | 0.512748 | 0.536000 |
| human_public_social_presence | 21 | 17.833929 | 1.461399 | 1.887320 | 0.577342 | 0.554095 |

## Four E256-Only Public-Swing Cells

| row_idx | target | subject_id | lifelog_date | action | prob_delta | swing | expected_focus | support_prob_focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 188 | Q3 | id08 | 2024-08-09 | add_e256_high_amp_cell | -0.033628 | 0.000085 | 0.000024 | 0.367857 |
| 96 | Q3 | id04 | 2024-10-16 | add_e256_high_amp_cell | -0.018814 | 0.000068 | -0.000014 | 0.400000 |
| 87 | Q3 | id04 | 2024-09-19 | add_e256_high_amp_cell | 0.017811 | 0.000056 | 0.000009 | 0.600000 |
| 138 | Q3 | id06 | 2024-07-17 | add_e256_high_amp_cell | 0.017795 | 0.000044 | 0.000001 | 0.600000 |

## Interpretation

E247/E256 should no longer be treated as only a prediction-smoothing story. The public-sensitive Q3 cells can now be inspected as human-day states: late social/contact load, presleep cognitive load, routine/charging stability, commute or deep-night movement, and sensor-measured fatigue.

The next high-value JEPA version should use:

1. context: non-target human diary features from E262, with masks by lifestyle family.
2. target representation: Q3 cell-tail state from E247/E256/E260, not raw Q3 label or raw app reconstruction.
3. LeJEPA health checks: subject/date-block stress, train/test lifestyle shift, and public-anchor group contrast.

## Falsification Rule

This branch dies if an OOF analogue cannot predict held-out Q3 tail-risk better than subject/date priors, or if the learned lifestyle-tail latent only predicts subject identity/train-test split.
