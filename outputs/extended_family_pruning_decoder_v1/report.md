# Extended Family Pruning Decoder

This experiment tests feature-family combinations beyond one-family-only/drop ablations.

## Best Recipes

| recipe | feature_count | best_candidate | best_avg_log_loss |
| --- | --- | --- | --- |
| drop_ratio_temporal_delta | 520 | prior_logit_blend_hgb_w20 | 0.624650 |
| drop_ratio_rank | 520 | prior_logit_blend_logreg_w03 | 0.626089 |
| only_rhythm_deviation | 520 | prior_logit_blend_state_mean_w10 | 0.626225 |
| drop_late_rank | 520 | prior_logit_blend_state_mean_w10 | 0.626233 |
| only_deviation_cross_modal | 520 | prior_logit_blend_residual_ridge_w03 | 0.626395 |
| only_rhythm_missingness | 520 | prior_logit_blend_logreg_w03 | 0.626632 |
| only_rhythm_cross_modal | 520 | prior_logit_blend_state_mean_w10 | 0.626956 |
| drop_raw_rank | 520 | prior_logit_blend_residual_ridge_w03 | 0.627005 |
| drop_missingness_ratio | 520 | prior_logit_blend_hgb_w10 | 0.627029 |
| drop_raw_ratio | 520 | prior_logit_blend_state_mean_w05 | 0.627061 |
| only_missingness_cross_modal | 520 | prior_logit_blend_logreg_w03 | 0.627079 |
| only_rhythm_deviation_cross_modal | 520 | prior_logit_blend_state_mean_w05 | 0.627080 |
| drop_sleep_late | 520 | prior_logit_blend_hgb_w10 | 0.627100 |
| only_state_core | 520 | prior_logit_blend_residual_ridge_w03 | 0.627286 |
| drop_gps_phone | 520 | prior_logit_blend_prototype_w05 | 0.627341 |
| only_rhythm_deviation_missingness | 520 | prior_logit_blend_state_mean_w03 | 0.627352 |

## Best Candidates

| preset | candidate | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drop_ratio_temporal_delta | prior_logit_blend_hgb_w20 | 0.624650 | 0.666330 | 0.697540 | 0.673976 | 0.575938 | 0.579571 | 0.534513 | 0.644679 |
| drop_ratio_temporal_delta | prior_logit_blend_hgb_w10 | 0.625408 | 0.668850 | 0.699598 | 0.674688 | 0.575411 | 0.579184 | 0.534753 | 0.645369 |
| drop_ratio_temporal_delta | prior_logit_blend_hgb_w35 | 0.625881 | 0.664980 | 0.697261 | 0.675017 | 0.578501 | 0.582571 | 0.536647 | 0.646192 |
| drop_ratio_rank | prior_logit_blend_logreg_w03 | 0.626089 | 0.671074 | 0.701163 | 0.671040 | 0.575479 | 0.581551 | 0.536660 | 0.645655 |
| drop_ratio_temporal_delta | prior_logit_blend_state_mean_w10 | 0.626180 | 0.670992 | 0.701182 | 0.675485 | 0.574258 | 0.579425 | 0.537434 | 0.644481 |
| only_rhythm_deviation | prior_logit_blend_state_mean_w10 | 0.626225 | 0.671729 | 0.698307 | 0.675202 | 0.574090 | 0.579794 | 0.539892 | 0.644560 |
| drop_late_rank | prior_logit_blend_state_mean_w10 | 0.626233 | 0.670553 | 0.700359 | 0.674839 | 0.573440 | 0.582006 | 0.539289 | 0.643145 |
| drop_ratio_temporal_delta | prior_logit_blend_hgb_w05 | 0.626256 | 0.670593 | 0.701185 | 0.675466 | 0.575499 | 0.579471 | 0.535360 | 0.646215 |
| drop_ratio_rank | prior_logit_blend_hgb_w10 | 0.626263 | 0.671016 | 0.701592 | 0.674036 | 0.576657 | 0.579146 | 0.538488 | 0.642908 |
| drop_ratio_rank | prior_logit_blend_hgb_w20 | 0.626345 | 0.670539 | 0.701315 | 0.672830 | 0.578877 | 0.579233 | 0.541958 | 0.639664 |
| drop_late_rank | prior_logit_blend_residual_ridge_w03 | 0.626362 | 0.670526 | 0.703227 | 0.675192 | 0.572502 | 0.580351 | 0.538361 | 0.644376 |
| drop_ratio_rank | prior_logit_blend_logreg_w05 | 0.626366 | 0.671110 | 0.701044 | 0.668581 | 0.576395 | 0.583664 | 0.538000 | 0.645769 |
| only_deviation_cross_modal | prior_logit_blend_residual_ridge_w03 | 0.626395 | 0.674840 | 0.700860 | 0.679470 | 0.571231 | 0.577054 | 0.539789 | 0.641524 |
| only_rhythm_deviation | prior_logit_blend_logreg_w03 | 0.626420 | 0.674400 | 0.702145 | 0.674284 | 0.574691 | 0.577832 | 0.538965 | 0.642626 |
| drop_late_rank | prior_logit_blend_logreg_w03 | 0.626442 | 0.671107 | 0.701904 | 0.673321 | 0.572821 | 0.582631 | 0.537934 | 0.645376 |
| drop_ratio_temporal_delta | prior_logit_blend_state_mean_w20 | 0.626472 | 0.670942 | 0.701050 | 0.675898 | 0.573975 | 0.580340 | 0.539761 | 0.643335 |
| drop_ratio_rank | prior_logit_blend_state_mean_w10 | 0.626597 | 0.672292 | 0.699249 | 0.671752 | 0.575867 | 0.580596 | 0.540860 | 0.645561 |
| only_rhythm_deviation | prior_logit_blend_state_mean_w05 | 0.626602 | 0.672004 | 0.700467 | 0.675657 | 0.574778 | 0.579702 | 0.537889 | 0.645714 |
| drop_ratio_temporal_delta | prior_logit_blend_state_mean_w05 | 0.626608 | 0.671623 | 0.701935 | 0.675824 | 0.574882 | 0.579560 | 0.536714 | 0.645718 |
| drop_late_rank | prior_logit_blend_state_mean_w05 | 0.626623 | 0.671404 | 0.701538 | 0.675483 | 0.574450 | 0.580824 | 0.537600 | 0.645065 |
| only_rhythm_missingness | prior_logit_blend_logreg_w03 | 0.626632 | 0.672744 | 0.703374 | 0.675723 | 0.573650 | 0.580470 | 0.537723 | 0.642737 |
| drop_late_rank | prior_logit_blend_state_mean_w20 | 0.626662 | 0.670064 | 0.699281 | 0.674743 | 0.572506 | 0.585690 | 0.543818 | 0.640535 |
| drop_ratio_temporal_delta | prior_logit_blend_hgb_w03 | 0.626682 | 0.671379 | 0.701923 | 0.675855 | 0.575600 | 0.579676 | 0.535692 | 0.646646 |
| drop_ratio_rank | prior_logit_blend_hgb_w05 | 0.626686 | 0.671691 | 0.702208 | 0.675119 | 0.576067 | 0.579486 | 0.537231 | 0.644996 |
| drop_ratio_rank | prior_logit_blend_state_mean_w05 | 0.626790 | 0.672266 | 0.700948 | 0.673935 | 0.575655 | 0.580129 | 0.538357 | 0.646242 |
| only_rhythm_deviation | prior_logit_blend_state_mean_w20 | 0.626797 | 0.672317 | 0.695550 | 0.675534 | 0.573793 | 0.581412 | 0.545120 | 0.643851 |
| only_rhythm_deviation | prior_logit_blend_state_mean_w03 | 0.626874 | 0.672220 | 0.701475 | 0.675954 | 0.575152 | 0.579797 | 0.537200 | 0.646322 |
| only_deviation_cross_modal | prior_logit_blend_state_mean_w10 | 0.626880 | 0.673478 | 0.699426 | 0.676005 | 0.575944 | 0.580115 | 0.540426 | 0.642769 |
| drop_late_rank | prior_logit_blend_logreg_w05 | 0.626885 | 0.671141 | 0.702210 | 0.672392 | 0.571850 | 0.585434 | 0.540017 | 0.645150 |
| drop_ratio_temporal_delta | prior_logit_blend_state_mean_w03 | 0.626885 | 0.671988 | 0.702363 | 0.676060 | 0.575220 | 0.579721 | 0.536508 | 0.646335 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | drop_ratio_temporal_delta__prior_logit_blend_hgb_w35 | 0.664980 | 0.616766 |
| Q2 | drop_raw_ratio__prior_logit_blend_hgb_w35 | 0.689098 | 0.616766 |
| Q3 | drop_sleep_late__prior_logit_blend_hgb_w35 | 0.665606 | 0.616766 |
| S1 | drop_raw_rank__prior_logit_blend_residual_ridge_w10 | 0.565500 | 0.616766 |
| S2 | only_rhythm_deviation_cross_modal__prior_logit_blend_residual_ridge_w05 | 0.572205 | 0.616766 |
| S3 | drop_ratio_temporal_delta__prior_logit_blend_hgb_w20 | 0.534513 | 0.616766 |
| S4 | only_missingness_cross_modal__prior_logit_blend_rank_pairwise_w10 | 0.625461 | 0.616766 |

## Summary

- Best global: `drop_ratio_temporal_delta__prior_logit_blend_hgb_w20` avg `0.624650`
- Target-wise avg: `0.616766`
- Best global drift vs reference: `0.066941`
- Target-wise drift vs reference: `0.068461`
