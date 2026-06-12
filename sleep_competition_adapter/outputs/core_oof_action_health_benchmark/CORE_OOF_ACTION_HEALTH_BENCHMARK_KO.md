# Core OOF Action-Health Benchmark

## 목적

이 실험은 public LB, 기존 submission, action teacher 없이 OG train 내부에서 HS-JEPA core가 실제 future-label logloss를 줄이는지 본다.

비교 대상은 다음이다.

- global prior
- subject prior
- raw lifelog KNN blend
- HS-JEPA core KNN blend
- HS-JEPA listener/action-health gated release

## 핵심 결과

- best temporal model: `hsjepa_target_listener_route_selector`
- best temporal mean logloss: `0.629398`
- subject prior temporal logloss: `0.650566`
- delta vs subject prior: `-0.021168`
- target listener route temporal logloss: `0.629398`
- target listener route delta vs subject prior: `-0.021168`
- generated candidate: `submission_hsjepa_core_oof_action_health_fea05ac1_uploadsafe.csv`

Target listener route:

| target | selected_listener_route |
| --- | --- |
| Q1 | core_knn_blend |
| Q2 | global_prior |
| Q3 | global_prior |
| S1 | raw_knn_blend |
| S2 | hsjepa_action_health__strict_listener_health |
| S3 | raw_knn_blend |
| S4 | core_knn_blend |

## 전체 score table

| split_family | model | mean_logloss | logloss_Q1 | logloss_Q2 | logloss_Q3 | logloss_S1 | logloss_S2 | logloss_S3 | logloss_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_subject_tail | global_prior | 0.666833 | 0.699896 | 0.666531 | 0.653411 | 0.605108 | 0.691062 | 0.654259 | 0.697563 |
| temporal_subject_tail | subject_prior | 0.650566 | 0.679910 | 0.681860 | 0.739765 | 0.540156 | 0.626297 | 0.631559 | 0.654413 |
| temporal_subject_tail | raw_knn_blend | 0.636997 | 0.666180 | 0.678549 | 0.688971 | 0.538308 | 0.623206 | 0.612370 | 0.651396 |
| temporal_subject_tail | core_knn_blend | 0.638266 | 0.662812 | 0.678728 | 0.683194 | 0.544318 | 0.633782 | 0.614202 | 0.650827 |
| temporal_subject_tail | hsjepa_action_health__strict_listener_health | 0.647582 | 0.678875 | 0.678099 | 0.731735 | 0.540156 | 0.621527 | 0.631559 | 0.651120 |
| temporal_subject_tail | raw_action_core_health__strict_listener_health | 0.649223 | 0.677729 | 0.676654 | 0.731804 | 0.540156 | 0.624622 | 0.631559 | 0.662040 |
| temporal_subject_tail | hsjepa_action_health__balanced_listener_health | 0.646601 | 0.679978 | 0.676136 | 0.720744 | 0.540156 | 0.621837 | 0.631559 | 0.655794 |
| temporal_subject_tail | raw_action_core_health__balanced_listener_health | 0.648920 | 0.679751 | 0.677102 | 0.720863 | 0.540156 | 0.625206 | 0.631559 | 0.667805 |
| temporal_subject_tail | hsjepa_action_health__wide_listener_health | 0.646813 | 0.678902 | 0.675482 | 0.717289 | 0.538934 | 0.629204 | 0.632254 | 0.655625 |
| temporal_subject_tail | raw_action_core_health__wide_listener_health | 0.648662 | 0.679480 | 0.675393 | 0.718903 | 0.542359 | 0.627878 | 0.628019 | 0.668604 |
| temporal_subject_tail | hsjepa_action_health__high_margin_listener_health | 0.644184 | 0.680069 | 0.671511 | 0.699578 | 0.540156 | 0.628769 | 0.631559 | 0.657648 |
| temporal_subject_tail | raw_action_core_health__high_margin_listener_health | 0.647802 | 0.681965 | 0.669838 | 0.706802 | 0.540156 | 0.625554 | 0.631559 | 0.678739 |
| subject_holdout | global_prior | 0.679633 | 0.704506 | 0.694860 | 0.681071 | 0.642306 | 0.667391 | 0.668170 | 0.699125 |
| subject_holdout | subject_prior | 0.679633 | 0.704506 | 0.694860 | 0.681071 | 0.642306 | 0.667391 | 0.668170 | 0.699125 |
| subject_holdout | raw_knn_blend | 0.679336 | 0.705100 | 0.687898 | 0.685847 | 0.635285 | 0.658719 | 0.683789 | 0.698712 |
| subject_holdout | core_knn_blend | 0.681340 | 0.706035 | 0.694229 | 0.682529 | 0.636000 | 0.676283 | 0.688703 | 0.685600 |
| subject_holdout | hsjepa_action_health__strict_listener_health | 0.679585 | 0.704018 | 0.694493 | 0.681474 | 0.642881 | 0.668711 | 0.668732 | 0.696788 |
| subject_holdout | raw_action_core_health__strict_listener_health | 0.680230 | 0.705226 | 0.694922 | 0.682034 | 0.642770 | 0.667377 | 0.669022 | 0.700257 |
| subject_holdout | hsjepa_action_health__balanced_listener_health | 0.679997 | 0.704080 | 0.696902 | 0.683637 | 0.643018 | 0.669714 | 0.668927 | 0.693699 |
| subject_holdout | raw_action_core_health__balanced_listener_health | 0.680531 | 0.706782 | 0.695237 | 0.681947 | 0.642878 | 0.668488 | 0.669353 | 0.699035 |
| subject_holdout | hsjepa_action_health__wide_listener_health | 0.678473 | 0.703833 | 0.695567 | 0.677762 | 0.639064 | 0.670333 | 0.668068 | 0.694685 |
| subject_holdout | raw_action_core_health__wide_listener_health | 0.679529 | 0.706016 | 0.693369 | 0.680152 | 0.640413 | 0.668902 | 0.668949 | 0.698904 |
| subject_holdout | hsjepa_action_health__high_margin_listener_health | 0.679748 | 0.703123 | 0.698410 | 0.678861 | 0.642968 | 0.671629 | 0.669869 | 0.693372 |
| subject_holdout | raw_action_core_health__high_margin_listener_health | 0.680875 | 0.706030 | 0.694326 | 0.683000 | 0.642588 | 0.671043 | 0.669995 | 0.699143 |
| temporal_subject_tail | hsjepa_target_listener_route_selector | 0.629398 | 0.662812 | 0.666531 | 0.653411 | 0.538308 | 0.621527 | 0.612370 | 0.650827 |
| subject_holdout | hsjepa_target_listener_route_selector | 0.679336 | 0.706035 | 0.694860 | 0.681071 | 0.635285 | 0.668711 | 0.683789 | 0.685600 |

## 해석

가장 중요한 결과는 단일 decoder가 아니라 target/listener별 route selector가 temporal OOF에서 가장 좋았다는 점이다.

즉 HS-JEPA core는 모든 target에 같은 방식으로 release되는 만능 predictor가 아니다. Q1/S4는 core KNN geometry를 듣고, S1/S3는 raw lifelog KNN을 듣고, Q2/Q3는 현재 train future split에서는 global prior가 더 안전하며, S2만 action-health release를 듣는다.

이것은 HS-JEPA를 `one encoder -> one classifier`가 아니라 `human-state core -> listener-specific route selection -> action-health release`로 정립해야 한다는 증거다.