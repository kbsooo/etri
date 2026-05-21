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
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |
| best__absolute__c0.3_b0.1 | 0.624911 | 0.669885 | 0.699546 | 0.674094 | 0.575375 | 0.577508 | 0.533403 | 0.644567 |
| best__deviation__c0.1_b0.2 | 0.624960 | 0.669308 | 0.698063 | 0.671486 | 0.572623 | 0.580822 | 0.537461 | 0.644954 |
| best__deviation__c0.3_b0.1 | 0.625027 | 0.670073 | 0.701956 | 0.673797 | 0.573042 | 0.578596 | 0.532199 | 0.645529 |
| best__absolute_plus_deviation__c0.03_b0.2 | 0.625131 | 0.671186 | 0.699156 | 0.673795 | 0.571766 | 0.579118 | 0.536996 | 0.643899 |
| best__absolute_plus_deviation__c0.1_b0.1 | 0.625131 | 0.671015 | 0.702424 | 0.675279 | 0.572622 | 0.578206 | 0.531687 | 0.644686 |
| best_plus_sleep_intrusion__absolute_plus_deviation__c0.1_b0.1 | 0.625158 | 0.668662 | 0.702719 | 0.682564 | 0.572659 | 0.574157 | 0.532481 | 0.642861 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.