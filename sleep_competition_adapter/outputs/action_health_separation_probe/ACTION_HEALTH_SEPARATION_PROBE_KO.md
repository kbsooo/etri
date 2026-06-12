# Action-Health Separation Probe

## 목적

이 실험은 HS-JEPA core representation이 action decoder의 독성을 public score 없이 줄일 수 있는지 본다.

Health score 계산에는 public LB를 쓰지 않는다. Public LB는 마지막 retrospective evaluation에만 쓴다.

## Health Score 구성

- core support: core-state geometry가 해당 row를 action-support row로 보는가
- outlier-law alignment: action 방향이 train에서 관측된 personal/cohort outlier target law와 맞는가
- route safety: train target manifold에서 멀어지는가
- spread/amplitude safety: 너무 넓고 큰 action field인가

## Retrospective 결과

- public score used for health features: `False`
- public score used for retrospective evaluation: `True`
- scored candidate count: `7`
- Spearman health vs -public_lb: `0.7567874686642696`
- nonzero-action scored candidate count: `6`
- nonzero-action Spearman health vs -public_lb: `0.8406680016960503`
- success mean health: `0.5434107504939683`
- failure mean health: `0.5157982566038454`

## Action Field Ranking

| semantic_name | public_lb | hsjepa_action_health_score | changed_cells | changed_rows | mean_core_support_rank | mean_weighted_law_alignment | route_energy_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| core_geometry_outlier_route_bigbet | nan | 0.638354 | 561 | 87 | 0.660271 | 0.177573 | 0.003140 |
| row_state_vector_frontier | 0.567748 | 0.587217 | 315 | 45 | 0.475467 | -0.005847 | 0.006007 |
| frontier_active_silence | 0.567727 | 0.569036 | 315 | 45 | 0.475467 | -0.005847 | 0.003079 |
| public_equation_jump | 0.568123 | 0.550000 | 0 | 0 | 0.000000 | 0.000000 | 0.000000 |
| target_split_xor_stress | 0.567930 | 0.520018 | 326 | 56 | 0.477080 | -0.002527 | 0.006303 |
| cross_listener_transport_stress | 0.568486 | 0.519114 | 338 | 59 | 0.506272 | -0.006330 | 0.006602 |
| q3_repair_only_stress | 0.567930 | 0.497372 | 325 | 55 | 0.476591 | -0.001003 | 0.006314 |
| dual_head_toxicity_stress | 0.568494 | 0.478281 | 1185 | 184 | 0.530056 | -0.023088 | 0.019850 |
| target_route_teacher_only | nan | 0.427308 | 385 | 105 | 0.522878 | -0.015220 | 0.042122 |
| target_route_q2_extra | nan | 0.422264 | 393 | 109 | 0.522656 | -0.018102 | 0.045148 |
| public_private_toxicity | nan | 0.407694 | 435 | 130 | 0.531154 | -0.011016 | 0.060130 |

## 생성된 후보

- `submission_hsjepa_action_health_separation_core_route_release_de79e203_uploadsafe.csv`

이 후보는 `core_geometry_outlier_route_bigbet`의 broad action field를 그대로 믿지 않고, cell-level action-health 하위 tail을 제거한 release다.

핵심 수치:

- input bigbet cells: `310`
- released cells: `180`
- released rows: `38`
- release threshold: `0.725067`

## 해석

좋아지면 HS-JEPA core representation이 실제로 action decoder 독성을 줄인다는 강한 증거다.

나빠지면 현재 core-state geometry는 row support를 찾는 데는 강하지만, cell-level release health를 단독으로 결정하기에는 아직 부족하다는 뜻이다.
