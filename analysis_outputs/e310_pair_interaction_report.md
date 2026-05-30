# E310 Pair-Interaction Materializer

Public LB는 사용하지 않았다. E309에서 살아남은 human episode target-pair representation을 current E247 tensor에 coupled target deltas로 번역하고, row/subject/dateblock/wrong-pair/swap/sign controls로 막았다.

## Prefilter

- generated candidates: `455`
- old strict candidates: `77`
- null-evaluated candidates: `42`

## Source Read

| episode | pair | pair_family | generated | old_strict | best_p90 | best_mean | median_move |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cashflow_stress | Q1_S1 | QS | 70 | 29 | -0.000379563 | -0.000535850 | 0.006220203 |
| home_recovery | Q1_S3 | QS | 35 | 17 | -0.000153378 | -0.000197600 | 0.002705376 |
| cashflow_stress | S1_S2 | SS | 35 | 15 | -0.000254328 | -0.000395387 | 0.006835694 |
| cashflow_stress | S1_S3 | SS | 35 | 13 | -0.000252852 | -0.000436480 | 0.005684052 |
| cashflow_stress | S1_S4 | SS | 35 | 3 | -0.000163216 | -0.000421876 | 0.006497264 |
| bedtime_arousal | S1_S2 | SS | 35 | 0 | -0.000044225 | -0.000267665 | 0.003586617 |
| home_recovery | S3_S4 | SS | 35 | 0 | -0.000017247 | -0.000091650 | 0.002958404 |
| bedtime_arousal | Q1_S1 | QS | 35 | 0 | -0.000002748 | -0.000105519 | 0.003267323 |
| bedtime_arousal | Q1_S3 | QS | 35 | 0 | -0.000000756 | -0.000001961 | 0.003859354 |
| badnight_aftereffect | Q3_S3 | QS | 35 | 0 | -0.000000039 | -0.000000163 | 0.001005179 |
| bedtime_arousal | Q2_S3 | QS | 35 | 0 | 0.000000378 | 0.000000105 | 0.005531059 |
| bedtime_arousal | Q3_S3 | QS | 35 | 0 | 0.000003148 | -0.000054382 | 0.003665034 |

## Matched Pair-Null Governor

- public-free ready candidates: `0`

| basename | episode | pair | rule | scale | old_strict_promote | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | wrong_pair_p90_dominance | swap_targets_p90_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e310_pair_cashflow_stress_S1_S4_hybrid_context_subject5_joint_centered_s014_600d3c43.csv | cashflow_stress | S1_S4 | joint_centered | 0.140000000 | True | -0.000242142 | -0.000084181 | 0.555555556 | 0.777777778 | 0.777777778 | 0.750000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_joint_centered_s010_f7f441d4.csv | cashflow_stress | Q1_S1 | joint_centered | 0.100000000 | True | -0.000202180 | -0.000159276 | 0.611111111 | 0.833333333 | 0.777777778 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs32_s014_8756c44a.csv | cashflow_stress | Q1_S1 | topabs32 | 0.140000000 | True | -0.000192784 | -0.000147670 | 0.666666667 | 0.777777778 | 0.555555556 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs32_s020_36096364.csv | cashflow_stress | Q1_S1 | topabs32 | 0.200000000 | True | -0.000299878 | -0.000226478 | 0.722222222 | 0.944444444 | 0.777777778 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs96_s014_90707388.csv | cashflow_stress | Q1_S1 | topabs96 | 0.140000000 | True | -0.000274497 | -0.000215030 | 0.722222222 | 0.666666667 | 0.777777778 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_topabs96_s020_68cd3503.csv | cashflow_stress | S1_S2 | topabs96 | 0.200000000 | True | -0.000308224 | -0.000196726 | 0.722222222 | 0.944444444 | 0.888888889 | 0.750000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_diff_top64_s020_96b3c216.csv | cashflow_stress | Q1_S1 | diff_top64 | 0.200000000 | True | -0.000312959 | -0.000187446 | 0.722222222 | 0.833333333 | 0.888888889 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs64_s014_d90ad181.csv | cashflow_stress | Q1_S1 | topabs64 | 0.140000000 | True | -0.000240790 | -0.000183976 | 0.722222222 | 0.777777778 | 0.611111111 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_same_sign_top64_s020_241c0731.csv | cashflow_stress | Q1_S1 | same_sign_top64 | 0.200000000 | True | -0.000283841 | -0.000164654 | 0.722222222 | 0.888888889 | 0.888888889 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_joint_centered_s014_615493fd.csv | cashflow_stress | S1_S2 | joint_centered | 0.140000000 | True | -0.000231821 | -0.000152301 | 0.722222222 | 0.777777778 | 0.777777778 | 0.750000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_diff_top64_s020_16c07552.csv | cashflow_stress | S1_S2 | diff_top64 | 0.200000000 | True | -0.000233454 | -0.000150487 | 0.722222222 | 0.944444444 | 0.888888889 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs96_s020_7cf1fd92.csv | cashflow_stress | Q1_S1 | topabs96 | 0.200000000 | True | -0.000467588 | -0.000379563 | 0.777777778 | 0.888888889 | 0.833333333 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_joint_centered_s020_25ac7e27.csv | cashflow_stress | Q1_S1 | joint_centered | 0.200000000 | True | -0.000535850 | -0.000376158 | 0.777777778 | 0.833333333 | 0.888888889 | 1.000000000 | 1.000000000 | 0.250000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs64_s020_455f7191.csv | cashflow_stress | Q1_S1 | topabs64 | 0.200000000 | True | -0.000405381 | -0.000296560 | 0.777777778 | 0.944444444 | 0.666666667 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_joint_centered_s014_34e27580.csv | cashflow_stress | Q1_S1 | joint_centered | 0.140000000 | True | -0.000317828 | -0.000241581 | 0.777777778 | 0.888888889 | 0.944444444 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S3_hybrid_context_subject5_topabs96_s020_c2a53309.csv | cashflow_stress | S1_S3 | topabs96 | 0.200000000 | True | -0.000366054 | -0.000175467 | 0.777777778 | 0.833333333 | 0.777777778 | 1.000000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_hybrid_context_subject5_joint_centered_s020_e13e653e.csv | cashflow_stress | Q1_S1 | joint_centered | 0.200000000 | True | -0.000359531 | -0.000165167 | 0.777777778 | 0.444444444 | 0.666666667 | 0.750000000 | 1.000000000 | 0.000000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S4_hybrid_context_subject5_joint_centered_s020_f62db7c9.csv | cashflow_stress | S1_S4 | joint_centered | 0.200000000 | True | -0.000421876 | -0.000163216 | 0.777777778 | 0.833333333 | 0.833333333 | 0.750000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_opp_sign_top64_s020_684d3ede.csv | home_recovery | Q1_S3 | opp_sign_top64 | 0.200000000 | True | -0.000197600 | -0.000153378 | 0.777777778 | 0.500000000 | 0.388888889 | 0.750000000 | 1.000000000 | 0.000000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S3_hybrid_context_subject5_topabs64_s020_b51c0edc.csv | cashflow_stress | S1_S3 | topabs64 | 0.200000000 | True | -0.000315276 | -0.000141136 | 0.777777778 | 0.611111111 | 0.666666667 | 1.000000000 | 1.000000000 | 0.000000000 | blocked_by_pair_nulls |
| submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_diff_top64_s020_29f1dd7c.csv | home_recovery | Q1_S3 | diff_top64 | 0.200000000 | True | -0.000170424 | -0.000127754 | 0.777777778 | 0.388888889 | 0.333333333 | 0.750000000 | 1.000000000 | 0.000000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_joint_centered_s020_21fd0fb5.csv | cashflow_stress | S1_S2 | joint_centered | 0.200000000 | True | -0.000395387 | -0.000254328 | 0.833333333 | 0.833333333 | 0.777777778 | 0.750000000 | 1.000000000 | 0.500000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_S1_S3_hybrid_context_subject5_joint_centered_s020_a94abe82.csv | cashflow_stress | S1_S3 | joint_centered | 0.200000000 | True | -0.000436480 | -0.000252852 | 0.833333333 | 0.944444444 | 0.833333333 | 1.000000000 | 1.000000000 | 0.750000000 | blocked_by_pair_nulls |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_diff_top64_s007_3c930841.csv | cashflow_stress | Q1_S1 | diff_top64 | 0.070000000 | False | -0.000081490 | -0.000048569 | 0.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs64_s004_022cb388.csv | cashflow_stress | Q1_S1 | topabs64 | 0.040000000 | False | -0.000056376 | -0.000044901 | 0.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_opp_sign_top64_s014_d9e0a872.csv | cashflow_stress | S1_S2 | opp_sign_top64 | 0.140000000 | False | -0.000066459 | -0.000043088 | 0.000000000 | 0.888888889 | 0.777777778 | 1.000000000 | 1.000000000 | 0.750000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s020_e16333df.csv | bedtime_arousal | Q1_S1 | opp_sign_top64 | 0.200000000 | False | -0.000006840 | -0.000002748 | 0.000000000 | 0.888888889 | 0.888888889 | 1.000000000 | 0.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s014_415aafad.csv | bedtime_arousal | Q1_S1 | opp_sign_top64 | 0.140000000 | False | -0.000004729 | -0.000001874 | 0.000000000 | 0.888888889 | 0.944444444 | 1.000000000 | 0.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_Q1_S3_hybrid_context_subject5_same_sign_top64_s020_cece7a73.csv | bedtime_arousal | Q1_S3 | same_sign_top64 | 0.200000000 | False | -0.000001961 | -0.000000756 | 0.000000000 | 0.944444444 | 0.777777778 | 0.750000000 | 1.000000000 | 0.750000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_Q1_S3_hybrid_context_subject5_same_sign_top64_s014_64a62510.csv | bedtime_arousal | Q1_S3 | same_sign_top64 | 0.140000000 | False | -0.000001306 | -0.000000538 | 0.000000000 | 0.833333333 | 0.666666667 | 0.750000000 | 1.000000000 | 0.750000000 | too_small_to_submit |
| submission_e310_pair_badnight_aftereffect_Q3_S3_raw_human_context_subject5_opp_sign_top64_s020_b174238e.csv | badnight_aftereffect | Q3_S3 | opp_sign_top64 | 0.200000000 | False | -0.000000163 | -0.000000039 | 0.000000000 | 0.611111111 | 0.333333333 | 1.000000000 | 0.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_badnight_aftereffect_Q3_S3_raw_human_context_subject5_opp_sign_top64_s014_752762e6.csv | badnight_aftereffect | Q3_S3 | opp_sign_top64 | 0.140000000 | False | -0.000000114 | -0.000000028 | 0.000000000 | 0.444444444 | 0.222222222 | 1.000000000 | 0.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs96_s004_bc5bcc90.csv | cashflow_stress | Q1_S1 | topabs96 | 0.040000000 | False | -0.000062643 | -0.000046354 | 0.111111111 | 0.777777778 | 0.833333333 | 1.000000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_S1_S2_raw_human_context_subject5_topabs64_s020_1036355e.csv | bedtime_arousal | S1_S2 | topabs64 | 0.200000000 | False | -0.000229125 | -0.000039715 | 0.111111111 | 0.555555556 | 0.500000000 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e310_pair_home_recovery_S3_S4_hybrid_context_dateblock5_topabs64_s020_62d65151.csv | home_recovery | S3_S4 | topabs64 | 0.200000000 | False | -0.000091650 | -0.000017247 | 0.111111111 | 0.722222222 | 0.833333333 | 0.500000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e310_pair_home_recovery_S3_S4_hybrid_context_dateblock5_same_sign_top64_s020_62d65151.csv | home_recovery | S3_S4 | same_sign_top64 | 0.200000000 | False | -0.000091650 | -0.000017247 | 0.111111111 | 0.694444444 | 0.833333333 | 0.500000000 | 1.000000000 | 0.500000000 | too_small_to_submit |
| submission_e310_pair_bedtime_arousal_S1_S2_raw_human_context_subject5_joint_centered_s020_eedc566d.csv | bedtime_arousal | S1_S2 | joint_centered | 0.200000000 | False | -0.000252485 | -0.000044225 | 0.222222222 | 0.722222222 | 0.666666667 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_S1_S4_hybrid_context_subject5_topabs96_s020_ce269ae7.csv | cashflow_stress | S1_S4 | topabs96 | 0.200000000 | False | -0.000281240 | -0.000047889 | 0.277777778 | 0.722222222 | 0.777777778 | 0.500000000 | 1.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_Q1_S1_hybrid_context_subject5_joint_centered_s010_71d2b41a.csv | cashflow_stress | Q1_S1 | joint_centered | 0.100000000 | False | -0.000115323 | -0.000045872 | 0.333333333 | 0.611111111 | 0.777777778 | 0.750000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e310_pair_cashflow_stress_S1_S3_hybrid_context_subject5_topabs96_s010_39ebc7b6.csv | cashflow_stress | S1_S3 | topabs96 | 0.100000000 | False | -0.000123442 | -0.000049995 | 0.388888889 | 0.611111111 | 0.666666667 | 1.000000000 | 1.000000000 | 0.250000000 | too_small_to_submit |
| submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_diff_top64_s007_4d8fa86b.csv | home_recovery | Q1_S3 | diff_top64 | 0.070000000 | False | -0.000058882 | -0.000043956 | 0.388888889 | 0.500000000 | 0.444444444 | 0.750000000 | 1.000000000 | 0.000000000 | too_small_to_submit |
| submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_topabs32_s010_4922eea0.csv | home_recovery | Q1_S3 | topabs32 | 0.100000000 | False | -0.000058582 | -0.000043928 | 0.611111111 | 0.333333333 | 0.277777778 | 0.750000000 | 1.000000000 | 0.000000000 | too_small_to_submit |

## Decision

- No E310 pair materialization is public-free ready.
- If old strict candidates exist but wrong-pair or shuffled controls also promote, E309 remains a representation breakthrough but not yet a submission translator.

## Outputs

- `analysis_outputs/e310_pair_interaction_candidates.csv`
- `analysis_outputs/e310_pair_interaction_selected.csv`
- `analysis_outputs/e310_pair_interaction_governor.csv`
- `analysis_outputs/e310_pair_interaction_scores.csv`
- `analysis_outputs/e310_pair_interaction_null_map.csv`
- `analysis_outputs/e310_pair_interaction_report.md`
