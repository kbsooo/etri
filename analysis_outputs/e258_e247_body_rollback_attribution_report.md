# E258 E247 Body/Rollback Attribution Atlas

## Question

E247 is public-positive, but did public reward the E224 capped-Q3/S4 body, the Q3 feature-NN1 rollback, or their interaction?

## Component Summary

| component_id | moved_cells | targets_moved | l2_logit | l1_abs_logit | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | Q3_abs_share | S4_abs_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_body_vs_e95 | 534 | Q1,Q3,S2,S3,S4 | 1.096690723 | 17.835743894 | -0.000653189 | 0.004094069 | 0.465789507 | 0.150551319 | 0.533416245 | 0.363619236 |
| e247_rollback_vs_e224 | 34 | Q3 | 0.434013527 | 2.285236082 | -0.000066519 | 0.000673258 | 0.566510083 | 1.413603067 | 1.000000000 | 0.000000000 |
| e256_rollback_vs_e224 | 25 | Q3 | 0.467150343 | 2.217878088 | -0.000047418 | 0.000651756 | 0.551678319 | 1.983036023 | 1.000000000 | 0.000000000 |
| e247_total_vs_e95 | 513 | Q1,Q3,S2,S3,S4 | 1.002645110 | 15.677961133 | -0.000719708 | 0.003497893 | 0.470775642 | 0.136636606 | 0.469199580 | 0.413664730 |
| e256_total_vs_e95 | 520 | Q1,Q3,S2,S3,S4 | 0.989631750 | 15.698781864 | -0.000700607 | 0.003501586 | 0.468433641 | 0.140361815 | 0.469903561 | 0.413116101 |
| e224_body_vs_e154 | 355 | Q3,S4 | 1.044320533 | 15.112576379 | -0.000623352 | 0.003400775 | 0.465984132 | 0.157757659 | 0.591856472 | 0.408143528 |

## Target Summary

| candidate_id | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| e224_body_vs_e154 | Q3 | 250 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| e224_body_vs_e154 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| e224_body_vs_e95 | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| e224_body_vs_e95 | Q3 | 250 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |
| e224_body_vs_e95 | S2 | 39 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| e224_body_vs_e95 | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| e224_body_vs_e95 | S4 | 119 | -0.000533760 | 0.001239673 | 0.478536176 | 0.181242349 |
| e247_rollback_vs_e224 | Q3 | 34 | -0.000066519 | 0.000673258 | 0.566510083 | 1.413603067 |
| e247_total_vs_e95 | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| e247_total_vs_e95 | Q3 | 229 | -0.000180358 | 0.001756244 | 0.460713875 | 0.545240602 |
| e247_total_vs_e95 | S2 | 39 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| e247_total_vs_e95 | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| e247_total_vs_e95 | S4 | 119 | -0.000533760 | 0.001239673 | 0.478536176 | 0.181242349 |
| e256_rollback_vs_e224 | Q3 | 25 | -0.000047418 | 0.000651756 | 0.551678319 | 1.983036023 |
| e256_total_vs_e95 | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| e256_total_vs_e95 | Q3 | 236 | -0.000161257 | 0.001759937 | 0.455758271 | 0.609825071 |
| e256_total_vs_e95 | S2 | 39 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| e256_total_vs_e95 | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| e256_total_vs_e95 | S4 | 119 | -0.000533760 | 0.001239673 | 0.478536176 | 0.181242349 |

## Rollback vs Body Overlap

| component_id | selected_cells | cos_body_rollback_all | cos_body_rollback_selected | rollback_l2_over_body_l2 | rollback_l2_over_total_l2 | selected_body_abs_share | rollback_abs_over_selected_body_abs | opposite_sign_share_selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e247_rollback_vs_e224 | 34 | -0.405271434 | -0.992683110 | 0.395748335 | 0.432868542 | 0.130133232 | 0.984581403 | 1.000000000 |
| e256_rollback_vs_e224 | 25 | -0.430970350 | -0.995302880 | 0.425963613 | 0.472044619 | 0.126605380 | 0.982187223 | 1.000000000 |

## Interpretation

- E247 rollback touches `34` cells and is mostly an opposite-sign trim of E224 body on those cells: opposite-sign share `1.000000`.
- E247 rollback L2 is `0.395748` of the E224 body and `0.432869` of the final E247 movement.
- E256 rollback touches `25` cells and has opposite-sign share `1.000000`.
- Therefore E247 should be read as E224 body plus a Q3 tail correction, not as a standalone smoothing replacement.
- Public E247 feedback alone cannot attribute the win. E224 is the clean body-attribution public question; E256 is the score-plus-information broad-vs-amplitude rollback question.

## Decision

- If the next slot prioritizes immediate score while staying inside the validated E247 mechanism, use E256.
- If the next slot prioritizes explaining why E247 won, use E224 because it removes the Q3 rollback and isolates the body.
- Do not build an E247/E256 blend before one of those attribution sensors is observed.
