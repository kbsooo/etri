# Routine-Break World Model Core

## 한 줄 요약

HS-JEPA의 hidden target을 단순 masked-view state에서 한 단계 바꾸어,
사람의 루틴 붕괴와 episode reset을 label 없이 예측하는 world model로 만든 실험이다.

```text
visible human-life context
  -> subject-relative deviation / transition / personal-baseline residual
  -> hidden routine-break representation
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `core_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label이나 public LB를 target으로 삼지 않는다.
target은 다음 세 가지로 만든 hidden human-state representation이다.

1. subject-relative current state
2. previous episode에서 현재 episode로 넘어온 jump
3. 개인 rolling baseline에서 벗어난 routine-break residual

따라서 이 실험의 질문은 다음이다.

```text
보이는 생활 context만으로
보이지 않는 루틴 붕괴/episode reset 표현을 예측할 수 있는가?
```

## Pretext 결과

- best pretext task: `masked_context_to_routine_break_view`
- best target: `mobility_environment`
- best component-corr lift vs null: `0.424933`
- best R2 lift vs null: `0.267127`

| task | target | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| masked_context_to_routine_break_view | mobility_environment | 0.409478 | -0.015455 | 0.424933 | 0.267127 |
| masked_context_to_routine_break_view | app_social_context | 0.354501 | -0.016740 | 0.371241 | 0.280137 |
| masked_context_to_routine_break_view | phone_behavior | 0.373832 | 0.026643 | 0.347189 | 0.223796 |
| current_context_to_next_routine_break | next_episode_routine_break | 0.233078 | 0.001825 | 0.231253 | 0.137994 |
| masked_context_to_routine_break_view | body_activity_sleep | 0.219674 | 0.015677 | 0.203998 | 0.185771 |
| masked_context_to_routine_break_view | calendar_rhythm | 0.110584 | 0.029910 | 0.080674 | 0.039982 |

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

| feature_set | logloss | auc |
| --- | --- | --- |
| routine_break_full_calibrated10 | 0.676185 | 0.412776 |
| raw_plus_routine_break_full_calibrated10 | 0.676382 | 0.416578 |
| routine_break_predicted_calibrated10 | 0.677581 | 0.401671 |
| routine_break_observed_calibrated10 | 0.677803 | 0.391011 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| routine_break_energy_calibrated10 | 0.677993 | 0.385292 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| routine_break_observed | 0.690880 | 0.463427 |
| routine_break_energy | 0.696678 | 0.456886 |
| routine_break_full | 0.703622 | 0.513628 |
| routine_break_predicted | 0.729714 | 0.490371 |
| existing_cohort_human_state | 0.766266 | 0.488759 |
| raw_plus_routine_break_full | 1.016836 | 0.513087 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_plus_routine_break_full_calibrated10 | 0.665202 | 0.604679 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| routine_break_full_calibrated10 | 0.669556 | 0.533246 |
| routine_break_energy_calibrated10 | 0.670171 | 0.514486 |
| routine_break_observed_calibrated10 | 0.670336 | 0.519252 |
| routine_break_predicted_calibrated10 | 0.670340 | 0.508072 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| raw_plus_routine_break_full | 0.678948 | 0.604679 |
| routine_break_observed | 0.682638 | 0.519252 |
| routine_break_energy | 0.689987 | 0.514486 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| routine_break_full | 0.716948 | 0.533246 |
| routine_break_predicted | 0.728209 | 0.508072 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| raw_plus_routine_break_full | 0.571048 | 0.529206 | 0.041841 |
| routine_break_predicted | 0.538857 | 0.528063 | 0.010794 |
| routine_break_full | 0.542286 | 0.532317 | 0.009968 |
| routine_break_observed | 0.537714 | 0.528635 | 0.009079 |
| routine_break_energy | 0.531746 | 0.531302 | 0.000444 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| routine_break_observed | 0.211111 | 0.126667 | 0.084444 |
| routine_break_full | 0.164444 | 0.126667 | 0.037778 |
| routine_break_energy | 0.106667 | 0.126667 | -0.020000 |
| routine_break_predicted | 0.097778 | 0.126667 | -0.028889 |

## Downstream Probe Candidate

- file: `submission_hsjepa_routine_break_world_model_probe_1cc38f16_uploadsafe.csv`

이 파일은 HS-JEPA core 증거가 아니라 downstream probe candidate다.

## 해석

positive이면:

```text
루틴 붕괴/episode reset은 HS-JEPA core target으로 적합하며,
subject-relative world model보다 더 강한 label-free human-state representation이다.
```

negative이면:

```text
루틴 붕괴 target은 예측 가능하더라도 Q/S label manifold로 잘 번역되지 않는다.
다음 core target은 sleep-stage-like hidden factor 쪽으로 옮겨야 한다.
```
