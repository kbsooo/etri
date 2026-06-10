# HS-JEPA Generality Report

이 문서는 HS-JEPA를 이번 대회 전용 `S2/public sensor` 트릭이 아니라, 다른 인간 이해 로그 문제에도 가져갈 수 있는 아키텍처로 다시 분리한다.

## Core Correction

지금까지의 패키지는 너무 `Route-Conserving S2 Bridge`가 전면에 있었다. 그것은 HS-JEPA 자체가 아니라, 이 대회에서 발견된 강한 case-study decoder다.

HS-JEPA의 더 일반적인 기술은 다음이다.

```text
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation
```

축구 비유로 말하면, `S2 bridge`는 특정 경기장에서 성공한 슛 궤적이다. 일반 기술은 `상황을 읽고, 공의 회전/위험/궤적 불변성을 제어하는 방법`이어야 한다.

## General Modules

| General module | Reusable role | Not allowed to be | Current case instance |
| --- | --- | --- | --- |
| `Human-State Context Encoder` | Convert person, cohort, time, routine, social, and sensor context into a latent human-state field. | A direct label predictor disguised as a representation. | sleep/routine/cohort context plus row-order and target-context artifacts. |
| `Masked State Prediction` | Predict hidden human-state or listener representation from partial context. | Raw input reconstruction or a memorized target prior. | cell-level target/listener orientation and hidden row-target support probes. |
| `Listener Responsibility` | Treat labels, sensors, or outcomes as listeners that react differently to the same human state. | A fixed target hierarchy hard-coded from label names. | Q/S targets and S2 listener/hub behavior inside the objective-stage decoder. |
| `Action-Health Decoder` | Separate state discovery from the decision that an output should actually move. | A broad correction head that trusts every latent signal. | H088 and other negative public sensors used as toxic-action diagnostics. |
| `Invariant Energy` | Reject actions that break a learned behavioral, physiological, temporal, or semantic manifold. | A dataset-specific target name rule with no null test. | Q/S route energy and route-conserving S2 bridge stress audit. |
| `Anti-Shortcut Validation` | Use cohort/time/group/null/stress tests to detect collapse, public overfit, and shortcut action fields. | A green CV score or a single leaderboard improvement. | public-sensor ablation, feasible-bundle nulls, upload-safety gates, release checklist. |

## Competition Case Study

이번 대회 구현은 아래처럼 제한적으로 말해야 한다.

```text
HS-JEPA general architecture
  + sleep-log competition case study
  + public-sensor assignment teacher
  + Q/S route invariant
  + S2 listener bridge decoder
```

따라서 논문에서 강하게 주장할 것은 `S2가 보편적 수면 중심 target이다`가 아니다. 강한 주장은 다음이다.

```text
Human-understanding prediction should separate hidden state representation, listener responsibility, action-health, and invariant-preserving decoding.
```

## Portability Checks

| Check | Status | Evidence | Meaning |
| --- | --- | --- | --- |
| `architecture_case_separation` | `PASS` | General HS-JEPA modules are named separately from the Route-Conserving S2 Bridge case study. | S2/public sensor is an instantiation, not the architecture itself. |
| `human_understanding_scope` | `PASS` | Human-state context includes personal baseline, cohort deviation, routine/social context, and sensor state. | The architecture targets human-state interpretation before label prediction. |
| `listener_not_label` | `PASS` | Targets are described as listeners/responses to hidden state, not only as seven binary columns. | The same architecture can apply when listeners are survey answers, sensors, app usage, or health outcomes. |
| `invariant_decoder_generalized` | `PASS` | Route energy is framed as one instance of invariant energy over output/action manifolds. | Other datasets can replace Q/S route with temporal, cohort, semantic, or physiological invariants. |
| `competition_sensor_boundary` | `PASS` | Public LB sensor is explicitly marked as competition-specific assignment teacher. | Paper claims can keep the reusable architecture separate from the leaderboard-specific sensor. |
| `remaining_generality_gap` | `BOUNDARY` | OG-only assignment probe status og_only_assignment_replacement_not_ready; pure row-cap2 recall 0.0404, distilled recall 0.1236. Assignment gap status row_support_is_primary_bottleneck; portable recall 0.1063, row-oracle recall 0.6896, row-support gap 0.5832. Hidden row-support transfer status portable_row_support_sensor_alive_partial; best family portable_row_support_composite, row AUC 0.8193, cell recall 0.3289. Masked row-support objective status masked_row_support_objective_supported_with_stress_boundary; full row AUC 0.8193, cell recall 0.3289, group stress AUC 0.5584. Row-support strict action decoder status row_support_action_decoder_alive_with_route_tradeoff; recommended exploratory_route_support_gate, exploratory changed cells 34, safety z 3.6437, combined z 1.3787. | The architecture is reusable; the current strongest competition instantiation is not yet fully portable or action-grade. |

## What Transfers

- 개인 baseline과 cohort deviation을 같이 보는 방식
- label을 정답 column이 아니라 hidden state를 듣는 listener로 보는 방식
- latent를 바로 output으로 쓰지 않고 action-health decoder를 통과시키는 방식
- output correction이 domain invariant를 깨는지 energy로 검사하는 방식
- shortcut/collapse/public-overfit을 ablation과 null로 죽이는 방식

## What Does Not Transfer Directly

- `S2`라는 target 이름
- public LB sensor
- Q/S route energy의 구체적 형태
- 250 rows x 7 targets sparse support geometry

## Current Honest Claim

HS-JEPA is a human-understanding architecture that predicts hidden human-state and listener/action representations before making bounded output moves.  The Route-Conserving S2 Bridge is the sleep-log competition instantiation, not the full architecture.

## Next Generality Breakthrough

Turn the partially alive masked row-support representation into an action-grade decoder. The first strict decoder is alive as an LB-informative probe, but route-gain is not yet stronger than the null. The next portable objective should preserve teacher-transfer strength while lifting subject/date/order held-out stress and route-gain before allowing row-support to drive safe release submissions.
