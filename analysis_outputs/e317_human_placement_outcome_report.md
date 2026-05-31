# E317 Human Placement Outcome Learner

Public LB는 사용하지 않았다. E316의 identity target을 버리고, E315 actual/null placement rows의 local outcome health를 직접 예측했다.

## Dataset

- placement rows: `1072`
- sources: `67`
- actual rows: `67`
- row nulls: `335`
- subject nulls: `335`
- dateblock nulls: `335`
- joint-health positive rate: `0.152052`

## Source-Holdout P90 Rank Health

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_group | predict_p90_rank | human_plus_identity_action | 1072 | 0.468750 | 0.459774 | 0.466347 | 0.276274 |  |  |  |  |  |
| source_group | predict_p90_rank | human_plus_action | 1072 | 0.468750 | 0.451921 | 0.456735 | 0.278569 |  |  |  |  |  |
| source_group | predict_p90_rank | shape_plus_identity | 1072 | 0.468750 | 0.401231 | 0.465651 | 0.254974 |  |  |  |  |  |
| source_group | predict_p90_rank | identity_signal | 1072 | 0.468750 | 0.397845 | 0.465730 | 0.254962 |  |  |  |  |  |
| source_group | predict_p90_rank | human_signature | 1072 | 0.468750 | 0.320748 | 0.317729 | 0.302643 |  |  |  |  |  |
| source_group | predict_p90_rank | shape_signature | 1072 | 0.468750 | 0.000000 | 0.000000 | 0.288111 |  |  |  |  |  |
| source_group | predict_p90_rank | action_shape | 1072 | 0.468750 | 0.000000 | 0.000000 | 0.288111 |  |  |  |  |  |

## Source-Holdout Health Score

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_group | predict_health_score | human_plus_identity_action | 1072 | 3.587687 | 0.645843 | 0.637230 | 0.754602 |  |  |  |  |  |
| source_group | predict_health_score | human_plus_action | 1072 | 3.587687 | 0.626088 | 0.609235 | 0.785171 |  |  |  |  |  |
| source_group | predict_health_score | shape_plus_identity | 1072 | 3.587687 | 0.574693 | 0.617131 | 0.731702 |  |  |  |  |  |
| source_group | predict_health_score | human_signature | 1072 | 3.587687 | 0.553735 | 0.513368 | 0.845105 |  |  |  |  |  |
| source_group | predict_health_score | identity_signal | 1072 | 3.587687 | 0.489305 | 0.570706 | 0.763604 |  |  |  |  |  |
| source_group | predict_health_score | shape_signature | 1072 | 3.587687 | 0.170867 | 0.229578 | 0.905060 |  |  |  |  |  |
| source_group | predict_health_score | action_shape | 1072 | 3.587687 | 0.161161 | 0.205946 | 0.911325 |  |  |  |  |  |

## Source-Holdout Joint Health

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| source_group | classify_joint_health | shape_plus_identity | 1072 |  |  |  |  | 0.152052 | 0.794344 | 0.359368 | 0.547311 | 0.402096 |
| source_group | classify_joint_health | human_plus_identity_action | 1072 |  |  |  |  | 0.152052 | 0.746526 | 0.342618 | 0.615890 | 0.294033 |
| source_group | classify_joint_health | human_plus_action | 1072 |  |  |  |  | 0.152052 | 0.738116 | 0.330973 | 0.631020 | 0.295626 |
| source_group | classify_joint_health | human_signature | 1072 |  |  |  |  | 0.152052 | 0.731185 | 0.316685 | 0.646129 | 0.299472 |
| source_group | classify_joint_health | action_shape | 1072 |  |  |  |  | 0.152052 | 0.683432 | 0.234892 | 0.620641 | 0.444171 |
| source_group | classify_joint_health | shape_signature | 1072 |  |  |  |  | 0.152052 | 0.680401 | 0.238003 | 0.626482 | 0.451893 |
| source_group | classify_joint_health | identity_signal | 1072 |  |  |  |  | 0.152052 | 0.678063 | 0.224650 | 0.616484 | 0.443439 |

## Leave-Mode-Out P90 Rank Health

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| leave_mode_actual | target_p90_rank_health | identity_signal | 67 | 0.620336 | -0.209566 | 0.248154 | 0.186472 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | shape_plus_identity | 67 | 0.620336 | -0.384249 | 0.019894 | 0.188398 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | human_signature | 67 | 0.620336 | -0.408087 | -0.460207 | 0.255868 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | human_plus_identity_action | 67 | 0.620336 | -0.458828 | -0.428217 | 0.245202 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | human_plus_action | 67 | 0.620336 | -0.475120 | -0.459742 | 0.250318 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | shape_signature | 67 | 0.620336 | -0.529006 | -0.487496 | 0.242036 |  |  |  |  |  |
| leave_mode_actual | target_p90_rank_health | action_shape | 67 | 0.620336 | -0.616245 | -0.680141 | 0.244056 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | human_signature | 335 | 0.532649 | 0.185752 | 0.186470 | 0.284870 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | human_plus_action | 335 | 0.532649 | 0.099669 | 0.097017 | 0.281593 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | identity_signal | 335 | 0.532649 | 0.091581 | 0.133381 | 0.256265 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | human_plus_identity_action | 335 | 0.532649 | 0.075981 | 0.082603 | 0.284206 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | shape_plus_identity | 335 | 0.532649 | -0.248915 | -0.298165 | 0.267991 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | shape_signature | 335 | 0.532649 | -0.282442 | -0.318305 | 0.266988 |  |  |  |  |  |
| leave_mode_dateblock | target_p90_rank_health | action_shape | 335 | 0.532649 | -0.311287 | -0.340053 | 0.268763 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | human_plus_identity_action | 335 | 0.269590 | 0.106610 | 0.046489 | 0.519061 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | human_plus_action | 335 | 0.269590 | 0.103961 | 0.046366 | 0.528035 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | human_signature | 335 | 0.269590 | 0.098838 | 0.044533 | 0.535583 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | identity_signal | 335 | 0.269590 | -0.011882 | -0.047602 | 0.388106 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | shape_signature | 335 | 0.269590 | -0.407116 | -0.581134 | 0.433390 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | shape_plus_identity | 335 | 0.269590 | -0.407165 | -0.555887 | 0.423762 |  |  |  |  |  |
| leave_mode_row | target_p90_rank_health | action_shape | 335 | 0.269590 | -0.431518 | -0.598060 | 0.435630 |  |  |  |  |  |
| leave_mode_subject | target_p90_rank_health | human_signature | 335 | 0.573694 | 0.115472 | 0.102701 | 0.394070 |  |  |  |  |  |
| leave_mode_subject | target_p90_rank_health | human_plus_action | 335 | 0.573694 | 0.065025 | 0.058991 | 0.383696 |  |  |  |  |  |
| leave_mode_subject | target_p90_rank_health | human_plus_identity_action | 335 | 0.573694 | 0.050045 | 0.042795 | 0.380955 |  |  |  |  |  |

## Mode and Source Summary

| summary | feature_block | value | n |
| --- | --- | --- | --- |
| null_mode_holdout_joint_auc_mean | shape_signature | 0.670704 | 3 |
| null_mode_holdout_joint_auc_mean | action_shape | 0.659182 | 3 |
| null_mode_holdout_joint_auc_mean | shape_plus_identity | 0.654984 | 3 |
| null_mode_holdout_joint_auc_mean | human_plus_action | 0.650849 | 3 |
| null_mode_holdout_joint_auc_mean | human_plus_identity_action | 0.647610 | 3 |
| null_mode_holdout_joint_auc_mean | human_signature | 0.643183 | 3 |
| null_mode_holdout_joint_auc_mean | identity_signal | 0.437081 | 3 |
| null_mode_holdout_p90_spearman_mean | human_signature | 0.133354 | 3 |
| null_mode_holdout_p90_spearman_mean | human_plus_action | 0.089551 | 3 |
| null_mode_holdout_p90_spearman_mean | human_plus_identity_action | 0.077545 | 3 |
| null_mode_holdout_p90_spearman_mean | identity_signal | 0.035977 | 3 |
| null_mode_holdout_p90_spearman_mean | shape_plus_identity | -0.318810 | 3 |
| null_mode_holdout_p90_spearman_mean | shape_signature | -0.337744 | 3 |
| null_mode_holdout_p90_spearman_mean | action_shape | -0.358750 | 3 |

| summary | feature_block | value | n |
| --- | --- | --- | --- |
| within_mode_joint_auc_mean | action_shape | 0.768215 | 4 |
| within_mode_joint_auc_mean | human_plus_action | 0.733018 | 4 |
| within_mode_joint_auc_mean | human_plus_identity_action | 0.733018 | 4 |
| within_mode_joint_auc_mean | shape_signature | 0.714201 | 4 |
| within_mode_joint_auc_mean | human_signature | 0.710989 | 4 |
| within_mode_joint_auc_mean | shape_plus_identity | 0.704294 | 4 |
| within_mode_joint_auc_mean | identity_signal | 0.525496 | 4 |
| within_mode_p90_spearman_mean | action_shape | 0.326136 | 4 |
| within_mode_p90_spearman_mean | human_plus_action | 0.311831 | 4 |
| within_mode_p90_spearman_mean | human_plus_identity_action | 0.311831 | 4 |
| within_mode_p90_spearman_mean | shape_signature | 0.272938 | 4 |
| within_mode_p90_spearman_mean | shape_plus_identity | 0.248519 | 4 |
| within_mode_p90_spearman_mean | human_signature | 0.238693 | 4 |
| within_mode_p90_spearman_mean | identity_signal | -0.076825 | 4 |

| summary | feature_block | value | n |
| --- | --- | --- | --- |
| source_top_mode_accuracy | human_plus_identity_action | 0.582090 | 67 |
| source_top_mode_accuracy | human_plus_action | 0.552239 | 67 |
| source_top_mode_accuracy | human_signature | 0.432836 | 67 |
| source_top_mode_accuracy | action_shape | 0.029851 | 67 |
| source_top_mode_accuracy | identity_signal | 0.029851 | 67 |
| source_top_mode_accuracy | shape_plus_identity | 0.029851 | 67 |
| source_top_mode_accuracy | shape_signature | 0.029851 | 67 |

## Within-Mode P90 Rank Health

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| within_mode_actual | target_p90_rank_health | human_plus_action | 67 | 0.620336 | 0.418730 | -0.160132 | 0.898023 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | human_plus_identity_action | 67 | 0.620336 | 0.418730 | -0.160132 | 0.898023 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | action_shape | 67 | 0.620336 | 0.417926 | 0.503790 | 0.153388 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | human_signature | 67 | 0.620336 | 0.411962 | -0.181014 | 1.138145 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | shape_signature | 67 | 0.620336 | 0.298475 | 0.258776 | 0.172831 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | shape_plus_identity | 67 | 0.620336 | 0.188912 | -0.234237 | 0.806261 |  |  |  |  |  |
| within_mode_actual | target_p90_rank_health | identity_signal | 67 | 0.620336 | -0.187554 | -0.257417 | 1.199890 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | human_plus_action | 335 | 0.532649 | 0.274249 | 0.286313 | 0.278261 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | human_plus_identity_action | 335 | 0.532649 | 0.274249 | 0.286313 | 0.278261 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | human_signature | 335 | 0.532649 | 0.268949 | 0.284763 | 0.275956 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | shape_plus_identity | 335 | 0.532649 | 0.230987 | 0.268026 | 0.229529 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | action_shape | 335 | 0.532649 | 0.218654 | 0.278993 | 0.228623 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | shape_signature | 335 | 0.532649 | 0.208745 | 0.257883 | 0.230026 |  |  |  |  |  |
| within_mode_dateblock | target_p90_rank_health | identity_signal | 335 | 0.532649 | 0.005747 | 0.067452 | 0.237827 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | action_shape | 335 | 0.269590 | 0.391662 | 0.581689 | 0.224024 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | human_plus_action | 335 | 0.269590 | 0.376703 | 0.416672 | 0.306917 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | human_plus_identity_action | 335 | 0.269590 | 0.376703 | 0.416672 | 0.306917 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | shape_signature | 335 | 0.269590 | 0.355664 | 0.553718 | 0.229399 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | shape_plus_identity | 335 | 0.269590 | 0.344011 | 0.551771 | 0.229771 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | human_signature | 335 | 0.269590 | 0.096092 | 0.102750 | 0.394616 |  |  |  |  |  |
| within_mode_row | target_p90_rank_health | identity_signal | 335 | 0.269590 | -0.038613 | -0.032655 | 0.276754 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | action_shape | 335 | 0.573694 | 0.276301 | 0.352014 | 0.243680 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | shape_plus_identity | 335 | 0.573694 | 0.230163 | 0.305952 | 0.248259 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | shape_signature | 335 | 0.573694 | 0.228865 | 0.324889 | 0.246232 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | human_signature | 335 | 0.573694 | 0.177770 | 0.227033 | 0.330481 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | human_plus_action | 335 | 0.573694 | 0.177642 | 0.217107 | 0.337475 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | human_plus_identity_action | 335 | 0.573694 | 0.177642 | 0.217107 | 0.337475 |  |  |  |  |  |
| within_mode_subject | target_p90_rank_health | identity_signal | 335 | 0.573694 | -0.086879 | -0.104648 | 0.262761 |  |  |  |  |  |

## Leave-Mode-Out Joint Health

| split | task | feature_block | n | target_mean | spearman | pearson | rmse | positive_rate | auc | average_precision | logloss | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| leave_mode_actual | target_joint_health | action_shape | 67 |  |  |  |  | 0.134328 | 0.613985 | 0.191986 | 0.618937 | 0.448387 |
| leave_mode_actual | target_joint_health | shape_signature | 67 |  |  |  |  | 0.134328 | 0.564176 | 0.173748 | 0.640541 | 0.452453 |
| leave_mode_actual | target_joint_health | shape_plus_identity | 67 |  |  |  |  | 0.134328 | 0.546935 | 0.149865 | 0.542195 | 0.379787 |
| leave_mode_actual | target_joint_health | human_plus_identity_action | 67 |  |  |  |  | 0.134328 | 0.531609 | 0.158034 | 0.583013 | 0.346508 |
| leave_mode_actual | target_joint_health | human_plus_action | 67 |  |  |  |  | 0.134328 | 0.516284 | 0.152655 | 0.694774 | 0.426226 |
| leave_mode_actual | target_joint_health | human_signature | 67 |  |  |  |  | 0.134328 | 0.476054 | 0.143190 | 0.643773 | 0.391901 |
| leave_mode_actual | target_joint_health | identity_signal | 67 |  |  |  |  | 0.134328 | 0.403257 | 0.238971 | 0.703419 | 0.507217 |
| leave_mode_dateblock | target_joint_health | shape_signature | 335 |  |  |  |  | 0.185075 | 0.666253 | 0.292036 | 0.619265 | 0.453163 |
| leave_mode_dateblock | target_joint_health | shape_plus_identity | 335 |  |  |  |  | 0.185075 | 0.652783 | 0.259996 | 0.507211 | 0.343332 |
| leave_mode_dateblock | target_joint_health | human_signature | 335 |  |  |  |  | 0.185075 | 0.649947 | 0.357277 | 0.911752 | 0.446731 |
| leave_mode_dateblock | target_joint_health | human_plus_action | 335 |  |  |  |  | 0.185075 | 0.647170 | 0.342909 | 0.903302 | 0.437536 |
| leave_mode_dateblock | target_joint_health | action_shape | 335 |  |  |  |  | 0.185075 | 0.644246 | 0.244803 | 0.619883 | 0.444100 |
| leave_mode_dateblock | target_joint_health | human_plus_identity_action | 335 |  |  |  |  | 0.185075 | 0.635058 | 0.332631 | 0.706979 | 0.309671 |
| leave_mode_dateblock | target_joint_health | identity_signal | 335 |  |  |  |  | 0.185075 | 0.500650 | 0.240649 | 0.558133 | 0.366145 |
| leave_mode_row | target_joint_health | human_plus_action | 335 |  |  |  |  | 0.017910 | 0.672239 | 0.056178 | 1.362404 | 0.448037 |
| leave_mode_row | target_joint_health | human_plus_identity_action | 335 |  |  |  |  | 0.017910 | 0.671226 | 0.056325 | 1.365375 | 0.447944 |
| leave_mode_row | target_joint_health | action_shape | 335 |  |  |  |  | 0.017910 | 0.668946 | 0.028779 | 0.675107 | 0.452728 |
| leave_mode_row | target_joint_health | shape_signature | 335 |  |  |  |  | 0.017910 | 0.660841 | 0.036012 | 0.676631 | 0.457369 |
| leave_mode_row | target_joint_health | shape_plus_identity | 335 |  |  |  |  | 0.017910 | 0.647416 | 0.032819 | 0.662513 | 0.450114 |
| leave_mode_row | target_joint_health | human_signature | 335 |  |  |  |  | 0.017910 | 0.645390 | 0.071246 | 1.195422 | 0.424998 |
| leave_mode_row | target_joint_health | identity_signal | 335 |  |  |  |  | 0.017910 | 0.356636 | 0.017777 | 0.668627 | 0.486801 |
| leave_mode_subject | target_joint_health | shape_signature | 335 |  |  |  |  | 0.256716 | 0.685019 | 0.363335 | 0.602494 | 0.444139 |
| leave_mode_subject | target_joint_health | shape_plus_identity | 335 |  |  |  |  | 0.256716 | 0.664752 | 0.359594 | 0.536782 | 0.345477 |
| leave_mode_subject | target_joint_health | action_shape | 335 |  |  |  |  | 0.256716 | 0.664355 | 0.328224 | 0.608560 | 0.434041 |

## Source Readout

| source_basename | feature_block | recipe | actual_pred_rank_health | actual_true_rank_health | pred_top_mode | true_top_mode | source_actual_p90 | source_null_strict_rate | source_worst_mode_p90_dominance | source_final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e315_humancomp_family_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv__09a4b12d.csv | action_shape | family_consensus | 0.468750 | 0.250000 | actual | row | -0.000171 | 0.772727 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c160_w12_00_6e0c7ea0.csv | action_shape | family_consensus | 0.468750 | 0.750000 | actual | subject | -0.000265 | 0.454545 | 0.600000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c24_w12_00_0958e5f2.csv | action_shape | family_consensus | 0.468750 | 0.437500 | actual | subject | -0.000290 | 0.681818 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c48_w12_00_e61f47be.csv | action_shape | family_consensus | 0.468750 | 0.562500 | actual | subject | -0.000258 | 0.636364 | 0.400000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c96_w12_00_6e0c7ea0.csv | action_shape | family_consensus | 0.468750 | 0.750000 | actual | subject | -0.000265 | 0.590909 | 0.600000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_call_w12_00_6e0c7ea0.csv | action_shape | family_consensus | 0.468750 | 0.625000 | actual | dateblock | -0.000265 | 0.636364 | 0.400000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c160_w5_00_5548dd85.csv | action_shape | family_consensus | 0.468750 | 0.562500 | actual | subject | -0.000200 | 0.545455 | 0.200000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c160_w8_00_6d271745.csv | action_shape | family_consensus | 0.468750 | 0.875000 | actual | row | -0.000294 | 0.500000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w12_00_7d4e5920.csv | action_shape | family_consensus | 0.468750 | 0.625000 | actual | subject | -0.000304 | 0.727273 | 0.400000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w5_00_827a8fe9.csv | action_shape | family_consensus | 0.468750 | 0.375000 | actual | subject | -0.000235 | 0.636364 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w8_00_82833aba.csv | action_shape | family_consensus | 0.468750 | 0.437500 | actual | dateblock | -0.000291 | 0.636364 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w12_00_8467d720.csv | action_shape | family_consensus | 0.468750 | 0.562500 | actual | dateblock | -0.000339 | 0.545455 | 0.200000 | information_sensor_only |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w5_00_d15a6127.csv | action_shape | family_consensus | 0.468750 | 0.437500 | actual | subject | -0.000229 | 0.590909 | 0.200000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w8_00_af769609.csv | action_shape | family_consensus | 0.468750 | 0.562500 | actual | dateblock | -0.000337 | 0.500000 | 0.400000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c96_w5_00_5548dd85.csv | action_shape | family_consensus | 0.468750 | 0.625000 | actual | subject | -0.000200 | 0.636364 | 0.200000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c96_w8_00_6d271745.csv | action_shape | family_consensus | 0.468750 | 0.750000 | actual | dateblock | -0.000294 | 0.545455 | 0.600000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_call_w5_00_5548dd85.csv | action_shape | family_consensus | 0.468750 | 0.375000 | actual | subject | -0.000200 | 0.545455 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_call_w8_00_6d271745.csv | action_shape | family_consensus | 0.468750 | 0.812500 | actual | subject | -0.000294 | 0.545455 | 0.600000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c160_w10_00_f27cec0c.csv | action_shape | ranked_negative_stack | 0.468750 | 0.375000 | actual | subject | -0.000205 | 0.636364 | 0.000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c160_w4_00_f7d22a7c.csv | action_shape | ranked_negative_stack | 0.468750 | 0.562500 | actual | row | -0.000192 | 0.636364 | 0.400000 | blocked_by_human_ready_composition_nulls |

## Top Human/Action Coefficients

| task | feature_block | feature | coef | abs_coef |
| --- | --- | --- | --- | --- |
| classify_joint_health | human_plus_identity_action | meta_mode_row | -0.751819 | 0.751819 |
| classify_joint_health | human_plus_identity_action | human_q_minus_s__diary_mobility_context_pc4 | 0.515718 | 0.515718 |
| classify_joint_health | human_plus_identity_action | meta_mode_subject | 0.515144 | 0.515144 |
| classify_joint_health | human_plus_action | source__abs_Q1 | 0.512981 | 0.512981 |
| classify_joint_health | human_signature | human_q_minus_s__diary_mobility_context_pc4 | 0.501054 | 0.501054 |
| classify_joint_health | human_plus_action | human_q_minus_s__diary_mobility_context_pc4 | 0.493652 | 0.493652 |
| classify_joint_health | human_plus_action | human_q_minus_s__cash_pay25_near3_money_rumination_subj_z | 0.476267 | 0.476267 |
| classify_joint_health | human_plus_identity_action | human_q_minus_s__cash_pay25_post3_relief_home_subj_z | -0.475935 | 0.475935 |
| classify_joint_health | human_plus_identity_action | source__abs_Q1 | 0.474497 | 0.474497 |
| classify_joint_health | human_plus_action | human_q_minus_s__cash_pay25_post3_relief_home_subj_z | -0.469560 | 0.469560 |
| classify_joint_health | human_plus_identity_action | human_q_minus_s__cash_pay25_near3_money_rumination_subj_z | 0.468136 | 0.468136 |
| classify_joint_health | human_signature | human_q_minus_s__cash_pay25_near3_money_rumination_subj_z | 0.467216 | 0.467216 |
| classify_joint_health | human_signature | human_q_minus_s__cash_pay25_pre7_budget_squeeze_subj_z | -0.465177 | 0.465177 |
| classify_joint_health | human_plus_identity_action | human_signed__diary_mobility_context_pc4 | -0.462130 | 0.462130 |
| classify_joint_health | human_signature | human_signed__diary_mobility_context_pc4 | -0.447724 | 0.447724 |
| classify_joint_health | human_plus_action | human_signed__diary_diary_state_k10_0 | -0.433803 | 0.433803 |
| classify_joint_health | human_signature | human_signed__diary_diary_state_k10_0 | -0.430477 | 0.430477 |
| classify_joint_health | human_signature | human_signed__diary_bedtime_phone_pc4 | 0.417913 | 0.417913 |
| classify_joint_health | human_signature | human_signed__diary_jepa_resid_dateblock_physiology_activity | -0.412943 | 0.412943 |
| classify_joint_health | human_plus_action | source__abs_Q3 | -0.412625 | 0.412625 |
| classify_joint_health | human_plus_identity_action | source__abs_Q3 | -0.411154 | 0.411154 |
| classify_joint_health | human_plus_action | human_q_minus_s__cash_pay25_pre7_budget_squeeze_subj_z | -0.408377 | 0.408377 |
| classify_joint_health | human_plus_identity_action | human_signed__cash_paymonth_start_post3_relief_home_subj_z | -0.405496 | 0.405496 |
| classify_joint_health | human_signature | human_signed__diary_diary_state_k6_1 | -0.402956 | 0.402956 |
| classify_joint_health | human_signature | human_q_minus_s__cash_pay25_post3_relief_home_subj_z | -0.401888 | 0.401888 |
| classify_joint_health | human_signature | human_signed__cash_paymonth_start_post3_relief_home_subj_z | -0.399299 | 0.399299 |
| classify_joint_health | human_plus_identity_action | human_q_minus_s__cash_pay25_pre7_budget_squeeze_subj_z | -0.393040 | 0.393040 |
| classify_joint_health | human_plus_action | human_absw__story_physical_fatigue | 0.392760 | 0.392760 |
| classify_joint_health | human_plus_action | human_signed__cash_paymonth_start_post3_relief_home_subj_z | -0.392305 | 0.392305 |
| classify_joint_health | human_signature | human_signed__diary_physiology_activity_pc2 | -0.391339 | 0.391339 |
| classify_joint_health | human_signature | human_signed__diary_jepa_resid_dateblock_social_comm | -0.387170 | 0.387170 |
| classify_joint_health | human_plus_action | human_signed__diary_physiology_activity_pc2 | -0.385168 | 0.385168 |
| classify_joint_health | human_plus_action | human_signed__diary_mobility_context_pc4 | -0.385017 | 0.385017 |
| classify_joint_health | human_plus_identity_action | human_absw__story_physical_fatigue | 0.384833 | 0.384833 |
| classify_joint_health | human_signature | human_signed__diary_diary_state_k4_1 | -0.384449 | 0.384449 |
| classify_joint_health | human_plus_identity_action | human_signed__diary_diary_state_k10_0 | -0.383923 | 0.383923 |
| classify_joint_health | human_plus_action | human_signed__diary_diary_state_k6_1 | -0.380185 | 0.380185 |
| classify_joint_health | human_signature | human_q_minus_s__diary_diary_state_k10_2 | 0.376981 | 0.376981 |
| classify_joint_health | human_plus_action | human_signed__story_media_binge_late | -0.376940 | 0.376940 |
| classify_joint_health | human_signature | human_absw__story_physical_fatigue | 0.374874 | 0.374874 |
| classify_joint_health | human_plus_action | human_signed__diary_jepa_resid_dateblock_social_comm | -0.374606 | 0.374606 |
| classify_joint_health | human_plus_action | human_signed__story_quiet_dark_bedtime_subj_z | 0.370317 | 0.370317 |
| classify_joint_health | human_plus_action | human_q_minus_s__diary_mobility_context_pc3 | -0.364395 | 0.364395 |
| classify_joint_health | human_signature | human_signed__diary_jepa_prednorm_subject_physiology_activity | 0.364340 | 0.364340 |
| classify_joint_health | human_plus_identity_action | human_signed__diary_physiology_activity_pc2 | -0.364281 | 0.364281 |
| classify_joint_health | human_plus_identity_action | human_signed__diary_diary_state_k4_1 | -0.362428 | 0.362428 |
| classify_joint_health | human_signature | human_signed__story_quiet_dark_bedtime_subj_z | 0.359733 | 0.359733 |
| classify_joint_health | human_signature | human_q_minus_s__diary_jepa_resid_dateblock_routine_calendar | -0.359282 | 0.359282 |
| classify_joint_health | human_plus_action | human_signed__diary_diary_state_pc5 | 0.357145 | 0.357145 |
| classify_joint_health | human_plus_action | human_absw__diary_physiology_activity_pc1 | -0.356821 | 0.356821 |

## Decision

- Human diary signatures beat action shape on source-held placement health. This would support a live placement-health latent.
- Within a fixed placement mode, action shape is stronger than human-only context (`0.326136` vs `0.238693` mean Spearman).
- Across held-out null modes, human-only context is the only positive p90-rank signal (`0.133354` vs action `-0.358750`), but the magnitude is too weak for promotion.
- Joint-health classification is not independently solved by human context.
- Revised bottleneck: human context helps choose which placement mode/source neighborhood is plausible, while action geometry still controls health inside a mode. The next generator should be mode-specialized, not a universal human-score multiplier.
- No submission is created. A future candidate needs a direct action generator whose predicted health beats row/subject/dateblock controls, not only a high identity score.

## Outputs

- `analysis_outputs/e317_human_placement_outcome_metrics.csv`
- `analysis_outputs/e317_human_placement_outcome_mode_holdout.csv`
- `analysis_outputs/e317_human_placement_outcome_within_mode.csv`
- `analysis_outputs/e317_human_placement_outcome_source_readout.csv`
- `analysis_outputs/e317_human_placement_outcome_summary.csv`
- `analysis_outputs/e317_human_placement_outcome_top_features.csv`
- `analysis_outputs/e317_human_placement_outcome_report.md`
