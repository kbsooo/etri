# OG-only Human-State Assignment Teacher Probe

이 프로브는 HS-JEPA Core가 public LB sensor 없이 row-target action assignment를 얼마나 설명할 수 있는지 확인한다.

## Verdict

- Status: `og_only_assignment_replacement_not_ready`
- Pure OG row-cap2 mean recall: `0.0404`
- Pure OG row-cap2 mean precision lift: `0.9581`
- Distilled row-cap2 mean recall: `0.1236`
- Distilled row-cap2 mean precision: `0.1236`
- Listener/source upper-bound row-cap2 mean recall: `0.1356`

해석:

Human-state explains action orientation, but the safe row-target assignment still needs adapter-side evidence.

## Row-Capped Metrics

| Teacher | Family | Cap | Precision | Recall | Row recall | Sign match | Lift |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `s2hub_jackpot` | `og_unsupervised` | `row_cap_2` | `0.0441` | `0.0441` | `0.1176` | `0.0000` | `1.1354` |
| `s2hub_jackpot` | `og_row_context_teacher` | `row_cap_2` | `0.0882` | `0.0882` | `0.2059` | `0.8333` | `2.2708` |
| `s2hub_jackpot` | `og_teacher_distilled` | `row_cap_2` | `0.1765` | `0.1765` | `0.2941` | `0.6667` | `4.5415` |
| `s2hub_jackpot` | `og_teacher_distilled_row_gated` | `row_cap_2` | `0.1618` | `0.1618` | `0.2647` | `0.6364` | `4.1631` |
| `s2hub_jackpot` | `listener_source_upper_bound` | `row_cap_2` | `0.0882` | `0.0882` | `0.2647` | `1.0000` | `2.2708` |
| `stagebridge_jackpot` | `og_unsupervised` | `row_cap_2` | `0.0366` | `0.0366` | `0.1707` | `0.3333` | `0.7808` |
| `stagebridge_jackpot` | `og_row_context_teacher` | `row_cap_2` | `0.1098` | `0.1098` | `0.2195` | `0.7778` | `2.3424` |
| `stagebridge_jackpot` | `og_teacher_distilled` | `row_cap_2` | `0.1220` | `0.1220` | `0.2439` | `0.8000` | `2.6026` |
| `stagebridge_jackpot` | `og_teacher_distilled_row_gated` | `row_cap_2` | `0.0854` | `0.0854` | `0.1951` | `0.8571` | `1.8218` |
| `stagebridge_jackpot` | `listener_source_upper_bound` | `row_cap_2` | `0.1829` | `0.1829` | `0.4146` | `0.8667` | `3.9039` |

## Boundary

- `og_unsupervised`: teacher label도 source artifact도 쓰지 않는 가장 강한 portability test.
- `og_teacher_distilled*`: OG feature로 public-sensitive teacher를 subject-held-out으로 distill한 capacity diagnostic.
- `listener_source_upper_bound`: source/listener artifact를 쓰는 adapter-side upper bound이며 pure HS-JEPA core 증거가 아니다.
