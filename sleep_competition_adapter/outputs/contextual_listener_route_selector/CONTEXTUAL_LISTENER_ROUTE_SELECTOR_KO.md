# Contextual Listener Route Selector

## 목적

target별 고정 route selector 다음 질문을 검증한다.

```text
HS-JEPA core context가 row-target마다 어떤 listener route를 들어야 하는지 고를 수 있는가?
```

이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 쓰지 않는다.

## 핵심 결과

- best OOF model: `raw_knn_blend`
- best OOF logloss: `0.636997`
- fixed target route OOF logloss: `0.657106`
- contextual hard router OOF logloss: `0.650110`
- contextual soft router OOF logloss: `0.643769`
- best contextual/fallback model: `contextual_raw_fallback_margin_0.014`
- best contextual/fallback OOF logloss: `0.638444`
- delta vs raw KNN: `0.001447`
- selected submission mode: `raw_fallback_margin_0.014`
- generated candidate: `submission_hsjepa_contextual_listener_router_3cbcbe6e_uploadsafe.csv`

## OOF score table

| model | mean_logloss |
| --- | --- |
| raw_knn_blend | 0.636997 |
| core_knn_blend | 0.638266 |
| contextual_raw_fallback_margin_0.014 | 0.638444 |
| contextual_raw_fallback_margin_0.008 | 0.640415 |
| contextual_raw_fallback_margin_0.022 | 0.642687 |
| contextual_listener_router_soft_oof | 0.643769 |
| hsjepa_action_health__high_margin_listener_health | 0.644184 |
| contextual_raw_fallback_margin_0.004 | 0.646388 |
| hsjepa_action_health__balanced_listener_health | 0.646601 |
| hsjepa_action_health__wide_listener_health | 0.646813 |
| hsjepa_action_health__strict_listener_health | 0.647582 |
| raw_action_core_health__high_margin_listener_health | 0.647802 |
| raw_action_core_health__wide_listener_health | 0.648662 |
| raw_action_core_health__balanced_listener_health | 0.648920 |
| raw_action_core_health__strict_listener_health | 0.649223 |
| contextual_raw_fallback_margin_0.000 | 0.649794 |
| contextual_listener_router_hard_oof | 0.650110 |
| subject_prior | 0.650566 |
| fixed_target_listener_route_oof | 0.657106 |
| global_prior | 0.666833 |

## 해석

contextual router가 fixed target route를 이기면 HS-JEPA가 sample-level listener responsibility로 확장됐다는 뜻이다.

raw-fallback이 raw KNN을 이기면 HS-JEPA가 좋은 기본 예측기에서 벗어날 순간을 고른다는 뜻이다.

이기지 못하면 현재 증거는 target-level route selection까지가 안정적이고, sample-level route는 아직 데이터 수가 부족하거나 action-risk supervision이 약하다는 뜻이다.