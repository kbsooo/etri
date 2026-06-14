# Transported Prototype Listener Readout Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 히스토리를 몰라도 HS-JEPA core의 `transported prototype listener interface` 실험을 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.

```text
cross-subject transported prototype grammar
  -> Q/S target listener chooses a transported grammar view
  -> frozen subject-heldout / chronological / row-block probes
```

## 핵심 질문

JEPA식 질문을 hidden grammar에서 한 단계 더 interface 쪽으로 확장한다.

```text
transported human-state grammar는 하나의 global latent로 읽어야 하는가,
아니면 target/listener별로 다른 grammar view를 읽어야 하는가?
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/transported_prototype_listener_readout_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_transported_prototype_listener_readout_core.py
```

필요하면 먼저 cross-subject transport 산출물을 자동으로 생성한다.

```text
hsjepa_core/run_cross_subject_prototype_transport_core.py
```

## 입력

```text
data/ch2026_metrics_train.csv
team_experiments/cohort_hsjepa/cohort_human_state_features.csv
hsjepa_core/outputs/cross_subject_prototype_transport_core/*
```

## 출력

```text
hsjepa_core/outputs/transported_prototype_listener_readout_core/
paper_hsjepa_core/TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md
```

주요 파일:

- `transported_prototype_listener_readout_summary.json`
- `TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md`
- `transported_prototype_listener_readout_probe_metrics.csv`
- `transported_prototype_listener_selection.csv`
- `transported_prototype_listener_selection_stability.csv`
- `transported_prototype_listener_subject_leakage.csv`

## 현재 결과

핵심 수치:

```text
verdict:
  transported_listener_readout_global_positive

subject-heldout:
  listener-conditioned logloss: 0.675348
  global transport logloss: 0.676724
  prior logloss: 0.677858
  delta vs global: -0.001376
  delta vs prior: -0.002509
  delta vs raw lifelog PCA: -0.003359

stress:
  row-block delta vs global: +0.000010
  chronological delta vs global: -0.000919
  selected route fold wins: 23 / 35
```

## Target별 선택 view

```text
Q1 -> mobility_environment stats
Q2 -> calendar_rhythm stats
Q3 -> app_social_context probabilities
S1 -> body_activity_sleep stats+probabilities
S2 -> calendar_rhythm stats+probabilities, but global transport is better
S3 -> calendar_rhythm stats+probabilities
S4 -> calendar_rhythm stats+probabilities, but global transport is slightly better
```

## 해석

이 실험은 HS-JEPA core가 단순히 하나의 latent vector를 내는 구조가 아니라,
target/listener가 읽을 수 있는 여러 transported grammar view를 노출해야 한다는 주장을 강화한다.

다만 label-free core pretext 자체는 아니다.
route 선택은 frozen probe에서 train labels를 사용한다.
따라서 논문에서는 다음처럼 분리해서 말해야 한다.

```text
Core evidence:
  cross-subject prototype grammar is transportable.

Core-interface diagnostic:
  the transported grammar is more useful when read through target-specific listeners.
```

## 논문 포인트

영문 표현:

```text
After transporting a subject-relative prototype grammar to held-out subjects,
we expose the grammar as multiple listener-readable views rather than a single
collapsed latent.  Frozen probes show that target-specific listener readout
improves over a global transported grammar, suggesting that HS-JEPA should
preserve interpretable human-state routes for downstream listeners.
```

한국어 표현:

```text
운반된 human-state grammar를 하나의 global latent로 압축하지 않고,
Q/S target listener가 서로 다른 grammar view를 선택적으로 읽도록 둔다.
frozen probe 결과는 이 listener-conditioned interface가 global transport보다 강하다는 것을 보이며,
HS-JEPA가 downstream listener를 위해 route/view 축을 보존해야 함을 시사한다.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/TRANSPORTED_PROTOTYPE_LISTENER_READOUT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
