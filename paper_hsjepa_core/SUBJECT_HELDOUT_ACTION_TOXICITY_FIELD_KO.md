# HS-JEPA Diagnostic Adapter: Subject-Heldout Action Toxicity Field

## 한 줄 요약

target-route policy를 고르는 대신, row-target-action 자체가 건강한지 예측했다.
각 cell에는 raw release와 inverse-toxic action 후보를 모두 만들고,
HS-JEPA core context가 어떤 action을 믿어야 하는지 subject-heldout으로 검증했다.

```text
masked world-state residual/energy
  -> listener-conditioned action context
  -> subject-heldout action toxicity field
  -> target-specific stable release
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden world-state representation

이 문서의 역할
  = 그 representation이 row-target action toxicity를 subject-heldout에서 구분하는지 검증한다.
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_heldout_action_toxicity_negative_or_fragile`
- action-health AUC: `0.597026`
- action-health AP: `0.567465`
- nested heldout selected cells: `112`
- nested heldout gain sum: `-5.538044`
- nested positive subjects: `2`
- nested negative subjects: `8`
- stable targets: `[]`
- stable OOF gain sum: `0.000000`
- released test cells: `0`

## Health Model Metrics

| metric | value |
| --- | --- |
| action_health_auc | 0.597026 |
| action_health_ap | 0.567465 |
| action_health_base_rate | 0.500000 |
| feature_count | 444.000000 |
| train_action_modes | 6300.000000 |
| test_action_modes | 3500.000000 |

## Full-OOF Chosen Policies

| target | accepted | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | raw_action_count | inverse_action_count | gain_lift_vs_null | action_health_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| Q2 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| Q3 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| S1 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| S2 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| S3 | False | hold | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0 | 0.000000 | 0.000000 | no_action_health_policy_passed |
| S4 | True | top_health_decisive | 0.180000 | 57 | 1.190091 | 0.631579 | 6 | 2 | 17 | 40 | 2.802809 | 2.501265 | positive_subjectheldout_health_gain |

## Nested Heldout Subject Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets | held_targets |
| --- | --- | --- | --- | --- | --- | --- |
| id01 | 1 | -0.478945 | -0.478945 | 0.000000 | S1,S4 | Q1,Q2,Q3,S2,S3 |
| id02 | 10 | 0.350943 | 0.035094 | 0.700000 | S1,S4 | Q1,Q2,Q3,S2,S3 |
| id03 | 6 | -0.169022 | -0.028170 | 0.333333 | S1,S4 | Q1,Q2,Q3,S2,S3 |
| id04 | 16 | -1.596476 | -0.099780 | 0.375000 | Q2,S1,S4 | Q1,Q3,S2,S3 |
| id05 | 17 | -0.296038 | -0.017414 | 0.470588 | Q1,Q2,S4 | Q3,S1,S2,S3 |
| id06 | 10 | 1.295478 | 0.129548 | 0.900000 | S1,S4 | Q1,Q2,Q3,S2,S3 |
| id07 | 10 | -0.304796 | -0.030480 | 0.600000 | S1,S4 | Q1,Q2,Q3,S2,S3 |
| id08 | 16 | -0.785328 | -0.049083 | 0.625000 | Q3,S1,S4 | Q1,Q2,S2,S3 |
| id09 | 15 | -2.084629 | -0.138975 | 0.266667 | Q1,Q2,S1 | Q3,S2,S3,S4 |
| id10 | 11 | -1.469231 | -0.133566 | 0.272727 | Q1,S1,S4 | Q2,Q3,S2,S3 |

## Nested Heldout Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 12 | -0.814094 | -0.067841 | 0.250000 | 4.000000 | 8.000000 | 0 | 3 |
| Q2 | 18 | -2.360712 | -0.131151 | 0.222222 | 7.000000 | 11.000000 | 0 | 3 |
| Q3 | 1 | -0.408512 | -0.408512 | 0.000000 | 1.000000 | 0.000000 | 0 | 1 |
| S1 | 19 | -2.717411 | -0.143022 | 0.526316 | 11.000000 | 8.000000 | 4 | 5 |
| S4 | 62 | 0.762686 | 0.012301 | 0.612903 | 29.000000 | 33.000000 | 4 | 4 |

## Route Decision Frequency

| target | heldout_accept_rate | top_policy | top_fraction | top_policy_count | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.300000 | hold | 0.000000 | 7 | -0.814094 | 0 | 3 |
| Q2 | 0.300000 | hold | 0.000000 | 7 | -2.360712 | 0 | 3 |
| Q3 | 0.100000 | hold | 0.000000 | 9 | -0.408512 | 0 | 1 |
| S1 | 0.900000 | top_health_all | 0.020000 | 6 | -2.717411 | 4 | 5 |
| S2 | 0.000000 | hold | 0.000000 | 10 | 0.000000 | 0 | 0 |
| S3 | 0.000000 | hold | 0.000000 | 10 | 0.000000 | 0 | 0 |
| S4 | 0.900000 | top_health_all | 0.180000 | 3 | 0.762686 | 4 | 4 |

## Stable Policies Used For Candidate

| target | accepted | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | hold | 0.000000 | 0.300000 | -0.814094 | 0 | 3 | 0.250000 | failed_subject_heldout_action_toxicity |
| Q2 | False | hold | 0.000000 | 0.300000 | -2.360712 | 0 | 3 | 0.222222 | failed_subject_heldout_action_toxicity |
| Q3 | False | hold | 0.000000 | 0.100000 | -0.408512 | 0 | 1 | 0.000000 | failed_subject_heldout_action_toxicity |
| S1 | False | hold | 0.000000 | 0.900000 | -2.717411 | 4 | 5 | 0.526316 | failed_subject_heldout_action_toxicity |
| S2 | False | hold | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 | failed_subject_heldout_action_toxicity |
| S3 | False | hold | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 | failed_subject_heldout_action_toxicity |
| S4 | False | hold | 0.000000 | 0.900000 | 0.762686 | 4 | 4 | 0.612903 | failed_subject_heldout_action_toxicity |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_heldout_action_toxicity_field_anchor_free_84bb9983_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.4955555555555556, 'probability_max': 0.6822222222222222}`

## 해석

좋은 결과:

```text
subject-heldout action-health score와 nested heldout policy가 모두 양수이면,
HS-JEPA core representation은 route policy보다 더 세밀한 action toxicity field를 가진다.
```

나쁜 결과:

```text
action-health AUC는 양수인데 nested heldout gain이 음수이면,
core representation은 action toxicity를 약하게 읽지만 release-grade decoder가 아직 없다.
```

현재 결론:

```text
이번 결과는 negative/fragile이다.
subject-heldout action-health AUC/AP는 양수라 core representation이 독성 단서를 읽기는 한다.
하지만 nested subject-heldout release gain은 음수이고 stable target은 없다.

따라서 HS-JEPA core representation만으로 action을 release하는 decoder는 아직 부족하다.
논문에서는 core가 hidden action-health geometry를 제공한다는 점과,
release-grade adapter에는 subject-invariant responsibility/assignment가 추가로 필요하다는 점을 함께 주장해야 한다.
```
