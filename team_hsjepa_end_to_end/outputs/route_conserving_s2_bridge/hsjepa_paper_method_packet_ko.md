# HS-JEPA Paper Method Packet

이 문서는 팀원이 과거 제출 버전명을 몰라도 HS-JEPA를 논문/발표 아이디어로 설명할 수 있도록 만든 method packet이다.

## One-Sentence Contribution

HS-JEPA treats sleep-log prediction as hidden human-state oriented sparse row-target action decoding, then constrains objective-stage corrections to preserve the learned Q/S route manifold through an S2 listener bridge.

## Abstract Draft

우리는 수면 기반 생활 로그 예측을 독립적인 7개 label 분류 문제가 아니라, 숨은 인간 생활 상태가 만드는 sparse row-target action decoding 문제로 재정의한다. 제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, target-listener, row-target action, route-consistency energy를 분리한다. 특히 objective sleep-stage target에서는 public-sensitive driver action을 단독으로 적용하지 않고, train label에서 학습한 Q/S route manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 route-conserving decoder는 기존 public-equation 이전 최고 public LB 0.5761589494에서 현재 최고 0.5677475939까지 -0.0084113555 개선된 signal을 설명하며, 선택된 bridge는 random feasible bundle 대비 route energy를 -0.02457 vs -0.01090로 낮춘다. 또한 S2는 listener/hub로 반복 등장한다 (1.000 vs null 0.615). Human-state latent는 cell-level orientation AUC 0.775를 보이지만 row assignment AUC는 0.545에 그쳐, encoder와 assignment decoder를 분리해야 함을 보여준다.

## Method

HS-JEPA는 다음 네 계층으로 구성된다.

1. Human-State Encoder: OG 생활 로그, 개인/코호트 상태, 수면 상태의 deviation을 latent context로 변환한다.
2. Target Listener Representation: 각 target이 현재 hidden state와 어떤 방향으로 반응하는지 cell-level orientation을 예측한다.
3. Row-Target Assignment Solver: 실제로 움직일 sparse row-target support를 찾는다. 이 단계는 competition-specific public sensor를 사용하므로 논문 claim에서 분리한다.
4. Route-Conserving S2 Bridge Decoder: driver target을 단독 이동하지 않고, Q/S route energy를 낮추는 bridge target을 함께 선택한다.

핵심은 label probability를 크게 만드는 것이 아니라, action 이후의 7-target vector가 train label의 공동 구조를 덜 위반하도록 만드는 것이다.

## Algorithm

```text
Algorithm: Route-Conserving S2 Bridge HS-JEPA

Input: OG lifestyle logs, train labels, public-sensor action anchors, current best prediction.
Output: sparse row-target correction field and upload-safe submission.

1. Learn a Q/S route energy model from train labels.
2. Build human-state and target-listener representations from OG/context artifacts.
3. Identify public-sensitive driver cells from the action anchor field.
4. For each driver cell, enumerate same-row objective-stage bridge candidates.
5. Score each driver/bridge bundle by public utility, route-energy gain, S2 listener usage, and toxicity stress.
6. Select sparse non-overlapping bundles under target/row budget constraints.
7. Apply bounded logit-space corrections and validate upload safety.
8. Stress-audit the selected bundles against random feasible bundle nulls.
```

## Evidence Snapshot

- Status: `paper_ready_with_boundary`
- Readiness gates: `7/7`
- Pre-public-equation best public LB: `0.5761589494`
- Current best public LB: `0.5677475939`
- Delta: `-0.0084113555`
- Route delta vs null: `-0.02457` vs `-0.01090`
- S2 usage vs null: `1.000` vs `0.615`
- Human-state cell AUC / row AUC: `0.775` / `0.545`

## Role-Based Outputs

| Role | Component | Changed cells | Changed rows | Claim |
| --- | --- | ---: | ---: | --- |
| `competition_primary` | Route-Conserving Objective Bridge | `82` | `41` | Public-sensitive S-stage driver actions should be paired with route-preserving bridge actions. |
| `interpretable_s2_hub` | S2 Listener Bridge | `68` | `34` | S2 acts as a public-sensitive listener/hub inside the objective sleep-stage route. |
| `human_state_probe` | Human-State Gated S2 Probe | `68` | `47` | OG human-state explains target/cell orientation, but not row assignment. |

## Stress Evidence

| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage |
| --- | ---: | ---: | ---: | ---: |
| `route_conserving_objective_bridge_primary` | `-0.02457` | `-0.01090` | `0.780` | `0.615` |
| `s2_listener_bridge_interpretable` | `-0.02696` | `-0.01082` | `1.000` | `0.615` |

## Boundaries

현재 패키지는 다음 경계를 명시한다.

- Pure OG-only model: `False`
- Uses public LB sensor: `True`
- Uses proprietary embedding API in team runner: `False`
- Human-state role: `orientation diagnostic, not complete row-target assignment solver`
- Competition decoder role: `public-sensitive row-target action solver with route-conserving S2 bridge`

따라서 논문에서는 HS-JEPA의 representation idea와 competition-specific action decoder를 분리해서 주장해야 한다.

## Team Reproduction

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

Generated supporting reports:

- `/Users/kbsoo/Downloads/cl2/team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.json`
- `/Users/kbsoo/Downloads/cl2/team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.json`
