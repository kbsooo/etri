# Joint state-space encoder

- Base OOF: `0.482206`
- Best source: `base`
- Best source OOF: `0.482206`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.482206 | 0.526613 | 0.539167 | 0.501873 | 0.470550 | 0.453825 | 0.412963 | 0.470452 |
| joint_proto_mix | 0.496022 | 0.539360 | 0.556046 | 0.520403 | 0.481366 | 0.465740 | 0.426111 | 0.483127 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.506512 | 0.574394 | 0.552028 | 0.534236 | 0.502095 | 0.474780 | 0.426769 | 0.481280 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.515850 | 0.570388 | 0.587825 | 0.539687 | 0.496474 | 0.484817 | 0.430575 | 0.501182 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.515904 | 0.567375 | 0.579495 | 0.541099 | 0.511349 | 0.507098 | 0.423970 | 0.480940 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.516512 | 0.586447 | 0.583684 | 0.546980 | 0.496827 | 0.475008 | 0.429228 | 0.497409 |
| joint_neighbor_logreg | 0.516582 | 0.544441 | 0.574481 | 0.537869 | 0.525939 | 0.493736 | 0.455880 | 0.483725 |
| joint_local_logreg | 0.516892 | 0.545077 | 0.574824 | 0.534446 | 0.523035 | 0.496598 | 0.450990 | 0.493270 |
| joint_metric_neighbor_logreg | 0.521972 | 0.547933 | 0.582280 | 0.549844 | 0.529055 | 0.497305 | 0.456530 | 0.490857 |
| joint_residual_metric_neighbor_logreg | 0.522203 | 0.546624 | 0.583061 | 0.546764 | 0.530335 | 0.496527 | 0.459137 | 0.492973 |
| joint_neighbor_hgb | 0.538748 | 0.576271 | 0.610741 | 0.566932 | 0.502994 | 0.504637 | 0.469673 | 0.539990 |
| joint_metric_neighbor_hgb | 0.545319 | 0.590746 | 0.618064 | 0.579066 | 0.501163 | 0.506592 | 0.473885 | 0.547716 |
| joint_residual_metric_neighbor_hgb | 0.547151 | 0.587319 | 0.611777 | 0.584253 | 0.512470 | 0.509428 | 0.474901 | 0.549913 |
| joint_residual_pls_local_logreg | 0.552404 | 0.607553 | 0.582512 | 0.621906 | 0.562807 | 0.516147 | 0.463782 | 0.512118 |
| joint_residual_pls_neighbor_logreg | 0.552930 | 0.610311 | 0.577160 | 0.621611 | 0.566117 | 0.521193 | 0.464558 | 0.509561 |
| joint_local_hgb | 0.553890 | 0.586087 | 0.636448 | 0.581719 | 0.522653 | 0.522056 | 0.466287 | 0.561981 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.560382 | 0.625794 | 0.633614 | 0.596613 | 0.529713 | 0.513426 | 0.468512 | 0.555004 |
| joint_neural_context_bin_gate_hgb_resid | 0.561059 | 0.631027 | 0.614638 | 0.598026 | 0.531235 | 0.523592 | 0.485277 | 0.543621 |
| joint_cross_family_residual_pls_knn_resid | 0.561948 | 0.616704 | 0.615791 | 0.606723 | 0.548519 | 0.528351 | 0.505718 | 0.511833 |
| joint_residual_contrast_hgb | 0.568277 | 0.592493 | 0.666444 | 0.599809 | 0.537283 | 0.524934 | 0.493672 | 0.563304 |
| joint_residual_pls_neighbor_hgb | 0.572168 | 0.622660 | 0.628918 | 0.634131 | 0.542677 | 0.523589 | 0.475531 | 0.577673 |
| joint_neural_cross_family_residual_knn_resid | 0.577297 | 0.569309 | 0.674804 | 0.616463 | 0.621619 | 0.538028 | 0.440054 | 0.580801 |
| joint_neural_bin_gate_knn_resid | 0.578064 | 0.645578 | 0.676086 | 0.621493 | 0.560669 | 0.532378 | 0.473022 | 0.537223 |
| joint_neural_learned_gate_knn_resid | 0.579614 | 0.649089 | 0.680272 | 0.619266 | 0.558869 | 0.535543 | 0.475816 | 0.538445 |
| joint_residual_pls_local_hgb | 0.582913 | 0.631672 | 0.650495 | 0.650300 | 0.554079 | 0.537659 | 0.480798 | 0.575389 |
| joint_residual_contrast_logreg | 0.585536 | 0.601545 | 0.659244 | 0.621589 | 0.590553 | 0.554819 | 0.502257 | 0.568744 |
| joint_pls_knn_resid | 0.588603 | 0.610032 | 0.685609 | 0.680512 | 0.567438 | 0.546831 | 0.478586 | 0.551213 |
| joint_neural_cross_family_residual_knn_logitresid | 0.589649 | 0.608122 | 0.703197 | 0.625939 | 0.598837 | 0.529407 | 0.473458 | 0.588582 |
| joint_cross_family_residual_pls_knn_logitresid | 0.592218 | 0.646822 | 0.672405 | 0.614039 | 0.591615 | 0.523085 | 0.524108 | 0.573454 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.596162 | 0.691632 | 0.582081 | 0.611879 | 0.567506 | 0.583874 | 0.524285 | 0.611878 |
| joint_residual_metric_knn_resid | 0.596363 | 0.623003 | 0.724975 | 0.662435 | 0.608162 | 0.541301 | 0.473448 | 0.541217 |
| joint_neural_context_bin_gate_logreg_resid | 0.598219 | 0.693607 | 0.665847 | 0.685445 | 0.580949 | 0.556022 | 0.475905 | 0.529755 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.599167 | 0.705320 | 0.666939 | 0.703704 | 0.572745 | 0.563139 | 0.451891 | 0.530430 |
| joint_metric_knn_resid | 0.601080 | 0.624090 | 0.721192 | 0.655795 | 0.584723 | 0.562435 | 0.482510 | 0.576812 |
| joint_neural_s_residual_knn_resid | 0.602034 | 0.569309 | 0.674804 | 0.616463 | 0.653061 | 0.611064 | 0.477908 | 0.611627 |
| joint_s_residual_pls_knn_resid | 0.605209 | 0.616704 | 0.615791 | 0.606723 | 0.678616 | 0.599383 | 0.463230 | 0.656013 |
| joint_attention_knn_resid | 0.607035 | 0.628637 | 0.723186 | 0.690544 | 0.568208 | 0.558093 | 0.507465 | 0.573113 |
| joint_neural_context_gate_hgb_resid | 0.612634 | 0.670094 | 0.691424 | 0.661297 | 0.578634 | 0.591264 | 0.507441 | 0.588281 |
| joint_metric_attention_knn_resid | 0.613944 | 0.648235 | 0.751920 | 0.662394 | 0.600596 | 0.553333 | 0.492744 | 0.588386 |
| joint_neural_context_gate_hgb_logitresid | 0.616053 | 0.674091 | 0.703351 | 0.650150 | 0.579690 | 0.596116 | 0.508776 | 0.600197 |
| joint_neural_multiview_s_residual_knn_resid | 0.617405 | 0.691632 | 0.582081 | 0.611879 | 0.701804 | 0.614348 | 0.501220 | 0.618873 |
| joint_neural_s_residual_knn_logitresid | 0.619009 | 0.608122 | 0.703197 | 0.625939 | 0.648669 | 0.621358 | 0.492016 | 0.633764 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.619652 | 0.714616 | 0.660563 | 0.675799 | 0.565283 | 0.604397 | 0.517887 | 0.599021 |
| joint_q_residual_pls_knn_resid | 0.623708 | 0.738778 | 0.734427 | 0.798328 | 0.548519 | 0.528351 | 0.505718 | 0.511833 |
| joint_proto_neural_multiview_residual_knn_resid | 0.626560 | 0.745721 | 0.643309 | 0.633028 | 0.637582 | 0.609508 | 0.498355 | 0.618417 |
| joint_s_residual_pls_knn_logitresid | 0.628250 | 0.646822 | 0.672405 | 0.614039 | 0.679684 | 0.625348 | 0.500202 | 0.659250 |
| joint_neural_multiview_qs_residual_knn_resid | 0.630920 | 0.713065 | 0.651440 | 0.650295 | 0.614406 | 0.618250 | 0.547549 | 0.621433 |
| joint_panel_neural_multiview_residual_knn_resid | 0.631017 | 0.697590 | 0.716354 | 0.647909 | 0.636611 | 0.565381 | 0.508737 | 0.644537 |
| joint_neural_multiview_q_residual_knn_resid | 0.632247 | 0.723744 | 0.665621 | 0.748821 | 0.567506 | 0.583874 | 0.524285 | 0.611878 |
| joint_pls_knn_logitresid | 0.633257 | 0.678231 | 0.769926 | 0.738436 | 0.582993 | 0.554998 | 0.517408 | 0.590809 |
| joint_proto_neural_residual_knn_resid | 0.633731 | 0.635735 | 0.726775 | 0.831789 | 0.595001 | 0.558254 | 0.530545 | 0.558015 |
| joint_neural_q_residual_knn_resid | 0.635870 | 0.766680 | 0.768812 | 0.735094 | 0.621619 | 0.538028 | 0.440054 | 0.580801 |
| joint_neural_qs_residual_knn_resid | 0.636939 | 0.647494 | 0.683812 | 0.775688 | 0.702451 | 0.595568 | 0.449045 | 0.604517 |
| joint_neural_multiview_residual_knn_resid | 0.637657 | 0.710098 | 0.668750 | 0.721853 | 0.650955 | 0.577750 | 0.489211 | 0.644979 |
| joint_proto_neural_multiview_metric_knn_resid | 0.641753 | 0.766818 | 0.660303 | 0.660372 | 0.657300 | 0.607194 | 0.482880 | 0.657405 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.642763 | 0.714616 | 0.660563 | 0.675799 | 0.645499 | 0.643044 | 0.502670 | 0.657148 |
| joint_neural_residual_knn_resid | 0.643539 | 0.675203 | 0.789435 | 0.681928 | 0.634093 | 0.605263 | 0.530205 | 0.588646 |
| joint_metric_knn_logitresid | 0.644929 | 0.702333 | 0.762562 | 0.716125 | 0.611211 | 0.571097 | 0.525985 | 0.625190 |
| joint_residual_metric_knn_logitresid | 0.646863 | 0.689490 | 0.777851 | 0.732014 | 0.623580 | 0.567212 | 0.513978 | 0.623919 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.649445 | 0.734014 | 0.722727 | 0.738728 | 0.595722 | 0.614890 | 0.510123 | 0.629914 |
| joint_attention_knn_logitresid | 0.652886 | 0.710456 | 0.784155 | 0.762613 | 0.587597 | 0.575409 | 0.538027 | 0.611943 |
| joint_proto_neural_metric_knn_resid | 0.655039 | 0.662718 | 0.755242 | 0.859851 | 0.655777 | 0.538379 | 0.550915 | 0.562393 |
| joint_neural_residual_knn_logitresid | 0.655239 | 0.689011 | 0.861990 | 0.710765 | 0.622111 | 0.581482 | 0.510583 | 0.610733 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.656421 | 0.748215 | 0.750526 | 0.716009 | 0.593622 | 0.625747 | 0.505186 | 0.655644 |
| joint_qs_residual_pls_knn_resid | 0.657664 | 0.721176 | 0.708345 | 0.706249 | 0.693824 | 0.576380 | 0.499740 | 0.697931 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.660546 | 0.753014 | 0.775637 | 0.808580 | 0.565283 | 0.604397 | 0.517887 | 0.599021 |
| joint_neural_multiview_residual_knn_logitresid | 0.661137 | 0.725847 | 0.782726 | 0.727906 | 0.628741 | 0.606886 | 0.509660 | 0.646191 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.661478 | 0.693091 | 0.807376 | 0.688168 | 0.628737 | 0.647862 | 0.514227 | 0.650886 |
| joint_target_neural_multiview_residual_knn_resid | 0.661741 | 0.714447 | 0.680511 | 0.695504 | 0.732854 | 0.659411 | 0.527571 | 0.621892 |
| joint_neural_bin_gate_knn_logitresid | 0.662329 | 0.751748 | 0.790861 | 0.748725 | 0.626850 | 0.622633 | 0.498542 | 0.596942 |
| joint_metric_attention_knn_logitresid | 0.662720 | 0.737388 | 0.773354 | 0.736261 | 0.615135 | 0.587071 | 0.547750 | 0.642082 |
| joint_neural_q_residual_knn_logitresid | 0.662876 | 0.783513 | 0.851489 | 0.814844 | 0.598837 | 0.529407 | 0.473458 | 0.588582 |
| joint_q_residual_pls_knn_logitresid | 0.663918 | 0.790115 | 0.828280 | 0.816769 | 0.591615 | 0.523085 | 0.524108 | 0.573454 |
| joint_neural_learned_gate_knn_logitresid | 0.664416 | 0.755076 | 0.804327 | 0.740786 | 0.623458 | 0.623281 | 0.507030 | 0.596955 |
| joint_panel_neural_residual_knn_resid | 0.666553 | 0.784863 | 0.821556 | 0.725945 | 0.638737 | 0.580021 | 0.522471 | 0.592276 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.666822 | 0.748484 | 0.765389 | 0.715873 | 0.607760 | 0.652891 | 0.509085 | 0.668269 |
| joint_family_residual_pls_knn_resid | 0.666968 | 0.738778 | 0.734427 | 0.798328 | 0.678616 | 0.599383 | 0.463230 | 0.656013 |
| joint_target_qs_residual_pls_knn_resid | 0.667839 | 0.723794 | 0.747604 | 0.723870 | 0.696391 | 0.577154 | 0.509781 | 0.696280 |
| joint_neural_qs_residual_knn_logitresid | 0.668768 | 0.694046 | 0.808150 | 0.815548 | 0.636256 | 0.604374 | 0.488691 | 0.634309 |
| joint_qs_residual_pls_knn_logitresid | 0.670665 | 0.740042 | 0.802106 | 0.720759 | 0.662597 | 0.588905 | 0.509005 | 0.671245 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.672020 | 0.718843 | 0.740205 | 0.783026 | 0.653951 | 0.646400 | 0.504296 | 0.657420 |
| joint_proto_neural_residual_knn_logitresid | 0.677122 | 0.708575 | 0.815741 | 0.792262 | 0.630275 | 0.623302 | 0.564060 | 0.605637 |
| joint_residual_pls_knn_resid | 0.681760 | 0.668134 | 0.729568 | 0.832795 | 0.697611 | 0.658790 | 0.513642 | 0.671783 |
| joint_neural_mixture_knn_resid | 0.684283 | 0.769189 | 0.768844 | 0.778737 | 0.687987 | 0.648713 | 0.477489 | 0.659025 |
| joint_target_qs_residual_pls_knn_logitresid | 0.685572 | 0.748099 | 0.840058 | 0.724458 | 0.674014 | 0.598923 | 0.524789 | 0.688661 |
| joint_neural_mixture_knn_logitresid | 0.690012 | 0.768454 | 0.852879 | 0.788085 | 0.640338 | 0.618467 | 0.515467 | 0.646395 |
| joint_panel_neural_residual_knn_logitresid | 0.698908 | 0.842432 | 0.882829 | 0.746931 | 0.680546 | 0.597952 | 0.530886 | 0.610782 |
| joint_family_residual_pls_knn_logitresid | 0.699950 | 0.790115 | 0.828280 | 0.816769 | 0.679684 | 0.625348 | 0.500202 | 0.659250 |
| joint_proto_neural_metric_knn_logitresid | 0.700599 | 0.717564 | 0.861417 | 0.841419 | 0.658484 | 0.619996 | 0.592982 | 0.612331 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_residual_pls_knn_logitresid | 0.708759 | 0.785469 | 0.820312 | 0.847633 | 0.676230 | 0.630749 | 0.525391 | 0.675529 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_context_gate_logreg_resid | 0.713943 | 0.901419 | 0.870354 | 0.832599 | 0.682220 | 0.644016 | 0.494662 | 0.572333 |
| joint_neural_context_gate_logreg_logitresid | 0.719060 | 0.849127 | 0.872300 | 0.853145 | 0.697530 | 0.669936 | 0.499257 | 0.592126 |
| joint_neural_gated_mixture_knn_logitresid | 0.723374 | 0.810910 | 0.885334 | 0.814648 | 0.679689 | 0.663786 | 0.541752 | 0.667502 |
| joint_neural_gated_mixture_knn_resid | 0.731539 | 0.823391 | 0.870050 | 0.841178 | 0.773814 | 0.658146 | 0.518560 | 0.635636 |
| joint_target_residual_pls_knn_resid | 0.732793 | 0.793579 | 0.957646 | 0.705127 | 0.817368 | 0.606863 | 0.588424 | 0.660547 |
| joint_target_residual_pls_knn_logitresid | 0.740191 | 0.786568 | 1.001224 | 0.753522 | 0.738291 | 0.633649 | 0.570996 | 0.697086 |
| joint_neural_mixture_metric_knn_logitresid | 0.747343 | 0.838901 | 0.906098 | 0.867577 | 0.671586 | 0.703276 | 0.558146 | 0.685814 |
| joint_neural_mixture_metric_knn_resid | 0.751030 | 0.884190 | 0.827193 | 0.866103 | 0.739654 | 0.739556 | 0.516292 | 0.684223 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.779659 | 0.908124 | 0.942862 | 0.868657 | 0.732223 | 0.744017 | 0.569592 | 0.692140 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_neural_gated_mixture_metric_knn_resid | 0.793414 | 0.954051 | 0.905377 | 0.888540 | 0.843328 | 0.736587 | 0.533219 | 0.692798 |
| joint_target_neural_residual_knn_logitresid | 0.829173 | 0.994260 | 1.058213 | 0.927467 | 0.752126 | 0.765835 | 0.590186 | 0.716121 |
| joint_target_neural_residual_knn_resid | 0.852040 | 1.037663 | 1.127727 | 0.965324 | 0.802358 | 0.770442 | 0.554843 | 0.705921 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.303024 | 8 | 8 | 10 | 0.275683 | 8 | 8 | 10 | 0.376327 | 10 | 0.386578 | 9 | 6262.456055 | 66 | 10 | 0.424052 | 10 | 0.442178 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.296372 | 8 | 8 | 10 | 0.280335 | 8 | 8 | 10 | 0.395031 | 10 | 0.362986 | 9 | 6422.349121 | 66 | 10 | 0.391038 | 10 | 0.397977 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.307476 | 8 | 8 | 10 | 0.251854 | 8 | 8 | 10 | 0.373402 | 10 | 0.317595 | 9 | 6354.659180 | 66 | 10 | 0.410917 | 10 | 0.414779 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.341401 | 8 | 8 | 10 | 0.261007 | 8 | 8 | 10 | 0.370303 | 10 | 0.348397 | 9 | 6461.073730 | 66 | 10 | 0.404462 | 10 | 0.394968 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.299234 | 8 | 8 | 10 | 0.202213 | 8 | 8 | 10 | 0.385563 | 10 | 0.325140 | 9 | 6450.119141 | 66 | 10 | 0.411139 | 10 | 0.414839 |
