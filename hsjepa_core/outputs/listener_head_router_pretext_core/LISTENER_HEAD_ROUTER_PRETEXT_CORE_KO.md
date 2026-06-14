# Listener Head Router Pretext Core

## 한 줄 요약

이 실험은 current/future/cohort head를 concat하지 않는다.
label-free router가 head confidence, entropy, energy, target semantic prior를 보고
각 target-row에서 어느 head를 읽을지 soft routing한다.

```text
subject-relative visible human-life context
  -> current / future / cohort listener-responsibility heads
  -> label-free listener-head router
  -> routed human-state interface
  -> frozen downstream probe
```

## 판정

- verdict: `listener_head_router_beats_single_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- router: `label_free_head_confidence_entropy_energy_and_target_semantic_prior`
- context encoder: `subject_relative_visible_lifelog_context`

## 핵심 수치

- best single head: `head_future_relative_listener_responsibility_calibrated10`
- best single-head logloss: `0.677463`
- best router: `semantic_prior_router_listener_responsibility_calibrated10`
- best router logloss: `0.677427`
- naive multi-head logloss: `0.677966`
- global transport logloss: `0.676724`
- direct semantic logloss: `0.677638`
- prior logloss: `0.677858`
- router delta vs single: `-0.000036`
- router delta vs prior: `-0.000430`
- router delta vs raw lifelog PCA: `-0.001086`
- router delta vs direct semantic: `-0.000211`
- router delta vs naive multi-head: `-0.000539`
- router delta vs global transport: `0.000703`
- row-block router delta vs global: `-0.000166`
- chronological router delta vs global: `-0.001477`

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.677427 | 0.393772 |
| head_future_relative_listener_responsibility_calibrated10 | 0.677463 | 0.394162 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.677507 | 0.392582 |
| head_current_relative_listener_responsibility_calibrated10 | 0.677614 | 0.391306 |
| direct_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| confidence_router_listener_responsibility_calibrated10 | 0.677769 | 0.392861 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.677966 | 0.393316 |
| anti_shortcut_router_listener_responsibility_calibrated10 | 0.677986 | 0.390824 |
| future_anchor_router_listener_responsibility_calibrated10 | 0.677990 | 0.390760 |
| semantic_confidence_router_listener_responsibility_calibrated10 | 0.678003 | 0.390644 |
| raw_lifelog_pca_calibrated10 | 0.678513 | 0.415359 |
| semantic_prior_router_listener_responsibility | 0.694880 | 0.482709 |
| head_cohort_relative_listener_responsibility | 0.695126 | 0.478843 |
| head_current_relative_listener_responsibility | 0.696035 | 0.476723 |
| head_future_relative_listener_responsibility | 0.696191 | 0.482610 |
| direct_semantic_listener_responsibility | 0.698179 | 0.473842 |
| anti_shortcut_router_listener_responsibility | 0.704169 | 0.471694 |
| confidence_router_listener_responsibility | 0.704572 | 0.475938 |
| future_anchor_router_listener_responsibility | 0.704574 | 0.471654 |
| semantic_confidence_router_listener_responsibility | 0.705291 | 0.470532 |
| multihead_current_future_cohort_listener_responsibility | 0.707799 | 0.475590 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668480 | 0.481690 |
| head_future_relative_listener_responsibility_calibrated10 | 0.673025 | 0.409507 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.673165 | 0.407553 |
| semantic_confidence_router_listener_responsibility_calibrated10 | 0.673265 | 0.407782 |
| head_current_relative_listener_responsibility_calibrated10 | 0.673296 | 0.404646 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.673364 | 0.407183 |
| direct_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.673415 | 0.405275 |
| confidence_router_listener_responsibility_calibrated10 | 0.673427 | 0.405931 |
| anti_shortcut_router_listener_responsibility_calibrated10 | 0.673443 | 0.405802 |
| future_anchor_router_listener_responsibility_calibrated10 | 0.673491 | 0.404645 |
| prior_only | 0.674078 | 0.401854 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| head_future_relative_listener_responsibility | 0.678622 | 0.492005 |
| semantic_prior_router_listener_responsibility | 0.678811 | 0.488500 |
| head_current_relative_listener_responsibility | 0.679651 | 0.484592 |
| head_cohort_relative_listener_responsibility | 0.680577 | 0.480986 |
| semantic_confidence_router_listener_responsibility | 0.685240 | 0.488759 |
| anti_shortcut_router_listener_responsibility | 0.685319 | 0.483971 |
| direct_semantic_listener_responsibility | 0.686009 | 0.497482 |
| future_anchor_router_listener_responsibility | 0.686092 | 0.482082 |
| confidence_router_listener_responsibility | 0.687593 | 0.486068 |
| multihead_current_future_cohort_listener_responsibility | 0.687692 | 0.485557 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.665020 | 0.596837 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.669977 | 0.526756 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.670053 | 0.523250 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.670059 | 0.526554 |
| head_future_relative_listener_responsibility_calibrated10 | 0.670077 | 0.526337 |
| head_current_relative_listener_responsibility_calibrated10 | 0.670108 | 0.524116 |
| direct_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| confidence_router_listener_responsibility_calibrated10 | 0.672452 | 0.499796 |
| future_anchor_router_listener_responsibility_calibrated10 | 0.675632 | 0.488144 |
| anti_shortcut_router_listener_responsibility_calibrated10 | 0.675945 | 0.483665 |
| head_cohort_relative_listener_responsibility | 0.676021 | 0.526756 |
| semantic_confidence_router_listener_responsibility_calibrated10 | 0.676285 | 0.487249 |
| semantic_prior_router_listener_responsibility | 0.676796 | 0.526554 |
| head_future_relative_listener_responsibility | 0.676821 | 0.526337 |
| head_current_relative_listener_responsibility | 0.677817 | 0.524116 |
| multihead_current_future_cohort_listener_responsibility | 0.678328 | 0.523250 |
| direct_semantic_listener_responsibility | 0.684005 | 0.524836 |
| raw_lifelog_pca | 0.717395 | 0.596837 |
| global_transported_prototype | 0.748130 | 0.491242 |
| semantic_confidence_router_listener_responsibility | 4.763149 | 0.487249 |
| future_anchor_router_listener_responsibility | 5.143784 | 0.488144 |

## Label-Free Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | ce_lift_vs_prior | top1_match_rate |
| --- | --- | --- | --- | --- | --- |
| chronological_holdout | head_cohort_relative | 0.942764 | 0.964138 | 0.021374 | 0.786260 |
| chronological_holdout | head_current_relative | 0.948227 | 0.979411 | 0.031184 | 0.655398 |
| chronological_holdout | head_future_relative | 0.968099 | 0.980229 | 0.012130 | 0.719738 |
| row_block_holdout | head_cohort_relative | 0.956157 | 0.977596 | 0.021439 | 0.786667 |
| row_block_holdout | head_current_relative | 0.966638 | 0.994646 | 0.028008 | 0.640317 |
| row_block_holdout | head_future_relative | 0.983781 | 0.994075 | 0.010294 | 0.704127 |
| subject_heldout | head_cohort_relative | 0.942310 | 0.967328 | 0.025017 | 0.794540 |
| subject_heldout | head_current_relative | 0.957346 | 0.987152 | 0.029806 | 0.651154 |
| subject_heldout | head_future_relative | 0.975560 | 0.987074 | 0.011514 | 0.714095 |

## Router Weight Summary

| router | target | mean_w_current | mean_w_future | mean_w_cohort | mean_entropy | mean_margin |
| --- | --- | --- | --- | --- | --- | --- |
| anti_shortcut_router | Q1 | 0.290817 | 0.556816 | 0.152367 | 0.881320 | 0.265999 |
| anti_shortcut_router | Q2 | 0.287629 | 0.560886 | 0.151485 | 0.878593 | 0.273257 |
| anti_shortcut_router | Q3 | 0.292958 | 0.554985 | 0.152057 | 0.877383 | 0.261855 |
| anti_shortcut_router | S1 | 0.289598 | 0.561506 | 0.148896 | 0.876192 | 0.271907 |
| anti_shortcut_router | S2 | 0.288959 | 0.560223 | 0.150818 | 0.879543 | 0.271265 |
| anti_shortcut_router | S3 | 0.284926 | 0.561840 | 0.153233 | 0.879421 | 0.276914 |
| anti_shortcut_router | S4 | 0.289121 | 0.559868 | 0.151011 | 0.875501 | 0.270630 |
| confidence_router | Q1 | 0.335410 | 0.332837 | 0.331753 | 0.991270 | 0.052648 |
| confidence_router | Q2 | 0.331445 | 0.337747 | 0.330808 | 0.992606 | 0.047780 |
| confidence_router | Q3 | 0.339001 | 0.332915 | 0.328084 | 0.977750 | 0.087455 |
| confidence_router | S1 | 0.336297 | 0.340256 | 0.323447 | 0.989795 | 0.049579 |
| confidence_router | S2 | 0.333851 | 0.337252 | 0.328897 | 0.994221 | 0.039987 |
| confidence_router | S3 | 0.326507 | 0.337895 | 0.335598 | 0.993502 | 0.044611 |
| confidence_router | S4 | 0.334309 | 0.338770 | 0.326921 | 0.981860 | 0.076348 |
| future_anchor_router | Q1 | 0.181101 | 0.658876 | 0.160022 | 0.796335 | 0.474001 |
| future_anchor_router | Q2 | 0.179032 | 0.661977 | 0.158991 | 0.792815 | 0.480145 |
| future_anchor_router | Q3 | 0.182704 | 0.657627 | 0.159669 | 0.793843 | 0.465668 |
| future_anchor_router | S1 | 0.180171 | 0.663259 | 0.156570 | 0.790337 | 0.479212 |
| future_anchor_router | S2 | 0.179759 | 0.661799 | 0.158443 | 0.793503 | 0.479899 |
| future_anchor_router | S3 | 0.177270 | 0.662258 | 0.160472 | 0.792900 | 0.482019 |
| future_anchor_router | S4 | 0.180032 | 0.661502 | 0.158466 | 0.790287 | 0.473721 |
| semantic_confidence_router | Q1 | 0.251518 | 0.548542 | 0.199940 | 0.904399 | 0.293975 |
| semantic_confidence_router | Q2 | 0.198849 | 0.602553 | 0.198599 | 0.858723 | 0.389485 |
| semantic_confidence_router | Q3 | 0.253931 | 0.497978 | 0.248092 | 0.935216 | 0.215721 |
| semantic_confidence_router | S1 | 0.350692 | 0.454153 | 0.195155 | 0.946022 | 0.103676 |
| semantic_confidence_router | S2 | 0.299909 | 0.452858 | 0.247233 | 0.966528 | 0.150122 |
| semantic_confidence_router | S3 | 0.394103 | 0.253472 | 0.352425 | 0.981317 | 0.058700 |
| semantic_confidence_router | S4 | 0.402005 | 0.254183 | 0.343812 | 0.973352 | 0.089106 |
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
| future_anchor_router_listener_responsibility | 0.424444 | 0.126667 | 0.297778 |
| anti_shortcut_router_listener_responsibility | 0.431111 | 0.126667 | 0.304444 |
| direct_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| head_current_relative_listener_responsibility | 0.451111 | 0.126667 | 0.324444 |
| confidence_router_listener_responsibility | 0.460000 | 0.126667 | 0.333333 |
| semantic_prior_router_listener_responsibility | 0.462222 | 0.126667 | 0.335556 |
| multihead_current_future_cohort_listener_responsibility | 0.466667 | 0.126667 | 0.340000 |
| semantic_confidence_router_listener_responsibility | 0.473333 | 0.126667 | 0.346667 |
| head_future_relative_listener_responsibility | 0.475556 | 0.126667 | 0.348889 |
| head_cohort_relative_listener_responsibility | 0.482222 | 0.126667 | 0.355556 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.940000 | 0.126667 | 0.813333 |

## 해석

positive이면:

```text
HS-JEPA should expose current/future/cohort heads and use a label-free listener router
instead of naive head concatenation.
```

negative이면:

```text
The missing component is not a hand-built head router.  The future head itself is useful,
but router learning must be a stronger JEPA objective rather than confidence heuristics.
```
