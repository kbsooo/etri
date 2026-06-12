# Subject-Invariant World-Model Listener Solver

## 한 줄 요약

HS-JEPA masked-context world model residual을 action-health listener로 쓰되,
full OOF gain이 아니라 subject-invariant objective로 listener rule을 고른 실험이다.

```text
HS-JEPA core residual energy
  -> target-specific listener candidates
  -> subject-balanced rule selector
  -> cross-subject prototype action veto
  -> subject-LOO stress
```

## HS-JEPA 안에서의 위치

이 문서는 HS-JEPA core 자체가 아니다.
정확한 위치는 core representation을 action decoder로 안전하게 번역할 수 있는지 검증하는
adapter + LeJEPA-style diagnostic이다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## 왜 필요한가

직전 `World-Model Residual Action Decoder`는 full OOF에서 toxic action을 잘 제거했다.
하지만 subject-heldout stress에서는 gain이 크게 줄어 `oof_positive_subjectheldout_fragile` 판정을 받았다.

이번 실험은 그 실패를 정면으로 찌른다.

```text
좋은 listener는 한 subject의 lucky tail이 아니라,
subject가 바뀌어도 같은 방향의 action-health를 보여야 한다.
```

## Objective Leaderboard

| objective | oof_gain_delta | oof_kept_gain_sum | rule_non_all_targets | subject_loo_improvement_sum | subject_loo_positive_subjects | subject_loo_negative_subjects |
| --- | --- | --- | --- | --- | --- | --- |
| subject_balanced_listener | 1.415175 | 6.442219 | 3 | -3.281044 | 1 | 4 |
| minimax_listener | 1.415175 | 6.442219 | 3 | -3.281044 | 1 | 4 |
| full_oof_improvement | 1.464804 | 6.491848 | 3 | -4.318627 | 1 | 5 |

## Release Objective

- selected objective: `subject_balanced_listener`
- verdict: `oof_positive_subject_invariant_negative`
- original OOF cells: `44`
- kept OOF cells: `32`
- OOF gain delta: `1.415175`
- subject-LOO improvement sum: `-3.281044`

## Learned Rules

| target | mode | score_col | threshold | objective_score | all_cells | selected_cells | improvement_sum | negative_improvement_subjects | min_subject_improvement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 | 12 | 12 | 0.000000 | 0 | 0.000000 |
| Q3 | low_energy_listener | wm_energy_phone_behavior | 1.932447 | 0.127560 | 9 | 7 | 0.092560 | 0 | 0.000000 |
| S2 | all | wm_energy_calendar_rhythm | 0.000000 | 0.000000 | 5 | 5 | 0.000000 | 0 | 0.000000 |
| S3 | low_energy_listener | wm_energy_app_social_context | 1.408010 | 0.229228 | 13 | 7 | 0.541795 | 1 | -0.291129 |
| S4 | high_energy_listener | wm_energy_calendar_rhythm | 1.545668 | 0.795820 | 5 | 1 | 0.780820 | 0 | 0.000000 |

Target summary:

| target | rule | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum |
| --- | --- | --- | --- | --- | --- | --- |
| Q2 | all::wm_energy_calendar_rhythm | 12 | 12 | 1.976824 | 1.976824 | 0.000000 |
| Q3 | low_energy_listener::wm_energy_phone_behavior | 9 | 7 | 1.168314 | 1.260874 | 0.092560 |
| S2 | all::wm_energy_calendar_rhythm | 5 | 5 | 1.361437 | 1.361437 | 0.000000 |
| S3 | low_energy_listener::wm_energy_app_social_context | 13 | 7 | 0.945472 | 1.487267 | 0.541795 |
| S4 | high_energy_listener::wm_energy_calendar_rhythm | 5 | 1 | -0.425003 | 0.355817 | 0.780820 |

## Subject-LOO Stress

| heldout_subject | all_cells | kept_cells | all_gain_sum | kept_gain_sum | improvement_sum | learned_non_all_targets |
| --- | --- | --- | --- | --- | --- | --- |
| id04 | 6 | 5 | 0.383416 | 0.027598 | -0.355817 | 3 |
| id05 | 15 | 10 | 2.377087 | 0.863855 | -1.513232 | 2 |
| id06 | 13 | 12 | 0.149282 | -0.148934 | -0.298216 | 2 |
| id07 | 1 | 0 | -0.122007 | 0.000000 | 0.122007 | 3 |
| id08 | 3 | 3 | 0.096271 | 0.096271 | 0.000000 | 2 |
| id09 | 5 | 2 | 1.933707 | 0.697920 | -1.235787 | 3 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 0.000000 | 3 |

## Test Candidate

- candidate: `submission_hsjepa_subject_invariant_world_model_listener_solver_1807cfd1_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `85`
- vetoed switched cells: `20`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 6 | 3 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 19 | 5 |
| S4 | 14 | 2 | 12 |

## 해석

성공 조건:

```text
subject-balanced selector가 full OOF toxicity separation을 유지하면서
subject-LOO에서도 positive improvement를 만든다.
```

실패 조건:

```text
selector가 all-action으로 후퇴하거나,
subject-LOO improvement가 음수가 되어 core residual listener가 subject-tail shortcut임을 보인다.
```

현재 결과는 위 verdict를 따른다. 이 문서는 좋은 점수용 tuning이 아니라,
HS-JEPA core residual을 action decoder로 번역할 때 필요한 subject-invariance 조건을
검증하는 논문용 stress experiment다.
