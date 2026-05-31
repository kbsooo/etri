# E313 Human-Diary Action Signature

Public LB는 사용하지 않았다. 후보 submission delta를 test-side human diary feature에 투영해서, 실제로 건드린 row의 생활 맥락이 action-health를 설명하는지 검증했다.

## Data

- governed rows: `1383`
- candidate files found: `1379` / `1383`
- selected human aggregate columns: `520`
- selector_visible: `418`
- null_rare: `930`
- visible_null_rare: `2`
- strict_health: `1`

## Global Leave-Experiment-Out Metrics

| feature_block | task | n_valid | positive_rate | auc | average_precision | mae | spearman | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| geometry_only | null_common | 1383 | 0.299349 | 0.982733 | 0.960592 |  |  | 0.333633 |
| geometry_plus_human | null_common | 1383 | 0.299349 | 0.953628 | 0.893383 |  |  | 0.337675 |
| geometry_plus_shape | null_common | 1383 | 0.299349 | 0.987170 | 0.964630 |  |  | 0.334677 |
| geometry_shape_human | null_common | 1383 | 0.299349 | 0.956459 | 0.904315 |  |  | 0.331167 |
| human_plus_shape | null_common | 1383 | 0.299349 | 0.906355 | 0.695876 |  |  | 0.344248 |
| human_signature | null_common | 1383 | 0.299349 | 0.866674 | 0.607208 |  |  | 0.367899 |
| semantic_plus_human | null_common | 1383 | 0.299349 | 0.863037 | 0.609268 |  |  | 0.349173 |
| shape_signature | null_common | 1383 | 0.299349 | 0.945643 | 0.811723 |  |  | 0.366385 |
| geometry_only | null_rare | 1383 | 0.672451 | 0.979666 | 0.984642 |  |  | 0.638194 |
| geometry_plus_human | null_rare | 1383 | 0.672451 | 0.958059 | 0.977731 |  |  | 0.603268 |
| geometry_plus_shape | null_rare | 1383 | 0.672451 | 0.984259 | 0.992333 |  |  | 0.639840 |
| geometry_shape_human | null_rare | 1383 | 0.672451 | 0.969243 | 0.984656 |  |  | 0.629479 |
| human_plus_shape | null_rare | 1383 | 0.672451 | 0.922836 | 0.968173 |  |  | 0.621735 |
| human_signature | null_rare | 1383 | 0.672451 | 0.881311 | 0.950571 |  |  | 0.600534 |
| semantic_plus_human | null_rare | 1383 | 0.672451 | 0.878967 | 0.950094 |  |  | 0.608117 |
| shape_signature | null_rare | 1383 | 0.672451 | 0.954553 | 0.980751 |  |  | 0.618210 |
| geometry_only | visible_null_common | 1383 | 0.295011 | 0.985975 | 0.961753 |  |  | 0.317495 |
| geometry_plus_human | visible_null_common | 1383 | 0.295011 | 0.964271 | 0.904815 |  |  | 0.329521 |
| geometry_plus_shape | visible_null_common | 1383 | 0.295011 | 0.990329 | 0.969020 |  |  | 0.319911 |
| geometry_shape_human | visible_null_common | 1383 | 0.295011 | 0.968896 | 0.917855 |  |  | 0.323365 |
| human_plus_shape | visible_null_common | 1383 | 0.295011 | 0.904666 | 0.689882 |  |  | 0.342071 |
| human_signature | visible_null_common | 1383 | 0.295011 | 0.869380 | 0.610888 |  |  | 0.366772 |
| semantic_plus_human | visible_null_common | 1383 | 0.295011 | 0.862875 | 0.605021 |  |  | 0.348026 |
| shape_signature | visible_null_common | 1383 | 0.295011 | 0.945259 | 0.806919 |  |  | 0.363025 |
| geometry_only | action_cliff | 1383 | 0.300795 | 0.993815 | 0.981619 |  |  | 0.321314 |
| geometry_plus_human | action_cliff | 1383 | 0.300795 | 0.981008 | 0.945892 |  |  | 0.329548 |
| geometry_plus_shape | action_cliff | 1383 | 0.300795 | 0.994541 | 0.984091 |  |  | 0.322840 |
| geometry_shape_human | action_cliff | 1383 | 0.300795 | 0.984662 | 0.956283 |  |  | 0.325160 |
| human_plus_shape | action_cliff | 1383 | 0.300795 | 0.911771 | 0.710758 |  |  | 0.350878 |
| human_signature | action_cliff | 1383 | 0.300795 | 0.876575 | 0.627652 |  |  | 0.376598 |
| semantic_plus_human | action_cliff | 1383 | 0.300795 | 0.871765 | 0.622632 |  |  | 0.364044 |
| shape_signature | action_cliff | 1383 | 0.300795 | 0.947344 | 0.814301 |  |  | 0.365669 |
| geometry_only | safe_invisible | 1383 | 0.671005 | 0.982483 | 0.986576 |  |  | 0.639242 |
| geometry_plus_human | safe_invisible | 1383 | 0.671005 | 0.964225 | 0.980203 |  |  | 0.605339 |
| geometry_plus_shape | safe_invisible | 1383 | 0.671005 | 0.987084 | 0.993629 |  |  | 0.639860 |
| geometry_shape_human | safe_invisible | 1383 | 0.671005 | 0.973478 | 0.986444 |  |  | 0.630788 |
| human_plus_shape | safe_invisible | 1383 | 0.671005 | 0.923739 | 0.968520 |  |  | 0.620143 |
| human_signature | safe_invisible | 1383 | 0.671005 | 0.883161 | 0.951323 |  |  | 0.599279 |
| semantic_plus_human | safe_invisible | 1383 | 0.671005 | 0.880037 | 0.950458 |  |  | 0.606566 |
| shape_signature | safe_invisible | 1383 | 0.671005 | 0.955164 | 0.980930 |  |  | 0.617545 |
| geometry_only | strict_health | 1263 | 0.000000 |  |  |  |  | 0.002415 |
| geometry_plus_human | strict_health | 1263 | 0.000000 |  |  |  |  | 0.000750 |
| geometry_plus_shape | strict_health | 1263 | 0.000000 |  |  |  |  | 0.002427 |
| geometry_shape_human | strict_health | 1263 | 0.000000 |  |  |  |  | 0.000805 |
| human_plus_shape | strict_health | 1263 | 0.000000 |  |  |  |  | 0.027179 |
| human_signature | strict_health | 1263 | 0.000000 |  |  |  |  | 0.026171 |
| semantic_plus_human | strict_health | 1263 | 0.000000 |  |  |  |  | 0.026220 |
| shape_signature | strict_health | 1263 | 0.000000 |  |  |  |  | 0.150904 |
| geometry_only | null_strict_rate | 1383 |  |  |  | 0.176086 | 0.788108 | 0.278729 |
| geometry_plus_human | null_strict_rate | 1383 |  |  |  | 0.161137 | 0.777587 | 0.266394 |
| geometry_plus_shape | null_strict_rate | 1383 |  |  |  | 0.165165 | 0.798573 | 0.282369 |
| geometry_shape_human | null_strict_rate | 1383 |  |  |  | 0.154614 | 0.782671 | 0.266875 |
| human_plus_shape | null_strict_rate | 1383 |  |  |  | 0.255591 | 0.711560 | 0.261239 |
| human_signature | null_strict_rate | 1383 |  |  |  | 0.300202 | 0.619198 | 0.250037 |
| semantic_plus_human | null_strict_rate | 1383 |  |  |  | 0.299180 | 0.594071 | 0.261755 |
| shape_signature | null_strict_rate | 1383 |  |  |  | 0.227669 | 0.750855 | 0.309985 |
| geometry_only | readiness_distance | 1383 |  |  |  | 0.863148 | 0.031522 | 1.491594 |
| geometry_plus_human | readiness_distance | 1383 |  |  |  | 0.574383 | 0.620742 | 1.517563 |
| geometry_plus_shape | readiness_distance | 1383 |  |  |  | 0.837603 | 0.059207 | 1.509302 |
| geometry_shape_human | readiness_distance | 1383 |  |  |  | 0.573946 | 0.596882 | 1.504534 |
| human_plus_shape | readiness_distance | 1383 |  |  |  | 0.468517 | 0.664320 | 1.381276 |
| human_signature | readiness_distance | 1383 |  |  |  | 0.452505 | 0.700161 | 1.466414 |
| semantic_plus_human | readiness_distance | 1383 |  |  |  | 0.468620 | 0.664601 | 1.535995 |
| shape_signature | readiness_distance | 1383 |  |  |  | 0.672795 | 0.031040 | 1.417098 |
| geometry_only | actual_p90 | 1383 |  |  |  | 0.000028 | 0.962399 | -0.000010 |
| geometry_plus_human | actual_p90 | 1383 |  |  |  | 0.000033 | 0.778333 | -0.000022 |
| geometry_plus_shape | actual_p90 | 1383 |  |  |  | 0.000024 | 0.967527 | -0.000024 |
| geometry_shape_human | actual_p90 | 1383 |  |  |  | 0.000029 | 0.874711 | -0.000028 |
| human_plus_shape | actual_p90 | 1383 |  |  |  | 0.000116 | 0.539457 | -0.000051 |
| human_signature | actual_p90 | 1383 |  |  |  | 0.000162 | 0.393321 | 0.000006 |
| semantic_plus_human | actual_p90 | 1383 |  |  |  | 0.000172 | 0.169187 | 0.000012 |
| shape_signature | actual_p90 | 1383 |  |  |  | 0.000090 | 0.435406 | -0.000050 |

## Null-Common Readout

| feature_block | auc | average_precision | pred_mean |
| --- | --- | --- | --- |
| geometry_plus_shape | 0.987170 | 0.964630 | 0.334677 |
| geometry_only | 0.982733 | 0.960592 | 0.333633 |
| geometry_shape_human | 0.956459 | 0.904315 | 0.331167 |
| geometry_plus_human | 0.953628 | 0.893383 | 0.337675 |
| shape_signature | 0.945643 | 0.811723 | 0.366385 |
| human_plus_shape | 0.906355 | 0.695876 | 0.344248 |
| human_signature | 0.866674 | 0.607208 | 0.367899 |
| semantic_plus_human | 0.863037 | 0.609268 | 0.349173 |

## Readiness-Distance Readout

| feature_block | mae | pred_mean | spearman |
| --- | --- | --- | --- |
| human_signature | 0.452505 | 1.466414 | 0.700161 |
| semantic_plus_human | 0.468620 | 1.535995 | 0.664601 |
| human_plus_shape | 0.468517 | 1.381276 | 0.664320 |
| geometry_plus_human | 0.574383 | 1.517563 | 0.620742 |
| geometry_shape_human | 0.573946 | 1.504534 | 0.596882 |
| geometry_plus_shape | 0.837603 | 1.509302 | 0.059207 |
| geometry_only | 0.863148 | 1.491594 | 0.031522 |
| shape_signature | 0.672795 | 1.417098 | 0.031040 |

## Top Human-Readiness Rows

| experiment | basename | family | target_norm | selector_visible | null_rare | null_common | actual_p90 | null_strict_rate | readiness_distance | pred_ready__human_signature | pred_ready__geometry_only | failure_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_add_high_preserve_top3_eaa52596.csv | human_plus_geometry | e247_common_vs_e284_extra | False | True | False | -0.000003 | 0.000000 | 2.311123 | -0.764377 | 1.392503 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_add_high_preserve_top3_03ccfe02.csv | human_plus_geometry | e247_common_vs_e284_extra | False | True | False | -0.000002 | 0.000000 | 2.502947 | -0.764377 | 1.393901 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_2b344e02.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000003 | 0.000000 | 0.553273 | -0.111751 | 1.673002 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_a41b61fd.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000007 | 0.000000 | 0.556552 | -0.111751 | 1.675112 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s020_e16333df.csv | bedtime_arousal | multi | False | True | False | -0.000003 | 0.000000 | 1.097252 | -0.103700 | 1.819044 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s014_415aafad.csv | bedtime_arousal | multi | False | True | False | -0.000002 | 0.000000 | 1.098126 | -0.103700 | 1.765916 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_swap_low_high_top3_80ab918c.csv | human_plus_geometry | e247_common_vs_e284_extra | False | True | False | -0.000001 | 0.000000 | 2.550887 | -0.014014 | 1.402111 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_swap_low_high_top3_754c906f.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000007 | 0.000000 | 2.416123 | 0.036174 | 1.674944 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_add_high_preserve_top3_3b1c3d2e.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000007 | 0.000000 | 2.512102 | 0.124743 | 1.642369 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_add_high_preserve_top3_88b70a26.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000004 | 0.000000 | 2.604180 | 0.124743 | 1.640714 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_paymonth_start_near3_money_rumin_top3_f0p5_165a43e0.csv | human_boundary_undo | multi | False | True | False | 0.000015 | 0.000000 | 0.565228 | 0.132896 | 1.961350 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_paymonth_start_near3_money_rumin_top3_f0p25_ab2ac6d8.csv | human_boundary_undo | multi | False | True | False | 0.000008 | 0.000000 | 0.557598 | 0.132896 | 1.959162 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_raw_add_high_preserve_top3_eae4879d.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | False | True | False | 0.000001 | 0.000000 | 2.315484 | 0.226119 | 1.549488 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_raw_add_high_preserve_top3_4d726a04.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | False | True | False | 0.000001 | 0.000000 | 2.505437 | 0.226119 | 1.549494 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_smooth_weighted_ctrl_undo_high_preserve_top3_40fc3712.csv | cell_geometry | e247_body_vs_clean_neither | False | True | False | 0.000007 | 0.000000 | 0.557313 | 0.254969 | 1.650730 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_smooth_weighted_undo_low_preserve_top3_4d6262b1.csv | human_plus_geometry | e247_body_vs_clean_neither | False | True | False | -0.000003 | 0.000000 | 1.168578 | 0.260576 | 1.392576 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_smooth_weighted_undo_low_preserve_top3_7515967c.csv | human_plus_geometry | e247_body_vs_clean_neither | False | True | False | -0.000001 | 0.000000 | 1.279522 | 0.260576 | 1.394173 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_anti_amp_ctrl_undo_high_preserve_top5_8be7e300.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | False | True | False | 0.000012 | 0.000000 | 0.562183 | 0.278071 | 1.653584 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p5_d782dddc.csv | e247_undo_rank | multi | False | True | False | 0.000004 | 0.000000 | 0.587513 | 0.317102 | 1.958223 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p25_16fd395c.csv | e247_undo_rank | multi | False | True | False | 0.000002 | 0.000000 | 0.637793 | 0.317102 | 1.957603 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_anti_amp_swap_low_high_top3_74b24159.csv | human_plus_geometry | e247_body_vs_clean_neither | False | True | False | 0.000004 | 0.000000 | 1.366072 | 0.319256 | 1.665372 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_jepa_prednorm_dateblock_bedtime__top5_f0p25_9206c97f.csv | human_boundary_undo | multi | False | True | False | 0.000007 | 0.000000 | 0.557235 | 0.332013 | 1.985204 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_jepa_prednorm_dateblock_bedtime__top5_f0p5_2f25b414.csv | human_boundary_undo | multi | False | True | False | 0.000014 | 0.000000 | 0.771628 | 0.332013 | 1.988514 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l1_c0p2_raw_undo_low_preserve_top5_9aa3e3a1.csv | human_social | e247_only_vs_e256_only | False | True | False | 0.000011 | 0.000000 | 0.560642 | 0.336803 | 1.603364 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l1_c0p2_raw_undo_low_preserve_top5_be9d8f4d.csv | human_social | e247_only_vs_e256_only | False | True | False | 0.000021 | 0.000000 | 0.826155 | 0.336803 | 1.608743 | safe_but_too_small_or_wrong_sign |

## Slice Metrics

| feature_block | task | slice | n | positive_rate | auc | average_precision | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| geometry_plus_shape | action_cliff | all | 1383 | 0.300795 | 0.994541 | 0.984091 | 0.322840 |
| geometry_only | action_cliff | all | 1383 | 0.300795 | 0.993815 | 0.981619 | 0.321314 |
| geometry_shape_human | action_cliff | all | 1383 | 0.300795 | 0.984662 | 0.956283 | 0.325160 |
| geometry_plus_human | action_cliff | all | 1383 | 0.300795 | 0.981008 | 0.945892 | 0.329548 |
| shape_signature | action_cliff | all | 1383 | 0.300795 | 0.947344 | 0.814301 | 0.365669 |
| human_plus_shape | action_cliff | all | 1383 | 0.300795 | 0.911771 | 0.710758 | 0.350878 |
| human_signature | action_cliff | all | 1383 | 0.300795 | 0.876575 | 0.627652 | 0.376598 |
| semantic_plus_human | action_cliff | all | 1383 | 0.300795 | 0.871765 | 0.622632 | 0.364044 |
| geometry_only | action_cliff | e310_e311 | 79 | 0.645570 | 1.000000 | 1.000000 | 0.660549 |
| geometry_plus_human | action_cliff | e310_e311 | 79 | 0.645570 | 1.000000 | 1.000000 | 0.612419 |
| geometry_plus_shape | action_cliff | e310_e311 | 79 | 0.645570 | 1.000000 | 1.000000 | 0.664559 |
| geometry_shape_human | action_cliff | e310_e311 | 79 | 0.645570 | 1.000000 | 1.000000 | 0.589877 |
| semantic_plus_human | action_cliff | e310_e311 | 79 | 0.645570 | 0.523459 | 0.621828 | 0.759607 |
| human_plus_shape | action_cliff | e310_e311 | 79 | 0.645570 | 0.522409 | 0.640311 | 0.700374 |
| human_signature | action_cliff | e310_e311 | 79 | 0.645570 | 0.507703 | 0.612462 | 0.737043 |
| shape_signature | action_cliff | e310_e311 | 79 | 0.645570 | 0.506303 | 0.647922 | 0.452908 |
| geometry_plus_shape | action_cliff | old_edge_negative | 656 | 0.634146 | 0.978005 | 0.984091 | 0.675202 |
| geometry_only | action_cliff | old_edge_negative | 656 | 0.634146 | 0.975090 | 0.981624 | 0.669923 |
| geometry_shape_human | action_cliff | old_edge_negative | 656 | 0.634146 | 0.946284 | 0.959908 | 0.656813 |
| geometry_plus_human | action_cliff | old_edge_negative | 656 | 0.634146 | 0.935657 | 0.951202 | 0.660350 |
| shape_signature | action_cliff | old_edge_negative | 656 | 0.634146 | 0.873998 | 0.922442 | 0.677516 |
| human_plus_shape | action_cliff | old_edge_negative | 656 | 0.634146 | 0.786508 | 0.826584 | 0.652190 |
| human_signature | action_cliff | old_edge_negative | 656 | 0.634146 | 0.707166 | 0.740937 | 0.671660 |
| semantic_plus_human | action_cliff | old_edge_negative | 656 | 0.634146 | 0.705143 | 0.739484 | 0.644244 |
| human_plus_shape | action_cliff | selector_visible | 418 | 0.995215 | 0.778846 | 0.998802 | 0.785649 |
| human_signature | action_cliff | selector_visible | 418 | 0.995215 | 0.757212 | 0.998665 | 0.776061 |
| semantic_plus_human | action_cliff | selector_visible | 418 | 0.995215 | 0.722356 | 0.998446 | 0.744587 |
| shape_signature | action_cliff | selector_visible | 418 | 0.995215 | 0.716346 | 0.998395 | 0.836690 |
| geometry_plus_shape | action_cliff | selector_visible | 418 | 0.995215 | 0.436298 | 0.994442 | 0.974894 |
| geometry_only | action_cliff | selector_visible | 418 | 0.995215 | 0.415865 | 0.993720 | 0.965990 |
| geometry_shape_human | action_cliff | selector_visible | 418 | 0.995215 | 0.344952 | 0.991816 | 0.921478 |
| geometry_plus_human | action_cliff | selector_visible | 418 | 0.995215 | 0.314904 | 0.990855 | 0.915548 |
| geometry_plus_shape | null_common | all | 1383 | 0.299349 | 0.987170 | 0.964630 | 0.334677 |
| geometry_only | null_common | all | 1383 | 0.299349 | 0.982733 | 0.960592 | 0.333633 |
| geometry_shape_human | null_common | all | 1383 | 0.299349 | 0.956459 | 0.904315 | 0.331167 |
| geometry_plus_human | null_common | all | 1383 | 0.299349 | 0.953628 | 0.893383 | 0.337675 |
| shape_signature | null_common | all | 1383 | 0.299349 | 0.945643 | 0.811723 | 0.366385 |
| human_plus_shape | null_common | all | 1383 | 0.299349 | 0.906355 | 0.695876 | 0.344248 |
| human_signature | null_common | all | 1383 | 0.299349 | 0.866674 | 0.607208 | 0.367899 |
| semantic_plus_human | null_common | all | 1383 | 0.299349 | 0.863037 | 0.609268 | 0.349173 |
| geometry_only | null_common | e310_e311 | 79 | 0.658228 | 0.990028 | 0.995921 | 0.689812 |
| geometry_plus_shape | null_common | e310_e311 | 79 | 0.658228 | 0.990028 | 0.995921 | 0.683957 |
| geometry_plus_human | null_common | e310_e311 | 79 | 0.658228 | 0.922365 | 0.967349 | 0.534663 |
| geometry_shape_human | null_common | e310_e311 | 79 | 0.658228 | 0.896724 | 0.955859 | 0.520249 |
| human_plus_shape | null_common | e310_e311 | 79 | 0.658228 | 0.509972 | 0.639680 | 0.699435 |
| semantic_plus_human | null_common | e310_e311 | 79 | 0.658228 | 0.503917 | 0.625224 | 0.756881 |
| shape_signature | null_common | e310_e311 | 79 | 0.658228 | 0.496439 | 0.658142 | 0.452590 |
| human_signature | null_common | e310_e311 | 79 | 0.658228 | 0.485043 | 0.614042 | 0.735328 |
| geometry_plus_shape | null_common | old_edge_negative | 656 | 0.629573 | 0.954045 | 0.966615 | 0.692841 |
| geometry_only | null_common | old_edge_negative | 656 | 0.629573 | 0.944300 | 0.963133 | 0.691856 |
| geometry_shape_human | null_common | old_edge_negative | 656 | 0.629573 | 0.891749 | 0.926863 | 0.644408 |
| geometry_plus_human | null_common | old_edge_negative | 656 | 0.629573 | 0.880409 | 0.917043 | 0.649708 |
| shape_signature | null_common | old_edge_negative | 656 | 0.629573 | 0.872777 | 0.922089 | 0.674646 |
| human_plus_shape | null_common | old_edge_negative | 656 | 0.629573 | 0.784434 | 0.821154 | 0.637044 |
| human_signature | null_common | old_edge_negative | 656 | 0.629573 | 0.701641 | 0.734980 | 0.652306 |
| semantic_plus_human | null_common | old_edge_negative | 656 | 0.629573 | 0.697068 | 0.738051 | 0.615922 |
| human_plus_shape | null_common | selector_visible | 418 | 0.976077 | 0.779412 | 0.993663 | 0.774149 |
| human_signature | null_common | selector_visible | 418 | 0.976077 | 0.745343 | 0.992353 | 0.754105 |
| shape_signature | null_common | selector_visible | 418 | 0.976077 | 0.700000 | 0.990849 | 0.834099 |
| semantic_plus_human | null_common | selector_visible | 418 | 0.976077 | 0.690686 | 0.990654 | 0.710919 |
| geometry_shape_human | null_common | selector_visible | 418 | 0.976077 | 0.581618 | 0.981417 | 0.883090 |
| geometry_plus_human | null_common | selector_visible | 418 | 0.976077 | 0.567402 | 0.980131 | 0.879014 |
| geometry_plus_shape | null_common | selector_visible | 418 | 0.976077 | 0.539951 | 0.981271 | 0.968170 |
| geometry_only | null_common | selector_visible | 418 | 0.976077 | 0.537255 | 0.981031 | 0.962668 |
| geometry_plus_shape | null_rare | all | 1383 | 0.672451 | 0.984259 | 0.992333 | 0.639840 |
| geometry_only | null_rare | all | 1383 | 0.672451 | 0.979666 | 0.984642 | 0.638194 |
| geometry_shape_human | null_rare | all | 1383 | 0.672451 | 0.969243 | 0.984656 | 0.629479 |
| geometry_plus_human | null_rare | all | 1383 | 0.672451 | 0.958059 | 0.977731 | 0.603268 |
| shape_signature | null_rare | all | 1383 | 0.672451 | 0.954553 | 0.980751 | 0.618210 |
| human_plus_shape | null_rare | all | 1383 | 0.672451 | 0.922836 | 0.968173 | 0.621735 |
| human_signature | null_rare | all | 1383 | 0.672451 | 0.881311 | 0.950571 | 0.600534 |
| semantic_plus_human | null_rare | all | 1383 | 0.672451 | 0.878967 | 0.950094 | 0.608117 |
| geometry_plus_shape | null_rare | e310_e311 | 79 | 0.151899 | 0.940920 | 0.733990 | 0.243449 |
| geometry_only | null_rare | e310_e311 | 79 | 0.151899 | 0.935945 | 0.653987 | 0.259927 |
| geometry_shape_human | null_rare | e310_e311 | 79 | 0.151899 | 0.883706 | 0.576492 | 0.221781 |
| geometry_plus_human | null_rare | e310_e311 | 79 | 0.151899 | 0.858831 | 0.507005 | 0.203458 |
| shape_signature | null_rare | e310_e311 | 79 | 0.151899 | 0.774254 | 0.619232 | 0.462598 |
| human_plus_shape | null_rare | e310_e311 | 79 | 0.151899 | 0.639925 | 0.559300 | 0.225280 |
| semantic_plus_human | null_rare | e310_e311 | 79 | 0.151899 | 0.455846 | 0.388153 | 0.188792 |
| human_signature | null_rare | e310_e311 | 79 | 0.151899 | 0.442164 | 0.346289 | 0.179066 |

## Top Human Signature Coefficients For Null-Common

| feature | coef_null_common | abs_coef |
| --- | --- | --- |
| human_signed__diary_routine_calendar_pc4 | 0.649091 | 0.649091 |
| human_q_minus_s__story_weekend_social_jetlag_subj_z | 0.637367 | 0.637367 |
| human_q_minus_s__story_bright_light_late_subj_z | -0.592804 | 0.592804 |
| human_q_minus_s__story_weekend_social_jetlag | 0.588684 | 0.588684 |
| human_q_minus_s__diary_jepa_prednorm_dateblock_bedtime_phone | 0.505156 | 0.505156 |
| human_signed__diary_jepa_prednorm_dateblock_routine_calendar | -0.452616 | 0.452616 |
| human_q_minus_s__diary_physiology_activity_pc2 | -0.450630 | 0.450630 |
| human_q_minus_s__diary_routine_calendar_pc4 | -0.416050 | 0.416050 |
| human_active__diary_sensor_measurement_pc2 | 0.412142 | 0.412142 |
| human_absw__cash_pay25_pre3_cash_stress_active | -0.407862 | 0.407862 |
| human_q_minus_s__story_bright_light_late | -0.404911 | 0.404911 |
| human_q_minus_s__diary_jepa_resid_dateblock_cognitive_money | 0.398929 | 0.398929 |
| human_q_minus_s__diary_jepa_prednorm_subject_bedtime_phone | 0.378502 | 0.378502 |
| human_absw__story_screen_fragmentation | -0.378199 | 0.378199 |
| human_q_minus_s__cash_pay15_post3_relief_home_subj_z | 0.373442 | 0.373442 |
| human_q_minus_s__story_social_isolation_media | -0.372011 | 0.372011 |
| human_q_minus_s__diary_routine_calendar_pc2 | 0.371864 | 0.371864 |
| human_absw__cash_payeom_pre3_cash_stress_active | 0.368242 | 0.368242 |
| human_signed__diary_physiology_activity_pc4 | 0.367140 | 0.367140 |
| human_signed__diary_routine_calendar_pc3 | 0.364802 | 0.364802 |
| human_absw__story_night_out_mobility | -0.354407 | 0.354407 |
| human_signed__cash_paymonth_start_pre3_cash_stress_active | -0.334785 | 0.334785 |
| human_signed__diary_diary_state_k10_3 | -0.334448 | 0.334448 |
| human_active__cash_monthstart_spending_reset_subj_z | 0.327722 | 0.327722 |
| human_absw__diary_mobility_context_pc2 | 0.323297 | 0.323297 |
| human_active__cash_payeom_post3_spend_outing_subj_z | -0.319834 | 0.319834 |
| human_signed__story_screen_fragmentation_subj_z | -0.317671 | 0.317671 |
| human_active__diary_jepa_prednorm_subject_social_comm | -0.312877 | 0.312877 |
| human_q_minus_s__diary_social_comm_pc1 | 0.306616 | 0.306616 |
| human_absw__cash_pay25_pre7_budget_squeeze_subj_z | -0.304912 | 0.304912 |
| human_active__story_weekend_social_jetlag | 0.303486 | 0.303486 |
| human_absw__story_low_hr_recovery | -0.301289 | 0.301289 |
| human_absw__diary_routine_calendar_pc2 | 0.301014 | 0.301014 |
| human_q_minus_s__cash_pay20_pre3_cash_stress_subj_z | -0.300820 | 0.300820 |
| human_q_minus_s__diary_diary_state_k8 | -0.300102 | 0.300102 |
| human_signed__diary_physiology_activity_pc2 | 0.297876 | 0.297876 |
| human_signed__cash_paymonth_start_near3_money_rumination_active | -0.297502 | 0.297502 |
| human_active__diary_jepa_prednorm_dateblock_bedtime_phone | -0.295746 | 0.295746 |
| human_q_minus_s__cash_pay15_post7_spend_outing_subj_z | -0.292830 | 0.292830 |
| human_signed__story_screen_fragmentation | -0.290839 | 0.290839 |

## Decision

- human_signature null_common AUC: `0.866674`
- geometry_only null_common AUC: `0.982733`
- geometry_shape_human null_common AUC: `0.956459`
- human incremental AUC over geometry: `-0.026273`
- human_signature readiness-distance Spearman: `0.700161`
- geometry_only readiness-distance Spearman: `0.031522`
- Human row placement is predictive by itself but does not improve over action geometry. Treat it as a diagnostic story lens, not a submission certifier.
- No submission is selected by E313.

## Outputs

- `analysis_outputs/e313_human_action_signature_features.csv`
- `analysis_outputs/e313_human_action_signature_metrics.csv`
- `analysis_outputs/e313_human_action_signature_oof.csv`
- `analysis_outputs/e313_human_action_signature_slice_metrics.csv`
- `analysis_outputs/e313_human_action_signature_top_features.csv`
- `analysis_outputs/e313_human_action_signature_readiness_readout.csv`
- `analysis_outputs/e313_human_action_signature_report.md`
