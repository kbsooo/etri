# S2-Hub Bridge Solver HS-JEPA

## 실험 목적

`Objective-Stage Bridge Conservation Solver`는 S-stage action에서 S2가 반복적으로 등장한다는 신호를 줬다.

하지만 직후 `Objective-Stage Factor Transport Solver`는 더 큰 가설을 약화했다.

```text
S1/S2/S3/S4 전체가 하나의 factor axis로 같이 움직인다
```

는 action-grade 구조가 아니었다.

그래서 이번 실험은 더 좁고 구체적인 가설을 세웠다.

> S2는 전체 S-stage factor가 아니라,
> public-sensitive S-stage action을 안전하게 만드는 local listener / bridge hub인가?

## 핵심 한 줄

S2를 모든 selected bundle에 포함시키면,
stagebridge_jackpot보다 작은 68-cell 후보가 만들어지고 route energy도 낮게 유지된다.
다만 S2는 energy-gain hub라기보다 public-utility hub에 가깝다.

## 코드

```bash
python3 paper_hsjepa_core/s2hub_bridge_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_s2hub_bridge_s2bridge_core_2cec9d38_uploadsafe.csv`
- `submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_bridge_readout.json`
- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_driver_pool.csv`
- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_s2bridge_core_selected.csv`
- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_s2hub_jackpot_selected.csv`
- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_s2bridge_core_raw_candidates.csv`
- `paper_hsjepa_core/outputs/s2hub_bridge_solver/s2hub_s2hub_jackpot_raw_candidates.csv`

## 구조

기존 stagebridge candidate generator를 그대로 사용한다.
그 다음 선택 조건만 S2-hub로 제한한다.

### S2 Bridge Core

조건:

- bridge target이 반드시 S2
- driver는 S1/S3/S4 중 하나
- route energy gain이 충분해야 함
- public utility가 있어야 함

즉:

```text
S1/S3/S4 driver -> S2 bridge
```

만 허용한다.

### S2 Hub Jackpot

조건:

- driver 또는 bridge 중 하나가 반드시 S2
- S2가 driver인 bundle도 허용
- 더 넓은 jackpot 조건 사용

즉:

```text
S2 driver -> other S bridge
other S driver -> S2 bridge
```

를 모두 허용한다.

## 결과 요약

### S2 Bridge Core

제출 파일:

```text
submission_hsjepa_s2hub_bridge_s2bridge_core_2cec9d38_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| raw candidate bundles | 391 |
| S2-bridge candidate bundles | 73 |
| selected bundles | 21 |
| selected cells | 42 |
| changed rows | 21 |
| S2 bridge bundles | 21 |
| route energy | 0.726721 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.019761 |
| negative-energy bundles | 21 |
| H088 cosine | -0.006979 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| S1 | 7 |
| S2 | 21 |
| S3 | 5 |
| S4 | 9 |

해석:

모든 selected bundle이 S2 bridge를 포함했고,
모든 bundle이 route energy를 낮췄다.
이건 S2 bridge 가설의 깨끗한 positive evidence다.

다만 selected cells가 42개라 stagebridge_jackpot보다 보수적이다.

### S2 Hub Jackpot

제출 파일:

```text
submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| raw candidate bundles | 556 |
| S2-hub candidate bundles | 302 |
| selected bundles | 34 |
| selected cells | 68 |
| changed rows | 34 |
| S2 bridge bundles | 22 |
| S2 driver bundles | 12 |
| route energy | 0.724714 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.026964 |
| negative-energy bundles | 34 |
| H088 cosine | -0.000696 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| S1 | 12 |
| S2 | 34 |
| S3 | 7 |
| S4 | 15 |

해석:

S2가 모든 selected bundle에 들어간다.
stagebridge_jackpot보다 cells는 적다.

비교:

| file | changed cells | route energy | H088 cosine |
|---|---:|---:|---:|
| stagebridge_jackpot | 82 | 0.724352 | -0.006888 |
| s2hub_jackpot | 68 | 0.724714 | -0.000696 |
| stagebridge | 60 | 0.725652 | 0.006676 |

`s2hub_jackpot`은 stagebridge_jackpot보다 약간 덜 공격적이고,
stagebridge보다 route energy가 낮다.

따라서 public slot이 있다면,
stagebridge_jackpot보다 약간 보수적인 같은 계열 후보로 의미가 있다.

## Hub Contrast

S2가 정말 특별한지 보기 위해 bridge target별 top-score를 비교했다.

### Core setting

| bridge hub | candidate count | top score sum | top energy gain | top public utility |
|---|---:|---:|---:|---:|
| S1 | 101 | 0.055330 | 0.793083 | 0.024534 |
| S2 | 88 | 0.056191 | 0.591924 | 0.030653 |
| S3 | 86 | 0.055488 | 0.785439 | 0.025560 |
| S4 | 94 | 0.049870 | 0.705675 | 0.021953 |

### Jackpot setting

| bridge hub | candidate count | top score sum | top energy gain | top public utility |
|---|---:|---:|---:|---:|
| S1 | 141 | 0.101325 | 1.302853 | 0.041932 |
| S2 | 124 | 0.100055 | 1.119361 | 0.045601 |
| S3 | 129 | 0.100370 | 1.305588 | 0.042037 |
| S4 | 137 | 0.089480 | 1.188754 | 0.035366 |

중요한 해석:

S2가 모든 기준에서 압도적인 hub는 아니다.
energy gain만 보면 S1/S3도 강하다.

하지만 S2는 top public utility가 가장 높다.

따라서 S2의 정확한 역할은:

```text
objective-stage energy hub
```

라기보다:

```text
public-sensitive S-stage listener / utility hub
```

에 가깝다.

## HS-JEPA 아키텍처에 주는 의미

현재 objective-stage decoder는 다음처럼 정리된다.

```text
S-stage factor encoder
  -> public-sensitive S2 listener/hub
  -> row-local driver/bridge solver
```

S2는 전체 factor를 대표하는 단일 축이 아니다.
하지만 public이 민감하게 듣는 S-stage route에서 중심 target처럼 행동한다.

이것은 HS-JEPA의 decoder를 더 구체화한다.

```text
context -> hidden S-stage representation -> listener target(S2) -> local bridge action
```

## 제출 판단

우선순위:

1. `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`
   - 가장 공격적인 stagebridge big-bet
2. `submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv`
   - S2-hub를 명시적으로 검증하는 더 해석 가능한 후보
3. `submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv`
   - 작은 stagebridge 후보
4. `submission_hsjepa_s2hub_bridge_s2bridge_core_2cec9d38_uploadsafe.csv`
   - 가장 깨끗한 S2-bridge diagnostic

`s2hub_jackpot`이 public에서 좋아지면:

```text
S2 listener/hub decoder
```

가 HS-JEPA의 핵심 paper claim이 된다.

나빠지면:

```text
S2는 반복적으로 보이는 local 신호지만,
강제 hub로 쓰면 public/private action safety가 깨진다.
```

로 해석한다.
