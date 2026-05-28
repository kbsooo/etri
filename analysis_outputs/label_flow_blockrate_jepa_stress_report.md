# Label-Flow Block-Rate JEPA Stress

Question: can label-flow/block-rate JEPA be treated as a semantic hidden-world representation, or is it another local-CV shortcut?

## Falsifiable Hypothesis

H15/H03 refinement: hidden blocks live on a low-dimensional label-rate manifold. A useful JEPA target should preserve block target-rate structure, be predictable from strict context without current-row leakage, improve downstream OOF under geometry and subject-chunk stress, and avoid public pairwise bad-axis gates.

Success criteria:

- semantic target preservation: oracle rate R2 > 0.30;
- context predictability: pred rate R2 > 0 with fold-min not catastrophically negative;
- downstream stress: subject-chunk and geometry branches both show non-trivial OOF gains;
- public-risk stress: at least one candidate passes pair_submit_gate, or a probe passes without selector conflict.

## Semantic Representation Stress

- semantic configs summarized: `60`
- semantic stress-pass configs: `1`
- best oracle_rate_r2: `0.347118`
- best pred_rate_r2: `0.092778`

```csv
source,context_variant,semantic_family,semantic_k,coarse_family,coarse_k,mode,pred_rate_r2_mean,pred_rate_r2_min,oracle_rate_r2_mean,semantic_acc_mean,stress_pass
two_level_proto,past_label,label_rate,10,raw_mean,8,context_plus_true_coarse_train,0.026047387,-0.077888678,0.347118489,0.327876984,True
semantic_proto,strict_surround,hybrid_oracle,10,none,0,direct,0.092777593,0.069202498,0.003045528,0.560196687,False
semantic_proto,strict_labelonly,hybrid_oracle,10,none,0,direct,0.086573661,0.022416199,0.003045528,0.677924431,False
semantic_proto,strict_prior,label_state,10,none,0,direct,0.065291151,-0.02489686,0.225953011,0.250336439,False
semantic_proto,strict_prior,hybrid_oracle,10,none,0,direct,0.065054118,0.022774519,0.003045528,0.657375776,False
semantic_proto,strict_labelonly,mean_latent,10,none,0,direct,0.064391278,0.005166655,0.030776382,0.64384058,False
semantic_proto,strict_surround,mean_latent,6,none,0,direct,0.05991898,-0.06571907,-0.040173318,0.744125259,False
semantic_proto,strict_labelonly,label_state,8,none,0,direct,0.057869948,-0.178823671,0.188764167,0.3813147,False
semantic_proto,strict_labelonly,label_state,10,none,0,direct,0.054190321,-0.179158103,0.225953011,0.296040373,False
semantic_proto,strict_surround,mean_latent,10,none,0,direct,0.052474606,-0.056456979,0.030776382,0.664389234,False
semantic_proto,strict_labelonly,label_state,6,none,0,direct,0.046254668,-0.161459501,0.180817495,0.400828157,False
semantic_proto,strict_labelonly,mean_latent,8,none,0,direct,0.045937247,-0.138187257,0.003790678,0.679710145,False
semantic_proto,strict_prior,label_state,8,none,0,direct,0.044400998,-0.095363762,0.188764167,0.358980331,False
semantic_proto,strict_labelonly,modality_state,6,none,0,direct,0.031818839,-0.050538865,-0.025000454,0.724663561,False
semantic_proto,strict_labelonly,mean_latent,6,none,0,direct,0.030540656,-0.030668992,-0.040173318,0.73429089,False
semantic_proto,strict_surround,hybrid_raw,8,none,0,direct,0.03009377,-0.051222155,-0.072625252,0.613069358,False
semantic_proto,strict_prior,label_state,6,none,0,direct,0.028593368,-0.093431717,0.180817495,0.478338509,False
two_level_proto,past_label,label_rate,10,hybrid_raw,4,context_plus_true_coarse_train,0.022316291,-0.132632483,0.347118489,0.325793651,False
two_level_proto,full_strict,label_rate,10,raw_mean,8,coarse_prob_only,0.020993128,-0.113175279,0.347118489,0.243452381,False
two_level_proto,past_label,label_rate,10,hybrid_raw,4,context_plus_coarse_prob,0.02002757,-0.101675991,0.347118489,0.301488095,False
```

## Downstream OOF Stress

- downstream rows scanned: `15936`
- best downstream delta vs stage2: `-0.003334`
- best subject_chunk delta: `-0.000537`
- best geometry delta: `-0.003334`

```csv
source,cv_mode,method,group,strength,concentration,base_mix,scale,mean_delta,min_delta,max_delta
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.7,20.0,0.0,0.5,-0.003334217,-0.003334217,-0.003334217
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.7,8.0,0.0,0.5,-0.003286618,-0.003286618,-0.003286618
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.9,20.0,0.35,0.5,-0.00327991,-0.00327991,-0.00327991
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.9,8.0,0.35,0.5,-0.003254205,-0.003254205,-0.003254205
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.9,4.0,0.35,0.5,-0.003210187,-0.003210187,-0.003210187
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.7,4.0,0.0,0.5,-0.003196216,-0.003196216,-0.003196216
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.7,20.0,0.0,0.5,-0.003181345,-0.003181345,-0.003181345
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.5,20.0,0.0,0.5,-0.003177846,-0.003177846,-0.003177846
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.9,20.0,0.35,0.5,-0.003175185,-0.003175185,-0.003175185
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.9,8.0,0.35,0.5,-0.003149483,-0.003149483,-0.003149483
mp_count_conditioning,geometry,mpj_ridge_resid,q_only,0.9,20.0,0.35,0.5,-0.003138579,-0.003138579,-0.003138579
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.7,8.0,0.0,0.5,-0.003138188,-0.003138188,-0.003138188
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.5,8.0,0.0,0.5,-0.003130967,-0.003130967,-0.003130967
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.9,2.0,0.35,0.5,-0.00312699,-0.00312699,-0.00312699
mp_count_conditioning,geometry,mpj_ridge_resid,q_only,0.9,8.0,0.35,0.5,-0.003110686,-0.003110686,-0.003110686
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.9,4.0,0.35,0.5,-0.003104966,-0.003104966,-0.003104966
mp_count_conditioning,geometry,mpj_ridge_resid,q_only,0.9,4.0,0.35,0.5,-0.003063665,-0.003063665,-0.003063665
mp_count_conditioning,geometry,mpj_ridge_resid,q_only,0.7,20.0,0.0,0.5,-0.003062327,-0.003062327,-0.003062327
mp_count_conditioning,geometry,mpj_ridge_resid_heavy,q_only,0.7,4.0,0.0,0.5,-0.003052538,-0.003052538,-0.003052538
mp_count_conditioning,geometry,mpj_ridge_rate,q_only,0.5,4.0,0.0,0.5,-0.003041196,-0.003041196,-0.003041196
```

## Public Pairwise Candidate Stress

- candidate files scored: `556` / pool `556`
- pair_submit_gate: `0`
- pair_control_better_than_a2c8_gate: `0`
- pair_probe_gate: `0`
- best p90 delta vs a2c8: `0.000125668`

```csv
source_path,candidate_family,pool_source,pair_delta_vs_a2c8_p90,pair_delta_vs_a2c8_mean,pair_beats_a2c8_rate,pair_delta_vs_raw05_p90,pair_beats_raw05_rate,bad_axis_abs_load,pair_submit_gate,pair_probe_gate,pair_selector_conflict,pair_rank_score
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000125909,2.8275e-05,0.235135135,-6.27e-07,0.910810811,0.019112651,False,False,False,0.000425756
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p75_q3_w0p2.csv,other_jepa,mp_count_submission,0.000126078,3.0418e-05,0.210810811,7.389e-06,0.775675676,0.023227962,False,False,False,0.000429394
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p5_c20_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000125668,3.0256e-05,0.208108108,6.36e-06,0.786486486,0.022910099,False,False,False,0.000429595
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000126815,3.0836e-05,0.2,8.475e-06,0.759459459,0.023852773,False,False,False,0.000432091
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p35.csv,other_jepa,mp_count_submission,0.000130238,3.1359e-05,0.218918919,1.1013e-05,0.694594595,0.025285618,False,False,False,0.000433243
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p75_q3_w0p35.csv,other_jepa,mp_count_submission,0.00013609,3.3477e-05,0.248648649,2.4095e-05,0.572972973,0.032487413,False,False,False,0.000440836
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p5.csv,other_jepa,mp_count_submission,0.000137781,3.3513e-05,0.245945946,2.3191e-05,0.578378378,0.031458585,False,False,False,0.000442058
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p5_c20_bm0p35_sc0p5_q3_w0p35.csv,other_jepa,mp_count_submission,0.000137471,3.3449e-05,0.245945946,2.2677e-05,0.581081081,0.031931151,False,False,False,0.000442123
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0_sc0p5_q3_w0p35.csv,other_jepa,mp_count_submission,0.000136682,3.3548e-05,0.243243243,2.49e-05,0.562162162,0.033580831,False,False,False,0.000442969
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p5_c20_bm0p35_sc0p5_q3_w0p5.csv,other_jepa,mp_count_submission,0.00013984,3.2806e-05,0.278378378,3.3629e-05,0.543243243,0.040952204,False,False,False,0.000449664
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q3_w0p75.csv,other_jepa,mp_count_submission,0.000142366,3.2732e-05,0.286486486,3.6022e-05,0.543243243,0.041746863,False,False,False,0.000453005
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p75_q3_w0p5.csv,other_jepa,mp_count_submission,0.000142366,3.2732e-05,0.286486486,3.6022e-05,0.543243243,0.041746863,False,False,False,0.000453005
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0_sc0p5_q3_w0p5.csv,other_jepa,mp_count_submission,0.00014325,3.2762e-05,0.283783784,3.7172e-05,0.532432432,0.04330889,False,False,False,0.000455906
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p9_c4_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000145498,2.4603e-05,0.375675676,4.521e-05,0.613513514,0.038658665,False,False,False,0.000464005
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p9_c8_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000146601,2.4779e-05,0.375675676,4.6573e-05,0.613513514,0.038844029,False,False,False,0.00046608
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p9_c20_bm0p35_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000147409,2.4895e-05,0.381081081,4.7432e-05,0.613513514,0.03898227,False,False,False,0.000466792
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p7_c4_bm0_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000151436,1.8487e-05,0.408108108,5.5129e-05,0.627027027,0.04598858,False,False,False,0.000481656
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p7_c8_bm0_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000152354,1.8482e-05,0.408108108,5.6748e-05,0.62972973,0.046317909,False,False,False,0.000483563
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_rate_q_only_st0p7_c20_bm0_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000152861,1.8369e-05,0.410810811,5.767e-05,0.627027027,0.046570109,False,False,False,0.000484339
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p5_c20_bm0p35_sc0p5_q3_w0p75.csv,other_jepa,mp_count_submission,0.000155858,3.1521e-05,0.324324324,6.1972e-05,0.540540541,0.056653286,False,False,False,0.000486791
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q_all_w0p2.csv,other_jepa,mp_count_submission,0.000190112,8.5506e-05,0.086486486,8.587e-05,0.059459459,0.043873246,False,False,False,0.000496904
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p75_q3_w0p75.csv,other_jepa,mp_count_submission,0.000162281,3.2333e-05,0.32972973,6.8391e-05,0.543243243,0.058753266,False,False,False,0.000496959
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0_sc0p5_q3_w0p75.csv,other_jepa,mp_count_submission,0.000161172,3.266e-05,0.332432432,7.1901e-05,0.535135135,0.061404371,False,False,False,0.000498681
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_geometry_mpj_ridge_resid_heavy_q_only_st0p7_c20_bm0_sc0p5_q3_w0p2.csv,other_jepa,mp_count_submission,0.000168927,2.141e-05,0.410810811,7.3055e-05,0.6,0.055391765,False,False,False,0.000510973
jepa/submission_mp_count_public_blend_raw_rescue05_submission_mp_count_conditioning_jepa_subject_chunk_mpj_knn18_q_only_st0p35_c20_bm0p35_sc0p5_q23_w0p2.csv,q2_specific,mp_count_submission,0.000195815,7.9853e-05,0.1,8.6598e-05,0.032432432,0.036158236,False,False,False,0.000513655
```

## Decision

- label-flow semantic structure supported: `True`
- direct submit support from this branch: `False`

Interpretation: label-flow/block-rate is a real semantic representation, but current candidate translation still fails public-risk stress. Use it as latent energy/gate, not as direct probability replacement.

Next experiment: build a gate that only applies block-rate corrections on samples where semantic confidence is high, raw05 distance is low, and target-dependency violation decreases.

## Files

- `label_flow_blockrate_jepa_semantic_summary.csv`
- `label_flow_blockrate_jepa_downstream_summary.csv`
- `label_flow_blockrate_jepa_downstream_mode_best.csv`
- `label_flow_blockrate_jepa_pairwise_scored.csv`
- `label_flow_blockrate_jepa_pairwise_shortlist.csv`
