# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.617784`
- Delta vs base: `-0.005407`
- Minimum train-fold improvement needed to switch: `0.000000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.656327 | 0.669182 | -0.012855 | best_plus_causal_chain_opportunity |
| Q2 | 0.699626 | 0.701693 | -0.002067 | best_plus_sleep_consensus_compact_rolling |
| Q3 | 0.674239 | 0.673889 | 0.000350 | mobility_constriction |
| S1 | 0.564710 | 0.570895 | -0.006186 | best_plus_wake_sleep_recovery_interaction |
| S2 | 0.574130 | 0.578316 | -0.004185 | sleep_consensus_micro_awakenings |
| S3 | 0.514926 | 0.525120 | -0.010194 | best_plus_sleep_onset_micro_subject_relative |
| S4 | 0.640534 | 0.643246 | -0.002713 | sleep_consensus_subject_relative |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | best_plus_causal_chain_opportunity | 5 |
| Q2 | best_plus_sleep_consensus_compact_rolling | 3 |
| Q2 | energy_recovery_slope | 2 |
| Q3 | mobility_constriction | 3 |
| Q3 | best_plus_causal_chain_recovery | 1 |
| Q3 | energy_recovery_slope | 1 |
| S1 | best_plus_wake_sleep_recovery_interaction | 4 |
| S1 | best_plus_wake_base_values | 1 |
| S2 | sleep_consensus_micro_awakenings | 3 |
| S2 | sleep_consensus_subject_relative | 2 |
| S3 | best_plus_sleep_onset_micro_subject_relative | 4 |
| S3 | best_plus_sleep_onset_micro_base_values | 1 |
| S4 | sleep_consensus_subject_relative | 3 |
| S4 | best_plus_causal_chain_interactions | 1 |
| S4 | best_plus_sleep_onset_consensus | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.