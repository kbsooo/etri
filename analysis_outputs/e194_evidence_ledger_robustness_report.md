# E194 Evidence Ledger Robustness

## Question

Is E193's E176-first decision robust, or is it an artifact of arbitrary evidence weights?

## Result

E176 remains first under every single-source leaveout and wins most random family-weight perturbations. The result is not unconditional: if non-comparable visible/top-cell evidence is removed and the antisymmetric pair sensor is discounted below about `0.725` of its E193 weight, E154 becomes the stronger repaired-branch worldview.

Baseline E176 balance is `3.1` versus E154 `-0.225` and E144 `-1.725`.

## Leaveout Stress

Single-source leaveout E176 win rate: `1`.

| scenario | dropped_families | winner | e176_balance | e154_balance | e144_balance | e176_minus_e154 | e176_minus_e144 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline |  | e176 | 3.1 | -0.225 | -1.725 | 3.325 | 4.825 |
| drop_antisymmetric_pair | antisymmetric_pair | e176 | 1.6 | 1.275 | -0.225 | 0.325 | 1.825 |
| drop_binary_world | binary_world | e176 | 5.6 | -2.1 | -3.6 | 7.7 | 9.2 |
| drop_clean_e72_tail | clean_e72_tail | e176 | 1.85 | -1.475 | -1.475 | 3.325 | 3.325 |
| drop_known_winner_topcell | known_winner_topcell | e176 | 2.6 | -0.225 | -1.725 | 2.825 | 4.325 |
| drop_pressure_branch | pressure_branch | e176 | 2.75 | 1.625 | 0.125 | 1.125 | 2.625 |
| drop_visible_body_q2 | visible_body_q2 | e176 | 1.1 | -0.225 | -1.725 | 1.325 | 2.825 |
| drop_visible_plus_topcell | known_winner_topcell,visible_body_q2 | e176 | 0.6 | -0.225 | -1.725 | 0.825 | 2.325 |
| drop_visible_topcell_pair | antisymmetric_pair,known_winner_topcell,visible_body_q2 | e154 | -0.9 | 1.275 | -0.225 | -2.175 | -0.675 |
| drop_binary_and_local_pressure | binary_world,pressure_branch | e176 | 5.25 | -0.25 | -1.75 | 5.5 | 7 |
| drop_antisymmetric_pair+binary_world | antisymmetric_pair,binary_world | e176 | 4.1 | -0.6 | -2.1 | 4.7 | 6.2 |
| drop_antisymmetric_pair+clean_e72_tail | antisymmetric_pair,clean_e72_tail | e176 | 0.35 | 0.025 | 0.025 | 0.325 | 0.325 |
| drop_antisymmetric_pair+known_winner_topcell | antisymmetric_pair,known_winner_topcell | e154 | 1.1 | 1.275 | -0.225 | -0.175 | 1.325 |
| drop_antisymmetric_pair+pressure_branch | antisymmetric_pair,pressure_branch | e154 | 1.25 | 3.125 | 1.625 | -1.875 | -0.375 |
| drop_antisymmetric_pair+visible_body_q2 | antisymmetric_pair,visible_body_q2 | e154 | -0.4 | 1.275 | -0.225 | -1.675 | -0.175 |
| drop_binary_world+clean_e72_tail | binary_world,clean_e72_tail | e176 | 4.35 | -3.35 | -3.35 | 7.7 | 7.7 |

## Monte Carlo Weight Stress

| design | n | e176_win_rate | e154_win_rate | e144_win_rate | e176_margin_mean | e176_margin_p05 | e176_margin_p50 | e176_margin_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_loguniform_0p25_4 | 20000 | 0.7713 | 0.2287 | 0 | 4.51864062 | -6.51173306 | 4.73851711 | 14.5245145 |
| family_loguniform_0p5_2 | 20000 | 0.90595 | 0.09405 | 0 | 3.57897611 | -0.849285227 | 3.66570424 | 7.79211385 |
| family_dropout_20pct | 20000 | 0.8965 | 0.1035 | 0 | 2.6634475 | -1.675 | 3.325 | 7.7 |

## Family-Alone Stress

| family | winner_if_alone | e176_balance | e154_balance | e144_balance | e176_minus_e154 | e176_minus_e144 |
| --- | --- | --- | --- | --- | --- | --- |
| antisymmetric_pair | e176 | 1.5 | -1.5 | -1.5 | 3 | 3 |
| binary_world | e154 | -2.5 | 1.875 | 1.875 | -4.375 | -4.375 |
| clean_e72_tail | e176 | 1.25 | 1.25 | -0.25 | 0 | 1.5 |
| known_winner_topcell | e176 | 0.5 | 0 | 0 | 0.5 | 0.5 |
| pressure_branch | e176 | 0.35 | -1.85 | -1.85 | 2.2 | 2.2 |
| visible_body_q2 | e176 | 2 | 0 | 0 | 2 | 2 |

## Missing-Penalty Stress

| missing_penalty | winner | e176_balance | e154_balance | e144_balance | e176_minus_e154 | e176_minus_e144 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | e176 | 3.1 | -0.225 | -1.725 | 3.325 | 4.825 |
| -0.1 | e176 | 3.1 | -0.525 | -2.025 | 3.625 | 5.125 |
| -0.25 | e176 | 3.1 | -0.975 | -2.475 | 4.075 | 5.575 |
| -0.5 | e176 | 3.1 | -1.725 | -3.225 | 4.825 | 6.325 |
| -1 | e176 | 3.1 | -3.225 | -4.725 | 6.325 | 7.825 |
| -2 | e176 | 3.1 | -6.225 | -7.725 | 9.325 | 10.825 |

## Adversarial Thresholds

| family_scaled | challenger | baseline_e176_minus_challenger | family_diff_component | non_family_diff_component | flip_multiplier | interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| antisymmetric_pair | e154 | 3.325 | 3 | 0.325 | -0.108333333 | cannot flip by positive multiplier alone |
| antisymmetric_pair | e144 | 4.825 | 3 | 1.825 | -0.608333333 | cannot flip by positive multiplier alone |
| binary_world | e154 | 3.325 | -4.375 | 7.7 | 1.76 | positive multiplier can flip ranking |
| binary_world | e144 | 4.825 | -4.375 | 9.2 | 2.10285714 | positive multiplier can flip ranking |
| clean_e72_tail | e154 | 3.325 | 0 | 3.325 | NA | family has no relative effect |
| clean_e72_tail | e144 | 4.825 | 1.5 | 3.325 | -2.21666667 | cannot flip by positive multiplier alone |
| known_winner_topcell | e154 | 3.325 | 0.5 | 2.825 | -5.65 | cannot flip by positive multiplier alone |
| known_winner_topcell | e144 | 4.825 | 0.5 | 4.325 | -8.65 | cannot flip by positive multiplier alone |
| pressure_branch | e154 | 3.325 | 2.2 | 1.125 | -0.511363636 | cannot flip by positive multiplier alone |
| pressure_branch | e144 | 4.825 | 2.2 | 2.625 | -1.19318182 | cannot flip by positive multiplier alone |
| visible_body_q2 | e154 | 3.325 | 2 | 1.325 | -0.6625 | cannot flip by positive multiplier alone |
| visible_body_q2 | e144 | 4.825 | 2 | 2.825 | -1.4125 | cannot flip by positive multiplier alone |
| antisymmetric_pair_after_dropping_noncomparable_visible | e154 | 0.825 | 3 | -2.175 | 0.725 | conservative stress: pair evidence must stay above this multiplier |
| antisymmetric_pair_after_dropping_noncomparable_visible | e144 | 2.325 | 3 | -0.675 | 0.225 | conservative stress: pair evidence must stay above this multiplier |

## Interpretation

- E176's first-slot status is robust to ordinary weight uncertainty.
- The most important challenger is not E144; it is E154 under a high-trust binary-world / low-trust pair-geometry worldview.
- E181 binary-world evidence would flip E176 versus E154 if its family weight were multiplied above `1.76` while all other families stayed fixed.
- If E176-only visible/top-cell evidence is excluded as non-comparable, E176 still leads, but then it depends materially on the antisymmetric pair geometry staying above about `0.725` of its current weight.
- This means E176 is a robust sensor-priority choice, not a theorem. The live alternative remains: trust inherited binary worlds more than pair/visible/clean-shape geometry and submit an E154-style repaired-branch sensor instead.

## Decision

No new submission is created. E176 remains the next single public sensor by robustness stress. The exact worldview is now more explicit: E176 bets that pair/shape/broad-body evidence is not a shortcut, while E154 bets that inherited binary-world counterprior is the cleaner hidden-label proxy.
