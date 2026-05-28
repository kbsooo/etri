# Public LB Inverse Mask Audit 7-Anchor

This is the public inverse audit after adding `submission_frontier_cvjepa_refine_a2c8d2c8.csv` public `0.577439321` as a seventh anchor.

## Actual Public Constraints

```
              key                                                            file  public_lb  delta_vs_stage2  weight
           stage2   submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv   0.577945         0.000000     0.0
        anchor578   submission_hybrid_0p578_logit_after_subject_final9_strict.csv   0.578427         0.000482     1.0
        ordinal_q submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv   0.578303         0.000358     1.0
            raw05         submission_raw_timeline_jepa_rescue_strict_scale0p5.csv   0.577526        -0.000419     1.8
      cvjepa_a2c8                  submission_frontier_cvjepa_refine_a2c8d2c8.csv   0.577439        -0.000506     2.0
jepa_bad_residual                       submission_jepa_latent_residual_probe.csv   0.581227         0.003282     0.9
      jepa_bad_q2                             submission_jepa_latent_q2_w0p45.csv   0.579801         0.001856     0.9
```

## Top Inverse-Fit Masks

```
                                                      scenario_file          mask_kind       mask_name  rows  inverse_fit_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  raw05_a2c8_sign_ok  pred_delta_raw05  pred_delta_cvjepa_a2c8  pred_delta_anchor578  pred_delta_ordinal_q                                         top_blocks
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv     single_subject            id01    27           0.950670           0.740128       0.000877           1.000000                True         -0.000002               -0.000238              0.000790              0.000619                              id01_b2:13;id01_b4:12
                   submission_public_minimaxens_r08_a10_h869363.csv       global_order prefix_frac0.20    50           1.001082           0.776301       0.000967           1.000000                True         -0.000002               -0.000192              0.000964              0.000456         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_minimaxens_r07_a12_h981086.csv       global_order prefix_frac0.20    50           1.001389           0.776536       0.000967           1.000000                True         -0.000002               -0.000192              0.000965              0.000456         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_minimaxens_r05_a10_h506746.csv       global_order prefix_frac0.20    50           1.002168           0.777125       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                    submission_public_minimaxens_r01_a6_h422045.csv       global_order prefix_frac0.20    50           1.002330           0.777253       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_minimaxens_r03_a12_h597891.csv       global_order prefix_frac0.20    50           1.002616           0.777468       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_universeens_u80_r04_8b6653a9.csv       global_order prefix_frac0.20    50           1.002898           0.777691       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                    submission_public_minimaxens_r06_a9_h512521.csv       global_order prefix_frac0.20    50           1.003217           0.777936       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_universeens_u80_r02_4c0e785c.csv       global_order prefix_frac0.20    50           1.003217           0.777936       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_minimaxens_r02_a13_h745897.csv       global_order prefix_frac0.20    50           1.003292           0.777994       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_minimaxens_r04_a11_h082844.csv       global_order prefix_frac0.20    50           1.003372           0.778056       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_universeens_u80_r03_72e58bdb.csv       global_order prefix_frac0.20    50           1.003372           0.778056       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_universeens_u80_r01_07c571e6.csv       global_order prefix_frac0.20    50           1.003850           0.778423       0.000968           1.000000                True         -0.000002               -0.000192              0.000969              0.000459         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv       global_order prefix_frac0.20    50           1.013172           0.785176       0.000987           1.000000                True         -0.000002               -0.000185              0.000984              0.000410         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv     single_subject            id01    27           1.061985           0.825164       0.000875           1.000000                True         -0.000002               -0.000237              0.000991              0.000694                              id01_b2:13;id01_b4:12
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv       global_order prefix_frac0.20    50           1.153100           0.892140       0.000987           1.000000                True         -0.000002               -0.000184              0.001222              0.000506         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep114    50           1.174556           0.835066       0.000639           0.736842                True         -0.000028               -0.000246             -0.000056             -0.000105  id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep192    75           1.204448           0.698653       0.000466           0.763158               False          0.000054               -0.000108              0.000368              0.000338  id02_b4:7;id09_b2:7;id01_b4:5;id10_b2:5;id07_b4:5
                   submission_public_entropyproj_public2d0_g100.csv       global_order    rowmod4_rem3    62           1.276996           0.753367       0.000406           0.763158               False          0.000065               -0.000142              0.000196              0.000109  id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep115    50           1.280861           0.752328       0.000611           0.763158               False          0.000083               -0.000109              0.000405              0.000201  id01_b2:7;id03_b2:4;id10_b2:3;id03_b4:3;id10_b4:3
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep077    75           1.289739           0.765954       0.000508           0.763158               False          0.000104               -0.000087              0.000281              0.000322  id01_b2:7;id07_b4:6;id01_b4:5;id02_b2:5;id08_b4:4
                   submission_public_entropyproj_public2d0_g075.csv     single_subject            id01    27           1.298420           0.742728       0.000881           0.763158               False          0.000003               -0.000236              0.000778              0.000620                              id01_b2:13;id01_b4:12
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv     single_subject            id01    27           1.298420           0.742728       0.000881           0.763158               False          0.000003               -0.000236              0.000778              0.000620                              id01_b2:13;id01_b4:12
                   submission_public_entropyproj_public2d0_g100.csv subject_contiguous frac0.25_rep150    64           1.306583           0.776795       0.000493           0.763158               False          0.000094               -0.000105              0.000524              0.000141  id07_b2:8;id01_b2:7;id09_b2:7;id04_b6:6;id10_b4:6
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep040   100           1.317953           0.790542       0.000517           0.763158               False          0.000107               -0.000042              0.000473              0.000486 id09_b2:10;id02_b4:8;id09_b4:8;id01_b2:8;id02_b2:7
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep056    75           1.324105           0.784634       0.000536           0.763158               False          0.000066               -0.000117              0.000020              0.000291  id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
                   submission_public_maskaware_t65_r08_7f7fa3e2.csv     single_subject            id01    27           1.333676           0.770191       0.000881           0.763158               False          0.000007               -0.000229              0.000799              0.000666                              id01_b2:13;id01_b4:12
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep221    75           1.335562           0.803054       0.000579           0.763158               False          0.000115               -0.000028              0.000437              0.000308  id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep132   100           1.336283           0.803972       0.000465           0.763158               False          0.000108               -0.000076              0.000771              0.000198  id02_b2:8;id02_b4:7;id01_b2:6;id07_b2:6;id10_b4:6
                   submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep139    50           1.340002           0.803352       0.000568           0.763158               False          0.000121               -0.000073              0.000697              0.000480  id07_b4:6;id09_b2:4;id02_b4:3;id03_b4:3;id04_b6:2
```

## Raw05 + A2C8 Sign-Compatible Masks

raw05+a2c8-compatible rows: `512`; all-sign-compatible rows: `512`.

```
                                                   scenario_file      mask_kind                   mask_name  rows  inverse_fit_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  raw05_a2c8_sign_ok  pred_delta_raw05  pred_delta_cvjepa_a2c8  pred_delta_anchor578  pred_delta_ordinal_q                                        top_blocks
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject                        id01    27           0.950670           0.740128       0.000877           1.000000                True         -0.000002               -0.000238              0.000790              0.000619                             id01_b2:13;id01_b4:12
                submission_public_minimaxens_r08_a10_h869363.csv   global_order             prefix_frac0.20    50           1.001082           0.776301       0.000967           1.000000                True         -0.000002               -0.000192              0.000964              0.000456        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_minimaxens_r07_a12_h981086.csv   global_order             prefix_frac0.20    50           1.001389           0.776536       0.000967           1.000000                True         -0.000002               -0.000192              0.000965              0.000456        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_minimaxens_r05_a10_h506746.csv   global_order             prefix_frac0.20    50           1.002168           0.777125       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order             prefix_frac0.20    50           1.002330           0.777253       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_minimaxens_r03_a12_h597891.csv   global_order             prefix_frac0.20    50           1.002616           0.777468       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000457        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order             prefix_frac0.20    50           1.002898           0.777691       0.000967           1.000000                True         -0.000002               -0.000192              0.000967              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order             prefix_frac0.20    50           1.003217           0.777936       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
              submission_public_universeens_u80_r02_4c0e785c.csv   global_order             prefix_frac0.20    50           1.003217           0.777936       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_minimaxens_r02_a13_h745897.csv   global_order             prefix_frac0.20    50           1.003292           0.777994       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_minimaxens_r04_a11_h082844.csv   global_order             prefix_frac0.20    50           1.003372           0.778056       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
              submission_public_universeens_u80_r03_72e58bdb.csv   global_order             prefix_frac0.20    50           1.003372           0.778056       0.000967           1.000000                True         -0.000002               -0.000192              0.000968              0.000458        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
              submission_public_universeens_u80_r01_07c571e6.csv   global_order             prefix_frac0.20    50           1.003850           0.778423       0.000968           1.000000                True         -0.000002               -0.000192              0.000969              0.000459        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv   global_order             prefix_frac0.20    50           1.013172           0.785176       0.000987           1.000000                True         -0.000002               -0.000185              0.000984              0.000410        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
   submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv single_subject                        id01    27           1.061985           0.825164       0.000875           1.000000                True         -0.000002               -0.000237              0.000991              0.000694                             id01_b2:13;id01_b4:12
   submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv   global_order             prefix_frac0.20    50           1.153100           0.892140       0.000987           1.000000                True         -0.000002               -0.000184              0.001222              0.000506        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_entropyproj_public2d0_g100.csv    random_rows             frac0.20_rep114    50           1.174556           0.835066       0.000639           0.736842                True         -0.000028               -0.000246             -0.000056             -0.000105 id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
                submission_public_entropyproj_public2d0_g100.csv   global_order             prefix_frac0.20    50           1.681051           1.211845       0.001027           0.736842                True         -0.000052               -0.000299             -0.000166             -0.000566        id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
                submission_public_entropyproj_public2d0_g100.csv single_subject                        id01    27           1.807787           1.312292       0.000966           0.736842                True         -0.000076               -0.000391             -0.000324             -0.000662                             id01_b2:13;id01_b4:12
                  submission_frontier_cvjepa_refine_a2c8d2c8.csv  subject_order per_subject_prefix_frac0.25    64           4.236531           3.264028       0.001539           1.000000                True         -0.000304               -0.000316              0.004160              0.002050 id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
                  submission_frontier_cvjepa_refine_fdba6a57.csv  subject_order per_subject_prefix_frac0.25    64           4.236531           3.264028       0.001539           1.000000                True         -0.000304               -0.000316              0.004160              0.002050 id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
                  submission_frontier_cvjepa_refine_5f76d74d.csv  subject_order per_subject_prefix_frac0.25    64           4.236635           3.264108       0.001539           1.000000                True         -0.000304               -0.000316              0.004160              0.002050 id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
                  submission_frontier_cvjepa_refine_cf0478ca.csv  subject_order per_subject_prefix_frac0.25    64           4.236635           3.264108       0.001539           1.000000                True         -0.000304               -0.000316              0.004160              0.002050 id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
                  submission_frontier_cvjepa_refine_b80b6231.csv  subject_order per_subject_prefix_frac0.25    64           4.236650           3.264120       0.001539           1.000000                True         -0.000304               -0.000316              0.004160              0.002050 id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
```

## Mask Kind Summary

```
         mask_kind    n  best_rank  best_score  mean_top_score  raw05_a2c8_ok_rate  all_sign_ok_rate  mean_rows  mean_subject_entropy
    single_subject   59          1    0.950670        1.546849            0.050847          0.033898  29.457627              0.000000
      global_order   72          2    1.001082        1.528567            0.208333          0.194444  68.388889              0.983243
       random_rows 1327         17    1.174556        1.713858            0.000754          0.000000 108.440090              0.980049
subject_contiguous  581         24    1.306583        1.715676            0.000000          0.000000 108.950086              0.993817
     subject_order    8        202    1.557017        1.684167            0.000000          0.000000 110.000000              0.993818
               all    1        532    1.647287        1.647287            0.000000          0.000000 250.000000              0.994313
```

## Scenario Summary

```
                                                      scenario_file    n  best_rank  best_score  mean_top_score  raw05_a2c8_ok_rate  all_sign_ok_rate
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv   14          1    0.950670        1.682830            0.142857          0.142857
                   submission_public_minimaxens_r08_a10_h869363.csv   21          2    1.001082        1.714502            0.047619          0.047619
                   submission_public_minimaxens_r07_a12_h981086.csv   21          3    1.001389        1.714671            0.047619          0.047619
                   submission_public_minimaxens_r05_a10_h506746.csv   21          4    1.002168        1.715202            0.047619          0.047619
                    submission_public_minimaxens_r01_a6_h422045.csv   21          5    1.002330        1.715955            0.047619          0.047619
                   submission_public_minimaxens_r03_a12_h597891.csv   21          6    1.002616        1.715651            0.047619          0.047619
                 submission_public_universeens_u80_r04_8b6653a9.csv   21          7    1.002898        1.715766            0.047619          0.047619
                    submission_public_minimaxens_r06_a9_h512521.csv   21          8    1.003217        1.715988            0.047619          0.047619
                 submission_public_universeens_u80_r02_4c0e785c.csv   21          9    1.003217        1.715988            0.047619          0.047619
                   submission_public_minimaxens_r02_a13_h745897.csv   21         10    1.003292        1.716326            0.047619          0.047619
                   submission_public_minimaxens_r04_a11_h082844.csv   21         11    1.003372        1.716292            0.047619          0.047619
                 submission_public_universeens_u80_r03_72e58bdb.csv   21         12    1.003372        1.716292            0.047619          0.047619
                 submission_public_universeens_u80_r01_07c571e6.csv   21         13    1.003850        1.717039            0.047619          0.047619
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv    3         15    1.061985        1.246667            0.666667          0.666667
                   submission_public_entropyproj_public2d0_g100.csv 1527         17    1.174556        1.697331            0.001965          0.000000
                   submission_public_entropyproj_public2d0_g075.csv   25         22    1.298420        1.734885            0.000000          0.000000
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv   25         23    1.298420        1.734885            0.000000          0.000000
                   submission_public_maskaware_t65_r08_7f7fa3e2.csv   21         27    1.333676        1.725516            0.000000          0.000000
                   submission_public_maskaware_t50_r05_fb7b695a.csv   15         31    1.340208        1.715168            0.000000          0.000000
                   submission_public_maskaware_t50_r06_8d5b4fe1.csv   15         35    1.343858        1.710994            0.000000          0.000000
                   submission_public_maskaware_t65_r07_768f6df0.csv   24         39    1.349585        1.736197            0.000000          0.000000
                   submission_public_maskaware_t50_r04_6761fb38.csv   18         42    1.357397        1.721191            0.000000          0.000000
                   submission_public_maskaware_t65_r09_35ff9a82.csv   16         43    1.358524        1.729445            0.000000          0.000000
                   submission_public_maskaware_t80_r10_18d78615.csv   21         68    1.388589        1.728358            0.000000          0.000000
   submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv   11         79    1.407423        1.729349            0.000000          0.000000
                       submission_public_entropyproj_proj0_g075.csv   19         83    1.412034        1.736783            0.000000          0.000000
                   submission_public_maskaware_t80_r11_544844af.csv   11        124    1.464967        1.736742            0.000000          0.000000
                   submission_public_maskaware_t80_r12_dcfaabba.csv    8        131    1.475590        1.720294            0.000000          0.000000
                 submission_public_universeens_u65_r02_c0e2b2f1.csv    6        175    1.531730        1.689130            0.000000          0.000000
                 submission_public_universeens_u65_r01_365a84a6.csv    6        361    1.612614        1.754752            0.000000          0.000000
                 submission_public_universeens_u65_r04_dc6f3303.csv    3        431    1.628523        1.737175            0.000000          0.000000
                 submission_public_universeens_u65_r03_cf973915.csv    4        438    1.630067        1.753100            0.000000          0.000000
                   submission_public_maskaware_t35_r02_517540cc.csv    2       1048    1.724788        1.759370            0.000000          0.000000
                    submission_public_maskplausens_r05_e8325bb7.csv    1       1981    1.870952        1.870952            0.000000          0.000000
                    submission_public_maskplausens_r04_161f5469.csv    1       2033    1.878266        1.878266            0.000000          0.000000
```

## Target Delta Decomposition

```
                                                   scenario_file      mask_kind       mask_name target  pred_delta_raw05  pred_delta_cvjepa_a2c8  pred_delta_anchor578  pred_delta_jepa_bad_residual
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     Q1          0.000412                0.000326              0.003891                      0.000684
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     Q2          0.000000               -0.000001              0.001565                      0.000753
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     Q3         -0.000675               -0.001667             -0.002587                      0.000492
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     S1          0.000240                0.000265              0.000096                      0.000924
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     S2         -0.000293               -0.000607             -0.001335                      0.003807
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     S3          0.000311                0.000050             -0.000995                      0.002965
submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv single_subject            id01     S4         -0.000007               -0.000030              0.004893                      0.000125
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003944                      0.000721
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002624                      0.000865
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001278             -0.001930                      0.000066
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000047                      0.001257
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000212             -0.000070                      0.002137
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     S3          0.000089               -0.000234             -0.001229                      0.002152
                submission_public_minimaxens_r08_a10_h869363.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003365                      0.000092
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003944                      0.000721
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002626                      0.000866
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001278             -0.001930                      0.000066
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000047                      0.001257
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000212             -0.000071                      0.002137
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     S3          0.000089               -0.000234             -0.001227                      0.002152
                submission_public_minimaxens_r07_a12_h981086.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003365                      0.000092
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003943                      0.000721
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002639                      0.000868
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001278             -0.001930                      0.000066
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000047                      0.001257
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000213             -0.000075                      0.002136
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     S3          0.000089               -0.000233             -0.001218                      0.002151
                submission_public_minimaxens_r05_a10_h506746.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003363                      0.000093
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003947                      0.000720
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002634                      0.000867
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001277             -0.001928                      0.000066
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000048                      0.001256
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000212             -0.000073                      0.002137
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     S3          0.000089               -0.000234             -0.001228                      0.002152
                 submission_public_minimaxens_r01_a6_h422045.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003367                      0.000092
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003943                      0.000721
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002639                      0.000868
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001277             -0.001930                      0.000066
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000047                      0.001257
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     S2         -0.000071               -0.000213             -0.000077                      0.002136
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     S3          0.000090               -0.000233             -0.001213                      0.002150
                submission_public_minimaxens_r03_a12_h597891.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003363                      0.000093
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003944                      0.000721
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002636                      0.000867
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001277             -0.001929                      0.000066
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000046                      0.001258
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000212             -0.000072                      0.002136
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     S3          0.000089               -0.000233             -0.001216                      0.002151
              submission_public_universeens_u80_r04_8b6653a9.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003364                      0.000093
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003944                      0.000721
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002638                      0.000868
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001277             -0.001929                      0.000066
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000046                      0.001258
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     S2         -0.000070               -0.000212             -0.000072                      0.002136
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     S3          0.000090               -0.000233             -0.001214                      0.002150
                 submission_public_minimaxens_r06_a9_h512521.csv   global_order prefix_frac0.20     S4          0.000089                0.000067              0.003363                      0.000093
              submission_public_universeens_u80_r02_4c0e785c.csv   global_order prefix_frac0.20     Q1          0.000184                0.000124              0.003944                      0.000721
              submission_public_universeens_u80_r02_4c0e785c.csv   global_order prefix_frac0.20     Q2          0.000000               -0.000001              0.002638                      0.000868
              submission_public_universeens_u80_r02_4c0e785c.csv   global_order prefix_frac0.20     Q3         -0.000493               -0.001277             -0.001929                      0.000066
              submission_public_universeens_u80_r02_4c0e785c.csv   global_order prefix_frac0.20     S1          0.000188                0.000190              0.000046                      0.001258
```

## Candidate Re-Ranking By 7-Anchor Inverse Masks

```
                                                               file  inverse7_candidate_score  inverse7_weighted_expected  inverse7_weighted_regret  inverse7_p90_regret  inverse7_win_rate_best_eps1e4
                   submission_public_entropyproj_public2d0_g075.csv                  0.577615                    0.577419                  0.000056             0.000104                        0.86875
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv                  0.577615                    0.577419                  0.000056             0.000104                        0.86875
                   submission_public_maskaware_t65_r07_768f6df0.csv                  0.577619                    0.577420                  0.000057             0.000105                        0.78750
                   submission_public_maskaware_t65_r08_7f7fa3e2.csv                  0.577625                    0.577422                  0.000058             0.000107                        0.73125
                       submission_public_entropyproj_proj0_g100.csv                  0.577633                    0.577420                  0.000057             0.000121                        0.63125
                   submission_public_maskaware_t50_r04_6761fb38.csv                  0.577635                    0.577424                  0.000061             0.000112                        0.55625
                   submission_public_entropyproj_public2d0_g100.csv                  0.577636                    0.577419                  0.000056             0.000128                        0.58750
                       submission_public_entropyproj_proj0_g075.csv                  0.577644                    0.577427                  0.000063             0.000113                        0.56250
                   submission_public_maskaware_t80_r10_18d78615.csv                  0.577660                    0.577431                  0.000067             0.000118                        0.54375
                   submission_public_maskaware_t50_r06_8d5b4fe1.csv                  0.577680                    0.577427                  0.000064             0.000118                        0.49375
                   submission_public_maskaware_t50_r05_fb7b695a.csv                  0.577682                    0.577427                  0.000064             0.000118                        0.49375
                   submission_public_minimaxens_r08_a10_h869363.csv                  0.577787                    0.577429                  0.000066             0.000126                        0.47500
                   submission_public_minimaxens_r07_a12_h981086.csv                  0.577787                    0.577429                  0.000066             0.000126                        0.47500
                 submission_public_universeens_u80_r04_8b6653a9.csv                  0.577788                    0.577429                  0.000066             0.000126                        0.47500
                   submission_public_minimaxens_r05_a10_h506746.csv                  0.577788                    0.577429                  0.000066             0.000126                        0.47500
                    submission_public_minimaxens_r06_a9_h512521.csv                  0.577788                    0.577429                  0.000066             0.000126                        0.47500
                 submission_public_universeens_u80_r02_4c0e785c.csv                  0.577788                    0.577429                  0.000066             0.000126                        0.47500
                   submission_public_minimaxens_r03_a12_h597891.csv                  0.577788                    0.577429                  0.000066             0.000127                        0.47500
                   submission_public_minimaxens_r02_a13_h745897.csv                  0.577788                    0.577429                  0.000066             0.000127                        0.47500
                   submission_public_minimaxens_r04_a11_h082844.csv                  0.577788                    0.577429                  0.000066             0.000127                        0.47500
                 submission_public_universeens_u80_r03_72e58bdb.csv                  0.577788                    0.577429                  0.000066             0.000127                        0.47500
                    submission_public_minimaxens_r01_a6_h422045.csv                  0.577789                    0.577429                  0.000066             0.000127                        0.47500
                 submission_public_universeens_u80_r01_07c571e6.csv                  0.577789                    0.577429                  0.000066             0.000127                        0.47500
                   submission_public_maskaware_t65_r09_35ff9a82.csv                  0.577811                    0.577435                  0.000072             0.000132                        0.47500
                 submission_public_universeens_u65_r02_c0e2b2f1.csv                  0.577860                    0.577445                  0.000082             0.000157                        0.47500
                 submission_public_universeens_u65_r01_365a84a6.csv                  0.577889                    0.577452                  0.000089             0.000166                        0.47500
   submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv                  0.577907                    0.577458                  0.000095             0.000165                        0.47500
                   submission_public_maskaware_t80_r11_544844af.csv                  0.577913                    0.577460                  0.000096             0.000168                        0.47500
                 submission_public_universeens_u65_r04_dc6f3303.csv                  0.577928                    0.577462                  0.000099             0.000178                        0.47500
                   submission_public_maskaware_t80_r12_dcfaabba.csv                  0.577928                    0.577463                  0.000100             0.000175                        0.47500
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv                  0.577931                    0.577460                  0.000096             0.000190                        0.47500
                 submission_public_universeens_u65_r03_cf973915.csv                  0.577936                    0.577463                  0.000100             0.000184                        0.47500
                   submission_public_maskaware_t35_r02_517540cc.csv                  0.578091                    0.577498                  0.000135             0.000245                        0.47500
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv                  0.578100                    0.577499                  0.000136             0.000254                        0.47500
                    submission_public_maskplausens_r05_e8325bb7.csv                  0.578104                    0.577503                  0.000140             0.000242                        0.47500
                    submission_public_maskplausens_r04_161f5469.csv                  0.578110                    0.577505                  0.000142             0.000243                        0.47500
                   submission_public_maskaware_t35_r01_2d5fa124.csv                  0.578342                    0.577558                  0.000195             0.000334                        0.47500
                   submission_public_maskaware_t35_r03_cac1b720.csv                  0.578499                    0.577571                  0.000208             0.000361                        0.45625
                    submission_public_maskplausens_r01_3de9be39.csv                  0.578538                    0.577542                  0.000179             0.000286                        0.41875
                   submission_public_entropyproj_public2d0_g050.csv                  0.579188                    0.577609                  0.000246             0.000417                        0.35000
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g050.csv                  0.579188                    0.577609                  0.000246             0.000417                        0.35000
                    submission_public_maskplausens_r03_40f65e60.csv                  0.579218                    0.577556                  0.000193             0.000302                        0.29375
                    submission_public_maskplausens_r02_dc594c28.csv                  0.579374                    0.577564                  0.000200             0.000311                        0.26875
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g050.csv                  0.580335                    0.577642                  0.000279             0.000477                        0.15000
   submission_public_entropytm_public2d0_q1_q2_q3_s1_s3_s4_g075.csv                  0.580374                    0.577577                  0.000214             0.000304                        0.07500
      submission_public_entropytm_public2d0_q1_q2_q3_s3_s4_g075.csv                  0.580562                    0.577617                  0.000254             0.000385                        0.07500
                 submission_public_universeens_u50_r04_f6ae8481.csv                  0.580628                    0.577607                  0.000244             0.000390                        0.05625
      submission_public_entropytm_public2d0_q1_q3_s1_s3_s4_g075.csv                  0.580637                    0.577616                  0.000253             0.000369                        0.05625
   submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g050.csv                  0.580800                    0.577644                  0.000280             0.000467                        0.05625
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g050.csv                  0.581010                    0.577677                  0.000313             0.000526                        0.04375
```

## Candidate Re-Ranking By Raw05+A2C8-Compatible Masks

```
                                                                                                   file  inverse7_candidate_score  inverse7_weighted_expected  inverse7_weighted_regret  inverse7_p90_regret  inverse7_win_rate_best_eps1e4
            submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ortho_ones_g020_7e46b3e4.csv                  0.577556                    0.575463                  0.000334             0.001707                        0.88125
               submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ortho_ones_g020_9bbd99ba.csv                  0.577556                    0.575463                  0.000334             0.001707                        0.88125
             submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ortho_ones_g020_492bdbc6.csv                  0.577556                    0.575463                  0.000334             0.001707                        0.88125
               submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ortho_ones_g020_5bd98a74.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                submission_raw05_jepa_public6q3s4corr_energyfront_prob_raw_ortho_ones_g020_a0c109a7.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                   submission_raw05_jepa_public6q3s4corr_efmicro3_prob_raw_ortho_ones_g020_ac8c2af3.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                 submission_raw05_jepa_public6q3s4corr_compatband_prob_raw_ortho_ones_g020_5ebef9cc.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_9d69b9bb.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_80e9f7f8.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_ab3d20e1.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_23d83f3c.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
                   submission_raw05_jepa_public6q3s4corr_efmicro5_prob_raw_ortho_ones_g020_a38a6762.csv                  0.577556                    0.575463                  0.000334             0.001708                        0.88125
submission_raw05_jepa_public6q3s4corr_energyfront_prob_raw_ortho_positive_entropy_mid_g020_2673b83a.csv                  0.577557                    0.575463                  0.000334             0.001708                        0.88125
     submission_raw05_jepa_public6q3s4corr_energyfront_prob_bad_raw_ortho_entropy_mid_g020_5895110b.csv                  0.577557                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_434452db.csv                  0.577557                    0.575463                  0.000334             0.001708                        0.88125
        submission_raw05_jepa_public6q3s4corr_efmicro3_prob_bad_raw_ortho_entropy_mid_g020_70a7deca.csv                  0.577557                    0.575463                  0.000334             0.001708                        0.88125
                                                         submission_frontier_cvjepa_refine_cc7fec9f.csv                  0.577557                    0.575463                  0.000334             0.001708                        0.88125
      submission_raw05_jepa_public6q3s4corr_compatband_prob_bad_raw_ortho_entropy_mid_g020_9d9c6fb6.csv                  0.577557                    0.575463                  0.000334             0.001709                        0.88125
        submission_raw05_jepa_public6q3s4corr_efmicro5_prob_bad_raw_ortho_entropy_mid_g020_061ae534.csv                  0.577557                    0.575463                  0.000334             0.001709                        0.88125
         submission_raw05_jepa_public6q3s4corr_energyfront_prob_raw_ortho_entropy_mid_g020_b51232c8.csv                  0.577557                    0.575463                  0.000334             0.001709                        0.88125
            submission_raw05_jepa_public6q3s4corr_efmicro3_prob_raw_ortho_entropy_mid_g020_10b709ca.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
              submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_entropy_g015_c8e87a92.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
          submission_raw05_jepa_public6q3s4corr_compatband_prob_raw_ortho_entropy_mid_g020_b295b6e0.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_a2c8d2c8.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_9f6d3772.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_5b5cd101.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_5f76d74d.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                 submission_raw05_jepa_public6q3s4corr_efmicro3_prob_strength_entropy_g015_442c6c5f.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
               submission_raw05_jepa_public6q3s4corr_compatband_prob_strength_entropy_g015_f6758d7e.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_f05638bd.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_c5ad1f8e.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_b80b6231.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
            submission_raw05_jepa_public6q3s4corr_efmicro5_prob_raw_ortho_entropy_mid_g020_fb2674bc.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_f89cfcda.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_1500c447.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_fa000489.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                 submission_raw05_jepa_public6q3s4corr_efmicro5_prob_strength_entropy_g015_1d023835.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_9587cd89.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_1f013549.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
      submission_raw05_jepa_public6q3s4corr_energyfront_direct_logit_strength_entropy_g015_2a3cf71d.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_c461c8af.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_c93a6c07.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_f7bd64c6.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                           submission_raw05_jepa_axistrade_70613b0c.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
         submission_raw05_jepa_public6q3s4corr_efmicro3_direct_logit_strength_entropy_g015_adfc4ab2.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_d525aac1.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_a599ed24.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_d4124661.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_9fbdbc4e.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
                                                         submission_frontier_cvjepa_refine_c4ca4659.csv                  0.577558                    0.575463                  0.000334             0.001709                        0.88125
```

## Interpretation

- Adding `a2c8` turns the public inverse problem into a stricter constraint: candidates now need to explain two good anchors (`raw05`, `a2c8`) while rejecting the two bad JEPA latent probes.
- If top masks concentrate in random/subject-contiguous masks, the public split is still underidentified; if they concentrate in a hidden-block scenario, that branch becomes a stronger hidden-test hypothesis.
- Candidate ranking is not a submit decision by itself. It is a diagnostic: prefer next probes that are high under both 7-anchor inverse masks and raw05+a2c8-compatible masks, and that move along a different axis from `a2c8`.
