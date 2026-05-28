# Public-Safe JEPA Hybrid Probe

This tests whether large JEPA moves can ride on top of the public-minimax candidates without violating the public-posterior scenario audit.

## Top Scored Rows

```
                                          name    score  mean_expected  mean_delta_vs_base  p90_delta_vs_base  mean_abs_delta_vs_stage2
                             base__minimax_r01 0.574683       0.574634       -1.500000e-08       2.960000e-07                  0.016378
                                     base__u80 0.574684       0.574634       -3.900000e-08       3.420000e-07                  0.016377
minimax_r01__neural_episode_bal__logit__w0.030 0.577495       0.574637        2.270000e-06       2.058600e-05                  0.015970
minimax_r05__neural_episode_bal__logit__w0.030 0.577520       0.574637        2.278000e-06       2.028700e-05                  0.015975
        u80__neural_episode_bal__logit__w0.030 0.577559       0.574637        2.276000e-06       2.066500e-05                  0.015968
 minimax_r01__neural_episode_bal__prob__w0.030 0.577839       0.574637        2.772000e-06       2.074400e-05                  0.015974
 minimax_r05__neural_episode_bal__prob__w0.030 0.577872       0.574637        2.792000e-06       2.045200e-05                  0.015979
         u80__neural_episode_bal__prob__w0.030 0.577914       0.574637        2.788000e-06       2.081800e-05                  0.015972
minimax_r01__neural_episode_bal__logit__w0.050 0.578813       0.574643        8.909000e-06       3.915000e-05                  0.015738
        u80__neural_episode_bal__logit__w0.050 0.578883       0.574643        8.934000e-06       3.923500e-05                  0.015736
minimax_r05__neural_episode_bal__logit__w0.050 0.578928       0.574643        8.913000e-06       3.884900e-05                  0.015743
 minimax_r01__neural_episode_bal__prob__w0.050 0.579733       0.574644        1.024500e-05       3.992200e-05                  0.015744
         u80__neural_episode_bal__prob__w0.050 0.579788       0.574645        1.028400e-05       4.000200e-05                  0.015742
 minimax_r05__neural_episode_bal__prob__w0.050 0.579881       0.574645        1.026600e-05       3.963100e-05                  0.015750
  minimax_r01__blockcanvas_noq2__logit__w0.030 0.580465       0.574639        4.346000e-06       1.841500e-05                  0.016075
          u80__blockcanvas_noq2__logit__w0.030 0.580528       0.574639        4.363000e-06       1.849400e-05                  0.016074
  minimax_r05__blockcanvas_noq2__logit__w0.030 0.580603       0.574639        4.371000e-06       1.813000e-05                  0.016081
   minimax_r01__blockcanvas_noq2__prob__w0.030 0.580991       0.574639        5.183000e-06       1.795700e-05                  0.016095
           u80__blockcanvas_noq2__prob__w0.030 0.581018       0.574639        5.208000e-06       1.804100e-05                  0.016093
   minimax_r05__blockcanvas_noq2__prob__w0.030 0.581051       0.574639        5.220000e-06       1.768700e-05                  0.016101
```

## Saved Hybrid Submissions

```
 rank                                                                     alias    score  mean_expected  mean_delta_vs_public_base  mean_abs_delta_vs_stage2
    1   submission_bigshot_hybrid_01_minimax_r01_multifeature_raw_prob_w0p3.csv 0.587549       0.575289                   0.000655                  0.018145
    2   submission_bigshot_hybrid_02_minimax_r05_multifeature_raw_prob_w0p3.csv 0.587550       0.575289                   0.000655                  0.018148
    3           submission_bigshot_hybrid_03_u80_multifeature_raw_prob_w0p3.csv 0.587550       0.575289                   0.000655                  0.018144
    4  submission_bigshot_hybrid_04_minimax_r01_multifeature_raw_logit_w0p4.csv 0.589276       0.575683                   0.001049                  0.019290
    5  submission_bigshot_hybrid_05_minimax_r05_multifeature_raw_logit_w0p4.csv 0.589278       0.575683                   0.001049                  0.019293
    6          submission_bigshot_hybrid_06_u80_multifeature_raw_logit_w0p4.csv 0.589278       0.575684                   0.001049                  0.019290
    7 submission_bigshot_hybrid_07_u65_maskrank_multifeature_raw_logit_w0p4.csv 0.589588       0.575752                   0.001117                  0.018589
    8  submission_bigshot_hybrid_08_minimax_r01_blockcanvas_noq2_logit_w0p4.csv 0.589671       0.575757                   0.001123                  0.018553
```

## Interpretation

The pure public bases still rank best. The saved hybrids are therefore not the first public-LB candidates; they are aggressive probes that keep the public-posterior expected loss under about 0.5759 while increasing JEPA movement.
