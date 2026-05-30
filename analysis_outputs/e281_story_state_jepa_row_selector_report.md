# E281 Story-State JEPA Row Selector Audit

## Question

Can the strongest human/social stories become target-free JEPA representations whose row placement survives local null checks?

## Method

- Top E280 stories tested: `6`
- For each story, predict its subject-normalized story score from all other numeric diary-state context columns, excluding the mapped family.
- Evaluate predicted story state as one extra feature on a calendar/subject baseline for all 7 labels.
- Matched nulls: `25` row, subject, and dateblock shuffles per story/split.
- No public LB, no submission.

## Summary

- story/split rows: `12`
- JEPA story gate rows: `3`
- stories passing both subject and dateblock gates: `1`

## Story/Split Results

| story_id | mapped_family | split | state_oof_r2 | state_oof_corr | actual_delta_mean | actual_delta_best | actual_best_target | null_median | null_best | dominance | jepa_story_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| app_entropy_scattered_day | routine_calendar | subject5 | 0.419010 | 0.751144 | -0.001950 | -0.017952 | Q3 | 0.001968 | -0.001425 | 1.000000 | True |
| single_app_monotony | routine_calendar | subject5 | 0.140158 | 0.621743 | -0.001594 | -0.019011 | Q3 | 0.001709 | -0.000407 | 1.000000 | True |
| app_entropy_scattered_day | routine_calendar | dateblock5 | 0.728347 | 0.853483 | -0.000109 | -0.005987 | Q2 | 0.001488 | -0.003046 | 0.920000 | True |
| single_app_monotony | routine_calendar | dateblock5 | 0.563699 | 0.753038 | 0.000025 | -0.004542 | Q2 | 0.001456 | -0.001191 | 0.906667 | False |
| commute_workday | mobility_context | dateblock5 | 0.499860 | 0.712647 | 0.000897 | -0.002670 | S4 | 0.001506 | -0.001794 | 0.666667 | False |
| vehicle_noise_day | mobility_context | dateblock5 | 0.616829 | 0.787327 | 0.001840 | -0.002118 | S3 | 0.001412 | -0.000806 | 0.360000 | False |
| bright_light_late | bedtime_phone | dateblock5 | 0.105266 | 0.374831 | 0.002905 | -0.000814 | S4 | 0.002025 | -0.000592 | 0.200000 | False |
| commute_workday | mobility_context | subject5 | 0.199246 | 0.584120 | 0.003311 | -0.002777 | Q2 | 0.002316 | -0.001873 | 0.253333 | False |
| heart_stress_late | physiology_activity | dateblock5 | 0.089595 | 0.396688 | 0.003693 | -0.004470 | Q3 | 0.002063 | -0.001628 | 0.093333 | False |
| vehicle_noise_day | mobility_context | subject5 | 0.397923 | 0.708911 | 0.005411 | 0.000690 | S4 | 0.001751 | -0.005062 | 0.040000 | False |
| heart_stress_late | physiology_activity | subject5 | -0.548213 | 0.280026 | 0.005661 | -0.002177 | S2 | 0.002845 | -0.001228 | 0.186667 | False |
| bright_light_late | bedtime_phone | subject5 | -0.704671 | 0.229200 | 0.014784 | -0.005027 | S1 | 0.003416 | -0.003598 | 0.000000 | False |

## Best Target Rows

| story_id | mapped_family | split | target | delta_logloss | state_oof_r2 | state_oof_corr |
| --- | --- | --- | --- | --- | --- | --- |
| single_app_monotony | routine_calendar | subject5 | Q3 | -0.019011 | 0.140158 | 0.621743 |
| app_entropy_scattered_day | routine_calendar | subject5 | Q3 | -0.017952 | 0.419010 | 0.751144 |
| app_entropy_scattered_day | routine_calendar | dateblock5 | Q2 | -0.005987 | 0.728347 | 0.853483 |
| bright_light_late | bedtime_phone | subject5 | S1 | -0.005027 | -0.704671 | 0.229200 |
| single_app_monotony | routine_calendar | dateblock5 | Q2 | -0.004542 | 0.563699 | 0.753038 |
| heart_stress_late | physiology_activity | dateblock5 | Q3 | -0.004470 | 0.089595 | 0.396688 |
| single_app_monotony | routine_calendar | dateblock5 | Q3 | -0.003591 | 0.563699 | 0.753038 |
| app_entropy_scattered_day | routine_calendar | dateblock5 | S2 | -0.003491 | 0.728347 | 0.853483 |
| commute_workday | mobility_context | subject5 | Q2 | -0.002777 | 0.199246 | 0.584120 |
| commute_workday | mobility_context | dateblock5 | S4 | -0.002670 | 0.499860 | 0.712647 |
| heart_stress_late | physiology_activity | subject5 | S2 | -0.002177 | -0.548213 | 0.280026 |
| vehicle_noise_day | mobility_context | dateblock5 | S3 | -0.002118 | 0.616829 | 0.787327 |
| app_entropy_scattered_day | routine_calendar | subject5 | Q2 | -0.001909 | 0.419010 | 0.751144 |
| app_entropy_scattered_day | routine_calendar | dateblock5 | Q3 | -0.001893 | 0.728347 | 0.853483 |
| heart_stress_late | physiology_activity | subject5 | S3 | -0.001389 | -0.548213 | 0.280026 |
| single_app_monotony | routine_calendar | dateblock5 | S2 | -0.001063 | 0.563699 | 0.753038 |
| bright_light_late | bedtime_phone | dateblock5 | S4 | -0.000814 | 0.105266 | 0.374831 |
| single_app_monotony | routine_calendar | dateblock5 | Q1 | -0.000719 | 0.563699 | 0.753038 |
| single_app_monotony | routine_calendar | subject5 | S4 | -0.000443 | 0.140158 | 0.621743 |
| app_entropy_scattered_day | routine_calendar | subject5 | S4 | -0.000396 | 0.419010 | 0.751144 |
| commute_workday | mobility_context | dateblock5 | S2 | -0.000396 | 0.499860 | 0.712647 |
| commute_workday | mobility_context | dateblock5 | Q3 | -0.000239 | 0.499860 | 0.712647 |
| app_entropy_scattered_day | routine_calendar | subject5 | Q1 | -0.000073 | 0.419010 | 0.751144 |
| app_entropy_scattered_day | routine_calendar | dateblock5 | Q1 | -0.000011 | 0.728347 | 0.853483 |
| single_app_monotony | routine_calendar | subject5 | Q1 | 0.000045 | 0.140158 | 0.621743 |
| commute_workday | mobility_context | subject5 | S1 | 0.000155 | 0.199246 | 0.584120 |
| single_app_monotony | routine_calendar | subject5 | Q2 | 0.000228 | 0.140158 | 0.621743 |
| app_entropy_scattered_day | routine_calendar | subject5 | S2 | 0.000423 | 0.419010 | 0.751144 |
| vehicle_noise_day | mobility_context | subject5 | S4 | 0.000690 | 0.397923 | 0.708911 |
| bright_light_late | bedtime_phone | dateblock5 | Q1 | 0.000778 | 0.105266 | 0.374831 |

## Decision

Stories passing both local gates: `app_entropy_scattered_day`. These still need a separate materialization governor before any public LB use.

## Files

- `e281_story_state_jepa_row_selector_summary.csv`
- `e281_story_state_jepa_row_selector_target_detail.csv`
- `e281_story_state_jepa_row_selector_nulls.csv`
