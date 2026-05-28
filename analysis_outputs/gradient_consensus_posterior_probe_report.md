# E63 Gradient-Consensus Posterior Probe

## Observe

E56 teacher energy is coherent but sub-margin under simple gates. E60 transition residuals are sign-informative but unsafe. The missing piece may be an independent gradient validator rather than another handcrafted gate.

## Wonder

Does E56 teacher movement point down the BCE gradient implied by independent hidden-rate views?

## Method

- Generated gradient-consensus E56 candidates: `404671`.
- Prefiltered by E56-world support, hidden-view support, and movement before actual-anchor scoring: `1300`.
- Independent views: subject mean, calendar strict, raw phone, transition row-safe, transition balanced, transition aggressive, and core median.
- Candidate probabilities are still capped logit moves from mixmin toward E56 teacher; hidden views only define gradient gates and validation deltas.
- Submission eligibility requires actual-anchor improvement margin `< -1e-05` plus world, movement, and hidden guards.

## Hidden Views

| view | bce_mixmin | bce_a2c8 | mixmin_delta_vs_a2c8 | weighted_mixmin_delta_vs_a2c8 | mixmin_better_block_rate |
| --- | --- | --- | --- | --- | --- |
| subject_mean | 0.629599 | 0.629154 | 0.000445159 |  |  |
| calendar_count_strict | 0.680507 | 0.680686 | -0.000178794 |  |  |
| raw_phone_base | 0.664426 | 0.664115 | 0.000310798 |  |  |
| transition_row_safe | 0.663166 | 0.662906 | 0.000260793 |  |  |
| transition_balanced_hidden_sign | 0.599003 | 0.599292 | -0.000289037 |  |  |
| transition_aggressive_hidden_sign | 0.550611 | 0.552094 | -0.00148256 |  |  |
| core_median | 0.661833 | 0.661808 | 2.56002e-05 |  |  |
| transition_method:transition_raw_residual_baseraw_k4_a24_w0.35 |  |  |  | 0.000229822 | 0.5 |
| transition_method:transition_raw_residual_baseraw_k8_a24_w0.35 |  |  |  | 0.000242571 | 0.5 |
| transition_method:raw_phone_base |  |  |  | 0.000310798 | 0.5 |
| transition_method:edge_shrink050 |  |  |  | -0.000374835 | 0.527778 |
| transition_method:transition_raw_residual_baseedge_shrink025_k8_a24_w1.00 |  |  |  | -0.000266404 | 0.5 |
| transition_method:transition_topology_baseedge_shrink025_k16_a4_w0.35 |  |  |  | -0.000255723 | 0.611111 |
| transition_method:transition_topology_baseedge_shrink025_k16_a24_w0.65 |  |  |  | -0.000247761 | 0.611111 |
| transition_method:transition_raw_residual_baseedge_shrink025_k8_a4_w0.35 |  |  |  | -0.000246899 | 0.5 |
| transition_method:transition_raw_topology_baseedge_shrink025_k4_a4_w0.35 |  |  |  | -0.000246019 | 0.527778 |
| transition_method:transition_topology_baseedge_shrink025_k4_a4_w0.35 |  |  |  | -0.000235967 | 0.583333 |
| transition_method:transition_raw_topology_baseedge_shrink025_k4_a12_w0.65 |  |  |  | -0.000230351 | 0.555556 |
| transition_method:transition_raw_residual_baseedge_shrink025_k4_a4_w0.35 |  |  |  | -0.000228857 | 0.527778 |
| transition_method:transition_topology_baseedge_shrink025_k4_a12_w0.65 |  |  |  | -0.000223185 | 0.583333 |
| transition_method:transition_raw_residual_baseedge_mid_k4_a4_w1.00 |  |  |  | -0.00156886 | 0.638889 |
| transition_method:transition_raw_residual_baseedge_mid_k4_a4_w0.65 |  |  |  | -0.00150278 | 0.666667 |
| transition_method:transition_raw_residual_baseedge_mid_k4_a12_w1.00 |  |  |  | -0.0014455 | 0.638889 |
| transition_method:transition_full_transition_baseedge_mid_k16_a4_w1.00 |  |  |  | -0.00139916 | 0.611111 |

## Top Scored Candidates

| candidate | direction | actual_anchor_score_final | anchor_delta_vs_mixmin | anchor_margin_gate | hidden_core_mean_delta | hidden_core_max_delta | hidden_core_improve_count | hidden_all_improve_count | raw_energy_quarter_median_delta | raw_energy_quarter_p90_delta | mean_abs_logit_move_vs_mixmin | movement_guard | world_guard | hidden_guard | eligible_submission_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.64959e-06 | False | -0.00028404 | -0.000259383 | 4 | 7 | -0.000525911 | -0.000300939 | 0.00201478 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_core_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.52246e-06 | False | -0.000285142 | -0.000261122 | 4 | 7 | -0.000534257 | -0.000306086 | 0.00204038 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_4of6|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.5064e-06 | False | -0.000292075 | -0.000268735 | 4 | 7 | -0.000540413 | -0.000312682 | 0.00224763 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.49671e-06 | False | -0.000283048 | -0.000262684 | 4 | 7 | -0.000530881 | -0.000309632 | 0.00199826 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.48745e-06 | False | -0.00028367 | -0.000263781 | 4 | 7 | -0.000535216 | -0.000313967 | 0.00201106 | True | True | True | False |
| toward_teacher|all|no_q2_s3|all|grad_all_4of6|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.41408e-06 | False | -0.000293207 | -0.000271209 | 4 | 7 | -0.000547821 | -0.000315631 | 0.00227831 | True | True | True | False |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.40631e-06 | False | -0.000257252 | -0.000238458 | 4 | 7 | -0.00052029 | -0.00030909 | 0.0016416 | True | True | True | False |
| toward_teacher|all|no_s3|raw_agree|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.38129e-06 | False | -0.000279866 | -0.000240389 | 4 | 7 | -0.000615652 | -0.000378852 | 0.0018304 | True | True | True | False |
| toward_teacher|low_slack_half|no_s3|raw_agree|grad_core_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.35978e-06 | False | -0.000271978 | -0.000235056 | 4 | 7 | -0.000541564 | -0.000365564 | 0.0017504 | True | True | True | False |
| toward_teacher|all|no_q2|all|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.35019e-06 | False | -0.00025794 | -0.000239719 | 4 | 7 | -0.000520965 | -0.000312965 | 0.0016512 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2|raw_agree|grad_all_4of6|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.3367e-06 | False | -0.000309164 | -0.000288615 | 4 | 7 | -0.000529181 | -0.000363433 | 0.00248841 | True | True | True | False |
| toward_teacher|all|no_s3|all|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.33382e-06 | False | -0.000280186 | -0.000241142 | 4 | 7 | -0.000618078 | -0.000381278 | 0.0018368 | True | True | True | False |
| toward_teacher|low_slack_half|no_s3|raw_agree|grad_all_top70|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.32376e-06 | False | -0.000255173 | -0.000223086 | 4 | 7 | -0.000534471 | -0.000364871 | 0.0015616 | True | True | True | False |
| toward_teacher|all|no_q2|raw_agree|grad_all_4of6|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.31953e-06 | False | -0.000315293 | -0.000293939 | 4 | 7 | -0.000590195 | -0.000357064 | 0.00255165 | True | True | True | False |
| toward_teacher|low_slack_half|no_s3|all|grad_all_top70|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.3142e-06 | False | -0.000255327 | -0.000223652 | 4 | 7 | -0.000535326 | -0.000365726 | 0.0015648 | True | True | True | False |
| toward_teacher|low_slack_half|no_s3|all|grad_core_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.30857e-06 | False | -0.000273195 | -0.000237281 | 4 | 7 | -0.000545524 | -0.000366324 | 0.0017664 | True | True | True | False |
| toward_teacher|all|no_s3|raw_agree|grad_core_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.29431e-06 | False | -0.000326457 | -0.000284631 | 4 | 7 | -0.000684332 | -0.000404961 | 0.00244349 | True | True | True | False |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_2of3|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.26661e-06 | False | -0.000292811 | -0.000261749 | 4 | 7 | -0.000552041 | -0.000314211 | 0.00234408 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2|raw_agree|grad_all_top50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.22951e-06 | False | -0.000299316 | -0.000279001 | 4 | 7 | -0.000528113 | -0.000357045 | 0.00224399 | True | True | True | False |
| toward_teacher|low_slack_half|no_s3|raw_agree|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.22447e-06 | False | -0.000276561 | -0.000245214 | 4 | 7 | -0.000571858 | -0.000383058 | 0.0018048 | True | True | True | False |
| toward_teacher|low_slack_half|all|raw_agree|grad_core_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.21875e-06 | False | -0.000287388 | -0.000249521 | 4 | 7 | -0.000572958 | -0.000396958 | 0.001904 | True | True | True | False |
| toward_teacher|all|no_s3|raw_agree|grad_core_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.21648e-06 | False | -0.000279176 | -0.000235789 | 4 | 7 | -0.000602651 | -0.000378651 | 0.0018176 | True | True | True | False |
| toward_teacher|low_slack_half|no_q2|all|grad_all_4of6|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.20822e-06 | False | -0.00031168 | -0.000294232 | 4 | 7 | -0.000534333 | -0.000372163 | 0.00254107 | True | True | True | False |
| toward_teacher|all|all|raw_agree|grad_all_abs50|all|w0.070|c0.080 | toward_teacher | 0.577731 | -3.20284e-06 | False | -0.000293758 | -0.000256541 | 4 | 7 | -0.000651968 | -0.000408768 | 0.001968 | True | True | True | False |

## Decision

- eligible toward-teacher submission gates: `0`.
- diagnostic reverse-control gates: `0`.
- best toward-teacher anchor delta: `-3.64959e-06` from `toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|w0.070|c0.080`.
- best reverse-control anchor delta: `-8.94278e-09` from `reverse_control|all|q_targets|support60|grad_all_6of6|teacher_row_top50|w0.006|c0.018`.
- No submission file is justified by E63.

## Interpretation

If gradient-consensus gates beat E58/E62 with selector-scale margin, E56 teacher has independent non-anchor support. If they remain sub-margin or require reverse movement, then the hidden-rate views do not validate E56 as a probability translator.

## Outputs

- `analysis_outputs/gradient_consensus_posterior_probe_scan.csv`
- `analysis_outputs/gradient_consensus_posterior_probe_summary.csv`
- `analysis_outputs/gradient_consensus_posterior_probe_view_summary.csv`
