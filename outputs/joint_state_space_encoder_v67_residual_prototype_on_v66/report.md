# Joint state-space encoder

- Base OOF: `0.489729`
- Best source: `base`
- Best source OOF: `0.489729`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.489729 | 0.533569 | 0.543122 | 0.509450 | 0.479082 | 0.466655 | 0.419794 | 0.476432 |
| joint_proto_mix | 0.502405 | 0.545280 | 0.559113 | 0.526591 | 0.488473 | 0.477757 | 0.431913 | 0.487708 |
| joint_local_logreg | 0.524406 | 0.551421 | 0.575979 | 0.541634 | 0.531802 | 0.513422 | 0.458895 | 0.497688 |
| joint_neighbor_logreg | 0.524880 | 0.550476 | 0.576961 | 0.546533 | 0.534430 | 0.511015 | 0.463723 | 0.491025 |
| joint_residual_metric_neighbor_logreg | 0.530217 | 0.554346 | 0.580569 | 0.558705 | 0.539053 | 0.513421 | 0.465965 | 0.499459 |
| joint_metric_neighbor_logreg | 0.530436 | 0.555718 | 0.583794 | 0.559311 | 0.536071 | 0.515698 | 0.464355 | 0.498105 |
| joint_neighbor_hgb | 0.543693 | 0.580416 | 0.604484 | 0.588997 | 0.515580 | 0.507854 | 0.469967 | 0.538551 |
| joint_metric_neighbor_hgb | 0.546135 | 0.591545 | 0.610556 | 0.589639 | 0.506335 | 0.512149 | 0.467398 | 0.545322 |
| joint_residual_pls_neighbor_logreg | 0.549952 | 0.586317 | 0.576839 | 0.632772 | 0.562084 | 0.532705 | 0.456418 | 0.502527 |
| joint_residual_pls_local_logreg | 0.550271 | 0.589184 | 0.584406 | 0.629498 | 0.557631 | 0.526737 | 0.457112 | 0.507331 |
| joint_residual_metric_neighbor_hgb | 0.550940 | 0.589054 | 0.609462 | 0.594275 | 0.516976 | 0.512824 | 0.480366 | 0.553625 |
| joint_local_hgb | 0.555954 | 0.588978 | 0.636306 | 0.592441 | 0.532806 | 0.519869 | 0.465235 | 0.556041 |
| joint_residual_pls_neighbor_hgb | 0.560203 | 0.602332 | 0.602773 | 0.634079 | 0.533151 | 0.517029 | 0.475411 | 0.556645 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.562966 | 0.641542 | 0.626994 | 0.582732 | 0.527403 | 0.543966 | 0.490047 | 0.528077 |
| joint_neural_cross_family_residual_knn_resid | 0.563581 | 0.621237 | 0.585135 | 0.619872 | 0.570557 | 0.519083 | 0.466897 | 0.562283 |
| joint_cross_family_residual_pls_knn_resid | 0.568583 | 0.602110 | 0.609235 | 0.604475 | 0.556986 | 0.555366 | 0.494755 | 0.557157 |
| joint_residual_pls_local_hgb | 0.569851 | 0.606076 | 0.633798 | 0.640486 | 0.549693 | 0.523501 | 0.478856 | 0.556547 |
| joint_residual_contrast_hgb | 0.571709 | 0.596368 | 0.662848 | 0.616216 | 0.548321 | 0.524825 | 0.483887 | 0.569494 |
| joint_neural_s_residual_knn_resid | 0.576148 | 0.621237 | 0.585135 | 0.619872 | 0.557247 | 0.585410 | 0.520044 | 0.544089 |
| joint_neural_residual_knn_resid | 0.587597 | 0.711956 | 0.636611 | 0.619694 | 0.556424 | 0.556470 | 0.487248 | 0.544776 |
| joint_pls_knn_resid | 0.589296 | 0.606304 | 0.682441 | 0.685533 | 0.560855 | 0.555733 | 0.483116 | 0.551090 |
| joint_neural_cross_family_residual_knn_logitresid | 0.589876 | 0.654378 | 0.659760 | 0.653722 | 0.577405 | 0.545355 | 0.477840 | 0.560674 |
| joint_residual_contrast_logreg | 0.590933 | 0.604505 | 0.665461 | 0.623352 | 0.598669 | 0.560736 | 0.511518 | 0.572289 |
| joint_cross_family_residual_pls_knn_logitresid | 0.593084 | 0.663369 | 0.673554 | 0.630265 | 0.559376 | 0.540012 | 0.519819 | 0.565195 |
| joint_proto_neural_multiview_residual_knn_resid | 0.594676 | 0.697072 | 0.651498 | 0.619341 | 0.598866 | 0.534144 | 0.512700 | 0.549110 |
| joint_neural_multiview_s_residual_knn_resid | 0.595100 | 0.641542 | 0.626994 | 0.582732 | 0.629078 | 0.583356 | 0.525945 | 0.576051 |
| joint_neural_multiview_q_residual_knn_resid | 0.595330 | 0.769802 | 0.641051 | 0.666965 | 0.527403 | 0.543966 | 0.490047 | 0.528077 |
| joint_metric_knn_resid | 0.601394 | 0.618121 | 0.713963 | 0.657113 | 0.564702 | 0.575632 | 0.485867 | 0.594357 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.601662 | 0.677207 | 0.682401 | 0.649732 | 0.572450 | 0.558954 | 0.515422 | 0.555470 |
| joint_s_residual_pls_knn_resid | 0.602797 | 0.602110 | 0.609235 | 0.604475 | 0.656738 | 0.618125 | 0.471584 | 0.657310 |
| joint_neural_multiview_qs_residual_knn_resid | 0.603579 | 0.702664 | 0.623701 | 0.644501 | 0.605823 | 0.575287 | 0.515747 | 0.557332 |
| joint_residual_metric_knn_resid | 0.603790 | 0.618872 | 0.717603 | 0.697936 | 0.592887 | 0.556778 | 0.483101 | 0.559350 |
| joint_neural_multiview_residual_knn_resid | 0.604482 | 0.653690 | 0.655937 | 0.645156 | 0.644390 | 0.562701 | 0.528241 | 0.541261 |
| joint_metric_attention_knn_resid | 0.607225 | 0.635756 | 0.738435 | 0.660998 | 0.566690 | 0.564775 | 0.496470 | 0.587453 |
| joint_attention_knn_resid | 0.607763 | 0.621792 | 0.714480 | 0.691619 | 0.569009 | 0.564437 | 0.509325 | 0.583676 |
| joint_panel_neural_multiview_residual_knn_resid | 0.608881 | 0.656456 | 0.675182 | 0.617803 | 0.613384 | 0.563485 | 0.551259 | 0.584598 |
| joint_neural_s_residual_knn_logitresid | 0.611317 | 0.654378 | 0.659760 | 0.653722 | 0.606310 | 0.588097 | 0.531535 | 0.585414 |
| joint_neural_q_residual_knn_resid | 0.614471 | 0.691076 | 0.790010 | 0.701387 | 0.570557 | 0.519083 | 0.466897 | 0.562283 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.625863 | 0.677207 | 0.682401 | 0.649732 | 0.639027 | 0.585795 | 0.533053 | 0.613823 |
| joint_neural_qs_residual_knn_resid | 0.626727 | 0.695844 | 0.760407 | 0.715711 | 0.573997 | 0.615603 | 0.471279 | 0.554247 |
| joint_qs_residual_pls_knn_resid | 0.628538 | 0.648396 | 0.763940 | 0.691973 | 0.651494 | 0.565449 | 0.511262 | 0.567248 |
| joint_s_residual_pls_knn_logitresid | 0.630245 | 0.663369 | 0.673554 | 0.630265 | 0.653944 | 0.620818 | 0.503769 | 0.665994 |
| joint_q_residual_pls_knn_resid | 0.634938 | 0.696890 | 0.768883 | 0.814530 | 0.556986 | 0.555366 | 0.494755 | 0.557157 |
| joint_target_neural_multiview_residual_knn_resid | 0.636686 | 0.719192 | 0.773503 | 0.669907 | 0.648908 | 0.574921 | 0.505618 | 0.564753 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.637147 | 0.716326 | 0.749745 | 0.703877 | 0.601860 | 0.580322 | 0.522481 | 0.585415 |
| joint_pls_knn_logitresid | 0.637510 | 0.679413 | 0.766900 | 0.731902 | 0.588063 | 0.590947 | 0.516555 | 0.588790 |
| joint_neural_residual_knn_logitresid | 0.639034 | 0.732842 | 0.725877 | 0.706658 | 0.621115 | 0.602204 | 0.507004 | 0.577537 |
| joint_target_qs_residual_pls_knn_resid | 0.639956 | 0.671205 | 0.794169 | 0.719761 | 0.644961 | 0.548313 | 0.513375 | 0.587910 |
| joint_residual_pls_knn_resid | 0.642636 | 0.633675 | 0.749763 | 0.801632 | 0.642692 | 0.598838 | 0.487683 | 0.584173 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.643259 | 0.773770 | 0.787103 | 0.739644 | 0.572450 | 0.558954 | 0.515422 | 0.555470 |
| joint_proto_neural_residual_knn_resid | 0.643784 | 0.655413 | 0.749054 | 0.752902 | 0.599935 | 0.581873 | 0.558050 | 0.609263 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.643786 | 0.734214 | 0.752011 | 0.705673 | 0.566214 | 0.617953 | 0.531475 | 0.598963 |
| joint_neural_multiview_residual_knn_logitresid | 0.646003 | 0.724911 | 0.748404 | 0.713247 | 0.611883 | 0.623715 | 0.515198 | 0.584660 |
| joint_metric_knn_logitresid | 0.649456 | 0.705551 | 0.756453 | 0.713206 | 0.617944 | 0.604811 | 0.523936 | 0.624289 |
| joint_neural_q_residual_knn_logitresid | 0.651325 | 0.767840 | 0.858860 | 0.771302 | 0.577405 | 0.545355 | 0.477840 | 0.560674 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.651769 | 0.703685 | 0.766196 | 0.691684 | 0.628708 | 0.624810 | 0.545094 | 0.602207 |
| joint_residual_metric_knn_logitresid | 0.652857 | 0.706095 | 0.762383 | 0.725978 | 0.629572 | 0.601035 | 0.519726 | 0.625213 |
| joint_attention_knn_logitresid | 0.656006 | 0.710302 | 0.782460 | 0.753126 | 0.590739 | 0.609446 | 0.536559 | 0.609410 |
| joint_q_residual_pls_knn_logitresid | 0.660735 | 0.775530 | 0.822484 | 0.842730 | 0.559376 | 0.540012 | 0.519819 | 0.565195 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.663920 | 0.730223 | 0.807600 | 0.726978 | 0.625677 | 0.625313 | 0.509404 | 0.622245 |
| joint_metric_attention_knn_logitresid | 0.665930 | 0.738641 | 0.768451 | 0.729732 | 0.619897 | 0.619104 | 0.544848 | 0.640837 |
| joint_qs_residual_pls_knn_logitresid | 0.666825 | 0.741835 | 0.798924 | 0.752896 | 0.646688 | 0.595141 | 0.491978 | 0.640314 |
| joint_neural_qs_residual_knn_logitresid | 0.668055 | 0.729352 | 0.794234 | 0.757868 | 0.612586 | 0.630170 | 0.536870 | 0.615305 |
| joint_family_residual_pls_knn_resid | 0.669151 | 0.696890 | 0.768883 | 0.814530 | 0.656738 | 0.618125 | 0.471584 | 0.657310 |
| joint_panel_neural_residual_knn_resid | 0.669357 | 0.781050 | 0.792963 | 0.744047 | 0.661098 | 0.572954 | 0.502243 | 0.631147 |
| joint_residual_pls_knn_logitresid | 0.672576 | 0.717036 | 0.787734 | 0.813655 | 0.660139 | 0.607194 | 0.501728 | 0.620544 |
| joint_target_qs_residual_pls_knn_logitresid | 0.678698 | 0.747073 | 0.834087 | 0.767581 | 0.646819 | 0.595738 | 0.495959 | 0.663631 |
| joint_panel_neural_residual_knn_logitresid | 0.689872 | 0.835048 | 0.874553 | 0.754914 | 0.610846 | 0.598765 | 0.531853 | 0.623121 |
| joint_target_residual_pls_knn_resid | 0.694742 | 0.791687 | 0.916656 | 0.706672 | 0.766548 | 0.517303 | 0.528141 | 0.636184 |
| joint_proto_neural_residual_knn_logitresid | 0.697445 | 0.777518 | 0.813138 | 0.785058 | 0.687534 | 0.622909 | 0.548166 | 0.647790 |
| joint_family_residual_pls_knn_logitresid | 0.697896 | 0.775530 | 0.822484 | 0.842730 | 0.653944 | 0.620818 | 0.503769 | 0.665994 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_target_residual_pls_knn_logitresid | 0.722050 | 0.814087 | 0.959496 | 0.733773 | 0.739829 | 0.596054 | 0.552038 | 0.659071 |
| joint_target_neural_residual_knn_resid | 0.737250 | 0.852316 | 0.788088 | 0.889600 | 0.701921 | 0.642431 | 0.548009 | 0.738383 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.788451 | 0.949403 | 0.915492 | 0.876484 | 0.716593 | 0.685645 | 0.573779 | 0.801764 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.343516 | 8 | 8 | 10 | 0.274199 | 8 | 8 | 10 | 0.386655 | 10 | 0.354232 | 9 | 6237.394043 | 66 | 10 | 0.397402 | 10 | 0.398732 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.305813 | 8 | 8 | 10 | 0.253763 | 8 | 8 | 10 | 0.381907 | 10 | 0.318374 | 9 | 6457.794922 | 66 | 10 | 0.403479 | 10 | 0.390984 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.312023 | 8 | 8 | 10 | 0.254737 | 8 | 8 | 10 | 0.370263 | 10 | 0.322587 | 9 | 6319.124023 | 66 | 10 | 0.374880 | 10 | 0.424427 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.341329 | 8 | 8 | 10 | 0.265448 | 8 | 8 | 10 | 0.395066 | 10 | 0.361270 | 9 | 6500.414062 | 66 | 10 | 0.398523 | 10 | 0.369492 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.341861 | 8 | 8 | 10 | 0.203397 | 8 | 8 | 10 | 0.415622 | 10 | 0.336699 | 9 | 6446.985352 | 66 | 10 | 0.402554 | 10 | 0.409345 |
