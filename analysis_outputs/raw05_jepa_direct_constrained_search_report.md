# Raw05 JEPA Direct Constrained Search

This search injects the axislocal direction while directly constraining posterior, raw/bad axes, and the Q3/S4 JEPA motif at candidate construction time.

## Counts

- generated candidates: `238656`
- prefiltered candidates: `1600`
- actual-anchor scored candidates: `1600`
- saved shortlist: `86`
- strict hits: `1600`
- tight-local hits: `9`

## Group Summary

```csv
mode,base_file,step_mask,n,strict_hits,tight_local_hits,best_local_delta,best_posterior,best_bad_abs,best_raw_abs,best_direct_score
axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,q2_s123,11,11,6,-3.9933e-06,0.5769049395,7.8848e-05,8.37e-08,-3.9929e-06
axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,q2_s123,267,267,2,-3.9921e-06,0.5769042391,3.62626e-05,3.51e-08,-3.9823e-06
axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,q1_s3,177,177,1,-3.9913e-06,0.5769043745,5.14738e-05,6.55e-08,-3.9913e-06
axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,all_soft,244,244,0,-3.99e-06,0.576904275,4.04802e-05,3.64e-08,-3.99e-06
axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,all_soft,5,5,0,-3.9896e-06,0.5769049864,8.36141e-05,8.74e-08,-3.988e-06
axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,q1_s3,378,378,0,-3.9814e-06,0.5769037412,4.31714e-05,4.84e-08,-3.9814e-06
axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,context_s4micro,249,249,0,-3.9805e-06,0.5769043062,3.93272e-05,3.6e-08,-3.9805e-06
axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,context,253,253,0,-3.9805e-06,0.5769043056,3.93215e-05,3.59e-08,-3.9805e-06
robust_axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,all_soft,16,16,0,-3.9723e-06,0.5769047465,4.07023e-05,3.87e-08,-3.9723e-06
```

## Shortlist

```csv
file,bucket,mode,base_file,local_file,safety_file,robust_file,step_mask,step_strength,step_cap,safety_mask,safety_eta,keep_orth,available_raw05_relative_delta_vs_raw05_public,available_raw05_relative_model_spread,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,q3s4_motif_cos,q3s4_motif_orth_ratio,direct_score,rank_score
submission_raw05_jepa_directcon_a903806a.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.28,0.0,-3.9811e-06,7.00567e-05,0.5778280678,0.5769048016,4.56e-08,-4.07816e-05,1.0,0.0,-3.9811e-06,270.56
submission_raw05_jepa_directcon_13ae72ff.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.28,0.0,-3.9814e-06,7.00552e-05,0.5778280686,0.5769048334,4.51e-08,-4.07155e-05,1.0,0.0,-3.9814e-06,280.56
submission_raw05_jepa_directcon_24c5fd81.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.0,-3.9793e-06,7.00406e-05,0.5778280864,0.5769048328,4.3e-08,-4.11138e-05,1.0,0.0,-3.9793e-06,299.94
submission_raw05_jepa_directcon_41cbb5e2.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.16,0.0,-3.9782e-06,7.00404e-05,0.5778280807,0.5769047669,4.51e-08,-4.24413e-05,1.0,0.0,-3.9782e-06,300.98
submission_raw05_jepa_directcon_b2e5ed28.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.0,-3.9781e-06,7.00439e-05,0.5778280789,0.5769047696,4.53e-08,-4.24008e-05,1.0,0.0,-3.9781e-06,302.0
submission_raw05_jepa_directcon_263bbb93.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.16,0.0,-3.9785e-06,7.00387e-05,0.5778280817,0.5769048039,4.44e-08,-4.23641e-05,1.0,0.0,-3.9785e-06,311.24
submission_raw05_jepa_directcon_7fff9480.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.0,-3.9784e-06,7.00422e-05,0.5778280798,0.5769048068,4.47e-08,-4.23205e-05,1.0,0.0,-3.9784e-06,312.26
submission_raw05_jepa_directcon_18aee823.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.0,-3.9797e-06,7.00388e-05,0.5778280874,0.5769048699,4.23e-08,-4.10367e-05,1.0,0.0,-3.9797e-06,314.04
submission_raw05_jepa_directcon_f19d3ee2.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.28,0.05,-3.9802e-06,7.0059e-05,0.5778280804,0.5769047981,4.49e-08,-3.91928e-05,0.9999999622,0.0003758387,-3.9802e-06,317.02
submission_raw05_jepa_directcon_c9375d84.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.0,-3.9751e-06,7.00304e-05,0.5778281138,0.5769047508,3.99e-08,-4.00756e-05,1.0,0.0,-3.9751e-06,317.04
submission_raw05_jepa_directcon_a0658e69.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.16,0.0,-3.9757e-06,7.00265e-05,0.5778281122,0.5769047825,4.01e-08,-4.07563e-05,1.0,0.0,-3.9757e-06,317.32
submission_raw05_jepa_directcon_c528e8a9.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.16,0.0,-3.9776e-06,7.00333e-05,0.5778280928,0.5769048145,4.28e-08,-4.20391e-05,1.0,0.0,-3.9776e-06,317.34
submission_raw05_jepa_directcon_396be2a6.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.16,0.0,-3.9761e-06,7.00247e-05,0.5778281132,0.5769048227,3.94e-08,-4.0671e-05,1.0,0.0,-3.9761e-06,319.14
submission_raw05_jepa_directcon_3ae124b0.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,context,0.08,0.0,-3.9758e-06,7.00254e-05,0.5778281122,0.5769047911,4e-08,-4.09028e-05,1.0,0.0,-3.9758e-06,320.4
submission_raw05_jepa_directcon_6867ee4f.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.08,0.0,-3.9782e-06,7.00298e-05,0.5778280989,0.5769048536,4.12e-08,-4.13353e-05,1.0,0.0,-3.9782e-06,321.9
submission_raw05_jepa_directcon_d152aad4.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,context,0.08,0.0,-3.9762e-06,7.00236e-05,0.5778281132,0.5769048317,3.93e-08,-4.08183e-05,1.0,0.0,-3.9762e-06,322.08
submission_raw05_jepa_directcon_cfee52c7.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.08,0.0,-3.9776e-06,7.00297e-05,0.577828096,0.5769048206,4.23e-08,-4.1999e-05,1.0,0.0,-3.9776e-06,323.24
submission_raw05_jepa_directcon_4c3627bc.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,context,0.16,0.0,-3.9749e-06,7.00301e-05,0.577828114,0.5769047449,3.99e-08,-4.01717e-05,1.0,0.0,-3.9749e-06,324.36
submission_raw05_jepa_directcon_8b0a1a39.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9764e-06,7.00228e-05,0.5778281117,0.5769048285,3.98e-08,-4.11565e-05,1.0,0.0,-3.9764e-06,325.16
submission_raw05_jepa_directcon_13670163.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9773e-06,7.00262e-05,0.577828102,0.5769048445,4.12e-08,-4.17979e-05,1.0,0.0,-3.9773e-06,325.66
submission_raw05_jepa_directcon_8725da5e.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.28,0.05,-3.9805e-06,7.00575e-05,0.5778280812,0.5769048299,4.43e-08,-3.91267e-05,0.9999999622,0.0003758387,-3.9805e-06,327.28
submission_raw05_jepa_directcon_294ea235.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.0,-3.9748e-06,7.00321e-05,0.5778281128,0.5769047136,4.05e-08,-4.01559e-05,1.0,0.0,-3.9748e-06,328.16
submission_raw05_jepa_directcon_a64a20aa.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.16,0.0,-3.978e-06,7.00314e-05,0.5778280938,0.5769048547,4.21e-08,-4.19538e-05,1.0,0.0,-3.978e-06,328.5
submission_raw05_jepa_directcon_72d8bb66.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,context,0.16,0.0,-3.9746e-06,7.00318e-05,0.577828113,0.5769047079,4.06e-08,-4.02489e-05,1.0,0.0,-3.9746e-06,330.62
submission_raw05_jepa_directcon_9cc8f8ff.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9767e-06,7.00208e-05,0.5778281128,0.5769048706,3.9e-08,-4.1068e-05,1.0,0.0,-3.9767e-06,333.18
submission_raw05_jepa_directcon_a4a739ee.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.08,0.0,-3.9785e-06,7.00279e-05,0.5778280999,0.5769048942,4.05e-08,-4.12508e-05,1.0,0.0,-3.9785e-06,333.78
submission_raw05_jepa_directcon_06cc6e00.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9777e-06,7.00242e-05,0.5778281031,0.5769048866,4.04e-08,-4.17094e-05,1.0,0.0,-3.9777e-06,335.6
submission_raw05_jepa_directcon_d83e504f.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.08,0.0,-3.9779e-06,7.00279e-05,0.5778280971,0.5769048612,4.16e-08,-4.19145e-05,1.0,0.0,-3.9779e-06,335.68
submission_raw05_jepa_directcon_0014f825.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,none,0.0,0.0,-3.977e-06,7.00191e-05,0.5778281113,0.5769048744,3.95e-08,-4.15568e-05,1.0,0.0,-3.977e-06,339.4
submission_raw05_jepa_directcon_d2ef8d53.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,context,0.08,0.0,-3.9837e-06,7.00155e-05,0.5778279775,0.5769046823,7.29e-08,-5.76063e-05,1.0,0.0,-3.9837e-06,340.5
submission_raw05_jepa_directcon_9557580f.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.05,-3.9772e-06,7.00463e-05,0.5778280913,0.5769047664,4.46e-08,-4.08172e-05,0.999999963,0.0003717394,-3.9772e-06,345.22
submission_raw05_jepa_directcon_9a81d724.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.16,0.004,context,0.08,0.0,-3.9855e-06,7.00198e-05,0.5778279614,0.5769047118,7.52e-08,-5.87024e-05,1.0,0.0,-3.9855e-06,345.36
submission_raw05_jepa_directcon_7a429e3e.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.05,-3.9784e-06,7.00429e-05,0.5778280991,0.5769048293,4.22e-08,-3.95251e-05,0.9999999622,0.0003758387,-3.9784e-06,346.76
submission_raw05_jepa_directcon_9f78c599.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.16,0.004,all_soft,0.08,0.0,-3.9853e-06,7.00144e-05,0.5778279625,0.576904733,7.54e-08,-5.93827e-05,1.0,0.0,-3.9853e-06,348.68
submission_raw05_jepa_directcon_3fa1bbe8.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,all_soft,0.16,0.0,-3.9832e-06,7.00138e-05,0.5778279795,0.5769046779,7.27e-08,-5.77701e-05,1.0,0.0,-3.9832e-06,349.04
submission_raw05_jepa_directcon_4ac35286.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.24,0.004,context,0.28,0.0,-3.9843e-06,7.00026e-05,0.5778279585,0.5769046499,7.89e-08,-6.22097e-05,1.0,0.0,-3.9843e-06,349.08
submission_raw05_jepa_directcon_c0247e2a.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,none,0.0,0.0,-3.9774e-06,7.0017e-05,0.5778281124,0.5769049186,3.87e-08,-4.14649e-05,1.0,0.0,-3.9774e-06,351.76
submission_raw05_jepa_directcon_c583f854.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.16,0.05,-3.9773e-06,7.00427e-05,0.5778280934,0.5769047633,4.44e-08,-4.08525e-05,0.9999999622,0.0003758387,-3.9773e-06,352.06
submission_raw05_jepa_directcon_2a8dd9e8.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.28,0.05,-3.9776e-06,7.00446e-05,0.5778280922,0.5769048036,4.4e-08,-4.07368e-05,0.999999963,0.0003717394,-3.9776e-06,352.94
submission_raw05_jepa_directcon_ac4db259.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,all_soft,0.08,0.0,-3.9844e-06,7.0011e-05,0.5778279722,0.576904717,7.4e-08,-5.87414e-05,1.0,0.0,-3.9844e-06,354.4
submission_raw05_jepa_directcon_7c9b5a37.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.05,-3.9787e-06,7.00411e-05,0.5778281,0.5769048664,4.16e-08,-3.94479e-05,0.9999999622,0.0003758387,-3.9787e-06,360.02
submission_raw05_jepa_directcon_6bf31d81.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,context,0.16,0.05,-3.9776e-06,7.0041e-05,0.5778280943,0.5769048004,4.37e-08,-4.07754e-05,0.9999999622,0.0003758387,-3.9776e-06,361.26
submission_raw05_jepa_directcon_a7745316.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,all_soft,0.16,0.05,-3.9768e-06,7.00356e-05,0.5778281053,0.5769048112,4.21e-08,-4.04533e-05,0.9999999627,0.0003734833,-3.9768e-06,362.28
submission_raw05_jepa_directcon_1c9491f4.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.16,0.004,none,0.0,0.0,-3.9856e-06,7.00082e-05,0.577827965,0.5769047561,7.52e-08,-5.97126e-05,1.0,0.0,-3.9856e-06,362.78
submission_raw05_jepa_directcon_eac33a56.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.28,0.12,-3.9789e-06,7.00622e-05,0.5778280981,0.5769047931,4.38e-08,-3.69686e-05,0.9999997822,0.0009019093,-3.9789e-06,364.86
submission_raw05_jepa_directcon_50a4fa51.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q2_s123,0.04,0.004,q2_s123,0.08,0.05,-3.9773e-06,7.00321e-05,0.5778281115,0.5769048501,4.05e-08,-3.97466e-05,0.9999999622,0.0003758387,-3.9773e-06,368.22
submission_raw05_jepa_directcon_6d32dde9.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.16,0.004,q2_s123,0.08,0.0,-3.9846e-06,7.00086e-05,0.5778279639,0.5769047571,7.52e-08,-6.0344e-05,1.0,0.0,-3.9846e-06,370.58
submission_raw05_jepa_directcon_145c7bf0.csv,direct_rank_fallback,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,q2_s123,0.08,0.0,-3.9823e-06,7.00042e-05,0.5778279772,0.5769046946,7.4e-08,-5.99115e-05,1.0,0.0,-3.9823e-06,371.3
submission_raw05_jepa_directcon_b19b5941.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.24,0.004,context,0.28,0.0,-3.9857e-06,6.99967e-05,0.5778279686,0.5769048004,7.53e-08,-6.07228e-05,1.0,0.0,-3.9857e-06,386.58
submission_raw05_jepa_directcon_2fd34400.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,context,0.16,0.0,-3.989e-06,7.00218e-05,0.5778279388,0.5769049485,7.2e-08,-5.52868e-05,1.0,0.0,-3.989e-06,448.76
submission_raw05_jepa_directcon_653fe1da.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.24,0.004,context,0.16,0.0,-3.9859e-06,6.99707e-05,0.5778279767,0.5769049002,7.54e-08,-6.29956e-05,1.0,0.0,-3.9859e-06,449.6
submission_raw05_jepa_directcon_93aef33a.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.0,-3.9896e-06,6.99655e-05,0.5778278357,0.5769048267,9.9e-08,-9.85415e-05,1.0,0.0,-3.9896e-06,452.36
submission_raw05_jepa_directcon_a96c6986.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,all_soft,0.28,0.0,-3.9893e-06,7.00191e-05,0.5778279355,0.5769049713,7.27e-08,-5.59914e-05,1.0,0.0,-3.9893e-06,466.18
submission_raw05_jepa_directcon_6780a595.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.0,-3.99e-06,6.99641e-05,0.5778278372,0.5769048607,9.83e-08,-9.83262e-05,1.0,0.0,-3.99e-06,476.82
submission_raw05_jepa_directcon_db24aae8.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,context,0.16,0.05,-3.9881e-06,7.00241e-05,0.5778279514,0.576904945,7.12e-08,-5.3698e-05,0.9999999622,0.0003758387,-3.9881e-06,488.72
submission_raw05_jepa_directcon_10946f46.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.24,0.004,context,0.08,0.0,-3.9861e-06,6.99534e-05,0.5778279821,0.5769049667,7.55e-08,-6.45108e-05,1.0,0.0,-3.9861e-06,496.82
submission_raw05_jepa_directcon_3cfd76d7.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.05,-3.9887e-06,6.99678e-05,0.5778278483,0.5769048232,9.82e-08,-9.69545e-05,0.9999999624,0.0003746971,-3.9887e-06,501.28
submission_raw05_jepa_directcon_44208861.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,all_soft,0.28,0.05,-3.9884e-06,7.00214e-05,0.5778279481,0.5769049677,7.2e-08,-5.44026e-05,0.9999999622,0.0003758387,-3.9884e-06,507.98
submission_raw05_jepa_directcon_4b4e92d7.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_anchorrobust_graft_e40a9b92.csv,,q1_s3,0.24,0.004,all_soft,0.08,0.0,-3.9858e-06,6.99449e-05,0.5778279841,0.5769050002,7.58e-08,-6.5532e-05,1.0,0.0,-3.9858e-06,513.78
submission_raw05_jepa_directcon_497545ea.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.05,-3.9891e-06,6.99664e-05,0.5778278498,0.5769048572,9.75e-08,-9.6739e-05,0.9999999624,0.0003748917,-3.9891e-06,519.48
submission_raw05_jepa_directcon_5cb7a18a.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,context,0.16,0.12,-3.9869e-06,7.00273e-05,0.5778279691,0.57690494,7.02e-08,-5.14738e-05,0.9999997822,0.0009019093,-3.9869e-06,524.32
submission_raw05_jepa_directcon_5fb2bf91.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_structrefine_90e28f7d.csv,,q1_s3,0.16,0.004,all_soft,0.28,0.12,-3.9871e-06,7.00246e-05,0.5778279658,0.5769049627,7.09e-08,-5.21784e-05,0.9999997822,0.0009019093,-3.9871e-06,540.72
submission_raw05_jepa_directcon_758a9f32.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.0,-3.9893e-06,6.99595e-05,0.5778278312,0.576904911,9.84e-08,-9.96091e-05,1.0,0.0,-3.9893e-06,541.62
submission_raw05_jepa_directcon_721f5393.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.12,-3.9874e-06,6.9971e-05,0.5778278659,0.5769048183,9.72e-08,-9.47326e-05,0.9999997835,0.0008991705,-3.9874e-06,542.68
submission_raw05_jepa_directcon_ef209256.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_7a15027d.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.12,-3.9857e-06,6.99704e-05,0.5778278575,0.5769047479,9.93e-08,-9.64895e-05,0.999999781,0.0009044205,-3.9857e-06,543.56
submission_raw05_jepa_directcon_2e7cbbfa.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q1_s3,0.16,0.004,all_soft,0.08,0.0,-3.9891e-06,6.99286e-05,0.5778278302,0.5769049284,9.74e-08,-8.80779e-05,1.0,0.0,-3.9891e-06,545.2
submission_raw05_jepa_directcon_25495bdc.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9929e-06,6.99901e-05,0.5778278426,0.5769049697,8.8e-08,-8.36231e-05,1.0,0.0,-3.9929e-06,555.4
submission_raw05_jepa_directcon_db07e01a.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.05,-3.9884e-06,6.99619e-05,0.5778278438,0.5769049073,9.76e-08,-9.80074e-05,0.9999999624,0.0003750174,-3.9884e-06,559.16
submission_raw05_jepa_directcon_4eaa2c45.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.12,-3.9878e-06,6.99696e-05,0.5778278674,0.5769048522,9.65e-08,-9.45169e-05,0.9999997833,0.0008996375,-3.9878e-06,560.96
submission_raw05_jepa_directcon_27290cd0.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.07,0.004,all_soft,0.08,0.0,-3.9896e-06,6.99639e-05,0.5778278472,0.5769050163,8.91e-08,-8.82936e-05,1.0,0.0,-3.9867e-06,562.58
submission_raw05_jepa_directcon_ff079802.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.0,-3.9933e-06,6.99881e-05,0.5778278436,0.5769050118,8.73e-08,-8.35346e-05,1.0,0.0,-3.9911e-06,578.38
submission_raw05_jepa_directcon_4e3a83cd.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q1_s3,0.16,0.004,all_soft,0.08,0.05,-3.9882e-06,6.99319e-05,0.5778278454,0.5769049158,9.66e-08,-8.61252e-05,0.9999999449,0.0004537348,-3.9882e-06,580.56
submission_raw05_jepa_directcon_0871c1ed.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.05,-3.992e-06,6.99934e-05,0.5778278578,0.5769049571,8.73e-08,-8.16704e-05,0.9999999449,0.0004537348,-3.992e-06,588.2
submission_raw05_jepa_directcon_733e4345.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.04,0.004,q2_s123,0.16,0.12,-3.9872e-06,6.99652e-05,0.5778278614,0.5769049022,9.66e-08,-9.5765e-05,0.9999997831,0.0008999389,-3.9872e-06,598.0
submission_raw05_jepa_directcon_48409823.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,q1_s3,0.16,0.004,q2_s123,0.08,0.12,-3.9913e-06,6.997e-05,0.5778278659,0.5769049214,9.96e-08,-8.52584e-05,0.9999997822,0.0009019093,-3.9913e-06,600.12
submission_raw05_jepa_directcon_3d297f8a.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q1_s3,0.16,0.004,all_soft,0.08,0.12,-3.9869e-06,6.99366e-05,0.5778278667,0.5769048982,9.56e-08,-8.33914e-05,0.9999996825,0.0010888294,-3.9869e-06,610.98
submission_raw05_jepa_directcon_1d7f766f.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.05,-3.9923e-06,6.99915e-05,0.5778278589,0.5769049992,8.65e-08,-8.15819e-05,0.9999999449,0.0004537348,-3.9923e-06,612.78
submission_raw05_jepa_directcon_49f8671e.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.12,-3.9907e-06,6.99981e-05,0.5778278791,0.5769049395,8.62e-08,-7.89366e-05,0.9999996825,0.0010888294,-3.9907e-06,619.24
submission_raw05_jepa_directcon_6c8ac0b9.csv,direct_tight_local,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_7a15027d.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.0,-3.9921e-06,6.99456e-05,0.5778278334,0.5769050546,9.67e-08,-0.0001009963,1.0,0.0,-3.9822e-06,621.52
submission_raw05_jepa_directcon_d39af782.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.07,0.004,all_soft,0.08,0.05,-3.9887e-06,6.99673e-05,0.5778278624,0.5769050039,8.84e-08,-8.63438e-05,0.9999999453,0.0004518622,-3.988e-06,628.92
submission_raw05_jepa_directcon_e096c9eb.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.05,-3.9871e-06,6.99746e-05,0.5778278675,0.5769050032,8.48e-08,-8.45295e-05,0.9999999449,0.0004537348,-3.9865e-06,631.66
submission_raw05_jepa_directcon_9c57fed2.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_20e4a625.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.12,-3.9911e-06,6.99961e-05,0.5778278802,0.5769049817,8.55e-08,-7.8848e-05,0.9999996825,0.0010888294,-3.9911e-06,644.78
submission_raw05_jepa_directcon_2f880ea2.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_d90f09cf.csv,submission_raw05_jepa_efback_cc265f32.csv,,all_soft,0.07,0.004,all_soft,0.08,0.12,-3.9875e-06,6.9972e-05,0.5778278836,0.5769049864,8.74e-08,-8.36141e-05,0.9999996852,0.0010843371,-3.9875e-06,659.94
submission_raw05_jepa_directcon_05278096.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,all_soft,0.08,0.12,-3.9858e-06,6.99793e-05,0.5778278889,0.5769049856,8.37e-08,-8.17956e-05,0.9999996825,0.0010888294,-3.9858e-06,663.28
submission_raw05_jepa_directcon_68279e13.csv,direct_tight_local,axis_direct,submission_raw05_jepa_structrefine_90e28f7d.csv,submission_raw05_jepa_axislocal_7a15027d.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.004,q2_s123,0.16,0.05,-3.9912e-06,6.99479e-05,0.577827846,0.576905051,9.59e-08,-9.94076e-05,0.9999999622,0.0003758387,-3.982e-06,667.72
submission_raw05_jepa_directcon_ab12b93d.csv,direct_strict,axis_direct,submission_raw05_jepa_structrefine_04ad10f8.csv,submission_raw05_jepa_axislocal_16ae093a.csv,submission_raw05_jepa_efback_cc265f32.csv,,q2_s123,0.04,0.008,all_soft,0.08,0.12,-3.9862e-06,6.9979e-05,0.5778278875,0.5769050012,8.38e-08,-8.17655e-05,0.9999996825,0.0010888294,-3.986e-06,670.64
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_directcon_a903806a.csv,250,True,0,0,0.0630759627,0.9797989093
submission_raw05_jepa_directcon_13ae72ff.csv,250,True,0,0,0.0630759627,0.9797989313
submission_raw05_jepa_directcon_24c5fd81.csv,250,True,0,0,0.0630759627,0.9797989199
submission_raw05_jepa_directcon_41cbb5e2.csv,250,True,0,0,0.0630765868,0.9797989199
submission_raw05_jepa_directcon_b2e5ed28.csv,250,True,0,0,0.0630764542,0.9797989204
submission_raw05_jepa_directcon_263bbb93.csv,250,True,0,0,0.0630765868,0.9797989455
submission_raw05_jepa_directcon_7fff9480.csv,250,True,0,0,0.0630764542,0.9797989463
submission_raw05_jepa_directcon_18aee823.csv,250,True,0,0,0.0630759627,0.9797989455
submission_raw05_jepa_directcon_f19d3ee2.csv,250,True,0,0,0.0630759627,0.9797989093
submission_raw05_jepa_directcon_c9375d84.csv,250,True,0,0,0.0630759627,0.9797987384
submission_raw05_jepa_directcon_a0658e69.csv,250,True,0,0,0.0630759627,0.9797988075
submission_raw05_jepa_directcon_c528e8a9.csv,250,True,0,0,0.0630762435,0.9797989263
submission_raw05_jepa_directcon_396be2a6.csv,250,True,0,0,0.0630759627,0.9797988353
submission_raw05_jepa_directcon_3ae124b0.csv,250,True,0,0,0.0630759627,0.979798819
submission_raw05_jepa_directcon_6867ee4f.csv,250,True,0,0,0.0630759627,0.979798927
submission_raw05_jepa_directcon_d152aad4.csv,250,True,0,0,0.0630759627,0.9797988471
submission_raw05_jepa_directcon_cfee52c7.csv,250,True,0,0,0.0630762747,0.979798927
submission_raw05_jepa_directcon_4c3627bc.csv,250,True,0,0,0.0630759627,0.9797987296
submission_raw05_jepa_directcon_8b0a1a39.csv,250,True,0,0,0.0630759627,0.9797988707
submission_raw05_jepa_directcon_13670163.csv,250,True,0,0,0.0630761031,0.9797989301
submission_raw05_jepa_directcon_8725da5e.csv,250,True,0,0,0.0630759627,0.9797989313
submission_raw05_jepa_directcon_294ea235.csv,250,True,0,0,0.0630759627,0.9797987126
submission_raw05_jepa_directcon_a64a20aa.csv,250,True,0,0,0.0630762435,0.9797989541
submission_raw05_jepa_directcon_72d8bb66.csv,250,True,0,0,0.0630759627,0.9797987039
submission_raw05_jepa_directcon_9cc8f8ff.csv,250,True,0,0,0.0630759627,0.9797988999
submission_raw05_jepa_directcon_a4a739ee.csv,250,True,0,0,0.0630759627,0.9797989551
submission_raw05_jepa_directcon_06cc6e00.csv,250,True,0,0,0.0630761031,0.9797989593
submission_raw05_jepa_directcon_d83e504f.csv,250,True,0,0,0.0630762747,0.9797989551
submission_raw05_jepa_directcon_0014f825.csv,250,True,0,0,0.0630759627,0.979798934
submission_raw05_jepa_directcon_d2ef8d53.csv,250,True,0,0,0.0630783827,0.9797987377
submission_raw05_jepa_directcon_9557580f.csv,250,True,0,0,0.0630764542,0.9797989204
submission_raw05_jepa_directcon_9a81d724.csv,250,True,0,0,0.0630786948,0.9797988457
submission_raw05_jepa_directcon_7a429e3e.csv,250,True,0,0,0.0630759627,0.9797989199
submission_raw05_jepa_directcon_9f78c599.csv,250,True,0,0,0.0630786389,0.9797988457
submission_raw05_jepa_directcon_3fa1bbe8.csv,250,True,0,0,0.0630784038,0.9797987269
submission_raw05_jepa_directcon_4ac35286.csv,250,True,0,0,0.0630790437,0.9797988457
submission_raw05_jepa_directcon_c0247e2a.csv,250,True,0,0,0.0630759627,0.9797989646
submission_raw05_jepa_directcon_c583f854.csv,250,True,0,0,0.0630765868,0.9797989199
submission_raw05_jepa_directcon_2a8dd9e8.csv,250,True,0,0,0.0630764542,0.9797989463
submission_raw05_jepa_directcon_ac4db259.csv,250,True,0,0,0.0630784985,0.9797987863
submission_raw05_jepa_directcon_7c9b5a37.csv,250,True,0,0,0.0630759627,0.9797989455
submission_raw05_jepa_directcon_6bf31d81.csv,250,True,0,0,0.0630765868,0.9797989455
submission_raw05_jepa_directcon_a7745316.csv,250,True,0,0,0.0630762435,0.9797989263
submission_raw05_jepa_directcon_1c9491f4.csv,250,True,0,0,0.0630785932,0.9797988457
submission_raw05_jepa_directcon_eac33a56.csv,250,True,0,0,0.0630759627,0.9797989093
submission_raw05_jepa_directcon_50a4fa51.csv,250,True,0,0,0.0630759627,0.979798927
submission_raw05_jepa_directcon_6d32dde9.csv,250,True,0,0,0.0630785932,0.9797988457
submission_raw05_jepa_directcon_145c7bf0.csv,250,True,0,0,0.0630785932,0.9797987377
submission_raw05_jepa_directcon_b19b5941.csv,250,True,0,0,0.0630784916,0.9797988457
submission_raw05_jepa_directcon_2fd34400.csv,250,True,0,0,0.063078994,0.9797986298
submission_raw05_jepa_directcon_653fe1da.csv,250,True,0,0,0.063078263,0.9797988457
submission_raw05_jepa_directcon_93aef33a.csv,250,True,0,0,0.0630759476,0.9798011244
submission_raw05_jepa_directcon_a96c6986.csv,250,True,0,0,0.0630791167,0.9797986379
submission_raw05_jepa_directcon_6780a595.csv,250,True,0,0,0.0630758901,0.9798011385
submission_raw05_jepa_directcon_db24aae8.csv,250,True,0,0,0.063078994,0.9797986298
submission_raw05_jepa_directcon_10946f46.csv,250,True,0,0,0.0630781106,0.9797988457
submission_raw05_jepa_directcon_3cfd76d7.csv,250,True,0,0,0.0630759476,0.9798011244
submission_raw05_jepa_directcon_44208861.csv,250,True,0,0,0.0630791167,0.9797986379
submission_raw05_jepa_directcon_4b4e92d7.csv,250,True,0,0,0.0630780268,0.9797988457
submission_raw05_jepa_directcon_497545ea.csv,250,True,0,0,0.0630758901,0.9798011385
submission_raw05_jepa_directcon_5cb7a18a.csv,250,True,0,0,0.063078994,0.9797986298
submission_raw05_jepa_directcon_5fb2bf91.csv,250,True,0,0,0.0630791167,0.9797986379
submission_raw05_jepa_directcon_758a9f32.csv,250,True,0,0,0.0630760001,0.979801117
submission_raw05_jepa_directcon_721f5393.csv,250,True,0,0,0.0630759476,0.9798011244
submission_raw05_jepa_directcon_ef209256.csv,250,True,0,0,0.0630762295,0.979801059
submission_raw05_jepa_directcon_2e7cbbfa.csv,250,True,0,0,0.0630824944,0.9797996014
submission_raw05_jepa_directcon_25495bdc.csv,250,True,0,0,0.0630827757,0.9798009245
submission_raw05_jepa_directcon_db07e01a.csv,250,True,0,0,0.0630760001,0.979801117
submission_raw05_jepa_directcon_4eaa2c45.csv,250,True,0,0,0.0630758901,0.9798011385
submission_raw05_jepa_directcon_27290cd0.csv,250,True,0,0,0.0630826317,0.9798008749
submission_raw05_jepa_directcon_ff079802.csv,250,True,0,0,0.0630827757,0.9798009537
submission_raw05_jepa_directcon_4e3a83cd.csv,250,True,0,0,0.0630824944,0.9797996014
submission_raw05_jepa_directcon_0871c1ed.csv,250,True,0,0,0.0630827757,0.9798009245
submission_raw05_jepa_directcon_733e4345.csv,250,True,0,0,0.0630760001,0.979801117
submission_raw05_jepa_directcon_48409823.csv,250,True,0,0,0.0630785932,0.9798002198
submission_raw05_jepa_directcon_3d297f8a.csv,250,True,0,0,0.0630824944,0.9797996014
submission_raw05_jepa_directcon_1d7f766f.csv,250,True,0,0,0.0630827757,0.9798009537
submission_raw05_jepa_directcon_49f8671e.csv,250,True,0,0,0.0630827757,0.9798009245
submission_raw05_jepa_directcon_6c8ac0b9.csv,250,True,0,0,0.0630759627,0.979801549
submission_raw05_jepa_directcon_d39af782.csv,250,True,0,0,0.0630826317,0.9798008749
submission_raw05_jepa_directcon_e096c9eb.csv,250,True,0,0,0.0630827757,0.9798009093
submission_raw05_jepa_directcon_9c57fed2.csv,250,True,0,0,0.0630827757,0.9798009537
submission_raw05_jepa_directcon_2f880ea2.csv,250,True,0,0,0.0630826317,0.9798008749
submission_raw05_jepa_directcon_05278096.csv,250,True,0,0,0.0630827757,0.9798009093
submission_raw05_jepa_directcon_68279e13.csv,250,True,0,0,0.0630759627,0.979801549
submission_raw05_jepa_directcon_ab12b93d.csv,250,True,0,0,0.0630827757,0.9798009093
```