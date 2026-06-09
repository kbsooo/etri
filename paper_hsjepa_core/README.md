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

### 5. Route-Consistency Energy

```bash
python3 paper_hsjepa_core/route_consistency_energy.py
```

이 스크립트는 train label만 사용해 Q/S target vector의 conditional route
manifold를 학습하고, candidate correction이 이 공동 구조를 깨는지 energy로
측정한다.

생성된 후보:

- `submission_hsjepa_route_energy_veto_public_private_toxicity_e08d9849_uploadsafe.csv`
- `submission_hsjepa_route_energy_veto_target_route_q2_extra_5dfa9e76_uploadsafe.csv`

현재 결과:

- `public_private_toxicity`: 150 changed cells 중 53개만 유지, route energy `0.738233 -> 0.725533`
- `target_route_q2_extra`: 108 changed cells 중 34개만 유지, route energy `0.736569 -> 0.726858`
- current best route energy: `0.728381`
- 두 후보 모두 upload-safe

해석:

- 공격적 후보일수록 Q/S 공동 label 구조를 더 많이 깨뜨린다.
- Q2 extra는 근거가 있지만 대부분이 route-consistency veto를 통과하지 못했다.
- S2 action은 상대적으로 많이 살아남아, target-route decoder가 Q2에만 고정되면 안 된다는 신호를 준다.
- 논문적으로는 HS-JEPA에 LeJEPA-style energy diagnostic을 붙인 형태다.

자세한 설명:

- `paper_hsjepa_core/ROUTE_CONSISTENCY_ENERGY_KO.md`

### 6. Energy-Utility Assignment Solver

```bash
python3 paper_hsjepa_core/energy_utility_assignment_solver.py
```

이 스크립트는 route-consistency를 사후 veto가 아니라 assignment solver 내부의
선택 기준으로 사용한다.

생성된 후보:

- `submission_hsjepa_energy_utility_solver_balanced_fd352632_uploadsafe.csv`
- `submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv`

현재 결과:

- support cells: `160`
- proposal cells: `96`
- balanced: 33 selected cells, route energy `0.727137`, upload-safe
- jackpot: 36 selected cells, route energy `0.727061`, upload-safe
- current best route energy: `0.728381`

해석:

- public utility와 route consistency가 동시에 동의하는 action은 30여 개로 압축된다.
- 반복적으로 S2 action이 많이 살아남는다.
- 다음 큰 가설은 Q2 단독 확장이 아니라 S2/Q2 route-consistent sparse action이다.

자세한 설명:

- `paper_hsjepa_core/ENERGY_UTILITY_ASSIGNMENT_SOLVER_KO.md`

### 7. Row-Bundle Transport Solver

```bash
python3 paper_hsjepa_core/row_bundle_transport_solver.py
```

이 스크립트는 cell 단위가 아니라 같은 row 안의 target bundle을 함께 평가한다.

생성된 후보:

- `submission_hsjepa_row_bundle_transport_paircore_ea3e13e3_uploadsafe.csv`
- `submission_hsjepa_row_bundle_transport_triadjackpot_294ddb94_uploadsafe.csv`

현재 결과:

- paircore: 24 bundles, 28 cells, route energy `0.727442`, upload-safe
- triadjackpot: 30 bundles, 33 cells, route energy `0.727385`, upload-safe
- Q2+S2 bundle은 선택되지 않았고, triad도 선택되지 않음
- 살아남은 pair는 주로 `S1+S2`, `S3+S4`, `Q3+S2`

해석:

- 큰 row-level vector transport 가설은 약해졌다.
- 안전한 action은 대부분 singleton이며, 일부 objective-stage micro-bundle만 살아남는다.
- HS-JEPA decoder는 bundle-heavy architecture보다 sparse micro-action solver로 보는 편이 현재 증거와 맞다.

자세한 설명:

- `paper_hsjepa_core/ROW_BUNDLE_TRANSPORT_SOLVER_KO.md`

### 8. Objective-Stage Bridge Conservation Solver

```bash
python3 paper_hsjepa_core/stage_bridge_conservation_solver.py
```

이 스크립트는 S-stage target에서 `driver action + bridge action` 구조를 테스트한다.

생성된 후보:

- `submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv`
- `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`

현재 결과:

- stagebridge: 30 bundles, 60 cells, route energy `0.725652`, upload-safe
- stagebridge_jackpot: 41 bundles, 82 cells, route energy `0.724352`, upload-safe
- 모든 selected bundle이 driver+bridge 구조
- S2가 target count `24/32`, bridge count `14/19`로 반복적인 hub 역할

해석:

- 큰 Q2/S2 row bundle은 약했지만, S-stage driver action에는 S2-hub bridge가 필요하다는 강한 신호가 나왔다.
- HS-JEPA decoder는 단순 support->action이 아니라 `driver action + route-preserving bridge` 구조로 발전할 수 있다.
- 이 실험은 현재 가장 강한 논문형 architecture evidence이자 high-risk big-bet 후보를 제공한다.

자세한 설명:

- `paper_hsjepa_core/STAGE_BRIDGE_CONSERVATION_SOLVER_KO.md`

### 9. Subjective Shadow Bridge Solver

```bash
python3 paper_hsjepa_core/subjective_shadow_bridge_solver.py
```

이 스크립트는 objective-stage bridge가 Q1 subjective satisfaction까지
전이되는지 테스트한다.

생성된 후보:

- `submission_hsjepa_subjective_shadow_bridge_q1shadow_guarded_7fab5753_uploadsafe.csv`
- `submission_hsjepa_subjective_shadow_bridge_q1shadow_jackpot_59852a64_uploadsafe.csv`

현재 결과:

- guarded: stage 60 cells + Q1 shadow 18 cells, route energy `0.725130`
- jackpot: stage 82 cells + Q1 shadow 29 cells, route energy `0.723289`
- 둘 다 stage-only보다 route energy는 낮아짐
- 하지만 Q1-S correlation null stress에서 실제 Q1-S 구조가 랜덤 구조보다 강하지 않음
  - guarded top-score z `-0.439`, p(null >= actual) `0.656`
  - jackpot top-score z `-0.909`, p(null >= actual) `0.828`

해석:

- S-stage bridge는 action-grade 구조지만, Q1 subjective shadow는 아직 action-grade 구조가 아니다.
- HS-JEPA decoder는 Q와 S를 하나로 뭉개기보다, objective-stage decoder와 subjective decoder를 분리해야 한다.

자세한 설명:

- `paper_hsjepa_core/SUBJECTIVE_SHADOW_BRIDGE_SOLVER_KO.md`

### 10. Objective-Stage Factor Transport Solver

```bash
python3 paper_hsjepa_core/stage_factor_transport_solver.py
```

이 스크립트는 S1/S2/S3/S4가 하나의 objective sleep-state factor 방향으로
같이 움직이는지 테스트한다.

생성된 후보:

- `submission_hsjepa_stage_factor_transport_factor_paircore_7cde1a77_uploadsafe.csv`
- `submission_hsjepa_stage_factor_transport_factor_axis_jackpot_976bf3f9_uploadsafe.csv`

현재 결과:

- train S-stage PC1은 모든 S target에 양수 weight를 갖고, 설명분산 `46.1%`
- factor_paircore는 selected bundle `0`, 즉 no-op
- factor_axis_jackpot은 full S-stage 4-target bundle `2`개, changed cells `8`
- factor null stress에서 실제 PC1이 random factor보다 압도적으로 강하지 않음
  - top-score z `0.435`, p(null >= actual) `0.292`
  - energy gain z `-0.016`, p(null >= actual) `0.292`

해석:

- S-stage common factor는 representation으로 존재한다.
- 하지만 public-safe action은 전체 factor axis를 그대로 따라가지 않는다.
- 현재 가장 강한 action 구조는 여전히 `row-specific driver + local bridge`다.

자세한 설명:

- `paper_hsjepa_core/STAGE_FACTOR_TRANSPORT_SOLVER_KO.md`
