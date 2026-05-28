# E53 Calendar-Flank Block Count-State Probe

## Observe

E48 made `submission_mixmin_0c916bb4.csv` the public frontier. E50-E52 then falsified three selector translations: calendar kNN, anchor-calendar kNN, and existing-candidate binary-world replacement.

## Wonder

Does the subject-calendar flank context actually predict a hidden block count/rate state, and does that predicted state prefer mixmin over a2c8 on the real hidden blocks?

## Hypothesis

H53: mixmin approximates a hidden block count-state. If true, a fold-safe calendar-flank posterior should beat subject mean on pseudo-hidden blocks and its real hidden-block rates should give negative expected LogLoss delta for mixmin versus a2c8.

## Method

- Pseudo-hidden blocks: `369`, generated from train rows with actual submission block lengths.
- Real hidden submission blocks: `36`.
- Context: subject mean, global mean, previous/next labeled flank values, block length bin, and donor block count/rate signatures.
- Predictors: subject mean, two edge-shrink baselines, strict-subject calendar count posterior, and local non-overlap calendar count posterior.
- Stress: strict-subject excludes same subject donors; local non-overlap allows same subject but excludes overlapping pseudo blocks.

## Pseudo-Hidden Block Results

| method | weighted_row_logloss | delta_weighted_row_logloss_vs_subject | weighted_count_nll_per_row | delta_weighted_count_nll_per_row_vs_subject | rate_mae_weighted | count_mae_mean |
| --- | --- | --- | --- | --- | --- | --- |
| calendar_count_local | 0.607736 | -0.005266 | 0.285504 | -0.005266 | 0.192483 | 0.887298 |
| edge_shrink025 | 0.612511 | -0.000491 | 0.290279 | -0.000491 | 0.192185 | 0.885928 |
| subject_mean | 0.613002 | 0.000000 | 0.290770 | 0.000000 | 0.193329 | 0.891199 |
| calendar_count_strict | 0.614436 | 0.001434 | 0.292203 | 0.001434 | 0.198208 | 0.913692 |
| edge_shrink050 | 0.652040 | 0.039038 | 0.329808 | 0.039038 | 0.214028 | 0.986617 |

## Target Detail

| method | target | target_row_logloss | delta_row_vs_subject | target_count_nll_per_row | delta_count_vs_subject | target_count_mae |
| --- | --- | --- | --- | --- | --- | --- |
| calendar_count_strict | Q1 | 0.636830 | -0.011907 | 0.299048 | -0.011907 | 0.948017 |
| calendar_count_local | Q1 | 0.638528 | -0.010209 | 0.300746 | -0.010209 | 0.956510 |
| subject_mean | Q1 | 0.648737 | 0.000000 | 0.310955 | 0.000000 | 0.995369 |
| calendar_count_strict | Q2 | 0.664615 | -0.029170 | 0.333340 | -0.029170 | 1.081603 |
| calendar_count_local | Q2 | 0.668231 | -0.025553 | 0.336956 | -0.025553 | 1.094975 |
| subject_mean | Q2 | 0.693785 | 0.000000 | 0.362510 | 0.000000 | 1.160347 |
| calendar_count_local | Q3 | 0.657142 | -0.012204 | 0.315564 | -0.012204 | 0.987508 |
| calendar_count_strict | Q3 | 0.657603 | -0.011743 | 0.316025 | -0.011743 | 0.993281 |
| subject_mean | Q3 | 0.669346 | 0.000000 | 0.327769 | 0.000000 | 1.025233 |
| calendar_count_local | S1 | 0.575210 | -0.001837 | 0.259979 | -0.001837 | 0.771223 |
| subject_mean | S1 | 0.577047 | 0.000000 | 0.261816 | 0.000000 | 0.756883 |
| calendar_count_strict | S1 | 0.578173 | 0.001126 | 0.262943 | 0.001126 | 0.783010 |
| subject_mean | S2 | 0.566900 | 0.000000 | 0.266909 | 0.000000 | 0.801674 |
| calendar_count_local | S2 | 0.570727 | 0.003827 | 0.270737 | 0.003827 | 0.826212 |
| calendar_count_strict | S2 | 0.590973 | 0.024074 | 0.290983 | 0.024074 | 0.907458 |
| subject_mean | S3 | 0.502954 | 0.000000 | 0.221066 | 0.000000 | 0.640065 |
| calendar_count_local | S3 | 0.510901 | 0.007948 | 0.229014 | 0.007948 | 0.691853 |
| calendar_count_strict | S3 | 0.537247 | 0.034293 | 0.255359 | 0.034293 | 0.797457 |
| subject_mean | S4 | 0.632245 | 0.000000 | 0.284363 | 0.000000 | 0.858820 |
| calendar_count_local | S4 | 0.633411 | 0.001166 | 0.285529 | 0.001166 | 0.882802 |
| calendar_count_strict | S4 | 0.635608 | 0.003363 | 0.287726 | 0.003363 | 0.885021 |

## Hidden-Block Mixmin Alignment

| mode | hidden_blocks | weighted_mixmin_delta_vs_a2c8 | mean_mixmin_delta_vs_a2c8 | mean_raw05_delta_vs_a2c8 | mixmin_better_block_rate | median_support_min |
| --- | --- | --- | --- | --- | --- | --- |
| strict_subject | 36.000000 | -0.000179 | -0.000434 | 0.000841 | 0.527778 | 5.500000 |
| local_nonoverlap | 36.000000 | 0.000250 | -0.000095 | 0.000779 | 0.444444 | 6.000000 |

## Hidden-Block Target Alignment

| mode | target | weighted_mixmin_delta_vs_a2c8 | mean_mixmin_delta_vs_a2c8 | mixmin_better_block_rate | mean_predicted_rate |
| --- | --- | --- | --- | --- | --- |
| local_nonoverlap | S3 | -0.002397 | -0.002785 | 0.777778 | 0.617309 |
| local_nonoverlap | S2 | -0.001477 | -0.002056 | 0.750000 | 0.627521 |
| local_nonoverlap | Q2 | -0.000939 | -0.001085 | 0.666667 | 0.571181 |
| local_nonoverlap | Q3 | 0.000248 | -0.000690 | 0.583333 | 0.610037 |
| local_nonoverlap | S4 | 0.000607 | 0.000468 | 0.472222 | 0.569159 |
| local_nonoverlap | Q1 | 0.001219 | 0.000440 | 0.472222 | 0.474592 |
| local_nonoverlap | S1 | 0.004487 | 0.005044 | 0.138889 | 0.665262 |
| strict_subject | S3 | -0.003537 | -0.003930 | 0.805556 | 0.629684 |
| strict_subject | S2 | -0.002363 | -0.003028 | 0.722222 | 0.641735 |
| strict_subject | Q2 | -0.000820 | -0.000942 | 0.666667 | 0.562599 |
| strict_subject | Q3 | 0.000333 | -0.000216 | 0.500000 | 0.592669 |
| strict_subject | Q1 | 0.000649 | -0.000030 | 0.472222 | 0.464215 |
| strict_subject | S4 | 0.000821 | 0.000706 | 0.444444 | 0.566856 |
| strict_subject | S1 | 0.003665 | 0.004405 | 0.166667 | 0.660291 |

## Decision

The only meaningful pseudo-hidden improvement is local/same-subject. That is a weak representation signal but not a private-safe mixmin explanation.

Strict-subject target count recovery improved `3` targets, while local recovery improved `4` targets. This keeps calendar-flank state as an energy feature, not a candidate generator.

## Outputs

- `analysis_outputs/calendar_flank_block_count_state_summary.csv`
- `analysis_outputs/calendar_flank_block_count_state_target_detail.csv`
- `analysis_outputs/calendar_flank_block_count_state_block_detail.csv`
- `analysis_outputs/calendar_flank_block_count_state_hidden_alignment.csv`
- `analysis_outputs/calendar_flank_block_count_state_hidden_target_alignment.csv`
