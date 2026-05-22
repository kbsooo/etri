# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_psg_qcore__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.618037`
- Delta vs subject prior: `-0.009617`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_psg_qcore__absolute_plus_deviation__c0.3_b0.2 | 0.618037 | 0.660513 | 0.704705 | 0.669986 | 0.564008 | 0.567287 | 0.524005 | 0.635758 |
| best_plus_psg_qcore__absolute__c0.3_b0.2 | 0.618557 | 0.660962 | 0.699715 | 0.666346 | 0.567172 | 0.567625 | 0.530804 | 0.637277 |
| best_plus_psg_qcore__deviation__c0.3_b0.2 | 0.618643 | 0.663509 | 0.699458 | 0.665167 | 0.565990 | 0.566891 | 0.531157 | 0.638330 |
| best_plus_psg_qcore__absolute_plus_deviation__c0.1_b0.2 | 0.619194 | 0.663286 | 0.701656 | 0.668660 | 0.566399 | 0.568262 | 0.528268 | 0.637830 |
| best_plus_psg_qcore__absolute__c0.1_b0.2 | 0.620032 | 0.663295 | 0.696305 | 0.666649 | 0.569731 | 0.569831 | 0.534531 | 0.639882 |
| best_plus_psg_qcore__deviation__c0.1_b0.2 | 0.620208 | 0.665268 | 0.695788 | 0.666253 | 0.568421 | 0.569772 | 0.535675 | 0.640283 |
| best_plus_psg_qcore__absolute_plus_deviation__c0.03_b0.2 | 0.621074 | 0.666352 | 0.697702 | 0.668767 | 0.569115 | 0.570768 | 0.534322 | 0.640492 |
| best_plus_psg_qcore__absolute_plus_deviation__c0.3_b0.1 | 0.621410 | 0.665544 | 0.703531 | 0.672456 | 0.568353 | 0.571818 | 0.527922 | 0.640248 |
| psg_qcore__absolute_plus_deviation__c0.3_b0.2 | 0.621490 | 0.665038 | 0.705870 | 0.677787 | 0.568159 | 0.565174 | 0.532537 | 0.635864 |
| psg_qcore__absolute_plus_deviation__c0.1_b0.2 | 0.621594 | 0.665395 | 0.702357 | 0.674371 | 0.568960 | 0.566827 | 0.534809 | 0.638442 |
| best_plus_psg_qcore__deviation__c0.3_b0.1 | 0.621728 | 0.667154 | 0.700910 | 0.670198 | 0.569415 | 0.571527 | 0.531402 | 0.641488 |
| best_plus_psg_qcore__absolute__c0.3_b0.1 | 0.621749 | 0.665875 | 0.701105 | 0.670931 | 0.570106 | 0.572042 | 0.531140 | 0.641041 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.