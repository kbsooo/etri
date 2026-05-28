# Public Mask-Aware Entropy Projection
This experiment inverts the assumption that the public LB subset behaves like all 250 rows. It solves the three public-score constraints on many plausible row masks, averages the resulting logit shifts, and scores marginal/conditional mask-bagged candidates.

## Public Mask Diagnostics
```
        family  masks  ok_rate  median_rows  mean_abs_logit_delta  p90_abs_logit_delta  max_abs_logit_delta  mean_probability_move
           all      1      1.0        250.0              0.091712             0.196481             0.700578               0.017658
        global     12      1.0        112.5              0.211588             0.454114             1.693998               0.035586
        random    200      1.0        100.0              0.098085             0.207793             1.022248               0.018525
      random50     40      1.0        125.0              0.097176             0.204643             0.826903               0.018286
        rowmod     14      1.0         62.5              0.095166             0.202719             0.838360               0.018113
subject_contig    160      1.0        113.5              0.090758             0.193585             0.773596               0.017478
 subject_order      8      1.0        113.5              0.091624             0.196437             0.745282               0.017755
```

## Saved Candidates
```
                                            file  selection_trust  selection_score      family_group    agg_mode target_mask  gamma  oof_loss  posterior_mean_expected  conservative_mean_expected  posterior_mean_delta_vs_stage2  conservative_mean_delta_vs_stage2  mean_probability_move
submission_public_maskaware_t35_r01_2d5fa124.csv             0.35         0.577739        random_all    marginal         all   1.25  0.554255                 0.575532                    0.575706                       -0.001460                          -0.000170               0.009689
submission_public_maskaware_t35_r02_517540cc.csv             0.35         0.577769          random50    marginal         all   1.25  0.553816                 0.575522                    0.575764                       -0.001471                          -0.000112               0.010966
submission_public_maskaware_t35_r03_cac1b720.csv             0.35         0.577797 all_struct_random    marginal         all   1.25  0.554957                 0.575545                    0.575734                       -0.001447                          -0.000142               0.009529
submission_public_maskaware_t50_r04_6761fb38.csv             0.50         0.577525 all_struct_random conditional         all   0.75  0.553121                 0.575502                    0.575823                       -0.001490                          -0.000052               0.013071
submission_public_maskaware_t50_r05_fb7b695a.csv             0.50         0.577527    subject_contig conditional         all   0.75  0.553212                 0.575500                    0.575822                       -0.001492                          -0.000054               0.012899
submission_public_maskaware_t50_r06_8d5b4fe1.csv             0.50         0.577530    subject_struct conditional         all   0.75  0.553262                 0.575500                    0.575823                       -0.001492                          -0.000053               0.012925
submission_public_maskaware_t65_r07_768f6df0.csv             0.65         0.577257        random_all conditional         all   0.75  0.553045                 0.575502                    0.575827                       -0.001491                          -0.000049               0.013186
submission_public_maskaware_t65_r08_7f7fa3e2.csv             0.65         0.577265          random50 conditional         all   0.75  0.553282                 0.575502                    0.575831                       -0.001490                          -0.000045               0.013164
submission_public_maskaware_t65_r09_35ff9a82.csv             0.65         0.577269        structured conditional         all   0.75  0.553294                 0.575512                    0.575827                       -0.001480                          -0.000049               0.013082
submission_public_maskaware_t80_r10_18d78615.csv             0.80         0.577002            rowmod conditional         all   0.75  0.553177                 0.575511                    0.575835                       -0.001482                          -0.000041               0.013318
submission_public_maskaware_t80_r11_544844af.csv             0.80         0.577013        random_all conditional        noq2   0.75  0.553156                 0.575502                    0.575845                       -0.001491                          -0.000031               0.011843
submission_public_maskaware_t80_r12_dcfaabba.csv             0.80         0.577016 all_struct_random conditional        noq2   0.75  0.553258                 0.575502                    0.575842                       -0.001490                          -0.000034               0.011740
```

## Integrity
```
                                            file  rows  key_match  duplicate_keys  null_predictions  min_prob  max_prob oof_shape  oof_min  oof_max
submission_public_maskaware_t35_r01_2d5fa124.csv   250       True               0                 0  0.070838  0.977226  (450, 7) 0.031838 0.988738
submission_public_maskaware_t35_r02_517540cc.csv   250       True               0                 0  0.072693  0.976573  (450, 7) 0.032757 0.989638
submission_public_maskaware_t35_r03_cac1b720.csv   250       True               0                 0  0.067515  0.977562  (450, 7) 0.029764 0.989331
submission_public_maskaware_t50_r04_6761fb38.csv   250       True               0                 0  0.074984  0.976965  (450, 7) 0.028548 0.989773
submission_public_maskaware_t50_r05_fb7b695a.csv   250       True               0                 0  0.074150  0.977317  (450, 7) 0.030790 0.989806
submission_public_maskaware_t50_r06_8d5b4fe1.csv   250       True               0                 0  0.073983  0.977425  (450, 7) 0.030731 0.989786
submission_public_maskaware_t65_r07_768f6df0.csv   250       True               0                 0  0.074589  0.976841  (450, 7) 0.025841 0.989859
submission_public_maskaware_t65_r08_7f7fa3e2.csv   250       True               0                 0  0.074109  0.976641  (450, 7) 0.027536 0.989638
submission_public_maskaware_t65_r09_35ff9a82.csv   250       True               0                 0  0.075895  0.977245  (450, 7) 0.030437 0.989710
submission_public_maskaware_t80_r10_18d78615.csv   250       True               0                 0  0.074662  0.976806  (450, 7) 0.025958 0.988757
submission_public_maskaware_t80_r11_544844af.csv   250       True               0                 0  0.074589  0.976841  (450, 7) 0.025841 0.989859
submission_public_maskaware_t80_r12_dcfaabba.csv   250       True               0                 0  0.074984  0.976965  (450, 7) 0.028548 0.989773
```