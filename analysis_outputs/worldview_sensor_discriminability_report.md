# E38 Worldview Sensor Discriminability Audit

## Observe

E37 showed raw and anchor support can coexist, but selector veto remains. The next question is which candidate is the most informative public sensor, not which one is safe.

## Wonder

Which candidate best separates the plausible hidden-public worldviews: anchor-loss binary worlds, raw observed structure, pairwise public-order selector, old hidden-subset selector, and local honest-CV/combo evidence?

## Hypothesis

H37: if no normal submit candidate exists, the next public slot should be allocated to the candidate with the highest predeclared worldview discriminability: large enough expected sign conflict, clear interpretation if LB improves/worsens, and no claim of safety.

## Method

- Compile E32/E33 anchor-loss bands, E35 independent-evidence audit, E36 raw-structure pseudo-label stress, and E37 bridge scale scan.
- Convert each source into a robust verdict: raw, anchor, pairwise selector, old selector, and honest CV when available.
- Rank by sign entropy and conflict span relative to the known raw05/A2C8 public gap. This is a sensor ranking, not an improvement ranking.

## Result

- candidates audited: `10`.
- normal submit candidates: `0`.
- public sensor candidates: `10`.
- top information sensor: `mixmin_0c916` (`top_anchor_worldview_sensor`), score `3.355110`.

## Lane Summary

| lane | n | normal_submit_candidates | public_sensor_candidates | best_role | best_file | best_recommendation | best_information_score | best_conflict_span | best_conflict_span_vs_raw05_gap | best_question |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw-structure bridge | 6 | 0 | 6 | inverse7blend_1040 | analysis_outputs/submission_inverse7blend_1040423d.csv | raw_anchor_vs_selector_sensor | 3.2356 | 0.00132302 | 15.2095 | Does raw observed structure plus anchor-loss support beat selector veto? |
| S4/Q3 selector disambiguation | 3 | 0 | 3 | pair_sensor_6b | analysis_outputs/submission_label_flow_focused_6b9335b1.csv | pair_vs_anchor_sensor | 3.08429 | 0.0029572 | 33.9961 | Does higher-amplitude pairwise S4/Q3 movement beat old/anchor veto? |
| anchor-loss worldview | 1 | 0 | 1 | mixmin_0c916 | analysis_outputs/submission_mixmin_0c916bb4.csv | top_anchor_worldview_sensor | 3.35511 | 0.0017379 | 19.979 | Does binary/actual-anchor/anchor-loss geometry beat pair/old selector veto? |

## Top Sensor Table

| role | lane | raw_verdict | anchor_verdict | pair_verdict | old_verdict | honest_cv_verdict | conflict_span_vs_raw05_gap | public_sensor_gate | normal_submit_gate | sensor_information_score | recommendation | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | anchor-loss worldview | worse | better | worse | worse | better | 19.979 | True | False | 3.35511 | top_anchor_worldview_sensor | analysis_outputs/submission_mixmin_0c916bb4.csv |
| inverse7blend_1040 | raw-structure bridge | better | better | worse | worse | missing | 15.2095 | True | False | 3.2356 | raw_anchor_vs_selector_sensor | analysis_outputs/submission_inverse7blend_1040423d.csv |
| inv7_s1p00 | raw-structure bridge | better | better | worse | worse | missing | 15.2095 | True | False | 3.2356 | raw_anchor_vs_selector_sensor | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s1p00.csv |
| pair_sensor_6b | S4/Q3 selector disambiguation | worse | worse | better | worse | missing | 33.9961 | True | False | 3.08429 | pair_vs_anchor_sensor | analysis_outputs/submission_label_flow_focused_6b9335b1.csv |
| inv7_s0p50 | raw-structure bridge | better | better | worse | worse | missing | 11.1207 | True | False | 2.94491 | raw_anchor_vs_selector_sensor | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p50.csv |
| pair_sensor_1bb | S4/Q3 selector disambiguation | worse | worse | better | worse | missing | 28.4342 | True | False | 2.94387 | pair_vs_anchor_sensor | analysis_outputs/submission_label_flow_focused_1bbfb735.csv |
| blend_m0p25_s0p50 | raw-structure bridge | better | better | worse | worse | missing | 10.6935 | True | False | 2.90903 | raw_anchor_vs_selector_sensor | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv |
| blend_m0p50_s0p50 | raw-structure bridge | better | better | worse | worse | missing | 10.2373 | True | False | 2.86924 | raw_anchor_vs_selector_sensor | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p50.csv |
| inv7_s0p25 | raw-structure bridge | better | better | worse | worse | missing | 8.84627 | True | False | 2.78709 | raw_anchor_vs_selector_sensor | analysis_outputs/bridge_scan_candidates/submission_bridge_inv7_s0p25.csv |
| pair_sensor_1bb_s0p65 | S4/Q3 selector disambiguation | worse | worse | better | worse | missing | 18.4822 | True | False | 2.60909 | pair_vs_anchor_sensor | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv |

## Key Metrics

| role | raw_mean_delta | raw_worst_delta | anchor_low_half_max_delta | pair_p90_delta | old_p90_delta | bad_axis_abs_load | mean_abs_move_vs_a2c8 | expected_lb_anchor_low_half_max | expected_lb_pair_p90 | expected_lb_old_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | 6.51068e-05 | 0.000498574 | -0.000537096 | 0.0008792 | 0.00104193 | 0.213626 | 0.0456142 | 0.576902 | 0.578319 | 0.578481 |
| inverse7blend_1040 | -0.000705727 | -0.000507826 | -2.46186e-05 | 0.000122038 | 0.000617292 | 0.0524804 | 0.0124131 | 0.577415 | 0.577561 | 0.578057 |
| inv7_s1p00 | -0.000705727 | -0.000507826 | -2.46186e-05 | 0.000122038 | 0.000617292 | 0.0524804 | 0.0124131 | 0.577415 | 0.577561 | 0.578057 |
| pair_sensor_6b | -0.000139452 | 0.00060343 | 0.00281774 | -6.52173e-05 | 0.000675515 | 0.0172468 | 0.0072335 | 0.580257 | 0.577374 | 0.578115 |
| inv7_s0p50 | -0.000360277 | -0.000261326 | -1.97224e-05 | 6.43721e-05 | 0.000607068 | 0.0431968 | 0.00620653 | 0.57742 | 0.577504 | 0.578046 |
| pair_sensor_1bb | -0.000140493 | 0.000474121 | 0.00233289 | -5.43159e-05 | 0.000638679 | 0.0206675 | 0.0060476 | 0.579772 | 0.577385 | 0.578078 |
| blend_m0p25_s0p50 | -0.000289936 | -0.000168217 | -0.000111161 | 0.000116208 | 0.000640247 | 0.0602971 | 0.00931369 | 0.577328 | 0.577556 | 0.57808 |
| blend_m0p50_s0p50 | -0.000213141 | -6.86529e-05 | -0.000196145 | 0.00021843 | 0.000677366 | 0.0791922 | 0.0137518 | 0.577243 | 0.577658 | 0.578117 |
| inv7_s0p25 | -0.000181991 | -0.000132515 | -1.17136e-05 | 3.54231e-05 | 0.000587512 | 0.0400513 | 0.00310326 | 0.577428 | 0.577475 | 0.578027 |
| pair_sensor_1bb_s0p65 | -0.000122815 | 0.000276683 | 0.00148488 | -3.4496e-05 | 0.000571958 | 0.0263509 | 0.00393094 | 0.578924 | 0.577405 | 0.578011 |

## Decision

No candidate is promoted to normal improvement submission. `mixmin_0c916` remains the top high-risk anchor-loss worldview sensor because it creates the clearest disagreement between anchor-loss/honest-CV support and pair/old/raw veto. `inv7_s0p25` is a cleaner raw+anchor bridge sensor, but its negative expected edge is less readable and the selector veto remains. `pair_sensor_1bb` remains the lower-risk S4/Q3 selector-disambiguation sensor.

## Outputs

- `analysis_outputs/worldview_sensor_discriminability_audit.csv`
- `analysis_outputs/worldview_sensor_discriminability_by_lane.csv`
