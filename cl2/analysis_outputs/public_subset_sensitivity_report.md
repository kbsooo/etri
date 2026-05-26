# Public Subset Sensitivity Audit
Expected losses use `submission_public_entropyproj_public2d0_g100.csv` as the posterior label distribution. Masks simulate possible public row subsets.

## Top Robust Candidates
```
                                                               file  full_expected  subset_p95_delta_vs_full  worst_structured_delta_vs_full  mean_delta_vs_prior  loss_vs_prior_p90  win_rate_vs_prior  subset_robust_score
                   submission_public_entropyproj_public2d0_g100.csv       0.575734                  0.008959                        0.070543            -0.001459          -0.001337                1.0             0.605471
                       submission_public_entropyproj_proj0_g100.csv       0.575738                  0.008959                        0.070541            -0.001455          -0.001333                1.0             0.605474
                   submission_public_entropyproj_public2d0_g075.csv       0.575826                  0.008956                        0.070590            -0.001368          -0.001253                1.0             0.605569
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv       0.575826                  0.008956                        0.070590            -0.001368          -0.001253                1.0             0.605569
                   submission_public_maskaware_t65_r07_768f6df0.csv       0.575827                  0.008955                        0.070587            -0.001366          -0.001252                1.0             0.605569
                   submission_public_maskaware_t80_r10_18d78615.csv       0.575836                  0.008948                        0.070588            -0.001357          -0.001244                1.0             0.605572
                       submission_public_entropyproj_proj0_g075.csv       0.575835                  0.008953                        0.070579            -0.001359          -0.001247                1.0             0.605572
                   submission_public_maskaware_t65_r08_7f7fa3e2.csv       0.575830                  0.008957                        0.070591            -0.001363          -0.001250                1.0             0.605574
                   submission_public_maskaware_t50_r04_6761fb38.csv       0.575834                  0.008956                        0.070600            -0.001359          -0.001245                1.0             0.605580
                   submission_public_maskaware_t50_r06_8d5b4fe1.csv       0.575839                  0.008955                        0.070585            -0.001354          -0.001240                1.0             0.605582
                   submission_public_minimaxens_r07_a12_h981086.csv       0.575848                  0.008952                        0.070570            -0.001344          -0.001229                1.0             0.605582
                   submission_public_minimaxens_r08_a10_h869363.csv       0.575848                  0.008952                        0.070570            -0.001344          -0.001229                1.0             0.605582
                 submission_public_universeens_u80_r04_8b6653a9.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                   submission_public_minimaxens_r05_a10_h506746.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                    submission_public_minimaxens_r06_a9_h512521.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                 submission_public_universeens_u80_r02_4c0e785c.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                   submission_public_minimaxens_r03_a12_h597891.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                   submission_public_minimaxens_r04_a11_h082844.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                 submission_public_universeens_u80_r03_72e58bdb.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                   submission_public_minimaxens_r02_a13_h745897.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                   submission_public_maskaware_t50_r05_fb7b695a.csv       0.575840                  0.008955                        0.070584            -0.001353          -0.001239                1.0             0.605582
                 submission_public_universeens_u80_r01_07c571e6.csv       0.575849                  0.008952                        0.070570            -0.001344          -0.001228                1.0             0.605582
                    submission_public_minimaxens_r01_a6_h422045.csv       0.575849                  0.008952                        0.070571            -0.001344          -0.001228                1.0             0.605582
                   submission_public_maskaware_t65_r09_35ff9a82.csv       0.575854                  0.008956                        0.070638            -0.001341          -0.001230                1.0             0.605611
```

## Worst Mask Examples For Top 8
```
                                                               file      mask_kind       mask_name  rows  expected_loss  delta_vs_full  delta_vs_prior
                       submission_public_entropyproj_proj0_g075.csv single_subject            id10    22       0.646414       0.070579       -0.002047
                       submission_public_entropyproj_proj0_g075.csv single_subject            id08    19       0.638444       0.062610       -0.001373
                       submission_public_entropyproj_proj0_g075.csv   global_order suffix_frac0.30    75       0.634440       0.058605       -0.001616
                       submission_public_entropyproj_proj0_g075.csv   global_order suffix_frac0.20    50       0.633982       0.058147       -0.001655
                       submission_public_entropyproj_proj0_g075.csv   global_order suffix_frac0.40   100       0.626725       0.050890       -0.001593
                       submission_public_entropyproj_proj0_g075.csv single_subject            id07    30       0.623493       0.047658       -0.001678
                       submission_public_entropyproj_proj0_g075.csv single_subject            id09    27       0.623064       0.047229       -0.001356
                       submission_public_entropyproj_proj0_g075.csv single_subject            id01    27       0.616919       0.041084       -0.001479
                       submission_public_entropyproj_proj0_g100.csv single_subject            id10    22       0.646279       0.070541       -0.002182
                       submission_public_entropyproj_proj0_g100.csv single_subject            id08    19       0.638360       0.062621       -0.001458
                       submission_public_entropyproj_proj0_g100.csv   global_order suffix_frac0.30    75       0.634330       0.058592       -0.001725
                       submission_public_entropyproj_proj0_g100.csv   global_order suffix_frac0.20    50       0.633869       0.058131       -0.001767
                       submission_public_entropyproj_proj0_g100.csv   global_order suffix_frac0.40   100       0.626615       0.050876       -0.001703
                       submission_public_entropyproj_proj0_g100.csv single_subject            id07    30       0.623370       0.047632       -0.001801
                       submission_public_entropyproj_proj0_g100.csv single_subject            id09    27       0.622968       0.047229       -0.001452
                       submission_public_entropyproj_proj0_g100.csv single_subject            id01    27       0.616803       0.041064       -0.001595
                   submission_public_entropyproj_public2d0_g075.csv single_subject            id10    22       0.646415       0.070590       -0.002046
                   submission_public_entropyproj_public2d0_g075.csv single_subject            id08    19       0.638448       0.062623       -0.001369
                   submission_public_entropyproj_public2d0_g075.csv   global_order suffix_frac0.30    75       0.634437       0.058611       -0.001619
                   submission_public_entropyproj_public2d0_g075.csv   global_order suffix_frac0.20    50       0.633978       0.058153       -0.001658
                   submission_public_entropyproj_public2d0_g075.csv   global_order suffix_frac0.40   100       0.626720       0.050894       -0.001597
                   submission_public_entropyproj_public2d0_g075.csv single_subject            id07    30       0.623482       0.047657       -0.001688
                   submission_public_entropyproj_public2d0_g075.csv single_subject            id09    27       0.623056       0.047230       -0.001364
                   submission_public_entropyproj_public2d0_g075.csv single_subject            id01    27       0.616900       0.041074       -0.001498
                   submission_public_entropyproj_public2d0_g100.csv single_subject            id10    22       0.646277       0.070543       -0.002184
                   submission_public_entropyproj_public2d0_g100.csv single_subject            id08    19       0.638357       0.062623       -0.001460
                   submission_public_entropyproj_public2d0_g100.csv   global_order suffix_frac0.30    75       0.634328       0.058594       -0.001727
                   submission_public_entropyproj_public2d0_g100.csv   global_order suffix_frac0.20    50       0.633867       0.058133       -0.001770
                   submission_public_entropyproj_public2d0_g100.csv   global_order suffix_frac0.40   100       0.626613       0.050879       -0.001705
                   submission_public_entropyproj_public2d0_g100.csv single_subject            id07    30       0.623369       0.047635       -0.001802
                   submission_public_entropyproj_public2d0_g100.csv single_subject            id09    27       0.622965       0.047231       -0.001455
                   submission_public_entropyproj_public2d0_g100.csv single_subject            id01    27       0.616800       0.041066       -0.001598
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv single_subject            id10    22       0.646415       0.070590       -0.002046
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv single_subject            id08    19       0.638448       0.062623       -0.001369
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv   global_order suffix_frac0.30    75       0.634437       0.058611       -0.001619
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv   global_order suffix_frac0.20    50       0.633978       0.058153       -0.001658
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv   global_order suffix_frac0.40   100       0.626720       0.050894       -0.001597
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv single_subject            id07    30       0.623482       0.047657       -0.001688
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv single_subject            id09    27       0.623056       0.047230       -0.001364
submission_public_entropytm_public2d0_q1_q2_q3_s1_s2_s3_s4_g075.csv single_subject            id01    27       0.616900       0.041074       -0.001498
                   submission_public_maskaware_t65_r07_768f6df0.csv single_subject            id10    22       0.646414       0.070587       -0.002047
                   submission_public_maskaware_t65_r07_768f6df0.csv single_subject            id08    19       0.638446       0.062619       -0.001372
                   submission_public_maskaware_t65_r07_768f6df0.csv   global_order suffix_frac0.30    75       0.634435       0.058608       -0.001620
                   submission_public_maskaware_t65_r07_768f6df0.csv   global_order suffix_frac0.20    50       0.633976       0.058149       -0.001660
                   submission_public_maskaware_t65_r07_768f6df0.csv   global_order suffix_frac0.40   100       0.626719       0.050892       -0.001598
                   submission_public_maskaware_t65_r07_768f6df0.csv single_subject            id07    30       0.623484       0.047657       -0.001687
                   submission_public_maskaware_t65_r07_768f6df0.csv single_subject            id09    27       0.623053       0.047226       -0.001367
                   submission_public_maskaware_t65_r07_768f6df0.csv single_subject            id01    27       0.616910       0.041083       -0.001487
```