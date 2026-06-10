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

### Contribution 7. Invariant-Projected Negative Action

Spectral negative representation만으로는 충분하지 않다.

실패 방향의 반대로 움직이는 것은 여전히 public-LB sensor에 대한 반응일 뿐이고, 그 action이 human-state manifold 위에서 말이 되는지는 별도로 검증해야 한다.

HS-JEPA는 따라서 negative representation을 바로 output으로 쓰지 않고, target-route invariant와 subject-prior invariant를 보존하는 feasible action으로 투영한다.

수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/negative_tangent_invariant_projection_solver.py
```

이 모듈은 H057 이후 public-bad tangent를 읽은 뒤, train label covariance와 subject별 label prior를 이용해 각 row-target action의 invariant energy 변화를 계산한다.

그리고 다음 조건을 동시에 만족하는 action만 release한다.

- public-bad tangent와 반대 방향이다.
- target-route energy를 크게 악화시키지 않는다.
- subject-prior coordinate에서 비정상적인 방향으로 튀지 않는다.

따라서 이 contribution의 핵심은 다음이다.

```text
negative representation is diagnostic;
invariant projection makes it action-grade.
```

### Contribution 8. LB-Conditioned Listener Responsibility

HS-JEPA는 listener responsibility를 target label head에서만 배우지 않는다.

대회 환경에서는 public LB 자체가 하나의 외부 listener처럼 작동한다. 이 listener는 row-target별 정답을 알려주지 않고, 제출 전체에 대한 scalar loss만 흘린다. HS-JEPA는 이 scalar 관측값들을 여러 action field와 함께 모아, 어느 row-target action이 public loss에 책임을 가졌는지 역추정할 수 있다.

수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/lb_conditioned_responsibility_solver.py
```

이 모듈은 기존 public 제출들의 action-delta와 public loss delta를 이용해 ridge/LOO responsibility equation을 맞춘 뒤, loss를 악화시킨 row-target 방향을 반대로 release한다.

핵심은 다음이다.

```text
external scalar outcomes can become listener responsibility signals;
responsibility is inferred before action release.
```

이 contribution은 spectral negative representation과 일부 충돌한다. 추천 후보는 predicted public-listener improvement와 route energy에서는 강하지만, spectral bad tangent와 완전히 반대 방향은 아니다. 따라서 이 후보는 다음 두 세계관을 가른다.

- spectral world: 실패들이 만든 bad tangent의 반대 방향이 action-grade다.
- scalar-listener world: public scalar 관측식에서 추정한 row-target responsibility가 더 직접적인 action equation이다.

### Contribution 9. Latent Listener Mixture Routing

LB-conditioned responsibility는 public LB를 하나의 scalar listener로 본다.
하지만 인간 이해 문제에서 하나의 관측자는 실제로 여러 listener의 합성일 수 있다.

예를 들어 주관적 Q label과 objective S label은 같은 human-state를 보더라도 서로 다른 방식으로 반응할 수 있다.
또 public subset과 private subset, subjective route와 sensor route도 같은 action field를 다르게 평가할 수 있다.

따라서 HS-JEPA의 다음 확장은 다음과 같다.

```text
one scalar listener
  -> latent listener mixture
  -> target-specific listener routing
```

수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/mixture_listener_responsibility_solver.py
```

이 모듈은 public 제출 action-delta를 spectral listener head로 분해한 뒤, row-target action을 세 가지 방식으로 release한다.

- listener consensus: scalar, dominant public mode, residual mode가 같은 방향을 말할 때만 release
- listener conflict: dominant public mode와 residual mode가 충돌하는 곳을 rescue
- Q/S target split: Q target은 residual listener, S target은 scalar/public consensus를 따르게 route

핵심은 다음이다.

```text
human-state action should be decoded through latent listener mixtures,
not through one monolithic public response gradient.
```

### Contribution 10. External Listener Subset Tomography

Mixture listener routing은 public response가 여러 listener의 합성일 수 있음을 보여준다.
하지만 scalar public feedback에는 더 근본적인 불완전성이 있다.

public LB는 모든 test row-target을 균일하게 말하지 않는다. 어떤 row-target은 public listener에 포함되어 강하게 말하고, 어떤 row-target은 private 또는 unobserved listener 쪽에 가까워 public scalar에는 거의 보이지 않을 수 있다.

따라서 HS-JEPA의 다음 확장은 다음이다.

```text
scalar external feedback
  -> public subset inclusion
  -> hidden label direction
  -> private-safety / toxicity filter
  -> row-target action release
```

수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/public_private_subset_tomography_solver.py
```

이 모듈은 LB-conditioned responsibility cell을 다시 분해한다.

- inclusion score: 이 row-target이 public listener에 포함되어 말해졌을 가능성
- label direction confidence: scalar feedback이 암시하는 hidden label 방향의 신뢰도
- private-safety score: public listener 밖에서도 보존될 가능성
- toxicity score: 실패한 public/action-health 축과 공선적인 위험도

핵심은 다음이다.

```text
external scalar feedback is not only a gradient;
it is a partially observed listener equation.
```

이 contribution은 HS-JEPA를 단순한 latent predictor에서 한 단계 더 밀어붙인다.
즉 representation을 예측하는 것에서 끝나지 않고, “누가 그 representation을 듣고 있었는가”와 “그 listener가 보지 못한 공간에서도 action이 건강한가”를 동시에 추정한다.

### Contribution 11. Anti-Listener Action-Health Equation

External listener tomography가 맞더라도, listener responsibility를 바로 action generator로 쓰면 실패할 수 있다.
실제로 target-listener route-lift, cross-listener transport, hard-world gate류는 local geometry가 그럴듯해도 public에서 H057을 넘지 못했다.

HS-JEPA는 이 실패를 버리지 않는다.
실패한 listener-derived action을 negative target representation으로 보고, 다음 질문으로 바꾼다.

```text
이 listener가 말한 방향이 action으로는 toxic했다면,
그 실패 방향을 반대로 보거나 veto할 때 private-safe action field가 생기는가?
```

수면 대회 adapter에서는 다음 실험으로 구현했다.

```bash
python3 sleep_competition_adapter/anti_listener_toxicity_equation_solver.py
```

이 모듈은 CrossListener, target-listener lift, H088 hard-world, objective S1/S4, mask-family JEPA 실패를 toxic anchor로 두고,
public scalar response, subset tomography, hard-world toxicity, broad toxicity를 함께 사용해 anti-listener action field를 만든다.

현재 local/stress readout:

```text
toxic anchors: 5
candidate row-target directions: 938
source responsibility LOO correlation: 0.7682
recommended variant: private_safe_anti_listener_bridge
changed cells: 30
selected rows: 29
sum predicted public delta: -0.69071
mean private safety: 0.7890
mean hard-world toxicity: 0.2003
mean broad toxicity: 0.4267
null score z: 9.9171
private-safety z: 9.2570
hard-world toxicity z: -4.9616
file: submission_hsjepa_anti_listener_toxicity_private_safe_anti_listener_bridge_0b72cf91_uploadsafe.csv
```

핵심은 다음이다.

```text
listener responsibility is not always an action generator;
failed listeners can be negative teachers for action-health.
```

이 후보가 public에서 좋아지면:

- HS-JEPA의 listener 모듈은 “무엇을 따라야 하는가”뿐 아니라 “무엇을 반대로 봐야 하는가”까지 학습한다.
- action-health는 confidence score가 아니라 positive/negative listener equation을 분리하는 field다.
- 논문 contribution은 `external listener tomography`에서 `anti-listener action-health`로 확장된다.

나빠지면:

- listener failure는 real diagnostic이지만 아직 invertible action equation은 아니다.
- public/private subset, route invariant, toxicity field 중 하나가 여전히 action validity를 충분히 설명하지 못한다.
- 다음에는 실패 anchor를 더 많이 모으거나, human-social/cohort invariant를 toxicity head에 직접 넣어야 한다.

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

### 증거 7. Negative representation은 invariant projection이 필요하다

Spectral solver 이후 새로 만든 projection solver는 public-bad tangent의 반대 방향을 그대로 쓰지 않고, target-route/subject-prior invariant를 통과한 cell만 release했다.

```text
projected cells: 232
recommended variant: subject_prior_safe_projection
changed cells: 18
bad tangent cosine: -0.2259
mean route energy delta: -0.01685
mean subject energy delta: -0.00106
file: submission_hsjepa_negative_tangent_invariant_subject_prior_safe_projection_ebdccca6_uploadsafe.csv
```

해석:

```text
HS-JEPA의 next thesis는 "negative public representation을 찾았다"가 아니라,
"그 representation을 human-state invariant 위의 action으로 project할 수 있다"이다.
```

이 후보가 public에서 좋아지면:

- failed action geometry는 단순 진단이 아니라 usable negative representation이다.
- subject-prior coordinate가 action validity에 중요하다는 증거가 생긴다.
- HS-JEPA의 decoder contribution은 `negative representation + invariant projection`으로 정리된다.

나빠지면:

- public-bad tangent는 real이지만 아직 invertible하지 않다.
- invariant를 train label/subject prior로 근사한 현재 방식이 부족하다.
- 다음에는 richer human/social/cohort invariant가 필요하다.

### 증거 8. Public scalar listener는 row-target responsibility를 일부 복원한다

LB-conditioned responsibility solver는 H057 이후 public 관측 26개를 외부 listener observation으로 보고, 115개 action feature에 대해 LOO ridge responsibility equation을 맞췄다.

```text
anchor count: 26
feature count: 115
LOO correlation: 0.7300
LOO MSE: 0.4829
recommended variant: pure_lb_gradient_jackpot
changed cells: 24
selected rows: 22
sum predicted loss delta: -7.11879
mean route energy delta: -0.03290
bad tangent cosine: 0.05506
file: submission_hsjepa_lb_responsibility_pure_lb_gradient_jackpot_f0a8129d_uploadsafe.csv
```

해석:

```text
public LB는 단순 점수표가 아니라, row-target action responsibility를 약하게 말하는 scalar listener다.
```

이 후보가 public에서 좋아지면:

- HS-JEPA의 listener responsibility는 explicit target label 없이도 external scalar outcome에서 추정될 수 있다.
- spectral bad tangent의 단순 반대 방향보다, scalar listener equation이 더 action-grade다.
- 논문 contribution은 `negative representation + invariant projection`에서 `external listener responsibility inversion`까지 확장된다.

나빠지면:

- public scalar equation은 descriptive diagnostic일 뿐, 아직 row-target action을 직접 release할 만큼 충분하지 않다.
- spectral tangent와 scalar listener가 충돌할 때, hidden public/private row-support assignment가 더 근본 병목이다.
- 다음에는 public/private subset factorization 또는 richer human-state invariant가 필요하다.

### 증거 9. Public response는 단일 listener보다 mixture listener로 더 잘 설명된다

Mixture-listener responsibility solver는 같은 26개 public 관측을 하나의 scalar gradient가 아니라 latent listener head들의 합성으로 설명했다.

```text
anchor count: 26
candidate cells: 575
mixture LOO correlation: 0.9578
scalar LOO correlation: 0.7300
recommended variant: target_listener_split_qs
changed cells: 30
selected rows: 28
sum predicted scalar delta: -4.34421
sum predicted mode delta: -0.53670
bad tangent cosine: -0.00420
file: submission_hsjepa_mixture_listener_target_listener_split_qs_7a383104_uploadsafe.csv
```

해석:

```text
public LB response is not necessarily one listener;
it may be a scalar projection of multiple latent listener heads.
```

이 후보가 public에서 좋아지면:

- HS-JEPA의 listener responsibility는 단일 scalar inversion보다 latent mixture routing으로 정리된다.
- Q/S target은 같은 hidden human-state를 보더라도 서로 다른 listener head를 통과해야 한다는 증거가 생긴다.
- 논문 contribution은 `external listener responsibility`에서 `latent listener mixture routing`까지 확장된다.

나빠지면:

- mixture decomposition은 public-score reconstruction에는 좋지만 action-grade decoder는 아니다.
- public anchors의 scalar 정보만으로는 latent listener를 식별하기 부족하다.
- 다음에는 private/public subset factorization 또는 richer human/social invariant가 필요하다.

### 증거 10. Public/private subset은 scalar response보다 더 날카로운 병목이다

Public/private subset tomography solver는 public scalar feedback을 `subset inclusion × hidden label direction`으로 다시 분해했다.

```text
anchor count: 26
source responsibility LOO correlation: 0.7300
candidate cells: 115
recommended variant: subset_label_direction_jackpot
changed cells: 18
selected rows: 16
sum predicted loss delta: -4.92956
mean inclusion score: 0.7610
mean label confidence: 0.8720
mean private safety score: 0.5850
mean toxicity score: 0.4250
file: submission_hsjepa_subset_tomography_subset_label_direction_jackpot_d12af8ff_uploadsafe.csv
```

동시에 더 안전한 thesis sensor도 생성했다.

```text
variant: qs_dual_subset_route
changed cells: 37
sum predicted loss delta: -4.57917
mean inclusion score: 0.6340
mean label confidence: 0.7810
mean private safety score: 0.6310
mean toxicity score: 0.3760
bad tangent cosine: -0.0392
file: submission_hsjepa_subset_tomography_qs_dual_subset_route_288f1d64_uploadsafe.csv
```

해석:

```text
0.53급 breakthrough는 더 큰 encoder가 아니라,
public listener가 말한 subset과 private-safe action subset을 분리하는 equation에서 나올 가능성이 높다.
```

이 후보가 public에서 좋아지면:

- public LB는 단순한 loss gradient가 아니라 partial listener equation이라는 주장이 강해진다.
- HS-JEPA의 listener responsibility는 subset membership, label direction, action-health를 동시에 풀어야 한다.
- 논문 contribution은 `latent listener mixture`에서 `external listener tomography`까지 확장된다.

나빠지면:

- current public anchors는 subset inclusion을 descriptive하게 설명하지만 action-grade로 release하기에는 부족하다.
- public/private split은 real이더라도, 현재 invariant가 private safety를 충분히 대변하지 못한다.
- 다음에는 human-social/cohort invariant를 private-safety head에 더 직접적으로 넣어야 한다.

## 논문에서 과장하면 안 되는 것

- HS-JEPA core만으로 현재 최고 LB를 바로 재현한다고 말하면 안 된다.
- public LB sensor는 일반 기술이 아니라 competition adapter의 관측 장비다.
- S2 hub는 이 대회의 case-study 발견이지, 모든 수면 문제에 universal하게 적용된다고 주장하면 안 된다.
- human-state encoder 하나가 row-target assignment를 완전히 해결했다고 말하면 안 된다.
- invariant projection 후보가 public에서 검증되기 전까지, negative representation을 action-grade decoder라고 단정하면 안 된다.
- LB-conditioned responsibility 후보가 public에서 검증되기 전까지, scalar public listener inversion을 portable decoder라고 말하면 안 된다.
- mixture-listener 후보가 public에서 검증되기 전까지, latent listener mixture routing을 action-grade decoder라고 단정하면 안 된다.
- subset tomography 후보가 public에서 검증되기 전까지, public/private listener equation을 action-grade decoder라고 단정하면 안 된다.
- anti-listener toxicity 후보가 public에서 검증되기 전까지, 실패한 listener action의 반대 방향이 항상 action-grade라고 단정하면 안 된다.

## 정확한 thesis 문장

논문에서 가장 안전하고 강한 문장은 다음이다.

```text
HS-JEPA reframes human-understanding prediction as hidden-state and action-field recovery.
In our sleep-log case study, the largest public-LB gains came not from direct label prediction,
but from recovering sparse row-target action fields and filtering them through listener responsibility,
action-health, invariant-preserving decoders, and negative-listener toxicity checks.
```

한국어로는:

```text
HS-JEPA는 인간 이해 예측을 label 분류가 아니라 hidden human-state와 action field 복원 문제로 재정의한다.
수면 생활 로그 대회에서는 직접 label을 맞히는 모델보다, row-target action field를 복원하고 이를 listener responsibility,
action-health, invariant decoder, negative-listener toxicity check로 통과시킨 접근이 가장 큰 public LB 개선을 만들었다.
```

## 다음으로 가장 정보량이 큰 제출 센서

현재 thesis 관점에서 가장 정보량이 큰 후보는 다음이다.

```text
submission_hsjepa_anti_listener_toxicity_private_safe_anti_listener_bridge_0b72cf91_uploadsafe.csv
```

이 후보가 좋아지면:

- 실패한 listener-derived action은 버릴 노이즈가 아니라 negative target representation이었다는 뜻이다.
- HS-JEPA의 `action-health`는 좋은 signal을 고르는 모듈뿐 아니라, 나쁜 listener 방향을 반대로 읽는 anti-listener equation을 포함해야 한다.
- public/private subset tomography와 hard-world/broad toxicity를 함께 통과한 private-safe action field가 action-grade일 수 있다.

이 후보가 나빠지고 subset tomography 또는 invariant-projected anti-tangent가 좋아지면:

- anti-listener inversion은 너무 강하거나 anchor-specific하고, subset membership 또는 invariant projection이 더 중요한 action-validity 조건이다.

둘 다 나빠지면:

- public failure geometry, scalar responsibility, anti-listener toxicity는 모두 real diagnostic이지만, 아직 public/private row-support assignment를 충분히 복원하지 못한다.
- HS-JEPA는 action direction보다 hidden public/private subset factorization과 richer human/social/cohort invariant를 더 강화해야 한다.
