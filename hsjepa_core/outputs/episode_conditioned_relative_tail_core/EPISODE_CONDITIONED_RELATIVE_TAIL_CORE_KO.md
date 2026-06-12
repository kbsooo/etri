# Episode-Conditioned Relative Tail Core

## 한 줄 요약

subject-relative badness도 아직 거칠다고 보고, row episode state별 tail scale로 다시 정규화했다.

```text
HS-JEPA residual/energy + sequence episode context
  -> episode-conditioned relative badness
  -> row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core target representation을 episode-conditioned tail field로 재정의하는 core-decoder boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 생활 context와 row sequence context만으로
보이지 않는 episode-specific action-tail representation을 예측할 수 있는가?
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `episode_conditioned_relative_tail_oof_positive_subjectheldout_fragile`
- full OOF selected gain: `3.733608`
- nested heldout gain: `-3.230895`
- stable targets: `['Q3', 'S3', 'S4']`
- stable OOF gain: `1.651284`
- candidate policy source: `stable_subjectheldout`
- released test cells: `50`

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
| episode_energy_mean_subject_z | 0.142174 | 1.005754 | 0.203658 | 1.001678 |
| episode_month_end | 0.035556 | 0.185179 | 0.016000 | 0.125475 |
| episode_quiet_pressure | 0.321583 | 0.320354 | 0.295761 | 0.274130 |
| episode_reset_pressure | 0.444348 | 0.456816 | 0.440895 | 0.515692 |

## Episode Tail Model Metrics

| metric | value |
| --- | --- |
| episode_conditioned_gain_mae | 0.991071 |
| episode_tail_loss_mae | 0.669120 |
| episode_positive_auc | 0.512829 |
| episode_positive_ap | 0.498631 |
| episode_toxic_tail_auc | 0.710248 |
| episode_toxic_tail_ap | 0.299470 |
| episode_toxic_tail_rate | 0.174444 |
| absolute_gain_sum_all_modes | -141.439797 |

## Full OOF Chosen Policies

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | episode_conditioned_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | episode_conditioned_utility | top_all | 0.040000 | 18 | 0.283327 | 0.611111 | 4 | 2 | 0.980527 | 0.201580 | positive_episode_conditioned_tail_policy |
| Q2 | True | episode_relative_health_score | top_all | 0.020000 | 9 | 0.118138 | 0.555556 | 2 | 0 | 0.463656 | 0.985600 | positive_episode_conditioned_tail_policy |
| Q3 | True | episode_relative_health_score | top_decisive | 0.040000 | 14 | 0.304386 | 0.571429 | 2 | 0 | 0.745432 | 1.379407 | positive_episode_conditioned_tail_policy |
| S1 | True | episode_relative_health_score | top_all | 0.040000 | 18 | 0.220405 | 0.666667 | 5 | 1 | 0.616206 | 0.947176 | positive_episode_conditioned_tail_policy |
| S2 | True | episode_conditioned_utility | top_all | 0.080000 | 36 | 1.460454 | 0.722222 | 5 | 2 | 1.563242 | 1.907509 | positive_episode_conditioned_tail_policy |
| S3 | True | episode_conditioned_pessimistic_utility | top_decisive | 0.020000 | 7 | 0.600462 | 0.857143 | 4 | 1 | 0.828945 | 1.416193 | positive_episode_conditioned_tail_policy |
| S4 | True | episode_conditioned_utility | top_decisive | 0.180000 | 57 | 0.746436 | 0.614035 | 7 | 2 | 2.776384 | 2.334728 | positive_episode_conditioned_tail_policy |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 23 | -0.203435 | -0.008845 | 0.478261 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id02 | 26 | -1.829511 | -0.070366 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id03 | 15 | 0.100352 | 0.006690 | 0.600000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id04 | 36 | -0.269141 | -0.007476 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id05 | 18 | -0.440668 | -0.024482 | 0.444444 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id06 | 26 | -0.807407 | -0.031054 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id07 | 24 | -0.466011 | -0.019417 | 0.583333 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id08 | 31 | -0.069444 | -0.002240 | 0.516129 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id09 | 16 | 0.685510 | 0.042844 | 0.750000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id10 | 14 | 0.068860 | 0.004919 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 36 | -3.205452 | -0.089040 | 0.361111 | 16.000000 | 20.000000 | 1 | 9 |
| Q2 | 20 | -0.027620 | -0.001381 | 0.600000 | 1.000000 | 19.000000 | 6 | 4 |
| Q3 | 50 | 0.376450 | 0.007529 | 0.560000 | 19.000000 | 31.000000 | 8 | 2 |
| S1 | 22 | -0.355842 | -0.016175 | 0.590909 | 11.000000 | 11.000000 | 5 | 5 |
| S2 | 36 | -0.815844 | -0.022662 | 0.444444 | 13.000000 | 23.000000 | 5 | 5 |
| S3 | 12 | 0.269248 | 0.022437 | 0.666667 | 4.000000 | 8.000000 | 7 | 3 |
| S4 | 53 | 0.528166 | 0.009965 | 0.584906 | 19.000000 | 34.000000 | 5 | 4 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | episode_conditioned_utility | hold | 0.000000 | 1.000000 | -3.205452 | 1 | 9 | 0.361111 | failed_episode_conditioned_tail_stress |
| Q2 | False | episode_relative_health_score | hold | 0.000000 | 1.000000 | -0.027620 | 6 | 4 | 0.600000 | failed_episode_conditioned_tail_stress |
| Q3 | True | episode_relative_health_score | top_decisive | 0.040000 | 1.000000 | 0.376450 | 8 | 2 | 0.560000 | episode_conditioned_tail_subjectheldout_stable |
| S1 | False | episode_relative_health_score | hold | 0.000000 | 1.000000 | -0.355842 | 5 | 5 | 0.590909 | failed_episode_conditioned_tail_stress |
| S2 | False | episode_conditioned_utility | hold | 0.000000 | 1.000000 | -0.815844 | 5 | 5 | 0.444444 | failed_episode_conditioned_tail_stress |
| S3 | True | episode_conditioned_pessimistic_utility | top_decisive | 0.020000 | 1.000000 | 0.269248 | 7 | 3 | 0.666667 | episode_conditioned_tail_subjectheldout_stable |
| S4 | True | episode_conditioned_utility | top_decisive | 0.180000 | 1.000000 | 0.528166 | 5 | 4 | 0.584906 | episode_conditioned_tail_subjectheldout_stable |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | episode_conditioned_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | episode_relative_health_score | top_all | 0.140000 | 63 | 0.473573 | 0.523810 | 8 | 0 | 2.504562 | 2.342494 | 3.863133 |
| Q3 | episode_conditioned_pessimistic_utility | top_decisive | 0.250000 | 87 | 0.846379 | 0.505747 | 8 | 2 | 2.634913 | 2.373649 | 2.606856 |
| Q3 | episode_relative_health_score | top_decisive | 0.250000 | 87 | 0.718463 | 0.517241 | 8 | 2 | 2.821033 | 1.080339 | 2.428982 |
| Q3 | episode_conditioned_pessimistic_utility | top_all | 0.250000 | 112 | 0.129922 | 0.517857 | 8 | 2 | 3.573983 | 2.438157 | 2.417656 |
| Q3 | episode_relative_health_score | top_all | 0.180000 | 81 | 0.589478 | 0.530864 | 8 | 2 | 2.947504 | 0.946533 | 2.356905 |
| S4 | episode_conditioned_utility | top_decisive | 0.180000 | 57 | 0.746436 | 0.614035 | 7 | 2 | 2.776384 | 1.731438 | 2.334728 |
| S2 | episode_conditioned_utility | top_all | 0.080000 | 36 | 1.460454 | 0.722222 | 5 | 2 | 1.563242 | 0.889311 | 1.907509 |
| S2 | predicted_episode_conditioned_gain | top_all | 0.060000 | 27 | 1.297375 | 0.740741 | 5 | 2 | 1.606636 | 1.415524 | 1.836073 |
| S2 | episode_conditioned_utility | top_decisive | 0.100000 | 36 | 1.504094 | 0.694444 | 5 | 3 | 2.171239 | 2.265546 | 1.593752 |
| S3 | episode_conditioned_pessimistic_utility | top_decisive | 0.020000 | 7 | 0.600462 | 0.857143 | 4 | 1 | 0.828945 | 1.629382 | 1.416193 |
| Q3 | episode_relative_health_score | top_decisive | 0.040000 | 14 | 0.304386 | 0.571429 | 2 | 0 | 0.745432 | 1.018136 | 1.379407 |
| Q2 | episode_relative_health_score | top_decisive | 0.040000 | 15 | 0.159365 | 0.533333 | 2 | 0 | 0.888619 | 1.115544 | 1.315304 |
| Q3 | episode_relative_health_score | top_all | 0.020000 | 9 | 0.248803 | 0.666667 | 2 | 0 | 0.665895 | 1.097014 | 1.313354 |
| Q3 | episode_relative_health_score | top_decisive | 0.140000 | 49 | 0.351759 | 0.469388 | 3 | 1 | 1.626578 | 1.066438 | 1.241696 |
| S2 | predicted_episode_conditioned_gain | top_decisive | 0.080000 | 29 | 0.676353 | 0.689655 | 4 | 2 | 1.824477 | 1.229761 | 1.099800 |
| Q3 | episode_relative_health_score | top_all | 0.040000 | 18 | 0.161173 | 0.500000 | 2 | 0 | 0.519996 | 0.687418 | 1.054661 |
| S2 | episode_conditioned_utility | top_decisive | 0.080000 | 29 | 0.589335 | 0.689655 | 4 | 2 | 1.858825 | 1.038289 | 1.008698 |
| Q2 | episode_relative_health_score | top_all | 0.020000 | 9 | 0.118138 | 0.555556 | 2 | 0 | 0.463656 | 0.613015 | 0.985600 |
| S1 | episode_relative_health_score | top_all | 0.040000 | 18 | 0.220405 | 0.666667 | 5 | 1 | 0.616206 | 0.593263 | 0.947176 |
| Q3 | predicted_episode_conditioned_gain | top_decisive | 0.180000 | 62 | 0.568188 | 0.435484 | 4 | 3 | 3.236885 | 1.911978 | 0.936783 |
| Q2 | episode_relative_health_score | top_decisive | 0.020000 | 7 | 0.104404 | 0.571429 | 2 | 0 | 0.391372 | 0.570255 | 0.930947 |
| Q3 | episode_relative_health_score | top_decisive | 0.080000 | 28 | 0.074853 | 0.428571 | 2 | 0 | 0.487974 | 0.411109 | 0.899715 |
| S2 | predicted_episode_conditioned_gain | top_decisive | 0.060000 | 22 | 0.641908 | 0.681818 | 4 | 2 | 1.402487 | 1.596194 | 0.875274 |
| Q3 | episode_relative_health_score | top_decisive | 0.020000 | 7 | 0.139224 | 0.571429 | 2 | 0 | 0.221981 | 0.449613 | 0.858124 |
| Q3 | episode_relative_health_score | top_all | 0.100000 | 45 | 0.226507 | 0.466667 | 3 | 1 | 1.164860 | 0.813903 | 0.831516 |
| S2 | episode_conditioned_pessimistic_utility | top_all | 0.060000 | 27 | 0.711397 | 0.740741 | 3 | 2 | 1.453775 | 1.363617 | 0.759793 |
| S4 | episode_relative_health_score | top_decisive | 0.020000 | 6 | 0.310592 | 0.833333 | 3 | 1 | 0.362195 | 0.776017 | 0.561255 |
| S2 | episode_conditioned_utility | top_decisive | 0.060000 | 22 | 0.671589 | 0.727273 | 2 | 2 | 1.522965 | 0.981188 | 0.508780 |
| S3 | episode_relative_health_score | top_all | 0.020000 | 9 | 0.163565 | 0.444444 | 3 | 1 | 0.723111 | 0.588189 | 0.492970 |
| S2 | episode_conditioned_utility | top_all | 0.100000 | 45 | 1.273016 | 0.688889 | 5 | 4 | 2.306186 | 1.281915 | 0.467470 |
| S4 | episode_relative_health_score | top_all | 0.250000 | 112 | 0.091654 | 0.544643 | 7 | 3 | 2.133552 | 0.985461 | 0.369523 |
| Q3 | predicted_episode_conditioned_gain | top_all | 0.250000 | 112 | -0.368777 | 0.428571 | 5 | 3 | 3.355853 | 2.151476 | 0.292262 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_episode_conditioned_relative_tail_anchor_free_56c526fc_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.41008421421877533, 'probability_max': 0.8293652784805956}`

## 해석

좋은 결과:

```text
episode-conditioned tail field가 subject-normalized tail field보다 nested damage를 줄이면,
HS-JEPA의 target representation은 human-relative일 뿐 아니라 episode-relative여야 한다.
```

나쁜 결과:

```text
episode conditioning이 오히려 나빠지면,
현재 row sequence/episode features는 subject-heldout에서 shortcut으로 작동한다.
그 경우 episode는 direct feature가 아니라 action-space constraint나 diagnostic으로만 써야 한다.
```
