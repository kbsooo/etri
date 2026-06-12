# Core OOF Action-Health Benchmark

## 한 줄 요약

public LB, 기존 submission, action teacher를 전혀 쓰지 않고 OG train 내부 future split에서 비교했을 때, 가장 좋은 구조는 단일 HS-JEPA decoder가 아니라 target/listener별로 서로 다른 representation을 선택하는 route selector였다.

## 왜 중요한가

이전 실험들은 HS-JEPA core가 다음을 할 수 있음을 보였다.

- row-state frontier 일부를 public score 없이 재발견한다.
- action-health score가 성공/실패 action field를 어느 정도 구분한다.

하지만 아직 약한 질문이 남아 있었다.

```text
그럼 HS-JEPA core 자체가 실제 label 예측에서도 좋아지는가?
그리고 좋아진다면 어떤 방식으로 좋아지는가?
```

이 실험은 이 질문을 train 내부 OOF로 직접 검증한다.

## 사용하지 않은 정보

이 실험은 다음을 쓰지 않는다.

- public LB score ledger
- 기존 submission probability
- 기존 성공 action teacher
- row-state frontier file
- active-silence frontier file

즉 대회 leaderboard 주변을 맞추는 실험이 아니라, OG 데이터만으로 HS-JEPA 구조가 실제 future-label logloss를 낮추는지 보는 실험이다.

## 코드

```bash
python3 sleep_competition_adapter/core_oof_action_health_benchmark.py
```

주요 산출물:

- `sleep_competition_adapter/outputs/core_oof_action_health_benchmark/core_oof_action_health_readout.json`
- `sleep_competition_adapter/outputs/core_oof_action_health_benchmark/core_oof_action_health_score_table.csv`
- `sleep_competition_adapter/outputs/core_oof_action_health_benchmark/core_oof_action_health_oof_audit.csv`
- `sleep_competition_adapter/outputs/core_oof_action_health_benchmark/core_oof_action_health_test_action_audit.csv`
- `submission_hsjepa_core_oof_action_health_fea05ac1_uploadsafe.csv`

## 비교한 구조

비교군:

| model | 의미 |
| --- | --- |
| global prior | 전체 train target prevalence |
| subject prior | subject별 과거 label prevalence |
| raw lifelog KNN blend | raw lifelog feature nearest-neighbor |
| core KNN blend | HS-JEPA human-state latent nearest-neighbor |
| HS-JEPA action-health release | core KNN action을 listener/action-health로 release |
| raw action + core health | raw lifelog action을 core support로 gate |
| target listener route selector | target별로 가장 적절한 listener route 선택 |

## 핵심 결과

temporal subject-tail OOF 기준:

| model | mean logloss |
| --- | ---: |
| subject prior | 0.650566 |
| raw lifelog KNN blend | 0.636997 |
| core KNN blend | 0.638266 |
| best single HS-JEPA action-health | 0.644184 |
| target listener route selector | 0.629398 |

target listener route selector는 subject prior 대비 `-0.021168`, raw lifelog KNN 대비 `-0.007599` 개선됐다.

## 발견한 listener route

| target | selected route | 해석 |
| --- | --- | --- |
| Q1 | core KNN blend | 주관 만족도는 raw activity보다 hidden human-state geometry가 더 잘 잡는다. |
| Q2 | global prior | 수면 개입 target은 현재 OOF에서 개인/근접 이웃 조정이 오히려 toxic하다. |
| Q3 | global prior | Q3는 local history를 강하게 믿으면 미래 tail에서 무너진다. |
| S1 | raw lifelog KNN blend | objective stage 일부는 raw lifelog proximity가 가장 직접적이다. |
| S2 | HS-JEPA action-health strict release | S2는 core action-health가 실제로 release 가치가 있는 target이다. |
| S3 | raw lifelog KNN blend | S3는 raw behavior/sensor proximity가 core보다 안정적이다. |
| S4 | core KNN blend | S4는 hidden-state geometry가 raw보다 약간 더 맞다. |

## 논문적 의미

이 실험은 HS-JEPA를 다음처럼 과장하면 안 된다는 것을 보여준다.

```text
human-state latent 하나를 만들면 모든 label을 직접 더 잘 맞힌다.
```

대신 더 정확한 주장은 다음이다.

```text
HS-JEPA는 인간 생활 로그를 hidden state geometry로 바꾸고,
각 target/listener가 어떤 representation을 들어야 하는지 route를 선택한다.
일부 listener는 core geometry를 듣고,
일부 listener는 raw lifelog proximity를 듣고,
일부 listener는 prior가 더 안전하며,
일부 listener만 action-health release를 허용한다.
```

즉 HS-JEPA의 핵심은 `one encoder -> one classifier`가 아니다.

```text
partial human context
  -> hidden human-state representation
  -> listener-specific route selection
  -> action-health release only where safe
```

## 현재 한계

- subject-holdout에서는 route selector가 raw KNN과 거의 동률이다.
- 즉 이 route는 cross-person generality보다 same-subject future prediction에 더 강하다.
- single HS-JEPA action-health decoder는 raw KNN보다 약하다.
- S2 외에는 action-health release가 선택되지 않았다.

## 다음 질문

가장 중요한 다음 질문은 다음이다.

```text
target listener route를 hand-selected OOF rule이 아니라,
HS-JEPA core가 context-dependent하게 sample별로 선택할 수 있는가?
```

이것이 풀리면 HS-JEPA는 고정 target별 route selector에서 더 일반적인 architecture로 올라간다.
