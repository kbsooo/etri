# Selector Support Topology Audit

Question: where do pairwise-public support and old hidden-subset support agree or disagree across the already scored candidate universe?

## Zone Summary

| support_zone | n | pair_strict_p90 | pair_majority | old_majority | two_selector_majority | pair_probe | pair_submit | strict_candidate_shape | best_pair_p90 | best_old_p90 | median_old_rate | median_pair_rate | median_move | median_bad_axis | median_q3s4_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_only | 465 | 209 | 465 | 0 | 0 | 386 | 61 | 0 | -6.52173e-05 | 0.00054061 | 0.266409 | 0.875676 | 0.0008157 | 0.036372 | 0.639225 |
| old_only | 97 | 0 | 0 | 97 | 0 | 0 | 0 | 0 | 6.77661e-05 | 0.000539282 | 0.57529 | 0.145946 | 0.00852481 | 0.0239811 | 0.396278 |
| neither | 5151 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3.51892e-06 | 0.000548476 | 0.138996 | 0.183784 | 0.00713917 | 0.0375835 | 0.388926 |
| pair_probe_not_majority | 56 | 0 | 0 | 0 | 0 | 56 | 0 | 0 | 4.13441e-06 | 0.000570569 | 0.297297 | 0.672973 | 0.00170717 | 0.0314407 | 0.62968 |

## Source Summary

| support_source | n | pair_strict_p90 | pair_majority | old_majority | two_selector_majority | pair_probe | pair_submit | strict_candidate_shape | best_pair_p90 | best_old_p90 | median_old_rate | median_pair_rate | median_move | median_bad_axis | median_q3s4_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| focused_label_flow_review | 163 | 163 | 163 | 0 | 0 | 163 | 61 | 0 | -6.52173e-05 | 0.000569397 | 0.274131 | 0.967568 | 0.00437279 | 0.0183531 | 1 |
| broad_pairwise_universe | 1886 | 46 | 251 | 92 | 0 | 216 | 0 | 0 | -1.56228e-06 | 0.000539282 | 0.254826 | 0.354054 | 0.00571912 | 0.0367265 | 0.355309 |
| block_measurement_rescore | 3316 | 0 | 51 | 0 | 0 | 63 | 0 | 0 | 1.07928e-05 | 0.000569355 | 0.127413 | 0.164865 | 0.00731311 | 0.0350152 | 0.399479 |
| old_positive_rescore | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0.000135356 | 0.000539282 | 0.501931 | 0.132432 | 0.0440096 | 0 | 0.333592 |
| oof_top_rescore | 399 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000532604 | 0.00111663 | 0.003861 | 0.0918919 | 0.082271 | 0.200585 | 0.387184 |

## Dominant Target Summary

| dominant_target | n | pair_strict_p90 | pair_majority | old_majority | two_selector_majority | pair_probe | pair_submit | strict_candidate_shape | best_pair_p90 | best_old_p90 | median_old_rate | median_pair_rate | median_move | median_bad_axis | median_q3s4_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | 252 | 132 | 178 | 2 | 0 | 172 | 61 | 0 | -6.52173e-05 | 0.00054061 | 0.27027 | 0.962162 | 0.00639597 | 0.0304012 | 0.930651 |
| S3 | 375 | 33 | 52 | 7 | 0 | 58 | 0 | 0 | -1.56228e-06 | 0.000577753 | 0.135135 | 0.132432 | 0.0248301 | 0.0514979 | 0.285169 |
| Q3 | 3596 | 31 | 98 | 88 | 0 | 67 | 0 | 0 | -6.86867e-07 | 0.000539282 | 0.173745 | 0.224324 | 0.00633424 | 0.0341445 | 0.437767 |
| Q1 | 806 | 13 | 117 | 0 | 0 | 115 | 0 | 0 | -4.85982e-07 | 0.000550641 | 0.131274 | 0.25 | 0.00422513 | 0.0514285 | 0.257634 |
| S2 | 178 | 0 | 20 | 0 | 0 | 30 | 0 | 0 | 1.76835e-06 | 0.00057833 | 0.111969 | 0.236486 | 0.0581813 | 0.0432071 | 0.282627 |
| S1 | 528 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6.24616e-06 | 0.000577999 | 0.034749 | 0.0851351 | 0.0146565 | 0.0487613 | 0.267621 |
| Q2 | 34 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.000149696 | 0.000625703 | 0 | 0.0837838 | 0.010222 | 0.0684928 | 0.302909 |

## Pair-Only Candidates

| source_path | support_source | candidate_bucket | support_zone | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | q3s4_move_share | dominant_target | pair_probe_gate | pair_submit_gate | strict_candidate_shape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_label_flow_focused_6b9335b1.csv | focused_label_flow_review | other | pair_only | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bcb4777d.csv | focused_label_flow_review | other | pair_only | -6.50841e-05 | 0.967568 | 0.000676129 | 0.277992 | 0.0161135 | 0.00729976 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_c87aaa14.csv | focused_label_flow_review | other | pair_only | -6.48179e-05 | 0.967568 | 0.000675114 | 0.277992 | 0.0180147 | 0.00718862 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_f7699bdc.csv | focused_label_flow_review | other | pair_only | -6.48177e-05 | 0.967568 | 0.000675958 | 0.277992 | 0.0164911 | 0.00730427 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_fe7cc64f.csv | focused_label_flow_review | other | pair_only | -6.47418e-05 | 0.967568 | 0.000676253 | 0.277992 | 0.0159104 | 0.00733821 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_04d507ca.csv | focused_label_flow_review | other | pair_only | -6.47355e-05 | 0.967568 | 0.000676453 | 0.277992 | 0.0155264 | 0.00736065 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_ab52c283.csv | focused_label_flow_review | other | pair_only | -6.47254e-05 | 0.967568 | 0.000676755 | 0.277992 | 0.0149552 | 0.00739404 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_70601867.csv | focused_label_flow_review | other | pair_only | -6.47105e-05 | 0.967568 | 0.000677163 | 0.277992 | 0.0142021 | 0.00743807 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_8a5e8191.csv | focused_label_flow_review | other | pair_only | -6.46854e-05 | 0.967568 | 0.000677786 | 0.281853 | 0.0130896 | 0.00750311 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bfe4ee38.csv | focused_label_flow_review | other | pair_only | -6.45194e-05 | 0.967568 | 0.000674818 | 0.277992 | 0.0185975 | 0.00715456 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_87affbd1.csv | focused_label_flow_review | other | pair_only | -6.43208e-05 | 0.967568 | 0.000674623 | 0.277992 | 0.0189894 | 0.00713166 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_e3dbc41f.csv | focused_label_flow_review | other | pair_only | -6.40237e-05 | 0.967568 | 0.000674335 | 0.277992 | 0.0195824 | 0.00709701 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_68e4f54e.csv | focused_label_flow_review | other | pair_only | -6.40018e-05 | 0.967568 | 0.000678337 | 0.281853 | 0.0126145 | 0.00759017 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_d317c71f.csv | focused_label_flow_review | other | pair_only | -6.35844e-05 | 0.967568 | 0.000678686 | 0.281853 | 0.0126347 | 0.0076232 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_59aab609.csv | focused_label_flow_review | other | pair_only | -6.31617e-05 | 0.967568 | 0.000683839 | 0.27027 | 0.0139122 | 0.00799635 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_56572a68.csv | focused_label_flow_review | other | pair_only | -6.31307e-05 | 0.967568 | 0.00068325 | 0.274131 | 0.0138927 | 0.00796472 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_86a7b095.csv | focused_label_flow_review | other | pair_only | -6.30971e-05 | 0.967568 | 0.000678921 | 0.281853 | 0.0126481 | 0.00764505 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_64ea2921.csv | focused_label_flow_review | other | pair_only | -6.29799e-05 | 0.967568 | 0.000682862 | 0.274131 | 0.0138797 | 0.00794348 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_cfb4d55f.csv | focused_label_flow_review | other | pair_only | -6.27639e-05 | 0.967568 | 0.000682287 | 0.274131 | 0.0138599 | 0.00791139 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bc6da6ae.csv | focused_label_flow_review | other | pair_only | -6.24981e-05 | 0.967568 | 0.000684726 | 0.266409 | 0.013938 | 0.00803813 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_6db9ce6c.csv | focused_label_flow_review | other | pair_only | -6.24461e-05 | 0.962162 | 0.000690862 | 0.262548 | 0.0165576 | 0.00835722 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_207e8b8f.csv | focused_label_flow_review | other | pair_only | -6.23925e-05 | 0.967568 | 0.000679274 | 0.281853 | 0.0126681 | 0.00767757 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_db4d87fa.csv | focused_label_flow_review | other | pair_only | -6.23619e-05 | 0.964865 | 0.000690377 | 0.262548 | 0.0164123 | 0.00833666 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_d0c38a15.csv | focused_label_flow_review | other | pair_only | -6.21834e-05 | 0.967568 | 0.000679748 | 0.281853 | 0.0126945 | 0.0077205 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_251db97c.csv | focused_label_flow_review | other | pair_only | -6.21726e-05 | 0.967568 | 0.000689654 | 0.262548 | 0.016193 | 0.00830562 | 1 | S4 | True | True | False |

## Old-Only Candidates

| source_path | support_source | candidate_bucket | support_zone | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | q3s4_move_share | dominant_target | pair_probe_gate | pair_submit_gate | strict_candidate_shape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv | broad_pairwise_universe | axis_repair | old_only | 0.000135356 | 0.145946 | 0.000539282 | 0.787645 | 0.02479 | 0.00853087 | 0.398687 | Q3 | False | False | False |
| jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | old_positive_rescore | raw_timeline | old_only | 0.000135356 | 0.145946 | 0.000539282 | 0.787645 | 0.02479 | 0.00853087 | 0.398687 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00075_0bbf9d04.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135191 | 0.145946 | 0.000539343 | 0.787645 | 0.0247833 | 0.00852633 | 0.398681 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_strength_prob_bad_raw_ortho_g00075_662099aa.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135179 | 0.145946 | 0.000539346 | 0.787645 | 0.0247811 | 0.00852612 | 0.398684 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_entropy_prob_bad_raw_ortho_g00100_acf7638d.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135138 | 0.145946 | 0.000539358 | 0.787645 | 0.0247771 | 0.00852505 | 0.398666 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00100_a6ce392e.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135136 | 0.145946 | 0.000539363 | 0.787645 | 0.024781 | 0.00852481 | 0.398678 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00100_306226f5.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135252 | 0.145946 | 0.000539374 | 0.787645 | 0.0248284 | 0.00852567 | 0.398931 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00100_f22e587f.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135231 | 0.145946 | 0.000539383 | 0.787645 | 0.0248213 | 0.0085257 | 0.39893 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00075_894a53ad.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135228 | 0.145946 | 0.000539387 | 0.787645 | 0.0248234 | 0.00852571 | 0.398929 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_raw_ortho_g00150_c968b72d.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135026 | 0.145946 | 0.000539403 | 0.787645 | 0.0247765 | 0.0085218 | 0.398673 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00150_76bed8db.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135216 | 0.145946 | 0.000539404 | 0.787645 | 0.0248379 | 0.00852421 | 0.398999 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00150_033ab59a.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.0001352 | 0.145946 | 0.00053942 | 0.787645 | 0.0248476 | 0.00852313 | 0.39905 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00100_f3f65865.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135186 | 0.145946 | 0.000539421 | 0.787645 | 0.0248345 | 0.00852405 | 0.399007 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00150_c105c2bf.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.00013517 | 0.145946 | 0.000539433 | 0.787645 | 0.024837 | 0.00852319 | 0.399047 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00200_1e74fe02.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.00013517 | 0.145946 | 0.000539445 | 0.787645 | 0.0248538 | 0.00852205 | 0.3991 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_top40_prob_bad_raw_ortho_g00200_06cdf759.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135158 | 0.145946 | 0.00053946 | 0.787645 | 0.0248679 | 0.0085206 | 0.399168 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_raw_ortho_g00200_92036fe6.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135149 | 0.145946 | 0.000539466 | 0.787645 | 0.0248668 | 0.00852065 | 0.399166 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_entropy_mid_prob_bad_raw_ortho_g00200_cf1cbb33.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135109 | 0.145946 | 0.000539484 | 0.787645 | 0.0248526 | 0.00852071 | 0.399163 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_ones_prob_bad_raw_ortho_g00150_59a513b2.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000135103 | 0.145946 | 0.000539491 | 0.787645 | 0.0248567 | 0.00852082 | 0.399158 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_logit_g00300_1e863baf.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000134711 | 0.145946 | 0.000539517 | 0.787645 | 0.02476 | 0.00851334 | 0.398628 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00300_bf5d732e.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000134701 | 0.145946 | 0.000539523 | 0.787645 | 0.0247647 | 0.00851272 | 0.398655 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_bad_ortho_g00300_6e667d7d.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000134698 | 0.145946 | 0.000539523 | 0.787645 | 0.0247632 | 0.00851275 | 0.398655 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_entropy_prob_bad_raw_ortho_g00300_a6a42719.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.00013508 | 0.145946 | 0.000539526 | 0.787645 | 0.0248857 | 0.00851782 | 0.399298 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_q3_s3_anti_signed_top40_prob_g00600_f7995f68.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000134053 | 0.145946 | 0.000539763 | 0.779923 | 0.0247394 | 0.00849471 | 0.398616 | Q3 | False | False | False |
| analysis_outputs/submission_raw05_jepa_public6drift_raw05_q1_s2_s3_anti_signed_strength_prob_bad_ortho_g00800_4a4e63a2.csv | broad_pairwise_universe | raw05_jepa | old_only | 0.000134552 | 0.145946 | 0.000540011 | 0.764479 | 0.025095 | 0.00849087 | 0.400566 | Q3 | False | False | False |

## Pair Probe Candidates

| source_path | support_source | candidate_bucket | support_zone | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | q3s4_move_share | dominant_target | pair_probe_gate | pair_submit_gate | strict_candidate_shape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_label_flow_focused_6b9335b1.csv | focused_label_flow_review | other | pair_only | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bcb4777d.csv | focused_label_flow_review | other | pair_only | -6.50841e-05 | 0.967568 | 0.000676129 | 0.277992 | 0.0161135 | 0.00729976 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_c87aaa14.csv | focused_label_flow_review | other | pair_only | -6.48179e-05 | 0.967568 | 0.000675114 | 0.277992 | 0.0180147 | 0.00718862 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_f7699bdc.csv | focused_label_flow_review | other | pair_only | -6.48177e-05 | 0.967568 | 0.000675958 | 0.277992 | 0.0164911 | 0.00730427 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_fe7cc64f.csv | focused_label_flow_review | other | pair_only | -6.47418e-05 | 0.967568 | 0.000676253 | 0.277992 | 0.0159104 | 0.00733821 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_04d507ca.csv | focused_label_flow_review | other | pair_only | -6.47355e-05 | 0.967568 | 0.000676453 | 0.277992 | 0.0155264 | 0.00736065 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_ab52c283.csv | focused_label_flow_review | other | pair_only | -6.47254e-05 | 0.967568 | 0.000676755 | 0.277992 | 0.0149552 | 0.00739404 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_70601867.csv | focused_label_flow_review | other | pair_only | -6.47105e-05 | 0.967568 | 0.000677163 | 0.277992 | 0.0142021 | 0.00743807 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_8a5e8191.csv | focused_label_flow_review | other | pair_only | -6.46854e-05 | 0.967568 | 0.000677786 | 0.281853 | 0.0130896 | 0.00750311 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bfe4ee38.csv | focused_label_flow_review | other | pair_only | -6.45194e-05 | 0.967568 | 0.000674818 | 0.277992 | 0.0185975 | 0.00715456 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_87affbd1.csv | focused_label_flow_review | other | pair_only | -6.43208e-05 | 0.967568 | 0.000674623 | 0.277992 | 0.0189894 | 0.00713166 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_e3dbc41f.csv | focused_label_flow_review | other | pair_only | -6.40237e-05 | 0.967568 | 0.000674335 | 0.277992 | 0.0195824 | 0.00709701 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_68e4f54e.csv | focused_label_flow_review | other | pair_only | -6.40018e-05 | 0.967568 | 0.000678337 | 0.281853 | 0.0126145 | 0.00759017 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_d317c71f.csv | focused_label_flow_review | other | pair_only | -6.35844e-05 | 0.967568 | 0.000678686 | 0.281853 | 0.0126347 | 0.0076232 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_59aab609.csv | focused_label_flow_review | other | pair_only | -6.31617e-05 | 0.967568 | 0.000683839 | 0.27027 | 0.0139122 | 0.00799635 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_56572a68.csv | focused_label_flow_review | other | pair_only | -6.31307e-05 | 0.967568 | 0.00068325 | 0.274131 | 0.0138927 | 0.00796472 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_86a7b095.csv | focused_label_flow_review | other | pair_only | -6.30971e-05 | 0.967568 | 0.000678921 | 0.281853 | 0.0126481 | 0.00764505 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_64ea2921.csv | focused_label_flow_review | other | pair_only | -6.29799e-05 | 0.967568 | 0.000682862 | 0.274131 | 0.0138797 | 0.00794348 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_cfb4d55f.csv | focused_label_flow_review | other | pair_only | -6.27639e-05 | 0.967568 | 0.000682287 | 0.274131 | 0.0138599 | 0.00791139 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_bc6da6ae.csv | focused_label_flow_review | other | pair_only | -6.24981e-05 | 0.967568 | 0.000684726 | 0.266409 | 0.013938 | 0.00803813 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_6db9ce6c.csv | focused_label_flow_review | other | pair_only | -6.24461e-05 | 0.962162 | 0.000690862 | 0.262548 | 0.0165576 | 0.00835722 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_207e8b8f.csv | focused_label_flow_review | other | pair_only | -6.23925e-05 | 0.967568 | 0.000679274 | 0.281853 | 0.0126681 | 0.00767757 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_db4d87fa.csv | focused_label_flow_review | other | pair_only | -6.23619e-05 | 0.964865 | 0.000690377 | 0.262548 | 0.0164123 | 0.00833666 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_d0c38a15.csv | focused_label_flow_review | other | pair_only | -6.21834e-05 | 0.967568 | 0.000679748 | 0.281853 | 0.0126945 | 0.0077205 | 1 | S4 | True | True | False |
| analysis_outputs/submission_label_flow_focused_251db97c.csv | focused_label_flow_review | other | pair_only | -6.21726e-05 | 0.967568 | 0.000689654 | 0.262548 | 0.016193 | 0.00830562 | 1 | S4 | True | True | False |

## Strict Candidate Shape

_None._

## Read

- `two_selector_majority` is the missing cell. If this remains empty, current candidates do not contain a robust public-positive direction.
- `pair_only` mostly means a candidate sits on the pairwise-public surrogate but lacks hidden-subset support; these are diagnostic sensors, not submissions.
- `old_only` means the old selector sees something, but the pairwise public order vetoes it; these candidates are useful for selector reconciliation, not direct submission.
- A useful next candidate must move from pair-only/old-only into two-selector support, or produce a new anchor that explains why one selector should be retired.

## Files

- `selector_support_topology_audit.csv`
- `selector_support_topology_by_source.csv`
- `selector_support_topology_by_target.csv`
- `selector_support_topology_zones.csv`
- `selector_support_topology_shortlist.csv`
