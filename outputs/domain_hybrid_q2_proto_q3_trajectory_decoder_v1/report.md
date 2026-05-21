# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.621107`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.668986 | 0.695230 | 0.668048 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |

## Test-Time Source Selection

| target | selected_source | source_family | selection_action |
| --- | --- | --- | --- |
| Q1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| Q2 | best_plus_trajectory_proto__deviation__c0.03_b0.2 | trajectory_proto | switch |
| Q3 | td_trajectory__deviation__c0.03_b0.2 | trajectory | switch |
| S1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S2 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S4 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.