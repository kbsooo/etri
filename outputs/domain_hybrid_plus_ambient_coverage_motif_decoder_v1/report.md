# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.623065`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.663097 | 0.687527 | 0.672112 | 0.571851 | 0.583867 | 0.529670 | 0.653331 |

## Test-Time Source Selection

| target | selected_source | source_family | raw_best_source | raw_best_selector_loss | base_selector_loss | selector_loss | selection_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | db_prebed__deviation__c0.1_b0.2 | digital_boundary_prebed | db_prebed__deviation__c0.1_b0.2 | 0.662936 | 0.669182 | 0.662936 | switch |
| Q2 | ef_recovery_slope__deviation__c0.3_b0.2 | energy_recovery_slope | ef_recovery_slope__deviation__c0.3_b0.2 | 0.683678 | 0.701693 | 0.683678 | switch |
| Q3 | best_plus_mobility_constriction__absolute__c0.1_b0.2 | mobility_constriction | best_plus_mobility_constriction__absolute__c0.1_b0.2 | 0.664158 | 0.673889 | 0.664158 | switch |
| S1 | best_plus_routine_regularity__absolute__c0.3_b0.2 | routine_regularity | best_plus_routine_regularity__absolute__c0.3_b0.2 | 0.562656 | 0.570895 | 0.562656 | switch |
| S2 | best_plus_sleep_intrusion__absolute__c0.3_b0.2 | sleep_intrusion | best_plus_sleep_intrusion__absolute__c0.3_b0.2 | 0.570610 | 0.578316 | 0.570610 | switch |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__absolute_plus_deviation__c0.3_b0.2 | 0.525120 | 0.525120 | 0.525120 | base |
| S4 | routine_regularity__absolute_plus_deviation__c0.1_b0.2 | routine_regularity | routine_regularity__absolute_plus_deviation__c0.1_b0.2 | 0.634713 | 0.643246 | 0.634713 | switch |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.