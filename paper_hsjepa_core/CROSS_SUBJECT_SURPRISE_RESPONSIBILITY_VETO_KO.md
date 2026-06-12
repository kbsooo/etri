# Cross-Subject Surprise Responsibility Veto

## 한 줄 요약

Cross-subject episode prototype transport가 만든 더 넓은 row-target action field에 masked-view surprise responsibility veto를 적용했다.

## HS-JEPA 안에서의 위치

이 실험은 HS-JEPA core 자체가 아니다.

```text
Core signal  = masked context-to-hidden-view prediction residual
Adapter      = cross-subject episode-action prototype transport
Diagnostic   = target-specific surprise responsibility veto
```

따라서 논문에서의 정확한 위치는 다음과 같다.

```text
HS-JEPA core가 만든 surprise representation이
cross-subject adapter의 toxic row-target action을 줄일 수 있는지 검증하는
adapter + LeJEPA-style diagnostic 실험
```

## 왜 필요한가

이전 `Surprise Responsibility Toxicity Veto`는 OOF gain을 개선했지만, source release가 `id02`, `id09` 두 subject에 몰려 있었다. 따라서 masked surprise가 진짜 general action-health signal인지, 좁은 subject tail에만 맞은 rule인지 구분하기 어려웠다.

이번 실험은 source action field를 cross-subject prototype transport로 바꾼다.

```text
peer subject episode-action prototype
  -> held-out subject row-target action
  -> masked-view surprise responsibility
  -> toxicity veto
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Source Cross-Subject Field

- release law: `route_episode_context__target_episode_family__knn13_distance`
- source policy: `topfrac` `0.06`
- original OOF cells: `44`
- original active subjects: `7`
- original gain sum: `5.027044`
- original positive gain rate: `0.681818`

## Target Listener Rules

| target | selected_mode | median_score | selected_cells | selected_gain_sum | all_gain_sum | selected_mean_gain | all_mean_gain | selected_positive_gain_rate | all_positive_gain_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | all | 0.695000 | 12 | 1.976824 | 1.976824 | 0.164735 | 0.164735 | 0.750000 | 0.750000 |
| Q3 | all | 0.397000 | 9 | 1.168314 | 1.168314 | 0.129813 | 0.129813 | 0.666667 | 0.666667 |
| S2 | all | 0.316333 | 5 | 1.361437 | 1.361437 | 0.272287 | 0.272287 | 1.000000 | 1.000000 |
| S3 | all | 0.604889 | 13 | 0.945472 | 0.945472 | 0.072729 | 0.072729 | 0.615385 | 0.615385 |
| S4 | low_surprise_listener | 0.736778 | 2 | 0.099617 | -0.425003 | 0.049809 | -0.085001 | 0.500000 | 0.400000 |

Rule detail:

| target | mode | cells | gain_sum | mean_gain | positive_gain_rate |
| --- | --- | --- | --- | --- | --- |
| Q2 | all | 12 | 1.976824 | 0.164735 | 0.750000 |
| Q2 | high_surprise_listener | 6 | 1.302397 | 0.217066 | 0.833333 |
| Q2 | low_surprise_listener | 6 | 0.674427 | 0.112405 | 0.666667 |
| Q3 | all | 9 | 1.168314 | 0.129813 | 0.666667 |
| Q3 | high_surprise_listener | 5 | 0.835428 | 0.167086 | 0.800000 |
| Q3 | low_surprise_listener | 4 | 0.332886 | 0.083221 | 0.500000 |
| S2 | all | 5 | 1.361437 | 0.272287 | 1.000000 |
| S2 | high_surprise_listener | 3 | 0.866807 | 0.288936 | 1.000000 |
| S2 | low_surprise_listener | 2 | 0.494630 | 0.247315 | 1.000000 |
| S3 | all | 13 | 0.945472 | 0.072729 | 0.615385 |
| S3 | high_surprise_listener | 7 | 0.485548 | 0.069364 | 0.714286 |
| S3 | low_surprise_listener | 6 | 0.459924 | 0.076654 | 0.500000 |
| S4 | all | 5 | -0.425003 | -0.085001 | 0.400000 |
| S4 | high_surprise_listener | 3 | -0.524620 | -0.174873 | 0.333333 |
| S4 | low_surprise_listener | 2 | 0.099617 | 0.049809 | 0.500000 |

## OOF Veto 결과

- kept cells: `41`
- kept active subjects: `7`
- kept gain sum: `5.551664`
- removed cells: `3`
- removed gain sum: `-0.524620`
- kept positive gain rate: `0.707317`

Subject summary:

| subject_id | cells | kept_cells | all_gain_sum | kept_gain_sum | positive_gain_rate |
| --- | --- | --- | --- | --- | --- |
| id04 | 6 | 6 | 0.383416 | 0.383416 | 0.500000 |
| id05 | 15 | 12 | 2.377087 | 2.901707 | 0.800000 |
| id06 | 13 | 13 | 0.149282 | 0.149282 | 0.538462 |
| id07 | 1 | 1 | -0.122007 | -0.122007 | 0.000000 |
| id08 | 3 | 3 | 0.096271 | 0.096271 | 0.666667 |
| id09 | 5 | 5 | 1.933707 | 1.933707 | 1.000000 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 1.000000 |

## Subject-Heldout Stress

| heldout_subject | all_cells | kept_cells | all_gain_sum | kept_gain_sum | removed_gain_sum | all_mean_gain | kept_mean_gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id04 | 6 | 5 | 0.383416 | 0.027598 | 0.355817 | 0.063903 | 0.005520 |
| id05 | 15 | 10 | 2.377087 | 0.863855 | 1.513232 | 0.158472 | 0.086386 |
| id06 | 13 | 13 | 0.149282 | 0.149282 | 0.000000 | 0.011483 | 0.011483 |
| id07 | 1 | 1 | -0.122007 | -0.122007 | 0.000000 | -0.122007 | -0.122007 |
| id08 | 3 | 3 | 0.096271 | 0.096271 | 0.000000 | 0.032090 | 0.032090 |
| id09 | 5 | 2 | 1.933707 | 0.697920 | 1.235787 | 0.386741 | 0.348960 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 0.000000 | 0.209289 | 0.209289 |

## Test Candidate

- candidate: `submission_hsjepa_cross_subject_surprise_responsibility_veto_aceca94c_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `101`
- vetoed switched cells: `4`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 9 | 0 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 24 | 0 |
| S4 | 14 | 10 | 4 |

## 해석

이 실험은 HS-JEPA의 action-health story를 더 강하게 검증한다.

성공 조건:

```text
cross-subject action field에서도 masked-view residual energy가 negative-gain actions를 더 많이 제거한다.
```

실패 조건:

```text
surprise responsibility는 narrow episode release에는 맞지만 cross-subject transport field에는 일반화되지 않는다.
```

결과 해석은 OOF gain sum뿐 아니라 active subject coverage와 subject-heldout stress를 같이 봐야 한다.

