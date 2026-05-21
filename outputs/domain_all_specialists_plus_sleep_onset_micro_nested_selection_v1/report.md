# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.619146`
- Delta vs base: `-0.004045`
- Minimum train-fold improvement needed to switch: `0.000000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.656327 | 0.669182 | -0.012855 | best_plus_causal_chain_opportunity |
| Q2 | 0.695155 | 0.701693 | -0.006538 | energy_recovery_slope |
| Q3 | 0.674239 | 0.673889 | 0.000350 | mobility_constriction |
| S1 | 0.574064 | 0.570895 | 0.003168 | best_plus_causal_chain_opportunity |
| S2 | 0.574198 | 0.578316 | -0.004117 | best_plus_causal_chain_opportunity |
| S3 | 0.514926 | 0.525120 | -0.010194 | best_plus_sleep_onset_micro_subject_relative |
| S4 | 0.645116 | 0.643246 | 0.001870 | best_plus_sleep_onset_consensus |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | best_plus_causal_chain_opportunity | 5 |
| Q2 | energy_recovery_slope | 4 |
| Q2 | best_plus_digital_isolation_prebed | 1 |
| Q3 | mobility_constriction | 3 |
| Q3 | best_plus_causal_chain_recovery | 1 |
| Q3 | energy_recovery_slope | 1 |
| S1 | best_plus_causal_chain_opportunity | 4 |
| S1 | best_plus_digital_isolation_rhythm | 1 |
| S2 | best_plus_causal_chain_opportunity | 4 |
| S2 | best_plus_sleep_onset_fragmentation | 1 |
| S3 | best_plus_sleep_onset_micro_subject_relative | 4 |
| S3 | best_plus_sleep_onset_micro_base_values | 1 |
| S4 | best_plus_causal_chain_interactions | 2 |
| S4 | best_plus_sleep_onset_consensus | 2 |
| S4 | sleep_onset_fragmentation | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.