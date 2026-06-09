# H155-H158 Posterior Loss-Null Jackpot HS-JEPA

Date: 2026-06-09

## 핵심 한 줄

H155-H158은 H057의 row-state best를 기준으로, H061 public posterior와 H154 local semantic listener를 결합한 뒤, 이미 public에서 손실로 관측된 action 축을 sparse support 안에서 제거하는 jackpot 실험이다.

## 왜 이게 큰 실험인가

이 실험은 단순 blend나 alpha 조절이 아니다.

기존 흐름은 다음과 같았다.

```text
H057: 특정 Q2-support row에는 완성된 hidden human-state vector가 있다.
H154: 그 hidden state 중 local semantic listener가 허락한 row-target cell만 안전하다.
H061: H057 feedback posterior는 public equation의 잔여 신호를 담고 있다.
```

H155-H158은 이 셋을 하나의 HS-JEPA decoder로 묶는다.

```text
H061 posterior field
  -> H154 semantic listener permission
  -> H155 posterior-listener bridge
  -> H154 source-consensus field와 결합
  -> known public-loss axes sparse 제거
  -> H158 row-target correction field
```

즉 “좋아 보이는 후보를 더 섞는다”가 아니라,

> 보이는 posterior/context/disagreement로 보이지 않는 listener-safe row-target action field를 예측한다.

라는 HS-JEPA식 주장이다.

## 실험별 의미

### H155: H061 posterior-listener bridge

파일:

`submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv`

의미:

H061 posterior를 그대로 쓰지 않고, H154 local semantic listener가 허락한 셀만 남겼다.

결과:

- changed cells: 150
- changed rows: 114
- base listener robust mean: -0.002063
- base listener robust max: -0.000644
- semantic listener robust mean: -0.001876
- semantic listener robust max: -0.000087
- H088 cosine: 0.002382

해석:

H061 posterior는 H154 semantic space 안에서 완전히 죽지 않았다.
다만 H154 자체보다 강하지는 않다.
따라서 H155는 단독 제출 후보라기보다, H154와 결합할 수 있는 posterior residual field로 보는 편이 맞다.

### H156: H154 + H155 combo field

파일:

`submission_h156_combo_h154_h155_a1.3_b1.3_30075624_uploadsafe.csv`

의미:

H154의 source-consensus semantic field와 H155의 H061 posterior field를 같은 방향의 listener-safe field로 보고 합쳤다.

결과:

- changed cells: 158
- changed rows: 117
- H154-H155 cosine: 0.687
- base listener robust mean: -0.006654
- base listener robust max: -0.002085
- semantic listener robust mean: -0.005568
- semantic listener robust max: -0.002810
- H088 cosine: 0.002649

해석:

H154와 H155는 완전히 같은 신호가 아니다.
서로 보완되는 action field이며, 합치면 listener stress가 크게 좋아진다.
이 후보는 “semantic source-consensus + posterior residual”이 같은 hidden public/private equation을 보고 있다는 bet이다.

### H157: dense loss-nullspace

상태: rejected

의미:

H156에서 known public-loss 축을 수학적으로 제거하려 했지만, correction이 1024개 셀로 퍼졌다.

해석:

이건 hidden state 복원이 아니라 global prior rewrite에 가까워졌다.
그래서 제출 후보로 승격하지 않는다.

중요한 실패:

known-loss projection은 전체 공간에서 하면 안 된다.
반드시 listener가 허락한 sparse support 안에서만 해야 한다.

### H158: sparse loss-nullspace jackpot

파일:

`submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv`

의미:

H156이 실제로 건드린 sparse support 안에서만 known public-loss 성분을 제거했다.

제거 대상으로 본 known-loss axes:

- H012 public equation broad posterior
- H042 Q2 phase route
- H088 dual state toxic gate
- H010 objective S1/S4 failure
- E323 null-common residual failure
- H145 Q3 repair shared-loss branch

결과:

- changed cells: 160
- changed rows: 117
- base listener robust mean: -0.009060
- base listener robust max: -0.003038
- semantic listener robust mean: -0.007628
- semantic listener robust max: -0.004325
- H088 cosine: 0.000066
- upload safe: true

known-loss cosine:

- vs H012: -0.1447
- vs H042: -0.1070
- vs H088: 0.000066
- vs H010: -0.1158
- vs E323: -0.1167
- vs H145: -0.00318

해석:

H158은 이번 세트에서 가장 큰 jackpot 후보다.
단순히 listener metric을 키운 게 아니라, known public-loss action과 거의 직교하거나 반대 방향이 되도록 sparse support 안에서 정리했다.

## 제출 우선순위

1. `submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv`
   - 가장 큰 bet.
   - H154/H155의 공통 hidden action field가 진짜라면 가장 크게 움직일 수 있다.
   - 실패하면 “listener stress + sparse known-loss nulling만으로 public equation을 복원할 수 없다”는 결론이 강해진다.

2. `submission_h156_combo_h154_h155_a1.3_b1.3_30075624_uploadsafe.csv`
   - H158보다 덜 변형된 후보.
   - H154/H155 결합 자체를 검증하는 용도다.

3. `submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv`
   - 단독 성능 후보라기보다 H061 posterior가 H154 semantic listener 안에서 살아남는지 보는 diagnostic이다.

## 이번에 알게 된 것

1. H061 posterior는 H154 semantic listener로 거르면 살아남는다.
   - broad posterior는 위험하지만, listener-permitted cell만 쓰면 all-stress-clean 후보가 많이 나온다.

2. H154와 H155는 같은 축이 아니다.
   - cosine 0.687이라 충분히 겹치지만, 완전히 중복은 아니다.
   - 그래서 합치면 stress metric이 크게 좋아진다.

3. known-loss projection은 dense하게 하면 안 된다.
   - H157은 1024 cells로 퍼져서 실패 가설로 처리했다.
   - public loss를 지우려면 sparse listener support 안에서만 해야 한다.

4. H158은 “0.0001 개선 보험형”이 아니다.
   - 160 cells / 117 rows를 움직이고, H057 이후 남은 hidden equation을 강하게 다시 쓰는 후보다.

## Public LB 해석 계획

H158이 좋아지면:

```text
H057 이후 병목은 새 모델 capacity가 아니라
listener-safe sparse support 안에서 public-loss action 성분을 제거하는 assignment 문제다.
```

H158이 나빠지면:

```text
local semantic listener와 known-loss nulling은 offline stress에는 맞지만,
실제 public subset/action response는 더 좁은 hidden subset 또는 다른 target route에 지배된다.
```

H156이 H158보다 좋으면:

```text
known-loss projection이 과했다.
H154+H061 posterior 결합 자체는 맞지만, loss-axis 제거는 public equation을 손상시켰다.
```

H155만 좋으면:

```text
H154 source-consensus보다 H061 posterior residual이 더 직접적인 public sensor였고,
강한 combo/amplification이 tail log loss를 망쳤다.
```

## 재현 코드

```bash
python3 hsjepa_jackpot/h155_h158_posterior_lossnull_jackpot.py
```

이 코드는 다음 파일을 재생성한다.

- `submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv`
- `submission_h156_combo_h154_h155_a1.3_b1.3_30075624_uploadsafe.csv`
- `submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv`
- `hsjepa_jackpot/outputs/h155_h158_repro_readout.json`

