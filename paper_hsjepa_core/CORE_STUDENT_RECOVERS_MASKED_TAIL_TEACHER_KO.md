# Core Student Recovers Masked Tail Teacher

## 한 줄 요약

masked-view consensus tail teacher는 현재 가장 강한 HS-JEPA core-boundary evidence다.
이번 실험은 그 teacher의 hidden action-tail representation을, action probability/magnitude/support score 없이
core student가 복원할 수 있는지 검사한다.

```text
visible human-state context + minimal action listener
  -> recover masked-view teacher hidden tail representation
  -> sparse row-target action assignment
```

## 빠른 판정: 이것은 HS-JEPA인가?

맞다. 정확히는 **HS-JEPA core student가 teacher의 hidden target representation을 예측하는지 보는
distillation-style core-boundary 실험**이다.

JEPA성은 다음 질문에서 나온다.

```text
보이는 human-state context만으로
보이지 않는 masked-view action-tail teacher representation을 복원할 수 있는가?
```

다만 이 실험은 teacher를 target representation으로 사용하므로, 독립적인 core proof가 아니라
`frontier hidden representation recoverability` sensor로 읽어야 한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- action probability as student feature: `False`
- action magnitude as student feature: `False`
- support score as student feature: `False`

## Verdict

- verdict: `core_student_teacher_recovery_oof_positive_subjectheldout_fragile`
- full OOF selected gain: `8.078259`
- nested heldout gain: `-3.635973`
- stable targets: `[]`
- stable OOF gain: `0.000000`
- candidate policy source: `full_oof_sensor`
- released test cells: `87`

## Teacher Masked-View Metrics

| view | feature_count | gain_mae | tail_mae | positive_auc | positive_ap | toxic_auc | toxic_ap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_context | 487 | 0.991071 | 0.669120 | 0.512829 | 0.498631 | 0.710248 | 0.299470 |
| mask_world_residual | 453 | 0.995744 | 0.668446 | 0.507161 | 0.496688 | 0.714868 | 0.303832 |
| mask_episode_context | 445 | 0.999776 | 0.664688 | 0.510701 | 0.497346 | 0.707113 | 0.298386 |
| mask_listener_support | 107 | 0.988453 | 0.663803 | 0.517775 | 0.505623 | 0.716770 | 0.306492 |
| consensus | 1492 | 0.987486 | 0.663648 | 0.515668 | 0.500204 | 0.714272 | 0.304596 |

## Student Recovery Metrics

| view | feature_count | teacher_mae | pessimistic_mae | teacher_top_auc | teacher_top_ap | realized_health_auc | realized_health_ap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| student_full_context | 482 | 0.596837 | 0.881183 | 0.575717 | 0.138602 | 0.586807 | 0.561782 |
| student_mask_world | 74 | 0.583595 | 0.856312 | 0.627556 | 0.153996 | 0.585798 | 0.558184 |
| student_mask_episode | 440 | 0.681885 | 1.009820 | 0.513082 | 0.103745 | 0.590909 | 0.564185 |
| student_mask_listener_interaction | 108 | 0.595350 | 0.869757 | 0.566743 | 0.125079 | 0.583970 | 0.557135 |
| student_mask_action_listener | 469 | 0.670088 | 0.975710 | 0.561768 | 0.127402 | 0.500000 | 0.500000 |
| student_consensus | 1573 | 0.604001 | 0.886907 | 0.582875 | 0.134131 | 0.592321 | 0.560345 |

## Student Disagreement By Target

| target | mean_student_disagreement | median_student_disagreement | teacher_score_mean | student_score_mean | realized_gain_mean |
| --- | --- | --- | --- | --- | --- |
| Q1 | 0.161272 | 0.135174 | -0.769986 | -1.616689 | -0.015615 |
| Q2 | 0.305491 | 0.254297 | -0.887933 | -1.969783 | -0.023504 |
| Q3 | 0.319590 | 0.263398 | -0.839683 | -1.978041 | -0.020509 |
| S1 | 0.728298 | 0.566838 | -1.274648 | -3.050246 | -0.026522 |
| S2 | 0.519924 | 0.418399 | -1.027860 | -2.503989 | -0.028166 |
| S3 | 0.600664 | 0.510879 | -1.061887 | -2.699110 | -0.028773 |
| S4 | 0.195262 | 0.162271 | -0.767817 | -1.677801 | -0.014068 |

## Teacher Disagreement By Target

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

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | student_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | student_pessimistic_mean | top_all | 0.180000 | 81 | 1.013147 | 0.555556 | 6 | 3 | 2.210001 | 1.175044 | positive_core_student_teacher_recovery |
| Q2 | True | student_conservative_tail_score | top_decisive | 0.060000 | 22 | 1.342671 | 0.590909 | 5 | 2 | 2.164325 | 2.281974 | positive_core_student_teacher_recovery |
| Q3 | True | student_teacher_mean | top_all | 0.010000 | 4 | 0.346915 | 0.750000 | 1 | 0 | 0.492186 | 1.193738 | positive_core_student_teacher_recovery |
| S1 | True | student_conservative_tail_score | top_decisive | 0.020000 | 7 | 0.524269 | 0.571429 | 2 | 1 | 0.705008 | 0.731307 | positive_core_student_teacher_recovery |
| S2 | True | student_teacher_top_mean | top_all | 0.080000 | 36 | 3.544362 | 0.611111 | 4 | 2 | 5.172625 | 6.387336 | positive_core_student_teacher_recovery |
| S3 | True | student_teacher_top_mean | top_all | 0.010000 | 4 | 0.577064 | 0.750000 | 1 | 1 | 0.650631 | 0.612526 | positive_core_student_teacher_recovery |
| S4 | True | student_conservative_tail_score | top_decisive | 0.020000 | 6 | 0.729831 | 1.000000 | 4 | 0 | 0.791765 | 2.517671 | positive_core_student_teacher_recovery |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 16 | -0.688463 | -0.043029 | 0.312500 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id02 | 14 | -0.769029 | -0.054931 | 0.428571 | Q1,Q2,S1,S2,S3,S4 |
| id03 | 14 | -0.521355 | -0.037240 | 0.214286 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id04 | 16 | -0.060215 | -0.003763 | 0.375000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id05 | 9 | 0.056396 | 0.006266 | 0.555556 | Q1,Q2,Q3,S1,S2,S4 |
| id06 | 12 | 0.384808 | 0.032067 | 0.416667 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id07 | 13 | -0.004231 | -0.000325 | 0.461538 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id08 | 20 | -1.662254 | -0.083113 | 0.200000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id09 | 11 | -0.104154 | -0.009469 | 0.636364 | Q1,Q2,Q3,S2,S3,S4 |
| id10 | 10 | -0.267477 | -0.026748 | 0.200000 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 30 | -1.076791 | -0.035893 | 0.400000 | 11.000000 | 19.000000 | 6 | 4 |
| Q2 | 19 | -0.750073 | -0.039478 | 0.315789 | 7.000000 | 12.000000 | 5 | 5 |
| Q3 | 9 | 0.018431 | 0.002048 | 0.333333 | 0.000000 | 9.000000 | 3 | 6 |
| S1 | 18 | -1.325147 | -0.073619 | 0.111111 | 8.000000 | 10.000000 | 0 | 9 |
| S2 | 33 | 0.244117 | 0.007397 | 0.515152 | 14.000000 | 19.000000 | 7 | 3 |
| S3 | 15 | -0.671943 | -0.044796 | 0.266667 | 10.000000 | 5.000000 | 3 | 6 |
| S4 | 11 | -0.074567 | -0.006779 | 0.454545 | 9.000000 | 2.000000 | 5 | 4 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | student_pessimistic_mean | hold | 0.000000 | 1.000000 | -1.076791 | 6 | 4 | 0.400000 | failed_core_student_subjectheldout |
| Q2 | False | student_conservative_tail_score | hold | 0.000000 | 1.000000 | -0.750073 | 5 | 5 | 0.315789 | failed_core_student_subjectheldout |
| Q3 | False | student_teacher_mean | hold | 0.000000 | 0.900000 | 0.018431 | 3 | 6 | 0.333333 | failed_core_student_subjectheldout |
| S1 | False | student_conservative_tail_score | hold | 0.000000 | 0.900000 | -1.325147 | 0 | 9 | 0.111111 | failed_core_student_subjectheldout |
| S2 | False | student_teacher_top_mean | hold | 0.000000 | 1.000000 | 0.244117 | 7 | 3 | 0.515152 | failed_core_student_subjectheldout |
| S3 | False | student_teacher_top_mean | hold | 0.000000 | 0.900000 | -0.671943 | 3 | 6 | 0.266667 | failed_core_student_subjectheldout |
| S4 | False | student_conservative_tail_score | hold | 0.000000 | 1.000000 | -0.074567 | 5 | 4 | 0.454545 | failed_core_student_subjectheldout |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | student_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | student_teacher_top_mean | top_all | 0.080000 | 36 | 3.544362 | 0.611111 | 4 | 2 | 5.172625 | 5.917284 | 6.387336 |
| S2 | student_teacher_top_mean | top_decisive | 0.080000 | 29 | 3.679135 | 0.655172 | 4 | 2 | 4.794755 | 2.801669 | 5.940086 |
| S2 | student_teacher_top_mean | top_decisive | 0.100000 | 36 | 2.978931 | 0.583333 | 4 | 2 | 3.997674 | 1.710785 | 4.628709 |
| S2 | student_teacher_top_mean | top_all | 0.100000 | 45 | 1.789904 | 0.511111 | 4 | 2 | 3.298986 | 1.735153 | 3.019312 |
| S2 | student_teacher_top_mean | top_decisive | 0.060000 | 22 | 1.814903 | 0.590909 | 3 | 2 | 3.191990 | 2.527494 | 2.877284 |
| S2 | student_teacher_top_mean | top_decisive | 0.040000 | 15 | 1.790628 | 0.666667 | 3 | 2 | 2.837517 | 2.464601 | 2.658807 |
| S4 | student_conservative_tail_score | top_decisive | 0.020000 | 6 | 0.729831 | 1.000000 | 4 | 0 | 0.791765 | 1.655135 | 2.517671 |
| Q2 | student_conservative_tail_score | top_decisive | 0.060000 | 22 | 1.342671 | 0.590909 | 5 | 2 | 2.164325 | 2.802230 | 2.281974 |
| Q2 | student_conservative_tail_score | top_all | 0.060000 | 27 | 1.295604 | 0.555556 | 5 | 2 | 1.964946 | 2.658666 | 2.093201 |
| S1 | student_teacher_top_mean | top_decisive | 0.140000 | 49 | 1.301578 | 0.469388 | 4 | 2 | 2.511754 | 1.223184 | 2.002524 |
| S2 | student_teacher_top_mean | top_all | 0.040000 | 18 | 2.081271 | 0.611111 | 3 | 3 | 2.995652 | 1.716238 | 1.987475 |
| S4 | student_conservative_tail_score | top_decisive | 0.010000 | 3 | 0.492028 | 1.000000 | 2 | 0 | 0.549465 | 1.783490 | 1.714737 |
| S4 | student_pessimistic_mean | top_decisive | 0.010000 | 3 | 0.492028 | 1.000000 | 2 | 0 | 0.481583 | 1.223451 | 1.608160 |
| S2 | student_teacher_top_mean | top_all | 0.060000 | 27 | 1.860941 | 0.555556 | 3 | 3 | 2.778361 | 1.300682 | 1.577361 |
| S4 | student_teacher_top_mean | top_decisive | 0.060000 | 19 | 0.553488 | 0.526316 | 3 | 1 | 1.394551 | 1.305210 | 1.360531 |
| Q3 | student_teacher_mean | top_all | 0.010000 | 4 | 0.346915 | 0.750000 | 1 | 0 | 0.492186 | 1.282120 | 1.193738 |
| Q1 | student_pessimistic_mean | top_all | 0.180000 | 81 | 1.013147 | 0.555556 | 6 | 3 | 2.210001 | 2.260060 | 1.175044 |
| Q1 | student_pessimistic_mean | top_decisive | 0.140000 | 47 | 1.256708 | 0.574468 | 6 | 3 | 1.778225 | 1.165004 | 1.041496 |
| Q3 | student_teacher_mean | top_decisive | 0.010000 | 3 | 0.319561 | 0.666667 | 1 | 0 | 0.296072 | 0.897333 | 0.985630 |
| S1 | student_teacher_top_mean | top_decisive | 0.060000 | 21 | 0.971068 | 0.476190 | 2 | 2 | 1.952136 | 1.349905 | 0.924343 |
| Q1 | student_pessimistic_mean | top_decisive | 0.010000 | 3 | 0.001417 | 0.666667 | 1 | 0 | 0.403113 | 2.469054 | 0.918176 |
| S1 | student_teacher_mean | top_all | 0.040000 | 18 | 0.208007 | 0.500000 | 3 | 1 | 1.091086 | 1.431533 | 0.847621 |
| S1 | student_conservative_tail_score | top_decisive | 0.020000 | 7 | 0.524269 | 0.571429 | 2 | 1 | 0.705008 | 1.377302 | 0.731307 |
| S1 | student_teacher_top_mean | top_decisive | 0.040000 | 14 | 0.787683 | 0.500000 | 2 | 2 | 1.717190 | 2.062966 | 0.696210 |
| S4 | student_recovered_tail_score | top_decisive | 0.020000 | 6 | 0.431373 | 0.833333 | 3 | 1 | 0.440950 | 0.640725 | 0.682345 |
| Q2 | student_pessimistic_mean | top_decisive | 0.080000 | 30 | 0.157993 | 0.433333 | 6 | 2 | 1.462632 | 1.225938 | 0.681765 |
| Q3 | student_teacher_top_mean | top_all | 0.140000 | 63 | 0.900560 | 0.507937 | 5 | 3 | 1.972877 | 1.940875 | 0.654718 |
| S2 | student_conservative_tail_score | top_decisive | 0.080000 | 29 | 0.647206 | 0.379310 | 5 | 3 | 2.366821 | 2.295412 | 0.640239 |
| Q3 | student_pessimistic_mean | top_all | 0.010000 | 4 | 0.039293 | 0.500000 | 1 | 0 | 0.305186 | 0.607926 | 0.634253 |
| Q2 | student_conservative_tail_score | top_all | 0.080000 | 36 | 0.882361 | 0.500000 | 6 | 3 | 1.567017 | 2.021485 | 0.628809 |
| S3 | student_teacher_top_mean | top_all | 0.010000 | 4 | 0.577064 | 0.750000 | 1 | 1 | 0.650631 | 1.671633 | 0.612526 |
| S1 | student_recovered_tail_score | top_decisive | 0.020000 | 7 | 0.524269 | 0.571429 | 2 | 1 | 0.589740 | 0.646475 | 0.576752 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_core_student_recovers_masked_tail_teacher_anchor_free_2648e9b5_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.30721483708484554, 'probability_max': 0.7048393792579564}`

## 해석

좋은 결과:

```text
core student가 teacher의 hidden action-tail representation을 subject-heldout에서도
release-safe하게 복원하면, HS-JEPA core가 frontier hidden structure를 일부 재발견했다는 증거다.
```

나쁜 결과:

```text
teacher representation 자체는 강하지만 student가 subject-heldout에서 무너지면,
현재 frontier는 core-only representation이 아니라 action-aware masked-view teacher boundary에 의존한다.
```
