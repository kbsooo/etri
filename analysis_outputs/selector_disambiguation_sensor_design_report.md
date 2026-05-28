# Selector Disambiguation Sensor Design

Question: after E21 showed an empty two-selector intersection, which public sensor would most efficiently decide whether the pairwise S4/Q3 world or old hidden-subset Q3/raw05-drift world is miscalibrated?

## Known Anchor Reliability

- A2C8 public: `0.5774393210`.
- Raw05 public: `0.5775263072`.
- Actual A2C8 minus Raw05: `-0.000086986`; A2C8 is better by `0.000086986`.

| selector | models | pass_models | pass_rate | median_loo_mae | best_loo_mae | median_l2o_mae | best_l2o_mae | median_rank_accuracy | raw05_direction_correct_rate | raw05_margin_definition | median_raw05_direction_margin | actual_a2_minus_raw | read |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pairwise_public_order | 36 | 33 | 0.916667 | 0.000850208 | 0.000218288 | 0.00134624 | 0.000444369 | 1 | 0.916667 | pred_a2c8_minus_raw05; correct if margin < 0 | -5.37522e-05 | -8.69862e-05 | matches known a2c8<raw05 direction in most models; still not precise enough for tiny submit claims |
| old_hidden_subset | 7 | 0 | 0 | 0.000553668 | 0.000536411 | 0.000646435 | 0.000565765 | 0.785714 | 0 | pred_raw05_minus_a2c8; correct if margin > 0 | -6.83315e-05 | -8.69862e-05 | over-endorses raw05/stage2-like hidden subset geometry; useful veto but not a submit selector |

## Sensor Candidates

| role | source_path | support_source | support_zone | dominant_target | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | q3s4_move_share | pair_submit_gate | pair_probe_gate | rationale | expected_information | recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_selector_high_contrast_sensor | analysis_outputs/submission_label_flow_focused_6b9335b1.csv | focused_label_flow_review | pair_only | S4 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | 1 | True | True | maximum contrast for S4/Q3 pairwise-public hypothesis; not an improvement claim because old support is weak | If public improves, pairwise S4/Q3 latent world is real and old selector is miscalibrated for this movement. If public worsens, pairwise-focused S4/Q3 is overfit. | diagnostic submit only; conservative sensor should go before high-contrast unless public slots are plentiful |
| pair_selector_conservative_sensor | analysis_outputs/submission_label_flow_focused_1bbfb735.csv | focused_label_flow_review | pair_only | S4 | -5.43159e-05 | 0.967568 | 0.000638679 | 0.277992 | 0.0206675 | 0.0060476 | 1 | True | True | least-bad old-selector p90 among pair-submit files; preferred if spending one diagnostic public slot | If public improves, pairwise S4/Q3 latent world is real and old selector is miscalibrated for this movement. If public worsens, pairwise-focused S4/Q3 is overfit. | best single diagnostic if user wants to resolve selector conflict |
| raw05_blockcount_probe_sensor | analysis_outputs/submission_raw05_jepa_blockcountreg_995c5b77.csv | block_measurement_rescore | pair_probe_not_majority | S4 | 1.07928e-05 | 0.672973 | 0.000574658 | 0.359073 | 0.0314518 | 0.00170904 | 0.632491 | False | True | low-risk raw05-compatible blockcount probe; expected not to beat a2c8, useful only for raw05 tangent calibration | If public unexpectedly improves, raw05/blockcount tangent has unmodeled public signal. If public worsens or is flat, current raw05-probe branch remains closed. | hold |
| old_selector_redundant_sensor | analysis_outputs/submission_public_repair_rawaxis_s1.000_bdba2431.csv | broad_pairwise_universe | old_only | Q3 | 0.000135356 | 0.145946 | 0.000539282 | 0.787645 | 0.02479 | 0.00853087 | 0.398687 | False | False | old-only hypothesis is largely already tested by raw05 being public-worse than a2c8; do not prioritize | Redundant with known raw05 LB; only useful if deliberately retesting old hidden-subset world. | hold |

## Decision

- The old hidden-subset selector already failed the key known direction: it endorses raw05-like geometry even though raw05 is public-worse than a2c8.
- The pairwise selector is still too noisy for a confident improvement claim, but it is the more faithful known-anchor order sensor.
- Therefore a public slot, if used, should test the pair-only S4/Q3 hypothesis rather than an old-only candidate.
- This is diagnostic, not an expected path to 0.54. A good result would reopen S4/Q3 and retire or downweight the old selector for that movement; a bad result would close focused S4/Q3 amplification.

## Files

- `selector_disambiguation_reliability.csv`
- `selector_disambiguation_sensor_candidates.csv`
