# Action-Support World Model Core

## 한 줄 요약

HS-JEPA core가 단순히 label을 직접 맞히는지 보지 않고,
raw lifelog memory action이 어떤 row-target에서 성공/실패할지를
subject-heldout으로 예측할 수 있는지 검증했다.

```text
visible lifelog context
  -> masked human-state world model
  -> hidden action-support representation prediction
  -> anchor-free sparse correction
```

## 왜 core 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target도 public 결과가 아니라 train label에서 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

그 다음 HS-JEPA world-state가 이 hidden action-support target을 예측하는지 본다.
즉 target은 Q/S label 자체가 아니라, label이 드러내는 **action-health representation**이다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Action Field Summary

| action_name | oof_logloss | prior_logloss | delta_vs_prior | positive_gain_rate | decisive_cells | decisive_positive_rate |
| --- | --- | --- | --- | --- | --- | --- |
| raw_lifelog_memory | 0.693113 | 0.677858 | 0.015255 | 0.498095 | 2440 | 0.495902 |
| masked_world_memory | 0.709167 | 0.677858 | 0.031309 | 0.474921 | 2290 | 0.479913 |

## Subject-Heldout Action-Support Prediction

아래 표는 feature set별로 hidden action-support를 예측한 결과다.
`selected_gain_sum`은 해당 feature set이 건강하다고 고른 raw-memory actions를 실제 OOF gain으로 평가한 값이다.

| feature_set | selection_policy | decoder_action | release_fraction | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hsjepa_masked_world_full | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.539592 | 0.530735 | 122 | 2.621567 | 0.647541 | 6.164069 | 2.636913 |
| hsjepa_core_plus_world | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.539592 | 0.530735 | 122 | 2.621567 | 0.647541 | 6.297425 | 2.082788 |
| hsjepa_masked_world_full | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.539592 | 0.530735 | 195 | 1.873462 | 0.646154 | 8.207351 | 2.735651 |
| hsjepa_core_plus_world | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.539592 | 0.530735 | 195 | 1.873462 | 0.646154 | 8.032810 | 2.297989 |
| hsjepa_masked_world_predicted | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.533830 | 0.516535 | 244 | -0.071859 | 0.635246 | 7.277156 | 1.909483 |
| hsjepa_masked_world_predicted | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.533830 | 0.516535 | 195 | -0.273550 | 0.656410 | 5.173296 | 1.629091 |
| hsjepa_core_plus_world | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.539592 | 0.530735 | 244 | -2.136234 | 0.602459 | 6.627120 | 1.913004 |
| hsjepa_masked_world_full | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.539592 | 0.530735 | 244 | -2.136234 | 0.602459 | 6.366150 | 2.084728 |
| hsjepa_masked_world_predicted | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.533830 | 0.516535 | 122 | -1.481456 | 0.663934 | 1.405050 | 0.502256 |
| raw_lifelog_context | top10_all_cells | raw_memory_release | 0.100000 | 0.503777 | 0.501523 | 315 | -2.646749 | 0.523810 | 2.090192 | 0.660863 |
| hsjepa_masked_world_predicted | top18_decisive_only | raw_memory_release | 0.180000 | 0.533830 | 0.516535 | 439 | -4.349802 | 0.535308 | 2.633145 | 0.634390 |
| target_prior_action_only | top05_all_cells | raw_memory_release | 0.050000 | 0.507764 | 0.497730 | 158 | -3.939623 | 0.506329 | -1.594034 | -0.641555 |
| hsjepa_masked_world_predicted | top18_all_cells | raw_memory_release | 0.180000 | 0.533830 | 0.516535 | 567 | -4.924598 | 0.514991 | 1.474072 | 0.331882 |
| hsjepa_core_cohort_state | top05_all_cells | raw_memory_release | 0.050000 | 0.507764 | 0.497730 | 158 | -3.939623 | 0.506329 | -2.421893 | -0.817289 |
| hsjepa_masked_world_predicted | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.533830 | 0.516535 | 439 | -7.484852 | 0.601367 | 6.963195 | 1.907934 |
| hsjepa_masked_world_predicted | top05_all_cells | raw_memory_release | 0.050000 | 0.533830 | 0.516535 | 158 | -4.814156 | 0.500000 | -3.094387 | -1.105541 |
| hsjepa_core_plus_world | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.539592 | 0.530735 | 439 | -7.968986 | 0.596811 | 7.530913 | 1.687752 |
| hsjepa_masked_world_full | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.539592 | 0.530735 | 439 | -7.968986 | 0.596811 | 7.345997 | 1.763404 |
| raw_lifelog_context | top05_all_cells | raw_memory_release | 0.050000 | 0.503777 | 0.501523 | 158 | -5.210492 | 0.481013 | -2.687852 | -1.194145 |
| hsjepa_masked_world_predicted | top10_all_cells | raw_memory_release | 0.100000 | 0.533830 | 0.516535 | 315 | -6.117157 | 0.498413 | -2.236877 | -0.547713 |
| hsjepa_masked_world_full | top18_all_cells | raw_memory_release | 0.180000 | 0.539592 | 0.530735 | 567 | -7.302949 | 0.541446 | -0.486726 | -0.098779 |
| hsjepa_core_plus_world | top18_all_cells | raw_memory_release | 0.180000 | 0.539592 | 0.530735 | 567 | -7.302949 | 0.541446 | -1.272409 | -0.239117 |
| hsjepa_masked_world_predicted | top25_all_cells | raw_memory_release | 0.250000 | 0.533830 | 0.516535 | 788 | -8.210812 | 0.520305 | 1.312149 | 0.270198 |
| hsjepa_masked_world_full | top05_all_cells | raw_memory_release | 0.050000 | 0.539592 | 0.530735 | 158 | -6.718363 | 0.563291 | -4.712473 | -1.499545 |
| hsjepa_core_plus_world | top05_all_cells | raw_memory_release | 0.050000 | 0.539592 | 0.530735 | 158 | -6.718363 | 0.563291 | -5.071567 | -1.706637 |
| hsjepa_core_plus_world | top10_all_cells | raw_memory_release | 0.100000 | 0.539592 | 0.530735 | 315 | -7.783920 | 0.546032 | -4.440433 | -0.980551 |
| hsjepa_masked_world_full | top10_all_cells | raw_memory_release | 0.100000 | 0.539592 | 0.530735 | 315 | -7.783920 | 0.546032 | -4.614274 | -1.275586 |
| hsjepa_masked_world_full | low25_inverse_decisive | inverse_toxic_memory | 0.250000 | 0.539592 | 0.530735 | 610 | -11.921080 | 0.583607 | 9.058778 | 2.350536 |

## Release Policy

- selected feature set: `hsjepa_masked_world_full`
- selected policy: `low05_inverse_decisive`
- decoder action: `inverse_toxic_memory`
- release fraction: `0.0500`
- selected gain sum: `2.621567`
- gain lift vs target-shuffle null: `6.164069`
- gain z vs target-shuffle null: `2.636913`
- selected positive gain rate: `0.647541`

## Anchor-Free Candidate

- candidate: `submission_hsjepa_action_support_world_model_anchor_free_9da5d2f1_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.4356681565533115, 'probability_max': 0.9223997575477667}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, HS-JEPA core가 예측한 action-support에 따라
raw-memory action을 release하거나 toxic action의 반대 방향으로 움직인다.
선택된 decoder가 `inverse_toxic_memory`이면, core가 toxic하다고 본 raw-memory action은 prior 기준 반대 방향으로 움직인다.
점수용 best candidate라기보다 core-only action-support sensor다.

## 해석

성공 조건:

```text
HS-JEPA world-state feature set이 target-prior/action-only baseline보다
더 높은 support AUC/AP와 selected OOF gain을 보여야 한다.
```

실패 조건:

```text
target-prior/action-only baseline이 world-state와 비슷하거나 더 좋다면,
현재 core는 action-health를 읽는 것이 아니라 action magnitude/target prior만 읽는 것이다.
```

현재 가장 중요한 결론:

```text
HS-JEPA core의 가치는 direct label prediction이 아니라,
row-target action을 release하기 전에 action-health/toxicity를 예측하는 데서 검증되어야 한다.
```
