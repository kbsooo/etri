# E62 Transition-Gated Posterior Distillation Probe

## Observe

E56 posterior energy is coherent internally, E58 simple slicing is sub-margin, and E60 transition residuals sense hidden mixmin sign only when row calibration collapses.

## Wonder

Can transition residuals be used as a gate for E56 teacher cells without using them as probability targets?

## Method

- Generated transition-gated E56 teacher candidates: `363258`.
- Prefiltered by E56-world support and movement before actual-anchor scoring: `1300`.
- Transition views: row-safe residual methods, balanced hidden-sign methods, and aggressive hidden-sign methods.
- Candidate movement remains a small capped logit move from mixmin toward the E56 teacher; transition residuals only open or close gates.
- Submission eligibility requires actual-anchor improvement margin `< -1e-05` versus mixmin plus movement/world guards.

## Transition Views

| group | view | n_methods | weighted_mixmin_delta_vs_a2c8 | mixmin_better_block_rate |
| --- | --- | --- | --- | --- |
| method | transition_raw_residual_baseraw_k4_a24_w0.35 | 1 | 0.000229822 | 0.5 |
| method | transition_raw_residual_baseraw_k8_a24_w0.35 | 1 | 0.000242571 | 0.5 |
| method | raw_phone_base | 1 | 0.000310798 | 0.5 |
| method | edge_shrink050 | 1 | -0.000374835 | 0.527778 |
| method | transition_raw_residual_baseedge_shrink025_k8_a24_w1.00 | 1 | -0.000266404 | 0.5 |
| method | transition_topology_baseedge_shrink025_k16_a4_w0.35 | 1 | -0.000255723 | 0.611111 |
| method | transition_topology_baseedge_shrink025_k16_a24_w0.65 | 1 | -0.000247761 | 0.611111 |
| method | transition_raw_residual_baseedge_shrink025_k8_a4_w0.35 | 1 | -0.000246899 | 0.5 |
| method | transition_raw_topology_baseedge_shrink025_k4_a4_w0.35 | 1 | -0.000246019 | 0.527778 |
| method | transition_topology_baseedge_shrink025_k4_a4_w0.35 | 1 | -0.000235967 | 0.583333 |
| method | transition_raw_topology_baseedge_shrink025_k4_a12_w0.65 | 1 | -0.000230351 | 0.555556 |
| method | transition_raw_residual_baseedge_shrink025_k4_a4_w0.35 | 1 | -0.000228857 | 0.527778 |
| method | transition_topology_baseedge_shrink025_k4_a12_w0.65 | 1 | -0.000223185 | 0.583333 |
| method | transition_raw_residual_baseedge_mid_k4_a4_w1.00 | 1 | -0.00156886 | 0.638889 |
| method | transition_raw_residual_baseedge_mid_k4_a4_w0.65 | 1 | -0.00150278 | 0.666667 |
| method | transition_raw_residual_baseedge_mid_k4_a12_w1.00 | 1 | -0.0014455 | 0.638889 |
| method | transition_full_transition_baseedge_mid_k16_a4_w1.00 | 1 | -0.00139916 | 0.611111 |
| method | transition_full_transition_baseedge_mid_k16_a12_w1.00 | 1 | -0.00138064 | 0.527778 |
| method | transition_raw_residual_baseedge_mid_k4_a4_w0.35 | 1 | -0.0013784 | 0.611111 |
| method | transition_full_transition_baseedge_mid_k16_a4_w0.65 | 1 | -0.00137335 | 0.527778 |
| method | transition_raw_residual_baseedge_mid_k4_a12_w0.65 | 1 | -0.00136639 | 0.611111 |
| aggregate | row_safe | 3 | 0.000260793 | 0.5 |
| aggregate | balanced_hidden_sign | 10 | -0.000289037 | 0.555556 |
| aggregate | aggressive_hidden_sign | 8 | -0.00148256 | 0.611111 |

## Top Scored Candidates

| candidate | direction | actual_anchor_score_final | anchor_delta_vs_mixmin | anchor_margin_gate | raw_energy_quarter_median_delta | raw_energy_quarter_p90_delta | world_all_median_delta | mean_abs_logit_move_vs_mixmin | movement_guard | world_guard | eligible_submission_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.71643e-06 | False | -0.000561406 | -0.000366609 | -0.000248158 | 0.00210335 | True | True | False |
| toward_teacher|all|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.6049e-06 | False | -0.000616971 | -0.000355676 | -0.000218338 | 0.0021701 | True | True | False |
| toward_teacher|all|no_q2|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.35324e-06 | False | -0.000532875 | -0.000322916 | -0.00020511 | 0.00206788 | True | True | False |
| toward_teacher|raw_energy_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.33474e-06 | False | -0.000787755 | -0.000439095 | -6.09908e-05 | 0.00200177 | True | True | False |
| toward_teacher|low_slack_half|no_q2|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.30171e-06 | False | -0.00048736 | -0.000325364 | -0.000233123 | 0.00201611 | True | True | False |
| toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.050|c0.080 | toward_teacher | 0.577732 | -2.15842e-06 | False | -0.000401237 | -0.000262097 | -0.000177489 | 0.00150239 | True | True | False |
| toward_teacher|all|no_s3|all|trans_bal_raw_consensus|all|w0.050|c0.080 | toward_teacher | 0.577732 | -2.13254e-06 | False | -0.000440935 | -0.000254296 | -0.000156197 | 0.00155007 | True | True | False |
| toward_teacher|raw_energy_quarter|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.13087e-06 | False | -0.000856173 | -0.000437505 | -5.31722e-05 | 0.00182252 | True | True | False |
| toward_teacher|low_slack_half|all|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.07944e-06 | False | -0.000612091 | -0.000402106 | -0.000271207 | 0.00232735 | True | True | False |
| toward_teacher|all|all|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.0702e-06 | False | -0.000664265 | -0.000391169 | -0.00025367 | 0.00239391 | True | True | False |
| toward_teacher|raw_energy_half|no_q2|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577732 | -2.05896e-06 | False | -0.000715334 | -0.00040903 | -7.62848e-05 | 0.00189134 | True | True | False |
| toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.050 | toward_teacher | 0.577733 | -1.98747e-06 | False | -0.000351838 | -0.000229875 | -0.00015514 | 0.00133023 | True | True | False |
| toward_teacher|all|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.050 | toward_teacher | 0.577733 | -1.93583e-06 | False | -0.000386543 | -0.000225299 | -0.000133439 | 0.0013699 | True | True | False |
| toward_teacher|raw_energy_half|no_s3|all|trans_bal_raw_consensus|teacher_row_top50|w0.070|c0.080 | toward_teacher | 0.577733 | -1.92931e-06 | False | -0.000561583 | -0.000312348 | -4.20846e-05 | 0.00118822 | True | True | False |
| toward_teacher|raw_energy_half|no_s3|all|trans_bal_raw_consensus|all|w0.050|c0.080 | toward_teacher | 0.577733 | -1.92024e-06 | False | -0.000562914 | -0.000313871 | -4.37968e-05 | 0.00142984 | True | True | False |
| toward_teacher|all|no_q2|all|trans_bal_raw_consensus|all|w0.050|c0.080 | toward_teacher | 0.577733 | -1.91727e-06 | False | -0.000380849 | -0.000230879 | -0.000146732 | 0.00147706 | True | True | False |
| toward_teacher|all|no_s3|all|trans_safe_not_opposed|all|w0.070|c0.080 | toward_teacher | 0.577733 | -1.86388e-06 | False | -0.000788888 | -0.000431698 | -0.00031718 | 0.00282558 | True | True | False |
| toward_teacher|low_slack_half|no_s3|all|trans_safe_not_opposed|all|w0.070|c0.080 | toward_teacher | 0.577733 | -1.83635e-06 | False | -0.000722002 | -0.000439405 | -0.00032945 | 0.00279307 | True | True | False |
| toward_teacher|raw_energy_quarter|no_q2|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577733 | -1.82098e-06 | False | -0.000780776 | -0.00040611 | -4.75855e-05 | 0.00173371 | True | True | False |
| toward_teacher|raw_energy_half|all|all|trans_bal_raw_consensus|all|w0.070|c0.080 | toward_teacher | 0.577733 | -1.81973e-06 | False | -0.000865847 | -0.000481987 | -4.94834e-05 | 0.00223857 | True | True | False |

## Decision

- eligible toward-teacher submission gates: `0`.
- diagnostic reverse-control gates: `0`.
- best toward-teacher anchor delta: `-2.71643e-06` from `toward_teacher|low_slack_half|no_s3|all|trans_bal_raw_consensus|all|w0.070|c0.080`.
- best reverse-control anchor delta: `-5.47202e-09` from `reverse_control|low_slack_half|s2_s3|confident_abs_support|trans_good_bal_agree|teacher_row_top70|w0.006|c0.010`.
- No submission file is justified by E62.

## Interpretation

If no gate opens, the transition residual axis is a risk diagnostic rather than the missing E56 validator. If only reverse controls improve, transition gates are exposing an adverse E56 direction. If a toward gate opens with margin, it becomes a candidate because it survived two independent hidden-world stresses: E56 world support and E60 transition gating.

## Outputs

- `analysis_outputs/transition_gated_posterior_distillation_probe_scan.csv`
- `analysis_outputs/transition_gated_posterior_distillation_probe_summary.csv`
- `analysis_outputs/transition_gated_posterior_distillation_probe_transition_views.csv`
