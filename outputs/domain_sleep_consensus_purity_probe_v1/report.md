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
| scp_micro_awakenings__deviation__c0.1_b0.2 | 0.623177 | 0.665851 | 0.697287 | 0.683090 | 0.572025 | 0.566212 | 0.538523 | 0.639253 |
| scp_micro_awakenings__deviation__c0.03_b0.2 | 0.623252 | 0.666435 | 0.696741 | 0.682786 | 0.570321 | 0.566405 | 0.539978 | 0.640097 |
| scp_consensus_purity__absolute_plus_deviation__c0.03_b0.2 | 0.623258 | 0.665772 | 0.696689 | 0.672897 | 0.572252 | 0.570193 | 0.536492 | 0.648513 |
| scp_consensus_purity__absolute__c0.03_b0.2 | 0.623283 | 0.664786 | 0.694952 | 0.670587 | 0.573352 | 0.572208 | 0.540795 | 0.646302 |
| scp_consensus_purity__absolute__c0.1_b0.2 | 0.623339 | 0.665795 | 0.695613 | 0.671125 | 0.574080 | 0.570294 | 0.538782 | 0.647683 |
| scp_rolling_context_only__deviation__c0.03_b0.2 | 0.623451 | 0.668961 | 0.690735 | 0.675182 | 0.574280 | 0.573604 | 0.539308 | 0.642087 |
| scp_consensus_purity__deviation__c0.03_b0.2 | 0.623469 | 0.663385 | 0.695958 | 0.671383 | 0.572240 | 0.571533 | 0.539599 | 0.650185 |
| scp_consensus_purity__deviation__c0.1_b0.2 | 0.623545 | 0.665442 | 0.695650 | 0.672289 | 0.573538 | 0.569241 | 0.537256 | 0.651397 |
| scp_rolling_context_only__deviation__c0.1_b0.2 | 0.623610 | 0.668657 | 0.691198 | 0.676506 | 0.574994 | 0.574734 | 0.536523 | 0.642658 |
| scp_micro_awakenings__deviation__c0.3_b0.2 | 0.623660 | 0.664281 | 0.698999 | 0.683368 | 0.573684 | 0.567787 | 0.537824 | 0.639676 |
| scp_micro_awakenings__absolute_plus_deviation__c0.03_b0.2 | 0.623679 | 0.666744 | 0.698095 | 0.684665 | 0.571243 | 0.567868 | 0.539693 | 0.637442 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.