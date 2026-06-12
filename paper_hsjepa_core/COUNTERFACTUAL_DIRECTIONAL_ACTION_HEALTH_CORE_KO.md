# Counterfactual Directional Action-Health Core

## 한 줄 요약

action-free vulnerability는 `위험한 상태인가`는 어느 정도 읽었지만, 어떤 방향의
action이 안전한지는 고르지 못했다. 이번 실험은 확률값이나 action magnitude를 보지 않고,
오직 `이 target을 올릴까/내릴까`라는 counterfactual direction listener만 주고
hidden action-health representation을 예측한다.

```text
visible human-state context + counterfactual direction listener
  -> hidden directional action-health / toxic-tail representation
  -> masked-view consensus
  -> row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 정확히는 **HS-JEPA core가 counterfactual action listener를 조건으로
보이지 않는 action-health representation을 예측하는지 검증하는 core-decoder boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 human-state context와 action direction listener만으로
보이지 않는 row-target action-health representation을 예측할 수 있는가?
```

action probability, action magnitude, support score, public LB ledger는 encoder에 넣지 않는다.
따라서 `좋은 제출값을 후처리했다`보다 `human-state에서 counterfactual action의 건강성을 예측했다`는
주장에 더 가깝다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- action probability as feature: `False`
- action magnitude as feature: `False`

## Verdict

- verdict: `counterfactual_directional_action_health_oof_positive_subjectheldout_fragile`
- full OOF selected gain: `3.026331`
- nested heldout gain: `-3.515635`
- stable targets: `[]`
- stable OOF gain: `0.000000`
- candidate policy source: `full_oof_sensor`
- released test cells: `36`

## Directional View Metrics

| view | feature_count | gain_mae | tail_mae | health_auc | health_ap | toxic_auc | toxic_ap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_directional_context | 495 | 0.184999 | 0.131191 | 0.531787 | 0.524548 | 0.533477 | 0.429877 |
| mask_world_state | 87 | 0.183946 | 0.131829 | 0.530838 | 0.521281 | 0.517546 | 0.419157 |
| mask_episode_context | 453 | 0.185987 | 0.136799 | 0.541330 | 0.529397 | 0.525615 | 0.425798 |
| mask_listener_interaction | 121 | 0.183488 | 0.131237 | 0.518579 | 0.513037 | 0.520658 | 0.412606 |
| mask_direction_listener | 469 | 0.173121 | 0.128225 | 0.500000 | 0.500000 | 0.538078 | 0.428467 |
| directional_consensus | 1625 | 0.180955 | 0.131151 | 0.539598 | 0.528134 | 0.538226 | 0.428788 |

## Direction Target Summary

| target | direction | cells | mean_gain | positive_gain_rate | toxic_tail_rate | mean_abs_action_move |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | down | 450 | -0.009529 | 0.504444 | 0.384444 | 0.070052 |
| Q1 | up | 450 | -0.021700 | 0.495556 | 0.415556 | 0.075646 |
| Q2 | down | 450 | -0.028541 | 0.437778 | 0.493333 | 0.095688 |
| Q2 | up | 450 | -0.018467 | 0.562222 | 0.371111 | 0.084120 |
| Q3 | down | 450 | -0.017749 | 0.400000 | 0.473333 | 0.068225 |
| Q3 | up | 450 | -0.023268 | 0.600000 | 0.320000 | 0.074613 |
| S1 | down | 450 | -0.017768 | 0.317778 | 0.506667 | 0.081187 |
| S1 | up | 450 | -0.035275 | 0.682222 | 0.284444 | 0.082506 |
| S2 | down | 450 | -0.023010 | 0.348889 | 0.526667 | 0.103000 |
| S2 | up | 450 | -0.033322 | 0.651111 | 0.306667 | 0.088040 |
| S3 | down | 450 | -0.019290 | 0.337778 | 0.504444 | 0.086274 |
| S3 | up | 450 | -0.038257 | 0.662222 | 0.315556 | 0.074417 |
| S4 | down | 450 | -0.015437 | 0.440000 | 0.395556 | 0.074079 |
| S4 | up | 450 | -0.012699 | 0.560000 | 0.348889 | 0.065091 |

## View Disagreement By Target

| target | mean_disagreement | median_disagreement | mean_abs_gain | toxic_tail_rate |
| --- | --- | --- | --- | --- |
| Q1 | 0.042646 | 0.040589 | 0.149887 | 0.400000 |
| Q2 | 0.054767 | 0.052030 | 0.186684 | 0.432222 |
| Q3 | 0.055044 | 0.051498 | 0.148881 | 0.396667 |
| S1 | 0.077734 | 0.069753 | 0.175385 | 0.395556 |
| S2 | 0.070585 | 0.063947 | 0.201806 | 0.416667 |
| S3 | 0.071955 | 0.065142 | 0.173793 | 0.410000 |
| S4 | 0.050473 | 0.046270 | 0.143513 | 0.372222 |

## Episode Feature Summary

| feature | train_mean | train_std | test_mean | test_std |
| --- | --- | --- | --- | --- |
| episode_action_pressure_max | 0.190830 | 0.052829 | 0.221676 | 0.060017 |
| episode_action_pressure_max_delta_next | 0.000192 | 0.069602 | -0.000451 | 0.072986 |
| episode_action_pressure_max_delta_prev | 0.000192 | 0.069602 | -0.000451 | 0.072986 |
| episode_action_pressure_max_subject_rank | 0.511111 | 0.288609 | 0.520000 | 0.288426 |
| episode_action_pressure_max_subject_z | 0.001225 | 1.010786 | -0.048986 | 1.007303 |
| episode_action_pressure_mean | 0.091668 | 0.027839 | 0.107973 | 0.035577 |
| episode_action_pressure_mean_delta_next | -0.000395 | 0.036615 | 0.000457 | 0.036605 |
| episode_action_pressure_mean_delta_prev | -0.000395 | 0.036615 | 0.000457 | 0.036605 |
| episode_action_pressure_mean_subject_rank | 0.511111 | 0.288609 | 0.520000 | 0.288456 |
| episode_action_pressure_mean_subject_z | 0.102452 | 1.004911 | 0.007799 | 1.022904 |
| episode_context_score | 0.479000 | 0.193834 | 0.480200 | 0.202345 |
| episode_energy_max | 20.359430 | 58.300934 | 2.048499 | 1.589336 |
| episode_energy_max_delta_next | -0.090306 | 20.302094 | -0.028267 | 2.114975 |
| episode_energy_max_delta_prev | -0.090306 | 20.302094 | -0.028267 | 2.114975 |
| episode_energy_max_subject_rank | 0.511111 | 0.288609 | 0.520000 | 0.288456 |
| episode_energy_max_subject_z | 0.210462 | 1.008458 | 0.303115 | 1.003036 |
| episode_energy_mean | 5.836193 | 15.470217 | 0.926190 | 0.426041 |
| episode_energy_mean_delta_next | -0.018887 | 5.385593 | -0.009016 | 0.536894 |
| episode_energy_mean_delta_prev | -0.018887 | 5.385593 | -0.009016 | 0.536894 |
| episode_energy_mean_subject_rank | 0.511111 | 0.288609 | 0.520000 | 0.288456 |

## Full OOF Chosen Policies

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | directional_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | directional_gain_mean | top_decisive | 0.080000 | 27 | 0.626455 | 0.555556 | 5 | 3 | 1.505096 | 0.046716 | positive_counterfactual_directional_action_health |
| Q2 | True | directional_action_health_score | top_all | 0.040000 | 18 | 0.796315 | 0.611111 | 5 | 2 | 2.035608 | 1.458855 | positive_counterfactual_directional_action_health |
| Q3 | True | directional_action_health_score | top_all | 0.020000 | 9 | 0.219561 | 0.666667 | 3 | 1 | 0.500611 | 0.448349 | positive_counterfactual_directional_action_health |
| S1 | True | directional_health_only_score | top_all | 0.010000 | 4 | 0.659670 | 1.000000 | 2 | 0 | 0.806172 | 1.996442 | positive_counterfactual_directional_action_health |
| S2 | True | directional_action_health_score | top_decisive | 0.020000 | 7 | 0.044445 | 0.571429 | 2 | 3 | 0.157921 | -2.109509 | positive_counterfactual_directional_action_health |
| S3 | False | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_counterfactual_directional_policy_passed |
| S4 | True | directional_gain_mean | top_all | 0.010000 | 4 | 0.679884 | 1.000000 | 2 | 0 | 0.706911 | 2.017098 | positive_counterfactual_directional_action_health |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 6 | -0.519069 | -0.086511 | 0.500000 | Q1,Q2,Q3,S1,S4 |
| id02 | 11 | 0.108439 | 0.009858 | 0.454545 | Q1,Q2,Q3,S1,S2,S4 |
| id03 | 13 | 0.149206 | 0.011477 | 0.461538 | Q1,Q2,Q3,S1,S2,S4 |
| id04 | 12 | 0.184763 | 0.015397 | 0.583333 | Q1,Q2,Q3,S1,S2,S4 |
| id05 | 10 | -1.066457 | -0.106646 | 0.300000 | Q1,Q2,Q3,S1,S2,S4 |
| id06 | 9 | 0.354323 | 0.039369 | 0.555556 | Q1,Q2,Q3,S1,S2,S4 |
| id07 | 8 | -0.344453 | -0.043057 | 0.625000 | Q1,Q2,Q3,S1,S2,S4 |
| id08 | 20 | -2.003807 | -0.100190 | 0.300000 | Q1,Q2,Q3,S1,S2,S4 |
| id09 | 11 | -0.939570 | -0.085415 | 0.272727 | Q1,Q2,Q3,S1,S2,S4 |
| id10 | 6 | 0.560989 | 0.093498 | 1.000000 | Q1,Q2,Q3,S1,S2,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 24 | -0.137288 | -0.005720 | 0.458333 | 10.000000 | 14.000000 | 6 | 4 |
| Q2 | 25 | -1.229831 | -0.049193 | 0.320000 | 9.000000 | 16.000000 | 6 | 4 |
| Q3 | 11 | -0.184179 | -0.016744 | 0.545455 | 6.000000 | 5.000000 | 6 | 4 |
| S1 | 10 | -1.065167 | -0.106517 | 0.600000 | 5.000000 | 5.000000 | 6 | 4 |
| S2 | 26 | -0.673420 | -0.025901 | 0.461538 | 7.000000 | 19.000000 | 4 | 5 |
| S4 | 10 | -0.225750 | -0.022575 | 0.600000 | 5.000000 | 5.000000 | 6 | 4 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | directional_gain_mean | hold | 0.000000 | 1.000000 | -0.137288 | 6 | 4 | 0.458333 | failed_counterfactual_directional_stress |
| Q2 | False | directional_action_health_score | hold | 0.000000 | 1.000000 | -1.229831 | 6 | 4 | 0.320000 | failed_counterfactual_directional_stress |
| Q3 | False | directional_action_health_score | hold | 0.000000 | 1.000000 | -0.184179 | 6 | 4 | 0.545455 | failed_counterfactual_directional_stress |
| S1 | False | directional_health_only_score | hold | 0.000000 | 1.000000 | -1.065167 | 6 | 4 | 0.600000 | failed_counterfactual_directional_stress |
| S2 | False | directional_action_health_score | hold | 0.000000 | 0.900000 | -0.673420 | 4 | 5 | 0.461538 | failed_counterfactual_directional_stress |
| S3 | False | directional_action_health_score | hold | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 | failed_counterfactual_directional_stress |
| S4 | False | directional_gain_mean | hold | 0.000000 | 1.000000 | -0.225750 | 6 | 4 | 0.600000 | failed_counterfactual_directional_stress |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | directional_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | directional_gain_mean | top_all | 0.010000 | 4 | 0.679884 | 1.000000 | 2 | 0 | 0.706911 | 2.153442 | 2.017098 |
| S1 | directional_health_only_score | top_all | 0.010000 | 4 | 0.659670 | 1.000000 | 2 | 0 | 0.806172 | 1.694815 | 1.996442 |
| S1 | directional_health_only_score | top_decisive | 0.010000 | 3 | 0.444967 | 1.000000 | 2 | 0 | 0.548870 | 1.183789 | 1.578900 |
| S4 | directional_gain_mean | top_decisive | 0.010000 | 3 | 0.509728 | 1.000000 | 2 | 0 | 0.377448 | 1.059257 | 1.534436 |
| Q2 | directional_action_health_score | top_all | 0.040000 | 18 | 0.796315 | 0.611111 | 5 | 2 | 2.035608 | 1.584810 | 1.458855 |
| S1 | directional_pessimistic_score | top_all | 0.010000 | 4 | 0.340701 | 0.500000 | 2 | 0 | 0.468533 | 1.050161 | 1.289413 |
| S1 | directional_health_only_score | top_decisive | 0.020000 | 7 | 0.520939 | 0.857143 | 2 | 0 | 0.034674 | 0.081901 | 1.204123 |
| Q2 | directional_health_only_score | top_all | 0.010000 | 4 | 0.237152 | 0.500000 | 2 | 0 | 0.368567 | 0.799176 | 1.100765 |
| Q2 | directional_health_only_score | top_decisive | 0.010000 | 4 | 0.237152 | 0.500000 | 2 | 0 | 0.352434 | 0.667413 | 1.076080 |
| S2 | directional_pessimistic_score | top_decisive | 0.040000 | 15 | 0.512281 | 0.533333 | 5 | 2 | 1.454725 | 1.301165 | 0.801853 |
| S4 | directional_gain_mean | top_decisive | 0.020000 | 6 | 0.473219 | 0.666667 | 2 | 1 | 0.877566 | 1.574660 | 0.801506 |
| Q2 | directional_action_health_score | top_decisive | 0.040000 | 15 | 0.742763 | 0.600000 | 4 | 2 | 1.112115 | 2.010329 | 0.725666 |
| S2 | directional_pessimistic_score | top_decisive | 0.180000 | 66 | 0.758145 | 0.500000 | 6 | 4 | 3.418267 | 1.691366 | 0.486156 |
| Q3 | directional_action_health_score | top_all | 0.020000 | 9 | 0.219561 | 0.666667 | 3 | 1 | 0.500611 | 0.639872 | 0.448349 |
| Q2 | directional_action_health_score | top_all | 0.010000 | 4 | 0.248034 | 0.750000 | 3 | 1 | 0.203283 | 0.715608 | 0.343213 |
| S1 | directional_pessimistic_score | top_decisive | 0.010000 | 3 | 0.266687 | 0.666667 | 2 | 1 | 0.493904 | 1.126060 | 0.330128 |
| S4 | directional_gain_mean | top_all | 0.020000 | 9 | 0.236137 | 0.555556 | 3 | 1 | 0.252171 | 0.633040 | 0.299685 |
| Q3 | directional_action_health_score | top_all | 0.040000 | 18 | 0.190666 | 0.666667 | 5 | 2 | 0.850474 | 0.981289 | 0.142848 |
| Q3 | directional_action_health_score | top_decisive | 0.020000 | 7 | 0.169563 | 0.571429 | 3 | 1 | 0.180235 | 0.171544 | 0.142135 |
| Q1 | directional_gain_mean | top_decisive | 0.080000 | 27 | 0.626455 | 0.555556 | 5 | 3 | 1.505096 | 1.696417 | 0.046716 |
| Q1 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| Q2 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| Q3 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| S1 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| S2 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| S3 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| S4 | directional_action_health_score | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | NA | 0.000000 |
| Q2 | directional_pessimistic_score | top_all | 0.020000 | 9 | 0.313304 | 0.555556 | 4 | 2 | 0.666813 | 1.501191 | -0.020917 |
| S2 | directional_health_only_score | top_all | 0.040000 | 18 | -0.002157 | 0.666667 | 1 | 1 | 0.709437 | 0.902500 | -0.067000 |
| Q2 | directional_action_health_score | top_decisive | 0.010000 | 4 | 0.107192 | 0.500000 | 2 | 1 | 0.222167 | 0.477064 | -0.098369 |
| Q1 | directional_gain_mean | top_decisive | 0.100000 | 34 | 0.521145 | 0.588235 | 6 | 3 | 1.167931 | 0.890603 | -0.112562 |
| Q1 | directional_action_health_score | top_decisive | 0.010000 | 3 | 0.214583 | 0.666667 | 1 | 1 | 0.246687 | 0.603639 | -0.140636 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_counterfactual_directional_action_health_anchor_free_83d20117_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.25578930072387673, 'probability_max': 0.829480335107557}`

## 해석

좋은 결과:

```text
direction listener만으로 nested subject-heldout gain이 살아나면,
HS-JEPA core는 row-target probability 후처리가 아니라
counterfactual human-state action-health model이라는 주장이 강해진다.
```

나쁜 결과:

```text
direction listener도 subject-heldout에서 무너지면,
현재 core는 action probability/magnitude 또는 support geometry 없이는
safe assignment를 만들지 못한다.
이 경우 HS-JEPA 논문 주장은 core-only가 아니라
core + action-aware adapter boundary로 제한해야 한다.
```
