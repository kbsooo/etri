# Joint state-space encoder

- Base OOF: `0.479449`
- Best source: `base`
- Best source OOF: `0.479449`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.479449 | 0.524853 | 0.535474 | 0.500706 | 0.468781 | 0.451615 | 0.408746 | 0.465970 |
| joint_proto_mix | 0.493443 | 0.537584 | 0.553019 | 0.519309 | 0.479524 | 0.463557 | 0.422208 | 0.478902 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.510426 | 0.577396 | 0.564437 | 0.536055 | 0.480319 | 0.473591 | 0.445858 | 0.495323 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.512588 | 0.583882 | 0.563368 | 0.542126 | 0.481675 | 0.472743 | 0.446562 | 0.497759 |
| joint_neighbor_logreg | 0.514155 | 0.542353 | 0.570774 | 0.538369 | 0.525744 | 0.489865 | 0.453127 | 0.478856 |
| joint_local_logreg | 0.514782 | 0.543219 | 0.571812 | 0.534822 | 0.523148 | 0.492632 | 0.448736 | 0.489106 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.516155 | 0.564814 | 0.568256 | 0.568771 | 0.500321 | 0.480145 | 0.442265 | 0.488510 |
| joint_residual_metric_neighbor_logreg | 0.518995 | 0.547948 | 0.582450 | 0.544629 | 0.529001 | 0.491449 | 0.452112 | 0.485376 |
| joint_metric_neighbor_logreg | 0.519402 | 0.546339 | 0.577884 | 0.549932 | 0.529426 | 0.493161 | 0.453553 | 0.485520 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.528332 | 0.602926 | 0.583757 | 0.571016 | 0.519765 | 0.490944 | 0.439219 | 0.490696 |
| joint_neighbor_hgb | 0.538567 | 0.576357 | 0.613683 | 0.569836 | 0.497752 | 0.514723 | 0.467335 | 0.530285 |
| joint_neural_cross_family_residual_knn_resid | 0.542426 | 0.618674 | 0.584213 | 0.547384 | 0.531043 | 0.527980 | 0.441606 | 0.546081 |
| joint_metric_neighbor_hgb | 0.542944 | 0.583222 | 0.618208 | 0.576045 | 0.498848 | 0.510005 | 0.470122 | 0.544157 |
| joint_residual_metric_neighbor_hgb | 0.547101 | 0.578878 | 0.617103 | 0.582585 | 0.514323 | 0.511894 | 0.476276 | 0.548648 |
| joint_residual_pls_neighbor_logreg | 0.549079 | 0.605705 | 0.580747 | 0.610363 | 0.566341 | 0.512631 | 0.460661 | 0.507107 |
| joint_cross_family_residual_pls_knn_resid | 0.551881 | 0.616527 | 0.582841 | 0.593633 | 0.528089 | 0.512540 | 0.494207 | 0.535330 |
| joint_residual_pls_local_logreg | 0.551965 | 0.606692 | 0.588171 | 0.616937 | 0.567758 | 0.510796 | 0.464760 | 0.508642 |
| joint_local_hgb | 0.554285 | 0.582074 | 0.646036 | 0.580532 | 0.511954 | 0.533884 | 0.469142 | 0.556372 |
| joint_neural_context_bin_gate_hgb_resid | 0.561071 | 0.607810 | 0.643070 | 0.618835 | 0.522411 | 0.517040 | 0.481939 | 0.536395 |
| joint_neural_s_residual_knn_resid | 0.563659 | 0.618674 | 0.584213 | 0.547384 | 0.639694 | 0.508502 | 0.495781 | 0.551366 |
| joint_residual_contrast_hgb | 0.563923 | 0.597878 | 0.653064 | 0.600460 | 0.541028 | 0.516861 | 0.478333 | 0.559836 |
| joint_neural_learned_gate_knn_resid | 0.564585 | 0.594011 | 0.636308 | 0.614588 | 0.545507 | 0.527767 | 0.476126 | 0.557785 |
| joint_neural_bin_gate_knn_resid | 0.566047 | 0.591442 | 0.644171 | 0.613259 | 0.542208 | 0.527888 | 0.482098 | 0.561260 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.569015 | 0.620237 | 0.664425 | 0.633729 | 0.512553 | 0.520391 | 0.482224 | 0.549548 |
| joint_residual_pls_neighbor_hgb | 0.571590 | 0.619645 | 0.660427 | 0.616149 | 0.531333 | 0.530359 | 0.477716 | 0.565501 |
| joint_neural_cross_family_residual_knn_logitresid | 0.579182 | 0.675038 | 0.651835 | 0.578459 | 0.574276 | 0.532768 | 0.465110 | 0.576791 |
| joint_residual_pls_local_hgb | 0.582642 | 0.635654 | 0.676019 | 0.631921 | 0.542959 | 0.543139 | 0.479371 | 0.569432 |
| joint_cross_family_residual_pls_knn_logitresid | 0.582893 | 0.649416 | 0.643202 | 0.625639 | 0.549313 | 0.525459 | 0.511768 | 0.575453 |
| joint_residual_contrast_logreg | 0.582979 | 0.600204 | 0.656486 | 0.620884 | 0.590566 | 0.546658 | 0.499092 | 0.566960 |
| joint_cross_family_residual_behavior_neural_knn_resid | 0.586346 | 0.632497 | 0.628912 | 0.617978 | 0.653723 | 0.490276 | 0.492286 | 0.588752 |
| joint_neural_q_residual_knn_resid | 0.586536 | 0.678610 | 0.688600 | 0.691835 | 0.531043 | 0.527980 | 0.441606 | 0.546081 |
| joint_pls_knn_resid | 0.586698 | 0.613115 | 0.682745 | 0.676736 | 0.563501 | 0.555916 | 0.474487 | 0.540385 |
| joint_neural_qs_residual_knn_resid | 0.591208 | 0.684323 | 0.672707 | 0.639761 | 0.595769 | 0.529222 | 0.466549 | 0.550124 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.593912 | 0.682308 | 0.593611 | 0.642031 | 0.590790 | 0.565686 | 0.501438 | 0.581519 |
| joint_s23_late_residual_behavior_neural_knn_resid | 0.594681 | 0.700093 | 0.634941 | 0.602221 | 0.535713 | 0.540036 | 0.549532 | 0.600232 |
| joint_attention_knn_resid | 0.598670 | 0.629966 | 0.709051 | 0.684921 | 0.564285 | 0.567094 | 0.488193 | 0.547178 |
| joint_metric_knn_resid | 0.602412 | 0.639092 | 0.748110 | 0.653143 | 0.564569 | 0.560125 | 0.478514 | 0.573332 |
| joint_cross_family_residual_behavior_neural_metric_knn_resid | 0.602440 | 0.633148 | 0.735793 | 0.646533 | 0.625802 | 0.501562 | 0.491851 | 0.582394 |
| joint_residual_metric_knn_resid | 0.604151 | 0.644656 | 0.740636 | 0.679642 | 0.588041 | 0.547303 | 0.480903 | 0.547873 |
| joint_neural_s_residual_knn_logitresid | 0.604587 | 0.675038 | 0.651835 | 0.578459 | 0.592644 | 0.576801 | 0.543717 | 0.613613 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.606322 | 0.657407 | 0.739360 | 0.716774 | 0.558595 | 0.546800 | 0.481929 | 0.543392 |
| joint_s23_late_residual_behavior_neural_metric_knn_resid | 0.608229 | 0.726080 | 0.645138 | 0.607544 | 0.556325 | 0.570641 | 0.553911 | 0.597968 |
| joint_s_residual_pls_knn_resid | 0.608253 | 0.616527 | 0.582841 | 0.593633 | 0.632716 | 0.661037 | 0.487713 | 0.683302 |
| joint_neural_qs_residual_knn_logitresid | 0.610864 | 0.718872 | 0.674037 | 0.666340 | 0.596537 | 0.539342 | 0.505543 | 0.575378 |
| joint_metric_attention_knn_resid | 0.612337 | 0.659785 | 0.758222 | 0.660379 | 0.578216 | 0.553832 | 0.488836 | 0.587088 |
| joint_q_residual_pls_knn_resid | 0.613655 | 0.771036 | 0.672501 | 0.781880 | 0.528089 | 0.512540 | 0.494207 | 0.535330 |
| joint_neural_multiview_s_residual_knn_resid | 0.617604 | 0.682308 | 0.593611 | 0.642031 | 0.660150 | 0.617553 | 0.530373 | 0.597201 |
| joint_neural_context_gate_hgb_logitresid | 0.618741 | 0.655062 | 0.686934 | 0.682040 | 0.568240 | 0.597110 | 0.525410 | 0.616388 |
| joint_neural_context_gate_hgb_resid | 0.619268 | 0.651683 | 0.695468 | 0.692607 | 0.573878 | 0.590751 | 0.521289 | 0.609196 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.619390 | 0.702451 | 0.638753 | 0.712505 | 0.603435 | 0.581756 | 0.496367 | 0.600463 |
| joint_neural_multiview_qs_residual_knn_resid | 0.620488 | 0.653629 | 0.630706 | 0.703969 | 0.640448 | 0.590738 | 0.527894 | 0.596030 |
| joint_neural_q_residual_knn_logitresid | 0.620909 | 0.729320 | 0.730540 | 0.737561 | 0.574276 | 0.532768 | 0.465110 | 0.576791 |
| joint_neural_multiview_residual_knn_resid | 0.624620 | 0.746744 | 0.648729 | 0.719350 | 0.607445 | 0.582247 | 0.471079 | 0.596743 |
| joint_neural_context_bin_gate_logreg_resid | 0.627369 | 0.645567 | 0.715366 | 0.714436 | 0.661519 | 0.568331 | 0.509468 | 0.576895 |
| joint_neural_residual_knn_resid | 0.628399 | 0.670679 | 0.689288 | 0.663591 | 0.642900 | 0.578098 | 0.533977 | 0.620260 |
| joint_cross_family_residual_behavior_neural_knn_logitresid | 0.630536 | 0.709426 | 0.763291 | 0.656211 | 0.618291 | 0.539179 | 0.502966 | 0.624389 |
| joint_pls_knn_logitresid | 0.631043 | 0.676673 | 0.769523 | 0.740754 | 0.580347 | 0.554445 | 0.514362 | 0.581199 |
| joint_s_residual_pls_knn_logitresid | 0.633669 | 0.649416 | 0.643202 | 0.625639 | 0.684322 | 0.627041 | 0.524075 | 0.681985 |
| joint_panel_neural_multiview_residual_knn_resid | 0.635265 | 0.721753 | 0.726258 | 0.686308 | 0.591956 | 0.582242 | 0.500755 | 0.637585 |
| joint_neural_bin_gate_knn_logitresid | 0.639974 | 0.666491 | 0.748352 | 0.713814 | 0.583642 | 0.590454 | 0.522489 | 0.654578 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.641222 | 0.702451 | 0.638753 | 0.712505 | 0.626166 | 0.635639 | 0.512058 | 0.660981 |
| joint_proto_neural_multiview_residual_knn_resid | 0.641444 | 0.725859 | 0.708746 | 0.657355 | 0.603636 | 0.620704 | 0.501011 | 0.672799 |
| joint_metric_knn_logitresid | 0.642402 | 0.701754 | 0.761008 | 0.716041 | 0.609179 | 0.569226 | 0.522462 | 0.617143 |
| joint_neural_multiview_q_residual_knn_resid | 0.642856 | 0.651341 | 0.766596 | 0.842620 | 0.590790 | 0.565686 | 0.501438 | 0.581519 |
| joint_cross_family_residual_behavior_neural_metric_knn_logitresid | 0.642964 | 0.703181 | 0.808282 | 0.664848 | 0.615697 | 0.551418 | 0.516422 | 0.640901 |
| joint_proto_neural_multiview_metric_knn_resid | 0.644709 | 0.732676 | 0.686952 | 0.671386 | 0.613572 | 0.645888 | 0.521249 | 0.641238 |
| joint_neural_learned_gate_knn_logitresid | 0.645112 | 0.673458 | 0.752990 | 0.736511 | 0.591062 | 0.592985 | 0.517883 | 0.650892 |
| joint_residual_metric_knn_logitresid | 0.647798 | 0.701562 | 0.769384 | 0.732449 | 0.623553 | 0.575045 | 0.518176 | 0.614416 |
| joint_q_residual_pls_knn_logitresid | 0.647834 | 0.774116 | 0.781412 | 0.817314 | 0.549313 | 0.525459 | 0.511768 | 0.575453 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.649621 | 0.704724 | 0.699009 | 0.789681 | 0.615470 | 0.610991 | 0.508658 | 0.618816 |
| joint_s23_residual_behavior_neural_knn_resid | 0.650271 | 0.658971 | 0.746842 | 0.622188 | 0.638462 | 0.632836 | 0.502263 | 0.750333 |
| joint_s23_late_residual_behavior_neural_knn_logitresid | 0.650748 | 0.727354 | 0.743946 | 0.631148 | 0.585798 | 0.640919 | 0.574318 | 0.651752 |
| joint_attention_knn_logitresid | 0.650777 | 0.708597 | 0.782402 | 0.765867 | 0.583974 | 0.575456 | 0.536406 | 0.602736 |
| joint_s23_residual_behavior_neural_metric_knn_resid | 0.653934 | 0.622805 | 0.767050 | 0.615644 | 0.631106 | 0.670980 | 0.491371 | 0.778582 |
| joint_target_neural_multiview_residual_knn_resid | 0.653986 | 0.785959 | 0.660171 | 0.721829 | 0.644776 | 0.609072 | 0.537555 | 0.618543 |
| joint_qs_residual_pls_knn_resid | 0.654728 | 0.688712 | 0.683724 | 0.752499 | 0.674657 | 0.583832 | 0.512272 | 0.687397 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.656919 | 0.713764 | 0.743078 | 0.859573 | 0.603435 | 0.581756 | 0.496367 | 0.600463 |
| joint_neural_residual_knn_logitresid | 0.657274 | 0.677425 | 0.767365 | 0.722439 | 0.671367 | 0.601097 | 0.530896 | 0.630329 |
| joint_neural_mixture_knn_resid | 0.658546 | 0.704308 | 0.748759 | 0.769740 | 0.644235 | 0.611585 | 0.498061 | 0.633132 |
| joint_proto_neural_residual_knn_resid | 0.659731 | 0.665033 | 0.702164 | 0.843360 | 0.570518 | 0.650120 | 0.537107 | 0.649814 |
| joint_metric_attention_knn_logitresid | 0.660512 | 0.736697 | 0.771001 | 0.737227 | 0.612058 | 0.586233 | 0.545013 | 0.635353 |
| joint_neural_multiview_residual_knn_logitresid | 0.662839 | 0.778805 | 0.708354 | 0.779545 | 0.612827 | 0.613212 | 0.519228 | 0.627899 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.663474 | 0.696687 | 0.776906 | 0.740275 | 0.621710 | 0.627452 | 0.539800 | 0.641484 |
| joint_s23_late_residual_behavior_neural_metric_knn_logitresid | 0.663493 | 0.753405 | 0.760001 | 0.639593 | 0.598203 | 0.654436 | 0.583173 | 0.655640 |
| joint_residual_behavior_neural_multiview_knn_resid | 0.667526 | 0.603389 | 0.703356 | 0.828776 | 0.676851 | 0.623790 | 0.571500 | 0.665017 |
| joint_panel_neural_residual_knn_resid | 0.668826 | 0.774716 | 0.760302 | 0.670600 | 0.702004 | 0.620331 | 0.524405 | 0.629425 |
| joint_target_qs_residual_pls_knn_resid | 0.669930 | 0.710846 | 0.727426 | 0.737073 | 0.691437 | 0.607206 | 0.514792 | 0.700727 |
| joint_family_residual_pls_knn_resid | 0.670027 | 0.771036 | 0.672501 | 0.781880 | 0.632716 | 0.661037 | 0.487713 | 0.683302 |
| joint_qs_residual_pls_knn_logitresid | 0.670990 | 0.731009 | 0.767479 | 0.741341 | 0.657450 | 0.595667 | 0.531469 | 0.672511 |
| joint_s23_residual_behavior_neural_knn_logitresid | 0.671170 | 0.680643 | 0.802474 | 0.701875 | 0.619955 | 0.674773 | 0.542122 | 0.676350 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.673752 | 0.717849 | 0.774835 | 0.748154 | 0.633165 | 0.636453 | 0.542070 | 0.663740 |
| joint_residual_behavior_neural_multiview_metric_knn_resid | 0.674098 | 0.640295 | 0.685256 | 0.796220 | 0.743890 | 0.633481 | 0.517369 | 0.702172 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.675143 | 0.709569 | 0.789067 | 0.734548 | 0.636865 | 0.645998 | 0.556524 | 0.653427 |
| joint_s23_residual_behavior_neural_metric_knn_logitresid | 0.677114 | 0.675064 | 0.838667 | 0.668315 | 0.612420 | 0.694484 | 0.542049 | 0.708798 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.678630 | 0.826712 | 0.736354 | 0.760618 | 0.652224 | 0.588024 | 0.521071 | 0.665405 |
| joint_residual_behavior_neural_multiview_knn_logitresid | 0.679983 | 0.700836 | 0.772896 | 0.772079 | 0.645164 | 0.631149 | 0.545158 | 0.692597 |
| joint_proto_neural_metric_knn_resid | 0.681141 | 0.681677 | 0.740705 | 0.905697 | 0.553781 | 0.652172 | 0.552310 | 0.681647 |
| joint_neural_mixture_knn_logitresid | 0.684040 | 0.763688 | 0.794052 | 0.787469 | 0.642458 | 0.644174 | 0.524414 | 0.632028 |
| joint_target_qs_residual_pls_knn_logitresid | 0.686710 | 0.744223 | 0.815204 | 0.744268 | 0.673735 | 0.609134 | 0.536420 | 0.683983 |
| joint_residual_pls_knn_resid | 0.686836 | 0.693338 | 0.751285 | 0.820987 | 0.662672 | 0.647452 | 0.544126 | 0.687994 |
| joint_proto_neural_residual_knn_logitresid | 0.689485 | 0.755021 | 0.830099 | 0.829433 | 0.622092 | 0.633057 | 0.509380 | 0.647314 |
| joint_residual_behavior_neural_multiview_metric_knn_logitresid | 0.696562 | 0.739185 | 0.777694 | 0.782232 | 0.676397 | 0.659527 | 0.555416 | 0.685481 |
| joint_family_residual_pls_knn_logitresid | 0.698609 | 0.774116 | 0.781412 | 0.817314 | 0.684322 | 0.627041 | 0.524075 | 0.681985 |
| joint_family_residual_behavior_neural_knn_resid | 0.700056 | 0.739621 | 0.870444 | 0.832161 | 0.634347 | 0.652597 | 0.556189 | 0.615035 |
| joint_panel_neural_residual_knn_logitresid | 0.700865 | 0.859992 | 0.802053 | 0.722901 | 0.698523 | 0.647891 | 0.561814 | 0.612884 |
| joint_residual_pls_knn_logitresid | 0.706448 | 0.777087 | 0.829619 | 0.824495 | 0.673494 | 0.626068 | 0.542234 | 0.672137 |
| joint_residual_behavior_neural_knn_resid | 0.706485 | 0.719100 | 0.765708 | 0.787634 | 0.869408 | 0.597758 | 0.478527 | 0.727262 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_proto_neural_metric_knn_logitresid | 0.708348 | 0.782941 | 0.883543 | 0.864590 | 0.618762 | 0.636065 | 0.511571 | 0.660966 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_family_residual_behavior_neural_metric_knn_resid | 0.713449 | 0.711896 | 0.913314 | 0.944654 | 0.641831 | 0.610843 | 0.558170 | 0.613433 |
| joint_neural_mixture_metric_knn_resid | 0.715262 | 0.773381 | 0.818990 | 0.842292 | 0.704146 | 0.657526 | 0.506357 | 0.704139 |
| joint_neural_context_gate_logreg_logitresid | 0.717215 | 0.725258 | 0.812543 | 0.911946 | 0.671491 | 0.677937 | 0.549663 | 0.671667 |
| joint_target_residual_behavior_neural_knn_resid | 0.726968 | 0.748683 | 0.772170 | 0.910128 | 0.650339 | 0.645942 | 0.588166 | 0.773345 |
| joint_residual_behavior_neural_knn_logitresid | 0.727347 | 0.751246 | 0.865256 | 0.850218 | 0.744860 | 0.633430 | 0.514538 | 0.731884 |
| joint_neural_mixture_metric_knn_logitresid | 0.727987 | 0.794839 | 0.883762 | 0.823513 | 0.674964 | 0.688979 | 0.555079 | 0.674773 |
| joint_family_residual_behavior_neural_knn_logitresid | 0.728562 | 0.785124 | 0.957660 | 0.860979 | 0.620196 | 0.658291 | 0.548940 | 0.668747 |
| joint_neural_gated_mixture_knn_logitresid | 0.731140 | 0.756740 | 0.933788 | 0.826369 | 0.676122 | 0.666965 | 0.565090 | 0.692904 |
| joint_neural_gated_mixture_knn_resid | 0.732921 | 0.793409 | 0.861699 | 0.834197 | 0.731880 | 0.641144 | 0.525550 | 0.742569 |
| joint_target_residual_pls_knn_logitresid | 0.732943 | 0.826319 | 0.983575 | 0.750520 | 0.686365 | 0.630474 | 0.585667 | 0.667682 |
| joint_target_residual_pls_knn_resid | 0.735033 | 0.852688 | 0.906979 | 0.738731 | 0.749948 | 0.627749 | 0.590916 | 0.678222 |
| joint_target_late_residual_behavior_neural_knn_logitresid | 0.735429 | 0.724087 | 0.809040 | 0.846515 | 0.632127 | 0.707106 | 0.616479 | 0.812645 |
| joint_target_late_residual_behavior_neural_knn_resid | 0.738754 | 0.704964 | 0.736080 | 0.769070 | 0.663859 | 0.754960 | 0.596645 | 0.945701 |
| joint_target_late_residual_behavior_neural_metric_knn_resid | 0.746360 | 0.680990 | 0.723494 | 0.753779 | 0.663560 | 0.855196 | 0.603273 | 0.944232 |
| joint_target_late_residual_behavior_neural_metric_knn_logitresid | 0.747406 | 0.726610 | 0.826046 | 0.820901 | 0.666814 | 0.741565 | 0.621245 | 0.828659 |
| joint_family_residual_behavior_neural_metric_knn_logitresid | 0.748080 | 0.793506 | 0.966561 | 0.928333 | 0.617469 | 0.670953 | 0.573605 | 0.686136 |
| joint_target_residual_behavior_neural_knn_logitresid | 0.750440 | 0.790072 | 0.837400 | 0.924125 | 0.683476 | 0.665629 | 0.569843 | 0.782533 |
| joint_residual_behavior_neural_metric_knn_resid | 0.750484 | 0.781174 | 0.798966 | 0.809501 | 0.922680 | 0.673863 | 0.483876 | 0.783330 |
| joint_residual_behavior_neural_metric_knn_logitresid | 0.754402 | 0.804811 | 0.881055 | 0.868067 | 0.762882 | 0.679344 | 0.530975 | 0.753677 |
| joint_target_neural_residual_knn_resid | 0.754831 | 0.763563 | 1.001577 | 0.877201 | 0.651086 | 0.732022 | 0.567627 | 0.690741 |
| joint_neural_context_gate_logreg_resid | 0.759864 | 0.751521 | 0.814003 | 0.916605 | 0.826230 | 0.720852 | 0.589603 | 0.700231 |
| joint_target_residual_behavior_neural_metric_knn_resid | 0.765315 | 0.832025 | 0.791595 | 0.908893 | 0.673354 | 0.690370 | 0.606156 | 0.854812 |
| joint_target_residual_behavior_neural_metric_knn_logitresid | 0.772646 | 0.828938 | 0.886561 | 0.921980 | 0.698188 | 0.688521 | 0.579355 | 0.804977 |
| joint_neural_gated_mixture_metric_knn_resid | 0.778566 | 0.824031 | 0.905162 | 0.895942 | 0.797418 | 0.672426 | 0.519671 | 0.835310 |
| joint_target_neural_residual_knn_logitresid | 0.778834 | 0.825243 | 0.991503 | 0.935810 | 0.690472 | 0.701133 | 0.585972 | 0.721703 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.782425 | 0.834145 | 0.996051 | 0.872631 | 0.722713 | 0.716205 | 0.587036 | 0.748190 |
| joint_neural_context_attention_knn_logitresid | 0.782470 | 0.815056 | 0.962381 | 0.877863 | 0.747228 | 0.713823 | 0.579157 | 0.781778 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_neural_context_attention_knn_resid | 0.827115 | 0.826881 | 1.090270 | 0.877757 | 0.794695 | 0.759610 | 0.576468 | 0.864125 |
| joint_neural_context_metric_attention_knn_logitresid | 0.890364 | 0.921530 | 1.150144 | 1.040979 | 0.771460 | 0.791063 | 0.671476 | 0.885897 |
| joint_neural_context_metric_attention_knn_resid | 0.945923 | 0.959395 | 1.261244 | 1.009442 | 0.895372 | 0.875530 | 0.626351 | 0.994125 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss | residual_neighborhood_k | residual_neighborhood_target_dim | residual_neighborhood_mean_distance | residual_behavior_neural_latent_dim | residual_behavior_neural_best_loss | residual_behavior_multiview_neural_latent_dim | residual_behavior_multiview_neural_best_loss | q_residual_neighborhood_target_dim | q_residual_neighborhood_mean_distance | s_residual_neighborhood_target_dim | s_residual_neighborhood_mean_distance | q_residual_behavior_neural_latent_dim | q_residual_behavior_neural_best_loss | s_residual_behavior_neural_latent_dim | s_residual_behavior_neural_best_loss | s23_residual_neighborhood_target_dim | s23_residual_neighborhood_mean_distance | s23_late_residual_neighborhood_target_dim | s23_late_residual_neighborhood_mean_distance | s23_residual_behavior_neural_latent_dim | s23_residual_behavior_neural_best_loss | s23_late_residual_behavior_neural_latent_dim | s23_late_residual_behavior_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.332464 | 8 | 8 | 10 | 0.261885 | 8 | 8 | 10 | 0.380088 | 10 | 0.361090 | 9 | 6235.394531 | 66 | 10 | 0.418651 | 10 | 0.427098 | 31 | 90 | 0.823523 | 10 | 0.321041 | 10 | 0.432103 | 42 | 0.464778 | 54 | 0.593031 | 8 | 0.368978 | 8 | 0.386876 | 30 | 0.414154 | 30 | 0.405236 | 7 | 0.395181 | 6 | 0.413674 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.310806 | 8 | 8 | 10 | 0.269115 | 8 | 8 | 10 | 0.403951 | 10 | 0.379427 | 9 | 6522.235352 | 66 | 10 | 0.420103 | 10 | 0.392019 | 31 | 90 | 0.846580 | 10 | 0.343848 | 10 | 0.418042 | 42 | 0.507786 | 54 | 0.618772 | 8 | 0.365002 | 8 | 0.351702 | 30 | 0.446787 | 30 | 0.428214 | 7 | 0.402020 | 6 | 0.411927 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.305055 | 8 | 8 | 10 | 0.248486 | 8 | 8 | 10 | 0.371749 | 10 | 0.311085 | 9 | 6314.656738 | 66 | 10 | 0.383036 | 10 | 0.397534 | 31 | 90 | 0.830860 | 10 | 0.365644 | 10 | 0.401144 | 42 | 0.471077 | 54 | 0.602823 | 8 | 0.349627 | 8 | 0.377427 | 30 | 0.428784 | 30 | 0.427608 | 7 | 0.409504 | 6 | 0.377033 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.343274 | 8 | 8 | 10 | 0.262315 | 8 | 8 | 10 | 0.406293 | 10 | 0.354541 | 9 | 6503.784668 | 66 | 10 | 0.405808 | 10 | 0.372733 | 31 | 90 | 0.819843 | 10 | 0.375527 | 10 | 0.385760 | 42 | 0.480370 | 54 | 0.604707 | 8 | 0.355081 | 8 | 0.395115 | 30 | 0.447312 | 30 | 0.489343 | 7 | 0.384115 | 6 | 0.354762 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.330941 | 8 | 8 | 10 | 0.208687 | 8 | 8 | 10 | 0.390228 | 10 | 0.330260 | 9 | 6419.064453 | 66 | 10 | 0.409398 | 10 | 0.420975 | 31 | 90 | 0.812316 | 10 | 0.369061 | 10 | 0.402779 | 42 | 0.490667 | 54 | 0.600457 | 8 | 0.347600 | 8 | 0.407072 | 30 | 0.438293 | 30 | 0.469837 | 7 | 0.419606 | 6 | 0.400304 |
