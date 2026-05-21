# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.614468`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.654835 | 0.687527 | 0.667025 | 0.563862 | 0.568897 | 0.523927 | 0.635204 |

## Test-Time Source Selection

| target | selected_source | source_family | selection_action |
| --- | --- | --- | --- |
| Q1 | best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.2 | fixed_causal_chain | fixed_replace |
| Q2 | ef_recovery_slope__deviation__c0.3_b0.2 | energy_recovery_slope | switch |
| Q3 | best_plus_mobility_constriction__absolute__c0.1_b0.2 | mobility_constriction | switch |
| S1 | best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.2 | fixed_causal_chain | fixed_replace |
| S2 | best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.2 | fixed_causal_chain | fixed_replace |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | base |
| S4 | best_plus_cc_chain_interactions__absolute__c0.3_b0.2 | fixed_causal_chain | fixed_replace |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.