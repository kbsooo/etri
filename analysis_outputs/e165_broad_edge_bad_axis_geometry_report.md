# E165 Broad Edge Bad-Axis Geometry

## Question

Do E164 broad candidates represent a new broad world law, or do they fall into known public-bad/collapse geometry?

## Summary

- bad axes used: `a2c8,raw05,stage2,ordinal,final9,e72,q2_bad,lejepa_bad,resid_bad`.
- E164 rows: `1977`; selected/scored rows: `205` / `205`.
- E164 candidate-gate rows scored: `192`.
- geometry-health survivor rows: `90`.
- known public-bad broad rows: `2`.

## Known-Public Calibration

| file | known_public_lb | known_delta_vs_e95 | e164_broad_edge_gate | e164_candidate_gate | geometry_health_gate | e164_expected_delta_vs_e95 | bad_span_energy | bad_span_residual | max_bad_axis | max_bad_cos | entropy_delta_vs_e95 | cos_e154_axis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000000000 | False | False | False | 0.000000000 | 0.000000000 | 1.000000000 | a2c8 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000009036 | False | False | False | 0.000046398 | 0.311462262 | 0.950258523 | e72 | 0.201134072 | -0.000024376 | -0.005523655 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000015311 | False | False | False | 0.000144543 | 0.752971984 | 0.658052575 | e72 | 0.671902535 | -0.000037731 | -0.023782332 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000116447 | True | False | False | -0.000869985 | 1.000000000 | 0.000000000 | e72 | 1.000000000 | 0.000561877 | -0.031628728 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439321 | 0.001147991 | False | False | False | 0.000342931 | 1.000000000 | 0.000000000 | a2c8 | 1.000000000 | 0.000353540 | 0.096863658 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.001234977 | False | False | False | 0.001278183 | 1.000000000 | 0.000000000 | raw05 | 1.000000000 | -0.000198715 | 0.091947371 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.003509956 | False | False | False | -0.000943508 | 1.000000000 | 0.000000000 | q2_bad | 1.000000000 | 0.000519746 | 0.109868955 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.003955489 | True | False | False | -0.002346961 | 1.000000000 | 0.000000000 | lejepa_bad | 1.000000000 | 0.006658353 | 0.148204217 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.004935998 | False | False | False | 0.002496322 | 1.000000000 | 0.000000000 | resid_bad | 1.000000000 | 0.000680536 | 0.205542728 |

## Geometry-Health Survivors

| file | family | e164_broad_edge_score | e164_expected_delta_vs_e95 | bad_span_energy | bad_span_residual | max_bad_axis | max_bad_cos | entropy_delta_vs_e95 | cos_e154_axis | cos_e101_axis | mean_abs_logit_move_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | jepa | 0.093544612 | -0.025880912 | 0.450742441 | 0.892654049 | q2_bad | 0.268538582 | 0.020377694 | 0.061661852 | -0.099145675 | 0.224398639 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | jepa | 0.087821392 | -0.024263334 | 0.512399527 | 0.858747183 | q2_bad | 0.314002637 | 0.017979225 | 0.090018078 | -0.115875488 | 0.207541978 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | jepa | 0.084915571 | -0.024097611 | 0.448447736 | 0.893809056 | stage2 | 0.269154408 | 0.019537667 | 0.065056807 | -0.102436580 | 0.200181611 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | jepa | 0.084478479 | -0.023662682 | 0.491502217 | 0.870876323 | stage2 | 0.296562260 | 0.017127352 | 0.111827323 | -0.116906302 | 0.196919765 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | jepa | 0.083367907 | -0.023754522 | 0.421741418 | 0.906716150 | stage2 | 0.223787914 | 0.019379054 | 0.052074049 | -0.093198642 | 0.197266874 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | jepa | 0.082643719 | -0.023586482 | 0.412041474 | 0.911165091 | stage2 | 0.203673863 | 0.019296666 | 0.046333619 | -0.089040322 | 0.196224475 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | jepa | 0.080947729 | -0.023278393 | 0.398844089 | 0.917018753 | a2c8 | 0.190085511 | 0.019140065 | 0.036573850 | -0.081870240 | 0.194922405 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | jepa | 0.079571091 | -0.022935265 | 0.389982782 | 0.920822149 | a2c8 | 0.188714403 | 0.018959300 | 0.026626395 | -0.074435582 | 0.194245741 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale1p0.csv | jepa | 0.078642010 | -0.022169690 | 0.512203911 | 0.858863874 | stage2 | 0.316953984 | 0.016409196 | 0.096309319 | -0.119294266 | 0.182504766 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | jepa | 0.077897080 | -0.020736972 | 0.494206089 | 0.869344777 | stage2 | 0.335373663 | 0.016058780 | 0.077651140 | -0.102804945 | 0.173136196 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw1p0.csv | jepa | 0.077040571 | -0.021824319 | 0.485297625 | 0.874349024 | stage2 | 0.266755659 | 0.016253158 | 0.082241069 | -0.109278830 | 0.179682575 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw1p0.csv | jepa | 0.076296450 | -0.021655465 | 0.475568053 | 0.879678934 | stage2 | 0.244273001 | 0.016172190 | 0.075927671 | -0.104699070 | 0.178723843 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw1p0.csv | jepa | 0.074630552 | -0.021346240 | 0.462459713 | 0.886640295 | a2c8 | 0.241376067 | 0.016018385 | 0.065080766 | -0.096715239 | 0.177577005 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale1p0.csv | jepa | 0.074595025 | -0.021341306 | 0.498654582 | 0.866800789 | stage2 | 0.314278153 | 0.015344596 | 0.119433559 | -0.119458886 | 0.174952339 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw1p0.csv | jepa | 0.073231971 | -0.021002252 | 0.453907963 | 0.891048574 | a2c8 | 0.240116118 | 0.015840951 | 0.053899663 | -0.088339913 | 0.176863328 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw1p0.csv | jepa | 0.073006013 | -0.020997730 | 0.467812665 | 0.883827647 | stage2 | 0.262448743 | 0.015188049 | 0.105384190 | -0.109184412 | 0.171930788 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw1p0.csv | jepa | 0.072269886 | -0.020829717 | 0.456488027 | 0.889729555 | stage2 | 0.239176914 | 0.015106992 | 0.099014370 | -0.104468370 | 0.170949939 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale0p75.csv | jepa | 0.071978976 | -0.019252485 | 0.558330847 | 0.829618385 | stage2 | 0.389359995 | 0.014150901 | 0.106439944 | -0.118859149 | 0.161026759 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw1p0.csv | jepa | 0.070972540 | -0.020521990 | 0.441028217 | 0.897493238 | a2c8 | 0.226050155 | 0.014953215 | 0.087986254 | -0.096225529 | 0.169740534 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale0p75.csv | jepa | 0.070225027 | -0.019206324 | 0.496902709 | 0.867806256 | stage2 | 0.354440673 | 0.015264858 | 0.081675757 | -0.106028519 | 0.155876472 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw1p0.csv | jepa | 0.069255778 | -0.020179623 | 0.430720974 | 0.902485148 | a2c8 | 0.224750427 | 0.014776040 | 0.076517390 | -0.087555402 | 0.168995827 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale0p75.csv | jepa | 0.069111322 | -0.018720022 | 0.541741897 | 0.840544893 | stage2 | 0.387780595 | 0.013464528 | 0.128120137 | -0.120001675 | 0.153295599 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw0p75.csv | jepa | 0.068589385 | -0.018860016 | 0.459432389 | 0.888212745 | stage2 | 0.298444531 | 0.015110962 | 0.065412228 | -0.094523818 | 0.152256498 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p75.csv | jepa | 0.067826445 | -0.018690796 | 0.445487680 | 0.895288069 | stage2 | 0.273031907 | 0.015030944 | 0.058078008 | -0.089229861 | 0.150932481 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv | jepa | 0.066164335 | -0.018381005 | 0.426381019 | 0.904543657 | a2c8 | 0.252643922 | 0.014878758 | 0.045450942 | -0.079969947 | 0.149233091 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p75.csv | jepa | 0.064414331 | -0.018036507 | 0.413807974 | 0.910364191 | a2c8 | 0.251422996 | 0.014702986 | 0.032430810 | -0.070236633 | 0.148444602 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale0p75.csv | jepa | 0.064284963 | -0.017499242 | 0.563326573 | 0.826234332 | stage2 | 0.409281398 | 0.012824366 | 0.113398960 | -0.122128313 | 0.142888851 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw0p75.csv | jepa | 0.062608406 | -0.017151692 | 0.526338380 | 0.850275197 | stage2 | 0.348692263 | 0.012672854 | 0.096205811 | -0.109906791 | 0.139353760 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw0p75.csv | jepa | 0.061830344 | -0.016982069 | 0.512572414 | 0.858644001 | stage2 | 0.320747890 | 0.012594104 | 0.088283682 | -0.104161254 | 0.138213212 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale0p75.csv | jepa | 0.060932811 | -0.016812453 | 0.553536411 | 0.832824976 | stage2 | 0.409922815 | 0.011995199 | 0.136215289 | -0.122396384 | 0.137683340 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw0p75.csv | jepa | 0.060188384 | -0.016671781 | 0.493834155 | 0.869556109 | a2c8 | 0.310449116 | 0.012444361 | 0.074436065 | -0.093961566 | 0.136670584 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw0p75.csv | jepa | 0.059265239 | -0.016466262 | 0.511781849 | 0.859115440 | stage2 | 0.347688388 | 0.011843293 | 0.119265949 | -0.109902630 | 0.133686058 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw0p75.csv | jepa | 0.058734634 | -0.016327002 | 0.481803824 | 0.876279108 | a2c8 | 0.309623670 | 0.012271447 | 0.059926258 | -0.083075513 | 0.135786156 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw0p75.csv | jepa | 0.058493682 | -0.016297277 | 0.495967412 | 0.868341135 | stage2 | 0.318858331 | 0.011764468 | 0.111342034 | -0.103997174 | 0.132351839 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p5.csv | jepa | 0.057412446 | -0.014667159 | 0.585559036 | 0.810629765 | stage2 | 0.477820793 | 0.011229443 | 0.105228164 | -0.107513954 | 0.124450507 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw0p75.csv | jepa | 0.057137297 | -0.015988126 | 0.474120219 | 0.880460117 | a2c8 | 0.298368271 | 0.011614735 | 0.097340764 | -0.093474364 | 0.130669050 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw0p75.csv | jepa | 0.055442515 | -0.015644580 | 0.459770201 | 0.888037929 | a2c8 | 0.297581424 | 0.011442003 | 0.082489451 | -0.082201562 | 0.129754381 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw0p5.csv | jepa | 0.049947656 | -0.013170133 | 0.543551094 | 0.839376083 | stage2 | 0.431770174 | 0.010444894 | 0.089033769 | -0.095425911 | 0.109220363 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p5.csv | jepa | 0.049158401 | -0.013000183 | 0.523212290 | 0.852202382 | stage2 | 0.398689074 | 0.010367913 | 0.079178404 | -0.088250229 | 0.107602176 |
| submission_bigshot_hybrid_05_minimax_r05_multifeature_raw_logit_w0p4.csv | jepa | 0.048322133 | -0.013499441 | 0.596819751 | 0.802375339 | final9 | 0.325051212 | 0.009892402 | 0.148772810 | -0.120583617 | 0.098119424 |
| submission_bigshot_hybrid_06_u80_multifeature_raw_logit_w0p4.csv | jepa | 0.048316173 | -0.013496168 | 0.596764439 | 0.802416478 | final9 | 0.324828371 | 0.009890219 | 0.148759874 | -0.120586721 | 0.098102760 |
| submission_bigshot_hybrid_04_minimax_r01_multifeature_raw_logit_w0p4.csv | jepa | 0.048304274 | -0.013491535 | 0.596786542 | 0.802400040 | final9 | 0.324867785 | 0.009886314 | 0.148763822 | -0.120625377 | 0.098093315 |
| submission_bigshot_hybrid_07_u65_maskrank_multifeature_raw_logit_w0p4.csv | jepa | 0.048116377 | -0.013440018 | 0.589775855 | 0.807566988 | final9 | 0.317715447 | 0.009875395 | 0.146494162 | -0.120350891 | 0.095784473 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p5.csv | jepa | 0.047756890 | -0.012689472 | 0.494654412 | 0.869089761 | a2c8 | 0.367923407 | 0.010221302 | 0.061683875 | -0.075324090 | 0.105527907 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p5.csv | jepa | 0.046037522 | -0.012344423 | 0.476065986 | 0.879409561 | a2c8 | 0.368167466 | 0.010051743 | 0.043126420 | -0.061369335 | 0.104416414 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw0p5.csv | jepa | 0.044625892 | -0.011695773 | 0.593690866 | 0.804693206 | stage2 | 0.454882154 | 0.008694237 | 0.109298912 | -0.101301018 | 0.099338510 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw0p5.csv | jepa | 0.043206879 | -0.011384932 | 0.566648140 | 0.823959881 | a2c8 | 0.433886709 | 0.008549375 | 0.090638904 | -0.087347685 | 0.097434427 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw0p5.csv | jepa | 0.042194847 | -0.011197457 | 0.583111228 | 0.812392329 | stage2 | 0.458166844 | 0.008124230 | 0.131688539 | -0.101113834 | 0.095722517 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw0p5.csv | jepa | 0.041312847 | -0.011039902 | 0.549339428 | 0.835599302 | a2c8 | 0.435401963 | 0.008381845 | 0.070341786 | -0.071971435 | 0.096415310 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw0p5.csv | jepa | 0.040788763 | -0.010887383 | 0.552366587 | 0.833601316 | a2c8 | 0.427551007 | 0.007979362 | 0.113035481 | -0.086748147 | 0.093545571 |

## Top Scored Rows

| file | family | geometry_health_gate | e164_broad_edge_score | e164_expected_delta_vs_e95 | bad_span_energy | bad_span_residual | max_bad_axis | max_bad_cos | entropy_delta_vs_e95 | cos_e154_axis | cos_e101_axis | mean_abs_logit_move_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | jepa | True | 0.093544612 | -0.025880912 | 0.450742441 | 0.892654049 | q2_bad | 0.268538582 | 0.020377694 | 0.061661852 | -0.099145675 | 0.224398639 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | jepa | True | 0.087821392 | -0.024263334 | 0.512399527 | 0.858747183 | q2_bad | 0.314002637 | 0.017979225 | 0.090018078 | -0.115875488 | 0.207541978 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | jepa | True | 0.084915571 | -0.024097611 | 0.448447736 | 0.893809056 | stage2 | 0.269154408 | 0.019537667 | 0.065056807 | -0.102436580 | 0.200181611 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | jepa | True | 0.084478479 | -0.023662682 | 0.491502217 | 0.870876323 | stage2 | 0.296562260 | 0.017127352 | 0.111827323 | -0.116906302 | 0.196919765 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | jepa | True | 0.083367907 | -0.023754522 | 0.421741418 | 0.906716150 | stage2 | 0.223787914 | 0.019379054 | 0.052074049 | -0.093198642 | 0.197266874 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | jepa | True | 0.082643719 | -0.023586482 | 0.412041474 | 0.911165091 | stage2 | 0.203673863 | 0.019296666 | 0.046333619 | -0.089040322 | 0.196224475 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | jepa | True | 0.080947729 | -0.023278393 | 0.398844089 | 0.917018753 | a2c8 | 0.190085511 | 0.019140065 | 0.036573850 | -0.081870240 | 0.194922405 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | jepa | True | 0.079571091 | -0.022935265 | 0.389982782 | 0.920822149 | a2c8 | 0.188714403 | 0.018959300 | 0.026626395 | -0.074435582 | 0.194245741 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale1p0.csv | jepa | True | 0.078642010 | -0.022169690 | 0.512203911 | 0.858863874 | stage2 | 0.316953984 | 0.016409196 | 0.096309319 | -0.119294266 | 0.182504766 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | jepa | True | 0.077897080 | -0.020736972 | 0.494206089 | 0.869344777 | stage2 | 0.335373663 | 0.016058780 | 0.077651140 | -0.102804945 | 0.173136196 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw1p0.csv | jepa | True | 0.077040571 | -0.021824319 | 0.485297625 | 0.874349024 | stage2 | 0.266755659 | 0.016253158 | 0.082241069 | -0.109278830 | 0.179682575 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw1p0.csv | jepa | True | 0.076296450 | -0.021655465 | 0.475568053 | 0.879678934 | stage2 | 0.244273001 | 0.016172190 | 0.075927671 | -0.104699070 | 0.178723843 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw1p0.csv | jepa | True | 0.074630552 | -0.021346240 | 0.462459713 | 0.886640295 | a2c8 | 0.241376067 | 0.016018385 | 0.065080766 | -0.096715239 | 0.177577005 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale1p0.csv | jepa | True | 0.074595025 | -0.021341306 | 0.498654582 | 0.866800789 | stage2 | 0.314278153 | 0.015344596 | 0.119433559 | -0.119458886 | 0.174952339 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw1p0.csv | jepa | True | 0.073231971 | -0.021002252 | 0.453907963 | 0.891048574 | a2c8 | 0.240116118 | 0.015840951 | 0.053899663 | -0.088339913 | 0.176863328 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw1p0.csv | jepa | True | 0.073006013 | -0.020997730 | 0.467812665 | 0.883827647 | stage2 | 0.262448743 | 0.015188049 | 0.105384190 | -0.109184412 | 0.171930788 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw1p0.csv | jepa | True | 0.072269886 | -0.020829717 | 0.456488027 | 0.889729555 | stage2 | 0.239176914 | 0.015106992 | 0.099014370 | -0.104468370 | 0.170949939 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale0p75.csv | jepa | True | 0.071978976 | -0.019252485 | 0.558330847 | 0.829618385 | stage2 | 0.389359995 | 0.014150901 | 0.106439944 | -0.118859149 | 0.161026759 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw1p0.csv | jepa | True | 0.070972540 | -0.020521990 | 0.441028217 | 0.897493238 | a2c8 | 0.226050155 | 0.014953215 | 0.087986254 | -0.096225529 | 0.169740534 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale0p75.csv | jepa | True | 0.070225027 | -0.019206324 | 0.496902709 | 0.867806256 | stage2 | 0.354440673 | 0.015264858 | 0.081675757 | -0.106028519 | 0.155876472 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw1p0.csv | jepa | True | 0.069255778 | -0.020179623 | 0.430720974 | 0.902485148 | a2c8 | 0.224750427 | 0.014776040 | 0.076517390 | -0.087555402 | 0.168995827 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale0p75.csv | jepa | True | 0.069111322 | -0.018720022 | 0.541741897 | 0.840544893 | stage2 | 0.387780595 | 0.013464528 | 0.128120137 | -0.120001675 | 0.153295599 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw0p75.csv | jepa | True | 0.068589385 | -0.018860016 | 0.459432389 | 0.888212745 | stage2 | 0.298444531 | 0.015110962 | 0.065412228 | -0.094523818 | 0.152256498 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p75.csv | jepa | True | 0.067826445 | -0.018690796 | 0.445487680 | 0.895288069 | stage2 | 0.273031907 | 0.015030944 | 0.058078008 | -0.089229861 | 0.150932481 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv | jepa | True | 0.066164335 | -0.018381005 | 0.426381019 | 0.904543657 | a2c8 | 0.252643922 | 0.014878758 | 0.045450942 | -0.079969947 | 0.149233091 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p75.csv | jepa | True | 0.064414331 | -0.018036507 | 0.413807974 | 0.910364191 | a2c8 | 0.251422996 | 0.014702986 | 0.032430810 | -0.070236633 | 0.148444602 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale0p75.csv | jepa | True | 0.064284963 | -0.017499242 | 0.563326573 | 0.826234332 | stage2 | 0.409281398 | 0.012824366 | 0.113398960 | -0.122128313 | 0.142888851 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw0p75.csv | jepa | True | 0.062608406 | -0.017151692 | 0.526338380 | 0.850275197 | stage2 | 0.348692263 | 0.012672854 | 0.096205811 | -0.109906791 | 0.139353760 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw0p75.csv | jepa | True | 0.061830344 | -0.016982069 | 0.512572414 | 0.858644001 | stage2 | 0.320747890 | 0.012594104 | 0.088283682 | -0.104161254 | 0.138213212 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale0p75.csv | jepa | True | 0.060932811 | -0.016812453 | 0.553536411 | 0.832824976 | stage2 | 0.409922815 | 0.011995199 | 0.136215289 | -0.122396384 | 0.137683340 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw0p75.csv | jepa | True | 0.060188384 | -0.016671781 | 0.493834155 | 0.869556109 | a2c8 | 0.310449116 | 0.012444361 | 0.074436065 | -0.093961566 | 0.136670584 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw0p75.csv | jepa | True | 0.059265239 | -0.016466262 | 0.511781849 | 0.859115440 | stage2 | 0.347688388 | 0.011843293 | 0.119265949 | -0.109902630 | 0.133686058 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw0p75.csv | jepa | True | 0.058734634 | -0.016327002 | 0.481803824 | 0.876279108 | a2c8 | 0.309623670 | 0.012271447 | 0.059926258 | -0.083075513 | 0.135786156 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw0p75.csv | jepa | True | 0.058493682 | -0.016297277 | 0.495967412 | 0.868341135 | stage2 | 0.318858331 | 0.011764468 | 0.111342034 | -0.103997174 | 0.132351839 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p5.csv | jepa | True | 0.057412446 | -0.014667159 | 0.585559036 | 0.810629765 | stage2 | 0.477820793 | 0.011229443 | 0.105228164 | -0.107513954 | 0.124450507 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw0p75.csv | jepa | True | 0.057137297 | -0.015988126 | 0.474120219 | 0.880460117 | a2c8 | 0.298368271 | 0.011614735 | 0.097340764 | -0.093474364 | 0.130669050 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw0p75.csv | jepa | True | 0.055442515 | -0.015644580 | 0.459770201 | 0.888037929 | a2c8 | 0.297581424 | 0.011442003 | 0.082489451 | -0.082201562 | 0.129754381 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw0p5.csv | jepa | True | 0.049947656 | -0.013170133 | 0.543551094 | 0.839376083 | stage2 | 0.431770174 | 0.010444894 | 0.089033769 | -0.095425911 | 0.109220363 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p5.csv | jepa | True | 0.049158401 | -0.013000183 | 0.523212290 | 0.852202382 | stage2 | 0.398689074 | 0.010367913 | 0.079178404 | -0.088250229 | 0.107602176 |
| submission_bigshot_hybrid_05_minimax_r05_multifeature_raw_logit_w0p4.csv | jepa | True | 0.048322133 | -0.013499441 | 0.596819751 | 0.802375339 | final9 | 0.325051212 | 0.009892402 | 0.148772810 | -0.120583617 | 0.098119424 |
| submission_bigshot_hybrid_06_u80_multifeature_raw_logit_w0p4.csv | jepa | True | 0.048316173 | -0.013496168 | 0.596764439 | 0.802416478 | final9 | 0.324828371 | 0.009890219 | 0.148759874 | -0.120586721 | 0.098102760 |
| submission_bigshot_hybrid_04_minimax_r01_multifeature_raw_logit_w0p4.csv | jepa | True | 0.048304274 | -0.013491535 | 0.596786542 | 0.802400040 | final9 | 0.324867785 | 0.009886314 | 0.148763822 | -0.120625377 | 0.098093315 |
| submission_bigshot_hybrid_07_u65_maskrank_multifeature_raw_logit_w0p4.csv | jepa | True | 0.048116377 | -0.013440018 | 0.589775855 | 0.807566988 | final9 | 0.317715447 | 0.009875395 | 0.146494162 | -0.120350891 | 0.095784473 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p5.csv | jepa | True | 0.047756890 | -0.012689472 | 0.494654412 | 0.869089761 | a2c8 | 0.367923407 | 0.010221302 | 0.061683875 | -0.075324090 | 0.105527907 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p5.csv | jepa | True | 0.046037522 | -0.012344423 | 0.476065986 | 0.879409561 | a2c8 | 0.368167466 | 0.010051743 | 0.043126420 | -0.061369335 | 0.104416414 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw0p5.csv | jepa | True | 0.044625892 | -0.011695773 | 0.593690866 | 0.804693206 | stage2 | 0.454882154 | 0.008694237 | 0.109298912 | -0.101301018 | 0.099338510 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw0p5.csv | jepa | True | 0.043206879 | -0.011384932 | 0.566648140 | 0.823959881 | a2c8 | 0.433886709 | 0.008549375 | 0.090638904 | -0.087347685 | 0.097434427 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw0p5.csv | jepa | True | 0.042194847 | -0.011197457 | 0.583111228 | 0.812392329 | stage2 | 0.458166844 | 0.008124230 | 0.131688539 | -0.101113834 | 0.095722517 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw0p5.csv | jepa | True | 0.041312847 | -0.011039902 | 0.549339428 | 0.835599302 | a2c8 | 0.435401963 | 0.008381845 | 0.070341786 | -0.071971435 | 0.096415310 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw0p5.csv | jepa | True | 0.040788763 | -0.010887383 | 0.552366587 | 0.833601316 | a2c8 | 0.427551007 | 0.007979362 | 0.113035481 | -0.086748147 | 0.093545571 |

## Decision

A broad edge is only actionable if it is also geometrically healthy against known public-bad axes. Rows that are broad but high-energy in the bad span are evidence for collapse/shortcut, not submissions.
