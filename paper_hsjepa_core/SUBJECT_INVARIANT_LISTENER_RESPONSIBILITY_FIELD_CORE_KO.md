# Subject-Invariant Listener Responsibility Field Core

## 한 줄 요약

action을 직접 예측하지 않고, 먼저 row-target 단위에서
`이 human-state에서 이 target listener가 개입할 책임이 있는가`를 예측했다.

```text
visible human-life context
  + target listener
  -> hidden listener responsibility field
  -> action decoder only after responsibility is high
```

## 왜 필요한 실험인가

Open-loop raw human-state와 masked-view pretext는 action-level strict release를
listener-only보다 잘 분리하지 못했다. 이 실험은 hidden target 자체를 action에서
listener responsibility field로 바꾼다. HS-JEPA가 인간 상태를 더 잘 표현한다면,
row-target listener responsibility는 단순 target prior/listener-only보다 잘 예측되어야 한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`
- masked-tail teacher score as feature: `False`
- label-informed peer margin as feature: `False`

## Verdict

- verdict: `listener_responsibility_field_positive_action_translation_fragile`
- best responsibility family: `masked_pretext_listener_responsibility`
- human responsibility AP lift: `0.077261`
- listener-only AP lift: `0.064292`
- masked-pretext AP lift: `0.079078`
- human-plus-pretext AP lift: `0.071150`
- action-decoder OOF gain for release family: `-0.565668`
- listener-only action-decoder OOF gain: `-3.045468`
- released test cells: `67`
- candidate: `submission_hsjepa_subject_invariant_listener_responsibility_field_a9a2ea47_uploadsafe.csv`

## Listener Responsibility Leaderboard

| feature_family | label_task | feature_count | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- | --- |
| masked_pretext_listener_responsibility | listener_responsible | 46 | 0.055238 | 0.695319 | 0.134316 | 0.079078 |
| human_listener_responsibility | listener_responsible | 126 | 0.055238 | 0.703712 | 0.132499 | 0.077261 |
| human_plus_masked_pretext_responsibility | listener_responsible | 180 | 0.055238 | 0.700847 | 0.126388 | 0.071150 |
| listener_only | listener_responsible | 12 | 0.055238 | 0.712156 | 0.119530 | 0.064292 |

## Target-Level Responsibility Metrics

| feature_family | target | positive_rate | auc | ap | ap_lift_vs_rate |
| --- | --- | --- | --- | --- | --- |
| human_listener_responsibility | Q1 | 0.035556 | 0.638393 | 0.132441 | 0.096886 |
| human_listener_responsibility | Q2 | 0.024444 | 0.810520 | 0.120939 | 0.096495 |
| human_listener_responsibility | S1 | 0.024444 | 0.669497 | 0.079770 | 0.055325 |
| human_listener_responsibility | Q3 | 0.066667 | 0.532460 | 0.089519 | 0.022852 |
| human_listener_responsibility | S4 | 0.182222 | 0.484889 | 0.191517 | 0.009294 |
| human_listener_responsibility | S3 | 0.017778 | 0.572964 | 0.021815 | 0.004038 |
| human_listener_responsibility | S2 | 0.035556 | 0.323157 | 0.027407 | -0.008149 |
| human_plus_masked_pretext_responsibility | Q3 | 0.066667 | 0.670556 | 0.151436 | 0.084770 |
| human_plus_masked_pretext_responsibility | Q2 | 0.024444 | 0.770760 | 0.080611 | 0.056167 |
| human_plus_masked_pretext_responsibility | Q1 | 0.035556 | 0.503312 | 0.076805 | 0.041250 |
| human_plus_masked_pretext_responsibility | S1 | 0.024444 | 0.577345 | 0.047271 | 0.022827 |
| human_plus_masked_pretext_responsibility | S3 | 0.017778 | 0.625283 | 0.025625 | 0.007847 |
| human_plus_masked_pretext_responsibility | S4 | 0.182222 | 0.461559 | 0.176440 | -0.005782 |
| human_plus_masked_pretext_responsibility | S2 | 0.035556 | 0.392425 | 0.029229 | -0.006326 |
| listener_only | Q2 | 0.024444 | 0.461483 | 0.022769 | -0.001675 |
| listener_only | S3 | 0.017778 | 0.422229 | 0.015064 | -0.002714 |
| listener_only | S1 | 0.024444 | 0.390971 | 0.019905 | -0.004540 |
| listener_only | S2 | 0.035556 | 0.432964 | 0.030631 | -0.004924 |
| listener_only | Q1 | 0.035556 | 0.432532 | 0.030603 | -0.004953 |
| listener_only | Q3 | 0.066667 | 0.405913 | 0.056111 | -0.010556 |
| listener_only | S4 | 0.182222 | 0.362556 | 0.146305 | -0.035917 |
| masked_pretext_listener_responsibility | Q3 | 0.066667 | 0.657897 | 0.123994 | 0.057327 |
| masked_pretext_listener_responsibility | Q1 | 0.035556 | 0.465222 | 0.054444 | 0.018888 |
| masked_pretext_listener_responsibility | S3 | 0.017778 | 0.652149 | 0.035505 | 0.017727 |
| masked_pretext_listener_responsibility | S4 | 0.182222 | 0.488716 | 0.199281 | 0.017059 |
| masked_pretext_listener_responsibility | Q2 | 0.024444 | 0.534686 | 0.036515 | 0.012070 |
| masked_pretext_listener_responsibility | S1 | 0.024444 | 0.482502 | 0.027111 | 0.002666 |
| masked_pretext_listener_responsibility | S2 | 0.035556 | 0.491215 | 0.037331 | 0.001775 |

## Release Simulation With Existing Action Decoder

| feature_family | selected_cells | realized_gain_sum | mean_realized_gain | positive_gain_rate | negative_gain_rate |
| --- | --- | --- | --- | --- | --- |
| masked_pretext_listener_responsibility | 120 | -0.565668 | -0.004714 | 0.616667 | 0.383333 |
| human_listener_responsibility | 120 | -1.364019 | -0.011367 | 0.541667 | 0.458333 |
| human_plus_masked_pretext_responsibility | 120 | -2.110568 | -0.017588 | 0.600000 | 0.400000 |
| listener_only | 120 | -3.045468 | -0.025379 | 0.450000 | 0.550000 |

## Fold Stability

| feature_family | label_task | fold | heldout_subjects | positive_rate | auc | ap |
| --- | --- | --- | --- | --- | --- | --- |
| listener_only | listener_responsible | 0 | id03,id04 | 0.034921 | 0.634569 | 0.052395 |
| listener_only | listener_responsible | 1 | id08,id10 | 0.041734 | 0.660546 | 0.073219 |
| listener_only | listener_responsible | 2 | id01,id07 | 0.073016 | 0.751266 | 0.185880 |
| listener_only | listener_responsible | 3 | id05,id06 | 0.060559 | 0.759292 | 0.187418 |
| listener_only | listener_responsible | 4 | id02,id09 | 0.065811 | 0.764814 | 0.184191 |
| listener_only | positive_listener_responsible | 0 | id03,id04 | 0.019048 | 0.627427 | 0.030710 |
| listener_only | positive_listener_responsible | 1 | id08,id10 | 0.020867 | 0.634678 | 0.038597 |
| listener_only | positive_listener_responsible | 2 | id01,id07 | 0.044444 | 0.713574 | 0.099008 |
| listener_only | positive_listener_responsible | 3 | id05,id06 | 0.023292 | 0.714520 | 0.070072 |
| listener_only | positive_listener_responsible | 4 | id02,id09 | 0.038523 | 0.803353 | 0.134582 |
| human_listener_responsibility | listener_responsible | 0 | id03,id04 | 0.034921 | 0.605637 | 0.068555 |
| human_listener_responsibility | listener_responsible | 1 | id08,id10 | 0.041734 | 0.663703 | 0.105378 |
| human_listener_responsibility | listener_responsible | 2 | id01,id07 | 0.073016 | 0.622915 | 0.111650 |
| human_listener_responsibility | listener_responsible | 3 | id05,id06 | 0.060559 | 0.813626 | 0.242809 |
| human_listener_responsibility | listener_responsible | 4 | id02,id09 | 0.065811 | 0.753856 | 0.201082 |
| human_listener_responsibility | positive_listener_responsible | 0 | id03,id04 | 0.019048 | 0.612257 | 0.030974 |
| human_listener_responsibility | positive_listener_responsible | 1 | id08,id10 | 0.020867 | 0.678436 | 0.065905 |
| human_listener_responsibility | positive_listener_responsible | 2 | id01,id07 | 0.044444 | 0.667774 | 0.110150 |
| human_listener_responsibility | positive_listener_responsible | 3 | id05,id06 | 0.023292 | 0.684367 | 0.156810 |
| human_listener_responsibility | positive_listener_responsible | 4 | id02,id09 | 0.038523 | 0.740853 | 0.140524 |
| masked_pretext_listener_responsibility | listener_responsible | 0 | id03,id04 | 0.034921 | 0.681519 | 0.090670 |
| masked_pretext_listener_responsibility | listener_responsible | 1 | id08,id10 | 0.041734 | 0.639061 | 0.090459 |
| masked_pretext_listener_responsibility | listener_responsible | 2 | id01,id07 | 0.073016 | 0.629206 | 0.180121 |
| masked_pretext_listener_responsibility | listener_responsible | 3 | id05,id06 | 0.060559 | 0.736173 | 0.162981 |
| masked_pretext_listener_responsibility | listener_responsible | 4 | id02,id09 | 0.065811 | 0.739733 | 0.216934 |
| masked_pretext_listener_responsibility | positive_listener_responsible | 0 | id03,id04 | 0.019048 | 0.645227 | 0.048673 |
| masked_pretext_listener_responsibility | positive_listener_responsible | 1 | id08,id10 | 0.020867 | 0.693190 | 0.069205 |
| masked_pretext_listener_responsibility | positive_listener_responsible | 2 | id01,id07 | 0.044444 | 0.613431 | 0.094179 |
| masked_pretext_listener_responsibility | positive_listener_responsible | 3 | id05,id06 | 0.023292 | 0.575994 | 0.038963 |
| masked_pretext_listener_responsibility | positive_listener_responsible | 4 | id02,id09 | 0.038523 | 0.674805 | 0.074719 |
| human_plus_masked_pretext_responsibility | listener_responsible | 0 | id03,id04 | 0.034921 | 0.639317 | 0.089280 |
| human_plus_masked_pretext_responsibility | listener_responsible | 1 | id08,id10 | 0.041734 | 0.675622 | 0.105959 |
| human_plus_masked_pretext_responsibility | listener_responsible | 2 | id01,id07 | 0.073016 | 0.654333 | 0.116864 |
| human_plus_masked_pretext_responsibility | listener_responsible | 3 | id05,id06 | 0.060559 | 0.778640 | 0.204258 |
| human_plus_masked_pretext_responsibility | listener_responsible | 4 | id02,id09 | 0.065811 | 0.741137 | 0.176866 |
| human_plus_masked_pretext_responsibility | positive_listener_responsible | 0 | id03,id04 | 0.019048 | 0.628304 | 0.041577 |
| human_plus_masked_pretext_responsibility | positive_listener_responsible | 1 | id08,id10 | 0.020867 | 0.641614 | 0.070748 |
| human_plus_masked_pretext_responsibility | positive_listener_responsible | 2 | id01,id07 | 0.044444 | 0.639327 | 0.074917 |
| human_plus_masked_pretext_responsibility | positive_listener_responsible | 3 | id05,id06 | 0.023292 | 0.657658 | 0.122778 |
| human_plus_masked_pretext_responsibility | positive_listener_responsible | 4 | id02,id09 | 0.038523 | 0.746661 | 0.101161 |

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
human-state + listener가 listener-only보다 row-target responsibility를 더 잘 예측하면,
HS-JEPA core가 action probability가 아니라 listener responsibility field를 먼저 복원한다는
논문 주장이 강화된다.
```

나쁜 결과:

```text
cell-level responsibility가 좋아도 action-decoder gain이 낮으면,
core는 "어디를 봐야 하는지"는 알지만 "어떻게 움직여야 하는지" 번역이 아직 toxic하다는 뜻이다.
```
