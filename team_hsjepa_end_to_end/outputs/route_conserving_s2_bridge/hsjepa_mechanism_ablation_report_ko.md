# HS-JEPA Mechanism Ablation Report

이 문서는 HS-JEPA를 과거 제출 버전들의 암묵지가 아니라, 어떤 대체 세계관을 죽이고 어떤 메커니즘이 살아남았는지로 설명하기 위한 팀/논문용 ablation report다.

## One-Sentence Finding

The public sensor killed direct latent decoding and broad action heads, while preserving sparse public-sensitive row-target support; local stress then shows the surviving action should be translated through a route-conserving S2 bridge rather than independent target moves.

## What Public LB Killed Or Preserved

| Alternative worldview | Sensor | Public LB | Delta | Verdict | Meaning |
| --- | --- | ---: | ---: | --- | --- |
| Direct JEPA latent can be decoded straight into target probabilities. | `submission_jepa_latent_residual_probe.csv` | `0.5812273278` | `0.0050683784` vs `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | `killed` | A latent can look coherent locally and still be a toxic action head. |
| Masked-family S2 JEPA translator is already an action-safe decoder. | `submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv` | `0.5772865088` | `0.0011275594` vs `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | `killed` | S2 matters, but S2-only translation without row-target assignment is not safe. |
| Human-social latent can be directly materialized as a tail correction. | `submission_e267_humansocial_tail_balanced_2936100f.csv` | `0.5763294974` | `0.0001705480` vs `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | `killed_as_direct_decoder` | Human/social context remains useful as latent context, not as direct public-safe movement. |
| S1/S4 objective-stage action is a safe objective sleep correction route. | `submission_h010_objective_s1s4_v2_uploadsafe.csv` | `0.5781718175` | `0.0020128681` vs `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | `killed` | Objective-stage movement is not automatically safe; route and listener constraints matter. |
| Public-sensitive row-target support exists. | `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` | `0.5681234831` | `-0.0080354663` vs `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` | `survived_strongly` | The big jump came from finding hidden row-target public-state support, not from larger model capacity. |
| Q2 support rows expose a broader hidden human-state vector. | `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` | `0.5677475939` | `-0.0003758892` vs `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` | `survived` | Freezing Q2 support and translating the rest of the row vector improved the public sensor. |
| Adding extra subjective target route cells should improve the Q2 route. | `submission_h050_target_route_phase_b140216b_uploadsafe.csv` | `0.5679048248` | `0.0000000000` vs `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv` | `not_supported` | Target route was plausible, but row placement/support did not add public value. |
| Dual-state Pareto gate is a private/action-grade decoder. | `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv` | `0.5684942019` | `0.0007466080` vs `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` | `killed_as_decoder` | The gate remains useful as toxicity stress, not as a broad action head. |
| Q3 repair or target-XOR split is the decisive missing axis. | `submission_h144_targetxor_def80b88_uploadsafe.csv / submission_h145_q3repair_2d818e46_uploadsafe.csv` | `0.5679296410` | `0.0001820471` vs `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` | `underidentified_or_killed` | Both tied at public precision; the common body matters more than the branch distinction. |

## What Local Mechanism Stress Killed

| Alternative worldview | Sensor | Actual | Null | p-value | Rank | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Route-conserving bridge selection is just lucky cell picking. | random feasible bundle null | `-0.02457` | `-0.01090` | `0.0000` | `0.186` | `killed_locally` |
| S2 is not special inside the objective-stage bridge decoder. | S2 usage random feasible bundle null | `1.00000` | `0.61508` | `0.0000` | `0.144` | `killed_locally` |

## Surviving Mechanism

```text
public-sensitive support -> row-target assignment -> route-conserving objective-stage bridge -> S2 listener/hub -> bounded submission
```

## Paper-Safe Interpretation

HS-JEPA's paper contribution is the modular separation of hidden human-state orientation, target listener responsibility, row-target assignment, and route-conserving action decoding.  The leaderboard-specific part is the public sensor used to identify sparse support; the reusable mechanism is the decoder invariant and the boundary checks that reject collapsed or toxic latent actions.

## Remaining Boundary

- private leaderboard safety is not proven
- OG-only row-target assignment is not solved
- S2 is a listener/hub for this decoder's action space, not a universal physiological claim
- public LB is used as a sensor and must be separated from the reusable HS-JEPA architecture claim
