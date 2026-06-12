# HS-JEPA Diagnostic Adapter: Subject-Heldout Route Responsibility

## 한 줄 요약

subject-balanced route conservation이 모든 subject를 보고 고른 균형인지,
아니면 held-out subject에도 전이되는 route responsibility인지 검사했다.

```text
for each held-out subject:
  train subjects only -> choose target-route policy
  held-out subject only -> apply selected policy
  measure realized action gain
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **LeJEPA-style diagnostic adapter**다.

```text
HS-JEPA core
  = visible human-life context -> hidden world-state representation

이 문서의 역할
  = 그 representation이 만든 target-route action law가 subject shortcut인지 반증한다.
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_heldout_route_responsibility_negative_or_fragile`
- heldout selected cells: `251`
- heldout gain sum: `-5.128700`
- heldout positive gain rate: `0.585657`
- positive heldout subjects: `4`
- negative heldout subjects: `6`
- listener global gain reference: `6.192500`
- subject-balanced gain reference: `10.122799`
- stable targets for candidate: `['Q3', 'S4']`
- released test cells: `42`

## Heldout Subject Summary

| heldout_subject | selected_cells | gain_sum | mean_gain | positive_gain_rate | accepted_targets | held_targets |
| --- | --- | --- | --- | --- | --- | --- |
| id01 | 15 | -0.553900 | -0.036927 | 0.400000 | Q1,Q2,Q3,S3,S4 | S1,S2 |
| id02 | 27 | 0.051345 | 0.001902 | 0.666667 | Q2,Q3,S3,S4 | Q1,S1,S2 |
| id03 | 15 | -0.823602 | -0.054907 | 0.600000 | Q2,Q3,S3,S4 | Q1,S1,S2 |
| id04 | 26 | 0.663714 | 0.025527 | 0.615385 | Q1,Q2,Q3,S3,S4 | S1,S2 |
| id05 | 38 | -4.368488 | -0.114960 | 0.421053 | Q2,Q3,S2,S3,S4 | Q1,S1 |
| id06 | 25 | 2.401507 | 0.096060 | 0.800000 | Q2,Q3,S3,S4 | Q1,S1,S2 |
| id07 | 25 | 1.759072 | 0.070363 | 0.600000 | Q1,Q2,S2,S3,S4 | Q3,S1 |
| id08 | 41 | -1.120120 | -0.027320 | 0.658537 | Q1,Q2,Q3,S1,S3,S4 | S2 |
| id09 | 17 | -0.839930 | -0.049408 | 0.529412 | Q2,Q3,S3,S4 | Q1,S1,S2 |
| id10 | 22 | -2.298299 | -0.104468 | 0.500000 | Q1,Q2,Q3,S1,S2,S3,S4 |  |

## Heldout Target Summary

| target | selected_cells | gain_sum | mean_gain | positive_gain_rate | positive_subjects | negative_subjects |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | 8 | -1.048452 | -0.131057 | 0.250000 | 1 | 4 |
| Q2 | 93 | 2.221769 | 0.023890 | 0.580645 | 5 | 5 |
| Q3 | 35 | 0.050794 | 0.001451 | 0.657143 | 6 | 3 |
| S1 | 3 | -2.724568 | -0.908189 | 0.333333 | 0 | 2 |
| S2 | 10 | -3.261192 | -0.326119 | 0.300000 | 1 | 2 |
| S3 | 32 | -2.366441 | -0.073951 | 0.562500 | 3 | 7 |
| S4 | 70 | 1.999390 | 0.028563 | 0.657143 | 5 | 4 |

## Route Decision Frequency

| target | heldout_accept_rate | top_decision | top_decision_count | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects |
| --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.500000 | hold|none|0.00 | 5 | -1.048452 | 1 | 4 |
| Q2 | 1.000000 | release_high_all|raw_memory_release|0.18 | 5 | 2.221769 | 5 | 5 |
| Q3 | 0.900000 | inverse_low_decisive|inverse_toxic_memory|0.02 | 5 | 0.050794 | 6 | 3 |
| S1 | 0.200000 | hold|none|0.00 | 8 | -2.724568 | 0 | 2 |
| S2 | 0.300000 | hold|none|0.00 | 7 | -3.261192 | 1 | 2 |
| S3 | 1.000000 | inverse_low_decisive|inverse_toxic_memory|0.10 | 9 | -2.366441 | 3 | 7 |
| S4 | 1.000000 | release_high_all|raw_memory_release|0.18 | 5 | 1.999390 | 5 | 4 |

## Stable Routes Used For Candidate

| target | accepted | policy | decoder_action | fraction | heldout_accept_rate | heldout_gain_sum | heldout_positive_subjects | heldout_negative_subjects | heldout_positive_gain_rate | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | hold | none | 0.000000 | 0.500000 | -1.048452 | 1 | 4 | 0.250000 | failed_subject_heldout_route_responsibility |
| Q2 | False | hold | none | 0.000000 | 1.000000 | 2.221769 | 5 | 5 | 0.580645 | failed_subject_heldout_route_responsibility |
| Q3 | True | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 0.900000 | 0.050794 | 6 | 3 | 0.657143 | heldout_stable_subject_route_responsibility |
| S1 | False | hold | none | 0.000000 | 0.200000 | -2.724568 | 0 | 2 | 0.333333 | failed_subject_heldout_route_responsibility |
| S2 | False | hold | none | 0.000000 | 0.300000 | -3.261192 | 1 | 2 | 0.300000 | failed_subject_heldout_route_responsibility |
| S3 | False | hold | none | 0.000000 | 1.000000 | -2.366441 | 3 | 7 | 0.562500 | failed_subject_heldout_route_responsibility |
| S4 | True | release_high_decisive | raw_memory_release | 0.180000 | 1.000000 | 1.999390 | 5 | 4 | 0.657143 | heldout_stable_subject_route_responsibility |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_heldout_route_responsibility_anchor_free_f2a44231_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.4106039285792241, 'probability_max': 0.8046232165702017}`

## 해석

좋은 결과:

```text
held-out subject를 route selection에서 완전히 제거해도 gain이 양수이면,
HS-JEPA route responsibility는 단순 subject-tail shortcut만은 아니다.
```

나쁜 결과:

```text
subject-balanced에서는 양수였지만 subject-heldout에서 무너지면,
현재 route law는 OOF balancing artifact이고 release-grade 일반 법칙은 아니다.
```

현재 결론:

```text
이번 결과는 negative/fragile이다.
subject-balanced route law는 모든 subject를 본 OOF audit에서는 강했지만,
subject를 완전히 가린 선택-평가에서는 전체 gain이 음수로 무너졌다.
따라서 현재 target-route decoder를 subject-general HS-JEPA law로 주장하면 안 된다.

다만 Q3/S4 route만 조건부로 살아남았으므로,
다음 core 연구는 전체 sparse action release가 아니라
target별 listener responsibility와 subject-heldout action toxicity를 분리해야 한다.
```
