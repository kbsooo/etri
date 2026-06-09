# Energy-Utility Assignment Solver HS-JEPA

## 실험 목적

`Route-Consistency Energy`는 공격적인 후보를 만든 뒤 위험한 action을 veto했다.

이번 실험은 한 단계 더 나아간다.

> action을 먼저 만들고 나중에 지우는 것이 아니라, 처음부터 public utility와 route consistency가 동시에 동의하는 row-target action만 선택한다.

즉 HS-JEPA를 다음 문제로 재정의한다.

```text
1750개 row-target cell 중에서
public-loss sensor가 좋아하고,
listener/source가 지지하고,
Q/S route energy를 깨지 않는 action subset을 찾아라.
```

## 핵심 한 줄

Public-loss sparse tomography가 제안한 support field와 train-label route energy를 결합해,
utility가 양수이고 공동 label manifold를 깨지 않는 action만 greedy assignment로 선택했다.

## 코드

```bash
python3 paper_hsjepa_core/energy_utility_assignment_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_energy_utility_solver_balanced_fd352632_uploadsafe.csv`
- `submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/energy_utility_assignment_solver/energy_utility_assignment_readout.json`
- `paper_hsjepa_core/outputs/energy_utility_assignment_solver/energy_utility_proposal_pool.csv`
- `paper_hsjepa_core/outputs/energy_utility_assignment_solver/energy_utility_balanced_audit.csv`
- `paper_hsjepa_core/outputs/energy_utility_assignment_solver/energy_utility_jackpot_audit.csv`

## 구조

입력:

1. current best probability
2. source/listener support field
3. public-loss sparse tomography coefficient
4. route-consistency energy model
5. H088-like toxic direction alignment

출력:

1. row-target action 후보 pool
2. action별 public utility estimate
3. action별 route energy delta
4. accepted action subset
5. upload-safe submission

전체 구조:

```text
Source/listener support
        |
        v
Public-loss utility sensor
        |
        v
Candidate action pool
        |
        v
Route-consistency energy check
        |
        v
Energy-Utility Assignment Solver
        |
        v
Sparse row-target correction field
```

## 중요한 주의

`estimated_public_delta`는 실제 public LB 예측값이 아니다.

public ledger가 작고 후보 간 상관이 크기 때문에 ridge coefficient는 절대값이 과장될 수 있다.
여기서는 “어느 action이 상대적으로 더 유망한가”를 보는 sensor로만 사용한다.

## 결과 요약

공통 입력:

- support cells: `160`
- proposal cells: `96`
- public observation count: `26`
- ridge RMSE: `0.000240820`
- ridge LOO RMSE: `0.001033583`
- stable cells > 0.8: `158`

### Balanced variant

제출 파일:

```text
submission_hsjepa_energy_utility_solver_balanced_fd352632_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| selected cells | 33 |
| changed rows | 31 |
| validation changed cells | 33 |
| mean route energy | 0.727137 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.009427 |
| negative-energy actions | 24 |
| H088 cosine | 0.008467 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| Q1 | 1 |
| Q2 | 5 |
| Q3 | 5 |
| S1 | 4 |
| S2 | 9 |
| S3 | 5 |
| S4 | 4 |

해석:

Balanced는 매우 압축된 solver다.
33개 cell만 움직이며, 선택된 action의 대부분이 route energy를 낮춘다.
성능 후보로는 보수적이지만, public utility와 route consistency가 동시에 동의하는 핵심 action set이다.

### Jackpot variant

제출 파일:

```text
submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| selected cells | 36 |
| changed rows | 34 |
| validation changed cells | 36 |
| mean route energy | 0.727061 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.009171 |
| negative-energy actions | 26 |
| H088 cosine | 0.008525 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| Q1 | 1 |
| Q2 | 5 |
| Q3 | 5 |
| S1 | 5 |
| S2 | 10 |
| S3 | 5 |
| S4 | 5 |

해석:

Jackpot은 Balanced보다 약간 더 공격적이다.
하지만 여전히 36개 cell만 움직이고, route energy는 더 낮다.
S2가 10개로 가장 많이 선택된 점이 중요하다.
직전 route-veto 실험에서도 S2가 많이 살아남았으므로, 현재 solver가 반복적으로 찾는 safe route는 Q2가 아니라 S2 축일 수 있다.

## 이번 실험에서 새로 얻은 것

가장 중요한 발견:

```text
HS-JEPA의 next action은 Q2 확장이 아니라,
S2 중심의 route-consistent sparse action일 가능성이 커졌다.
```

이전에는 Q2가 가장 문제라고 봤다.
하지만 route-energy 관점에서 보면 Q2 extra는 많이 탈락하고, S2 action은 반복적으로 살아남는다.

따라서 현재 세계관은 다음처럼 수정된다.

```text
Q2는 public-loss sensor에 민감한 route다.
하지만 안전하게 action으로 번역되는 route는 S2와 Q2 일부의 조합이다.
```

## 논문형 의미

이 실험은 HS-JEPA를 더 명확히 아키텍처로 만든다.

단순히:

```text
latent -> prediction
```

이 아니라:

```text
latent/context -> candidate action
candidate action -> utility estimate
candidate action -> route-consistency energy
utility + energy -> assignment solver
```

로 분리된다.

즉 HS-JEPA는 label을 직접 맞히는 모델이 아니라,
row-target action을 생성하고 검증하며 선택하는 joint embedding predictive system이다.

## 제출 판단

둘 중 하나만 고르면:

```text
submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv
```

이유:

- Balanced보다 cell 수가 3개 많지만 여전히 sparse하다.
- route energy가 더 낮다.
- S2/Q2 safe route를 조금 더 넓게 테스트한다.
- H088 cosine은 Balanced와 거의 같다.
- public LB가 좋아지면 HS-JEPA의 energy-utility solver 주장이 크게 강화된다.

실패 시 해석:

- public/private safety는 train-label route manifold와 다르다.
- 또는 public-loss sparse tomography coefficient가 support ranking에는 유효하지만 action magnitude에는 과장되어 있다.
- 그래도 실패는 “route consistency만으로는 충분하지 않다”는 논문형 negative result가 된다.
