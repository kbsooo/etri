# Failure Boundary Law Distillation

## 한 줄 요약

raw KNN failure detector의 sharp boundary를 shallow tree / sparse linear law로 증류했다.

## 목적

직전 contrastive atlas는 prototype geometry만으로 release-grade action을 고르지 못했다. 이번 실험은 boundary가 완전히 black-box인지, 아니면 몇 개의 HS-JEPA context law로 설명 가능한지 검증한다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- best law: `route_disagreement_law__tree_depth2_leaf28`
- best law family: `shallow_tree`
- best feature view: `route_disagreement_law`
- best law OOF logloss: `0.632902`
- delta vs raw KNN: `-0.004095`
- delta vs GBDT failure detector: `0.000425`
- OOF switched cells: `59`
- target matched-null p(gain >= observed): `0.023000`
- target+family matched-null p(gain >= observed): `0.024750`
- generated candidate: `submission_hsjepa_failure_boundary_law_distillation_65ce2d48_uploadsafe.csv`
- submission priority: `high_information_sensor_prior_reset_law`
- law reading: `If an alternative route stays close enough to core geometry and the route-average probability is not extremely low, treat it as a lower-toxicity prior-reset candidate rather than a positive-gain action.`

## Best law target counts

| target | count |
| --- | --- |
| Q1 | 9 |
| Q2 | 9 |
| Q3 | 9 |
| S1 | 8 |
| S2 | 8 |
| S3 | 8 |
| S4 | 8 |

## Best law expert-family counts

| expert_family | count |
| --- | --- |
| prior | 59 |

## Top features

| feature | importance |
| --- | --- |
| expert_prob_mean | 0.535939 |
| abs_vs_core | 0.464061 |
| expert_pred | 0.000000 |
| expert_logit | 0.000000 |
| target_idx | 0.000000 |
| target_is_q | 0.000000 |
| target_is_s | 0.000000 |
| target_is_q2 | 0.000000 |
| target_is_s2 | 0.000000 |
| expert_is_global_prior | 0.000000 |
| expert_is_subject_prior | 0.000000 |
| expert_is_core_geometry | 0.000000 |
| expert_is_core_action_health | 0.000000 |
| expert_is_raw_action_core_gate | 0.000000 |
| expert_is_strict | 0.000000 |
| expert_is_balanced | 0.000000 |
| expert_is_wide | 0.000000 |
| expert_is_high_margin | 0.000000 |

## Distilled tree law

```text
|--- abs_vs_core <= 0.27
|   |--- expert_prob_mean <= 0.17
|   |   |--- value: [-0.65]
|   |--- expert_prob_mean >  0.17
|   |   |--- value: [-0.01]
|--- abs_vs_core >  0.27
|   |--- value: [-0.55]
```

## Top policies

| law_name | policy | param | logloss | switched_cells | mean_realized_gain_all_cells | positive_true_gain_rate | target_null_p_ge_observed | target_family_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.080000 | 0.632902 | 59 | 0.004095 | 0.593220 | 0.023000 | 0.024750 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.080000 | 0.632902 | 59 | 0.004095 | 0.593220 | 0.028000 | 0.025250 |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.060000 | 0.632964 | 44 | 0.004033 | 0.636364 | 0.019000 | 0.023500 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.060000 | 0.632964 | 44 | 0.004033 | 0.636364 | 0.019250 | 0.017500 |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.040000 | 0.633604 | 29 | 0.003393 | 0.655172 | 0.021500 | 0.021250 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.040000 | 0.633604 | 29 | 0.003393 | 0.655172 | 0.023250 | 0.022750 |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.100000 | 0.634589 | 74 | 0.002408 | 0.554054 | 0.089750 | 0.082750 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.100000 | 0.634589 | 74 | 0.002408 | 0.554054 | 0.081750 | 0.075500 |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.030000 | 0.634722 | 22 | 0.002275 | 0.681818 | 0.058000 | 0.055250 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.030000 | 0.634722 | 22 | 0.002275 | 0.681818 | 0.055750 | 0.055000 |
| human_state_law__tree_depth5_leaf14 | threshold | 0.080000 | 0.634849 | 41 | 0.002148 | 0.853659 | 0.019000 | 0.018250 |
| human_state_law__tree_depth5_leaf14 | topfrac | 0.060000 | 0.635873 | 44 | 0.001124 | 0.818182 | 0.047500 | 0.045750 |
| route_disagreement_law__tree_depth2_leaf28 | topfrac | 0.020000 | 0.635900 | 15 | 0.001097 | 0.600000 | 0.156500 | 0.146750 |
| compact_hsjepa_law__tree_depth2_leaf28 | topfrac | 0.020000 | 0.635900 | 15 | 0.001097 | 0.600000 | 0.150250 | 0.147000 |

## 논문용 해석

가장 중요한 발견은 depth-2 tree가 GBDT detector와 거의 같은 OOF gain을 냈다는 점이다. 즉 sharp failure boundary가 완전한 black-box는 아니다.

다만 이 law는 직접 human-social feature가 아니라 `abs_vs_core`와 `expert_prob_mean`만 사용했다. 따라서 HS-JEPA core는 label predictor라기보다, raw KNN/priors/action routes가 과하게 벗어났는지를 재는 listener agreement 기준점으로 작동한다.

또 하나의 중요한 점은 tree leaf 값이 모두 음수라는 것이다. 이 law는 절대적 positive-gain predictor가 아니라, 여러 toxic action 중 덜 위험한 prior-reset 후보를 상대적으로 고르는 toxicity-minimizing ranker다.

결론적으로 HS-JEPA release decoder는 `human-state -> label`이 아니라 `raw memory가 불안정할 때 core agreement를 기준으로 prior reset을 허용하는 law`로 정리할 수 있다.