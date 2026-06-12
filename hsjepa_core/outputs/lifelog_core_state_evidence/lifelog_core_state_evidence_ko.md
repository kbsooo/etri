# HS-JEPA Lifelog Core State Evidence

## 목적

이 실험은 public LB나 제출 점수표를 쓰지 않고, OG lifelog에서 만든 HS-JEPA human-state representation이 실제로 인간 생활 상태를 더 잘 표현하는지 확인한다.

핵심 질문은 두 개다.

1. label을 직접 맞히기 전에, raw lifelog context가 보이지 않는 human-state representation으로 압축되는가?
2. 그 representation이 target manifold, masked view prediction, neighbor consistency, external action replay에서 살아남는가?

## 입력과 분리 원칙

- feature source: `team_experiments/cohort_hsjepa/cohort_human_state_features.csv`
- public score ledger 사용: `False`
- proprietary embedding API 사용: `False`
- raw/core feature 수: raw `99`, core-state `15`
- core-only 검증에서 제외한 label-informed feature: `peer_margin_Q1, peer_margin_Q2, peer_margin_Q3, peer_margin_S1, peer_margin_S2, peer_margin_S3, peer_margin_S4, target_route_margin_q2q3s2`

## 핵심 결과

- grouped label probe에서 prior mean logloss는 `0.677858`이고, HS-JEPA state-only mean logloss는 `0.730555`이다.
- HS-JEPA state-only의 prior 대비 변화는 `0.052697`이다. 이 값이 음수이면 label을 직접 쓰지 않은 state representation만으로도 target manifold 일부를 설명한다.
- latent nearest-neighbor target match lift는 `0.050603`이다.
- masked context prediction에서 가장 잘 살아난 target view는 `phone_behavior`이고, null 대비 R2 lift는 `20.928748`, component-corr lift는 `0.380375`이다.
- external action replay에서 core-state geometry 평균 row AUC는 `0.954311`, 평균 recall@k는 `0.838594`이다. 이 항목은 core 학습이 아니라 adapter replay 진단이다.

## Label Manifold Probe

같은 subject가 fold 양쪽에 동시에 들어가지 않도록 GroupKFold로 검증했다.

| feature_set | mean_logloss | mean_auc |
| --- | --- | --- |
| prior_only | 0.677858 | 0.382414 |
| calendar_rhythm_linear | 0.678833 | 0.481425 |
| hsjepa_state_only_tree | 0.730555 | 0.503440 |
| raw_plus_hsjepa_state_tree | 0.736790 | 0.493310 |
| hsjepa_state_only_linear | 0.769864 | 0.488754 |
| raw_lifelog_views_linear | 1.452717 | 0.506239 |
| raw_plus_hsjepa_state_linear | 1.478114 | 0.515446 |

## Masked Context → Target View Prediction

I-JEPA식으로 한 view를 가리고, 나머지 lifelog view에서 가려진 view의 PCA representation을 예측했다. raw value 복원이 아니라 view-level representation prediction이다.

| target_view | context_feature_count | target_feature_count | mean_r2 | mean_null_r2 | r2_lift_vs_null | mean_component_corr | component_corr_lift_vs_null |
| --- | --- | --- | --- | --- | --- | --- | --- |
| phone_behavior | 59 | 40 | -2.884497 | -23.813244 | 20.928748 | 0.356871 | 0.380375 |
| body_activity_sleep | 81 | 18 | -22.150160 | -41.974094 | 19.823934 | 0.268730 | 0.260881 |
| app_social_context | 81 | 18 | -0.563292 | -0.573111 | 0.009818 | 0.336699 | 0.360004 |
| mobility_environment | 81 | 18 | -12.300181 | -11.172672 | -1.127510 | 0.327065 | 0.335219 |
| calendar_rhythm | 94 | 5 | -24.026399 | -10.761033 | -13.265366 | 0.045320 | 0.044661 |

## Nearest-Neighbor Label Consistency

좋은 human-state latent라면 가까운 이웃의 target vector도 random 이웃보다 더 비슷해야 한다.

| representation | neighbor_match_rate | random_match_rate | lift |
| --- | --- | --- | --- |
| calendar_rhythm | 0.586159 | 0.528571 | 0.057587 |
| hsjepa_state_only | 0.577333 | 0.526730 | 0.050603 |
| raw_lifelog_pca8 | 0.575937 | 0.526032 | 0.049905 |

## Human-State Outlier Shift

cohort/personal outlier score 상위 25%와 하위 25% 사이에서 target prevalence가 달라지는지 본다.

| score | target | low_quantile_rate | high_quantile_rate | absolute_shift | direction |
| --- | --- | --- | --- | --- | --- |
| dist_to_peer_normal | S4 | 0.477876 | 0.637168 | 0.159292 | higher_in_outliers |
| cohort_outlier_score | S4 | 0.486726 | 0.619469 | 0.132743 | higher_in_outliers |
| dist_to_subject_normal | Q3 | 0.513274 | 0.637168 | 0.123894 | higher_in_outliers |
| dist_to_peer_normal | S2 | 0.566372 | 0.681416 | 0.115044 | higher_in_outliers |
| dist_to_peer_normal | S1 | 0.734513 | 0.628319 | 0.106195 | lower_in_outliers |
| dist_to_subject_normal | S3 | 0.672566 | 0.575221 | 0.097345 | lower_in_outliers |
| cohort_outlier_score | S2 | 0.584071 | 0.672566 | 0.088496 | higher_in_outliers |
| cohort_outlier_score | Q2 | 0.504425 | 0.584071 | 0.079646 | higher_in_outliers |
| dist_to_subject_normal | S4 | 0.530973 | 0.601770 | 0.070796 | higher_in_outliers |
| cohort_outlier_score | S1 | 0.699115 | 0.628319 | 0.070796 | lower_in_outliers |
| dist_to_peer_normal | Q2 | 0.504425 | 0.566372 | 0.061947 | higher_in_outliers |
| dist_to_subject_normal | Q2 | 0.513274 | 0.575221 | 0.061947 | higher_in_outliers |
| dist_to_peer_normal | Q3 | 0.610619 | 0.557522 | 0.053097 | lower_in_outliers |
| dist_to_subject_normal | Q1 | 0.460177 | 0.504425 | 0.044248 | higher_in_outliers |

## External Adapter Action Replay

이 부분은 core-only 성능 증명이 아니라 adapter replay다. public score는 쓰지 않지만, 기존 row-action teacher가 고른 row를 외부 label로 두고 core state가 다른 teacher의 row support를 재발견하는지 본다.

| train_teacher | test_teacher | feature_set | row_auc | row_average_precision | row_recall_at_k | auc_z_vs_permuted_train |
| --- | --- | --- | --- | --- | --- | --- |
| stagebridge_jackpot | s2hub_jackpot | raw_lifelog_context | 0.982162 | 0.798152 | 0.823529 | 8.809317 |
| stagebridge_jackpot | s2hub_jackpot | core_plus_raw_context | 0.981890 | 0.784901 | 0.852941 | 9.396606 |
| stagebridge_jackpot | s2hub_jackpot | core_state_geometry | 0.980392 | 0.818120 | 0.823529 | 8.745216 |
| stagebridge_jackpot | s2hub_jackpot | label_informed_adapter_context | 0.977669 | 0.760519 | 0.823529 | 8.980982 |
| s2hub_jackpot | stagebridge_jackpot | raw_lifelog_context | 0.938149 | 0.912516 | 0.853659 | 8.890243 |
| s2hub_jackpot | stagebridge_jackpot | core_plus_raw_context | 0.935348 | 0.906865 | 0.853659 | 7.491064 |
| s2hub_jackpot | stagebridge_jackpot | label_informed_adapter_context | 0.929513 | 0.905709 | 0.853659 | 8.260818 |
| s2hub_jackpot | stagebridge_jackpot | core_state_geometry | 0.928230 | 0.898874 | 0.853659 | 8.006483 |

## 해석

이 실험의 논문적 의미는 HS-JEPA가 특정 제출 파일을 만드는 요령이 아니라, 원천 생활 로그를 hidden human-state space로 보내고 그 공간에서 target/action 구조를 읽는 일반 절차라는 점을 검증하는 것이다.

다만 external action replay는 아직 competition adapter 영역이다. 논문 본문에서는 core evidence와 adapter evidence를 분리해서 제시해야 한다.
