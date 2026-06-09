# Route-Consistency Energy HS-JEPA

## 실험 목적

직전 실험들은 `Listener Responsibility`와 `Target-Route Toxicity Head`를 통해
어느 row-target cell을 움직일지, 그리고 target별로 얼마나 공격적으로 움직일지를
분리했다.

하지만 아직 한 가지 위험이 남아 있다.

> 어떤 cell correction은 단독으로는 그럴듯해 보여도, 7개 target의 공동 구조를 깨뜨릴 수 있다.

이번 실험은 이 위험을 직접 측정한다.

HS-JEPA를 단순 correction generator가 아니라, correction이 만든 target vector가
훈련 label의 Q/S 공동 구조 위에 남아 있는지 검사하는 energy system으로 확장한다.

## 핵심 한 줄

Train label만으로 Q1/Q2/Q3/S1/S2/S3/S4의 conditional route manifold를 학습하고,
각 candidate correction이 이 manifold를 얼마나 깨는지 energy로 측정한 뒤,
energy를 과도하게 높이는 row-target action을 veto했다.

## 코드

```bash
python3 paper_hsjepa_core/route_consistency_energy.py
```

## 산출물

제출 후보:

- `submission_hsjepa_route_energy_veto_public_private_toxicity_e08d9849_uploadsafe.csv`
- `submission_hsjepa_route_energy_veto_target_route_q2_extra_5dfa9e76_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/route_consistency_energy/route_consistency_readout.json`
- `paper_hsjepa_core/outputs/route_consistency_energy/route_consistency_candidate_energy.csv`
- `paper_hsjepa_core/outputs/route_consistency_energy/route_energy_veto_audit.csv`

## Energy 모델

Energy 모델은 public score를 사용하지 않는다.

훈련 label에서 target 하나를 나머지 target 여섯 개로 예측하는 conditional
pseudo-likelihood 모델을 만든다.

```text
P(Q1 | Q2,Q3,S1,S2,S3,S4)
P(Q2 | Q1,Q3,S1,S2,S3,S4)
...
P(S4 | Q1,Q2,Q3,S1,S2,S3)
```

candidate submission이 만든 7-target probability vector를 이 모델에 넣고,
각 target probability가 다른 target들이 암시하는 conditional probability와
얼마나 어긋나는지 soft BCE로 energy를 계산한다.

쉽게 말하면:

```text
이 row의 Q/S 조합은 train label 세계에서 자연스러운 조합인가?
아니면 어느 cell을 세게 움직이면서 이상한 조합이 되었는가?
```

## Candidate energy 비교

| candidate | changed cells | mean route energy | delta vs current best | p95 row energy |
|---|---:|---:|---:|---:|
| current_best | 0 | 0.728381 | 0.000000 | 0.929419 |
| candidate1 public-loss sparse | 94 | 0.734474 | 0.006093 | 0.963079 |
| target route teacher only | 94 | 0.735985 | 0.007604 | 0.983825 |
| target route q2 extra | 108 | 0.736569 | 0.008188 | 0.983825 |
| public/private toxicity | 150 | 0.738233 | 0.009851 | 0.976793 |
| listener responsibility | 118 | 0.742779 | 0.014398 | 0.996016 |

관찰:

- aggressive correction일수록 route energy가 올라간다.
- `listener_responsibility`는 public-free support를 일부 복원하지만, 그대로 action으로 쓰면 target 공동 구조를 가장 많이 깨뜨린다.
- `public_private_toxicity`와 `target_route_q2_extra`도 current best보다 energy가 높다.
- 따라서 HS-JEPA decoder에는 support/action 생성기뿐 아니라 route-consistency veto가 필요하다.

## Veto 방식

candidate가 current best에서 바꾼 cell을 하나씩 검사한다.

각 cell에 대해:

1. candidate 값을 유지한 row vector의 route energy를 계산한다.
2. 해당 cell만 current best로 되돌린 row vector의 route energy를 계산한다.
3. 유지했을 때 energy가 tolerance 이상 증가하면 veto한다.

target별 tolerance는 다르게 둔다.

- Q2: listener responsibility 근거가 강하므로 조금 넓게 허용
- teacher cell: public-loss sparse teacher가 선택한 cell이므로 일반 extra보다 넓게 허용
- 그 외 extra: 보수적으로 허용

## Veto 결과

### 1. Public/Private Toxicity 후보에 veto 적용

입력:

- `submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv`
- changed cells: `150`

출력:

- `submission_hsjepa_route_energy_veto_public_private_toxicity_e08d9849_uploadsafe.csv`
- kept cells: `53`
- vetoed cells: `97`
- changed rows: `46`
- route energy: `0.738233 -> 0.725533`
- current best route energy: `0.728381`
- upload-safe: `true`

target별 kept:

| target | kept | vetoed |
|---|---:|---:|
| Q1 | 4 | 11 |
| Q2 | 7 | 28 |
| Q3 | 3 | 11 |
| S1 | 6 | 13 |
| S2 | 21 | 7 |
| S3 | 6 | 11 |
| S4 | 6 | 16 |

해석:

공격적 toxicity 후보에서 살아남은 cell은 150개 중 53개뿐이다.
특히 Q2 extra는 대부분 veto되었고, S2는 오히려 많이 살아남았다.
이것은 “Q2를 무조건 더 세게 건드리자”가 아니라,
“Q2는 강한 route지만 공동 label 구조를 깨지 않는 소수만 안전하다”는 뜻이다.

### 2. Target-Route Q2 Extra 후보에 veto 적용

입력:

- `submission_hsjepa_target_route_toxicity_q2_extra_90b62d2d_uploadsafe.csv`
- changed cells: `108`

출력:

- `submission_hsjepa_route_energy_veto_target_route_q2_extra_5dfa9e76_uploadsafe.csv`
- kept cells: `34`
- vetoed cells: `74`
- changed rows: `32`
- route energy: `0.736569 -> 0.726858`
- current best route energy: `0.728381`
- upload-safe: `true`

target별 kept:

| target | kept | vetoed |
|---|---:|---:|
| Q1 | 1 | 8 |
| Q2 | 8 | 26 |
| Q3 | 2 | 9 |
| S1 | 3 | 11 |
| S2 | 11 | 3 |
| S3 | 5 | 6 |
| S4 | 4 | 11 |

해석:

Q2 extra big-bet은 대부분 route-consistency 기준에서 탈락했다.
살아남은 Q2는 8개뿐이다.
반대로 S2는 11개가 살아남아, target-route decoder가 Q2 중심으로만
설계되면 중요한 safe route를 놓칠 수 있음을 보여준다.

## 논문형 의미

이 실험은 HS-JEPA에 LeJEPA식 energy diagnostic을 붙인 첫 명확한 형태다.

기존 구조:

```text
Human-State Encoder
    -> Listener Responsibility Solver
    -> Action Decoder
```

이번 확장:

```text
Human-State Encoder
    -> Listener Responsibility Solver
    -> Action Decoder
    -> Route-Consistency Energy Veto
```

즉 HS-JEPA는 action을 만들기만 하는 모델이 아니라,
그 action이 label manifold를 깨뜨리는지 검사하는 자기 검열 구조를 가진다.

## 현재 결론

가장 중요한 발견:

```text
큰 correction 후보가 public에서 실패하는 이유 중 하나는
cell 단위 support가 틀려서만이 아니라,
선택된 correction이 7-target 공동 구조를 깨기 때문이다.
```

따라서 다음 breakthrough 방향은 더 많은 action을 추가하는 것이 아니라:

1. listener responsibility로 후보 support를 찾고,
2. target-route toxicity로 target별 허용 강도를 정하고,
3. route-consistency energy로 공동 label 구조를 깨는 action을 veto하는 것이다.

## 제출 판단

가장 정보량이 큰 후보는 다음이다.

```text
submission_hsjepa_route_energy_veto_target_route_q2_extra_5dfa9e76_uploadsafe.csv
```

이유:

- Q2 extra big-bet의 핵심만 남겼다.
- changed cells가 34개라 public risk가 낮다.
- route energy가 current best보다도 낮아졌다.
- 좋아지면 route-consistency energy가 실제 action safety를 설명한다.
- 나빠지면 train-label manifold energy가 public/private safety와 다르다는 뜻이다.

두 번째 후보:

```text
submission_hsjepa_route_energy_veto_public_private_toxicity_e08d9849_uploadsafe.csv
```

이 후보는 더 공격적인 toxicity 후보를 53개 cell로 압축한 형태다.
좋아지면 public/private toxicity head는 맞았고, 문제는 extra action의 과잉이었다는 해석이 가능하다.
