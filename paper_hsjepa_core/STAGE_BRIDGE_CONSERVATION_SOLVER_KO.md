# Objective-Stage Bridge Conservation Solver HS-JEPA

## 실험 목적

직전 `Row-Bundle Transport Solver`는 중요한 negative result를 줬다.

같은 row 안에서 여러 target을 함께 움직이는 bundle을 허용했지만,
Q2+S2 bundle이나 triad는 살아남지 않았다.
대부분의 action은 singleton으로 돌아갔다.

하지만 그 실험은 bundle 안의 모든 cell을 public utility action으로 취급했다.

이번 실험은 질문을 바꾼다.

> public-loss가 지지하는 driver action 하나를 움직일 때,
> S-stage manifold를 보존하기 위해 public utility가 약한 bridge action을 같이 움직여야 하는가?

즉 이번 구조는 단순 bundle이 아니다.

```text
driver = public-loss sensor가 지지하는 주 action
bridge = route energy를 낮추기 위한 objective-stage 보존 action
```

## 핵심 한 줄

S1/S2/S3/S4 objective-stage target에서 driver+bridge 구조를 만들자,
모든 selected action이 2-cell bridge bundle로 바뀌었고,
S2가 bridge/driver 양쪽의 허브로 반복 선택되었다.

## 코드

```bash
python3 paper_hsjepa_core/stage_bridge_conservation_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv`
- `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_conservation_readout.json`
- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_driver_pool.csv`
- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_stagebridge_selected.csv`
- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_stagebridge_jackpot_selected.csv`
- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_stagebridge_candidates.csv`
- `paper_hsjepa_core/outputs/stage_bridge_conservation_solver/stage_bridge_stagebridge_jackpot_candidates.csv`

## 배경 관찰

Train label에서 S-stage target은 Q target보다 서로 강하게 연결된다.

상관:

| pair | corr |
|---|---:|
| S2-S4 | 0.478 |
| S2-S3 | 0.394 |
| S1-S2 | 0.382 |
| S1-S3 | 0.118 |
| S1-S4 | 0.107 |
| S3-S4 | 0.086 |

반면 Q2와 S targets는 거의 독립에 가깝다.

| pair | corr |
|---|---:|
| Q2-S1 | 0.052 |
| Q2-S2 | 0.003 |
| Q2-S3 | -0.052 |
| Q2-S4 | -0.024 |

따라서 Q2/S2 bundle이 안 살아난 것은 이상한 결과가 아니다.
S-stage 내부, 특히 S2 hub가 더 자연스러운 bridge 축이다.

## 구조

각 row에서 S-stage driver 후보를 고른다.

driver 후보:

- target in `S1/S2/S3/S4`
- public utility가 있음
- source/listener support가 있음
- stability와 toxicity 조건을 통과

그 다음 같은 row의 다른 S target을 bridge로 붙여본다.

bridge 후보:

- `S1/S2/S3/S4` 중 driver가 아닌 target
- public utility가 없어도 허용
- 여러 step 크기를 grid search
- route energy를 낮추면 강하게 보상
- public utility를 해치면 penalty

선택 기준:

```text
score =
public utility
+ route energy decrease bonus
- route energy increase penalty
- bridge public harm penalty
+ same-direction / S2-hub bonus
```

## 결과 요약

### Stagebridge

제출 파일:

```text
submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| stage driver pool cells | 56 |
| candidate actions | 391 |
| selected bundles | 30 |
| selected cells | 60 |
| selected bridge bundles | 30 |
| changed rows | 30 |
| mean route energy | 0.725652 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.022745 |
| negative energy bundles | 29 |
| H088 cosine | 0.006676 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| S1 | 12 |
| S2 | 24 |
| S3 | 8 |
| S4 | 16 |

Bridge counts:

| bridge target | count |
|---|---:|
| S1 | 7 |
| S2 | 14 |
| S3 | 2 |
| S4 | 7 |

해석:

모든 selected bundle이 driver+bridge 구조다.
S2가 24회 등장했고, bridge로도 14회 쓰였다.
30개 중 29개 bundle이 route energy를 낮췄다.

이것은 S2가 단순히 target 하나가 아니라 objective-stage balance를 맞추는 허브일 수 있음을 보여준다.

### Stagebridge Jackpot

제출 파일:

```text
submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv
```

결과:

| 항목 | 값 |
|---|---:|
| stage driver pool cells | 56 |
| candidate actions | 556 |
| selected bundles | 41 |
| selected cells | 82 |
| selected bridge bundles | 41 |
| changed rows | 41 |
| mean route energy | 0.724352 |
| current best route energy | 0.728381 |
| mean selected energy delta | -0.024566 |
| negative energy bundles | 38 |
| H088 cosine | -0.006888 |
| upload-safe | true |

Target counts:

| target | count |
|---|---:|
| S1 | 17 |
| S2 | 32 |
| S3 | 11 |
| S4 | 22 |

Bridge counts:

| bridge target | count |
|---|---:|
| S1 | 10 |
| S2 | 19 |
| S3 | 2 |
| S4 | 10 |

해석:

Jackpot variant는 더 공격적이다.
82 cells를 움직이지만 H088 cosine은 오히려 음수이고, route energy는 지금까지 가장 낮은 축이다.
public risk는 크지만, big-bet 정보량은 높다.

## 이번 실험의 가장 중요한 발견

이전 bundle 실험에서는 “모든 cell이 public action인 bundle”을 봤고, 대부분 singleton으로 무너졌다.

이번 bridge 실험에서는 “public action + route-preserving bridge”를 봤고, 모든 selected action이 2-cell bridge bundle이 되었다.

따라서 결론은 다음처럼 바뀐다.

```text
HS-JEPA에서 큰 row-level target bundle은 약하다.
하지만 objective-stage driver action은 S2-hub bridge를 필요로 한다.
```

즉, hidden state는 label 전체를 크게 옮기는 vector가 아니라:

```text
public-sensitive driver
        +
objective-stage conservation bridge
```

형태로 번역될 수 있다.

## 논문형 의미

이 실험은 HS-JEPA를 더 강한 아키텍처로 만든다.

기존 decoder:

```text
support -> action
```

이번 decoder:

```text
support -> driver action
route energy -> bridge action
driver + bridge -> human-state transition
```

I-JEPA식으로 보면:

- context: public-sensitive action support, row state, S-stage target context
- target representation: 보이지 않는 objective-stage balance bridge
- prediction: raw label이 아니라 bridge action

LeJEPA식으로 보면:

- bridge는 prediction loss만으로 선택하지 않는다.
- route energy와 toxicity alignment로 shortcut/collapse를 막는다.

## 제출 판단

정보량이 가장 큰 후보:

```text
submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv
```

이유:

- S2-hub bridge 가설을 가장 크게 건다.
- route energy가 `0.724352`로 가장 낮다.
- H088 cosine이 음수다.
- 좋아지면 HS-JEPA의 `driver + bridge` decoder가 강하게 입증된다.
- 나빠지면 route energy가 public/private safety를 과대평가하거나, 82-cell action이 너무 공격적이라는 뜻이다.

더 보수적인 후보:

```text
submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv
```

이 후보는 60 cells만 움직이고, 동일한 bridge 가설을 더 작게 테스트한다.

현재 제출 우선순위:

1. `stagebridge_jackpot`
2. `stagebridge`
3. `energy_utility_solver_jackpot`
4. `row_bundle_paircore`
