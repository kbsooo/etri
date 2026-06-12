# HS-JEPA Diagnostic Adapter: Subject-Relative Responsibility Assignment

## 한 줄 요약

subject-heldout action-health score는 양수였지만 절대 top-k release는 무너졌다.
이번 실험은 같은 score를 subject-relative rank, target-relative rank, raw-vs-inverse pairwise
responsibility로 재해석해서 calibration 문제가 병목인지 확인했다.

```text
masked world-state residual/energy
  -> subject-heldout action-health score
  -> subject-relative / pairwise responsibility coordinates
  -> nested subject-heldout assignment stress
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden action-health geometry

이 문서의 역할
  = 그 geometry를 어떤 coordinate system으로 action assignment에 번역해야 하는지 검증한다.
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_relative_assignment_negative_or_fragile`
- action-health AUC: `0.597026`
- action-health AP: `0.567465`
- best score coordinate: `pairwise_responsibility`
- best nested gain: `-1.188289`
- best positive/negative subjects: `5` / `5`
- stable targets: `['S4']`
- stable OOF gain sum: `0.825558`
- released test cells: `8`

## Responsibility Coordinate Summary

| score_col | nested_selected_cells | nested_gain_sum | nested_positive_gain_rate | positive_subjects | negative_subjects | survival_score |
| --- | --- | --- | --- | --- | --- | --- |
| pairwise_responsibility | 97 | -1.188289 | 0.587629 | 5 | 5 | -2.438289 |
| health_score | 81 | -3.528860 | 0.530864 | 3 | 7 | -8.278860 |
| support_aligned_responsibility | 128 | -5.309210 | 0.523438 | 4 | 6 | -8.309210 |
| conservative_pair_best_responsibility | 78 | -5.778085 | 0.500000 | 4 | 6 | -8.778085 |
| subject_relative_responsibility | 113 | -10.210479 | 0.504425 | 3 | 7 | -14.960479 |

## Best Coordinate Full-OOF Policies

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | raw_action_count | inverse_action_count | gain_lift_vs_null | assignment_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | pairwise_responsibility | top_responsibility_pairbest | 0.080000 | 36 | 2.456329 | 0.666667 | 8 | 1 | 27 | 9 | 3.429825 | 5.981642 | positive_subject_relative_responsibility |
| Q2 | True | pairwise_responsibility | top_responsibility_decisive | 0.040000 | 15 | 0.288951 | 0.666667 | 2 | 3 | 12 | 3 | 0.560691 | -1.223635 | positive_subject_relative_responsibility |
| Q3 | False | pairwise_responsibility | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_subject_relative_policy_passed |
| S1 | True | pairwise_responsibility | top_responsibility_pairbest | 0.010000 | 4 | 0.905069 | 1.000000 | 4 | 0 | 3 | 1 | 0.974675 | 3.199886 | positive_subject_relative_responsibility |
| S2 | False | pairwise_responsibility | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_subject_relative_policy_passed |
| S3 | False | pairwise_responsibility | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_subject_relative_policy_passed |
| S4 | True | pairwise_responsibility | top_responsibility_decisive | 0.040000 | 13 | 0.825558 | 0.692308 | 4 | 1 | 8 | 5 | 1.201833 | 2.092346 | positive_subject_relative_responsibility |

## Best Coordinate Nested Heldout Subject Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets | held_targets |
| --- | --- | --- | --- | --- | --- | --- |
| id01 | 6 | -0.614828 | -0.102471 | 0.333333 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id02 | 9 | 1.341086 | 0.149010 | 0.888889 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id03 | 7 | 1.008874 | 0.144125 | 0.857143 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id04 | 14 | -1.167407 | -0.083386 | 0.357143 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id05 | 14 | -1.997314 | -0.142665 | 0.500000 | Q1,Q2,S1,S2,S3,S4 | Q3 |
| id06 | 9 | 0.788203 | 0.087578 | 0.666667 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id07 | 14 | 0.774065 | 0.055290 | 0.642857 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id08 | 8 | 0.272814 | 0.034102 | 0.750000 | Q1,Q3,S1,S4 | Q2,S2,S3 |
| id09 | 8 | -0.845311 | -0.105664 | 0.375000 | Q1,Q2,S1,S4 | Q3,S2,S3 |
| id10 | 8 | -0.748472 | -0.093559 | 0.625000 | Q1,Q2,S1,S4 | Q3,S2,S3 |

## Best Coordinate Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 36 | 1.407841 | 0.039107 | 0.583333 | 26.000000 | 10.000000 | 8 | 2 |
| Q2 | 26 | -1.326224 | -0.051009 | 0.500000 | 15.000000 | 11.000000 | 3 | 6 |
| Q3 | 1 | -0.408512 | -0.408512 | 0.000000 | 1.000000 | 0.000000 | 0 | 1 |
| S1 | 10 | -0.323194 | -0.032319 | 0.700000 | 7.000000 | 3.000000 | 7 | 3 |
| S2 | 1 | -1.331706 | -1.331706 | 0.000000 | 1.000000 | 0.000000 | 0 | 1 |
| S3 | 2 | -0.765639 | -0.382819 | 0.500000 | 2.000000 | 0.000000 | 0 | 1 |
| S4 | 21 | 1.559146 | 0.074245 | 0.714286 | 12.000000 | 9.000000 | 6 | 3 |

## Route Decision Frequency

| score_col | target | heldout_accept_rate | top_policy | top_fraction | top_policy_count | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pairwise_responsibility | Q1 | 1.000000 | top_responsibility_pairbest | 0.080000 | 4 | 1.407841 | 8 | 2 |
| pairwise_responsibility | Q2 | 0.900000 | top_responsibility_decisive | 0.040000 | 5 | -1.326224 | 3 | 6 |
| pairwise_responsibility | Q3 | 0.100000 | hold | 0.000000 | 9 | -0.408512 | 0 | 1 |
| pairwise_responsibility | S1 | 1.000000 | top_responsibility_all | 0.010000 | 7 | -0.323194 | 7 | 3 |
| pairwise_responsibility | S2 | 0.100000 | hold | 0.000000 | 9 | -1.331706 | 0 | 1 |
| pairwise_responsibility | S3 | 0.100000 | hold | 0.000000 | 9 | -0.765639 | 0 | 1 |
| pairwise_responsibility | S4 | 1.000000 | top_responsibility_decisive | 0.040000 | 4 | 1.559146 | 6 | 3 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | pairwise_responsibility | hold | 0.000000 | 1.000000 | 1.407841 | 8 | 2 | 0.583333 | failed_subject_relative_assignment |
| Q2 | False | pairwise_responsibility | hold | 0.000000 | 0.900000 | -1.326224 | 3 | 6 | 0.500000 | failed_subject_relative_assignment |
| Q3 | False | pairwise_responsibility | hold | 0.000000 | 0.100000 | -0.408512 | 0 | 1 | 0.000000 | failed_subject_relative_assignment |
| S1 | False | pairwise_responsibility | hold | 0.000000 | 1.000000 | -0.323194 | 7 | 3 | 0.700000 | failed_subject_relative_assignment |
| S2 | False | pairwise_responsibility | hold | 0.000000 | 0.100000 | -1.331706 | 0 | 1 | 0.000000 | failed_subject_relative_assignment |
| S3 | False | pairwise_responsibility | hold | 0.000000 | 0.100000 | -0.765639 | 0 | 1 | 0.500000 | failed_subject_relative_assignment |
| S4 | True | pairwise_responsibility | top_responsibility_decisive | 0.040000 | 1.000000 | 1.559146 | 6 | 3 | 0.714286 | subject_relative_assignment_stable |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_relative_responsibility_assignment_anchor_free_eecb4e37_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.4955555555555556, 'probability_max': 0.81369883780552}`

## 해석

좋은 결과:

```text
subject-relative responsibility가 nested heldout gain을 양수로 바꾸면,
HS-JEPA core signal의 병목은 signal absence가 아니라 calibration coordinate였다.
```

나쁜 결과:

```text
relative coordinate도 음수이면,
현재 core action-health geometry는 action assignment를 만들 만큼 충분히 안정적이지 않다.
```

현재 결론:

```text
이번 결과는 negative/fragile이지만 이전 실패보다 구조적으로 낫다.
absolute health score release는 nested heldout에서 크게 무너졌고,
pairwise responsibility coordinate가 손실을 크게 줄였다.

따라서 HS-JEPA core signal의 일부 병목은 calibration coordinate였다.
다만 전체 gain은 아직 음수이고 S4만 strict stable target으로 남았으므로,
subject-relative assignment alone을 release-grade decoder라고 주장하면 안 된다.
다음 big bet은 pairwise responsibility를 multi-row episode / listener responsibility와 결합하는 것이다.
```
