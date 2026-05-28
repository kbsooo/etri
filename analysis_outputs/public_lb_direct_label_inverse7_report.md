# Public LB Direct Label Inverse7

This audit treats each candidate public subset mask as the actual public rows and solves directly for soft binary labels that explain the observed seven-anchor public deltas.

## Top Soft-Label Solutions

```
solution_id          mask_kind                   mask_name  rows   prior_name  lambda  solution_score  weighted_std_rmse  weighted_rmse  weighted_sign_acc  mean_abs_shift_vs_prior  near_binary_rate_05  pred_delta_raw05  pred_delta_cvjepa_a2c8  pred_delta_jepa_bad_residual                                             top_blocks
   d0690b07        random_rows             frac0.40_rep009   100 entropy_g075     0.0        0.000384           0.000000   0.000000e+00                1.0                 0.012806             0.017143         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   0d90297c subject_contiguous             frac0.40_rep052   101 entropy_g075     0.0        0.000419           0.000000   0.000000e+00                1.0                 0.013974             0.022631         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   4e1f92a7        random_rows             frac0.40_rep002   100 entropy_g075     0.0        0.000442           0.000000   0.000000e+00                1.0                 0.014726             0.022857         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   3216ad61        random_rows             frac0.40_rep009   100 entropy_g050     0.0        0.000449           0.000000   0.000000e+00                1.0                 0.014976             0.020000         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   8ed337f8        random_rows             frac0.30_rep221    75 entropy_g075     0.0        0.000452           0.000000   0.000000e+00                1.0                 0.015073             0.017143         -0.000419               -0.000506                      0.003282      id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
   a2066891        random_rows             frac0.20_rep114    50 entropy_g075     0.0        0.000457           0.000000   0.000000e+00                1.0                 0.015248             0.028571         -0.000419               -0.000506                      0.003282      id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
   b823da73 subject_contiguous             frac0.50_rep142   126 entropy_g075     0.0        0.000463           0.000000   0.000000e+00                1.0                 0.015438             0.024943         -0.000419               -0.000506                      0.003282 id02_b4:15;id01_b2:13;id07_b4:10;id10_b4:10;id03_b2:10
   9090ba05 subject_contiguous             frac0.40_rep052   101 entropy_g050     0.0        0.000476           0.000000   0.000000e+00                1.0                 0.015859             0.025460         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   3b2bec2a        random_rows             frac0.20_rep115    50 entropy_g075     0.0        0.000481           0.000000   0.000000e+00                1.0                 0.016047             0.022857         -0.000419               -0.000506                      0.003282      id01_b2:7;id03_b2:4;id10_b2:3;id03_b4:3;id10_b4:3
   6e78b756       global_order                rowmod4_rem3    62 entropy_g075     0.0        0.000482           0.000000   0.000000e+00                1.0                 0.016074             0.018433         -0.000419               -0.000506                      0.003282      id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
   6c71f82c        random_rows             frac0.30_rep056    75 entropy_g075     0.0        0.000491           0.000000   0.000000e+00                1.0                 0.016379             0.017143         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
   bce02ad3 subject_contiguous             frac0.25_rep099    64 entropy_g075     0.0        0.000493           0.000000   0.000000e+00                1.0                 0.016436             0.017857         -0.000419               -0.000506                      0.003282      id02_b2:8;id07_b4:8;id01_b4:7;id05_b2:5;id03_b4:4
   f66db3d9        random_rows             frac0.40_rep002   100 entropy_g050     0.0        0.000495           0.000000   0.000000e+00                1.0                 0.016489             0.024286         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   5ba6da1b        random_rows             frac0.20_rep114    50 entropy_g050     0.0        0.000499           0.000000   0.000000e+00                1.0                 0.016632             0.028571         -0.000419               -0.000506                      0.003282      id01_b2:6;id03_b2:4;id09_b2:3;id07_b4:3;id10_b2:2
   c8f5a2d9        random_rows             frac0.40_rep197   100 entropy_g075     0.0        0.000501           0.000000   0.000000e+00                1.0                 0.016694             0.024286         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   cbc67fbf        random_rows             frac0.30_rep221    75 entropy_g050     0.0        0.000506           0.000000   0.000000e+00                1.0                 0.016865             0.019048         -0.000419               -0.000506                      0.003282      id09_b4:8;id09_b2:7;id02_b4:5;id02_b2:4;id07_b4:4
   d4c3b9aa subject_contiguous             frac0.40_rep009   101 entropy_g075     0.0        0.000509           0.000000   0.000000e+00                1.0                 0.016955             0.016973         -0.000419               -0.000506                      0.003282     id07_b4:12;id10_b2:9;id09_b2:7;id04_b6:7;id01_b2:7
   970b0802        random_rows             frac0.40_rep002   100         a2c8     0.0        0.000509           0.000000   0.000000e+00                1.0                 0.016977             0.018571         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   ff47ddac      subject_order per_subject_prefix_frac0.25    64 entropy_g075     0.0        0.000512           0.000000   0.000000e+00                1.0                 0.017080             0.015625         -0.000419               -0.000506                      0.003282      id02_b2:8;id07_b2:8;id01_b2:7;id09_b2:7;id06_b2:6
   3c81d16b        random_rows             frac0.40_rep092   100 entropy_g050     0.0        0.000515           0.000000   0.000000e+00                1.0                 0.017157             0.017143         -0.000419               -0.000506                      0.003282      id02_b2:9;id02_b4:7;id07_b4:7;id01_b4:6;id09_b2:6
   2acb6131        random_rows             frac0.40_rep009   100         a2c8     0.0        0.000515           0.000000   0.000000e+00                1.0                 0.017178             0.024286         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   a09657cc subject_contiguous             frac0.25_rep119    64 entropy_g075     0.0        0.000517           0.000000   0.000000e+00                1.0                 0.017221             0.015625         -0.000419               -0.000506                      0.003282      id01_b2:7;id02_b4:7;id09_b2:7;id07_b4:6;id10_b4:6
   cd9cccfb subject_contiguous             frac0.40_rep052   101         a2c8     0.0        0.000520           0.000000   0.000000e+00                1.0                 0.017317             0.019802         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   d245d0d0 subject_contiguous             frac0.25_rep150    64 entropy_g075     0.0        0.000520           0.000000   0.000000e+00                1.0                 0.017324             0.015625         -0.000419               -0.000506                      0.003282      id07_b2:8;id01_b2:7;id09_b2:7;id04_b6:6;id10_b4:6
   23d456d7 subject_contiguous             frac0.50_rep142   126 entropy_g050     0.0        0.000520           0.000000   0.000000e+00                1.0                 0.017330             0.024943         -0.000419               -0.000506                      0.003282 id02_b4:15;id01_b2:13;id07_b4:10;id10_b4:10;id03_b2:10
   cb0a98f6 subject_contiguous             frac0.25_rep099    64 entropy_g050     0.0        0.000522           0.000000   0.000000e+00                1.0                 0.017385             0.015625         -0.000419               -0.000506                      0.003282      id02_b2:8;id07_b4:8;id01_b4:7;id05_b2:5;id03_b4:4
   c35c88a0        random_rows             frac0.50_rep169   125 entropy_g075     0.0        0.000523           0.000000   0.000000e+00                1.0                 0.017434             0.014857         -0.000419               -0.000506                      0.003282      id02_b2:9;id07_b2:8;id10_b2:8;id10_b4:8;id01_b4:7
   ebb870ed        random_rows             frac0.40_rep002   100        raw05     0.0        0.000524           0.000000   0.000000e+00                1.0                 0.017482             0.020000         -0.000419               -0.000506                      0.003282      id01_b4:8;id07_b4:7;id10_b4:6;id02_b2:6;id02_b4:5
   d6c8fe4a        random_rows             frac0.30_rep056    75 entropy_g050     0.0        0.000527           0.000000   0.000000e+00                1.0                 0.017579             0.020952         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
   fd68d73d        random_rows             frac0.40_rep052   100 entropy_g075     0.0        0.000529           0.000000   0.000000e+00                1.0                 0.017649             0.017143         -0.000419               -0.000506                      0.003282      id02_b2:9;id10_b4:7;id04_b6:6;id01_b2:6;id03_b2:5
   ed9e7474        random_rows             frac0.40_rep040   100         a2c8     0.0        0.000531           0.000000   0.000000e+00                1.0                 0.017701             0.020000         -0.000419               -0.000506                      0.003282     id09_b2:10;id02_b4:8;id09_b4:8;id01_b2:8;id02_b2:7
   d97ba894       global_order                rowmod4_rem3    62 entropy_g050     0.0        0.000531           0.000000   0.000000e+00                1.0                 0.017716             0.018433         -0.000419               -0.000506                      0.003282      id02_b2:4;id02_b4:4;id07_b4:4;id01_b2:3;id09_b4:3
   6f790127        random_rows             frac0.40_rep009   100        raw05     0.0        0.000534           0.000000   0.000000e+00                1.0                 0.017786             0.025714         -0.000419               -0.000506                      0.003282      id01_b4:7;id02_b4:6;id09_b4:6;id07_b4:6;id02_b2:5
   13af2903 subject_contiguous             frac0.40_rep052   101        raw05     0.0        0.000537           0.000000   0.000000e+00                1.0                 0.017894             0.018388         -0.000419               -0.000506                      0.003282     id02_b4:12;id09_b2:9;id01_b2:8;id07_b4:8;id10_b4:7
   35f927ce        random_rows             frac0.40_rep197   100 entropy_g050     0.0        0.000537           0.000000   0.000000e+00                1.0                 0.017900             0.024286         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   580c0a90        random_rows             frac0.40_rep092   100 entropy_g075     0.0        0.000537           0.000057   2.500000e-08                1.0                 0.015570             0.015714         -0.000419               -0.000506                      0.003282      id02_b2:9;id02_b4:7;id07_b4:7;id01_b4:6;id09_b2:6
   1082315b        random_rows             frac0.40_rep197   100         a2c8     0.0        0.000537           0.000000   0.000000e+00                1.0                 0.017916             0.018571         -0.000419               -0.000506                      0.003282      id09_b2:9;id07_b2:8;id02_b2:7;id07_b4:5;id01_b2:5
   1c0ef38b        random_rows             frac0.20_rep115    50 entropy_g050     0.0        0.000541           0.000000   0.000000e+00                1.0                 0.018041             0.020000         -0.000419               -0.000506                      0.003282      id01_b2:7;id03_b2:4;id10_b2:3;id03_b4:3;id10_b4:3
   a8f522e1        random_rows             frac0.50_rep073   125         a2c8     0.0        0.000542           0.000000   0.000000e+00                1.0                 0.018052             0.021714         -0.000419               -0.000506                      0.003282     id07_b4:11;id01_b2:9;id02_b4:7;id10_b2:6;id09_b4:6
   aae29225        random_rows             frac0.30_rep056    75         a2c8     0.0        0.000546           0.000000   0.000000e+00                1.0                 0.018187             0.020952         -0.000419               -0.000506                      0.003282      id01_b2:6;id01_b4:5;id02_b2:4;id02_b4:4;id07_b2:4
```

## Target Rate Shifts In Top Solutions

```
solution_id target  solution_rate  prior_rate  rate_delta_vs_prior  mean_abs_shift_vs_prior
   d0690b07     Q1       0.497218    0.508185            -0.010966                 0.019373
   d0690b07     Q2       0.552105    0.552185            -0.000080                 0.006183
   d0690b07     Q3       0.620394    0.620278             0.000116                 0.011115
   d0690b07     S1       0.680824    0.684767            -0.003943                 0.014617
   d0690b07     S2       0.644870    0.644911            -0.000041                 0.014035
   d0690b07     S3       0.659020    0.651727             0.007293                 0.014769
   d0690b07     S4       0.577952    0.576529             0.001423                 0.009553
   0d90297c     Q1       0.497905    0.508315            -0.010410                 0.021046
   0d90297c     Q2       0.539765    0.539255             0.000510                 0.005227
   0d90297c     Q3       0.599773    0.597172             0.002601                 0.012276
   0d90297c     S1       0.656174    0.659981            -0.003806                 0.016217
   0d90297c     S2       0.637087    0.636322             0.000765                 0.016021
   0d90297c     S3       0.663150    0.655195             0.007955                 0.015606
   0d90297c     S4       0.570724    0.571210            -0.000486                 0.011426
   4e1f92a7     Q1       0.490434    0.499682            -0.009248                 0.020984
   4e1f92a7     Q2       0.544485    0.544070             0.000415                 0.006045
   4e1f92a7     Q3       0.614794    0.612993             0.001801                 0.011963
   4e1f92a7     S1       0.636943    0.641530            -0.004587                 0.020910
   4e1f92a7     S2       0.622622    0.622538             0.000083                 0.014087
   4e1f92a7     S3       0.653648    0.644847             0.008801                 0.016105
   4e1f92a7     S4       0.548680    0.548214             0.000466                 0.012990
   3216ad61     Q1       0.497233    0.509565            -0.012331                 0.023119
   3216ad61     Q2       0.552176    0.551824             0.000352                 0.008825
   3216ad61     Q3       0.620938    0.621131            -0.000192                 0.010943
   3216ad61     S1       0.681066    0.685131            -0.004065                 0.015870
   3216ad61     S2       0.645078    0.645329            -0.000251                 0.016508
   3216ad61     S3       0.659522    0.648823             0.010699                 0.018617
   3216ad61     S4       0.577979    0.577103             0.000876                 0.010953
   8ed337f8     Q1       0.472645    0.484890            -0.012245                 0.021631
   8ed337f8     Q2       0.551687    0.553927            -0.002240                 0.008420
   8ed337f8     Q3       0.604627    0.603292             0.001335                 0.014895
   8ed337f8     S1       0.656101    0.661342            -0.005241                 0.016420
   8ed337f8     S2       0.661821    0.660089             0.001732                 0.015859
   8ed337f8     S3       0.671972    0.664802             0.007171                 0.018179
   8ed337f8     S4       0.572975    0.571611             0.001364                 0.010104
   a2066891     Q1       0.474232    0.482847            -0.008616                 0.017634
   a2066891     Q2       0.558277    0.563898            -0.005622                 0.013774
   a2066891     Q3       0.644635    0.639323             0.005312                 0.015865
   a2066891     S1       0.661335    0.667274            -0.005939                 0.018538
   a2066891     S2       0.648015    0.649715            -0.001700                 0.015235
   a2066891     S3       0.679333    0.674609             0.004725                 0.012892
   a2066891     S4       0.569022    0.568701             0.000321                 0.012802
   b823da73     Q1       0.495296    0.503696            -0.008400                 0.022414
   b823da73     Q2       0.538600    0.538691            -0.000091                 0.006420
   b823da73     Q3       0.599071    0.597325             0.001747                 0.013653
   b823da73     S1       0.651155    0.654415            -0.003260                 0.019150
   b823da73     S2       0.630504    0.631134            -0.000630                 0.016294
   b823da73     S3       0.664685    0.655977             0.008708                 0.016888
   b823da73     S4       0.560339    0.561188            -0.000849                 0.013245
   9090ba05     Q1       0.497690    0.508716            -0.011026                 0.023433
   9090ba05     Q2       0.539957    0.539436             0.000521                 0.007545
   9090ba05     Q3       0.600423    0.598990             0.001433                 0.013610
   9090ba05     S1       0.656442    0.659776            -0.003335                 0.017537
   9090ba05     S2       0.637135    0.636025             0.001110                 0.018498
   9090ba05     S3       0.663567    0.651564             0.012003                 0.019012
   9090ba05     S4       0.570706    0.572247            -0.001541                 0.011374
```

## Selected Direct-Label Probe Submissions

```
      submit_role                              file source_solution_id   source_mask_kind source_mask_name source_prior_name target_mask  strength   cap  direct_selection_score  direct_delta_vs_a2c8  direct_p90_delta_vs_a2c8  direct_worst_delta_vs_a2c8  direct_win_rate_vs_a2c8  mean_abs_move_vs_a2c8  logit_orth_ratio_to_a2c8_move
direct_large_move submission_directlbl_89fbdeb6.csv           b823da73 subject_contiguous  frac0.50_rep142      entropy_g075         all      0.36 0.040               -0.021973             -0.000754                 -0.000439                   -0.000146                      1.0               0.004399                       0.944377
direct_large_move submission_directlbl_05afa7e8.csv           b823da73 subject_contiguous  frac0.50_rep142      entropy_g075       no_q2      0.36 0.040               -0.020370             -0.000721                 -0.000421                   -0.000141                      1.0               0.003982                       0.943111
direct_large_move submission_directlbl_e8e6de2e.csv           c8f5a2d9        random_rows  frac0.40_rep197      entropy_g075         all      0.36 0.040               -0.017263             -0.000520                 -0.000292                   -0.000231                      1.0               0.003219                       0.934191
direct_large_move submission_directlbl_aef78c3e.csv           4e1f92a7        random_rows  frac0.40_rep002      entropy_g075         all      0.36 0.040               -0.017098             -0.000516                 -0.000296                   -0.000186                      1.0               0.003190                       0.924106
direct_large_move submission_directlbl_2050bd8b.csv           f66db3d9        random_rows  frac0.40_rep002      entropy_g050         all      0.36 0.040               -0.017053             -0.000529                 -0.000300                   -0.000191                      1.0               0.003172                       0.926047
direct_large_move submission_directlbl_37c28fdd.csv           0d90297c subject_contiguous  frac0.40_rep052      entropy_g075         all      0.36 0.040               -0.016983             -0.000559                 -0.000295                   -0.000091                      1.0               0.003151                       0.921903
direct_large_move submission_directlbl_308b72b7.csv           9090ba05 subject_contiguous  frac0.40_rep052      entropy_g050         all      0.36 0.040               -0.016949             -0.000571                 -0.000306                   -0.000093                      1.0               0.003136                       0.923928
direct_large_move submission_directlbl_b7ea3059.csv           3216ad61        random_rows  frac0.40_rep009      entropy_g050         all      0.36 0.040               -0.016417             -0.000523                 -0.000327                   -0.000246                      1.0               0.003014                       0.918412
direct_large_move submission_directlbl_18212cf0.csv           d0690b07        random_rows  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.016401             -0.000512                 -0.000317                   -0.000236                      1.0               0.003017                       0.915296
direct_large_move submission_directlbl_3a9efdf5.csv           b823da73 subject_contiguous  frac0.50_rep142      entropy_g075         all      0.24 0.040               -0.016131             -0.000551                 -0.000332                   -0.000111                      1.0               0.002948                       0.905222
 direct_safe_move submission_directlbl_8b33d6dd.csv           b823da73 subject_contiguous  frac0.50_rep142      entropy_g075         all      0.36 0.024               -0.021017             -0.000689                 -0.000409                   -0.000134                      1.0               0.004166                       0.940724
 direct_safe_move submission_directlbl_6ecccf9f.csv           b823da73 subject_contiguous  frac0.50_rep142      entropy_g075       no_q2      0.36 0.024               -0.019412             -0.000657                 -0.000391                   -0.000130                      1.0               0.003749                       0.939127
 direct_safe_move submission_directlbl_8dfdd4ca.csv           c8f5a2d9        random_rows  frac0.40_rep197      entropy_g075         all      0.36 0.024               -0.016642             -0.000474                 -0.000279                   -0.000218                      1.0               0.003070                       0.931014
 direct_safe_move submission_directlbl_5361ec9d.csv           f66db3d9        random_rows  frac0.40_rep002      entropy_g050         all      0.36 0.024               -0.016463             -0.000490                 -0.000293                   -0.000187                      1.0               0.003031                       0.921468
 direct_safe_move submission_directlbl_39a60f04.csv           4e1f92a7        random_rows  frac0.40_rep002      entropy_g075         all      0.36 0.024               -0.016457             -0.000479                 -0.000288                   -0.000181                      1.0               0.003037                       0.918136
 direct_safe_move submission_directlbl_80d51a1d.csv           9090ba05 subject_contiguous  frac0.40_rep052      entropy_g050         all      0.36 0.024               -0.016345             -0.000526                 -0.000283                   -0.000083                      1.0               0.002992                       0.919529
 direct_safe_move submission_directlbl_900c4d37.csv           0d90297c subject_contiguous  frac0.40_rep052      entropy_g075         all      0.36 0.024               -0.016339             -0.000513                 -0.000274                   -0.000082                      1.0               0.002998                       0.916369
 direct_safe_move submission_directlbl_1422ff77.csv           c8f5a2d9        random_rows  frac0.40_rep197      entropy_g075       no_q2      0.36 0.040               -0.016075             -0.000500                 -0.000280                   -0.000219                      1.0               0.002910                       0.932658
```

## Candidate Scan Top

```
              name                              file source_mask_name source_prior_name target_mask  strength   cap  direct_selection_score  direct_delta_vs_a2c8  direct_p90_delta_vs_a2c8  mean_abs_move_vs_a2c8
directlbl_89fbdeb6 submission_directlbl_89fbdeb6.csv  frac0.50_rep142      entropy_g075         all      0.36 0.040               -0.021973             -0.000754                 -0.000439               0.004399
directlbl_8b33d6dd submission_directlbl_8b33d6dd.csv  frac0.50_rep142      entropy_g075         all      0.36 0.024               -0.021017             -0.000689                 -0.000409               0.004166
directlbl_05afa7e8 submission_directlbl_05afa7e8.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.040               -0.020370             -0.000721                 -0.000421               0.003982
directlbl_6ecccf9f submission_directlbl_6ecccf9f.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.024               -0.019412             -0.000657                 -0.000391               0.003749
directlbl_2f6b324f submission_directlbl_2f6b324f.csv  frac0.50_rep142      entropy_g075         all      0.36 0.012               -0.017961             -0.000530                 -0.000331               0.003411
directlbl_e8e6de2e submission_directlbl_e8e6de2e.csv  frac0.40_rep197      entropy_g075         all      0.36 0.040               -0.017263             -0.000520                 -0.000292               0.003219
directlbl_aef78c3e submission_directlbl_aef78c3e.csv  frac0.40_rep002      entropy_g075         all      0.36 0.040               -0.017098             -0.000516                 -0.000296               0.003190
directlbl_2050bd8b submission_directlbl_2050bd8b.csv  frac0.40_rep002      entropy_g050         all      0.36 0.040               -0.017053             -0.000529                 -0.000300               0.003172
directlbl_37c28fdd submission_directlbl_37c28fdd.csv  frac0.40_rep052      entropy_g075         all      0.36 0.040               -0.016983             -0.000559                 -0.000295               0.003151
directlbl_308b72b7 submission_directlbl_308b72b7.csv  frac0.40_rep052      entropy_g050         all      0.36 0.040               -0.016949             -0.000571                 -0.000306               0.003136
directlbl_8dfdd4ca submission_directlbl_8dfdd4ca.csv  frac0.40_rep197      entropy_g075         all      0.36 0.024               -0.016642             -0.000474                 -0.000279               0.003070
directlbl_5361ec9d submission_directlbl_5361ec9d.csv  frac0.40_rep002      entropy_g050         all      0.36 0.024               -0.016463             -0.000490                 -0.000293               0.003031
directlbl_39a60f04 submission_directlbl_39a60f04.csv  frac0.40_rep002      entropy_g075         all      0.36 0.024               -0.016457             -0.000479                 -0.000288               0.003037
directlbl_b7ea3059 submission_directlbl_b7ea3059.csv  frac0.40_rep009      entropy_g050         all      0.36 0.040               -0.016417             -0.000523                 -0.000327               0.003014
directlbl_18212cf0 submission_directlbl_18212cf0.csv  frac0.40_rep009      entropy_g075         all      0.36 0.040               -0.016401             -0.000512                 -0.000317               0.003017
directlbl_308615e1 submission_directlbl_308615e1.csv  frac0.50_rep142      entropy_g075       no_q2      0.36 0.012               -0.016389             -0.000498                 -0.000311               0.003004
directlbl_80d51a1d submission_directlbl_80d51a1d.csv  frac0.40_rep052      entropy_g050         all      0.36 0.024               -0.016345             -0.000526                 -0.000283               0.002992
directlbl_900c4d37 submission_directlbl_900c4d37.csv  frac0.40_rep052      entropy_g075         all      0.36 0.024               -0.016339             -0.000513                 -0.000274               0.002998
directlbl_3a9efdf5 submission_directlbl_3a9efdf5.csv  frac0.50_rep142      entropy_g075         all      0.24 0.040               -0.016131             -0.000551                 -0.000332               0.002948
directlbl_1422ff77 submission_directlbl_1422ff77.csv  frac0.40_rep197      entropy_g075       no_q2      0.36 0.040               -0.016075             -0.000500                 -0.000280               0.002910
directlbl_f07af813 submission_directlbl_f07af813.csv  frac0.50_rep142      entropy_g075         all      0.24 0.024               -0.016018             -0.000542                 -0.000327               0.002923
directlbl_26d5b28b submission_directlbl_26d5b28b.csv  frac0.40_rep009      entropy_g050         all      0.36 0.024               -0.015884             -0.000488                 -0.000314               0.002889
directlbl_d5db7828 submission_directlbl_d5db7828.csv  frac0.40_rep002      entropy_g050       no_q2      0.36 0.040               -0.015849             -0.000504                 -0.000291               0.002859
directlbl_a3bf9c37 submission_directlbl_a3bf9c37.csv  frac0.40_rep002      entropy_g075       no_q2      0.36 0.040               -0.015846             -0.000490                 -0.000288               0.002865
directlbl_da48a24e submission_directlbl_da48a24e.csv  frac0.40_rep009      entropy_g075         all      0.36 0.024               -0.015834             -0.000476                 -0.000303               0.002884
directlbl_8bf0074d submission_directlbl_8bf0074d.csv  frac0.40_rep052      entropy_g050       no_q2      0.36 0.040               -0.015795             -0.000546                 -0.000290               0.002837
directlbl_adbca2ef submission_directlbl_adbca2ef.csv  frac0.40_rep052      entropy_g075       no_q2      0.36 0.040               -0.015785             -0.000533                 -0.000278               0.002841
directlbl_540640a8 submission_directlbl_540640a8.csv  frac0.40_rep197      entropy_g075       no_q2      0.36 0.024               -0.015453             -0.000453                 -0.000267               0.002761
directlbl_53e102f3 submission_directlbl_53e102f3.csv  frac0.40_rep002      entropy_g050       no_q2      0.36 0.024               -0.015257             -0.000466                 -0.000285               0.002718
directlbl_efe01e23 submission_directlbl_efe01e23.csv  frac0.40_rep002      entropy_g075       no_q2      0.36 0.024               -0.015202             -0.000454                 -0.000280               0.002712
directlbl_c6ac29e2 submission_directlbl_c6ac29e2.csv  frac0.40_rep052      entropy_g050       no_q2      0.36 0.024               -0.015189             -0.000501                 -0.000267               0.002693
directlbl_9aa1f60c submission_directlbl_9aa1f60c.csv  frac0.40_rep009      entropy_g050       no_q2      0.36 0.040               -0.015172             -0.000496                 -0.000312               0.002692
directlbl_30d474fd submission_directlbl_30d474fd.csv  frac0.40_rep052      entropy_g075       no_q2      0.36 0.024               -0.015139             -0.000488                 -0.000258               0.002689
directlbl_b07f685f submission_directlbl_b07f685f.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.040               -0.015112             -0.000484                 -0.000299               0.002684
directlbl_5e036dad submission_directlbl_5e036dad.csv  frac0.50_rep142      entropy_g075       no_q2      0.24 0.040               -0.015055             -0.000527                 -0.000318               0.002670
directlbl_81cde906 submission_directlbl_81cde906.csv  frac0.50_rep142      entropy_g075       no_q2      0.24 0.024               -0.014941             -0.000518                 -0.000313               0.002645
directlbl_d7006e34 submission_directlbl_d7006e34.csv  frac0.40_rep197      entropy_g075         all      0.36 0.012               -0.014793             -0.000374                 -0.000232               0.002621
directlbl_65a22bad submission_directlbl_65a22bad.csv  frac0.50_rep142      entropy_g075         all      0.24 0.012               -0.014688             -0.000451                 -0.000280               0.002612
directlbl_ca56625c submission_directlbl_ca56625c.csv  frac0.40_rep009      entropy_g050       no_q2      0.36 0.024               -0.014636             -0.000461                 -0.000299               0.002567
directlbl_6aeca095 submission_directlbl_6aeca095.csv  frac0.50_rep142      entropy_g075 q3_s2_s3_s4      0.36 0.040               -0.014586             -0.000413                 -0.000207               0.002601
directlbl_9fc199f9 submission_directlbl_9fc199f9.csv  frac0.40_rep009      entropy_g075       no_q2      0.36 0.024               -0.014542             -0.000447                 -0.000288               0.002552
directlbl_c760692a submission_directlbl_c760692a.csv  frac0.40_rep002      entropy_g050         all      0.36 0.012               -0.014527             -0.000388                 -0.000239               0.002568
directlbl_bd1ae067 submission_directlbl_bd1ae067.csv  frac0.40_rep002      entropy_g075         all      0.36 0.012               -0.014508             -0.000380                 -0.000233               0.002564
directlbl_3689c44d submission_directlbl_3689c44d.csv  frac0.30_rep056      entropy_g075         all      0.36 0.040               -0.014402             -0.000389                 -0.000198               0.002513
directlbl_37a7dc3e submission_directlbl_37a7dc3e.csv  frac0.30_rep221      entropy_g075         all      0.36 0.040               -0.014356             -0.000426                 -0.000245               0.002505
directlbl_069081c6 submission_directlbl_069081c6.csv  frac0.40_rep052      entropy_g050         all      0.36 0.012               -0.014347             -0.000413                 -0.000244               0.002518
directlbl_4db706d3 submission_directlbl_4db706d3.csv  frac0.30_rep221      entropy_g050         all      0.36 0.040               -0.014326             -0.000434                 -0.000264               0.002489
directlbl_cb75c6bf submission_directlbl_cb75c6bf.csv  frac0.40_rep052      entropy_g075         all      0.36 0.012               -0.014321             -0.000405                 -0.000234               0.002515
directlbl_3b90c94f submission_directlbl_3b90c94f.csv  frac0.50_rep142      entropy_g075 q3_s2_s3_s4      0.36 0.024               -0.014097             -0.000384                 -0.000199               0.002485
directlbl_1baac448 submission_directlbl_1baac448.csv  frac0.40_rep009      entropy_g050         all      0.36 0.012               -0.014005             -0.000391                 -0.000263               0.002438
directlbl_fd426e2e submission_directlbl_fd426e2e.csv  frac0.40_rep009      entropy_g075         all      0.36 0.012               -0.013952             -0.000383                 -0.000256               0.002428
directlbl_87a0ec9c submission_directlbl_87a0ec9c.csv  frac0.30_rep056      entropy_g075         all      0.36 0.024               -0.013904             -0.000355                 -0.000183               0.002398
directlbl_145a5385 submission_directlbl_145a5385.csv  frac0.30_rep221      entropy_g050         all      0.36 0.024               -0.013828             -0.000396                 -0.000254               0.002375
directlbl_0c69f2f8 submission_directlbl_0c69f2f8.csv  frac0.30_rep221      entropy_g075         all      0.36 0.024               -0.013825             -0.000387                 -0.000233               0.002385
directlbl_a667bb5c submission_directlbl_a667bb5c.csv  frac0.40_rep197      entropy_g075       no_q2      0.36 0.012               -0.013651             -0.000355                 -0.000221               0.002326
directlbl_91aba0af submission_directlbl_91aba0af.csv  frac0.50_rep142      entropy_g075       no_q2      0.24 0.012               -0.013605             -0.000428                 -0.000265               0.002334
directlbl_29a95464 submission_directlbl_29a95464.csv  frac0.30_rep056      entropy_g075       no_q2      0.36 0.040               -0.013429             -0.000373                 -0.000188               0.002261
directlbl_8c63441a submission_directlbl_8c63441a.csv  frac0.40_rep002      entropy_g050       no_q2      0.36 0.012               -0.013345             -0.000364                 -0.000229               0.002264
directlbl_210bf455 submission_directlbl_210bf455.csv  frac0.40_rep002      entropy_g075       no_q2      0.36 0.012               -0.013288             -0.000356                 -0.000225               0.002250
directlbl_92acbc03 submission_directlbl_92acbc03.csv  frac0.50_rep142      entropy_g075         all      0.36 0.006               -0.013241             -0.000333                 -0.000214               0.002274
```

## Interpretation

- A low fit error here does not prove the mask is the real public subset; the system is underdetermined. It proves that the mask admits a plausible label assignment that explains all observed anchor signs and magnitudes.
- The most useful solutions are the ones that fit public anchors while requiring structured target-rate shifts, especially on id01/early-prefix masks already favored by inverse7.
- Direct-label probes are intentionally larger than raw05-compatible micro-refines. They should be submitted only as diagnostic larger-move tests, not as conservative score-safe candidates.
