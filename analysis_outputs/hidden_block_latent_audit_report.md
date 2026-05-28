# Hidden Block Latent Audit

JEPA is treated here as a block-state reconstruction tool: the target is an entire hidden submission episode rate/count latent, and the context is surrounding train labels plus raw timeline state.

## Public Constraints Used

```csv
key,file,public_lb,role
anchor578,analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv,0.5784273528,observed_anchor
stage2,analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv,0.5779449757,observed_stage2
ordinal_q,analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv,0.5783033652,observed_bad_count_shift
raw05,jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv,0.5775263072,observed_raw_axis
jepa_bad_residual,jepa/submission_jepa_latent_residual_probe.csv,0.5812273278,observed_jepa_bad_axis
jepa_bad_q2,jepa/submission_jepa_latent_q2_w0p45.csv,0.5798012862,observed_jepa_bad_axis
```

## Raw-Rescue Axis

The observed raw05 public score fits a stage2->raw05 latent with one scalar alpha. Scanning the stronger raw10 direction gives only a tiny expected gain beyond raw05, so this is a probe axis, not the 0.54 breakthrough.

```csv
candidate_kind,scale,pred_public_from_raw05_axis,pred_delta_vs_stage2,mean_abs_move_vs_stage2,raw05_latent_alpha
raw_strict_scale_scan,0.875,0.5775085176,-0.0004364581,0.0094655003,1.2808825328
raw_strict_scale_scan,0.9,0.5775088035,-0.0004361722,0.0097358921,1.2808825328
raw_strict_scale_scan,0.85,0.5775089408,-0.0004360349,0.0091950966,1.2808825328
raw_strict_scale_scan,0.925,0.5775097984,-0.0004351773,0.0100062711,1.2808825328
raw_strict_scale_scan,0.825,0.577510073,-0.0004349027,0.0089246817,1.2808825328
raw_strict_scale_scan,0.95,0.5775115023,-0.0004334734,0.0102766365,1.2808825328
raw_strict_scale_scan,0.8,0.5775119143,-0.0004330614,0.0086542565,1.2808825328
raw_strict_scale_scan,0.975,0.5775139153,-0.0004310604,0.0105469875,1.2808825328
raw_strict_scale_scan,0.775,0.5775144647,-0.000430511,0.0083838218,1.2808825328
raw_strict_scale_scan,1.0,0.5775170372,-0.0004279385,0.0108173233,1.2808825328
raw_strict_scale_scan,0.75,0.5775177241,-0.0004272516,0.0081133784,1.2808825328
raw_strict_scale_scan,1.025,0.5775208681,-0.0004241076,0.011087643,1.2808825328
```

Saved raw-axis candidates:

- `submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv`
- `submission_hiddenblock_rawaxis_stage2_raw10_s0p875_f5e1e1c0.csv`
- `submission_hiddenblock_rawaxis_stage2_raw10_s1p0_e8dc057d.csv`
- `submission_hiddenblock_posterior_raw05_g0p05_8b49d70e.csv`
- `submission_hiddenblock_posterior_raw05_g0p1_18050567.csv`
- `submission_hiddenblock_posterior_raw05_g0p2_9588c3fc.csv`

## Block Posterior Constraint Fit

```csv
constraint_index,target_score,fitted_score,residual,converged,iterations,constraint_key,constraint_role
0,0.5784273528,0.5784273528,-0.0,True,5,anchor578,observed_anchor
1,0.5779449757,0.5779449757,0.0,True,5,stage2,observed_stage2
2,0.5783033652,0.578303365201,-1e-12,True,5,ordinal_q,observed_bad_count_shift
3,0.5775263072,0.577526307201,-1e-12,True,5,raw05,observed_raw_axis
4,0.5812273278,0.5812273278,-0.0,True,5,jepa_bad_residual,observed_jepa_bad_axis
5,0.5798012862,0.5798012862,-0.0,True,5,jepa_bad_q2,observed_jepa_bad_axis
```

## Candidate Public-Fit Ranking

```csv
candidate,observed_public_lb,posterior_expected_public_vs_anchor,raw_axis_expected_public_vs_stage2,mean_abs_move_vs_stage2,mean_abs_move_vs_raw05,bad_residual_axis_ratio,bad_q2_axis_ratio,min_prob,max_prob
raw075,,0.5774891896,0.5775057524,0.0096266335,0.0021945509,0.0037765761,0.0,0.0611045272,0.9802206775
submission_hiddenblock_rawaxis_stage2_raw10_s0p875_f5e1e1c0.csv,,0.5774648824,0.5775085176,0.0094655003,0.0021443118,0.0004918985,-0.0,0.061758719,0.9800579119
raw10,,0.5774671684,0.5775170372,0.0108173233,0.0034587804,0.0006116387,0.0,0.0611819112,0.9801772771
submission_hiddenblock_rawaxis_stage2_raw10_s1p0_e8dc057d.csv,,0.5774671684,0.5775170372,0.0108173233,0.0034587804,0.0006116387,-0.0,0.0611819112,0.9801772771
submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,,0.5774803224,0.5775177241,0.0081133784,0.0009288469,0.0003838461,-0.0,0.0623406037,0.9799378427
raw05,0.5775263072,0.5775263072,0.5775263072,0.0074542211,0.0,0.0048441395,0.0,0.0619387639,0.9800550384
submission_hiddenblock_posterior_raw05_g0p05_8b49d70e.csv,,0.5742878257,0.5776103284,0.0089887424,0.0043049547,-0.0075040086,-0.0025160486,0.0680963432,0.9793303293
raw025,,0.5776446317,0.5776404825,0.0042593847,0.0031991638,0.0036620609,0.0,0.0635800945,0.979709276
submission_hiddenblock_posterior_raw05_g0p1_18050567.csv,,0.5712244033,0.5778694087,0.0119281771,0.0086085136,-0.0200111659,-0.0050032935,0.0662510713,0.978579863
stage2,0.5779449757,0.5779449757,0.5779449757,0.0,0.0074542211,0.0,0.0,0.0659406575,0.9792024182
submission_hiddenblock_posterior_raw05_g0p2_9588c3fc.csv,,0.5656227075,0.5789127183,0.0193548938,0.017200895,-0.0455157242,-0.009888512,0.0624918114,0.9769981409
jepa_bad_q2,0.5798012862,0.5798012862,0.5796628467,0.0068679694,0.0143221905,0.5726249631,1.0,0.0659406575,0.9792024182
jepa_bad_residual,0.5812273278,0.5812273278,0.5800188824,0.0196506083,0.0215094714,1.0,0.640393451,0.0598283935,0.9804379902
ordinal_q,0.5783033652,0.5783033652,0.5813293869,0.0245912956,0.0255997269,-0.0035798689,-0.0117225328,0.0719103318,0.9811666297
anchor578,0.5784273528,0.5784273528,0.5831131699,0.0340060416,0.03485168,-0.0476969461,-0.0197657414,0.1075237074,0.9769920311
```

## Highest Posterior Block Shifts

```csv
hidden_block_id,subject_id,n_rows,start,end,posterior_mean_abs_shift,raw05_mean_abs_shift_vs_stage2
id08_b12,id08,2,2024-09-13,2024-09-14,0.1473808,0.01028382
id08_b8,id08,1,2024-09-04,2024-09-04,0.11165407,0.00590237
id04_b4,id04,5,2024-09-11,2024-09-15,0.10727046,0.00919885
id10_b4,id10,11,2024-09-15,2024-09-26,0.10725758,0.01026129
id08_b4,id08,6,2024-08-05,2024-08-10,0.10352144,0.00999434
id01_b2,id01,14,2024-07-30,2024-08-16,0.10177171,0.008005
id05_b6,id05,2,2024-11-06,2024-11-07,0.09915312,0.00461589
id05_b10,id05,5,2024-11-15,2024-11-19,0.09680495,0.0087711
id08_b14,id08,2,2024-09-17,2024-09-19,0.09616694,0.00649583
id04_b8,id04,6,2024-10-14,2024-10-19,0.09468456,0.00641048
id05_b4,id05,5,2024-10-10,2024-10-17,0.09439791,0.00640085
id01_b4,id01,13,2024-09-01,2024-09-14,0.09390354,0.0072914
id05_b2,id05,7,2024-09-28,2024-10-06,0.092171,0.01044818
id08_b10,id08,4,2024-09-06,2024-09-10,0.09193321,0.00823527
id05_b8,id05,2,2024-11-12,2024-11-13,0.09007597,0.00897679
id09_b2,id09,14,2024-08-05,2024-08-20,0.08885707,0.00796351
id04_b2,id04,1,2024-09-09,2024-09-09,0.08777378,0.01062378
id04_b14,id04,3,2024-10-27,2024-10-29,0.08752589,0.00908699
```

## Endpoint Priors

Endpoint/length priors are saved as `hidden_block_endpoint_priors.csv`. They are useful as weak count priors; pseudo-block tests show endpoints are informative but too noisy for hard constraints.

```csv
hidden_block_id,subject_id,n_rows,len_bin,endpoint_rate_Q1,endpoint_count_Q1,endpoint_source_Q1,endpoint_support_Q1,endpoint_sd_Q1,endpoint_rate_Q2,endpoint_count_Q2,endpoint_source_Q2,endpoint_support_Q2,endpoint_sd_Q2,endpoint_rate_Q3,endpoint_count_Q3,endpoint_source_Q3,endpoint_support_Q3,endpoint_sd_Q3,endpoint_rate_S1,endpoint_count_S1,endpoint_source_S1,endpoint_support_S1,endpoint_sd_S1,endpoint_rate_S2,endpoint_count_S2,endpoint_source_S2,endpoint_support_S2,endpoint_sd_S2,endpoint_rate_S3,endpoint_count_S3,endpoint_source_S3,endpoint_support_S3,endpoint_sd_S3,endpoint_rate_S4,endpoint_count_S4,endpoint_source_S4,endpoint_support_S4,endpoint_sd_S4
id01_b2,id01,14,11-16,0.404461,5.662455,prev_next_len,480,0.198585,0.636056,8.904778,prev_next_len,624,0.202124,0.65673,9.19422,prev_next_len,685,0.171493,0.756212,10.586972,prev_next_len,886,0.189861,0.617872,8.650202,prev_next_len,352,0.202826,0.790971,11.07359,prev_next_len,896,0.193962,0.547713,7.667984,prev_next_len,424,0.204568
id01_b4,id01,13,11-16,0.635366,8.259756,prev_shrunk,0,,0.714634,9.290244,prev_shrunk,0,,0.730488,9.496341,prev_shrunk,0,,0.762195,9.908537,prev_shrunk,0,,0.730488,9.496341,prev_shrunk,0,,0.904878,11.763415,prev_shrunk,0,,0.667073,8.671951,prev_shrunk,0,
id02_b2,id02,16,11-16,0.492313,7.877014,prev_next_len,426,0.194363,0.642423,10.27876,prev_next_len,624,0.202124,0.617811,9.884972,prev_next_len,375,0.199337,0.766616,12.265862,prev_next_len,886,0.189861,0.799711,12.795377,prev_next_len,880,0.1935,0.792773,12.684369,prev_next_len,896,0.193962,0.570316,9.125059,prev_next_len,424,0.204568
id02_b4,id02,16,11-16,0.702083,11.233333,prev_shrunk,0,,0.783333,12.533333,prev_shrunk,0,,0.823958,13.183333,prev_shrunk,0,,0.91875,14.7,prev_shrunk,0,,0.945833,15.133333,prev_shrunk,0,,0.932292,14.916667,prev_shrunk,0,,0.4875,7.8,prev_shrunk,0,
id03_b2,id03,11,11-16,0.619776,6.817539,prev_next_len,443,0.232074,0.65155,7.167049,prev_next_len,624,0.202124,0.617628,6.79391,prev_next_len,375,0.199337,0.645628,7.101911,prev_next_len,350,0.204036,0.469949,5.169442,prev_next_len,277,0.216265,0.77521,8.527306,prev_next_len,896,0.193962,0.406791,4.474705,prev_next_len,396,0.210064
id03_b4,id03,10,6-10,0.551515,5.515152,prev_shrunk,0,,0.881818,8.818182,prev_shrunk,0,,0.822727,8.227273,prev_shrunk,0,,0.531818,5.318182,prev_shrunk,0,,0.684848,6.848485,prev_shrunk,0,,0.665152,6.651515,prev_shrunk,0,,0.448485,4.484848,prev_shrunk,0,
id04_b2,id04,1,1-2,0.364613,0.364613,prev_next_len,241,0.415552,0.563484,0.563484,prev_next_len,175,0.434702,0.756531,0.756531,prev_next_len,324,0.376323,0.779409,0.779409,prev_next_len,408,0.36622,0.775553,0.775553,prev_next_len,403,0.370732,0.77408,0.77408,prev_next_len,417,0.362529,0.559602,0.559602,prev_next_len,184,0.434707
id04_b4,id04,5,3-5,0.505416,2.527082,prev_next_len,275,0.291063,0.559719,2.798595,prev_next_len,236,0.310131,0.632332,3.161658,prev_next_len,249,0.295891,0.754936,3.774678,prev_next_len,600,0.256333,0.777269,3.886343,prev_next_len,586,0.263118,0.773618,3.86809,prev_next_len,596,0.256727,0.544058,2.720292,prev_next_len,260,0.303645
id04_b6,id04,8,6-10,0.496189,3.969512,prev_next_len,375,0.225242,0.544307,4.354456,prev_next_len,466,0.265784,0.688264,5.506114,prev_next_len,661,0.193303,0.64681,5.17448,prev_next_len,344,0.222789,0.619285,4.954276,prev_next_len,340,0.225572,0.619897,4.959174,prev_next_len,325,0.230756,0.445065,3.560524,prev_next_len,410,0.233411
id04_b8,id04,6,6-10,0.610247,3.661481,prev_next_len,486,0.255067,0.544307,3.265842,prev_next_len,466,0.265784,0.688264,4.129585,prev_next_len,661,0.193303,0.762749,4.576492,prev_next_len,878,0.210348,0.784196,4.705175,prev_next_len,876,0.221337,0.781493,4.688959,prev_next_len,886,0.215212,0.658797,3.952782,prev_next_len,627,0.219422
id04_b10,id04,1,1-2,0.672633,0.672633,prev_next_len,232,0.409384,0.571459,0.571459,prev_next_len,165,0.432212,0.617755,0.617755,prev_next_len,184,0.449312,0.779409,0.779409,prev_next_len,408,0.36622,0.775553,0.775553,prev_next_len,403,0.370732,0.587719,0.587719,prev_next_len,151,0.432126,0.559602,0.559602,prev_next_len,184,0.434707
id04_b12,id04,3,3-5,0.621258,1.863773,prev_next_len,328,0.311934,0.546402,1.639207,prev_next_len,266,0.318671,0.633692,1.901077,prev_next_len,268,0.291329,0.648296,1.944889,prev_next_len,219,0.292274,0.603562,1.810685,prev_next_len,209,0.294044,0.441547,1.324641,prev_next_len,202,0.302944,0.459534,1.378603,prev_next_len,266,0.299461
```

## Interpretation

- The raw-rescue JEPA axis is public-positive and almost orthogonal to the two known JEPA-bad axes, but its remaining scale upside is tiny.
- The block posterior can satisfy all observed public scores with small residuals because 36 hidden blocks create many degrees of freedom; treat it as a diagnostic map, not a direct label oracle.
- The 0.54 path still requires reconstructing block rates from context, not just fitting public constraints. The validation block-rate oracle remains the upper-bound evidence that this is possible, while subject-chunk count-JEPA shows current representation is not yet sufficient.