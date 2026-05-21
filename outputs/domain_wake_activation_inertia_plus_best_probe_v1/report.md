# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.618903`
- Delta vs subject prior: `-0.008751`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2 | 0.618903 | 0.661696 | 0.699598 | 0.670362 | 0.557111 | 0.575587 | 0.522824 | 0.645139 |
| best_plus_wai_sleep_recovery_interaction__absolute__c0.3_b0.2 | 0.619715 | 0.661237 | 0.694791 | 0.671069 | 0.562902 | 0.572607 | 0.531539 | 0.643859 |
| best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.1_b0.2 | 0.620120 | 0.662877 | 0.698538 | 0.671010 | 0.561209 | 0.575534 | 0.527611 | 0.644059 |
| best_plus_wai_sleep_recovery_interaction__deviation__c0.3_b0.2 | 0.620504 | 0.662232 | 0.698820 | 0.668916 | 0.562933 | 0.576260 | 0.528881 | 0.645484 |
| best_plus_wai_sleep_recovery_interaction__absolute__c0.1_b0.2 | 0.621291 | 0.663092 | 0.694504 | 0.671208 | 0.567748 | 0.574453 | 0.534326 | 0.643708 |
| best_plus_wai_sleep_recovery_interaction__deviation__c0.1_b0.2 | 0.621719 | 0.662729 | 0.696100 | 0.669853 | 0.567020 | 0.578231 | 0.533149 | 0.644949 |
| best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.1 | 0.622142 | 0.666169 | 0.701215 | 0.672970 | 0.564688 | 0.576977 | 0.527636 | 0.645337 |
| best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.03_b0.2 | 0.622180 | 0.665269 | 0.697014 | 0.671760 | 0.566503 | 0.576839 | 0.533507 | 0.644366 |
| best_plus_wai_light_hr_entrainment__absolute_plus_deviation__c0.3_b0.2 | 0.622321 | 0.668910 | 0.702318 | 0.678374 | 0.562406 | 0.580239 | 0.523521 | 0.640480 |
| best_plus_wai_sleep_recovery_interaction__absolute__c0.3_b0.1 | 0.622485 | 0.665994 | 0.698712 | 0.673436 | 0.567655 | 0.575211 | 0.531822 | 0.644564 |
| best_plus_wai_light_hr_entrainment__absolute_plus_deviation__c0.1_b0.2 | 0.622862 | 0.669055 | 0.701632 | 0.677424 | 0.563640 | 0.579830 | 0.528658 | 0.639795 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.