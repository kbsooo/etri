# E128 Transfer-shrinkage energy candidate audit

## Question

E127 showed that tail-neutral / low-alpha density predicts the E101-compatible
cell budget. E128 asks whether that energy explains known public anchors and
usefully triages live candidates.

## Known Public Anchors

| name | role | public_delta_vs_e95 | tail_equal_law_cosine | tail_equal_law_projection | tail_equal_law_resid_ratio | e101_active_delta95_l1 | q2s3_delta95_l1 | e72_adverse_exposure_e101_plausible | transfer_shrinkage_risk_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e95 | known_public | 0.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.001557 | -0.999221 |
| e101 | known_public | 0.000009 | 1.000000 | 1.000000 | 0.000000 | 0.010792 | 0.001079 | 0.001543 | -0.987357 |
| mixmin | known_public | 0.000015 | 0.000000 | 0.000000 | 1.000000 | 0.043170 | 0.004317 | 0.000000 | 0.047487 |
| failed_e72 | known_public | 0.000116 | 0.024468 | 0.041455 | 1.946178 | 0.015921 | 0.003286 | 0.007634 | -0.001444 |
| a2c8 | known_public | 0.001148 | 0.684978 | 3.413671 | 4.359945 | 0.036700 | 0.040400 | 0.010517 | -0.602619 |
| raw_timeline | known_public | 0.001235 | 0.649402 | 3.330471 | 4.543215 | 0.040250 | 0.044225 | 0.009511 | -0.560171 |
| stage2 | known_public | 0.001654 | 0.513652 | 3.684892 | 6.715288 | 0.058701 | 0.055335 | 0.013385 | -0.392924 |
| ordinal | known_public | 0.002012 | 0.113117 | 2.076928 | 18.274722 | 0.112066 | 0.080763 | 0.025203 | 0.092313 |
| final9 | known_public | 0.002136 | -0.128465 | -2.329759 | 18.290761 | 0.175425 | 0.138603 | 0.046004 | 0.465495 |
| q2_bad | known_public | 0.003510 | 0.277091 | 3.684892 | 13.056796 | 0.111541 | 0.149321 | 0.024872 | -0.003793 |
| lejepa_bad | known_public | 0.003955 | 0.296974 | 5.112094 | 16.943922 | 0.077873 | 0.099436 | 0.021460 | -0.108935 |
| resid_bad | known_public | 0.004936 | 0.489869 | 8.092128 | 16.052800 | 0.134525 | 0.145880 | 0.028773 | -0.195077 |

## Live Candidate Triage

| name | role | public_delta_vs_e95 | tail_equal_law_cosine | tail_equal_law_projection | tail_equal_law_resid_ratio | e101_active_delta95_l1 | q2s3_delta95_l1 | e72_adverse_exposure_e101_plausible | transfer_shrinkage_risk_index |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e85 | live_candidate |  | 0.994651 | 0.871458 | 0.157206 | 0.003562 | 0.000356 | 0.001496 | -0.989984 |
| e89 | live_candidate |  | 0.988304 | 0.955022 | 0.154073 | 0.003562 | 0.000356 | 0.001686 | -0.983543 |
| noq2 | live_candidate |  | 0.993839 | 1.082730 | 0.146372 | 0.009608 | 0.000961 | 0.001882 | -0.982328 |
| e90 | live_candidate |  | 0.903679 | 1.063746 | 0.508075 | 0.002317 | 0.000730 | 0.002449 | -0.899407 |
| e86 | live_candidate |  | 0.830872 | 1.082606 | 0.729748 | 0.002404 | 0.001239 | 0.003258 | -0.825599 |

## Public Correlation of Key Metrics

| metric | spearman_public_delta | pearson_public_delta | e95_value | e101_value | mixmin_value | failed_e72_value |
| --- | --- | --- | --- | --- | --- | --- |
| q2s3_delta95_l1 | 0.958042 | 0.906271 | 0.000000 | 0.001079 | 0.004317 | 0.003286 |
| tail_equal_law_resid_ratio | 0.888112 | 0.833894 | 0.000000 | 0.000000 | 1.000000 | 1.946178 |
| e72_adverse_exposure_e101_plausible | 0.881119 | 0.716347 | 0.001557 | 0.001543 | 0.000000 | 0.007634 |
| e101_active_delta95_l1 | 0.874126 | 0.739375 | 0.000000 | 0.010792 | 0.043170 | 0.015921 |
| tail_equal_law_projection | 0.622378 | 0.717531 | 1.000000 | 1.000000 | 0.000000 | 0.041455 |
| transfer_shrinkage_risk_index | 0.440559 | 0.405635 | -0.999221 | -0.987357 | 0.047487 | -0.001444 |
| tail_equal_law_cosine | -0.374782 | -0.220426 | 1.000000 | 1.000000 | 0.000000 | 0.024468 |

## Interpretation

- E95 has tail-equal law cosine `1.000000` by construction; mixmin is `0.000000` because it has no E95 law movement.
- E101 preserves the E95 law on tail-neutral cells but pays active rollback: E101-active delta95 L1 `0.010792`.
- The energy is useful as a veto/diagnostic: it separates E101's active rollback from E95 and keeps q2s3/active movement explicit.
- The energy is not sufficient as a public selector: known-public correlations are not enough to rank all bad anchors, and live candidates still require the E124/E126 public-world stress.

Lowest-risk live candidate by this index is `e85`, but it remains a diagnostic ranking, not a submit gate.

## Decision

No submission. Transfer-shrinkage energy is promoted to a candidate-risk
component, not a standalone ranker. A future candidate must satisfy this energy
plus E124/E126 stress and must show selector-scale expected movement.
