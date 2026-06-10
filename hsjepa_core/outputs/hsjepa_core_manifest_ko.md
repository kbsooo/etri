# HS-JEPA Core Architecture Manifest

이 문서는 HS-JEPA의 재사용 가능한 core를 정의한다. 여기에는 특정 대회 target 이름, public LB, submission 파일명이 들어가지 않는다.

## Core Claim

HS-JEPA is a general architecture for human-understanding prediction: predict hidden human-state, listener responsibility, action-health, and invariant-preserving action representations before making bounded outputs.

## Core Equation

```text
partial_human_context -> hidden_human_state -> listener_responsibility -> action_health -> invariant_preserving_decoder -> anti_shortcut_validation
```

## Modules

| Module | Purpose | Output | Failure if removed |
| --- | --- | --- | --- |
| `Human-State Context Encoder` | Encode partial person, cohort, time, routine, social, and sensor context into a hidden human-state field. | hidden human-state embedding, state uncertainty, context coverage mask | The model collapses into direct label prior fitting or local feature heuristics. |
| `Masked State Predictor` | Predict unobserved state/listener representations from visible context without reconstructing raw inputs. | predicted hidden state, prediction energy | The representation no longer proves that it understands hidden human structure. |
| `Listener Responsibility` | Treat labels, sensors, surveys, or outcomes as listeners that react differently to the same human state. | listener responsibility distribution, listener-specific uncertainty | The architecture becomes a flat multi-label classifier with no explanation of which outcome should react. |
| `Action-Health Decoder` | Decide whether a latent signal is healthy enough to translate into an output action. | action-health score, toxicity/risk flag, bounded action amplitude | Good-looking latent signals become unsafe output moves and overfit shortcut regions. |
| `Invariant Energy` | Score whether an action preserves the behavioral, physiological, temporal, or semantic manifold of the domain. | invariant energy delta, veto decision | The model can improve a local listener while breaking the global human-state manifold. |
| `Anti-Shortcut Validation` | Stress-test the representation and action field against nulls, cohort shifts, time shifts, and shortcut sensors. | shortcut verdict, collapse verdict, portability warning | A lucky split or public-only shortcut can be mistaken for human-state understanding. |

## Portability Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| `no_competition_target_names` | `PASS` | Core contracts use generic listeners/outcomes instead of dataset-specific target names. |
| `no_public_sensor_dependency` | `PASS` | Core contracts do not require leaderboard observations or submission files. |
| `adapter_boundary_required` | `PASS` | Dataset-specific invariants and output schema must be supplied by an adapter. |
| `ablation_contract_defined` | `PASS` | Each core module has a removal test and expected failure mode. |
| `human_understanding_scope` | `PASS` | The core predicts hidden state/listener/action representations before final labels. |

## Adapter가 책임지는 것

- dataset schema
- domain invariant definition
- listener/output names
- deployment metric
- submission or serving format

## Core에 들어오면 안 되는 것

- public leaderboard observations
- dataset-specific target names
- submission file names
- manual row ids
- private labels
