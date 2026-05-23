# Moonshot masked validation report

## Overall mean logloss
                 candidate     mean      std  count  delta_vs_anchor  delta_vs_w03proxy
      moon_validated_block 0.649642 0.008421     11        -0.011930          -0.007254
 moon_raw_all_antifix_q1s4 0.650206 0.008661     11        -0.011365          -0.006689
moon_validated_block_sharp 0.650740 0.008755     11        -0.010831          -0.006155
 moon_optimized_keep_s4raw 0.651038 0.009178     11        -0.010534          -0.005858
 moon_optimized_targetwise 0.651089 0.008349     11        -0.010483          -0.005807
  moon_graph_raw_sharpened 0.653411 0.010037     11        -0.008161          -0.003485
   moon_graph_raw_all_noq3 0.654734 0.008185     11        -0.006838          -0.002162
moon_graph_raw_noq3_q2half 0.655825 0.008299     11        -0.005746          -0.001070
            w03_noq3_q2w02 0.656896 0.005737     11        -0.004676           0.000000
     moon_family_best_only 0.661501 0.010743     11        -0.000071           0.004605
           anchor_w02_noq3 0.661572 0.005889     11         0.000000           0.004676

## By target mean logloss
candidate  anchor_w02_noq3  moon_family_best_only  moon_graph_raw_all_noq3  moon_graph_raw_noq3_q2half  moon_graph_raw_sharpened  moon_optimized_keep_s4raw  moon_optimized_targetwise  moon_raw_all_antifix_q1s4  moon_validated_block  moon_validated_block_sharp  w03_noq3_q2w02
target                                                                                                                                                                                                                                                                             
Q1                0.666570               0.683496                 0.683496                    0.683496                  0.682747                   0.670633                   0.670633                   0.671386              0.666570                    0.670633        0.665369
Q2                0.694205               0.715623                 0.668257                    0.675897                  0.676177                   0.668257                   0.668257                   0.668257              0.668257                    0.667001        0.694205
Q3                0.735700               0.735700                 0.735700                    0.735700                  0.735700                   0.735700                   0.735700                   0.735700              0.735700                    0.735700        0.735700
S1                0.625581               0.608232                 0.608232                    0.608232                  0.610190                   0.608232                   0.608232                   0.608232              0.608232                    0.608785        0.616558
S2                0.634710               0.622664                 0.622664                    0.622664                  0.619588                   0.619588                   0.619588                   0.619588              0.619588                    0.619616        0.624589
S3                0.614320               0.599165                 0.599165                    0.599165                  0.589231                   0.589231                   0.589231                   0.589231              0.589231                    0.587470        0.604150
S4                0.659916               0.665624                 0.665624                    0.665624                  0.660245                   0.665624                   0.665978                   0.659050              0.659916                    0.665978        0.657699

## Mean movement vs anchor
                 candidate target  mean_abs_vs_anchor
     moon_family_best_only     Q1            0.061624
     moon_family_best_only     Q2            0.022029
     moon_family_best_only     Q3            0.000000
     moon_family_best_only     S1            0.178087
     moon_family_best_only     S2            0.153237
     moon_family_best_only     S3            0.157704
     moon_family_best_only     S4            0.084159
   moon_graph_raw_all_noq3     Q1            0.061624
   moon_graph_raw_all_noq3     Q2            0.072643
   moon_graph_raw_all_noq3     Q3            0.000000
   moon_graph_raw_all_noq3     S1            0.178087
   moon_graph_raw_all_noq3     S2            0.153237
   moon_graph_raw_all_noq3     S3            0.157704
   moon_graph_raw_all_noq3     S4            0.084159
moon_graph_raw_noq3_q2half     Q1            0.061624
moon_graph_raw_noq3_q2half     Q2            0.036322
moon_graph_raw_noq3_q2half     Q3            0.000000
moon_graph_raw_noq3_q2half     S1            0.178087
moon_graph_raw_noq3_q2half     S2            0.153237
moon_graph_raw_noq3_q2half     S3            0.157704
moon_graph_raw_noq3_q2half     S4            0.084159
  moon_graph_raw_sharpened     Q1            0.072842
  moon_graph_raw_sharpened     Q2            0.035249
  moon_graph_raw_sharpened     Q3            0.000000
  moon_graph_raw_sharpened     S1            0.187485
  moon_graph_raw_sharpened     S2            0.161150
  moon_graph_raw_sharpened     S3            0.164598
  moon_graph_raw_sharpened     S4            0.092142
 moon_optimized_keep_s4raw     Q1            0.015277
 moon_optimized_keep_s4raw     Q2            0.072643
 moon_optimized_keep_s4raw     Q3            0.000000
 moon_optimized_keep_s4raw     S1            0.178087
 moon_optimized_keep_s4raw     S2            0.161150
 moon_optimized_keep_s4raw     S3            0.164598
 moon_optimized_keep_s4raw     S4            0.084159
 moon_optimized_targetwise     Q1            0.015277
 moon_optimized_targetwise     Q2            0.072643
 moon_optimized_targetwise     Q3            0.000000
 moon_optimized_targetwise     S1            0.178087
 moon_optimized_targetwise     S2            0.161150
 moon_optimized_targetwise     S3            0.164598
 moon_optimized_targetwise     S4            0.018724
 moon_raw_all_antifix_q1s4     Q1            0.027238
 moon_raw_all_antifix_q1s4     Q2            0.072643
 moon_raw_all_antifix_q1s4     Q3            0.000000
 moon_raw_all_antifix_q1s4     S1            0.178087
 moon_raw_all_antifix_q1s4     S2            0.161150
 moon_raw_all_antifix_q1s4     S3            0.164598
 moon_raw_all_antifix_q1s4     S4            0.036072
      moon_validated_block     Q1            0.000000
      moon_validated_block     Q2            0.072643
      moon_validated_block     Q3            0.000000
      moon_validated_block     S1            0.178087
      moon_validated_block     S2            0.161150
      moon_validated_block     S3            0.164598
      moon_validated_block     S4            0.000000
moon_validated_block_sharp     Q1            0.015277
moon_validated_block_sharp     Q2            0.077260
moon_validated_block_sharp     Q3            0.000000
moon_validated_block_sharp     S1            0.183625
moon_validated_block_sharp     S2            0.163698
moon_validated_block_sharp     S3            0.166861
moon_validated_block_sharp     S4            0.018724
            w03_noq3_q2w02     Q1            0.007639
            w03_noq3_q2w02     Q2            0.000000
            w03_noq3_q2w02     Q3            0.000000
            w03_noq3_q2w02     S1            0.017505
            w03_noq3_q2w02     S2            0.015867
            w03_noq3_q2w02     S3            0.017106
            w03_noq3_q2w02     S4            0.009362