# Phase 4B — Descriptive day archetypes

KMeans를 예측 모델로 쓰는 게 아니라, 일상 day를 몇 가지 **서술 가능한 생활 상태**로 묶어 라벨 분포를 본다.

## archetype별 label rate

| archetype | n_days | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|---|
| 0.000 | 138.000 | 0.522 | 0.529 | 0.623 | 0.717 | 0.659 | 0.638 | 0.558 |
| 1.000 | 67.000 | 0.493 | 0.612 | 0.642 | 0.522 | 0.507 | 0.567 | 0.597 |
| 2.000 | 37.000 | 0.595 | 0.541 | 0.622 | 0.757 | 0.838 | 0.838 | 0.703 |
| 3.000 | 51.000 | 0.451 | 0.588 | 0.490 | 0.686 | 0.667 | 0.745 | 0.471 |
| 4.000 | 157.000 | 0.465 | 0.567 | 0.592 | 0.701 | 0.656 | 0.656 | 0.541 |


## archetype을 가장 잘 설명하는 feature

| archetype | feature | z_vs_global |
|---|---|---|
| 0 | app_unique_count | 0.524 |
| 0 | wlight_max | 0.517 |
| 0 | app_total_time | 0.512 |
| 0 | steps_sum | 0.507 |
| 0 | state_entropy | 0.455 |
| 0 | mlight_max | 0.425 |
| 0 | hr_mean_21_03 | 0.399 |
| 0 | wifi_unique_bssid | 0.373 |
| 1 | screen_use_00_06 | 1.522 |
| 1 | screen_use_sum | 1.158 |
| 1 | screen_use_18_24 | 1.154 |
| 1 | longest_screenoff_run_h | -1.121 |
| 1 | app_time_21_03 | 1.022 |
| 1 | app_social_time | 0.940 |
| 1 | hr_count | 0.754 |
| 1 | gps_speed_mean | -0.546 |
| 2 | gps_radius_proxy | 2.636 |
| 2 | gps_speed_mean | 2.270 |
| 2 | gps_unique_grid4 | 1.954 |
| 2 | wifi_unique_bssid | 0.872 |
| 2 | screen_use_sum | -0.851 |
| 2 | app_browser_search_time | 0.819 |
| 2 | longest_screenoff_run_h | 0.684 |
| 2 | screen_use_18_24 | -0.641 |
| 3 | ble_unique_addr | 2.261 |
| 3 | ble_records | 2.261 |
| 3 | screen_use_sum | 0.939 |
| 3 | mlight_mean | 0.705 |
| 3 | gps_count | -0.618 |
| 3 | state_entropy | 0.594 |
| 3 | night_state_entropy | 0.517 |
| 3 | hr_std | -0.500 |
| 4 | app_total_time | -0.661 |
| 4 | state_entropy | -0.652 |
| 4 | night_state_entropy | -0.613 |
| 4 | ble_records | -0.596 |
| 4 | ble_unique_addr | -0.581 |
| 4 | wifi_unique_bssid | -0.580 |
| 4 | steps_sum | -0.573 |
| 4 | app_unique_count | -0.549 |

