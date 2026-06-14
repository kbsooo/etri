# Learned Listener Responsibility Pretext Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 번호나 제출 히스토리를 몰라도
HS-JEPA의 `learned listener responsibility pretext` 실험을 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.
목적은 다음 질문을 검증하는 것이다.

```text
target 설명을 사람이 고정하지 않아도,
visible human-life context만으로 hidden listener responsibility를 학습할 수 있는가?
```

## 구조

```text
cross-subject transported prototype grammar
  -> confidence / entropy / energy로 label-free responsibility teacher 생성
visible human-life context
  -> responsibility teacher 예측
predicted responsibility
  -> frozen subject-heldout / row-block / chronological probes
```

labels는 responsibility teacher를 만들거나 pretext를 학습하는 데 쓰지 않는다.
labels는 representation을 고정한 뒤 frozen probe 검증에만 쓴다.

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/learned_listener_responsibility_pretext_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_learned_listener_responsibility_pretext_core.py
```

필요하면 먼저 cross-subject transport 산출물을 자동으로 사용한다.

```text
hsjepa_core/outputs/cross_subject_prototype_transport_core/
```

## 출력

```text
hsjepa_core/outputs/learned_listener_responsibility_pretext_core/
paper_hsjepa_core/LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md
```

주요 파일:

- `learned_listener_responsibility_pretext_summary.json`
- `LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md`
- `learned_listener_responsibility_probe_metrics.csv`
- `learned_listener_responsibility_pretext_metrics.csv`
- `learned_listener_responsibility_subject_leakage.csv`

## 현재 결과

```text
verdict:
  learned_listener_responsibility_beats_handcoded_positive

subject-heldout:
  global transport logloss: 0.676724
  learned semantic balanced logloss: 0.677143
  direct hand-coded semantic logloss: 0.677638
  prior logloss: 0.677858
  raw lifelog PCA logloss: 0.678707

delta:
  vs hand-coded semantic: -0.000495
  vs prior: -0.000715
  vs raw lifelog PCA: -0.001565
  vs global transport: +0.000419

stress:
  row-block delta vs global: -0.000051
  chronological delta vs global: -0.001510

subject-relative responsibility:
  best pretext CE lift vs prior: +0.029806
  subject leakage: 0.480000
```

## 해석

좋은 점:

```text
listener responsibility는 label 없이 visible context에서 학습 가능하다.
learned semantic responsibility는 사람이 고정한 semantic profile보다 downstream probe가 좋다.
row-block과 chronological stress에서는 global transport보다도 살아남는다.
subject-relative context는 pretext 품질과 leakage가 더 건강하다.
```

주의점:

```text
subject-heldout에서는 아직 global transported grammar를 넘지 못한다.
absolute context encoder는 subject leakage가 높다.
따라서 이것은 release-grade classifier가 아니라 HS-JEPA core evidence + boundary다.
```

## 논문 포인트

한국어 표현:

```text
우리는 listener responsibility를 사람이 정한 target profile이 아니라,
보이는 생활 context가 보이지 않는 transported human-state grammar의 어느 부분을
읽어야 하는지 예측하는 self-supervised target으로 재정의한다.
```

영문 표현:

```text
We formulate listener responsibility as a label-free pretext target:
given visible human-life context, the model predicts which transported
human-state grammar views should be attended by each target listener.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/LEARNED_LISTENER_RESPONSIBILITY_PRETEXT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/LABEL_FREE_TRANSPORTED_LISTENER_RESPONSIBILITY_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
