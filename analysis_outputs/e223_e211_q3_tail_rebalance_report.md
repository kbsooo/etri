# E223 E211 Q3 Tail Rebalance

## Question

Can we keep the E211 S4 body while reducing the Q3 hard-tail risk identified by E222?

## Graft vs Anchor

| candidate_id | pair_kind | q3_scale | s4_mode | anchor | anchor_scale | moved_cells | targets_moved | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | q3_top1_over_abs_expected | geometry_delta | e211_frontier_gate | e223_gate | e223_score | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e223_q3s0p75_closer_e154 | graft_vs_anchor | 0.750000000 | closer | e154 | 0.500000000 | 355 | Q3,S4 | -0.000636968 | 0.003852760 | 0.464872165 | 0.185262393 | 0.936649094 | -0.000556139 | True | True | 0.632476310 | submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv |
| e223_q3s0p75_toward_e95 | graft_vs_anchor | 0.750000000 | toward | e95 | 0.500000000 | 358 | Q3,S4 | -0.000635269 | 0.003912769 | 0.465282775 | 0.185757873 | 0.920258541 | -0.000595322 | True | True | 0.631515040 | submission_e223_jepa_q3s0p75_s4toward_e95_a0p5_55d326e5.csv |
| e223_q3s0p75_toward_e154 | graft_vs_anchor | 0.750000000 | toward | e154 | 0.500000000 | 358 | Q3,S4 | -0.000632208 | 0.003915830 | 0.465282775 | 0.186657208 | 0.936649094 | -0.000595322 | True | True | 0.627798622 | submission_e223_jepa_q3s0p75_s4toward_e154_a0p5_b5bc6d7c.csv |
| e223_q3s0p75_closer_e95 | graft_vs_anchor | 0.750000000 | closer | e95 | 0.500000000 | 354 | Q3,S4 | -0.000628326 | 0.003841258 | 0.464674464 | 0.187810373 | 0.920258541 | -0.000556139 | True | True | 0.624450795 | submission_e223_jepa_q3s0p75_s4closer_e95_a0p5_dac78e4d.csv |
| e223_q3s1p0_closer_e154 | graft_vs_anchor | 1.000000000 | closer | e154 | 0.500000000 | 355 | Q3,S4 | -0.000655277 | 0.004765654 | 0.463231022 | 0.240114517 | 1.090400695 | -0.000619840 | True | False | 0.643913061 | submission_e223_jepa_q3s1p0_s4closer_e154_a0p5_c20eee9c.csv |
| e223_q3s1p0_toward_e95 | graft_vs_anchor | 1.000000000 | toward | e95 | 0.500000000 | 358 | Q3,S4 | -0.000654330 | 0.004824911 | 0.463586825 | 0.240462280 | 1.068226753 | -0.000659024 | True | False | 0.643395499 | submission_e223_jepa_q3s1p0_s4toward_e95_a0p5_e4e44d91.csv |
| e223_q3s1p0_toward_e154 | graft_vs_anchor | 1.000000000 | toward | e154 | 0.500000000 | 358 | Q3,S4 | -0.000650517 | 0.004828724 | 0.463586825 | 0.241871425 | 1.090400695 | -0.000659024 | True | False | 0.638618254 | submission_e223_jepa_q3s1p0_s4toward_e154_a0p5_50e6b7ec.csv |
| e223_q3s1p0_closer_e95 | graft_vs_anchor | 1.000000000 | closer | e95 | 0.500000000 | 354 | Q3,S4 | -0.000647387 | 0.004753401 | 0.463062456 | 0.243040999 | 1.068226753 | -0.000619840 | True | False | 0.636882199 | submission_e223_jepa_q3s1p0_s4closer_e95_a0p5_8e3dc02d.csv |

## Actual vs E95

| candidate_id | pair_kind | q3_scale | s4_mode | anchor | anchor_scale | moved_cells | targets_moved | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | q3_top1_over_abs_expected | geometry_delta | e211_frontier_gate | e223_gate | e223_score | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e223_q3s0p75_closer_e154 | actual_vs_e95 | 0.750000000 | closer | e154 | 0.500000000 | 534 | Q1,Q3,S2,S3,S4 | -0.000666805 | 0.004533247 | 0.464769102 | 0.176972452 | 0.936649094 | -0.000556139 | True | False | 0.662015652 | submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv |
| e223_q3s1p0_closer_e154 | actual_vs_e95 | 1.000000000 | closer | e154 | 0.500000000 | 534 | Q1,Q3,S2,S3,S4 | -0.000685115 | 0.005426827 | 0.463226350 | 0.229657247 | 1.090400695 | -0.000619840 | True | False | 0.660880955 | submission_e223_jepa_q3s1p0_s4closer_e154_a0p5_c20eee9c.csv |
| e223_q3s0p75_toward_e154 | actual_vs_e95 | 0.750000000 | toward | e154 | 0.500000000 | 537 | Q1,Q3,S2,S3,S4 | -0.000662046 | 0.004596316 | 0.465125190 | 0.178244804 | 0.936649094 | -0.000595322 | True | False | 0.657295372 | submission_e223_jepa_q3s0p75_s4toward_e154_a0p5_b5bc6d7c.csv |
| e223_q3s1p0_toward_e154 | actual_vs_e95 | 1.000000000 | toward | e154 | 0.500000000 | 537 | Q1,Q3,S2,S3,S4 | -0.000680355 | 0.005489897 | 0.463542317 | 0.231263944 | 1.090400695 | -0.000659024 | True | False | 0.654891259 | submission_e223_jepa_q3s1p0_s4toward_e154_a0p5_50e6b7ec.csv |
| e223_q3s1p0_toward_e95 | actual_vs_e95 | 1.000000000 | toward | e95 | 0.500000000 | 358 | Q3,S4 | -0.000654330 | 0.004824911 | 0.463586825 | 0.240462280 | 1.068226753 | -0.000659024 | True | False | 0.643395499 | submission_e223_jepa_q3s1p0_s4toward_e95_a0p5_e4e44d91.csv |
| e223_q3s1p0_closer_e95 | actual_vs_e95 | 1.000000000 | closer | e95 | 0.500000000 | 354 | Q3,S4 | -0.000647387 | 0.004753401 | 0.463062456 | 0.243040999 | 1.068226753 | -0.000619840 | True | False | 0.636882199 | submission_e223_jepa_q3s1p0_s4closer_e95_a0p5_8e3dc02d.csv |
| e223_q3s0p75_toward_e95 | actual_vs_e95 | 0.750000000 | toward | e95 | 0.500000000 | 358 | Q3,S4 | -0.000635269 | 0.003912769 | 0.465282775 | 0.185757873 | 0.920258541 | -0.000595322 | True | False | 0.631515040 | submission_e223_jepa_q3s0p75_s4toward_e95_a0p5_55d326e5.csv |
| e223_q3s0p75_closer_e95 | actual_vs_e95 | 0.750000000 | closer | e95 | 0.500000000 | 354 | Q3,S4 | -0.000628326 | 0.003841258 | 0.464674464 | 0.187810373 | 0.920258541 | -0.000556139 | True | False | 0.624450795 | submission_e223_jepa_q3s0p75_s4closer_e95_a0p5_dac78e4d.csv |

## Target Breakdown

| candidate_id | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| e223_q3s0p75_closer_e154 | Q3 | 250 | -0.000125988 | 0.002667622 | 0.455478271 | 0.936649094 |
| e223_q3s0p75_closer_e154 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| e223_q3s0p75_closer_e95 | Q3 | 250 | -0.000128232 | 0.002665378 | 0.455478271 | 0.920258541 |
| e223_q3s0p75_closer_e95 | S4 | 104 | -0.000500095 | 0.001175880 | 0.480857314 | 0.168985725 |
| e223_q3s0p75_toward_e154 | Q3 | 250 | -0.000125988 | 0.002667622 | 0.455478271 | 0.936649094 |
| e223_q3s0p75_toward_e154 | S4 | 108 | -0.000506220 | 0.001248207 | 0.481796770 | 0.166940843 |
| e223_q3s0p75_toward_e95 | Q3 | 250 | -0.000128232 | 0.002665378 | 0.455478271 | 0.920258541 |
| e223_q3s0p75_toward_e95 | S4 | 108 | -0.000507037 | 0.001247390 | 0.481796770 | 0.166671896 |
| e223_q3s1p0_closer_e154 | Q3 | 250 | -0.000144297 | 0.003580516 | 0.455478271 | 1.090400695 |
| e223_q3s1p0_closer_e154 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| e223_q3s1p0_closer_e95 | Q3 | 250 | -0.000147292 | 0.003577521 | 0.455478271 | 1.068226753 |
| e223_q3s1p0_closer_e95 | S4 | 104 | -0.000500095 | 0.001175880 | 0.480857314 | 0.168985725 |
| e223_q3s1p0_toward_e154 | Q3 | 250 | -0.000144297 | 0.003580516 | 0.455478271 | 1.090400695 |
| e223_q3s1p0_toward_e154 | S4 | 108 | -0.000506220 | 0.001248207 | 0.481796770 | 0.166940843 |
| e223_q3s1p0_toward_e95 | Q3 | 250 | -0.000147292 | 0.003577521 | 0.455478271 | 1.068226753 |
| e223_q3s1p0_toward_e95 | S4 | 108 | -0.000507037 | 0.001247390 | 0.481796770 | 0.166671896 |

## Selected

| candidate_id | pair_kind | q3_scale | s4_mode | anchor | anchor_scale | moved_cells | targets_moved | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | q3_top1_over_abs_expected | geometry_delta | e211_frontier_gate | e223_gate | e223_score | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e223_q3s0p75_closer_e154 | graft_vs_anchor | 0.750000000 | closer | e154 | 0.500000000 | 355 | Q3,S4 | -0.000636968 | 0.003852760 | 0.464872165 | 0.185262393 | 0.936649094 | -0.000556139 | True | True | 0.632476310 | submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv |
| e223_q3s0p75_toward_e95 | graft_vs_anchor | 0.750000000 | toward | e95 | 0.500000000 | 358 | Q3,S4 | -0.000635269 | 0.003912769 | 0.465282775 | 0.185757873 | 0.920258541 | -0.000595322 | True | True | 0.631515040 | submission_e223_jepa_q3s0p75_s4toward_e95_a0p5_55d326e5.csv |
| e223_q3s0p75_toward_e154 | graft_vs_anchor | 0.750000000 | toward | e154 | 0.500000000 | 358 | Q3,S4 | -0.000632208 | 0.003915830 | 0.465282775 | 0.186657208 | 0.936649094 | -0.000595322 | True | True | 0.627798622 | submission_e223_jepa_q3s0p75_s4toward_e154_a0p5_b5bc6d7c.csv |
| e223_q3s0p75_closer_e95 | graft_vs_anchor | 0.750000000 | closer | e95 | 0.500000000 | 354 | Q3,S4 | -0.000628326 | 0.003841258 | 0.464674464 | 0.187810373 | 0.920258541 | -0.000556139 | True | True | 0.624450795 | submission_e223_jepa_q3s0p75_s4closer_e95_a0p5_dac78e4d.csv |

## Decision

- Best E223 candidate: `submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv`. It lowers Q3 to `0.75`, keeps S4 `closer`, and preserves E211 frontier/geometry eligibility while reducing Q3 top-cell risk.
- This is a risk-rebalanced JEPA sensor, not a fully support-safe candidate: support probability remains below 0.5, but Q3 adverse capacity and top-cell concentration are materially lower than the E211 selected files.
- This is a direct post-E216/E222 correction, not a new model-capacity experiment.
