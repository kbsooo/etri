# Public Anchor Bottleneck Decomposition

This audit puts all known public anchors, including `a2c8`, into one submission-geometry frame.
It is a bottleneck diagnostic: small proxy differences are treated as unresolved unless they exceed the leave-one-anchor error floor.

## Known Public Anchors

```csv
file,public_lb,known_source,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,bad_axis_abs_load,good_span_residual_ratio,raw05_a2c8_compat_energy
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
raw05_a2c8_compat,fixed_loocv,"mean_abs_move_vs_raw05,mean_abs_move_vs_a2c8,good_span_residual_ratio,bad_axis_abs_load",1.0,0.000546739,0.0005986,0.000982989,5.9129e-05,0.821428571,0.000701657,0.000807504
good_bad_axes,fixed_loocv,"proj_a2c8,proj_raw05,bad_axis_abs_load,proj_ordinal,mean_abs_move_vs_raw05",1.0,0.000553668,0.000648271,0.000909767,1.3115e-05,0.785714286,0.000849538,0.000892916
bad_axes_only,fixed_loocv,"bad_axis_abs_load,bad_axis_positive_load,proj_q2_bad,proj_resid_bad,proj_lejepa_bad",1.0,0.000891613,0.001403594,0.003635547,0.000472702,0.785714286,0.001013229,0.001808372
constant_median,baseline,,,0.001061102,0.001393674,0.002861969,-0.000499235,,0.001703247,0.002175613
target_move_core,fixed_loocv,"move_abs_a2c8_Q2,move_abs_a2c8_Q3,move_abs_a2c8_S2,move_abs_a2c8_S3,move_abs_a2c8_S4",1.0,0.001100864,0.001399704,0.002348947,0.000264022,0.714285714,0.002113232,0.002243221
compact_energy,fixed_loocv,"raw05_a2c8_compat_energy,bad_to_good_load_ratio,mean_abs_move_vs_stage2",1.0,0.006145059,0.014432517,0.040647107,0.005229387,0.678571429,0.002300893,0.01390189
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
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577620519,0.000181198,0.000247816,-0.331415433,True,0.008530873,0.0,0.02479001,1e-09,0.577712212
submission_raw05_jepa_axisbridge_9d6e707c.csv,0.57761621,0.000176889,0.000285613,-0.323534489,True,0.001025472,0.007816951,0.034284298,0.026367457,0.577725141
submission_raw05_jepa_axisbridge_0edfd32b.csv,0.577616225,0.000176904,0.000285609,-0.323562007,True,0.001026402,0.007813249,0.034289949,0.026358856,0.577725155
submission_raw05_jepa_axisbridge_705367e9.csv,0.577616114,0.000176793,0.000285911,-0.323358517,True,0.001058844,0.00777545,0.034200827,0.02676342,0.577725164
submission_raw05_jepa_axisbridge_f411b287.csv,0.577616281,0.00017696,0.000285619,-0.323663755,True,0.001022781,0.007819716,0.034332474,0.026349284,0.577725222
submission_raw05_jepa_axisbridge_04a3de62.csv,0.577616377,0.000177056,0.000285684,-0.323840584,True,0.001039753,0.007801262,0.034377325,0.026646372,0.577725374
submission_raw05_jepa_axisrepair_47558ed9.csv,0.577617123,0.000177802,0.000284156,-0.325203954,True,0.000706366,0.008034735,0.034759411,0.024345059,0.577725477
submission_raw05_jepa_axisrepair_a3d71669.csv,0.577617126,0.000177805,0.000284157,-0.325209329,True,0.000706231,0.008034872,0.034761456,0.024344109,0.57772548
submission_raw05_jepa_axisrepair_3b2013ed.csv,0.577617133,0.000177812,0.000284153,-0.325223243,True,0.000707305,0.008032368,0.03476323,0.024341948,0.577725487
submission_raw05_jepa_axisrepair_9b44d436.csv,0.577617133,0.000177812,0.000284154,-0.325223099,True,0.000706899,0.008033161,0.034764168,0.024341865,0.577725487
submission_raw05_jepa_axisrepair_b97ea70c.csv,0.577617078,0.000177757,0.0002843,-0.325121544,True,0.000719237,0.008014864,0.03472139,0.024529335,0.577725489
submission_raw05_jepa_axisrepair_8a6d4b92.csv,0.577617099,0.000177778,0.000284354,-0.325161396,True,0.000722471,0.008009495,0.034732299,0.024592076,0.577725537
submission_raw05_jepa_axisrepair_51efcb66.csv,0.577617107,0.000177786,0.000284352,-0.325175422,True,0.000723513,0.008007754,0.034735011,0.02458999,0.577725545
submission_raw05_jepa_axisrepair_74310fcf.csv,0.577617133,0.000177812,0.000284357,-0.325223098,True,0.000721164,0.008010823,0.034755423,0.024580155,0.577725576
submission_raw05_jepa_axisrepair_fe881329.csv,0.577617143,0.000177822,0.000284344,-0.325241576,True,0.00073163,0.008002322,0.034752777,0.024707703,0.577725591
submission_raw05_jepa_axisrepair_cec61011.csv,0.577617179,0.000177858,0.000284389,-0.325307005,True,0.000729982,0.008001915,0.034776952,0.024709319,0.577725647
submission_raw05_jepa_axisbridge_e34b4795.csv,0.577616553,0.000177232,0.000286056,-0.32416189,True,0.001047409,0.007752085,0.034447851,0.026334107,0.577725669
submission_raw05_jepa_axisbridge_2f6bc887.csv,0.577616557,0.000177236,0.000286057,-0.324169961,True,0.00104732,0.007751892,0.03445042,0.026331003,0.577725674
submission_raw05_jepa_axisbridge_2574f23d.csv,0.577616557,0.000177236,0.000286058,-0.324169938,True,0.001047324,0.007751927,0.034450473,0.026331424,0.577725674
submission_raw05_jepa_axisbridge_45f2ba5a.csv,0.577616559,0.000177238,0.000286059,-0.324172759,True,0.001047277,0.007751905,0.034451482,0.026331196,0.577725676
```

## Known Control Predictions

```csv
file,known_public_lb,proxy_pred_mean,proxy_delta_vs_a2c8_public,proxy_pred_spread,below_proxy_resolution,candidate_risk_score
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,0.577617808,0.000178487,0.000287584,True,0.577725843
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,0.577620519,0.000181198,0.000247816,True,0.577712212
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,0.57781848,0.000379159,0.000492359,True,0.577990806
```

## Bottleneck Read

- Current best public anchor is `submission_frontier_cvjepa_refine_a2c8d2c8.csv` at `0.577439321`.
- Best fixed LOOCV proxy is `raw05_a2c8_compat` with MAE `0.000546739` and p90 error `0.000807504`.
- Raw05 vs a2c8 public gap is `0.000086986`, only `0.159x` of the best LOOCV MAE.
- Candidates outside that MAE band: `24` / `213`.
- Resolved-better candidates versus a2c8: `0`. Resolved-worse candidates: `24`.
- Current post-hoc candidates mostly live inside the proxy error floor; their apparent edges are not strong evidence of a real LB improvement.
- The candidates that are outside the proxy error floor are on the worse side of a2c8 under this audit, not breakthrough candidates.
- The bad JEPA anchors are geometrically separable, but raw05/a2c8-compatible gates shrink movement so much that the candidate set becomes locally unresolved.
- Therefore the immediate bottleneck is not lack of more micro-features. It is missing a stable selector for the hidden public subset or a representation that moves off the raw05/a2c8 manifold without loading the bad JEPA axes.

## Critical Caveat

This audit does not prove the true competition public subset. It proves that the current 8-anchor proxy is too coarse to justify the present post-hoc candidate differences.
The most dangerous false assumption would be treating this proxy resolution as ground truth: it cannot even explain the a2c8/raw05 ordering with margin.

## Next High-Upside Branches

1. `Hidden-subset selector stress harness`: re-rank existing raw05/a2c8, raw+neural+episode, safe LeJEPA, and known-bad JEPA families under LOO/L2O/synthetic-mask stress. Gate: LOOCV/L2O MAE <= `0.00040`, rank accuracy > `0.90`, and a2c8 > raw05 > bad anchors.
2. `Targetwise safe multi-block LeJEPA`: split Q/S latents, use multiple semantic target blocks, and lower SIGReg toward the paper-default `0.05-0.10` range. Gate: targetwise CV stays non-positive on all targets, geometry mean <= `-0.003`, bad-axis projection < `0.05`.
3. `Output-masked raw-timeline I-JEPA`: predict encoded hidden-block latents from large context plus position tokens instead of reconstructing raw values. Gate: pilot Q2 delta < `-0.002`, Q3 delta < `-0.007`, bad-axis projection < `0.05`, and movement exceeds selector uncertainty.

Experiment order: run the selector harness first because it is cheap and determines whether the safe LeJEPA or raw-timeline branch deserves the next expensive training pass.

## Files

- `public_anchor_bottleneck_known.csv`
- `public_anchor_bottleneck_model_scores.csv`
- `public_anchor_bottleneck_candidate_scores.csv`
