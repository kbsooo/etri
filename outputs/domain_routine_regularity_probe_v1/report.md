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
| best_plus_routine_regularity__deviation__c0.03_b0.2 | 0.623775 | 0.669293 | 0.701846 | 0.671496 | 0.568617 | 0.574433 | 0.543603 | 0.637136 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| routine_regularity__deviation__c0.03_b0.2 | 0.624260 | 0.670459 | 0.700338 | 0.671755 | 0.571147 | 0.574483 | 0.545210 | 0.636425 |
| best_plus_routine_regularity__deviation__c0.03_b0.1 | 0.624466 | 0.670122 | 0.701954 | 0.673537 | 0.570858 | 0.575844 | 0.538192 | 0.640757 |
| routine_regularity__deviation__c0.1_b0.1 | 0.624590 | 0.672450 | 0.701482 | 0.673302 | 0.570054 | 0.574439 | 0.540989 | 0.639417 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| best_plus_routine_regularity__deviation__c0.1_b0.1 | 0.624705 | 0.671476 | 0.702953 | 0.672869 | 0.569099 | 0.575590 | 0.540507 | 0.640443 |
| best_plus_routine_regularity__absolute_plus_deviation__c0.03_b0.1 | 0.624729 | 0.669389 | 0.703685 | 0.674342 | 0.569083 | 0.576240 | 0.539815 | 0.640549 |
| best_plus_routine_regularity__absolute_plus_deviation__c0.03_b0.2 | 0.624740 | 0.668443 | 0.705670 | 0.673614 | 0.565616 | 0.575598 | 0.547104 | 0.637136 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.