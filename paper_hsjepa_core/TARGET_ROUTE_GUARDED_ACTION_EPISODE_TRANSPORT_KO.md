# Target-Route Guarded Action-Episode Transport

## 한 줄 요약

전역 action-episode transport를 target별 route guard로 분해했다.
S3처럼 transport가 살아나는 route는 믿고, S4처럼 손실이 나는 route는 별도 veto/guard를 허용한다.

```text
target-specific route guard
  -> keep all / veto all / action-episode transport
  -> row-target action responsibility
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 target-route action decoder로 번역하는 adapter다.
전역 action listener가 서로 다른 target noise/action regime을 섞는 문제를 해결하기 위해,
listener responsibility를 target별로 분해한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Learned Target Guards

| target | policy_key | guarded_score | oof_gain_delta | oof_removed_gain_sum | positive_subjects | negative_subjects | min_subject_improvement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | keep_all | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 |
| Q3 | keep_all | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 |
| S2 | keep_all | 0.000000 | 0.000000 | 0.000000 | 0 | 0 | 0.000000 |
| S3 | target_expert__knn1__uniform__thr-0.10 | 1.246489 | 1.186489 | -1.186489 | 2 | 0 | 0.000000 |
| S4 | veto_all | 0.268258 | 0.425003 | -0.425003 | 1 | 1 | -0.355817 |

## OOF Result

- verdict: `target_route_guard_positive`
- original gain sum: `5.027044`
- kept gain sum: `6.638536`
- OOF gain delta: `1.611492`
- removed action gain sum: `-1.611492`
- positive subjects: `3`
- negative subjects: `1`

Subject summary:

| subject_id | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- |
| id04 | 6 | 5 | 0.383416 | 0.027598 | -0.355817 |
| id05 | 15 | 11 | 2.377087 | 3.157907 | 0.780820 |
| id06 | 13 | 9 | 0.149282 | 1.213763 | 1.064481 |
| id07 | 1 | 0 | -0.122007 | 0.000000 | 0.122007 |
| id08 | 3 | 3 | 0.096271 | 0.096271 | 0.000000 |
| id09 | 5 | 5 | 1.933707 | 1.933707 | 0.000000 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 0.000000 |

Target summary:

| target | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- |
| Q2 | 12 | 12 | 1.976824 | 1.976824 | 0.000000 |
| Q3 | 9 | 9 | 1.168314 | 1.168314 | 0.000000 |
| S2 | 5 | 5 | 1.361437 | 1.361437 | 0.000000 |
| S3 | 13 | 8 | 0.945472 | 2.131961 | 1.186489 |
| S4 | 5 | 0 | -0.425003 | 0.000000 | 0.425003 |

Top target policy alternatives:

| target | policy_key | guarded_score | oof_gain_delta | oof_kept_gain_sum | oof_removed_gain_sum |
| --- | --- | --- | --- | --- | --- |
| Q2 | keep_all | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__uniform__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__uniform__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__uniform__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__uniform__thr0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__distance__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__distance__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn3__distance__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__uniform__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__uniform__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__uniform__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__distance__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__distance__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__distance__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn5__distance__thr0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__uniform__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__uniform__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__uniform__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__distance__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__distance__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn7__distance__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__uniform__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__uniform__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__uniform__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__uniform__thr0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__uniform__thr0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__distance__thr-0.10 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__distance__thr-0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__distance__thr0.00 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |
| Q2 | target_expert__knn11__distance__thr0.05 | 0.000000 | 0.000000 | 1.976824 | 0.000000 |

## Test Candidate

- candidate: `submission_hsjepa_target_route_guarded_action_episode_transport_964c6cc7_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `72`
- vetoed switched cells: `33`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 9 | 0 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 5 | 19 |
| S4 | 14 | 0 | 14 |

## 해석

성공 조건:

```text
전역 action-episode transport의 S3 positive signal을 유지하면서 S4 손실을 제거한다.
```

실패 조건:

```text
target별 guard가 OOF gain을 늘리지 못하거나, 지나치게 veto_all로 collapse한다.
```

이 실험은 HS-JEPA adapter를 더 일반화한다.
core representation 자체보다 중요한 것은 target별 listener responsibility의 위치를 찾는 것이다.
