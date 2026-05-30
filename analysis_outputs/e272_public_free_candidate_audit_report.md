# E272 Public-Free Candidate Audit

## Question

Can any social/cash-flow follow-up be promoted without spending another public LB test?

## Promotion Rule

A scarce public submission requires `strict_promote_gate`: p90 predicted delta vs current E247 < `-0.00005`, candidate beats current in at least `75%` of pairwise stress scenarios, and incremental bad-axis change versus E247 <= `0.015`.

If a candidate is only mean-negative but its p10/p90 interval overlaps zero, it is an information sensor but not a submission-grade candidate.

## Model Reliability

- known public anchors: `17`
- selected local selector models: `1`
- selected model current-order pass rate: `1.000`
- selected model median LOO sign accuracy: `0.732`
- selected model median L2O sign accuracy: `0.625`

## Candidate Decisions

- strict promote count: `0`
- information-sensor count: `9`
- best local candidate by gate/sort: `submission_e269_anti_e256_tophalf_beta035_4e910856.csv` -> `too_small_to_submit`

## E271 Cash-Flow Read

- decision: `too_small_to_submit`
- pred mean delta vs E247: `-0.000005422`
- pred p10/p90 delta vs E247: `-0.000007555` / `-0.000001953`
- beats-current scenario rate: `1.000`
- interpretation: cash-flow is a plausible story diagnostic, but this candidate does not clear the public-free promotion bar unless the row above says `promote_candidate`.

## E269 Social Boundary Read

- decision: `too_small_to_submit`
- pred mean delta vs E247: `-0.000011178`
- pred p10/p90 delta vs E247: `-0.000015892` / `-0.000003311`
- beats-current scenario rate: `0.971`

## Score Table

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | mean_abs_move_vs_a2c8 | mean_abs_move_vs_raw05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e269_anti_e256_tophalf_beta035_4e910856.csv | too_small_to_submit | -0.000017223 | -0.000022775 | -0.000008141 | 1.000000000 | -0.000686488 | 0.044400423 | 0.047533611 |
| submission_e269_combo_phonebed8_anti4_small_b27a2e23.csv | too_small_to_submit | -0.000011178 | -0.000015892 | -0.000003311 | 0.970588235 | 0.000074972 | 0.044401639 | 0.047527281 |
| submission_e271_cashflow_top8_anti4_tiny_ccd08be8.csv | too_small_to_submit | -0.000005422 | -0.000007555 | -0.000001953 | 1.000000000 | 0.000003168 | 0.044370086 | 0.047503273 |
| submission_e269_e247only_all_amp006_control_2cef7c9d.csv | too_small_to_submit | -0.000002100 | -0.000002622 | -0.000001460 | 1.000000000 | -0.000090704 | 0.044346372 | 0.047474043 |
| submission_e271_calendar_only_control_top8_36405aed.csv | too_small_to_submit | -0.000002617 | -0.000003433 | -0.000001312 | 1.000000000 | -0.000068002 | 0.044354460 | 0.047478454 |
| submission_e271_cashflow_top8_amp010_170ae6b0.csv | too_small_to_submit | -0.000001692 | -0.000002111 | -0.000001188 | 1.000000000 | -0.000075275 | 0.044344307 | 0.047477495 |
| submission_e271_pay25_pre3_only_amp016_62659ed5.csv | too_small_to_submit | -0.000002112 | -0.000003202 | -0.000001167 | 0.970588235 | -0.000172523 | 0.044336079 | 0.047469266 |
| submission_e271_cashflow_top6_amp014_ecc2b44c.csv | too_small_to_submit | -0.000001468 | -0.000001918 | -0.000000763 | 1.000000000 | -0.000042521 | 0.044350960 | 0.047484147 |
| submission_e271_cashflow_top6_anti_pay15_c12a8485.csv | too_small_to_submit | -0.000003479 | -0.000005149 | -0.000000596 | 0.941176471 | -0.000017194 | 0.044368248 | 0.047501436 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.044347121 | 0.047480309 |
| submission_mixmin_0c916bb4.csv | below_selector_resolution | -0.000019008 | -0.000063311 | 0.000059167 | 0.529411765 | 0.014065559 | 0.045614200 | 0.049029823 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | below_selector_resolution | 0.000051379 | 0.000034668 | 0.000065211 | 0.000000000 | 0.000877850 | 0.044309456 | 0.047413947 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | below_selector_resolution | 0.000030913 | -0.000000266 | 0.000066989 | 0.117647059 | 0.004508382 | 0.044653450 | 0.047737273 |
| submission_e95_hardtail_541e3973.csv | below_selector_resolution | 0.000037657 | -0.000004465 | 0.000082671 | 0.147058824 | -0.012373491 | 0.041131552 | 0.044481036 |

## Movement Anatomy

| basename | changed_cells_vs_current | changed_rows_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_submission_e256_featnn1_top50_amp_then_smooth25_a3827329 | cos_delta_with_submission_e267_humansocial_tail_balanced_2936100f |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e271_calendar_only_control_top8_36405aed.csv | 8 | 8 | 0.028227614 | 0.001273022 | -0.389687178 | -0.198291165 |
| submission_e271_cashflow_top6_amp014_ecc2b44c.csv | 6 | 6 | 0.028256535 | 0.001597182 | -0.318695281 | -0.162167149 |
| submission_e271_pay25_pre3_only_amp016_62659ed5.csv | 4 | 4 | 0.028512144 | 0.002204137 | -0.338505418 | -0.172247478 |
| submission_e271_cashflow_top8_amp010_170ae6b0.csv | 8 | 8 | 0.029905587 | 0.001377474 | -0.409231209 | -0.208236087 |
| submission_e269_e247only_all_amp006_control_2cef7c9d.csv | 13 | 13 | 0.030517540 | 0.000826439 | -0.543688921 | -0.276654495 |
| submission_e271_cashflow_top6_anti_pay15_c12a8485.csv | 8 | 8 | 0.055434019 | 0.002885853 | -0.607237569 | -0.067521094 |
| submission_e271_cashflow_top8_anti4_tiny_ccd08be8.csv | 12 | 12 | 0.068051236 | 0.003442609 | -0.930622589 | -0.075674260 |
| submission_e269_anti_e256_tophalf_beta035_4e910856.csv | 2 | 2 | 0.093278879 | 0.012106959 | -0.701592919 | 0.000000000 |
| submission_e269_combo_phonebed8_anti4_small_b27a2e23.csv | 12 | 12 | 0.124283781 | 0.006898588 | -0.921265673 | -0.059067466 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 17 | 17 | 0.949893339 | 0.033627922 | 1.000000000 | 0.150413984 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 60 | 54 | 3.375416139 | 0.041105376 | 0.150413984 | 1.000000000 |
| submission_e95_hardtail_541e3973.csv | 513 | 242 | 15.677961133 | 0.034974186 | 0.182615806 | 0.212537765 |
| submission_mixmin_0c916bb4.csv | 1019 | 250 | 25.169198999 | 0.034974186 | 0.161006930 | 0.187388233 |

## Decision

Do not spend a public LB slot on any candidate unless it clears `strict_promote_gate` or unless the explicit goal is information gain, not score improvement.

For the current social/cash-flow probes, the local bar is intentionally higher than before. A tiny boundary move can stay in the hypothesis graph, but it should not be called a score candidate when selector uncertainty is larger than the expected edge.

## Files

- `e272_public_free_candidate_audit_models.csv`
- `e272_public_free_candidate_audit_scores.csv`
- `e272_public_free_candidate_audit_anatomy.csv`
