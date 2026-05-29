# E105 E101 Public-Label Break-Even Anatomy

## Question

E101 is the next public sensor, but its public result will be meaningful only if
we know what hidden label world it tests. This audit asks which hard labels on
the `50` active Q2/S3 cells make E101 better or worse than E95.

## Result

- active cells: `50` (`Q2=11`, `S3=39`)
- support labels: `0 -> 25`, `1 -> 25`
- all-support E101-vs-E95 delta: `-0.000096679`
- all-adverse E101-vs-E95 delta: `0.000211677`
- minimum high-impact supportive cells to beat E95: `23` / `50`
- minimum high-impact supportive cells to match E95's mixmin edge: `25` / `50`

## Prior Simulation

| prior | mean_delta_vs_e95 | std_delta_vs_e95 | p_e101_beats_e95 | p_e101_beats_by_5e-6 | p_e101_matches_e95_edge_vs_mixmin | p_e101_worse_by_2e-5 | q05 | q50 | q95 | mean_support_probability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | 0.000048971 | 0.000023415 | 0.016610000 | 0.009195000 | 0.002165000 | 0.892395000 | 0.000010810 | 0.000048755 | 0.000087829 | 0.498000000 |
| subject | 0.000007854 | 0.000017643 | 0.335360000 | 0.237125000 | 0.090855000 | 0.242705000 | -0.000020450 | 0.000007382 | 0.000037582 | 0.587685814 |

## Break-Even Thresholds

| threshold | target_delta_per_all_cells | min_high_impact_support_cells | support_cell_fraction | achieved_delta_per_all_cells | selected_flip_benefit_share |
| --- | --- | --- | --- | --- | --- |
| beat_e95_zero_delta | 0.000000000 | 23 | 0.460000000 | -0.000001981 | 0.692894218 |
| beat_e95_by_1e-6 | -0.000001000 | 23 | 0.460000000 | -0.000001981 | 0.692894218 |
| beat_e95_by_5e-6 | -0.000005000 | 24 | 0.480000000 | -0.000009439 | 0.717081445 |
| match_e95_edge_vs_mixmin | -0.000015311 | 25 | 0.500000000 | -0.000016515 | 0.740028781 |
| all_support | -0.000096679 | 50 | 1.000000000 | -0.000096679 | 1.000000000 |

## Target Contribution

| target | active_cells | support_label_0 | support_label_1 | flip_benefit_share | support_delta_sum_per_all_cells | adverse_delta_sum_per_all_cells | subject_expected_delta_sum_per_all_cells |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | 11 | 5 | 6 | 0.064137678 | -0.000006815 | 0.000012962 | 0.000002109 |
| S3 | 39 | 20 | 19 | 0.935862322 | -0.000089863 | 0.000198715 | 0.000005744 |

## Top Swing Cells

| flip_rank | sub_idx | target | subject_id | sleep_date | hidden_block_id | edge_distance | prob_e95 | prob_e101 | support_label | support_delta | adverse_delta | flip_benefit | subject_support_probability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 133 | S3 | id06 | 2024-07-12 | id06_b2 | 2 | 0.943247384 | 0.944326117 | 1 | -0.001142984 | 0.019190605 | 0.020333589 | 0.958333333 |
| 2 | 145 | S3 | id06 | 2024-08-15 | id06_b8 | 0 | 0.955616433 | 0.956445354 | 1 | -0.000867044 | 0.018852912 | 0.019719957 | 0.958333333 |
| 3 | 141 | S3 | id06 | 2024-08-10 | id06_b6 | 0 | 0.956808096 | 0.957600666 | 1 | -0.000828006 | 0.018520428 | 0.019348433 | 0.958333333 |
| 4 | 39 | S3 | id02 | 2024-09-07 | id02_b2 | 3 | 0.903784994 | 0.905414332 | 1 | -0.001801170 | 0.017079366 | 0.018880536 | 0.895833333 |
| 5 | 215 | S3 | id09 | 2024-09-05 | id09_b4 | 0 | 0.708696874 | 0.712498468 | 1 | -0.005349867 | 0.013136205 | 0.018486072 | 0.707317073 |
| 6 | 146 | S3 | id06 | 2024-08-20 | id06_b10 | 0 | 0.953178426 | 0.953996412 | 1 | -0.000857798 | 0.017624674 | 0.018482472 | 0.958333333 |
| 7 | 235 | S3 | id10 | 2024-08-18 | id10_b2 | 3 | 0.461321485 | 0.465898211 | 1 | -0.009872014 | 0.008532508 | 0.018404522 | 0.484848485 |
| 8 | 120 | S3 | id05 | 2024-11-08 | id05_b6 | 0 | 0.125608785 | 0.123664435 | 0 | -0.002221193 | 0.015600471 | 0.017821665 | 0.863636364 |
| 9 | 241 | S3 | id10 | 2024-09-18 | id10_b4 | 2 | 0.487966691 | 0.483664160 | 0 | -0.008367726 | 0.008856365 | 0.017224092 | 0.515151515 |
| 10 | 8 | S3 | id01 | 2024-08-10 | id01_b2 | 5 | 0.856033082 | 0.858035670 | 1 | -0.002336649 | 0.014007706 | 0.016344355 | 0.853658537 |
| 11 | 57 | S3 | id02 | 2024-10-15 | id02_b4 | 1 | 0.900010687 | 0.901440219 | 1 | -0.001587090 | 0.014400030 | 0.015987120 | 0.895833333 |
| 12 | 12 | S3 | id01 | 2024-08-15 | id01_b2 | 1 | 0.866032842 | 0.867871650 | 1 | -0.002121004 | 0.013820884 | 0.015941888 | 0.853658537 |
| 13 | 129 | S3 | id06 | 2024-07-08 | id06_b2 | 1 | 0.937740258 | 0.938641017 | 1 | -0.000960102 | 0.014573440 | 0.015533543 | 0.958333333 |
| 14 | 86 | S3 | id04 | 2024-09-19 | id04_b6 | 0 | 0.512375952 | 0.508522809 | 0 | -0.007870816 | 0.007548567 | 0.015419382 | 0.456140351 |
| 15 | 144 | S3 | id06 | 2024-08-14 | id06_b8 | 1 | 0.935949828 | 0.936849502 | 1 | -0.000960780 | 0.014145977 | 0.015106756 | 0.958333333 |

## Interpretation

- E101 is not a global-prior bet. Under global train priors, the expected E101-vs-E95 delta is `0.000048971` and the Monte Carlo beat probability is `0.016610`.
- Under subject priors, E101 is much closer to a live sensor: expected delta `0.000007854` and beat probability `0.335360`.
- The risk is mostly S3: S3 owns `0.935862` of total flip benefit across active cells.
- If E101 improves public, the hidden public labels likely deviate from global priors toward subject/block-local Q2/S3 tail labels, especially S3. If E101 worsens, the Q2/S3 rollback branch is not supported by the realized public hard labels, and E104's higher-alpha variants should be demoted rather than amplified.
