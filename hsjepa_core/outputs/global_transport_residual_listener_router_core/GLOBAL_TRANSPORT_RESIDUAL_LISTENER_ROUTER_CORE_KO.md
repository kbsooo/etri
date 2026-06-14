# Global Transport Residual Listener-Router Core

## 한 줄 요약

이 실험은 learned listener-head router가 global transported prototype grammar를
대체해야 하는지, 아니면 그 위에 붙는 residual listener interface여야 하는지 검증한다.

```text
subject-relative visible human-life context
  -> cross-subject transported prototype grammar
  -> label-free hidden listener-head suitability prediction
  -> learned residual listener-router interface
  -> frozen downstream probe
```

## 판정

- verdict: `global_transport_residual_listener_router_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- architecture question: `listener_router_replacement_vs_global_transport_residual_interface`
- residual interface: `learned_label_free_listener_head_router_on_global_transport_backbone`

## 핵심 수치

- global transport logloss: `0.676724`
- learned router alone logloss: `0.677359`
- semantic-prior router alone logloss: `0.677427`
- best residual feature set: `global_plus_semantic_and_learned_router_calibrated10`
- best residual logloss: `0.675817`
- best residual delta vs global: `-0.000907`
- best learned residual feature set: `global_plus_semantic_and_learned_router_calibrated10`
- best learned residual logloss: `0.675817`
- best learned residual delta vs global: `-0.000907`
- best learned residual delta vs learned alone: `-0.001542`
- row-block best learned residual delta vs global: `-0.000428`
- chronological best learned residual delta vs global: `0.001965`

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_plus_semantic_and_learned_router_calibrated10 | 0.675817 | 0.407251 |
| global_plus_learned_router_full_residual_calibrated10 | 0.675826 | 0.406097 |
| global_plus_learned_router_delta_signal_calibrated10 | 0.676307 | 0.404049 |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| global_plus_learned_router_weight_signal_calibrated10 | 0.676869 | 0.402632 |
| global_plus_future_listener_head_calibrated10 | 0.676931 | 0.402524 |
| global_plus_semantic_prior_router_calibrated10 | 0.677100 | 0.399876 |
| learned_listener_head_router_calibrated10 | 0.677359 | 0.397261 |
| semantic_prior_router_calibrated10 | 0.677427 | 0.393772 |
| future_listener_head_calibrated10 | 0.677463 | 0.394162 |
| learned_router_weight_signal_calibrated10 | 0.677580 | 0.390233 |
| direct_semantic_listener_calibrated10 | 0.677638 | 0.391800 |
| global_plus_learned_listener_head_router_calibrated10 | 0.677815 | 0.399244 |
| learned_router_delta_signal_calibrated10 | 0.677833 | 0.395928 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| raw_lifelog_pca_calibrated10 | 0.678513 | 0.415359 |
| learned_router_weight_signal | 0.680060 | 0.451916 |
| semantic_prior_router | 0.694880 | 0.482709 |
| future_listener_head | 0.696191 | 0.482610 |
| direct_semantic_listener | 0.698179 | 0.473842 |
| learned_listener_head_router | 0.701545 | 0.489199 |
| learned_router_delta_signal | 0.707556 | 0.467275 |
| global_plus_learned_router_full_residual | 0.708710 | 0.518014 |
| global_plus_learned_router_delta_signal | 0.710446 | 0.509756 |
| global_plus_semantic_and_learned_router | 0.710981 | 0.518906 |
| global_plus_learned_router_weight_signal | 0.733397 | 0.502276 |
| global_transported_prototype | 0.736658 | 0.500467 |
| global_plus_future_listener_head | 0.737631 | 0.502292 |
| global_plus_semantic_prior_router | 0.737929 | 0.498646 |
| global_plus_learned_listener_head_router | 0.741999 | 0.489352 |
| raw_lifelog_pca | 1.087640 | 0.501735 |

## Best Learned Residual Target Breakdown

| target | logloss | auc |
| --- | --- | --- |
| Q1 | 0.705354 | 0.398135 |
| Q2 | 0.695330 | 0.424731 |
| Q3 | 0.680340 | 0.418992 |
| S1 | 0.640599 | 0.396346 |
| S2 | 0.653920 | 0.451425 |
| S3 | 0.659429 | 0.352217 |
| S4 | 0.695749 | 0.408911 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668480 | 0.481690 |
| learned_listener_head_router_calibrated10 | 0.672826 | 0.412684 |
| global_plus_semantic_and_learned_router_calibrated10 | 0.672903 | 0.428250 |
| future_listener_head_calibrated10 | 0.673025 | 0.409507 |
| global_plus_learned_router_full_residual_calibrated10 | 0.673056 | 0.427954 |
| global_plus_future_listener_head_calibrated10 | 0.673076 | 0.424888 |
| learned_router_delta_signal_calibrated10 | 0.673079 | 0.426857 |
| semantic_prior_router_calibrated10 | 0.673165 | 0.407553 |
| global_plus_learned_listener_head_router_calibrated10 | 0.673232 | 0.427740 |
| global_plus_learned_router_delta_signal_calibrated10 | 0.673268 | 0.427550 |
| global_plus_semantic_prior_router_calibrated10 | 0.673329 | 0.422905 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| direct_semantic_listener_calibrated10 | 0.673375 | 0.413186 |
| global_plus_learned_router_weight_signal_calibrated10 | 0.673715 | 0.424578 |
| learned_router_weight_signal_calibrated10 | 0.673891 | 0.413575 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| learned_router_weight_signal | 0.678545 | 0.467714 |
| future_listener_head | 0.678622 | 0.492005 |
| semantic_prior_router | 0.678811 | 0.488500 |
| learned_listener_head_router | 0.683755 | 0.502819 |
| direct_semantic_listener | 0.686009 | 0.497482 |
| raw_lifelog_pca | 0.693523 | 0.581903 |
| learned_router_delta_signal | 0.705450 | 0.499557 |
| global_plus_semantic_and_learned_router | 0.722331 | 0.515435 |
| global_plus_future_listener_head | 0.723814 | 0.507025 |
| global_plus_learned_router_delta_signal | 0.724406 | 0.506841 |
| global_plus_learned_router_full_residual | 0.725010 | 0.511116 |
| global_plus_semantic_prior_router | 0.725889 | 0.503674 |
| global_transported_prototype | 0.728298 | 0.506119 |
| global_plus_learned_listener_head_router | 0.731981 | 0.508079 |
| global_plus_learned_router_weight_signal | 0.738598 | 0.504459 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.665020 | 0.596837 |
| learned_listener_head_router_calibrated10 | 0.670051 | 0.526053 |
| semantic_prior_router_calibrated10 | 0.670059 | 0.526554 |
| future_listener_head_calibrated10 | 0.670077 | 0.526337 |
| direct_semantic_listener_calibrated10 | 0.670193 | 0.524836 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| learned_router_weight_signal_calibrated10 | 0.670826 | 0.500000 |
| learned_router_weight_signal | 0.670827 | 0.500000 |
| global_plus_learned_router_weight_signal_calibrated10 | 0.671537 | 0.491242 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| global_plus_future_listener_head_calibrated10 | 0.671714 | 0.489039 |
| global_plus_learned_listener_head_router_calibrated10 | 0.671720 | 0.490149 |
| global_plus_semantic_prior_router_calibrated10 | 0.671724 | 0.489808 |
| global_plus_semantic_and_learned_router_calibrated10 | 0.673502 | 0.508073 |
| global_plus_learned_router_delta_signal_calibrated10 | 0.673537 | 0.515829 |
| global_plus_learned_router_full_residual_calibrated10 | 0.674230 | 0.509728 |
| learned_router_delta_signal_calibrated10 | 0.675060 | 0.513856 |
| learned_listener_head_router | 0.676786 | 0.526053 |
| semantic_prior_router | 0.676796 | 0.526554 |
| future_listener_head | 0.676821 | 0.526337 |
| direct_semantic_listener | 0.684005 | 0.524836 |
| raw_lifelog_pca | 0.717395 | 0.596837 |
| global_plus_learned_router_weight_signal | 0.748130 | 0.491242 |
| global_transported_prototype | 0.748130 | 0.491242 |
| global_plus_future_listener_head | 0.751794 | 0.489039 |
| global_plus_semantic_prior_router | 0.752246 | 0.489808 |
| global_plus_learned_listener_head_router | 0.752284 | 0.490149 |
| global_plus_semantic_and_learned_router | 3.293483 | 0.508073 |
| global_plus_learned_router_delta_signal | 3.298464 | 0.515829 |
| global_plus_learned_router_full_residual | 3.305988 | 0.509728 |
| learned_router_delta_signal | 3.424552 | 0.513856 |

## Label-Free Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | semantic_cross_entropy | ce_lift_vs_prior | ce_lift_vs_semantic | top1_match_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | head_cohort_relative | 0.942764 | 0.964138 | NA | 0.021374 | NA | 0.786260 |
| chronological_holdout | head_current_relative | 0.948227 | 0.979411 | NA | 0.031184 | NA | 0.655398 |
| chronological_holdout | head_future_relative | 0.968099 | 0.980229 | NA | 0.012130 | NA | 0.719738 |
| chronological_holdout | learned_semantic_router_context_headsignal | 1.200156 | 1.052950 | NA | -0.147207 | NA | 0.379498 |
| row_block_holdout | head_cohort_relative | 0.956157 | 0.977596 | NA | 0.021439 | NA | 0.786667 |
| row_block_holdout | head_current_relative | 0.966638 | 0.994646 | NA | 0.028008 | NA | 0.640317 |
| row_block_holdout | head_future_relative | 0.983781 | 0.994075 | NA | 0.010294 | NA | 0.704127 |
| row_block_holdout | learned_semantic_router_context_headsignal | 1.054305 | 1.057085 | NA | 0.002780 | NA | 0.712381 |
| subject_heldout | head_cohort_relative | 0.942310 | 0.967328 | NA | 0.025017 | NA | 0.794540 |
| subject_heldout | head_current_relative | 0.957346 | 0.987152 | NA | 0.029806 | NA | 0.651154 |
| subject_heldout | head_future_relative | 0.975560 | 0.987074 | NA | 0.011514 | NA | 0.714095 |
| subject_heldout | learned_semantic_router_context_headsignal | 1.052675 | 1.055147 | NA | 0.002473 | NA | 0.724736 |

## Router Weight Summary

| router | target | mean_w_current | mean_w_future | mean_w_cohort | mean_entropy | mean_margin |
| --- | --- | --- | --- | --- | --- | --- |
| learned_semantic_router_context_headsignal | Q1 | 0.256823 | 0.520734 | 0.222443 | 0.929587 | 0.260597 |
| learned_semantic_router_context_headsignal | Q2 | 0.210689 | 0.565081 | 0.224230 | 0.895346 | 0.334219 |
| learned_semantic_router_context_headsignal | Q3 | 0.258241 | 0.468356 | 0.273403 | 0.961625 | 0.184353 |
| learned_semantic_router_context_headsignal | S1 | 0.341893 | 0.445751 | 0.212357 | 0.960166 | 0.103858 |
| learned_semantic_router_context_headsignal | S2 | 0.295924 | 0.447238 | 0.256837 | 0.972332 | 0.150498 |
| learned_semantic_router_context_headsignal | S3 | 0.370611 | 0.276953 | 0.352435 | 0.990910 | 0.038642 |
| learned_semantic_router_context_headsignal | S4 | 0.383919 | 0.255897 | 0.360184 | 0.983693 | 0.051896 |
| semantic_prior_router | Q1 | 0.250000 | 0.550000 | 0.200000 | 0.907756 | 0.300000 |
| semantic_prior_router | Q2 | 0.200000 | 0.600000 | 0.200000 | 0.864974 | 0.400000 |
| semantic_prior_router | Q3 | 0.250000 | 0.500000 | 0.250000 | 0.946395 | 0.250000 |
| semantic_prior_router | S1 | 0.350000 | 0.450000 | 0.200000 | 0.954526 | 0.100000 |
| semantic_prior_router | S2 | 0.300000 | 0.450000 | 0.250000 | 0.971311 | 0.150000 |
| semantic_prior_router | S3 | 0.400000 | 0.250000 | 0.350000 | 0.983539 | 0.050000 |
| semantic_prior_router | S4 | 0.400000 | 0.250000 | 0.350000 | 0.983539 | 0.050000 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| learned_router_weight_signal | 0.246667 | 0.126667 | 0.120000 |
| learned_router_delta_signal | 0.364444 | 0.126667 | 0.237778 |
| global_plus_learned_router_delta_signal | 0.440000 | 0.126667 | 0.313333 |
| global_plus_semantic_and_learned_router | 0.440000 | 0.126667 | 0.313333 |
| global_plus_learned_router_full_residual | 0.444444 | 0.126667 | 0.317778 |
| learned_listener_head_router | 0.446667 | 0.126667 | 0.320000 |
| semantic_prior_router | 0.462222 | 0.126667 | 0.335556 |
| future_listener_head | 0.475556 | 0.126667 | 0.348889 |
| global_plus_learned_listener_head_router | 0.495556 | 0.126667 | 0.368889 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.940000 | 0.126667 | 0.813333 |

## 해석

positive이면 논문 문장은 다음처럼 정리한다.

```text
HS-JEPA should not expose one monolithic human-state vector.
It first transports a subject-invariant episode grammar and then learns a
listener-specific residual interface that decides how each target should read it.
```

negative이면 죽는 믿음은 이것이다.

```text
Current learned listener-head routing contains additional subject-heldout
information beyond global transported prototype grammar.
```

그 경우 learned router는 아직 replacement도 residual interface도 아니며,
다음 core는 residual을 붙이는 방식보다 hidden action-health/release gate를
별도 target representation으로 만들어야 한다.
