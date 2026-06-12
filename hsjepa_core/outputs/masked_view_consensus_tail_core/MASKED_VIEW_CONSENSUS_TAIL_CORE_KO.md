# Masked-View Consensus Tail Core

## 한 줄 요약

HS-JEPA가 예측한 hidden tail representation이 진짜 구조라면, 일부 context view를 가려도
비슷한 결론을 내야 한다. 그래서 여러 masked view가 동의하는 row-target-action만 release한다.

```text
visible human context views
  -> predict the same hidden episode-conditioned tail representation
  -> penalize view disagreement
  -> row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 정확히는 **HS-JEPA core target representation의 masked-view invariance를 검사하는 core-decoder boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
서로 다른 visible context mask들이 같은 hidden action-tail representation을 예측하는가?
```

LeJEPA성은 다음 질문에서 나온다.

```text
좋아 보이는 action score가 특정 view shortcut/collapse가 아니라는 것을
view disagreement penalty로 확인할 수 있는가?
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `masked_view_consensus_tail_subjectheldout_positive`
- full OOF selected gain: `2.779623`
- nested heldout gain: `0.578637`
- stable targets: `['S2', 'S4']`
- stable OOF gain: `2.018205`
- candidate policy source: `stable_subjectheldout`
- released test cells: `74`

## View Metrics

| view | feature_count | gain_mae | tail_mae | positive_auc | positive_ap | toxic_auc | toxic_ap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_context | 487 | 0.991071 | 0.669120 | 0.512829 | 0.498631 | 0.710248 | 0.299470 |
| mask_world_residual | 453 | 0.995744 | 0.668446 | 0.507161 | 0.496688 | 0.714868 | 0.303832 |
| mask_episode_context | 445 | 0.999776 | 0.664688 | 0.510701 | 0.497346 | 0.707113 | 0.298386 |
| mask_listener_support | 107 | 0.988453 | 0.663803 | 0.517775 | 0.505623 | 0.716770 | 0.306492 |
| consensus | 1492 | 0.987486 | 0.663648 | 0.515668 | 0.500204 | 0.714272 | 0.304596 |

## View Disagreement By Target

| target | mean_disagreement | median_disagreement | mean_abs_gain | toxic_tail_rate |
| --- | --- | --- | --- | --- |
| Q1 | 0.067971 | 0.039879 | 0.149887 | 0.171111 |
| Q2 | 0.089600 | 0.045556 | 0.186684 | 0.171111 |
| Q3 | 0.087195 | 0.039323 | 0.148881 | 0.180000 |
| S1 | 0.259181 | 0.146326 | 0.175385 | 0.167778 |
| S2 | 0.198407 | 0.115764 | 0.201806 | 0.180000 |
| S3 | 0.196038 | 0.094300 | 0.173793 | 0.172222 |
| S4 | 0.095974 | 0.049870 | 0.143513 | 0.178889 |

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

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | masked_view_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | masked_view_consensus_utility | top_decisive | 0.020000 | 7 | 0.085318 | 0.571429 | 3 | 1 | 0.194547 | 0.085328 | positive_masked_view_consensus_policy |
| Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 7 | 0.168347 | 0.571429 | 2 | 0 | 0.805384 | 1.360981 | positive_masked_view_consensus_policy |
| Q3 | True | masked_view_consensus_health_score | top_all | 0.060000 | 27 | 0.410365 | 0.666667 | 7 | 1 | 1.222874 | 2.013891 | positive_masked_view_consensus_policy |
| S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 9 | 0.097388 | 0.666667 | 4 | 1 | 0.806215 | 0.803624 | positive_masked_view_consensus_policy |
| S2 | True | masked_view_consensus_utility | top_decisive | 0.060000 | 22 | 1.293124 | 0.772727 | 3 | 1 | 2.457120 | 2.798643 | positive_masked_view_consensus_policy |
| S3 | False | masked_view_gain_mean | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_masked_view_consensus_policy_passed |
| S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 112 | 0.725081 | 0.571429 | 8 | 2 | 1.412284 | 1.708372 | positive_masked_view_consensus_policy |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 29 | 0.460456 | 0.015878 | 0.517241 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id02 | 31 | -0.477452 | -0.015402 | 0.451613 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id03 | 14 | 0.415840 | 0.029703 | 0.642857 | Q1,Q2,Q3,S1,S2,S4 |
| id04 | 15 | -0.071243 | -0.004750 | 0.666667 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id05 | 26 | 0.382860 | 0.014725 | 0.538462 | Q1,Q2,Q3,S1,S2,S4 |
| id06 | 22 | -0.996520 | -0.045296 | 0.181818 | Q2,Q3,S2,S3,S4 |
| id07 | 22 | 0.348604 | 0.015846 | 0.636364 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id08 | 19 | -0.009731 | -0.000512 | 0.315789 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id09 | 18 | -0.107724 | -0.005985 | 0.500000 | Q1,Q2,Q3,S2,S3,S4 |
| id10 | 15 | 0.633548 | 0.042237 | 0.600000 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 16 | -0.981123 | -0.061320 | 0.562500 | 5.000000 | 11.000000 | 3 | 6 |
| Q2 | 16 | -0.032074 | -0.002005 | 0.437500 | 1.000000 | 15.000000 | 5 | 5 |
| Q3 | 31 | -0.328817 | -0.010607 | 0.419355 | 11.000000 | 20.000000 | 4 | 6 |
| S1 | 21 | -0.036084 | -0.001718 | 0.380952 | 12.000000 | 9.000000 | 5 | 3 |
| S2 | 19 | 2.657036 | 0.139844 | 0.684211 | 6.000000 | 13.000000 | 8 | 2 |
| S3 | 13 | -1.011257 | -0.077789 | 0.230769 | 8.000000 | 5.000000 | 2 | 6 |
| S4 | 95 | 0.310957 | 0.003273 | 0.536842 | 54.000000 | 41.000000 | 7 | 3 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | masked_view_consensus_utility | hold | 0.000000 | 0.900000 | -0.981123 | 3 | 6 | 0.562500 | failed_masked_view_consensus_stress |
| Q2 | False | masked_view_consensus_pessimistic_utility | hold | 0.000000 | 1.000000 | -0.032074 | 5 | 5 | 0.437500 | failed_masked_view_consensus_stress |
| Q3 | False | masked_view_consensus_health_score | hold | 0.000000 | 1.000000 | -0.328817 | 4 | 6 | 0.419355 | failed_masked_view_consensus_stress |
| S1 | False | masked_view_consensus_health_score | hold | 0.000000 | 0.800000 | -0.036084 | 5 | 3 | 0.380952 | failed_masked_view_consensus_stress |
| S2 | True | masked_view_consensus_utility | top_decisive | 0.060000 | 1.000000 | 2.657036 | 8 | 2 | 0.684211 | masked_view_consensus_subjectheldout_stable |
| S3 | False | masked_view_gain_mean | hold | 0.000000 | 0.800000 | -1.011257 | 2 | 6 | 0.230769 | failed_masked_view_consensus_stress |
| S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 1.000000 | 0.310957 | 7 | 3 | 0.536842 | masked_view_consensus_subjectheldout_stable |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | masked_view_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | masked_view_consensus_utility | top_decisive | 0.060000 | 22 | 1.293124 | 0.772727 | 3 | 1 | 2.457120 | 1.476727 | 2.798643 |
| Q3 | masked_view_consensus_health_score | top_decisive | 0.250000 | 87 | 0.695035 | 0.517241 | 8 | 2 | 2.772210 | 1.312993 | 2.449786 |
| Q2 | masked_view_consensus_pessimistic_utility | top_all | 0.080000 | 36 | 0.282112 | 0.472222 | 3 | 0 | 1.927309 | 1.172551 | 2.318713 |
| Q2 | masked_view_consensus_pessimistic_utility | top_all | 0.250000 | 112 | 0.518426 | 0.473214 | 8 | 2 | 2.572995 | 1.024502 | 2.112007 |
| Q3 | masked_view_consensus_pessimistic_utility | top_decisive | 0.250000 | 87 | 0.894682 | 0.505747 | 7 | 3 | 3.592232 | 2.007499 | 2.035514 |
| Q2 | masked_view_consensus_pessimistic_utility | top_decisive | 0.100000 | 37 | 0.380081 | 0.513514 | 3 | 0 | 1.305734 | 0.802248 | 2.022055 |
| Q3 | masked_view_consensus_health_score | top_all | 0.060000 | 27 | 0.410365 | 0.666667 | 7 | 1 | 1.222874 | 1.146601 | 2.013891 |
| S2 | masked_view_gain_mean | top_decisive | 0.020000 | 7 | 1.091274 | 0.857143 | 3 | 1 | 1.345859 | 1.551434 | 1.982330 |
| Q3 | masked_view_consensus_health_score | top_decisive | 0.180000 | 62 | 0.427748 | 0.483871 | 7 | 2 | 2.322519 | 1.744185 | 1.745079 |
| S4 | masked_view_consensus_health_score | top_all | 0.250000 | 112 | 0.725081 | 0.571429 | 8 | 2 | 1.412284 | 1.344243 | 1.708372 |
| Q2 | masked_view_consensus_pessimistic_utility | top_all | 0.100000 | 45 | 0.186604 | 0.444444 | 3 | 0 | 0.726524 | 0.454612 | 1.433653 |
| Q3 | masked_view_consensus_health_score | top_all | 0.080000 | 36 | 0.561743 | 0.638889 | 8 | 2 | 1.291661 | 0.788432 | 1.425240 |
| Q3 | masked_view_consensus_health_score | top_all | 0.040000 | 18 | 0.226808 | 0.666667 | 6 | 1 | 0.856535 | 0.988570 | 1.378893 |
| Q2 | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 7 | 0.168347 | 0.571429 | 2 | 0 | 0.805384 | 1.188784 | 1.360981 |
| Q3 | masked_view_consensus_utility | top_decisive | 0.250000 | 87 | 0.692462 | 0.494253 | 7 | 3 | 2.715903 | 2.113902 | 1.334918 |
| Q2 | masked_view_consensus_pessimistic_utility | top_all | 0.180000 | 81 | 0.447754 | 0.456790 | 4 | 2 | 2.696160 | 1.451192 | 1.279868 |
| Q2 | masked_view_consensus_pessimistic_utility | top_decisive | 0.140000 | 52 | 0.373504 | 0.500000 | 4 | 2 | 2.619840 | 1.755782 | 1.208706 |
| Q3 | masked_view_consensus_utility | top_decisive | 0.140000 | 49 | 0.146079 | 0.448980 | 4 | 1 | 1.555885 | 0.721015 | 1.177259 |
| Q3 | masked_view_consensus_utility | top_decisive | 0.180000 | 62 | 0.079307 | 0.451613 | 5 | 2 | 2.678949 | 1.524733 | 1.128968 |
| S2 | masked_view_consensus_utility | top_all | 0.040000 | 18 | 0.243104 | 0.722222 | 2 | 1 | 1.327557 | 1.767223 | 0.895710 |
| Q2 | masked_view_consensus_pessimistic_utility | top_all | 0.140000 | 63 | 0.594921 | 0.507937 | 4 | 2 | 1.811181 | 0.957142 | 0.867247 |
| S1 | masked_view_consensus_health_score | top_all | 0.020000 | 9 | 0.097388 | 0.666667 | 4 | 1 | 0.806215 | 1.183039 | 0.803624 |
| S4 | masked_view_gain_mean | top_decisive | 0.020000 | 6 | 0.474071 | 0.666667 | 3 | 1 | 0.545014 | 0.690331 | 0.749686 |
| S2 | masked_view_gain_mean | top_decisive | 0.060000 | 22 | 0.916844 | 0.681818 | 4 | 3 | 2.036907 | 2.860575 | 0.641974 |
| Q2 | masked_view_consensus_pessimistic_utility | top_decisive | 0.180000 | 67 | 0.447890 | 0.507463 | 5 | 4 | 4.366988 | 1.770746 | 0.620099 |
| Q2 | masked_view_consensus_pessimistic_utility | top_decisive | 0.040000 | 15 | 0.100823 | 0.466667 | 2 | 1 | 1.232207 | 1.153293 | 0.560564 |
| S4 | masked_view_consensus_health_score | top_all | 0.180000 | 81 | 0.424507 | 0.555556 | 6 | 3 | 2.311703 | 1.444848 | 0.547565 |
| S2 | masked_view_gain_mean | top_all | 0.020000 | 9 | 0.725909 | 0.777778 | 3 | 2 | 1.188246 | 1.374328 | 0.534456 |
| S4 | masked_view_consensus_health_score | top_decisive | 0.060000 | 19 | 0.277969 | 0.631579 | 6 | 2 | 0.840572 | 1.292966 | 0.498552 |
| S4 | masked_view_consensus_pessimistic_utility | top_all | 0.100000 | 45 | 0.181371 | 0.511111 | 3 | 1 | 0.683015 | 0.462432 | 0.470789 |
| Q2 | masked_view_consensus_health_score | top_decisive | 0.020000 | 7 | 0.061772 | 0.571429 | 3 | 1 | 0.581181 | 1.308555 | 0.408741 |
| S4 | masked_view_consensus_pessimistic_utility | top_all | 0.060000 | 27 | 0.228140 | 0.555556 | 3 | 1 | 0.456439 | 0.472334 | 0.398443 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_masked_view_consensus_tail_anchor_free_375886b3_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.42869444444444427, 'probability_max': 0.791861784308804}`

## 해석

좋은 결과:

```text
masked-view consensus가 nested damage를 줄이면,
HS-JEPA의 hidden action-tail representation은 single-view shortcut보다
view-invariant human-state signal에 가까워진다.
```

나쁜 결과:

```text
consensus가 나빠지면 현재 hidden tail signal은 masked-view invariant하지 않다.
그 경우 HS-JEPA core는 아직 representation 학습이 아니라 adapter-specific sensor에 가깝다.
```
