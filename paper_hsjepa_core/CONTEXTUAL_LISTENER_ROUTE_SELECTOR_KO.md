# Contextual Listener Route Selector

## 한 줄 요약

HS-JEPA core context로 row-target마다 listener route를 고르는 sample-level router를 만들었지만, 현재 OOF에서는 raw lifelog KNN을 넘지 못했다. 다만 fixed target route보다는 크게 좋아져서, sample-level routing 신호는 살아 있으나 아직 action-grade는 아니라는 결론이다.

## 왜 필요한가

이전 `Core OOF Action-Health Benchmark`에서는 target별 route selector가 강했다.

```text
Q1 -> core KNN
Q2 -> global prior
Q3 -> global prior
S1 -> raw lifelog KNN
S2 -> HS-JEPA action-health
S3 -> raw lifelog KNN
S4 -> core KNN
```

하지만 이 방식은 아직 hand-selected target route다.

HS-JEPA를 더 일반적인 아키텍처로 주장하려면 다음 질문이 중요하다.

```text
target 전체에 하나의 route를 고르는 수준을 넘어,
각 row-target cell마다 어떤 listener route를 들어야 하는지
HS-JEPA core context가 고를 수 있는가?
```

## 사용하지 않은 정보

이 실험은 다음을 쓰지 않는다.

- public LB score ledger
- 기존 submission probability
- 기존 성공 action teacher
- row-state frontier file
- active-silence frontier file

즉 public feedback을 이용해 route를 맞춘 것이 아니라, train OOF cell에서 route-risk를 학습한 실험이다.

## 코드

```bash
python3 sleep_competition_adapter/contextual_listener_route_selector.py
```

주요 산출물:

- `sleep_competition_adapter/outputs/contextual_listener_route_selector/contextual_listener_route_readout.json`
- `sleep_competition_adapter/outputs/contextual_listener_route_selector/contextual_listener_route_oof_metrics.csv`
- `sleep_competition_adapter/outputs/contextual_listener_route_selector/contextual_listener_route_oof_cells.csv`
- `sleep_competition_adapter/outputs/contextual_listener_route_selector/contextual_listener_route_oof_pairs.csv`
- `sleep_competition_adapter/outputs/contextual_listener_route_selector/contextual_listener_route_test_selected_cells.csv`
- `submission_hsjepa_contextual_listener_router_3cbcbe6e_uploadsafe.csv`

## 방법

1. temporal subject-tail OOF split을 만든다.
2. 각 OOF row-target cell에 대해 여러 expert prediction을 만든다.
3. expert별 실제 cell logloss를 계산한다.
4. HS-JEPA context, expert disagreement, outlier geometry, expert family feature로 route-risk regressor를 학습한다.
5. held-out subject의 row-target cell에서 예상 loss가 낮은 route를 고른다.
6. 추가로 raw lifelog KNN을 기본값으로 두고, router가 충분히 자신 있을 때만 다른 route로 이탈하는 raw-fallback 정책을 평가한다.

비교한 route:

- `global_prior`
- `subject_prior`
- `raw_knn_blend`
- `core_knn_blend`
- `hsjepa_action_health_*`
- `raw_action_core_health_*`

## 결과

OOF score:

| model | mean logloss |
| --- | ---: |
| raw lifelog KNN blend | 0.636997 |
| core KNN blend | 0.638266 |
| contextual raw-fallback margin 0.014 | 0.638444 |
| contextual soft router | 0.643769 |
| contextual hard router | 0.650110 |
| subject prior | 0.650566 |
| fixed target listener route OOF | 0.657106 |
| global prior | 0.666833 |

핵심 수치:

- contextual soft router는 fixed target route보다 `-0.013337` 좋다.
- best raw-fallback router는 fixed target route보다 좋고 raw KNN에 근접하지만, raw KNN보다 `+0.001447` 나쁘다.
- 따라서 sample-level router는 살아 있지만 아직 raw KNN을 이길 정도로 안정적이지 않다.

## 해석

이 실험은 HS-JEPA에 유리한 결과와 불리한 결과를 동시에 준다.

유리한 점:

```text
HS-JEPA context는 fixed target route보다 나은 sample-level responsibility signal을 가진다.
```

불리한 점:

```text
그 signal은 아직 raw lifelog KNN이라는 강한 기본 예측기를 넘어설 만큼 안정적이지 않다.
```

즉 현재 HS-JEPA의 architecture boundary는 다음과 같다.

```text
target-level route selection: strong evidence
sample-level contextual route selection: alive but not release-grade
```

## 논문에서의 위치

이 결과는 실패가 아니다. 오히려 HS-JEPA를 더 정확하게 만든다.

과장된 주장:

```text
HS-JEPA core가 모든 row-target에 대해 최적 listener를 직접 고른다.
```

현재 증거에 맞는 주장:

```text
HS-JEPA core provides route-risk features that improve over fixed listener routes,
but sample-level route selection still requires stronger supervision or more data
to outperform robust raw-lifelog nearest-neighbor baselines.
```

한국어로는:

```text
HS-JEPA core는 고정된 target route보다 더 세밀한 route-risk 신호를 제공하지만,
현재 데이터 규모에서는 sample-level listener router가 raw lifelog KNN을 안정적으로 넘지는 못한다.
```

## 다음 질문

다음 breakthrough 질문은 다음이다.

```text
sample-level route를 바로 예측하지 말고,
raw KNN이 실패하는 조건만 더 정확히 찾을 수 있는가?
```

즉 다음 모듈은 full router가 아니라 `raw-KNN failure detector`가 되어야 한다.
