# Masked View Surprise Action Release

## 한 줄 요약

이 실험은 HS-JEPA core를 더 JEPA답게 해석한다. label을 바로 예측하지 않고, 보이는 생활 view로 가려진 생활 view representation을 예측한 뒤, 예측이 깨지는 residual energy를 hidden human-state episode로 사용한다.

## JEPA Mapping

| JEPA 구성요소 | 이 실험에서의 의미 |
| --- | --- |
| context | calendar, phone/device, body/sleep/activity, app/social, mobility/environment 중 target view를 제외한 나머지 view |
| target representation | 가려진 view의 PCA latent representation |
| predictor | context view들에서 target view latent를 예측하는 ridge predictor |
| energy | 예측 latent와 실제 target-view latent 사이의 residual norm |
| action decoder | surprise energy가 큰 row에서만 target prevalence law와 neighbor margin이 동의하는 action release |
| anti-shortcut check | public score/action teacher 없이 target shift와 frontier overlap을 사후 평가 |

## 사용하지 않은 정보

- public LB ledger: `False`
- action teacher for support: `False`
- proprietary embedding API: `False`

후보 파일의 probability prior는 `submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv`를 사용한다. 단, row/target 선택은 이 prior와의 차이가 아니라 masked-view surprise energy로 정한다.

## View Prediction Residual

주의: train residual은 subject-heldout OOF residual이고 test residual은 train-fit predictor residual이다. 따라서 절대값을 직접 비교하기보다 row ranking과 target shift를 본다.

| target_view | context_feature_count | target_feature_count | train_mean_residual | test_mean_residual | test_minus_train_mean |
| --- | --- | --- | --- | --- | --- |
| calendar_rhythm | 94 | 5 | 8.022113 | 1.028160 | -6.993953 |
| phone_device | 59 | 40 | 8.593232 | 1.450716 | -7.142517 |
| body_sleep_activity | 81 | 18 | 19.355981 | 1.320793 | -18.035188 |
| app_social_context | 81 | 18 | 4.974281 | 1.175963 | -3.798317 |
| mobility_environment | 81 | 18 | 12.787647 | 0.999600 | -11.788047 |

## Target Surprise Laws

각 target마다 train set에서 surprise 상위 25%와 하위 25%의 prevalence 차이가 가장 큰 score를 골랐다.

| target | surprise_score | low_rate | high_rate | shift | abs_shift |
| --- | --- | --- | --- | --- | --- |
| Q3 | surprise_phone_device_rank | 0.707965 | 0.530973 | -0.176991 | 0.176991 |
| Q2 | surprise_app_social_context_rank | 0.451327 | 0.619469 | 0.168142 | 0.168142 |
| S3 | surprise_body_sleep_activity_rank | 0.619469 | 0.769912 | 0.150442 | 0.150442 |
| S1 | masked_surprise_energy_mean_rank | 0.778761 | 0.654867 | -0.123894 | 0.123894 |
| Q1 | surprise_phone_device_rank | 0.584071 | 0.469027 | -0.115044 | 0.115044 |
| S4 | masked_surprise_energy_disagreement_rank | 0.557522 | 0.654867 | 0.097345 | 0.097345 |
| S2 | masked_surprise_energy_disagreement_rank | 0.654867 | 0.725664 | 0.070796 | 0.070796 |

상세 top shifts:

| target | surprise_score | low_rate | high_rate | shift | abs_shift |
| --- | --- | --- | --- | --- | --- |
| Q3 | surprise_phone_device_rank | 0.707965 | 0.530973 | -0.176991 | 0.176991 |
| Q2 | surprise_app_social_context_rank | 0.451327 | 0.619469 | 0.168142 | 0.168142 |
| S3 | surprise_body_sleep_activity_rank | 0.619469 | 0.769912 | 0.150442 | 0.150442 |
| Q2 | masked_surprise_energy_max_rank | 0.469027 | 0.601770 | 0.132743 | 0.132743 |
| S1 | masked_surprise_energy_mean_rank | 0.778761 | 0.654867 | -0.123894 | 0.123894 |
| S3 | surprise_mobility_environment_rank | 0.628319 | 0.752212 | 0.123894 | 0.123894 |
| S3 | masked_surprise_energy_mean_rank | 0.610619 | 0.725664 | 0.115044 | 0.115044 |
| Q1 | surprise_phone_device_rank | 0.584071 | 0.469027 | -0.115044 | 0.115044 |
| S1 | surprise_mobility_environment_rank | 0.761062 | 0.646018 | -0.115044 | 0.115044 |
| S3 | surprise_phone_device_rank | 0.619469 | 0.725664 | 0.106195 | 0.106195 |
| Q2 | masked_surprise_energy_mean_rank | 0.486726 | 0.592920 | 0.106195 | 0.106195 |
| S4 | masked_surprise_energy_disagreement_rank | 0.557522 | 0.654867 | 0.097345 | 0.097345 |
| Q1 | masked_surprise_energy_max_rank | 0.548673 | 0.451327 | -0.097345 | 0.097345 |
| Q1 | masked_surprise_energy_mean_rank | 0.557522 | 0.460177 | -0.097345 | 0.097345 |
| S1 | surprise_app_social_context_rank | 0.761062 | 0.663717 | -0.097345 | 0.097345 |
| Q2 | surprise_mobility_environment_rank | 0.539823 | 0.628319 | 0.088496 | 0.088496 |
| S3 | surprise_app_social_context_rank | 0.646018 | 0.725664 | 0.079646 | 0.079646 |
| S4 | masked_surprise_energy_mean_rank | 0.530973 | 0.610619 | 0.079646 | 0.079646 |

## Frontier Row 재발견

frontier 파일은 support score 계산에 쓰지 않고, 사후 overlap 평가에만 쓴다.

| reference | top_fraction | k | reference_rows | overlap_rows | recall | precision | mean_selected_surprise_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| row_state_vector_frontier | 0.100000 | 25 | 45 | 4 | 0.088889 | 0.160000 | 0.952000 |
| row_state_vector_frontier | 0.150000 | 38 | 45 | 5 | 0.111111 | 0.131579 | 0.926000 |
| row_state_vector_frontier | 0.200000 | 50 | 45 | 7 | 0.155556 | 0.140000 | 0.902000 |
| row_state_vector_frontier | 0.250000 | 62 | 45 | 11 | 0.244444 | 0.177419 | 0.878000 |
| row_state_vector_frontier | 0.300000 | 75 | 45 | 16 | 0.355556 | 0.213333 | 0.852000 |
| frontier_active_silence | 0.100000 | 25 | 45 | 4 | 0.088889 | 0.160000 | 0.952000 |
| frontier_active_silence | 0.150000 | 38 | 45 | 5 | 0.111111 | 0.131579 | 0.926000 |
| frontier_active_silence | 0.200000 | 50 | 45 | 7 | 0.155556 | 0.140000 | 0.902000 |
| frontier_active_silence | 0.250000 | 62 | 45 | 11 | 0.244444 | 0.177419 | 0.878000 |
| frontier_active_silence | 0.300000 | 75 | 45 | 16 | 0.355556 | 0.213333 | 0.852000 |

Random baseline 대비:

| reference | top_fraction | recall_lift_vs_random | precision_lift_vs_random |
| --- | --- | --- | --- |
| row_state_vector_frontier | 0.100000 | -0.011111 | -0.020000 |
| row_state_vector_frontier | 0.150000 | -0.038889 | -0.048421 |
| row_state_vector_frontier | 0.200000 | -0.044444 | -0.040000 |
| row_state_vector_frontier | 0.250000 | -0.005556 | -0.002581 |
| row_state_vector_frontier | 0.300000 | 0.055556 | 0.033333 |
| frontier_active_silence | 0.100000 | -0.011111 | -0.020000 |
| frontier_active_silence | 0.150000 | -0.038889 | -0.048421 |
| frontier_active_silence | 0.200000 | -0.044444 | -0.040000 |
| frontier_active_silence | 0.250000 | -0.005556 | -0.002581 |
| frontier_active_silence | 0.300000 | 0.055556 | 0.033333 |

## 생성된 후보

- candidate: `submission_hsjepa_masked_view_surprise_action_release_14472506_uploadsafe.csv`
- changed rows: `56`
- changed cells: `177`
- mean abs logit move: `0.187398`
- max abs logit move: `0.493100`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 1e-05, 'probability_max': 0.99999}`

Target action counts:

`{'S1': 38, 'Q2': 35, 'Q1': 27, 'S4': 26, 'Q3': 23, 'S3': 14, 'S2': 14}`

## 해석

이 실험이 성공하면 HS-JEPA core의 contribution은 더 분명해진다.

```text
생활 로그의 부분 context로 다른 view의 latent representation을 예측하고,
그 예측이 깨지는 residual energy가 row-target action support를 설명한다.
```

즉 HS-JEPA는 단순히 대회 label을 맞히는 classifier가 아니라, 인간 생활 상태의 predictability break를 찾아 action-health decoder에 넘기는 architecture가 된다.

실패하면 죽는 주장은 다음이다.

```text
masked-view surprise energy만으로는 action-grade row-target release를 만들 수 있다.
```

현재 local evidence에서 frontier overlap lift는 크지 않고, 더 강한 증거는 Q3/Q2/S3 target prevalence shift다. 따라서 이 후보는 점수 미세조정보다 "masked-view predictability break가 label/action route와 연결되는가"를 확인하는 센서에 가깝다.

실패하더라도 core thesis 전체가 죽지는 않는다. 그 경우에는 surprise energy가 support 후보는 설명하지만, listener responsibility / toxicity veto가 별도 모듈로 필요하다는 결론이 강화된다.

