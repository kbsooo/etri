# E277 Placebo-Resistant Q-Sleep Gate

## Question

Can any E275/E276 q-sleep diary-energy candidate beat a matched null distribution that preserves its movement magnitude but destroys row/state alignment?

## Promotion Rule

A candidate must pass the old strict gate and also beat its own row/subject/dateblock shuffle nulls:

- p90 dominance over all nulls >= `0.80`;
- mean dominance over all nulls >= `0.70`;
- worst per-mode p90 dominance >= `0.60`;
- null strict-promote rate <= `0.20`;
- actual p90 at least `1e-6` better than null p90 q20;
- inverse controls cannot promote.

## Summary

- semantic/control candidates tested: `21`
- matched null files generated: `441`
- selected E272-style selector models: `1`
- old strict-promote candidates: `10`
- old strict candidates blocked by placebo-promote rate: `10`
- E277 placebo-resistant promotes: `0`

## Candidate Results

| basename | variant_type | family_tested | axis_kind_tested | old_promotion_decision | e277_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | placebo_adjusted_p90_vs_median | placebo_adjusted_p90_vs_best |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | axis_ablation | routine_calendar | only | below_selector_resolution | below_selector_resolution | 0.000004124 | 0.000028507 | 0.000000000 | 0.857142857 | 0.714285714 | -0.000001737 | 0.000001419 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | axis_ablation | all | jepa_only | promote_candidate | blocked_by_placebo_promotes | -0.000133692 | -0.000093390 | 0.904761905 | 0.761904762 | 0.714285714 | -0.000011330 | 0.000032121 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | axis_ablation | social_comm | only | below_selector_resolution | below_selector_resolution | 0.000020825 | 0.000036001 | 0.000000000 | 0.714285714 | 0.571428571 | -0.000001407 | 0.000007809 |
| submission_e276_no_media_game_m160_72fc6fa6.csv | axis_ablation | media_game | leave_one_out | promote_candidate | blocked_by_placebo_promotes | -0.000229075 | -0.000129314 | 0.904761905 | 0.666666667 | 0.428571429 | -0.000004104 | 0.000038349 |
| submission_e276_q3_only_m160_6034ca83.csv | axis_ablation | q3_only | all | promote_candidate | blocked_by_placebo_promotes | -0.000118807 | -0.000057680 | 0.904761905 | 0.619047619 | 0.142857143 | -0.000000403 | 0.000017597 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | primary | all | all | promote_candidate | blocked_by_placebo_promotes | -0.000190473 | -0.000084726 | 0.952380952 | 0.571428571 | 0.285714286 | -0.000000953 | 0.000031367 |
| submission_e276_q12_only_m160_7bcd965c.csv | axis_ablation | q12_only | all | too_small_to_submit | too_small_to_submit | -0.000069206 | 0.000004534 | 0.000000000 | 0.523809524 | 0.000000000 | -0.000001368 | 0.000029334 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | axis_ablation | mobility_context | only | promote_candidate | blocked_by_placebo_promotes | -0.000130580 | -0.000095305 | 0.904761905 | 0.476190476 | 0.142857143 | 0.000004319 | 0.000045735 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | axis_ablation | cognitive_money | leave_one_out | promote_candidate | blocked_by_placebo_promotes | -0.000194311 | -0.000086281 | 0.952380952 | 0.476190476 | 0.142857143 | 0.000000588 | 0.000040122 |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | axis_ablation | all | all | promote_candidate | blocked_by_placebo_promotes | -0.000188014 | -0.000082769 | 0.904761905 | 0.476190476 | 0.285714286 | 0.000003976 | 0.000033915 |
| submission_e276_inverse_primary_m080_4574c953.csv | inverse_control | all | inverse | below_selector_resolution | below_selector_resolution | 0.000110348 | 0.000207722 | 0.000000000 | 0.476190476 | 0.285714286 | 0.000000322 | 0.000012008 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | axis_ablation | social_comm | leave_one_out | promote_candidate | blocked_by_placebo_promotes | -0.000186941 | -0.000092156 | 0.857142857 | 0.380952381 | 0.142857143 | 0.000009924 | 0.000046160 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | axis_ablation | routine_calendar | leave_one_out | promote_candidate | blocked_by_placebo_promotes | -0.000167479 | -0.000072275 | 0.952380952 | 0.380952381 | 0.285714286 | 0.000010124 | 0.000035326 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | axis_ablation | cognitive_money | only | below_selector_resolution | below_selector_resolution | 0.000070131 | 0.000090007 | 0.000000000 | 0.380952381 | 0.142857143 | 0.000011225 | 0.000045727 |
| submission_e276_no_diary_global_m160_d8951434.csv | axis_ablation | diary_global | leave_one_out | promote_candidate | blocked_by_placebo_promotes | -0.000125204 | -0.000050408 | 0.666666667 | 0.333333333 | 0.142857143 | 0.000009120 | 0.000045508 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | axis_ablation | bedtime_phone | leave_one_out | too_small_to_submit | too_small_to_submit | -0.000134969 | -0.000040128 | 0.476190476 | 0.285714286 | 0.000000000 | 0.000008751 | 0.000043003 |
| submission_e276_no_mobility_context_m160_68587259.csv | axis_ablation | mobility_context | leave_one_out | below_selector_resolution | below_selector_resolution | 0.000103989 | 0.000148352 | 0.000000000 | 0.238095238 | 0.000000000 | 0.000021558 | 0.000054366 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | axis_ablation | bedtime_phone | only | below_selector_resolution | below_selector_resolution | 0.000063463 | 0.000083706 | 0.000000000 | 0.142857143 | 0.000000000 | 0.000027300 | 0.000047999 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | axis_ablation | diary_global | only | block_or_reject | block_or_reject | 0.000094796 | 0.000118033 | 0.000000000 | 0.142857143 | 0.000000000 | 0.000031174 | 0.000054267 |
| submission_e276_only_media_game_m160_8f065696.csv | axis_ablation | media_game | only | below_selector_resolution | below_selector_resolution | 0.000042889 | 0.000076317 | 0.000000000 | 0.047619048 | 0.000000000 | 0.000014142 | 0.000028440 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | axis_ablation | all | nonjepa_only | block_or_reject | block_or_reject | 0.000129312 | 0.000183796 | 0.000000000 | 0.047619048 | 0.000000000 | 0.000055218 | 0.000080462 |

## Null Mode Stress

| source_basename | mode | nulls | strict_rate | best_p90 | median_p90 | mean_p90 |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e276_no_media_game_m160_72fc6fa6.csv | row | 7 | 1.000000000 | -0.000167663 | -0.000128344 | -0.000128888 |
| submission_e276_no_media_game_m160_72fc6fa6.csv | dateblock | 7 | 1.000000000 | -0.000143449 | -0.000129677 | -0.000125629 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | subject | 7 | 1.000000000 | -0.000141040 | -0.000099624 | -0.000100248 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | dateblock | 7 | 1.000000000 | -0.000135983 | -0.000109448 | -0.000113430 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | dateblock | 7 | 1.000000000 | -0.000128442 | -0.000106093 | -0.000107454 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | dateblock | 7 | 1.000000000 | -0.000126404 | -0.000100608 | -0.000100082 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | dateblock | 7 | 1.000000000 | -0.000125512 | -0.000088987 | -0.000090824 |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | dateblock | 7 | 1.000000000 | -0.000116684 | -0.000092434 | -0.000093599 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | dateblock | 7 | 1.000000000 | -0.000116093 | -0.000105036 | -0.000102923 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | row | 7 | 1.000000000 | -0.000115341 | -0.000070745 | -0.000080978 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | subject | 7 | 1.000000000 | -0.000107844 | -0.000091083 | -0.000088122 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | row | 7 | 1.000000000 | -0.000103876 | -0.000071296 | -0.000076630 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | subject | 7 | 1.000000000 | -0.000102839 | -0.000082346 | -0.000081361 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | dateblock | 7 | 1.000000000 | -0.000096497 | -0.000092400 | -0.000081918 |
| submission_e276_q3_only_m160_6034ca83.csv | row | 7 | 1.000000000 | -0.000075277 | -0.000061138 | -0.000063366 |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | row | 7 | 0.857142857 | -0.000113860 | -0.000079484 | -0.000084270 |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | subject | 7 | 0.857142857 | -0.000107601 | -0.000097051 | -0.000083736 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | subject | 7 | 0.857142857 | -0.000107004 | -0.000085093 | -0.000082418 |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | subject | 7 | 0.857142857 | -0.000105095 | -0.000079033 | -0.000077673 |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | row | 7 | 0.857142857 | -0.000099454 | -0.000081759 | -0.000080109 |
| submission_e276_no_diary_global_m160_d8951434.csv | subject | 7 | 0.857142857 | -0.000095916 | -0.000070523 | -0.000064122 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | subject | 7 | 0.857142857 | -0.000090586 | -0.000075771 | -0.000073401 |
| submission_e276_no_diary_global_m160_d8951434.csv | dateblock | 7 | 0.857142857 | -0.000087560 | -0.000070680 | -0.000069534 |
| submission_e276_q3_only_m160_6034ca83.csv | dateblock | 7 | 0.857142857 | -0.000059100 | -0.000055794 | -0.000055068 |
| submission_e276_q3_only_m160_6034ca83.csv | subject | 7 | 0.857142857 | -0.000057887 | -0.000055648 | -0.000054936 |
| submission_e276_no_social_comm_m160_cea48ae0.csv | row | 7 | 0.714285714 | -0.000138315 | -0.000103026 | -0.000086459 |
| submission_e276_no_media_game_m160_72fc6fa6.csv | subject | 7 | 0.714285714 | -0.000125855 | -0.000112868 | -0.000106039 |
| submission_e276_only_mobility_context_m160_6ac81269.csv | row | 7 | 0.714285714 | -0.000104771 | -0.000067864 | -0.000068908 |
| submission_e276_jepa_only_m160_75d0e9cf.csv | row | 7 | 0.714285714 | -0.000102954 | -0.000058439 | -0.000066321 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | subject | 7 | 0.571428571 | -0.000078093 | -0.000053287 | -0.000049033 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | dateblock | 7 | 0.428571429 | -0.000083131 | -0.000048879 | -0.000055880 |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | row | 7 | 0.428571429 | -0.000067135 | -0.000040348 | -0.000045175 |
| submission_e276_no_diary_global_m160_d8951434.csv | row | 7 | 0.285714286 | -0.000077833 | -0.000047439 | -0.000043621 |
| submission_e276_q12_only_m160_7bcd965c.csv | dateblock | 7 | 0.000000000 | -0.000024800 | -0.000012263 | -0.000011921 |
| submission_e276_q12_only_m160_7bcd965c.csv | row | 7 | 0.000000000 | -0.000021256 | 0.000031148 | 0.000027838 |
| submission_e276_q12_only_m160_7bcd965c.csv | subject | 7 | 0.000000000 | 0.000000292 | 0.000017368 | 0.000014652 |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | row | 7 | 0.000000000 | 0.000027088 | 0.000030244 | 0.000034626 |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | dateblock | 7 | 0.000000000 | 0.000027322 | 0.000028985 | 0.000030883 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | row | 7 | 0.000000000 | 0.000028192 | 0.000036990 | 0.000037377 |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | subject | 7 | 0.000000000 | 0.000029500 | 0.000032391 | 0.000034732 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | dateblock | 7 | 0.000000000 | 0.000033639 | 0.000037180 | 0.000036939 |
| submission_e276_only_social_comm_m160_22a09ec4.csv | subject | 7 | 0.000000000 | 0.000035130 | 0.000038214 | 0.000039272 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | row | 7 | 0.000000000 | 0.000035707 | 0.000039076 | 0.000040218 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | row | 7 | 0.000000000 | 0.000044279 | 0.000060044 | 0.000066888 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | dateblock | 7 | 0.000000000 | 0.000046054 | 0.000057087 | 0.000064886 |
| submission_e276_only_media_game_m160_8f065696.csv | row | 7 | 0.000000000 | 0.000047877 | 0.000061865 | 0.000059943 |
| submission_e276_only_media_game_m160_8f065696.csv | dateblock | 7 | 0.000000000 | 0.000049538 | 0.000064586 | 0.000062365 |
| submission_e276_only_media_game_m160_8f065696.csv | subject | 7 | 0.000000000 | 0.000049577 | 0.000059317 | 0.000061505 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | subject | 7 | 0.000000000 | 0.000054022 | 0.000094326 | 0.000089061 |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | subject | 7 | 0.000000000 | 0.000056251 | 0.000078411 | 0.000078897 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | dateblock | 7 | 0.000000000 | 0.000057758 | 0.000078781 | 0.000083221 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | row | 7 | 0.000000000 | 0.000063766 | 0.000085691 | 0.000080455 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | dateblock | 7 | 0.000000000 | 0.000078963 | 0.000084314 | 0.000086151 |
| submission_e276_no_mobility_context_m160_68587259.csv | row | 7 | 0.000000000 | 0.000093986 | 0.000112729 | 0.000111680 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | dateblock | 7 | 0.000000000 | 0.000103335 | 0.000127000 | 0.000128940 |
| submission_e276_only_diary_global_m160_6988f6a1.csv | subject | 7 | 0.000000000 | 0.000106639 | 0.000117512 | 0.000117478 |
| submission_e276_no_mobility_context_m160_68587259.csv | dateblock | 7 | 0.000000000 | 0.000108061 | 0.000126794 | 0.000126699 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | row | 7 | 0.000000000 | 0.000112085 | 0.000124391 | 0.000127754 |
| submission_e276_no_mobility_context_m160_68587259.csv | subject | 7 | 0.000000000 | 0.000113738 | 0.000158901 | 0.000158096 |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | subject | 7 | 0.000000000 | 0.000118632 | 0.000155866 | 0.000159889 |

## Movement Anatomy Of Actual Candidates

| basename | changed_cells_vs_current | changed_rows_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current |
| --- | --- | --- | --- | --- |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | 185 | 143 | 10.003742085 | 0.022473244 |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | 185 | 143 | 9.951742085 | 0.021974698 |
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

## Decision

No q-sleep semantic candidate beats matched placebos. E275/E276 remain diagnostic; do not submit from this branch yet.

## Next Action

Build a row-alignment objective, not another amplitude ladder: the real JEPA/mobility/Q3 candidate must be trained or gated to maximize distance from matched row/subject/dateblock shuffle nulls.

## Files

- `e277_placebo_resistant_qsleep_gate_summary.csv`
- `e277_placebo_resistant_qsleep_gate_scores.csv`
- `e277_placebo_resistant_qsleep_gate_nulls.csv`
- `e277_placebo_resistant_qsleep_gate_anatomy.csv`
