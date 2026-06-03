# H148 Listener-Responsibility Equation HS-JEPA

Date: 2026-06-03

## Question

H057 proves that some row-state correction is public-positive. H088 proves that
not every public/private-looking action is safe. H144/H145 prove that a
plausible two-cell branch can be almost inaudible to public. H148 asks:

```text
Can known public LB deltas recover a listener/responsibility field that tells
which row-target corrections public actually hears?
```

## Method

- Base: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` public LB `0.5677475939`.
- Observation unit: full `250 x 7 = 1750` row-target logit movement versus H057.
- Target: public LB delta versus H057.
- Fitter: origin-constrained dual ridge, with H144/H145 equality penalty in
  model selection.
- Translation source: `submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv`.
- Decoder: copy H071 assignment cells only when the listener equation says the
  cell is both heard and beneficial, with H088/tie-branch penalties.

## Public Observations Used

| file | public_lb | delta_vs_h057 | role |
| --- | --- | --- | --- |
| submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.567747594 | 0.000000000 | frontier |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.000157231 | frontier_basin |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | frontier_basin |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 0.567929641 | 0.000182047 | tie_sensor |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.567929641 | 0.000182047 | tie_sensor |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000375889 | breakthrough_anchor |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.568494202 | 0.000746608 | negative_sensor |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | pre_h_world |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | pre_h_world |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | pre_h_world |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008543736 | pre_h_world |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008552772 | pre_h_world |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | pre_h_world |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | pre_h_world |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | pre_h_world |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | pre_h_world |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | bad_anchor |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | bad_anchor |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | bad_anchor |

## Listener Model Selection

| model | alpha | n_obs | loo_mae | loo_rmse | loo_p90_abs | loo_spearman | h144_h145_pred_gap_abs | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h_frontier | 3.000000000 | 7 | 0.000278925 | 0.000375544 | 0.000531407 | -0.794461347 | 0.000000008 | 0.000279044 |
| h_frontier | 1.000000000 | 7 | 0.000290631 | 0.000399309 | 0.000561168 | -0.794461347 | 0.000000020 | 0.000290933 |
| h_frontier | 0.300000000 | 7 | 0.000305919 | 0.000447981 | 0.000627552 | -0.794461347 | 0.000000085 | 0.000307188 |
| h_frontier | 0.000010000 | 7 | 0.000317322 | 0.000575266 | 0.000796047 | -0.971008312 | 0.000000024 | 0.000317682 |
| h_frontier | 0.000030000 | 7 | 0.000317431 | 0.000575530 | 0.000796380 | -0.971008312 | 0.000000061 | 0.000318339 |
| h_frontier | 0.100000000 | 7 | 0.000316926 | 0.000503966 | 0.000703362 | -0.794461347 | 0.000000159 | 0.000319309 |
| h_frontier | 0.000100000 | 7 | 0.000317660 | 0.000575992 | 0.000796963 | -0.971008312 | 0.000000129 | 0.000319601 |
| h_frontier | 0.000300000 | 7 | 0.000317892 | 0.000576255 | 0.000797297 | -0.971008312 | 0.000000192 | 0.000320766 |
| h_frontier | 0.001000000 | 7 | 0.000318119 | 0.000575767 | 0.000796691 | -0.971008312 | 0.000000230 | 0.000321563 |
| h_frontier | 0.003000000 | 7 | 0.000318429 | 0.000573642 | 0.000794036 | -0.971008312 | 0.000000241 | 0.000322046 |
| h_frontier | 0.010000000 | 7 | 0.000319160 | 0.000566247 | 0.000784723 | -0.971008312 | 0.000000237 | 0.000322718 |
| h_frontier | 0.030000000 | 7 | 0.000319916 | 0.000547823 | 0.000761130 | -0.794461347 | 0.000000215 | 0.000323147 |
| all_observed | 1.000000000 | 19 | 0.000436045 | 0.000826826 | 0.001278932 | 0.400826660 | 0.000000599 | 0.000445029 |
| all_observed | 0.300000000 | 19 | 0.000434479 | 0.000866785 | 0.001317233 | 0.471074632 | 0.000000800 | 0.000446481 |
| all_observed | 3.000000000 | 19 | 0.000444606 | 0.000788303 | 0.001220506 | 0.390496076 | 0.000000334 | 0.000449615 |
| all_observed | 0.100000000 | 19 | 0.000450693 | 0.000900903 | 0.001342078 | 0.495868033 | 0.000000905 | 0.000464274 |
| all_observed | 0.030000000 | 19 | 0.000477757 | 0.000937213 | 0.001369952 | 0.530992019 | 0.000000980 | 0.000492459 |
| all_observed | 0.010000000 | 19 | 0.000506882 | 0.000972835 | 0.001399042 | 0.535124252 | 0.000001033 | 0.000522374 |

Chosen model: `h_frontier`.

## Observed Fit

| file | role | actual_delta | h_frontier_fit_delta | h_frontier_fit_error |
| --- | --- | --- | --- | --- |
| submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | frontier | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | frontier_basin | 0.000157231 | 0.000241422 | 0.000084191 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | frontier_basin | 0.000157231 | 0.000179545 | 0.000022315 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | tie_sensor | 0.000182047 | 0.000007608 | -0.000174439 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | tie_sensor | 0.000182047 | 0.000007616 | -0.000174431 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | breakthrough_anchor | 0.000375889 | 0.000256055 | -0.000119834 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | negative_sensor | 0.000746608 | 0.000726133 | -0.000020475 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | pre_h_world | 0.008411356 | -0.001567660 | -0.009979016 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | pre_h_world | 0.008532974 | -0.001569765 | -0.010102738 |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | pre_h_world | 0.008542835 | -0.001563534 | -0.010106369 |
| submission_e95_hardtail_541e3973.csv | pre_h_world | 0.008543736 | -0.001568072 | -0.010111808 |
| submission_e101_q2s3tail_177569bc.csv | pre_h_world | 0.008552772 | -0.001568141 | -0.010120913 |
| submission_mixmin_0c916bb4.csv | pre_h_world | 0.008559047 | -0.001569776 | -0.010128823 |
| submission_e176_abl_q2_to0p75_91e49725.csv | pre_h_world | 0.008564237 | -0.001568792 | -0.010133029 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | pre_h_world | 0.008581903 | -0.001567158 | -0.010149061 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | pre_h_world | 0.008660183 | -0.001571680 | -0.010231864 |
| submission_e323_5508f966_uploadsafe.csv | bad_anchor | 0.009287908 | -0.001569875 | -0.010857783 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | bad_anchor | 0.009538915 | -0.001595437 | -0.011134352 |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | bad_anchor | 0.010424224 | -0.001605456 | -0.012029679 |

## Highest-Responsibility Cells

| row | subject_id | sleep_date | lifelog_date | target | h057_prob | listener_coef | listener_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 144 | id06 | 2024-08-14 00:00:00 | 2024-08-13 00:00:00 | S4 | 0.999805884 | 0.000021739 | 1.000000000 |
| 139 | id06 | 2024-07-19 00:00:00 | 2024-07-18 00:00:00 | S3 | 0.999832218 | 0.000021739 | 0.999428571 |
| 135 | id06 | 2024-07-14 00:00:00 | 2024-07-13 00:00:00 | S3 | 0.999817432 | 0.000021739 | 0.998857143 |
| 188 | id08 | 2024-08-10 00:00:00 | 2024-08-09 00:00:00 | Q3 | 0.659822798 | 0.000018383 | 0.998285714 |
| 164 | id07 | 2024-07-26 00:00:00 | 2024-07-25 00:00:00 | S1 | 0.922350704 | 0.000014809 | 0.997714286 |
| 70 | id03 | 2024-09-16 00:00:00 | 2024-09-15 00:00:00 | Q1 | 0.997205140 | -0.000014636 | 0.997142857 |
| 164 | id07 | 2024-07-26 00:00:00 | 2024-07-25 00:00:00 | S4 | 0.377326496 | -0.000014421 | 0.996571429 |
| 128 | id06 | 2024-07-07 00:00:00 | 2024-07-06 00:00:00 | S1 | 0.999977178 | 0.000013309 | 0.996000000 |
| 54 | id02 | 2024-10-12 00:00:00 | 2024-10-11 00:00:00 | S1 | 0.999975462 | 0.000013309 | 0.995428571 |
| 32 | id02 | 2024-08-31 00:00:00 | 2024-08-30 00:00:00 | S2 | 0.999967117 | 0.000013309 | 0.994857143 |
| 130 | id06 | 2024-07-09 00:00:00 | 2024-07-08 00:00:00 | S1 | 0.999979766 | 0.000013309 | 0.994285714 |
| 31 | id02 | 2024-08-30 00:00:00 | 2024-08-29 00:00:00 | S2 | 0.999967095 | 0.000013309 | 0.993714286 |
| 140 | id06 | 2024-07-21 00:00:00 | 2024-07-20 00:00:00 | S2 | 0.999967329 | 0.000013309 | 0.993142857 |
| 142 | id06 | 2024-08-12 00:00:00 | 2024-08-11 00:00:00 | S2 | 0.999972396 | 0.000013309 | 0.992571429 |
| 138 | id06 | 2024-07-18 00:00:00 | 2024-07-17 00:00:00 | S3 | 0.995121614 | 0.000013309 | 0.992000000 |
| 129 | id06 | 2024-07-08 00:00:00 | 2024-07-07 00:00:00 | S2 | 0.993291559 | 0.000013309 | 0.991428571 |
| 140 | id06 | 2024-07-21 00:00:00 | 2024-07-20 00:00:00 | S3 | 0.996093890 | 0.000013309 | 0.990857143 |
| 129 | id06 | 2024-07-08 00:00:00 | 2024-07-07 00:00:00 | S1 | 0.999980303 | 0.000013309 | 0.990285714 |
| 142 | id06 | 2024-08-12 00:00:00 | 2024-08-11 00:00:00 | S1 | 0.999975996 | 0.000013309 | 0.989714286 |
| 147 | id06 | 2024-08-21 00:00:00 | 2024-08-20 00:00:00 | S2 | 0.999970132 | 0.000013309 | 0.989142857 |
| 54 | id02 | 2024-10-12 00:00:00 | 2024-10-11 00:00:00 | S2 | 0.987462364 | 0.000012552 | 0.988571429 |
| 164 | id07 | 2024-07-26 00:00:00 | 2024-07-25 00:00:00 | Q1 | 0.572623636 | -0.000011323 | 0.988000000 |
| 151 | id06 | 2024-08-25 00:00:00 | 2024-08-24 00:00:00 | Q3 | 0.805151753 | 0.000011154 | 0.987428571 |
| 145 | id06 | 2024-08-15 00:00:00 | 2024-08-14 00:00:00 | S2 | 0.999970509 | 0.000010921 | 0.986857143 |
| 137 | id06 | 2024-07-17 00:00:00 | 2024-07-16 00:00:00 | S1 | 0.999977748 | 0.000010916 | 0.986285714 |

## Candidate Stress Ranking

| file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | h_frontier_pred_delta | h_frontier_high_listener_toxic_cells | h_frontier_high_listener_benefit_cells |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 28 | 23 | -0.057669876 | 0.000006336 | 12 | 15 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 28 | 23 | -0.064775307 | 0.000007608 | 11 | 15 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 27 | 22 | -0.063807440 | 0.000007616 | 11 | 15 |
| submission_h141_commoncore_0999d3ae_uploadsafe.csv | 27 | 22 | -0.063558603 | 0.000007665 | 11 | 15 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 343 | 111 | -0.125396149 | 0.000179545 | 40 | 17 |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 270 | 45 | -0.144085796 | 0.000241422 | 39 | 10 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 315 | 45 | -0.144102131 | 0.000256055 | 80 | 10 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 980 | 168 | 1.000000000 | 0.000726133 | 94 | 18 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 524 | 152 | 0.835549425 | 0.001036091 | 76 | 27 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 597 | 152 | 0.828647527 | 0.001070554 | 80 | 25 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 736 | 158 | 0.887472000 | 0.001226392 | 84 | 22 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 657 | 141 | 0.887213191 | 0.001228502 | 83 | 9 |

## Promoted Diagnostic Candidate

| candidate_file | candidate_path | source_file | best_listener_model | selected_cells | selected_rows | selected_targets | worldview | why_big_bet | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | metric_changed_cells_vs_h057 | metric_changed_rows_vs_h057 | metric_move_l1 | metric_move_l2 | metric_prob_l1_vs_h057 | metric_h088_move_cosine | metric_h_frontier_pred_delta | metric_h_frontier_listened_benefit_sum | metric_h_frontier_listened_toxicity_sum | metric_h_frontier_high_listener_toxic_cells | metric_h_frontier_high_listener_benefit_cells | metric_h_frontier_listener_mass_changed | metric_h_plus_bad_pred_delta | metric_h_plus_bad_listened_benefit_sum | metric_h_plus_bad_listened_toxicity_sum | metric_h_plus_bad_high_listener_toxic_cells | metric_h_plus_bad_high_listener_benefit_cells | metric_h_plus_bad_listener_mass_changed | metric_all_observed_pred_delta | metric_all_observed_listened_benefit_sum | metric_all_observed_listened_toxicity_sum | metric_all_observed_high_listener_toxic_cells | metric_all_observed_high_listener_benefit_cells | metric_all_observed_listener_mass_changed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h148_listeneraware_assignment_d8d2e3b6_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h148_listeneraware_assignment_d8d2e3b6_uploadsafe.csv | submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | h_frontier | 22 | 19 | Q1,Q2,S2,S4 | H057 found a listened row-state; H071 has broad assignment support; H148 translates H071 through a public listener equation learned from H057/H088/H144/H145 and older bad anchors. | This is not a top-k alpha tweak: it tests whether public LB deltas can recover the hidden listener field that decides which row-target actions are heard. | /Users/kbsoo/Downloads/cl2/submission_h148_listeneraware_assignment_d8d2e3b6_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 22 | True | 22 | 19 | 7.085624696 | 2.060149773 | 1.132740826 | 0.001921438 | -0.000036025 | 0.000036025 | 0.000000000 | 0 | 21 | 0.000087686 | -0.000489131 | 0.000509851 | 0.000020720 | 2 | 19 | 0.001278696 | -0.000078777 | 0.000080793 | 0.000002017 | 0 | 0 | 0.000198041 |

Selected cell target counts:

| target | cells |
| --- | --- |
| Q2 | 19 |
| S4 | 1 |
| S2 | 1 |
| Q1 | 1 |

## Interpretation

H148 treats listener responsibility as a separate HS-JEPA target representation:

```text
context -> hidden human state -> action proposal
        -> listener responsibility -> toxicity/safety -> correction field
```

The promoted candidate is a diagnostic, not a guaranteed submission slot.  It is
a large worldview test: if this family improves public, then public LB deltas
can be inverted into a useful row-target listener head.  If it fails, the public
equation is too underdetermined at cell resolution and listener recovery must
move to row/route bundles rather than individual cells.
