# HS-JEPA Big-Bet Queue

이 문서는 0.0001 개선용 조정이 아니라 HS-JEPA의 core/adaptor 구조를 바꿀 수 있는 큰 실험만 남긴다.

| Big bet | Worldview | Adapter move | Latest probe | Expected LB delta if true | Kill criterion |
| --- | --- | --- | --- | ---: | --- |
| `OG-only Human-State Assignment Teacher` | The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. | Train a row-target support teacher from OG personal/cohort/time masks, then feed it into the existing invariant decoder. | `portable_row_support_sensor_alive_partial` | `-0.003` | Masked row-support keeps failing subject/date/order stress or cannot be converted into safe row-target actions. |
| `Masked Row-Support Action Decoder` | The masked row-support representation can choose which route-conserving S2/stage bundles are safe enough to move. | Gate route-conserving bridge bundles by transferred row-support and factorized broad/hard-world toxicity. | `row_support_action_decoder_alive_with_route_tradeoff` | `-0.002` | Public LB worsens or route/null stress remains weak after increasing row-support selectivity. |
| `Route-Frontier Action Decoder` | The action decoder should select route-manifold frontier moves first, then check row-support and toxicity. | Choose public-selected and open-candidate route-frontier bundles that beat broad and matched nulls. | `route_frontier_action_decoder_alive_with_matched_boundary` | `-0.0025` | Public LB worsens or matched-null frontier score fails after larger candidate pools are used. |
| `Listener-Invariant Contrastive Decoder` | A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. | Score candidate row-target actions by listener gain minus route-energy toxicity under random feasible nulls. | `listener_invariant_decoder_not_ready` | `-0.002` | Listener gain and invariant energy remain anti-correlated on strong candidates. |
| `Private-Safe Toxicity Field` | The plateau comes from actions that help public-like rows but poison private-like rows. | Use failed public sensors, null bundles, and cohort/time stress to learn a toxicity veto before submission packaging. | `toxicity_field_promising_with_hardworld_gap` | `-0.0015` | Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls. |
| `Hard-World Mixture Toxicity Decoder` | H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized. | Replace scalar toxicity with a two-head broad-public/hard-world safety gate before row-target assignment. | `hardworld_mixture_factorization_required` | `-0.0025` | Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching. |
| `Cross-Listener Human-State Transport` | Subjective Q and objective S labels are different listeners of one human state, not separate tasks. | Move actions only when Q-listener and S-listener state transitions are mutually consistent. | `not_run` | `-0.001` | Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge. |

## 우선순위

1. `OG-only Human-State Assignment Teacher`: 성공하면 HS-JEPA의 범용성이 가장 크게 올라간다.
2. `Hard-World Mixture Toxicity Decoder`: H088류 hard-world 독성을 broad toxicity와 분리한다.
3. `Listener-Invariant Contrastive Decoder`: 현재 S2 bridge를 일반 action-health decoder로 확장한다.
4. `Private-Safe Toxicity Field`: public-specific gain의 private risk를 줄이는 방향이다.
