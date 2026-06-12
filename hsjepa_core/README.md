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

- `paper_hsjepa_core/HS_JEPA_JEPA_CONTRACT_KO.md`

## 생성

```bash
python3 hsjepa_core/build_core_architecture_manifest.py
python3 hsjepa_core/run_core_reference_demo.py
python3 hsjepa_core/run_core_module_benchmark.py
python3 hsjepa_core/run_lifelog_core_state_evidence.py
python3 hsjepa_core/run_masked_context_world_model.py
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

## 실행 가능한 core

- `hsjepa_core/core.py`: dataset adapter 없이 hidden state, listener responsibility, action-health, invariant energy를 계산하는 reference implementation.
- `hsjepa_core/run_core_reference_demo.py`: synthetic context/listener/action으로 module removal behavior를 보여주는 reference run.
- `hsjepa_core/run_core_module_benchmark.py`: 여러 generic human-state scenario에서 full core와 module-removal policy를 비교하는 dataset-free benchmark.
- `hsjepa_core/run_lifelog_core_state_evidence.py`: public LB 없이 OG lifelog-derived feature table만으로 core-state representation의 label manifold, masked-view prediction, nearest-neighbor consistency, external action replay를 검증하는 real-data evidence run.
- `hsjepa_core/run_masked_context_world_model.py`: semantic lifelog view를 하나씩 mask하고 나머지 view로 target-view PCA representation을 예측해, explicit HS-JEPA world-model state와 residual energy를 만든다.

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

## Core가 아닌 것

- `S2`라는 target 이름
- public LB sensor
- Q/S route의 구체적 형태
- 특정 submission 파일명
- 250 rows x 7 targets sparse geometry

이 요소들은 `sleep_competition_adapter/`가 책임진다.
