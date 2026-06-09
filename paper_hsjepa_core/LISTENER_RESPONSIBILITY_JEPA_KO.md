# Listener Responsibility JEPA

## 실험 목적

직전 Human-State Action Distillation 실험에서 중요한 병목이 드러났다.

OG human-state context만으로는 어느 row-target cell을 움직일지 찾지 못했다.

그래서 이번 실험은 질문을 바꿨다.

> support assignment는 human-state encoder의 일이 아니라, listener/source responsibility를 예측하는 별도 JEPA module의 일 아닐까?

즉 이번 실험은 public LB score ledger를 읽지 않고, source/listener consensus와 OG human-state context만으로 row-target support를 고르는 solver를 만든다.

## 핵심 한 줄

public score 없이도 Candidate 1 teacher cell 94개 중 39개를 회수했고, 겹친 39개 cell의 sign은 100% 일치했다.

## 입력

이 solver가 보는 context:

1. **Source responsibility**
   - 여러 source submission이 같은 row-target/sign을 지지하는가?
   - source support 수
   - source move 평균/최대/분산
   - source consensus score

2. **Listener responsibility**
   - semantic listener benefit
   - base listener benefit
   - listener benefit rank
   - hard-world shortcut alignment penalty

3. **Human-state context**
   - cohort outlier score
   - personal/peer normal distance
   - peer-only toxicity
   - target peer margin
   - Q/S route margin
   - base probability uncertainty

중요한 점:

- `data_analytics/hsjepa_public_score_ledger.csv`를 읽지 않는다.
- public LB 점수는 solver scoring에 사용하지 않는다.
- Candidate 1은 실행 후 teacher overlap 평가에만 사용한다.

## 코드

```bash
python3 paper_hsjepa_core/listener_responsibility_jepa.py
```

## 산출물

- 제출 후보:
  - `submission_hsjepa_listener_responsibility_9990e658_uploadsafe.csv`

- 세부 산출물:
  - `paper_hsjepa_core/outputs/listener_responsibility_jepa/listener_responsibility_readout.json`
  - `paper_hsjepa_core/outputs/listener_responsibility_jepa/listener_responsibility_ranked_cells.csv`
  - `paper_hsjepa_core/outputs/listener_responsibility_jepa/listener_responsibility_sign_frame.csv`
  - `paper_hsjepa_core/outputs/listener_responsibility_jepa/listener_responsibility_action_audit.csv`

## 결과

Teacher는 최종 후보 1인 Public-Loss Sparse Tomography HS-JEPA다.

| 항목 | 값 |
|---|---:|
| selected cells | 118 |
| teacher cells | 94 |
| teacher overlap | 39 |
| precision vs teacher | 0.3305 |
| recall vs teacher | 0.4149 |
| sign match on overlap | 1.0000 |
| changed rows | 90 |
| upload-safe | true |

Target별 overlap:

| target | selected | teacher overlap |
|---|---:|---:|
| Q1 | 4 | 1 |
| Q2 | 31 | 19 |
| Q3 | 14 | 3 |
| S1 | 14 | 4 |
| S2 | 20 | 5 |
| S3 | 18 | 5 |
| S4 | 17 | 2 |

가장 중요한 결과는 Q2다.

Q2는 31개 선택 중 19개가 teacher와 겹쳤고, 겹친 cell의 sign이 모두 맞았다.

이는 Q2 route가 단순 public-loss 암묵지만이 아니라 source/listener responsibility 구조에도 강하게 남아 있다는 뜻이다.

## Listener diagnostic

| Metric | Value |
|---|---:|
| base listener mean delta | -0.038410 |
| base listener max delta | -0.006685 |
| base listener negative count | 10 |
| semantic listener mean delta | -0.029228 |
| semantic listener max delta | -0.004400 |
| semantic listener negative count | 10 |
| hard-world cosine | 0.042439 |

Candidate 1보다 changed cells가 많고 listener delta도 더 크다. 이것은 public LB에서 반드시 좋다는 뜻은 아니다. 다만 listener responsibility 관점에서는 강한 action field다.

## 해석

이 실험은 중요한 중간 결론을 준다.

Human-state encoder만으로 support를 찾으려 하면 실패했다.

하지만 source/listener responsibility를 넣으면 public score 없이도 teacher support의 41%를 회수했다. 특히 겹친 support의 sign이 100% 맞았다는 것은 route direction이 우연이 아니라는 강한 신호다.

따라서 HS-JEPA는 다음처럼 정리하는 것이 맞다.

```text
Human-State Encoder
    -> 상태/위험성/route context 제공

Listener Responsibility JEPA
    -> 어느 row-target/sign을 들어야 하는지 support assignment

Action Decoder
    -> 선택된 support를 calibrated probability correction으로 번역
```

## 제출 후보로서의 의미

이 파일은 정보량이 큰 big-bet이다.

좋아지면:

- public LB 없이도 support assignment를 상당히 복원했다는 뜻이다.
- HS-JEPA를 competition trick이 아니라 listener responsibility architecture로 주장할 수 있다.

나빠지면:

- source/listener responsibility가 public-loss teacher와 일부 겹치긴 하지만, public/private action toxicity를 충분히 구분하지 못한다는 뜻이다.
- 이 경우 Listener Responsibility JEPA는 support 후보 generator로 남기고, 최종 decoder에는 public/private toxicity head가 필요하다.

## 현재 판단

제출 슬롯이 매우 제한되어 있다면 Candidate 1이 우선이다.

하지만 논문/아키텍처 관점에서 가장 중요한 새 후보는 이 Listener Responsibility JEPA다. 이유는 public score ledger 없이 support assignment를 일부 복원했다는 점 때문이다.
