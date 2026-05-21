# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.625433`
- Delta vs base: `0.002241`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.673637 | 0.669182 | 0.004456 | best_late_fusion |
| Q2 | 0.703207 | 0.701693 | 0.001514 | best_late_fusion |
| Q3 | 0.666368 | 0.673889 | -0.007521 | mobility_constriction |
| S1 | 0.570895 | 0.570895 | 0.000000 | best_late_fusion |
| S2 | 0.588323 | 0.578316 | 0.010008 | best_late_fusion |
| S3 | 0.530800 | 0.525120 | 0.005680 | best_late_fusion |
| S4 | 0.644800 | 0.643246 | 0.001554 | best_late_fusion |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | best_late_fusion | 3 |
| Q1 | mobility_constriction | 2 |
| Q2 | best_late_fusion | 4 |
| Q2 | mobility_constriction | 1 |
| Q3 | mobility_constriction | 5 |
| S1 | best_late_fusion | 5 |
| S2 | best_late_fusion | 3 |
| S2 | mobility_constriction | 2 |
| S3 | best_late_fusion | 4 |
| S3 | mobility_constriction | 1 |
| S4 | best_late_fusion | 4 |
| S4 | mobility_constriction | 1 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.