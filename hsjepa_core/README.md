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

## 실행 가능한 core

- `hsjepa_core/core.py`: dataset adapter 없이 hidden state, listener responsibility, action-health, invariant energy를 계산하는 reference implementation.
- `hsjepa_core/run_core_reference_demo.py`: synthetic context/listener/action으로 module removal behavior를 보여주는 reference run.
- `hsjepa_core/run_core_module_benchmark.py`: 여러 generic human-state scenario에서 full core와 module-removal policy를 비교하는 dataset-free benchmark.
- `hsjepa_core/run_lifelog_core_state_evidence.py`: public LB 없이 OG lifelog-derived feature table만으로 core-state representation의 label manifold, masked-view prediction, nearest-neighbor consistency, external action replay를 검증하는 real-data evidence run.
- `hsjepa_core/run_masked_context_world_model.py`: semantic lifelog view를 하나씩 mask하고 나머지 view로 target-view PCA representation을 예측해, explicit HS-JEPA world-model state와 residual energy를 만든다.
- `hsjepa_core/run_action_support_world_model_core.py`: train label만으로 raw lifelog-memory action의 success/toxicity target을 만들고, HS-JEPA masked world-state가 subject-heldout으로 action-support를 예측하는지 검증한다.
- `hsjepa_core/run_action_support_view_invariance_core.py`: action-support 신호가 target/action shortcut인지, single-view artifact인지, masked world-state residual/energy 신호인지 stress한다.
- `hsjepa_core/run_listener_conditioned_action_support_core.py`: target-blind world state가 부족한지 확인하기 위해 target/family listener-conditioned residual/energy support predictor를 검증한다.

## 팀 공유 시 주의점

`Cross-Subject Episode Prototype Transport`, `Target-Route Guarded Action-Episode Transport`,
`Target-Route Conservation Decoder`, `Subject-Invariant Episode Controller` 같은 문서는
HS-JEPA core 자체가 아니다.

- cross-subject/action-episode transport: core representation의 adapter/probe
- target-route guard: competition-specific action decoder
- target-route conservation decoder: listener-conditioned core signal을 Q/S target route별
  release/inverse/hold action으로 번역하는 competition adapter
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

## Core가 아닌 것

- `S2`라는 target 이름
- public LB sensor
- Q/S route의 구체적 형태
- 특정 submission 파일명
- 250 rows x 7 targets sparse geometry

이 요소들은 `sleep_competition_adapter/`가 책임진다.
