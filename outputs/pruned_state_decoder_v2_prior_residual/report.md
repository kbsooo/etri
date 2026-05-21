# Pruned State Decoder

This experiment treats v83 only as a diagnostic reference. Predictions are built from pruned encoder input families plus state decoders.

## Best Presets

| preset | feature_count | best_candidate | best_avg_log_loss |
| --- | --- | --- | --- |
| only_rhythm | 520 | prior_logit_blend_hgb_w20 | 0.625801 |
| no_derivative | 520 | prior_logit_blend_hgb_w10 | 0.626284 |
| no_ratio | 520 | prior_logit_blend_residual_ridge_w03 | 0.626331 |
| no_temporal_delta | 520 | prior_logit_blend_hgb_w10 | 0.626364 |
| only_cross_modal | 520 | prior_logit_blend_hgb_w10 | 0.626521 |
| no_missingness | 520 | prior_logit_blend_residual_ridge_w03 | 0.626711 |
| no_rank | 520 | prior_logit_blend_hgb_w10 | 0.626732 |
| full | 520 | prior_logit_blend_hgb_w10 | 0.626748 |
| no_raw | 520 | prior_logit_blend_hgb_w10 | 0.626798 |
| only_deviation | 520 | prior_logit_blend_hgb_w10 | 0.626852 |
| only_missingness | 520 | prior_logit_blend_hgb_w10 | 0.626924 |
| no_sleep | 520 | prior_logit_blend_hgb_w10 | 0.627100 |
| no_gps | 520 | prior_logit_blend_hgb_w05 | 0.627132 |
| no_late_pool | 520 | prior_logit_blend_hgb_w05 | 0.627269 |
| no_phone | 520 | prior_logit_blend_hgb_w05 | 0.627311 |

## Best Candidates

| preset | candidate | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm | prior_logit_blend_hgb_w20 | 0.625801 | 0.670652 | 0.693460 | 0.675440 | 0.572511 | 0.583591 | 0.538852 | 0.646104 |
| only_rhythm | prior_logit_blend_hgb_w10 | 0.625964 | 0.671112 | 0.697697 | 0.675232 | 0.573588 | 0.581122 | 0.536904 | 0.646093 |
| only_rhythm | prior_logit_blend_state_mean_w10 | 0.626207 | 0.671074 | 0.699205 | 0.673459 | 0.572249 | 0.580201 | 0.539519 | 0.647743 |
| no_derivative | prior_logit_blend_hgb_w10 | 0.626284 | 0.671218 | 0.700275 | 0.675458 | 0.574656 | 0.579674 | 0.538112 | 0.644596 |
| no_derivative | prior_logit_blend_hgb_w20 | 0.626321 | 0.670779 | 0.698813 | 0.675431 | 0.574491 | 0.580409 | 0.541102 | 0.643219 |
| no_ratio | prior_logit_blend_residual_ridge_w03 | 0.626331 | 0.671261 | 0.697588 | 0.677570 | 0.578272 | 0.580022 | 0.535813 | 0.643794 |
| no_temporal_delta | prior_logit_blend_hgb_w10 | 0.626364 | 0.669950 | 0.699982 | 0.675493 | 0.576604 | 0.581105 | 0.537953 | 0.643459 |
| no_temporal_delta | prior_logit_blend_state_mean_w10 | 0.626429 | 0.672572 | 0.698705 | 0.675593 | 0.573696 | 0.581718 | 0.539428 | 0.643291 |
| only_cross_modal | prior_logit_blend_hgb_w10 | 0.626521 | 0.671302 | 0.702535 | 0.676685 | 0.574871 | 0.581663 | 0.535680 | 0.642911 |
| only_rhythm | prior_logit_blend_hgb_w05 | 0.626529 | 0.671750 | 0.700269 | 0.675691 | 0.574560 | 0.580424 | 0.536431 | 0.646580 |
| only_rhythm | prior_logit_blend_state_mean_w05 | 0.626586 | 0.671659 | 0.700930 | 0.674756 | 0.573846 | 0.579910 | 0.537686 | 0.647315 |
| no_ratio | prior_logit_blend_state_mean_w10 | 0.626630 | 0.671239 | 0.695730 | 0.675908 | 0.576916 | 0.581135 | 0.539476 | 0.646003 |
| no_temporal_delta | prior_logit_blend_hgb_w20 | 0.626651 | 0.668442 | 0.698472 | 0.675813 | 0.578595 | 0.583459 | 0.540939 | 0.640842 |
| no_derivative | prior_logit_blend_state_mean_w10 | 0.626691 | 0.672486 | 0.699604 | 0.676033 | 0.576203 | 0.579649 | 0.538296 | 0.644563 |
| no_derivative | prior_logit_blend_hgb_w05 | 0.626704 | 0.671813 | 0.701534 | 0.675861 | 0.575113 | 0.579735 | 0.537055 | 0.645818 |
| no_missingness | prior_logit_blend_residual_ridge_w03 | 0.626711 | 0.670680 | 0.701008 | 0.681608 | 0.576004 | 0.577284 | 0.536290 | 0.644106 |
| no_temporal_delta | prior_logit_blend_hgb_w05 | 0.626723 | 0.671155 | 0.701356 | 0.675840 | 0.576062 | 0.580428 | 0.536955 | 0.645262 |
| no_temporal_delta | prior_logit_blend_state_mean_w05 | 0.626724 | 0.672416 | 0.700673 | 0.675850 | 0.574575 | 0.580727 | 0.537697 | 0.645129 |
| no_rank | prior_logit_blend_hgb_w10 | 0.626732 | 0.673047 | 0.699324 | 0.673297 | 0.576867 | 0.583588 | 0.539570 | 0.641429 |
| full | prior_logit_blend_hgb_w10 | 0.626748 | 0.671501 | 0.702016 | 0.673790 | 0.574817 | 0.583141 | 0.538311 | 0.643658 |
| no_raw | prior_logit_blend_hgb_w10 | 0.626798 | 0.669778 | 0.700710 | 0.675665 | 0.574788 | 0.585148 | 0.538187 | 0.643311 |
| no_ratio | prior_logit_blend_state_mean_w05 | 0.626811 | 0.671733 | 0.699192 | 0.676011 | 0.576204 | 0.580407 | 0.537683 | 0.646449 |
| only_cross_modal | prior_logit_blend_hgb_w05 | 0.626813 | 0.671826 | 0.702669 | 0.676449 | 0.575194 | 0.580742 | 0.535825 | 0.644983 |
| only_rhythm | prior_logit_blend_state_mean_w20 | 0.626818 | 0.671146 | 0.697235 | 0.672281 | 0.570205 | 0.582193 | 0.544525 | 0.650141 |
| only_rhythm | prior_logit_blend_hgb_w03 | 0.626845 | 0.672080 | 0.701381 | 0.675979 | 0.575030 | 0.580244 | 0.536334 | 0.646866 |
| only_deviation | prior_logit_blend_hgb_w10 | 0.626852 | 0.674629 | 0.700995 | 0.673725 | 0.575965 | 0.578783 | 0.538535 | 0.645334 |
| no_derivative | prior_logit_blend_state_mean_w05 | 0.626853 | 0.672397 | 0.701140 | 0.676105 | 0.575842 | 0.579673 | 0.537098 | 0.645719 |
| no_ratio | prior_logit_blend_logreg_w03 | 0.626855 | 0.672127 | 0.697864 | 0.676474 | 0.577327 | 0.580143 | 0.540970 | 0.643082 |
| no_missingness | prior_logit_blend_state_mean_w10 | 0.626856 | 0.670706 | 0.697962 | 0.675950 | 0.578400 | 0.581381 | 0.539652 | 0.643937 |
| only_rhythm | prior_logit_blend_state_mean_w03 | 0.626863 | 0.672009 | 0.701756 | 0.675407 | 0.574591 | 0.579922 | 0.537074 | 0.647286 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | only_missingness__prior_logit_blend_logreg_w10 | 0.664662 | 0.617441 |
| Q2 | no_ratio__prior_logit_blend_state_mean_w35 | 0.685805 | 0.617441 |
| Q3 | no_sleep__prior_logit_blend_hgb_w35 | 0.665606 | 0.617441 |
| S1 | only_rhythm__prior_logit_blend_rank_pairwise_w05 | 0.567031 | 0.617441 |
| S2 | no_missingness__prior_logit_blend_residual_ridge_w05 | 0.577195 | 0.617441 |
| S3 | only_missingness__prior_logit_blend_rank_pairwise_w05 | 0.529217 | 0.617441 |
| S4 | no_rank__prior_logit_blend_hgb_w35 | 0.632572 | 0.617441 |

## Summary

- Best global: `only_rhythm__prior_logit_blend_hgb_w20` avg `0.625801`
- Target-wise avg: `0.617441`
- Best global drift vs reference: `0.068234`
- Target-wise drift vs reference: `0.067860`
