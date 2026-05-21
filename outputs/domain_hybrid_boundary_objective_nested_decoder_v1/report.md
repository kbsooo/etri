# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.618663`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.654680 | 0.700904 | 0.671657 | 0.564816 | 0.579388 | 0.513728 | 0.645469 |

## Test-Time Source Selection

| target | selected_source | source_family | raw_best_source | raw_best_selector_loss | base_selector_loss | selector_loss | selection_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | boundary_target_map__absolute__c0.03_b0.2 | boundary_target_map | boundary_target_map__absolute__c0.03_b0.2 | 0.653762 | 0.669182 | 0.653762 | switch |
| Q2 | best_plus_scc_rolling__absolute__c0.3_b0.2 | best_plus_sleep_consensus_compact_rolling | best_plus_scc_rolling__absolute__c0.3_b0.2 | 0.682062 | 0.701693 | 0.682062 | switch |
| Q3 | best_plus_mobility_constriction__absolute__c0.1_b0.2 | mobility_constriction | best_plus_mobility_constriction__absolute__c0.1_b0.2 | 0.664158 | 0.673889 | 0.664158 | switch |
| S1 | best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2 | best_plus_wake_sleep_recovery_interaction | best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2 | 0.557172 | 0.570895 | 0.557172 | switch |
| S2 | boundary_target_map__absolute__c0.03_b0.2 | boundary_target_map | boundary_target_map__absolute__c0.03_b0.2 | 0.569721 | 0.578316 | 0.569721 | switch |
| S3 | best_plus_sot_micro_subject_relative_only__absolute_plus_deviation__c0.3_b0.2 | best_plus_sleep_onset_micro_subject_relative | best_plus_sot_micro_subject_relative_only__absolute_plus_deviation__c0.3_b0.2 | 0.513590 | 0.525120 | 0.513590 | switch |
| S4 | best_plus_sot_onset_consensus__absolute__c0.03_b0.2 | best_plus_sleep_onset_consensus | best_plus_sot_onset_consensus__absolute__c0.03_b0.2 | 0.635555 | 0.643246 | 0.635555 | switch |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.