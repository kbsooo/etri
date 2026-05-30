# E283 App-Entropy Q3 Smooth Context Audit

## Question

Does the validated human/social app-entropy state help select public-positive E247-style Q3 feature-NN smoothing cells?

## Group Anatomy

| group | n_rows | e237_overlap | e230_swing_overlap | e230_risk_overlap | app_state_avg_z_mean | app_state_avg_z_median | app_story_score_mean | app_story_score_median | single_row_smooth_gain_sum_mean | single_row_smooth_gain_sum_median | rollback_amp_abs_mean | rollback_amp_abs_median | state_x_amp_mean | state_x_amp_median | story_x_amp_mean | story_x_amp_median | nn_dist_mean | nn_dist_median | app_state_high80_rate | app_story_high80_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e247_e256_common | 21 | 13 | 10 | 7 | 0.099883025 | 0.112987941 | -0.130371231 | -0.557958040 | 0.121572885 | 0.087624411 | 0.084600496 | 0.076433549 | 0.262617117 | 0.079531828 | -0.217881396 | -0.502151403 | 10.602562428 | 8.400505751 | 0.238095238 | 0.333333333 |
| e247_only | 13 | 0 | 0 | 0 | 0.235262155 | 0.266751516 | 0.570663416 | 0.752707008 | 0.077142999 | 0.077662709 | 0.039125051 | 0.038831354 | 0.070438926 | 0.049614491 | 0.101983060 | 0.083526026 | 6.118931537 | 5.832526616 | 0.153846154 | 0.384615385 |
| e256_only | 4 | 1 | 4 | 0 | 0.719623888 | 0.732049311 | 1.142024398 | 0.961202852 | 0.012322468 | 0.009735247 | 0.110316918 | 0.108228172 | 1.738090302 | 1.520934342 | 2.889477805 | 2.649937732 | 7.230545594 | 7.126368780 | 0.500000000 | 0.750000000 |
| neither | 212 | 11 | 11 | 14 | 0.058279146 | 0.157312483 | 0.001254692 | 0.145547465 | -0.022242629 | -0.008011203 | 0.029330058 | 0.022533769 | -0.019498017 | -0.032126766 | -0.043536276 | -0.020179682 | 7.221184574 | 6.967129993 | 0.198113208 | 0.169811321 |

## Local E246/E237 Geometry

- selectors tested: `28`
- local E237-like gate passes: `27`

| candidate_id | rule_family | pruned_cells | selected_smooth_gain_sum | selected_amp_mean | expected_loss_vs_e224 | adverse_reduction_vs_e224 | actual_adverse_reduction_vs_e224 | overlap_e237 | e237_like_gate | e237_like_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_e247_nn_smooth_sum_top34 | control | 34 | 3.555889570 | 0.067212826 | -0.000066519 | 0.000632592 | 0.000596176 | 13 | True | 0.073034939 |
| state_score_b0p2_top34 | appentropy_score | 34 | 3.506372762 | 0.067397688 | -0.000061310 | 0.000630796 | 0.000594381 | 12 | True | 0.072107346 |
| avoid_high_state_amp_b0p25_top34 | appentropy_amp_penalty | 34 | 3.532854941 | 0.065701635 | -0.000070271 | 0.000615942 | 0.000567876 | 12 | True | 0.071966486 |
| state_score_bm0p2_top34 | appentropy_score | 34 | 3.439892386 | 0.063990522 | -0.000077936 | 0.000604275 | 0.000578792 | 12 | True | 0.071912076 |
| story_score_b0p5_top34 | appentropy_story_score | 34 | 3.230850288 | 0.064052889 | -0.000058829 | 0.000603924 | 0.000569105 | 9 | True | 0.069005129 |
| control_e256_top50_amp_then_smooth25 | control_known_public_worse | 25 | 2.602320463 | 0.088715124 | -0.000047418 | 0.000615602 | 0.000592484 | 14 | True | 0.068441797 |
| avoid_high_state_amp_b0p5_top34 | appentropy_amp_penalty | 34 | 3.411481840 | 0.062131838 | -0.000062881 | 0.000590100 | 0.000542035 | 11 | True | 0.068193431 |
| avoid_high_state_amp_b0p75_top34 | appentropy_amp_penalty | 34 | 3.406312188 | 0.061979789 | -0.000057967 | 0.000578579 | 0.000530514 | 11 | True | 0.066409444 |
| state_score_bm0p4_top34 | appentropy_score | 34 | 3.148192503 | 0.057152282 | -0.000081682 | 0.000542064 | 0.000518391 | 10 | True | 0.066248229 |
| story_score_bm0p5_top34 | appentropy_story_score | 34 | 2.968631478 | 0.056605483 | -0.000080644 | 0.000540874 | 0.000535545 | 11 | True | 0.065932246 |
| avoid_high_state_amp_b1p0_top34 | appentropy_amp_penalty | 34 | 3.062240089 | 0.055706812 | -0.000075031 | 0.000545845 | 0.000508541 | 9 | True | 0.065443991 |
| state_score_b0p4_top34 | appentropy_score | 34 | 3.325872962 | 0.061612976 | -0.000050749 | 0.000568475 | 0.000545106 | 10 | True | 0.064383426 |
| state_score_bm0p2_top25 | appentropy_score | 25 | 3.029836866 | 0.073603709 | -0.000072884 | 0.000509805 | 0.000497198 | 9 | True | 0.061743852 |
| story_lowmid_smooth_top34 | appentropy_story_band | 34 | 2.530627580 | 0.048013481 | -0.000083809 | 0.000494441 | 0.000465781 | 8 | True | 0.061427185 |
| state_score_b0p75_top34 | appentropy_score | 34 | 3.010783991 | 0.057032369 | -0.000055301 | 0.000530288 | 0.000506919 | 9 | True | 0.061210345 |
| state_band_lowmid_smooth_top34 | appentropy_band | 34 | 2.690665668 | 0.051329332 | -0.000069010 | 0.000497935 | 0.000456668 | 8 | True | 0.059829623 |
| state_band_mid_smooth_top34 | appentropy_band | 34 | 2.757619906 | 0.055684291 | -0.000048589 | 0.000507825 | 0.000444865 | 9 | True | 0.058060396 |
| state_score_b0p2_top25 | appentropy_score | 25 | 2.986021875 | 0.071995283 | -0.000055534 | 0.000488710 | 0.000465341 | 9 | True | 0.057130464 |
| story_score_bm0p5_top25 | appentropy_story_score | 25 | 2.643796404 | 0.066713097 | -0.000071807 | 0.000463529 | 0.000458718 | 9 | True | 0.056951387 |
| state_score_bm0p4_top25 | appentropy_score | 25 | 2.808153323 | 0.066858641 | -0.000069462 | 0.000461693 | 0.000445352 | 8 | True | 0.056444346 |
| state_score_b0p4_top25 | appentropy_score | 25 | 2.806785165 | 0.069094828 | -0.000049604 | 0.000465429 | 0.000442060 | 9 | True | 0.053948989 |
| story_score_b0p5_top25 | appentropy_story_score | 25 | 2.811377735 | 0.069310631 | -0.000050458 | 0.000460686 | 0.000437317 | 9 | True | 0.053668167 |
| state_score_bm0p75_top34 | appentropy_score | 34 | 2.751415696 | 0.049388908 | -0.000053409 | 0.000455699 | 0.000433623 | 7 | True | 0.053514627 |
| state_band_midhigh_smooth_top34 | appentropy_band | 34 | 2.516228584 | 0.056162384 | -0.000015879 | 0.000505661 | 0.000459192 | 8 | True | 0.052987224 |
| state_score_b0p75_top25 | appentropy_score | 25 | 2.568186539 | 0.063157346 | -0.000040336 | 0.000410825 | 0.000400063 | 7 | True | 0.047246126 |
| story_mid_smooth_top34 | appentropy_story_band | 34 | 2.149623129 | 0.042418962 | -0.000035111 | 0.000396018 | 0.000348595 | 6 | True | 0.044754241 |
| state_score_bm0p75_top25 | appentropy_score | 25 | 2.158388204 | 0.053380152 | -0.000050291 | 0.000362249 | 0.000352780 | 6 | True | 0.043706486 |
| story_midhigh_smooth_top34 | appentropy_story_band | 34 | 2.350487204 | 0.053181251 | 0.000010185 | 0.000459216 | 0.000412746 | 6 | False | 0.041133783 |

## Current-Anchor Governor

- materialized non-current candidates: `27`
- selected public-anchor models: `1`
- old strict-promote candidates: `0`
- matched-placebo gate passes: `0`
- public-free submission-ready candidates: `0`

| basename | selector_id | final_decision | rule_family | e247_overlap | mean_app_state | mean_app_story | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | matched_placebo_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e283_appentropy_q3smooth_avoid_high_state_amp_b0p25_top34_3cf3998d.csv | avoid_high_state_amp_b0p25_top34 | too_small_to_submit | appentropy_amp_penalty | 32 | 0.087094887 | 0.095741608 | too_small_to_submit | -0.000008442 | -0.000005847 | 0.000000000 | 0.515151515 | 0.272727273 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p2_top34_7b77be3e.csv | state_score_bm0p2_top34 | too_small_to_submit | appentropy_score | 29 | -0.188903743 | -0.219111643 | too_small_to_submit | -0.000010008 | -0.000004766 | 0.000000000 | 0.696969697 | 0.636363636 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p2_top34_3c3d79ca.csv | state_score_b0p2_top34 | below_selector_resolution | appentropy_score | 31 | 0.328583648 | 0.306488216 | below_selector_resolution | 0.000003948 | 0.000005031 | 0.000000000 | 0.121212121 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_avoid_high_state_amp_b0p75_top34_28fa62a3.csv | avoid_high_state_amp_b0p75_top34 | too_small_to_submit | appentropy_amp_penalty | 30 | -0.029054113 | -0.033701064 | too_small_to_submit | -0.000006633 | 0.000007813 | 0.000000000 | 0.303030303 | 0.000000000 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p4_top34_654f73d5.csv | state_score_b0p4_top34 | below_selector_resolution | appentropy_score | 27 | 0.576463123 | 0.540725996 | below_selector_resolution | 0.000001066 | 0.000010612 | 0.000000000 | 0.393939394 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_story_score_b0p5_top34_2c4685c1.csv | story_score_b0p5_top34 | below_selector_resolution | appentropy_story_score | 26 | 0.577235013 | 0.722888088 | below_selector_resolution | 0.000011899 | 0.000014858 | 0.000000000 | 0.242424242 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p2_top25_e9f51565.csv | state_score_bm0p2_top25 | below_selector_resolution | appentropy_score | 25 | -0.027632592 | -0.059365845 | below_selector_resolution | 0.000003552 | 0.000015399 | 0.000000000 | 0.848484848 | 0.727272727 | False |
| submission_e283_appentropy_q3smooth_avoid_high_state_amp_b0p5_top34_e0f4cb23.csv | avoid_high_state_amp_b0p5_top34 | below_selector_resolution | appentropy_amp_penalty | 30 | 0.025084959 | -0.018418130 | below_selector_resolution | 0.000006352 | 0.000017059 | 0.000000000 | 0.212121212 | 0.000000000 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p2_top25_7ce118ed.csv | state_score_b0p2_top25 | below_selector_resolution | appentropy_score | 25 | 0.344672550 | 0.337189143 | below_selector_resolution | 0.000005377 | 0.000018102 | 0.000000000 | 0.545454545 | 0.363636364 | False |
| submission_e283_appentropy_q3smooth_story_score_b0p5_top25_c6cb83ef.csv | story_score_b0p5_top25 | too_small_to_submit | appentropy_story_score | 23 | 0.547434785 | 0.644572385 | too_small_to_submit | -0.000000928 | 0.000019068 | 0.000000000 | 0.212121212 | 0.181818182 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p4_top34_1d49d9c6.csv | state_score_bm0p4_top34 | below_selector_resolution | appentropy_score | 25 | -0.515749078 | -0.500765571 | below_selector_resolution | 0.000006846 | 0.000021926 | 0.000000000 | 0.575757576 | 0.454545455 | False |
| submission_e283_appentropy_q3smooth_story_score_bm0p5_top34_357f766a.csv | story_score_bm0p5_top34 | below_selector_resolution | appentropy_story_score | 22 | -0.462540488 | -0.790641902 | below_selector_resolution | 0.000003111 | 0.000022309 | 0.000000000 | 0.545454545 | 0.363636364 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p75_top25_1411126b.csv | state_score_b0p75_top25 | too_small_to_submit | appentropy_score | 19 | 0.780109758 | 0.693371459 | too_small_to_submit | -0.000009063 | 0.000027570 | 0.000000000 | 0.151515152 | 0.000000000 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p4_top25_d18f9eba.csv | state_score_b0p4_top25 | below_selector_resolution | appentropy_score | 23 | 0.583461191 | 0.612870215 | below_selector_resolution | 0.000009565 | 0.000027863 | 0.000000000 | 0.393939394 | 0.272727273 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p4_top25_2161ebfa.csv | state_score_bm0p4_top25 | below_selector_resolution | appentropy_score | 21 | -0.382507807 | -0.413417298 | below_selector_resolution | 0.000001759 | 0.000029042 | 0.000000000 | 0.727272727 | 0.636363636 | False |
| submission_e283_appentropy_q3smooth_state_score_b0p75_top34_a838ce32.csv | state_score_b0p75_top34 | below_selector_resolution | appentropy_score | 23 | 0.771401380 | 0.721988524 | below_selector_resolution | 0.000014636 | 0.000030611 | 0.000000000 | 0.272727273 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p75_top34_f86186ed.csv | state_score_bm0p75_top34 | too_small_to_submit | appentropy_score | 20 | -0.752978450 | -0.718645270 | too_small_to_submit | -0.000000945 | 0.000035033 | 0.000000000 | 0.484848485 | 0.272727273 | False |
| submission_e283_appentropy_q3smooth_story_score_bm0p5_top25_639584f4.csv | story_score_bm0p5_top25 | below_selector_resolution | appentropy_story_score | 19 | -0.426369304 | -0.746889867 | below_selector_resolution | 0.000010490 | 0.000037275 | 0.000000000 | 0.606060606 | 0.363636364 | False |
| submission_e283_appentropy_q3smooth_state_band_mid_smooth_top34_4c40d3af.csv | state_band_mid_smooth_top34 | below_selector_resolution | appentropy_band | 21 | 0.148696650 | 0.011685674 | below_selector_resolution | 0.000026297 | 0.000038138 | 0.000000000 | 0.151515152 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_state_band_lowmid_smooth_top34_f03daba1.csv | state_band_lowmid_smooth_top34 | below_selector_resolution | appentropy_band | 20 | -0.330746801 | -0.450075927 | below_selector_resolution | 0.000014519 | 0.000048457 | 0.000000000 | 0.696969697 | 0.545454545 | False |
| submission_e283_appentropy_q3smooth_avoid_high_state_amp_b1p0_top34_b7535859.csv | avoid_high_state_amp_b1p0_top34 | below_selector_resolution | appentropy_amp_penalty | 27 | -0.059955437 | -0.128976314 | below_selector_resolution | 0.000019887 | 0.000048797 | 0.000000000 | 0.606060606 | 0.545454545 | False |
| submission_e283_appentropy_q3smooth_state_score_bm0p75_top25_34144316.csv | state_score_bm0p75_top25 | below_selector_resolution | appentropy_score | 14 | -0.969945857 | -1.030271666 | below_selector_resolution | 0.000000814 | 0.000049037 | 0.000000000 | 0.363636364 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_state_band_midhigh_smooth_top34_1b51c424.csv | state_band_midhigh_smooth_top34 | below_selector_resolution | appentropy_band | 21 | 0.647504723 | 0.689900047 | below_selector_resolution | 0.000049279 | 0.000064648 | 0.000000000 | 0.151515152 | 0.090909091 | False |
| submission_e283_appentropy_q3smooth_control_e256_top50_amp_then_smooth25_b9f15c68.csv | control_e256_top50_amp_then_smooth25 | below_selector_resolution | control_known_public_worse | 21 | 0.199041563 | 0.073212069 | below_selector_resolution | 0.000051379 | 0.000065211 | 0.000000000 | 0.000000000 | 0.000000000 | False |
| submission_e283_appentropy_q3smooth_story_lowmid_smooth_top34_adbafcf9.csv | story_lowmid_smooth_top34 | below_selector_resolution | appentropy_story_band | 17 | -0.300718594 | -0.660200254 | below_selector_resolution | 0.000050189 | 0.000082271 | 0.000000000 | 0.757575758 | 0.636363636 | False |
| submission_e283_appentropy_q3smooth_story_midhigh_smooth_top34_5eef7b82.csv | story_midhigh_smooth_top34 | blocked_by_e246_local_geometry | appentropy_story_band | 19 | 0.669543921 | 0.846247246 | below_selector_resolution | 0.000067166 | 0.000088398 | 0.000000000 | 0.121212121 | 0.000000000 | False |
| submission_e283_appentropy_q3smooth_story_mid_smooth_top34_616365da.csv | story_mid_smooth_top34 | below_selector_resolution | appentropy_story_band | 14 | 0.173447501 | 0.056086114 | below_selector_resolution | 0.000079171 | 0.000117226 | 0.000000000 | 0.151515152 | 0.090909091 | False |

## Decision

No app-entropy-conditioned Q3 smoothing selector is submission-ready. App-entropy explains some E247/E256 cell anatomy, but it does not currently improve the public-positive E247 mechanism in a placebo-resistant way.

## Interpretation

The useful human/social state is not dead, but this audit separates two roles. App-entropy can describe lifestyle context around Q3 cells, while E247's public win still comes from feature-neighbor smoothing geometry. Replacing or refilling E247 cells by app-entropy criteria is not yet certified.

## Files

- `e283_appentropy_q3_smooth_context_group_summary.csv`
- `e283_appentropy_q3_smooth_context_local_summary.csv`
- `e283_appentropy_q3_smooth_context_candidate_summary.csv`
- `e283_appentropy_q3_smooth_context_summary.csv`
- `e283_appentropy_q3_smooth_context_scores.csv`
