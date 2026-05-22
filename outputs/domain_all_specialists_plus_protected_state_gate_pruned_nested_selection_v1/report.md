# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.619622`
- Delta vs base: `-0.003570`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.658421 | 0.669182 | -0.010761 | boundary_target_map |
| Q2 | 0.700396 | 0.701693 | -0.001297 | best_plus_sleep_consensus_compact_rolling |
| Q3 | 0.674081 | 0.673889 | 0.000192 | mobility_constriction |
| S1 | 0.569862 | 0.570895 | -0.001033 | best_plus_wake_sleep_recovery_interaction |
| S2 | 0.581975 | 0.578316 | 0.003660 | protected_state_gate |
| S3 | 0.514926 | 0.525120 | -0.010194 | best_plus_sleep_onset_micro_subject_relative |
| S4 | 0.637691 | 0.643246 | -0.005556 | protected_state_gate |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | boundary_target_map | 4 |
| Q1 | best_plus_s2cmi | 1 |
| Q2 | best_plus_sleep_consensus_compact_rolling | 2 |
| Q2 | boundary_target_map | 2 |
| Q2 | best_plus_digital_isolation_social | 1 |
| Q3 | best_plus_s4_routine_fragment | 2 |
| Q3 | mobility_constriction | 2 |
| Q3 | rr_mobility_body_rhythm | 1 |
| S1 | best_plus_wake_sleep_recovery_interaction | 3 |
| S1 | best_plus_rr_long_rolling_volatility | 1 |
| S1 | best_plus_wake_base_values | 1 |
| S2 | protected_state_gate | 2 |
| S2 | best_plus_rr_sleep_regular_break | 1 |
| S2 | s4_routine_fragment | 1 |
| S2 | sleep_consensus_subject_relative | 1 |
| S3 | best_plus_sleep_onset_micro_subject_relative | 4 |
| S3 | best_plus_sleep_onset_micro_base_values | 1 |
| S4 | protected_state_gate | 3 |
| S4 | best_plus_rr_coverage_rhythm | 1 |
| S4 | best_plus_rr_sleep_regular_break | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.