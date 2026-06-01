# H003 HS-JEPA Prototype

## Question

Can Human-State JEPA produce a hidden lifestyle representation that is context-predictable, geometrically healthy, target-block relevant, and safe enough to translate on top of E247?

## Method

- JEPA target: explicit human episode states, not raw features and not final probabilities.
- Context views: family JEPA context, raw human context, and hybrid context.
- Masking: semantic view mask by context family and grouped OOF split.
- Latent: PCA of context-predicted episode targets plus residual/surprise diagnostics.
- Safety: LeJEPA-style geometry, adjacent-row positive-pair diagnostics, label/null stress, and public-sensor alignment.

## Human-State Targets

| episode | human_story | source | feature_col | weight |
| --- | --- | --- | --- | --- |
| commute_pressure | weekday commute, vehicle exposure, routine pressure, less home stability | human_social | commute_workday_subj_z | 1.000000 |
| commute_pressure | weekday commute, vehicle exposure, routine pressure, less home stability | human_social | vehicle_noise_day_subj_z | 0.800000 |
| commute_pressure | weekday commute, vehicle exposure, routine pressure, less home stability | human_social | weekday_routine_pressure_subj_z | 0.700000 |
| commute_pressure | weekday commute, vehicle exposure, routine pressure, less home stability | human_social | afterwork_recovery_subj_z | -0.350000 |
| commute_pressure | weekday commute, vehicle exposure, routine pressure, less home stability | human_social | home_stability_subj_z | -0.550000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | bright_light_late_subj_z | 1.000000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | phone_in_bed_subj_z | 0.900000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | deepnight_phone_awake_subj_z | 0.900000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | presleep_msg_drag_subj_z | 0.750000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | late_msg_call_subj_z | 0.700000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | late_search_spiral_subj_z | 0.750000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | media_binge_late_subj_z | 0.550000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | game_dopamine_late_subj_z | 0.550000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | screen_fragmentation_subj_z | 0.750000 |
| bedtime_arousal | bright screen, messages, search spiral, media/game and phone-in-bed before sleep | human_social | quiet_dark_bedtime_subj_z | -0.650000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | app_entropy_scattered_day_subj_z | 1.000000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | screen_fragmentation_subj_z | 0.850000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | single_app_monotony_subj_z | 0.550000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | weekend_social_jetlag_subj_z | 0.650000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | sensor_sparse_day_subj_z | 0.450000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | ritual_anchor_subj_z | -0.750000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | charge_bed_anchor_subj_z | -0.550000 |
| routine_fragmentation | scattered app attention, fragmented screen use, broken routine, sensor sparse/noisy day | human_social | quiet_dark_bedtime_subj_z | -0.700000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | ritual_anchor_subj_z | 1.000000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | charge_bed_anchor_subj_z | 0.850000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | quiet_dark_bedtime_subj_z | 1.000000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | weekend_ritual_rest_subj_z | 0.650000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | home_stability_subj_z | 0.650000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | low_hr_recovery_subj_z | 0.550000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | app_entropy_scattered_day_subj_z | -0.750000 |
| routine_anchor_recovery | stable home/charging/ritual routine, quiet bedtime, lower arousal recovery | human_social | deepnight_phone_awake_subj_z | -0.650000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | human_social | finance_shopping_stress_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay10_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay15_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay20_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay25_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | payeom_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | paymonth_start_pre3_cash_stress_subj_z | 0.900000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay10_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay15_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay20_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay25_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | payeom_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | paymonth_start_pre7_budget_squeeze_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay10_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay15_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay20_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay25_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | payeom_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | paymonth_start_near3_money_rumination_subj_z | 0.700000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay10_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay15_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay20_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay25_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | payeom_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | paymonth_start_post3_late_shopping_subj_z | 0.500000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | eom_bill_anxiety_subj_z | 0.800000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay10_post3_relief_home_subj_z | -0.350000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay15_post3_relief_home_subj_z | -0.350000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay20_post3_relief_home_subj_z | -0.350000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | pay25_post3_relief_home_subj_z | -0.350000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | payeom_post3_relief_home_subj_z | -0.350000 |
| cashflow_stress | money rumination, budget squeeze, bill anxiety, late shopping/finance arousal | cashflow | paymonth_start_post3_relief_home_subj_z | -0.350000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay10_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay10_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay15_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay15_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay20_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay20_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay25_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay25_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | payeom_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | payeom_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | paymonth_start_post3_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | paymonth_start_post7_spend_outing_subj_z | 0.900000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay10_post3_relief_home_subj_z | 0.700000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay15_post3_relief_home_subj_z | 0.700000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay20_post3_relief_home_subj_z | 0.700000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | pay25_post3_relief_home_subj_z | 0.700000 |
| cashflow_relief_spend | payday/month-start relief, spending/outings, reset energy | cashflow | payeom_post3_relief_home_subj_z | 0.700000 |

## Context -> Human-State Reconstruction

| view_id | split | episode | r2 | corr | train_test_pred_z_gap |
| --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | measurement_wear_confidence | 0.694487 | 0.835851 | 0.101954 |
| hybrid_context | dateblock5 | social_overload | 0.625023 | 0.802986 | -0.042669 |
| family_jepa_context | dateblock5 | badnight_aftereffect | 0.624071 | 0.798400 | 0.040909 |
| family_jepa_context | dateblock5 | commute_pressure | 0.621365 | 0.794130 | -0.163654 |
| family_jepa_context | dateblock5 | social_overload | 0.615586 | 0.787358 | -0.091050 |
| hybrid_context | dateblock5 | commute_pressure | 0.610934 | 0.793872 | -0.092889 |
| hybrid_context | dateblock5 | bedtime_arousal | 0.609768 | 0.800087 | 0.134275 |
| hybrid_context | dateblock5 | physiology_strain | 0.565596 | 0.776054 | 0.087898 |
| family_jepa_context | subject5 | badnight_aftereffect | 0.526448 | 0.756658 | 0.039702 |
| raw_human_context | dateblock5 | bedtime_arousal | 0.466444 | 0.724909 | 0.017804 |
| family_jepa_context | dateblock5 | bedtime_arousal | 0.457143 | 0.691552 | 0.047622 |
| raw_human_context | dateblock5 | badnight_aftereffect | 0.440628 | 0.696436 | 0.117641 |
| hybrid_context | dateblock5 | badnight_aftereffect | 0.440198 | 0.728564 | 0.065023 |
| family_jepa_context | dateblock5 | physiology_strain | 0.431554 | 0.673484 | 0.110866 |
| raw_human_context | dateblock5 | physiology_strain | 0.425618 | 0.724884 | 0.115152 |
| family_jepa_context | subject5 | measurement_wear_confidence | 0.415968 | 0.727739 | 0.068751 |
| family_jepa_context | dateblock5 | routine_anchor_recovery | 0.352209 | 0.620443 | 0.024595 |
| hybrid_context | dateblock5 | routine_anchor_recovery | 0.343652 | 0.639932 | -0.009758 |
| raw_human_context | dateblock5 | measurement_wear_confidence | 0.308639 | 0.683567 | 0.161665 |
| family_jepa_context | dateblock5 | cashflow_stress | 0.308457 | 0.576766 | -0.075022 |
| family_jepa_context | subject5 | commute_pressure | 0.299190 | 0.675474 | -0.103580 |
| family_jepa_context | dateblock5 | cashflow_relief_spend | 0.273261 | 0.553115 | 0.097173 |
| family_jepa_context | dateblock5 | routine_fragmentation | 0.215174 | 0.517042 | -0.049622 |
| hybrid_context | dateblock5 | cashflow_stress | 0.211384 | 0.575662 | -0.053338 |
| family_jepa_context | subject5 | physiology_strain | 0.201616 | 0.599776 | 0.173981 |
| hybrid_context | dateblock5 | measurement_wear_confidence | 0.186682 | 0.659647 | 0.099651 |
| family_jepa_context | subject5 | cashflow_relief_spend | 0.184142 | 0.514748 | 0.028277 |
| family_jepa_context | dateblock5 | home_recovery | 0.179545 | 0.485871 | 0.095275 |
| family_jepa_context | subject5 | social_overload | 0.165645 | 0.640472 | 0.120676 |
| hybrid_context | dateblock5 | routine_fragmentation | 0.165063 | 0.551132 | 0.025282 |
| hybrid_context | subject5 | badnight_aftereffect | 0.150716 | 0.646721 | 0.002302 |
| hybrid_context | dateblock5 | cashflow_relief_spend | 0.139521 | 0.541603 | 0.096289 |
| raw_human_context | dateblock5 | commute_pressure | 0.114847 | 0.491779 | -0.020506 |
| hybrid_context | subject5 | physiology_strain | 0.054655 | 0.641174 | 0.029322 |
| hybrid_context | subject5 | cashflow_stress | 0.013725 | 0.533255 | -0.094491 |

## Latent Geometry

| latent | dims | explained_var_sum | participation_ratio | anisotropy | train_energy_mean | test_energy_mean | train_surprise_mean | test_surprise_mean | slice_abs_skew_mean | slice_abs_excess_kurt_mean | slice_gaussian_penalty |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hsjepa | 8 | 0.758982 | 5.344604 | 2.681719 | 2.444568 | 1.814922 | 0.753363 | 0.732105 | 0.929496 | 8.604939 | 5.231965 |

## Positive-Pair Diagnostics

| split | positive_pair_count | autocorr_mean | autocorr_min | autocorr_max | increment_abs_skew_mean | increment_abs_excess_kurt_mean | increment_l2_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 440 | 0.376875 | -0.003166 | 0.584073 | 0.206259 | 11.150752 | 6.752133 |
| test | 240 | 0.188386 | 0.057402 | 0.341301 | 0.135357 | 0.763008 | 6.047297 |
| all | 690 | 0.335017 | 0.042584 | 0.542620 | 0.195910 | 11.554672 | 6.607893 |

## Target Translation Stress

| split | target | delta_logloss | null_median | dominance | row_dominance | subject_dominance | dateblock_dominance | target_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject5 | Q2 | 0.002116659 | 0.033792842 | 0.833333333 | 1.000000000 | 0.833333333 | 0.666666667 | False |
| dateblock5 | Q3 | 0.006867661 | 0.023848372 | 0.833333333 | 1.000000000 | 1.000000000 | 0.500000000 | False |
| dateblock5 | S1 | 0.008417534 | 0.030853556 | 0.888888889 | 0.833333333 | 0.833333333 | 1.000000000 | False |
| subject5 | S1 | 0.020694206 | 0.051521179 | 0.833333333 | 0.666666667 | 1.000000000 | 0.833333333 | False |
| dateblock5 | Q1 | 0.022263634 | 0.022014700 | 0.444444444 | 0.500000000 | 0.666666667 | 0.166666667 | False |
| dateblock5 | Q2 | 0.022311322 | 0.026841735 | 0.722222222 | 0.833333333 | 0.666666667 | 0.666666667 | False |
| dateblock5 | S4 | 0.028484189 | 0.030886847 | 0.555555556 | 0.500000000 | 0.666666667 | 0.500000000 | False |
| subject5 | Q3 | 0.033467067 | 0.040904324 | 0.555555556 | 0.333333333 | 1.000000000 | 0.333333333 | False |
| dateblock5 | S3 | 0.036999388 | 0.019708074 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | False |
| dateblock5 | S2 | 0.042101896 | 0.039941282 | 0.500000000 | 0.333333333 | 0.500000000 | 0.666666667 | False |
| subject5 | Q1 | 0.052718692 | 0.041964931 | 0.388888889 | 0.000000000 | 0.666666667 | 0.500000000 | False |
| subject5 | S2 | 0.053773282 | 0.049322768 | 0.444444444 | 0.000000000 | 0.500000000 | 0.833333333 | False |
| subject5 | S4 | 0.068900711 | 0.036928823 | 0.222222222 | 0.000000000 | 0.333333333 | 0.333333333 | False |
| subject5 | S3 | 0.069758709 | 0.040781722 | 0.111111111 | 0.000000000 | 0.333333333 | 0.000000000 | False |

## Episode Target Routes

This is the sparse HS-JEPA translation test: one human episode should only affect the targets it can explain under matched nulls.

| split | episode | target | delta_logloss | null_median | dominance | row_dominance | subject_dominance | dateblock_dominance | route_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject5 | home_recovery | S3 | -0.013044173 | -0.001697998 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | bedtime_arousal | S3 | -0.010444948 | 0.000031443 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | social_overload | S3 | -0.009121835 | 0.000692726 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | True |
| dateblock5 | routine_anchor_recovery | S2 | -0.005921853 | 0.002992862 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | True |
| dateblock5 | home_recovery | S4 | -0.004999434 | 0.003392934 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| dateblock5 | cashflow_stress | S3 | -0.004837016 | 0.000612162 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| dateblock5 | home_recovery | S3 | -0.004706756 | 0.000837023 | 0.888888889 | 1.000000000 | 0.666666667 | 1.000000000 | True |
| subject5 | badnight_aftereffect | Q3 | -0.004585621 | 0.000765179 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| dateblock5 | routine_fragmentation | S3 | -0.004425964 | 0.001065120 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | routine_anchor_recovery | Q2 | -0.003137053 | 0.000107895 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | True |
| dateblock5 | routine_anchor_recovery | S3 | -0.002876823 | 0.001707748 | 0.888888889 | 0.666666667 | 1.000000000 | 1.000000000 | True |
| subject5 | physiology_strain | Q1 | -0.002834207 | 0.001207382 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | True |
| subject5 | badnight_aftereffect | S2 | -0.002788849 | 0.000779367 | 0.888888889 | 1.000000000 | 0.666666667 | 1.000000000 | True |
| subject5 | routine_anchor_recovery | S3 | -0.002697847 | 0.001118469 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | routine_fragmentation | S1 | -0.002656371 | 0.001202709 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| dateblock5 | commute_pressure | S4 | -0.002650042 | -0.000708601 | 0.888888889 | 0.666666667 | 1.000000000 | 1.000000000 | True |
| dateblock5 | home_recovery | Q2 | -0.002583347 | 0.000447565 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | True |
| subject5 | bedtime_arousal | S1 | -0.002537004 | 0.001644368 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | routine_anchor_recovery | S1 | -0.002335291 | 0.001315995 | 0.888888889 | 1.000000000 | 0.666666667 | 1.000000000 | True |
| dateblock5 | physiology_strain | Q1 | -0.002017433 | 0.001095553 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | True |
| subject5 | cashflow_stress | S3 | -0.003868382 | -0.001689735 | 0.666666667 | 1.000000000 | 1.000000000 | 0.000000000 | False |
| dateblock5 | commute_pressure | Q2 | -0.003861539 | 0.000154360 | 0.777777778 | 1.000000000 | 1.000000000 | 0.333333333 | False |
| dateblock5 | social_overload | Q2 | -0.002954707 | 0.001037468 | 0.777777778 | 1.000000000 | 1.000000000 | 0.333333333 | False |
| subject5 | routine_fragmentation | Q2 | -0.002792573 | 0.002224732 | 0.666666667 | 0.666666667 | 1.000000000 | 0.333333333 | False |
| dateblock5 | commute_pressure | Q3 | -0.002377026 | 0.001655031 | 0.666666667 | 1.000000000 | 1.000000000 | 0.000000000 | False |
| dateblock5 | bedtime_arousal | S3 | -0.002058459 | 0.000488769 | 0.777777778 | 1.000000000 | 1.000000000 | 0.333333333 | False |
| dateblock5 | routine_anchor_recovery | Q2 | -0.001740455 | 0.001254559 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | False |
| dateblock5 | cashflow_stress | S2 | -0.001615152 | 0.000600707 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | False |
| dateblock5 | routine_fragmentation | Q2 | -0.001319029 | 0.001015626 | 0.777777778 | 1.000000000 | 1.000000000 | 0.333333333 | False |
| subject5 | social_overload | Q3 | -0.001267438 | 0.002050442 | 0.777777778 | 0.666666667 | 1.000000000 | 0.666666667 | False |
| dateblock5 | physiology_strain | S2 | -0.001024478 | 0.001411632 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | False |
| dateblock5 | social_overload | S3 | -0.000973230 | 0.001515778 | 0.888888889 | 1.000000000 | 0.666666667 | 1.000000000 | False |
| dateblock5 | routine_anchor_recovery | S4 | -0.000763004 | 0.001682333 | 0.777777778 | 0.666666667 | 0.666666667 | 1.000000000 | False |
| subject5 | commute_pressure | S2 | -0.000745351 | 0.001396466 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | False |
| subject5 | cashflow_stress | S1 | -0.000573752 | 0.007523027 | 0.888888889 | 0.666666667 | 1.000000000 | 1.000000000 | False |
| subject5 | physiology_strain | S1 | -0.000557542 | 0.000383920 | 0.777777778 | 1.000000000 | 0.666666667 | 0.666666667 | False |
| dateblock5 | routine_fragmentation | S1 | -0.000454185 | 0.000984609 | 0.777777778 | 0.666666667 | 1.000000000 | 0.666666667 | False |
| subject5 | social_overload | S2 | -0.000439307 | 0.002422985 | 0.888888889 | 1.000000000 | 1.000000000 | 0.666666667 | False |
| dateblock5 | badnight_aftereffect | Q3 | -0.000392789 | -0.000246433 | 0.666666667 | 1.000000000 | 0.666666667 | 0.333333333 | False |
| subject5 | badnight_aftereffect | Q1 | -0.000326775 | 0.003172002 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | False |

## Public-Sensor Alignment

| feature | e256_q3_top20_d | e323_bad_top20_d | e368_q2s1_top20_d | max_abs_sensor_d |
| --- | --- | --- | --- | --- |
| hsjepa_resid_routine_fragmentation | 0.000000 | -0.281191 | 0.353520 | 0.353520 |
| hsjepa_resid_commute_pressure | 0.000000 | -0.325381 | 0.074302 | 0.325381 |
| hsjepa_pred_badnight_aftereffect | 0.000000 | -0.135548 | 0.306817 | 0.306817 |
| hsjepa_pc6 | 0.000000 | 0.080748 | -0.303318 | 0.303318 |
| hsjepa_resid_home_recovery | 0.000000 | 0.242619 | -0.289389 | 0.289389 |
| hsjepa_cluster_distance | 0.000000 | 0.289259 | -0.150671 | 0.289259 |
| hsjepa_resid_bedtime_arousal | 0.000000 | -0.058041 | 0.282650 | 0.282650 |
| hsjepa_resid_routine_anchor_recovery | 0.000000 | 0.262637 | -0.230982 | 0.262637 |
| hsjepa_pred_routine_fragmentation | 0.000000 | 0.256351 | -0.010751 | 0.256351 |
| hsjepa_pred_cashflow_stress | 0.000000 | 0.126446 | 0.241618 | 0.241618 |
| hsjepa_pred_commute_pressure | 0.000000 | -0.073144 | 0.238536 | 0.238536 |
| hsjepa_resid_badnight_aftereffect | 0.000000 | -0.042610 | 0.233639 | 0.233639 |
| hsjepa_pred_routine_anchor_recovery | 0.000000 | -0.069321 | -0.229022 | 0.229022 |
| hsjepa_surprise | 0.000000 | 0.209798 | -0.062351 | 0.209798 |
| hsjepa_resid_cashflow_relief_spend | 0.000000 | 0.144193 | -0.201773 | 0.201773 |
| hsjepa_pc8 | 0.000000 | -0.196278 | 0.160600 | 0.196278 |
| hsjepa_resid_physiology_strain | 0.000000 | 0.049363 | 0.189721 | 0.189721 |
| hsjepa_pc1 | 0.000000 | 0.011646 | 0.185217 | 0.185217 |
| hsjepa_pc2 | 0.000000 | -0.170603 | 0.061197 | 0.170603 |
| hsjepa_pc4 | 0.000000 | -0.159462 | -0.058334 | 0.159462 |
| hsjepa_resid_measurement_wear_confidence | 0.000000 | -0.107060 | 0.142074 | 0.142074 |
| hsjepa_k6 | 0.000000 | 0.140855 | -0.123202 | 0.140855 |
| hsjepa_pc7 | 0.000000 | 0.128095 | -0.117750 | 0.128095 |
| hsjepa_k5 | 0.000000 | -0.124655 | 0.124655 | 0.124655 |
| hsjepa_pred_cashflow_relief_spend | 0.000000 | -0.116841 | 0.077260 | 0.116841 |

## Cluster Story Read

| cluster | n_train | dominant_subject | Q1_rate | Q2_rate | Q3_rate | S1_rate | S2_rate | S3_rate | S4_rate | top_human_state_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 123 | id07 | 0.487805 | 0.560976 | 0.560976 | 0.715447 | 0.682927 | 0.739837 | 0.560976 | commute_pressure:0.94; social_overload:0.94; badnight_aftereffect:0.79; routine_anchor_recovery:-0.76; home_recovery:-0.71; measurement_wear_confidence:0.63; physiology_strain:0.62; bedtime_arousal:0.47 |
| 1 | 99 | id04 | 0.575758 | 0.585859 | 0.656566 | 0.747475 | 0.686869 | 0.575758 | 0.646465 | bedtime_arousal:-0.80; routine_fragmentation:-0.61; social_overload:-0.60; cashflow_stress:-0.52; home_recovery:0.48; measurement_wear_confidence:0.44; cashflow_relief_spend:0.37; badnight_aftereffect:0.34 |
| 5 | 72 | id08 | 0.555556 | 0.513889 | 0.597222 | 0.555556 | 0.597222 | 0.652778 | 0.555556 | bedtime_arousal:0.79; cashflow_stress:0.68; cashflow_relief_spend:-0.61; commute_pressure:-0.57; physiology_strain:0.53; routine_fragmentation:0.32; social_overload:-0.30; measurement_wear_confidence:0.21 |
| 4 | 64 | id06 | 0.484375 | 0.593750 | 0.625000 | 0.671875 | 0.640625 | 0.625000 | 0.515625 | measurement_wear_confidence:-1.45; badnight_aftereffect:-1.17; physiology_strain:-0.92; routine_fragmentation:0.56; social_overload:0.47; bedtime_arousal:0.44; home_recovery:-0.31; commute_pressure:-0.23 |
| 6 | 44 | id08 | 0.431818 | 0.636364 | 0.681818 | 0.613636 | 0.590909 | 0.477273 | 0.477273 | bedtime_arousal:-1.23; badnight_aftereffect:-1.13; physiology_strain:-1.00; routine_anchor_recovery:0.97; commute_pressure:-0.96; home_recovery:0.94; measurement_wear_confidence:-0.88; social_overload:-0.84 |
| 3 | 36 | id01 | 0.416667 | 0.611111 | 0.611111 | 0.638889 | 0.611111 | 0.861111 | 0.472222 | bedtime_arousal:0.25; badnight_aftereffect:0.23; measurement_wear_confidence:0.22; cashflow_stress:0.11; social_overload:0.10; home_recovery:-0.10; commute_pressure:0.09; physiology_strain:0.08 |
| 2 | 11 | id06 | 0.000000 | 0.000000 | 0.090909 | 1.000000 | 0.727273 | 0.909091 | 0.636364 | social_overload:-1.44; bedtime_arousal:-1.27; cashflow_stress:-0.88; routine_fragmentation:-0.61; routine_anchor_recovery:0.60; commute_pressure:-0.38; measurement_wear_confidence:0.37; badnight_aftereffect:-0.31 |
| 7 | 1 | id08 | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | cashflow_relief_spend:-1.71; bedtime_arousal:1.68; cashflow_stress:1.59; physiology_strain:1.31; routine_fragmentation:1.15; routine_anchor_recovery:-1.11; badnight_aftereffect:0.49; measurement_wear_confidence:0.49 |

## Candidate Translators

| candidate_id | file | basename | selected_targets | strict_route_count | weight | cap | changed_cells | mean_abs_logit_move | max_abs_logit_move | tail_top20_move_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| semantic_tiny | hitl/h003_hs_jepa_prototype/submission_h003_semantic_tiny_11e7aa3b.csv | submission_h003_semantic_tiny_11e7aa3b.csv | S3,S2,S4,Q3,Q2,Q1,S1 | 20 | 0.015000000 | 0.018000000 | 1750 | 0.007737851 | 0.018000000 | 0.209693869 |
| semantic_micro | hitl/h003_hs_jepa_prototype/submission_h003_semantic_micro_ebeebefd.csv | submission_h003_semantic_micro_ebeebefd.csv | S3,S2,S4,Q3,Q2,Q1,S1 | 20 | 0.025000000 | 0.030000000 | 1750 | 0.012896418 | 0.030000000 | 0.209693869 |
| semantic_tail_micro | hitl/h003_hs_jepa_prototype/submission_h003_semantic_tail_micro_fbdd9c4f.csv | submission_h003_semantic_tail_micro_fbdd9c4f.csv | S3,S2,S4,Q3,Q2,Q1,S1 | 20 | 0.035000000 | 0.035000000 | 1750 | 0.012425950 | 0.035000000 | 0.276523343 |

## Label Translator Meta

| target | route_episodes | train_rate | test_pred_mean | test_pred_std |
| --- | --- | --- | --- | --- |
| S3 | home_recovery,bedtime_arousal,social_overload,cashflow_stress | 0.662222 | 0.645858 | 0.216306 |
| S2 | routine_anchor_recovery,badnight_aftereffect | 0.651111 | 0.599827 | 0.209999 |
| S4 | home_recovery,commute_pressure | 0.560000 | 0.522856 | 0.192855 |
| Q3 | badnight_aftereffect | 0.600000 | 0.672699 | 0.125278 |
| Q2 | routine_anchor_recovery,home_recovery | 0.562222 | 0.594792 | 0.134189 |
| Q1 | physiology_strain,physiology_strain | 0.495556 | 0.568830 | 0.162964 |
| S1 | routine_fragmentation,bedtime_arousal,routine_anchor_recovery | 0.682222 | 0.682918 | 0.176440 |

## Public-Free Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h003_semantic_tiny_11e7aa3b.csv | below_selector_resolution | -0.000014939 | -0.000145481 | 0.000060253 | 0.416666667 | -0.015975352 |
| submission_h003_semantic_tail_micro_fbdd9c4f.csv | below_selector_resolution | -0.000041249 | -0.000315360 | 0.000092470 | 0.416666667 | -0.025075161 |
| submission_h003_semantic_micro_ebeebefd.csv | below_selector_resolution | -0.000019254 | -0.000266979 | 0.000124466 | 0.388888889 | -0.026625586 |

## Candidate Anatomy

| basename | cos_with_e323_bad_delta | l1_ratio_to_e323_delta | changed_rows | changed_cells | mean_abs_logit_delta | max_abs_prob_delta |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h003_semantic_tiny_11e7aa3b.csv | 0.016012297 | 0.304652522 | 250 | 1750 | 0.007737851 | 0.004499920 |
| submission_h003_semantic_tail_micro_fbdd9c4f.csv | 0.014936591 | 0.489231036 | 250 | 1750 | 0.012425950 | 0.008748728 |
| submission_h003_semantic_micro_ebeebefd.csv | 0.016012297 | 0.507754203 | 250 | 1750 | 0.012896418 | 0.007499859 |

## Selection

| decision | selected_uploadsafe_file | strict_promote_count | target_gate_count | route_gate_count | best_diagnostic_basename |
| --- | --- | --- | --- | --- | --- |
| diagnostic_only_no_h003_submission | none | 0 | 0 | 20 | submission_h003_semantic_tiny_11e7aa3b.csv |

## Decision

HS-JEPA produced a usable representation prototype, but its current probability translator is not strong enough. Keep the latent and rebuild the translator.

## Files

- `hitl/h003_hs_jepa_prototype/h003_hs_jepa_features.parquet`
- `hitl/h003_hs_jepa_prototype/h003_context_target_reconstruction.csv`
- `hitl/h003_hs_jepa_prototype/h003_latent_geometry.csv`
- `hitl/h003_hs_jepa_prototype/h003_positive_pair_diagnostics.csv`
- `hitl/h003_hs_jepa_prototype/h003_target_translation_stress.csv`
- `hitl/h003_hs_jepa_prototype/h003_episode_target_route_stress.csv`
- `hitl/h003_hs_jepa_prototype/h003_public_sensor_alignment.csv`
- `hitl/h003_hs_jepa_prototype/h003_candidates.csv`
- `hitl/h003_hs_jepa_prototype/h003_selector_scores.csv`
