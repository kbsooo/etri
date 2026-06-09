# Objective-Stage Factor Transport Solver HS-JEPA

## 실험 목적

직전 `Objective-Stage Bridge Conservation Solver`는 S-stage target에서
`driver + bridge` 구조가 강하다는 증거를 줬다.

이번 실험은 그보다 더 큰 법칙을 물었다.

> S1/S2/S3/S4는 row마다 임의의 pair bridge로 움직이는 것이 아니라,
> 하나의 objective sleep-state factor 방향으로 같이 움직이는가?

즉 stagebridge가 발견한 구조를 다음처럼 확장하려 했다.

```text
local driver + bridge
```

에서:

```text
shared S-stage latent factor transport
```

로.

이 가설이 맞으면 논문적으로 더 강하다.
HS-JEPA가 단순히 개별 target correction을 고른 것이 아니라,
objective sleep-state representation의 이동 방향을 복원했다고 말할 수 있기 때문이다.

## 코드

```bash
python3 paper_hsjepa_core/stage_factor_transport_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_stage_factor_transport_factor_paircore_7cde1a77_uploadsafe.csv`
- `submission_hsjepa_stage_factor_transport_factor_axis_jackpot_976bf3f9_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_transport_readout.json`
- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_driver_pool.csv`
- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_factor_paircore_selected.csv`
- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_factor_axis_jackpot_selected.csv`
- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_factor_paircore_candidates.csv`
- `paper_hsjepa_core/outputs/stage_factor_transport_solver/stage_factor_factor_axis_jackpot_candidates.csv`

## Public-free S-stage factor

Train labels의 S1/S2/S3/S4 covariance에서 1번 주성분을 구했다.

PC1 weights:

| target | weight |
|---|---:|
| S1 | 0.382789 |
| S2 | 0.651711 |
| S3 | 0.396470 |
| S4 | 0.521111 |

Explained variance ratio:

| component | ratio |
|---|---:|
| PC1 | 0.461050 |
| PC2 | 0.235979 |
| PC3 | 0.211421 |
| PC4 | 0.091549 |

중요한 관찰:

PC1은 모든 S target에 양수 weight를 갖고, 설명분산도 46.1%다.
즉 S-stage에는 public-free 공통 objective factor가 실제로 있다.

하지만 이것이 곧 action-grade factor라는 뜻은 아니다.
이번 실험은 바로 그 차이를 검증한다.

## 방법

1. public utility가 있는 S-stage driver cell을 고른다.
2. driver step이 S-stage PC1 위에 놓이도록 나머지 S target의 bridge step을 계산한다.
3. paircore는 driver + 가장 강한 factor bridge 하나만 허용한다.
4. axis_jackpot은 driver + 최대 3개 bridge, 즉 S1/S2/S3/S4 factor-axis 이동을 허용한다.
5. route energy, public utility, H088 toxicity, factor residual을 함께 평가한다.
6. PC1이 진짜인지 보기 위해 factor weight를 랜덤 permutation/sign flip한 null stress를 수행한다.

## 결과 요약

### Factor Paircore

제출 파일:

```text
submission_hsjepa_stage_factor_transport_factor_paircore_7cde1a77_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| candidate bundles | 0 |
| selected bundles | 0 |
| changed cells | 0 |
| route energy | 0.728381 |
| upload-safe | true |

해석:

paircore는 아무 action도 선택하지 못했다.
파일 hash가 `7cde1a77`인 것도 현재 best와 동일한 no-op이라는 뜻이다.

즉 PC1 방향에서 driver+single bridge를 강제하면,
stagebridge에서 발견한 local bridge보다 약하다.

### Factor Axis Jackpot

제출 파일:

```text
submission_hsjepa_stage_factor_transport_factor_axis_jackpot_976bf3f9_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| candidate bundles | 2 |
| selected bundles | 2 |
| selected cells | 8 |
| changed rows | 2 |
| bundle size | 4 targets x 2 rows |
| target counts | S1 2, S2 2, S3 2, S4 2 |
| route energy | 0.728248 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.016660 |
| H088 cosine | ~0 |
| upload-safe | true |

Axis jackpot은 아주 작은 수의 full S-stage factor bundle만 찾았다.
방향 자체는 깨끗하지만, 선택된 row가 2개뿐이라 대회 성능을 크게 움직일 후보는 아니다.

## Null Stress

PC1 factor가 random S-stage axis보다 강한지 보기 위해,
weight magnitude를 섞고 sign을 랜덤으로 뒤집은 null factor를 96회 만들었다.

Axis jackpot null 결과:

| 항목 | 값 |
|---|---:|
| actual candidate count | 2 |
| null candidate count mean | 2.375 |
| actual top score sum | 0.002627 |
| null top score mean | 0.001772 |
| top score z | 0.435 |
| p(null >= actual) | 0.292 |
| actual top energy gain | 0.033319 |
| null energy gain mean | 0.033958 |
| energy gain z | -0.016 |
| p(null >= actual) | 0.292 |

해석:

PC1이 random factor보다 압도적으로 강하지 않다.
특히 energy gain은 null과 거의 같다.

## 이번 실험의 결론

S-stage에는 분명한 common factor가 있다.

하지만:

```text
common factor exists
```

와

```text
common factor is the right action transport direction
```

은 다르다.

이번 실험은 두 번째 주장을 약화한다.

현재 evidence는 다음이 더 정확하다.

```text
S-stage label space에는 공통 objective factor가 있다.
하지만 public-safe action은 그 factor 전체를 따라 이동하지 않는다.
action-grade 구조는 row별 public-sensitive driver와 local bridge다.
```

## HS-JEPA 아키텍처에 주는 의미

이 실험은 stagebridge를 더 강하게 만든다.

왜냐하면 가능한 더 큰 이론인 “전체 S-stage factor transport”를 테스트했는데,
실제로는 거의 선택되지 않았기 때문이다.

따라서 HS-JEPA decoder는:

```text
S-stage factor encoder
  -> row-specific driver detector
  -> local bridge solver
```

여야 한다.

`S-stage factor encoder`는 representation으로는 유용하다.
하지만 action decoder가 그 factor를 그대로 따라가면 안 된다.

## 제출 판단

두 파일 모두 upload-safe지만, public 제출 우선순위는 낮다.

- `factor_paircore`는 no-op이다.
- `factor_axis_jackpot`은 8 cells만 바꾸는 diagnostic이다.

현재 public slot 우선순위는 유지한다.

1. `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`
2. `submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv`
3. `submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv`

이 실험의 가치는 제출 후보가 아니라,
HS-JEPA 논문 구조를 좁힌 데 있다.
