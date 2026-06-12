# Action-Support View Invariance Core

## 한 줄 요약

HS-JEPA action-support 신호가 target/action shortcut인지,
특정 lifelog view 하나의 우연한 artifact인지,
아니면 masked human-state world representation에서 나온 안정적인 신호인지 stress했다.

```text
raw-memory action support target
  -> target-blind / single-view / leave-one-view-out support predictors
  -> release / inverse-toxic action pocket stability
```

## 왜 core stress인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> positive/toxic action-support target
```

차이는 feature set이다. target/action-only baseline, target-blind world state,
single-view world state, leave-one-view-out world state를 같은 subject-heldout stress에 넣었다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Core Stress Verdict

- verdict: `world_state_signal_positive_target_blind_weakly_survives`
- selected feature set: `world_residual_energy`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- selected gain sum: `6.146252`
- gain lift vs target-shuffle null: `9.817777`
- gain z vs target-shuffle null: `2.942742`
- released test cells: `136`

## Feature Family Summary

| feature_set | family | view | best_policy | best_decoder_action | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| world_residual_energy | world_all | all | top10_all_cells | raw_memory_release | 0.542555 | 0.536845 | 315 | 6.146252 | 0.565079 | 9.817777 | 2.942742 | 8.977386 |
| leaveout_view_app_social_context | leaveout_view | app_social_context | low08_inverse_decisive | inverse_toxic_memory | 0.549393 | 0.544331 | 195 | 4.682284 | 0.671795 | 10.497242 | 2.966008 | 7.711824 |
| world_full_all_views | world_all | all | low05_inverse_decisive | inverse_toxic_memory | 0.538615 | 0.529594 | 122 | 3.432323 | 0.655738 | 8.218793 | 3.641637 | 5.942286 |
| leaveout_view_body_activity_sleep | leaveout_view | body_activity_sleep | top10_all_cells | raw_memory_release | 0.550575 | 0.547388 | 315 | 3.133639 | 0.603175 | 6.728895 | 1.551154 | 5.090749 |
| single_view_calendar_rhythm | single_view | calendar_rhythm | top10_all_cells | raw_memory_release | 0.508336 | 0.507787 | 315 | 2.406992 | 0.552381 | 4.308380 | 0.851654 | 3.690315 |
| single_view_mobility_environment | single_view | mobility_environment | low10_inverse_decisive | inverse_toxic_memory | 0.529349 | 0.520828 | 244 | 1.028717 | 0.622951 | 8.045046 | 2.071302 | 3.361421 |
| single_view_phone_behavior | single_view | phone_behavior | low10_inverse_decisive | inverse_toxic_memory | 0.535939 | 0.521369 | 244 | 0.594024 | 0.606557 | 8.296037 | 2.450465 | 3.015710 |
| leaveout_view_phone_behavior | leaveout_view | phone_behavior | top05_all_cells | raw_memory_release | 0.540658 | 0.534972 | 158 | 1.781481 | 0.594937 | 3.943051 | 1.211111 | 3.012867 |
| world_predicted_only | world_all | all | low10_inverse_decisive | inverse_toxic_memory | 0.533763 | 0.516146 | 244 | -0.071859 | 0.635246 | 7.277156 | 1.909483 | 2.059000 |
| target_blind_world_full | target_blind | all | low05_inverse_decisive | inverse_toxic_memory | 0.531633 | 0.525287 | 122 | -0.320604 | 0.581967 | 4.432486 | 2.086112 | 1.099898 |
| target_family_world_full | target_family | all | low08_inverse_decisive | inverse_toxic_memory | 0.537457 | 0.529169 | 195 | -1.021714 | 0.620513 | 6.869645 | 1.877977 | 1.001064 |
| leaveout_view_calendar_rhythm | leaveout_view | calendar_rhythm | low05_inverse_decisive | inverse_toxic_memory | 0.517195 | 0.510567 | 122 | -0.183082 | 0.557377 | 3.062651 | 1.172062 | 0.815690 |
| leaveout_view_mobility_environment | leaveout_view | mobility_environment | low05_inverse_decisive | inverse_toxic_memory | 0.525168 | 0.520069 | 122 | -2.758438 | 0.590164 | 1.077064 | 0.382723 | -2.311013 |
| single_view_app_social_context | single_view | app_social_context | top10_all_cells | raw_memory_release | 0.508679 | 0.499875 | 315 | -3.948793 | 0.495238 | -2.333186 | -0.639897 | -4.459472 |
| target_action_only | baseline | none | top05_all_cells | raw_memory_release | 0.509262 | 0.498032 | 158 | -4.107447 | 0.500000 | -1.835469 | -0.762804 | -4.502339 |
| world_energy_only | world_all | all | top05_all_cells | raw_memory_release | 0.512849 | 0.508120 | 158 | -6.158391 | 0.518987 | -3.473400 | -1.251127 | -6.997085 |
| single_view_body_activity_sleep | single_view | body_activity_sleep | top05_all_cells | raw_memory_release | 0.467459 | 0.474525 | 158 | -7.027003 | 0.449367 | -4.096423 | -1.414218 | -8.051905 |

## Single View Listeners

| feature_set | view | best_policy | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| single_view_calendar_rhythm | calendar_rhythm | top10_all_cells | 2.406992 | 0.552381 | 4.308380 | 0.851654 | 3.690315 |
| single_view_mobility_environment | mobility_environment | low10_inverse_decisive | 1.028717 | 0.622951 | 8.045046 | 2.071302 | 3.361421 |
| single_view_phone_behavior | phone_behavior | low10_inverse_decisive | 0.594024 | 0.606557 | 8.296037 | 2.450465 | 3.015710 |
| single_view_app_social_context | app_social_context | top10_all_cells | -3.948793 | 0.495238 | -2.333186 | -0.639897 | -4.459472 |
| single_view_body_activity_sleep | body_activity_sleep | top05_all_cells | -7.027003 | 0.449367 | -4.096423 | -1.414218 | -8.051905 |

## Leave-One-View-Out Stress

| feature_set | view | best_policy | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| leaveout_view_app_social_context | app_social_context | low08_inverse_decisive | 4.682284 | 0.671795 | 10.497242 | 2.966008 | 7.711824 |
| leaveout_view_body_activity_sleep | body_activity_sleep | top10_all_cells | 3.133639 | 0.603175 | 6.728895 | 1.551154 | 5.090749 |
| leaveout_view_phone_behavior | phone_behavior | top05_all_cells | 1.781481 | 0.594937 | 3.943051 | 1.211111 | 3.012867 |
| leaveout_view_calendar_rhythm | calendar_rhythm | low05_inverse_decisive | -0.183082 | 0.557377 | 3.062651 | 1.172062 | 0.815690 |
| leaveout_view_mobility_environment | mobility_environment | low05_inverse_decisive | -2.758438 | 0.590164 | 1.077064 | 0.382723 | -2.311013 |

## Full Metric Leaderboard

| feature_set | selection_policy | decoder_action | release_fraction | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| world_residual_energy | top10_all_cells | raw_memory_release | 0.100000 | 0.542555 | 0.536845 | 315 | 6.146252 | 0.565079 | 9.817777 | 2.942742 | 8.977386 |
| leaveout_view_app_social_context | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.549393 | 0.544331 | 195 | 4.682284 | 0.671795 | 10.497242 | 2.966008 | 7.711824 |
| leaveout_view_app_social_context | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.549393 | 0.544331 | 122 | 4.195517 | 0.721311 | 7.159321 | 2.440132 | 6.360886 |
| world_residual_energy | top18_decisive_only | raw_memory_release | 0.180000 | 0.542555 | 0.536845 | 439 | 3.255667 | 0.569476 | 10.188599 | 2.140403 | 6.116418 |
| world_full_all_views | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.538615 | 0.529594 | 122 | 3.432323 | 0.655738 | 8.218793 | 3.641637 | 5.942286 |
| leaveout_view_app_social_context | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.549393 | 0.544331 | 244 | 2.462271 | 0.663934 | 10.374637 | 2.588530 | 5.428996 |
| leaveout_view_body_activity_sleep | top10_all_cells | raw_memory_release | 0.100000 | 0.550575 | 0.547388 | 315 | 3.133639 | 0.603175 | 6.728895 | 1.551154 | 5.090749 |
| world_full_all_views | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.538615 | 0.529594 | 195 | 1.689773 | 0.641026 | 8.734909 | 2.421826 | 4.227503 |
| leaveout_view_app_social_context | top05_all_cells | raw_memory_release | 0.050000 | 0.549393 | 0.544331 | 158 | 2.776195 | 0.639241 | 4.454089 | 1.264557 | 4.150692 |
| leaveout_view_body_activity_sleep | top18_decisive_only | raw_memory_release | 0.180000 | 0.550575 | 0.547388 | 439 | 1.645080 | 0.594533 | 8.543027 | 1.835775 | 4.076332 |
| leaveout_view_body_activity_sleep | top18_all_cells | raw_memory_release | 0.180000 | 0.550575 | 0.547388 | 567 | 1.571942 | 0.583774 | 8.038007 | 1.747121 | 3.867157 |
| single_view_calendar_rhythm | top10_all_cells | raw_memory_release | 0.100000 | 0.508336 | 0.507787 | 315 | 2.406992 | 0.552381 | 4.308380 | 0.851654 | 3.690315 |
| single_view_mobility_environment | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.529349 | 0.520828 | 244 | 1.028717 | 0.622951 | 8.045046 | 2.071302 | 3.361421 |
| single_view_mobility_environment | top05_all_cells | raw_memory_release | 0.050000 | 0.529349 | 0.520828 | 158 | 2.181670 | 0.594937 | 3.616096 | 1.302940 | 3.338663 |
| world_residual_energy | top18_all_cells | raw_memory_release | 0.180000 | 0.542555 | 0.536845 | 567 | 1.075856 | 0.539683 | 7.751058 | 1.531444 | 3.271057 |
| leaveout_view_body_activity_sleep | top05_all_cells | raw_memory_release | 0.050000 | 0.550575 | 0.547388 | 158 | 2.057445 | 0.626582 | 3.634752 | 1.147307 | 3.214564 |
| single_view_phone_behavior | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.535939 | 0.521369 | 244 | 0.594024 | 0.606557 | 8.296037 | 2.450465 | 3.015710 |
| leaveout_view_phone_behavior | top05_all_cells | raw_memory_release | 0.050000 | 0.540658 | 0.534972 | 158 | 1.781481 | 0.594937 | 3.943051 | 1.211111 | 3.012867 |
| single_view_mobility_environment | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.529349 | 0.520828 | 122 | 1.130249 | 0.696721 | 5.228303 | 1.892357 | 2.762894 |
| world_residual_energy | top05_all_cells | raw_memory_release | 0.050000 | 0.542555 | 0.536845 | 158 | 1.296842 | 0.575949 | 2.711470 | 0.993262 | 2.198158 |
| world_predicted_only | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.533763 | 0.516146 | 244 | -0.071859 | 0.635246 | 7.277156 | 1.909483 | 2.059000 |
| single_view_phone_behavior | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.535939 | 0.521369 | 195 | 0.044125 | 0.610256 | 6.482459 | 1.959429 | 1.974058 |
| world_predicted_only | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.533763 | 0.516146 | 195 | -0.273550 | 0.656410 | 5.173296 | 1.629091 | 1.314203 |
| single_view_mobility_environment | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.529349 | 0.520828 | 195 | -0.479465 | 0.646154 | 5.977457 | 1.635796 | 1.307301 |
| leaveout_view_app_social_context | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.549393 | 0.544331 | 439 | -2.555988 | 0.624146 | 13.407709 | 2.687126 | 1.166946 |
| target_blind_world_full | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.531633 | 0.525287 | 122 | -0.320604 | 0.581967 | 4.432486 | 2.086112 | 1.099898 |
| single_view_phone_behavior | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.535939 | 0.521369 | 122 | 0.012465 | 0.688525 | 3.241096 | 1.112745 | 1.083890 |
| target_family_world_full | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.537457 | 0.529169 | 195 | -1.021714 | 0.620513 | 6.869645 | 1.877977 | 1.001064 |
| target_family_world_full | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.537457 | 0.529169 | 122 | -0.504977 | 0.606557 | 4.623064 | 2.082229 | 0.969007 |
| leaveout_view_calendar_rhythm | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.517195 | 0.510567 | 122 | -0.183082 | 0.557377 | 3.062651 | 1.172062 | 0.815690 |
| leaveout_view_phone_behavior | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.540658 | 0.534972 | 122 | -0.416111 | 0.540984 | 3.565831 | 1.564332 | 0.735739 |
| world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.542555 | 0.536845 | 122 | -0.509286 | 0.581967 | 3.459742 | 1.366485 | 0.610460 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_action_support_view_invariance_anchor_free_84071a4b_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.273236080057702, 'probability_max': 0.9142433058486573}`

이 후보는 leaderboard anchor를 쓰지 않는다.
train prior에서 시작하고, selected view-invariance support model이 release-worthy라고 본
raw-memory action을 decoder에 따라 그대로 release하거나, inverse-toxic decoder이면
prior 기준 반대 방향으로 움직인다.

## 해석

성공 조건:

```text
world-state feature set이 target/action-only baseline보다 더 높은 selected gain과
null lift를 보이고, target-blind 또는 leave-one-view stress에서도 완전히 무너지지 않아야 한다.
```

실패 조건:

```text
target/action-only baseline이 world-state와 같거나 더 좋으면,
현재 신호는 HS-JEPA representation이 아니라 action magnitude/target prior shortcut이다.
```

현재 결론:

```text
HS-JEPA core는 direct classifier가 아니라 action-support world model이어야 하며,
이 stress는 그 신호가 어느 lifelog view와 target route에 의존하는지 분해한다.
```
