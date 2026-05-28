# E71 Unified Q2/S3 Strict-Cell Consensus Probe

## Observe

E70 found strict consensus rows, but all used `gate=none` and heldout-specific cell reconstruction.

## Wonder

Does the E70 consensus survive when each E68 strict cell is rebuilt once with the full combo family?

## Method

- E68 strict rows: `155`.
- Unique strict cells: `104`.
- Cells with support from two heldout families: `51`.
- Candidate rows: `3136`.
- Unique predictions: `2842` plus mixmin reference.
- Pools: `14`; base aggregators: `['mean', 'median']`; delta aggregators: `['mean', 'median', 'weighted_mean', 'signed_p75']`; gates: `['none', 'agree60', 'agree75', 'agree60_top50']`; alphas: `[0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]`.
- Strict unified gate uses the same tail/hidden/world/block requirements as E70.
- Deployable unified gate additionally requires `gate != none`, so it cannot rely on disagreement-permissive consensus.

## Summary

| pool | base_agg | delta_agg | gate | n | pool_size | pool_support_mean | strict_unified_gate | deployable_unified_gate | loose_unified_gate | all_margin_vs_mixmin | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_sets_beating_base | best_sets_tail_neutral | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top75_heldout_mean | mean | signed_p75 | none | 7 | 75 | 1.64 | 1 | 0 | 3 | 1 | -1.0056e-05 | -5.16412e-06 | 7.55949e-06 | 3 | 3 | -0.000477907 | -0.000413602 | 0.833333 |
| translator_tail_soft_p90_m1.00 | mean | signed_p75 | none | 7 | 25 | 1.36 | 0 | 0 | 3 | 1 | -1.06182e-05 | -5.66459e-06 | 8.35176e-06 | 3 | 3 | -0.000470485 | -0.000394856 | 0.833333 |
| translator_tail_soft_p90_m1.00 | median | signed_p75 | none | 7 | 25 | 1.36 | 0 | 0 | 3 | 1 | -1.03266e-05 | -5.7075e-06 | 7.31663e-06 | 3 | 3 | -0.000470485 | -0.000395333 | 0.833333 |
| top75_heldout_mean | median | signed_p75 | none | 7 | 75 | 1.64 | 0 | 0 | 3 | 0 | -9.91713e-06 | -5.24408e-06 | 7.10444e-06 | 3 | 3 | -0.000477907 | -0.00041186 | 0.833333 |
| top50_heldout_mean | mean | signed_p75 | none | 7 | 50 | 1.84 | 0 | 0 | 3 | 0 | -9.89558e-06 | -5.09471e-06 | 7.9649e-06 | 3 | 3 | -0.000461407 | -0.000381535 | 0.833333 |
| support2 | mean | signed_p75 | none | 7 | 51 | 2 | 0 | 0 | 3 | 0 | -9.83981e-06 | -5.09413e-06 | 7.92077e-06 | 3 | 3 | -0.000416911 | -0.00033472 | 0.833333 |
| translator_tail_soft_p90_m0.50 | mean | weighted_mean | none | 7 | 13 | 1.46154 | 0 | 0 | 3 | 0 | -9.83758e-06 | -5.07205e-06 | 1.06241e-05 | 3 | 3 | -0.000412126 | -0.00034734 | 0.833333 |
| support2_top50 | mean | signed_p75 | none | 7 | 50 | 2 | 0 | 0 | 3 | 0 | -9.83187e-06 | -5.08531e-06 | 7.94542e-06 | 3 | 3 | -0.000421927 | -0.000339755 | 0.833333 |
| translator_tail_soft_p90_m1.00 | mean | weighted_mean | none | 7 | 25 | 1.36 | 0 | 0 | 3 | 0 | -9.82336e-06 | -4.86977e-06 | 8.56237e-06 | 3 | 3 | -0.000377484 | -0.000317977 | 0.833333 |
| top50_heldout_mean | median | signed_p75 | none | 7 | 50 | 1.84 | 0 | 0 | 3 | 0 | -9.79762e-06 | -5.13827e-06 | 7.32288e-06 | 3 | 3 | -0.000461407 | -0.000381692 | 0.833333 |
| top75_heldout_mean | mean | weighted_mean | none | 7 | 75 | 1.64 | 0 | 0 | 3 | 0 | -9.64151e-06 | -4.74965e-06 | 7.49313e-06 | 3 | 3 | -0.00034558 | -0.000279524 | 0.833333 |
| all_unique | mean | weighted_mean | none | 7 | 104 | 1.49038 | 0 | 0 | 3 | 0 | -9.58152e-06 | -4.68823e-06 | 7.11935e-06 | 3 | 3 | -0.0003473 | -0.000289152 | 0.833333 |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | agree60_top50 | 7 | 13 | 1.46154 | 0 | 0 | 3 | 0 | -9.49854e-06 | -4.733e-06 | 9.81686e-06 | 3 | 3 | -0.000345799 | -0.000276864 | 0.694444 |
| translator_tail_p90_nonpos_m0.50 | mean | signed_p75 | none | 7 | 12 | 1.41667 | 0 | 0 | 3 | 0 | -8.83059e-06 | -4.10006e-06 | 7.13065e-06 | 3 | 3 | -0.000306025 | -0.000235088 | 0.583333 |
| translator_tail_p90_nonpos_m0.50 | median | signed_p75 | none | 7 | 12 | 1.41667 | 0 | 0 | 3 | 0 | -8.78758e-06 | -3.99023e-06 | 6.49809e-06 | 3 | 3 | -0.000306025 | -0.00023367 | 0.583333 |
| high_hidden | mean | mean | none | 7 | 37 | 1.43243 | 0 | 0 | 3 | 0 | -8.69436e-06 | -3.80786e-06 | 6.34796e-06 | 3 | 3 | -0.000396127 | -0.000345425 | 0.833333 |
| high_hidden | median | mean | none | 7 | 37 | 1.43243 | 0 | 0 | 3 | 0 | -8.63783e-06 | -3.82887e-06 | 5.52756e-06 | 3 | 3 | -0.000396127 | -0.00034467 | 0.833333 |
| high_world | mean | mean | none | 7 | 37 | 1.32432 | 0 | 0 | 3 | 0 | -8.63266e-06 | -3.7108e-06 | 6.29385e-06 | 3 | 3 | -0.000405666 | -0.000358055 | 0.833333 |
| high_world | median | mean | none | 7 | 37 | 1.32432 | 0 | 0 | 3 | 0 | -8.53935e-06 | -3.72991e-06 | 5.72838e-06 | 3 | 3 | -0.000405666 | -0.000357351 | 0.833333 |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | none | 7 | 13 | 1.46154 | 0 | 0 | 2 | 1 | -1.08217e-05 | -6.05613e-06 | 1.04839e-05 | 3 | 3 | -0.000249889 | -0.000196902 | 0.833333 |
| support2 | mean | mean | none | 7 | 51 | 2 | 0 | 0 | 2 | 1 | -1.03117e-05 | -5.56598e-06 | 7.75192e-06 | 3 | 3 | -0.000293808 | -0.000227074 | 0.833333 |
| support2_top50 | mean | mean | none | 7 | 50 | 2 | 0 | 0 | 2 | 1 | -1.02804e-05 | -5.53386e-06 | 7.75722e-06 | 3 | 3 | -0.000296323 | -0.000228885 | 0.833333 |
| top50_heldout_mean | mean | mean | none | 7 | 50 | 1.84 | 0 | 0 | 2 | 1 | -1.02753e-05 | -5.47448e-06 | 7.90408e-06 | 3 | 3 | -0.000316642 | -0.000246627 | 0.833333 |
| translator_tail_soft_p90_m0.50 | median | signed_p75 | none | 7 | 13 | 1.46154 | 0 | 0 | 2 | 1 | -1.02232e-05 | -5.99548e-06 | 1.27075e-05 | 3 | 3 | -0.000249889 | -0.000195667 | 0.833333 |
| support2 | median | mean | none | 7 | 51 | 2 | 0 | 0 | 2 | 1 | -1.02198e-05 | -5.6098e-06 | 7.19849e-06 | 3 | 3 | -0.000293808 | -0.000228763 | 0.833333 |
| top75_heldout_mean | mean | mean | none | 7 | 75 | 1.64 | 0 | 0 | 2 | 1 | -1.02182e-05 | -5.32639e-06 | 7.53827e-06 | 3 | 3 | -0.000313468 | -0.000255608 | 0.833333 |
| high_block | mean | mean | none | 7 | 47 | 1.76596 | 0 | 0 | 2 | 1 | -1.02024e-05 | -5.44397e-06 | 9.42708e-06 | 3 | 3 | -0.000264693 | -0.000209995 | 0.833333 |
| top50_heldout_mean | median | mean | none | 7 | 50 | 1.84 | 0 | 0 | 2 | 1 | -1.01727e-05 | -5.51338e-06 | 7.26198e-06 | 3 | 3 | -0.000316642 | -0.000247207 | 0.833333 |
| support2_top50 | median | mean | none | 7 | 50 | 2 | 0 | 0 | 2 | 1 | -1.017e-05 | -5.57649e-06 | 7.21806e-06 | 3 | 3 | -0.000296323 | -0.000230101 | 0.833333 |
| high_block | mean | weighted_mean | none | 7 | 47 | 1.76596 | 0 | 0 | 2 | 1 | -1.01665e-05 | -5.4081e-06 | 9.40726e-06 | 3 | 3 | -0.000282842 | -0.000223397 | 0.833333 |

## Best Full-Combo Rows

| pool | pool_size | pool_support_mean | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | strict_unified_gate | deployable_unified_gate | loose_unified_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_p90_m0.50 | 13 | 1.46154 | mean | signed_p75 | none | 16 | -1.08217e-05 | -6.05613e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | none | 8 | -1.06182e-05 | -5.66459e-06 | 3 | 1 | -0.000394856 | -0.000470485 | 0.833333 | False | False | True |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | signed_p75 | none | 8 | -1.03266e-05 | -5.7075e-06 | 3 | 1 | -0.000395333 | -0.000470485 | 0.833333 | False | False | True |
| support2 | 51 | 2 | mean | mean | none | 16 | -1.03117e-05 | -5.56598e-06 | 2 | 3 |  |  |  | False | False | False |
| support2_top50 | 50 | 2 | mean | mean | none | 16 | -1.02804e-05 | -5.53386e-06 | 2 | 3 |  |  |  | False | False | False |
| top50_heldout_mean | 50 | 1.84 | mean | mean | none | 16 | -1.02753e-05 | -5.47448e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m0.50 | 13 | 1.46154 | median | signed_p75 | none | 16 | -1.02232e-05 | -5.99548e-06 | 2 | 1 |  |  |  | False | False | False |
| support2 | 51 | 2 | median | mean | none | 16 | -1.02198e-05 | -5.6098e-06 | 2 | 3 |  |  |  | False | False | False |
| top75_heldout_mean | 75 | 1.64 | mean | mean | none | 16 | -1.02182e-05 | -5.32639e-06 | 2 | 3 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | mean | none | 16 | -1.02024e-05 | -5.44397e-06 | 2 | 1 |  |  |  | False | False | False |
| top50_heldout_mean | 50 | 1.84 | median | mean | none | 16 | -1.01727e-05 | -5.51338e-06 | 2 | 1 |  |  |  | False | False | False |
| support2_top50 | 50 | 2 | median | mean | none | 16 | -1.017e-05 | -5.57649e-06 | 2 | 3 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | weighted_mean | none | 16 | -1.01665e-05 | -5.4081e-06 | 2 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | mean | weighted_mean | none | 16 | -1.01195e-05 | -5.36274e-06 | 2 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | mean | mean | none | 16 | -1.00868e-05 | -5.33005e-06 | 2 | 1 |  |  |  | False | False | False |
| top75_heldout_mean | 75 | 1.64 | median | mean | none | 16 | -1.00645e-05 | -5.39143e-06 | 2 | 3 |  |  |  | False | False | False |
| top75_heldout_mean | 75 | 1.64 | mean | signed_p75 | none | 8 | -1.0056e-05 | -5.16412e-06 | 3 | 3 | -0.000413602 | -0.000477907 | 0.833333 | True | False | True |
| high_block | 47 | 1.76596 | median | mean | none | 16 | -1.00096e-05 | -5.44672e-06 | 2 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | signed_p75 | none | 16 | -1.00049e-05 | -5.24653e-06 | 1 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | median | weighted_mean | none | 16 | -9.97585e-06 | -5.41296e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | mean | none | 16 | -9.95756e-06 | -5.00398e-06 | 1 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | median | weighted_mean | none | 16 | -9.93533e-06 | -5.36498e-06 | 2 | 1 |  |  |  | False | False | False |
| top75_heldout_mean | 75 | 1.64 | median | signed_p75 | none | 8 | -9.91713e-06 | -5.24408e-06 | 3 | 3 | -0.00041186 | -0.000477907 | 0.833333 | False | False | True |
| top50_heldout_mean | 50 | 1.84 | mean | signed_p75 | none | 8 | -9.89558e-06 | -5.09471e-06 | 3 | 3 | -0.000381535 | -0.000461407 | 0.833333 | False | False | True |
| support2_high_block | 36 | 2 | median | mean | none | 16 | -9.88884e-06 | -5.31849e-06 | 2 | 1 |  |  |  | False | False | False |

## Decision

- Strict unified gates exist: `1`, but deployable gates are `0`; strict gate counts by consensus gate: `{'none': 1}`.
- Unified consensus survives only as a diagnostic energy unless a conservative gate can reproduce the margin.
- No submission file is produced.

## Outputs

- `analysis_outputs/q2_s3_unified_strict_cell_consensus_probe_scan.csv`
- `analysis_outputs/q2_s3_unified_strict_cell_consensus_probe_summary.csv`
