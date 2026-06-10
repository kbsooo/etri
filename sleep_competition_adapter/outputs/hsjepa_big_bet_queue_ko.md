# HS-JEPA Big-Bet Queue

이 문서는 0.0001 개선용 조정이 아니라 HS-JEPA의 core/adaptor 구조를 바꿀 수 있는 큰 실험만 남긴다.

| Big bet | Worldview | Adapter move | Expected LB delta if true | Kill criterion |
| --- | --- | --- | ---: | --- |
| `OG-only Human-State Assignment Teacher` | The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. | Train a row-target support teacher from OG personal/cohort/time masks, then feed it into the existing invariant decoder. | `-0.003` | Cell orientation remains high but row assignment stays near random under subject/time stress. |
| `Listener-Invariant Contrastive Decoder` | A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. | Score candidate row-target actions by listener gain minus route-energy toxicity under random feasible nulls. | `-0.002` | Listener gain and invariant energy remain anti-correlated on strong candidates. |
| `Private-Safe Toxicity Field` | The plateau comes from actions that help public-like rows but poison private-like rows. | Use failed public sensors, null bundles, and cohort/time stress to learn a toxicity veto before submission packaging. | `-0.0015` | Toxicity score only recovers known public failures and does not separate local nulls. |
| `Cross-Listener Human-State Transport` | Subjective Q and objective S labels are different listeners of one human state, not separate tasks. | Move actions only when Q-listener and S-listener state transitions are mutually consistent. | `-0.001` | Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge. |

## 우선순위

1. `OG-only Human-State Assignment Teacher`: 성공하면 HS-JEPA의 범용성이 가장 크게 올라간다.
2. `Listener-Invariant Contrastive Decoder`: 현재 S2 bridge를 일반 action-health decoder로 확장한다.
3. `Private-Safe Toxicity Field`: public-specific gain의 private risk를 줄이는 방향이다.
