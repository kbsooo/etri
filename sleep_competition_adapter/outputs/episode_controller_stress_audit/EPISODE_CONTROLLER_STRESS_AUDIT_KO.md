# Episode Controller Stress Audit

## 한 줄 요약

episode action-space controller가 전체 OOF policy selection artifact인지 subject-LOO로 검증했다.

## 재현 명령

```bash
python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py
python3 sleep_competition_adapter/episode_controller_stress_audit.py
```

public LB, prior submission probability, action teacher, frontier file은 사용하지 않는다.

## 핵심 결과

- raw OOF logloss from cells: `0.636997`
- full best policy logloss: `0.629771`
- subject-LOO selected-policy logloss: `0.639997`
- subject-LOO delta vs raw: `0.003000`
- subject-LOO positive subject rate: `0.000000`
- most selected policy: `route_tree_depth3_leaf24||episode_family_space_q90||topfrac||0.06`
- verdict: `policy_selection_artifact_risk`

## Top Full-OOF Policies

| law_name | action_space_policy | selection_policy | selection_param | logloss | gain_per_cell | selected_cells | positive_subjects | negative_subjects | min_subject_gain_per_cell |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.060000 | 0.629771 | 0.007227 | 44.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.080000 | 0.630064 | 0.006933 | 59.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.100000 | 0.630617 | 0.006380 | 74.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | threshold | -0.020000 | 0.631138 | 0.005859 | 77.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.150000 | 0.631138 | 0.005859 | 77.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_family_space_q70 | topfrac | 0.150000 | 0.631618 | 0.005379 | 110.000000 | 3 | 4 | -0.013907 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | topfrac | 0.150000 | 0.631706 | 0.005291 | 110.000000 | 3 | 3 | -0.006336 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | topfrac | 0.100000 | 0.631817 | 0.005180 | 74.000000 | 3 | 2 | -0.006336 |
| route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.060000 | 0.631830 | 0.005167 | 44.000000 | 2 | 0 | 0.000000 |
| route_tree_depth3_leaf24 | episode_rows_only_any_route_q90 | topfrac | 0.080000 | 0.632006 | 0.004991 | 59.000000 | 1 | 1 | -0.005978 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | threshold | -0.020000 | 0.632115 | 0.004882 | 77.000000 | 1 | 1 | -0.006686 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | threshold | -0.010000 | 0.632115 | 0.004882 | 77.000000 | 1 | 1 | -0.006686 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | topfrac | 0.150000 | 0.632115 | 0.004882 | 77.000000 | 1 | 1 | -0.006686 |
| route_tree_depth3_leaf24 | episode_family_space_q80 | threshold | -0.020000 | 0.632250 | 0.004748 | 147.000000 | 2 | 4 | -0.006336 |
| route_tree_depth2_leaf28 | episode_family_space_q90 | topfrac | 0.100000 | 0.632492 | 0.004505 | 74.000000 | 1 | 1 | -0.006686 |
| route_tree_depth3_leaf24 | episode_family_space_q90 | topfrac | 0.040000 | 0.632680 | 0.004317 | 29.000000 | 2 | 0 | 0.000000 |

## Subject-LOO Decisions

| heldout_subject | selected_action_space_policy | heldout_logloss | heldout_raw_logloss | heldout_gain_per_cell | heldout_selected_cells | heldout_positive |
| --- | --- | --- | --- | --- | --- | --- |
| id01 | episode_family_space_q90 | 0.711960 | 0.711960 | 0.000000 | 0 | False |
| id02 | episode_rows_only_any_route_q90 | 0.539925 | 0.511292 | -0.028633 | 35 | False |
| id03 | episode_family_space_q90 | 0.523093 | 0.523093 | 0.000000 | 0 | False |
| id04 | episode_family_space_q90 | 0.648093 | 0.648093 | 0.000000 | 0 | False |
| id05 | episode_family_space_q90 | 0.673918 | 0.673918 | 0.000000 | 0 | False |
| id06 | episode_family_space_q90 | 0.409706 | 0.409706 | 0.000000 | 0 | False |
| id07 | episode_family_space_q90 | 0.683280 | 0.683280 | 0.000000 | 0 | False |
| id08 | episode_family_space_q90 | 0.698176 | 0.698176 | 0.000000 | 0 | False |
| id09 | episode_veto_family_mismatch_q90 | 0.791449 | 0.791449 | 0.000000 | 0 | False |
| id10 | episode_family_space_q90 | 0.722265 | 0.722265 | 0.000000 | 0 | False |

## 논문용 해석

이 audit는 controller 자체를 다시 학습하지 않는다. 이미 OOF로 저장된 action logs만 사용해, policy selection 단계가 held-out subject label에 의존했는지 본다.

subject-LOO에서도 raw보다 낮은 logloss를 유지하면, episode controller는 단일 OOF grid artifact가 아니라 subject-general action-space restriction이라는 증거가 된다.
반대로 subject-LOO에서 무너지면, 0.62977은 full OOF에서 정책을 고른 선택 편향일 가능성이 크다.