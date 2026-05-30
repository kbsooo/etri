# E208 Feature-Neighbor JEPA Probe

Purpose: actually train a JEPA-style context-to-target representation using the only E207-certified positive-pair regime: feature nearest neighbors in the broad stage2 latent space.

This probe does not materialize a submission. It tests whether the representation beats copy-self/random controls and whether its features survive downstream OOF, subject bootstrap, and geometry stress.

## Data

- rows: `700` train+submission rows
- context families: `5`

## Context Families

| family | columns | components | explained_variance |
| --- | --- | --- | --- |
| deep | 1291 | 10 | 0.415222 |
| prectx | 3240 | 10 | 0.437914 |
| presleep | 406 | 10 | 0.585398 |
| proxy | 158 | 4 | 0.409453 |
| quiet | 600 | 10 | 0.947047 |

## JEPA Training Diagnostics

| seed | train_mse | val_mse | copy_self_mse | mean_target_mse | random_pair_mse | hidden_var_penalty | pred_var_penalty | hidden_cov_penalty | epochs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 261002 | 0.454631 | 0.588331 | 0.812629 | 0.639551 | 1.97909 | 0.201376 | 0.659299 | 0.314522 | 171 |
| 261020 | 0.464782 | 0.555652 | 0.88536 | 0.613004 | 2.07109 | 0.188999 | 0.666241 | 0.311437 | 171 |
| 261038 | 0.425028 | 0.550826 | 0.815146 | 0.630471 | 1.98849 | 0.199363 | 0.623923 | 0.264745 | 181 |

## Embedding Geometry

| embedding | skew_abs | excess_kurt_abs | effective_rank | rank_fraction | cov_eig_cv | cov_condition |
| --- | --- | --- | --- | --- | --- | --- |
| pred_mean | 0.285629 | 0.303127 | 18.3943 | 0.287411 | 1.94091 | 1365.92 |
| hidden_mean | 0.15987 | 0.257722 | 19.5788 | 0.611836 | 1.02816 | 44.0311 |
| pred_resid_self | 0.33282 | 3.14745 | 58.2025 | 0.909414 | 0.384578 | 16.8872 |
| pred_resid_nn | 0.16145 | 0.853142 | 55.6065 | 0.868851 | 0.51232 | 85.0553 |

## Downstream Target Summary

| target | best_feature | best_mode | best_c_value | best_weight | best_delta_vs_base | best_mean_delta | best_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | e208_resid_self_pc10 | subject_center | 0.2 | 0.45 | -0.00645757 | -0.00633163 | 0.95 |
| S2 | e208_pred_pc12 | subject_z | 0.2 | 0.45 | -0.00421528 | -0.00364736 | 0.942308 |
| S4 | e208_pred_pc14 | subject_rank | 0.2 | 0.45 | -0.00313375 | -0.00122957 | 0.673077 |
| S3 | e208_hidden_z00 | subject_center | 0.2 | 0.3 | -0.000536019 | 0.000458777 | 0.334615 |
| Q1 | e208_resid_nn_pc02 | subject_z | 0.2 | 0.2 | -0.000363683 | 0.00087115 | 0.273077 |
| S1 | e208_resid_nn_pc03 | subject_z | 0.2 | 0.1 | -3.55451e-05 | 0.000782027 | 0.0807692 |
| Q2 | e208_resid_self_pc02 | subject_rank | 0.05 | 0 | 0 | 0 | 0 |

## Geometry-Stressed Candidates

| target | feature | mode | c_value | best_weight | delta_vs_base | mean_delta | win_rate | geometry_delta_mean | geometry_win_rate | passes_e208_probe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3 | e208_resid_self_pc10 | subject_z | 0.2 | 0.45 | -0.00581021 | -0.00515223 | 0.926923 | -0.000509835 | 0.75 | True |
| S4 | e208_pred_pc14 | subject_rank | 0.2 | 0.45 | -0.00313375 | -0.00122957 | 0.673077 | -0.000499177 | 0.875 | True |
| Q3 | e208_resid_self_pc10 | subject_center | 0.2 | 0.45 | -0.00645757 | -0.00633163 | 0.95 | -0.000405604 | 0.625 | True |
| Q3 | e208_resid_self_pc10 | subject_rank | 0.2 | 0.45 | -0.00576939 | -0.00483683 | 0.903846 | -0.000378714 | 0.625 | True |
| Q3 | e208_resid_self_pc10 | global_z | 0.2 | 0.45 | -0.00522004 | -0.00466483 | 0.926923 | -0.000221444 | 0.625 | True |
| Q3 | e208_resid_self_pc10 | subject_z | 0.1 | 0.45 | -0.00516202 | -0.00450879 | 0.926923 | -0.000211893 | 0.625 | True |
| Q3 | e208_resid_self_pc10 | subject_center | 0.1 | 0.45 | -0.00577531 | -0.00551477 | 0.95 | -0.000109449 | 0.625 | True |
| Q3 | e208_resid_self_pc10 | subject_rank | 0.1 | 0.45 | -0.00508385 | -0.00423214 | 0.896154 | -8.53563e-05 | 0.5 | True |
| Q3 | e208_resid_self_pc10 | global_z | 0.1 | 0.45 | -0.00451197 | -0.00390503 | 0.919231 | 8.3037e-05 | 0.5 | False |
| S2 | e208_pred_pc12 | subject_rank | 0.2 | 0.45 | -0.0037175 | -0.00299357 | 0.876923 | 0.000104676 | 0.375 | False |
| Q3 | e208_resid_self_pc10 | subject_z | 0.05 | 0.45 | -0.00368112 | -0.00280676 | 0.888462 | 0.000242672 | 0.5 | False |
| S2 | e208_pred_pc12 | subject_z | 0.2 | 0.45 | -0.00421528 | -0.00364736 | 0.942308 | 0.000263555 | 0.375 | False |
| S2 | e208_pred_pc12 | subject_rank | 0.1 | 0.45 | -0.003129 | -0.00228357 | 0.846154 | 0.000312958 | 0.25 | False |
| Q3 | e208_resid_self_pc10 | subject_center | 0.05 | 0.45 | -0.00423324 | -0.00361474 | 0.907692 | 0.000338643 | 0.5 | False |
| Q3 | e208_resid_self_pc10 | subject_rank | 0.05 | 0.45 | -0.00355484 | -0.00254285 | 0.857692 | 0.000359617 | 0.5 | False |
| S2 | e208_pred_pc12 | subject_z | 0.1 | 0.45 | -0.00358506 | -0.00284065 | 0.896154 | 0.00045743 | 0.25 | False |

## Decision

- materialization gate pass count: `8`
- E208 found at least one feature that can move to a separate materialization/stress step. Do not submit directly from this probe; build E209 with the passing operation and compare against E95/E154 public-sensor geometry first.
