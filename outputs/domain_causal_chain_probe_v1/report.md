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
| causal_chain__deviation__c0.1_b0.2 | 0.623874 | 0.664470 | 0.700023 | 0.680368 | 0.567834 | 0.573457 | 0.541424 | 0.639543 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| causal_chain__deviation__c0.3_b0.2 | 0.624076 | 0.662235 | 0.703334 | 0.680224 | 0.566061 | 0.573004 | 0.543936 | 0.639741 |
| causal_chain__absolute_plus_deviation__c0.1_b0.2 | 0.624081 | 0.660971 | 0.705506 | 0.682936 | 0.566049 | 0.572859 | 0.543418 | 0.636830 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| causal_chain__absolute_plus_deviation__c0.03_b0.2 | 0.624438 | 0.665024 | 0.701872 | 0.682125 | 0.568801 | 0.573503 | 0.541404 | 0.638336 |
| causal_chain__deviation__c0.3_b0.1 | 0.624457 | 0.666353 | 0.702879 | 0.677802 | 0.569431 | 0.574510 | 0.538057 | 0.642164 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| causal_chain__deviation__c0.1_b0.1 | 0.624656 | 0.667749 | 0.701603 | 0.678226 | 0.570608 | 0.574986 | 0.537018 | 0.642400 |
| causal_chain__absolute_plus_deviation__c0.3_b0.1 | 0.624668 | 0.664762 | 0.705613 | 0.678370 | 0.568740 | 0.574987 | 0.539570 | 0.640635 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.