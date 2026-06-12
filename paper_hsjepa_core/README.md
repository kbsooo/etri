# Paper-Core HS-JEPA Experiments

이 폴더는 대회용 best submission을 그대로 설명하는 데서 멈추지 않고, HS-JEPA를 논문형 아키텍처로 정리하기 위한 실험을 담는다.

팀 공유용 최상위 설명 문서:

- `paper_hsjepa_core/HS_JEPA_CORE_FIRST_THESIS_KO.md`
- `paper_hsjepa_core/HS_JEPA_CORE_ADAPTER_DIAGNOSTIC_BOUNDARY_KO.md`
- `paper_hsjepa_core/HS_JEPA_PAPER_THESIS_KO.md`
- `paper_hsjepa_core/HS_JEPA_ARCHITECTURE_PACKAGE_KO.md`
- `paper_hsjepa_core/HS_JEPA_JEPA_CONTRACT_KO.md`
- `paper_hsjepa_core/MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md`
- `paper_hsjepa_core/ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md`
- `paper_hsjepa_core/ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md`
- `paper_hsjepa_core/LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md`
- `paper_hsjepa_core/SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md`
- `paper_hsjepa_core/TARGET_ROUTE_CONSERVATION_DECODER_KO.md`
- `paper_hsjepa_core/SUBJECT_BALANCED_ROUTE_CONSERVATION_DECODER_KO.md`
- `paper_hsjepa_core/WORLD_MODEL_RESIDUAL_ACTION_DECODER_KO.md`
- `paper_hsjepa_core/SUBJECT_INVARIANT_WORLD_MODEL_LISTENER_SOLVER_KO.md`
- `paper_hsjepa_core/COHORT_LISTENER_RESPONSIBILITY_TRANSPORT_KO.md`
- `paper_hsjepa_core/ACTION_EPISODE_LISTENER_TRANSPORT_KO.md`
- `paper_hsjepa_core/TARGET_ROUTE_GUARDED_ACTION_EPISODE_TRANSPORT_KO.md`
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
- `paper_hsjepa_core/EPISODE_SELECTIVE_ASSIGNMENT_DECODER_KO.md`
- `paper_hsjepa_core/EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md`
- `paper_hsjepa_core/EPISODE_CONTROLLER_STRESS_AUDIT_KO.md`
- `paper_hsjepa_core/SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md`
- `paper_hsjepa_core/CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md`
- `paper_hsjepa_core/MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md`
- `paper_hsjepa_core/SURPRISE_RESPONSIBILITY_TOXICITY_VETO_KO.md`
- `paper_hsjepa_core/CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md`

처음 보는 팀원은 `HS_JEPA_CORE_FIRST_THESIS_KO.md`를 먼저 읽는다. 이 문서는 HS-JEPA를 kNN transport, veto rule, submission CSV가 아니라 `visible human context -> hidden human-state target representation prediction`이라는 core-first architecture로 정리한다.

만약 특정 실험이 "이게 HS-JEPA인지, 아니면 그냥 adapter/diagnostic인지" 헷갈리면 `HS_JEPA_CORE_ADAPTER_DIAGNOSTIC_BOUNDARY_KO.md`를 먼저 확인한다. 이 문서는 다음 규칙을 강제한다.

```text
Core       = 보이는 human context로 보이지 않는 representation을 예측
Adapter    = 그 representation을 row-target action으로 번역
Diagnostic = 그 action이 shortcut/collapse/subject-tail인지 검사
```

즉 `Cross-Subject Episode Prototype Transport`와 `Subject-Relative Responsibility Assignment`는 HS-JEPA 세계 안의 중요한 실험이지만, HS-JEPA core 자체로 소개하면 안 된다.

논문 방향으로는 그 다음 `HS_JEPA_PAPER_THESIS_KO.md`를 읽는다. 이 문서는 HS-JEPA를 대회용 trick이 아니라 `hidden human-state -> listener responsibility -> action-health -> invariant release` 아키텍처로 정리하고, public LB를 그 주장을 검증하는 sensor로 해석한다.

`HS_JEPA_CORE_ADAPTER_DIAGNOSTIC_BOUNDARY_KO.md`는 팀 공유용 경계 문서다. HS-JEPA를 다음 세 층으로 나눈다.

```text
Core       = visible human-life context -> hidden human-state representation
Adapter    = hidden representation -> row-target correction/action
Diagnostic = action이 shortcut/collapse/subject-tail/public-luck인지 검사
```

이 경계를 유지해야 `Cross-Subject Episode Prototype Transport` 같은 competition adapter를 HS-JEPA core처럼 과장하지 않고, `Subject-Invariant Episode Controller` 같은 stress audit을 LeJEPA-style diagnostic으로 정확히 위치시킬 수 있다.

`MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md`는 가장 core에 가까운 최신 실험이다. semantic lifelog view 하나를 가리고 나머지 view로 target-view representation을 예측한다. 결과는 양면적이다.

- app/social target-view는 null 대비 component-correlation lift `+0.248882`로 예측된다.
- world-model state의 nearest-neighbor target match lift는 `+0.031302`다.
- 하지만 direct label probe는 prior보다 나쁘다.
- S3/S4 action-health diagnostic에서는 residual energy가 toxic action pocket을 분리한다.

즉 HS-JEPA core는 직접 classifier가 아니라, action-health와 listener responsibility를 위한 hidden human-state geometry라는 주장이 더 강해졌다.

`ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md`는 masked-context world model을 한 단계 더 core-first로 검증한다. target label을 직접 예측하지 않고, train label만으로 만든 raw lifelog-memory action의 success/toxicity representation을 subject-heldout으로 예측한다.

현재 핵심 결과:

- raw lifelog memory action은 전체적으로 prior보다 손해다: OOF gain sum `-48.053725`.
- HS-JEPA masked world full-state는 action-support AUC `0.539592`, AP `0.530735`를 기록했다.
- support score가 낮은 decisive action을 inverse-toxic decoder로 반대로 움직이면 selected OOF gain sum `+2.621567`을 얻었다.
- target-shuffle null 대비 gain lift `+6.164069`, z-score `2.636913`이다.
- public LB ledger, 기존 best submission probability, proprietary embedding API는 쓰지 않았다.

현재 해석:

```text
HS-JEPA core는 label classifier나 broad action generator가 아니라,
row-target action을 release하기 전에 action-health/toxicity를 예측하는
hidden world-state representation이다.
```

이 문서는 `Cross-Subject Episode Prototype Transport`보다 더 HS-JEPA core에 가깝다. 단, 생성된 submission은 best-score adapter가 아니라 core-only action-support sensor로 읽어야 한다.

`ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md`는 위 action-support 신호가 target/action shortcut인지 stress한다. 같은 train-only target을 target/action-only, target-blind, single-view, leave-one-view-out feature set으로 다시 예측했다.

현재 핵심 결과:

- target/action-only baseline selected gain: `-4.107447`
- selected world-state feature set: `world_residual_energy`
- selected OOF gain sum: `+6.146252`
- support AUC/AP: `0.542555` / `0.536845`
- target-shuffle null 대비 gain lift: `+9.817777`, z-score `2.942742`
- target-blind world full-state는 baseline보다 낫지만 selected gain `-0.320604`로 positive는 아니다.
- verdict: `world_state_signal_positive_target_blind_weakly_survives`

현재 해석:

```text
HS-JEPA residual/energy world state는 target/action-only shortcut보다 강한 action-support 신호를 가진다.
다만 완전한 target-invariant representation은 아니므로,
논문 주장은 "listener-conditioned human-state action-support model"이어야 한다.
```

`LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md`는 이 결론을 직접 검증한다. target-blind world state가 약했던 이유를 listener 부재로 보고, world-state residual/energy에 target/family listener interaction을 붙여 action-support를 예측했다.

현재 핵심 결과:

- selected listener: `target_interaction_world_residual_energy`
- selected OOF gain sum: `+6.192500`
- support AUC/AP: `0.611128` / `0.600888`
- target-shuffle null 대비 gain lift: `+10.137463`, z-score `2.610537`
- target/action-only baseline selected gain: `+1.543383`
- global world residual/energy selected gain: `-1.955206`
- target-heldout transfer는 AUC `0.629874`지만 selected gain `-2.496232`로 release-grade가 아니다.
- verdict: `listener_conditioning_positive_but_target_transfer_unproven`

현재 해석:

```text
HS-JEPA core evidence는 target-free universal decoder가 아니라
listener-conditioned action-support world model 쪽으로 수렴한다.
Target listener가 있을 때는 OOF action-support가 강하지만,
새 target route로 전이되는 법칙은 아직 증명되지 않았다.
```

`SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md`는 위 결론을 더 일반적인 방향에서 다시 찌른다. target/listener conditioning이 너무 대회 특화처럼 보일 수 있으므로, 같은 subject + 같은 target 내부의 pairwise ordering으로 supervision을 바꿔 subject/target prior shortcut을 제거했다.

현재 핵심 결과:

- selected feature set: `binary_preference__world_residual_energy_pair`
- selected OOF gain sum: `+2.383219`
- support AUC/AP: `0.512922` / `0.508946`
- target-shuffle null 대비 gain lift: `+7.010120`, z-score `1.526122`
- shortcut/action-only baselines는 AUC가 높아도 selected gain이 모두 음수다.
- tail-weighted preference도 utility로 번역되지 않았다.
- verdict: `subject_contrastive_world_state_weakly_positive`

현재 해석:

```text
HS-JEPA residual energy는 subject/target shortcut을 제거해도 약한 episode-level
action-health ordering을 갖는다.
하지만 높은 AUC가 Log Loss utility를 보장하지 않는다.
따라서 논문 주장은 "core representation + tail-safe action-health decoder"로
정리해야 한다.
```

`TARGET_ROUTE_CONSERVATION_DECODER_KO.md`는 위 core evidence를 competition adapter로 번역한다. 이 문서는 HS-JEPA core 자체가 아니라, listener-conditioned core signal을 Q/S target route별 release / inverse-toxic / hold action으로 바꾸는 adapter다.

현재 핵심 결과:

- public LB ledger 사용: `False`
- 기존 submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- OOF selected gain sum: `+15.595885`
- listener global gain reference: `+6.192500`
- gain over listener global reference: `+9.403385`
- selected positive gain rate: `0.734104`
- released test cells: `197`
- Q2/S2/S4는 raw-memory release, Q3/S1/S3는 inverse-toxic action을 선택했다.
- candidate: `submission_hsjepa_target_route_conservation_decoder_anchor_free_4837b6ce_uploadsafe.csv`

현재 해석:

```text
HS-JEPA core만으로는 release law가 완성되지 않는다.
하지만 core residual/energy는 target listener와 결합될 때 action-health를 강하게 설명한다.
따라서 competition adapter는 target-route conservation decoder를 가져야 한다.
```

`SUBJECT_BALANCED_ROUTE_CONSERVATION_DECODER_KO.md`는 이 positive adapter가 subject-tail shortcut인지 검사한다. 같은 public-free route law를 쓰되, subject별 gain exposure가 나쁜 target route를 버린다.

현재 핵심 결과:

- public LB ledger 사용: `False`
- 기존 submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- OOF selected gain sum: `+10.122799`
- listener global gain reference: `+6.192500`
- route conservation gain reference: `+15.595885`
- gain retained vs route conservation reference: `0.649069`
- selected positive gain rate: `0.740964`
- accepted targets: `Q2`, `Q3`, `S3`, `S4`
- held targets: `Q1`, `S1`, `S2`
- released test cells: `96`
- subject별 total gain은 10명 모두 양수다.
- candidate: `submission_hsjepa_subject_balanced_route_conservation_anchor_free_74ca928e_uploadsafe.csv`

현재 해석:

```text
target-route conservation gain이 전부 subject-tail shortcut은 아니다.
subject-balanced stress를 걸어도 listener-global reference를 넘고 약 65% gain이 남는다.
다만 core 단독 증명이 아니라, HS-JEPA core representation이 adapter/diagnostic을 거칠 때
action-health 독성을 줄인다는 증거로 써야 한다.
```

`WORLD_MODEL_RESIDUAL_ACTION_DECODER_KO.md`는 이 core evidence를 adapter로 번역하는 다음 단계다. masked-context world model의 residual energy를 cross-subject prototype transport action field의 target-specific listener로 사용했다.

현재 핵심 결과:

- source cross-subject action cells: `44`
- source active subjects: `7`
- original gain sum: `5.027044`
- world-model listener kept cells: `35`
- kept gain sum: `6.093459`
- removed cells: `9`
- removed gain sum: `-1.066415`
- kept positive gain rate: `0.771429`
- subject-heldout original gain sum: `5.027044`
- subject-heldout kept gain sum: `1.557169`
- verdict: `oof_positive_subjectheldout_fragile`

현재 해석:

```text
HS-JEPA core residual energy는 action toxicity pocket을 감지하지만,
그대로 subject-general release law라고 주장하기에는 아직 fragile하다.
```

따라서 이 문서는 HS-JEPA core가 아니라 adapter/diagnostic이다. 논문에서는
`core representation이 action decoder 독성을 줄이는 방향의 증거`와
`subject-heldout에서 아직 완성되지 않은 한계`를 동시에 말해야 한다.

`SUBJECT_INVARIANT_WORLD_MODEL_LISTENER_SOLVER_KO.md`는 위 fragile 결과를 더 엄격하게 찌른다. full OOF gain이 아니라 subject-balanced objective로 target별 listener rule을 고르게 만들었다.

현재 핵심 결과:

- source cross-subject action cells: `44`
- selected objective: `subject_balanced_listener`
- original gain sum: `5.027044`
- subject-balanced kept gain sum: `6.442219`
- removed action gain sum: `-1.415175`
- non-all listener targets: `3`
- subject-LOO improvement sum: `-3.281044`
- verdict: `oof_positive_subject_invariant_negative`

현재 해석:

```text
subject-balanced selector를 걸어도 OOF toxicity separation은 더 강해진다.
하지만 subject-LOO에서는 여전히 음수라서, 현재 residual listener는
subject-general release law가 아니라 toxic-pocket diagnostic에 가깝다.
```

이 결과는 실패가 아니라 경계 증거다. HS-JEPA core residual이 의미 없는 신호는 아니지만,
논문에서 `release-grade architecture`로 주장하려면 subject-invariant listener responsibility가
다음 핵심 병목이다.

`COHORT_LISTENER_RESPONSIBILITY_TRANSPORT_KO.md`는 그 다음 후보였던 subject/cohort-level transport를 검증한다. world-model subject fingerprint가 비슷한 peer subject에서 target별 listener responsibility rule을 가져와 held-out subject에 적용했다.

현재 핵심 결과:

- selected neighbors: `1`
- original OOF gain sum: `5.027044`
- transported kept gain sum: `2.681536`
- transported gain delta: `-2.345507`
- positive subjects: `0`
- negative subjects: `3`
- test vetoed switched cells: `6`
- verdict: `cohort_transport_negative_or_inconclusive`

현재 해석:

```text
subject-level world-model fingerprint만으로는 listener responsibility가 전이되지 않는다.
현재 병목은 subject similarity가 아니라 row-target route/action-context를 포함한
responsibility transport다.
```

이 실험은 cohort 방향을 버리라는 뜻이 아니라, cohort를 `사람 단위 평균 fingerprint`로 정의하면
HS-JEPA action responsibility를 설명하기에 너무 거칠다는 negative evidence다.

`ACTION_EPISODE_LISTENER_TRANSPORT_KO.md`는 위 negative evidence를 반영해 responsibility 전이 단위를 subject에서 row-target action episode로 바꾼다. 같은 target, action expert/family, HS-JEPA residual geometry가 가까운 peer action의 gain으로 현재 action을 keep/veto한다.

현재 핵심 결과:

- release policy: `target_expert__knn3__uniform__thr-0.10`
- original OOF gain sum: `5.027044`
- kept OOF gain sum: `5.857716`
- OOF gain delta: `+0.830672`
- removed action gain sum: `-0.830672`
- active subjects: `6`
- positive subjects: `2`
- negative subjects: `1`
- test vetoed switched cells: `29`
- verdict: `action_episode_transport_positive`

현재 해석:

```text
HS-JEPA responsibility는 subject 평균 fingerprint로는 전이되지 않지만,
row-target action route와 residual geometry를 같이 보면 일부 전이된다.
```

이것은 HS-JEPA adapter claim에 더 가까운 positive evidence다. 다만 개선은 S3/id06 쪽에 집중되고
S4/id04 손실이 남아 있어, 논문에서는 `완성된 decoder`가 아니라
`action-episode responsibility transport가 필요한 이유와 가능성`으로 설명해야 한다.

`TARGET_ROUTE_GUARDED_ACTION_EPISODE_TRANSPORT_KO.md`는 action-episode transport의 남은 S4 손실을 target-route responsibility로 분해한다. 전역 listener 하나를 쓰지 않고, target별로 keep-all / veto-all / action-episode transport 중 하나를 선택한다.

현재 핵심 결과:

- Q2/Q3/S2: `keep_all`
- S3: `target_expert__knn1__uniform__thr-0.10`
- S4: `veto_all`
- original OOF gain sum: `5.027044`
- kept OOF gain sum: `6.638536`
- OOF gain delta: `+1.611492`
- removed action gain sum: `-1.611492`
- positive subjects: `3`
- negative subjects: `1`
- test vetoed switched cells: `33`
- verdict: `target_route_guard_positive`

현재 해석:

```text
HS-JEPA adapter는 단일 global listener가 아니라 target-route별 responsibility system이어야 한다.
S3-like action route는 peer action-episode transport를 믿고,
S4-like action route는 더 강한 guard가 필요하다.
```

이 결과는 논문 패키징에 중요하다. 단순 후처리 튜닝이 아니라,
HS-JEPA core representation이 action decoder로 번역될 때 필요한 구조적 decoder 분해를 보여준다.

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

`EPISODE_SELECTIVE_ASSIGNMENT_DECODER_KO.md`는 바로 그 결합을 시도한 ablation이다. row-level hidden episode score를 cell-level target/listener assignment decoder에 넣어, row episode state가 실제 release decision을 바꾸는지 확인했다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- row episode detector OOF: `0.634030`
- best no-episode assignment OOF: `0.632902`
- best episode-conditioned assignment OOF: `0.632902`
- episode gain over no-episode: `0.000000`
- release top features: `expert_prob_mean`, `abs_vs_core`, `raw_confidence`
- release 후보는 failure-boundary law와 동일한 prediction이다.
- generated candidate: `submission_hsjepa_episode_selective_assignment_decoder_65ce2d48_uploadsafe.csv`

현재 해석:

```text
row episode state는 diagnostic으로는 살아 있지만,
단순 feature injection만으로는 release-grade target/listener assignment에 쓰이지 않았다.
다음 구조는 episode score를 feature로 더하는 방식이 아니라,
episode가 action space 자체를 제한하거나 listener responsibility를 재가중하는 방식이어야 한다.
```

`EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md`는 그 다음 구조적 결합을 검증한다. row episode score를 feature로 더하지 않고, action 후보 공간을 제한하는 controller로 사용했다.

현재 핵심 결과:

- raw KNN OOF: `0.636997`
- unrestricted route law OOF: `0.632902`
- episode action-space restriction OOF: `0.629771`
- delta vs unrestricted: `-0.003132`
- best policy: `episode_family_space_q90`
- switched OOF cells: `44`
- target+family null p-value: `0.000625`
- generated candidate: `submission_hsjepa_episode_action_space_restriction_decoder_816c3a6e_uploadsafe.csv`

현재 해석:

```text
episode를 ordinary feature로 넣으면 decoder가 무시했지만,
episode가 action space를 제한하면 unrestricted route law를 이긴다.
HS-JEPA row-state encoder는 label predictor보다 action responsibility controller로 더 잘 작동한다.
```

`EPISODE_CONTROLLER_STRESS_AUDIT_KO.md`는 이 positive result가 policy-selection artifact인지 subject-LOO로 검증한다. 전체 OOF에서 best policy를 고르는 대신, 한 subject를 완전히 빼고 policy를 고른 뒤 held-out subject에서 평가했다.

현재 핵심 결과:

- full best policy OOF: `0.629771`
- subject-LOO selected-policy OOF: `0.639997`
- subject-LOO delta vs raw: `+0.003000`
- subject-LOO positive subject rate: `0.000000`
- verdict: `policy_selection_artifact_risk`

현재 해석:

```text
episode action-space restriction은 full OOF에서는 강하지만,
subject-LOO policy selection에서는 무너진다.
따라서 이 구조는 제출 후보/센서로는 정보량이 높지만,
논문 주장으로는 아직 subject-general controller가 아니라
episode-conditioned policy overfit 위험을 가진다.
다음 단계는 full OOF best policy가 아니라 subject-invariant controller objective다.
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

### 14. HS-JEPA JEPA Contract

HS-JEPA가 단순 대회 adapter가 아니라 JEPA 계열 아키텍처로 읽히려면,
각 실험이 다음 mapping을 분명히 가져야 한다.

```text
visible human context
  -> hidden target representation prediction
  -> listener/action responsibility
  -> action-health energy
  -> invariant-preserving sparse decoder
```

이 contract를 별도 문서로 정리했다.

- `paper_hsjepa_core/HS_JEPA_JEPA_CONTRACT_KO.md`

### 15. Subject-Invariant Episode Controller

```bash
python3 sleep_competition_adapter/episode_action_space_restriction_decoder.py
python3 sleep_competition_adapter/subject_invariant_episode_controller.py
```

이 스크립트는 episode action-space controller가 특정 subject tail에만 맞은
artifact인지 검증한다.

현재 결과:

- full OOF best restricted logloss: `0.629771`
- subject-invariant objective의 subject-LOO logloss: `0.636997`
- raw OOF logloss: `0.636997`
- verdict: `subject_invariant_selector_is_safe_but_inactive`

해석:

- episode controller는 full OOF에서는 강하지만 subject-general law로 바로
  주장하기 어렵다.
- 안전한 subject-invariant objective를 걸면 held-out subject에서 action을
  거의 하지 않는 쪽으로 수렴한다.
- 즉 row episode state는 신호가 있지만, 그대로 release policy로 쓰면
  subject-specific action tail에 묶일 수 있다.

자세한 설명:

- `paper_hsjepa_core/SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md`

### 16. Cross-Subject Episode Prototype Transport

```bash
python3 sleep_competition_adapter/cross_subject_episode_prototype_transport.py
```

이 스크립트는 위 실패를 해결하기 위해, 같은 subject 안의 과거 action을
그대로 쓰지 않고 다른 subject에서 성공한 episode-action prototype을
비슷한 row-target-route로 전이한다.

현재 결과:

- raw OOF logloss: `0.636997`
- best transport OOF logloss: `0.629211`
- best delta vs raw: `-0.007786`
- robust release OOF logloss: `0.630158`
- robust release delta vs raw: `-0.006840`
- robust release active subjects: `7`
- robust release negative active subjects: `1`
- generated candidate: `submission_hsjepa_cross_subject_episode_prototype_transport_b034ce3b_uploadsafe.csv`

해석:

- HS-JEPA episode state를 특정 사람의 label memory가 아니라
  cross-subject state-action prototype geometry로 쓰면 subject tail 의존이
  줄어든다.
- 이것은 HS-JEPA가 인간 생활 상태를 “개인 내부 기억”이 아니라
  “다른 사람에게도 전이 가능한 action representation”으로 복원할 수 있다는
  더 일반적인 논문용 증거다.
- 현재까지의 가장 강한 architecture-first positive result다.

자세한 설명:

- `paper_hsjepa_core/CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md`

### 17. Masked View Surprise Action Release

```bash
python3 sleep_competition_adapter/masked_view_surprise_action_release.py
```

이 스크립트는 HS-JEPA를 더 직접적인 JEPA 문제로 만든다.
calendar/phone/body/app/mobility 중 하나의 view를 가리고,
나머지 view로 target-view PCA representation을 예측한다.
그 예측 residual energy가 큰 row를 hidden human-state episode로 보고,
target prevalence law와 neighbor margin이 동의하는 row-target action만 release한다.

현재 결과:

- public LB ledger 사용: `False`
- action teacher for support 사용: `False`
- proprietary embedding API 사용: `False`
- strongest target surprise law: Q3 phone-device surprise, prevalence shift `-0.176991`
- Q2 app/social surprise shift: `+0.168142`
- S3 body/sleep/activity surprise shift: `+0.150442`
- row-state frontier top 30% recall: `0.355556`
- random 대비 recall lift: `+0.055556`
- generated candidate: `submission_hsjepa_masked_view_surprise_action_release_14472506_uploadsafe.csv`

해석:

- 이 실험의 강한 증거는 frontier overlap보다 target prevalence shift다.
- HS-JEPA core가 label classifier라기보다, 생활 context의 predictability break를
  hidden episode energy로 바꾸는 architecture라는 주장을 강화한다.
- frontier overlap lift는 작으므로, 이 실험만으로 action-grade decoder가 완성됐다고
  주장하면 안 된다.

자세한 설명:

- `paper_hsjepa_core/MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md`

### 18. Surprise Responsibility Toxicity Veto

```bash
python3 sleep_competition_adapter/surprise_responsibility_toxicity_veto.py
```

이 스크립트는 masked-view residual energy를 action 생성기가 아니라
target별 listener responsibility로 사용한다. 즉 `surprise가 큰 row를 움직인다`가
아니라, `이 target은 high-surprise listener를 믿을지, low-surprise listener를
믿을지, 아니면 전체 action을 유지할지`를 OOF action gain으로 고른다.

현재 결과:

- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- source decoder: `episode_action_space_restriction_decoder`
- original OOF release cells: `44`
- original OOF gain sum: `5.311535`
- surprise-veto kept cells: `32`
- kept gain sum: `5.542476`
- removed gain sum: `-0.230941`
- original positive gain rate: `0.704545`
- kept positive gain rate: `0.781250`
- generated candidate: `submission_hsjepa_surprise_responsibility_toxicity_veto_5e3d6e26_uploadsafe.csv`

해석:

- masked-view surprise energy는 넓은 action을 직접 만드는 장치보다
  target listener responsibility / toxicity veto로 더 자연스럽게 작동한다.
- OOF에서는 독성 cell을 일부 제거한다.
- 하지만 release OOF가 `id02`, `id09` 두 subject에 몰려 있어 subject-heldout
  stress는 강한 검증이 아니다. 논문에서는 positive evidence와 subject-tail
  한계를 같이 말해야 한다.

자세한 설명:

- `paper_hsjepa_core/SURPRISE_RESPONSIBILITY_TOXICITY_VETO_KO.md`

### 19. Subject-Heldout Route Responsibility Diagnostic

```bash
python3 sleep_competition_adapter/subject_heldout_route_responsibility_diagnostic.py
```

이 스크립트는 subject-balanced route conservation이 진짜 subject-general law인지,
아니면 모든 subject를 본 상태에서만 좋아 보이는 balancing artifact인지 검사한다.

검증 방식:

```text
held-out subject를 완전히 제거
  -> 나머지 subject로 target-route policy 선택
  -> held-out subject에만 선택 policy 적용
  -> realized row-target action gain 측정
```

현재 결과:

- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- verdict: `subject_heldout_route_responsibility_negative_or_fragile`
- heldout selected cells: `251`
- heldout gain sum: `-5.128700`
- heldout positive gain rate: `0.585657`
- positive heldout subjects: `4`
- negative heldout subjects: `6`
- stable targets: `Q3`, `S4`
- stable OOF gain sum: `+4.434772`
- released test cells: `42`
- generated candidate: `submission_hsjepa_subject_heldout_route_responsibility_anchor_free_f2a44231_uploadsafe.csv`

해석:

- subject-balanced route law는 모든 subject를 본 OOF audit에서는 강했지만,
  subject-heldout selection에서는 전체 gain이 음수로 무너졌다.
- 따라서 target-route conservation decoder를 그대로 subject-general HS-JEPA law라고
  주장하면 안 된다.
- 다만 Q3/S4 route는 조건부로 살아남았다. 다음 architecture claim은 전체 sparse
  action release가 아니라 target별 listener responsibility와 subject-heldout
  action toxicity field를 분리하는 방향이어야 한다.

자세한 설명:

- `paper_hsjepa_core/SUBJECT_HELDOUT_ROUTE_RESPONSIBILITY_DIAGNOSTIC_KO.md`

### 20. Subject-Heldout Action Toxicity Field

```bash
python3 sleep_competition_adapter/subject_heldout_action_toxicity_field.py
```

이 스크립트는 route policy를 고르는 대신, row-target-action 자체를 예측 단위로 낮춘다.
각 row-target cell에 대해 두 action 후보를 만든다.

```text
raw_memory_release
inverse_toxic_memory
```

그리고 HS-JEPA masked world-state residual/energy와 listener-conditioned support context가
어떤 action이 건강한지 subject-heldout으로 예측하는지 본다.

현재 결과:

- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- verdict: `subject_heldout_action_toxicity_negative_or_fragile`
- action-health AUC: `0.597026`
- action-health AP: `0.567465`
- full OOF selected cells: `57`
- full OOF gain sum: `+1.190091`
- nested heldout selected cells: `112`
- nested heldout gain sum: `-5.538044`
- nested positive/negative subjects: `2/8`
- stable targets: none
- released test cells: `0`
- generated candidate: `submission_hsjepa_subject_heldout_action_toxicity_field_anchor_free_84bb9983_uploadsafe.csv`

해석:

- core representation은 action toxicity를 완전히 못 읽는 것이 아니다. AUC/AP는 base rate보다
  유의미하게 높다.
- 하지만 이 신호를 nested subject-heldout release로 번역하면 무너진다.
- 따라서 현재 HS-JEPA core는 hidden action-health geometry의 단서를 제공하지만,
  release-grade decoder에는 subject-invariant responsibility/assignment가 더 필요하다.
- 이 실험은 `core evidence`와 `adapter success`를 분리해야 한다는 논문 구조를 강화한다.

자세한 설명:

- `paper_hsjepa_core/SUBJECT_HELDOUT_ACTION_TOXICITY_FIELD_KO.md`

### 21. Subject-Relative Responsibility Assignment

```bash
python3 sleep_competition_adapter/subject_relative_responsibility_assignment.py
```

이 스크립트는 subject-heldout action-health score가 release로 무너진 이유가
절대 점수 calibration 문제인지 검사한다.

같은 HS-JEPA action-health score를 다음 좌표계로 바꿔 비교했다.

- raw `health_score`
- `subject_relative_responsibility`
- `pairwise_responsibility`
- `support_aligned_responsibility`
- `conservative_pair_best_responsibility`

현재 결과:

- public LB ledger 사용: `False`
- prior submission probability 사용: `False`
- proprietary embedding API 사용: `False`
- verdict: `subject_relative_assignment_negative_or_fragile`
- action-health AUC/AP: `0.597026` / `0.567465`
- best coordinate: `pairwise_responsibility`
- best nested heldout gain: `-1.188289`
- previous absolute toxicity nested gain: `-5.538044`
- best positive/negative subjects: `5/5`
- stable targets: `S4`
- stable OOF gain sum: `+0.825558`
- released test cells: `8`
- generated candidate: `submission_hsjepa_subject_relative_responsibility_assignment_anchor_free_eecb4e37_uploadsafe.csv`

해석:

- subject-relative/pairwise coordinate는 absolute health score보다 훨씬 덜 무너졌다.
- 따라서 HS-JEPA core signal의 병목 중 일부는 signal absence가 아니라 calibration coordinate였다.
- 그러나 전체 nested gain은 여전히 음수이고, strict stable target은 S4뿐이다.
- 논문에서는 `subject-relative responsibility assignment`를 성공한 최종 decoder가 아니라,
  core action-health geometry를 안전한 action으로 바꾸는 데 필요한 adapter layer 후보로 설명해야 한다.

자세한 설명:

- `paper_hsjepa_core/SUBJECT_RELATIVE_RESPONSIBILITY_ASSIGNMENT_KO.md`
