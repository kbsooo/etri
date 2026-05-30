# E302 S4 Placement-Health Decoder

Public LB는 사용하지 않았다. E301 actual/null placement 세계에서 S4 placement health가 human diary representation으로 예측되는지 검사했다.

## Question

E301의 실패가 단순한 S4 방향 문제가 아니라 subject/dateblock placement 문제라면, 좋은 placement는 raw human/social/day state aggregate에서 설명되어야 한다.

## Summary

| placement_mode | n | strict_rate | mean_median | mean_best | p90_median | p90_best |
| --- | --- | --- | --- | --- | --- | --- |
| actual | 1 | 1.000000 | -0.000161 | -0.000161 | -0.000051 | -0.000051 |
| dateblock | 64 | 0.406250 | -0.000164 | -0.000176 | -0.000049 | -0.000053 |
| row | 64 | 0.000000 | -0.000134 | -0.000184 | -0.000039 | -0.000049 |
| sign | 64 | 0.000000 | 0.000029 | -0.000063 | 0.000067 | -0.000016 |
| subject | 64 | 0.250000 | -0.000162 | -0.000179 | -0.000048 | -0.000053 |

## Leave-Mode-Out CV

| feature_set | mean_mae | mean_spearman | p90_mae | p90_spearman | strict_auc |
| --- | --- | --- | --- | --- | --- |
| human_all | 0.000051 | 0.400962 | 0.000048 | -0.090201 | 0.597838 |
| human_all_plus_topology | 0.000053 | 0.325973 | 0.000048 | -0.104041 | 0.601454 |
| story_episode | 0.000059 | 0.139057 | 0.000041 | -0.098443 | 0.629383 |
| topology | 0.000054 | 0.117502 | 0.000035 | 0.145879 | 0.570579 |

## Actual Candidate Predicted Rank

| feature_set | actual_mean | actual_p90 | actual_strict | mean_pred_full | p90_pred_full | strict_pred_full | actual_mean_pred_rank_pct | actual_p90_pred_rank_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| topology | -0.000161 | -0.000051 | True | -0.000162 | -0.000049 | 0.362273 | 0.250000 | 0.003906 |
| story_episode | -0.000161 | -0.000051 | True | -0.000137 | -0.000054 | 0.502203 | 0.585938 | 0.089844 |
| human_all | -0.000161 | -0.000051 | True | -0.000155 | -0.000080 | 0.356388 | 0.460938 | 0.000000 |
| human_all_plus_topology | -0.000161 | -0.000051 | True | -0.000156 | -0.000081 | 0.360901 | 0.433594 | 0.000000 |

Interpretation of rank columns: lower predicted mean/p90 is better. A high rank_pct means the model predicts the actual candidate as worse than many null placements.

## Best Actual Null Placements

| basename | placement_mode | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_bool |
| --- | --- | --- | --- | --- |
| submission_e301null_row_r055_57aba604.csv | row | -0.000184 | -0.000025 | False |
| submission_e301null_subject_r058_f796b5f6.csv | subject | -0.000179 | -0.000035 | False |
| submission_e301null_subject_r059_5c199803.csv | subject | -0.000177 | -0.000038 | False |
| submission_e301null_dateblock_r001_e3fc2086.csv | dateblock | -0.000176 | -0.000045 | False |
| submission_e301null_dateblock_r021_459de684.csv | dateblock | -0.000175 | -0.000045 | False |
| submission_e301null_subject_r018_5a158fd2.csv | subject | -0.000175 | -0.000051 | True |
| submission_e301null_subject_r014_3f516a9b.csv | subject | -0.000172 | -0.000047 | False |
| submission_e301null_dateblock_r044_78565928.csv | dateblock | -0.000171 | -0.000048 | False |
| submission_e301null_dateblock_r020_c1e49f05.csv | dateblock | -0.000171 | -0.000046 | False |
| submission_e301null_dateblock_r016_9a2fd3f5.csv | dateblock | -0.000171 | -0.000046 | False |
| submission_e301null_dateblock_r060_0f67ef35.csv | dateblock | -0.000170 | -0.000051 | True |
| submission_e301null_dateblock_r022_4b4f8b66.csv | dateblock | -0.000170 | -0.000051 | True |
| submission_e301null_subject_r025_b2052f01.csv | subject | -0.000170 | -0.000037 | False |
| submission_e301null_subject_r010_6fa8eed1.csv | subject | -0.000170 | -0.000051 | True |
| submission_e301null_subject_r057_3c6e0573.csv | subject | -0.000170 | -0.000044 | False |

## Features Associated With Better Mean Edge

| aggregate_feature | weight_for_lower_mean_is_negative | source | human_story |
| --- | --- | --- | --- |
| top__subject_signed_share_id07 | -0.000002 | topology | top  subject signed share id07 |
| human_signed__diary__bedtime_phone_pc2 | -0.000002 | diary | bedtime phone pc2 |
| human_pos_minus_neg__diary__subject_order | -0.000002 | diary | subject order |
| human_signed__diary__mobility_context_energy | -0.000002 | diary | mobility context energy |
| human_signed__story__night_out_mobility | -0.000001 | human_social | Late/deepnight movement, public ambience, weak charging. |
| human_signed__diary__jepa_prednorm_dateblock_sensor_measurement | -0.000001 | diary | JEPA residual/prednorm diary signal for measurement |
| human_signed__diary__jepa_resid_dateblock_physiology_activity | -0.000001 | diary | JEPA residual/prednorm diary signal for activity |
| human_signed__diary__jepa_prednorm_subject_sensor_measurement | -0.000001 | diary | JEPA residual/prednorm diary signal for measurement |
| human_signed__diary__jepa_prednorm_dateblock_mobility_context | -0.000001 | diary | JEPA residual/prednorm diary signal for context |
| human_signed__diary__subject_order | -0.000001 | diary | subject order |
| human_signed__diary__jepa_prednorm_subject_social_comm | -0.000001 | diary | JEPA residual/prednorm diary signal for comm |
| human_signed__diary__sensor_measurement_energy | -0.000001 | diary | sensor measurement energy |
| human_pos_minus_neg__diary__month_sin | -0.000001 | diary | month sin |
| human_signed__diary__weekday_sin | -0.000001 | diary | weekday sin |
| human_signed__diary__jepa_resid_subject_social_comm | -0.000001 | diary | JEPA residual/prednorm diary signal for comm |

## Features Associated With Worse Mean Edge

| aggregate_feature | weight_for_lower_mean_is_negative | source | human_story |
| --- | --- | --- | --- |
| top__subject_signed_share_id06 | 0.000003 | topology | top  subject signed share id06 |
| top__subject_signed_share_id03 | 0.000002 | topology | top  subject signed share id03 |
| human_pos_minus_neg__diary__social_comm_energy | 0.000001 | diary | social comm energy |
| top__neg_rows | 0.000001 | topology | top  neg rows |
| human_signed__diary__month_cos | 0.000001 | diary | month cos |
| human_pos_minus_neg__diary__social_comm_pc1 | 0.000001 | diary | social comm pc1 |
| human_pos_minus_neg__diary__jepa_prednorm_dateblock_physiology_activity | 0.000001 | diary | JEPA residual/prednorm diary signal for activity |
| top__neg_abs_sum | 0.000001 | topology | top  neg abs sum |
| human_pos_minus_neg__diary__jepa_resid_dateblock_sensor_measurement | 0.000001 | diary | JEPA residual/prednorm diary signal for measurement |
| human_pos_minus_neg__diary__media_game_energy | 0.000001 | diary | media game energy |
| human_pos_minus_neg__diary__routine_calendar_pc4 | 0.000001 | diary | routine calendar pc4 |
| human_signed__story__bright_light_late | 0.000001 | human_social | Phone/wearable light exposure near sleep. |
| human_signed__diary__month_sin | 0.000001 | diary | month sin |
| human_abs__story__weekday_routine_pressure | 0.000001 | human_social | Weekday plus commute/work/study signal. |
| human_signed__diary__diary_state_pc9 | 0.000001 | diary | learned day-level diary state geometry |

## Decision

- Placement health has some learnable structure, but this is not yet a submission rule.
- The E300 actual candidate predicted mean rank pct is `0.433594` under human_all_plus_topology.
- Do not submit E300 or any E301 null placement.
- Next useful step: if any feature family has stable leave-mode-out signal, turn it into a constrained subject/dateblock placement prior; otherwise stop S4 mask surgery and return to broader episode/block-state targets.

## Outputs

- `analysis_outputs/e302_s4_placement_health_summary.csv`
- `analysis_outputs/e302_s4_placement_health_cv.csv`
- `analysis_outputs/e302_s4_placement_health_predictions.csv`
- `analysis_outputs/e302_s4_placement_health_feature_weights.csv`
- `analysis_outputs/e302_s4_placement_health_best_nulls.csv`
- `analysis_outputs/e302_s4_placement_health_report.md`
