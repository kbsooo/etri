# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_di_prebed_consumption__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.622540`
- Delta vs subject prior: `-0.005113`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_di_prebed_consumption__absolute_plus_deviation__c0.3_b0.2 | 0.622540 | 0.670136 | 0.691868 | 0.678558 | 0.573958 | 0.578000 | 0.524642 | 0.640622 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_di_prebed_consumption__absolute_plus_deviation__c0.1_b0.2 | 0.622997 | 0.669470 | 0.693579 | 0.677822 | 0.572138 | 0.577885 | 0.529449 | 0.640635 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best_plus_di_prebed_consumption__absolute_plus_deviation__c0.3_b0.1 | 0.623947 | 0.670509 | 0.696948 | 0.676905 | 0.573673 | 0.578105 | 0.528659 | 0.642832 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| best_plus_di_prebed_consumption__absolute_plus_deviation__c0.03_b0.2 | 0.624120 | 0.668950 | 0.695019 | 0.676593 | 0.571537 | 0.579405 | 0.535394 | 0.641941 |
| best_plus_di_social_isolation__absolute_plus_deviation__c0.1_b0.2 | 0.624121 | 0.667050 | 0.689805 | 0.675438 | 0.577742 | 0.583662 | 0.527319 | 0.647829 |
| best_plus_di_social_isolation__absolute_plus_deviation__c0.03_b0.2 | 0.624346 | 0.665508 | 0.689770 | 0.674069 | 0.577566 | 0.584019 | 0.532295 | 0.647194 |
| best_plus_di_social_isolation__absolute_plus_deviation__c0.3_b0.2 | 0.624369 | 0.668706 | 0.689185 | 0.675820 | 0.578870 | 0.584971 | 0.523590 | 0.649440 |
| best_plus_di_prebed_consumption__absolute_plus_deviation__c0.1_b0.1 | 0.624457 | 0.670479 | 0.698148 | 0.676894 | 0.572984 | 0.578242 | 0.531366 | 0.643091 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.