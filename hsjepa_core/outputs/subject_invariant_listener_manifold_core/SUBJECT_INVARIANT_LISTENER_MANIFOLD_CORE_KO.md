# Subject-Invariant Listener Manifold Core

## 한 줄 요약

subject-invariant jury가 고른 action-health가 단순 rule인지, 아니면 HS-JEPA hidden
representation 공간에서 subject를 넘어 분리되는지 검증했다.

```text
HS-JEPA hidden representation
  -> subject-heldout listener/action-health separability probe
  -> learned listener-manifold release score
  -> sparse diagnostic correction
```

## 빠른 판정

이 실험은 HS-JEPA core 자체를 직접 label classifier로 쓰는 실험이 아니다.
정확히는 **core representation이 adapter가 찾은 성공/실패 action-health를 재현 가능한
manifold로 담고 있는지** 확인하는 representation probe다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `hsjepa_listener_manifold_beats_action_geometry`
- best strict-jury family: `full_decoder_context`
- best strict-jury AP lift: `0.234538`
- HS-JEPA listener AP lift: `0.233257`
- action-only AP lift: `0.041516`
- released test cells: `67`
- candidate: `submission_hsjepa_subject_invariant_listener_manifold_anchor_free_40628330_uploadsafe.csv`

## Strict Jury Release Manifold Leaderboard

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| full_decoder_context | strict_jury_released | 129 | 0.027619 | 0.915401 | 0.262157 | 0.234538 |
| hsjepa_listener_manifold | strict_jury_released | 119 | 0.027619 | 0.913526 | 0.260876 | 0.233257 |
| masked_tail_representation | strict_jury_released | 27 | 0.027619 | 0.895612 | 0.183365 | 0.155746 |
| world_episode_minimal_listener | strict_jury_released | 92 | 0.027619 | 0.687395 | 0.075968 | 0.048349 |
| action_geometry_only | strict_jury_released | 13 | 0.027619 | 0.748687 | 0.069135 | 0.041516 |

## Target-Level Strict Jury Release Metrics

| feature_family | target | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- |
| action_geometry_only | S2 | 0.017778 | 0.635464 | 0.227485 | 0.209707 |
| action_geometry_only | S4 | 0.091111 | 0.768740 | 0.195028 | 0.103917 |
| action_geometry_only | Q2 | 0.012222 | 0.840884 | 0.065791 | 0.053569 |
| action_geometry_only | Q3 | 0.033333 | 0.716858 | 0.061751 | 0.028418 |
| action_geometry_only | Q1 | 0.017778 | 0.652043 | 0.028536 | 0.010758 |
| action_geometry_only | S1 | 0.012222 | 0.679057 | 0.021615 | 0.009392 |
| action_geometry_only | S3 | 0.008889 | 0.528587 | 0.010997 | 0.002108 |
| full_decoder_context | S2 | 0.017778 | 0.929157 | 0.435941 | 0.418163 |
| full_decoder_context | Q3 | 0.033333 | 0.860651 | 0.291737 | 0.258403 |
| full_decoder_context | S4 | 0.091111 | 0.898287 | 0.340988 | 0.249877 |
| full_decoder_context | S3 | 0.008889 | 0.922646 | 0.216086 | 0.207198 |
| full_decoder_context | Q1 | 0.017778 | 0.806844 | 0.171730 | 0.153953 |
| full_decoder_context | S1 | 0.012222 | 0.941661 | 0.161726 | 0.149504 |
| full_decoder_context | Q2 | 0.012222 | 0.894826 | 0.059281 | 0.047059 |
| hsjepa_listener_manifold | S2 | 0.017778 | 0.945065 | 0.431960 | 0.414182 |
| hsjepa_listener_manifold | Q3 | 0.033333 | 0.872299 | 0.393644 | 0.360311 |
| hsjepa_listener_manifold | S4 | 0.091111 | 0.889461 | 0.335838 | 0.244727 |
| hsjepa_listener_manifold | S1 | 0.012222 | 0.949893 | 0.205826 | 0.193604 |
| hsjepa_listener_manifold | S3 | 0.008889 | 0.878503 | 0.139536 | 0.130647 |
| hsjepa_listener_manifold | Q1 | 0.017778 | 0.795638 | 0.136917 | 0.119139 |
| hsjepa_listener_manifold | Q2 | 0.012222 | 0.874323 | 0.059474 | 0.047252 |
| masked_tail_representation | S4 | 0.091111 | 0.914671 | 0.438508 | 0.347397 |
| masked_tail_representation | Q3 | 0.033333 | 0.858257 | 0.240523 | 0.207190 |
| masked_tail_representation | S2 | 0.017778 | 0.903422 | 0.196617 | 0.178839 |
| masked_tail_representation | S1 | 0.012222 | 0.953472 | 0.145202 | 0.132979 |
| masked_tail_representation | S3 | 0.008889 | 0.887752 | 0.095296 | 0.086408 |
| masked_tail_representation | Q2 | 0.012222 | 0.881992 | 0.073023 | 0.060801 |
| masked_tail_representation | Q1 | 0.017778 | 0.815187 | 0.069233 | 0.051455 |
| world_episode_minimal_listener | S4 | 0.091111 | 0.641526 | 0.132780 | 0.041669 |
| world_episode_minimal_listener | S1 | 0.012222 | 0.744043 | 0.032558 | 0.020336 |
| world_episode_minimal_listener | Q3 | 0.033333 | 0.602490 | 0.048063 | 0.014730 |
| world_episode_minimal_listener | S2 | 0.017778 | 0.552390 | 0.025634 | 0.007856 |
| world_episode_minimal_listener | Q1 | 0.017778 | 0.517746 | 0.021402 | 0.003624 |
| world_episode_minimal_listener | S3 | 0.008889 | 0.437430 | 0.008500 | -0.000389 |
| world_episode_minimal_listener | Q2 | 0.012222 | 0.419982 | 0.010639 | -0.001583 |

## All Label-Task Metrics

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| action_geometry_only | strict_jury_released | 13 | 0.027619 | 0.748687 | 0.069135 | 0.041516 |
| action_geometry_only | strict_positive_release | 13 | 0.014603 | 0.741062 | 0.033252 | 0.018649 |
| action_geometry_only | healthy_action | 13 | 0.500000 | 0.581974 | 0.568410 | 0.068410 |
| action_geometry_only | toxic_tail_action | 13 | 0.403333 | 0.704541 | 0.552175 | 0.148842 |
| masked_tail_representation | strict_jury_released | 27 | 0.027619 | 0.895612 | 0.183365 | 0.155746 |
| masked_tail_representation | strict_positive_release | 27 | 0.014603 | 0.873898 | 0.112763 | 0.098159 |
| masked_tail_representation | healthy_action | 27 | 0.500000 | 0.522211 | 0.526832 | 0.026832 |
| masked_tail_representation | toxic_tail_action | 27 | 0.403333 | 0.663851 | 0.506572 | 0.103239 |
| world_episode_minimal_listener | strict_jury_released | 92 | 0.027619 | 0.687395 | 0.075968 | 0.048349 |
| world_episode_minimal_listener | strict_positive_release | 92 | 0.014603 | 0.687086 | 0.039355 | 0.024751 |
| world_episode_minimal_listener | healthy_action | 92 | 0.500000 | 0.508722 | 0.504960 | 0.004960 |
| world_episode_minimal_listener | toxic_tail_action | 92 | 0.403333 | 0.636924 | 0.484597 | 0.081263 |
| hsjepa_listener_manifold | strict_jury_released | 119 | 0.027619 | 0.913526 | 0.260876 | 0.233257 |
| hsjepa_listener_manifold | strict_positive_release | 119 | 0.014603 | 0.896240 | 0.128296 | 0.113692 |
| hsjepa_listener_manifold | healthy_action | 119 | 0.500000 | 0.510403 | 0.507834 | 0.007834 |
| hsjepa_listener_manifold | toxic_tail_action | 119 | 0.403333 | 0.658818 | 0.497350 | 0.094017 |
| full_decoder_context | strict_jury_released | 129 | 0.027619 | 0.915401 | 0.262157 | 0.234538 |
| full_decoder_context | strict_positive_release | 129 | 0.014603 | 0.898753 | 0.129548 | 0.114945 |
| full_decoder_context | healthy_action | 129 | 0.500000 | 0.571501 | 0.565140 | 0.065140 |
| full_decoder_context | toxic_tail_action | 129 | 0.403333 | 0.700816 | 0.552998 | 0.149665 |

## Fold Stability

| feature_family | label_task | fold | heldout_subjects | positive_rate | auc | ap |
| --- | --- | --- | --- | --- | --- | --- |
| action_geometry_only | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.626505 | 0.027293 |
| action_geometry_only | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.762926 | 0.078077 |
| action_geometry_only | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.658370 | 0.063277 |
| action_geometry_only | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.803320 | 0.170298 |
| action_geometry_only | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.833347 | 0.103490 |
| action_geometry_only | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.678853 | 0.015067 |
| action_geometry_only | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.741656 | 0.035374 |
| action_geometry_only | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.667498 | 0.058865 |
| action_geometry_only | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.796439 | 0.091890 |
| action_geometry_only | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.807880 | 0.064654 |
| action_geometry_only | healthy_action | 0 | id03,id04 | 0.500000 | 0.597023 | 0.586120 |
| action_geometry_only | healthy_action | 1 | id08,id10 | 0.500000 | 0.573206 | 0.553118 |
| action_geometry_only | healthy_action | 2 | id01,id07 | 0.500000 | 0.593748 | 0.575901 |
| action_geometry_only | healthy_action | 3 | id05,id06 | 0.500000 | 0.566230 | 0.566608 |
| action_geometry_only | healthy_action | 4 | id02,id09 | 0.500000 | 0.582501 | 0.585505 |
| action_geometry_only | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.711981 | 0.582569 |
| action_geometry_only | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.694081 | 0.547243 |
| action_geometry_only | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.721288 | 0.587646 |
| action_geometry_only | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.700111 | 0.534012 |
| action_geometry_only | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.708292 | 0.541232 |
| masked_tail_representation | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.852695 | 0.132613 |
| masked_tail_representation | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.870397 | 0.192700 |
| masked_tail_representation | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.890319 | 0.267071 |
| masked_tail_representation | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.908255 | 0.203859 |
| masked_tail_representation | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.956067 | 0.379122 |
| masked_tail_representation | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.846755 | 0.117188 |
| masked_tail_representation | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.867490 | 0.232941 |
| masked_tail_representation | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.848968 | 0.149887 |
| masked_tail_representation | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.912543 | 0.169608 |
| masked_tail_representation | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.913956 | 0.139898 |
| masked_tail_representation | healthy_action | 0 | id03,id04 | 0.500000 | 0.514118 | 0.531970 |
| masked_tail_representation | healthy_action | 1 | id08,id10 | 0.500000 | 0.542648 | 0.529855 |
| masked_tail_representation | healthy_action | 2 | id01,id07 | 0.500000 | 0.500266 | 0.518365 |
| masked_tail_representation | healthy_action | 3 | id05,id06 | 0.500000 | 0.506410 | 0.519964 |
| masked_tail_representation | healthy_action | 4 | id02,id09 | 0.500000 | 0.540452 | 0.549490 |
| masked_tail_representation | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.650351 | 0.513459 |
| masked_tail_representation | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.661235 | 0.529686 |
| masked_tail_representation | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.644025 | 0.483572 |
| masked_tail_representation | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.658152 | 0.500217 |
| masked_tail_representation | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.708100 | 0.539133 |
| world_episode_minimal_listener | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.563427 | 0.021631 |
| world_episode_minimal_listener | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.607598 | 0.037091 |
| world_episode_minimal_listener | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.696297 | 0.141493 |
| world_episode_minimal_listener | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.653497 | 0.174006 |
| world_episode_minimal_listener | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.815849 | 0.196305 |
| world_episode_minimal_listener | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.631744 | 0.016863 |
| world_episode_minimal_listener | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.637033 | 0.029517 |
| world_episode_minimal_listener | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.688370 | 0.052825 |
| world_episode_minimal_listener | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.684734 | 0.056119 |
| world_episode_minimal_listener | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.835498 | 0.143730 |
| world_episode_minimal_listener | healthy_action | 0 | id03,id04 | 0.500000 | 0.511004 | 0.503864 |
| world_episode_minimal_listener | healthy_action | 1 | id08,id10 | 0.500000 | 0.505421 | 0.511436 |
| world_episode_minimal_listener | healthy_action | 2 | id01,id07 | 0.500000 | 0.526466 | 0.530759 |
| world_episode_minimal_listener | healthy_action | 3 | id05,id06 | 0.500000 | 0.529466 | 0.522836 |
| world_episode_minimal_listener | healthy_action | 4 | id02,id09 | 0.500000 | 0.477997 | 0.480060 |
| world_episode_minimal_listener | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.619596 | 0.481193 |
| world_episode_minimal_listener | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.638172 | 0.503424 |
| world_episode_minimal_listener | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.648260 | 0.508141 |
| world_episode_minimal_listener | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.656753 | 0.493026 |
| world_episode_minimal_listener | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.646913 | 0.466618 |
| hsjepa_listener_manifold | strict_jury_released | 0 | id03,id04 | 0.017460 | 0.874302 | 0.175846 |
| hsjepa_listener_manifold | strict_jury_released | 1 | id08,id10 | 0.020867 | 0.866078 | 0.180121 |
| hsjepa_listener_manifold | strict_jury_released | 2 | id01,id07 | 0.036508 | 0.911351 | 0.270338 |
| hsjepa_listener_manifold | strict_jury_released | 3 | id05,id06 | 0.030280 | 0.935497 | 0.431659 |
| hsjepa_listener_manifold | strict_jury_released | 4 | id02,id09 | 0.032905 | 0.969214 | 0.457377 |
| hsjepa_listener_manifold | strict_positive_release | 0 | id03,id04 | 0.009524 | 0.891426 | 0.081042 |
| hsjepa_listener_manifold | strict_positive_release | 1 | id08,id10 | 0.010433 | 0.867802 | 0.140557 |
| hsjepa_listener_manifold | strict_positive_release | 2 | id01,id07 | 0.022222 | 0.875783 | 0.132510 |
| hsjepa_listener_manifold | strict_positive_release | 3 | id05,id06 | 0.011646 | 0.904635 | 0.136341 |
| hsjepa_listener_manifold | strict_positive_release | 4 | id02,id09 | 0.019262 | 0.962391 | 0.362917 |
| hsjepa_listener_manifold | healthy_action | 0 | id03,id04 | 0.500000 | 0.518022 | 0.524692 |
| hsjepa_listener_manifold | healthy_action | 1 | id08,id10 | 0.500000 | 0.538630 | 0.523613 |
| hsjepa_listener_manifold | healthy_action | 2 | id01,id07 | 0.500000 | 0.478044 | 0.477791 |
| hsjepa_listener_manifold | healthy_action | 3 | id05,id06 | 0.500000 | 0.500620 | 0.523786 |
| hsjepa_listener_manifold | healthy_action | 4 | id02,id09 | 0.500000 | 0.511907 | 0.508064 |
| hsjepa_listener_manifold | toxic_tail_action | 0 | id03,id04 | 0.416667 | 0.656187 | 0.517177 |
| hsjepa_listener_manifold | toxic_tail_action | 1 | id08,id10 | 0.411717 | 0.660867 | 0.513327 |
| hsjepa_listener_manifold | toxic_tail_action | 2 | id01,id07 | 0.407143 | 0.635254 | 0.476216 |
| hsjepa_listener_manifold | toxic_tail_action | 3 | id05,id06 | 0.394410 | 0.652274 | 0.489306 |
| hsjepa_listener_manifold | toxic_tail_action | 4 | id02,id09 | 0.386838 | 0.690102 | 0.508519 |

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
HS-JEPA listener manifold가 action-only baseline보다 strict jury release를 더 잘
분리하면, hidden human-state representation이 adapter rule의 부산물이 아니라
subject-invariant action-health geometry를 담고 있다는 증거가 된다.
```

나쁜 결과:

```text
action geometry only가 압도적으로 이기면, 현재 성과는 HS-JEPA core보다
competition adapter의 action magnitude/prior geometry에 더 의존한다는 뜻이다.
```
