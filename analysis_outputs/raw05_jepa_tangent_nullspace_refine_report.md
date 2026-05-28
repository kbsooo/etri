# Raw05 JEPA Tangent Nullspace Refine

Explore the local logit-residual tangent space of the raw05-compatible A-family. Probability-space steps are optionally projected away from raw/bad/ordinal public axes before converting back into logit space.

## Counts

- generated candidates: `228303`
- actual-anchor scored candidates: `2400`
- saved shortlist: `24`

## Mode Summary

```csv
source,mode,profile,n,best_actual,best_selection,best_bad_abs,best_raw
basis,centered,context_only,31,0.5778402011,0.5778402417,0.000199978,9.5e-08
basis,centered,all,23,0.5778402106,0.5778402106,0.0001998977,9.5e-08
basis,centered,target_tiny,74,0.5778402179,0.5778402357,0.0002074685,-1.443e-07
pair,centered,all,152,0.5778402269,0.5778402352,0.000147962,9.69e-08
pair,raw,all,156,0.5778402291,0.5778402386,7.30902e-05,9.67e-08
basis,centered,q1light_context,182,0.577840231,0.5778402356,7.63441e-05,-8.52e-08
pair,centered,q2s1heavy,117,0.5778402319,0.5778402434,0.0001833775,9.75e-08
basis,centered,q2s1heavy,26,0.577840234,0.577840234,0.0002015272,9.5e-08
pair,raw,q2s1heavy,137,0.5778402343,0.5778402453,0.00014082,9.74e-08
pair,centered,target_tiny,158,0.5778402368,0.5778402426,0.0001264527,9.69e-08
pair,raw,target_tiny,159,0.5778402391,0.5778402458,0.000106397,9.67e-08
pair,centered,q1light_context,159,0.5778402488,0.5778402557,0.0001314862,9.72e-08
pair,raw,q1light_context,160,0.577840252,0.5778402585,0.0001092413,9.7e-08
basis,null_prob,q1light_context,63,0.5778402564,0.5778402564,0.0002444987,9.39e-08
pair,null_prob,target_tiny,143,0.5778402571,0.5778402571,0.0002444987,9.56e-08
pair,null_prob,all,134,0.5778402574,0.5778402574,0.0002444987,9.57e-08
pair,null_prob,q1light_context,135,0.5778402578,0.5778402578,0.0002444987,9.58e-08
pair,null_prob,q2s1heavy,117,0.577840258,0.577840258,0.0002444987,9.59e-08
basis,null_prob,all,62,0.5778402585,0.5778402585,0.0002444987,9.22e-08
basis,null_prob,q2s1heavy,61,0.577840259,0.577840259,0.0002444986,9.31e-08
basis,null_prob,context_only,62,0.5778402594,0.5778402594,0.0002444987,9.21e-08
basis,null_prob,target_tiny,63,0.5778402597,0.5778402597,0.0002444987,9.32e-08
pair,null_prob,context_only,10,0.5778402602,0.5778402602,0.0002444987,9.65e-08
pair,centered,context_only,8,0.5778402698,0.5778402698,0.0002546143,9.62e-08
pair,raw,context_only,8,0.5778402715,0.5778402715,0.0002574303,9.57e-08
```

## Shortlist

```csv
file,bucket,source,base_file,direction_name,profile,mode,weight,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_base,mean_abs_move_vs_raw05,selection_score,rank_score
submission_raw05_jepa_tangentnull_fe15355a.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,q1light_context,centered,-0.2,0.5778402356,0.5768888358,9.96e-08,0.0002234229,2.43e-06,0.001498029,0.5778402356,551.14
submission_raw05_jepa_tangentnull_bb350e4f.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,q1light_context,centered,-0.12,0.5778402463,0.5768888664,9.84e-08,0.0002318532,1.458e-06,0.0014977029,0.5778402463,587.8
submission_raw05_jepa_tangentnull_26c10612.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,target_tiny,centered,-0.2,0.5778402179,0.5768887235,1.02e-07,0.0002271542,2.8284e-06,0.0014982838,0.5778408174,590.82
submission_raw05_jepa_tangentnull_dd4f38b9.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,context_only,centered,-0.2,0.5778402011,0.5768886371,1.042e-07,0.00022573,3.5472e-06,0.0014986224,0.5778414582,593.26
submission_raw05_jepa_tangentnull_2733815c.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,target_tiny,centered,-0.12,0.5778402357,0.5768887989,9.98e-08,0.000234092,1.6971e-06,0.0014978558,0.5778402357,609.8
submission_raw05_jepa_tangentnull_7c1914b8.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,context_only,centered,-0.12,0.5778402256,0.5768887471,1.011e-07,0.0002332374,2.1283e-06,0.0014980545,0.5778405607,611.72
submission_raw05_jepa_tangentnull_d1ce7517.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,context_only,centered,-0.06,0.577840244,0.5768888297,9.88e-08,0.000238868,1.0642e-06,0.0014976352,0.577840244,622.5
submission_raw05_jepa_tangentnull_9277d7bb.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,all,centered,-0.06,0.5778402443,0.5768888309,9.88e-08,0.0002388533,1.069e-06,0.0014976344,0.5778402443,622.82
submission_raw05_jepa_tangentnull_3ccc51b0.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,target_tiny,centered,-0.06,0.5778402491,0.5768888556,9.82e-08,0.0002392953,8.485e-07,0.001497536,0.5778402491,625.38
submission_raw05_jepa_tangentnull_22901e04.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,q2s1heavy,centered,-0.06,0.5778402488,0.5768888461,9.83e-08,0.0002386119,8.862e-07,0.0014975165,0.5778402488,625.66
submission_raw05_jepa_tangentnull_05d883a7.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca2_s0.0260,q1light_context,centered,-0.06,0.5778402544,0.5768888893,9.75e-08,0.000238176,7.29e-07,0.0014974594,0.5778402544,628.74
submission_raw05_jepa_tangentnull_2f4f1a04.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,context_only,centered,-0.2,0.5778402417,0.5768887895,9.57e-08,0.0002713181,2.6169e-06,0.0014973849,0.5778402417,666.38
submission_raw05_jepa_tangentnull_7eaa7f83.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q1light_context,centered,-0.2,0.577840244,0.576888789,9.53e-08,0.0002718472,2.3315e-06,0.0014973698,0.577840244,668.68
submission_raw05_jepa_tangentnull_4a47cb99.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q2s1heavy,centered,-0.2,0.5778402396,0.5768888152,9.5e-08,0.0002770064,2.6495e-06,0.0014975074,0.5778402396,669.08
submission_raw05_jepa_tangentnull_82da9b26.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,all,centered,0.05,0.5778402563,0.5768888866,9.92e-08,0.0002384434,8.658e-07,0.0014972121,0.5778402563,674.46
submission_raw05_jepa_tangentnull_e11f843d.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,target_tiny,centered,-0.2,0.577840248,0.5768888217,9.49e-08,0.0002685647,2.3178e-06,0.0014973565,0.577840248,675.52
submission_raw05_jepa_tangentnull_8077459e.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q1light_context,centered,-0.12,0.5778402514,0.5768888382,9.58e-08,0.0002609078,1.3989e-06,0.001497308,0.5778402514,680.0
submission_raw05_jepa_tangentnull_3e139d7b.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q2s1heavy,centered,-0.12,0.5778402487,0.576888854,9.56e-08,0.0002640034,1.5897e-06,0.0014973904,0.5778402487,680.28
submission_raw05_jepa_tangentnull_18cf015e.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,context_only,centered,-0.12,0.5778402499,0.5768888386,9.6e-08,0.0002605903,1.5701e-06,0.0014973171,0.5778402499,682.32
submission_raw05_jepa_tangentnull_97401e85.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,target_tiny,centered,-0.12,0.5778402538,0.5768888579,9.56e-08,0.0002589383,1.3907e-06,0.0014973003,0.5778402538,683.86
submission_raw05_jepa_tangentnull_afb53de7.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q2s1heavy,centered,-0.06,0.5778402556,0.5768888831,9.61e-08,0.0002542511,7.949e-07,0.0014973034,0.5778402556,694.26
submission_raw05_jepa_tangentnull_9c8407bf.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,q1light_context,centered,-0.06,0.5778402569,0.5768888752,9.62e-08,0.0002527033,6.994e-07,0.0014972623,0.5778402569,698.08
submission_raw05_jepa_tangentnull_546160b6.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,context_only,centered,-0.06,0.5778402562,0.5768888754,9.63e-08,0.0002525445,7.851e-07,0.0014972668,0.5778402562,698.48
submission_raw05_jepa_tangentnull_3f408511.csv,tangent_rank_fallback,basis,submission_raw05_jepa_efgate_ac60a2e6.csv,pca10_s0.0023,target_tiny,centered,-0.06,0.5778402581,0.5768888851,9.61e-08,0.0002517185,6.954e-07,0.0014972584,0.5778402581,708.84
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_tangentnull_fe15355a.csv,250,True,0,0,0.0631496633,0.9798124902
submission_raw05_jepa_tangentnull_bb350e4f.csv,250,True,0,0,0.0631490609,0.9798124829
submission_raw05_jepa_tangentnull_26c10612.csv,250,True,0,0,0.0631507391,0.9798124884
submission_raw05_jepa_tangentnull_dd4f38b9.csv,250,True,0,0,0.0631517432,0.9798124902
submission_raw05_jepa_tangentnull_2733815c.csv,250,True,0,0,0.0631497064,0.9798124818
submission_raw05_jepa_tangentnull_7c1914b8.csv,250,True,0,0,0.0631503088,0.9798124829
submission_raw05_jepa_tangentnull_d1ce7517.csv,250,True,0,0,0.063149233,0.9798124775
submission_raw05_jepa_tangentnull_9277d7bb.csv,250,True,0,0,0.063149233,0.9798124775
submission_raw05_jepa_tangentnull_3ccc51b0.csv,250,True,0,0,0.0631489318,0.979812477
submission_raw05_jepa_tangentnull_22901e04.csv,250,True,0,0,0.0631489103,0.9798124787
submission_raw05_jepa_tangentnull_05d883a7.csv,250,True,0,0,0.0631486091,0.9798124775
submission_raw05_jepa_tangentnull_2f4f1a04.csv,250,True,0,0,0.0631477416,0.9798115772
submission_raw05_jepa_tangentnull_7eaa7f83.csv,250,True,0,0,0.0631479827,0.9798115772
submission_raw05_jepa_tangentnull_4a47cb99.csv,250,True,0,0,0.0631478663,0.9798113803
submission_raw05_jepa_tangentnull_82da9b26.csv,250,True,0,0,0.0631482612,0.9798126958
submission_raw05_jepa_tangentnull_e11f843d.csv,250,True,0,0,0.063147858,0.9798116667
submission_raw05_jepa_tangentnull_8077459e.csv,250,True,0,0,0.0631480525,0.9798119351
submission_raw05_jepa_tangentnull_3e139d7b.csv,250,True,0,0,0.0631479827,0.979811817
submission_raw05_jepa_tangentnull_18cf015e.csv,250,True,0,0,0.0631479079,0.9798119351
submission_raw05_jepa_tangentnull_97401e85.csv,250,True,0,0,0.0631479777,0.9798119888
submission_raw05_jepa_tangentnull_afb53de7.csv,250,True,0,0,0.06314807,0.9798121445
submission_raw05_jepa_tangentnull_9c8407bf.csv,250,True,0,0,0.0631481049,0.9798122036
submission_raw05_jepa_tangentnull_546160b6.csv,250,True,0,0,0.0631480326,0.9798122036
submission_raw05_jepa_tangentnull_3f408511.csv,250,True,0,0,0.0631480675,0.9798122305
```
