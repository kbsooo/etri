# Joint state-space encoder

- Base OOF: `0.483657`
- Best source: `base`
- Best source OOF: `0.483657`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483657 | 0.527420 | 0.539802 | 0.503916 | 0.472622 | 0.455641 | 0.414965 | 0.471233 |
| joint_proto_mix | 0.497313 | 0.539958 | 0.556589 | 0.522297 | 0.483421 | 0.467493 | 0.427716 | 0.483714 |
| joint_neighbor_logreg | 0.517982 | 0.545531 | 0.574920 | 0.541557 | 0.527220 | 0.496323 | 0.456776 | 0.483548 |
| joint_local_logreg | 0.518185 | 0.546258 | 0.574943 | 0.537194 | 0.524924 | 0.498814 | 0.452011 | 0.493150 |
| joint_residual_metric_neighbor_logreg | 0.522778 | 0.546886 | 0.582728 | 0.552067 | 0.530407 | 0.498052 | 0.458099 | 0.491209 |
| joint_metric_neighbor_logreg | 0.523354 | 0.549293 | 0.582626 | 0.553908 | 0.529181 | 0.500314 | 0.457711 | 0.490443 |
| joint_neighbor_hgb | 0.537139 | 0.574102 | 0.606503 | 0.569770 | 0.509189 | 0.499635 | 0.464715 | 0.536062 |
| joint_metric_neighbor_hgb | 0.547270 | 0.597289 | 0.618343 | 0.576466 | 0.508338 | 0.505665 | 0.475543 | 0.549247 |
| joint_residual_metric_neighbor_hgb | 0.547298 | 0.579168 | 0.615569 | 0.580404 | 0.516497 | 0.508390 | 0.477215 | 0.553843 |
| joint_residual_pls_local_logreg | 0.550716 | 0.604898 | 0.583199 | 0.624768 | 0.555925 | 0.516238 | 0.465724 | 0.504262 |
| joint_residual_pls_neighbor_logreg | 0.551938 | 0.607271 | 0.577032 | 0.628815 | 0.560654 | 0.523994 | 0.464842 | 0.500955 |
| joint_cross_family_residual_pls_knn_resid | 0.553406 | 0.587554 | 0.593930 | 0.602074 | 0.558077 | 0.534197 | 0.479471 | 0.518536 |
| joint_local_hgb | 0.554477 | 0.585044 | 0.636672 | 0.585165 | 0.533500 | 0.516144 | 0.466092 | 0.558724 |
| joint_neural_cross_family_residual_knn_resid | 0.559372 | 0.601269 | 0.598495 | 0.566388 | 0.560864 | 0.546012 | 0.448838 | 0.593737 |
| joint_residual_pls_neighbor_hgb | 0.566161 | 0.628156 | 0.616322 | 0.632669 | 0.550796 | 0.524169 | 0.463055 | 0.547962 |
| joint_residual_contrast_hgb | 0.569838 | 0.592128 | 0.670287 | 0.606514 | 0.538213 | 0.526527 | 0.484967 | 0.570229 |
| joint_neural_bin_gate_knn_resid | 0.575777 | 0.640043 | 0.654795 | 0.639425 | 0.550687 | 0.530948 | 0.466591 | 0.547949 |
| joint_neural_learned_gate_knn_resid | 0.579036 | 0.648965 | 0.662254 | 0.650809 | 0.547762 | 0.532442 | 0.465444 | 0.545576 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.581457 | 0.661053 | 0.609331 | 0.586416 | 0.568358 | 0.566899 | 0.513517 | 0.564623 |
| joint_residual_pls_local_hgb | 0.581733 | 0.634983 | 0.655871 | 0.651138 | 0.564832 | 0.537474 | 0.471727 | 0.556110 |
| joint_residual_contrast_logreg | 0.585979 | 0.601504 | 0.661927 | 0.622598 | 0.587922 | 0.552604 | 0.505172 | 0.570125 |
| joint_pls_knn_resid | 0.587725 | 0.610068 | 0.683532 | 0.682929 | 0.558506 | 0.545300 | 0.479401 | 0.554337 |
| joint_neural_s_residual_knn_resid | 0.589033 | 0.601269 | 0.598495 | 0.566388 | 0.653647 | 0.570553 | 0.532105 | 0.600770 |
| joint_neural_cross_family_residual_knn_logitresid | 0.589199 | 0.642524 | 0.689894 | 0.601227 | 0.563954 | 0.576510 | 0.462450 | 0.587833 |
| joint_cross_family_residual_pls_knn_logitresid | 0.590567 | 0.635368 | 0.670021 | 0.614443 | 0.581928 | 0.547399 | 0.506137 | 0.578676 |
| joint_metric_knn_resid | 0.599632 | 0.623106 | 0.721824 | 0.657853 | 0.570657 | 0.563510 | 0.482806 | 0.577667 |
| joint_proto_neural_multiview_residual_knn_resid | 0.602928 | 0.683969 | 0.640200 | 0.648094 | 0.607616 | 0.573735 | 0.486634 | 0.580245 |
| joint_s_residual_pls_knn_resid | 0.604559 | 0.587554 | 0.593930 | 0.602074 | 0.663104 | 0.682442 | 0.465764 | 0.637046 |
| joint_attention_knn_resid | 0.605521 | 0.628533 | 0.724416 | 0.691800 | 0.557969 | 0.556135 | 0.507516 | 0.572275 |
| joint_residual_metric_knn_resid | 0.607315 | 0.639439 | 0.743418 | 0.659445 | 0.609032 | 0.542789 | 0.500589 | 0.556495 |
| joint_neural_q_residual_knn_resid | 0.607753 | 0.722956 | 0.685933 | 0.695928 | 0.560864 | 0.546012 | 0.448838 | 0.593737 |
| joint_metric_attention_knn_resid | 0.608804 | 0.645220 | 0.743371 | 0.664448 | 0.569461 | 0.554166 | 0.493343 | 0.591617 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.610399 | 0.700086 | 0.674739 | 0.662555 | 0.583456 | 0.575298 | 0.485845 | 0.590814 |
| joint_neural_context_gate_hgb_resid | 0.611006 | 0.677234 | 0.684211 | 0.663379 | 0.579472 | 0.569138 | 0.493546 | 0.610060 |
| joint_neural_residual_knn_resid | 0.613752 | 0.644247 | 0.633074 | 0.732474 | 0.620917 | 0.559195 | 0.481973 | 0.624384 |
| joint_neural_context_gate_hgb_logitresid | 0.615603 | 0.673341 | 0.703503 | 0.663239 | 0.581707 | 0.576008 | 0.502676 | 0.608745 |
| joint_panel_neural_multiview_residual_knn_resid | 0.617031 | 0.683527 | 0.677156 | 0.650071 | 0.627706 | 0.577043 | 0.487300 | 0.616417 |
| joint_neural_qs_residual_knn_resid | 0.617697 | 0.715331 | 0.659923 | 0.697057 | 0.642020 | 0.571515 | 0.461536 | 0.576496 |
| joint_proto_neural_multiview_metric_knn_resid | 0.620911 | 0.700059 | 0.640941 | 0.673898 | 0.610119 | 0.602191 | 0.503930 | 0.615241 |
| joint_neural_multiview_qs_residual_knn_resid | 0.621002 | 0.694455 | 0.687141 | 0.676530 | 0.597429 | 0.585089 | 0.487081 | 0.619292 |
| joint_neural_s_residual_knn_logitresid | 0.621618 | 0.642524 | 0.689894 | 0.601227 | 0.630054 | 0.610262 | 0.522618 | 0.654750 |
| joint_neural_multiview_s_residual_knn_resid | 0.622458 | 0.661053 | 0.609331 | 0.586416 | 0.633854 | 0.614974 | 0.538236 | 0.713340 |
| joint_neural_multiview_residual_knn_resid | 0.622599 | 0.713212 | 0.650624 | 0.704225 | 0.628097 | 0.575330 | 0.484463 | 0.602245 |
| joint_q_residual_pls_knn_resid | 0.623498 | 0.746064 | 0.715389 | 0.812752 | 0.558077 | 0.534197 | 0.479471 | 0.518536 |
| joint_neural_multiview_q_residual_knn_resid | 0.628934 | 0.725816 | 0.691524 | 0.771798 | 0.568358 | 0.566899 | 0.513517 | 0.564623 |
| joint_s_residual_pls_knn_logitresid | 0.631268 | 0.635368 | 0.670021 | 0.614443 | 0.678824 | 0.650702 | 0.505817 | 0.663702 |
| joint_pls_knn_logitresid | 0.633999 | 0.675998 | 0.770342 | 0.740542 | 0.586549 | 0.560537 | 0.515180 | 0.588845 |
| joint_neural_qs_residual_knn_logitresid | 0.635670 | 0.719553 | 0.744804 | 0.699365 | 0.595475 | 0.586198 | 0.493119 | 0.611177 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.636131 | 0.700086 | 0.674739 | 0.662555 | 0.614486 | 0.629472 | 0.495432 | 0.676145 |
| joint_qs_residual_pls_knn_resid | 0.638216 | 0.694219 | 0.679035 | 0.703742 | 0.650712 | 0.570791 | 0.509867 | 0.659148 |
| joint_neural_q_residual_knn_logitresid | 0.638533 | 0.743076 | 0.762916 | 0.772993 | 0.563954 | 0.576510 | 0.462450 | 0.587833 |
| joint_target_neural_multiview_residual_knn_resid | 0.640137 | 0.736729 | 0.723284 | 0.730245 | 0.627147 | 0.586095 | 0.483275 | 0.594184 |
| joint_metric_knn_logitresid | 0.645544 | 0.700933 | 0.762323 | 0.718947 | 0.615064 | 0.575623 | 0.523182 | 0.622733 |
| joint_neural_residual_knn_logitresid | 0.646976 | 0.710605 | 0.732735 | 0.742012 | 0.631214 | 0.596208 | 0.507966 | 0.608090 |
| joint_residual_metric_knn_logitresid | 0.648528 | 0.689207 | 0.779977 | 0.732989 | 0.617312 | 0.576482 | 0.523228 | 0.620504 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.649520 | 0.744175 | 0.756843 | 0.724211 | 0.594932 | 0.597790 | 0.494783 | 0.633909 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.650203 | 0.714333 | 0.776217 | 0.684913 | 0.612421 | 0.625733 | 0.531510 | 0.606297 |
| joint_neural_bin_gate_knn_logitresid | 0.652529 | 0.735279 | 0.770411 | 0.746714 | 0.607685 | 0.600424 | 0.488429 | 0.618761 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.653288 | 0.760075 | 0.798010 | 0.779518 | 0.583456 | 0.575298 | 0.485845 | 0.590814 |
| joint_neural_multiview_residual_knn_logitresid | 0.653471 | 0.717293 | 0.746652 | 0.769107 | 0.619619 | 0.594327 | 0.504400 | 0.622902 |
| joint_attention_knn_logitresid | 0.653538 | 0.707774 | 0.784909 | 0.764793 | 0.590257 | 0.580687 | 0.536060 | 0.610283 |
| joint_neural_learned_gate_knn_logitresid | 0.655307 | 0.743483 | 0.776590 | 0.741085 | 0.609774 | 0.607517 | 0.489444 | 0.619253 |
| joint_panel_neural_residual_knn_resid | 0.656340 | 0.764934 | 0.765239 | 0.715749 | 0.650731 | 0.603029 | 0.478556 | 0.616140 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.656573 | 0.716248 | 0.772438 | 0.723389 | 0.606894 | 0.627496 | 0.515757 | 0.633791 |
| joint_qs_residual_pls_knn_logitresid | 0.661215 | 0.718015 | 0.770608 | 0.707695 | 0.637778 | 0.611446 | 0.517318 | 0.665647 |
| joint_metric_attention_knn_logitresid | 0.663208 | 0.735476 | 0.773359 | 0.738840 | 0.618200 | 0.591504 | 0.545185 | 0.639890 |
| joint_proto_neural_residual_knn_resid | 0.664470 | 0.725473 | 0.734043 | 0.789489 | 0.666793 | 0.619816 | 0.492188 | 0.623484 |
| joint_q_residual_pls_knn_logitresid | 0.667642 | 0.785269 | 0.823990 | 0.850098 | 0.581928 | 0.547399 | 0.506137 | 0.578676 |
| joint_neural_mixture_knn_resid | 0.668744 | 0.789774 | 0.750872 | 0.760645 | 0.698665 | 0.621962 | 0.464086 | 0.595205 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.669317 | 0.741953 | 0.789770 | 0.705079 | 0.629347 | 0.648728 | 0.529573 | 0.640771 |
| joint_target_qs_residual_pls_knn_resid | 0.670384 | 0.716010 | 0.756737 | 0.724656 | 0.664727 | 0.628854 | 0.513768 | 0.687937 |
| joint_family_residual_pls_knn_resid | 0.674652 | 0.746064 | 0.715389 | 0.812752 | 0.663104 | 0.682442 | 0.465764 | 0.637046 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.676675 | 0.752070 | 0.773489 | 0.800889 | 0.629631 | 0.630220 | 0.512177 | 0.638250 |
| joint_residual_pls_knn_resid | 0.677616 | 0.664322 | 0.690159 | 0.837196 | 0.688507 | 0.676040 | 0.521355 | 0.665730 |
| joint_neural_mixture_knn_logitresid | 0.680946 | 0.779214 | 0.819181 | 0.753805 | 0.624855 | 0.625883 | 0.509768 | 0.653915 |
| joint_proto_neural_metric_knn_resid | 0.682347 | 0.730182 | 0.744827 | 0.856072 | 0.667684 | 0.645162 | 0.505705 | 0.626793 |
| joint_target_qs_residual_pls_knn_logitresid | 0.684302 | 0.739251 | 0.826813 | 0.724170 | 0.664862 | 0.627616 | 0.528178 | 0.679226 |
| joint_panel_neural_residual_knn_logitresid | 0.685922 | 0.787166 | 0.832357 | 0.762449 | 0.673284 | 0.615807 | 0.506298 | 0.624097 |
| joint_neural_context_gate_logreg_resid | 0.688101 | 0.812048 | 0.812996 | 0.787338 | 0.650327 | 0.667808 | 0.493383 | 0.592806 |
| joint_neural_context_gate_logreg_logitresid | 0.691541 | 0.784826 | 0.815975 | 0.847711 | 0.642216 | 0.628351 | 0.506334 | 0.615373 |
| joint_proto_neural_residual_knn_logitresid | 0.693319 | 0.725025 | 0.821351 | 0.830583 | 0.684310 | 0.652310 | 0.520634 | 0.619017 |
| joint_neural_gated_mixture_knn_resid | 0.695701 | 0.790089 | 0.749442 | 0.820607 | 0.646210 | 0.679611 | 0.512066 | 0.671886 |
| joint_residual_pls_knn_logitresid | 0.706734 | 0.785642 | 0.802405 | 0.855230 | 0.687959 | 0.631937 | 0.527771 | 0.656194 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_family_residual_pls_knn_logitresid | 0.708343 | 0.785269 | 0.823990 | 0.850098 | 0.678824 | 0.650702 | 0.505817 | 0.663702 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_proto_neural_metric_knn_logitresid | 0.714508 | 0.742118 | 0.850254 | 0.863000 | 0.704237 | 0.684784 | 0.538263 | 0.618903 |
| joint_neural_gated_mixture_knn_logitresid | 0.715865 | 0.829628 | 0.838548 | 0.815083 | 0.653804 | 0.687530 | 0.528844 | 0.657617 |
| joint_neural_mixture_metric_knn_resid | 0.722355 | 0.901804 | 0.777207 | 0.803288 | 0.734362 | 0.666445 | 0.494172 | 0.679206 |
| joint_neural_mixture_metric_knn_logitresid | 0.730087 | 0.849116 | 0.852094 | 0.815635 | 0.677848 | 0.672430 | 0.537113 | 0.706370 |
| joint_target_residual_pls_knn_resid | 0.736265 | 0.826490 | 1.002280 | 0.717017 | 0.822087 | 0.595129 | 0.542835 | 0.648017 |
| joint_target_residual_pls_knn_logitresid | 0.745216 | 0.834598 | 0.996933 | 0.751427 | 0.749693 | 0.622538 | 0.551993 | 0.709328 |
| joint_neural_gated_mixture_metric_knn_resid | 0.747421 | 0.876038 | 0.800948 | 0.844833 | 0.729142 | 0.676891 | 0.547156 | 0.756936 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.761414 | 0.916934 | 0.870064 | 0.853979 | 0.695428 | 0.730608 | 0.569522 | 0.693366 |
| joint_target_neural_residual_knn_resid | 0.778772 | 0.931185 | 0.976779 | 0.897139 | 0.684020 | 0.741208 | 0.550328 | 0.670748 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.792490 | 0.960914 | 1.004037 | 0.938694 | 0.701923 | 0.700930 | 0.543662 | 0.697270 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.324075 | 8 | 8 | 10 | 0.272445 | 8 | 8 | 10 | 0.387277 | 10 | 0.383172 | 9 | 6272.369141 | 66 | 10 | 0.421456 | 10 | 0.432513 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.280013 | 8 | 8 | 10 | 0.269254 | 8 | 8 | 10 | 0.397518 | 10 | 0.336873 | 9 | 6484.809570 | 66 | 10 | 0.409120 | 10 | 0.350747 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.311541 | 8 | 8 | 10 | 0.256711 | 8 | 8 | 10 | 0.368218 | 10 | 0.336757 | 9 | 6349.447266 | 66 | 10 | 0.401204 | 10 | 0.420968 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.359021 | 8 | 8 | 10 | 0.264422 | 8 | 8 | 10 | 0.379494 | 10 | 0.355391 | 9 | 6496.242676 | 66 | 10 | 0.366865 | 10 | 0.397480 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.327696 | 8 | 8 | 10 | 0.208892 | 8 | 8 | 10 | 0.391759 | 10 | 0.357345 | 9 | 6454.710938 | 66 | 10 | 0.393377 | 10 | 0.425731 |
