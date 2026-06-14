# Learned Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 hand-coded listener profile을 그대로 쓰지 않는다.
OG visible human-life context만 보고 transported prototype reliability에서 만든
hidden listener responsibility field를 예측한다.

```text
visible human-life context
  -> hidden transported listener-responsibility field
  -> frozen subject-heldout / row-block probes
```

## 판정

- verdict: `learned_listener_responsibility_beats_handcoded_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- pretext teacher: `transported_prototype_confidence_entropy_energy`
- context encoder: `ridge_alpha_12.0_over_visible_lifelog_context`

## 핵심 수치

- best learned feature set: `learned_semantic_balanced_listener_responsibility_calibrated10`
- subject best learned logloss: `0.677143`
- subject global transport logloss: `0.676724`
- subject direct semantic logloss: `0.677638`
- subject prior logloss: `0.677858`
- delta vs prior: `-0.000715`
- delta vs raw lifelog PCA: `-0.001565`
- delta vs global transport: `0.000419`
- delta vs direct semantic: `-0.000495`
- row-block delta vs global: `-0.000051`
- chronological delta vs global: `-0.001510`

## Label-Free Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | ce_lift_vs_prior | ce_lift_vs_uniform | top1_match_rate |
| --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | learned_family_balanced | 1.455648 | 1.496343 | 0.040695 | 0.153790 | 0.583424 |
| chronological_holdout | learned_generic_balanced | 1.502391 | 1.545171 | 0.042780 | 0.107047 | 0.458015 |
| chronological_holdout | learned_semantic_balanced | 0.950209 | 0.979411 | 0.029202 | 0.659229 | 0.652126 |
| chronological_holdout | learned_semantic_conservative | 0.964291 | 0.979411 | 0.015120 | 0.645147 | 0.643402 |
| chronological_holdout | learned_semantic_open_loop | 0.951760 | 0.979411 | 0.027651 | 0.657678 | 0.679389 |
| chronological_holdout | learned_semantic_relative_balanced | 0.948227 | 0.979411 | 0.031184 | 0.661211 | 0.655398 |
| chronological_holdout | learned_semantic_relative_conservative | 0.963192 | 0.979411 | 0.016219 | 0.646246 | 0.642312 |
| row_block_holdout | learned_family_balanced | 1.469910 | 1.502124 | 0.032214 | 0.139528 | 0.633968 |
| row_block_holdout | learned_generic_balanced | 1.517468 | 1.550018 | 0.032550 | 0.091969 | 0.533333 |
| row_block_holdout | learned_semantic_balanced | 0.969605 | 0.994646 | 0.025041 | 0.639833 | 0.641587 |
| row_block_holdout | learned_semantic_conservative | 0.981601 | 0.994646 | 0.013045 | 0.627837 | 0.624127 |
| row_block_holdout | learned_semantic_open_loop | 0.975455 | 0.994646 | 0.019191 | 0.633983 | 0.668889 |
| row_block_holdout | learned_semantic_relative_balanced | 0.966638 | 0.994646 | 0.028008 | 0.642800 | 0.640317 |
| row_block_holdout | learned_semantic_relative_conservative | 0.980145 | 0.994646 | 0.014501 | 0.629293 | 0.624762 |
| subject_heldout | learned_family_balanced | 1.485297 | 1.497105 | 0.011808 | 0.124140 | 0.570503 |
| subject_heldout | learned_generic_balanced | 1.527597 | 1.541120 | 0.013523 | 0.081840 | 0.549498 |
| subject_heldout | learned_semantic_balanced | 0.973911 | 0.987152 | 0.013241 | 0.635527 | 0.632861 |
| subject_heldout | learned_semantic_conservative | 0.976109 | 0.987152 | 0.011043 | 0.633328 | 0.622497 |
| subject_heldout | learned_semantic_open_loop | 1.931600 | 0.987152 | -0.944448 | -0.322162 | 0.629028 |
| subject_heldout | learned_semantic_relative_balanced | 0.957346 | 0.987152 | 0.029806 | 0.652092 | 0.651154 |
| subject_heldout | learned_semantic_relative_conservative | 0.971673 | 0.987152 | 0.015479 | 0.637765 | 0.627576 |

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| learned_semantic_balanced_listener_responsibility_calibrated10 | 0.677143 | 0.394607 |
| learned_semantic_conservative_listener_responsibility_calibrated10 | 0.677275 | 0.394979 |
| learned_semantic_open_loop_listener_responsibility_calibrated10 | 0.677443 | 0.393271 |
| direct_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| direct_family_listener_responsibility_calibrated10 | 0.677683 | 0.389376 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| learned_semantic_relative_balanced_listener_responsibility_calibrated10 | 0.677901 | 0.389895 |
| learned_semantic_relative_conservative_listener_responsibility_calibrated10 | 0.678043 | 0.388256 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| learned_family_balanced_listener_responsibility_calibrated10 | 0.679023 | 0.386671 |
| learned_generic_balanced_listener_responsibility_calibrated10 | 0.679568 | 0.382470 |
| direct_semantic_listener_responsibility | 0.698179 | 0.473842 |
| direct_family_listener_responsibility | 0.700823 | 0.468973 |
| learned_semantic_relative_balanced_listener_responsibility | 0.705159 | 0.472176 |
| learned_semantic_relative_conservative_listener_responsibility | 0.707387 | 0.470531 |
| learned_semantic_balanced_listener_responsibility | 0.715437 | 0.491929 |
| learned_semantic_conservative_listener_responsibility | 0.717108 | 0.489962 |
| learned_semantic_open_loop_listener_responsibility | 0.725341 | 0.483257 |

## Best Learned Target Probe

| target | logloss | auc |
| --- | --- | --- |
| Q1 | 0.704261 | 0.397029 |
| Q2 | 0.696206 | 0.415200 |
| Q3 | 0.679219 | 0.438107 |
| S1 | 0.644777 | 0.360789 |
| S2 | 0.659303 | 0.402056 |
| S3 | 0.658993 | 0.342304 |
| S4 | 0.697241 | 0.406766 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| learned_generic_balanced_listener_responsibility_calibrated10 | 0.672707 | 0.409036 |
| learned_semantic_relative_balanced_listener_responsibility_calibrated10 | 0.672783 | 0.410785 |
| learned_semantic_relative_conservative_listener_responsibility_calibrated10 | 0.672826 | 0.410512 |
| learned_family_balanced_listener_responsibility_calibrated10 | 0.672989 | 0.405596 |
| direct_family_listener_responsibility_calibrated10 | 0.673158 | 0.412629 |
| learned_semantic_open_loop_listener_responsibility_calibrated10 | 0.673222 | 0.406393 |
| learned_semantic_balanced_listener_responsibility_calibrated10 | 0.673280 | 0.405088 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| direct_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| learned_semantic_conservative_listener_responsibility_calibrated10 | 0.673501 | 0.404973 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| learned_semantic_relative_balanced_listener_responsibility | 0.682242 | 0.499173 |
| learned_semantic_relative_conservative_listener_responsibility | 0.682955 | 0.497810 |
| learned_generic_balanced_listener_responsibility | 0.684295 | 0.498914 |
| direct_semantic_listener_responsibility | 0.686009 | 0.497482 |
| learned_family_balanced_listener_responsibility | 0.686261 | 0.490663 |
| raw_lifelog_pca | 0.686287 | 0.588427 |
| learned_semantic_open_loop_listener_responsibility | 0.686344 | 0.498734 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| learned_semantic_conservative_listener_responsibility_calibrated10 | 0.669964 | 0.529204 |
| learned_semantic_relative_conservative_listener_responsibility_calibrated10 | 0.669997 | 0.527504 |
| learned_semantic_balanced_listener_responsibility_calibrated10 | 0.670027 | 0.527600 |
| learned_semantic_relative_balanced_listener_responsibility_calibrated10 | 0.670108 | 0.523874 |
| direct_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| learned_semantic_open_loop_listener_responsibility_calibrated10 | 0.670215 | 0.519543 |
| learned_family_balanced_listener_responsibility_calibrated10 | 0.670220 | 0.511899 |
| learned_generic_balanced_listener_responsibility_calibrated10 | 0.670462 | 0.502972 |
| direct_family_listener_responsibility_calibrated10 | 0.670775 | 0.498091 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| learned_semantic_conservative_listener_responsibility | 0.675521 | 0.529204 |
| learned_semantic_relative_conservative_listener_responsibility | 0.675885 | 0.527504 |
| learned_semantic_balanced_listener_responsibility | 0.677150 | 0.527600 |
| learned_semantic_relative_balanced_listener_responsibility | 0.678071 | 0.523874 |
| learned_family_balanced_listener_responsibility | 0.682904 | 0.511899 |
| direct_semantic_listener_responsibility | 0.684005 | 0.524836 |
| learned_semantic_open_loop_listener_responsibility | 0.685948 | 0.519543 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| direct_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| learned_semantic_relative_balanced_listener_responsibility | 0.480000 | 0.126667 | 0.353333 |
| learned_semantic_relative_conservative_listener_responsibility | 0.491111 | 0.126667 | 0.364444 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| learned_generic_balanced_listener_responsibility | 0.722222 | 0.126667 | 0.595556 |
| learned_family_balanced_listener_responsibility | 0.775556 | 0.126667 | 0.648889 |
| learned_semantic_open_loop_listener_responsibility | 0.784444 | 0.126667 | 0.657778 |
| learned_semantic_conservative_listener_responsibility | 0.797778 | 0.126667 | 0.671111 |
| learned_semantic_balanced_listener_responsibility | 0.800000 | 0.126667 | 0.673333 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## 해석

이 실험은 HS-JEPA를 다음 주장으로 좁힌다.

```text
listener responsibility는 사람이 target 설명으로 고정하는 profile이 아니라,
visible human context에서 hidden transported grammar를 예측하는 pretext여야 한다.
```

성공이면:

```text
HS-JEPA core can learn a listener-responsibility interface without labels.
```

실패이면:

```text
transported grammar는 존재하지만 listener responsibility를 raw context encoder만으로
학습하기에는 teacher나 objective가 아직 약하다. 다음 core는 future/cohort consistency를
teacher에 포함해야 한다.
```
