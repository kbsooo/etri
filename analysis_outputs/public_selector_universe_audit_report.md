# Public Selector Universe Audit

This audit removes the previous JEPA filename filter and scores every valid `submission*.csv` under `analysis_outputs/` and `jepa/` with the same public-anchor stress harness.

## Scope

- Scored candidates: `15871`.
- Skipped paths: `0`.
- Selector uncertainty reference: `0.001418568`.
- Public-bad-axis limit: `0.050`.

## Gate Counts

- Resolved-better than a2c8 gate: `0`.
- Frontier escape candidates: `91`.
- Novel frontier candidates: `19`.

## Family Summary

```csv
candidate_family,n,resolved_better,escape_candidates,novel_escape_candidates,low_bad_axis_rate,movement_over_uncertainty_rate,raw05_novel_movement_rate,majority_beats_a2c8_rate,best_source_path,best_priority_score,best_selector_p90_delta,best_selector_mean_delta,best_beats_a2c8_rate,best_bad_axis_abs_load,best_mean_abs_move_vs_a2c8,best_mean_abs_move_vs_raw05
cvjepa,88,0,39,9,0.931818182,1.0,0.556818182,0.443181818,analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0ba9eec.csv,0.000787755,0.00055295,0.00028779,0.505791506,0.02179632,0.008748977,0.001527641
hiddenblock_seqmotif,2882,0,4,4,0.913948647,1.0,1.0,0.001387925,analysis_outputs/submission_hiddenblock_paretomix_w0.65_d508e99b.csv,0.000802156,0.000563992,0.000289676,0.471042471,0.026914778,0.005389668,0.004555211
public6entropy,280,0,4,3,0.307142857,0.964285714,0.992857143,0.014285714,analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,0.000785399,0.000550609,0.000287117,0.517374517,0.026513129,0.007472062,0.001854409
axis_repair,94,0,4,3,0.510638298,1.0,0.989361702,0.042553191,analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv,0.00079401,0.000539282,0.000276693,0.787644788,0.02479001,0.008530873,0.0
raw05_jepa,2631,0,37,0,0.936906119,0.787913341,0.983656404,0.014063094,analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_bad_raw_ord_ortho_top60_strength_g160_e3189f46.csv,0.000790621,0.000556352,0.000295652,0.405405405,0.026844666,0.007849825,0.001438135
other_jepa,1557,0,1,0,0.706486834,1.0,0.999357739,0.002569043,jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p5_c20_bm0p35_sc0p5_q3_w0p2.csv,0.000784919,0.000551747,0.000292404,0.44015444,0.022910099,0.009226001,0.001746103
raw_timeline,7,0,1,0,0.857142857,1.0,0.857142857,0.142857143,jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.00079401,0.000539282,0.000276693,0.787644788,0.02479001,0.008530873,0.0
known_public,8,0,1,0,0.375,0.875,0.875,0.25,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.00079401,0.000539282,0.000276693,0.787644788,0.02479001,0.008530873,0.0
blockscale,544,0,0,0,0.433823529,1.0,1.0,0.0,analysis_outputs/submission_blockscale_jepa_raw05_rt_bc_nb_sg_loc_ridge_zctx_a12_blend0p2_q3s4_w0p05_410c9f71.csv,0.000782427,0.000553109,0.000334325,0.108108108,0.03663922,0.010135734,0.005887581
lejepa,63,0,0,0,0.111111111,1.0,1.0,0.0,analysis_outputs/submission_public_repair_raw05_antilejepa_q3_only_g0.040_90725dca.csv,0.000783569,0.000548476,0.000289335,0.436293436,0.026420538,0.009117456,0.001538034
blockpublic,180,0,0,0,0.9,1.0,1.0,0.0,analysis_outputs/submission_blockpublic_jepa_q3s4_35991e25.csv,0.000805809,0.000559454,0.000299107,0.355212355,0.027201686,0.006110445,0.00881558
energy_gate,280,0,0,0,0.867857143,1.0,1.0,0.0,analysis_outputs/submission_jepa_public_blockentropy_energy_balanced_core_q1_q3_s3_s4_g003_88872f51.csv,0.000809066,0.000572537,0.000326478,0.250965251,0.029795896,0.009970338,0.013522967
publicmask,100,0,0,0,0.82,1.0,1.0,0.0,analysis_outputs/submission_jepa_public_blockentropy_publicmask_core_q1_q3_s3_s4_g003_9e55efe2.csv,0.000812219,0.000575166,0.00032921,0.250965251,0.029571454,0.010365401,0.013659669
q2_specific,643,0,0,0,0.110419907,1.0,1.0,0.0,analysis_outputs/submission_jepa_public_blockentropy_seq1501_no_q2_g000_c4a9fa17.csv,0.000820513,0.000576933,0.000308245,0.150579151,0.033365901,0.004633471,0.00675993
directrob,39,0,0,0,0.0,1.0,1.0,0.0,analysis_outputs/submission_directrob_fa912ae4.csv,0.000832527,0.000579282,0.000342911,0.266409266,0.06097676,0.006192719,0.013045588
frontier_cvjepa,88,0,0,0,1.0,0.193181818,1.0,0.0,analysis_outputs/submission_frontier_cvjepa_refine_2ec9e953.csv,0.000842696,0.000588287,0.000291455,0.343629344,0.031242142,0.002911557,0.008862908
direct_inverse,40,0,0,0,0.475,0.7,1.0,0.0,analysis_outputs/submission_inverse7blend_2dc0510c.csv,0.000846708,0.000579168,0.000286467,0.216216216,0.036262698,0.000270789,0.00837701
episode_graph_rawstack,194,0,0,0,0.077319588,1.0,1.0,0.0,jepa/submission_jepa_episode_rawstack_raw05_er_strict075_rw1p0_ew0p25.csv,0.000890847,0.000665002,0.000421677,0.046332046,0.049065376,0.019960806,0.017758019
sparse_jepa_ladder,46,0,0,0,0.0,1.0,1.0,0.0,analysis_outputs/submission_sparsejepa_7162ff43.csv,0.000904052,0.00065389,0.000388427,0.038610039,0.053608065,0.013752752,0.018382182
targetwise,44,0,0,0,0.295454545,1.0,1.0,0.0,analysis_outputs/submission_targetabl_ef7e267d.csv,0.000956471,0.000676981,0.00038499,0.088803089,0.05805091,0.010945501,0.017525253
other,5142,0,0,0,0.244846363,1.0,1.0,0.000777907,analysis_outputs/submission_inv7gate_5db28d0b.csv,0.000992679,0.000710881,0.000414375,0.173745174,0.078962659,0.012161737,0.019721286
directcons,28,0,0,0,0.0,1.0,1.0,0.0,analysis_outputs/submission_directcons_bf4f6c46.csv,0.001139788,0.000753164,0.000418392,0.158301158,0.08207085,0.017653735,0.024366051
neural_episode_rawstack,873,0,0,0,0.0,1.0,1.0,0.0,jepa/submission_jepa_neural_episode_rawstack_raw05_nb_top075_none_rw0p75_nw0p5_ew0p0.csv,0.001282135,0.001018055,0.000647835,0.1003861,0.11644172,0.045921714,0.044963473
blockorth,9,0,0,0,0.0,1.0,1.0,0.0,analysis_outputs/submission_blockorth_f3e02850.csv,0.001341915,0.001019982,0.00064924,0.088803089,0.192055518,0.045636981,0.048460992
mixmin,11,0,0,0,0.0,1.0,1.0,0.0,analysis_outputs/submission_mixmin_5a4c25e0.csv,0.00135112,0.001015772,0.000654989,0.092664093,0.21489201,0.045989328,0.049403379
```

## Shortlist

```csv
source_path,candidate_family,selector_delta_vs_a2c8_public,selector_p90_delta_vs_a2c8_public,selector_stress_spread,beats_a2c8_scenario_rate,resolved_better_than_a2c8_gate,frontier_escape_candidate,novel_frontier_candidate,bad_axis_abs_load,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,submission_priority_score
analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,public6entropy,0.000287117,0.000550609,0.001255185,0.517374517,False,True,True,0.026513129,0.007472062,0.001854409,0.000785399
analysis_outputs/submission_public6entropy_raw05_ctx_g030_adcc5520.csv,public6entropy,0.000284679,0.000552932,0.001254997,0.555984556,False,True,True,0.023413405,0.007858149,0.002070869,0.000787208
analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0ba9eec.csv,cvjepa,0.00028779,0.00055295,0.001258995,0.505791506,False,True,True,0.02179632,0.008748977,0.001527641,0.000787755
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ba2783d3.csv,cvjepa,0.000287826,0.000552962,0.001259065,0.505791506,False,True,True,0.021823508,0.008738629,0.001533294,0.000787786
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ff9a333c.csv,cvjepa,0.000287784,0.000552976,0.001259029,0.505791506,False,True,True,0.021791605,0.00874252,0.001534281,0.000787788
analysis_outputs/submission_raw05_cvjepa_surprise_graft_cb6e0af2.csv,cvjepa,0.000287049,0.000553003,0.001261044,0.517374517,False,True,True,0.02062248,0.008725375,0.001508297,0.000788043
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9e024d5b.csv,cvjepa,0.000286946,0.00055299,0.001261272,0.521235521,False,True,True,0.02053572,0.008724207,0.001508297,0.000788063
analysis_outputs/submission_raw05_cvjepa_surprise_graft_87cd58a0.csv,cvjepa,0.000287967,0.000554016,0.001258271,0.513513514,False,True,True,0.02151278,0.008768361,0.001764068,0.000788634
analysis_outputs/submission_public6entropy_raw05_noq2_g030_1fcb614c.csv,public6entropy,0.000285625,0.00055498,0.001255858,0.532818533,False,True,True,0.024854118,0.007264884,0.002630502,0.000789662
analysis_outputs/submission_raw05_cvjepa_surprise_graft_8b2f4c54.csv,cvjepa,0.000288322,0.000554696,0.001261978,0.513513514,False,True,True,0.020159421,0.008841416,0.001675886,0.00078985
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9cbdda72.csv,cvjepa,0.000288209,0.000554682,0.001262231,0.513513514,False,True,True,0.020063021,0.008840248,0.001675886,0.000789872
analysis_outputs/submission_raw05_cvjepa_surprise_graft_c0fc8aea.csv,cvjepa,0.000289571,0.00055916,0.001263085,0.501930502,False,True,True,0.019390254,0.009013981,0.002151314,0.000794415
analysis_outputs/submission_public_repair_rawaxis_s0.875_4bfcf007.csv,axis_repair,0.0002951,0.000564661,0.001280778,0.67953668,False,True,True,0.021691259,0.011336076,0.004911422,0.00080373
analysis_outputs/submission_hiddenblock_rawgate_s_all_s0.7_5ccfb1c6.csv,hiddenblock_seqmotif,0.000290359,0.000570019,0.001271395,0.536679537,False,True,True,0.024789422,0.007655433,0.004490536,0.000807787
analysis_outputs/submission_public_repair_rawaxis_s1.125_45affdb6.csv,axis_repair,0.000277631,0.000573462,0.00126563,0.833976834,False,True,True,0.027888761,0.00825137,0.004911422,0.000810524
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_0331e2e5.csv,hiddenblock_seqmotif,0.000289873,0.000572027,0.00128125,0.501930502,False,True,True,0.026548123,0.005910386,0.005648507,0.000812082
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_4b6b636a.csv,hiddenblock_seqmotif,0.000289832,0.000572143,0.001281659,0.501930502,False,True,True,0.026530571,0.005903853,0.00566327,0.000812277
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_b151e1b9.csv,hiddenblock_seqmotif,0.000290165,0.000572289,0.001283827,0.501930502,False,True,True,0.026695038,0.005906429,0.005678562,0.000812882
analysis_outputs/submission_public_repair_rawaxis_s0.750_8f3da762.csv,axis_repair,0.000314683,0.000577572,0.00130685,0.583011583,False,True,True,0.018592508,0.015455034,0.009822845,0.000821267
analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv,axis_repair,0.000276693,0.000539282,0.001256328,0.787644788,False,True,False,0.02479001,0.008530873,0.0,0.00079401
jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,raw_timeline,0.000276693,0.000539282,0.001256328,0.787644788,False,True,False,0.02479001,0.008530873,0.0,0.00079401
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,known_public,0.000276693,0.000539282,0.001256328,0.787644788,False,True,False,0.02479001,0.008530873,0.0,0.00079401
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv,raw05_jepa,0.000276757,0.000539343,0.001256167,0.787644788,False,True,False,0.024783259,0.008526328,6.871e-06,0.000794038
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_strength_prob_bad_raw_ortho_g00075_662099aa.csv,raw05_jepa,0.000276755,0.000539346,0.00125617,0.787644788,False,True,False,0.024781132,0.00852612,7.445e-06,0.000794041
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00100_a6ce392e.csv,raw05_jepa,0.000276778,0.000539363,0.001256113,0.787644788,False,True,False,0.024781008,0.008524813,9.161e-06,0.000794047
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_entropy_prob_bad_raw_ortho_g00100_acf7638d.csv,raw05_jepa,0.000276764,0.000539358,0.001256145,0.787644788,False,True,False,0.024777131,0.008525054,9.095e-06,0.000794048
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00100_306226f5.csv,raw05_jepa,0.000276828,0.000539374,0.001256031,0.787644788,False,True,False,0.024828414,0.008525668,9.66e-06,0.000794048
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00100_f22e587f.csv,raw05_jepa,0.000276825,0.000539383,0.001256047,0.787644788,False,True,False,0.024821304,0.008525695,1.1324e-05,0.00079406
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00075_894a53ad.csv,raw05_jepa,0.000276833,0.000539387,0.001256039,0.787644788,False,True,False,0.024823352,0.008525712,1.1737e-05,0.000794062
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00150_76bed8db.csv,raw05_jepa,0.000276869,0.000539404,0.001255942,0.787644788,False,True,False,0.024837869,0.008524213,1.2886e-05,0.000794062
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00150_c968b72d.csv,raw05_jepa,0.000276821,0.000539403,0.001256005,0.787644788,False,True,False,0.024776506,0.008521799,1.3741e-05,0.000794065
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00150_033ab59a.csv,raw05_jepa,0.000276896,0.00053942,0.001255882,0.787644788,False,True,False,0.024847615,0.008523127,1.4489e-05,0.000794068
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00100_f3f65865.csv,raw05_jepa,0.00027688,0.000539421,0.001255942,0.787644788,False,True,False,0.024834466,0.008524047,1.5649e-05,0.000794079
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00200_1e74fe02.csv,raw05_jepa,0.000276928,0.000539445,0.001255813,0.787644788,False,True,False,0.02485382,0.008522054,1.7181e-05,0.00079408
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_top40_prob_bad_raw_ortho_g00200_06cdf759.csv,raw05_jepa,0.000276962,0.00053946,0.001255732,0.787644788,False,True,False,0.024867925,0.0085206,1.8335e-05,0.000794081
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00150_c105c2bf.csv,raw05_jepa,0.000276891,0.000539433,0.001255906,0.787644788,False,True,False,0.024836951,0.008523191,1.6986e-05,0.000794084
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00200_92036fe6.csv,raw05_jepa,0.000276964,0.000539466,0.001255734,0.787644788,False,True,False,0.024866814,0.008520653,1.9319e-05,0.000794087
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00200_cf1cbb33.csv,raw05_jepa,0.000276958,0.000539484,0.001255766,0.787644788,False,True,False,0.024852596,0.008520706,2.2647e-05,0.000794109
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00150_59a513b2.csv,raw05_jepa,0.000276974,0.000539491,0.00125575,0.787644788,False,True,False,0.024856692,0.008520816,2.3473e-05,0.000794114
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00300_a6a42719.csv,raw05_jepa,0.000277046,0.000539526,0.001255556,0.787644788,False,True,False,0.024885722,0.008517818,2.5771e-05,0.000794115
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_logit_g00300_1e863baf.csv,raw05_jepa,0.000276936,0.000539517,0.001255707,0.787644788,False,True,False,0.024760026,0.008513344,2.6747e-05,0.000794117
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00300_bf5d732e.csv,raw05_jepa,0.000276949,0.000539523,0.00125568,0.787644788,False,True,False,0.02476472,0.008512722,2.7299e-05,0.000794118
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_ortho_g00300_6e667d7d.csv,raw05_jepa,0.000276948,0.000539523,0.001255682,0.787644788,False,True,False,0.024763245,0.008512754,2.7349e-05,0.000794119
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00600_f7995f68.csv,raw05_jepa,0.000277205,0.000539763,0.001255032,0.77992278,False,True,False,0.024739402,0.00849471,5.4595e-05,0.000794226
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_ortho_g00800_4a4e63a2.csv,raw05_jepa,0.000277779,0.000540011,0.001253956,0.764478764,False,True,False,0.025094989,0.008490867,7.6264e-05,0.000794311
analysis_outputs/submission_raw05_jepa_public6drift_raw05_s3_follow_ones_prob_bad_raw_ortho_g01200_348b390d.csv,raw05_jepa,0.000278207,0.000540367,0.001253838,0.756756757,False,True,False,0.024840781,0.008451538,0.000123327,0.000794608
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_follow_ones_prob_bad_raw_ortho_g01200_470f4e4c.csv,raw05_jepa,0.000278654,0.000540439,0.001253238,0.749034749,False,True,False,0.025231937,0.00847906,0.000120159,0.000794617
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_logit_g01200_ff70f5a5.csv,raw05_jepa,0.000278297,0.000540448,0.001253361,0.752895753,False,True,False,0.025217959,0.008472674,0.000129895,0.000794648
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_g01200_fe989cb6.csv,raw05_jepa,0.000278368,0.00054049,0.001253357,0.752895753,False,True,False,0.025236096,0.008470324,0.000134358,0.000794693
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_follow_ones_prob_bad_raw_ortho_g00800_5534de7c.csv,raw05_jepa,0.000278325,0.000540899,0.001253361,0.756756757,False,True,False,0.024996898,0.008409176,0.00022441,0.000795068
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s3_follow_ones_prob_bad_raw_ortho_g01200_0c4050bf.csv,raw05_jepa,0.000279285,0.000541261,0.001253398,0.722007722,False,True,False,0.02519507,0.008387771,0.000256561,0.000795468
analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_follow_signed_strength_prob_bad_raw_ortho_g01200_8daa05fc.csv,raw05_jepa,0.000280501,0.000541488,0.001252441,0.702702703,False,True,False,0.026505729,0.008390025,0.000280039,0.000795701
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_ones_g015_643dca92.csv,raw05_jepa,0.000280904,0.00054198,0.001253659,0.691119691,False,True,False,0.025983441,0.008268279,0.000389706,0.000796361
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_ones_g020_9130be82.csv,raw05_jepa,0.000282291,0.000542887,0.001253693,0.648648649,False,True,False,0.02638073,0.008185609,0.000519564,0.000797337
analysis_outputs/submission_raw05_cvjepa_surprise_graft_4f6bd5bf.csv,cvjepa,0.000283063,0.000544135,0.001256618,0.594594595,False,True,False,0.023364959,0.008586558,0.000386539,0.000798706
analysis_outputs/submission_raw05_cvjepa_surprise_graft_00bd151f.csv,cvjepa,0.000283161,0.000544191,0.001256633,0.594594595,False,True,False,0.023406809,0.008589855,0.00039274,0.000798771
analysis_outputs/submission_raw05_cvjepa_surprise_graft_80768e62.csv,cvjepa,0.000283241,0.000544263,0.001256757,0.586872587,False,True,False,0.023343758,0.008588449,0.000395699,0.000798858
analysis_outputs/submission_raw05_cvjepa_surprise_graft_6ba29f43.csv,cvjepa,0.000283267,0.000544273,0.001256753,0.586872587,False,True,False,0.02340774,0.008588245,0.0003984,0.000798877
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_bad_raw_ortho_top60_strength_g040_d2719cde.csv,raw05_jepa,0.000286054,0.000544189,0.001253722,0.532818533,False,True,False,0.028022213,0.008091159,0.000621857,0.000798894
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_raw_ortho_positive_top60_strength_g040_dadad1c4.csv,raw05_jepa,0.000285512,0.000544209,0.001254283,0.536679537,False,True,False,0.027449042,0.008084084,0.000632386,0.00079894
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_raw_ortho_top60_strength_g040_b96489a3.csv,raw05_jepa,0.000285528,0.000544221,0.001254241,0.536679537,False,True,False,0.027451365,0.008085299,0.000633781,0.000798945
analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0bbfc8e.csv,cvjepa,0.000284294,0.000544484,0.001256784,0.555984556,False,True,False,0.023901071,0.008610986,0.000395794,0.000799168
analysis_outputs/submission_public6entropy_raw05_q3s4_g030_5776b7ae.csv,public6entropy,0.000284777,0.000544646,0.001253845,0.563706564,False,True,False,0.027051603,0.008041056,0.000769726,0.000799232
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_ones_g030_22fb0479.csv,raw05_jepa,0.000285015,0.000544746,0.001253772,0.548262548,False,True,False,0.027174534,0.008030821,0.000779214,0.000799336
analysis_outputs/submission_raw05_cvjepa_surprise_graft_88f9bb0a.csv,cvjepa,0.000284517,0.000544693,0.001256863,0.548262548,False,True,False,0.023782185,0.00862372,0.000417189,0.000799375
analysis_outputs/submission_raw05_cvjepa_surprise_graft_f4eac11a.csv,cvjepa,0.000285367,0.000545112,0.001257172,0.544401544,False,True,False,0.0238023,0.008646094,0.000439771,0.000799857
analysis_outputs/submission_raw05_cvjepa_surprise_graft_e06a4da9.csv,cvjepa,0.000280998,0.000545377,0.001256867,0.613899614,False,True,False,0.022830915,0.008426345,0.000709029,0.000799922
analysis_outputs/submission_raw05_cvjepa_surprise_graft_d865222a.csv,cvjepa,0.000280938,0.00054537,0.001256973,0.613899614,False,True,False,0.02279013,0.008425177,0.000709029,0.00079993
analysis_outputs/submission_raw05_cvjepa_surprise_graft_fda4cee4.csv,cvjepa,0.000282744,0.000545313,0.001256629,0.583011583,False,True,False,0.023650138,0.008447174,0.00064272,0.000799933
analysis_outputs/submission_raw05_cvjepa_surprise_graft_10c411e1.csv,cvjepa,0.000282655,0.000545347,0.001256774,0.586872587,False,True,False,0.023523353,0.00844649,0.00064896,0.000799977
analysis_outputs/submission_raw05_cvjepa_surprise_graft_12e31828.csv,cvjepa,0.000284817,0.000545335,0.001257245,0.548262548,False,True,False,0.023277846,0.008635161,0.000492069,0.000800016
analysis_outputs/submission_raw05_cvjepa_surprise_graft_c3d9cd3d.csv,cvjepa,0.000285623,0.000545347,0.00125726,0.540540541,False,True,False,0.023670205,0.008661205,0.000463543,0.000800089
analysis_outputs/submission_raw05_cvjepa_surprise_graft_a9f915d2.csv,cvjepa,0.000284986,0.000545444,0.001257287,0.548262548,False,True,False,0.023289548,0.008642953,0.000502766,0.000800135
analysis_outputs/submission_raw05_cvjepa_surprise_graft_7da3c5e5.csv,cvjepa,0.000281973,0.000545836,0.001257023,0.598455598,False,True,False,0.02276076,0.008457577,0.000732092,0.000800401
analysis_outputs/submission_raw05_cvjepa_surprise_graft_a99b6518.csv,cvjepa,0.000282342,0.000546009,0.001257159,0.586872587,False,True,False,0.023016627,0.008434336,0.00075355,0.000800641
analysis_outputs/submission_raw05_cvjepa_surprise_graft_5ba5a755.csv,cvjepa,0.000282452,0.000546059,0.001257054,0.586872587,False,True,False,0.023027942,0.008439566,0.000757613,0.000800671
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_bad_raw_ord_ortho_top60_strength_g065_67c662ca.csv,raw05_jepa,0.000284877,0.000546476,0.00125298,0.575289575,False,True,False,0.025629356,0.008142442,0.000585087,0.000800672
analysis_outputs/submission_raw05_cvjepa_surprise_graft_916734bd.csv,cvjepa,0.000286005,0.00054607,0.001257692,0.540540541,False,True,False,0.023109828,0.008679599,0.000546743,0.000800814
analysis_outputs/submission_raw05_cvjepa_surprise_graft_4f89f1f1.csv,cvjepa,0.000283743,0.000546242,0.001257107,0.55984556,False,True,False,0.0234873,0.008471188,0.000734537,0.000800932
analysis_outputs/submission_raw05_cvjepa_surprise_graft_0dd10fa8.csv,cvjepa,0.000286195,0.000546191,0.001257738,0.540540541,False,True,False,0.02312283,0.008688581,0.000558629,0.000800947
```

## Known Controls

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

- If this universe audit still has zero strict winners, the plateau is not a naming-filter artifact.
- Families with many novel escape candidates but zero strict winners are useful teacher/gate pools, not direct submission evidence.
- Families with high movement but high bad-axis load should be used only as negative axes or anti-directions.

## Files

- `public_selector_universe_audit_candidates.csv`
- `public_selector_universe_audit_shortlist.csv`
- `public_selector_universe_audit_family_summary.csv`
- `public_selector_universe_audit_skipped.csv`
