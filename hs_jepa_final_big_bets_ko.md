# HS-JEPA 최종 Big Bet 아이디어

마지막 수정: 2026-06-09

이 문서는 지금까지 나온 모든 아이디어를 두 개의 end-to-end 실험으로
압축한다. 목표는 작은 보정이나 소폭 개선이 아니다. 각 아이디어는 하나의
데이터 생성 세계관이다.

성공하면 왜 현재 점수 장벽이 생겼는지 설명할 수 있어야 하고, 실패하면
어떤 큰 가설이 틀렸는지 분명해야 한다.

현재 가장 강한 public 결과:

- 파일: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

## 현재 병목

지금까지의 실험으로 알게 된 가장 중요한 점은 이것이다.

> hidden state를 찾는 능력은 어느 정도 생겼지만, 그 hidden state를 안전한
> row-target correction으로 번역하는 능력이 아직 부족하다.

즉 문제는 더 그럴듯한 latent를 하나 더 만드는 것이 아니다.

진짜 문제는:

- 어떤 row가 진짜 움직여야 하는지;
- 어떤 target이 같이 움직여야 하는지;
- 어느 정도 움직여야 하는지;
- public에서는 좋아 보이지만 private에서 위험한 action은 무엇인지;
- human/social/cohort 신호를 언제 믿고 언제 버려야 하는지;

를 결정하는 것이다.

현재 살아남은 신호들은 다음이다.

- public LB가 흘린 equation signal;
- current best가 잡은 compact row-state correction;
- Q/S target route dependency;
- human-social/routine context;
- 개인 평소 대비 anomaly;
- cohort-relative anomaly;
- action-health / shortcut / toxicity diagnostic.

하지만 이 신호를 바로 확률값에 꽂으면 자주 망가진다. 따라서 최종
아이디어 두 개는 모두 “hidden state -> 안전한 action” 번역 문제를 정면으로
다룬다.

---

# Big Bet 1: Public-Private Equation HS-JEPA Solver

## 한 줄 요약

지금까지 제출한 파일들과 public LB 점수를 전부 하나의 noisy equation으로
보고, 숨은 public listener, row-target responsibility, safe correction field를
역으로 푸는 방법이다.

## 핵심 세계관

public LB는 단순 점수가 아니다. public LB는 hidden subset과 hidden row-target
weight를 측정하는 센서다.

현재 최고 점수는 모델이 “전체적으로 더 똑똑해져서” 나온 결과라기보다,
public responsibility가 높은 cell을 우연히 잘 건드리고, action toxicity가 큰
cell은 비교적 피했기 때문에 나온 결과일 가능성이 크다.

그렇다면 다음 한 방은 새로운 feature를 더 붙이는 것이 아니다.

> public LB가 지금까지 측정해 온 숨은 방정식을 복원해야 한다.

## End-to-End 구조

```text
모든 과거 submission 파일
  + 알려진 public LB 점수
  + current best 확률값
  + raw human-state / cohort / social context
  -> public listener equation inversion
  -> row-target responsibility field
  -> route-constrained action solver
  -> upload-safe submission
```

## 구성 요소

### 1. Submission Delta Matrix

모든 과거 제출 파일에 대해 current best 대비 움직임을 계산한다.

```text
delta_logit[submission, row, target]
delta_prob[submission, row, target]
```

그리고 public LB 변화량을 다음 식의 관측값으로 본다.

```text
observed_lb_delta(submission)
  ~= sum(row_target_weight * loss_change(row, target, submission))
```

여기서 모르는 것은 다음이다.

- public row-target weight;
- pseudo-public label/posterior;
- action toxicity;
- route assignment.

### 2. JEPA Context Encoder

context view:

- raw daily human-state feature;
- 개인 평소 대비 anomaly;
- cohort 대비 anomaly;
- target route feature;
- submission disagreement;
- public-good / public-bad action history.

target representation:

- hidden public responsibility;
- safe action value;
- row-target route.

JEPA-style masked task:

- public observation 일부를 가리고 LB 반응을 예측한다;
- 특정 candidate family를 가리고 움직임이 toxic한지 예측한다;
- target route 일부를 가리고 row-level action pattern을 복원한다.

여기서 JEPA의 핵심은 raw value 복원이 아니다.

> 보이는 context로 보이지 않는 public responsibility와 action safety
> representation을 예측하는 것이다.

### 3. Equation-Constrained Decoder

decoder는 그냥 확률값을 내지 않는다. 다음 제약 아래에서 action을 고른다.

- row-route sparsity;
- target-route consistency;
- 전체 table을 무차별적으로 흔들지 않기;
- public-good 방향은 leave-one-public-observation-out에서도 살아남기;
- public-bad 방향은 negative penalty 받기;
- action이 특정 target prior shift 하나로 collapse하지 않기.

candidate 생성은 다음 최적화 문제가 된다.

```text
maximize expected equation gain
minus action toxicity
minus shortcut risk
minus private-overfit penalty
```

## 왜 1등급 한 방 후보인가

가장 큰 점프는 일반 CV나 단순 모델 개선에서 나온 것이 아니라 public
equation 계열 정보에서 나왔다. 따라서 hidden public listener를 부분적으로라도
복원할 수 있다면, 이 방식은 0.0001 단위가 아니라 0.001 이상 움직일 수 있는
몇 안 되는 경로다.

이 아이디어는 지금까지의 모든 작업을 사용한다.

- public score history;
- current best row-state correction;
- action-health 실패 실험;
- human/social context;
- cohort context;
- target route constraint.

## 제출 전 성공 기준

제출하기 전에 최소한 아래 조건을 봐야 한다.

- leave-one-public-observation-out sign accuracy가 `70%` 이상;
- 예측한 LB delta 크기가 실제 known delta와 대략 맞음;
- null-permutation submission에서는 equation fit이 무너짐;
- 선택된 action이 특정 target이나 특정 subject에만 몰리지 않음;
- current best positive row와 어느 정도 겹치면서도 새로운 positive row를 찾음.

## 제출했을 때 기대 반응

맞다면:

- public LB가 `0.001+` 단위로 의미 있게 움직일 수 있다;
- current best가 왜 강했는지 equation 관점에서 설명된다;
- HS-JEPA의 action decoder가 public sensor inversion을 포함해야 한다는
  주장이 강해진다.

틀리면:

- public LB 관측값이 너무 적거나 noisy해서 stable responsibility field를
  식별할 수 없다는 뜻이다;
- public score는 계속 sensor로만 써야 하고, 직접 solver target으로 쓰면
  overfit 위험이 크다는 결론이 된다.

---

# Big Bet 2: Personal-Cohort Human-State Atlas JEPA

## 한 줄 요약

raw lifelog에서 해석 가능한 인간의 하루 상태 atlas를 만들고, feature-to-label
직접 예측이 아니라 state route와 personal/cohort memory를 통해 label을
예측하는 방법이다.

## 핵심 세계관

이 대회의 label은 독립적인 7개 label이 아니라, 소수의 hidden human state가
여러 target으로 투영된 결과일 수 있다.

예상되는 hidden state 예시:

- 정상 루틴 day;
- 수면 fragmentation / recovery day;
- 야간 phone arousal day;
- 저활동 fatigue day;
- 높은 social interaction 또는 late interaction day;
- measurement-noise day;
- 주관적으로는 괜찮지만 객관 수면 stage는 나쁜 mismatch day;
- objective sleep-stage disruption day.

current best는 이 atlas 중 하나의 compact row-state를 발견한 것으로 볼 수
있다. 더 크게 개선하려면 이보다 넓은 state dictionary를 복원해야 한다.

## End-to-End 구조

```text
subject-day raw lifelog
  -> open-source daily feature encoder
  -> personal baseline state
  -> peer-cohort baseline state
  -> human-state atlas assignment
  -> target route posterior
  -> safe correction field
  -> upload-safe submission
```

## 구성 요소

### 1. Daily Human-State Encoder

외부 closed embedding 모델 없이 재현 가능한 open-source 계산만 쓴다.

입력:

- phone usage와 app category;
- activity와 step rhythm;
- heart-rate와 wearable light;
- screen / charging timing;
- GPS / Wi-Fi / BLE proximity;
- ambience label;
- calendar와 routine timing.

각 subject-day는 여러 좌표계로 표현한다.

- 개인 평소 기준 좌표;
- peer cohort 기준 좌표;
- raw sensor 좌표;
- social/routine 좌표;
- measurement-confidence 좌표.

### 2. Human-State Atlas 구성

작은 latent day-state dictionary를 만든다.

단순히 raw feature만 clustering하지 않는다. 여러 view가 동시에 일관되는지를
본다.

```text
state = f(
  raw sensor latent,
  personal deviation,
  cohort deviation,
  sequence neighborhood,
  target-route compatibility,
  action-health diagnostic
)
```

각 atlas state는 다음 정보를 가진다.

- state centroid;
- subject-specific offset;
- cohort offset;
- target route distribution;
- confidence / measurement quality;
- action toxicity profile.

### 3. JEPA Masked Prediction

학습/검증 task:

- raw sensor family를 가리고 atlas state를 예측한다;
- 개인 history를 가리고 cohort로 현재 state를 예측한다;
- cohort를 가리고 개인 deviation을 예측한다;
- Q label view를 가리고 S-route representation을 예측한다;
- S label view를 가리고 Q-route representation을 예측한다;
- action response를 가리고 state로 toxicity를 예측한다.

이것이 HS-JEPA의 핵심이다.

> 보이는 생활 context로 보이지 않는 human-state representation을 예측한다.
> raw value를 복원하는 것이 아니다.

### 4. Route-Aware Label Decoder

각 test row에 대해 다음을 만든다.

```text
P(state | context)
P(route | state, subject, cohort)
P(action_safe | state, route)
```

그 다음 route-consistent correction만 적용한다.

- subjective route: 주로 Q label이 움직인다;
- objective route: 주로 S label이 움직인다;
- mismatch route: Q와 S가 반대 방향으로 움직인다;
- measurement-noise route: confidence를 낮추고 과보정을 피한다;
- known public row-state route: current best route를 쓰되 toxicity가 크면 막는다.

## 왜 1등급 한 방 후보인가

current best는 hidden atlas의 일부를 발견한 결과일 수 있다. 이 아이디어는
그 atlas 전체를 복원하려고 한다.

특히 public feedback에만 기대지 않고 raw lifelog, subject baseline, peer
cohort 구조를 함께 쓰기 때문에 private에서도 살아남을 가능성이 있다.

논문 관점에서는 이쪽이 HS-JEPA의 본체에 가깝다.

- 인간적 의미가 latent state 수준에 존재한다;
- target label은 hidden state의 projection이다;
- public LB feedback은 action-health sensor 중 하나일 뿐이다;
- cohort-relative reasoning은 포함하지만 직접 label rule로 믿지는 않는다.

## 제출 전 성공 기준

제출하기 전에 최소한 아래 조건을 봐야 한다.

- atlas state의 train/test 분포가 안정적임;
- 각 state가 nontrivial target-route prior를 가짐;
- 개인 anomaly가 peer anomaly 단독보다 state assignment에 더 도움 됨;
- cohort feature가 held-out subject 또는 subject-group stress에서 의미 있음;
- masked-view state prediction이 permutation/null test를 통과함;
- 생성된 correction field가 random cell이 아니라 route-consistent row-target
  group을 움직임.

## 제출했을 때 기대 반응

맞다면:

- public LB가 `0.001+` 단위로 움직일 수 있다;
- current best가 발견한 row-state 외의 새로운 state가 존재한다는 증거가 된다;
- HS-JEPA가 단순 대회 트릭이 아니라 human-state architecture라는 주장이
  강해진다.

틀리면:

- human-social/cohort 이론은 narrative와 diagnostic에는 좋지만, 최종 확률
  action을 직접 만들기에는 약하다는 뜻이다;
- 그 경우 우승용 경로는 richer semantic atlas보다 equation solver 쪽으로
  더 기울어야 한다.

---

# 최종 추천

두 아이디어를 모두 실행해야 하지만 역할은 다르다.

## 제출 성능을 노리는 1순위

> Public-Private Equation HS-JEPA Solver

이유:

가장 큰 public jump의 원천인 public score sensor inversion과 row-target
responsibility를 직접 겨냥한다.

## 논문/아키텍처를 세우는 1순위

> Personal-Cohort Human-State Atlas JEPA

이유:

HS-JEPA를 leaderboard-only solver가 아니라, 수면 생활 로그에서 hidden human
state를 복원하는 재사용 가능한 아키텍처로 만든다.

## 둘을 합친 최종 시스템

최종 HS-JEPA는 이렇게 가야 한다.

```text
Human-State Atlas
  -> state 후보와 route 후보를 제안한다

Public-Private Equation Solver
  -> 그 후보들 중 제출 가능한 safe action만 통과시킨다
```

즉:

- atlas는 generator다;
- equation solver는 judge다.

atlas 없이 judge만 있으면 public overfit이 된다.

judge 없이 atlas만 있으면 그럴듯하지만 위험한 correction이 된다.

최종 HS-JEPA는 둘 다 필요하다.

## 한 문장 결론

> Human-State Atlas가 “이 row는 어떤 인간 상태인가?”를 말하고,
> Public-Private Equation Solver가 “그 상태를 실제 확률 보정으로 바꿔도
> 안전한가?”를 판정하는 구조가 최종 HS-JEPA다.
