# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.610257`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.654680 | 0.682902 | 0.665238 | 0.557111 | 0.566343 | 0.512376 | 0.633149 |

## Test-Time Source Selection

| target | selected_source | source_family | selection_action |
| --- | --- | --- | --- |
| Q1 | boundary_target_map__absolute__c0.03_b0.2 | boundary_target_map | fixed_q1_boundary_swap |
| Q2 | best_plus_scc_rolling__absolute__c0.3_b0.2 | fixed_sleep_consensus_compact_rolling_probe | fixed_probe_replace |
| Q3 | best_plus_cc_recovery__deviation__c0.3_b0.2 | fixed_causal_chain | fixed_replace |
| S1 | best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2 | fixed_wake_sleep_recovery_interaction | fixed_replace |
| S2 | scp_subject_relative_only__absolute_plus_deviation__c0.03_b0.2 | fixed_sleep_consensus_subject_relative_probe | fixed_probe_replace |
| S3 | best_plus_sot_micro_subject_relative_only__absolute_plus_deviation__c0.3_b0.2 | fixed_sleep_onset_subject_relative | fixed_replace |
| S4 | scp_subject_relative_only__absolute__c0.1_b0.2 | fixed_sleep_consensus_subject_relative_probe | fixed_probe_replace |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.