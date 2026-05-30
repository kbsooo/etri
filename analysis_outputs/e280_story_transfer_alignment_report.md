# E280 Story Transfer and Row-Alignment Atlas

## Question

Public LB cannot be used as the iteration loop. The question here is whether the human/social and payday stories are transferable hidden-state signals or only public-boundary diagnostics.

## Method

- Combine E268 human/social stories and E270 payday/cash-flow stories.
- Score each story by label lift, blocked CV delta, train/test feature stability, E278 train row-alignment support, E273 JEPA family reconstructability, and E275 q-sleep row overlap.
- Treat E247/E256/E267 movement alignment as a weak diagnostic only, not as a promotion rule.
- Produce no submission file.

## Public-Free Guardrail

- E279 audited candidates: `66`
- E279 submission-ready candidates: `0`
- E279 matched-placebo gate passes: `0`
- prior social direct gates in E269: `7` tiny/materialization candidates
- prior cash-flow direct gates in E271: `6` tiny/materialization candidates
- q-sleep candidates blocked by matched placebo: `13`

Read: a story can be real and still not be submission-ready. Direct row edits remain blocked unless they beat matched row/subject/dateblock nulls.

## Summary Counts

- total stories audited: `86`
- alive for story-state gate: `3`
- alive but needs transfer test: `23`
- blocked by train/test transfer gap: `6`
- public-anchor diagnostic only: `6`

## Top Transfer Stories

| story_id | source | mapped_family | transfer_survival_score | e280_verdict | best_label_target | best_label_abs_effect | best_dateblock_delta | subject_best_delta | score_train_test_z_gap | e275_qsleep_selected_q3_d | jepa_context_oof_r2_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| commute_workday | human_social | mobility_context | 0.791906 | alive_for_story_state_gate | S4 | 0.168142 | -0.011513 | -0.041825 | 0.080707 | -0.218253 | 0.638181 |
| bright_light_late | human_social | bedtime_phone | 0.781993 | alive_for_story_state_gate | S4 | 0.203540 | -0.013849 | -0.006700 | 0.020057 | 0.028638 | 0.588066 |
| vehicle_noise_day | human_social | mobility_context | 0.716287 | diagnostic_story_only | S3 | 0.088496 | -0.011397 | -0.045630 | 0.070339 | -0.269566 | 0.638181 |
| single_app_monotony | human_social | routine_calendar | 0.716179 | alive_but_needs_transfer_test | Q3 | 0.203540 | -0.008958 | -0.059585 | 0.031502 | 0.140463 | 0.099948 |
| app_entropy_scattered_day | human_social | routine_calendar | 0.649240 | alive_but_needs_transfer_test | Q3 | 0.168142 | -0.006340 | -0.031234 | 0.038060 | -0.129778 | 0.099948 |
| heart_stress_late | human_social | physiology_activity | 0.613616 | alive_but_needs_transfer_test | Q3 | 0.149027 | -0.016048 | -0.017291 | 0.134958 | 0.012513 | 0.861479 |
| outdoor_nature_day | human_social | mobility_context | 0.602621 | diagnostic_story_only | Q1 | 0.097345 | -0.001800 | -0.017389 | 0.026121 | -0.113621 | 0.638181 |
| morning_after_badnight | human_social | diary_global | 0.593819 | alive_for_story_state_gate | Q2 | 0.159292 | -0.003585 | -0.018539 | 0.121185 | -0.135498 |  |
| quiet_dark_bedtime | human_social | routine_calendar | 0.582313 | alive_but_needs_transfer_test | S4 | 0.115044 | -0.011893 | -0.022731 | 0.014863 | -0.002853 | 0.099948 |
| media_binge_late | human_social | media_game | 0.580289 | diagnostic_story_only | Q2 | 0.194690 | -0.002340 | -0.012053 | 0.012658 | -0.125996 | 0.561328 |
| night_out_mobility | human_social | mobility_context | 0.567439 | diagnostic_story_only | S4 | 0.107880 | 0.002416 | -0.010045 | 0.022930 | -0.165731 | 0.638181 |
| weekday_routine_pressure | human_social | routine_calendar | 0.561285 | diagnostic_story_only | S3 | 0.079646 | -0.008318 | -0.039209 | 0.022966 | -0.000913 | 0.099948 |
| phone_in_bed | human_social | bedtime_phone | 0.554765 | public_anchor_diagnostic_only | Q2 | 0.070796 | -0.001091 | -0.011789 | 0.031163 | -0.120349 | 0.588066 |
| paymonth_start_post7_spend_outing | cashflow | cognitive_money | 0.553285 | alive_but_needs_transfer_test | S2 | 0.102080 | -0.015117 | -0.021504 | 0.055492 | 0.157790 | -0.106007 |
| monthstart_spending_reset | cashflow | cognitive_money | 0.551867 | alive_but_needs_transfer_test | S3 | 0.121739 | -0.014516 | -0.020994 | 0.106503 | 0.110462 | -0.106007 |
| paymonth_start_post3_late_shopping | cashflow | cognitive_money | 0.551476 | alive_but_needs_transfer_test | S2 | 0.238756 | -0.008061 | -0.002187 | 0.068398 | -0.128883 | -0.106007 |
| weekend_ritual_rest | human_social | routine_calendar | 0.550726 | public_anchor_diagnostic_only | Q3 | 0.221239 | -0.005106 | -0.002539 | 0.043567 | -0.126384 | 0.099948 |
| low_hr_recovery | human_social | physiology_activity | 0.549628 | diagnostic_story_only | Q3 | 0.194690 | -0.006106 | -0.001893 | 0.058775 | -0.115074 | 0.861479 |
| ritual_anchor | human_social | routine_calendar | 0.546187 | alive_but_needs_transfer_test | Q3 | 0.177376 | -0.009102 | 0.005602 | 0.014599 | -0.193411 | 0.099948 |
| sedentary_screen_day | human_social | media_game | 0.531442 | diagnostic_story_only | Q2 | 0.168142 | -0.002176 | -0.011899 | 0.047580 | -0.114933 | 0.561328 |

## Family-Level Read

| mapped_family | n_stories | alive_story_state_gate_n | alive_needs_transfer_test_n | blocked_transfer_gap_n | max_transfer_survival_score | top_story_id | e278_only_gate_count | jepa_context_oof_r2_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobility_context | 5 | 1 | 0 | 0 | 0.791906 | commute_workday | 2 | 0.638181 |
| bedtime_phone | 4 | 1 | 0 | 0 | 0.781993 | bright_light_late | 2 | 0.588066 |
| diary_global | 1 | 1 | 0 | 0 | 0.593819 | morning_after_badnight | 2 |  |
| routine_calendar | 21 | 0 | 9 | 3 | 0.716179 | single_app_monotony | 0 | 0.099948 |
| physiology_activity | 4 | 0 | 2 | 0 | 0.613616 | heart_stress_late | 0 | 0.861479 |
| media_game | 4 | 0 | 1 | 0 | 0.580289 | media_binge_late | 0 | 0.561328 |
| cognitive_money | 41 | 0 | 10 | 3 | 0.553285 | paymonth_start_post7_spend_outing | 0 | -0.106007 |
| social_comm | 4 | 0 | 0 | 0 | 0.484128 | social_isolation_media | 0 | 0.579755 |
| sensor_measurement | 2 | 0 | 1 | 0 | 0.475914 | sensor_sparse_day | 0 | 0.967658 |

## Main Contradictions

| story_id | source | mapped_family | contradiction_type | transfer_survival_score | best_label_abs_effect | best_dateblock_delta | score_train_test_z_gap | public_align_score | e280_verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single_app_monotony | human_social | routine_calendar | local_cv_without_qsleep_family_support | 0.716179 | 0.203540 | -0.008958 | 0.031502 | 1.200200 | alive_but_needs_transfer_test |
| app_entropy_scattered_day | human_social | routine_calendar | local_cv_without_qsleep_family_support | 0.649240 | 0.168142 | -0.006340 | 0.038060 | 1.333283 | alive_but_needs_transfer_test |
| heart_stress_late | human_social | physiology_activity | local_cv_without_qsleep_family_support | 0.613616 | 0.149027 | -0.016048 | 0.134958 | 0.389224 | alive_but_needs_transfer_test |
| quiet_dark_bedtime | human_social | routine_calendar | local_cv_without_qsleep_family_support | 0.582313 | 0.115044 | -0.011893 | 0.014863 | 0.106453 | alive_but_needs_transfer_test |
| weekday_routine_pressure | human_social | routine_calendar | local_cv_without_qsleep_family_support | 0.561285 | 0.079646 | -0.008318 | 0.022966 | 0.604368 | diagnostic_story_only |
| phone_in_bed | human_social | bedtime_phone | public_sensor_without_local_cv | 0.554765 | 0.070796 | -0.001091 | 0.031163 | 1.503433 | public_anchor_diagnostic_only |
| paymonth_start_post7_spend_outing | cashflow | cognitive_money | local_cv_without_qsleep_family_support | 0.553285 | 0.102080 | -0.015117 | 0.055492 | 0.082842 | alive_but_needs_transfer_test |
| monthstart_spending_reset | cashflow | cognitive_money | local_cv_without_qsleep_family_support | 0.551867 | 0.121739 | -0.014516 | 0.106503 | 0.458374 | alive_but_needs_transfer_test |
| weekend_ritual_rest | human_social | routine_calendar | public_sensor_without_local_cv | 0.550726 | 0.221239 | -0.005106 | 0.043567 | 1.239223 | public_anchor_diagnostic_only |
| pay20_post3_relief_home | cashflow | routine_calendar | local_cv_without_qsleep_family_support | 0.504515 | 0.160145 | -0.011568 | 0.131549 | 1.012623 | alive_but_needs_transfer_test |
| social_isolation_media | human_social | social_comm | local_cv_without_qsleep_family_support | 0.484128 | 0.053097 | -0.005494 | 0.047552 | 1.126364 | diagnostic_story_only |
| pay15_post3_relief_home | cashflow | routine_calendar | public_sensor_without_local_cv | 0.472064 | 0.205985 | -0.000694 | 0.042709 | 1.086322 | public_anchor_diagnostic_only |
| pay20_post7_spend_outing | cashflow | cognitive_money | local_cv_without_qsleep_family_support | 0.467946 | 0.137657 | -0.006662 | 0.109169 | 0.288458 | alive_but_needs_transfer_test |
| pay15_post3_late_shopping | cashflow | cognitive_money | local_cv_without_qsleep_family_support | 0.467511 | 0.326243 | -0.008158 | 0.300791 | 0.941488 | blocked_transfer_gap |
| public_social_evening | human_social | social_comm | local_cv_without_qsleep_family_support | 0.441655 | 0.067544 | 0.000656 | 0.104503 | 0.179702 | diagnostic_story_only |
| pay10_pre7_budget_squeeze | cashflow | cognitive_money | local_cv_without_qsleep_family_support | 0.385172 | 0.091273 | -0.004389 | 0.178148 | 0.495730 | diagnostic_story_only |
| pay15_post3_spend_outing | cashflow | cognitive_money | public_sensor_without_local_cv | 0.374783 | 0.113021 | -0.002574 | 0.036939 | 1.050137 | public_anchor_diagnostic_only |
| pay25_near7_calendar_only | cashflow | routine_calendar | local_cv_without_qsleep_family_support | 0.371331 | 0.089040 | -0.007581 | 0.240444 | 0.849246 | diagnostic_story_only |
| monthstart_reset_relief | cashflow | cognitive_money | public_sensor_without_local_cv | 0.366116 | 0.119715 | -0.003304 | 0.152666 | 1.014354 | public_anchor_diagnostic_only |
| pay15_pre7_budget_squeeze | cashflow | cognitive_money | public_sensor_without_local_cv | 0.357924 | 0.226608 | 0.003088 | 0.286506 | 1.320757 | blocked_transfer_gap |

## Next Public-Free Tests

| priority | story_id | source | mapped_family | test_name | belief_that_can_die | success_rule | do_not_do | transfer_survival_score | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | commute_workday | human_social | mobility_context | masked_context_to_mobility_context_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.791906 | Build a row selector and require matched row/subject/dateblock null survival. |
| 2 | bright_light_late | human_social | bedtime_phone | masked_context_to_bedtime_phone_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.781993 | Build a row selector and require matched row/subject/dateblock null survival. |
| 3 | single_app_monotony | human_social | routine_calendar | masked_context_to_routine_calendar_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.716179 | Run a masked context->story-state test before any materialization. |
| 4 | app_entropy_scattered_day | human_social | routine_calendar | masked_context_to_routine_calendar_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.649240 | Run a masked context->story-state test before any materialization. |
| 5 | heart_stress_late | human_social | physiology_activity | masked_context_to_physiology_activity_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.613616 | Run a masked context->story-state test before any materialization. |
| 6 | morning_after_badnight | human_social | diary_global | masked_context_to_diary_global_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.593819 | Build a row selector and require matched row/subject/dateblock null survival. |
| 7 | quiet_dark_bedtime | human_social | routine_calendar | masked_context_to_routine_calendar_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.582313 | Run a masked context->story-state test before any materialization. |
| 8 | paymonth_start_post7_spend_outing | cashflow | cognitive_money | masked_context_to_cognitive_money_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.553285 | Run a masked context->story-state test before any materialization. |
| 9 | monthstart_spending_reset | cashflow | cognitive_money | masked_context_to_cognitive_money_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.551867 | Run a masked context->story-state test before any materialization. |
| 10 | paymonth_start_post3_late_shopping | cashflow | cognitive_money | masked_context_to_cognitive_money_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.551476 | Run a masked context->story-state test before any materialization. |
| 11 | ritual_anchor | human_social | routine_calendar | masked_context_to_routine_calendar_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.546187 | Run a masked context->story-state test before any materialization. |
| 12 | charge_bed_anchor | human_social | routine_calendar | masked_context_to_routine_calendar_story_state | Story row placement transfers from train hidden state to test hidden state. | OOF gain plus row/subject/dateblock matched-null dominance; no public LB needed. | Do not create a direct Q3 boundary edit from this story alone. | 0.522064 | Run a masked context->story-state test before any materialization. |

## Decision

No submission is recommended from E280. The strongest surviving direction is not a tiny public-boundary edit; it is a masked context-to-story-state row selector whose row placement must beat matched nulls before public LB is touched.

## Files

- `e280_story_transfer_alignment_summary.csv`
- `e280_story_transfer_alignment_family_summary.csv`
- `e280_story_transfer_alignment_contradictions.csv`
- `e280_story_transfer_alignment_next_tests.csv`
