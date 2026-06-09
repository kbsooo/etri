# Target-Listener Route Lift Solver HS-JEPA

## 한 줄 요약

이 실험은 `row를 직접 맞히는 모델`이 아니라 `target/cell listener posterior를 먼저 복원한 뒤, route-energy로 안전한 row-target action만 들어올리는 모델`을 테스트한다.

## 왜 필요한가

S2-hub human-state distillation에서 이상한 비대칭이 나왔다.

| 항목 | 결과 |
| --- | ---: |
| S2-hub cell-level OOF AUC | `0.775` |
| S2-hub row-level OOF AUC | `0.545` |
| Stagebridge cell-level OOF AUC | `0.722` |
| Stagebridge row-level OOF AUC | `0.493` |

즉 OG human-state는 `어느 target/cell route가 그럴듯한지`는 꽤 잘 설명하지만, `어느 row를 고칠지`는 잘 설명하지 못한다.

그래서 질문을 바꿨다.

```text
Q. row assignment를 바로 예측하지 말고,
   target listener posterior를 먼저 만든 뒤
   route-energy가 허용하는 cell만 row action으로 들어올리면 어떨까?
```

## HS-JEPA 관점

일반적인 row classifier 관점에서는 row별로 action 여부를 예측하려고 한다.

하지만 HS-JEPA에서는 row가 먼저가 아니라 listener가 먼저다.

```text
OG human-state context
  -> target/cell listener posterior
  -> route-energy constrained row lift
  -> sparse correction field
```

이 구조는 JEPA식으로 보면 다음과 같다.

| JEPA 요소 | 이 실험의 해석 |
| --- | --- |
| context | OG human-state atlas, cohort state, target identity, peer margin |
| target representation | S2-hub/stagebridge teacher의 row-target action field |
| predictor | target/cell listener posterior student |
| energy | train-label Q/S route-consistency energy |
| decoder | posterior가 높은 cell 중 route를 깨지 않는 action만 추가 |

## 실험 방법

1. `s2hub_jackpot` 또는 `stagebridge_jackpot`을 teacher action field로 둔다.
2. OG human-state + target context로 subject-held-out cell student를 학습한다.
3. OOF cell posterior를 row별로 aggregate해서 row-lift 가능성을 진단한다.
4. full student posterior가 높은 non-teacher cell을 후보로 만든다.
5. route-energy 증가가 작은 후보만 추가 action으로 채택한다.
6. teacher action은 유지하되 variant별로 amplitude를 조금 조정한다.

## 생성 파일

코드:

- `paper_hsjepa_core/target_listener_route_lift_solver.py`

readout:

- `paper_hsjepa_core/outputs/target_listener_route_lift_solver/target_listener_route_lift_readout.json`

제출 후보:

- `submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_core_88b45606_uploadsafe.csv`
- `submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv`
- `submission_hsjepa_target_listener_route_lift_stagebridge_listener_lift_jackpot_0365d7d9_uploadsafe.csv`

## 결과

### 1. S2-hub listener lift core

| 항목 | 값 |
| --- | ---: |
| teacher cells | `68` |
| extra pool cells | `0` |
| extra selected cells | `0` |
| mean route energy | `0.724763` |
| H088 cosine | `-0.000696` |
| changed cells vs current best | `68` |

해석:

core 설정은 너무 보수적이었다. 사실상 S2-hub teacher amplitude만 `0.98`로 줄인 후보가 되었다.

### 2. S2-hub listener lift jackpot

| 항목 | 값 |
| --- | ---: |
| teacher cells | `68` |
| extra pool cells | `13` |
| extra selected cells | `13` |
| extra selected rows | `12` |
| extra target counts | `S2=10`, `S1=1`, `S4=2` |
| mean extra route energy delta | `-0.001124` |
| mean route energy | `0.724585` |
| H088 cosine | `-0.000532` |
| changed cells vs current best | `81` |

해석:

이 변형만 실제로 추가 action을 찾았다. 추가된 13개 cell 중 10개가 S2였고, 평균 route-energy delta가 음수다.

이는 `S2 listener posterior + route energy` 조합이 완전히 죽은 아이디어는 아니라는 뜻이다.

하지만 추가 cell 수가 작고, row-lift OOF가 약하므로 아직 제출 1순위는 아니다.

### 3. Stagebridge listener lift jackpot

| 항목 | 값 |
| --- | ---: |
| teacher cells | `82` |
| extra pool cells | `1` |
| extra selected cells | `1` |
| extra target counts | `S2=1` |
| mean route energy | `0.724353` |
| H088 cosine | `-0.005828` |
| changed cells vs current best | `83` |

해석:

Stagebridge teacher는 이미 bridge solver가 대부분의 action을 찾은 상태라, listener-lift가 새로 추가할 공간이 거의 없었다.

## 가장 중요한 진단

S2-hub teacher에서 cell posterior는 강하지만 row-lift는 약하다.

| row aggregation | AUC | AP |
| --- | ---: | ---: |
| max cell posterior | `0.556` | `0.168` |
| mean cell posterior | `0.544` | `0.166` |
| top2 cell posterior | `0.542` | `0.165` |
| S2 posterior | `0.561` | `0.157` |

따라서 다음 주장은 약화된다.

```text
cell posterior를 row로 aggregate하면 row assignment가 풀린다.
```

대신 다음 주장이 강화된다.

```text
HS-JEPA에서 target listener는 action orientation/route 보조 역할을 한다.
row assignment는 별도 listener responsibility solver 또는 public/private decoder가 필요하다.
```

## 제출 판단

현재 제출 우선순위는 다음과 같다.

1. `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`
2. `submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv`
3. `submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv`
4. `submission_hsjepa_ogdistilled_s2hub_jackpot_38d995b0_uploadsafe.csv`

`s2hub_listener_lift_jackpot`은 제출 슬롯을 쓸 수는 있지만, 질문은 성능 1순위가 아니라 다음이다.

```text
target-listener posterior가 약한 row assignment를 뚫고
route-energy-safe extra S2 action을 실제 public에서도 살릴 수 있는가?
```

좋아지면:

- S2 listener posterior가 action-grade라는 뜻이다.
- HS-JEPA decoder에 `target listener -> route lift` 모듈을 넣을 수 있다.

나빠지면:

- target listener posterior는 representation/diagnostic으로만 유효하다.
- row assignment는 stagebridge/public-private solver가 계속 맡아야 한다.

## 논문에서의 의미

이 실험은 대박 성능 후보라기보다 HS-JEPA의 모듈 경계를 선명하게 만든다.

```text
Human-State Encoder:
  target/cell route orientation을 설명한다.

Target Listener:
  S2-hub 같은 objective listener posterior를 만든다.

Row Assignment Solver:
  아직 human-state만으로는 약하므로 별도 solver가 필요하다.

Route Energy:
  listener가 제안한 extra action 중 route를 깨지 않는 것만 통과시킨다.
```

즉 HS-JEPA는 하나의 거대한 classifier가 아니라, hidden human-state, target listener, row assignment, route energy가 역할을 나눠 갖는 joint embedding predictive architecture다.
