# Causal Chain Variant: continuity

- Output: `artifacts/domain_causal_chain_continuity_v1.parquet`
- Rows: `700`
- Feature count: `40`

## Patterns

`sleep_friction`, `continuity`, `fragmented`, `sleep_quality`

## Feature Summary

| feature | mean | std |
| --- | --- | --- |
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
| z_cc_fragmented_recovery_gap | -0.069074 | 0.606598 |
| z_cc_fragmented_recovery_gap_subdev | -0.017546 | 0.577562 |
| z_cc_fragmented_recovery_gap_subpct | 0.507143 | 0.288853 |
| z_cc_fragmented_recovery_gap_subrz | -0.017546 | 0.577562 |
| z_cc_sleep_friction | 0.272801 | 0.338839 |
| z_cc_sleep_friction_past14_delta | -0.005122 | 0.333530 |
| z_cc_sleep_friction_past14_volatility_gap | 0.188366 | 0.169717 |
| z_cc_sleep_friction_past28_delta | -0.008490 | 0.328035 |
| z_cc_sleep_friction_past28_volatility_gap | 0.184905 | 0.167240 |
| z_cc_sleep_friction_past3_delta | -0.005118 | 0.359487 |
| z_cc_sleep_friction_past3_volatility_gap | 0.211714 | 0.192321 |
| z_cc_sleep_friction_past7_delta | -0.005415 | 0.341528 |
| z_cc_sleep_friction_past7_volatility_gap | 0.195709 | 0.175188 |
| z_cc_sleep_friction_subdev | 0.039589 | 0.323615 |
| z_cc_sleep_friction_subpct | 0.507143 | 0.288853 |
| z_cc_sleep_friction_subrz | 0.039589 | 0.323615 |
| z_cc_sleep_quality_chain_score | -0.509471 | 0.790364 |
| z_cc_sleep_quality_chain_score_past14_delta | -0.066216 | 0.717511 |
| z_cc_sleep_quality_chain_score_past14_volatility_gap | 0.319282 | 0.302805 |
| z_cc_sleep_quality_chain_score_past28_delta | -0.078543 | 0.714920 |
| z_cc_sleep_quality_chain_score_past28_volatility_gap | 0.308972 | 0.295866 |
| z_cc_sleep_quality_chain_score_past3_delta | -0.020934 | 0.762932 |
| z_cc_sleep_quality_chain_score_past3_volatility_gap | 0.375310 | 0.348880 |
| z_cc_sleep_quality_chain_score_past7_delta | -0.044663 | 0.728639 |
| z_cc_sleep_quality_chain_score_past7_volatility_gap | 0.334703 | 0.312315 |
| z_cc_sleep_quality_chain_score_subdev | -0.007702 | 0.741971 |
| z_cc_sleep_quality_chain_score_subpct | 0.507143 | 0.288853 |
| z_cc_sleep_quality_chain_score_subrz | -0.007702 | 0.741971 |