# Listener-Conditioned Route Readout Core

## 한 줄 요약

HS-JEPA가 만든 route-preserving hidden bundle을 유지한 채,
각 target/listener가 어떤 route subspace를 읽는지 frozen probe로 진단한 실험이다.

```text
visible human-life context
  -> predicted routine-break / sleep-pressure / cohort-relative routes
  -> route-preserving HS-JEPA bundle
  -> target/listener-conditioned frozen readout
```

## 판정

- verdict: `listener_conditioned_readout_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- listener-conditioned delta vs prior: `-0.003246`
- listener-conditioned delta vs multi-target bundle: `-0.001747`
- selected route counts: `{'sleep_pressure_route': 2, 'multi_target_predicted': 1, 'sleep_cohort_pair': 1, 'routine_cohort_pair': 1, 'cohort_relative_route': 1, 'routine_break_route': 1}`

## 왜 이것이 HS-JEPA Core와 연결되는가

core는 여전히 label-free다.
Q/S label은 representation을 만든 뒤 frozen linear probe에서만 사용된다.

이 실험이 묻는 질문은 다음이다.

```text
HS-JEPA가 route axes를 보존했을 때,
각 target listener는 같은 route를 읽는가,
아니면 target마다 다른 hidden route를 읽는가?
```

## Target별 선택 route

| target | selected_feature_set | selected_logloss | multi_target_logloss | delta_vs_multi_target |
| --- | --- | --- | --- | --- |
| Q1 | multi_target_predicted | 0.702161 | 0.702161 | 0.000000 |
| Q2 | sleep_pressure_route | 0.690818 | 0.692763 | -0.001945 |
| Q3 | sleep_cohort_pair | 0.677841 | 0.678900 | -0.001059 |
| S1 | sleep_pressure_route | 0.641524 | 0.643910 | -0.002386 |
| S2 | routine_cohort_pair | 0.659829 | 0.662402 | -0.002573 |
| S3 | cohort_relative_route | 0.650004 | 0.653356 | -0.003352 |
| S4 | routine_break_route | 0.700102 | 0.701018 | -0.000915 |

## Fold Stability

선택된 route가 subject-heldout fold별로 multi-target bundle을 얼마나 자주 이기는지 본다.

| target | selected_feature_set | mean_delta_vs_multi_target | win_folds_vs_multi_target | total_folds |
| --- | --- | --- | --- | --- |
| Q1 | multi_target_predicted | 0.000000 | 0 | 5 |
| Q2 | sleep_pressure_route | -0.001970 | 4 | 5 |
| Q3 | sleep_cohort_pair | -0.001066 | 4 | 5 |
| S1 | sleep_pressure_route | -0.002370 | 5 | 5 |
| S2 | routine_cohort_pair | -0.002585 | 5 | 5 |
| S3 | cohort_relative_route | -0.003349 | 4 | 5 |
| S4 | routine_break_route | -0.000930 | 3 | 5 |

- total selected-route wins: `25 / 35`

## Frozen Subject-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| listener_conditioned_route_readout_calibrated10 | 0.674611 | 0.429447 |
| routine_cohort_pair_calibrated10 | 0.675826 | 0.416162 |
| sleep_cohort_pair_calibrated10 | 0.676238 | 0.412579 |
| multi_target_predicted_calibrated10 | 0.676358 | 0.411174 |
| cohort_relative_route_calibrated10 | 0.676477 | 0.411050 |
| routine_sleep_pair_calibrated10 | 0.677148 | 0.405195 |
| sleep_pressure_route_calibrated10 | 0.677266 | 0.405051 |
| routine_break_route_calibrated10 | 0.677581 | 0.401671 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| existing_cohort_human_state_calibrated10 | 0.678684 | 0.408091 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| routine_sleep_pair | 0.714780 | 0.495751 |
| multi_target_predicted | 0.715521 | 0.508003 |
| sleep_cohort_pair | 0.716891 | 0.508302 |
| routine_cohort_pair | 0.716983 | 0.515283 |
| cohort_relative_route | 0.721511 | 0.504779 |
| sleep_pressure_route | 0.722684 | 0.494996 |
| routine_break_route | 0.729714 | 0.490371 |
| existing_cohort_human_state | 0.766266 | 0.488759 |

## Chronological Row-Heldout Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| existing_cohort_human_state_calibrated10 | 0.667243 | 0.588222 |
| listener_conditioned_route_readout_calibrated10 | 0.668190 | 0.538378 |
| routine_cohort_pair_calibrated10 | 0.668341 | 0.536031 |
| cohort_relative_route_calibrated10 | 0.668615 | 0.533023 |
| multi_target_predicted_calibrated10 | 0.669005 | 0.526753 |
| sleep_cohort_pair_calibrated10 | 0.669449 | 0.525060 |
| routine_break_route_calibrated10 | 0.670340 | 0.508072 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| routine_sleep_pair_calibrated10 | 0.671111 | 0.496027 |
| sleep_pressure_route_calibrated10 | 0.671377 | 0.492233 |
| existing_cohort_human_state | 0.673190 | 0.588222 |
| cohort_relative_route | 0.705746 | 0.533023 |
| multi_target_predicted | 0.709419 | 0.526753 |
| routine_cohort_pair | 0.710324 | 0.536031 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| sleep_cohort_pair | 0.715909 | 0.525060 |
| routine_break_route | 0.728209 | 0.508072 |
| routine_sleep_pair | 0.733389 | 0.496027 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| cohort_relative_route | 0.353333 | 0.126667 | 0.226667 |
| listener_conditioned_selected_routes | 0.257778 | 0.126667 | 0.131111 |
| multi_target_predicted | 0.257778 | 0.126667 | 0.131111 |
| routine_break_route | 0.097778 | 0.126667 | -0.028889 |
| sleep_pressure_route | 0.093333 | 0.126667 | -0.033333 |

## Downstream Probe Candidate

- file: `submission_hsjepa_listener_conditioned_route_readout_probe_74befb45_uploadsafe.csv`

이 파일은 core evidence 자체가 아니라, target/listener-specific route readout을 competition label로 번역한 probe candidate다.

## 해석

positive이면:

```text
HS-JEPA route axes는 target/listener별로 다르게 읽혀야 한다.
하나의 global bundle보다 listener-conditioned route readout이 더 좋은 representation interface다.
```

negative이면:

```text
target별 route selection은 현재 validation에서는 과적합이거나 정보 손실이다.
route-preserving bundle 자체를 유지하고, listener-conditioned readout은 더 강한 split/nesting이 필요하다.
```
