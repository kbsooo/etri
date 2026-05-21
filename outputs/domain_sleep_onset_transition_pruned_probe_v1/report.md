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
| sot_prebed_fragmentation__absolute_plus_deviation__c0.03_b0.2 | 0.624313 | 0.666903 | 0.699660 | 0.678591 | 0.578534 | 0.574420 | 0.531156 | 0.640926 |
| sot_prebed_fragmentation__absolute__c0.1_b0.2 | 0.624350 | 0.666063 | 0.696442 | 0.678230 | 0.579296 | 0.575155 | 0.534446 | 0.640820 |
| sot_onset_consensus__deviation__c0.03_b0.2 | 0.624457 | 0.665211 | 0.699325 | 0.678773 | 0.577212 | 0.579414 | 0.530964 | 0.640300 |
| sot_prebed_fragmentation__absolute__c0.3_b0.2 | 0.624511 | 0.667966 | 0.695202 | 0.679853 | 0.580068 | 0.574513 | 0.533692 | 0.640282 |
| sot_prebed_fragmentation__absolute_plus_deviation__c0.1_b0.2 | 0.624517 | 0.668974 | 0.698375 | 0.680548 | 0.580073 | 0.573767 | 0.530079 | 0.639805 |
| sot_onset_consensus__absolute_plus_deviation__c0.03_b0.2 | 0.624539 | 0.665104 | 0.700829 | 0.683288 | 0.578008 | 0.578941 | 0.527823 | 0.637781 |
| sot_prebed_fragmentation__absolute__c0.03_b0.2 | 0.624558 | 0.664954 | 0.697936 | 0.676224 | 0.578704 | 0.576459 | 0.536358 | 0.641268 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.