# Tail-Safe Expected Utility Core

## 한 줄 요약

HS-JEPA core score를 `건강한 action 확률`로 쓰지 않고,
Log Loss 관점의 expected gain과 negative-tail risk를 직접 예측해
tail-safe utility decoder로 바꿨다.

## 빠른 판정: 이것은 HS-JEPA인가?

부분적으로 맞다. 정확히는 **HS-JEPA core와 competition adapter 사이의 decoder-boundary 실험**이다.

```text
HS-JEPA core question
  = visible human context -> hidden human-state/action-health representation prediction

이 문서의 question
  = predicted hidden action-health geometry -> Log Loss expected utility / tail-risk action
```

따라서 이 문서를 HS-JEPA 본체로 소개하면 JEPA 느낌이 흐려진다.
논문에서는 masked-context world model과 subject-contrastive action-support core를 먼저 설명하고,
이 실험은 `core representation을 Log Loss action으로 안전하게 번역하려면 tail-safe utility decoder가 필요하다`
는 증거로 배치해야 한다.

```text
masked world-state residual/energy
  -> listener + subject-contrastive support context
  -> expected gain / tail loss / toxic-tail probability
  -> tail-safe row-target-action assignment
```

## 왜 필요한가

이전 subject-contrastive 실험에서 중요한 모순이 나왔다.

```text
shortcut/action-only score는 AUC가 높아도 selected Log Loss gain이 음수였다.
world residual-energy score만 약한 positive utility를 냈다.
```

즉 HS-JEPA core를 증명하려면 AUC가 아니라 utility를 봐야 한다.
이 실험은 action-health를 sign classification이 아니라 expected utility problem으로 재정의한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `tail_safe_expected_utility_oof_positive_subjectheldout_fragile`
- full OOF selected gain: `10.396344`
- nested heldout gain: `-8.823949`
- stable targets: `['Q1']`
- stable OOF gain: `2.143778`
- candidate policy source: `stable_subjectheldout`
- released test cells: `7`

## Utility Model Metrics

| metric | value |
| --- | --- |
| gain_mae | 0.174261 |
| tail_loss_mae | 0.100312 |
| health_auc | 0.594411 |
| health_ap | 0.566594 |
| toxic_tail_auc | 0.692999 |
| toxic_tail_ap | 0.539363 |
| realized_gain_sum_all_modes | -141.439797 |
| positive_action_rate | 0.500000 |
| toxic_tail_rate | 0.403333 |

## Subject-Contrastive Score Summary

| feature_set | base_feature_set | pairwise_weight_mode | support_auc | support_ap | score_mean | score_std |
| --- | --- | --- | --- | --- | --- | --- |
| binary_preference__world_residual_energy_pair | world_residual_energy_pair | binary_preference | 0.512810 | 0.509087 | 0.502477 | 0.024778 |
| tail_weighted_preference__world_residual_energy_pair | world_residual_energy_pair | tail_weighted_preference | 0.506334 | 0.492223 | 0.512751 | 0.039228 |

## Full OOF Chosen Policies

| target | accepted | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | raw_action_count | inverse_action_count | gain_lift_vs_null | tail_safe_policy_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | predicted_gain | top_decisive | 0.040000 | 13 | 2.143778 | 0.769231 | 4 | 1 | 13 | 0 | 2.369992 | 3.610473 | positive_expected_utility_tail_safe |
| Q2 | True | predicted_gain | top_all | 0.020000 | 9 | 2.290855 | 0.888889 | 4 | 1 | 9 | 0 | 2.606469 | 3.901018 | positive_expected_utility_tail_safe |
| Q3 | True | pessimistic_utility | top_decisive | 0.040000 | 14 | 0.285450 | 0.642857 | 6 | 2 | 1 | 13 | 0.521103 | 0.452327 | positive_expected_utility_tail_safe |
| S1 | True | health_score_only | top_all | 0.040000 | 18 | 0.029510 | 0.666667 | 4 | 1 | 16 | 2 | 0.635899 | 0.588208 | positive_expected_utility_tail_safe |
| S2 | True | predicted_gain | top_all | 0.020000 | 9 | 2.211289 | 0.777778 | 2 | 0 | 7 | 2 | 2.711149 | 4.146015 | positive_expected_utility_tail_safe |
| S3 | True | predicted_gain | top_decisive | 0.020000 | 7 | 1.692567 | 0.714286 | 2 | 1 | 7 | 0 | 1.978112 | 2.584487 | positive_expected_utility_tail_safe |
| S4 | True | predicted_gain | top_all | 0.080000 | 36 | 1.742896 | 0.611111 | 5 | 4 | 32 | 4 | 2.302395 | 0.958014 | positive_expected_utility_tail_safe |

## Nested Subject-Heldout Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets |
| --- | --- | --- | --- | --- | --- |
| id01 | 20 | -1.491226 | -0.074561 | 0.450000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id02 | 21 | -2.356500 | -0.112214 | 0.333333 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id03 | 18 | -0.296108 | -0.016450 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id04 | 23 | -1.648663 | -0.071681 | 0.391304 | Q1,Q2,Q3,S1,S2,S4 |
| id05 | 20 | 0.041617 | 0.002081 | 0.400000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id06 | 26 | -0.773845 | -0.029763 | 0.346154 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id07 | 23 | -1.389343 | -0.060406 | 0.347826 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id08 | 12 | -0.505723 | -0.042144 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id09 | 12 | -0.228463 | -0.019039 | 0.333333 | Q1,Q2,Q3,S1,S2,S3,S4 |
| id10 | 12 | -0.175697 | -0.014641 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Nested Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | raw_action_count | inverse_action_count | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 17 | 0.349221 | 0.020542 | 0.588235 | 14.000000 | 3.000000 | 5 | 5 |
| Q2 | 26 | 0.166440 | 0.006402 | 0.461538 | 15.000000 | 11.000000 | 7 | 3 |
| Q3 | 19 | 0.033825 | 0.001780 | 0.473684 | 6.000000 | 13.000000 | 3 | 7 |
| S1 | 47 | -5.355366 | -0.113944 | 0.234043 | 13.000000 | 34.000000 | 2 | 8 |
| S2 | 11 | -0.840117 | -0.076374 | 0.363636 | 8.000000 | 3.000000 | 3 | 7 |
| S3 | 9 | -2.009685 | -0.223298 | 0.333333 | 6.000000 | 3.000000 | 3 | 6 |
| S4 | 58 | -1.168266 | -0.020143 | 0.448276 | 39.000000 | 19.000000 | 3 | 7 |

## Stable Policies Used For Candidate

| target | accepted | score_col | policy | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | True | predicted_gain | top_decisive | 0.040000 | 1.000000 | 0.349221 | 5 | 5 | 0.588235 | tail_safe_subjectheldout_stable |
| Q2 | False | predicted_gain | hold | 0.000000 | 1.000000 | 0.166440 | 7 | 3 | 0.461538 | failed_tail_safe_subjectheldout |
| Q3 | False | pessimistic_utility | hold | 0.000000 | 1.000000 | 0.033825 | 3 | 7 | 0.473684 | failed_tail_safe_subjectheldout |
| S1 | False | health_score_only | hold | 0.000000 | 1.000000 | -5.355366 | 2 | 8 | 0.234043 | failed_tail_safe_subjectheldout |
| S2 | False | predicted_gain | hold | 0.000000 | 1.000000 | -0.840117 | 3 | 7 | 0.363636 | failed_tail_safe_subjectheldout |
| S3 | False | predicted_gain | hold | 0.000000 | 0.900000 | -2.009685 | 3 | 6 | 0.333333 | failed_tail_safe_subjectheldout |
| S4 | False | predicted_gain | hold | 0.000000 | 1.000000 | -1.168266 | 3 | 7 | 0.448276 | failed_tail_safe_subjectheldout |

## Policy Board Top Rows

| target | score_col | policy | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | positive_subjects | negative_subjects | gain_lift_vs_null | gain_z_vs_null | tail_safe_policy_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | predicted_gain | top_all | 0.020000 | 9 | 2.211289 | 0.777778 | 2 | 0 | 2.711149 | 3.136025 | 4.146015 |
| Q2 | predicted_gain | top_all | 0.020000 | 9 | 2.290855 | 0.888889 | 4 | 1 | 2.606469 | 3.367878 | 3.901018 |
| S2 | predicted_gain | top_decisive | 0.020000 | 7 | 2.090314 | 0.857143 | 2 | 0 | 2.242602 | 2.950508 | 3.870275 |
| Q1 | predicted_gain | top_decisive | 0.040000 | 13 | 2.143778 | 0.769231 | 4 | 1 | 2.369992 | 3.179677 | 3.610473 |
| S2 | predicted_gain | top_all | 0.080000 | 36 | 2.099155 | 0.500000 | 4 | 1 | 2.983204 | 1.696827 | 3.537959 |
| S2 | predicted_gain | top_decisive | 0.080000 | 29 | 2.044294 | 0.517241 | 3 | 1 | 3.133395 | 2.112736 | 3.383291 |
| S2 | predicted_gain | top_all | 0.060000 | 27 | 1.743373 | 0.518519 | 3 | 1 | 2.619356 | 2.472792 | 2.938909 |
| Q1 | predicted_gain | top_decisive | 0.020000 | 7 | 1.726616 | 0.857143 | 3 | 1 | 1.833522 | 2.668827 | 2.785232 |
| S2 | predicted_gain | top_decisive | 0.040000 | 15 | 1.694551 | 0.600000 | 2 | 1 | 2.557262 | 2.269423 | 2.676535 |
| Q2 | predicted_gain | top_all | 0.100000 | 45 | 2.241130 | 0.644444 | 6 | 3 | 3.092377 | 1.637304 | 2.662747 |
| Q2 | predicted_gain | top_decisive | 0.020000 | 7 | 1.577753 | 0.857143 | 3 | 1 | 1.732224 | 2.510564 | 2.585088 |
| S3 | predicted_gain | top_decisive | 0.020000 | 7 | 1.692567 | 0.714286 | 2 | 1 | 1.978112 | 2.995805 | 2.584487 |
| S1 | tail_safe_utility | top_decisive | 0.140000 | 49 | 1.628344 | 0.489796 | 7 | 3 | 3.876426 | 1.734943 | 2.480016 |
| S2 | predicted_gain | top_all | 0.040000 | 18 | 1.335675 | 0.555556 | 3 | 1 | 2.312913 | 1.983032 | 2.387942 |
| Q1 | predicted_gain | top_all | 0.040000 | 18 | 1.882558 | 0.666667 | 4 | 2 | 2.040453 | 2.424501 | 2.372499 |
| Q1 | predicted_gain | top_all | 0.250000 | 112 | 1.827723 | 0.589286 | 6 | 3 | 3.314506 | 1.835644 | 2.327614 |
| Q1 | predicted_gain | top_decisive | 0.060000 | 20 | 1.694151 | 0.650000 | 5 | 2 | 1.984147 | 2.070083 | 2.323110 |
| S2 | predicted_gain | top_decisive | 0.060000 | 22 | 1.543417 | 0.500000 | 2 | 1 | 2.063965 | 1.896920 | 2.280497 |
| Q2 | predicted_gain | top_decisive | 0.040000 | 15 | 1.803029 | 0.733333 | 5 | 3 | 2.339497 | 2.450339 | 1.873554 |
| Q1 | predicted_gain | top_all | 0.020000 | 9 | 1.022886 | 0.666667 | 3 | 1 | 1.279838 | 2.374079 | 1.791571 |
| Q2 | predicted_gain | top_decisive | 0.060000 | 22 | 1.823229 | 0.681818 | 5 | 3 | 2.223602 | 1.981440 | 1.788270 |
| Q2 | predicted_gain | top_decisive | 0.080000 | 30 | 1.621136 | 0.666667 | 5 | 3 | 2.776852 | 1.855268 | 1.761895 |
| S1 | tail_safe_utility | top_decisive | 0.100000 | 35 | 1.496372 | 0.485714 | 6 | 3 | 2.625993 | 1.572216 | 1.692691 |
| Q1 | predicted_gain | top_decisive | 0.250000 | 84 | 1.208343 | 0.547619 | 6 | 3 | 3.057724 | 1.452009 | 1.565414 |
| S2 | tail_safe_utility | top_decisive | 0.140000 | 51 | 1.406029 | 0.450980 | 5 | 3 | 2.960862 | 1.323187 | 1.482492 |
| Q2 | health_weighted_utility | top_decisive | 0.040000 | 15 | 1.149084 | 0.533333 | 4 | 2 | 1.701436 | 1.954339 | 1.426687 |
| S4 | predicted_gain | top_all | 0.140000 | 63 | 1.320842 | 0.555556 | 6 | 3 | 2.246870 | 1.420955 | 1.393786 |
| S1 | health_weighted_utility | top_all | 0.140000 | 63 | 0.290083 | 0.539683 | 7 | 2 | 2.503538 | 1.371298 | 1.392340 |
| Q2 | predicted_gain | top_decisive | 0.100000 | 37 | 2.065138 | 0.675676 | 5 | 4 | 2.556362 | 1.624253 | 1.358776 |
| Q1 | predicted_gain | top_all | 0.060000 | 27 | 1.528553 | 0.592593 | 5 | 3 | 1.769932 | 2.319982 | 1.337434 |
| Q1 | predicted_gain | top_all | 0.140000 | 63 | 1.315689 | 0.587302 | 5 | 3 | 2.590542 | 1.589529 | 1.336888 |
| Q2 | predicted_gain | top_all | 0.250000 | 112 | 1.356818 | 0.508929 | 5 | 4 | 4.514405 | 1.979393 | 1.312924 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_tail_safe_expected_utility_core_anchor_free_06ca3b66_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.25578930072387673, 'probability_max': 0.7311545979562902}`

## 해석

좋은 결과:

```text
tail-safe expected utility가 health probability보다 좋은 full/nested gain을 만들면,
HS-JEPA core의 병목은 representation 부재가 아니라 objective/decoder mismatch였다는 뜻이다.
```

나쁜 결과:

```text
expected utility와 tail risk를 직접 예측해도 nested heldout에서 무너지면,
현재 core representation은 action toxicity sign을 약하게 읽지만
tail magnitude까지 subject-general하게 읽지는 못한다.
```
