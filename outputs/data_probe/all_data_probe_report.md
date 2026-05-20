# All-data utilization probe

This is an EDA artifact, not a model-training report.

## Inventory
- Rows: 700 total = 450 train + 250 test/unlabeled target rows
- Subjects: 10
- Numeric feature candidates created for all rows: 324

## Target rates
- Q1: 0.496
- Q2: 0.562
- Q3: 0.600
- S1: 0.682
- S2: 0.651
- S3: 0.662
- S4: 0.560

## Most useful all-data routes
1. Build the sensor representation on all 700 subject-days, then train only the final supervised head on the 450 labeled days.
2. Use all 700 rows for transductive preprocessing: feature vocabularies, robust scaling, PCA/clusters, missingness profiles, and train-test shift diagnostics.
3. Convert each modality into self-supervised targets before using labels: next-hour activity/screen/charging prediction, masked sensor reconstruction, and cross-modal reconstruction.
4. Use the 250 test rows as unlabeled distribution anchors for semi-supervised consistency or conservative pseudo-labeling, but keep pseudo labels gated by CV stability.
5. Treat each subject as a short longitudinal panel: learn subject routines from every available lifelog day, then predict deviations from each person's own baseline.

## Coverage by modality
| modality | split | n_rows | available_days | availability_rate | median_events | mean_events |
| --- | --- | --- | --- | --- | --- | --- |
| mAC | test | 250 | 250 | 1 | 1396 | 1343 |
| mAC | train | 450 | 450 | 1 | 1399 | 1342 |
| mActivity | test | 250 | 250 | 1 | 1440 | 1374 |
| mActivity | train | 450 | 450 | 1 | 1440 | 1372 |
| mAmbience | test | 250 | 250 | 1 | 720 | 681.8 |
| mAmbience | train | 450 | 450 | 1 | 720 | 680.3 |
| mBle | test | 250 | 235 | 0.94 | 34 | 34.64 |
| mBle | train | 450 | 416 | 0.9244 | 31 | 32.91 |
| mGps | test | 250 | 235 | 0.94 | 1387 | 1223 |
| mGps | train | 450 | 425 | 0.9444 | 1387 | 1208 |
| mLight | test | 250 | 250 | 1 | 144 | 137.8 |
| mLight | train | 450 | 450 | 1 | 144 | 137.4 |
| mScreen | test | 250 | 250 | 1 | 1394 | 1345 |
| mScreen | train | 450 | 450 | 1 | 1400 | 1341 |
| mUsage | test | 250 | 250 | 1 | 67 | 66 |
| mUsage | train | 450 | 440 | 0.9778 | 66.5 | 65.22 |
| mWifi | test | 250 | 246 | 0.984 | 120 | 111.7 |
| mWifi | train | 450 | 439 | 0.9756 | 119 | 111.3 |
| wHr | test | 250 | 245 | 0.98 | 606 | 584.9 |
| wHr | train | 450 | 391 | 0.8689 | 613 | 612.8 |
| wLight | test | 250 | 250 | 1 | 997.5 | 935.2 |
| wLight | train | 450 | 414 | 0.92 | 1059 | 966 |
| wPedo | test | 250 | 249 | 0.996 | 1281 | 1160 |
| wPedo | train | 450 | 404 | 0.8978 | 1280 | 1137 |

## Top train-test shifts
| feature | train_mean | test_mean | smd_test_minus_train | ks_stat | ks_pvalue | train_missing | test_missing |
| --- | --- | --- | --- | --- | --- | --- | --- |
| day_index_subject | 32.48 | 58.5 | 1.046 | 0.5596 | 5.992e-47 | 0 | 0 |
| gps_points_std | 2.406 | 2.129 | -0.326 | 0.2018 | 7.088e-06 | 0.05778 | 0.06 |
| gps_points_mean | 10.39 | 11.03 | 0.3083 | 0.1915 | 2.447e-05 | 0.05556 | 0.06 |
| wPedo_burned_calories_max | 38.3 | 21.01 | -0.2988 | 0.177 | 0.0001063 | 0.1022 | 0.004 |
| wPedo_burned_calories_std | 1.486 | 0.9144 | -0.322 | 0.1527 | 0.00131 | 0.1022 | 0.004 |
| gps_points_sum | 1.264e+04 | 1.351e+04 | 0.2092 | 0.1433 | 0.003495 | 0.05556 | 0.06 |
| wLight_w_light_sum | 1.961e+05 | 1.777e+05 | -0.1027 | 0.1413 | 0.003476 | 0.08 | 0 |
| mWifi_rssi_mean_max | -55.24 | -57.18 | -0.2551 | 0.1411 | 0.003305 | 0.02444 | 0.016 |
| wPedo_burned_calories_mean | 0.1766 | 0.1366 | -0.2863 | 0.1346 | 0.006674 | 0.1022 | 0.004 |
| wLight_w_light_afternoon_mean | 364 | 304.5 | -0.1672 | 0.1345 | 0.00755 | 0.1111 | 0.032 |
| wLight_w_light_evening_mean | 72.39 | 58.67 | -0.1559 | 0.1292 | 0.01269 | 0.1356 | 0.044 |
| gps_speed_mean_max | 19.69 | 20.15 | 0.02764 | 0.1268 | 0.01382 | 0.05556 | 0.06 |
| mUsage_app_help_CNUH24_rate | 0.03097 | 0.0257 | -0.2319 | 0.1233 | 0.01414 | 0.02222 | 0 |
| wPedo_burned_calories_afternoon_mean | 0.2697 | 0.2059 | -0.2637 | 0.1223 | 0.02033 | 0.1133 | 0.04 |
| mUsage_app_Withings_rate | 0.02906 | 0.01674 | -0.2605 | 0.1207 | 0.01728 | 0.02222 | 0 |
| wLight_w_light_mean | 207.4 | 184.2 | -0.1226 | 0.1199 | 0.02033 | 0.08 | 0 |
| mBle_class_unique_count_mean | 1.994 | 1.952 | -0.1057 | 0.1184 | 0.02671 | 0.07556 | 0.06 |
| mLight_m_light_afternoon_mean | 373.6 | 346.1 | -0.0483 | 0.1171 | 0.02256 | 0.004444 | 0.004 |
| mWifi_rssi_mean_std | 6.222 | 5.764 | -0.2348 | 0.1166 | 0.02823 | 0.04889 | 0.048 |
| wLight_w_light_median | 49.65 | 41.42 | -0.13 | 0.1135 | 0.03268 | 0.08 | 0 |

## Top feature-label associations
| target | feature | mi | spearman | abs_spearman |
| --- | --- | --- | --- | --- |
| Q1 | mWifi_rssi_min_mean | 0.07568 | 0.06297 | 0.06297 |
| Q1 | mScreen_rows | 0.0692 | 0.0284 | 0.0284 |
| Q1 | mAC_m_charging_median | 0.05483 | 0.07908 | 0.07908 |
| Q1 | mUsage_app_help_CNUH24_rate | 0.05138 | -0.1018 | 0.1018 |
| Q1 | hr_mean_max | 0.0501 | 0.0804 | 0.0804 |
| Q1 | subject_ord | 0.05004 | -0.08725 | 0.08725 |
| Q1 | mUsage_app_Microsoft_Launcher_rate | 0.05003 | 0.01474 | 0.01474 |
| Q1 | wPedo_burned_calories_afternoon_mean | 0.04974 | -0.004692 | 0.004692 |
| Q1 | mUsage_app_One_UI_홈_rate | 0.04895 | -0.1458 | 0.1458 |
| Q1 | gps_lat_std_sum | 0.04788 | 0.08623 | 0.08623 |
| Q1 | hr_p90_mean | 0.04703 | 0.05716 | 0.05716 |
| Q1 | hr_p10_max | 0.04445 | 0.06357 | 0.06357 |
| Q2 | mWifi_class_unique_count_mean | 0.06678 |  |  |
| Q2 | mWifi_scan_count_sum | 0.0631 | -0.143 | 0.143 |
| Q2 | mWifi_unique_count_sum | 0.0618 | -0.143 | 0.143 |
| Q2 | gps_alt_mean_sum | 0.05906 | -0.002259 | 0.002259 |
| Q2 | hr_std_std | 0.0589 | -0.006267 | 0.006267 |
| Q2 | mUsage_app_total_time_sum | 0.05855 | 0.1031 | 0.1031 |
| Q2 | mUsage_app_events_mean | 0.05394 | 0.001017 | 0.001017 |
| Q2 | mUsage_unique_apps_mean | 0.05356 | 0.001155 | 0.001155 |
| Q2 | mBle_scan_count_max | 0.05278 | -0.08921 | 0.08921 |
| Q2 | mGps_rows | 0.05193 | -0.04567 | 0.04567 |
| Q2 | gps_speed_mean_max | 0.051 | -0.06373 | 0.06373 |
| Q2 | mUsage_app_네이트_rate | 0.05087 | 0.1552 | 0.1552 |
| Q3 | mScreen_hour_entropy | 0.07572 | 0.006624 | 0.006624 |
| Q3 | mUsage_app_max_time_std | 0.06835 | 0.07687 | 0.07687 |
| Q3 | mWifi_rssi_max_mean | 0.06536 | -0.07991 | 0.07991 |
| Q3 | mBle_rows | 0.05592 | -0.03537 | 0.03537 |
| Q3 | wPedo_running_step_std | 0.0554 |  |  |
| Q3 | mUsage_app_max_time_mean | 0.05475 | -0.06821 | 0.06821 |
| Q3 | mUsage_app_갤러리_rate | 0.05418 | 0.1632 | 0.1632 |
| Q3 | mUsage_app_네이트_rate | 0.05095 | -0.09222 | 0.09222 |
| Q3 | mUsage_app_통화_rate | 0.05042 | -0.09895 | 0.09895 |
| Q3 | mUsage_app_캐시워크_rate | 0.05001 | 0.04431 | 0.04431 |
| Q3 | mAmbience_rows | 0.04888 | 0.05892 | 0.05892 |
| Q3 | hr_mean_std | 0.04847 | 0.1295 | 0.1295 |
| S1 | mUsage_app_max_time_mean | 0.06628 | -0.2433 | 0.2433 |
| S1 | subject_ord | 0.06571 | -0.1801 | 0.1801 |
| S1 | wPedo_rows | 0.05986 | 0.03762 | 0.03762 |
| S1 | wPedo_burned_calories_afternoon_mean | 0.05807 | -0.01826 | 0.01826 |
| S1 | wPedo_hour_entropy | 0.05557 | 0.02799 | 0.02799 |
| S1 | mWifi_rssi_min_mean | 0.0539 | -0.07692 | 0.07692 |
| S1 | mUsage_unique_apps_sum | 0.0538 | -0.06724 | 0.06724 |
| S1 | wPedo_burned_calories_morning_mean | 0.05047 | -0.07927 | 0.07927 |
| S1 | gps_alt_std_mean | 0.05047 | 0.04979 | 0.04979 |
| S1 | mLight_m_light_night_mean | 0.05013 | -0.04514 | 0.04514 |
| S1 | mScreen_m_screen_use_sum | 0.04702 | -0.2082 | 0.2082 |
| S1 | mBle_rssi_mean_sum | 0.0445 | 0.1701 | 0.1701 |
| S2 | hr_p90_min | 0.08781 | -0.1977 | 0.1977 |
| S2 | subject_ord | 0.08444 | -0.05832 | 0.05832 |
| S2 | mBle_scan_count_std | 0.07712 | 0.09521 | 0.09521 |
| S2 | gps_lat_std_max | 0.07424 | 0.141 | 0.141 |
| S2 | mBle_rssi_max_max | 0.07254 | 0.1972 | 0.1972 |
| S2 | wPedo_step_max | 0.07183 | -0.02063 | 0.02063 |
| S2 | mBle_unique_count_std | 0.06384 | 0.09521 | 0.09521 |
| S2 | mUsage_app_캐시워크_rate | 0.06006 | -0.2206 | 0.2206 |
| S2 | mWifi_scan_count_mean | 0.05831 | 0.117 | 0.117 |
| S2 | mWifi_rssi_mean_max | 0.05626 | -0.1267 | 0.1267 |
| S2 | mUsage_app_전화_rate | 0.05263 | 0.2068 | 0.2068 |
| S2 | hr_std_std | 0.05185 | 0.1211 | 0.1211 |
| S3 | subject_ord | 0.1108 | -0.06477 | 0.06477 |
| S3 | mUsage_app_통화_rate | 0.0734 | 0.1689 | 0.1689 |
| S3 | mBle_rssi_max_max | 0.06957 | 0.2294 | 0.2294 |
| S3 | wPedo_walking_step_median | 0.06273 |  |  |
| S3 | gps_lon_std_mean | 0.06196 | 0.07461 | 0.07461 |
| S3 | mWifi_rssi_max_max | 0.06037 | -0.1898 | 0.1898 |
| S3 | mBle_rssi_max_sum | 0.06008 | 0.08268 | 0.08268 |
| S3 | wLight_w_light_late_night_mean | 0.05818 | 0.1452 | 0.1452 |
| S3 | mAC_rows | 0.05532 | 0.1045 | 0.1045 |
| S3 | hr_mean_mean | 0.05381 | -0.2075 | 0.2075 |
| S3 | mUsage_app_시스템_UI_rate | 0.05117 | -0.09422 | 0.09422 |
| S3 | mUsage_app_Google_Play_스토어_rate | 0.04914 | -0.033 | 0.033 |
| S4 | mUsage_app_events_mean | 0.06848 | 0.08509 | 0.08509 |
| S4 | mUsage_unique_apps_mean | 0.06737 | 0.08502 | 0.08502 |
| S4 | wLight_w_light_mean | 0.06479 | 0.01136 | 0.01136 |
| S4 | wPedo_burned_calories_mean | 0.06306 | -0.1141 | 0.1141 |
| S4 | gps_speed_mean_max | 0.06211 | 0.1692 | 0.1692 |
| S4 | wLight_active_hours | 0.06156 | -0.001988 | 0.001988 |
| S4 | gps_lon_std_std | 0.05811 | 0.0463 | 0.0463 |
| S4 | hr_p10_min | 0.0575 | -0.01526 | 0.01526 |
| S4 | gps_alt_std_max | 0.05549 | -0.07514 | 0.07514 |
| S4 | mLight_m_light_median | 0.05541 | 0.02626 | 0.02626 |
| S4 | subject_ord | 0.05243 | 0.08207 | 0.08207 |
| S4 | hr_std_min | 0.04846 | 0.07053 | 0.07053 |

## Unsupervised clusters
Silhouette by k:
| k | silhouette |
| --- | --- |
| 3 | 0.1346 |
| 4 | 0.1462 |
| 5 | 0.1593 |
| 6 | 0.1684 |
| 7 | 0.1876 |
| 8 | 0.2015 |

Cluster composition and train label rates:
| cluster | split | n | subjects | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | test | 38 | 2 | 0.4839 | 0.4839 | 0.629 | 0.5323 | 0.4355 | 0.5645 | 0.4839 |
| 0 | train | 62 | 4 | 0.4839 | 0.4839 | 0.629 | 0.5323 | 0.4355 | 0.5645 | 0.4839 |
| 1 | test | 60 | 6 | 0.5859 | 0.5781 | 0.7188 | 0.8281 | 0.6797 | 0.5938 | 0.5156 |
| 1 | train | 128 | 8 | 0.5859 | 0.5781 | 0.7188 | 0.8281 | 0.6797 | 0.5938 | 0.5156 |
| 2 | test | 23 | 4 | 0.5 | 0.6154 | 0.6154 | 0.8462 | 1 | 0.9615 | 0.7692 |
| 2 | train | 26 | 2 | 0.5 | 0.6154 | 0.6154 | 0.8462 | 1 | 0.9615 | 0.7692 |
| 3 | test | 18 | 2 | 0.3958 | 0.75 | 0.4167 | 0.4375 | 0.6042 | 0.6458 | 0.5625 |
| 3 | train | 48 | 1 | 0.3958 | 0.75 | 0.4167 | 0.4375 | 0.6042 | 0.6458 | 0.5625 |
| 4 | test | 23 | 1 | 0.4872 | 0.4359 | 0.4103 | 0.5641 | 0.7692 | 0.7179 | 0.5641 |
| 4 | train | 39 | 1 | 0.4872 | 0.4359 | 0.4103 | 0.5641 | 0.7692 | 0.7179 | 0.5641 |
| 5 | test | 44 | 8 | 0.4754 | 0.5738 | 0.623 | 0.7705 | 0.7377 | 0.8033 | 0.6557 |
| 5 | train | 61 | 9 | 0.4754 | 0.5738 | 0.623 | 0.7705 | 0.7377 | 0.8033 | 0.6557 |
| 6 | test | 34 | 3 | 0.4921 | 0.5079 | 0.5873 | 0.6825 | 0.5873 | 0.6667 | 0.5556 |
| 6 | train | 63 | 5 | 0.4921 | 0.5079 | 0.5873 | 0.6825 | 0.5873 | 0.6667 | 0.5556 |
| 7 | test | 10 | 5 | 0.3043 | 0.5652 | 0.5217 | 0.5652 | 0.5217 | 0.5217 | 0.5217 |
| 7 | train | 23 | 9 | 0.3043 | 0.5652 | 0.5217 | 0.5652 | 0.5217 | 0.5217 | 0.5217 |

## Strong sensor relationships
| feature_a | feature_b | spearman | abs_spearman |
| --- | --- | --- | --- |
| mBle_rows | mScreen_m_screen_use_mean | 0.8971 | 0.8971 |
| mActivity_rows | mAmbience_rows | 0.8957 | 0.8957 |
| mAC_rows | mScreen_rows | 0.8026 | 0.8026 |
| mUsage_rows | mUsage_app_total_time_sum | 0.7891 | 0.7891 |
| mAmbience_rows | mLight_rows | 0.744 | 0.744 |
| mActivity_rows | mLight_rows | 0.7295 | 0.7295 |
| mWifi_rows | mAC_m_charging_mean | 0.6871 | 0.6871 |
| mActivity_rows | mScreen_rows | 0.6779 | 0.6779 |
| mAC_rows | mActivity_rows | 0.6693 | 0.6693 |
| wHr_rows | wLight_rows | 0.6507 | 0.6507 |
| mAmbience_rows | mScreen_rows | 0.6278 | 0.6278 |
| mAC_rows | mAmbience_rows | 0.5964 | 0.5964 |
| mGps_rows | mWifi_rows | 0.5914 | 0.5914 |
| mLight_rows | mScreen_rows | 0.5866 | 0.5866 |
| mAC_rows | mLight_rows | 0.5786 | 0.5786 |
| mLight_m_light_mean | wLight_w_light_mean | 0.5378 | 0.5378 |
| wLight_rows | wPedo_rows | 0.4838 | 0.4838 |
| mBle_rows | mUsage_app_total_time_sum | 0.4834 | 0.4834 |
| mGps_rows | mLight_rows | 0.4538 | 0.4538 |
| wLight_w_light_mean | wPedo_step_sum | 0.4307 | 0.4307 |
| mBle_unique_count_mean | mLight_m_light_mean | 0.428 | 0.428 |
| mBle_unique_count_mean | gps_speed_mean_mean | 0.4269 | 0.4269 |
| mActivity_rows | mGps_rows | 0.415 | 0.415 |
| wHr_rows | wPedo_step_sum | 0.4107 | 0.4107 |
| mBle_rows | mUsage_rows | 0.4106 | 0.4106 |
| mAmbience_rows | mGps_rows | 0.4088 | 0.4088 |
| mScreen_m_screen_use_mean | mUsage_app_total_time_sum | 0.408 | 0.408 |
| mLight_rows | mWifi_rows | 0.3888 | 0.3888 |
| mAmbience_rows | mWifi_rows | 0.3712 | 0.3712 |
| mAC_m_charging_mean | mWifi_unique_count_mean | 0.363 | 0.363 |

## Cautions
- Do not use test labels; submission_sample target zeros are placeholders.
- Subject-level statistics can leak if computed with labels or fold-held rows. Unsupervised sensor-only statistics across all 700 rows are acceptable for transductive exploration but should be explicitly separated from supervised CV.
- The target rows overlap in calendar time across train/test by subject, so validation must be temporal or grouped temporal, not random-only.
