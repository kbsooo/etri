# E217 Teacher-Student Tabular JEPA Probe

## Purpose

Train a teacher-student JEPA closer to the paper mechanics than E215: the context encoder sees masked feature-family blocks plus same-subject row-neighborhood context, while an EMA teacher sees the full current row representation. The learned latent is frozen and tested only as a downstream calibration/gate signal.

## Data

- rows: `700` train+submission rows
- context families: `5`
- mask specs: `12`

## Context Families

| family | columns | components | explained_variance |
| --- | --- | --- | --- |
| deep | 1291 | 10 | 0.415222 |
| prectx | 3240 | 10 | 0.437917 |
| presleep | 406 | 10 | 0.585398 |
| proxy | 158 | 4 | 0.409453 |
| quiet | 600 | 10 | 0.947047 |

## Mask Specs

| name | families | n_families |
| --- | --- | --- |
| single_deep | deep | 1 |
| single_prectx | prectx | 1 |
| single_presleep | presleep | 1 |
| single_proxy | proxy | 1 |
| single_quiet | quiet | 1 |
| pair_deep_prectx | deep,prectx | 2 |
| pair_prectx_presleep | prectx,presleep | 2 |
| pair_presleep_proxy | presleep,proxy | 2 |
| pair_proxy_quiet | proxy,quiet | 2 |
| pair_quiet_deep | deep,quiet | 2 |
| triple_lowfreq | deep,prectx,presleep | 3 |
| triple_highfreq | presleep,proxy,quiet | 3 |

## Same-Subject Neighborhood Context

| metric | value |
| --- | --- |
| mean_neighbor_norm | 4.16421 |
| mean_delta_norm | 6.23773 |
| rows_with_neighbor | 1 |
| meta_columns | 5 |

## JEPA Training Diagnostics

| seed | train_loss | val_loss | mean_teacher_loss | shuffled_teacher_loss | context_var_penalty | pred_var_penalty | target_var_penalty | epochs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 291228 | 0.00131974 | 0.00185272 | 0.0260194 | 0.0415788 | 0 | 0 | 0.0301395 | 720 |
| 291246 | 0.00136206 | 0.00191371 | 0.0262274 | 0.0418611 | 0.000135887 | 0 | 0.0442061 | 720 |
| 291264 | 0.00133675 | 0.00189689 | 0.0268268 | 0.0423812 | 0 | 0.000219049 | 0.0352225 | 720 |

## Embedding Geometry

| embedding | skew_abs | excess_kurt_abs | effective_rank | rank_fraction | cov_eig_cv | cov_condition |
| --- | --- | --- | --- | --- | --- | --- |
| teacher_mean | 0.124868 | 0.279481 | 24.6229 | 0.769466 | 0.754613 | 16.3615 |
| pred_mean | 0.191179 | 0.279568 | 22.6666 | 0.708331 | 0.891565 | 26.0129 |
| context_mean | 0.149621 | 0.219659 | 27.4173 | 0.856791 | 0.551314 | 8.63693 |
| residual | 0.340147 | 0.60214 | 23.1802 | 0.724381 | 1.02192 | 18.5661 |
| hard_residual | 0.366269 | 0.569077 | 23.7897 | 0.743428 | 0.975242 | 17.2883 |

## Downstream Target Summary

| target | best_feature | best_mode | best_c_value | best_weight | best_delta_vs_base | best_mean_delta | best_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | e217_teacher_pc07 | subject_z | 0.2 | 0.45 | -0.00285262 | -0.00162937 | 0.757692 |
| S1 | e217_resid_pc14 | subject_rank | 0.2 | 0.45 | -0.0014245 | 0.000569624 | 0.25 |
| Q3 | e217_resid_pc09 | subject_z | 0.2 | 0.45 | -0.00113447 | -0.000117846 | 0.584615 |
| S4 | e217_teacher_pc15 | subject_center | 0.2 | 0.2 | -0.000419011 | 0.00179371 | 0.173077 |
| S3 | e217_resid_pc13 | subject_z | 0.2 | 0.1 | -4.56112e-05 | 0.000548866 | 0.176923 |
| Q1 | e217_context_pc11 | subject_center | 0.03 | 0 | 0 | 0 | 0 |
| Q2 | e217_resid_pc01 | global_z | 0.03 | 0 | 0 | 0 | 0 |

## Geometry-Stressed Candidates

| target | feature | mode | c_value | best_weight | delta_vs_base | mean_delta | win_rate | geometry_delta_mean | geometry_win_rate | passes_e217_probe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S1 | e217_resid_pc14 | subject_center | 0.2 | 0.3 | -0.000588576 | 0.0012112 | 0.0576923 | -0.000235349 | 0.75 | False |
| S1 | e217_resid_pc14 | subject_z | 0.2 | 0.3 | -0.000712648 | 0.00129247 | 0.0807692 | -0.000217771 | 0.75 | False |
| S1 | e217_resid_pc14 | subject_rank | 0.2 | 0.45 | -0.0014245 | 0.000569624 | 0.25 | -0.000187237 | 0.75 | False |
| S1 | e217_resid_pc14 | subject_rank | 0.1 | 0.3 | -0.000861345 | 0.00102394 | 0.146154 | -0.000147693 | 0.75 | False |
| Q3 | e217_resid_pc09 | global_z | 0.2 | 0.45 | -0.0010198 | -0.00016028 | 0.55 | -5.18246e-05 | 0.75 | False |
| Q3 | e217_resid_pc09 | global_z | 0.1 | 0.3 | -0.000569703 | 0.000216292 | 0.457692 | -4.96822e-05 | 0.5 | False |
| Q3 | e217_resid_pc09 | subject_center | 0.1 | 0.3 | -0.00065303 | 0.000204827 | 0.453846 | -3.07348e-05 | 0.5 | False |
| Q3 | e217_resid_pc09 | subject_center | 0.2 | 0.45 | -0.00112463 | -0.00016898 | 0.580769 | -1.98545e-05 | 0.625 | False |
| Q3 | e217_resid_pc09 | subject_z | 0.1 | 0.3 | -0.000664095 | 0.000283812 | 0.45 | -5.03246e-06 | 0.5 | False |
| Q3 | e217_hard_resid_pc09 | subject_center | 0.1 | 0.3 | -0.000553018 | 0.000249755 | 0.411538 | 1.57935e-05 | 0.5 | False |
| Q3 | e217_hard_resid_pc09 | global_z | 0.2 | 0.45 | -0.000927618 | -0.00016023 | 0.584615 | 1.98684e-05 | 0.5 | False |
| Q3 | e217_resid_pc09 | subject_z | 0.2 | 0.45 | -0.00113447 | -0.000117846 | 0.584615 | 2.15563e-05 | 0.375 | False |
| Q3 | e217_hard_resid_pc09 | subject_z | 0.2 | 0.3 | -0.000553611 | 0.000331022 | 0.392308 | 4.2502e-05 | 0.5 | False |
| Q3 | e217_hard_resid_pc09 | subject_center | 0.2 | 0.45 | -0.0010024 | -0.000125382 | 0.573077 | 4.83976e-05 | 0.5 | False |
| S2 | e217_pred_pc14 | subject_rank | 0.2 | 0.3 | -0.000723762 | 0.00075003 | 0.3 | 0.000138052 | 0.375 | False |
| S2 | e217_teacher_pc07 | global_z | 0.2 | 0.3 | -0.000660347 | 0.000463727 | 0.426923 | 0.000341055 | 0.375 | False |
| S2 | e217_teacher_pc07 | subject_z | 0.2 | 0.45 | -0.00285262 | -0.00162937 | 0.757692 | 0.000409545 | 0.375 | False |
| S2 | e217_teacher_pc07 | subject_center | 0.1 | 0.3 | -0.00083879 | 0.000278626 | 0.465385 | 0.000486097 | 0.375 | False |
| S2 | e217_teacher_pc07 | subject_rank | 0.2 | 0.45 | -0.00240522 | -0.00131524 | 0.742308 | 0.000508567 | 0.5 | False |
| S2 | e217_teacher_pc07 | subject_z | 0.05 | 0.3 | -0.00119577 | 2.01685e-05 | 0.507692 | 0.000579705 | 0.25 | False |
| S2 | e217_teacher_pc07 | subject_z | 0.1 | 0.45 | -0.00234223 | -0.00110718 | 0.707692 | 0.000613005 | 0.375 | False |
| S2 | e217_teacher_pc07 | subject_center | 0.2 | 0.45 | -0.00121816 | 5.10196e-06 | 0.515385 | 0.000617859 | 0.375 | False |
| S2 | e217_teacher_pc07 | subject_rank | 0.05 | 0.3 | -0.000902391 | 0.000191729 | 0.480769 | 0.000649383 | 0.25 | False |
| S2 | e217_teacher_pc07 | subject_rank | 0.1 | 0.45 | -0.00191998 | -0.000846627 | 0.707692 | 0.000710071 | 0.375 | False |

## Decision

- materialization gate pass count: `0`
- E217 has local signal (`S2` via `e217_teacher_pc07`, delta `-0.00285262`) but no geometry-safe materialization gate yet.
- This would weaken full teacher-student JEPA as an immediate submission source, while still keeping its energy features as diagnostics.
