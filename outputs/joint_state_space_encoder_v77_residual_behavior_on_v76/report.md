# Joint state-space encoder

- Base OOF: `0.480978`
- Best source: `base`
- Best source OOF: `0.480978`
- Selected raw columns: `594`

## Scores

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| base | 0.480978 | 0.525443 | 0.538870 | 0.501289 | 0.469875 | 0.453129 | 0.411283 | 0.466958 |
| joint_proto_mix | 0.494857 | 0.538043 | 0.555778 | 0.520067 | 0.480490 | 0.465142 | 0.424585 | 0.479898 |
| joint_neural_context_secondhalf_gate_logreg_resid | 0.508575 | 0.571624 | 0.545829 | 0.543758 | 0.517701 | 0.472305 | 0.430227 | 0.478582 |
| joint_neural_context_secondhalf_gate_hgb_resid | 0.510145 | 0.567007 | 0.568023 | 0.541640 | 0.489760 | 0.474172 | 0.428081 | 0.502329 |
| joint_neural_context_secondhalf_gate_logreg_logitresid | 0.510321 | 0.556605 | 0.565381 | 0.546232 | 0.514100 | 0.481142 | 0.424532 | 0.484253 |
| joint_neural_context_secondhalf_gate_hgb_logitresid | 0.512473 | 0.575328 | 0.580360 | 0.534844 | 0.493036 | 0.475319 | 0.429299 | 0.499123 |
| joint_neighbor_logreg | 0.515491 | 0.543192 | 0.574513 | 0.537183 | 0.525826 | 0.492787 | 0.454853 | 0.480086 |
| joint_local_logreg | 0.515870 | 0.543886 | 0.574946 | 0.533859 | 0.523091 | 0.495297 | 0.450023 | 0.489988 |
| joint_metric_neighbor_logreg | 0.521009 | 0.546891 | 0.582473 | 0.549150 | 0.529217 | 0.496376 | 0.455712 | 0.487245 |
| joint_residual_metric_neighbor_logreg | 0.521081 | 0.546328 | 0.585579 | 0.545813 | 0.529546 | 0.494096 | 0.459064 | 0.487142 |
| joint_neighbor_hgb | 0.536686 | 0.572122 | 0.608269 | 0.565025 | 0.498691 | 0.514253 | 0.465868 | 0.532571 |
| joint_metric_neighbor_hgb | 0.543877 | 0.588187 | 0.611456 | 0.577691 | 0.500539 | 0.512559 | 0.473447 | 0.543257 |
| joint_residual_metric_neighbor_hgb | 0.548070 | 0.575089 | 0.622171 | 0.581730 | 0.507479 | 0.518085 | 0.476153 | 0.555787 |
| joint_local_hgb | 0.553081 | 0.583389 | 0.639300 | 0.578495 | 0.515917 | 0.525464 | 0.468273 | 0.560729 |
| joint_cross_family_residual_pls_knn_resid | 0.553452 | 0.593645 | 0.592385 | 0.620497 | 0.543433 | 0.485746 | 0.503784 | 0.534675 |
| joint_residual_pls_neighbor_logreg | 0.554959 | 0.611155 | 0.587870 | 0.619172 | 0.566328 | 0.526706 | 0.463278 | 0.510206 |
| joint_residual_pls_local_logreg | 0.555146 | 0.607814 | 0.593181 | 0.623277 | 0.565007 | 0.520051 | 0.465416 | 0.511277 |
| joint_neural_context_bin_gate_hgb_resid | 0.558384 | 0.615944 | 0.609108 | 0.601942 | 0.519182 | 0.517327 | 0.489691 | 0.555494 |
| joint_neural_context_bin_gate_hgb_logitresid | 0.560878 | 0.631176 | 0.623655 | 0.608277 | 0.511037 | 0.502288 | 0.495623 | 0.554092 |
| joint_neural_learned_gate_knn_resid | 0.565827 | 0.619560 | 0.631278 | 0.615449 | 0.559562 | 0.509453 | 0.469789 | 0.555699 |
| joint_neural_bin_gate_knn_resid | 0.566036 | 0.616732 | 0.630211 | 0.613494 | 0.561741 | 0.510770 | 0.466226 | 0.563075 |
| joint_residual_contrast_hgb | 0.566102 | 0.599276 | 0.657752 | 0.600102 | 0.545901 | 0.518452 | 0.485587 | 0.555646 |
| joint_residual_pls_neighbor_hgb | 0.571141 | 0.631536 | 0.638104 | 0.622220 | 0.542756 | 0.519997 | 0.471954 | 0.571423 |
| joint_neural_multiview_cross_family_residual_knn_resid | 0.571901 | 0.607438 | 0.633247 | 0.588745 | 0.584209 | 0.526360 | 0.523713 | 0.539596 |
| joint_neural_cross_family_residual_knn_resid | 0.582530 | 0.587854 | 0.665065 | 0.632641 | 0.595693 | 0.543024 | 0.490464 | 0.562974 |
| joint_residual_pls_local_hgb | 0.583181 | 0.632793 | 0.662725 | 0.644159 | 0.550059 | 0.542959 | 0.479009 | 0.570561 |
| joint_residual_contrast_logreg | 0.583964 | 0.599784 | 0.660084 | 0.620502 | 0.590840 | 0.548848 | 0.501356 | 0.566334 |
| joint_neural_context_bin_gate_logreg_logitresid | 0.586146 | 0.700157 | 0.642984 | 0.663745 | 0.559213 | 0.519983 | 0.479514 | 0.537429 |
| joint_cross_family_residual_pls_knn_logitresid | 0.586435 | 0.648732 | 0.656596 | 0.612984 | 0.571866 | 0.516342 | 0.522014 | 0.576507 |
| joint_pls_knn_resid | 0.587636 | 0.607871 | 0.682466 | 0.679138 | 0.565007 | 0.557432 | 0.476637 | 0.544900 |
| joint_neural_context_bin_gate_logreg_resid | 0.589774 | 0.676154 | 0.640323 | 0.676878 | 0.599460 | 0.530411 | 0.473340 | 0.531853 |
| joint_metric_knn_resid | 0.599238 | 0.622909 | 0.733716 | 0.654790 | 0.565834 | 0.561498 | 0.480579 | 0.575342 |
| joint_neural_multiview_cross_family_residual_knn_logitresid | 0.604461 | 0.670800 | 0.686487 | 0.634629 | 0.574203 | 0.557847 | 0.515479 | 0.591780 |
| joint_neural_s_residual_knn_resid | 0.604929 | 0.587854 | 0.665065 | 0.632641 | 0.654641 | 0.563030 | 0.479296 | 0.651980 |
| joint_residual_metric_knn_resid | 0.607047 | 0.637433 | 0.762986 | 0.677150 | 0.603401 | 0.541100 | 0.473820 | 0.553438 |
| joint_attention_knn_resid | 0.607471 | 0.625670 | 0.722930 | 0.687221 | 0.565819 | 0.568456 | 0.493095 | 0.589105 |
| joint_s_residual_pls_knn_resid | 0.607514 | 0.593645 | 0.592385 | 0.620497 | 0.673672 | 0.647324 | 0.468203 | 0.656870 |
| joint_neural_context_gate_hgb_resid | 0.609700 | 0.650230 | 0.677421 | 0.660748 | 0.582408 | 0.561597 | 0.524547 | 0.610948 |
| joint_metric_attention_knn_resid | 0.611278 | 0.658443 | 0.747830 | 0.661834 | 0.579909 | 0.553718 | 0.490298 | 0.586914 |
| joint_proto_neural_residual_knn_resid | 0.611726 | 0.689539 | 0.714662 | 0.711510 | 0.571531 | 0.534406 | 0.489624 | 0.570813 |
| joint_neural_context_gate_hgb_logitresid | 0.612377 | 0.649467 | 0.676450 | 0.669910 | 0.568148 | 0.565426 | 0.522458 | 0.634781 |
| joint_neural_multiview_q_residual_knn_resid | 0.612804 | 0.713467 | 0.715999 | 0.686283 | 0.584209 | 0.526360 | 0.523713 | 0.539596 |
| joint_neural_cross_family_residual_knn_logitresid | 0.613437 | 0.650419 | 0.707584 | 0.622403 | 0.611536 | 0.568808 | 0.513417 | 0.619893 |
| joint_neural_multiview_s_residual_knn_resid | 0.615522 | 0.607438 | 0.633247 | 0.588745 | 0.643842 | 0.629881 | 0.501753 | 0.703748 |
| joint_neural_s_residual_knn_logitresid | 0.620184 | 0.650419 | 0.707584 | 0.622403 | 0.635977 | 0.590700 | 0.501176 | 0.633029 |
| joint_neural_qs_residual_knn_resid | 0.620248 | 0.673397 | 0.671933 | 0.724170 | 0.630451 | 0.557756 | 0.490464 | 0.593568 |
| joint_panel_neural_multiview_residual_knn_resid | 0.620622 | 0.707100 | 0.636908 | 0.640109 | 0.659208 | 0.599587 | 0.476821 | 0.624621 |
| joint_neural_multiview_qs_residual_knn_resid | 0.620717 | 0.725052 | 0.607059 | 0.681308 | 0.615016 | 0.571030 | 0.490370 | 0.655185 |
| joint_s_residual_pls_knn_logitresid | 0.622763 | 0.648732 | 0.656596 | 0.612984 | 0.660238 | 0.624277 | 0.494610 | 0.661904 |
| joint_neural_q_residual_knn_resid | 0.623976 | 0.751881 | 0.679837 | 0.743957 | 0.595693 | 0.543024 | 0.490464 | 0.562974 |
| joint_neural_multiview_residual_knn_resid | 0.624585 | 0.701882 | 0.634828 | 0.674394 | 0.721126 | 0.582033 | 0.455483 | 0.602347 |
| joint_q_residual_pls_knn_resid | 0.629584 | 0.812203 | 0.726488 | 0.800761 | 0.543433 | 0.485746 | 0.503784 | 0.534675 |
| joint_proto_neural_multiview_residual_knn_resid | 0.630517 | 0.724420 | 0.664399 | 0.641770 | 0.618066 | 0.587001 | 0.488237 | 0.689727 |
| joint_pls_knn_logitresid | 0.631905 | 0.676035 | 0.770076 | 0.741731 | 0.580776 | 0.555446 | 0.515318 | 0.583952 |
| joint_neural_residual_knn_resid | 0.636908 | 0.717950 | 0.729133 | 0.620760 | 0.680646 | 0.578124 | 0.497155 | 0.634591 |
| joint_residual_behavior_neural_multiview_knn_resid | 0.637188 | 0.666396 | 0.678585 | 0.754207 | 0.656654 | 0.574874 | 0.497966 | 0.631638 |
| joint_neural_bin_gate_knn_logitresid | 0.637300 | 0.708607 | 0.727512 | 0.709636 | 0.604384 | 0.562739 | 0.504299 | 0.643923 |
| joint_neural_learned_gate_knn_logitresid | 0.638082 | 0.705648 | 0.731124 | 0.716046 | 0.610085 | 0.561817 | 0.505848 | 0.636006 |
| joint_neural_multiview_s_residual_knn_logitresid | 0.640641 | 0.670800 | 0.686487 | 0.634629 | 0.626557 | 0.638110 | 0.508685 | 0.719220 |
| joint_neural_multiview_residual_knn_logitresid | 0.641635 | 0.727910 | 0.664617 | 0.739760 | 0.618375 | 0.622312 | 0.495374 | 0.623097 |
| joint_metric_knn_logitresid | 0.643944 | 0.700923 | 0.763655 | 0.717172 | 0.609110 | 0.571476 | 0.524481 | 0.620787 |
| joint_proto_neural_multiview_metric_knn_resid | 0.644926 | 0.764588 | 0.674890 | 0.640825 | 0.627860 | 0.633523 | 0.465379 | 0.707413 |
| joint_neural_qs_residual_knn_logitresid | 0.645478 | 0.714111 | 0.728450 | 0.752014 | 0.617644 | 0.572116 | 0.503399 | 0.630616 |
| joint_neural_multiview_qs_residual_knn_logitresid | 0.646329 | 0.725231 | 0.707860 | 0.735845 | 0.602182 | 0.580583 | 0.508384 | 0.664216 |
| joint_target_neural_multiview_residual_knn_resid | 0.646770 | 0.699438 | 0.686095 | 0.714970 | 0.691985 | 0.562970 | 0.500047 | 0.671887 |
| joint_residual_metric_knn_logitresid | 0.647702 | 0.691232 | 0.781480 | 0.731333 | 0.622909 | 0.569061 | 0.516550 | 0.621346 |
| joint_proto_neural_multiview_residual_knn_logitresid | 0.650579 | 0.739536 | 0.742360 | 0.683116 | 0.596416 | 0.633318 | 0.513664 | 0.645640 |
| joint_qs_residual_pls_knn_resid | 0.650944 | 0.689287 | 0.704358 | 0.707618 | 0.691496 | 0.600028 | 0.503536 | 0.660285 |
| joint_attention_knn_logitresid | 0.651362 | 0.707711 | 0.783182 | 0.766355 | 0.584789 | 0.575866 | 0.535960 | 0.605670 |
| joint_neural_residual_knn_logitresid | 0.651655 | 0.740958 | 0.743984 | 0.670250 | 0.677549 | 0.594756 | 0.506993 | 0.627097 |
| joint_neural_multiview_q_residual_knn_logitresid | 0.651870 | 0.770507 | 0.766904 | 0.786370 | 0.574203 | 0.557847 | 0.515479 | 0.591780 |
| joint_proto_neural_metric_knn_resid | 0.657940 | 0.715411 | 0.744902 | 0.788582 | 0.630377 | 0.603002 | 0.493763 | 0.629544 |
| joint_q_residual_pls_knn_logitresid | 0.660100 | 0.785239 | 0.827887 | 0.820844 | 0.571866 | 0.516342 | 0.522014 | 0.576507 |
| joint_neural_q_residual_knn_logitresid | 0.661316 | 0.734240 | 0.792669 | 0.788648 | 0.611536 | 0.568808 | 0.513417 | 0.619893 |
| joint_metric_attention_knn_logitresid | 0.661657 | 0.735474 | 0.773274 | 0.737867 | 0.612388 | 0.587676 | 0.546067 | 0.638851 |
| joint_panel_neural_multiview_residual_knn_logitresid | 0.661989 | 0.756204 | 0.733415 | 0.694546 | 0.630429 | 0.665126 | 0.498818 | 0.655389 |
| joint_qs_residual_pls_knn_logitresid | 0.663120 | 0.718901 | 0.780533 | 0.716213 | 0.655283 | 0.595256 | 0.510872 | 0.664785 |
| joint_target_qs_residual_pls_knn_resid | 0.663729 | 0.714345 | 0.730969 | 0.734234 | 0.709059 | 0.597650 | 0.506207 | 0.653640 |
| joint_residual_behavior_neural_multiview_metric_knn_resid | 0.668966 | 0.713748 | 0.754790 | 0.753265 | 0.669582 | 0.628860 | 0.493481 | 0.669037 |
| joint_proto_neural_multiview_metric_knn_logitresid | 0.669450 | 0.767126 | 0.760823 | 0.695093 | 0.610993 | 0.666491 | 0.518270 | 0.667357 |
| joint_target_neural_multiview_residual_knn_logitresid | 0.673430 | 0.745301 | 0.775860 | 0.738777 | 0.664945 | 0.605122 | 0.507287 | 0.676717 |
| joint_neural_mixture_knn_resid | 0.676898 | 0.765219 | 0.725346 | 0.802527 | 0.659386 | 0.605675 | 0.502209 | 0.677923 |
| joint_target_qs_residual_pls_knn_logitresid | 0.677097 | 0.738044 | 0.822012 | 0.721918 | 0.664772 | 0.601426 | 0.517634 | 0.673872 |
| joint_proto_neural_residual_knn_logitresid | 0.678046 | 0.742279 | 0.837400 | 0.772436 | 0.612200 | 0.596603 | 0.529441 | 0.655960 |
| joint_neural_mixture_knn_logitresid | 0.683571 | 0.769154 | 0.802583 | 0.780306 | 0.630791 | 0.617946 | 0.514687 | 0.669531 |
| joint_family_residual_pls_knn_resid | 0.683646 | 0.812203 | 0.726488 | 0.800761 | 0.673672 | 0.647324 | 0.468203 | 0.656870 |
| joint_residual_pls_knn_resid | 0.686263 | 0.692737 | 0.760537 | 0.822561 | 0.672773 | 0.653578 | 0.507048 | 0.694604 |
| joint_neural_context_gate_logreg_logitresid | 0.688843 | 0.818264 | 0.752728 | 0.828662 | 0.680305 | 0.568373 | 0.529110 | 0.644459 |
| joint_panel_neural_residual_knn_resid | 0.691290 | 0.825191 | 0.820673 | 0.757396 | 0.648423 | 0.642583 | 0.543905 | 0.600862 |
| joint_family_residual_pls_knn_logitresid | 0.696428 | 0.785239 | 0.827887 | 0.820844 | 0.660238 | 0.624277 | 0.494610 | 0.661904 |
| joint_neural_context_gate_logreg_resid | 0.697161 | 0.821825 | 0.741001 | 0.855332 | 0.732208 | 0.585121 | 0.507016 | 0.637624 |
| joint_panel_neural_residual_knn_logitresid | 0.699269 | 0.844424 | 0.842219 | 0.727253 | 0.655353 | 0.636983 | 0.550264 | 0.638389 |
| joint_proto_neural_metric_knn_logitresid | 0.700142 | 0.783648 | 0.865763 | 0.826919 | 0.647199 | 0.616343 | 0.530043 | 0.631079 |
| joint_residual_behavior_neural_multiview_knn_logitresid | 0.700264 | 0.753559 | 0.808267 | 0.799528 | 0.658863 | 0.639724 | 0.531714 | 0.710196 |
| joint_pls_ridge | 0.708130 | 0.714437 | 0.699147 | 0.715594 | 0.712704 | 0.707376 | 0.707802 | 0.699852 |
| joint_neural_mixture_metric_knn_resid | 0.708340 | 0.837049 | 0.757451 | 0.834552 | 0.671405 | 0.662878 | 0.499349 | 0.695699 |
| joint_neural_gated_mixture_knn_resid | 0.709036 | 0.779092 | 0.843295 | 0.850426 | 0.685525 | 0.627983 | 0.484151 | 0.692778 |
| joint_residual_behavior_neural_multiview_metric_knn_logitresid | 0.709763 | 0.775775 | 0.830683 | 0.796249 | 0.672291 | 0.669952 | 0.523561 | 0.699827 |
| joint_pls_hgb | 0.710819 | 0.752950 | 0.759455 | 0.734034 | 0.687684 | 0.684481 | 0.644662 | 0.712464 |
| joint_residual_pls_knn_logitresid | 0.716089 | 0.794240 | 0.833714 | 0.856008 | 0.686009 | 0.636569 | 0.526378 | 0.679702 |
| joint_target_residual_pls_knn_resid | 0.719242 | 0.825812 | 0.942585 | 0.694502 | 0.765652 | 0.582084 | 0.592828 | 0.631231 |
| joint_residual_behavior_neural_knn_resid | 0.723429 | 0.753482 | 0.753646 | 0.824250 | 0.838567 | 0.636078 | 0.482314 | 0.775664 |
| joint_neural_gated_mixture_knn_logitresid | 0.725125 | 0.829168 | 0.855659 | 0.841425 | 0.673559 | 0.646399 | 0.551277 | 0.678388 |
| joint_neural_mixture_metric_knn_logitresid | 0.726421 | 0.821361 | 0.854524 | 0.813342 | 0.666317 | 0.672549 | 0.542514 | 0.714342 |
| joint_target_residual_pls_knn_logitresid | 0.734176 | 0.804494 | 0.980919 | 0.735268 | 0.730187 | 0.640478 | 0.563405 | 0.684477 |
| joint_residual_behavior_neural_knn_logitresid | 0.736412 | 0.810244 | 0.831162 | 0.860135 | 0.730981 | 0.620795 | 0.513449 | 0.788118 |
| joint_neural_context_attention_knn_logitresid | 0.756131 | 0.873590 | 0.882948 | 0.851447 | 0.662736 | 0.657774 | 0.568184 | 0.796235 |
| joint_neural_gated_mixture_metric_knn_resid | 0.756151 | 0.891362 | 0.933135 | 0.881039 | 0.672499 | 0.663609 | 0.498554 | 0.752857 |
| joint_residual_behavior_neural_metric_knn_logitresid | 0.761131 | 0.858098 | 0.887348 | 0.870860 | 0.744242 | 0.626930 | 0.538258 | 0.802182 |
| joint_neural_gated_mixture_metric_knn_logitresid | 0.764827 | 0.865554 | 0.911406 | 0.876548 | 0.719930 | 0.688844 | 0.561944 | 0.729564 |
| joint_residual_behavior_neural_metric_knn_resid | 0.765760 | 0.858778 | 0.838010 | 0.888436 | 0.864401 | 0.618810 | 0.504630 | 0.787251 |
| joint_target_neural_residual_knn_resid | 0.778020 | 0.860618 | 0.933812 | 0.841332 | 0.842149 | 0.601036 | 0.547147 | 0.820047 |
| joint_pls_logreg | 0.785425 | 0.785705 | 0.778618 | 0.781067 | 0.783386 | 0.785332 | 0.795593 | 0.788275 |
| joint_target_neural_residual_knn_logitresid | 0.794639 | 0.900125 | 0.991166 | 0.856047 | 0.773847 | 0.601639 | 0.620166 | 0.819480 |
| joint_neural_context_attention_knn_resid | 0.803767 | 0.913627 | 0.827911 | 0.970745 | 0.772914 | 0.684980 | 0.565581 | 0.890610 |
| joint_neural_context_metric_attention_knn_logitresid | 0.846215 | 0.987289 | 0.982479 | 0.983029 | 0.736723 | 0.698337 | 0.631823 | 0.903824 |
| joint_neural_context_metric_attention_knn_resid | 0.864374 | 1.014005 | 0.901038 | 1.084829 | 0.864628 | 0.702777 | 0.559528 | 0.923810 |

## Fold Latent Meta

| fold | train_rows | valid_rows | selected_features | pca_dim | pls_dim | latent_dim | residual_selected_features | residual_pls_dim | residual_latent_dim | q_residual_pls_dim | q_residual_latent_dim | s_residual_pls_dim | s_residual_latent_dim | neural_latent_dim | neural_best_loss | q_neural_latent_dim | s_neural_latent_dim | multiview_neural_latent_dim | multiview_neural_best_loss | q_multiview_neural_latent_dim | s_multiview_neural_latent_dim | panel_neural_latent_dim | panel_neural_best_loss | panel_multiview_neural_latent_dim | panel_multiview_neural_best_loss | residual_prototype_clusters | residual_prototype_inertia | residual_prototype_target_dim | proto_neural_latent_dim | proto_neural_best_loss | proto_multiview_neural_latent_dim | proto_multiview_neural_best_loss | residual_neighborhood_k | residual_neighborhood_target_dim | residual_neighborhood_mean_distance | residual_behavior_neural_latent_dim | residual_behavior_neural_best_loss | residual_behavior_multiview_neural_latent_dim | residual_behavior_multiview_neural_best_loss |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 355 | 95 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.324281 | 8 | 8 | 10 | 0.276049 | 8 | 8 | 10 | 0.387759 | 10 | 0.354489 | 9 | 6244.272461 | 66 | 10 | 0.422874 | 10 | 0.427327 | 31 | 90 | 0.823266 | 10 | 0.331520 | 10 | 0.426858 |
| 1 | 358 | 92 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.323537 | 8 | 8 | 10 | 0.273671 | 8 | 8 | 10 | 0.397992 | 10 | 0.353607 | 9 | 6461.803223 | 66 | 10 | 0.396042 | 10 | 0.363173 | 31 | 90 | 0.845396 | 10 | 0.365633 | 10 | 0.410047 |
| 2 | 359 | 91 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.310998 | 8 | 8 | 10 | 0.255546 | 8 | 8 | 10 | 0.371373 | 10 | 0.300194 | 9 | 6338.085449 | 66 | 10 | 0.400104 | 10 | 0.420023 | 31 | 90 | 0.830213 | 10 | 0.364787 | 10 | 0.411485 |
| 3 | 363 | 87 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.331582 | 8 | 8 | 10 | 0.265327 | 8 | 8 | 10 | 0.378488 | 10 | 0.348368 | 9 | 6509.859375 | 66 | 10 | 0.401233 | 10 | 0.398240 | 31 | 90 | 0.819662 | 10 | 0.373822 | 10 | 0.385175 |
| 4 | 365 | 85 | 420 | 32 | 7 | 39 | 420 | 7 | 7 | 3 | 3 | 4 | 4 | 10 | 0.295726 | 8 | 8 | 10 | 0.204891 | 8 | 8 | 10 | 0.384037 | 10 | 0.329556 | 9 | 6443.852539 | 66 | 10 | 0.411859 | 10 | 0.418560 | 31 | 90 | 0.812309 | 10 | 0.370002 | 10 | 0.395496 |
