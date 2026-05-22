# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_psg_proto__absolute_plus_deviation__c0.1_b0.2`
- Avg logloss: `0.622307`
- Delta vs subject prior: `-0.005347`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_psg_proto__absolute_plus_deviation__c0.1_b0.2 | 0.622307 | 0.668800 | 0.696344 | 0.674792 | 0.573728 | 0.576344 | 0.526680 | 0.639461 |
| best_plus_psg_core__absolute_plus_deviation__c0.1_b0.2 | 0.622654 | 0.670777 | 0.699658 | 0.679458 | 0.574806 | 0.572977 | 0.527341 | 0.633557 |
| best_plus_psg_proto__absolute__c0.1_b0.2 | 0.623273 | 0.671610 | 0.693138 | 0.674371 | 0.573315 | 0.575230 | 0.534122 | 0.641124 |
| best_plus_psg_proto__deviation__c0.1_b0.2 | 0.623285 | 0.668527 | 0.692408 | 0.673418 | 0.573967 | 0.578267 | 0.534592 | 0.641817 |
| best_plus_psg_core__absolute__c0.1_b0.2 | 0.623479 | 0.669773 | 0.696860 | 0.679514 | 0.576537 | 0.573443 | 0.533145 | 0.635082 |
| best_plus_psg_proto__absolute_plus_deviation__c0.03_b0.2 | 0.623636 | 0.671127 | 0.695099 | 0.675682 | 0.572932 | 0.577217 | 0.532571 | 0.640824 |
| best__absolute_plus_deviation__c0.1_b0.2 | 0.623793 | 0.670035 | 0.701000 | 0.673654 | 0.570927 | 0.577386 | 0.530510 | 0.643038 |
| best_plus_psg_core__deviation__c0.1_b0.2 | 0.623968 | 0.671999 | 0.695820 | 0.677522 | 0.576835 | 0.574297 | 0.535092 | 0.636210 |
| best_plus_psg_core__absolute_plus_deviation__c0.1_b0.1 | 0.624004 | 0.670792 | 0.701134 | 0.677438 | 0.574191 | 0.575245 | 0.530085 | 0.639147 |
| best_plus_psg_core__absolute_plus_deviation__c0.03_b0.2 | 0.624144 | 0.671827 | 0.698081 | 0.680108 | 0.575022 | 0.574318 | 0.533917 | 0.635732 |
| best_plus_psg_proto__absolute_plus_deviation__c0.1_b0.1 | 0.624181 | 0.670193 | 0.699734 | 0.675596 | 0.573872 | 0.577499 | 0.529787 | 0.642583 |
| best_plus_psg_proto__deviation__c0.03_b0.2 | 0.624485 | 0.670544 | 0.690987 | 0.674894 | 0.574584 | 0.580139 | 0.537990 | 0.642256 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.