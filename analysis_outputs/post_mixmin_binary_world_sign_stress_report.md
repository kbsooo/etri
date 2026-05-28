# E52 Post-Mixmin Binary-World Sign Stress

## Observe

Mixmin is now a real public anchor. E50/E51 failed to translate calendar or anchor-calendar fingerprints into a known-submission selector.

## Wonder

If we condition the E30/E32 binary worlds on the observed mixmin public delta, does any existing candidate have a stable one-sided sign versus mixmin?

## Hypothesis

H52: mixmin is not just the best known public file; it may be a local sign frontier inside the current binary-world family. If true, post-mixmin feasible worlds should not certify another candidate as one-sided better than mixmin. If false, at least one candidate should beat mixmin across mixmin-compatible and low-energy world bands.

## Method

- Actual mixmin delta versus a2c8: `-0.0011326805`.
- Raw05-a2c8 gap used as one resolution unit: `0.0000869862`.
- Reused the E30 frontier-box binary worlds and E32 anchor-energy scores.
- Defined post-mixmin feasible bands by whether each world reproduces mixmin's observed delta within 1x, 2x, or 5x the raw05-a2c8 gap, plus LeJEPA-style postmix energy combining old anchor energy and mixmin residual.
- Scored curated candidates from E51, E37 bridge variants, E38 worldview sensors, and top selected bridge families by LogLoss delta versus mixmin on every binary world.

## World Bands

| band | worlds | random_fit_worlds | median_anchor_energy | median_postmix_world_energy | median_mixmin_error_over_gap | min_mixmin_delta_vs_a2c8 | median_mixmin_delta_vs_a2c8 | max_mixmin_delta_vs_a2c8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 29 | 19 | -0.189324 | 0.115193 | 3.77104 | -0.01018 | -0.000806675 | 0.00877411 |
| old_low_anchor_half | 15 | 12 | -1.11728 | -0.428381 | 3.74778 | -0.00127493 | -0.000806675 | -0.000537096 |
| old_low_anchor_quarter | 7 | 7 | -2.0751 | -1.12397 | 1.96078 | -0.00127493 | -0.00096212 | -0.000537096 |
| mixmin_fit_gap | 5 | 5 | -1.01174 | -1.32118 | 0.326053 | -0.00120947 | -0.00114376 | -0.00110285 |
| mixmin_fit_2gap | 8 | 7 | -1.26976 | -1.24871 | 0.612835 | -0.00127493 | -0.0011524 | -0.00096212 |
| mixmin_fit_5gap | 18 | 12 | -0.266992 | -0.0443541 | 2.2425 | -0.00137289 | -0.00103249 | -0.000740159 |
| mixmin_fit_gap_low_anchor_half | 5 | 5 | -1.01174 | -1.32118 | 0.326053 | -0.00120947 | -0.00114376 | -0.00110285 |
| mixmin_fit_2gap_low_anchor_half | 7 | 7 | -1.52778 | -1.25074 | 0.342926 | -0.00127493 | -0.00114376 | -0.00096212 |
| mixmin_fit_2gap_low_anchor_quarter | 4 | 4 | -1.7637 | -1.38125 | 0.989106 | -0.00127493 | -0.00112331 | -0.00096212 |
| mixmin_fit_gap_random_fit | 5 | 5 | -1.01174 | -1.32118 | 0.326053 | -0.00120947 | -0.00114376 | -0.00110285 |
| postmix_energy_half | 14 | 11 | -1.06451 | -0.704713 | 2.02837 | -0.00127493 | -0.00095624 | -0.000602114 |
| postmix_energy_quarter | 7 | 7 | -1.52778 | -1.25074 | 0.342926 | -0.00127493 | -0.00114376 | -0.00096212 |
| postmix_energy_half_random_fit | 11 | 11 | -1.52778 | -1.12397 | 1.63529 | -0.00127493 | -0.00110285 | -0.000602114 |

## Top Candidate Signs

| name | role | source | mixmin_fit_gap__worlds | mixmin_fit_gap__better_rate | mixmin_fit_gap__median_delta | mixmin_fit_gap__max_delta | mixmin_fit_2gap__better_rate | postmix_energy_quarter__better_rate | postmix_energy_quarter__median_delta | postmix_energy_quarter__max_delta | mean_abs_logit_move_vs_mixmin | mixmin_equivalent_prediction | strict_better_than_mixmin_gate | loose_better_than_mixmin_gate | near_tie_with_mixmin_gate | postmix_sign_rank_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bridge_blend_m0p75_s1p25 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0.2 | 3.41455e-05 | 4.8002e-05 | 0.375 | 0.285714 | 8.82539e-06 | 4.8002e-05 | 0.00352245 | False | False | False | True | -4.22985e-05 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv |
| mixmin | active_frontier | manual_anchor | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True | False | False | False | 0 | analysis_outputs/submission_mixmin_0c916bb4.csv |
| bridge_mixmin_s1p00 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0 | 2.22045e-16 | 0 | 0 | 0 | 2.22045e-16 | 3.85277e-17 | True | False | False | False | 5.55112e-17 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s1p00.csv |
| direns_c4af | inverse_feasibility_candidate | E26_candidate_list | 5 | 0 | 3.30461e-05 | 9.6419e-05 | 0.125 | 0.142857 | 3.30461e-05 | 9.6419e-05 | 0.00191427 | False | False | False | False | 5.22453e-05 | analysis_outputs/submission_direns_c4af1fd8.csv |
| bridge_blend_m0p75_s1p00 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000209303 | 0.000223992 | 0 | 0 | 0.000193895 | 0.000223992 | 0.0100911 | False | False | False | False | 0.000362249 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p00.csv |
| bridge_mixmin_s0p75 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.00023138 | 0.000247807 | 0 | 0 | 0.00023138 | 0.000264172 | 0.0114036 | False | False | False | False | 0.000413114 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p75.csv |
| bridge_blend_m0p50_s1p25 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000303502 | 0.000323797 | 0 | 0 | 0.000245418 | 0.000323797 | 0.0139975 | False | False | False | False | 0.00050716 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p25.csv |
| bridge_blend_m0p75_s0p75 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000399786 | 0.000435279 | 0 | 0 | 0.000399786 | 0.000435279 | 0.0189699 | False | False | False | False | 0.000708499 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p75.csv |
| bridge_blend_m0p50_s1p00 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000444336 | 0.000473713 | 0 | 0 | 0.00041352 | 0.000473713 | 0.0201822 | False | False | False | False | 0.000769524 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p00.csv |
| bridge_mixmin_s0p50 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000499119 | 0.000531972 | 0 | 0 | 0.000499119 | 0.000564702 | 0.0228071 | False | False | False | False | 0.000889854 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p50.csv |
| bridge_blend_m0p25_s1p25 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.0006131 | 0.000651755 | 0 | 0 | 0.000522528 | 0.000651755 | 0.0264979 | False | False | False | False | 0.0010373 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s1p25.csv |
| bridge_blend_m0p50_s0p75 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000592906 | 0.000637238 | 0 | 0 | 0.000592906 | 0.000637238 | 0.0265362 | False | False | False | False | 0.00104867 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p75.csv |
| bridge_blend_m0p75_s0p50 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.00061426 | 0.00066995 | 0 | 0 | 0.00061426 | 0.000687632 | 0.0278513 | False | False | False | False | 0.0010933 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p50.csv |
| bridge_blend_m0p25_s1p00 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000705138 | 0.000749203 | 0 | 0 | 0.000658914 | 0.000749203 | 0.0302732 | False | False | False | False | 0.0012219 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s1p00.csv |
| blend_m0p50_s0p50 | raw-structure bridge | E51_candidate_table | 5 | 0 | 0.000749279 | 0.000814373 | 0 | 0 | 0.000749279 | 0.000817007 | 0.0328955 | False | False | False | False | 0.00132817 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv |
| targetabl_q3stage | inverse_feasibility_candidate | E26_candidate_list | 5 | 0 | 0.000770343 | 0.000913767 | 0 | 0 | 0.000716152 | 0.000913767 | 0.0207841 | False | False | False | False | 0.00135686 | analysis_outputs/submission_targetabl_b19056bb.csv |
| targetabl_q3s234 | inverse_feasibility_candidate | E26_candidate_list | 5 | 0 | 0.000726885 | 0.00112977 | 0 | 0 | 0.000726885 | 0.00112977 | 0.0201591 | False | False | False | False | 0.00137277 | analysis_outputs/submission_targetabl_1049b8e7.csv |
| bridge_blend_m0p25_s0p75 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000800529 | 0.000853701 | 0 | 0 | 0.000800529 | 0.000853701 | 0.0341026 | False | False | False | False | 0.00141422 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p75.csv |
| bridge_mixmin_s0p25 | raw_structure_bridge_variant | E37_bridge_grid | 5 | 0 | 0.000803239 | 0.000852518 | 0 | 0 | 0.000803239 | 0.000901614 | 0.0342107 | False | False | False | False | 0.00143026 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p25.csv |
| blend_m0p25_s0p50 | raw-structure bridge | E51_candidate_table | 5 | 0 | 0.000894259 | 0.000965245 | 0 | 0 | 0.000894259 | 0.000965245 | 0.0379398 | False | False | False | False | 0.0015827 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv |

## Decision

- candidates scored: `158`.
- strict better-than-mixmin gates: `0`.
- loose better-than-mixmin gates: `0`.
- near-tie-with-mixmin gates: `1`.
- No candidate is one-sided better. Best surviving pattern is a near-tie, led by `analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv`. This supports mixmin as a local frontier under the current binary-world family.

## Outputs

- `analysis_outputs/post_mixmin_binary_world_sign_stress_worlds.csv`
- `analysis_outputs/post_mixmin_binary_world_sign_stress_bands.csv`
- `analysis_outputs/post_mixmin_binary_world_sign_stress_scores.csv`
- `analysis_outputs/post_mixmin_binary_world_sign_stress_summary.csv`
