# Residual State Objective Decoder

This experiment predicts logit residuals over subject-prior from state latents using residual prototypes, residual nearest-neighbor, and residual ridge objectives.

## Best Sources

| source | preset | decoder | weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_ratio__residual_ridge_w03 | no_ratio | residual_ridge | 0.030000 | 0.626331 | 0.671261 | 0.697588 | 0.677570 | 0.578272 | 0.580022 | 0.535813 | 0.643794 |
| only_deviation_cross_modal__residual_ridge_w03 | only_deviation_cross_modal | residual_ridge | 0.030000 | 0.626395 | 0.674840 | 0.700860 | 0.679470 | 0.571231 | 0.577054 | 0.539789 | 0.641524 |
| no_ratio__residual_mean_w05 | no_ratio | residual_mean | 0.050000 | 0.626461 | 0.671671 | 0.699884 | 0.676859 | 0.576783 | 0.579569 | 0.535618 | 0.644841 |
| no_ratio__residual_mean_w03 | no_ratio | residual_mean | 0.030000 | 0.626694 | 0.671911 | 0.701037 | 0.676570 | 0.576250 | 0.579634 | 0.535745 | 0.645711 |
| no_missingness__residual_ridge_w03 | no_missingness | residual_ridge | 0.030000 | 0.626711 | 0.670680 | 0.701008 | 0.681608 | 0.576004 | 0.577284 | 0.536290 | 0.644106 |
| no_ratio__residual_mean_w10 | no_ratio | residual_mean | 0.100000 | 0.626731 | 0.671962 | 0.697873 | 0.678467 | 0.578959 | 0.580203 | 0.536110 | 0.643542 |
| only_deviation_cross_modal__residual_mean_w05 | only_deviation_cross_modal | residual_mean | 0.050000 | 0.626771 | 0.674016 | 0.701892 | 0.678116 | 0.573250 | 0.578787 | 0.538353 | 0.642983 |
| no_temporal_delta__residual_knn_w10 | no_temporal_delta | residual_knn | 0.100000 | 0.626783 | 0.670688 | 0.702021 | 0.675547 | 0.575984 | 0.580854 | 0.537454 | 0.644933 |
| no_missingness__residual_mean_w05 | no_missingness | residual_mean | 0.050000 | 0.626801 | 0.671804 | 0.701562 | 0.678795 | 0.575980 | 0.578288 | 0.536294 | 0.644882 |
| no_temporal_delta__residual_knn_w05 | no_temporal_delta | residual_knn | 0.050000 | 0.626853 | 0.671505 | 0.702304 | 0.675803 | 0.575572 | 0.580185 | 0.536647 | 0.645956 |
| only_deviation_cross_modal__residual_mean_w03 | only_deviation_cross_modal | residual_mean | 0.030000 | 0.626870 | 0.673322 | 0.702210 | 0.677324 | 0.574111 | 0.579165 | 0.537381 | 0.644576 |
| no_missingness__residual_mean_w03 | no_missingness | residual_mean | 0.030000 | 0.626890 | 0.671988 | 0.702018 | 0.677717 | 0.575774 | 0.578852 | 0.536157 | 0.645721 |
| no_temporal_delta__residual_mean_w05 | no_temporal_delta | residual_mean | 0.050000 | 0.626952 | 0.672089 | 0.704159 | 0.676806 | 0.572101 | 0.581983 | 0.537379 | 0.644146 |
| no_temporal_delta__residual_mean_w03 | no_temporal_delta | residual_mean | 0.030000 | 0.626985 | 0.672173 | 0.703590 | 0.676538 | 0.573430 | 0.581073 | 0.536807 | 0.645284 |
| no_temporal_delta__residual_knn_w03 | no_temporal_delta | residual_knn | 0.030000 | 0.627018 | 0.671925 | 0.702572 | 0.676035 | 0.575591 | 0.580074 | 0.536448 | 0.646480 |
| no_ratio__residual_knn_w05 | no_ratio | residual_knn | 0.050000 | 0.627065 | 0.672834 | 0.702451 | 0.676752 | 0.575382 | 0.579332 | 0.536023 | 0.646679 |
| drop_ratio_temporal_delta__residual_mean_w03 | drop_ratio_temporal_delta | residual_mean | 0.030000 | 0.627146 | 0.672377 | 0.703721 | 0.677340 | 0.575645 | 0.579769 | 0.536524 | 0.644647 |
| no_ratio__residual_knn_w03 | no_ratio | residual_knn | 0.030000 | 0.627151 | 0.672717 | 0.702667 | 0.676605 | 0.575501 | 0.579577 | 0.536075 | 0.646913 |
| no_ratio__residual_knn_w10 | no_ratio | residual_knn | 0.100000 | 0.627156 | 0.673390 | 0.702251 | 0.677437 | 0.575409 | 0.579021 | 0.536195 | 0.646391 |
| drop_ratio_temporal_delta__residual_mean_w05 | drop_ratio_temporal_delta | residual_mean | 0.050000 | 0.627195 | 0.672416 | 0.704343 | 0.678128 | 0.575743 | 0.579774 | 0.536898 | 0.643059 |
| only_rhythm__residual_knn_w05 | only_rhythm | residual_knn | 0.050000 | 0.627243 | 0.672069 | 0.702576 | 0.675664 | 0.574762 | 0.580245 | 0.536390 | 0.648994 |
| drop_ratio_temporal_delta__residual_knn_w05 | drop_ratio_temporal_delta | residual_knn | 0.050000 | 0.627252 | 0.672163 | 0.703701 | 0.676159 | 0.575669 | 0.580544 | 0.536909 | 0.645620 |
| only_rhythm__residual_knn_w03 | only_rhythm | residual_knn | 0.030000 | 0.627261 | 0.672250 | 0.702759 | 0.675959 | 0.575122 | 0.580123 | 0.536309 | 0.648306 |
| drop_ratio_temporal_delta__residual_knn_w03 | drop_ratio_temporal_delta | residual_knn | 0.030000 | 0.627263 | 0.672324 | 0.703414 | 0.676236 | 0.575675 | 0.580314 | 0.536598 | 0.646282 |
| only_rhythm_deviation_cross_modal__residual_mean_w03 | only_rhythm_deviation_cross_modal | residual_mean | 0.030000 | 0.627306 | 0.673422 | 0.704362 | 0.678176 | 0.575528 | 0.577790 | 0.536869 | 0.644996 |
| no_temporal_delta__residual_ridge_w03 | no_temporal_delta | residual_ridge | 0.030000 | 0.627317 | 0.672812 | 0.705277 | 0.678057 | 0.569685 | 0.583786 | 0.538469 | 0.643135 |
| no_ratio__residual_ridge_w05 | no_ratio | residual_ridge | 0.050000 | 0.627389 | 0.672261 | 0.695709 | 0.680108 | 0.581588 | 0.581630 | 0.537129 | 0.643297 |
| no_missingness__residual_knn_w03 | no_missingness | residual_knn | 0.030000 | 0.627415 | 0.673603 | 0.702420 | 0.676068 | 0.576277 | 0.580123 | 0.536556 | 0.646862 |
| only_rhythm_deviation_cross_modal__residual_knn_w03 | only_rhythm_deviation_cross_modal | residual_knn | 0.030000 | 0.627419 | 0.673304 | 0.703054 | 0.676651 | 0.575915 | 0.579837 | 0.536937 | 0.646236 |
| only_rhythm__residual_mean_w03 | only_rhythm | residual_mean | 0.030000 | 0.627430 | 0.673332 | 0.703870 | 0.675426 | 0.575318 | 0.579655 | 0.536590 | 0.647822 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | only_missingness__residual_ridge_w05 | 0.667048 | 0.620437 |
| Q2 | no_ratio__residual_ridge_w05 | 0.695709 | 0.620437 |
| Q3 | only_rhythm__residual_mean_w10 | 0.674722 | 0.620437 |
| S1 | no_temporal_delta__residual_ridge_w10 | 0.567079 | 0.620437 |
| S2 | only_rhythm_deviation_cross_modal__residual_ridge_w05 | 0.572205 | 0.620437 |
| S3 | only_missingness__residual_ridge_w10 | 0.530604 | 0.620437 |
| S4 | only_missingness_cross_modal__residual_mean_w20 | 0.635694 | 0.620437 |

## Summary

- Best global: `no_ratio__residual_ridge_w03` avg `0.626331`
- Target-wise avg: `0.620437`
- Best global drift vs reference: `0.063475`
- Target-wise drift vs reference: `0.066478`
