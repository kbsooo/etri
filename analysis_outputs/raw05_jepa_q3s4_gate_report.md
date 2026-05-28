# Raw05 JEPA Q3/S4 Gate Audit

Goal: connect the public-winning raw05 axis to JEPA-style context-to-target latent prediction residuals, then project the resulting Q3/S4 gate onto hidden/test blocks.

## Raw05 reconstruction

```csv
subfit_disk_max_abs,subfit_disk_mean_abs
0.0,0.0
```

## Target-level raw05 OOF effect

```csv
target,stage2_loss,raw05_loss,raw05_delta_vs_stage2,raw05_win_rate,raw05_gain_mean,raw05_gain_p90,raw05_loss_hurt_p90
Q1,0.5746308241,0.5729444376,-0.0016863865,0.56,0.0016863865,0.0376094212,0.0390761308
Q2,0.6429986926,0.6429986926,0.0,0.0,0.0,0.0,0.0
Q3,0.630348489,0.6272561407,-0.0030923483,0.5688888889,0.0030923483,0.0460613462,0.0430028981
S1,0.4789432759,0.4775978673,-0.0013454086,0.5822222222,0.0013454086,0.0355057719,0.0293366171
S2,0.5389534496,0.5365495865,-0.0024038631,0.5511111111,0.0024038631,0.0405163873,0.036939406
S3,0.5034376795,0.500933991,-0.0025036885,0.5822222222,0.0025036885,0.0449200416,0.0444507347
S4,0.6034040622,0.6009818086,-0.0024222536,0.5355555556,0.0024222536,0.040258803,0.035323422
```

## Gate model summary

```csv
target,raw_gain_mean,raw_win_rate,reg_oof_corr_gain,prob_oof_win_auc_proxy,blend_oof_top30_gain,blend_oof_bottom30_gain
Q3,0.0030923483,0.5688888889,-0.0942469832,-0.0206486016,0.0007896172,0.0104835421
S4,0.0024222536,0.5355555556,0.1228148277,0.0188417054,0.0053030396,0.0009795932
```

## Best OOF gate variants

```csv
target_set,gate_kind,scale,mean_loss,delta_vs_stage2,q3_delta,s4_delta,moved_cell_frac,mean_gate
Q3S4,all,1.25,0.5666011366,-0.0009297881,-0.0036619276,-0.002846589,1.0,1.0
Q3S4,all,1.0,0.5667431244,-0.0007878003,-0.0030923483,-0.0024222536,1.0,1.0
Q3S4,all,0.75,0.5669070996,-0.0006238251,-0.0024414258,-0.0019253498,1.0,1.0
Q3S4,prob,1.25,0.5669726819,-0.0005582428,-0.0016658745,-0.0022418252,1.0,0.5262342669
Q3,all,1.25,0.5670077922,-0.0005231325,-0.0036619276,0.0,1.0,1.0
Q3S4,blend,1.25,0.5670531253,-0.0004777993,-0.0011426529,-0.0022019425,1.0,0.5106579103
Q3S4,prob,1.0,0.5670704706,-0.0004604541,-0.0013832302,-0.0018399482,1.0,0.5262342669
Q3,all,1.0,0.5670891606,-0.000441764,-0.0030923483,0.0,1.0,1.0
Q3S4,all,0.5,0.5670930649,-0.0004378598,-0.0017090802,-0.0013559385,1.0,1.0
Q3S4,reg_rank,1.25,0.5671100343,-0.0004208904,-0.0007884974,-0.0021577353,1.0,0.5011111111
S4,all,1.25,0.5671242691,-0.0004066556,-0.0,-0.002846589,1.0,1.0
Q3S4,blend,1.0,0.5671313703,-0.0003995544,-0.0009786773,-0.0018182034,1.0,0.5106579103
Q3S4,reg_rank,1.0,0.5671735608,-0.0003573639,-0.0007093071,-0.0017922402,1.0,0.5011111111
Q3S4,prob,0.75,0.5671751938,-0.0003557309,-0.0010753144,-0.001414802,1.0,0.5262342669
Q3,all,0.75,0.5671821496,-0.0003487751,-0.0024414258,0.0,1.0,1.0
S4,all,1.0,0.5671848885,-0.0003460362,-0.0,-0.0024222536,1.0,1.0
S4,prob,1.25,0.567210664,-0.0003202607,-0.0,-0.0022418252,1.0,0.5092808164
Q3S4,all,0.35,0.5672151965,-0.0003157282,-0.0012305716,-0.0009795259,1.0,1.0
S4,blend,1.25,0.5672163615,-0.0003145632,-0.0,-0.0022019425,1.0,0.5042155991
Q3S4,blend,0.75,0.567218288,-0.0003126367,-0.000782373,-0.0014060838,1.0,0.5106579103
S4,reg_rank,1.25,0.5672226768,-0.0003082479,-0.0,-0.0021577353,1.0,0.5011111111
Q3S4,hard50,1.25,0.5672430172,-0.0002879075,-0.0001638291,-0.0018515236,0.5,0.5
Q3S4,reg_rank,0.75,0.567247435,-0.0002834897,-0.0005907861,-0.0013936417,1.0,0.5011111111
S4,hard80,1.25,0.5672536751,-0.0002772496,-0.0,-0.001940747,0.2,0.2
S4,all,0.75,0.5672558747,-0.00027505,-0.0,-0.0019253498,1.0,1.0
Q3S4,hard80,1.25,0.5672607553,-0.0002701694,4.95611e-05,-0.001940747,0.2,0.2
S4,hard50,1.25,0.5672664213,-0.0002645034,-0.0,-0.0018515236,0.5,0.5
S4,prob,1.0,0.5672680749,-0.0002628497,-0.0,-0.0018399482,1.0,0.5092808164
S4,blend,1.0,0.5672711814,-0.0002597433,-0.0,-0.0018182034,1.0,0.5042155991
Q3S4,hard50,1.0,0.567272265,-0.0002586597,-0.0002331317,-0.001577486,0.5,0.5
```

## Top JEPA features

```csv
target,model,rank,feature,importance
Q3,regressor,1,rtday_both_err_13,0.041525724
Q3,regressor,2,rtday_next_err_13,0.0252729184
Q3,regressor,3,rtmod_m2w_pred_05,0.0173123412
Q3,regressor,4,rtday_next_pred_05,0.0153280003
Q3,regressor,5,rtday_prev_err_13,0.0133072581
Q3,regressor,6,rtday_target_13,0.0126682459
Q3,regressor,7,next_Q2,0.0123679274
Q3,regressor,8,rtday_both_pred_05,0.0078047719
Q3,regressor,9,next_Q3,0.0075174707
Q3,regressor,10,prev_Q2,0.0067216373
Q3,regressor,11,rtday_prev_pred_05,0.0066532016
Q3,regressor,12,rtwin_night_abserr_01,0.0065944971
Q3,regressor,13,rtwin_night_pred_02,0.0065285035
Q3,regressor,14,rtmod_m2w_pred_09,0.0064196777
Q3,regressor,15,rtday_both_err_15,0.0064094282
Q3,regressor,16,rtmod_mobile_target_07,0.0063816182
Q3,regressor,17,prev_Q3,0.0060825088
Q3,regressor,18,rtmod_m2w_abserr_08,0.0058981542
Q3,regressor,19,rtday_prev_pred_10,0.0058414675
Q3,regressor,20,prev_Q1,0.0058231522
Q3,regressor,21,rtmod_w2m_abserr_09,0.0053445699
Q3,regressor,22,rtmod_mobile_target_10,0.0053100801
Q3,regressor,23,rtmod_m2w_pred_04,0.0051571279
Q3,regressor,24,next_S4,0.0051014978
Q3,regressor,25,rtmod_w2m_err_09,0.0050819741
Q3,regressor,26,rtwin_night_abserr_03,0.0050589787
Q3,regressor,27,rtday_prev_err_15,0.0050532483
Q3,regressor,28,rtmod_w2m_err_07,0.0048218542
Q3,regressor,29,rtday_target_10,0.0047016339
Q3,regressor,30,rtmod_m2w_err_05,0.0047015438
Q3,regressor,31,rtday_next_pred_10,0.0045687581
Q3,regressor,32,rtday_both_abserr_07,0.0045277544
Q3,regressor,33,rtday_both_pred_06,0.0045113282
Q3,regressor,34,rtmod_wear_target_05,0.0044934553
Q3,regressor,35,rtday_next_abserr_09,0.0044785561
Q3,regressor,36,rtday_both_pred_10,0.0044777436
Q3,regressor,37,subject_pos_all,0.0044502525
Q3,regressor,38,rtday_prev_pred_14,0.0043733874
Q3,regressor,39,rtday_target_05,0.0043663131
Q3,regressor,40,rtwin_night_abserr_02,0.0041865674
```

## Top candidate scores

```csv
file,base_source,target_set,gate_kind,scale,filter,delta_vs_raw05_rawaxis,raw_axis_expected_public_vs_stage2,posterior_expected_public_vs_anchor,focused_scenario_score,mean_abs_move_vs_base
submission_raw05_jepa_q3s4gate_66b886a1.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.35,posterior_agree,-9.0517e-06,0.5775172555,0.5773067148,0.5827541987,0.0006189431
submission_raw05_jepa_q3s4gate_0df5a5a9.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.35,rawq_post_agree,-8.6393e-06,0.5775176679,0.5772879207,0.5827404311,0.0005747382
submission_raw05_jepa_q3s4gate_4a2a54de.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.35,plain,-8.385e-06,0.5775179222,0.5774386268,0.582862984,0.0009213356
submission_raw05_jepa_q3s4gate_df7dc3ee.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.35,rawq_good,-8.385e-06,0.5775179222,0.5774386268,0.582862984,0.0009213356
submission_raw05_jepa_q3s4gate_bd0f6740.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.35,rawq_strong,-8.3447e-06,0.5775179625,0.5774367921,0.5828219546,0.0006444924
submission_raw05_jepa_q3s4gate_e5019a0e.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,prob,0.75,posterior_agree,-6.8898e-06,0.5775194174,0.5772767207,0.5828066868,0.0007244939
submission_raw05_jepa_q3s4gate_b50bfd6a.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,prob,0.75,rawq_post_agree,-6.4348e-06,0.5775198724,0.5772550246,0.58279028,0.0006737411
submission_raw05_jepa_q3s4gate_841bb327.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,prob,0.75,rawq_strong,-5.484e-06,0.5775208232,0.5774275857,0.5828875382,0.0007589391
submission_raw05_jepa_q3s4gate_c135e8ca.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,prob,0.75,plain,-5.2984e-06,0.5775210088,0.5774296783,0.5829381897,0.0010715369
submission_raw05_jepa_q3s4gate_468a0fe0.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,prob,0.75,rawq_good,-5.2984e-06,0.5775210088,0.5774296783,0.5829381897,0.0010715369
submission_raw05_jepa_q3s4gate_16135ae7.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,all,0.35,plain,-5.2398e-06,0.5775210674,0.5768730652,0.5828137373,0.0009204705
submission_raw05_jepa_q3s4gate_5a60b57a.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,all,0.35,rawq_good,-5.2398e-06,0.5775210674,0.5768730652,0.5828137373,0.0009204705
submission_raw05_jepa_q3s4gate_fd65e5bc.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,all,0.35,rawq_strong,-4.8289e-06,0.5775214783,0.5768716012,0.5827736819,0.0006440582
submission_raw05_jepa_q3s4gate_39220660.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.5,posterior_agree,-4.6359e-06,0.5775216713,0.5772369282,0.5828750181,0.0008836806
submission_raw05_jepa_q3s4gate_44002f4d.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,all,0.35,plain,-4.2681e-06,0.5775220391,0.5771311907,0.5826608767,0.000921539
submission_raw05_jepa_q3s4gate_1d2b5cab.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,all,0.35,rawq_good,-4.2681e-06,0.5775220391,0.5771311907,0.5826608767,0.000921539
submission_raw05_jepa_q3s4gate_06776b39.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.5,rawq_post_agree,-4.1263e-06,0.5775221809,0.5772099998,0.5828551906,0.0008205231
submission_raw05_jepa_q3s4gate_ff947b09.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,all,0.35,rawq_strong,-3.9705e-06,0.5775223367,0.5771296134,0.5826206735,0.0006446761
submission_raw05_jepa_q3s4gate_e6346549.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,all,0.35,posterior_agree,-3.8786e-06,0.5775224286,0.5770003351,0.5825559558,0.0006191969
submission_raw05_jepa_q3s4gate_f8f0bd26.csv,submission_hiddenblock_rateprobe_neutral_605de284.csv,Q3S4,all,0.35,plain,-3.8287e-06,0.5775224785,0.5767948592,0.5827731958,0.0009206351
submission_raw05_jepa_q3s4gate_698369bb.csv,submission_hiddenblock_rateprobe_neutral_605de284.csv,Q3S4,all,0.35,rawq_good,-3.8287e-06,0.5775224785,0.5767948592,0.5827731958,0.0009206351
submission_raw05_jepa_q3s4gate_d733cd03.csv,submission_hiddenblock_seqmotif_neutral_ebf79910.csv,Q3S4,all,0.35,plain,-3.7138e-06,0.5775225934,0.5771825457,0.5826381955,0.0009217242
submission_raw05_jepa_q3s4gate_fd128985.csv,submission_hiddenblock_seqmotif_neutral_ebf79910.csv,Q3S4,all,0.35,rawq_good,-3.7138e-06,0.5775225934,0.5771825457,0.5826381955,0.0009217242
submission_raw05_jepa_q3s4gate_676c0f93.csv,submission_hiddenblock_rateprobe_neutral_605de284.csv,Q3S4,all,0.35,rawq_strong,-3.3685e-06,0.5775229387,0.5767934445,0.5827335474,0.0006441676
submission_raw05_jepa_q3s4gate_81f94b63.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,all,0.35,rawq_post_agree,-3.3118e-06,0.5775229954,0.5769816952,0.5825428924,0.0005750003
submission_raw05_jepa_q3s4gate_b0e2114f.csv,submission_hiddenblock_seqmotif_neutral_d0ca7647.csv,Q3S4,all,0.35,plain,-3.2734e-06,0.5775230338,0.5767626717,0.5827538145,0.0009206796
submission_raw05_jepa_q3s4gate_9ee24851.csv,submission_hiddenblock_seqmotif_neutral_d0ca7647.csv,Q3S4,all,0.35,rawq_good,-3.2734e-06,0.5775230338,0.5767626717,0.5827538145,0.0009206796
submission_raw05_jepa_q3s4gate_68ead30b.csv,submission_hiddenblock_seqmotif_neutral_ebf79910.csv,Q3S4,all,0.35,rawq_strong,-3.248e-06,0.5775230592,0.5771811366,0.5825990583,0.0006448611
submission_raw05_jepa_q3s4gate_49a1b99d.csv,submission_hiddenblock_seqmotif_neutral_ebf79910.csv,Q3S4,all,0.35,posterior_agree,-3.1086e-06,0.5775231986,0.5770519057,0.5825344777,0.0006193236
submission_raw05_jepa_q3s4gate_8bbbf297.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,all,0.35,posterior_agree,-3.0901e-06,0.5775232171,0.5767439698,0.5827161041,0.0006185062
submission_raw05_jepa_q3s4gate_597d374d.csv,submission_hiddenblock_seqmotif_neutral_d0ca7647.csv,Q3S4,all,0.35,rawq_strong,-2.8094e-06,0.5775234978,0.5767612608,0.582714073,0.000644192
submission_raw05_jepa_q3s4gate_2837eb12.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,prob,0.75,plain,-2.7185e-06,0.5775235887,0.5768635515,0.582885094,0.001070682
submission_raw05_jepa_q3s4gate_5976cae8.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,prob,0.75,rawq_good,-2.7185e-06,0.5775235887,0.5768635515,0.582885094,0.001070682
submission_raw05_jepa_q3s4gate_16d75651.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,prob,0.75,rawq_strong,-2.519e-06,0.5775237882,0.576861844,0.582836338,0.0007585403
submission_raw05_jepa_q3s4gate_58801138.csv,submission_hiddenblock_seqmotif_neutral_ebf79910.csv,Q3S4,all,0.35,rawq_post_agree,-2.5102e-06,0.577523797,0.5770332976,0.5825216526,0.0005751186
submission_raw05_jepa_q3s4gate_6362a15c.csv,submission_hiddenblock_paretomix_w0.4_507296eb.csv,Q3S4,all,0.35,rawq_post_agree,-2.2663e-06,0.5775240409,0.5767255869,0.5827040764,0.000574366
submission_raw05_jepa_q3s4gate_20d86262.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,prob,0.75,posterior_agree,-2.0692e-06,0.577524238,0.5769699884,0.5826070216,0.0007248216
submission_raw05_jepa_q3s4gate_d23d41bd.csv,submission_hiddenblock_rawaxis_stage2_raw10_s0p75_0cf1aeac.csv,Q3S4,all,0.5,rawq_strong,-1.9427e-06,0.5775243645,0.5774244361,0.5829808674,0.0009204485
submission_raw05_jepa_q3s4gate_f330f08d.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,prob,0.75,plain,-1.7145e-06,0.5775245927,0.5771217093,0.5827333645,0.0010718267
submission_raw05_jepa_q3s4gate_951b71c4.csv,submission_hiddenblock_seqmotif_neutral_1501e8f9.csv,Q3S4,prob,0.75,rawq_good,-1.7145e-06,0.5775245927,0.5771217093,0.5827333645,0.0010718267
```