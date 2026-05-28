# E69 Q2/S3 Strict-Cell Amplitude Probe

## Observe

E68 validates many Q2/S3 tail-gated cells outside same-anchor construction, but their held-out edge is only `1e-6` scale.

## Wonder

Can the independently validated Q2/S3 cells be amplified while preserving held-out, train, hidden, world, and block stress?

## Method

- E68 strict pairs used: `155`.
- Alpha grid over Q2/S3 logit delta: `[0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 24.0]`.
- Unique predictions scored: `2061`.
- Non-Q2/S3 targets stay fixed at the matched `no_q2_s3` base.
- Strict amplitude gate requires heldout/train/all beats, heldout tail neutrality, full-combo margin vs mixmin, hidden/world/block support, and raw-energy non-worsening.

## Summary

| alpha | n | heldout_beats_base | heldout_tail_neutral | train_beats_base | all_beats_base | all_margin_vs_mixmin | strict_amplitude_gate | beats_alpha1_on_all | best_all_delta_vs_mixmin | best_all_minus_base | median_all_minus_base | best_heldout_minus_base | median_heldout_minus_base | best_world_support_minus_base | best_hidden_q2s3_minus_base | best_block_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 155 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | -5.08172e-06 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0.5 | 155 | 155 | 155 | 155 | 155 | 0 | 0 | 0 | -5.69259e-06 | -1.45518e-06 | -4.07441e-07 | -7.54268e-07 | -1.96865e-07 | -6.12034e-05 | -5.50074e-05 | 0.888889 |
| 1 | 155 | 155 | 155 | 155 | 155 | 0 | 0 | 0 | -6.42421e-06 | -2.55723e-06 | -7.91609e-07 | -1.26082e-06 | -3.68888e-07 | -0.000122113 | -0.000109229 | 0.888889 |
| 1.25 | 155 | 152 | 152 | 155 | 155 | 0 | 0 | 155 | -6.7899e-06 | -2.97092e-06 | -9.75012e-07 | -1.47747e-06 | -4.54707e-07 | -0.000152557 | -0.000136045 | 0.888889 |
| 1.5 | 155 | 150 | 147 | 155 | 155 | 0 | 0 | 155 | -7.11064e-06 | -3.31171e-06 | -1.1598e-06 | -1.65943e-06 | -5.36238e-07 | -0.000181784 | -0.000162664 | 0.888889 |
| 2 | 155 | 144 | 137 | 155 | 155 | 0 | 0 | 155 | -7.61337e-06 | -3.76969e-06 | -1.50646e-06 | -1.84317e-06 | -6.86301e-07 | -0.000241596 | -0.00021531 | 0.888889 |
| 3 | 155 | 135 | 118 | 155 | 155 | 0 | 0 | 155 | -8.15945e-06 | -3.91875e-06 | -2.11145e-06 | -1.8579e-06 | -9.3314e-07 | -0.000358867 | -0.000318233 | 0.888889 |
| 4 | 155 | 125 | 102 | 155 | 155 | 0 | 0 | 152 | -8.14336e-06 | -3.92504e-06 | -2.53409e-06 | -2.18509e-06 | -9.84157e-07 | -0.000472171 | -0.000417988 | 0.888889 |
| 6 | 155 | 115 | 84 | 152 | 151 | 0 | 0 | 142 | -8.32553e-06 | -4.0764e-06 | -2.87904e-06 | -2.9813e-06 | -8.36153e-07 | -0.000692649 | -0.000607955 | 0.888889 |
| 8 | 155 | 92 | 69 | 148 | 137 | 0 | 0 | 131 | -8.7556e-06 | -4.43765e-06 | -3.0223e-06 | -3.66517e-06 | -4.72256e-07 | -0.000911911 | -0.000785135 | 0.888889 |
| 10 | 155 | 76 | 60 | 137 | 122 | 0 | 0 | 117 | -9.0266e-06 | -4.41021e-06 | -2.94524e-06 | -4.31962e-06 | 1.28946e-07 | -0.00112797 | -0.000949457 | 0.888889 |
| 12 | 155 | 56 | 49 | 118 | 113 | 0 | 0 | 105 | -9.16676e-06 | -4.4355e-06 | -3.00721e-06 | -4.8459e-06 | 1.23383e-06 | -0.00133649 | -0.00110085 | 0.888889 |
| 16 | 155 | 40 | 37 | 101 | 86 | 0 | 0 | 83 | -8.94934e-06 | -4.49685e-06 | -1.29157e-06 | -5.4851e-06 | 4.52041e-06 | -0.00173041 | -0.00136458 | 0.888889 |
| 24 | 155 | 26 | 22 | 63 | 51 | 0 | 0 | 45 | -9.1779e-06 | -4.47881e-06 | 8.05256e-06 | -5.7776e-06 | 1.67705e-05 | -0.00242803 | -0.00193047 | 0.888889 |

## Best Full-Combo Rows

| heldout_set | translator | alpha | all_delta_vs_mixmin | all_minus_base | heldout_minus_base | train_minus_base | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | strict_amplitude_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inverse_top | tail_soft_max_m1.00 | 24 | -9.1779e-06 | -4.47881e-06 | -4.90601e-06 | -4.26521e-06 | -0.00029944 | -0.000297043 | 0.694444 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -9.16676e-06 | -4.42861e-06 | -1.04709e-06 | -6.11937e-06 | -0.000365153 | -0.000314978 | 0.722222 | False |
| inverse_top | tail_soft_p90_m0.50 | 24 | -9.16676e-06 | -4.42861e-06 | -1.04709e-06 | -6.11937e-06 | -0.000365153 | -0.000314978 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 24 | -9.12489e-06 | -4.43475e-06 | -5.74871e-06 | -3.77777e-06 | -0.000307852 | -0.000326363 | 0.666667 | False |
| inverse_top | tail_soft_max_m1.00 | 24 | -9.12142e-06 | -4.38327e-06 | -4.92777e-06 | -4.11103e-06 | -0.000315024 | -0.000318892 | 0.694444 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -9.10806e-06 | -4.40897e-06 | -1.24337e-06 | -5.99177e-06 | -0.000340924 | -0.00029271 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 24 | -9.10365e-06 | -4.33289e-06 | -5.7776e-06 | -3.61053e-06 | -0.000334517 | -0.000353289 | 0.666667 | False |
| inverse_top | tail_soft_p90_m1.00 | 10 | -9.0266e-06 | -4.28845e-06 | -1.43478e-06 | -5.71529e-06 | -0.000304557 | -0.000264482 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 24 | -9.00185e-06 | -4.47853e-06 | -4.90858e-06 | -4.2635e-06 | -0.000300287 | -0.000297043 | 0.694444 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -8.9836e-06 | -4.42775e-06 | -1.05469e-06 | -6.11428e-06 | -0.000366858 | -0.000314978 | 0.722222 | False |
| inverse_top | tail_soft_p90_m0.50 | 24 | -8.9836e-06 | -4.42775e-06 | -1.05469e-06 | -6.11428e-06 | -0.000366858 | -0.000314978 | 0.722222 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -8.95882e-06 | -4.4355e-06 | -1.25495e-06 | -6.02577e-06 | -0.000342365 | -0.00029271 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 24 | -8.95867e-06 | -4.40283e-06 | -4.93226e-06 | -4.13811e-06 | -0.000316729 | -0.000318892 | 0.694444 | False |
| inverse_top | tail_soft_p90_m1.00 | 16 | -8.94934e-06 | -4.25025e-06 | -1.45656e-07 | -6.30255e-06 | -0.000453792 | -0.000384827 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 16 | -8.94001e-06 | -4.20186e-06 | -4.38846e-06 | -4.10856e-06 | -0.000213768 | -0.000217024 | 0.694444 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -8.93587e-06 | -4.1651e-06 | -1.76794e-06 | -5.36369e-06 | -0.000355347 | -0.000332293 | 0.666667 | False |
| inverse_top | tail_soft_p90_m1.00 | 10 | -8.89289e-06 | -4.19381e-06 | -1.51591e-06 | -5.53275e-06 | -0.00028441 | -0.000245628 | 0.722222 | False |
| inverse_top | tail_soft_p90_m1.00 | 10 | -8.88189e-06 | -4.32605e-06 | -1.44047e-06 | -5.76884e-06 | -0.000306262 | -0.000264482 | 0.722222 | False |
| inverse_top | tail_soft_max_m1.00 | 16 | -8.88006e-06 | -4.1093e-06 | -4.97005e-06 | -3.67892e-06 | -0.000222973 | -0.00023962 | 0.666667 | False |
| inverse_top | tail_soft_p90_m1.00 | 12 | -8.84741e-06 | -4.15727e-06 | -1.99119e-06 | -5.24031e-06 | -0.000325043 | -0.000306062 | 0.666667 | False |

## Decision

- Strict amplitude gates are `0`. E68 validates Q2/S3 cell direction, but simple alpha amplification still fails to create selector-scale probability movement.
- No submission file is produced.

## Outputs

- `analysis_outputs/q2_s3_strict_cell_amplitude_probe_scan.csv`
- `analysis_outputs/q2_s3_strict_cell_amplitude_probe_summary.csv`
