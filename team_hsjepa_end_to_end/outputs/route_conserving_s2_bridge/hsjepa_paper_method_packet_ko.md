# HS-JEPA Paper Method Packet

이 문서는 팀원이 과거 제출 버전명을 몰라도 HS-JEPA를 논문/발표 아이디어로 설명할 수 있도록 만든 method packet이다.

## One-Sentence Contribution

HS-JEPA is a human-understanding architecture that predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations before producing bounded predictions; the Route-Conserving S2 Bridge is the sleep-log competition case study.

## Abstract Draft

우리는 인간 생활 로그 예측을 label column에 대한 직접 분류 문제가 아니라, 숨은 인간 생활 상태가 여러 listener와 action으로 드러나는 representation prediction 문제로 재정의한다. 제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, listener responsibility, action-health, invariant energy를 분리한다. 수면 로그 대회 case study에서는 이 일반 구조가 sparse row-target action decoding으로 구현되며, objective sleep-stage target에서는 public-sensitive driver action을 단독으로 적용하지 않고 train label에서 학습한 Q/S route manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 case-study decoder는 기존 public-equation 이전 최고 public LB 0.5761589494에서 현재 최고 0.5677475939까지 -0.0084113555 개선된 signal을 설명하며, 선택된 bridge는 random feasible bundle 대비 route energy를 -0.02457 vs -0.01090로 낮춘다. 또한 S2는 listener/hub로 반복 등장한다 (1.000 vs null 0.615). Human-state latent는 cell-level orientation AUC 0.775를 보이지만 row assignment AUC는 0.545에 그쳐, encoder와 assignment decoder를 분리해야 함을 보여준다.

## Method

HS-JEPA는 일반적으로 다음 다섯 계층으로 구성된다.

1. Human-State Context Encoder: 개인 baseline, cohort deviation, 시간/사회적 루틴, sensor state를 latent context로 변환한다.
2. Masked State Predictor: partial context에서 보이지 않는 human-state 또는 listener representation을 예측한다.
3. Listener Responsibility: label, sensor, survey, behavior outcome을 hidden state를 듣는 listener로 해석한다.
4. Action-Health Decoder: latent가 실제 output move로 번역되어도 안전한지 판단한다.
5. Invariant-Preserving Decoder: action 이후에도 행동/생리/시간/의미 manifold가 깨지지 않도록 bounded output을 만든다.

이번 수면 대회에서는 3-5번이 row-target assignment, public-sensor action teacher, Q/S route energy, S2 listener bridge로 구현되었다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 listener/action/invariant decoder를 분리한다는 점이다.

## Generality

HS-JEPA general architecture != Route-Conserving S2 Bridge competition case study

일반 HS-JEPA에서 재사용되는 것은 다음 구조다.

```text
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation
```

이번 대회의 S2/public-sensor 구조는 이 일반 구조의 case study다.

- Generality status: `general_architecture_separated_with_case_boundary`
- Portability checks: `5/6`
- Nonblocking boundaries: `remaining_generality_gap`

가장 중요한 남은 과제는 public-sensor row-target assignment teacher를 OG-only personal/cohort/time human-state teacher로 교체하는 것이다.

## Algorithm

```text
Algorithm: HS-JEPA General Pattern with Sleep-Log Case Decoder

Input: human lifestyle/context logs, listener labels or sensor outcomes, optional deployment sensor, current prediction.
Output: bounded prediction/action field with invariant and shortcut checks.

1. Encode personal, cohort, time, routine, social, and sensor context into a human-state representation.
2. Predict masked listener/action representations from partial human context.
3. Estimate listener responsibility: which outcomes should react to the hidden state.
4. Estimate action-health: whether the latent signal is safe to translate into output movement.
5. Learn an invariant energy over valid output/action manifolds.
6. Decode bounded actions that improve listener fit while preserving the invariant.
7. Reject shortcuts with cohort/time/group/null stress tests.
8. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.
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
