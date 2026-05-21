# Nested Temporal Decoder

## Purpose

Materialize nested source-selection diagnostics as OOF and test prediction files.

## OOF Score

- Avg logloss: `0.621238`

## Per Target

| Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.668986 | 0.696142 | 0.668048 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |

## Test-Time Source Selection

| target | selected_source | source_family | raw_best_source | raw_best_selector_loss | base_selector_loss | selector_loss | selection_action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__deviation__c0.3_b0.2 | 0.668691 | 0.669182 | 0.669182 | base |
| Q2 | td_trajectory__deviation__c0.3_b0.2 | trajectory | td_trajectory__deviation__c0.3_b0.2 | 0.691913 | 0.701693 | 0.691913 | switch |
| Q3 | td_trajectory__deviation__c0.03_b0.2 | trajectory | td_trajectory__deviation__c0.03_b0.2 | 0.667135 | 0.673889 | 0.667135 | switch |
| S1 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__absolute_plus_deviation__c0.3_b0.2 | 0.570895 | 0.570895 | 0.570895 | base |
| S2 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__absolute__c0.3_b0.2 | 0.578113 | 0.578316 | 0.578316 | base |
| S3 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__absolute_plus_deviation__c0.3_b0.2 | 0.525120 | 0.525120 | 0.525120 | base |
| S4 | best__absolute_plus_deviation__c0.3_b0.2 | best_late_fusion | best__absolute_plus_deviation__c0.1_b0.2 | 0.643205 | 0.643246 | 0.643246 | base |

## Read

Only targets listed in the source-selection table move away from the current best late-fusion source.