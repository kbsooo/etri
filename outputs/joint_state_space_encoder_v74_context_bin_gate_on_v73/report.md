# Joint state-space encoder

- Base OOF: `0.483097`
- Best source: `base`
- Best source OOF: `0.483097`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.483097 | 0.526868 | 0.539350 | 0.502451 | 0.472410 | 0.455589 | 0.414280 | 0.470727 |
| joint_proto_mix | 0.496853 | 0.539612 | 0.556178 | 0.520966 | 0.483272 | 0.467440 | 0.427118 | 0.483387 |
| joint_neighbor_logreg | 0.517352 | 0.544705 | 0.574480 | 0.538614 | 0.526862 | 0.496395 | 0.456476 | 0.483928 |
| joint_local_logreg | 0.517635 | 0.545252 | 0.574873 | 0.534875 | 0.524530 | 0.498893 | 0.451526 | 0.493497 |
| joint_metric_neighbor_logreg | 0.522716 | 0.548157 | 0.582280 | 0.550903 | 0.529043 | 0.500421 | 0.457183 | 0.491026 |
| joint_residual_metric_neighbor_logreg | 0.522813 | 0.546549 | 0.583045 | 0.547866 | 0.530081 | 0.499723 | 0.459466 | 0.492961 |
| joint_neighbor_hgb | 0.538429 | 0.572606 | 0.610600 | 0.567661 | 0.510156 | 0.499285 | 0.467963 | 0.540728 |
| joint_metric_neighbor_hgb | 0.545544 | 0.588020 | 0.616335 | 0.576052 | 0.507865 | 0.504743 | 0.475302 | 0.550491 |
| joint_residual_metric_neighbor_hgb | 0.547138 | 0.579759 | 0.617420 | 0.581653 | 0.509868 | 0.508175 | 0.479026 | 0.554065 |
| joint_residual_pls_local_logreg | 0.551812 | 0.604310 | 0.585650 | 0.623278 | 0.559507 | 0.514475 | 0.466956 | 0.508506 |
| joint_neural_cross_family_residual_knn_resid | 0.552110 | 0.569371 | 0.611419 | 0.597371 | 0.573763 | 0.507353 | 0.467300 | 0.538195 |
| joint_residual_pls_neighbor_logreg | 0.553534 | 0.607043 | 0.581374 | 0.627744 | 0.562964 | 0.523292 | 0.467134 | 0.505190 |
| joint_local_hgb | 0.555494 | 0.587743 | 0.639424 | 0.583729 | 0.529144 | 0.515871 | 0.466763 | 0.565784 |
| joint_neural_context_bin_gate_hgb_resid | 0.560282 | 0.610173 | 0.651297 | 0.602885 | 0.537485 | 0.511601 | 0.472496 | 0.536036 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.565346 | 0.614652 | 0.659155 | 0.593777 | 0.537597 | 0.512896 | 0.491822 | 0.547526 |
| joint_cross_family_residual_pls_knn_resid | 0.567971 | 0.616201 | 0.628294 | 0.621297 | 0.555091 | 0.536253 | 0.502075 | 0.516589 |
| joint_residual_contrast_hgb | 0.569301 | 0.592284 | 0.667831 | 0.598868 | 0.545544 | 0.524898 | 0.489989 | 0.565690 |
| joint_residual_pls_neighbor_hgb | 0.571015 | 0.624699 | 0.622916 | 0.632580 | 0.547983 | 0.531542 | 0.478768 | 0.558619 |
| joint_neural_learned_gate_knn_resid | 0.572598 | 0.654222 | 0.660693 | 0.609336 | 0.550188 | 0.510542 | 0.462904 | 0.560303 |
| joint_neural_bin_gate_knn_resid | 0.572671 | 0.652663 | 0.660504 | 0.607105 | 0.555262 | 0.509513 | 0.462013 | 0.561638 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.574626 | 0.647897 | 0.599916 | 0.603991 | 0.541504 | 0.564870 | 0.501747 | 0.562456 |
| joint_residual_pls_local_hgb | 0.581301 | 0.630438 | 0.641746 | 0.641348 | 0.562008 | 0.540666 | 0.479615 | 0.573289 |
| joint_neural_s_residual_knn_resid | 0.584278 | 0.569371 | 0.611419 | 0.597371 | 0.644827 | 0.532408 | 0.513407 | 0.621143 |
| joint_residual_contrast_logreg | 0.585418 | 0.600552 | 0.659463 | 0.622823 | 0.589343 | 0.552208 | 0.504379 | 0.569158 |
| joint_neural_cross_family_residual_knn_logitresid | 0.588967 | 0.621251 | 0.673104 | 0.633276 | 0.590705 | 0.546120 | 0.482152 | 0.576164 |
| joint_pls_knn_resid | 0.589163 | 0.610501 | 0.686032 | 0.681306 | 0.559065 | 0.545499 | 0.478149 | 0.563588 |
| joint_neural_context_bin_gate_logreg_resid | 0.592818 | 0.681822 | 0.740044 | 0.654022 | 0.574614 | 0.516319 | 0.458768 | 0.524135 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.593359 | 0.678688 | 0.707803 | 0.670120 | 0.588277 | 0.523978 | 0.457697 | 0.526952 |
| joint_cross_family_residual_pls_knn_logitresid | 0.596546 | 0.656414 | 0.675174 | 0.618306 | 0.593255 | 0.537965 | 0.518205 | 0.576505 |
| joint_residual_metric_knn_resid | 0.599215 | 0.618228 | 0.724860 | 0.681582 | 0.588373 | 0.542530 | 0.496925 | 0.542010 |
| joint_neural_multiview_s_residual_knn_resid | 0.600077 | 0.647897 | 0.599916 | 0.603991 | 0.621858 | 0.601069 | 0.492535 | 0.633272 |
| joint_panel_neural_multiview_residual_knn_resid | 0.601130 | 0.700901 | 0.644184 | 0.594773 | 0.594463 | 0.581848 | 0.497891 | 0.593854 |
| joint_metric_knn_resid | 0.601392 | 0.624491 | 0.721098 | 0.656579 | 0.584028 | 0.563526 | 0.482086 | 0.577933 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.604001 | 0.672732 | 0.673056 | 0.653074 | 0.565560 | 0.569321 | 0.505629 | 0.588635 |
| joint_attention_knn_resid | 0.605466 | 0.628940 | 0.723096 | 0.690810 | 0.558046 | 0.556454 | 0.506870 | 0.574046 |
| joint_neural_s_residual_knn_logitresid | 0.606226 | 0.621251 | 0.673104 | 0.633276 | 0.623615 | 0.593741 | 0.497469 | 0.601126 |
| joint_s_residual_pls_knn_resid | 0.608112 | 0.616201 | 0.628294 | 0.621297 | 0.669345 | 0.626744 | 0.459415 | 0.635491 |
| joint_neural_context_gate_hgb_resid | 0.608889 | 0.674319 | 0.709533 | 0.642804 | 0.598800 | 0.552984 | 0.502145 | 0.581636 |
| joint_neural_residual_knn_resid | 0.609421 | 0.652287 | 0.700163 | 0.678344 | 0.554245 | 0.525570 | 0.511048 | 0.644292 |
| joint_metric_attention_knn_resid | 0.609959 | 0.648322 | 0.751365 | 0.663063 | 0.569742 | 0.554233 | 0.492344 | 0.590646 |
| joint_neural_context_gate_hgb_logitresid | 0.614551 | 0.674525 | 0.704208 | 0.656401 | 0.604787 | 0.565576 | 0.508641 | 0.587720 |
| joint_neural_multiview_residual_knn_resid | 0.614983 | 0.730828 | 0.647026 | 0.666106 | 0.595768 | 0.581543 | 0.487873 | 0.595738 |
| joint_neural_q_residual_knn_resid | 0.617276 | 0.823687 | 0.710922 | 0.699712 | 0.573763 | 0.507353 | 0.467300 | 0.538195 |
| joint_proto_neural_multiview_residual_knn_resid | 0.617298 | 0.727311 | 0.643913 | 0.650928 | 0.615956 | 0.548198 | 0.514125 | 0.620654 |
| joint_neural_multiview_qs_residual_knn_resid | 0.620583 | 0.735444 | 0.658557 | 0.679262 | 0.583557 | 0.562939 | 0.486571 | 0.637753 |
| joint_neural_qs_residual_knn_resid | 0.624206 | 0.698163 | 0.751032 | 0.683840 | 0.614153 | 0.559072 | 0.498311 | 0.564873 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.625238 | 0.672732 | 0.673056 | 0.653074 | 0.632805 | 0.625469 | 0.467560 | 0.651973 |
| joint_q_residual_pls_knn_resid | 0.628448 | 0.739107 | 0.735004 | 0.815017 | 0.555091 | 0.536253 | 0.502075 | 0.516589 |
| joint_s_residual_pls_knn_logitresid | 0.629950 | 0.656414 | 0.675174 | 0.618306 | 0.674313 | 0.631737 | 0.496754 | 0.656950 |
| joint_neural_multiview_q_residual_knn_resid | 0.633470 | 0.716912 | 0.703461 | 0.843336 | 0.541504 | 0.564870 | 0.501747 | 0.562456 |
| joint_pls_knn_logitresid | 0.634685 | 0.678915 | 0.770132 | 0.740460 | 0.586994 | 0.560361 | 0.515168 | 0.590767 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.637291 | 0.749193 | 0.716706 | 0.666069 | 0.587686 | 0.606764 | 0.528660 | 0.605962 |
| joint_neural_residual_knn_logitresid | 0.637820 | 0.698187 | 0.784055 | 0.691887 | 0.582662 | 0.568602 | 0.502373 | 0.636971 |
| joint_proto_neural_multiview_metric_knn_resid | 0.638177 | 0.756095 | 0.677149 | 0.666901 | 0.624787 | 0.610695 | 0.527776 | 0.603837 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.641385 | 0.714073 | 0.745441 | 0.723265 | 0.595805 | 0.590200 | 0.480193 | 0.640721 |
| joint_neural_qs_residual_knn_logitresid | 0.643793 | 0.704340 | 0.792510 | 0.737367 | 0.601456 | 0.569579 | 0.481834 | 0.619464 |
| joint_metric_knn_logitresid | 0.646398 | 0.703035 | 0.762839 | 0.718623 | 0.615730 | 0.575803 | 0.523451 | 0.625308 |
| joint_residual_metric_knn_logitresid | 0.647406 | 0.686742 | 0.778006 | 0.732666 | 0.619254 | 0.571490 | 0.519013 | 0.624676 |
| joint_target_neural_multiview_residual_knn_resid | 0.647572 | 0.706098 | 0.725577 | 0.756555 | 0.687252 | 0.595930 | 0.488788 | 0.572803 |
| joint_neural_q_residual_knn_logitresid | 0.649281 | 0.790703 | 0.791671 | 0.767453 | 0.590705 | 0.546120 | 0.482152 | 0.576164 |
| joint_neural_bin_gate_knn_logitresid | 0.651554 | 0.752381 | 0.785941 | 0.716524 | 0.632765 | 0.572432 | 0.498627 | 0.602211 |
| joint_qs_residual_pls_knn_resid | 0.651796 | 0.719177 | 0.712143 | 0.724458 | 0.676097 | 0.565858 | 0.499717 | 0.665124 |
| joint_neural_learned_gate_knn_logitresid | 0.652642 | 0.748065 | 0.783807 | 0.727665 | 0.618390 | 0.575413 | 0.498560 | 0.616593 |
| joint_attention_knn_logitresid | 0.654377 | 0.711116 | 0.784572 | 0.765132 | 0.591137 | 0.580572 | 0.536028 | 0.612082 |
| joint_neural_multiview_residual_knn_logitresid | 0.655953 | 0.773269 | 0.731621 | 0.714852 | 0.619781 | 0.613405 | 0.512719 | 0.626026 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.656299 | 0.748001 | 0.809551 | 0.807397 | 0.565560 | 0.569321 | 0.505629 | 0.588635 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.658573 | 0.722242 | 0.750943 | 0.743777 | 0.628547 | 0.592134 | 0.542601 | 0.629768 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.663097 | 0.709286 | 0.775273 | 0.764060 | 0.639732 | 0.644896 | 0.501270 | 0.607164 |
| joint_target_qs_residual_pls_knn_resid | 0.663808 | 0.699061 | 0.762811 | 0.739509 | 0.663620 | 0.604893 | 0.507213 | 0.669552 |
| joint_metric_attention_knn_logitresid | 0.664246 | 0.738075 | 0.773809 | 0.739154 | 0.619179 | 0.591677 | 0.545480 | 0.642352 |
| joint_q_residual_pls_knn_logitresid | 0.666920 | 0.782768 | 0.826200 | 0.833539 | 0.593255 | 0.537965 | 0.518205 | 0.576505 |
| joint_family_residual_pls_knn_resid | 0.668589 | 0.739107 | 0.735004 | 0.815017 | 0.669345 | 0.626744 | 0.459415 | 0.635491 |
| joint_neural_mixture_knn_resid | 0.670481 | 0.816407 | 0.765496 | 0.756351 | 0.631675 | 0.598209 | 0.493075 | 0.632157 |
| joint_qs_residual_pls_knn_logitresid | 0.671973 | 0.735708 | 0.808679 | 0.731502 | 0.657238 | 0.596699 | 0.505453 | 0.668531 |
| joint_residual_pls_knn_resid | 0.673638 | 0.651799 | 0.743754 | 0.816807 | 0.681217 | 0.659580 | 0.513285 | 0.649021 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.673816 | 0.747744 | 0.791130 | 0.759418 | 0.621037 | 0.619691 | 0.544440 | 0.633250 |
| joint_proto_neural_residual_knn_resid | 0.675057 | 0.722677 | 0.855340 | 0.762815 | 0.621821 | 0.606079 | 0.498553 | 0.658114 |
| joint_neural_mixture_knn_logitresid | 0.683675 | 0.768769 | 0.833382 | 0.769835 | 0.641627 | 0.601787 | 0.514776 | 0.655549 |
| joint_target_qs_residual_pls_knn_logitresid | 0.685041 | 0.741720 | 0.850271 | 0.722349 | 0.664230 | 0.615891 | 0.520719 | 0.680110 |
| joint_panel_neural_residual_knn_resid | 0.688502 | 0.781040 | 0.853230 | 0.737857 | 0.662690 | 0.621896 | 0.525878 | 0.636926 |
| joint_neural_context_gate_logreg_logitresid | 0.695815 | 0.826085 | 0.829192 | 0.810300 | 0.700173 | 0.585769 | 0.497644 | 0.621540 |
| joint_panel_neural_residual_knn_logitresid | 0.697258 | 0.812053 | 0.820741 | 0.759150 | 0.683283 | 0.628027 | 0.514915 | 0.662636 |
| joint_proto_neural_metric_knn_resid | 0.697474 | 0.745769 | 0.851784 | 0.785256 | 0.643783 | 0.653276 | 0.534187 | 0.668264 |
| joint_family_residual_pls_knn_logitresid | 0.700323 | 0.782768 | 0.826200 | 0.833539 | 0.674313 | 0.631737 | 0.496754 | 0.656950 |
| joint_proto_neural_residual_knn_logitresid | 0.706316 | 0.748454 | 0.893424 | 0.817920 | 0.673102 | 0.644228 | 0.502505 | 0.664581 |
| joint_residual_pls_knn_logitresid | 0.707384 | 0.770056 | 0.809164 | 0.860345 | 0.687036 | 0.632325 | 0.527462 | 0.665299 |
| joint_neural_context_gate_logreg_resid | 0.707401 | 0.886723 | 0.869110 | 0.813232 | 0.672930 | 0.571900 | 0.508745 | 0.629164 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_neural_gated_mixture_knn_resid | 0.717923 | 0.864109 | 0.894103 | 0.822382 | 0.669391 | 0.616241 | 0.495574 | 0.663657 |
| joint_proto_neural_metric_knn_logitresid | 0.718425 | 0.771460 | 0.894153 | 0.842377 | 0.672530 | 0.653909 | 0.514271 | 0.680273 |
| joint_target_residual_pls_knn_resid | 0.721260 | 0.812613 | 0.981437 | 0.693617 | 0.814899 | 0.599658 | 0.501349 | 0.645247 |
| joint_neural_gated_mixture_knn_logitresid | 0.722261 | 0.841468 | 0.909005 | 0.837648 | 0.652605 | 0.619468 | 0.533995 | 0.661637 |
| joint_target_residual_pls_knn_logitresid | 0.730436 | 0.793747 | 0.997190 | 0.725498 | 0.737542 | 0.627423 | 0.547972 | 0.683678 |
| joint_neural_mixture_metric_knn_resid | 0.737361 | 0.916345 | 0.906407 | 0.837353 | 0.686628 | 0.647424 | 0.513271 | 0.654100 |
| joint_neural_mixture_metric_knn_logitresid | 0.737514 | 0.856466 | 0.919431 | 0.840784 | 0.665090 | 0.658142 | 0.526870 | 0.695817 |
| joint_neural_gated_mixture_metric_knn_resid | 0.749286 | 0.922366 | 0.930432 | 0.877519 | 0.704812 | 0.656079 | 0.485315 | 0.668482 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.773334 | 0.944016 | 0.985795 | 0.885861 | 0.695025 | 0.663419 | 0.537726 | 0.701497 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.785467 | 1.009612 | 0.962597 | 0.910020 | 0.721685 | 0.613664 | 0.553147 | 0.727542 |
| joint_target_neural_residual_knn_resid | 0.810592 | 1.011881 | 1.015281 | 0.960439 | 0.728231 | 0.600375 | 0.530659 | 0.827280 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.332488 | 8 | 8 | 10 | 0.270919 | 8 | 8 | 10 | 0.389684 | 10 | 0.376957 | 9 | 6230.527344 | 66 | 10 | 0.409768 | 10 | 0.427477 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.321771 | 8 | 8 | 10 | 0.268558 | 8 | 8 | 10 | 0.384840 | 10 | 0.348104 | 9 | 6492.875488 | 66 | 10 | 0.418795 | 10 | 0.390268 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.310588 | 8 | 8 | 10 | 0.255346 | 8 | 8 | 10 | 0.364720 | 10 | 0.318178 | 9 | 6335.852539 | 66 | 10 | 0.391317 | 10 | 0.415604 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.333598 | 8 | 8 | 10 | 0.262789 | 8 | 8 | 10 | 0.365767 | 10 | 0.375813 | 9 | 6469.970703 | 66 | 10 | 0.379030 | 10 | 0.384518 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.335808 | 8 | 8 | 10 | 0.211688 | 8 | 8 | 10 | 0.392445 | 10 | 0.352393 | 9 | 6421.217773 | 66 | 10 | 0.411089 | 10 | 0.416138 |
