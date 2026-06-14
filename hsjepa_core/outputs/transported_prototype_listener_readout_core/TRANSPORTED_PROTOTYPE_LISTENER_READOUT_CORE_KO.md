# Transported Prototype Listener Readout Core

## 한 줄 요약

Cross-subject transported prototype grammar를 하나의 global latent로 읽지 않고,
Q/S target listener별로 어떤 transported grammar view를 읽어야 하는지 frozen probe로 진단한 실험이다.

```text
train subjects define prototype grammar
  -> held-out rows receive transported prototype responsibilities
  -> target listener chooses a transported prototype view
```

## 판정

- verdict: `transported_listener_readout_global_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`

## 핵심 수치

- subject listener-conditioned logloss: `0.675348`
- subject global transport logloss: `0.676724`
- subject prior logloss: `0.677858`
- delta vs global transport: `-0.001376`
- delta vs prior: `-0.002509`
- row-block delta vs global transport: `0.000010`
- chronological delta vs global transport: `-0.000919`
- selected-route fold wins: `23 / 35`

## Target별 Listener View 선택

| target | selected_feature_set | selected_logloss | global_transport_logloss | delta_vs_global_transport |
| --- | --- | --- | --- | --- |
| Q1 | listener_view_mobility_environment_stats | 0.703784 | 0.707795 | -0.004011 |
| Q2 | listener_view_calendar_rhythm_stats | 0.693521 | 0.695594 | -0.002073 |
| Q3 | listener_view_app_social_context_probabilities | 0.679028 | 0.679294 | -0.000266 |
| S1 | listener_view_body_activity_sleep_stats_probabilities | 0.638590 | 0.640184 | -0.001593 |
| S2 | listener_view_calendar_rhythm_stats_probabilities | 0.657930 | 0.652743 | 0.005187 |
| S3 | listener_view_calendar_rhythm_stats_probabilities | 0.657502 | 0.665953 | -0.008451 |
| S4 | listener_view_calendar_rhythm_stats_probabilities | 0.697083 | 0.695505 | 0.001578 |

## Fold Stability

| target | selected_feature_set | mean_delta_vs_global | win_folds_vs_global | total_folds |
| --- | --- | --- | --- | --- |
| Q1 | listener_view_mobility_environment_stats | -0.004027 | 4 | 5 |
| Q2 | listener_view_calendar_rhythm_stats | -0.002072 | 4 | 5 |
| Q3 | listener_view_app_social_context_probabilities | -0.000261 | 3 | 5 |
| S1 | listener_view_body_activity_sleep_stats_probabilities | -0.001592 | 4 | 5 |
| S2 | listener_view_calendar_rhythm_stats_probabilities | 0.005223 | 1 | 5 |
| S3 | listener_view_calendar_rhythm_stats_probabilities | -0.008473 | 5 | 5 |
| S4 | listener_view_calendar_rhythm_stats_probabilities | 0.001597 | 2 | 5 |

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| listener_conditioned_transported_prototype_readout_calibrated10 | 0.675348 | 0.403342 |
| listener_view_mobility_environment_probabilities | 0.675961 | 0.474476 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated10 | 0.676707 | 0.397543 |
| transported_prototype_stats_probabilities_calibrated10 | 0.676724 | 0.400691 |
| calendar_rhythm_calibrated10 | 0.676787 | 0.402565 |
| listener_view_body_activity_sleep_stats_probabilities_calibrated10 | 0.676872 | 0.388260 |
| listener_view_mobility_environment_probabilities_calibrated10 | 0.676922 | 0.392908 |
| listener_view_mobility_environment_stats_probabilities_calibrated10 | 0.677107 | 0.389120 |
| transported_prototype_stats_probabilities_calibrated05 | 0.677120 | 0.387924 |
| listener_view_calendar_rhythm_stats_calibrated10 | 0.677156 | 0.395219 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated05 | 0.677226 | 0.390426 |
| transported_prototype_probabilities_calibrated10 | 0.677252 | 0.394541 |
| listener_view_body_activity_sleep_probabilities_calibrated10 | 0.677282 | 0.387583 |
| calendar_rhythm_calibrated05 | 0.677293 | 0.396052 |
| listener_view_body_activity_sleep_stats_probabilities_calibrated05 | 0.677326 | 0.384172 |
| listener_view_calendar_rhythm_probabilities_calibrated10 | 0.677350 | 0.387094 |
| listener_view_mobility_environment_probabilities_calibrated05 | 0.677369 | 0.387174 |
| listener_view_calendar_rhythm_stats | 0.677421 | 0.456960 |
| listener_view_app_social_context_probabilities_calibrated10 | 0.677430 | 0.394968 |
| transported_prototype_probabilities_calibrated05 | 0.677431 | 0.385015 |
| listener_view_mobility_environment_stats_probabilities_calibrated05 | 0.677452 | 0.384968 |
| transported_prototype_stats_calibrated10 | 0.677457 | 0.395582 |
| listener_view_calendar_rhythm_stats_calibrated05 | 0.677489 | 0.391311 |
| listener_view_body_activity_sleep_probabilities_calibrated05 | 0.677554 | 0.387103 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| raw_lifelog_pca_calibrated05 | 0.670991 | 0.447387 |
| transported_prototype_probabilities_calibrated10 | 0.673229 | 0.412043 |
| calendar_rhythm_calibrated10 | 0.673248 | 0.416598 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated10 | 0.673249 | 0.417726 |
| transported_prototype_stats_probabilities_calibrated10 | 0.673331 | 0.422598 |
| listener_conditioned_transported_prototype_readout_calibrated10 | 0.673341 | 0.414845 |
| listener_view_calendar_rhythm_stats_calibrated10 | 0.673433 | 0.417375 |
| transported_prototype_probabilities_calibrated05 | 0.673546 | 0.405155 |
| transported_prototype_stats_probabilities_calibrated05 | 0.673558 | 0.408898 |
| listener_view_app_social_context_probabilities_calibrated10 | 0.673597 | 0.403330 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated05 | 0.673626 | 0.410072 |
| calendar_rhythm_calibrated05 | 0.673631 | 0.410856 |
| listener_view_app_social_context_stats_probabilities_calibrated10 | 0.673667 | 0.402461 |
| listener_view_calendar_rhythm_stats | 0.673674 | 0.473643 |
| listener_view_calendar_rhythm_stats_calibrated05 | 0.673739 | 0.412626 |
| listener_view_mobility_environment_probabilities_calibrated10 | 0.673765 | 0.406051 |
| listener_view_app_social_context_probabilities_calibrated05 | 0.673820 | 0.400905 |
| listener_view_app_social_context_stats_probabilities_calibrated05 | 0.673846 | 0.398683 |
| listener_view_mobility_environment_probabilities_calibrated05 | 0.673905 | 0.404391 |
| listener_view_mobility_environment_stats_probabilities_calibrated10 | 0.673961 | 0.406172 |
| listener_view_body_activity_sleep_stats_calibrated10 | 0.673974 | 0.399771 |
| listener_view_body_activity_sleep_stats_probabilities_calibrated10 | 0.673987 | 0.399107 |
| listener_view_mobility_environment_stats_probabilities_calibrated05 | 0.673991 | 0.404438 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| raw_lifelog_pca_calibrated05 | 0.667603 | 0.603053 |
| calendar_rhythm_calibrated10 | 0.669335 | 0.547961 |
| listener_view_body_activity_sleep_stats | 0.669384 | 0.532051 |
| listener_view_body_activity_sleep_stats_probabilities_calibrated10 | 0.669476 | 0.552849 |
| calendar_rhythm_calibrated05 | 0.670047 | 0.547961 |
| calendar_rhythm | 0.670067 | 0.547961 |
| listener_view_body_activity_sleep_stats_probabilities_calibrated05 | 0.670111 | 0.552849 |
| listener_view_body_activity_sleep_stats_calibrated10 | 0.670163 | 0.532051 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated10 | 0.670191 | 0.519754 |
| listener_view_body_activity_sleep_probabilities_calibrated10 | 0.670261 | 0.534694 |
| listener_view_calendar_rhythm_stats_calibrated10 | 0.670267 | 0.512704 |
| listener_view_phone_behavior_stats_calibrated10 | 0.670319 | 0.528846 |
| transported_prototype_stats_calibrated10 | 0.670341 | 0.506034 |
| listener_view_calendar_rhythm_stats_probabilities_calibrated05 | 0.670460 | 0.519754 |
| transported_prototype_stats_calibrated05 | 0.670467 | 0.506034 |
| listener_view_body_activity_sleep_stats_calibrated05 | 0.670481 | 0.532051 |
| listener_view_calendar_rhythm_stats_calibrated05 | 0.670508 | 0.512704 |
| listener_view_body_activity_sleep_probabilities_calibrated05 | 0.670522 | 0.534694 |
| listener_view_phone_behavior_stats_calibrated05 | 0.670551 | 0.528846 |
| listener_conditioned_transported_prototype_readout_calibrated10 | 0.670618 | 0.515177 |
| listener_view_mobility_environment_probabilities_calibrated10 | 0.670757 | 0.505327 |
| listener_view_phone_behavior_stats_probabilities_calibrated05 | 0.670758 | 0.510824 |
| listener_view_phone_behavior_stats_probabilities_calibrated10 | 0.670763 | 0.510824 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| listener_view_calendar_rhythm_stats | 0.131111 | 0.126667 | 0.004444 |
| calendar_rhythm | 0.137778 | 0.126667 | 0.011111 |
| listener_view_app_social_context_stats | 0.140000 | 0.126667 | 0.013333 |
| listener_view_phone_behavior_stats | 0.142222 | 0.126667 | 0.015556 |
| listener_view_mobility_environment_stats | 0.164444 | 0.126667 | 0.037778 |
| listener_view_body_activity_sleep_stats | 0.171111 | 0.126667 | 0.044444 |
| transported_prototype_stats | 0.177778 | 0.126667 | 0.051111 |
| listener_view_app_social_context_stats_probabilities | 0.215556 | 0.126667 | 0.088889 |
| listener_view_body_activity_sleep_probabilities | 0.228889 | 0.126667 | 0.102222 |
| listener_view_body_activity_sleep_stats_probabilities | 0.228889 | 0.126667 | 0.102222 |
| listener_view_app_social_context_probabilities | 0.244444 | 0.126667 | 0.117778 |
| listener_view_calendar_rhythm_probabilities | 0.253333 | 0.126667 | 0.126667 |
| listener_view_calendar_rhythm_stats_probabilities | 0.273333 | 0.126667 | 0.146667 |
| listener_view_mobility_environment_probabilities | 0.284444 | 0.126667 | 0.157778 |
| listener_view_mobility_environment_stats_probabilities | 0.295556 | 0.126667 | 0.168889 |
| listener_view_phone_behavior_stats_probabilities | 0.384444 | 0.126667 | 0.257778 |
| listener_view_phone_behavior_probabilities | 0.397778 | 0.126667 | 0.271111 |
| transported_prototype_probabilities | 0.468889 | 0.126667 | 0.342222 |
| transported_prototype_stats_probabilities | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## 해석

positive이면 다음 주장이 강화된다.

```text
HS-JEPA의 transported prototype grammar는 하나의 global latent가 아니라
listener별로 읽어야 하는 human-state grammar interface다.
```

negative이면 다음 경계가 생긴다.

```text
cross-subject grammar transport는 존재하지만,
target별 listener readout은 현재 split에서는 과적합이거나 아직 약하다.
```
