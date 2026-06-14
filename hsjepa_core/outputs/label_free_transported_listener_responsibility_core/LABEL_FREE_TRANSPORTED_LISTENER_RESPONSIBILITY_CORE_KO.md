# Label-Free Transported Listener Responsibility Core

## 한 줄 요약

이 실험은 target/listener view를 label probe로 고르지 않는다.
target 설명에서 고정한 human-state listener profile과 transported prototype의 confidence/entropy/energy만으로
label-free listener responsibility를 만든 뒤, frozen probe로만 검증한다.

```text
target description + transported prototype reliability
  -> label-free listener responsibility
  -> frozen subject-heldout / row-block probes
```

## 판정

- verdict: `label_free_listener_responsibility_prior_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- listener profile source: `target_descriptions_and_human_state_semantics`

## 핵심 수치

- subject semantic listener logloss: `0.677638`
- subject global transport logloss: `0.676724`
- subject prior logloss: `0.677858`
- delta vs global transport: `0.000914`
- delta vs prior: `-0.000219`
- delta vs raw lifelog PCA: `-0.001069`
- row-block delta vs global: `0.000044`
- chronological delta vs global: `-0.001343`

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| label_free_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| label_free_family_listener_responsibility_calibrated10 | 0.677683 | 0.389376 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| label_free_semantic_listener_responsibility | 0.698179 | 0.473842 |
| label_free_family_listener_responsibility | 0.700823 | 0.468973 |
| global_transported_prototype | 0.736658 | 0.500467 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Target별 Semantic Listener Probe

| target | logloss | auc |
| --- | --- | --- |
| Q1 | 0.703667 | 0.395508 |
| Q2 | 0.697038 | 0.395096 |
| Q3 | 0.681953 | 0.405494 |
| S1 | 0.642905 | 0.393043 |
| S2 | 0.657738 | 0.417556 |
| S3 | 0.660806 | 0.359877 |
| S4 | 0.699360 | 0.376022 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| label_free_family_listener_responsibility_calibrated10 | 0.673158 | 0.412629 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| label_free_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| prior_only | 0.674078 | 0.401854 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| label_free_semantic_listener_responsibility | 0.686009 | 0.497482 |
| raw_lifelog_pca | 0.686287 | 0.588427 |
| label_free_family_listener_responsibility | 0.687783 | 0.495743 |
| global_transported_prototype | 0.728298 | 0.506119 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| label_free_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| label_free_family_listener_responsibility_calibrated10 | 0.670775 | 0.498091 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| label_free_semantic_listener_responsibility | 0.684005 | 0.524836 |
| label_free_family_listener_responsibility | 0.692994 | 0.498091 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| global_transported_prototype | 0.748130 | 0.491242 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| label_free_family_listener_responsibility | 0.395556 | 0.126667 | 0.268889 |
| label_free_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## Semantic Target Profiles

```json
{
  "Q1": {
    "body_activity_sleep": 1.4,
    "mobility_environment": 1.1,
    "calendar_rhythm": 1.0
  },
  "Q2": {
    "calendar_rhythm": 1.3,
    "phone_behavior": 1.1,
    "app_social_context": 1.0
  },
  "Q3": {
    "body_activity_sleep": 1.3,
    "app_social_context": 1.1,
    "phone_behavior": 1.0
  },
  "S1": {
    "body_activity_sleep": 1.5,
    "calendar_rhythm": 1.0
  },
  "S2": {
    "body_activity_sleep": 1.4,
    "calendar_rhythm": 1.1,
    "mobility_environment": 0.7
  },
  "S3": {
    "calendar_rhythm": 1.3,
    "phone_behavior": 1.0,
    "app_social_context": 0.8
  },
  "S4": {
    "body_activity_sleep": 1.3,
    "phone_behavior": 1.0,
    "app_social_context": 0.8
  }
}
```

## 해석

positive이면:

```text
HS-JEPA can expose a listener-readable transported grammar without selecting routes from labels.
```

negative이면:

```text
Human-semantic listener profiles are not enough.
The previous listener-readout gain mostly came from frozen label selection, so the next core must learn
listener responsibility as a pretext target rather than hand-code it.
```
