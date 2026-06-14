# Global Transport Residual Listener-Router Core

## 목적

이 패키지는 HS-JEPA core의 중요한 설계 질문을 검증한다.

```text
learned listener-head router는 global transported prototype grammar를 대체해야 하는가,
아니면 그 위에 붙는 residual listener interface여야 하는가?
```

이 실험은 제출 CSV를 만들지 않는다.
public LB ledger, prior submission probability, proprietary embedding API를 사용하지 않는다.
label은 representation이 고정된 뒤 frozen downstream probe에서만 사용한다.

## 구조

```text
OG train lifelog table
  -> subject-relative visible human-life context
  -> cross-subject transported prototype grammar
  -> current / future / cohort listener heads
  -> label-free hidden listener-head suitability prediction
  -> learned residual listener-router interface
  -> frozen subject-heldout / row-block / chronological probes
```

## 왜 중요한가

직전 learned listener-head router는 fixed semantic-prior router와 best single future head를 이겼다.
하지만 subject-heldout global transported prototype grammar는 넘지 못했다.

그래서 이번에는 router를 `replacement`로 보지 않고, transported grammar 위의 `residual interface`로 본다.
이게 맞다면 HS-JEPA core는 하나의 벡터가 아니라 다음 구조가 된다.

```text
transport backbone + listener-specific residual router
```

## 실행

프로젝트 루트에서 실행한다.

```bash
python3 team_hsjepa_end_to_end/global_transport_residual_listener_router_core/run_end_to_end.py
```

## 출력

```text
hsjepa_core/outputs/global_transport_residual_listener_router_core/
paper_hsjepa_core/GLOBAL_TRANSPORT_RESIDUAL_LISTENER_ROUTER_CORE_KO.md
```

주요 파일:

- `global_transport_residual_listener_router_summary.json`
- `GLOBAL_TRANSPORT_RESIDUAL_LISTENER_ROUTER_CORE_KO.md`
- `global_transport_residual_listener_router_probe_metrics.csv`
- `global_transport_residual_listener_router_pretext_metrics.csv`
- `global_transport_residual_listener_router_subject_leakage.csv`
- `global_transport_residual_listener_router_weights.csv`

## 현재 결과

판정:

```text
global_transport_residual_listener_router_positive
```

핵심 수치:

```text
global transport logloss: 0.676724
learned router alone logloss: 0.677359
semantic-prior router alone logloss: 0.677427
best residual feature: global_plus_semantic_and_learned_router_calibrated10
best residual logloss: 0.675817
delta vs global transport: -0.000907
delta vs learned router alone: -0.001542
delta vs semantic-prior router alone: -0.001610
row-block delta vs global: -0.000428
chronological delta vs global: +0.001965
```

Subject leakage:

```text
best residual leakage: 0.440000
global transport leakage: 0.542222
learned router alone leakage: 0.446667
raw lifelog PCA leakage: 0.940000
```

## 해석

살아난 믿음:

```text
HS-JEPA는 transported grammar를 하나의 global latent로만 내보내면 부족하다.
listener가 target별로 어떤 head를 들어야 하는지 학습한 residual interface를 붙이면
subject-heldout과 row-block stress에서 더 잘 읽힌다.
```

남은 경계:

```text
chronological holdout에서는 global transport 대비 악화된다.
즉 이 residual router는 subject-invariant 읽기에는 도움이 되지만,
시간 순서 drift를 자동으로 해결하는 decoder는 아니다.
```

## 논문 포인트

이 실험은 HS-JEPA를 다음처럼 정리하는 근거가 된다.

```text
HS-JEPA first learns a transferable human-state grammar, then exposes it through
a listener-specific residual interface.  The representation is not a single
monolithic embedding; it is a transported grammar plus a learned readout route.
```

한국어로는 다음 문장이 적절하다.

```text
HS-JEPA는 인간 생활 상태를 하나의 벡터로 압축하지 않고,
운반 가능한 생활 episode grammar를 backbone으로 둔 뒤,
각 target listener가 그 grammar를 어떻게 읽어야 하는지 residual router로 학습한다.
```

## 과장하면 안 되는 점

이 실험은 core representation 증거다.
competition 제출용 action decoder나 public/private equation solver가 아니다.

또한 chronological stress가 악화되므로, paper에서는 다음처럼 말해야 한다.

```text
Residual listener routing improves subject-invariant readability, but temporal
drift still requires a separate rhythm-conditioned or action-health decoder.
```
