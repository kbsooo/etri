# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.623294`
- Delta vs base: `0.000102`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.668655 | 0.669182 | -0.000526 | routine_digital |
| Q2 | 0.699213 | 0.701693 | -0.002480 | best_late_fusion |
| Q3 | 0.673144 | 0.673889 | -0.000745 | routine_digital |
| S1 | 0.576622 | 0.570895 | 0.005727 | routine_digital |
| S2 | 0.575462 | 0.578316 | -0.002854 | routine_digital |
| S3 | 0.525120 | 0.525120 | 0.000000 | best_late_fusion |
| S4 | 0.644841 | 0.643246 | 0.001595 | routine_digital |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | routine_digital | 4 |
| Q1 | best_late_fusion | 1 |
| Q2 | best_late_fusion | 5 |
| Q3 | routine_digital | 4 |
| Q3 | best_late_fusion | 1 |
| S1 | routine_digital | 3 |
| S1 | best_late_fusion | 2 |
| S2 | routine_digital | 5 |
| S3 | best_late_fusion | 5 |
| S4 | routine_digital | 4 |
| S4 | best_late_fusion | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.