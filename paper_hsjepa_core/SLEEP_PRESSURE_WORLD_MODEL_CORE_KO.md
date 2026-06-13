# Sleep-Pressure World Model Core

## 한 줄 요약

HS-JEPA의 hidden target을 `수면 label`이 아니라 label-free sleep-pressure surrogate로 만든 실험이다.

```text
visible daily human-life context
  -> hidden sleep-pressure / arousal / recovery-load representation
  -> frozen low-trust Q/S probe
```

## 판정

- verdict: `core_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 HS-JEPA Core인가

이 실험은 Q/S label을 직접 예측하지 않는다.
target representation은 다음 label-free human-state surrogate에서 나온다.

1. night disturbance
2. physiological load
3. social/cognitive arousal
4. rest-environment stability
5. calendar routine pressure

즉 질문은 다음이다.

```text
낮 동안 보이는 생활 context만으로
그날 밤의 숨은 sleep-pressure 표현을 예측할 수 있는가?
```

## Pretext 결과

- best pretext task: `masked_context_to_sleep_pressure_family`
- best target: `social_cognitive_arousal`
- best component-corr lift vs null: `0.563048`
- best R2 lift vs null: `0.499132`

| task | target | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| masked_context_to_sleep_pressure_family | social_cognitive_arousal | 0.585739 | 0.022691 | 0.563048 | 0.499132 |
| masked_context_to_sleep_pressure_family | rest_environment_stability | 0.444959 | -0.018689 | 0.463648 | 0.366696 |
| masked_context_to_sleep_pressure_family | physiological_load | 0.313664 | 0.002845 | 0.310819 | 0.232742 |
| current_context_to_next_sleep_pressure | next_sleep_pressure_state | 0.215894 | 0.011108 | 0.204786 | 0.095942 |
| masked_context_to_sleep_pressure_family | night_disturbance | 0.160856 | -0.014264 | 0.175119 | 0.047803 |
| masked_context_to_sleep_pressure_family | calendar_routine_pressure | 0.117262 | 0.026575 | 0.090688 | 0.050868 |

## Frozen Subject-Heldout Probe

`_calibrated10`은 fold prior에서 10%만 움직이는 fixed low-trust probe다.

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_plus_sleep_pressure_full_calibrated10 | 0.676588 | 0.414241 |
| sleep_pressure_full_calibrated10 | 0.676990 | 0.405260 |
| sleep_pressure_predicted_calibrated10 | 0.677266 | 0.405051 |
| sleep_pressure_observed_calibrated10 | 0.677467 | 0.392188 |
| sleep_pressure_energy_calibrated10 | 0.677588 | 0.395356 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| sleep_pressure_energy | 0.692204 | 0.472252 |
| sleep_pressure_observed | 0.692324 | 0.470147 |
| sleep_pressure_full | 0.709677 | 0.497753 |
| sleep_pressure_predicted | 0.722684 | 0.494996 |
| existing_cohort_human_state | 0.766266 | 0.488759 |
| raw_plus_sleep_pressure_full | 0.977087 | 0.508476 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_plus_sleep_pressure_full_calibrated10 | 0.666039 | 0.589777 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| sleep_pressure_full_calibrated10 | 0.669543 | 0.524929 |
| sleep_pressure_observed_calibrated10 | 0.669925 | 0.526917 |
| sleep_pressure_energy_calibrated10 | 0.670252 | 0.532942 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| sleep_pressure_predicted_calibrated10 | 0.671377 | 0.492233 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| sleep_pressure_observed | 0.679087 | 0.526917 |
| sleep_pressure_energy | 0.691240 | 0.532942 |
| raw_plus_sleep_pressure_full | 0.694723 | 0.589777 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| sleep_pressure_full | 0.720043 | 0.524929 |
| sleep_pressure_predicted | 0.742424 | 0.492233 |

## Nearest-Neighbor State Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.580571 | 0.530794 | 0.049778 |
| existing_cohort_human_state | 0.577333 | 0.528127 | 0.049206 |
| raw_plus_sleep_pressure_full | 0.562349 | 0.529206 | 0.033143 |
| sleep_pressure_predicted | 0.539556 | 0.528063 | 0.011492 |
| sleep_pressure_full | 0.531111 | 0.532317 | -0.001206 |
| sleep_pressure_observed | 0.527175 | 0.528635 | -0.001460 |
| sleep_pressure_energy | 0.522032 | 0.531302 | -0.009270 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |
| existing_cohort_human_state | 0.913333 | 0.126667 | 0.786667 |
| sleep_pressure_observed | 0.275556 | 0.126667 | 0.148889 |
| sleep_pressure_energy | 0.151111 | 0.126667 | 0.024444 |
| sleep_pressure_full | 0.137778 | 0.126667 | 0.011111 |
| sleep_pressure_predicted | 0.093333 | 0.126667 | -0.033333 |

## Downstream Probe Candidate

- file: `submission_hsjepa_sleep_pressure_world_model_probe_2ed37b9a_uploadsafe.csv`

이 파일은 HS-JEPA core 증거를 public에서 관측하기 위한 downstream probe candidate다.

## 해석

positive이면:

```text
sleep-pressure surrogate는 HS-JEPA core target으로 적합하다.
인간 생활 context에서 수면 압력/회복부하 representation을 label 없이 만들 수 있다.
```

negative이면:

```text
sleep-pressure surrogate는 예측 가능해도 Q/S label manifold로 잘 번역되지 않는다.
다음 target은 sleep pressure 자체가 아니라 listener responsibility 또는 target-route hidden state여야 한다.
```
