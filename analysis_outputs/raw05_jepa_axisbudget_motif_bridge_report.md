# Raw05 JEPA Axis-Budget Motif Bridge

Bridges high-actual public6 Q3/S4 target moves with raw-axis-negative motif/cellgate counter moves on top of raw05-compatible A-family bases. This is a nonlocal JEPA residual test: keep the context/public axes stable while importing a target-block motif direction.

## Counts

- generated candidates: `106920`
- actual-anchor scored candidates: `3100`
- saved shortlist: `29`

## Profile Summary

```csv
profile,n,best_actual,best_selection,best_raw_abs,best_bad_abs
risk_q3_counter_noq2,10,0.5778286793,0.577886131,5.13e-07,0.0002015296
risk_q3s4_counter_q3s4,2400,0.5778104224,0.577888661,1.1831e-06,0.0002396653
risk_q3s4_counter_noq2,690,0.5778311037,0.577892563,9.838e-07,0.0003263268
```

## Shortlist

```csv
file,bucket,base_file,risk_file,counter_file,profile,risk_weight,counter_weight,max_step,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_base,mean_abs_move_vs_raw05,selection_score,rank_score
submission_raw05_jepa_axisbridge_7217d193.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778312161,0.5769750255,-1.0063e-06,-0.0003815271,0.0003355863,0.0014968722,0.5778988326,873.26
submission_raw05_jepa_axisbridge_1968b38c.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_siggate_prob_ones_g200_84da82f9.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778286793,0.5769766023,-5.13e-07,-0.0002015296,0.0003822902,0.0015075386,0.577886131,881.38
submission_raw05_jepa_axisbridge_35fe4935.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_efmicro5_prob_ones_g200_cf7fc70b.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778287025,0.5769766221,-5.156e-07,-0.0002064711,0.0003821152,0.0015073513,0.5778861691,882.96
submission_raw05_jepa_axisbridge_c99ee489.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_compatband_prob_ones_g200_f0ba88c5.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778287058,0.5769766279,-5.159e-07,-0.0002077219,0.0003821037,0.0015073372,0.5778861767,884.18
submission_raw05_jepa_axisbridge_74a95f7b.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_siggate_direct_logit_ones_g200_44230df6.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778288917,0.576976446,-5.693e-07,-0.0002247227,0.0003811428,0.0015064676,0.5778862263,884.22
submission_raw05_jepa_axisbridge_5a189d26.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_efmicro3_prob_ones_g200_85ee9d99.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.577828706,0.5769766288,-5.159e-07,-0.0002079345,0.0003821096,0.0015073433,0.5778861776,884.74
submission_raw05_jepa_axisbridge_970e949f.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_ones_g200_63dfdcc2.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778287094,0.5769766342,-5.156e-07,-0.0002107979,0.0003821459,0.0015073708,0.5778861851,885.26
submission_raw05_jepa_axisbridge_5bce22bc.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_efmicro5_direct_logit_ones_g200_2e75e659.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778289145,0.5769764657,-5.718e-07,-0.0002296104,0.0003809716,0.0015062835,0.5778862638,885.4
submission_raw05_jepa_axisbridge_8c9a99c0.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_compatband_direct_logit_ones_g200_e91f5b92.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778289178,0.5769764715,-5.721e-07,-0.0002308508,0.0003809599,0.0015062692,0.5778862714,886.84
submission_raw05_jepa_axisbridge_9e61b879.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_efmicro3_direct_logit_ones_g200_02184371.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.577828918,0.5769764724,-5.721e-07,-0.0002310625,0.0003809656,0.001506275,0.5778862723,887.4
submission_raw05_jepa_axisbridge_18aad556.csv,axisbridge_rawnegative,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_energyfront_direct_logit_ones_g200_5cc36abe.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3_counter_noq2,0.4,0.22,0.1,0.5778289214,0.5769764777,-5.718e-07,-0.0002339164,0.0003810014,0.001506302,0.5778862797,887.96
submission_raw05_jepa_axisbridge_4bb109a4.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_siggate_direct_logit_strength_g250_fcf695f2.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.577831402,0.5769752045,-1.0654e-06,-0.0003836441,0.0003340234,0.0014954141,0.5779024033,917.74
submission_raw05_jepa_axisbridge_45f2ba5a.csv,axisbridge_rank_fallback,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_efmicro5_direct_logit_strength_g250_7c08c955.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.577831418,0.5769752261,-1.0671e-06,-0.0003870447,0.0003338959,0.0014952596,0.5779025306,923.04
submission_raw05_jepa_axisbridge_2574f23d.csv,axisbridge_rank_fallback,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_efmicro3_direct_logit_strength_g250_71db204e.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778314197,0.5769752332,-1.0672e-06,-0.0003881364,0.0003339067,0.0014952614,0.5779025425,924.58
submission_raw05_jepa_axisbridge_2f6bc887.csv,axisbridge_rank_fallback,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_compatband_direct_logit_strength_g250_7d05552f.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778314197,0.5769752325,-1.0673e-06,-0.0003879614,0.0003338995,0.0014952546,0.5779025442,924.86
submission_raw05_jepa_axisbridge_e34b4795.csv,axisbridge_rank_fallback,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_energyfront_direct_logit_strength_g250_15b4481d.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.577831421,0.5769752333,-1.0669e-06,-0.0003904718,0.0003339465,0.0014952943,0.5779025265,926.6
submission_raw05_jepa_axisbridge_c466e24b.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_siggate_prob_ones_g200_84da82f9.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778316341,0.5769751682,-1.0568e-06,-0.0003263268,0.0003468395,0.0015055042,0.5779021358,950.54
submission_raw05_jepa_axisbridge_8d16268c.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_efmicro5_prob_ones_g200_cf7fc70b.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778316511,0.5769751971,-1.0588e-06,-0.0003298007,0.0003466627,0.0015053031,0.5779022835,956.44
submission_raw05_jepa_axisbridge_ce987933.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_compatband_prob_ones_g200_f0ba88c5.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778316535,0.5769752068,-1.059e-06,-0.000330729,0.0003466565,0.0015052897,0.5779023062,959.5
submission_raw05_jepa_axisbridge_fba45696.csv,axisbridge_rank_fallback,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_c9ae6feb.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.577831343,0.5769766444,-1.0372e-06,-0.0004726568,0.0003461515,0.0015012213,0.5779018699,959.56
submission_raw05_jepa_axisbridge_a63fbaf3.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_efmicro3_prob_ones_g200_85ee9d99.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778316536,0.5769752083,-1.059e-06,-0.0003309039,0.0003466648,0.0015052974,0.5779023056,959.84
submission_raw05_jepa_axisbridge_2d1e56a5.csv,axisbridge_lowbad,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_ones_g200_63dfdcc2.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778316549,0.5769752146,-1.0588e-06,-0.0003332384,0.0003467142,0.0015053318,0.5779022978,962.04
submission_raw05_jepa_axisbridge_f411b287.csv,axisbridge_rank_fallback,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778313136,0.5769720329,-9.838e-07,-0.0006602613,0.0003357331,0.0015079877,0.5778954488,962.66
submission_raw05_jepa_axisbridge_15d0f6ab.csv,axisbridge_rank_fallback,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_7c6e234e.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778313766,0.5769761503,-1.0443e-06,-0.0004808897,0.0003465853,0.0015019524,0.5779019257,965.02
submission_raw05_jepa_axisbridge_9d6e707c.csv,axisbridge_rank_fallback,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778313221,0.5769721057,-9.842e-07,-0.0006771434,0.0003357308,0.0015073714,0.5778955297,980.46
submission_raw05_jepa_axisbridge_04a3de62.csv,axisbridge_rank_fallback,submission_raw05_jepa_efmicro_1859bae9.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778313126,0.5769748827,-9.999e-07,-0.0006486247,0.0003352829,0.0015051387,0.5778984702,980.88
submission_raw05_jepa_axisbridge_0edfd32b.csv,axisbridge_rank_fallback,submission_raw05_jepa_efmicro_9e631d75.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778313486,0.5769720461,-9.855e-07,-0.0006739058,0.0003357052,0.0015067208,0.5778955862,981.16
submission_raw05_jepa_axisbridge_705367e9.csv,axisbridge_rank_fallback,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_95520dcf.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778312456,0.5769744941,-9.941e-07,-0.0006686114,0.000335446,0.0014989356,0.5778977922,987.68
submission_raw05_jepa_axisbridge_3840c870.csv,axisbridge_lowbad,submission_raw05_jepa_efback_cc265f32.csv,submission_raw05_jepa_public6q3s4corr_energyfront_prob_strength_g250_281bdb4c.csv,submission_hiddenblock_seqmotif_cellgate_05a9b3b9.csv,risk_q3s4_counter_noq2,0.22,0.22,0.1,0.5778315799,0.5769767301,-1.0401e-06,-0.0004491279,0.0003463923,0.0015043888,0.5779023345,994.76
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_axisbridge_7217d193.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_1968b38c.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_35fe4935.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_c99ee489.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_74a95f7b.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_5a189d26.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_970e949f.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_5bce22bc.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_8c9a99c0.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_9e61b879.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_18aad556.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_4bb109a4.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_45f2ba5a.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_2574f23d.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_2f6bc887.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_e34b4795.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_c466e24b.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_8d16268c.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_ce987933.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_fba45696.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_a63fbaf3.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_2d1e56a5.csv,250,True,0,0,0.0629859692,0.9798522348
submission_raw05_jepa_axisbridge_f411b287.csv,250,True,0,0,0.0629834018,0.979847259
submission_raw05_jepa_axisbridge_15d0f6ab.csv,250,True,0,0,0.0629795082,0.9798428788
submission_raw05_jepa_axisbridge_9d6e707c.csv,250,True,0,0,0.062983437,0.9798472596
submission_raw05_jepa_axisbridge_04a3de62.csv,250,True,0,0,0.0629837221,0.9798525034
submission_raw05_jepa_axisbridge_0edfd32b.csv,250,True,0,0,0.0629830887,0.9798472484
submission_raw05_jepa_axisbridge_705367e9.csv,250,True,0,0,0.0629889267,0.979852481
submission_raw05_jepa_axisbridge_3840c870.csv,250,True,0,0,0.0629795082,0.9798428788
```