# E164 Universe Broad Edge Screen

## Question

Does the existing submission universe contain a broad post-E95 successor, or are broad-looking edges still selector-unsafe and aligned with known bad axes?

## Summary

- raw submission paths scanned: `2052`.
- unique prediction tensors loaded: `1977`.
- skipped load/schema failures: `0`; duplicates: `75`.
- broad-edge rows versus E95: `198`.
- broad-edge rows with low E72-axis cosine: `193`.
- final conservative candidate-gate rows: `192`.
- known-public worse-than-E95 rows that still pass broad-edge gate: `2`.

## Known-Public Calibration Rows

| file | known_public_lb | known_delta_vs_e95 | broad_edge_gate | candidate_gate | vs_e95_expected_delta_focus_mean | vs_e95_cells_to_flip_expected_focus_mean | vs_e95_top1_over_abs_expected | cos_move_e95_vs_e72_from_e95 | q2s3_share_vs_e95 | family |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000000000 | False | False | 0.000000000 | -1 |  | 0.000000000 | 0.000000000 | hardtail |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000009036 | False | False | 0.000046398 | 5 | 0.250424793 | 0.201134072 | 1.000000000 | e101_q2s3 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000015311 | False | False | 0.000144543 | 4 | 0.321543667 | 0.671902535 | 0.222307092 | mixmin |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000116447 | True | False | -0.000869985 | 39 | 0.026932509 | 1.000000000 | 0.106376216 | q2s3_sparse |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.577439321 | 0.001147991 | False | False | 0.000342931 | 6 | 0.224057231 | -0.256339104 | 0.280635943 | jepa |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.001234977 | False | False | 0.001278183 | 18 | 0.082970306 | -0.297499917 | 0.284070495 | jepa |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.003509956 | False | False | -0.000943508 | 2 | 0.801699978 | -0.097510787 | 0.475117433 | jepa |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.003955489 | True | False | -0.002346961 | 8 | 0.146775247 | -0.122229388 | 0.208234824 | jepa |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.004935998 | False | False | 0.002496322 | 6 | 0.233379785 | -0.263511897 | 0.316665877 | jepa |

## Top Shortlist By Broad-Edge Score

| file | family | known_public_lb | candidate_gate | broad_edge_gate | low_e72_axis_gate | broad_edge_score | vs_e95_expected_delta_focus_mean | vs_e95_cells_to_flip_expected_focus_mean | vs_e95_top1_over_abs_expected | cos_move_e95_vs_e72_from_e95 | cos_move_e95_vs_e101_loss | q2s3_share_vs_e95 | vs_e95_moved_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | jepa |  | True | True | True | 0.093544612 | -0.025880912 | 54 | 0.029985445 | 0.108705614 | -0.099145675 | 0.250718585 | 1750 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | jepa |  | True | True | True | 0.087821392 | -0.024263334 | 57 | 0.032982617 | 0.121821012 | -0.115875488 | 0.280110076 | 1750 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | jepa |  | True | True | True | 0.084915571 | -0.024097611 | 50 | 0.032204465 | 0.115785974 | -0.102436580 | 0.160074050 | 1750 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | jepa |  | True | True | True | 0.084478479 | -0.023662682 | 56 | 0.034072223 | 0.132471134 | -0.116906302 | 0.265051787 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | jepa |  | True | True | True | 0.083367907 | -0.023754522 | 50 | 0.032081573 | 0.120318878 | -0.093198642 | 0.158683217 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | jepa |  | True | True | True | 0.082643719 | -0.023586482 | 50 | 0.032056331 | 0.122141353 | -0.089040322 | 0.158097875 | 1750 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | jepa |  | True | True | True | 0.080947729 | -0.023278393 | 49 | 0.032051989 | 0.124992747 | -0.081870240 | 0.157299103 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | jepa |  | True | True | True | 0.079571091 | -0.022935265 | 49 | 0.032096490 | 0.127586447 | -0.074435582 | 0.156712146 | 1750 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale1p0.csv | jepa |  | True | True | True | 0.078642010 | -0.022169690 | 53 | 0.036097403 | 0.124520362 | -0.119294266 | 0.181350807 | 1750 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | jepa |  | True | True | True | 0.077897080 | -0.020736972 | 58 | 0.028189046 | 0.085480747 | -0.102804945 | 0.253296540 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw1p0.csv | jepa |  | True | True | True | 0.077040571 | -0.021824319 | 53 | 0.036028618 | 0.130013163 | -0.109278830 | 0.179938305 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw1p0.csv | jepa |  | True | True | True | 0.076296450 | -0.021655465 | 53 | 0.036033106 | 0.132206071 | -0.104699070 | 0.179403344 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw1p0.csv | jepa |  | True | True | True | 0.074630552 | -0.021346240 | 52 | 0.036087684 | 0.135604700 | -0.096715239 | 0.178915447 | 1750 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale1p0.csv | jepa |  | True | True | True | 0.074595025 | -0.021341306 | 52 | 0.037778391 | 0.135882935 | -0.119458886 | 0.172769965 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw1p0.csv | jepa |  | True | True | True | 0.073231971 | -0.021002252 | 52 | 0.036203693 | 0.138643021 | -0.088339913 | 0.178469531 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw1p0.csv | jepa |  | True | True | True | 0.073006013 | -0.020997730 | 52 | 0.037731317 | 0.141921247 | -0.109184412 | 0.170966109 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw1p0.csv | jepa |  | True | True | True | 0.072269886 | -0.020829717 | 52 | 0.037748263 | 0.144322499 | -0.104468370 | 0.170293092 | 1750 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale0p75.csv | jepa |  | True | True | True | 0.071978976 | -0.019252485 | 59 | 0.031306019 | 0.095129606 | -0.118859149 | 0.282653076 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw1p0.csv | jepa |  | True | True | True | 0.070972540 | -0.020521990 | 52 | 0.037828122 | 0.148025563 | -0.096225529 | 0.169462533 | 1750 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale0p75.csv | jepa |  | True | True | True | 0.070225027 | -0.019206324 | 53 | 0.030435572 | 0.090974592 | -0.106028519 | 0.170616354 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw1p0.csv | jepa |  | True | True | True | 0.069255778 | -0.020179623 | 51 | 0.037975490 | 0.151306203 | -0.087555402 | 0.168965323 | 1750 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale0p75.csv | jepa |  | True | True | True | 0.069111322 | -0.018720022 | 58 | 0.032435733 | 0.104473008 | -0.120001675 | 0.266822136 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw0p75.csv | jepa |  | True | True | True | 0.068589385 | -0.018860016 | 53 | 0.030253806 | 0.096850540 | -0.094523818 | 0.169019048 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw0p75.csv | jepa |  | True | True | True | 0.067826445 | -0.018690796 | 53 | 0.030207429 | 0.099236222 | -0.089229861 | 0.168400379 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv | jepa |  | True | True | True | 0.066164335 | -0.018381005 | 52 | 0.030173737 | 0.102980267 | -0.079969947 | 0.167312853 | 1750 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p75.csv | jepa |  | True | True | True | 0.064414331 | -0.018036507 | 51 | 0.030196885 | 0.106378542 | -0.070236633 | 0.166540640 | 1750 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale0p75.csv | jepa |  | True | True | True | 0.064284963 | -0.017499242 | 55 | 0.034442558 | 0.095755505 | -0.122128313 | 0.191595079 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw0p75.csv | jepa |  | True | True | True | 0.062608406 | -0.017151692 | 55 | 0.034326086 | 0.102752763 | -0.109906791 | 0.190561003 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw0p75.csv | jepa |  | True | True | True | 0.061830344 | -0.016982069 | 55 | 0.034316436 | 0.105586611 | -0.104161254 | 0.189966491 | 1750 |
| submission_block_canvas_multifeature_k3_c0p02_noq2_scale0p75.csv | jepa |  | True | True | True | 0.060932811 | -0.016812453 | 54 | 0.036115946 | 0.105694904 | -0.122396384 | 0.183685258 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw0p75.csv | jepa |  | True | True | True | 0.060188384 | -0.016671781 | 54 | 0.034356665 | 0.110004576 | -0.093961566 | 0.189007654 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p35_mw0p75.csv | jepa |  | True | True | True | 0.059265239 | -0.016466262 | 54 | 0.036026964 | 0.113398015 | -0.109902630 | 0.181985968 | 1750 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw1p0_mw0p75.csv | jepa |  | True | True | True | 0.058734634 | -0.016327002 | 54 | 0.034471087 | 0.113954977 | -0.083075513 | 0.188343123 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p5_mw0p75.csv | jepa |  | True | True | True | 0.058493682 | -0.016297277 | 54 | 0.036033201 | 0.116507227 | -0.103997174 | 0.181287950 | 1750 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p5.csv | jepa |  | True | True | True | 0.057412446 | -0.014667159 | 58 | 0.026798666 | 0.041688567 | -0.107513954 | 0.256471454 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw0p75_mw0p75.csv | jepa |  | True | True | True | 0.057137297 | -0.015988126 | 54 | 0.036105905 | 0.121329715 | -0.093474364 | 0.180180729 | 1750 |
| submission_jepa_multifeature_rawstack_k3_c0p02_noq2_rw1p0_mw0p75.csv | jepa |  | True | True | True | 0.055442515 | -0.015644580 | 53 | 0.036261023 | 0.125597925 | -0.082201562 | 0.179383874 | 1750 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale0p5.csv | jepa |  | True | True | True | 0.052864858 | -0.013503377 | 59 | 0.030005019 | 0.045826653 | -0.121585334 | 0.284382844 | 1750 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale0p5.csv | jepa |  | True | True | True | 0.051385322 | -0.013518664 | 52 | 0.029075379 | 0.044520895 | -0.110330807 | 0.187932149 | 1750 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale0p5.csv | jepa |  | True | True | True | 0.050723949 | -0.013095477 | 58 | 0.031167636 | 0.052703856 | -0.122694678 | 0.268861286 | 1750 |

## Family Summary

| family | rows | broad_edge_gate | low_e72_axis_gate | candidate_gate | best_broad_edge_score | best_expected_delta_vs_e95 | median_e72_axis_cos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| jepa | 1943 | 190 | 1943 | 189 | 0.093544612 | -0.025880912 | -0.139673268 |
| other | 18 | 6 | 13 | 3 | 0.167995610 | -0.051243097 | -0.173607518 |
| q2s3_sparse | 5 | 2 | 2 | 0 | 0.001702772 | -0.000913562 | 0.207351434 |
| repaired_branch | 5 | 0 | 5 | 0 | 0.000043052 | -0.000031056 | -0.027413915 |
| block | 1 | 0 | 1 | 0 | 0.000000000 | 0.000341238 | -0.256006586 |
| e101_q2s3 | 3 | 0 | 0 | 0 | 0.000000000 | 0.000046398 | 0.201134072 |
| hardtail | 1 | 0 | 1 | 0 | 0.000000000 | 0.000000000 | 0.000000000 |
| mixmin | 1 | 0 | 0 | 0 | 0.000000000 | 0.000144543 | 0.671902535 |

## Decision

Broadness by itself is not enough. If the conservative gate is empty or dominated by known-bad families, then the existing universe has no pre-feedback broad successor to E95. If it is non-empty, those rows are still only hypothesis candidates until checked against the known-public calibration rows and E72/E101 axes.
