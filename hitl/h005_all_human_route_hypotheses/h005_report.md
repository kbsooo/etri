# H005 All Human-State Route Hypotheses

## Question

Can the 1000 imported human/social hypotheses be converted into falsifiable HS-JEPA route tests, and which story families survive local direction, split, and null stress?

## Method

- Parse each row into `hidden_human_state`, row gate, and direct target route.
- Build a state score from matched human/social/cashflow features plus core HS-JEPA episode fallback.
- On train OOF predictions, apply only the stated tiny route direction.
- Compare against no move, opposite direction, subject/dateblock OOF, and shuffled controls.
- No public LB is used.

## Inventory

- hypotheses: `1000`
- direct-testable hypotheses: `950`
- states: `99`
- route families: `68`

### Priority Counts

| priority | n |
| --- | --- |
| medium | 478 |
| high | 319 |
| low | 203 |

### Verdict Counts

| verdict | n |
| --- | --- |
| survives_both_splits | 422 |
| weak_avg_only | 293 |
| direction_reversed_or_ambiguous | 101 |
| dateblock_only_fragile | 77 |
| subject_only_fragile | 57 |
| no_direct_route | 50 |

## Shortlist

| hypothesis_id | hidden_human_state | priority | route_key | gate_tags | selected_rows | amp | top_frac | subject5_delta | dateblock5_delta | avg_delta | worst_delta | opposite_avg_delta | null_dominance | direction_support_rate | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H0568 | errand_fragmentation | low | S1_down|S4_up|Q1_down | cashflow_calendar | 71 | 0.015000000 | 0.350000000 | -0.000100231 | -0.000091426 | -0.000095829 | -0.000091426 | 0.000099070 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0704 | weekend_obligation_commute | medium | S4_up|Q2_up|S1_down | subject_residual | 113 | 0.015000000 | 0.250000000 | -0.000105648 | -0.000085065 | -0.000095356 | -0.000085065 | 0.000100650 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0709 | weekend_obligation_commute | low | S4_up|Q2_up|S1_down | block_stress_required | 113 | 0.015000000 | 0.250000000 | -0.000105648 | -0.000085065 | -0.000095356 | -0.000085065 | 0.000100650 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0710 | weekend_obligation_commute | low | S4_up|Q2_up|S1_down | subject_sign_flip | 113 | 0.015000000 | 0.250000000 | -0.000105648 | -0.000085065 | -0.000095356 | -0.000085065 | 0.000100650 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0562 | errand_fragmentation | medium | S1_down|S4_up|Q1_down | weekday | 110 | 0.015000000 | 0.350000000 | -0.000088136 | -0.000081919 | -0.000085028 | -0.000081919 | 0.000090180 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0774 | errand_physical_drain | medium | Q1_down|S4_up|S1_down | subject_residual | 158 | 0.015000000 | 0.350000000 | -0.000104979 | -0.000081202 | -0.000093091 | -0.000081202 | 0.000100479 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0779 | errand_physical_drain | low | Q1_down|S4_up|S1_down | block_stress_required | 158 | 0.015000000 | 0.350000000 | -0.000104979 | -0.000081202 | -0.000093091 | -0.000081202 | 0.000100479 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0780 | errand_physical_drain | low | Q1_down|S4_up|S1_down | subject_sign_flip | 158 | 0.015000000 | 0.350000000 | -0.000104979 | -0.000081202 | -0.000093091 | -0.000081202 | 0.000100479 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0094 | forced_commute_after_badnight | high | Q3_up|S4_up|Q1_down | subject_residual | 113 | 0.015000000 | 0.250000000 | -0.000079826 | -0.000087638 | -0.000083732 | -0.000079826 | 0.000089197 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0099 | forced_commute_after_badnight | medium | Q3_up|S4_up|Q1_down | block_stress_required | 113 | 0.015000000 | 0.250000000 | -0.000079826 | -0.000087638 | -0.000083732 | -0.000079826 | 0.000089197 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0100 | forced_commute_after_badnight | medium | Q3_up|S4_up|Q1_down | subject_sign_flip | 113 | 0.015000000 | 0.250000000 | -0.000079826 | -0.000087638 | -0.000083732 | -0.000079826 | 0.000089197 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0447 | routine_anchor_recovery | high | Q2_down|S2_up|Q1_up | badnight_residue | 71 | 0.015000000 | 0.350000000 | -0.000078381 | -0.000086777 | -0.000082579 | -0.000078381 | 0.000085922 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0567 | errand_fragmentation | medium | S1_down|S4_up|Q1_down | badnight_residue | 71 | 0.015000000 | 0.350000000 | -0.000077881 | -0.000075668 | -0.000076774 | -0.000075668 | 0.000080098 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0701 | weekend_obligation_commute | medium | S4_up|Q2_up|S1_down | high_sensor | 87 | 0.015000000 | 0.350000000 | -0.000077215 | -0.000073778 | -0.000075496 | -0.000073778 | 0.000079639 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0284 | decision_fatigue_bedtime | medium | S3_down|Q1_down|Q2_up | subject_residual | 113 | 0.015000000 | 0.250000000 | -0.000090748 | -0.000070546 | -0.000080647 | -0.000070546 | 0.000085776 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0289 | decision_fatigue_bedtime | low | S3_down|Q1_down|Q2_up | block_stress_required | 113 | 0.015000000 | 0.250000000 | -0.000090748 | -0.000070546 | -0.000080647 | -0.000070546 | 0.000085776 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0290 | decision_fatigue_bedtime | low | S3_down|Q1_down|Q2_up | subject_sign_flip | 113 | 0.015000000 | 0.250000000 | -0.000090748 | -0.000070546 | -0.000080647 | -0.000070546 | 0.000085776 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0091 | forced_commute_after_badnight | high | Q3_up|S4_up|Q1_down | high_sensor | 87 | 0.015000000 | 0.350000000 | -0.000068835 | -0.000074382 | -0.000071608 | -0.000068835 | 0.000075846 | 0.888888889 | 0.666666667 | survives_both_splits |
| H0281 | decision_fatigue_bedtime | medium | S3_down|Q1_down|Q2_up | high_sensor | 62 | 0.015000000 | 0.250000000 | -0.000080424 | -0.000066904 | -0.000073664 | -0.000066904 | 0.000076475 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0561 | errand_fragmentation | medium | S1_down|S4_up|Q1_down | high_sensor | 87 | 0.015000000 | 0.350000000 | -0.000080293 | -0.000065525 | -0.000072909 | -0.000065525 | 0.000077040 | 0.888888889 | 1.000000000 | survives_both_splits |
| H0707 | weekend_obligation_commute | medium | S4_up|Q2_up|S1_down | badnight_residue | 71 | 0.015000000 | 0.350000000 | -0.000088972 | -0.000065100 | -0.000077036 | -0.000065100 | 0.000080408 | 0.777777778 | 1.000000000 | survives_both_splits |
| H0544 | routine_fragmentation | high | S1_down|Q2_up|Q1_down | subject_residual | 158 | 0.015000000 | 0.350000000 | -0.000078475 | -0.000062476 | -0.000070475 | -0.000062476 | 0.000077738 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0549 | routine_fragmentation | medium | S1_down|Q2_up|Q1_down | block_stress_required | 158 | 0.015000000 | 0.350000000 | -0.000078475 | -0.000062476 | -0.000070475 | -0.000062476 | 0.000077738 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0550 | routine_fragmentation | medium | S1_down|Q2_up|Q1_down | subject_sign_flip | 158 | 0.015000000 | 0.350000000 | -0.000078475 | -0.000062476 | -0.000070475 | -0.000062476 | 0.000077738 | 0.888888889 | 1.000000000 | survives_both_splits |
| H0646 | high_confidence_vehicle_exposure | high | S4_up|S1_down | late_arousal | 71 | 0.015000000 | 0.350000000 | -0.000065977 | -0.000062271 | -0.000064124 | -0.000062271 | 0.000065514 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0604 | sleep_debt_recovery_break | medium | S1_up|Q1_up|Q2_down | subject_residual | 113 | 0.015000000 | 0.250000000 | -0.000061626 | -0.000070245 | -0.000065935 | -0.000061626 | 0.000071179 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0609 | sleep_debt_recovery_break | low | S1_up|Q1_up|Q2_down | block_stress_required | 113 | 0.015000000 | 0.250000000 | -0.000061626 | -0.000070245 | -0.000065935 | -0.000061626 | 0.000071179 | 1.000000000 | 1.000000000 | survives_both_splits |
| H0610 | sleep_debt_recovery_break | low | S1_up|Q1_up|Q2_down | subject_sign_flip | 113 | 0.015000000 | 0.250000000 | -0.000061626 | -0.000070245 | -0.000065935 | -0.000061626 | 0.000071179 | 0.888888889 | 1.000000000 | survives_both_splits |
| H0569 | errand_fragmentation | low | S1_down|S4_up|Q1_down | block_stress_required | 158 | 0.015000000 | 0.350000000 | -0.000059992 | -0.000063426 | -0.000061709 | -0.000059992 | 0.000068990 | 1.000000000 | 0.666666667 | survives_both_splits |
| H0570 | errand_fragmentation | low | S1_down|S4_up|Q1_down | subject_sign_flip | 158 | 0.015000000 | 0.350000000 | -0.000059992 | -0.000063426 | -0.000061709 | -0.000059992 | 0.000068990 | 1.000000000 | 0.666666667 | survives_both_splits |

## Best Hidden States

| hidden_human_state | n | high | survives | weak | reversed | best_avg_delta | best_worst_delta | median_avg_delta | best_null_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weekend_obligation_commute | 10 | 0 | 10 | 0 | 0 | -0.000095356 | -0.000085065 | -0.000071710 | 1.000000000 |
| errand_physical_drain | 10 | 0 | 10 | 0 | 0 | -0.000093091 | -0.000081202 | -0.000051028 | 1.000000000 |
| routine_anchor_recovery | 10 | 5 | 10 | 0 | 0 | -0.000082579 | -0.000078381 | -0.000046881 | 1.000000000 |
| routine_fragmentation | 10 | 5 | 10 | 0 | 0 | -0.000070475 | -0.000062476 | -0.000040729 | 1.000000000 |
| physiology_recovery | 10 | 5 | 10 | 0 | 0 | -0.000061925 | -0.000054381 | -0.000056781 | 1.000000000 |
| unplanned_errand_day | 10 | 0 | 10 | 0 | 0 | -0.000066414 | -0.000052178 | -0.000052436 | 1.000000000 |
| social_commute_coupled_pressure | 10 | 5 | 10 | 0 | 0 | -0.000043243 | -0.000037945 | -0.000021731 | 1.000000000 |
| home_recovery | 10 | 5 | 10 | 0 | 0 | -0.000040076 | -0.000034995 | -0.000022931 | 1.000000000 |
| errand_fragmentation | 10 | 0 | 9 | 1 | 0 | -0.000095829 | -0.000091426 | -0.000064050 | 1.000000000 |
| high_confidence_vehicle_exposure | 10 | 5 | 9 | 1 | 0 | -0.000064124 | -0.000062271 | -0.000049250 | 1.000000000 |
| sleep_debt_recovery_break | 10 | 0 | 9 | 1 | 0 | -0.000065935 | -0.000061626 | -0.000039720 | 1.000000000 |
| commute_adaptation | 10 | 5 | 9 | 1 | 0 | -0.000059226 | -0.000057044 | -0.000038637 | 1.000000000 |
| personalized_anchor_recovery | 10 | 5 | 9 | 1 | 0 | -0.000050014 | -0.000045466 | -0.000048252 | 1.000000000 |
| phone_carried_not_body_state | 10 | 0 | 9 | 1 | 0 | -0.000042237 | -0.000041459 | -0.000023869 | 1.000000000 |
| post_social_arousal | 10 | 5 | 9 | 1 | 0 | -0.000053842 | -0.000039646 | -0.000036575 | 1.000000000 |
| weekend_social_jetlag | 10 | 5 | 9 | 1 | 0 | -0.000045855 | -0.000030538 | -0.000032937 | 1.000000000 |
| forced_commute_after_badnight | 10 | 5 | 8 | 1 | 1 | -0.000083732 | -0.000079826 | -0.000062498 | 1.000000000 |
| financial_rumination_arousal | 10 | 0 | 8 | 1 | 0 | -0.000061027 | -0.000056199 | -0.000049632 | 1.000000000 |
| distributed_social_load | 10 | 5 | 8 | 1 | 0 | -0.000062246 | -0.000048059 | -0.000038527 | 1.000000000 |
| badnight_aftereffect | 20 | 10 | 8 | 7 | 3 | -0.000045064 | -0.000044304 | -0.000013203 | 1.000000000 |
| cognitive_slump_after_badnight | 10 | 5 | 8 | 1 | 1 | -0.000050231 | -0.000042363 | -0.000042627 | 1.000000000 |
| outing_overload | 10 | 5 | 8 | 2 | 0 | -0.000046795 | -0.000040228 | -0.000032769 | 1.000000000 |
| masked_badnight_aftereffect | 10 | 5 | 8 | 0 | 1 | -0.000031816 | -0.000030621 | -0.000023563 | 1.000000000 |
| morning_activation_anchor | 10 | 5 | 7 | 1 | 2 | -0.000065738 | -0.000055777 | -0.000030948 | 1.000000000 |
| weekend_routine_preservation | 10 | 5 | 7 | 1 | 0 | -0.000039957 | -0.000033172 | -0.000027769 | 1.000000000 |
| rebound_recovery_after_badnight | 10 | 5 | 7 | 2 | 0 | -0.000034311 | -0.000030009 | -0.000025557 | 1.000000000 |
| commute_recovered_at_home | 10 | 5 | 7 | 2 | 0 | -0.000047637 | -0.000029739 | -0.000025370 | 1.000000000 |
| decision_fatigue_bedtime | 10 | 0 | 6 | 4 | 0 | -0.000080647 | -0.000070546 | -0.000043049 | 1.000000000 |
| physical_fatigue_strain | 10 | 5 | 6 | 1 | 2 | -0.000059719 | -0.000058023 | -0.000035674 | 1.000000000 |
| recovered_routine_after_fragmentation | 10 | 0 | 6 | 2 | 1 | -0.000069686 | -0.000056203 | -0.000027228 | 1.000000000 |
| sensory_decompression | 10 | 5 | 6 | 2 | 0 | -0.000026863 | -0.000026092 | -0.000023508 | 1.000000000 |
| daytime_fatigue_after_badnight | 10 | 5 | 5 | 4 | 1 | -0.000058793 | -0.000053050 | -0.000021811 | 1.000000000 |
| budget_squeeze_isolation | 10 | 0 | 5 | 4 | 1 | -0.000057676 | -0.000053047 | -0.000036978 | 1.000000000 |
| health_anxiety | 10 | 0 | 5 | 3 | 1 | -0.000042613 | -0.000039337 | -0.000016812 | 0.888888889 |
| cognitive_rumination | 10 | 5 | 5 | 4 | 1 | -0.000043855 | -0.000036024 | -0.000027078 | 1.000000000 |

## Best Route Families

| route_key | n | survives | weak | best_avg_delta | best_worst_delta | median_avg_delta |
| --- | --- | --- | --- | --- | --- | --- |
| Q2_down|S2_up|Q1_up | 60 | 29 | 15 | -0.000082579 | -0.000078381 | -0.000019682 |
| S3_down|Q1_down|Q2_up | 70 | 22 | 30 | -0.000080647 | -0.000070546 | -0.000018714 |
| S3_up|Q1_up|Q2_down | 30 | 20 | 6 | -0.000040076 | -0.000034995 | -0.000021179 |
| S4_up | 20 | 18 | 2 | -0.000059226 | -0.000057044 | -0.000025168 |
| S3_down|S4_up | 20 | 17 | 3 | -0.000053842 | -0.000040228 | -0.000032769 |
| S3_down|Q2_up|Q1_down | 20 | 13 | 5 | -0.000061027 | -0.000056199 | -0.000031019 |
| Q3_up|Q1_down|S1_down | 20 | 13 | 5 | -0.000058793 | -0.000053050 | -0.000028815 |
| S3_down|Q3_up|Q1_down | 30 | 13 | 13 | -0.000043855 | -0.000036024 | -0.000020160 |
| Q1_down|S3_down|Q2_up | 30 | 12 | 10 | -0.000057676 | -0.000053047 | -0.000019737 |
| S4_up|Q2_up|S1_down | 10 | 10 | 0 | -0.000095356 | -0.000085065 | -0.000071710 |
| Q1_down|S4_up|S1_down | 10 | 10 | 0 | -0.000093091 | -0.000081202 | -0.000051028 |
| S1_down|Q2_up|Q1_down | 10 | 10 | 0 | -0.000070475 | -0.000062476 | -0.000040729 |
| Q1_up|S3_up|Q2_down | 10 | 10 | 0 | -0.000061925 | -0.000054381 | -0.000056781 |
| S1_down|S4_up|Q2_up | 10 | 10 | 0 | -0.000066414 | -0.000052178 | -0.000052436 |
| S4_up|S3_down | 10 | 10 | 0 | -0.000043243 | -0.000037945 | -0.000021731 |
| S1_down|S4_up|Q1_down | 10 | 9 | 1 | -0.000095829 | -0.000091426 | -0.000064050 |
| S4_up|S1_down | 10 | 9 | 1 | -0.000064124 | -0.000062271 | -0.000049250 |
| S1_up|Q1_up|Q2_down | 10 | 9 | 1 | -0.000065935 | -0.000061626 | -0.000039720 |
| Q2_down|S2_up | 10 | 9 | 1 | -0.000050014 | -0.000045466 | -0.000048252 |
| Q2_down|S2_up|S1_up | 20 | 9 | 8 | -0.000039957 | -0.000037733 | -0.000019657 |
| S3_down|S1_down | 10 | 9 | 1 | -0.000045855 | -0.000030538 | -0.000032937 |
| Q3_up|S4_up|Q1_down | 10 | 8 | 1 | -0.000083732 | -0.000079826 | -0.000062498 |
| S3_down|S1_down|Q1_down | 10 | 8 | 1 | -0.000062246 | -0.000048059 | -0.000038527 |
| Q3_up | 10 | 8 | 0 | -0.000031816 | -0.000030621 | -0.000023563 |
| Q3_up|Q1_down | 10 | 7 | 2 | -0.000040993 | -0.000039734 | -0.000029209 |
| Q3_up|S3_up|Q2_down | 10 | 7 | 2 | -0.000034311 | -0.000030009 | -0.000025557 |
| S4_up|S3_up|Q1_up | 10 | 7 | 2 | -0.000047637 | -0.000029739 | -0.000025370 |
| S3_down|Q2_up | 20 | 7 | 4 | -0.000039051 | -0.000028654 | -0.000007242 |
| Q1_down|S3_up|S4_up | 10 | 6 | 1 | -0.000059719 | -0.000058023 | -0.000035674 |
| S3_down|S4_up|Q2_up | 20 | 6 | 12 | -0.000049945 | -0.000041018 | -0.000023871 |
| Q3_up|Q1_down|S3_down | 20 | 6 | 10 | -0.000035628 | -0.000029645 | -0.000021362 |
| S3_up|Q1_up|S1_up | 10 | 6 | 2 | -0.000026863 | -0.000026092 | -0.000023508 |
| Q1_down|Q2_up|Q3_up | 10 | 5 | 3 | -0.000042613 | -0.000039337 | -0.000016812 |
| S3_up|Q2_down|S1_up | 10 | 5 | 2 | -0.000032068 | -0.000031075 | -0.000018360 |
| S4_up|S1_down|S3_down | 10 | 4 | 6 | -0.000061606 | -0.000047190 | -0.000023540 |

## Gate Summary

| gate_primary | n | survives | best_avg_delta | median_avg_delta |
| --- | --- | --- | --- | --- |
| late_arousal | 100 | 56 | -0.000067924 | -0.000022924 |
| high_sensor | 100 | 48 | -0.000075496 | -0.000026646 |
| cashflow_calendar | 94 | 47 | -0.000095829 | -0.000020196 |
| badnight_residue | 100 | 43 | -0.000082579 | -0.000021640 |
| block_stress_required | 100 | 41 | -0.000095356 | -0.000023474 |
| subject_residual | 94 | 40 | -0.000095356 | -0.000023491 |
| subject_sign_flip | 94 | 39 | -0.000095356 | -0.000023491 |
| weekday | 94 | 37 | -0.000085028 | -0.000024227 |
| weekend | 100 | 34 | -0.000052482 | -0.000007903 |
| low_sensor | 100 | 31 | -0.000051835 | -0.000006308 |
| all_rows | 24 | 6 | -0.000040087 | -0.000023132 |

## Interpretation

`422` hypotheses survived both subject and dateblock stress. These are not submission-ready by themselves, but they are route-library candidates for a later sparse materializer.
`293` hypotheses were average-favorable but split-fragile; `101` looked more consistent in the opposite direction or had ambiguous directional support.

## Files

- `hitl/h005_all_human_route_hypotheses/h005_hypothesis_parsed.csv`
- `hitl/h005_all_human_route_hypotheses/h005_all_route_tests.csv`
- `hitl/h005_all_human_route_hypotheses/h005_route_null_controls.csv`
- `hitl/h005_all_human_route_hypotheses/h005_state_summary.csv`
- `hitl/h005_all_human_route_hypotheses/h005_gate_summary.csv`
- `hitl/h005_all_human_route_hypotheses/h005_route_family_summary.csv`
- `hitl/h005_all_human_route_hypotheses/h005_shortlist.csv`
