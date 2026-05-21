# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `sfr_sleep_sensor__deviation__c0.1_b0.2`
- Avg logloss: `0.622631`
- Delta vs subject prior: `-0.005023`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sfr_sleep_sensor__deviation__c0.1_b0.2 | 0.622631 | 0.660348 | 0.706807 | 0.675378 | 0.567493 | 0.574444 | 0.535099 | 0.638849 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| sfr_sleep_sensor__deviation__c0.03_b0.2 | 0.622974 | 0.660726 | 0.704745 | 0.673801 | 0.568630 | 0.575834 | 0.536750 | 0.640329 |
| sfr_sleep_sensor__deviation__c0.3_b0.2 | 0.623170 | 0.661258 | 0.708496 | 0.677067 | 0.568176 | 0.574396 | 0.534281 | 0.638516 |
| sfr_sleep_sensor__absolute_plus_deviation__c0.03_b0.2 | 0.623284 | 0.661594 | 0.705300 | 0.675417 | 0.567032 | 0.578113 | 0.536914 | 0.638620 |
| sfr_sleep_sensor__absolute_plus_deviation__c0.1_b0.2 | 0.623331 | 0.662534 | 0.706615 | 0.677669 | 0.565900 | 0.577032 | 0.536389 | 0.637175 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best__deviation__c0.3_b0.2 | 0.624010 | 0.668486 | 0.700536 | 0.670945 | 0.572281 | 0.578804 | 0.531926 | 0.645093 |
| sfr_sleep_sensor__absolute_plus_deviation__c0.3_b0.2 | 0.624104 | 0.663367 | 0.707827 | 0.680355 | 0.566084 | 0.577100 | 0.536963 | 0.637034 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| sfr_sleep_sensor__deviation__c0.1_b0.1 | 0.624230 | 0.665698 | 0.705256 | 0.675849 | 0.570437 | 0.576368 | 0.534061 | 0.641940 |
| sfr_sleep_sensor__deviation__c0.3_b0.1 | 0.624337 | 0.665958 | 0.705926 | 0.676542 | 0.570591 | 0.576200 | 0.533539 | 0.641600 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.