# S2 label-preserving compression / blend no-submit follow-up

No submission files were created.

## chrono best
 group                 source          model       k   n      C  blend_w  logloss   delta    auc  runs
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.3000   0.5689 -0.0007 0.7174     3
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.4000   0.5689 -0.0007 0.7178     3
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.2000   0.5690 -0.0006 0.7189     3
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.5000   0.5690 -0.0006 0.7186     3
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.1000   0.5692 -0.0004 0.7190     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.3000   0.5695 -0.0000 0.7174     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.4000   0.5695 -0.0000 0.7168     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.2000   0.5695 -0.0000 0.7180     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.5000   0.5695 -0.0000 0.7146     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.1000   0.5695 -0.0000 0.7180     3
chrono      existing_base_cfg        basecfg     NaN NaN    NaN   0.0000   0.5696  0.0000 0.7175     3
chrono       existing_no_flat            raw 20.0000 NaN 0.0010   1.0000   0.5696  0.0000 0.7175     3
chrono combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.7000   0.5696  0.0000 0.7159     3
chrono       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.7000   0.5696  0.0000 0.7194     3
chrono combo_existing_dayflat            raw 32.0000 NaN 0.0010   1.0000   0.5697  0.0001 0.7168     3

## testpattern best
      group                 source model       k   n      C  blend_w  logloss   delta    auc  runs
testpattern       existing_no_flat   raw 48.0000 NaN 0.0010   1.0000   0.5898 -0.0377 0.7301     4
testpattern       existing_no_flat   raw 48.0000 NaN 0.0030   1.0000   0.5900 -0.0374 0.7258     4
testpattern       existing_no_flat   raw 64.0000 NaN 0.0010   1.0000   0.5906 -0.0369 0.7293     4
testpattern       existing_no_flat   raw 64.0000 NaN 0.0030   1.0000   0.5921 -0.0354 0.7257     4
testpattern       existing_no_flat   raw 48.0000 NaN 0.0100   1.0000   0.5974 -0.0300 0.7198     4
testpattern combo_existing_dayflat   raw 48.0000 NaN 0.0030   1.0000   0.6027 -0.0248 0.7209     4
testpattern combo_existing_dayflat   raw 20.0000 NaN 0.0100   1.0000   0.6034 -0.0241 0.7222     4
testpattern combo_existing_dayflat   raw 48.0000 NaN 0.0100   1.0000   0.6043 -0.0232 0.7118     4
testpattern       existing_no_flat   raw 64.0000 NaN 0.0100   1.0000   0.6045 -0.0229 0.7163     4
testpattern combo_existing_dayflat   raw 48.0000 NaN 0.0010   1.0000   0.6079 -0.0196 0.7230     4
testpattern       existing_no_flat   raw 20.0000 NaN 0.0100   1.0000   0.6093 -0.0181 0.7079     4
testpattern       existing_no_flat   raw 32.0000 NaN 0.0100   1.0000   0.6098 -0.0176 0.7091     4
testpattern combo_existing_dayflat   raw 64.0000 NaN 0.0030   1.0000   0.6099 -0.0176 0.7073     4
testpattern combo_existing_dayflat   raw 64.0000 NaN 0.0010   1.0000   0.6100 -0.0175 0.7135     4
testpattern combo_existing_dayflat   raw 32.0000 NaN 0.0100   1.0000   0.6102 -0.0173 0.7060     4

## random_gap best
     group                 source          model       k   n      C  blend_w  logloss   delta    auc  runs
random_gap combo_existing_dayflat            raw 20.0000 NaN 0.0100   1.0000   0.5604 -0.0237 0.7650     4
random_gap       existing_no_flat            raw 20.0000 NaN 0.0100   1.0000   0.5605 -0.0236 0.7693     4
random_gap combo_existing_dayflat            raw 32.0000 NaN 0.0100   1.0000   0.5619 -0.0222 0.7530     4
random_gap combo_existing_dayflat            raw 48.0000 NaN 0.0100   1.0000   0.5627 -0.0213 0.7529     4
random_gap       existing_no_flat            raw 32.0000 NaN 0.0100   1.0000   0.5630 -0.0211 0.7572     4
random_gap combo_existing_dayflat            raw 48.0000 NaN 0.0030   1.0000   0.5688 -0.0152 0.7562     4
random_gap combo_existing_dayflat            raw 32.0000 NaN 0.0030   1.0000   0.5714 -0.0127 0.7611     4
random_gap       existing_no_flat            raw 32.0000 NaN 0.0030   1.0000   0.5716 -0.0125 0.7590     4
random_gap combo_existing_dayflat            raw 20.0000 NaN 0.0030   1.0000   0.5721 -0.0120 0.7683     4
random_gap       existing_no_flat            raw 20.0000 NaN 0.0030   1.0000   0.5721 -0.0120 0.7725     4
random_gap       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.7000   0.5747 -0.0094 0.7616     4
random_gap       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.5000   0.5770 -0.0070 0.7647     4
random_gap       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.4000   0.5783 -0.0058 0.7663     4
random_gap       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.3000   0.5797 -0.0044 0.7687     4
random_gap combo_existing_dayflat            raw 48.0000 NaN 0.0010   1.0000   0.5808 -0.0033 0.7598     4

## tail best
group                 source          model       k   n      C  blend_w  logloss   delta    auc  runs
 tail       existing_no_flat            raw 32.0000 NaN 0.0010   1.0000   0.5793 -0.0222 0.7125     4
 tail combo_existing_dayflat            raw 32.0000 NaN 0.0010   1.0000   0.5813 -0.0202 0.7110     4
 tail       existing_no_flat            raw 32.0000 NaN 0.0030   1.0000   0.5838 -0.0177 0.7129     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.7000   0.5843 -0.0172 0.7119     4
 tail combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.7000   0.5857 -0.0158 0.7095     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.7000   0.5864 -0.0151 0.7116     4
 tail combo_existing_dayflat            raw 32.0000 NaN 0.0030   1.0000   0.5878 -0.0137 0.7089     4
 tail combo_existing_dayflat            raw 48.0000 NaN 0.0010   1.0000   0.5882 -0.0133 0.7105     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.5000   0.5884 -0.0131 0.7116     4
 tail combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.5000   0.5894 -0.0121 0.7087     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.5000   0.5895 -0.0120 0.7112     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.4000   0.5907 -0.0108 0.7112     4
 tail       existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.4000   0.5914 -0.0101 0.7108     4
 tail combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.4000   0.5915 -0.0100 0.7100     4
 tail combo_existing_dayflat            raw 64.0000 NaN 0.0010   1.0000   0.5929 -0.0085 0.7024     4

## Robust ranking
                source          model       k   n      C  blend_w  mean_delta  worst_delta  best_group_delta  groups  mean_auc
      existing_no_flat            raw 32.0000 NaN 0.0030   1.0000     -0.0096       0.0019           -0.0177       4    0.7256
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.7000     -0.0082       0.0000           -0.0151       4    0.7256
combo_existing_dayflat            raw 32.0000 NaN 0.0030   1.0000     -0.0079       0.0047           -0.0137       4    0.7232
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.5000     -0.0065      -0.0006           -0.0120       4    0.7262
combo_existing_dayflat            raw 48.0000 NaN 0.0030   1.0000     -0.0058       0.0228           -0.0248       4    0.7261
      existing_no_flat            raw 32.0000 NaN 0.0100   1.0000     -0.0058       0.0183           -0.0211       4    0.7257
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.4000     -0.0055      -0.0007           -0.0101       4    0.7265
      existing_no_flat            raw 20.0000 NaN 0.0100   1.0000     -0.0053       0.0140           -0.0236       4    0.7236
combo_existing_dayflat            raw 32.0000 NaN 0.0010   1.0000     -0.0052       0.0001           -0.0202       4    0.7234
      existing_no_flat            raw 20.0000 NaN 0.0030   1.0000     -0.0050       0.0022           -0.0120       4    0.7239
combo_existing_dayflat            raw 48.0000 NaN 0.0010   1.0000     -0.0045       0.0180           -0.0196       4    0.7286
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.3000     -0.0043      -0.0007           -0.0080       4    0.7255
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.7000     -0.0041       0.0000           -0.0158       4    0.7241
combo_existing_dayflat            raw 32.0000 NaN 0.0100   1.0000     -0.0041       0.0203           -0.0222       4    0.7208
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.7000     -0.0039       0.0026           -0.0172       4    0.7260
      existing_no_flat            raw 32.0000 NaN 0.0010   1.0000     -0.0036       0.0093           -0.0222       4    0.7244
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.5000     -0.0032      -0.0000           -0.0121       4    0.7253
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.5000     -0.0031       0.0014           -0.0131       4    0.7269
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.2000     -0.0030      -0.0006           -0.0056       4    0.7266
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.4000     -0.0026      -0.0000           -0.0100       4    0.7265
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.4000     -0.0026       0.0009           -0.0108       4    0.7269
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.3000     -0.0021       0.0006           -0.0083       4    0.7271
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.3000     -0.0021      -0.0000           -0.0077       4    0.7270
      existing_no_flat raw_blend_base 32.0000 NaN 0.0030   0.1000     -0.0016      -0.0004           -0.0029       4    0.7259
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.2000     -0.0014       0.0004           -0.0057       4    0.7263
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.2000     -0.0014      -0.0000           -0.0053       4    0.7261
      existing_no_flat raw_blend_base 32.0000 NaN 0.0010   0.1000     -0.0007       0.0002           -0.0030       4    0.7254
combo_existing_dayflat raw_blend_base 32.0000 NaN 0.0010   0.1000     -0.0007      -0.0000           -0.0028       4    0.7252
combo_existing_dayflat            raw 20.0000 NaN 0.0100   1.0000     -0.0001       0.0299           -0.0241       4    0.7161
     existing_base_cfg        basecfg     NaN NaN    NaN   0.0000      0.0000       0.0000            0.0000       4    0.7243
      existing_no_flat            raw 20.0000 NaN 0.0010   1.0000      0.0000       0.0000            0.0000       4    0.7243
      existing_no_flat            raw 48.0000 NaN 0.0030   1.0000      0.0004       0.0305           -0.0374       4    0.7265
      existing_no_flat            raw 48.0000 NaN 0.0010   1.0000      0.0009       0.0261           -0.0377       4    0.7277
combo_existing_dayflat            raw 48.0000 NaN 0.0100   1.0000      0.0033       0.0426           -0.0232       4    0.7194
      existing_no_flat            raw 64.0000 NaN 0.0010   1.0000      0.0037       0.0319           -0.0369       4    0.7239

## Best compression-only
                source      model       k       n      C  blend_w  mean_delta  worst_delta  best_group_delta  groups  mean_auc
      existing_no_flat select_pca 96.0000  8.0000 0.0030   1.0000      0.0676       0.0933            0.0424       4    0.7077
      existing_no_flat select_pca 96.0000 16.0000 0.0030   1.0000      0.0688       0.0916            0.0410       4    0.6909
      existing_no_flat select_pca 96.0000 32.0000 0.0030   1.0000      0.0693       0.0965            0.0393       4    0.6906
combo_existing_dayflat select_pca 48.0000  8.0000 0.0030   1.0000      0.0693       0.1039            0.0350       4    0.6730
combo_existing_dayflat select_pca 64.0000  8.0000 0.0030   1.0000      0.0695       0.1027            0.0398       4    0.6886
combo_existing_dayflat select_pca 96.0000  8.0000 0.0030   1.0000      0.0696       0.0967            0.0452       4    0.6814
      existing_no_flat select_pca 64.0000  8.0000 0.0030   1.0000      0.0705       0.1000            0.0423       4    0.6737
      existing_no_flat select_pca 64.0000 16.0000 0.0030   1.0000      0.0706       0.0967            0.0398       4    0.6620
combo_existing_dayflat select_pca 96.0000 16.0000 0.0030   1.0000      0.0710       0.1002            0.0426       4    0.6629
combo_existing_dayflat  pls_logit 96.0000  4.0000 0.0030   1.0000      0.0710       0.1024            0.0455       4    0.6559
combo_existing_dayflat  pls_logit 96.0000  8.0000 0.0030   1.0000      0.0716       0.1019            0.0464       4    0.6500
combo_existing_dayflat  pls_logit 64.0000  4.0000 0.0030   1.0000      0.0720       0.1053            0.0416       4    0.6642
combo_existing_dayflat select_pca 48.0000 16.0000 0.0030   1.0000      0.0721       0.1147            0.0356       4    0.6524
combo_existing_dayflat  pls_logit 96.0000 12.0000 0.0030   1.0000      0.0725       0.1058            0.0453       4    0.6624
combo_existing_dayflat  pls_logit 64.0000  8.0000 0.0030   1.0000      0.0726       0.1090            0.0419       4    0.6650
combo_existing_dayflat  pls_logit 48.0000  4.0000 0.0030   1.0000      0.0726       0.1095            0.0401       4    0.6631
combo_existing_dayflat select_pca 64.0000 16.0000 0.0030   1.0000      0.0727       0.1016            0.0391       4    0.6720
      existing_no_flat  pls_logit 64.0000  4.0000 0.0030   1.0000      0.0730       0.1037            0.0426       4    0.6698
      existing_no_flat  pls_logit 96.0000  4.0000 0.0030   1.0000      0.0733       0.1060            0.0413       4    0.6814
      existing_no_flat  pls_logit 96.0000  8.0000 0.0030   1.0000      0.0734       0.1058            0.0411       4    0.6758

## Best base blends
                source                 model       k       n      C  blend_w  mean_delta  worst_delta  best_group_delta  groups  mean_auc
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.7000     -0.0082       0.0000           -0.0151       4    0.7256
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.5000     -0.0065      -0.0006           -0.0120       4    0.7262
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.4000     -0.0055      -0.0007           -0.0101       4    0.7265
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.3000     -0.0043      -0.0007           -0.0080       4    0.7255
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.7000     -0.0041       0.0000           -0.0158       4    0.7241
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.7000     -0.0039       0.0026           -0.0172       4    0.7260
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.5000     -0.0032      -0.0000           -0.0121       4    0.7253
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.5000     -0.0031       0.0014           -0.0131       4    0.7269
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.2000     -0.0030      -0.0006           -0.0056       4    0.7266
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.4000     -0.0026      -0.0000           -0.0100       4    0.7265
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.4000     -0.0026       0.0009           -0.0108       4    0.7269
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.3000     -0.0021       0.0006           -0.0083       4    0.7271
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.3000     -0.0021      -0.0000           -0.0077       4    0.7270
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0030   0.1000     -0.0016      -0.0004           -0.0029       4    0.7259
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.2000     -0.0014       0.0004           -0.0057       4    0.7263
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.2000     -0.0014      -0.0000           -0.0053       4    0.7261
      existing_no_flat        raw_blend_base 32.0000     NaN 0.0010   0.1000     -0.0007       0.0002           -0.0030       4    0.7254
combo_existing_dayflat        raw_blend_base 32.0000     NaN 0.0010   0.1000     -0.0007      -0.0000           -0.0028       4    0.7252
      existing_no_flat select_pca_blend_base 64.0000 16.0000 0.0030   0.1000      0.0040       0.0077            0.0011       4    0.7247
      existing_no_flat  pls_logit_blend_base 64.0000  8.0000 0.0030   0.1000      0.0041       0.0083            0.0009       4    0.7267
