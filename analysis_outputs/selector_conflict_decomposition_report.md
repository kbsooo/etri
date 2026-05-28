# Selector Conflict Decomposition

Purpose: explain why E14 S4+Q3 label-flow candidates look good to the pairwise selector but fail independent hidden-subset survival.

Sign convention: `pred_delta_vs_a2c8 < 0` means the selector predicts the candidate is better than a2c8; positive means worse.

## Candidate-Level Predicted Deltas

candidate,selector,mean_pred_delta,median_pred_delta,p10_pred_delta,p90_pred_delta,better_rate
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,2.352e-06,4.4498e-05,-9.8557e-05,5.6647e-05,0.285714286
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,-1.62e-06,-1.948e-05,-0.000211533,0.000274323,0.5
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,-6.7e-08,7.9443e-05,-0.000171922,8.7447e-05,0.285714286
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,8.045e-06,-1.3245e-05,-0.000266109,0.000388583,0.5
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,-2.418e-06,9.0053e-05,-0.000205783,0.000102206,0.285714286
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,5.813e-06,-1.5453e-05,-0.000318392,0.000448666,0.5
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,7.21e-07,1.033e-06,-7.39e-07,1.655e-06,0.285714286
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,-3.61e-07,-5.83e-07,-1.1475e-05,8.506e-06,0.666666667
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,3.607e-06,6.267e-06,-4.637e-06,8.405e-06,0.285714286
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,-2.754e-06,-4.233e-06,-6.2138e-05,4.5273e-05,0.666666667
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,2.1e-07,8.53e-06,-2.2766e-05,1.4213e-05,0.285714286
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,2.972e-06,-4.43e-07,-3.4726e-05,5.5378e-05,0.5


## Top Contributions By Candidate

### analysis_outputs/submission_label_flow_focused_1bbfb735.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,good_span_residual_ratio,0.000258446,0.000216434,0.000258446,0.795883853,0.554899327,0.000325123
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,max_abs_move_vs_a2c8,-0.000113527,-3.5096e-05,0.000113577,0.523193724,0.429616007,-6.4925e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,rms_move_vs_a2c8,-6.9622e-05,2.0211e-05,0.000103738,0.291196092,0.034963802,-6.4925e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,move_abs_a2c8_S4,-0.000101464,-9.6813e-05,0.000101464,0.437094444,0.037507226,-0.000150195
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,mean_prob_S4,-5.3894e-05,-5.4512e-05,5.3894e-05,-0.165449448,-0.001035555,-8.3759e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,mean_abs_move_vs_a2c8,5.0882e-05,1.2008e-05,5.0882e-05,0.068291272,0.006047604,-6.4925e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,proj_raw05,3.184e-05,3.3507e-05,3.2251e-05,-0.192967114,-0.123651952,0.000230829
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,pairwise_order,proj_a2c8,2.7526e-05,3.4182e-05,2.9983e-05,-0.207920018,-0.120885566,0.000230829


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,move_abs_a2c8_S4,-0.000407372,-0.000407372,0.000407372,0.660824685,0.037507226,-0.000390429
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,good_span_residual_ratio,0.000103241,9.5752e-05,0.000103241,1.203263284,0.554899327,8.6092e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,raw05_a2c8_compat_energy,8.0104e-05,8.0104e-05,8.0104e-05,0.143276624,0.012788865,7.9527e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,proj_a2c8,7.9183e-05,7.9183e-05,7.9183e-05,-0.31434552,-0.120885566,7.8409e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,bad_axis_abs_load,-2.0954e-05,-2.4627e-05,2.0954e-05,-0.024083582,-0.016238241,6.2087e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,move_abs_a2c8_Q3,1.6943e-05,1.6943e-05,1.6943e-05,0.05250313,0.004826006,-0.000390429
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,proj_raw05,-1.3058e-05,-1.3058e-05,1.3058e-05,-0.291738854,-0.123651952,7.8409e-05
analysis_outputs/submission_label_flow_focused_1bbfb735.csv,old_hidden_subset,proj_ordinal,9.907e-06,9.907e-06,9.907e-06,-0.043091973,-0.014629944,7.8409e-05


### analysis_outputs/submission_label_flow_focused_6b9335b1.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,good_span_residual_ratio,0.000296266,0.000248105,0.000296266,0.912348151,0.636099568,0.000377572
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,max_abs_move_vs_a2c8,-0.00013546,-4.1876e-05,0.000135519,0.624271002,0.51261474,-8.02e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,rms_move_vs_a2c8,-8.3634e-05,2.4278e-05,0.000124616,0.34980246,0.042000645,-8.02e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,move_abs_a2c8_S4,-0.000121336,-0.000115774,0.000121336,0.522699789,0.04485305,-0.000179755
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,mean_prob_S4,-6.4673e-05,-6.5414e-05,6.4673e-05,-0.198539338,-0.001242667,-0.000100226
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,mean_abs_move_vs_a2c8,6.086e-05,1.4362e-05,6.086e-05,0.081682794,0.007233505,-8.02e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,proj_raw05,3.8515e-05,4.0531e-05,3.9012e-05,-0.233418917,-0.149573179,0.000268829
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,pairwise_order,proj_a2c8,3.3308e-05,4.1362e-05,3.6281e-05,-0.251592933,-0.14627718,0.000268829


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,move_abs_a2c8_S4,-0.000487156,-0.000487156,0.000487156,0.7902478,0.04485305,-0.000466859
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,good_span_residual_ratio,0.000118348,0.000109763,0.000118348,1.379340753,0.636099568,9.7523e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,proj_a2c8,9.5816e-05,9.5816e-05,9.5816e-05,-0.380372761,-0.14627718,9.5269e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,raw05_a2c8_compat_energy,9.4897e-05,9.4897e-05,9.4897e-05,0.169734817,0.015150522,9.3826e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,bad_axis_abs_load,-2.5368e-05,-2.9815e-05,2.5368e-05,-0.029156958,-0.01965894,7.1221e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,move_abs_a2c8_Q3,2.0298e-05,2.0298e-05,2.0298e-05,0.062897957,0.005781482,-0.000466859
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,proj_raw05,-1.5796e-05,-1.5796e-05,1.5796e-05,-0.352896232,-0.149573179,9.5269e-05
analysis_outputs/submission_label_flow_focused_6b9335b1.csv,old_hidden_subset,proj_ordinal,1.2133e-05,1.2133e-05,1.2133e-05,-0.05277531,-0.017917487,9.5269e-05


### analysis_outputs/submission_label_flow_combo_3d536109.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,good_span_residual_ratio,0.000193313,0.000161888,0.000193313,0.595307263,0.415055034,0.000225176
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,max_abs_move_vs_a2c8,-8.3175e-05,-2.5713e-05,8.3211e-05,0.383314085,0.314755049,-6.4712e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,rms_move_vs_a2c8,-4.9575e-05,1.4391e-05,7.3867e-05,0.207348925,0.024896305,-6.4712e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,move_abs_a2c8_S4,-5.4642e-05,-5.2137e-05,5.4642e-05,0.235390192,0.020198914,-0.000101412
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,mean_abs_move_vs_a2c8,3.4963e-05,8.251e-06,3.4963e-05,0.046925715,0.004155555,-6.4712e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,mean_prob_S4,-2.8744e-05,-2.9073e-05,2.8744e-05,-0.088239706,-0.000552296,-6.0641e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,mean_prob_Q3,-2.4046e-05,-2.4075e-05,2.4046e-05,0.063802489,0.001806863,-6.0641e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,pairwise_order,proj_raw05,2.186e-05,2.3004e-05,2.2143e-05,-0.132483061,-0.084894201,0.000153998


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,move_abs_a2c8_S4,-0.000219384,-0.000219384,0.000219384,0.355876519,0.020198914,-0.000188173
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,good_span_residual_ratio,7.7222e-05,7.1621e-05,7.7222e-05,0.900019984,0.415055034,4.9478e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,raw05_a2c8_compat_energy,5.4842e-05,5.4842e-05,5.4842e-05,0.098091171,0.008755613,5.4854e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,proj_a2c8,5.2084e-05,5.2084e-05,5.2084e-05,-0.206763992,-0.079513722,4.0163e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,move_abs_a2c8_Q3,3.1211e-05,3.1211e-05,3.1211e-05,0.096715895,0.008889974,-0.000188173
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,bad_axis_abs_load,-2.7883e-05,-3.2771e-05,2.7883e-05,-0.032047282,-0.021607727,2.9957e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,bad_axis_positive_load,-1.2115e-05,-1.2115e-05,1.2115e-05,-0.032394399,-0.022033499,-3.8814e-05
analysis_outputs/submission_label_flow_combo_3d536109.csv,old_hidden_subset,proj_lejepa_bad,-1.1093e-05,-1.1093e-05,1.1093e-05,-0.042355367,-0.013416884,-3.8814e-05


### analysis_outputs/submission_label_flow_twampl_b8c66b64.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,good_span_residual_ratio,3.6546e-05,3.0605e-05,3.6546e-05,0.112542432,0.078465871,4.4998e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,max_abs_move_vs_a2c8,-1.5739e-05,-4.866e-06,1.5746e-05,0.072533021,0.059559864,-7.458e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,move_abs_a2c8_S4,-1.3801e-05,-1.3168e-05,1.3801e-05,0.059453265,0.005101705,-1.8102e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,rms_move_vs_a2c8,-9.189e-06,2.668e-06,1.3692e-05,0.038434343,0.004614797,-7.458e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,mean_prob_S4,-7.186e-06,-7.268e-06,7.186e-06,-0.022059926,-0.000138074,-9.64e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,mean_abs_move_vs_a2c8,6.132e-06,1.447e-06,6.132e-06,0.008229987,0.000728815,-7.458e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,proj_raw05,3.89e-06,4.094e-06,3.94e-06,-0.023574913,-0.015106636,3.2321e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,pairwise_order,proj_a2c8,3.445e-06,4.278e-06,3.753e-06,-0.026022785,-0.015129756,3.2321e-05


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,move_abs_a2c8_S4,-5.541e-05,-5.541e-05,5.541e-05,0.089884887,0.005101705,-5.541e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,good_span_residual_ratio,1.4599e-05,1.354e-05,1.4599e-05,0.170148164,0.078465871,1.4056e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,proj_a2c8,9.91e-06,9.91e-06,9.91e-06,-0.039342752,-0.015129756,8.53e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,raw05_a2c8_compat_energy,6.934e-06,6.934e-06,6.934e-06,0.012401681,0.001106973,7.188e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,proj_raw05,-1.595e-06,-1.595e-06,1.595e-06,-0.035641918,-0.015106636,8.53e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,bad_axis_abs_load,-1.065e-06,-1.252e-06,1.065e-06,-0.001224573,-0.000825662,9.939e-06
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,mean_abs_move_vs_a2c8,1.027e-06,1.027e-06,1.027e-06,0.012442571,0.000728815,1.3301e-05
analysis_outputs/submission_label_flow_twampl_b8c66b64.csv,old_hidden_subset,proj_ordinal,9.23e-07,9.23e-07,9.23e-07,-0.00401558,-0.00136331,8.53e-06


### analysis_outputs/submission_label_flow_gated_ff8df011.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,good_span_residual_ratio,3.7126e-05,3.1091e-05,3.7126e-05,0.114329037,0.079711512,3.4498e-05
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,max_abs_move_vs_a2c8,-2.3475e-05,-7.257e-06,2.3486e-05,0.108187503,0.088837233,-2.6493e-05
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,rms_move_vs_a2c8,-9.253e-06,2.686e-06,1.3788e-05,0.038702292,0.004646969,-2.6493e-05
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,bad_axis_abs_load,-4.521e-06,-3.663e-06,4.521e-06,-0.004530594,-0.004618319,-2.061e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,mean_prob_Q3,-4.48e-06,-4.486e-06,4.48e-06,0.01188785,0.000336659,-3.628e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,mean_abs_move_vs_a2c8,3.115e-06,7.35e-07,3.115e-06,0.004180409,0.0003702,-2.6493e-05
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,bad_axis_positive_load,-2.548e-06,-2.387e-06,2.548e-06,-0.00449117,-0.004618319,6.044e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,pairwise_order,mean_prob_S4,-2.544e-06,-2.573e-06,2.544e-06,-0.007808747,-4.8875e-05,-3.628e-06


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,good_span_residual_ratio,1.4831e-05,1.3755e-05,1.4831e-05,0.172849256,0.079711512,8.205e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,move_abs_a2c8_Q3,6.504e-06,6.504e-06,6.504e-06,0.020153977,0.001852522,5.04e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,raw05_a2c8_compat_energy,6.241e-06,6.241e-06,6.241e-06,0.011163144,0.000996422,6.267e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,bad_axis_abs_load,-5.959e-06,-7.004e-06,5.959e-06,-0.006849614,-0.004618319,2.788e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,proj_a2c8,2.682e-06,2.682e-06,2.682e-06,-0.010648314,-0.004094944,-1.84e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,bad_axis_positive_load,-2.539e-06,-2.539e-06,2.539e-06,-0.00679001,-0.004618319,-8.834e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,move_abs_a2c8_S4,-2.202e-06,-2.202e-06,2.202e-06,0.003572445,0.000202766,5.04e-06
analysis_outputs/submission_label_flow_gated_ff8df011.csv,old_hidden_subset,proj_lejepa_bad,-2.068e-06,-2.068e-06,2.068e-06,-0.007895422,-0.002501028,-8.834e-06


### analysis_outputs/submission_label_flow_gated_f1046674.csv

#### pairwise_order

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,good_span_residual_ratio,6.824e-06,5.714e-06,6.824e-06,0.021013428,0.014650802,6.465e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,max_abs_move_vs_a2c8,-4.383e-06,-1.355e-06,4.385e-06,0.02019985,0.016586933,-4.818e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,rms_move_vs_a2c8,-1.702e-06,4.94e-07,2.536e-06,0.00711731,0.000854573,-4.818e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,bad_axis_abs_load,-7.52e-07,-6.09e-07,7.52e-07,-0.000753657,-0.00076825,-2.7e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,mean_prob_Q3,-7.18e-07,-7.19e-07,7.18e-07,0.001906161,5.3982e-05,-4.48e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,mean_abs_move_vs_a2c8,5.33e-07,1.26e-07,5.33e-07,0.000716002,6.3406e-05,-4.818e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,mean_prob_S4,-4.29e-07,-4.34e-07,4.29e-07,-0.001317453,-8.246e-06,-4.48e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,pairwise_order,bad_axis_positive_load,-4.24e-07,-3.97e-07,4.24e-07,-0.000747099,-0.00076825,1.256e-06


#### old_hidden_subset

candidate,selector,feature,mean_contribution,median_contribution,abs_mean_contribution,mean_z_diff,mean_raw_diff,mean_pred_delta
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,good_span_residual_ratio,2.726e-06,2.528e-06,2.726e-06,0.031769317,0.014650802,1.619e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,move_abs_a2c8_Q3,1.093e-06,1.093e-06,1.093e-06,0.00338545,0.000311185,8.77e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,raw05_a2c8_compat_energy,1.018e-06,1.018e-06,1.018e-06,0.001821645,0.0001626,1.033e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,bad_axis_abs_load,-9.91e-07,-1.165e-06,9.91e-07,-0.001139423,-0.00076825,6.28e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,proj_a2c8,5.84e-07,5.84e-07,5.84e-07,-0.002319514,-0.000891999,-2.57e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,bad_axis_positive_load,-4.22e-07,-4.22e-07,4.22e-07,-0.001129508,-0.00076825,-1.461e-06
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,move_abs_a2c8_S4,-3.73e-07,-3.73e-07,3.73e-07,0.000605139,3.4347e-05,8.77e-07
analysis_outputs/submission_label_flow_gated_f1046674.csv,old_hidden_subset,proj_lejepa_bad,-3.42e-07,-3.42e-07,3.42e-07,-0.001305841,-0.00041365,-1.461e-06


## Interpretation

- Pairwise models are internally mixed: S4 target-local movement and max-move terms often give favorable contributions, while residual-span/projection terms push the other way. E14 optimized the favorable pairwise scenario tail, not a unanimous pairwise model family.
- Old hidden-subset models also mix signs, but they do not give a scenario-majority endorsement. They mostly treat the focused S4/Q3 movement as an underidentified move away from a2c8 because the known public anchor set has no positive example for this exact direction.
- This is an underidentification problem: current anchors cannot tell whether the pairwise S4+Q3 direction is real public signal or a surrogate artifact. That is why E15 closed the submission gate.
