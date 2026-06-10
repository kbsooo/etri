# HS-JEPA Core Ablation Contract

이 문서는 HS-JEPA를 논문/발표용 아키텍처로 주장하기 위해 반드시 죽여봐야 할 제거 실험을 정의한다.

## Purpose

Make the HS-JEPA mechanism falsifiable instead of only descriptive.

## Ablations

| Ablation | Removed module | Expected failure | Measurement |
| --- | --- | --- | --- |
| `remove_context_encoder` | `context_encoder` | listener responsibility becomes prior-heavy and cohort/time generalization weakens. | drop in listener orientation, worse stress performance under cohort/time split. |
| `remove_masked_state_prediction` | `masked_state_predictor` | representation can no longer predict hidden state under semantic masks. | masked representation prediction energy loses separation from null. |
| `remove_listener_responsibility` | `listener_responsibility` | the same latent move is applied to wrong outcomes/listeners. | target/listener action precision drops while aggregate score may look locally stable. |
| `remove_action_health` | `action_health_decoder` | unsafe latent signals are translated into overbroad output moves. | toxicity or negative-sensor alignment rises; high-energy tails worsen. |
| `remove_invariant_energy` | `invariant_energy` | local action gains break the domain manifold. | selected actions lose energy advantage versus feasible null bundles. |
| `remove_anti_shortcut_validation` | `anti_shortcut_validation` | collapse, split shortcut, or public-only behavior is overclaimed as architecture. | green score without null/stress survival is marked non-releasable. |

## Minimum Publishable Evidence

- core module removal changes downstream behavior
- invariant-energy removal loses null separation
- action-health removal increases toxic action rate
- listener removal hurts target/outcome routing
- counterfactual listener-dropout exposes at least one single-listener shortcut or validates a robust action field
- anti-shortcut validation rejects at least one tempting but false shortcut
