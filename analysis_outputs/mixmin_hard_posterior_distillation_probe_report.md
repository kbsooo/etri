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
| toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.070|c0.120 | toward_teacher | 0.57773 | -4.08086e-06 | False | -0.000860265 | -0.0005282 | -0.000508415 | 0.00419249 | True | True | False |
| toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.095|c0.120 | toward_teacher | 0.577731 | -3.98584e-06 | False | -0.00116592 | -0.000715262 | -0.000688411 | 0.00568981 | True | True | False |
| toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.095|c0.080 | toward_teacher | 0.577731 | -3.98101e-06 | False | -0.000778961 | -0.000481783 | -0.000454848 | 0.00386999 | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577731 | -3.897e-06 | False | -0.000914361 | -0.000589573 | -0.000425693 | 0.00356328 | True | True | False |
| toward_teacher|all|no_q2|raw_agree|all|w0.070|c0.120 | toward_teacher | 0.577731 | -3.77731e-06 | False | -0.00096226 | -0.000530949 | -0.000501971 | 0.0042809 | True | True | False |
| toward_teacher|all|no_q2|raw_agree|all|w0.095|c0.080 | toward_teacher | 0.577731 | -3.71508e-06 | False | -0.000871147 | -0.000480247 | -0.000450865 | 0.00395089 | True | True | False |
| toward_teacher|all|all|raw_agree|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577731 | -3.5551e-06 | False | -0.000986346 | -0.00056536 | -0.000405017 | 0.00368974 | True | True | False |
| toward_teacher|all|no_q2|raw_agree|all|w0.095|c0.120 | toward_teacher | 0.577731 | -3.44887e-06 | False | -0.0013043 | -0.000718952 | -0.000679626 | 0.0058098 | True | True | False |
| toward_teacher|raw_energy_half|no_q2|raw_agree|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577731 | -3.3671e-06 | False | -0.00096488 | -0.000545584 | -9.399e-05 | 0.00257442 | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|all|w0.095|c0.080 | toward_teacher | 0.577731 | -3.23165e-06 | False | -0.00102295 | -0.000645475 | -0.000558214 | 0.00456567 | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|all|w0.070|c0.120 | toward_teacher | 0.577731 | -3.14273e-06 | False | -0.00112746 | -0.000707662 | -0.000625123 | 0.00494838 | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|all|w0.050|c0.120 | toward_teacher | 0.577731 | -3.05201e-06 | False | -0.000806141 | -0.000506285 | -0.000447328 | 0.00353455 | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.01354e-06 | False | -0.000754404 | -0.000476263 | -0.000411966 | 0.00336418 | True | True | False |
| toward_teacher|all|all|raw_agree|all|w0.050|c0.120 | toward_teacher | 0.577732 | -2.87652e-06 | False | -0.00089447 | -0.000503463 | -0.000446598 | 0.00362118 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|raw_agree|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577732 | -2.86687e-06 | False | -0.00105387 | -0.000548751 | -6.79801e-05 | 0.00229613 | True | True | False |
| toward_teacher|all|all|raw_agree|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.83212e-06 | False | -0.000835157 | -0.00046876 | -0.000421331 | 0.00344284 | True | True | False |
| toward_teacher|all|all|raw_agree|all|w0.095|c0.080 | toward_teacher | 0.577732 | -2.81597e-06 | False | -0.00113252 | -0.000635267 | -0.000570899 | 0.00467243 | True | True | False |
| toward_teacher|all|all|raw_agree|all|w0.070|c0.120 | toward_teacher | 0.577732 | -2.73848e-06 | False | -0.00125109 | -0.000703676 | -0.000624065 | 0.00506965 | True | True | False |
| toward_teacher|raw_energy_half|all|raw_agree|raw_row_top50|w0.095|c0.120 | toward_teacher | 0.577732 | -2.62753e-06 | False | -0.00124126 | -0.000704888 | -0.000182449 | 0.00315175 | True | True | False |
| toward_teacher|raw_energy_half|all|raw_agree|raw_row_top50|w0.070|c0.120 | toward_teacher | 0.577732 | -2.60255e-06 | False | -0.000915291 | -0.000520069 | -0.000135113 | 0.00232234 | True | True | False |

## Decision

- eligible toward-teacher submission gates: `0`.
- diagnostic reverse-control gates: `0`.
- best toward-teacher anchor delta: `-4.08086e-06` from `toward_teacher|low_slack_half|no_q2|raw_agree|all|w0.070|c0.120`.
- best reverse-control anchor delta: `-1.25523e-08` from `reverse_control|all|s2_s3|agree_support60|teacher_row_top70|w0.010|c0.018`.
- No submission file is justified by E58.

## Interpretation

If toward-teacher gates are empty while reverse controls improve anchor stress, E56 posterior is useful mainly as an adverse energy axis. If neither direction improves anchor stress, the E56 posterior is a hidden-world diagnostic but not the next probability movement.

## Outputs

- `analysis_outputs/mixmin_hard_posterior_distillation_probe_scan.csv`
- `analysis_outputs/mixmin_hard_posterior_distillation_probe_summary.csv`
