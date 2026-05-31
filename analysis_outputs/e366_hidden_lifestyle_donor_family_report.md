# E366 Hidden Lifestyle-State Donor-Family Latent

## Question

Can the E365 Q3/S1 donor-graft support set be turned into a row-wise hidden lifestyle-state latent, or is the selected E365 point already the non-linear optimum?

## Method

- Anchor: E247 public-best probability tensor.
- Source family: E365 jackknife-supported donor-graft members (`q3s1`, `q3`, `s1` when available).
- Hidden state: E328/E358 own-lifestyle latent, row-state bad/good cluster rates, and selected human/social story tails.
- Generated actions: family centers, target-cell recombinations, and row-state gates such as phone-bed, finance/cashflow, routine pressure, recovery fatigue, and E323-heavy clusters.
- Stress: E363 output/row-state gates, E364 known-public movement-axis score, and E365-style feature-view + leave-public-out jackknife.

## Inputs

- generated candidates: `79`
- known public rows available: `13`
- feature views: `all`(129), `axis`(62), `target`(49), `anatomy`(18), `bad_good`(38), `compact`(20)
- E365 reference variant: `e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11`

## Source Family

| key | variant | file | support_top1 | support_top5 | support_top10 | support_rank_mean | support_score_mean | e364_public_like_score | e363_robust_score | rowstate_loss | rowstate_exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3s1 | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_07638e6a.csv | 42.000000 | 62.000000 | 68.000000 | 4.738095 | 4.618581 | 5.169168 | 0.637083 | 0.000438 | 0.137438 |
| q3 | e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_92cfe11c.csv | 34.000000 | 77.000000 | 82.000000 | 2.626506 | 4.635703 | 4.735687 | 0.671772 | 0.000702 | 0.135241 |
| s1 | e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1198dfee.csv | 0.000000 | 58.000000 | 83.000000 | 4.253012 | 4.589847 | 5.067970 | 0.602529 | 0.000467 | 0.137067 |

## Scenario Summary

| feature_view | scenarios | top_generated_rate | top_e365_rate | e365_rank_mean | generated_gated_mean |
| --- | --- | --- | --- | --- | --- |
| all | 14 | 1.000000 | 0.000000 | 16.428571 | 23.000000 |
| anatomy | 14 | 0.785714 | 0.000000 | 8.714286 | 23.000000 |
| axis | 14 | 1.000000 | 0.000000 | 67.214286 | 23.000000 |
| bad_good | 14 | 1.000000 | 0.000000 | 63.071429 | 23.000000 |
| compact | 14 | 1.000000 | 0.000000 | 9.214286 | 23.000000 |
| target | 14 | 1.000000 | 0.000000 | 7.142857 | 23.000000 |

## Top Jackknife Support

| variant | family | candidate_origin | top1_count | top5_count | top10_count | rank_mean | score_mean | pred_mean | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2 | null_row_lifestyle_gate | e366_generated | 81 | 84 | 84 | 1.071429 | 5.371914 | 0.000275 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2_a91d9ac9.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.00_s10.70 | target_scale | e364_existing | 3 | 3 | 3 | 60.608696 | 4.169758 | 0.000184 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_00_s10_70_e42abfdd.csv |
| e366_targetrow_q3_good_s1_bad_cluster_356_bad | target_row_lifestyle_gate | e366_generated | 0 | 84 | 84 | 2.345238 | 5.234847 | 0.000274 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_targetrow_q3_good_s1_bad_cluster_356_bad_033b92ee.csv |
| e366_targetrow_q3_good_s1_bad_energy_x_recovery | target_row_lifestyle_gate | e366_generated | 0 | 82 | 84 | 2.821429 | 5.213613 | 0.000275 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_targetrow_q3_good_s1_bad_energy_x_recovery_d26c08c7.csv |
| e366_nulltargetrow_q3_good_s1_bad_random_rate_match_0 | null_row_lifestyle_gate | e366_generated | 0 | 81 | 83 | 4.535714 | 5.125286 | 0.000277 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_nulltargetrow_q3_good_s1_bad_random_rate_match_0_220c8af8.csv |
| e366_nulltargetrow_q3_good_s1_bad_perm_cluster_1 | null_row_lifestyle_gate | e366_generated | 0 | 81 | 84 | 4.702381 | 5.132192 | 0.000275 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_nulltargetrow_q3_good_s1_bad_perm_cluster_1_ea93afcb.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.00_s10.70 | target_scale | e364_existing | 0 | 3 | 3 | 59.434783 | 4.176261 | 0.000183 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_00_s10_70_f4284749.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 2 | 14 | 32.888889 | 4.302562 | 0.000332 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_3aeb0277.csv |
| e366_nulltargetrow_q3_good_s1_bad_random_rate_match_2 | null_row_lifestyle_gate | e366_generated | 0 | 0 | 82 | 6.511905 | 5.039543 | 0.000276 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_nulltargetrow_q3_good_s1_bad_random_rate_match_2_c0af2326.csv |
| e366_rowlatent_weekend_to_q3s1_s1.00 | row_lifestyle_gate | e366_generated | 0 | 0 | 71 | 8.714286 | 4.944850 | 0.000290 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_rowlatent_weekend_to_q3s1_s1_00_5f17f63d.csv |
| e366_pair_q3s1_q3_wa0.60 | pair_center | e366_generated | 0 | 0 | 75 | 8.952381 | 4.943361 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_60_4b049b1e.csv |
| e366_rowlatent_weekend_to_q3s1_s0.70 | row_lifestyle_gate | e366_generated | 0 | 0 | 52 | 11.392857 | 4.902455 | 0.000291 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_rowlatent_weekend_to_q3s1_s0_70_d0af5b60.csv |
| e366_pair_q3s1_q3_wa0.60_amp1.03 | pair_center_amp | e366_generated | 0 | 0 | 29 | 11.821429 | 4.893889 | 0.000285 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_60_amp1_03_cdafc393.csv |
| e366_pair_q3s1_q3_wa0.40_amp1.03 | pair_center_amp | e366_generated | 0 | 0 | 27 | 13.250000 | 4.871964 | 0.000289 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_40_amp1_03_293e618f.csv |
| e366_targetrow_s1_tail_only_cluster_356_bad | target_row_lifestyle_gate | e366_generated | 0 | 0 | 0 | 13.428571 | 4.862820 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_targetrow_s1_tail_only_cluster_356_bad_b1327fd7.csv |
| e366_pair_q3s1_q3_wa0.50 | pair_center | e366_generated | 0 | 0 | 0 | 13.892857 | 4.859165 | 0.000286 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_50_0bc9e0e0.csv |
| e366_pair_q3s1_q3_wa0.75 | pair_center | e366_generated | 0 | 0 | 13 | 14.059524 | 4.865198 | 0.000281 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_75_5fb708de.csv |
| e366_pair_q3s1_q3_wa0.50_amp1.03 | pair_center_amp | e366_generated | 0 | 0 | 0 | 16.333333 | 4.823081 | 0.000287 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_50_amp1_03_11402cea.csv |
| e366_pair_q3s1_q3_wa0.60_amp0.97 | pair_center_amp | e366_generated | 0 | 0 | 0 | 16.595238 | 4.826992 | 0.000283 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_60_amp0_97_aa621600.csv |
| e366_pair_q3s1_q3_wa0.75_amp1.03 | pair_center_amp | e366_generated | 0 | 0 | 0 | 18.083333 | 4.805433 | 0.000282 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_75_amp1_03_224e4408.csv |
| e366_center_support_amp1.03 | family_center_amp | e366_generated | 0 | 0 | 0 | 20.869048 | 4.748869 | 0.000285 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_center_support_amp1_03_ee963a1e.csv |
| e366_center_support | family_center | e366_generated | 0 | 0 | 0 | 21.750000 | 4.729146 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_center_support_18a69370.csv |
| e366_center_equal_amp1.03 | family_center_amp | e366_generated | 0 | 0 | 0 | 22.583333 | 4.719723 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_center_equal_amp1_03_1c47db5e.csv |
| e366_center_publicscore_amp1.03 | family_center_amp | e366_generated | 0 | 0 | 0 | 23.428571 | 4.715602 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_center_publicscore_amp1_03_556d1f7f.csv |
| e366_pair_q3s1_q3_wa0.75_amp0.97 | pair_center_amp | e366_generated | 0 | 0 | 0 | 25.261905 | 4.636230 | 0.000280 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_pair_q3s1_q3_wa0_75_amp0_97_fadbf126.csv |
| e366_center_top10_amp1.03 | family_center_amp | e366_generated | 0 | 0 | 0 | 26.285714 | 4.651742 | 0.000284 | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_center_top10_amp1_03_5da81906.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 13 | 28.216867 | 4.467325 | 0.000300 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1198dfee.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 37 | 28.630952 | 4.492405 | 0.000310 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_07638e6a.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 33.957746 | 4.178932 | 0.000194 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_45_s11_00_2ffbb23b.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.00_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 35.771429 | 4.290779 | 0.000185 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_00_s10_90_906fa0e1.csv |

## Top Public-Like Scores

| variant | family | candidate_origin | e366_public_like_score | e366_pred_public_delta_mean | e366_pred_public_delta_std | public_bad_axis_sum | rowstate_pred_public_loss_mean | rowstate_bad_minus_good_exposure | e363_robust_score | pred_delta_vs_current_p90 | e363_submission_gate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e362_ablate_s1_only_amp1.00 | target_ablation | e364_existing | 5.952012 | 0.000058 | 0.000034 | 0.000899 | 0.000168 | 0.116393 | 0.640512 | 0.000010 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_00_28f4e72a.csv |
| e362_ablate_s1_only_amp1.08 | target_ablation | e364_existing | 5.946426 | 0.000059 | 0.000034 | 0.000971 | 0.000168 | 0.116393 | 0.640011 | 0.000011 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_08_cc145be9.csv |
| e362_ablate_s1_only_amp1.16 | target_ablation | e364_existing | 5.945015 | 0.000059 | 0.000033 | 0.001043 | 0.000168 | 0.116393 | 0.639907 | 0.000012 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_16_5a253895.csv |
| e362_ablate_s1_only_amp1.28 | target_ablation | e364_existing | 5.941351 | 0.000060 | 0.000033 | 0.001151 | 0.000169 | 0.116393 | 0.639714 | 0.000013 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_28_e777faa5.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | e364_existing | 5.838709 | 0.000169 | 0.000082 | 0.000919 | 0.000344 | 0.132921 | 0.637054 | -0.000031 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_931f0560.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | e364_existing | 5.803183 | 0.000175 | 0.000082 | 0.001396 | 0.000445 | 0.123081 | 0.634631 | -0.000031 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_be304efd.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185 | donor_graft | e364_existing | 5.802402 | 0.000169 | 0.000081 | 0.004126 | 0.000158 | 0.125741 | 0.653773 | -0.000028 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185_1b400a58.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | e364_existing | 5.789279 | 0.000188 | 0.000084 | 0.000830 | 0.000258 | 0.131737 | 0.640696 | -0.000028 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_3399f779.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | e364_existing | 5.771291 | 0.000183 | 0.000094 | 0.000261 | 0.000224 | 0.128675 | 0.638258 | -0.000016 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_3de2bc86.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | e364_existing | 5.728348 | 0.000175 | 0.000088 | 0.001746 | 0.000486 | 0.120835 | 0.624350 | -0.000031 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_e213488e.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | e364_existing | 5.726907 | 0.000177 | 0.000091 | 0.001303 | 0.000392 | 0.133359 | 0.633761 | -0.000036 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_dd10e72d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | e364_existing | 5.723574 | 0.000193 | 0.000090 | 0.001225 | 0.000333 | 0.132434 | 0.638055 | -0.000034 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_90363a99.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.65 | donor_blend | e364_existing | 5.720420 | 0.000176 | 0.000089 | 0.000638 | 0.000278 | 0.129032 | 0.597363 | -0.000029 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_65_9d18265d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | e364_existing | 5.717447 | 0.000195 | 0.000080 | 0.002357 | 0.000385 | 0.124020 | 0.637398 | -0.000035 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_0432e2d5.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | e364_existing | 5.704444 | 0.000172 | 0.000083 | 0.003292 | 0.000355 | 0.124537 | 0.644026 | -0.000029 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_0087bcd7.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | e364_existing | 5.702703 | 0.000186 | 0.000102 | 0.000545 | 0.000308 | 0.130112 | 0.631426 | -0.000026 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_3d505f1d.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 5.682492 | 0.000163 | 0.000073 | 0.003790 | 0.000189 | 0.130609 | 0.651652 | -0.000031 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_9d0a49a1.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | e364_existing | 5.680150 | 0.000189 | 0.000084 | 0.002254 | 0.000467 | 0.125505 | 0.628607 | -0.000038 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_515efd3f.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.50 | donor_blend | e364_existing | 5.656336 | 0.000183 | 0.000095 | 0.000843 | 0.000337 | 0.130272 | 0.595164 | -0.000036 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_50_5a835e8b.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.35 | donor_blend | e364_existing | 5.600721 | 0.000199 | 0.000096 | 0.002152 | 0.000410 | 0.133144 | 0.631791 | -0.000039 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_35_421edebd.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.35 | donor_blend | e364_existing | 5.600661 | 0.000189 | 0.000103 | 0.001365 | 0.000409 | 0.131570 | 0.598165 | -0.000043 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_35_3a053152.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | e364_existing | 5.580901 | 0.000199 | 0.000085 | 0.002993 | 0.000427 | 0.126093 | 0.629305 | -0.000039 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_79e0b113.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | e364_existing | 5.574174 | 0.000182 | 0.000078 | 0.003739 | 0.000411 | 0.128913 | 0.634751 | -0.000030 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_a08578d3.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.35 | donor_blend | e364_existing | 5.565556 | 0.000186 | 0.000099 | 0.002359 | 0.000451 | 0.133800 | 0.625898 | -0.000041 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_35_489b55ae.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | e364_existing | 5.563483 | 0.000188 | 0.000089 | 0.002523 | 0.000506 | 0.123732 | 0.608806 | -0.000036 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_c978a341.csv |
| e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2 | null_row_lifestyle_gate | e366_generated | 5.563363 | 0.000167 | 0.000083 | 0.002947 | 0.000425 | 0.137331 | 0.655613 | -0.000053 | True | analysis_outputs/submission_e366_hiddenlife_donorlatent_e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2_a91d9ac9.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | e364_existing | 5.563183 | 0.000186 | 0.000099 | 0.001893 | 0.000407 | 0.134369 | 0.607159 | -0.000040 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_3c6c1204.csv |
| e362_ablate_q1_only_amp1.00 | target_ablation | e364_existing | 5.560450 | 0.000175 | 0.000086 | 0.003679 | 0.000097 | 0.134272 | 0.629324 | -0.000012 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_q1_only_amp1_00_c6299d65.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.35 | donor_blend | e364_existing | 5.558468 | 0.000192 | 0.000107 | 0.000830 | 0.000396 | 0.131541 | 0.621025 | -0.000036 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_35_8b8fe11c.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | e364_existing | 5.544745 | 0.000180 | 0.000091 | 0.003713 | 0.000411 | 0.126930 | 0.637440 | -0.000035 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_44b92316.csv |

## Decision

| decision | variant | family | candidate_origin | selected_uploadsafe_file | scenario_count | e365_top1_rate | e365_top10_rate | best_generated_variant | best_generated_top1_rate | best_generated_top10_rate | best_null_variant | best_null_top1_rate | best_null_top10_rate | e365_public_like_score | best_generated_public_like_score | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reject_e366_lifestyle_gate_keep_e365 | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv | 84 | 0.000000 | 0.166667 | e366_targetrow_q3_good_s1_bad_cluster_356_bad | 0.000000 | 1.000000 | e366_nulltargetrow_q3_good_s1_bad_perm_cluster_2 | 0.964286 | 1.000000 | 5.025616 | 5.436757 | A permuted/random null row gate beats the real lifestyle-state gates under jackknife. This kills the row-gate translator as a trustworthy hidden-state discovery; keep E365. |

## Interpretation

- If a generated row-lifestyle candidate beats E365 under jackknife and also beats null gates, the donor-graft signal is a transferable hidden state and not a one-file edge.
- If a permuted/random null gate beats the real lifestyle gate, the row-state translator is rejected even if its local score is high.
- If centers score well but fail top1/top10 stability, the family is real but non-linear; E365 should remain the actionable submission.
- If row-story gates underperform constant centers, the human/social latent is useful as a diagnostic exposure but not yet as a probability translator.

## Files

- `analysis_outputs/e366_hidden_lifestyle_donor_family_candidates.csv`
- `analysis_outputs/e366_hidden_lifestyle_donor_family_scores.csv`
- `analysis_outputs/e366_hidden_lifestyle_donor_family_scenarios.csv`
- `analysis_outputs/e366_hidden_lifestyle_donor_family_support.csv`
- `analysis_outputs/e366_hidden_lifestyle_donor_family_selection.csv`
