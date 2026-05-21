# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_routine_digital__deviation__c0.03_b0.2`
- Avg logloss: `0.622618`
- Delta vs subject prior: `-0.005036`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_routine_digital__deviation__c0.03_b0.2 | 0.622618 | 0.666116 | 0.704933 | 0.670240 | 0.567063 | 0.567782 | 0.543562 | 0.638633 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_routine_digital__deviation__c0.03_b0.1 | 0.623414 | 0.668181 | 0.703382 | 0.672441 | 0.569728 | 0.571413 | 0.537530 | 0.641221 |
| best_plus_routine_digital__absolute__c0.03_b0.2 | 0.623655 | 0.663136 | 0.702135 | 0.669587 | 0.568485 | 0.569586 | 0.549936 | 0.642721 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best_plus_routine_digital__absolute__c0.03_b0.1 | 0.623965 | 0.666647 | 0.702072 | 0.672215 | 0.570461 | 0.572019 | 0.541123 | 0.643221 |
| best_plus_routine_digital__absolute_plus_deviation__c0.03_b0.1 | 0.623979 | 0.667918 | 0.705126 | 0.673621 | 0.569168 | 0.570717 | 0.539682 | 0.641622 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best_plus_routine_digital__absolute_plus_deviation__c0.03_b0.2 | 0.624073 | 0.666099 | 0.708939 | 0.673143 | 0.566267 | 0.566962 | 0.547096 | 0.640005 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| best_plus_routine_digital__deviation__c0.1_b0.1 | 0.624218 | 0.669101 | 0.705354 | 0.673682 | 0.569772 | 0.571089 | 0.539009 | 0.641517 |
| best_plus_routine_digital__absolute__c0.1_b0.1 | 0.624424 | 0.667224 | 0.703144 | 0.673947 | 0.569195 | 0.571189 | 0.542191 | 0.644080 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.