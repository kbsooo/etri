# Cross-Listener Transport Decoder

## 핵심 해석

이 모듈은 실패한 target-listener route-lift를 그대로 반복하지 않는다.
listener posterior는 action을 직접 생성하지 않고, route/fusion/core가 제안한 cell의 이동량과 release 경계를 보정하는 transport calibrator로만 사용한다.

## Verdict

- Status: `cross_listener_transport_ready`
- Recommended LB sensor: `submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv`
- Recommended big-bet sensor: `submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv`
- Prior negative sensor: target-listener lift public LB `0.5680255019`

## Ranking

| Rank | Variant | Cells | Extra | Transport z | Listener z | S2 z | Action z | Priority | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `listener_confirmed_shadow` | 23 | 4 | 3.2686 | 3.3448 | 3.4100 | 1.6251 | 0.9427 | `submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv` |
| 2 | `objective_listener_island_probe` | 23 | 4 | 3.2686 | 3.3448 | 3.4100 | 1.6251 | 0.9427 | `submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv` |
| 3 | `row_s2_transport_pressure` | 23 | 4 | 3.2686 | 3.3448 | 3.4100 | 1.6251 | 0.9427 | `submission_hsjepa_cross_listener_transport_row_s2_transport_pressure_d94f8a8e_uploadsafe.csv` |
| 4 | `strict_listener_recalibrated` | 19 | 0 | -0.8796 | 0.0000 | 0.7008 | -0.7147 | 0.0125 | `submission_hsjepa_cross_listener_transport_strict_listener_recalibrated_217acb61_uploadsafe.csv` |

## What This Tests

- 좋아지면: target-listener posterior는 직접 action generator가 아니어도, action release/calibration boundary로는 전이된다는 뜻이다.
- 나빠지면: listener posterior는 representation diagnostic으로만 남고, public-safe assignment는 decoder jury/core-health가 계속 맡아야 한다.
- 특히 `objective_listener_island_probe`가 이기면 현재 H057 row-state 밖에도 objective-stage listener island가 있다는 강한 증거다.
