# Family Label-State Decoder

This experiment splits the sparse 7-label state bottleneck into Q-family and S-family intermediate states. Each family is decoded separately from the same feature-pruned state latent, recombined into seven probabilities, then blended with a fold-safe subject prior.

## Best Sources

| source | preset | q_decoder | s_decoder | weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drop_ratio_temporal_delta__family_q_pattern_s_pattern_w10 | drop_ratio_temporal_delta | q_pattern | s_pattern | 0.100000 | 0.626385 | 0.670886 | 0.699637 | 0.673089 | 0.576277 | 0.580099 | 0.539013 | 0.645691 |
| only_rhythm__family_q_knn25_s_knn25_w10 | only_rhythm | q_knn25 | s_knn25 | 0.100000 | 0.626497 | 0.669490 | 0.698141 | 0.673661 | 0.574945 | 0.581340 | 0.539067 | 0.648833 |
| no_ratio__family_q_knn25_s_knn25_w10 | no_ratio | q_knn25 | s_knn25 | 0.100000 | 0.626571 | 0.672357 | 0.698697 | 0.675142 | 0.575504 | 0.579686 | 0.538318 | 0.646294 |
| drop_ratio_temporal_delta__family_q_pattern_s_cluster8_w10 | drop_ratio_temporal_delta | q_pattern | s_cluster8 | 0.100000 | 0.626612 | 0.670886 | 0.699637 | 0.673089 | 0.576075 | 0.581846 | 0.538469 | 0.646279 |
| no_temporal_delta__family_q_knn25_s_knn25_w10 | no_temporal_delta | q_knn25 | s_knn25 | 0.100000 | 0.626619 | 0.670823 | 0.698651 | 0.674486 | 0.575910 | 0.581122 | 0.539594 | 0.645747 |
| drop_ratio_temporal_delta__family_q_pattern_s_pattern_w05 | drop_ratio_temporal_delta | q_pattern | s_pattern | 0.050000 | 0.626630 | 0.671438 | 0.701005 | 0.674468 | 0.575866 | 0.579871 | 0.537455 | 0.646304 |
| only_rhythm__family_q_knn25_s_knn25_w20 | only_rhythm | q_knn25 | s_knn25 | 0.200000 | 0.626681 | 0.667346 | 0.693950 | 0.671589 | 0.575104 | 0.583985 | 0.543535 | 0.651254 |
| drop_ratio_temporal_delta__family_q_pattern_s_cluster8_w05 | drop_ratio_temporal_delta | q_pattern | s_cluster8 | 0.050000 | 0.626732 | 0.671438 | 0.701005 | 0.674468 | 0.575730 | 0.580745 | 0.537183 | 0.646556 |
| no_ratio__family_q_knn25_s_knn25_w20 | no_ratio | q_knn25 | s_knn25 | 0.200000 | 0.626740 | 0.673055 | 0.695224 | 0.674527 | 0.576098 | 0.580425 | 0.541546 | 0.646301 |
| only_rhythm__family_q_knn25_s_knn25_w05 | only_rhythm | q_knn25 | s_knn25 | 0.050000 | 0.626818 | 0.670947 | 0.700541 | 0.674993 | 0.575255 | 0.580539 | 0.537461 | 0.647991 |
| drop_ratio_temporal_delta__family_q_state_mean_s_state_mean_w10 | drop_ratio_temporal_delta | q_state_mean | s_state_mean | 0.100000 | 0.626838 | 0.671831 | 0.699516 | 0.673326 | 0.575944 | 0.581724 | 0.539208 | 0.646316 |
| no_ratio__family_q_knn25_s_knn25_w05 | no_ratio | q_knn25 | s_knn25 | 0.050000 | 0.626868 | 0.672384 | 0.700798 | 0.675737 | 0.575550 | 0.579743 | 0.537156 | 0.646707 |
| no_temporal_delta__family_q_knn25_s_knn25_w05 | no_temporal_delta | q_knn25 | s_knn25 | 0.050000 | 0.626883 | 0.671623 | 0.700764 | 0.675406 | 0.575715 | 0.580443 | 0.537793 | 0.646436 |
| no_ratio__family_q_state_mean_s_state_mean_w10 | no_ratio | q_state_mean | s_state_mean | 0.100000 | 0.626888 | 0.672272 | 0.697091 | 0.675874 | 0.576926 | 0.580692 | 0.539728 | 0.645632 |
| drop_ratio_temporal_delta__family_q_cluster4_s_pattern_w05 | drop_ratio_temporal_delta | q_cluster4 | s_pattern | 0.050000 | 0.626899 | 0.672875 | 0.701685 | 0.674234 | 0.575866 | 0.579871 | 0.537455 | 0.646304 |
| no_temporal_delta__family_q_knn25_s_knn25_w20 | no_temporal_delta | q_knn25 | s_knn25 | 0.200000 | 0.626904 | 0.669934 | 0.695220 | 0.673242 | 0.577208 | 0.583434 | 0.544104 | 0.645183 |
| drop_ratio_temporal_delta__family_q_cluster4_s_pattern_w10 | drop_ratio_temporal_delta | q_cluster4 | s_pattern | 0.100000 | 0.626912 | 0.673883 | 0.701174 | 0.672249 | 0.576277 | 0.580099 | 0.539013 | 0.645691 |
| no_temporal_delta__family_q_state_mean_s_state_mean_w10 | no_temporal_delta | q_state_mean | s_state_mean | 0.100000 | 0.626934 | 0.673344 | 0.697626 | 0.674893 | 0.574372 | 0.581623 | 0.540329 | 0.646350 |
| no_ratio__family_q_cluster4_s_pattern_w05 | no_ratio | q_cluster4 | s_pattern | 0.050000 | 0.626954 | 0.672546 | 0.699353 | 0.676021 | 0.576096 | 0.580052 | 0.538208 | 0.646401 |
| only_rhythm__family_q_state_mean_s_state_mean_w10 | only_rhythm | q_state_mean | s_state_mean | 0.100000 | 0.626961 | 0.672068 | 0.698367 | 0.672421 | 0.575988 | 0.582014 | 0.539668 | 0.648199 |
| no_ratio__family_q_state_mean_s_state_mean_w05 | no_ratio | q_state_mean | s_state_mean | 0.050000 | 0.626986 | 0.672293 | 0.699930 | 0.676104 | 0.576223 | 0.580216 | 0.537823 | 0.646312 |
| drop_ratio_temporal_delta__family_q_state_mean_s_state_mean_w05 | drop_ratio_temporal_delta | q_state_mean | s_state_mean | 0.050000 | 0.626988 | 0.672095 | 0.701143 | 0.674819 | 0.575766 | 0.580769 | 0.537611 | 0.646714 |
| only_rhythm__family_q_state_mean_s_state_mean_w05 | only_rhythm | q_state_mean | s_state_mean | 0.050000 | 0.626998 | 0.672203 | 0.700552 | 0.674372 | 0.575734 | 0.580812 | 0.537744 | 0.647568 |
| drop_ratio_temporal_delta__family_q_cluster4_s_cluster8_w05 | drop_ratio_temporal_delta | q_cluster4 | s_cluster8 | 0.050000 | 0.627001 | 0.672875 | 0.701685 | 0.674234 | 0.575730 | 0.580745 | 0.537183 | 0.646556 |
| no_temporal_delta__family_q_state_mean_s_state_mean_w05 | no_temporal_delta | q_state_mean | s_state_mean | 0.050000 | 0.627002 | 0.672838 | 0.700181 | 0.675600 | 0.574932 | 0.580665 | 0.538113 | 0.646687 |
| only_rhythm__family_q_pattern_s_pattern_w05 | only_rhythm | q_pattern | s_pattern | 0.050000 | 0.627006 | 0.672486 | 0.700428 | 0.674031 | 0.575623 | 0.581187 | 0.538143 | 0.647147 |
| no_temporal_delta__family_q_pattern_s_cluster8_w05 | no_temporal_delta | q_pattern | s_cluster8 | 0.050000 | 0.627024 | 0.672565 | 0.700521 | 0.675484 | 0.574646 | 0.580641 | 0.538396 | 0.646918 |
| only_missingness__family_q_cluster4_s_pattern_w05 | only_missingness | q_cluster4 | s_pattern | 0.050000 | 0.627030 | 0.669390 | 0.702429 | 0.675479 | 0.576750 | 0.581719 | 0.536697 | 0.646743 |
| no_ratio__family_q_cluster4_s_cluster8_w05 | no_ratio | q_cluster4 | s_cluster8 | 0.050000 | 0.627052 | 0.672546 | 0.699353 | 0.676021 | 0.576454 | 0.580628 | 0.538602 | 0.645758 |
| only_missingness__family_q_cluster4_s_cluster8_w05 | only_missingness | q_cluster4 | s_cluster8 | 0.050000 | 0.627065 | 0.669390 | 0.702429 | 0.675479 | 0.577238 | 0.581983 | 0.536585 | 0.646348 |

## Target-wise Selection

| target | family | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- | --- |
| Q1 | Q | only_missingness__family_q_cluster4_s_cluster6_w20 | 0.664445 | 0.621171 |
| Q2 | Q | no_ratio__family_q_state_mean_s_state_mean_w35 | 0.688544 | 0.621171 |
| Q3 | Q | only_rhythm__family_q_cluster4_s_cluster6_w35 | 0.662129 | 0.621171 |
| S1 | S | no_temporal_delta__family_q_cluster4_s_cluster6_w10 | 0.573445 | 0.621171 |
| S2 | S | no_ratio__family_q_knn25_s_knn25_w10 | 0.579686 | 0.621171 |
| S3 | S | only_missingness__family_q_cluster4_s_cluster8_w05 | 0.536585 | 0.621171 |
| S4 | S | no_sleep__family_q_state_mean_s_state_mean_w20 | 0.643365 | 0.621171 |

## Summary

- Best global: `drop_ratio_temporal_delta__family_q_pattern_s_pattern_w10` avg `0.626385`
- Target-wise avg: `0.621171`
- Best global drift vs reference: `0.065777`
- Target-wise drift vs reference: `0.070116`
- Q/S pattern counts by fold: `[{'fit_q_patterns': 8, 'fit_s_patterns': 15, 'fit_full_patterns': 87}, {'fit_q_patterns': 8, 'fit_s_patterns': 14, 'fit_full_patterns': 87}, {'fit_q_patterns': 8, 'fit_s_patterns': 15, 'fit_full_patterns': 90}, {'fit_q_patterns': 8, 'fit_s_patterns': 15, 'fit_full_patterns': 91}, {'fit_q_patterns': 8, 'fit_s_patterns': 14, 'fit_full_patterns': 90}]`
