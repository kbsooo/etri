# Joint Label-State Decoder

This experiment decodes through a joint 7-label state: label clusters, label patterns, label-neighbor states, and their mean, then blends the resulting 7-label vector with a fold-safe subject prior.

## Best Sources

| source | preset | decoder | weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_temporal_delta__joint_label_cluster8_w10 | no_temporal_delta | label_cluster8 | 0.100000 | 0.625946 | 0.670992 | 0.696769 | 0.676393 | 0.574416 | 0.577493 | 0.539959 | 0.645601 |
| no_temporal_delta__joint_label_cluster8_w20 | no_temporal_delta | label_cluster8 | 0.200000 | 0.626019 | 0.670862 | 0.691778 | 0.677603 | 0.574393 | 0.576892 | 0.545174 | 0.645429 |
| drop_ratio_temporal_delta__joint_label_cluster8_w10 | drop_ratio_temporal_delta | label_cluster8 | 0.100000 | 0.626156 | 0.670667 | 0.699749 | 0.674525 | 0.575660 | 0.578115 | 0.538530 | 0.645848 |
| drop_ratio_temporal_delta__joint_label_cluster8_w20 | drop_ratio_temporal_delta | label_cluster8 | 0.200000 | 0.626301 | 0.669941 | 0.697641 | 0.673982 | 0.576759 | 0.577904 | 0.541986 | 0.645895 |
| no_temporal_delta__joint_label_cluster8_w05 | no_temporal_delta | label_cluster8 | 0.050000 | 0.626490 | 0.671634 | 0.699786 | 0.676291 | 0.574946 | 0.578542 | 0.537935 | 0.646298 |
| only_rhythm__joint_label_knn25_w10 | only_rhythm | label_knn25 | 0.100000 | 0.626497 | 0.669490 | 0.698141 | 0.673661 | 0.574945 | 0.581340 | 0.539067 | 0.648833 |
| no_temporal_delta__joint_label_state_mean_w10 | no_temporal_delta | label_state_mean | 0.100000 | 0.626530 | 0.671362 | 0.698058 | 0.674551 | 0.575716 | 0.580304 | 0.539812 | 0.645908 |
| no_temporal_delta__joint_label_state_mean_w20 | no_temporal_delta | label_state_mean | 0.200000 | 0.626536 | 0.670867 | 0.693737 | 0.673205 | 0.576483 | 0.581585 | 0.544549 | 0.645330 |
| no_ratio__joint_label_knn25_w10 | no_ratio | label_knn25 | 0.100000 | 0.626571 | 0.672357 | 0.698697 | 0.675142 | 0.575504 | 0.579686 | 0.538318 | 0.646294 |
| drop_ratio_temporal_delta__joint_label_cluster8_w05 | drop_ratio_temporal_delta | label_cluster8 | 0.050000 | 0.626612 | 0.671505 | 0.701287 | 0.675343 | 0.575585 | 0.578881 | 0.537260 | 0.646424 |
| no_temporal_delta__joint_label_knn25_w10 | no_temporal_delta | label_knn25 | 0.100000 | 0.626619 | 0.670823 | 0.698651 | 0.674486 | 0.575910 | 0.581122 | 0.539594 | 0.645747 |
| only_rhythm__joint_label_knn25_w20 | only_rhythm | label_knn25 | 0.200000 | 0.626681 | 0.667346 | 0.693950 | 0.671589 | 0.575104 | 0.583985 | 0.543535 | 0.651254 |
| no_ratio__joint_label_knn25_w20 | no_ratio | label_knn25 | 0.200000 | 0.626740 | 0.673055 | 0.695224 | 0.674527 | 0.576098 | 0.580425 | 0.541546 | 0.646301 |
| only_rhythm__joint_label_knn25_w05 | only_rhythm | label_knn25 | 0.050000 | 0.626818 | 0.670947 | 0.700541 | 0.674993 | 0.575255 | 0.580539 | 0.537461 | 0.647991 |
| no_missingness__joint_label_cluster8_w10 | no_missingness | label_cluster8 | 0.100000 | 0.626852 | 0.669089 | 0.701471 | 0.677591 | 0.575795 | 0.579487 | 0.538360 | 0.646168 |
| no_temporal_delta__joint_label_state_mean_w05 | no_temporal_delta | label_state_mean | 0.050000 | 0.626862 | 0.671911 | 0.700505 | 0.675460 | 0.575661 | 0.580061 | 0.537901 | 0.646538 |
| no_ratio__joint_label_knn25_w05 | no_ratio | label_knn25 | 0.050000 | 0.626868 | 0.672384 | 0.700798 | 0.675737 | 0.575550 | 0.579743 | 0.537156 | 0.646707 |
| no_temporal_delta__joint_label_knn25_w05 | no_temporal_delta | label_knn25 | 0.050000 | 0.626883 | 0.671623 | 0.700764 | 0.675406 | 0.575715 | 0.580443 | 0.537793 | 0.646436 |
| only_missingness__joint_label_cluster8_w10 | only_missingness | label_cluster8 | 0.100000 | 0.626895 | 0.670369 | 0.701489 | 0.671831 | 0.578270 | 0.582821 | 0.538823 | 0.644664 |
| no_temporal_delta__joint_label_knn25_w20 | no_temporal_delta | label_knn25 | 0.200000 | 0.626904 | 0.669934 | 0.695220 | 0.673242 | 0.577208 | 0.583434 | 0.544104 | 0.645183 |
| drop_ratio_temporal_delta__joint_label_state_mean_w10 | drop_ratio_temporal_delta | label_state_mean | 0.100000 | 0.626931 | 0.671894 | 0.699748 | 0.674160 | 0.576429 | 0.580589 | 0.539168 | 0.646530 |
| no_missingness__joint_label_cluster8_w05 | no_missingness | label_cluster8 | 0.050000 | 0.626942 | 0.670661 | 0.702124 | 0.676921 | 0.575628 | 0.579547 | 0.537119 | 0.646594 |
| only_missingness__joint_label_cluster8_w05 | only_missingness | label_cluster8 | 0.050000 | 0.626962 | 0.671362 | 0.702146 | 0.673983 | 0.576830 | 0.581243 | 0.537363 | 0.645806 |
| drop_ratio_temporal_delta__joint_label_pattern_w10 | drop_ratio_temporal_delta | label_pattern | 0.100000 | 0.627015 | 0.671825 | 0.700886 | 0.674439 | 0.575905 | 0.580142 | 0.538634 | 0.647276 |
| no_ratio__joint_label_state_mean_w10 | no_ratio | label_state_mean | 0.100000 | 0.627056 | 0.670994 | 0.699277 | 0.676033 | 0.575843 | 0.580860 | 0.539203 | 0.647180 |
| drop_ratio_temporal_delta__joint_label_state_mean_w05 | drop_ratio_temporal_delta | label_state_mean | 0.050000 | 0.627072 | 0.672188 | 0.701350 | 0.675260 | 0.576030 | 0.580223 | 0.537600 | 0.646855 |
| no_missingness__joint_label_knn25_w10 | no_missingness | label_knn25 | 0.100000 | 0.627083 | 0.671858 | 0.698680 | 0.673469 | 0.577510 | 0.581774 | 0.540493 | 0.645793 |
| drop_ratio_temporal_delta__joint_label_pattern_w05 | drop_ratio_temporal_delta | label_pattern | 0.050000 | 0.627096 | 0.672135 | 0.701902 | 0.675377 | 0.575758 | 0.579978 | 0.537300 | 0.647221 |
| no_temporal_delta__joint_label_pattern_w10 | no_temporal_delta | label_pattern | 0.100000 | 0.627100 | 0.671011 | 0.698966 | 0.674749 | 0.575538 | 0.581864 | 0.540717 | 0.646855 |
| no_temporal_delta__joint_label_cluster12_w05 | no_temporal_delta | label_cluster12 | 0.050000 | 0.627111 | 0.672890 | 0.700718 | 0.675116 | 0.576300 | 0.580613 | 0.537674 | 0.646468 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | only_rhythm__joint_label_knn25_w35 | 0.666110 | 0.621371 |
| Q2 | no_temporal_delta__joint_label_cluster8_w35 | 0.686994 | 0.621371 |
| Q3 | only_missingness__joint_label_cluster8_w35 | 0.666890 | 0.621371 |
| S1 | no_temporal_delta__joint_label_cluster8_w20 | 0.574393 | 0.621371 |
| S2 | no_temporal_delta__joint_label_cluster8_w20 | 0.576892 | 0.621371 |
| S3 | only_rhythm__joint_label_cluster12_w05 | 0.537057 | 0.621371 |
| S4 | no_sleep__joint_label_cluster8_w35 | 0.641260 | 0.621371 |

## Summary

- Best global: `no_temporal_delta__joint_label_cluster8_w10` avg `0.625946`
- Target-wise avg: `0.621371`
- Best global drift vs reference: `0.066050`
- Target-wise drift vs reference: `0.073087`
