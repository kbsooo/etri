# E273 Human Diary State JEPA Audit

## Question

Can raw lifelog, social stories, and cash-flow stories form a larger hidden lifestyle state that is useful beyond tiny E247-boundary cell surgery?

## Inputs

- E262 raw day-level human/social features.
- E268 explicit human story scores.
- E270 payday/cash-flow story scores.
- E247/E256/E267/E224 candidate geometry for boundary diagnostics.

## Family Representations

| family | n_cols | n_pcs | explained_var_sum | pc1_var | story |
| --- | --- | --- | --- | --- | --- |
| social_comm | 31 | 4 | 0.669856 | 0.271443 | messaging, calls, speech, and passive social isolation |
| cognitive_money | 120 | 4 | 0.420508 | 0.130336 | search, work, shopping, finance, and monthly cash-flow rumination |
| media_game | 36 | 4 | 0.658975 | 0.412517 | media, games, music, and attention entropy |
| bedtime_phone | 120 | 4 | 0.576296 | 0.295920 | bed phone use, charging, light, and sleep-onset fragmentation |
| mobility_context | 120 | 4 | 0.616768 | 0.337625 | home/away, commute, public context, and environmental motion |
| physiology_activity | 120 | 4 | 0.920506 | 0.721547 | steps, physical load, heart rate, and recovery/arousal |
| routine_calendar | 54 | 4 | 0.609746 | 0.240269 | ritual, weekend/workday rhythm, and stable routine |
| sensor_measurement | 109 | 4 | 0.732876 | 0.502784 | device availability, sensor density, and measurement state |

## JEPA Context -> Target Family Predictability

| family | split | target_dim | context_cols | oof_r2 | resid_train_mean | resid_test_mean |
| --- | --- | --- | --- | --- | --- | --- |
| sensor_measurement | dateblock | 4 | 28 | 0.976587 | 1.165202 | 1.088358 |
| sensor_measurement | subject | 4 | 28 | 0.958729 | 1.496475 | 1.467484 |
| physiology_activity | dateblock | 4 | 28 | 0.891374 | 2.240256 | 2.155930 |
| physiology_activity | subject | 4 | 28 | 0.831583 | 2.784348 | 2.789724 |
| mobility_context | dateblock | 4 | 28 | 0.746016 | 3.141525 | 3.033215 |
| bedtime_phone | dateblock | 4 | 28 | 0.735212 | 2.551728 | 2.478204 |
| social_comm | dateblock | 4 | 28 | 0.642126 | 1.665176 | 1.529557 |
| media_game | dateblock | 4 | 28 | 0.632396 | 1.684974 | 1.438297 |
| mobility_context | subject | 4 | 28 | 0.530345 | 4.165996 | 4.151131 |
| social_comm | subject | 4 | 28 | 0.517384 | 1.928968 | 1.765764 |
| media_game | subject | 4 | 28 | 0.490260 | 2.017771 | 1.808037 |
| bedtime_phone | subject | 4 | 28 | 0.440921 | 3.494204 | 3.425712 |
| routine_calendar | dateblock | 4 | 28 | 0.255557 | 2.272147 | 2.136699 |
| routine_calendar | subject | 4 | 28 | -0.055662 | 2.619785 | 2.577770 |
| cognitive_money | dateblock | 4 | 28 | -0.075066 | 6.005571 | 5.801341 |
| cognitive_money | subject | 4 | 28 | -0.136947 | 6.128419 | 6.161536 |

Read: high OOF R2 means a family is predictable from the rest of the diary; high residual energy means a day violates the learned human-state expectation.

## Cluster Health

| k | subject_nmi | subject_ari | test_cluster_entropy | train_cluster_entropy | self_transition_rate | pca_explained_var_first8 |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 0.325717 | 0.129930 | 1.080696 | 1.189349 | 0.776812 | 0.627343 |
| 6 | 0.351220 | 0.136860 | 1.283653 | 1.417675 | 0.747826 | 0.627343 |
| 8 | 0.349076 | 0.166160 | 1.593451 | 1.759090 | 0.608696 | 0.627343 |
| 10 | 0.335682 | 0.159679 | 1.837497 | 2.025910 | 0.510145 | 0.627343 |

## Blocked CV Summary

Diary-state features are added to a calendar/subject-order/subject-id baseline. Negative delta is good.

### By Split

| split | mean | min | max |
| --- | --- | --- | --- |
| dateblock5 | 0.047561770 | 0.014363799 | 0.103297211 |
| subject5 | 0.149546366 | 0.039024595 | 0.221886035 |

### By Target

| target | mean | min | max |
| --- | --- | --- | --- |
| S1 | 0.038622469 | 0.038220343 | 0.039024595 |
| Q3 | 0.076068746 | 0.014363799 | 0.137773692 |
| S3 | 0.091747706 | 0.025735323 | 0.157760089 |
| Q2 | 0.092718565 | 0.060360706 | 0.125076425 |
| S4 | 0.107076893 | 0.022928922 | 0.191224864 |
| Q1 | 0.121052473 | 0.068026087 | 0.174078859 |
| S2 | 0.162591623 | 0.103297211 | 0.221886035 |

### Best Target/Split Rows

| split | target | loss_base | loss_state | delta_logloss | state_feature_count |
| --- | --- | --- | --- | --- | --- |
| dateblock5 | Q3 | 0.681810597 | 0.696174396 | 0.014363799 | 51 |
| dateblock5 | S4 | 0.672891325 | 0.695820247 | 0.022928922 | 51 |
| dateblock5 | S3 | 0.529595741 | 0.555331064 | 0.025735323 | 51 |
| dateblock5 | S1 | 0.581931639 | 0.620151982 | 0.038220343 | 51 |
| subject5 | S1 | 0.645117310 | 0.684141905 | 0.039024595 | 51 |
| dateblock5 | Q2 | 0.708944976 | 0.769305682 | 0.060360706 | 51 |
| dateblock5 | Q1 | 0.677772593 | 0.745798680 | 0.068026087 | 51 |
| dateblock5 | S2 | 0.586453181 | 0.689750393 | 0.103297211 | 51 |
| subject5 | Q2 | 0.735371632 | 0.860448056 | 0.125076425 | 51 |
| subject5 | Q3 | 0.725174873 | 0.862948565 | 0.137773692 | 51 |

### Worst Target/Split Rows

| split | target | loss_base | loss_state | delta_logloss | state_feature_count |
| --- | --- | --- | --- | --- | --- |
| subject5 | S2 | 0.666747428 | 0.888633462 | 0.221886035 | 51 |
| subject5 | S4 | 0.706652435 | 0.897877299 | 0.191224864 | 51 |
| subject5 | Q1 | 0.714675710 | 0.888754569 | 0.174078859 | 51 |
| subject5 | S3 | 0.599936591 | 0.757696680 | 0.157760089 | 51 |
| subject5 | Q3 | 0.725174873 | 0.862948565 | 0.137773692 | 51 |
| subject5 | Q2 | 0.735371632 | 0.860448056 | 0.125076425 | 51 |
| dateblock5 | S2 | 0.586453181 | 0.689750393 | 0.103297211 | 51 |
| dateblock5 | Q1 | 0.677772593 | 0.745798680 | 0.068026087 | 51 |

## Strong Label Lifts

| feature | target | high_minus_low | abs_effect | high_n | low_n |
| --- | --- | --- | --- | --- | --- |
| jepa_prednorm_subject_mobility_context | Q3 | -0.327434 | 0.327434 | 113 | 113 |
| jepa_prednorm_dateblock_mobility_context | Q3 | -0.256637 | 0.256637 | 113 | 113 |
| mobility_context_energy | Q3 | -0.256637 | 0.256637 | 113 | 113 |
| mobility_context_energy | Q1 | -0.230088 | 0.230088 | 113 | 113 |
| jepa_resid_subject_bedtime_phone | Q1 | -0.221239 | 0.221239 | 113 | 113 |
| jepa_resid_dateblock_cognitive_money | S1 | -0.221239 | 0.221239 | 113 | 113 |
| mobility_context_energy | S3 | 0.221239 | 0.221239 | 113 | 113 |
| jepa_resid_subject_sensor_measurement | S1 | -0.212389 | 0.212389 | 113 | 113 |
| jepa_resid_dateblock_bedtime_phone | Q3 | -0.203540 | 0.203540 | 113 | 113 |
| jepa_resid_subject_bedtime_phone | Q3 | -0.203540 | 0.203540 | 113 | 113 |
| jepa_prednorm_subject_bedtime_phone | Q3 | -0.203540 | 0.203540 | 113 | 113 |
| jepa_resid_subject_cognitive_money | S1 | -0.203540 | 0.203540 | 113 | 113 |
| jepa_prednorm_subject_mobility_context | Q1 | -0.203540 | 0.203540 | 113 | 113 |
| jepa_prednorm_dateblock_mobility_context | Q1 | -0.194690 | 0.194690 | 113 | 113 |
| jepa_prednorm_subject_cognitive_money | S3 | 0.194690 | 0.194690 | 113 | 113 |
| diary_state_energy | Q3 | -0.185841 | 0.185841 | 113 | 113 |
| diary_state_pc10 | Q2 | -0.185841 | 0.185841 | 113 | 113 |
| jepa_prednorm_subject_cognitive_money | Q1 | -0.185841 | 0.185841 | 113 | 113 |
| diary_state_pc8 | S1 | -0.185841 | 0.185841 | 113 | 113 |
| jepa_prednorm_subject_routine_calendar | Q3 | -0.185841 | 0.185841 | 113 | 113 |
| diary_state_pc10 | S3 | 0.176991 | 0.176991 | 113 | 113 |
| jepa_prednorm_subject_cognitive_money | Q3 | -0.176991 | 0.176991 | 113 | 113 |
| diary_state_pc1 | Q3 | -0.176991 | 0.176991 | 113 | 113 |
| cognitive_money_energy | S1 | -0.168142 | 0.168142 | 113 | 113 |
| jepa_resid_subject_social_comm | Q3 | -0.168142 | 0.168142 | 113 | 113 |

## E247/E256 Boundary Alignment

| feature | e247_only_d_vs_neutral | e256_only_d_vs_neutral | e247_vs_e256_d | e267_moved_d_vs_neutral | abs_boundary_signal |
| --- | --- | --- | --- | --- | --- |
| jepa_prednorm_subject_social_comm | -0.666275 | 0.291319 | -1.332902 | -0.116002 | 1.332902 |
| diary_state_pc6 | -0.460445 | 0.636984 | -1.239802 | -0.145904 | 1.239802 |
| jepa_resid_dateblock_cognitive_money | 0.526012 | -0.531480 | 1.199200 | 0.083336 | 1.199200 |
| diary_state_pc8 | 0.191764 | -0.918777 | 1.156544 | 0.210373 | 1.156544 |
| diary_state_k10_4 | -0.248758 | 0.824922 | -1.118034 | -0.207861 | 1.118034 |
| diary_state_k6_3 | -0.268432 | 0.740054 | -1.118034 | -0.237204 | 1.118034 |
| diary_state_k8_0 | -0.507546 | 0.131318 | -1.118034 | -0.069394 | 1.118034 |
| diary_state_k8_5 | -0.248758 | 0.824922 | -1.118034 | -0.207861 | 1.118034 |
| jepa_prednorm_subject_mobility_context | -0.511810 | 0.147491 | -0.937272 | -0.168154 | 0.937272 |
| jepa_prednorm_dateblock_mobility_context | -0.398713 | 0.381019 | -0.927377 | -0.173381 | 0.927377 |
| jepa_prednorm_dateblock_social_comm | -0.544312 | -0.129920 | -0.914600 | -0.003413 | 0.914600 |
| cognitive_money_energy | 0.393777 | -0.360503 | 0.820255 | 0.162652 | 0.820255 |
| diary_state_pc10 | 0.013028 | -0.503054 | 0.789844 | -0.042150 | 0.789844 |
| jepa_resid_subject_cognitive_money | 0.333909 | -0.364960 | 0.778954 | -0.015914 | 0.778954 |
| diary_state_pc5 | -0.025453 | 0.617210 | -0.747665 | -0.012553 | 0.747665 |
| jepa_prednorm_dateblock_bedtime_phone | 0.285293 | -0.555246 | 0.703197 | 0.004596 | 0.703197 |
| jepa_prednorm_subject_cognitive_money | -0.601584 | -0.031490 | -0.698292 | 0.279416 | 0.698292 |
| mobility_context_energy | -0.474602 | 0.161052 | -0.671366 | -0.218640 | 0.671366 |
| jepa_resid_subject_mobility_context | -0.465099 | 0.131570 | -0.644267 | -0.217110 | 0.644267 |
| jepa_resid_subject_physiology_activity | -0.443579 | 0.049731 | -0.643658 | 0.035517 | 0.643658 |
| jepa_resid_dateblock_sensor_measurement | 0.263853 | -0.370328 | 0.640947 | -0.145178 | 0.640947 |
| diary_state_k8 | 0.282044 | -0.144663 | 0.631633 | -0.128642 | 0.631633 |
| jepa_resid_subject_bedtime_phone | -0.446797 | 0.188005 | -0.612947 | -0.279221 | 0.612947 |
| jepa_prednorm_dateblock_routine_calendar | -0.171074 | -0.648284 | 0.608845 | 0.141519 | 0.608845 |
| diary_state_energy | -0.168470 | 0.375966 | -0.605910 | 0.042709 | 0.605910 |

## Cluster Stories

| cluster | n_all | n_train | n_test | test_share | dominant_subject | Q1_rate | Q2_rate | Q3_rate | S1_rate | S2_rate | S3_rate | S4_rate | top_story_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 250 | 149 | 101 | 0.404000 | id04 | 0.543624 | 0.570470 | 0.671141 | 0.697987 | 0.684564 | 0.604027 | 0.570470 | music_ambient_late_subj_z:-0.76; vehicle_noise_day_subj_z:-0.69; sensor_sparse_day_subj_z:-0.65; public_social_evening_subj_z:-0.52; home_stability_subj_z:0.46; high_sensor_wear_day_subj_z:0.45; morning_after_badnight_subj_z:0.42; physical_fatigue_subj_z:0.40 |
| 0 | 138 | 91 | 47 | 0.340580 | id09 | 0.505495 | 0.549451 | 0.571429 | 0.714286 | 0.648352 | 0.703297 | 0.560440 | music_ambient_late_subj_z:1.22; outdoor_nature_day_subj_z:0.94; vehicle_noise_day_subj_z:0.90; public_social_evening_subj_z:0.89; late_msg_call_subj_z:0.56; social_isolation_media_subj_z:-0.48; night_out_mobility_subj_z:0.47; home_stability_subj_z:-0.40 |
| 7 | 138 | 91 | 47 | 0.340580 | id02 | 0.505495 | 0.604396 | 0.659341 | 0.714286 | 0.703297 | 0.648352 | 0.670330 | home_stability_subj_z:-0.53; commute_workday_subj_z:0.33; deepnight_phone_awake_subj_z:-0.33; weekend_ritual_rest_subj_z:-0.32; vehicle_noise_day_subj_z:0.31; presleep_msg_drag_subj_z:-0.30; phone_in_bed_subj_z:-0.30; low_hr_recovery_subj_z:-0.30 |
| 1 | 74 | 44 | 30 | 0.405405 | id01 | 0.431818 | 0.568182 | 0.568182 | 0.613636 | 0.590909 | 0.795455 | 0.454545 | heart_stress_late_subj_z:0.38; pay20_near7_calendar_only_subj_z:-0.37; paymonth_start_post3_relief_home_subj_z:0.36; monthstart_reset_relief_subj_z:0.29; paymonth_start_post3_late_shopping_subj_z:0.29; pay10_near3_money_rumination_subj_z:0.28; pay25_pre7_budget_squeeze_subj_z:-0.28; paymonth_start_post7_spend_outing_subj_z:0.28 |
| 4 | 34 | 30 | 4 | 0.117647 | id04 | 0.600000 | 0.466667 | 0.666667 | 0.666667 | 0.500000 | 0.533333 | 0.433333 | high_sensor_wear_day_subj_z:-1.70; sensor_sparse_day_subj_z:1.64; physical_fatigue_subj_z:-1.54; overtraining_arousal_subj_z:-1.43; sedentary_screen_day_subj_z:1.29; human_physical_fatigue_subj_z:-1.23; outdoor_nature_day_subj_z:-1.22; low_hr_recovery_subj_z:1.04 |
| 5 | 26 | 12 | 14 | 0.538462 | id08 | 0.333333 | 0.416667 | 0.000000 | 0.250000 | 0.500000 | 0.666667 | 0.500000 | pay10_post3_relief_home_subj_z:0.75; night_out_mobility_subj_z:-0.74; public_social_evening_subj_z:-0.71; physical_fatigue_subj_z:0.57; vehicle_noise_day_subj_z:-0.54; home_stability_subj_z:0.48; overtraining_arousal_subj_z:0.47; human_public_social_presence_subj_z:-0.47 |
| 2 | 20 | 18 | 2 | 0.100000 | id08 | 0.333333 | 0.888889 | 0.500000 | 0.500000 | 0.555556 | 0.833333 | 0.333333 | high_sensor_wear_day_subj_z:-1.14; sensor_sparse_day_subj_z:1.11; physical_fatigue_subj_z:-1.10; overtraining_arousal_subj_z:-1.03; outdoor_nature_day_subj_z:-1.00; human_physical_fatigue_subj_z:-0.98; low_hr_recovery_subj_z:0.98; sedentary_screen_day_subj_z:0.97 |
| 6 | 20 | 15 | 5 | 0.250000 | id06 | 0.200000 | 0.200000 | 0.266667 | 0.933333 | 0.733333 | 0.733333 | 0.666667 | presleep_msg_drag_subj_z:-1.94; app_entropy_scattered_day_subj_z:-1.87; single_app_monotony_subj_z:1.85; sedentary_screen_day_subj_z:-1.79; social_isolation_media_subj_z:1.36; phone_in_bed_subj_z:-1.32; media_binge_late_subj_z:-1.31; morning_after_badnight_subj_z:-0.94 |

## Decision

The current diary-state construction is diagnostic rather than action-grade. It explains some labels and boundary cells but does not improve blocked CV enough to justify a submission.

- best target/split delta: `0.014363799`
- dateblock mean delta: `0.047561770`
- subject mean delta: `0.149546366`

Next action: if alive, materialize only a larger target-specific candidate that passes E272 public-free promotion; otherwise rebuild the state representation with sharper subject/block priors.

## Files

- `e273_human_diary_state_jepa_audit_features.parquet`
- `e273_human_diary_state_jepa_audit_family_summary.csv`
- `e273_human_diary_state_jepa_audit_cv.csv`
- `e273_human_diary_state_jepa_audit_label_lift.csv`
- `e273_human_diary_state_jepa_audit_boundary.csv`
- `e273_human_diary_state_jepa_audit_clusters.csv`
