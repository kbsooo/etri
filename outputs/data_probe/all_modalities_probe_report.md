# All Modalities Overview

## Inventory
| modality | file | kind | rows | subjects | time_min | time_max | columns | median_gap_min | p95_gap_min | gaps_over_10m_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mACStatus | ch2025_mACStatus.parquet | scalar | 939896 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 | subject_id, timestamp, m_charging | 1 | 1 | 0.002628 |
| mActivity | ch2025_mActivity.parquet | categorical | 961062 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 | subject_id, timestamp, m_activity | 1 | 1 | 0.0004599 |
| mAmbience | ch2025_mAmbience.parquet | ambience | 476577 | 10 | 2024-06-03 13:00:10 | 2024-11-19 23:58:10 | subject_id, timestamp, m_ambience | 2 | 2 | 0.0008582 |
| mBle | ch2025_mBle.parquet | device_list | 21830 | 10 | 2024-06-03 13:07:00 | 2024-11-19 21:27:00 | subject_id, timestamp, m_ble | 10 | 180 | 0.398 |
| mGps | ch2025_mGps.parquet | gps | 800611 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 | subject_id, timestamp, m_gps | 1 | 1 | 0.003201 |
| mLight | ch2025_mLight.parquet | scalar | 96258 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:57:00 | subject_id, timestamp, m_light | 10 | 10 | 0.00401 |
| mScreenStatus | ch2025_mScreenStatus.parquet | scalar | 939653 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:59:00 | subject_id, timestamp, m_screen_use | 1 | 1 | 0.002658 |
| mUsageStats | ch2025_mUsageStats.parquet | usage | 45197 | 10 | 2024-06-09 11:00:00 | 2024-11-19 22:10:00 | subject_id, timestamp, m_usage_stats | 10 | 60 | 0.2604 |
| mWifi | ch2025_mWifi.parquet | device_list | 76336 | 10 | 2024-06-03 12:57:00 | 2024-11-19 23:57:00 | subject_id, timestamp, m_wifi | 10 | 17 | 0.05059 |
| wHr | ch2025_wHr.parquet | hr_list | 382918 | 10 | 2024-06-03 14:28:00 | 2024-11-19 15:37:00 | subject_id, timestamp, heart_rate | 1 | 1 | 0.004617 |
| wLight | ch2025_wLight.parquet | scalar | 633741 | 10 | 2024-06-03 14:28:00 | 2024-11-19 23:59:00 | subject_id, timestamp, w_light | 1 | 2 | 0.006493 |
| wPedo | ch2025_wPedo.parquet | multiscalar | 748100 | 10 | 2024-06-03 14:15:00 | 2024-11-19 23:59:00 | subject_id, timestamp, step, step_frequency, running_step, walking_step, distance, speed, burned_calories | 1 | 1 | 0.002072 |

## Coverage By Split
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mACStatus | test | 250 | 250 | 1 | 1396 | 24 |
| mACStatus | train | 450 | 450 | 1 | 1399 | 24 |
| mActivity | test | 250 | 250 | 1 | 1440 | 24 |
| mActivity | train | 450 | 450 | 1 | 1440 | 24 |
| mAmbience | test | 250 | 250 | 1 | 720 | 24 |
| mAmbience | train | 450 | 450 | 1 | 720 | 24 |
| mBle | test | 250 | 235 | 0.94 | 34 | 13 |
| mBle | train | 450 | 416 | 0.9244 | 31 | 13 |
| mGps | test | 250 | 235 | 0.94 | 1387 | 24 |
| mGps | train | 450 | 425 | 0.9444 | 1387 | 24 |
| mLight | test | 250 | 250 | 1 | 144 | 24 |
| mLight | train | 450 | 450 | 1 | 144 | 24 |
| mScreenStatus | test | 250 | 250 | 1 | 1394 | 24 |
| mScreenStatus | train | 450 | 450 | 1 | 1400 | 24 |
| mUsageStats | test | 250 | 250 | 1 | 67 | 18 |
| mUsageStats | train | 450 | 440 | 0.9778 | 66.5 | 18 |
| mWifi | test | 250 | 246 | 0.984 | 120 | 23 |
| mWifi | train | 450 | 439 | 0.9756 | 119 | 23 |
| wHr | test | 250 | 245 | 0.98 | 606 | 13 |
| wHr | train | 450 | 391 | 0.8689 | 613 | 13 |
| wLight | test | 250 | 250 | 1 | 997.5 | 24 |
| wLight | train | 450 | 414 | 0.92 | 1059 | 24 |
| wPedo | test | 250 | 249 | 0.996 | 1281 | 24 |
| wPedo | train | 450 | 404 | 0.8978 | 1280 | 23 |

## Practical Encoder Input Plan
- Align every modality to `subject_id + lifelog_date + hour`.
- For dense minute sensors, aggregate hourly mean/sum/std/rate and keep availability masks.
- For list sensors, use count/unique/RSSI/probability summaries plus top-K or hashed tokens.
- For sequence encoders, feed 24 hourly bins with modality masks; for tabular heads, flatten daypart/day summaries.
- Compute within-subject deviations for every stable numeric channel.


## mACStatus

- file: `ch2025_mACStatus.parquet`
- kind: `scalar`
- rows: 939,896
- columns: subject_id, timestamp, m_charging
- time: 2024-06-03 12:57:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mACStatus | test | 250 | 250 | 1 | 1396 | 24 |
| mACStatus | train | 450 | 450 | 1 | 1399 | 24 |

**numeric_stats**

| feature | count | missing_rate | mean | std | min | p01 | p05 | p50 | p95 | p99 | max | zero_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m_charging | 939896 | 0 | 0.2914 | 0.4544 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0.7086 |

**value_counts**

| modality | feature | value | count | rate |
| --- | --- | --- | --- | --- |
| mACStatus | m_charging | 0 | 666031 | 0.7086 |
| mACStatus | m_charging | 1 | 273865 | 0.2914 |

**Recommended use**
- Use as a phone routine and charging-at-night signal.
- Aggregate charging rate by hour/daypart and longest charging run.
- Do not over-interpret as sleep by itself; combine with screen inactivity and watch signals.

## mActivity

- file: `ch2025_mActivity.parquet`
- kind: `categorical`
- rows: 961,062
- columns: subject_id, timestamp, m_activity
- time: 2024-06-03 12:57:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mActivity | test | 250 | 250 | 1 | 1440 | 24 |
| mActivity | train | 450 | 450 | 1 | 1440 | 24 |

**category_counts**

| value | count | rate |
| --- | --- | --- |
| 3 | 785792 | 0.8176 |
| 4 | 71502 | 0.0744 |
| 0 | 70506 | 0.07336 |
| 7 | 31404 | 0.03268 |
| 1 | 1056 | 0.001099 |
| 8 | 802 | 0.0008345 |

**Recommended use**
- Use class proportions, entropy, daypart proportions, and transition counts.
- Keep the raw integer classes as categorical embeddings for sequence encoders.
- Treat high unknown/still rates as behavior signals, not only noise.

## mAmbience

- file: `ch2025_mAmbience.parquet`
- kind: `ambience`
- rows: 476,577
- columns: subject_id, timestamp, m_ambience
- time: 2024-06-03 13:00:10 to 2024-11-19 23:58:10

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mAmbience | test | 250 | 250 | 1 | 720 | 24 |
| mAmbience | train | 450 | 450 | 1 | 720 | 24 |

**ambience_stats**

| feature | count | mean | std | min | 1% | 5% | 50% | 95% | 99% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| labels_per_row | 4.766e+05 | 10 | 0 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| top_probability | 4.766e+05 | 0.8098 | 0.3109 | 0 | 0.1105 | 0.1697 | 1 | 1 | 1 | 1 |
| probability_sum | 4.766e+05 | 1 | 0.2369 | 0 | 0.4586 | 0.6503 | 1 | 1.344 | 2.008 | 4.89 |

**top_ambience_labels**

| label | top_count | top_rate | any_count |
| --- | --- | --- | --- |
| Silence | 334119 | 0.7011 | 354232 |
| Speech | 50551 | 0.1061 | 396387 |
| Inside, small room | 13845 | 0.02905 | 419651 |
| Music | 10931 | 0.02294 | 352983 |
| Vehicle | 10338 | 0.02169 | 48099 |
| Animal | 7369 | 0.01546 | 69431 |
| Breathing | 6237 | 0.01309 | 19629 |
| Outside, rural or natural | 3551 | 0.007451 | 58371 |
| Mechanical fan | 3449 | 0.007237 | 21134 |
| Snake | 2673 | 0.005609 | 41834 |
| Wind | 2388 | 0.005011 | 25540 |
| Typing | 2316 | 0.00486 | 6023 |

**Recommended use**
- Use top-label rates, label entropy, top probability, and broad groups such as Speech/Music/Vehicle/Outside.
- This is useful for context but labels are noisy; prefer daily/hourly rates over single observations.

## mBle

- file: `ch2025_mBle.parquet`
- kind: `device_list`
- rows: 21,830
- columns: subject_id, timestamp, m_ble
- time: 2024-06-03 13:07:00 to 2024-11-19 21:27:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mBle | test | 250 | 235 | 0.94 | 34 | 13 |
| mBle | train | 450 | 416 | 0.9244 | 31 | 13 |

**device_stats**

| stat | scan_count | unique_count | class_unique_count | rssi_mean | rssi_max | rssi_min |
| --- | --- | --- | --- | --- | --- | --- |
| count | 2.183e+04 | 2.183e+04 | 2.183e+04 | 2.183e+04 | 2.183e+04 | 2.183e+04 |
| mean | 20.02 | 20.02 | 1.913 | -77.17 | -56.07 | -90.76 |
| std | 25.13 | 25.13 | 0.6261 | 7.778 | 15.19 | 7.22 |
| min | 0 | 0 | 0 | -100 | -100 | -106 |
| 1% | 1 | 1 | 1 | -90.4 | -87 | -100 |
| 5% | 2 | 2 | 1 | -87.17 | -80 | -98 |
| 50% | 8 | 8 | 2 | -78.6 | -57 | -92 |
| 95% | 79 | 79 | 3 | -63.29 | -31 | -78 |
| 99% | 96 | 96 | 3 | -51.35 | -22 | -62 |
| max | 196 | 196 | 5 | -15 | -1 | -15 |
| total_unique_ids | 3.505e+05 |  |  |  |  |  |

**top_device_ids**

| id | count |
| --- | --- |
| E8:CA:C8:C8:E4:1A | 1889 |
| 40:CA:63:DB:F2:FB | 1851 |
| 50:FD:D5:01:6D:43 | 1808 |
| 64:12:36:25:0A:75 | 1789 |
| F8:4E:58:7E:E9:D9 | 1766 |
| F8:3B:1D:A0:33:67 | 1674 |
| 80:47:86:65:36:0D | 1569 |
| 50:FD:D5:84:D1:FF | 1109 |
| C8:12:0B:F1:98:2B | 1083 |
| F8:F0:05:DB:D3:21 | 976 |
| F8:F0:05:78:90:CB | 971 |
| 24:11:53:BB:68:B9 | 930 |

**device_aux**

| class | count | type | stat | rssi |
| --- | --- | --- | --- | --- |
| 0 | 3.857e+05 | class |  |  |
| 7936 | 4.5e+04 | class |  |  |
| 1796 | 2524 | class |  |  |
|  | 1144 | class |  |  |
| 1084 | 967 | class |  |  |
| 524 | 662 | class |  |  |
| 1060 | 443 | class |  |  |
| 1280 | 382 | class |  |  |
| 284 | 146 | class |  |  |
| 1024 | 30 | class |  |  |
| 1408 | 15 | class |  |  |
| 1344 | 15 | class |  |  |

**Recommended use**
- Use unique device count, scan count, RSSI stats, class diversity, and within-subject stable-device hashes.
- Good for social/proximity/place context; sparse compared with minute sensors.
- Avoid raw address one-hot explosion; use top-K per subject or feature hashing.

## mGps

- file: `ch2025_mGps.parquet`
- kind: `gps`
- rows: 800,611
- columns: subject_id, timestamp, m_gps
- time: 2024-06-03 12:57:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mGps | test | 250 | 235 | 0.94 | 1387 | 24 |
| mGps | train | 450 | 425 | 0.9444 | 1387 | 24 |

**gps_stats**

| feature | count | mean | std | min | 1% | 5% | 50% | 95% | 99% | max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| points_per_row | 8.006e+05 | 10.68 | 3.111 | 1 | 5 | 6 | 11 | 18 | 19 | 20 |
| latitude | 8.547e+06 | 0.5876 | 0.5428 | 0 | 0.02491 | 0.02557 | 0.476 | 1.418 | 2.417 | 2.749 |
| longitude | 8.547e+06 | 0.4701 | 0.3166 | 0 | 0.01167 | 0.0684 | 0.4931 | 1.032 | 1.119 | 2.47 |
| altitude | 8.547e+06 | 99.34 | 36.26 | -627.2 | 33.1 | 58.8 | 99.8 | 149.9 | 177.7 | 1249 |
| speed | 8.547e+06 | 0.8493 | 3.938 | 0 | 0 | 0 | 0.064 | 2.96 | 19.68 | 246.7 |

**gps_speed_outliers**

| threshold | rate |
| --- | --- |
| 0.5 | 0.153 |
| 1 | 0.1011 |
| 2 | 0.0603 |
| 5 | 0.03851 |
| 10 | 0.02415 |
| 20 | 0.009718 |
| 50 | 0.001286 |
| 100 | 3.51e-07 |

**Recommended use**
- Use as anonymized relative mobility, not real map coordinates.
- Aggregate speed, stationary/moving rate, coordinate spread, active hours, and within-subject mobility deviation.
- Clip speed/altitude outliers before neural inputs.

## mLight

- file: `ch2025_mLight.parquet`
- kind: `scalar`
- rows: 96,258
- columns: subject_id, timestamp, m_light
- time: 2024-06-03 12:57:00 to 2024-11-19 23:57:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mLight | test | 250 | 250 | 1 | 144 | 24 |
| mLight | train | 450 | 450 | 1 | 144 | 24 |

**numeric_stats**

| feature | count | missing_rate | mean | std | min | p01 | p05 | p50 | p95 | p99 | max | zero_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m_light | 96258 | 0 | 185.2 | 1940 | 0 | 0 | 0 | 9 | 628 | 1420 | 3.343e+05 | 0.4212 |

**value_counts**

_empty_

**Recommended use**
- Use phone ambient light exposure by daypart, especially evening/night and morning.
- Combine with screen and charging to infer phone context; phone light alone may reflect device placement.

## mScreenStatus

- file: `ch2025_mScreenStatus.parquet`
- kind: `scalar`
- rows: 939,653
- columns: subject_id, timestamp, m_screen_use
- time: 2024-06-03 12:57:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mScreenStatus | test | 250 | 250 | 1 | 1394 | 24 |
| mScreenStatus | train | 450 | 450 | 1 | 1400 | 24 |

**numeric_stats**

| feature | count | missing_rate | mean | std | min | p01 | p05 | p50 | p95 | p99 | max | zero_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| m_screen_use | 939653 | 0 | 0.2284 | 0.4198 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0.7716 |

**value_counts**

| modality | feature | value | count | rate |
| --- | --- | --- | --- | --- |
| mScreenStatus | m_screen_use | 0 | 725047 | 0.7716 |
| mScreenStatus | m_screen_use | 1 | 214606 | 0.2284 |

**Recommended use**
- Highly useful bedtime behavior signal.
- Use screen-use rate by hour, late-night use, last active time, total active minutes, and long inactivity runs.

## mUsageStats

- file: `ch2025_mUsageStats.parquet`
- kind: `usage`
- rows: 45,197
- columns: subject_id, timestamp, m_usage_stats
- time: 2024-06-09 11:00:00 to 2024-11-19 22:10:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mUsageStats | test | 250 | 250 | 1 | 67 | 18 |
| mUsageStats | train | 450 | 440 | 0.9778 | 66.5 | 18 |

**usage_stats**

| stat | apps_per_row | unique_apps_per_row | total_time_sum | total_time_max |
| --- | --- | --- | --- | --- |
| count | 4.52e+04 | 4.52e+04 | 4.52e+04 | 4.52e+04 |
| mean | 3.505 | 3.505 | 4.623e+05 | 2.51e+05 |
| std | 2.122 | 2.122 | 4.371e+05 | 1.871e+05 |
| min | 1 | 1 | 3 | 3 |
| 1% | 1 | 1 | 189 | 186.9 |
| 5% | 1 | 1 | 2927 | 2911 |
| 50% | 3 | 3 | 3.733e+05 | 2.513e+05 |
| 95% | 7 | 7 | 1.338e+06 | 5.534e+05 |
| 99% | 10 | 10 | 1.836e+06 | 5.889e+05 |
| max | 21 | 21 | 3.222e+06 | 6.003e+05 |
| app_total_time_count |  |  | 1.584e+05 |  |
| app_total_time_mean |  |  | 1.319e+05 |  |

**top_apps**

| app | count |
| --- | --- |
| One UI 홈 | 29114 |
| 카카오톡 | 17548 |
| 시스템 UI | 16388 |
| NAVER | 7361 |
| 캐시워크 | 5042 |
| ✝️성경일독Q | 4615 |
| YouTube | 4566 |
| 통화 | 4364 |
| 메시지 | 3845 |
| 타임스프레드 | 3504 |
| Instagram | 3440 |
| 전화 | 2997 |

**Recommended use**
- Use total app time, unique apps, app entropy, late-night app use, and coarse app categories/top-K apps.
- App names are high-cardinality and personal; use top-K/hash/category rather than raw one-hot everywhere.

## mWifi

- file: `ch2025_mWifi.parquet`
- kind: `device_list`
- rows: 76,336
- columns: subject_id, timestamp, m_wifi
- time: 2024-06-03 12:57:00 to 2024-11-19 23:57:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| mWifi | test | 250 | 246 | 0.984 | 120 | 23 |
| mWifi | train | 450 | 439 | 0.9756 | 119 | 23 |

**device_stats**

| stat | scan_count | unique_count | class_unique_count | rssi_mean | rssi_max | rssi_min |
| --- | --- | --- | --- | --- | --- | --- |
| count | 7.634e+04 | 7.634e+04 | 7.634e+04 | 7.634e+04 | 7.634e+04 | 7.634e+04 |
| mean | 16.64 | 16.64 | 0 | -71.38 | -48.1 | -87.47 |
| std | 12.94 | 12.94 | 0 | 8.014 | 13.8 | 5.927 |
| min | 1 | 1 | 0 | -96 | -96 | -101 |
| 1% | 2 | 2 | 0 | -87.67 | -84 | -96 |
| 5% | 4 | 4 | 0 | -84.44 | -76 | -95 |
| 50% | 13 | 13 | 0 | -71.14 | -46 | -88 |
| 95% | 40 | 40 | 0 | -58.91 | -30 | -78 |
| 99% | 64 | 64 | 0 | -53.25 | -18 | -67 |
| max | 199 | 199 | 0 | -25 | 0 | -29 |
| total_unique_ids | 1.252e+05 |  |  |  |  |  |

**top_device_ids**

| id | count |
| --- | --- |
| 00:23:aa:58:95:e4 | 7315 |
| 88:3c:1c:a7:a2:17 | 7283 |
| 42:23:aa:58:95:e4 | 7282 |
| 80:ca:4b:0d:3b:66 | 7254 |
| 00:23:aa:58:95:e5 | 7224 |
| 42:23:aa:58:95:e5 | 7215 |
| 88:3c:1c:a7:a2:18 | 7183 |
| 80:ca:4b:0d:3b:67 | 6922 |
| 1c:ec:72:51:1a:97 | 6831 |
| 50:46:ae:3b:2b:c7 | 6459 |
| 08:5d:dd:d8:9e:53 | 6221 |
| 3a:5d:dd:d8:9e:53 | 6219 |

**device_aux**

| type | stat | rssi |
| --- | --- | --- |
| rssi | count | 1.27e+06 |
| rssi | mean | -72.4 |
| rssi | std | 15.55 |
| rssi | min | -101 |
| rssi | 1% | -94 |
| rssi | 5% | -92 |
| rssi | 50% | -77 |
| rssi | 95% | -42 |
| rssi | 99% | -33 |
| rssi | max | 0 |

**Recommended use**
- Strong place/routine proxy; often more useful than anonymized GPS for location stability.
- Use unique AP count, scan density, RSSI stats, repeated AP overlap, place entropy, and within-subject location clusters.
- Avoid raw BSSID leakage/overfit; use subject-local clustering or hashing.

## wHr

- file: `ch2025_wHr.parquet`
- kind: `hr_list`
- rows: 382,918
- columns: subject_id, timestamp, heart_rate
- time: 2024-06-03 14:28:00 to 2024-11-19 15:37:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| wHr | test | 250 | 245 | 0.98 | 606 | 13 |
| wHr | train | 450 | 391 | 0.8689 | 613 | 13 |

**hr_stats**

| stat | hr_points_per_row | hr_mean | hr_std | hr_min | hr_max |
| --- | --- | --- | --- | --- | --- |
| count | 3.829e+05 | 3.829e+05 | 3.829e+05 | 3.829e+05 | 3.829e+05 |
| mean | 52.21 | 88.09 | 3.596 | 81.79 | 94.69 |
| std | 17.23 | 15.48 | 2.423 | 15.39 | 16.08 |
| min | 1 | 1 | 0 | 1 | 1 |
| 1% | 1 | 58.6 | 0 | 52 | 60 |
| 5% | 4 | 64.81 | 0.8635 | 60 | 70 |
| 50% | 59 | 87.1 | 3.062 | 81 | 94 |
| 95% | 60 | 115.4 | 8.078 | 109 | 122 |
| 99% | 61 | 130.2 | 12 | 124 | 138 |
| max | 61 | 254 | 56.5 | 254 | 254 |
| raw_hr_count |  | 1.999e+07 |  |  |  |
| raw_hr_mean |  | 87.79 |  |  |  |

**Recommended use**
- Use heart-rate level/variability, nighttime resting HR, high-HR bursts, and coverage as watch-wearing signal.
- List values per minute should be summarized per hour before feeding sequence models.

## wLight

- file: `ch2025_wLight.parquet`
- kind: `scalar`
- rows: 633,741
- columns: subject_id, timestamp, w_light
- time: 2024-06-03 14:28:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| wLight | test | 250 | 250 | 1 | 997.5 | 24 |
| wLight | train | 450 | 414 | 0.92 | 1059 | 24 |

**numeric_stats**

| feature | count | missing_rate | mean | std | min | p01 | p05 | p50 | p95 | p99 | max | zero_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| w_light | 633741 | 0 | 198.2 | 1344 | 0 | 0 | 0 | 23 | 593 | 2774 | 1.27e+05 | 0.3581 |

**value_counts**

_empty_

**Recommended use**
- Use wrist light exposure, night darkness, morning exposure, and coverage/wearing proxies.
- Interpret together with watch HR and pedometer.

## wPedo

- file: `ch2025_wPedo.parquet`
- kind: `multiscalar`
- rows: 748,100
- columns: subject_id, timestamp, step, step_frequency, running_step, walking_step, distance, speed, burned_calories
- time: 2024-06-03 14:15:00 to 2024-11-19 23:59:00

**Target-day coverage**
| modality | split | target_days | available_days | availability | median_rows | median_active_hours |
| --- | --- | --- | --- | --- | --- | --- |
| wPedo | test | 250 | 249 | 0.996 | 1281 | 24 |
| wPedo | train | 450 | 404 | 0.8978 | 1280 | 23 |

**numeric_stats**

| feature | count | missing_rate | mean | std | min | p01 | p05 | p50 | p95 | p99 | max | zero_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| step | 748100 | 0 | 3.452 | 14.89 | 0 | 0 | 0 | 0 | 22 | 94 | 317 | 0.91 |
| step_frequency | 748100 | 0 | 0.05753 | 0.2481 | 0 | 0 | 0 | 0 | 0.3667 | 1.567 | 5.283 | 0.91 |
| running_step | 748100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| walking_step | 748100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| distance | 748100 | 0 | 2.579 | 11.25 | 0 | 0 | 0 | 0 | 15.95 | 69.7 | 302.2 | 0.91 |
| speed | 748100 | 0 | 0.04298 | 0.1875 | 0 | 0 | 0 | 0 | 0.2658 | 1.162 | 5.037 | 0.91 |
| burned_calories | 748100 | 0 | 0.1524 | 2.139 | 0 | 0 | 0 | 0 | 0.76 | 3.39 | 310.7 | 0.9153 |

**value_counts**

| modality | feature | value | count | rate |
| --- | --- | --- | --- | --- |
| wPedo | running_step | 0 | 748100 | 1 |
| wPedo | walking_step | 0 | 748100 | 1 |

**Recommended use**
- Use steps/distance/speed/calories by hour/daypart, active bouts, sedentary duration, and personal deviations.
- Zeros are meaningful; preserve zero rates rather than imputing them away.

