# Causal Chain Variant: load

- Output: `artifacts/domain_causal_chain_load_v1.parquet`
- Rows: `700`
- Feature count: `32`

## Patterns

`physical_load`, `mobility_context`, `high_load`, `load_after`

## Feature Summary

| feature | mean | std |
| --- | --- | --- |
| z_cc_high_load_low_opportunity | -0.030416 | 0.843242 |
| z_cc_high_load_low_opportunity_subdev | -0.078806 | 0.811792 |
| z_cc_high_load_low_opportunity_subpct | 0.507143 | 0.288853 |
| z_cc_high_load_low_opportunity_subrz | -0.078806 | 0.811792 |
| z_cc_load_after_bad_sleep | 0.018229 | 0.288622 |
| z_cc_load_after_bad_sleep_subdev | 0.003529 | 0.284272 |
| z_cc_load_after_bad_sleep_subpct | 0.507143 | 0.286422 |
| z_cc_load_after_bad_sleep_subrz | 0.003529 | 0.284272 |
| z_cc_mobility_context_switch | 0.065230 | 0.372542 |
| z_cc_mobility_context_switch_past14_delta | -0.015470 | 0.325101 |
| z_cc_mobility_context_switch_past14_volatility_gap | 0.187116 | 0.159078 |
| z_cc_mobility_context_switch_past28_delta | -0.029418 | 0.320583 |
| z_cc_mobility_context_switch_past28_volatility_gap | 0.186056 | 0.155466 |
| z_cc_mobility_context_switch_past3_delta | -0.007067 | 0.354329 |
| z_cc_mobility_context_switch_past3_volatility_gap | 0.214968 | 0.181020 |
| z_cc_mobility_context_switch_past7_delta | -0.010075 | 0.325171 |
| z_cc_mobility_context_switch_past7_volatility_gap | 0.188804 | 0.161962 |
| z_cc_mobility_context_switch_subdev | 0.025492 | 0.317920 |
| z_cc_mobility_context_switch_subpct | 0.507143 | 0.288853 |
| z_cc_mobility_context_switch_subrz | 0.025492 | 0.317920 |
| z_cc_physical_load | 0.048524 | 0.669893 |
| z_cc_physical_load_past14_delta | -0.045267 | 0.637719 |
| z_cc_physical_load_past14_volatility_gap | 0.307530 | 0.270294 |
| z_cc_physical_load_past28_delta | -0.075603 | 0.624570 |
| z_cc_physical_load_past28_volatility_gap | 0.298587 | 0.270499 |
| z_cc_physical_load_past3_delta | -0.015930 | 0.711002 |
| z_cc_physical_load_past3_volatility_gap | 0.369599 | 0.312802 |
| z_cc_physical_load_past7_delta | -0.024824 | 0.642335 |
| z_cc_physical_load_past7_volatility_gap | 0.311764 | 0.271267 |
| z_cc_physical_load_subdev | -0.044713 | 0.621634 |
| z_cc_physical_load_subpct | 0.507143 | 0.288853 |
| z_cc_physical_load_subrz | -0.044713 | 0.621634 |