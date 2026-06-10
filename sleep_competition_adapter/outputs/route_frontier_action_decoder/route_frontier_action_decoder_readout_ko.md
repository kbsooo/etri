# Route-Frontier Action Decoder

이 실험은 row-support decoder의 약점이었던 route-gain/null 문제를 정면으로 찌른다.

## Verdict

- Status: `route_frontier_action_decoder_alive_with_matched_boundary`
- Recommended variant: `seed_route_frontier`
- Reason: The selected frontier beats broad route nulls and is upload-safe. Matched-null score remains the boundary, so this is a big-bet LB sensor rather than a default release.

## Worldview

HS-JEPA action decoder는 좋은 row를 찾는 것만으로는 부족하다. 실제 output을 움직이려면 route manifold의 frontier 위에 있는 action만 살아남아야 한다.

## Generated Candidates

| Variant | File | Bundles | Changed cells | Route gain | Route rank | Row support | Open rate | Upload-safe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `seed_route_frontier` | `submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv` | `10` | `20` | `0.0303` | `0.8027` | `0.8972` | `0.0000` | `True` |
| `s2_route_frontier` | `submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv` | `10` | `20` | `0.0310` | `0.8066` | `0.8720` | `0.0000` | `True` |
| `open_route_frontier` | `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv` | `10` | `20` | `0.0267` | `0.7486` | `0.8552` | `1.0000` | `True` |

## Null Stress

| Variant | Broad route z | Broad score z | Matched route z | Matched score z |
| --- | ---: | ---: | ---: | ---: |
| `seed_route_frontier` | `2.63` | `4.24` | `1.88` | `3.62` |
| `s2_route_frontier` | `2.82` | `3.95` | `2.19` | `3.31` |
| `open_route_frontier` | `2.49` | `2.72` | `2.30` | `3.08` |

## Interpretation

- 좋아지면 route-frontier decoder가 hidden row-support를 안전한 action field로 번역할 수 있다는 뜻이다.
- 나빠지면 route energy만으로는 public/private toxicity를 이기지 못한다는 뜻이다.
- open frontier가 좋아지면 기존 public-selected action 후보 밖에도 살아있는 route-invariant action이 있다는 큰 발견이다.
