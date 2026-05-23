# Advanced DS Insight Analysis

## 0. 질문 재정의

이번 분석은 제출 파일을 만들지 않고, `라벨 생성 구조가 무엇인지`, `그 구조가 센서/행동 feature에서 관측 가능한지`, `target별로 어떤 feature family가 실제 신호를 갖는지`를 보는 분석이다.

## 1. Latent label-state discovery

Best Bernoulli mixture: K=3, BIC=4023.21, loglik=-1941.35

### State emission probabilities

 state    Q1    Q2    Q3    S1    S2    S3    S4  mixing_weight  severity_mean
     0 0.436 0.558 0.596 0.428 0.030 0.406 0.228          0.342          0.383
     1 0.099 0.441 0.455 0.575 0.970 0.894 0.764          0.266          0.600
     2 0.817 0.647 0.700 0.970 0.970 0.725 0.711          0.392          0.791

### Label entropy explained by latent state

target  H_y_bits  H_y_given_state_bits  MI_state_y_bits  explained_entropy_share
    Q1     1.000                 0.554            0.446                    0.446
    Q2     0.989                 0.970            0.019                    0.019
    Q3     0.971                 0.949            0.022                    0.022
    S1     0.902                 0.671            0.231                    0.256
    S2     0.933                 0.020            0.914                    0.979
    S3     0.923                 0.776            0.147                    0.159
    S4     0.990                 0.809            0.181                    0.182

### State transition matrix

        to_0  to_1  to_2
from_0 0.450 0.225 0.325
from_1 0.258 0.453 0.289
from_2 0.304 0.217 0.478

### Subject state occupancy

subject_id  state_0_share  state_1_share  state_2_share    Q1    Q2    Q3    S1    S2    S3    S4
      id01          0.390          0.268          0.341 0.439 0.561 0.585 0.634 0.585 0.854 0.488
      id02          0.083          0.354          0.562 0.542 0.667 0.729 0.875 0.917 0.896 0.750
      id03          0.485          0.121          0.394 0.848 0.818 0.727 0.818 0.515 0.485 0.152
      id04          0.298          0.193          0.509 0.561 0.491 0.772 0.754 0.702 0.544 0.509
      id05          0.750          0.045          0.205 0.614 0.432 0.682 0.477 0.250 0.136 0.409
      id06          0.083          0.771          0.146 0.146 0.396 0.500 0.938 0.917 0.958 0.854
      id07          0.286          0.184          0.531 0.510 0.510 0.510 0.796 0.714 0.796 0.469
      id08          0.393          0.339          0.268 0.411 0.786 0.446 0.446 0.607 0.661 0.607
      id09          0.220          0.366          0.415 0.512 0.439 0.439 0.561 0.780 0.707 0.585
      id10          0.636          0.152          0.212 0.485 0.545 0.636 0.485 0.364 0.485 0.667

## 2. Are latent states observable from features?

          scheme  masks   acc  bal_acc  state_logloss  majority_acc
interleaved_rank      4 0.337    0.373          1.070         0.362
     testpattern      5 0.369    0.389          1.056         0.373

### Top separator feature families by latent state

 state           family  n_top  mean_abs_smd
     0     screen_phone     77         0.402
     0 location_context     53         0.353
     0              ssl     16         0.306
     0      heart_light      5         0.370
     0     routine_axes      5         0.274
     0   activity_steps      4         0.359
     1 location_context     81         0.403
     1     screen_phone     65         0.464
     1   activity_steps      8         0.340
     1    sleep_episode      2         0.286
     1     routine_axes      2         0.261
     1      heart_light      1         0.298
     1              ssl      1         0.256
     2 location_context     83         0.269
     2     screen_phone     60         0.311
     2   activity_steps      7         0.274
     2      heart_light      4         0.337
     2     routine_axes      4         0.227
     2    sleep_episode      1         0.233
     2              ssl      1         0.211

## 3. Feature-family signal by target

Top families below are ranked by mean logloss improvement over global prior under masked validation. Positive means the family carries signal; negative means mostly noise/overfit in this setup.

          scheme target  rank                      family  mean_improvement_vs_prior  mean_logloss
interleaved_rank     Q1     1              activity_steps                     0.0200        0.6779
interleaved_rank     Q1     2 same_subject_temporal_label                     0.0149        0.6831
interleaved_rank     Q1     3                screen_phone                     0.0074        0.6906
interleaved_rank     Q1     4                 heart_light                     0.0067        0.6912
interleaved_rank     Q1     5                         ssl                    -0.0210        0.7190
interleaved_rank     Q2     1 same_subject_temporal_label                     0.0008        0.6856
interleaved_rank     Q2     2                 heart_light                    -0.0081        0.6945
interleaved_rank     Q2     3                         ssl                    -0.0344        0.7209
interleaved_rank     Q2     4                routine_axes                    -0.0363        0.7227
interleaved_rank     Q2     5                screen_phone                    -0.0580        0.7444
interleaved_rank     Q3     1 same_subject_temporal_label                     0.0154        0.6536
interleaved_rank     Q3     2              activity_steps                     0.0078        0.6612
interleaved_rank     Q3     3                         ssl                    -0.0183        0.6874
interleaved_rank     Q3     4                routine_axes                    -0.0192        0.6883
interleaved_rank     Q3     5                 heart_light                    -0.0281        0.6972
interleaved_rank     S1     1 same_subject_temporal_label                     0.0176        0.6091
interleaved_rank     S1     2              activity_steps                    -0.0163        0.6429
interleaved_rank     S1     3                routine_axes                    -0.0210        0.6476
interleaved_rank     S1     4                         ssl                    -0.0217        0.6483
interleaved_rank     S1     5                screen_phone                    -0.0237        0.6503
interleaved_rank     S2     1 same_subject_temporal_label                     0.0523        0.5893
interleaved_rank     S2     2              activity_steps                     0.0173        0.6244
interleaved_rank     S2     3                screen_phone                    -0.0045        0.6462
interleaved_rank     S2     4                         ssl                    -0.0082        0.6498
interleaved_rank     S2     5            location_context                    -0.0306        0.6723
interleaved_rank     S3     1 same_subject_temporal_label                     0.0681        0.5708
interleaved_rank     S3     2            location_context                     0.0308        0.6081
interleaved_rank     S3     3              activity_steps                     0.0107        0.6281
interleaved_rank     S3     4                screen_phone                    -0.0044        0.6432
interleaved_rank     S3     5                         ssl                    -0.0144        0.6533
interleaved_rank     S4     1 same_subject_temporal_label                     0.0346        0.6536
interleaved_rank     S4     2              activity_steps                     0.0302        0.6580
interleaved_rank     S4     3                screen_phone                     0.0276        0.6606
interleaved_rank     S4     4                 heart_light                    -0.0072        0.6954
interleaved_rank     S4     5                         ssl                    -0.0153        0.7034
     testpattern     Q1     1 same_subject_temporal_label                     0.0280        0.6667
     testpattern     Q1     2                screen_phone                     0.0235        0.6712
     testpattern     Q1     3              activity_steps                     0.0109        0.6838
     testpattern     Q1     4                 heart_light                     0.0033        0.6914
     testpattern     Q1     5            location_context                    -0.0099        0.7046
     testpattern     Q2     1 same_subject_temporal_label                     0.0239        0.6609
     testpattern     Q2     2                 heart_light                    -0.0088        0.6936
     testpattern     Q2     3                         ssl                    -0.0208        0.7056
     testpattern     Q2     4                screen_phone                    -0.0221        0.7069
     testpattern     Q2     5              activity_steps                    -0.0234        0.7082
     testpattern     Q3     1 same_subject_temporal_label                     0.0154        0.6538
     testpattern     Q3     2                         ssl                    -0.0004        0.6696
     testpattern     Q3     3                 heart_light                    -0.0267        0.6959
     testpattern     Q3     4              activity_steps                    -0.0298        0.6990
     testpattern     Q3     5                screen_phone                    -0.0393        0.7085
     testpattern     S1     1 same_subject_temporal_label                     0.0264        0.5967
     testpattern     S1     2              activity_steps                    -0.0070        0.6301
     testpattern     S1     3                         ssl                    -0.0139        0.6369
     testpattern     S1     4                screen_phone                    -0.0242        0.6473
     testpattern     S1     5                routine_axes                    -0.0356        0.6586
     testpattern     S2     1 same_subject_temporal_label                     0.0502        0.6083
     testpattern     S2     2                screen_phone                     0.0108        0.6477
     testpattern     S2     3              activity_steps                     0.0044        0.6540
     testpattern     S2     4                         ssl                     0.0011        0.6574
     testpattern     S2     5            location_context                    -0.0225        0.6809
     testpattern     S3     1 same_subject_temporal_label                     0.0661        0.5829
     testpattern     S3     2              activity_steps                     0.0215        0.6275
     testpattern     S3     3            location_context                     0.0144        0.6346
     testpattern     S3     4                screen_phone                     0.0117        0.6373
     testpattern     S3     5                         ssl                    -0.0113        0.6604
     testpattern     S4     1 same_subject_temporal_label                     0.0337        0.6595
     testpattern     S4     2              activity_steps                     0.0337        0.6595
     testpattern     S4     3                screen_phone                     0.0281        0.6651
     testpattern     S4     4                 heart_light                    -0.0007        0.6939
     testpattern     S4     5                         ssl                    -0.0046        0.6978

## 4. Robust target/family map

          scheme target                      family  mean_improvement_vs_prior  std_improvement  robust_score
     testpattern     Q1 same_subject_temporal_label                     0.0280           0.0057        0.0224
interleaved_rank     Q1              activity_steps                     0.0200           0.0039        0.0161
     testpattern     Q1                screen_phone                     0.0235           0.0132        0.0103
interleaved_rank     Q1 same_subject_temporal_label                     0.0149           0.0072        0.0077
interleaved_rank     Q1                 heart_light                     0.0067           0.0012        0.0056
     testpattern     Q1                 heart_light                     0.0033           0.0018        0.0015
     testpattern     Q2 same_subject_temporal_label                     0.0239           0.0138        0.0101
interleaved_rank     Q2 same_subject_temporal_label                     0.0008           0.0075       -0.0068
     testpattern     Q2                 heart_light                    -0.0088           0.0043       -0.0131
interleaved_rank     Q2                 heart_light                    -0.0081           0.0059       -0.0140
     testpattern     Q2                screen_phone                    -0.0221           0.0074       -0.0295
     testpattern     Q2              activity_steps                    -0.0234           0.0100       -0.0334
interleaved_rank     Q3 same_subject_temporal_label                     0.0154           0.0104        0.0050
     testpattern     Q3 same_subject_temporal_label                     0.0154           0.0110        0.0044
     testpattern     Q3                         ssl                    -0.0004           0.0021       -0.0025
interleaved_rank     Q3              activity_steps                     0.0078           0.0107       -0.0029
interleaved_rank     Q3                         ssl                    -0.0183           0.0133       -0.0316
interleaved_rank     Q3                 heart_light                    -0.0281           0.0038       -0.0320
     testpattern     S1 same_subject_temporal_label                     0.0264           0.0067        0.0197
interleaved_rank     S1 same_subject_temporal_label                     0.0176           0.0118        0.0058
     testpattern     S1              activity_steps                    -0.0070           0.0149       -0.0220
     testpattern     S1                         ssl                    -0.0139           0.0116       -0.0255
     testpattern     S1                screen_phone                    -0.0242           0.0057       -0.0300
interleaved_rank     S1              activity_steps                    -0.0163           0.0150       -0.0313
interleaved_rank     S2 same_subject_temporal_label                     0.0523           0.0147        0.0376
     testpattern     S2 same_subject_temporal_label                     0.0502           0.0163        0.0339
interleaved_rank     S2              activity_steps                     0.0173           0.0059        0.0114
interleaved_rank     S2                screen_phone                    -0.0045           0.0064       -0.0109
     testpattern     S2                screen_phone                     0.0108           0.0241       -0.0133
     testpattern     S2                         ssl                     0.0011           0.0220       -0.0210
interleaved_rank     S3 same_subject_temporal_label                     0.0681           0.0066        0.0615
     testpattern     S3 same_subject_temporal_label                     0.0661           0.0124        0.0537
interleaved_rank     S3            location_context                     0.0308           0.0218        0.0089
     testpattern     S3              activity_steps                     0.0215           0.0170        0.0045
     testpattern     S3                screen_phone                     0.0117           0.0154       -0.0037
interleaved_rank     S3                screen_phone                    -0.0044           0.0098       -0.0142
interleaved_rank     S4 same_subject_temporal_label                     0.0346           0.0052        0.0294
     testpattern     S4 same_subject_temporal_label                     0.0337           0.0089        0.0248
interleaved_rank     S4                screen_phone                     0.0276           0.0029        0.0247
interleaved_rank     S4              activity_steps                     0.0302           0.0063        0.0239
     testpattern     S4              activity_steps                     0.0337           0.0133        0.0204
     testpattern     S4                screen_phone                     0.0281           0.0094        0.0187

## 5. Interpretation

- 라벨별 모델 적용은 맞다. 다만 더 정확히는 `라벨별 모델`이라기보다 `라벨별 생성 메커니즘/latent state 연결 방식`을 다르게 둬야 한다.
- Bernoulli mixture state가 여러 target의 entropy를 동시에 설명하면, target을 독립 binary로만 보면 정보가 버려진다. 특히 S-family/Q2-Q3류는 joint state 관점이 맞다.
- state가 feature로 예측 가능하면 graph/label smoothing만의 문제가 아니라, 센서 feature 안에 실제 behavioral regime 신호가 있다는 뜻이다. 반대로 state 예측력이 낮으면 feature보다 subject-time label interpolation 문제가 크다.
- feature-family별 신호가 target마다 갈리면, 다음 단계는 제출 후보가 아니라 `각 target의 측정 의미`를 feature family 관점에서 재해석하는 것이다.

## 6. Output files

- `experiments/advanced_ds_bernoulli_mixture_bic.csv`
- `experiments/advanced_ds_latent_state_emissions.csv`
- `experiments/advanced_ds_row_latent_states.csv`
- `experiments/advanced_ds_latent_state_transition_matrix.csv`
- `experiments/advanced_ds_subject_state_occupancy.csv`
- `experiments/advanced_ds_state_label_information.csv`
- `experiments/advanced_ds_latent_state_predictability.csv`
- `experiments/advanced_ds_state_feature_separators.csv`
- `experiments/advanced_ds_state_separator_family_summary.csv`
- `experiments/advanced_ds_feature_family_signal_raw.csv`
- `experiments/advanced_ds_feature_family_signal_summary.csv`
- `experiments/advanced_ds_top_feature_families_by_target.csv`
