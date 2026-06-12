# World-Model Residual Action Decoder

## 한 줄 요약

HS-JEPA core의 masked-context world model이 만든 residual energy를 cross-subject row-target action decoder의 listener로 사용했다.

```text
HS-JEPA core world-model residual
  -> target-specific action-health listener
  -> cross-subject prototype action veto
  -> subject-heldout stress
```

## 위치

이 실험은 HS-JEPA core 자체가 아니라, core representation을 사용하는 adapter/diagnostic이다.

- Core input: `hsjepa_core/run_masked_context_world_model.py`
- Adapter input: `cross_subject_episode_prototype_transport.py`
- Diagnostic: target-specific residual-energy listener와 subject-heldout stress

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Source Field

- source release law: `route_episode_context__target_episode_family__knn13_distance`
- source policy: `topfrac` `0.06`
- original OOF cells: `44`
- original active subjects: `7`
- original gain sum: `5.027044`
- original positive gain rate: `0.681818`
- verdict: `oof_positive_subjectheldout_fragile`

## Learned Listener Rules

| target | mode | score_col | selected_cells | selected_gain_sum | all_gain_sum | removed_gain_sum | gain_improvement | selected_positive_gain_rate | all_positive_gain_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | all | wm_energy_calendar_rhythm | 12 | 1.976824 | 1.976824 | 0.000000 | 0.000000 | 0.750000 | 0.750000 |
| Q3 | all | wm_energy_calendar_rhythm | 9 | 1.168314 | 1.168314 | 0.000000 | 0.000000 | 0.666667 | 0.666667 |
| S2 | all | wm_energy_calendar_rhythm | 5 | 1.361437 | 1.361437 | 0.000000 | 0.000000 | 1.000000 | 1.000000 |
| S3 | low_energy_listener | wm_energy_app_social_context | 7 | 1.487267 | 0.945472 | -0.541795 | 0.541795 | 0.857143 | 0.615385 |
| S4 | high_energy_listener | wm_energy_calendar_rhythm | 2 | 0.099617 | -0.425003 | -0.524620 | 0.524620 | 0.500000 | 0.400000 |

## OOF 결과

- kept cells: `35`
- kept active subjects: `6`
- kept gain sum: `6.093459`
- removed cells: `9`
- removed gain sum: `-1.066415`
- kept positive gain rate: `0.771429`

Target summary:

| target | rule | all_cells | kept_cells | all_gain_sum | kept_gain_sum | removed_gain_sum | all_positive_gain_rate | kept_positive_gain_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | all::wm_energy_calendar_rhythm | 12 | 12 | 1.976824 | 1.976824 | 0.000000 | 0.750000 | 0.750000 |
| Q3 | all::wm_energy_calendar_rhythm | 9 | 9 | 1.168314 | 1.168314 | 0.000000 | 0.666667 | 0.666667 |
| S2 | all::wm_energy_calendar_rhythm | 5 | 5 | 1.361437 | 1.361437 | 0.000000 | 1.000000 | 1.000000 |
| S3 | low_energy_listener::wm_energy_app_social_context | 13 | 7 | 0.945472 | 1.487267 | -0.541795 | 0.615385 | 0.857143 |
| S4 | high_energy_listener::wm_energy_calendar_rhythm | 5 | 2 | -0.425003 | 0.099617 | -0.524620 | 0.400000 | 0.500000 |

## Subject-Heldout Stress

| heldout_subject | all_cells | kept_cells | all_gain_sum | kept_gain_sum | removed_gain_sum | all_mean_gain | kept_mean_gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id04 | 6 | 5 | 0.383416 | 0.027598 | 0.355817 | 0.063903 | 0.005520 |
| id05 | 15 | 10 | 2.377087 | 0.863855 | 1.513232 | 0.158472 | 0.086386 |
| id06 | 13 | 12 | 0.149282 | -0.148934 | 0.298216 | 0.011483 | -0.012411 |
| id07 | 1 | 0 | -0.122007 | 0.000000 | -0.122007 | -0.122007 | 0.000000 |
| id08 | 3 | 2 | 0.096271 | -0.092560 | 0.188831 | 0.032090 | -0.046280 |
| id09 | 5 | 2 | 1.933707 | 0.697920 | 1.235787 | 0.386741 | 0.348960 |
| id10 | 1 | 1 | 0.209289 | 0.209289 | 0.000000 | 0.209289 | 0.209289 |

Stress summary:

- subject-heldout original gain sum: `5.027044`
- subject-heldout kept gain sum: `1.557169`
- subject-heldout delta: `-3.469875`

## Test Candidate

- candidate: `submission_hsjepa_world_model_residual_action_decoder_b3361d85_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `88`
- vetoed switched cells: `17`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 test kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 12 | 12 | 0 |
| Q2 | 32 | 32 | 0 |
| Q3 | 9 | 9 | 0 |
| S1 | 1 | 1 | 0 |
| S2 | 13 | 13 | 0 |
| S3 | 24 | 19 | 5 |
| S4 | 14 | 2 | 12 |

## 해석

성공 조건:

```text
core world-model residual energy가 cross-subject action field에서 negative-gain action을 제거한다.
```

실패 조건:

```text
world-model residual은 representation evidence로는 의미가 있지만,
row-target action decoder에서는 subject-heldout stress를 통과하지 못한다.
```

이 실험은 LB 최적화가 아니라 HS-JEPA core representation이 adapter 독성을 줄일 수 있는지 확인하는 stress test다.

현재 판정은 full OOF positive / subject-heldout fragile이다. 즉 core residual energy가 toxic pocket을 찾는 신호는 있지만,
그 신호를 그대로 public/private-safe release rule로 주장하기에는 아직 이르다.
