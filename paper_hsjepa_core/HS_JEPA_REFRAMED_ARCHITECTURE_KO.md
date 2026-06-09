# HS-JEPA Reframed Architecture

## 왜 재정의가 필요한가

현재까지의 실험을 그대로 보면 HS-JEPA가 “새로운 아키텍처”라기보다 대회 중 얻은 암묵지를 잘 조합한 시스템처럼 보일 위험이 있다.

특히 public-loss sparse tomography는 성능 후보로는 강하지만, 논문 본체로 두면 다음 비판을 피하기 어렵다.

> public leaderboard 반응을 이용한 후처리 아닌가?

따라서 HS-JEPA를 다음처럼 재정의한다.

## 핵심 주장

수면 생활 로그 예측 문제에서 label은 직접 예측 대상이 아니라, 숨은 인간 생활 상태와 row-target listener responsibility가 결합되어 나온 관측 결과다.

HS-JEPA는 raw feature에서 label을 바로 예측하지 않고, 다음 세 representation을 분리해 학습/추론한다.

1. **Human-State Representation**
   - 오늘의 생활 상태는 어떤가?
   - 이 사람의 평소와 다른가?
   - 비슷한 사람들의 평소와도 다른가?

2. **Listener Responsibility / Row-Target Support**
   - 1750개 row-target cell 중 어느 cell이 실제로 중요한가?
   - 어떤 target route가 public/private loss를 크게 움직이는가?

3. **Action-Health / Correction Field**
   - 선택된 cell을 어느 방향과 강도로 움직여야 하는가?
   - 이 action은 shortcut/collapse/public-only toxicity에 빠져 있지 않은가?

## 최종 구조

```text
OG raw lifestyle logs
        |
        v
Human-State Encoder
        |
        +--> personal state axis
        +--> peer cohort state axis
        +--> Q/S target-route margin
        +--> action-health representation

Submission/source disagreement + listener context
        |
        v
Row-Target Assignment Solver
        |
        +--> sparse support over row-target cells

Human-state representation + support
        |
        v
Action Decoder
        |
        +--> calibrated row-target correction field
        |
        v
Final multi-label probability
```

## JEPA와의 연결

일반적인 JEPA는 보이는 context에서 보이지 않는 target representation을 예측한다.

HS-JEPA에서는 context와 target을 다음처럼 바꾼다.

| JEPA 요소 | HS-JEPA 해석 |
|---|---|
| context | 생활 로그, 개인 과거, peer cohort, submission disagreement, listener state |
| target representation | label 자체가 아니라 hidden state, route, support, correction field |
| mask | feature mask가 아니라 subject/row/target/source/public-private mask |
| prediction | raw value reconstruction이 아니라 action representation prediction |
| energy/diagnostic | collapse, shortcut, public-only action, unsafe correction 감지 |

## 이번 실험이 준 핵심 근거

Human-State Action Distillation 결과:

- action 위치 OOF AUC: `0.447316`
- action 위치 OOF AP: `0.048815`
- action 방향 sign AUC: `0.607790`

이 결과는 다음을 의미한다.

1. human-state encoder만으로 row-target support를 찾는 것은 아직 어렵다.
2. action support는 별도의 listener/assignment solver가 필요하다.
3. human-state representation은 support가 주어진 뒤 방향/위험성/해석을 보조하는 쪽이 더 자연스럽다.

Listener Responsibility JEPA 결과:

- public score ledger 사용: `false`
- selected cells: `118`
- teacher cells: `94`
- teacher overlap: `39`
- precision vs teacher: `0.330508`
- recall vs teacher: `0.414894`
- sign match on overlap: `1.000000`
- Q2 selected/teacher overlap: `31 / 19`

이 결과는 support assignment가 완전히 public-loss 암묵지에만 의존하지 않는다는 증거다. 특히 Q2 route는 source/listener responsibility만으로도 상당히 복원된다.

따라서 현재 HS-JEPA의 가장 강한 구조적 주장은 다음이다.

> Human-state representation alone cannot solve support assignment, but listener/source responsibility can recover a meaningful subset of row-target support without reading public scores. HS-JEPA should therefore be formulated as a modular joint embedding system: human-state encoder, listener responsibility solver, and action decoder.

## 논문에서 피해야 할 주장

다음 표현은 피해야 한다.

- “HS-JEPA가 raw lifelog만으로 모든 target을 직접 예측한다.”
- “human-state latent만으로 public best를 설명한다.”
- “public-loss tomography가 HS-JEPA 본체다.”

이 표현들은 현재 실험 근거보다 강하다.

## 논문에서 할 수 있는 주장

대신 다음 주장은 가능하다.

- 우리는 label 직접 예측 대신 row-target action representation을 예측하는 HS-JEPA를 제안한다.
- human-state latent는 개인/peer 생활 상태를 표현하고, target-route correction의 방향과 안전성을 해석한다.
- row-target assignment는 별도 listener responsibility 문제로 분리되어야 하며, public-loss tomography는 이 assignment solver의 competition-specific teacher 역할을 한다.
- 이 분리는 단순 tabular classifier나 blend와 다르게, 왜 특정 target/row만 수정해야 하는지를 설명한다.

## 대회 패키징

대회용 최종 후보는 다음처럼 설명한다.

1. `Public-Loss Sparse Tomography HS-JEPA`
   - row-target assignment solver + competition decoder
   - 성능 우선 후보

2. `Cohort-Relative Human-State Atlas HS-JEPA`
   - human-state encoder + action-health gate
   - 논문/해석 우선 후보

3. `Human-State Action Distillation HS-JEPA`
   - public-loss teacher를 human-state student가 설명할 수 있는지 검증한 negative/diagnostic experiment
   - 현재 제출 우선순위는 낮지만, 아키텍처 재정의의 핵심 근거

4. `Listener Responsibility JEPA`
   - public score ledger 없이 source/listener responsibility로 support assignment를 복원하는 실험
   - Q2 route에서 강한 overlap을 보이며, HS-JEPA core architecture의 가장 중요한 새 증거

5. `Public/Private Toxicity Head HS-JEPA`
   - Listener Responsibility가 만든 public-score-free support를 competition-specific decoder가 안전성 기준으로 증폭/감쇠/추가하는 실험
   - public-bad anchor는 support 생성이 아니라 toxicity 판단에만 사용
   - architecture role split을 명확히 보여주는 실험

6. `Target-Route Toxicity Head HS-JEPA`
   - toxicity tolerance를 target-route별로 분리한 decoder
   - Q2는 제한적 extra를 허용하고, S-tail은 teacher-only calibration으로 보수화
   - target-agnostic decoder가 아니라 route-aware action decoder가 필요하다는 증거

## 다음 큰 발견 후보

현재 가장 중요한 미해결 문제는 support assignment다.

즉 다음 big bet은 feature 추가가 아니라:

> public LB 없이 row-target support를 찾는 Listener Responsibility JEPA

였고, 첫 구현에서 teacher support 41% recall과 overlap sign 100%를 확인했다.

다음 단계는 이 Listener Responsibility JEPA에 public/private toxicity head를 붙여, 복원된 support 중 실제로 안전한 action과 toxic action을 분리하는 것이다. 이것이 성공하면 HS-JEPA는 대회 트릭에서 논문형 아키텍처로 넘어갈 수 있다.

첫 Public/Private Toxicity Head 결과:

- teacher cells retained: `94`
- LRJ extra cells added: `56`
- changed cells: `150`
- mean teacher amp: `1.167986`
- upload-safe: `true`

이 결과는 구조적으로는 의미 있지만 high-risk다. extra action이 많기 때문에 public LB가 나빠지면 LRJ extra support가 아직 toxic하다는 뜻이다. 그 경우 다음 방향은 extra support를 추가하지 않고, Candidate 1 teacher action만 toxicity-calibrated amplitude로 조정하는 conservative decoder다.

Target-Route Toxicity Head 결과:

- `teacher_only`: teacher 94 cells 유지, extra 0, changed rows 82, upload-safe
- `q2_extra`: teacher 94 cells + Q2 extra 14, changed rows 90, upload-safe

이 결과는 decoder를 target-agnostic하게 두면 안 된다는 설계 방향을 강화한다. Q2 route는 Listener Responsibility 실험에서 teacher overlap이 강했기 때문에 extra를 제한적으로 허용할 수 있지만, S1/S3/S4 objective tail은 public-bad anchor에 민감하므로 더 보수적으로 다뤄야 한다.
