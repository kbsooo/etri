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

## 실행 가능한 core

- `hsjepa_core/core.py`: dataset adapter 없이 hidden state, listener responsibility, action-health, invariant energy를 계산하는 reference implementation.
- `hsjepa_core/run_core_reference_demo.py`: synthetic context/listener/action으로 module removal behavior를 보여주는 reference run.
- `hsjepa_core/run_core_module_benchmark.py`: 여러 generic human-state scenario에서 full core와 module-removal policy를 비교하는 dataset-free benchmark.
- `hsjepa_core/run_lifelog_core_state_evidence.py`: public LB 없이 OG lifelog-derived feature table만으로 core-state representation의 label manifold, masked-view prediction, nearest-neighbor consistency, external action replay를 검증하는 real-data evidence run.

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

## Core가 아닌 것

- `S2`라는 target 이름
- public LB sensor
- Q/S route의 구체적 형태
- 특정 submission 파일명
- 250 rows x 7 targets sparse geometry

이 요소들은 `sleep_competition_adapter/`가 책임진다.
