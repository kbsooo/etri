# Strict JEPA Data Reframing

이번 턴의 목적은 단순히 JEPA 이름을 붙이는 것이 아니라, **우리 데이터에서 진짜 JEPA가 먹히려면 hidden target과 context가 어떤 형태여야 하는지**를 수치로 분리하는 것이었습니다.

## 이번에 새로 한 실험

1. `jepa_ready_data_audit.py`
   - 기존 block-canvas 계열이 얼마나 `partly-JEPA`였는지 확인
   - `current_visible_target` vs `strict_surround` vs `strict_labelonly` vs `strict_prior` 비교

2. `jepa_semantic_prototype_search.py`
   - hidden block을 raw reconstruction 대신 `semantic prototype codebook`으로 바꿔봄
   - 각 family를 K-way prototype으로 군집화하고, strict context가 그 prototype을 얼마나 예측 가능한지 측정
   - prototype posterior가 7개 target rate를 얼마나 복원하는지도 함께 측정

## 핵심 발견

### 1) 기존 일부 JEPA 실험은 strict JEPA가 아니었다

`block_canvas_jepa`의 context에는 hidden block 자체에서 나온 요약이 일부 들어가 있었습니다.  
그래서 예전 결과 중 일부는 “가린 block을 주변만 보고 맞힌 것”이 아니라, **가린 block을 조금 본 뒤 representation을 맞힌 것**에 더 가까웠습니다.

이걸 strict하게 분리한 결과:

- `mean_latent`: `current_visible_target 0.0625 -> strict_surround -0.0210`
- `modality_state`: `0.0203 -> -0.0287`
- `label_state`: `-0.5481 -> -0.5974`

즉, hidden block을 직접 조금이라도 보여주면 성립하던 신호가, strict setting에서는 크게 약해집니다.

### 2) strict JEPA에서 잘 맞는 건 “정교한 raw latent”가 아니라 “거친 routine prototype”이다

strict surround에서 prototype 예측이 가장 잘 되는 후보는 전부 **작은 codebook(K=4)** 입니다.

- `hybrid_raw K=4`: `proto_logloss 0.6379`, `proto_acc 0.8236`
- `mean_latent K=4`: `proto_logloss 0.7244`, `proto_acc 0.8462`
- `window_state K=4`: `proto_logloss 1.0714`, `proto_acc 0.7472`

해석:

- subject timeline에는 block-level raw state가 무한히 다양하게 있는 것이 아니라,
- **소수의 반복적인 routine / episode 타입**으로 접히는 구조가 있습니다.
- 즉, 다음 JEPA는 hidden target을 “정밀한 latent vector”로 두기보다 **작은 semantic codebook**으로 두는 쪽이 더 자연스럽습니다.

### 3) label 의미를 많이 담는 prototype은 예측 가능성이 떨어진다

반대로 label-semantic을 많이 담는 family는, true prototype만 알면 label 복원력이 높지만 strict context에서 예측하기가 어렵습니다.

예:

- `label_rate_only K=10`: `oracle_rate_r2 0.3791`, 하지만 `strict_labelonly pred_rate_r2 0.0221`
- `label_state K=10`: `oracle_rate_r2 0.2260`, 하지만 `strict_surround proto_logloss 4.6836`
- `hybrid_oracle K=10`: `strict_surround pred_rate_r2 0.0928`, 하지만 `proto_logloss 2.2495`, `proto_acc 0.5602`

해석:

- **semantic usefulness**와 **context predictability**가 같은 축이 아닙니다.
- raw routine prototype은 잘 맞지만 label과 1:1로 이어지지 않고,
- label-rich prototype은 downstream에는 좋지만 context만으로는 잘 안 맞습니다.

즉 다음 JEPA는 한 단계짜리 latent보다:

- `coarse predictable latent`
- `semantic distilled latent`

의 **2-level target**이 더 맞습니다.

### 4) block을 길게 잡을수록 JEPA에 유리하다

I-JEPA 논문의 “큰 semantic target block” 가설이 우리 데이터에서도 거의 그대로 확인됐습니다.

예를 들어 strict surround에서:

- `hybrid_raw K=4`
  - `long_5p`: `acc 0.9362`, `logloss 0.3610`
  - `short_1_2`: `acc 0.7308`, `logloss 0.9773`

- `mean_latent K=4`
  - `long_5p`: `acc 0.9149`, `logloss 0.4420`
  - `short_1_2`: `acc 0.7308`, `logloss 1.4125`

해석:

- 짧은 block은 measurement noise와 local randomness 비중이 너무 큽니다.
- **길이 5 이상 contiguous episode**가 되어야 semantic state가 드러납니다.

### 5) raw context를 많이 넣는다고 좋아지지 않는다

오히려 prototype 예측만 보면 `strict_labelonly`가 `strict_surround`보다 더 낫습니다.

예:

- `hybrid_raw K=4`: `strict_labelonly logloss 0.3192` vs `strict_surround 0.6379`
- `mean_latent K=4`: `0.6286` vs `0.7244`

해석:

- 주변 raw sensor context는 informative하기도 하지만, 현재 방식으로는 noise도 같이 큽니다.
- raw context를 그대로 predictor에 밀어 넣기보다,
  **gated / compressed / prototype-ized context**로 바꾸는 게 맞습니다.

## 데이터 관점에서 다시 정의한 “JEPA-friendly” 형태

다음 JEPA에서 hidden target은 아래 조건을 만족해야 합니다.

1. **길다**
   - `len >= 5` contiguous episode 위주

2. **거칠다**
   - 상세 raw latent 전체가 아니라 `K=4` 수준의 coarse routine code

3. **semantic 보조축이 있다**
   - coarse code 하나만으로는 label 정보가 약하므로
   - `K=8~10` 수준 semantic distilled head를 같이 둬야 함

4. **context는 분산돼 있어야 한다**
   - left/right flank
   - subject prior
   - process / rhythm metadata
   - raw context는 직접 concat보다 compress 후 사용

## 다음 JEPA 실험 후보

### 1. Two-Level Prototype JEPA

- target 1: `coarse raw routine code (K=4)`
- target 2: `semantic distilled code (K=8 or 10)`
- predictor는 먼저 coarse target을 맞추고, 그 위에서 semantic head를 residual처럼 맞춤

이게 지금 데이터 구조에 가장 맞습니다.

### 2. Long-Block Only JEPA

- short block은 버리거나 weight를 크게 낮춤
- pretraining target은 `len >= 5` hidden episode만 사용
- 짧은 block은 downstream probe feature로만 사용

### 3. Label-Distilled Raw Codebook JEPA

- raw-only family로 먼저 predictable codebook을 만들고
- 그 codebook에 label-state teacher를 distill
- 즉 “예측 가능한 raw routine”과 “downstream에 필요한 semantic state” 사이를 연결

## 생성된 파일

- `jepa/jepa_ready_data_audit.py`
- `jepa/jepa_ready_data_audit_summary.csv`
- `jepa/jepa_ready_data_audit_gap.csv`
- `jepa/jepa_ready_data_audit_report.md`
- `jepa/jepa_semantic_prototype_search.py`
- `jepa/jepa_semantic_prototype_search_summary.csv`
- `jepa/jepa_semantic_prototype_search_lenbucket.csv`
- `jepa/jepa_semantic_prototype_shortlist.csv`

## 결론

지금까지는 JEPA 아이디어를 “hidden block latent를 맞히는 것”에 가깝게 가져왔습니다.  
이번 실험으로 보니, 우리 데이터에서는 그보다 더 JEPA답게 가려면:

- **큰 hidden episode**
- **작은 routine codebook**
- **semantic distillation 보조축**
- **compressed context**

이 네 가지가 핵심입니다.

즉, 다음 단계는 raw timeline 자체를 더 세게 밀기보다,  
**raw timeline을 semantic prototype episode로 다시 조직한 뒤 그 위에서 JEPA를 거는 것**입니다.
