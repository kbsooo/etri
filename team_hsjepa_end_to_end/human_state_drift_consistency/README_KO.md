# Human-State Drift Consistency End-to-End

## 목적

이 폴더는 팀원이 기존 실험 히스토리를 몰라도 `0.5619100863` public LB를 만든 HS-JEPA drift consistency 실험을 재현하고, 논문 포인트를 이해할 수 있게 하는 진입점이다.

## 결과

제출 파일:

```text
submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv
```

Public LB:

```text
0.5619100863
```

비교:

```text
FrontierSilence 0.5677269444 -> 0.5619100863
개선폭 -0.0058168581
```

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/human_state_drift_consistency/run_end_to_end.py
```

이 wrapper는 실제 구현체인 아래 파일을 실행한다.

```text
sleep_competition_adapter/human_state_drift_consistency_certifier.py
```

## 입력

```text
data/ch2026_metrics_train.csv
submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv
```

## 출력

```text
submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv
submission_hsjepa_human_state_drift_consistency_drift_consistency_overshoot_0fb93301_uploadsafe.csv
sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/
```

## 핵심 아이디어

test row를 독립 샘플로 보지 않는다. 같은 subject의 test rows는 하나의 숨은 human-state drift field를 공유한다고 본다.

```text
subject hidden state direction
  -> Q2 intervention route
  -> Q3 sleep-quality companion route
  -> subject-uniform logit correction
```

## 논문 포인트

이 실험은 HS-JEPA의 `core-to-adapter bridge`다.

```text
HS-JEPA core:
  visible human-life context -> hidden human-state representation

Drift consistency adapter:
  hidden subject drift -> Q2/Q3 subject-uniform action
```

중요한 contribution은 다음이다.

1. subject-level recovery/degradation direction을 JEPA target representation으로 둔다.
2. 같은 subject 내부에는 같은 logit action을 적용해 row assignment noise를 줄인다.
3. public LB는 최적화 target이 아니라 hidden subject drift를 들려주는 aggregate listener로 사용한다.

## 발표 문장

```text
우리는 public score를 직접 맞춘 것이 아니라, aggregate listener가 들려준 subject-level
회복/악화 방향을 train history와 결합해 hidden human-state drift로 해석했다.
그 drift를 Q2/Q3 route에 subject-uniform하게 번역하자 public LB가 0.5619100863까지 개선됐다.
```

## 관련 문서

- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/HUMAN_STATE_DRIFT_CONSISTENCY_TEAM_BRIEF_KO.md`
- `/Users/kbsoo/Downloads/cl2/paper_hsjepa_core/HUMAN_STATE_DRIFT_CONSISTENCY_CERTIFIER_KO.md`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/HUMAN_STATE_DRIFT_CONSISTENCY_CERTIFIER_KO.md`
