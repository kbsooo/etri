# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `current_best__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.622961`
- Delta vs subject prior: `-0.004693`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| current_best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| current_best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| combo_order_event_missing__absolute_plus_deviation__c0.3_b0.2 | 0.623926 | 0.668911 | 0.704364 | 0.671756 | 0.573871 | 0.579380 | 0.526124 | 0.643075 |
| current_best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| current_best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| combo_order_event_missing__deviation__c0.3_b0.2 | 0.624371 | 0.666816 | 0.701570 | 0.670626 | 0.574625 | 0.580898 | 0.531548 | 0.644511 |
| combo_order_event_missing__absolute_plus_deviation__c0.1_b0.2 | 0.624406 | 0.668616 | 0.703747 | 0.672695 | 0.573481 | 0.578851 | 0.530165 | 0.643286 |
| current_best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| combo_order_event_missing__absolute__c0.3_b0.2 | 0.624702 | 0.667951 | 0.697791 | 0.670426 | 0.577042 | 0.581952 | 0.533655 | 0.644095 |
| current_best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |
| combo_order_event_missing__absolute__c0.1_b0.2 | 0.624819 | 0.667358 | 0.698850 | 0.671367 | 0.577006 | 0.581534 | 0.534399 | 0.643219 |
| current_best__absolute__c0.3_b0.1 | 0.624911 | 0.669885 | 0.699546 | 0.674094 | 0.575375 | 0.577508 | 0.533403 | 0.644567 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.