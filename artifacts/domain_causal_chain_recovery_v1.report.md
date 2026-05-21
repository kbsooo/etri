# Causal Chain Variant: recovery

- Output: `artifacts/domain_causal_chain_recovery_v1.parquet`
- Rows: `700`
- Feature count: `40`

## Patterns

`morning_recovery`, `recovery`, `fatigue`

## Feature Summary

| feature | mean | std |
| --- | --- | --- |
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
| z_cc_morning_recovery | 0.281499 | 0.434752 |
| z_cc_morning_recovery_past14_delta | -0.030460 | 0.429537 |
| z_cc_morning_recovery_past14_volatility_gap | 0.229016 | 0.212782 |
| z_cc_morning_recovery_past28_delta | -0.035990 | 0.424124 |
| z_cc_morning_recovery_past28_volatility_gap | 0.224773 | 0.208469 |
| z_cc_morning_recovery_past3_delta | -0.012796 | 0.463140 |
| z_cc_morning_recovery_past3_volatility_gap | 0.259511 | 0.237837 |
| z_cc_morning_recovery_past7_delta | -0.021846 | 0.439248 |
| z_cc_morning_recovery_past7_volatility_gap | 0.234971 | 0.224417 |
| z_cc_morning_recovery_subdev | 0.058399 | 0.420518 |
| z_cc_morning_recovery_subpct | 0.507143 | 0.288853 |
| z_cc_morning_recovery_subrz | 0.058399 | 0.420518 |
| z_cc_recovery_deficit | 0.039827 | 0.797108 |
| z_cc_recovery_deficit_past14_delta | -0.019929 | 0.779602 |
| z_cc_recovery_deficit_past14_volatility_gap | 0.353130 | 0.308861 |
| z_cc_recovery_deficit_past28_delta | -0.048103 | 0.769952 |
| z_cc_recovery_deficit_past28_volatility_gap | 0.343665 | 0.300370 |
| z_cc_recovery_deficit_past3_delta | -0.008253 | 0.859215 |
| z_cc_recovery_deficit_past3_volatility_gap | 0.430038 | 0.366781 |
| z_cc_recovery_deficit_past7_delta | -0.008393 | 0.786823 |
| z_cc_recovery_deficit_past7_volatility_gap | 0.362816 | 0.317730 |
| z_cc_recovery_deficit_subdev | 0.008273 | 0.765011 |
| z_cc_recovery_deficit_subpct | 0.507143 | 0.288853 |
| z_cc_recovery_deficit_subrz | 0.008273 | 0.765011 |