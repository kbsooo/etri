# E66 Q2/S3 Conflict Translator Probe

## Observe

E65's best local response excludes Q2 and S3. That could mean target loss conflict, hidden-view conflict, or nonlinear anchor-score conflict.

## Wonder

When the same E56 gradient cell set is held fixed, what exactly happens when Q2 and/or S3 are added back?

## Method

- Generated focused matched-mask candidates: `3000`.
- Masks: `all`, `no_q2`, `no_s3`, `no_q2_s3`, `q2`, `s3`, `q2_s3`.
- For each candidate, computed actual-anchor score, actual-anchor target mean contribution, hidden core/all target BCE deltas, and paired same-configuration deltas versus `no_q2_s3`.

## Target Mask Response

| target_mask | n | anchor_beats_mixmin | best_anchor_delta | median_anchor_delta | best_hidden_core_delta | median_hidden_core_delta | best_anchor_q2_s3_contrib | median_anchor_q2_s3_contrib | best_candidate | best_anchor_mean_delta_Q1 | best_hidden_core_delta_Q1 | best_anchor_mean_delta_Q2 | best_hidden_core_delta_Q2 | best_anchor_mean_delta_Q3 | best_hidden_core_delta_Q3 | best_anchor_mean_delta_S1 | best_hidden_core_delta_S1 | best_anchor_mean_delta_S2 | best_hidden_core_delta_S2 | best_anchor_mean_delta_S3 | best_hidden_core_delta_S3 | best_anchor_mean_delta_S4 | best_hidden_core_delta_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_q2_s3 | 432 | 328 | -5.99494e-06 | -2.28245e-06 | -0.000674013 | -0.000214967 | -4.45966e-18 | -4.45966e-18 | toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | -3.08142e-06 | -0.00136174 | 4.44795e-19 | 0 | 4.61952e-07 | -0.000678273 | -5.19124e-06 | -0.0018412 | 3.18398e-07 | -0.000295031 | -4.90445e-18 | 0 | -2.059e-06 | -0.000541841 |
| no_q2 | 432 | 300 | -5.09038e-06 | -1.70122e-06 | -0.000521864 | -0.000230535 | -1.01231e-06 | -2.64095e-07 | toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | -2.53341e-06 | -0.000997123 | 4.44795e-19 | 0 | 8.39341e-08 | -0.000497502 | -4.10261e-06 | -0.00134766 | 8.08958e-08 | -0.000216651 | -1.01231e-06 | -0.000196787 | -1.69095e-06 | -0.000397324 |
| no_s3 | 432 | 287 | -4.72639e-06 | -1.86187e-06 | -0.000567623 | -0.000248735 | 5.53759e-07 | 1.3041e-07 | toward_teacher|all|no_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | -2.53341e-06 | -0.000997123 | 5.53759e-07 | -0.000517098 | 8.39341e-08 | -0.000497502 | -4.10261e-06 | -0.00134766 | 8.08958e-08 | -0.000216651 | -4.90445e-18 | 0 | -1.69095e-06 | -0.000397324 |
| all | 432 | 274 | -4.19324e-06 | -1.35733e-06 | -0.000543835 | -0.000264242 | -5.1218e-07 | -1.04e-07 | toward_teacher|all|all|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | -2.37232e-06 | -0.000910091 | 4.3656e-07 | -0.000472228 | 2.1495e-08 | -0.000454261 | -3.80981e-06 | -0.00122992 | 4.08285e-08 | -0.000197875 | -9.48739e-07 | -0.000179709 | -1.58307e-06 | -0.000362767 |
| s3 | 432 | 2 | -2.14385e-08 | 3.70719e-07 | -5.34089e-06 | -1.44447e-05 | -3.44376e-07 | -2.64095e-07 | toward_teacher|all|s3|support60|grad_all_abs50|all|flat|s0.070|c0.080 | -9.59302e-20 | 0 | 4.44795e-19 | 0 | -4.44788e-18 | 0 | -2.68946e-18 | 0 | 3.63037e-18 | 0 | -3.44376e-07 | -3.73863e-05 | 2.82668e-18 | -2.77556e-17 |
| q2_s3 | 432 | 0 | 9.37611e-08 | 7.67078e-07 | -3.70219e-05 | -4.80744e-05 | -4.47706e-07 | -1.04e-07 | toward_teacher|all|q2_s3|raw_agree|grad_all_abs50|all|core_gain|s0.070|c0.080 | -9.59302e-20 | 0 | -4.39669e-08 | -0.000178553 | -4.44788e-18 | 0 | -2.68946e-18 | 0 | 3.63037e-18 | 0 | -4.03739e-07 | -8.06002e-05 | 2.82668e-18 | -2.77556e-17 |
| q2 | 408 | 0 | 1.02254e-07 | 4.72058e-07 | -2.55075e-05 | -3.35698e-05 | -4.39669e-08 | 1.32319e-07 | toward_teacher|all|q2|raw_agree|grad_all_abs50|all|core_gain|s0.070|c0.080 | -9.59302e-20 | 0 | -4.39669e-08 | -0.000178553 | -4.44788e-18 | 0 | -2.68946e-18 | 0 | 3.63037e-18 | 0 | -4.90445e-18 | 0 | 2.82668e-18 | -2.77556e-17 |

## Matched Add-Back Summary

- matched base configurations: `432`.
- `add_all_anchor_minus_no_q2_s3` adverse count: `432/432`.
- `add_all_mean_anchor_minus_no_q2_s3` adverse count: `144/432`.
- `add_no_q2_anchor_minus_no_q2_s3` adverse count: `429/432`.
- `add_no_q2_mean_anchor_minus_no_q2_s3` adverse count: `46/432`.
- `add_no_s3_anchor_minus_no_q2_s3` adverse count: `432/432`.
- `add_no_s3_mean_anchor_minus_no_q2_s3` adverse count: `402/432`.
- `add_q2_anchor_minus_no_q2_s3` adverse count: `380/432`.
- `add_q2_mean_anchor_minus_no_q2_s3` adverse count: `404/432`.
- `add_s3_anchor_minus_no_q2_s3` adverse count: `378/432`.
- `add_s3_mean_anchor_minus_no_q2_s3` adverse count: `409/432`.
- `add_q2_s3_anchor_minus_no_q2_s3` adverse count: `424/432`.
- `add_q2_s3_mean_anchor_minus_no_q2_s3` adverse count: `421/432`.
- `add_all` mean-anchor improves: `288/432`.
- `add_all` max-set tail worsens: `432/432`.
- `add_all` min-set tail improves: `432/432`.

| band | base_cell_gate | gradient_gate | row_gate | shape | scale | cap | base_no_q2_s3_anchor_delta | add_all_anchor_minus_no_q2_s3 | add_all_mean_anchor_minus_no_q2_s3 | add_all_max_set_minus_no_q2_s3 | add_no_q2_anchor_minus_no_q2_s3 | add_no_s3_anchor_minus_no_q2_s3 | add_q2_s3_anchor_minus_no_q2_s3 | add_all_hidden_core_minus_no_q2_s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | support60 | grad_all_abs50 | all | core_gain | 0.07 | 0.08 | -9.24084e-08 | 1.76837e-07 | -1.97775e-07 | 1.2903e-06 | -2.28815e-08 | 1.7858e-07 | 2.46635e-07 | -1.33876e-05 |
| all | support60 | grad_all_abs50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -4.38182e-08 | 1.97856e-07 | -6.52718e-08 | 8.92132e-07 | -2.86845e-09 | 1.82075e-07 | 2.40358e-07 | -1.10872e-05 |
| all | support60 | grad_all_4of6 | all | core_gain | 0.07 | 0.08 | -1.68237e-08 | 2.12674e-07 | -2.22394e-07 | 1.45747e-06 | 1.52236e-08 | 1.82059e-07 | 2.20235e-07 | -1.42545e-05 |
| all | raw_agree | grad_all_abs50 | all | core_gain | 0.07 | 0.08 | -2.38586e-06 | 2.15249e-07 | -4.47706e-07 | 2.11845e-06 | 1.56414e-07 | 6.18575e-08 | 2.47962e-06 | -3.70219e-05 |
| low_slack_half | support60 | grad_all_4of6 | all | core_gain | 0.07 | 0.08 | -1.12415e-07 | 2.31205e-07 | -1.50038e-07 | 1.37351e-06 | 8.31309e-08 | 1.51305e-07 | 3.41943e-07 | -1.36117e-05 |
| all | support60 | grad_core_top50 | all | core_gain | 0.07 | 0.08 | -2.36785e-08 | 2.39381e-07 | -1.60929e-07 | 1.39936e-06 | 2.95073e-08 | 1.88586e-07 | 2.49552e-07 | -1.40291e-05 |
| all | support60 | grad_all_abs50 | all | flat | 0.07 | 0.08 | -6.71055e-08 | 2.39443e-07 | -2.86451e-07 | 1.81401e-06 | -2.6421e-08 | 2.37967e-07 | 2.71763e-07 | -1.75555e-05 |
| low_slack_half | support60 | grad_core_top50 | all | core_gain | 0.07 | 0.08 | -5.58378e-08 | 2.40347e-07 | -1.17143e-07 | 1.31918e-06 | 8.56399e-08 | 1.54812e-07 | 2.92812e-07 | -1.36194e-05 |
| all | all | grad_all_abs50 | all | core_gain | 0.07 | 0.08 | -2.35753e-06 | 2.46226e-07 | -4.37474e-07 | 2.18083e-06 | 1.92553e-07 | 7.71947e-08 | 2.46796e-06 | -3.74352e-05 |
| low_slack_half | support60 | grad_all_abs50 | all | core_gain | 0.07 | 0.08 | -2.2898e-07 | 2.51021e-07 | -6.45548e-08 | 1.19407e-06 | 1.12894e-07 | 1.5642e-07 | 4.63216e-07 | -1.24548e-05 |
| low_slack_half | raw_agree | grad_all_4of6 | all | core_gain | 0.07 | 0.08 | -2.40062e-06 | 2.51247e-07 | -5.71195e-07 | 2.46003e-06 | 1.49769e-07 | 8.76294e-08 | 2.53766e-06 | -4.26524e-05 |
| low_slack_half | support60 | grad_all_abs50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -1.24961e-07 | 2.56364e-07 | -9.72282e-09 | 9.53967e-07 | 1.11328e-07 | 1.59169e-07 | 3.68761e-07 | -9.68209e-06 |
| all | all | grad_all_abs50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -1.52129e-06 | 2.56933e-07 | -1.34047e-07 | 1.33199e-06 | 1.82875e-07 | 9.45139e-08 | 1.79995e-06 | -2.4887e-05 |
| all | support60 | grad_all_4of6 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -9.14342e-09 | 2.63699e-07 | -7.08767e-08 | 1.04034e-06 | 6.07478e-08 | 2.02747e-07 | 2.53144e-07 | -1.16675e-05 |
| low_slack_half | support60 | grad_all_4of6 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -1.85112e-08 | 2.6497e-07 | -2.65884e-08 | 1.06126e-06 | 1.16998e-07 | 1.35276e-07 | 2.80125e-07 | -1.02111e-05 |
| low_slack_half | support60 | grad_core_top50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | 1.52732e-08 | 2.66249e-07 | 3.39982e-10 | 9.96718e-07 | 1.17662e-07 | 1.35557e-07 | 2.46995e-07 | -1.02984e-05 |
| low_slack_half | raw_agree | grad_core_top50 | all | core_gain | 0.07 | 0.08 | -2.36685e-06 | 2.67332e-07 | -4.89895e-07 | 2.41613e-06 | 1.75126e-07 | 7.33625e-08 | 2.51878e-06 | -4.30096e-05 |
| all | raw_agree | grad_all_abs50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | -1.56208e-06 | 2.68705e-07 | -1.37377e-07 | 1.29793e-06 | 1.91569e-07 | 1.16565e-07 | 1.83894e-06 | -2.45448e-05 |
| all | support60 | grad_all_abs50 | teacher_row_top50 | flat | 0.07 | 0.08 | -1.57839e-08 | 2.77161e-07 | -6.79409e-08 | 1.17374e-06 | 3.05535e-08 | 2.55035e-07 | 2.75175e-07 | -1.43012e-05 |
| all | support60 | grad_core_top50 | teacher_row_top50 | core_gain | 0.07 | 0.08 | 1.01256e-08 | 2.78565e-07 | -2.78146e-08 | 9.9786e-07 | 6.58844e-08 | 2.04242e-07 | 2.49438e-07 | -1.16022e-05 |

## Top Candidates

| candidate | target_mask | anchor_delta_vs_mixmin | anchor_mean_delta_q2_s3 | hidden_core_mean_delta | hidden_core_delta_Q2 | hidden_core_delta_S3 | mean_abs_logit_move_vs_mixmin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | no_q2_s3 | -5.99494e-06 | -4.45966e-18 | -0.000674013 | 0 | 0 | 0.00418971 |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.120 | no_q2_s3 | -5.91849e-06 | -4.45966e-18 | -0.000674463 | 0 | 0 | 0.00419863 |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | no_q2_s3 | -5.72727e-06 | -4.45966e-18 | -0.000668853 | 0 | 0 | 0.00417189 |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.120 | no_q2_s3 | -5.60384e-06 | -4.45966e-18 | -0.000670306 | 0 | 0 | 0.00418971 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | no_q2_s3 | -5.56959e-06 | -4.45966e-18 | -0.000493752 | 0 | 0 | 0.00306171 |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.095|c0.120 | no_q2_s3 | -5.48087e-06 | -4.45966e-18 | -0.000494084 | 0 | 0 | 0.00306823 |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | no_q2_s3 | -5.42003e-06 | -4.45966e-18 | -0.000489972 | 0 | 0 | 0.00304869 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | no_q2_s3 | -5.34592e-06 | -4.45966e-18 | -0.000450701 | 0 | 0 | 0.00279314 |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.095|c0.120 | no_q2_s3 | -5.32697e-06 | -4.45966e-18 | -0.000491041 | 0 | 0 | 0.00306171 |
| toward_teacher|all|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.080 | no_q2_s3 | -5.26138e-06 | -4.45966e-18 | -0.000451005 | 0 | 0 | 0.00279909 |
| toward_teacher|low_slack_half|no_q2_s3|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | no_q2_s3 | -5.22102e-06 | -4.45966e-18 | -0.000447252 | 0 | 0 | 0.00278126 |
| toward_teacher|low_slack_half|no_q2_s3|all|grad_all_abs50|all|flat|s0.130|c0.080 | no_q2_s3 | -5.13768e-06 | -4.45966e-18 | -0.000448228 | 0 | 0 | 0.00279314 |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.095|c0.120 | no_q2 | -5.09038e-06 | -1.01231e-06 | -0.000521864 | 0 | -0.000196787 | 0.00334183 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.095|c0.120 | no_q2_s3 | -5.08172e-06 | -4.45966e-18 | -0.000571728 | 0 | 0 | 0.004078 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_abs50|all|core_gain|s0.130|c0.120 | no_q2_s3 | -5.07031e-06 | -4.45966e-18 | -0.000443233 | 0 | 0 | 0.00250509 |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.130|c0.120 | no_q2 | -5.06254e-06 | -1.22638e-06 | -0.000712317 | 0 | -0.00026813 | 0.00457303 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|core_gain|s0.130|c0.120 | no_q2_s3 | -5.06046e-06 | -4.45966e-18 | -0.000481969 | 0 | 0 | 0.00300772 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_core_top50|all|flat|s0.130|c0.080 | no_q2_s3 | -5.01328e-06 | -4.45966e-18 | -0.000525827 | 0 | 0 | 0.00374174 |
| toward_teacher|all|no_q2_s3|raw_agree|grad_all_4of6|all|core_gain|s0.130|c0.120 | no_q2_s3 | -4.98189e-06 | -4.45966e-18 | -0.000486669 | 0 | 0 | 0.00315088 |
| toward_teacher|all|no_q2|raw_agree|grad_all_abs50|all|flat|s0.130|c0.080 | no_q2 | -4.95378e-06 | -9.48739e-07 | -0.000476374 | 0 | -0.000179709 | 0.00304869 |

## Decision

- E66 is an audit, not a submission generator.
- If Q2/S3 add-back is consistently actual-anchor adverse while hidden deltas remain favorable, the next translator must model target-specific public calibration rather than hidden direction.
- If Q2/S3 are also hidden-adverse, the E56 teacher cell set itself must be redefined for those targets.

## Outputs

- `analysis_outputs/q2_s3_conflict_translator_probe_scan.csv`
- `analysis_outputs/q2_s3_conflict_translator_probe_pair_decomposition.csv`
- `analysis_outputs/q2_s3_conflict_translator_probe_target_contribution.csv`
