# E170 E169 Public Feedback Decoder

## Question

If `submission_e169_ctx_veto_c5e806e3.csv` is submitted, how should its public
LB update the current world model without post-hoc tuning?

Current anchors:

- E95 public LB: `0.5762913298`
- E101 public LB: `0.5763003660`
- mixmin public LB: `0.5763066405`
- E95 edge over mixmin: `-0.0000153107`

## E169 Local Health Summary

| policy | expected_delta_focus_mean | moved_cells | moved_rows | cells_to_flip_expected | top1_over_abs_expected | bad_span_energy | max_bad_axis | max_bad_cos | mean_abs_logit_move_vs_e95 | q2s3_share_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context_high__veto | -0.000120457 | 904 | 193 | 32 | 0.048415375 | 0.295326361 | q2_bad | 0.222381361 | 0.001095928 | 0.347774767 |

## Decoder Bands

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | beats_e95 | beats_e101 | beats_mixmin | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| broad_breakthrough | -inf | 0.576261330 | True | True | True | Promote E169 as a new anchor. Decompose target/context amplitudes around ctx_veto before trying raw E166 or larger scale. |  |
| clean_win | 0.576261330 | 0.576276019 | True | True | True | Use E169 as the broad-branch anchor and run target/context ablations. Raw E166 becomes a controlled upside contrast, not the next automatic file. | conditional:raw_E166_as_upside_contrast |
| micro_win | 0.576276019 | 0.576288330 | True | True | True | Promote cautiously. Prefer attribution and breadth-preserving ablation over amplitude increase. |  |
| tie | 0.576288330 | 0.576294330 | False | True | True | Keep E95 as practical frontier. Raw E166 is allowed only as an explicit safety-atlas falsification sensor, not as an expected-score followup. | conditional:raw_E166_information_only |
| small_loss | 0.576294330 | 0.576300366 | False | False | True | Do not submit near-duplicate high-density p50. Decide between raw E166 as deliberate atlas-falsification or E154 as conservative repaired-branch sensor. | conditional:E154_or_raw_E166_by_question |
| e101_worse_mixmin_safe | 0.576300366 | 0.576306641 | False | False | False | Prefer E154 if a public slot is still available. Raw E166 should be used only if the next question is whether the safety atlas was overconservative. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| branch_loss | 0.576306641 | 0.576341330 | False | False | False | Demote E169 and raw E166. Use E154 only as the separate conservative branch, or rebuild the broad safety axis. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| hard_fail | 0.576341330 | inf | False | False | False | Close E169/E166 same-family followups and rebuild broad-branch bad-axis geometry from the failure. |  |

## Pairwise Hard-Label Readability

| new | base | moved_cells | moved_rows | targets_moved | expected_delta_focus_mean | cells_to_flip_expected_focus_mean | top1_swing | top5_swing | cells_for_2e6_guard | cells_for_e95_edge | support_prob_swing_weighted_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e169_ctx_veto | e95 | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000120457 | 32 | 0.000005832 | 0.000023823 | 1 | 4 | 0.459906676 |
| e169_high_density | e95 | 894 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000119080 | 32 | 0.000005832 | 0.000023823 | 1 | 4 | 0.460701782 |
| e166_raw | e95 | 1750 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000332077 | 74 | 0.000007761 | 0.000034557 | 1 | 3 | 0.465746836 |
| e169_ctx_veto | e166_raw | 846 | 240 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000211620 | 44 | 0.000007761 | 0.000034557 | 1 | 3 | 0.528678190 |
| e169_high_density | e166_raw | 856 | 240 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000212997 | 44 | 0.000007761 | 0.000034557 | 1 | 3 | 0.529522992 |
| e169_ctx_veto | e169_high_density | 10 | 10 | Q2,S3 | -0.000001377 | 1 | 0.000002652 | 0.000008177 | 1 | -1 | 0.374228338 |
| e169_ctx_veto | e154 | 1027 | 238 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000090619 | 7 | 0.000015957 | 0.000075262 | 1 | 1 | 0.503841913 |
| e169_ctx_veto | e101 | 944 | 201 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000166855 | 17 | 0.000014271 | 0.000057948 | 1 | 2 | 0.460646995 |
| e169_ctx_veto | mixmin | 1227 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000264999 | 6 | 0.000049128 | 0.000223837 | 1 | 1 | 0.504424502 |

## E169 Group Attribution

| group_kind | group | n_cells | n_rows | expected_delta_focus_mean | abs_expected_share | support_prob_swing_weighted | mean_safe_density | e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context_type | between_train_runs | 741 | 156 | -0.000097701 | 0.811087670 | 0.458003923 | 0.344889297 | 0.267206478 |
| context_type | after_train_run | 163 | 37 | -0.000022756 | 0.188912330 | 0.469605551 | 0.351883483 | 0.276073620 |
| e72_active | False | 661 | 193 | -0.000088834 | 0.737479817 | 0.460845333 | 0.305594769 | 0.000000000 |
| e72_active | True | 243 | 147 | -0.000031622 | 0.262520183 | 0.457533463 | 0.456468452 | 1.000000000 |
| target | S1 | 95 | 95 | -0.000023838 | 0.197895092 | 0.361074405 | 0.455104170 | 0.536842105 |
| target | S3 | 168 | 168 | -0.000022961 | 0.190613515 | 0.361719227 | 0.178804235 | 0.053571429 |
| target | Q2 | 165 | 165 | -0.000018847 | 0.156461805 | 0.533222074 | 0.184092630 | 0.006060606 |
| target | S4 | 116 | 116 | -0.000018812 | 0.156172857 | 0.495046639 | 0.435114405 | 0.344827586 |
| target | Q1 | 121 | 121 | -0.000014340 | 0.119046087 | 0.471280950 | 0.433137833 | 0.388429752 |
| target | S2 | 122 | 122 | -0.000013954 | 0.115845523 | 0.443728661 | 0.453014613 | 0.393442623 |
| target | Q3 | 117 | 117 | -0.000007705 | 0.063965120 | 0.572054126 | 0.436922678 | 0.401709402 |
| target_context | S3:between_train_runs | 141 | 141 | -0.000020977 | 0.174147096 | 0.364058838 | 0.177653070 | 0.063829787 |
| target_context | S1:between_train_runs | 79 | 79 | -0.000020808 | 0.172743512 | 0.359723491 | 0.456701058 | 0.544303797 |
| target_context | Q2:between_train_runs | 136 | 136 | -0.000015347 | 0.127408313 | 0.539060606 | 0.183938408 | 0.007352941 |
| target_context | S4:between_train_runs | 97 | 97 | -0.000013476 | 0.111872369 | 0.486800968 | 0.436260083 | 0.350515464 |
| target_context | Q1:between_train_runs | 99 | 99 | -0.000010805 | 0.089697380 | 0.466713930 | 0.433220050 | 0.363636364 |
| target_context | S2:between_train_runs | 91 | 91 | -0.000010165 | 0.084384508 | 0.436675820 | 0.454818945 | 0.384615385 |
| target_context | Q3:between_train_runs | 98 | 98 | -0.000006123 | 0.050834493 | 0.567288497 | 0.436983080 | 0.408163265 |
| target_context | S4:after_train_run | 19 | 19 | -0.000005336 | 0.044300488 | 0.528966892 | 0.429265418 | 0.315789474 |
| target_context | S2:after_train_run | 31 | 31 | -0.000003790 | 0.031461016 | 0.463392825 | 0.447718026 | 0.419354839 |
| target_context | Q1:after_train_run | 22 | 22 | -0.000003535 | 0.029348708 | 0.503019823 | 0.432767856 | 0.500000000 |
| target_context | Q2:after_train_run | 29 | 29 | -0.000003500 | 0.029053492 | 0.501622517 | 0.184815876 | 0.000000000 |
| target_context | S1:after_train_run | 16 | 16 | -0.000003030 | 0.025151580 | 0.369334247 | 0.447219538 | 0.500000000 |
| target_context | S3:after_train_run | 27 | 27 | -0.000001983 | 0.016466419 | 0.346491225 | 0.184815876 | 0.000000000 |
| target_context | Q3:after_train_run | 19 | 19 | -0.000001582 | 0.013130628 | 0.603806474 | 0.436611131 | 0.368421053 |

## Top E169-vs-E95 Hard-Label Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e169_ctx_veto_vs_e95 | 141 | S1 | 0.000005832 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 196 | Q3 | 0.000004562 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e95 | 190 | Q3 | 0.000004531 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e95 | 194 | Q3 | 0.000004466 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e95 | 67 | S4 | 0.000004432 | 1 | 0.287171717 | 0.151515152 | 0.150000000 |
| e169_ctx_veto_vs_e95 | 135 | S1 | 0.000004082 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 143 | S1 | 0.000004017 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 182 | Q3 | 0.000004015 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e95 | 205 | S2 | 0.000003995 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e169_ctx_veto_vs_e95 | 136 | S1 | 0.000003981 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 139 | S3 | 0.000003936 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e169_ctx_veto_vs_e95 | 180 | S1 | 0.000003915 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 63 | S1 | 0.000003819 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 70 | S4 | 0.000003816 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |
| e169_ctx_veto_vs_e95 | 113 | Q1 | 0.000003792 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e95 | 132 | S1 | 0.000003791 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 5 | Q1 | 0.000003755 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e95 | 138 | S3 | 0.000003626 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e169_ctx_veto_vs_e95 | 190 | Q2 | 0.000003605 | 0 | 0.562222222 | 0.562222222 | 0.562222222 |
| e169_ctx_veto_vs_e95 | 163 | Q1 | 0.000003596 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e95 | 141 | Q1 | 0.000003521 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e95 | 164 | S1 | 0.000003515 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e95 | 0 | Q1 | 0.000003508 | 1 | 0.361526649 | 0.439024390 | 0.150000000 |
| e169_ctx_veto_vs_e95 | 204 | S2 | 0.000003452 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e169_ctx_veto_vs_e95 | 79 | S4 | 0.000003436 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |

## Top E169-vs-Raw-E166 Mask-Removal Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e169_ctx_veto_vs_e166_raw | 122 | S2 | 0.000007761 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e169_ctx_veto_vs_e166_raw | 121 | S2 | 0.000007212 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e169_ctx_veto_vs_e166_raw | 130 | S1 | 0.000006851 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 129 | S1 | 0.000006603 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 193 | Q3 | 0.000006129 | 0 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e166_raw | 134 | S1 | 0.000005875 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 195 | Q3 | 0.000005821 | 0 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e166_raw | 10 | Q1 | 0.000005710 | 0 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e166_raw | 59 | S1 | 0.000005693 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 128 | S1 | 0.000005657 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 236 | S1 | 0.000005552 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 133 | S1 | 0.000005400 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 1 | Q1 | 0.000005373 | 0 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e166_raw | 228 | S1 | 0.000005363 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 68 | S1 | 0.000005231 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 191 | Q3 | 0.000005029 | 0 | 0.600000000 | 0.600000000 | 0.600000000 |
| e169_ctx_veto_vs_e166_raw | 248 | S1 | 0.000004978 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 63 | S4 | 0.000004965 | 0 | 0.560000000 | 0.560000000 | 0.560000000 |
| e169_ctx_veto_vs_e166_raw | 60 | S1 | 0.000004838 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 9 | Q1 | 0.000004830 | 0 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e166_raw | 168 | S1 | 0.000004764 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 103 | S1 | 0.000004693 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 2 | Q1 | 0.000004548 | 0 | 0.495555556 | 0.495555556 | 0.495555556 |
| e169_ctx_veto_vs_e166_raw | 247 | S1 | 0.000004435 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e169_ctx_veto_vs_e166_raw | 176 | S1 | 0.000004407 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |

## Observed Score Decision

_No observed E169 public score supplied._

## Decision

E170 creates no submission. The next broad-branch submission remains
`analysis_outputs/submission_e169_ctx_veto_c5e806e3.csv`.

- A win below E95 promotes the context-high/veto broad latent.
- A tie or small loss keeps E95 as practical frontier and makes raw E166 an
  information-only atlas-falsification sensor.
- A worse-than-E101 result demotes the E169 repair and shifts priority to E154
  or a new broad safety-axis search.
- A worse-than-mixmin result blocks near-duplicate E169 threshold variants.
