# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.625410`
- Delta vs base: `0.002218`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.665733 | 0.669182 | -0.003448 | sleep_fragment_recovery_sleep_sensor |
| Q2 | 0.702939 | 0.701693 | 0.001246 | trajectory_proto |
| Q3 | 0.673620 | 0.673889 | -0.000269 | mobility_constriction |
| S1 | 0.575389 | 0.570895 | 0.004494 | routine_regularity |
| S2 | 0.584886 | 0.578316 | 0.006570 | sleep_intrusion |
| S3 | 0.530800 | 0.525120 | 0.005680 | best_late_fusion |
| S4 | 0.644500 | 0.643246 | 0.001254 | routine_regularity |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | sleep_fragment_recovery_sleep_sensor | 4 |
| Q1 | digital_boundary_prebed | 1 |
| Q2 | trajectory_proto | 4 |
| Q2 | digital_boundary_prebed | 1 |
| Q3 | mobility_constriction | 3 |
| Q3 | sleep_fragment_recovery_core | 2 |
| S1 | routine_regularity | 4 |
| S1 | sleep_fragment_recovery_sleep_sensor | 1 |
| S2 | sleep_intrusion | 4 |
| S2 | routine_regularity | 1 |
| S3 | best_late_fusion | 4 |
| S3 | mobility_constriction | 1 |
| S4 | routine_regularity | 4 |
| S4 | sleep_intrusion | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.