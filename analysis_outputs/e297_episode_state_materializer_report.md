# E297 Episode-State Materializer

## Question

Can the strict E296 human episode-target states be translated into current-best E247 edits that survive the public-free governor?

## Prefilter

- generated candidates: `150`
- old strict candidates: `25`
- null-evaluated candidates: `39`

| basename | episode | target | rule | scale | nonzero_rows | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_promote_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s030_f8fc2700.csv | routine_fragmentation | S1 | all_centered | 0.300000 | 250 | promote_candidate | -0.001284 | -0.000565 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s030_11e075f1.csv | bedtime_arousal | S1 | all_centered | 0.300000 | 250 | promote_candidate | -0.000924 | -0.000525 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s022_7c891264.csv | routine_fragmentation | S1 | all_centered | 0.220000 | 250 | promote_candidate | -0.000838 | -0.000352 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s030_e87583ab.csv | routine_fragmentation | S1 | topabs64 | 0.300000 | 64 | promote_candidate | -0.000966 | -0.000337 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s030_8582e4d0.csv | bedtime_arousal | S1 | topabs64 | 0.300000 | 64 | promote_candidate | -0.000700 | -0.000323 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s022_bfbce9d1.csv | bedtime_arousal | S1 | all_centered | 0.220000 | 250 | promote_candidate | -0.000568 | -0.000319 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s022_9f144823.csv | routine_fragmentation | S1 | topabs64 | 0.220000 | 64 | promote_candidate | -0.000658 | -0.000216 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s030_eb7092a0.csv | routine_fragmentation | S1 | topabs32 | 0.300000 | 32 | promote_candidate | -0.000599 | -0.000209 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s022_c26dbc46.csv | bedtime_arousal | S1 | topabs64 | 0.220000 | 64 | promote_candidate | -0.000454 | -0.000202 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s015_355ad200.csv | routine_fragmentation | S1 | all_centered | 0.150000 | 250 | promote_candidate | -0.000486 | -0.000190 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s030_729cd76d.csv | bedtime_arousal | S1 | topabs32 | 0.300000 | 32 | promote_candidate | -0.000614 | -0.000181 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s015_a272d5c7.csv | bedtime_arousal | S1 | all_centered | 0.150000 | 250 | promote_candidate | -0.000302 | -0.000166 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s022_cc86ffb5.csv | routine_fragmentation | S1 | topabs32 | 0.220000 | 32 | promote_candidate | -0.000412 | -0.000136 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s022_4f3299d1.csv | bedtime_arousal | S1 | topabs32 | 0.220000 | 32 | promote_candidate | -0.000424 | -0.000117 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s030_e97c2622.csv | routine_fragmentation | S1 | topabs16 | 0.300000 | 16 | promote_candidate | -0.000379 | -0.000117 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s015_396a220c.csv | routine_fragmentation | S1 | topabs64 | 0.150000 | 64 | promote_candidate | -0.000388 | -0.000111 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s015_3828136b.csv | bedtime_arousal | S1 | topabs64 | 0.150000 | 64 | promote_candidate | -0.000245 | -0.000100 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s010_c5e3baaf.csv | routine_fragmentation | S1 | all_centered | 0.100000 | 250 | promote_candidate | -0.000273 | -0.000096 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s010_98acd6c1.csv | bedtime_arousal | S1 | all_centered | 0.100000 | 250 | promote_candidate | -0.000155 | -0.000083 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_pos_top24_s030_7c09f232.csv | bedtime_arousal | S1 | pos_top24 | 0.300000 | 24 | promote_candidate | -0.000707 | -0.000081 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s022_7518d5e2.csv | routine_fragmentation | S1 | topabs16 | 0.220000 | 16 | promote_candidate | -0.000268 | -0.000079 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs16_s030_934aed66.csv | bedtime_arousal | S1 | topabs16 | 0.300000 | 16 | promote_candidate | -0.000478 | -0.000078 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_pos_top24_s030_18aadc84.csv | routine_fragmentation | S1 | pos_top24 | 0.300000 | 24 | promote_candidate | -0.000802 | -0.000076 | True |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s015_72380d40.csv | routine_fragmentation | S1 | topabs32 | 0.150000 | 32 | promote_candidate | -0.000248 | -0.000073 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s015_2cf0f75d.csv | bedtime_arousal | S1 | topabs32 | 0.150000 | 32 | promote_candidate | -0.000257 | -0.000061 | True |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs16_s022_b2d40003.csv | bedtime_arousal | S1 | topabs16 | 0.220000 | 16 | too_small_to_submit | -0.000337 | -0.000049 | False |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s010_ab243cb1.csv | routine_fragmentation | S1 | topabs64 | 0.100000 | 64 | too_small_to_submit | -0.000215 | -0.000049 | False |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s006_7e48318e.csv | routine_fragmentation | S1 | all_centered | 0.060000 | 250 | too_small_to_submit | -0.000149 | -0.000049 | False |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_pos_top24_s022_c9c485f8.csv | bedtime_arousal | S1 | pos_top24 | 0.220000 | 24 | too_small_to_submit | -0.000499 | -0.000047 | False |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s015_c61fbdcd.csv | routine_fragmentation | S1 | topabs16 | 0.150000 | 16 | too_small_to_submit | -0.000170 | -0.000047 | False |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_pos_top24_s022_c71d82f4.csv | routine_fragmentation | S1 | pos_top24 | 0.220000 | 24 | too_small_to_submit | -0.000571 | -0.000045 | False |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s010_44b82f59.csv | bedtime_arousal | S1 | topabs64 | 0.100000 | 64 | too_small_to_submit | -0.000125 | -0.000045 | False |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s006_f675ca42.csv | bedtime_arousal | S1 | all_centered | 0.060000 | 250 | too_small_to_submit | -0.000080 | -0.000042 | False |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s010_09ae5fdf.csv | routine_fragmentation | S1 | topabs32 | 0.100000 | 32 | too_small_to_submit | -0.000136 | -0.000031 | False |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs16_s015_b28f243d.csv | bedtime_arousal | S1 | topabs16 | 0.150000 | 16 | too_small_to_submit | -0.000214 | -0.000024 | False |

## Matched Null Governor

- public-free ready candidates: `0`

| basename | episode | target | rule | scale | nonzero_rows | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s010_98acd6c1.csv | bedtime_arousal | S1 | all_centered | 0.100000 | 250 | promote_candidate | -0.000155 | -0.000083 | 0.714286 | 0.857143 | 0.571429 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s030_f8fc2700.csv | routine_fragmentation | S1 | all_centered | 0.300000 | 250 | promote_candidate | -0.001284 | -0.000565 | 0.904762 | 0.904762 | 0.666667 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s010_c5e3baaf.csv | routine_fragmentation | S1 | all_centered | 0.100000 | 250 | promote_candidate | -0.000273 | -0.000096 | 0.904762 | 0.904762 | 0.809524 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s022_7c891264.csv | routine_fragmentation | S1 | all_centered | 0.220000 | 250 | promote_candidate | -0.000838 | -0.000352 | 0.952381 | 0.904762 | 0.857143 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s022_9f144823.csv | routine_fragmentation | S1 | topabs64 | 0.220000 | 64 | promote_candidate | -0.000658 | -0.000216 | 0.952381 | 0.857143 | 0.666667 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s015_3828136b.csv | bedtime_arousal | S1 | topabs64 | 0.150000 | 64 | promote_candidate | -0.000245 | -0.000100 | 0.952381 | 0.761905 | 0.380952 | 0.571429 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_pos_top24_s030_7c09f232.csv | bedtime_arousal | S1 | pos_top24 | 0.300000 | 24 | promote_candidate | -0.000707 | -0.000081 | 0.952381 | 0.809524 | 0.238095 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s030_11e075f1.csv | bedtime_arousal | S1 | all_centered | 0.300000 | 250 | promote_candidate | -0.000924 | -0.000525 | 1.000000 | 0.904762 | 0.238095 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s030_e87583ab.csv | routine_fragmentation | S1 | topabs64 | 0.300000 | 64 | promote_candidate | -0.000966 | -0.000337 | 1.000000 | 0.380952 | 0.333333 | 0.285714 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s030_8582e4d0.csv | bedtime_arousal | S1 | topabs64 | 0.300000 | 64 | promote_candidate | -0.000700 | -0.000323 | 1.000000 | 0.666667 | 0.047619 | 0.571429 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s022_bfbce9d1.csv | bedtime_arousal | S1 | all_centered | 0.220000 | 250 | promote_candidate | -0.000568 | -0.000319 | 1.000000 | 0.904762 | 0.333333 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s030_eb7092a0.csv | routine_fragmentation | S1 | topabs32 | 0.300000 | 32 | promote_candidate | -0.000599 | -0.000209 | 1.000000 | 0.619048 | 0.428571 | 0.428571 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s022_c26dbc46.csv | bedtime_arousal | S1 | topabs64 | 0.220000 | 64 | promote_candidate | -0.000454 | -0.000202 | 1.000000 | 0.904762 | 0.142857 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s015_355ad200.csv | routine_fragmentation | S1 | all_centered | 0.150000 | 250 | promote_candidate | -0.000486 | -0.000190 | 1.000000 | 0.809524 | 0.619048 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s030_729cd76d.csv | bedtime_arousal | S1 | topabs32 | 0.300000 | 32 | promote_candidate | -0.000614 | -0.000181 | 1.000000 | 0.619048 | 0.380952 | 0.571429 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s015_a272d5c7.csv | bedtime_arousal | S1 | all_centered | 0.150000 | 250 | promote_candidate | -0.000302 | -0.000166 | 1.000000 | 0.761905 | 0.476190 | 0.571429 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s022_cc86ffb5.csv | routine_fragmentation | S1 | topabs32 | 0.220000 | 32 | promote_candidate | -0.000412 | -0.000136 | 1.000000 | 0.666667 | 0.476190 | 0.285714 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s022_4f3299d1.csv | bedtime_arousal | S1 | topabs32 | 0.220000 | 32 | promote_candidate | -0.000424 | -0.000117 | 1.000000 | 0.904762 | 0.523810 | 0.857143 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s030_e97c2622.csv | routine_fragmentation | S1 | topabs16 | 0.300000 | 16 | promote_candidate | -0.000379 | -0.000117 | 1.000000 | 0.857143 | 0.476190 | 0.714286 | blocked_by_matched_nulls |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s015_396a220c.csv | routine_fragmentation | S1 | topabs64 | 0.150000 | 64 | promote_candidate | -0.000388 | -0.000111 | 1.000000 | 0.666667 | 0.428571 | 0.571429 | blocked_by_matched_nulls |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_all_centered_s006_f675ca42.csv | bedtime_arousal | S1 | all_centered | 0.060000 | 250 | too_small_to_submit | -0.000080 | -0.000042 | 0.000000 | 0.904762 | 0.333333 | 0.714286 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs16_s015_b28f243d.csv | bedtime_arousal | S1 | topabs16 | 0.150000 | 16 | too_small_to_submit | -0.000214 | -0.000024 | 0.000000 | 0.666667 | 0.333333 | 0.428571 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s010_6c226d0a.csv | routine_fragmentation | S1 | topabs16 | 0.100000 | 16 | too_small_to_submit | -0.000100 | -0.000023 | 0.000000 | 0.904762 | 0.523810 | 0.857143 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs32_s010_0dc79909.csv | bedtime_arousal | S1 | topabs32 | 0.100000 | 32 | too_small_to_submit | -0.000141 | -0.000023 | 0.000000 | 0.714286 | 0.523810 | 0.571429 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s006_55330ee9.csv | routine_fragmentation | S1 | topabs64 | 0.060000 | 64 | too_small_to_submit | -0.000115 | -0.000021 | 0.000000 | 0.857143 | 0.761905 | 0.714286 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S3_hybrid_context_subject5_pos_top24_s006_717bec6d.csv | routine_fragmentation | S3 | pos_top24 | 0.060000 | 24 | too_small_to_submit | -0.000020 | 0.000001 | 0.000000 | 0.523810 | 0.809524 | 0.285714 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S3_hybrid_context_subject5_pos_top24_s010_05503413.csv | routine_fragmentation | S3 | pos_top24 | 0.100000 | 24 | too_small_to_submit | -0.000033 | 0.000001 | 0.000000 | 0.380952 | 0.857143 | 0.285714 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S3_hybrid_context_subject5_pos_top24_s006_b3ceebc6.csv | bedtime_arousal | S3 | pos_top24 | 0.060000 | 24 | too_small_to_submit | -0.000025 | 0.000003 | 0.000000 | 0.190476 | 0.904762 | 0.000000 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S3_hybrid_context_subject5_pos_top24_s010_7f580fc6.csv | bedtime_arousal | S3 | pos_top24 | 0.100000 | 24 | too_small_to_submit | -0.000042 | 0.000004 | 0.000000 | 0.000000 | 0.904762 | 0.000000 | too_small_to_submit |
| submission_e297_epstate_routine_anchor_recovery_S2_family_jepa_context_subject5_neg_top24_s006_06cd9f8c.csv | routine_anchor_recovery | S2 | neg_top24 | 0.060000 | 24 | too_small_to_submit | -0.000048 | 0.000006 | 0.000000 | 0.809524 | 0.619048 | 0.571429 | too_small_to_submit |
| submission_e297_epstate_routine_anchor_recovery_S2_family_jepa_context_subject5_neg_top24_s010_f4592f4b.csv | routine_anchor_recovery | S2 | neg_top24 | 0.100000 | 24 | too_small_to_submit | -0.000073 | 0.000017 | 0.000000 | 0.476190 | 0.333333 | 0.428571 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_pos_top24_s022_c9c485f8.csv | bedtime_arousal | S1 | pos_top24 | 0.220000 | 24 | too_small_to_submit | -0.000499 | -0.000047 | 0.047619 | 0.904762 | 0.476190 | 0.714286 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs32_s010_09ae5fdf.csv | routine_fragmentation | S1 | topabs32 | 0.100000 | 32 | too_small_to_submit | -0.000136 | -0.000031 | 0.047619 | 0.571429 | 0.428571 | 0.571429 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s006_7e48318e.csv | routine_fragmentation | S1 | all_centered | 0.060000 | 250 | too_small_to_submit | -0.000149 | -0.000049 | 0.095238 | 0.904762 | 0.809524 | 0.714286 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s015_c61fbdcd.csv | routine_fragmentation | S1 | topabs16 | 0.150000 | 16 | too_small_to_submit | -0.000170 | -0.000047 | 0.095238 | 0.857143 | 0.666667 | 0.857143 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_pos_top24_s022_c71d82f4.csv | routine_fragmentation | S1 | pos_top24 | 0.220000 | 24 | too_small_to_submit | -0.000571 | -0.000045 | 0.095238 | 0.714286 | 0.619048 | 0.571429 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs64_s010_44b82f59.csv | bedtime_arousal | S1 | topabs64 | 0.100000 | 64 | too_small_to_submit | -0.000125 | -0.000045 | 0.095238 | 0.761905 | 0.523810 | 0.714286 | too_small_to_submit |
| submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s010_ab243cb1.csv | routine_fragmentation | S1 | topabs64 | 0.100000 | 64 | too_small_to_submit | -0.000215 | -0.000049 | 0.285714 | 0.666667 | 0.619048 | 0.571429 | too_small_to_submit |
| submission_e297_epstate_bedtime_arousal_S1_raw_human_context_dateblock5_topabs16_s022_b2d40003.csv | bedtime_arousal | S1 | topabs16 | 0.220000 | 16 | too_small_to_submit | -0.000337 | -0.000049 | 0.333333 | 0.571429 | 0.428571 | 0.428571 | too_small_to_submit |

## Decision

No E297 materialization is public-free ready. The episode states are real local label signals, but this translator does not yet make a placebo-resistant E247 edit.

## Interpretation

This is the first strict bridge from human/social episode theory to current-submission action in this branch. A fail does not kill the bedtime/routine state; it says the current logistic delta translator is too crude or too selector-visible compared with matched null placements.

## Files

- `e297_episode_state_materializer_candidates.csv`
- `e297_episode_state_materializer_selected.csv`
- `e297_episode_state_materializer_governor.csv`
- `e297_episode_state_materializer_scores.csv`
- `e297_episode_state_materializer_null_map.csv`
