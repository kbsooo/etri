# Route-Responsibility World Model Core

## 한 줄 요약

route-preserving multi-target HS-JEPA 위에서,
각 row가 어떤 hidden route에 책임을 둬야 하는지 label 없이 추정하는 실험이다.

```text
other predicted routes
  -> held-out route representation
  -> cross-route residual energy
  -> label-free route responsibility
  -> responsibility-weighted human-state axes
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `core_positive_but_not_base_improving`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- primary probe: `route_weighted_predicted_calibrated10`
- route-weighted delta vs prior: `-0.000720`
- route-weighted delta vs base multi-target: `0.000780`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label을 route responsibility target으로 쓰지 않는다.
대신 route 간 예측 가능성만 본다.

예를 들어 routine-break와 sleep-pressure만으로 cohort-relative route를 잘 예측할 수 없다면,
그 row에서 cohort route는 non-redundant한 책임을 가진다.

즉 core 질문은 다음이다.

```text
HS-JEPA가 hidden route bundle 안에서
어느 route가 그 row의 독립적인 human-state 정보를 들고 있는지
label 없이 추정할 수 있는가?
```

## Route Pretext 결과

| task | target_route | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| cross_route_to_hidden_route | routine_break | 0.946524 | 0.073634 | 0.872891 | 0.975238 |
| cross_route_to_hidden_route | sleep_pressure | 0.909081 | 0.053403 | 0.855678 | 0.946943 |
| cross_route_to_hidden_route | cohort_relative | 0.784211 | -0.000472 | 0.784684 | 0.772297 |

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

| feature_set | logloss | auc |
| --- | --- | --- |
| base_multi_target_predicted_calibrated10 | 0.676358 | 0.411174 |
| route_weighted_predicted_calibrated10 | 0.677138 | 0.403992 |
| base_multi_target_energy_calibrated10 | 0.677392 | 0.404384 |
| route_weighted_plus_scores_calibrated10 | 0.677642 | 0.398308 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| route_responsibility_scores_calibrated10 | 0.678220 | 0.383662 |
| route_weighted_plus_residual_calibrated10 | 0.678281 | 0.390661 |
| route_responsibility_full_calibrated10 | 0.678570 | 0.388196 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| route_responsibility_scores | 0.691489 | 0.440748 |
| base_multi_target_predicted | 0.715521 | 0.508003 |
| route_weighted_predicted | 0.715970 | 0.502641 |
| route_weighted_plus_scores | 0.719047 | 0.492557 |
| base_multi_target_energy | 0.721245 | 0.496250 |
| route_weighted_plus_residual | 0.725302 | 0.473987 |
| route_responsibility_full | 0.726050 | 0.464773 |
| existing_cohort_human_state | 0.766266 | 0.488759 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| base_multi_target_predicted_calibrated10 | 0.669005 | 0.526753 |
| route_weighted_predicted_calibrated10 | 0.669712 | 0.523134 |
| route_weighted_plus_residual_calibrated10 | 0.669994 | 0.514543 |
| base_multi_target_energy_calibrated10 | 0.670047 | 0.529286 |
| route_weighted_plus_scores_calibrated10 | 0.670103 | 0.517707 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| route_responsibility_scores_calibrated10 | 0.670957 | 0.503563 |
| route_responsibility_full_calibrated10 | 0.671111 | 0.498031 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| route_responsibility_scores | 0.683736 | 0.503563 |
| base_multi_target_predicted | 0.709419 | 0.526753 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| route_weighted_plus_scores | 0.715905 | 0.517707 |
| route_weighted_plus_residual | 0.716261 | 0.514543 |
| route_weighted_predicted | 0.717723 | 0.523134 |
| route_responsibility_full | 0.723747 | 0.498031 |
| base_multi_target_energy | 0.725809 | 0.529286 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| route_weighted_plus_residual | 0.546222 | 0.521397 | 0.024825 |
| base_multi_target_predicted | 0.545333 | 0.528063 | 0.017270 |
| route_responsibility_full | 0.540063 | 0.525778 | 0.014286 |
| route_weighted_plus_scores | 0.540635 | 0.529206 | 0.011429 |
| base_multi_target_energy | 0.538413 | 0.531302 | 0.007111 |
| route_weighted_predicted | 0.538921 | 0.532317 | 0.006603 |
| route_responsibility_scores | 0.517651 | 0.528635 | -0.010984 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| base_multi_target_energy | 0.400000 | 0.126667 | 0.273333 |
| base_multi_target_predicted | 0.257778 | 0.126667 | 0.131111 |
| route_weighted_predicted | 0.226667 | 0.126667 | 0.100000 |
| route_weighted_plus_residual | 0.224444 | 0.126667 | 0.097778 |
| route_weighted_plus_scores | 0.220000 | 0.126667 | 0.093333 |
| route_responsibility_scores | 0.166667 | 0.126667 | 0.040000 |

## Downstream Probe Candidate

- file: `submission_hsjepa_route_responsibility_world_model_probe_bab0d5b7_uploadsafe.csv`

이 파일은 core evidence 자체가 아니라, route responsibility weighted axes를 competition label로 번역한 downstream probe candidate다.

## 해석

positive이면:

```text
HS-JEPA core는 route를 보존할 뿐 아니라,
어떤 route가 row의 non-redundant hidden state를 들고 있는지 label 없이 추정할 수 있다.
단, base multi-target을 이기지 못하면 route weighting은 core diagnostic이지 최종 representation replacement는 아니다.
```

negative이면:

```text
route responsibility는 label-free redundancy만으로는 부족하다.
다음에는 listener/target별 responsibility를 weak supervision 또는 action-health diagnostic과 분리해서 배워야 한다.
```
