# JEPA Selector Frontier Audit

This audit expands the previous 213-row candidate check to the JEPA-related submission universe and asks whether any existing representation moves far enough beyond selector uncertainty while staying off the known public-bad axes.

## Scope

- Scored candidates: `7318`.
- Skipped paths: `0`.
- Selector uncertainty reference: `0.001418568` from a2c8 stress spread.
- Public-bad-axis limit: `0.050`.

## Gate Counts

- Resolved-better than a2c8 gate: `0`.
- Frontier escape candidates: `86`.
- Novel frontier candidates, also moved away from raw05: `15`.
- Low-bad-axis + movement-over-uncertainty candidates: `4013`.

## Family Summary

```csv
candidate_family,n,escape_candidates,novel_escape_candidates,resolved_better,low_bad_axis_rate,movement_over_uncertainty_rate,raw05_novel_movement_rate,majority_beats_a2c8_rate,best_file,best_source_path,best_priority_score,best_selector_p90_delta,best_selector_mean_delta,best_beats_a2c8_rate,best_bad_axis_abs_load,best_mean_abs_move_vs_a2c8
cvjepa,176,39,9,0,0.965909091,0.596590909,0.778409091,0.221590909,submission_raw05_cvjepa_surprise_graft_4f6bd5bf.csv,analysis_outputs/submission_raw05_cvjepa_surprise_graft_4f6bd5bf.csv,0.000798706,0.000544135,0.000283063,0.594594595,0.023364959,0.008586558
raw05_jepa,2631,37,0,0,0.936906119,0.787913341,0.983656404,0.014063094,submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv,analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv,0.000794038,0.000539343,0.000276757,0.787644788,0.024783259,0.008526328
axis_repair,56,4,3,0,0.517857143,1.0,0.982142857,0.071428571,submission_public_repair_rawaxis_s1.000_bdba2431.csv,analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv,0.00079401,0.000539282,0.000276693,0.787644788,0.02479001,0.008530873
other,73,4,3,0,0.383561644,1.0,0.97260274,0.068493151,submission_public6entropy_raw05_q3s4_g030_5776b7ae.csv,analysis_outputs/submission_public6entropy_raw05_q3s4_g030_5776b7ae.csv,0.000799232,0.000544646,0.000284777,0.563706564,0.027051603,0.008041056
raw_timeline,7,1,0,0,0.857142857,1.0,0.857142857,0.142857143,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.00079401,0.000539282,0.000276693,0.787644788,0.02479001,0.008530873
other_jepa,2225,1,0,0,0.528089888,1.0,0.999550562,0.001797753,submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p2.csv,jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p2.csv,0.000804126,0.000550424,0.000283364,0.55984556,0.019112651,0.008857144
blockscale,594,0,0,0,0.449494949,1.0,1.0,0.0,submission_blockscale_jepa_raw05_rt_bc_nb_sg_loc_ridge_zctx_a12_blend0p2_q3s4_w0p05_410c9f71.csv,analysis_outputs/submission_blockscale_jepa_raw05_rt_bc_nb_sg_loc_ridge_zctx_a12_blend0p2_q3s4_w0p05_410c9f71.csv,0.000802427,0.000553109,0.000334325,0.108108108,0.03663922,0.010135734
lejepa,63,0,0,0,0.111111111,1.0,1.0,0.0,submission_public_repair_raw05_antilejepa_q3_only_g0.040_90725dca.csv,analysis_outputs/submission_public_repair_raw05_antilejepa_q3_only_g0.040_90725dca.csv,0.000803569,0.000548476,0.000289335,0.436293436,0.026420538,0.009117456
blockpublic,180,0,0,0,0.9,1.0,1.0,0.0,submission_blockpublic_jepa_q3s4_35991e25.csv,analysis_outputs/submission_blockpublic_jepa_q3s4_35991e25.csv,0.000825809,0.000559454,0.000299107,0.355212355,0.027201686,0.006110445
energy_gate,320,0,0,0,0.790625,0.99375,1.0,0.0,submission_jepa_public_blockentropy_energy_balanced_core_q1_q3_s3_s4_g003_88872f51.csv,analysis_outputs/submission_jepa_public_blockentropy_energy_balanced_core_q1_q3_s3_s4_g003_88872f51.csv,0.000829066,0.000572537,0.000326478,0.250965251,0.029795896,0.009970338
publicmask,100,0,0,0,0.82,1.0,1.0,0.0,submission_jepa_public_blockentropy_publicmask_core_q1_q3_s3_s4_g003_9e55efe2.csv,analysis_outputs/submission_jepa_public_blockentropy_publicmask_core_q1_q3_s3_s4_g003_9e55efe2.csv,0.000832219,0.000575166,0.00032921,0.250965251,0.029571454,0.010365401
neural_episode_rawstack,873,0,0,0,0.0,1.0,1.0,0.0,submission_jepa_neural_episode_rawstack_raw05_nb_top075_none_rw0p75_nw0p5_ew0p0.csv,jepa/submission_jepa_neural_episode_rawstack_raw05_nb_top075_none_rw0p75_nw0p5_ew0p0.csv,0.001302135,0.001018055,0.000647835,0.1003861,0.11644172,0.045921714
blockorth,9,0,0,0,0.0,1.0,1.0,0.0,submission_blockorth_f3e02850.csv,analysis_outputs/submission_blockorth_f3e02850.csv,0.001361915,0.001019982,0.00064924,0.088803089,0.192055518,0.045636981
mixmin,11,0,0,0,0.0,1.0,1.0,0.0,submission_mixmin_5a4c25e0.csv,analysis_outputs/submission_mixmin_5a4c25e0.csv,0.00137112,0.001015772,0.000654989,0.092664093,0.21489201,0.045989328
```

## Shortlist

```csv
source_path,candidate_family,selector_stress_mean,selector_delta_vs_a2c8_public,selector_p90_delta_vs_a2c8_public,selector_stress_spread,beats_a2c8_scenario_rate,frontier_escape_candidate,novel_frontier_candidate,resolved_better_than_a2c8_gate,bad_axis_abs_load,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,submission_priority_score
analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,other,0.577726438,0.000287117,0.000550609,0.001255185,0.517374517,True,True,False,0.026513129,0.007472062,0.001854409,0.000805399
analysis_outputs/submission_public6entropy_raw05_ctx_g030_adcc5520.csv,other,0.577724,0.000284679,0.000552932,0.001254997,0.555984556,True,True,False,0.023413405,0.007858149,0.002070869,0.000807208
analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0ba9eec.csv,cvjepa,0.577727111,0.00028779,0.00055295,0.001258995,0.505791506,True,True,False,0.02179632,0.008748977,0.001527641,0.000807755
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ba2783d3.csv,cvjepa,0.577727147,0.000287826,0.000552962,0.001259065,0.505791506,True,True,False,0.021823508,0.008738629,0.001533294,0.000807786
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ff9a333c.csv,cvjepa,0.577727105,0.000287784,0.000552976,0.001259029,0.505791506,True,True,False,0.021791605,0.00874252,0.001534281,0.000807788
analysis_outputs/submission_raw05_cvjepa_surprise_graft_cb6e0af2.csv,cvjepa,0.57772637,0.000287049,0.000553003,0.001261044,0.517374517,True,True,False,0.02062248,0.008725375,0.001508297,0.000808043
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9e024d5b.csv,cvjepa,0.577726267,0.000286946,0.00055299,0.001261272,0.521235521,True,True,False,0.02053572,0.008724207,0.001508297,0.000808063
analysis_outputs/submission_raw05_cvjepa_surprise_graft_87cd58a0.csv,cvjepa,0.577727288,0.000287967,0.000554016,0.001258271,0.513513514,True,True,False,0.02151278,0.008768361,0.001764068,0.000808634
analysis_outputs/submission_public6entropy_raw05_noq2_g030_1fcb614c.csv,other,0.577724946,0.000285625,0.00055498,0.001255858,0.532818533,True,True,False,0.024854118,0.007264884,0.002630502,0.000809662
analysis_outputs/submission_raw05_cvjepa_surprise_graft_8b2f4c54.csv,cvjepa,0.577727643,0.000288322,0.000554696,0.001261978,0.513513514,True,True,False,0.020159421,0.008841416,0.001675886,0.00080985
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9cbdda72.csv,cvjepa,0.57772753,0.000288209,0.000554682,0.001262231,0.513513514,True,True,False,0.020063021,0.008840248,0.001675886,0.000809872
analysis_outputs/submission_raw05_cvjepa_surprise_graft_c0fc8aea.csv,cvjepa,0.577728892,0.000289571,0.00055916,0.001263085,0.501930502,True,True,False,0.019390254,0.009013981,0.002151314,0.000814415
analysis_outputs/submission_public_repair_rawaxis_s0.875_4bfcf007.csv,axis_repair,0.577734421,0.0002951,0.000564661,0.001280778,0.67953668,True,True,False,0.021691259,0.011336076,0.004911422,0.00082373
analysis_outputs/submission_public_repair_rawaxis_s1.125_45affdb6.csv,axis_repair,0.577716952,0.000277631,0.000573462,0.00126563,0.833976834,True,True,False,0.027888761,0.00825137,0.004911422,0.000830524
analysis_outputs/submission_public_repair_rawaxis_s0.750_8f3da762.csv,axis_repair,0.577754004,0.000314683,0.000577572,0.00130685,0.583011583,True,True,False,0.018592508,0.015455034,0.009822845,0.000841267
analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv,axis_repair,0.577716014,0.000276693,0.000539282,0.001256328,0.787644788,True,False,False,0.02479001,0.008530873,0.0,0.00079401
jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,raw_timeline,0.577716014,0.000276693,0.000539282,0.001256328,0.787644788,True,False,False,0.02479001,0.008530873,0.0,0.00079401
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv,raw05_jepa,0.577716078,0.000276757,0.000539343,0.001256167,0.787644788,True,False,False,0.024783259,0.008526328,6.871e-06,0.000794038
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_strength_prob_bad_raw_ortho_g00075_662099aa.csv,raw05_jepa,0.577716076,0.000276755,0.000539346,0.00125617,0.787644788,True,False,False,0.024781132,0.00852612,7.445e-06,0.000794041
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00100_a6ce392e.csv,raw05_jepa,0.577716099,0.000276778,0.000539363,0.001256113,0.787644788,True,False,False,0.024781008,0.008524813,9.161e-06,0.000794047
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_entropy_prob_bad_raw_ortho_g00100_acf7638d.csv,raw05_jepa,0.577716085,0.000276764,0.000539358,0.001256145,0.787644788,True,False,False,0.024777131,0.008525054,9.095e-06,0.000794048
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00100_306226f5.csv,raw05_jepa,0.577716149,0.000276828,0.000539374,0.001256031,0.787644788,True,False,False,0.024828414,0.008525668,9.66e-06,0.000794048
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00100_f22e587f.csv,raw05_jepa,0.577716146,0.000276825,0.000539383,0.001256047,0.787644788,True,False,False,0.024821304,0.008525695,1.1324e-05,0.00079406
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00075_894a53ad.csv,raw05_jepa,0.577716154,0.000276833,0.000539387,0.001256039,0.787644788,True,False,False,0.024823352,0.008525712,1.1737e-05,0.000794062
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00150_76bed8db.csv,raw05_jepa,0.57771619,0.000276869,0.000539404,0.001255942,0.787644788,True,False,False,0.024837869,0.008524213,1.2886e-05,0.000794062
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00150_c968b72d.csv,raw05_jepa,0.577716142,0.000276821,0.000539403,0.001256005,0.787644788,True,False,False,0.024776506,0.008521799,1.3741e-05,0.000794065
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00150_033ab59a.csv,raw05_jepa,0.577716217,0.000276896,0.00053942,0.001255882,0.787644788,True,False,False,0.024847615,0.008523127,1.4489e-05,0.000794068
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00100_f3f65865.csv,raw05_jepa,0.577716201,0.00027688,0.000539421,0.001255942,0.787644788,True,False,False,0.024834466,0.008524047,1.5649e-05,0.000794079
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00200_1e74fe02.csv,raw05_jepa,0.577716249,0.000276928,0.000539445,0.001255813,0.787644788,True,False,False,0.02485382,0.008522054,1.7181e-05,0.00079408
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_top40_prob_bad_raw_ortho_g00200_06cdf759.csv,raw05_jepa,0.577716283,0.000276962,0.00053946,0.001255732,0.787644788,True,False,False,0.024867925,0.0085206,1.8335e-05,0.000794081
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00150_c105c2bf.csv,raw05_jepa,0.577716212,0.000276891,0.000539433,0.001255906,0.787644788,True,False,False,0.024836951,0.008523191,1.6986e-05,0.000794084
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00200_92036fe6.csv,raw05_jepa,0.577716285,0.000276964,0.000539466,0.001255734,0.787644788,True,False,False,0.024866814,0.008520653,1.9319e-05,0.000794087
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00200_cf1cbb33.csv,raw05_jepa,0.577716279,0.000276958,0.000539484,0.001255766,0.787644788,True,False,False,0.024852596,0.008520706,2.2647e-05,0.000794109
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00150_59a513b2.csv,raw05_jepa,0.577716295,0.000276974,0.000539491,0.00125575,0.787644788,True,False,False,0.024856692,0.008520816,2.3473e-05,0.000794114
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00300_a6a42719.csv,raw05_jepa,0.577716367,0.000277046,0.000539526,0.001255556,0.787644788,True,False,False,0.024885722,0.008517818,2.5771e-05,0.000794115
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_logit_g00300_1e863baf.csv,raw05_jepa,0.577716257,0.000276936,0.000539517,0.001255707,0.787644788,True,False,False,0.024760026,0.008513344,2.6747e-05,0.000794117
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00300_bf5d732e.csv,raw05_jepa,0.57771627,0.000276949,0.000539523,0.00125568,0.787644788,True,False,False,0.02476472,0.008512722,2.7299e-05,0.000794118
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_ortho_g00300_6e667d7d.csv,raw05_jepa,0.577716269,0.000276948,0.000539523,0.001255682,0.787644788,True,False,False,0.024763245,0.008512754,2.7349e-05,0.000794119
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00600_f7995f68.csv,raw05_jepa,0.577716526,0.000277205,0.000539763,0.001255032,0.77992278,True,False,False,0.024739402,0.00849471,5.4595e-05,0.000794226
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_ortho_g00800_4a4e63a2.csv,raw05_jepa,0.5777171,0.000277779,0.000540011,0.001253956,0.764478764,True,False,False,0.025094989,0.008490867,7.6264e-05,0.000794311
```

## Known Controls In This Audit

```csv
source_path,known_public_lb,selector_delta_vs_a2c8_public,selector_p90_delta_vs_a2c8_public,bad_axis_abs_load,mean_abs_move_vs_a2c8
analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,0.000283661,0.000579937,0.036905767,0.0
jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,0.000276693,0.000539282,0.02479001,0.008530873
analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,0.000433029,0.00081519,0.0,0.044009635
analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.578303365,0.001205926,0.001614994,0.551693149,0.128555445
analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.578427353,0.001410108,0.002004917,0.468006593,0.175679488
jepa/submission_jepa_latent_q2_w0p45.csv,0.579801286,0.003751651,0.003045501,1.511295353,0.07285159
jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv,0.580246819,0.002521755,0.002764675,1.275870766,0.12747362
jepa/submission_jepa_latent_residual_probe.csv,0.581227328,0.002914732,0.003549657,1.78904652,0.110359077
```

## Read

- `resolved_better_than_a2c8_gate` is the strict submission gate. A candidate failing it is not evidence of a public improvement.
- `frontier_escape_candidate` is a research gate: enough movement, low bad-axis load, tolerable p90 selector damage, and majority scenario wins. It can justify the next experiment family, not an automatic submission.
- `novel_frontier_candidate` additionally requires movement away from raw05. This is the important gate for escaping the current plateau instead of rediscovering raw05-compatible micro-variants.
- If no strict winner appears, the next useful action is not more raw05-compatible blending. It is a representation run that increases movement while preserving the low-bad-axis constraint.

## Files

- `jepa_selector_frontier_audit_candidates.csv`
- `jepa_selector_frontier_audit_shortlist.csv`
- `jepa_selector_frontier_audit_family_summary.csv`
- `jepa_selector_frontier_audit_skipped.csv`
