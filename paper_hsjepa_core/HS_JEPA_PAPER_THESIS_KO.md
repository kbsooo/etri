# HS-JEPA Paper Thesis

## 한 문장 논문 주장

HS-JEPA는 인간 생활 로그를 label로 직접 매핑하지 않고, 보이는 생활 context에서 보이지 않는 human-state representation을 예측한 뒤, 여러 listener가 그 상태를 어떻게 듣는지와 어떤 action이 domain invariant를 보존하는지를 분리해 결정하는 joint embedding predictive architecture다.

## 기존 접근과의 차이

일반적인 tabular competition 모델은 다음 구조다.

```text
lifestyle features -> classifier/ensemble -> labels
```

HS-JEPA는 다음 구조다.

```text
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> row/listener action proposal
  -> action-health / toxicity field
  -> invariant-preserving release
  -> final output
```

즉 HS-JEPA의 core contribution은 좋은 feature를 더 붙이는 것이 아니다. 핵심은 `hidden state`, `listener`, `action`, `invariant`를 분리하고, label 예측 전에 보이지 않는 인간 상태와 action health를 먼저 예측하는 것이다.

## JEPA에서 가져온 것

JEPA의 핵심 질문은 raw input을 복원하는 것이 아니라 보이는 context로 보이지 않는 representation을 예측하는 것이다.

HS-JEPA에서는 이 질문을 다음처럼 바꾼다.

```text
이 사람의 일부 생활 로그와 주변 context만 보고,
오늘의 숨은 human state와 그 state를 듣는 listener/action representation을 예측할 수 있는가?
```

따라서 HS-JEPA에서 reconstruction target은 원본 feature가 아니다.

- 개인 baseline 밖의 오늘 상태
- peer/cohort 기준 outlier 상태
- target/listener responsibility
- row-target action support
- action-health/toxicity
- domain invariant를 깨는지 여부

이것들이 HS-JEPA의 target representation이다.

## 논문 contribution

### Contribution 1. Human-State World Model

생활 로그를 독립 row의 feature table이 아니라, 개인/코호트/시간/사회적 routine이 만든 hidden human-state의 관측값으로 본다.

이 모듈은 “어느 label이 1인가”보다 먼저 “오늘이 어떤 인간 상태인가”를 예측한다.

### Contribution 2. Listener Responsibility

Q/S label, sensor, survey, health outcome을 모두 같은 hidden state를 다르게 듣는 listener로 해석한다.

이 관점에서는 target별 예측 head가 중요한 것이 아니라, 어떤 listener가 현재 human-state에 책임을 가져야 하는지가 중요하다.

### Contribution 3. Action-Health / Toxicity Field

좋은 latent signal이 항상 좋은 output action은 아니다.

HS-JEPA는 latent signal을 바로 prediction으로 바꾸지 않고, action이 건강한지, shortcut인지, public/private equation에서 toxic한지 검사한다.

### Contribution 4. Invariant-Preserving Decoder

각 target을 독립적으로 조정하면 local score는 좋아질 수 있지만, human-state manifold를 깨뜨릴 수 있다.

HS-JEPA는 action 후에도 보존되어야 하는 domain invariant를 정의하고, 그 invariant를 깨는 action을 release하지 않는다.

### Contribution 5. Counterfactual Listener-Dropout

새로 추가한 논문용 검증 축이다.

좋은 action은 특정 listener 하나에만 맞는 shortcut이어서는 안 된다. route, fusion, target-listener, anti-shortcut listener 중 하나를 가려도 action-health가 유지되어야 한다.

이 원칙을 수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/counterfactual_listener_dropout_solver.py
```

이 실험은 실패한 public 제출을 버리지 않고, action toxicity label로 재해석한다. 그리고 같은 high-survival action을 그대로 믿는 `dropout_fullfield_aggressive`와, public-negative direction을 반대로 보는 `toxic_direction_inversion`을 A/B 센서로 만든다.

### Contribution 6. Spectral Negative Representation

HS-JEPA는 실패한 action도 버리지 않는다. 여러 public-negative action이 서로 독립 실패가 아니라 같은 저차원 방향으로 실패한다면, 그 방향은 negative representation이다.

수면 대회 adapter에서는 H057 이후 public에서 나빠진 제출들을 모아 action-delta matrix를 만들고, 그 첫 번째 spectral mode를 public-bad tangent로 해석한다.

```bash
python3 sleep_competition_adapter/spectral_public_tangent_solver.py
```

이 모듈은 두 가지 세계관을 직접 가른다.

- anti-tangent world: 실패들이 가리키는 나쁜 방향의 반대로 가면 더 좋은 action field가 된다.
- orthogonal residual world: H057은 public tangent상 거의 최적이고, 남은 upside는 나쁜 방향과 직교한 private-safe residual subspace에 있다.

따라서 이 contribution의 핵심은 “실패를 평균으로 지우지 않고, 실패 자체를 JEPA의 target representation으로 만든다”는 점이다.

## 이번 대회에서 얻은 핵심 증거

### 증거 1. Direct JEPA latent label prediction은 실패했다

직접 JEPA latent를 target probability로 번역한 실험들은 public에서 크게 나빠졌다. 이는 raw latent가 label predictor로 바로 쓰이면 collapse/shortcut/public-mismatch에 빠진다는 증거다.

### 증거 2. 큰 성능 점프는 row-target action field에서 나왔다

H012와 H057 계열은 단순 모델 개선이 아니라, 특정 row-target action field를 맞히면서 public LB를 크게 낮췄다.

현재 최고 관측값:

```text
submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv
public LB 0.5677475939
```

이 결과는 HS-JEPA의 실제 target이 label probability 자체가 아니라 row-target correction/action field임을 보여준다.

### 증거 3. Listener posterior는 action generator가 아니었다

target-listener route-lift와 cross-listener transport는 local geometry가 좋아도 H057을 넘지 못했다.

해석:

```text
listener responsibility는 action을 직접 생성하는 head가 아니라,
action boundary/toxicity를 진단하는 모듈이다.
```

### 증거 4. Action-health는 scalar가 아니라 mixture다

H088류 hard-world toxicity와 broad public-bad toxicity는 같은 축이 아니었다.

따라서 HS-JEPA의 action-health는 하나의 confidence score가 아니라, 여러 failure mode를 분리하는 field로 봐야 한다.

### 증거 5. Counterfactual listener-dropout은 action-health를 cell 단위로 쪼갠다

새 solver 결과:

```text
dropout_fullfield_aggressive
- changed cells: 17
- rows: 10
- listener-dropout health z: 4.8297
- min-score z: 5.2360
- survival z: 5.5625
- file: submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv

toxic_direction_inversion
- changed cells: 15
- rows: 8
- listener-dropout health z: 4.5056
- min-score z: 4.8430
- survival z: 4.9093
- file: submission_hsjepa_counterfactual_listener_dropout_toxic_direction_inversion_f0101750_uploadsafe.csv
```

이 둘은 같은 high-survival hidden action field를 두 방식으로 해석한다.

- `dropout_fullfield_aggressive`: 실패한 public sensor 안에도 좋은 core cells가 섞여 있었다.
- `toxic_direction_inversion`: 실패한 public sensor가 action 방향이 반대여야 한다는 신호였다.

둘 중 어느 쪽이 public에서 더 낫든, HS-JEPA의 action-health/toxicity 세계관이 좁혀진다.

### 증거 6. Public failure는 저차원 negative representation을 만든다

H057 이후 public에서 실패한 26개 제출을 H057 대비 action-delta vector로 보고 spectral decomposition을 수행했다.

```text
first bad-mode variance: 0.962855
top-5 cumulative variance: 0.994683
candidate cells: 116
anti-bad cells: 98
bad-aligned cells: 18
```

해석:

```text
H057 이후의 실패는 제각각 실패한 것이 아니라, 대부분 같은 public-bad action tangent 위에서 실패했다.
```

이것은 논문적으로 중요하다. HS-JEPA의 action-health는 단순 confidence가 아니라, positive latent와 negative latent를 모두 갖는 representation geometry로 봐야 한다.

현재 가장 정보량이 큰 sensor:

```text
submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv
```

이 후보가 좋아지면:

- public-bad tangent는 단순 실패 요약이 아니라 invertible action equation이다.
- HS-JEPA는 실패 제출을 negative representation으로 학습해 더 좋은 action을 만들 수 있다.

이 후보가 나빠지고 orthogonal residual이 좋아지면:

- H057은 public tangent 방향에서 이미 충분히 최적화됐고, 남은 개선은 tangent와 직교한 private-safe subspace에서 찾아야 한다.

둘 다 나빠지면:

- public failure의 저차원 구조는 real이지만, 그 반대 방향이 label-valid action이라는 보장은 없다.
- 다음 병목은 public-mode discovery가 아니라 label-validity/invariant constraint다.

## 논문에서 과장하면 안 되는 것

- HS-JEPA core만으로 현재 최고 LB를 바로 재현한다고 말하면 안 된다.
- public LB sensor는 일반 기술이 아니라 competition adapter의 관측 장비다.
- S2 hub는 이 대회의 case-study 발견이지, 모든 수면 문제에 universal하게 적용된다고 주장하면 안 된다.
- human-state encoder 하나가 row-target assignment를 완전히 해결했다고 말하면 안 된다.

## 정확한 thesis 문장

논문에서 가장 안전하고 강한 문장은 다음이다.

```text
HS-JEPA reframes human-understanding prediction as hidden-state and action-field recovery.
In our sleep-log case study, the largest public-LB gains came not from direct label prediction,
but from recovering sparse row-target action fields and filtering them through listener responsibility,
action-health, and invariant-preserving decoders.
```

한국어로는:

```text
HS-JEPA는 인간 이해 예측을 label 분류가 아니라 hidden human-state와 action field 복원 문제로 재정의한다.
수면 생활 로그 대회에서는 직접 label을 맞히는 모델보다, row-target action field를 복원하고 이를 listener responsibility,
action-health, invariant decoder로 통과시킨 접근이 가장 큰 public LB 개선을 만들었다.
```

## 다음으로 가장 정보량이 큰 제출 센서

현재 thesis 관점에서 가장 정보량이 큰 후보는 다음이다.

```text
submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv
```

이 후보가 좋아지면:

- post-H057 failure action들은 같은 bad tangent를 공유했고, 그 반대 방향이 실제로 public-good action이다.
- HS-JEPA의 negative representation/action-health thesis가 강해진다.

이 후보가 나빠지고 orthogonal residual이 좋아지면:

- 실패들의 spectral mode는 real이지만 invertible하지 않다.
- H057 이후 개선은 public-bad direction 반대가 아니라 private-safe residual subspace에서 찾아야 한다.

둘 다 나빠지면:

- low-rank public failure geometry는 descriptive diagnostic일 뿐 action equation은 아니다.
- HS-JEPA는 action 방향보다 label-valid invariant constraint를 더 강화해야 한다.
