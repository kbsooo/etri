# Multi-Head Listener Responsibility Pretext Core

## 목적

이 실험은 HS-JEPA의 hidden listener responsibility를 하나의 smoothed teacher로 만들지 않고,
`current`, `future`, `cohort` 세 head로 보존하는 것이 더 좋은지 검증한다.

```text
subject-relative visible human-life context
  -> current responsibility head
  -> future-consistent responsibility head
  -> cohort-consistent responsibility head
  -> frozen listener probe reads single/concat/delta head geometry
```

## 실행

```bash
python3 team_hsjepa_end_to_end/multi_head_listener_responsibility_pretext_core/run_end_to_end.py
```

## 입력

- OG train/test lifelog data
- cross-subject transported prototype state outputs
- public LB ledger: 사용하지 않음
- prior submission probabilities: 사용하지 않음
- proprietary embedding API: 사용하지 않음

## 현재 결론

multi-head concat은 best single head를 넘지 못했다.
하지만 compact future-consistent head는 prior, raw lifelog PCA, direct semantic responsibility를 이겼다.

```text
best single head: head_future_relative_listener_responsibility_calibrated10
best single-head logloss: 0.677463
best multi-head logloss: 0.677735
delta multi vs single: +0.000272
delta future head vs prior: -0.000395
delta future head vs direct semantic: -0.000175
```

## 해석

죽은 믿음:

```text
current/future/cohort responsibility를 단순 concat하면 listener가 자동으로 좋은 head를 읽는다.
```

살아남은 믿음:

```text
future-consistent listener responsibility is the strongest current core head.
HS-JEPA should expose future-responsibility as a compact interface, not blindly concatenate all heads.
```

## 다음 실험

이 결과가 가리키는 다음 방향은 `future-responsibility head`를 더 강하게 만들거나,
target/listener별로 future/current/cohort head를 선택하는 label-free router를 만드는 것이다.
