# Joint state-space encoder

- Base OOF: `0.488680`
- Best source: `base`
- Best source OOF: `0.488680`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.488680 | 0.533398 | 0.542175 | 0.508788 | 0.478086 | 0.463496 | 0.419292 | 0.475524 |
| joint_proto_mix | 0.501608 | 0.545065 | 0.558414 | 0.526280 | 0.487901 | 0.475002 | 0.431518 | 0.487076 |
| joint_local_logreg | 0.523149 | 0.551435 | 0.575658 | 0.540327 | 0.530400 | 0.508869 | 0.458168 | 0.497190 |
| joint_neighbor_logreg | 0.523554 | 0.550530 | 0.576580 | 0.545115 | 0.533274 | 0.506258 | 0.462810 | 0.490308 |
| joint_residual_metric_neighbor_logreg | 0.528543 | 0.553399 | 0.583112 | 0.554656 | 0.536624 | 0.508473 | 0.465249 | 0.498292 |
| joint_metric_neighbor_logreg | 0.529084 | 0.555696 | 0.583730 | 0.557727 | 0.535085 | 0.510232 | 0.463690 | 0.497426 |
| joint_neighbor_hgb | 0.541669 | 0.578030 | 0.600761 | 0.583098 | 0.518034 | 0.501352 | 0.470516 | 0.539894 |
| joint_cross_family_residual_pls_knn_resid | 0.548254 | 0.593628 | 0.613684 | 0.553223 | 0.559276 | 0.493543 | 0.487012 | 0.537413 |
| joint_metric_neighbor_hgb | 0.548676 | 0.594394 | 0.614746 | 0.585982 | 0.509440 | 0.514464 | 0.473567 | 0.548140 |
| joint_residual_metric_neighbor_hgb | 0.549540 | 0.587848 | 0.605510 | 0.594591 | 0.521340 | 0.504780 | 0.479964 | 0.552745 |
| joint_residual_pls_local_logreg | 0.550487 | 0.585156 | 0.588789 | 0.623969 | 0.557833 | 0.523560 | 0.468629 | 0.505471 |
| joint_residual_pls_neighbor_logreg | 0.550658 | 0.584945 | 0.582199 | 0.628963 | 0.565043 | 0.528789 | 0.466670 | 0.497996 |
| joint_local_hgb | 0.554166 | 0.586882 | 0.632386 | 0.587669 | 0.534360 | 0.518929 | 0.464673 | 0.554263 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.554939 | 0.636524 | 0.600336 | 0.595828 | 0.536019 | 0.505464 | 0.499669 | 0.510731 |
| joint_residual_pls_neighbor_hgb | 0.563822 | 0.605041 | 0.609783 | 0.622599 | 0.535650 | 0.530780 | 0.486864 | 0.556039 |
| joint_neural_cross_family_residual_knn_resid | 0.563905 | 0.609909 | 0.624659 | 0.588642 | 0.581544 | 0.545741 | 0.460233 | 0.536606 |
| joint_residual_contrast_hgb | 0.570462 | 0.591520 | 0.655944 | 0.615046 | 0.550408 | 0.530267 | 0.484232 | 0.565816 |
| joint_residual_pls_local_hgb | 0.573556 | 0.603619 | 0.644371 | 0.637949 | 0.549995 | 0.532461 | 0.483649 | 0.562848 |
| joint_s_residual_pls_knn_resid | 0.585385 | 0.593628 | 0.613684 | 0.553223 | 0.656642 | 0.604451 | 0.469921 | 0.606143 |
| joint_cross_family_residual_pls_knn_logitresid | 0.588492 | 0.647280 | 0.687537 | 0.607467 | 0.568126 | 0.529182 | 0.516153 | 0.563701 |
| joint_pls_knn_resid | 0.589124 | 0.606103 | 0.681643 | 0.685222 | 0.568903 | 0.550813 | 0.483063 | 0.548121 |
| joint_neural_multiview_s_residual_knn_resid | 0.590285 | 0.636524 | 0.600336 | 0.595828 | 0.600885 | 0.590430 | 0.515685 | 0.592307 |
| joint_residual_contrast_logreg | 0.591039 | 0.603961 | 0.666324 | 0.623582 | 0.599929 | 0.558952 | 0.512019 | 0.572507 |
| joint_neural_qs_residual_knn_resid | 0.592342 | 0.637332 | 0.649526 | 0.707894 | 0.572917 | 0.550371 | 0.461915 | 0.566439 |
| joint_neural_multiview_residual_knn_resid | 0.594982 | 0.647670 | 0.630891 | 0.675056 | 0.598883 | 0.555882 | 0.484410 | 0.572081 |
| joint_metric_knn_resid | 0.597467 | 0.618039 | 0.713809 | 0.646834 | 0.567666 | 0.557654 | 0.485618 | 0.592652 |
| joint_neural_s_residual_knn_resid | 0.599641 | 0.609909 | 0.624659 | 0.588642 | 0.672502 | 0.590058 | 0.494067 | 0.617652 |
| joint_neural_residual_knn_resid | 0.602017 | 0.669531 | 0.641508 | 0.632439 | 0.594457 | 0.552139 | 0.473556 | 0.650491 |
| joint_neural_cross_family_residual_knn_logitresid | 0.602065 | 0.671515 | 0.689476 | 0.633460 | 0.580504 | 0.589339 | 0.470033 | 0.580127 |
| joint_neural_q_residual_knn_resid | 0.602898 | 0.693728 | 0.703783 | 0.698652 | 0.581544 | 0.545741 | 0.460233 | 0.536606 |
| joint_residual_metric_knn_resid | 0.605261 | 0.621015 | 0.710731 | 0.699805 | 0.579702 | 0.550459 | 0.497680 | 0.577434 |
| joint_metric_attention_knn_resid | 0.606914 | 0.635763 | 0.739508 | 0.661478 | 0.569419 | 0.561103 | 0.496338 | 0.584790 |
| joint_attention_knn_resid | 0.607120 | 0.621675 | 0.725164 | 0.691871 | 0.570020 | 0.559812 | 0.509236 | 0.572059 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.608723 | 0.694135 | 0.694889 | 0.660587 | 0.568554 | 0.573124 | 0.507767 | 0.562003 |
| joint_neural_multiview_qs_residual_knn_resid | 0.612359 | 0.732704 | 0.657323 | 0.657119 | 0.574086 | 0.558188 | 0.541437 | 0.565655 |
| joint_panel_neural_multiview_residual_knn_resid | 0.613126 | 0.664496 | 0.683950 | 0.740801 | 0.568292 | 0.548270 | 0.525095 | 0.560974 |
| joint_neural_multiview_q_residual_knn_resid | 0.616397 | 0.806263 | 0.708008 | 0.748625 | 0.536019 | 0.505464 | 0.499669 | 0.510731 |
| joint_proto_neural_multiview_residual_knn_resid | 0.616419 | 0.762048 | 0.646780 | 0.655845 | 0.589845 | 0.577132 | 0.511739 | 0.571545 |
| joint_q_residual_pls_knn_resid | 0.619935 | 0.694279 | 0.750300 | 0.817718 | 0.559276 | 0.493543 | 0.487012 | 0.537413 |
| joint_proto_neural_residual_knn_resid | 0.626813 | 0.695968 | 0.725679 | 0.675475 | 0.589328 | 0.599623 | 0.489945 | 0.611669 |
| joint_qs_residual_pls_knn_resid | 0.627690 | 0.667759 | 0.746517 | 0.692174 | 0.658592 | 0.545127 | 0.506255 | 0.577409 |
| joint_s_residual_pls_knn_logitresid | 0.629204 | 0.647280 | 0.687537 | 0.607467 | 0.659009 | 0.627185 | 0.511204 | 0.664749 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.632778 | 0.694135 | 0.694889 | 0.660587 | 0.613114 | 0.622233 | 0.527970 | 0.616521 |
| joint_residual_pls_knn_resid | 0.633218 | 0.633257 | 0.721709 | 0.785061 | 0.661060 | 0.562673 | 0.507470 | 0.561299 |
| joint_proto_neural_multiview_metric_knn_resid | 0.635239 | 0.786765 | 0.670530 | 0.665617 | 0.607078 | 0.622148 | 0.508004 | 0.586535 |
| joint_pls_knn_logitresid | 0.637019 | 0.678768 | 0.768059 | 0.736482 | 0.589065 | 0.580066 | 0.516035 | 0.590659 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.640141 | 0.716465 | 0.757922 | 0.725829 | 0.591677 | 0.594297 | 0.507332 | 0.587467 |
| joint_neural_s_residual_knn_logitresid | 0.641148 | 0.671515 | 0.689476 | 0.633460 | 0.636707 | 0.649530 | 0.569786 | 0.637565 |
| joint_neural_residual_knn_logitresid | 0.642134 | 0.722242 | 0.742058 | 0.684044 | 0.635024 | 0.624941 | 0.485414 | 0.601215 |
| joint_neural_multiview_residual_knn_logitresid | 0.647807 | 0.717500 | 0.758190 | 0.737297 | 0.610210 | 0.625071 | 0.489394 | 0.596986 |
| joint_metric_knn_logitresid | 0.648515 | 0.705010 | 0.757816 | 0.716343 | 0.618505 | 0.593645 | 0.522624 | 0.625664 |
| joint_panel_neural_residual_knn_resid | 0.649388 | 0.705602 | 0.796308 | 0.721073 | 0.611892 | 0.632115 | 0.514354 | 0.564371 |
| joint_target_qs_residual_pls_knn_resid | 0.651074 | 0.729726 | 0.771721 | 0.717735 | 0.655795 | 0.551783 | 0.534061 | 0.596699 |
| joint_proto_neural_metric_knn_resid | 0.652385 | 0.711601 | 0.743248 | 0.764039 | 0.628711 | 0.635560 | 0.487359 | 0.596173 |
| joint_residual_metric_knn_logitresid | 0.653891 | 0.708630 | 0.769570 | 0.733442 | 0.625648 | 0.590650 | 0.519597 | 0.629702 |
| joint_neural_qs_residual_knn_logitresid | 0.655233 | 0.738012 | 0.764579 | 0.760360 | 0.597171 | 0.610768 | 0.511033 | 0.604710 |
| joint_attention_knn_logitresid | 0.655631 | 0.709654 | 0.783648 | 0.758594 | 0.592342 | 0.598087 | 0.536481 | 0.610610 |
| joint_family_residual_pls_knn_resid | 0.657065 | 0.694279 | 0.750300 | 0.817718 | 0.656642 | 0.604451 | 0.469921 | 0.606143 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.660460 | 0.760535 | 0.750960 | 0.731835 | 0.594415 | 0.617965 | 0.536366 | 0.631146 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.661044 | 0.775993 | 0.838730 | 0.801138 | 0.568554 | 0.573124 | 0.507767 | 0.562003 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.661795 | 0.714341 | 0.797188 | 0.766616 | 0.587396 | 0.623611 | 0.529596 | 0.613816 |
| joint_qs_residual_pls_knn_logitresid | 0.662350 | 0.744228 | 0.774159 | 0.742228 | 0.634103 | 0.599585 | 0.501685 | 0.640458 |
| joint_q_residual_pls_knn_logitresid | 0.663376 | 0.795993 | 0.826726 | 0.843748 | 0.568126 | 0.529182 | 0.516153 | 0.563701 |
| joint_metric_attention_knn_logitresid | 0.665085 | 0.738220 | 0.769705 | 0.733679 | 0.621088 | 0.607485 | 0.543782 | 0.641636 |
| joint_target_neural_multiview_residual_knn_resid | 0.669083 | 0.679050 | 0.795711 | 0.758242 | 0.675751 | 0.686453 | 0.554928 | 0.533447 |
| joint_neural_q_residual_knn_logitresid | 0.670120 | 0.818279 | 0.839710 | 0.812850 | 0.580504 | 0.589339 | 0.470033 | 0.580127 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.677960 | 0.780315 | 0.774888 | 0.746759 | 0.607208 | 0.645867 | 0.534869 | 0.655816 |
| joint_target_qs_residual_pls_knn_logitresid | 0.679818 | 0.759309 | 0.820826 | 0.750612 | 0.644659 | 0.616662 | 0.512394 | 0.654267 |
| joint_residual_pls_knn_logitresid | 0.680199 | 0.721258 | 0.803300 | 0.851457 | 0.660270 | 0.606756 | 0.496725 | 0.621630 |
| joint_panel_neural_residual_knn_logitresid | 0.683048 | 0.786502 | 0.865334 | 0.745331 | 0.624653 | 0.650454 | 0.525444 | 0.583616 |
| joint_proto_neural_residual_knn_logitresid | 0.684407 | 0.813461 | 0.810543 | 0.751895 | 0.654617 | 0.620454 | 0.524671 | 0.615208 |
| joint_proto_neural_metric_knn_logitresid | 0.685228 | 0.792614 | 0.801283 | 0.769640 | 0.663012 | 0.642344 | 0.524792 | 0.602909 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.687297 | 0.736490 | 0.807587 | 0.809917 | 0.638997 | 0.710577 | 0.523559 | 0.583954 |
| joint_family_residual_pls_knn_logitresid | 0.704088 | 0.795993 | 0.826726 | 0.843748 | 0.659009 | 0.627185 | 0.511204 | 0.664749 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_target_residual_pls_knn_resid | 0.718747 | 0.821132 | 0.967952 | 0.708635 | 0.825433 | 0.542734 | 0.536245 | 0.629099 |
| joint_target_residual_pls_knn_logitresid | 0.743654 | 0.839566 | 1.001738 | 0.737982 | 0.745480 | 0.619143 | 0.552329 | 0.709340 |
| joint_target_neural_residual_knn_resid | 0.766186 | 0.854015 | 1.043898 | 0.913500 | 0.696440 | 0.610583 | 0.587945 | 0.656925 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.823347 | 1.016863 | 1.080883 | 1.017776 | 0.689683 | 0.680379 | 0.540938 | 0.736903 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.328006 | 8 | 8 | 10 | 0.269579 | 8 | 8 | 10 | 0.386802 | 10 | 0.349503 | 9 | 6233.797852 | 66 | 10 | 0.422836 | 10 | 0.426135 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.313815 | 8 | 8 | 10 | 0.262257 | 8 | 8 | 10 | 0.406849 | 10 | 0.330926 | 9 | 6413.163086 | 66 | 10 | 0.387777 | 10 | 0.377178 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.300139 | 8 | 8 | 10 | 0.255141 | 8 | 8 | 10 | 0.370035 | 10 | 0.348141 | 9 | 6305.913086 | 66 | 10 | 0.421690 | 10 | 0.415798 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.331610 | 8 | 8 | 10 | 0.261622 | 8 | 8 | 10 | 0.390652 | 10 | 0.362764 | 9 | 6436.376953 | 66 | 10 | 0.378692 | 10 | 0.371433 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.352812 | 8 | 8 | 10 | 0.203108 | 8 | 8 | 10 | 0.402500 | 10 | 0.355814 | 9 | 6451.972168 | 66 | 10 | 0.410075 | 10 | 0.425203 |
