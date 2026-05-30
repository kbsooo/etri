# E295 Human Episode-State JEPA Audit

## Question

Can raw lifelog stories be grouped into larger human episode states that are context-predictable and label-useful under matched null stress?

## Episode States

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

## Reconstruction Summary

| view_id | split | episode_count | r2_mean | r2_median | r2_positive_rate | corr_mean | abs_test_gap_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | 11 | 0.438241 | 0.434840 | 1.000000 | 0.667845 | 0.083148 |
| hybrid_context | dateblock5 | 11 | 0.333683 | 0.346770 | 0.909091 | 0.664787 | 0.068525 |
| raw_human_context | dateblock5 | 11 | -0.000509 | -0.073919 | 0.454545 | 0.473826 | 0.074327 |
| family_jepa_context | subject5 | 11 | -0.036365 | 0.185684 | 0.545455 | 0.533347 | 0.112008 |
| hybrid_context | subject5 | 11 | -0.313723 | -0.193702 | 0.272727 | 0.533865 | 0.076684 |
| raw_human_context | subject5 | 11 | -2.229614 | -2.565663 | 0.000000 | 0.315292 | 0.100069 |

## Best Episode Reconstructions

| view_id | split | episode | r2 | corr | train_test_pred_z_gap |
| --- | --- | --- | --- | --- | --- |
| family_jepa_context | dateblock5 | measurement_wear_confidence | 0.691952 | 0.834047 | 0.103608 |
| hybrid_context | dateblock5 | social_overload | 0.630662 | 0.804829 | -0.041595 |
| family_jepa_context | dateblock5 | badnight_aftereffect | 0.627828 | 0.799740 | 0.040325 |
| family_jepa_context | dateblock5 | commute_pressure | 0.622068 | 0.793812 | -0.164854 |
| hybrid_context | dateblock5 | bedtime_arousal | 0.619817 | 0.803435 | 0.134535 |
| family_jepa_context | dateblock5 | social_overload | 0.619660 | 0.789346 | -0.090534 |
| hybrid_context | dateblock5 | commute_pressure | 0.614188 | 0.794594 | -0.096703 |
| hybrid_context | dateblock5 | physiology_strain | 0.579418 | 0.781330 | 0.086117 |
| family_jepa_context | subject5 | badnight_aftereffect | 0.534533 | 0.759422 | 0.038391 |
| raw_human_context | dateblock5 | bedtime_arousal | 0.480467 | 0.729085 | 0.017386 |
| family_jepa_context | dateblock5 | bedtime_arousal | 0.461831 | 0.693037 | 0.049858 |
| hybrid_context | dateblock5 | badnight_aftereffect | 0.459586 | 0.734727 | 0.062356 |
| raw_human_context | dateblock5 | badnight_aftereffect | 0.450160 | 0.699820 | 0.118638 |
| raw_human_context | dateblock5 | physiology_strain | 0.442388 | 0.729604 | 0.115628 |
| family_jepa_context | dateblock5 | physiology_strain | 0.434840 | 0.674065 | 0.109869 |
| family_jepa_context | subject5 | measurement_wear_confidence | 0.420889 | 0.727874 | 0.069763 |
| family_jepa_context | dateblock5 | routine_anchor_recovery | 0.358643 | 0.621748 | 0.026180 |
| hybrid_context | dateblock5 | routine_anchor_recovery | 0.346770 | 0.638318 | -0.006178 |
| family_jepa_context | subject5 | commute_pressure | 0.315842 | 0.678132 | -0.105584 |
| family_jepa_context | dateblock5 | cashflow_stress | 0.313868 | 0.578680 | -0.079165 |
| raw_human_context | dateblock5 | measurement_wear_confidence | 0.304734 | 0.681384 | 0.161803 |
| family_jepa_context | dateblock5 | cashflow_relief_spend | 0.280783 | 0.555813 | 0.102321 |
| family_jepa_context | subject5 | physiology_strain | 0.226499 | 0.604054 | 0.170002 |
| hybrid_context | dateblock5 | cashflow_stress | 0.224413 | 0.578043 | -0.055060 |
| family_jepa_context | dateblock5 | routine_fragmentation | 0.221922 | 0.518144 | -0.050025 |
| family_jepa_context | subject5 | cashflow_relief_spend | 0.200637 | 0.520090 | 0.025711 |
| hybrid_context | subject5 | badnight_aftereffect | 0.190429 | 0.654902 | 0.005790 |
| family_jepa_context | dateblock5 | home_recovery | 0.187251 | 0.487861 | 0.097885 |
| hybrid_context | dateblock5 | measurement_wear_confidence | 0.185990 | 0.657995 | 0.101775 |
| hybrid_context | dateblock5 | routine_fragmentation | 0.185872 | 0.555281 | 0.022579 |

## Bundle Label Stress

| view_id | split | rep | actual_delta_mean | actual_delta_best | actual_delta_worst | targets_improved | null_q20 | null_median | null_best | dominance | label_gate | Q1_delta | Q2_delta | Q3_delta | S1_delta | S2_delta | S3_delta | S4_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hybrid_context | dateblock5 | episode_pc | 0.009103 | 0.000786 | 0.021073 | 0 | 0.007692 | 0.009666 | 0.003154 | 0.583333 | False | 0.005283 | 0.021073 | 0.001632 | 0.000786 | 0.017008 | 0.005779 | 0.012160 |
| family_jepa_context | dateblock5 | episode_pc | 0.009460 | -0.001386 | 0.021450 | 1 | 0.006552 | 0.007979 | 0.003589 | 0.250000 | False | 0.009472 | 0.021450 | -0.001386 | 0.009200 | 0.015637 | 0.008050 | 0.003797 |
| raw_human_context | dateblock5 | episode_pc | 0.011158 | -0.002796 | 0.031823 | 1 | 0.008969 | 0.010568 | 0.007944 | 0.500000 | False | 0.006154 | 0.015191 | 0.031823 | -0.002796 | 0.009360 | 0.010942 | 0.007430 |
| family_jepa_context | dateblock5 | episode_scores | 0.017189 | 0.005262 | 0.038776 | 0 | 0.013967 | 0.015553 | 0.009316 | 0.333333 | False | 0.007816 | 0.038776 | 0.005262 | 0.008343 | 0.026685 | 0.012763 | 0.020679 |
| hybrid_context | subject5 | episode_pc | 0.023534 | -0.002885 | 0.044880 | 1 | 0.008209 | 0.015662 | 0.005681 | 0.083333 | False | 0.028776 | 0.036370 | 0.007969 | 0.044880 | 0.027274 | -0.002885 | 0.022355 |
| family_jepa_context | subject5 | episode_pc | 0.023905 | -0.000483 | 0.049693 | 1 | 0.006021 | 0.012820 | 0.004830 | 0.250000 | False | 0.019774 | 0.020725 | 0.049693 | 0.031035 | -0.000483 | 0.024225 | 0.022367 |
| hybrid_context | dateblock5 | episode_scores | 0.025020 | 0.008877 | 0.061137 | 0 | 0.014555 | 0.019231 | 0.011614 | 0.166667 | False | 0.016425 | 0.061137 | 0.008877 | 0.011106 | 0.037413 | 0.016060 | 0.024118 |
| raw_human_context | dateblock5 | episode_scores | 0.025866 | 0.009075 | 0.041261 | 0 | 0.018787 | 0.022669 | 0.009812 | 0.333333 | False | 0.017433 | 0.041261 | 0.023921 | 0.029230 | 0.041107 | 0.019033 | 0.009075 |
| family_jepa_context | subject5 | episode_scores | 0.038309 | 0.012334 | 0.065320 | 0 | 0.017229 | 0.025616 | 0.009781 | 0.166667 | False | 0.043989 | 0.026958 | 0.065320 | 0.033138 | 0.012334 | 0.031820 | 0.054604 |
| hybrid_context | subject5 | episode_scores | 0.038727 | 0.001722 | 0.078219 | 0 | 0.018259 | 0.026502 | 0.010202 | 0.166667 | False | 0.078219 | 0.041273 | 0.001722 | 0.064594 | 0.031253 | 0.017809 | 0.036223 |
| raw_human_context | subject5 | episode_pc | 0.041845 | -0.009791 | 0.101974 | 1 | 0.011499 | 0.021404 | 0.008888 | 0.083333 | False | 0.037983 | 0.037413 | 0.019286 | -0.009791 | 0.054142 | 0.051909 | 0.101974 |
| raw_human_context | subject5 | episode_scores | 0.058343 | -0.001683 | 0.131060 | 1 | 0.013101 | 0.038738 | 0.009706 | 0.083333 | False | 0.069632 | 0.077540 | -0.001683 | 0.023371 | 0.073415 | 0.035063 | 0.131060 |

## Target-Specific Episode Gates

| view_id | split | episode | target | delta_logloss | null_median | null_best | dominance | row_dominance | subject_dominance | dateblock_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_human_context | subject5 | cashflow_stress | S1 | -0.017244 | 0.002440 | -0.020730 | 0.916667 | 1.000000 | 0.750000 | 1.000000 |
| raw_human_context | subject5 | bedtime_arousal | S1 | -0.017000 | 0.002002 | -0.007997 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | bedtime_arousal | S3 | -0.016376 | 0.000452 | -0.008625 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | subject5 | badnight_aftereffect | Q3 | -0.015000 | 0.001323 | -0.014008 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | cashflow_stress | S1 | -0.013144 | 0.001753 | -0.007849 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | subject5 | routine_fragmentation | S1 | -0.011595 | 0.000188 | -0.009036 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | social_overload | S3 | -0.011343 | 0.000179 | -0.009478 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | subject5 | routine_anchor_recovery | S1 | -0.010700 | -0.000839 | -0.020711 | 0.916667 | 1.000000 | 0.750000 | 1.000000 |
| raw_human_context | subject5 | physiology_strain | S1 | -0.010361 | 0.002040 | -0.011067 | 0.916667 | 1.000000 | 0.750000 | 1.000000 |
| raw_human_context | dateblock5 | routine_fragmentation | S1 | -0.009804 | 0.001489 | -0.002515 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | dateblock5 | home_recovery | S3 | -0.009509 | 0.003116 | -0.001318 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | home_recovery | S3 | -0.009217 | 0.001101 | -0.004046 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | routine_anchor_recovery | S2 | -0.009187 | 0.001138 | -0.008468 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | dateblock5 | commute_pressure | S2 | -0.008906 | 0.002697 | -0.001037 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | routine_fragmentation | S3 | -0.007785 | 0.001230 | -0.003978 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | subject5 | social_overload | Q3 | -0.007727 | 0.002259 | -0.014067 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| hybrid_context | dateblock5 | cashflow_stress | S1 | -0.007484 | 0.000961 | -0.011924 | 0.916667 | 1.000000 | 0.750000 | 1.000000 |
| raw_human_context | dateblock5 | bedtime_arousal | S1 | -0.006915 | 0.001194 | -0.006267 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | badnight_aftereffect | Q1 | -0.006496 | 0.002810 | -0.004260 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | cashflow_relief_spend | Q3 | -0.006493 | 0.000585 | -0.007494 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| raw_human_context | subject5 | commute_pressure | Q3 | -0.005833 | 0.000133 | -0.002688 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | home_recovery | S2 | -0.005070 | 0.000548 | -0.005994 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| raw_human_context | dateblock5 | home_recovery | S4 | -0.005056 | 0.005364 | -0.003045 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | routine_fragmentation | S2 | -0.005052 | 0.000919 | -0.003007 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | dateblock5 | measurement_wear_confidence | S4 | -0.004792 | 0.000975 | -0.006657 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| hybrid_context | subject5 | cashflow_relief_spend | S2 | -0.004667 | 0.000791 | -0.003018 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | dateblock5 | routine_anchor_recovery | S3 | -0.004538 | 0.001125 | -0.001035 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | dateblock5 | routine_fragmentation | S3 | -0.004319 | 0.001978 | -0.008014 | 0.916667 | 1.000000 | 0.750000 | 1.000000 |
| family_jepa_context | dateblock5 | physiology_strain | S4 | -0.004256 | 0.002664 | -0.007178 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| hybrid_context | dateblock5 | social_overload | S3 | -0.004202 | 0.001259 | -0.004985 | 0.916667 | 0.750000 | 1.000000 | 1.000000 |
| family_jepa_context | dateblock5 | home_recovery | S3 | -0.004116 | 0.001141 | -0.002975 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | subject5 | bedtime_arousal | S4 | -0.004059 | 0.003063 | -0.007548 | 0.916667 | 0.750000 | 1.000000 | 1.000000 |
| family_jepa_context | dateblock5 | social_overload | S3 | -0.004046 | 0.002052 | -0.000908 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | dateblock5 | commute_pressure | S4 | -0.003959 | 0.000714 | -0.002313 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| family_jepa_context | dateblock5 | badnight_aftereffect | S4 | -0.003668 | 0.001946 | -0.000261 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| hybrid_context | subject5 | routine_anchor_recovery | S3 | -0.003611 | 0.001183 | -0.004055 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| hybrid_context | dateblock5 | routine_anchor_recovery | S2 | -0.003513 | 0.001256 | -0.002314 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | dateblock5 | cashflow_stress | S3 | -0.003159 | 0.001056 | -0.007246 | 0.916667 | 1.000000 | 1.000000 | 0.750000 |
| hybrid_context | dateblock5 | cashflow_stress | Q1 | -0.003050 | 0.001685 | -0.002193 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| raw_human_context | subject5 | social_overload | S3 | -0.002353 | 0.000791 | -0.002074 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |

## Episode Family Read

| episode | best_delta | mean_delta | target_gates | best_dominance |
| --- | --- | --- | --- | --- |
| badnight_aftereffect | -0.015000 | 0.003087 | 8 | 1.000000 |
| routine_anchor_recovery | -0.010700 | 0.004186 | 7 | 1.000000 |
| cashflow_stress | -0.017244 | 0.002600 | 6 | 1.000000 |
| home_recovery | -0.009509 | 0.005769 | 6 | 1.000000 |
| routine_fragmentation | -0.011595 | 0.004200 | 5 | 1.000000 |
| social_overload | -0.011343 | 0.006031 | 5 | 1.000000 |
| bedtime_arousal | -0.017000 | 0.003316 | 4 | 1.000000 |
| commute_pressure | -0.008906 | 0.005441 | 3 | 1.000000 |
| cashflow_relief_spend | -0.006493 | 0.002306 | 3 | 1.000000 |
| physiology_strain | -0.010361 | 0.004858 | 2 | 0.916667 |
| measurement_wear_confidence | -0.004792 | 0.003884 | 2 | 0.916667 |

## Decision

E295 found train/null-surviving episode-state signals. These are not submissions yet; next step is a materialization governor only for the gated episode-target rows.

## Interpretation

This experiment is deliberately more human than cell-level surgery: commute pressure, bedtime arousal, routine fragmentation/anchor, cash-flow stress/relief, physiology strain, home recovery, social overload, measurement confidence, and bad-night aftereffect are treated as hidden day-level states. A state only matters if another context can predict it and if that predicted state beats row/subject/dateblock shuffles on labels.

## Files

- `e295_episode_state_definition.csv`
- `e295_episode_state_recon_summary.csv`
- `e295_episode_state_label_stress.csv`
- `e295_episode_state_target_detail.csv`
- `e295_episode_state_nulls.csv`
