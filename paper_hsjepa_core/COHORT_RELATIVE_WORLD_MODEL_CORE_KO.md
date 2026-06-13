# Cohort-Relative World Model Core

## 한 줄 요약

HS-JEPA의 hidden target을 `개인의 평소`와 `비슷한 peer cohort의 평소` 사이의 좌표계로 만든 실험이다.

```text
visible daily human-life context
  -> hidden personal-vs-peer cohort-relative representation
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `core_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- cohort count: `2`
- cohort sizes: `{'0': 5, '1': 5}`
- cohort selection: singleton cohort를 허용하지 않는 가장 큰 K를 선택한다.

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label이나 public LB를 target으로 삼지 않는다.
target은 다음 label-free geometry다.

1. 오늘이 이 사람의 평소에서 얼마나 벗어났는가
2. 오늘이 비슷한 peer cohort의 평소에서 얼마나 벗어났는가
3. 이 사람 자체가 자기 cohort 안에서 얼마나 특이한가
4. 이 row가 개인 기준 outlier인지, peer 기준 outlier인지

즉 질문은 다음이다.

```text
보이는 생활 context만으로
개인-대-peer human-state 좌표계에서 오늘의 위치를 예측할 수 있는가?
```

## Pretext 결과

- best pretext task: `visible_context_to_cohort_relative_state`
- best context: `all_visible_context`
- best component-corr lift vs null: `0.672489`
- best R2 lift vs null: `0.572030`

| task | context | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| visible_context_to_cohort_relative_state | all_visible_context | 0.598483 | -0.074006 | 0.672489 | 0.572030 |
| visible_context_to_cohort_relative_state | masked_without_calendar_rhythm | 0.573907 | -0.086500 | 0.660407 | 0.536780 |
| visible_context_to_cohort_relative_state | masked_without_app_social_context | 0.564018 | -0.094286 | 0.658303 | 0.522193 |
| visible_context_to_cohort_relative_state | masked_without_mobility_environment | 0.552843 | -0.083190 | 0.636033 | 0.487831 |
| visible_context_to_cohort_relative_state | masked_without_body_activity_sleep | 0.529760 | -0.084595 | 0.614354 | 0.471030 |
| visible_context_to_cohort_relative_state | masked_without_phone_behavior | 0.474052 | -0.081995 | 0.556048 | 0.361465 |
| current_context_to_next_cohort_relative_state | all_visible_context | 0.111484 | -0.082493 | 0.193978 | 0.123383 |

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

| feature_set | logloss | auc |
| --- | --- | --- |
| cohort_relative_predicted_calibrated10 | 0.676477 | 0.411050 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| cohort_relative_energy_calibrated10 | 0.677962 | 0.391897 |
| raw_plus_cohort_relative_full_calibrated10 | 0.678492 | 0.419254 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| cohort_relative_full_calibrated10 | 0.679152 | 0.403703 |
| cohort_relative_observed_calibrated10 | 0.679624 | 0.404343 |
| cohort_relative_energy | 0.696558 | 0.464403 |
| cohort_relative_predicted | 0.721511 | 0.504779 |
| existing_cohort_human_state | 0.766266 | 0.488759 |
| cohort_relative_full | 0.766885 | 0.468455 |
| cohort_relative_observed | 0.820386 | 0.472299 |
| raw_plus_cohort_relative_full | 1.147171 | 0.496542 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_plus_cohort_relative_full_calibrated10 | 0.665592 | 0.584905 |
| cohort_relative_observed_calibrated10 | 0.667238 | 0.572705 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| cohort_relative_predicted_calibrated10 | 0.668615 | 0.533023 |
| cohort_relative_full_calibrated10 | 0.669335 | 0.528330 |
| cohort_relative_energy_calibrated10 | 0.670142 | 0.531454 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| cohort_relative_energy | 0.678239 | 0.531454 |
| raw_plus_cohort_relative_full | 0.698338 | 0.584905 |
| cohort_relative_predicted | 0.705746 | 0.533023 |
| cohort_relative_observed | 0.711037 | 0.572705 |
| cohort_relative_full | 0.714741 | 0.528330 |
| raw_lifelog_pca | 0.715704 | 0.603053 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| raw_plus_cohort_relative_full | 0.563238 | 0.529206 | 0.034032 |
| cohort_relative_predicted | 0.552762 | 0.528063 | 0.024698 |
| cohort_relative_observed | 0.552889 | 0.528635 | 0.024254 |
| cohort_relative_full | 0.548952 | 0.532317 | 0.016635 |
| cohort_relative_energy | 0.535937 | 0.531302 | 0.004635 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| cohort_relative_observed | 0.962222 | 0.126667 | 0.835556 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| cohort_relative_full | 0.851111 | 0.126667 | 0.724444 |
| cohort_relative_predicted | 0.353333 | 0.126667 | 0.226667 |
| cohort_relative_energy | 0.346667 | 0.126667 | 0.220000 |

## Downstream Probe Candidate

- file: `submission_hsjepa_cohort_relative_world_model_probe_24fd334b_uploadsafe.csv`

이 파일은 HS-JEPA core 증거를 public에서 관측하기 위한 downstream probe candidate다.

## 해석

positive이면:

```text
cohort-relative human-state는 HS-JEPA core target으로 적합하다.
개인 내부 비교와 peer cohort 비교를 동시에 쓰면 label-free representation이 더 유용해진다.
```

주의:

```text
observed/full cohort geometry는 subject identity를 강하게 담는다.
따라서 core evidence는 observed state가 아니라 subject-heldout OOF predicted state에 둔다.
```

negative이면:

```text
cohort-relative geometry는 subject identity 또는 cohort shortcut을 담을 수 있지만,
Q/S label manifold로 안전하게 번역되지 않는다.
cohort는 core target보다 diagnostic/adapter로 남겨야 한다.
```
