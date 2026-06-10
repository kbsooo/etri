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

## 산출물

- `sleep_competition_adapter/outputs/sleep_competition_adapter_report.json`
- `sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json`
- `sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md`

## 경계

이 adapter는 LB score를 움직이는 대회 적용체다. 논문에서 일반 기술로 주장할 부분은 `hsjepa_core/`에 있어야 하고, 이 adapter는 case study로 말해야 한다.
