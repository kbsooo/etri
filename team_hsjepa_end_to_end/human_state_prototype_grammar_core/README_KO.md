# Human-State Prototype Grammar Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 히스토리를 몰라도 HS-JEPA core의 `subject-invariant human-life episode grammar` 실험을 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.

```text
subject-relative visible lifelog views
  -> hidden episode prototype grammar
  -> masked context predicts hidden prototype responsibilities
  -> frozen subject-heldout / chronological / row-block probes
```

## 핵심 질문

JEPA식 질문을 인간 생활 로그에 맞게 바꾼다.

```text
한 사람의 절대 사용량이나 센서 크기를 외우지 않고,
그 사람 기준으로 오늘이 어떤 생활 episode 원형인지 예측할 수 있는가?
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/human_state_prototype_grammar_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_human_state_prototype_grammar_core.py
```

## 입력

```text
data/ch2026_metrics_train.csv
team_experiments/cohort_hsjepa/cohort_human_state_features.csv
```

feature table이 없으면 기존 builder가 먼저 생성한다.

## 출력

```text
hsjepa_core/outputs/human_state_prototype_grammar_core/
paper_hsjepa_core/HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md
```

주요 파일:

- `human_state_prototype_grammar_summary.json`
- `HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md`
- `prototype_grammar_pretext_metrics.csv`
- `prototype_grammar_probe_metrics.csv`
- `prototype_grammar_subject_leakage.csv`
- `prototype_grammar_interpretation.csv`

## 현재 결과

핵심 수치:

```text
verdict:
  subject_invariant_prototype_grammar_core_positive_boundary

pretext mean cross-entropy lift vs prior:
  +0.072856

best hidden view:
  app_social_context
  cross-entropy lift: +0.148333
  accuracy lift: +0.161429

subject-heldout frozen probe:
  predicted_prototype_grammar delta vs prior: -0.000490
  predicted_prototype_grammar_energy delta vs prior: -0.000484

subject leakage:
  predicted_prototype_grammar_energy subject-id accuracy: 0.231111
  raw_lifelog_pca subject-id accuracy: 0.957778
```

## 해석

이 실험은 HS-JEPA core가 단순히 subject identity를 외우는 것이 아니라, subject-relative 좌표에서 생활 episode 원형을 일부 복원한다는 증거다.

다만 효과 크기는 아직 작다.

```text
좋은 점:
  label-free pretext가 prior보다 좋다.
  subject identity leakage가 raw lifelog보다 크게 낮다.
  frozen subject-heldout probe에서 prior를 작게 이긴다.

남은 한계:
  row-block holdout에서는 raw lifelog가 더 강하다.
  neighbor consistency에서는 calendar rhythm이 여전히 best다.
  LB breakthrough는 이 core를 listener/drift decoder로 번역해야 가능하다.
```

## 논문 포인트

이 실험은 HS-JEPA를 다음처럼 설명할 수 있게 해준다.

```text
HS-JEPA first converts absolute lifelog measurements into subject-relative
human-state prototype responsibilities.  The model then predicts masked
prototype responsibilities from the remaining visible context, producing a
label-free episode grammar that is less subject-identifying than raw lifelog
features while remaining weakly predictive of downstream sleep/wellbeing labels.
```

한국어 표현:

```text
우리는 사람마다 다른 절대 센서/사용량 크기를 그대로 쓰지 않고,
각자의 평소 기준에서 오늘이 어떤 생활 episode 원형에 가까운지를 먼저 표현한다.
그 다음 보이는 생활 context로 가려진 prototype responsibility를 예측하게 하여,
label 없이도 subject-invariant human-state grammar를 학습한다.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/human_state_prototype_grammar_core/HUMAN_STATE_PROTOTYPE_GRAMMAR_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
