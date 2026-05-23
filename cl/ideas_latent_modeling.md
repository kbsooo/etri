# DACON ETRI 생활/수면/디지털 행동 데이터 기반 다중 이진 라벨 예측 — 아이디어 로그

작성 시작: 2026-05-22
작성자: 람봉 / Byungsoo Kang 논의

## 0. 현재 문제 인식

- 라벨은 `ch2026_metrics_train.csv` 기준 450개로 매우 적다.
- 반면 입력 lifelog 데이터는 sensor stream 형태로 매우 풍부하다.
- target은 7개 binary label: `Q1, Q2, Q3, S1, S2, S3, S4`.
- test도 같은 10명 subject의 다른 날짜를 예측하는 구조다.
- 핵심은 일반적인 tabular tree fitting보다, 풍부한 unlabeled/semi-labeled sequential sensor data에서 좋은 representation을 뽑고, 그 latent representation을 작은 라벨셋에 안정적으로 연결하는 것일 가능성이 크다.

## 1. Byungsoo의 핵심 모델링 직관

> Transformer Encoder-Decoder, Diffusion Forward-Reverse처럼 중간에 latent space를 두는 구조가 가능성이 있어 보인다. 라벨은 적지만 자세한 sensor 데이터는 많기 때문이다.

이 직관은 상당히 타당하다. 이 문제에서 모델링의 핵심은 “450개 label을 직접 맞추는 supervised learner”라기보다,

```text
raw lifelog streams -> subject/day latent state -> seven sleep/condition labels
```

로 보는 게 더 자연스럽다.

## 2. 내 현재 의견

### 2.1 Tree 모델만으로 끝내기 아쉬운 이유

LightGBM/CatBoost 같은 tree 모델은 baseline과 feature importance 확인에는 강하지만, 이 대회에서 참신한 점수 상승을 만들기에는 한계가 있을 수 있다.

특히 이 데이터는 다음 특성이 있다.

1. sensor stream이 시간축을 가진다.
2. label은 day-level binary로 압축되어 있다.
3. label 수가 매우 작다.
4. 같은 subject의 여러 날짜가 존재한다.
5. Q-label은 개인 평균 대비 subjective outcome이다.
6. S-label은 수면 구조의 latent property다.

따라서 직접 engineered feature -> binary classifier보다,

```text
하루의 행동 리듬 / 수면 리듬 / 스트레스 상태 / 회복 상태
```

같은 latent state를 먼저 학습하고, 그 latent state로 label을 예측하는 접근이 더 문제 구조에 맞을 수 있다.

### 2.2 latent space 접근이 유리할 수 있는 이유

라벨은 450개뿐이지만, unlabeled day-level sensor data는 train/test 전체와 sensor 내부 시계열까지 포함하면 훨씬 많다. 그러므로 다음 방식이 가능하다.

- self-supervised pretraining
- reconstruction objective
- masked sensor modeling
- contrastive learning
- subject/day embedding
- sequence-to-sequence summarization
- denoising objective
- latent diffusion 또는 diffusion-inspired denoising

즉, label을 직접 학습하기 전에 sensor data의 structure를 먼저 학습할 수 있다.

## 3. 핵심 방향: feature engineering 90%, model novelty 10%

현재 우선순위는 여전히 데이터 가설/feature 쪽이다.

이유:

- 라벨이 작아서 복잡한 neural model은 쉽게 overfit한다.
- 좋은 latent model도 결국 어떤 입력 representation을 먹일지가 중요하다.
- 수면/피로/스트레스 label은 domain proxy가 강하다.
- sensor별 aggregation, subject-normalization, sleep proxy 설계가 성능의 대부분을 좌우할 가능성이 크다.

하지만 feature를 단순 tabular column으로 끝내지 않고, latent model이 먹기 좋은 형태로 만드는 게 중요하다.

## 4. 잠정 모델링 철학

### 4.1 하지 않을 것

- 단순히 모든 aggregate feature를 만들고 LightGBM만 돌리는 접근에 머무르지 않는다.
- 앱 이름, WiFi/BLE 주소 등을 무식하게 one-hot해서 overfit하지 않는다.
- 랜덤 KFold 성능에 속지 않는다.
- label 450개로 큰 Transformer를 end-to-end supervised 학습하지 않는다.

### 4.2 할 것

- subject/day 단위의 행동 latent state를 만든다.
- 각 날짜를 시간대별 token sequence로 표현한다.
- self-supervised objective로 representation을 먼저 학습한다.
- 이후 작은 supervised head 또는 calibrated linear/probe model로 7개 label을 예측한다.
- 최종 제출에서는 subject prior와 calibrated prediction을 blend한다.

## 5. 유망한 latent modeling 후보

### 5.1 Day Encoder: 하루를 token sequence로 보기

하루를 예를 들어 30분 또는 1시간 bin으로 나눈다.

```text
1 day = 24 tokens if hourly
1 day = 48 tokens if 30-min bins
```

각 token에는 sensor aggregate가 들어간다.

```text
screen_on, steps, distance, light, HR, GPS movement, app usage, ambience, wifi/ble density, charging, activity
```

그 다음:

```text
[time-bin sensor vector sequence] -> Transformer Encoder -> day embedding
```

이 day embedding으로 7개 label을 예측한다.

장점:

- 시간 구조를 살릴 수 있다.
- 취침 전/수면 중/기상 후 pattern을 자동으로 잡을 수 있다.
- engineered feature보다 더 풍부한 rhythm representation이 가능하다.

위험:

- label이 작아서 supervised end-to-end는 overfit 가능성이 높다.
- 반드시 self-supervised pretraining 또는 strong regularization 필요.

### 5.2 Masked Sensor Modeling

BERT식 objective.

입력 sequence 일부 시간 bin 또는 sensor channel을 mask하고 복원한다.

예:

```text
mask 20% time bins -> reconstruct steps/light/screen/hr
mask one modality -> reconstruct from other modalities
```

학습 데이터는 train/test 모든 lifelog day를 사용할 수 있다. label이 없어도 된다.

학습 후:

```text
pretrained encoder -> freeze or partial fine-tune -> small classifier head
```

### 5.3 Denoising Autoencoder

Diffusion의 forward-reverse까지 크게 가지 않더라도, denoising objective는 강한 후보.

```text
clean day sequence x
noisy/corrupted x_t = random masking + gaussian noise + time block dropout
encoder-decoder reconstruct x
latent z = encoder bottleneck
```

이 z를 day-level representation으로 사용.

특히 sensor missingness가 많은 실제 데이터에 잘 맞을 수 있음.

### 5.4 Contrastive Learning: same-subject nearby days

좋은 positive pair 후보:

- 같은 subject의 인접 날짜
- 같은 subject의 비슷한 요일
- 같은 subject의 비슷한 sleep proxy pattern

negative pair:

- 다른 subject
- 같은 subject라도 너무 다른 rhythm day

주의:

- 너무 강하게 subject identity만 학습하면 label에는 도움되지만 generalization이 약해질 수 있다.
- 이 대회는 test subject가 train subject와 같으므로 subject identity 학습이 완전히 나쁜 것은 아니다.

가능 objective:

```text
SimCLR / SupCon-like unsupervised contrastive
```

### 5.5 Sequence-to-sequence behavioral reconstruction

Encoder-decoder 구조를 명시적으로 사용:

```text
encoder: 전날/당일 행동 sequence -> latent z
 decoder: sensor sequence reconstruction or next-window prediction
 head: Q/S labels prediction
```

특히 다음 task가 가능하다.

- 오전/오후 데이터로 저녁/밤 pattern 예측
- daytime behavior로 night recovery proxy 예측
- previous day latent로 current sleep label 예측

### 5.6 Latent state model / HMM-style idea

하루를 몇 개의 latent 상태로 본다.

예:

```text
Resting / Active / Commuting / Social / Screen-heavy / Sleep-like / Disturbed-sleep
```

방법:

- unsupervised clustering of time bins
- 각 day를 state occupancy vector로 요약
- state transition counts를 feature로 사용

이건 neural보다 구현이 쉽고, 도메인 설명력도 좋다.

```text
time-bin features -> clustering/KMeans/GMM -> daily state histogram + transition matrix -> label model
```

참신하면서도 안정적인 접근일 수 있다.

## 6. 중요한 데이터 가설

### 6.1 개인 기준 deviation이 핵심

Q1~Q3는 개인 평균 대비 label이므로, 모든 feature는 subject-normalized version이 필요하다.

```text
x_raw
x_subject_mean
x - subject_mean
(x - subject_mean) / subject_std
x / subject_mean
rolling_3d_delta
rolling_7d_delta
```

### 6.2 수면 label은 sleep-like block을 찾아야 한다

S1~S4는 sleep sensor에서 나온 label이지만, 제공 데이터에서는 직접 sleep stage가 없다. 따라서 sensor stream에서 sleep proxy를 추정해야 한다.

핵심 proxy:

- longest screen-off block
- low activity block
- low light block
- low movement block
- HR resting period
- night interruptions

### 6.3 Q2/Q3는 daytime load + recovery의 함수

피로/스트레스는 단일 feature보다 다음 조합이 중요할 수 있다.

```text
daytime physical/social/cognitive load + night recovery quality
```

load proxy:

- steps
- GPS mobility
- app usage entropy
- screen fragmentation
- BLE/WiFi density
- ambience speech/vehicle/outside
- HR high percentile

recovery proxy:

- sleep-like block length
- night interruption
- resting HR
- darkness duration

## 7. 향후 실험 우선순위

### Stage 1. 강한 feature table 만들기

- subject/day 단위 aggregate
- time-bin aggregate
- subject-normalized features
- sleep proxy features
- app/WiFi/BLE/ambience semantic features

### Stage 2. latent representation 만들기

1. hourly/30-min sequence tensor 생성
2. masked sensor modeling pretraining
3. denoising autoencoder pretraining
4. latent z 추출
5. z + engineered features 결합

### Stage 3. small supervised head

- logistic/ridge probe
- tiny MLP with dropout
- target-specific heads
- multi-task shared encoder + 7 heads

### Stage 4. calibration/blending

- subject prior smoothing
- prediction clipping
- target별 temperature scaling
- subject prior + latent model blend

## 8. 당장 합의한 방향

- 데이터 가설/feature engineering을 우선한다.
- 하지만 feature를 tree-only 용도가 아니라 latent model input으로도 쓸 수 있게 설계한다.
- 참신한 모델은 “큰 Transformer supervised 학습”보다 “self-supervised day representation + 작은 supervised head” 쪽이 더 현실적이다.
- 문서화는 이 파일에 계속 누적한다.


---

## 9. 추가 논의: Tree 계열을 넘는 모델링 방향에 대한 합의

Byungsoo가 지적한 것처럼, 이 대회는 단순히 tree 계열 tabular classifier를 잘 튜닝하는 것만으로는 재미도 없고, 잠재적인 상위권 아이디어를 놓칠 수 있다.

중요한 관찰은 다음과 같다.

```text
라벨: 450개로 작음
입력: sensor stream은 매우 자세하고 풍부함
```

따라서 이 문제는 supervised tabular classification이라기보다,

```text
rich unlabeled/semi-labeled lifelog data에서 day-level latent state를 학습하고,
그 latent state를 작은 label set에 연결하는 문제
```

로 보는 게 더 적절하다.

### 9.1 내가 동의하는 핵심 방향

- 큰 supervised Transformer를 바로 학습하는 것은 위험하다.
- 하지만 Transformer/Diffusion의 철학, 즉 **중간 latent space를 통해 구조를 학습한다**는 방향은 매우 좋다.
- 이 데이터에서는 full diffusion보다 lightweight denoising / masked modeling / contrastive learning이 현실적이다.
- 모델 novelty보다 먼저 sensor proxy와 domain feature가 좋아야 한다.
- feature를 tree model용 table로만 보지 말고, latent model input sequence로도 설계해야 한다.

### 9.2 추천 구조

```text
raw sensor streams
  -> time-bin sequence representation
  -> self-supervised encoder / denoising autoencoder / behavioral state clustering
  -> day latent z
  -> small supervised head
  -> subject prior blend + calibration
  -> final probabilities
```

### 9.3 왜 이 접근이 좋나

1. label이 적어도 unlabeled sensor structure를 활용할 수 있다.
2. 하루의 rhythm, recovery, stimulation, interruption 같은 latent state를 학습할 수 있다.
3. subject별 개인차를 latent space와 subject-normalized feature로 모두 반영할 수 있다.
4. sleep labels는 직접 관측되지 않는 sleep quality variables라 latent proxy가 자연스럽다.
5. logloss 관점에서 small head + calibration이 큰 모델보다 안정적일 수 있다.

### 9.4 실험하기로 한 방향

모든 관련 실험을 진행한다. 별도 실행 계획은 다음 파일에 정리했다.

```text
/Users/kbsoo/Downloads/cl/experiment_plan.md
```

우선순위는 다음과 같다.

```text
1. validation + subject prior baseline
2. daily/window/domain features
3. subject-normalized deviation features
4. sleep-like block / recovery proxy
5. behavioral state clustering
6. denoising autoencoder
7. masked sensor modeling
8. contrastive day encoder
9. small supervised probe + calibration/blending
```
