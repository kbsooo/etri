# Deep Dive Findings

## Inventory
- Train rows: 450, submission rows: 250, feature rows: 700, feature columns: 1375
- Overall train positive rates: {"Q1": 0.496, "Q2": 0.562, "Q3": 0.6, "S1": 0.682, "S2": 0.651, "S3": 0.662, "S4": 0.56}
- Top missing feature rates: {"hr_early_row_mean_std": 0.749, "hr_early_mean": 0.7, "hr_early_rows": 0.7, "hr_early_points": 0.7, "hr_early_min": 0.7, "hr_early_max": 0.7, "hr_early_std_mean": 0.7, "hr_late_row_mean_std": 0.533, "hr_late_mean": 0.502, "hr_late_rows": 0.502, "hr_late_points": 0.502, "hr_late_min": 0.502, "hr_late_max": 0.502, "hr_late_std_mean": 0.502, "ble_early_items_sum": 0.436, "ble_early_rows": 0.436, "ble_early_items_mean": 0.436, "ble_early_unique_mean": 0.436, "ble_early_unique_max": 0.436, "ble_early_rssi_mean": 0.436, "ble_early_rssi_max": 0.436, "ble_early_class_mean": 0.436, "watch_pedo_step_frequency_early_std": 0.291, "watch_pedo_step_early_std": 0.291, "watch_pedo_burned_calories_early_std": 0.291, "watch_pedo_speed_early_std": 0.291, "watch_pedo_distance_early_std": 0.291, "watch_pedo_burned_calories_early_count": 0.282, "watch_pedo_distance_early_mean": 0.282, "watch_pedo_step_frequency_early_max": 0.282}

## Best CV Rows
```
          fold                        features         model  logloss
 group_subject                    global_prior          mean 0.677858
 group_subject                   subject_prior smoothed_mean 0.677858
 group_subject                          sensor    extratrees 0.690532
 group_subject                calendar_subject        logreg 0.694617
 group_subject                          sensor        logreg 2.047545
        random subject_temporal_target_history   kernel_mean 0.603934
        random                   subject_prior smoothed_mean 0.616112
        random                          sensor    extratrees 0.618546
        random                calendar_subject        logreg 0.621254
        random                          sensor           hgb 0.631342
subject_blocks subject_temporal_target_history   kernel_mean 0.625827
subject_blocks                   subject_prior smoothed_mean 0.627654
subject_blocks                          sensor    extratrees 0.637923
subject_blocks                calendar_subject        logreg 0.639719
subject_blocks                    global_prior          mean 0.667657
```

## Split Chronology
```
subject_id  train_n  sub_n  train_min  train_max    sub_min    sub_max  sub_before_or_on_train_max  train_after_or_on_sub_min                                        runs
      id01       41     27 2024-06-26 2024-08-31 2024-07-30 2024-09-14                          14                         13                             T28 S14 T13 S13
      id02       48     32 2024-07-17 2024-09-27 2024-08-25 2024-10-15                          16                         16                             T32 S16 T16 S16
      id03       33     21 2024-07-17 2024-09-12 2024-08-16 2024-10-09                          11                         11                             T22 S11 T11 S10
      id04       57     27 2024-07-31 2024-10-26 2024-09-09 2024-10-29                          24                         23 T34 S1 T1 S5 T2 S8 T17 S6 T1 S1 T1 S3 T1 S3
      id05       44     21 2024-08-28 2024-11-14 2024-09-28 2024-11-19                          16                         18             T26 S7 T1 S5 T13 S2 T3 S2 T1 S5
      id06       48     24 2024-06-03 2024-08-18 2024-07-06 2024-08-24                          18                         18             T30 S8 T1 S5 T14 S1 T1 S4 T2 S6
      id07       49     30 2024-06-09 2024-08-13 2024-07-13 2024-09-01                          15                         16                             T33 S15 T16 S15
      id08       56     19 2024-06-25 2024-09-16 2024-07-31 2024-09-19                          17                         24 T32 S2 T2 S6 T1 S2 T17 S1 T1 S4 T1 S2 T2 S2
      id09       41     27 2024-07-01 2024-09-03 2024-08-05 2024-09-21                          14                         13                             T28 S14 T13 S13
      id10       33     22 2024-07-06 2024-09-14 2024-08-04 2024-09-26                          11                         11                             T22 S11 T11 S11
```

## Target Autocorrelation
```
target  lag  corr_mean  same_rate_mean
    Q1    1      0.138           0.619
    Q1    2     -0.029           0.551
    Q1    3      0.046           0.572
    Q1    5      0.022           0.565
    Q2    1      0.225           0.655
    Q2    2      0.160           0.624
    Q2    3      0.028           0.573
    Q2    5      0.120           0.605
    Q3    1      0.219           0.649
    Q3    2      0.020           0.564
    Q3    3     -0.042           0.538
    Q3    5      0.077           0.594
    S1    1      0.036           0.645
    S1    2     -0.091           0.586
    S1    3     -0.081           0.590
    S1    5      0.013           0.628
    S2    1      0.002           0.615
    S2    2      0.058           0.655
    S2    3     -0.069           0.588
    S2    5      0.001           0.624
    S3    1     -0.029           0.645
    S3    2     -0.030           0.651
    S3    3     -0.047           0.638
    S3    5     -0.011           0.660
    S4    1      0.015           0.588
    S4    2     -0.017           0.566
    S4    3     -0.056           0.553
    S4    5     -0.069           0.546
```

## Top Subject-Centered Feature Correlations
```
target                                  feature  subject_centered_corr
    Q1        usage_late_usage_kw_call_time_max                 -0.222
    Q1         watch_light_w_light_all_log_mean                 -0.197
    Q1        usage_late_usage_kw_call_time_sum                 -0.187
    Q1                        hr_early_std_mean                  0.178
    Q1       usage_late_usage_kw_call_time_mean                 -0.175
    Q1        watch_light_w_light_all_zero_frac                  0.173
    Q1     usage_evening_usage_kw_call_time_max                 -0.164
    Q1    usage_evening_usage_kw_call_time_mean                 -0.161
    Q2       phone_activity_morning_transitions                 -0.174
    Q2           phone_activity_all_transitions                 -0.171
    Q2          phone_light_m_light_morning_sum                 -0.161
    Q2    phone_activity_m_activity_morning_std                 -0.157
    Q2          phone_light_m_light_morning_q90                 -0.155
    Q2                   ble_evening_items_mean                 -0.153
    Q2                  ble_evening_unique_mean                 -0.153
    Q2                          hr_morning_rows                 -0.151
    Q3             watch_light_w_light_late_std                 -0.166
    Q3                     gps_evening_alt_mean                  0.165
    Q3                   ble_morning_unique_max                 -0.164
    Q3                           wifi_late_rows                  0.157
    Q3                   ble_morning_items_mean                 -0.148
    Q3                  ble_morning_unique_mean                 -0.148
    Q3      phone_charge_m_charging_morning_max                  0.148
    Q3             watch_light_w_light_late_q90                 -0.146
    S1     watch_pedo_burned_calories_early_max                 -0.168
    S1      watch_pedo_step_frequency_early_max                 -0.155
    S1                watch_pedo_step_early_max                 -0.155
    S1     usage_all_usage_kw_finance_time_mean                 -0.154
    S1               watch_pedo_speed_early_max                 -0.153
    S1            watch_pedo_distance_early_max                 -0.153
    S1     watch_pedo_burned_calories_early_std                 -0.150
    S1                           hr_morning_min                 -0.148
    S2                        hr_early_std_mean                  0.186
    S2      ambience_evening_top_is_outside_sum                 -0.150
    S2      usage_early_usage_kw_chat_time_mean                  0.134
    S2                   ambience_all_hour_mean                 -0.132
    S2       ambience_evening_top_is_animal_sum                 -0.126
    S2     ambience_evening_top_is_outside_mean                 -0.124
    S2      ambience_evening_top_is_animal_mean                 -0.123
    S2       ambience_evening_top_is_animal_max                 -0.121
    S3                          hr_early_points                  0.174
    S3                            hr_early_rows                  0.169
    S3                          hr_morning_rows                  0.143
    S3                         hr_afternoon_min                  0.130
    S3      phone_activity_m_activity_early_q90                 -0.128
    S3         phone_charge_m_charging_late_std                  0.124
    S3                     ble_early_class_mean                 -0.122
    S3             phone_light_m_light_late_std                  0.121
    S4     ambience_evening_top_is_outside_mean                 -0.179
    S4                        hr_early_std_mean                  0.177
    S4      ambience_evening_top_is_outside_sum                 -0.174
    S4       phone_activity_m_activity_late_sum                 -0.158
    S4            phone_light_m_light_early_max                  0.154
    S4 phone_charge_m_charging_afternoon_median                 -0.145
    S4     watch_light_w_light_afternoon_median                 -0.143
    S4                     hr_late_row_mean_std                 -0.142
```