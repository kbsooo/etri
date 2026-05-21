# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `previous_combo__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.624798`
- Delta vs subject prior: `-0.002856`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| previous_combo__absolute_plus_deviation__c0.3_b0.2 | 0.624798 | 0.672135 | 0.700326 | 0.679580 | 0.572296 | 0.579583 | 0.521652 | 0.648012 |
| previous_combo__deviation__c0.3_b0.2 | 0.624899 | 0.669787 | 0.694281 | 0.677706 | 0.572929 | 0.581737 | 0.528887 | 0.648965 |
| previous_combo__absolute_plus_deviation__c0.1_b0.2 | 0.624955 | 0.672558 | 0.697400 | 0.678677 | 0.572779 | 0.579455 | 0.526514 | 0.647303 |
| previous_combo__absolute__c0.3_b0.2 | 0.625319 | 0.672545 | 0.697244 | 0.677198 | 0.572712 | 0.579090 | 0.531668 | 0.646774 |
| previous_combo__deviation__c0.3_b0.1 | 0.625509 | 0.670921 | 0.698764 | 0.677268 | 0.573452 | 0.580084 | 0.530608 | 0.647463 |
| previous_combo__absolute__c0.1_b0.2 | 0.625524 | 0.672628 | 0.695953 | 0.676394 | 0.573798 | 0.580181 | 0.533742 | 0.645975 |
| previous_combo__absolute__c0.3_b0.1 | 0.625546 | 0.672174 | 0.700179 | 0.676992 | 0.573281 | 0.578475 | 0.531433 | 0.646290 |
| previous_combo__deviation__c0.1_b0.2 | 0.625558 | 0.670841 | 0.692289 | 0.677190 | 0.574298 | 0.582529 | 0.533987 | 0.647773 |
| previous_combo__absolute_plus_deviation__c0.3_b0.1 | 0.625648 | 0.672198 | 0.701946 | 0.678196 | 0.573436 | 0.579368 | 0.527272 | 0.647121 |
| previous_combo__absolute_plus_deviation__c0.03_b0.2 | 0.625766 | 0.673403 | 0.695200 | 0.677290 | 0.573828 | 0.580964 | 0.532805 | 0.646872 |
| previous_combo__absolute__c0.1_b0.1 | 0.625775 | 0.672301 | 0.699648 | 0.676690 | 0.573989 | 0.579110 | 0.532722 | 0.645968 |
| previous_combo__absolute_plus_deviation__c0.1_b0.1 | 0.625783 | 0.672488 | 0.700581 | 0.677874 | 0.573762 | 0.579252 | 0.529704 | 0.646822 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.