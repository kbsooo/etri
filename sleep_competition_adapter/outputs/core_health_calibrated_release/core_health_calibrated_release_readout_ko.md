# HS-JEPA Core-Health Calibrated Release

dataset-free core benchmark에서 action-health 제거가 false positive를 크게 만든다는 결론을 실제 sleep adapter release rule에 넣은 실험이다.

## Verdict

- Status: `core_health_calibrated_release_ready`
- Recommended LB candidate: `benchmark_guarded_full_plus` / `submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv` / priority `0.3882`
- Recommended big-bet sensor: `route_pressure_boundary_probe` / `submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv` / priority `0.3834`
- Recommended pressure sensor: `health_relaxed_pressure_sensor` / `submission_hsjepa_core_health_health_relaxed_pressure_sensor_7da82c23_uploadsafe.csv` / priority `-0.2113`
- Core benchmark action-health FP lift: `9.0`

## Ranking

| Rank | Variant | Cells | Extra | Full overlap | Pressure z | Health z | Risk margin z | High risk | Priority | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `1` | `benchmark_guarded_full_plus` | `31` | `13` | `0.9355` | `1.9675` | `2.4878` | `-2.1838` | `0.0000` | `0.3882` | `submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv` |
| `2` | `route_pressure_boundary_probe` | `43` | `25` | `0.6744` | `1.9291` | `2.4953` | `-2.2102` | `0.0930` | `0.3834` | `submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv` |
| `3` | `health_relaxed_pressure_sensor` | `21` | `2` | `0.8571` | `0.9577` | `-1.7659` | `2.0495` | `0.0000` | `-0.2113` | `submission_hsjepa_core_health_health_relaxed_pressure_sensor_7da82c23_uploadsafe.csv` |

## Interpretation

- `benchmark_guarded_full_plus`가 public에서 좋으면 action-health guard가 leaderboard action에도 유효하다는 주장에 힘이 실린다.
- `route_pressure_boundary_probe`가 좋으면 route-only high-responsibility cells가 action-health에 의해 과하게 막혔다는 뜻이다.
- `health_relaxed_pressure_sensor`가 이기면 generic benchmark와 sleep adapter가 충돌한다. 그 경우 action-health는 버릴 모듈이 아니라 adapter-specific decoder를 다시 배워야 하는 모듈이다.
