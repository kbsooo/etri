# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_rr_routine_state__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.620696`
- Delta vs subject prior: `-0.006958`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_rr_routine_state__absolute_plus_deviation__c0.3_b0.2 | 0.620696 | 0.664996 | 0.694493 | 0.673055 | 0.568087 | 0.574366 | 0.526621 | 0.643253 |
| best_plus_rr_profile_distance__absolute_plus_deviation__c0.3_b0.2 | 0.620720 | 0.666682 | 0.696539 | 0.674628 | 0.572035 | 0.576682 | 0.523704 | 0.634767 |
| best_plus_rr_routine_state__deviation__c0.3_b0.2 | 0.621469 | 0.664959 | 0.693629 | 0.669736 | 0.569696 | 0.572717 | 0.533514 | 0.646033 |
| best_plus_rr_profile_distance__absolute_plus_deviation__c0.1_b0.2 | 0.621685 | 0.668436 | 0.695756 | 0.673820 | 0.571462 | 0.576248 | 0.530854 | 0.635215 |
| best_plus_rr_routine_state__absolute_plus_deviation__c0.1_b0.2 | 0.621785 | 0.665681 | 0.695434 | 0.673400 | 0.568459 | 0.574589 | 0.531832 | 0.643099 |
| best_plus_rr_profile_distance__deviation__c0.3_b0.2 | 0.621848 | 0.667430 | 0.694471 | 0.671210 | 0.572270 | 0.576561 | 0.533026 | 0.637965 |
| best_plus_rr_phase_shift__absolute_plus_deviation__c0.3_b0.2 | 0.621869 | 0.660062 | 0.703743 | 0.668161 | 0.570300 | 0.579402 | 0.524966 | 0.646449 |
| best_plus_rr_profile_distance__absolute__c0.3_b0.2 | 0.622299 | 0.667479 | 0.690682 | 0.672183 | 0.576561 | 0.574903 | 0.537685 | 0.636599 |
| best_plus_rr_sleep_regular_break__absolute_plus_deviation__c0.1_b0.2 | 0.622302 | 0.671496 | 0.703015 | 0.668429 | 0.567712 | 0.569672 | 0.540498 | 0.635291 |
| best_plus_rr_phase_shift__absolute_plus_deviation__c0.1_b0.2 | 0.622705 | 0.661534 | 0.701499 | 0.670132 | 0.569235 | 0.578905 | 0.531124 | 0.646505 |
| best_plus_rr_sleep_regular_break__absolute_plus_deviation__c0.03_b0.2 | 0.622717 | 0.669762 | 0.700763 | 0.669639 | 0.567356 | 0.571229 | 0.541617 | 0.638649 |
| best_plus_rr_sleep_regular_break__deviation__c0.1_b0.2 | 0.622773 | 0.670761 | 0.700484 | 0.665750 | 0.567334 | 0.574222 | 0.542639 | 0.638223 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.