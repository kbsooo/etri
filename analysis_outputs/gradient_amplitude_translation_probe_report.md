# E64 Gradient-Amplitude Translation Probe

## Observe

E63 validates E56 teacher direction under independent hidden-rate gradients but fails selector-scale anchor margin.

## Wonder

Is E63 only under-amplified, or does public-anchor geometry saturate before the validated direction becomes useful?

## Method

- Generated amplitude-expanded candidates: `12096`.
- Selected for actual-anchor scoring after world, hidden, and movement prefilters: `1796`.
- Candidate probabilities are larger capped logit moves from mixmin toward E56 teacher on E63 gradient-consensus cells.
- Tested flat and gradient-gain-shaped amplitudes, broader caps, and larger scales, plus reverse controls.
- Submission eligibility still requires toward direction, actual-anchor margin `< -1e-5`, world guard, hidden guard, and movement guard.

## Direction Summary

| direction | scored | anchor_beats | anchor_margin | hidden_guard | world_guard | movement_guard | best_anchor_delta | median_anchor_delta | max_move |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reverse_control | 450 | 0 | 0 | 0 | 0 | 450 | 1.53525e-07 | 2.28691e-06 | 0.00221809 |
| toward_teacher | 1346 | 0 | 0 | 1346 | 1346 | 1346 | 3.02387e-06 | 0.000757074 | 0.0799501 |

## Top Scored Candidates

| candidate | direction | actual_anchor_score_final | anchor_delta_vs_mixmin | anchor_margin_gate | hidden_core_mean_delta | hidden_all_mean_delta | raw_energy_quarter_median_delta | raw_energy_quarter_p90_delta | world_all_median_delta | mean_abs_logit_move_vs_mixmin | movement_guard | world_guard | hidden_guard | eligible_submission_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reverse_control|low_slack_half|all|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 1.53525e-07 | False | 7.15909e-05 | 7.52349e-05 | 0.000308967 | 0.000313539 | 0.000212967 | 0.000763429 | True | False | False | False |
| reverse_control|low_slack_half|all|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 1.674e-07 | False | 5.16166e-05 | 5.24171e-05 | 0.000203537 | 0.000208109 | 0.000150336 | 0.000467142 | True | False | False | False |
| reverse_control|all|all|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.13665e-07 | False | 5.38535e-05 | 5.31603e-05 | 0.000210614 | 0.000215186 | 0.000145846 | 0.000477708 | True | False | False | False |
| reverse_control|low_slack_half|no_q2|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 2.22807e-07 | False | 5.79313e-05 | 6.21584e-05 | 0.000240705 | 0.000245276 | 0.000158419 | 0.000603429 | True | False | False | False |
| reverse_control|all|no_s3|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.34571e-07 | False | 4.93988e-05 | 4.77536e-05 | 0.000191703 | 0.000196274 | 0.000132933 | 0.000420764 | True | False | False | False |
| reverse_control|low_slack_half|all|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.3805e-07 | False | 5.1527e-05 | 5.2945e-05 | 0.000205897 | 0.000210468 | 0.000151807 | 0.000477607 | True | False | False | False |
| reverse_control|low_slack_half|no_s3|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.51275e-07 | False | 4.71249e-05 | 4.68765e-05 | 0.000181955 | 0.000186527 | 0.000130837 | 0.000409633 | True | False | False | False |
| reverse_control|all|all|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.86776e-07 | False | 5.44272e-05 | 5.44457e-05 | 0.000216807 | 0.000221378 | 0.000146573 | 0.000501318 | True | False | False | False |
| reverse_control|low_slack_half|no_q2|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 2.90362e-07 | False | 4.1202e-05 | 4.33262e-05 | 0.000154911 | 0.000159483 | 0.000106284 | 0.000364434 | True | False | False | False |
| reverse_control|all|no_s3|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.03043e-07 | False | 4.97792e-05 | 4.87082e-05 | 0.000196697 | 0.000201268 | 0.0001333 | 0.000437814 | True | False | False | False |
| reverse_control|low_slack_half|no_s3|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 3.06795e-07 | False | 6.59688e-05 | 6.81337e-05 | 0.000280954 | 0.000285526 | 0.00020324 | 0.000681143 | True | False | False | False |
| reverse_control|low_slack_half|no_s3|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.28262e-07 | False | 4.69149e-05 | 4.71683e-05 | 0.000183352 | 0.000187923 | 0.000132417 | 0.00041462 | True | False | False | False |
| reverse_control|low_slack_half|no_q2_s3|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 3.28835e-07 | False | 5.23093e-05 | 5.50572e-05 | 0.000212692 | 0.000217263 | 0.000139549 | 0.000521143 | True | False | False | False |
| reverse_control|all|all|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 3.5206e-07 | False | 7.43914e-05 | 7.47255e-05 | 0.000324493 | 0.000329065 | 0.00021935 | 0.000772571 | True | False | False | False |
| reverse_control|low_slack_half|no_q2|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.61338e-07 | False | 4.13581e-05 | 4.40206e-05 | 0.000157965 | 0.000162536 | 0.000109095 | 0.000375375 | True | False | False | False |
| reverse_control|low_slack_half|all|support60|grad_all_4of6|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 3.67156e-07 | False | 7.20804e-05 | 7.81089e-05 | 0.000323724 | 0.000328295 | 0.000227724 | 0.000815405 | True | False | False | False |
| reverse_control|low_slack_half|no_q2_s3|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.77232e-07 | False | 3.67103e-05 | 3.77855e-05 | 0.000133329 | 0.0001379 | 9.04241e-05 | 0.000306925 | True | False | False | False |
| reverse_control|all|no_s3|support60|grad_all_abs50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.80114e-07 | False | 4.82893e-05 | 4.67781e-05 | 0.000179956 | 0.000184527 | 0.000124168 | 0.000390321 | True | False | False | False |
| reverse_control|all|no_q2_s3|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.86828e-07 | False | 3.70844e-05 | 3.64073e-05 | 0.000138834 | 0.000143406 | 9.31715e-05 | 0.000309233 | True | False | False | False |
| reverse_control|all|no_q2|support60|grad_core_top50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 3.87567e-07 | False | 4.15391e-05 | 4.1814e-05 | 0.000157746 | 0.000162317 | 0.000107511 | 0.000366178 | True | False | False | False |
| reverse_control|low_slack_half|all|support60|grad_all_abs50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.00458e-07 | False | 4.93862e-05 | 4.92837e-05 | 0.000187001 | 0.000191573 | 0.000138196 | 0.000415091 | True | False | False | False |
| reverse_control|all|all|support60|grad_all_abs50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.07832e-07 | False | 5.22948e-05 | 5.15183e-05 | 0.000196398 | 0.00020097 | 0.000138552 | 0.000437368 | True | False | False | False |
| reverse_control|all|no_s3|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 4.21467e-07 | False | 6.84862e-05 | 6.73233e-05 | 0.000298126 | 0.000302697 | 0.000202126 | 0.000685714 | True | False | False | False |
| reverse_control|low_slack_half|no_q2|support60|grad_all_4of6|teacher_row_top50|flat|s0.10|c0.080 | reverse_control | 0.577735 | 4.39096e-07 | False | 5.88152e-05 | 6.51326e-05 | 0.00025499 | 0.000259562 | 0.000166442 | 0.000650834 | True | False | False | False |
| reverse_control|low_slack_half|no_q2_s3|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.42607e-07 | False | 3.6746e-05 | 3.82439e-05 | 0.00013542 | 0.000139991 | 9.03319e-05 | 0.000312389 | True | False | False | False |
| reverse_control|all|no_q2_s3|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.43881e-07 | False | 3.75637e-05 | 3.73639e-05 | 0.000144011 | 0.000148582 | 9.7502e-05 | 0.00032517 | True | False | False | False |
| reverse_control|all|all|support60|grad_core_top50|all|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.46782e-07 | False | 6.96878e-05 | 7.03867e-05 | 0.000270998 | 0.000273626 | 0.000179124 | 0.000634111 | True | False | False | False |
| reverse_control|all|no_q2|support60|grad_all_4of6|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.52937e-07 | False | 4.22117e-05 | 4.31014e-05 | 0.000164121 | 0.000168692 | 0.000110485 | 0.000388673 | True | False | False | False |
| reverse_control|all|no_s3|support60|grad_core_top50|all|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.5339e-07 | False | 6.3021e-05 | 6.20419e-05 | 0.000241739 | 0.000244367 | 0.000160838 | 0.000546642 | True | False | False | False |
| reverse_control|low_slack_half|no_s3|support60|grad_all_abs50|teacher_row_top50|core_gain|s0.10|c0.080 | reverse_control | 0.577735 | 4.69867e-07 | False | 4.51871e-05 | 4.41683e-05 | 0.000166977 | 0.000171549 | 0.000120828 | 0.000363206 | True | False | False | False |

## Decision

- eligible toward-teacher gates: `0`.
- diagnostic reverse-control gates: `0`.
- best anchor delta: `1.53525e-07` from `reverse_control|low_slack_half|all|support60|grad_core_top50|teacher_row_top50|flat|s0.10|c0.080`.
- No submission file is justified by E64.

## Interpretation

If larger amplitudes clear margin while reverse controls do not, E63 was under-scaled. If not, the missing variable is not scalar amplitude but a different calibration/targetwise translator.

## Outputs

- `analysis_outputs/gradient_amplitude_translation_probe_scan.csv`
- `analysis_outputs/gradient_amplitude_translation_probe_summary.csv`
