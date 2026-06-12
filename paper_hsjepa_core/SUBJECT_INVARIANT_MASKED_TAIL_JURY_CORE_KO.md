# Subject-Invariant Masked-Tail Jury Core

## 한 줄 요약

HS-JEPA hidden tail representation이 진짜 human-state 구조라면,
특정 subject를 빼고 policy를 골라도 비슷한 row-target-action이 살아남아야 한다.
이 실험은 subject-excluded worlds를 jury로 사용해 subject shortcut을 release 조건 안에 넣었다.

```text
masked visible context views
  -> hidden episode-conditioned tail representation
  -> subject-excluded policy selection
  -> jury vote over row-target-action release
  -> sparse anchor-free correction
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 단, classifier가 아니라 **HS-JEPA core-decoder boundary**다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 masked human context만으로 보이지 않는 episode-conditioned action-tail representation을
subject가 바뀌어도 예측할 수 있는가?
```

LeJEPA성은 다음 질문에서 나온다.

```text
좋아 보이는 tail action이 subject shortcut/collapse인지,
subject-excluded jury vote로 걸러낼 수 있는가?
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- parent hidden-tail state source: `parent_masked_view_state_cache`

## Verdict

- verdict: `subject_invariant_masked_tail_jury_positive`
- strict subject-heldout gain: `0.564736`
- strict subject-heldout selected cells: `174`
- release targets: `['Q2', 'S1', 'S2', 'S4']`
- released test cells: `63`
- candidate: `submission_hsjepa_subject_invariant_masked_tail_jury_anchor_free_12249175_uploadsafe.csv`

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

## Jury Subject Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 24 | 0.618227 | 0.025759 | 0.583333 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id02 | 23 | -0.042942 | -0.001867 | 0.652174 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id03 | 8 | 0.427990 | 0.053499 | 0.750000 | Q1,Q2,Q3,S1,S2,S4 |
| id04 | 14 | -0.910723 | -0.065052 | 0.428571 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id05 | 21 | 0.370009 | 0.017619 | 0.523810 | Q1,Q2,Q3,S1,S2,S4 |
| id06 | 18 | -0.940421 | -0.052246 | 0.222222 | Q2,Q3,S1,S2,S3,S4 |
| id07 | 22 | 0.348604 | 0.015846 | 0.636364 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id08 | 11 | 0.168167 | 0.015288 | 0.363636 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id09 | 18 | -0.107724 | -0.005985 | 0.500000 | Q1,Q2,Q3,S2,S3,S4 |
| id10 | 15 | 0.633548 | 0.042237 | 0.600000 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Jury Route Rows

| heldout_subject | target | accepted | score_col | policy | fraction | heldout_selected_cells | heldout_gain_sum | heldout_positive_gain_rate | raw_action_count | inverse_action_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id01 | Q1 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 2 | -0.008450 | 0.500000 | 0 | 2 |
| id01 | Q2 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 2 | 0.013703 | 0.500000 | 0 | 2 |
| id01 | Q3 | True | masked_view_consensus_health_score | top_decisive | 0.180000 | 7 | 0.165160 | 0.571429 | 0 | 7 |
| id01 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.170337 | 1.000000 | 0 | 1 |
| id01 | S2 | True | masked_view_gain_mean | top_all | 0.020000 | 1 | 0.157582 | 1.000000 | 0 | 1 |
| id01 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | 0.096465 | 1.000000 | 0 | 1 |
| id01 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 10 | 0.023431 | 0.500000 | 10 | 0 |
| id02 | Q1 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 2 | 0.082604 | 1.000000 | 1 | 1 |
| id02 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | 0.049879 | 1.000000 | 0 | 1 |
| id02 | Q3 | True | masked_view_consensus_health_score | top_all | 0.060000 | 3 | 0.088856 | 1.000000 | 1 | 2 |
| id02 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | -0.014008 | 0.000000 | 0 | 1 |
| id02 | S2 | True | masked_view_consensus_utility | top_all | 0.060000 | 3 | -0.178558 | 0.000000 | 0 | 3 |
| id02 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.329150 | 0.000000 | 0 | 1 |
| id02 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 12 | 0.257434 | 0.750000 | 7 | 5 |
| id03 | Q1 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 1 | 0.019389 | 1.000000 | 0 | 1 |
| id03 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | -0.067410 | 0.000000 | 0 | 1 |
| id03 | Q3 | True | masked_view_gain_mean | top_decisive | 0.060000 | 1 | 0.089926 | 1.000000 | 1 | 0 |
| id03 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.049928 | 1.000000 | 0 | 1 |
| id03 | S2 | True | masked_view_consensus_utility | top_decisive | 0.060000 | 2 | 0.322767 | 1.000000 | 0 | 2 |
| id03 | S3 | False | masked_view_gain_mean | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 |
| id03 | S4 | True | masked_view_consensus_health_score | top_decisive | 0.060000 | 2 | 0.013391 | 0.500000 | 0 | 2 |
| id04 | Q1 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 2 | 0.041151 | 1.000000 | 1 | 1 |
| id04 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | -0.064439 | 0.000000 | 0 | 1 |
| id04 | Q3 | True | masked_view_gain_mean | top_decisive | 0.060000 | 3 | -0.358082 | 0.000000 | 0 | 3 |
| id04 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.083619 | 1.000000 | 0 | 1 |
| id04 | S2 | True | masked_view_gain_mean | top_decisive | 0.040000 | 2 | -0.357632 | 0.000000 | 0 | 2 |
| id04 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.333455 | 0.000000 | 1 | 0 |
| id04 | S4 | True | masked_view_consensus_health_score | top_decisive | 0.100000 | 4 | 0.078116 | 0.750000 | 1 | 3 |
| id05 | Q1 | True | masked_view_consensus_pessimistic_utility | top_all | 0.040000 | 2 | -0.015838 | 0.500000 | 0 | 2 |
| id05 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | 0.082748 | 1.000000 | 0 | 1 |
| id05 | Q3 | True | masked_view_gain_mean | top_decisive | 0.080000 | 3 | -0.324597 | 0.000000 | 2 | 1 |
| id05 | S1 | True | masked_view_consensus_health_score | top_all | 0.060000 | 3 | -0.038090 | 0.333333 | 2 | 1 |
| id05 | S2 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | 0.439532 | 1.000000 | 0 | 1 |
| id05 | S3 | False | masked_view_gain_mean | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 |
| id05 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 11 | 0.226254 | 0.636364 | 7 | 4 |
| id06 | Q1 | False | masked_view_gain_mean | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 |
| id06 | Q2 | True | masked_view_consensus_health_score | top_decisive | 0.020000 | 1 | 0.090144 | 1.000000 | 1 | 0 |
| id06 | Q3 | True | masked_view_consensus_health_score | top_all | 0.040000 | 2 | -0.054451 | 0.000000 | 1 | 1 |
| id06 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.002242 | 1.000000 | 0 | 1 |
| id06 | S2 | True | masked_view_gain_mean | top_decisive | 0.040000 | 1 | -0.320534 | 0.000000 | 0 | 1 |
| id06 | S3 | True | masked_view_consensus_utility | top_decisive | 0.040000 | 1 | -0.227804 | 0.000000 | 1 | 0 |
| id06 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 12 | -0.430017 | 0.166667 | 8 | 4 |
| id07 | Q1 | True | masked_view_gain_mean | top_decisive | 0.060000 | 2 | -0.107935 | 0.500000 | 1 | 1 |
| id07 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | 0.076526 | 1.000000 | 0 | 1 |
| id07 | Q3 | True | masked_view_consensus_health_score | top_all | 0.060000 | 3 | 0.018778 | 0.666667 | 1 | 2 |
| id07 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.019729 | 1.000000 | 1 | 0 |
| id07 | S2 | True | masked_view_gain_mean | top_decisive | 0.040000 | 2 | 0.337051 | 0.500000 | 2 | 0 |
| id07 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.158347 | 0.000000 | 0 | 1 |
| id07 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 12 | 0.162802 | 0.666667 | 3 | 9 |
| id08 | Q1 | True | masked_view_gain_mean | top_decisive | 0.060000 | 2 | -0.961700 | 0.000000 | 2 | 0 |
| id08 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | -0.054776 | 0.000000 | 0 | 1 |
| id08 | Q3 | True | masked_view_consensus_health_score | top_all | 0.060000 | 3 | 0.018606 | 0.333333 | 1 | 2 |
| id08 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | -0.027725 | 0.000000 | 1 | 0 |
| id08 | S2 | True | masked_view_gain_mean | top_decisive | 0.040000 | 2 | 0.878927 | 1.000000 | 2 | 0 |
| id08 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | 0.440164 | 1.000000 | 1 | 0 |
| id08 | S4 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.125328 | 0.000000 | 1 | 0 |
| id09 | Q1 | True | masked_view_consensus_utility | top_all | 0.040000 | 2 | -0.018877 | 0.500000 | 0 | 2 |
| id09 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | -0.056743 | 0.000000 | 0 | 1 |
| id09 | Q3 | True | masked_view_consensus_health_score | top_all | 0.080000 | 3 | -0.066600 | 0.333333 | 1 | 2 |
| id09 | S1 | False | masked_view_gain_mean | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 |
| id09 | S2 | True | masked_view_gain_mean | top_decisive | 0.040000 | 1 | 0.385647 | 1.000000 | 1 | 0 |
| id09 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.312151 | 0.000000 | 1 | 0 |
| id09 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 10 | -0.039001 | 0.600000 | 8 | 2 |
| id10 | Q1 | True | masked_view_consensus_utility | top_all | 0.040000 | 1 | -0.011467 | 0.000000 | 0 | 1 |
| id10 | Q2 | True | masked_view_consensus_pessimistic_utility | top_decisive | 0.020000 | 1 | 0.056066 | 1.000000 | 0 | 1 |
| id10 | Q3 | True | masked_view_consensus_health_score | top_all | 0.060000 | 2 | -0.030330 | 0.500000 | 1 | 1 |
| id10 | S1 | True | masked_view_consensus_health_score | top_all | 0.020000 | 1 | 0.074240 | 1.000000 | 1 | 0 |
| id10 | S2 | True | masked_view_consensus_utility | top_decisive | 0.060000 | 1 | 0.434841 | 1.000000 | 0 | 1 |
| id10 | S3 | True | masked_view_gain_mean | top_decisive | 0.020000 | 1 | -0.133122 | 0.000000 | 1 | 0 |
| id10 | S4 | True | masked_view_consensus_health_score | top_all | 0.250000 | 8 | 0.243320 | 0.625000 | 2 | 6 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 16 | -0.981123 | -0.061320 | 0.562500 | 5.000000 | 11.000000 | 3 | 6 |
| Q2 | 11 | 0.125698 | 0.011427 | 0.545455 | 1.000000 | 10.000000 | 6 | 4 |
| Q3 | 30 | -0.452735 | -0.015091 | 0.433333 | 9.000000 | 21.000000 | 5 | 5 |
| S1 | 11 | 0.320272 | 0.029116 | 0.636364 | 5.000000 | 6.000000 | 6 | 3 |
| S2 | 16 | 2.099623 | 0.131226 | 0.562500 | 5.000000 | 11.000000 | 7 | 3 |
| S3 | 8 | -0.957400 | -0.119675 | 0.250000 | 5.000000 | 3.000000 | 2 | 6 |
| S4 | 82 | 0.410401 | 0.005005 | 0.560976 | 47.000000 | 35.000000 | 7 | 3 |

## Subject-Jury Release Laws

| target | accepted | vote_threshold | test_budget | heldout_accept_rate | heldout_gain_sum | heldout_selected_cells | heldout_positive_gain_rate | heldout_positive_subjects | heldout_negative_subjects | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | 4 | 0 | 0.900000 | -0.981123 | 16 | 0.562500 | 3 | 6 | failed_subject_invariant_jury_stress |
| Q2 | True | 4 | 6 | 1.000000 | 0.125698 | 11 | 0.545455 | 6 | 4 | subject_invariant_masked_tail_jury_release |
| Q3 | False | 4 | 0 | 1.000000 | -0.452735 | 30 | 0.433333 | 5 | 5 | failed_subject_invariant_jury_stress |
| S1 | True | 4 | 6 | 0.900000 | 0.320272 | 11 | 0.636364 | 6 | 3 | subject_invariant_masked_tail_jury_release |
| S2 | True | 3 | 9 | 1.000000 | 2.099623 | 16 | 0.562500 | 7 | 3 | subject_invariant_masked_tail_jury_release |
| S3 | False | 4 | 0 | 0.800000 | -0.957400 | 8 | 0.250000 | 2 | 6 | failed_subject_invariant_jury_stress |
| S4 | True | 4 | 46 | 1.000000 | 0.410401 | 82 | 0.560976 | 7 | 3 | subject_invariant_masked_tail_jury_release |

## Jury Vote Distribution

| target | train_mean_vote_fraction | train_p90_vote_fraction | test_mean_vote_fraction | test_p90_vote_fraction | test_high_vote_cells |
| --- | --- | --- | --- | --- | --- |
| Q1 | 0.018444 | 0.000000 | 0.018000 | 0.000000 | 10 |
| Q2 | 0.009000 | 0.000000 | 0.007400 | 0.000000 | 3 |
| Q3 | 0.032667 | 0.100000 | 0.031600 | 0.100000 | 15 |
| S1 | 0.011000 | 0.000000 | 0.011000 | 0.000000 | 5 |
| S2 | 0.018000 | 0.000000 | 0.017600 | 0.000000 | 8 |
| S3 | 0.007000 | 0.000000 | 0.008800 | 0.000000 | 5 |
| S4 | 0.093444 | 0.700000 | 0.094400 | 0.700000 | 62 |

## 해석

좋은 결과:

```text
subject-excluded jury가 positive heldout gain을 유지하면,
HS-JEPA hidden tail representation은 단일 subject의 tail memory가 아니라
subject-invariant action-health field에 가깝다.
```

나쁜 결과:

```text
full masked-view consensus가 좋고 jury가 나쁘면,
현재 positive signal은 view-invariant일 수는 있어도 subject-invariant하지 않다.
그 경우 HS-JEPA core는 아직 public/private-safe release law가 아니라
adapter가 의심해야 할 teacher signal로 다뤄야 한다.
```
