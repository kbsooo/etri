# Nested Temporal-Deviation Selection Sweep

## Result

| selector | min_train_delta | base_avg | nested_selected_avg | delta_vs_base | dir |
| --- | --- | --- | --- | --- | --- |
| broad | 0.000000 | 0.623192 | 0.623061 | -0.000131 | domain_temporal_deviation_nested_selection_v1_margin_0 |
| broad | 0.000500 | 0.623192 | 0.622931 | -0.000261 | domain_temporal_deviation_nested_selection_v1_margin_0p0005 |
| broad | 0.001000 | 0.623192 | 0.622676 | -0.000516 | domain_temporal_deviation_nested_selection_v1_margin_0p001 |
| broad | 0.002000 | 0.623192 | 0.622590 | -0.000602 | domain_temporal_deviation_nested_selection_v1_margin_0p002 |
| broad | 0.003000 | 0.623192 | 0.622182 | -0.001010 | domain_temporal_deviation_nested_selection_v1_margin_0p003 |
| broad | 0.005000 | 0.623192 | 0.622449 | -0.000743 | domain_temporal_deviation_nested_selection_v1_margin_0p005 |
| trajectory_only | 0.000000 | 0.623192 | 0.623347 | 0.000156 | domain_temporal_deviation_nested_selection_trajectory_only_margin_0 |
| trajectory_only | 0.001000 | 0.623192 | 0.622601 | -0.000591 | domain_temporal_deviation_nested_selection_trajectory_only_margin_0p001 |
| trajectory_only | 0.002000 | 0.623192 | 0.621928 | -0.001263 | domain_temporal_deviation_nested_selection_trajectory_only_margin_0p002 |
| trajectory_only | 0.003000 | 0.623192 | 0.621507 | -0.001685 | domain_temporal_deviation_nested_selection_trajectory_only_margin_0p003 |
| trajectory_only | 0.005000 | 0.623192 | 0.621907 | -0.001285 | domain_temporal_deviation_nested_selection_trajectory_only_margin_0p005 |

## Read

- Broad family selection confirms some signal but lets unstable future/recovery candidates harm S2.
- Trajectory-only selection with margin `0.003` is the cleanest diagnostic: Q2/Q3 switch in all folds and all other targets remain on base.
- This is still a fold-loss diagnostic, not a submission-ready decoder output.