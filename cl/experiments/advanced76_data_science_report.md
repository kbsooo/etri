# Advanced measurement/context/temporal data-science diagnostics

This extends observation-process diagnostics into measurement theory and subject-debiased context analysis. No submissions generated.

## Produced files

- `advanced76_measurement_lowrank_fit.csv`
- `advanced76_measurement_label_loadings.csv`
- `advanced76_measurement_row_scores_anomalies.csv`
- `advanced76_subject_calibration_measurement.csv`
- `advanced76_residual_anomaly_coverage_association.csv`
- `advanced76_subject_debiased_token_association.csv`
- `advanced76_temporal_influence_network.csv`
- `advanced76_context_token_event_study.csv`

## 1. Bernoulli measurement model fit

Lower mean logloss means the label matrix is better explained by latent row factors; BIC penalizes tiny-data overparameterization.

```
 k        loss  mean_logloss          bic
 0 2092.015183      0.664132  4240.416469
 1 1185.944506      0.376490  9734.303179
 2 1312.643111      0.416712 13668.907473
 3 1553.193790      0.493077 17831.215914
```

Label loadings from the strongest nonzero latent-factor model:

```
label  label_bias  empirical_rate  loading_1
   Q1    0.043653        0.495556   0.833979
   Q2    0.404542        0.562222   7.389562
   Q3    0.429120        0.600000   3.144808
   S1    1.116374        0.682222   0.120831
   S2    0.908257        0.651111  -3.165075
   S3    1.473632        0.662222  -5.828343
   S4    0.203786        0.560000  -2.071507
```

Subject calibration summary:

```
subject_id  n  residual_mean  severity_mean  severity_std  prev_Q1  prev_Q2  prev_Q3  prev_S1  prev_S2  prev_S3  prev_S4
      id05 44       3.619295      -0.869122      1.207293 0.613636 0.431818 0.681818 0.477273 0.250000 0.136364 0.409091
      id08 56       3.150580      -0.081071      1.384070 0.410714 0.785714 0.446429 0.446429 0.607143 0.660714 0.607143
      id10 33       2.936965      -0.224823      1.468877 0.484848 0.545455 0.636364 0.484848 0.363636 0.484848 0.666667
      id09 41       2.737737      -0.019139      1.206410 0.512195 0.439024 0.439024 0.560976 0.780488 0.707317 0.585366
      id01 41       2.718570       0.108846      1.378725 0.439024 0.560976 0.585366 0.634146 0.585366 0.853659 0.487805
      id04 57       2.646778       0.216096      1.454626 0.561404 0.491228 0.771930 0.754386 0.701754 0.543860 0.508772
      id07 49       2.636689       0.173987      1.601554 0.510204 0.510204 0.510204 0.795918 0.714286 0.795918 0.469388
      id03 33       2.421441       0.242289      1.058878 0.848485 0.818182 0.727273 0.818182 0.515152 0.484848 0.151515
      id06 48       1.861609       0.420547      0.986955 0.145833 0.395833 0.500000 0.937500 0.916667 0.958333 0.854167
      id02 48       1.673035       1.360984      1.682610 0.541667 0.666667 0.729167 0.875000 0.916667 0.895833 0.750000
```

## 2. High-residual/noisy label rows vs sensor coverage

Rows badly fit by the label measurement model are candidate label-noise, transition, or multi-state days. Coverage associations:

```
                      feature  auc_absdir_for_high_residual  mean_high  mean_other  diff_high_minus_other
w_light_longest_missing_hours                      0.621536   4.488889    2.469136               2.019753
               hr_night_hours                      0.609163   0.711111    1.392593              -0.681481
  usage_longest_missing_hours                      0.588615   5.044444    4.276543               0.767901
                pedo_record_n                      0.582606 942.977778 1029.219753             -86.241975
                  pedo_item_n                      0.582606 942.977778 1029.219753             -86.241975
            usage_night_hours                      0.580357   3.444444    3.923457              -0.479012
         w_light_active_hours                      0.579890  18.377778   19.269136              -0.891358
            pedo_active_hours                      0.577750  17.200000   18.585185              -1.385185
               pedo_day_hours                      0.572565  12.288889   12.982716              -0.693827
           usage_active_hours                      0.572428  16.644444   17.375309              -0.730864
              ble_night_hours                      0.571523   1.933333    2.219753              -0.286420
   pedo_longest_missing_hours                      0.564911   3.355556    2.646914               0.708642
```

## 3. Subject-debiased identity-token associations

These survive within-subject label permutation tests, so they are less likely to be pure subject fingerprint. Still small-N and context-specific.

```
target                        token  within_subject_cov   perm_p  presence_days  raw_rate_present  raw_rate_absent
    Q1        usage_app_name:삼성 인터넷            0.018625 0.012346            195          0.548718         0.454902
    S4 wifi_bssid:98:25:4a:80:6f:62            0.012698 0.012346             93          0.741935         0.512605
    S4 wifi_bssid:9e:25:4a:80:6f:61            0.014523 0.012346             90          0.755556         0.511111
    S4        ble_device_class:7936            0.016094 0.012346            414          0.572464         0.416667
    S4 wifi_bssid:80:ca:4b:59:3b:52            0.016219 0.012346             67          0.805970         0.516971
    S4           ble_device_class:0            0.016742 0.012346            416          0.574519         0.382353
    S4 wifi_bssid:50:46:ae:5f:2e:14            0.014769 0.012346             61          0.803279         0.521851
    Q2            usage_app_name:시계           -0.019162 0.012346            331          0.519637         0.680672
    Q2 wifi_bssid:b4:a9:4f:45:df:9e           -0.010037 0.012346             54          0.388889         0.585859
    Q2 wifi_bssid:8a:ca:4b:0d:3b:67           -0.009027 0.012346             55          0.400000         0.584810
    Q2     usage_app_name:Instagram            0.012979 0.012346            206          0.577670         0.549180
    Q2       usage_app_name:YouTube            0.017318 0.012346            256          0.578125         0.541237
    S2      usage_app_name:One UI 홈            0.005370 0.012346            439          0.651481         0.636364
    Q2 wifi_bssid:9c:a3:a9:d2:db:72           -0.009263 0.024691             55          0.400000         0.584810
    S4      usage_app_name:LG ThinQ            0.011385 0.024691             61          0.360656         0.591260
    S4 wifi_bssid:9e:25:4a:80:73:13            0.015000 0.024691             85          0.764706         0.512329
    S4 wifi_bssid:ee:5c:68:90:0c:eb            0.015070 0.024691             51          0.803922         0.528822
    S4 wifi_bssid:60:29:d5:4a:47:d3            0.017882 0.024691             63          0.825397         0.516796
    S3        usage_app_name:권한 관리자           -0.018173 0.024691            281          0.608541         0.751479
    S3            usage_app_name:날씨            0.013271 0.024691            103          0.796117         0.622478
```

## 4. Temporal influence network controlling subject

`ALL_LAGS` rows show predictive value of all previous-day labels beyond subject-only and own-lag baselines. Edge rows are regularized coefficients.

```
target         edge      coef      auc  ll_improve_vs_base  ll_improve_vs_subject_only  ll_improve_vs_own_lag   n
    Q1     ALL_LAGS       NaN 0.653577            0.038427                    0.002802              -0.005366 440
    Q1 Q1_lag_to_Q1  0.367809      NaN                 NaN                         NaN                    NaN 440
    Q1 Q2_lag_to_Q1 -0.152369      NaN                 NaN                         NaN                    NaN 440
    Q1 Q3_lag_to_Q1 -0.031573      NaN                 NaN                         NaN                    NaN 440
    Q1 S1_lag_to_Q1 -0.008106      NaN                 NaN                         NaN                    NaN 440
    Q1 S2_lag_to_Q1  0.072151      NaN                 NaN                         NaN                    NaN 440
    Q1 S3_lag_to_Q1 -0.150129      NaN                 NaN                         NaN                    NaN 440
    Q1 S4_lag_to_Q1 -0.105311      NaN                 NaN                         NaN                    NaN 440
    Q2     ALL_LAGS       NaN 0.682983            0.041919                    0.027902              -0.000232 440
    Q2 Q1_lag_to_Q2  0.313665      NaN                 NaN                         NaN                    NaN 440
    Q2 Q2_lag_to_Q2  0.466759      NaN                 NaN                         NaN                    NaN 440
    Q2 Q3_lag_to_Q2  0.092969      NaN                 NaN                         NaN                    NaN 440
    Q2 S1_lag_to_Q2  0.200995      NaN                 NaN                         NaN                    NaN 440
    Q2 S2_lag_to_Q2 -0.060107      NaN                 NaN                         NaN                    NaN 440
    Q2 S3_lag_to_Q2  0.029854      NaN                 NaN                         NaN                    NaN 440
    Q2 S4_lag_to_Q2  0.021259      NaN                 NaN                         NaN                    NaN 440
    Q3     ALL_LAGS       NaN 0.691094            0.035172                    0.040901               0.013003 440
    Q3 Q1_lag_to_Q3  0.453783      NaN                 NaN                         NaN                    NaN 440
    Q3 Q2_lag_to_Q3  0.003047      NaN                 NaN                         NaN                    NaN 440
    Q3 Q3_lag_to_Q3  0.484887      NaN                 NaN                         NaN                    NaN 440
    Q3 S1_lag_to_Q3  0.084013      NaN                 NaN                         NaN                    NaN 440
    Q3 S2_lag_to_Q3 -0.089207      NaN                 NaN                         NaN                    NaN 440
    Q3 S3_lag_to_Q3 -0.037306      NaN                 NaN                         NaN                    NaN 440
    Q3 S4_lag_to_Q3 -0.172372      NaN                 NaN                         NaN                    NaN 440
    S1     ALL_LAGS       NaN 0.657861           -0.027462                   -0.013012              -0.013299 440
    S1 Q1_lag_to_S1  0.137221      NaN                 NaN                         NaN                    NaN 440
    S1 Q2_lag_to_S1 -0.171049      NaN                 NaN                         NaN                    NaN 440
    S1 Q3_lag_to_S1  0.036422      NaN                 NaN                         NaN                    NaN 440
    S1 S1_lag_to_S1  0.161525      NaN                 NaN                         NaN                    NaN 440
    S1 S2_lag_to_S1  0.042162      NaN                 NaN                         NaN                    NaN 440
    S1 S3_lag_to_S1 -0.038284      NaN                 NaN                         NaN                    NaN 440
    S1 S4_lag_to_S1 -0.002816      NaN                 NaN                         NaN                    NaN 440
    S2     ALL_LAGS       NaN 0.696166            0.016241                   -0.011780              -0.008337 440
    S2 Q1_lag_to_S2 -0.041606      NaN                 NaN                         NaN                    NaN 440
    S2 Q2_lag_to_S2 -0.070842      NaN                 NaN                         NaN                    NaN 440
    S2 Q3_lag_to_S2  0.086653      NaN                 NaN                         NaN                    NaN 440
    S2 S1_lag_to_S2  0.244006      NaN                 NaN                         NaN                    NaN 440
    S2 S2_lag_to_S2 -0.013163      NaN                 NaN                         NaN                    NaN 440
    S2 S3_lag_to_S2  0.044127      NaN                 NaN                         NaN                    NaN 440
    S2 S4_lag_to_S2  0.076210      NaN                 NaN                         NaN                    NaN 440
```

## 5. Context event study

For top subject-debiased tokens, this checks whether labels change on token appearance/continuation/disappearance days.

```
                       token              phase target  n     rate  global_rate  lift_vs_global
     usage_app_name:LG ThinQ disappearance_edge     Q3  4 1.000000     0.600000        0.400000
wifi_bssid:50:46:ae:5f:2e:14         appearance     S4 30 0.900000     0.560000        0.340000
wifi_bssid:80:ca:4b:59:3b:52         appearance     S4 35 0.885714     0.560000        0.325714
wifi_bssid:9c:a3:a9:d2:db:72 disappearance_edge     S4  8 0.875000     0.560000        0.315000
wifi_bssid:ee:5c:68:90:0c:eb         continuing     S4 16 0.875000     0.560000        0.315000
wifi_bssid:60:29:d5:4a:47:d3 disappearance_edge     S4 16 0.875000     0.560000        0.315000
wifi_bssid:9e:25:4a:80:6f:61         appearance     S4 33 0.848485     0.560000        0.288485
     usage_app_name:LG ThinQ         continuing     Q1 46 0.782609     0.495556        0.287053
wifi_bssid:ee:5c:68:90:0c:eb         appearance     S4 24 0.833333     0.560000        0.273333
wifi_bssid:98:25:4a:80:6f:62         appearance     S4 34 0.823529     0.560000        0.263529
wifi_bssid:9e:25:4a:80:73:13         appearance     S4 33 0.818182     0.560000        0.258182
wifi_bssid:60:29:d5:4a:47:d3         appearance     S4 33 0.818182     0.560000        0.258182
wifi_bssid:80:ca:4b:59:3b:52         continuing     S2 11 0.909091     0.651111        0.257980
wifi_bssid:9c:a3:a9:d2:db:72 disappearance_edge     Q1  8 0.750000     0.495556        0.254444
     usage_app_name:LG ThinQ disappearance_edge     Q1  4 0.750000     0.495556        0.254444
wifi_bssid:ee:5c:68:90:0c:eb         continuing     Q2 16 0.812500     0.562222        0.250278
wifi_bssid:60:29:d5:4a:47:d3         continuing     S4 14 0.785714     0.560000        0.225714
wifi_bssid:60:29:d5:4a:47:d3         continuing     Q2 14 0.785714     0.562222        0.223492
     usage_app_name:LG ThinQ         continuing     Q2 46 0.782609     0.562222        0.220386
wifi_bssid:12:96:cd:84:93:6b disappearance_edge     Q1  7 0.714286     0.495556        0.218730
wifi_bssid:b4:a9:4f:45:df:9e disappearance_edge     Q1  7 0.714286     0.495556        0.218730
wifi_bssid:80:ca:4b:14:42:4a disappearance_edge     Q1  7 0.714286     0.495556        0.218730
wifi_bssid:1c:e8:9e:07:22:d2 disappearance_edge     Q1  7 0.714286     0.495556        0.218730
     usage_app_name:One UI 홈 disappearance_edge     Q3 11 0.818182     0.600000        0.218182
          ble_device_class:0 disappearance_edge     Q3 11 0.818182     0.600000        0.218182
       ble_device_class:7936 disappearance_edge     S4 13 0.769231     0.560000        0.209231
wifi_bssid:9e:25:4a:80:73:13         continuing     S4 29 0.758621     0.560000        0.198621
wifi_bssid:50:46:ae:5f:2e:14 disappearance_edge     S1 16 0.875000     0.682222        0.192778
wifi_bssid:60:a4:b7:3d:19:aa disappearance_edge     S4  8 0.750000     0.560000        0.190000
wifi_bssid:8a:ca:4b:0d:3b:67 disappearance_edge     S4  8 0.750000     0.560000        0.190000
```

## Interpretation notes

- If low-rank label factors group Q/S items differently from the earlier mixture states, the labels have multiple measurement axes rather than one severity axis.
- If BIC does not prefer complex factors but residual anomalies are structured, the data has sparse exceptions/noise rather than smooth latent dimensions.
- Subject-debiased token results are stronger evidence than raw BSSID chi-square because subject prevalence is removed by within-subject centering and permutation.
- Temporal influence edges are not causal. They indicate label grammar: which previous-day answers help complete current answers after controlling subject.
