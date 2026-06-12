# Lifelog Core State Evidence

## 한 줄 결론

HS-JEPA core는 현재 단계에서 `label을 바로 맞히는 분류기`라기보다, 원천 생활 로그를 action-safe human-state geometry로 바꿔 row-action support를 재발견하게 만드는 representation module에 가깝다.

## 왜 이 실험이 필요한가

지금까지의 좋은 public 결과는 일부 public equation, row-state vector, active-silence 같은 competition adapter와 강하게 연결되어 있었다.

그 상태로 논문을 쓰면 다음 비판을 피하기 어렵다.

> HS-JEPA가 좋은 게 아니라, 특정 대회 LB에 맞춘 sparse correction이 좋은 것 아닌가?

그래서 별도 실험을 만들었다.

```bash
python3 hsjepa_core/run_lifelog_core_state_evidence.py
```

이 실험은 public LB ledger를 읽지 않는다. Gemini 같은 proprietary embedding도 쓰지 않는다. `peer_margin_*`, `target_route_margin_*`처럼 train label을 써서 만든 feature는 core-only 검증에서 제외한다.

즉 질문은 단순하다.

> OG lifelog에서 만든 HS-JEPA human-state representation만으로도 인간 상태 구조가 보이는가?

## 실험 구성

입력은 `team_experiments/cohort_hsjepa/cohort_human_state_features.csv`다.

이 feature table은 OG raw lifelog에서 만든 daily context를 담는다.

- calendar/rhythm
- phone behavior
- body/activity/sleep sensor
- app/social context
- mobility/environment
- PCA 기반 human-state latent
- personal normal distance
- peer/cohort normal distance
- cohort outlier score

core-only 검증에서는 다음을 제외한다.

- `peer_margin_Q1` ... `peer_margin_S4`
- `target_route_margin_q2q3s2`
- public score ledger
- 제출 파일별 public LB

## Public-Free Evidence

### 1. Label Manifold Probe

subject가 train/validation 양쪽에 동시에 들어가지 않도록 GroupKFold를 썼다.

결과는 솔직히 약하다.

| feature set | mean logloss | mean AUC |
| --- | ---: | ---: |
| prior only | 0.677858 | 0.382414 |
| calendar rhythm linear | 0.678833 | 0.481425 |
| HS-JEPA state-only tree | 0.730555 | 0.503440 |
| raw + HS-JEPA state tree | 0.736790 | 0.493310 |
| HS-JEPA state-only linear | 0.769864 | 0.488754 |

해석:

HS-JEPA core를 `단독 label classifier`라고 주장하면 안 된다.
subject-holdout 상황에서는 label prior가 매우 강하고, raw/state feature를 직접 분류기에 넣으면 calibration이 쉽게 무너진다.

이건 실패가 아니라 구조를 정리해주는 negative evidence다.

```text
HS-JEPA core != direct label predictor
HS-JEPA core == hidden state geometry + action-health context
```

### 2. Nearest-Neighbor Target Consistency

좋은 human-state latent라면 latent space에서 가까운 row들이 target vector도 random neighbor보다 비슷해야 한다.

| representation | neighbor match | random match | lift |
| --- | ---: | ---: | ---: |
| calendar rhythm | 0.586159 | 0.528571 | +0.057587 |
| HS-JEPA state-only | 0.577333 | 0.526730 | +0.050603 |
| raw lifelog PCA8 | 0.575937 | 0.526032 | +0.049905 |

해석:

HS-JEPA state latent는 직접 logloss를 이기지는 못했지만, target vector가 놓인 local geometry는 random보다 분명히 더 잘 잡는다.

이 결과는 core를 `classifier`가 아니라 `state space`로 해석해야 한다는 주장을 강화한다.

### 3. Masked Context To Target View Prediction

I-JEPA식으로 한 생활 view를 가리고, 다른 view들로 가려진 view의 PCA representation을 예측했다.

| target view | component-corr lift vs null | 의미 |
| --- | ---: | --- |
| phone behavior | +0.380375 | 다른 생활 로그만 보고 phone behavior representation을 일부 예측 가능 |
| app/social context | +0.360004 | 사회/앱 사용 view가 다른 context와 연결됨 |
| mobility/environment | +0.335219 | 이동/환경 view도 context와 약하게 연결됨 |
| body/activity/sleep | +0.260881 | 몸/활동/sleep sensor view가 완전히 독립은 아님 |

주의:

R2는 음수인 view가 많다. 즉 raw value reconstruction으로는 좋지 않다.
하지만 component correlation은 null보다 살아난다.
이건 JEPA 관점과 맞는다.

```text
raw reconstruction은 어렵다.
representation-level relation은 살아 있다.
```

### 4. Human-State Outlier Target Shift

personal/cohort outlier 상위 25%와 하위 25%의 target prevalence를 비교했다.

큰 shift:

- peer outlier 기준 S4: +0.159292
- cohort outlier 기준 S4: +0.132743
- subject outlier 기준 Q3: +0.123894
- peer outlier 기준 S2: +0.115044
- peer outlier 기준 S1: -0.106195

해석:

outlier state는 단순 noise가 아니다. 특히 S-stage 계열에서 prevalence가 움직인다.
따라서 personal/cohort anomaly는 HS-JEPA의 target representation 후보로 유지할 가치가 있다.

## Adapter Replay Evidence

이 항목은 core-only 증명이 아니다.
하지만 public score 없이, 기존 action teacher가 고른 row support를 다른 teacher로 transfer할 수 있는지 보는 adapter diagnostic이다.

| train teacher | test teacher | feature set | row AUC | recall@k | z vs permuted |
| --- | --- | --- | ---: | ---: | ---: |
| stagebridge action | s2hub action | core-state geometry | 0.980392 | 0.823529 | 9.909321 |
| s2hub action | stagebridge action | core-state geometry | 0.928230 | 0.853659 | 8.136543 |

평균:

- row AUC: 0.954311
- recall@k: 0.838594
- permutation z: 8.375849

해석:

이건 가장 강한 결과다.
HS-JEPA core-state geometry는 label을 직접 맞히지는 못하지만, 어떤 row가 action support를 받을 가능성이 있는지는 매우 강하게 재발견한다.

즉 논문에서 강조할 핵심은 다음이다.

```text
Human-state representation is weak as a direct classifier,
but strong as a row-action support geometry.
```

## 논문 주장 수정

이 실험 이후 HS-JEPA의 paper thesis는 더 명확해진다.

기존의 약한 주장:

```text
HS-JEPA는 생활 로그에서 label을 더 잘 예측한다.
```

수정된 강한 주장:

```text
HS-JEPA learns a hidden human-state geometry from partial lifelog context.
This geometry does not replace the label predictor;
it makes listener responsibility and sparse action-health decisions recoverable.
```

한국어로는:

```text
HS-JEPA는 라벨을 직접 맞히는 새 classifier가 아니다.
HS-JEPA는 생활 로그를 숨은 인간 상태 공간으로 바꾸고,
그 공간에서 어떤 row-target action이 건강하게 release될 수 있는지 판단하게 하는 아키텍처다.
```

## 현재 한계

1. subject-holdout label logloss는 prior보다 나쁘다.
2. masked-view R2는 음수인 경우가 많다.
3. external action replay는 adapter teacher를 쓰므로 core-only proof가 아니다.
4. row-action support는 강하지만, action direction/amount까지 core만으로 안전하게 정하는 단계는 아니다.

## 다음 Big-Bet

다음 큰 실험은 `Core Geometry -> Anchor-Free Action Proposal`이다.

아이디어:

1. public score ledger 없이 core-state geometry에서 row support 후보를 만든다.
2. candidate row에 대해 target route를 직접 정하지 않고, listener responsibility가 가장 안정적인 target bundle만 선택한다.
3. release는 action-health invariant를 통과한 bundle만 허용한다.
4. 이 결과가 frontier 근처 row support를 재현하면, HS-JEPA core가 adapter anchor 없이도 row-state frontier 일부를 찾는다는 증거가 된다.

이 실험이 성공하면 논문 contribution은 더 강해진다.

```text
HS-JEPA core can propose action-support rows before leaderboard-conditioned decoding.
```
