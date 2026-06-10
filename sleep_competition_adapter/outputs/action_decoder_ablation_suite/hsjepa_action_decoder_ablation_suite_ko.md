# HS-JEPA Action Decoder Ablation Suite

이 문서는 HS-JEPA sleep adapter의 action decoder 후보들을 같은 좌표계에서 비교한다. 목적은 점수 예측이 아니라, 어떤 모듈이 현재 evidence를 들고 있는지 분해하는 것이다.

## Verdict

- Status: `action_decoder_ablation_ready_route_frontier_leads`
- Recommended LB sensor: `route_frontier.s2_route_frontier` -> `submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv`
- Open big-bet sensor: `route_frontier.open_route_frontier` -> `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv`
- Reason: The suite ranks action decoders by route-null survival, toxicity safety, upload safety, and action size. It is a submission-slot prioritizer, not a public-LB predictor.

## Decoder Ranking

| Rank | Family | Variant | Changed | Route z | Matched score z | Safety z | Upload | Priority | File |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1` | `route_frontier` | `s2_route_frontier` | `20` | `2.8238` | `3.3124` | `2.5617` | `True` | `1.1178` | `submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv` |
| `2` | `route_frontier` | `seed_route_frontier` | `20` | `2.6317` | `3.6235` | `2.1296` | `True` | `1.0720` | `submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv` |
| `3` | `route_frontier` | `open_route_frontier` | `20` | `2.4923` | `3.0832` | `2.1707` | `True` | `1.0545` | `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv` |
| `4` | `route_toxicity_fusion` | `s2_driver_safe_route_fusion` | `20` | `2.5212` | `3.3339` | `1.4350` | `True` | `0.9860` | `submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv` |
| `5` | `route_toxicity_fusion` | `seed_driver_safe_route_fusion` | `20` | `1.9565` | `4.0408` | `1.1376` | `True` | `0.8784` | `submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv` |
| `6` | `route_toxicity_fusion` | `open_driver_safe_route_fusion` | `20` | `1.2492` | `1.8707` | `1.1862` | `True` | `0.6124` | `submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv` |
| `7` | `factorized_toxicity` | `dual_safe_expansion` | `114` | `n/a` | `n/a` | `13.6669` | `True` | `0.5800` | `submission_hsjepa_factorized_toxicity_decoder_dual_safe_expansion_23b6de1e_uploadsafe.csv` |
| `8` | `factorized_toxicity` | `teacher_dual_head` | `94` | `n/a` | `n/a` | `12.0672` | `True` | `0.5800` | `submission_hsjepa_factorized_toxicity_decoder_teacher_dual_head_2a3c5d2d_uploadsafe.csv` |
| `9` | `route_toxicity_fusion` | `seed_route_toxicity_fusion` | `8` | `-0.0541` | `0.0002` | `0.0000` | `True` | `0.2890` | `submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv` |
| `10` | `route_toxicity_fusion` | `s2_route_toxicity_fusion` | `8` | `-0.0636` | `0.0002` | `0.0000` | `True` | `0.2881` | `submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv` |
| `11` | `route_toxicity_fusion` | `open_route_toxicity_fusion` | `4` | `-0.1674` | `0.0000` | `0.0002` | `True` | `0.2714` | `submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv` |
| `12` | `row_support_strict` | `strict_route_support_gate` | `4` | `-0.5097` | `2.6873` | `3.1001` | `True` | `0.2635` | `submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv` |
| `13` | `row_support_strict` | `exploratory_route_support_gate` | `34` | `-1.0165` | `1.3787` | `3.6437` | `True` | `0.2098` | `submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv` |

## Module Ablation Findings

| Claim | Status | Evidence | Next test |
| --- | --- | --- | --- |
| Support-first decoding is not the full HS-JEPA action rule. | `survived_as_partial_module` | Best row-support route_z=-0.5097, while best route-frontier route_z=2.8238. | Submit route-frontier before expanding support-first amplitudes. |
| Invariant route energy is currently the sharper action-ordering signal. | `alive` | Top ablation row is route_frontier.s2_route_frontier with priority 1.1178 and matched_score_z=3.3124. | Use route-frontier as the next LB sensor; interpret failure as public/private toxicity dominance. |
| Factorized action-health is necessary but not sufficient. | `alive_with_route_gap` | Best factorized decoder safety_z=13.6669, route boundary=route_not_claimed. | Do not ship factorized toxicity alone unless route-preserving assignment is added. |
| Route-first and toxicity-first are not alternatives; they compose into a decoder order. | `alive` | Best fusion row is s2_driver_safe_route_fusion with route_z=2.5212 and matched_score_z=3.3339. | Use route-toxicity fusion as the next adapter LB sensor if it outranks plain route-frontier. |
| Open candidate route frontier is a true big-bet boundary. | `high_information_if_submitted` | The open-route variant is upload-safe and route-supported locally, but it is outside the selected public seed set. | If seed-route fails but open-route wins, the public-selected candidate pool was too narrow. |

## How To Read This

- route-frontier가 이기면, HS-JEPA의 병목은 latent 발견보다 action ordering에 가깝다.
- route-toxicity fusion이 이기면, action ordering 다음 병목은 factorized action-health gate였다는 뜻이다.
- factorized toxicity가 이기면, public/private toxicity field가 route보다 강한 병목이다.
- row-support strict가 이기면, masked row-support representation이 action-grade decoder로 번역되기 시작한 것이다.
- open-route가 public에서 이기면, 기존 public-selected seed 후보 공간 자체가 좁았다는 큰 발견이다.
