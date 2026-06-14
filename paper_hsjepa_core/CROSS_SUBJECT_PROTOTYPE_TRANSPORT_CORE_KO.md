# Cross-Subject Prototype Transport Core

## 한 줄 요약

이 실험은 HS-JEPA prototype grammar를 더 엄격하게 검증한다.
prototype을 전체 데이터에서 한 번 만든 것이 아니라, fold마다 train subjects/blocks에서만 만든 뒤 held-out row/subject로 운반했다.

```text
train subjects define subject-relative episode grammar
  -> held-out subject is transported into that grammar
  -> visible views predict hidden transported prototype responsibilities
  -> frozen probes read transported state
```

## 판정

- verdict: `cross_subject_prototype_transport_core_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 왜 이것이 이전 Prototype Grammar보다 엄격한가

이전 실험은 subject-relative grammar 자체가 유효한지 먼저 확인했다.
이번 실험은 더 강한 질문을 던진다.

```text
다른 subject들이 만든 human-state grammar를
처음 보는 subject에게 운반해도 같은 구조가 들리는가?
```

즉 subject identity shortcut을 줄이는 것에서 한 단계 더 나아가,
grammar가 cross-subject transport 가능한지 본다.

## Subject-Heldout Transport Pretext

- mean cross-entropy lift vs prior: `0.060052`

| target_view | cross_entropy | prior_cross_entropy | cross_entropy_lift_vs_prior | accuracy | prior_accuracy |
| --- | --- | --- | --- | --- | --- |
| phone_behavior | 0.724108 | 0.829704 | 0.105597 | 0.666667 | 0.648889 |
| app_social_context | 0.914042 | 1.009415 | 0.095373 | 0.573333 | 0.460000 |
| body_activity_sleep | 0.960824 | 1.025588 | 0.064764 | 0.544444 | 0.524444 |
| mobility_environment | 0.971262 | 1.002899 | 0.031638 | 0.553333 | 0.508889 |
| calendar_rhythm | 0.735643 | 0.738530 | 0.002887 | 0.726667 | 0.686667 |

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| transported_prototype_stats_probabilities_calibrated10 | 0.675831 | 0.408289 |
| transported_observed_upper_bound_calibrated10 | 0.676276 | 0.407043 |
| transported_prototype_stats_calibrated10 | 0.676446 | 0.407225 |
| transported_prototype_stats_probabilities_calibrated05 | 0.676689 | 0.393426 |
| calendar_rhythm_calibrated10 | 0.676787 | 0.402565 |
| transported_observed_upper_bound_calibrated05 | 0.676960 | 0.396405 |
| transported_prototype_probabilities_calibrated10 | 0.677041 | 0.394149 |
| transported_prototype_stats_calibrated05 | 0.677048 | 0.394126 |
| transported_prototype_probabilities_calibrated05 | 0.677291 | 0.383771 |
| calendar_rhythm_calibrated05 | 0.677293 | 0.396052 |
| prior_only_calibrated05 | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| raw_lifelog_pca_calibrated05 | 0.678009 | 0.398296 |
| calendar_rhythm | 0.678576 | 0.480758 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| transported_observed_upper_bound | 0.704449 | 0.509842 |
| transported_prototype_stats | 0.706093 | 0.503166 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_lifelog_pca_calibrated05 | 0.667603 | 0.603053 |
| transported_observed_upper_bound_calibrated10 | 0.668631 | 0.543993 |
| transported_prototype_stats_probabilities_calibrated10 | 0.669220 | 0.535684 |
| transported_prototype_stats_calibrated10 | 0.669298 | 0.523682 |
| calendar_rhythm_calibrated10 | 0.669335 | 0.547961 |
| transported_observed_upper_bound_calibrated05 | 0.669639 | 0.543993 |
| transported_prototype_stats_probabilities_calibrated05 | 0.669886 | 0.535684 |
| transported_prototype_stats_calibrated05 | 0.669930 | 0.523682 |
| calendar_rhythm_calibrated05 | 0.670047 | 0.547961 |
| calendar_rhythm | 0.670067 | 0.547961 |
| prior_only_calibrated05 | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| transported_prototype_probabilities_calibrated05 | 0.670958 | 0.493803 |
| transported_prototype_probabilities_calibrated10 | 0.671265 | 0.493803 |
| transported_observed_upper_bound | 0.685536 | 0.543993 |
| transported_prototype_probabilities | 0.712417 | 0.493803 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| raw_lifelog_pca_calibrated05 | 0.670991 | 0.447387 |
| calendar_rhythm_calibrated10 | 0.673248 | 0.416598 |
| calendar_rhythm_calibrated05 | 0.673631 | 0.410856 |
| transported_prototype_probabilities_calibrated10 | 0.673725 | 0.406109 |
| transported_prototype_probabilities_calibrated05 | 0.673787 | 0.399657 |
| transported_observed_upper_bound_calibrated05 | 0.673901 | 0.404786 |
| transported_observed_upper_bound_calibrated10 | 0.673942 | 0.413328 |
| transported_prototype_stats_probabilities_calibrated05 | 0.674016 | 0.405059 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| prior_only_calibrated05 | 0.674078 | 0.401854 |
| transported_prototype_stats_probabilities_calibrated10 | 0.674258 | 0.416296 |
| transported_prototype_stats_calibrated05 | 0.674343 | 0.404814 |
| transported_prototype_stats_calibrated10 | 0.674786 | 0.413064 |
| calendar_rhythm | 0.678226 | 0.490044 |
| raw_lifelog_pca | 0.686287 | 0.588427 |
| transported_prototype_probabilities | 0.716160 | 0.491011 |

## Subject Leakage Probe

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| calendar_rhythm | 0.137778 | 0.126667 | 0.011111 |
| transported_prototype_stats | 0.273333 | 0.126667 | 0.146667 |
| transported_prototype_probabilities | 0.464444 | 0.126667 | 0.337778 |
| transported_observed_upper_bound | 0.468889 | 0.126667 | 0.342222 |
| transported_prototype_stats_probabilities | 0.535556 | 0.126667 | 0.408889 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## Neighbor Consistency

| feature_set | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| calendar_rhythm | 0.586159 | 0.530794 | 0.055365 |
| raw_lifelog_pca | 0.580571 | 0.528127 | 0.052444 |
| transported_prototype_stats_probabilities | 0.544254 | 0.528635 | 0.015619 |
| transported_observed_upper_bound | 0.546095 | 0.532317 | 0.013778 |
| transported_prototype_probabilities | 0.543302 | 0.531302 | 0.012000 |
| transported_prototype_stats | 0.539111 | 0.528063 | 0.011048 |

## 현재 해석

strong positive이면 논문 주장은 다음으로 강화된다.

```text
HS-JEPA learns a subject-relative human-state grammar that can be transported
from observed subjects to unseen subjects before any label-specific decoder.
```

negative이면 경계도 명확하다.

```text
Prototype grammar is useful when fitted on the full cohort,
but its cross-subject transported form is not yet strong enough.
The next step should be route/listener-conditioned transport rather than a single global grammar.
```
