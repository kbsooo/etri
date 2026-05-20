# Joint state-space encoder

- Base OOF: `0.481505`
- Best source: `base`
- Best source OOF: `0.481505`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.481505 | 0.525837 | 0.539061 | 0.501390 | 0.470091 | 0.453197 | 0.412158 | 0.468803 |
| joint_proto_mix | 0.495349 | 0.538612 | 0.555854 | 0.520116 | 0.480633 | 0.465252 | 0.425434 | 0.481542 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.511266 | 0.560523 | 0.577544 | 0.545526 | 0.492346 | 0.475220 | 0.430571 | 0.497132 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.512079 | 0.572577 | 0.569555 | 0.551384 | 0.485124 | 0.479914 | 0.429983 | 0.496017 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.513772 | 0.573393 | 0.577835 | 0.546330 | 0.490643 | 0.482467 | 0.427774 | 0.497959 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.514848 | 0.562984 | 0.579375 | 0.556985 | 0.495435 | 0.496808 | 0.426439 | 0.485911 |
| joint_neighbor_logreg | 0.515946 | 0.543480 | 0.574465 | 0.537318 | 0.526001 | 0.493082 | 0.456165 | 0.481106 |
| joint_local_logreg | 0.516302 | 0.544123 | 0.574769 | 0.533997 | 0.523205 | 0.495712 | 0.451313 | 0.490995 |
| joint_residual_metric_neighbor_logreg | 0.521157 | 0.545671 | 0.583947 | 0.547427 | 0.531247 | 0.494710 | 0.456719 | 0.488379 |
| joint_metric_neighbor_logreg | 0.521287 | 0.546950 | 0.582290 | 0.549301 | 0.529284 | 0.496692 | 0.456864 | 0.487628 |
| joint_neighbor_hgb | 0.536719 | 0.568253 | 0.609476 | 0.560109 | 0.500986 | 0.513648 | 0.467168 | 0.537395 |
| joint_metric_neighbor_hgb | 0.543183 | 0.584571 | 0.614634 | 0.574503 | 0.500507 | 0.511592 | 0.472111 | 0.544364 |
| joint_residual_metric_neighbor_hgb | 0.545758 | 0.578539 | 0.609931 | 0.577425 | 0.511906 | 0.519134 | 0.473175 | 0.550198 |
| joint_local_hgb | 0.551555 | 0.577838 | 0.636787 | 0.575748 | 0.517170 | 0.525630 | 0.467551 | 0.560161 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.554322 | 0.600413 | 0.634205 | 0.577968 | 0.524169 | 0.511376 | 0.480928 | 0.551198 |
| joint_residual_pls_neighbor_logreg | 0.554961 | 0.609060 | 0.587914 | 0.628294 | 0.563468 | 0.523583 | 0.461494 | 0.510918 |
| joint_residual_pls_local_logreg | 0.555998 | 0.607254 | 0.593441 | 0.632612 | 0.563254 | 0.519828 | 0.463285 | 0.512313 |
| joint_neural_cross_family_residual_knn_resid | 0.557671 | 0.615801 | 0.632371 | 0.600321 | 0.524701 | 0.487336 | 0.490332 | 0.552833 |
| joint_neural_context_bin_gate_hgb_resid | 0.558388 | 0.610685 | 0.626462 | 0.591894 | 0.521555 | 0.520519 | 0.485473 | 0.552127 |
| joint_cross_family_residual_pls_knn_resid | 0.559811 | 0.594425 | 0.607617 | 0.617058 | 0.547005 | 0.524475 | 0.489985 | 0.538112 |
| joint_residual_contrast_hgb | 0.566041 | 0.594622 | 0.660455 | 0.597461 | 0.544302 | 0.521527 | 0.484637 | 0.559286 |
| joint_residual_pls_neighbor_hgb | 0.573998 | 0.628332 | 0.634987 | 0.642955 | 0.544284 | 0.525138 | 0.475227 | 0.567060 |
| joint_neural_bin_gate_knn_resid | 0.575957 | 0.631626 | 0.670752 | 0.600172 | 0.549998 | 0.532172 | 0.494899 | 0.552078 |
| joint_neural_learned_gate_knn_resid | 0.576311 | 0.631288 | 0.673664 | 0.603265 | 0.548325 | 0.540364 | 0.489038 | 0.548232 |
| joint_residual_pls_local_hgb | 0.579038 | 0.623967 | 0.646787 | 0.649519 | 0.550883 | 0.547238 | 0.474769 | 0.560105 |
| joint_neural_s_residual_knn_resid | 0.579763 | 0.615801 | 0.632371 | 0.600321 | 0.672041 | 0.503166 | 0.465494 | 0.569149 |
| joint_residual_contrast_logreg | 0.584399 | 0.600548 | 0.658569 | 0.620165 | 0.592252 | 0.549158 | 0.502453 | 0.567645 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.585563 | 0.666232 | 0.608392 | 0.610924 | 0.582532 | 0.544458 | 0.509055 | 0.577344 |
| joint_cross_family_residual_pls_knn_logitresid | 0.586442 | 0.643563 | 0.658665 | 0.608462 | 0.569123 | 0.525112 | 0.524982 | 0.575187 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.588870 | 0.640685 | 0.692228 | 0.659720 | 0.569361 | 0.534466 | 0.457091 | 0.568541 |
| joint_pls_knn_resid | 0.589001 | 0.609754 | 0.681796 | 0.679291 | 0.565541 | 0.557376 | 0.478349 | 0.550900 |
| joint_neural_context_bin_gate_logreg_resid | 0.590840 | 0.628305 | 0.685972 | 0.665694 | 0.574027 | 0.561511 | 0.462661 | 0.557711 |
| joint_neural_cross_family_residual_knn_logitresid | 0.597657 | 0.661437 | 0.729129 | 0.603008 | 0.594203 | 0.533047 | 0.493589 | 0.569184 |
| joint_metric_knn_resid | 0.600555 | 0.623597 | 0.721066 | 0.654822 | 0.584144 | 0.561603 | 0.482023 | 0.576633 |
| joint_proto_neural_multiview_residual_knn_resid | 0.602777 | 0.672050 | 0.627733 | 0.647620 | 0.558696 | 0.593552 | 0.528149 | 0.591640 |
| joint_s_residual_pls_knn_resid | 0.604082 | 0.594425 | 0.607617 | 0.617058 | 0.639530 | 0.629440 | 0.477597 | 0.662906 |
| joint_residual_metric_knn_resid | 0.604416 | 0.635054 | 0.724431 | 0.660437 | 0.608317 | 0.541613 | 0.486546 | 0.574516 |
| joint_neural_qs_residual_knn_resid | 0.606346 | 0.673244 | 0.712739 | 0.701052 | 0.608570 | 0.533466 | 0.462224 | 0.553127 |
| joint_neural_multiview_q_residual_knn_resid | 0.606963 | 0.698459 | 0.685567 | 0.651326 | 0.582532 | 0.544458 | 0.509055 | 0.577344 |
| joint_attention_knn_resid | 0.607587 | 0.628358 | 0.721884 | 0.687227 | 0.566269 | 0.568295 | 0.507359 | 0.573718 |
| joint_neural_context_gate_hgb_logitresid | 0.607869 | 0.640525 | 0.702367 | 0.660960 | 0.562942 | 0.573936 | 0.508262 | 0.606092 |
| joint_metric_attention_knn_resid | 0.609435 | 0.648287 | 0.737203 | 0.661573 | 0.584595 | 0.553459 | 0.492157 | 0.588774 |
| joint_neural_context_gate_hgb_resid | 0.610404 | 0.656250 | 0.695012 | 0.663391 | 0.568763 | 0.569164 | 0.517557 | 0.602694 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.611987 | 0.692965 | 0.702400 | 0.656738 | 0.567429 | 0.578748 | 0.505519 | 0.580108 |
| joint_neural_multiview_s_residual_knn_resid | 0.613835 | 0.666232 | 0.608392 | 0.610924 | 0.672873 | 0.612501 | 0.489089 | 0.636836 |
| joint_neural_multiview_qs_residual_knn_resid | 0.615912 | 0.713712 | 0.620708 | 0.687285 | 0.581056 | 0.585866 | 0.535487 | 0.587273 |
| joint_neural_s_residual_knn_logitresid | 0.617292 | 0.661437 | 0.729129 | 0.603008 | 0.638455 | 0.585213 | 0.498693 | 0.605110 |
| joint_neural_q_residual_knn_resid | 0.619648 | 0.796542 | 0.768194 | 0.717596 | 0.524701 | 0.487336 | 0.490332 | 0.552833 |
| joint_panel_neural_multiview_residual_knn_resid | 0.620304 | 0.719721 | 0.661807 | 0.591330 | 0.666002 | 0.597300 | 0.524637 | 0.581334 |
| joint_proto_neural_multiview_metric_knn_resid | 0.621939 | 0.684241 | 0.636510 | 0.646383 | 0.598549 | 0.599130 | 0.520364 | 0.668398 |
| joint_s_residual_pls_knn_logitresid | 0.624942 | 0.643563 | 0.658665 | 0.608462 | 0.671128 | 0.618620 | 0.508165 | 0.665993 |
| joint_q_residual_pls_knn_resid | 0.629982 | 0.803090 | 0.704859 | 0.802348 | 0.547005 | 0.524475 | 0.489985 | 0.538112 |
| joint_pls_knn_logitresid | 0.632462 | 0.678623 | 0.768923 | 0.741148 | 0.580342 | 0.555150 | 0.517065 | 0.585980 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.633134 | 0.692965 | 0.702400 | 0.656738 | 0.623602 | 0.622827 | 0.488878 | 0.644528 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.634282 | 0.663069 | 0.712587 | 0.705217 | 0.560834 | 0.596006 | 0.543748 | 0.658516 |
| joint_neural_residual_knn_resid | 0.638130 | 0.707078 | 0.669698 | 0.679514 | 0.679618 | 0.570423 | 0.498210 | 0.662367 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.640660 | 0.728442 | 0.704679 | 0.712882 | 0.584365 | 0.604780 | 0.504987 | 0.644485 |
| joint_neural_multiview_residual_knn_resid | 0.640842 | 0.718156 | 0.634954 | 0.720068 | 0.681362 | 0.597684 | 0.505466 | 0.628202 |
| joint_metric_knn_logitresid | 0.644282 | 0.703075 | 0.762010 | 0.716804 | 0.608899 | 0.571517 | 0.525944 | 0.621722 |
| joint_neural_qs_residual_knn_logitresid | 0.644777 | 0.726873 | 0.775850 | 0.735057 | 0.610899 | 0.553275 | 0.493364 | 0.618123 |
| joint_target_neural_multiview_residual_knn_resid | 0.645225 | 0.709695 | 0.655215 | 0.712400 | 0.643233 | 0.598197 | 0.541387 | 0.656450 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.647816 | 0.760615 | 0.777986 | 0.764305 | 0.567429 | 0.578748 | 0.505519 | 0.580108 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.648116 | 0.719256 | 0.718941 | 0.699317 | 0.581378 | 0.605789 | 0.538951 | 0.673181 |
| joint_residual_metric_knn_logitresid | 0.648619 | 0.695772 | 0.778223 | 0.733116 | 0.623934 | 0.569526 | 0.522236 | 0.617523 |
| joint_neural_bin_gate_knn_logitresid | 0.648944 | 0.713248 | 0.791406 | 0.725904 | 0.599548 | 0.579981 | 0.514248 | 0.618272 |
| joint_neural_residual_knn_logitresid | 0.649322 | 0.710312 | 0.739009 | 0.767729 | 0.644039 | 0.583054 | 0.511034 | 0.590080 |
| joint_neural_multiview_residual_knn_logitresid | 0.650580 | 0.720789 | 0.716389 | 0.752942 | 0.608061 | 0.596779 | 0.523064 | 0.636038 |
| joint_attention_knn_logitresid | 0.652013 | 0.710654 | 0.782681 | 0.765623 | 0.584439 | 0.575590 | 0.537647 | 0.607462 |
| joint_qs_residual_pls_knn_resid | 0.653288 | 0.690750 | 0.695383 | 0.732356 | 0.702618 | 0.582618 | 0.503590 | 0.665700 |
| joint_neural_learned_gate_knn_logitresid | 0.653367 | 0.716053 | 0.790185 | 0.728968 | 0.606843 | 0.585795 | 0.517306 | 0.628422 |
| joint_neural_q_residual_knn_logitresid | 0.656221 | 0.790637 | 0.844236 | 0.768650 | 0.594203 | 0.533047 | 0.493589 | 0.569184 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.656888 | 0.745990 | 0.709025 | 0.695271 | 0.638367 | 0.629401 | 0.537215 | 0.642946 |
| joint_metric_attention_knn_logitresid | 0.662037 | 0.737978 | 0.772245 | 0.737278 | 0.612282 | 0.587655 | 0.547651 | 0.639168 |
| joint_target_qs_residual_pls_knn_resid | 0.662790 | 0.702254 | 0.733985 | 0.736604 | 0.707974 | 0.595309 | 0.488953 | 0.674451 |
| joint_q_residual_pls_knn_logitresid | 0.663952 | 0.802381 | 0.829450 | 0.821430 | 0.569123 | 0.525112 | 0.524982 | 0.575187 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.664818 | 0.733596 | 0.762053 | 0.725729 | 0.644515 | 0.622141 | 0.533113 | 0.632581 |
| joint_qs_residual_pls_knn_logitresid | 0.664824 | 0.726096 | 0.790822 | 0.723928 | 0.652512 | 0.589309 | 0.508022 | 0.663076 |
| joint_proto_neural_residual_knn_resid | 0.668933 | 0.668399 | 0.706678 | 0.834306 | 0.704714 | 0.630681 | 0.530481 | 0.607269 |
| joint_panel_neural_residual_knn_resid | 0.670961 | 0.806706 | 0.781425 | 0.742896 | 0.635400 | 0.638991 | 0.493651 | 0.597656 |
| joint_neural_mixture_knn_resid | 0.672553 | 0.784239 | 0.770599 | 0.749323 | 0.623559 | 0.619336 | 0.518373 | 0.642444 |
| joint_family_residual_pls_knn_resid | 0.674253 | 0.803090 | 0.704859 | 0.802348 | 0.639530 | 0.629440 | 0.477597 | 0.662906 |
| joint_target_qs_residual_pls_knn_logitresid | 0.676549 | 0.742526 | 0.830947 | 0.716289 | 0.665933 | 0.602087 | 0.512972 | 0.665092 |
| joint_neural_mixture_knn_logitresid | 0.684203 | 0.770473 | 0.846842 | 0.764476 | 0.611345 | 0.615238 | 0.514021 | 0.667028 |
| joint_proto_neural_metric_knn_resid | 0.685542 | 0.693863 | 0.764242 | 0.832633 | 0.713601 | 0.628372 | 0.565046 | 0.601037 |
| joint_neural_context_gate_logreg_logitresid | 0.687965 | 0.744213 | 0.854702 | 0.798913 | 0.643017 | 0.603565 | 0.516573 | 0.654774 |
| joint_neural_context_gate_logreg_resid | 0.689038 | 0.734682 | 0.871060 | 0.767588 | 0.644963 | 0.633651 | 0.514984 | 0.656338 |
| joint_residual_pls_knn_resid | 0.694676 | 0.702742 | 0.739360 | 0.827175 | 0.695594 | 0.672286 | 0.537522 | 0.688055 |
| joint_panel_neural_residual_knn_logitresid | 0.695674 | 0.842463 | 0.810842 | 0.751013 | 0.655369 | 0.673206 | 0.525466 | 0.611359 |
| joint_neural_gated_mixture_knn_resid | 0.698066 | 0.776504 | 0.785995 | 0.805626 | 0.698682 | 0.628922 | 0.502205 | 0.688532 |
| joint_family_residual_pls_knn_logitresid | 0.702452 | 0.802381 | 0.829450 | 0.821430 | 0.671128 | 0.618620 | 0.508165 | 0.665993 |
| joint_proto_neural_residual_knn_logitresid | 0.703943 | 0.742739 | 0.814954 | 0.814509 | 0.718919 | 0.639658 | 0.556450 | 0.640375 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_proto_neural_metric_knn_logitresid | 0.708459 | 0.739185 | 0.809846 | 0.823625 | 0.736523 | 0.649574 | 0.565386 | 0.635078 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_gated_mixture_knn_logitresid | 0.715018 | 0.811489 | 0.831207 | 0.813132 | 0.682558 | 0.648982 | 0.541999 | 0.675760 |
| joint_residual_pls_knn_logitresid | 0.719039 | 0.805814 | 0.833187 | 0.857126 | 0.682614 | 0.642242 | 0.533836 | 0.678451 |
| joint_target_residual_pls_knn_resid | 0.720795 | 0.799437 | 0.950830 | 0.713085 | 0.781923 | 0.611238 | 0.563948 | 0.625104 |
| joint_neural_mixture_metric_knn_resid | 0.724771 | 0.912797 | 0.822193 | 0.797816 | 0.694770 | 0.645124 | 0.513276 | 0.687423 |
| joint_neural_mixture_metric_knn_logitresid | 0.729273 | 0.834057 | 0.890995 | 0.811786 | 0.668738 | 0.661466 | 0.532762 | 0.705105 |
| joint_neural_gated_mixture_metric_knn_resid | 0.743269 | 0.869187 | 0.862250 | 0.841289 | 0.718660 | 0.647249 | 0.569957 | 0.694291 |
| joint_target_residual_pls_knn_logitresid | 0.747527 | 0.831236 | 0.997860 | 0.751859 | 0.750224 | 0.639938 | 0.573168 | 0.688405 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.751867 | 0.872871 | 0.885043 | 0.845408 | 0.714256 | 0.691080 | 0.557841 | 0.696571 |
| joint_neural_context_attention_knn_logitresid | 0.754534 | 0.835531 | 0.954919 | 0.875705 | 0.671597 | 0.710749 | 0.539497 | 0.693740 |
| joint_neural_context_attention_knn_resid | 0.780906 | 0.883414 | 0.898183 | 0.953412 | 0.696372 | 0.700801 | 0.552568 | 0.781588 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.792016 | 0.903334 | 1.069221 | 0.846624 | 0.706598 | 0.674400 | 0.599745 | 0.744192 |
| joint_target_neural_residual_knn_resid | 0.813275 | 0.896873 | 1.141821 | 0.842802 | 0.687191 | 0.740227 | 0.625444 | 0.758565 |
| joint_neural_context_metric_attention_knn_resid | 0.858515 | 0.981096 | 1.179436 | 1.087473 | 0.695778 | 0.721580 | 0.514967 | 0.829273 |
| joint_neural_context_metric_attention_knn_logitresid | 0.860983 | 0.952869 | 1.162726 | 1.006944 | 0.717662 | 0.767309 | 0.586205 | 0.833168 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.318487 | 8 | 8 | 10 | 0.268392 | 8 | 8 | 10 | 0.386148 | 10 | 0.356780 | 9 | 6261.301270 | 66 | 10 | 0.428606 | 10 | 0.419940 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.294754 | 8 | 8 | 10 | 0.269721 | 8 | 8 | 10 | 0.398581 | 10 | 0.336320 | 9 | 6405.354492 | 66 | 10 | 0.412153 | 10 | 0.393087 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.313100 | 8 | 8 | 10 | 0.252012 | 8 | 8 | 10 | 0.356409 | 10 | 0.331373 | 9 | 6334.762695 | 66 | 10 | 0.398280 | 10 | 0.430880 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.324054 | 8 | 8 | 10 | 0.270092 | 8 | 8 | 10 | 0.390081 | 10 | 0.348925 | 9 | 6488.083008 | 66 | 10 | 0.382356 | 10 | 0.400711 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.347801 | 8 | 8 | 10 | 0.225295 | 8 | 8 | 10 | 0.391801 | 10 | 0.340870 | 9 | 6451.140137 | 66 | 10 | 0.407373 | 10 | 0.426723 |
