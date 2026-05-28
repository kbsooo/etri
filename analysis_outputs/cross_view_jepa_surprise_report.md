# Cross-View JEPA Surprise Probe

This probe builds unsupervised cross-view JEPA-style features from existing raw-log representations.
Each sensor view is compressed into PCA latents, then one view predicts another with ridge regression.
The residuals are treated as sensor-view surprise features and tested as fold-safe one-feature logit corrections on top of stage2 OOF.

## Base

- Base OOF: `final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy`
- Base mean log loss: `0.5675309247`
- Feature rows/columns: `450` / `574` train-frame columns
- Prefilter rows: `168`
- Scanned rows: `840`
- Strict repeated-subject passes: `32`

## Best Per Target

```csv
target,feature,mode,corr,c_value,base_loss,best_loss,delta,best_weight
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_max,subject_rank,-0.1715290511,0.5,0.5746308241,0.5702075973,-0.0044232268,0.45
Q2,cvjepa__quiet_fragment_to_measurement_process__resid_pc00,subject_rank,0.1616206804,0.03,0.6429986926,0.6429986926,0.0,0.0
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_rank,0.1360000225,0.5,0.630348489,0.6279806894,-0.0023677995,0.45
S1,cvjepa__measurement_process_to_deep_context__resid_pc05,subject_rank,-0.1243253628,0.5,0.4789432759,0.4769337805,-0.0020094954,0.45
S2,cvjepa__measurement_process_to_rhythm_regular__target_pred_cos,subject_z,-0.1621216337,0.5,0.5389534496,0.5332890935,-0.0056643561,0.45
S3,cvjepa__deep_context_to_deep_phone__resid_pc00,subject_rank,0.1316636,0.5,0.5034376795,0.501324978,-0.0021127015,0.45
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_center,0.1558025412,0.5,0.6034040622,0.599513106,-0.0038909562,0.45
```

## Guarded Top

```csv
target,feature,mode,c_value,delta,best_weight,guard_mean_delta,guard_win_rate,guard_mean_selected_weight,guard_zero_weight_rate,strict_pass
S2,cvjepa__measurement_process_to_rhythm_regular__target_pred_cos,subject_z,0.5,-0.0056643561,0.45,-0.0036203171,0.7615384615,0.3711538462,0.0384615385,True
S2,cvjepa__measurement_process_to_rhythm_regular__target_pred_cos,subject_z,0.2,-0.0052359022,0.45,-0.0032379318,0.7346153846,0.3685769231,0.0538461538,True
S2,cvjepa__sleep_proxy_to_measurement_process__resid_pc01,subject_rank,0.5,-0.0047699641,0.45,-0.0045277061,0.9884615385,0.4375,0.0,True
S2,cvjepa__measurement_process_to_rhythm_regular__target_pred_cos,subject_center,0.5,-0.0046478481,0.45,-0.0023444538,0.6769230769,0.3518461538,0.1115384615,True
S2,cvjepa__measurement_process_to_rhythm_regular__target_pred_cos,subject_z,0.1,-0.0044627844,0.45,-0.0024706769,0.7115384615,0.3586923077,0.0769230769,True
S2,cvjepa__sleep_proxy_to_measurement_process__resid_pc01,subject_rank,0.2,-0.0044256517,0.45,-0.0041153022,0.9769230769,0.4325,0.0,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_max,subject_rank,0.5,-0.0044232268,0.45,-0.0040499942,0.9576923077,0.4161538462,0.0,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_max,subject_rank,0.2,-0.004190655,0.45,-0.003704332,0.95,0.4092307692,0.0,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_center,0.5,-0.0038909562,0.45,-0.001628515,0.6884615385,0.3393846154,0.1115384615,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_mean,subject_rank,0.5,-0.0038511927,0.45,-0.0026517372,0.8346153846,0.3768461538,0.0307692308,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_center,0.2,-0.0037635565,0.45,-0.0017810026,0.7038461538,0.3488461538,0.0961538462,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_max,subject_rank,0.1,-0.0036786647,0.45,-0.0029400129,0.9115384615,0.3921538462,0.0115384615,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_abs_mean,subject_rank,0.2,-0.0036175107,0.45,-0.0024208931,0.8384615385,0.3756538462,0.0307692308,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_center,0.1,-0.0034138106,0.45,-0.0017301684,0.7230769231,0.3517692308,0.0807692308,True
Q1,cvjepa__deep_context_to_quiet_fragment__resid_l2,subject_rank,0.5,-0.0033160214,0.45,-0.0024463509,0.9230769231,0.3711153846,0.0,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_z,0.5,-0.0031011844,0.45,-0.0005758736,0.5730769231,0.3118076923,0.1230769231,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_z,0.2,-0.0029718108,0.45,-0.0007020927,0.5846153846,0.3171923077,0.1230769231,True
S4,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc00,subject_z,0.1,-0.0026257766,0.45,-0.0006857439,0.6192307692,0.3186538462,0.1192307692,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_rank,0.5,-0.0023677995,0.45,-0.0014611214,0.7961538462,0.3621538462,0.0269230769,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_center,0.5,-0.0022303517,0.45,-0.0013995088,0.8192307692,0.3673076923,0.0384615385,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_rank,0.2,-0.002147035,0.45,-0.0013032861,0.7692307692,0.3625384615,0.0423076923,True
S3,cvjepa__deep_context_to_deep_phone__resid_pc00,subject_rank,0.5,-0.0021127015,0.45,-0.0009642143,0.6807692308,0.3525384615,0.0423076923,True
S3,cvjepa__all_context_to_deep_phone__resid_pc00,subject_rank,0.5,-0.0021127015,0.45,-0.0009642143,0.6807692308,0.3525384615,0.0423076923,True
S1,cvjepa__measurement_process_to_deep_context__resid_pc05,subject_rank,0.5,-0.0020094954,0.45,-0.0005513808,0.6115384615,0.3172692308,0.1538461538,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_center,0.2,-0.0020022015,0.45,-0.0011747009,0.7961538462,0.3577692308,0.0384615385,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,subject_z,0.5,-0.0019562502,0.45,-0.0010469529,0.7538461538,0.3468461538,0.0384615385,True
S3,cvjepa__sleep_proxy_to_rhythm_regular__resid_pc03,subject_rank,0.5,-0.0019121995,0.45,-0.0004763188,0.5807692308,0.3024230769,0.1576923077,True
Q3,cvjepa__rhythm_regular_to_sleep_proxy__resid_pc02,global_z,0.5,-0.0018205206,0.45,-0.0009371826,0.7230769231,0.3414230769,0.05,True
```

## Interpretation

- A strict pass means the cross-view residual improves the full subject-block OOF target and survives repeated subject-half weight selection.
- Failing this guard does not make the feature useless; it means it should be treated as a hidden-structure clue rather than a direct submission correction.
- The most valuable features here are residual norms/cosines where sleep/quiet/rhythm latents are not predictable from phone/context/measurement-process latents.