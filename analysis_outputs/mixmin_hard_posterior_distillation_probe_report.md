# E58 Mixmin-Hard Posterior Distillation Probe

## Observe

E56 posterior is internally coherent, while E57 rejects direct posterior averaging under actual-anchor safety.

## Wonder

Can E56 posterior energy be distilled only on confident cells and still stay public-anchor-compatible near mixmin?

## Method

- Generated latent-gated candidates from E56 posterior components: `104727`.
- Prefiltered by movement and world-support before actual-anchor scoring: `1200`.
- Candidate generation used teacher band, target mask, raw-agreement/support/entropy cell gates, row gates, caps, and small weights.
- Actual-anchor score was used only as a final safety stress, not to generate per-cell directions.
- Submission eligibility requires actual-anchor improvement margin `< -1e-05` versus mixmin.

## Top Scored Candidates

| candidate | direction | actual_anchor_score_final | anchor_delta_vs_mixmin | anchor_margin_gate | raw_energy_quarter_median_delta | raw_energy_quarter_p90_delta | world_all_median_delta | mean_abs_logit_move_vs_mixmin | movement_guard | world_guard | eligible_submission_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|raw_energy_quarter|no_q2|low_entropy40|teacher_row_top50|w0.095|c0.080 | toward_teacher | 0.577731 | -3.5551e-06 | False | -0.000949919 | -0.000949919 | -6.39763e-05 | 0.00229737 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|support60|teacher_row_top50|w0.095|c0.080 | toward_teacher | 0.577731 | -3.4328e-06 | False | -0.000950182 | -0.000950182 | -6.42394e-05 | 0.00229303 | True | True | False |
| toward_teacher|raw_energy_quarter|q2_s2_s3|raw_agree|all|w0.095|c0.120 | toward_teacher | 0.577731 | -3.35615e-06 | False | -0.00105632 | -0.000476552 | -0.000229003 | 0.00236189 | True | True | False |
| toward_teacher|raw_energy_half|q3_s|high_abs75|all|w0.095|c0.120 | toward_teacher | 0.577732 | -2.87842e-06 | False | -0.000993027 | -0.000758512 | -0.000133141 | 0.002052 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|support60|support_row_top50|w0.070|c0.120 | toward_teacher | 0.577732 | -2.87652e-06 | False | -0.00109279 | -0.00109279 | -3.83581e-05 | 0.00316816 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|all|all|w0.050|c0.080 | toward_teacher | 0.577732 | -2.83212e-06 | False | -0.00123006 | -0.000570703 | -4.76088e-05 | 0.0033981 | True | True | False |
| toward_teacher|raw_energy_quarter|all|agree_support60|teacher_row_top50|w0.095|c0.120 | toward_teacher | 0.577732 | -2.81597e-06 | False | -0.00108968 | -0.00108968 | -0.000138598 | 0.0021432 | True | True | False |
| toward_teacher|raw_energy_half|s_all|all|support_row_top50|w0.095|c0.120 | toward_teacher | 0.577732 | -2.79536e-06 | False | -0.00103502 | -0.000606758 | -0.000120323 | 0.0031872 | True | True | False |
| toward_teacher|raw_energy_half|all|support60|all|w0.070|c0.120 | toward_teacher | 0.577732 | -2.73848e-06 | False | -0.00113569 | -0.000878663 | -0.000140541 | 0.00372071 | True | True | False |
| toward_teacher|raw_energy_quarter|all|all|teacher_row_top50|w0.070|c0.080 | toward_teacher | 0.577732 | -2.63076e-06 | False | -0.00123111 | -0.000634273 | -6.57216e-05 | 0.00279147 | True | True | False |
| toward_teacher|raw_energy_quarter|all|high_abs60|teacher_row_top50|w0.095|c0.080 | toward_teacher | 0.577732 | -2.50532e-06 | False | -0.0011452 | -0.000867253 | -8.11959e-05 | 0.00210194 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|all|all|w0.070|c0.050 | toward_teacher | 0.577732 | -2.49136e-06 | False | -0.00107584 | -0.000501118 | -4.18969e-05 | 0.00298301 | True | True | False |
| toward_teacher|raw_energy_quarter|q1_q3_s3|low_entropy40|all|w0.095|c0.120 | toward_teacher | 0.577732 | -2.43852e-06 | False | -0.00109248 | -0.00109248 | -0.00016508 | 0.00323363 | True | True | False |
| toward_teacher|raw_energy_quarter|all|low_entropy40|raw_row_top50|w0.070|c0.120 | toward_teacher | 0.577732 | -2.24822e-06 | False | -0.000950921 | -0.000950921 | -7.74959e-05 | 0.00292995 | True | True | False |
| toward_teacher|raw_energy_quarter|all|low_entropy40|all|w0.095|c0.050 | toward_teacher | 0.577732 | -2.22726e-06 | False | -0.00111352 | -0.00111352 | -5.10696e-05 | 0.00323496 | True | True | False |
| toward_teacher|raw_energy_quarter|all|raw_agree|support_row_top50|w0.095|c0.080 | toward_teacher | 0.577732 | -2.20393e-06 | False | -0.00105973 | -0.000523043 | -8.69302e-05 | 0.00202629 | True | True | False |
| toward_teacher|raw_energy_quarter|all|high_abs60|all|w0.095|c0.050 | toward_teacher | 0.577732 | -2.0113e-06 | False | -0.00101231 | -0.000751736 | -6.50218e-05 | 0.0019 | True | True | False |
| toward_teacher|raw_energy_quarter|q2_s2_s3|support60|all|w0.095|c0.120 | toward_teacher | 0.577733 | -1.95731e-06 | False | -0.0011076 | -0.0011076 | -0.000195595 | 0.00339851 | True | True | False |
| toward_teacher|all|q3_s|all|all|w0.070|c0.120 | toward_teacher | 0.577733 | -1.92248e-06 | False | -0.00114732 | -0.000631587 | -0.00067968 | 0.00555203 | True | True | False |
| toward_teacher|raw_energy_half|all|high_abs60|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577733 | -1.89812e-06 | False | -0.00117143 | -0.000793599 | -0.000135657 | 0.00238423 | True | True | False |

## Decision

- eligible toward-teacher submission gates: `0`.
- diagnostic reverse-control gates: `0`.
- best toward-teacher anchor delta: `-3.5551e-06` from `toward_teacher|raw_energy_quarter|no_q2|low_entropy40|teacher_row_top50|w0.095|c0.080`.
- best reverse-control anchor delta: `-5.31077e-07` from `reverse_control|raw_energy_quarter|s2_s3|high_abs75|teacher_row_top70|w0.010|c0.010`.
- No submission file is justified by E58.

## Interpretation

If toward-teacher gates are empty while reverse controls improve anchor stress, E56 posterior is useful mainly as an adverse energy axis. If neither direction improves anchor stress, the E56 posterior is a hidden-world diagnostic but not the next probability movement.

## Outputs

- `analysis_outputs/mixmin_hard_posterior_distillation_probe_scan.csv`
- `analysis_outputs/mixmin_hard_posterior_distillation_probe_summary.csv`
