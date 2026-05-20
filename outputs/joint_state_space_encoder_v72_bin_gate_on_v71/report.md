# Joint state-space encoder

- Base OOF: `0.484026`
- Best source: `base`
- Best source OOF: `0.484026`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.484026 | 0.527627 | 0.540598 | 0.504044 | 0.472902 | 0.455850 | 0.415578 | 0.471582 |
| joint_proto_mix | 0.497604 | 0.540067 | 0.557227 | 0.522340 | 0.483643 | 0.467738 | 0.428232 | 0.483982 |
| joint_neighbor_logreg | 0.518531 | 0.545412 | 0.576184 | 0.541798 | 0.527756 | 0.496907 | 0.457946 | 0.483717 |
| joint_local_logreg | 0.518692 | 0.546379 | 0.575746 | 0.537389 | 0.525431 | 0.499538 | 0.453204 | 0.493158 |
| joint_residual_metric_neighbor_logreg | 0.523567 | 0.546619 | 0.585425 | 0.552282 | 0.530516 | 0.498286 | 0.459602 | 0.492236 |
| joint_metric_neighbor_logreg | 0.523855 | 0.549307 | 0.583699 | 0.554090 | 0.529637 | 0.500941 | 0.458656 | 0.490655 |
| joint_neighbor_hgb | 0.538793 | 0.575486 | 0.606920 | 0.570413 | 0.512030 | 0.501892 | 0.465893 | 0.538914 |
| joint_residual_metric_neighbor_hgb | 0.545539 | 0.584262 | 0.611992 | 0.577596 | 0.513431 | 0.505961 | 0.479310 | 0.546222 |
| joint_metric_neighbor_hgb | 0.546656 | 0.597209 | 0.617733 | 0.577872 | 0.504805 | 0.505191 | 0.473748 | 0.550036 |
| joint_residual_pls_local_logreg | 0.550640 | 0.601468 | 0.587848 | 0.624448 | 0.556514 | 0.517626 | 0.462813 | 0.503764 |
| joint_residual_pls_neighbor_logreg | 0.551726 | 0.601819 | 0.580510 | 0.630654 | 0.560646 | 0.525921 | 0.462559 | 0.499972 |
| joint_local_hgb | 0.554239 | 0.583253 | 0.634574 | 0.583941 | 0.531553 | 0.521699 | 0.465460 | 0.559193 |
| joint_cross_family_residual_pls_knn_resid | 0.557555 | 0.610191 | 0.616477 | 0.595017 | 0.552359 | 0.514450 | 0.499884 | 0.514506 |
| joint_neural_cross_family_residual_knn_resid | 0.564505 | 0.609794 | 0.599710 | 0.633887 | 0.530872 | 0.565558 | 0.455510 | 0.556203 |
| joint_residual_pls_neighbor_hgb | 0.566831 | 0.618968 | 0.618626 | 0.630870 | 0.542312 | 0.529001 | 0.471593 | 0.556448 |
| joint_residual_contrast_hgb | 0.568455 | 0.593776 | 0.666984 | 0.604813 | 0.539521 | 0.523977 | 0.482332 | 0.567785 |
| joint_neural_bin_gate_knn_resid | 0.574214 | 0.607641 | 0.673294 | 0.624282 | 0.545840 | 0.532635 | 0.486462 | 0.549343 |
| joint_neural_learned_gate_knn_resid | 0.575370 | 0.610690 | 0.679148 | 0.624010 | 0.544454 | 0.534515 | 0.484274 | 0.550497 |
| joint_residual_pls_local_hgb | 0.580659 | 0.621897 | 0.646287 | 0.650112 | 0.558033 | 0.547337 | 0.483381 | 0.557568 |
| joint_neural_s_residual_knn_resid | 0.582537 | 0.609794 | 0.599710 | 0.633887 | 0.594256 | 0.560354 | 0.503617 | 0.576138 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.582655 | 0.643170 | 0.622036 | 0.648653 | 0.568711 | 0.518380 | 0.475254 | 0.602381 |
| joint_residual_contrast_logreg | 0.587123 | 0.600245 | 0.663307 | 0.622756 | 0.591281 | 0.554999 | 0.506063 | 0.571207 |
| joint_pls_knn_resid | 0.590071 | 0.608978 | 0.684029 | 0.683294 | 0.568312 | 0.544105 | 0.480382 | 0.561396 |
| joint_cross_family_residual_pls_knn_logitresid | 0.592189 | 0.673965 | 0.673035 | 0.601769 | 0.573687 | 0.538049 | 0.514905 | 0.569915 |
| joint_metric_knn_resid | 0.597750 | 0.621844 | 0.722276 | 0.658099 | 0.568313 | 0.551172 | 0.483241 | 0.579304 |
| joint_neural_cross_family_residual_knn_logitresid | 0.601174 | 0.651516 | 0.697456 | 0.670391 | 0.563547 | 0.583736 | 0.460581 | 0.580991 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.602139 | 0.661670 | 0.655523 | 0.659948 | 0.581304 | 0.577653 | 0.491296 | 0.587579 |
| joint_s_residual_pls_knn_resid | 0.603373 | 0.610191 | 0.616477 | 0.595017 | 0.686305 | 0.607114 | 0.472259 | 0.636248 |
| joint_residual_metric_knn_resid | 0.605720 | 0.639378 | 0.745381 | 0.659800 | 0.593400 | 0.541158 | 0.502053 | 0.558872 |
| joint_attention_knn_resid | 0.607205 | 0.627128 | 0.726523 | 0.691741 | 0.569408 | 0.554758 | 0.507714 | 0.573160 |
| joint_metric_attention_knn_resid | 0.611373 | 0.642845 | 0.752061 | 0.664741 | 0.568957 | 0.554194 | 0.494128 | 0.602683 |
| joint_neural_qs_residual_knn_resid | 0.612801 | 0.670727 | 0.717683 | 0.751049 | 0.582532 | 0.557515 | 0.448406 | 0.561695 |
| joint_q_residual_pls_knn_resid | 0.617199 | 0.738080 | 0.718584 | 0.782533 | 0.552359 | 0.514450 | 0.499884 | 0.514506 |
| joint_neural_multiview_qs_residual_knn_resid | 0.617217 | 0.682201 | 0.725549 | 0.658014 | 0.589411 | 0.542770 | 0.497679 | 0.624896 |
| joint_neural_q_residual_knn_resid | 0.617490 | 0.686872 | 0.751506 | 0.775912 | 0.530872 | 0.565558 | 0.455510 | 0.556203 |
| joint_neural_s_residual_knn_logitresid | 0.625326 | 0.651516 | 0.697456 | 0.670391 | 0.642935 | 0.603725 | 0.506528 | 0.604732 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.626472 | 0.661670 | 0.655523 | 0.659948 | 0.621250 | 0.604526 | 0.512680 | 0.669708 |
| joint_neural_multiview_s_residual_knn_resid | 0.626983 | 0.643170 | 0.622036 | 0.648653 | 0.664791 | 0.565754 | 0.550514 | 0.693960 |
| joint_panel_neural_multiview_residual_knn_resid | 0.627175 | 0.669649 | 0.720534 | 0.717539 | 0.611709 | 0.582550 | 0.508253 | 0.579991 |
| joint_neural_multiview_q_residual_knn_resid | 0.628492 | 0.671726 | 0.750795 | 0.812200 | 0.568711 | 0.518380 | 0.475254 | 0.602381 |
| joint_pls_knn_logitresid | 0.633585 | 0.675894 | 0.771171 | 0.738996 | 0.586449 | 0.560101 | 0.515303 | 0.587178 |
| joint_panel_neural_residual_knn_resid | 0.633678 | 0.735084 | 0.708601 | 0.697541 | 0.584476 | 0.628803 | 0.503082 | 0.578159 |
| joint_neural_multiview_residual_knn_resid | 0.633992 | 0.637306 | 0.667499 | 0.760742 | 0.641543 | 0.609171 | 0.515559 | 0.606126 |
| joint_s_residual_pls_knn_logitresid | 0.635282 | 0.673965 | 0.673035 | 0.601769 | 0.684287 | 0.635867 | 0.515074 | 0.662975 |
| joint_proto_neural_multiview_residual_knn_resid | 0.640045 | 0.749390 | 0.688233 | 0.670007 | 0.649327 | 0.613362 | 0.491901 | 0.618096 |
| joint_metric_knn_logitresid | 0.645119 | 0.701395 | 0.762957 | 0.717422 | 0.614808 | 0.575654 | 0.523208 | 0.620389 |
| joint_neural_bin_gate_knn_logitresid | 0.646841 | 0.694719 | 0.787818 | 0.737537 | 0.606068 | 0.591624 | 0.518056 | 0.592067 |
| joint_qs_residual_pls_knn_resid | 0.647510 | 0.682008 | 0.709287 | 0.707251 | 0.675535 | 0.584734 | 0.504414 | 0.669342 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.647922 | 0.712944 | 0.748182 | 0.732646 | 0.585317 | 0.596846 | 0.516958 | 0.642562 |
| joint_residual_metric_knn_logitresid | 0.648606 | 0.691146 | 0.782379 | 0.731612 | 0.622148 | 0.571246 | 0.521483 | 0.620225 |
| joint_neural_learned_gate_knn_logitresid | 0.648985 | 0.699782 | 0.805407 | 0.727102 | 0.602523 | 0.598195 | 0.512053 | 0.597834 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.649097 | 0.744842 | 0.779574 | 0.781432 | 0.581304 | 0.577653 | 0.491296 | 0.587579 |
| joint_target_neural_multiview_residual_knn_resid | 0.652076 | 0.691221 | 0.730030 | 0.681837 | 0.638836 | 0.589229 | 0.556845 | 0.676531 |
| joint_neural_qs_residual_knn_logitresid | 0.652509 | 0.737824 | 0.795567 | 0.772299 | 0.601090 | 0.591910 | 0.481493 | 0.587379 |
| joint_attention_knn_logitresid | 0.653049 | 0.707484 | 0.785357 | 0.762846 | 0.590326 | 0.580290 | 0.536222 | 0.608821 |
| joint_neural_q_residual_knn_logitresid | 0.653652 | 0.768297 | 0.827396 | 0.791013 | 0.563547 | 0.583736 | 0.460581 | 0.580991 |
| joint_neural_residual_knn_resid | 0.653668 | 0.712054 | 0.802019 | 0.714443 | 0.652010 | 0.572757 | 0.517804 | 0.604589 |
| joint_panel_neural_residual_knn_logitresid | 0.658125 | 0.757702 | 0.736642 | 0.749332 | 0.598929 | 0.598725 | 0.527767 | 0.637781 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.662560 | 0.717296 | 0.807906 | 0.740847 | 0.597891 | 0.637535 | 0.517200 | 0.619243 |
| joint_metric_attention_knn_logitresid | 0.662652 | 0.735763 | 0.773289 | 0.737002 | 0.617993 | 0.591465 | 0.545277 | 0.637772 |
| joint_family_residual_pls_knn_resid | 0.663018 | 0.738080 | 0.718584 | 0.782533 | 0.686305 | 0.607114 | 0.472259 | 0.636248 |
| joint_q_residual_pls_knn_logitresid | 0.664122 | 0.783341 | 0.830863 | 0.838094 | 0.573687 | 0.538049 | 0.514905 | 0.569915 |
| joint_residual_pls_knn_resid | 0.665001 | 0.655164 | 0.745317 | 0.805234 | 0.683974 | 0.618336 | 0.518269 | 0.628715 |
| joint_proto_neural_residual_knn_resid | 0.665972 | 0.676070 | 0.776813 | 0.823782 | 0.670934 | 0.586862 | 0.487224 | 0.640122 |
| joint_neural_multiview_residual_knn_logitresid | 0.666610 | 0.699115 | 0.808388 | 0.797631 | 0.613252 | 0.624910 | 0.510037 | 0.612935 |
| joint_qs_residual_pls_knn_logitresid | 0.666757 | 0.728163 | 0.793274 | 0.721565 | 0.647246 | 0.604716 | 0.511629 | 0.660705 |
| joint_target_qs_residual_pls_knn_resid | 0.669598 | 0.693375 | 0.769377 | 0.736214 | 0.699319 | 0.592930 | 0.513689 | 0.682284 |
| joint_proto_neural_multiview_metric_knn_resid | 0.669785 | 0.746726 | 0.734764 | 0.710044 | 0.717927 | 0.624797 | 0.493805 | 0.660431 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.673300 | 0.736779 | 0.822056 | 0.743920 | 0.611988 | 0.664200 | 0.526666 | 0.607489 |
| joint_neural_mixture_knn_resid | 0.674494 | 0.751817 | 0.761976 | 0.807763 | 0.644572 | 0.661416 | 0.467490 | 0.626427 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.678483 | 0.727421 | 0.793531 | 0.779758 | 0.629819 | 0.611862 | 0.521607 | 0.685383 |
| joint_neural_residual_knn_logitresid | 0.679911 | 0.739916 | 0.844432 | 0.761497 | 0.643808 | 0.646195 | 0.500635 | 0.622891 |
| joint_target_qs_residual_pls_knn_logitresid | 0.683165 | 0.741386 | 0.840069 | 0.728635 | 0.656810 | 0.617057 | 0.526626 | 0.671573 |
| joint_neural_mixture_knn_logitresid | 0.685320 | 0.767985 | 0.807190 | 0.807104 | 0.631670 | 0.632713 | 0.513007 | 0.637571 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.697714 | 0.771329 | 0.847442 | 0.791324 | 0.633017 | 0.681619 | 0.534961 | 0.624308 |
| joint_proto_neural_metric_knn_resid | 0.699035 | 0.705602 | 0.874499 | 0.844288 | 0.674442 | 0.630070 | 0.519503 | 0.644842 |
| joint_residual_pls_knn_logitresid | 0.702805 | 0.775337 | 0.806688 | 0.853517 | 0.677126 | 0.632391 | 0.526771 | 0.647808 |
| joint_family_residual_pls_knn_logitresid | 0.707214 | 0.783341 | 0.830863 | 0.838094 | 0.684287 | 0.635867 | 0.515074 | 0.662975 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_proto_neural_residual_knn_logitresid | 0.708558 | 0.713011 | 0.903678 | 0.906418 | 0.682388 | 0.591137 | 0.547329 | 0.615946 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_gated_mixture_knn_resid | 0.723008 | 0.741736 | 0.789172 | 0.855533 | 0.750169 | 0.697300 | 0.526852 | 0.700295 |
| joint_neural_gated_mixture_knn_logitresid | 0.726410 | 0.783655 | 0.840464 | 0.850469 | 0.689883 | 0.671337 | 0.552122 | 0.696943 |
| joint_neural_mixture_metric_knn_logitresid | 0.731123 | 0.815624 | 0.886904 | 0.873639 | 0.660704 | 0.683065 | 0.528033 | 0.669894 |
| joint_neural_mixture_metric_knn_resid | 0.733317 | 0.809074 | 0.817248 | 0.887145 | 0.698353 | 0.725091 | 0.534598 | 0.661708 |
| joint_proto_neural_metric_knn_logitresid | 0.734264 | 0.765462 | 0.933608 | 0.925299 | 0.687976 | 0.616619 | 0.567747 | 0.643136 |
| joint_target_residual_pls_knn_resid | 0.745523 | 0.807969 | 1.050247 | 0.717127 | 0.816536 | 0.606827 | 0.541137 | 0.678820 |
| joint_target_residual_pls_knn_logitresid | 0.747178 | 0.819398 | 1.043373 | 0.741950 | 0.742152 | 0.622015 | 0.558622 | 0.702733 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.762223 | 0.852333 | 0.911191 | 0.878796 | 0.710839 | 0.701397 | 0.573702 | 0.707302 |
| joint_target_neural_residual_knn_resid | 0.780536 | 0.801032 | 1.026870 | 0.980941 | 0.754052 | 0.664696 | 0.523439 | 0.712723 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_neural_gated_mixture_metric_knn_resid | 0.788348 | 0.906417 | 0.846815 | 0.900918 | 0.761295 | 0.759917 | 0.577069 | 0.766007 |
| joint_target_neural_residual_knn_logitresid | 0.806381 | 0.890295 | 1.109124 | 0.935997 | 0.732979 | 0.718330 | 0.559139 | 0.698805 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.302409 | 8 | 8 | 10 | 0.269802 | 8 | 8 | 10 | 0.387876 | 10 | 0.357997 | 9 | 6244.820312 | 66 | 10 | 0.393230 | 10 | 0.429497 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.299648 | 8 | 8 | 10 | 0.272136 | 8 | 8 | 10 | 0.414690 | 10 | 0.344020 | 9 | 6457.946289 | 66 | 10 | 0.375429 | 10 | 0.378576 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.312185 | 8 | 8 | 10 | 0.258718 | 8 | 8 | 10 | 0.374570 | 10 | 0.327129 | 9 | 6348.673828 | 66 | 10 | 0.390611 | 10 | 0.392314 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.342197 | 8 | 8 | 10 | 0.266225 | 8 | 8 | 10 | 0.402328 | 10 | 0.340322 | 9 | 6491.970703 | 66 | 10 | 0.383773 | 10 | 0.369455 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.340255 | 8 | 8 | 10 | 0.211939 | 8 | 8 | 10 | 0.402417 | 10 | 0.360818 | 9 | 6450.196777 | 66 | 10 | 0.415067 | 10 | 0.400732 |
