# HS-JEPA JEPA Contract

## 한 줄 요약

HS-JEPA는 수면/생활 로그의 label을 바로 맞히는 모델이 아니라, 보이는 인간 생활 context에서 보이지 않는 human-state target representation을 예측하고, 그 representation이 안전한 row-target action으로 번역되는지 검증하는 아키텍처다.

## 왜 일반 JEPA와 다른가

일반적인 I-JEPA식 질문은 다음이다.

```text
부분 context만 보고 보이지 않는 target representation을 예측할 수 있는가?
```

HS-JEPA에서는 이 질문을 인간 생활 로그에 맞게 바꾼다.

```text
오늘의 관측 가능한 생활 context만 보고,
보이지 않는 인간 상태와 그 상태에서 유효한 action representation을 예측할 수 있는가?
```

여기서 action은 대회용 trick이 아니라, hidden state가 label space로 표현되는 방식이다.

## HS-JEPA의 Core Contract

```text
visible human context
  -> human-state context embedding
  -> hidden target representation prediction
  -> listener/action responsibility
  -> action-health energy
  -> invariant-preserving sparse decoder
  -> anti-shortcut validation
```

각 구성요소의 역할은 다음과 같다.

| Component | 역할 |
| --- | --- |
| context encoder | lifelog, row order, subject/cohort state, target route를 human-state embedding으로 바꾼다 |
| target representation | raw label이 아니라 hidden episode, listener route, action prototype, correction field를 표현한다 |
| predictor | 현재 context로 보이지 않는 target representation을 예측한다 |
| energy decoder | 예측된 representation이 어떤 row-target action을 허용하는지 판단한다 |
| invariant decoder | Q/S 구조, target route, subject shift에서 무너지지 않는 action만 release한다 |
| LeJEPA-style health check | collapse, shortcut, subject-specific artifact, public-only luck을 검사한다 |

## 이번 두 실험의 위치

### Subject-Invariant Episode Controller

이 실험은 HS-JEPA predictor 자체가 아니라 LeJEPA-style health check다.

```text
row episode representation
  -> action-space controller
  -> subject-heldout stress
```

결과는 negative evidence다.

- full OOF에서는 episode action-space controller가 강했다.
- 하지만 subject-LOO에서는 raw와 동률로 수렴했다.
- 안전한 selector는 held-out subject에서 action을 거의 하지 않았다.

의미:

```text
row episode state에는 신호가 있지만,
그대로 release policy로 쓰면 subject-specific action tail에 묶일 수 있다.
```

### Cross-Subject Episode Prototype Transport

이 실험은 HS-JEPA predictor의 non-parametric prototype 구현이다.

```text
current row-target-route context
  -> joint embedding
  -> retrieve/predict peer subject's successful hidden action representation
  -> release action if transport energy is healthy
```

여기서 kNN은 핵심 contribution이 아니다.

```text
kNN = JEPA predictor를 구현한 임시 non-parametric readout
```

핵심 contribution은 target을 label로 보지 않고, 성공한 hidden action representation으로 정의했다는 점이다.

## 왜 label prediction이 아닌가

단순 분류 모델은 다음을 한다.

```text
x -> Q1/Q2/Q3/S1/S2/S3/S4 probability
```

HS-JEPA는 중간에 더 큰 질문을 둔다.

```text
x -> hidden human state
hidden human state -> which listener/action representation is valid?
valid action representation -> calibrated sparse label correction
```

이 구조가 필요한 이유는 현재 실험들이 반복해서 보여준 병목 때문이다.

- core state만으로 label을 직접 예측하면 약하다.
- 하지만 core state는 action support와 failure boundary를 잘 설명한다.
- action을 바로 release하면 subject/public shortcut이 생긴다.
- subject-invariant health check와 cross-subject transport를 거치면 더 일반적인 action geometry가 나온다.

## 논문에서 주장할 수 있는 형태

강한 주장은 다음이다.

```text
HS-JEPA represents human lifestyle logs as latent state-action geometry.
Instead of predicting labels directly, it predicts hidden target representations:
which listener/action routes become valid under a latent human-state episode.
This representation supports cross-subject prototype transport and reduces
toxic row-target corrections under subject-shift stress.
```

한국어 표현:

```text
HS-JEPA는 생활 로그를 단순 feature table로 보지 않고,
숨은 인간 생활 상태와 그 상태에서 유효한 action representation을 복원한다.
label은 최종 출력일 뿐이며, 핵심 target은 row-target correction을 가능하게 하는
숨은 action geometry다.
```

## 아직 부족한 점

현재 구현은 완전한 neural JEPA가 아니다.

- target representation predictor는 아직 kNN/prototype readout이다.
- representation loss는 explicit contrastive/energy objective라기보다 OOF action gain으로 관측된다.
- cross-subject transport는 positive지만 public/private invariant까지 완전히 증명하지는 않았다.

따라서 현재 정확한 표현은 다음이다.

```text
HS-JEPA core idea with a non-parametric target-representation predictor
and competition-specific sparse action decoder.
```

다음 단계는 이 prototype predictor를 명시적인 JEPA loss로 바꾸는 것이다.

```text
context embedding -> predict action-prototype embedding
loss = target representation prediction error
     + action-health energy
     + subject-invariant regularization
```
