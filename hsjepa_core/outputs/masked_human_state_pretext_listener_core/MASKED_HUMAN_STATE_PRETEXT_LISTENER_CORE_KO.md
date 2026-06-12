# Masked Human-State Pretext Listener Core

## 한 줄 요약

raw human-state feature를 그대로 decoder에 넣지 않고, 먼저 JEPA-style masked-view
pretext representation을 만든 뒤 subject-invariant action-health support를 읽는지 검증했다.

```text
visible lifelog views
  -> predict masked human-state view representation
  -> predicted/residual/surprise state
  -> listener-conditioned action-health support
```

## 왜 필요한 실험인가

`Open-Loop Human-State Listener Core`는 raw OG human-state가 action-only보다 낫지만
listener-only를 이기지 못한다는 경계 결과였다. 이 실험은 그 실패가
human-state 자체의 부재 때문인지, 아니면 representation화하지 않은 raw feature decoder 때문인지
반증한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- masked-tail teacher score as feature: `False`
- label-informed peer margin as feature: `False`

## Verdict

- verdict: `masked_pretext_improves_raw_human_state_but_not_listener_only`
- best strict-jury family: `listener_only`
- masked-pretext AP lift: `0.064389`
- open-loop AP lift: `0.062217`
- listener-only AP lift: `0.079972`
- action-only AP lift: `0.038054`
- release family: `masked_pretext_prediction_listener`
- released test cells: `67`
- candidate: `submission_hsjepa_masked_human_state_pretext_listener_anchor_free_c47e9223_uploadsafe.csv`

## Masked-View Pretext Metrics

| target_view | context_feature_count | target_feature_count | components | oof_r2 | oof_component_corr | train_energy_mean | test_energy_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_rhythm | 94 | 5 | 4 | -453.763173 | 0.004705 | 7.950124 | 1.017505 |
| phone_behavior | 59 | 40 | 4 | -150.628833 | 0.105008 | 9.245706 | 1.440984 |
| body_activity_sleep | 81 | 18 | 4 | -1481.296505 | -0.048899 | 19.492440 | 1.311194 |
| app_social_context | 81 | 18 | 4 | -0.132434 | 0.156728 | 1.630479 | 1.172112 |
| mobility_environment | 81 | 18 | 4 | -336.893778 | -0.053134 | 9.674250 | 0.994601 |

## Strict Jury Release Leaderboard

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| listener_only | strict_jury_released | 14 | 0.027619 | 0.737839 | 0.107591 | 0.079972 |
| masked_pretext_prediction_listener | strict_jury_released | 48 | 0.027619 | 0.691683 | 0.092009 | 0.064389 |
| open_loop_human_state_listener | strict_jury_released | 128 | 0.027619 | 0.711199 | 0.089836 | 0.062217 |
| human_plus_masked_pretext_listener | strict_jury_released | 182 | 0.027619 | 0.724119 | 0.078839 | 0.051220 |
| masked_pretext_residual_listener | strict_jury_released | 48 | 0.027619 | 0.698591 | 0.072919 | 0.045300 |
| masked_pretext_full_listener | strict_jury_released | 68 | 0.027619 | 0.689367 | 0.069992 | 0.042373 |
| action_geometry_only | strict_jury_released | 12 | 0.027619 | 0.744112 | 0.065673 | 0.038054 |

## Target-Level Strict Jury Release Metrics

| feature_family | target | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- |
| action_geometry_only | Q2 | 0.012222 | 0.831578 | 0.128963 | 0.116740 |
| action_geometry_only | S2 | 0.017778 | 0.617612 | 0.127296 | 0.109519 |
| action_geometry_only | S4 | 0.091111 | 0.743105 | 0.172022 | 0.080911 |
| action_geometry_only | Q3 | 0.033333 | 0.725345 | 0.066661 | 0.033328 |
| action_geometry_only | Q1 | 0.017778 | 0.686581 | 0.032300 | 0.014523 |
| action_geometry_only | S1 | 0.012222 | 0.634012 | 0.018885 | 0.006663 |
| action_geometry_only | S3 | 0.008889 | 0.409123 | 0.007907 | -0.000982 |
| human_plus_masked_pretext_listener | Q2 | 0.012222 | 0.616167 | 0.058133 | 0.045911 |
| human_plus_masked_pretext_listener | S4 | 0.091111 | 0.645201 | 0.132975 | 0.041864 |
| human_plus_masked_pretext_listener | Q1 | 0.017778 | 0.668870 | 0.053578 | 0.035801 |
| human_plus_masked_pretext_listener | Q3 | 0.033333 | 0.670728 | 0.067168 | 0.033835 |
| human_plus_masked_pretext_listener | S1 | 0.012222 | 0.793230 | 0.045076 | 0.032854 |
| human_plus_masked_pretext_listener | S3 | 0.008889 | 0.710762 | 0.016562 | 0.007673 |
| human_plus_masked_pretext_listener | S2 | 0.017778 | 0.366657 | 0.013680 | -0.004098 |
| listener_only | S4 | 0.091111 | 0.662219 | 0.160349 | 0.069238 |
| listener_only | S1 | 0.012222 | 0.767972 | 0.034248 | 0.022025 |
| listener_only | Q3 | 0.033333 | 0.623333 | 0.052517 | 0.019184 |
| listener_only | Q1 | 0.017778 | 0.520751 | 0.028483 | 0.010705 |
| listener_only | Q2 | 0.012222 | 0.696748 | 0.021538 | 0.009315 |
| listener_only | S3 | 0.008889 | 0.523122 | 0.009840 | 0.000952 |
| listener_only | S2 | 0.017778 | 0.467937 | 0.017398 | -0.000380 |
| masked_pretext_full_listener | S1 | 0.012222 | 0.647408 | 0.055423 | 0.043200 |
| masked_pretext_full_listener | S4 | 0.091111 | 0.645782 | 0.125058 | 0.033947 |
| masked_pretext_full_listener | Q3 | 0.033333 | 0.617835 | 0.054885 | 0.021552 |
| masked_pretext_full_listener | S2 | 0.017778 | 0.586609 | 0.024750 | 0.006972 |
| masked_pretext_full_listener | Q1 | 0.017778 | 0.545602 | 0.023894 | 0.006116 |
| masked_pretext_full_listener | S3 | 0.008889 | 0.478980 | 0.009687 | 0.000798 |
| masked_pretext_full_listener | Q2 | 0.012222 | 0.362665 | 0.009637 | -0.002586 |
| masked_pretext_prediction_listener | S4 | 0.091111 | 0.642995 | 0.168579 | 0.077468 |
| masked_pretext_prediction_listener | Q3 | 0.033333 | 0.668927 | 0.086621 | 0.053288 |
| masked_pretext_prediction_listener | Q1 | 0.017778 | 0.559000 | 0.037899 | 0.020121 |
| masked_pretext_prediction_listener | S1 | 0.012222 | 0.663002 | 0.029827 | 0.017604 |
| masked_pretext_prediction_listener | S3 | 0.008889 | 0.528798 | 0.018776 | 0.009887 |
| masked_pretext_prediction_listener | S2 | 0.017778 | 0.492824 | 0.026249 | 0.008471 |
| masked_pretext_prediction_listener | Q2 | 0.012222 | 0.534513 | 0.016292 | 0.004070 |
| masked_pretext_residual_listener | S4 | 0.091111 | 0.675137 | 0.147870 | 0.056759 |
| masked_pretext_residual_listener | S1 | 0.012222 | 0.751406 | 0.055199 | 0.042977 |
| masked_pretext_residual_listener | Q3 | 0.033333 | 0.665345 | 0.057015 | 0.023682 |
| masked_pretext_residual_listener | S2 | 0.017778 | 0.539876 | 0.018976 | 0.001198 |
| masked_pretext_residual_listener | Q2 | 0.012222 | 0.491103 | 0.013045 | 0.000823 |
| masked_pretext_residual_listener | S3 | 0.008889 | 0.429302 | 0.009142 | 0.000253 |
| masked_pretext_residual_listener | Q1 | 0.017778 | 0.477588 | 0.017121 | -0.000656 |
| open_loop_human_state_listener | Q2 | 0.012222 | 0.618775 | 0.102642 | 0.090420 |
| open_loop_human_state_listener | S4 | 0.091111 | 0.665066 | 0.151942 | 0.060831 |
| open_loop_human_state_listener | Q1 | 0.017778 | 0.682551 | 0.059413 | 0.041635 |
| open_loop_human_state_listener | S1 | 0.012222 | 0.711474 | 0.040431 | 0.028208 |
| open_loop_human_state_listener | Q3 | 0.033333 | 0.619923 | 0.053359 | 0.020025 |
| open_loop_human_state_listener | S3 | 0.008889 | 0.580087 | 0.014685 | 0.005796 |
| open_loop_human_state_listener | S2 | 0.017778 | 0.400276 | 0.015195 | -0.002583 |

## Fold Stability

| feature_family | label_task | fold | heldout_subjects | positive_rate | auc | ap |
| --- | --- | --- | --- | --- | --- | --- |
| listener_only | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.628213 | 0.025673 |
| listener_only | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.718852 | 0.064784 |
| listener_only | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.732818 | 0.133876 |
| listener_only | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.756677 | 0.239471 |
| listener_only | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.823692 | 0.277970 |
| listener_only | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.654748 | 0.015397 |
| listener_only | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.748394 | 0.030284 |
| listener_only | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.685456 | 0.068862 |
| listener_only | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.737549 | 0.068678 |
| listener_only | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.879825 | 0.186975 |
| listener_only | healthy_action | 0 | id03,id04 | 0.500000 | 0.497186 | 0.505016 |
| listener_only | healthy_action | 1 | id08,id10 | 0.500000 | 0.487985 | 0.493159 |
| listener_only | healthy_action | 2 | id01,id07 | 0.500000 | 0.465996 | 0.473542 |
| listener_only | healthy_action | 3 | id05,id06 | 0.500000 | 0.524751 | 0.504604 |
| listener_only | healthy_action | 4 | id02,id09 | 0.500000 | 0.472358 | 0.475539 |
| listener_only | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.635981 | 0.498937 |
| listener_only | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.628094 | 0.486582 |
| listener_only | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.617788 | 0.467494 |
| listener_only | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.692772 | 0.538138 |
| listener_only | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.638925 | 0.460361 |
| action_geometry_only | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.591698 | 0.030817 |
| action_geometry_only | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.768112 | 0.063691 |
| action_geometry_only | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.696243 | 0.068749 |
| action_geometry_only | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.807846 | 0.175560 |
| action_geometry_only | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.809989 | 0.105155 |
| action_geometry_only | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.692642 | 0.015772 |
| action_geometry_only | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.694772 | 0.028719 |
| action_geometry_only | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.647003 | 0.034186 |
| action_geometry_only | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.833805 | 0.049819 |
| action_geometry_only | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.774584 | 0.044908 |
| action_geometry_only | healthy_action | 0 | id03,id04 | 0.500000 | 0.597526 | 0.571743 |
| action_geometry_only | healthy_action | 1 | id08,id10 | 0.500000 | 0.547375 | 0.524976 |
| action_geometry_only | healthy_action | 2 | id01,id07 | 0.500000 | 0.544099 | 0.540336 |
| action_geometry_only | healthy_action | 3 | id05,id06 | 0.500000 | 0.555707 | 0.563673 |
| action_geometry_only | healthy_action | 4 | id02,id09 | 0.500000 | 0.577101 | 0.568010 |
| action_geometry_only | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.707416 | 0.568032 |
| action_geometry_only | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.685331 | 0.536020 |
| action_geometry_only | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.676978 | 0.524719 |
| action_geometry_only | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.702616 | 0.526759 |
| action_geometry_only | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.734589 | 0.565539 |
| open_loop_human_state_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.515696 | 0.017868 |
| open_loop_human_state_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.722825 | 0.076588 |
| open_loop_human_state_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.741297 | 0.122840 |
| open_loop_human_state_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.754737 | 0.202286 |
| open_loop_human_state_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.785518 | 0.179750 |
| open_loop_human_state_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.570146 | 0.012409 |
| open_loop_human_state_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.636222 | 0.032765 |
| open_loop_human_state_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.649452 | 0.052136 |
| open_loop_human_state_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.727468 | 0.112762 |
| open_loop_human_state_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.769469 | 0.106528 |
| open_loop_human_state_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.485954 | 0.496844 |
| open_loop_human_state_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.506798 | 0.505177 |
| open_loop_human_state_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.449583 | 0.463307 |
| open_loop_human_state_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.503343 | 0.498887 |
| open_loop_human_state_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.474568 | 0.477757 |
| open_loop_human_state_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.630809 | 0.497257 |
| open_loop_human_state_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.675306 | 0.540243 |
| open_loop_human_state_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.609114 | 0.456635 |
| open_loop_human_state_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.668494 | 0.503210 |
| open_loop_human_state_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.643194 | 0.470339 |
| masked_pretext_prediction_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.572606 | 0.024379 |
| masked_pretext_prediction_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.629351 | 0.070019 |
| masked_pretext_prediction_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.693566 | 0.146752 |
| masked_pretext_prediction_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.697922 | 0.177964 |
| masked_pretext_prediction_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.794798 | 0.184881 |
| masked_pretext_prediction_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.594151 | 0.013271 |
| masked_pretext_prediction_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.597105 | 0.058283 |
| masked_pretext_prediction_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.625275 | 0.071401 |
| masked_pretext_prediction_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.643991 | 0.027210 |
| masked_pretext_prediction_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.698769 | 0.072558 |
| masked_pretext_prediction_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.518553 | 0.519069 |
| masked_pretext_prediction_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.540289 | 0.525369 |
| masked_pretext_prediction_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.580894 | 0.584533 |
| masked_pretext_prediction_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.498013 | 0.492138 |
| masked_pretext_prediction_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.489399 | 0.485192 |
| masked_pretext_prediction_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.619530 | 0.486180 |
| masked_pretext_prediction_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.660470 | 0.537385 |
| masked_pretext_prediction_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.709293 | 0.576287 |
| masked_pretext_prediction_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.649079 | 0.484698 |
| masked_pretext_prediction_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.644547 | 0.465308 |
| masked_pretext_residual_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.582593 | 0.021641 |
| masked_pretext_residual_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.630076 | 0.041074 |
| masked_pretext_residual_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.665559 | 0.136875 |
| masked_pretext_residual_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.710610 | 0.165906 |
| masked_pretext_residual_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.816314 | 0.230739 |
| masked_pretext_residual_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.625534 | 0.015451 |
| masked_pretext_residual_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.598571 | 0.031549 |
| masked_pretext_residual_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.708343 | 0.075547 |
| masked_pretext_residual_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.685206 | 0.051240 |
| masked_pretext_residual_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.837033 | 0.092466 |
| masked_pretext_residual_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.569809 | 0.553874 |
| masked_pretext_residual_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.547706 | 0.541056 |
| masked_pretext_residual_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.564607 | 0.552445 |
| masked_pretext_residual_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.522860 | 0.519242 |
| masked_pretext_residual_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.505233 | 0.507392 |
| masked_pretext_residual_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.628678 | 0.493928 |
| masked_pretext_residual_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.664651 | 0.535433 |
| masked_pretext_residual_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.695390 | 0.550055 |
| masked_pretext_residual_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.652457 | 0.490458 |
| masked_pretext_residual_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.664331 | 0.506973 |

## Release Counts

| target | count |
| --- | --- |
| Q2 | 6 |
| S1 | 6 |
| S2 | 9 |
| S4 | 46 |

## 해석

좋은 결과:

```text
masked pretext state가 listener-only/open-loop raw human-state를 넘으면,
HS-JEPA core의 핵심은 raw feature가 아니라 masked human-state world model이라는 주장이 강화된다.
```

나쁜 결과:

```text
masked pretext state도 listener-only를 못 넘으면,
현재 core-only representation은 아직 subject-invariant action-health를 독립적으로 복원하지 못한다.
그 경우 strong evidence는 hidden-tail/listener manifold 쪽에 남는다.
```
