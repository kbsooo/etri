# E70 Q2/S3 Strict-Cell Consensus Probe

## Observe

E69 says one strict pair plus global alpha cannot clear margin without tail instability.

## Wonder

Do multiple E68 strict cells share a consensus row/target representation that accumulates into safer Q2/S3 movement?

## Method

- Strict E68 cells used: `155` in the full pool.
- Candidate rows: `2688`.
- Unique predictions: `2576` plus mixmin reference.
- Pools: `12`; base aggregators: `['mean', 'median']`; delta aggregators: `['mean', 'median', 'weighted_mean', 'signed_p75']`; gates: `['none', 'agree60', 'agree75', 'agree60_top50']`; alphas: `[0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]`.
- Strict gate requires all-combo margin, all combo sets beat base, all set worst tails non-worse, hidden/world/block support, and raw-energy non-worsening.

## Summary

| pool | base_agg | delta_agg | gate | n | pool_size | strict_consensus_gate | loose_consensus_gate | all_margin_vs_mixmin | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_sets_beating_base | best_sets_tail_neutral | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_max_m1.00 | mean | mean | none | 7 | 44 | 1 | 3 | 1 | -1.02775e-05 | -5.40624e-06 | 7.79759e-06 | 3 | 3 | -0.000542368 | -0.000488815 | 0.916667 |
| top100_heldout | mean | weighted_mean | none | 7 | 100 | 1 | 3 | 1 | -1.01004e-05 | -5.31171e-06 | 4.72486e-06 | 3 | 3 | -0.000825397 | -0.00079671 | 0.916667 |
| top100_heldout | mean | signed_p75 | none | 7 | 100 | 1 | 2 | 1 | -1.01161e-05 | -5.32742e-06 | 5.98881e-06 | 3 | 3 | -0.000513923 | -0.000468741 | 0.888889 |
| translator_tail_soft_p90_m1.00 | mean | signed_p75 | none | 7 | 34 | 1 | 2 | 1 | -1.01106e-05 | -5.21345e-06 | 6.51216e-06 | 3 | 3 | -0.000486475 | -0.000497488 | 0.888889 |
| translator_tail_soft_max_m1.00 | median | mean | none | 7 | 44 | 1 | 2 | 1 | -1.00184e-05 | -5.35111e-06 | 7.13274e-06 | 3 | 3 | -0.000542368 | -0.000489942 | 0.916667 |
| all | mean | weighted_mean | none | 7 | 155 | 1 | 2 | 1 | -1.00057e-05 | -5.14795e-06 | 2.77216e-06 | 3 | 3 | -0.000410696 | -0.000424434 | 0.916667 |
| all | mean | signed_p75 | none | 7 | 155 | 0 | 3 | 0 | -9.99089e-06 | -5.13318e-06 | 1.93472e-06 | 3 | 3 | -0.000412373 | -0.000429187 | 0.777778 |
| top100_heldout | median | weighted_mean | none | 7 | 100 | 0 | 3 | 0 | -9.96898e-06 | -5.33216e-06 | 4.30956e-06 | 3 | 3 | -0.000825397 | -0.000797829 | 0.916667 |
| top100_heldout | mean | mean | none | 7 | 100 | 0 | 3 | 0 | -9.87518e-06 | -5.08649e-06 | 4.8043e-06 | 3 | 3 | -0.000674712 | -0.000648634 | 0.916667 |
| high_block | mean | mean | none | 7 | 65 | 0 | 3 | 0 | -9.82423e-06 | -5.09644e-06 | 7.9188e-06 | 3 | 3 | -0.000646863 | -0.000615124 | 0.916667 |
| all | mean | mean | none | 7 | 155 | 0 | 3 | 0 | -9.81017e-06 | -4.95246e-06 | 3.28264e-06 | 3 | 3 | -0.000645488 | -0.000668896 | 0.916667 |
| top100_heldout | median | mean | none | 7 | 100 | 0 | 3 | 0 | -9.76873e-06 | -5.13191e-06 | 4.30224e-06 | 3 | 3 | -0.000674712 | -0.000651235 | 0.916667 |
| high_block | mean | mean | agree60 | 7 | 65 | 0 | 3 | 0 | -9.75772e-06 | -5.02992e-06 | 6.49266e-06 | 3 | 3 | -0.000423304 | -0.000407101 | 0.666667 |
| translator_tail_soft_p90_m1.00 | mean | mean | none | 7 | 34 | 0 | 3 | 0 | -9.73106e-06 | -4.83389e-06 | 5.62002e-06 | 3 | 3 | -0.000628755 | -0.000660621 | 0.888889 |
| high_block | median | mean | none | 7 | 65 | 0 | 3 | 0 | -9.67309e-06 | -5.09596e-06 | 6.83211e-06 | 3 | 3 | -0.000646863 | -0.000616121 | 0.916667 |
| all | median | mean | none | 7 | 155 | 0 | 3 | 0 | -9.64224e-06 | -5.03279e-06 | 3.05776e-06 | 3 | 3 | -0.000645488 | -0.000669861 | 0.916667 |
| translator_tail_soft_p90_m1.00 | mean | weighted_mean | none | 7 | 34 | 0 | 3 | 0 | -9.61285e-06 | -4.71567e-06 | 6.46619e-06 | 3 | 3 | -0.000724316 | -0.000735453 | 0.888889 |
| high_world | mean | mean | none | 7 | 54 | 0 | 3 | 0 | -9.55994e-06 | -4.67942e-06 | 2.82184e-06 | 3 | 3 | -0.000502598 | -0.000523097 | 0.916667 |
| translator_tail_soft_p90_m0.50 | mean | mean | none | 7 | 19 | 0 | 3 | 0 | -9.53e-06 | -4.81225e-06 | 7.52206e-06 | 3 | 3 | -0.000720717 | -0.000749325 | 0.888889 |
| translator_tail_soft_max_m1.00 | mean | median | none | 7 | 44 | 0 | 3 | 0 | -9.49898e-06 | -4.62771e-06 | 5.90668e-06 | 3 | 3 | -0.000500268 | -0.000456206 | 0.666667 |
| translator_tail_soft_p90_m1.00 | median | mean | none | 7 | 34 | 0 | 3 | 0 | -9.46904e-06 | -4.86054e-06 | 4.9761e-06 | 3 | 3 | -0.000628755 | -0.000661192 | 0.888889 |
| top100_heldout | mean | weighted_mean | agree60 | 7 | 100 | 0 | 3 | 0 | -9.45497e-06 | -4.66627e-06 | 4.36835e-06 | 3 | 3 | -0.000577577 | -0.000492356 | 0.611111 |
| top100_heldout | mean | weighted_mean | agree60_top50 | 7 | 100 | 0 | 3 | 0 | -9.40869e-06 | -4.62e-06 | 4.25544e-06 | 3 | 3 | -0.000568423 | -0.000481659 | 0.611111 |
| high_world | median | mean | none | 7 | 54 | 0 | 3 | 0 | -9.39718e-06 | -4.70651e-06 | 1.85751e-06 | 3 | 3 | -0.000502598 | -0.000524344 | 0.916667 |
| top100_heldout | median | weighted_mean | agree60 | 7 | 100 | 0 | 3 | 0 | -9.32973e-06 | -4.69291e-06 | 3.93018e-06 | 3 | 3 | -0.000577577 | -0.000494502 | 0.611111 |
| high_block | mean | weighted_mean | agree60 | 7 | 65 | 0 | 3 | 0 | -9.3297e-06 | -4.60191e-06 | 6.91511e-06 | 3 | 3 | -0.000485336 | -0.000458468 | 0.666667 |
| translator_tail_soft_p90_m1.00 | median | weighted_mean | none | 7 | 34 | 0 | 3 | 0 | -9.32518e-06 | -4.71668e-06 | 5.82144e-06 | 3 | 3 | -0.000724316 | -0.000736024 | 0.888889 |
| high_block | mean | signed_p75 | agree60 | 7 | 65 | 0 | 3 | 0 | -9.29149e-06 | -4.5637e-06 | 6.70131e-06 | 3 | 3 | -0.000546921 | -0.000535327 | 0.666667 |
| translator_tail_soft_max_m1.00 | median | median | none | 7 | 44 | 0 | 3 | 0 | -9.28483e-06 | -4.61754e-06 | 5.21752e-06 | 3 | 3 | -0.000500268 | -0.000456513 | 0.666667 |
| top100_heldout | median | weighted_mean | agree60_top50 | 7 | 100 | 0 | 3 | 0 | -9.28451e-06 | -4.64769e-06 | 3.82034e-06 | 3 | 3 | -0.000568423 | -0.000484038 | 0.611111 |

## Best Full-Combo Rows

| pool | pool_size | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | strict_consensus_gate | loose_consensus_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_max_m1.00 | 44 | mean | mean | none | 16 | -1.02775e-05 | -5.40624e-06 | 3 | 3 | -0.000488815 | -0.000542368 | 0.916667 | True | True |
| top100_heldout | 100 | mean | signed_p75 | none | 8 | -1.01161e-05 | -5.32742e-06 | 3 | 3 | -0.000468741 | -0.000513923 | 0.888889 | True | True |
| translator_tail_soft_p90_m1.00 | 34 | mean | signed_p75 | none | 8 | -1.01106e-05 | -5.21345e-06 | 3 | 3 | -0.000497488 | -0.000486475 | 0.888889 | True | True |
| top100_heldout | 100 | mean | weighted_mean | none | 8 | -1.01004e-05 | -5.31171e-06 | 3 | 3 | -0.000403081 | -0.000425773 | 0.916667 | True | True |
| translator_tail_soft_max_m1.00 | 44 | median | mean | none | 16 | -1.00184e-05 | -5.35111e-06 | 3 | 3 | -0.000489942 | -0.000542368 | 0.916667 | True | True |
| all | 155 | mean | weighted_mean | none | 8 | -1.00057e-05 | -5.14795e-06 | 3 | 3 | -0.000424434 | -0.000410696 | 0.916667 | True | True |
| all | 155 | mean | signed_p75 | none | 8 | -9.99089e-06 | -5.13318e-06 | 3 | 3 | -0.000429187 | -0.000412373 | 0.777778 | False | True |
| top100_heldout | 100 | median | weighted_mean | none | 8 | -9.96898e-06 | -5.33216e-06 | 3 | 3 | -0.000405602 | -0.000425773 | 0.916667 | False | True |
| top100_heldout | 100 | median | signed_p75 | none | 8 | -9.92967e-06 | -5.29285e-06 | 3 | 3 | -0.000469184 | -0.000513923 | 0.888889 | False | True |
| top100_heldout | 100 | mean | mean | none | 16 | -9.87518e-06 | -5.08649e-06 | 3 | 3 | -0.000648634 | -0.000674712 | 0.916667 | False | True |
| all | 155 | median | weighted_mean | none | 8 | -9.84971e-06 | -5.24027e-06 | 3 | 3 | -0.000424443 | -0.000410696 | 0.916667 | False | True |
| top50_heldout | 50 | mean | mean | none | 8 | -9.83338e-06 | -5.15536e-06 | 3 | 3 | -0.000384903 | -0.000411597 | 0.916667 | False | True |
| high_block | 65 | mean | mean | none | 16 | -9.82423e-06 | -5.09644e-06 | 3 | 3 | -0.000615124 | -0.000646863 | 0.916667 | False | True |
| translator_tail_soft_p90_m1.00 | 34 | median | signed_p75 | none | 8 | -9.82231e-06 | -5.2138e-06 | 3 | 3 | -0.00049837 | -0.000486475 | 0.888889 | False | True |
| all | 155 | mean | mean | none | 8 | -9.81017e-06 | -4.95246e-06 | 3 | 3 | -0.000337978 | -0.000332013 | 0.916667 | False | True |
| all | 155 | median | signed_p75 | none | 8 | -9.80692e-06 | -5.19747e-06 | 3 | 3 | -0.000429389 | -0.000412373 | 0.777778 | False | True |
| top100_heldout | 100 | mean | mean | none | 8 | -9.77814e-06 | -4.98945e-06 | 3 | 3 | -0.000327162 | -0.000345745 | 0.916667 | False | True |
| top50_heldout | 50 | median | mean | none | 8 | -9.77064e-06 | -5.14521e-06 | 3 | 3 | -0.00038515 | -0.000411597 | 0.916667 | False | True |
| top100_heldout | 100 | median | mean | none | 16 | -9.76873e-06 | -5.13191e-06 | 3 | 3 | -0.000651235 | -0.000674712 | 0.916667 | False | True |
| top50_heldout | 50 | mean | weighted_mean | none | 8 | -9.76783e-06 | -5.0898e-06 | 3 | 3 | -0.000441932 | -0.000471789 | 0.916667 | False | True |
| high_block | 65 | mean | mean | agree60 | 16 | -9.75772e-06 | -5.02992e-06 | 3 | 3 | -0.000407101 | -0.000423304 | 0.666667 | False | True |
| translator_tail_soft_p90_m1.00 | 34 | mean | mean | none | 16 | -9.73106e-06 | -4.83389e-06 | 3 | 3 | -0.000660621 | -0.000628755 | 0.888889 | False | True |
| translator_tail_soft_p90_m0.50 | 19 | mean | weighted_mean | none | 16 | -9.67915e-06 | -4.9614e-06 | 3 | 3 | -0.000410949 | -0.000417801 | 0.888889 | False | True |
| top50_heldout | 50 | median | weighted_mean | none | 8 | -9.67362e-06 | -5.04819e-06 | 3 | 3 | -0.000442366 | -0.000471789 | 0.916667 | False | True |
| high_block | 65 | median | mean | none | 16 | -9.67309e-06 | -5.09596e-06 | 3 | 3 | -0.000616121 | -0.000646863 | 0.916667 | False | True |

## Decision

- Strict consensus gates exist: `6`. This branch deserves a unified-rule stress before any submission.
- No submission file is produced.

## Outputs

- `analysis_outputs/q2_s3_strict_cell_consensus_probe_scan.csv`
- `analysis_outputs/q2_s3_strict_cell_consensus_probe_summary.csv`
