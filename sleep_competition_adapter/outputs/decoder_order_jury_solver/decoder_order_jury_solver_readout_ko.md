# HS-JEPA Decoder-Order Jury Solver

이 실험은 route-first decoder와 route-toxicity fusion decoder가 같은 row-target action을 같은 방향으로 고르는지 본다.
단일 decoder 점수를 더 믿는 대신, 여러 decoder가 독립적으로 동의한 action만 release한다.

## Verdict

- Status: `decoder_order_jury_ready`
- Recommended LB sensor: `family_supermajority` -> `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv`
- Claim: Safe row-target assignment is a cross-decoder jury: route invariant proposes the action, factorized action-health confirms it, and only same-direction consensus is released.
- Failure interpretation: If public LB worsens, consensus is too conservative or action-health removes useful route-frontier signal.

## Ranking

| Rank | Variant | Changed | Rows | Consensus z | Cross-family z | Priority | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `1` | `family_supermajority` | `19` | `11` | `5.3987` | `5.2815` | `1.3925` | `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv` |
| `2` | `route_majority_fusion_confirmed` | `19` | `11` | `5.3987` | `5.2815` | `1.3925` | `submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv` |
| `3` | `s2_pair_consensus` | `18` | `9` | `-0.2400` | `-0.8223` | `0.2598` | `submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv` |
| `4` | `seed_pair_consensus` | `18` | `9` | `-0.3789` | `-1.0645` | `0.2018` | `submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv` |

## Interpretation

- 이 후보가 public에서 route-frontier보다 좋으면, HS-JEPA action decoder는 route-first 단독이 아니라 cross-decoder listener jury가 맞다는 뜻이다.
- 나쁘면, consensus가 너무 보수적이거나 action-health gate가 route signal을 과하게 깎았다는 뜻이다.
- 이 모듈은 HS-JEPA core가 아니라 sleep competition adapter의 row-target assignment solver다.
