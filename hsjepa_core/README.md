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

## 생성

```bash
python3 hsjepa_core/build_core_architecture_manifest.py
python3 hsjepa_core/run_core_reference_demo.py
```

## 산출물

- `hsjepa_core/outputs/hsjepa_core_manifest.json`
- `hsjepa_core/outputs/hsjepa_core_manifest_ko.md`
- `hsjepa_core/outputs/hsjepa_core_ablation_contract.json`
- `hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md`
- `hsjepa_core/outputs/hsjepa_core_reference_run.json`
- `hsjepa_core/outputs/hsjepa_core_reference_run_ko.md`

## 실행 가능한 core

- `hsjepa_core/core.py`: dataset adapter 없이 hidden state, listener responsibility, action-health, invariant energy를 계산하는 reference implementation.
- `hsjepa_core/run_core_reference_demo.py`: synthetic context/listener/action으로 module removal behavior를 보여주는 reference run.

## Core가 아닌 것

- `S2`라는 target 이름
- public LB sensor
- Q/S route의 구체적 형태
- 특정 submission 파일명
- 250 rows x 7 targets sparse geometry

이 요소들은 `sleep_competition_adapter/`가 책임진다.
