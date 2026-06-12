# Action-Health Separation Probe

## 한 줄 결론

HS-JEPA core representation으로 만든 score-free action-health metric은 기존 action field들의 public 성공/실패 방향과 꽤 강하게 정렬된다.

특히 no-action baseline을 제외한 nonzero action field 6개에서:

- Spearman(action health, -public LB): `0.840668`
- p-value: `0.036058`

이 값은 public LB를 health score 계산에 넣어서 얻은 것이 아니다.
Public LB는 마지막 retrospective evaluation에만 사용했다.

## 왜 중요한가

직전 `lifelog_core_state_evidence` 실험은 다음을 보였다.

```text
HS-JEPA core는 직접 label classifier로는 약하지만,
row-action support geometry로는 강하다.
```

하지만 이것만으로는 부족하다.
row support를 잘 찾아도, 실제 action으로 번역할 때 독성이 생기면 public/private에서 무너진다.

따라서 이번 실험의 질문은 더 날카롭다.

> HS-JEPA core가 action decoder의 독성을 public score 없이 줄일 수 있는가?

## 실험 코드

```bash
python3 sleep_competition_adapter/action_health_separation_probe.py
```

산출물:

- `sleep_competition_adapter/outputs/action_health_separation_probe/action_field_health_ranking.csv`
- `sleep_competition_adapter/outputs/action_health_separation_probe/cell_action_health_audit.csv`
- `sleep_competition_adapter/outputs/action_health_separation_probe/action_health_separation_readout.json`
- `sleep_competition_adapter/outputs/action_health_separation_probe/ACTION_HEALTH_SEPARATION_PROBE_KO.md`
- `submission_hsjepa_action_health_separation_core_route_release_de79e203_uploadsafe.csv`

## Health Score 구성

Health score는 public LB 없이 계산한다.

구성 요소:

1. core support
   - HS-JEPA core-state geometry가 해당 row를 action-support row로 보는가

2. outlier-law alignment
   - action 방향이 train에서 관측된 personal/cohort outlier target law와 맞는가

3. route safety
   - action 후 target vector가 train target manifold에서 너무 멀어지는가

4. spread/amplitude safety
   - action field가 너무 넓거나, logit move가 너무 큰가

즉 health score는 다음을 묻는다.

```text
이 action은 core-state가 지지하는 row에서,
train에서 보인 human-state law와 맞는 방향으로,
target route invariant를 크게 깨지 않으면서,
너무 넓거나 과격하지 않게 움직이는가?
```

## Retrospective 결과

Public LB는 health score 계산에는 쓰지 않고, 마지막 검증 label로만 사용했다.

| 평가 | 값 |
| --- | ---: |
| scored candidates | 7 |
| Spearman health vs -public LB | 0.756787 |
| p-value | 0.048905 |
| nonzero action candidates | 6 |
| nonzero Spearman health vs -public LB | 0.840668 |
| nonzero p-value | 0.036058 |

해석:

샘플 수가 작으므로 과장하면 안 된다.
하지만 이 결과는 HS-JEPA action-health가 단순한 사후 해석이 아니라, 실제 toxic/stress action field를 걸러내는 score-free diagnostic일 가능성을 강화한다.

## Action Field Ranking

상위:

- `core_geometry_outlier_route_bigbet`: public 미제출, health `0.638354`
- `row_state_vector_frontier`: public `0.567748`, health `0.587217`
- `frontier_active_silence`: public `0.567727`, health `0.569036`

하위:

- `dual_head_toxicity_stress`: public `0.568494`, health `0.478281`
- `target_route_teacher_only`: public 미제출, health `0.427308`
- `target_route_q2_extra`: public 미제출, health `0.422264`
- `public_private_toxicity`: public 미제출, health `0.407694`

중요한 점:

dual-head toxicity stress와 cross-listener transport는 사람이 보기에 coherent해 보였지만 public에서 나빴다.
이번 health metric은 이 둘을 positive frontier보다 낮게 둔다.

## 생성된 후보

`core_geometry_outlier_route_bigbet`은 broad action field였다.
이번 probe는 그 후보의 cell-level action-health 하위 tail을 제거한 release를 만든다.

파일:

```text
submission_hsjepa_action_health_separation_core_route_release_de79e203_uploadsafe.csv
```

핵심 수치:

- input bigbet cells: 310
- released cells: 180
- released rows: 38
- dropped cells mean health: 0.673729
- released cells mean health: 0.778574

비교:

- bigbet meaningful changed cells: 294
- health-gated meaningful changed cells: 176
- bigbet meaningful changed rows: 52
- health-gated meaningful changed rows: 38

## 논문 해석

이 실험은 HS-JEPA를 더 명확하게 만든다.

HS-JEPA는 다음 두 단계를 분리한다.

```text
1. core representation: hidden human-state geometry를 만든다.
2. action-health decoder: 그 geometry 위에서 release할 action과 toxic action을 구분한다.
```

즉 좋은 latent를 바로 probability correction으로 바꾸지 않는다.

```text
representation -> responsibility -> health -> release
```

이 구조가 일반적인 tabular blending과 다른 부분이다.

## 실패 시 해석

새 후보가 public에서 나쁘면 다음이 죽는다.

```text
현재 cell-level action-health는 broad action field의 하위 tail 제거에는 부족하다.
```

하지만 다음은 여전히 살아 있다.

```text
score-free action-health ranking은 기존 positive/stress action field를 구분한다.
```

따라서 실패하더라도 HS-JEPA core가 의미 없다는 뜻은 아니다.
실패는 cell-level release rule이 아직 충분히 target/listener-specific하지 않다는 뜻이다.
