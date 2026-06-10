# Route-Conserving S2 Bridge HS-JEPA Team Handoff

이 파일은 팀원이 과거 실험 버전명을 몰라도 현재 HS-JEPA 패키지의 실행 결과와 논문용 주장을 한 번에 이해하도록 만든 최종 핸드오프 요약이다.

## One-Command Reproduction

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

전체 dependency까지 재생성하려면:

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py --refresh
```

## Core Mechanism

```text
public-sensitive driver action
  + route-conserving bridge action
  + S2 listener/hub constraint
  + human-state orientation diagnostic
```

축구 비유로 말하면, 이 패키지의 무회전 슛은 `target correction은 route manifold를 보존해야 한다`는 규칙이다. 세부 셀을 외운 것이 아니라, 가능한 action space에서 route를 깨지 않는 driver/bridge 궤적을 고른다.

## Generated Submission Roles

| Role | File | Upload-safe | Changed cells |
| --- | --- | ---: | ---: |
| `competition_primary` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` | `True` | `82` |
| `interpretable_s2_hub` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` | `True` | `68` |
| `human_state_probe` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` | `True` | `68` |

## Mechanism Evidence

| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage | Route p | S2 p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `route_conserving_objective_bridge_primary` | `-0.02457` | `-0.01090` | `0.780` | `0.615` | `0.0000` | `0.0006` |
| `s2_listener_bridge_interpretable` | `-0.02696` | `-0.01082` | `1.000` | `0.615` | `0.0000` | `0.0000` |

자동 validator가 확인한 핵심 수치:

- Primary route z-score: `-9.66`
- S2 listener route z-score: `-9.46`
- S2 listener usage: `1.000` vs null `0.615`
- Package validation passed: `True`
- Architecture readiness: `paper_ready_with_boundary` (`7/7` gates)

## Paper Claim

강하게 주장할 수 있는 내용:

```text
HS-JEPA reframes multi-label sleep prediction as sparse row-target action decoding.
For objective sleep-stage targets, the decoder should not move targets independently.
It should pair public-sensitive driver actions with route-conserving bridge actions.
S2 emerges as the listener/hub in this route-conserving decoder.
Human-state representation is useful as an orientation diagnostic, not as a complete row-assignment solver.
```

## Competition Use

제출 슬롯이 있다면 우선순위는 다음이다.

1. `competition_primary`: 성능 중심 Route-Conserving Objective Bridge
2. `interpretable_s2_hub`: 논문 설명력이 가장 강한 S2 Listener Bridge
3. `human_state_probe`: OG human-state orientation diagnostic

## Reproducibility Contract

이 패키지는 입력을 다음처럼 분리해서 기록한다.

```text
OG raw data != public-LB sensor != generated action artifact
```

계약 문서:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md
```

## Boundary

이 패키지가 증명하지 않는 것:

- private leaderboard safety
- OG human-state encoder 단독으로 row-target assignment 해결
- S2가 모든 수면 생리학적 factor의 중심이라는 주장

정확한 결론은 더 좁고 강하다.

```text
Given a public-sensitive action field, route conservation plus S2 listener usage selects a statistically unusual and interpretable correction path.
```

## Architecture Readiness Report

논문/팀 공유용 gate 판정:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md
```

## Paper Method Packet

논문 초안/발표에 바로 옮길 수 있는 method packet:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md
```
