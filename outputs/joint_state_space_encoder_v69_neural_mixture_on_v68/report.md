# Joint state-space encoder

- Base OOF: `0.486989`
- Best source: `base`
- Best source OOF: `0.486989`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.486989 | 0.532067 | 0.541544 | 0.507506 | 0.476227 | 0.459189 | 0.418446 | 0.473941 |
| joint_proto_mix | 0.500234 | 0.544126 | 0.558047 | 0.525228 | 0.486449 | 0.471076 | 0.430861 | 0.485852 |
| joint_local_logreg | 0.521555 | 0.550567 | 0.576106 | 0.539807 | 0.528712 | 0.503145 | 0.456580 | 0.495971 |
| joint_neighbor_logreg | 0.521670 | 0.549922 | 0.576830 | 0.544510 | 0.531322 | 0.500278 | 0.461268 | 0.487562 |
| joint_residual_metric_neighbor_logreg | 0.526528 | 0.552483 | 0.584306 | 0.553753 | 0.533842 | 0.502298 | 0.464234 | 0.494782 |
| joint_metric_neighbor_logreg | 0.527149 | 0.554777 | 0.584210 | 0.556823 | 0.533247 | 0.504064 | 0.462442 | 0.494481 |
| joint_neural_cross_family_residual_knn_resid | 0.540506 | 0.566732 | 0.602494 | 0.601237 | 0.560400 | 0.496671 | 0.458080 | 0.497926 |
| joint_neighbor_hgb | 0.543840 | 0.590138 | 0.606835 | 0.581206 | 0.513646 | 0.500205 | 0.473615 | 0.541235 |
| joint_residual_pls_neighbor_logreg | 0.548382 | 0.584399 | 0.575701 | 0.632955 | 0.557751 | 0.528794 | 0.459099 | 0.499977 |
| joint_residual_pls_local_logreg | 0.548552 | 0.588374 | 0.582640 | 0.629716 | 0.552526 | 0.521910 | 0.459658 | 0.505040 |
| joint_metric_neighbor_hgb | 0.549540 | 0.595626 | 0.613956 | 0.591388 | 0.508705 | 0.508545 | 0.473109 | 0.555449 |
| joint_residual_metric_neighbor_hgb | 0.552267 | 0.598319 | 0.605571 | 0.594655 | 0.523357 | 0.503728 | 0.482308 | 0.557929 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.554812 | 0.646647 | 0.617651 | 0.561090 | 0.541308 | 0.528019 | 0.472596 | 0.516374 |
| joint_local_hgb | 0.556424 | 0.593201 | 0.629851 | 0.586068 | 0.531961 | 0.518924 | 0.473501 | 0.561461 |
| joint_cross_family_residual_pls_knn_resid | 0.561271 | 0.635983 | 0.611510 | 0.564221 | 0.563787 | 0.543795 | 0.472267 | 0.537336 |
| joint_neural_s_residual_knn_resid | 0.562733 | 0.566732 | 0.602494 | 0.601237 | 0.602311 | 0.500071 | 0.472689 | 0.593601 |
| joint_residual_pls_neighbor_hgb | 0.564387 | 0.608498 | 0.614271 | 0.634105 | 0.537478 | 0.532697 | 0.473627 | 0.550031 |
| joint_residual_contrast_hgb | 0.574483 | 0.602106 | 0.659428 | 0.618589 | 0.551067 | 0.527855 | 0.487917 | 0.574422 |
| joint_neural_q_residual_knn_resid | 0.576054 | 0.627177 | 0.671657 | 0.720466 | 0.560400 | 0.496671 | 0.458080 | 0.497926 |
| joint_residual_pls_local_hgb | 0.578565 | 0.630835 | 0.641799 | 0.655233 | 0.547889 | 0.536371 | 0.478913 | 0.558919 |
| joint_pls_knn_resid | 0.587020 | 0.606670 | 0.683687 | 0.672045 | 0.569349 | 0.547206 | 0.484160 | 0.546026 |
| joint_neural_cross_family_residual_knn_logitresid | 0.587062 | 0.620928 | 0.700376 | 0.621245 | 0.584192 | 0.552802 | 0.489966 | 0.539921 |
| joint_neural_qs_residual_knn_resid | 0.588179 | 0.589447 | 0.752934 | 0.637471 | 0.594370 | 0.512659 | 0.463078 | 0.567291 |
| joint_proto_neural_multiview_residual_knn_resid | 0.589023 | 0.639744 | 0.642473 | 0.592985 | 0.613426 | 0.555205 | 0.511902 | 0.567425 |
| joint_residual_contrast_logreg | 0.589915 | 0.603827 | 0.666678 | 0.622392 | 0.598087 | 0.554107 | 0.511592 | 0.572725 |
| joint_cross_family_residual_pls_knn_logitresid | 0.591114 | 0.651886 | 0.684616 | 0.622005 | 0.574413 | 0.550171 | 0.494128 | 0.560580 |
| joint_neural_residual_knn_resid | 0.594335 | 0.703384 | 0.651515 | 0.617546 | 0.574657 | 0.544485 | 0.481598 | 0.587162 |
| joint_panel_neural_multiview_residual_knn_resid | 0.594791 | 0.645246 | 0.619950 | 0.613420 | 0.629305 | 0.579151 | 0.509717 | 0.566750 |
| joint_metric_knn_resid | 0.597145 | 0.619099 | 0.715787 | 0.644869 | 0.567628 | 0.553464 | 0.485345 | 0.593820 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.597818 | 0.681645 | 0.677655 | 0.646485 | 0.558378 | 0.564941 | 0.486369 | 0.569254 |
| joint_proto_neural_multiview_metric_knn_resid | 0.598404 | 0.652916 | 0.649582 | 0.603009 | 0.612976 | 0.571521 | 0.530569 | 0.568252 |
| joint_neural_multiview_s_residual_knn_resid | 0.598968 | 0.646647 | 0.617651 | 0.561090 | 0.631882 | 0.588240 | 0.528567 | 0.618698 |
| joint_neural_multiview_q_residual_knn_resid | 0.603008 | 0.696154 | 0.690666 | 0.775938 | 0.541308 | 0.528019 | 0.472596 | 0.516374 |
| joint_s_residual_pls_knn_resid | 0.604335 | 0.635983 | 0.611510 | 0.564221 | 0.688442 | 0.640447 | 0.461979 | 0.627766 |
| joint_attention_knn_resid | 0.604771 | 0.622505 | 0.725715 | 0.682853 | 0.570797 | 0.556582 | 0.509258 | 0.565689 |
| joint_neural_multiview_residual_knn_resid | 0.605313 | 0.706043 | 0.641027 | 0.642223 | 0.604308 | 0.541573 | 0.495183 | 0.606830 |
| joint_residual_metric_knn_resid | 0.605791 | 0.623168 | 0.707543 | 0.685803 | 0.596247 | 0.549167 | 0.500658 | 0.577950 |
| joint_neural_s_residual_knn_logitresid | 0.606001 | 0.620928 | 0.700376 | 0.621245 | 0.620420 | 0.537772 | 0.517325 | 0.623941 |
| joint_metric_attention_knn_resid | 0.607599 | 0.637407 | 0.740701 | 0.661953 | 0.570787 | 0.558594 | 0.496411 | 0.587338 |
| joint_neural_multiview_qs_residual_knn_resid | 0.617590 | 0.728532 | 0.651503 | 0.631864 | 0.583233 | 0.590259 | 0.531088 | 0.606650 |
| joint_q_residual_pls_knn_resid | 0.629585 | 0.733485 | 0.715460 | 0.840964 | 0.563787 | 0.543795 | 0.472267 | 0.537336 |
| joint_neural_mixture_knn_resid | 0.630469 | 0.683110 | 0.706800 | 0.725748 | 0.631267 | 0.551701 | 0.511092 | 0.603561 |
| joint_s_residual_pls_knn_logitresid | 0.630845 | 0.651886 | 0.684616 | 0.622005 | 0.667778 | 0.634073 | 0.498467 | 0.657087 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.631963 | 0.681645 | 0.677655 | 0.646485 | 0.598480 | 0.617781 | 0.544666 | 0.657030 |
| joint_neural_qs_residual_knn_logitresid | 0.633032 | 0.674249 | 0.803073 | 0.687560 | 0.615416 | 0.558472 | 0.507836 | 0.584621 |
| joint_pls_knn_logitresid | 0.635628 | 0.676860 | 0.770332 | 0.738041 | 0.588934 | 0.567901 | 0.516948 | 0.590378 |
| joint_qs_residual_pls_knn_resid | 0.637223 | 0.702508 | 0.724535 | 0.709723 | 0.660413 | 0.580050 | 0.500325 | 0.583009 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.637482 | 0.711896 | 0.710832 | 0.698846 | 0.595897 | 0.604729 | 0.518346 | 0.621825 |
| joint_neural_q_residual_knn_logitresid | 0.637630 | 0.717627 | 0.737376 | 0.841526 | 0.584192 | 0.552802 | 0.489966 | 0.539921 |
| joint_proto_neural_residual_knn_resid | 0.638452 | 0.738039 | 0.697594 | 0.711437 | 0.634564 | 0.598408 | 0.490220 | 0.598904 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.640158 | 0.680096 | 0.740114 | 0.679609 | 0.591935 | 0.615882 | 0.538243 | 0.635228 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.640634 | 0.768838 | 0.768405 | 0.768255 | 0.558378 | 0.564941 | 0.486369 | 0.569254 |
| joint_neural_multiview_residual_knn_logitresid | 0.641134 | 0.707380 | 0.758994 | 0.728447 | 0.588730 | 0.597355 | 0.484002 | 0.623028 |
| joint_residual_pls_knn_resid | 0.641530 | 0.623461 | 0.677837 | 0.774876 | 0.698395 | 0.589014 | 0.546252 | 0.580877 |
| joint_neural_residual_knn_logitresid | 0.643734 | 0.756100 | 0.726401 | 0.661432 | 0.646787 | 0.574020 | 0.526193 | 0.615206 |
| joint_panel_neural_residual_knn_resid | 0.645299 | 0.717482 | 0.804497 | 0.704183 | 0.635418 | 0.562652 | 0.494520 | 0.598343 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.645433 | 0.765076 | 0.718791 | 0.709269 | 0.590647 | 0.589778 | 0.517078 | 0.627393 |
| joint_metric_knn_logitresid | 0.647234 | 0.703023 | 0.760579 | 0.717421 | 0.617642 | 0.583615 | 0.523508 | 0.624848 |
| joint_target_neural_multiview_residual_knn_resid | 0.651378 | 0.711481 | 0.730568 | 0.659662 | 0.734340 | 0.618342 | 0.501161 | 0.604095 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.654165 | 0.709638 | 0.754952 | 0.699479 | 0.606640 | 0.624766 | 0.540929 | 0.642754 |
| joint_attention_knn_logitresid | 0.654504 | 0.707523 | 0.785780 | 0.760317 | 0.592285 | 0.586841 | 0.537403 | 0.611377 |
| joint_residual_metric_knn_logitresid | 0.654811 | 0.710077 | 0.771982 | 0.736860 | 0.633056 | 0.582758 | 0.522421 | 0.626524 |
| joint_target_qs_residual_pls_knn_resid | 0.657397 | 0.709707 | 0.806252 | 0.716580 | 0.680627 | 0.579526 | 0.504138 | 0.604947 |
| joint_metric_attention_knn_logitresid | 0.664041 | 0.736055 | 0.772244 | 0.735007 | 0.620284 | 0.598058 | 0.544906 | 0.641736 |
| joint_q_residual_pls_knn_logitresid | 0.666123 | 0.807898 | 0.835163 | 0.840509 | 0.574413 | 0.550171 | 0.494128 | 0.560580 |
| joint_neural_mixture_knn_logitresid | 0.667548 | 0.744054 | 0.784380 | 0.750741 | 0.621479 | 0.599157 | 0.522902 | 0.650123 |
| joint_proto_neural_metric_knn_resid | 0.669071 | 0.796999 | 0.715056 | 0.791616 | 0.622148 | 0.623664 | 0.499916 | 0.634098 |
| joint_qs_residual_pls_knn_logitresid | 0.670478 | 0.747509 | 0.792222 | 0.759410 | 0.647072 | 0.599037 | 0.500243 | 0.647850 |
| joint_family_residual_pls_knn_resid | 0.672649 | 0.733485 | 0.715460 | 0.840964 | 0.688442 | 0.640447 | 0.461979 | 0.627766 |
| joint_residual_pls_knn_logitresid | 0.680042 | 0.699218 | 0.779241 | 0.849003 | 0.668161 | 0.619156 | 0.523703 | 0.621812 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.681781 | 0.745501 | 0.752962 | 0.793748 | 0.659097 | 0.678509 | 0.509373 | 0.633275 |
| joint_target_qs_residual_pls_knn_logitresid | 0.682059 | 0.759032 | 0.824022 | 0.755714 | 0.658955 | 0.603433 | 0.508014 | 0.665243 |
| joint_proto_neural_residual_knn_logitresid | 0.683877 | 0.779952 | 0.812709 | 0.723471 | 0.675066 | 0.642509 | 0.522735 | 0.630693 |
| joint_panel_neural_residual_knn_logitresid | 0.693496 | 0.835113 | 0.855010 | 0.750874 | 0.655982 | 0.592140 | 0.536937 | 0.628417 |
| joint_neural_mixture_metric_knn_resid | 0.701135 | 0.725270 | 0.775877 | 0.831249 | 0.697371 | 0.666035 | 0.555709 | 0.656431 |
| joint_family_residual_pls_knn_logitresid | 0.705854 | 0.807898 | 0.835163 | 0.840509 | 0.667778 | 0.634073 | 0.498467 | 0.657087 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_proto_neural_metric_knn_logitresid | 0.710702 | 0.811193 | 0.837403 | 0.745821 | 0.694858 | 0.671412 | 0.546065 | 0.668161 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_mixture_metric_knn_logitresid | 0.727674 | 0.801636 | 0.871919 | 0.842399 | 0.663019 | 0.658849 | 0.555178 | 0.700718 |
| joint_target_residual_pls_knn_resid | 0.733935 | 0.811876 | 0.997929 | 0.722563 | 0.811417 | 0.536439 | 0.603411 | 0.653912 |
| joint_target_residual_pls_knn_logitresid | 0.734753 | 0.799207 | 1.028942 | 0.738546 | 0.743592 | 0.591392 | 0.563451 | 0.678141 |
| joint_target_neural_residual_knn_resid | 0.760087 | 0.912557 | 0.958585 | 0.761475 | 0.667059 | 0.769762 | 0.556936 | 0.694236 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.800554 | 0.959989 | 1.017448 | 0.848934 | 0.727863 | 0.769976 | 0.581445 | 0.698225 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.318539 | 8 | 8 | 10 | 0.280339 | 8 | 8 | 10 | 0.388879 | 10 | 0.376640 | 9 | 6182.943359 | 66 | 10 | 0.438648 | 10 | 0.408688 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.306914 | 8 | 8 | 10 | 0.265811 | 8 | 8 | 10 | 0.421367 | 10 | 0.325349 | 9 | 6488.489258 | 66 | 10 | 0.394925 | 10 | 0.400483 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.316145 | 8 | 8 | 10 | 0.255404 | 8 | 8 | 10 | 0.364993 | 10 | 0.339926 | 9 | 6335.794922 | 66 | 10 | 0.419282 | 10 | 0.417867 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.330441 | 8 | 8 | 10 | 0.267681 | 8 | 8 | 10 | 0.386801 | 10 | 0.369201 | 9 | 6447.655762 | 66 | 10 | 0.367934 | 10 | 0.369942 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.328554 | 8 | 8 | 10 | 0.215554 | 8 | 8 | 10 | 0.382975 | 10 | 0.342751 | 9 | 6528.612305 | 66 | 10 | 0.400049 | 10 | 0.412465 |
