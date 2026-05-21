# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `boundary_target_map__absolute_plus_deviation__c0.03_b0.2`
- Avg logloss: `0.617752`
- Delta vs subject prior: `-0.009902`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| boundary_target_map__absolute_plus_deviation__c0.03_b0.2 | 0.617752 | 0.655171 | 0.685252 | 0.679239 | 0.572675 | 0.570585 | 0.524316 | 0.637030 |
| boundary_target_map__absolute_plus_deviation__c0.01_b0.2 | 0.617891 | 0.656328 | 0.686329 | 0.676891 | 0.572199 | 0.569696 | 0.527489 | 0.636306 |
| boundary_target_map__deviation__c0.03_b0.2 | 0.617920 | 0.657160 | 0.683787 | 0.677315 | 0.573894 | 0.569420 | 0.526210 | 0.637657 |
| boundary_target_map__absolute__c0.03_b0.2 | 0.617979 | 0.653648 | 0.684525 | 0.676997 | 0.577192 | 0.568708 | 0.528371 | 0.636415 |
| boundary_target_map__deviation__c0.1_b0.2 | 0.618279 | 0.659430 | 0.682832 | 0.679098 | 0.573778 | 0.570036 | 0.523109 | 0.639674 |
| boundary_target_map__absolute__c0.1_b0.2 | 0.618474 | 0.653966 | 0.684071 | 0.678786 | 0.579029 | 0.569500 | 0.525484 | 0.638481 |
| boundary_target_map__absolute__c0.01_b0.2 | 0.619135 | 0.656870 | 0.686420 | 0.674445 | 0.576151 | 0.570204 | 0.532993 | 0.636863 |
| boundary_target_map__deviation__c0.01_b0.2 | 0.619193 | 0.658771 | 0.686179 | 0.675418 | 0.574070 | 0.571124 | 0.530543 | 0.638245 |
| boundary_target_map__absolute_plus_deviation__c0.1_b0.2 | 0.619743 | 0.658188 | 0.685989 | 0.680327 | 0.574745 | 0.573318 | 0.524939 | 0.640696 |
| boundary_target_map__deviation__c0.3_b0.2 | 0.620194 | 0.663924 | 0.684237 | 0.679724 | 0.574737 | 0.571779 | 0.522937 | 0.644021 |
| boundary_target_map__absolute__c0.3_b0.2 | 0.620298 | 0.657325 | 0.685892 | 0.678277 | 0.580398 | 0.571040 | 0.526564 | 0.642590 |
| boundary_target_map__deviation__c0.1_b0.1 | 0.620692 | 0.664189 | 0.691382 | 0.676175 | 0.572538 | 0.572530 | 0.526668 | 0.641364 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.