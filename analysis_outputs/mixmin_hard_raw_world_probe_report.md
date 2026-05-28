# E56 Mixmin-Hard Raw-World Probe

## Observe

E52 filtered old binary worlds by mixmin after the fact. E54 showed raw overnight context is a real strict block-state latent, and E55 showed target-rate projection cannot translate it into mixmin alignment.

## Wonder

If mixmin is made an observed public constraint during world generation, does the raw overnight block-state prior become useful as a feasibility energy and produce a stable movement beyond mixmin?

## Hypothesis

H56: mixmin-hard binary worlds with raw block-state energy should either produce a coherent posterior movement that beats mixmin under world-LOO stress, or prove that raw context is only a private-risk/feasibility diagnostic rather than a candidate generator.

## Method

- Known public anchors in the MILP, including mixmin: `9`.
- Slack cap resolution: raw05-a2c8 public gap `0.0000869862`; tight mixmin scenario uses `0.5x` this gap.
- Raw prior: E54 `night_phone_rawctx_strict_k8_a24` hidden block rates mapped to all 250 submission rows.
- World generation scenarios: raw CE objective only, loose raw block-count constraints, and tighter mixmin slack.
- Candidate checks: existing files are only sensors; new posterior candidates are evaluated by leave-one-world stress before any submission file is kept.

## World Summary

| scenario | objective | world_id | max_abs_residual | mixmin_abs_residual | raw_ce_energy | raw_block_count_mae | elapsed_sec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mixhard_gap_rawobj | slack_only | 07e0c0e4e4c8 | 8.48292e-05 | 4.61424e-05 | 0.616349 | 1.07311 | 4.02555 |
| mixhard_gap_rawobj | raw_ce_a0.004 | 54d54d06da16 | 8.00228e-05 | 7.95457e-05 | 0.533193 | 1.70847 | 4.01837 |
| mixhard_gap_rawobj | raw_ce_a0.01 | 3950a489c057 | 4.99251e-05 | 2.86592e-05 | 0.533099 | 1.73154 | 4.01465 |
| mixhard_gap_rawobj | raw_ce_a0.024 | 1af50dae4523 | 7.25697e-05 | 7.0079e-06 | 0.533001 | 1.72949 | 4.01311 |
| mixhard_gap_rawobj | raw_ce_target_Q1 | 18fb288ad486 | 7.99843e-05 | 6.84339e-05 | 0.617519 | 1.32482 | 4.01234 |
| mixhard_gap_rawobj | raw_ce_target_Q2 | 1ecd0b900dfb | 5.37712e-05 | 4.9971e-05 | 0.613311 | 1.25958 | 4.0259 |
| mixhard_gap_rawobj | raw_ce_target_Q3 | 3608dd9f8d71 | 7.22488e-05 | 6.89679e-05 | 0.61663 | 1.19508 | 4.04124 |
| mixhard_gap_rawobj | raw_ce_target_S1 | f15358a58ce1 | 6.6839e-05 | 8.00947e-06 | 0.610227 | 1.20071 | 4.01906 |
| mixhard_gap_rawobj | raw_ce_target_S2 | 9815e1f3e3ef | 6.52915e-05 | 6.52915e-05 | 0.611775 | 1.20831 | 4.02702 |
| mixhard_gap_rawobj | raw_ce_target_S3 | b0edad627ef3 | 4.74696e-05 | 8.14018e-06 | 0.608252 | 1.26296 | 4.00829 |
| mixhard_gap_rawobj | raw_ce_target_S4 | b854e74aebde | 6.44502e-05 | 4.92797e-05 | 0.616279 | 1.18885 | 4.04419 |
| mixhard_gap_rawobj | raw_random_00 | 68125a4c8897 | 6.0694e-05 | 6.23894e-06 | 0.570926 | 0.959233 | 4.01377 |
| mixhard_gap_rawobj | raw_random_01 | 3f025b594135 | 7.99392e-05 | 4.28609e-05 | 0.578508 | 0.845496 | 4.0116 |
| mixhard_gap_rawobj | raw_random_02 | 8d9c3d275c3a | 7.8829e-05 | 7.8829e-05 | 0.567393 | 1.04522 | 4.01102 |
| mixhard_gap_rawobj | raw_random_03 | 30eb56558a6c | 8.37008e-05 | 6.1483e-05 | 0.56032 | 0.933177 | 4.01354 |
| mixhard_gap_rawcount_loose | slack_only | 961adf01730f | 7.04337e-05 | 1.57955e-06 | 0.60893 | 1.04489 | 4.02178 |
| mixhard_gap_rawcount_loose | raw_ce_a0.004 | ccf200fbcc70 | 6.19209e-05 | 3.60199e-05 | 0.53454 | 1.69182 | 4.0154 |
| mixhard_gap_rawcount_loose | raw_ce_a0.01 | 3ec8b98636d3 | 7.04524e-05 | 3.08642e-05 | 0.535177 | 1.71167 | 4.01359 |
| mixhard_gap_rawcount_loose | raw_ce_a0.024 | 3ec8b98636d3 | 7.04524e-05 | 3.08642e-05 | 0.535177 | 1.71167 | 4.01588 |
| mixhard_gap_rawcount_loose | raw_ce_target_Q1 | a4975c1b9ef3 | 6.98822e-05 | 1.80372e-05 | 0.614609 | 1.24049 | 4.05729 |

## Existing Candidate Sensor Signs

| name | role | raw_energy_quarter__better_rate | raw_energy_quarter__median_delta | raw_energy_quarter__p90_delta | low_slack_half__better_rate | strict_gate | score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bridge_mixmin_s1p00 | raw_structure_bridge_variant | 0 | 0 | 0 | 0.0909091 | False | 0 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s1p00.csv |
| bridge_blend_m0p75_s1p25 | raw_structure_bridge_variant | 0 | 1.18925e-05 | 3.55301e-05 | 0.227273 | False | 2.49936e-05 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv |
| direns_c4af | direns_c4af | 0 | 0.000107908 | 0.000158726 | 0.227273 | False | 0.000163923 | analysis_outputs/submission_direns_c4af1fd8.csv |
| bridge_blend_m0p75_s1p00 | raw_structure_bridge_variant | 0 | 0.000195613 | 0.000212266 | 0 | False | 0.000342837 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s1p00.csv |
| targetabl_q3s234 | targetabl_q3s234 | 0 | 0.000114343 | 0.00034836 | 0 | False | 0.000405798 | analysis_outputs/submission_targetabl_1049b8e7.csv |
| bridge_mixmin_s0p75 | raw_structure_bridge_variant | 0 | 0.000241278 | 0.000246557 | 0 | False | 0.000417368 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p75.csv |
| bridge_blend_m0p50_s1p25 | raw_structure_bridge_variant | 0 | 0.000276971 | 0.000301951 | 0 | False | 0.000479136 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p25.csv |
| bridge_blend_m0p75_s0p75 | raw_structure_bridge_variant | 0 | 0.000404319 | 0.000425235 | 0 | False | 0.000703434 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p75.csv |
| bridge_blend_m0p50_s1p00 | raw_structure_bridge_variant | 0 | 0.000416956 | 0.000450261 | 0 | False | 0.000730701 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s1p00.csv |
| bridge_mixmin_s0p50 | raw_structure_bridge_variant | 0 | 0.000518914 | 0.000529472 | 0 | False | 0.000898363 | analysis_outputs/bridge_scan_candidates/submission_bridge_mixmin_s0p50.csv |
| pair_sensor_6b | pair_sensor_6b | 0 | 0.000276047 | 0.000518768 | 0 | False | 0.000899869 | analysis_outputs/submission_label_flow_focused_6b9335b1.csv |
| bridge_blend_m0p25_s1p25 | raw_structure_bridge_variant | 0 | 0.000576722 | 0.00061768 | 0 | False | 0.000999357 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p25_s1p25.csv |
| bridge_blend_m0p50_s0p75 | raw_structure_bridge_variant | 0 | 0.000588141 | 0.0006184 | 0 | False | 0.00102377 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p50_s0p75.csv |
| pair_sensor_1bb | pair_sensor_1bb | 0 | 0.000406692 | 0.000634307 | 0 | False | 0.00105148 | analysis_outputs/submission_label_flow_focused_1bbfb735.csv |
| bridge_blend_m0p75_s0p50 | raw_structure_bridge_variant | 0 | 0.000640907 | 0.000661587 | 0 | False | 0.0011113 | analysis_outputs/bridge_scan_candidates/submission_bridge_blend_m0p75_s0p50.csv |

## Posterior World-LOO

| candidate | held_worlds | better_rate | median_delta | p90_delta | max_delta | strict_gate |
| --- | --- | --- | --- | --- | --- | --- |
| posterior_raw_energy_quarter_w0.28 | 11 | 1 | -0.154291 | -0.0698873 | -0.0691034 | True |
| posterior_raw_energy_quarter_w0.18 | 11 | 1 | -0.103658 | -0.0498739 | -0.0493764 | True |
| posterior_raw_energy_quarter_w0.10 | 11 | 1 | -0.0595652 | -0.0298921 | -0.0296183 | True |
| posterior_raw_energy_half_w0.28 | 22 | 0.954545 | -0.0506513 | -0.0390048 | 0.00145096 | True |
| posterior_raw_energy_half_w0.18 | 22 | 1 | -0.0347101 | -0.0272515 | -0.00137945 | True |
| posterior_raw_energy_quarter_w0.05 | 11 | 1 | -0.0303963 | -0.0156232 | -0.015487 | True |
| posterior_all_w0.28 | 45 | 1 | -0.0229634 | -0.0179805 | -0.00733651 | True |
| posterior_raw_energy_half_w0.10 | 22 | 1 | -0.0202348 | -0.0161036 | -0.00179064 | True |
| posterior_all_w0.18 | 45 | 1 | -0.0157166 | -0.012516 | -0.00569042 | True |
| posterior_raw_energy_half_w0.05 | 22 | 1 | -0.0104133 | -0.00835158 | -0.00121396 | True |
| posterior_all_w0.10 | 45 | 1 | -0.00915513 | -0.00737802 | -0.00359373 | True |
| posterior_all_w0.05 | 45 | 1 | -0.00470969 | -0.00382143 | -0.00193169 | True |

## Decision

- incumbent worlds: `45`.
- unique incumbent worlds: `44`.
- existing-candidate strict gates: `0`.
- posterior strict gates: `12`.
- A posterior diagnostic submission was written: `analysis_outputs/submission_mixhard_rawposterior_af1502f9.csv`. Treat it as a world-model hypothesis, not a safe public claim.

## Interpretation

If no gate opens, the active worldview remains: mixmin is a real public frontier and raw overnight context is useful as energy/private-risk stress, but not yet a direct candidate generator. If a future public submission from this branch improves, it would mean mixmin-hard binary worlds are closer to the public subset than pseudo-hidden block-rate stress; if it worsens, the binary worlds are still underidentified.

## Outputs

- `analysis_outputs/mixmin_hard_raw_world_probe_worlds.csv`
- `analysis_outputs/mixmin_hard_raw_world_probe_block_constraints.csv`
- `analysis_outputs/mixmin_hard_raw_world_probe_existing_candidate_scores.csv`
- `analysis_outputs/mixmin_hard_raw_world_probe_posterior_cv.csv`
- `analysis_outputs/mixmin_hard_raw_world_probe_posterior_summary.csv`
