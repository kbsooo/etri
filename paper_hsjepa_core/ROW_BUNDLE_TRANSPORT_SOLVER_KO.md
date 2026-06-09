# Row-Bundle Transport Solver HS-JEPA

## 실험 목적

이전 `Energy-Utility Assignment Solver`는 row-target cell을 하나씩 선택했다.

하지만 인간 생활 상태가 실제로 변한다면, 특정 target 하나만 움직이는 것보다
같은 row 안에서 여러 target이 함께 움직이는 것이 더 자연스러울 수 있다.

예:

```text
Q2만 나빠진다
```

보다

```text
Q2와 S2가 함께 변한다
S1과 S2가 함께 변한다
S3와 S4가 함께 변한다
```

가 더 human-state transition에 가까울 수 있다.

이번 실험은 이 가설을 직접 테스트한다.

> 개별 cell action이 아니라 row-local target bundle을 선택하면, 더 자연스러운 hidden-state transport를 만들 수 있는가?

## 핵심 한 줄

row별 후보 action을 1~3개 묶음으로 조합해 public utility와 route-consistency energy를 동시에 평가했다.
결과적으로 Q2/S2 큰 bundle 가설은 약했고, 대부분의 안전 action은 singleton이었으며 일부 objective pair만 살아남았다.

## 코드

```bash
python3 paper_hsjepa_core/row_bundle_transport_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_row_bundle_transport_paircore_ea3e13e3_uploadsafe.csv`
- `submission_hsjepa_row_bundle_transport_triadjackpot_294ddb94_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_transport_readout.json`
- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_proposal_pool.csv`
- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_paircore_selected.csv`
- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_triadjackpot_selected.csv`
- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_paircore_candidates.csv`
- `paper_hsjepa_core/outputs/row_bundle_transport_solver/row_bundle_triadjackpot_candidates.csv`

## 구조

입력은 Energy-Utility solver와 같다.

- source/listener support
- public-loss utility coefficient
- target-route consistency energy
- H088-like toxicity alignment

차이는 선택 단위다.

기존:

```text
cell -> accept/reject
```

이번:

```text
row 안의 cell 조합 -> bundle accept/reject
```

각 row에서 후보 cell을 최대 5~6개 가져오고,
size 1, 2, 3 조합을 모두 평가한다.

bundle은 다음 조건을 통과해야 한다.

1. public utility가 양수
2. route energy delta가 허용 범위 이하
3. H088 toxic alignment가 낮음
4. stability가 충분함
5. target별 bundle 수 제한을 넘지 않음

## 결과 요약

### Paircore

제출 파일:

```text
submission_hsjepa_row_bundle_transport_paircore_ea3e13e3_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| candidate bundles | 38 |
| selected bundles | 24 |
| selected cells | 28 |
| changed rows | 24 |
| mean route energy | 0.727442 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.009780 |
| negative energy bundles | 20 |
| H088 cosine | 0.006596 |
| base listener max delta | -0.000297 |
| semantic listener max delta | -0.000297 |
| upload-safe | true |

Bundle size:

| size | count |
|---|---:|
| 1 | 20 |
| 2 | 4 |

Target counts:

| target | count |
|---|---:|
| Q2 | 6 |
| Q3 | 1 |
| S1 | 5 |
| S2 | 7 |
| S3 | 5 |
| S4 | 4 |

살아남은 pair:

- row 184: `S2+S1`
- row 5: `Q3+S2`
- row 234: `S4+S3`
- row 109: `S2+S1`

해석:

paircore는 가장 안정적인 diagnostic 후보다.
모든 listener model에서 max delta가 음수이고, H088 cosine도 낮다.
하지만 선택된 bundle의 대부분은 singleton이다.
즉 “bundle이 핵심이다”라기보다는 “일부 objective pair만 bundle로 의미가 있다”는 결과다.

### Triadjackpot

제출 파일:

```text
submission_hsjepa_row_bundle_transport_triadjackpot_294ddb94_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| candidate bundles | 43 |
| selected bundles | 30 |
| selected cells | 33 |
| changed rows | 30 |
| mean route energy | 0.727385 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.008304 |
| negative energy bundles | 24 |
| H088 cosine | 0.007915 |
| upload-safe | true |

Bundle size:

| size | count |
|---|---:|
| 1 | 27 |
| 2 | 3 |

Target counts:

| target | count |
|---|---:|
| Q1 | 1 |
| Q2 | 8 |
| Q3 | 2 |
| S1 | 5 |
| S2 | 7 |
| S3 | 5 |
| S4 | 5 |

해석:

triad를 허용했지만 실제 triad는 선택되지 않았다.
이것은 중요한 negative result다.
현재 support/utility/energy 조건에서는 큰 multi-target human-state jump보다
작은 sparse action이 더 자연스럽다.

## 반증된 가설

이번 실험은 다음 가설을 약화시킨다.

```text
0.53급 breakthrough는 같은 row 안에서 Q2/S2 등 여러 target을 동시에 크게 이동시키는 bundle transport에서 나온다.
```

관측:

- Q2+S2 bundle은 선택되지 않았다.
- triad도 선택되지 않았다.
- 살아남은 pair는 `S1/S2`, `S3/S4`, `Q3/S2`처럼 objective route에 가깝다.

따라서 현재 증거는 다음 쪽에 가깝다.

```text
HS-JEPA action field는 큰 row-level vector transport보다,
route-consistent sparse micro-action의 합으로 설명되는 편이 더 자연스럽다.
```

## 새로 살아난 가설

Q2 단독 문제가 아니라 S-stage objective subroute가 더 중요할 수 있다.

반복적으로 살아남은 축:

- S2
- S1/S2 pair
- S3/S4 pair
- Q2 일부

이것은 target 이름 기준보다 다음 route가 더 실재적일 수 있음을 암시한다.

```text
intervention-sensitive route: Q2 일부
objective-stage-balance route: S1/S2, S3/S4
```

## 제출 판단

성능 후보로 하나 고르면:

```text
submission_hsjepa_row_bundle_transport_paircore_ea3e13e3_uploadsafe.csv
```

이유:

- changed cells 28개로 sparse하다.
- route energy가 current best보다 낮다.
- H088 cosine이 낮다.
- base/semantic listener max delta가 모두 음수라 robust stress가 좋다.

하지만 큰 한방 후보로는 `energy_utility_solver_jackpot`이 여전히 더 강하다.

이번 실험의 가장 큰 가치는 제출 파일보다:

```text
Q2/S2 큰 bundle breakthrough 가설을 약화시키고,
objective-stage micro-bundle과 sparse action solver 쪽으로 세계관을 좁힌 것
```

이다.
