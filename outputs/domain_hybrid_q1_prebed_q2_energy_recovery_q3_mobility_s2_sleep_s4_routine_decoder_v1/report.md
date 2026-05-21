# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.618005`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.663097 | 0.687527 | 0.667025 | 0.570959 | 0.576740 | 0.523927 | 0.636763 |

## Test-Time Source Selection

| target | selected_source | source_family | selection_action |
| --- | --- | --- | --- |
| Q1 | db_prebed__deviation__c0.1_b0.2 | digital_boundary_prebed | switch |
| Q2 | ef_recovery_slope__deviation__c0.3_b0.2 | energy_recovery_slope | switch |
| Q3 | best_plus_mobility_constriction__absolute__c0.1_b0.2 | mobility_constriction | switch |
| S1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S2 | best_plus_sleep_intrusion__absolute__c0.3_b0.2 | sleep_intrusion | switch |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S4 | routine_regularity__absolute_plus_deviation__c0.1_b0.2 | routine_regularity | switch |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.