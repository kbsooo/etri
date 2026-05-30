# E215 Masked Family JEPA Probe

## Purpose

Train an I-JEPA-style masked feature-family objective: context is all visible feature-family PCA blocks, target is the hidden family representation block. This tests whether changing the JEPA target representation creates broader or cleaner downstream target signal than E208's feature-neighbor target.

## Data

- rows: `700` train+submission rows
- context families: `5`

## Context Families

| family | columns | components | explained_variance |
| --- | --- | --- | --- |
| deep | 1291 | 10 | 0.415222 |
| prectx | 3240 | 10 | 0.437917 |
| presleep | 406 | 10 | 0.585398 |
| proxy | 158 | 4 | 0.409453 |
| quiet | 600 | 10 | 0.947047 |

## JEPA Training Diagnostics

| seed | train_mse | val_mse | copy_visible_mse | mean_block_mse | hidden_var_penalty | pred_var_penalty | hidden_cov_penalty | epochs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 291218 | 0.442308 | 0.603973 | 1 | 1.00038 | 0.249094 | 0.384642 | 0.222062 | 221 |
| 291234 | 0.450443 | 0.585198 | 1 | 1.00025 | 0.238572 | 0.371802 | 0.228426 | 221 |
| 291256 | 0.407954 | 0.593995 | 1 | 1.00048 | 0.253829 | 0.348754 | 0.201443 | 231 |

## Embedding Geometry

| embedding | skew_abs | excess_kurt_abs | effective_rank | rank_fraction | cov_eig_cv | cov_condition |
| --- | --- | --- | --- | --- | --- | --- |
| pred_mean | 0.317647 | 0.484536 | 15.1432 | 0.344163 | 1.78375 | 301.55 |
| hidden_mean | 0.17395 | 0.276415 | 17.1555 | 0.53611 | 1.29832 | 85.9591 |
| residual | 0.431297 | 4.94111 | 34.9594 | 0.794532 | 0.644105 | 27.91 |

## Downstream Target Summary

| target | best_feature | best_mode | best_c_value | best_weight | best_delta_vs_base | best_mean_delta | best_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | e215_pred_pc06 | subject_rank | 0.2 | 0.45 | -0.00496505 | -0.00467769 | 0.976923 |
| S2 | e215_resid_pc10 | subject_rank | 0.2 | 0.45 | -0.00437042 | -0.00375283 | 0.926923 |
| S4 | e215_deep_resid_abs_mean | subject_rank | 0.2 | 0.45 | -0.00331256 | -0.00204887 | 0.792308 |
| Q3 | e215_pred_pc08 | subject_rank | 0.2 | 0.45 | -0.00151482 | -0.000288302 | 0.588462 |
| S3 | e215_quiet_pred_z02 | subject_z | 0.2 | 0.3 | -0.000872736 | 0.000264833 | 0.376923 |
| S1 | e215_deep_resid_norm | subject_z | 0.2 | 0.3 | -0.000763914 | 0.000821109 | 0.280769 |
| Q2 | e215_hidden_z01 | subject_rank | 0.05 | 0 | 0 | 0 | 0 |

## Geometry-Stressed Candidates

| target | feature | mode | c_value | best_weight | delta_vs_base | mean_delta | win_rate | geometry_delta_mean | geometry_win_rate | passes_e215_probe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | e215_pred_pc06 | subject_rank | 0.2 | 0.45 | -0.00496505 | -0.00467769 | 0.976923 | -0.000754984 | 0.875 | True |
| Q1 | e215_pred_pc06 | subject_rank | 0.1 | 0.45 | -0.00445369 | -0.00417296 | 0.973077 | -0.00058579 | 0.625 | True |
| S4 | e215_deep_resid_abs_mean | subject_rank | 0.2 | 0.45 | -0.00331256 | -0.00204887 | 0.792308 | -0.000275038 | 0.625 | True |
| S4 | e215_deep_resid_abs_mean | subject_z | 0.2 | 0.45 | -0.00296646 | -0.00181339 | 0.780769 | -0.000263331 | 0.625 | True |
| Q1 | e215_pred_pc06 | subject_rank | 0.05 | 0.45 | -0.00319798 | -0.00254565 | 0.903846 | -0.000254276 | 0.5 | True |
| S2 | e215_resid_pc10 | subject_rank | 0.2 | 0.45 | -0.00437042 | -0.00375283 | 0.926923 | -0.000184853 | 0.625 | True |
| S4 | e215_deep_resid_norm | subject_z | 0.2 | 0.45 | -0.00218913 | -0.000844563 | 0.680769 | -0.000169762 | 0.5 | True |
| S4 | e215_deep_resid_abs_mean | subject_rank | 0.1 | 0.45 | -0.00299813 | -0.00197483 | 0.819231 | -0.000110555 | 0.5 | True |
| S4 | e215_deep_resid_abs_mean | subject_z | 0.1 | 0.45 | -0.00268885 | -0.00176548 | 0.803846 | -0.000100114 | 0.625 | True |
| S4 | e215_hidden_z01 | subject_z | 0.2 | 0.45 | -0.00302539 | -0.00113492 | 0.65 | -7.75871e-05 | 0.625 | True |
| S4 | e215_hidden_z01 | subject_center | 0.2 | 0.45 | -0.00301851 | -0.00101804 | 0.584615 | -9.97276e-05 | 0.625 | False |
| S2 | e215_resid_pc10 | subject_rank | 0.1 | 0.45 | -0.00373537 | -0.00296886 | 0.888462 | 1.72167e-05 | 0.625 | False |
| S4 | e215_hidden_z01 | subject_center | 0.1 | 0.45 | -0.00280703 | -0.000961263 | 0.623077 | 4.8817e-05 | 0.375 | False |
| S4 | e215_hidden_z01 | subject_z | 0.1 | 0.45 | -0.0028072 | -0.00106586 | 0.661538 | 6.68661e-05 | 0.375 | False |
| S2 | e215_resid_pc10 | subject_z | 0.2 | 0.45 | -0.00282807 | -0.00213763 | 0.896154 | 0.000102833 | 0.625 | False |
| S4 | e215_deep_resid_abs_mean | subject_rank | 0.05 | 0.45 | -0.00212919 | -0.00125574 | 0.776923 | 0.000192428 | 0.375 | False |
| S2 | e215_resid_pc10 | subject_z | 0.1 | 0.45 | -0.00228471 | -0.00143556 | 0.788462 | 0.000287745 | 0.375 | False |
| S2 | e215_resid_pc10 | subject_rank | 0.05 | 0.45 | -0.00229184 | -0.00119635 | 0.742308 | 0.000390564 | 0.375 | False |

## Decision

- materialization gate pass count: `10`
- E215 found downstream-stressed masked-family JEPA features. Compare them against E208/E211 before materialization; this objective is a representation candidate, not a direct submission yet.
