# Listener-Conditioned Action-Support Core

## 한 줄 요약

target-blind world state가 약했던 이유를 검증하기 위해,
HS-JEPA world-state residual/energy를 listener-conditioned action-support predictor로 바꿨다.

```text
visible human context
  -> masked world-state residual/energy
  -> target/family listener-conditioned support prediction
  -> anchor-free row-target correction sensor
```

## 왜 core 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

이전 stress에서 target-blind world state는 target/action baseline보다 낫지만 positive gain까지는 못 갔다.
이번 실험은 그 병목이 `listener가 없는 decoder` 때문인지 확인한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `listener_conditioning_positive_but_target_transfer_unproven`
- selected feature set: `target_interaction_world_residual_energy`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- selected gain sum: `6.192500`
- gain lift vs target-shuffle null: `10.137463`
- gain z vs target-shuffle null: `2.610537`
- released test cells: `175`

## Listener Summary

| feature_set | listener_family | best_policy | best_decoder_action | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_interaction_world_residual_energy | explicit_interaction | top10_all_cells | raw_memory_release | 0.611128 | 0.600888 | 315 | 6.192500 | 0.704762 | 10.137463 | 2.610537 | 9.111899 |
| target_blind_world_residual_energy | target_blind | low08_inverse_decisive | inverse_toxic_memory | 0.606443 | 0.586268 | 195 | 0.791207 | 0.682051 | 8.996472 | 2.741381 | 3.430149 |
| family_interaction_world_residual_energy | explicit_interaction | low05_inverse_decisive | inverse_toxic_memory | 0.604847 | 0.601336 | 122 | 1.489033 | 0.762295 | 5.521086 | 1.748462 | 3.199755 |
| target_action_only | global_or_baseline | top10_all_cells | raw_memory_release | 0.607203 | 0.596569 | 315 | 1.543383 | 0.676190 | 4.953675 | 1.072693 | 3.036664 |
| per_family_world_residual_energy | per_family | top05_all_cells | raw_memory_release | 0.588139 | 0.563603 | 158 | 0.417354 | 0.607595 | 2.893882 | 1.040656 | 1.375976 |
| target_heldout_world_residual_energy | target_heldout_transfer | top25_all_cells | raw_memory_release | 0.629874 | 0.600935 | 788 | -2.496232 | 0.638325 | 12.167035 | 3.028215 | 0.947365 |
| global_world_residual_energy | global_or_baseline | top10_all_cells | raw_memory_release | 0.603496 | 0.596592 | 315 | -1.955206 | 0.663492 | 4.288271 | 1.119257 | -0.627725 |
| per_target_world_residual_energy | per_target | top05_all_cells | raw_memory_release | 0.571713 | 0.569217 | 158 | -3.053041 | 0.613924 | -2.474337 | -0.731105 | -3.576633 |

## Target Gain For Selected Listener

| target | selected_cells | selected_gain_sum | selected_mean_gain | selected_positive_gain_rate |
| --- | --- | --- | --- | --- |
| Q1 | 8 | -0.052821 | -0.006603 | 0.500000 |
| Q2 | 81 | 3.176745 | 0.039219 | 0.617284 |
| Q3 | 19 | -0.215819 | -0.011359 | 0.631579 |
| S1 | 66 | -2.403852 | -0.036422 | 0.712121 |
| S2 | 87 | 2.027212 | 0.023301 | 0.770115 |
| S3 | 27 | 1.406791 | 0.052103 | 0.740741 |
| S4 | 27 | 2.254243 | 0.083490 | 0.814815 |

## Full Metric Leaderboard

| feature_set | selection_policy | decoder_action | release_fraction | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_interaction_world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.611128 | 0.600888 | 315 | 6.192500 | 0.704762 | 10.137463 | 2.610537 | 9.111899 |
| target_interaction_world_residual_energy | top18_decisive_only | raw_memory_release | 0.180000 | 0.611128 | 0.600888 | 439 | 3.200894 | 0.676538 | 11.330043 | 2.323413 | 6.388412 |
| target_interaction_world_residual_energy | top18_all_cells | raw_memory_release | 0.180000 | 0.611128 | 0.600888 | 567 | 1.504338 | 0.675485 | 9.368204 | 1.874923 | 4.165254 |
| target_blind_world_residual_energy | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.606443 | 0.586268 | 195 | 0.791207 | 0.682051 | 8.996472 | 2.741381 | 3.430149 |
| family_interaction_world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.604847 | 0.601336 | 122 | 1.489033 | 0.762295 | 5.521086 | 1.748462 | 3.199755 |
| target_action_only | top10_all_cells | raw_memory_release | 0.100000 | 0.607203 | 0.596569 | 315 | 1.543383 | 0.676190 | 4.953675 | 1.072693 | 3.036664 |
| target_blind_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.606443 | 0.586268 | 158 | 1.518860 | 0.626582 | 4.718077 | 1.708978 | 2.991744 |
| target_blind_world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.606443 | 0.586268 | 122 | 0.737540 | 0.696721 | 5.496695 | 2.237730 | 2.464913 |
| per_family_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.588139 | 0.563603 | 158 | 0.417354 | 0.607595 | 2.893882 | 1.040656 | 1.375976 |
| target_heldout_world_residual_energy | top25_all_cells | raw_memory_release | 0.250000 | 0.629874 | 0.600935 | 788 | -2.496232 | 0.638325 | 12.167035 | 3.028215 | 0.947365 |
| target_interaction_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.611128 | 0.600888 | 158 | -0.183221 | 0.664557 | 0.847339 | 0.276624 | 0.216883 |
| target_heldout_world_residual_energy | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.629874 | 0.600935 | 244 | -2.457328 | 0.692623 | 9.016983 | 2.268053 | 0.151517 |
| global_world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.603496 | 0.596592 | 315 | -1.955206 | 0.663492 | 4.288271 | 1.119257 | -0.627725 |
| target_interaction_world_residual_energy | top25_all_cells | raw_memory_release | 0.250000 | 0.611128 | 0.600888 | 788 | -3.295310 | 0.654822 | 8.247197 | 1.528976 | -0.947488 |
| target_heldout_world_residual_energy | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.629874 | 0.600935 | 195 | -3.270340 | 0.682051 | 6.133678 | 1.772608 | -1.424599 |
| target_heldout_world_residual_energy | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.629874 | 0.600935 | 439 | -5.392000 | 0.681093 | 13.635991 | 3.155319 | -1.560304 |
| target_blind_world_residual_energy | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.606443 | 0.586268 | 244 | -3.889793 | 0.659836 | 6.171590 | 1.934360 | -2.027188 |
| target_heldout_world_residual_energy | low25_inverse_decisive | inverse_toxic_memory | 0.250000 | 0.629874 | 0.600935 | 610 | -7.213109 | 0.668852 | 18.571693 | 3.678325 | -2.108706 |
| family_interaction_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.604847 | 0.601336 | 158 | -2.427123 | 0.702532 | -0.214886 | -0.079465 | -2.311569 |
| global_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.603496 | 0.596592 | 158 | -2.581769 | 0.651899 | -0.815085 | -0.306113 | -2.647055 |
| family_interaction_world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.604847 | 0.601336 | 315 | -3.310280 | 0.682540 | 0.253088 | 0.072080 | -3.070607 |
| target_heldout_world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.629874 | 0.600935 | 122 | -3.990820 | 0.663934 | 2.014077 | 0.712771 | -3.264296 |
| target_heldout_world_residual_energy | top18_all_cells | raw_memory_release | 0.180000 | 0.629874 | 0.600935 | 567 | -5.216174 | 0.634921 | 5.625691 | 1.361707 | -3.542084 |
| per_target_world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.571713 | 0.569217 | 158 | -3.053041 | 0.613924 | -2.474337 | -0.731105 | -3.576633 |
| global_world_residual_energy | top18_decisive_only | raw_memory_release | 0.180000 | 0.603496 | 0.596592 | 439 | -5.517454 | 0.662870 | 6.126061 | 1.583674 | -3.693527 |
| family_interaction_world_residual_energy | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.604847 | 0.601336 | 244 | -5.412197 | 0.680328 | 4.600905 | 1.197569 | -3.996083 |
| target_interaction_world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.611128 | 0.600888 | 122 | -4.191931 | 0.696721 | -0.786412 | -0.241199 | -4.233650 |
| per_target_world_residual_energy | top18_all_cells | raw_memory_release | 0.180000 | 0.571713 | 0.569217 | 567 | -4.927469 | 0.619048 | 1.393134 | 0.264946 | -4.403228 |
| per_target_world_residual_energy | top18_decisive_only | raw_memory_release | 0.180000 | 0.571713 | 0.569217 | 439 | -5.073248 | 0.605923 | 1.763426 | 0.346896 | -4.453159 |
| family_interaction_world_residual_energy | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.604847 | 0.601336 | 195 | -5.613664 | 0.676923 | 2.390549 | 0.640060 | -4.795591 |
| per_family_world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.588139 | 0.563603 | 122 | -4.858925 | 0.606557 | -0.462574 | -0.167299 | -4.836314 |
| target_heldout_world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.629874 | 0.600935 | 315 | -5.246789 | 0.647619 | 0.885069 | 0.294395 | -4.840065 |
| global_world_residual_energy | top25_all_cells | raw_memory_release | 0.250000 | 0.603496 | 0.596592 | 788 | -7.667784 | 0.638325 | 7.339514 | 1.218917 | -5.575811 |
| per_target_world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.571713 | 0.569217 | 315 | -5.103823 | 0.628571 | -2.357906 | -0.512649 | -5.577169 |
| global_world_residual_energy | top18_all_cells | raw_memory_release | 0.180000 | 0.603496 | 0.596592 | 567 | -7.143611 | 0.652557 | 4.652384 | 1.179443 | -5.723020 |
| target_heldout_world_residual_energy | top18_decisive_only | raw_memory_release | 0.180000 | 0.629874 | 0.600935 | 439 | -7.562048 | 0.628702 | 3.795514 | 0.949760 | -6.380013 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_listener_conditioned_action_support_anchor_free_efdf0586_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.30721483708484554, 'probability_max': 0.9493333333333336}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, selected listener-conditioned support model이 release-worthy라고 판단한
raw-memory row-target action을 decoder에 따라 release하거나 inverse-toxic 방향으로 움직인다.

## 해석

성공 조건:

```text
listener-conditioned world-state predictor가 target/action-only baseline과
global world-state baseline을 모두 이기고, target-heldout transfer가 baseline보다 나쁘지 않아야 한다.
```

실패 조건:

```text
per-target listener만 좋아지고 target-heldout transfer가 무너지면,
이 신호는 general HS-JEPA listener가 아니라 target-specific memorization일 수 있다.
```

현재 결론:

```text
HS-JEPA core는 target-free decoder가 아니라 listener-conditioned action-support world model로 정립해야 한다.
```
