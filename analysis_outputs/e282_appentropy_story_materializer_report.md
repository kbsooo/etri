# E282 App-Entropy Story-State Materializer

## Question

Can the E281 surviving human/social story become a submission-grade edit without spending public LB?

## Human/Social Worldview

`app_entropy_scattered_day` is interpreted as a routine-break / attention-fragmentation state: many apps across the day, less single-routine anchoring, and likely noisier sleep-quality self-report. The JEPA-style part is target-free: other context families predict this hidden story-state, and only then do we test whether that state deserves tiny Q3/Q2/S2 logit edits.

## State Diagnostics

| story_id | mapped_family | score_col | context_cols | split | state_oof_r2 | state_oof_corr |
| --- | --- | --- | --- | --- | --- | --- |
| app_entropy_scattered_day | routine_calendar | app_entropy_scattered_day_subj_z | 117 | subject5 | 0.419010357 | 0.751144172 |
| app_entropy_scattered_day | routine_calendar | app_entropy_scattered_day_subj_z | 117 | dateblock5 | 0.728346614 | 0.853482540 |

## Target Direction

| target | logistic_coef_state_avg_z | label_rate_high_minus_low | e281_mean_delta | e281_best_delta | support_strength | target_weight | supported_for_materialization |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.110626752 | 0.144444444 | -0.000042243 | -0.000073322 | 0.000042243 | 0.000000000 | False |
| Q2 | 0.327734745 | 0.155555556 | -0.003948182 | -0.005987309 | 0.003948182 | 0.630808296 | True |
| Q3 | 0.327701640 | 0.188888889 | -0.009922073 | -0.017951625 | 0.009922073 | 1.000000000 | True |
| S1 | -0.085824908 | -0.088888889 | 0.002911870 | 0.002385472 | 0.000000000 | 0.000000000 | False |
| S2 | 0.313787616 | 0.033333333 | -0.001533766 | -0.003490570 | 0.001533766 | 0.393168177 | True |
| S3 | 0.141934133 | 0.000000000 | 0.004399007 | 0.002819992 | 0.000000000 | 0.000000000 | False |
| S4 | 0.142231134 | 0.044444444 | 0.000930153 | -0.000396261 | 0.000000000 | 0.000000000 | False |

## Candidate Movement

| candidate_id | basename | source_path | scope | targets | shape | amp | changed_cells | changed_rows | mean_abs_logit_delta | max_abs_logit_delta | mean_signed_state_shape | std_signed_state_shape | state_q10 | state_q90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | submission_e282_appentropy_q3_linear_a0p006_04875df1.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p006_04875df1.csv | q3 | Q3 | linear | 0.006000000 | 250 | 250 | 0.000536253 | 0.012000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 1 | submission_e282_appentropy_q3_linear_a0p010_323c9cf7.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p010_323c9cf7.csv | q3 | Q3 | linear | 0.010000000 | 250 | 250 | 0.000893754 | 0.020000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 2 | submission_e282_appentropy_q3_linear_a0p016_6930b167.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p016_6930b167.csv | q3 | Q3 | linear | 0.016000000 | 250 | 250 | 0.001430007 | 0.032000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 3 | submission_e282_appentropy_q3_linear_a0p022_6021bd56.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p022_6021bd56.csv | q3 | Q3 | linear | 0.022000000 | 250 | 250 | 0.001966259 | 0.044000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 4 | submission_e282_appentropy_q3_linear_a0p023_ce916f68.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p023_ce916f68.csv | q3 | Q3 | linear | 0.023000000 | 250 | 250 | 0.002055635 | 0.046000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 5 | submission_e282_appentropy_q3_linear_a0p024_3aa39b55.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p024_3aa39b55.csv | q3 | Q3 | linear | 0.024000000 | 250 | 250 | 0.002145010 | 0.048000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 6 | submission_e282_appentropy_q3_linear_a0p025_29551469.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p025_29551469.csv | q3 | Q3 | linear | 0.025000000 | 250 | 250 | 0.002234386 | 0.050000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 7 | submission_e282_appentropy_q3_linear_a0p026_136f92ff.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p026_136f92ff.csv | q3 | Q3 | linear | 0.026000000 | 250 | 250 | 0.002323761 | 0.052000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 8 | submission_e282_appentropy_q3_linear_a0p028_8f5c4791.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p028_8f5c4791.csv | q3 | Q3 | linear | 0.028000000 | 250 | 250 | 0.002502512 | 0.056000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 9 | submission_e282_appentropy_q3_linear_a0p030_798f561b.csv | analysis_outputs/submission_e282_appentropy_q3_linear_a0p030_798f561b.csv | q3 | Q3 | linear | 0.030000000 | 250 | 250 | 0.002681263 | 0.060000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 10 | submission_e282_appentropy_q3_tail_a0p010_d49e38be.csv | analysis_outputs/submission_e282_appentropy_q3_tail_a0p010_d49e38be.csv | q3 | Q3 | tail | 0.010000000 | 83 | 83 | 0.000170109 | 0.015602032 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 11 | submission_e282_appentropy_q3_tail_a0p014_1d3de553.csv | analysis_outputs/submission_e282_appentropy_q3_tail_a0p014_1d3de553.csv | q3 | Q3 | tail | 0.014000000 | 83 | 83 | 0.000238153 | 0.021842845 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 12 | submission_e282_appentropy_q3_tail_a0p020_265e39f8.csv | analysis_outputs/submission_e282_appentropy_q3_tail_a0p020_265e39f8.csv | q3 | Q3 | tail | 0.020000000 | 83 | 83 | 0.000340219 | 0.031204064 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 13 | submission_e282_appentropy_q3_tail_a0p030_355905f4.csv | analysis_outputs/submission_e282_appentropy_q3_tail_a0p030_355905f4.csv | q3 | Q3 | tail | 0.030000000 | 83 | 83 | 0.000510328 | 0.046806096 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 14 | submission_e282_appentropy_q2q3_linear_a0p006_21b2333e.csv | analysis_outputs/submission_e282_appentropy_q2q3_linear_a0p006_21b2333e.csv | q2q3 | Q2,Q3 | linear | 0.006000000 | 500 | 250 | 0.000874525 | 0.012000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 15 | submission_e282_appentropy_q2q3_linear_a0p010_bbda2f33.csv | analysis_outputs/submission_e282_appentropy_q2q3_linear_a0p010_bbda2f33.csv | q2q3 | Q2,Q3 | linear | 0.010000000 | 500 | 250 | 0.001457542 | 0.020000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 16 | submission_e282_appentropy_q2q3_tail_a0p010_8aca7e7b.csv | analysis_outputs/submission_e282_appentropy_q2q3_tail_a0p010_8aca7e7b.csv | q2q3 | Q2,Q3 | tail | 0.010000000 | 166 | 83 | 0.000277416 | 0.015602032 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 17 | submission_e282_appentropy_q2q3_tail_a0p014_59e040c7.csv | analysis_outputs/submission_e282_appentropy_q2q3_tail_a0p014_59e040c7.csv | q2q3 | Q2,Q3 | tail | 0.014000000 | 166 | 83 | 0.000388382 | 0.021842845 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 18 | submission_e282_appentropy_q2q3s2_linear_a0p006_c37fbb7d.csv | analysis_outputs/submission_e282_appentropy_q2q3s2_linear_a0p006_c37fbb7d.csv | q2q3s2 | Q2,Q3,S2 | linear | 0.006000000 | 750 | 250 | 0.001085363 | 0.012000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 19 | submission_e282_appentropy_q2q3s2_linear_a0p010_71a1114f.csv | analysis_outputs/submission_e282_appentropy_q2q3s2_linear_a0p010_71a1114f.csv | q2q3s2 | Q2,Q3,S2 | linear | 0.010000000 | 750 | 250 | 0.001808938 | 0.020000000 | 0.081627229 | 0.776194520 | -1.015149612 | 0.984186473 |
| 20 | submission_e282_appentropy_q2q3s2_tail_a0p010_e6e6ed48.csv | analysis_outputs/submission_e282_appentropy_q2q3s2_tail_a0p010_e6e6ed48.csv | q2q3s2 | Q2,Q3,S2 | tail | 0.010000000 | 249 | 83 | 0.000344297 | 0.015602032 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |
| 21 | submission_e282_appentropy_q2q3s2_tail_a0p014_fc713d44.csv | analysis_outputs/submission_e282_appentropy_q2q3s2_tail_a0p014_fc713d44.csv | q2q3s2 | Q2,Q3,S2 | tail | 0.014000000 | 249 | 83 | 0.000482016 | 0.021842845 | -0.003948421 | 0.268390243 | -0.223190369 | 0.199729298 |

## Public-Free Governor

- selected public-anchor selector models: `1`
- candidates audited: `22`
- submission-ready candidates: `0`

| basename | final_decision | old_promotion_decision | actual_mean | actual_p90 | actual_beats_current_rate | null_strict_rate | p90_dominance | worst_mode_p90_dominance | matched_placebo_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e282_appentropy_q3_linear_a0p030_798f561b.csv | blocked_by_matched_placebo | promote_candidate | -0.000157675 | -0.000064970 | 1.000000000 | 0.939393939 | 0.878787879 | 0.727272727 | False |
| submission_e282_appentropy_q3_linear_a0p028_8f5c4791.csv | blocked_by_matched_placebo | promote_candidate | -0.000145173 | -0.000060752 | 1.000000000 | 0.787878788 | 0.939393939 | 0.909090909 | False |
| submission_e282_appentropy_q3_linear_a0p026_136f92ff.csv | blocked_by_matched_placebo | promote_candidate | -0.000132963 | -0.000056519 | 1.000000000 | 0.848484848 | 0.848484848 | 0.727272727 | False |
| submission_e282_appentropy_q3_linear_a0p025_29551469.csv | blocked_by_matched_placebo | promote_candidate | -0.000126983 | -0.000054396 | 1.000000000 | 0.515151515 | 0.878787879 | 0.727272727 | False |
| submission_e282_appentropy_q3_linear_a0p024_3aa39b55.csv | blocked_by_matched_placebo | promote_candidate | -0.000121004 | -0.000052270 | 1.000000000 | 0.272727273 | 0.878787879 | 0.818181818 | False |
| submission_e282_appentropy_q3_linear_a0p023_ce916f68.csv | blocked_by_matched_placebo | promote_candidate | -0.000115120 | -0.000050139 | 1.000000000 | 0.121212121 | 0.878787879 | 0.727272727 | False |
| submission_e282_appentropy_q3_linear_a0p022_6021bd56.csv | too_small_to_submit | too_small_to_submit | -0.000109290 | -0.000048005 | 1.000000000 | 0.000000000 | 0.848484848 | 0.636363636 | False |
| submission_e282_appentropy_q3_linear_a0p016_6930b167.csv | too_small_to_submit | too_small_to_submit | -0.000074531 | -0.000035132 | 1.000000000 | 0.000000000 | 0.818181818 | 0.727272727 | False |
| submission_e282_appentropy_q3_linear_a0p010_323c9cf7.csv | too_small_to_submit | too_small_to_submit | -0.000042757 | -0.000022106 | 1.000000000 | 0.000000000 | 0.939393939 | 0.909090909 | False |
| submission_e282_appentropy_q3_linear_a0p006_04875df1.csv | too_small_to_submit | too_small_to_submit | -0.000024573 | -0.000013316 | 1.000000000 | 0.000000000 | 0.939393939 | 0.818181818 | False |
| submission_e282_appentropy_q3_tail_a0p010_d49e38be.csv | too_small_to_submit | too_small_to_submit | -0.000002107 | 0.000000572 | 0.764705882 | 0.000000000 | 0.848484848 | 0.636363636 | False |
| submission_e282_appentropy_q3_tail_a0p014_1d3de553.csv | too_small_to_submit | too_small_to_submit | -0.000003106 | 0.000000809 | 0.764705882 | 0.000000000 | 0.787878788 | 0.636363636 | False |
| submission_e282_appentropy_q3_tail_a0p020_265e39f8.csv | too_small_to_submit | too_small_to_submit | -0.000005196 | 0.000001172 | 0.764705882 | 0.000000000 | 0.818181818 | 0.636363636 | False |
| submission_e282_appentropy_q2q3_linear_a0p006_21b2333e.csv | too_small_to_submit | too_small_to_submit | -0.000012334 | 0.000001251 | 0.823529412 | 0.000000000 | 0.272727273 | 0.090909091 | False |
| submission_e282_appentropy_q3_tail_a0p030_355905f4.csv | too_small_to_submit | too_small_to_submit | -0.000009564 | 0.000001851 | 0.764705882 | 0.000000000 | 0.909090909 | 0.818181818 | False |
| submission_e282_appentropy_q2q3_linear_a0p010_bbda2f33.csv | too_small_to_submit | too_small_to_submit | -0.000022357 | 0.000002586 | 0.852941176 | 0.000000000 | 0.121212121 | 0.000000000 | False |
| submission_e282_appentropy_q2q3_tail_a0p010_8aca7e7b.csv | below_selector_resolution | below_selector_resolution | 0.000002601 | 0.000005950 | 0.117647059 | 0.000000000 | 0.393939394 | 0.090909091 | False |
| submission_e282_appentropy_q2q3_tail_a0p014_59e040c7.csv | below_selector_resolution | below_selector_resolution | 0.000003486 | 0.000008354 | 0.117647059 | 0.000000000 | 0.333333333 | 0.272727273 | False |
| submission_e282_appentropy_q2q3s2_tail_a0p010_e6e6ed48.csv | below_selector_resolution | below_selector_resolution | 0.000005950 | 0.000009969 | 0.117647059 | 0.000000000 | 0.090909091 | 0.000000000 | False |
| submission_e282_appentropy_q2q3s2_tail_a0p014_fc713d44.csv | below_selector_resolution | below_selector_resolution | 0.000008341 | 0.000014095 | 0.117647059 | 0.000000000 | 0.030303030 | 0.000000000 | False |
| submission_e282_appentropy_q2q3s2_linear_a0p006_c37fbb7d.csv | below_selector_resolution | below_selector_resolution | 0.000000831 | 0.000017805 | 0.352941176 | 0.000000000 | 0.121212121 | 0.000000000 | False |
| submission_e282_appentropy_q2q3s2_linear_a0p010_71a1114f.csv | below_selector_resolution | below_selector_resolution | 0.000000717 | 0.000030906 | 0.382352941 | 0.000000000 | 0.090909091 | 0.000000000 | False |

## Decision

No E282 app-entropy candidate is submission-ready. Best local row is `submission_e282_appentropy_q3_linear_a0p030_798f561b.csv` with decision `blocked_by_matched_placebo`. Keep the story-state hypothesis alive, but do not spend a public LB slot on these materializations.

## Files

- `e282_appentropy_story_state.csv`
- `e282_appentropy_story_materializer_candidates.csv`
- `e282_appentropy_story_materializer_nulls.csv`
- `e282_appentropy_story_materializer_scores.csv`
- `e282_appentropy_story_materializer_summary.csv`
