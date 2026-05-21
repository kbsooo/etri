# Nested Source Selection Diagnostics

## Purpose

Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.

## Overall

- Base source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg fold loss: `0.623192`
- Nested selected avg fold loss: `0.623440`
- Delta vs base: `0.000248`
- Minimum train-fold improvement needed to switch: `0.003000`

## Target Summary

| target | selected_loss | base_loss | delta_vs_base | most_common_family |
| --- | --- | --- | --- | --- |
| Q1 | 0.670935 | 0.669182 | 0.001753 | sleep_intrusion |
| Q2 | 0.700763 | 0.701693 | -0.000930 | best_late_fusion |
| Q3 | 0.674820 | 0.673889 | 0.000931 | best_late_fusion |
| S1 | 0.570895 | 0.570895 | 0.000000 | best_late_fusion |
| S2 | 0.577340 | 0.578316 | -0.000976 | sleep_intrusion |
| S3 | 0.525120 | 0.525120 | 0.000000 | best_late_fusion |
| S4 | 0.644206 | 0.643246 | 0.000959 | sleep_intrusion |

## Selected Family Counts

| target | source_family | size |
| --- | --- | --- |
| Q1 | sleep_intrusion | 4 |
| Q1 | best_late_fusion | 1 |
| Q2 | best_late_fusion | 3 |
| Q2 | sleep_intrusion | 2 |
| Q3 | best_late_fusion | 5 |
| S1 | best_late_fusion | 5 |
| S2 | sleep_intrusion | 5 |
| S3 | best_late_fusion | 5 |
| S4 | sleep_intrusion | 3 |
| S4 | best_late_fusion | 2 |

## Read

A negative delta means the family choice still helps after the held fold is hidden during source selection.
A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.