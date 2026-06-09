# Human-State Action Distillation HS-JEPA

## 실험 목적

우리가 지금 가진 가장 강한 후보는 public-loss sparse tomography 기반이다. 성능적으로는 의미가 있지만, 그대로 논문에 쓰면 “기존 제출 결과와 public LB를 잘 이용한 대회 전략”처럼 보일 수 있다.

그래서 이 실험은 더 근본적인 질문을 던졌다.

> public-loss teacher가 찾은 row-target action field를 OG human-state context만으로 설명할 수 있는가?

만약 설명할 수 있다면, HS-JEPA는 단순 제출 트릭이 아니라 실제 human-state representation architecture라고 주장할 수 있다.

## 실험 구조

### 1. Teacher

Teacher는 최종 후보 1이다.

- 파일: `submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv`
- 현재 best 대비 changed cells: `94`
- 의미: public-loss sensor와 listener diagnostic을 통과한 sparse row-target action field

### 2. Student context

Student는 public score를 직접 보지 않는다. OG raw lifelog에서 만든 human-state atlas만 본다.

사용 context:

- 개인 normal distance
- peer cohort normal distance
- subject/peer axis disagreement
- cohort outlier score
- target peer margin
- Q/S group margin
- atlas action-health
- base probability / uncertainty
- target identity
- calendar position
- PCA human-state latent

### 3. Student task

250 rows x 7 targets = 1750개 cell에 대해 다음을 예측한다.

1. 이 cell이 teacher action을 받았는가?
2. action 방향은 positive인가 negative인가?
3. logit 이동 크기는 어느 정도인가?

검증은 row-group OOF로 했다. 같은 row의 다른 target이 train/valid에 섞이지 않도록 row 단위로 fold를 나눈다.

## 결과

핵심 숫자:

| Metric | Value |
|---|---:|
| teacher action rate | 0.053714 |
| OOF action-location AUC | 0.447316 |
| OOF action-location AP | 0.048815 |
| OOF move RMSE all cells | 0.219960 |
| OOF move RMSE teacher-action cells | 0.927353 |
| OOF sign AUC on action cells | 0.607790 |

## 해석

가장 중요한 결론은 부정적이다.

OG human-state context는 teacher가 고른 action 위치를 맞히지 못했다. AUC가 0.5보다 낮고 AP도 teacher action prior보다 낮다.

즉 다음 주장은 아직 하면 안 된다.

> HS-JEPA human-state encoder만으로 어느 row-target cell을 고칠지 찾을 수 있다.

대신 할 수 있는 주장은 이쪽이다.

> Human-state encoder는 action support를 단독으로 찾지는 못하지만, support가 정해진 뒤 action 방향과 위험성을 해석하는 데 약한 신호를 제공한다.

근거는 action cell 내부 sign AUC가 `0.607790`이라는 점이다. 강한 성능 근거는 아니지만, 완전한 noise는 아니다.

## 생성된 diagnostic submission

이 실험은 student가 강하게 지지하는 cell을 확장한 후보도 만들었다.

- 파일: `submission_hsjepa_paper_student_action_distill_8f097c06_uploadsafe.csv`
- changed cells: `314`
- teacher keep cells: `94`
- student expansion cells: `220`
- upload-safe: `true`

이 파일은 현재 제출 우선순위가 낮다. 이유는 action-location OOF가 약하기 때문에 student expansion의 근거가 부족하다.

## 논문형 HS-JEPA에 주는 교훈

처음에는 HS-JEPA를 하나의 큰 encoder-decoder처럼 말하고 싶었다.

```text
raw lifestyle logs
-> human-state latent
-> target prediction
```

하지만 이번 실험 결과 이 구조는 너무 단순하다.

더 맞는 구조는 다음이다.

```text
raw lifestyle logs
-> Human-State Encoder
-> state/route/health representation

submission response + listener context
-> Row-Target Assignment Solver
-> action support

human-state representation + action support
-> Action Decoder
-> calibrated correction field
```

즉 HS-JEPA의 본질은 “human-state encoder 하나로 모든 것을 맞힌다”가 아니라:

> human-state representation, listener responsibility, row-target action을 joint embedding space에서 분리하고 다시 결합하는 architecture

라고 보는 것이 더 정확하다.

## 앞으로의 big-bet 방향

다음 큰 발견은 human-state feature를 더 늘리는 데서 나오기보다, support assignment solver를 논문형으로 만드는 데서 나올 가능성이 크다.

후보:

1. **Listener Responsibility JEPA**
   - public-loss tomography를 teacher로 쓰되, public LB 없이도 source disagreement와 listener geometry만으로 support를 예측한다.

2. **Two-Stage HS-JEPA**
   - Stage 1: row-target support assignment
   - Stage 2: human-state action direction/strength decoder

3. **Counterfactual Route JEPA**
   - 특정 target route를 mask하고, Q/S group context로 missing route representation을 예측한다.

4. **Public/Private Decoupled Decoder**
   - public sensor에 잘 맞는 action과 private에 안전할 action을 별도 head로 분리한다.

## 결론

이번 실험은 제출용 jackpot은 아니다.

하지만 논문 방향에는 매우 중요하다. HS-JEPA가 무엇을 할 수 있고, 무엇을 아직 못 하는지 선을 그어줬기 때문이다.

현재 결론:

- public-loss sparse tomography는 competition decoder로 남긴다.
- human-state/cohort atlas는 architecture representation으로 남긴다.
- 둘 사이를 연결하는 핵심 미해결 문제는 row-target support assignment다.
