# E346 Counter-Axis Public-Analog Audit

## Question

Do the E344/E345 hidden lifestyle-state counter-axis candidates avoid the anatomy of already observed public-loss submissions?

## Observed Public Axes

| file | exists | public_lb | public_delta_vs_e247 | loss_tier | changed_rows | share_Q1 | share_Q2 | share_Q3 | share_S1 | share_S2 | share_S3 | share_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | True | 0.578427353 | 0.002268403 | severe | 250.000000000 | 0.189352104 | 0.082406474 | 0.147293967 | 0.101438663 | 0.147498085 | 0.171689234 | 0.160321473 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | True | 0.578303365 | 0.002144416 | severe | 250.000000000 | 0.181065224 | 0.029429392 | 0.225774193 | 0.112329030 | 0.125443583 | 0.172948587 | 0.153009991 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | True | 0.577944976 | 0.001786026 | severe | 250.000000000 | 0.162982041 | 0.057989246 | 0.188673357 | 0.129639621 | 0.133689709 | 0.181803372 | 0.145222654 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | True | 0.577286509 | 0.001127559 | severe | 250.000000000 | 0.000000000 | 0.000000000 | 0.183827960 | 0.000000000 | 0.645901969 | 0.000000000 | 0.170270072 |
| submission_e323_5508f966_uploadsafe.csv | True | 0.577035502 | 0.000876552 | severe | 250.000000000 | 0.258564395 | 0.000000001 | 0.000000001 | 0.263324602 | 0.000000001 | 0.478110999 | 0.000000001 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | True | 0.576407777 | 0.000248828 | mild | 250.000000000 | 0.090237172 | 0.033702584 | 0.267518013 | 0.134013217 | 0.178155973 | 0.044198883 | 0.252174159 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | True | 0.576329497 | 0.000170548 | mild | 54.000000000 | 0.000000000 | 0.000000000 | 0.855411481 | 0.000000000 | 0.000000000 | 0.000000000 | 0.144588519 |
| submission_e176_abl_q2_to0p75_91e49725.csv | True | 0.576311831 | 0.000152882 | mild | 249.000000000 | 0.057548942 | 0.014198792 | 0.445405471 | 0.013942978 | 0.035641892 | 0.043575358 | 0.389686566 |
| submission_mixmin_0c916bb4.csv | True | 0.576306641 | 0.000147691 | mild | 250.000000000 | 0.032752265 | 0.005500390 | 0.292265669 | 0.154626257 | 0.155588112 | 0.101594446 | 0.257672863 |
| submission_e101_q2s3tail_177569bc.csv | True | 0.576300366 | 0.000141417 | mild | 243.000000000 | 0.050834478 | 0.002134276 | 0.453622763 | 0.000000000 | 0.029219698 | 0.064257186 | 0.399931599 |
| submission_e95_hardtail_541e3973.csv | True | 0.576291330 | 0.000132380 | mild | 242.000000000 | 0.052580068 | 0.000000000 | 0.469199580 | 0.000000000 | 0.030223065 | 0.034332557 | 0.413664730 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | True | 0.576280568 | 0.000121618 | mild | 17.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_jepa_latent_residual_probe.csv | False | 0.581227328 | 0.005068378 |  |  |  |  |  |  |  |  |  |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | False | 0.580246819 | 0.004087870 |  |  |  |  |  |  |  |  |  |
| submission_jepa_latent_q2_w0p45.csv | False | 0.579801286 | 0.003642337 |  |  |  |  |  |  |  |  |  |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | False | 0.577526307 | 0.001367358 |  |  |  |  |  |  |  |  |  |

## Candidate Public-Analog Scores

| role | family | basename | public_analog_survival_score | public_analog_risk_score | public_loss_weighted_pos_cos | severe_loss_weighted_pos_cos | max_severe_pos_cos | poscos_e323 | poscos_e216 | poscos_e267 | poscos_e256 | move_l1 | changed_rows | share_Q1 | share_Q2 | share_Q3 | share_S1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e344_nullsafe_top5 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_e131968c.csv | 0.528061224 | 0.044818570 | 0.006914995 | 0.007855233 | 0.030048342 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.638905726 | 250 | 0.480761563 | 0.220899617 | 0.049210308 | 0.241199739 |
| e344_nullsafe_top3 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_bdadf4e2.csv | 0.488520408 | 0.044910027 | 0.006929106 | 0.007871262 | 0.030109659 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.581587126 | 108 | 0.485873691 | 0.223663214 | 0.049825960 | 0.240637135 |
| e344_nullsafe_top6 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_9fdf1eb9.csv | 0.482142857 | 0.044817254 | 0.006914792 | 0.007855002 | 0.030047460 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.645835726 | 250 | 0.480044431 | 0.222061769 | 0.049136903 | 0.240839951 |
| e344_nullsafe_top2 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_8de06933.csv | 0.480867347 | 0.051130788 | 0.007888898 | 0.008961559 | 0.034280331 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.548931069 | 107 | 0.489361701 | 0.225268856 | 0.043004811 | 0.242364631 |
| e345_nullsafe_top6 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_45_q1s1_counter_20f213b3.csv | 0.479591837 | 0.050838349 | 0.007843778 | 0.008910304 | 0.034084267 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.669741172 | 107 | 0.478263854 | 0.222409008 | 0.041984181 | 0.257342957 |
| e345_nullsafe_top3 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_35_joint_cellveto_61d91c4c.csv | 0.478316327 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| e344_nullsafe_top4 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_1860f60a.csv | 0.474489796 | 0.044908712 | 0.006928903 | 0.007871032 | 0.030108777 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.588517126 | 108 | 0.485139880 | 0.224835709 | 0.049750709 | 0.240273703 |
| e345_nullsafe_top1 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_35_q1q2s1_counter_61d91c4c.csv | 0.466836735 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| E345_upload | e345 | submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv | 0.461734694 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| e345_nullsafe_top4 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_35_preserve_q2_cellve_61d91c4c.csv | 0.454081633 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| E344_upload | e344 | submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv | 0.452806122 | 0.051129078 | 0.007888634 | 0.008961259 | 0.034279185 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.555861069 | 107 | 0.488617325 | 0.226447314 | 0.042939396 | 0.241995966 |
| e345_nullsafe_top7 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_45_joint_cellveto_20f213b3.csv | 0.443877551 | 0.050838349 | 0.007843778 | 0.008910304 | 0.034084267 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.669741172 | 107 | 0.478263854 | 0.222409008 | 0.041984181 | 0.257342957 |
| e345_nullsafe_top8 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_45_preserve_q2_cellve_20f213b3.csv | 0.438775510 | 0.050838349 | 0.007843778 | 0.008910304 | 0.034084267 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.669741172 | 107 | 0.478263854 | 0.222409008 | 0.041984181 | 0.257342957 |
| e345_nullsafe_top5 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_45_q1q2s1_counter_20f213b3.csv | 0.438775510 | 0.050838349 | 0.007843778 | 0.008910304 | 0.034084267 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.669741172 | 107 | 0.478263854 | 0.222409008 | 0.041984181 | 0.257342957 |
| e345_nullsafe_top2 | e345 | submission_e345_counterrefine_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_105_v0_35_q1s1_counter_61d91c4c.csv | 0.433673469 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| e344_nullsafe_top1 | e344 | submission_e344_counteraxis_e342_submission_e342_signtransfer_q2_su__ctr_submission_e315null_submission_e31__w0_10_cellveto_9d09e4d2.csv | 0.426020408 | 0.051129078 | 0.007888634 | 0.008961259 | 0.034279185 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.555861069 | 107 | 0.488617325 | 0.226447314 | 0.042939396 | 0.241995966 |

## Upload Candidate Read

| role | family | basename | public_analog_survival_score | public_analog_risk_score | public_loss_weighted_pos_cos | severe_loss_weighted_pos_cos | max_severe_pos_cos | poscos_e323 | poscos_e216 | poscos_e267 | poscos_e256 | move_l1 | changed_rows | share_Q1 | share_Q2 | share_Q3 | share_S1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E345_upload | e345 | submission_e345_counterrefine_lifestyle_61d91c4c_uploadsafe.csv | 0.461734694 | 0.051144175 | 0.007890964 | 0.008963905 | 0.034289306 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.630661621 | 107 | 0.481512300 | 0.221442546 | 0.042292140 | 0.254753013 |
| E344_upload | e344 | submission_e344_counteraxis_lifestyle_9d09e4d2_uploadsafe.csv | 0.452806122 | 0.051129078 | 0.007888634 | 0.008961259 | 0.034279185 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 4.555861069 | 107 | 0.488617325 | 0.226447314 | 0.042939396 | 0.241995966 |

## Interpretation

- E344 public-analog risk score: `0.051129078`; survival score `0.452806122`.
- E345 public-analog risk score: `0.051144175`; survival score `0.461734694`.
- Lower public-analog risk among upload candidates: `E344`.
- Direct positive alignment to E323/E216/E267/E256 hard-veto axes: E344 `0.000000000`, E345 `0.000000000`.
- Certification-grade public-analog dominance: `False`.
- This audit is a veto/stress diagnostic, not a public LB predictor.
- The current upload candidates do not have a hard public-bad-axis veto: their positive alignment to E323/E216/E267/E256 is zero in this axis set.
- They are not certification-grade either: public-analog survival is near the middle of matched movement nulls, not above a strong `0.70` dominance threshold.
- Decision: keep E344 first because it has slightly lower public-analog risk and stronger p90; keep E345 as the bad-axis-margin backup. Do not create a new public candidate from E346 alone.

## Files

- `e346_public_analog_observed_axes.csv`
- `e346_counteraxis_public_analog_candidates.csv`
- `e346_counteraxis_public_analog_scores.csv`
- `e346_counteraxis_public_analog_nulls.csv`
