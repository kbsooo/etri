# Open-Loop Human-State Listener Core

## 한 줄 요약

masked-tail teacher와 action probability/magnitude를 빼고,
OG lifelog/social/cohort human-state와 minimal listener만으로 subject-invariant
action-health support가 분리되는지 검증했다.

```text
OG human-state context
  + target listener
  + raw/inverse action listener
  -> subject-invariant action-health support
```

## 빠른 판정

이 실험은 HS-JEPA core의 가장 엄격한 쪽 probe다.
성공하면 core representation이 teacher-free/open-loop 상태에서도 action-health의 일부를
읽는다는 뜻이고, 실패하면 현재 strong evidence가 masked-tail teacher에 크게 의존한다는 뜻이다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- masked-tail teacher score as feature: `False`
- label-informed peer margin as feature: `False`

## Verdict

- verdict: `open_loop_human_state_beats_action_but_not_listener_only`
- open-loop AP lift: `0.062217`
- listener-only AP lift: `0.079972`
- action-only AP lift: `0.038054`
- released test cells: `67`
- candidate: `submission_hsjepa_open_loop_human_state_listener_anchor_free_adfadd58_uploadsafe.csv`

## Strict Jury Release Leaderboard

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| listener_only | strict_jury_released | 14 | 0.027619 | 0.737839 | 0.107591 | 0.079972 |
| latent_cohort_listener | strict_jury_released | 29 | 0.027619 | 0.698289 | 0.090764 | 0.063145 |
| open_loop_human_state_listener | strict_jury_released | 128 | 0.027619 | 0.711199 | 0.089836 | 0.062217 |
| calendar_social_listener | strict_jury_released | 37 | 0.027619 | 0.709486 | 0.080895 | 0.053276 |
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
| calendar_social_listener | S4 | 0.091111 | 0.673482 | 0.137340 | 0.046228 |
| calendar_social_listener | S1 | 0.012222 | 0.690919 | 0.045487 | 0.033264 |
| calendar_social_listener | Q3 | 0.033333 | 0.641897 | 0.063073 | 0.029739 |
| calendar_social_listener | S3 | 0.008889 | 0.514084 | 0.025401 | 0.016512 |
| calendar_social_listener | Q1 | 0.017778 | 0.588553 | 0.023739 | 0.005961 |
| calendar_social_listener | S2 | 0.017778 | 0.504383 | 0.019071 | 0.001293 |
| calendar_social_listener | Q2 | 0.012222 | 0.463749 | 0.011959 | -0.000263 |
| latent_cohort_listener | S4 | 0.091111 | 0.662778 | 0.185339 | 0.094227 |
| latent_cohort_listener | Q2 | 0.012222 | 0.682534 | 0.027684 | 0.015462 |
| latent_cohort_listener | Q3 | 0.033333 | 0.606341 | 0.046387 | 0.013053 |
| latent_cohort_listener | S3 | 0.008889 | 0.575392 | 0.018973 | 0.010084 |
| latent_cohort_listener | S1 | 0.012222 | 0.652009 | 0.021314 | 0.009092 |
| latent_cohort_listener | Q1 | 0.017778 | 0.582827 | 0.026486 | 0.008708 |
| latent_cohort_listener | S2 | 0.017778 | 0.389989 | 0.015327 | -0.002451 |
| listener_only | S4 | 0.091111 | 0.662219 | 0.160349 | 0.069238 |
| listener_only | S1 | 0.012222 | 0.767972 | 0.034248 | 0.022025 |
| listener_only | Q3 | 0.033333 | 0.623333 | 0.052517 | 0.019184 |
| listener_only | Q1 | 0.017778 | 0.520751 | 0.028483 | 0.010705 |
| listener_only | Q2 | 0.012222 | 0.696748 | 0.021538 | 0.009315 |
| listener_only | S3 | 0.008889 | 0.523122 | 0.009840 | 0.000952 |
| listener_only | S2 | 0.017778 | 0.467937 | 0.017398 | -0.000380 |
| open_loop_human_state_listener | Q2 | 0.012222 | 0.618775 | 0.102642 | 0.090420 |
| open_loop_human_state_listener | S4 | 0.091111 | 0.665066 | 0.151942 | 0.060831 |
| open_loop_human_state_listener | Q1 | 0.017778 | 0.682551 | 0.059413 | 0.041635 |
| open_loop_human_state_listener | S1 | 0.012222 | 0.711474 | 0.040431 | 0.028208 |
| open_loop_human_state_listener | Q3 | 0.033333 | 0.619923 | 0.053359 | 0.020025 |
| open_loop_human_state_listener | S3 | 0.008889 | 0.580087 | 0.014685 | 0.005796 |
| open_loop_human_state_listener | S2 | 0.017778 | 0.400276 | 0.015195 | -0.002583 |

## All Label-Task Metrics

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| listener_only | strict_jury_released | 14 | 0.027619 | 0.737839 | 0.107591 | 0.079972 |
| listener_only | strict_positive_release | 14 | 0.014603 | 0.743296 | 0.054258 | 0.039655 |
| listener_only | healthy_action | 14 | 0.500000 | 0.487964 | 0.486301 | -0.013699 |
| listener_only | toxic_tail_action | 14 | 0.403333 | 0.643159 | 0.483853 | 0.080519 |
| calendar_social_listener | strict_jury_released | 37 | 0.027619 | 0.709486 | 0.080895 | 0.053276 |
| calendar_social_listener | strict_positive_release | 37 | 0.014603 | 0.667478 | 0.039480 | 0.024877 |
| calendar_social_listener | healthy_action | 37 | 0.500000 | 0.490193 | 0.495257 | -0.004743 |
| calendar_social_listener | toxic_tail_action | 37 | 0.403333 | 0.631157 | 0.482039 | 0.078706 |
| latent_cohort_listener | strict_jury_released | 29 | 0.027619 | 0.698289 | 0.090764 | 0.063145 |
| latent_cohort_listener | strict_positive_release | 29 | 0.014603 | 0.680438 | 0.041325 | 0.026722 |
| latent_cohort_listener | healthy_action | 29 | 0.500000 | 0.482391 | 0.487821 | -0.012179 |
| latent_cohort_listener | toxic_tail_action | 29 | 0.403333 | 0.625981 | 0.474093 | 0.070759 |
| open_loop_human_state_listener | strict_jury_released | 128 | 0.027619 | 0.711199 | 0.089836 | 0.062217 |
| open_loop_human_state_listener | strict_positive_release | 128 | 0.014603 | 0.660442 | 0.036191 | 0.021587 |
| open_loop_human_state_listener | healthy_action | 128 | 0.500000 | 0.484887 | 0.485687 | -0.014313 |
| open_loop_human_state_listener | toxic_tail_action | 128 | 0.403333 | 0.643523 | 0.485839 | 0.082505 |
| action_geometry_only | strict_jury_released | 12 | 0.027619 | 0.744112 | 0.065673 | 0.038054 |
| action_geometry_only | strict_positive_release | 12 | 0.014603 | 0.729558 | 0.029155 | 0.014552 |
| action_geometry_only | healthy_action | 12 | 0.500000 | 0.561444 | 0.547904 | 0.047904 |
| action_geometry_only | toxic_tail_action | 12 | 0.403333 | 0.699676 | 0.541186 | 0.137853 |

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
| calendar_social_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.539874 | 0.019889 |
| calendar_social_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.722683 | 0.045761 |
| calendar_social_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.720301 | 0.117284 |
| calendar_social_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.698918 | 0.122104 |
| calendar_social_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.809068 | 0.265573 |
| calendar_social_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.598691 | 0.013870 |
| calendar_social_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.588933 | 0.034487 |
| calendar_social_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.674209 | 0.070345 |
| calendar_social_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.673841 | 0.038542 |
| calendar_social_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.764508 | 0.115316 |
| calendar_social_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.529468 | 0.521078 |
| calendar_social_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.497472 | 0.506214 |
| calendar_social_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.443479 | 0.460532 |
| calendar_social_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.502187 | 0.511406 |
| calendar_social_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.489470 | 0.494873 |
| calendar_social_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.627351 | 0.493541 |
| calendar_social_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.641816 | 0.502070 |
| calendar_social_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.615957 | 0.465673 |
| calendar_social_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.619498 | 0.456210 |
| calendar_social_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.651426 | 0.489421 |
| latent_cohort_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.570605 | 0.021385 |
| latent_cohort_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.710214 | 0.081596 |
| latent_cohort_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.736838 | 0.090408 |
| latent_cohort_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.705015 | 0.131284 |
| latent_cohort_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.777897 | 0.202750 |
| latent_cohort_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.622796 | 0.013655 |
| latent_cohort_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.621436 | 0.106882 |
| latent_cohort_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.682195 | 0.064634 |
| latent_cohort_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.694161 | 0.053711 |
| latent_cohort_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.797753 | 0.090227 |
| latent_cohort_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.516163 | 0.506919 |
| latent_cohort_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.489465 | 0.509560 |
| latent_cohort_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.467846 | 0.478311 |
| latent_cohort_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.463492 | 0.477979 |
| latent_cohort_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.484527 | 0.487558 |
| latent_cohort_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.625184 | 0.492896 |
| latent_cohort_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.625607 | 0.493283 |
| latent_cohort_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.599957 | 0.451965 |
| latent_cohort_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.647175 | 0.484202 |
| latent_cohort_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.655744 | 0.487480 |
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
open-loop human-state listener가 listener-only와 action-only를 이기면,
HS-JEPA core가 teacher 없이도 human-state/action-health support의 일부를 잡는다.
```

나쁜 결과:

```text
open-loop가 약하고 masked-tail representation만 강하면,
현재 HS-JEPA의 release-grade 성과는 아직 teacher/action-tail representation에 의존한다.
논문에서는 open-loop core와 teacher-derived tail field를 분리해서 말해야 한다.
```
