# HS-JEPA Core Reference Run

이 파일은 특정 데이터셋 adapter 없이 HS-JEPA core가 실행 가능하다는 것을 보여주는 synthetic reference run이다.

## Claim

The HS-JEPA mechanism executes without a domain adapter and exposes falsifiable module-removal behavior.

## Release Summary

| Case | Released | Rejected | Released actions |
| --- | ---: | ---: | --- |
| `full_core` | `1` | `3` | `survey_small_shift` |
| `remove_listener_responsibility` | `3` | `1` | `survey_small_shift, sensor_route_shift, recovery_minor_shift` |
| `remove_action_health` | `4` | `0` | `survey_small_shift, sensor_route_shift, recovery_minor_shift, unsupported_large_shortcut` |
| `remove_invariant_energy` | `1` | `3` | `survey_small_shift` |

## Responsibilities

```json
{
  "survey_listener": 0.8132721080153977,
  "sensor_listener": 0.0949278686304252,
  "recovery_listener": 0.09180002335417713
}
```

## Interpretation

- listener responsibility는 같은 hidden state가 어느 listener로 번역될지 정한다.
- action-health는 좋아 보이는 latent move가 곧바로 output action이 되는 것을 막는다.
- invariant energy는 adapter가 제공한 human-state manifold 밖으로 나가는 action을 제한한다.
