# Human-State World Model Core

## 한 줄 요약

HS-JEPA를 competition 후처리에서 떼어내고, label 없이 학습되는
Human-State World Model로 직접 구현한 실험이다.

```text
visible human-life context views
  -> predict masked / future / cohort hidden human-state representations
  -> freeze representation
  -> simple downstream probe로만 Q/S label 검증
```

## 판정

- verdict: `core_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 HS-JEPA Core인가

이 실험의 학습 목표는 Q1/Q2/Q3/S1/S2/S3/S4를 직접 맞히는 것이 아니다.
수면/활동/앱/모빌리티/캘린더 view 중 일부만 보고, 가려진 다른 view의 latent state와
다음 episode state를 예측한다.

즉 target은 label이 아니라 hidden human-state representation이다.

## Architecture Contract

```text
Human Context Tokenizer
  -> semantic views: calendar, phone, body, app/social, mobility/environment
Context Encoder
  -> available views only
Target Encoder
  -> masked target-view PCA state / future episode state
Predictor
  -> ridge JEPA predictor under subject-heldout OOF
Energy
  -> prediction residual and cohort-normal distance
Frozen Probe
  -> subject-heldout / chronological label probe
```

## Pretext 결과

- best pretext target: `phone_behavior`
- best component-corr lift vs null: `0.464197`
- best R2 lift vs null: `0.327008`

| task | target | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| masked_context_to_view_state | phone_behavior | 0.482254 | 0.018058 | 0.464197 | 0.327008 |
| masked_context_to_view_state | mobility_environment | 0.407046 | 0.025198 | 0.381848 | 0.300896 |
| masked_context_to_view_state | app_social_context | 0.327764 | 0.000595 | 0.327169 | 0.376750 |
| masked_context_to_view_state | body_activity_sleep | 0.307958 | 0.003224 | 0.304734 | 0.302112 |
| masked_context_to_view_state | phone_behavior | 0.199755 | -0.046782 | 0.246537 | 1.168039 |
| masked_context_to_view_state | app_social_context | 0.182834 | -0.059753 | 0.242587 | 0.171517 |
| current_context_to_future_state | next_subject_episode | 0.129260 | -0.028295 | 0.157554 | 10.059206 |
| masked_context_to_view_state | body_activity_sleep | 0.195134 | 0.049745 | 0.145389 | 7.820362 |
| masked_context_to_view_state | mobility_environment | 0.064641 | -0.067564 | 0.132205 | 7.456473 |
| masked_context_to_view_state | calendar_rhythm | 0.089124 | 0.026550 | 0.062574 | 0.056419 |

## Frozen Subject-Heldout Probe

이 표는 world model representation을 freeze한 뒤, 단순 linear probe만 붙인 결과다.
`_calibrated10`은 fold prior에서 10%만 움직이는 고정 low-trust calibration probe다.
이는 representation ranking 신호와 probability overconfidence를 분리하기 위한 장치이며,
public LB나 submission 결과를 사용하지 않는다.

| feature_set | logloss | auc |
| --- | --- | --- |
| subject_relative_world_model_predicted_calibrated10 | 0.677279 | 0.401090 |
| raw_plus_subject_relative_world_model_calibrated10 | 0.677529 | 0.415263 |
| subject_relative_world_model_full_calibrated10 | 0.677657 | 0.399762 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| subject_relative_world_model_energy_calibrated10 | 0.678917 | 0.387583 |
| absolute_world_model_predicted_calibrated10 | 0.679413 | 0.394012 |
| hybrid_absolute_relative_world_model_calibrated10 | 0.679478 | 0.394681 |
| absolute_world_model_full_calibrated10 | 0.681739 | 0.389740 |
| subject_relative_world_model_full | 0.714107 | 0.486525 |
| subject_relative_world_model_energy | 0.721473 | 0.456041 |
| subject_relative_world_model_predicted | 0.722382 | 0.494864 |
| existing_cohort_human_state | 0.766266 | 0.488759 |
| hybrid_absolute_relative_world_model | 0.966087 | 0.470912 |
| raw_plus_subject_relative_world_model | 1.086959 | 0.501514 |
| absolute_world_model_predicted | 1.106534 | 0.477688 |
| absolute_world_model_full | 1.126070 | 0.447899 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Chronological Row-Heldout Probe

각 subject의 앞쪽 날짜로 학습하고 뒤쪽 날짜를 검증한 결과다.

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| absolute_world_model_full_calibrated10 | 0.665122 | 0.596401 |
| raw_plus_subject_relative_world_model_calibrated10 | 0.666873 | 0.580746 |
| absolute_world_model_predicted_calibrated10 | 0.667038 | 0.582384 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| hybrid_absolute_relative_world_model_calibrated10 | 0.668908 | 0.534268 |
| subject_relative_world_model_energy_calibrated10 | 0.669994 | 0.533031 |
| subject_relative_world_model_full_calibrated10 | 0.670216 | 0.521219 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| subject_relative_world_model_predicted_calibrated10 | 0.671288 | 0.499647 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| absolute_world_model_predicted | 0.674757 | 0.582384 |
| absolute_world_model_full | 0.685629 | 0.596401 |
| subject_relative_world_model_energy | 0.690952 | 0.533031 |
| raw_plus_subject_relative_world_model | 0.696585 | 0.580746 |
| hybrid_absolute_relative_world_model | 0.711506 | 0.534268 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| subject_relative_world_model_full | 0.718469 | 0.521219 |
| subject_relative_world_model_predicted | 0.737774 | 0.499647 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| absolute_world_model_predicted | 0.578095 | 0.528063 | 0.050032 |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| raw_plus_subject_relative_world_model | 0.570222 | 0.525778 | 0.044444 |
| absolute_world_model_full | 0.574349 | 0.531302 | 0.043048 |
| hybrid_absolute_relative_world_model | 0.554286 | 0.521397 | 0.032889 |
| subject_relative_world_model_predicted | 0.547302 | 0.528635 | 0.018667 |
| subject_relative_world_model_full | 0.547556 | 0.529206 | 0.018349 |
| subject_relative_world_model_energy | 0.538540 | 0.532317 | 0.006222 |

## Subject Leakage Diagnostic

representation이 human-state가 아니라 subject identity만 외우는지 보기 위한 진단이다.

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| absolute_world_model_full | 0.922222 | 0.126667 | 0.795556 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| absolute_world_model_predicted | 0.884444 | 0.126667 | 0.757778 |
| hybrid_absolute_relative_world_model | 0.697778 | 0.126667 | 0.571111 |
| subject_relative_world_model_energy | 0.517778 | 0.126667 | 0.391111 |
| subject_relative_world_model_full | 0.257778 | 0.126667 | 0.131111 |
| subject_relative_world_model_predicted | 0.073333 | 0.126667 | -0.053333 |

## Downstream Probe Candidate

- file: `submission_hsjepa_human_state_world_model_probe_69ab0808_uploadsafe.csv`

이 파일은 HS-JEPA core 증거가 아니다.
core representation을 competition label로 번역한 downstream probe candidate일 뿐이다.

## 현재 해석

이 실험이 positive이면 다음 주장이 가능하다.

```text
HS-JEPA core는 label 없이 학습한 human-state world representation만으로도
subject-heldout label manifold를 prior/raw baseline보다 더 선형적으로 만든다.
```

negative이면 다음 경계가 생긴다.

```text
masked/future human-state prediction은 가능하지만,
그 representation이 Q/S label을 일반화 가능하게 만들지는 아직 못했다.
```
