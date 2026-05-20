# Joint state-space encoder

- Base OOF: `0.486152`
- Best source: `base`
- Best source OOF: `0.486152`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.486152 | 0.530515 | 0.541332 | 0.506621 | 0.475868 | 0.458462 | 0.417891 | 0.472379 |
| joint_proto_mix | 0.499584 | 0.542997 | 0.557871 | 0.524703 | 0.486117 | 0.470494 | 0.430359 | 0.484544 |
| joint_local_logreg | 0.520732 | 0.548889 | 0.576245 | 0.539550 | 0.528387 | 0.502125 | 0.455739 | 0.494191 |
| joint_neighbor_logreg | 0.520844 | 0.548488 | 0.577025 | 0.544318 | 0.530819 | 0.499558 | 0.460574 | 0.485127 |
| joint_residual_metric_neighbor_logreg | 0.526029 | 0.549863 | 0.584094 | 0.554030 | 0.534866 | 0.501549 | 0.464455 | 0.493348 |
| joint_metric_neighbor_logreg | 0.526255 | 0.553124 | 0.584353 | 0.556797 | 0.532613 | 0.503429 | 0.461576 | 0.491893 |
| joint_neighbor_hgb | 0.540749 | 0.584224 | 0.606972 | 0.576242 | 0.511700 | 0.495787 | 0.464533 | 0.545786 |
| joint_residual_metric_neighbor_hgb | 0.547432 | 0.583912 | 0.604071 | 0.586629 | 0.527461 | 0.504594 | 0.472218 | 0.553137 |
| joint_metric_neighbor_hgb | 0.548776 | 0.596513 | 0.612232 | 0.586156 | 0.508797 | 0.510545 | 0.469766 | 0.557423 |
| joint_residual_pls_local_logreg | 0.552403 | 0.601685 | 0.589002 | 0.630500 | 0.556497 | 0.518567 | 0.465298 | 0.505275 |
| joint_residual_pls_neighbor_logreg | 0.553585 | 0.602473 | 0.582642 | 0.634256 | 0.560331 | 0.526191 | 0.466633 | 0.502568 |
| joint_local_hgb | 0.553655 | 0.584988 | 0.629223 | 0.584316 | 0.534128 | 0.516951 | 0.460935 | 0.565046 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.559475 | 0.592041 | 0.588298 | 0.592262 | 0.549989 | 0.586992 | 0.464002 | 0.542739 |
| joint_cross_family_residual_pls_knn_resid | 0.559706 | 0.613128 | 0.593314 | 0.588977 | 0.569542 | 0.548963 | 0.482576 | 0.521444 |
| joint_neural_cross_family_residual_knn_resid | 0.563976 | 0.598946 | 0.652951 | 0.605897 | 0.566337 | 0.520512 | 0.475549 | 0.527640 |
| joint_residual_pls_neighbor_hgb | 0.565421 | 0.618093 | 0.608605 | 0.633585 | 0.531274 | 0.531867 | 0.474873 | 0.559650 |
| joint_residual_contrast_hgb | 0.571891 | 0.600219 | 0.656031 | 0.614278 | 0.548472 | 0.525087 | 0.486855 | 0.572295 |
| joint_residual_pls_local_hgb | 0.577826 | 0.621634 | 0.630355 | 0.653258 | 0.560873 | 0.536185 | 0.472305 | 0.570175 |
| joint_neural_s_residual_knn_resid | 0.586781 | 0.598946 | 0.652951 | 0.605897 | 0.635045 | 0.587019 | 0.455721 | 0.571891 |
| joint_pls_knn_resid | 0.587438 | 0.607464 | 0.683757 | 0.670557 | 0.568754 | 0.548449 | 0.484961 | 0.548126 |
| joint_cross_family_residual_pls_knn_logitresid | 0.588874 | 0.634242 | 0.692861 | 0.638679 | 0.588351 | 0.531638 | 0.493772 | 0.542572 |
| joint_residual_contrast_logreg | 0.589658 | 0.603254 | 0.666965 | 0.624552 | 0.599097 | 0.553113 | 0.510563 | 0.570063 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.590423 | 0.625271 | 0.653736 | 0.631512 | 0.595050 | 0.559613 | 0.487149 | 0.580629 |
| joint_proto_neural_multiview_metric_knn_resid | 0.592333 | 0.622001 | 0.628502 | 0.634443 | 0.642991 | 0.557647 | 0.498553 | 0.562192 |
| joint_neural_multiview_s_residual_knn_resid | 0.593525 | 0.592041 | 0.588298 | 0.592262 | 0.633254 | 0.625678 | 0.502441 | 0.620699 |
| joint_proto_neural_multiview_residual_knn_resid | 0.593649 | 0.611912 | 0.649454 | 0.638315 | 0.630574 | 0.528342 | 0.520105 | 0.576838 |
| joint_s_residual_pls_knn_resid | 0.594700 | 0.613128 | 0.593314 | 0.588977 | 0.661368 | 0.624707 | 0.465209 | 0.616201 |
| joint_neural_multiview_qs_residual_knn_resid | 0.595385 | 0.625154 | 0.644891 | 0.628073 | 0.585758 | 0.568814 | 0.497087 | 0.617920 |
| joint_metric_knn_resid | 0.597197 | 0.620087 | 0.716019 | 0.644450 | 0.567061 | 0.554536 | 0.485267 | 0.592957 |
| joint_neural_residual_knn_resid | 0.597829 | 0.676144 | 0.635958 | 0.648862 | 0.619355 | 0.553531 | 0.523094 | 0.527856 |
| joint_residual_metric_knn_resid | 0.599770 | 0.622906 | 0.706295 | 0.671500 | 0.590585 | 0.549135 | 0.499730 | 0.558242 |
| joint_neural_cross_family_residual_knn_logitresid | 0.601512 | 0.655757 | 0.722926 | 0.657127 | 0.565168 | 0.552965 | 0.497579 | 0.559064 |
| joint_panel_neural_multiview_residual_knn_resid | 0.601614 | 0.674682 | 0.648950 | 0.652266 | 0.541899 | 0.576269 | 0.510983 | 0.606249 |
| joint_attention_knn_resid | 0.605663 | 0.623475 | 0.725809 | 0.678790 | 0.570088 | 0.558337 | 0.509163 | 0.573980 |
| joint_metric_attention_knn_resid | 0.607935 | 0.638989 | 0.741010 | 0.662178 | 0.570242 | 0.559357 | 0.496671 | 0.587102 |
| joint_neural_multiview_residual_knn_resid | 0.608647 | 0.696645 | 0.631972 | 0.725054 | 0.593307 | 0.536563 | 0.467074 | 0.609916 |
| joint_neural_multiview_q_residual_knn_resid | 0.612120 | 0.696701 | 0.668888 | 0.775529 | 0.549989 | 0.586992 | 0.464002 | 0.542739 |
| joint_neural_q_residual_knn_resid | 0.619451 | 0.701023 | 0.800408 | 0.744691 | 0.566337 | 0.520512 | 0.475549 | 0.527640 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.620151 | 0.625271 | 0.653736 | 0.631512 | 0.626484 | 0.620477 | 0.509474 | 0.674105 |
| joint_neural_residual_knn_logitresid | 0.626889 | 0.704647 | 0.672503 | 0.743127 | 0.618940 | 0.577066 | 0.504689 | 0.567250 |
| joint_neural_qs_residual_knn_resid | 0.629396 | 0.628797 | 0.703029 | 0.804729 | 0.569857 | 0.582813 | 0.511496 | 0.605055 |
| joint_q_residual_pls_knn_resid | 0.629682 | 0.712406 | 0.715426 | 0.857416 | 0.569542 | 0.548963 | 0.482576 | 0.521444 |
| joint_s_residual_pls_knn_logitresid | 0.630468 | 0.634242 | 0.692861 | 0.638679 | 0.653416 | 0.634763 | 0.497803 | 0.661512 |
| joint_neural_s_residual_knn_logitresid | 0.630921 | 0.655757 | 0.722926 | 0.657127 | 0.635991 | 0.623411 | 0.482606 | 0.638629 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.633597 | 0.697267 | 0.726068 | 0.713061 | 0.599388 | 0.587805 | 0.491617 | 0.619971 |
| joint_neural_multiview_residual_knn_logitresid | 0.635933 | 0.703137 | 0.717035 | 0.750451 | 0.588982 | 0.589306 | 0.495731 | 0.606887 |
| joint_pls_knn_logitresid | 0.636575 | 0.680519 | 0.771111 | 0.741334 | 0.588462 | 0.569140 | 0.516588 | 0.588873 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.636892 | 0.698870 | 0.698648 | 0.705268 | 0.568749 | 0.611922 | 0.537470 | 0.637316 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.638435 | 0.692536 | 0.716934 | 0.690936 | 0.607809 | 0.610889 | 0.547622 | 0.602317 |
| joint_qs_residual_pls_knn_resid | 0.643110 | 0.680094 | 0.750319 | 0.736389 | 0.670082 | 0.606150 | 0.479840 | 0.578895 |
| joint_target_neural_multiview_residual_knn_resid | 0.643285 | 0.740397 | 0.698414 | 0.646876 | 0.670241 | 0.613189 | 0.540958 | 0.592919 |
| joint_proto_neural_residual_knn_resid | 0.645524 | 0.667208 | 0.715360 | 0.848601 | 0.626457 | 0.560532 | 0.481986 | 0.618525 |
| joint_neural_mixture_knn_resid | 0.646497 | 0.704428 | 0.711262 | 0.743731 | 0.598090 | 0.619874 | 0.564420 | 0.583672 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.646639 | 0.689528 | 0.718529 | 0.709133 | 0.626354 | 0.627847 | 0.554739 | 0.600340 |
| joint_panel_neural_residual_knn_resid | 0.647851 | 0.788086 | 0.818294 | 0.680045 | 0.593270 | 0.566637 | 0.469998 | 0.618629 |
| joint_metric_knn_logitresid | 0.648235 | 0.706876 | 0.761555 | 0.720445 | 0.617366 | 0.584668 | 0.524268 | 0.622470 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.648477 | 0.737704 | 0.782016 | 0.797180 | 0.595050 | 0.559613 | 0.487149 | 0.580629 |
| joint_neural_q_residual_knn_logitresid | 0.650737 | 0.757586 | 0.838002 | 0.784795 | 0.565168 | 0.552965 | 0.497579 | 0.559064 |
| joint_residual_pls_knn_resid | 0.651357 | 0.666495 | 0.667956 | 0.738063 | 0.615802 | 0.635592 | 0.570356 | 0.665232 |
| joint_residual_metric_knn_logitresid | 0.652583 | 0.703451 | 0.772915 | 0.741367 | 0.624093 | 0.580514 | 0.522602 | 0.623136 |
| joint_neural_qs_residual_knn_logitresid | 0.653564 | 0.708535 | 0.784789 | 0.782997 | 0.596528 | 0.579586 | 0.506055 | 0.616460 |
| joint_attention_knn_logitresid | 0.655669 | 0.711263 | 0.786295 | 0.764676 | 0.591402 | 0.588293 | 0.537216 | 0.610539 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.657995 | 0.747706 | 0.769109 | 0.729146 | 0.612455 | 0.631467 | 0.508260 | 0.607819 |
| joint_family_residual_pls_knn_resid | 0.664676 | 0.712406 | 0.715426 | 0.857416 | 0.661368 | 0.624707 | 0.465209 | 0.616201 |
| joint_metric_attention_knn_logitresid | 0.665365 | 0.740397 | 0.772810 | 0.739263 | 0.619598 | 0.599681 | 0.545914 | 0.639888 |
| joint_target_qs_residual_pls_knn_resid | 0.666873 | 0.706058 | 0.794310 | 0.761483 | 0.677662 | 0.625857 | 0.505985 | 0.596756 |
| joint_q_residual_pls_knn_logitresid | 0.666952 | 0.811518 | 0.834370 | 0.866446 | 0.588351 | 0.531638 | 0.493772 | 0.542572 |
| joint_neural_gated_mixture_knn_resid | 0.668412 | 0.759113 | 0.773457 | 0.733145 | 0.627491 | 0.649086 | 0.510072 | 0.626522 |
| joint_qs_residual_pls_knn_logitresid | 0.669595 | 0.733381 | 0.811589 | 0.772479 | 0.625455 | 0.603494 | 0.494970 | 0.645795 |
| joint_neural_mixture_knn_logitresid | 0.672500 | 0.735101 | 0.785986 | 0.781524 | 0.610274 | 0.620791 | 0.546077 | 0.627747 |
| joint_panel_neural_residual_knn_logitresid | 0.674013 | 0.824439 | 0.830678 | 0.700035 | 0.633502 | 0.587073 | 0.525983 | 0.616385 |
| joint_target_qs_residual_pls_knn_logitresid | 0.680599 | 0.751618 | 0.831490 | 0.776875 | 0.638941 | 0.604043 | 0.504848 | 0.656373 |
| joint_proto_neural_metric_knn_resid | 0.684227 | 0.737810 | 0.744110 | 0.871257 | 0.684718 | 0.624357 | 0.504761 | 0.622578 |
| joint_residual_pls_knn_logitresid | 0.687569 | 0.778956 | 0.775117 | 0.819966 | 0.633332 | 0.632332 | 0.537778 | 0.635498 |
| joint_neural_mixture_metric_knn_resid | 0.705353 | 0.809298 | 0.795499 | 0.834251 | 0.706284 | 0.641235 | 0.522916 | 0.627991 |
| joint_neural_gated_mixture_knn_logitresid | 0.705882 | 0.787730 | 0.808295 | 0.826266 | 0.651456 | 0.655093 | 0.544418 | 0.667916 |
| joint_proto_neural_residual_knn_logitresid | 0.707100 | 0.789674 | 0.845387 | 0.880934 | 0.674951 | 0.608549 | 0.498364 | 0.651838 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_family_residual_pls_knn_logitresid | 0.708547 | 0.811518 | 0.834370 | 0.866446 | 0.653416 | 0.634763 | 0.497803 | 0.661512 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_mixture_metric_knn_logitresid | 0.724906 | 0.808850 | 0.858870 | 0.842279 | 0.666886 | 0.664284 | 0.550350 | 0.682822 |
| joint_neural_gated_mixture_metric_knn_resid | 0.737055 | 0.841090 | 0.796210 | 0.864186 | 0.719802 | 0.686285 | 0.548615 | 0.703194 |
| joint_target_residual_pls_knn_resid | 0.737828 | 0.833297 | 1.051893 | 0.685331 | 0.816791 | 0.533163 | 0.543161 | 0.701161 |
| joint_proto_neural_metric_knn_logitresid | 0.740743 | 0.828382 | 0.888173 | 0.926457 | 0.703307 | 0.632930 | 0.539637 | 0.666313 |
| joint_target_neural_residual_knn_resid | 0.743115 | 0.824846 | 0.980941 | 0.785391 | 0.732311 | 0.598955 | 0.588336 | 0.691025 |
| joint_target_residual_pls_knn_logitresid | 0.748617 | 0.833848 | 1.032586 | 0.746633 | 0.735316 | 0.610836 | 0.551933 | 0.729170 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.756423 | 0.864369 | 0.870578 | 0.870981 | 0.719154 | 0.697512 | 0.568166 | 0.704205 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.800885 | 0.934975 | 1.009673 | 0.857918 | 0.798859 | 0.699953 | 0.575583 | 0.729232 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.326563 | 8 | 8 | 10 | 0.276017 | 8 | 8 | 10 | 0.382032 | 10 | 0.342580 | 9 | 6232.405762 | 66 | 10 | 0.418387 | 10 | 0.409097 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.334261 | 8 | 8 | 10 | 0.267151 | 8 | 8 | 10 | 0.411562 | 10 | 0.350117 | 9 | 6471.811035 | 66 | 10 | 0.378241 | 10 | 0.407923 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.305081 | 8 | 8 | 10 | 0.257450 | 8 | 8 | 10 | 0.367670 | 10 | 0.349593 | 9 | 6309.560547 | 66 | 10 | 0.376947 | 10 | 0.436680 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.326092 | 8 | 8 | 10 | 0.261405 | 8 | 8 | 10 | 0.406009 | 10 | 0.359018 | 9 | 6497.356934 | 66 | 10 | 0.376853 | 10 | 0.399250 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.324209 | 8 | 8 | 10 | 0.224682 | 8 | 8 | 10 | 0.388267 | 10 | 0.341286 | 9 | 6464.263672 | 66 | 10 | 0.421595 | 10 | 0.396962 |
