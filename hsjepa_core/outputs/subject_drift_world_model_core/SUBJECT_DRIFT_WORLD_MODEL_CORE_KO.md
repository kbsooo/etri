# Subject-Drift World Model Core

## 한 줄 요약

이 실험은 HS-JEPA를 leaderboard adapter가 아니라 `미래 episode drift를 읽는 human-state world model`로 검증한다.

```text
visible lifelog context
  -> predict masked/future/cohort hidden human-state representation
  -> freeze representation
  -> probe: next local episode가 회복/악화/변화 방향으로 움직이는가?
```

## 판정

- verdict: `core_drift_weak_positive_boundary`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- drift window: previous/next `4` rows, min periods `2`
- low-trust probe shrink: `0.05, 0.1`

## 왜 이 실험이 논문적으로 중요한가

최근 public result에서 강하게 살아남은 것은 단순 row correction이 아니라 subject-level Q2/Q3 drift였다.
그렇다면 논문 관점의 질문은 다음으로 바뀐다.

```text
공개 점수 방정식 없이도, OG lifelog context만으로 이 사람의 다음 상태가
회복/악화 방향으로 움직이는지를 표현하는 latent를 만들 수 있는가?
```

이 실험은 그 질문을 core-only 형태로 찌른다.
HS-JEPA pretext는 label-free이며, label은 freeze된 representation을 읽는 probe target으로만 쓰인다.

## HS-JEPA Contract

```text
Context = calendar / phone / body / app-social / mobility-environment views
Hidden target = masked view state + next-episode state + cohort-relative state
Predictor = subject-heldout ridge JEPA predictor
Energy = hidden state prediction residual and cohort/personal normal distance
Probe = subject-heldout drift readout, not core training
```

## Pretext 결과

- best pretext target: `phone_behavior`
- best component-corr lift vs null: `0.486474`
- best R2 lift vs null: `0.362343`

| variant | task | target | component_corr | null_component_corr | component_corr_lift_vs_null | r2_lift_vs_null |
| --- | --- | --- | --- | --- | --- | --- |
| subject_relative | masked_context_to_view_state | phone_behavior | 0.482254 | -0.004220 | 0.486474 | 0.362343 |
| subject_relative | masked_context_to_view_state | mobility_environment | 0.407046 | 0.036086 | 0.370959 | 0.297949 |
| absolute | masked_context_to_view_state | app_social_context | 0.182834 | -0.164661 | 0.347494 | 0.139273 |
| subject_relative | masked_context_to_view_state | app_social_context | 0.327764 | 0.008008 | 0.319756 | 0.348920 |
| subject_relative | masked_context_to_view_state | body_activity_sleep | 0.307958 | 0.002570 | 0.305388 | 0.259197 |
| absolute | masked_context_to_view_state | body_activity_sleep | 0.195134 | -0.041579 | 0.236713 | 12.268517 |
| absolute | masked_context_to_view_state | phone_behavior | 0.199755 | -0.027113 | 0.226868 | 26.963841 |
| absolute | masked_context_to_view_state | mobility_environment | 0.064641 | -0.122780 | 0.187421 | 11.001318 |
| absolute | current_context_to_future_state | next_subject_episode | 0.129269 | -0.054072 | 0.183341 | 3.059427 |
| subject_relative | current_context_to_future_state | next_subject_episode | 0.034659 | -0.035158 | 0.069817 | 0.066599 |
| subject_relative | masked_context_to_view_state | calendar_rhythm | 0.089124 | 0.026701 | 0.062423 | 0.055447 |
| absolute | masked_context_to_view_state | calendar_rhythm | 0.004055 | 0.011269 | -0.007214 | 4.701222 |

## Drift Probe Targets

| probe_target | positive_rate | valid_rows | has_two_classes |
| --- | --- | --- | --- |
| recovery_up_subjective | 0.434146 | 410 | True |
| intervention_relief_Q2 | 0.321951 | 410 | True |
| intervention_worsening_Q2 | 0.400000 | 410 | True |
| quality_rise_Q3 | 0.407317 | 410 | True |
| objective_stage_shift | 0.958537 | 410 | True |
| drift_up_Q1 | 0.392683 | 410 | True |
| drift_down_Q1 | 0.326829 | 410 | True |
| drift_up_Q2 | 0.400000 | 410 | True |
| drift_down_Q2 | 0.321951 | 410 | True |
| drift_up_Q3 | 0.407317 | 410 | True |
| drift_down_Q3 | 0.348780 | 410 | True |
| drift_up_S1 | 0.341463 | 410 | True |
| drift_down_S1 | 0.324390 | 410 | True |
| drift_up_S2 | 0.312195 | 410 | True |
| drift_down_S2 | 0.302439 | 410 | True |
| drift_up_S3 | 0.307317 | 410 | True |
| drift_down_S3 | 0.319512 | 410 | True |
| drift_up_S4 | 0.385366 | 410 | True |
| drift_down_S4 | 0.336585 | 410 | True |

## Subject-Heldout Drift Probe

이 표는 같은 subject가 train/validation 양쪽에 동시에 들어가지 않도록 만든다.
즉 subject identity만 외운 표현은 여기서 살아남기 어렵다.
`_calibrated05`와 `_calibrated10`은 fold prior에서 각각 5%, 10%만 움직이는 고정 low-trust readout이다.
representation ranking과 probability overconfidence를 분리하기 위한 장치이며 public LB는 쓰지 않는다.

| feature_set | logloss | auc | average_precision |
| --- | --- | --- | --- |
| calendar_rhythm_calibrated10 | 0.625950 | 0.438778 | 0.361954 |
| subject_relative_hsjepa_predicted_calibrated05 | 0.626024 | 0.437453 | 0.363363 |
| calendar_rhythm_calibrated05 | 0.626045 | 0.432156 | 0.359075 |
| subject_relative_hsjepa_predicted_calibrated10 | 0.626104 | 0.450389 | 0.371733 |
| prior_only | 0.626192 | 0.426453 | 0.356078 |
| prior_only_calibrated10 | 0.626192 | 0.426453 | 0.356078 |
| prior_only_calibrated05 | 0.626192 | 0.426453 | 0.356078 |
| raw_lifelog_pca_calibrated05 | 0.626203 | 0.434553 | 0.361939 |
| absolute_hsjepa_predicted_calibrated05 | 0.626348 | 0.437757 | 0.363406 |
| subject_relative_hsjepa_energy_calibrated05 | 0.626499 | 0.424934 | 0.355249 |
| subject_relative_hsjepa_full_calibrated05 | 0.626499 | 0.424934 | 0.355249 |
| raw_lifelog_pca_calibrated10 | 0.626615 | 0.447940 | 0.371436 |
| existing_human_state_features_calibrated05 | 0.626644 | 0.424547 | 0.355097 |
| raw_plus_subject_relative_hsjepa_calibrated05 | 0.626774 | 0.426052 | 0.355337 |
| absolute_hsjepa_predicted_calibrated10 | 0.626865 | 0.447537 | 0.371257 |
| subject_relative_hsjepa_full_calibrated10 | 0.626972 | 0.432287 | 0.359393 |
| subject_relative_hsjepa_energy_calibrated10 | 0.626972 | 0.432287 | 0.359393 |
| hybrid_absolute_relative_hsjepa_calibrated05 | 0.626977 | 0.425192 | 0.352849 |
| absolute_hsjepa_full_calibrated05 | 0.626979 | 0.427726 | 0.354846 |
| existing_human_state_features_calibrated10 | 0.627278 | 0.430943 | 0.357329 |

## Chronological Drift Probe

각 subject의 앞쪽 episode로 학습하고 뒤쪽 episode의 drift를 읽는다.

| feature_set | logloss | auc | average_precision |
| --- | --- | --- | --- |
| subject_relative_hsjepa_predicted_calibrated10 | 0.625324 | 0.506142 | 0.429210 |
| subject_relative_hsjepa_predicted_calibrated05 | 0.625509 | 0.506142 | 0.429210 |
| prior_only | 0.625919 | 0.500000 | 0.386924 |
| prior_only_calibrated10 | 0.625919 | 0.500000 | 0.386924 |
| prior_only_calibrated05 | 0.625919 | 0.500000 | 0.386924 |
| subject_relative_hsjepa_full_calibrated05 | 0.626108 | 0.490564 | 0.407603 |
| subject_relative_hsjepa_energy_calibrated05 | 0.626108 | 0.490564 | 0.407603 |
| calendar_rhythm_calibrated05 | 0.626229 | 0.462951 | 0.393783 |
| raw_plus_subject_relative_hsjepa_calibrated05 | 0.626249 | 0.491345 | 0.402692 |
| hybrid_absolute_relative_hsjepa_calibrated05 | 0.626251 | 0.485659 | 0.399831 |
| existing_human_state_features_calibrated05 | 0.626282 | 0.470843 | 0.395749 |
| absolute_hsjepa_predicted_calibrated05 | 0.626287 | 0.487290 | 0.396147 |
| raw_lifelog_pca_calibrated05 | 0.626383 | 0.489112 | 0.406036 |
| subject_relative_hsjepa_full_calibrated10 | 0.626494 | 0.490564 | 0.407603 |
| subject_relative_hsjepa_energy_calibrated10 | 0.626494 | 0.490564 | 0.407603 |
| calendar_rhythm_calibrated10 | 0.626622 | 0.462951 | 0.393783 |
| absolute_hsjepa_full_calibrated05 | 0.626724 | 0.469959 | 0.378686 |
| existing_human_state_features_calibrated10 | 0.626737 | 0.470843 | 0.395749 |
| raw_plus_subject_relative_hsjepa_calibrated10 | 0.626770 | 0.491345 | 0.402692 |
| hybrid_absolute_relative_hsjepa_calibrated10 | 0.626791 | 0.485659 | 0.399831 |

## Q2/Q3 Drift Focus

최근 강한 public result가 Q2/Q3 subject-drift와 연결되어 있으므로, Q2/Q3 route만 따로 본다.

| probe_target | feature_set | logloss | auc | average_precision |
| --- | --- | --- | --- | --- |
| drift_down_Q2 | absolute_hsjepa_predicted_calibrated10 | 0.628788 | 0.499646 | 0.322122 |
| drift_down_Q2 | absolute_hsjepa_predicted_calibrated05 | 0.629147 | 0.487383 | 0.307909 |
| drift_down_Q2 | raw_lifelog_pca_calibrated05 | 0.629544 | 0.461876 | 0.313859 |
| drift_down_Q2 | prior_only | 0.629643 | 0.465173 | 0.303225 |
| drift_down_Q2 | prior_only_calibrated05 | 0.629643 | 0.465173 | 0.303225 |
| drift_down_Q2 | prior_only_calibrated10 | 0.629643 | 0.465173 | 0.303225 |
| drift_down_Q2 | raw_lifelog_pca_calibrated10 | 0.629746 | 0.479998 | 0.323721 |
| drift_down_Q2 | existing_human_state_features_calibrated05 | 0.629893 | 0.470160 | 0.312828 |
| drift_down_Q2 | calendar_rhythm_calibrated05 | 0.630032 | 0.443986 | 0.284744 |
| drift_down_Q2 | subject_relative_hsjepa_predicted_calibrated05 | 0.630248 | 0.463702 | 0.289965 |
| drift_down_Q2 | hybrid_absolute_relative_hsjepa_calibrated05 | 0.630300 | 0.446261 | 0.295316 |
| drift_down_Q2 | existing_human_state_features_calibrated10 | 0.630313 | 0.473594 | 0.315269 |
| drift_down_Q2 | calendar_rhythm_calibrated10 | 0.630447 | 0.441669 | 0.283685 |
| drift_down_Q2 | raw_plus_subject_relative_hsjepa_calibrated05 | 0.630504 | 0.441193 | 0.293515 |
| drift_down_Q2 | subject_relative_hsjepa_energy_calibrated05 | 0.630573 | 0.438113 | 0.295332 |
| drift_down_Q2 | subject_relative_hsjepa_full_calibrated05 | 0.630573 | 0.438113 | 0.295332 |
| drift_down_Q2 | absolute_hsjepa_full_calibrated05 | 0.630878 | 0.449204 | 0.294273 |
| drift_down_Q2 | subject_relative_hsjepa_predicted_calibrated10 | 0.631088 | 0.468389 | 0.292203 |
| drift_down_Q2 | hybrid_absolute_relative_hsjepa_calibrated10 | 0.631099 | 0.444272 | 0.292773 |
| drift_down_Q2 | raw_plus_subject_relative_hsjepa_calibrated10 | 0.631583 | 0.442773 | 0.294235 |
| drift_down_Q2 | subject_relative_hsjepa_energy_calibrated10 | 0.631629 | 0.437541 | 0.292495 |
| drift_down_Q2 | subject_relative_hsjepa_full_calibrated10 | 0.631629 | 0.437541 | 0.292495 |
| drift_down_Q2 | absolute_hsjepa_full_calibrated10 | 0.632403 | 0.449886 | 0.295495 |
| drift_down_Q2 | calendar_rhythm | 0.643542 | 0.454314 | 0.285235 |
| drift_down_Q2 | absolute_hsjepa_predicted | 0.654125 | 0.532129 | 0.346389 |
| drift_down_Q2 | existing_human_state_features | 0.669298 | 0.484658 | 0.333441 |
| drift_down_Q2 | subject_relative_hsjepa_energy | 0.675745 | 0.451984 | 0.305631 |
| drift_down_Q2 | subject_relative_hsjepa_full | 0.675745 | 0.451984 | 0.305631 |

## Drift Magnitude Regression

binary direction뿐 아니라 drift magnitude 자체를 읽을 수 있는지도 본다.

| feature_set | regression_target | corr | mae | null_mae | mae_lift_vs_null |
| --- | --- | --- | --- | --- | --- |
| calendar_rhythm | drift_Q3 | 0.051503 | 0.302817 | 0.299702 | -0.003115 |
| calendar_rhythm | drift_Q2 | -0.080115 | 0.302174 | 0.298713 | -0.003461 |
| calendar_rhythm | drift_subjective_recovery | 0.065338 | 0.449724 | 0.443516 | -0.006208 |
| existing_human_state_features | drift_Q2 | -0.098131 | 0.308158 | 0.298713 | -0.009445 |
| existing_human_state_features | drift_Q3 | 0.033159 | 0.312712 | 0.299702 | -0.013010 |
| subject_relative_hsjepa_predicted | drift_subjective_recovery | 0.038141 | 0.459949 | 0.443516 | -0.016434 |
| existing_human_state_features | drift_subjective_recovery | 0.123223 | 0.461430 | 0.443516 | -0.017914 |
| subject_relative_hsjepa_predicted | drift_Q3 | 0.001005 | 0.317799 | 0.299702 | -0.018097 |
| subject_relative_hsjepa_predicted | drift_Q2 | -0.010101 | 0.326046 | 0.298713 | -0.027333 |
| subject_relative_hsjepa_full | drift_subjective_recovery | 0.063845 | 0.479105 | 0.443516 | -0.035590 |
| subject_relative_hsjepa_energy | drift_subjective_recovery | 0.063845 | 0.479105 | 0.443516 | -0.035590 |
| subject_relative_hsjepa_energy | drift_Q3 | -0.001747 | 0.338005 | 0.299702 | -0.038303 |
| subject_relative_hsjepa_full | drift_Q3 | -0.001747 | 0.338005 | 0.299702 | -0.038303 |
| absolute_hsjepa_full | drift_Q3 | -0.005903 | 0.338457 | 0.299702 | -0.038755 |
| subject_relative_hsjepa_energy | drift_Q2 | -0.111335 | 0.355724 | 0.298713 | -0.057011 |
| subject_relative_hsjepa_full | drift_Q2 | -0.111335 | 0.355724 | 0.298713 | -0.057011 |
| absolute_hsjepa_predicted | drift_Q2 | -0.000311 | 0.398318 | 0.298713 | -0.099604 |
| hybrid_absolute_relative_hsjepa | drift_Q3 | -0.024570 | 0.478661 | 0.299702 | -0.178959 |

## 현재 해석

현재 결과는 `subject_relative_hsjepa_predicted_calibrated05`가 subject-heldout drift에서 prior보다
`-0.000168` 낮은 logloss를 보인다는 뜻이다.
하지만 효과가 0.001보다 작고 calendar low-trust readout이 전체 best이므로,
이 결과는 큰 core breakthrough가 아니라 `weak positive boundary`로 해석한다.

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA는 label classifier가 아니라, 미래 human-state drift를 표현하는 world model이다.
visible lifelog context에서 만든 hidden representation은 subject-heldout 조건에서도
회복/악화 episode를 더 선형적으로 읽게 만든다.
```

negative이면 경계도 명확하다.

```text
public에서 살아남은 subject drift correction은 아직 core representation만으로 복원되지 않았다.
그 경우 drift consistency는 competition adapter/certifier 영역이고,
core contribution은 masked/future state prediction과 listener responsibility에 머문다.
```
