# Action-Episode Listener Transport

## 한 줄 요약

Subject 평균 fingerprint가 아니라, 비슷한 row-target action episode에서 listener responsibility를 전이했다.

```text
target + action route + HS-JEPA world-model residual geometry
  -> peer action gain
  -> keep/veto current row-target action
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니라, core representation을 action responsibility로 번역하는 adapter다.
직전 cohort 실험이 subject 평균 fingerprint에서 실패했기 때문에, responsibility의 단위를
subject에서 action episode로 낮췄다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Policy Leaderboard

| policy_key | oof_gain_delta | oof_kept_gain_sum | oof_removed_gain_sum | active_subjects | positive_subjects | negative_subjects | min_subject_improvement |
| --- | --- | --- | --- | --- | --- | --- | --- |
| target_expert__knn3__uniform__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn3__distance__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn5__uniform__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn5__distance__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn7__uniform__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn7__uniform__thr-0.05 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn7__distance__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn7__distance__thr-0.05 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn11__uniform__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn11__uniform__thr-0.05 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn11__distance__thr-0.10 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_expert__knn11__distance__thr-0.05 | 0.830672 | 5.857716 | -0.830672 | 6 | 2 | 1 | -0.355817 |
| target_family__knn3__uniform__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn3__distance__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn5__uniform__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn5__distance__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn7__uniform__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn7__uniform__thr-0.05 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn7__distance__thr-0.10 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |
| target_family__knn7__distance__thr-0.05 | 0.650861 | 5.677905 | -0.650861 | 6 | 2 | 1 | -0.355817 |

## Release Policy

- policy: `target_expert__knn3__uniform__thr-0.10`
- verdict: `action_episode_transport_positive`
- original OOF gain sum: `5.027044`
- kept OOF gain sum: `5.857716`
- OOF gain delta: `0.830672`
- positive subjects: `2`
- negative subjects: `1`

## OOF Action-Episode Audit

| cell_key | subject_id | target | action_family | true_gain | predicted_gain | neighbor_positive_rate | keep |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 171:Q3 | id04 | Q3 | prior | -0.213762 | 0.152268 | 0.666667 | True |
| 172:Q3 | id04 | Q3 | prior | -0.248198 | 0.368282 | 1.000000 | True |
| 174:Q2 | id04 | Q2 | prior | 0.411982 | 0.080449 | 0.666667 | True |
| 175:Q2 | id04 | Q2 | prior | -0.370088 | 0.352438 | 1.000000 | True |
| 175:S4 | id04 | S4 | core_action_health | 0.355817 | -0.321824 | 0.000000 | False |
| 176:Q2 | id04 | Q2 | prior | 0.447665 | 0.299773 | 1.000000 | True |
| 214:S2 | id05 | S2 | core_action_health | 0.263222 | 0.209289 | 1.000000 | True |
| 214:S3 | id05 | S3 | core_action_health | 0.329593 | 0.147790 | 1.000000 | True |
| 214:S4 | id05 | S4 | core_action_health | -0.256200 | 0.355817 | 1.000000 | True |
| 215:S3 | id05 | S3 | raw_action_core_health | 0.174275 | 0.000000 | 0.000000 | True |
| 215:S4 | id05 | S4 | core_action_health | 0.184653 | 0.000000 | 0.000000 | True |
| 216:S3 | id05 | S3 | core_action_health | 0.329593 | 0.147790 | 1.000000 | True |
| 217:S2 | id05 | S2 | prior | 0.285340 | 0.000000 | 0.000000 | True |
| 219:S3 | id05 | S3 | core_action_health | 0.291129 | 0.000000 | 0.000000 | True |
| 219:S4 | id05 | S4 | core_action_health | -0.310406 | 0.355817 | 1.000000 | True |
| 220:S2 | id05 | S2 | core_action_health | 0.199658 | 0.209289 | 1.000000 | True |
| 220:S3 | id05 | S3 | core_action_health | 0.310176 | 0.000000 | 0.000000 | True |
| 220:S4 | id05 | S4 | core_action_health | -0.398867 | 0.355817 | 1.000000 | True |
| 222:Q2 | id05 | Q2 | prior | 0.201399 | 0.306957 | 1.000000 | True |
| 222:S2 | id05 | S2 | core_action_health | 0.403928 | 0.209289 | 1.000000 | True |
| 222:S3 | id05 | S3 | core_action_health | 0.369595 | 0.000000 | 0.000000 | True |
| 260:S3 | id06 | S3 | prior | -0.221657 | -0.122007 | 0.000000 | False |
| 261:Q2 | id06 | Q2 | prior | -0.378053 | 0.109277 | 0.666667 | True |
| 262:Q2 | id06 | Q2 | prior | 0.312901 | 0.124852 | 0.666667 | True |

Subject summary:

| subject_id | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- |
| id04 | 6 | 5 | 0.383416 | 0.027598 | -0.355817 |
| id05 | 15 | 15 | 2.377087 | 2.377087 | 0.000000 |
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
| S4 | 5 | 4 | -0.425003 | -0.780820 | -0.355817 |

## Test Candidate

- candidate: `submission_hsjepa_action_episode_listener_transport_6e58a450_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `76`
- vetoed switched cells: `29`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 8 | 1 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 5 | 19 |
| S4 | 14 | 5 | 9 |

## 해석

성공 조건:

```text
row-target action episode geometry가 peer action gain을 예측해 toxic actions를 제거한다.
```

실패 조건:

```text
route/action/residual geometry를 넣어도 peer action gain이 전이되지 않는다.
```

이 실험은 HS-JEPA의 adapter claim을 더 정확히 찌른다.
core residual 자체보다 중요한 것은, 그 residual이 어떤 action route에서 어떤 책임을 가져야 하는지다.
