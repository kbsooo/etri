# Action-Tail Representation World Model Core

## 무엇을 검증하나

이 팀용 wrapper는 HS-JEPA의 action translation 병목을 직접 검증한다.

```text
visible human-life context
  -> hidden row-level action-tail representation
  -> row-target action-health decoder
```

즉 label probability를 바로 맞히지 않고, OG train label에서 만든 `row-level action-tail field`를
숨은 target representation으로 둔다. 그 다음 visible human-life context가 이 hidden field를
예측할 수 있는지, 그리고 예측된 representation이 action-health stress readout에 도움이 되는지 본다.

## 실행

루트 디렉토리에서:

```bash
python3 team_hsjepa_end_to_end/action_tail_representation_world_model_core/run_end_to_end.py
```

## 사용하지 않는 정보

- public LB ledger를 쓰지 않는다.
- prior submission probability를 쓰지 않는다.
- proprietary embedding API를 쓰지 않는다.

## 중요한 경계

이 실험은 label-derived action-tail teacher를 쓴다.
따라서 pure label-free HS-JEPA core claim이 아니라 `core-to-decoder boundary` 실험이다.

## 현재 결론

```text
verdict: action_tail_policy_readout_positive_but_pretext_not_readable
```

정확한 해석:

- fast action policy readout에서는 일부 양성 신호가 있다.
- 하지만 JEPA pretext 자체는 mean teacher baseline보다 낮다.
- 즉 visible human-life context가 full row-level action-tail vector를 직접 복원하지는 못했다.
- 다음 설계는 action-tail teacher를 target-route/listener 조건부로 쪼개야 한다.

## 생성물

- `hsjepa_core/outputs/action_tail_representation_world_model_core/action_tail_representation_world_model_summary.json`
- `hsjepa_core/outputs/action_tail_representation_world_model_core/ACTION_TAIL_REPRESENTATION_WORLD_MODEL_CORE_KO.md`
- `hsjepa_core/outputs/action_tail_representation_world_model_core/action_tail_representation_pretext_results.csv`
- `hsjepa_core/outputs/action_tail_representation_world_model_core/action_tail_representation_action_health_results.csv`
- `paper_hsjepa_core/ACTION_TAIL_REPRESENTATION_WORLD_MODEL_CORE_KO.md`
