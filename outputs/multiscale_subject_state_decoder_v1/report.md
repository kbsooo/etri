# Multiscale Subject State Decoder

This experiment strengthens the encoder state with subject-history baselines, past-only ranks, recent 7/14-day deviations, and distance/novelty summaries before applying state decoders.

## Best Sources

| source | preset | decoder | weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm__multiscale_state_mean_w10 | only_rhythm | state_mean | 0.100000 | 0.626267 | 0.671437 | 0.702856 | 0.675653 | 0.572250 | 0.579705 | 0.535835 | 0.646134 |
| drop_ratio_temporal_delta__multiscale_hgb_w10 | drop_ratio_temporal_delta | hgb | 0.100000 | 0.626288 | 0.669974 | 0.700691 | 0.675945 | 0.578266 | 0.578559 | 0.536051 | 0.644531 |
| only_rhythm__multiscale_hgb_w10 | only_rhythm | hgb | 0.100000 | 0.626370 | 0.671014 | 0.702507 | 0.673838 | 0.574762 | 0.580230 | 0.536665 | 0.645577 |
| drop_ratio_temporal_delta__multiscale_hgb_w20 | drop_ratio_temporal_delta | hgb | 0.200000 | 0.626388 | 0.668363 | 0.699650 | 0.676636 | 0.581659 | 0.578050 | 0.537305 | 0.643053 |
| drop_ratio_temporal_delta__multiscale_state_mean_w10 | drop_ratio_temporal_delta | state_mean | 0.100000 | 0.626534 | 0.673156 | 0.704491 | 0.676332 | 0.576144 | 0.576112 | 0.537680 | 0.641822 |
| only_rhythm__multiscale_state_mean_w05 | only_rhythm | state_mean | 0.050000 | 0.626546 | 0.671766 | 0.702656 | 0.675717 | 0.573821 | 0.579657 | 0.535814 | 0.646390 |
| only_rhythm__multiscale_hgb_w20 | only_rhythm | hgb | 0.200000 | 0.626668 | 0.670541 | 0.703443 | 0.672639 | 0.574777 | 0.581336 | 0.538570 | 0.645372 |
| drop_ratio_temporal_delta__multiscale_state_mean_w05 | drop_ratio_temporal_delta | state_mean | 0.050000 | 0.626692 | 0.672662 | 0.703458 | 0.676113 | 0.575754 | 0.577837 | 0.536738 | 0.644278 |
| drop_ratio_temporal_delta__multiscale_hgb_w05 | drop_ratio_temporal_delta | hgb | 0.050000 | 0.626699 | 0.671182 | 0.701741 | 0.676076 | 0.576926 | 0.579193 | 0.535986 | 0.645790 |
| no_sleep__multiscale_state_mean_w10 | no_sleep | state_mean | 0.100000 | 0.626711 | 0.673657 | 0.699905 | 0.674059 | 0.577225 | 0.581400 | 0.540732 | 0.639997 |
| only_rhythm__multiscale_hgb_w05 | only_rhythm | hgb | 0.050000 | 0.626725 | 0.671689 | 0.702628 | 0.674996 | 0.575158 | 0.580036 | 0.536287 | 0.646284 |
| no_sleep__multiscale_state_mean_w05 | no_sleep | state_mean | 0.050000 | 0.626808 | 0.672907 | 0.701258 | 0.674995 | 0.576311 | 0.580511 | 0.538291 | 0.643380 |
| no_temporal_delta__multiscale_state_mean_w05 | no_temporal_delta | state_mean | 0.050000 | 0.626900 | 0.670980 | 0.701742 | 0.678147 | 0.573807 | 0.580837 | 0.537715 | 0.645068 |
| no_temporal_delta__multiscale_state_mean_w10 | no_temporal_delta | state_mean | 0.100000 | 0.626916 | 0.669861 | 0.701015 | 0.680419 | 0.572218 | 0.582081 | 0.539532 | 0.643286 |
| no_ratio__multiscale_state_mean_w05 | no_ratio | state_mean | 0.050000 | 0.626971 | 0.672134 | 0.700199 | 0.676779 | 0.576861 | 0.580133 | 0.536937 | 0.645756 |
| no_missingness__multiscale_state_mean_w05 | no_missingness | state_mean | 0.050000 | 0.627031 | 0.671566 | 0.701394 | 0.677055 | 0.576772 | 0.580078 | 0.538249 | 0.644100 |
| no_ratio__multiscale_state_mean_w10 | no_ratio | state_mean | 0.100000 | 0.627088 | 0.672116 | 0.697935 | 0.677706 | 0.578371 | 0.580646 | 0.538056 | 0.644790 |
| no_ratio__multiscale_hgb_w05 | no_ratio | hgb | 0.050000 | 0.627129 | 0.671790 | 0.701881 | 0.676655 | 0.576255 | 0.580315 | 0.536486 | 0.646519 |
| no_ratio__multiscale_hgb_w10 | no_ratio | hgb | 0.100000 | 0.627132 | 0.671157 | 0.700969 | 0.677118 | 0.576910 | 0.580818 | 0.536962 | 0.645989 |
| no_missingness__multiscale_state_mean_w10 | no_missingness | state_mean | 0.100000 | 0.627162 | 0.671011 | 0.700226 | 0.678248 | 0.578174 | 0.580461 | 0.540599 | 0.641416 |
| no_missingness__multiscale_hgb_w05 | no_missingness | hgb | 0.050000 | 0.627231 | 0.672137 | 0.701948 | 0.676109 | 0.576747 | 0.580126 | 0.538128 | 0.645422 |
| no_temporal_delta__multiscale_hgb_w05 | no_temporal_delta | hgb | 0.050000 | 0.627245 | 0.671319 | 0.702859 | 0.676873 | 0.575715 | 0.580180 | 0.537870 | 0.645896 |
| no_missingness__multiscale_hgb_w10 | no_missingness | hgb | 0.100000 | 0.627327 | 0.671895 | 0.701104 | 0.676010 | 0.577901 | 0.580383 | 0.540243 | 0.643756 |
| no_sleep__multiscale_hgb_w05 | no_sleep | hgb | 0.050000 | 0.627366 | 0.672320 | 0.702837 | 0.675415 | 0.576475 | 0.581743 | 0.537995 | 0.644774 |
| no_temporal_delta__multiscale_hgb_w10 | no_temporal_delta | hgb | 0.100000 | 0.627383 | 0.670257 | 0.702978 | 0.677576 | 0.575910 | 0.580543 | 0.539712 | 0.644709 |
| only_rhythm__multiscale_state_mean_w20 | only_rhythm | state_mean | 0.200000 | 0.627481 | 0.672460 | 0.705308 | 0.677753 | 0.570391 | 0.581208 | 0.537369 | 0.647877 |
| only_missingness__multiscale_hgb_w05 | only_missingness | hgb | 0.050000 | 0.627496 | 0.671108 | 0.702986 | 0.676953 | 0.575704 | 0.581700 | 0.536940 | 0.647083 |
| no_sleep__multiscale_hgb_w10 | no_sleep | hgb | 0.100000 | 0.627581 | 0.672236 | 0.702811 | 0.674599 | 0.577375 | 0.583658 | 0.539921 | 0.642467 |
| only_missingness__multiscale_state_mean_w05 | only_missingness | state_mean | 0.050000 | 0.627747 | 0.671961 | 0.702761 | 0.678679 | 0.575654 | 0.582926 | 0.535258 | 0.646988 |
| only_missingness__multiscale_hgb_w10 | only_missingness | hgb | 0.100000 | 0.627898 | 0.669889 | 0.703201 | 0.677740 | 0.575913 | 0.583602 | 0.537930 | 0.647011 |

## Target-wise Selection

| target | source | log_loss | targetwise_avg_log_loss |
| --- | --- | --- | --- |
| Q1 | drop_ratio_temporal_delta__multiscale_hgb_w20 | 0.668363 | 0.620484 |
| Q2 | no_ratio__multiscale_state_mean_w20 | 0.695445 | 0.620484 |
| Q3 | only_rhythm__multiscale_hgb_w20 | 0.672639 | 0.620484 |
| S1 | no_temporal_delta__multiscale_residual_ridge_w10 | 0.565332 | 0.620484 |
| S2 | drop_ratio_temporal_delta__multiscale_residual_ridge_w05 | 0.574176 | 0.620484 |
| S3 | only_missingness__multiscale_residual_ridge_w05 | 0.532312 | 0.620484 |
| S4 | no_sleep__multiscale_state_mean_w20 | 0.635119 | 0.620484 |

## Summary

- Best global: `only_rhythm__multiscale_state_mean_w10` avg `0.626267`
- Target-wise avg: `0.620484`
- Best global drift vs reference: `0.063039`
- Target-wise drift vs reference: `0.064398`
