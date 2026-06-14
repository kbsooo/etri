# Invariant Listener Responsibility Pretext Core

## 한 줄 요약

이 실험은 현재 row의 listener responsibility만 맞히지 않는다.
같은 subject의 인접 episode와 다른 subject의 유사 episode를 함께 보아
future/cohort-consistent listener responsibility teacher를 만든 뒤,
subject-relative visible context가 그 hidden teacher를 예측하게 한다.

```text
current transported responsibility
  + future episode consistency
  + cross-subject cohort consistency
  -> invariant listener responsibility teacher
  -> subject-relative context prediction
```

## 판정

- verdict: `invariant_listener_responsibility_beats_current_positive`
- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- label을 pretext target으로 사용: `False`
- teacher: `current_plus_future_plus_cross_subject_cohort_transport_reliability`
- context encoder: `subject_relative_visible_lifelog_context`

## 핵심 수치

- best invariant feature set: `future_only_relative_balanced_listener_responsibility_calibrated10`
- subject best invariant logloss: `0.677643`
- subject current-relative logloss: `0.677901`
- subject global transport logloss: `0.676724`
- subject direct semantic logloss: `0.677638`
- subject prior logloss: `0.677858`
- delta vs current-relative: `-0.000258`
- delta vs direct semantic: `0.000005`
- delta vs prior: `-0.000214`
- delta vs raw lifelog PCA: `-0.001064`
- delta vs global transport: `0.000919`
- row-block delta vs global: `-0.000612`
- chronological delta vs global: `-0.001460`

## Label-Free Pretext Quality

| split | feature_set | pretext_cross_entropy | prior_cross_entropy | ce_lift_vs_prior | ce_lift_vs_uniform | top1_match_rate |
| --- | --- | --- | --- | --- | --- | --- |
| chronological_holdout | cohort_only_relative_balanced | 0.942764 | 0.964138 | 0.021374 | 0.666674 | 0.786260 |
| chronological_holdout | current_relative_semantic_balanced | 0.948227 | 0.979411 | 0.031184 | 0.661211 | 0.655398 |
| chronological_holdout | future_cohort_relative_balanced | 0.957576 | 0.972864 | 0.015288 | 0.651862 | 0.770992 |
| chronological_holdout | future_only_relative_balanced | 0.968099 | 0.980229 | 0.012130 | 0.641339 | 0.719738 |
| chronological_holdout | invariant_mix_relative_balanced | 0.954285 | 0.975731 | 0.021447 | 0.655153 | 0.690294 |
| chronological_holdout | invariant_mix_relative_conservative | 0.964962 | 0.975731 | 0.010770 | 0.644476 | 0.682661 |
| row_block_holdout | cohort_only_relative_balanced | 0.956157 | 0.977596 | 0.021439 | 0.653281 | 0.786667 |
| row_block_holdout | current_relative_semantic_balanced | 0.966638 | 0.994646 | 0.028008 | 0.642800 | 0.640317 |
| row_block_holdout | future_cohort_relative_balanced | 0.971750 | 0.986568 | 0.014818 | 0.637688 | 0.767619 |
| row_block_holdout | future_only_relative_balanced | 0.983781 | 0.994075 | 0.010294 | 0.625657 | 0.704127 |
| row_block_holdout | invariant_mix_relative_balanced | 0.970129 | 0.990113 | 0.019985 | 0.639309 | 0.696825 |
| row_block_holdout | invariant_mix_relative_conservative | 0.980228 | 0.990113 | 0.009885 | 0.629210 | 0.685714 |
| subject_heldout | cohort_only_relative_balanced | 0.942310 | 0.967328 | 0.025017 | 0.667128 | 0.794540 |
| subject_heldout | current_relative_semantic_balanced | 0.957346 | 0.987152 | 0.029806 | 0.652092 | 0.651154 |
| subject_heldout | future_cohort_relative_balanced | 0.961250 | 0.978272 | 0.017022 | 0.648188 | 0.777628 |
| subject_heldout | future_only_relative_balanced | 0.975560 | 0.987074 | 0.011514 | 0.633878 | 0.714095 |
| subject_heldout | invariant_mix_relative_balanced | 0.959876 | 0.982242 | 0.022366 | 0.649562 | 0.710332 |
| subject_heldout | invariant_mix_relative_conservative | 0.971161 | 0.982242 | 0.011080 | 0.638276 | 0.697914 |

## Subject-Heldout Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| global_transported_prototype_calibrated10 | 0.676724 | 0.400691 |
| direct_semantic_listener_responsibility_calibrated10 | 0.677638 | 0.391800 |
| future_only_relative_balanced_listener_responsibility_calibrated10 | 0.677643 | 0.393354 |
| future_cohort_relative_balanced_listener_responsibility_calibrated10 | 0.677787 | 0.390061 |
| invariant_mix_relative_balanced_listener_responsibility_calibrated10 | 0.677836 | 0.390011 |
| prior_only | 0.677858 | 0.382414 |
| prior_only_calibrated10 | 0.677858 | 0.382414 |
| current_relative_semantic_balanced_listener_responsibility_calibrated10 | 0.677901 | 0.389895 |
| invariant_mix_relative_conservative_listener_responsibility_calibrated10 | 0.677960 | 0.388686 |
| cohort_only_relative_balanced_listener_responsibility_calibrated10 | 0.678031 | 0.386962 |
| raw_lifelog_pca_calibrated10 | 0.678707 | 0.417426 |
| direct_semantic_listener_responsibility | 0.698179 | 0.473842 |
| future_only_relative_balanced_listener_responsibility | 0.703748 | 0.481775 |
| current_relative_semantic_balanced_listener_responsibility | 0.705159 | 0.472176 |
| future_cohort_relative_balanced_listener_responsibility | 0.705237 | 0.476811 |
| invariant_mix_relative_balanced_listener_responsibility | 0.705576 | 0.475659 |
| cohort_only_relative_balanced_listener_responsibility | 0.707803 | 0.469552 |
| invariant_mix_relative_conservative_listener_responsibility | 0.707945 | 0.474083 |
| global_transported_prototype | 0.736658 | 0.500467 |
| raw_lifelog_pca | 1.268418 | 0.498364 |

## Row-Block Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.668246 | 0.483958 |
| future_only_relative_balanced_listener_responsibility_calibrated10 | 0.672719 | 0.414067 |
| current_relative_semantic_balanced_listener_responsibility_calibrated10 | 0.672783 | 0.410785 |
| invariant_mix_relative_balanced_listener_responsibility_calibrated10 | 0.672925 | 0.411549 |
| invariant_mix_relative_conservative_listener_responsibility_calibrated10 | 0.673024 | 0.410576 |
| future_cohort_relative_balanced_listener_responsibility_calibrated10 | 0.673136 | 0.410020 |
| global_transported_prototype_calibrated10 | 0.673331 | 0.422598 |
| direct_semantic_listener_responsibility_calibrated10 | 0.673375 | 0.413186 |
| cohort_only_relative_balanced_listener_responsibility_calibrated10 | 0.673504 | 0.404467 |
| prior_only_calibrated10 | 0.674078 | 0.401854 |
| prior_only | 0.674078 | 0.401854 |
| current_relative_semantic_balanced_listener_responsibility | 0.682242 | 0.499173 |
| future_only_relative_balanced_listener_responsibility | 0.683625 | 0.504541 |
| invariant_mix_relative_balanced_listener_responsibility | 0.684627 | 0.497345 |
| invariant_mix_relative_conservative_listener_responsibility | 0.685983 | 0.494556 |
| direct_semantic_listener_responsibility | 0.686009 | 0.497482 |
| raw_lifelog_pca | 0.686287 | 0.588427 |
| future_cohort_relative_balanced_listener_responsibility | 0.686874 | 0.493989 |
| cohort_only_relative_balanced_listener_responsibility | 0.687548 | 0.481978 |
| global_transported_prototype | 0.728298 | 0.506119 |

## Chronological Frozen Probe

| feature_set | logloss | auc |
| --- | --- | --- |
| raw_lifelog_pca_calibrated10 | 0.664773 | 0.603053 |
| invariant_mix_relative_conservative_listener_responsibility_calibrated10 | 0.669968 | 0.527164 |
| cohort_only_relative_balanced_listener_responsibility_calibrated10 | 0.669972 | 0.526724 |
| future_cohort_relative_balanced_listener_responsibility_calibrated10 | 0.670025 | 0.526616 |
| invariant_mix_relative_balanced_listener_responsibility_calibrated10 | 0.670070 | 0.526099 |
| future_only_relative_balanced_listener_responsibility_calibrated10 | 0.670076 | 0.526608 |
| current_relative_semantic_balanced_listener_responsibility_calibrated10 | 0.670108 | 0.523874 |
| direct_semantic_listener_responsibility_calibrated10 | 0.670193 | 0.524836 |
| prior_only_calibrated10 | 0.670826 | 0.500000 |
| prior_only | 0.670826 | 0.500000 |
| global_transported_prototype_calibrated10 | 0.671537 | 0.491242 |
| invariant_mix_relative_conservative_listener_responsibility | 0.675486 | 0.527164 |
| cohort_only_relative_balanced_listener_responsibility | 0.676235 | 0.526724 |
| future_cohort_relative_balanced_listener_responsibility | 0.676533 | 0.526616 |
| future_only_relative_balanced_listener_responsibility | 0.677077 | 0.526608 |
| invariant_mix_relative_balanced_listener_responsibility | 0.677195 | 0.526099 |
| current_relative_semantic_balanced_listener_responsibility | 0.678071 | 0.523874 |
| direct_semantic_listener_responsibility | 0.684005 | 0.524836 |
| raw_lifelog_pca | 0.715704 | 0.603053 |
| global_transported_prototype | 0.748130 | 0.491242 |

## Subject Leakage Diagnostic

| feature_set | subject_id_accuracy | chance_accuracy | leakage_lift_vs_chance |
| --- | --- | --- | --- |
| direct_semantic_listener_responsibility | 0.437778 | 0.126667 | 0.311111 |
| cohort_only_relative_balanced_listener_responsibility | 0.471111 | 0.126667 | 0.344444 |
| invariant_mix_relative_balanced_listener_responsibility | 0.475556 | 0.126667 | 0.348889 |
| future_cohort_relative_balanced_listener_responsibility | 0.475556 | 0.126667 | 0.348889 |
| current_relative_semantic_balanced_listener_responsibility | 0.480000 | 0.126667 | 0.353333 |
| future_only_relative_balanced_listener_responsibility | 0.480000 | 0.126667 | 0.353333 |
| invariant_mix_relative_conservative_listener_responsibility | 0.495556 | 0.126667 | 0.368889 |
| global_transported_prototype | 0.542222 | 0.126667 | 0.415556 |
| raw_lifelog_pca | 0.957778 | 0.126667 | 0.831111 |

## 해석

positive이면:

```text
HS-JEPA listener responsibility becomes more stable when the hidden teacher
is constrained by future and cohort consistency rather than current-row reliability alone.
```

negative이면:

```text
future/cohort smoothing destroys target-specific listener signal, so invariant responsibility
must be learned as a multi-head objective rather than a smoothed single teacher.
```
