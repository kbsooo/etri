# Old-Positive Anchor Pairwise Rescore

Purpose: check whether candidates supported by the old hidden-subset selector also survive pairwise public-order stress, and whether any such candidate provides an independent S4/Q3 positive anchor.

## Counts

- rescored candidates: `212`
- old scenario-majority candidates: `97`
- old-majority AND pair-majority candidates: `0`
- old-majority AND pair-probe candidates: `0`
- q3/s4 share >= 0.70 candidates: `0`
- q3/s4 anchor-like candidates: `0`

## Old-Majority Candidates

source_path,candidate_family,selector_p90_delta_vs_a2c8_public,beats_a2c8_scenario_rate,pair_delta_vs_a2c8_p90,pair_beats_a2c8_rate,pair_delta_vs_raw05_p90,pair_beats_raw05_rate,q3s4_move_share,dominant_target,move_abs_a2c8_Q3,move_abs_a2c8_S4,bad_axis_abs_load,mean_abs_move_vs_a2c8,pair_probe_gate,pair_control_better_than_a2c8_gate,pair_selector_conflict
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_4b6b636a.csv,hiddenblock_seqmotif,0.000572143,0.501930502,6.7766e-05,0.178378378,1.0569e-05,0.610810811,0.404607558,Q3,0.009023188,0.007698017,0.026530571,0.005903853,False,False,False
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_0331e2e5.csv,hiddenblock_seqmotif,0.000572027,0.501930502,6.7775e-05,0.178378378,1.0525e-05,0.613513514,0.404516989,Q3,0.009037515,0.007698446,0.026548123,0.005910386,False,False,False
analysis_outputs/submission_hiddenblock_seqmotif_cellgate_b151e1b9.csv,hiddenblock_seqmotif,0.000572289,0.501930502,6.8333e-05,0.178378378,1.1766e-05,0.583783784,0.407939921,Q3,0.009119654,0.007746623,0.026695038,0.005906429,False,False,False
analysis_outputs/submission_hiddenblock_rawgate_s_all_s0.7_5ccfb1c6.csv,hiddenblock_seqmotif,0.000570019,0.536679537,0.000101194,0.162162162,9.96e-06,0.618918919,0.400775548,Q3,0.012473381,0.009003392,0.024789422,0.007655433,False,False,False
analysis_outputs/submission_public6entropy_raw05_noq2_g030_1fcb614c.csv,public6entropy,0.00055498,0.532818533,0.000101217,0.143243243,1.4599e-05,0.383783784,0.400740755,Q3,0.010977283,0.009402061,0.024854118,0.007264884,False,False,False
analysis_outputs/submission_public6entropy_raw05_ctx_g030_adcc5520.csv,public6entropy,0.000552932,0.555984556,0.000104834,0.164864865,8.22e-06,0.72972973,0.432818418,Q3,0.012473381,0.011334681,0.023413405,0.007858149,False,False,False
analysis_outputs/submission_public_repair_rawaxis_s1.125_45affdb6.csv,axis_repair,0.000573462,0.833976834,0.000105167,0.118918919,3.0014e-05,0.281081081,0.371502406,Q3,0.011679688,0.009778137,0.027888761,0.00825137,False,False,False
analysis_outputs/submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,public6entropy,0.000550609,0.517374517,0.000115734,0.113513514,2.9164e-05,0.283783784,0.389629406,Q3,0.010977283,0.009402061,0.026513129,0.007472062,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_c0fc8aea.csv,cvjepa,0.00055916,0.501930502,0.000121881,0.213513514,2.911e-06,0.832432432,0.394145339,S4,0.012402334,0.012467397,0.019390254,0.009013981,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_e06a4da9.csv,cvjepa,0.000545377,0.613899614,0.000122255,0.167567568,-2.48e-07,0.905405405,0.39627831,Q3,0.011971113,0.011403132,0.022830915,0.008426345,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_d865222a.csv,cvjepa,0.00054537,0.613899614,0.000122281,0.17027027,-2.92e-07,0.908108108,0.395942485,Q3,0.011948067,0.011403132,0.02279013,0.008425177,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_7da3c5e5.csv,cvjepa,0.000545836,0.598455598,0.000123051,0.167567568,5.18e-07,0.875675676,0.395074735,Q3,0.01200184,0.011387783,0.02276076,0.008457577,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_a99b6518.csv,cvjepa,0.000546009,0.586872587,0.000123214,0.162162162,1.086e-06,0.802702703,0.393407838,Q3,0.011859942,0.011366993,0.023016627,0.008434336,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_5ba5a755.csv,cvjepa,0.000546059,0.586872587,0.000123258,0.162162162,1.124e-06,0.805405405,0.393653029,Q3,0.011888832,0.011366993,0.023027942,0.008439566,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_4f89f1f1.csv,cvjepa,0.000546242,0.55984556,0.000123837,0.156756757,2.1e-06,0.632432432,0.394425116,Q3,0.01211653,0.011272215,0.0234873,0.008471188,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_13a17ee7.csv,cvjepa,0.000546283,0.55984556,0.000123929,0.156756757,2.413e-06,0.637837838,0.3937786,Q3,0.012078764,0.011272215,0.023342401,0.008471395,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_10c411e1.csv,cvjepa,0.000545347,0.586872587,0.00012404,0.156756757,1.625e-06,0.643243243,0.394207422,Q3,0.012072524,0.01123516,0.023523353,0.00844649,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ef1ffdcf.csv,cvjepa,0.000548761,0.55984556,0.00012406,0.167567568,5.08e-07,0.872972973,0.398620592,Q3,0.012473381,0.011334681,0.02274044,0.008532303,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_87cd58a0.csv,cvjepa,0.000554016,0.513513514,0.000124287,0.175675676,7.147e-06,0.705405405,0.387889108,Q3,0.012473381,0.011334681,0.02151278,0.008768361,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_fda4cee4.csv,cvjepa,0.000545313,0.583011583,0.000124289,0.154054054,1.429e-06,0.645945946,0.394708656,Q3,0.01210405,0.01123516,0.023650138,0.008447174,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_3e7ce30f.csv,cvjepa,0.000549264,0.552123552,0.000124489,0.167567568,9.34e-07,0.854054054,0.398124837,Q3,0.012473381,0.011334681,0.022725667,0.008542928,False,False,False
analysis_outputs/submission_raw05_jepa_public6q3s4corr_raw05_prob_bad_raw_ord_ortho_top60_strength_g065_67c662ca.csv,raw05_jepa,0.000546476,0.575289575,0.000124808,0.124324324,1.7168e-05,0.218918919,0.370002106,Q3,0.011681219,0.009407826,0.025629356,0.008142442,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9cbdda72.csv,cvjepa,0.000554682,0.513513514,0.000125406,0.224324324,2.017e-06,0.854054054,0.401891307,S4,0.012402334,0.012467397,0.020063021,0.008840248,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_8b2f4c54.csv,cvjepa,0.000554696,0.513513514,0.000125568,0.224324324,1.725e-06,0.87027027,0.40298615,Q3,0.01247338,0.012467397,0.020159421,0.008841416,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ae5e7cb0.csv,cvjepa,0.000546449,0.552123552,0.000125642,0.164864865,7.45e-07,0.859459459,0.401077383,Q3,0.012473381,0.011648316,0.023415556,0.00859175,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_619416a4.csv,cvjepa,0.000547199,0.548262548,0.000125671,0.164864865,1.963e-06,0.797297297,0.399914798,Q3,0.012473381,0.011725411,0.023232555,0.008644267,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_9e024d5b.csv,cvjepa,0.00055299,0.521235521,0.000125757,0.197297297,1.901e-06,0.851351351,0.399165842,Q3,0.012211025,0.012165813,0.02053572,0.008724207,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_cb6e0af2.csv,cvjepa,0.000553003,0.517374517,0.000125869,0.2,1.578e-06,0.864864865,0.400139391,Q3,0.012273751,0.012165813,0.02062248,0.008725375,False,False,False
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,0.000550424,0.55984556,0.000125909,0.235135135,-6.27e-07,0.910810811,0.42083798,Q3,0.014757278,0.011334681,0.019112651,0.008857144,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_e7e973d3.csv,cvjepa,0.000547599,0.521235521,0.000126381,0.154054054,3.265e-06,0.72972973,0.397950573,Q3,0.012473381,0.011632272,0.023628527,0.008653499,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_916734bd.csv,cvjepa,0.00054607,0.540540541,0.000127727,0.154054054,6.149e-06,0.524324324,0.391855844,Q3,0.012473381,0.011334681,0.023109828,0.008679599,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_0dd10fa8.csv,cvjepa,0.000546191,0.540540541,0.000127766,0.154054054,6.437e-06,0.502702703,0.391450786,Q3,0.012473381,0.011334681,0.02312283,0.008688581,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ba2783d3.csv,cvjepa,0.000552962,0.505791506,0.000127917,0.175675676,6.198e-06,0.72972973,0.395382801,Q3,0.012473381,0.011712343,0.021823508,0.008738629,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ff9a333c.csv,cvjepa,0.000552976,0.505791506,0.000127951,0.175675676,6.191e-06,0.754054054,0.395206837,Q3,0.012473381,0.011712343,0.021791605,0.00874252,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_ba58605c.csv,cvjepa,0.000546917,0.521235521,0.00012796,0.140540541,9.117e-06,0.324324324,0.389741076,Q3,0.012473381,0.011334681,0.024004306,0.008726696,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_12e31828.csv,cvjepa,0.000545335,0.548262548,0.000127967,0.156756757,4.623e-06,0.581081081,0.393872435,Q3,0.012473381,0.011334681,0.023277846,0.008635161,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_a9f915d2.csv,cvjepa,0.000545444,0.548262548,0.000127994,0.156756757,4.934e-06,0.548648649,0.393517307,Q3,0.012473381,0.011334681,0.023289548,0.008642953,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_323e8b88.csv,cvjepa,0.000546987,0.521235521,0.000128012,0.143243243,9.203e-06,0.324324324,0.38963542,Q3,0.012473381,0.011334681,0.023966457,0.008729062,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_b0ba9eec.csv,cvjepa,0.00055295,0.505791506,0.000128111,0.172972973,6.107e-06,0.7,0.394915167,Q3,0.012473381,0.011712343,0.02179632,0.008748977,False,False,False
analysis_outputs/submission_raw05_cvjepa_surprise_graft_e307fc4f.csv,cvjepa,0.000547079,0.517374517,0.000128193,0.140540541,9.61e-06,0.318918919,0.389280175,Q3,0.012473381,0.011334681,0.023960632,0.008737028,False,False,False


## Q3/S4-Shaped Candidates

source_path,candidate_family,selector_p90_delta_vs_a2c8_public,beats_a2c8_scenario_rate,pair_delta_vs_a2c8_p90,pair_beats_a2c8_rate,pair_delta_vs_raw05_p90,pair_beats_raw05_rate,q3s4_move_share,dominant_target,move_abs_a2c8_Q3,move_abs_a2c8_S4,bad_axis_abs_load,mean_abs_move_vs_a2c8,pair_probe_gate,pair_control_better_than_a2c8_gate,pair_selector_conflict


## Two-Selector Agreement Candidates

_None._

## Interpretation

- The existing old-positive universe does not contain an independent S4/Q3 positive anchor. Old-majority candidates are stage2-like broad moves, while Q3/S4-shaped candidates are not old-majority and do not clear pairwise p90.
- This supports the E15/E16 reading: S4/Q3 label-flow is a real semantic direction but underidentified by current public anchors.
