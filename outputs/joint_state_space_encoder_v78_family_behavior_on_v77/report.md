# Joint state-space encoder

- Base OOF: `0.480038`
- Best source: `base`
- Best source OOF: `0.480038`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480038 | 0.525112 | 0.536798 | 0.500706 | 0.469235 | 0.451806 | 0.410320 | 0.466289 |
| joint_proto_mix | 0.493974 | 0.537697 | 0.554052 | 0.519309 | 0.480009 | 0.463637 | 0.423860 | 0.479253 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.507693 | 0.572926 | 0.565672 | 0.534424 | 0.491334 | 0.465885 | 0.429920 | 0.493691 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.511765 | 0.579383 | 0.562562 | 0.543369 | 0.497873 | 0.469371 | 0.436555 | 0.493239 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.514083 | 0.567632 | 0.566598 | 0.553311 | 0.520077 | 0.475693 | 0.432682 | 0.482588 |
| joint_neighbor_logreg | 0.514972 | 0.542446 | 0.572919 | 0.538369 | 0.526566 | 0.490126 | 0.454683 | 0.479696 |
| joint_local_logreg | 0.515518 | 0.543357 | 0.574085 | 0.534822 | 0.523693 | 0.492710 | 0.450269 | 0.489687 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.516188 | 0.595783 | 0.562419 | 0.542351 | 0.515724 | 0.480691 | 0.433814 | 0.482533 |
| joint_metric_neighbor_logreg | 0.520447 | 0.546341 | 0.580159 | 0.549932 | 0.530830 | 0.493428 | 0.455727 | 0.486711 |
| joint_residual_metric_neighbor_logreg | 0.520656 | 0.547109 | 0.583640 | 0.544629 | 0.534760 | 0.493006 | 0.454599 | 0.486847 |
| joint_neighbor_hgb | 0.538489 | 0.572654 | 0.604925 | 0.569836 | 0.503182 | 0.512397 | 0.465455 | 0.540974 |
| joint_metric_neighbor_hgb | 0.542675 | 0.586554 | 0.617631 | 0.576045 | 0.502431 | 0.507214 | 0.467205 | 0.541646 |
| joint_residual_metric_neighbor_hgb | 0.545378 | 0.577161 | 0.617043 | 0.582585 | 0.516503 | 0.504678 | 0.470003 | 0.549673 |
| joint_residual_pls_neighbor_logreg | 0.551549 | 0.604395 | 0.580721 | 0.607489 | 0.570724 | 0.518730 | 0.460180 | 0.518604 |
| joint_neural_cross_family_residual_knn_resid | 0.552391 | 0.560404 | 0.591877 | 0.636553 | 0.548467 | 0.554531 | 0.439701 | 0.535207 |
| joint_residual_pls_local_logreg | 0.552876 | 0.603411 | 0.588790 | 0.612934 | 0.570134 | 0.514265 | 0.463203 | 0.517395 |
| joint_local_hgb | 0.553863 | 0.579815 | 0.640030 | 0.580532 | 0.516638 | 0.531925 | 0.466815 | 0.561288 |
| joint_cross_family_residual_pls_knn_resid | 0.554564 | 0.638235 | 0.589866 | 0.590307 | 0.533364 | 0.508247 | 0.503506 | 0.518426 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.563776 | 0.620444 | 0.646315 | 0.594515 | 0.516218 | 0.515783 | 0.492951 | 0.560206 |
| joint_residual_contrast_hgb | 0.565043 | 0.596863 | 0.656340 | 0.600460 | 0.547491 | 0.514657 | 0.483590 | 0.555901 |
| joint_neural_context_bin_gate_hgb_resid | 0.565751 | 0.606418 | 0.637454 | 0.599488 | 0.525085 | 0.525843 | 0.484038 | 0.581928 |
| joint_neural_bin_gate_knn_resid | 0.569300 | 0.610829 | 0.654895 | 0.610273 | 0.561663 | 0.521146 | 0.473171 | 0.553127 |
| joint_neural_learned_gate_knn_resid | 0.570080 | 0.613353 | 0.655824 | 0.611005 | 0.566596 | 0.520260 | 0.473816 | 0.549706 |
| joint_neural_s_residual_knn_resid | 0.570817 | 0.560404 | 0.591877 | 0.636553 | 0.617874 | 0.540857 | 0.486712 | 0.561438 |
| joint_residual_pls_neighbor_hgb | 0.573118 | 0.625364 | 0.645609 | 0.622241 | 0.545084 | 0.527397 | 0.471864 | 0.574267 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.577143 | 0.658715 | 0.572590 | 0.618804 | 0.567917 | 0.531259 | 0.525420 | 0.565299 |
| joint_cross_family_residual_behavior_neural_knn_resid | 0.580957 | 0.603107 | 0.617855 | 0.635334 | 0.708941 | 0.492383 | 0.459518 | 0.549561 |
| joint_residual_contrast_logreg | 0.583453 | 0.599174 | 0.656552 | 0.620884 | 0.592310 | 0.548161 | 0.500436 | 0.566654 |
| joint_residual_pls_local_hgb | 0.584471 | 0.643928 | 0.661938 | 0.638519 | 0.552374 | 0.543245 | 0.473725 | 0.577571 |
| joint_pls_knn_resid | 0.586497 | 0.608819 | 0.679957 | 0.676736 | 0.564565 | 0.555679 | 0.476721 | 0.543002 |
| joint_neural_cross_family_residual_knn_logitresid | 0.590269 | 0.629959 | 0.647682 | 0.684996 | 0.565912 | 0.543133 | 0.470514 | 0.589685 |
| joint_cross_family_residual_pls_knn_logitresid | 0.592007 | 0.667026 | 0.658039 | 0.626073 | 0.557812 | 0.524711 | 0.528077 | 0.582310 |
| joint_cross_family_residual_behavior_neural_metric_knn_resid | 0.599514 | 0.616387 | 0.666463 | 0.695850 | 0.686737 | 0.496072 | 0.448875 | 0.586217 |
| joint_metric_knn_resid | 0.600726 | 0.637077 | 0.734000 | 0.653143 | 0.566521 | 0.559977 | 0.480663 | 0.573700 |
| joint_attention_knn_resid | 0.604220 | 0.625840 | 0.707267 | 0.684921 | 0.565510 | 0.566594 | 0.505944 | 0.573463 |
| joint_residual_metric_knn_resid | 0.606777 | 0.639538 | 0.761900 | 0.679642 | 0.589475 | 0.541886 | 0.482992 | 0.552007 |
| joint_metric_attention_knn_resid | 0.610480 | 0.657003 | 0.748608 | 0.660379 | 0.579850 | 0.552446 | 0.490353 | 0.584723 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.611227 | 0.682982 | 0.631801 | 0.690486 | 0.599058 | 0.578294 | 0.515648 | 0.580320 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.612025 | 0.671554 | 0.725957 | 0.687060 | 0.580751 | 0.561466 | 0.478726 | 0.578662 |
| joint_neural_q_residual_knn_resid | 0.612434 | 0.712330 | 0.770279 | 0.726522 | 0.548467 | 0.554531 | 0.439701 | 0.535207 |
| joint_residual_behavior_neural_multiview_knn_resid | 0.613509 | 0.652704 | 0.633658 | 0.689191 | 0.613638 | 0.632009 | 0.476447 | 0.596920 |
| joint_neural_s_residual_knn_logitresid | 0.614131 | 0.629959 | 0.647682 | 0.684996 | 0.628643 | 0.577117 | 0.533264 | 0.597253 |
| joint_neural_multiview_q_residual_knn_resid | 0.614632 | 0.698654 | 0.666483 | 0.747393 | 0.567917 | 0.531259 | 0.525420 | 0.565299 |
| joint_q_residual_pls_knn_resid | 0.617387 | 0.782190 | 0.702655 | 0.773320 | 0.533364 | 0.508247 | 0.503506 | 0.518426 |
| joint_neural_qs_residual_knn_resid | 0.618467 | 0.636796 | 0.666453 | 0.743097 | 0.608168 | 0.637115 | 0.469467 | 0.568172 |
| joint_neural_context_gate_hgb_logitresid | 0.621177 | 0.657360 | 0.701044 | 0.677891 | 0.587918 | 0.563001 | 0.528754 | 0.632269 |
| joint_neural_context_gate_hgb_resid | 0.622578 | 0.664077 | 0.711709 | 0.679916 | 0.573435 | 0.576365 | 0.524071 | 0.628473 |
| joint_neural_context_bin_gate_logreg_resid | 0.623144 | 0.669812 | 0.768654 | 0.721807 | 0.607203 | 0.552622 | 0.488682 | 0.553229 |
| joint_cross_family_residual_behavior_neural_knn_logitresid | 0.623395 | 0.674375 | 0.737814 | 0.689133 | 0.623231 | 0.538116 | 0.495056 | 0.606041 |
| joint_residual_behavior_neural_multiview_metric_knn_resid | 0.623793 | 0.656797 | 0.642171 | 0.747389 | 0.599495 | 0.644960 | 0.475362 | 0.600377 |
| joint_s_residual_pls_knn_resid | 0.628587 | 0.638235 | 0.589866 | 0.590307 | 0.698851 | 0.680959 | 0.505812 | 0.696079 |
| joint_pls_knn_logitresid | 0.631217 | 0.675141 | 0.770123 | 0.740754 | 0.582019 | 0.551938 | 0.516347 | 0.582196 |
| joint_neural_multiview_qs_residual_knn_resid | 0.632161 | 0.716568 | 0.632686 | 0.645054 | 0.627165 | 0.671467 | 0.515662 | 0.616524 |
| joint_neural_q_residual_knn_logitresid | 0.633202 | 0.696832 | 0.807955 | 0.758384 | 0.565912 | 0.543133 | 0.470514 | 0.589685 |
| joint_neural_multiview_residual_knn_resid | 0.634359 | 0.756079 | 0.645770 | 0.669807 | 0.689411 | 0.600553 | 0.508880 | 0.570016 |
| joint_neural_multiview_s_residual_knn_resid | 0.636670 | 0.658715 | 0.572590 | 0.618804 | 0.720817 | 0.666454 | 0.560045 | 0.659267 |
| joint_cross_family_residual_behavior_neural_metric_knn_logitresid | 0.637368 | 0.667754 | 0.775544 | 0.706449 | 0.654920 | 0.556904 | 0.483369 | 0.616635 |
| joint_proto_neural_multiview_residual_knn_resid | 0.638564 | 0.804704 | 0.650454 | 0.649191 | 0.655103 | 0.632113 | 0.486349 | 0.592034 |
| joint_panel_neural_multiview_residual_knn_resid | 0.639175 | 0.722872 | 0.660529 | 0.661448 | 0.650613 | 0.665113 | 0.517709 | 0.595944 |
| joint_neural_qs_residual_knn_logitresid | 0.642368 | 0.683523 | 0.732773 | 0.780715 | 0.623710 | 0.571272 | 0.498055 | 0.606529 |
| joint_s_residual_pls_knn_logitresid | 0.642520 | 0.667026 | 0.658039 | 0.626073 | 0.688220 | 0.637708 | 0.528419 | 0.692155 |
| joint_metric_knn_logitresid | 0.643411 | 0.700514 | 0.762430 | 0.716041 | 0.610804 | 0.568643 | 0.525651 | 0.619796 |
| joint_residual_metric_knn_logitresid | 0.648979 | 0.694453 | 0.782772 | 0.732449 | 0.622769 | 0.569335 | 0.521285 | 0.619786 |
| joint_neural_bin_gate_knn_logitresid | 0.649702 | 0.697243 | 0.754664 | 0.721298 | 0.631532 | 0.600653 | 0.515750 | 0.626772 |
| joint_target_neural_multiview_residual_knn_resid | 0.650657 | 0.757404 | 0.775031 | 0.722811 | 0.641269 | 0.578295 | 0.457699 | 0.622093 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.650717 | 0.736861 | 0.762405 | 0.782436 | 0.599058 | 0.578294 | 0.515648 | 0.580320 |
| joint_attention_knn_logitresid | 0.650986 | 0.706549 | 0.783817 | 0.765867 | 0.586681 | 0.572707 | 0.537134 | 0.604149 |
| joint_neural_residual_knn_resid | 0.651047 | 0.769548 | 0.704060 | 0.672438 | 0.651318 | 0.607991 | 0.547269 | 0.604705 |
| joint_neural_learned_gate_knn_logitresid | 0.651731 | 0.710559 | 0.760492 | 0.726180 | 0.626043 | 0.600069 | 0.518391 | 0.620383 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.653020 | 0.682982 | 0.631801 | 0.690486 | 0.679130 | 0.676651 | 0.539782 | 0.670308 |
| joint_q_residual_pls_knn_logitresid | 0.656163 | 0.779088 | 0.811422 | 0.809718 | 0.557812 | 0.524711 | 0.528077 | 0.582310 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.656241 | 0.708947 | 0.688239 | 0.763532 | 0.630079 | 0.647355 | 0.520655 | 0.634879 |
| joint_proto_neural_residual_knn_resid | 0.656269 | 0.735054 | 0.747126 | 0.840425 | 0.559463 | 0.577228 | 0.518909 | 0.615678 |
| joint_qs_residual_pls_knn_resid | 0.656600 | 0.674352 | 0.681844 | 0.733547 | 0.719730 | 0.588539 | 0.508002 | 0.690187 |
| joint_proto_neural_multiview_metric_knn_resid | 0.656891 | 0.799436 | 0.653069 | 0.657663 | 0.684705 | 0.653326 | 0.490935 | 0.659106 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.659265 | 0.751915 | 0.732810 | 0.704364 | 0.624647 | 0.641709 | 0.533201 | 0.626212 |
| joint_metric_attention_knn_logitresid | 0.661459 | 0.734984 | 0.772924 | 0.737227 | 0.614552 | 0.585238 | 0.547019 | 0.638269 |
| joint_panel_neural_residual_knn_resid | 0.662348 | 0.834105 | 0.799196 | 0.638515 | 0.633069 | 0.655371 | 0.455294 | 0.620887 |
| joint_residual_behavior_neural_multiview_knn_logitresid | 0.662961 | 0.716213 | 0.740928 | 0.720803 | 0.623012 | 0.639293 | 0.519549 | 0.680930 |
| joint_neural_mixture_knn_resid | 0.663604 | 0.762344 | 0.778679 | 0.749633 | 0.665596 | 0.579800 | 0.483509 | 0.625669 |
| joint_neural_multiview_residual_knn_logitresid | 0.665152 | 0.781551 | 0.710439 | 0.734916 | 0.649047 | 0.632757 | 0.539428 | 0.607925 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.666475 | 0.760060 | 0.723323 | 0.718599 | 0.611778 | 0.667624 | 0.551245 | 0.632699 |
| joint_neural_residual_knn_logitresid | 0.671363 | 0.721457 | 0.789349 | 0.759431 | 0.645658 | 0.633558 | 0.525526 | 0.624563 |
| joint_residual_behavior_neural_multiview_metric_knn_logitresid | 0.671814 | 0.737252 | 0.752326 | 0.743205 | 0.632850 | 0.640262 | 0.524632 | 0.672172 |
| joint_qs_residual_pls_knn_logitresid | 0.676711 | 0.725077 | 0.789838 | 0.745583 | 0.657154 | 0.604895 | 0.530686 | 0.683744 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.678439 | 0.772757 | 0.745747 | 0.730590 | 0.628192 | 0.668452 | 0.545527 | 0.657808 |
| joint_proto_neural_metric_knn_resid | 0.679725 | 0.759717 | 0.792936 | 0.833291 | 0.649183 | 0.599696 | 0.514303 | 0.608948 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.681802 | 0.786320 | 0.842538 | 0.749230 | 0.634580 | 0.626441 | 0.495109 | 0.638396 |
| joint_target_qs_residual_pls_knn_resid | 0.683749 | 0.740508 | 0.732677 | 0.736313 | 0.739950 | 0.610889 | 0.513659 | 0.712244 |
| joint_residual_pls_knn_resid | 0.685445 | 0.711225 | 0.728376 | 0.787775 | 0.689241 | 0.642374 | 0.518859 | 0.720264 |
| joint_family_residual_behavior_neural_knn_resid | 0.685568 | 0.727462 | 0.818036 | 0.771286 | 0.629286 | 0.664668 | 0.546183 | 0.642054 |
| joint_neural_mixture_knn_logitresid | 0.686148 | 0.776370 | 0.818898 | 0.782097 | 0.637035 | 0.625983 | 0.522115 | 0.640539 |
| joint_proto_neural_residual_knn_logitresid | 0.687368 | 0.781218 | 0.803863 | 0.825120 | 0.625032 | 0.600918 | 0.531805 | 0.643616 |
| joint_family_residual_pls_knn_resid | 0.691409 | 0.782190 | 0.702655 | 0.773320 | 0.698851 | 0.680959 | 0.505812 | 0.696079 |
| joint_target_qs_residual_pls_knn_logitresid | 0.693359 | 0.748356 | 0.829474 | 0.749468 | 0.680080 | 0.611536 | 0.541387 | 0.693209 |
| joint_family_residual_behavior_neural_metric_knn_resid | 0.696439 | 0.776812 | 0.829491 | 0.801004 | 0.628904 | 0.681205 | 0.530209 | 0.627448 |
| joint_panel_neural_residual_knn_logitresid | 0.702539 | 0.891463 | 0.847484 | 0.704201 | 0.692354 | 0.647321 | 0.507175 | 0.627776 |
| joint_family_residual_pls_knn_logitresid | 0.706676 | 0.779088 | 0.811422 | 0.809718 | 0.688220 | 0.637708 | 0.528419 | 0.692155 |
| joint_target_residual_pls_knn_resid | 0.707461 | 0.841235 | 0.843487 | 0.738731 | 0.759282 | 0.593729 | 0.568127 | 0.607638 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_residual_pls_knn_logitresid | 0.710420 | 0.780978 | 0.812432 | 0.837981 | 0.680447 | 0.636682 | 0.532601 | 0.691816 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_proto_neural_metric_knn_logitresid | 0.711764 | 0.803197 | 0.856535 | 0.854612 | 0.646574 | 0.644601 | 0.550181 | 0.626644 |
| joint_family_residual_behavior_neural_knn_logitresid | 0.721650 | 0.792850 | 0.916672 | 0.802185 | 0.648136 | 0.680227 | 0.564388 | 0.647094 |
| joint_residual_behavior_neural_knn_logitresid | 0.724853 | 0.719986 | 0.845168 | 0.858769 | 0.782647 | 0.635876 | 0.492703 | 0.738823 |
| joint_residual_behavior_neural_knn_resid | 0.727038 | 0.659157 | 0.777095 | 0.841293 | 0.961511 | 0.610345 | 0.512830 | 0.727037 |
| joint_target_residual_pls_knn_logitresid | 0.727288 | 0.813319 | 0.933249 | 0.750520 | 0.715380 | 0.629629 | 0.589650 | 0.659270 |
| joint_neural_context_gate_logreg_logitresid | 0.727872 | 0.783576 | 0.890006 | 0.855770 | 0.709627 | 0.630266 | 0.557650 | 0.668211 |
| joint_family_residual_behavior_neural_metric_knn_logitresid | 0.733300 | 0.794512 | 0.936061 | 0.830321 | 0.646408 | 0.696460 | 0.577680 | 0.651660 |
| joint_neural_mixture_metric_knn_logitresid | 0.734747 | 0.828833 | 0.897140 | 0.816884 | 0.667369 | 0.702871 | 0.533355 | 0.696776 |
| joint_neural_mixture_metric_knn_resid | 0.735057 | 0.812995 | 0.796204 | 0.895256 | 0.700308 | 0.688165 | 0.500693 | 0.751780 |
| joint_neural_gated_mixture_knn_resid | 0.736328 | 0.755783 | 0.893547 | 0.845336 | 0.695521 | 0.654397 | 0.517418 | 0.792294 |
| joint_neural_gated_mixture_knn_logitresid | 0.738228 | 0.797647 | 0.906434 | 0.831544 | 0.660831 | 0.694771 | 0.571452 | 0.704920 |
| joint_target_residual_behavior_neural_knn_resid | 0.743045 | 0.699082 | 0.791694 | 0.925556 | 0.702360 | 0.638038 | 0.587511 | 0.857074 |
| joint_neural_context_gate_logreg_resid | 0.748854 | 0.808675 | 0.949731 | 0.881151 | 0.746861 | 0.639992 | 0.544685 | 0.670886 |
| joint_residual_behavior_neural_metric_knn_logitresid | 0.760926 | 0.766946 | 0.878709 | 0.922895 | 0.816485 | 0.664797 | 0.507140 | 0.769510 |
| joint_target_residual_behavior_neural_knn_logitresid | 0.761384 | 0.758427 | 0.846809 | 0.918375 | 0.737306 | 0.666896 | 0.619553 | 0.782318 |
| joint_residual_behavior_neural_metric_knn_resid | 0.762373 | 0.743694 | 0.848396 | 0.859692 | 0.997242 | 0.622267 | 0.516138 | 0.749184 |
| joint_neural_context_attention_knn_logitresid | 0.773790 | 0.869309 | 0.974509 | 0.817898 | 0.743860 | 0.682456 | 0.573425 | 0.755073 |
| joint_target_neural_residual_knn_resid | 0.780814 | 0.858028 | 1.099187 | 0.877201 | 0.736736 | 0.639068 | 0.531293 | 0.724184 |
| joint_target_residual_behavior_neural_metric_knn_resid | 0.781920 | 0.712060 | 0.797165 | 0.973777 | 0.697543 | 0.732338 | 0.610168 | 0.950390 |
| joint_target_residual_behavior_neural_metric_knn_logitresid | 0.785102 | 0.744234 | 0.869084 | 0.929406 | 0.746376 | 0.708340 | 0.647119 | 0.851157 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.786687 | 0.884717 | 1.036705 | 0.935810 | 0.703649 | 0.623921 | 0.589670 | 0.732334 |
| joint_neural_context_attention_knn_resid | 0.791093 | 0.845035 | 0.911971 | 0.895576 | 0.834800 | 0.636483 | 0.589554 | 0.824231 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.791202 | 0.860790 | 0.957762 | 0.886770 | 0.727084 | 0.752201 | 0.607809 | 0.745996 |
| joint_neural_gated_mixture_metric_knn_resid | 0.808101 | 0.828744 | 0.925639 | 0.954688 | 0.782639 | 0.733000 | 0.570817 | 0.861177 |
| joint_neural_context_metric_attention_knn_resid | 0.877567 | 0.984098 | 1.062353 | 1.005585 | 0.989546 | 0.655614 | 0.571833 | 0.873938 |
| joint_neural_context_metric_attention_knn_logitresid | 0.880802 | 0.987541 | 1.115621 | 0.960310 | 0.836295 | 0.742002 | 0.661325 | 0.862517 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss | residual_neighborhood_k | residual_neighborhood_target_dim | residual_neighborhood_mean_distance | residual_behavior_neural_latent_dim | residual_behavior_neural_best_loss | residual_behavior_multiview_neural_latent_dim | residual_behavior_multiview_neural_best_loss | q_residual_neighborhood_target_dim | q_residual_neighborhood_mean_distance | s_residual_neighborhood_target_dim | s_residual_neighborhood_mean_distance | q_residual_behavior_neural_latent_dim | q_residual_behavior_neural_best_loss | s_residual_behavior_neural_latent_dim | s_residual_behavior_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.327201 | 8 | 8 | 10 | 0.267700 | 8 | 8 | 10 | 0.379181 | 10 | 0.363917 | 9 | 6254.942383 | 66 | 10 | 0.416336 | 10 | 0.414505 | 31 | 90 | 0.823334 | 10 | 0.359536 | 10 | 0.425546 | 42 | 0.464194 | 54 | 0.593070 | 8 | 0.379696 | 8 | 0.387367 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.301386 | 8 | 8 | 10 | 0.272391 | 8 | 8 | 10 | 0.387259 | 10 | 0.350581 | 9 | 6486.716309 | 66 | 10 | 0.398688 | 10 | 0.370932 | 31 | 90 | 0.846149 | 10 | 0.366610 | 10 | 0.425423 | 42 | 0.506706 | 54 | 0.618576 | 8 | 0.372615 | 8 | 0.369881 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.309353 | 8 | 8 | 10 | 0.252834 | 8 | 8 | 10 | 0.369865 | 10 | 0.312952 | 9 | 6343.100586 | 66 | 10 | 0.427562 | 10 | 0.411223 | 31 | 90 | 0.830580 | 10 | 0.357781 | 10 | 0.408143 | 42 | 0.470452 | 54 | 0.602870 | 8 | 0.334282 | 8 | 0.380057 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.348978 | 8 | 8 | 10 | 0.261634 | 8 | 8 | 10 | 0.393496 | 10 | 0.349287 | 9 | 6494.617676 | 66 | 10 | 0.371077 | 10 | 0.352745 | 31 | 90 | 0.819317 | 10 | 0.375047 | 10 | 0.419333 | 42 | 0.479245 | 54 | 0.604594 | 8 | 0.361932 | 8 | 0.397953 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.319011 | 8 | 8 | 10 | 0.205804 | 8 | 8 | 10 | 0.385662 | 10 | 0.336026 | 9 | 6428.881836 | 66 | 10 | 0.415348 | 10 | 0.411553 | 31 | 90 | 0.812380 | 10 | 0.369225 | 10 | 0.406117 | 42 | 0.489879 | 54 | 0.600366 | 8 | 0.354635 | 8 | 0.391253 |
