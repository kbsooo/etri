# E102 E101 Active-Cell Structure Audit

## Question

E101 changes only Q2/S3 cells relative to E95. This audit asks whether those
cells are a hidden block/subject/calendar subset or just the cells where E95
differs from mixmin on Q2/S3.

## Core Counts

| metric | value |
| --- | --- |
| eligible_q2s3_cells | 500.000000 |
| e101_active_cells | 50.000000 |
| e101_active_rows | 48.000000 |
| e101_active_blocks | 26.000000 |
| e101_active_subjects | 10.000000 |
| q2_active_cells | 11.000000 |
| s3_active_cells | 39.000000 |
| e95_mixmin_active_q2s3_cells | 50.000000 |
| max_active_cells_per_block | 4.000000 |
| blocks_with_ge3_active_cells | 9.000000 |
| min_perm_p | 0.016999 |

## Active By Target

| target | cells | rows |
| --- | --- | --- |
| Q2 | 11 | 11 |
| S3 | 39 | 39 |

Rollback shrink fraction to mixmin among active cells: `mean=0.250000, min=0.250000, max=0.250000`.

## Top Active Blocks

| hidden_block_id | subject_id | context_type | block_n_rows | active_cells | active_rows | active_q2 | active_s3 | active_cell_rate_q2s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id02_b4 | id02 | after_train_run | 16 | 4 | 4 | 0 | 4 | 0.125000 |
| id07_b4 | id07 | after_train_run | 15 | 4 | 4 | 3 | 1 | 0.133333 |
| id04_b6 | id04 | between_train_runs | 8 | 4 | 4 | 0 | 4 | 0.250000 |
| id02_b2 | id02 | between_train_runs | 16 | 3 | 3 | 0 | 3 | 0.093750 |
| id01_b2 | id01 | between_train_runs | 14 | 3 | 3 | 0 | 3 | 0.107143 |
| id01_b4 | id01 | after_train_run | 13 | 3 | 3 | 0 | 3 | 0.115385 |
| id10_b4 | id10 | after_train_run | 11 | 3 | 3 | 1 | 2 | 0.136364 |
| id06_b2 | id06 | between_train_runs | 8 | 3 | 3 | 1 | 2 | 0.187500 |
| id04_b8 | id04 | between_train_runs | 6 | 3 | 2 | 2 | 1 | 0.250000 |
| id06_b10 | id06 | after_train_run | 6 | 2 | 2 | 0 | 2 | 0.166667 |
| id06_b8 | id06 | between_train_runs | 4 | 2 | 2 | 0 | 2 | 0.250000 |
| id04_b14 | id04 | after_train_run | 3 | 2 | 1 | 1 | 1 | 0.333333 |

## Strongest Enrichments

| unit | field | value | active | total_in_group | expected_active | lift | z |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cell | target | S3 | 39 | 250 | 25.000000 | 1.560000 | 3.959798 |
| row | subject_id | id06 | 9 | 24 | 4.608000 | 1.953125 | 2.151899 |
| cell | subject_id | id04 | 10 | 54 | 5.400000 | 1.851852 | 2.095938 |
| row | hidden_block_id | id04_b6 | 4 | 8 | 1.536000 | 2.604167 | 2.020726 |
| cell | subject_id | id06 | 9 | 48 | 4.800000 | 1.875000 | 2.016250 |
| cell | hidden_block_id | id04_b6 | 4 | 16 | 1.600000 | 2.500000 | 1.928473 |
| cell | hidden_block_id | id04_b14 | 2 | 6 | 0.600000 | 3.333333 | 1.818335 |
| cell | pos_bin | near_edge | 15 | 100 | 10.000000 | 1.500000 | 1.767767 |
| cell | hidden_block_id | id04_b8 | 3 | 12 | 1.200000 | 2.500000 | 1.663248 |
| row | pos_bin | near_edge | 14 | 50 | 9.600000 | 1.458333 | 1.587713 |
| cell | pos_bin | left_edge | 10 | 64 | 6.400000 | 1.562500 | 1.523892 |
| row | hidden_block_id | id06_b8 | 2 | 4 | 0.768000 | 2.604167 | 1.417205 |
| cell | hidden_block_id | id06_b8 | 2 | 8 | 0.800000 | 2.500000 | 1.352504 |
| cell | block_len_bin | 6-10 | 14 | 102 | 10.200000 | 1.372549 | 1.333604 |
| row | subject_id | id04 | 8 | 27 | 5.184000 | 1.543210 | 1.309537 |

## Target-Count Permutation Null

| metric | observed | null_mean | null_p05 | null_p50 | null_p95 | p_one_sided | direction | n_perm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| edge_or_near_edge_rate | 0.620000 | 0.471289 | 0.360000 | 0.480000 | 0.580000 | 0.016999 | high_is_concentrated | 20000 |
| mean_edge_distance | 1.680000 | 2.138444 | 1.720000 | 2.140000 | 2.580000 | 0.040848 | low_is_concentrated | 20000 |
| max_cells_per_subject | 10.000000 | 8.750000 | 7.000000 | 9.000000 | 11.000000 | 0.248838 | high_is_concentrated | 20000 |
| n_rows_touched | 48.000000 | 48.278300 | 46.000000 | 48.000000 | 50.000000 | 0.536323 | low_is_concentrated | 20000 |
| rows_with_both_targets | 2.000000 | 1.721700 | 0.000000 | 2.000000 | 4.000000 | 0.536323 | high_is_concentrated | 20000 |
| weekend_rate | 0.260000 | 0.271650 | 0.180000 | 0.280000 | 0.360000 | 0.639268 | high_is_concentrated | 20000 |
| between_train_runs_rate | 0.600000 | 0.624398 | 0.520000 | 0.620000 | 0.720000 | 0.708615 | high_is_concentrated | 20000 |
| max_cells_per_row | 2.000000 | 1.849700 | 1.000000 | 2.000000 | 2.000000 | 0.849708 | high_is_concentrated | 20000 |

## Interpretation

- Active cells touch `26` hidden submission blocks, `10` subjects, and `48` rows.
- The largest hidden block contains `4` active Q2/S3 cells.
- Strongest permutation p-value is `0.016999`.
- E101 has weak-to-moderate structure concentration. Treat it as an amplitude sensor, but keep block-local rollback as the next falsification if public improves.

## Decision

If E101 improves public, use this audit to decide the follow-up:

- strong concentration: test a block/subject-local E95 rollback mask;
- weak concentration: test a target-axis amplitude line around E101;
- no concentration: do not search handcrafted row masks; move back to block-state JEPA representation.

If E101 worsens public, this audit helps decide whether the failure kills only
generic Q2/S3 amplitude rollback or also the hidden-block-local rollback idea.
