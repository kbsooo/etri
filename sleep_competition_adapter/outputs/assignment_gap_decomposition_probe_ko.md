# Assignment Gap Decomposition Probe

이 프로브는 HS-JEPA에서 public-sensor assignment teacher를 OG human-state teacher로 대체하지 못한 이유를 target-route 문제와 row-support 문제로 분해한다.

## Verdict

- Status: `row_support_is_primary_bottleneck`
- Mean best portable recall: `0.1063`
- Mean distilled row-gated recall: `0.1236`
- Mean target oracle recall: `0.1063`
- Mean row oracle + stage prior recall: `0.6896`
- Mean row support gap: `0.5832`

해석:

The decisive missing variable is row support, not target route.  When row support is provided by an oracle, the same fixed objective-stage prior recovers most teacher cells; current human/social/cohort context does not.

다음 행동:

Stop spending submission slots on target-route tweaks; search for a hidden row-support sensor.

## Teacher Summary

| Teacher | Best portable | Portable recall | Distilled recall | Target oracle | Row oracle | Row gap |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `s2hub_jackpot` | `fixed_objective_stage_prior` | `0.1029` | `0.1618` | `0.1029` | `0.7206` | `0.6176` |
| `stagebridge_jackpot` | `fixed_objective_stage_prior` | `0.1098` | `0.0854` | `0.1098` | `0.6585` | `0.5488` |

## Family Metrics

| Teacher | Family | Type | Precision | Recall | Row recall | AUC | Lift |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `s2hub_jackpot` | `fixed_objective_stage_prior` | `portable_adapter_prior` | `0.1029` | `0.1029` | `0.2059` | `0.8148` | `2.6492` |
| `s2hub_jackpot` | `calendar_social_context` | `portable_human_context` | `0.0000` | `0.0000` | `0.1176` | `0.4719` | `0.0000` |
| `s2hub_jackpot` | `cohort_relative_context` | `portable_human_context` | `0.0147` | `0.0147` | `0.0882` | `0.4569` | `0.3785` |
| `s2hub_jackpot` | `latent_geometry_context` | `portable_human_context` | `0.0000` | `0.0000` | `0.0588` | `0.4562` | `0.0000` |
| `s2hub_jackpot` | `peer_route_context` | `portable_human_context` | `0.0000` | `0.0000` | `0.0882` | `0.4929` | `0.0000` |
| `s2hub_jackpot` | `portable_human_composite` | `portable_human_context` | `0.0441` | `0.0441` | `0.0882` | `0.6377` | `1.1354` |
| `s2hub_jackpot` | `distilled_cell_teacher` | `teacher_distilled_capacity` | `0.1765` | `0.1765` | `0.2941` | `0.7667` | `4.5415` |
| `s2hub_jackpot` | `distilled_row_gated_teacher` | `teacher_distilled_capacity` | `0.1618` | `0.1618` | `0.2647` | `0.7159` | `4.1631` |
| `s2hub_jackpot` | `listener_source_upper_bound` | `adapter_source_upper_bound` | `0.0882` | `0.0882` | `0.2647` | `0.6222` | `2.2708` |
| `s2hub_jackpot` | `target_oracle` | `oracle_decomposition` | `0.1029` | `0.1029` | `0.2059` | `0.8148` | `2.6492` |
| `s2hub_jackpot` | `row_oracle_plus_stage_prior` | `oracle_decomposition` | `0.7206` | `0.7206` | `1.0000` | `0.9923` | `18.5446` |
| `stagebridge_jackpot` | `fixed_objective_stage_prior` | `portable_adapter_prior` | `0.1098` | `0.1098` | `0.2439` | `0.7870` | `2.3424` |
| `stagebridge_jackpot` | `calendar_social_context` | `portable_human_context` | `0.0000` | `0.0000` | `0.1707` | `0.4822` | `0.0000` |
| `stagebridge_jackpot` | `cohort_relative_context` | `portable_human_context` | `0.0366` | `0.0366` | `0.1463` | `0.4784` | `0.7808` |
| `stagebridge_jackpot` | `latent_geometry_context` | `portable_human_context` | `0.0000` | `0.0000` | `0.1707` | `0.4913` | `0.0000` |
| `stagebridge_jackpot` | `peer_route_context` | `portable_human_context` | `0.0244` | `0.0244` | `0.0976` | `0.4915` | `0.5205` |
| `stagebridge_jackpot` | `portable_human_composite` | `portable_human_context` | `0.0610` | `0.0610` | `0.1463` | `0.6408` | `1.3013` |
| `stagebridge_jackpot` | `distilled_cell_teacher` | `teacher_distilled_capacity` | `0.1220` | `0.1220` | `0.2439` | `0.7129` | `2.6026` |
| `stagebridge_jackpot` | `distilled_row_gated_teacher` | `teacher_distilled_capacity` | `0.0854` | `0.0854` | `0.1951` | `0.6611` | `1.8218` |
| `stagebridge_jackpot` | `listener_source_upper_bound` | `adapter_source_upper_bound` | `0.1829` | `0.1829` | `0.4146` | `0.6567` | `3.9039` |
| `stagebridge_jackpot` | `target_oracle` | `oracle_decomposition` | `0.1098` | `0.1098` | `0.2439` | `0.7870` | `2.3424` |
| `stagebridge_jackpot` | `row_oracle_plus_stage_prior` | `oracle_decomposition` | `0.6585` | `0.6585` | `1.0000` | `0.9856` | `14.0541` |

## Boundary

- `portable_human_context`: public score ledger나 source artifact 없이 calendar/cohort/latent/peer-route context만 사용한다.
- `teacher_distilled_capacity`: OG feature로 public-sensitive teacher를 OOF distill한 capacity diagnostic이다.
- `oracle_decomposition`: 가설 분해용이며 deployment나 submission candidate가 아니다.
- 이 결과가 말하는 것은 target route를 더 다듬는 것보다 hidden row-support sensor를 찾는 것이 0.53급 big bet에 가깝다는 점이다.
