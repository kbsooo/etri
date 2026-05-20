# Joint state-space encoder

- Base OOF: `0.478230`
- Best source: `base`
- Best source OOF: `0.478230`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.478230 | 0.521789 | 0.534703 | 0.498183 | 0.467950 | 0.451165 | 0.408038 | 0.465779 |
| joint_proto_mix | 0.492481 | 0.534818 | 0.553142 | 0.516852 | 0.478933 | 0.463292 | 0.421377 | 0.478955 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.510968 | 0.571471 | 0.576133 | 0.535777 | 0.496064 | 0.473741 | 0.427703 | 0.495885 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.511106 | 0.577211 | 0.580148 | 0.531308 | 0.489394 | 0.468616 | 0.432410 | 0.498657 |
| joint_neighbor_logreg | 0.512709 | 0.539196 | 0.570395 | 0.534898 | 0.524595 | 0.489376 | 0.451649 | 0.478851 |
| joint_local_logreg | 0.513432 | 0.540238 | 0.570611 | 0.532003 | 0.522118 | 0.492198 | 0.447699 | 0.489160 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.517078 | 0.564636 | 0.580387 | 0.562916 | 0.514103 | 0.483310 | 0.431148 | 0.483043 |
| joint_metric_neighbor_logreg | 0.518112 | 0.543463 | 0.577752 | 0.546145 | 0.528738 | 0.492592 | 0.452405 | 0.485688 |
| joint_residual_metric_neighbor_logreg | 0.518608 | 0.543054 | 0.584047 | 0.541792 | 0.533047 | 0.491333 | 0.450997 | 0.485984 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.528132 | 0.611146 | 0.586730 | 0.560203 | 0.520671 | 0.493854 | 0.439038 | 0.485281 |
| joint_neighbor_hgb | 0.536122 | 0.566255 | 0.606465 | 0.560575 | 0.502974 | 0.512045 | 0.466358 | 0.538181 |
| joint_residual_metric_neighbor_hgb | 0.541953 | 0.575263 | 0.613571 | 0.574938 | 0.504850 | 0.506670 | 0.473201 | 0.545177 |
| joint_metric_neighbor_hgb | 0.542970 | 0.582553 | 0.616625 | 0.573068 | 0.503962 | 0.507684 | 0.467103 | 0.549795 |
| joint_residual_pls_neighbor_logreg | 0.549643 | 0.609931 | 0.594835 | 0.606910 | 0.555015 | 0.510352 | 0.465779 | 0.504677 |
| joint_residual_pls_local_logreg | 0.552620 | 0.607952 | 0.600836 | 0.612488 | 0.559592 | 0.509806 | 0.469333 | 0.508336 |
| joint_local_hgb | 0.554669 | 0.582333 | 0.644577 | 0.576527 | 0.520301 | 0.530867 | 0.470168 | 0.557907 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.561321 | 0.607858 | 0.644235 | 0.579725 | 0.532958 | 0.530142 | 0.493261 | 0.541070 |
| joint_neural_context_bin_gate_hgb_resid | 0.561881 | 0.611732 | 0.658747 | 0.576649 | 0.525030 | 0.522217 | 0.483023 | 0.555767 |
| joint_residual_contrast_hgb | 0.564266 | 0.600563 | 0.658652 | 0.592471 | 0.546634 | 0.517448 | 0.476461 | 0.557629 |
| joint_cross_family_residual_pls_knn_resid | 0.567387 | 0.634854 | 0.608204 | 0.612964 | 0.577778 | 0.497989 | 0.503333 | 0.536589 |
| joint_residual_pls_neighbor_hgb | 0.569457 | 0.626632 | 0.644301 | 0.622484 | 0.525129 | 0.513957 | 0.483946 | 0.569746 |
| joint_neural_learned_gate_knn_resid | 0.575855 | 0.609366 | 0.680849 | 0.628699 | 0.556287 | 0.532733 | 0.468441 | 0.554613 |
| joint_neural_bin_gate_knn_resid | 0.576783 | 0.608192 | 0.685885 | 0.626993 | 0.555014 | 0.532361 | 0.471126 | 0.557907 |
| joint_residual_contrast_logreg | 0.582485 | 0.605303 | 0.655756 | 0.616103 | 0.591221 | 0.544541 | 0.498062 | 0.566409 |
| joint_residual_pls_local_hgb | 0.583485 | 0.634226 | 0.667909 | 0.638250 | 0.542204 | 0.544684 | 0.484336 | 0.572789 |
| joint_neural_cross_family_residual_knn_resid | 0.584411 | 0.676553 | 0.707339 | 0.571455 | 0.558909 | 0.503246 | 0.517662 | 0.555714 |
| joint_cross_family_residual_pls_knn_logitresid | 0.586681 | 0.649551 | 0.673172 | 0.641223 | 0.570926 | 0.503957 | 0.504259 | 0.563682 |
| joint_pls_knn_resid | 0.589697 | 0.607642 | 0.707111 | 0.673761 | 0.565426 | 0.557299 | 0.472809 | 0.543833 |
| joint_s23_late_residual_behavior_neural_knn_resid | 0.589969 | 0.596420 | 0.626725 | 0.625454 | 0.507484 | 0.600092 | 0.526535 | 0.647073 |
| joint_cross_family_late_residual_behavior_neural_knn_resid | 0.592286 | 0.658161 | 0.671621 | 0.655854 | 0.615351 | 0.509610 | 0.465805 | 0.569598 |
| joint_cross_family_late_residual_behavior_neural_metric_knn_resid | 0.592463 | 0.655752 | 0.679938 | 0.676740 | 0.615424 | 0.490258 | 0.476337 | 0.552789 |
| joint_s23_late_residual_behavior_neural_metric_knn_resid | 0.596140 | 0.606939 | 0.650067 | 0.612482 | 0.511119 | 0.619466 | 0.546046 | 0.626858 |
| joint_cross_family_residual_behavior_neural_knn_resid | 0.596669 | 0.647956 | 0.708324 | 0.686172 | 0.623107 | 0.491101 | 0.470839 | 0.549183 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.597960 | 0.657589 | 0.613412 | 0.608562 | 0.557542 | 0.618468 | 0.567696 | 0.562454 |
| joint_residual_metric_knn_resid | 0.598245 | 0.627508 | 0.745945 | 0.649871 | 0.591229 | 0.546515 | 0.475912 | 0.550734 |
| joint_cross_family_residual_behavior_neural_metric_knn_resid | 0.598950 | 0.648943 | 0.720196 | 0.664447 | 0.599093 | 0.491144 | 0.469805 | 0.599023 |
| joint_metric_knn_resid | 0.602248 | 0.636808 | 0.731699 | 0.649596 | 0.584002 | 0.561130 | 0.476981 | 0.575521 |
| joint_neural_cross_family_residual_knn_logitresid | 0.603832 | 0.691424 | 0.731951 | 0.620167 | 0.585628 | 0.529476 | 0.482231 | 0.585946 |
| joint_attention_knn_resid | 0.607077 | 0.626858 | 0.729717 | 0.683355 | 0.566209 | 0.568817 | 0.485793 | 0.588792 |
| joint_neural_residual_knn_resid | 0.611241 | 0.669737 | 0.650764 | 0.667183 | 0.635706 | 0.560991 | 0.462309 | 0.631997 |
| joint_metric_attention_knn_resid | 0.612848 | 0.657981 | 0.754673 | 0.659799 | 0.581458 | 0.556335 | 0.487213 | 0.592477 |
| joint_neural_s_residual_knn_resid | 0.615977 | 0.676553 | 0.707339 | 0.571455 | 0.595545 | 0.596650 | 0.523683 | 0.640613 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.616179 | 0.679321 | 0.682865 | 0.690659 | 0.564812 | 0.604425 | 0.508057 | 0.583114 |
| joint_neural_context_gate_hgb_resid | 0.619457 | 0.655968 | 0.729655 | 0.668350 | 0.572762 | 0.586573 | 0.520977 | 0.601916 |
| joint_q_residual_pls_knn_resid | 0.619503 | 0.749673 | 0.704035 | 0.767124 | 0.577778 | 0.497989 | 0.503333 | 0.536589 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.620337 | 0.715209 | 0.730826 | 0.715669 | 0.564562 | 0.553526 | 0.472348 | 0.590217 |
| joint_neural_context_gate_hgb_logitresid | 0.621492 | 0.656805 | 0.736923 | 0.678839 | 0.573812 | 0.588975 | 0.524858 | 0.590234 |
| joint_cross_family_residual_behavior_neural_knn_logitresid | 0.622840 | 0.695692 | 0.772761 | 0.680769 | 0.594731 | 0.534735 | 0.485316 | 0.595879 |
| joint_neural_multiview_s_residual_knn_resid | 0.625063 | 0.657589 | 0.613412 | 0.608562 | 0.646929 | 0.634124 | 0.524640 | 0.690187 |
| joint_s_residual_pls_knn_resid | 0.627053 | 0.634854 | 0.608204 | 0.612964 | 0.664465 | 0.652493 | 0.511944 | 0.704450 |
| joint_cross_family_residual_behavior_neural_metric_knn_logitresid | 0.627214 | 0.678806 | 0.803078 | 0.667422 | 0.609392 | 0.536510 | 0.486806 | 0.608481 |
| joint_cross_family_late_residual_behavior_neural_metric_knn_logitresid | 0.628440 | 0.697709 | 0.730779 | 0.652968 | 0.617542 | 0.562681 | 0.514458 | 0.622946 |
| joint_cross_family_late_residual_behavior_neural_knn_logitresid | 0.630725 | 0.706361 | 0.728198 | 0.649938 | 0.612230 | 0.566029 | 0.521813 | 0.630503 |
| joint_pls_knn_logitresid | 0.631228 | 0.674332 | 0.776726 | 0.736797 | 0.581489 | 0.555636 | 0.511507 | 0.582109 |
| joint_neural_s_residual_knn_logitresid | 0.632967 | 0.691424 | 0.731951 | 0.620167 | 0.635767 | 0.608537 | 0.507545 | 0.635381 |
| joint_neural_qs_residual_knn_resid | 0.633569 | 0.719304 | 0.738254 | 0.748372 | 0.612437 | 0.543685 | 0.485334 | 0.587596 |
| joint_neural_q_residual_knn_resid | 0.634776 | 0.734497 | 0.756902 | 0.816505 | 0.558909 | 0.503246 | 0.517662 | 0.555714 |
| joint_s23_late_residual_behavior_neural_knn_logitresid | 0.635021 | 0.655530 | 0.704856 | 0.641578 | 0.570666 | 0.643566 | 0.558804 | 0.670146 |
| joint_neural_residual_knn_logitresid | 0.635073 | 0.688379 | 0.748678 | 0.705100 | 0.628621 | 0.560612 | 0.517030 | 0.597094 |
| joint_metric_knn_logitresid | 0.642054 | 0.696853 | 0.766963 | 0.710902 | 0.610926 | 0.570203 | 0.519695 | 0.618838 |
| joint_s_residual_pls_knn_logitresid | 0.643103 | 0.649551 | 0.673172 | 0.641223 | 0.667883 | 0.628790 | 0.532487 | 0.708611 |
| joint_s23_late_residual_behavior_neural_metric_knn_logitresid | 0.643114 | 0.647247 | 0.722299 | 0.660633 | 0.574902 | 0.661914 | 0.563320 | 0.671484 |
| joint_residual_metric_knn_logitresid | 0.646356 | 0.702318 | 0.770324 | 0.721802 | 0.623361 | 0.571198 | 0.516608 | 0.618884 |
| joint_q_residual_pls_knn_logitresid | 0.649426 | 0.749779 | 0.829735 | 0.823645 | 0.570926 | 0.503957 | 0.504259 | 0.563682 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.650035 | 0.679321 | 0.682865 | 0.690659 | 0.666455 | 0.644212 | 0.526640 | 0.660089 |
| joint_proto_neural_residual_knn_resid | 0.651023 | 0.755889 | 0.774119 | 0.736665 | 0.596216 | 0.605534 | 0.483726 | 0.605016 |
| joint_attention_knn_logitresid | 0.651410 | 0.707277 | 0.789467 | 0.762304 | 0.586287 | 0.576742 | 0.533681 | 0.604109 |
| joint_neural_multiview_residual_knn_resid | 0.651921 | 0.669973 | 0.786185 | 0.832269 | 0.636694 | 0.603121 | 0.481102 | 0.554106 |
| joint_neural_context_bin_gate_logreg_resid | 0.654220 | 0.712378 | 0.802972 | 0.758931 | 0.616155 | 0.586120 | 0.498507 | 0.604478 |
| joint_neural_learned_gate_knn_logitresid | 0.655113 | 0.697551 | 0.798569 | 0.734734 | 0.603040 | 0.603209 | 0.506724 | 0.641963 |
| joint_neural_bin_gate_knn_logitresid | 0.655385 | 0.700835 | 0.796011 | 0.728660 | 0.602420 | 0.598979 | 0.513298 | 0.647488 |
| joint_proto_neural_multiview_residual_knn_resid | 0.656727 | 0.671345 | 0.827817 | 0.645017 | 0.592142 | 0.671565 | 0.537354 | 0.651846 |
| joint_qs_residual_pls_knn_resid | 0.657059 | 0.684978 | 0.735032 | 0.751575 | 0.642319 | 0.605917 | 0.527389 | 0.652203 |
| joint_neural_multiview_qs_residual_knn_resid | 0.657531 | 0.636428 | 0.749994 | 0.847419 | 0.603279 | 0.598913 | 0.543219 | 0.623463 |
| joint_metric_attention_knn_logitresid | 0.660516 | 0.732535 | 0.776963 | 0.732243 | 0.614811 | 0.587154 | 0.542485 | 0.637422 |
| joint_neural_q_residual_knn_logitresid | 0.664825 | 0.784018 | 0.837151 | 0.849323 | 0.585628 | 0.529476 | 0.482231 | 0.585946 |
| joint_neural_multiview_q_residual_knn_resid | 0.666855 | 0.711971 | 0.839579 | 0.810272 | 0.557542 | 0.618468 | 0.567696 | 0.562454 |
| joint_neural_qs_residual_knn_logitresid | 0.668630 | 0.782786 | 0.789081 | 0.751924 | 0.615193 | 0.588418 | 0.510589 | 0.642421 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.670354 | 0.729112 | 0.861432 | 0.841526 | 0.564812 | 0.604425 | 0.508057 | 0.583114 |
| joint_neural_multiview_residual_knn_logitresid | 0.670628 | 0.710286 | 0.784589 | 0.809970 | 0.615957 | 0.631513 | 0.511326 | 0.630753 |
| joint_proto_neural_multiview_metric_knn_resid | 0.672510 | 0.704144 | 0.863650 | 0.680333 | 0.593257 | 0.689931 | 0.504160 | 0.672098 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.674569 | 0.709752 | 0.849570 | 0.717468 | 0.611935 | 0.630582 | 0.562535 | 0.640142 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.677315 | 0.673455 | 0.794360 | 0.844717 | 0.622884 | 0.624275 | 0.530370 | 0.651148 |
| joint_late_residual_behavior_neural_knn_resid | 0.677748 | 0.622089 | 0.782364 | 0.743125 | 0.658418 | 0.681125 | 0.543548 | 0.713570 |
| joint_target_neural_multiview_residual_knn_resid | 0.677900 | 0.798403 | 0.788437 | 0.797649 | 0.636088 | 0.572053 | 0.496899 | 0.655768 |
| joint_residual_pls_knn_resid | 0.678076 | 0.735588 | 0.747432 | 0.788325 | 0.650318 | 0.629142 | 0.528643 | 0.667081 |
| joint_family_late_residual_behavior_neural_knn_resid | 0.678304 | 0.674445 | 0.791060 | 0.850914 | 0.604326 | 0.648440 | 0.536766 | 0.642178 |
| joint_family_late_residual_behavior_neural_metric_knn_resid | 0.678711 | 0.670841 | 0.775266 | 0.858572 | 0.596901 | 0.680385 | 0.513569 | 0.655444 |
| joint_qs_residual_pls_knn_logitresid | 0.679160 | 0.725424 | 0.822965 | 0.767890 | 0.648034 | 0.597441 | 0.529591 | 0.662772 |
| joint_family_residual_pls_knn_resid | 0.679169 | 0.749673 | 0.704035 | 0.767124 | 0.664465 | 0.652493 | 0.511944 | 0.704450 |
| joint_proto_neural_residual_knn_logitresid | 0.680021 | 0.787510 | 0.814706 | 0.772397 | 0.641525 | 0.595417 | 0.521883 | 0.626709 |
| joint_panel_neural_multiview_residual_knn_resid | 0.680490 | 0.715140 | 0.845201 | 0.817395 | 0.597947 | 0.584213 | 0.525557 | 0.677977 |
| joint_target_qs_residual_pls_knn_resid | 0.681434 | 0.725429 | 0.793137 | 0.766399 | 0.688817 | 0.604705 | 0.518162 | 0.673387 |
| joint_proto_neural_metric_knn_resid | 0.682746 | 0.799660 | 0.740976 | 0.826927 | 0.680938 | 0.610830 | 0.507943 | 0.611950 |
| joint_panel_neural_residual_knn_resid | 0.683477 | 0.877649 | 0.890413 | 0.650440 | 0.653770 | 0.606210 | 0.519627 | 0.586232 |
| joint_residual_behavior_neural_multiview_knn_resid | 0.686250 | 0.611081 | 0.727247 | 0.832594 | 0.673888 | 0.637959 | 0.541670 | 0.779308 |
| joint_family_residual_behavior_neural_knn_resid | 0.688975 | 0.695484 | 0.812805 | 0.826021 | 0.626224 | 0.671908 | 0.534227 | 0.656157 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.691126 | 0.714323 | 0.830040 | 0.793786 | 0.610527 | 0.652625 | 0.554849 | 0.681728 |
| joint_s23_residual_behavior_neural_metric_knn_resid | 0.693052 | 0.647273 | 0.845907 | 0.623605 | 0.620735 | 0.780791 | 0.550440 | 0.782616 |
| joint_s23_residual_behavior_neural_knn_logitresid | 0.693318 | 0.680530 | 0.839976 | 0.683230 | 0.614176 | 0.753503 | 0.570560 | 0.711255 |
| joint_target_qs_residual_pls_knn_logitresid | 0.693886 | 0.747721 | 0.858723 | 0.764426 | 0.667267 | 0.601262 | 0.543488 | 0.674315 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.696275 | 0.745710 | 0.871270 | 0.743549 | 0.637865 | 0.651514 | 0.565158 | 0.658860 |
| joint_neural_mixture_knn_resid | 0.698135 | 0.805727 | 0.816236 | 0.820695 | 0.634185 | 0.594892 | 0.538959 | 0.676254 |
| joint_s23_residual_behavior_neural_knn_resid | 0.699225 | 0.633869 | 0.846917 | 0.645486 | 0.646388 | 0.803281 | 0.555229 | 0.763403 |
| joint_neural_mixture_knn_logitresid | 0.701628 | 0.790443 | 0.843230 | 0.817001 | 0.631939 | 0.637164 | 0.532633 | 0.658982 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.701640 | 0.799512 | 0.857832 | 0.830666 | 0.644748 | 0.593225 | 0.528655 | 0.656844 |
| joint_residual_behavior_neural_knn_resid | 0.702370 | 0.745092 | 0.850417 | 0.722951 | 0.743322 | 0.616512 | 0.460491 | 0.777804 |
| joint_family_late_residual_behavior_neural_knn_logitresid | 0.702776 | 0.730045 | 0.901380 | 0.833426 | 0.627511 | 0.643778 | 0.531218 | 0.652071 |
| joint_panel_neural_residual_knn_logitresid | 0.703200 | 0.896654 | 0.882886 | 0.689954 | 0.679242 | 0.648745 | 0.532655 | 0.592268 |
| joint_residual_behavior_neural_multiview_knn_logitresid | 0.703665 | 0.701215 | 0.802521 | 0.810100 | 0.690114 | 0.630664 | 0.541517 | 0.749522 |
| joint_s23_residual_behavior_neural_metric_knn_logitresid | 0.705306 | 0.695723 | 0.864132 | 0.662536 | 0.623101 | 0.757771 | 0.573130 | 0.760748 |
| joint_family_residual_pls_knn_logitresid | 0.705847 | 0.749779 | 0.829735 | 0.823645 | 0.667883 | 0.628790 | 0.532487 | 0.708611 |
| joint_residual_pls_knn_logitresid | 0.705997 | 0.779953 | 0.842966 | 0.806710 | 0.663234 | 0.626722 | 0.549066 | 0.673328 |
| joint_family_residual_behavior_neural_metric_knn_resid | 0.706351 | 0.776337 | 0.862008 | 0.824677 | 0.587293 | 0.662296 | 0.540808 | 0.691038 |
| joint_late_residual_behavior_neural_metric_knn_resid | 0.707591 | 0.679781 | 0.812914 | 0.741153 | 0.680739 | 0.707199 | 0.568772 | 0.762581 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_proto_neural_metric_knn_logitresid | 0.709956 | 0.842385 | 0.816606 | 0.831729 | 0.670420 | 0.626571 | 0.536197 | 0.645781 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_late_residual_behavior_neural_knn_logitresid | 0.711358 | 0.696845 | 0.861986 | 0.746359 | 0.682262 | 0.678805 | 0.576560 | 0.736688 |
| joint_family_late_residual_behavior_neural_metric_knn_logitresid | 0.712176 | 0.719308 | 0.912371 | 0.848461 | 0.656575 | 0.652678 | 0.520318 | 0.675522 |
| joint_target_residual_pls_knn_resid | 0.712509 | 0.841776 | 0.808991 | 0.684847 | 0.735201 | 0.646473 | 0.622449 | 0.647828 |
| joint_residual_behavior_neural_multiview_metric_knn_resid | 0.715213 | 0.631688 | 0.778302 | 0.872341 | 0.687895 | 0.642779 | 0.540937 | 0.852551 |
| joint_family_residual_behavior_neural_knn_logitresid | 0.720071 | 0.791108 | 0.894238 | 0.850697 | 0.594291 | 0.675968 | 0.558991 | 0.675201 |
| joint_late_residual_behavior_neural_metric_knn_logitresid | 0.720241 | 0.723550 | 0.860619 | 0.740536 | 0.688469 | 0.706267 | 0.579411 | 0.742832 |
| joint_residual_behavior_neural_metric_knn_resid | 0.722464 | 0.801123 | 0.831404 | 0.768258 | 0.740509 | 0.672483 | 0.466282 | 0.777190 |
| joint_residual_behavior_neural_multiview_metric_knn_logitresid | 0.723666 | 0.703006 | 0.830988 | 0.847019 | 0.707808 | 0.654149 | 0.546286 | 0.776402 |
| joint_residual_behavior_neural_knn_logitresid | 0.729081 | 0.766974 | 0.910648 | 0.799917 | 0.699786 | 0.660899 | 0.515335 | 0.750007 |
| joint_family_residual_behavior_neural_metric_knn_logitresid | 0.731717 | 0.825333 | 0.929427 | 0.846739 | 0.600544 | 0.673284 | 0.560119 | 0.686570 |
| joint_target_residual_pls_knn_logitresid | 0.733881 | 0.822410 | 0.958586 | 0.729459 | 0.699229 | 0.658058 | 0.588581 | 0.680841 |
| joint_target_late_residual_behavior_neural_knn_logitresid | 0.736094 | 0.744194 | 0.754729 | 0.766184 | 0.710771 | 0.742297 | 0.608720 | 0.825762 |
| joint_residual_behavior_neural_metric_knn_logitresid | 0.745742 | 0.793415 | 0.911308 | 0.841608 | 0.704635 | 0.684340 | 0.516475 | 0.768410 |
| joint_target_late_residual_behavior_neural_metric_knn_logitresid | 0.746770 | 0.733778 | 0.792848 | 0.774514 | 0.704888 | 0.751422 | 0.615084 | 0.854855 |
| joint_neural_context_gate_logreg_logitresid | 0.747121 | 0.816722 | 0.907634 | 0.879842 | 0.683297 | 0.686956 | 0.557539 | 0.697857 |
| joint_neural_mixture_metric_knn_logitresid | 0.752787 | 0.862676 | 0.916332 | 0.878553 | 0.684085 | 0.678048 | 0.547128 | 0.702689 |
| joint_target_residual_behavior_neural_knn_resid | 0.756288 | 0.735122 | 0.863872 | 0.929237 | 0.719556 | 0.636567 | 0.551118 | 0.858540 |
| joint_neural_mixture_metric_knn_resid | 0.758368 | 0.852700 | 0.905692 | 0.862020 | 0.711146 | 0.670031 | 0.526493 | 0.780493 |
| joint_target_late_residual_behavior_neural_metric_knn_resid | 0.759261 | 0.694119 | 0.687811 | 0.724848 | 0.719152 | 0.869611 | 0.641635 | 0.977652 |
| joint_neural_gated_mixture_knn_logitresid | 0.761719 | 0.840696 | 0.891480 | 0.857895 | 0.704292 | 0.745963 | 0.572260 | 0.719450 |
| joint_target_residual_behavior_neural_knn_logitresid | 0.764418 | 0.789829 | 0.925506 | 0.925106 | 0.704907 | 0.657149 | 0.578767 | 0.769662 |
| joint_target_late_residual_behavior_neural_knn_resid | 0.767248 | 0.737733 | 0.667547 | 0.752631 | 0.740992 | 0.830825 | 0.658050 | 0.982961 |
| joint_neural_context_attention_knn_logitresid | 0.774523 | 0.895266 | 0.980904 | 0.837512 | 0.728408 | 0.672035 | 0.563090 | 0.744450 |
| joint_neural_gated_mixture_knn_resid | 0.783020 | 0.819173 | 0.907103 | 0.880299 | 0.704370 | 0.755158 | 0.589166 | 0.825869 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_neural_context_gate_logreg_resid | 0.788251 | 0.863434 | 0.964627 | 0.843016 | 0.776573 | 0.720329 | 0.575350 | 0.774425 |
| joint_target_neural_residual_knn_logitresid | 0.788327 | 0.904764 | 1.063407 | 0.843468 | 0.730280 | 0.675658 | 0.573879 | 0.726832 |
| joint_target_residual_behavior_neural_metric_knn_logitresid | 0.789628 | 0.784799 | 0.946301 | 0.914362 | 0.753536 | 0.668879 | 0.640448 | 0.819069 |
| joint_target_residual_behavior_neural_metric_knn_resid | 0.793510 | 0.733682 | 0.873444 | 0.933383 | 0.757843 | 0.678562 | 0.637438 | 0.940217 |
| joint_neural_context_attention_knn_resid | 0.809832 | 0.952166 | 0.972304 | 0.940685 | 0.749885 | 0.685216 | 0.529765 | 0.838801 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.811292 | 0.926957 | 0.940242 | 0.892155 | 0.739954 | 0.783877 | 0.617152 | 0.778705 |
| joint_target_neural_residual_knn_resid | 0.814582 | 0.866073 | 1.172001 | 0.879628 | 0.825017 | 0.694237 | 0.545768 | 0.719350 |
| joint_neural_gated_mixture_metric_knn_resid | 0.845188 | 0.959792 | 0.940282 | 0.912787 | 0.768570 | 0.804770 | 0.641534 | 0.888581 |
| joint_neural_context_metric_attention_knn_logitresid | 0.874314 | 1.001128 | 1.122545 | 0.955823 | 0.769454 | 0.772772 | 0.659131 | 0.839347 |
| joint_neural_context_metric_attention_knn_resid | 0.915265 | 1.068863 | 1.166748 | 1.020062 | 0.892315 | 0.766279 | 0.556831 | 0.935762 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss | residual_neighborhood_k | residual_neighborhood_target_dim | residual_neighborhood_mean_distance | residual_behavior_neural_latent_dim | residual_behavior_neural_best_loss | residual_behavior_multiview_neural_latent_dim | residual_behavior_multiview_neural_best_loss | q_residual_neighborhood_target_dim | q_residual_neighborhood_mean_distance | s_residual_neighborhood_target_dim | s_residual_neighborhood_mean_distance | q_residual_behavior_neural_latent_dim | q_residual_behavior_neural_best_loss | s_residual_behavior_neural_latent_dim | s_residual_behavior_neural_best_loss | s23_residual_neighborhood_target_dim | s23_residual_neighborhood_mean_distance | s23_late_residual_neighborhood_target_dim | s23_late_residual_neighborhood_mean_distance | s23_residual_behavior_neural_latent_dim | s23_residual_behavior_neural_best_loss | s23_late_residual_behavior_neural_latent_dim | s23_late_residual_behavior_neural_best_loss | late_residual_neighborhood_target_dim | late_residual_neighborhood_mean_distance | q_late_residual_neighborhood_target_dim | q_late_residual_neighborhood_mean_distance | s_late_residual_neighborhood_target_dim | s_late_residual_neighborhood_mean_distance | late_residual_behavior_neural_latent_dim | late_residual_behavior_neural_best_loss | q_late_residual_behavior_neural_latent_dim | q_late_residual_behavior_neural_best_loss | s_late_residual_behavior_neural_latent_dim | s_late_residual_behavior_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.329666 | 8 | 8 | 10 | 0.246774 | 8 | 8 | 10 | 0.377489 | 10 | 0.345407 | 9 | 6233.644043 | 66 | 10 | 0.415688 | 10 | 0.420363 | 31 | 90 | 0.823582 | 10 | 0.357545 | 10 | 0.410809 | 42 | 0.465841 | 54 | 0.594105 | 8 | 0.370782 | 8 | 0.383844 | 30 | 0.415403 | 30 | 0.406925 | 7 | 0.388363 | 6 | 0.416018 | 90 | 0.799147 | 42 | 0.500222 | 54 | 0.612160 | 9 | 0.382061 | 7 | 0.368736 | 7 | 0.407212 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.306520 | 8 | 8 | 10 | 0.286915 | 8 | 8 | 10 | 0.419785 | 10 | 0.362375 | 9 | 6520.095215 | 66 | 10 | 0.385354 | 10 | 0.371687 | 31 | 90 | 0.846399 | 10 | 0.362458 | 10 | 0.420579 | 42 | 0.509465 | 54 | 0.620017 | 8 | 0.344136 | 8 | 0.362904 | 30 | 0.448129 | 30 | 0.429858 | 7 | 0.383537 | 6 | 0.418357 | 90 | 0.807505 | 42 | 0.527202 | 54 | 0.632297 | 9 | 0.367201 | 7 | 0.360861 | 7 | 0.378678 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.318483 | 8 | 8 | 10 | 0.242608 | 8 | 8 | 10 | 0.374353 | 10 | 0.304525 | 9 | 6326.949707 | 66 | 10 | 0.419947 | 10 | 0.403496 | 31 | 90 | 0.830820 | 10 | 0.364444 | 10 | 0.398619 | 42 | 0.473130 | 54 | 0.603472 | 8 | 0.356292 | 8 | 0.386243 | 30 | 0.429662 | 30 | 0.429090 | 7 | 0.379667 | 6 | 0.371268 | 90 | 0.797561 | 42 | 0.517487 | 54 | 0.631111 | 9 | 0.377414 | 7 | 0.365489 | 7 | 0.400669 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.338745 | 8 | 8 | 10 | 0.268456 | 8 | 8 | 10 | 0.384859 | 10 | 0.369257 | 9 | 6477.657227 | 66 | 10 | 0.399524 | 10 | 0.374374 | 31 | 90 | 0.819577 | 10 | 0.371148 | 10 | 0.409972 | 42 | 0.481542 | 54 | 0.605166 | 8 | 0.355855 | 8 | 0.387797 | 30 | 0.448097 | 30 | 0.490230 | 7 | 0.393278 | 6 | 0.410767 | 90 | 0.822937 | 42 | 0.556894 | 54 | 0.665917 | 9 | 0.369721 | 7 | 0.330322 | 7 | 0.375480 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.342983 | 8 | 8 | 10 | 0.201393 | 8 | 8 | 10 | 0.383043 | 10 | 0.337081 | 9 | 6405.141113 | 66 | 10 | 0.417209 | 10 | 0.423150 | 31 | 90 | 0.811700 | 10 | 0.367736 | 10 | 0.388690 | 42 | 0.491799 | 54 | 0.600696 | 8 | 0.344063 | 8 | 0.393502 | 30 | 0.438733 | 30 | 0.469311 | 7 | 0.421702 | 6 | 0.368552 | 90 | 0.827108 | 42 | 0.581449 | 54 | 0.663254 | 9 | 0.348293 | 7 | 0.349022 | 7 | 0.412409 |
