# JEPA-Friendly Data Mining Report

이번 goal은 예전의 “Log Loss 0.5대 단서 찾기”를 그대로 가져오되, 목적 함수를 바꾼 것입니다.

이전 목표:

- 숨은 라벨 생성 규칙, 준누수, feature를 찾아 Log Loss를 낮춘다.

이번 목표:

- strict context만으로 예측 가능한 hidden target을 찾는다.
- 그 target이 Q1/Q2/Q3/S1-S4 의미를 충분히 보존해야 한다.
- collapse 없이 codebook이 균형을 가져야 한다.
- submission-like hidden block geometry에서 성립해야 한다.

즉, 이번에는 `JEPA-friendly = predictable + semantic + non-collapsed + fold-safe`로 정의했습니다.

## 새로 만든 실험

### 1. JEPA-Friendly Atlas

파일:

- `jepa_friendly_atlas.py`
- `jepa_friendly_atlas_summary.csv`
- `jepa_friendly_atlas_pareto.csv`
- `jepa_friendly_atlas_context_summary.csv`
- `jepa_friendly_atlas_block_summary.csv`
- `jepa_friendly_atlas_family_summary.csv`
- `jepa_friendly_practical_shortlist.csv`

스캔 축:

- block geometry: `submission_like`, `fixed_2`, `fixed_4`, `fixed_6`, `fixed_8`
- target family: `time_meta`, `raw_mean`, `raw_trend`, `window_state`, `modality_state`, `canvas_process`, `hybrid_raw`, `label_rate`, `label_state`, `teacher_hybrid`
- codebook size: `K=4,8,10`
- context: `meta`, `past/future/bidir/prior raw`, `past/future/bidir/prior label`, `full_strict`

### 2. Two-Level Prototype JEPA Audit

파일:

- `two_level_proto_jepa_audit.py`
- `two_level_proto_jepa_summary.csv`
- `two_level_proto_jepa_vs_direct.csv`

검증한 가설:

- 먼저 predictable coarse raw routine code를 맞히고
- 그 posterior가 semantic label-rate code 예측을 도와주는지 확인

### 3. Targetwise JEPA Probe

파일:

- `jepa_friendly_targetwise_probe.py`
- `jepa_friendly_targetwise_summary.csv`
- `jepa_friendly_targetwise_pivot.csv`

검증한 가설:

- JEPA-friendly 신호가 Q와 S 타깃에 균등하게 있지 않을 것이다.
- 특히 objective stage ratio인 S1-S4 쪽에 더 강할 가능성이 높다.

## 핵심 발견

### 1. 너무 쉬운 target은 JEPA-friendly가 아니다

`time_meta`는 score 상위권을 휩쓸었습니다.

예:

- `fixed_2 / time_meta / K=4 / meta_only`
- `proto_logloss 0.0833`
- `proto_acc 0.9913`
- `proto_predictability 0.9399`

하지만 semantic은 없습니다.

- `oracle_rate_r2 -0.0518`
- `pred_rate_r2 -0.0494`

결론:

- JEPA target이 “context로 잘 맞는다”만 보면 안 됩니다.
- `time/position/dow` 같은 trivial target은 강한 collapse-safe pretext처럼 보이지만, downstream sleep target 의미가 없습니다.

### 2. 예측 가능성과 의미 보존은 서로 다른 축이다

가장 중요한 구조적 발견입니다.

`raw_mean K=8`은 매우 JEPA-friendly한 routine latent입니다.

- `submission_like / raw_mean / K=8 / prior_label`
- `proto_predictability 0.6788`
- `proto_acc 0.8288`
- `pred_rate_r2 0.1076`

반면 semantic target인 `label_rate K=10`은 의미 보존이 훨씬 강하지만 예측은 더 어렵습니다.

- `submission_like / label_rate / K=10 / past_label`
- `oracle_rate_r2 0.3825`
- `pred_rate_r2 0.1385`
- `proto_predictability 0.2021`
- `proto_acc 0.3912`

결론:

- raw routine code는 예측 가능하지만 의미가 약합니다.
- label-rate semantic code는 의미가 강하지만 예측이 어렵습니다.
- 따라서 단일 JEPA target보다 **routine head + semantic head**가 맞습니다.

### 3. 실제 submission-like geometry에서 가장 실용적인 semantic bridge는 label-rate code다

직접적인 bridge 관점에서 최고는:

- `submission_like / label_rate / K=10 / past_label`
- `pred_rate_r2 0.1385`
- `oracle_rate_r2 0.3825`

그 다음:

- `submission_like / label_rate / K=8 / past_label`
- `pred_rate_r2 0.1214`
- `oracle_rate_r2 0.3380`

해석:

- hidden block label-rate distribution은 주변 train label 흐름에서 꽤 예측됩니다.
- 특히 subject prior보다 `past_label`이 더 잘 작동합니다.
- 이 데이터는 “raw image patch completion”보다 **subject episode label-flow completion**에 더 가깝습니다.

### 4. raw context를 많이 넣는 것이 답이 아니다

context summary에서 best semantic bridge는 label context 쪽이 강했습니다.

- `past_label`: best `pred_rate_r2 0.1385`
- `prior_label`: best `pred_rate_r2 0.1076`
- `bidir_label`: best `pred_rate_r2 0.1034`
- raw 계열은 대부분 더 낮거나 overfit/noise가 큼

결론:

- 우리 데이터의 JEPA context는 raw sensor canvas 전체가 아니라,
- `known label/base prediction/routine prior`가 들어간 compressed context여야 합니다.

### 5. target-wise로 보면 S 타깃이 JEPA-friendly하다

가장 중요한 downstream insight입니다.

`submission_like / label_rate / K=10 / past_label` target-wise:

- `Q1 0.0198`
- `Q2 0.1292`
- `Q3 0.0988`
- `S1 0.1841`
- `S2 0.2913`
- `S3 0.2706`
- `S4 0.1047`
- mean `0.1569`

다른 geometry에서도 S2/S3가 강합니다.

`fixed_4 / label_rate / K=10 / prior_label`:

- `S3 pred_r2 0.4697`
- `S2 pred_r2 0.3506`
- `S1 pred_r2 0.2629`
- `S4 pred_r2 0.0989`

결론:

- JEPA가 가장 잘 살릴 수 있는 축은 Q subjective target보다 S objective stage ratio입니다.
- 특히 S2/S3는 hidden block context completion 문제로 재해석하기 좋습니다.

### 6. Two-Level JEPA는 일부 상황에서는 맞지만, 아직 큰 한방은 아니다

2-level audit 결과:

- direct `full_strict / label_rate K=10`: `pred_rate_r2 -0.2765`
- `raw_mean K=8 coarse_prob_only`를 쓰면: `pred_rate_r2 0.0210`
- improvement: `+0.2975`

즉, raw/full strict context가 너무 noisy할 때 coarse routine posterior가 semantic 예측을 크게 구제합니다.

하지만 전체 최고는 여전히:

- direct `past_label / label_rate K=10`
- `pred_rate_r2 0.1385`

결론:

- 2-level은 방향은 맞습니다.
- 다만 “coarse를 섞으면 무조건 더 좋다”는 아닙니다.
- label-context가 좋은 경우에는 direct semantic code prediction이 더 강합니다.

## JEPA-Friendly 데이터 형태 재정의

이 데이터는 이미지처럼 `raw patch -> hidden patch latent`로 보기보다, 아래처럼 보는 것이 더 맞습니다.

### Recommended Data Object

`Subject Episode Graph`

각 subject timeline을 다음 token들로 구성합니다.

1. observed label context token
   - 주변 train label rate
   - base prediction mean/std
   - label entropy
   - past/future/prior 분리

2. raw routine token
   - `raw_mean K=8`
   - subject routine / measurement process / hidden episode type

3. semantic rate token
   - `label_rate K=8 or K=10`
   - hidden block의 7-target rate distribution

4. stage-specific token
   - S1/S2/S3/S4 별도 head
   - 특히 S2/S3는 강하게 weight

### Recommended JEPA Geometry

1. primary geometry
   - `submission_like` hidden contiguous block
   - 실제 test 구조와 맞음

2. auxiliary geometry
   - `fixed_4` label-rate block
   - S2/S3 stage semantic이 가장 잘 살아남음

3. caution geometry
   - `fixed_8` raw target은 매우 예측 가능하지만 semantic이 약하거나 음수
   - pretext 안정화에는 쓸 수 있지만 downstream target으로 과신하면 안 됨

## 다음 모델 실험 우선순위

### 1. Label-Context Semantic JEPA

가장 직접적입니다.

- context: `past_label + prior_label + base prediction`
- target: `label_rate K=10`
- geometry: `submission_like`
- downstream focus: S1-S4, 특히 S2/S3

성공 기준:

- semantic prototype OOF에서 `pred_rate_r2 > 0.14`
- targetwise S2/S3 유지

### 2. Routine-Regularized Semantic JEPA

2-level을 더 보수적으로 씁니다.

- auxiliary head: `raw_mean K=8`
- main head: `label_rate K=10`
- coarse posterior는 semantic predictor의 regularizer로만 사용
- full strict/noisy context에서만 coarse posterior weight를 키움

성공 기준:

- direct past-label 성능을 해치지 않으면서 full-strict rescue 유지

### 3. Stage-Weighted JEPA

타깃을 균등하게 보지 않습니다.

- S2/S3 head 가중치 증가
- S1/S4 보조
- Q는 weak semantic head로 따로 분리

성공 기준:

- targetwise S2/S3 pred R2가 유지 또는 상승
- Q 쪽 negative transfer가 줄어듦

## 결론

JEPA-friendly 관점에서 우리 데이터의 핵심은 raw timeline canvas가 아닙니다.

더 정확한 형태는:

> 주변 label/base/routine context를 보고, hidden subject episode의 semantic rate code와 sleep-stage code를 맞히는 문제

입니다.

따라서 다음 JEPA는 “raw image-like reconstruction”보다:

- `past/prior label context encoder`
- `raw routine auxiliary encoder`
- `label-rate semantic target encoder`
- `S-stage weighted target heads`

이 구조가 맞습니다.
