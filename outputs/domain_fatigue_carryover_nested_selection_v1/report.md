# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.626132`
- Delta vs base: `0.002940`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.675452 | 0.669182 | 0.006270 | fatigue_carryover |
| Q2 | 0.699213 | 0.701693 | -0.002480 | best_late_fusion |
| Q3 | 0.679733 | 0.673889 | 0.005845 | best_late_fusion |
| S1 | 0.574791 | 0.570895 | 0.003895 | best_late_fusion |
| S2 | 0.578316 | 0.578316 | 0.000000 | best_late_fusion |
| S3 | 0.525120 | 0.525120 | 0.000000 | best_late_fusion |
| S4 | 0.650296 | 0.643246 | 0.007049 | best_late_fusion |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | fatigue_carryover | 3 |
| Q1 | best_late_fusion | 2 |
| Q2 | best_late_fusion | 5 |
| Q3 | best_late_fusion | 4 |
| Q3 | fatigue_carryover | 1 |
| S1 | best_late_fusion | 3 |
| S1 | fatigue_carryover | 2 |
| S2 | best_late_fusion | 5 |
| S3 | best_late_fusion | 5 |
| S4 | best_late_fusion | 3 |
| S4 | fatigue_carryover | 2 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.