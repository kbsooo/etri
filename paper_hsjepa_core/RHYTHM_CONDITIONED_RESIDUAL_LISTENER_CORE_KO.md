# Rhythm-Conditioned Residual Listener Core

## 한 줄 요약

이 실험은 residual listener router가 시간 순서 split에서 독성을 보인 이유를
`리듬이 안정적인 날의 residual`과 `리듬이 흔들리는 날의 residual`을 구분하지 못했기 때문이라고 가정한다.

```text
calendar rhythm confidence / entropy / energy
  -> rhythm stability gate
  -> stable residual listener channel
  -> unstable residual listener channel
  -> frozen downstream probe
```

## 판정

- verdict: `rhythm_context_temporal_decoder_with_gated_residual_subject_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- architecture question: `can_visible_rhythm_context_separate_stable_listener_residual_from_temporal_drift`
- residual interface: `global_transport_backbone_plus_rhythm_gated_listener_residual`

## 핵심 수치

### Subject-Heldout

- global transport: `0.676724`
- plain residual: `0.675817`
- best rhythm feature: `global_plus_residual_and_rhythm_gated_residual_calibrated10`
- best rhythm logloss: `0.675281`
- best rhythm delta vs global: `-0.001443`
- best rhythm delta vs plain residual: `-0.000537`
- best gated residual feature: `global_plus_residual_and_rhythm_gated_residual_calibrated10`
- best gated residual logloss: `0.675281`
- best gated residual delta vs plain residual: `-0.000537`

### Row-Block

- global transport: `0.673331`
- plain residual: `0.672903`
- best rhythm feature: `global_plus_rhythm_context_calibrated10`
- best rhythm logloss: `0.672363`
- best rhythm delta vs global: `-0.000968`
- best rhythm delta vs plain residual: `-0.000541`
- best gated residual feature: `global_plus_residual_and_rhythm_gated_residual_calibrated10`
- best gated residual logloss: `0.672421`
- best gated residual delta vs plain residual: `-0.000483`

### Chronological

- global transport: `0.671537`
- plain residual: `0.673502`
- plain residual delta vs global: `0.001965`
- best rhythm feature: `rhythm_context_calibrated10`
- best rhythm logloss: `0.669300`
- best rhythm delta vs global: `-0.002237`
- best rhythm delta vs plain residual: `-0.004202`
- best gated residual feature: `global_plus_residual_and_rhythm_gated_residual_calibrated10`
- best gated residual logloss: `0.671564`
- best gated residual delta vs global: `0.000027`
- best gated residual delta vs plain residual: `-0.001938`

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_plus_residual_and_rhythm_gated_residual_calibrated10 | 0.675281 | 0.416802 |
| global_plus_residual_rhythm_context_and_gated_residual_calibrated10 | 0.675401 | 0.415079 |
| global_plus_rhythm_context_and_gated_residual_calibrated10 | 0.675525 | 0.412789 |
| global_plus_rhythm_gated_residual_listener_calibrated10 | 0.675641 | 0.413058 |
| global_plus_rhythm_context_calibrated10 | 0.675662 | 0.414035 |
| global_plus_semantic_and_learned_router_calibrated10 | 0.675817 | 0.407251 |
| rhythm_gated_residual_listener_calibrated10 | 0.676368 | 0.409472 |
| rhythm_context_calibrated10 | 0.676677 | 0.403696 |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| learned_listener_head_router_calibrated10 | 0.677359 | 0.397261 |
| semantic_prior_router_calibrated10 | 0.677427 | 0.393772 |
| future_listener_head_calibrated10 | 0.677463 | 0.394162 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| prior_only | 0.677858 | 0.382414 |
| raw_lifelog_pca_calibrated10 | 0.678513 | 0.415359 |
| rhythm_context | 0.685963 | 0.495316 |
| semantic_prior_router | 0.694880 | 0.482709 |
| future_listener_head | 0.696191 | 0.482610 |
| learned_listener_head_router | 0.701545 | 0.489199 |
| global_plus_semantic_and_learned_router | 0.710981 | 0.518906 |
| global_plus_residual_and_rhythm_gated_residual | 0.717717 | 0.529758 |
| global_plus_residual_rhythm_context_and_gated_residual | 0.718636 | 0.525696 |
| global_plus_rhythm_context_and_gated_residual | 0.719727 | 0.522719 |
| global_plus_rhythm_context | 0.721446 | 0.518013 |
| global_plus_rhythm_gated_residual_listener | 0.722132 | 0.522250 |
| rhythm_gated_residual_listener | 0.736156 | 0.508413 |
| global_transported_prototype | 0.736658 | 0.500467 |
| raw_lifelog_pca | 1.087640 | 0.501735 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668480 | 0.481690 |
| global_plus_rhythm_context_calibrated10 | 0.672363 | 0.430104 |
| global_plus_residual_and_rhythm_gated_residual_calibrated10 | 0.672421 | 0.434978 |
| global_plus_rhythm_context_and_gated_residual_calibrated10 | 0.672422 | 0.437032 |
| global_plus_residual_rhythm_context_and_gated_residual_calibrated10 | 0.672434 | 0.434283 |
| global_plus_rhythm_gated_residual_listener_calibrated10 | 0.672557 | 0.436435 |
| learned_listener_head_router_calibrated10 | 0.672826 | 0.412684 |
| rhythm_context_calibrated10 | 0.672856 | 0.421917 |
| global_plus_semantic_and_learned_router_calibrated10 | 0.672903 | 0.428250 |
| rhythm_gated_residual_listener_calibrated10 | 0.672981 | 0.430900 |
| future_listener_head_calibrated10 | 0.673025 | 0.409507 |
| semantic_prior_router_calibrated10 | 0.673165 | 0.407553 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| future_listener_head | 0.678622 | 0.492005 |
| semantic_prior_router | 0.678811 | 0.488500 |
| rhythm_context | 0.681438 | 0.508117 |
| learned_listener_head_router | 0.683755 | 0.502819 |
| raw_lifelog_pca | 0.693523 | 0.581903 |
| global_plus_semantic_and_learned_router | 0.722331 | 0.515435 |
| global_plus_rhythm_context | 0.723113 | 0.517518 |
| global_plus_rhythm_context_and_gated_residual | 0.724449 | 0.517838 |
| global_plus_residual_and_rhythm_gated_residual | 0.724758 | 0.517059 |
| global_plus_residual_rhythm_context_and_gated_residual | 0.724796 | 0.515594 |
| global_plus_rhythm_gated_residual_listener | 0.726054 | 0.514427 |
| global_transported_prototype | 0.728298 | 0.506119 |
| rhythm_gated_residual_listener | 0.739182 | 0.506967 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.665020 | 0.596837 |
| rhythm_context_calibrated10 | 0.669300 | 0.532666 |
| global_plus_rhythm_context_calibrated10 | 0.669671 | 0.528233 |
| learned_listener_head_router_calibrated10 | 0.670051 | 0.526053 |
| semantic_prior_router_calibrated10 | 0.670059 | 0.526554 |
| future_listener_head_calibrated10 | 0.670077 | 0.526337 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| global_plus_residual_and_rhythm_gated_residual_calibrated10 | 0.671564 | 0.524254 |
| global_plus_rhythm_gated_residual_listener_calibrated10 | 0.672292 | 0.529447 |
| global_plus_residual_rhythm_context_and_gated_residual_calibrated10 | 0.672735 | 0.514839 |
| global_plus_rhythm_context_and_gated_residual_calibrated10 | 0.673044 | 0.519694 |
| global_plus_semantic_and_learned_router_calibrated10 | 0.673502 | 0.508073 |
| rhythm_gated_residual_listener_calibrated10 | 0.676584 | 0.514771 |
| learned_listener_head_router | 0.676786 | 0.526053 |
| semantic_prior_router | 0.676796 | 0.526554 |
| future_listener_head | 0.676821 | 0.526337 |
| rhythm_context | 0.686822 | 0.532666 |
| raw_lifelog_pca | 0.717395 | 0.596837 |
| global_plus_rhythm_context | 0.721779 | 0.528233 |
| global_transported_prototype | 0.748130 | 0.491242 |
| global_plus_rhythm_context_and_gated_residual | 2.896991 | 0.519694 |
| global_plus_rhythm_gated_residual_listener | 3.032280 | 0.529447 |
| global_plus_residual_rhythm_context_and_gated_residual | 3.283545 | 0.514839 |
| global_plus_semantic_and_learned_router | 3.293483 | 0.508073 |
| global_plus_residual_and_rhythm_gated_residual | 3.337257 | 0.524254 |
| rhythm_gated_residual_listener | 3.415747 | 0.514771 |

## Chronological Target Breakdown For Best Rhythm Feature

| target | logloss | auc |
| --- | --- | --- |
| Q1 | 0.698609 | 0.500704 |
| Q2 | 0.679366 | 0.514190 |
| Q3 | 0.658568 | 0.514438 |
| S1 | 0.619732 | 0.555556 |
| S2 | 0.671858 | 0.587990 |
| S3 | 0.664975 | 0.520657 |
| S4 | 0.691992 | 0.535129 |

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
| rhythm_context | 0.113333 | 0.126667 | -0.013333 |
| rhythm_gated_residual_listener | 0.400000 | 0.126667 | 0.273333 |
| global_plus_rhythm_gated_residual_listener | 0.402222 | 0.126667 | 0.275556 |
| global_plus_rhythm_context_and_gated_residual | 0.404444 | 0.126667 | 0.277778 |
| global_plus_residual_rhythm_context_and_gated_residual | 0.415556 | 0.126667 | 0.288889 |
| global_plus_residual_and_rhythm_gated_residual | 0.420000 | 0.126667 | 0.293333 |
| global_plus_semantic_and_learned_router | 0.440000 | 0.126667 | 0.313333 |
| global_plus_rhythm_context | 0.475556 | 0.126667 | 0.348889 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.940000 | 0.126667 | 0.813333 |

## 해석

positive이면:

```text
HS-JEPA should separate two readouts:
1. rhythm context as the temporal drift decoder,
2. rhythm-gated residual listener channels as subject/block readability adapters.
```

negative이면:

```text
Simple rhythm gating is not enough to solve chronological drift toxicity.
The next core target should predict future drift/action-health directly rather than
only gate residual readout by rhythm confidence.
```
