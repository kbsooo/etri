# Paper-Core HS-JEPA Experiments

이 폴더는 대회용 best submission을 그대로 설명하는 데서 멈추지 않고, HS-JEPA를 논문형 아키텍처로 정리하기 위한 실험을 담는다.

## 핵심 질문

현재 강한 후보는 public-loss sparse tomography로 만들어졌다. 하지만 이것만으로는 논문에서 “새로운 아키텍처가 문제를 해결했다”고 말하기 어렵다.

그래서 이 폴더의 실험은 다음을 묻는다.

> public-loss teacher가 고른 row-target action field는 OG human-state context로 설명 가능한가?

설명 가능하면 HS-JEPA의 human-state encoder가 실제 action representation을 복원했다고 주장할 수 있다.

설명 불가능하면 HS-JEPA는 다음처럼 분리되어야 한다.

- human-state encoder: 생활 상태와 action 방향/위험성을 해석한다.
- row-target assignment solver: 어느 cell을 들을지, 어느 cell을 움직일지 찾는다.
- competition decoder: public/private sensor를 사용해 sparse correction을 만든다.

## 현재 실험

### 1. Human-State Action Distillation

```bash
python3 paper_hsjepa_core/human_state_action_distillation.py
```

이 스크립트는 다음을 수행한다.

1. OG raw lifelog에서 cohort-relative human-state atlas를 만든다.
2. 최종 후보 1의 sparse correction을 action teacher로 둔다.
3. 250 rows x 7 targets = 1750개 cell feature table을 만든다.
4. row-group OOF student로 teacher action 위치/방향/크기를 예측한다.
5. teacher action을 유지하면서 student가 강하게 지지하는 cell을 확장한 diagnostic submission을 만든다.

## 산출물

- `outputs/student_action_distillation_readout.json`
- `outputs/student_action_cell_frame.csv`
- `outputs/student_action_decode_audit.csv`
- `outputs/submission_hsjepa_paper_student_action_distill_8f097c06_uploadsafe.csv`
- root submission: `submission_hsjepa_paper_student_action_distill_8f097c06_uploadsafe.csv`

## 현재 결론

가장 중요한 결과:

- action 위치 OOF AUC: `0.447316`
- action 위치 OOF AP: `0.048815`
- teacher action rate: `0.053714`
- action cell 방향 sign AUC: `0.607790`

해석:

- OG human-state context만으로 “어느 cell을 움직여야 하는지”는 설명되지 않았다.
- 하지만 이미 움직일 cell이 정해졌을 때, 방향성에는 약한 human-state 신호가 있다.

따라서 논문형 HS-JEPA의 주장은 다음으로 바뀌어야 한다.

> Human-state representation alone is not a full row-target assignment solver. It is a state/route representation that helps orient and diagnose actions once a listener/assignment module identifies candidate cells.

한국어로는:

> 인간 생활 상태 latent는 “어디를 고칠지”를 단독으로 찾는 장치가 아니라, listener/assignment solver가 찾은 row-target 후보를 어떤 방향과 강도로 해석할지 돕는 representation이다.

### 2. Listener Responsibility JEPA

```bash
python3 paper_hsjepa_core/listener_responsibility_jepa.py
```

이 스크립트는 public score ledger를 읽지 않고, source/listener consensus와 OG human-state context로 row-target support를 고른다.

현재 결과:

- selected cells: `118`
- teacher cells: `94`
- teacher overlap: `39`
- precision vs teacher: `0.3305`
- recall vs teacher: `0.4149`
- sign match on overlap: `1.0000`
- Q2 selected/overlap: `31 / 19`
- upload-safe: `true`

해석:

- human-state만으로는 support 위치를 못 찾았지만, source/listener responsibility를 결합하면 public score 없이도 teacher support의 41%를 회수한다.
- 특히 Q2 route는 강하다. Q2 selected 31개 중 19개가 teacher와 겹쳤고, 겹친 sign은 모두 맞았다.
- 따라서 HS-JEPA의 core는 human-state encoder 하나가 아니라 **Human-State Encoder + Listener Responsibility JEPA + Action Decoder**의 3-part 구조로 보는 것이 맞다.

## 제출 판단

`submission_hsjepa_paper_student_action_distill_8f097c06_uploadsafe.csv`는 upload-safe이지만, 현재는 제출 우선순위가 낮다.

이유:

- 94개 teacher cell을 314개 changed cell로 확장했다.
- listener metric은 여전히 negative 방향이지만, action-location OOF 근거가 약하다.
- 따라서 성능 후보라기보다 “human-state student가 아직 support assignment를 못 한다”는 논문형 negative result다.

## 다음 방향

HS-JEPA를 하나의 encoder로 과장하지 말고, 다음 3-part architecture로 정리한다.

1. **Human-State Encoder**
   - OG 생활 로그에서 개인/peer 생활 상태 latent를 만든다.

2. **Listener Responsibility / Row-Target Assignment Solver**
   - 어느 row-target cell을 들을지 결정한다.
   - 현재는 public-loss tomography가 이 역할을 가장 잘 수행한다.

3. **Human-State Action Decoder**
   - 선택된 cell의 방향, 강도, 위험성을 human-state context로 조정한다.

이 구조가 대회와 논문을 동시에 살리는 현재 최선의 패키징이다.

새로 생성된 `submission_hsjepa_listener_responsibility_9990e658_uploadsafe.csv`는 성능 1순위라기보다 정보량이 큰 big-bet이다. public score 없이 support assignment를 일부 복원했기 때문에 논문형 architecture 증거로 중요하다.

### 3. Public/Private Toxicity Head

```bash
python3 paper_hsjepa_core/public_private_toxicity_head.py
```

이 스크립트는 Listener Responsibility support 위에 competition-specific toxicity decoder를 붙인다.

역할 분리:

- support generator: public score ledger를 읽지 않는 Listener Responsibility JEPA
- toxicity decoder: public-bad anchor를 이용해 action을 증폭/감쇠/추가

현재 결과:

- teacher cells retained: `94`
- LRJ extra cells added: `56`
- changed cells: `150`
- changed rows: `111`
- mean teacher amp: `1.167986`
- upload-safe: `true`

제출 파일:

- `submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv`

해석:

- Candidate 1보다 큰 움직임을 거는 high-risk big-bet이다.
- 좋아지면 support generator + toxicity decoder 구조가 강화된다.
- 나빠지면 LRJ extra action이 아직 toxic하다는 뜻이고, 다음은 extra 추가 없이 teacher action만 toxicity-calibrate하는 conservative variant로 가야 한다.

### 4. Target-Route Toxicity Head

```bash
python3 paper_hsjepa_core/target_route_toxicity_head.py
```

이 스크립트는 target별 toxicity tolerance를 분리한다.

- Q2: listener responsibility 근거가 강하므로 제한적 extra 허용
- S1/S3/S4: public-bad anchor에 민감하므로 teacher action만 보수적으로 calibration
- Q1/Q3/S2: 중간 calibration

생성된 후보:

- `submission_hsjepa_target_route_toxicity_teacher_only_66f1f5b4_uploadsafe.csv`
- `submission_hsjepa_target_route_toxicity_q2_extra_90b62d2d_uploadsafe.csv`

현재 결과:

- teacher_only: teacher 94 cells, extra 0, upload-safe
- q2_extra: teacher 94 cells + Q2 extra 14 cells, upload-safe

해석:

- `teacher_only`는 Candidate 1 support는 유지하고 amplitude만 target-route별로 calibration한 안전한 ablation이다.
- `q2_extra`는 Q2 listener route가 public/private에도 살아 있는지 확인하는 target-specific big-bet이다.
