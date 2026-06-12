# Subject-Normalized Tail Field Core

## 한 줄 요약

absolute action gain을 바로 예측하지 않고, subject-target-action route 내부의 tail scale로 정규화한
`이 사람 기준으로 나쁜 action인가`를 예측했다.

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core representation을 subject-invariant tail representation으로 재정의하는 core-decoder boundary 실험**이다.

```text
visible human context
  -> hidden action-health / residual-energy representation
  -> subject-normalized tail field
  -> row-target action assignment
```

## 왜 필요한가

Tail-Safe Expected Utility Core는 full OOF utility를 크게 올렸지만,
subject-heldout에서는 S-target tail이 무너지며 negative였다.

이 실험의 가설:

```text
absolute gain은 subject별 tail scale을 섞어 놓기 때문에 subject shift에서 깨진다.
HS-JEPA가 읽어야 할 target representation은 absolute gain이 아니라
subject-normalized badness / relative tail field다.
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_normalized_tail_field_oof_positive_subjectheldout_fragile`
- full OOF selected gain: `2.898288`
- nested heldout gain: `-3.812519`
- stable targets: `['Q2', 'S4']`
- stable OOF gain: `1.543893`
- candidate policy source: `stable_subjectheldout`
- released test cells: `67`

## Relative Tail Model Metrics

| metric | value |
| --- | --- |
| normalized_gain_mae | 0.875755 |
| relative_tail_loss_mae | 0.554101 |
| relative_positive_auc | 0.525853 |
| relative_positive_ap | 0.508418 |
| relative_toxic_tail_auc | 0.740461 |
| relative_toxic_tail_ap | 0.314014 |
| relative_toxic_tail_rate | 0.172698 |
| absolute_gain_sum_all_modes | -141.439797 |

## Full OOF Chosen Policies

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | subject_normalized_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | predicted_subject_normalized_gain | top_all | 0.020000 | 9 | 1.146289 | 0.666667 | 5 | 0 | 1.257432 | 3.201323 | positive_subject_normalized_tail_policy |
| Q2 | True | subject_normalized_pessimistic_utility | top_all | 0.250000 | 112 | 1.222540 | 0.580357 | 8 | 2 | 4.089747 | 3.734823 | positive_subject_normalized_tail_policy |
| Q3 | True | subject_relative_health_score | top_decisive | 0.040000 | 14 | 0.198591 | 0.714286 | 3 | 0 | 0.260187 | 1.164413 | positive_subject_normalized_tail_policy |
| S1 | False | predicted_subject_normalized_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_subject_normalized_policy_passed |
| S2 | True | subject_relative_health_score | top_decisive | 0.020000 | 7 | 0.009515 | 0.714286 | 3 | 1 | 0.481058 | 0.296724 | positive_subject_normalized_tail_policy |
| S3 | False | predicted_subject_normalized_gain | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0.000000 | 0.000000 | no_subject_normalized_policy_passed |
| S4 | True | subject_relative_health_score | top_all | 0.020000 | 9 | 0.321352 | 0.777778 | 3 | 0 | 0.327269 | 1.383589 | positive_subject_normalized_tail_policy |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 18 | -0.598563 | -0.033253 | 0.611111 | Q1,Q2,Q3,S1,S2,S4 |
| id02 | 20 | -0.445021 | -0.022251 | 0.400000 | Q1,Q2,Q3,S1,S2,S4 |
| id03 | 15 | 0.383119 | 0.025541 | 0.666667 | Q1,Q2,Q3,S1,S2,S4 |
| id04 | 21 | 0.791743 | 0.037702 | 0.761905 | Q1,Q2,Q3,S1,S2,S4 |
| id05 | 35 | -1.338250 | -0.038236 | 0.400000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id06 | 30 | -0.611067 | -0.020369 | 0.366667 | Q1,Q2,Q3,S1,S2,S4 |
| id07 | 32 | -1.152286 | -0.036009 | 0.406250 | Q1,Q2,Q3,S1,S4 |
| id08 | 35 | -0.291670 | -0.008333 | 0.457143 | Q1,Q2,Q3,S4 |
| id09 | 18 | -0.537776 | -0.029876 | 0.444444 | Q1,Q2,Q3,S1,S2,S4 |
| id10 | 15 | -0.012748 | -0.000850 | 0.600000 | Q1,Q2,Q3,S1,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 46 | -0.733371 | -0.015943 | 0.434783 | 31.000000 | 15.000000 | 4 | 6 |
| Q2 | 101 | 0.235969 | 0.002336 | 0.524752 | 33.000000 | 68.000000 | 6 | 4 |
| Q3 | 36 | -1.255660 | -0.034879 | 0.416667 | 24.000000 | 12.000000 | 3 | 7 |
| S1 | 10 | -0.819454 | -0.081945 | 0.500000 | 5.000000 | 5.000000 | 4 | 5 |
| S2 | 8 | -0.279404 | -0.034925 | 0.500000 | 2.000000 | 6.000000 | 3 | 4 |
| S3 | 11 | -1.176402 | -0.106946 | 0.181818 | 10.000000 | 1.000000 | 0 | 1 |
| S4 | 27 | 0.215803 | 0.007993 | 0.629630 | 18.000000 | 9.000000 | 6 | 3 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | predicted_subject_normalized_gain | hold | 0.000000 | 1.000000 | -0.733371 | 4 | 6 | 0.434783 | failed_subject_normalized_tail_stress |
| Q2 | True | subject_normalized_pessimistic_utility | top_all | 0.250000 | 1.000000 | 0.235969 | 6 | 4 | 0.524752 | subject_normalized_tail_subjectheldout_stable |
| Q3 | False | subject_relative_health_score | hold | 0.000000 | 1.000000 | -1.255660 | 3 | 7 | 0.416667 | failed_subject_normalized_tail_stress |
| S1 | False | predicted_subject_normalized_gain | hold | 0.000000 | 0.900000 | -0.819454 | 4 | 5 | 0.500000 | failed_subject_normalized_tail_stress |
| S2 | False | subject_relative_health_score | hold | 0.000000 | 0.700000 | -0.279404 | 3 | 4 | 0.500000 | failed_subject_normalized_tail_stress |
| S3 | False | predicted_subject_normalized_gain | hold | 0.000000 | 0.100000 | -1.176402 | 0 | 1 | 0.181818 | failed_subject_normalized_tail_stress |
| S4 | True | subject_relative_health_score | top_all | 0.020000 | 1.000000 | 0.215803 | 6 | 3 | 0.629630 | subject_normalized_tail_subjectheldout_stable |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | subject_normalized_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | subject_normalized_pessimistic_utility | top_all | 0.250000 | 112 | 1.222540 | 0.580357 | 8 | 2 | 4.089747 | 1.815273 | 3.734823 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.020000 | 9 | 1.146289 | 0.666667 | 5 | 0 | 1.257432 | 1.639830 | 3.201323 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.250000 | 112 | 1.967222 | 0.580357 | 6 | 3 | 3.936019 | 2.153581 | 3.185552 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.100000 | 45 | 1.847238 | 0.577778 | 5 | 2 | 2.374509 | 1.744973 | 2.807059 |
| Q2 | subject_relative_health_score | top_decisive | 0.140000 | 52 | 0.448718 | 0.634615 | 7 | 1 | 2.209787 | 2.062198 | 2.620218 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.180000 | 61 | 2.030773 | 0.590164 | 6 | 3 | 2.685134 | 2.305035 | 2.581742 |
| Q2 | subject_relative_health_score | top_decisive | 0.180000 | 67 | 0.806745 | 0.656716 | 7 | 2 | 2.846485 | 1.912410 | 2.465980 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.020000 | 7 | 1.066459 | 0.714286 | 4 | 1 | 1.410495 | 2.584896 | 2.280990 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.100000 | 34 | 1.548333 | 0.558824 | 6 | 3 | 2.666873 | 1.954311 | 2.039336 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.040000 | 13 | 1.502827 | 0.692308 | 4 | 2 | 1.770806 | 2.120082 | 2.004257 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.140000 | 63 | 1.649882 | 0.571429 | 5 | 3 | 2.594979 | 1.793820 | 1.885236 |
| Q2 | subject_normalized_pessimistic_utility | top_decisive | 0.180000 | 67 | 0.719006 | 0.537313 | 7 | 3 | 3.384712 | 1.754468 | 1.775462 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.080000 | 27 | 1.720971 | 0.555556 | 4 | 3 | 2.430545 | 2.345697 | 1.728143 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.060000 | 20 | 1.774552 | 0.600000 | 4 | 3 | 2.338340 | 2.133250 | 1.716629 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.180000 | 81 | 1.562423 | 0.543210 | 6 | 3 | 2.244208 | 0.897806 | 1.690276 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.080000 | 36 | 1.663060 | 0.583333 | 4 | 3 | 2.288531 | 2.291157 | 1.592525 |
| Q2 | subject_relative_health_score | top_decisive | 0.020000 | 7 | 0.306083 | 0.857143 | 3 | 0 | 0.589819 | 1.125843 | 1.579870 |
| Q2 | subject_normalized_pessimistic_utility | top_decisive | 0.250000 | 93 | 0.613689 | 0.516129 | 7 | 3 | 3.088663 | 1.382143 | 1.457343 |
| Q1 | predicted_subject_normalized_gain | top_decisive | 0.250000 | 84 | 1.602169 | 0.559524 | 6 | 4 | 3.100825 | 1.451808 | 1.421721 |
| S4 | subject_relative_health_score | top_all | 0.020000 | 9 | 0.321352 | 0.777778 | 3 | 0 | 0.327269 | 0.731621 | 1.383589 |
| Q2 | subject_relative_health_score | top_decisive | 0.060000 | 22 | 0.344367 | 0.681818 | 3 | 0 | 0.375238 | 0.416699 | 1.371206 |
| Q2 | subject_normalized_pessimistic_utility | top_decisive | 0.140000 | 52 | 0.808096 | 0.576923 | 7 | 3 | 2.400591 | 1.900141 | 1.350668 |
| Q2 | subject_normalized_utility | top_decisive | 0.250000 | 93 | 0.211645 | 0.516129 | 7 | 3 | 3.631579 | 1.274966 | 1.341042 |
| Q1 | predicted_subject_normalized_gain | top_all | 0.060000 | 27 | 1.652836 | 0.629630 | 4 | 3 | 1.736377 | 2.052625 | 1.261565 |
| Q2 | subject_normalized_utility | top_all | 0.250000 | 112 | 0.494135 | 0.562500 | 7 | 3 | 2.861169 | 1.134448 | 1.194537 |
| S4 | subject_relative_health_score | top_all | 0.250000 | 112 | -0.010099 | 0.553571 | 8 | 2 | 1.912647 | 0.849490 | 1.182189 |
| Q3 | subject_relative_health_score | top_decisive | 0.040000 | 14 | 0.198591 | 0.714286 | 3 | 0 | 0.260187 | 0.367892 | 1.164413 |
| Q2 | subject_normalized_pessimistic_utility | top_decisive | 0.040000 | 15 | 0.515556 | 0.666667 | 4 | 1 | 0.793949 | 0.738176 | 1.157476 |
| S4 | subject_relative_health_score | top_decisive | 0.080000 | 25 | 0.244703 | 0.640000 | 5 | 1 | 0.846045 | 0.583523 | 1.090051 |
| Q2 | subject_normalized_pessimistic_utility | top_all | 0.180000 | 81 | 0.589787 | 0.530864 | 6 | 3 | 2.692998 | 1.670531 | 1.054116 |
| S4 | subject_relative_health_score | top_decisive | 0.060000 | 19 | 0.314497 | 0.684211 | 5 | 1 | 0.502777 | 0.432787 | 0.964011 |
| Q2 | subject_normalized_pessimistic_utility | top_decisive | 0.100000 | 37 | 0.897115 | 0.648649 | 7 | 3 | 1.624115 | 0.976648 | 0.919738 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_normalized_tail_field_anchor_free_d4bf6a61_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.4955555555555556, 'probability_max': 0.6822222222222222}`

## 해석

좋은 결과:

```text
subject-normalized tail field가 nested heldout damage를 줄이면,
HS-JEPA의 핵심 target representation은 absolute action utility가 아니라
human-specific relative badness라는 주장이 강해진다.
```

나쁜 결과:

```text
정규화해도 heldout tail이 무너지면,
현재 residual/energy core는 subject-relative tail magnitude를 충분히 표현하지 못한다.
그 경우 다음 문제는 feature 추가가 아니라 sequence/episode-level state target을 다시 정의하는 것이다.
```
