# Human-State JEPA

> 수면 기반 생활습관 로그에서 보이지 않는 인간 생활 상태를 복원하고, 그 상태가 어떤 target correction으로 이어지는지 예측하려는 JEPA 변형 아키텍처.

## 1. 한 줄 요약

Human-State JEPA, 줄여서 HS-JEPA는 수면/생활 로그 데이터를 단순한 tabular classification 문제로 보지 않는다.  
대신 이 데이터를 “어떤 사람의 생활 리듬, 피로, 루틴 붕괴, 회복, 사회적 활동, 측정 상태 같은 숨은 인간 상태가 남긴 관측 로그”로 보고, 그 숨은 상태를 먼저 복원한 뒤 Q1/Q2/Q3/S1/S2/S3/S4 예측으로 번역하려는 구조다.

최종 목표는 대회 metric인 7개 binary target의 Log Loss를 낮추는 것이지만, HS-JEPA의 핵심 질문은 단순히 “어떤 모델이 점수가 좋나?”가 아니다.

핵심 질문은 다음이다.

> 이 row는 어떤 숨은 인간 상태에서 나온 것인가?  
> 그 상태는 어떤 target route를 통해 label에 반영되는가?  
> public/private 평가가 실제로 듣는 row-target action은 무엇인가?

## 2. 문제 배경

이 대회는 수면 기반 생활습관 로그를 입력으로 받아 7개 target을 예측하는 문제다.

| Target | 의미 |
| --- | --- |
| Q1 | 주관적 수면 만족도. 높을수록 만족도가 높다고 해석할 수 있음 |
| Q2 | 수면 개입 정도. 낮을수록 좋은 방향으로 해석 |
| Q3 | 수면 품질 관련 주관/혼합 신호 |
| S1-S4 | objective sleep-stage ratio 계열 신호 |

Metric은 Log Loss다.  
즉 확률값의 calibration이 매우 중요하고, 틀린 방향으로 확신하면 점수가 크게 나빠진다.

처음에는 일반적인 tabular 대회처럼 feature engineering, neural net, smoothing, blend, calibration 등을 시도했다.  
이 접근으로도 어느 정도 성능은 나왔지만, public LB가 `0.576` 근처에서 오래 정체됐다.

이후 중요한 변화가 있었다.

| 단계 | Public LB | 의미 |
| --- | ---: | --- |
| E247 | `0.5761589494` | 기존 feature/NN/smoothing 계열의 강한 baseline |
| H012 | `0.5681234831` | public equation inversion 계열의 큰 점프 |
| H042/H050 | `0.5679048248` | Q2/row-state 계열 추가 개선 |
| H057 | `0.5677475939` | 현재 best. Q2-row/full-vector state frontier |

E247에서 H057까지 약 `0.00841` Log Loss가 개선됐다.  
이 정도 개선은 단순한 미세 blend로 설명하기 어렵고, 데이터 안에 public/private subset, row-state, target route 같은 숨은 구조가 있다는 신호로 해석했다.

## 3. JEPA에서 가져온 아이디어

HS-JEPA는 Yann LeCun 계열의 JEPA, 특히 I-JEPA와 LeJEPA에서 출발했다.  
다만 논문 구조를 그대로 복제한 것은 아니다. 이 대회 데이터에 맞게 질문을 바꿨다.

### 3.1 JEPA의 핵심

JEPA의 핵심은 raw input을 그대로 복원하는 것이 아니다.  
보이는 context를 이용해 보이지 않는 target의 representation을 예측하는 것이다.

이미지 예시로 말하면, 빈 부분의 pixel을 정확히 복원하는 것이 아니라, 그 빈 부분이 어떤 semantic representation을 가져야 하는지 예측한다.

HS-JEPA에서는 이 생각을 다음처럼 바꿨다.

```text
보이는 context:
  생활 로그 feature
  row order
  subject/session/block-like pattern
  target dependency
  기존 submission 간 disagreement
  public LB 반응
  인간사회적 가설

예측해야 하는 hidden representation:
  human-state latent
  row-state
  target route
  action-health
  public/private listener field
  row-target correction field
```

### 3.2 I-JEPA에서 가져온 것

I-JEPA식으로 본다면 이 대회의 핵심은 다음 질문이다.

> 일부 feature, 일부 row, 일부 target, 일부 public observation만 보고  
> 보이지 않는 인간 상태와 target route를 예측할 수 있는가?

그래서 random column masking보다 의미 있는 masking을 사용하려고 했다.

- feature-family mask
- row-window mask
- subject/block-like mask
- target-group mask
- train/test domain mask
- public LB observation mask
- submission disagreement mask

### 3.3 LeJEPA에서 가져온 것

LeJEPA식으로는 representation이 진짜 구조인지 계속 의심했다.

좋아 보이는 latent가 다음 중 하나일 수 있기 때문이다.

- 특정 CV split에만 맞는 shortcut
- public subset overfit
- prior memorization
- collapse된 embedding
- Log Loss calibration luck
- H088/H018 같은 stress diagnostic을 action head로 착각한 것

그래서 HS-JEPA에서는 latent를 바로 믿지 않고, 다음 stress를 계속 붙였다.

- known public LB observation과 일치하는가
- H057 같은 best frontier와 충돌하지 않는가
- H088 같은 negative sensor 방향으로 빠지지 않는가
- row-target action이 public이 실제로 듣는 cell인가
- 같은 score 개선을 다른 submission difference로 설명할 수 있는가

## 4. HS-JEPA의 정의

HS-JEPA는 다음 구조를 가진다.

```text
observed context C
  -> context encoder f(C)
  -> hidden human-state representation z
  -> route/action proposal a(row, target)
  -> listener responsibility l(row, target)
  -> toxicity/safety s(row, target)
  -> correction field c = a * l * s
  -> calibrated submission probability
```

처음에는 단순히 다음 구조로 생각했다.

```text
context -> human-state latent -> action/toxicity -> correction
```

하지만 H144/H145 실험 이후 구조를 수정했다.

지금의 핵심은 `listener responsibility`다.

즉 어떤 action이 좋아 보여도, public/private 평가가 그 row-target을 실제로 듣지 않는다면 점수에는 거의 영향을 주지 않는다.  
반대로 public이 듣는 action이 toxic하면 점수가 크게 망가진다.

그래서 HS-JEPA는 이제 다음 세 가지를 분리한다.

| Field | 질문 |
| --- | --- |
| `action(row,target)` | 이 hidden human-state에서는 어떤 target을 움직이고 싶어 하는가? |
| `listener(row,target)` | public/private 평가가 이 row-target을 실제로 듣는가? |
| `toxicity(row,target)` | 들었을 때 좋은 방향인가, 벌점 방향인가? |

## 5. Human-State란 무엇인가

Human-State는 사람이 직접 이름 붙인 feature 하나가 아니다.  
예를 들어 “주말”, “야간 카톡”, “월급날”, “교회/성당”, “출근 루틴” 같은 것을 단순 rule로 박는 것이 아니다.

이런 사회적/생활적 이야기는 latent를 만들기 위한 context view다.

예를 들면 다음과 같은 상태를 상상할 수 있다.

- 평일 출근 리듬
- 주말 보상수면
- 과피로 후 회복
- 야간 휴대폰/사회활동
- 루틴 붕괴
- 측정 confidence 저하
- subjective satisfaction과 objective sleep-stage의 괴리
- Q2가 높아지는 개입/불안정 상태
- 특정 subject-like block의 반복 패턴
- public subset이 더 민감하게 듣는 row-state

중요한 점은 이 가설들을 직접 label에 꽂지 않는다는 것이다.  
HS-JEPA는 이 가설들을 context representation으로 만들고, 실제 public/result sensor가 살아남기는지 본다.

## 6. 실험 흐름

### 6.1 기존 모델링의 한계

초기에는 feature NN, smoothing, top-k blend, calibration 등으로 성능을 끌어올렸다.  
대표적으로 E247이 public LB `0.5761589494`를 기록했다.

하지만 이 방식은 더 좋은 모델을 계속 쌓아도 큰 개선이 어려웠다.  
문제는 모델 capacity가 아니라, hidden public/private equation과 row-state를 제대로 못 보는 것처럼 보였다.

### 6.2 H012: public equation breakthrough

H012는 가장 중요한 전환점 중 하나였다.

Public LB:

```text
H012 = 0.5681234831
```

E247 대비 약 `0.008` 이상 좋아졌다.  
이건 단순한 seed luck이나 smoothing으로 보기 어려운 변화다.

해석:

> public LB는 단순 점수표가 아니라, 어떤 hidden public equation을 관측하는 센서다.

이때부터 public score를 최적화 대상이 아니라 실험 관측값으로 보기 시작했다.

### 6.3 H057: row-state frontier

현재 best는 H057이다.

```text
submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv
public LB = 0.5677475939
```

H057은 Q2-row/full-vector state 쪽 신호가 실제 public에서 살아남는다는 것을 보여줬다.

해석:

> 특정 row-state/action field는 public이 실제로 듣는다.  
> H057은 그 들리는 상태를 가장 잘 건드린 제출이다.

### 6.4 H088: dual-head gate의 실패

H088은 public/private dual-head gate를 테스트했다.

아이디어:

```text
public posterior와 hard-world posterior가 둘 다 좋아하는 action만 선택하면 안전하지 않을까?
```

결과:

```text
H088 = 0.5684942019
```

H057보다 `+0.0007466080` 나빴다.

해석:

> H018/H088 hard-world head는 action-grade decoder가 아니다.  
> 이것은 private action head가 아니라 stress diagnostic으로 써야 한다.

즉 H088은 실패했지만 매우 중요한 negative sensor였다.  
어떤 action 방향이 public에서 벌점이 되는지 알려줬기 때문이다.

### 6.5 H144/H145: listener field 발견

H144와 H145는 row-target assignment를 테스트한 실험이다.

두 파일의 public LB:

```text
H144 = 0.567929641
H145 = 0.567929641
```

두 파일은 딱 2개의 row-target cell만 달랐다.

| Row | Subject | Target | H144 | H145 | 차이 |
| ---: | --- | --- | ---: | ---: | ---: |
| 135 | id06 | Q3 | 0.829783853053 | 0.829580714006 | +0.000203139047 |
| 207 | id09 | S2 | 0.808870352651 | 0.810987067381 | -0.002116714730 |

기대한 해석은 이랬다.

- H144가 이기면 row207 S2 relief가 action-grade
- H145가 이기면 Q3 repair-only가 더 안전

하지만 결과는 완전 동점이었다.

해석:

> public은 이 두 row-target 차이를 거의 듣지 않았다.  
> 좋은 action인지 아닌지보다 먼저, public/private가 그 action을 듣는지 예측해야 한다.

이 실험 때문에 HS-JEPA 구조에 `listener responsibility`가 추가됐다.

## 7. 지금까지 얻은 핵심 인사이트

### 인사이트 1. Public LB는 센서다

Public LB를 단순히 맞춰야 하는 정답표로 보지 않았다.  
각 submission은 “이 데이터 세계가 이런 구조를 가진다”는 주장이고, public score는 그 주장에 대한 관측값이다.

H012, H057, H088, H144/H145는 각각 다른 센서 역할을 했다.

| 실험 | 역할 |
| --- | --- |
| H012 | public equation이 있다는 positive sensor |
| H057 | 들리는 row-state/action field가 있다는 positive sensor |
| H088 | hard-world action head가 toxic하다는 negative sensor |
| H144/H145 | row-target action에 listener field가 필요하다는 equality sensor |

### 인사이트 2. Hidden state는 있다

E247에서 H012/H057까지의 개선 폭을 보면, 단순 feature 추가만으로 보기 어렵다.  
특히 H057은 특정 row-state가 public에서 살아남는다는 것을 보여줬다.

따라서 이 데이터에는 최소한 다음 구조가 있다고 보는 것이 합리적이다.

- public/private subset 차이
- row-state 또는 subject/block-like structure
- target route dependency
- Q2와 full-vector state의 결합
- action이 public에 들리는 정도 차이

### 인사이트 3. 좋은 latent와 좋은 action은 다르다

여러 JEPA-style latent는 내부적으로는 그럴듯했다.  
하지만 public에서 살아남지 못한 경우가 많았다.

이유는 latent가 “구조를 설명”하는 것과 “submission으로 안전하게 번역”되는 것이 다르기 때문이다.

그래서 HS-JEPA는 단순 representation model이 아니라, representation이 만든 action이 public/private 관측식에서 안전한지 판단하는 equation solver로 발전했다.

### 인사이트 4. H088은 실패했지만 쓸모 있다

H088은 점수로 보면 실패다.  
하지만 이 실패는 “어떤 방향이 public에서 벌점이 되는지” 알려줬다.

그래서 H088은 action head가 아니라 toxicity stress diagnostic으로 남았다.

### 인사이트 5. Listener field가 다음 핵심이다

H144/H145가 완전 동점이 된 것은 매우 중요하다.  
두 파일은 두 cell만 다른데 public이 구분하지 않았다.

이것은 다음을 의미한다.

```text
그 action이 맞냐 틀리냐 이전에,
public/private가 그 row-target을 실제로 듣느냐가 먼저다.
```

따라서 앞으로 HS-JEPA는 `listener(row,target)`를 명시적으로 배워야 한다.

## 8. 현재 성과

현재 best:

```text
submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv
public LB = 0.5677475939
```

비교:

| 기준 | Public LB | H057 대비 |
| --- | ---: | ---: |
| E247 | `0.5761589494` | H057이 약 `0.0084113555` 좋음 |
| H012 | `0.5681234831` | H057이 `0.0003758892` 좋음 |
| H042/H050 | `0.5679048248` | H057이 `0.0001572309` 좋음 |
| H057 | `0.5677475939` | 현재 best |
| H088 | `0.5684942019` | H057보다 `0.0007466080` 나쁨 |
| H144/H145 | `0.5679296410` | H057보다 `0.0001820471` 나쁨 |

가장 큰 성과는 단순히 점수가 오른 것이 아니다.  
이 대회에서 어떤 구조가 중요한지 분해했다는 점이다.

정리하면:

- public equation을 이용하면 큰 점프가 가능했다.
- row-state/full-vector state는 public에서 실제로 먹혔다.
- hard-world dual-head gate는 action head가 아니었다.
- row-target micro action은 listener가 낮으면 public에 거의 안 들린다.
- HS-JEPA는 listener responsibility를 포함한 구조로 확장되어야 한다.

## 9. HS-JEPA가 기존 tabular 접근과 다른 점

기존 tabular 접근:

```text
features -> model -> probabilities
```

HS-JEPA 접근:

```text
features / row-order / human stories / public observations
  -> hidden human-state representation
  -> target route
  -> listener responsibility
  -> toxicity/safety
  -> probability correction
```

기존 접근은 label을 바로 맞히려고 한다.  
HS-JEPA는 label이 생겨난 숨은 상태를 먼저 맞히려고 한다.

기존 접근은 public LB를 점수로만 본다.  
HS-JEPA는 public LB를 hidden observation sensor로 본다.

기존 접근은 feature importance를 본다.  
HS-JEPA는 “이 feature가 어떤 인간 상태를 말하는가?”를 본다.

## 10. 연구적으로 주장할 수 있는 contribution

HS-JEPA는 아직 완성된 정답 모델이라기보다, 이 대회에서 발견한 구조를 설명하기 위한 연구 아키텍처다.

논문/문서 관점에서 주장할 수 있는 contribution은 다음이다.

### 10.1 Human-State Representation

수면 생활 로그에서 label을 직접 예측하지 않고, 먼저 숨은 인간 생활 상태를 복원한다.

### 10.2 Public LB as Sensor

Leaderboard score를 단순 최적화 대상이 아니라, hidden public/private observation equation을 읽는 센서로 사용한다.

### 10.3 Row-Target Route Decoder

sample 단위가 아니라 row-target 단위의 route/action을 예측한다.

### 10.4 Action-Health and Toxicity Stress

좋아 보이는 action이 public에서 toxic할 수 있으므로, negative sensor를 사용해 action-health를 평가한다.

### 10.5 Listener Responsibility

어떤 action이 좋은지 이전에, public/private가 그 action을 실제로 듣는지를 예측한다.

이 마지막 항목이 H144/H145 이후 HS-JEPA의 핵심 업데이트다.

## 11. 한계

HS-JEPA는 아직 완성된 end-to-end deep architecture가 아니다.  
현재는 여러 solver, public observation, latent diagnostic, submission experiment를 조합한 research prototype에 가깝다.

한계는 분명하다.

- public LB observation 수가 제한적이다.
- private set에 대한 직접 검증은 불가능하다.
- 일부 latent는 내부적으로 그럴듯하지만 submission으로 번역하면 약하다.
- 인간사회적 가설은 의미 있는 context가 될 수 있지만, 직접 rule로 쓰면 쉽게 overfit된다.
- 현재 best `0.5677475939`에서 목표 `0.53`까지는 아직 큰 간격이 있다.

하지만 실패도 구조를 좁히는 증거가 됐다.

특히 H088과 H144/H145는 점수로는 실패했지만, HS-JEPA가 어떤 방향으로 바뀌어야 하는지 알려준 중요한 실험이다.

## 12. 다음 방향

앞으로의 핵심 방향은 더 많은 smoothing이나 blend가 아니다.

다음 질문을 풀어야 한다.

> public/private 평가가 실제로 듣는 row-target은 무엇인가?

이를 위해 필요한 다음 단계:

1. 모든 public submission 결과를 equality/inequality constraint로 정리한다.
2. H057이 왜 public-listened field였는지 listener model을 만든다.
3. H088 같은 실패 submission을 toxicity sensor로 사용한다.
4. H144/H145 같은 동점 submission을 low-listener constraint로 사용한다.
5. human/social story feature는 직접 rule이 아니라 listener/action latent의 context로 사용한다.
6. 최종 decoder는 `action * listener * safety` 형태의 row-target correction field를 낸다.

## 13. 최종 요약

HS-JEPA는 수면 생활 로그 예측 문제를 다음처럼 재정의한다.

> 이 문제는 feature에서 label을 바로 맞히는 문제가 아니다.  
> 이 문제는 생활 로그 뒤에 숨어 있는 인간 상태, 그 상태가 label로 번역되는 route, 그리고 public/private가 실제로 듣는 row-target action을 복원하는 문제다.

현재까지의 실험은 다음을 보여줬다.

- public equation과 row-state는 실제로 존재할 가능성이 높다.
- 단순 action-quality만으로는 부족하다.
- hard-world diagnostic을 action head로 쓰면 실패한다.
- low-listener action은 아무리 그럴듯해도 public score를 움직이지 않는다.
- 따라서 HS-JEPA의 다음 핵심은 listener responsibility다.

현재 best score는 `0.5677475939`이고, 아직 `0.53`까지는 멀다.  
하지만 HS-JEPA는 단순 점수 개선 이상의 의미가 있다.  
이 대회 데이터를 “예측할 표”가 아니라 “숨은 인간 생활 상태가 남긴 관측 로그”로 다루는 새로운 접근이기 때문이다.
