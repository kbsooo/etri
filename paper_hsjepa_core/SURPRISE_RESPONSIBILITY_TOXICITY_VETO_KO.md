# Surprise Responsibility Toxicity Veto

## 한 줄 요약

Masked-view surprise energy를 action release 자체가 아니라 target별 listener responsibility로 사용해, episode action-space decoder의 독성 cell을 public LB 없이 OOF gain 기준으로 veto하는 실험이다.

## 왜 필요한가

`Masked View Surprise Action Release`는 JEPA residual energy가 Q3/Q2/S3 target law와 연결된다는 증거를 만들었다. 하지만 그 energy를 그대로 action으로 release하면 action-grade decoder인지 아직 불분명하다.

이번 실험은 질문을 바꾼다.

```text
surprise energy가 action을 직접 만드는가?
```

가 아니라,

```text
surprise energy가 target listener별로 어떤 action을 믿고 버릴지 결정하는가?
```

## JEPA Mapping

| 구성 | 의미 |
| --- | --- |
| context | episode action-space decoder가 제안한 row-target action |
| hidden target representation | masked-view residual energy가 만든 hidden episode responsibility |
| predictor | target별로 high-surprise listener / low-surprise listener / all listener 중 어느 책임자가 건강한지 OOF gain으로 선택 |
| energy decoder | 선택된 listener responsibility와 맞지 않는 action을 veto |
| stress | subject-heldout으로 target listener rule이 특정 subject tail인지 검사 |

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Target Listener Rules

| target | selected_mode | median_score | selected_cells | selected_gain_sum | all_gain_sum | selected_mean_gain | all_mean_gain | selected_positive_gain_rate | all_positive_gain_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | high_surprise_listener | 0.268833 | 3 | 0.278269 | 0.246517 | 0.092756 | 0.041086 | 1.000000 | 0.666667 |
| Q2 | all | 0.220778 | 6 | 0.939331 | 0.939331 | 0.156555 | 0.156555 | 0.666667 | 0.666667 |
| Q3 | all | 0.268833 | 6 | 1.162831 | 1.162831 | 0.193805 | 0.193805 | 0.833333 | 0.833333 |
| S1 | low_surprise_listener | 0.227778 | 3 | 0.161004 | 0.062711 | 0.053668 | 0.010452 | 1.000000 | 0.833333 |
| S2 | high_surprise_listener | 0.344000 | 4 | 0.311208 | 0.221898 | 0.077802 | 0.031700 | 0.500000 | 0.571429 |
| S3 | all | 0.319833 | 8 | 2.497804 | 2.497804 | 0.312226 | 0.312226 | 0.750000 | 0.750000 |
| S4 | low_surprise_listener | 0.250000 | 2 | 0.192029 | 0.180443 | 0.096015 | 0.036089 | 1.000000 | 0.600000 |

상세 rule 비교:

| target | mode | cells | gain_sum | mean_gain | positive_gain_rate |
| --- | --- | --- | --- | --- | --- |
| Q1 | all | 6 | 0.246517 | 0.041086 | 0.666667 |
| Q1 | high_surprise_listener | 3 | 0.278269 | 0.092756 | 1.000000 |
| Q1 | low_surprise_listener | 3 | -0.031752 | -0.010584 | 0.333333 |
| Q2 | all | 6 | 0.939331 | 0.156555 | 0.666667 |
| Q2 | high_surprise_listener | 3 | 0.840108 | 0.280036 | 1.000000 |
| Q2 | low_surprise_listener | 3 | 0.099223 | 0.033074 | 0.333333 |
| Q3 | all | 6 | 1.162831 | 0.193805 | 0.833333 |
| Q3 | high_surprise_listener | 3 | 0.936645 | 0.312215 | 1.000000 |
| Q3 | low_surprise_listener | 3 | 0.226186 | 0.075395 | 0.666667 |
| S1 | all | 6 | 0.062711 | 0.010452 | 0.833333 |
| S1 | high_surprise_listener | 3 | -0.098294 | -0.032765 | 0.666667 |
| S1 | low_surprise_listener | 3 | 0.161004 | 0.053668 | 1.000000 |
| S2 | all | 7 | 0.221898 | 0.031700 | 0.571429 |
| S2 | high_surprise_listener | 4 | 0.311208 | 0.077802 | 0.500000 |
| S2 | low_surprise_listener | 3 | -0.089310 | -0.029770 | 0.666667 |
| S3 | all | 8 | 2.497804 | 0.312226 | 0.750000 |
| S3 | high_surprise_listener | 4 | 1.996278 | 0.499070 | 0.750000 |
| S3 | low_surprise_listener | 4 | 0.501526 | 0.125381 | 0.750000 |
| S4 | all | 5 | 0.180443 | 0.036089 | 0.600000 |
| S4 | high_surprise_listener | 3 | -0.011586 | -0.003862 | 0.333333 |
| S4 | low_surprise_listener | 2 | 0.192029 | 0.096015 | 1.000000 |

## OOF Veto 결과

- original episode release cells: `44`
- original gain sum: `5.311535`
- veto-kept cells: `32`
- veto-kept gain sum: `5.542476`
- removed gain sum: `-0.230941`
- original positive gain rate: `0.704545`
- kept positive gain rate: `0.781250`

## Subject-Heldout Stress

| heldout_subject | all_cells | kept_cells | all_gain_sum | kept_gain_sum | removed_gain_sum | all_mean_gain | kept_mean_gain |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id02 | 5 | 5 | 1.485178 | 1.485178 | 0.000000 | 0.297036 | 0.297036 |
| id09 | 39 | 39 | 3.826356 | 3.826356 | 0.000000 | 0.098112 | 0.098112 |

주의: 이 release policy의 OOF action은 `id02`, `id09` 두 subject에만 집중되어 있다. 따라서 subject-heldout stress는 강한 검증이 아니라 "현재 release가 subject-tail에 몰려 있어 target listener rule을 안정적으로 외삽하기 어렵다"는 약한 진단으로 읽어야 한다.

## Test Candidate

- candidate: `submission_hsjepa_surprise_responsibility_toxicity_veto_5e3d6e26_uploadsafe.csv`
- original switched cells: `105`
- kept switched cells: `72`
- vetoed switched cells: `33`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.1458333333333333, 'probability_max': 0.9583333333333334}`

Target별 kept/vetoed:

| target | switched | kept | vetoed |
| --- | --- | --- | --- |
| Q1 | 15 | 10 | 5 |
| Q2 | 15 | 15 | 0 |
| Q3 | 15 | 15 | 0 |
| S1 | 15 | 2 | 13 |
| S2 | 15 | 14 | 1 |
| S3 | 15 | 15 | 0 |
| S4 | 15 | 1 | 14 |

## 해석

이 실험은 masked surprise가 넓은 action을 직접 만드는 장치가 아니라, target별 listener responsibility로 더 잘 작동하는지 검증한다.

OOF에서 gain이 증가하면:

```text
HS-JEPA residual energy can reduce action toxicity by assigning target-specific listener responsibility.
```

OOF에서는 증가하지만 subject-heldout에서 약하면:

```text
surprise responsibility is real but still subject-tail sensitive.
```

OOF에서도 감소하면:

```text
masked surprise energy is a state diagnostic, not a release-grade toxicity veto.
```

