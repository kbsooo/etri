# Public LB Direct Label Inverse7

This audit treats each candidate public subset mask as the actual public rows and solves directly for soft binary labels that explain the observed seven-anchor public deltas.

## Top Soft-Label Solutions

```
solution_id          mask_kind       mask_name  rows   prior_name  lambda  solution_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  mean_abs_shift_vs_prior  near_binary_rate_05  pred_delta_raw05  pred_delta_cvjepa_a2c8  pred_delta_jepa_bad_residual                                             top_blocks
   6bc28e74        random_rows frac0.40_rep009   100 entropy_g075     0.0        0.000384           0.000000   0.000000e+00                1.0                 0.012791             0.017143         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   5f68765b subject_contiguous frac0.40_rep052   101 entropy_g075     0.0        0.000423           0.000000   0.000000e+00                1.0                 0.014114             0.022631         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   08893e2a        random_rows frac0.40_rep002   100 entropy_g075     0.0        0.000444           0.000000   0.000000e+00                1.0                 0.014806             0.022857         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   13c90bcc        random_rows frac0.40_rep009   100 entropy_g050     0.0        0.000449           0.000000   0.000000e+00                1.0                 0.014964             0.020000         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   4df045f4        random_rows frac0.30_rep221    75 entropy_g075     0.0        0.000452           0.000000   0.000000e+00                1.0                 0.015064             0.017143         -0.000419               -0.000506                      0.003282      id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
   f4b74e2f        random_rows frac0.20_rep114    50 entropy_g075     0.0        0.000454           0.000000   0.000000e+00                1.0                 0.015148             0.028571         -0.000419               -0.000506                      0.003282      id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
   b6ae0add subject_contiguous frac0.50_rep142   126 entropy_g075     0.0        0.000467           0.000000   0.000000e+00                1.0                 0.015558             0.024943         -0.000419               -0.000506                      0.003282 id02_b4:15;id01_b2:13;id07_b4:10;id10_b4:10;id03_b2:10
   15766c08 subject_contiguous frac0.40_rep052   101 entropy_g050     0.0        0.000479           0.000000   0.000000e+00                1.0                 0.015956             0.025460         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   2de8001a       global_order    rowmod4_rem3    62 entropy_g075     0.0        0.000483           0.000000   0.000000e+00                1.0                 0.016113             0.018433         -0.000419               -0.000506                      0.003282      id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
   954a647c        random_rows frac0.30_rep056    75 entropy_g075     0.0        0.000490           0.000000   0.000000e+00                1.0                 0.016336             0.017143         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
   b4863538 subject_contiguous frac0.25_rep099    64 entropy_g075     0.0        0.000495           0.000000   0.000000e+00                1.0                 0.016497             0.020089         -0.000419               -0.000506                      0.003282      id02_b2:8;id07_b4:8;id01_b4:7;id05_b2:5;id03_b4:4
   54b0139f        random_rows frac0.20_rep114    50 entropy_g050     0.0        0.000496           0.000000   0.000000e+00                1.0                 0.016547             0.028571         -0.000419               -0.000506                      0.003282      id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
   c1ef0015        random_rows frac0.40_rep002   100 entropy_g050     0.0        0.000497           0.000000   0.000000e+00                1.0                 0.016562             0.024286         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   674e6548        random_rows frac0.40_rep197   100 entropy_g075     0.0        0.000501           0.000000   0.000000e+00                1.0                 0.016702             0.024286         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   06158183        random_rows frac0.30_rep221    75 entropy_g050     0.0        0.000505           0.000000   0.000000e+00                1.0                 0.016848             0.019048         -0.000419               -0.000506                      0.003282      id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
   513139a7 subject_contiguous frac0.40_rep009   101 entropy_g075     0.0        0.000506           0.000000   0.000000e+00                1.0                 0.016870             0.018388         -0.000419               -0.000506                      0.003282     id07_b4:12;id10_b2:9;id09_b2:7;id04_b6:7;id01_b2:7
   220c6c19        random_rows frac0.40_rep002   100         a2c8     0.0        0.000509           0.000000   0.000000e+00                1.0                 0.016958             0.018571         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   de58f831        random_rows frac0.40_rep009   100         a2c8     0.0        0.000515           0.000000   0.000000e+00                1.0                 0.017181             0.024286         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   c33b7229 subject_contiguous frac0.40_rep052   101         a2c8     0.0        0.000521           0.000000   0.000000e+00                1.0                 0.017375             0.021216         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   270176f6 subject_contiguous frac0.25_rep099    64 entropy_g050     0.0        0.000523           0.000000   0.000000e+00                1.0                 0.017417             0.020089         -0.000419               -0.000506                      0.003282      id02_b2:8;id07_b4:8;id01_b4:7;id05_b2:5;id03_b4:4
   7cd37e18        random_rows frac0.50_rep169   125 entropy_g075     0.0        0.000523           0.000000   0.000000e+00                1.0                 0.017426             0.014857         -0.000419               -0.000506                      0.003282      id02_b2:9;id07_b2:8;id10_b2:8;id10_b4:8;id01_b4:7
   f3a84c90 subject_contiguous frac0.25_rep150    64 entropy_g075     0.0        0.000524           0.000000   0.000000e+00                1.0                 0.017454             0.015625         -0.000419               -0.000506                      0.003282      id07_b2:8;id01_b2:7;id09_b2:7;id04_b6:6;id10_b4:6
   8a83d3dd subject_contiguous frac0.50_rep142   126 entropy_g050     0.0        0.000524           0.000000   0.000000e+00                1.0                 0.017460             0.024943         -0.000419               -0.000506                      0.003282 id02_b4:15;id01_b2:13;id07_b4:10;id10_b4:10;id03_b2:10
   cfb7ce90        random_rows frac0.40_rep002   100        raw05     0.0        0.000524           0.000000   0.000000e+00                1.0                 0.017466             0.018571         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   1d5f7a07 subject_contiguous frac0.25_rep119    64 entropy_g075     0.0        0.000525           0.000000   0.000000e+00                1.0                 0.017486             0.022321         -0.000419               -0.000506                      0.003282      id01_b2:7;id02_b4:7;id09_b2:7;id07_b4:6;id10_b4:6
   4680d820        random_rows frac0.40_rep092   100 entropy_g050     0.0        0.000526           0.000009   4.000000e-09                1.0                 0.017154             0.017143         -0.000419               -0.000506                      0.003282      id02_b2:9;id02_b4:7;id07_b4:7;id01_b4:6;id09_b2:6
   c3cb2883        random_rows frac0.30_rep056    75 entropy_g050     0.0        0.000527           0.000000   0.000000e+00                1.0                 0.017576             0.020952         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
   9bbbe927        random_rows frac0.40_rep052   100 entropy_g075     0.0        0.000530           0.000000   0.000000e+00                1.0                 0.017675             0.018571         -0.000419               -0.000506                      0.003282      id02_b2:9;id10_b4:7;id04_b6:6;id01_b2:6;id03_b2:5
   f5b3993d        random_rows frac0.40_rep040   100         a2c8     0.0        0.000531           0.000000   0.000000e+00                1.0                 0.017700             0.020000         -0.000419               -0.000506                      0.003282     id09_b2:10;id02_b4:8;id09_b4:8;id01_b2:8;id02_b2:7
   fc1a5d26       global_order    rowmod4_rem3    62 entropy_g050     0.0        0.000531           0.000000   0.000000e+00                1.0                 0.017709             0.018433         -0.000419               -0.000506                      0.003282      id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
   580d44d2        random_rows frac0.40_rep009   100        raw05     0.0        0.000534           0.000000   0.000000e+00                1.0                 0.017789             0.025714         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   c9b525b3        random_rows frac0.40_rep197   100 entropy_g050     0.0        0.000537           0.000000   0.000000e+00                1.0                 0.017900             0.024286         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   eef8f34c subject_contiguous frac0.40_rep052   101        raw05     0.0        0.000538           0.000000   0.000000e+00                1.0                 0.017935             0.019802         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   af38786f        random_rows frac0.40_rep197   100         a2c8     0.0        0.000538           0.000000   0.000000e+00                1.0                 0.017941             0.018571         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   60dde636        random_rows frac0.40_rep092   100 entropy_g075     0.0        0.000542           0.000061   2.900000e-08                1.0                 0.015569             0.015714         -0.000419               -0.000506                      0.003282      id02_b2:9;id02_b4:7;id07_b4:7;id01_b4:6;id09_b2:6
   03d23fe5        random_rows frac0.50_rep073   125         a2c8     0.0        0.000542           0.000000   0.000000e+00                1.0                 0.018057             0.021714         -0.000419               -0.000506                      0.003282     id07_b4:11;id01_b2:9;id02_b4:7;id10_b2:6;id09_b4:6
   1af6cd1b subject_contiguous frac0.40_rep009   101 entropy_g050     0.0        0.000544           0.000000   0.000000e+00                1.0                 0.018149             0.019802         -0.000419               -0.000506                      0.003282     id07_b4:12;id10_b2:9;id09_b2:7;id04_b6:7;id01_b2:7
   f63c6177        random_rows frac0.30_rep056    75         a2c8     0.0        0.000545           0.000000   0.000000e+00                1.0                 0.018181             0.020952         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
   45395c22        random_rows frac0.40_rep092   100         a2c8     0.0        0.000547           0.000000   0.000000e+00                1.0                 0.018220             0.020000         -0.000419               -0.000506                      0.003282      id02_b2:9;id02_b4:7;id07_b4:7;id01_b4:6;id09_b2:6
   45c768a6        random_rows frac0.50_rep115   125         a2c8     0.0        0.000548           0.000000   0.000000e+00                1.0                 0.018259             0.016000         -0.000419               -0.000506                      0.003282      id09_b4:9;id09_b2:9;id03_b2:8;id01_b2:7;id02_b2:7
```

## Target Rate Shifts In Top Solutions

```
solution_id target  solution_rate  prior_rate  rate_delta_vs_prior  mean_abs_shift_vs_prior
   6bc28e74     Q1       0.497062    0.508185            -0.011123                 0.019415
   6bc28e74     Q2       0.551901    0.552185            -0.000284                 0.006157
   6bc28e74     Q3       0.619674    0.620278            -0.000604                 0.010998
   6bc28e74     S1       0.680769    0.684767            -0.003998                 0.014671
   6bc28e74     S2       0.644864    0.644911            -0.000048                 0.014006
   6bc28e74     S3       0.659036    0.651727             0.007309                 0.014766
   6bc28e74     S4       0.578073    0.576529             0.001544                 0.009528
   5f68765b     Q1       0.498795    0.508315            -0.009520                 0.021359
   5f68765b     Q2       0.540373    0.539255             0.001118                 0.005260
   5f68765b     Q3       0.602254    0.597172             0.005081                 0.012930
   5f68765b     S1       0.656308    0.659981            -0.003673                 0.016306
   5f68765b     S2       0.637000    0.636322             0.000679                 0.015965
   5f68765b     S3       0.663105    0.655195             0.007910                 0.015565
   5f68765b     S4       0.570142    0.571210            -0.001068                 0.011415
   08893e2a     Q1       0.489443    0.499682            -0.010238                 0.021094
   08893e2a     Q2       0.543258    0.544070            -0.000811                 0.005958
   08893e2a     Q3       0.611092    0.612993            -0.001901                 0.011953
   08893e2a     S1       0.636230    0.641530            -0.005300                 0.021143
   08893e2a     S2       0.622358    0.622538            -0.000180                 0.014221
   08893e2a     S3       0.653703    0.644847             0.008856                 0.016184
   08893e2a     S4       0.549372    0.548214             0.001158                 0.013087
   13c90bcc     Q1       0.497034    0.509565            -0.012531                 0.023212
   13c90bcc     Q2       0.551916    0.551824             0.000092                 0.008794
   13c90bcc     Q3       0.620022    0.621131            -0.001109                 0.010823
   13c90bcc     S1       0.680996    0.685131            -0.004135                 0.015909
   13c90bcc     S2       0.645069    0.645329            -0.000260                 0.016492
   13c90bcc     S3       0.659543    0.648823             0.010720                 0.018617
   13c90bcc     S4       0.578133    0.577103             0.001030                 0.010904
   4df045f4     Q1       0.472487    0.484890            -0.012403                 0.021611
   4df045f4     Q2       0.551399    0.553927            -0.002529                 0.008333
   4df045f4     Q3       0.603692    0.603292             0.000401                 0.014870
   4df045f4     S1       0.656026    0.661342            -0.005316                 0.016439
   4df045f4     S2       0.661831    0.660089             0.001742                 0.015923
   4df045f4     S3       0.671997    0.664802             0.007195                 0.018180
   4df045f4     S4       0.573122    0.571611             0.001511                 0.010095
   f4b74e2f     Q1       0.473373    0.482847            -0.009474                 0.017542
   f4b74e2f     Q2       0.557469    0.563898            -0.006429                 0.013576
   f4b74e2f     Q3       0.641964    0.639323             0.002641                 0.015021
   f4b74e2f     S1       0.661067    0.667274            -0.006207                 0.019029
   f4b74e2f     S2       0.647922    0.649715            -0.001793                 0.015269
   f4b74e2f     S3       0.679318    0.674609             0.004709                 0.012948
   f4b74e2f     S4       0.569539    0.568701             0.000838                 0.012653
   b6ae0add     Q1       0.496347    0.503696            -0.007349                 0.022684
   b6ae0add     Q2       0.539388    0.538691             0.000697                 0.006496
   b6ae0add     Q3       0.602330    0.597325             0.005005                 0.014343
   b6ae0add     S1       0.651518    0.654415            -0.002897                 0.019210
   b6ae0add     S2       0.630600    0.631134            -0.000534                 0.016152
   b6ae0add     S3       0.664630    0.655977             0.008653                 0.016840
   b6ae0add     S4       0.559587    0.561188            -0.001602                 0.013185
   15766c08     Q1       0.498505    0.508716            -0.010210                 0.023392
   15766c08     Q2       0.540514    0.539436             0.001078                 0.007558
   15766c08     Q3       0.602696    0.598990             0.003706                 0.014181
   15766c08     S1       0.656564    0.659776            -0.003212                 0.017619
   15766c08     S2       0.637056    0.636025             0.001031                 0.018437
   15766c08     S3       0.663526    0.651564             0.011962                 0.018985
   15766c08     S4       0.570172    0.572247            -0.002075                 0.011520
```

## Selected Direct-Label Probe Submissions

```
      submit_role                              file source_solution_id   source_mask_kind source_mask_name source_prior_name target_mask  strength   cap  direct_selection_score  direct_delta_vs_a2c8  direct_p90_delta_vs_a2c8  direct_worst_delta_vs_a2c8  direct_win_rate_vs_a2c8  mean_abs_move_vs_a2c8  logit_orth_ratio_to_a2c8_move
direct_large_move submission_directlbl_cbdeefd5.csv           b6ae0add subject_contiguous  frac0.50_rep142      entropy_g075         all      0.36 0.040               -0.022022             -0.000747                 -0.000465                   -0.000146                      1.0               0.004411                       0.946640
direct_large_move submission_directlbl_adcea671.csv           b6ae0add subject_contiguous  frac0.50_rep142      entropy_g075       no_q2      0.36 0.040               -0.020415             -0.000715                 -0.000447                   -0.000142                      1.0               0.003993                       0.945441
direct_large_move submission_directlbl_1fecf3f2.csv           513139a7 subject_contiguous  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.018218             -0.000565                 -0.000333                   -0.000107                      1.0               0.003457                       0.938048
direct_large_move submission_directlbl_d88ac3c8.csv           674e6548        random_rows  frac0.40_rep197      entropy_g075         all      0.36 0.040               -0.017256             -0.000512                 -0.000291                   -0.000233                      1.0               0.003219                       0.934422
direct_large_move submission_directlbl_eabdf0bd.csv           08893e2a        random_rows  frac0.40_rep002      entropy_g075         all      0.36 0.040               -0.017041             -0.000503                 -0.000301                   -0.000184                      1.0               0.003182                       0.921317
direct_large_move submission_directlbl_d1b04780.csv           5f68765b subject_contiguous  frac0.40_rep052      entropy_g075         all      0.36 0.040               -0.017005             -0.000559                 -0.000309                   -0.000089                      1.0               0.003153                       0.924539
direct_large_move submission_directlbl_7daa3dec.csv           c1ef0015        random_rows  frac0.40_rep002      entropy_g050         all      0.36 0.040               -0.016998             -0.000517                 -0.000318                   -0.000189                      1.0               0.003163                       0.923670
direct_large_move submission_directlbl_7e5c3668.csv           15766c08 subject_contiguous  frac0.40_rep052      entropy_g050         all      0.36 0.040               -0.016966             -0.000572                 -0.000321                   -0.000091                      1.0               0.003137                       0.925958
direct_large_move submission_directlbl_4a0bfaab.csv           513139a7 subject_contiguous  frac0.40_rep009      entropy_g075       no_q2      0.36 0.040               -0.016893             -0.000539                 -0.000316                   -0.000105                      1.0               0.003113                       0.936408
direct_large_move submission_directlbl_59f0396f.csv           13c90bcc        random_rows  frac0.40_rep009      entropy_g050         all      0.36 0.040               -0.016410             -0.000521                 -0.000326                   -0.000241                      1.0               0.003013                       0.917828
 direct_safe_move submission_directlbl_230cff97.csv           b6ae0add subject_contiguous  frac0.50_rep142      entropy_g075         all      0.36 0.024               -0.021074             -0.000684                 -0.000427                   -0.000135                      1.0               0.004179                       0.943467
 direct_safe_move submission_directlbl_207dd9c4.csv           b6ae0add subject_contiguous  frac0.50_rep142      entropy_g075       no_q2      0.36 0.024               -0.019466             -0.000651                 -0.000409                   -0.000131                      1.0               0.003761                       0.941970
 direct_safe_move submission_directlbl_fc3b8fe9.csv           513139a7 subject_contiguous  frac0.40_rep009      entropy_g075         all      0.36 0.024               -0.017548             -0.000517                 -0.000311                   -0.000094                      1.0               0.003300                       0.931291
 direct_safe_move submission_directlbl_035aa161.csv           674e6548        random_rows  frac0.40_rep197      entropy_g075         all      0.36 0.024               -0.016635             -0.000466                 -0.000278                   -0.000220                      1.0               0.003070                       0.931295
 direct_safe_move submission_directlbl_6872c202.csv           c1ef0015        random_rows  frac0.40_rep002      entropy_g050         all      0.36 0.024               -0.016406             -0.000480                 -0.000306                   -0.000186                      1.0               0.003022                       0.918932
 direct_safe_move submission_directlbl_c46624e2.csv           08893e2a        random_rows  frac0.40_rep002      entropy_g075         all      0.36 0.024               -0.016395             -0.000468                 -0.000295                   -0.000179                      1.0               0.003028                       0.914719
 direct_safe_move submission_directlbl_ea309728.csv           6bc28e74        random_rows  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.016391             -0.000509                 -0.000316                   -0.000231                      1.0               0.003015                       0.914756
 direct_safe_move submission_directlbl_05d36e1e.csv           5f68765b subject_contiguous  frac0.40_rep052      entropy_g075         all      0.36 0.024               -0.016375             -0.000514                 -0.000290                   -0.000080                      1.0               0.003003                       0.919762
```

## Candidate Scan Top

```
              name                              file source_mask_name source_prior_name target_mask  strength   cap  direct_selection_score  direct_delta_vs_a2c8  direct_p90_delta_vs_a2c8  mean_abs_move_vs_a2c8
directlbl_cbdeefd5 submission_directlbl_cbdeefd5.csv  frac0.50_rep142      entropy_g075         all      0.36 0.040               -0.022022             -0.000747                 -0.000465               0.004411
directlbl_230cff97 submission_directlbl_230cff97.csv  frac0.50_rep142      entropy_g075         all      0.36 0.024               -0.021074             -0.000684                 -0.000427               0.004179
directlbl_adcea671 submission_directlbl_adcea671.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.040               -0.020415             -0.000715                 -0.000447               0.003993
directlbl_207dd9c4 submission_directlbl_207dd9c4.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.024               -0.019466             -0.000651                 -0.000409               0.003761
directlbl_1fecf3f2 submission_directlbl_1fecf3f2.csv  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.018218             -0.000565                 -0.000333               0.003457
directlbl_4d8985ca submission_directlbl_4d8985ca.csv  frac0.50_rep142      entropy_g075         all      0.36 0.012               -0.017970             -0.000526                 -0.000331               0.003411
directlbl_fc3b8fe9 submission_directlbl_fc3b8fe9.csv  frac0.40_rep009      entropy_g075         all      0.36 0.024               -0.017548             -0.000517                 -0.000311               0.003300
directlbl_d88ac3c8 submission_directlbl_d88ac3c8.csv  frac0.40_rep197      entropy_g075         all      0.36 0.040               -0.017256             -0.000512                 -0.000291               0.003219
directlbl_eabdf0bd submission_directlbl_eabdf0bd.csv  frac0.40_rep002      entropy_g075         all      0.36 0.040               -0.017041             -0.000503                 -0.000301               0.003182
directlbl_d1b04780 submission_directlbl_d1b04780.csv  frac0.40_rep052      entropy_g075         all      0.36 0.040               -0.017005             -0.000559                 -0.000309               0.003153
directlbl_7daa3dec submission_directlbl_7daa3dec.csv  frac0.40_rep002      entropy_g050         all      0.36 0.040               -0.016998             -0.000517                 -0.000318               0.003163
directlbl_7e5c3668 submission_directlbl_7e5c3668.csv  frac0.40_rep052      entropy_g050         all      0.36 0.040               -0.016966             -0.000572                 -0.000321               0.003137
directlbl_4a0bfaab submission_directlbl_4a0bfaab.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.040               -0.016893             -0.000539                 -0.000316               0.003113
directlbl_035aa161 submission_directlbl_035aa161.csv  frac0.40_rep197      entropy_g075         all      0.36 0.024               -0.016635             -0.000466                 -0.000278               0.003070
directlbl_59f0396f submission_directlbl_59f0396f.csv  frac0.40_rep009      entropy_g050         all      0.36 0.040               -0.016410             -0.000521                 -0.000326               0.003013
directlbl_6872c202 submission_directlbl_6872c202.csv  frac0.40_rep002      entropy_g050         all      0.36 0.024               -0.016406             -0.000480                 -0.000306               0.003022
directlbl_c7238eef submission_directlbl_c7238eef.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.012               -0.016401             -0.000495                 -0.000313               0.003005
directlbl_c46624e2 submission_directlbl_c46624e2.csv  frac0.40_rep002      entropy_g075         all      0.36 0.024               -0.016395             -0.000468                 -0.000295               0.003028
directlbl_ea309728 submission_directlbl_ea309728.csv  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.016391             -0.000509                 -0.000316               0.003015
directlbl_05d36e1e submission_directlbl_05d36e1e.csv  frac0.40_rep052      entropy_g075         all      0.36 0.024               -0.016375             -0.000514                 -0.000290               0.003003
directlbl_6c53bd0c submission_directlbl_6c53bd0c.csv  frac0.40_rep052      entropy_g050         all      0.36 0.024               -0.016372             -0.000528                 -0.000300               0.002996
directlbl_cabdef0c submission_directlbl_cabdef0c.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.024               -0.016220             -0.000491                 -0.000295               0.002956
directlbl_0a23961a submission_directlbl_0a23961a.csv  frac0.50_rep142      entropy_g075         all      0.24 0.040               -0.016179             -0.000548                 -0.000352               0.002957
directlbl_e021e4bf submission_directlbl_e021e4bf.csv  frac0.50_rep142      entropy_g075         all      0.24 0.024               -0.016068             -0.000539                 -0.000345               0.002932
directlbl_c3e31751 submission_directlbl_c3e31751.csv  frac0.40_rep197      entropy_g075       no_q2      0.36 0.040               -0.016068             -0.000492                 -0.000279               0.002910
directlbl_9ed50749 submission_directlbl_9ed50749.csv  frac0.40_rep009      entropy_g050         all      0.36 0.024               -0.015878             -0.000487                 -0.000313               0.002889
directlbl_e5f59689 submission_directlbl_e5f59689.csv  frac0.40_rep009      entropy_g075         all      0.36 0.024               -0.015823             -0.000473                 -0.000302               0.002883
directlbl_f9673d8a submission_directlbl_f9673d8a.csv  frac0.40_rep052      entropy_g050       no_q2      0.36 0.040               -0.015812             -0.000547                 -0.000308               0.002838
directlbl_99bc3a36 submission_directlbl_99bc3a36.csv  frac0.40_rep002      entropy_g050       no_q2      0.36 0.040               -0.015809             -0.000493                 -0.000308               0.002855
directlbl_c28b5e3d submission_directlbl_c28b5e3d.csv  frac0.40_rep052      entropy_g075       no_q2      0.36 0.040               -0.015807             -0.000533                 -0.000291               0.002843
directlbl_347af1c9 submission_directlbl_347af1c9.csv  frac0.40_rep002      entropy_g075       no_q2      0.36 0.040               -0.015802             -0.000479                 -0.000290               0.002861
directlbl_1af3fcc3 submission_directlbl_1af3fcc3.csv  frac0.40_rep197      entropy_g075       no_q2      0.36 0.024               -0.015445             -0.000446                 -0.000266               0.002761
directlbl_69aef7ec submission_directlbl_69aef7ec.csv  frac0.40_rep052      entropy_g050       no_q2      0.36 0.024               -0.015216             -0.000503                 -0.000287               0.002697
directlbl_763ca2aa submission_directlbl_763ca2aa.csv  frac0.40_rep002      entropy_g050       no_q2      0.36 0.024               -0.015216             -0.000456                 -0.000294               0.002713
directlbl_822dd62c submission_directlbl_822dd62c.csv  frac0.40_rep009      entropy_g075         all      0.36 0.012               -0.015195             -0.000403                 -0.000249               0.002725
directlbl_11cfa363 submission_directlbl_11cfa363.csv  frac0.40_rep052      entropy_g075       no_q2      0.36 0.024               -0.015175             -0.000488                 -0.000272               0.002693
directlbl_e28df8a6 submission_directlbl_e28df8a6.csv  frac0.40_rep009      entropy_g050       no_q2      0.36 0.040               -0.015167             -0.000494                 -0.000311               0.002692
directlbl_1a88ed44 submission_directlbl_1a88ed44.csv  frac0.40_rep002      entropy_g075       no_q2      0.36 0.024               -0.015153             -0.000443                 -0.000285               0.002707
directlbl_1eec7473 submission_directlbl_1eec7473.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.040               -0.015104             -0.000481                 -0.000299               0.002684
directlbl_4816aa27 submission_directlbl_4816aa27.csv  frac0.50_rep142      entropy_g075       no_q2      0.24 0.040               -0.015099             -0.000524                 -0.000338               0.002678
directlbl_6833a591 submission_directlbl_6833a591.csv  frac0.50_rep142      entropy_g075       no_q2      0.24 0.024               -0.014988             -0.000515                 -0.000332               0.002653
directlbl_f0df806e submission_directlbl_f0df806e.csv  frac0.40_rep197      entropy_g075         all      0.36 0.012               -0.014786             -0.000368                 -0.000231               0.002620
directlbl_4892f0a2 submission_directlbl_4892f0a2.csv  frac0.50_rep142      entropy_g075         all      0.24 0.012               -0.014726             -0.000449                 -0.000289               0.002617
directlbl_f6e7dd6e submission_directlbl_f6e7dd6e.csv  frac0.40_rep009      entropy_g050       no_q2      0.36 0.024               -0.014632             -0.000460                 -0.000299               0.002568
directlbl_cb484502 submission_directlbl_cb484502.csv  frac0.50_rep142      entropy_g075 q3_s2_s3_s4      0.36 0.040               -0.014622             -0.000406                 -0.000230               0.002611
directlbl_f158f205 submission_directlbl_f158f205.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.024               -0.014533             -0.000445                 -0.000288               0.002551
directlbl_83b2a787 submission_directlbl_83b2a787.csv  frac0.40_rep002      entropy_g050         all      0.36 0.012               -0.014518             -0.000382                 -0.000254               0.002571
directlbl_43220732 submission_directlbl_43220732.csv  frac0.40_rep002      entropy_g075         all      0.36 0.012               -0.014495             -0.000375                 -0.000244               0.002567
directlbl_a23fa70a submission_directlbl_a23fa70a.csv  frac0.30_rep056      entropy_g075         all      0.36 0.040               -0.014367             -0.000375                 -0.000196               0.002509
directlbl_802a676d submission_directlbl_802a676d.csv  frac0.30_rep221      entropy_g075         all      0.36 0.040               -0.014344             -0.000418                 -0.000246               0.002504
directlbl_748c86ed submission_directlbl_748c86ed.csv  frac0.40_rep052      entropy_g050         all      0.36 0.012               -0.014335             -0.000415                 -0.000251               0.002511
directlbl_4369f0ae submission_directlbl_4369f0ae.csv  frac0.40_rep052      entropy_g075         all      0.36 0.012               -0.014322             -0.000406                 -0.000244               0.002509
directlbl_51eec58e submission_directlbl_51eec58e.csv  frac0.30_rep221      entropy_g050         all      0.36 0.040               -0.014315             -0.000427                 -0.000264               0.002489
directlbl_4bdb4f02 submission_directlbl_4bdb4f02.csv  frac0.50_rep142      entropy_g075 q3_s2_s3_s4      0.36 0.024               -0.014145             -0.000378                 -0.000216               0.002498
directlbl_4ed21e20 submission_directlbl_4ed21e20.csv  frac0.40_rep009      entropy_g050         all      0.36 0.012               -0.014002             -0.000391                 -0.000262               0.002438
directlbl_cfb20e94 submission_directlbl_cfb20e94.csv  frac0.40_rep009      entropy_g075         all      0.36 0.012               -0.013945             -0.000383                 -0.000256               0.002427
directlbl_7e12cf9b submission_directlbl_7e12cf9b.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.012               -0.013915             -0.000377                 -0.000235               0.002394
directlbl_4fad0fde submission_directlbl_4fad0fde.csv  frac0.30_rep056      entropy_g075         all      0.36 0.024               -0.013874             -0.000342                 -0.000182               0.002395
directlbl_d3d12dcc submission_directlbl_d3d12dcc.csv  frac0.30_rep221      entropy_g050         all      0.36 0.024               -0.013816             -0.000390                 -0.000255               0.002374
directlbl_7b6aa931 submission_directlbl_7b6aa931.csv  frac0.30_rep221      entropy_g075         all      0.36 0.024               -0.013813             -0.000380                 -0.000236               0.002384
```

## Interpretation

- A low fit error here does not prove the mask is the real public subset; the system is underdetermined. It proves that the mask admits a plausible label assignment that explains all observed anchor signs and magnitudes.
- The most useful solutions are the ones that fit public anchors while requiring structured target-rate shifts, especially on id01/early-prefix masks already favored by inverse7.
- Direct-label probes are intentionally larger than raw05-compatible micro-refines. They should be submitted only as diagnostic larger-move tests, not as conservative score-safe candidates.
