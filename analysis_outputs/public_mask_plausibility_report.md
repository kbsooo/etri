# Public Mask Plausibility Reweight
Re-ranks existing submissions by crossing posterior-scenario profiles with explicit public-mask plausibility priors. `mask_equal` reproduces the old equal-mask assumption; the other profiles downweight global prefix/suffix masks whose public projection requires much larger probability movement than the all-row solution.

## Consensus Ranking
```
                                              file  best_rank  mean_rank  worst_rank  top1_count  top3_count  mean_score  mean_weighted_expected  mean_weighted_regret  mean_delta_vs_prior
submission_public_universeens_u65_r04_dc6f3303.csv          3  17.541667          26           0           4    0.576299                0.574710              0.000269            -0.000659
submission_public_universeens_u65_r01_365a84a6.csv          1  17.541667          28           6           6    0.576335                0.574712              0.000271            -0.000657
submission_public_universeens_u65_r03_cf973915.csv          3  17.916667          27           0           2    0.576329                0.574711              0.000269            -0.000658
submission_public_universeens_u65_r02_c0e2b2f1.csv          2  20.666667          36           0           6    0.576384                0.574715              0.000274            -0.000654
   submission_public_maskplausens_r04_161f5469.csv         11  21.250000          32           0           0    0.576276                0.574713              0.000271            -0.000656
   submission_public_maskplausens_r05_e8325bb7.csv         12  21.500000          31           0           0    0.576278                0.574712              0.000271            -0.000657
   submission_public_maskplausens_r02_dc594c28.csv          5  22.875000          37           0           0    0.576267                0.574731              0.000290            -0.000638
   submission_public_maskplausens_r01_3de9be39.csv          7  23.083333          35           0           0    0.576263                0.574724              0.000282            -0.000645
   submission_public_maskplausens_r03_40f65e60.csv          6  23.250000          36           0           0    0.576266                0.574731              0.000289            -0.000639
submission_public_universeens_u50_r04_f6ae8481.csv          4  26.500000          40           0           0    0.576335                0.574743              0.000301            -0.000626
submission_public_universeens_u80_r01_07c571e6.csv          1  26.833333          53           5           5    0.576466                0.574726              0.000285            -0.000643
submission_public_universeens_u50_r02_93b58286.csv          2  27.833333          44           0           6    0.576359                0.574753              0.000312            -0.000616
submission_public_universeens_u50_r03_77e68ed8.csv          1  27.958333          46           3           6    0.576353                0.574755              0.000313            -0.000614
submission_public_universeens_u50_r01_f5115a9b.csv          1  28.708333          47           3           6    0.576359                0.574756              0.000315            -0.000613
  submission_public_minimaxens_r02_a13_h745897.csv          3  28.916667          54           0           1    0.576467                0.574726              0.000285            -0.000643
  submission_public_minimaxens_r04_a11_h082844.csv          1  29.000000          55           1           2    0.576467                0.574726              0.000285            -0.000643
submission_public_universeens_u80_r03_72e58bdb.csv          2  30.000000          56           0           2    0.576467                0.574726              0.000285            -0.000643
   submission_public_minimaxens_r06_a9_h512521.csv          2  30.208333          57           0           4    0.576467                0.574726              0.000285            -0.000643
  submission_public_maskaware_t50_r05_fb7b695a.csv         20  30.416667          41           0           0    0.576481                0.574730              0.000289            -0.000639
  submission_public_maskaware_t35_r01_2d5fa124.csv         17  30.541667          38           0           0    0.576434                0.574742              0.000301            -0.000627
      submission_public_entropyproj_proj0_g075.csv         24  30.916667          39           0           0    0.576464                0.574730              0.000288            -0.000640
  submission_public_consfront_t65_r09_6ab53561.csv          6  31.166667          57           0           0    0.576447                0.574799              0.000358            -0.000570
submission_public_universeens_u80_r02_4c0e785c.csv          3  31.208333          58           0           3    0.576467                0.574726              0.000285            -0.000643
  submission_public_entropyproj_public2d0_g050.csv         12  31.375000          42           0           0    0.576511                0.574764              0.000322            -0.000605
```

## Reference Rows
```
                                                           file  best_rank   mean_rank  worst_rank  top1_count  top3_count  mean_score  mean_weighted_expected  mean_weighted_regret  mean_delta_vs_prior
                submission_public_minimaxens_r01_a6_h422045.csv          2   33.291667          62           0           1    0.576467                0.574727              0.000285            -0.000643
               submission_public_minimaxens_r05_a10_h506746.csv          7   35.000000          61           0           0    0.576467                0.574726              0.000285            -0.000643
                         submission_public2dblend_budget0p0.csv        108  109.000000         112           0           0    0.587272                0.575369              0.000928             0.000000
  submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv        118  119.541667         121           0           0    0.589052                0.576003              0.001561             0.000634
submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv       3055 3057.625000        3060           0           0    0.595979                0.577499              0.003058             0.002130
```

## Top Candidate Per Profile
```
       mask_profile scenario_profile                                               file    score  weighted_expected  weighted_regret  p90_regret
   diag_plaus_sharp              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.577499           0.574954         0.000505    0.000709
   diag_plaus_sharp              u50 submission_public_universeens_u50_r03_77e68ed8.csv 0.576398           0.574933         0.000335    0.000447
   diag_plaus_sharp              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575730           0.574876         0.000180    0.000163
   diag_plaus_sharp              u80 submission_public_universeens_u80_r01_07c571e6.csv 0.575437           0.574869         0.000125    0.000124
    diag_plaus_soft              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.576962           0.574417         0.000505    0.000709
    diag_plaus_soft              u50 submission_public_universeens_u50_r03_77e68ed8.csv 0.575860           0.574395         0.000335    0.000447
    diag_plaus_soft              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575192           0.574338         0.000180    0.000163
    diag_plaus_soft              u80 submission_public_universeens_u80_r01_07c571e6.csv 0.574899           0.574331         0.000125    0.000123
         mask_equal              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.577284           0.574732         0.000505    0.000707
         mask_equal              u50 submission_public_universeens_u50_r01_f5115a9b.csv 0.576166           0.574712         0.000337    0.000439
         mask_equal              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575504           0.574653         0.000181    0.000160
         mask_equal              u80 submission_public_universeens_u80_r01_07c571e6.csv 0.575211           0.574646         0.000126    0.000121
no_global_no_single              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.577495           0.574949         0.000504    0.000710
no_global_no_single              u50 submission_public_universeens_u50_r01_f5115a9b.csv 0.576392           0.574929         0.000336    0.000443
no_global_no_single              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575724           0.574871         0.000180    0.000162
no_global_no_single              u80 submission_public_universeens_u80_r01_07c571e6.csv 0.575431           0.574864         0.000125    0.000123
       random_heavy              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.577192           0.574639         0.000505    0.000709
       random_heavy              u50 submission_public_universeens_u50_r01_f5115a9b.csv 0.576079           0.574620         0.000337    0.000442
       random_heavy              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575414           0.574562         0.000181    0.000162
       random_heavy              u80 submission_public_universeens_u80_r01_07c571e6.csv 0.575123           0.574554         0.000126    0.000122
      subject_heavy              u35 submission_public_universeens_u35_r01_b5f79815.csv 0.577495           0.574954         0.000504    0.000709
      subject_heavy              u50 submission_public_universeens_u50_r03_77e68ed8.csv 0.576397           0.574932         0.000335    0.000447
      subject_heavy              u65 submission_public_universeens_u65_r01_365a84a6.csv 0.575730           0.574875         0.000180    0.000163
      subject_heavy              u80   submission_public_minimaxens_r04_a11_h082844.csv 0.575437           0.574868         0.000125    0.000124
```