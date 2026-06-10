# Listener-Invariant Contrastive Probe

이 프로브는 listener responsibility와 route-invariant safety가 같은 action bundle을 가리키는지 확인한다.

## Verdict

- Status: `listener_invariant_decoder_not_ready`
- Mean listener-route Spearman: `-0.0313`
- Mean contrastive overlap with existing decoder: `0.2152`
- Mean high-listener/low-route conflict rate: `0.0719`

Listener responsibility and invariant safety are not sufficiently aligned; use this as a diagnostic before making new submissions.

## Metrics

| Probe | Listener-route rho | Existing overlap | Conflict rate | Selected listener | Contrastive listener |
| --- | ---: | ---: | ---: | ---: | ---: |
| `stagebridge` | `-0.0313` | `0.1951` | `0.0719` | `0.4652` | `0.6342` |
| `s2hub` | `-0.0313` | `0.2353` | `0.0719` | `0.4578` | `0.6303` |

## Boundary

- 이 프로브는 새 submission을 만들지 않는다.
- 목적은 action-health decoder의 다음 big-bet이 살아 있는지 확인하는 것이다.
- conflict가 높으면 listener score만 믿는 decoder는 public/private 모두에서 위험하다.
