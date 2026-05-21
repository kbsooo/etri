# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.623695`
- Delta vs base: `0.000504`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.658087 | 0.669182 | -0.011095 | best_plus_causal_chain_opportunity |
| Q2 | 0.695155 | 0.701693 | -0.006538 | energy_recovery_slope |
| Q3 | 0.674239 | 0.673889 | 0.000350 | mobility_constriction |
| S1 | 0.577622 | 0.570895 | 0.006726 | routine_regularity |
| S2 | 0.584269 | 0.578316 | 0.005953 | sleep_intrusion |
| S3 | 0.530800 | 0.525120 | 0.005680 | best_late_fusion |
| S4 | 0.645697 | 0.643246 | 0.002450 | routine_regularity |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | best_plus_causal_chain_opportunity | 4 |
| Q1 | causal_chain_opportunity | 1 |
| Q2 | energy_recovery_slope | 4 |
| Q2 | best_plus_digital_isolation_prebed | 1 |
| Q3 | mobility_constriction | 3 |
| Q3 | best_plus_causal_chain_recovery | 1 |
| Q3 | energy_recovery_slope | 1 |
| S1 | routine_regularity | 4 |
| S1 | best_plus_digital_isolation_rhythm | 1 |
| S2 | sleep_intrusion | 3 |
| S2 | best_plus_causal_chain_opportunity | 1 |
| S2 | routine_regularity | 1 |
| S3 | best_late_fusion | 4 |
| S3 | mobility_constriction | 1 |
| S4 | routine_regularity | 3 |
| S4 | best_plus_causal_chain_interactions | 1 |
| S4 | sleep_intrusion | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.