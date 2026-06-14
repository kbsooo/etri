# Listener Head Router Pretext Core

## 목적

이 실험은 HS-JEPA가 만든 `current`, `future`, `cohort` listener responsibility head를
무작정 concat하지 않고, target별 listener router가 어떤 head를 읽어야 하는지 검증한다.

```text
subject-relative visible human-life context
  -> current / future / cohort responsibility heads
  -> label-free listener-head router
  -> routed human-state interface
  -> frozen downstream probe
```

## 실행

```bash
python3 team_hsjepa_end_to_end/listener_head_router_pretext_core/run_end_to_end.py
```

## 입력

- OG train/test lifelog data
- transported prototype state outputs
- public LB ledger: 사용하지 않음
- prior submission probabilities: 사용하지 않음
- proprietary embedding API: 사용하지 않음
- labels: pretext/router에서는 사용하지 않고 frozen downstream probe에서만 사용

## 현재 결론

router 구조는 positive다.
best router는 `semantic_prior_router`였고 best single future head를 소폭 이겼다.

```text
best single head: head_future_relative_listener_responsibility_calibrated10
best single-head logloss: 0.677463
best router: semantic_prior_router_listener_responsibility_calibrated10
best router logloss: 0.677427
router delta vs single: -0.000036
router delta vs prior: -0.000430
router delta vs direct semantic: -0.000211
router delta vs naive multi-head concat: -0.000539
```

## 중요한 한계

best가 dynamic confidence router가 아니라 semantic prior router였다는 점이 중요하다.
즉 현재 증거는 다음 문장을 지지한다.

```text
HS-JEPA needs a listener router, but confidence/entropy heuristics are not yet the right learned router.
Target semantics still carries the strongest routing prior.
```

## 다음 실험

다음 단계는 semantic prior를 고정 규칙으로 두는 것이 아니라,
masked/future/cohort pretext에서 target별 head-routing target을 학습시키는 것이다.
