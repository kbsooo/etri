# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_sbc_no_wear_episode__absolute__c0.1_b0.2`
- Avg logloss: `0.623313`
- Delta vs subject prior: `-0.004341`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_sbc_no_wear_episode__absolute__c0.1_b0.2 | 0.623313 | 0.665824 | 0.700331 | 0.671406 | 0.570008 | 0.577751 | 0.532327 | 0.645541 |
| best_plus_sbc_no_wear_episode__absolute_plus_deviation__c0.1_b0.2 | 0.623381 | 0.666672 | 0.703181 | 0.671166 | 0.568189 | 0.579937 | 0.530049 | 0.644475 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best_plus_sbc_no_wear_episode__absolute_plus_deviation__c0.03_b0.2 | 0.624106 | 0.667792 | 0.702209 | 0.672540 | 0.568538 | 0.578848 | 0.534364 | 0.644449 |
| best_plus_sbc_no_wear_episode__absolute__c0.03_b0.2 | 0.624331 | 0.666810 | 0.701127 | 0.672608 | 0.571069 | 0.578036 | 0.535791 | 0.644874 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |
| best_plus_sbc_no_wear_episode__absolute__c0.1_b0.1 | 0.624833 | 0.668722 | 0.701877 | 0.674082 | 0.572237 | 0.578398 | 0.532769 | 0.645746 |
| best_plus_sbc_no_wear_episode__deviation__c0.1_b0.2 | 0.624883 | 0.667280 | 0.700620 | 0.668758 | 0.571102 | 0.582017 | 0.537564 | 0.646840 |
| best_plus_sbc_no_wear_episode__absolute_plus_deviation__c0.1_b0.1 | 0.624910 | 0.669245 | 0.703359 | 0.673927 | 0.571297 | 0.579541 | 0.531660 | 0.645341 |
| best__deviation__c0.1_b0.2 | 0.624960 | 0.669308 | 0.698063 | 0.671486 | 0.572623 | 0.580822 | 0.537461 | 0.644954 |
| best_plus_sbc_boundary_recoverage__absolute__c0.1_b0.2 | 0.625085 | 0.667814 | 0.708419 | 0.670645 | 0.580590 | 0.574880 | 0.529984 | 0.643265 |
| best__absolute_plus_deviation__c0.03_b0.2 | 0.625131 | 0.671186 | 0.699156 | 0.673795 | 0.571766 | 0.579118 | 0.536996 | 0.643899 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.