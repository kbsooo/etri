# Multi-Head Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 current/future/cohort consistency를 하나의 teacher로 평균내지 않는다.
세 개의 hidden listener-responsibility head를 따로 예측하고,
frozen listener probe가 어떤 head geometry를 읽어야 하는지 검사한다.

```text
subject-relative visible human-life context
  -> current responsibility head
  -> future-consistent responsibility head
  -> cohort-consistent responsibility head
  -> frozen listener reads single/concat/delta head geometry
```

## 판정

- verdict: `multi_head_listener_responsibility_prior_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- teacher: `separate_current_future_cohort_listener_responsibility_heads`
- context encoder: `subject_relative_visible_lifelog_context`

## 핵심 수치

- best single-head feature set: `head_future_relative_listener_responsibility_calibrated10`
- best single-head logloss: `0.677463`
- best multi-head feature set: `multihead_current_future_listener_responsibility_calibrated10`
- best multi-head logloss: `0.677735`
- subject global transport logloss: `0.676724`
- subject direct semantic logloss: `0.677638`
- subject prior logloss: `0.677858`
- delta vs best single head: `0.000272`
- delta vs prior: `-0.000123`
- delta vs raw lifelog PCA: `-0.000778`
- delta vs global transport: `0.001011`
- delta vs direct semantic: `0.000097`
- row-block delta vs global: `-0.000265`
- chronological delta vs global: `-0.001451`

## Label-Free Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | ce_lift_vs_prior | ce_lift_vs_uniform | top1_match_rate |
| --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | head_cohort_relative | 0.942764 | 0.964138 | 0.021374 | 0.666674 | 0.786260 |
| chronological_holdout | head_current_relative | 0.948227 | 0.979411 | 0.031184 | 0.661211 | 0.655398 |
| chronological_holdout | head_future_relative | 0.968099 | 0.980229 | 0.012130 | 0.641339 | 0.719738 |
| row_block_holdout | head_cohort_relative | 0.956157 | 0.977596 | 0.021439 | 0.653281 | 0.786667 |
| row_block_holdout | head_current_relative | 0.966638 | 0.994646 | 0.028008 | 0.642800 | 0.640317 |
| row_block_holdout | head_future_relative | 0.983781 | 0.994075 | 0.010294 | 0.625657 | 0.704127 |
| subject_heldout | head_cohort_relative | 0.942310 | 0.967328 | 0.025017 | 0.667128 | 0.794540 |
| subject_heldout | head_current_relative | 0.957346 | 0.987152 | 0.029806 | 0.652092 | 0.651154 |
| subject_heldout | head_future_relative | 0.975560 | 0.987074 | 0.011514 | 0.633878 | 0.714095 |

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| head_future_relative_listener_responsibility_calibrated10 | 0.677463 | 0.394162 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.677507 | 0.392582 |
| head_current_relative_listener_responsibility_calibrated10 | 0.677614 | 0.391306 |
| direct_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| multihead_current_future_listener_responsibility_calibrated10 | 0.677735 | 0.393815 |
| multihead_future_cohort_listener_responsibility_calibrated10 | 0.677759 | 0.393084 |
| multihead_current_cohort_listener_responsibility_calibrated10 | 0.677765 | 0.392173 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.677966 | 0.393316 |
| raw_lifelog_pca_calibrated10 | 0.678513 | 0.415359 |
| multihead_delta_listener_responsibility_calibrated10 | 0.678629 | 0.381398 |
| head_cohort_relative_listener_responsibility | 0.695126 | 0.478843 |
| head_current_relative_listener_responsibility | 0.696035 | 0.476723 |
| head_future_relative_listener_responsibility | 0.696191 | 0.482610 |
| direct_semantic_listener_responsibility | 0.698179 | 0.473842 |
| multihead_current_cohort_listener_responsibility | 0.701959 | 0.478489 |
| multihead_current_future_listener_responsibility | 0.702416 | 0.477675 |
| multihead_future_cohort_listener_responsibility | 0.702867 | 0.478473 |
| multihead_current_future_cohort_listener_responsibility | 0.707799 | 0.475590 |
| multihead_delta_listener_responsibility | 0.715945 | 0.443376 |
| global_transported_prototype | 0.736658 | 0.500467 |
| raw_lifelog_pca | 1.087640 | 0.501735 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668480 | 0.481690 |
| head_future_relative_listener_responsibility_calibrated10 | 0.673025 | 0.409507 |
| multihead_current_future_listener_responsibility_calibrated10 | 0.673065 | 0.409688 |
| multihead_delta_listener_responsibility_calibrated10 | 0.673102 | 0.420065 |
| head_current_relative_listener_responsibility_calibrated10 | 0.673296 | 0.404646 |
| multihead_future_cohort_listener_responsibility_calibrated10 | 0.673326 | 0.406696 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.673364 | 0.407183 |
| direct_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.673415 | 0.405275 |
| multihead_current_cohort_listener_responsibility_calibrated10 | 0.673489 | 0.403800 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| head_future_relative_listener_responsibility | 0.678622 | 0.492005 |
| head_current_relative_listener_responsibility | 0.679651 | 0.484592 |
| head_cohort_relative_listener_responsibility | 0.680577 | 0.480986 |
| multihead_current_future_listener_responsibility | 0.682301 | 0.495899 |
| multihead_future_cohort_listener_responsibility | 0.685401 | 0.483447 |
| multihead_current_cohort_listener_responsibility | 0.685403 | 0.480010 |
| direct_semantic_listener_responsibility | 0.686009 | 0.497482 |
| multihead_current_future_cohort_listener_responsibility | 0.687692 | 0.485557 |
| raw_lifelog_pca | 0.693523 | 0.581903 |
| multihead_delta_listener_responsibility | 0.694429 | 0.491538 |
| global_transported_prototype | 0.728298 | 0.506119 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.665020 | 0.596837 |
| head_cohort_relative_listener_responsibility_calibrated10 | 0.669977 | 0.526756 |
| multihead_future_cohort_listener_responsibility_calibrated10 | 0.670025 | 0.524198 |
| multihead_current_cohort_listener_responsibility_calibrated10 | 0.670039 | 0.523669 |
| multihead_current_future_cohort_listener_responsibility_calibrated10 | 0.670053 | 0.523250 |
| head_future_relative_listener_responsibility_calibrated10 | 0.670077 | 0.526337 |
| multihead_current_future_listener_responsibility_calibrated10 | 0.670086 | 0.524267 |
| head_current_relative_listener_responsibility_calibrated10 | 0.670108 | 0.524116 |
| direct_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| multihead_delta_listener_responsibility_calibrated10 | 0.670234 | 0.515628 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| head_cohort_relative_listener_responsibility | 0.676021 | 0.526756 |
| head_future_relative_listener_responsibility | 0.676821 | 0.526337 |
| multihead_future_cohort_listener_responsibility | 0.677427 | 0.524198 |
| head_current_relative_listener_responsibility | 0.677817 | 0.524116 |
| multihead_current_cohort_listener_responsibility | 0.677889 | 0.523669 |
| multihead_current_future_cohort_listener_responsibility | 0.678328 | 0.523250 |
| multihead_current_future_listener_responsibility | 0.678349 | 0.524267 |
| direct_semantic_listener_responsibility | 0.684005 | 0.524836 |
| raw_lifelog_pca | 0.717395 | 0.596837 |
| global_transported_prototype | 0.748130 | 0.491242 |
| multihead_delta_listener_responsibility | 2.094809 | 0.515628 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| multihead_delta_listener_responsibility | 0.213333 | 0.126667 | 0.086667 |
| direct_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| head_current_relative_listener_responsibility | 0.451111 | 0.126667 | 0.324444 |
| multihead_current_cohort_listener_responsibility | 0.460000 | 0.126667 | 0.333333 |
| multihead_current_future_listener_responsibility | 0.466667 | 0.126667 | 0.340000 |
| multihead_current_future_cohort_listener_responsibility | 0.466667 | 0.126667 | 0.340000 |
| multihead_future_cohort_listener_responsibility | 0.468889 | 0.126667 | 0.342222 |
| head_future_relative_listener_responsibility | 0.475556 | 0.126667 | 0.348889 |
| head_cohort_relative_listener_responsibility | 0.482222 | 0.126667 | 0.355556 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.940000 | 0.126667 | 0.813333 |

## 해석

positive이면:

```text
HS-JEPA should preserve current/future/cohort responsibility as separate heads.
The useful human-state interface is not a smoothed invariant teacher but a
route-preserving multi-head representation.
```

negative이면:

```text
current/future/cohort separation is not enough; the missing component is not
head preservation but a stronger listener decoder or a better hidden teacher.
```
