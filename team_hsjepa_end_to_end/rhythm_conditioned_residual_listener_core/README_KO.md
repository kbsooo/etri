# Rhythm-Conditioned Residual Listener Core

## 목적

이 패키지는 HS-JEPA core의 temporal drift 문제를 검증한다.

직전 실험에서 `global transport + residual listener router`는 subject-heldout과 row-block에서는 좋아졌지만,
chronological split에서는 나빠졌다.

이번 실험의 질문은 다음이다.

```text
시간 순서 drift는 residual router를 더 키워서 풀 문제인가,
아니면 rhythm-conditioned temporal decoder로 분리해야 하는가?
```

## 구조

```text
OG train lifelog table
  -> calendar-rhythm transported state
  -> rhythm confidence / entropy / energy
  -> rhythm stability gate
  -> stable residual listener channel
  -> unstable residual listener channel
  -> frozen subject-heldout / row-block / chronological probes
```

representation 생성 단계에서는 public LB ledger, prior submission probability, proprietary embedding API, label을 쓰지 않는다.
label은 representation freeze 이후 downstream probe에서만 사용한다.

## 실행

프로젝트 루트에서 실행한다.

```bash
python3 team_hsjepa_end_to_end/rhythm_conditioned_residual_listener_core/run_end_to_end.py
```

## 출력

```text
hsjepa_core/outputs/rhythm_conditioned_residual_listener_core/
paper_hsjepa_core/RHYTHM_CONDITIONED_RESIDUAL_LISTENER_CORE_KO.md
```

주요 파일:

- `rhythm_conditioned_residual_listener_summary.json`
- `RHYTHM_CONDITIONED_RESIDUAL_LISTENER_CORE_KO.md`
- `rhythm_conditioned_residual_listener_probe_metrics.csv`
- `rhythm_conditioned_residual_listener_pretext_metrics.csv`
- `rhythm_conditioned_residual_listener_subject_leakage.csv`
- `rhythm_conditioned_residual_listener_weights.csv`

## 현재 결과

판정:

```text
rhythm_context_temporal_decoder_with_gated_residual_subject_positive
```

핵심 수치:

```text
Subject-heldout:
  global transport: 0.676724
  plain residual: 0.675817
  best rhythm/gated residual: 0.675281
  delta vs global: -0.001443
  delta vs plain residual: -0.000537

Row-block:
  global transport: 0.673331
  plain residual: 0.672903
  best rhythm context: 0.672363
  best gated residual: 0.672421

Chronological:
  global transport: 0.671537
  plain residual: 0.673502
  rhythm context: 0.669300
  rhythm context delta vs global: -0.002237
  rhythm context delta vs plain residual: -0.004202
  best gated residual: 0.671564
```

Subject leakage:

```text
rhythm context: 0.113333
best rhythm/gated residual: 0.420000
plain residual: 0.440000
global transport: 0.542222
raw lifelog PCA: 0.940000
```

## 해석

가장 중요한 발견은 `gated residual이 chronological을 완전히 해결했다`가 아니다.

정확한 해석은 다음이다.

```text
1. temporal drift는 rhythm context가 가장 잘 읽는다.
2. subject/block readability는 rhythm-gated residual이 더 좋다.
3. 따라서 HS-JEPA core는 residual listener router와 rhythm temporal decoder를 분리해야 한다.
```

논문 문장:

```text
HS-JEPA separates human-state readability into two interfaces:
a rhythm-conditioned temporal decoder for chronological drift, and a
rhythm-gated listener residual for subject/block-invariant readout.
```

## 과장하면 안 되는 점

raw lifelog PCA는 row-block과 chronological에서 더 낮은 logloss를 보인다.
하지만 raw lifelog PCA는 subject leakage가 `0.940000`으로 매우 높다.

따라서 논문에서는 raw feature가 특정 split에서 강하다는 사실을 숨기면 안 된다.
대신 다음처럼 정리한다.

```text
Raw lifelog can be a strong local predictor, but it is subject-identifying.
HS-JEPA rhythm context gives a low-leakage temporal decoder.
```
