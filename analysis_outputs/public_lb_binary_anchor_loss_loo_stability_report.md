# Binary Anchor Loss LOO Stability Audit

Question: is E32 driven by one known public anchor, or is the anchor-loss energy stable under leave-one-anchor-out stress?

## Method

- Recompute `anchor_energy` after omitting one known public anchor at a time.
- Re-rank the 29 E30 frontier-box binary worlds by each LOO energy.
- Check candidate signs inside low-energy bands and whether mixmin-adverse worlds enter those bands.

## LOO Band Summary

| band | role | loo_count | worlds_min | worlds_median | worlds_max | better_rate_min | better_rate_median | better_rate_max | max_delta_max | adverse_in_band_max | adverse_min_rank_min | adverse_max_rank_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loo_low_anchor_energy_half | inverse7blend_1040 | 7 | 14 | 14 | 15 | 0.928571 | 1 | 1 | 6.01494e-05 | 0 | 21 | 29 |
| loo_low_anchor_energy_half | mixmin_0c916 | 7 | 14 | 14 | 15 | 1 | 1 | 1 | -0.000315338 | 0 | 21 | 29 |
| loo_low_anchor_energy_half | pair_sensor_1bb | 7 | 14 | 14 | 15 | 0.357143 | 0.428571 | 0.428571 | 0.00233289 | 0 | 21 | 29 |
| loo_low_anchor_energy_half | pair_sensor_1bb_s0p65 | 7 | 14 | 14 | 15 | 0.357143 | 0.428571 | 0.428571 | 0.00148488 | 0 | 21 | 29 |
| loo_low_anchor_energy_half | pair_sensor_6b | 7 | 14 | 14 | 15 | 0.285714 | 0.357143 | 0.357143 | 0.00281774 | 0 | 21 | 29 |
| loo_low_anchor_energy_quarter | inverse7blend_1040 | 7 | 7 | 7 | 7 | 1 | 1 | 1 | -3.52737e-05 | 0 | 21 | 29 |
| loo_low_anchor_energy_quarter | mixmin_0c916 | 7 | 7 | 7 | 7 | 1 | 1 | 1 | -0.000537096 | 0 | 21 | 29 |
| loo_low_anchor_energy_quarter | pair_sensor_1bb | 7 | 7 | 7 | 7 | 0.428571 | 0.571429 | 0.714286 | 0.00185244 | 0 | 21 | 29 |
| loo_low_anchor_energy_quarter | pair_sensor_1bb_s0p65 | 7 | 7 | 7 | 7 | 0.428571 | 0.571429 | 0.714286 | 0.00117259 | 0 | 21 | 29 |
| loo_low_anchor_energy_quarter | pair_sensor_6b | 7 | 7 | 7 | 7 | 0.285714 | 0.428571 | 0.571429 | 0.00224221 | 0 | 21 | 29 |
| loo_low_anchor_energy_random_plus_fit | inverse7blend_1040 | 7 | 11 | 12 | 13 | 0.923077 | 1 | 1 | 6.01494e-05 | 0 | 21 | 29 |
| loo_low_anchor_energy_random_plus_fit | mixmin_0c916 | 7 | 11 | 12 | 13 | 1 | 1 | 1 | -0.000315338 | 0 | 21 | 29 |
| loo_low_anchor_energy_random_plus_fit | pair_sensor_1bb | 7 | 11 | 12 | 13 | 0.454545 | 0.461538 | 0.5 | 0.000490769 | 0 | 21 | 29 |
| loo_low_anchor_energy_random_plus_fit | pair_sensor_1bb_s0p65 | 7 | 11 | 12 | 13 | 0.454545 | 0.461538 | 0.5 | 0.000287504 | 0 | 21 | 29 |
| loo_low_anchor_energy_random_plus_fit | pair_sensor_6b | 7 | 11 | 12 | 13 | 0.363636 | 0.384615 | 0.416667 | 0.000614961 | 0 | 21 | 29 |

## Low-Energy-Half Detail

| omitted_anchor | role | worlds | better_rate | max_delta | adverse_mixmin_worlds_in_band | adverse_mixmin_min_rank | adverse_mixmin_max_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 29 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 27 | 29 |
| submission_jepa_latent_q2_w0p45.csv | inverse7blend_1040 | 15 | 1 | -2.46186e-05 | 0 | 26 | 29 |
| submission_jepa_latent_residual_probe.csv | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 27 | 28 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | inverse7blend_1040 | 14 | 1 | -3.52737e-05 | 0 | 25 | 28 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 21 | 29 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 29 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 29 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 27 | 29 |
| submission_jepa_latent_q2_w0p45.csv | mixmin_0c916 | 15 | 1 | -0.000537096 | 0 | 26 | 29 |
| submission_jepa_latent_residual_probe.csv | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 27 | 28 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 25 | 28 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 21 | 29 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 29 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 27 | 29 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | pair_sensor_1bb | 14 | 0.428571 | 0.00185244 | 0 | 27 | 29 |
| submission_jepa_latent_q2_w0p45.csv | pair_sensor_1bb | 15 | 0.4 | 0.00233289 | 0 | 26 | 29 |
| submission_jepa_latent_residual_probe.csv | pair_sensor_1bb | 14 | 0.428571 | 0.00185244 | 0 | 27 | 28 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | pair_sensor_1bb | 14 | 0.357143 | 0.00233289 | 0 | 25 | 28 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 21 | 29 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | pair_sensor_1bb | 14 | 0.428571 | 0.00185244 | 0 | 27 | 29 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 27 | 29 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | pair_sensor_6b | 14 | 0.357143 | 0.00224221 | 0 | 27 | 29 |
| submission_jepa_latent_q2_w0p45.csv | pair_sensor_6b | 15 | 0.333333 | 0.00281774 | 0 | 26 | 29 |
| submission_jepa_latent_residual_probe.csv | pair_sensor_6b | 14 | 0.357143 | 0.00224221 | 0 | 27 | 28 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | pair_sensor_6b | 14 | 0.285714 | 0.00281774 | 0 | 25 | 28 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 21 | 29 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | pair_sensor_6b | 14 | 0.357143 | 0.00224221 | 0 | 27 | 29 |

## Adverse Mixmin Rank Stability

| omitted_anchor | adverse_in_low_half | adverse_min_rank | adverse_max_rank |
| --- | --- | --- | --- |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0 | 27 | 29 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0 | 27 | 29 |
| submission_jepa_latent_q2_w0p45.csv | 0 | 26 | 29 |
| submission_jepa_latent_residual_probe.csv | 0 | 27 | 28 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0 | 25 | 28 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0 | 21 | 29 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0 | 27 | 29 |

## Decision

- leave-one-anchor runs: `7`.
- Mixmin is negative in every low-energy-half and low-energy-quarter LOO band.
- Inverse7 is nearly as stable, but can lose one low-energy-half world when the final9 anchor is omitted.
- No mixmin-adverse world enters any LOO low-energy-half band.
- E32 is not driven by a single known public anchor, but it remains an anchor-derived diagnostic rather than a certified submission gate.
