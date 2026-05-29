# E118 E101 Flank-Label Support Audit

## Question

E102 found weak edge locality for E101's `50` active Q2/S3 cells. E105 showed
that subject priors make the active hard-label world less implausible than
global priors. E114 showed raw context does not pre-validate that world.

This audit asks whether the simplest remaining visible context, train-label
flanks around each hidden block, supports the hard labels that would make E101
beat E95.

## Prior Summary

| prior | expected_delta_per_all_cells | beat_e95_probability | match_e95_mixmin_edge_probability | mean_support_probability | s3_support_probability | top10_flip_support_probability |
| --- | --- | --- | --- | --- | --- | --- |
| edge_endpoint_beta | 0.000003 | 0.437780 | 0.120745 | 0.591791 | 0.608095 | 0.876919 |
| both_equal_beta | 0.000005 | 0.392225 | 0.102360 | 0.601429 | 0.598638 | 0.844036 |
| nearest_beta | 0.000006 | 0.370610 | 0.093965 | 0.591791 | 0.599548 | 0.843585 |
| next_beta | 0.000007 | 0.347720 | 0.095350 | 0.584534 | 0.607474 | 0.825949 |
| subject | 0.000008 | 0.337185 | 0.093600 | 0.587686 | 0.604450 | 0.815378 |
| conflict_flat | 0.000010 | 0.297985 | 0.072895 | 0.584471 | 0.595546 | 0.805483 |
| both_distance_beta | 0.000010 | 0.297125 | 0.070510 | 0.576146 | 0.594239 | 0.829096 |
| prev_beta | 0.000011 | 0.272680 | 0.062235 | 0.577027 | 0.588328 | 0.816830 |
| nearest_hard085 | 0.000018 | 0.146745 | 0.021070 | 0.570000 | 0.562821 | 0.780000 |
| global | 0.000049 | 0.015920 | 0.002150 | 0.498000 | 0.495840 | 0.597333 |

## Target Breakdown

| target | cells | both_flanks_rate | conflict_rate | edge_or_near_edge_rate | subject_support | best_flank_support |
| --- | --- | --- | --- | --- | --- | --- |
| Q2 | 11 | 0.545455 | 0.454545 | 0.545455 | 0.528248 | 0.533983 |
| S3 | 39 | 0.615385 | 0.179487 | 0.641026 | 0.604450 | 0.608095 |

## Active-Cell Structure Versus Target-Count Null

| metric | observed | null_mean | null_p05 | null_p50 | null_p95 | p_one_sided | direction | n_perm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| edge_or_near_edge_rate | 0.620000 | 0.471289 | 0.360000 | 0.480000 | 0.580000 | 0.016999 | high_is_concentrated | 20000 |
| conflict_given_both_rate | 0.400000 | 0.240056 | 0.125000 | 0.241379 | 0.363636 | 0.018649 | high_is_concentrated | 20000 |
| flank_conflict_rate | 0.240000 | 0.149933 | 0.080000 | 0.140000 | 0.220000 | 0.048998 | high_is_concentrated | 20000 |
| edge_and_conflict_rate | 0.160000 | 0.098000 | 0.040000 | 0.100000 | 0.160000 | 0.095645 | high_is_concentrated | 20000 |
| mean_min_flank_gap_days | 4.500000 | 5.246002 | 4.260000 | 5.220000 | 6.340000 | 0.118744 | low_is_concentrated | 20000 |
| gap_le1_rate | 0.240000 | 0.199782 | 0.120000 | 0.200000 | 0.280000 | 0.280136 | high_is_concentrated | 20000 |
| prev_only_rate | 0.400000 | 0.375602 | 0.280000 | 0.380000 | 0.480000 | 0.406880 | high_is_concentrated | 20000 |
| both_flanks_rate | 0.600000 | 0.624398 | 0.520000 | 0.620000 | 0.720000 | 0.708615 | high_is_concentrated | 20000 |

## Structure Counts

| metric | value |
| --- | --- |
| active_cells | 50.000000 |
| q2_active_cells | 11.000000 |
| s3_active_cells | 39.000000 |
| both_flanks_rate | 0.600000 |
| prev_only_rate | 0.400000 |
| flank_conflict_rate | 0.240000 |
| conflict_given_both_rate | 0.400000 |
| edge_or_near_edge_rate | 0.620000 |
| mean_min_flank_gap_days | 4.500000 |
| gap_le1_rate | 0.240000 |

## Interpretation

- Best flank-like prior: `edge_endpoint_beta` with beat-E95 probability `0.437780`.
- Subject prior beat-E95 probability: `0.337185`.
- Best flank expected delta per all cells: `0.000003014`.
- Subject expected delta per all cells: `0.000007853`.
- Train-label flank context materially improves the E101 hard-label prior over subject prior, but the expected delta is still positive. E101 is less of a pure public sensor than before, yet it is not locally certified.

## Decision

No submission is created. If E101 is submitted, this audit should be used as a
belief update, not as a post-hoc license to change branches:

- if E101 wins, the win strengthens an edge/flank transition-state reading of
  the `50` active cells and the E116 decoder should decide the E108 branch;
- if E101 ties or loses, the visible flank support was not strong enough to
  certify the file, so do not rescue the same rollback line by increasing
  amplitude or claiming train flanks had already proved it.
