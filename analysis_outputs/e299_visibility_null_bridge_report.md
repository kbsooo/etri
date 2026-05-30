# E299 Visibility/Null Bridge Scan

Public LB는 사용하지 않았다. E298 near-miss 후보를 logit-space로 미세 rescale하고 matched null governor를 다시 적용했다.

## Counts

- base rows: `14`
- generated candidates: `102`
- old strict prefilter candidates: `81`
- null-evaluated candidates: `71`
- public-free ready candidates: `0`

## Lane Summary

| bridge_lane | n | ready | old_strict | min_null_strict_rate | best_actual_p90 | best_actual_mean | best_p90_dominance | best_mean_dominance | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| null_rare_edge_near | 12 | 0 | 2 | 0.000000000 | -0.000066403 | -0.000197755 | 0.904761905 | 0.761904762 | 0.857142857 |
| visible_common_scale_down | 45 | 0 | 45 | 0.952380952 | -0.000557161 | -0.001267168 | 1.000000000 | 0.857142857 | 1.000000000 |
| visible_low_null_near | 14 | 0 | 3 | 0.000000000 | -0.000052025 | -0.000191663 | 1.000000000 | 0.666666667 | 1.000000000 |

## Best Governor Rows

| bridge_lane | source_experiment | source_target | source_family | multiplier | old_strict_promote | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | public_free_submission_ready | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| visible_low_null_near | e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lowmax35_bf70 | 0.970000000 | True | -0.000050918 | 0.095238095 | 0.952380952 | 0.476190476 | 0.857142857 | False | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv |
| visible_low_null_near | e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_dateblock_cv_contrast_half_bf70 | 0.990000000 | True | -0.000050909 | 0.190476190 | 0.857142857 | 0.428571429 | 0.714285714 | False | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p990_9a53d270.csv |
| visible_low_null_near | e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lowmax35_bf70 | 0.990000000 | True | -0.000052025 | 0.238095238 | 1.000000000 | 0.428571429 | 1.000000000 | False | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p990_df233e89.csv |
| null_rare_edge_near | e297 | S1 | routine_fragmentation | 1.200000000 | True | -0.000059832 | 0.428571429 | 0.904761905 | 0.761904762 | 0.857142857 | False | submission_e299_bridge_null_rare_edge_near_e297_epstate_routine_fragmentation_S1_raw_human_context_date_m1p200_e02cc4bc.csv |
| null_rare_edge_near | e297 | S1 | routine_fragmentation | 1.300000000 | True | -0.000066403 | 0.571428571 | 0.761904762 | 0.714285714 | 0.571428571 | False | submission_e299_bridge_null_rare_edge_near_e297_epstate_routine_fragmentation_S1_raw_human_context_date_m1p300_023271ed.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.990000000 | True | -0.000517132 | 0.952380952 | 0.857142857 | 0.190476190 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p990_d717b4f8.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.920000000 | True | -0.000277644 | 0.952380952 | 0.714285714 | 0.190476190 | 0.428571429 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p920_24b11ed6.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.990000000 | True | -0.000557161 | 1.000000000 | 0.857142857 | 0.714285714 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p990_9c74921f.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.970000000 | True | -0.000540561 | 1.000000000 | 0.952380952 | 0.761904762 | 0.857142857 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p970_882116d4.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.970000000 | True | -0.000500645 | 1.000000000 | 0.857142857 | 0.285714286 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p970_73623e56.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.920000000 | True | -0.000499536 | 1.000000000 | 1.000000000 | 0.714285714 | 1.000000000 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p920_3fe20b68.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.920000000 | True | -0.000460206 | 1.000000000 | 0.857142857 | 0.380952381 | 0.857142857 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p920_5be1d0b2.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.850000000 | True | -0.000442751 | 1.000000000 | 0.761904762 | 0.761904762 | 0.428571429 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p850_17ab72f3.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.850000000 | True | -0.000405562 | 1.000000000 | 0.666666667 | 0.285714286 | 0.571428571 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p850_010deaff.csv |
| visible_common_scale_down | e289 | Q3 | family_jepa_context | 0.990000000 | True | -0.000394691 | 1.000000000 | 0.904761905 | 0.666666667 | 0.857142857 | False | submission_e299_bridge_visible_common_scale_down_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_ce_m0p990_5c9d13c8.csv |
| visible_common_scale_down | e289 | Q3 | family_jepa_context | 0.970000000 | True | -0.000386716 | 1.000000000 | 0.904761905 | 0.523809524 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_ce_m0p970_2c5bd47f.csv |
| visible_common_scale_down | e289 | Q3 | family_jepa_context | 0.920000000 | True | -0.000366013 | 1.000000000 | 0.761904762 | 0.523809524 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_ce_m0p920_b1731380.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.750000000 | True | -0.000365049 | 1.000000000 | 0.857142857 | 0.761904762 | 0.571428571 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p750_84828960.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.990000000 | True | -0.000346941 | 1.000000000 | 0.857142857 | 0.809523810 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p990_596a83ce.csv |
| visible_common_scale_down | e289 | Q3 | family_jepa_context | 0.850000000 | True | -0.000336935 | 1.000000000 | 0.809523810 | 0.714285714 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_ce_m0p850_a13970d7.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.970000000 | True | -0.000336045 | 1.000000000 | 0.857142857 | 0.571428571 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p970_26ef4510.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.750000000 | True | -0.000330838 | 1.000000000 | 0.857142857 | 0.476190476 | 0.857142857 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p750_a24fc906.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.990000000 | True | -0.000313584 | 1.000000000 | 0.904761905 | 0.428571429 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p990_3fb9678e.csv |
| visible_common_scale_down | e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv | 0.990000000 | True | -0.000311015 | 1.000000000 | 0.904761905 | 0.476190476 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e291_lifeblock_Q3_family_jepa_context_dateblock5_pc_su_m0p990_a8cca6ed.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.920000000 | True | -0.000309265 | 1.000000000 | 0.857142857 | 0.619047619 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p920_526afab3.csv |
| visible_common_scale_down | e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv | 0.970000000 | True | -0.000304740 | 1.000000000 | 0.857142857 | 0.476190476 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e291_lifeblock_Q3_family_jepa_context_dateblock5_pc_su_m0p970_3fafcb06.csv |
| visible_common_scale_down | e297 | S1 | bedtime_arousal | 0.970000000 | True | -0.000303169 | 1.000000000 | 0.857142857 | 0.285714286 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_bedtime_arousal_S1_raw_human_context_date_m0p970_233cbf2b.csv |
| visible_common_scale_down | e289 | Q3 | family_jepa_context | 0.750000000 | True | -0.000294126 | 1.000000000 | 0.761904762 | 0.809523810 | 0.571428571 | False | submission_e299_bridge_visible_common_scale_down_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_ce_m0p750_8e976eb1.csv |
| visible_common_scale_down | e297 | S1 | routine_fragmentation | 0.650000000 | True | -0.000291652 | 1.000000000 | 0.952380952 | 0.857142857 | 0.857142857 | False | submission_e299_bridge_visible_common_scale_down_e297_epstate_routine_fragmentation_S1_raw_human_contex_m0p650_0cd8c25a.csv |
| visible_common_scale_down | e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv | 0.920000000 | True | -0.000289051 | 1.000000000 | 0.857142857 | 0.285714286 | 0.714285714 | False | submission_e299_bridge_visible_common_scale_down_e291_lifeblock_Q3_family_jepa_context_dateblock5_pc_su_m0p920_aa734ff1.csv |

## Interpretation

- No rescaled near-miss crossed `selector-visible + null-rare`.
- The E298 gap is not just a coarse amplitude-grid artifact for the tested near-miss families.
- Next work should change placement geometry or train the action outcome target, not run another scale sweep.

## Outputs

- `analysis_outputs/e299_visibility_null_bridge_candidates.csv`
- `analysis_outputs/e299_visibility_null_bridge_prefilter.csv`
- `analysis_outputs/e299_visibility_null_bridge_governor.csv`
- `analysis_outputs/e299_visibility_null_bridge_report.md`
