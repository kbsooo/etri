# E279 Public-Free Submission Governor

## Question

Can we decide whether a candidate deserves a scarce public LB slot without submitting it?

## Governor Rule

A candidate is submission-ready only if all of these hold:

- old E272 strict current-anchor gate passes;
- real row placement beats matched row/subject/dateblock shuffle nulls;
- null strict-promote rate is low (`<= 0.10`);
- if the candidate is q-sleep diary-derived, E278 train row-alignment support exists;
- if the candidate already has public LB and is worse than E247, it is blocked.

## Summary

- candidates audited, including current anchor: `66`
- matched null files generated: `1365`
- selected E272 selector models: `1`
- old strict-promote candidates: `13`
- matched-placebo gate passes: `0`
- known-public old strict false positives versus E247: `0`
- final public-free submission-ready candidates: `0`

## Candidate Decisions

| basename | final_governor_decision | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | matched_placebo_gate | train_policy_id | train_support_gate | public_delta_vs_current |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e276_no_media_game_m160_72fc6fa6.csv | blocked_by_matched_placebo | promote_candidate | -0.000229075 | -0.000129314 | 0.952380952 | 0.714285714 | 0.571428571 | False | no_media_game | True |  |
| submission_e276_only_mobility_context_m160_6ac81269.csv | blocked_by_matched_placebo | promote_candidate | -0.000130580 | -0.000095305 | 0.904761905 | 0.428571429 | 0.142857143 | False | only_mobility_context | True |  |
| submission_e276_jepa_only_m160_75d0e9cf.csv | blocked_by_matched_placebo | promote_candidate | -0.000133692 | -0.000093390 | 0.857142857 | 0.666666667 | 0.571428571 | False | jepa_only | True |  |
| submission_e276_no_social_comm_m160_cea48ae0.csv | blocked_by_matched_placebo | promote_candidate | -0.000186941 | -0.000092156 | 1.000000000 | 0.476190476 | 0.285714286 | False | no_social_comm | True |  |
| submission_e276_no_cognitive_money_m160_35f41cd8.csv | blocked_by_matched_placebo | promote_candidate | -0.000194311 | -0.000086281 | 1.000000000 | 0.285714286 | 0.000000000 | False | no_cognitive_money | True |  |
| submission_e275_q_sleep_amp_m160_86528b2f.csv | blocked_by_matched_placebo | promote_candidate | -0.000190473 | -0.000084726 | 0.952380952 | 0.571428571 | 0.428571429 | False | full_qsleep | True |  |
| submission_e276_story_full_rebuild_m160_00f95c9a.csv | blocked_by_matched_placebo | promote_candidate | -0.000188014 | -0.000082769 | 0.952380952 | 0.666666667 | 0.571428571 | False | full_qsleep | True |  |
| submission_e276_no_routine_calendar_m160_9ee2a993.csv | blocked_by_matched_placebo | promote_candidate | -0.000167479 | -0.000072275 | 0.952380952 | 0.380952381 | 0.000000000 | False | no_routine_calendar | True |  |
| submission_e275_q_sleep_amp_m145_3a3aff10.csv | blocked_by_matched_placebo | promote_candidate | -0.000164916 | -0.000070089 | 0.952380952 | 0.142857143 | 0.000000000 | False | full_qsleep | True |  |
| submission_e275_q_sleep_amp_m130_27722489.csv | blocked_by_matched_placebo | promote_candidate | -0.000141975 | -0.000064075 | 0.714285714 | 0.666666667 | 0.428571429 | False | full_qsleep | True |  |
| submission_e276_q3_only_m160_6034ca83.csv | blocked_by_matched_placebo | promote_candidate | -0.000118807 | -0.000057680 | 0.857142857 | 0.523809524 | 0.000000000 | False | q3_only | True |  |
| submission_e275_q_sleep_amp_m114_c3771d1c.csv | blocked_by_matched_placebo | promote_candidate | -0.000118990 | -0.000057493 | 0.666666667 | 0.428571429 | 0.142857143 | False | full_qsleep | True |  |
| submission_e276_no_diary_global_m160_d8951434.csv | blocked_by_matched_placebo | promote_candidate | -0.000125204 | -0.000050408 | 0.666666667 | 0.333333333 | 0.142857143 | False | no_diary_global | False |  |
| submission_e274_q_sleep_subjective_top12_8e391007.csv | too_small_to_submit | too_small_to_submit | -0.000098347 | -0.000048780 | 0.380952381 | 0.523809524 | 0.285714286 | False | full_qsleep | True |  |
| submission_e275_q_sleep_amp_m100_8e391007.csv | too_small_to_submit | too_small_to_submit | -0.000098347 | -0.000048780 | 0.666666667 | 0.238095238 | 0.000000000 | False | full_qsleep | True |  |
| submission_e276_no_bedtime_phone_m160_b81efadd.csv | too_small_to_submit | too_small_to_submit | -0.000134969 | -0.000040128 | 0.523809524 | 0.428571429 | 0.285714286 | False | no_bedtime_phone | True |  |
| submission_e275_q_sleep_amp_m080_f6617ef0.csv | too_small_to_submit | too_small_to_submit | -0.000074590 | -0.000037762 | 0.380952381 | 0.142857143 | 0.000000000 | False | full_qsleep | True |  |
| submission_e274_q3_boundary_energy_top8_e5e4b0f4.csv | too_small_to_submit | too_small_to_submit | -0.000050650 | -0.000026449 | 0.000000000 | 0.523809524 | 0.142857143 | False |  |  |  |
| submission_e275_q_sleep_amp_m060_519b3f22.csv | too_small_to_submit | too_small_to_submit | -0.000052634 | -0.000026136 | 0.047619048 | 0.238095238 | 0.142857143 | False | full_qsleep | True |  |
| submission_e269_combo_phonebed5_anti2_sharp_eea8f640.csv | too_small_to_submit | too_small_to_submit | -0.000018159 | -0.000008505 | 0.000000000 | 0.523809524 | 0.428571429 | False |  |  |  |
| submission_e269_anti_e256_tophalf_beta035_4e910856.csv | too_small_to_submit | too_small_to_submit | -0.000017223 | -0.000008141 | 0.000000000 | 0.380952381 | 0.142857143 | False |  |  |  |
| submission_e269_combo_phonebed8_anti4_small_b27a2e23.csv | too_small_to_submit | too_small_to_submit | -0.000011178 | -0.000003311 | 0.000000000 | 0.476190476 | 0.000000000 | False |  |  |  |
| submission_e269_phonebed_e247only_top8_amp015_bd6b7fee.csv | too_small_to_submit | too_small_to_submit | -0.000003810 | -0.000002460 | 0.000000000 | 1.000000000 | 1.000000000 | False |  |  |  |
| submission_e271_cashflow_top8_anti4_tiny_ccd08be8.csv | too_small_to_submit | too_small_to_submit | -0.000005422 | -0.000001953 | 0.000000000 | 0.523809524 | 0.285714286 | False |  |  |  |
| submission_e269_phonebed_e247only_top5_amp025_d487a8ab.csv | too_small_to_submit | too_small_to_submit | -0.000004244 | -0.000001908 | 0.000000000 | 0.857142857 | 0.714285714 | False |  |  |  |
| submission_e269_anti_e256_bright_lowphone_beta025_23b79263.csv | too_small_to_submit | too_small_to_submit | -0.000010157 | -0.000001601 | 0.000000000 | 0.190476190 | 0.000000000 | False |  |  |  |
| submission_e269_e247only_all_amp006_control_2cef7c9d.csv | too_small_to_submit | too_small_to_submit | -0.000002100 | -0.000001460 | 0.000000000 | 0.857142857 | 0.571428571 | False |  |  |  |
| submission_e271_calendar_only_control_top8_36405aed.csv | too_small_to_submit | too_small_to_submit | -0.000002617 | -0.000001312 | 0.000000000 | 0.952380952 | 0.857142857 | False |  |  |  |
| submission_e271_cashflow_top8_amp010_170ae6b0.csv | too_small_to_submit | too_small_to_submit | -0.000001692 | -0.000001188 | 0.000000000 | 0.714285714 | 0.571428571 | False |  |  |  |
| submission_e271_pay25_pre3_only_amp016_62659ed5.csv | too_small_to_submit | too_small_to_submit | -0.000002112 | -0.000001167 | 0.000000000 | 0.380952381 | 0.000000000 | False |  |  |  |
| submission_e271_cashflow_top6_amp014_ecc2b44c.csv | too_small_to_submit | too_small_to_submit | -0.000001468 | -0.000000763 | 0.000000000 | 0.952380952 | 0.857142857 | False |  |  |  |
| submission_e271_cashflow_top6_anti_pay15_c12a8485.csv | too_small_to_submit | too_small_to_submit | -0.000003479 | -0.000000596 | 0.000000000 | 0.380952381 | 0.142857143 | False |  |  |  |
| submission_e276_q12_only_m160_7bcd965c.csv | too_small_to_submit | too_small_to_submit | -0.000069206 | 0.000004534 | 0.000000000 | 0.476190476 | 0.142857143 | False | q12_only | False |  |
| submission_e276_only_routine_calendar_m160_06a8bbcf.csv | below_selector_resolution | below_selector_resolution | 0.000004124 | 0.000028507 | 0.000000000 | 0.761904762 | 0.428571429 | False | only_routine_calendar | False |  |
| submission_e276_only_social_comm_m160_22a09ec4.csv | below_selector_resolution | below_selector_resolution | 0.000020825 | 0.000036001 | 0.000000000 | 0.571428571 | 0.142857143 | False | only_social_comm | False |  |
| submission_e274_action_only_top12_soft_efd9e3a7.csv | below_selector_resolution | below_selector_resolution | 0.000015602 | 0.000039877 | 0.000000000 | 0.285714286 | 0.000000000 | False |  |  |  |
| submission_e274_s_objective_energy_top12_0e83fa92.csv | below_selector_resolution | below_selector_resolution | 0.000006602 | 0.000053228 | 0.000000000 | 0.285714286 | 0.000000000 | False |  |  |  |
| submission_mixmin_0c916bb4.csv | blocked_known_public_worse_than_current | below_selector_resolution | -0.000019008 | 0.000059167 | 0.285714286 | 0.238095238 | 0.000000000 | False |  |  | 0.000147691 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | blocked_known_public_worse_than_current | below_selector_resolution | 0.000051379 | 0.000065211 | 0.000000000 | 0.047619048 | 0.000000000 | False |  |  | 0.000121618 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | blocked_known_public_worse_than_current | below_selector_resolution | 0.000030913 | 0.000066989 | 0.000000000 | 0.095238095 | 0.000000000 | False |  |  | 0.000170548 |
| submission_e276_only_media_game_m160_8f065696.csv | below_selector_resolution | below_selector_resolution | 0.000042889 | 0.000076317 | 0.000000000 | 0.000000000 | 0.000000000 | False | only_media_game | False |  |
| submission_e95_hardtail_541e3973.csv | blocked_known_public_worse_than_current | below_selector_resolution | 0.000037657 | 0.000082671 | 0.047619048 | 0.190476190 | 0.000000000 | False |  |  | 0.000132380 |
| submission_e101_q2s3tail_177569bc.csv | blocked_known_public_worse_than_current | below_selector_resolution | 0.000038001 | 0.000083109 | 0.000000000 | 0.190476190 | 0.000000000 | False |  |  | 0.000141417 |
| submission_e274_energy_top18_balanced_238aa96b.csv | below_selector_resolution | below_selector_resolution | 0.000048165 | 0.000083199 | 0.000000000 | 0.333333333 | 0.000000000 | False |  |  |  |
| submission_e276_only_bedtime_phone_m160_1e694a7d.csv | below_selector_resolution | below_selector_resolution | 0.000063463 | 0.000083706 | 0.000000000 | 0.238095238 | 0.000000000 | False | only_bedtime_phone | True |  |
| submission_e176_abl_q2_to0p75_91e49725.csv | blocked_known_public_worse_than_current | below_selector_resolution | 0.000037421 | 0.000086117 | 0.190476190 | 0.190476190 | 0.000000000 | False |  |  | 0.000152882 |
| submission_e276_only_cognitive_money_m160_0de79a2d.csv | below_selector_resolution | below_selector_resolution | 0.000070131 | 0.000090007 | 0.000000000 | 0.476190476 | 0.000000000 | False | only_cognitive_money | False |  |
| submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_p05_5173ecf6.csv | block_or_reject | block_or_reject | 0.000083327 | 0.000103954 | 0.000000000 | 0.142857143 | 0.000000000 | False |  |  |  |
| submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_subject5_risk_q0p10_drop_q3_p05_5173ecf6.csv | block_or_reject | block_or_reject | 0.000083327 | 0.000103954 | 0.000000000 | 0.000000000 | 0.000000000 | False |  |  |  |
| submission_e252_e237_e250_union_q3top31_67707aef.csv | below_selector_resolution | below_selector_resolution | 0.000072018 | 0.000115988 | 0.000000000 | 0.000000000 | 0.000000000 | False |  |  |  |
| submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top13_8ae24a48.csv | block_or_reject | block_or_reject | 0.000095347 | 0.000117282 | 0.000000000 | 0.095238095 | 0.000000000 | False |  |  |  |
| submission_e276_only_diary_global_m160_6988f6a1.csv | block_or_reject | block_or_reject | 0.000094796 | 0.000118033 | 0.000000000 | 0.238095238 | 0.000000000 | False | only_diary_global | True |  |
| submission_e276_no_mobility_context_m160_68587259.csv | below_selector_resolution | below_selector_resolution | 0.000103989 | 0.000148352 | 0.000000000 | 0.285714286 | 0.000000000 | False | no_mobility_context | True |  |
| submission_e250_featnn1_decisive_all3_latent_no_targetid_featnn1_hgb_shallow_row5_risk_q0p10_drop_q3_top21_4e9a88af.csv | block_or_reject | block_or_reject | 0.000125803 | 0.000161057 | 0.000000000 | 0.000000000 | 0.000000000 | False |  |  |  |
| submission_e276_nonjepa_only_m160_a1ae06d0.csv | block_or_reject | block_or_reject | 0.000129312 | 0.000183796 | 0.000000000 | 0.095238095 | 0.000000000 | False | nonjepa_only | True |  |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | blocked_known_public_worse_than_current | block_or_reject | 0.000196332 | 0.000232923 | 0.000000000 | 0.666666667 | 0.428571429 | False |  |  | 0.000248828 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001119201 | 0.001073308 | 0.000000000 | 0.238095238 | 0.000000000 | False |  |  | 0.001127559 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001196872 | 0.001231760 | 0.000000000 | 0.619047619 | 0.142857143 | False |  |  | 0.001280372 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001204711 | 0.001266875 | 0.000000000 | 0.952380952 | 0.857142857 | False |  |  | 0.001367358 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001731893 | 0.001738496 | 0.000000000 | 0.904761905 | 0.857142857 | False |  |  | 0.001786026 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001893052 | 0.002076681 | 0.000000000 | 0.714285714 | 0.714285714 | False |  |  | 0.002144416 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | blocked_known_public_worse_than_current | block_or_reject | 0.001866594 | 0.002197983 | 0.000000000 | 0.904761905 | 0.714285714 | False |  |  | 0.002268403 |
| submission_jepa_latent_q2_w0p45.csv | blocked_known_public_worse_than_current | block_or_reject | 0.003064655 | 0.003576611 | 0.000000000 | 0.333333333 | 0.000000000 | False |  |  | 0.003642337 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | blocked_known_public_worse_than_current | block_or_reject | 0.003994768 | 0.004022196 | 0.000000000 | 1.000000000 | 1.000000000 | False |  |  | 0.004087870 |
| submission_jepa_latent_residual_probe.csv | blocked_known_public_worse_than_current | block_or_reject | 0.005542656 | 0.005014739 | 0.000000000 | 0.952380952 | 0.857142857 | False |  |  | 0.005068378 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | current_anchor | current_anchor | 0.000000000 | 0.000000000 |  |  |  |  |  |  | 0.000000000 |

## Known Public Calibration

| basename | public_lb_if_known | public_delta_vs_current | old_promotion_decision | old_strict_promote | final_governor_decision | actual_p90 | null_strict_rate | p90_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.000000000 | current_anchor | False | current_anchor | 0.000000000 |  |  |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.000121618 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000065211 | 0.000000000 | 0.047619048 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000132380 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000082671 | 0.047619048 | 0.190476190 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000141417 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000083109 | 0.000000000 | 0.190476190 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000147691 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000059167 | 0.285714286 | 0.238095238 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.000152882 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000086117 | 0.190476190 | 0.190476190 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.000170548 | below_selector_resolution | False | blocked_known_public_worse_than_current | 0.000066989 | 0.000000000 | 0.095238095 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000248828 | block_or_reject | False | blocked_known_public_worse_than_current | 0.000232923 | 0.000000000 | 0.666666667 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.001127559 | block_or_reject | False | blocked_known_public_worse_than_current | 0.001073308 | 0.000000000 | 0.238095238 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439321 | 0.001280372 | block_or_reject | False | blocked_known_public_worse_than_current | 0.001231760 | 0.000000000 | 0.619047619 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.001367358 | block_or_reject | False | blocked_known_public_worse_than_current | 0.001266875 | 0.000000000 | 0.952380952 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.001786026 | block_or_reject | False | blocked_known_public_worse_than_current | 0.001738496 | 0.000000000 | 0.904761905 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.002144416 | block_or_reject | False | blocked_known_public_worse_than_current | 0.002076681 | 0.000000000 | 0.714285714 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.002268403 | block_or_reject | False | blocked_known_public_worse_than_current | 0.002197983 | 0.000000000 | 0.904761905 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.003642337 | block_or_reject | False | blocked_known_public_worse_than_current | 0.003576611 | 0.000000000 | 0.333333333 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.004087870 | block_or_reject | False | blocked_known_public_worse_than_current | 0.004022196 | 0.000000000 | 1.000000000 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.005068378 | block_or_reject | False | blocked_known_public_worse_than_current | 0.005014739 | 0.000000000 | 0.952380952 |

## Decision

No current candidate is submission-ready. This is intentional: E272-style improvement alone is now treated as insufficient unless row placement beats matched placebo nulls.

## Interpretation

The governor separates two ideas that were previously mixed together: target/magnitude direction and row-aligned hidden-state evidence. A file can have a favorable Q-side movement direction and still be blocked if the same movement works after shuffling rows.

For the human/social q-sleep branch, E278 says train row alignment is real, but E279 still requires test-side matched-placebo resistance before any submission recommendation.

## Files

- `e279_public_free_governor_summary.csv`
- `e279_public_free_governor_scores.csv`
- `e279_public_free_governor_nulls.csv`
- `e279_public_free_governor_known_calibration.csv`
- `e279_public_free_governor_nulls/`
