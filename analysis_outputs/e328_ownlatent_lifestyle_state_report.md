# E328 Own-Latent Lifestyle-State Experiment

## Question

Can a learned hidden lifestyle state, built from human/social context and own-latent prediction, explain both labels and the E247/E323 public sensor boundary?

## JEPA / Own-Latent Construction

- Teacher: PCA latent from all lifestyle context views, fitted on train days.
- Students: masked context views predict teacher PCs under subject/dateblock OOF splits.
- State: PCA + kmeans on student predictions and residual energies.
- Target is learned latent representation, not raw feature reconstruction.

## View Predictability

| view_id | split | context_cols | teacher_dims | oof_teacher_r2 | resid_energy_train_mean | resid_energy_test_mean | explained_var_sum | participation_ratio | anisotropy | teacher_explained_var_sum | teacher_participation_ratio | teacher_anisotropy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_story | dateblock | 280 | 12 | 0.972508 | 0.679666 | 0.607482 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| family_story | dateblock | 248 | 12 | 0.968609 | 0.726377 | 0.654935 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| family | dateblock | 40 | 12 | 0.916472 | 1.195947 | 1.127773 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| family_jepa_story | subject | 280 | 12 | 0.902893 | 1.269700 | 0.607482 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| family_story | subject | 248 | 12 | 0.886121 | 1.360834 | 0.654935 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| family | subject | 40 | 12 | 0.842690 | 1.619655 | 1.127773 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| story_bundle | dateblock | 208 | 12 | 0.776162 | 1.892624 | 1.680525 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| story_bundle | subject | 208 | 12 | 0.558777 | 2.683663 | 1.680525 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| raw_day | dateblock | 160 | 12 | 0.452752 | 3.061406 | 2.890440 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| jepa_resid | dateblock | 32 | 12 | 0.421244 | 3.193601 | 3.099187 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| jepa_resid | subject | 32 | 12 | 0.160737 | 3.775347 | 3.099187 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| raw_day | subject | 160 | 12 | 0.079867 | 3.840100 | 2.890440 |  |  |  | 0.500311 | 8.646519 | 2.576270 |
| own_lifestyle_state | train_geometry | 96 | 8 |  | 2.108243 | 1.676724 | 0.777381 | 5.829640 | 3.261151 | 0.500311 | 8.646519 | 2.576270 |

## Label Stress

Negative delta is good. The null columns shuffle the same latent by row/subject/dateblock.

| split | actual_delta_mean | actual_delta_best | actual_delta_worst | targets_improved | null_best | null_median | null_q20 | dominance | placebo_adjusted_vs_median | label_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject | 0.035211637 | 0.004534832 | 0.087219912 | 0 | 0.014935816 | 0.036667575 | 0.029423608 | 0.600000000 | -0.001455938 | False |
| dateblock | 0.022631387 | 0.014601032 | 0.035164372 | 0 | 0.011367880 | 0.023277245 | 0.016852385 | 0.533333333 | -0.000645858 | False |

### Target Detail

| split | target | base_loss | ownlatent_loss | delta_logloss |
| --- | --- | --- | --- | --- |
| subject | S2 | 0.686272549 | 0.690807381 | 0.004534832 |
| subject | Q3 | 0.684812169 | 0.697011428 | 0.012199259 |
| dateblock | Q3 | 0.675642560 | 0.690243592 | 0.014601032 |
| subject | S1 | 0.642635844 | 0.658893492 | 0.016257648 |
| dateblock | S3 | 0.531727381 | 0.548120852 | 0.016393471 |
| dateblock | S4 | 0.657011186 | 0.676001615 | 0.018990429 |
| dateblock | Q1 | 0.675655442 | 0.694775150 | 0.019119707 |
| subject | S3 | 0.680037639 | 0.701023060 | 0.020985422 |
| dateblock | Q2 | 0.693912051 | 0.718562006 | 0.024649955 |
| dateblock | S1 | 0.580425377 | 0.609926118 | 0.029500740 |
| dateblock | S2 | 0.577395701 | 0.612560073 | 0.035164372 |
| subject | S4 | 0.699162812 | 0.742372936 | 0.043210123 |
| subject | Q2 | 0.697624975 | 0.759699239 | 0.062074265 |
| subject | Q1 | 0.708250668 | 0.795470580 | 0.087219912 |

## Public-Sensor Boundary Alignment

| feature | e247_vs_e256_d | e323_top20_d_vs_rest | e247_only_d_vs_neutral | e256_only_d_vs_neutral | abs_boundary_signal |
| --- | --- | --- | --- | --- | --- |
| ownlife_k8_0 | -1.477419 | -0.267756 | -0.489104 | 0.734952 | 1.477419 |
| ownlife_pc6 | 1.189473 | 0.247522 | 0.431166 | -0.493427 | 1.189473 |
| ownlife_energy | 1.091194 | 0.022876 | 0.054717 | -0.543266 | 1.091194 |
| ownlife_global_distance | 1.091194 | 0.022876 | 0.054717 | -0.543266 | 1.091194 |
| ownlife_k8_5 | 0.849208 | 0.115793 | 0.536811 | -0.464085 | 0.849208 |
| ownlife_k8_3 | 0.716115 | 0.545557 | 0.465174 | -0.407942 | 0.716115 |
| ownlife_pc3 | -0.644586 | -0.435687 | 0.056550 | 0.306681 | 0.644586 |
| ownlife_pc4 | 0.543765 | 0.024185 | -0.308389 | -0.623360 | 0.543765 |
| ownlife_cluster_distance | 0.505526 | -0.091787 | -0.284707 | -0.755678 | 0.505526 |
| ownlife_pc5 | -0.482164 | -0.142714 | -0.193693 | 0.469527 | 0.482164 |
| ownlife_student_resid_max | 0.432689 | 0.241661 | -0.151221 | -0.517519 | 0.432689 |
| ownlife_pc7 | -0.036466 | 0.286839 | -0.149635 | -0.124800 | 0.286839 |
| ownlife_k8_2 | 0.000000 | -0.274411 | -0.370480 | -0.363584 | 0.274411 |
| ownlife_pc1 | 0.261017 | -0.161747 | -0.297314 | -0.522103 | 0.261017 |
| ownlife_k8_1 | -0.238293 | -0.224725 | 0.409827 | 0.824922 | 0.238293 |
| ownlife_student_resid_mean | 0.220313 | 0.182347 | -0.330360 | -0.503798 | 0.220313 |
| ownlife_k8_6 | 0.000000 | 0.207478 | -0.338666 | -0.332361 | 0.207478 |
| ownlife_pc8 | -0.145879 | 0.094123 | -0.030698 | 0.079899 | 0.145879 |
| ownlife_k8_4 | 0.000000 | -0.137416 | -0.116873 | -0.114697 | 0.137416 |
| ownlife_pc2 | -0.136588 | -0.054471 | -0.715095 | -0.552990 | 0.136588 |

## Lifestyle State Clusters

| cluster | n_test | e247_only_rate | e256_only_rate | e323_top20_rate | e323_l1_mean | ownlife_energy_mean | top_subject | n_train | dominant_subject | Q1_rate | Q2_rate | Q3_rate | S1_rate | S2_rate | S3_rate | S4_rate | top_story_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 37 | 0.108108 | 0.000000 | 0.405405 | 0.258547 | 2.595804 | id02 | 78 | id04 | 0.538462 | 0.641026 | 0.589744 | 0.705128 | 0.576923 | 0.512821 | 0.564103 | payeom_post3_late_shopping_subj_z:1.43; paymonth_start_post3_late_shopping_subj_z:1.40; monthstart_reset_relief_subj_z:1.34; monthstart_spending_reset_subj_z:1.20; paymonth_start_near7_calendar_only_subj_z:1.14; payeom_near7_calendar_only_subj_z:1.11; pay20_near7_calendar_only_subj_z:-1.05; pay15_near7_calendar_only_subj_z:-1.05 |
| 6 | 23 | 0.000000 | 0.000000 | 0.304348 | 0.191723 | 3.781523 | id10 | 36 | id10 | 0.555556 | 0.611111 | 0.611111 | 0.611111 | 0.722222 | 0.638889 | 0.750000 | weekday_routine_pressure_subj_z:-1.21; weekend_ritual_rest_subj_z:1.14; commute_workday_subj_z:-1.07; weekend_social_jetlag_subj_z:1.06; physical_fatigue_subj_z:-0.96; morning_after_badnight_subj_z:-0.84; deepnight_phone_awake_subj_z:0.65; quiet_dark_bedtime_subj_z:-0.64 |
| 5 | 46 | 0.108696 | 0.000000 | 0.239130 | 0.191940 | 2.587879 | id07 | 95 | id08 | 0.431579 | 0.557895 | 0.578947 | 0.631579 | 0.652632 | 0.652632 | 0.536842 | pay25_near7_calendar_only_subj_z:1.23; payeom_pre7_budget_squeeze_subj_z:1.18; pay10_near7_calendar_only_subj_z:-1.18; pay25_post3_late_shopping_subj_z:1.10; paymonth_start_pre7_budget_squeeze_subj_z:1.06; eom_bill_anxiety_subj_z:0.90; pay15_near7_calendar_only_subj_z:-0.87; payeom_pre3_cash_stress_subj_z:0.85 |
| 0 | 96 | 0.020833 | 0.031250 | 0.145833 | 0.160887 | 2.435890 | id06 | 120 | id02 | 0.558333 | 0.525000 | 0.666667 | 0.725000 | 0.741667 | 0.725000 | 0.600000 | pay15_near7_calendar_only_subj_z:1.32; payeom_near7_calendar_only_subj_z:-1.27; paymonth_start_near7_calendar_only_subj_z:-1.17; pay10_post3_late_shopping_subj_z:0.78; pay20_pre7_budget_squeeze_subj_z:0.72; pay15_pre7_budget_squeeze_subj_z:0.72; pay15_post3_late_shopping_subj_z:0.64; overtraining_arousal_subj_z:0.64 |
| 2 | 27 | 0.000000 | 0.000000 | 0.074074 | 0.147072 | 4.004092 | id01 | 38 | id01 | 0.421053 | 0.578947 | 0.605263 | 0.631579 | 0.605263 | 0.842105 | 0.473684 | morning_after_badnight_abs_subj_z:-0.33; finance_shopping_stress_abs_subj_z:-0.24; outdoor_nature_day_abs_subj_z:-0.22; ritual_anchor_abs_subj_z:-0.22; morning_after_badnight_subj_z:0.21; media_binge_late_abs_subj_z:0.18; music_ambient_late_abs_subj_z:-0.18; pay25_post3_relief_home_subj_z:-0.18 |
| 1 | 16 | 0.125000 | 0.062500 | 0.062500 | 0.116181 | 2.966406 | id04 | 42 | id04 | 0.547619 | 0.476190 | 0.619048 | 0.761905 | 0.619048 | 0.642857 | 0.428571 | physical_fatigue_subj_z:-1.77; high_sensor_wear_day_subj_z:-1.75; overtraining_arousal_subj_z:-1.65; sensor_sparse_day_subj_z:1.64; sedentary_screen_day_subj_z:1.39; outdoor_nature_day_subj_z:-1.21; low_hr_recovery_subj_z:1.18; heart_stress_late_subj_z:-0.90 |
| 4 | 3 | 0.000000 | 0.000000 | 0.000000 | 0.094735 | 4.524838 | id09 | 17 | id06 | 0.294118 | 0.235294 | 0.235294 | 0.941176 | 0.588235 | 0.647059 | 0.647059 | presleep_msg_drag_subj_z:-2.03; sedentary_screen_day_subj_z:-2.02; app_entropy_scattered_day_subj_z:-1.94; single_app_monotony_subj_z:1.94; media_binge_late_subj_z:-1.74; social_isolation_media_subj_z:1.52; late_msg_call_subj_z:-1.29; presleep_msg_drag_abs_subj_z:1.21 |
| 7 | 2 | 0.000000 | 0.000000 | 0.000000 | 0.041946 | 4.233997 | id08 | 24 | id08 | 0.375000 | 0.791667 | 0.583333 | 0.458333 | 0.500000 | 0.666667 | 0.458333 | sensor_sparse_day_subj_z:1.29; high_sensor_wear_day_subj_z:-1.26; physical_fatigue_subj_z:-1.19; morning_after_badnight_subj_z:-1.15; overtraining_arousal_subj_z:-1.13; weekday_routine_pressure_subj_z:-1.01; outdoor_nature_day_subj_z:-0.98; commute_workday_subj_z:-0.98 |

## Anti-E323 Candidate Probe

| candidate_id | file | basename | gate | weight | changed_rows | changed_cells | mean_abs_logit_move | max_abs_logit_move | top20_abs_move_share | latent_risk_top20_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| anti_e323_softtail_w0p015 | analysis_outputs/submission_e328_ownlatent_anti_e323_softtail_w0p015_aa16c169.csv | submission_e328_ownlatent_anti_e323_softtail_w0p015_aa16c169.csv | softtail | 0.015000000 | 249 | 987 | 0.000168771 | 0.004782104 | 0.371859224 | 50 |
| anti_e323_softtail_w0p025 | analysis_outputs/submission_e328_ownlatent_anti_e323_softtail_w0p025_1f459c14.csv | submission_e328_ownlatent_anti_e323_softtail_w0p025_1f459c14.csv | softtail | 0.025000000 | 250 | 1221 | 0.000281284 | 0.007970173 | 0.371859224 | 50 |
| anti_e323_softtail_w0p04 | analysis_outputs/submission_e328_ownlatent_anti_e323_softtail_w0p04_a1bc4a8f.csv | submission_e328_ownlatent_anti_e323_softtail_w0p04_a1bc4a8f.csv | softtail | 0.040000000 | 250 | 1411 | 0.000450055 | 0.012752277 | 0.371859224 | 50 |
| anti_e323_softtail_w0p06 | analysis_outputs/submission_e328_ownlatent_anti_e323_softtail_w0p06_53129290.csv | submission_e328_ownlatent_anti_e323_softtail_w0p06_53129290.csv | softtail | 0.060000000 | 250 | 1520 | 0.000675082 | 0.019128416 | 0.371859224 | 50 |
| anti_e323_hardtop20_w0p015 | analysis_outputs/submission_e328_ownlatent_anti_e323_hardtop20_w0p015_b877c668.csv | submission_e328_ownlatent_anti_e323_hardtop20_w0p015_b877c668.csv | hardtop20 | 0.015000000 | 50 | 284 | 0.000078028 | 0.005250000 | 1.000000000 | 50 |
| anti_e323_hardtop20_w0p025 | analysis_outputs/submission_e328_ownlatent_anti_e323_hardtop20_w0p025_bc134b7e.csv | submission_e328_ownlatent_anti_e323_hardtop20_w0p025_bc134b7e.csv | hardtop20 | 0.025000000 | 50 | 313 | 0.000130046 | 0.008750000 | 1.000000000 | 50 |
| anti_e323_hardtop20_w0p04 | analysis_outputs/submission_e328_ownlatent_anti_e323_hardtop20_w0p04_e0a74913.csv | submission_e328_ownlatent_anti_e323_hardtop20_w0p04_e0a74913.csv | hardtop20 | 0.040000000 | 50 | 326 | 0.000208074 | 0.014000000 | 1.000000000 | 50 |
| anti_e323_hardtop20_w0p06 | analysis_outputs/submission_e328_ownlatent_anti_e323_hardtop20_w0p06_c116957c.csv | submission_e328_ownlatent_anti_e323_hardtop20_w0p06_c116957c.csv | hardtop20 | 0.060000000 | 50 | 336 | 0.000312111 | 0.021000000 | 1.000000000 | 50 |

## Public-Free Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p015_b877c668.csv | below_selector_resolution | 0.000001219 | -0.000000096 | 0.000003164 | 0.277777778 | 0.000064229 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p025_bc134b7e.csv | below_selector_resolution | 0.000001971 | -0.000000175 | 0.000005137 | 0.291666667 | 0.000107048 |
| submission_e328_ownlatent_anti_e323_softtail_w0p015_aa16c169.csv | below_selector_resolution | 0.000001784 | -0.000000213 | 0.000005636 | 0.138888889 | 0.000110771 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p04_e0a74913.csv | below_selector_resolution | 0.000003077 | -0.000000308 | 0.000008076 | 0.319444444 | 0.000171277 |
| submission_e328_ownlatent_anti_e323_softtail_w0p025_1f459c14.csv | below_selector_resolution | 0.000002740 | -0.000000445 | 0.000008701 | 0.138888889 | 0.000184619 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p06_c116957c.csv | below_selector_resolution | 0.000004530 | -0.000000535 | 0.000012011 | 0.333333333 | 0.000256915 |
| submission_e328_ownlatent_anti_e323_softtail_w0p04_a1bc4a8f.csv | below_selector_resolution | 0.000004202 | -0.000000986 | 0.000013296 | 0.138888889 | 0.000295390 |
| submission_e328_ownlatent_anti_e323_softtail_w0p06_53129290.csv | below_selector_resolution | 0.000006092 | -0.000001028 | 0.000019177 | 0.152777778 | 0.000443085 |

## Candidate Anatomy

| basename | cos_with_e323_bad_delta | l1_ratio_to_e323_delta | changed_rows | changed_cells | mean_abs_logit_delta | max_abs_prob_delta |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p015_b877c668.csv | -0.428900733 | 0.003072085 | 50 | 284 | 0.000078028 | 0.001071535 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p025_bc134b7e.csv | -0.428900733 | 0.005120141 | 50 | 313 | 0.000130046 | 0.001785283 |
| submission_e328_ownlatent_anti_e323_softtail_w0p015_aa16c169.csv | -0.900533492 | 0.006644790 | 249 | 987 | 0.000168771 | 0.000985217 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p04_e0a74913.csv | -0.428900733 | 0.008192225 | 50 | 326 | 0.000208074 | 0.002854988 |
| submission_e328_ownlatent_anti_e323_softtail_w0p025_1f459c14.csv | -0.900533492 | 0.011074650 | 250 | 1221 | 0.000281284 | 0.001641515 |
| submission_e328_ownlatent_anti_e323_hardtop20_w0p06_c116957c.csv | -0.428900733 | 0.012288338 | 50 | 336 | 0.000312111 | 0.004279531 |
| submission_e328_ownlatent_anti_e323_softtail_w0p04_a1bc4a8f.csv | -0.900533492 | 0.017719440 | 250 | 1411 | 0.000450055 | 0.002625186 |
| submission_e328_ownlatent_anti_e323_softtail_w0p06_53129290.csv | -0.900533492 | 0.026579160 | 250 | 1520 | 0.000675082 | 0.003935288 |

## Decision

This own-latent construction did not find a strong enough lifestyle-state invariant. Do not submit its candidates; rebuild the state target or use a different negative anchor.

- best boundary signal: `0.545557`
- any label-stress negative mean: `False`
- strict promote count: `0`

## Files

- `e328_ownlatent_lifestyle_state_features.parquet`
- `e328_ownlatent_lifestyle_state_view_summary.csv`
- `e328_ownlatent_lifestyle_state_label_stress.csv`
- `e328_ownlatent_lifestyle_state_target_detail.csv`
- `e328_ownlatent_lifestyle_state_boundary_alignment.csv`
- `e328_ownlatent_lifestyle_state_cluster_summary.csv`
- `e328_ownlatent_lifestyle_state_candidates.csv`
- `e328_ownlatent_lifestyle_state_candidate_scores.csv`
- `e328_ownlatent_lifestyle_state_candidate_anatomy.csv`
