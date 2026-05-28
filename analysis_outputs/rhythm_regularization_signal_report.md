# Rhythm Regularization Signal Report

Top rhythm features were evaluated on the stage2 OOF residuals. Positive residual means the base under-predicted label=1.

## Summary
```
target                                              feature           mode   n   raw_mean     raw_std  z_mean    z_std  corr_label  corr_residual  label_rate  base_mean
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev      subject_z 450  20.384444   98.273417    -0.0 0.998888   -0.226920      -0.205638    0.600000   0.605602
    S1    rhythm__rr_mlight_core5h_m_light_min_dev_subj_med      subject_z 450   1.810186   14.603063     0.0 0.998888   -0.133240      -0.200661    0.682222   0.684106
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev subject_center 450 252.466951 1195.646202    -0.0 0.998888    0.172049       0.173773    0.560000   0.561844
```

## Q3: rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev (subject_z)
```
target                                              feature  bin  n    z_mean    raw_mean  label_rate  base_mean  residual_mean
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev    0 90 -1.147977 -103.005556    0.788889   0.673527       0.115362
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev    1 90 -0.592098  -17.244444    0.544444   0.565970      -0.021525
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev    2 90 -0.273768   -3.155556    0.688889   0.600192       0.088697
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev    3 90  0.427513   57.688889    0.566667   0.594061      -0.027395
    Q3 rhythm__rr_hr_pre6h_hr_points_count_same_weekend_dev    4 90  1.586330  167.638889    0.411111   0.594259      -0.183148
```

## S1: rhythm__rr_mlight_core5h_m_light_min_dev_subj_med (subject_z)
```
target                                           feature  bin  n    z_mean  raw_mean  label_rate  base_mean  residual_mean
    S1 rhythm__rr_mlight_core5h_m_light_min_dev_subj_med    0 90 -0.336541  0.011111    0.488889   0.481427       0.007462
    S1 rhythm__rr_mlight_core5h_m_light_min_dev_subj_med    1 90 -0.239975  0.000000    0.677778   0.659449       0.018329
    S1 rhythm__rr_mlight_core5h_m_light_min_dev_subj_med    2 90 -0.033951  0.065789    0.800000   0.807030      -0.007030
    S1 rhythm__rr_mlight_core5h_m_light_min_dev_subj_med    3 90  0.000000  0.000000    0.788889   0.786501       0.002387
    S1 rhythm__rr_mlight_core5h_m_light_min_dev_subj_med    4 90  0.610467 11.863941    0.655556   0.686121      -0.030565
```

## S4: rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev (subject_center)
```
target                                              feature  bin  n    z_mean     raw_mean  label_rate  base_mean  residual_mean
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev    0 90 -1.196167 -1001.459733    0.377778   0.462967      -0.085189
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev    1 90 -0.485899  -313.647918    0.533333   0.601662      -0.068329
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev    2 90 -0.169687   -15.225386    0.522222   0.595450      -0.073228
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev    3 90  0.298568   483.857983    0.733333   0.611296       0.122038
    S4 rhythm__rr_mlight_pre3h_m_light_sum_same_weekend_dev    4 90  1.553184  2108.809811    0.633333   0.537846       0.095487
```
