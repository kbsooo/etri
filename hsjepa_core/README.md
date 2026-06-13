# HS-JEPA Core

이 디렉토리는 HS-JEPA를 특정 대회 target, public LB, S2 bridge와 분리한 일반 아키텍처로 정의한다.

핵심은 다음이다.

```text
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation
```

Transformer에서 BPE가 입력을 준비하는 층이고 attention이 핵심 기술인 것처럼, HS-JEPA에서 sleep-specific feature engineering과 public-sensor decoding은 adapter이고, 위 구조가 core다.

## JEPA Contract

HS-JEPA의 JEPA성은 모델 이름이 아니라 다음 contract에서 나온다.

```text
visible human context
  -> predict hidden target representation
  -> decode action-health under invariant constraints
```

여기서 target representation은 raw label이 아니다. hidden episode, listener route, action prototype, correction field처럼 label이 만들어지는 중간 구조다.

자세한 논문용 정리는 다음 문서에 둔다.

- `paper_hsjepa_core/HS_JEPA_CORE_FIRST_THESIS_KO.md`
- `paper_hsjepa_core/HS_JEPA_JEPA_CONTRACT_KO.md`

## 생성

```bash
python3 hsjepa_core/build_core_architecture_manifest.py
python3 hsjepa_core/run_core_reference_demo.py
python3 hsjepa_core/run_core_module_benchmark.py
python3 hsjepa_core/run_lifelog_core_state_evidence.py
python3 hsjepa_core/run_masked_context_world_model.py
python3 hsjepa_core/run_action_support_world_model_core.py
python3 hsjepa_core/run_action_support_view_invariance_core.py
python3 hsjepa_core/run_listener_conditioned_action_support_core.py
python3 hsjepa_core/run_subject_contrastive_action_support_core.py
python3 hsjepa_core/run_tail_safe_expected_utility_core.py
python3 hsjepa_core/run_subject_normalized_tail_field_core.py
python3 hsjepa_core/run_episode_conditioned_relative_tail_core.py
python3 hsjepa_core/run_masked_view_consensus_tail_core.py
python3 hsjepa_core/run_action_free_vulnerability_gate_core.py
python3 hsjepa_core/run_counterfactual_directional_action_health_core.py
python3 hsjepa_core/run_core_student_recovers_masked_tail_teacher.py
python3 hsjepa_core/run_subject_invariant_masked_tail_jury_core.py
python3 hsjepa_core/run_subject_invariant_listener_manifold_core.py
python3 hsjepa_core/run_open_loop_human_state_listener_core.py
python3 hsjepa_core/run_masked_human_state_pretext_listener_core.py
python3 hsjepa_core/run_subject_invariant_listener_responsibility_field_core.py
python3 hsjepa_core/run_signed_listener_responsibility_direction_core.py
python3 hsjepa_core/run_counterfactual_direction_pretext_core.py
python3 hsjepa_core/build_core_evidence_ledger.py
```

## 산출물

- `hsjepa_core/outputs/hsjepa_core_manifest.json`
- `hsjepa_core/outputs/hsjepa_core_manifest_ko.md`
- `hsjepa_core/outputs/hsjepa_core_ablation_contract.json`
- `hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md`
- `hsjepa_core/outputs/hsjepa_core_reference_run.json`
- `hsjepa_core/outputs/hsjepa_core_reference_run_ko.md`
- `hsjepa_core/outputs/hsjepa_core_module_benchmark.json`
- `hsjepa_core/outputs/hsjepa_core_module_benchmark_ko.md`
- `hsjepa_core/outputs/hsjepa_core_module_benchmark_cases.csv`
- `hsjepa_core/outputs/lifelog_core_state_evidence/lifelog_core_state_evidence_summary.json`
- `hsjepa_core/outputs/lifelog_core_state_evidence/lifelog_core_state_evidence_ko.md`
- `hsjepa_core/outputs/lifelog_core_state_evidence/*_metrics.csv`
- `hsjepa_core/outputs/masked_context_world_model/masked_context_world_model_summary.json`
- `hsjepa_core/outputs/masked_context_world_model/MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md`
- `hsjepa_core/outputs/masked_context_world_model/*_metrics.csv`
- `hsjepa_core/outputs/action_support_world_model_core/action_support_world_model_core_summary.json`
- `hsjepa_core/outputs/action_support_world_model_core/ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md`
- `hsjepa_core/outputs/action_support_world_model_core/*_metrics.csv`
- `hsjepa_core/outputs/action_support_view_invariance_core/action_support_view_invariance_core_summary.json`
- `hsjepa_core/outputs/action_support_view_invariance_core/ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md`
- `hsjepa_core/outputs/action_support_view_invariance_core/*_metrics.csv`
- `hsjepa_core/outputs/listener_conditioned_action_support_core/listener_conditioned_action_support_core_summary.json`
- `hsjepa_core/outputs/listener_conditioned_action_support_core/LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md`
- `hsjepa_core/outputs/listener_conditioned_action_support_core/*_metrics.csv`
- `hsjepa_core/outputs/subject_contrastive_action_support_core/subject_contrastive_action_support_core_summary.json`
- `hsjepa_core/outputs/subject_contrastive_action_support_core/SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md`
- `hsjepa_core/outputs/subject_contrastive_action_support_core/*_metrics.csv`
- `hsjepa_core/outputs/tail_safe_expected_utility_core/tail_safe_expected_utility_core_summary.json`
- `hsjepa_core/outputs/tail_safe_expected_utility_core/TAIL_SAFE_EXPECTED_UTILITY_CORE_KO.md`
- `hsjepa_core/outputs/tail_safe_expected_utility_core/*_metrics.csv`
- `hsjepa_core/outputs/subject_normalized_tail_field_core/subject_normalized_tail_field_core_summary.json`
- `hsjepa_core/outputs/subject_normalized_tail_field_core/SUBJECT_NORMALIZED_TAIL_FIELD_CORE_KO.md`
- `hsjepa_core/outputs/subject_normalized_tail_field_core/*_metrics.csv`
- `hsjepa_core/outputs/episode_conditioned_relative_tail_core/episode_conditioned_relative_tail_core_summary.json`
- `hsjepa_core/outputs/episode_conditioned_relative_tail_core/EPISODE_CONDITIONED_RELATIVE_TAIL_CORE_KO.md`
- `hsjepa_core/outputs/episode_conditioned_relative_tail_core/*_metrics.csv`
- `hsjepa_core/outputs/masked_view_consensus_tail_core/masked_view_consensus_tail_core_summary.json`
- `hsjepa_core/outputs/masked_view_consensus_tail_core/MASKED_VIEW_CONSENSUS_TAIL_CORE_KO.md`
- `hsjepa_core/outputs/masked_view_consensus_tail_core/*_metrics.csv`
- `hsjepa_core/outputs/action_free_vulnerability_gate_core/action_free_vulnerability_gate_core_summary.json`
- `hsjepa_core/outputs/action_free_vulnerability_gate_core/ACTION_FREE_VULNERABILITY_GATE_CORE_KO.md`
- `hsjepa_core/outputs/action_free_vulnerability_gate_core/*_metrics.csv`
- `hsjepa_core/outputs/counterfactual_directional_action_health_core/counterfactual_directional_action_health_core_summary.json`
- `hsjepa_core/outputs/counterfactual_directional_action_health_core/COUNTERFACTUAL_DIRECTIONAL_ACTION_HEALTH_CORE_KO.md`
- `hsjepa_core/outputs/counterfactual_directional_action_health_core/*_metrics.csv`
- `hsjepa_core/outputs/core_student_recovers_masked_tail_teacher/core_student_recovers_masked_tail_teacher_summary.json`
- `hsjepa_core/outputs/core_student_recovers_masked_tail_teacher/CORE_STUDENT_RECOVERS_MASKED_TAIL_TEACHER_KO.md`
- `hsjepa_core/outputs/core_student_recovers_masked_tail_teacher/*_metrics.csv`
- `hsjepa_core/outputs/subject_invariant_masked_tail_jury_core/subject_invariant_masked_tail_jury_core_summary.json`
- `hsjepa_core/outputs/subject_invariant_masked_tail_jury_core/SUBJECT_INVARIANT_MASKED_TAIL_JURY_CORE_KO.md`
- `hsjepa_core/outputs/subject_invariant_masked_tail_jury_core/*.csv`
- `hsjepa_core/outputs/subject_invariant_listener_manifold_core/subject_invariant_listener_manifold_core_summary.json`
- `hsjepa_core/outputs/subject_invariant_listener_manifold_core/SUBJECT_INVARIANT_LISTENER_MANIFOLD_CORE_KO.md`
- `hsjepa_core/outputs/subject_invariant_listener_manifold_core/*.csv`
- `hsjepa_core/outputs/open_loop_human_state_listener_core/open_loop_human_state_listener_core_summary.json`
- `hsjepa_core/outputs/open_loop_human_state_listener_core/OPEN_LOOP_HUMAN_STATE_LISTENER_CORE_KO.md`
- `hsjepa_core/outputs/open_loop_human_state_listener_core/*.csv`
- `hsjepa_core/outputs/masked_human_state_pretext_listener_core/masked_human_state_pretext_listener_core_summary.json`
- `hsjepa_core/outputs/masked_human_state_pretext_listener_core/MASKED_HUMAN_STATE_PRETEXT_LISTENER_CORE_KO.md`
- `hsjepa_core/outputs/masked_human_state_pretext_listener_core/*.csv`
- `hsjepa_core/outputs/subject_invariant_listener_responsibility_field_core/subject_invariant_listener_responsibility_field_core_summary.json`
- `hsjepa_core/outputs/subject_invariant_listener_responsibility_field_core/SUBJECT_INVARIANT_LISTENER_RESPONSIBILITY_FIELD_CORE_KO.md`
- `hsjepa_core/outputs/subject_invariant_listener_responsibility_field_core/*.csv`
- `hsjepa_core/outputs/signed_listener_responsibility_direction_core/signed_listener_responsibility_direction_core_summary.json`
- `hsjepa_core/outputs/signed_listener_responsibility_direction_core/SIGNED_LISTENER_RESPONSIBILITY_DIRECTION_CORE_KO.md`
- `hsjepa_core/outputs/signed_listener_responsibility_direction_core/*.csv`
- `hsjepa_core/outputs/counterfactual_direction_pretext_core/counterfactual_direction_pretext_core_summary.json`
- `hsjepa_core/outputs/counterfactual_direction_pretext_core/COUNTERFACTUAL_DIRECTION_PRETEXT_CORE_KO.md`
- `hsjepa_core/outputs/counterfactual_direction_pretext_core/*.csv`
- `hsjepa_core/outputs/core_evidence_ledger/core_evidence_ledger_summary.json`
- `hsjepa_core/outputs/core_evidence_ledger/CORE_EVIDENCE_LEDGER_KO.md`

## 실행 가능한 core

- `hsjepa_core/core.py`: dataset adapter 없이 hidden state, listener responsibility, action-health, invariant energy를 계산하는 reference implementation.
- `hsjepa_core/run_core_reference_demo.py`: synthetic context/listener/action으로 module removal behavior를 보여주는 reference run.
- `hsjepa_core/run_core_module_benchmark.py`: 여러 generic human-state scenario에서 full core와 module-removal policy를 비교하는 dataset-free benchmark.
- `hsjepa_core/run_lifelog_core_state_evidence.py`: public LB 없이 OG lifelog-derived feature table만으로 core-state representation의 label manifold, masked-view prediction, nearest-neighbor consistency, external action replay를 검증하는 real-data evidence run.
- `hsjepa_core/run_masked_context_world_model.py`: semantic lifelog view를 하나씩 mask하고 나머지 view로 target-view PCA representation을 예측해, explicit HS-JEPA world-model state와 residual energy를 만든다.
- `hsjepa_core/run_action_support_world_model_core.py`: train label만으로 raw lifelog-memory action의 success/toxicity target을 만들고, HS-JEPA masked world-state가 subject-heldout으로 action-support를 예측하는지 검증한다.
- `hsjepa_core/run_action_support_view_invariance_core.py`: action-support 신호가 target/action shortcut인지, single-view artifact인지, masked world-state residual/energy 신호인지 stress한다.
- `hsjepa_core/run_listener_conditioned_action_support_core.py`: target-blind world state가 부족한지 확인하기 위해 target/family listener-conditioned residual/energy support predictor를 검증한다.
- `hsjepa_core/run_subject_contrastive_action_support_core.py`: 같은 subject-target 내부 pairwise ordering으로 subject/target shortcut을 제거하고, masked world residual energy가 episode-level action-health ordering을 복원하는지 검증한다.
- `hsjepa_core/run_tail_safe_expected_utility_core.py`: action-health를 AUC 문제가 아니라 Log Loss expected gain과 negative-tail risk 문제로 바꾸어, HS-JEPA core geometry가 release-grade utility로 번역되는지 subject-heldout stress까지 검증한다.
- `hsjepa_core/run_subject_normalized_tail_field_core.py`: absolute action utility 대신 subject-target-action route 내부 tail scale로 정규화한 relative badness를 예측해, subject shift에서 S-tail 독성이 줄어드는지 검증한다.
- `hsjepa_core/run_episode_conditioned_relative_tail_core.py`: subject-relative badness가 아직 거칠다는 가설을 검사하기 위해 row episode context를 추가하고, 보이는 episode context로 보이지 않는 episode-conditioned tail representation을 예측한다.
- `hsjepa_core/run_masked_view_consensus_tail_core.py`: full/세계잔차마스크/episode마스크/listener마스크 view가 같은 episode-conditioned tail representation에 동의하는 cell만 release해, hidden tail field가 single-view shortcut인지 검사한다.
- `hsjepa_core/run_action_free_vulnerability_gate_core.py`: action/probability/support 입력 없이 row-target vulnerability를 예측해 masked-view action decoder를 gate할 수 있는지 검사한다. 현재 결과는 negative sensor다.
- `hsjepa_core/run_counterfactual_directional_action_health_core.py`: action probability/magnitude 없이 counterfactual up/down direction listener만으로 hidden action-health를 예측할 수 있는지 검사한다. 현재 결과는 negative sensor다.
- `hsjepa_core/run_core_student_recovers_masked_tail_teacher.py`: masked-view consensus tail teacher의 hidden representation을 action probability/magnitude/support 없이 core student가 복원할 수 있는지 검사한다. 현재 결과는 OOF positive / subject-heldout negative sensor다.
- `hsjepa_core/run_subject_invariant_masked_tail_jury_core.py`: masked-view consensus teacher를 subject-excluded jury로 다시 읽어, subject를 하나씩 가려도 같은 hidden-tail action이 살아남는지 검사한다. 현재 결과는 subject-heldout positive다.
- `hsjepa_core/run_subject_invariant_listener_manifold_core.py`: subject-invariant jury release가 HS-JEPA hidden representation 공간에서 action-only baseline보다 잘 분리되는지 검사한다. 현재 결과는 listener-manifold positive다.
- `hsjepa_core/run_open_loop_human_state_listener_core.py`: masked-tail teacher와 action probability/magnitude를 제외하고, OG human-state + minimal listener만으로 subject-invariant action-health support를 복원할 수 있는지 검사한다. 현재 결과는 mixed boundary다.
- `hsjepa_core/run_masked_human_state_pretext_listener_core.py`: raw OG human-state를 바로 decoder에 넣지 않고 masked-view pretext state로 바꾼 뒤, subject-invariant action-health support가 더 잘 분리되는지 검사한다. 현재 결과는 raw open-loop 대비 소폭 positive / listener-only 대비 negative다.
- `hsjepa_core/run_subject_invariant_listener_responsibility_field_core.py`: action을 직접 예측하기 전에 row-target listener responsibility field를 복원할 수 있는지 검사한다. 현재 결과는 core responsibility positive / action translation fragile이다.
- `hsjepa_core/run_signed_listener_responsibility_direction_core.py`: responsibility-high cell 내부에서 raw/inverse signed action direction을 예측해 action translation toxicity를 줄일 수 있는지 검사한다. 현재 결과는 responsibility core + action-geometry direction adapter positive다.
- `hsjepa_core/run_counterfactual_direction_pretext_core.py`: raw/inverse direction을 action-probability-free counterfactual hidden target으로 끌어올려, HS-JEPA core가 direction까지 복원하는지 검사한다. 현재 결과는 negative boundary다.
- `hsjepa_core/build_core_evidence_ledger.py`: public-free core evidence를 하나의 논문용 ledger로 묶어, 무엇이 HS-JEPA core 증거이고 무엇이 adapter/diagnostic boundary인지 분리한다.

## 팀 공유 시 주의점

`Cross-Subject Episode Prototype Transport`, `Target-Route Guarded Action-Episode Transport`,
`Target-Route Conservation Decoder`, `Subject-Balanced Route Conservation Decoder`,
`Subject-Heldout Route Responsibility Diagnostic`, `Subject-Heldout Action Toxicity Field`,
`Subject-Relative Responsibility Assignment`, `Subject-Invariant Episode Controller`
같은 문서는 HS-JEPA core 자체가 아니다.

- cross-subject/action-episode transport: core representation의 adapter/probe
- target-route guard: competition-specific action decoder
- target-route conservation decoder: listener-conditioned core signal을 Q/S target route별
  release/inverse/hold action으로 번역하는 competition adapter
- subject-balanced route conservation decoder: 위 adapter가 subject-tail shortcut인지 확인하는
  LeJEPA-style diagnostic adapter
- subject-heldout route responsibility diagnostic: target-route law가 subject를 완전히 가린
  선택-평가에서도 살아남는지 보는 LeJEPA-style diagnostic adapter
- subject-heldout action toxicity field: core representation이 row-target-action 독성을
  subject-heldout에서 읽는지와 release decoder가 안전한지 분리하는 diagnostic adapter
- subject-relative responsibility assignment: action-health score를 subject-relative/pairwise
  좌표계로 바꾸어 calibration 병목인지 검증하는 assignment adapter
- subject-invariant controller: LeJEPA-style anti-shortcut diagnostic

이들을 먼저 설명하면 HS-JEPA가 row-target 후처리처럼 보인다.
팀원에게는 `core.py`와 masked context world-model을 먼저 보여주고,
그 다음 adapter case study로 넘어가야 한다.

## Real-Data Core Evidence

`run_lifelog_core_state_evidence.py`는 HS-JEPA core가 대회용 submission trick이 아니라는 점을 검증하기 위한 실험이다.

분리 원칙:

- public score ledger를 읽지 않는다.
- proprietary embedding API를 쓰지 않는다.
- `peer_margin_*`, `target_route_margin_*` 같은 label-informed feature는 core-only 검증에서 제외한다.
- external action replay는 core 증명이 아니라 adapter 진단으로 분리해서 보고한다.

현재 핵심 결과:

- HS-JEPA state-only는 subject-holdout label logloss에서 prior를 이기지 못했다. 즉 core를 직접 label classifier로 과장하면 안 된다.
- nearest-neighbor target consistency는 random 대비 `+0.0506` lift를 보였다.
- masked context prediction은 phone/app/body view에서 null 대비 component-correlation lift를 보였다.
- external adapter action replay에서는 core-state geometry만으로 평균 row AUC `0.9543`, recall@k `0.8386`, permutation z `8.38`을 보였다.

따라서 현재 논문 주장은 다음이 가장 정확하다.

```text
HS-JEPA core is not a standalone label predictor.
It is a human-state geometry that makes row-action support and action-health
more recoverable before the competition adapter releases a sparse correction.
```

## Explicit Masked Context World Model

`run_masked_context_world_model.py`는 HS-JEPA core를 더 직접적인 JEPA 형태로 검증한다.

```text
visible lifelog views
  -> predict masked target-view representation
  -> predicted state + residual surprise energy
  -> label/action structure probe
```

현재 핵심 결과:

- best masked target view는 `app_social_context`이고, null 대비 component-correlation lift는 `+0.248882`다.
- masked world-model predicted state의 nearest-neighbor target match lift는 `+0.031302`다.
- 하지만 grouped label probe에서 world full-state mean logloss는 `1.122751`로 prior `0.677858`보다 나쁘다.
- anchor-free world-model KNN OOF logloss는 calibration 후 `0.715135`다.
- action-health diagnostic에서는 S3 app/social low-energy listener가 gain `0.945472 -> 1.487267`, S4 calendar high-energy listener가 gain `-0.425003 -> 0.099617`로 toxic pocket을 분리했다.
- diagnostic candidate: `submission_hsjepa_masked_context_world_model_core_ff673c9a_uploadsafe.csv`

해석:

```text
Masked context prediction은 JEPA-style hidden representation으로 의미가 있다.
하지만 이 representation을 direct label predictor로 쓰면 실패한다.
따라서 HS-JEPA core는 classifier가 아니라, adapter가 사용할 action-health/surprise geometry다.
```

## Action-Support World Model Core

`run_action_support_world_model_core.py`는 HS-JEPA core가 label을 직접 맞히는 대신
row-target action의 health/toxicity를 읽는다는 주장을 더 직접적으로 검증한다.

```text
visible lifelog context
  -> masked human-state world model
  -> raw-memory action-support/toxicity representation
  -> anchor-free sparse correction sensor
```

분리 원칙:

- public score ledger를 읽지 않는다.
- 기존 best submission probability를 읽지 않는다.
- proprietary embedding API를 쓰지 않는다.
- action-support target은 train-fold prior 대비 raw lifelog KNN memory의 realized logloss gain으로 만든다.

현재 핵심 결과:

- raw lifelog memory action은 전체 OOF에서 prior보다 나쁘다: gain sum `-48.053725`.
- HS-JEPA masked world full-state의 support AUC/AP는 `0.539592` / `0.530735`다.
- 낮은 support score의 decisive actions를 inverse-toxic decoder로 뒤집으면 selected OOF gain sum `+2.621567`을 얻었다.
- target-shuffle null 대비 gain lift는 `+6.164069`, z-score는 `2.636913`이다.
- anchor-free candidate: `submission_hsjepa_action_support_world_model_anchor_free_9da5d2f1_uploadsafe.csv`

해석:

```text
HS-JEPA core는 broad raw-memory action generator가 아니다.
하지만 action을 release하기 전에 어떤 row-target action이 toxic한지 구분하는
world-state/action-support geometry를 제공한다.
```

## Action-Support View Invariance Core

`run_action_support_view_invariance_core.py`는 위 action-support 결과를 더 엄격하게 찌른다.
같은 train-only action-support target을 두고 target/action-only baseline, target-blind world state,
single-view world state, leave-one-view-out world state를 비교한다.

현재 핵심 결과:

- selected feature set: `world_residual_energy`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- support AUC/AP: `0.542555` / `0.536845`
- selected OOF gain sum: `+6.146252`
- target-shuffle null 대비 gain lift: `+9.817777`, z-score `2.942742`
- target/action-only baseline은 selected gain `-4.107447`로 실패했다.
- target-blind world full-state는 baseline보다는 낫지만 selected gain `-0.320604`로 아직 positive는 아니다.
- anchor-free candidate: `submission_hsjepa_action_support_view_invariance_anchor_free_84071a4b_uploadsafe.csv`

해석:

```text
HS-JEPA world-state residual/energy는 target/action-only shortcut보다 강한 action-support 신호를 가진다.
하지만 완전한 target-invariant core라고 주장하기에는 아직 부족하고,
listener/target route conditioning이 필요한 상태다.
```

## Listener-Conditioned Action-Support Core

`run_listener_conditioned_action_support_core.py`는 target-blind stress의 다음 단계다.
HS-JEPA residual/energy world state를 target/family listener와 결합했을 때
action-support가 실제로 좋아지는지 확인한다.

현재 핵심 결과:

- selected feature set: `target_interaction_world_residual_energy`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- support AUC/AP: `0.611128` / `0.600888`
- selected OOF gain sum: `+6.192500`
- target-shuffle null 대비 gain lift: `+10.137463`, z-score `2.610537`
- target/action-only baseline selected gain: `+1.543383`
- global world residual/energy selected gain: `-1.955206`
- target-heldout transfer AUC는 `0.629874`지만 selected gain은 `-2.496232`라 release law로는 아직 불안정하다.
- anchor-free candidate: `submission_hsjepa_listener_conditioned_action_support_anchor_free_efdf0586_uploadsafe.csv`

해석:

```text
HS-JEPA core는 target-free universal decoder가 아니다.
World-state residual/energy는 target listener와 결합될 때 action-support가 강해진다.
다만 cross-target listener transfer는 아직 증명되지 않았으므로,
현재 architecture claim은 listener-conditioned action-support model이다.
```

## Subject-Contrastive Action-Support Core

`run_subject_contrastive_action_support_core.py`는 core evidence를 더 일반적으로 찌른다.
일반 support classifier가 subject/target prior를 외울 수 있다는 문제를 피하기 위해,
supervision을 같은 subject + 같은 target 내부의 pairwise ordering으로 바꾼다.

```text
same subject + same target action pair
  -> which day has healthier raw-memory action?
  -> held-out subject cells scored against peer references
```

현재 핵심 결과:

- selected feature set: `binary_preference__world_residual_energy_pair`
- selected policy: `top10_all_cells`
- selected decoder: `raw_memory_release`
- support AUC/AP: `0.512922` / `0.508946`
- selected OOF gain sum: `+2.383219`
- target-shuffle null 대비 gain lift: `+7.010120`, z-score `1.526122`
- shortcut/action-only baselines는 AUC가 높아도 selected gain이 음수다.
- tail-weighted preference도 utility로 번역되지 않았다.
- anchor-free candidate: `submission_hsjepa_subject_contrastive_action_support_anchor_free_2cc6457c_uploadsafe.csv`

해석:

```text
HS-JEPA residual energy는 subject/target shortcut을 제거해도 약한 episode-level
action-health ordering을 갖는다.
하지만 AUC가 높은 score가 Log Loss utility를 보장하지 않는다.
따라서 HS-JEPA core 주장은 "ranking classifier"가 아니라
tail-safe action-health geometry와 decoder 분리까지 포함해야 한다.
```

## Tail-Safe Expected Utility Core

`run_tail_safe_expected_utility_core.py`는 subject-contrastive 실험의 가장 중요한 모순을 직접 다룬다.
action-health AUC가 좋아도 Log Loss utility가 망가질 수 있으므로,
HS-JEPA core score를 건강한 action 확률로 쓰지 않고 expected gain과 negative-tail risk로 다시 예측한다.

```text
masked world-state residual/energy
  -> listener + subject-contrastive support context
  -> expected gain / tail loss / toxic-tail probability
  -> tail-safe row-target-action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+10.396344`
- full OOF selected cells: `106`
- nested subject-heldout gain sum: `-8.823949`
- stable target after heldout filtering: `Q1`
- stable OOF gain sum: `+2.143778`
- released test cells: `7`
- toxic-tail AUC/AP: `0.692999` / `0.539363`
- anchor-free candidate: `submission_hsjepa_tail_safe_expected_utility_core_anchor_free_06ca3b66_uploadsafe.csv`

해석:

```text
HS-JEPA core geometry는 expected utility와 toxic-tail signal을 읽을 수 있다.
하지만 full OOF utility가 subject-heldout release safety를 보장하지 않는다.
따라서 논문 주장은 "HS-JEPA core + tail-safe decoder가 필요하다"이지,
"core alone이 바로 submission solver다"가 아니다.
```

## Subject-Normalized Tail Field Core

`run_subject_normalized_tail_field_core.py`는 tail-safe 결과의 다음 질문을 다룬다.
full OOF expected utility는 강하지만 subject-heldout S-tail에서 깨졌기 때문에,
absolute gain 대신 subject-target-action route 내부의 tail scale로 정규화한 relative badness를 예측한다.

```text
hidden action-health / residual-energy representation
  -> subject-normalized tail field
  -> relative badness / toxic-tail probability
  -> row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+2.898288`
- nested subject-heldout gain sum: `-3.812519`
- tail-safe expected utility의 nested heldout gain `-8.823949` 대비 손실이 크게 줄었다.
- relative toxic-tail AUC/AP: `0.740461` / `0.314014`
- stable targets after heldout filtering: `Q2`, `S4`
- stable OOF gain sum: `+1.543893`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_subject_normalized_tail_field_anchor_free_d4bf6a61_uploadsafe.csv`

해석:

```text
subject-normalization은 full OOF upside를 줄였지만 subject-heldout tail damage를 절반 이상 줄였다.
따라서 HS-JEPA target representation은 absolute action utility보다
human-specific relative badness / tail field 쪽이 더 일반화될 가능성이 있다.
다만 nested gain은 여전히 음수라서 완성된 release solver는 아니다.
```

## Episode-Conditioned Relative Tail Core

`run_episode_conditioned_relative_tail_core.py`는 subject-normalized tail field의 다음 질문을 다룬다.
`이 사람 기준으로 나쁜 action`도 아직 너무 넓은 표현일 수 있으므로,
같은 subject라도 episode/reset/transition context에 따라 tail scale이 달라진다고 본다.

```text
visible episode context + hidden action-health geometry
  -> episode-conditioned relative tail representation
  -> row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+3.733608`
- nested subject-heldout gain sum: `-3.230895`
- subject-normalized tail field의 nested heldout gain `-3.812519` 대비 손실이 추가로 줄었다.
- tail-safe expected utility의 nested heldout gain `-8.823949` 대비로는 훨씬 덜 독성적이다.
- stable targets after heldout filtering: `Q3`, `S3`, `S4`
- stable OOF gain sum: `+1.651284`
- released test cells: `50`
- anchor-free candidate: `submission_hsjepa_episode_conditioned_relative_tail_anchor_free_56c526fc_uploadsafe.csv`

해석:

```text
episode context는 단순한 보정 feature가 아니라 hidden target representation의 조건이다.
HS-JEPA가 맞혀야 할 것은 global utility가 아니라
이 사람의 이 episode 상태에서 어떤 action이 relative tail인지에 가까워지고 있다.
다만 nested gain은 아직 음수이므로, 완성된 release solver가 아니라
core-decoder boundary를 좁힌 positive direction으로 읽어야 한다.
```

## Masked-View Consensus Tail Core

`run_masked_view_consensus_tail_core.py`는 episode-conditioned tail field의 다음 질문을 다룬다.
좋아 보이는 tail score가 single-view shortcut이면 subject-heldout에서 깨질 수 있으므로,
여러 의미 있는 context mask가 같은 hidden tail representation을 예측하는지 검사한다.

```text
full / no-world-residual / no-episode / no-listener views
  -> same hidden episode-conditioned tail representation
  -> view-disagreement penalty
  -> row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+2.779623`
- nested subject-heldout gain sum: `+0.578637`
- 이전 ladder 대비 nested gain 변화:
  - tail-safe expected utility: `-8.823949`
  - subject-normalized tail field: `-3.812519`
  - episode-conditioned relative tail: `-3.230895`
  - masked-view consensus tail: `+0.578637`
- stable targets after heldout filtering: `S2`, `S4`
- stable OOF gain sum: `+2.018205`
- released test cells: `74`
- anchor-free candidate: `submission_hsjepa_masked_view_consensus_tail_anchor_free_375886b3_uploadsafe.csv`

해석:

```text
HS-JEPA core의 hidden tail representation은 single full-context score보다
masked-view consensus로 읽을 때 subject-heldout action toxicity가 줄어든다.
처음으로 nested subject-heldout gain이 양수가 되었으므로,
paper thesis는 "human-relative tail field"에서
"masked-view invariant human-relative tail field"로 올라갈 수 있다.
단, 살아남은 route가 S2/S4에 집중되어 있으므로 universal solver라고 과장하면 안 된다.
```

## Action-Free Vulnerability Gate Core

`run_action_free_vulnerability_gate_core.py`는 masked-view consensus tail core를 더 강하게 반증하려는 실험이다.
action-aware score가 아니라 action/probability/support 입력을 제거한 core context만으로
row-target vulnerability를 먼저 예측하고, 그 score로 action decoder를 gate한다.

```text
action-free human context
  -> hidden row-target vulnerability representation
  -> gate masked-view action decoder
  -> row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+4.367758`
- nested subject-heldout gain sum: `-3.006164`
- stable targets after heldout filtering: `Q3`
- stable OOF gain sum: `+0.679489`
- released test cells: `15`
- action-free toxic vulnerability consensus AUC/AP: `0.631354` / `0.858096`
- all targets have opportunity rate `1.0`, so the opportunity label is degenerate.
- anchor-free candidate: `submission_hsjepa_action_free_vulnerability_gate_anchor_free_df083171_uploadsafe.csv`

해석:

```text
HS-JEPA core context can read broad toxic vulnerability, but action-free
vulnerability is not enough to make a safe release decoder.
The successful masked-view consensus result should not be overstated as
"core-only vulnerability solves action toxicity".
The current strongest claim remains:
masked-view invariant, action-aware tail representation reduces decoder toxicity,
especially on S2/S4.
```

## Counterfactual Directional Action-Health Core

`run_counterfactual_directional_action_health_core.py`는 action-free vulnerability의 실패를 더 날카롭게 분해한다.
vulnerability만으로는 어떤 action 방향이 안전한지 고를 수 없으므로, 확률값과 action magnitude는 숨기고
`올릴까/내릴까`라는 counterfactual direction listener만 준다.

```text
human-state context + counterfactual direction listener
  -> hidden directional action-health representation
  -> masked-view consensus
  -> row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+3.026331`
- nested subject-heldout gain sum: `-3.515635`
- stable targets after heldout filtering: none
- released test cells: `36`
- directional consensus health AUC/AP: `0.539598` / `0.528134`
- directional consensus toxic AUC/AP: `0.538226` / `0.428788`
- action probability as feature: `False`
- action magnitude as feature: `False`
- anchor-free candidate: `submission_hsjepa_counterfactual_directional_action_health_anchor_free_83d20117_uploadsafe.csv`

해석:

```text
Counterfactual direction listener alone is not enough for subject-invariant
safe assignment.  HS-JEPA can be framed as a counterfactual action-health model,
but release-grade decoding still needs richer action-tail representation:
probability/magnitude/support geometry or masked-view action-tail consensus.
```

## Core Student Recovers Masked Tail Teacher

`run_core_student_recovers_masked_tail_teacher.py`는 현재 가장 강한 positive evidence인
masked-view consensus tail teacher를 core-only student가 복원할 수 있는지 검사한다.
student는 minimal action listener(raw/inverse, up/down/no-op direction)만 보고, action probability,
action magnitude, support score는 보지 않는다.

```text
human-state context + minimal action listener
  -> recover masked-view teacher hidden tail representation
  -> sparse row-target action assignment
```

현재 핵심 결과:

- full OOF selected gain sum: `+8.078259`
- nested subject-heldout gain sum: `-3.635973`
- stable targets after heldout filtering: none
- released test cells: `87`
- student consensus teacher-top AUC/AP: `0.582875` / `0.134131`
- student consensus realized-health AUC/AP: `0.592321` / `0.560345`
- action probability as student feature: `False`
- action magnitude as student feature: `False`
- support score as student feature: `False`
- anchor-free candidate: `submission_hsjepa_core_student_recovers_masked_tail_teacher_anchor_free_2648e9b5_uploadsafe.csv`

해석:

```text
Core student can imitate enough of the teacher to create a large full-OOF gain,
but this recovery is not subject-invariant.  The current frontier should not be
claimed as core-only distillation.  The safer claim remains masked-view
action-tail teacher boundary, with core student recovery as a diagnostic.
```

## Subject-Invariant Masked-Tail Jury Core

`run_subject_invariant_masked_tail_jury_core.py`는 masked-view consensus tail teacher의 다음 질문을 다룬다.
좋아 보이는 hidden-tail action이 특정 subject의 tail shortcut이면, subject를 하나씩 가린 world에서
같은 release law가 반복해서 나오지 않아야 한다. 그래서 각 subject-excluded world를 하나의 jury로 두고,
jury가 반복해서 받아들이는 row-target-action만 candidate로 번역한다.

```text
masked visible context views
  -> hidden episode-conditioned tail representation
  -> subject-excluded policy selection
  -> jury vote over row-target-action release
  -> sparse anchor-free correction
```

현재 핵심 결과:

- strict subject-heldout gain sum: `+0.564736`
- strict subject-heldout selected cells: `174`
- release targets: `Q2`, `S1`, `S2`, `S4`
- released test cells: `63`
- parent hidden-tail state source: `parent_masked_view_state_cache`
- anchor-free candidate: `submission_hsjepa_subject_invariant_masked_tail_jury_anchor_free_12249175_uploadsafe.csv`

해석:

```text
masked-view consensus tail의 positive evidence가 subject-invariant 조건을 걸어도
거의 유지됐다.  S2/S4만 남았던 이전 stable policy보다 Q2/S1까지 작은 positive
listener로 살아난 점이 새롭다.  반대로 Q1/Q3/S3은 jury에서 죽었으므로,
HS-JEPA hidden-tail field는 universal label solver가 아니라 listener-specific
action-health representation이라고 주장해야 한다.
```

## Subject-Invariant Listener Manifold Core

`run_subject_invariant_listener_manifold_core.py`는 subject-invariant jury 결과를 한 단계 더 core 쪽에서 묻는다.
Jury가 고른 row-target-action이 단순 rule의 산물인지, 아니면 HS-JEPA hidden representation 공간에서
subject를 넘어 분리되는 action-health manifold인지 비교한다.

```text
HS-JEPA hidden representation
  -> subject-heldout listener/action-health separability probe
  -> learned listener-manifold release score
  -> sparse diagnostic correction
```

현재 핵심 결과:

- verdict: `hsjepa_listener_manifold_beats_action_geometry`
- strict jury release positive rate: `0.027619`
- action geometry only AP lift: `+0.041516`
- masked tail representation AP lift: `+0.155746`
- HS-JEPA listener manifold AP lift: `+0.233257`
- full decoder context AP lift: `+0.234538`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_subject_invariant_listener_manifold_anchor_free_40628330_uploadsafe.csv`

해석:

```text
성공/실패 action-health가 action magnitude/prior geometry만으로 설명되는 것이 아니라,
HS-JEPA hidden tail + world/episode/listener representation에서 훨씬 잘 분리된다.
full decoder context와 HS-JEPA listener manifold의 차이가 작기 때문에,
논문 주장은 "adapter rule이 우연히 맞았다"보다
"HS-JEPA representation이 subject-invariant listener/action-health manifold를 만든다"에
더 가까워졌다.
```

## Open-Loop Human-State Listener Core

`run_open_loop_human_state_listener_core.py`는 위 positive result에서 teacher 의존도를 더 줄이는
반대 실험이다. masked-tail teacher score와 action probability/magnitude를 feature에서 제외하고,
OG lifelog/social/cohort human-state와 최소 listener만으로 strict subject-invariant jury release를
복원할 수 있는지 검사한다.

```text
OG human-state context
  + target/listener route
  -> open-loop action-health support
  -> sparse diagnostic correction
```

현재 핵심 결과:

- verdict: `open_loop_human_state_beats_action_but_not_listener_only`
- listener-only AP lift: `+0.079972`
- open-loop human-state listener AP lift: `+0.062217`
- action-only AP lift: `+0.038054`
- masked-tail teacher score 사용: `False`
- label-informed peer margin 사용: `False`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_open_loop_human_state_listener_anchor_free_adfadd58_uploadsafe.csv`

해석:

```text
Open-loop human-state는 action geometry만 보는 것보다는 낫다.
하지만 listener-only baseline을 넘지 못했고 S2에서는 약하다.
따라서 현재 evidence는 "OG human-state core만으로 release-grade action-health를 복원했다"가 아니다.
강한 주장은 여전히 teacher-derived hidden-tail/listener manifold가 필요하다는 쪽이다.
이 실험은 HS-JEPA core-only 독립성을 과장하지 않게 만드는 boundary/negative sensor다.
```

## Masked Human-State Pretext Listener Core

`run_masked_human_state_pretext_listener_core.py`는 open-loop의 약점을 한 단계 더 HS-JEPA답게 찌른다.
OG human-state feature를 그대로 decoder에 넣지 않고, semantic lifelog view 하나를 가리고 나머지 view로
그 view의 PCA representation을 예측한다. 그 predicted/residual/surprise state가
subject-invariant action-health support를 raw human-state보다 잘 읽는지 비교한다.

```text
visible lifelog views
  -> predict masked human-state view representation
  -> predicted/residual/surprise state
  -> listener-conditioned action-health support
```

현재 핵심 결과:

- verdict: `masked_pretext_improves_raw_human_state_but_not_listener_only`
- best strict-jury family: `listener_only`
- best masked-pretext family: `masked_pretext_prediction_listener`
- masked-pretext AP lift: `+0.064389`
- open-loop raw human-state AP lift: `+0.062217`
- listener-only AP lift: `+0.079972`
- action-only AP lift: `+0.038054`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_masked_human_state_pretext_listener_anchor_free_c47e9223_uploadsafe.csv`

해석:

```text
Masked-pretext representation은 raw human-state보다 약간 낫다.
따라서 "raw feature가 아니라 representation이어야 한다"는 방향은 약하게 강화된다.
하지만 listener-only를 넘지 못하므로 core-only 독립 breakthrough는 아니다.
현재 strong evidence는 여전히 hidden-tail/listener manifold에 있다.
```

## Subject-Invariant Listener Responsibility Field Core

`run_subject_invariant_listener_responsibility_field_core.py`는 hidden target을 action에서
row-target listener responsibility field로 바꾼다. 즉 action을 직접 맞히는 대신,
먼저 "이 human-state에서 이 target listener가 개입할 책임이 있는가"를 예측한다.

```text
visible human-life context
  + target listener
  -> hidden listener responsibility field
  -> action decoder only after responsibility is high
```

현재 핵심 결과:

- verdict: `listener_responsibility_field_positive_action_translation_fragile`
- best responsibility family: `masked_pretext_listener_responsibility`
- masked-pretext responsibility AP lift: `+0.079078`
- human responsibility AP lift: `+0.077261`
- listener-only AP lift: `+0.064292`
- action-decoder OOF gain for release family: `-0.565668`
- listener-only action-decoder OOF gain: `-3.045468`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_subject_invariant_listener_responsibility_field_a9a2ea47_uploadsafe.csv`

해석:

```text
HS-JEPA core는 "어느 row-target listener가 책임을 져야 하는지"를
listener-only보다 잘 복원한다.  이것은 core representation evidence로는 강하다.
다만 기존 action decoder로 번역하면 gain은 아직 음수다.
따라서 다음 병목은 responsibility field 발견이 아니라,
responsibility -> safe action direction 번역이다.
```

## Signed Listener Responsibility Direction Core

`run_signed_listener_responsibility_direction_core.py`는 직전 responsibility field의 병목을 직접 겨냥한다.
먼저 HS-JEPA responsibility field로 row-target cell을 고른 뒤, 그 cell에서 raw 방향과 inverse 방향 중
어느 action이 Log Loss gain을 만드는지 signed action-health field로 예측한다.

```text
visible human-state context
  + target listener
  + raw/inverse direction listener
  -> hidden signed action-health field
  -> responsibility-high cell에서 direction-safe action release
```

현재 핵심 결과:

- verdict: `signed_direction_core_positive_action_translation_repaired`
- responsibility source: `masked_pretext_listener_responsibility`
- best direction family: `action_geometry_direction`
- best direction AP lift: `+0.114069`
- previous responsibility decoder OOF gain: `-0.565668`
- signed direction responsibility-gated OOF gain: `+1.640820`
- action-geometry direction responsibility-gated OOF gain: `+1.640820`
- released test cells: `67`
- anchor-free candidate: `submission_hsjepa_signed_listener_responsibility_direction_3a0fba1d_uploadsafe.csv`

해석:

```text
이 결과는 "HS-JEPA core만으로 direction까지 해결했다"가 아니다.
정확한 결론은 HS-JEPA masked-pretext responsibility field가 action 후보 공간을 좁히고,
그 위에서 signed direction adapter가 기존 action decoder의 독성을 양수 OOF gain으로 수리했다는 것이다.
Core evidence는 responsibility field이고, direction 선택은 core-decoder boundary / competition adapter다.
```

## Core가 아닌 것

- `S2`라는 target 이름
- public LB sensor
- Q/S route의 구체적 형태
- 특정 submission 파일명
- 250 rows x 7 targets sparse geometry

이 요소들은 `sleep_competition_adapter/`가 책임진다.
