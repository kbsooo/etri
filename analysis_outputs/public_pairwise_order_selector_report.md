# Public Pairwise Order Selector

This audit trains on known public-anchor pairs directly. The prediction target is pairwise public LogLoss delta, e.g. `candidate - a2c8`, instead of absolute public LB.

## Known Public Order

```csv
file,public_lb,known_source,mean_abs_move_vs_a2c8,mean_abs_move_vs_raw05,bad_axis_abs_load
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,manual_extra,0.0,0.008530873,0.036905767
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,public_probe_observations,0.008530873,0.0,0.02479001
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,public_probe_observations,0.044009635,0.039291379,0.0
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.578303365,public_probe_observations,0.128555445,0.129664865,0.551693149
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.578427353,public_probe_observations,0.175679488,0.1799807,0.468006593
submission_jepa_latent_q2_w0p45.csv,0.579801286,public_probe_observations,0.07285159,0.06824925,1.511295353
submission_lejepa_targetwise_strict_best_scale0p5.csv,0.580246819,public_probe_observations,0.12747362,0.12564974,1.275870766
submission_jepa_latent_residual_probe.csv,0.581227328,public_probe_observations,0.110359077,0.107274943,1.78904652
```

## Pairwise Model Gate

- Candidate pool scored: `1893`.
- Pairwise models tested: `36`.
- Models preserving key order (`a2c8 < raw05`, `stage2 < bad JEPA`, `top1=a2c8`): `33`.
- Selected model scenarios used for candidates: `370`.
- Submit-gate candidates: `0`.
- Baseline-relative better-than-a2c8 candidates: `46`.
- Probe-gate candidates: `216`.

```csv
model,feature_set,alpha,order_pass,model_score,loo_mae,loo_sign_acc,l2o_mae,l2o_sign_acc,top1_is_a2c8,a2c8_beats_raw05,pred_a2c8_minus_raw05,stage2_beats_bad_anchors,known_rank_accuracy_vs_a2c8
target_moves_a0.03,target_moves,0.03,True,0.000554174,0.000218288,1.0,0.000447848,1.0,True,True,-8.271e-05,True,1.0
target_moves_a0.1,target_moves,0.1,True,0.000577264,0.000228352,1.0,0.000465216,1.0,True,True,-7.502e-05,True,1.0
target_moves_a0.3,target_moves,0.3,True,0.000653135,0.000268301,0.982142857,0.000507159,1.0,True,True,-6.0708e-05,True,1.0
micro_distance_a0.3,micro_distance,0.3,True,0.000765278,0.000390929,0.892857143,0.000444369,0.928571429,True,True,-2.4443e-05,True,0.964285714
target_moves_a1,target_moves,1.0,True,0.000812031,0.000357604,1.0,0.000596378,0.964285714,True,True,-3.846e-05,True,1.0
micro_distance_a0.1,micro_distance,0.1,True,0.000825517,0.000422153,0.892857143,0.000483057,0.928571429,True,True,-0.000112425,True,0.964285714
micro_distance_a0.03,micro_distance,0.03,True,0.000899955,0.000454315,0.892857143,0.000539425,0.928571429,True,True,-0.000200854,True,0.964285714
target_moves_a3,target_moves,3.0,True,0.001010594,0.000460969,0.964285714,0.000711405,0.964285714,True,True,-2.0482e-05,True,1.0
target_moves_a10,target_moves,10.0,True,0.001243317,0.000594433,0.946428571,0.000828273,0.928571429,True,True,-9.905e-06,True,1.0
target_means_a0.03,target_means,0.03,True,0.001737627,0.000692218,0.875,0.001304593,0.821428571,True,True,-9.4363e-05,True,1.0
target_means_a3,target_means,3.0,True,0.001746408,0.000777179,0.857142857,0.001187542,0.785714286,True,True,-0.000103928,True,1.0
target_means_a0.3,target_means,0.3,True,0.001748768,0.000734059,0.875,0.001254136,0.785714286,True,True,-0.000104958,True,1.0
target_means_a0.1,target_means,0.1,True,0.001757085,0.000717509,0.875,0.001287291,0.785714286,True,True,-0.000100879,True,1.0
target_means_a10,target_means,10.0,True,0.001759145,0.000789868,0.839285714,0.001181655,0.785714286,True,True,-0.000105008,True,0.964285714
target_means_a1,target_means,1.0,True,0.001761862,0.000771587,0.857142857,0.001215605,0.785714286,True,True,-0.000105285,True,1.0
axis_compact_a0.03,axis_compact,0.03,True,0.001834823,0.000821359,0.910714286,0.001292952,0.892857143,True,True,-5.8389e-05,True,1.0
axis_compact_a10,axis_compact,10.0,True,0.001915247,0.000850208,0.892857143,0.001346242,0.857142857,True,True,-5.7083e-05,True,0.964285714
axis_compact_a0.1,axis_compact,0.1,True,0.002026378,0.000866705,0.892857143,0.001472421,0.857142857,True,True,-5.1664e-05,True,1.0
```

## Selected Models

```csv
model,feature_set,alpha,order_pass,model_score,loo_mae,loo_sign_acc,l2o_mae,l2o_sign_acc,top1_is_a2c8,a2c8_beats_raw05,pred_a2c8_minus_raw05,stage2_beats_bad_anchors,known_rank_accuracy_vs_a2c8
target_moves_a0.03,target_moves,0.03,True,0.000554174,0.000218288,1.0,0.000447848,1.0,True,True,-8.271e-05,True,1.0
target_moves_a0.1,target_moves,0.1,True,0.000577264,0.000228352,1.0,0.000465216,1.0,True,True,-7.502e-05,True,1.0
target_moves_a0.3,target_moves,0.3,True,0.000653135,0.000268301,0.982142857,0.000507159,1.0,True,True,-6.0708e-05,True,1.0
micro_distance_a0.3,micro_distance,0.3,True,0.000765278,0.000390929,0.892857143,0.000444369,0.928571429,True,True,-2.4443e-05,True,0.964285714
target_moves_a1,target_moves,1.0,True,0.000812031,0.000357604,1.0,0.000596378,0.964285714,True,True,-3.846e-05,True,1.0
micro_distance_a0.1,micro_distance,0.1,True,0.000825517,0.000422153,0.892857143,0.000483057,0.928571429,True,True,-0.000112425,True,0.964285714
micro_distance_a0.03,micro_distance,0.03,True,0.000899955,0.000454315,0.892857143,0.000539425,0.928571429,True,True,-0.000200854,True,0.964285714
target_moves_a3,target_moves,3.0,True,0.001010594,0.000460969,0.964285714,0.000711405,0.964285714,True,True,-2.0482e-05,True,1.0
target_moves_a10,target_moves,10.0,True,0.001243317,0.000594433,0.946428571,0.000828273,0.928571429,True,True,-9.905e-06,True,1.0
target_means_a0.03,target_means,0.03,True,0.001737627,0.000692218,0.875,0.001304593,0.821428571,True,True,-9.4363e-05,True,1.0
```

## Known Controls Under Candidate Scoring

```csv
basename,known_public_lb,pair_delta_vs_a2c8_p90,pair_delta_vs_a2c8_mean,pair_beats_a2c8_rate,pair_delta_vs_raw05_p90,pair_beats_raw05_rate,bad_axis_abs_load,pair_rank_score
submission_frontier_cvjepa_refine_a2c8d2c8.csv,0.577439321,0.0,0.0,0.0,2.531e-05,0.854054054,0.036905767,0.000159226
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.577526307,0.000135356,3.8936e-05,0.145945946,0.0,0.0,0.02479001,0.000460395
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.577944976,0.000495299,0.000234375,0.132432432,0.000410617,0.227027027,0.0,0.000932236
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.578303365,0.001039856,0.000850076,0.005405405,0.001000374,0.0,0.551693149,0.001946707
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.578427353,0.001601109,0.00108666,0.002702703,0.00153667,0.0,0.468006593,0.003056204
submission_jepa_latent_q2_w0p45.csv,0.579801286,0.002713822,0.002337777,0.002702703,0.002642617,0.002702703,1.511295353,0.003979278
submission_lejepa_targetwise_strict_best_scale0p5.csv,0.580246819,0.002842532,0.002595319,0.018918919,0.002817805,0.018918919,1.275870766,0.004553255
submission_jepa_latent_residual_probe.csv,0.581227328,0.003778806,0.003372179,0.0,0.003698843,0.0,1.78904652,0.004924853
```

## Candidate Top

```csv
source_path,candidate_family,pool_source,pair_delta_vs_a2c8_p90,pair_delta_vs_a2c8_mean,pair_beats_a2c8_rate,pair_delta_vs_raw05_p90,pair_beats_raw05_rate,bad_axis_abs_load,selector_p90_delta_vs_a2c8_public,beats_a2c8_scenario_rate,localization_score,pair_control_better_than_a2c8_gate,pair_submit_gate,pair_probe_gate,pair_selector_conflict,pair_rank_score
analysis_outputs/submission_hiddenloc_bridge_8ff484be.csv,hiddenloc_bridge,hiddenloc_bridge,-1.069e-06,-1.1258e-05,0.962162162,1.6808e-05,0.867567568,0.03697127,0.000578913,0.33976834,-0.000165828,True,False,True,True,9.016e-06
analysis_outputs/submission_hiddenloc_bridge_773913a3.csv,hiddenloc_bridge,hiddenloc_bridge,-7.26e-07,-7.197e-06,0.962162162,2.209e-05,0.867567568,0.036947876,0.000579313,0.33976834,-0.000107712,True,False,True,True,9.329e-06
analysis_outputs/submission_hiddenloc_bridge_81e7b614.csv,hiddenloc_bridge,hiddenloc_bridge,-7.26e-07,-7.197e-06,0.962162162,2.209e-05,0.867567568,0.036947876,0.000579313,0.33976834,-0.000107712,True,False,True,True,9.329e-06
analysis_outputs/submission_hiddenloc_bridge_07590a56.csv,hiddenloc_bridge,hiddenloc_bridge,-6.79e-07,-6.793e-06,0.959459459,2.2741e-05,0.867567568,0.036981122,0.000579382,0.33976834,-0.000105911,True,False,True,True,9.827e-06
analysis_outputs/submission_hiddenloc_bridge_16c6e986.csv,hiddenloc_bridge,hiddenloc_bridge,-6.79e-07,-6.793e-06,0.959459459,2.2741e-05,0.867567568,0.036981122,0.000579382,0.33976834,-0.000105911,True,False,True,True,9.827e-06
analysis_outputs/submission_hiddenloc_bridge_4fc2a73c.csv,hiddenloc_bridge,hiddenloc_bridge,-1.004e-06,-1.066e-05,0.956756757,1.7349e-05,0.867567568,0.037020184,0.000579015,0.33976834,-0.000163215,True,False,True,True,9.954e-06
analysis_outputs/submission_hiddenloc_bridge_a50b04d6.csv,hiddenloc_bridge,hiddenloc_bridge,-1.114e-06,-8.827e-06,0.954054054,2.1489e-05,0.867567568,0.036741457,0.000578733,0.343629344,-0.000134106,True,False,True,True,1.0984e-05
analysis_outputs/submission_hiddenloc_bridge_6dc9bfcc.csv,hiddenloc_bridge,hiddenloc_bridge,-1.137e-06,-8.874e-06,0.954054054,2.1456e-05,0.867567568,0.036721688,0.000578702,0.343629344,-0.000134217,True,False,True,True,1.1014e-05
analysis_outputs/submission_hiddenloc_bridge_693b0ea9.csv,hiddenloc_bridge,hiddenloc_bridge,-1.562e-06,-1.1714e-05,0.956756757,1.559e-05,0.867567568,0.036058614,0.000577753,0.397683398,-0.000112218,True,False,True,True,1.2335e-05
analysis_outputs/submission_hiddenloc_bridge_b26a7e99.csv,hiddenloc_bridge,hiddenloc_bridge,-1.508e-06,-1.1129e-05,0.956756757,1.6302e-05,0.867567568,0.03608691,0.000577822,0.397683398,-0.000109277,True,False,True,True,1.2393e-05
analysis_outputs/submission_hiddenloc_bridge_705a17ba.csv,hiddenloc_bridge,hiddenloc_bridge,-1.496e-06,-9.026e-06,0.954054054,2.0201e-05,0.867567568,0.036092994,0.000577975,0.397683398,-8.9077e-05,True,False,True,True,1.3003e-05
analysis_outputs/submission_hiddenloc_bridge_76ae5309.csv,hiddenloc_bridge,hiddenloc_bridge,-1.521e-06,-9.057e-06,0.954054054,2.0176e-05,0.867567568,0.036083843,0.000577963,0.397683398,-8.9078e-05,True,False,True,True,1.3038e-05
analysis_outputs/submission_hiddenloc_bridge_0872c1f0.csv,hiddenloc_bridge,hiddenloc_bridge,-4.86e-07,-8.057e-06,0.954054054,1.9668e-05,0.867567568,0.036648568,0.00057907,0.324324324,-8.0462e-05,True,False,True,True,1.3252e-05
analysis_outputs/submission_hiddenloc_bridge_18ea6b83.csv,hiddenloc_bridge,hiddenloc_bridge,-2.53e-07,-8.739e-06,0.905405405,2.2932e-05,0.867567568,0.037158095,0.000578471,0.324324324,-0.000209488,True,False,True,True,1.3725e-05
analysis_outputs/submission_hiddenloc_bridge_f1cd60b4.csv,hiddenloc_bridge,hiddenloc_bridge,-1.89e-07,-8.737e-06,0.905405405,2.2976e-05,0.867567568,0.037191805,0.000578525,0.32046332,-0.000211746,True,False,True,True,1.3734e-05
analysis_outputs/submission_hiddenloc_bridge_4f9931b1.csv,hiddenloc_bridge,hiddenloc_bridge,-1.2e-07,-7.715e-06,0.905405405,2.3447e-05,0.867567568,0.037570844,0.000578297,0.366795367,-0.000181418,True,False,True,True,1.4861e-05
analysis_outputs/submission_hiddenloc_bridge_4dec4139.csv,hiddenloc_bridge,hiddenloc_bridge,-1.21e-07,-7.714e-06,0.905405405,2.3448e-05,0.867567568,0.03757104,0.000578297,0.366795367,-0.000181406,True,False,True,True,1.4861e-05
analysis_outputs/submission_hiddenloc_bridge_fe9e4575.csv,hiddenloc_bridge,hiddenloc_bridge,-1.5e-08,-8.256e-06,0.9,2.3124e-05,0.867567568,0.037230605,0.000578632,0.32046332,-0.000206162,True,False,True,True,1.4878e-05
analysis_outputs/submission_hiddenloc_bridge_6d34fe28.csv,hiddenloc_bridge,hiddenloc_bridge,-1.31e-07,-7.717e-06,0.905405405,2.3409e-05,0.867567568,0.037538961,0.00057828,0.370656371,-0.000179435,True,False,True,True,1.4896e-05
analysis_outputs/submission_hiddenloc_bridge_7f1cb90b.csv,hiddenloc_bridge,hiddenloc_bridge,-1.31e-07,-7.717e-06,0.905405405,2.3409e-05,0.867567568,0.037539194,0.00057828,0.370656371,-0.000179427,True,False,True,True,1.4896e-05
analysis_outputs/submission_hiddenloc_bridge_d5aca95c.csv,hiddenloc_bridge,hiddenloc_bridge,-3.39e-07,-1.2373e-05,0.910810811,2.4288e-05,0.87027027,0.038433469,0.000582898,0.324324324,-0.000241098,True,False,True,True,1.5345e-05
analysis_outputs/submission_hiddenloc_bridge_d5019ea9.csv,hiddenloc_bridge,hiddenloc_bridge,-4.5e-08,-7.508e-06,0.902702703,2.3468e-05,0.867567568,0.037535268,0.000578307,0.366795367,-0.000179395,True,False,True,True,1.543e-05
analysis_outputs/submission_hiddenloc_bridge_575a8ccc.csv,hiddenloc_bridge,hiddenloc_bridge,-4.5e-08,-7.507e-06,0.902702703,2.3468e-05,0.867567568,0.037535472,0.000578307,0.366795367,-0.000179383,True,False,True,True,1.5431e-05
analysis_outputs/submission_hiddenloc_bridge_9c578e30.csv,hiddenloc_bridge,hiddenloc_bridge,-3.34e-07,-1.2322e-05,0.910810811,2.4309e-05,0.87027027,0.038449863,0.000582871,0.324324324,-0.00023884,True,False,True,True,1.5448e-05
analysis_outputs/submission_hiddenloc_bridge_1634a672.csv,hiddenloc_bridge,hiddenloc_bridge,1.16e-07,-8.252e-06,0.894594595,2.3166e-05,0.867567568,0.037262227,0.000578683,0.32046332,-0.000208175,False,False,True,False,1.5775e-05
analysis_outputs/submission_hiddenloc_bridge_7db7c7c1.csv,hiddenloc_bridge,hiddenloc_bridge,1.46e-07,-7.168e-06,0.891891892,2.3474e-05,0.867567568,0.037455282,0.000578274,0.366795367,-0.000180183,False,False,True,False,1.6938e-05
analysis_outputs/submission_hiddenloc_bridge_b8f55494.csv,hiddenloc_bridge,hiddenloc_bridge,1.39e-07,-7.156e-06,0.891891892,2.3472e-05,0.867567568,0.037453406,0.000578281,0.366795367,-0.000179267,False,False,True,False,1.6959e-05
analysis_outputs/submission_hiddenloc_bridge_2c9c85cd.csv,hiddenloc_bridge,hiddenloc_bridge,-5.93e-07,-8.873e-06,0.935135135,2.0936e-05,0.864864865,0.036930582,0.000578897,0.366795367,-9.2277e-05,True,False,True,True,1.7545e-05
analysis_outputs/submission_hiddenloc_bridge_b6c14e5e.csv,hiddenloc_bridge,hiddenloc_bridge,-6.29e-07,-9.872e-06,0.935135135,1.905e-05,0.864864865,0.037042672,0.000578998,0.351351351,-9.7298e-05,True,False,True,True,1.7653e-05
analysis_outputs/submission_hiddenloc_bridge_120fe387.csv,hiddenloc_bridge,hiddenloc_bridge,-6.29e-07,-9.874e-06,0.935135135,1.9048e-05,0.864864865,0.037042935,0.000578998,0.351351351,-9.7305e-05,True,False,True,True,1.7654e-05
analysis_outputs/submission_hiddenloc_bridge_8ec1ff28.csv,hiddenloc_bridge,hiddenloc_bridge,8.95e-07,-1.2351e-05,0.875675676,1.6472e-05,0.864864865,0.038530906,0.000582431,0.28957529,-0.000326043,False,False,True,False,1.776e-05
analysis_outputs/submission_hiddenloc_bridge_9ad3cb71.csv,hiddenloc_bridge,hiddenloc_bridge,-5.67e-07,-9.558e-06,0.935135135,1.9672e-05,0.864864865,0.037055176,0.000579033,0.351351351,-9.5642e-05,True,False,True,True,1.7902e-05
analysis_outputs/submission_hiddenloc_bridge_43887eeb.csv,hiddenloc_bridge,hiddenloc_bridge,-5.66e-07,-9.559e-06,0.935135135,1.9669e-05,0.864864865,0.03705544,0.000579033,0.351351351,-9.5648e-05,True,False,True,True,1.7904e-05
analysis_outputs/submission_hiddenloc_bridge_7e5720ec.csv,hiddenloc_bridge,hiddenloc_bridge,-5.56e-07,-8.775e-06,0.932432432,2.1168e-05,0.864864865,0.03694556,0.000578933,0.355212355,-9.0885e-05,True,False,True,True,1.8089e-05
analysis_outputs/submission_hiddenloc_bridge_5df72bc5.csv,hiddenloc_bridge,hiddenloc_bridge,5.85e-07,-8.016e-06,0.875675676,2.3039e-05,0.867567568,0.037242847,0.000578611,0.281853282,-0.000223259,False,False,True,False,1.8213e-05
analysis_outputs/submission_hiddenloc_bridge_a6196023.csv,hiddenloc_bridge,hiddenloc_bridge,5.59e-07,-7.959e-06,0.875675676,2.3063e-05,0.867567568,0.037259242,0.00057858,0.281853282,-0.000221001,False,False,True,False,1.825e-05
analysis_outputs/submission_hiddenloc_bridge_d56d2a46.csv,hiddenloc_bridge,hiddenloc_bridge,5.53e-07,-7.679e-06,0.87027027,2.3054e-05,0.867567568,0.037185286,0.000578525,0.281853282,-0.000220109,False,False,True,False,1.9021e-05
analysis_outputs/submission_hiddenloc_bridge_45de25a8.csv,hiddenloc_bridge,hiddenloc_bridge,5.24e-07,-7.629e-06,0.87027027,2.3077e-05,0.867567568,0.037200964,0.000578498,0.281853282,-0.000218096,False,False,True,False,1.9049e-05
analysis_outputs/submission_hiddenloc_bridge_a640c387.csv,hiddenloc_bridge,hiddenloc_bridge,9.1e-07,-1.0474e-05,0.878378378,2.0698e-05,0.867567568,0.037831991,0.000580753,0.32046332,-0.000268631,False,False,True,False,1.9142e-05
analysis_outputs/submission_hiddenloc_bridge_23a5d13e.csv,hiddenloc_bridge,hiddenloc_bridge,-1.07e-07,-5.781e-06,0.910810811,2.4421e-05,0.862162162,0.037694574,0.000580072,0.231660232,-8.1354e-05,True,False,True,True,1.9442e-05
```

## Worst Known Pair Sign Errors

```csv
model,left,right,actual_delta,pred_delta,sign_ok,abs_error
micro_distance_a3,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000505655,5.041e-05,False,0.000556065
micro_distance_a1,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000505655,4.8591e-05,False,0.000554245
micro_distance_a0.03,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000418669,5.5609e-05,False,0.000474278
micro_distance_a0.1,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000418669,3.7539e-05,False,0.000456207
micro_distance_a0.3,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000418669,2.0106e-05,False,0.000438774
micro_distance_a1,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000418669,4.113e-06,False,0.000422781
axis_compact_a10,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000123988,4.0779e-05,False,0.000164766
micro_distance_a3,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,-8.6986e-05,6.5475e-05,False,0.000152461
target_means_a10,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000123988,1.6999e-05,False,0.000140987
micro_distance_a10,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,-8.6986e-05,4.9561e-05,False,0.000136547
micro_distance_a1,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,-8.6986e-05,4.4478e-05,False,0.000131464
axis_compact_a3,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000123988,2.858e-06,False,0.000126845
micro_distance_a10,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,submission_jepa_latent_residual_probe.csv,-0.002799975,-0.001829501,True,0.000970474
micro_distance_a10,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_jepa_latent_residual_probe.csv,-0.002923963,-0.00200036,True,0.000923603
micro_distance_a10,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_jepa_latent_residual_probe.csv,-0.003788007,-0.002882254,True,0.000905753
micro_distance_a10,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_jepa_latent_residual_probe.csv,-0.003701021,-0.002931815,True,0.000769205
target_moves_a10,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,submission_jepa_latent_residual_probe.csv,-0.002799975,-0.002059728,True,0.000740247
target_moves_a10,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_jepa_latent_residual_probe.csv,-0.002923963,-0.002206105,True,0.000717858
micro_distance_a10,submission_jepa_latent_q2_w0p45.csv,submission_jepa_latent_residual_probe.csv,-0.001426042,-0.000709873,True,0.000716169
target_moves_a10,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_jepa_latent_residual_probe.csv,-0.003788007,-0.003119299,True,0.000668708
micro_distance_a3,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_jepa_latent_residual_probe.csv,-0.003788007,-0.003158262,True,0.000629745
target_moves_a10,submission_jepa_latent_q2_w0p45.csv,submission_jepa_latent_residual_probe.csv,-0.001426042,-0.000799434,True,0.000626607
target_moves_a10,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,submission_jepa_latent_residual_probe.csv,-0.003701021,-0.003109394,True,0.000591626
micro_distance_a3,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,submission_jepa_latent_residual_probe.csv,-0.002799975,-0.002217731,True,0.000582244
micro_distance_a10,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000482377,-0.001042338,True,0.000559961
micro_distance_a3,submission_jepa_latent_q2_w0p45.csv,submission_jepa_latent_residual_probe.csv,-0.001426042,-0.000872357,True,0.000553685
micro_distance_a10,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,submission_lejepa_targetwise_strict_best_scale0p5.csv,-0.001819466,-0.001272224,True,0.000547243
micro_distance_a1,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_jepa_latent_q2_w0p45.csv,-0.001856311,-0.002376364,True,0.000520054
axis_compact_a10,submission_jepa_latent_q2_w0p45.csv,submission_jepa_latent_residual_probe.csv,-0.001426042,-0.000907867,True,0.000518174
micro_distance_a1,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_jepa_latent_residual_probe.csv,-0.003788007,-0.00327382,True,0.000514186
micro_distance_a10,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,-0.00035839,-0.000871479,True,0.00051309
micro_distance_a3,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000482377,-0.000990941,True,0.000508564
micro_distance_a0.3,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_jepa_latent_q2_w0p45.csv,-0.001856311,-0.002364492,True,0.000508181
micro_distance_a0.3,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000505655,-4.337e-06,True,0.000501318
micro_distance_a10,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_lejepa_targetwise_strict_best_scale0p5.csv,-0.001943454,-0.001443083,True,0.000500371
micro_distance_a10,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,-0.000505655,-1.0415e-05,True,0.00049524
micro_distance_a3,submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,submission_jepa_latent_residual_probe.csv,-0.002923963,-0.00243641,True,0.000487552
micro_distance_a10,submission_frontier_cvjepa_refine_a2c8d2c8.csv,submission_lejepa_targetwise_strict_best_scale0p5.csv,-0.002807498,-0.002324977,True,0.000482522
micro_distance_a1,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_hybrid_0p578_logit_after_subject_final9_strict.csv,-0.000482377,-0.000962868,True,0.000480491
micro_distance_a3,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,submission_jepa_latent_q2_w0p45.csv,-0.001856311,-0.002336315,True,0.000480004
```

## Read

- A trustworthy submission must beat `a2c8` and `raw05` under pairwise stress, while also staying under the old selector's p90-risk and low bad-axis load.
- If no candidate passes submit gate, the bottleneck is not file format or simple blending. It is the missing sign/localization of the hidden public correction at a scale smaller than the anchor-model error floor.
- Pairwise models are intentionally treated as a veto/gate, not as public-LB truth: only candidates that agree with old stress, bad-axis, and localization evidence are allowed through.

## Files

- `public_pairwise_order_selector_models.csv`
- `public_pairwise_order_selector_candidates.csv`
- `public_pairwise_order_selector_shortlist.csv`
- `public_pairwise_order_selector_known_pairs.csv`
