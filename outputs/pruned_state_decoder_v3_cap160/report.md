# Pruned State Decoder

This experiment treats v83 only as a diagnostic reference. Predictions are built from pruned encoder input families plus state decoders.

## Best Presets

| preset | feature_count | best_candidate | best_avg_log_loss |
| --- | --- | --- | --- |
| only_cross_modal | 160 | prior_logit_blend_logreg_w03 | 0.626764 |
| no_temporal_delta | 160 | prior_logit_blend_hgb_w10 | 0.626831 |
| only_missingness | 160 | prior_logit_blend_state_mean_w05 | 0.627294 |
| no_missingness | 160 | prior_logit_blend_prototype_w03 | 0.627363 |
| no_late_pool | 160 | prior_logit_blend_prototype_w03 | 0.627368 |
| no_sleep | 160 | prior_logit_blend_prototype_w03 | 0.627368 |
| only_deviation | 160 | prior_logit_blend_prototype_w03 | 0.627369 |
| only_rhythm | 160 | prior_logit_blend_prototype_w03 | 0.627373 |
| no_derivative | 160 | prior_logit_blend_prototype_w03 | 0.627373 |
| no_gps | 160 | prior_logit_blend_prototype_w03 | 0.627375 |
| no_raw | 160 | prior_logit_blend_prototype_w03 | 0.627379 |
| no_phone | 160 | prior_logit_blend_prototype_w03 | 0.627380 |
| no_ratio | 160 | prior_logit_blend_prototype_w03 | 0.627386 |
| full | 160 | prior_logit_blend_prototype_w03 | 0.627386 |
| no_rank | 160 | prior_logit_blend_prototype_w03 | 0.627386 |

## Best Candidates

| preset | candidate | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal | prior_logit_blend_logreg_w03 | 0.626764 | 0.672881 | 0.701697 | 0.673425 | 0.575149 | 0.580968 | 0.538798 | 0.644433 |
| no_temporal_delta | prior_logit_blend_hgb_w10 | 0.626831 | 0.670622 | 0.702336 | 0.673167 | 0.574723 | 0.581520 | 0.540127 | 0.645322 |
| no_temporal_delta | prior_logit_blend_hgb_w05 | 0.626969 | 0.671510 | 0.702595 | 0.674691 | 0.575129 | 0.580645 | 0.538033 | 0.646183 |
| no_temporal_delta | prior_logit_blend_hgb_w03 | 0.627110 | 0.671937 | 0.702779 | 0.675387 | 0.575371 | 0.580381 | 0.537293 | 0.646625 |
| only_cross_modal | prior_logit_blend_residual_ridge_w03 | 0.627264 | 0.672938 | 0.702198 | 0.676821 | 0.573159 | 0.580969 | 0.540782 | 0.643984 |
| only_cross_modal | prior_logit_blend_state_mean_w05 | 0.627283 | 0.672484 | 0.702290 | 0.675228 | 0.575389 | 0.581519 | 0.538780 | 0.645293 |
| only_cross_modal | prior_logit_blend_state_mean_w03 | 0.627293 | 0.672512 | 0.702584 | 0.675705 | 0.575524 | 0.580900 | 0.537740 | 0.646087 |
| only_missingness | prior_logit_blend_state_mean_w05 | 0.627294 | 0.671333 | 0.702922 | 0.674837 | 0.576765 | 0.581462 | 0.536881 | 0.646862 |
| only_cross_modal | prior_logit_blend_logreg_w05 | 0.627302 | 0.673905 | 0.701625 | 0.672367 | 0.575641 | 0.582606 | 0.541404 | 0.643568 |
| only_missingness | prior_logit_blend_state_mean_w03 | 0.627304 | 0.671820 | 0.702973 | 0.675471 | 0.576346 | 0.580875 | 0.536611 | 0.647036 |
| only_cross_modal | prior_logit_blend_hgb_w03 | 0.627331 | 0.672394 | 0.703328 | 0.676237 | 0.575092 | 0.581001 | 0.537614 | 0.645650 |
| only_missingness | prior_logit_blend_hgb_w03 | 0.627340 | 0.672250 | 0.702786 | 0.675773 | 0.575925 | 0.580509 | 0.536829 | 0.647311 |
| only_cross_modal | prior_logit_blend_hgb_w05 | 0.627342 | 0.672284 | 0.703524 | 0.676114 | 0.574667 | 0.581671 | 0.538575 | 0.644556 |
| no_temporal_delta | prior_logit_blend_prototype_w05 | 0.627348 | 0.672149 | 0.701667 | 0.675349 | 0.576245 | 0.580736 | 0.537860 | 0.647431 |
| no_temporal_delta | prior_logit_blend_prototype_w03 | 0.627351 | 0.672334 | 0.702240 | 0.675805 | 0.576051 | 0.580442 | 0.537191 | 0.647394 |
| no_temporal_delta | prior_logit_blend_state_mean_w03 | 0.627355 | 0.672854 | 0.702848 | 0.676363 | 0.575757 | 0.580037 | 0.537449 | 0.646179 |
| only_missingness | prior_logit_blend_hgb_w05 | 0.627357 | 0.672046 | 0.702614 | 0.675336 | 0.576067 | 0.580853 | 0.537258 | 0.647324 |
| only_cross_modal | prior_logit_blend_prototype_w03 | 0.627360 | 0.672322 | 0.702222 | 0.675797 | 0.576093 | 0.580444 | 0.537224 | 0.647417 |
| no_missingness | prior_logit_blend_prototype_w03 | 0.627363 | 0.672366 | 0.702184 | 0.675839 | 0.576083 | 0.580433 | 0.537158 | 0.647477 |
| only_cross_modal | prior_logit_blend_prototype_w05 | 0.627363 | 0.672130 | 0.701637 | 0.675335 | 0.576316 | 0.580740 | 0.537915 | 0.647469 |
| no_late_pool | prior_logit_blend_prototype_w03 | 0.627368 | 0.672343 | 0.702249 | 0.675858 | 0.576077 | 0.580417 | 0.537208 | 0.647422 |
| no_sleep | prior_logit_blend_prototype_w03 | 0.627368 | 0.672344 | 0.702220 | 0.675843 | 0.576134 | 0.580424 | 0.537176 | 0.647436 |
| no_missingness | prior_logit_blend_prototype_w05 | 0.627368 | 0.672203 | 0.701573 | 0.675407 | 0.576299 | 0.580721 | 0.537805 | 0.647569 |
| only_deviation | prior_logit_blend_prototype_w03 | 0.627369 | 0.672323 | 0.702236 | 0.675835 | 0.576081 | 0.580471 | 0.537187 | 0.647450 |
| only_rhythm | prior_logit_blend_prototype_w03 | 0.627373 | 0.672346 | 0.702260 | 0.675850 | 0.576112 | 0.580419 | 0.537171 | 0.647454 |
| no_derivative | prior_logit_blend_prototype_w03 | 0.627373 | 0.672363 | 0.702206 | 0.675826 | 0.576111 | 0.580455 | 0.537243 | 0.647407 |
| no_temporal_delta | prior_logit_blend_state_mean_w05 | 0.627374 | 0.673041 | 0.702710 | 0.676311 | 0.575765 | 0.580066 | 0.538289 | 0.645437 |
| no_gps | prior_logit_blend_prototype_w03 | 0.627375 | 0.672316 | 0.702248 | 0.675847 | 0.576104 | 0.580430 | 0.537208 | 0.647472 |
| no_late_pool | prior_logit_blend_prototype_w05 | 0.627376 | 0.672165 | 0.701681 | 0.675437 | 0.576289 | 0.580694 | 0.537888 | 0.647477 |
| only_rhythm | prior_logit_blend_state_mean_w03 | 0.627376 | 0.672913 | 0.701432 | 0.676743 | 0.575768 | 0.580175 | 0.537868 | 0.646735 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | only_missingness__prior_logit_blend_state_mean_w20 | 0.669509 | 0.619789 |
| Q2 | only_rhythm__prior_logit_blend_state_mean_w35 | 0.689990 | 0.619789 |
| Q3 | no_late_pool__prior_logit_blend_state_mean_w35 | 0.662253 | 0.619789 |
| S1 | only_cross_modal__prior_logit_blend_residual_ridge_w05 | 0.572599 | 0.619789 |
| S2 | full__prior_logit_blend_rank_pairwise_w05 | 0.576515 | 0.619789 |
| S3 | only_missingness__prior_logit_blend_residual_ridge_w05 | 0.533026 | 0.619789 |
| S4 | only_cross_modal__prior_logit_blend_hgb_w35 | 0.634631 | 0.619789 |

## Summary

- Best global: `only_cross_modal__prior_logit_blend_logreg_w03` avg `0.626764`
- Target-wise avg: `0.619789`
- Best global drift vs reference: `0.064171`
- Target-wise drift vs reference: `0.068343`
