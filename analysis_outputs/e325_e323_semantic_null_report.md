# E325 E323 Semantic Null Attribution

Public LB was not used.

## Question

Do the E323 residual candidates touch rows with coherent human/social diary states, or can matched row/subject/dateblock placements reproduce the same semantic alignment?

## Summary

| basename | highrep_actual_p90 | highrep_null_strict_rate | best_signed_semantic_z | best_abs_semantic_z | semantic_signed_hits_z2 | semantic_abs_hits_z2 | q_abs_share | s_abs_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | -0.000054 | 0.050388 | 2.871546 | 2.316330 | 9 | 2 | 0.258564 | 0.741436 |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | -0.000076 | 0.081395 | 2.634592 | 2.157111 | 12 | 2 | 0.256120 | 0.743880 |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | -0.000109 | 0.093023 | 3.214537 | 2.096949 | 10 | 1 | 0.261517 | 0.738483 |

## Priority Candidate Semantic Read

Priority by E324 risk remains `submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv`.

| target | feature | source | family | signed_z_worst_abs | abs_z_worst_abs | signed_worst_mode_dominance | actual_signed_weighted_mean | human_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | hstory__night_out_mobility | human_social | nightlife_mobility | 2.871546 | 2.316330 | 0.992188 | -0.384870 | Late/deepnight movement, public ambience, weak charging. |
| Q1 | e280__night_out_mobility | human_social | mobility_context | 2.740340 | 1.827446 | 0.984375 | -0.250749 | Late/deepnight movement, public ambience, weak charging. |
| S1 | e280__phone_in_bed | human_social | bedtime_phone | 2.683822 | 0.863064 | 0.992188 | -0.331102 | Screen use while phone is charging at presleep. |
| S1 | hstory__phone_in_bed | human_social | sleep_fragment | 2.540286 | 0.540638 | 0.992188 | -0.292102 | Screen use while phone is charging at presleep. |
| S1 | episode__bedtime_arousal | episode | bedtime_arousal | 2.536066 | 0.287810 | 0.992188 | -0.314694 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep |
| S1 | hstory__home_stability | human_social | routine_anchor | 2.482326 | 0.458110 | 0.984375 | -0.291846 | Low GPS range, stable WiFi, charge, and low public ambience. |
| S1 | hstory__game_dopamine_late | human_social | media_binge | 2.135829 | 0.541891 | 0.968750 | -0.251412 | Late games with screen exposure. |
| S3 | hstory__social_isolation_media | human_social | social_isolation | 2.122491 | 0.299072 | 1.000000 | 0.218207 | Low direct social signal but high passive media/home utility. |
| S1 | hstory__night_out_mobility | human_social | nightlife_mobility | 2.042137 | 0.248257 | 0.984375 | 0.219166 | Late/deepnight movement, public ambience, weak charging. |
| S1 | e280__sedentary_screen_day | human_social | media_game | 1.981530 | 0.111106 | 0.968750 | -0.176596 | Low movement but high screen/media/social day. |
| S1 | e280__night_out_mobility | human_social | mobility_context | 1.942788 | 0.364265 | 0.960938 | 0.186113 | Late/deepnight movement, public ambience, weak charging. |
| S3 | episode__commute_pressure | episode | commute_pressure | 1.942014 | 0.697455 | 0.976562 | -0.171454 | weekday commute, vehicle exposure, routine pressure, less home stability |
| S3 | hstory__weekday_routine_pressure | human_social | calendar_social | 1.884600 | 0.684248 | 0.968750 | -0.218460 | Weekday plus commute/work/study signal. |
| S3 | hstory__commute_workday | human_social | workday_commute | 1.818674 | 0.075783 | 0.960938 | -0.178273 | Morning/evening movement and WiFi variety consistent with commute. |
| S1 | hstory__sedentary_screen_day | human_social | sedentary_screen | 1.780104 | 0.054202 | 0.960938 | -0.178064 | Low movement but high screen/media/social day. |
| S3 | cash__pay20_post3_relief_home | cashflow | post_pay_relief | 1.778417 | 0.088281 | 0.968750 | 0.283393 | After anchor 20: money available but quiet home/charging routine. |
| S3 | e280__weekday_routine_pressure | human_social | routine_calendar | 1.763911 | 0.701081 | 0.960938 | -0.151674 | Weekday plus commute/work/study signal. |
| S3 | e280__commute_workday | human_social | mobility_context | 1.756795 | 0.397171 | 0.960938 | -0.127865 | Morning/evening movement and WiFi variety consistent with commute. |
| Q1 | cash__pay10_near3_money_rumination | cashflow | cashflow_transition | 1.737948 | 1.684511 | 0.984375 | 0.321378 | Near anchor 10: finance/shopping/search rumination. |
| Q1 | e280__ritual_anchor | human_social | routine_calendar | 1.725150 | 0.341350 | 0.937500 | 0.162713 | Religious/routine app use and charging before sleep. |

## Top Semantic Alignments Across Ready Files

| basename | target | feature | source | family | signed_z_worst_abs | abs_z_worst_abs | signed_worst_mode_dominance | human_story |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | Q1 | hstory__night_out_mobility | human_social | nightlife_mobility | 3.214537 | 1.870691 | 1.000000 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | Q1 | e280__night_out_mobility | human_social | mobility_context | 2.900405 | 1.440951 | 1.000000 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | Q1 | hstory__night_out_mobility | human_social | nightlife_mobility | 2.871546 | 2.316330 | 0.992188 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | Q1 | e280__night_out_mobility | human_social | mobility_context | 2.740340 | 1.827446 | 0.984375 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | episode__bedtime_arousal | episode | bedtime_arousal | 2.697607 | 0.030221 | 1.000000 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | e280__phone_in_bed | human_social | bedtime_phone | 2.683822 | 0.863064 | 0.992188 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | hstory__game_dopamine_late | human_social | media_binge | 2.656102 | 0.152238 | 1.000000 | Late games with screen exposure. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | e280__phone_in_bed | human_social | bedtime_phone | 2.634592 | 0.711363 | 1.000000 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | hstory__phone_in_bed | human_social | sleep_fragment | 2.540286 | 0.540638 | 0.992188 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | episode__bedtime_arousal | episode | bedtime_arousal | 2.536066 | 0.287810 | 0.992188 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | Q1 | hstory__night_out_mobility | human_social | nightlife_mobility | 2.498368 | 1.991793 | 0.992188 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | hstory__home_stability | human_social | routine_anchor | 2.482326 | 0.458110 | 0.984375 | Low GPS range, stable WiFi, charge, and low public ambience. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | hstory__phone_in_bed | human_social | sleep_fragment | 2.448084 | 0.399640 | 1.000000 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | episode__bedtime_arousal | episode | bedtime_arousal | 2.402416 | 0.288507 | 0.984375 | bright screen, messages, search spiral, media/game and phone-in-bed before sleep |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | Q1 | e280__night_out_mobility | human_social | mobility_context | 2.349422 | 1.585502 | 0.984375 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | e280__phone_in_bed | human_social | bedtime_phone | 2.346223 | 0.494291 | 0.992188 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | hstory__home_stability | human_social | routine_anchor | 2.293498 | 0.256831 | 1.000000 | Low GPS range, stable WiFi, charge, and low public ambience. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | hstory__game_dopamine_late | human_social | media_binge | 2.273851 | 0.603184 | 0.992188 | Late games with screen exposure. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | hstory__home_stability | human_social | routine_anchor | 2.223332 | 0.613536 | 0.976562 | Low GPS range, stable WiFi, charge, and low public ambience. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | hstory__phone_in_bed | human_social | sleep_fragment | 2.218637 | 0.238440 | 0.992188 | Screen use while phone is charging at presleep. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | e280__sedentary_screen_day | human_social | media_game | 2.217740 | 0.248501 | 0.984375 | Low movement but high screen/media/social day. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | e280__sedentary_screen_day | human_social | media_game | 2.193599 | 0.083702 | 0.984375 | Low movement but high screen/media/social day. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S3 | hstory__social_isolation_media | human_social | social_isolation | 2.172911 | 0.400202 | 0.976562 | Low direct social signal but high passive media/home utility. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S3 | hstory__social_isolation_media | human_social | social_isolation | 2.155627 | 0.104419 | 0.968750 | Low direct social signal but high passive media/home utility. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | hstory__game_dopamine_late | human_social | media_binge | 2.135829 | 0.541891 | 0.968750 | Late games with screen exposure. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S3 | hstory__social_isolation_media | human_social | social_isolation | 2.122491 | 0.299072 | 1.000000 | Low direct social signal but high passive media/home utility. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | Q1 | cash__pay10_near3_money_rumination | cashflow | cashflow_transition | 2.102369 | 1.847527 | 0.984375 | Near anchor 10: finance/shopping/search rumination. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_5508f966.csv | S1 | hstory__night_out_mobility | human_social | nightlife_mobility | 2.042137 | 0.248257 | 0.984375 | Late/deepnight movement, public ambience, weak charging. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____meanresid_l1_50__kal_de5d9c5d.csv | S1 | hstory__sedentary_screen_day | human_social | sedentary_screen | 2.024233 | 0.224718 | 0.976562 | Low movement but high screen/media/social day. |
| submission_e323_healthresid_null_common_residual__src_human_regime_only__recipe_family_consensus____orth_nullmean__kall__51ed84b0.csv | S1 | hstory__sedentary_screen_day | human_social | sedentary_screen | 2.018944 | 0.023886 | 0.976562 | Low movement but high screen/media/social day. |

## Decision

- This is an attribution/checking experiment, not a new submission generator.
- A ready file gains semantic support only if its actual touched rows have target/story alignment that remains extreme against row, subject, and dateblock placements.
- If no semantic z-score clears the nulls, E323 should be treated as an action-geometry residual rather than a human-story breakthrough.

## Outputs

- `analysis_outputs/e325_e323_semantic_null_attribution.csv`
- `analysis_outputs/e325_e323_semantic_null_summary.csv`
- `analysis_outputs/e325_e323_semantic_feature_meta.csv`
- `analysis_outputs/e325_e323_semantic_null_report.md`
