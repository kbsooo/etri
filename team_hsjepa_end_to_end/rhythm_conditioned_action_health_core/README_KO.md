# Rhythm-Conditioned Action-Health Core

## 목적

이 패키지는 HS-JEPA core의 중요한 경계를 검증한다.

직전 실험에서 HS-JEPA는 다음 두 인터페이스를 분리해야 한다는 결론을 얻었다.

```text
rhythm-conditioned temporal decoder
rhythm-gated listener residual interface
```

이번 질문은 더 직접적이다.

```text
이 둘을 합치면 곧바로 안전한 row-target action decoder가 되는가?
```

## 구조

```text
OG train lifelog table
  -> transported human-state grammar
  -> listener residual interface
  -> rhythm-conditioned temporal decoder
  -> train-only action-health / toxic-tail target
  -> tail-safe row-target release policy
```

representation 생성 단계에서는 public LB ledger, prior submission probability,
proprietary embedding API를 쓰지 않는다.

action-health target은 OG train label에서만 만든다. 즉 raw lifelog-memory action이
fold prior보다 logloss를 줄였는지를 train fold 안에서 계산한다.

## 실행

프로젝트 루트에서 실행한다.

```bash
python3 team_hsjepa_end_to_end/rhythm_conditioned_action_health_core/run_end_to_end.py
```

## 출력

```text
hsjepa_core/outputs/rhythm_conditioned_action_health_core/
paper_hsjepa_core/RHYTHM_CONDITIONED_ACTION_HEALTH_CORE_KO.md
```

주요 파일:

- `rhythm_conditioned_action_health_summary.json`
- `RHYTHM_CONDITIONED_ACTION_HEALTH_CORE_KO.md`
- `rhythm_conditioned_action_health_split_results.csv`
- `rhythm_conditioned_action_health_chosen_policies.csv`
- `rhythm_conditioned_action_health_action_audit.csv`

## 현재 결과

판정:

```text
rhythm_conditioned_action_health_no_safe_assignment_boundary
```

핵심 수치:

```text
accepted target count total: 0
subject health-AUC delta vs listener baseline: -0.006253
chronological health-AUC delta vs listener baseline: -0.001439
subject toxic-tail-AUC delta vs listener baseline: +0.001081
chronological toxic-tail-AUC delta vs listener baseline: -0.001028
```

모든 split/feature set에서 tail-safe policy가 release를 허용한 target은 없었다.

## 해석

이 결과는 HS-JEPA core가 실패했다는 뜻이 아니다.
정확한 의미는 다음이다.

```text
HS-JEPA core representation은 hidden human-state readability를 만든다.
하지만 그 representation을 row-target action으로 안전하게 release하려면
별도의 action-tail teacher, tail-safe utility objective, 또는 competition adapter가 필요하다.
```

죽은 믿음:

```text
rhythm-conditioned residual interface alone is already an action-grade decoder.
```

살아남은 방향:

```text
action-health는 representation readout 문제가 아니라 별도 hidden target이다.
다음 HS-JEPA는 visible context에서 action-tail representation 자체를 예측해야 한다.
```

논문 문장:

```text
HS-JEPA separates human-state readability from action release.
The core can expose rhythm-conditioned and listener-conditioned hidden states,
but release-grade row-target decisions require an explicit action-health objective.
```
