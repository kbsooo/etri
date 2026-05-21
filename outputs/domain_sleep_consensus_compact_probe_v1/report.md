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
| scc_rolling__deviation__c0.3_b0.2 | 0.624117 | 0.667311 | 0.683698 | 0.673757 | 0.578581 | 0.579968 | 0.542823 | 0.642682 |
| best__absolute__c0.3_b0.2 | 0.624117 | 0.668482 | 0.696014 | 0.671596 | 0.576790 | 0.577124 | 0.535370 | 0.643446 |
| scc_subject_relative__absolute__c0.3_b0.2 | 0.624464 | 0.665806 | 0.706664 | 0.677877 | 0.573026 | 0.571703 | 0.532370 | 0.643804 |
| scc_subject_relative__absolute__c0.1_b0.2 | 0.624486 | 0.667820 | 0.706817 | 0.676838 | 0.573587 | 0.570963 | 0.533887 | 0.641493 |
| scc_rolling__absolute_plus_deviation__c0.3_b0.2 | 0.624494 | 0.669749 | 0.685687 | 0.674811 | 0.577157 | 0.579590 | 0.539517 | 0.644949 |
| best__absolute_plus_deviation__c0.3_b0.1 | 0.624640 | 0.670387 | 0.702880 | 0.675390 | 0.572565 | 0.578298 | 0.528312 | 0.644648 |
| scc_subject_relative__absolute__c0.03_b0.2 | 0.624756 | 0.669009 | 0.705503 | 0.676051 | 0.573848 | 0.572263 | 0.535786 | 0.640830 |
| scc_rolling__deviation__c0.1_b0.2 | 0.624780 | 0.666415 | 0.686423 | 0.673872 | 0.578165 | 0.581703 | 0.543948 | 0.642933 |
| best__absolute__c0.1_b0.2 | 0.624806 | 0.669021 | 0.695986 | 0.672282 | 0.576570 | 0.578542 | 0.537590 | 0.643649 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.