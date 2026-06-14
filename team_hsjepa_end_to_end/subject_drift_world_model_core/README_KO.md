# Subject-Drift World Model Core End-to-End

## 목적

이 폴더는 팀원이 이전 실험 버전명을 몰라도, HS-JEPA core가 `미래 인간 상태 drift`를 표현하는지 재현할 수 있게 하는 진입점이다.

이 실험은 제출 CSV를 만들기 위한 adapter가 아니다.

```text
OG lifelog context
  -> HS-JEPA masked/future/cohort hidden state prediction
  -> frozen drift probe
  -> subject-heldout / chronological stress
```

## 핵심 질문

최근 강한 public 결과는 Q2/Q3의 subject-level drift consistency와 연결되어 있었다.
그렇다면 논문 관점의 질문은 다음이다.

```text
public LB 방정식 없이도, OG lifelog context만으로
이 사람의 다음 episode가 회복/악화 방향으로 움직일지 읽을 수 있는가?
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/subject_drift_world_model_core/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
hsjepa_core/run_subject_drift_world_model_core.py
```

## 입력

```text
data/ch2026_metrics_train.csv
team_experiments/cohort_hsjepa/cohort_human_state_features.csv
```

feature table이 없으면 기존 builder가 먼저 생성한다.

## 출력

```text
hsjepa_core/outputs/subject_drift_world_model_core/
paper_hsjepa_core/SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md
```

주요 파일:

- `subject_drift_world_model_summary.json`
- `SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md`
- `subject_drift_world_model_pretext_metrics.csv`
- `subject_drift_probe_metrics.csv`
- `subject_drift_probe_predictions.csv`
- `subject_drift_regression_metrics.csv`
- `subject_drift_probe_targets.csv`

## 현재 결과

핵심 수치:

```text
subject_relative_hsjepa_predicted_calibrated05
  vs prior_only: -0.000168 logloss

chronological_holdout best:
  subject_relative_hsjepa_predicted_calibrated10
  logloss 0.625324
```

해석:

```text
HS-JEPA world-state에는 future drift ranking 신호가 아주 약하게 있다.
하지만 효과가 0.001보다 작고 calendar low-trust readout이 전체 best라서,
이것을 큰 core breakthrough라고 부르면 안 된다.
```

## 논문 포인트

이 실험의 가치는 성공보다 경계 설정에 있다.

```text
public에서 크게 살아난 drift consistency는 인간 상태 drift라는 해석과 잘 맞지만,
OG lifelog core representation만으로는 아직 강하게 복원되지 않았다.
```

따라서 논문에서 정확한 표현은 다음이다.

```text
HS-JEPA core can weakly expose future human-state drift under low-trust readout,
but release-grade drift correction requires a listener/certifier adapter.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/subject_drift_world_model_core/SUBJECT_DRIFT_WORLD_MODEL_CORE_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/CORE_EVIDENCE_LEDGER_KO.md`
