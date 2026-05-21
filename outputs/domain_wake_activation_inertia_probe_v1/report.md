# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.622961`
- Delta vs subject prior: `-0.004693`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2 | 0.624499 | 0.666933 | 0.698534 | 0.671879 | 0.568551 | 0.578625 | 0.537363 | 0.649611 |
| wai_sleep_recovery_interaction__absolute__c0.3_b0.2 | 0.624576 | 0.667670 | 0.696692 | 0.671973 | 0.570016 | 0.577775 | 0.539726 | 0.648179 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| wai_sleep_recovery_interaction__absolute_plus_deviation__c0.1_b0.2 | 0.624789 | 0.667008 | 0.696583 | 0.671691 | 0.571203 | 0.579209 | 0.538343 | 0.649486 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |
| best__absolute__c0.3_b0.1 | 0.624911 | 0.669885 | 0.699546 | 0.674094 | 0.575375 | 0.577508 | 0.533403 | 0.644567 |
| best__deviation__c0.1_b0.2 | 0.624960 | 0.669308 | 0.698063 | 0.671486 | 0.572623 | 0.580822 | 0.537461 | 0.644954 |
| wai_sleep_recovery_interaction__absolute__c0.1_b0.2 | 0.625009 | 0.667688 | 0.695554 | 0.671515 | 0.572326 | 0.579042 | 0.540411 | 0.648525 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.