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
| ef_recovery_slope__deviation__c0.3_b0.2 | 0.623962 | 0.670470 | 0.684014 | 0.667182 | 0.583079 | 0.574938 | 0.542103 | 0.645945 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| ef_recovery_slope__absolute_plus_deviation__c0.3_b0.2 | 0.624297 | 0.676008 | 0.686623 | 0.667278 | 0.587304 | 0.573859 | 0.538224 | 0.640784 |
| ef_recovery_slope__absolute_plus_deviation__c0.1_b0.2 | 0.624558 | 0.673734 | 0.688034 | 0.668276 | 0.586073 | 0.574193 | 0.539344 | 0.642251 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| ef_recovery_slope__deviation__c0.3_b0.1 | 0.624768 | 0.670800 | 0.693232 | 0.671240 | 0.578699 | 0.576187 | 0.537474 | 0.645744 |
| ef_recovery_slope__deviation__c0.1_b0.2 | 0.624798 | 0.669723 | 0.686464 | 0.669083 | 0.582818 | 0.576396 | 0.542234 | 0.646866 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |
| best__absolute__c0.3_b0.1 | 0.624911 | 0.669885 | 0.699546 | 0.674094 | 0.575375 | 0.577508 | 0.533403 | 0.644567 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.