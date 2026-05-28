# Public LB Inverse Mask Audit

Fits observed public LB deltas by sweeping posterior scenarios and candidate public row masks.

## Actual Public Constraints

```
              key                                                            file  public_lb  delta_vs_stage2  weight
           stage2   submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv   0.577945         0.000000     0.0
        anchor578   submission_hybrid_0p578_logit_after_subject_final9_strict.csv   0.578427         0.000482     1.0
        ordinal_q submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv   0.578303         0.000358     1.0
            raw05         submission_raw_timeline_jepa_rescue_strict_scale0p5.csv   0.577526        -0.000419     1.8
jepa_bad_residual                       submission_jepa_latent_residual_probe.csv   0.581227         0.003282     0.9
      jepa_bad_q2                             submission_jepa_latent_q2_w0p45.csv   0.579801         0.001856     0.9
```

## Top Inverse-Fit Masks

```
                                   scenario_file          mask_kind       mask_name  rows  inverse_fit_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  pred_delta_raw05  pred_delta_anchor578  pred_delta_ordinal_q                                             top_blocks
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep192    75           0.973807           0.664090       0.000488           0.678571          0.000054              0.000368              0.000338      id02_b4:7;id09_b2:7;id01_b4:5;id10_b2:5;id07_b4:5
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep040   100           1.068405           0.740570       0.000534           0.678571          0.000107              0.000473              0.000486     id09_b2:10;id02_b4:8;id09_b4:8;id01_b2:8;id02_b2:7
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep077    75           1.072268           0.742862       0.000537           0.678571          0.000104              0.000281              0.000322      id01_b2:7;id07_b4:6;id01_b4:5;id02_b2:5;id08_b4:4
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep115    50           1.077284           0.740174       0.000671           0.678571          0.000083              0.000405              0.000201      id01_b2:7;id03_b2:4;id10_b2:3;id03_b4:3;id10_b4:3
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep221    75           1.077801           0.746345       0.000611           0.678571          0.000115              0.000437              0.000308      id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep002   100           1.094166           0.765823       0.000460           0.678571          0.000128              0.000400              0.000485      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.50_rep156   125           1.095461           0.765208       0.000495           0.678571          0.000123              0.000516              0.000214      id02_b2:9;id07_b4:9;id02_b4:8;id09_b2:7;id07_b2:7
submission_public_entropyproj_public2d0_g100.csv       global_order    rowmod4_rem3    62           1.102658           0.765326       0.000420           0.678571          0.000065              0.000196              0.000109      id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep064   100           1.104506           0.779206       0.000420           0.678571          0.000150              0.000511              0.000295      id01_b4:8;id02_b2:7;id02_b4:7;id01_b2:6;id09_b2:6
submission_public_entropyproj_public2d0_g100.csv       global_order    rowmod5_rem3    50           1.106954           0.773894       0.000547           0.678571          0.000139              0.000482              0.000281      id02_b2:3;id02_b4:3;id09_b2:3;id07_b4:3;id07_b2:3
submission_public_entropyproj_public2d0_g100.csv subject_contiguous frac0.25_rep150    64           1.111159           0.771429       0.000522           0.678571          0.000094              0.000524              0.000141      id07_b2:8;id01_b2:7;id09_b2:7;id04_b6:6;id10_b4:6
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep009   100           1.117797           0.778708       0.000506           0.678571          0.000105              0.000758              0.000211      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
submission_public_entropyproj_public2d0_g100.csv subject_contiguous frac0.50_rep142   126           1.120647           0.784675       0.000545           0.678571          0.000143              0.000325              0.000381 id02_b4:15;id01_b2:13;id07_b4:10;id10_b4:10;id03_b2:10
submission_public_entropyproj_public2d0_g100.csv subject_contiguous frac0.40_rep052   101           1.122316           0.783595       0.000538           0.678571          0.000125              0.000241              0.000273     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep075    50           1.126442           0.791311       0.000539           0.678571          0.000154              0.000451              0.000415      id07_b2:5;id02_b2:4;id07_b4:4;id10_b2:3;id02_b4:3
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep132   100           1.126471           0.786771       0.000477           0.678571          0.000108              0.000771              0.000198      id02_b2:8;id02_b4:7;id01_b2:6;id07_b2:6;id10_b4:6
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.20_rep139    50           1.127113           0.783967       0.000609           0.678571          0.000121              0.000697              0.000480      id07_b4:6;id09_b2:4;id02_b4:3;id03_b4:3;id04_b6:2
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.50_rep073   125           1.129341           0.789908       0.000558           0.678571          0.000138              0.000359              0.000494     id07_b4:11;id01_b2:9;id02_b4:7;id10_b2:6;id09_b4:6
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep132    75           1.134453           0.790623       0.000620           0.678571          0.000129              0.000347              0.000509      id02_b2:7;id02_b4:5;id03_b4:5;id09_b2:5;id07_b4:5
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.50_rep171   125           1.137737           0.793434       0.000678           0.678571          0.000145              0.000492              0.000278      id01_b2:9;id07_b4:8;id02_b2:8;id02_b4:8;id03_b2:7
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.60_rep001   150           1.140629           0.796760       0.000672           0.678571          0.000150              0.000468              0.000312    id01_b2:11;id09_b2:10;id02_b2:9;id07_b4:9;id01_b4:7
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.50_rep083   125           1.141135           0.801222       0.000589           0.678571          0.000161              0.000483              0.000406      id01_b2:6;id09_b2:6;id07_b4:6;id07_b2:6;id06_b2:6
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.40_rep223   100           1.141742           0.802851       0.000469           0.678571          0.000139              0.000635              0.000174      id03_b4:7;id07_b4:7;id07_b2:7;id10_b4:6;id01_b4:6
submission_public_entropyproj_public2d0_g100.csv        random_rows frac0.30_rep056    75           1.142748           0.790330       0.000580           0.678571          0.000066              0.000020              0.000291      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
```

## Mask Kind Summary

```
         mask_kind    n  best_rank  best_score  mean_top_score  mean_rows  mean_subject_entropy
       random_rows 1360          1    0.973807        1.412269 114.669118              0.981588
      global_order   29          8    1.102658        1.388319  85.344828              0.983969
subject_contiguous  638         11    1.111159        1.408906 110.648903              0.993822
    single_subject   12         28    1.156440        1.405552  27.750000              0.000000
     subject_order    8         34    1.160611        1.299743 110.000000              0.993818
               all    1        275    1.245213        1.245213 250.000000              0.994313
```

## Best Raw05/All-Sign Compatible Masks

Raw05-compatible rows: 512; all-sign-compatible rows: 512

```
                                                                          scenario_file          mask_kind                   mask_name  rows  inverse_fit_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  pred_delta_raw05  pred_delta_anchor578  pred_delta_ordinal_q                                         top_blocks
                          submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv     single_subject                        id01    27           1.156440           0.907490       0.001007                1.0         -0.000002              0.000991              0.000694                              id01_b2:13;id01_b4:12
                          submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv       global_order             prefix_frac0.20    50           1.239641           0.967367       0.001134                1.0         -0.000002              0.001222              0.000506         id02_b2:15;id01_b2:13;id01_b4:12;id02_b4:7
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv subject_contiguous             frac0.25_rep099    64           5.161673           4.040316       0.001916                1.0         -0.000253              0.004004              0.002549  id02_b2:8;id07_b4:8;id01_b4:7;id05_b2:5;id03_b4:4
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv      subject_order per_subject_prefix_frac0.25    64           5.218610           4.080135       0.001918                1.0         -0.000259              0.004452              0.002154  id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep028    50           5.237802           4.104344       0.001795                1.0         -0.000292              0.003675              0.002899  id09_b4:7;id07_b2:4;id02_b2:4;id09_b2:4;id10_b2:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv subject_contiguous             frac0.25_rep039    64           5.306061           4.149954       0.001910                1.0         -0.000261              0.004395              0.002330  id02_b2:8;id07_b2:8;id03_b2:5;id09_b4:4;id10_b2:4
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep060    50           5.332422           4.171231       0.002029                1.0         -0.000281              0.004333              0.002418  id01_b2:5;id02_b2:4;id03_b4:3;id04_b6:3;id07_b2:2
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep128    50           5.334026           4.170528       0.001988                1.0         -0.000277              0.004509              0.002227 id02_b2:5;id10_b4:5;id09_b2:4;id07_b2:3;id06_b10:2
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep134    50           5.344660           4.178031       0.002001                1.0         -0.000259              0.004598              0.002131  id07_b4:4;id02_b4:4;id03_b2:4;id04_b6:3;id08_b4:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep235    50           5.373677           4.208494       0.001970                1.0         -0.000303              0.003935              0.002825  id01_b2:5;id05_b2:3;id02_b2:3;id09_b2:3;id06_b4:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv     single_subject                        id06    24           5.433020           4.262693       0.002108                1.0         -0.000113              0.003218              0.003301           id06_b2:7;id06_b10:5;id06_b4:4;id06_b8:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep039    50           5.445586           4.264242       0.001984                1.0         -0.000258              0.004049              0.002801  id01_b2:5;id03_b4:4;id08_b4:4;id01_b4:3;id10_b2:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep211    50           5.473134           4.287395       0.001867                1.0         -0.000289              0.003934              0.002930  id07_b4:4;id06_b2:4;id01_b2:4;id01_b4:3;id09_b4:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep042    50           5.496039           4.300280       0.001993                1.0         -0.000283              0.004369              0.002572  id01_b2:4;id09_b4:4;id10_b4:3;id02_b2:3;id02_b4:2
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep049    50           5.525463           4.321536       0.001984                1.0         -0.000228              0.004573              0.002390  id02_b2:5;id02_b4:5;id09_b2:4;id01_b2:3;id07_b2:3
/Users/kbsoo/Downloads/cl2/jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv        random_rows             frac0.20_rep104    50           5.549010           4.343497       0.001984                1.0         -0.000243              0.004281              0.002712  id07_b4:5;id01_b4:3;id06_b8:2;id02_b2:2;id10_b2:2
```

## Candidate Re-Ranking By Inverse-Fit Masks

```
                                                               file  inverse_candidate_score  inverse_weighted_expected  inverse_weighted_regret  inverse_p90_regret  inverse_win_rate_best_eps1e4
                   submission_public_entropyproj_public2d0_g100.csv                 0.574857                   0.574843                 0.000003            0.000000                      0.984375
                       submission_public_entropyproj_proj0_g100.csv                 0.574873                   0.574847                 0.000007            0.000005                      0.992188
                   submission_public_entropyproj_public2d0_g075.csv                 0.575199                   0.574932                 0.000092            0.000102                      0.867188
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv                 0.575199                   0.574932                 0.000092            0.000102                      0.867188
                   submission_public_maskaware_t65_r07_768f6df0.csv                 0.575205                   0.574934                 0.000094            0.000103                      0.796875
                   submission_public_maskaware_t65_r08_7f7fa3e2.csv                 0.575215                   0.574937                 0.000096            0.000106                      0.664062
                   submission_public_maskaware_t50_r04_6761fb38.csv                 0.576129                   0.574941                 0.000100            0.000110                      0.320312
                       submission_public_entropyproj_proj0_g075.csv                 0.576172                   0.574941                 0.000101            0.000112                      0.312500
                   submission_public_maskaware_t80_r10_18d78615.csv                 0.576690                   0.574944                 0.000103            0.000116                      0.210938
                   submission_public_maskaware_t50_r06_8d5b4fe1.csv                 0.577162                   0.574946                 0.000105            0.000114                      0.117188
                   submission_public_maskaware_t50_r05_fb7b695a.csv                 0.577283                   0.574946                 0.000106            0.000116                      0.093750
                   submission_public_minimaxens_r08_a10_h869363.csv                 0.577591                   0.574955                 0.000115            0.000127                      0.039062
                   submission_public_minimaxens_r07_a12_h981086.csv                 0.577591                   0.574955                 0.000115            0.000127                      0.039062
                 submission_public_universeens_u80_r04_8b6653a9.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                   submission_public_minimaxens_r05_a10_h506746.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                    submission_public_minimaxens_r06_a9_h512521.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                 submission_public_universeens_u80_r02_4c0e785c.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                   submission_public_minimaxens_r04_a11_h082844.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                 submission_public_universeens_u80_r03_72e58bdb.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                   submission_public_minimaxens_r03_a12_h597891.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                   submission_public_minimaxens_r02_a13_h745897.csv                 0.577592                   0.574955                 0.000115            0.000127                      0.039062
                    submission_public_minimaxens_r01_a6_h422045.csv                 0.577593                   0.574956                 0.000115            0.000127                      0.039062
                 submission_public_universeens_u80_r01_07c571e6.csv                 0.577593                   0.574956                 0.000115            0.000127                      0.039062
                   submission_public_maskaware_t65_r09_35ff9a82.csv                 0.577606                   0.574959                 0.000118            0.000132                      0.039062
                 submission_public_universeens_u65_r02_c0e2b2f1.csv                 0.577776                   0.574983                 0.000142            0.000156                      0.023438
                 submission_public_universeens_u65_r01_365a84a6.csv                 0.577805                   0.574990                 0.000150            0.000165                      0.023438
   submission_public_entropytm_public2d0_q1_q3_s1_s2_s3_s4_g075.csv                 0.577815                   0.574993                 0.000153            0.000165                      0.023438
                   submission_public_maskaware_t80_r11_544844af.csv                 0.577821                   0.574995                 0.000154            0.000167                      0.023438
                 submission_public_universeens_u65_r04_dc6f3303.csv                 0.577843                   0.575000                 0.000159            0.000176                      0.023438
                   submission_public_maskaware_t80_r12_dcfaabba.csv                 0.577845                   0.575001                 0.000161            0.000174                      0.023438
   submission_public_entropytm_public2d0_q1_q2_q3_s2_s3_s4_g075.csv                 0.577863                   0.575002                 0.000162            0.000190                      0.023438
                 submission_public_universeens_u65_r03_cf973915.csv                 0.577868                   0.575006                 0.000166            0.000183                      0.023438
                    submission_public_maskplausens_r05_e8325bb7.csv                 0.578069                   0.575058                 0.000217            0.000240                      0.023438
                    submission_public_maskplausens_r04_161f5469.csv                 0.578071                   0.575059                 0.000218            0.000239                      0.023438
                   submission_public_maskaware_t35_r02_517540cc.csv                 0.578081                   0.575061                 0.000221            0.000243                      0.023438
      submission_public_entropytm_public2d0_q1_q3_s2_s3_s4_g075.csv                 0.578097                   0.575063                 0.000222            0.000254                      0.023438
                    submission_public_maskplausens_r01_3de9be39.csv                 0.578301                   0.575097                 0.000256            0.000286                      0.007812
                    submission_public_maskplausens_r03_40f65e60.csv                 0.578349                   0.575109                 0.000269            0.000300                      0.007812
                   submission_public_maskaware_t35_r01_2d5fa124.csv                 0.578378                   0.575138                 0.000297            0.000325                      0.023438
                    submission_public_maskplausens_r02_dc594c28.csv                 0.578424                   0.575118                 0.000278            0.000311                      0.000000
```

## Candidate Re-Ranking By Sign-Compatible Masks

```
                                                          file  inverse_candidate_score  inverse_weighted_expected  inverse_weighted_regret  inverse_p90_regret  inverse_win_rate_best_eps1e4
            submission_hiddenblock_paretomix_w0.4_507296eb.csv                 0.567909                   0.567681                 0.000054        6.150000e-07                      0.984375
         submission_hiddenblock_rateprobe_neutral_7018cfdb.csv                 0.567911                   0.567682                 0.000054        1.176000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_c95eca2a.csv                 0.567911                   0.567682                 0.000054        1.345000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_e3cb8900.csv                 0.567911                   0.567682                 0.000054        1.351000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_1501e8f9.csv                 0.567911                   0.567682                 0.000054        1.789000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_27ca3bb0.csv                 0.567912                   0.567682                 0.000054        1.395000e-06                      0.984375
submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv                 0.567912                   0.567682                 0.000054        3.660000e-07                      0.984375
            submission_hiddenblock_paretomix_w0.3_b7621063.csv                 0.567912                   0.567682                 0.000054        1.546000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_746faa39.csv                 0.567913                   0.567682                 0.000054        1.784000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_b648fac9.csv                 0.567913                   0.567682                 0.000055        2.246000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_605de284.csv                 0.567913                   0.567682                 0.000055        1.956000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_45639604.csv                 0.567914                   0.567682                 0.000055        1.406000e-06                      0.984375
         submission_hiddenblock_rateprobe_neutral_4196fa0e.csv                 0.567914                   0.567682                 0.000055        1.516000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_0331e2e5.csv                 0.567914                   0.567682                 0.000055        1.504000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_4b6b636a.csv                 0.567914                   0.567682                 0.000055        1.555000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_fd0aef03.csv                 0.567914                   0.567682                 0.000055        1.560000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_b151e1b9.csv                 0.567914                   0.567682                 0.000055        1.600000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_d0ca7647.csv                 0.567914                   0.567683                 0.000055        2.368000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_1aa93658.csv                 0.567914                   0.567683                 0.000055        2.378000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_ebf79910.csv                 0.567915                   0.567683                 0.000055        2.472000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_dd59bf78.csv                 0.567915                   0.567683                 0.000055        2.174000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_a70cd599.csv                 0.567915                   0.567683                 0.000055        1.877000e-06                      0.984375
          submission_hiddenblock_seqmotif_neutral_d6755a69.csv                 0.567915                   0.567683                 0.000055        2.581000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_bba3cd6e.csv                 0.567915                   0.567683                 0.000055        2.247000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_37a1433b.csv                 0.567915                   0.567683                 0.000055        1.924000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_f34936b8.csv                 0.567915                   0.567683                 0.000055        1.587000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_61c219cc.csv                 0.567915                   0.567683                 0.000055        1.930000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_e706a74a.csv                 0.567915                   0.567683                 0.000055        1.627000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_d67cd0a9.csv                 0.567915                   0.567683                 0.000055        2.269000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_0aa528bf.csv                 0.567915                   0.567683                 0.000055        1.960000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_4117a63b.csv                 0.567915                   0.567683                 0.000055        2.002000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_79550724.csv                 0.567915                   0.567683                 0.000055        2.323000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_5b1a81df.csv                 0.567916                   0.567683                 0.000055        2.101000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_afac65f7.csv                 0.567916                   0.567683                 0.000055        2.602000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_c4367e3b.csv                 0.567916                   0.567683                 0.000055        1.943000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_7433e304.csv                 0.567916                   0.567683                 0.000055        2.014000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_8741d6d9.csv                 0.567916                   0.567683                 0.000055        2.389000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_fb98af7a.csv                 0.567916                   0.567683                 0.000055        2.435000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_20b23f5f.csv                 0.567916                   0.567683                 0.000055        2.076000e-06                      0.984375
         submission_hiddenblock_seqmotif_cellgate_1089cece.csv                 0.567916                   0.567683                 0.000055        2.006000e-06                      0.984375
```
