# Causal Chain Latents

## Purpose

Encode a subject-day as a causal sketch: physical/mobility load, evening arousal, sleep opportunity, continuity loss, and morning recovery.

- Output: `artifacts/domain_causal_chain_v1.parquet`
- Rows: `700`
- Feature count: `168`

## Feature Summary

| feature | mean | std |
| --- | --- | --- |
| z_cc_arousal_to_opportunity_gap | 0.100537 | 0.610113 |
| z_cc_arousal_to_opportunity_gap_subdev | -0.004477 | 0.597175 |
| z_cc_arousal_to_opportunity_gap_subpct | 0.507143 | 0.288853 |
| z_cc_arousal_to_opportunity_gap_subrz | -0.004477 | 0.597175 |
| z_cc_arousal_without_load | -0.096063 | 0.496060 |
| z_cc_arousal_without_load_subdev | -0.037861 | 0.473847 |
| z_cc_arousal_without_load_subpct | 0.507143 | 0.288853 |
| z_cc_arousal_without_load_subrz | -0.037861 | 0.473847 |
| z_cc_continuity_loss | 0.212425 | 0.379857 |
| z_cc_continuity_loss_past14_delta | 0.001956 | 0.353902 |
| z_cc_continuity_loss_past14_volatility_gap | 0.209841 | 0.166048 |
| z_cc_continuity_loss_past28_delta | -0.003683 | 0.350143 |
| z_cc_continuity_loss_past28_volatility_gap | 0.207369 | 0.165713 |
| z_cc_continuity_loss_past3_delta | 0.000492 | 0.386865 |
| z_cc_continuity_loss_past3_volatility_gap | 0.240917 | 0.182010 |
| z_cc_continuity_loss_past7_delta | 0.001814 | 0.365703 |
| z_cc_continuity_loss_past7_volatility_gap | 0.219616 | 0.170155 |
| z_cc_continuity_loss_subdev | 0.029827 | 0.342427 |
| z_cc_continuity_loss_subpct | 0.507143 | 0.288844 |
| z_cc_continuity_loss_subrz | 0.029827 | 0.342427 |
| z_cc_evening_arousal | 0.179478 | 0.317382 |
| z_cc_evening_arousal_past14_delta | -0.010432 | 0.314006 |
| z_cc_evening_arousal_past14_volatility_gap | 0.172323 | 0.164902 |
| z_cc_evening_arousal_past28_delta | -0.013062 | 0.309137 |
| z_cc_evening_arousal_past28_volatility_gap | 0.168879 | 0.162397 |
| z_cc_evening_arousal_past3_delta | -0.006777 | 0.342763 |
| z_cc_evening_arousal_past3_volatility_gap | 0.194490 | 0.190545 |
| z_cc_evening_arousal_past7_delta | -0.010328 | 0.320906 |
| z_cc_evening_arousal_past7_volatility_gap | 0.177358 | 0.166975 |
| z_cc_evening_arousal_subdev | 0.069389 | 0.308793 |
| z_cc_evening_arousal_subpct | 0.507143 | 0.288853 |
| z_cc_evening_arousal_subrz | 0.069389 | 0.308793 |
| z_cc_fatigue_chain_score | 0.044680 | 0.980732 |
| z_cc_fatigue_chain_score_past14_delta | -0.028321 | 0.933871 |
| z_cc_fatigue_chain_score_past14_volatility_gap | 0.388492 | 0.338391 |
| z_cc_fatigue_chain_score_past28_delta | -0.072714 | 0.914349 |
| z_cc_fatigue_chain_score_past28_volatility_gap | 0.374813 | 0.329704 |
| z_cc_fatigue_chain_score_past3_delta | -0.009709 | 1.013417 |
| z_cc_fatigue_chain_score_past3_volatility_gap | 0.478492 | 0.409741 |
| z_cc_fatigue_chain_score_past7_delta | -0.011239 | 0.929278 |
| z_cc_fatigue_chain_score_past7_volatility_gap | 0.400595 | 0.342639 |
| z_cc_fatigue_chain_score_subdev | -0.028058 | 0.907787 |
| z_cc_fatigue_chain_score_subpct | 0.507143 | 0.288853 |
| z_cc_fatigue_chain_score_subrz | -0.028196 | 0.857228 |
| z_cc_fragmented_recovery_gap | -0.069074 | 0.606598 |
| z_cc_fragmented_recovery_gap_subdev | -0.017546 | 0.577562 |
| z_cc_fragmented_recovery_gap_subpct | 0.507143 | 0.288853 |
| z_cc_fragmented_recovery_gap_subrz | -0.017546 | 0.577562 |
| z_cc_high_load_low_opportunity | -0.030416 | 0.843242 |
| z_cc_high_load_low_opportunity_subdev | -0.078806 | 0.811792 |
| z_cc_high_load_low_opportunity_subpct | 0.507143 | 0.288853 |
| z_cc_high_load_low_opportunity_subrz | -0.078806 | 0.811792 |
| z_cc_late_arousal_chain | 2.230383 | 2.395869 |
| z_cc_late_arousal_chain_subdev | 0.588279 | 2.348225 |
| z_cc_late_arousal_chain_subpct | 0.507143 | 0.288853 |
| z_cc_late_arousal_chain_subrz | 0.215737 | 0.884825 |
| z_cc_load_after_bad_sleep | 0.018229 | 0.288622 |
| z_cc_load_after_bad_sleep_subdev | 0.003529 | 0.284272 |
| z_cc_load_after_bad_sleep_subpct | 0.507143 | 0.286422 |
| z_cc_load_after_bad_sleep_subrz | 0.003529 | 0.284272 |