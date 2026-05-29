# E94 Soft-Health / Hard-Label Tail Audit

## Question

E92 and E93 both reward the known public-negative E72 file. E94 asks whether these soft health checks hide hard-label LogLoss tail risk.

## Method

- Use mixmin as the active frontier.
- For every cell, compute candidate-minus-mixmin LogLoss delta for hard label `0` and hard label `1`.
- Define the E72-adverse hard label as the label that would make E72's move wrong in that cell.
- Measure each candidate's exposure to that same adverse label direction.
- Merge E92 posterior CE and E93 target-manifold health only as context, not as a fitted score.

## Decision

Hard-label E72-adverse tail exposure supports E89 as the lower-downside sensor among E86/E90/E89, with E85 as the conservative floor and E86 as the max-upside soft-health candidate.

## E72 Miss Scale

- E72 public miss vs mixmin: `0.0001011367`.
- E72 active moved cells: `893` / `1750`.
- If every E72 active cell had the E72-adverse label, E72 positive exposure all-cells is `0.002330945`.
- The observed public miss is only `0.043389` of that full-exposure scale.

## Live Candidate Tail Risk

| role | e72_adverse_positive_exposure_all | e72_adverse_weighted_positive_mean | e72_adverse_positive_weight_frac | e72_same_direction_weight_frac | soft_health_gain_sum | posterior_ce_delta_all_vs_mixmin | target_manifold_delta_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| conservative_e85 | 0.000739201 | 0.002410231 | 0.303417829 | 0.303417829 | 0.000949136 | -0.000207023 | -0.000742113 |
| min_contam_e89 | 0.000799109 | 0.002497430 | 0.307258068 | 0.307258068 | 0.001042370 | -0.000235903 | -0.000806467 |
| noq2_contrast | 0.000906798 | 0.002924102 | 0.315626800 | 0.319846374 | 0.001171380 | -0.000257196 | -0.000914184 |
| balanced_e90 | 0.000934031 | 0.002988389 | 0.371819468 | 0.373015002 | 0.001128712 | -0.000250767 | -0.000877945 |
| max_upside_e86 | 0.001010242 | 0.003325247 | 0.408084922 | 0.409280455 | 0.001177404 | -0.000255621 | -0.000921783 |

## Live Candidate Soft-Health Order

| role | soft_health_gain_sum | e72_adverse_positive_exposure_all | kl_if_mixmin_calibrated | hard_worst_tail_mean | entropy_delta_vs_mixmin |
| --- | --- | --- | --- | --- | --- |
| max_upside_e86 | 0.001177404 | 0.001010242 | 0.000013335 | 0.002923078 | 0.000068710 |
| noq2_contrast | 0.001171380 | 0.000906798 | 0.000013742 | 0.002820289 | 0.000042608 |
| balanced_e90 | 0.001128712 | 0.000934031 | 0.000012517 | 0.002791944 | 0.000057706 |
| min_contam_e89 | 0.001042370 | 0.000799109 | 0.000011194 | 0.002650950 | 0.000019066 |
| conservative_e85 | 0.000949136 | 0.000739201 | 0.000009255 | 0.002300434 | 0.000032229 |

## Known Public Anchor Snapshot

| role | public_lb | public_delta_vs_mixmin | e72_adverse_positive_exposure_all | kl_if_mixmin_calibrated | hard_worst_tail_mean | soft_health_gain_sum |
| --- | --- | --- | --- | --- | --- | --- |
| frontier_mixmin | 0.576306641 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | -0.000000000 |
| failed_e72 | 0.576407777 | 0.000101137 | 0.002330945 | 0.000010407 | 0.002330945 | 0.001755987 |
| previous_a2c8 | 0.577439321 | 0.001132680 | 0.004146123 | 0.000290920 | 0.022549114 | -0.000000000 |
| raw05 | 0.577526307 | 0.001219667 | 0.003864338 | 0.000325557 | 0.025064679 | -0.000000000 |
| stage2 | 0.577944976 | 0.001638335 | 0.005983139 | 0.000664886 | 0.032916215 | 0.001093162 |
| ordinal_q | 0.578303365 | 0.001996725 | 0.012885880 | 0.003050076 | 0.063283181 | -0.000000000 |
| final9 | 0.578427353 | 0.002120712 | 0.025058260 | 0.004134252 | 0.070134214 | 0.020801364 |
| bad_q2_jepa | 0.579801286 | 0.003494646 | 0.007744391 | 0.002427909 | 0.046161236 | 0.002958703 |
| bad_lejepa | 0.580246819 | 0.003940179 | 0.011812808 | 0.002981883 | 0.062283030 | -0.000000000 |
| bad_residual_jepa | 0.581227328 | 0.004920687 | 0.011039848 | 0.003185001 | 0.068789741 | -0.000000000 |

## Known Public Sanity Correlation

| metric | spearman_public_lb |
| --- | --- |
| e72_adverse_positive_exposure_all | 0.793939 |
| kl_if_mixmin_calibrated | 0.866667 |
| hard_worst_tail_mean | 0.866667 |
| soft_health_gain_sum | 0.081935 |

## Interpretation

- E72 can look good under soft posterior/target-manifold objectives while requiring only a small realized hard-label tail to miss public.
- E86 has the largest live soft-health gain and a larger E72-adverse tail than E90/E89, so it remains an upside sensor rather than a low-risk file.
- E89 lowers E72-adverse tail by sacrificing soft-health and hidden/world/block edge; E90 is the row-coherent middle point.
- This audit does not create a public score forecast. It explains why soft JEPA-like health metrics need a hard-label tail check.

## Outputs

- `e94_soft_health_hard_tail_scores.csv`
- `e94_soft_health_hard_tail_target_detail.csv`
