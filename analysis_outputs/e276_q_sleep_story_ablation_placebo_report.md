# E276 Q-Sleep Story Ablation + Placebo Audit

## Question

Does the E275 q-sleep diary-energy candidate survive because it encodes coherent human lifestyle state, or because the public-free selector likes any Q-side movement with similar magnitude?

## Gate

- selected E272-style selector models: `1`
- primary E275 p90 delta vs E247: `-0.000084726`
- strict semantic/control variants: `10`
- strict shuffled placebos: `13`

## Axis Families In The E275 Story

| target | story_family | axis_kind | n_axes | mean_local_axis_score | min_dateblock_delta | mean_abs_label_lift | features |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | mobility_context | jepa_prednorm | 2 | 0.029247407 | -0.013697360 | 0.292035398 | jepa_prednorm_dateblock_mobility_context;jepa_prednorm_subject_mobility_context |
| Q3 | routine_calendar | jepa_prednorm | 1 | 0.027476442 | -0.018569811 | 0.185840708 | jepa_prednorm_subject_routine_calendar |
| Q3 | bedtime_phone | jepa_resid | 1 | 0.026605531 | -0.018941832 | 0.203539823 | jepa_resid_subject_bedtime_phone |
| Q3 | mobility_context | energy | 1 | 0.026042339 | -0.013127964 | 0.256637168 | mobility_context_energy |
| Q2 | media_game | pc | 1 | 0.022828890 | -0.015133742 | 0.194690265 | media_game_pc2 |
| Q3 | diary_global | energy | 1 | 0.022800618 | -0.012069679 | 0.185840708 | diary_state_energy |
| Q3 | cognitive_money | jepa_prednorm | 1 | 0.022787828 | -0.015051731 | 0.176991150 | jepa_prednorm_subject_cognitive_money |
| Q3 | social_comm | energy | 1 | 0.015223527 | -0.006555757 | 0.132743363 | social_comm_energy |
| Q3 | diary_global | pc | 1 | 0.013915673 | -0.007072569 | 0.176991150 | diary_state_pc1 |
| Q2 | diary_global | pc | 1 | 0.010879351 | -0.004355192 | 0.185840708 | diary_state_pc10 |
| Q1 | mobility_context | jepa_prednorm | 1 | 0.009081410 | -0.002045565 | 0.203539823 | jepa_prednorm_subject_mobility_context |

## Semantic Ablation Scores

| basename | variant_type | family_tested | axis_kind_tested | axis_count | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e276_no_media_game_m160_72fc6fa6.csv | axis_ablation | media_game | leave_one_out | 11.000000000 | promote_candidate | -0.000229075 | -0.000129314 | 1.000000000 | -0.010213869 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | axis_ablation | mobility_context | only | 4.000000000 | promote_candidate | -0.000130580 | -0.000095305 | 1.000000000 | -0.006209848 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | axis_ablation | all | jepa_only | 6.000000000 | promote_candidate | -0.000133692 | -0.000093390 | 1.000000000 | -0.008256811 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | axis_ablation | social_comm | leave_one_out | 11.000000000 | promote_candidate | -0.000186941 | -0.000092156 | 0.970588235 | -0.003803609 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | axis_ablation | cognitive_money | leave_one_out | 11.000000000 | promote_candidate | -0.000194311 | -0.000086281 | 0.970588235 | -0.003035236 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | primary | all | all | 12.000000000 | promote_candidate | -0.000190473 | -0.000084726 | 0.970588235 | -0.004007782 |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | axis_ablation | all | all | 12.000000000 | promote_candidate | -0.000188014 | -0.000082769 | 0.970588235 | -0.003779790 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | axis_ablation | routine_calendar | leave_one_out | 11.000000000 | promote_candidate | -0.000167479 | -0.000072275 | 0.970588235 | -0.003028825 |
| submission_e276_q3_only_m160_6034ca83.csv | axis_ablation | q3_only | all | 9.000000000 | promote_candidate | -0.000118807 | -0.000057680 | 1.000000000 | -0.008487964 |
| submission_e276_no_diary_global_m160_d8951434.csv | axis_ablation | diary_global | leave_one_out | 9.000000000 | promote_candidate | -0.000125204 | -0.000050408 | 0.970588235 | -0.001347709 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | axis_ablation | bedtime_phone | leave_one_out | 11.000000000 | too_small_to_submit | -0.000134969 | -0.000040128 | 0.941176471 | -0.000916141 |
| submission_e276_q12_only_m160_7bcd965c.csv | axis_ablation | q12_only | all | 3.000000000 | too_small_to_submit | -0.000069206 | 0.000004534 | 0.882352941 | 0.004708174 |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | axis_ablation | routine_calendar | only | 1.000000000 | below_selector_resolution | 0.000004124 | 0.000028507 | 0.558823529 | 0.000663229 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | axis_ablation | social_comm | only | 1.000000000 | below_selector_resolution | 0.000020825 | 0.000036001 | 0.058823529 | 0.000603428 |
| submission_e276_only_media_game_m160_8f065696.csv | axis_ablation | media_game | only | 1.000000000 | below_selector_resolution | 0.000042889 | 0.000076317 | 0.117647059 | 0.008126647 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | axis_ablation | bedtime_phone | only | 1.000000000 | below_selector_resolution | 0.000063463 | 0.000083706 | 0.000000000 | 0.001389854 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | axis_ablation | cognitive_money | only | 1.000000000 | below_selector_resolution | 0.000070131 | 0.000090007 | 0.000000000 | 0.000821391 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | axis_ablation | diary_global | only | 3.000000000 | block_or_reject | 0.000094796 | 0.000118033 | 0.058823529 | 0.005298419 |
| submission_e276_no_mobility_context_m160_68587259.csv | axis_ablation | mobility_context | leave_one_out | 8.000000000 | below_selector_resolution | 0.000103989 | 0.000148352 | 0.088235294 | 0.008267111 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | axis_ablation | all | nonjepa_only | 6.000000000 | block_or_reject | 0.000129312 | 0.000183796 | 0.058823529 | 0.011175668 |
| submission_e276_inverse_primary_m080_4574c953.csv | inverse_control | all | inverse | 12.000000000 | below_selector_resolution | 0.000110348 | 0.000207722 | 0.058823529 | 0.003206226 |

## Placebo Shuffle Summary

| family_tested | n | strict_promote | best_p90 | mean_p90 | best_mean |
| --- | --- | --- | --- | --- | --- |
| dateblock | 5 | 5 | -0.000132538 | -0.000102799 | -0.000283562 |
| subject | 5 | 4 | -0.000123510 | -0.000073958 | -0.000265323 |
| row | 5 | 4 | -0.000091288 | -0.000078948 | -0.000291646 |

## Top Placebo Rows

| basename | variant_type | family_tested | axis_kind_tested | axis_count | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e276_shuffle_dateblock_r0_86ba3e14.csv | shuffle_placebo | dateblock | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000283562 | -0.000132538 | 1.000000000 | -0.007250400 |
| submission_e276_shuffle_subject_r0_8c7d1ff6.csv | shuffle_placebo | subject | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000265323 | -0.000123510 | 1.000000000 | -0.002794039 |
| submission_e276_shuffle_dateblock_r2_212ad15a.csv | shuffle_placebo | dateblock | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000252071 | -0.000110998 | 1.000000000 | -0.001289261 |
| submission_e276_shuffle_dateblock_r4_620d6f89.csv | shuffle_placebo | dateblock | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000239003 | -0.000107250 | 1.000000000 | -0.002374453 |
| submission_e276_shuffle_row_r0_4a3bd132.csv | shuffle_placebo | row | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000279287 | -0.000091288 | 1.000000000 | -0.011232504 |
| submission_e276_shuffle_row_r1_ac0d437e.csv | shuffle_placebo | row | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000291646 | -0.000090094 | 1.000000000 | -0.002693598 |
| submission_e276_shuffle_row_r2_baca8ed7.csv | shuffle_placebo | row | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000181889 | -0.000085096 | 1.000000000 | 0.001995536 |
| submission_e276_shuffle_dateblock_r3_281b5e46.csv | shuffle_placebo | dateblock | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000221243 | -0.000085049 | 1.000000000 | -0.005156570 |
| submission_e276_shuffle_subject_r2_c860bcea.csv | shuffle_placebo | subject | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000185615 | -0.000083408 | 1.000000000 | 0.000669575 |
| submission_e276_shuffle_row_r3_c424f61b.csv | shuffle_placebo | row | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000255762 | -0.000080190 | 1.000000000 | -0.002465479 |
| submission_e276_shuffle_dateblock_r1_17882307.csv | shuffle_placebo | dateblock | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000206419 | -0.000078158 | 1.000000000 | -0.003069609 |
| submission_e276_shuffle_subject_r3_49e900ba.csv | shuffle_placebo | subject | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000212273 | -0.000077702 | 1.000000000 | -0.000863338 |
| submission_e276_shuffle_subject_r4_d78fd988.csv | shuffle_placebo | subject | same_delta_shuffled | 12.000000000 | promote_candidate | -0.000143038 | -0.000055504 | 0.941176471 | 0.005920300 |
| submission_e276_shuffle_row_r4_69b8c9b0.csv | shuffle_placebo | row | same_delta_shuffled | 12.000000000 | too_small_to_submit | -0.000233625 | -0.000048071 | 0.970588235 | 0.005286037 |
| submission_e276_shuffle_subject_r1_86325907.csv | shuffle_placebo | subject | same_delta_shuffled | 12.000000000 | too_small_to_submit | -0.000120510 | -0.000029667 | 0.941176471 | 0.006490006 |

## Movement Anatomy

| basename | changed_cells_vs_current | changed_rows_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current |
| --- | --- | --- | --- | --- |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | 185 | 143 | 10.003742085 | 0.022473244 |
| submission_e276_shuffle_row_r3_c424f61b.csv | 185 | 146 | 9.951742085 | 0.021993108 |
| submission_e276_shuffle_dateblock_r4_620d6f89.csv | 185 | 150 | 9.951742085 | 0.021993576 |
| submission_e276_shuffle_dateblock_r1_17882307.csv | 185 | 149 | 9.951742085 | 0.021996419 |
| submission_e276_shuffle_subject_r3_49e900ba.csv | 185 | 147 | 9.951742085 | 0.021995395 |
| submission_e276_shuffle_row_r4_69b8c9b0.csv | 185 | 155 | 9.951742085 | 0.021978831 |
| submission_e276_shuffle_dateblock_r3_281b5e46.csv | 185 | 152 | 9.951742085 | 0.021993576 |
| submission_e276_shuffle_subject_r1_86325907.csv | 185 | 150 | 9.951742085 | 0.021932686 |
| submission_e276_shuffle_dateblock_r0_86ba3e14.csv | 185 | 147 | 9.951742085 | 0.021993576 |
| submission_e276_shuffle_subject_r2_c860bcea.csv | 185 | 156 | 9.951742085 | 0.021974698 |
| submission_e276_shuffle_subject_r4_d78fd988.csv | 185 | 152 | 9.951742085 | 0.021996445 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | 185 | 143 | 9.951742085 | 0.021974698 |
| submission_e276_shuffle_row_r0_4a3bd132.csv | 185 | 149 | 9.951742085 | 0.021992998 |
| submission_e276_shuffle_dateblock_r2_212ad15a.csv | 185 | 151 | 9.951742085 | 0.021994944 |
| submission_e276_shuffle_subject_r0_8c7d1ff6.csv | 185 | 151 | 9.951742085 | 0.021877003 |
| submission_e276_shuffle_row_r2_baca8ed7.csv | 185 | 154 | 9.951742085 | 0.021996445 |
| submission_e276_shuffle_row_r1_ac0d437e.csv | 185 | 154 | 9.951742085 | 0.021984675 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | 179 | 137 | 9.557615764 | 0.022473244 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | 177 | 135 | 9.510915524 | 0.022473244 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | 173 | 135 | 9.457488995 | 0.021043811 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | 173 | 131 | 9.238506658 | 0.022253052 |
| submission_e276_no_media_game_m160_72fc6fa6.csv | 162 | 129 | 8.714772476 | 0.022473244 |
| submission_e276_inverse_primary_m080_4574c953.csv | 185 | 143 | 7.961393668 | 0.017597019 |
| submission_e276_no_diary_global_m160_d8951434.csv | 148 | 115 | 7.805938129 | 0.022473244 |
| submission_e276_no_mobility_context_m160_68587259.csv | 142 | 131 | 7.559819848 | 0.022473244 |
| submission_e276_q3_only_m160_6034ca83.csv | 114 | 114 | 5.929100380 | 0.022473244 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | 117 | 106 | 5.883035090 | 0.022253052 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | 105 | 81 | 5.664925113 | 0.021014924 |
| submission_e276_q12_only_m160_7bcd965c.csv | 71 | 63 | 4.074641705 | 0.021043811 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | 67 | 43 | 3.867856146 | 0.021014924 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | 62 | 60 | 3.369958922 | 0.021014924 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | 24 | 24 | 1.370378267 | 0.016824145 |
| submission_e276_only_media_game_m160_8f065696.csv | 24 | 24 | 1.325763338 | 0.017461298 |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | 24 | 24 | 1.227556327 | 0.016616026 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | 24 | 24 | 1.099197950 | 0.015833328 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | 24 | 24 | 0.735312250 | 0.011538811 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0 | 0 | 0.000000000 | 0.000000000 |

## Decision

- At least one shuffled placebo passes the strict gate. E275 must be demoted until the selector is made less magnitude-sensitive.
- The original E275 primary remains strict-promoted under the same audit.
- Best surviving semantic variant is `submission_e276_no_media_game_m160_72fc6fa6.csv`; its family/kind is `media_game` / `leave_one_out`.

## Interpretation Rules

- If shuffled placebos pass: treat E275 as a selector artifact, not a lifestyle-state candidate.
- If only Q3/JEPA/mobility variants pass: the useful hidden state is narrower than the broad q-sleep story.
- If leave-one-family variants pass but only-family variants do not: the representation is a composite lifestyle state and should be gated, not simplified.
- If inverse control passes: the direction is not identifiable and the candidate should be rejected.

## Files

- `e276_q_sleep_story_ablation_placebo_scores.csv`
- `e276_q_sleep_story_ablation_placebo_anatomy.csv`
- `e276_q_sleep_story_ablation_placebo_variants.csv`
- `e276_q_sleep_story_ablation_placebo_nulls.csv`
- `e276_q_sleep_story_ablation_placebo_axis_summary.csv`
