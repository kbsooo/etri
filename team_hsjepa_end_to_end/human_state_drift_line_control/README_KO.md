# Human-State Drift Line Control End-to-End

## 목적

`certified_replay`가 public LB `0.5619100863`을 기록한 뒤, 다음으로 확인해야 할 것은 subject drift direction이 아니라 magnitude다.

이 폴더는 팀원이 다음 후보들을 재현하고, 왜 `q2_dominant_forward_axis`가 가장 정보량 높은 제출 후보인지 이해하기 위한 진입점이다.

## 실행

```bash
cd /Users/kbsoo/Downloads/cl2
python3 team_hsjepa_end_to_end/human_state_drift_line_control/run_end_to_end.py
```

## 생성 후보

| 후보 | 질문 |
| --- | --- |
| `q2_dominant_forward_axis` | Q2 route가 아직 under-powered인가? |
| `joint_forward_axis` | Q2/Q3 line 전체가 under-powered인가? |
| `q2_forward_q3_pullback_axis` | Q3는 이미 충분하고 Q2만 더 밀어야 하는가? |
| `silent_subject_reentry_axis` | listener가 침묵한 id05도 Q2 downward state로 열어야 하는가? |

추천 제출 후보:

```text
submission_hsjepa_human_state_drift_line_q2_dominant_forward_axis_03b49564_uploadsafe.csv
```

## 논문 포인트

이 실험은 HS-JEPA를 `hidden state discovery`에서 `hidden state control`로 확장한다.

```text
hidden subject drift direction
  -> target route selection
  -> route-specific action magnitude
```

`q2_dominant_forward_axis`가 좋아지면 Q2 intervention/degradation route가 아직 under-powered였다는 뜻이고, HS-JEPA에는 route-specific magnitude decoder가 필요하다는 주장이 강해진다.

나빠지면 현재 `0.75` Q2 step이 이미 포화점에 가깝다는 뜻이다. 이 경우 다음 breakthrough는 S target hidden route 또는 private-state factorization이어야 한다.
