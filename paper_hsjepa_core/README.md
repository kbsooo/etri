# Paper-Core HS-JEPA Experiments

이 폴더는 대회용 best submission을 그대로 설명하는 데서 멈추지 않고, HS-JEPA를 논문형 아키텍처로 정리하기 위한 실험을 담는다.

팀 공유용 최상위 설명 문서:

- `paper_hsjepa_core/HS_JEPA_PAPER_THESIS_KO.md`
- `paper_hsjepa_core/HS_JEPA_ARCHITECTURE_PACKAGE_KO.md`
- `paper_hsjepa_core/LIFELOG_CORE_STATE_EVIDENCE_KO.md`
- `paper_hsjepa_core/ACTION_HEALTH_SEPARATION_PROBE_KO.md`
- `paper_hsjepa_core/TEACHER_FREE_CORE_SUPPORT_RELEASE_KO.md`
- `paper_hsjepa_core/CORE_OOF_ACTION_HEALTH_BENCHMARK_KO.md`
- `paper_hsjepa_core/CONTEXTUAL_LISTENER_ROUTE_SELECTOR_KO.md`
- `paper_hsjepa_core/RAW_KNN_FAILURE_DETECTOR_KO.md`
- `paper_hsjepa_core/RAW_KNN_OVERRIDE_SAFETY_JURY_KO.md`
- `paper_hsjepa_core/CONTRASTIVE_FAILURE_ATLAS_KO.md`
- `paper_hsjepa_core/FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md`
- `paper_hsjepa_core/ROW_RESET_EPISODE_DETECTOR_KO.md`

논문 방향으로는 `HS_JEPA_PAPER_THESIS_KO.md`를 먼저 읽는다. 이 문서는 HS-JEPA를 대회용 trick이 아니라 `hidden human-state -> listener responsibility -> action-health -> invariant release` 아키텍처로 정리하고, public LB를 그 주장을 검증하는 sensor로 해석한다.

`LIFELOG_CORE_STATE_EVIDENCE_KO.md`는 public LB 없이 OG lifelog-derived context만으로 HS-JEPA core representation이 무엇을 설명하는지 정리한다. 현재 결론은 명확하다.

```text
HS-JEPA core는 단독 label predictor가 아니라,
row-action support와 action-health를 더 잘 읽게 하는 human-state geometry다.
```

`ACTION_HEALTH_SEPARATION_PROBE_KO.md`는 그 다음 질문을 다룬다. core-state geometry가 action decoder의 독성을 public score 없이 줄일 수 있는지 확인한다.

현재 핵심 결과:

- health score 계산에는 public LB를 쓰지 않는다.
- retrospective evaluation에서 nonzero action field 6개 기준 Spearman(action health, -public LB) `0.8407`, p-value `0.0361`.
- broad `core_geometry_outlier_route_bigbet`에서 cell-level health 하위 tail을 제거한 후보 `submission_hsjepa_action_health_separation_core_route_release_de79e203_uploadsafe.csv`를 생성했다.

`TEACHER_FREE_CORE_SUPPORT_RELEASE_KO.md`는 더 강한 질문을 다룬다. 기존 성공 action teacher 없이 HS-JEPA core만으로 row-state frontier 일부를 다시 찾을 수 있는지 본다.

현재 핵심 결과:

- support score 계산에는 public LB와 action teacher를 쓰지 않는다.
- top 28% teacher-free support에서 row-state frontier 45개 row 중 16개를 회수했다.
- recall `0.3556`, precision `0.2286`.
- 후보 `submission_hsjepa_teacher_free_core_support_release_8d9899fb_uploadsafe.csv`를 생성했다.

현재 해석:

```text
HS-JEPA core는 action-grade decoder가 아니라,
listener/assignment solver가 사용할 수 있는 row-support geometry다.
```

`CORE_OOF_ACTION_HEALTH_BENCHMARK_KO.md`는 public/submission teacher 없이 OG train future split에서 HS-JEPA가 실제 Log Loss를 줄이는 방식을 검증한다.

현재 핵심 결과:

- subject prior temporal OOF: `0.650566`
- raw lifelog KNN blend: `0.636997`
- core KNN blend: `0.638266`
- best single action-health decoder: `0.644184`
- target listener route selector: `0.629398`

현재 해석:

```text
HS-JEPA의 성능은 단일 decoder가 아니라 target/listener별 route selection에서 나온다.
```

`CONTEXTUAL_LISTENER_ROUTE_SELECTOR_KO.md`는 그 다음 질문을 다룬다. target-level route가 아니라 row-target sample-level route를 HS-JEPA context가 고를 수 있는지 검증한다.

현재 핵심 결과:

- raw lifelog KNN blend: `0.636997`
- fixed target listener route OOF: `0.657106`
- contextual soft router: `0.643769`
- best raw-fallback router: `0.638444`

현재 해석:

```text
sample-level router는 fixed route를 이기지만, raw KNN을 안정적으로 넘지는 못한다.
따라서 다음은 full router가 아니라 raw-KNN failure detector다.
```

`RAW_KNN_FAILURE_DETECTOR_KO.md`는 이 다음 질문을 직접 검증한다. raw lifelog KNN을 기본값으로 두고, HS-JEPA route-risk가 실패 가능성이 큰 cell만 sparse override한다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- raw-KNN failure detector OOF: `0.632612`
- delta: `-0.004385`
- OOF switched cells: `29`
- generated candidate: `submission_hsjepa_raw_knn_failure_detector_2a097b16_uploadsafe.csv`

현재 해석:

```text
HS-JEPA는 full predictor보다 failure-aware listener override로 쓸 때 더 강하다.
```

`RAW_KNN_OVERRIDE_SAFETY_JURY_KO.md`는 failure detector를 더 엄격하게 검증한다. 여러 gain detector와 vote/consensus guard를 붙여 sharp boundary가 우연인지, consensus로도 살아남는 안정 신호인지 확인한다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- sharp boundary OOF: `0.632478`
- delta: `-0.004519`
- OOF switched cells: `22`
- target matched-null p-value: `0.001000`
- target+family matched-null p-value: `0.000500`
- best guarded OOF: `0.635705`
- generated candidate: `submission_hsjepa_raw_knn_override_safety_jury_50450d26_uploadsafe.csv`

현재 해석:

```text
큰 gain은 broad consensus가 아니라 sharp route-risk boundary에서 나온다.
consensus guard는 action-health stress diagnostic으로는 유용하지만, release signal을 지나치게 죽인다.
```

`CONTRASTIVE_FAILURE_ATLAS_KO.md`는 sharp boundary를 더 JEPA답게 바꾸려는 ablation이다. 성공 action과 toxic action을 HS-JEPA human-state context 안의 positive/negative prototype atlas로 만들고, prototype energy만으로 raw-KNN override를 할 수 있는지 본다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- best contrastive atlas OOF: `0.635425`
- delta: `-0.001572`
- OOF switched cells: `59`
- target matched-null p-value: `0.529250`
- target+family matched-null p-value: `0.534500`
- generated candidate: `submission_hsjepa_contrastive_failure_atlas_7a28f76d_uploadsafe.csv`
- submission priority: `low_negative_evidence_not_primary_submission`

현재 해석:

```text
prototype atlas는 raw KNN보다 평균 OOF를 조금 개선하지만 matched-null을 통과하지 못한다.
따라서 HS-JEPA core representation alone은 release-grade action solver가 아니며,
row-target assignment/release decoder가 별도로 필요하다.
```

`FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md`는 prototype atlas 실패 이후의 다음 질문을 다룬다. sharp GBDT boundary가 완전한 black-box인지, 아니면 작은 HS-JEPA action law로 증류되는지 확인한다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- depth-2 law OOF: `0.632902`
- GBDT failure detector OOF: `0.632478`
- delta vs raw KNN: `-0.004095`
- delta vs GBDT detector: `+0.000425`
- OOF switched cells: `59`
- target+family matched-null p-value: `0.024750`
- nonzero feature count: `2`
- selected feature: `expert_prob_mean`, `abs_vs_core`
- generated candidate: `submission_hsjepa_failure_boundary_law_distillation_65ce2d48_uploadsafe.csv`
- submission priority: `high_information_sensor_prior_reset_law`

현재 해석:

```text
raw-KNN failure boundary는 완전한 black-box가 아니며,
core geometry와 route-average probability만으로 거의 GBDT 수준까지 증류된다.
HS-JEPA core는 label predictor가 아니라 prior-reset/action-toxicity를 판단하는 listener agreement 기준점으로 작동한다.
```

`ROW_RESET_EPISODE_DETECTOR_KO.md`는 그 다음 일반화 질문을 다룬다. failure-boundary law가 고른 action이 실제로는 독립 cell이 아니라 특정 row 전체 reset처럼 보였기 때문에, 이를 hidden episode detector로 재정의했다.

현재 핵심 결과:

- public score ledger, 기존 submission probability, action teacher, frontier file을 쓰지 않는다.
- raw KNN OOF: `0.636997`
- best row reset detector OOF: `0.634030`
- delta vs raw KNN: `-0.002967`
- selected OOF rows: `6`
- row-null p-value: `0.005833`
- generated candidate: `submission_hsjepa_row_reset_episode_detector_9054c5d1_uploadsafe.csv`

현재 해석:

```text
raw lifelog memory가 row 전체 차원에서 실패하는 hidden episode가 있고,
HS-JEPA context는 이를 public/LB teacher 없이 일부 탐지한다.
하지만 row reset만으로는 release-grade solver가 아니며,
target/listener assignment decoder와 결합해야 한다.
```

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

### 0. Lifelog Core State Evidence

```bash
python3 hsjepa_core/run_lifelog_core_state_evidence.py
```

이 스크립트는 public score ledger를 읽지 않고, OG lifelog-derived feature table에서 core-state evidence를 만든다.

현재 결과:

- subject-holdout label logloss는 prior보다 나쁘다. 따라서 HS-JEPA core를 direct classifier로 과장하면 안 된다.
- nearest-neighbor target consistency는 random 대비 `+0.0506` lift를 보인다.
- masked context prediction은 phone/app/body view에서 null 대비 component-correlation lift를 보인다.
- external action replay에서는 core-state geometry만으로 평균 row AUC `0.9543`, recall@k `0.8386`, permutation z `8.38`을 보인다.

논문 해석:

> Human-state representation is weak as a direct classifier, but strong as a row-action support geometry.

### 0b. Action-Health Separation Probe

```bash
python3 sleep_competition_adapter/action_health_separation_probe.py
```

이 스크립트는 public score 없이 action-health score를 계산한 뒤, public outcome은 마지막 retrospective label로만 사용한다.

현재 결과:

- scored candidates: `7`
- nonzero action candidates: `6`
- nonzero Spearman health vs -public LB: `0.8407`
- generated candidate: `submission_hsjepa_action_health_separation_core_route_release_de79e203_uploadsafe.csv`

논문 해석:

> HS-JEPA core geometry is useful not only for row support, but also for ranking action toxicity before release.

### 0c. Teacher-Free Core Support Release

```bash
python3 sleep_competition_adapter/teacher_free_core_support_release.py
```

이 스크립트는 public score ledger와 기존 action teacher 없이, OG lifelog-derived HS-JEPA core geometry만으로 row support를 만든다.

현재 결과:

- changed rows: `40`
- changed cells: `160`
- best overlap: row-state frontier 45개 row 중 `16`개 회수 at top 28%
- recall / precision: `0.3556 / 0.2286`
- generated candidate: `submission_hsjepa_teacher_free_core_support_release_8d9899fb_uploadsafe.csv`

논문 해석:

> HS-JEPA core can recover non-trivial row-state support without action-teacher supervision, but a separate listener/assignment and action-health decoder is still required for release-grade corrections.

### 0d. Core OOF Action-Health Benchmark

```bash
python3 sleep_competition_adapter/core_oof_action_health_benchmark.py
```

이 스크립트는 public score, 기존 submission, action teacher 없이 OG train 내부 future split에서 HS-JEPA 구조를 비교한다.

현재 결과:

- best temporal model: `hsjepa_target_listener_route_selector`
- temporal mean logloss: `0.629398`
- subject prior 대비 delta: `-0.021168`
- raw KNN 대비 delta: `-0.007599`
- generated candidate: `submission_hsjepa_core_oof_action_health_fea05ac1_uploadsafe.csv`

논문 해석:

> HS-JEPA should be framed as listener-specific route selection over human-state, raw-lifelog, prior, and action-health routes, not as a monolithic latent classifier.

### 0e. Contextual Listener Route Selector

```bash
python3 sleep_competition_adapter/contextual_listener_route_selector.py
```

이 스크립트는 target별 route 선택을 row-target별 contextual routing으로 확장할 수 있는지 본다.

현재 결과:

- fixed target route OOF: `0.657106`
- contextual soft router: `0.643769`
- best raw-fallback router: `0.638444`
- raw KNN baseline: `0.636997`
- generated candidate: `submission_hsjepa_contextual_listener_router_3cbcbe6e_uploadsafe.csv`

논문 해석:

> HS-JEPA context improves over fixed listener routes, but sample-level routing is not yet strong enough to outperform raw-lifelog nearest-neighbor prediction.

### 0f. Raw-KNN Failure Detector

```bash
python3 sleep_competition_adapter/raw_knn_failure_detector.py
```

이 스크립트는 raw KNN을 기본값으로 두고, HS-JEPA route-risk가 predicted gain이 높은 cell만 다른 listener route로 sparse override한다.

현재 결과:

- raw KNN OOF: `0.636997`
- best failure detector OOF: `0.632612`
- delta vs raw KNN: `-0.004385`
- switched OOF cells: `29`
- generated candidate: `submission_hsjepa_raw_knn_failure_detector_2a097b16_uploadsafe.csv`

논문 해석:

> HS-JEPA is most useful as a failure-aware listener override on top of a strong raw-lifelog predictor, not as a broad replacement for that predictor.

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

### 11. S2-Hub Bridge Solver

```bash
python3 paper_hsjepa_core/s2hub_bridge_solver.py
```

이 스크립트는 S2가 objective-stage local bridge/listener hub인지 테스트한다.

생성된 후보:

- `submission_hsjepa_s2hub_bridge_s2bridge_core_2cec9d38_uploadsafe.csv`
- `submission_hsjepa_s2hub_bridge_s2hub_jackpot_f0866f50_uploadsafe.csv`

현재 결과:

- s2bridge_core: 21 bundles, 42 cells, route energy `0.726721`, H088 cosine `-0.006979`
- s2hub_jackpot: 34 bundles, 68 cells, route energy `0.724714`, H088 cosine `-0.000696`
- s2hub_jackpot은 모든 bundle에 S2를 포함하면서 stagebridge보다 낮은 route energy를 얻음
- hub contrast상 S2는 energy-gain hub라기보다 public-utility hub

해석:

- S2는 전체 S-stage factor가 아니라 public-sensitive S-stage listener/hub에 가깝다.
- stagebridge_jackpot이 가장 큰 후보라면, s2hub_jackpot은 더 해석 가능한 S2-hub 후보다.

자세한 설명:

- `paper_hsjepa_core/S2HUB_BRIDGE_SOLVER_KO.md`

### 12. OG Human-State Distillation of S2-Hub

```bash
python3 paper_hsjepa_core/s2hub_human_state_distillation.py
```

이 스크립트는 OG raw lifelog 기반 human-state context가 S2-hub/stagebridge
action support를 설명할 수 있는지 테스트한다.

생성된 후보:

- `submission_hsjepa_ogdistilled_s2hub_jackpot_38d995b0_uploadsafe.csv`
- `submission_hsjepa_ogdistilled_stagebridge_jackpot_96a9fd11_uploadsafe.csv`

현재 결과:

- S2-hub cell-level subject-held-out OOF AUC `0.775`, AP `0.094`
- S2-hub row-level subject-held-out OOF AUC `0.545`, AP `0.168`
- Stagebridge cell-level OOF AUC `0.722`, AP `0.094`
- Stagebridge row-level OOF AUC `0.493`, AP `0.171`

해석:

- OG human-state는 target/cell route orientation을 설명한다.
- 하지만 어느 row를 고칠지는 거의 설명하지 못한다.
- 따라서 HS-JEPA 본체는 action orientation encoder이고, row assignment는 별도 listener/competition decoder가 필요하다.

자세한 설명:

- `paper_hsjepa_core/S2HUB_HUMAN_STATE_DISTILLATION_KO.md`

### 13. Target-Listener Route Lift Solver

```bash
python3 paper_hsjepa_core/target_listener_route_lift_solver.py
```

이 스크립트는 row assignment를 직접 예측하지 않고, OG human-state가
복원한 target/cell listener posterior를 route-energy로 들어올릴 수
있는지 테스트한다.

생성된 후보:

- `submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_core_88b45606_uploadsafe.csv`
- `submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv`
- `submission_hsjepa_target_listener_route_lift_stagebridge_listener_lift_jackpot_0365d7d9_uploadsafe.csv`

현재 결과:

- S2-hub cell OOF AUC는 `0.775`로 강하지만 row-lift AUC는 `0.556` 수준
- core는 extra cell `0`개라 사실상 S2-hub teacher amplitude ablation
- s2hub_listener_lift_jackpot은 extra `13` cells를 찾았고, 그중 `10`개가 S2
- extra cell 평균 route energy delta는 `-0.001124`
- stagebridge_listener_lift_jackpot은 extra `1` cell만 추가

해석:

- target/cell listener posterior는 실제 신호다.
- 하지만 이 posterior를 row로 단순 lift하는 것만으로는 row assignment가 풀리지 않는다.
- HS-JEPA는 `Human-State Encoder -> Target Listener -> Row Assignment Solver -> Route Energy Decoder`처럼 모듈화되어야 한다.

자세한 설명:

- `paper_hsjepa_core/TARGET_LISTENER_ROUTE_LIFT_SOLVER_KO.md`
