# HS-JEPA Core Module Benchmark

이 벤치마크는 sleep competition adapter 없이 HS-JEPA core가 여러 인간상태 상황에서 기대한 release/reject 행동을 내는지 확인한다.

## Verdict

- Status: `core_module_benchmark_ready`
- Full-core mean F1: `1.000`
- Action-health removal false-positive lift: `9`
- Invariant removal false-positive lift: `1`

## Policy Summary

| Policy | Mean F1 | False positives | False negatives |
| --- | ---: | ---: | ---: |
| `full_core` | `1.000` | `0` | `0` |
| `remove_listener_responsibility` | `0.800` | `3` | `0` |
| `remove_action_health` | `0.467` | `9` | `0` |
| `remove_invariant_energy` | `0.933` | `1` | `0` |
| `invariant_only` | `0.500` | `8` | `0` |

## Scenario Summary

| Scenario | Expected release | Full-core release | Main failure exposed |
| --- | --- | --- | --- |
| `stable_routine_survey_state` | `survey_small_state_update` | `survey_small_state_update` | remove_action_health: may over-release low-support shortcuts; remove_invariant_energy: may release state moves without manifold support |
| `sensor_fragmentation_state` | `sensor_fragmentation_update` | `sensor_fragmentation_update` | remove_listener_responsibility: may flatten listener authority and release subjective actions; remove_action_health: may release weak survey/recovery moves |
| `recovery_debt_state` | `recovery_debt_update` | `recovery_debt_update` | remove_listener_responsibility: may confuse recovery with sensor/social listeners; remove_action_health: may release weak non-recovery moves |
| `cohort_outlier_uncertain_state` | `none` | `none` | remove_action_health: may release uncertain guesses because threshold is gone; remove_invariant_energy: may ignore that all guesses leave the stable manifold |
| `off_manifold_listener_trap` | `survey_manifold_update` | `survey_manifold_update` | remove_invariant_energy: may release off-manifold high-support listener action; remove_action_health: may release weak social action |

## 해석

- 이 파일은 LB 점수를 만들지 않는다.
- 대신 HS-JEPA가 `특정 대회 target 이름 없이도` context/listener/action/invariant 구조로 행동한다는 증거를 만든다.
- sleep adapter의 public-sensor 실험은 별도 case-study이고, 이 benchmark는 architecture sanity check다.
