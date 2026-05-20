# Joint state-space encoder

- Base OOF: `0.485258`
- Best source: `base`
- Best source OOF: `0.485258`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.485258 | 0.530257 | 0.541065 | 0.504545 | 0.475179 | 0.457025 | 0.416664 | 0.472072 |
| joint_proto_mix | 0.498732 | 0.542671 | 0.557699 | 0.522833 | 0.485566 | 0.468891 | 0.429166 | 0.484301 |
| joint_local_logreg | 0.519934 | 0.548956 | 0.576305 | 0.537153 | 0.527475 | 0.501127 | 0.454569 | 0.493953 |
| joint_neighbor_logreg | 0.520031 | 0.548593 | 0.576980 | 0.541689 | 0.530181 | 0.498489 | 0.459266 | 0.485020 |
| joint_residual_metric_neighbor_logreg | 0.525048 | 0.550048 | 0.585051 | 0.551384 | 0.534475 | 0.499105 | 0.461947 | 0.493326 |
| joint_metric_neighbor_logreg | 0.525539 | 0.553409 | 0.584258 | 0.554358 | 0.532267 | 0.502384 | 0.460181 | 0.491917 |
| joint_neighbor_hgb | 0.541187 | 0.584963 | 0.605554 | 0.577292 | 0.513314 | 0.497987 | 0.467082 | 0.542113 |
| joint_residual_metric_neighbor_hgb | 0.547009 | 0.591663 | 0.600559 | 0.579075 | 0.523960 | 0.508392 | 0.478730 | 0.546684 |
| joint_metric_neighbor_hgb | 0.548194 | 0.596064 | 0.609176 | 0.581693 | 0.510037 | 0.509030 | 0.474578 | 0.556779 |
| joint_cross_family_residual_pls_knn_resid | 0.549396 | 0.612529 | 0.582394 | 0.589932 | 0.548761 | 0.514069 | 0.474620 | 0.523470 |
| joint_residual_pls_local_logreg | 0.549755 | 0.599889 | 0.588904 | 0.624275 | 0.550461 | 0.513341 | 0.466091 | 0.505327 |
| joint_residual_pls_neighbor_logreg | 0.550350 | 0.601744 | 0.581562 | 0.624444 | 0.556253 | 0.519798 | 0.466654 | 0.501996 |
| joint_local_hgb | 0.554199 | 0.585064 | 0.625952 | 0.591036 | 0.535792 | 0.514916 | 0.465551 | 0.561080 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.560303 | 0.646855 | 0.627224 | 0.564972 | 0.520323 | 0.515066 | 0.494942 | 0.552737 |
| joint_residual_pls_neighbor_hgb | 0.564701 | 0.622149 | 0.619366 | 0.621191 | 0.529483 | 0.526469 | 0.479480 | 0.554766 |
| joint_neural_learned_gate_knn_resid | 0.566600 | 0.636277 | 0.645739 | 0.590701 | 0.538810 | 0.534937 | 0.474699 | 0.545037 |
| joint_residual_contrast_hgb | 0.569588 | 0.605053 | 0.653013 | 0.608350 | 0.546226 | 0.525438 | 0.486415 | 0.562620 |
| joint_neural_cross_family_residual_knn_resid | 0.570721 | 0.591381 | 0.647121 | 0.601240 | 0.567276 | 0.494785 | 0.522301 | 0.570941 |
| joint_residual_pls_local_hgb | 0.577345 | 0.629279 | 0.638246 | 0.642310 | 0.561005 | 0.532464 | 0.479242 | 0.558867 |
| joint_neural_q_residual_knn_resid | 0.580823 | 0.653691 | 0.615659 | 0.641105 | 0.567276 | 0.494785 | 0.522301 | 0.570941 |
| joint_cross_family_residual_pls_knn_logitresid | 0.581279 | 0.639623 | 0.660041 | 0.623791 | 0.576926 | 0.527779 | 0.491617 | 0.549175 |
| joint_neural_residual_knn_resid | 0.581837 | 0.654723 | 0.677596 | 0.670079 | 0.544605 | 0.522759 | 0.477680 | 0.525418 |
| joint_pls_knn_resid | 0.587176 | 0.607104 | 0.684415 | 0.670809 | 0.569169 | 0.545722 | 0.482958 | 0.550054 |
| joint_neural_qs_residual_knn_resid | 0.587291 | 0.614119 | 0.666769 | 0.637909 | 0.603078 | 0.520220 | 0.482997 | 0.585943 |
| joint_residual_contrast_logreg | 0.588560 | 0.603765 | 0.665539 | 0.624807 | 0.593974 | 0.553286 | 0.509048 | 0.569503 |
| joint_neural_s_residual_knn_resid | 0.589820 | 0.591381 | 0.647121 | 0.601240 | 0.641606 | 0.551331 | 0.536657 | 0.559405 |
| joint_panel_neural_multiview_residual_knn_resid | 0.591371 | 0.661520 | 0.651564 | 0.643530 | 0.571133 | 0.571978 | 0.488198 | 0.551672 |
| joint_proto_neural_multiview_residual_knn_resid | 0.596064 | 0.714571 | 0.619698 | 0.647877 | 0.587884 | 0.529053 | 0.487197 | 0.586166 |
| joint_metric_knn_resid | 0.597503 | 0.619895 | 0.716367 | 0.643770 | 0.573076 | 0.552374 | 0.484369 | 0.592672 |
| joint_neural_cross_family_residual_knn_logitresid | 0.597615 | 0.686534 | 0.705197 | 0.603343 | 0.555976 | 0.539792 | 0.492712 | 0.599753 |
| joint_residual_metric_knn_resid | 0.598414 | 0.619813 | 0.709998 | 0.666276 | 0.588709 | 0.544068 | 0.501545 | 0.558491 |
| joint_neural_multiview_q_residual_knn_resid | 0.599880 | 0.675977 | 0.689578 | 0.750537 | 0.520323 | 0.515066 | 0.494942 | 0.552737 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.601253 | 0.688857 | 0.671377 | 0.660647 | 0.545945 | 0.550706 | 0.509000 | 0.582237 |
| joint_s_residual_pls_knn_resid | 0.604301 | 0.612529 | 0.582394 | 0.589932 | 0.686429 | 0.632349 | 0.459639 | 0.666837 |
| joint_metric_attention_knn_resid | 0.606260 | 0.639021 | 0.741537 | 0.652689 | 0.571630 | 0.556316 | 0.495871 | 0.586752 |
| joint_attention_knn_resid | 0.607046 | 0.623286 | 0.725761 | 0.691989 | 0.570398 | 0.555760 | 0.508229 | 0.573895 |
| joint_neural_multiview_qs_residual_knn_resid | 0.607342 | 0.710555 | 0.628863 | 0.629686 | 0.573139 | 0.554555 | 0.538574 | 0.616021 |
| joint_neural_multiview_s_residual_knn_resid | 0.611105 | 0.646855 | 0.627224 | 0.564972 | 0.636086 | 0.659725 | 0.492268 | 0.650607 |
| joint_q_residual_pls_knn_resid | 0.611155 | 0.678335 | 0.705755 | 0.833072 | 0.548761 | 0.514069 | 0.474620 | 0.523470 |
| joint_neural_residual_knn_logitresid | 0.613084 | 0.696434 | 0.730929 | 0.690961 | 0.557630 | 0.561532 | 0.504287 | 0.549817 |
| joint_proto_neural_residual_knn_resid | 0.614845 | 0.689264 | 0.666996 | 0.659532 | 0.632699 | 0.542020 | 0.510792 | 0.602614 |
| joint_neural_multiview_residual_knn_resid | 0.616350 | 0.647314 | 0.679911 | 0.699804 | 0.596009 | 0.580549 | 0.546333 | 0.564533 |
| joint_proto_neural_multiview_metric_knn_resid | 0.616616 | 0.705802 | 0.671969 | 0.683412 | 0.587455 | 0.558597 | 0.483398 | 0.625680 |
| joint_neural_q_residual_knn_logitresid | 0.618490 | 0.704521 | 0.714019 | 0.722655 | 0.555976 | 0.539792 | 0.492712 | 0.599753 |
| joint_neural_qs_residual_knn_logitresid | 0.624009 | 0.685703 | 0.716274 | 0.670803 | 0.600646 | 0.581838 | 0.507928 | 0.604874 |
| joint_s_residual_pls_knn_logitresid | 0.628495 | 0.639623 | 0.660041 | 0.623791 | 0.674387 | 0.643579 | 0.488482 | 0.669559 |
| joint_neural_s_residual_knn_logitresid | 0.629563 | 0.686534 | 0.705197 | 0.603343 | 0.637699 | 0.607266 | 0.527334 | 0.639566 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.634357 | 0.724108 | 0.727303 | 0.703219 | 0.580846 | 0.575935 | 0.510644 | 0.618445 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.634572 | 0.688857 | 0.671377 | 0.660647 | 0.617127 | 0.641229 | 0.504327 | 0.658443 |
| joint_pls_knn_logitresid | 0.635054 | 0.680140 | 0.772229 | 0.739537 | 0.587369 | 0.562691 | 0.515470 | 0.587945 |
| joint_target_neural_multiview_residual_knn_resid | 0.638759 | 0.754410 | 0.684038 | 0.655417 | 0.721701 | 0.567589 | 0.483931 | 0.604224 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.641687 | 0.738281 | 0.784173 | 0.781467 | 0.545945 | 0.550706 | 0.509000 | 0.582237 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.642228 | 0.746200 | 0.723708 | 0.715954 | 0.593607 | 0.599182 | 0.510142 | 0.606804 |
| joint_neural_mixture_knn_resid | 0.644782 | 0.685906 | 0.718142 | 0.774737 | 0.636136 | 0.609807 | 0.495270 | 0.593478 |
| joint_qs_residual_pls_knn_resid | 0.645248 | 0.705917 | 0.710825 | 0.714593 | 0.665450 | 0.607025 | 0.477900 | 0.635026 |
| joint_neural_learned_gate_knn_logitresid | 0.646370 | 0.735924 | 0.760396 | 0.710999 | 0.598619 | 0.618872 | 0.491357 | 0.608423 |
| joint_metric_knn_logitresid | 0.646841 | 0.706686 | 0.762949 | 0.718649 | 0.615623 | 0.578442 | 0.523265 | 0.622270 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.648389 | 0.699335 | 0.766159 | 0.724727 | 0.600525 | 0.632425 | 0.509263 | 0.606290 |
| joint_residual_metric_knn_logitresid | 0.650614 | 0.700426 | 0.779679 | 0.734794 | 0.618482 | 0.576669 | 0.522805 | 0.621443 |
| joint_proto_neural_metric_knn_resid | 0.651927 | 0.705065 | 0.716442 | 0.708660 | 0.719378 | 0.558821 | 0.524356 | 0.630769 |
| joint_residual_pls_knn_resid | 0.653382 | 0.646579 | 0.703645 | 0.766878 | 0.668142 | 0.623555 | 0.538105 | 0.626771 |
| joint_neural_multiview_residual_knn_logitresid | 0.653606 | 0.715965 | 0.796608 | 0.739684 | 0.585194 | 0.624160 | 0.513502 | 0.600127 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.654350 | 0.744922 | 0.749821 | 0.741994 | 0.599494 | 0.611527 | 0.519157 | 0.613537 |
| joint_attention_knn_logitresid | 0.654433 | 0.710671 | 0.787282 | 0.763247 | 0.590969 | 0.582934 | 0.536370 | 0.609555 |
| joint_target_qs_residual_pls_knn_resid | 0.657856 | 0.712259 | 0.772068 | 0.740975 | 0.663431 | 0.620913 | 0.491363 | 0.603984 |
| joint_q_residual_pls_knn_logitresid | 0.663521 | 0.813080 | 0.846183 | 0.839884 | 0.576926 | 0.527779 | 0.491617 | 0.549175 |
| joint_metric_attention_knn_logitresid | 0.664282 | 0.740000 | 0.774105 | 0.738079 | 0.618668 | 0.594289 | 0.545321 | 0.639508 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.664351 | 0.765694 | 0.753850 | 0.739650 | 0.646449 | 0.617053 | 0.490513 | 0.637249 |
| joint_family_residual_pls_knn_resid | 0.666060 | 0.678335 | 0.705755 | 0.833072 | 0.686429 | 0.632349 | 0.459639 | 0.666837 |
| joint_panel_neural_residual_knn_resid | 0.666749 | 0.790208 | 0.818323 | 0.720863 | 0.650759 | 0.577774 | 0.495672 | 0.613640 |
| joint_neural_mixture_knn_logitresid | 0.668567 | 0.734090 | 0.800645 | 0.769469 | 0.636998 | 0.614235 | 0.508481 | 0.616054 |
| joint_qs_residual_pls_knn_logitresid | 0.671549 | 0.747270 | 0.797444 | 0.754303 | 0.650792 | 0.604027 | 0.498713 | 0.648295 |
| joint_neural_gated_mixture_knn_resid | 0.674415 | 0.680137 | 0.820435 | 0.782509 | 0.643334 | 0.666867 | 0.505941 | 0.621684 |
| joint_proto_neural_residual_knn_logitresid | 0.675570 | 0.818854 | 0.762259 | 0.724691 | 0.643100 | 0.588944 | 0.544780 | 0.646363 |
| joint_target_qs_residual_pls_knn_logitresid | 0.681853 | 0.758512 | 0.824663 | 0.754870 | 0.658482 | 0.605595 | 0.509883 | 0.660964 |
| joint_neural_mixture_metric_knn_resid | 0.686872 | 0.721337 | 0.761018 | 0.783572 | 0.702151 | 0.651235 | 0.535881 | 0.652911 |
| joint_residual_pls_knn_logitresid | 0.689086 | 0.769984 | 0.800468 | 0.834637 | 0.643841 | 0.611939 | 0.525326 | 0.637410 |
| joint_proto_neural_metric_knn_logitresid | 0.699654 | 0.834021 | 0.818932 | 0.754267 | 0.674378 | 0.606921 | 0.545522 | 0.663540 |
| joint_panel_neural_residual_knn_logitresid | 0.700507 | 0.866386 | 0.850834 | 0.794682 | 0.677403 | 0.619353 | 0.507358 | 0.587534 |
| joint_neural_mixture_metric_knn_logitresid | 0.703050 | 0.787075 | 0.840888 | 0.793467 | 0.668727 | 0.642344 | 0.539406 | 0.649446 |
| joint_neural_gated_mixture_knn_logitresid | 0.703923 | 0.767413 | 0.839911 | 0.808253 | 0.658619 | 0.656464 | 0.540433 | 0.656369 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_family_residual_pls_knn_logitresid | 0.710736 | 0.813080 | 0.846183 | 0.839884 | 0.674387 | 0.643579 | 0.488482 | 0.669559 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_gated_mixture_metric_knn_resid | 0.713719 | 0.754879 | 0.802880 | 0.804820 | 0.671712 | 0.681778 | 0.567363 | 0.712604 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.743390 | 0.827408 | 0.892306 | 0.850509 | 0.678189 | 0.699568 | 0.566198 | 0.689553 |
| joint_target_residual_pls_knn_resid | 0.744607 | 0.811835 | 1.086223 | 0.705143 | 0.842549 | 0.561666 | 0.553150 | 0.651685 |
| joint_target_residual_pls_knn_logitresid | 0.751082 | 0.813733 | 1.039079 | 0.757300 | 0.750201 | 0.596021 | 0.569258 | 0.731983 |
| joint_target_neural_residual_knn_resid | 0.764417 | 0.846254 | 0.889435 | 0.832972 | 0.707430 | 0.790224 | 0.597239 | 0.687363 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.796393 | 0.959718 | 1.057140 | 0.842939 | 0.703232 | 0.748946 | 0.594522 | 0.668254 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.331604 | 8 | 8 | 10 | 0.266708 | 8 | 8 | 10 | 0.381838 | 10 | 0.379127 | 9 | 6224.385742 | 66 | 10 | 0.421348 | 10 | 0.439612 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.344216 | 8 | 8 | 10 | 0.265786 | 8 | 8 | 10 | 0.387745 | 10 | 0.346401 | 9 | 6512.827148 | 66 | 10 | 0.405714 | 10 | 0.392921 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.314560 | 8 | 8 | 10 | 0.256616 | 8 | 8 | 10 | 0.377743 | 10 | 0.347846 | 9 | 6318.682617 | 66 | 10 | 0.423403 | 10 | 0.421830 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.338737 | 8 | 8 | 10 | 0.266001 | 8 | 8 | 10 | 0.399591 | 10 | 0.379469 | 9 | 6480.439453 | 66 | 10 | 0.400218 | 10 | 0.399460 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.317552 | 8 | 8 | 10 | 0.235620 | 8 | 8 | 10 | 0.385101 | 10 | 0.338631 | 9 | 6419.146973 | 66 | 10 | 0.413799 | 10 | 0.420745 |
