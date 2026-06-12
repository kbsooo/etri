# Cross-Subject Episode Prototype Transport

## 한 줄 요약

다른 subject에서 성공한 episode-action prototype을 held-out subject의 비슷한 row-target-route로 전이할 수 있는지 검증했다.

## 재현 명령

```bash
python3 sleep_competition_adapter/cross_subject_episode_prototype_transport.py
```

public LB, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.

## 왜 이것이 HS-JEPA인가

이 실험의 핵심은 kNN 자체가 아니다. kNN은 JEPA predictor를 non-parametric하게 구현한 한 가지 방식일 뿐이다.

| JEPA 구성요소 | 이 실험에서의 의미 |
| --- | --- |
| context | 현재 row의 lifelog 상태, target route, expert route, row episode state |
| target representation | 다른 subject에서 실제로 성공했던 hidden episode-action prototype |
| predictor | 현재 context embedding에서 가까운 성공 action representation을 검색/예측하는 cross-subject prototype transport |
| energy / decoder | 예측된 target representation과 가까운 action만 row-target correction으로 release |
| LeJEPA-style health check | active subject coverage, negative active subject count, robust transport score로 shortcut/collapse를 검사 |

따라서 이 실험은 label을 직접 맞히는 모델이 아니라, 보이는 human context에서 보이지 않는 action representation을 예측하는 HS-JEPA adapter다.

## Architecture Contract

```text
visible human-state context
  -> row/target/route joint embedding
  -> predict hidden episode-action representation from peer subjects
  -> score action-health energy
  -> release sparse row-target correction only when transport is healthy
```

## 핵심 결과

- raw OOF logloss: `0.636997`
- best transport OOF logloss: `0.629211`
- best transport delta vs raw: `-0.007786`
- robust release law: `route_episode_context__target_episode_family__knn13_distance`
- robust release OOF logloss: `0.630158`
- robust release active subjects: `7`
- robust release negative active subjects: `1`
- candidate: `submission_hsjepa_cross_subject_episode_prototype_transport_b034ce3b_uploadsafe.csv`
- verdict: `cross_subject_transport_positive`

## Best by OOF logloss

| law_name | policy | param | logloss | switched_cells | mean_realized_gain_all_cells | active_subjects | negative_active_subjects | robust_transport_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_episode_context__target_episode_family__knn7_distance | topfrac | 0.100000 | 0.629211 | 74 | 0.007786 | 8 | 3 | 0.001703 |
| route_episode_context__target_episode_family__knn7_uniform | topfrac | 0.080000 | 0.629889 | 59 | 0.007108 | 7 | 2 | 0.002473 |
| route_episode_context__target_episode_family__knn13_distance | topfrac | 0.060000 | 0.630158 | 44 | 0.006840 | 7 | 1 | 0.004232 |
| route_episode_context__target_episode_family__knn7_uniform | topfrac | 0.100000 | 0.630158 | 74 | 0.006839 | 8 | 3 | 0.000830 |
| route_episode_context__target__knn21_uniform | topfrac | 0.100000 | 0.630491 | 74 | 0.006506 | 5 | 1 | 0.002565 |
| route_episode_context__target_episode_family__knn7_distance | topfrac | 0.080000 | 0.630651 | 59 | 0.006346 | 8 | 3 | 0.000775 |
| route_episode_context__target_episode_family__knn13_distance | topfrac | 0.080000 | 0.630721 | 59 | 0.006276 | 7 | 3 | 0.000620 |
| route_episode_context__target_episode_family__knn21_uniform | topfrac | 0.060000 | 0.630768 | 44 | 0.006229 | 6 | 2 | 0.001605 |
| route_episode_context__target_episode_family__knn13_uniform | topfrac | 0.040000 | 0.630835 | 29 | 0.006162 | 5 | 1 | 0.003221 |
| route_episode_context__target_episode_family__knn13_distance | topfrac | 0.150000 | 0.631131 | 110 | 0.005867 | 10 | 3 | 0.000074 |
| route_episode_context__target_episode_family__knn21_uniform | topfrac | 0.020000 | 0.631184 | 15 | 0.005813 | 4 | 1 | 0.002685 |
| compact_episode_context__target_episode_family__knn7_uniform | topfrac | 0.100000 | 0.631367 | 74 | 0.005630 | 9 | 3 | -0.000067 |
| compact_episode_context__target_episode_family__knn21_uniform | topfrac | 0.080000 | 0.631374 | 59 | 0.005623 | 8 | 1 | 0.003511 |
| route_episode_context__target_episode_family__knn13_distance | topfrac | 0.100000 | 0.631441 | 74 | 0.005556 | 9 | 4 | -0.001812 |
| compact_episode_context__target_episode_family__knn7_distance | topfrac | 0.150000 | 0.631492 | 110 | 0.005505 | 10 | 4 | -0.001866 |
| compact_episode_context__target_episode_family__knn7_distance | topfrac | 0.100000 | 0.631536 | 74 | 0.005461 | 9 | 3 | -0.000193 |

## Best by robust transport score

| law_name | policy | param | logloss | switched_cells | mean_realized_gain_all_cells | active_subjects | negative_active_subjects | robust_transport_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_episode_context__target_episode_family__knn13_distance | topfrac | 0.060000 | 0.630158 | 44 | 0.006840 | 7 | 1 | 0.004232 |
| route_episode_context__target__knn21_distance | topfrac | 0.030000 | 0.632800 | 22 | 0.004197 | 4 | 0 | 0.003697 |
| compact_episode_context__target_episode_family__knn21_uniform | topfrac | 0.080000 | 0.631374 | 59 | 0.005623 | 8 | 1 | 0.003511 |
| route_episode_context__target_episode_family__knn13_uniform | topfrac | 0.040000 | 0.630835 | 29 | 0.006162 | 5 | 1 | 0.003221 |
| route_episode_context__target_episode_family__knn21_uniform | topfrac | 0.020000 | 0.631184 | 15 | 0.005813 | 4 | 1 | 0.002685 |
| route_episode_context__target__knn21_uniform | topfrac | 0.100000 | 0.630491 | 74 | 0.006506 | 5 | 1 | 0.002565 |
| route_episode_context__target_episode_family__knn7_uniform | topfrac | 0.080000 | 0.629889 | 59 | 0.007108 | 7 | 2 | 0.002473 |
| route_episode_context__target_episode_family__knn21_uniform | topfrac | 0.010000 | 0.633620 | 7 | 0.003377 | 2 | 0 | 0.002469 |
| route_episode_context__target_episode_family__knn21_distance | topfrac | 0.010000 | 0.633620 | 7 | 0.003377 | 2 | 0 | 0.002469 |
| route_episode_context__target_episode_family__knn21_uniform | topfrac | 0.030000 | 0.632026 | 22 | 0.004971 | 5 | 1 | 0.002323 |
| route_episode_context__target__knn21_uniform | topfrac | 0.020000 | 0.634339 | 15 | 0.002658 | 3 | 0 | 0.002235 |
| route_episode_context__target__knn21_uniform | topfrac | 0.010000 | 0.634419 | 7 | 0.002578 | 3 | 0 | 0.002166 |
| route_episode_context__target__knn21_distance | topfrac | 0.020000 | 0.634597 | 15 | 0.002401 | 3 | 0 | 0.002128 |
| route_episode_context__target__knn7_uniform | topfrac | 0.020000 | 0.632831 | 15 | 0.004167 | 5 | 1 | 0.002006 |
| compact_episode_context__target_episode_family__knn21_distance | topfrac | 0.080000 | 0.633356 | 59 | 0.003641 | 8 | 1 | 0.001835 |
| route_episode_context__target_episode_family__knn35_distance | topfrac | 0.010000 | 0.634213 | 7 | 0.002784 | 2 | 0 | 0.001791 |

## Release test switched target counts

| target | count |
| --- | --- |
| Q1 | 12 |
| Q2 | 32 |
| Q3 | 9 |
| S1 | 1 |
| S2 | 13 |
| S3 | 24 |
| S4 | 14 |

## 논문용 해석

이 실험은 HS-JEPA를 개인의 과거 label memory가 아니라 cross-subject target-representation prediction으로 해석한다.
여기서 target representation은 raw label이 아니라, peer subject에서 성공한 episode-action prototype이다.
성공하면 human-state latent가 subject identity를 넘어 전이 가능한 action geometry를 가진다는 증거가 된다.
실패하면 현재 episode latent는 local diagnostic으로는 유효하지만, peer subject로 전이 가능한 일반 representation은 아직 아니라는 결론이다.
