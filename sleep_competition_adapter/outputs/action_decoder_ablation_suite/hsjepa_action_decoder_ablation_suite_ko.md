# HS-JEPA Action Decoder Ablation Suite

이 문서는 HS-JEPA sleep adapter의 action decoder 후보들을 같은 좌표계에서 비교한다. 목적은 점수 예측이 아니라, 어떤 모듈이 현재 evidence를 들고 있는지 분해하는 것이다.

## Verdict

- Status: `action_decoder_ablation_ready_decoder_jury_leads`
- Recommended LB sensor: `decoder_order_jury.family_supermajority` -> `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv`
- Open big-bet sensor: `route_frontier.open_route_frontier` -> `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv`
- Reason: The suite ranks action decoders by route-null survival, toxicity safety, upload safety, and action size. It is a submission-slot prioritizer, not a public-LB predictor.

## Decoder Ranking

| Rank | Family | Variant | Changed | Route z | Matched score z | Safety z | Upload | Priority | File |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1` | `decoder_order_jury` | `family_supermajority` | `19` | `5.3987` | `5.2815` | `3.5519` | `True` | `1.3944` | `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv` |
| `2` | `decoder_order_jury` | `route_majority_fusion_confirmed` | `19` | `5.3987` | `5.2815` | `3.5519` | `True` | `1.3944` | `submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv` |
| `3` | `core_release_ablation` | `full_core_reference` | `29` | `3.0876` | `3.0876` | `2.4226` | `True` | `1.1830` | `submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv` |
| `4` | `core_release_ablation` | `invariant_only` | `29` | `3.1471` | `2.7626` | `2.3652` | `True` | `1.1524` | `submission_hsjepa_core_ablation_invariant_only_6edb3385_uploadsafe.csv` |
| `5` | `route_frontier` | `s2_route_frontier` | `20` | `2.8238` | `3.3124` | `2.5617` | `True` | `1.1178` | `submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv` |
| `6` | `route_frontier` | `seed_route_frontier` | `20` | `2.6317` | `3.6235` | `2.1296` | `True` | `1.0720` | `submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv` |
| `7` | `route_frontier` | `open_route_frontier` | `20` | `2.4923` | `3.0832` | `2.1707` | `True` | `1.0545` | `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv` |
| `8` | `route_toxicity_fusion` | `s2_driver_safe_route_fusion` | `20` | `2.5212` | `3.3339` | `1.4350` | `True` | `0.9860` | `submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv` |
| `9` | `route_toxicity_fusion` | `seed_driver_safe_route_fusion` | `20` | `1.9565` | `4.0408` | `1.1376` | `True` | `0.8784` | `submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv` |
| `10` | `core_mediated_release` | `core_consensus_shadow_plus` | `29` | `1.9671` | `1.9671` | `2.1394` | `True` | `0.8398` | `submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv` |
| `11` | `decoder_boundary_tomography` | `consensus_shadow_plus` | `27` | `1.8312` | `2.2121` | `1.3977` | `True` | `0.8323` | `submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv` |
| `12` | `core_mediated_release` | `core_boundary_balanced` | `31` | `1.6422` | `1.6422` | `1.6459` | `True` | `0.6344` | `submission_hsjepa_core_mediated_core_boundary_balanced_3b003319_uploadsafe.csv` |
| `13` | `route_toxicity_fusion` | `open_driver_safe_route_fusion` | `20` | `1.2492` | `1.8707` | `1.1862` | `True` | `0.6124` | `submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv` |
| `14` | `core_release_ablation` | `no_action_health` | `40` | `1.4226` | `1.4330` | `1.4179` | `True` | `0.6085` | `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` |
| `15` | `factorized_toxicity` | `dual_safe_expansion` | `114` | `n/a` | `n/a` | `13.6669` | `True` | `0.5800` | `submission_hsjepa_factorized_toxicity_decoder_dual_safe_expansion_23b6de1e_uploadsafe.csv` |
| `16` | `factorized_toxicity` | `teacher_dual_head` | `94` | `n/a` | `n/a` | `12.0672` | `True` | `0.5800` | `submission_hsjepa_factorized_toxicity_decoder_teacher_dual_head_2a3c5d2d_uploadsafe.csv` |
| `17` | `decoder_boundary_tomography` | `boundary_dual_probe` | `25` | `1.5617` | `2.0647` | `0.0000` | `True` | `0.5514` | `submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv` |
| `18` | `decoder_boundary_tomography` | `fusion_only_probe` | `23` | `1.3672` | `1.3287` | `0.0000` | `True` | `0.4765` | `submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv` |
| `19` | `decoder_order_jury` | `s2_pair_consensus` | `18` | `-0.2400` | `-0.8223` | `4.7416` | `True` | `0.4585` | `submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv` |
| `20` | `decoder_boundary_tomography` | `route_only_rescue` | `23` | `1.3200` | `1.4329` | `0.0000` | `True` | `0.4198` | `submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv` |
| `21` | `decoder_order_jury` | `seed_pair_consensus` | `18` | `-0.3789` | `-1.0645` | `4.1153` | `True` | `0.3740` | `submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv` |
| `22` | `route_toxicity_fusion` | `seed_route_toxicity_fusion` | `8` | `-0.0541` | `0.0002` | `0.0000` | `True` | `0.2890` | `submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv` |
| `23` | `route_toxicity_fusion` | `s2_route_toxicity_fusion` | `8` | `-0.0636` | `0.0002` | `0.0000` | `True` | `0.2881` | `submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv` |
| `24` | `core_release_ablation` | `no_invariant_energy` | `32` | `-1.0237` | `0.6297` | `0.9686` | `True` | `0.2741` | `submission_hsjepa_core_ablation_no_invariant_energy_363ccea6_uploadsafe.csv` |
| `25` | `route_toxicity_fusion` | `open_route_toxicity_fusion` | `4` | `-0.1674` | `0.0000` | `0.0002` | `True` | `0.2714` | `submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv` |
| `26` | `row_support_strict` | `strict_route_support_gate` | `4` | `-0.5097` | `2.6873` | `3.1001` | `True` | `0.2635` | `submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv` |
| `27` | `row_support_strict` | `exploratory_route_support_gate` | `34` | `-1.0165` | `1.3787` | `3.6437` | `True` | `0.2098` | `submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv` |
| `28` | `decoder_boundary_tomography` | `consensus_shadow_all_soft` | `32` | `0.0000` | `0.0000` | `-0.9993` | `True` | `0.1751` | `submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv` |
| `29` | `core_release_ablation` | `no_listener_responsibility` | `32` | `-1.0237` | `-1.0707` | `0.9686` | `True` | `0.1550` | `submission_hsjepa_core_ablation_no_listener_responsibility_d2560dc4_uploadsafe.csv` |
| `30` | `core_mediated_release` | `core_jury_veto` | `19` | `-1.6397` | `-1.6397` | `-0.9993` | `True` | `0.1149` | `submission_hsjepa_core_mediated_core_jury_veto_a37f6054_uploadsafe.csv` |
| `31` | `core_mediated_release` | `core_route_rescue` | `19` | `-1.6397` | `-1.6397` | `-0.9993` | `True` | `-0.0451` | `submission_hsjepa_core_mediated_core_route_rescue_a37f6054_uploadsafe.csv` |

## Module Ablation Findings

| Claim | Status | Evidence | Next test |
| --- | --- | --- | --- |
| Support-first decoding is not the full HS-JEPA action rule. | `survived_as_partial_module` | Best row-support route_z=-0.5097, while best route-frontier route_z=2.8238. | Submit route-frontier before expanding support-first amplitudes. |
| Invariant route energy is currently the sharper action-ordering signal. | `alive` | Top ablation row is decoder_order_jury.family_supermajority with priority 1.3944 and matched_score_z=5.2815. | Use route-frontier as the next LB sensor; interpret failure as public/private toxicity dominance. |
| Factorized action-health is necessary but not sufficient. | `alive_with_route_gap` | Best factorized decoder safety_z=13.6669, route boundary=route_not_claimed. | Do not ship factorized toxicity alone unless route-preserving assignment is added. |
| Route-first and toxicity-first are not alternatives; they compose into a decoder order. | `alive` | Best fusion row is s2_driver_safe_route_fusion with route_z=2.5212 and matched_score_z=3.3339. | Use route-toxicity fusion as the next adapter LB sensor if it outranks plain route-frontier. |
| Open candidate route frontier is a true big-bet boundary. | `high_information_if_submitted` | The open-route variant is upload-safe and route-supported locally, but it is outside the selected public seed set. | If seed-route fails but open-route wins, the public-selected candidate pool was too narrow. |
| Cross-decoder jury is the next action-grade HS-JEPA hypothesis. | `alive` | Best jury row is family_supermajority with consensus_z=5.3987 and cross_family_z=5.2815. | Submit the jury consensus candidate if it outranks plain route-frontier after public-sensor risk review. |
| Strict decoder-order jury may be too conservative. | `alive` | Best boundary row is consensus_shadow_plus with boundary_z=1.8312, changed_cells=27, and priority=0.8323. | If strict jury is positive on LB, submit consensus_shadow_plus to test whether weak cross-decoder consensus should be released. |
| The generic HS-JEPA core can mediate real sleep-adapter actions. | `alive` | Best core-mediated row is core_consensus_shadow_plus with release_z=1.9671, invariant_z=2.1394, and priority=0.8398. | Submit core_consensus_shadow_plus after/against strict jury to test whether generic core release improves the action boundary. |
| HS-JEPA core modules are now falsifiable on real adapter actions. | `alive` | Best core-ablation row is full_core_reference with release_z=3.0876, score_z=3.0876, and priority=1.1830. | Use full-core as the safer LB candidate and no-action-health as the architecture sensor for whether action-health is over-constraining release. |

## How To Read This

- route-frontier가 이기면, HS-JEPA의 병목은 latent 발견보다 action ordering에 가깝다.
- route-toxicity fusion이 이기면, action ordering 다음 병목은 factorized action-health gate였다는 뜻이다.
- factorized toxicity가 이기면, public/private toxicity field가 route보다 강한 병목이다.
- row-support strict가 이기면, masked row-support representation이 action-grade decoder로 번역되기 시작한 것이다.
- open-route가 public에서 이기면, 기존 public-selected seed 후보 공간 자체가 좁았다는 큰 발견이다.
- boundary tomography가 이기면, strict cross-decoder jury가 action을 너무 보수적으로 release했다는 뜻이다.
- core-mediated release가 이기면, 범용 HS-JEPA core API가 실제 sleep adapter action release에도 쓸 수 있다는 뜻이다.
- core-release ablation이 이기면, listener/action-health/invariant 중 어떤 core module이 adapter를 과하게 제한하는지 public sensor로 볼 수 있다는 뜻이다.
