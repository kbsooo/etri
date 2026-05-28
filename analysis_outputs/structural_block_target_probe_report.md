# E59 Structural Block Target Representation Probe

Question: are hidden block targets better represented as a 128-state joint label-pattern distribution than as seven independent marginal rates?

Decision gates:

- pseudo-hidden pattern NLL improves over raw independent pattern baseline;
- pseudo-hidden row LogLoss also improves over raw marginal baseline;
- predicted joint pattern carries information beyond its own marginals;
- S3 does not regress versus subject mean;
- real hidden-block expected mixmin delta versus a2c8 is negative.

Joint gates opened: `0`.

Best by structural pattern stress:

| method | weighted_pattern_nll | delta_pattern_nll_vs_raw | weighted_joint_gain_vs_own_margins | delta_weighted_row_logloss_vs_raw | s3_delta_vs_subject | weighted_mixmin_delta_vs_a2c8 | joint_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| struct_raw_calendar_subject_fbsubject_k16_a12_w0.35 | 4.174287 | -0.062594 | -0.088340 | 0.003678 | 0.002727 | 0.000304 | 0.000000 |
| struct_raw_calendar_subject_fbsubject_k16_a24_w0.65 | 4.176099 | -0.060782 | -0.093380 | 0.004657 | 0.006245 | 0.000262 | 0.000000 |
| struct_raw_calendar_fbsubject_k16_a12_w0.35 | 4.176170 | -0.060711 | -0.089466 | 0.004108 | 0.003078 | 0.000370 | 0.000000 |
| struct_raw_calendar_fbsubject_k16_a24_w0.65 | 4.177175 | -0.059705 | -0.094274 | 0.004938 | 0.006670 | 0.000347 | 0.000000 |
| struct_raw_calendar_subject_fbsubject_k16_a4_w0.35 | 4.178479 | -0.058401 | -0.094492 | 0.005156 | 0.007623 | 0.000248 | 0.000000 |
| struct_raw_calendar_fbsubject_k16_a4_w0.35 | 4.179289 | -0.057591 | -0.095174 | 0.005369 | 0.008068 | 0.000340 | 0.000000 |
| struct_raw_calendar_subject_fbsubject_k16_a24_w0.35 | 4.182042 | -0.054838 | -0.079721 | 0.003554 | 0.000240 | 0.000347 | 0.000000 |
| struct_raw_calendar_fbsubject_k16_a24_w0.35 | 4.184715 | -0.052165 | -0.080428 | 0.004037 | 0.000497 | 0.000392 | 0.000000 |
| struct_raw_calendar_fbraw_k16_a12_w0.35 | 4.185050 | -0.051830 | -0.085790 | 0.004851 | 0.018852 | 0.000262 | 0.000000 |
| struct_raw_subject_fbsubject_k16_a12_w0.35 | 4.185052 | -0.051829 | -0.081129 | 0.004186 | 0.004036 | 0.000265 | 0.000000 |
| struct_raw_calendar_fbraw_k16_a24_w0.35 | 4.186236 | -0.050644 | -0.071307 | 0.002952 | 0.014994 | 0.000277 | 0.000000 |
| struct_raw_calendar_subject_fbraw_k16_a12_w0.35 | 4.186799 | -0.050082 | -0.084271 | 0.004884 | 0.018312 | 0.000197 | 0.000000 |

Best hidden mixmin alignment:

| method | weighted_mixmin_delta_vs_a2c8 | mean_mixmin_delta_vs_a2c8 | mixmin_better_block_rate |
| --- | --- | --- | --- |
| struct_raw_subject_fbraw_k8_a4_w1.00 | -0.000367 | -0.000683 | 0.527778 |
| struct_raw_subject_fbsubject_k8_a4_w1.00 | -0.000322 | -0.000610 | 0.527778 |
| struct_raw_subject_fbraw_k16_a4_w1.00 | -0.000303 | -0.000639 | 0.500000 |
| struct_raw_subject_fbsubject_k16_a4_w1.00 | -0.000276 | -0.000595 | 0.527778 |
| struct_raw_subject_fbraw_k4_a4_w1.00 | -0.000259 | -0.000505 | 0.527778 |
| struct_raw_calendar_subject_fbraw_k8_a4_w1.00 | -0.000218 | -0.000597 | 0.527778 |
| struct_raw_calendar_subject_fbraw_k4_a4_w1.00 | -0.000200 | -0.000468 | 0.555556 |
| struct_raw_subject_fbsubject_k4_a4_w1.00 | -0.000192 | -0.000395 | 0.527778 |
| calendar_count_indep | -0.000179 | -0.000434 | 0.527778 |
| struct_raw_calendar_subject_fbsubject_k8_a4_w1.00 | -0.000173 | -0.000524 | 0.527778 |
| struct_raw_calendar_subject_fbraw_k16_a4_w1.00 | -0.000144 | -0.000603 | 0.500000 |
| struct_raw_calendar_subject_fbsubject_k4_a4_w1.00 | -0.000133 | -0.000358 | 0.583333 |

Target stress for the best structural method:

| target | target_row_logloss | delta_row_vs_subject | delta_row_vs_raw |
| --- | --- | --- | --- |
| Q1 | 0.639215 | -0.009515 | 0.001205 |
| Q2 | 0.680030 | -0.013750 | 0.003492 |
| Q3 | 0.667883 | -0.001461 | 0.014845 |
| S1 | 0.572064 | -0.004976 | 0.004927 |
| S2 | 0.565789 | -0.001107 | 0.005768 |
| S3 | 0.505668 | 0.002727 | -0.005089 |
| S4 | 0.631977 | -0.000265 | 0.000597 |

Interpretation:

No structural joint-pattern method survived the full gate. If pattern NLL improves without row/mixmin survival, the joint structure is learnable but not the current public frontier latent.

Most informative rows:

- best structural method: `struct_raw_calendar_subject_fbsubject_k16_a12_w0.35`
- best hidden-sign method: `struct_raw_subject_fbraw_k8_a4_w1.00`

Next action:

Use this result to decide whether the next branch should translate joint-pattern structure into a submission, or abandon joint labels and seek an independent non-anchor validator for the E56 posterior.
