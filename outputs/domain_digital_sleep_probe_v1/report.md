# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_digital_sleep__absolute_plus_deviation__c0.1_b0.2`
- Avg logloss: `0.621977`
- Delta vs subject prior: `-0.005677`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_digital_sleep__absolute_plus_deviation__c0.1_b0.2 | 0.621977 | 0.671081 | 0.697132 | 0.671609 | 0.569447 | 0.568057 | 0.532249 | 0.644260 |
| best_plus_digital_sleep__absolute_plus_deviation__c0.03_b0.2 | 0.622023 | 0.668122 | 0.696344 | 0.670430 | 0.569679 | 0.569810 | 0.536293 | 0.643480 |
| best_plus_digital_sleep__deviation__c0.03_b0.2 | 0.622332 | 0.667644 | 0.694057 | 0.669128 | 0.569580 | 0.572958 | 0.539162 | 0.643796 |
| best_plus_digital_sleep__absolute__c0.1_b0.2 | 0.622398 | 0.667039 | 0.695684 | 0.671512 | 0.575195 | 0.569575 | 0.535493 | 0.642291 |
| best_plus_digital_sleep__deviation__c0.1_b0.2 | 0.622401 | 0.669985 | 0.694734 | 0.670938 | 0.569056 | 0.571055 | 0.536480 | 0.644555 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_digital_sleep__absolute_plus_deviation__c0.1_b0.1 | 0.623388 | 0.670941 | 0.699634 | 0.673130 | 0.571141 | 0.572025 | 0.532436 | 0.644405 |
| best_plus_digital_sleep__deviation__c0.1_b0.1 | 0.623481 | 0.670400 | 0.698495 | 0.672940 | 0.570842 | 0.573303 | 0.533778 | 0.644606 |
| best_plus_digital_sleep__absolute__c0.1_b0.1 | 0.623631 | 0.668974 | 0.699058 | 0.673286 | 0.574116 | 0.572646 | 0.533910 | 0.643430 |
| best_plus_digital_sleep__deviation__c0.03_b0.1 | 0.623653 | 0.669426 | 0.698423 | 0.672337 | 0.571303 | 0.574363 | 0.535295 | 0.644424 |
| best_plus_digital_sleep__absolute_plus_deviation__c0.03_b0.1 | 0.623662 | 0.669714 | 0.699570 | 0.672902 | 0.571483 | 0.573027 | 0.534628 | 0.644310 |
| best_plus_digital_sleep__absolute__c0.03_b0.2 | 0.623685 | 0.665846 | 0.695446 | 0.669655 | 0.574489 | 0.571312 | 0.538954 | 0.650093 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.