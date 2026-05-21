# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.619428`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.665349 | 0.695230 | 0.667025 | 0.570959 | 0.576740 | 0.523927 | 0.636763 |

## Test-Time Source Selection

| target | selected_source | source_family | selection_action |
| --- | --- | --- | --- |
| Q1 | sfr_sleep_sensor__deviation__c0.1_b0.2 | sleep_fragment_recovery_sleep_sensor | switch |
| Q2 | best_plus_trajectory_proto__deviation__c0.03_b0.2 | trajectory_proto | switch |
| Q3 | best_plus_mobility_constriction__absolute__c0.1_b0.2 | mobility_constriction | switch |
| S1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S2 | best_plus_sleep_intrusion__absolute__c0.3_b0.2 | sleep_intrusion | switch |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S4 | routine_regularity__absolute_plus_deviation__c0.1_b0.2 | routine_regularity | switch |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.