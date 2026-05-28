# Public Universe Minimax
Expanded minimax search over entropy, target-mask, mask-aware, conservative-frontier, and prior candidates. Profiles weight core posterior, mask-aware posterior, and conservative pseudo-posterior scenarios differently.

## Saved Candidates
```
                                              file profile    score  weighted_expected  weighted_regret  p90_regret  p95_regret  weighted_delta_vs_prior  win_rate_vs_prior  oof_loss  active_weights
submission_public_universeens_u80_r01_07c571e6.csv     u80 0.575211           0.574646         0.000126    0.000121    0.000149                -0.000710           0.970005  0.554343               3
submission_public_universeens_u80_r02_4c0e785c.csv     u80 0.575211           0.574646         0.000126    0.000121    0.000149                -0.000710           0.970005  0.554349               1
submission_public_universeens_u80_r03_72e58bdb.csv     u80 0.575211           0.574646         0.000126    0.000121    0.000149                -0.000710           0.970005  0.554345               1
submission_public_universeens_u80_r04_8b6653a9.csv     u80 0.575211           0.574646         0.000126    0.000121    0.000149                -0.000710           0.970005  0.554346               2
submission_public_universeens_u65_r01_365a84a6.csv     u65 0.575504           0.574653         0.000181    0.000160    0.000750                -0.000692           0.940009  0.554318               7
submission_public_universeens_u65_r02_c0e2b2f1.csv     u65 0.575506           0.574653         0.000180    0.000153    0.000784                -0.000693           0.940009  0.554117              33
submission_public_universeens_u65_r03_cf973915.csv     u65 0.575514           0.574653         0.000180    0.000175    0.000743                -0.000693           0.940028  0.554895               4
submission_public_universeens_u65_r04_dc6f3303.csv     u65 0.575514           0.574655         0.000182    0.000171    0.000747                -0.000690           0.940056  0.554759              46
submission_public_universeens_u50_r01_f5115a9b.csv     u50 0.576166           0.574712         0.000337    0.000439    0.000966                -0.000611           0.892166  0.556550              44
submission_public_universeens_u50_r02_93b58286.csv     u50 0.576166           0.574709         0.000334    0.000434    0.000988                -0.000613           0.889510  0.556492              61
submission_public_universeens_u50_r03_77e68ed8.csv     u50 0.576167           0.574711         0.000335    0.000442    0.000966                -0.000612           0.892260  0.556381              58
submission_public_universeens_u50_r04_f6ae8481.csv     u50 0.576176           0.574700         0.000324    0.000460    0.001050                -0.000623           0.884463  0.555918              58
submission_public_universeens_u35_r01_b5f79815.csv     u35 0.577284           0.574732         0.000505    0.000707    0.003200                -0.000554           0.851766  0.557983              33
submission_public_universeens_u35_r02_caa8c427.csv     u35 0.577305           0.574737         0.000509    0.000719    0.003184                -0.000550           0.851041  0.557331               5
submission_public_universeens_u35_r03_efb5e8c9.csv     u35 0.577312           0.574733         0.000505    0.000780    0.003064                -0.000554           0.831470  0.556975               4
submission_public_universeens_u35_r04_02cf816a.csv     u35 0.577316           0.574740         0.000513    0.000697    0.003264                -0.000546           0.853480  0.557366               5
```

## Integrity
```
                                              file  rows  key_match  duplicate_keys  null_predictions  min_prob  max_prob oof_shape  oof_min  oof_max
submission_public_universeens_u80_r01_07c571e6.csv   250       True               0                 0  0.076000  0.977363  (450, 7) 0.026385 0.987939
submission_public_universeens_u80_r02_4c0e785c.csv   250       True               0                 0  0.076029  0.977358  (450, 7) 0.026446 0.987945
submission_public_universeens_u80_r03_72e58bdb.csv   250       True               0                 0  0.076015  0.977360  (450, 7) 0.026425 0.987948
submission_public_universeens_u80_r04_8b6653a9.csv   250       True               0                 0  0.076023  0.977359  (450, 7) 0.026418 0.987946
submission_public_universeens_u65_r01_365a84a6.csv   250       True               0                 0  0.074404  0.977473  (450, 7) 0.029651 0.988685
submission_public_universeens_u65_r02_c0e2b2f1.csv   250       True               0                 0  0.075003  0.977323  (450, 7) 0.028985 0.988514
submission_public_universeens_u65_r03_cf973915.csv   250       True               0                 0  0.075144  0.977449  (450, 7) 0.028812 0.987984
submission_public_universeens_u65_r04_dc6f3303.csv   250       True               0                 0  0.075055  0.977345  (450, 7) 0.030544 0.988469
submission_public_universeens_u50_r01_f5115a9b.csv   250       True               0                 0  0.071883  0.977680  (450, 7) 0.039666 0.987650
submission_public_universeens_u50_r02_93b58286.csv   250       True               0                 0  0.071718  0.977748  (450, 7) 0.037860 0.987254
submission_public_universeens_u50_r03_77e68ed8.csv   250       True               0                 0  0.071784  0.977686  (450, 7) 0.037263 0.987526
submission_public_universeens_u50_r04_f6ae8481.csv   250       True               0                 0  0.071742  0.977609  (450, 7) 0.036476 0.987871
submission_public_universeens_u35_r01_b5f79815.csv   250       True               0                 0  0.074047  0.977805  (450, 7) 0.044692 0.987385
submission_public_universeens_u35_r02_caa8c427.csv   250       True               0                 0  0.074199  0.977852  (450, 7) 0.035180 0.988008
submission_public_universeens_u35_r03_efb5e8c9.csv   250       True               0                 0  0.074708  0.977763  (450, 7) 0.038286 0.988418
submission_public_universeens_u35_r04_02cf816a.csv   250       True               0                 0  0.074004  0.977745  (450, 7) 0.037188 0.988360
```