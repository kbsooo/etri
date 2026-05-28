# Local LB Proxy Uncertainty Decomposition

This report tests how much the local public-LB proxy can really resolve from the six known public submissions.
It should be read as a submission-risk diagnostic, not as a ground-truth replacement for public LB.

## Resolution

- Best leave-one-public-anchor model: `loocv_ridge_abs_axes_a1`.
- LOOCV MAE/RMSE: `0.0003184931` / `0.0004029881`.
- Best-model absolute error p50/p80/p90/max over known anchors: `0.0003380359` / `0.0005912615` / `0.0006026900` / `0.0006141185`.
- Raw05 is over/under-predicted by the best model by `0.0006141185`.
- Candidates with raw05-relative edge below `0.05 * MAE = 0.0000159247` are below this proxy's practical resolution.
- Negative-delta candidates below that 5% resolution floor: `1067` / `1287`.
- Locally resolved candidates under the strict rule: `0`.

## Known Anchor Error Decomposition

```csv
file,known_public,actual_anchor_score_final,abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05,best_model_error,best_model_abs_error,loocv_error_abs_mean,worst_loocv_model
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5775263072,0.5779059944,0.0,0.0048441395,0.0,0.0006141185,0.0006141185,0.0007992058,loocv_ridge_anchor_gap_a1
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5784273528,0.5813157907,0.0055868627,0.0476969461,0.03485168,0.0005912615,0.0005912615,0.0014001292,loocv_ridge_mean_a1
submission_jepa_latent_residual_probe.csv,0.5812273278,0.5802891189,0.0024925752,1.0,0.0215094714,-0.0004341105,0.0004341105,0.0014012067,loocv_ridge_anchor_gap_a1
submission_jepa_latent_q2_w0p45.csv,0.5798012862,0.5801455759,0.0021365395,0.5726249631,0.0143221905,-0.0002419613,0.0002419613,0.0004819443,loocv_ridge_anchor_gap_a1
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5783033652,0.5799865296,0.0038030797,0.0035798689,0.0255997269,2.55259e-05,2.55259e-05,0.000583573,loocv_ridge_signed_axes_a1
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,0.5779449757,0.0004186685,0.0,0.0074542211,3.9808e-06,3.9808e-06,0.0002215853,loocv_ridge_anchor_gap_a1
```

## Strongest Error Correlations

```csv
model,anchor_feature,spearman_abs_error,pearson_abs_error
loocv_ridge_mean_a1,abs_bad_residual_axis_ratio,0.942857,0.526037
loocv_ridge_signed_axes_a1,abs_ordinal_axis_ratio,0.942857,0.840674
loocv_ridge_anchor_gap_a1,abs_bad_residual_axis_ratio,0.771429,0.601628
loocv_ridge_mean_a1,actual_anchor_score_final,0.771429,0.745664
loocv_ridge_mean_a1,mean_actual_anchor,0.771429,0.800633
loocv_ridge_actual_a1,abs_bad_residual_axis_ratio,0.657143,0.56232
loocv_ridge_public_shape_a1,abs_ordinal_axis_ratio,0.6,0.58792
loocv_ridge_signed_axes_a1,abs_delta_vs_raw05_rawaxis,0.6,0.754508
loocv_ridge_signed_axes_a1,mean_abs_move_vs_raw05,0.6,0.685821
loocv_ridge_actual_a1,actual_anchor_score_final,0.542857,0.696816
loocv_ridge_actual_a1,mean_actual_anchor,0.542857,0.754526
loocv_ridge_anchor_gap_a1,actual_anchor_score_final,0.542857,0.524262
loocv_ridge_anchor_gap_a1,mean_actual_anchor,0.542857,0.607616
loocv_ridge_abs_axes_a1,abs_bad_residual_axis_ratio,0.485714,0.149467
loocv_ridge_anchor_abs_axes_a1,abs_bad_residual_axis_ratio,0.485714,0.106677
loocv_ridge_signed_axes_a1,prob_span,-0.463817,-0.595351
loocv_ridge_actual_a1,abs_delta_vs_raw05_rawaxis,0.428571,0.576466
loocv_ridge_actual_a1,mean_abs_move_vs_raw05,0.428571,0.620476
```

## Focus Candidate Risk

```csv
file,rank,tier,local_uncertainty_tier,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,relative_model_improve_rate,edge_to_best_mae,edge_to_model_spread,anchor_robust_delta_p90,anchor_robust_delta_max,structural_raw05_relative_delta_vs_raw05_public,anchor_feature_zdist,submit_risk_score,local_uncertainty_flags
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,47.0,known-public-control,raw05_baseline,0.0,0.0,0.0,-0.0,-0.0,0.0,0.0,0.0,1.1649782234,0.0,raw05_baseline
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,48.0,known-public-control,anchor_tail_risk,9.99477e-05,0.0001672532,0.0,-0.3138144945,-0.5975835228,0.0001958093,0.0003654519,0.0007112111,0.9970164477,0.0004174684,model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05
submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,10.0,A-graft-local-lowbad,below_proxy_resolution,-3.9998e-06,7.04113e-05,0.6666666667,0.0125584118,0.0568057953,1.84272e-05,3.16417e-05,0.0001086579,1.1617177307,4.99812e-05,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05|strict_raw05_motif_guard
submission_raw05_jepa_lowbadcon_71601b5f.csv,11.0,A-lowbad-balanced,below_proxy_resolution,-3.9979e-06,7.03853e-05,0.6666666667,0.0125524342,0.0567997025,1.84239e-05,3.16383e-05,0.0001086848,1.1617119697,4.99816e-05,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05|strict_raw05_motif_guard
submission_raw05_jepa_lowbadcon_2240eb29.csv,12.0,A-lowbad-local-boundary,below_proxy_resolution,-4.0057e-06,7.03882e-05,0.6666666667,0.0125770319,0.0569086573,1.84177e-05,3.16266e-05,0.0001088706,1.1617243956,5.00179e-05,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05|strict_raw05_motif_guard
submission_raw05_jepa_directcon_a903806a.csv,15.0,A-directcon-motif-lock,below_proxy_resolution,-3.9811e-06,7.00567e-05,0.6666666667,0.0124997778,0.0568267429,1.82959e-05,3.14878e-05,0.0001077225,1.1617012169,4.96116e-05,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05|strict_raw05_motif_guard
submission_raw05_jepa_directcon_ff079802.csv,16.0,A-directcon-local-edge,below_proxy_resolution,-3.9933e-06,6.99881e-05,0.6666666667,0.0125380153,0.0570564051,1.81407e-05,3.13152e-05,0.0001078949,1.1618042673,4.95478e-05,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05|strict_raw05_motif_guard
submission_public6entropy_raw05_q3s4_g250_b19cb905.csv,,,below_proxy_resolution,-1.24824e-05,7.90085e-05,0.6666666667,0.0391919073,0.1579874405,1.17669e-05,2.41587e-05,0.0003706515,1.1791384307,0.0001058161,proxy_mean_below_raw05|model_sign_disagreement|below_5pct_best_mae|edge_smaller_than_model_spread|some_model_worse_than_raw05|anchor_drop_p90_positive_tail|anchor_drop_max_positive_tail|structural_proxy_worse_than_raw05
submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,,,below_proxy_resolution,-1.02376e-05,1.22524e-05,1.0,0.0321437468,0.8355544634,-4.7045e-06,-1.616e-06,0.0002804115,1.1698644075,6.29284e-05,proxy_mean_below_raw05|all_relative_models_improve|below_5pct_best_mae|edge_smaller_than_model_spread|structural_proxy_worse_than_raw05
```

## Best Raw Risk Scores

```csv
file,rank,tier,family,local_uncertainty_tier,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,relative_model_improve_rate,edge_to_best_mae,edge_to_uncertainty_load,anchor_robust_delta_max,structural_raw05_relative_delta_vs_raw05_public,anchor_feature_zdist,submit_risk_score
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,47.0,known-public-control,raw_timeline_jepa_rescue,raw05_baseline,0.0,0.0,0.0,-0.0,-0.0,0.0,0.0,1.1649782234,0.0
submission_raw05_jepa_axisbridge_45f2ba5a.csv,21.0,A-axisbridge-health-probe,raw05_jepa_axisbridge,below_proxy_resolution,-4.1823e-06,6.39525e-05,0.6666666667,0.013131631,0.0092070056,2.73552e-05,0.000111898,1.1618832301,4.77108e-05
submission_raw05_jepa_axisbridge_2f6bc887.csv,,,,below_proxy_resolution,-4.181e-06,6.39491e-05,0.6666666667,0.0131275583,0.0092040313,2.73536e-05,0.0001119147,1.1645416358,4.77159e-05
submission_raw05_jepa_axisbridge_2574f23d.csv,,,,below_proxy_resolution,-4.1808e-06,6.39488e-05,0.6666666667,0.0131266941,0.0092033824,2.73534e-05,0.0001119188,1.1645415403,4.77173e-05
submission_raw05_jepa_axisbridge_e34b4795.csv,,,,below_proxy_resolution,-4.1774e-06,6.39431e-05,0.6666666667,0.0131162294,0.0091958081,2.73504e-05,0.0001119472,1.1645405083,4.77279e-05
submission_raw05_jepa_axisbridge_4bb109a4.csv,,,,below_proxy_resolution,-4.1873e-06,6.39729e-05,0.6666666667,0.013147276,0.0092168006,2.73621e-05,0.0001119753,1.1645458232,4.77296e-05
submission_raw05_jepa_axisbridge_7217d193.csv,,,,below_proxy_resolution,-4.2162e-06,6.42231e-05,0.6666666667,0.013237819,0.0092552716,2.73738e-05,0.0001138863,1.1646067888,4.82519e-05
submission_raw05_jepa_axisrepair_1ab3a7cb.csv,,,,below_proxy_resolution,-4.2593e-06,6.76928e-05,0.6666666667,0.0133732181,0.0092915833,2.83899e-05,0.000110939,1.1652272521,4.87718e-05
submission_raw05_jepa_axisrepair_5f8a4419.csv,,,,below_proxy_resolution,-4.2288e-06,6.77142e-05,0.6666666667,0.0132775384,0.0092220381,2.85257e-05,0.0001111068,1.1651754417,4.88732e-05
submission_raw05_jepa_axisbridge_705367e9.csv,,,,below_proxy_resolution,-3.8623e-06,6.50109e-05,0.6666666667,0.0121266564,0.008460932,2.7876e-05,0.0001132736,1.1645592502,4.88791e-05
submission_raw05_jepa_axisrepair_c5b80c88.csv,,,,below_proxy_resolution,-4.3197e-06,6.75051e-05,0.6666666667,0.0135628503,0.0094181958,2.87599e-05,0.0001120214,1.1650964073,4.88835e-05
submission_raw05_jepa_axisrepair_c9a298a1.csv,,,,below_proxy_resolution,-4.1953e-06,6.78477e-05,0.6666666667,0.0131721893,0.0091483168,2.84684e-05,0.0001108569,1.1652167862,4.88872e-05
submission_raw05_jepa_axisrepair_07a92ed6.csv,,,,below_proxy_resolution,-4.2054e-06,6.7762e-05,0.6666666667,0.0132041087,0.009170663,2.85657e-05,0.0001109823,1.1651513904,4.8894e-05
submission_raw05_jepa_axisrepair_acf27bd8.csv,,,,below_proxy_resolution,-4.2024e-06,6.77557e-05,0.6666666667,0.0131947856,0.0091640097,2.85328e-05,0.0001110219,1.1651546943,4.8903e-05
submission_raw05_jepa_axisrepair_7187ae3d.csv,,,,below_proxy_resolution,-4.1991e-06,6.77738e-05,0.6666666667,0.0131841415,0.0091564864,2.85389e-05,0.0001109836,1.1651541814,4.89051e-05
submission_raw05_jepa_axislocal_20e4a625.csv,,,,below_proxy_resolution,-4.2943e-06,6.75676e-05,0.6666666667,0.0134830462,0.0093606598,2.88714e-05,0.0001120471,1.165052,4.89452e-05
submission_raw05_jepa_axislocal_29b02cca.csv,,,,below_proxy_resolution,-4.2929e-06,6.76536e-05,0.6666666667,0.0134788749,0.0093545611,2.88645e-05,0.0001121178,1.165085951,4.90036e-05
submission_raw05_jepa_axisrepair_3668fbb7.csv,,,,below_proxy_resolution,-4.1382e-06,6.78978e-05,0.6666666667,0.012993196,0.0090193957,2.85644e-05,0.0001110872,1.1651529169,4.90488e-05
submission_raw05_jepa_axislocal_d90f09cf.csv,,,,below_proxy_resolution,-4.2853e-06,6.76685e-05,0.6666666667,0.0134550086,0.009335612,2.88835e-05,0.0001122994,1.165076215,4.90661e-05
submission_raw05_jepa_axislocal_e3e6088b.csv,,,,below_proxy_resolution,-4.2793e-06,6.76636e-05,0.6666666667,0.0134359693,0.0093226823,2.88685e-05,0.0001122619,1.1650816693,4.90665e-05
submission_raw05_jepa_axislocal_fdcd8ce0.csv,,,,below_proxy_resolution,-4.2787e-06,6.76581e-05,0.6666666667,0.0134342793,0.0093214365,2.8873e-05,0.0001122848,1.1650771961,4.90702e-05
submission_raw05_jepa_axislocal_d620ff36.csv,,,,below_proxy_resolution,-4.2795e-06,6.76467e-05,0.6666666667,0.013436834,0.0093232669,2.88681e-05,0.0001123102,1.1650779217,4.90708e-05
submission_raw05_jepa_axislocal_180cac45.csv,,,,below_proxy_resolution,-4.2791e-06,6.76563e-05,0.6666666667,0.0134354448,0.0093221887,2.88723e-05,0.0001122959,1.165076944,4.90716e-05
submission_raw05_jepa_axislocal_48477499.csv,,,,below_proxy_resolution,-4.2779e-06,6.76476e-05,0.6666666667,0.0134316826,0.0093194583,2.88709e-05,0.0001123267,1.165076468,4.9078e-05
```

## Family Summary

```csv
family,n,best_submit_risk_score,best_available_delta,median_edge_to_mae,median_model_improve_rate,median_anchor_tail_max,median_structural_delta,focus_count,top_file
raw_timeline_jepa_rescue,1,0.0,0.0,0.0,0.0,0.0,0.0,1,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv
raw05_jepa_axisbridge,2,4.77108e-05,-4.7559e-06,0.0140320148,0.6666666667,2.7401e-05,0.0001804184,0,submission_raw05_jepa_axisbridge_45f2ba5a.csv
unknown,905,4.77159e-05,-5.9779e-06,0.012168534,0.6666666667,3.16725e-05,0.0001203567,0,submission_raw05_jepa_axisbridge_2f6bc887.csv
raw05_jepa_axisrepair,2,4.93141e-05,-4.0081e-06,0.012349089,0.6666666667,2.99469e-05,0.0001331524,0,submission_raw05_jepa_axisrepair_2a20d67f.csv
raw05_jepa_directcon,2,4.95478e-05,-3.9933e-06,0.0125188965,0.6666666667,3.14015e-05,0.0001078087,2,submission_raw05_jepa_directcon_ff079802.csv
raw05_jepa_anchorrobust_graft,1,4.99812e-05,-3.9998e-06,0.0125584118,0.6666666667,3.16417e-05,0.0001086579,1,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv
raw05_jepa_lowbadcon,2,4.99816e-05,-4.0057e-06,0.012564733,0.6666666667,3.16325e-05,0.0001087777,2,submission_raw05_jepa_lowbadcon_71601b5f.csv
raw05_jepa_structrefine,2,4.99957e-05,-3.9661e-06,0.0124176102,0.6666666667,3.17136e-05,0.0001088141,0,submission_raw05_jepa_structrefine_04ad10f8.csv
raw05_jepa_axistrade,2,5.02455e-05,-3.786e-06,0.0118297212,0.6666666667,3.19586e-05,0.0001098054,0,submission_raw05_jepa_axistrade_931a03a1.csv
public6entropy,95,6.07607e-05,-1.24824e-05,-0.3045967894,0.6666666667,0.0003422642,0.0001823879,2,submission_public6entropy_efmicro3_q3s4_g030_c2fe0845.csv
raw05_jepa_public6drift,160,6.42717e-05,-3.7343e-06,0.008287355,0.6666666667,3.2461e-05,0.000174675,0,submission_raw05_jepa_public6drift_efmicro3_q1_s3_follow_ones_prob_bad_raw_ortho_g01200_dae06073.csv
raw05_jepa_public6q3s4corr,1,6.467e-05,-2.6602e-06,0.0083526072,0.6666666667,3.34415e-05,0.0001650358,0,submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_top60_strength_g015_4050287e.csv
raw05_jepa_siggate,4,6.53775e-05,-3.1956e-06,0.0099514841,0.6666666667,3.25123e-05,0.0001748205,0,submission_raw05_jepa_siggate_6d681440.csv
raw05_jepa_efback,2,6.55142e-05,-3.1253e-06,0.0086498644,0.6666666667,3.29575e-05,0.0001747562,0,submission_raw05_jepa_efback_9c50051c.csv
raw05_jepa_efgate,2,6.55266e-05,-3.1062e-06,0.009022961,0.6666666667,3.28172e-05,0.000175248,0,submission_raw05_jepa_efgate_d592970e.csv
raw05_jepa_blockcountreg,1,6.56877e-05,-2.9953e-06,0.009404748,0.6666666667,3.2805e-05,0.0001748907,0,submission_raw05_jepa_blockcountreg_50b1cf4a.csv
raw05_jepa_efmicro,6,6.63024e-05,-2.5896e-06,0.0077274455,0.6666666667,3.32385e-05,0.0001728302,0,submission_raw05_jepa_efmicro_9f19106d.csv
raw05_jepa_siganchor,2,6.65208e-05,-2.5391e-06,0.0078921583,0.6666666667,3.32077e-05,0.0001730887,0,submission_raw05_jepa_siganchor_3644a42f.csv
raw05_jepa_energyfront,4,6.76296e-05,-1.927e-06,0.0057537712,0.6666666667,3.34948e-05,0.0001737825,0,submission_raw05_jepa_energyfront_ea665780.csv
jepa_bridge_ensemble,1,7.91751e-05,2.27e-06,-0.0071271759,0.5,3.70434e-05,0.0001977238,0,submission_jepa_bridge_ensemble_c42fbf1e.csv
jepa_bridge_posteriorreg,1,8.14677e-05,2.5924e-06,-0.0081395885,0.5,3.78019e-05,0.0002059139,0,submission_jepa_bridge_posteriorreg_9c5e225e.csv
jepa_public_minimax_bridge,1,8.3585e-05,3.1687e-06,-0.0099491633,0.5,3.82648e-05,0.0002163341,0,submission_jepa_public_minimax_bridge_84b71a03.csv
jepa_micro_bridge_ensemble,1,8.51497e-05,2.8317e-06,-0.0088908353,0.5,4.04181e-05,0.0002096397,0,submission_jepa_micro_bridge_ensemble_5ffa44a8.csv
jepa_block_consensus_rawcorr,1,8.5612e-05,3.2022e-06,-0.0100542491,0.5,4.31712e-05,0.0002062465,0,submission_jepa_block_consensus_rawcorr_4fd8bab2.csv
jepa_block_consensus_rawcorr_refine,1,8.66626e-05,3.1668e-06,-0.0099430044,0.5,4.26059e-05,0.0002109769,0,submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv
jepa_block_consensus_rawcorr_micro,2,8.72672e-05,3.3612e-06,-0.0105619229,0.5,4.34528e-05,0.0002113207,0,submission_jepa_block_consensus_rawcorr_micro_fea06910.csv
jepa_block_countshift,80,0.0001123239,5.4257e-06,-0.0193556479,0.5,4.00417e-05,0.0003690871,0,submission_jepa_block_countshift_a1f54938.csv
jepa_public_blockentropy,2,0.0001163864,7.0037e-06,-0.0250164109,0.5,4.20444e-05,0.0003553759,0,submission_jepa_public_blockentropy_countb2434_q3_s4_g000_770c0eed.csv
hybrid_0p567,1,0.0004174684,9.99477e-05,-0.3138144945,0.0,0.0003654519,0.0007112111,1,submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv
```

## Practical Read

- The proxy can rank coarse regimes, but it cannot prove the 1e-6 to 1e-5 differences among raw05-compatible JEPA micro-candidates.
- The e40/lowbad/direct candidates are therefore local-structure probes, not locally verified LB improvements.
- Larger negative local deltas from public6entropy-style rows are not automatically better because they carry structural/anchor-tail risk outside the JEPA guardrails.
- Submit order should keep a conservative structural candidate first, then use lowbad/direct variants as information probes only if public LB budget allows.

## Files

- `local_lb_proxy_uncertainty_known_errors.csv`
- `local_lb_proxy_uncertainty_error_correlations.csv`
- `local_lb_proxy_uncertainty_candidate_risk.csv`
- `local_lb_proxy_uncertainty_family_summary.csv`