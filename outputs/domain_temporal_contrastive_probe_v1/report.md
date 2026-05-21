# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `adjacent_subject_token_event_cross_missing__absolute__c0.3_b0.1`
- Avg logloss: `0.626525`
- Delta vs subject prior: `-0.001129`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| adjacent_subject_token_event_cross_missing__absolute__c0.3_b0.1 | 0.626525 | 0.671413 | 0.701796 | 0.673465 | 0.577392 | 0.578910 | 0.537529 | 0.645169 |
| adjacent_subject_token_event_cross_missing__deviation__c0.3_b0.1 | 0.626555 | 0.671295 | 0.700187 | 0.674044 | 0.577602 | 0.579763 | 0.537292 | 0.645705 |
| adjacent_subject_token_event_cross_missing__absolute__c0.1_b0.1 | 0.626639 | 0.671812 | 0.701512 | 0.673699 | 0.577067 | 0.579234 | 0.537867 | 0.645282 |
| adjacent_global_event_cross_missing__absolute__c0.03_b0.1 | 0.626641 | 0.670974 | 0.699747 | 0.674205 | 0.576113 | 0.580600 | 0.538389 | 0.646459 |
| adjacent_subject_token_only_event__deviation__c0.3_b0.1 | 0.626670 | 0.672689 | 0.697694 | 0.678727 | 0.572557 | 0.581152 | 0.534033 | 0.649839 |
| adjacent_subject_token_event_cross_missing__deviation__c0.3_b0.2 | 0.626679 | 0.670518 | 0.696639 | 0.671151 | 0.580508 | 0.581105 | 0.541455 | 0.645374 |
| adjacent_global_event_cross_missing__absolute__c0.1_b0.1 | 0.626700 | 0.670673 | 0.699948 | 0.673791 | 0.576258 | 0.581414 | 0.537959 | 0.646859 |
| same_global_event_cross_missing__absolute__c0.3_b0.1 | 0.626736 | 0.670938 | 0.701808 | 0.672268 | 0.576234 | 0.581518 | 0.537819 | 0.646564 |
| same_global_event_cross_missing__deviation__c0.3_b0.1 | 0.626746 | 0.671850 | 0.702094 | 0.674970 | 0.575759 | 0.580670 | 0.535680 | 0.646203 |
| adjacent_subject_token_event_cross_missing__deviation__c0.1_b0.1 | 0.626763 | 0.671603 | 0.700047 | 0.674153 | 0.577389 | 0.580215 | 0.538063 | 0.645872 |
| adjacent_subject_token_only_event__deviation__c0.1_b0.1 | 0.626768 | 0.672728 | 0.697510 | 0.678023 | 0.573804 | 0.580985 | 0.534972 | 0.649355 |
| same_global_event_cross_missing__deviation__c0.1_b0.1 | 0.626779 | 0.671717 | 0.701289 | 0.675258 | 0.575818 | 0.580628 | 0.536402 | 0.646344 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.