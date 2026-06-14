# Invariant Listener Responsibility Pretext Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험명을 몰라도
HS-JEPA의 `invariant listener responsibility pretext` 실험을 재현할 수 있게 하는 진입점이다.

직전 learned responsibility 실험은 다음을 보였다.

```text
listener responsibility는 label 없이 학습 가능하다.
하지만 absolute context encoder는 subject shortcut을 강하게 담는다.
```

이번 실험은 그 shortcut을 줄이기 위해 hidden teacher 자체를 바꾼다.

## 구조

```text
current transported responsibility
  + same-subject future episode consistency
  + cross-subject cohort consistency
  -> invariant listener responsibility teacher

subject-relative visible human-life context
  -> invariant teacher prediction
  -> frozen subject-heldout / row-block / chronological probes
```

labels는 teacher를 만들거나 pretext를 학습하는 데 쓰지 않는다.
labels는 representation이 고정된 뒤 frozen probe 검증에만 쓴다.

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/invariant_listener_responsibility_pretext_core/run_end_to_end.py
```

실제 구현체:

```text
hsjepa_core/run_invariant_listener_responsibility_pretext_core.py
```

## 출력

```text
hsjepa_core/outputs/invariant_listener_responsibility_pretext_core/
paper_hsjepa_core/INVARIANT_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md
```

주요 파일:

- `invariant_listener_responsibility_pretext_summary.json`
- `INVARIANT_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md`
- `invariant_listener_responsibility_probe_metrics.csv`
- `invariant_listener_responsibility_pretext_metrics.csv`
- `invariant_listener_responsibility_subject_leakage.csv`

## 현재 결과

```text
verdict:
  invariant_listener_responsibility_beats_current_positive

subject-heldout:
  global transport logloss: 0.676724
  direct semantic logloss: 0.677638
  future-only invariant logloss: 0.677643
  current-relative logloss: 0.677901
  prior logloss: 0.677858

delta:
  vs current-relative: -0.000258
  vs direct semantic: +0.000005
  vs prior: -0.000214
  vs raw lifelog PCA: -0.001064
  vs global transport: +0.000919

stress:
  row-block delta vs global: -0.000612
  chronological delta vs global: -0.001460

leakage:
  future-only invariant: 0.480000
  global transport: 0.542222
  raw lifelog PCA: 0.957778
```

## 해석

좋은 점:

```text
future-consistent responsibility는 current-relative responsibility보다 downstream이 좋다.
subject leakage는 global transport보다 낮다.
row-block과 chronological stress에서는 global transport보다 살아남는다.
```

주의점:

```text
subject-heldout에서는 global transport를 넘지 못한다.
direct semantic과 거의 동률이다.
cohort-only teacher는 pretext/top1은 강하지만 downstream probe는 약하다.
```

## 논문 포인트

한국어 표현:

```text
우리는 listener responsibility를 현재 row의 reliability로만 정의하지 않고,
같은 사람의 다음 episode와 다른 사람의 유사 episode에서 반복되는 책임 패턴으로 다시 정의한다.
이때 future consistency는 downstream probe에 도움이 되지만,
cohort smoothing은 pretext accuracy와 downstream utility가 분리될 수 있음을 보여준다.
```

영문 표현:

```text
We define listener responsibility as an invariant pretext target by combining
current transported reliability with future-episode and cross-subject cohort
consistency.  Future consistency improves frozen downstream probes, while
cohort smoothing exposes a pretext/downstream mismatch.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/INVARIANT_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
