# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_scc_rolling__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.620983`
- Delta vs subject prior: `-0.006670`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_scc_rolling__absolute_plus_deviation__c0.3_b0.2 | 0.620983 | 0.664138 | 0.686604 | 0.672675 | 0.572558 | 0.579882 | 0.528418 | 0.642610 |
| best_plus_scc_rolling__deviation__c0.3_b0.2 | 0.621145 | 0.662522 | 0.684022 | 0.670568 | 0.573462 | 0.580767 | 0.535648 | 0.641030 |
| best_plus_scc_subject_relative__absolute__c0.3_b0.2 | 0.621148 | 0.660671 | 0.705263 | 0.672977 | 0.569109 | 0.571646 | 0.525472 | 0.642901 |
| best_plus_scc_rolling__absolute_plus_deviation__c0.1_b0.2 | 0.621365 | 0.664051 | 0.686426 | 0.673432 | 0.571554 | 0.579617 | 0.533667 | 0.640812 |
| best_plus_scc_all__deviation__c0.3_b0.2 | 0.621379 | 0.662707 | 0.688655 | 0.677774 | 0.571100 | 0.573448 | 0.529488 | 0.646484 |
| best_plus_scc_subject_relative__deviation__c0.3_b0.2 | 0.621504 | 0.660296 | 0.706229 | 0.674240 | 0.568952 | 0.573265 | 0.525354 | 0.642195 |
| best_plus_scc_all__absolute_plus_deviation__c0.3_b0.2 | 0.621515 | 0.662604 | 0.691369 | 0.677484 | 0.571396 | 0.574042 | 0.527118 | 0.646589 |
| best_plus_scc_all__absolute__c0.3_b0.2 | 0.621549 | 0.662171 | 0.692381 | 0.677667 | 0.572601 | 0.571720 | 0.529476 | 0.644826 |
| best_plus_scc_subject_relative__absolute_plus_deviation__c0.3_b0.2 | 0.621735 | 0.662042 | 0.705580 | 0.675036 | 0.569701 | 0.575028 | 0.521923 | 0.642837 |
| best_plus_scc_all__absolute_plus_deviation__c0.1_b0.2 | 0.621805 | 0.663764 | 0.693007 | 0.678916 | 0.570764 | 0.572879 | 0.529866 | 0.643438 |
| best_plus_scc_subject_relative__absolute_plus_deviation__c0.1_b0.2 | 0.622070 | 0.662608 | 0.706645 | 0.676096 | 0.570000 | 0.573143 | 0.525195 | 0.640806 |
| best_plus_scc_subject_relative__absolute__c0.1_b0.2 | 0.622074 | 0.662748 | 0.705929 | 0.674995 | 0.570924 | 0.570222 | 0.528971 | 0.640729 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.