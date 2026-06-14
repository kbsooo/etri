# Human-State Prototype Grammar Core

## 한 줄 요약

이 실험은 HS-JEPA를 연속 latent 후처리가 아니라 `인간 생활 episode prototype grammar`를 예측하는 core architecture로 검증한다.

```text
visible semantic lifelog views
  -> predict masked hidden prototype responsibilities
  -> freeze predicted grammar
  -> subject-heldout / chronological / row-block probes
```

## 판정

- verdict: `subject_invariant_prototype_grammar_core_positive_boundary`
- grammar frame: `subject_relative_lifelog`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 HS-JEPA Core인가

JEPA의 질문을 인간 생활 로그로 옮기면 다음과 같다.

```text
일부 생활 context만 보고,
보이지 않는 semantic view가 어떤 human-state prototype에 속하는지 예측할 수 있는가?
```

여기서 prototype은 Q/S label이 아니다. phone behavior, body/sleep, social/app, mobility/environment 같은 semantic view가 만드는 label-free episode 원형이다.
또한 prototype은 absolute feature가 아니라 subject-relative lifelog 좌표에서 만든다.
따라서 한 사람의 고유 센서/사용량 크기를 외우는 것이 아니라, 그 사람 기준으로 오늘이 어떤 생활 episode 원형에 가까운지를 묻는다.

## Masked Context -> Prototype Responsibility Pretext

- 평균 cross-entropy lift vs prior: `0.072856`
- best pretext view: `app_social_context`
- best cross-entropy lift: `0.148333`

| target_view | prototype_count | context_feature_count | cross_entropy | prior_cross_entropy | cross_entropy_lift_vs_prior | accuracy | prior_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| app_social_context | 3 | 16 | 0.871740 | 1.020074 | 0.148333 | 0.637143 | 0.475714 |
| phone_behavior | 3 | 16 | 0.666394 | 0.764233 | 0.097840 | 0.711429 | 0.715714 |
| mobility_environment | 3 | 16 | 0.911525 | 0.995238 | 0.083713 | 0.578571 | 0.534286 |
| body_activity_sleep | 3 | 16 | 0.983495 | 1.023918 | 0.040423 | 0.521429 | 0.482857 |
| calendar_rhythm | 3 | 16 | 0.725685 | 0.719658 | -0.006027 | 0.732857 | 0.695714 |

## Subject-Heldout Frozen Probe

같은 subject가 train/validation 양쪽에 동시에 들어가지 않는다. label은 frozen representation을 읽는 probe에서만 사용한다.

| feature_set | logloss | auc |
| --- | --- | --- |
| observed_prototype_upper_bound_calibrated10 | 0.676519 | 0.407258 |
| prototype_full_observed_predicted_calibrated10 | 0.676747 | 0.410006 |
| calendar_rhythm_calibrated10 | 0.676787 | 0.402565 |
| observed_prototype_upper_bound_calibrated05 | 0.677095 | 0.396841 |
| prototype_full_observed_predicted_calibrated05 | 0.677189 | 0.397529 |
| calendar_rhythm_calibrated05 | 0.677293 | 0.396052 |
| predicted_prototype_grammar_calibrated10 | 0.677367 | 0.402592 |
| predicted_prototype_grammar_energy_calibrated10 | 0.677373 | 0.404157 |
| predicted_prototype_grammar_energy_calibrated05 | 0.677518 | 0.394005 |
| predicted_prototype_grammar_calibrated05 | 0.677526 | 0.393203 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated05 | 0.677858 | 0.382414 |
| raw_lifelog_pca_calibrated05 | 0.678009 | 0.398296 |
| calendar_rhythm | 0.678576 | 0.480758 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| observed_prototype_upper_bound | 0.701063 | 0.502720 |
| predicted_prototype_grammar | 0.708659 | 0.488960 |

## Chronological Frozen Probe

각 subject의 앞쪽 episode로 읽고 뒤쪽 episode를 평가한다.

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_lifelog_pca_calibrated05 | 0.667603 | 0.603053 |
| observed_prototype_upper_bound_calibrated10 | 0.668794 | 0.541113 |
| calendar_rhythm_calibrated10 | 0.669335 | 0.547961 |
| prototype_full_observed_predicted_calibrated10 | 0.669500 | 0.529361 |
| observed_prototype_upper_bound_calibrated05 | 0.669707 | 0.541113 |
| prototype_full_observed_predicted_calibrated05 | 0.670037 | 0.529361 |
| calendar_rhythm_calibrated05 | 0.670047 | 0.547961 |
| calendar_rhythm | 0.670067 | 0.547961 |
| predicted_prototype_grammar_calibrated10 | 0.670597 | 0.513735 |
| predicted_prototype_grammar_calibrated05 | 0.670614 | 0.513735 |
| predicted_prototype_grammar_energy_calibrated05 | 0.670656 | 0.511706 |
| predicted_prototype_grammar_energy_calibrated10 | 0.670738 | 0.511706 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only_calibrated05 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| observed_prototype_upper_bound | 0.693018 | 0.541113 |
| predicted_prototype_grammar | 0.710584 | 0.513735 |

## Row-Block Frozen Probe

전체 row order를 시간 block으로 나누어 특정 시기 block을 통째로 holdout한다.

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| raw_lifelog_pca_calibrated05 | 0.670991 | 0.447387 |
| observed_prototype_upper_bound_calibrated10 | 0.672657 | 0.432755 |
| prototype_full_observed_predicted_calibrated10 | 0.672915 | 0.432183 |
| calendar_rhythm_calibrated10 | 0.673248 | 0.416598 |
| observed_prototype_upper_bound_calibrated05 | 0.673277 | 0.419634 |
| prototype_full_observed_predicted_calibrated05 | 0.673392 | 0.419473 |
| calendar_rhythm_calibrated05 | 0.673631 | 0.410856 |
| predicted_prototype_grammar_calibrated05 | 0.674037 | 0.407880 |
| predicted_prototype_grammar_energy_calibrated05 | 0.674077 | 0.409491 |
| prior_only_calibrated05 | 0.674078 | 0.401854 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| predicted_prototype_grammar_calibrated10 | 0.674158 | 0.415304 |
| predicted_prototype_grammar_energy_calibrated10 | 0.674269 | 0.418390 |
| calendar_rhythm | 0.678226 | 0.490044 |
| raw_lifelog_pca | 0.686287 | 0.588427 |
| observed_prototype_upper_bound | 0.696583 | 0.516499 |

## Neighbor Consistency

좋은 prototype grammar라면 가까운 이웃의 target vector가 random 이웃보다 더 비슷해야 한다.

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| calendar_rhythm | 0.586159 | 0.530794 | 0.055365 |
| raw_lifelog_pca | 0.580571 | 0.528127 | 0.052444 |
| observed_prototype_upper_bound | 0.534286 | 0.528635 | 0.005651 |
| predicted_prototype_grammar | 0.529587 | 0.528063 | 0.001524 |
| prototype_full_observed_predicted | 0.533460 | 0.532317 | 0.001143 |
| predicted_prototype_grammar_energy | 0.532000 | 0.531302 | 0.000698 |

## Subject Leakage Probe

prototype grammar가 subject identity shortcut인지 확인한다. accuracy가 높을수록 subject identity를 더 잘 외운다.

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| calendar_rhythm | 0.137778 | 0.126667 | 0.011111 |
| observed_prototype_upper_bound | 0.186667 | 0.126667 | 0.060000 |
| predicted_prototype_grammar | 0.204444 | 0.126667 | 0.077778 |
| prototype_full_observed_predicted | 0.226667 | 0.126667 | 0.100000 |
| predicted_prototype_grammar_energy | 0.231111 | 0.126667 | 0.104444 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## Prototype Interpretation

각 prototype의 상위 feature는 사람이 해석 가능한 생활 episode 원형을 제공한다.

| view | prototype | rows | subject_entropy_0to1 | top_positive_features | top_negative_features |
| --- | --- | --- | --- | --- | --- |
| app_social_context | 0 | 114 | 0.988325 | night_usage_home_launcher_time, night_usage_total_time, night_usage_social_time, night_usage_search_browser_time, night_usage_finance_time | usage_media_time, usage_search_browser_time, usage_call_time, usage_social_time, usage_religion_ritual_time |
| app_social_context | 1 | 333 | 0.990597 | usage_total_time, usage_entropy, usage_app_count, usage_home_launcher_time, usage_social_time | night_usage_home_launcher_time, night_usage_total_time, night_usage_search_browser_time, night_usage_social_time, night_usage_finance_time |
| app_social_context | 2 | 253 | 0.994355 | night_usage_media_time, usage_media_time, night_usage_call_time, night_usage_search_browser_time, night_usage_finance_time | usage_total_time, usage_entropy, usage_app_count, usage_home_launcher_time, usage_social_time |
| body_activity_sleep | 0 | 241 | 0.993199 | distance_sum, walking_step_sum, step_sum, running_step_sum, speed_mean | hr_max, pedo_rows, hr_mean, hr_points, hr_min |
| body_activity_sleep | 1 | 338 | 0.985574 | night_step_sum, active_minutes, pedo_rows, hr_min, hr_max | distance_sum, walking_step_sum, step_sum, running_step_sum, hr_mean |
| body_activity_sleep | 2 | 121 | 0.995766 | hr_mean, hr_rows, hr_points, hr_max, speed_max | active_minutes, night_step_sum, speed_mean, walking_step_sum, step_sum |
| calendar_rhythm | 0 | 190 | 0.995852 | is_weekend, dayofweek, month_start_proximity, dayofmonth, month_end | month_end, dayofmonth, month_start_proximity, dayofweek, is_weekend |
| calendar_rhythm | 1 | 487 | 0.995132 | month_start_proximity, dayofmonth, month_end, dayofweek, is_weekend | is_weekend, dayofweek, month_end, dayofmonth, month_start_proximity |
| calendar_rhythm | 2 | 23 | 0.972032 | month_end, dayofmonth, is_weekend, dayofweek, month_start_proximity | month_start_proximity, dayofweek, is_weekend, dayofmonth, month_end |
| mobility_environment | 0 | 107 | 0.948610 | gps_lon_std, gps_lat_std, gps_speed_mean, wifi_rssi_mean, ble_rssi_mean | gps_rows, gps_points, wifi_count, wifi_strong_count, gps_moving_points |
| mobility_environment | 1 | 219 | 0.979633 | ble_count, ble_strong_count, gps_moving_points, wifi_count, wifi_strong_count | ble_rssi_mean, wifi_rssi_mean, gps_points, gps_rows, gps_lon_std |
| mobility_environment | 2 | 374 | 0.981409 | gps_rows, gps_points, ble_rssi_mean, wifi_rssi_mean, wifi_strong_count | ble_count, ble_strong_count, gps_lat_std, gps_lon_std, gps_speed_mean |
| phone_behavior | 0 | 51 | 0.934279 | screen_use_morning_value, phone_light_mean, screen_use_count, phone_activity_mean, phone_activity_morning_value | phone_activity_evening_value, screen_use_evening_value, phone_charging_morning_value, phone_charging_count, phone_charging_std |
| phone_behavior | 1 | 148 | 0.986998 | phone_light_morning_value, watch_light_count, watch_light_std, phone_light_std, phone_light_count | screen_use_morning_value, phone_charging_evening_value, phone_activity_max, phone_activity_mean, screen_use_count |
| phone_behavior | 2 | 501 | 0.989721 | screen_use_evening_value, phone_activity_evening_value, phone_charging_morning_value, phone_charging_count, phone_charging_evening_value | phone_light_morning_value, watch_light_count, watch_light_std, phone_activity_morning_value, phone_light_count |

## 현재 해석

이 실험이 strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 label prediction 이전에 subject-invariant human-life episode grammar를 복원한다.
이 grammar는 subject-heldout 조건에서도 target manifold를 더 선형적으로 만든다.
```

negative이면 다음 경계가 생긴다.

```text
prototype grammar 자체는 masked view를 예측할 수 있지만,
Q/S label로 번역되는 축은 listener-specific drift/route decoder가 따로 필요하다.
```
