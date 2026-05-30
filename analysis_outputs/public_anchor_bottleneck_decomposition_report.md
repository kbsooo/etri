# Public Anchor Bottleneck Decomposition

This audit puts all known public anchors, including `a2c8`, into one submission-geometry frame.
It is a bottleneck diagnostic: small proxy differences are treated as unresolved unless they exceed the leave-one-anchor error floor.

## Known Public Anchors

```csv
file,public_lb,known_source,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,bad_axis_abs_load,good_span_residual_ratio,raw05_a2c8_compat_energy
submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv,0.576158949,public_probe_observations,0.044347121,0.047480309,0.199560265,0.655112441,0.07254633
submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv,0.576280568,public_probe_observations,0.044309456,0.047413947,0.200438115,0.654087854,0.072469707
submission_e95_hardtail_541e3973.csv,0.57629133,public_probe_observations,0.041131552,0.044481036,0.187186774,0.630993991,0.06799482
submission_e101_q2s3tail_177569bc.csv,0.576300366,public_probe_observations,0.041124157,0.044479046,0.18830066,0.628823794,0.067985249
submission_mixmin_0c916bb4.csv,0.57630664,public_probe_observations,0.0456142,0.049029823,0.213625824,0.655709864,0.074756279
submission_e176_abl_q2_to0p75_91e49725.csv,0.576311831,public_probe_observations,0.041232784,0.04451113,0.183839549,0.630493647,0.068005135
submission_e72_topabs50_q2s3_gate_4e48cba2.csv,0.576407777,public_probe_observations,0.046728369,0.049942789,0.206975068,0.652437649,0.07592672
submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv,0.577286509,public_probe_observations,0.050557358,0.053453016,0.183653398,0.724922622,0.081152118
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,manual_extra,0.0,0.008530873,0.036905767,1e-09,0.00908446
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,public_probe_observations,0.008530873,0.0,0.02479001,1e-09,0.003357656
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,public_probe_observations,0.044009635,0.039291379,0.0,0.0,0.054694751
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.578303365,public_probe_observations,0.128555445,0.129664865,0.551693149,0.9418532,0.1923532
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.578427353,public_probe_observations,0.175679488,0.1799807,0.468006593,0.781544763,0.256304068
submission_jepa_latent_q2_w0p45.csv,0.579801286,public_probe_observations,0.07285159,0.06824925,1.511295353,0.999954031,0.126416277
submission_lejepa_targetwise_strict_best_scale0p5.csv,0.580246819,public_probe_observations,0.12747362,0.12564974,1.275870766,0.995345321,0.199357022
submission_jepa_latent_residual_probe.csv,0.581227328,public_probe_observations,0.110359077,0.107274943,1.78904652,0.995229167,0.18268861
```

## LOOCV Public Proxy Resolution

```csv
model,kind,features,alpha,mae,rmse,max_abs_error,bias,pairwise_rank_accuracy,p80_abs_error,p90_abs_error
raw05_a2c8_compat,fixed_loocv,"mean_abs_move_vs_raw05,mean_abs_move_vs_a2c8,good_span_residual_ratio,bad_axis_abs_load",1.0,0.00045741,0.000507695,0.001017443,2.1648e-05,0.833333333,0.00054451,0.000714876
good_bad_axes,fixed_loocv,"proj_a2c8,proj_raw05,bad_axis_abs_load,proj_ordinal,mean_abs_move_vs_raw05",1.0,0.000773761,0.000987794,0.002592859,-9.2775e-05,0.55,0.001037672,0.001423395
target_move_core,fixed_loocv,"move_abs_a2c8_Q2,move_abs_a2c8_Q3,move_abs_a2c8_S2,move_abs_a2c8_S3,move_abs_a2c8_S4",1.0,0.001220582,0.001366538,0.002980439,6.0989e-05,0.675,0.001489934,0.001944499
constant_median,baseline,,,0.001223299,0.00157365,0.003864413,-0.00027838,,0.001203965,0.002661138
bad_axes_only,fixed_loocv,"bad_axis_abs_load,bad_axis_positive_load,proj_q2_bad,proj_resid_bad,proj_lejepa_bad",1.0,0.001366868,0.002574171,0.009621987,0.000677778,0.625,0.001201859,0.001808724
compact_energy,fixed_loocv,"raw05_a2c8_compat_energy,bad_to_good_load_ratio,mean_abs_move_vs_stage2",1.0,0.004248305,0.013017953,0.0518432,0.003198592,0.708333333,0.001660318,0.002300009
```

## Direct Hidden-Label Inverse Check

- LOO train-best MAE: `0.000598722`.
- LOO oracle-best MAE: `0.000362682`.
- L2O train-best MAE: `0.000532341`.
- L2O oracle-best MAE: `0.000344458`.

The gap between train-selected and oracle-selected inverse solutions means the inverse has enough degrees of freedom to fit anchors, but the selector is not yet identifying the true public subset.

## Candidate Proxy Scores

```csv
file,proxy_pred_mean,proxy_delta_vs_a2c8_public,proxy_pred_spread,edge_to_proxy_mae,below_proxy_resolution,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,bad_axis_abs_load,good_span_residual_ratio,candidate_risk_score
submission_directlbl_1422ff77.csv,0.576428087,0.000269138,0.000217456,-0.58839479,True,0.016910787,0.022947964,0.100449811,0.540236959,0.576567506
submission_directlbl_6ecccf9f.csv,0.576441454,0.000282505,0.000172783,-0.617618016,True,0.022053317,0.027197476,0.115651848,0.570609571,0.576570707
submission_directlbl_05afa7e8.csv,0.576429477,0.000270528,0.00019881,-0.59143332,True,0.023164582,0.028308741,0.12487153,0.598999716,0.576571955
submission_directlbl_5361ec9d.csv,0.576453614,0.000294664,0.00023422,-0.644201114,True,0.017939267,0.023884274,0.095122836,0.527027365,0.576596777
submission_directlbl_2050bd8b.csv,0.576443445,0.000284496,0.00027204,-0.621971025,True,0.018609025,0.024554032,0.098433338,0.550186622,0.576602361
submission_directlbl_39a60f04.csv,0.576474473,0.000315523,0.000222394,-0.689803448,True,0.017518988,0.023461523,0.093310289,0.507308893,0.576611557
submission_directlbl_aef78c3e.csv,0.576462091,0.000303141,0.000272228,-0.662734094,True,0.018234246,0.024176782,0.095725421,0.534246882,0.576619255
submission_directlbl_3a9efdf5.csv,0.576527187,0.000368237,0.000135693,-0.805048065,True,0.016706844,0.021994234,0.098977044,0.463884874,0.576631585
submission_directlbl_b7ea3059.csv,0.576511483,0.000352534,0.000251299,-0.770716832,True,0.017381674,0.023615465,0.113062506,0.525076442,0.576664056
submission_directlbl_80d51a1d.csv,0.576507081,0.000348132,0.000281704,-0.761092962,True,0.017180159,0.023209016,0.096447948,0.512362577,0.576665956
submission_directlbl_308b72b7.csv,0.576496129,0.00033718,0.000303969,-0.737150221,True,0.017885029,0.023913886,0.104590718,0.538080281,0.576666483
submission_directlbl_e8e6de2e.csv,0.576492979,0.000334029,0.000314791,-0.730261938,True,0.01825934,0.024273359,0.108458702,0.546286149,0.57666855
submission_directlbl_8dfdd4ca.csv,0.576505184,0.000346235,0.000297981,-0.756946439,True,0.017547591,0.02356161,0.100929503,0.521247111,0.576671363
submission_directlbl_18212cf0.csv,0.576523886,0.000364936,0.000241343,-0.79783193,True,0.016996196,0.023217152,0.11104739,0.510655439,0.576671418
submission_directlbl_900c4d37.csv,0.576519942,0.000360993,0.000272599,-0.789210232,True,0.016829445,0.022836262,0.094397541,0.497246781,0.576674011
submission_directlbl_37c28fdd.csv,0.576508339,0.000349389,0.000301481,-0.763842669,True,0.017555862,0.023562679,0.102482301,0.525130641,0.576676364
submission_directlbl_89fbdeb6.csv,0.576514969,0.000356019,0.000368849,-0.778336844,True,0.024990054,0.030090581,0.132512922,0.604721054,0.576718946
submission_directlbl_8b33d6dd.csv,0.576526197,0.000367247,0.000358871,-0.802884056,True,0.023878789,0.028979315,0.12329324,0.577296389,0.576722644
submission_public6entropy_raw05_q3s4_g250_b19cb905.csv,0.576615996,0.000457047,0.000248048,-0.999206017,True,0.009562509,0.006414384,0.043636614,0.234681833,0.576730315
submission_jepa_public_minimax_bridge_575ce5a9.csv,0.576682972,0.000524022,0.000580138,-1.145629041,False,0.003229988,0.007484698,0.031945485,0.072143576,0.576898181
```

## Known Control Predictions

```csv
file,known_public_lb,proxy_pred_mean,proxy_delta_vs_a2c8_public,proxy_pred_spread,below_proxy_resolution,candidate_risk_score
submission_mixmin_0c916bb4.csv,0.57630664,0.576797458,0.000638509,0.000461555,False,0.577054185
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,0.576703754,0.000544805,0.000777298,False,0.57698319
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,0.576782107,0.000623158,0.000722429,False,0.577039915
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,0.577548016,0.001389067,0.001710294,False,0.578146619
```

## Bottleneck Read

- Current best public anchor is `submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv` at `0.576158949`.
- Best fixed LOOCV proxy is `raw05_a2c8_compat` with MAE `0.000457410` and p90 error `0.000714876`.
- Raw05 vs a2c8 public gap is `0.000086986`, only `0.190x` of the best LOOCV MAE.
- Candidates outside that MAE band relative to the current best: `194` / `213`.
- Resolved-better candidates versus the current best: `0`. Resolved-worse candidates: `194`.
- After adding mixmin and E72, this proxy should be treated as a selector-collapse diagnostic: it ranks many candidates as resolved-worse while also failing to explain the known mixmin/E72 frontier distinction.
- Therefore the candidate scores in this report are useful as geometry descriptors, not as a reliable post-mixmin submission order.
- The bad JEPA anchors are geometrically separable, but raw05/a2c8-compatible gates shrink movement so much that the candidate set becomes locally unresolved.
- Therefore the immediate bottleneck is not lack of more micro-features. It is missing a stable selector for the hidden public subset or a representation that moves off the raw05/a2c8 manifold without loading the bad JEPA axes.

## Critical Caveat

This audit does not prove the true competition public subset. It proves that the current 16-anchor proxy is too coarse to justify the present post-hoc candidate differences.
The most dangerous false assumption would be treating this proxy resolution as ground truth: the E91 update shows that it cannot resolve the known mixmin/E72 distinction at frontier scale.

## Next High-Upside Branches

1. `Hidden-subset selector stress harness`: re-rank existing raw05/a2c8, raw+neural+episode, safe LeJEPA, and known-bad JEPA families under LOO/L2O/synthetic-mask stress. Gate: LOOCV/L2O MAE <= `0.00040`, rank accuracy > `0.90`, and a2c8 > raw05 > bad anchors.
2. `Targetwise safe multi-block LeJEPA`: split Q/S latents, use multiple semantic target blocks, and lower SIGReg toward the paper-default `0.05-0.10` range. Gate: targetwise CV stays non-positive on all targets, geometry mean <= `-0.003`, bad-axis projection < `0.05`.
3. `Output-masked raw-timeline I-JEPA`: predict encoded hidden-block latents from large context plus position tokens instead of reconstructing raw values. Gate: pilot Q2 delta < `-0.002`, Q3 delta < `-0.007`, bad-axis projection < `0.05`, and movement exceeds selector uncertainty.

Experiment order: run the selector harness first because it is cheap and determines whether the safe LeJEPA or raw-timeline branch deserves the next expensive training pass.

## Files

- `public_anchor_bottleneck_known.csv`
- `public_anchor_bottleneck_model_scores.csv`
- `public_anchor_bottleneck_candidate_scores.csv`
