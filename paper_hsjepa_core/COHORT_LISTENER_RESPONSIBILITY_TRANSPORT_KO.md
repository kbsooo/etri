# Cohort Listener Responsibility Transport

## 한 줄 요약

Cell-level threshold 대신, HS-JEPA world-model subject fingerprint가 비슷한 peer subject에서
target별 listener responsibility rule을 빌려와 held-out subject/test subject에 전이했다.

```text
HS-JEPA world-model subject fingerprint
  -> nearest peer subjects
  -> peer target-listener responsibility rule
  -> held-out subject row-target action veto
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 subject/cohort-level
action responsibility로 번역하는 adapter 실험이다.

이전 실패는 cell-level residual threshold가 subject-LOO에서 무너진다는 것이었다.
이번 실험은 decision level을 cell에서 subject/cohort로 올린다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Objective Board

| objective | neighbors | oof_gain_delta | oof_kept_gain_sum | non_all_assignments | positive_subjects | negative_subjects | min_subject_improvement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| subject_balanced_listener | 1 | -2.345507 | 2.681536 | 4 | 0 | 3 | -1.714630 |
| subject_balanced_listener | 4 | -2.365028 | 2.662016 | 5 | 1 | 4 | -1.513232 |
| subject_balanced_listener | 3 | -2.377918 | 2.649125 | 5 | 1 | 4 | -1.513232 |
| subject_balanced_listener | 2 | -2.701324 | 2.325719 | 5 | 0 | 4 | -1.714630 |
| subject_balanced_listener | 5 | -3.281044 | 1.746000 | 6 | 1 | 4 | -1.513232 |
| subject_balanced_listener | 6 | -3.281044 | 1.746000 | 6 | 1 | 4 | -1.513232 |

## Release Setting

- release objective: `subject_balanced_listener`
- peer neighbors: `1`
- verdict: `cohort_transport_negative_or_inconclusive`
- original OOF gain sum: `5.027044`
- transported kept gain sum: `2.681536`
- transported gain delta: `-2.345507`
- positive subjects: `0`
- negative subjects: `3`

## OOF Subject Transport Summary

| subject_id | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- |
| id04 | 6 | 6 | 0.383416 | 0.383416 | 0.000000 |
| id05 | 15 | 9 | 2.377087 | 0.662457 | -1.714630 |
| id06 | 13 | 12 | 0.149282 | -0.148934 | -0.298216 |
| id07 | 1 | 1 | -0.122007 | -0.122007 | 0.000000 |
| id08 | 3 | 3 | 0.096271 | 0.096271 | 0.000000 |
| id09 | 5 | 4 | 1.933707 | 1.601046 | -0.332661 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 0.000000 |

Target summary:

| target | rule | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- | --- |
| Q2 | cohort_peer_transport | 12 | 10 | 1.976824 | 1.442764 | -0.534059 |
| Q3 | cohort_peer_transport | 9 | 8 | 1.168314 | 0.870098 | -0.298216 |
| S2 | cohort_peer_transport | 5 | 5 | 1.361437 | 1.361437 | 0.000000 |
| S3 | cohort_peer_transport | 13 | 8 | 0.945472 | -0.567760 | -1.513232 |
| S4 | cohort_peer_transport | 5 | 5 | -0.425003 | -0.425003 | 0.000000 |

Assignment examples:

| split | subject_id | target | peers | mode | score_col | threshold | peer_improvement_sum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| oof | id04 | Q2 | id09 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id04 | Q3 | id09 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id04 | S4 | id09 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id05 | Q2 | id06 | high_energy_listener | wm_energy_app_social_context | 1.694273 | 0.672556 |
| oof | id05 | S2 | id06 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id05 | S3 | id06 | high_energy_listener | wm_energy_rank_max | 0.880556 | 1.064481 |
| oof | id05 | S4 | id06 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id06 | Q2 | id08 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id06 | Q3 | id08 | low_energy_listener | wm_energy_body_activity_sleep | 0.780072 | 0.207103 |
| oof | id06 | S3 | id08 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id07 | S3 | id10 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id08 | Q3 | id07 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id09 | Q2 | id04 | low_energy_listener | wm_energy_app_social_context | 1.959978 | 0.370088 |
| oof | id09 | Q3 | id04 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |
| oof | id10 | S2 | id07 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 |

## Test Candidate

- candidate: `submission_hsjepa_cohort_listener_responsibility_transport_50e86104_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `99`
- vetoed switched cells: `6`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 9 | 0 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 22 | 2 |
| S4 | 14 | 10 | 4 |

## 해석

성공 조건:

```text
peer subject에서 학습한 listener responsibility가 held-out subject에서도 toxic action을 제거한다.
```

실패 조건:

```text
nearest-peer responsibility가 subject-LOO에서 개선되지 않거나,
대부분 all-action으로 후퇴한다.
```

이 실험의 의미는 단순 veto가 아니다. HS-JEPA core representation을 subject/cohort
좌표계로 해석했을 때, action responsibility가 개인을 넘어 전이 가능한지 검증한다.
