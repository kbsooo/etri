# Raw05 JEPA Public6 Q3S4 Axis-Corrected Candidates

Uses the six-anchor posterior only as a target-block direction for Q3/S4. Candidate moves are optionally projected away from raw-public and bad residual axes, matching the JEPA idea of changing the target representation while preserving context/public-axis compatibility.

- generated candidates: `2160`
- shortlisted/saved candidates: `180`

## Projection Fit

```csv
prior,prior_file,projection_converged,projection_max_abs_residual,projection_mean_abs_move,expected_anchor578,expected_stage2,expected_ordinal,expected_raw05,expected_latent_q2,expected_latent_resid
compatband,submission_raw05_jepa_compatband_e065e98e.csv,True,0.0,0.0172103669,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
efmicro5,submission_raw05_jepa_efmicro_5d2d2af0.csv,True,0.0,0.0172104622,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
efmicro3,submission_raw05_jepa_efmicro_3eece507.csv,True,0.0,0.0172109717,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
energyfront,submission_raw05_jepa_energyfront_a190aa25.csv,True,0.0,0.017216935,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
siggate,submission_raw05_jepa_siggate_6d681440.csv,True,0.0,0.0172194533,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
raw05,submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,True,0.0,0.0181051323,0.5784273528,0.5779449757,0.5783033652,0.5775263072,0.5798012862,0.5812273278
```

## Best Prior/Mode Groups

```csv
prior,mode,n,best_actual,best_selection,best_raw_abs,best_bad_abs
energyfront,prob_bad_raw_ortho,60,0.5777874285,0.5778321073,1.463e-07,8.04103e-05
energyfront,prob_raw_ortho,60,0.577790097,0.5778326965,1.493e-07,5.6892e-06
compatband,prob_bad_raw_ortho,60,0.5777874289,0.5778331145,1.661e-07,1.03484e-05
efmicro3,prob_bad_raw_ortho,60,0.5777874375,0.5778331215,1.607e-07,1.40874e-05
efmicro5,prob_bad_raw_ortho,60,0.5777875152,0.5778332572,1.742e-07,2.1801e-06
compatband,prob_raw_ortho,60,0.5777900851,0.5778332582,1.691e-07,3.68e-08
efmicro3,prob_raw_ortho,60,0.5777900886,0.5778332652,1.637e-07,4.1942e-06
efmicro5,prob_raw_ortho,60,0.5777901701,0.5778334037,1.772e-07,1.80648e-05
siggate,prob_bad_raw_ortho,60,0.5777883649,0.5778345336,1.71e-07,5.1606e-06
siggate,prob_raw_ortho,60,0.577790984,0.5778347244,1.74e-07,0.0002342719
energyfront,prob_raw_ortho_positive,60,0.5777874284,0.5778360769,2.194e-07,1.94303e-05
compatband,prob_bad_raw_ord_ortho,60,0.5778248729,0.5778371701,1.221e-07,3.9244e-06
efmicro5,prob_bad_raw_ord_ortho,60,0.5778250258,0.5778373049,1.303e-07,8.1225e-06
energyfront,prob_bad_raw_ord_ortho,60,0.5778247761,0.5778374462,1.024e-07,1.27637e-05
efmicro3,prob_bad_raw_ord_ortho,60,0.5778248704,0.5778374735,1.168e-07,8.0236e-06
efmicro3,prob_raw_ortho_positive,60,0.577787431,0.5778378312,2.338e-07,6.2471e-06
compatband,prob_raw_ortho_positive,60,0.5777874221,0.577838466,2.392e-07,2.0925e-06
siggate,prob_bad_raw_ord_ortho,60,0.5778262921,0.5778388223,1.269e-07,3.5073e-06
efmicro5,prob_raw_ortho_positive,60,0.5777875051,0.5778395745,2.473e-07,2.13542e-05
siggate,prob_raw_ortho_positive,60,0.5777883493,0.5778405229,2.442e-07,0.00023587
energyfront,direct_logit,60,0.5777732269,0.5778774113,5.67e-07,5.8803e-06
efmicro3,direct_logit,60,0.577773247,0.5778791647,5.814e-07,7.4094e-06
energyfront,prob,60,0.5777728631,0.5778793188,5.837e-07,9.726e-07
compatband,direct_logit,60,0.5777732402,0.5778797999,5.867e-07,3.2513e-06
efmicro5,direct_logit,60,0.5777733128,0.5778809091,5.949e-07,3.67571e-05
efmicro3,prob,60,0.577772871,0.5778810717,5.981e-07,2.9007e-06
compatband,prob,60,0.5777728611,0.5778817067,6.034e-07,1.258e-06
siggate,direct_logit,60,0.5777741397,0.5778818433,5.918e-07,0.00024345
efmicro5,prob,60,0.5777729333,0.5778828161,6.115e-07,3.22433e-05
siggate,prob,60,0.5777737556,0.5778837494,6.085e-07,0.0002411974
raw05,direct_logit,60,0.5777989417,0.5790759683,5e-10,0.0001142475
raw05,prob,60,0.5777982133,0.5790783387,4.3e-09,0.0001248849
raw05,prob_raw_ortho_positive,60,0.5777941554,0.5791289213,1.37e-08,0.0001259397
raw05,prob_raw_ortho,60,0.5777937119,0.5791314695,2.6e-09,0.0001334423
raw05,prob_bad_raw_ortho,60,0.5777903038,0.5791445194,2e-10,0.0030029412
raw05,prob_bad_raw_ord_ortho,60,0.5778736202,0.5791593012,1.13e-08,0.002735067
```

## Top Shortlist

```csv
file,prior,mode,gate,gamma,actual_anchor_score_final,ranker_selection_score,q3s4_corr_score,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,raw_penalty,bad_penalty,posterior_penalty,mean_abs_move_vs_raw05,candidate_mean_abs_move_vs_prior,mean_target_delta_Q3,mean_target_delta_S4
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_top60_strength_g015_bcef9a36.csv,compatband,prob_bad_raw_ord_ortho,top60_strength,0.015,0.57783745,0.57783745,0.5778436336,0.5768993862,1.786e-07,0.0003936251,0.0,0.0,0.0,0.0015067178,2.39471e-05,-6.9439e-06,5.1995e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_top60_strength_g015_4050287e.csv,efmicro5,prob_bad_raw_ord_ortho,top60_strength,0.015,0.577837585,0.577837585,0.5778437524,0.5768973679,1.867e-07,0.0003596404,0.0,0.0,0.0,0.0015136101,2.395e-05,-6.9399e-06,5.2092e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_top60_strength_g015_eb7beab5.csv,efmicro3,prob_bad_raw_ord_ortho,top60_strength,0.015,0.577837457,0.5778381118,0.5778442936,0.5769003274,1.732e-07,0.0003895535,0.0,0.0,6.549e-07,0.001504027,2.39479e-05,-6.9458e-06,5.1966e-06
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_strength_entropy_g015_eadff4b4.csv,compatband,prob_bad_raw_ord_ortho,strength_entropy,0.015,0.5778376541,0.5778376574,0.5778447525,0.5769000017,1.464e-07,0.0004236237,0.0,0.0,3.3e-09,0.0015078435,2.75331e-05,-1.34035e-05,8.824e-07
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_strength_entropy_g015_19907b79.csv,efmicro5,prob_bad_raw_ord_ortho,strength_entropy,0.015,0.5778377892,0.5778377892,0.5778448681,0.5768979831,1.545e-07,0.000389646,0.0,0.0,0.0,0.0015147358,2.75363e-05,-1.33975e-05,8.917e-07
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_strength_g015_2d2e400b.csv,compatband,prob_bad_raw_ord_ortho,strength,0.015,0.5778375596,0.5778375596,0.5778449064,0.5768998736,1.573e-07,0.0004201067,0.0,0.0,0.0,0.0015086556,2.85473e-05,-1.49433e-05,2.5883e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_strength_g015_181a33a9.csv,efmicro5,prob_bad_raw_ord_ortho,strength,0.015,0.5778376946,0.5778376946,0.5778450253,0.576897855,1.654e-07,0.0003861303,0.0,0.0,0.0,0.001515548,2.85505e-05,-1.49367e-05,2.5982e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_top60_strength_g015_af4b94ba.csv,siggate,prob_bad_raw_ord_ortho,top60_strength,0.015,0.5778390985,0.5778390985,0.5778451416,0.5768914971,1.834e-07,-9.89096e-05,0.0,0.0,0.0,0.001506962,2.39743e-05,-6.9589e-06,5.1971e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_top60_strength_g020_7cb11c49.csv,energyfront,prob_bad_raw_ord_ortho,top60_strength,0.02,0.577837006,0.5778374462,0.5778457889,0.5769002201,1.96e-07,0.0007161462,0.0,0.0,4.402e-07,0.0015061223,3.19385e-05,-9.2648e-06,6.9224e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_top60_strength_g015_dd423b4b.csv,energyfront,prob_bad_raw_ord_ortho,top60_strength,0.015,0.5778374329,0.5778395326,0.5778458967,0.5769010498,1.588e-07,0.0007513153,0.0,0.0,2.0997e-06,0.001500945,2.39539e-05,-6.9486e-06,5.1918e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_strength_entropy_g015_1706207a.csv,siggate,prob_bad_raw_ord_ortho,strength_entropy,0.015,0.5778392486,0.5778392486,0.5778461742,0.5768921132,1.512e-07,-6.88725e-05,0.0,0.0,0.0,0.001508089,2.75646e-05,-1.34336e-05,8.765e-07
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_strength_g015_c82d0b15.csv,siggate,prob_bad_raw_ord_ortho,strength,0.015,0.5778391689,0.5778391689,0.5778463501,0.5768919849,1.621e-07,-7.23805e-05,0.0,0.0,0.0,0.0015089031,2.85804e-05,-1.49752e-05,2.5832e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_top60_strength_g020_5719f188.csv,efmicro3,prob_bad_raw_ord_ortho,top60_strength,0.02,0.5778370304,0.5778382777,0.5778464376,0.5768994977,2.104e-07,0.0003544026,1.2473e-06,0.0,0.0,0.0015092022,3.19305e-05,-9.2611e-06,6.9288e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_strength_g015_401479c6.csv,efmicro3,prob_bad_raw_ord_ortho,strength,0.015,0.5778375666,0.5778391966,0.5778465417,0.576900815,1.519e-07,0.0004160344,0.0,0.0,1.63e-06,0.001505965,2.85482e-05,-1.4947e-05,2.5854e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_strength_entropy_g015_db746a45.csv,efmicro3,prob_bad_raw_ord_ortho,strength_entropy,0.015,0.5778376612,0.5778395472,0.5778466405,0.576900943,1.411e-07,0.0004195517,0.0,0.0,1.886e-06,0.0015051529,2.7534e-05,-1.34069e-05,8.795e-07
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_strength_entropy_g020_111285da.csv,compatband,prob_bad_raw_ord_ortho,strength_entropy,0.02,0.5778372952,0.5778372952,0.5778466721,0.5768993765,1.725e-07,0.0003984738,0.0,0.0,0.0,0.0015133789,3.67108e-05,-1.78713e-05,1.1766e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_strength_entropy_g020_bf9ca6dc.csv,efmicro5,prob_bad_raw_ord_ortho,strength_entropy,0.02,0.57783743,0.57783743,0.577846791,0.5768973575,1.806e-07,0.0003644961,0.0,0.0,0.0,0.0015202719,3.6715e-05,-1.78634e-05,1.189e-06
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_strength_g020_8089d79a.csv,compatband,prob_bad_raw_ord_ortho,strength,0.02,0.5778371701,0.5778371701,0.5778468827,0.5768992067,1.878e-07,0.0003937845,0.0,0.0,0.0,0.0015145016,3.8063e-05,-1.99244e-05,3.4511e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_strength_g020_2cead1ff.csv,efmicro5,prob_bad_raw_ord_ortho,strength,0.02,0.5778373049,0.5778373049,0.5778470016,0.5768971876,1.959e-07,0.0003598085,0.0,0.0,0.0,0.0015213948,3.80673e-05,-1.99156e-05,3.4643e-06
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_top60_strength_g020_ff7e4e7e.csv,compatband,prob_bad_raw_ord_ortho,top60_strength,0.02,0.5778370234,0.577838912,0.5778470736,0.5768985564,2.157e-07,0.0003584756,1.8885e-06,0.0,0.0,0.0015118927,3.19295e-05,-9.2585e-06,6.9326e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_strength_g020_2735fa11.csv,efmicro3,prob_bad_raw_ord_ortho,strength,0.02,0.5778371771,0.5778374735,0.5778471844,0.5769001482,1.824e-07,0.0003897105,0.0,0.0,2.963e-07,0.0015118114,3.80643e-05,-1.99294e-05,3.4472e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ord_ortho_strength_entropy_g020_6755ef8d.csv,efmicro3,prob_bad_raw_ord_ortho,strength_entropy,0.02,0.5778373023,0.5778379382,0.5778473134,0.576900318,1.671e-07,0.0003944002,0.0,0.0,6.36e-07,0.0015106886,3.6712e-05,-1.78759e-05,1.1727e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_strength_g015_28d35c5b.csv,energyfront,prob_bad_raw_ord_ortho,strength,0.015,0.5778375426,0.5778406185,0.5778481462,0.5769015379,1.375e-07,0.0007777878,0.0,0.0,3.0759e-06,0.0015028842,2.85554e-05,-1.49554e-05,2.5816e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_top60_strength_g020_4408cbd5.csv,efmicro5,prob_bad_raw_ord_ortho,top60_strength,0.02,0.5778371582,0.5778400202,0.5778481658,0.5768965377,2.238e-07,0.0003244886,2.862e-06,0.0,0.0,0.0015187859,3.19333e-05,-9.2531e-06,6.9457e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_strength_entropy_g020_fec5dc5a.csv,siggate,prob_bad_raw_ord_ortho,strength_entropy,0.02,0.5778389402,0.5778389402,0.5778481754,0.5768914867,1.773e-07,-9.40315e-05,0.0,0.0,0.0,0.0015136341,3.67528e-05,-1.79114e-05,1.1686e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_strength_entropy_g015_207b801b.csv,energyfront,prob_bad_raw_ord_ortho,strength_entropy,0.015,0.5778376372,0.5778409692,0.5778482451,0.576901666,1.266e-07,0.000781311,0.0,0.0,3.3319e-06,0.0015020721,2.75412e-05,-1.34141e-05,8.747e-07
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_strength_g020_f245fb7c.csv,siggate,prob_bad_raw_ord_ortho,strength,0.02,0.5778388223,0.5778388223,0.5778483984,0.5768913166,1.926e-07,-9.87089e-05,0.0,0.0,0.0,0.0015147595,3.81071e-05,-1.99669e-05,3.4443e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_entropy_mid_g015_9be8f706.csv,efmicro5,prob_bad_raw_ord_ortho,entropy_mid,0.015,0.577838086,0.577838086,0.5778487663,0.5768990292,1.303e-07,0.0004549923,0.0,0.0,0.0,0.0015215366,4.18111e-05,-2.90111e-05,-9.9198e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_strength_g020_63a5547d.csv,energyfront,prob_bad_raw_ord_ortho,strength,0.02,0.5778371528,0.5778388953,0.5778487895,0.5769008712,1.68e-07,0.0007514428,0.0,0.0,1.7425e-06,0.0015087331,3.80739e-05,-1.99406e-05,3.4422e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ord_ortho_strength_entropy_g020_7c0cbda2.csv,energyfront,prob_bad_raw_ord_ortho,strength_entropy,0.02,0.577837278,0.5778393602,0.5778489187,0.5769010411,1.527e-07,0.0007561404,0.0,0.0,2.0822e-06,0.0015076103,3.67216e-05,-1.78854e-05,1.1663e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_top60_strength_g020_42473f20.csv,siggate,prob_bad_raw_ord_ortho,top60_strength,0.02,0.5778386757,0.5778411568,0.5778492153,0.5768906657,2.207e-07,-0.000134081,2.4811e-06,0.0,0.0,0.0015121462,3.19658e-05,-9.2785e-06,6.9295e-06
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ortho_entropy_mid_g015_6558d03d.csv,compatband,prob_bad_raw_ortho,entropy_mid,0.015,0.577833774,0.577833774,0.5778497706,0.5768951612,1.661e-07,0.0004873205,0.0,0.0,0.0,0.0015255622,6.30119e-05,-5.71981e-05,-3.9953e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ortho_entropy_mid_g015_f1f95b77.csv,efmicro3,prob_bad_raw_ortho,entropy_mid,0.015,0.577833781,0.577833781,0.577849776,0.5768961025,1.607e-07,0.0004832532,0.0,0.0,0.0,0.0015228724,6.30136e-05,-5.72055e-05,-3.9983e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ortho_entropy_mid_g015_f6d92164.csv,efmicro5,prob_bad_raw_ortho,entropy_mid,0.015,0.5778339079,0.5778339079,0.5778498892,0.5768931422,1.742e-07,0.0004533406,0.0,0.0,0.0,0.0015324563,6.30184e-05,-5.71855e-05,-3.9875e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_entropy_mid_g015_ebcef5e2.csv,siggate,prob_bad_raw_ord_ortho,entropy_mid,0.015,0.5778394369,0.5778394369,0.5778499032,0.5768931609,1.269e-07,-3.5073e-06,0.0,0.0,0.0,0.0015149029,4.1858e-05,-2.90598e-05,-9.9406e-06
submission_raw05_jepa_public6q3s4corr_compatband_prob_raw_ortho_entropy_mid_g015_47a20ebc.csv,compatband,prob_raw_ortho,entropy_mid,0.015,0.5778338991,0.5778338991,0.5778499252,0.5768955101,1.691e-07,0.0002051356,0.0,0.0,0.0,0.0015244863,6.36941e-05,-2.85585e-05,4.4283e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_raw_ortho_entropy_mid_g015_9336898a.csv,efmicro3,prob_raw_ortho,entropy_mid,0.015,0.5778339062,0.5778339062,0.5778499307,0.5768964515,1.637e-07,0.0002010155,0.0,0.0,0.0,0.0015217963,6.36961e-05,-2.85605e-05,4.4268e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ortho_entropy_mid_g015_0b3953cd.csv,energyfront,prob_bad_raw_ortho,entropy_mid,0.015,0.5778337569,0.5778337569,0.577849935,0.5768968255,1.463e-07,0.0008450684,0.0,0.0,0.0,0.0015197951,6.3022e-05,-5.72294e-05,-4.0081e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_raw_ortho_entropy_mid_g015_443b90a1.csv,efmicro5,prob_raw_ortho,entropy_mid,0.015,0.577834033,0.577834033,0.5778500434,0.5768934907,1.772e-07,0.0001714356,0.0,0.0,0.0,0.0015313812,6.36986e-05,-2.85743e-05,4.4276e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_raw_ortho_entropy_mid_g015_b04dca03.csv,energyfront,prob_raw_ortho,entropy_mid,0.015,0.5778338825,0.5778338825,0.5778500905,0.5768971753,1.493e-07,0.0005621241,0.0,0.0,0.0,0.0015187167,6.37079e-05,-2.85127e-05,4.4381e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ortho_strength_entropy_g015_52b006a1.csv,energyfront,prob_bad_raw_ortho,strength_entropy,0.015,0.5778342195,0.5778380416,0.5778501453,0.5768974036,2.319e-07,0.0007865302,3.822e-06,0.0,0.0,0.0015130817,4.68417e-05,-4.24053e-05,7.4156e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ord_ortho_ones_g015_8f124681.csv,efmicro5,prob_bad_raw_ord_ortho,ones,0.015,0.5778380186,0.5778380186,0.5778501622,0.576899389,1.339e-07,0.0004650958,0.0,0.0,0.0,0.0015247058,4.76441e-05,-3.70577e-05,-1.1124e-05
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ord_ortho_entropy_mid_g015_0e8b26c0.csv,compatband,prob_bad_raw_ord_ortho,entropy_mid,0.015,0.577837951,0.5778400466,0.5778507424,0.5769010478,1.221e-07,0.000488972,0.0,0.0,2.0957e-06,0.0015146436,4.18051e-05,-2.90254e-05,-9.9271e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ortho_entropy_mid_g015_3bc27348.csv,siggate,prob_bad_raw_ortho,entropy_mid,0.015,0.5778351721,0.5778351721,0.5778509459,0.5768872682,1.71e-07,-5.1606e-06,0.0,0.0,0.0,0.0015258339,6.30851e-05,-5.72617e-05,-4.0025e-06
submission_raw05_jepa_public6q3s4corr_energyfront_prob_raw_ortho_strength_entropy_g015_937adef7.csv,energyfront,prob_raw_ortho,strength_entropy,0.015,0.5778342991,0.5778388699,0.5778510588,0.5768972926,2.381e-07,0.0006136122,4.5709e-06,0.0,0.0,0.0015131705,4.75283e-05,-2.50097e-05,1.19525e-05
submission_raw05_jepa_public6q3s4corr_siggate_prob_bad_raw_ord_ortho_ones_g015_fbe13227.csv,siggate,prob_bad_raw_ord_ortho,ones,0.015,0.5778393602,0.5778393602,0.577851288,0.5768935218,1.307e-07,6.6045e-06,0.0,0.0,0.0,0.0015180782,4.76982e-05,-3.71239e-05,-1.11501e-05
submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ortho_ones_g015_ff018ee7.csv,compatband,prob_bad_raw_ortho,ones,0.015,0.5778331145,0.5778331145,0.5778513045,0.576894375,1.675e-07,0.0004990734,0.0,0.0,0.0,0.001529118,7.17618e-05,-6.32418e-05,-5.0589e-06
submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ortho_ones_g015_1e1c2ea8.csv,efmicro3,prob_bad_raw_ortho,ones,0.015,0.5778331215,0.5778331215,0.5778513099,0.5768953166,1.622e-07,0.0004950061,0.0,0.0,0.0,0.0015264287,7.17636e-05,-6.32515e-05,-5.0629e-06
submission_raw05_jepa_public6q3s4corr_siggate_prob_raw_ortho_entropy_mid_g015_b12ee150.csv,siggate,prob_raw_ortho,entropy_mid,0.015,0.5778353432,0.5778353432,0.5778514256,0.5768876154,1.74e-07,-0.0002860196,0.0,0.0,0.0,0.0015247626,6.37574e-05,-2.87566e-05,4.3814e-06
submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ortho_ones_g015_489be7fd.csv,efmicro5,prob_bad_raw_ortho,ones,0.015,0.5778332572,0.5778332572,0.5778514321,0.5768923555,1.756e-07,0.0004650958,0.0,0.0,0.0,0.0015360118,7.17693e-05,-6.32243e-05,-5.0489e-06
```
