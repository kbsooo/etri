# Row-Support Strict Action Decoder

이 실험은 masked row-support representation을 실제 row-target action으로 번역할 수 있는지 보는 adapter-side big bet이다.

## Verdict

- Status: `row_support_action_decoder_alive_with_route_tradeoff`
- Recommended variant: `exploratory_route_support_gate`
- Reason: The exploratory variant moves enough cells to be LB-informative and is strongly safer than local feasible nulls, but route-gain is not superior to null, so it is a big-bet candidate rather than a safe release candidate.

## Worldview

좋은 action은 세 조건을 동시에 만족해야 한다.

1. row-support가 높은 row여야 한다.
2. route/S2 bridge invariant를 깨지 않아야 한다.
3. broad-public / hard-world toxicity가 낮아야 한다.

## Generated Candidates

| Variant | File | Bundles | Changed cells | Row support | Route gain | Joint safety | Upload-safe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `strict_route_support_gate` | `submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv` | `2` | `4` | `0.8840` | `0.0222` | `0.7949` | `True` |
| `exploratory_route_support_gate` | `submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv` | `17` | `34` | `0.8306` | `0.0221` | `0.5935` | `True` |

## Local Null Stress

| Variant | Support z | Route z | Safety z | Combined z |
| --- | ---: | ---: | ---: | ---: |
| `strict_route_support_gate` | `0.56` | `-0.51` | `3.10` | `2.69` |
| `exploratory_route_support_gate` | `0.12` | `-1.02` | `3.64` | `1.38` |

## Interpretation

- 좋아지면 masked row-support가 action-health decoder로 승격될 수 있다는 신호다.
- 나빠지면 row-support representation은 살아있지만, route/toxicity 조건만으로는 아직 action assignment가 부족하다는 뜻이다.
- 이 실험은 HS-JEPA core가 아니라 sleep competition adapter의 row-target action solver다.
