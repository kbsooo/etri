# Episode Transition Retrieval Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 히스토리를 몰라도, HS-JEPA core가 `다음 인간 생활 episode`를 예측하는 world model인지 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만드는 adapter가 아니다.

```text
current visible lifelog context
  -> hidden next-episode representation prediction
  -> retrieve the actual next episode among candidates
  -> frozen next-label probe
```

## 핵심 질문

I-JEPA식 질문을 lifelog에 직접 적용한다.

```text
현재의 보이는 human-life context만 보고,
보이지 않는 다음 episode representation을 맞힐 수 있는가?
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/episode_transition_retrieval_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_episode_transition_retrieval_core.py
```

## 입력

```text
data/ch2026_metrics_train.csv
team_experiments/cohort_hsjepa/cohort_human_state_features.csv
```

feature table이 없으면 기존 builder가 먼저 생성한다.

## 출력

```text
hsjepa_core/outputs/episode_transition_retrieval_core/
paper_hsjepa_core/EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md
```

주요 파일:

- `episode_transition_retrieval_summary.json`
- `EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md`
- `episode_transition_retrieval_metrics.csv`
- `episode_transition_retrieval_fold_metrics.csv`
- `episode_transition_next_label_probe_metrics.csv`

## 현재 결과

핵심 수치:

```text
subject-heldout retrieval best:
  calendar_to_next_state
  rank-pct lift vs random: +0.087878

subject-relative HS-JEPA transition predictor:
  rank-pct lift vs random: +0.044611

persistence baseline:
  rank-pct lift vs random: +0.078214

rhythm-conditioned subject-relative predictor:
  rank-pct lift vs random: +0.044534
```

해석:

```text
다음 episode transition은 복잡한 lifelog 상태 변화보다 calendar/rhythm view가 더 강하게 설명한다.
HS-JEPA transition predictor는 random보다 낫지만 persistence와 calendar를 넘지 못한다.
```

## 논문 포인트

이 실험은 HS-JEPA가 반드시 모든 hidden target에서 강해야 한다는 식의 과장을 막아준다.

정확한 주장:

```text
HS-JEPA core can predict parts of future human-state structure,
but in this dataset the dominant transition listener is calendar rhythm.
Therefore future-state prediction should be rhythm-conditioned rather than treated as a generic latent transition.
```

이 결과는 다음 core 방향을 만든다.

```text
static human-state world model
  -> rhythm-conditioned human-state transition model
  -> listener-conditioned route readout
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/episode_transition_retrieval_core/EPISODE_TRANSITION_RETRIEVAL_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
