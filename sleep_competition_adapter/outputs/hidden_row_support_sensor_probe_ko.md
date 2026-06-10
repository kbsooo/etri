# Hidden Row-Support Sensor Probe

이 프로브는 HS-JEPA의 다음 병목인 hidden row-support를 teacher-transfer 방식으로 찾는다.
한 teacher 세계에서 row-support를 학습하고, 다른 teacher 세계에서 같은 row-support가 살아남는지 본다.

## Verdict

- Status: `portable_row_support_sensor_alive_partial`
- Best portable family: `portable_row_support_composite`
- Best portable mean row AUC: `0.8193`
- Best portable mean row recall@K: `0.4132`
- Best portable mean cell recall with stage prior: `0.3289`
- Best portable mean AUC z vs permuted train: `6.4180`
- Adapter minus portable cell-recall gap: `-0.0735`

해석:

A transferable row-support sensor exists, but it is partial: the seven-target prediction landscape transfers better than calendar/cohort-only state and turns the row-support bottleneck into a concrete HS-JEPA pretraining target.

다음 행동:

Promote prediction-landscape row support into a masked HS-JEPA row-support objective, then stress against subject/date splits.

## Family Summary

| Family | Type | Mean row AUC | Mean row recall@K | Mean cell recall | Mean AUC z |
| --- | --- | ---: | ---: | ---: | ---: |
| `portable_row_support_composite` | `portable_composite_context` | `0.8193` | `0.4132` | `0.3289` | `6.4180` |
| `listener_adapter_upper_bound` | `adapter_source_upper_bound` | `0.7807` | `0.3813` | `0.2678` | `2.4795` |
| `prediction_landscape` | `portable_prediction_context` | `0.7215` | `0.3569` | `0.2348` | `3.5599` |
| `cohort_social_outlier` | `portable_human_context` | `0.6210` | `0.2640` | `0.2274` | `3.2840` |
| `calendar_sequence_phase` | `portable_human_context` | `0.6565` | `0.2543` | `0.1992` | `3.2806` |
| `latent_geometry` | `portable_human_context` | `0.6647` | `0.2371` | `0.1980` | `2.8966` |
| `subject_peer_block` | `portable_human_context` | `0.6195` | `0.2005` | `0.1419` | `2.2622` |
| `distilled_row_context_capacity` | `teacher_distilled_capacity` | `0.5064` | `0.1320` | `0.1198` | `0.1278` |

## Teacher Transfer Metrics

| Family | Train -> Test | Row AUC | Row recall@K | Cell recall | AUC z |
| --- | --- | ---: | ---: | ---: | ---: |
| `calendar_sequence_phase` | `stagebridge_jackpot -> s2hub_jackpot` | `0.6623` | `0.2647` | `0.1912` | `3.4911` |
| `calendar_sequence_phase` | `s2hub_jackpot -> stagebridge_jackpot` | `0.6507` | `0.2439` | `0.2073` | `3.0700` |
| `cohort_social_outlier` | `stagebridge_jackpot -> s2hub_jackpot` | `0.6484` | `0.2353` | `0.2353` | `3.6391` |
| `cohort_social_outlier` | `s2hub_jackpot -> stagebridge_jackpot` | `0.5937` | `0.2927` | `0.2195` | `2.9289` |
| `distilled_row_context_capacity` | `stagebridge_jackpot -> s2hub_jackpot` | `0.5165` | `0.1176` | `0.1176` | `0.5599` |
| `distilled_row_context_capacity` | `s2hub_jackpot -> stagebridge_jackpot` | `0.4963` | `0.1463` | `0.1220` | `-0.3043` |
| `latent_geometry` | `stagebridge_jackpot -> s2hub_jackpot` | `0.6722` | `0.2059` | `0.1765` | `2.9208` |
| `latent_geometry` | `s2hub_jackpot -> stagebridge_jackpot` | `0.6571` | `0.2683` | `0.2195` | `2.8723` |
| `listener_adapter_upper_bound` | `stagebridge_jackpot -> s2hub_jackpot` | `0.7702` | `0.3235` | `0.2794` | `2.4549` |
| `listener_adapter_upper_bound` | `s2hub_jackpot -> stagebridge_jackpot` | `0.7913` | `0.4390` | `0.2561` | `2.5041` |
| `portable_row_support_composite` | `stagebridge_jackpot -> s2hub_jackpot` | `0.8397` | `0.4118` | `0.3529` | `6.4710` |
| `portable_row_support_composite` | `s2hub_jackpot -> stagebridge_jackpot` | `0.7989` | `0.4146` | `0.3049` | `6.3650` |
| `prediction_landscape` | `stagebridge_jackpot -> s2hub_jackpot` | `0.7369` | `0.3235` | `0.2500` | `3.8135` |
| `prediction_landscape` | `s2hub_jackpot -> stagebridge_jackpot` | `0.7060` | `0.3902` | `0.2195` | `3.3062` |
| `subject_peer_block` | `stagebridge_jackpot -> s2hub_jackpot` | `0.6182` | `0.2059` | `0.1618` | `2.3216` |
| `subject_peer_block` | `s2hub_jackpot -> stagebridge_jackpot` | `0.6207` | `0.1951` | `0.1220` | `2.2029` |

## Boundary

- 이 프로브는 submission 후보가 아니라 row-support sensor가 이식 가능한지 보는 진단이다.
- `prediction_landscape`는 public score ledger를 쓰지 않지만 기존 base prediction/margin 구조는 사용한다.
- `listener_adapter_upper_bound`는 adapter-side source artifact를 쓰므로 HS-JEPA core portability 증거가 아니다.
- 살아남은 신호는 target route가 아니라 row-level seven-target landscape이며, 다음 HS-JEPA objective는 이 row support를 masked prediction target으로 삼아야 한다.
