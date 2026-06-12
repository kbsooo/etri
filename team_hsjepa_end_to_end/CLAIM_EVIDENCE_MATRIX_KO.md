# HS-JEPA Claim-Evidence Matrix

이 문서는 팀원이 이전 실험 버전명을 몰라도, Route-Conserving S2 Bridge HS-JEPA가 어떤 주장을 하고 어떤 증거로 버티는지 한 번에 확인하기 위한 매트릭스다.

핵심 메시지는 다음이다.

```text
HS-JEPA의 현재 가장 강한 "무회전 슛"은
public-sensitive target을 독립적으로 움직이는 것이 아니라,
수면-stage route manifold를 보존하는 S2-centered bridge action으로 번역하는 것이다.
```

## 1. Claim-Evidence Matrix

| 주장 | 증거 | 반증 가능성 | 현재 상태 |
| --- | --- | --- | --- |
| 수면-stage correction은 독립 target move가 아니라 route-conserving bridge action이어야 한다. | selected bridge의 route delta가 random feasible null보다 훨씬 낮음. Primary `-0.02457` vs null `-0.01090`, S2 bridge `-0.02696` vs null `-0.01082`. | 같은 후보 pool에서 random/null action도 같은 수준의 route delta를 보이면 죽는다. | 살아 있음 |
| S2는 단순 target이 아니라 public-sensitive listener/hub다. | S2 Listener Bridge의 S2 사용률 `1.000`, random null `0.615`, p-value `0.0000`. | 다른 S target도 같은 stress audit에서 동일하게 hub 역할을 하면 S2 특수성은 약해진다. | 강하게 살아 있음 |
| Human-state encoder는 row assignment solver가 아니라 action orientation diagnostic이다. | cell-level OOF AUC는 높지만 row-level AUC는 약함. Target-listener route lift public LB `0.5680255019`로 current best `0.5677269444`보다 악화. | OG human-state만으로 row-target support를 안정적으로 복원하면 역할 정의가 바뀐다. | 역할이 좁아졌지만 살아 있음 |
| Active silence는 action-health의 일부다. | frontier active-silence positive-path가 public LB `0.5677269444`로 새 best를 만들었다. | active-silence 계열의 다른 방향이 모두 악화되고, 새 best가 단순 확률 smoothing으로 설명되면 약해진다. | 살아 있으나 anchor-local |
| HS-JEPA는 단순 blend가 아니라 action field architecture다. | package가 `Human-State Encoder -> Target Listener -> Row-Target Assignment -> Route-Conserving Decoder`로 분리되고, 각 모듈의 실패/성공 경계가 기록됨. | 최종 후보가 단순 alpha/mix만으로 같은 효과를 내면 architecture 기여가 약해진다. | 살아 있음 |
| 현재 패키지는 team-facing end-to-end로 재현 가능하다. | wrapper, audit, validation script가 같은 산출물을 생성/검증함. | clean checkout에서 명령이 실패하거나 upload-safe 검증이 깨지면 죽는다. | 검증 필요 시 `validate_route_conserving_s2_bridge_package.py` 실행 |

## 2. 핵심 검증 명령

루트 디렉토리에서 순서대로 실행한다.

```bash
python3 team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py
python3 team_hsjepa_end_to_end/audit_route_conserving_s2_bridge.py
python3 team_hsjepa_end_to_end/validate_route_conserving_s2_bridge_package.py
```

검증 리포트:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.md
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.json
```

## 3. 논문에서 강하게 말할 수 있는 것

강하게 말할 수 있는 주장:

```text
Multi-label sleep prediction can be reframed as sparse row-target action decoding.
For objective sleep-stage targets, independent correction is unsafe; a route-conserving bridge decoder produces a statistically unusual and interpretable action path.
S2 emerges as a listener/hub in this decoder, while human-state representation provides action orientation rather than full support assignment.
```

한국어로는:

```text
우리는 수면 생활 로그를 바로 7개 label로 예측하지 않고,
숨은 human-state와 row-target action field를 분리해 복원한다.
특히 objective sleep-stage correction은 독립적인 확률 조정이 아니라
route manifold를 보존하는 S2-centered bridge action으로 번역되어야 한다.
```

## 4. 조심해서 말해야 하는 것

아직 과장하면 안 되는 주장:

- HS-JEPA가 OG 데이터만으로 current best를 완전히 재현한다.
- S2가 모든 수면 생리학적 구조의 중심 factor다.
- route-conserving decoder가 private leaderboard에서도 반드시 안전하다.
- human-state encoder 하나가 row-target assignment를 해결한다.

현재 더 정확한 표현:

```text
HS-JEPA는 human-state representation, listener/assignment solver, route-conserving action decoder를 분리한다.
현재 가장 강한 성능 모듈은 competition-specific public sensor를 포함하지만,
decoder의 route-conservation/S2-hub 성질은 후보 공간 대비 통계적으로 검증된다.
```

추가로, 2026-06-12 기준 current best는 `frontier active-silence positive-path`의 `0.5677269444`다. 다만 이 결과는 큰 구조 발견이라기보다 row-state frontier 주변의 local continuation이다. 0.53급 도약을 주장하려면 다음 단계에서 anchor-free state transport가 필요하다.

## 5. 팀원에게 보여줄 최소 파일

처음 보는 팀원에게는 아래 순서로 보여주면 된다.

1. `team_hsjepa_end_to_end/README.md`
2. `team_hsjepa_end_to_end/SEMANTIC_NAMING_GUIDE_KO.md`
3. `team_hsjepa_end_to_end/ROUTE_CONSERVING_S2_BRIDGE_KO.md`
4. `team_hsjepa_end_to_end/CLAIM_EVIDENCE_MATRIX_KO.md`
5. `team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py`
6. `team_hsjepa_end_to_end/audit_route_conserving_s2_bridge.py`
7. `team_hsjepa_end_to_end/validate_route_conserving_s2_bridge_package.py`

이 순서가 중요한 이유는, 먼저 아이디어를 설명하고 그 다음에 코드가 그 아이디어를 어떻게 검증하는지 보여주기 때문이다.
