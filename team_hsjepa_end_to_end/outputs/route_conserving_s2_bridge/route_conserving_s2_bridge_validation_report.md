# Route-Conserving S2 Bridge Validation Report

이 리포트는 팀원이 HS-JEPA 패키지를 열었을 때, 핵심 주장이 산출물로 검증되는지 확인하기 위한 자동 검증 결과다.

## Pass/Fail Checks

| Check | Status | Detail |
| --- | --- | --- |
| `exists:route_conserving_s2_bridge_package.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_package.json |
| `exists:route_conserving_s2_bridge_evidence_table.csv` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_evidence_table.csv |
| `exists:route_conserving_s2_bridge_stress_audit.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_audit.json |
| `exists:route_conserving_s2_bridge_stress_summary.csv` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_summary.csv |
| `exists:README.md` | `PASS` | team_hsjepa_end_to_end/README.md |
| `exists:ROUTE_CONSERVING_S2_BRIDGE_KO.md` | `PASS` | team_hsjepa_end_to_end/ROUTE_CONSERVING_S2_BRIDGE_KO.md |
| `exists:HS_JEPA_ARCHITECTURE_PACKAGE_KO.md` | `PASS` | paper_hsjepa_core/HS_JEPA_ARCHITECTURE_PACKAGE_KO.md |
| `exists:experiment_log.md` | `PASS` | experiment_log.md |
| `roles:all_present` | `PASS` | roles=['competition_primary', 'human_state_probe', 'interpretable_s2_hub'] |
| `submission_root:competition_primary` | `PASS` | submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv |
| `submission_local:competition_primary` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv |
| `upload_safe:competition_primary` | `PASS` | {"rows": 250, "keys_match": true, "duplicate_keys": 0, "nan_cells": 0, "finite": true, "min_prob": 4.939277944527429e-06, "max_prob": 0.9999967514907456, "upload_safe": true} |
| `submission_root:interpretable_s2_hub` | `PASS` | submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv |
| `submission_local:interpretable_s2_hub` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv |
| `upload_safe:interpretable_s2_hub` | `PASS` | {"rows": 250, "keys_match": true, "duplicate_keys": 0, "nan_cells": 0, "finite": true, "min_prob": 4.939277944527429e-06, "max_prob": 0.9999967514907456, "upload_safe": true} |
| `submission_root:human_state_probe` | `PASS` | submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv |
| `submission_local:human_state_probe` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv |
| `upload_safe:human_state_probe` | `PASS` | {"rows": 250, "keys_match": true, "duplicate_keys": 0, "nan_cells": 0, "finite": true, "min_prob": 4.939277944527429e-06, "max_prob": 0.9999967514907456, "upload_safe": true} |
| `evidence:three_roles` | `PASS` | rows=3 |
| `evidence:roles` | `PASS` | competition_primary,interpretable_s2_hub,human_state_probe |
| `stress:primary_present` | `PASS` | route_conserving_objective_bridge_primary |
| `stress:s2_present` | `PASS` | s2_listener_bridge_interpretable |
| `mechanism:primary_route_p` | `PASS` | p=0.0 |
| `mechanism:primary_route_z` | `PASS` | z=-9.66 |
| `mechanism:primary_rank` | `PASS` | rank=0.186 |
| `mechanism:s2_route_p` | `PASS` | p=0.0 |
| `mechanism:s2_route_z` | `PASS` | z=-9.46 |
| `mechanism:s2_hub_p` | `PASS` | p=0.0 |
| `mechanism:s2_hub_usage` | `PASS` | rate=1.000 |
| `mechanism:s2hub_rank` | `PASS` | rank=0.144 |

## Claim-Evidence Matrix

| Claim | Evidence | Boundary |
| --- | --- | --- |
| Route-conserving decoder | Primary route z `-9.66`, S2 route z `-9.46` | This proves unusual selection inside the candidate pool, not private leaderboard safety. |
| S2 listener/hub | S2 bridge usage `1.000` vs null `0.615` | S2 is a listener/hub in this route decoder, not necessarily a universal sleep factor. |
| Human-state as orientation diagnostic | Package contains a separate human_state_probe role and does not use it as the primary assignment solver | Human-state alone still does not solve row support assignment. |
| Team reproducibility | Wrapper, stress audit, validation report, manifest, and upload-safe submissions are generated | The package depends on existing local competition artifacts and score ledger. |

## Interpretation

이 검증이 통과하면, 현재 패키지는 단순 leaderboard 시행착오 묶음이 아니라 다음 형태의 검증 가능한 메커니즘으로 설명할 수 있다.

```text
public-sensitive driver action
  + route-conserving bridge action
  + S2 listener/hub constraint
  + human-state orientation diagnostic
```

검증이 증명하지 않는 것도 명확하다. 이것은 private-safe를 증명하지 않고, OG-only encoder가 완전한 row-target assignment solver임을 증명하지도 않는다. 대신 가능한 action 후보 공간 안에서 선택된 bridge rule이 통계적으로 특이하고 재현 가능한 decoder constraint임을 증명한다.
