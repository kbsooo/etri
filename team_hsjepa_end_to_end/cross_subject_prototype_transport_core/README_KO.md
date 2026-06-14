# Cross-Subject Prototype Transport Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 히스토리를 몰라도 HS-JEPA core의 `cross-subject human-state grammar transport` 실험을 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.

```text
train subjects define subject-relative episode grammar
  -> held-out subject/block is transported into that grammar
  -> visible context predicts hidden transported prototype responsibilities
  -> frozen subject-heldout / chronological / row-block probes
```

## 핵심 질문

JEPA식 질문을 인간 생활 로그에 맞게 더 엄격하게 바꾼다.

```text
다른 subject들이 만든 생활 episode grammar를
처음 보는 subject에게 운반해도 같은 hidden human-state structure가 들리는가?
```

## 왜 중요한가

이전 `Human-State Prototype Grammar Core`는 subject-relative episode grammar가 유효한지 확인했다.
하지만 full cohort 안에서 prototype을 만든다면, 이 구조가 실제 human-state grammar인지 cohort-specific shortcut인지 애매할 수 있다.

이번 실험은 그 의심을 더 세게 찌른다.

```text
prototype grammar fit:
  validation subject/block 제외

hidden target:
  held-out row의 transported prototype responsibility

pretext:
  remaining visible views -> hidden transported prototype

downstream:
  frozen low-trust probe only after representation is fixed
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/cross_subject_prototype_transport_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_cross_subject_prototype_transport_core.py
```

## 입력

```text
data/ch2026_metrics_train.csv
team_experiments/cohort_hsjepa/cohort_human_state_features.csv
```

feature table이 없으면 기존 builder가 먼저 생성한다.

## 출력

```text
hsjepa_core/outputs/cross_subject_prototype_transport_core/
paper_hsjepa_core/CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md
```

주요 파일:

- `cross_subject_prototype_transport_summary.json`
- `CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md`
- `cross_subject_transport_pretext_metrics.csv`
- `cross_subject_transport_probe_metrics.csv`
- `cross_subject_transport_subject_leakage.csv`
- `cross_subject_transport_neighbor_consistency.csv`
- `cross_subject_transport_state_subject_heldout.csv`
- `cross_subject_transport_state_chronological_holdout.csv`
- `cross_subject_transport_state_row_block_holdout.csv`

## 현재 결과

핵심 수치:

```text
verdict:
  cross_subject_prototype_transport_core_positive

subject-heldout pretext mean cross-entropy lift vs prior:
  +0.060052

subject-heldout frozen probe:
  transported_prototype_stats_probabilities delta vs prior: -0.002026
  transported_prototype_stats delta vs prior: -0.001411
  transported_prototype_stats delta vs raw lifelog PCA: -0.002261

subject leakage:
  transported_prototype_stats subject-id accuracy: 0.273333
  raw_lifelog_pca subject-id accuracy: 0.957778
```

## 해석

이 실험은 HS-JEPA core가 full cohort 안에서만 작동하는 subject-relative grammar가 아니라,
train subjects에서 정의된 grammar를 held-out subject로 운반할 수 있음을 보여준다.

```text
좋은 점:
  label-free pretext가 prior보다 좋다.
  frozen subject-heldout probe에서 prior와 raw lifelog PCA를 이긴다.
  stats-only representation은 raw lifelog보다 subject identity leakage가 훨씬 낮다.

남은 한계:
  probabilities까지 넣으면 예측력은 좋아지지만 subject leakage가 커질 수 있다.
  row-block holdout에서는 raw lifelog PCA가 아직 best다.
  LB breakthrough로 번역하려면 listener/drift/action-health decoder가 필요하다.
```

## 논문 포인트

영문 표현:

```text
We define a subject-relative episode prototype grammar using only the training
subjects or blocks, transport held-out subjects into that grammar, and train a
masked context predictor to infer hidden prototype responsibilities.  This
tests whether HS-JEPA learns a transferable human-state grammar rather than a
subject fingerprint.
```

한국어 표현:

```text
우리는 train subject/block만으로 subject-relative 생활 episode grammar를 정의하고,
처음 보는 subject/day를 그 grammar 공간으로 운반한다.
그 다음 보이는 생활 context로 가려진 transported prototype responsibility를 예측하게 하여,
HS-JEPA가 subject fingerprint가 아니라 운반 가능한 hidden human-state grammar를 학습하는지 검증한다.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/cross_subject_prototype_transport_core/CROSS_SUBJECT_PROTOTYPE_TRANSPORT_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
