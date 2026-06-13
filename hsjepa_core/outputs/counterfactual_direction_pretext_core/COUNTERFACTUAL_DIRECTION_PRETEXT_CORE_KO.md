# Counterfactual Direction Pretext Core

## 한 줄 요약

raw/inverse action 방향 선택을 adapter heuristic으로 두지 않고,
HS-JEPA의 hidden target representation으로 끌어올릴 수 있는지 검증했다.

```text
visible human-state context + target listener
  -> counterfactual direction representation
  -> responsibility-high row-target cell에서 raw 또는 inverse 선택
```

## 왜 필요한가

직전 signed-direction 실험은 action translation 독성을 수리했지만,
best family가 `action_geometry_direction`이었다.
즉 점수 관점에서는 좋아도 논문 관점에서는 pure HS-JEPA core 증거가 약했다.

이번 실험은 같은 문제를 cell-level counterfactual target으로 다시 정의했다.

```text
hidden target = raw gain > inverse gain 인가?
```

core feature는 action probability, action magnitude, previous submission probability, public LB를 쓰지 않는다.
`action_geometry_reference`는 adapter reference로만 보고한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probabilities: `False`
- proprietary embedding API: `False`
- action probability as core feature: `False`
- label-informed peer margin: `False`

## Verdict

- verdict: `counterfactual_direction_pretext_negative`
- responsibility source: `masked_pretext_listener_responsibility`
- best overall family: `human_plus_masked_pretext_direction`
- best core family: `human_plus_masked_pretext_direction`
- best core AP lift: `0.011620`
- best core responsibility-gated gain: `-0.848511`
- action-geometry reference gain: `-1.239670`
- oracle responsibility-gated gain: `14.946064`
- released test cells: `67`
- candidate: `submission_hsjepa_counterfactual_direction_pretext_d9e2a870_uploadsafe.csv`

## Direction Family Leaderboard

| feature_family | feature_count | raw_better_rate | auc | ap | ap_lift_vs_rate | all_gain_sum | responsibility_gain_sum | responsibility_positive_rate | responsibility_raw_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_plus_masked_pretext_direction | 163 | 0.498095 | 0.521613 | 0.509715 | 0.011620 | -53.856580 | -0.848511 | 0.516667 | 0.516667 |
| responsibility_weighted_pretext_direction | 49 | 0.498095 | 0.527971 | 0.514112 | 0.016016 | -48.306964 | -1.226020 | 0.566667 | 0.333333 |
| action_geometry_reference | 20 | 0.498095 | 0.597807 | 0.586391 | 0.088295 | -61.563410 | -1.239670 | 0.575000 | 0.525000 |
| human_context_direction | 128 | 0.498095 | 0.509190 | 0.502947 | 0.004852 | -55.080719 | -1.945516 | 0.500000 | 0.666667 |
| masked_pretext_direction | 48 | 0.498095 | 0.531273 | 0.517723 | 0.019628 | -51.466928 | -4.767804 | 0.458333 | 0.625000 |
| listener_only_direction | 14 | 0.498095 | 0.479214 | 0.470251 | -0.027845 | -63.998873 | -5.905396 | 0.441667 | 0.941667 |

## Baselines

| baseline | all_gain_sum | all_positive_rate | responsibility_gain_sum | responsibility_positive_rate | responsibility_raw_rate |
| --- | --- | --- | --- | --- | --- |
| always_raw | -48.053725 | 0.498095 | -6.190934 | 0.433333 | 1.000000 |
| always_inverse | -93.386072 | 0.501905 | 1.209666 | 0.566667 | 0.000000 |
| oracle_direction | 460.256847 | 1.000000 | 14.946064 | 1.000000 | 0.433333 |

## Target-Level Direction Metrics

| feature_family | target | raw_better_rate | auc | ap | direction_gain_sum | direction_positive_rate | direction_raw_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| action_geometry_reference | S4 | 0.520000 | 0.571413 | 0.574008 | -1.994154 | 0.533333 | 0.537778 |
| action_geometry_reference | S1 | 0.515556 | 0.683031 | 0.684414 | -8.105433 | 0.657778 | 0.506667 |
| action_geometry_reference | S3 | 0.417778 | 0.626563 | 0.530562 | -8.622888 | 0.597778 | 0.362222 |
| action_geometry_reference | Q3 | 0.491111 | 0.573208 | 0.532260 | -9.817488 | 0.531111 | 0.337778 |
| action_geometry_reference | Q2 | 0.524444 | 0.544591 | 0.587091 | -10.639023 | 0.522222 | 0.495556 |
| action_geometry_reference | S2 | 0.524444 | 0.644771 | 0.641536 | -10.819777 | 0.611111 | 0.557778 |
| action_geometry_reference | Q1 | 0.493333 | 0.474030 | 0.505967 | -11.564648 | 0.477778 | 0.504444 |
| human_context_direction | S4 | 0.520000 | 0.501543 | 0.506512 | -0.557905 | 0.520000 | 0.631111 |
| human_context_direction | Q1 | 0.493333 | 0.509977 | 0.498003 | -1.318393 | 0.524444 | 0.577778 |
| human_context_direction | Q2 | 0.524444 | 0.458043 | 0.495227 | -3.762131 | 0.495556 | 0.660000 |
| human_context_direction | S2 | 0.524444 | 0.508257 | 0.538328 | -6.394480 | 0.524444 | 0.573333 |
| human_context_direction | Q3 | 0.491111 | 0.547827 | 0.539930 | -9.688380 | 0.537778 | 0.455556 |
| human_context_direction | S1 | 0.515556 | 0.546900 | 0.577215 | -15.371061 | 0.544444 | 0.517778 |
| human_context_direction | S3 | 0.417778 | 0.418893 | 0.360558 | -17.988371 | 0.475556 | 0.302222 |
| human_plus_masked_pretext_direction | S4 | 0.520000 | 0.540677 | 0.550323 | 2.459378 | 0.542222 | 0.537778 |
| human_plus_masked_pretext_direction | Q1 | 0.493333 | 0.497451 | 0.484163 | -2.980410 | 0.522222 | 0.535556 |
| human_plus_masked_pretext_direction | Q2 | 0.524444 | 0.477032 | 0.499657 | -4.338992 | 0.488889 | 0.595556 |
| human_plus_masked_pretext_direction | Q3 | 0.491111 | 0.509415 | 0.522448 | -5.155924 | 0.517778 | 0.435556 |
| human_plus_masked_pretext_direction | S2 | 0.524444 | 0.536423 | 0.551849 | -10.040056 | 0.517778 | 0.513333 |
| human_plus_masked_pretext_direction | S3 | 0.417778 | 0.496447 | 0.401208 | -15.869795 | 0.508889 | 0.273333 |
| human_plus_masked_pretext_direction | S1 | 0.515556 | 0.549272 | 0.566692 | -17.930780 | 0.524444 | 0.417778 |
| listener_only_direction | S4 | 0.520000 | 0.466198 | 0.506048 | 0.407368 | 0.520000 | 1.000000 |
| listener_only_direction | Q2 | 0.524444 | 0.405136 | 0.469442 | -0.548096 | 0.524444 | 1.000000 |
| listener_only_direction | S3 | 0.417778 | 0.410376 | 0.368445 | -7.390146 | 0.582222 | 0.000000 |
| listener_only_direction | Q3 | 0.491111 | 0.436741 | 0.454782 | -10.840523 | 0.466667 | 0.197778 |
| listener_only_direction | Q1 | 0.493333 | 0.434339 | 0.459016 | -11.224575 | 0.453333 | 0.795556 |
| listener_only_direction | S1 | 0.515556 | 0.401979 | 0.462960 | -11.593914 | 0.462222 | 0.800000 |
| listener_only_direction | S2 | 0.524444 | 0.406077 | 0.469533 | -22.808987 | 0.437778 | 0.597778 |
| masked_pretext_direction | Q1 | 0.493333 | 0.515825 | 0.494698 | -0.640610 | 0.520000 | 0.577778 |
| masked_pretext_direction | S4 | 0.520000 | 0.524513 | 0.552611 | -5.701043 | 0.480000 | 0.555556 |
| masked_pretext_direction | S3 | 0.417778 | 0.577564 | 0.462612 | -5.890731 | 0.553333 | 0.291111 |
| masked_pretext_direction | Q3 | 0.491111 | 0.522249 | 0.545932 | -6.362786 | 0.520000 | 0.420000 |
| masked_pretext_direction | Q2 | 0.524444 | 0.459449 | 0.491697 | -8.700788 | 0.497778 | 0.626667 |
| masked_pretext_direction | S1 | 0.515556 | 0.546356 | 0.561241 | -10.509683 | 0.517778 | 0.473333 |
| masked_pretext_direction | S2 | 0.524444 | 0.532512 | 0.536022 | -13.661287 | 0.517778 | 0.451111 |
| responsibility_weighted_pretext_direction | Q1 | 0.493333 | 0.506954 | 0.484948 | 0.464699 | 0.517778 | 0.620000 |
| responsibility_weighted_pretext_direction | S4 | 0.520000 | 0.539530 | 0.556569 | -0.229704 | 0.524444 | 0.497778 |
| responsibility_weighted_pretext_direction | S3 | 0.417778 | 0.573118 | 0.461525 | -3.581080 | 0.555556 | 0.306667 |
| responsibility_weighted_pretext_direction | Q3 | 0.491111 | 0.496888 | 0.507824 | -5.835986 | 0.504444 | 0.400000 |
| responsibility_weighted_pretext_direction | S2 | 0.524444 | 0.539710 | 0.546901 | -9.812195 | 0.531111 | 0.455556 |
| responsibility_weighted_pretext_direction | S1 | 0.515556 | 0.545763 | 0.570538 | -13.461278 | 0.522222 | 0.468889 |
| responsibility_weighted_pretext_direction | Q2 | 0.524444 | 0.452420 | 0.485437 | -15.851419 | 0.477778 | 0.637778 |

## Fold Stability

| feature_family | fold | heldout_subjects | positive_rate | auc | ap |
| --- | --- | --- | --- | --- | --- |
| listener_only_direction | 0 | id03,id04 | 0.536508 | 0.473555 | 0.514494 |
| listener_only_direction | 1 | id08,id10 | 0.502408 | 0.476152 | 0.492269 |
| listener_only_direction | 2 | id01,id07 | 0.436508 | 0.513828 | 0.432354 |
| listener_only_direction | 3 | id05,id06 | 0.524845 | 0.538249 | 0.535668 |
| listener_only_direction | 4 | id02,id09 | 0.489567 | 0.471554 | 0.460854 |
| human_context_direction | 0 | id03,id04 | 0.536508 | 0.503415 | 0.544653 |
| human_context_direction | 1 | id08,id10 | 0.502408 | 0.514578 | 0.520101 |
| human_context_direction | 2 | id01,id07 | 0.436508 | 0.511216 | 0.456001 |
| human_context_direction | 3 | id05,id06 | 0.524845 | 0.548033 | 0.572661 |
| human_context_direction | 4 | id02,id09 | 0.489567 | 0.475250 | 0.475426 |
| masked_pretext_direction | 0 | id03,id04 | 0.536508 | 0.526389 | 0.551311 |
| masked_pretext_direction | 1 | id08,id10 | 0.502408 | 0.531011 | 0.528344 |
| masked_pretext_direction | 2 | id01,id07 | 0.436508 | 0.533004 | 0.453783 |
| masked_pretext_direction | 3 | id05,id06 | 0.524845 | 0.516586 | 0.534379 |
| masked_pretext_direction | 4 | id02,id09 | 0.489567 | 0.508171 | 0.505415 |
| responsibility_weighted_pretext_direction | 0 | id03,id04 | 0.536508 | 0.516166 | 0.540602 |
| responsibility_weighted_pretext_direction | 1 | id08,id10 | 0.502408 | 0.528836 | 0.528098 |
| responsibility_weighted_pretext_direction | 2 | id01,id07 | 0.436508 | 0.516686 | 0.441294 |
| responsibility_weighted_pretext_direction | 3 | id05,id06 | 0.524845 | 0.511684 | 0.537864 |
| responsibility_weighted_pretext_direction | 4 | id02,id09 | 0.489567 | 0.507671 | 0.498442 |
| human_plus_masked_pretext_direction | 0 | id03,id04 | 0.536508 | 0.518314 | 0.554879 |
| human_plus_masked_pretext_direction | 1 | id08,id10 | 0.502408 | 0.540596 | 0.528439 |
| human_plus_masked_pretext_direction | 2 | id01,id07 | 0.436508 | 0.513460 | 0.441923 |
| human_plus_masked_pretext_direction | 3 | id05,id06 | 0.524845 | 0.548265 | 0.588602 |
| human_plus_masked_pretext_direction | 4 | id02,id09 | 0.489567 | 0.459759 | 0.462903 |
| action_geometry_reference | 0 | id03,id04 | 0.536508 | 0.631140 | 0.650195 |
| action_geometry_reference | 1 | id08,id10 | 0.502408 | 0.531336 | 0.538135 |
| action_geometry_reference | 2 | id01,id07 | 0.436508 | 0.609280 | 0.525107 |
| action_geometry_reference | 3 | id05,id06 | 0.524845 | 0.560854 | 0.593213 |
| action_geometry_reference | 4 | id02,id09 | 0.489567 | 0.663429 | 0.634209 |

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
best core family가 action_geometry_reference에 근접하거나 responsibility-gated gain이 양수면,
HS-JEPA core가 어디를 볼지뿐 아니라 raw/inverse 방향 표현까지 일부 복원한다는 뜻이다.
```

나쁜 결과:

```text
action_geometry_reference만 강하고 core families가 약하면,
현재 HS-JEPA core는 listener responsibility까지는 좋지만 signed direction은 아직 adapter 영역이다.
```
