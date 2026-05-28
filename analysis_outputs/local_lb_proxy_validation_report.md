# Local Public-LB Proxy Validation

Known public submissions are used as anchors only for this validation. The posterior scenario column is not treated as an independent predictor because it is calibrated to the same known public points.

## Model Scores

```csv
model,kind,features,alpha,mae,rmse,max_abs_error,bias_mean_pred_minus_public,pairwise_rank_accuracy,spearman,kendall,notes
identity_posterior_in_sample,anchored_scenario_not_independent,posterior_expected_public_vs_anchor,,0.0,0.0,0.0,0.0,1.0,1.0,1.0,public-anchor scenario axis; included only to expose in-sample fit
identity_mean_anchor,independent_proxy,mean_actual_anchor,,0.0008190756,0.0011173364,0.0021897411,0.0003598325,0.8666666667,0.8285714286,0.7333333333,raw weighted anchor mean without fitting
identity_actual_anchor,independent_proxy,actual_anchor_score_final,,0.0010389647,0.0014328904,0.0028884379,0.0007262284,0.8666666667,0.8285714286,0.7333333333,raw actual-anchor score without fitting
loocv_ridge_abs_axes_a1,leave_one_anchor_out,"abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0003184931,0.0004029881,0.0006141185,9.31358e-05,0.9333333333,0.9428571429,0.8666666667,public label of held-out submission is not used for that prediction
loocv_ridge_anchor_abs_axes_a1,leave_one_anchor_out,"actual_anchor_score_final,abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0003588898,0.0004480914,0.0007086613,8.3334e-05,0.9333333333,0.9428571429,0.8666666667,public label of held-out submission is not used for that prediction
loocv_ridge_public_shape_a1,leave_one_anchor_out,"actual_anchor_score_final,abs_delta_vs_raw05_rawaxis,abs_bad_residual_axis_ratio,abs_ordinal_axis_ratio,prob_span",1.0,0.0004513379,0.000519643,0.0007581175,-0.0002407484,0.7333333333,0.6,0.4666666667,public label of held-out submission is not used for that prediction
loocv_ridge_signed_axes_a1,leave_one_anchor_out,"delta_vs_raw05_rawaxis,bad_residual_axis_ratio,ordinal_axis_ratio,mean_abs_move_vs_raw05",1.0,0.0005823885,0.0007040258,0.0011182262,-9.0223e-06,0.8,0.7714285714,0.6,public label of held-out submission is not used for that prediction
loocv_ridge_mean_a1,leave_one_anchor_out,mean_actual_anchor,1.0,0.0012389645,0.0015209668,0.0024952811,0.0001318059,0.6,0.4285714286,0.2,public label of held-out submission is not used for that prediction
loocv_ridge_actual_a1,leave_one_anchor_out,actual_anchor_score_final,1.0,0.0013085821,0.0015447219,0.0025931506,0.0001595107,0.6,0.4285714286,0.2,public label of held-out submission is not used for that prediction
loocv_ridge_anchor_gap_a1,leave_one_anchor_out,"actual_anchor_score_final,actual_minus_mean_anchor,mean_abs_move_vs_raw05",1.0,0.001443596,0.0016563083,0.0027313764,0.0001662522,0.3333333333,-0.4285714286,-0.3333333333,public label of held-out submission is not used for that prediction
```

## Main Read

- Best independent LOOCV MAE: `0.0003184931` from `loocv_ridge_abs_axes_a1`.
- Raw `actual_anchor_score_final` MAE against known public: `0.0010389647`.
- Posterior scenario in-sample MAE: `0.0000000000`; this is an anchored reconstruction, not a submit-before-LB validation.
- Best raw05-relative candidate in this pass: `submission_public6entropy_raw05_q3s4_g250_b19cb905.csv` at `0.5775138248`, delta `-0.0000124824` versus raw05 public `0.5775263072` using `full`.
- That relative delta is much smaller than the best independent LOOCV MAE `0.0003184931` and even the within-candidate model spread `0.0000790085`.
- Practical resolution: candidate gaps below about `0.0010389647` should be treated as indistinguishable locally.

## Known Anchor Predictions

```csv
file,known_public,actual_anchor_score_final,identity_actual_anchor_error,posterior_expected_public_vs_anchor,identity_posterior_in_sample_error,loocv_ridge_anchor_abs_axes_a1,loocv_ridge_anchor_abs_axes_a1_error
submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5775263072,0.5779059944,0.0003796872,0.5775263072,0.0,0.5781443172,0.00061801
submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,0.5779449757,0.0,0.5779449757,-0.0,0.5778041861,-0.0001407896
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5783033652,0.5799865296,0.0016831644,0.5783033652,0.0,0.5782960431,-7.3221e-06
submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5784273528,0.5813157907,0.0028884379,0.5784273528,0.0,0.5791360141,0.0007086613
submission_jepa_latent_q2_w0p45.csv,0.5798012862,0.5801455759,0.0003442897,0.5798012862,0.0,0.5796497373,-0.0001515489
submission_jepa_latent_residual_probe.csv,0.5812273278,0.5802891189,-0.0009382089,0.5812273278,0.0,0.5807003212,-0.0005270066
```

## Current Candidate LB Bands

```csv
rank,file,tier,actual_anchor_score_final,posterior_scenario_not_independent,independent_lb_proxy_mean,independent_lb_proxy_model_spread,raw05_relative_lb_proxy_mean,raw05_relative_delta_vs_raw05_public,raw05_relative_lb_proxy_model_spread,axis_only_raw05_relative_lb_proxy_mean,axis_only_raw05_relative_delta_vs_raw05_public,axis_only_raw05_relative_lb_proxy_model_spread,available_raw05_relative_lb_proxy_mean,available_raw05_relative_delta_vs_raw05_public,available_proxy_model_family,independent_lb_proxy_conservative_low,independent_lb_proxy_conservative_high,bad_residual_axis_ratio,mean_abs_move_vs_raw05
,submission_public6entropy_raw05_q3s4_g250_b19cb905.csv,,0.5777989417,0.577344942,0.5778649092,0.0003436857,0.5775138248,-1.24824e-05,7.90085e-05,0.5775362509,9.9437e-06,4.5703e-06,0.5775138248,-1.24824e-05,full,0.5772592921,0.5784705263,-0.0001795372,0.0013582534
,submission_public6entropy_raw05_q3s4_g180_15f6d69a.csv,,0.5778160474,0.5773902126,0.5778669458,0.0003648649,0.5775158615,-1.04457e-05,5.21045e-05,0.5775328546,6.5474e-06,2.7865e-06,0.5775158615,-1.04457e-05,full,0.5772613287,0.5784725629,0.0012257539,0.0009770678
,submission_public6entropy_raw05_q1q3s34_g030_7ad3f3e6.csv,,0.5778687714,0.5774590201,0.577867154,0.0004013635,0.5775160696,-1.02376e-05,1.22524e-05,0.5775208869,-5.4203e-06,1.27e-07,0.5775160696,-1.02376e-05,full,0.5772615368,0.5784727711,0.0004937317,0.0003629832
,submission_public6entropy_raw05_q3s4_g350_d2a81f0f.csv,,0.5777869982,0.5772877437,0.5778688886,0.0003025263,0.5775178043,-8.5029e-06,0.0001271999,0.5775474281,2.11209e-05,1.62981e-05,0.5775178043,-8.5029e-06,full,0.5772632715,0.5784745057,-0.0021839803,0.0019039004
,submission_raw05_jepa_public6q3s4corr_raw05_direct_logit_strength_entropy_g100_2884f233.csv,,0.5778619994,0.577465104,0.5778714137,0.0003936838,0.5775203293,-5.9779e-06,2.25606e-05,0.5775275942,1.287e-06,1.6686e-06,0.5775203293,-5.9779e-06,full,0.5772657965,0.5784770308,0.0031885374,0.0003605265
,submission_public6entropy_energyfront_q3s4_g080_ee13ca29.csv,,0.5778057359,0.5768467713,0.5778720995,0.0003328905,0.5775210152,-5.292e-06,9.0412e-05,0.5775456688,1.93616e-05,2.8253e-06,0.5775210152,-5.292e-06,full,0.5772664824,0.5784777166,-0.000795789,0.0017773505
,submission_public6entropy_energyfront_q3s4_g050_7eb44daa.csv,,0.5778168627,0.5768674802,0.5778721396,0.0003424345,0.5775210553,-5.2519e-06,7.91226e-05,0.5775432279,1.69207e-05,1.1103e-06,0.5775210553,-5.2519e-06,full,0.5772665225,0.5784777567,-0.0001761485,0.0016565342
,submission_public6entropy_energyfront_q3s4_g120_05c23935.csv,,0.5777942514,0.5768202603,0.5778724513,0.0003177216,0.577521367,-4.9402e-06,0.0001089861,0.5775492581,2.29509e-05,7.9524e-06,0.577521367,-4.9402e-06,full,0.5772668342,0.5784780684,-0.0016217493,0.0019542763
,submission_raw05_jepa_public6q3s4corr_raw05_direct_logit_strength_entropy_g080_e3327d6b.csv,,0.5778701845,0.5774768986,0.5778725309,0.0003973077,0.5775214466,-4.8606e-06,1.82913e-05,0.5775273244,1.0172e-06,1.3503e-06,0.5775214466,-4.8606e-06,full,0.5772669138,0.578478148,0.0035197751,0.000288347
,submission_public6entropy_efmicro3_q3s4_g080_3d96f587.csv,,0.577805779,0.5768460374,0.5778725439,0.0003318758,0.5775214596,-4.8476e-06,9.14929e-05,0.5775460338,1.97266e-05,4.6763e-06,0.5775214596,-4.8476e-06,full,0.5772669268,0.578478161,-0.0011533731,0.0017803789
,submission_public6entropy_compatband_q3s4_g080_a6e9cbfb.csv,,0.5778057719,0.5768450935,0.5778725704,0.0003318363,0.577521486,-4.8212e-06,9.15498e-05,0.5775460815,1.97743e-05,4.6412e-06,0.577521486,-4.8212e-06,full,0.5772669532,0.5784781875,-0.0011489891,0.0017830589
,submission_public6entropy_efmicro3_q3s4_g050_2ed29f90.csv,,0.5778168998,0.5768667507,0.5778725863,0.0003414245,0.577521502,-4.8052e-06,7.90898e-05,0.5775435947,1.72875e-05,7.488e-07,0.577521502,-4.8052e-06,full,0.5772669692,0.5784782034,-0.0005353205,0.0016595851
,submission_public6entropy_compatband_q3s4_g050_86c6de73.csv,,0.5778168938,0.5768658079,0.5778726129,0.0003413834,0.5775215286,-4.7786e-06,7.91482e-05,0.5775436426,1.73354e-05,7.143e-07,0.5775215286,-4.7786e-06,full,0.5772669958,0.57847823,-0.0005310553,0.0016622691
22.0,submission_raw05_jepa_axisbridge_1968b38c.csv,A-axisbridge-local-proxy,0.5778286793,0.5769766023,0.5778726357,0.0003519566,0.5775215513,-4.7559e-06,6.62609e-05,0.5775405391,1.42319e-05,8.087e-07,0.5775215513,-4.7559e-06,full,0.5772670185,0.5784782528,-0.0002015296,0.0015075386
,submission_raw05_jepa_axisbridge_35fe4935.csv,,0.5778287025,0.5769766221,0.5778726431,0.0003519552,0.5775215588,-4.7484e-06,6.62339e-05,0.5775405406,1.42334e-05,7.847e-07,0.5775215588,-4.7484e-06,full,0.577267026,0.5784782603,-0.0002064711,0.0015073513
,submission_raw05_jepa_axisbridge_c99ee489.csv,,0.5778287058,0.5769766279,0.577872645,0.0003519536,0.5775215606,-4.7466e-06,6.62288e-05,0.5775405415,1.42343e-05,7.783e-07,0.5775215606,-4.7466e-06,full,0.5772670279,0.5784782621,-0.0002077219,0.0015073372
,submission_raw05_jepa_axisbridge_5a189d26.csv,,0.577828706,0.5769766288,0.5778726453,0.000351953,0.577521561,-4.7462e-06,6.62283e-05,0.5775405418,1.42346e-05,7.772e-07,0.577521561,-4.7462e-06,full,0.5772670282,0.5784782624,-0.0002079345,0.0015073433
,submission_raw05_jepa_axisbridge_970e949f.csv,,0.5778287094,0.5769766342,0.5778726494,0.0003519457,0.5775215651,-4.7421e-06,6.62211e-05,0.5775405449,1.42377e-05,7.627e-07,0.5775215651,-4.7421e-06,full,0.5772670323,0.5784782666,-0.0002107979,0.0015073708
,submission_raw05_jepa_axisbridge_74a95f7b.csv,,0.5778288917,0.576976446,0.5778726969,0.0003521135,0.5775216126,-4.6946e-06,6.59559e-05,0.5775405439,1.42367e-05,6.963e-07,0.5775216126,-4.6946e-06,full,0.5772670798,0.578478314,-0.0002247227,0.0015064676
,submission_raw05_jepa_axisbridge_5bce22bc.csv,,0.5778289145,0.5769764657,0.5778727042,0.0003521119,0.5775216199,-4.6873e-06,6.59296e-05,0.5775405455,1.42383e-05,6.725e-07,0.5775216199,-4.6873e-06,full,0.5772670871,0.5784783214,-0.0002296104,0.0015062835
,submission_raw05_jepa_axisbridge_8c9a99c0.csv,,0.5778289178,0.5769764715,0.5778727061,0.0003521103,0.5775216217,-4.6855e-06,6.59245e-05,0.5775405464,1.42392e-05,6.662e-07,0.5775216217,-4.6855e-06,full,0.5772670889,0.5784783232,-0.0002308508,0.0015062692
,submission_raw05_jepa_axisbridge_9e61b879.csv,,0.577828918,0.5769764724,0.5778727064,0.0003521097,0.5775216221,-4.6851e-06,6.59241e-05,0.5775405467,1.42395e-05,6.651e-07,0.5775216221,-4.6851e-06,full,0.5772670893,0.5784783235,-0.0002310625,0.001506275
,submission_raw05_jepa_axisbridge_18aad556.csv,,0.5778289214,0.5769764777,0.5778727105,0.0003521024,0.5775216262,-4.681e-06,6.59168e-05,0.5775405497,1.42425e-05,6.507e-07,0.5775216262,-4.681e-06,full,0.5772670934,0.5784783276,-0.0002339164,0.001506302
,submission_public6entropy_efmicro5_q3s4_g080_7638608b.csv,,0.5778058821,0.5768430591,0.577872715,0.0003317072,0.5775216306,-4.6766e-06,9.17087e-05,0.5775462464,1.99392e-05,4.7658e-06,0.5775216306,-4.6766e-06,full,0.5772670979,0.5784783321,-0.0011812914,0.00178998
```
