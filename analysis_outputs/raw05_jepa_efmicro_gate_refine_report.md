# Raw05 JEPA EFMicro Gate Refine

This pass refines the second-stage bad-axis row gate around the energyfront/micro frontier.
It varies bad-gate floor/scale and beta to test whether the low-bad micro structure can recover the actual-anchor frontier.

## Counts

- generated candidates: 59439
- actual-anchor rescored candidates: 2201
- saved candidates: 48

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,energy_delta_vs_base,blend_profile,beta,row_gate,gate_mean,gate_p10,base_file,donor_file
submission_raw05_jepa_efgate_ac60a2e6.csv,gate_actual,0.5778402624,0.5768889122,9.66e-08,0.0002444987,0.0014972167,-0.0222745,q1light,0.44,bad_f010_s075,0.448305313,0.101842713,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_e7d05c45.csv,gate_actual,0.5778402642,0.5768889476,9.67e-08,0.0002357429,0.0014969768,-0.0223929907,q1light,0.44,bad_f010_s075,0.447593507,0.101591043,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_8bd2def3.csv,gate_actual,0.5778402665,0.5768889836,9.67e-08,0.0002278604,0.0014967286,-0.0225333538,q1light,0.44,bad_f010_s075,0.4471416894,0.1014868316,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_b6e8ee31.csv,gate_actual,0.5778402736,0.5768924016,9.89e-08,6.28585e-05,0.0014935043,-0.022964278,q2s1heavy,0.44,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_b5fade58.csv,gate_actual,0.5778402771,0.5768924283,9.87e-08,5.68203e-05,0.0014932704,-0.0230916575,q2s1heavy,0.44,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_48c25ff7.csv,gate_actual,0.5778402797,0.5768890442,9.87e-08,0.0005315278,0.0014889685,-0.026267302,q2s1heavy,0.4,bad_f010_s075,0.4727433223,0.1050158098,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_fc53e556.csv,gate_actual,0.5778402869,0.576892569,9.63e-08,5.99876e-05,0.001493059,-0.0226620275,q2s1heavy,0.44,bad_hard_f010,0.4024,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_793e3f5d.csv,gate_actual,0.5778402891,0.5768888662,8.58e-08,0.000364676,0.0014964716,-0.0240364195,q1light,0.4,bad_f020_s100,0.5153821693,0.2076376726,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_d359abc4.csv,gate_actual,0.5778402904,0.5768925959,9.62e-08,5.39487e-05,0.0014928248,-0.0227872604,q2s1heavy,0.44,bad_hard_f010,0.4024,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_94a45c75.csv,gate_actual,0.5778402906,0.5768889024,8.59e-08,0.0003558775,0.0014962328,-0.0242022836,q1light,0.4,bad_f020_s100,0.5146224086,0.2068468017,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_eae9c6ac.csv,gate_actual,0.5778402927,0.5768889384,8.59e-08,0.0003480414,0.0014959865,-0.024389152,q1light,0.4,bad_f020_s100,0.5141501834,0.2065096289,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_754e2cb4.csv,gate_actual,0.5778403005,0.5768923462,9.97e-08,6.4211e-05,0.0014928937,-0.0252134638,q2s1heavy,0.44,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_c2d77911.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_b17b5030.csv,gate_actual,0.5778403052,0.5768923692,9.85e-08,6.2708e-05,0.0014926749,-0.023088271,q2s1heavy,0.44,bad_hard_f010,0.4024,0.1,submission_raw05_jepa_efmicro_61a4476f.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_5248c6f2.csv,gate_actual,0.5778403151,0.5768925441,9.47e-08,5.9941e-05,0.0014921652,-0.0227682277,q2s1heavy,0.44,bad_hard_f010,0.4024,0.1,submission_raw05_jepa_efmicro_61a4476f.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_d5532b5a.csv,gate_actual,0.577840318,0.5768925471,9.45e-08,6.14594e-05,0.0014922777,-0.022671393,q2s1heavy,0.44,bad_hard_f010,0.4024,0.1,submission_raw05_jepa_efmicro_c2d77911.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_71b69c58.csv,gate_raw_tight,0.5778403714,0.5768892859,7.89e-08,0.0003610843,0.0014953977,-0.0302813924,q1light,0.44,bad_f020_s100,0.5139090966,0.2054686859,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_83dc6d85.csv,gate_raw_tight,0.577840374,0.576889321,7.87e-08,0.0003544316,0.0014951507,-0.0305310981,q1light,0.44,bad_f020_s100,0.5137277859,0.2055006242,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_80b04d8b.csv,gate_raw_tight,0.5778403763,0.5768893566,7.85e-08,0.0003474292,0.0014949054,-0.0307826498,q1light,0.44,bad_f020_s100,0.5134650294,0.2054348636,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_a538d5c0.csv,gate_raw_tight,0.5778403788,0.576889257,7.84e-08,0.0003613927,0.0014951962,-0.030170467,q1light,0.44,bad_f020_s100,0.5136474073,0.2050789928,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_daa7eaaf.csv,gate_raw_tight,0.5778403813,0.5768893601,7.5e-08,0.000374642,0.0014891416,-0.034603919,q1light,0.46,bad_f020_s100,0.516327265,0.2078099782,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_8dff62c3.csv,gate_raw_tight,0.5778403814,0.576889292,7.82e-08,0.0003547743,0.001494949,-0.030419494,q1light,0.44,bad_f020_s100,0.5134745309,0.205123369,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_a1778739.csv,gate_raw_tight,0.5778403835,0.5768893879,7.5e-08,0.0003675491,0.0014889019,-0.0349553221,q1light,0.46,bad_f020_s100,0.5160522722,0.2076801492,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_6ec2b8a9.csv,gate_raw_tight,0.5778403839,0.5768893273,7.79e-08,0.0003480997,0.0014947013,-0.0306750562,q1light,0.44,bad_f020_s100,0.5132986271,0.2051674127,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_7f1625c6.csv,gate_raw_tight,0.5778403841,0.5768940227,7.55e-08,5.66509e-05,0.0014895665,-0.0206224792,context_only,0.44,bad_hard_f010,0.3988,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_718c6fcb.csv,gate_raw_tight,0.5778403855,0.5768894778,7.6e-08,0.0005979553,0.0014869755,-0.0251482014,q1light,0.44,bad_f010_s075,0.4608173453,0.1016755158,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_d592970e.csv,gate_raw_tight,0.5778403876,0.5768940501,7.53e-08,5.05423e-05,0.0014893232,-0.0207455582,context_only,0.44,bad_hard_f010,0.3988,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_4024a723.csv,gate_raw_tight,0.5778403908,0.5768892784,7.31e-08,0.0003623744,0.0014950253,-0.0295856977,q1light,0.44,bad_f020_s100,0.5125752435,0.2046199114,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_a297600b.csv,gate_actual,0.5778402883,0.5768923718,1.004e-07,6.41115e-05,0.0014929399,-0.0253994765,q2s1heavy,0.44,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_61a4476f.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_a199e1b3.csv,gate_raw_tight,0.5778403932,0.5768893139,7.3e-08,0.000355303,0.0014947814,-0.029823006,q1light,0.44,bad_f020_s100,0.5122707322,0.2045792158,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_62d53675.csv,gate_raw_tight,0.5778403932,0.5768939276,7.12e-08,6.32418e-05,0.0014890886,-0.0261742012,context_only,0.46,bad_f005_s075,0.4163965597,0.053353618,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
submission_raw05_jepa_efgate_10765d3c.csv,gate_raw_tight,0.5778403959,0.5768893491,7.27e-08,0.0003488761,0.0014945317,-0.0300777842,q1light,0.44,bad_f020_s100,0.512158706,0.2047409987,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_19afbed3.csv,gate_raw_tight,0.5778404024,0.57688949,6.57e-08,0.0007118238,0.0014863692,-0.0273054153,q1light,0.4,bad_f020_s100,0.5250237867,0.2071132255,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_10290c5b.csv,gate_raw_tight,0.5778404085,0.5768939715,7.42e-08,6.3223e-05,0.0014889188,-0.0206021109,context_only,0.44,bad_hard_f010,0.3988,0.1,submission_raw05_jepa_efmicro_47eb1bcc.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_aacc9adf.csv,gate_raw_tight,0.5778404118,0.5768939983,7.41e-08,5.67602e-05,0.0014886795,-0.0207256158,context_only,0.44,bad_hard_f010,0.3988,0.1,submission_raw05_jepa_efmicro_61a4476f.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_d4300caf.csv,gate_raw_tight,0.5778404144,0.5768940008,7.39e-08,5.85727e-05,0.0014887998,-0.0206315919,context_only,0.44,bad_hard_f010,0.3988,0.1,submission_raw05_jepa_efmicro_c2d77911.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
submission_raw05_jepa_efgate_42c57e95.csv,gate_raw_tight,0.5778404174,0.5768896015,7.55e-08,0.0005540492,0.0014872887,-0.0308651746,q1light,0.52,bad_f010_s075,0.4604945356,0.1022084239,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_cc5cbecb.csv,gate_raw_tight,0.5778404269,0.5768925895,7.81e-08,5.94061e-05,0.0014899473,-0.0228814197,context_only,0.46,bad_f005_s075,0.4180841101,0.0534391255,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_5861a3e6.csv,gate_raw_tight,0.577840434,0.5768888049,7.88e-08,0.0003563585,0.0014952367,-0.0315602346,q1light,0.46,bad_f020_s100,0.5139093764,0.2054687104,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_9d40abd2.csv,gate_actual,0.5778402635,0.5768924235,1.018e-07,5.82792e-05,0.0014936005,-0.0254194081,q2s1heavy,0.44,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_db557ec2.csv,gate_actual,0.5778403001,0.576888541,1.018e-07,0.0001761433,0.001497509,-0.0221536296,q1light,0.48,bad_f005_s075,0.4176565092,0.0519452282,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_019477a0.csv,gate_actual,0.5778403197,0.5768919073,1.042e-07,4.18215e-05,0.0014937091,-0.026390011,q2s1heavy,0.46,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_f03e6331.csv,gate_actual,0.5778403162,0.5768918808,1.043e-07,4.78168e-05,0.0014939389,-0.0262299146,q2s1heavy,0.46,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
submission_raw05_jepa_efgate_8511e097.csv,gate_actual,0.5778403032,0.5768874988,1.099e-07,0.0002863664,0.0014982799,-0.02763236,q2s1heavy,0.4,bad_f020_s100,0.5245574676,0.2141783892,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_bf207a7c.csv,gate_actual,0.5778403006,0.5768874648,1.101e-07,0.0002932119,0.0014985164,-0.0274273521,q2s1heavy,0.4,bad_f020_s100,0.5248361667,0.2144098871,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_cfadd8d7.csv,gate_actual,0.5778403034,0.5768904546,1.141e-07,4.42397e-05,0.0014942146,-0.022280701,q2s1heavy,0.44,bad_hard_f010,0.4132,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_8400aff8.csv,gate_actual,0.5778402999,0.5768904284,1.143e-07,5.02551e-05,0.0014944483,-0.0221638572,q2s1heavy,0.44,bad_hard_f010,0.4132,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_ebba81f9.csv,gate_actual,0.5778403194,0.5768902749,1.145e-07,5.63435e-05,0.0014938626,-0.0234464904,q2s1heavy,0.44,bad_hard_f010,0.4168,0.1,submission_raw05_jepa_efmicro_47eb1bcc.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
submission_raw05_jepa_efgate_88d3005a.csv,gate_actual,0.5778403199,0.5768901041,1.16e-07,6.07439e-05,0.0014918232,-0.028147606,q2s1heavy,0.5,bad_hard_f010,0.406,0.1,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
```

## Best By Blend / Gate / Beta

```csv
blend_profile,row_gate,beta,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,energy_delta_vs_base,gate_mean,gate_p10,base_file,donor_file
q1light,bad_f010_s075,0.44,0.5778402624,0.5768889122,9.66e-08,0.0002444987,-0.0222745,0.448305313,0.101842713,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_hard_f010,0.44,0.5778402635,0.5768924235,1.018e-07,5.82792e-05,-0.0254194081,0.406,0.1,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f010_s075,0.4,0.5778402797,0.5768890442,9.87e-08,0.0005315278,-0.026267302,0.4727433223,0.1050158098,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.4,0.5778402891,0.5768888662,8.58e-08,0.000364676,-0.0240364195,0.5153821693,0.2076376726,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f005_s075,0.48,0.5778403001,0.576888541,1.018e-07,0.0001761433,-0.0221536296,0.4176565092,0.0519452282,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f020_s100,0.4,0.5778403006,0.5768874648,1.101e-07,0.0002932119,-0.0274273521,0.5248361667,0.2144098871,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_hard_f010,0.46,0.5778403162,0.5768918808,1.043e-07,4.78168e-05,-0.0262299146,0.406,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_hard_f010,0.5,0.5778403199,0.5768901041,1.16e-07,6.07439e-05,-0.028147606,0.406,0.1,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_f010_s075,0.46,0.5778403201,0.5768884142,9.73e-08,0.000234473,-0.0232259925,0.4483057398,0.1018427804,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f005_s075,0.5,0.5778403296,0.5768895347,8.97e-08,0.0001722919,-0.0258449966,0.4140475689,0.050990361,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
q2s1heavy,bad_f005_s075,0.46,0.5778403312,0.5768905503,1.01e-07,5.52999e-05,-0.0261888339,0.4277167115,0.0531369669,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
context_only,bad_hard_f010,0.48,0.5778403335,0.576892585,9.87e-08,5.79916e-05,-0.0240117737,0.4024,0.1,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
q1light,bad_f010_s075,0.5,0.5778403406,0.5768895778,8.7e-08,0.0002359436,-0.0309149486,0.4502442513,0.1018994497,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f005_s075,0.48,0.5778403437,0.5768916468,9.29e-08,5.76953e-05,-0.0314118627,0.4275314011,0.0530698528,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_f010_s075,0.48,0.5778403444,0.5768894333,8.99e-08,0.0002253914,-0.0279930081,0.4462219488,0.1010784322,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
context_only,bad_hard_f010,0.5,0.577840351,0.5768921199,1.091e-07,5.67875e-05,-0.0250149258,0.3952,0.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_hard_f010,0.44,0.5778403513,0.5768941038,8.44e-08,6.32995e-05,-0.0197415253,0.3952,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f020_s100,0.44,0.5778403515,0.5768882786,9.98e-08,0.0002944788,-0.0378716888,0.5259354327,0.2151166014,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f010_s075,0.48,0.5778403589,0.5768888687,1.005e-07,0.0004634631,-0.0327726665,0.4725449633,0.1090133163,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_hard_f010,0.44,0.5778403659,0.5768895486,8.9e-08,0.0005441504,-0.0215853453,0.4204,0.1,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,energy_soft_floor,0.4,0.5778403695,0.5768872382,9.15e-08,0.0008589744,-0.0791524164,0.7087826508,0.4070917819,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.44,0.5778403714,0.5768892859,7.89e-08,0.0003610843,-0.0302813924,0.5139090966,0.2054686859,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_hard_f010,0.48,0.5778403724,0.5768913649,1.067e-07,3.13008e-05,-0.0271815944,0.406,0.1,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_f005_s075,0.52,0.5778403726,0.5768891131,9.55e-08,0.0001600015,-0.0274234455,0.4156591779,0.0511253114,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
q1light,bad_f005_s075,0.46,0.5778403735,0.5768895517,8.01e-08,0.000544471,-0.0239512129,0.430862873,0.0517685395,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_hard_f010,0.52,0.5778403749,0.5768895689,1.184e-07,5.04464e-05,-0.02884155,0.406,0.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f020_s100,0.46,0.5778403749,0.5768894801,8.99e-08,0.000300997,-0.0448506638,0.5256746611,0.2131378603,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
q1light,bad_f020_s100,0.46,0.5778403813,0.5768893601,7.5e-08,0.000374642,-0.034603919,0.516327265,0.2078099782,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f005_s075,0.52,0.5778403866,0.5768880785,1.159e-07,6.00787e-05,-0.0328543047,0.4287182409,0.0546059351,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
context_only,bad_f005_s075,0.46,0.5778403932,0.5768939276,7.12e-08,6.32418e-05,-0.0261742012,0.4163965597,0.053353618,submission_raw05_jepa_efmicro_9f19106d.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
context_only,bad_hard_f010,0.46,0.5778403985,0.5768906472,9.76e-08,6.37859e-05,-0.0196794049,0.3952,0.1,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
q2s1heavy,bad_f005_s075,0.5,0.5778403986,0.5768911426,9.46e-08,4.22781e-05,-0.0325849766,0.4275316017,0.0530696943,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_f010_s075,0.52,0.5778403996,0.5768890481,8.8e-08,0.0002255845,-0.0320372719,0.4502450298,0.1018996708,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f010_s075,0.44,0.577840407,0.576889652,8.43e-08,0.0005113477,-0.0323702282,0.4689422424,0.1034420827,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
context_only,bad_f020_s100,0.4,0.577840409,0.5768892168,8.62e-08,0.0003042433,-0.0238164184,0.5170453581,0.2126875476,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
context_only,bad_hard_f010,0.52,0.5778404107,0.5768916922,1.112e-07,3.9264e-05,-0.0258474843,0.3952,0.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_hard_f010,0.46,0.5778404217,0.5768890422,9.06e-08,0.0005302092,-0.0224514381,0.4204,0.1,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f010_s075,0.5,0.577840422,0.5768882574,1.028e-07,0.0004470739,-0.0340014792,0.4725450726,0.109012746,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f005_s075,0.56,0.5778404292,0.5768887728,9.4e-08,0.0001471202,-0.030991032,0.4197047306,0.0520056748,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f020_s100,0.48,0.5778404294,0.5768889224,9.18e-08,0.0002925885,-0.0467398318,0.5258533966,0.2128555538,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f010_s075,0.46,0.5778404308,0.5768890724,9.46e-08,0.0004976753,-0.0345397839,0.4714534679,0.1040235275,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f005_s075,0.48,0.5778404418,0.5768934811,7.29e-08,5.68149e-05,-0.0271686316,0.4172817188,0.0534629977,submission_raw05_jepa_efmicro_26253469.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f010_s075,0.46,0.5778404456,0.5768888465,9.93e-08,0.0001547324,-0.0227477797,0.446857129,0.1036436331,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.48,0.577840447,0.5768887748,7.55e-08,0.0003694122,-0.0359853683,0.5163279753,0.2078106547,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f005_s075,0.56,0.5778404471,0.5768888726,1.082e-07,5.37184e-05,-0.0399763305,0.4284464883,0.0539193574,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f005_s075,0.52,0.5778404492,0.576891932,8.38e-08,6.35987e-05,-0.0325582618,0.4172684428,0.0538423179,submission_raw05_jepa_efmicro_58129468.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f010_s075,0.52,0.5778404543,0.5768872651,1.146e-07,0.0001200206,-0.0361033326,0.4589669092,0.104624517,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
context_only,bad_f005_s075,0.5,0.5778404633,0.5768900056,9.7e-08,6.36299e-05,-0.026101345,0.4147953055,0.0535034192,submission_raw05_jepa_efmicro_f88f2cec.csv,submission_raw05_jepa_ctxenergy_c6b68fde.csv
q1light,bad_hard_f010,0.52,0.5778404687,0.576887164,1.185e-07,0.0001255557,-0.0222619872,0.3988,0.1,submission_raw05_jepa_efmicro_a89cd60b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_hard_f010,0.48,0.5778404776,0.5768885358,9.23e-08,0.0005162682,-0.0233075257,0.4204,0.1,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_hard_f010,0.56,0.5778404824,0.5768885587,9.93e-08,0.0004535156,-0.028086232,0.4168,0.1,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f020_s100,0.5,0.5778404946,0.5768883434,9.3e-08,0.000284155,-0.0484643391,0.5258533751,0.2128550222,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_hard_f010,0.56,0.5778404968,0.5768887328,1.193e-07,1.04833e-05,-0.0299301819,0.3988,0.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
context_only,bad_f020_s100,0.44,0.5778404996,0.5768896605,8.04e-08,0.0002903225,-0.0299439181,0.515809768,0.2108998494,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f010_s075,0.48,0.5778405089,0.5768883676,1.003e-07,0.0001412339,-0.0236763263,0.4468546873,0.1036419704,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.5,0.5778405128,0.5768881895,7.6e-08,0.0003641827,-0.0373565616,0.5163286857,0.2078113313,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,energy_soft_floor,0.44,0.5778405173,0.5768857076,9.45e-08,0.0008948268,-0.0862078181,0.707436496,0.4038580341,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f010_s075,0.56,0.5778405177,0.5768879889,9.02e-08,0.0002048672,-0.0342555473,0.4502465869,0.101900113,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.52,0.5778405244,0.5768894161,6.74e-08,0.0003693126,-0.0440733974,0.5154225039,0.2057708084,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f010_s075,0.44,0.5778405281,0.5768896529,8.23e-08,0.0004941803,-0.0249250335,0.4656473535,0.1030340574,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
context_only,bad_hard_f010,0.56,0.5778405303,0.5768908371,1.157e-07,4.2181e-06,-0.0274738232,0.3952,0.1,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q1light,bad_hard_f010,0.5,0.5778405335,0.5768880295,9.41e-08,0.0005023274,-0.0241536082,0.4204,0.1,submission_raw05_jepa_energyfront_ce903f7b.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q2s1heavy,bad_f010_s075,0.56,0.5778405479,0.5768885585,9.83e-08,0.0004088243,-0.0428495925,0.4699401145,0.105315636,submission_raw05_jepa_energyfront_a190aa25.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
q2s1heavy,bad_f020_s100,0.52,0.5778405598,0.5768877645,9.44e-08,0.0002757216,-0.050171007,0.5258533536,0.2128544906,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f020_s100,0.46,0.5778405683,0.5768891967,8.05e-08,0.0002823877,-0.0312106239,0.5158117386,0.2109020503,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f005_s075,0.56,0.5778405683,0.5768910615,8.59e-08,3.81191e-05,-0.0345027826,0.4175243597,0.0538631424,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f010_s075,0.5,0.577840569,0.5768894626,8.26e-08,0.0001305659,-0.0277684613,0.445566179,0.1042836362,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_3605e0ce.csv
context_only,bad_f010_s075,0.52,0.5778405841,0.5768890067,9.52e-08,0.0001176288,-0.0293479446,0.4455284738,0.1029762214,submission_raw05_jepa_efmicro_5d2d2af0.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
context_only,bad_f020_s100,0.48,0.5778406284,0.5768893146,7.33e-08,0.0002815134,-0.0355367785,0.5183844025,0.212418258,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_7ff87859.csv
q1light,bad_f020_s100,0.56,0.5778406522,0.5768883853,6.8e-08,0.0003596487,-0.0470865761,0.5154230182,0.2057709972,submission_raw05_jepa_efmicro_3eece507.csv,submission_raw05_jepa_ctxenergy_d19d7846.csv
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_efgate_ac60a2e6.csv,250,True,0,0,0.0631481573,0.9798124721
submission_raw05_jepa_efgate_e7d05c45.csv,250,True,0,0,0.0631482154,0.9798124775
submission_raw05_jepa_efgate_8bd2def3.csv,250,True,0,0,0.0631482395,0.9798124731
submission_raw05_jepa_efgate_b6e8ee31.csv,250,True,0,0,0.0631590013,0.979826412
submission_raw05_jepa_efgate_b5fade58.csv,250,True,0,0,0.0631590259,0.9798264116
submission_raw05_jepa_efgate_48c25ff7.csv,250,True,0,0,0.0631321263,0.9798131122
submission_raw05_jepa_efgate_fc53e556.csv,250,True,0,0,0.0631585883,0.9798263477
submission_raw05_jepa_efgate_793e3f5d.csv,250,True,0,0,0.0631472824,0.9798122651
submission_raw05_jepa_efgate_d359abc4.csv,250,True,0,0,0.0631586129,0.9798263473
submission_raw05_jepa_efgate_94a45c75.csv,250,True,0,0,0.0631473258,0.9798122685
submission_raw05_jepa_efgate_eae9c6ac.csv,250,True,0,0,0.0631473484,0.979812266
submission_raw05_jepa_efgate_754e2cb4.csv,250,True,0,0,0.0631583766,0.9798263862
submission_raw05_jepa_efgate_b17b5030.csv,250,True,0,0,0.0631585973,0.979826385
submission_raw05_jepa_efgate_5248c6f2.csv,250,True,0,0,0.0631581843,0.9798263206
submission_raw05_jepa_efgate_d5532b5a.csv,250,True,0,0,0.0631579636,0.9798263218
submission_raw05_jepa_efgate_71b69c58.csv,250,True,0,0,0.0631453715,0.9798139263
submission_raw05_jepa_efgate_83dc6d85.csv,250,True,0,0,0.0631453709,0.9798139198
submission_raw05_jepa_efgate_80b04d8b.csv,250,True,0,0,0.0631453764,0.9798139142
submission_raw05_jepa_efgate_a538d5c0.csv,250,True,0,0,0.0631452956,0.9798138427
submission_raw05_jepa_efgate_daa7eaaf.csv,250,True,0,0,0.063150521,0.9798157597
submission_raw05_jepa_efgate_8dff62c3.csv,250,True,0,0,0.0631452943,0.9798138359
submission_raw05_jepa_efgate_a1778739.csv,250,True,0,0,0.0631505296,0.9798157517
submission_raw05_jepa_efgate_6ec2b8a9.csv,250,True,0,0,0.0631452932,0.9798138288
submission_raw05_jepa_efgate_7f1625c6.csv,250,True,0,0,0.0631568399,0.979826655
submission_raw05_jepa_efgate_718c6fcb.csv,250,True,0,0,0.0631427322,0.979813152
submission_raw05_jepa_efgate_d592970e.csv,250,True,0,0,0.0631568643,0.9798266546
submission_raw05_jepa_efgate_4024a723.csv,250,True,0,0,0.063144084,0.9798136637
submission_raw05_jepa_efgate_a297600b.csv,250,True,0,0,0.0631586248,0.9798264093
submission_raw05_jepa_efgate_a199e1b3.csv,250,True,0,0,0.0631440912,0.9798136586
submission_raw05_jepa_efgate_62d53675.csv,250,True,0,0,0.0631268703,0.9798215319
submission_raw05_jepa_efgate_10765d3c.csv,250,True,0,0,0.0631440826,0.9798136492
submission_raw05_jepa_efgate_19afbed3.csv,250,True,0,0,0.0631419215,0.9798132299
submission_raw05_jepa_efgate_10290c5b.csv,250,True,0,0,0.063156415,0.9798266278
submission_raw05_jepa_efgate_aacc9adf.csv,250,True,0,0,0.0631564396,0.9798266278
submission_raw05_jepa_efgate_d4300caf.csv,250,True,0,0,0.0631562209,0.9798266289
submission_raw05_jepa_efgate_42c57e95.csv,250,True,0,0,0.0631475009,0.9798149266
submission_raw05_jepa_efgate_cc5cbecb.csv,250,True,0,0,0.0631273235,0.979819623
submission_raw05_jepa_efgate_5861a3e6.csv,250,True,0,0,0.0631444422,0.9798135758
submission_raw05_jepa_efgate_9d40abd2.csv,250,True,0,0,0.0631590534,0.9798264359
submission_raw05_jepa_efgate_db557ec2.csv,250,True,0,0,0.063147721,0.9798121742
submission_raw05_jepa_efgate_019477a0.csv,250,True,0,0,0.0631587554,0.9798263484
submission_raw05_jepa_efgate_f03e6331.csv,250,True,0,0,0.0631587309,0.9798263488
submission_raw05_jepa_efgate_8511e097.csv,250,True,0,0,0.0631329373,0.9798112538
submission_raw05_jepa_efgate_bf207a7c.csv,250,True,0,0,0.0631329361,0.9798112594
submission_raw05_jepa_efgate_cfadd8d7.csv,250,True,0,0,0.0631590454,0.9798258901
submission_raw05_jepa_efgate_8400aff8.csv,250,True,0,0,0.0631590208,0.9798258905
submission_raw05_jepa_efgate_ebba81f9.csv,250,True,0,0,0.063158592,0.9798258635
submission_raw05_jepa_efgate_88d3005a.csv,250,True,0,0,0.0631652039,0.979826153
```
