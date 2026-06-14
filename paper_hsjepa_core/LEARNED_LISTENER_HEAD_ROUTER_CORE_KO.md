# Learned Listener-Head Router Core

## 한 줄 요약

이 실험은 사람이 고정한 semantic-prior router를 넘기 위해,
current/future/cohort head 중 어느 head를 들어야 하는지를 label-free hidden
head-suitability pretext로 학습한다.

```text
visible subject-relative human-life context
  + predicted current/future/cohort listener heads
  -> hidden head-suitability field prediction
  -> learned listener-head router
  -> routed HS-JEPA interface
  -> frozen downstream probe
```

## 판정

- verdict: `learned_listener_head_router_beats_semantic_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- router: `learned_label_free_hidden_head_suitability`
- context encoder: `subject_relative_visible_lifelog_context_plus_predicted_listener_heads`

## 핵심 수치

- best learned router: `learned_semantic_router_context_headsignal_listener_responsibility_calibrated10`
- best learned router logloss: `0.677359`
- fixed semantic-prior router logloss: `0.677427`
- best single head: `head_future_relative_listener_responsibility_calibrated10`
- best single-head logloss: `0.677463`
- naive multi-head logloss: `0.677966`
- global transport logloss: `0.676724`
- direct semantic logloss: `0.677638`
- prior logloss: `0.677858`
- learned delta vs fixed semantic router: `-0.000068`
- learned delta vs single: `-0.000103`
- learned delta vs prior: `-0.000498`
- learned delta vs raw lifelog PCA: `-0.001154`
- learned delta vs direct semantic: `-0.000279`
- learned delta vs naive multi-head: `-0.000606`
- learned delta vs global transport: `0.000636`
- row-block learned delta vs global: `-0.000505`
- chronological learned delta vs global: `-0.001486`

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| learned_semantic_router_context_headsignal_listener_responsibility_calibrated10 | 0.677359 | 0.397261 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility_calibrated10 | 0.677414 | 0.396571 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.677427 | 0.393772 |
| head_future_relative_listener_responsibility_calibrated10 | 0.677463 | 0.394162 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.677507 | 0.392582 |
| learned_state_router_context_headsignal_listener_responsibility_calibrated10 | 0.677541 | 0.395145 |
| head_current_relative_listener_responsibility_calibrated10 | 0.677614 | 0.391306 |
| direct_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| learned_state_router_context_listener_responsibility_calibrated10 | 0.677767 | 0.391812 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.677966 | 0.393316 |
| learned_semantic_distilled_router_headsignal_listener_responsibility_calibrated10 | 0.678108 | 0.393732 |
| learned_state_router_headsignal_listener_responsibility_calibrated10 | 0.678218 | 0.390676 |
| raw_lifelog_pca_calibrated10 | 0.678513 | 0.415359 |
| semantic_prior_router_listener_responsibility | 0.694880 | 0.482709 |
| head_cohort_relative_listener_responsibility | 0.695126 | 0.478843 |
| head_current_relative_listener_responsibility | 0.696035 | 0.476723 |
| head_future_relative_listener_responsibility | 0.696191 | 0.482610 |
| direct_semantic_listener_responsibility | 0.698179 | 0.473842 |
| learned_semantic_router_context_headsignal_listener_responsibility | 0.701545 | 0.489199 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility | 0.703012 | 0.487298 |
| learned_state_router_context_headsignal_listener_responsibility | 0.703686 | 0.485286 |
| learned_state_router_context_listener_responsibility | 0.704186 | 0.478713 |
| multihead_current_future_cohort_listener_responsibility | 0.707799 | 0.475590 |
| learned_semantic_distilled_router_headsignal_listener_responsibility | 0.708977 | 0.473580 |
| learned_state_router_headsignal_listener_responsibility | 0.712412 | 0.470088 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668480 | 0.481690 |
| learned_semantic_router_context_headsignal_listener_responsibility_calibrated10 | 0.672826 | 0.412684 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility_calibrated10 | 0.672920 | 0.412756 |
| learned_state_router_context_headsignal_listener_responsibility_calibrated10 | 0.672969 | 0.413656 |
| learned_semantic_distilled_router_headsignal_listener_responsibility_calibrated10 | 0.672970 | 0.413471 |
| head_future_relative_listener_responsibility_calibrated10 | 0.673025 | 0.409507 |
| learned_state_router_context_listener_responsibility_calibrated10 | 0.673057 | 0.411082 |
| learned_state_router_headsignal_listener_responsibility_calibrated10 | 0.673144 | 0.412423 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.673165 | 0.407553 |
| head_current_relative_listener_responsibility_calibrated10 | 0.673296 | 0.404646 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.673364 | 0.407183 |
| direct_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.673415 | 0.405275 |
| prior_only | 0.674078 | 0.401854 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| head_future_relative_listener_responsibility | 0.678622 | 0.492005 |
| semantic_prior_router_listener_responsibility | 0.678811 | 0.488500 |
| head_current_relative_listener_responsibility | 0.679651 | 0.484592 |
| head_cohort_relative_listener_responsibility | 0.680577 | 0.480986 |
| learned_semantic_router_context_headsignal_listener_responsibility | 0.683755 | 0.502819 |
| learned_semantic_distilled_router_headsignal_listener_responsibility | 0.684538 | 0.487711 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility | 0.685933 | 0.502866 |
| direct_semantic_listener_responsibility | 0.686009 | 0.497482 |
| learned_state_router_context_listener_responsibility | 0.687266 | 0.501066 |
| multihead_current_future_cohort_listener_responsibility | 0.687692 | 0.485557 |
| learned_state_router_context_headsignal_listener_responsibility | 0.687799 | 0.506115 |
| learned_state_router_headsignal_listener_responsibility | 0.689618 | 0.486762 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.665020 | 0.596837 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.669977 | 0.526756 |
| learned_state_router_context_headsignal_listener_responsibility_calibrated10 | 0.670048 | 0.525981 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility_calibrated10 | 0.670051 | 0.526706 |
| learned_semantic_router_context_headsignal_listener_responsibility_calibrated10 | 0.670051 | 0.526053 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.670053 | 0.523250 |
| learned_state_router_context_listener_responsibility_calibrated10 | 0.670057 | 0.526308 |
| semantic_prior_router_listener_responsibility_calibrated10 | 0.670059 | 0.526554 |
| learned_state_router_headsignal_listener_responsibility_calibrated10 | 0.670062 | 0.525641 |
| learned_semantic_distilled_router_headsignal_listener_responsibility_calibrated10 | 0.670066 | 0.526053 |
| head_future_relative_listener_responsibility_calibrated10 | 0.670077 | 0.526337 |
| head_current_relative_listener_responsibility_calibrated10 | 0.670108 | 0.524116 |
| direct_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| prior_only | 0.670826 | 0.500000 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| head_cohort_relative_listener_responsibility | 0.676021 | 0.526756 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility | 0.676768 | 0.526706 |
| learned_state_router_context_headsignal_listener_responsibility | 0.676781 | 0.525981 |
| learned_semantic_router_context_headsignal_listener_responsibility | 0.676786 | 0.526053 |
| semantic_prior_router_listener_responsibility | 0.676796 | 0.526554 |
| head_future_relative_listener_responsibility | 0.676821 | 0.526337 |
| learned_state_router_context_listener_responsibility | 0.676830 | 0.526308 |
| learned_state_router_headsignal_listener_responsibility | 0.676932 | 0.525641 |
| learned_semantic_distilled_router_headsignal_listener_responsibility | 0.676948 | 0.526053 |
| head_current_relative_listener_responsibility | 0.677817 | 0.524116 |
| multihead_current_future_cohort_listener_responsibility | 0.678328 | 0.523250 |
| direct_semantic_listener_responsibility | 0.684005 | 0.524836 |

## Label-Free Router Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | semantic_cross_entropy | ce_lift_vs_prior | ce_lift_vs_semantic | top1_match_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | head_cohort_relative | 0.942764 | 0.964138 | NA | 0.021374 | NA | 0.786260 |
| chronological_holdout | head_current_relative | 0.948227 | 0.979411 | NA | 0.031184 | NA | 0.655398 |
| chronological_holdout | head_future_relative | 0.968099 | 0.980229 | NA | 0.012130 | NA | 0.719738 |
| chronological_holdout | learned_semantic_blend_router_context_headsignal | 1.170901 | 1.097837 | NA | -0.073064 | NA | 0.305344 |
| chronological_holdout | learned_semantic_distilled_router_headsignal | 1.168917 | 1.010263 | NA | -0.158654 | NA | 0.402399 |
| chronological_holdout | learned_semantic_router_context_headsignal | 1.200156 | 1.052950 | NA | -0.147207 | NA | 0.379498 |
| chronological_holdout | learned_state_router_context | 1.094733 | 1.097837 | NA | 0.003103 | NA | 0.422028 |
| chronological_holdout | learned_state_router_context_headsignal | 1.249235 | 1.097837 | NA | -0.151399 | NA | 0.299891 |
| chronological_holdout | learned_state_router_headsignal | 1.273968 | 1.097837 | NA | -0.176132 | NA | 0.266085 |
| row_block_holdout | head_cohort_relative | 0.956157 | 0.977596 | NA | 0.021439 | NA | 0.786667 |
| row_block_holdout | head_current_relative | 0.966638 | 0.994646 | NA | 0.028008 | NA | 0.640317 |
| row_block_holdout | head_future_relative | 0.983781 | 0.994075 | NA | 0.010294 | NA | 0.704127 |
| row_block_holdout | learned_semantic_blend_router_context_headsignal | 1.102217 | 1.099080 | NA | -0.003136 | NA | 0.384762 |
| row_block_holdout | learned_semantic_distilled_router_headsignal | 1.011837 | 1.012655 | NA | 0.000818 | NA | 0.883175 |
| row_block_holdout | learned_semantic_router_context_headsignal | 1.054305 | 1.057085 | NA | 0.002780 | NA | 0.712381 |
| row_block_holdout | learned_state_router_context | 1.094895 | 1.099080 | NA | 0.004185 | NA | 0.426667 |
| row_block_holdout | learned_state_router_context_headsignal | 1.094917 | 1.099080 | NA | 0.004164 | NA | 0.420000 |
| row_block_holdout | learned_state_router_headsignal | 1.094310 | 1.099080 | NA | 0.004770 | NA | 0.424444 |
| subject_heldout | head_cohort_relative | 0.942310 | 0.967328 | NA | 0.025017 | NA | 0.794540 |
| subject_heldout | head_current_relative | 0.957346 | 0.987152 | NA | 0.029806 | NA | 0.651154 |
| subject_heldout | head_future_relative | 0.975560 | 0.987074 | NA | 0.011514 | NA | 0.714095 |
| subject_heldout | learned_semantic_blend_router_context_headsignal | 1.101760 | 1.098389 | NA | -0.003372 | NA | 0.376400 |
| subject_heldout | learned_semantic_distilled_router_headsignal | 1.010583 | 1.011377 | NA | 0.000794 | NA | 0.886543 |
| subject_heldout | learned_semantic_router_context_headsignal | 1.052675 | 1.055147 | NA | 0.002473 | NA | 0.724736 |
| subject_heldout | learned_state_router_context | 1.094670 | 1.098389 | NA | 0.003719 | NA | 0.417846 |
| subject_heldout | learned_state_router_context_headsignal | 1.094562 | 1.098389 | NA | 0.003826 | NA | 0.410294 |
| subject_heldout | learned_state_router_headsignal | 1.093797 | 1.098389 | NA | 0.004592 | NA | 0.415754 |

## Router Weight Summary

| router | target | mean_w_current | mean_w_future | mean_w_cohort | mean_entropy | mean_margin |
| --- | --- | --- | --- | --- | --- | --- |
| learned_semantic_blend_router_context_headsignal | Q1 | 0.296035 | 0.416153 | 0.287811 | 0.984908 | 0.108795 |
| learned_semantic_blend_router_context_headsignal | Q2 | 0.274077 | 0.437181 | 0.288742 | 0.977039 | 0.140032 |
| learned_semantic_blend_router_context_headsignal | Q3 | 0.297671 | 0.391540 | 0.310789 | 0.991215 | 0.071065 |
| learned_semantic_blend_router_context_headsignal | S1 | 0.334437 | 0.385859 | 0.279704 | 0.991374 | 0.051340 |
| learned_semantic_blend_router_context_headsignal | S2 | 0.313958 | 0.386789 | 0.299253 | 0.993413 | 0.068670 |
| learned_semantic_blend_router_context_headsignal | S3 | 0.342488 | 0.315554 | 0.341958 | 0.998024 | 0.023158 |
| learned_semantic_blend_router_context_headsignal | S4 | 0.352737 | 0.296953 | 0.350310 | 0.995341 | 0.033368 |
| learned_semantic_distilled_router_headsignal | Q1 | 0.227657 | 0.596219 | 0.176124 | 0.865468 | 0.368562 |
| learned_semantic_distilled_router_headsignal | Q2 | 0.170596 | 0.655798 | 0.173606 | 0.802862 | 0.478984 |
| learned_semantic_distilled_router_headsignal | Q3 | 0.231944 | 0.532666 | 0.235390 | 0.923361 | 0.291930 |
| learned_semantic_distilled_router_headsignal | S1 | 0.346188 | 0.479271 | 0.174541 | 0.932278 | 0.133083 |
| learned_semantic_distilled_router_headsignal | S2 | 0.286997 | 0.482125 | 0.230878 | 0.954175 | 0.195127 |
| learned_semantic_distilled_router_headsignal | S3 | 0.405585 | 0.242336 | 0.352079 | 0.979983 | 0.053506 |
| learned_semantic_distilled_router_headsignal | S4 | 0.412644 | 0.232678 | 0.354677 | 0.975333 | 0.058220 |
| learned_semantic_router_context_headsignal | Q1 | 0.256823 | 0.520734 | 0.222443 | 0.929587 | 0.260597 |
| learned_semantic_router_context_headsignal | Q2 | 0.210689 | 0.565081 | 0.224230 | 0.895346 | 0.334219 |
| learned_semantic_router_context_headsignal | Q3 | 0.258241 | 0.468356 | 0.273403 | 0.961625 | 0.184353 |
| learned_semantic_router_context_headsignal | S1 | 0.341893 | 0.445751 | 0.212357 | 0.960166 | 0.103858 |
| learned_semantic_router_context_headsignal | S2 | 0.295924 | 0.447238 | 0.256837 | 0.972332 | 0.150498 |
| learned_semantic_router_context_headsignal | S3 | 0.370611 | 0.276953 | 0.352435 | 0.990910 | 0.038642 |
| learned_semantic_router_context_headsignal | S4 | 0.383919 | 0.255897 | 0.360184 | 0.983693 | 0.051896 |
| learned_state_router_context | Q1 | 0.320337 | 0.343971 | 0.335693 | 0.996504 | 0.030158 |
| learned_state_router_context | Q2 | 0.314594 | 0.350558 | 0.334848 | 0.995934 | 0.033726 |
| learned_state_router_context | Q3 | 0.324119 | 0.334072 | 0.341809 | 0.996014 | 0.037473 |
| learned_state_router_context | S1 | 0.326206 | 0.350310 | 0.323484 | 0.997193 | 0.026807 |
| learned_state_router_context | S2 | 0.321021 | 0.352964 | 0.326015 | 0.997508 | 0.025606 |
| learned_state_router_context | S3 | 0.312333 | 0.351658 | 0.336009 | 0.996122 | 0.032612 |
| learned_state_router_context | S4 | 0.328500 | 0.323930 | 0.347570 | 0.995813 | 0.040591 |
| learned_state_router_context_headsignal | Q1 | 0.320823 | 0.344082 | 0.335094 | 0.996386 | 0.031515 |
| learned_state_router_context_headsignal | Q2 | 0.313964 | 0.349510 | 0.336527 | 0.995518 | 0.036655 |
| learned_state_router_context_headsignal | Q3 | 0.323339 | 0.333139 | 0.343522 | 0.995412 | 0.040542 |
| learned_state_router_context_headsignal | S1 | 0.326057 | 0.351321 | 0.322621 | 0.997327 | 0.026663 |
| learned_state_router_context_headsignal | S2 | 0.321473 | 0.352752 | 0.325774 | 0.997588 | 0.026326 |
| learned_state_router_context_headsignal | S3 | 0.311520 | 0.350853 | 0.337627 | 0.995769 | 0.035269 |
| learned_state_router_context_headsignal | S4 | 0.327287 | 0.322236 | 0.350477 | 0.994923 | 0.045699 |
| learned_state_router_headsignal | Q1 | 0.322747 | 0.343277 | 0.333976 | 0.997435 | 0.023611 |
| learned_state_router_headsignal | Q2 | 0.315958 | 0.350777 | 0.333265 | 0.996674 | 0.030111 |
| learned_state_router_headsignal | Q3 | 0.325152 | 0.332945 | 0.341903 | 0.996623 | 0.033410 |
| learned_state_router_headsignal | S1 | 0.327442 | 0.352236 | 0.320321 | 0.997953 | 0.021028 |
| learned_state_router_headsignal | S2 | 0.322268 | 0.351917 | 0.325815 | 0.998297 | 0.020616 |
| learned_state_router_headsignal | S3 | 0.313803 | 0.351986 | 0.334211 | 0.996894 | 0.028820 |
| learned_state_router_headsignal | S4 | 0.329934 | 0.323252 | 0.346814 | 0.996328 | 0.038363 |
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
| learned_state_router_context_listener_responsibility | 0.406667 | 0.126667 | 0.280000 |
| learned_state_router_context_headsignal_listener_responsibility | 0.411111 | 0.126667 | 0.284444 |
| direct_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| learned_semantic_blend_router_context_headsignal_listener_responsibility | 0.442222 | 0.126667 | 0.315556 |
| learned_semantic_router_context_headsignal_listener_responsibility | 0.446667 | 0.126667 | 0.320000 |
| head_current_relative_listener_responsibility | 0.451111 | 0.126667 | 0.324444 |
| semantic_prior_router_listener_responsibility | 0.462222 | 0.126667 | 0.335556 |
| multihead_current_future_cohort_listener_responsibility | 0.466667 | 0.126667 | 0.340000 |
| learned_state_router_headsignal_listener_responsibility | 0.473333 | 0.126667 | 0.346667 |
| head_future_relative_listener_responsibility | 0.475556 | 0.126667 | 0.348889 |
| head_cohort_relative_listener_responsibility | 0.482222 | 0.126667 | 0.355556 |
| learned_semantic_distilled_router_headsignal_listener_responsibility | 0.511111 | 0.126667 | 0.384444 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.940000 | 0.126667 | 0.813333 |

## 해석

이 실험은 HS-JEPA의 논문 포인트를 더 엄격하게 찌른다.
기존 fixed semantic router는 사람이 target 의미를 보고 current/future/cohort head prior를 넣었다.
여기서는 그 prior를 hidden head-suitability prediction으로 대체할 수 있는지 본다.

positive이면:

```text
HS-JEPA can learn listener-head routing as a core pretext objective.
```

negative이면:

```text
The current learned router does not yet replace semantic listener priors.
HS-JEPA still needs a stronger route-suitability target or a better router objective.
```
