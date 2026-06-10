# HS-JEPA Core Release Ablation Probe

실제 sleep-adapter action 후보에서 HS-JEPA core module을 하나씩 제거해 release boundary가 어떻게 바뀌는지 본다.

## Verdict

- Status: `core_release_ablation_ready`
- Recommended LB candidate: `full_core_reference` / `submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv` / priority `0.8314`
- Recommended architecture sensor: `no_action_health` / `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` / priority `0.3282`
- Recommended negative control: `no_action_health` / `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` / priority `0.3282`
- Claim: HS-JEPA core modules change the real sleep-adapter action boundary when removed. This makes listener responsibility, action-health, and invariant energy falsifiable rather than only descriptive.

## Ranking

| Rank | Variant | Cells | Extra | Full overlap | High invariant | Score z | Release z | Priority | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1` | `full_core_reference` | `29` | `11` | `1.0000` | `0.0000` | `3.0876` | `3.0876` | `0.8314` | `submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv` |
| `2` | `invariant_only` | `29` | `12` | `0.9655` | `0.0000` | `2.7626` | `3.1471` | `0.6256` | `submission_hsjepa_core_ablation_invariant_only_6edb3385_uploadsafe.csv` |
| `3` | `no_action_health` | `40` | `21` | `0.7250` | `0.0000` | `1.4330` | `1.4226` | `0.3282` | `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` |
| `4` | `no_listener_responsibility` | `32` | `13` | `0.9062` | `0.0000` | `-1.0707` | `-1.0237` | `-0.0002` | `submission_hsjepa_core_ablation_no_listener_responsibility_d2560dc4_uploadsafe.csv` |
| `5` | `no_invariant_energy` | `32` | `13` | `0.9062` | `0.0000` | `0.6297` | `-1.0237` | `-0.0102` | `submission_hsjepa_core_ablation_no_invariant_energy_363ccea6_uploadsafe.csv` |

## Findings

- `no_listener_responsibility_mostly_matches_full_core`: overlap_with_full=0.9062, high_invariant_rate=0.0000, mean_release_score=0.2838, full_mean_release_score=0.2911
- `no_action_health_changes_release_boundary`: overlap_with_full=0.7250, high_invariant_rate=0.0000, mean_release_score=0.2548, full_mean_release_score=0.2911
- `no_invariant_energy_mostly_matches_full_core`: overlap_with_full=0.9062, high_invariant_rate=0.0000, mean_release_score=0.2838, full_mean_release_score=0.2911
- `invariant_only_mostly_matches_full_core`: overlap_with_full=0.9655, high_invariant_rate=0.0000, mean_release_score=0.2909, full_mean_release_score=0.2911

## Interpretation

full-core와 module-removed 후보의 overlap이 낮으면 해당 module은 장식이 아니라 실제 row-target release를 바꾸는 구조다. public에서 no-module 후보가 이기면 그 module은 현재 adapter에서 과하게 보수적이고, 지면 full HS-JEPA release boundary가 더 설득력 있다.
