# Subject-Contrastive Action-Support Core

## 한 줄 요약

HS-JEPA world state가 subject/target 평균을 외우는 shortcut이 아니라,
같은 subject-target 안에서 어떤 날의 row-target action이 더 건강한지를 맞힐 수 있는지 검증했다.

```text
same subject + same target action pair
  -> which day has healthier raw-memory action?
  -> held-out subject cells scored against peer references
  -> anchor-free action-support sensor
```

## 왜 HS-JEPA core 실험인가

이 실험의 target은 Q/S label probability가 아니다.
보이는 lifelog context에서 보이지 않는 `action-health ordering representation`을 예측한다.

일반 action-support classifier는 subject나 target prior를 외울 수 있다.
여기서는 pairwise supervision을 같은 subject/target 내부에만 만들기 때문에,
학습 신호가 다음 질문으로 바뀐다.

```text
이 사람의 이 target에서 A날과 B날 중 어느 날의 hidden human-state가
raw-memory action을 더 건강하게 만드는가?
```

그 다음 held-out subject의 row-target cell을 다른 subject의 peer reference와 비교해 score를 만든다.
즉 subject identity를 직접 쓰는 memory가 아니라, hidden episode/action-support geometry를 쓰는 실험이다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_contrastive_world_state_weakly_positive`
- selected feature set: `binary_preference__world_residual_energy_pair`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- selected gain sum: `2.383219`
- gain lift vs target-shuffle null: `7.010120`
- gain z vs target-shuffle null: `1.526122`
- released test cells: `175`

## Feature Family Summary

| feature_set | base_feature_set | pairwise_weight_mode | family | best_policy | best_decoder_action | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score | full_pairwise_training_examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| binary_preference__world_residual_energy_pair | world_residual_energy_pair | binary_preference | world_residual_energy | top10_all_cells | raw_memory_release | 0.512922 | 0.508946 | 315 | 2.383219 | 0.539683 | 7.010120 | 1.526122 | 4.392760 | 25200 |
| tail_weighted_preference__world_residual_energy_pair | world_residual_energy_pair | tail_weighted_preference | world_residual_energy | low08_inverse_decisive | inverse_toxic_memory | 0.506334 | 0.492223 | 195 | -5.219139 | 0.564103 | 3.604499 | 1.626364 | -4.046880 | 25200 |
| tail_weighted_preference__world_residual_energy_action_pair | world_residual_energy_action_pair | tail_weighted_preference | world_residual_energy | top05_all_cells | raw_memory_release | 0.544157 | 0.528994 | 158 | -3.988581 | 0.518987 | -2.570056 | -0.797957 | -4.565185 | 25200 |
| tail_weighted_preference__world_full_action_pair | world_full_action_pair | tail_weighted_preference | world_full | low05_inverse_decisive | inverse_toxic_memory | 0.546594 | 0.538614 | 122 | -4.724454 | 0.639344 | -0.004267 | -0.002462 | -4.565882 | 25200 |
| tail_weighted_preference__world_predicted_action_pair | world_predicted_action_pair | tail_weighted_preference | world_predicted | top05_all_cells | raw_memory_release | 0.542525 | 0.528833 | 158 | -6.585878 | 0.575949 | -4.616704 | -1.739910 | -7.735259 | 25200 |
| binary_preference__world_predicted_action_pair | world_predicted_action_pair | binary_preference | world_predicted | top05_all_cells | raw_memory_release | 0.574231 | 0.557971 | 158 | -6.829319 | 0.594937 | -4.711486 | -1.685891 | -7.993328 | 25200 |
| binary_preference__world_residual_energy_action_pair | world_residual_energy_action_pair | binary_preference | world_residual_energy | low05_inverse_decisive | inverse_toxic_memory | 0.575185 | 0.562123 | 122 | -9.291177 | 0.573770 | -6.742665 | -2.931228 | -11.067899 | 25200 |
| tail_weighted_preference__action_pair_only | action_pair_only | tail_weighted_preference | shortcut_baseline | top18_decisive_only | raw_memory_release | 0.582562 | 0.564000 | 439 | -11.347928 | 0.637813 | -1.569970 | -0.233719 | -11.599664 | 25200 |
| binary_preference__world_full_action_pair | world_full_action_pair | binary_preference | world_full | low05_inverse_decisive | inverse_toxic_memory | 0.573377 | 0.559321 | 122 | -11.850489 | 0.557377 | -7.147550 | -3.094300 | -13.745576 | 25200 |
| binary_preference__action_pair_only | action_pair_only | binary_preference | shortcut_baseline | top10_all_cells | raw_memory_release | 0.549215 | 0.549167 | 315 | -12.167459 | 0.622222 | -6.877444 | -2.086411 | -13.898177 | 25200 |
| binary_preference__target_action_pair_only | target_action_pair_only | binary_preference | shortcut_baseline | top18_decisive_only | raw_memory_release | 0.556537 | 0.553419 | 439 | -14.247101 | 0.628702 | -3.711218 | -0.730911 | -15.076203 | 25200 |
| tail_weighted_preference__target_action_pair_only | target_action_pair_only | tail_weighted_preference | shortcut_baseline | top05_all_cells | raw_memory_release | 0.559908 | 0.546349 | 158 | -14.536543 | 0.569620 | -12.033719 | -5.076771 | -17.808709 | 25200 |

## Pairwise Score Summary

| feature_set | base_feature_set | pairwise_weight_mode | pairwise_training_examples_mean | pairwise_training_examples_min | full_pairwise_training_examples | support_auc | support_ap | score_mean | score_std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tail_weighted_preference__action_pair_only | action_pair_only | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.582562 | 0.564000 | 0.499419 | 0.022669 |
| binary_preference__world_residual_energy_action_pair | world_residual_energy_action_pair | binary_preference | 22680.000000 | 22680 | 25200 | 0.575185 | 0.562123 | 0.506558 | 0.051030 |
| binary_preference__world_predicted_action_pair | world_predicted_action_pair | binary_preference | 22680.000000 | 22680 | 25200 | 0.574231 | 0.557971 | 0.506799 | 0.052537 |
| binary_preference__world_full_action_pair | world_full_action_pair | binary_preference | 22680.000000 | 22680 | 25200 | 0.573377 | 0.559321 | 0.503473 | 0.050669 |
| tail_weighted_preference__target_action_pair_only | target_action_pair_only | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.559908 | 0.546349 | 0.500023 | 0.022168 |
| binary_preference__target_action_pair_only | target_action_pair_only | binary_preference | 22680.000000 | 22680 | 25200 | 0.556537 | 0.553419 | 0.498502 | 0.040951 |
| binary_preference__action_pair_only | action_pair_only | binary_preference | 22680.000000 | 22680 | 25200 | 0.549215 | 0.549167 | 0.496768 | 0.038071 |
| tail_weighted_preference__world_full_action_pair | world_full_action_pair | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.546594 | 0.538614 | 0.496854 | 0.046620 |
| tail_weighted_preference__world_residual_energy_action_pair | world_residual_energy_action_pair | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.544157 | 0.528994 | 0.503608 | 0.045085 |
| tail_weighted_preference__world_predicted_action_pair | world_predicted_action_pair | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.542525 | 0.528833 | 0.493793 | 0.041540 |
| binary_preference__world_residual_energy_pair | world_residual_energy_pair | binary_preference | 22680.000000 | 22680 | 25200 | 0.512922 | 0.508946 | 0.502433 | 0.024757 |
| tail_weighted_preference__world_residual_energy_pair | world_residual_energy_pair | tail_weighted_preference | 22680.000000 | 22680 | 25200 | 0.506334 | 0.492223 | 0.512751 | 0.039228 |

## Target Gain For Selected Policy

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate |
| --- | --- | --- | --- | --- |
| Q1 | 57 | -0.638383 | -0.011200 | 0.491228 |
| Q2 | 29 | 0.528078 | 0.018210 | 0.620690 |
| Q3 | 50 | -0.121675 | -0.002433 | 0.560000 |
| S1 | 34 | -0.518287 | -0.015244 | 0.500000 |
| S2 | 48 | 3.542119 | 0.073794 | 0.583333 |
| S3 | 44 | -1.840343 | -0.041826 | 0.409091 |
| S4 | 53 | 1.431710 | 0.027013 | 0.622642 |

## Full Metric Leaderboard

| feature_set | selection_policy | decoder_action | release_fraction | support_auc | support_ap | selected_cells | selected_gain_sum | selected_positive_gain_rate | gain_lift_vs_null | gain_z_vs_null | robust_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| binary_preference__world_residual_energy_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.512922 | 0.508946 | 315 | 2.383219 | 0.539683 | 7.010120 | 1.526122 | 4.392760 |
| binary_preference__world_residual_energy_pair | top25_all_cells | raw_memory_release | 0.250000 | 0.512922 | 0.508946 | 788 | -1.720584 | 0.507614 | 9.247459 | 1.378629 | 0.828474 |
| binary_preference__world_residual_energy_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.512922 | 0.508946 | 158 | -0.909028 | 0.512658 | 1.628081 | 0.540084 | -0.330637 |
| binary_preference__world_residual_energy_pair | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.512922 | 0.508946 | 122 | -2.655718 | 0.549180 | 2.465078 | 0.873186 | -1.832298 |
| binary_preference__world_residual_energy_pair | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.512922 | 0.508946 | 195 | -4.395466 | 0.533333 | 4.075130 | 1.326577 | -3.137224 |
| tail_weighted_preference__world_residual_energy_pair | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.506334 | 0.492223 | 195 | -5.219139 | 0.564103 | 3.604499 | 1.626364 | -4.046880 |
| binary_preference__world_residual_energy_pair | top18_decisive_only | raw_memory_release | 0.180000 | 0.512922 | 0.508946 | 439 | -5.407805 | 0.501139 | 3.800093 | 0.682201 | -4.277920 |
| tail_weighted_preference__world_residual_energy_action_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.544157 | 0.528994 | 158 | -3.988581 | 0.518987 | -2.570056 | -0.797957 | -4.565185 |
| tail_weighted_preference__world_full_action_pair | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.546594 | 0.538614 | 122 | -4.724454 | 0.639344 | -0.004267 | -0.002462 | -4.565882 |
| tail_weighted_preference__world_full_action_pair | low08_inverse_decisive | inverse_toxic_memory | 0.080000 | 0.546594 | 0.538614 | 195 | -5.426214 | 0.641026 | 2.222071 | 0.854478 | -4.642082 |
| tail_weighted_preference__world_residual_energy_pair | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.506334 | 0.492223 | 244 | -6.035221 | 0.557377 | 4.398429 | 1.858473 | -4.647592 |
| binary_preference__world_residual_energy_pair | top18_all_cells | raw_memory_release | 0.180000 | 0.512922 | 0.508946 | 567 | -5.619145 | 0.499118 | 3.033415 | 0.565844 | -4.690744 |
| tail_weighted_preference__world_full_action_pair | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.546594 | 0.538614 | 244 | -6.183481 | 0.635246 | 3.048130 | 1.041014 | -5.179356 |
| tail_weighted_preference__world_residual_energy_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.506334 | 0.492223 | 158 | -4.907206 | 0.411392 | -1.915392 | -0.434823 | -5.317992 |
| tail_weighted_preference__world_full_action_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.546594 | 0.538614 | 158 | -5.060345 | 0.613924 | -2.553835 | -0.658366 | -5.597992 |
| binary_preference__world_residual_energy_pair | low10_inverse_decisive | inverse_toxic_memory | 0.100000 | 0.512922 | 0.508946 | 244 | -6.747392 | 0.528689 | 3.470767 | 1.108726 | -5.658830 |
| tail_weighted_preference__world_residual_energy_pair | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.506334 | 0.492223 | 122 | -6.566680 | 0.516393 | -0.628241 | -0.272618 | -6.616451 |
| tail_weighted_preference__world_residual_energy_pair | top25_all_cells | raw_memory_release | 0.250000 | 0.506334 | 0.492223 | 788 | -8.522281 | 0.491117 | 4.928259 | 0.778991 | -7.105118 |
| tail_weighted_preference__world_predicted_action_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.542525 | 0.528833 | 158 | -6.585878 | 0.575949 | -4.616704 | -1.739910 | -7.735259 |
| binary_preference__world_predicted_action_pair | top05_all_cells | raw_memory_release | 0.050000 | 0.574231 | 0.557971 | 158 | -6.829319 | 0.594937 | -4.711486 | -1.685891 | -7.993328 |
| tail_weighted_preference__world_residual_energy_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.506334 | 0.492223 | 315 | -7.487170 | 0.422222 | -2.991695 | -0.653660 | -8.181831 |
| tail_weighted_preference__world_residual_energy_pair | low18_inverse_decisive | inverse_toxic_memory | 0.180000 | 0.506334 | 0.492223 | 439 | -10.137243 | 0.548975 | 6.231338 | 1.575096 | -8.316158 |
| tail_weighted_preference__world_residual_energy_action_pair | top18_decisive_only | raw_memory_release | 0.180000 | 0.544157 | 0.528994 | 439 | -9.531928 | 0.574032 | -0.882825 | -0.149148 | -9.621058 |
| tail_weighted_preference__world_residual_energy_pair | top18_all_cells | raw_memory_release | 0.180000 | 0.506334 | 0.492223 | 567 | -10.012897 | 0.467372 | -0.483754 | -0.091849 | -10.024340 |
| binary_preference__world_predicted_action_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.574231 | 0.557971 | 315 | -8.955103 | 0.590476 | -4.834459 | -1.088736 | -10.103197 |
| tail_weighted_preference__world_full_action_pair | top18_decisive_only | raw_memory_release | 0.180000 | 0.546594 | 0.538614 | 439 | -10.399260 | 0.576310 | -1.491133 | -0.383290 | -10.658629 |
| binary_preference__world_residual_energy_action_pair | low05_inverse_decisive | inverse_toxic_memory | 0.050000 | 0.575185 | 0.562123 | 122 | -9.291177 | 0.573770 | -6.742665 | -2.931228 | -11.067899 |
| tail_weighted_preference__world_residual_energy_pair | top18_decisive_only | raw_memory_release | 0.180000 | 0.506334 | 0.492223 | 439 | -10.879197 | 0.451025 | -1.243002 | -0.239405 | -11.096343 |
| binary_preference__world_residual_energy_action_pair | top25_all_cells | raw_memory_release | 0.250000 | 0.575185 | 0.562123 | 788 | -11.132410 | 0.614213 | -0.709974 | -0.160445 | -11.169186 |
| tail_weighted_preference__world_predicted_action_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.542525 | 0.528833 | 315 | -9.908472 | 0.542857 | -5.502463 | -1.544388 | -11.271925 |
| tail_weighted_preference__world_full_action_pair | top18_all_cells | raw_memory_release | 0.180000 | 0.546594 | 0.538614 | 567 | -10.858879 | 0.567901 | -2.061319 | -0.516716 | -11.273571 |
| tail_weighted_preference__world_full_action_pair | top25_all_cells | raw_memory_release | 0.250000 | 0.546594 | 0.538614 | 788 | -11.538915 | 0.552030 | -0.057958 | -0.015341 | -11.416624 |
| tail_weighted_preference__world_full_action_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.546594 | 0.538614 | 315 | -10.533575 | 0.558730 | -4.212180 | -0.976174 | -11.525032 |
| tail_weighted_preference__action_pair_only | top18_decisive_only | raw_memory_release | 0.180000 | 0.582562 | 0.564000 | 439 | -11.347928 | 0.637813 | -1.569970 | -0.233719 | -11.599664 |
| tail_weighted_preference__world_residual_energy_action_pair | top18_all_cells | raw_memory_release | 0.180000 | 0.544157 | 0.528994 | 567 | -11.998971 | 0.553792 | -3.527246 | -0.590494 | -12.789575 |
| tail_weighted_preference__world_residual_energy_action_pair | top10_all_cells | raw_memory_release | 0.100000 | 0.544157 | 0.528994 | 315 | -11.382575 | 0.514286 | -6.314397 | -1.251082 | -12.932689 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_contrastive_action_support_anchor_free_2cc6457c_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.24394568290839252, 'probability_max': 0.8765707382310982}`

이 후보는 train prior에서 시작한다.
subject-contrastive support score가 release-worthy라고 본 row-target action만 sparse하게 release하거나,
low-support decisive action은 inverse-toxic 방향으로 움직인다.

## 해석

성공 조건:

```text
world-state pairwise feature가 action-only / target-action shortcut baseline보다 높은
selected gain과 target-shuffle null lift를 보여야 한다.
```

실패 조건:

```text
action-only baseline만 좋거나, world-state score가 null보다 낫지 않으면
현재 HS-JEPA core는 subject-contrastive episode ordering을 잡지 못한다.
```

현재 결론:

```text
HS-JEPA core의 일반성은 direct label prediction이 아니라
subject-contrastive action-health ordering으로 검증해야 한다.
```
