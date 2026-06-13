# Multi-Target Human-State World Model Core

## 한 줄 요약

HS-JEPA를 단일 hidden target 실험에서 통합 world model로 올린 실험이다.

```text
visible human-life context
  -> predicted routine-break state
  -> predicted sleep-pressure state
  -> predicted personal-vs-peer cohort state
  -> unified hidden human-state bundle
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `core_positive_with_route_preservation`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- primary probe: `multi_target_predicted_calibrated10`
- route-preserving predicted bundle delta vs prior: `-0.001499`
- route-preserving predicted bundle delta vs best single predicted target: `-0.000118`
- compressed core-latent delta vs prior: `0.000422`
- compressed core-latent delta vs best single predicted target: `0.001802`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label을 pretext target으로 쓰지 않는다.
대신 보이는 생활 context가 세 종류의 보이지 않는 human-state representation을 동시에 예측해야 한다.

1. routine-break: 개인 루틴이 얼마나 깨졌는가
2. sleep-pressure: 수면 압력/각성/회복부하가 어떤 상태인가
3. cohort-relative: 개인 기준과 peer 기준에서 오늘은 어디에 놓이는가

따라서 architecture claim은 다음이다.

```text
HS-JEPA는 하나의 label을 맞히는 모델이 아니라,
여러 human-state target representation을 예측해
사람의 생활 상태를 더 선형적인 latent bundle로 만든다.
```

## Pretext 결과

- best module: `cohort_relative`
- best task: `visible_context_to_cohort_relative_state`
- best target: `personal_vs_peer_state`
- best component-corr lift vs null: `0.672489`
- best R2 lift vs null: `0.572030`

| module | task | target | context | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | all_visible_context | 0.672489 | 0.572030 |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | masked_without_calendar_rhythm | 0.660407 | 0.536780 |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | masked_without_app_social_context | 0.658303 | 0.522193 |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | masked_without_mobility_environment | 0.636033 | 0.487831 |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | masked_without_body_activity_sleep | 0.614354 | 0.471030 |
| sleep_pressure | masked_context_to_sleep_pressure_family | social_cognitive_arousal | NA | 0.563048 | 0.499132 |
| cohort_relative | visible_context_to_cohort_relative_state | personal_vs_peer_state | masked_without_phone_behavior | 0.556048 | 0.361465 |
| sleep_pressure | masked_context_to_sleep_pressure_family | rest_environment_stability | NA | 0.463648 | 0.366696 |
| routine_break | masked_context_to_routine_break_view | mobility_environment | NA | 0.424933 | 0.267127 |
| routine_break | masked_context_to_routine_break_view | app_social_context | NA | 0.371241 | 0.280137 |
| routine_break | masked_context_to_routine_break_view | phone_behavior | NA | 0.347189 | 0.223796 |
| sleep_pressure | masked_context_to_sleep_pressure_family | physiological_load | NA | 0.310819 | 0.232742 |
| routine_break | current_context_to_next_routine_break | next_episode_routine_break | NA | 0.231253 | 0.137994 |
| sleep_pressure | current_context_to_next_sleep_pressure | next_sleep_pressure_state | NA | 0.204786 | 0.095942 |
| routine_break | masked_context_to_routine_break_view | body_activity_sleep | NA | 0.203998 | 0.185771 |
| cohort_relative | current_context_to_next_cohort_relative_state | next_personal_vs_peer_state | all_visible_context | 0.193978 | 0.123383 |
| sleep_pressure | masked_context_to_sleep_pressure_family | night_disturbance | NA | 0.175119 | 0.047803 |
| sleep_pressure | masked_context_to_sleep_pressure_family | calendar_routine_pressure | NA | 0.090688 | 0.050868 |

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

| feature_set | logloss | auc |
| --- | --- | --- |
| multi_target_predicted_calibrated10 | 0.676358 | 0.411174 |
| cohort_relative_predicted_calibrated10 | 0.676477 | 0.411050 |
| sleep_pressure_predicted_calibrated10 | 0.677266 | 0.405051 |
| multi_target_energy_calibrated10 | 0.677392 | 0.404384 |
| multi_target_predicted_latent_calibrated10 | 0.677433 | 0.397147 |
| routine_break_predicted_calibrated10 | 0.677581 | 0.401671 |
| multi_target_predicted_energy_calibrated10 | 0.677680 | 0.401269 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| multi_target_core_latent_calibrated10 | 0.678279 | 0.390818 |
| multi_target_safe_core_calibrated10 | 0.678631 | 0.390084 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| cohort_relative_full_calibrated10 | 0.679152 | 0.403703 |
| cohort_relative_observed_calibrated10 | 0.679624 | 0.404343 |
| multi_target_predicted_latent | 0.707275 | 0.483961 |
| multi_target_predicted | 0.715521 | 0.508003 |
| multi_target_core_latent | 0.718823 | 0.466698 |
| multi_target_energy | 0.721245 | 0.496250 |
| cohort_relative_predicted | 0.721511 | 0.504779 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| cohort_relative_observed_calibrated10 | 0.667238 | 0.572705 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| cohort_relative_predicted_calibrated10 | 0.668615 | 0.533023 |
| multi_target_predicted_calibrated10 | 0.669005 | 0.526753 |
| cohort_relative_full_calibrated10 | 0.669335 | 0.528330 |
| multi_target_predicted_latent_calibrated10 | 0.669883 | 0.522232 |
| multi_target_energy_calibrated10 | 0.670047 | 0.529286 |
| multi_target_predicted_energy_calibrated10 | 0.670207 | 0.512432 |
| routine_break_predicted_calibrated10 | 0.670340 | 0.508072 |
| multi_target_core_latent_calibrated10 | 0.670348 | 0.517802 |
| multi_target_safe_core_calibrated10 | 0.670639 | 0.511353 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| sleep_pressure_predicted_calibrated10 | 0.671377 | 0.492233 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| multi_target_predicted_latent | 0.696436 | 0.522232 |
| cohort_relative_predicted | 0.705746 | 0.533023 |
| multi_target_predicted | 0.709419 | 0.526753 |
| cohort_relative_observed | 0.711037 | 0.572705 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| cohort_relative_observed | 0.552889 | 0.523492 | 0.029397 |
| cohort_relative_predicted | 0.552762 | 0.528635 | 0.024127 |
| cohort_relative_full | 0.548952 | 0.526159 | 0.022794 |
| multi_target_predicted_energy | 0.543937 | 0.521397 | 0.022540 |
| multi_target_predicted_latent | 0.545206 | 0.525778 | 0.019429 |
| multi_target_predicted | 0.545333 | 0.532317 | 0.013016 |
| multi_target_core_latent | 0.542222 | 0.529905 | 0.012317 |
| routine_break_predicted | 0.538857 | 0.528063 | 0.010794 |
| multi_target_safe_core | 0.543937 | 0.533333 | 0.010603 |
| multi_target_energy | 0.538413 | 0.529206 | 0.009206 |
| sleep_pressure_predicted | 0.539556 | 0.531302 | 0.008254 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| multi_target_energy | 0.400000 | 0.126667 | 0.273333 |
| multi_target_safe_core | 0.386667 | 0.126667 | 0.260000 |
| multi_target_predicted_energy | 0.360000 | 0.126667 | 0.233333 |
| cohort_relative_predicted | 0.353333 | 0.126667 | 0.226667 |
| multi_target_core_latent | 0.348889 | 0.126667 | 0.222222 |
| multi_target_predicted | 0.257778 | 0.126667 | 0.131111 |
| multi_target_predicted_latent | 0.251111 | 0.126667 | 0.124444 |
| routine_break_predicted | 0.097778 | 0.126667 | -0.028889 |
| sleep_pressure_predicted | 0.093333 | 0.126667 | -0.033333 |

## Downstream Probe Candidate

- file: `submission_hsjepa_multi_target_human_state_world_model_probe_d3165dfa_uploadsafe.csv`

이 파일은 core 증거 자체가 아니라, frozen multi-target representation을 competition label로 번역한 probe candidate다.

## 해석

positive이면:

```text
여러 hidden target을 함께 예측하는 HS-JEPA bundle이 subject-heldout label manifold를 더 잘 정렬한다.
단, route 축을 보존해야 하며 PCA식 단일 latent 압축은 오히려 신호를 죽일 수 있다.
```

negative이면:

```text
각 hidden target은 따로는 의미가 있지만, 단순 결합만으로는 더 일반적인 HS-JEPA core가 되지 않는다.
다음 breakthrough는 bundle 결합이 아니라 target별 listener responsibility 또는 adapter-free route selection이어야 한다.
```
