# Subject-Invariant Episode Controller

## 한 줄 요약

episode row-state controller를 full OOF 최저점으로 고르지 않고, subject가 바뀌어도 살아남는 목적함수로 고르는 실험이다.

## 재현 명령

```bash
python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py
python3 sleep_competition_adapter/subject_invariant_episode_controller.py
```

public LB, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.

## 왜 이것이 HS-JEPA/LeJEPA 진단인가

이 실험은 새 predictor를 만드는 실험이 아니라, HS-JEPA representation이 만든 action을 믿어도 되는지 검사하는 health check다.

| JEPA 구성요소 | 이 실험에서의 의미 |
| --- | --- |
| context | row episode state와 target/route context |
| target representation | full OOF에서 성공한 것처럼 보이는 action-space policy |
| predictor | subject를 하나 가린 상태에서 어떤 controller가 target representation을 안정적으로 재현하는지 선택 |
| energy / decoder | 선택된 controller가 held-out subject에서 raw보다 낮은 action energy를 만드는지 검사 |
| LeJEPA-style health check | subject-LOO, active subject rate, negative heldout action으로 shortcut/collapse를 판정 |

따라서 이 문서는 positive release 모델이라기보다, HS-JEPA decoder가 subject shortcut에 빠졌는지 확인하는 anti-collapse audit다.

## Architecture Contract

```text
row episode representation
  -> candidate action-space controller
  -> subject-heldout policy selection
  -> heldout action-health stress
  -> accept only if representation survives subject shift
```

## 핵심 결과

- raw OOF logloss: `0.636997`
- full OOF best restricted logloss: `0.629771`
- best subject-invariant objective: `active_subject_balanced`
- best subject-LOO logloss: `0.636997`
- best subject-LOO delta vs raw: `-0.000000`
- release objective: `active_subject_balanced`
- release policy: `route_tree_depth3_leaf24||episode_family_space_q90||topfrac||0.06`
- release full OOF logloss: `0.629771`
- release candidate: `submission_hsjepa_subject_invariant_episode_controller_816c3a6e_uploadsafe.csv`
- verdict: `subject_invariant_selector_is_safe_but_inactive`

## Objective leaderboard

| objective_name | subject_loo_logloss | delta_vs_raw | heldout_active_rate | heldout_positive_rate_all | heldout_negative_rate_all | selected_policy_entropy |
| --- | --- | --- | --- | --- | --- | --- |
| active_subject_balanced | 0.636997 | -0.000000 | 0.000000 | 0.000000 | 0.000000 | 3 |
| minimax_active_gain | 0.636997 | -0.000000 | 0.000000 | 0.000000 | 0.000000 | 3 |
| full_oof_gain | 0.639997 | 0.003000 | 0.100000 | 0.000000 | 0.100000 | 3 |
| negative_veto_balanced | 0.639997 | 0.003000 | 0.100000 | 0.000000 | 0.100000 | 3 |
| coverage_first_controller | 0.653200 | 0.016203 | 0.700000 | 0.100000 | 0.600000 | 5 |

## Release objective top policies

| objective_name | law_name | action_space_policy | selection_policy | selection_param | objective_score | logloss | gain_per_cell | selected_cells | active_subjects | negative_active_subjects | no_action_subject_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.060000 | 0.003037 | 0.629771 | 0.007227 | 44 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.080000 | 0.002565 | 0.630064 | 0.006933 | 59 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.100000 | 0.002035 | 0.630617 | 0.006380 | 74 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.040000 | 0.001893 | 0.632680 | 0.004317 | 29 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.030000 | 0.001735 | 0.632998 | 0.003999 | 22 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.060000 | 0.001641 | 0.631830 | 0.005167 | 44 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.150000 | 0.001506 | 0.631138 | 0.005859 | 77 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | threshold | -0.020000 | 0.001506 | 0.631138 | 0.005859 | 77 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.040000 | 0.000997 | 0.633822 | 0.003175 | 29 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_exact_route_space_q90 | topfrac | 0.100000 | 0.000814 | 0.634490 | 0.002507 | 74 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_exact_route_space_q90 | topfrac | 0.080000 | 0.000793 | 0.634540 | 0.002457 | 59 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.020000 | 0.000771 | 0.634440 | 0.002557 | 15 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth2_leaf28 | episode_exact_route_space_q90 | topfrac | 0.150000 | 0.000585 | 0.635011 | 0.001986 | 77 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth2_leaf28 | episode_exact_route_space_q90 | threshold | -0.020000 | 0.000585 | 0.635011 | 0.001986 | 77 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth2_leaf28 | episode_exact_route_space_q90 | threshold | -0.010000 | 0.000585 | 0.635011 | 0.001986 | 77 | 2 | 0 | 0.800000 |
| active_subject_balanced | route_tree_depth3_leaf24 | episode_exact_route_space_q90 | topfrac | 0.150000 | 0.000585 | 0.635011 | 0.001986 | 77 | 2 | 0 | 0.800000 |

## Release test switched target counts

| target | count |
| --- | --- |
| Q1 | 15 |
| Q2 | 15 |
| Q3 | 15 |
| S1 | 15 |
| S2 | 15 |
| S3 | 15 |
| S4 | 15 |

## Subject-LOO decisions for release objective

| heldout_subject | selected_action_space_policy | heldout_logloss | heldout_raw_logloss | heldout_gain_per_cell | heldout_selected_cells | heldout_positive | heldout_negative |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id01 | episode_family_space_q90 | 0.711960 | 0.711960 | 0.000000 | 0 | False | False |
| id02 | unrestricted_route_law | 0.511292 | 0.511292 | 0.000000 | 0 | False | False |
| id03 | episode_family_space_q90 | 0.523093 | 0.523093 | 0.000000 | 0 | False | False |
| id04 | episode_family_space_q90 | 0.648093 | 0.648093 | 0.000000 | 0 | False | False |
| id05 | episode_family_space_q90 | 0.673918 | 0.673918 | 0.000000 | 0 | False | False |
| id06 | episode_family_space_q90 | 0.409706 | 0.409706 | 0.000000 | 0 | False | False |
| id07 | episode_family_space_q90 | 0.683280 | 0.683280 | 0.000000 | 0 | False | False |
| id08 | episode_family_space_q90 | 0.698176 | 0.698176 | 0.000000 | 0 | False | False |
| id09 | episode_family_space_q70 | 0.791449 | 0.791449 | 0.000000 | 0 | False | False |
| id10 | episode_family_space_q90 | 0.722265 | 0.722265 | 0.000000 | 0 | False | False |

## 논문용 해석

이 실험은 HS-JEPA representation을 더 크게 만드는 실험이 아니라, representation이 만든 action을 어떤 기준으로 믿을지 정의한다.
LeJEPA식으로 보면 full OOF loss만 낮은 controller는 shortcut/collapse일 수 있다.
따라서 subject-invariant objective는 human-state representation의 건강성 검사이자 row-target assignment decoder의 안전장치다.

좋은 결과는 subject-LOO에서도 raw보다 낮은 logloss를 유지하는 것이다.
나쁜 결과는 episode state가 action-space를 제한할 수는 있지만, 아직 subject-general law로는 번역되지 않았다는 뜻이다.
