# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_sot_prebed_fragmentation__absolute__c0.3_b0.2`
- Avg logloss: `0.621300`
- Delta vs subject prior: `-0.006354`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_sot_prebed_fragmentation__absolute__c0.3_b0.2 | 0.621300 | 0.666993 | 0.695570 | 0.673369 | 0.578689 | 0.571407 | 0.525756 | 0.637317 |
| best_plus_sot_prebed_fragmentation__absolute_plus_deviation__c0.3_b0.2 | 0.621364 | 0.669565 | 0.697898 | 0.673111 | 0.576652 | 0.572844 | 0.522368 | 0.637109 |
| best_plus_sot_prebed_fragmentation__absolute_plus_deviation__c0.1_b0.2 | 0.621504 | 0.668543 | 0.699288 | 0.673700 | 0.575906 | 0.571991 | 0.523369 | 0.637727 |
| best_plus_sot_shutdown_slope__absolute_plus_deviation__c0.3_b0.2 | 0.621512 | 0.671192 | 0.702568 | 0.680926 | 0.565826 | 0.572676 | 0.516182 | 0.641217 |
| best_plus_sot_shutdown_slope__absolute__c0.3_b0.2 | 0.621760 | 0.667023 | 0.697462 | 0.678781 | 0.571766 | 0.572262 | 0.524891 | 0.640134 |
| best_plus_sot_prebed_fragmentation__absolute__c0.1_b0.2 | 0.621956 | 0.665226 | 0.696601 | 0.674614 | 0.578587 | 0.571925 | 0.528785 | 0.637956 |
| best_plus_sot_prebed_fragmentation__deviation__c0.3_b0.2 | 0.622176 | 0.671429 | 0.699462 | 0.670802 | 0.576576 | 0.573241 | 0.522752 | 0.640969 |
| best_plus_sot_prebed_fragmentation__absolute_plus_deviation__c0.03_b0.2 | 0.622328 | 0.667410 | 0.700811 | 0.675283 | 0.575290 | 0.572251 | 0.526644 | 0.638604 |
| best_plus_sot_shutdown_slope__absolute_plus_deviation__c0.1_b0.2 | 0.622448 | 0.672711 | 0.701764 | 0.679963 | 0.566923 | 0.573601 | 0.522450 | 0.639725 |
| best_plus_sot_prebed_fragmentation__deviation__c0.1_b0.2 | 0.622627 | 0.669039 | 0.700608 | 0.672640 | 0.575986 | 0.573592 | 0.525202 | 0.641324 |
| best_plus_sot_shutdown_slope__deviation__c0.3_b0.2 | 0.622637 | 0.674751 | 0.699744 | 0.677584 | 0.567020 | 0.574490 | 0.523295 | 0.641576 |
| best_plus_sot_shutdown_slope__absolute__c0.1_b0.2 | 0.622804 | 0.669233 | 0.697680 | 0.678294 | 0.572278 | 0.574146 | 0.528563 | 0.639436 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.