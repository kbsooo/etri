# Public Anchor Bottleneck Decomposition

This audit puts all known public anchors, including `a2c8`, into one submission-geometry frame.
It is a bottleneck diagnostic: small proxy differences are treated as unresolved unless they exceed the leave-one-anchor error floor.

## Known Public Anchors

```csv
file,public_lb,known_source,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,bad_axis_abs_load,good_span_residual_ratio,raw05_a2c8_compat_energy
submission_mixmin_0c916bb4.csv,0.57630664,public_probe_observations,0.0456142,0.049029823,0.213625824,0.655709864,0.074756279
submission_e72_topabs50_q2s3_gate_4e48cba2.csv,0.576407777,public_probe_observations,0.046728369,0.049942789,0.206975068,0.652437649,0.07592672
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
raw05_a2c8_compat,fixed_loocv,"mean_abs_move_vs_raw05,mean_abs_move_vs_a2c8,good_span_residual_ratio,bad_axis_abs_load",1.0,0.000543412,0.000641783,0.001142722,5.691e-05,0.8,0.000827512,0.001010234
good_bad_axes,fixed_loocv,"proj_a2c8,proj_raw05,bad_axis_abs_load,proj_ordinal,mean_abs_move_vs_raw05",1.0,0.00086514,0.000971823,0.001637175,-4.9107e-05,0.733333333,0.001062504,0.001549587
constant_median,baseline,,,0.001238113,0.001554991,0.003103157,-0.000238947,,0.001878554,0.0022207
bad_axes_only,fixed_loocv,"bad_axis_abs_load,bad_axis_positive_load,proj_q2_bad,proj_resid_bad,proj_lejepa_bad",1.0,0.001303641,0.002424846,0.007348056,0.000835432,0.733333333,0.001068047,0.001787258
target_move_core,fixed_loocv,"move_abs_a2c8_Q2,move_abs_a2c8_Q3,move_abs_a2c8_S2,move_abs_a2c8_S3,move_abs_a2c8_S4",1.0,0.001329572,0.001557661,0.002836998,0.000144449,0.755555556,0.00204636,0.002188931
compact_energy,fixed_loocv,"raw05_a2c8_compat_energy,bad_to_good_load_ratio,mean_abs_move_vs_stage2",1.0,0.005762599,0.014710261,0.046314545,0.00464901,0.711111111,0.001870235,0.007048422
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
submission_directlbl_5361ec9d.csv,0.576797023,0.000490383,2.6288e-05,-0.902414344,True,0.017939267,0.023884274,0.095122836,0.527027365,0.576867411
submission_directlbl_2050bd8b.csv,0.576788648,0.000482007,5.0302e-05,-0.887001707,True,0.018609025,0.024554032,0.098433338,0.550186622,0.576869955
submission_directlbl_39a60f04.csv,0.576808739,0.000502099,7.676e-06,-0.923974612,True,0.017518988,0.023461523,0.093310289,0.507308893,0.576870673
submission_directlbl_aef78c3e.csv,0.576797805,0.000491164,4.0991e-05,-0.903851981,True,0.018234246,0.024176782,0.095725421,0.534246882,0.576874036
submission_directlbl_1422ff77.csv,0.576803354,0.000496713,7.1382e-05,-0.914064037,True,0.016910787,0.022947964,0.100449811,0.540236959,0.576891647
submission_directlbl_6ecccf9f.csv,0.57681567,0.00050903,2.7081e-05,-0.93672915,True,0.022053317,0.027197476,0.115651848,0.570609571,0.576893928
submission_directlbl_05afa7e8.csv,0.576813326,0.000506685,4.3327e-05,-0.932414647,True,0.023164582,0.028308741,0.12487153,0.598999716,0.576901385
submission_directlbl_8dfdd4ca.csv,0.576824306,0.000517666,4.3805e-05,-0.952621031,True,0.017547591,0.02356161,0.100929503,0.521247111,0.576901524
submission_directlbl_e8e6de2e.csv,0.576819937,0.000513297,6.1162e-05,-0.944580934,True,0.01825934,0.024273359,0.108458702,0.546286149,0.576906738
submission_directlbl_900c4d37.csv,0.576835056,0.000528415,3.7824e-05,-0.972402582,True,0.016829445,0.022836262,0.094397541,0.497246781,0.576906954
submission_directlbl_80d51a1d.csv,0.576829016,0.000522376,5.4306e-05,-0.961288631,True,0.017180159,0.023209016,0.096447948,0.512362577,0.576908302
submission_directlbl_8b33d6dd.csv,0.576833493,0.000526853,1.4389e-05,-0.969526843,True,0.023878789,0.028979315,0.12329324,0.577296389,0.576909371
submission_directlbl_37c28fdd.csv,0.576829167,0.000522526,5.7686e-05,-0.96156588,True,0.017555862,0.023562679,0.102482301,0.525130641,0.576911864
submission_directlbl_308b72b7.csv,0.576824185,0.000517544,7.0032e-05,-0.95239786,True,0.017885029,0.023913886,0.104590718,0.538080281,0.576912661
submission_directlbl_89fbdeb6.csv,0.576831859,0.000525218,2.9214e-05,-0.966519208,True,0.024990054,0.030090581,0.132512922,0.604721054,0.576916964
submission_directlbl_b7ea3059.csv,0.576844021,0.00053738,4.0408e-05,-0.988900568,True,0.017381674,0.023615465,0.113062506,0.525076442,0.576922782
submission_directlbl_18212cf0.csv,0.576850806,0.000544166,2.788e-05,-1.001387201,False,0.016996196,0.023217152,0.11104739,0.510655439,0.576923626
submission_directlbl_3a9efdf5.csv,0.576858201,0.00055156,2.9047e-05,-1.01499499,False,0.016706844,0.021994234,0.098977044,0.463884874,0.576925274
submission_public6entropy_raw05_q3s4_g250_b19cb905.csv,0.576964296,0.000657655,6.1422e-05,-1.210233093,False,0.009562509,0.006414384,0.043636614,0.234681833,0.577013295
submission_jepa_public_minimax_bridge_a46c5492.csv,0.577029652,0.000723012,0.000281579,-1.330504138,False,0.003180183,0.007567965,0.031056819,0.070286724,0.577140039
```

## Known Control Predictions

```csv
file,known_public_lb,proxy_pred_mean,proxy_delta_vs_a2c8_public,proxy_pred_spread,below_proxy_resolution,candidate_risk_score
submission_mixmin_0c916bb4.csv,0.57630664,0.577034251,0.00072761,0.000153896,False,0.577183296
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,0.577059228,0.000752587,0.000420979,False,0.577213952
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,0.577122329,0.000815688,0.000301293,False,0.577232739
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,0.577949618,0.001642977,0.000804916,False,0.578231338
```

## Bottleneck Read

- Current best public anchor is `submission_mixmin_0c916bb4.csv` at `0.576306641`.
- Best fixed LOOCV proxy is `raw05_a2c8_compat` with MAE `0.000543412` and p90 error `0.001010234`.
- Raw05 vs a2c8 public gap is `0.000086986`, only `0.160x` of the best LOOCV MAE.
- Candidates outside that MAE band relative to the current best: `197` / `213`.
- Resolved-better candidates versus the current best: `0`. Resolved-worse candidates: `197`.
- After adding mixmin and E72, this proxy should be treated as a selector-collapse diagnostic: it ranks many candidates as resolved-worse while also failing to explain the known mixmin/E72 frontier distinction.
- Therefore the candidate scores in this report are useful as geometry descriptors, not as a reliable post-mixmin submission order.
- The bad JEPA anchors are geometrically separable, but raw05/a2c8-compatible gates shrink movement so much that the candidate set becomes locally unresolved.
- Therefore the immediate bottleneck is not lack of more micro-features. It is missing a stable selector for the hidden public subset or a representation that moves off the raw05/a2c8 manifold without loading the bad JEPA axes.

## Critical Caveat

This audit does not prove the true competition public subset. It proves that the current 10-anchor proxy is too coarse to justify the present post-hoc candidate differences.
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
