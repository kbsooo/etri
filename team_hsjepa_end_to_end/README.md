# Team HS-JEPA End-to-End Package

이 폴더는 이전 실험 버전명을 모르는 팀원이 봐도 HS-JEPA의 핵심 아이디어와 제출 후보를 재현할 수 있도록 만든 팀 공유용 패키지다.

## 핵심 컨셉

축구 비유로 말하면, 지금까지 우리는 수많은 슛을 차면서 어느 방향이 막히는지 배웠다.

이 폴더의 목적은 그 암묵지를 그대로 나열하는 것이 아니라, 하나의 재현 가능한 슈팅 기술로 정리하는 것이다.

현재 가장 강한 기술 이름:

```text
Route-Conserving S2 Bridge HS-JEPA
```

## 한 줄 설명

수면 단계 target을 하나씩 독립적으로 고치지 않고, public-sensitive driver correction을 찾은 뒤 S-stage route manifold를 보존하는 bridge correction을 함께 붙인다. 이때 S2는 objective sleep-stage route에서 가장 중요한 listener/hub로 해석한다.

## 왜 이게 단순 trial-and-error가 아닌가

단순 경험칙:

```text
이 파일은 올랐다.
저 파일은 떨어졌다.
그러니 이쪽으로 조금 더 섞자.
```

Route-Conserving S2 Bridge:

```text
1. Train label에서 Q/S target route manifold를 배운다.
2. Public sensor가 지지하는 S-stage driver action을 찾는다.
3. 같은 row에서 route energy를 낮추는 bridge target을 찾는다.
4. S2가 반복적으로 bridge/listener hub인지 확인한다.
5. Human-state representation은 row 선택기가 아니라 action orientation 진단기로 둔다.
```

즉 핵심은 “어디로 조금 더 찰까”가 아니라:

```text
target correction은 route manifold를 보존해야 한다.
```

라는 하나의 규칙이다.

## 실행

루트 디렉토리에서:

```bash
python3 team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py
```

기존 산출물이 없거나 전체 재생성이 필요하면:

```bash
python3 team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py --refresh
```

## 생성물

출력 디렉토리:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/
```

주요 파일:

- `route_conserving_s2_bridge_package.json`
- `route_conserving_s2_bridge_evidence_table.csv`
- `submission_team_hsjepa_route_conserving_objective_bridge_primary_*_uploadsafe.csv`
- `submission_team_hsjepa_s2_listener_bridge_interpretable_*_uploadsafe.csv`
- `submission_team_hsjepa_human_state_gated_s2_bridge_probe_*_uploadsafe.csv`

root에도 같은 submission 파일을 복사한다.

## 세 후보의 역할

| 역할 | 의미 |
| --- | --- |
| `competition_primary` | 성능 중심. objective-stage driver/bridge를 가장 강하게 건다. |
| `interpretable_s2_hub` | 논문 설명 중심. S2 listener/hub 가설이 가장 선명하다. |
| `human_state_probe` | human-state가 action orientation을 설명하는지 보는 진단 후보. |

## 논문에서의 핵심 주장

HS-JEPA는 label을 직접 예측하는 모델이 아니다.

```text
Human-state representation
  -> target listener
  -> row-target assignment
  -> route-conserving action decoder
```

로 문제를 분해한다.

이번 패키지의 가장 중요한 기여는 `route-conserving action decoder`다.

> 수면 단계 target의 correction은 독립적인 logit move가 아니라, route manifold를 보존하는 driver/bridge action이어야 한다.

## 대회 측면에서의 현재 위치

현재 알려진 최고 public LB:

```text
submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv
0.5677475939
```

이 패키지는 이 점수를 이미 낸 암묵지를 버리지 않는다.
대신 그 암묵지를 다음 구조로 재해석한다.

```text
public-sensitive action field
  + route conservation
  + S2 listener/hub
  + human-state diagnostic
```

즉 대회 성능 자산과 논문 아이디어를 분리하지 않고, 하나의 end-to-end 설명 가능한 구조로 묶는다.
