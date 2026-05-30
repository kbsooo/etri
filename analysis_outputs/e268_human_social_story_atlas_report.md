# E268 Human/Social Story Atlas

## Question

After `submission_e267_humansocial_tail_balanced_2936100f.csv` lost publicly, does the human/social worldview die, or did it fail because it was translated through the wrong E224/E154 rollback action?

This experiment treats each story as a falsifiable hidden-state hypothesis and tests it four ways: train label lift, date-block/subject CV, train/test shift, and alignment with E247/E256/E267 public-anchor movements.

## Inventory

- explicit human/social stories: `35`
- train rows: `450`
- test rows: `250`

## Best Story Verdicts

| story_id | family | human_story | best_label_target | best_label_abs_effect | best_dateblock_target | best_dateblock_delta | subject_split_best_delta | e247_only_d | e256_only_d | e247_vs_e256_d | e267_moved_d | train_test_gap | public_align_score | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phone_in_bed | sleep_fragment | Screen use while phone is charging at presleep. | Q2 | 0.070796 | Q3 | -0.001091 | -0.011789 | 0.476689 | -0.319016 | 1.164309 | -0.259547 | 0.031163 | 1.503433 | promising_for_direct_e247_gate |
| app_entropy_scattered_day | routine_break | Attention spread across many apps during the day. | Q3 | 0.168142 | Q3 | -0.006340 | -0.031234 | 0.622129 | 1.325362 | -0.741665 | -0.041993 | 0.038060 | 1.333283 | promising_for_direct_e247_gate |
| weekend_ritual_rest | calendar_social | Weekend routine/religion/charge and low mobility. | Q3 | 0.221239 | Q3 | -0.005106 | -0.002539 | -0.405218 | -1.067535 | 1.033308 | -0.376824 | 0.043567 | 1.239223 | promising_for_direct_e247_gate |
| single_app_monotony | routine_anchor | One dominant app or ritual dominates the day. | Q3 | 0.203540 | Q3 | -0.008958 | -0.059585 | -0.745833 | -1.177082 | 0.527132 | 0.129779 | 0.031502 | 1.200200 | promising_for_direct_e247_gate |
| social_isolation_media | social_isolation | Low direct social signal but high passive media/home utility. | S1 | 0.053097 | S1 | -0.005494 | -0.019087 | -0.074107 | -1.281637 | 1.229457 | -0.330623 | 0.047552 | 1.126364 | promising_for_direct_e247_gate |
| ritual_anchor | routine_anchor | Religious/routine app use and charging before sleep. | Q3 | 0.177376 | Q3 | -0.009102 | 0.005602 | 0.089870 | -0.749923 | 0.908264 | -0.167757 | 0.014599 | 0.910606 | promising_for_direct_e247_gate |
| morning_after_badnight | nextday_echo | High morning heart/mobility after a possibly fragmented night. | Q2 | 0.159292 | S4 | -0.003585 | -0.018539 | -0.162892 | 0.413305 | -0.736767 | -0.123524 | 0.121185 | 0.807600 | promising_for_direct_e247_gate |
| weekend_social_jetlag | calendar_social | Weekend late social/media/deepnight phone. | S4 | 0.221239 | Q2 | -0.000169 | -0.008859 | -0.078638 | -0.882883 | 0.796772 | -0.116275 | 0.094889 | 0.793550 | promising_for_direct_e247_gate |
| low_hr_recovery | physiology_recovery | Low presleep heart rate and quiet charging. | Q3 | 0.194690 | Q3 | -0.006106 | -0.001893 | 0.228115 | -0.438707 | 0.736979 | -0.332948 | 0.058775 | 0.783927 | promising_for_direct_e247_gate |
| deepnight_phone_awake | sleep_fragment | Phone activity after midnight when the day should be winding down. | Q3 | 0.104770 | Q1 | -0.003314 | -0.005166 | 0.224093 | -0.294758 | 0.546401 | 0.130645 | 0.117375 | 0.675828 | promising_for_direct_e247_gate |
| weekday_routine_pressure | calendar_social | Weekday plus commute/work/study signal. | S3 | 0.079646 | S2 | -0.008318 | -0.039209 | -0.208662 | 0.248546 | -0.469951 | 0.137007 | 0.022966 | 0.604368 | promising_for_direct_e247_gate |
| bright_light_late | sleep_fragment | Phone/wearable light exposure near sleep. | S4 | 0.203540 | S4 | -0.013849 | -0.006700 | 0.150887 | 0.741559 | -0.649663 | 0.433453 | 0.020057 | 0.578810 | promising_for_direct_e247_gate |
| presleep_msg_drag | social_overstim | Presleep messaging plus repeated phone checks. | S1 | 0.097345 | S2 | -0.001735 | -0.005117 | 0.341706 | 0.531863 | -0.193590 | 0.006265 | 0.041983 | 0.521667 | promising_for_direct_e247_gate |
| music_ambient_late | media_binge | Music ambience late or deepnight. | S2 | 0.148100 | Q1 | -0.006495 | -0.004387 | -0.192762 | 0.082252 | -0.323233 | -0.079546 | 0.099081 | 0.451452 | promising_for_direct_e247_gate |
| physical_fatigue | physical_fatigue | High steps/distance/calories and heart activity. | S4 | 0.079646 | S4 | -0.001670 | -0.013580 | 0.029508 | 0.497870 | -0.488510 | 0.203763 | 0.002919 | 0.415407 | promising_for_direct_e247_gate |
| outdoor_nature_day | environment | Outdoor/nature ambience and movement. | Q1 | 0.097345 | S3 | -0.001800 | -0.017389 | -0.378409 | -0.334600 | -0.116880 | 0.162126 | 0.026121 | 0.407695 | promising_for_direct_e247_gate |
| heart_stress_late | physiology_stress | High late/presleep heart rate and variance. | Q3 | 0.149027 | Q1 | -0.016048 | -0.017291 | -0.231974 | 0.116758 | -0.367220 | 0.352461 | 0.134958 | 0.389224 | promising_for_direct_e247_gate |
| finance_shopping_stress | cognitive_load | Money or shopping attention late in the day. | S4 | 0.073437 | S4 | 0.002505 | 0.009773 | 0.689714 | 0.318415 | 0.286772 | 0.167215 | 0.006930 | 0.891146 | public_anchor_diagnostic_only |
| screen_fragmentation | sleep_fragment | Many short screen sessions late. | S4 | 0.088496 | S1 | 0.000528 | -0.005655 | 0.417332 | -0.099055 | 0.472736 | 0.007206 | 0.004906 | 0.885239 | public_anchor_diagnostic_only |
| game_dopamine_late | media_binge | Late games with screen exposure. | S3 | 0.150442 | S1 | -0.004817 | -0.006355 | 0.075010 | -0.209862 | 0.292084 | -0.086896 | 0.066691 | 0.306974 | real_but_action_unproven |
| late_search_spiral | cognitive_load | Late searching, browsing, work, finance, and shopping loops. | S1 | 0.143611 | S1 | -0.003163 | 0.013649 | 0.129338 | 0.315369 | -0.224767 | 0.146691 | 0.005253 | 0.279446 | real_but_action_unproven |
| sedentary_screen_day | sedentary_screen | Low movement but high screen/media/social day. | Q2 | 0.168142 | Q3 | -0.002176 | -0.011899 | 0.297113 | 0.188053 | 0.116394 | -0.246357 | 0.047580 | 0.278434 | real_but_action_unproven |
| overtraining_arousal | physical_fatigue | Physical load plus high evening/presleep heart rate. | S4 | 0.123894 | S3 | -0.005063 | -0.014019 | 0.003066 | 0.407341 | -0.428571 | 0.294225 | 0.029598 | 0.277125 | real_but_action_unproven |
| sensor_sparse_day | measurement_state | Sparse sensor counts that may encode phone/watch availability. | S4 | 0.150442 | S4 | -0.004336 | -0.004891 | -0.010052 | -0.294097 | 0.287632 | -0.055329 | 0.093858 | 0.246555 | real_but_action_unproven |
| afterwork_recovery | workday_commute | Commute signal followed by quiet/charging at night. | Q2 | 0.141593 | S2 | 0.000645 | -0.005854 | 0.053151 | -0.222426 | 0.256956 | -0.085243 | 0.138014 | 0.232982 | real_but_action_unproven |

## Strongest Label Lifts

| story_id | variant | family | target | high_minus_low | abs_effect | corr |
| --- | --- | --- | --- | --- | --- | --- |
| music_ambient_late | score_abs_subj_z | media_binge | S3 | 0.267427 | 0.267427 | 0.080546 |
| single_app_monotony | score | routine_anchor | S2 | 0.265487 | 0.265487 | 0.153464 |
| late_msg_call | score | social_overstim | S3 | 0.256637 | 0.256637 | 0.187376 |
| media_binge_late | score_abs_subj_z | media_binge | Q3 | -0.250761 | 0.250761 | -0.176017 |
| heart_stress_late | score_abs_subj_z | physiology_stress | Q1 | 0.247788 | 0.247788 | 0.172012 |
| heart_stress_late | score_abs_subj_z | physiology_stress | Q2 | 0.238938 | 0.238938 | 0.110952 |
| media_binge_late | score_abs_subj_z | media_binge | S1 | -0.229466 | 0.229466 | -0.090749 |
| media_binge_late | score_abs_subj_z | media_binge | S2 | -0.228429 | 0.228429 | -0.135218 |
| deepnight_phone_awake | score | sleep_fragment | S1 | -0.221239 | 0.221239 | -0.135289 |
| weekend_social_jetlag | score_subj_z | calendar_social | S4 | 0.221239 | 0.221239 | 0.129808 |
| weekend_ritual_rest | score_subj_z | calendar_social | Q3 | 0.221239 | 0.221239 | 0.176686 |
| weekend_ritual_rest | score | calendar_social | S1 | -0.212389 | 0.212389 | -0.118421 |
| commute_workday | score | workday_commute | S1 | 0.212389 | 0.212389 | 0.168835 |
| weekday_routine_pressure | score | calendar_social | S2 | 0.210940 | 0.210940 | 0.152497 |
| bright_light_late | score_subj_z | sleep_fragment | S4 | 0.203540 | 0.203540 | 0.153152 |
| app_entropy_scattered_day | score | routine_break | S1 | -0.203540 | 0.203540 | -0.150055 |
| app_entropy_scattered_day | score | routine_break | S2 | -0.203540 | 0.203540 | -0.133850 |
| bright_light_late | score | sleep_fragment | S3 | 0.203540 | 0.203540 | 0.154978 |
| night_out_mobility | score | nightlife_mobility | S4 | 0.203540 | 0.203540 | 0.135740 |
| quiet_dark_bedtime | score | routine_anchor | S3 | -0.203540 | 0.203540 | -0.133221 |
| single_app_monotony | score | routine_anchor | S1 | 0.203540 | 0.203540 | 0.154611 |
| single_app_monotony | score_subj_z | routine_anchor | Q3 | -0.203540 | 0.203540 | -0.129502 |
| heart_stress_late | score | physiology_stress | Q1 | 0.202286 | 0.202286 | 0.116636 |
| weekday_routine_pressure | score | calendar_social | S1 | 0.201633 | 0.201633 | 0.124567 |
| night_out_mobility | score | nightlife_mobility | S1 | 0.194690 | 0.194690 | 0.157983 |
| low_hr_recovery | score_subj_z | physiology_recovery | Q3 | 0.194690 | 0.194690 | 0.149795 |
| media_binge_late | score_subj_z | media_binge | Q2 | 0.194690 | 0.194690 | 0.131115 |
| heart_stress_late | score_abs_subj_z | physiology_stress | S3 | 0.194690 | 0.194690 | 0.097426 |
| home_stability | score | routine_anchor | S1 | -0.194690 | 0.194690 | -0.138922 |
| night_out_mobility | score | nightlife_mobility | S3 | 0.194690 | 0.194690 | 0.207045 |

## Best Blocked CV Deltas

| story_id | family | split | target | delta_logloss | loss_base | loss_story |
| --- | --- | --- | --- | --- | --- | --- |
| single_app_monotony | routine_anchor | subject5 | S2 | -0.059585356 | 0.672251403 | 0.612666047 |
| vehicle_noise_day | environment | subject5 | S1 | -0.045629803 | 0.648262335 | 0.602632532 |
| commute_workday | workday_commute | subject5 | S1 | -0.041824867 | 0.648262335 | 0.606437468 |
| weekday_routine_pressure | calendar_social | subject5 | S2 | -0.039209081 | 0.672251403 | 0.633042322 |
| weekday_routine_pressure | calendar_social | subject5 | S1 | -0.037407341 | 0.648262335 | 0.610854994 |
| app_entropy_scattered_day | routine_break | subject5 | S2 | -0.031233665 | 0.672251403 | 0.641017738 |
| single_app_monotony | routine_anchor | subject5 | S1 | -0.029882410 | 0.648262335 | 0.618379925 |
| public_social_evening | social_outing | subject5 | S1 | -0.027020580 | 0.648262335 | 0.621241755 |
| home_stability | routine_anchor | subject5 | S1 | -0.023757211 | 0.648262335 | 0.624505124 |
| quiet_dark_bedtime | routine_anchor | subject5 | Q1 | -0.022730751 | 0.708226114 | 0.685495363 |
| social_isolation_media | social_isolation | subject5 | S1 | -0.019087350 | 0.648262335 | 0.629174985 |
| morning_after_badnight | nextday_echo | subject5 | S3 | -0.018538550 | 0.662506726 | 0.643968176 |
| weekday_routine_pressure | calendar_social | subject5 | S3 | -0.018385676 | 0.662506726 | 0.644121050 |
| outdoor_nature_day | environment | subject5 | S1 | -0.017388505 | 0.648262335 | 0.630873830 |
| heart_stress_late | physiology_stress | subject5 | Q1 | -0.017290615 | 0.708226114 | 0.690935500 |
| heart_stress_late | physiology_stress | dateblock5 | Q1 | -0.016047951 | 0.670711878 | 0.654663927 |
| heart_stress_late | physiology_stress | subject5 | Q3 | -0.014293923 | 0.687593978 | 0.673300055 |
| overtraining_arousal | physical_fatigue | subject5 | Q1 | -0.014019124 | 0.708226114 | 0.694206990 |
| social_isolation_media | social_isolation | subject5 | Q1 | -0.013986341 | 0.708226114 | 0.694239773 |
| bright_light_late | sleep_fragment | dateblock5 | S4 | -0.013849164 | 0.660706471 | 0.646857306 |
| physical_fatigue | physical_fatigue | subject5 | Q1 | -0.013579653 | 0.708226114 | 0.694646461 |
| single_app_monotony | routine_anchor | subject5 | Q2 | -0.013340317 | 0.699631895 | 0.686291579 |
| media_binge_late | media_binge | subject5 | Q3 | -0.012052814 | 0.687593978 | 0.675541164 |
| sedentary_screen_day | sedentary_screen | subject5 | S1 | -0.011899150 | 0.648262335 | 0.636363184 |
| quiet_dark_bedtime | routine_anchor | dateblock5 | Q1 | -0.011892512 | 0.670711878 | 0.658819366 |
| phone_in_bed | sleep_fragment | subject5 | Q2 | -0.011788760 | 0.699631895 | 0.687843136 |
| commute_workday | workday_commute | dateblock5 | S4 | -0.011513081 | 0.660706471 | 0.649193390 |
| vehicle_noise_day | environment | dateblock5 | S1 | -0.011396697 | 0.584091795 | 0.572695098 |
| app_entropy_scattered_day | routine_break | subject5 | Q2 | -0.010742661 | 0.699631895 | 0.688889235 |
| charge_bed_anchor | routine_anchor | dateblock5 | Q3 | -0.010571664 | 0.678867291 | 0.668295627 |

## E247-Only Q3 Movement Alignment

Positive `cohen_d` means the story is higher on the E247-only Q3 rows than on neutral rows. This is a public-anchor diagnostic, not label truth.

| story_id | family | n_group | n_neutral | mean_group | mean_neutral | cohen_d_group_vs_neutral |
| --- | --- | --- | --- | --- | --- | --- |
| finance_shopping_stress | cognitive_load | 13 | 191 | 0.651176 | -0.051956 | 0.689714 |
| app_entropy_scattered_day | routine_break | 13 | 191 | 0.570663 | 0.027648 | 0.622129 |
| phone_in_bed | sleep_fragment | 13 | 191 | 0.432452 | 0.037186 | 0.476689 |
| screen_fragmentation | sleep_fragment | 13 | 191 | 0.345147 | 0.000655 | 0.417332 |
| presleep_msg_drag | social_overstim | 13 | 191 | 0.309830 | 0.036366 | 0.341706 |
| sedentary_screen_day | sedentary_screen | 13 | 191 | 0.358063 | 0.094020 | 0.297113 |
| night_out_mobility | nightlife_mobility | 13 | 191 | 0.190023 | -0.101650 | 0.267606 |
| low_hr_recovery | physiology_recovery | 13 | 191 | 0.275741 | 0.029930 | 0.228115 |
| deepnight_phone_awake | sleep_fragment | 13 | 191 | 0.324828 | 0.092419 | 0.224093 |
| bright_light_late | sleep_fragment | 13 | 191 | 0.014072 | -0.128320 | 0.150887 |
| late_search_spiral | cognitive_load | 13 | 191 | 0.089325 | -0.038083 | 0.129338 |
| media_binge_late | media_binge | 13 | 191 | 0.158090 | 0.023809 | 0.124958 |
| home_stability | routine_anchor | 13 | 191 | 0.309285 | 0.202864 | 0.095938 |
| ritual_anchor | routine_anchor | 13 | 191 | 0.134047 | 0.042487 | 0.089870 |
| public_social_evening | social_outing | 13 | 191 | -0.118013 | -0.186392 | 0.079098 |
| game_dopamine_late | media_binge | 13 | 191 | 0.021027 | -0.046862 | 0.075010 |
| late_msg_call | social_overstim | 13 | 191 | 0.002883 | -0.054824 | 0.059194 |
| afterwork_recovery | workday_commute | 13 | 191 | -0.057427 | -0.117922 | 0.053151 |
| physical_fatigue | physical_fatigue | 13 | 191 | -0.024141 | -0.053892 | 0.029508 |
| high_sensor_wear_day | measurement_state | 13 | 191 | 0.107797 | 0.091034 | 0.019275 |
| overtraining_arousal | physical_fatigue | 13 | 191 | -0.107510 | -0.110922 | 0.003066 |
| sensor_sparse_day | measurement_state | 13 | 191 | -0.082414 | -0.072241 | -0.010052 |
| commute_workday | workday_commute | 13 | 191 | -0.203302 | -0.146171 | -0.051903 |
| social_isolation_media | social_isolation | 13 | 191 | -0.028293 | 0.042402 | -0.074107 |
| weekend_social_jetlag | calendar_social | 13 | 191 | 0.057101 | 0.131400 | -0.078638 |

## E267 Failed-Movement Exposure

If a story is high here, the failed E267 action already leaned on it. That weakens direct reuse unless the next action is changed.

| story_id | family | n_group | n_neutral | mean_group | mean_neutral | cohen_d_group_vs_neutral |
| --- | --- | --- | --- | --- | --- | --- |
| bright_light_late | sleep_fragment | 54 | 191 | 0.299591 | -0.128320 | 0.433453 |
| public_social_evening | social_outing | 54 | 191 | 0.200009 | -0.186392 | 0.406127 |
| night_out_mobility | nightlife_mobility | 54 | 191 | 0.260172 | -0.101650 | 0.365297 |
| heart_stress_late | physiology_stress | 54 | 191 | 0.500176 | 0.028521 | 0.352461 |
| overtraining_arousal | physical_fatigue | 54 | 191 | 0.206784 | -0.110922 | 0.294225 |
| high_sensor_wear_day | measurement_state | 54 | 191 | 0.316306 | 0.091034 | 0.269419 |
| commute_workday | workday_commute | 54 | 191 | 0.114410 | -0.146171 | 0.243043 |
| late_msg_call | social_overstim | 54 | 191 | 0.154999 | -0.054824 | 0.207063 |
| physical_fatigue | physical_fatigue | 54 | 191 | 0.144707 | -0.053892 | 0.203763 |
| vehicle_noise_day | environment | 54 | 191 | 0.084819 | -0.105713 | 0.182505 |
| finance_shopping_stress | cognitive_load | 54 | 191 | 0.119107 | -0.051956 | 0.167215 |
| outdoor_nature_day | environment | 54 | 191 | 0.096879 | -0.051490 | 0.162126 |
| late_search_spiral | cognitive_load | 54 | 191 | 0.110275 | -0.038083 | 0.146691 |
| weekday_routine_pressure | calendar_social | 54 | 191 | 0.078377 | -0.058973 | 0.137007 |
| deepnight_phone_awake | sleep_fragment | 54 | 191 | 0.229203 | 0.092419 | 0.130645 |
| single_app_monotony | routine_anchor | 54 | 191 | 0.092077 | -0.042145 | 0.129779 |
| screen_fragmentation | sleep_fragment | 54 | 191 | 0.007821 | 0.000655 | 0.007206 |
| presleep_msg_drag | social_overstim | 54 | 191 | 0.042243 | 0.036366 | 0.006265 |
| app_entropy_scattered_day | routine_break | 54 | 191 | -0.013627 | 0.027648 | -0.041993 |
| sensor_sparse_day | measurement_state | 54 | 191 | -0.131752 | -0.072241 | -0.055329 |
| music_ambient_late | media_binge | 54 | 191 | 0.001454 | 0.133646 | -0.079546 |
| afterwork_recovery | workday_commute | 54 | 191 | -0.205061 | -0.117922 | -0.085243 |
| game_dopamine_late | media_binge | 54 | 191 | -0.118476 | -0.046862 | -0.086896 |
| weekend_social_jetlag | calendar_social | 54 | 191 | 0.023951 | 0.131400 | -0.116275 |
| morning_after_badnight | nextday_echo | 54 | 191 | -0.241428 | -0.099756 | -0.123524 |

## Story Latent Diagnostic

| latent | target | n_components | pc1_var | pc8_cum_var | anisotropy_pc1_over_mean | loss_base | loss_latent | delta_logloss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| story_subj_z_pca | S4 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.660706471 | 0.664393658 | 0.003687188 |
| story_subj_z_pca | Q3 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.678867291 | 0.685348181 | 0.006480890 |
| story_subj_z_pca | S2 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.588181419 | 0.601014945 | 0.012833525 |
| story_subj_z_pca | Q1 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.670711878 | 0.686175195 | 0.015463317 |
| story_subj_z_pca | S3 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.531327261 | 0.550585687 | 0.019258426 |
| story_subj_z_pca | S1 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.584091795 | 0.604613488 | 0.020521692 |
| story_subj_z_pca | Q2 | 8 | 0.181637629 | 0.690802296 | 2.103497688 | 0.701511268 | 0.723647936 | 0.022136669 |

## Read

- Promising direct E247 gates: `17`.
- Real but action-unproven stories: `12`.
- Public-anchor diagnostics only: `2`.

If no story reaches the direct-gate bucket, the lesson is not that human/social context is useless. It means the current public-positive mechanism needs a new action target: it should predict which E247 Q3 rollback cells to keep or undo directly, not inherit the E224/E154 social rollback body used by E267.
