# HS-JEPA Paper Method Packet

이 문서는 팀원이 과거 제출 버전명을 몰라도 HS-JEPA를 논문/발표 아이디어로 설명할 수 있도록 만든 method packet이다.

## One-Sentence Contribution

HS-JEPA Core is a human-understanding architecture that predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations before producing bounded predictions; the Sleep Competition Adapter instantiates that core as a Route-Conserving S2 Bridge case study.

## Abstract Draft

우리는 인간 생활 로그 예측을 label column에 대한 직접 분류 문제가 아니라, 숨은 인간 생활 상태가 여러 listener와 action으로 드러나는 representation prediction 문제로 재정의한다. 제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, listener responsibility, action-health, invariant energy를 분리한다. 수면 로그 대회 case study에서는 이 일반 구조가 sparse row-target action decoding으로 구현되며, objective sleep-stage target에서는 public-sensitive driver action을 단독으로 적용하지 않고 train label에서 학습한 Q/S route manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 case-study decoder는 기존 public-equation 이전 최고 public LB 0.5761589494에서 현재 최고 0.5677475939까지 -0.0084113555 개선된 signal을 설명하며, 선택된 bridge는 random feasible bundle 대비 route energy를 -0.02457 vs -0.01090로 낮춘다. 또한 S2는 listener/hub로 반복 등장한다 (1.000 vs null 0.615). Human-state latent는 cell-level orientation AUC 0.775를 보이지만 row assignment AUC는 0.545에 그쳐, encoder와 assignment decoder를 분리해야 함을 보여준다.

## Method

HS-JEPA는 core와 adapter를 분리한다.

Core equation:

```text
partial_human_context -> hidden_human_state -> listener_responsibility -> action_health -> invariant_preserving_decoder -> anti_shortcut_validation
```

Core modules:

1. Human-State Context Encoder: Encode partial person, cohort, time, routine, social, and sensor context into a hidden human-state field.
2. Masked State Predictor: Predict unobserved state/listener representations from visible context without reconstructing raw inputs.
3. Listener Responsibility: Treat labels, sensors, surveys, or outcomes as listeners that react differently to the same human state.
4. Action-Health Decoder: Decide whether a latent signal is healthy enough to translate into an output action.
5. Invariant Energy: Score whether an action preserves the behavioral, physiological, temporal, or semantic manifold of the domain.
6. Anti-Shortcut Validation: Stress-test the representation and action field against nulls, cohort shifts, time shifts, and shortcut sensors.

Sleep competition adapter:

This adapter converts HS-JEPA Core into a sleep-log competition system by supplying Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding.

이번 수면 대회에서는 listener가 Q1/Q2/Q3/S1/S2/S3/S4로, invariant가 Q/S route energy로, action-health가 public/private toxicity 및 feasible-bundle stress로 구현되었다. 새 hard-world probe는 broad toxicity와 H088 toxicity가 역상관될 수 있음을 보여주므로, action-health는 단일 위험 점수가 아니라 factorized energy head로 다루어야 한다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 core의 listener/action/invariant 경로를 adapter가 안전한 sparse row-target action으로 번역한다는 점이다.

## Core / Adapter Evidence

- Core status: `core_ready_for_adapter` (`5/5` gates)
- Core ablation contract: `ablation_contract_ready` (`6` ablations)
- Adapter status: `adapter_ready_with_public_sensor_boundary`
- Big-bet queue: `big_bet_queue_ready` (`5` bets)

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
- OG-only assignment probe: `og_only_assignment_replacement_not_ready`
- Pure OG row-cap2 recall: `0.0404`
- Distilled row-cap2 recall: `0.1236`
- Listener-invariant probe: `listener_invariant_decoder_not_ready`
- Listener-route Spearman: `-0.0313`
- Private-safe toxicity probe: `toxicity_field_promising_with_hardworld_gap`
- Toxicity mean LOO AUC: `0.7880`
- Toxicity worst LOO AUC: `0.3683`
- Hard-world factorization probe: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`

가장 중요한 남은 과제는 public-sensor row-target assignment teacher를 OG-only personal/cohort/time human-state teacher로 교체하고, 이미 생성된 broad-public/hard-world factorized decoder 후보가 실제 public/private score에서 action-grade decoder인지 검증하는 것이다.

## Algorithm

```text
Algorithm: HS-JEPA General Pattern with Sleep-Log Case Decoder

Input: human lifestyle/context logs, listener labels or sensor outcomes, optional deployment sensor, current prediction.
Output: bounded prediction/action field with invariant and shortcut checks.

1. Encode personal, cohort, time, routine, social, and sensor context into a human-state representation.
2. Predict masked listener/action representations from partial human context.
3. Estimate listener responsibility: which outcomes should react to the hidden state.
4. Estimate action-health: whether the latent signal is safe to translate into output movement.
5. Factorize action-health when shortcut modes are anti-correlated rather than scalar.
6. Learn an invariant energy over valid output/action manifolds.
7. Decode bounded actions that improve listener fit while preserving the invariant.
8. Reject shortcuts with cohort/time/group/null stress tests.
9. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.
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

## Big-Bet Queue

다음 큰 실험은 HS-JEPA core/adaptor 경계를 바꾸는 실험이어야 한다.

- `OG-only Human-State Assignment Teacher`: The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. Expected LB delta if true `-0.003`. Kill: Pure OG row-target recall stays near base-rate and distillation cannot recover row assignment under subject/time stress.
- `Listener-Invariant Contrastive Decoder`: A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. Expected LB delta if true `-0.002`. Kill: Listener gain and invariant energy remain anti-correlated on strong candidates.
- `Private-Safe Toxicity Field`: The plateau comes from actions that help public-like rows but poison private-like rows. Expected LB delta if true `-0.0015`. Kill: Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls.
- `Hard-World Mixture Toxicity Decoder`: H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized. Expected LB delta if true `-0.0025`. Kill: Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching.
- `Cross-Listener Human-State Transport`: Subjective Q and objective S labels are different listeners of one human state, not separate tasks. Expected LB delta if true `-0.001`. Kill: Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge.

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
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_manifest.json`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_ablation_contract.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/sleep_competition_adapter_report.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json`
