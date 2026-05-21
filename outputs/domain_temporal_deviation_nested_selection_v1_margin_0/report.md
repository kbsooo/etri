# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.623061`
- Delta vs base: `-0.000131`
- Minimum train-fold improvement needed to switch: `0.000000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.667090 | 0.669182 | -0.002092 | future |
| Q2 | 0.697723 | 0.701693 | -0.003970 | trajectory |
| Q3 | 0.668035 | 0.673889 | -0.005854 | trajectory |
| S1 | 0.571673 | 0.570895 | 0.000777 | best_late_fusion |
| S2 | 0.582941 | 0.578316 | 0.004626 | future |
| S3 | 0.525120 | 0.525120 | 0.000000 | best_late_fusion |
| S4 | 0.648844 | 0.643246 | 0.005598 | best_late_fusion |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | future | 5 |
| Q2 | trajectory | 4 |
| Q2 | recovery | 1 |
| Q3 | trajectory | 5 |
| S1 | best_late_fusion | 5 |
| S2 | future | 4 |
| S2 | past | 1 |
| S3 | best_late_fusion | 5 |
| S4 | best_late_fusion | 5 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.