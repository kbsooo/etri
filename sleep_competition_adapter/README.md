# Sleep Competition Adapter

이 디렉토리는 범용 `hsjepa_core/`를 수면 기반 생활습관 로그 대회에 꽂는 adapter다.

Core는 `listener`, `invariant`, `action-health` 같은 일반 개념만 알고, adapter가 다음을 제공한다.

- Q1/Q2/Q3/S1/S2/S3/S4 listener schema
- sleep-stage/Q-S route invariant
- public LB sensor boundary
- row-target sparse submission format
- upload-safe submission packaging

## 생성

```bash
python3 sleep_competition_adapter/build_sleep_competition_adapter_report.py
```

큰 thesis 검증 실험:

```bash
python3 sleep_competition_adapter/spectral_public_tangent_solver.py
python3 sleep_competition_adapter/counterfactual_listener_dropout_solver.py
```

`spectral_public_tangent_solver.py`는 H057 이후 public에서 실패한 제출들을 독립 실패로 보지 않고 하나의 negative representation space로 본다. 실패 액션들의 첫 spectral mode가 지배적이면, 다음 제출은 bad tangent의 반대 방향을 타야 하는지 또는 그와 직교한 private-safe residual subspace만 믿어야 하는지를 가르는 센서가 된다.

이 실험은 route/fusion/target-listener/anti-shortcut을 서로 다른 listener로 보고, 한 listener를 가려도 살아남는 row-target action만 건강한 action 후보로 본다. 생성되는 `dropout_fullfield_aggressive`와 `toxic_direction_inversion` 후보는 같은 hidden action field를 믿을지, public-negative direction을 뒤집을지를 가르는 A/B 센서다.

## 산출물

- `sleep_competition_adapter/outputs/sleep_competition_adapter_report.json`
- `sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md`
- `sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout_ko.md`
- `sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout_ko.md`

## 경계

이 adapter는 LB score를 움직이는 대회 적용체다. 논문에서 일반 기술로 주장할 부분은 `hsjepa_core/`에 있어야 하고, 이 adapter는 case study로 말해야 한다.
