# E67 Tail-Neutral Q2/S3 Translator Probe

## Observe

E66 split Q2/S3 into a hidden/mean-positive signal and a robust-anchor tail risk. A target mask alone cannot decide this conflict.

## Wonder

Can Q2/S3 be partially added back only where first-order public-anchor scenario tails are neutral, beating the `no_q2_s3` pocket without expanding the max-set tail?

## Method

- Generated candidates: `7632`.
- Non-Q2/S3 targets keep the E65 move; Q2/S3 are added by uniform small weights or anchor-tail gates.
- Tail gates use first-order BCE derivative `(mixmin - scenario) * teacher_delta` over the existing anchor scenario/mask family.
- Scored actual-anchor, hidden-rate validation, and matched same-configuration deltas versus `no_q2_s3`.

## Summary

| translator | n | anchor_beats_mixmin | anchor_margin | hidden_guard | best_anchor_delta | median_anchor_delta | best_max_set_delta_vs_mixmin | best_hidden_core_delta | best_q2_gate_mean | best_s3_gate_mean | best_candidate | beats_base | tail_neutral_beats_base | best_anchor_minus_base | median_anchor_minus_base | best_max_set_minus_base |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tail_meanneg_m1.00 | 432 | 387 | 0 | 432 | -6.93314e-06 | -2.81131e-06 | 9.70154e-06 | -0.0006453 | 0.268 | 0.208 | toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.095|c0.120 | 432 | 0 | -2.65903e-06 | -5.17273e-07 | 1.49402e-07 |
| tail_meanneg_m0.50 | 432 | 373 | 0 | 432 | -6.77841e-06 | -2.61867e-06 | 9.75751e-06 | -0.000716792 | 0.106 | 0.06 | toward_teacher|all|tail_meanneg_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 0 | -1.8187e-06 | -3.07272e-07 | 6.63772e-08 |
| tail_p90_nonpos_m1.00 | 432 | 360 | 0 | 432 | -6.58701e-06 | -2.69194e-06 | 7.97128e-06 | -0.000690471 | 0.032 | 0.028 | toward_teacher|all|tail_p90_nonpos_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 360 | -1.87206e-06 | -2.83159e-07 | -1.07191e-06 |
| tail_soft_p90_m1.00 | 432 | 358 | 0 | 432 | -6.45068e-06 | -2.50684e-06 | 8.21504e-06 | -0.000687379 | 0.0347773 | 0.0145404 | toward_teacher|all|tail_soft_p90_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 284 | -1.08154e-06 | -1.80924e-07 | -4.25254e-07 |
| tail_p90_nonpos_m0.50 | 432 | 346 | 0 | 432 | -6.31779e-06 | -2.49541e-06 | 8.03563e-06 | -0.000682294 | 0.016 | 0.014 | toward_teacher|all|tail_p90_nonpos_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 381 | -1.04878e-06 | -1.48048e-07 | -6.05145e-07 |
| tail_soft_max_m1.00 | 432 | 340 | 0 | 432 | -6.23258e-06 | -2.40531e-06 | 8.32399e-06 | -0.000681924 | 0.0189681 | 0.00957066 | toward_teacher|all|tail_soft_max_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 156 | -7.0429e-07 | -1.04295e-07 | -1.57253e-07 |
| tail_soft_p90_m0.50 | 432 | 341 | 0 | 432 | -6.23032e-06 | -2.37775e-06 | 8.19187e-06 | -0.000680705 | 0.0173887 | 0.0072702 | toward_teacher|all|tail_soft_p90_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 316 | -5.548e-07 | -9.19889e-08 | -2.27496e-07 |
| tail_soft_max_m0.50 | 432 | 332 | 0 | 432 | -6.11777e-06 | -2.33806e-06 | 8.25157e-06 | -0.000677972 | 0.00948406 | 0.00478533 | toward_teacher|all|tail_soft_max_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 432 | 168 | -3.60227e-07 | -5.31221e-08 | -8.6153e-08 |
| tail_max_nonpos_m1.00 | 360 | 298 | 0 | 360 | -6.05518e-06 | -2.6207e-06 | 8.13124e-06 | -0.000674939 | 0 | 0.004 | toward_teacher|all|tail_max_nonpos_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 360 | 288 | -7.17332e-07 | -7.18046e-08 | -4.53379e-07 |
| tail_max_nonpos_m0.50 | 360 | 298 | 0 | 360 | -6.02594e-06 | -2.55717e-06 | 8.15814e-06 | -0.000674477 | 0 | 0.002 | toward_teacher|all|tail_max_nonpos_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 360 | 288 | -3.77884e-07 | -3.64129e-08 | -2.27997e-07 |
| no_q2_s3 | 432 | 328 | 0 | 432 | -5.99494e-06 | -2.28245e-06 | 8.1875e-06 | -0.000674013 | 0 | 0 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 0 | 0 | 0 | 0 | 0 |
| uniform_q20.05_s30.05 | 432 | 324 | 0 | 432 | -5.9648e-06 | -2.259e-06 | 8.57828e-06 | -0.000681067 | 0.05 | 0.05 | toward_teacher|all|uniform_q20.05_s30.05|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 0 | 0 | 3.08439e-09 | 2.04921e-08 | 4.20714e-08 |
| uniform_q20.10_s30.10 | 432 | 319 | 0 | 432 | -5.92362e-06 | -2.2111e-06 | 8.98028e-06 | -0.00068811 | 0.1 | 0.1 | toward_teacher|all|uniform_q20.10_s30.10|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 0 | 0 | 7.37261e-09 | 4.32391e-08 | 8.44564e-08 |
| uniform_q20.20_s30.00 | 432 | 313 | 0 | 432 | -5.91338e-06 | -2.2649e-06 | 8.68786e-06 | -0.000694404 | 0.2 | 0 | toward_teacher|all|uniform_q20.20_s30.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 21 | 0 | -7.55614e-09 | 3.37894e-08 | 6.93199e-08 |
| uniform_q20.00_s30.20 | 432 | 324 | 0 | 432 | -5.90014e-06 | -2.13743e-06 | 9.31762e-06 | -0.000681772 | 0 | 0.2 | toward_teacher|all|uniform_q20.00_s30.20|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 10 | 0 | -2.11594e-08 | 6.03891e-08 | 8.29189e-08 |
| uniform_q20.20_s30.20 | 432 | 310 | 0 | 432 | -5.81389e-06 | -2.12056e-06 | 9.81799e-06 | -0.000702163 | 0.2 | 0.2 | toward_teacher|all|uniform_q20.20_s30.20|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 0 | 0 | 1.68949e-08 | 9.691e-08 | 1.70167e-07 |
| uniform_q20.35_s30.35 | 432 | 301 | 0 | 432 | -5.60154e-06 | -2.02277e-06 | 1.11573e-05 | -0.000723158 | 0.35 | 0.35 | toward_teacher|all|uniform_q20.35_s30.35|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | 0 | 0 | 3.64433e-08 | 1.90933e-07 | 3.00625e-07 |
| uniform_q21.00_s31.00 | 432 | 274 | 0 | 432 | -4.19324e-06 | -1.35733e-06 | 1.01305e-05 | -0.000543835 | 1 | 1 | toward_teacher|all|uniform_q21.00_s31.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | 0 | 0 | 1.76837e-07 | 8.01994e-07 | 8.92132e-07 |

## Matched Base Comparison

- `no_q2_s3` best anchor delta: `-5.99494353e-06`.
- translators beating matched `no_q2_s3`: `4207/7200`.
- translators beating matched `no_q2_s3` with max-set tail neutral: `2241/7200`.

| band | base_cell_gate | gradient_gate | row_gate | shape | scale | cap | translator | base_anchor_delta | translator_anchor_delta | anchor_minus_base | max_set_minus_base | hidden_core_minus_base | q2_hidden_minus_base | s3_hidden_minus_base |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| low_slack_half | all | grad_core_top50 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -3.58333e-06 | -5.45538e-06 | -1.87206e-06 | -9.18081e-07 | -2.76608e-05 | -8.63302e-05 | -0.000107296 |
| low_slack_half | raw_agree | grad_all_4of6 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -4.1471e-06 | -6.00956e-06 | -1.86247e-06 | -1.07191e-06 | -2.28621e-05 | -8.63302e-05 | -7.37043e-05 |
| low_slack_half | all | grad_all_4of6 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -3.92084e-06 | -5.76772e-06 | -1.84688e-06 | -1.02514e-06 | -2.28621e-05 | -8.63302e-05 | -7.37043e-05 |
| all | all | grad_all_4of6 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -3.39618e-06 | -5.21504e-06 | -1.81886e-06 | -1.06541e-06 | -2.18946e-05 | -8.63302e-05 | -6.69319e-05 |
| all | raw_agree | grad_all_4of6 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -3.82284e-06 | -5.6244e-06 | -1.80155e-06 | -9.75488e-07 | -2.18946e-05 | -8.63302e-05 | -6.69319e-05 |
| low_slack_half | raw_agree | grad_core_top50 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -4.35543e-06 | -6.13055e-06 | -1.77512e-06 | -9.55418e-07 | -2.61825e-05 | -8.63302e-05 | -9.69472e-05 |
| low_slack_half | raw_agree | grad_all_4of6 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.73815e-06 | -6.17885e-06 | -1.4407e-06 | -8.8631e-07 | -1.67871e-05 | -6.32866e-05 | -5.42234e-05 |
| all | all | grad_core_top50 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -4.23989e-06 | -5.68019e-06 | -1.4403e-06 | -9.47782e-07 | -2.42242e-05 | -8.63302e-05 | -8.32394e-05 |
| low_slack_half | all | grad_all_4of6 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.55585e-06 | -5.99527e-06 | -1.43942e-06 | -8.82448e-07 | -1.67871e-05 | -6.32866e-05 | -5.42234e-05 |
| low_slack_half | all | grad_core_top50 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.2407e-06 | -5.64871e-06 | -1.40802e-06 | -7.90753e-07 | -2.0294e-05 | -6.32866e-05 | -7.87716e-05 |
| all | raw_agree | grad_core_top50 | all | flat | 0.13 | 0.12 | tail_p90_nonpos_m1.00 | -4.71822e-06 | -6.12615e-06 | -1.40793e-06 | -9.64358e-07 | -2.27459e-05 | -8.63302e-05 | -7.28909e-05 |
| all | raw_agree | grad_all_4of6 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.59801e-06 | -5.98142e-06 | -1.38342e-06 | -7.96016e-07 | -1.60765e-05 | -6.32866e-05 | -4.92486e-05 |
| all | all | grad_all_4of6 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.36787e-06 | -5.74124e-06 | -1.37337e-06 | -8.03254e-07 | -1.60765e-05 | -6.32866e-05 | -4.92486e-05 |
| low_slack_half | raw_agree | grad_core_top50 | all | flat | 0.095 | 0.12 | tail_p90_nonpos_m1.00 | -4.77077e-06 | -6.12303e-06 | -1.35227e-06 | -7.57699e-07 | -1.92072e-05 | -6.32866e-05 | -7.11642e-05 |
| low_slack_half | raw_agree | grad_all_4of6 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.69909e-06 | -6.04415e-06 | -1.34506e-06 | -8.22803e-07 | -1.5421e-05 | -5.77784e-05 | -5.01689e-05 |
| low_slack_half | all | grad_all_4of6 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.52332e-06 | -5.86676e-06 | -1.34344e-06 | -8.1842e-07 | -1.5421e-05 | -5.77784e-05 | -5.01689e-05 |
| all | raw_agree | grad_all_4of6 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.53551e-06 | -5.84968e-06 | -1.31418e-06 | -7.7887e-07 | -1.48443e-05 | -5.77784e-05 | -4.61314e-05 |
| low_slack_half | all | grad_core_top50 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.21832e-06 | -5.52779e-06 | -1.30947e-06 | -7.59976e-07 | -1.86155e-05 | -5.77784e-05 | -7.25305e-05 |
| all | all | grad_all_4of6 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.27407e-06 | -5.57965e-06 | -1.30559e-06 | -7.78923e-07 | -1.48443e-05 | -5.77784e-05 | -4.61314e-05 |
| low_slack_half | raw_agree | grad_core_top50 | all | flat | 0.13 | 0.08 | tail_p90_nonpos_m1.00 | -4.69014e-06 | -5.96746e-06 | -1.27732e-06 | -7.05085e-07 | -1.76227e-05 | -5.77784e-05 | -6.55806e-05 |

## Top Candidates

| candidate | translator | anchor_delta_vs_mixmin | mean_actual_anchor | max_set_score | hidden_core_mean_delta | hidden_core_delta_Q2 | hidden_core_delta_S3 | q2_gate_mean | s3_gate_mean | mean_abs_logit_move_vs_mixmin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.93314e-06 | 0.577589 | 0.578047 | -0.0006453 | -0.000325729 | -0.000189279 | 0.268 | 0.208 | 0.0048518 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.91545e-06 | 0.577589 | 0.578047 | -0.000635421 | -0.000314429 | -0.000208225 | 0.252 | 0.224 | 0.00485038 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_all_4of6|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.83435e-06 | 0.577588 | 0.578048 | -0.000645982 | -0.000329262 | -0.000193016 | 0.296 | 0.232 | 0.00520914 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.130|c0.120 | tail_meanneg_m1.00 | -6.82957e-06 | 0.577587 | 0.578054 | -0.000880406 | -0.000443722 | -0.000257841 | 0.268 | 0.208 | 0.0066393 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.79228e-06 | 0.577589 | 0.578046 | -0.000593169 | -0.00029853 | -0.000172862 | 0.268 | 0.208 | 0.00444894 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | tail_meanneg_m1.00 | -6.7912e-06 | 0.577588 | 0.57805 | -0.000758937 | -0.000406842 | -0.000187628 | 0.212 | 0.12 | 0.0049296 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.78169e-06 | 0.577589 | 0.578046 | -0.00058496 | -0.000288662 | -0.000195128 | 0.252 | 0.224 | 0.00445271 |
| toward_teacher|all|tail_meanneg_m0.50|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | tail_meanneg_m0.50 | -6.77841e-06 | 0.577589 | 0.578047 | -0.000716792 | -0.000204911 | -9.45421e-05 | 0.106 | 0.06 | 0.00455966 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_all_4of6|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.75647e-06 | 0.577588 | 0.578049 | -0.000659669 | -0.000334613 | -0.000192168 | 0.3 | 0.252 | 0.00534909 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|flat|s0.130|c0.120 | tail_meanneg_m1.00 | -6.75098e-06 | 0.577587 | 0.578054 | -0.000866902 | -0.000428389 | -0.000283701 | 0.252 | 0.224 | 0.00663736 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_all_4of6|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.74794e-06 | 0.577589 | 0.578047 | -0.000598572 | -0.000304698 | -0.000181554 | 0.296 | 0.232 | 0.00483838 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|all|grad_all_4of6|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.70195e-06 | 0.577588 | 0.578049 | -0.000649618 | -0.000330603 | -0.000193725 | 0.3 | 0.236 | 0.00529875 |
| toward_teacher|all|tail_meanneg_m1.00|all|grad_all_abs50|all|flat|s0.130|c0.120 | tail_meanneg_m1.00 | -6.67959e-06 | 0.577588 | 0.57805 | -0.000759387 | -0.000406842 | -0.000187628 | 0.212 | 0.12 | 0.00493851 |
| toward_teacher|all|tail_meanneg_m1.00|all|grad_core_top50|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.67129e-06 | 0.577589 | 0.578048 | -0.000648896 | -0.000325729 | -0.000198997 | 0.268 | 0.22 | 0.00492346 |
| toward_teacher|all|tail_meanneg_m0.50|all|grad_all_abs50|all|flat|s0.130|c0.120 | tail_meanneg_m0.50 | -6.65404e-06 | 0.577589 | 0.578048 | -0.000717242 | -0.000204911 | -9.45421e-05 | 0.106 | 0.06 | 0.00456857 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_all_4of6|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.64945e-06 | 0.577589 | 0.578047 | -0.000609908 | -0.000307368 | -0.000178353 | 0.3 | 0.252 | 0.00496674 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|all|grad_all_4of6|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.59442e-06 | 0.577589 | 0.578048 | -0.000602094 | -0.000306248 | -0.000182203 | 0.3 | 0.236 | 0.00492429 |
| toward_teacher|all|tail_p90_nonpos_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | tail_p90_nonpos_m1.00 | -6.58701e-06 | 0.57759 | 0.578046 | -0.000690471 | -8.35293e-05 | -3.16746e-05 | 0.032 | 0.028 | 0.00432343 |
| toward_teacher|all|tail_meanneg_m1.00|all|grad_all_4of6|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.57814e-06 | 0.577588 | 0.578049 | -0.000662404 | -0.000338572 | -0.000192876 | 0.308 | 0.256 | 0.00542827 |
| toward_teacher|all|tail_meanneg_m1.00|all|grad_core_top50|all|flat|s0.130|c0.080 | tail_meanneg_m1.00 | -6.56138e-06 | 0.577589 | 0.578046 | -0.000596457 | -0.00029853 | -0.000181742 | 0.268 | 0.22 | 0.00451431 |
| toward_teacher|low_slack_half|tail_meanneg_m1.00|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | tail_meanneg_m1.00 | -6.55495e-06 | 0.577589 | 0.57805 | -0.000746611 | -0.000374636 | -0.000169668 | 0.188 | 0.104 | 0.00482263 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_core_top50|all|core_gain|s0.130|c0.120 | tail_meanneg_m1.00 | -6.55055e-06 | 0.57759 | 0.578046 | -0.000552026 | -0.000299338 | -0.000191065 | 0.268 | 0.208 | 0.00364651 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_all_4of6|all|core_gain|s0.130|c0.120 | tail_meanneg_m1.00 | -6.51062e-06 | 0.57759 | 0.578046 | -0.000556418 | -0.000302468 | -0.000185778 | 0.3 | 0.252 | 0.00380321 |
| toward_teacher|all|tail_meanneg_m1.00|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | tail_meanneg_m1.00 | -6.50666e-06 | 0.57759 | 0.578045 | -0.000556061 | -0.00029848 | -0.000137686 | 0.212 | 0.12 | 0.0036024 |
| toward_teacher|all|tail_p90_nonpos_m1.00|all|grad_all_abs50|all|flat|s0.130|c0.120 | tail_p90_nonpos_m1.00 | -6.49574e-06 | 0.57759 | 0.578046 | -0.000690921 | -8.35293e-05 | -3.16746e-05 | 0.032 | 0.028 | 0.00433234 |

## Decision

- E67 is a tail-risk translator audit, not a submission generator.
- If tail-gated Q2/S3 beats matched `no_q2_s3` with max-set neutral, the next experiment should add independent non-anchor validation before considering a file.
- If it cannot beat `no_q2_s3`, Q2/S3 tail risk is not solved by first-order anchor-tail gating; the next branch must use rowwise calibration or a structural target, not Q2/S3 add-back.

## Outputs

- `analysis_outputs/q2_s3_tail_neutral_translator_probe_scan.csv`
- `analysis_outputs/q2_s3_tail_neutral_translator_probe_summary.csv`
- `analysis_outputs/q2_s3_tail_neutral_translator_probe_pair.csv`
