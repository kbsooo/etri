# Episode-Conditioned Selective Assignment Decoder

## 한 줄 요약

row-level hidden episode state를 cell-level target/listener assignment decoder에 주입했다.

즉 HS-JEPA가 먼저 `오늘 raw memory를 믿어도 되는 episode인가`를 판단하고, 그 다음 `어느 target만 어떤 listener route로 바꿀지`를 고른다.

## 재현 명령

```bash
python3 sleep_competition_adapter/episode_selective_assignment_decoder.py
```

public LB score ledger, 기존 submission probability, action teacher, frontier file은 쓰지 않는다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- row episode detector OOF logloss: `0.634030`
- best no-episode assignment OOF: `0.632902`
- best episode-conditioned assignment OOF: `0.632902`
- episode gain over raw: `-0.004095`
- episode gain over no-episode: `0.000000`
- release law: `episode_route_gate__episode_tree_depth2_leaf18`
- release switched OOF cells: `59`
- target+family null p-value: `0.020333`
- generated candidate: `submission_hsjepa_episode_selective_assignment_decoder_65ce2d48_uploadsafe.csv`
- same prediction as failure-boundary law: `True`

## 판정

episode-conditioned view는 raw KNN보다 좋아졌지만, no-episode route law를 넘지 못했다.

release model의 nonzero feature에도 `row_episode_*`가 남지 않았다.
즉 row-level hidden episode state는 OOF에서 존재하지만, 현 selective assignment decoder는 그 정보를 실제 action 선택으로 번역하지 못했고 route-disagreement law로 붕괴했다.

따라서 이 실험의 결론은 positive release가 아니라 negative architecture evidence다.
다음 단계는 episode score를 단순 feature로 넣는 방식이 아니라, episode가 action space 자체를 제한하거나 listener responsibility를 재가중하는 구조여야 한다.

## Release target counts

| target | count |
| --- | --- |
| Q1 | 9 |
| Q2 | 9 |
| Q3 | 9 |
| S1 | 8 |
| S2 | 8 |
| S3 | 8 |
| S4 | 8 |

## Release expert-family counts

| expert_family | count |
| --- | --- |
| prior | 59 |

## Release model top features

| feature | importance |
| --- | --- |
| expert_prob_mean | 0.488529 |
| abs_vs_core | 0.423010 |
| raw_confidence | 0.088461 |
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
| family_is_prior | 0.000000 |
| family_is_core_geometry | 0.000000 |
| family_is_core_action_health | 0.000000 |
| family_is_raw_action_core_health | 0.000000 |
| abs_vs_global | 0.000000 |

## Top policies

| law_name | policy | param | logloss | switched_cells | mean_realized_gain_all_cells | positive_true_gain_rate | episode_route_match_rate | target_family_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_law_no_episode__episode_tree_depth2_leaf18 | topfrac | 0.080000 | 0.632902 | 59 | 0.004095 | 0.593220 | 0.000000 | 0.020667 |
| episode_route_gate__episode_tree_depth2_leaf18 | topfrac | 0.080000 | 0.632902 | 59 | 0.004095 | 0.593220 | 0.000000 | 0.020333 |
| episode_full_assignment__episode_tree_depth2_leaf18 | topfrac | 0.080000 | 0.632902 | 59 | 0.004095 | 0.593220 | 0.000000 | 0.027000 |
| route_law_no_episode__episode_tree_depth2_leaf18 | topfrac | 0.060000 | 0.632964 | 44 | 0.004033 | 0.636364 | 0.000000 | 0.014333 |
| episode_route_gate__episode_tree_depth2_leaf18 | topfrac | 0.060000 | 0.632964 | 44 | 0.004033 | 0.636364 | 0.000000 | 0.019333 |
| episode_full_assignment__episode_tree_depth2_leaf18 | topfrac | 0.060000 | 0.632964 | 44 | 0.004033 | 0.636364 | 0.000000 | 0.020333 |
| route_law_no_episode__episode_tree_depth2_leaf18 | topfrac | 0.040000 | 0.633604 | 29 | 0.003393 | 0.655172 | 0.000000 | 0.017000 |
| episode_route_gate__episode_tree_depth2_leaf18 | topfrac | 0.040000 | 0.633604 | 29 | 0.003393 | 0.655172 | 0.000000 | 0.018000 |
| episode_full_assignment__episode_tree_depth2_leaf18 | topfrac | 0.040000 | 0.633604 | 29 | 0.003393 | 0.655172 | 0.000000 | 0.019333 |
| episode_full_assignment__episode_gbdt_shallow | topfrac | 0.020000 | 0.633748 | 15 | 0.003249 | 0.800000 | 0.333333 | 0.000000 |
| route_law_no_episode__episode_tree_depth2_leaf18 | topfrac | 0.150000 | 0.633951 | 110 | 0.003046 | 0.536364 | 0.172727 | 0.044667 |
| episode_route_gate__episode_tree_depth2_leaf18 | topfrac | 0.150000 | 0.633951 | 110 | 0.003046 | 0.536364 | 0.172727 | 0.051333 |
| episode_full_assignment__episode_tree_depth2_leaf18 | topfrac | 0.150000 | 0.633951 | 110 | 0.003046 | 0.536364 | 0.172727 | 0.046000 |
| episode_human_listener_assignment__episode_gbdt_shallow | topfrac | 0.060000 | 0.634301 | 44 | 0.002696 | 0.772727 | 0.227273 | 0.001000 |
| episode_full_assignment__episode_gbdt_shallow | threshold | 0.120000 | 0.634449 | 10 | 0.002548 | 0.800000 | 0.100000 | 0.001667 |
| route_law_no_episode__episode_tree_depth2_leaf18 | topfrac | 0.100000 | 0.634589 | 74 | 0.002408 | 0.554054 | 0.054054 | 0.079667 |

## 논문용 해석

이 실험은 HS-JEPA를 두 단계로 분해한다.

1. row episode encoder: 하루 전체의 raw-memory failure state를 예측한다.
2. selective assignment decoder: 그 episode state를 target/listener route 선택에 사용한다.

episode-conditioned decoder가 no-episode decoder보다 낫다면, HS-JEPA core는 단순 feature가 아니라 action decoder의 독성을 줄이는 latent state로 작동한다는 강한 증거다.

반대로 no-episode가 더 좋다면, row episode state는 존재하지만 release-grade target assignment에는 아직 충분히 번역되지 않았다는 뜻이다.