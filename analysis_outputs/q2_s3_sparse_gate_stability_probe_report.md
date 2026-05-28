# E74 Sparse Q2/S3 Gate Stability Probe

## Observe

E73 is the first materialized non-`none` Q2/S3 consensus file, but its selected pool has only `13` cells.

## Wonder

Is the E73 sparse-magnitude gate a broad latent consensus, or does it depend on a few fragile cells?

## Method

- Source pool: `translator_tail_soft_p90_m0.50`.
- Source cells in pool: `13`.
- Variants: `94` across reference, jackknife, group-keep, rank-keep, and deterministic bootstrap subsets.
- Alphas: `[8.0, 12.0, 16.0, 20.0, 24.0]`; gate: `top_abs50`; base/delta: `mean`/`signed_p75`.
- Every variant is combo-scored and hidden/world/block stressed, not just ranked by all-combo delta.

## Reference E73 Geometry

| all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | strict_gate | deployable_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| -1.05458e-05 | -5.78026e-06 | 1.00163e-05 | -0.000391043 | -0.000280957 | 0.722222 | True | True |

## Stability Summary

| variant_kind | rows | variants | strict | deployable | loose | alpha16_deployable | alpha16_loose | best_all_delta_vs_mixmin | median_alpha16_all_delta | worst_alpha16_all_delta | best_all_minus_base | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate | median_jaccard_vs_e73 | max_q2s3_delta_vs_e73 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bootstrap8 | 300 | 60 | 91 | 91 | 300 | 48 | 60 | -1.08084e-05 | -1.034e-05 | -9.7796e-06 | -6.06232e-06 | -0.000604609 | -0.000469118 | 0.75 | 0.707547 | 0.00100693 |
| jackknife | 65 | 13 | 26 | 26 | 65 | 13 | 13 | -1.07697e-05 | -1.04346e-05 | -1.03552e-05 | -5.99236e-06 | -0.00059229 | -0.00046094 | 0.722222 | 0.885714 | 0.000395102 |
| rank_keep | 50 | 10 | 14 | 14 | 50 | 7 | 10 | -1.06602e-05 | -1.00336e-05 | -9.50832e-06 | -6.02525e-06 | -0.000606017 | -0.000484545 | 0.75 | 0.704644 | 0.00112239 |
| group_keep | 50 | 10 | 8 | 8 | 50 | 3 | 10 | -1.07068e-05 | -9.74255e-06 | -9.3266e-06 | -5.96833e-06 | -0.000602703 | -0.000463525 | 0.75 | 0.699982 | 0.00164889 |
| reference | 5 | 1 | 2 | 2 | 5 | 1 | 1 | -1.07261e-05 | -1.05458e-05 | -1.05458e-05 | -5.96055e-06 | -0.000576243 | -0.000422721 | 0.722222 | 1 | 0 |

## Alpha Sensitivity

| variant_kind | alpha | rows | deployable | strict | loose | best | median |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bootstrap8 | 8 | 60 | 0 | 0 | 60 | -8.59776e-06 | -8.43858e-06 |
| bootstrap8 | 12 | 60 | 0 | 0 | 60 | -9.85109e-06 | -9.65242e-06 |
| bootstrap8 | 16 | 60 | 48 | 48 | 60 | -1.05658e-05 | -1.034e-05 |
| bootstrap8 | 20 | 60 | 43 | 43 | 60 | -1.08084e-05 | -1.05251e-05 |
| bootstrap8 | 24 | 60 | 0 | 0 | 60 | -1.06041e-05 | -1.01834e-05 |
| group_keep | 8 | 10 | 0 | 0 | 10 | -8.58232e-06 | -8.04714e-06 |
| group_keep | 12 | 10 | 0 | 0 | 10 | -9.7949e-06 | -9.16051e-06 |
| group_keep | 16 | 10 | 3 | 3 | 10 | -1.04974e-05 | -9.74255e-06 |
| group_keep | 20 | 10 | 4 | 4 | 10 | -1.07068e-05 | -9.86589e-06 |
| group_keep | 24 | 10 | 1 | 1 | 10 | -1.03918e-05 | -9.60674e-06 |
| jackknife | 8 | 13 | 0 | 0 | 13 | -8.61829e-06 | -8.54016e-06 |
| jackknife | 12 | 13 | 0 | 0 | 13 | -9.87221e-06 | -9.75921e-06 |
| jackknife | 16 | 13 | 13 | 13 | 13 | -1.05728e-05 | -1.04346e-05 |
| jackknife | 20 | 13 | 13 | 13 | 13 | -1.07697e-05 | -1.06017e-05 |
| jackknife | 24 | 13 | 0 | 0 | 13 | -1.04558e-05 | -1.02861e-05 |
| rank_keep | 8 | 10 | 0 | 0 | 10 | -8.54789e-06 | -8.26127e-06 |
| rank_keep | 12 | 10 | 0 | 0 | 10 | -9.81801e-06 | -9.39597e-06 |
| rank_keep | 16 | 10 | 7 | 7 | 10 | -1.04886e-05 | -1.00336e-05 |
| rank_keep | 20 | 10 | 7 | 7 | 10 | -1.06602e-05 | -1.0166e-05 |
| rank_keep | 24 | 10 | 0 | 0 | 10 | -1.02774e-05 | -9.84415e-06 |
| reference | 8 | 1 | 0 | 0 | 1 | -8.60941e-06 | -8.60941e-06 |
| reference | 12 | 1 | 0 | 0 | 1 | -9.85003e-06 | -9.85003e-06 |
| reference | 16 | 1 | 1 | 1 | 1 | -1.05458e-05 | -1.05458e-05 |
| reference | 20 | 1 | 1 | 1 | 1 | -1.07261e-05 | -1.07261e-05 |
| reference | 24 | 1 | 0 | 0 | 1 | -1.03474e-05 | -1.03474e-05 |

## Jackknife At Alpha 16

| variant_name | pool_size | pool_support2_count | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | q2s3_topabs_jaccard_vs_e73 | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| drop_cell_098 | 12 | 6 | -1.05728e-05 | -5.80673e-06 | 1.02651e-05 | -0.000401747 | -0.000305493 | 0.722222 | 0.867925 | True | True | True |
| drop_cell_097 | 12 | 6 | -1.05569e-05 | -5.80687e-06 | 1.027e-05 | -0.000401747 | -0.000305538 | 0.722222 | 0.867925 | True | True | True |
| drop_cell_077 | 12 | 6 | -1.05347e-05 | -5.72415e-06 | 1.0059e-05 | -0.000400143 | -0.00030313 | 0.722222 | 0.850467 | True | True | True |
| drop_cell_048 | 12 | 5 | -1.05212e-05 | -5.7653e-06 | 1.0335e-05 | -0.000391043 | -0.000280463 | 0.722222 | 0.912621 | True | True | True |
| drop_cell_076 | 12 | 6 | -1.0513e-05 | -5.72413e-06 | 1.00655e-05 | -0.000400143 | -0.000303192 | 0.722222 | 0.850467 | True | True | True |
| drop_cell_050 | 12 | 5 | -1.04443e-05 | -5.69057e-06 | 1.02239e-05 | -0.000399303 | -0.00028276 | 0.722222 | 0.885714 | True | True | True |
| drop_cell_049 | 12 | 5 | -1.04346e-05 | -5.69594e-06 | 1.02271e-05 | -0.000399303 | -0.000282977 | 0.722222 | 0.885714 | True | True | True |
| drop_cell_043 | 12 | 5 | -1.04167e-05 | -5.61827e-06 | 9.98499e-06 | -0.000380522 | -0.000279517 | 0.722222 | 0.912621 | True | True | True |
| drop_cell_100 | 12 | 6 | -1.03835e-05 | -5.68833e-06 | 1.01367e-05 | -0.00038869 | -0.00028285 | 0.722222 | 0.867925 | True | True | True |
| drop_cell_099 | 12 | 6 | -1.03768e-05 | -5.64967e-06 | 1.00032e-05 | -0.00038526 | -0.000279231 | 0.722222 | 0.87619 | True | True | True |
| drop_cell_047 | 12 | 5 | -1.03712e-05 | -5.57702e-06 | 9.81358e-06 | -0.000394957 | -0.00028627 | 0.722222 | 0.885714 | True | True | True |
| drop_cell_046 | 12 | 5 | -1.03566e-05 | -5.58282e-06 | 9.81759e-06 | -0.000394957 | -0.000286568 | 0.722222 | 0.885714 | True | True | True |
| drop_cell_058 | 12 | 6 | -1.03552e-05 | -5.61048e-06 | 1.00513e-05 | -0.000385372 | -0.000286357 | 0.722222 | 0.903846 | True | True | True |

## Best Rows

| variant_kind | variant_name | pool_size | alpha | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | q2s3_topabs_jaccard_vs_e73 | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bootstrap8 | bootstrap8_002 | 8 | 20 | -1.08084e-05 | -5.96242e-06 | 1.04732e-05 | -0.000498842 | -0.000364282 | 0.722222 | 0.698113 | True | True | True |
| bootstrap8 | bootstrap8_059 | 8 | 20 | -1.07737e-05 | -6.06232e-06 | 1.09295e-05 | -0.000504162 | -0.000367818 | 0.75 | 0.691589 | True | True | True |
| jackknife | drop_cell_077 | 12 | 20 | -1.07697e-05 | -5.95912e-06 | 1.10523e-05 | -0.000496106 | -0.000380028 | 0.722222 | 0.850467 | True | True | True |
| jackknife | drop_cell_098 | 12 | 20 | -1.07584e-05 | -5.99236e-06 | 1.129e-05 | -0.000497883 | -0.000382998 | 0.722222 | 0.867925 | True | True | True |
| bootstrap8 | bootstrap8_019 | 8 | 20 | -1.07519e-05 | -5.88645e-06 | 1.07415e-05 | -0.00048382 | -0.000367302 | 0.722222 | 0.721154 | True | True | True |
| jackknife | drop_cell_076 | 12 | 20 | -1.07482e-05 | -5.9593e-06 | 1.10588e-05 | -0.000496106 | -0.000380034 | 0.722222 | 0.850467 | True | True | True |
| bootstrap8 | bootstrap8_048 | 8 | 20 | -1.07392e-05 | -6.00035e-06 | 1.17517e-05 | -0.000488839 | -0.000358021 | 0.75 | 0.704762 | True | True | True |
| jackknife | drop_cell_097 | 12 | 20 | -1.07374e-05 | -5.98742e-06 | 1.13102e-05 | -0.000497883 | -0.000383002 | 0.722222 | 0.867925 | True | True | True |
| bootstrap8 | bootstrap8_050 | 8 | 20 | -1.07301e-05 | -5.93154e-06 | 1.17754e-05 | -0.000507979 | -0.00038982 | 0.722222 | 0.716981 | True | True | True |
| reference | full_pool | 13 | 20 | -1.07261e-05 | -5.96055e-06 | 1.10367e-05 | -0.000484506 | -0.000351115 | 0.722222 | 1 | True | True | True |
| bootstrap8 | bootstrap8_001 | 8 | 20 | -1.07195e-05 | -5.96719e-06 | 1.07931e-05 | -0.000488992 | -0.000347429 | 0.75 | 0.72381 | True | True | True |
| bootstrap8 | bootstrap8_053 | 8 | 20 | -1.07172e-05 | -6.04077e-06 | 1.1066e-05 | -0.000490953 | -0.000374787 | 0.75 | 0.707547 | True | True | True |
| jackknife | drop_cell_048 | 12 | 20 | -1.07153e-05 | -5.95932e-06 | 1.13141e-05 | -0.000484506 | -0.000350522 | 0.722222 | 0.912621 | True | True | True |
| group_keep | base_cell_gate_raw_agree | 6 | 20 | -1.07068e-05 | -5.81425e-06 | 1.11479e-05 | -0.000479587 | -0.000364393 | 0.722222 | 0.708738 | True | True | True |
| bootstrap8 | bootstrap8_031 | 8 | 20 | -1.06929e-05 | -6.04148e-06 | 1.10909e-05 | -0.000490953 | -0.000374706 | 0.75 | 0.707547 | True | True | True |
| bootstrap8 | bootstrap8_052 | 8 | 20 | -1.06925e-05 | -5.88243e-06 | 1.03395e-05 | -0.000502333 | -0.000382582 | 0.75 | 0.685185 | True | True | True |
| bootstrap8 | bootstrap8_028 | 8 | 20 | -1.06892e-05 | -5.98801e-06 | 1.03658e-05 | -0.000485776 | -0.000378112 | 0.75 | 0.707547 | True | True | True |
| bootstrap8 | bootstrap8_004 | 8 | 20 | -1.06749e-05 | -5.9137e-06 | 1.12943e-05 | -0.00050149 | -0.000367748 | 0.722222 | 0.691589 | True | True | True |
| bootstrap8 | bootstrap8_027 | 8 | 20 | -1.06695e-05 | -5.83006e-06 | 1.07174e-05 | -0.00047602 | -0.000372221 | 0.722222 | 0.714286 | True | True | True |
| bootstrap8 | bootstrap8_025 | 8 | 20 | -1.0666e-05 | -5.88623e-06 | 1.07566e-05 | -0.000485131 | -0.000367877 | 0.722222 | 0.707547 | True | True | True |
| rank_keep | world_support_minus_base_top8 | 8 | 20 | -1.06602e-05 | -6.02525e-06 | 1.25676e-05 | -0.000509392 | -0.000381778 | 0.75 | 0.716981 | True | True | True |
| bootstrap8 | bootstrap8_060 | 8 | 20 | -1.06558e-05 | -5.86299e-06 | 1.10801e-05 | -0.000489321 | -0.000346448 | 0.722222 | 0.72381 | True | True | True |
| bootstrap8 | bootstrap8_034 | 8 | 20 | -1.0645e-05 | -5.93409e-06 | 1.08769e-05 | -0.000486921 | -0.000346503 | 0.75 | 0.72381 | True | True | True |
| bootstrap8 | bootstrap8_038 | 8 | 20 | -1.06443e-05 | -5.94557e-06 | 1.20434e-05 | -0.00048753 | -0.000369629 | 0.722222 | 0.714286 | True | True | True |
| bootstrap8 | bootstrap8_013 | 8 | 20 | -1.06434e-05 | -5.86396e-06 | 1.0288e-05 | -0.000500827 | -0.000379541 | 0.722222 | 0.685185 | True | True | True |
| bootstrap8 | bootstrap8_041 | 8 | 20 | -1.06381e-05 | -5.82473e-06 | 1.01867e-05 | -0.000498712 | -0.000373453 | 0.694444 | 0.675926 | True | True | True |
| bootstrap8 | bootstrap8_056 | 8 | 20 | -1.06319e-05 | -5.88068e-06 | 1.1479e-05 | -0.000484443 | -0.000362976 | 0.722222 | 0.707547 | True | True | True |
| bootstrap8 | bootstrap8_022 | 8 | 20 | -1.06298e-05 | -5.93976e-06 | 1.13995e-05 | -0.000500574 | -0.000386774 | 0.722222 | 0.707547 | True | True | True |
| bootstrap8 | bootstrap8_026 | 8 | 20 | -1.06269e-05 | -5.86554e-06 | 1.13836e-05 | -0.000490243 | -0.000349206 | 0.722222 | 0.72381 | True | True | True |
| jackknife | drop_cell_043 | 12 | 20 | -1.06268e-05 | -5.82842e-06 | 1.09232e-05 | -0.000471505 | -0.000349398 | 0.722222 | 0.912621 | True | True | True |

## Best Deployable Rows

| variant_kind | variant_name | pool_size | alpha | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | q2s3_topabs_jaccard_vs_e73 | mean_abs_q2s3_logit_delta_vs_e73 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bootstrap8 | bootstrap8_002 | 8 | 20 | -1.08084e-05 | -5.96242e-06 | 1.04732e-05 | -0.000498842 | -0.000364282 | 0.722222 | 0.698113 | 0.00147324 |
| bootstrap8 | bootstrap8_059 | 8 | 20 | -1.07737e-05 | -6.06232e-06 | 1.09295e-05 | -0.000504162 | -0.000367818 | 0.75 | 0.691589 | 0.00155005 |
| jackknife | drop_cell_077 | 12 | 20 | -1.07697e-05 | -5.95912e-06 | 1.10523e-05 | -0.000496106 | -0.000380028 | 0.722222 | 0.850467 | 0.00137629 |
| jackknife | drop_cell_098 | 12 | 20 | -1.07584e-05 | -5.99236e-06 | 1.129e-05 | -0.000497883 | -0.000382998 | 0.722222 | 0.867925 | 0.00137341 |
| bootstrap8 | bootstrap8_019 | 8 | 20 | -1.07519e-05 | -5.88645e-06 | 1.07415e-05 | -0.00048382 | -0.000367302 | 0.722222 | 0.721154 | 0.00126902 |
| jackknife | drop_cell_076 | 12 | 20 | -1.07482e-05 | -5.9593e-06 | 1.10588e-05 | -0.000496106 | -0.000380034 | 0.722222 | 0.850467 | 0.00137629 |
| bootstrap8 | bootstrap8_048 | 8 | 20 | -1.07392e-05 | -6.00035e-06 | 1.17517e-05 | -0.000488839 | -0.000358021 | 0.75 | 0.704762 | 0.00143644 |
| jackknife | drop_cell_097 | 12 | 20 | -1.07374e-05 | -5.98742e-06 | 1.13102e-05 | -0.000497883 | -0.000383002 | 0.722222 | 0.867925 | 0.00137341 |
| bootstrap8 | bootstrap8_050 | 8 | 20 | -1.07301e-05 | -5.93154e-06 | 1.17754e-05 | -0.000507979 | -0.00038982 | 0.722222 | 0.716981 | 0.00143128 |
| reference | full_pool | 13 | 20 | -1.07261e-05 | -5.96055e-06 | 1.10367e-05 | -0.000484506 | -0.000351115 | 0.722222 | 1 | 0.00120089 |
| bootstrap8 | bootstrap8_001 | 8 | 20 | -1.07195e-05 | -5.96719e-06 | 1.07931e-05 | -0.000488992 | -0.000347429 | 0.75 | 0.72381 | 0.00124177 |
| bootstrap8 | bootstrap8_053 | 8 | 20 | -1.07172e-05 | -6.04077e-06 | 1.1066e-05 | -0.000490953 | -0.000374787 | 0.75 | 0.707547 | 0.00140306 |
| jackknife | drop_cell_048 | 12 | 20 | -1.07153e-05 | -5.95932e-06 | 1.13141e-05 | -0.000484506 | -0.000350522 | 0.722222 | 0.912621 | 0.00120089 |
| group_keep | base_cell_gate_raw_agree | 6 | 20 | -1.07068e-05 | -5.81425e-06 | 1.11479e-05 | -0.000479587 | -0.000364393 | 0.722222 | 0.708738 | 0.0011912 |
| bootstrap8 | bootstrap8_031 | 8 | 20 | -1.06929e-05 | -6.04148e-06 | 1.10909e-05 | -0.000490953 | -0.000374706 | 0.75 | 0.707547 | 0.00140306 |
| bootstrap8 | bootstrap8_052 | 8 | 20 | -1.06925e-05 | -5.88243e-06 | 1.03395e-05 | -0.000502333 | -0.000382582 | 0.75 | 0.685185 | 0.00136447 |
| bootstrap8 | bootstrap8_028 | 8 | 20 | -1.06892e-05 | -5.98801e-06 | 1.03658e-05 | -0.000485776 | -0.000378112 | 0.75 | 0.707547 | 0.00123703 |
| bootstrap8 | bootstrap8_004 | 8 | 20 | -1.06749e-05 | -5.9137e-06 | 1.12943e-05 | -0.00050149 | -0.000367748 | 0.722222 | 0.691589 | 0.00149647 |
| bootstrap8 | bootstrap8_027 | 8 | 20 | -1.06695e-05 | -5.83006e-06 | 1.07174e-05 | -0.00047602 | -0.000372221 | 0.722222 | 0.714286 | 0.00114738 |
| bootstrap8 | bootstrap8_025 | 8 | 20 | -1.0666e-05 | -5.88623e-06 | 1.07566e-05 | -0.000485131 | -0.000367877 | 0.722222 | 0.707547 | 0.00127284 |
| rank_keep | world_support_minus_base_top8 | 8 | 20 | -1.06602e-05 | -6.02525e-06 | 1.25676e-05 | -0.000509392 | -0.000381778 | 0.75 | 0.716981 | 0.00157577 |
| bootstrap8 | bootstrap8_060 | 8 | 20 | -1.06558e-05 | -5.86299e-06 | 1.10801e-05 | -0.000489321 | -0.000346448 | 0.722222 | 0.72381 | 0.0012834 |
| bootstrap8 | bootstrap8_034 | 8 | 20 | -1.0645e-05 | -5.93409e-06 | 1.08769e-05 | -0.000486921 | -0.000346503 | 0.75 | 0.72381 | 0.00127965 |
| bootstrap8 | bootstrap8_038 | 8 | 20 | -1.06443e-05 | -5.94557e-06 | 1.20434e-05 | -0.00048753 | -0.000369629 | 0.722222 | 0.714286 | 0.00143084 |
| bootstrap8 | bootstrap8_013 | 8 | 20 | -1.06434e-05 | -5.86396e-06 | 1.0288e-05 | -0.000500827 | -0.000379541 | 0.722222 | 0.685185 | 0.00147307 |
| bootstrap8 | bootstrap8_041 | 8 | 20 | -1.06381e-05 | -5.82473e-06 | 1.01867e-05 | -0.000498712 | -0.000373453 | 0.694444 | 0.675926 | 0.00143835 |
| bootstrap8 | bootstrap8_056 | 8 | 20 | -1.06319e-05 | -5.88068e-06 | 1.1479e-05 | -0.000484443 | -0.000362976 | 0.722222 | 0.707547 | 0.00134957 |
| bootstrap8 | bootstrap8_022 | 8 | 20 | -1.06298e-05 | -5.93976e-06 | 1.13995e-05 | -0.000500574 | -0.000386774 | 0.722222 | 0.707547 | 0.00134028 |
| bootstrap8 | bootstrap8_026 | 8 | 20 | -1.06269e-05 | -5.86554e-06 | 1.13836e-05 | -0.000490243 | -0.000349206 | 0.722222 | 0.72381 | 0.00132061 |
| jackknife | drop_cell_043 | 12 | 20 | -1.06268e-05 | -5.82842e-06 | 1.09232e-05 | -0.000471505 | -0.000349398 | 0.722222 | 0.912621 | 0.00100806 |

## Decision

- E73 is not single-cell fragile: many jackknife variants remain deployable and bootstrap support is non-zero.
- This probe does not write a new submission. It decides whether the existing E73 file should be treated as robust or as a high-risk public sensor.

## Outputs

- `analysis_outputs/q2_s3_sparse_gate_stability_probe_scan.csv`
- `analysis_outputs/q2_s3_sparse_gate_stability_probe_summary.csv`
