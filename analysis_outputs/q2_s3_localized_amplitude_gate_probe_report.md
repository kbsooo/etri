# E78 Q2/S3 Localized Amplitude Gate Probe

## Observe

E76 says S3-heavy/Q2-low direction is subset-stable but exact E75 amplitude is only partly deployable. E77 says averaging those subset predictions is not enough: safe Q2/S3 posterior movement is sub-margin, while full posterior margin is tail/set unsafe.

## Wonder

Is the missing object a row/target reliability gate over E75's sparse amplitude movement, especially a gate that shrinks Q2 or unstable cells while leaving S3-heavy signal intact?

## Method

- Base movement: E75 full-pool `translator_tail_soft_p90_m0.50` / `top_abs50` unit delta.
- Q2 alpha grid: `[0.0, 4.0, 8.0, 12.0, 16.0, 20.0]`.
- S3 alpha grid: `[16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0]`.
- Reliability maps are derived from E76 source-subset exact-asym, deployable, S3-heavy, and deployable-vs-failed stacks.
- Localizations: both Q2/S3 localized, Q2 localized with full S3, and S3 localized with full Q2.
- Candidates are scored by the same combo, hidden, world, block, and raw-energy gates used by E76/E77.

## Mask Summary

| source_name | mask_mode | threshold | mask_mean_q2 | mask_mean_s3 | mask_active_q2 | mask_active_s3 |
| --- | --- | --- | --- | --- | --- | --- |
| control | identity |  | 1 | 1 | 1 | 1 |
| exact_all | soft_consensus |  | 1 | 1 | 1 | 1 |
| exact_all | hard_consensus_0.55 | 0.55 | 1 | 1 | 1 | 1 |
| exact_all | hard_consensus_0.70 | 0.7 | 1 | 1 | 1 | 1 |
| exact_all | hard_consensus_0.85 | 0.85 | 1 | 1 | 1 | 1 |
| exact_all | hard_sign_0.60 | 0.6 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| exact_all | hard_sign_0.75 | 0.75 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| exact_all | hard_sign_0.90 | 0.9 | 0.875 | 0.769231 | 0.875 | 0.769231 |
| exact_deployable | soft_consensus |  | 1 | 1 | 1 | 1 |
| exact_deployable | hard_consensus_0.55 | 0.55 | 1 | 1 | 1 | 1 |
| exact_deployable | hard_consensus_0.70 | 0.7 | 1 | 1 | 1 | 1 |
| exact_deployable | hard_consensus_0.85 | 0.85 | 1 | 1 | 1 | 1 |
| exact_deployable | hard_sign_0.60 | 0.6 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| exact_deployable | hard_sign_0.75 | 0.75 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| exact_deployable | hard_sign_0.90 | 0.9 | 0.9 | 0.846154 | 0.9 | 0.846154 |
| s3_deployable | soft_consensus |  | 1 | 1 | 1 | 1 |
| s3_deployable | hard_consensus_0.55 | 0.55 | 1 | 1 | 1 | 1 |
| s3_deployable | hard_consensus_0.70 | 0.7 | 1 | 1 | 1 | 1 |
| s3_deployable | hard_consensus_0.85 | 0.85 | 1 | 1 | 1 | 1 |
| s3_deployable | hard_sign_0.60 | 0.6 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| s3_deployable | hard_sign_0.75 | 0.75 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| s3_deployable | hard_sign_0.90 | 0.9 | 0.9 | 0.871795 | 0.9 | 0.871795 |
| all_deployable | soft_consensus |  | 1 | 1 | 1 | 1 |
| all_deployable | hard_consensus_0.55 | 0.55 | 1 | 1 | 1 | 1 |
| all_deployable | hard_consensus_0.70 | 0.7 | 1 | 1 | 1 | 1 |
| all_deployable | hard_consensus_0.85 | 0.85 | 1 | 1 | 1 | 1 |
| all_deployable | hard_sign_0.60 | 0.6 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| all_deployable | hard_sign_0.75 | 0.75 | 0.9 | 0.974359 | 0.9 | 0.974359 |
| all_deployable | hard_sign_0.90 | 0.9 | 0 | 0.871795 | 0 | 0.871795 |
| exact_deployable_vs_failed | soft_excess |  | 0.0101608 | 0.029647 | 0.15 | 0.179487 |
| exact_deployable_vs_failed | hard_excess_q50 | 0.0942055 | 0.05 | 0.128205 | 0.05 | 0.128205 |
| exact_deployable_vs_failed | hard_excess_q70 | 0.229266 | 0 | 0.102564 | 0 | 0.102564 |
| exact_deployable_vs_failed | hard_excess_q85 | 0.229266 | 0 | 0.0512821 | 0 | 0.0512821 |
| exact_deployable_vs_failed | bad_veto_le0.75 | 0.75 | 0.025 | 0.128205 | 0.025 | 0.128205 |
| exact_deployable_vs_failed | bad_veto_le1.00 | 1 | 0.15 | 0.179487 | 0.15 | 0.179487 |
| exact_deployable_vs_failed | bad_veto_le1.25 | 1.25 | 1 | 0.974359 | 1 | 0.974359 |

## Stress Summary

| source_name | mask_mode | localization | rows | strict | deployable | loose | beats_e75_local_all | deployable_beats_e75 | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate | best_alpha_q2 | best_alpha_s3 | best_deployable_delta | best_strict_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s3_deployable | hard_sign_0.90 | s3_local_q2_full | 42 | 21 | 21 | 42 | 0 | 0 | -1.16605e-05 | -6.89494e-06 | 9.25947e-06 | -0.000627097 | -0.000363112 | 0.694444 | 8 | 28 | -1.16605e-05 | -1.16605e-05 |
| all_deployable | hard_sign_0.90 | s3_local_q2_full | 42 | 21 | 21 | 42 | 0 | 0 | -1.16605e-05 | -6.89494e-06 | 9.25947e-06 | -0.000627097 | -0.000363112 | 0.694444 | 8 | 28 | -1.16605e-05 | -1.16605e-05 |
| s3_deployable | hard_sign_0.90 | both | 42 | 21 | 21 | 42 | 0 | 0 | -1.16298e-05 | -6.86431e-06 | 9.28771e-06 | -0.000616824 | -0.000361106 | 0.694444 | 8 | 28 | -1.16298e-05 | -1.16298e-05 |
| control | identity | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | soft_consensus | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | soft_consensus | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | soft_consensus | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.55 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.55 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.55 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.70 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.70 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.70 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.85 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.85 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_consensus_0.85 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | soft_consensus | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | soft_consensus | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | soft_consensus | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.55 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.55 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.55 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.70 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.70 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.70 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.85 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.85 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable | hard_consensus_0.85 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | soft_consensus | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | soft_consensus | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | soft_consensus | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.55 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.55 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.55 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.70 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.70 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.70 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.85 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.85 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| s3_deployable | hard_consensus_0.85 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | soft_consensus | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | soft_consensus | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | soft_consensus | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.55 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.55 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.55 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.70 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.70 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.70 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.85 | both | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.85 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| all_deployable | hard_consensus_0.85 | s3_local_q2_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_deployable_vs_failed | bad_veto_le1.25 | q2_local_s3_full | 42 | 20 | 20 | 42 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000645536 | -0.000405518 | 0.722222 | 8 | 28 | -1.23676e-05 | -1.23676e-05 |
| exact_all | hard_sign_0.60 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| exact_all | hard_sign_0.75 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| exact_deployable | hard_sign_0.60 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| exact_deployable | hard_sign_0.75 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| s3_deployable | hard_sign_0.60 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| s3_deployable | hard_sign_0.75 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |
| all_deployable | hard_sign_0.60 | s3_local_q2_full | 42 | 19 | 19 | 42 | 0 | 0 | -1.22678e-05 | -7.5023e-06 | 9.49753e-06 | -0.000645618 | -0.000381131 | 0.722222 | 8 | 28 | -1.22678e-05 | -1.22678e-05 |

## By Axis

| dominant_axis | localization | rows | strict | deployable | loose | beats_e75 | deployable_beats_e75 | best_all | best_hidden | best_world | best_block |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s3_higher | q2_local_s3_full | 1120 | 454 | 454 | 1120 | 0 | 0 | -1.23676e-05 | -0.000645536 | -0.000405518 | 0.722222 |
| s3_higher | both | 1152 | 420 | 420 | 960 | 0 | 0 | -1.23676e-05 | -0.000645618 | -0.000405518 | 0.722222 |
| s3_higher | s3_local_q2_full | 1120 | 408 | 408 | 928 | 0 | 0 | -1.23676e-05 | -0.000645618 | -0.000405518 | 0.722222 |
| s3_only | q2_local_s3_full | 245 | 105 | 105 | 245 | 0 | 0 | -1.17109e-05 | -0.000343184 | -0.000116425 | 0.583333 |
| s3_only | both | 252 | 86 | 86 | 203 | 0 | 0 | -1.17109e-05 | -0.000343266 | -0.000116425 | 0.583333 |
| s3_only | s3_local_q2_full | 245 | 83 | 83 | 196 | 0 | 0 | -1.17109e-05 | -0.000343266 | -0.000116425 | 0.583333 |
| equal | q2_local_s3_full | 70 | 70 | 70 | 70 | 0 | 0 | -1.10528e-05 | -0.000484506 | -0.000351115 | 0.722222 |
| equal | both | 72 | 57 | 57 | 60 | 0 | 0 | -1.07261e-05 | -0.000484506 | -0.000351115 | 0.722222 |
| equal | s3_local_q2_full | 70 | 56 | 56 | 58 | 0 | 0 | -1.07261e-05 | -0.000484506 | -0.000351115 | 0.722222 |
| q2_higher | q2_local_s3_full | 35 | 34 | 34 | 35 | 0 | 0 | -1.03016e-05 | -0.000449756 | -0.000340418 | 0.722222 |
| q2_higher | both | 36 | 17 | 17 | 30 | 0 | 0 | -1.00055e-05 | -0.000449756 | -0.000340418 | 0.722222 |
| q2_higher | s3_local_q2_full | 35 | 16 | 16 | 29 | 0 | 0 | -1.00055e-05 | -0.000449756 | -0.000340418 | 0.722222 |

## Best Rows

| source_name | mask_mode | localization | alpha_q2 | alpha_s3 | dominant_axis | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | raw_energy_q_p90_minus_base | strict_gate | deployable_gate | loose_gate | beats_e75_local_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control | identity | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | soft_consensus | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.55 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.55 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.55 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.70 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.70 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.85 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.85 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.55 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.55 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.55 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.70 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.70 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.70 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.85 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | hard_consensus_0.85 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| exact_deployable_vs_failed | bad_veto_le1.25 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| all_deployable | soft_consensus | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| s3_deployable | hard_consensus_0.70 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| exact_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| exact_all | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| exact_all | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| exact_all | soft_consensus | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |

## Best Deployable Rows

| source_name | mask_mode | localization | alpha_q2 | alpha_s3 | dominant_axis | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | raw_energy_q_p90_minus_base | beats_e75_local_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control | identity | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | soft_consensus | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.55 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.55 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.55 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.70 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.70 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.70 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.85 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | hard_consensus_0.85 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | soft_consensus | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.55 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.55 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.55 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.70 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.70 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.85 | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.85 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| exact_deployable_vs_failed | bad_veto_le1.25 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| s3_deployable | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| all_deployable | hard_consensus_0.70 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| exact_deployable | hard_consensus_0.85 | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| exact_deployable | hard_consensus_0.85 | s3_local_q2_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| exact_all | soft_consensus | both | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| exact_all | soft_consensus | q2_local_s3_full | 8 | 28 | s3_higher | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |

## Decision

- Localized amplitude creates deployable rows, but none beat E75 local all-combo.
- This probe writes no submission by default. Materialize only if the best deployable row has a clearer stress profile than E73/E75/E74.

## Outputs

- `analysis_outputs/q2_s3_localized_amplitude_gate_probe_scan.csv`
- `analysis_outputs/q2_s3_localized_amplitude_gate_probe_summary.csv`
- `analysis_outputs/q2_s3_localized_amplitude_gate_probe_mask_summary.csv`
