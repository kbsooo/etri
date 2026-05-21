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
| cc_opportunity__absolute_plus_deviation__c0.3_b0.2 | 0.623996 | 0.656851 | 0.704707 | 0.681742 | 0.566792 | 0.573390 | 0.543632 | 0.640858 |
| cc_opportunity__deviation__c0.3_b0.2 | 0.624000 | 0.657292 | 0.701046 | 0.678696 | 0.568068 | 0.574644 | 0.544984 | 0.643270 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| cc_opportunity__deviation__c0.1_b0.2 | 0.624292 | 0.659624 | 0.699721 | 0.678109 | 0.569649 | 0.575452 | 0.544073 | 0.643419 |
| cc_opportunity__absolute_plus_deviation__c0.1_b0.2 | 0.624533 | 0.658768 | 0.702481 | 0.680465 | 0.568843 | 0.575072 | 0.544167 | 0.641938 |
| cc_recovery__absolute_plus_deviation__c0.3_b0.2 | 0.624572 | 0.671876 | 0.697474 | 0.671010 | 0.574700 | 0.576989 | 0.538698 | 0.641259 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| cc_chain_interactions__deviation__c0.3_b0.2 | 0.624755 | 0.665804 | 0.700674 | 0.678563 | 0.568474 | 0.576235 | 0.543932 | 0.639600 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.