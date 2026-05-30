# E288 Lifestyle-Bundle JEPA Audit

## Question

Can multiple human/social stories form a hidden lifestyle state that is reconstructable from raw day context and useful for labels beyond matched nulls?

## Story Bundle

- stories used: `28`
- selected from E280 by transfer survival score, including mobility/commute, bright light, routine fragmentation, app entropy, heart stress, and cash-flow/payday stories.

| story | source | mapped_family | transfer_survival_score | e280_verdict |
| --- | --- | --- | --- | --- |
| commute_workday | human_social | mobility_context | 0.791906 | alive_for_story_state_gate |
| bright_light_late | human_social | bedtime_phone | 0.781993 | alive_for_story_state_gate |
| vehicle_noise_day | human_social | mobility_context | 0.716287 | diagnostic_story_only |
| single_app_monotony | human_social | routine_calendar | 0.716179 | alive_but_needs_transfer_test |
| app_entropy_scattered_day | human_social | routine_calendar | 0.649240 | alive_but_needs_transfer_test |
| heart_stress_late | human_social | physiology_activity | 0.613616 | alive_but_needs_transfer_test |
| outdoor_nature_day | human_social | mobility_context | 0.602621 | diagnostic_story_only |
| morning_after_badnight | human_social | diary_global | 0.593819 | alive_for_story_state_gate |
| quiet_dark_bedtime | human_social | routine_calendar | 0.582313 | alive_but_needs_transfer_test |
| media_binge_late | human_social | media_game | 0.580289 | diagnostic_story_only |
| night_out_mobility | human_social | mobility_context | 0.567439 | diagnostic_story_only |
| weekday_routine_pressure | human_social | routine_calendar | 0.561285 | diagnostic_story_only |
| phone_in_bed | human_social | bedtime_phone | 0.554765 | public_anchor_diagnostic_only |
| paymonth_start_post7_spend_outing | cashflow | cognitive_money | 0.553285 | alive_but_needs_transfer_test |
| monthstart_spending_reset | cashflow | cognitive_money | 0.551867 | alive_but_needs_transfer_test |
| paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.551476 | alive_but_needs_transfer_test |
| weekend_ritual_rest | human_social | routine_calendar | 0.550726 | public_anchor_diagnostic_only |
| low_hr_recovery | human_social | physiology_activity | 0.549628 | diagnostic_story_only |
| ritual_anchor | human_social | routine_calendar | 0.546187 | alive_but_needs_transfer_test |
| sedentary_screen_day | human_social | media_game | 0.531442 | diagnostic_story_only |
| afterwork_recovery | human_social | mobility_context | 0.528594 | diagnostic_story_only |
| screen_fragmentation | human_social | bedtime_phone | 0.526405 | diagnostic_story_only |
| charge_bed_anchor | human_social | routine_calendar | 0.522064 | alive_but_needs_transfer_test |
| overtraining_arousal | human_social | physiology_activity | 0.519324 | alive_but_needs_transfer_test |
| deepnight_phone_awake | human_social | bedtime_phone | 0.515715 | diagnostic_story_only |
| payeom_post3_late_shopping | cashflow | cognitive_money | 0.508376 | alive_but_needs_transfer_test |
| pay20_post3_relief_home | cashflow | routine_calendar | 0.504515 | alive_but_needs_transfer_test |
| pay25_pre3_cash_stress | cashflow | cognitive_money | 0.499454 | alive_but_needs_transfer_test |

## Reconstruction Summary

| view_id | split | context_cols | story_count | story_r2_mean | story_r2_median | story_r2_min | story_r2_positive_rate | latent_dims | explained_var_sum | participation_ratio | anisotropy | best_label_delta_mean | label_gate_any |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | 126 | 28 | 0.385944 | 0.379369 | -0.073564 | 0.928571 | 6.000000 | 0.680789 | 5.131048 | 1.890916 | 0.005250 | False |
| hybrid_context | dateblock5 | 246 | 28 | 0.291692 | 0.452032 | -0.984357 | 0.857143 | 6.000000 | 0.626992 | 5.358072 | 1.645815 | 0.002443 | False |
| family_jepa_context | subject5 | 126 | 28 | -0.036976 | 0.019739 | -2.119778 | 0.535714 | 6.000000 | 0.702582 | 5.185624 | 1.753152 | 0.007517 | False |
| raw_human_context | dateblock5 | 260 | 28 | -0.113906 | -0.061976 | -0.994171 | 0.392857 | 6.000000 | 0.674073 | 5.212763 | 1.740120 | 0.002093 | False |
| hybrid_context | subject5 | 246 | 28 | -0.230447 | -0.054118 | -1.480673 | 0.464286 | 6.000000 | 0.643806 | 5.256527 | 1.659420 | 0.028632 | False |
| raw_human_context | subject5 | 260 | 28 | -2.485787 | -1.181823 | -21.758683 | 0.107143 | 6.000000 | 0.770854 | 3.863454 | 2.612956 | 0.066675 | False |

## Story-Level Reconstruction

| view_id | split | story | source | mapped_family | r2 | corr |
| --- | --- | --- | --- | --- | --- | --- |
| raw_human_context | dateblock5 | heart_stress_late | human_social | physiology_activity | 0.852864 | 0.925495 |
| family_jepa_context | dateblock5 | paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.813342 | 0.902112 |
| hybrid_context | dateblock5 | heart_stress_late | human_social | physiology_activity | 0.797935 | 0.894681 |
| family_jepa_context | dateblock5 | app_entropy_scattered_day | human_social | routine_calendar | 0.739960 | 0.860488 |
| hybrid_context | dateblock5 | paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.721263 | 0.854321 |
| family_jepa_context | dateblock5 | vehicle_noise_day | human_social | mobility_context | 0.704754 | 0.842160 |
| hybrid_context | dateblock5 | app_entropy_scattered_day | human_social | routine_calendar | 0.678340 | 0.826087 |
| family_jepa_context | dateblock5 | outdoor_nature_day | human_social | mobility_context | 0.673177 | 0.822955 |
| hybrid_context | dateblock5 | outdoor_nature_day | human_social | mobility_context | 0.662628 | 0.821006 |
| raw_human_context | dateblock5 | media_binge_late | human_social | media_game | 0.656167 | 0.814862 |
| family_jepa_context | subject5 | paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.654106 | 0.823228 |
| family_jepa_context | dateblock5 | payeom_post3_late_shopping | cashflow | cognitive_money | 0.646341 | 0.804857 |
| family_jepa_context | subject5 | payeom_post3_late_shopping | cashflow | cognitive_money | 0.625435 | 0.794967 |
| hybrid_context | dateblock5 | vehicle_noise_day | human_social | mobility_context | 0.618202 | 0.799976 |
| family_jepa_context | dateblock5 | morning_after_badnight | human_social | diary_global | 0.617591 | 0.790852 |
| hybrid_context | dateblock5 | deepnight_phone_awake | human_social | bedtime_phone | 0.614965 | 0.799813 |
| family_jepa_context | dateblock5 | weekend_ritual_rest | human_social | routine_calendar | 0.608033 | 0.782621 |
| family_jepa_context | dateblock5 | sedentary_screen_day | human_social | media_game | 0.601644 | 0.780531 |
| family_jepa_context | dateblock5 | single_app_monotony | human_social | routine_calendar | 0.582670 | 0.763882 |
| family_jepa_context | dateblock5 | commute_workday | human_social | mobility_context | 0.574685 | 0.763199 |
| family_jepa_context | subject5 | app_entropy_scattered_day | human_social | routine_calendar | 0.574625 | 0.791138 |
| raw_human_context | dateblock5 | deepnight_phone_awake | human_social | bedtime_phone | 0.570129 | 0.777097 |
| hybrid_context | dateblock5 | sedentary_screen_day | human_social | media_game | 0.556058 | 0.763730 |
| hybrid_context | dateblock5 | overtraining_arousal | human_social | physiology_activity | 0.528202 | 0.749806 |
| hybrid_context | subject5 | paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.528197 | 0.766238 |
| hybrid_context | dateblock5 | payeom_post3_late_shopping | cashflow | cognitive_money | 0.526541 | 0.740405 |
| hybrid_context | dateblock5 | commute_workday | human_social | mobility_context | 0.525478 | 0.755257 |
| hybrid_context | subject5 | app_entropy_scattered_day | human_social | routine_calendar | 0.524438 | 0.761235 |
| hybrid_context | dateblock5 | weekday_routine_pressure | human_social | routine_calendar | 0.519985 | 0.742473 |
| hybrid_context | dateblock5 | media_binge_late | human_social | media_game | 0.489088 | 0.740731 |

## Label Stress

| view_id | split | rep | actual_delta_mean | actual_delta_best | actual_delta_worst | targets_improved | null_median | null_best | dominance | label_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_human_context | dateblock5 | cluster6 | 0.002093 | -0.009653 | 0.013891 | 3 | 0.005473 | 0.000824 | 0.972222 | False |
| hybrid_context | dateblock5 | cluster6 | 0.002443 | -0.006452 | 0.008914 | 2 | 0.007824 | 0.002829 | 1.000000 | False |
| family_jepa_context | dateblock5 | cluster6 | 0.005250 | -0.013125 | 0.016532 | 1 | 0.008145 | 0.001837 | 0.805556 | False |
| family_jepa_context | subject5 | cluster6 | 0.007517 | -0.003437 | 0.011187 | 1 | 0.008014 | 0.003011 | 0.555556 | False |
| hybrid_context | dateblock5 | pc | 0.007659 | 0.000293 | 0.017910 | 0 | 0.011972 | 0.004827 | 0.777778 | False |
| family_jepa_context | dateblock5 | pc | 0.008305 | -0.006200 | 0.018734 | 2 | 0.009175 | 0.003071 | 0.611111 | False |
| raw_human_context | dateblock5 | pc | 0.009304 | -0.003654 | 0.022746 | 2 | 0.014091 | 0.005660 | 0.944444 | False |
| hybrid_context | subject5 | pc | 0.028632 | -0.000358 | 0.049414 | 1 | 0.017245 | 0.003376 | 0.194444 | False |
| family_jepa_context | subject5 | pc | 0.031728 | 0.010233 | 0.060638 | 0 | 0.016674 | 0.004227 | 0.277778 | False |
| raw_human_context | subject5 | pc | 0.066675 | -0.014466 | 0.170242 | 1 | 0.029409 | 0.008858 | 0.055556 | False |
| hybrid_context | subject5 | cluster6 | 0.085220 | 0.027857 | 0.142757 | 0 | 0.085369 | 0.002671 | 0.500000 | False |
| raw_human_context | subject5 | cluster6 | 0.150878 | 0.047437 | 0.303535 | 0 | 0.089403 | 0.005985 | 0.027778 | False |

## Best Target Deltas

| view_id | split | rep | target | base_loss | rep_loss | delta_logloss |
| --- | --- | --- | --- | --- | --- | --- |
| raw_human_context | subject5 | pc | Q3 | 0.694383 | 0.679917 | -0.014466 |
| family_jepa_context | dateblock5 | cluster6 | S4 | 0.670940 | 0.657815 | -0.013125 |
| raw_human_context | dateblock5 | cluster6 | S4 | 0.670940 | 0.661287 | -0.009653 |
| hybrid_context | dateblock5 | cluster6 | Q3 | 0.679848 | 0.673396 | -0.006452 |
| family_jepa_context | dateblock5 | pc | Q3 | 0.679848 | 0.673649 | -0.006200 |
| hybrid_context | dateblock5 | cluster6 | S2 | 0.583578 | 0.578430 | -0.005149 |
| raw_human_context | dateblock5 | pc | S1 | 0.578496 | 0.574841 | -0.003654 |
| family_jepa_context | subject5 | cluster6 | Q3 | 0.694383 | 0.690946 | -0.003437 |
| raw_human_context | dateblock5 | cluster6 | S2 | 0.583578 | 0.580571 | -0.003008 |
| raw_human_context | dateblock5 | cluster6 | Q3 | 0.679848 | 0.677401 | -0.002447 |
| hybrid_context | subject5 | pc | Q3 | 0.694383 | 0.694026 | -0.000358 |
| family_jepa_context | dateblock5 | pc | S4 | 0.670940 | 0.670597 | -0.000343 |
| raw_human_context | dateblock5 | pc | S4 | 0.670940 | 0.670612 | -0.000328 |
| hybrid_context | dateblock5 | pc | S2 | 0.583578 | 0.583871 | 0.000293 |
| raw_human_context | dateblock5 | cluster6 | S3 | 0.530612 | 0.530980 | 0.000368 |
| family_jepa_context | dateblock5 | cluster6 | Q2 | 0.704733 | 0.705663 | 0.000930 |
| hybrid_context | dateblock5 | cluster6 | S4 | 0.670940 | 0.672085 | 0.001146 |
| family_jepa_context | dateblock5 | cluster6 | S2 | 0.583578 | 0.584900 | 0.001321 |
| hybrid_context | dateblock5 | pc | Q3 | 0.679848 | 0.682163 | 0.002315 |
| family_jepa_context | dateblock5 | cluster6 | Q3 | 0.679848 | 0.683560 | 0.003711 |
| hybrid_context | dateblock5 | pc | S4 | 0.670940 | 0.674698 | 0.003758 |
| raw_human_context | dateblock5 | cluster6 | Q2 | 0.704733 | 0.708641 | 0.003908 |
| hybrid_context | dateblock5 | pc | Q2 | 0.704733 | 0.709554 | 0.004821 |
| hybrid_context | dateblock5 | cluster6 | Q2 | 0.704733 | 0.709567 | 0.004834 |
| family_jepa_context | subject5 | cluster6 | Q1 | 0.713377 | 0.718553 | 0.005176 |
| raw_human_context | subject5 | pc | Q2 | 0.722797 | 0.728409 | 0.005612 |
| hybrid_context | subject5 | pc | S3 | 0.634677 | 0.640387 | 0.005710 |
| raw_human_context | dateblock5 | pc | Q2 | 0.704733 | 0.710888 | 0.006155 |
| hybrid_context | dateblock5 | cluster6 | S3 | 0.530612 | 0.537386 | 0.006774 |
| hybrid_context | dateblock5 | cluster6 | S1 | 0.578496 | 0.585533 | 0.007038 |

## Cluster Diagnostics

| view_id | split | k | train_test_js | subject_nmi | self_transition | Q1_cluster_prior_std | Q2_cluster_prior_std | Q3_cluster_prior_std | S1_cluster_prior_std | S2_cluster_prior_std | S3_cluster_prior_std | S4_cluster_prior_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | 4 | 0.037356 | 0.035200 | 0.515909 | 0.046826 | 0.052095 | 0.087918 | 0.048818 | 0.014570 | 0.033035 | 0.054670 |
| hybrid_context | dateblock5 | 4 | 0.040382 | 0.018296 | 0.595455 | 0.235016 | 0.191813 | 0.262168 | 0.152456 | 0.151776 | 0.158820 | 0.189254 |
| raw_human_context | dateblock5 | 4 | 0.066931 | 0.027814 | 0.561364 | 0.353679 | 0.355419 | 0.305591 | 0.160440 | 0.176712 | 0.170829 | 0.354831 |
| raw_human_context | dateblock5 | 6 | 0.075750 | 0.073980 | 0.425000 | 0.295260 | 0.293122 | 0.275303 | 0.148601 | 0.183979 | 0.161589 | 0.291280 |
| hybrid_context | dateblock5 | 6 | 0.078320 | 0.047072 | 0.413636 | 0.202637 | 0.180326 | 0.236902 | 0.130088 | 0.128372 | 0.131595 | 0.166734 |
| raw_human_context | dateblock5 | 8 | 0.080771 | 0.094052 | 0.363636 | 0.310954 | 0.304019 | 0.324302 | 0.152781 | 0.181883 | 0.169728 | 0.293791 |
| family_jepa_context | dateblock5 | 6 | 0.096122 | 0.070843 | 0.415909 | 0.050517 | 0.045936 | 0.065509 | 0.047810 | 0.014347 | 0.058805 | 0.067476 |
| hybrid_context | dateblock5 | 8 | 0.108344 | 0.092155 | 0.368182 | 0.179144 | 0.153534 | 0.214495 | 0.125423 | 0.116711 | 0.121737 | 0.171729 |
| family_jepa_context | dateblock5 | 8 | 0.159139 | 0.091067 | 0.375000 | 0.099122 | 0.062857 | 0.080553 | 0.076436 | 0.052681 | 0.093232 | 0.092520 |
| family_jepa_context | subject5 | 4 | 0.217617 | 0.229525 | 0.695455 | 0.032683 | 0.029219 | 0.036404 | 0.051835 | 0.029189 | 0.121968 | 0.054305 |
| hybrid_context | subject5 | 4 | 0.236752 | 0.225246 | 0.654545 | 0.065541 | 0.057921 | 0.071005 | 0.048762 | 0.018712 | 0.088631 | 0.061931 |
| hybrid_context | subject5 | 6 | 0.271379 | 0.333010 | 0.588636 | 0.086271 | 0.087567 | 0.098102 | 0.105734 | 0.060279 | 0.114543 | 0.094553 |
| hybrid_context | subject5 | 8 | 0.275123 | 0.367461 | 0.515909 | 0.208004 | 0.169078 | 0.211541 | 0.140852 | 0.133162 | 0.147903 | 0.165060 |
| raw_human_context | subject5 | 6 | 0.282158 | 0.410301 | 0.675000 | 0.292864 | 0.294610 | 0.263690 | 0.172198 | 0.136423 | 0.147112 | 0.173230 |
| raw_human_context | subject5 | 4 | 0.290414 | 0.350776 | 0.820455 | 0.208927 | 0.223631 | 0.189029 | 0.125378 | 0.033978 | 0.105366 | 0.070510 |
| family_jepa_context | subject5 | 8 | 0.300742 | 0.282777 | 0.550000 | 0.055083 | 0.088707 | 0.114691 | 0.126603 | 0.077087 | 0.115029 | 0.095484 |
| family_jepa_context | subject5 | 6 | 0.301534 | 0.283689 | 0.611364 | 0.064368 | 0.094602 | 0.121162 | 0.122095 | 0.061216 | 0.110591 | 0.070103 |
| raw_human_context | subject5 | 8 | 0.331938 | 0.434390 | 0.625000 | 0.305630 | 0.315483 | 0.287837 | 0.190842 | 0.184827 | 0.221919 | 0.261917 |

## E247/E256 Boundary Alignment

| view_id | split | cluster6 | n_test_rows | e247_q3_changed_rate | e256_vs_e247_q3_changed_rate | e247_q3_abs_logit_delta_mean | e256_vs_e247_q3_abs_logit_delta_mean | life_pc1_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | 0 | 22 | 0.136364 | 0.136364 | 0.008979 | 0.007491 | -2.330323 |
| family_jepa_context | dateblock5 | 1 | 68 | 0.088235 | 0.014706 | 0.007110 | 0.001741 | 1.663426 |
| family_jepa_context | dateblock5 | 2 | 71 | 0.154930 | 0.112676 | 0.009820 | 0.006952 | -0.168298 |
| family_jepa_context | dateblock5 | 3 | 31 | 0.161290 | 0.000000 | 0.012345 | 0.000000 | 0.099488 |
| family_jepa_context | dateblock5 | 4 | 23 | 0.173913 | 0.173913 | 0.006206 | 0.006206 | 1.268557 |
| family_jepa_context | dateblock5 | 5 | 35 | 0.142857 | 0.028571 | 0.010901 | 0.000868 | -2.905788 |
| family_jepa_context | subject5 | 0 | 122 | 0.106557 | 0.049180 | 0.007341 | 0.003768 | -0.952461 |
| family_jepa_context | subject5 | 1 | 85 | 0.152941 | 0.070588 | 0.011811 | 0.003730 | 0.218264 |
| family_jepa_context | subject5 | 4 | 19 | 0.210526 | 0.052632 | 0.012785 | 0.001599 | -1.234071 |
| family_jepa_context | subject5 | 5 | 24 | 0.166667 | 0.166667 | 0.005948 | 0.005948 | -0.248863 |
| hybrid_context | dateblock5 | 0 | 59 | 0.067797 | 0.000000 | 0.006255 | 0.000000 | 1.954535 |
| hybrid_context | dateblock5 | 2 | 26 | 0.153846 | 0.115385 | 0.007416 | 0.004602 | -0.889518 |
| hybrid_context | dateblock5 | 3 | 24 | 0.250000 | 0.041667 | 0.016904 | 0.001266 | 0.546513 |
| hybrid_context | dateblock5 | 4 | 36 | 0.222222 | 0.166667 | 0.014392 | 0.007914 | 0.537080 |
| hybrid_context | dateblock5 | 5 | 105 | 0.114286 | 0.066667 | 0.007615 | 0.004904 | -1.287870 |
| hybrid_context | subject5 | 0 | 5 | 0.200000 | 0.000000 | 0.017416 | 0.000000 | -0.078572 |
| hybrid_context | subject5 | 1 | 149 | 0.140940 | 0.080537 | 0.008838 | 0.004796 | 0.010059 |
| hybrid_context | subject5 | 2 | 12 | 0.416667 | 0.166667 | 0.034117 | 0.006510 | -0.230263 |
| hybrid_context | subject5 | 3 | 57 | 0.070175 | 0.052632 | 0.003192 | 0.002757 | 1.277497 |
| hybrid_context | subject5 | 4 | 27 | 0.111111 | 0.000000 | 0.010741 | 0.000000 | 0.776247 |
| raw_human_context | dateblock5 | 0 | 14 | 0.214286 | 0.071429 | 0.020144 | 0.002170 | -0.967720 |
| raw_human_context | dateblock5 | 1 | 45 | 0.155556 | 0.088889 | 0.010851 | 0.004176 | -0.561170 |
| raw_human_context | dateblock5 | 2 | 93 | 0.150538 | 0.053763 | 0.010355 | 0.002834 | 0.887449 |
| raw_human_context | dateblock5 | 3 | 98 | 0.102041 | 0.071429 | 0.005632 | 0.004776 | -0.223874 |
| raw_human_context | subject5 | 1 | 159 | 0.113208 | 0.088050 | 0.006250 | 0.005008 | 0.243666 |
| raw_human_context | subject5 | 3 | 67 | 0.134328 | 0.014925 | 0.009726 | 0.001145 | -0.753231 |
| raw_human_context | subject5 | 5 | 24 | 0.291667 | 0.083333 | 0.026663 | 0.003205 | -0.485478 |

## Decision

No lifestyle-bundle latent is submission-ready. Use the best surviving views as diagnostic state/energy only.

## Interpretation

This audit tests a bigger hidden object than a single story. A positive reconstruction score alone is not enough: the latent must also improve label CV and beat row/subject/dateblock shuffles. Failure means the lifestyle bundle may still describe human behavior, but it is not yet a safe probability editor.

## Files

- `e288_lifestyle_bundle_jepa_summary.csv`
- `e288_lifestyle_bundle_story_recon.csv`
- `e288_lifestyle_bundle_label_stress.csv`
- `e288_lifestyle_bundle_target_detail.csv`
- `e288_lifestyle_bundle_cluster_diagnostics.csv`
- `e288_lifestyle_bundle_boundary_alignment.csv`
- `e288_lifestyle_bundle_nulls.csv`
