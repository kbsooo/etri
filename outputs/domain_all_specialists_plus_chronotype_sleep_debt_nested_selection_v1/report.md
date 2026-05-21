# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.624955`
- Delta vs base: `0.001763`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.663354 | 0.669182 | -0.005827 | digital_boundary_prebed |
| Q2 | 0.702939 | 0.701693 | 0.001246 | trajectory_proto |
| Q3 | 0.666368 | 0.673889 | -0.007521 | mobility_constriction |
| S1 | 0.571877 | 0.570895 | 0.000981 | routine_regularity |
| S2 | 0.592294 | 0.578316 | 0.013979 | chronotype_sleep_debt |
| S3 | 0.530800 | 0.525120 | 0.005680 | best_late_fusion |
| S4 | 0.647049 | 0.643246 | 0.003803 | routine_regularity |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | digital_boundary_prebed | 5 |
| Q2 | trajectory_proto | 4 |
| Q2 | digital_boundary_prebed | 1 |
| Q3 | mobility_constriction | 5 |
| S1 | routine_regularity | 4 |
| S1 | best_late_fusion | 1 |
| S2 | chronotype_sleep_debt | 2 |
| S2 | sleep_intrusion | 2 |
| S2 | routine_regularity | 1 |
| S3 | best_late_fusion | 4 |
| S3 | mobility_constriction | 1 |
| S4 | routine_regularity | 3 |
| S4 | chronotype_sleep_debt | 2 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.