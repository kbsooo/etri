# Raw05 JEPA Context-Target Energy Gate

This pass applies the I-JEPA idea more literally: non-Q3/S1/S2/S3/Q1 predictions are the context block, Q3/S4 is the target block, and a learned context-to-target compatibility energy decides how much counterweight to apply per row.

## Model

- context targets: Q1+Q2+S1+S2+S3
- target block: Q3+S4
- train energy mean: 0.999837
- train energy p90: 2.000868

## Counts

- generated candidates: 117348
- actual-anchor rescored candidates: 1513
- saved candidates: 59

## Top Saved

```csv
file,bucket,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,mean_abs_move_vs_raw05,profile,alpha,energy_gate,energy_gate_mean,energy_delta_vs_base,base_file,counter_file
submission_raw05_jepa_ctxenergy_88fa416a.csv,actual_probe,0.577840255,0.5768939171,6.93e-08,0.0017047789,0.0014628741,nonq3s4_flat,0.68,soft_floor,0.5823595226,-0.0260359335,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_a726b739.csv,posterior,0.5778406779,0.5768933502,6.02e-08,0.0016969992,0.0014572422,nonq3s4_q2s1heavy,0.68,soft_floor,0.5807475785,-0.0331559431,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_b30b13f7.csv,posterior,0.5778407388,0.5768933827,5.94e-08,0.0017027017,0.0014563211,nonq3s4_q2s1heavy,0.68,soft_floor,0.5807200175,-0.0331595035,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_ctxenergy_7b657360.csv,raw_boundary,0.577840323,0.5768939523,6.75e-08,0.0017112112,0.0014617158,nonq3s4_flat,0.68,soft_floor,0.5822579353,-0.0258385395,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_ctxenergy_a8ab21c0.csv,posterior,0.5778407539,0.5768933906,5.92e-08,0.0017040888,0.0014560958,nonq3s4_q2s1heavy,0.68,soft_floor,0.5807144425,-0.0331680587,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_ctxenergy_d57bdec8.csv,raw_boundary,0.5778403399,0.5768939603,6.71e-08,0.0017126241,0.0014614317,nonq3s4_flat,0.68,soft_floor,0.5822421781,-0.0258170086,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_ctxenergy_37dd7e0a.csv,posterior,0.5778405495,0.5768931405,5.73e-08,0.0017279778,0.0014596646,nonq3s4_q2s1heavy,0.68,soft_floor,0.5921449399,-0.020825808,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_dc01246b.csv,posterior,0.5778406531,0.57689315,6.16e-08,0.0017284699,0.0014587092,nonq3s4_q2s1heavy,0.68,soft_floor,0.584256386,-0.0389572437,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_0731d036.csv,posterior,0.5778406132,0.5768931631,5.65e-08,0.0017331243,0.0014587235,nonq3s4_q2s1heavy,0.68,soft_floor,0.5920415363,-0.0207958242,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_ctxenergy_ddb8eeef.csv,posterior,0.577840629,0.576893168,5.63e-08,0.0017342161,0.0014584918,nonq3s4_q2s1heavy,0.68,soft_floor,0.5920307314,-0.0208087518,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_ctxenergy_a69018a3.csv,actual_probe,0.5778402221,0.5768936974,7.12e-08,0.0017417728,0.0014645762,nonq3s4_flat,0.68,soft_floor,0.5856978736,-0.0305482491,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_c9b67a1a.csv,posterior,0.5778406447,0.576893173,5.62e-08,0.0017353127,0.00145826,nonq3s4_q2s1heavy,0.68,soft_floor,0.5920200056,-0.0208219202,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_ctxenergy_341d4af3.csv,posterior,0.5778407157,0.5768931859,6.07e-08,0.0017348843,0.0014577776,nonq3s4_q2s1heavy,0.68,soft_floor,0.5842014077,-0.0388220756,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_ctxenergy_a17ee5ee.csv,posterior,0.5778406605,0.5768931785,5.6e-08,0.0017365138,0.0014580265,nonq3s4_q2s1heavy,0.68,soft_floor,0.5920017101,-0.0208256198,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_4a27604e.csv
submission_raw05_jepa_ctxenergy_529adb1a.csv,posterior,0.5778407311,0.5768931943,6.04e-08,0.0017363578,0.0014575486,nonq3s4_q2s1heavy,0.68,soft_floor,0.5841947582,-0.038813823,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_ctxenergy_5cb845bc.csv,posterior,0.5778407465,0.5768932026,6.02e-08,0.0017378319,0.0014573195,nonq3s4_q2s1heavy,0.68,soft_floor,0.5841879457,-0.038805675,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_ctxenergy_a83ded85.csv,raw_boundary,0.5778402894,0.5768937272,6.96e-08,0.0017468526,0.0014634395,nonq3s4_flat,0.68,soft_floor,0.5856872169,-0.030551549,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_ctxenergy_0da8b0a3.csv,actual_probe,0.5778401686,0.5768959537,1.009e-07,0.0017460067,0.0014616844,nonq3s4_q2light,0.68,hard_improve,0.516,-0.0270894024,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_28942f90.csv,raw_boundary,0.5778403064,0.5768937355,6.92e-08,0.0017483003,0.0014631516,nonq3s4_flat,0.68,soft_floor,0.5856717192,-0.0305252701,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_ctxenergy_52b26818.csv,raw_boundary,0.5778403232,0.5768937429,6.88e-08,0.0017495511,0.0014628698,nonq3s4_flat,0.68,soft_floor,0.585669999,-0.030530718,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_ctxenergy_c00fe37b.csv,actual_probe,0.5778400953,0.5768937334,6.73e-08,0.0017609877,0.0014661164,nonq3s4_flat,0.68,soft_floor,0.5955847698,-0.0199700131,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_cd7078b1.csv,actual_probe,0.5778401685,0.5768937543,6.56e-08,0.0017671642,0.0014649812,nonq3s4_flat,0.68,soft_floor,0.5954155924,-0.019773045,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_ctxenergy_4b55c30f.csv,actual_probe,0.5778401869,0.5768937586,6.51e-08,0.0017684121,0.0014647016,nonq3s4_flat,0.68,soft_floor,0.5953967696,-0.0197505103,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_ctxenergy_a6fd3246.csv,actual_probe,0.5778402052,0.5768937629,6.47e-08,0.0017696641,0.0014644218,nonq3s4_flat,0.68,soft_floor,0.5953775898,-0.0197281477,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_ctxenergy_80e5df15.csv,actual_probe,0.5778402236,0.5768937672,6.43e-08,0.0017709202,0.001464142,nonq3s4_flat,0.68,soft_floor,0.5953580504,-0.0197059579,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_4a27604e.csv
submission_raw05_jepa_ctxenergy_c9d6bd2a.csv,raw_boundary,0.5778403379,0.576896144,9.06e-08,0.0017716578,0.0014588022,nonq3s4_q2light,0.64,hard_improve,0.516,-0.0256375146,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_07abbce8.csv,actual_probe,0.5778402441,0.5768963879,1.036e-07,0.0017601705,0.0014603894,nonq3s4_q2light,0.68,hard_improve,0.524,-0.0265347039,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_0773ee96.csv
submission_raw05_jepa_ctxenergy_4c46ea22.csv,actual_probe,0.5778401867,0.5768934576,7.34e-08,0.0017762101,0.0014662911,nonq3s4_flat,0.68,soft_floor,0.5893217578,-0.0357959309,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_af91437e.csv,actual_probe,0.5778402543,0.5768934873,7.17e-08,0.0017812164,0.0014651466,nonq3s4_flat,0.68,soft_floor,0.5893328038,-0.0358190295,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_d7470f9d.csv
submission_raw05_jepa_ctxenergy_6d4cca0c.csv,raw_boundary,0.5778402713,0.5768934949,7.13e-08,0.0017825016,0.0014648614,nonq3s4_flat,0.68,soft_floor,0.5893324729,-0.0358200176,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_05274703.csv
submission_raw05_jepa_ctxenergy_07b2272d.csv,raw_boundary,0.5778402882,0.5768935025,7.09e-08,0.0017837886,0.0014645764,nonq3s4_flat,0.68,soft_floor,0.5893319048,-0.0358211163,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_83b273ba.csv
submission_raw05_jepa_ctxenergy_34f72d9a.csv,raw_boundary,0.5778402666,0.5768940527,6.07e-08,0.0017848883,0.0014631927,nonq3s4_flat,0.64,soft_floor,0.5964963238,-0.018934491,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_b1dd57e4.csv,raw_boundary,0.577840336,0.5768940723,5.93e-08,0.0017907789,0.0014621432,nonq3s4_flat,0.64,soft_floor,0.5963121142,-0.0187433377,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_ctxenergy_36f4ee59.csv,raw_boundary,0.5778403535,0.5768940763,5.89e-08,0.0017919672,0.001461887,nonq3s4_flat,0.64,soft_floor,0.5962909898,-0.0187212136,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_492c24f9.csv
submission_raw05_jepa_ctxenergy_8d15316d.csv,actual_probe,0.577840086,0.5768934593,6.96e-08,0.0017969425,0.0014679747,nonq3s4_flat,0.68,soft_floor,0.5975473715,-0.0237274905,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_424b6910.csv,actual_probe,0.5778401138,0.5768938465,6.74e-08,0.0017994622,0.0014662755,nonq3s4_q2light,0.68,soft_floor,0.5931808337,-0.0184647532,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
submission_raw05_jepa_ctxenergy_4537a4b0.csv,raw_boundary,0.577840353,0.5768942118,5.76e-08,0.0017966536,0.0014617604,nonq3s4_flat,0.62,soft_floor,0.5969715446,-0.0184308372,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_fc3a3f13.csv,actual_probe,0.5778401576,0.5768934789,6.79e-08,0.0018016822,0.0014668486,nonq3s4_flat,0.68,soft_floor,0.5975414787,-0.0237002729,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_af508901.csv
submission_raw05_jepa_ctxenergy_45f3054d.csv,raw_boundary,0.5778403229,0.5768943429,5.79e-08,0.0017988744,0.0014671599,nonq3_s4tiny,0.68,soft_floor,0.5675481663,-0.0134089574,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
submission_raw05_jepa_ctxenergy_3e1d850b.csv,actual_probe,0.5778401754,0.576893483,6.75e-08,0.0018026203,0.0014665729,nonq3s4_flat,0.68,soft_floor,0.5975635324,-0.0237185487,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_492c24f9.csv
```

## Best By Profile / Alpha / Energy Gate

```csv
profile,alpha,energy_gate,actual_anchor_score_final,posterior_expected_public_vs_anchor,delta_vs_raw05_rawaxis,bad_residual_axis_ratio,energy_delta_vs_base,base_file,counter_file
nonq3s4_flat,0.68,soft_floor,0.5778400631,0.5768931955,7.21e-08,0.0018323855,-0.0281815447,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2light,0.68,soft_floor,0.5778401138,0.5768938465,6.74e-08,0.0017994622,-0.0184647532,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2light,0.68,hard_improve,0.5778401686,0.5768959537,1.009e-07,0.0017460067,-0.0270894024,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.64,soft_floor,0.5778402557,0.5768937793,6.29e-08,0.0018222354,-0.0225046866,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2light,0.64,soft_floor,0.5778402834,0.5768941576,6.07e-08,0.0018205791,-0.0175448721,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3_s4tiny,0.68,soft_floor,0.5778403229,0.5768943429,5.79e-08,0.0017988744,-0.0134089574,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2light,0.64,hard_improve,0.5778403379,0.576896144,9.06e-08,0.0017716578,-0.0256375146,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.62,soft_floor,0.577840353,0.5768942118,5.76e-08,0.0017966536,-0.0184308372,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2light,0.62,hard_improve,0.5778404056,0.5768962355,8.94e-08,0.0017842319,-0.0249056873,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.6,soft_floor,0.5778404398,0.5768943714,5.48e-08,0.001808467,-0.0179217851,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2s1heavy,0.68,hard_improve,0.5778404506,0.5768939537,1.027e-07,0.0017915584,-0.0625381327,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.68,hard_improve,0.5778405,0.5768937658,1.106e-07,0.0016956481,-0.045728015,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.68,soft_floor,0.5778405183,0.5768927072,6.12e-08,0.0017910105,-0.0304324243,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3_s4tiny,0.64,soft_floor,0.5778405513,0.5768946462,5.71e-08,0.0018111093,-0.0228513961,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.64,hard_improve,0.5778406206,0.5768943825,9.85e-08,0.0017752692,-0.0530293223,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.58,soft_floor,0.5778406272,0.576894439,5.58e-08,0.0018117629,-0.0268851742,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.64,hard_improve,0.5778406577,0.5768940851,1e-07,0.0017242504,-0.0434891633,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3_s4tiny,0.62,soft_floor,0.5778406674,0.5768950125,5.18e-08,0.0017885303,-0.0176338352,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.64,soft_floor,0.577840668,0.5768930494,5.67e-08,0.0018196534,-0.0289454408,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2s1heavy,0.62,hard_improve,0.5778407014,0.5768945274,9.46e-08,0.0017898548,-0.0517077041,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.68,soft,0.5778407107,0.5768943837,6.91e-08,0.0017922504,-0.0358478131,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3_s4tiny,0.68,hard_improve,0.5778407336,0.5768948213,8.25e-08,0.0018058045,-0.0345177676,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.62,hard_improve,0.5778407369,0.5768942451,9.51e-08,0.0017385532,-0.0423485954,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.62,soft_floor,0.5778407421,0.5768932218,5.46e-08,0.0018341452,-0.0281770909,submission_raw05_jepa_targetw_f8c12205.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.56,soft_floor,0.5778407425,0.5768948135,5.16e-08,0.0017838082,-0.0224122202,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3_s4tiny,0.6,soft_floor,0.5778407439,0.5768951397,4.94e-08,0.0018001669,-0.0172824549,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.6,hard_improve,0.5778407605,0.5768942292,9.84e-08,0.0018002814,-0.0411939967,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.6,hard_improve,0.5778407825,0.5768946725,9.08e-08,0.001804441,-0.0503644377,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3_s4tiny,0.64,hard_improve,0.577840791,0.5768945994,9.87e-08,0.0018089581,-0.0441528691,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_d7470f9d.csv
nonq3s4_q2s1heavy,0.6,soft_floor,0.5778408359,0.5768936187,5.07e-08,0.0018140004,-0.0227354048,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_flat,0.58,hard_improve,0.5778408421,0.5768943954,9.37e-08,0.001813003,-0.0400253356,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_flat,0.64,soft,0.5778408459,0.5768946465,6.36e-08,0.0018119383,-0.0341554222,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.58,hard_improve,0.5778408848,0.5768949851,8.54e-08,0.0017777004,-0.0431503745,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.68,soft,0.577840899,0.5768935246,5.97e-08,0.0018294983,-0.0326446459,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2s1heavy,0.58,soft_floor,0.5778409094,0.5768937933,4.89e-08,0.001827612,-0.0220956191,submission_raw05_jepa_targetw_038f70cc.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2s1heavy,0.56,hard_improve,0.5778409662,0.5768951322,8.2e-08,0.0017916503,-0.0419119193,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.56,soft_floor,0.5778409982,0.5768941919,4.54e-08,0.0018045595,-0.0176828591,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3_s4tiny,0.62,hard_improve,0.5778410259,0.5768955526,7.69e-08,0.0017860591,-0.0377452283,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
nonq3s4_q2s1heavy,0.64,soft,0.5778410427,0.576894094,5.37e-08,0.0018146619,-0.0259627607,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_2f6a1cf2.csv
nonq3s4_q2light,0.6,hard_improve,0.5778410673,0.5768943405,6.56e-08,0.0018088683,-0.0293407878,submission_raw05_jepa_targetw_23629fbf.csv,submission_raw05_jepa_targetw_3263040f.csv
```

## Integrity

```csv
file,rows,key_ok,duplicate_keys,null_probs,min_prob,max_prob
submission_raw05_jepa_ctxenergy_88fa416a.csv,250,True,0,0,0.0631649208,0.9798192027
submission_raw05_jepa_ctxenergy_a726b739.csv,250,True,0,0,0.0631486073,0.9798183536
submission_raw05_jepa_ctxenergy_b30b13f7.csv,250,True,0,0,0.0631472112,0.9798182981
submission_raw05_jepa_ctxenergy_7b657360.csv,250,True,0,0,0.063162891,0.9798191623
submission_raw05_jepa_ctxenergy_a8ab21c0.csv,250,True,0,0,0.0631468713,0.9798182839
submission_raw05_jepa_ctxenergy_d57bdec8.csv,250,True,0,0,0.0631624337,0.9798191508
submission_raw05_jepa_ctxenergy_37dd7e0a.csv,250,True,0,0,0.0631482339,0.9798183001
submission_raw05_jepa_ctxenergy_dc01246b.csv,250,True,0,0,0.0631486384,0.9798182144
submission_raw05_jepa_ctxenergy_0731d036.csv,250,True,0,0,0.0631469127,0.9798182391
submission_raw05_jepa_ctxenergy_ddb8eeef.csv,250,True,0,0,0.0631466168,0.9798182221
submission_raw05_jepa_ctxenergy_a69018a3.csv,250,True,0,0,0.0631647106,0.9798190897
submission_raw05_jepa_ctxenergy_c9b67a1a.csv,250,True,0,0,0.0631463206,0.979818205
submission_raw05_jepa_ctxenergy_341d4af3.csv,250,True,0,0,0.0631470574,0.9798181669
submission_raw05_jepa_ctxenergy_a17ee5ee.csv,250,True,0,0,0.0631460073,0.9798181888
submission_raw05_jepa_ctxenergy_529adb1a.csv,250,True,0,0,0.0631466929,0.9798181534
submission_raw05_jepa_ctxenergy_5cb845bc.csv,250,True,0,0,0.0631463285,0.9798181399
submission_raw05_jepa_ctxenergy_a83ded85.csv,250,True,0,0,0.0631630046,0.9798190382
submission_raw05_jepa_ctxenergy_0da8b0a3.csv,250,True,0,0,0.0631758747,0.9798164002
submission_raw05_jepa_ctxenergy_28942f90.csv,250,True,0,0,0.0631625324,0.9798190269
submission_raw05_jepa_ctxenergy_52b26818.csv,250,True,0,0,0.0631621125,0.9798190137
submission_raw05_jepa_ctxenergy_c00fe37b.csv,250,True,0,0,0.0631650067,0.9798190837
submission_raw05_jepa_ctxenergy_cd7078b1.csv,250,True,0,0,0.0631630394,0.9798190395
submission_raw05_jepa_ctxenergy_4b55c30f.csv,250,True,0,0,0.0631626073,0.9798190264
submission_raw05_jepa_ctxenergy_a6fd3246.csv,250,True,0,0,0.0631621752,0.9798190133
submission_raw05_jepa_ctxenergy_80e5df15.csv,250,True,0,0,0.0631617429,0.9798190001
submission_raw05_jepa_ctxenergy_c9d6bd2a.csv,250,True,0,0,0.063170496,0.9798168779
submission_raw05_jepa_ctxenergy_07abbce8.csv,250,True,0,0,0.0631728097,0.9798162948
submission_raw05_jepa_ctxenergy_4c46ea22.csv,250,True,0,0,0.0631647881,0.9798189644
submission_raw05_jepa_ctxenergy_af91437e.csv,250,True,0,0,0.0631630822,0.9798189105
submission_raw05_jepa_ctxenergy_6d4cca0c.csv,250,True,0,0,0.0631626474,0.9798188974
submission_raw05_jepa_ctxenergy_07b2272d.csv,250,True,0,0,0.0631622126,0.9798188842
submission_raw05_jepa_ctxenergy_34f72d9a.csv,250,True,0,0,0.0631601723,0.9798193931
submission_raw05_jepa_ctxenergy_b1dd57e4.csv,250,True,0,0,0.0631583161,0.9798193517
submission_raw05_jepa_ctxenergy_36f4ee59.csv,250,True,0,0,0.0631579091,0.9798193393
submission_raw05_jepa_ctxenergy_8d15316d.csv,250,True,0,0,0.063165264,0.9798189592
submission_raw05_jepa_ctxenergy_424b6910.csv,250,True,0,0,0.0631637437,0.9798190891
submission_raw05_jepa_ctxenergy_4537a4b0.csv,250,True,0,0,0.063157806,0.9798195467
submission_raw05_jepa_ctxenergy_fc3a3f13.csv,250,True,0,0,0.0631635842,0.9798189019
submission_raw05_jepa_ctxenergy_45f3054d.csv,250,True,0,0,0.0631647917,0.9798191713
submission_raw05_jepa_ctxenergy_3e1d850b.csv,250,True,0,0,0.0631632148,0.9798188853
```
