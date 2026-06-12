# Raw-KNN Failure Detector

## 한 줄 요약

HS-JEPA route-risk signal은 full contextual router로 넓게 쓰면 raw lifelog KNN을 넘지 못했지만, raw KNN을 기본값으로 두고 실패 가능성이 큰 row-target cell만 다른 listener route로 전환하면 OOF Log Loss를 낮췄다.

## 왜 중요한가

직전 실험인 `Contextual Listener Route Selector`는 다음을 보여줬다.

```text
sample-level contextual router는 fixed target route보다 낫다.
하지만 raw lifelog KNN보다 안정적으로 좋지는 않다.
```

이 결과는 HS-JEPA를 full router로 과장하면 안 된다는 뜻이었다.

그래서 질문을 바꿨다.

```text
HS-JEPA가 모든 row-target route를 고르지 않아도 된다.
대신 raw KNN이 실패할 것 같은 cell만 찾을 수 있는가?
```

이 실험은 이 질문에 대한 첫 양성 증거다.

## 사용하지 않은 정보

이 실험은 다음을 쓰지 않는다.

- public LB score ledger
- 기존 submission probability
- 기존 성공 action teacher
- row-state frontier file
- active-silence frontier file

또한 leakage guard를 넣었다.

feature column에 다음 정보가 들어가면 스크립트가 실패한다.

- `loss`
- `gain`
- `raw_loss`
- `y`
- `loss__*`
- `oracle_*`

## 코드

```bash
python3 sleep_competition_adapter/raw_knn_failure_detector.py
```

주요 산출물:

- `sleep_competition_adapter/outputs/raw_knn_failure_detector/raw_knn_failure_detector_readout.json`
- `sleep_competition_adapter/outputs/raw_knn_failure_detector/raw_knn_failure_detector_oof_metrics.csv`
- `sleep_competition_adapter/outputs/raw_knn_failure_detector/raw_knn_failure_detector_oof_candidate_cells.csv`
- `sleep_competition_adapter/outputs/raw_knn_failure_detector/raw_knn_failure_detector_oof_gain_pairs.csv`
- `sleep_competition_adapter/outputs/raw_knn_failure_detector/raw_knn_failure_detector_test_actions.csv`
- `submission_hsjepa_raw_knn_failure_detector_2a097b16_uploadsafe.csv`

## 방법

1. temporal subject-tail OOF split을 만든다.
2. 각 row-target cell에서 raw KNN과 여러 listener route expert의 prediction을 만든다.
3. OOF train cell에서 다음 gain을 정의한다.

```text
gain = raw_knn_cell_loss - alternative_expert_cell_loss
```

4. HS-JEPA context, expert disagreement, outlier geometry, expert family feature로 gain regressor를 학습한다.
5. held-out subject에서 predicted gain이 높은 cell만 raw KNN에서 벗어난다.

즉 이 모듈은 full router가 아니다.

```text
default route = raw lifelog KNN
override route = only if HS-JEPA failure detector predicts high gain
```

## 결과

OOF 기준:

| model | policy | logloss | switched cells |
| --- | --- | ---: | ---: |
| raw KNN baseline | none | 0.636997 | 0 |
| raw-KNN failure detector | gradient boosted gain, top 4% | 0.632612 | 29 |

개선:

```text
0.636997 -> 0.632612
delta = -0.004385
```

test candidate에서는 1750개 row-target cell 중 70개 cell만 raw KNN에서 벗어났다.

test selected expert counts:

| selected expert | cells |
| --- | ---: |
| raw KNN | 1680 |
| subject prior | 32 |
| global prior | 17 |
| core KNN | 9 |
| HS-JEPA action-health high-margin | 6 |
| HS-JEPA action-health wide | 2 |
| HS-JEPA action-health strict | 2 |
| HS-JEPA action-health balanced | 1 |
| raw action + core health wide | 1 |

## 해석

이 실험은 HS-JEPA의 현재 가장 설득력 있는 역할을 바꾼다.

약한 주장:

```text
HS-JEPA core가 raw lifelog KNN보다 항상 더 좋은 predictor다.
```

현재 증거에 맞는 강한 주장:

```text
HS-JEPA core는 raw lifelog KNN이 실패할 조건을 감지하고,
그때만 listener route를 override하는 failure-aware architecture다.
```

즉 HS-JEPA는 모든 sample을 직접 예측하는 모델보다,
강한 기본 예측기의 실패 조건을 감지하는 meta-world-model로 쓸 때 더 안정적이다.

## 논문적 contribution

이 결과는 HS-JEPA를 다음 구조로 정립하게 만든다.

```text
raw lifelog proximity predictor
  -> HS-JEPA human-state / route-risk representation
  -> raw-KNN failure detector
  -> sparse listener override
  -> final prediction
```

JEPA 관점에서는 다음과 같다.

```text
visible context: human-state geometry, raw/core disagreement, cohort outlier, route family
hidden target representation: whether raw KNN will fail on this row-target cell
prediction: sparse override decision, not raw label reconstruction
```

## 다음 질문

다음 breakthrough 질문은 다음이다.

```text
raw-KNN failure detector가 찾은 override cell이 public/private에서도 안전한가?
```

이제 action-health decoder는 모든 action을 판단하는 장치가 아니라, detector가 고른 sparse override cell의 toxic 여부를 검증하는 장치로 붙이는 것이 맞다.
