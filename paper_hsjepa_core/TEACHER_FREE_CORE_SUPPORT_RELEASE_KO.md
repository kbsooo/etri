# Teacher-Free Core Support Release

## 한 줄 요약

이 실험은 HS-JEPA core가 기존 성공 action field를 teacher로 보지 않고도, OG 생활 로그에서 만든 human-state geometry만으로 위험/기회 row를 일부 찾아낼 수 있는지 검증한다.

## 왜 필요한가

지금까지 가장 강한 대회 성능은 public-equation prior, row-state vector frontier, active-silence 같은 competition adapter의 암묵지가 많이 들어간 결과였다.

논문으로 HS-JEPA를 주장하려면 다음 질문에 답해야 한다.

```text
HS-JEPA core 자체가 인간 생활 상태를 더 잘 표현한다는 증거가 있는가?
아니면 우리는 그저 public feedback 주변을 잘 조정한 것인가?
```

Teacher-Free Core Support Release는 이 질문을 직접 찌른다.

## 사용한 정보

support score를 만들 때 사용한 정보:

- OG lifelog-derived human-state latent
- personal/cohort outlier score
- train label nearest-neighbor target margin
- calendar edge signal

support score를 만들 때 사용하지 않은 정보:

- public LB score ledger
- 기존 성공/실패 action teacher
- row-state frontier 파일의 action 위치
- active-silence frontier 파일의 action 위치

단, 기존 frontier 파일들은 마지막에 overlap evaluation 용도로만 사용했다. 즉 “정답을 보고 고른 support”가 아니라 “core가 고른 support가 과거 성공 row와 얼마나 겹치는지”를 사후 평가한 것이다.

## 코드

```bash
python3 sleep_competition_adapter/teacher_free_core_support_release.py
```

주요 산출물:

- `sleep_competition_adapter/outputs/teacher_free_core_support_release/teacher_free_core_support_readout.json`
- `sleep_competition_adapter/outputs/teacher_free_core_support_release/teacher_free_core_row_support.csv`
- `sleep_competition_adapter/outputs/teacher_free_core_support_release/teacher_free_frontier_overlap.csv`
- `sleep_competition_adapter/outputs/teacher_free_core_support_release/teacher_free_core_support_action_audit.csv`
- `submission_hsjepa_teacher_free_core_support_release_8d9899fb_uploadsafe.csv`

## 실험 구조

```text
OG lifelog table
  -> HS-JEPA human-state latent
  -> personal / cohort outlier geometry
  -> train-label nearest-neighbor target margin
  -> teacher-free row support score
  -> target별 outlier law
  -> row-target correction release
```

이 실험은 완전한 end-to-end label predictor가 아니다.

더 정확한 역할은 다음이다.

```text
core representation이 action을 직접 낼 수 있는가?
아니면 action 후보를 걸러낼 support geometry까지만 제공하는가?
```

## 결과

생성된 후보:

```text
submission_hsjepa_teacher_free_core_support_release_8d9899fb_uploadsafe.csv
```

파일 안전성:

- rows: 250
- columns: sample submission과 동일
- NaN: 0
- duplicate keys: 0
- probability range: `[0.00003294, 0.99998030]`

action 규모:

- changed rows: 40
- changed cells: 160
- mean abs logit move: 0.097056
- max abs logit move: 0.271152

target별 action 수:

| target | changed cells |
| --- | ---: |
| S4 | 40 |
| Q2 | 34 |
| S2 | 25 |
| S1 | 22 |
| S3 | 19 |
| Q3 | 18 |
| Q1 | 2 |

## Row-State Frontier 재발견 능력

teacher-free support top 28%에서:

- row-state vector frontier rows: 45개 중 16개 회수
- recall: 0.3556
- precision: 0.2286

| reference | top_fraction | k | reference_rows | overlap_rows | recall | precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| frontier active-silence rows | 0.10 | 25 | 45 | 5 | 0.1111 | 0.2000 |
| frontier active-silence rows | 0.15 | 38 | 45 | 6 | 0.1333 | 0.1579 |
| frontier active-silence rows | 0.18 | 45 | 45 | 8 | 0.1778 | 0.1778 |
| frontier active-silence rows | 0.22 | 55 | 45 | 11 | 0.2444 | 0.2000 |
| frontier active-silence rows | 0.28 | 70 | 45 | 16 | 0.3556 | 0.2286 |

## 해석

이 결과는 두 가지를 동시에 말한다.

첫째, HS-JEPA core는 완전히 무력하지 않다. public score나 action teacher 없이도 기존 row-state frontier의 일부를 다시 찾았다. 이는 core representation이 단순 feature engineering이 아니라 row support geometry를 어느 정도 담고 있다는 증거다.

둘째, HS-JEPA core만으로는 아직 action-grade decoder가 아니다. top 28%에서도 recall은 35.6%, precision은 22.9%다. 즉 core가 “어디가 수상한지”는 일부 말하지만, “어느 row-target을 얼마나 움직여도 안전한지”까지는 충분히 말하지 못한다.

## 논문용 주장

이 실험을 논문에 넣는다면 주장은 다음이 가장 안전하다.

```text
HS-JEPA core can recover a non-trivial subset of row-state frontier support
without using action-teacher supervision or public score feedback.
However, action-grade prediction requires a separate listener/assignment
and action-health decoder.
```

한국어로는:

```text
HS-JEPA core는 public 점수나 기존 성공 action을 보지 않고도
row-state frontier 일부를 재발견한다.
하지만 core representation만으로는 아직 안전한 row-target correction을 완성할 수 없으며,
listener assignment와 action-health decoder가 별도 모듈로 필요하다.
```

## 실패하면 무엇을 배웠는가

이 submission이 public에서 나빠지면 다음 결론이 강화된다.

```text
HS-JEPA core는 human-state support representation이지,
그 자체로 release 가능한 action decoder가 아니다.
```

즉 실패하더라도 논문 구조는 약해지지 않는다. 오히려 HS-JEPA를 다음처럼 분리해야 한다는 근거가 된다.

```text
Human-State Encoder
  -> Teacher-Free Support Geometry
  -> Listener / Row-Target Assignment
  -> Action-Health Decoder
  -> Competition Adapter
```

## 다음 질문

가장 중요한 다음 질문은 이것이다.

```text
teacher-free core support가 고른 row 중에서,
어떤 row-target action이 public/private 모두에서 독성이 낮은지
core geometry만으로 더 잘 구분할 수 있는가?
```

이 질문이 풀리면 HS-JEPA core evidence가 LB 개선과 직접 연결된다.
