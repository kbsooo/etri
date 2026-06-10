# HS-JEPA Decoder Boundary Tomography Solver

이 실험은 strict decoder-order jury가 버린 셀을 세 부류로 나누어 본다.

- `consensus_shadow`: route와 fusion이 같은 방향으로 동의했지만 strict vote 기준을 못 넘긴 셀
- `route_only`: route invariant만 action을 제안한 셀
- `fusion_only`: action-health/fusion만 action을 제안한 셀

## Verdict

- Status: `boundary_tomography_ready`
- Recommended LB sensor: `consensus_shadow_plus` -> `submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv`
- Claim: The next action-decoder bottleneck is whether strict cross-decoder jury is too conservative; weak consensus and route-only cells are separate hidden worlds and must be tested separately.
- Failure interpretation: If every boundary probe worsens public LB, the safe frontier is strict cross-decoder consensus. If consensus_shadow wins, the jury was too conservative. If route_only wins, action-health is over-vetoing route signal.

## Ranking

| Rank | Variant | Extra cells | Classes | Boundary z | Weight z | Priority | File |
| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| `1` | `consensus_shadow_plus` | `8` | `consensus_shadow` | `1.8312` | `1.3626` | `0.6991` | `submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv` |
| `2` | `boundary_dual_probe` | `6` | `route_only,fusion_only` | `1.5617` | `1.3905` | `0.3581` | `submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv` |
| `3` | `route_only_rescue` | `4` | `route_only` | `1.3200` | `0.5152` | `0.3303` | `submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv` |
| `4` | `fusion_only_probe` | `4` | `fusion_only` | `1.3672` | `1.3661` | `0.3067` | `submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv` |
| `5` | `consensus_shadow_all_soft` | `13` | `consensus_shadow` | `0.0000` | `-1.4423` | `0.1932` | `submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv` |

## Why This Matters

strict jury가 public에서 좋으면 안전한 consensus가 맞다. 하지만 그 다음 병목은 too-conservative release일 수 있다.
이 solver는 그 보수성을 구조적으로 찌르는 다음 실험 후보를 만든다.
