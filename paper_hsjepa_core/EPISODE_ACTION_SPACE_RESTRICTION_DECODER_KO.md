# Episode Action-Space Restriction Decoder

## 한 줄 요약

row episode state를 gain model feature로 넣지 않고, action 후보 공간을 제한하는 controller로 사용했다.

## 재현 명령

```bash
python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py
```

public LB score ledger, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- unrestricted best OOF: `0.632902`
- best restricted OOF: `0.629771`
- restricted delta vs raw: `-0.007227`
- restricted delta vs unrestricted: `-0.003132`
- release action-space policy: `episode_family_space_q90`
- release switched OOF cells: `44`
- release target+family null p-value: `0.000625`
- generated candidate: `submission_hsjepa_episode_action_space_restriction_decoder_816c3a6e_uploadsafe.csv`
- same prediction as failure-boundary law: `False`

## 판정

restricted action-space가 unrestricted route law를 이겼다. row episode state가 action toxicity를 줄이는 controller로 작동했다는 positive evidence다.

## Release target counts

| target | count |
| --- | --- |
| Q1 | 6 |
| Q2 | 6 |
| Q3 | 6 |
| S1 | 6 |
| S2 | 7 |
| S3 | 8 |
| S4 | 5 |

## Release expert-family counts

| expert_family | count |
| --- | --- |
| core_geometry | 25 |
| prior | 19 |

## Release scorer top features

| feature | importance |
| --- | --- |
| expert_prob_mean | 0.413576 |
| abs_vs_core | 0.358109 |
| confidence_delta | 0.228316 |
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

## Top policies

| law_name | action_space_policy | selection_policy | selection_param | logloss | switched_cells | mean_realized_gain_all_cells | episode_family_match_rate | target_family_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.060000 | 0.629771 | 44 | 0.007227 | 1.000000 | 0.000625 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.080000 | 0.630064 | 59 | 0.006933 | 1.000000 | 0.015000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.100000 | 0.630617 | 74 | 0.006380 | 1.000000 | 0.034375 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.150000 | 0.631138 | 77 | 0.005859 | 1.000000 | 1.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | threshold | -0.020000 | 0.631138 | 77 | 0.005859 | 1.000000 | 1.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q70 | topfrac | 0.150000 | 0.631618 | 110 | 0.005379 | 1.000000 | 0.010625 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | topfrac | 0.150000 | 0.631706 | 110 | 0.005291 | 1.000000 | 0.173125 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | topfrac | 0.100000 | 0.631817 | 74 | 0.005180 | 1.000000 | 0.087500 |
| route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.060000 | 0.631830 | 44 | 0.005167 | 0.431818 | 0.059375 |
| route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.080000 | 0.632006 | 59 | 0.004991 | 0.423729 | 0.087500 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | topfrac | 0.150000 | 0.632115 | 77 | 0.004882 | 1.000000 | 1.000000 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | threshold | -0.020000 | 0.632115 | 77 | 0.004882 | 1.000000 | 1.000000 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | threshold | -0.010000 | 0.632115 | 77 | 0.004882 | 1.000000 | 1.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | threshold | -0.020000 | 0.632250 | 147 | 0.004748 | 1.000000 | 0.835000 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | topfrac | 0.100000 | 0.632492 | 74 | 0.004505 | 1.000000 | 0.851250 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.040000 | 0.632680 | 29 | 0.004317 | 1.000000 | 0.258125 |

## 논문용 해석

이 실험은 HS-JEPA의 row-state encoder를 decoder feature가 아니라 action-space controller로 사용했다.
feature injection이 실패했기 때문에, 더 강한 구조적 결합을 검증한 것이다.

restricted policy가 unrestricted policy보다 낮은 OOF를 만들면, row episode state가 action toxicity를 줄이는 controller라는 주장이 강화된다.
반대로 restricted policy가 뒤처지면, 현재 row episode는 diagnostic으로는 유효하지만 action-space를 자를 만큼 충분한 causal/responsibility state는 아니라는 결론이다.