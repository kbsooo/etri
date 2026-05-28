# E65 Near-Zero Amplitude Response Probe

## Observe

E63 has a tiny favorable edge; E64 shows scalar amplification is adverse.

## Wonder

Is there a targetwise near-zero amplitude pocket that clears selector margin, or is the local edge bounded below submission scale?

## Method

- Generated near-zero targetwise candidates: `27384`.
- Selected for actual-anchor scoring: `2400`.
- Tested small scales, target masks, gradient gates, row gates, caps, and flat/core-gain shapes around mixmin.
- Submission eligibility requires toward direction, actual-anchor margin `< -1e-5`, hidden guard, world guard, and movement guard.

## Direction Summary

| direction | scored | anchor_beats | anchor_margin | hidden_guard | world_guard | movement_guard | best_anchor_delta | median_anchor_delta | max_move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reverse_control | 110 | 106 | 0 | 0 | 0 | 110 | -1.2132e-08 | -2.75838e-09 | 4.11429e-06 |
| toward_teacher | 2290 | 1753 | 0 | 2290 | 2290 | 2290 | -5.99494e-06 | -1.08973e-06 | 0.00844244 |

## Target Response

| target_mask | n | anchor_beats | anchor_margin | best_delta | median_delta | best_move | best_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no_q2_s3 | 237 | 233 | 0 | -5.99494e-06 | -3.17423e-06 | 0.00418971 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 |
| no_q2 | 312 | 301 | 0 | -5.09038e-06 | -2.0338e-06 | 0.00334183 | toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 |
| no_s3 | 496 | 478 | 0 | -4.72639e-06 | -1.94102e-06 | 0.00372617 | toward_teacher|all|no_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 |
| all | 527 | 490 | 0 | -4.19324e-06 | -1.48764e-06 | 0.00365486 | toward_teacher|all|all|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 |
| q1 | 201 | 101 | 0 | -1.41774e-06 | -6.08445e-10 | 0.00101623 | toward_teacher|all|q1|all|grad_all_abs50|all|flat|s0.130|c0.120 |
| s4 | 195 | 95 | 0 | -1.30874e-06 | 4.82383e-10 | 0.000971364 | toward_teacher|all|s4|raw_agree|grad_core_top50|all|flat|s0.130|c0.120 |
| q3 | 161 | 55 | 0 | -3.33409e-07 | 7.31671e-09 | 0.000594665 | toward_teacher|all|q3|all|grad_all_4of6|all|flat|s0.095|c0.080 |
| s2 | 161 | 0 | 0 | 1.40922e-10 | 1.99414e-08 | 6.13227e-06 | toward_teacher|low_slack_half|s2|support60|grad_all_abs50|all|core_gain|s0.016|c0.030 |

## Scale Response

| scale | n | anchor_beats | anchor_margin | best_delta | median_delta | best_move | best_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.13 | 607 | 457 | 0 | -5.99494e-06 | -1.4247e-06 | 0.00418971 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 |
| 0.095 | 381 | 338 | 0 | -5.56959e-06 | -2.30638e-06 | 0.00306171 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 |
| 0.07 | 182 | 173 | 0 | -4.77176e-06 | -2.82722e-06 | 0.002256 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.070|c0.120 |
| 0.05 | 123 | 120 | 0 | -3.81879e-06 | -2.42219e-06 | 0.00161143 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.050|c0.120 |
| 0.035 | 134 | 121 | 0 | -2.89111e-06 | -1.82534e-06 | 0.00150242 | toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.035|c0.120 |
| 0.024 | 154 | 121 | 0 | -2.12413e-06 | -1.28229e-06 | 0.00103023 | toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.024|c0.120 |
| 0.016 | 184 | 123 | 0 | -1.49809e-06 | -7.64612e-07 | 0.000686822 | toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.016|c0.120 |
| 0.01 | 244 | 130 | 0 | -9.94251e-07 | -1.7053e-08 | 0.000536905 | toward_teacher|all|no_q2|raw_agree|grad_all_4of6|all|flat|s0.010|c0.120 |
| 0.006 | 281 | 170 | 0 | -6.10252e-07 | -1.1436e-08 | 0.000322143 | toward_teacher|all|no_q2|raw_agree|grad_all_4of6|all|flat|s0.006|c0.120 |

## Top Scored Candidates

| candidate | direction | actual_anchor_score_final | anchor_delta_vs_mixmin | anchor_margin_gate | hidden_core_mean_delta | raw_energy_quarter_median_delta | raw_energy_quarter_p90_delta | mean_abs_logit_move_vs_mixmin | movement_guard | world_guard | hidden_guard | eligible_submission_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.577728 | -5.99494e-06 | False | -0.000674013 | -0.00134429 | -0.000773779 | 0.00418971 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.577729 | -5.91849e-06 | False | -0.000674463 | -0.00134866 | -0.000778145 | 0.00419863 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.577729 | -5.72727e-06 | False | -0.000668853 | -0.00125697 | -0.000784518 | 0.00417189 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.577729 | -5.60384e-06 | False | -0.000670306 | -0.00125662 | -0.000784165 | 0.00418971 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.56959e-06 | False | -0.000493752 | -0.000983572 | -0.000566657 | 0.00306171 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.48087e-06 | False | -0.000494084 | -0.000986766 | -0.000569852 | 0.00306823 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.42003e-06 | False | -0.000489972 | -0.000919753 | -0.000574496 | 0.00304869 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.577729 | -5.34592e-06 | False | -0.000450701 | -0.000897555 | -0.000517212 | 0.00279314 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.32697e-06 | False | -0.000491041 | -0.000919502 | -0.000574245 | 0.00306171 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.577729 | -5.26138e-06 | False | -0.000451005 | -0.00090047 | -0.000520127 | 0.00279909 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.577729 | -5.22102e-06 | False | -0.000447252 | -0.000839333 | -0.000524361 | 0.00278126 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.577729 | -5.13768e-06 | False | -0.000448228 | -0.000839105 | -0.000524133 | 0.00279314 | True | True | True | False |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.09038e-06 | False | -0.000521864 | -0.00105733 | -0.000627391 | 0.00334183 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.095|c0.120 | toward_teacher | 0.577729 | -5.08172e-06 | False | -0.000571728 | -0.00106695 | -0.000610329 | 0.004078 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.577729 | -5.07031e-06 | False | -0.000443233 | -0.000932088 | -0.000559933 | 0.00250509 | True | True | True | False |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.577729 | -5.06254e-06 | False | -0.000712317 | -0.00144506 | -0.000856722 | 0.00457303 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.577729 | -5.06046e-06 | False | -0.000481969 | -0.000976999 | -0.000585145 | 0.00300772 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.130|c0.080 | toward_teacher | 0.577729 | -5.01328e-06 | False | -0.000525827 | -0.000975015 | -0.000557211 | 0.00374174 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_4of6|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.98189e-06 | False | -0.000486669 | -0.000980523 | -0.000588986 | 0.00315088 | True | True | True | False |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.57773 | -4.95378e-06 | False | -0.000476374 | -0.000964873 | -0.000572644 | 0.00304869 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.94506e-06 | False | -0.000443615 | -0.00093578 | -0.000563626 | 0.00251263 | True | True | True | False |
| toward_teacher|all|no_q2|all|grad_all_abs50|all|flat|s0.095|c0.120 | toward_teacher | 0.57773 | -4.90094e-06 | False | -0.000523253 | -0.0010587 | -0.000635269 | 0.00336137 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.87754e-06 | False | -0.000451388 | -0.000873004 | -0.000567472 | 0.00260618 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_core_top50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.85758e-06 | False | -0.00048327 | -0.000987441 | -0.000592006 | 0.00303629 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_4of6|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.85281e-06 | False | -0.000487847 | -0.000988893 | -0.000594596 | 0.00317967 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_4of6|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.84284e-06 | False | -0.000490272 | -0.000897826 | -0.000600115 | 0.00321863 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_core_top50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.82219e-06 | False | -0.000486591 | -0.00090378 | -0.000595088 | 0.0031239 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|core_gain|s0.130|c0.120 | toward_teacher | 0.57773 | -4.80224e-06 | False | -0.000452077 | -0.000874828 | -0.000569297 | 0.00261607 | True | True | True | False |
| toward_teacher|all|no_q2|all|grad_all_abs50|all|flat|s0.130|c0.120 | toward_teacher | 0.57773 | -4.77732e-06 | False | -0.000714207 | -0.00144692 | -0.00086749 | 0.00459977 | True | True | True | False |
| toward_teacher|all|no_q2|all|grad_all_abs50|all|flat|s0.130|c0.080 | toward_teacher | 0.57773 | -4.77284e-06 | False | -0.000477643 | -0.000966118 | -0.000579833 | 0.00306651 | True | True | True | False |

## Decision

- eligible toward-teacher gates: `0`.
- diagnostic reverse-control gates: `0`.
- best anchor delta: `-5.99494e-06` from `toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120`.
- No submission file is justified by E65.

## Interpretation

A margin-clearing tiny targetwise pocket would support an amplitude translator. If the best local edge remains sub-margin, E56 gradient energy is a diagnostic rather than the next candidate generator.

## Outputs

- `analysis_outputs/near_zero_amplitude_response_probe_scan.csv`
- `analysis_outputs/near_zero_amplitude_response_probe_summary.csv`
- `analysis_outputs/near_zero_amplitude_response_probe_target_response.csv`
- `analysis_outputs/near_zero_amplitude_response_probe_scale_response.csv`
