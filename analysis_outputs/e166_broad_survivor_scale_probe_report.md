# E166 Broad Survivor Scale Probe

## Question

Can an E95-to-E165-survivor tiny logit step keep a broad hard-label edge while avoiding known public-bad geometry?

## Summary

- source directions: `21`.
- scaled rows scored: `198`.
- negative-control scaled rows: `22`.
- scaled sensor-gate rows: `112`.
- material-gate rows with scale <= 0.03: `51`.
- bad axes: `a2c8,raw05,stage2,ordinal,final9,e72,q2_bad,lejepa_bad,resid_bad`.
- materialized file: `submission_e166_broadsurv_s0p01_d8bfa94b.csv`.

## Selected Materialized Row

| materialized_file | source_file | scale | sensor_score | scaled_expected_delta_focus_mean | scaled_cells_to_flip_expected | scaled_top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | entropy_delta_vs_e95 | mean_abs_logit_move_vs_e95 | max_abs_logit_move_vs_e95 | q2s3_share_vs_e95 | cos_e154_axis | cos_e101_axis | cos_mixmin_axis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | 0.010000000 | 0.016501606 | -0.000332077 | 74 | 0.023369627 | 0.450742441 | q2_bad | 0.268538582 | 0.000238386 | 0.002243986 | 0.013580886 | 0.250718585 | 0.061661852 | -0.099145675 | -0.137683489 |

## Top Sensor Rows

| source_file | scale | scaled_sensor_gate | material_gate | sensor_score | scaled_expected_delta_focus_mean | scaled_cells_to_flip_expected | scaled_top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_move_vs_e95 | max_abs_logit_move_vs_e95 | entropy_delta_vs_e95 | q2s3_share_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | 0.020000000 | True | True | 0.025630110 | -0.000662760 | 74 | 0.023418742 | 0.450742441 | q2_bad | 0.268538582 | 0.004487973 | 0.027161773 | 0.000476206 | 0.250718585 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | 0.030000000 | True | True | 0.025522352 | -0.000992048 | 74 | 0.023468129 | 0.450742441 | q2_bad | 0.268538582 | 0.006731959 | 0.040742659 | 0.000713458 | 0.250718585 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | 0.015000000 | True | True | 0.024700541 | -0.000497593 | 74 | 0.023394151 | 0.450742441 | q2_bad | 0.268538582 | 0.003365980 | 0.020371330 | 0.000357367 | 0.250718585 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | 0.020000000 | True | True | 0.023336120 | -0.000584943 | 66 | 0.025510814 | 0.398844089 | a2c8 | 0.190085511 | 0.003898448 | 0.026114157 | 0.000432815 | 0.157299103 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | 0.030000000 | True | True | 0.023245127 | -0.000875702 | 66 | 0.025560696 | 0.398844089 | a2c8 | 0.190085511 | 0.005847672 | 0.039171236 | 0.000648633 | 0.157299103 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | 0.020000000 | True | True | 0.023116548 | -0.000577458 | 65 | 0.025495946 | 0.389982782 | a2c8 | 0.188714403 | 0.003884915 | 0.025764952 | 0.000429403 | 0.156712146 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | 0.030000000 | True | True | 0.023025631 | -0.000864482 | 65 | 0.025546232 | 0.389982782 | a2c8 | 0.188714403 | 0.005827372 | 0.038647429 | 0.000643508 | 0.156712146 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | 0.020000000 | True | True | 0.022948421 | -0.000592415 | 66 | 0.025525885 | 0.412041474 | stage2 | 0.203673863 | 0.003924490 | 0.026463363 | 0.000436219 | 0.158097875 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | 0.030000000 | True | True | 0.022859173 | -0.000886893 | 66 | 0.025575667 | 0.412041474 | stage2 | 0.203673863 | 0.005886734 | 0.039695044 | 0.000653738 | 0.158097875 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | 0.030000000 | True | True | 0.022728714 | -0.000748802 | 73 | 0.023419614 | 0.494206089 | stage2 | 0.335373663 | 0.005194086 | 0.030689162 | 0.000540407 | 0.253296540 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | 0.020000000 | True | True | 0.022612121 | -0.000596892 | 66 | 0.025535023 | 0.421741418 | stage2 | 0.223787914 | 0.003945337 | 0.026672886 | 0.000438257 | 0.158683217 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | 0.020000000 | True | True | 0.022561633 | -0.000500033 | 73 | 0.023380662 | 0.494206089 | stage2 | 0.335373663 | 0.003462724 | 0.020459441 | 0.000360616 | 0.253296540 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | 0.030000000 | True | True | 0.022524070 | -0.000893593 | 66 | 0.025584885 | 0.421741418 | stage2 | 0.223787914 | 0.005918006 | 0.040009328 | 0.000656791 | 0.158683217 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | 0.020000000 | True | True | 0.021934147 | -0.000607319 | 67 | 0.025556614 | 0.448447736 | stage2 | 0.269154408 | 0.004003632 | 0.027161773 | 0.000443001 | 0.160074050 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | 0.030000000 | True | True | 0.021521722 | -0.000909184 | 66 | 0.025607061 | 0.448447736 | stage2 | 0.269154408 | 0.006005448 | 0.040742659 | 0.000663889 | 0.160074050 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p75.csv | 0.030000000 | True | True | 0.021236469 | -0.000641789 | 64 | 0.025459148 | 0.413807974 | a2c8 | 0.251422996 | 0.004453338 | 0.028593932 | 0.000482744 | 0.166540640 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv | 0.030000000 | True | True | 0.021015244 | -0.000653008 | 64 | 0.025480100 | 0.426381019 | a2c8 | 0.252643922 | 0.004476993 | 0.029117739 | 0.000487860 | 0.167312853 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | 0.020000000 | True | True | 0.020158737 | -0.000605159 | 75 | 0.026448183 | 0.512399527 | q2_bad | 0.314002637 | 0.004150840 | 0.028009388 | 0.000419702 | 0.280110076 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | 0.030000000 | True | True | 0.020081606 | -0.000906001 | 75 | 0.026498927 | 0.512399527 | q2_bad | 0.314002637 | 0.006226259 | 0.042014083 | 0.000628796 | 0.280110076 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | 0.020000000 | True | True | 0.019902112 | -0.000583513 | 73 | 0.027634012 | 0.491502217 | stage2 | 0.296562260 | 0.003938395 | 0.028218407 | 0.000397240 | 0.265051787 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | 0.030000000 | True | True | 0.019829461 | -0.000873670 | 73 | 0.027684589 | 0.491502217 | stage2 | 0.296562260 | 0.005907593 | 0.042327611 | 0.000595174 | 0.265051787 |
| submission_bigshot_11_jepa_multifeature_rawstack.csv | 0.015000000 | True | True | 0.019532591 | -0.000439135 | 66 | 0.025485972 | 0.398844089 | a2c8 | 0.190085511 | 0.002923836 | 0.019585618 | 0.000324758 | 0.157299103 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p5_mw1p0.csv | 0.015000000 | True | True | 0.019336293 | -0.000444743 | 66 | 0.025501093 | 0.412041474 | stage2 | 0.203673863 | 0.002943367 | 0.019847522 | 0.000327311 | 0.158097875 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw1p0.csv | 0.015000000 | True | True | 0.019281964 | -0.000433519 | 65 | 0.025470903 | 0.389982782 | a2c8 | 0.188714403 | 0.002913686 | 0.019323714 | 0.000322200 | 0.156712146 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p35_mw1p0.csv | 0.015000000 | True | True | 0.019154189 | -0.000448105 | 66 | 0.025510191 | 0.421741418 | stage2 | 0.223787914 | 0.002959003 | 0.020004664 | 0.000328841 | 0.158683217 |
| submission_block_canvas_multifeature_k8_c0p02_noq2_scale1p0.csv | 0.015000000 | True | True | 0.018854820 | -0.000455937 | 67 | 0.025531491 | 0.448447736 | stage2 | 0.269154408 | 0.003002724 | 0.020371330 | 0.000332403 | 0.160074050 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw0p75_mw0p75.csv | 0.020000000 | True | True | 0.018256610 | -0.000436003 | 65 | 0.025441254 | 0.426381019 | a2c8 | 0.252643922 | 0.002984662 | 0.019411826 | 0.000325476 | 0.167312853 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw1p0.csv | 0.020000000 | True | True | 0.018196789 | -0.000521916 | 68 | 0.029519529 | 0.462459713 | a2c8 | 0.241376067 | 0.003551540 | 0.026961773 | 0.000363710 | 0.178915447 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw1p0.csv | 0.020000000 | True | True | 0.018179203 | -0.000529388 | 69 | 0.029479835 | 0.475568053 | stage2 | 0.244273001 | 0.003574477 | 0.027310978 | 0.000367112 | 0.179403344 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p75_mw1p0.csv | 0.030000000 | True | True | 0.018132791 | -0.000781497 | 68 | 0.029571577 | 0.462459713 | a2c8 | 0.241376067 | 0.005327310 | 0.040442660 | 0.000545022 | 0.178915447 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p5_mw1p0.csv | 0.030000000 | True | True | 0.018115363 | -0.000792687 | 69 | 0.029531735 | 0.475568053 | stage2 | 0.244273001 | 0.005361715 | 0.040966467 | 0.000550124 | 0.179403344 |
| submission_jepa_multifeature_rawstack_k8_c0p02_noq2_rw1p0_mw0p75.csv | 0.020000000 | True | True | 0.018069518 | -0.000428519 | 64 | 0.025419963 | 0.413807974 | a2c8 | 0.251422996 | 0.002968892 | 0.019062621 | 0.000322067 | 0.166540640 |
| submission_block_canvas_multifeature_k5_c0p02_all_scale1p0.csv | 0.015000000 | True | True | 0.017964826 | -0.000454304 | 75 | 0.026422906 | 0.512399527 | q2_bad | 0.314002637 | 0.003113130 | 0.021007041 | 0.000314965 | 0.280110076 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw1p0.csv | 0.020000000 | True | True | 0.017910730 | -0.000533865 | 69 | 0.029456908 | 0.485297625 | stage2 | 0.266755659 | 0.003593651 | 0.027520501 | 0.000369149 | 0.179938305 |
| submission_jepa_multifeature_rawstack_k5_c0p02_noq2_rw0p35_mw1p0.csv | 0.030000000 | True | True | 0.017847670 | -0.000799386 | 69 | 0.029508901 | 0.485297625 | stage2 | 0.266755659 | 0.005390477 | 0.041280752 | 0.000553175 | 0.179938305 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale1p0.csv | 0.020000000 | True | True | 0.017067895 | -0.000544291 | 69 | 0.029405896 | 0.512203911 | stage2 | 0.316953984 | 0.003650095 | 0.028009388 | 0.000373890 | 0.181350807 |
| submission_block_canvas_multifeature_k5_c0p02_noq2_scale1p0.csv | 0.030000000 | True | True | 0.017006860 | -0.000814975 | 69 | 0.029458615 | 0.512203911 | stage2 | 0.316953984 | 0.005475143 | 0.042014083 | 0.000560267 | 0.181350807 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale0p75.csv | 0.015000000 | True | True | 0.016949359 | -0.000375337 | 73 | 0.023361249 | 0.494206089 | stage2 | 0.335373663 | 0.002597043 | 0.015344581 | 0.000270591 | 0.253296540 |
| submission_block_canvas_multifeature_k3_c0p02_all_scale1p0.csv | 0.015000000 | True | True | 0.016826897 | -0.000438034 | 73 | 0.027608815 | 0.491502217 | stage2 | 0.296562260 | 0.002953796 | 0.021163805 | 0.000298101 | 0.265051787 |
| submission_block_canvas_multifeature_k8_c0p02_all_scale1p0.csv | 0.010000000 | True | True | 0.016501606 | -0.000332077 | 74 | 0.023369627 | 0.450742441 | q2_bad | 0.268538582 | 0.002243986 | 0.013580886 | 0.000238386 | 0.250718585 |

## Negative-Control Gate Check

| source_kind | source_file | scale | source_known_public_lb | scaled_sensor_gate | scaled_expected_delta_focus_mean | scaled_cells_to_flip_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_move_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.005000000 | 0.576407777 | False | -0.000004429 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000044125 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.010000000 | 0.576407777 | False | -0.000008857 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000088251 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.015000000 | 0.576407777 | False | -0.000013285 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000132376 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.020000000 | 0.576407777 | False | -0.000017711 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000176502 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.030000000 | 0.576407777 | False | -0.000026562 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000264753 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.040000000 | 0.576407777 | False | -0.000035410 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000353004 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.050000000 | 0.576407777 | False | -0.000044254 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000441254 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.075000000 | 0.576407777 | False | -0.000066352 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000661882 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.100000000 | 0.576407777 | False | -0.000088429 | 39 | 1.000000000 | e72 | 1.000000000 | 0.000882509 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.150000000 | 0.576407777 | False | -0.000132525 | 39 | 1.000000000 | e72 | 1.000000000 | 0.001323763 |
| e72_bad_public | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.200000000 | 0.576407777 | False | -0.000176541 | 39 | 1.000000000 | e72 | 1.000000000 | 0.001765018 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.005000000 | 0.577439321 | False | 0.000000463 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.000205658 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.010000000 | 0.577439321 | False | 0.000000939 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.000411316 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.015000000 | 0.577439321 | False | 0.000001428 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.000616973 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.020000000 | 0.577439321 | False | 0.000001929 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.000822631 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.030000000 | 0.577439321 | False | 0.000002968 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.001233947 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.040000000 | 0.577439321 | False | 0.000004058 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.001645262 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.050000000 | 0.577439321 | False | 0.000005198 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.002056578 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.075000000 | 0.577439321 | False | 0.000008268 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.003084866 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.100000000 | 0.577439321 | False | 0.000011653 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.004113155 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.150000000 | 0.577439321 | False | 0.000019364 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.006169733 |
| a2c8_bad_public | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.200000000 | 0.577439321 | False | 0.000028332 | 2 | 1.000000000 | a2c8 | 1.000000000 | 0.008226310 |

## Decision

If the materialized row exists, it is not a JEPA full-model submission. It is a small-amplitude broad-world sensor: E95 remains the anchor, and only a controlled fraction of the broad survivor direction is grafted in. A public win would strengthen the claim that E95 is missing a broad latent branch; a loss would weaken broad-survivor geometry and push the search back to repaired-branch/hidden-label-resolution sensors.
